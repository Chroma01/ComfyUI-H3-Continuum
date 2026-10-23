"""Real HTTP boundary tests; no model execution, real user data or GPU."""
import asyncio
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import uuid

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
import pytest

from ComfyUI_H3_Continuum_Join import project_manager_api as api


@pytest.fixture
def manager_server(tmp_path, monkeypatch):
    profile = tmp_path / "user"
    output = tmp_path / "output"
    folders = SimpleNamespace(get_user_directory=lambda: str(profile), get_output_directory=lambda: str(output),
        get_public_user_directory=lambda user: str(profile / user))
    monkeypatch.setitem(sys.modules, "folder_paths", folders)
    def user_id(request):
        user = request.headers.get("comfy-user", "default")
        if user not in {"default", "second"}:
            raise KeyError("Unknown user")
        return user
    queue = SimpleNamespace(running=[], pending=[])
    queue.get_current_queue = lambda: (queue.running, queue.pending)
    server = SimpleNamespace(routes=web.RouteTableDef(), prompt_queue=queue,
        user_manager=SimpleNamespace(get_request_user_id=user_id))
    api.register_routes(server)
    count = len(list(server.routes))
    api.register_routes(server)
    assert len(list(server.routes)) == count == 5
    app = web.Application()
    app.add_routes(server.routes)
    return app, server, profile, output


def create_body():
    return {"name": "Test project", "project_id": str(uuid.uuid4()), "operation_id": str(uuid.uuid4())}


def test_profile_id_length_follows_core_validation(tmp_path):
    user = "user_" + "a" * 140
    server = SimpleNamespace(user_manager=SimpleNamespace(get_request_user_id=lambda request: user))
    folders = SimpleNamespace(get_public_user_directory=lambda identity: tmp_path / identity)
    assert api._request_directory(server, object(), folders) == tmp_path / user / "h3_continuum/project_manager/projects"


def test_unused_routes_and_empty_listing_create_no_data(manager_server):
    app, _, profile, output = manager_server
    assert not profile.exists() and not output.exists()
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            response = await client.get(api.PREFIX)
            assert response.status == 200
            assert (await response.json())["projects"] == []
            assert response.headers["Cache-Control"] == "no-store"
    asyncio.run(scenario())
    assert not profile.exists() and not output.exists()


def test_create_retry_revision_conflict_and_user_separation(manager_server):
    app, _, profile, output = manager_server
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            body = create_body()
            made = await client.post(api.PREFIX, json=body)
            assert made.status == 200, await made.text()
            project = await made.json()
            duplicate = await client.post(api.PREFIX, json=body)
            assert duplicate.status == 200
            assert (await duplicate.json())["revision"] == project["revision"]
            other = await client.get(api.PREFIX, headers={"comfy-user": "second"})
            assert (await other.json())["projects"] == []
            assert (await client.get(api.PREFIX + "/" + project["id"], headers={"comfy-user": "second"})).status == 404
            uri = api.PREFIX + "/" + project["id"] + "/operations"
            op = {"revision": project["revision"], "operation_id": str(uuid.uuid4()), "action": "new_attempt", "name": "Alternative"}
            response = await client.post(uri, json=op)
            assert response.status == 200, await response.text()
            value = await response.json()
            assert value["attempts"][-1]["run_name"] == ""
            stale = {**op, "operation_id": str(uuid.uuid4())}
            assert (await client.post(uri, json=stale)).status == 409
            retry = await client.post(uri, json=op)
            assert retry.status == 200 and len((await retry.json())["attempts"]) == 1
    asyncio.run(scenario())
    assert not output.exists(), "Management operations must not create or update Runs"


def test_http_input_validation(manager_server):
    app, _, _, _ = manager_server
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            assert (await client.get(api.PREFIX, headers={"comfy-user": "../default"})).status == 403
            assert (await client.post(api.PREFIX, data="{}")).status == 415
            assert (await client.post(api.PREFIX, data="{", headers={"Content-Type": "application/json"})).status == 400
            assert (await client.post(api.PREFIX, json=[])).status == 400
            assert (await client.post(api.PREFIX, json={**create_body(), "path": "outside"})).status == 400
            assert (await client.post(api.PREFIX, json={**create_body(), "name": "x" * 66000})).status == 413
            assert (await client.post(api.PREFIX, json={**create_body(), "project_id": "../outside"})).status == 400
    asyncio.run(scenario())


def test_http_savepoint_and_prepare_use_actual_persisted_take(manager_server, tmp_path):
    from ComfyUI_H3_Continuum_Join.project_manager import ProjectManager
    from .test_project_manager import hashes, run_fixture
    app, _, profile, output = manager_server
    manager = ProjectManager(profile / "default" / "h3_continuum" / "project_manager" / "projects",
                             output / "h3_continuum" / "runs")
    controller, history = run_fixture(tmp_path, manager, prefix=2)
    before = hashes(manager.runs_root)
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            response = await client.post(api.PREFIX, json=create_body())
            project = await response.json()
            uri = api.PREFIX + "/" + project["id"]
            response = await client.post(uri + "/operations", json={
                "revision": project["revision"], "operation_id": str(uuid.uuid4()),
                "action": "attach_attempt", "name": "Existing trial", "run_name": controller.run_name})
            assert response.status == 200, await response.text()
            project = await response.json()
            response = await client.post(uri + "/operations", json={
                "revision": project["revision"], "operation_id": str(uuid.uuid4()),
                "action": "savepoint", "name": "Keep first two", "attempt_id": project["last_result"]["attempt_id"],
                "revision_id": history["canonical_head_revision_id"]})
            assert response.status == 200, await response.text()
            project = await response.json()
            response = await client.post(uri + "/prepare", json={"savepoint_id": project["last_result"]["savepoint_id"]})
            assert response.status == 200, await response.text()
            prepared = await response.json()
            assert prepared["run_name"] == controller.run_name
            assert prepared["revision_id"] == history["canonical_head_revision_id"]
            assert prepared["group"]["end"] == 2 and prepared["generation_reusable"] is True
    asyncio.run(scenario())
    assert hashes(manager.runs_root) == before


def test_prepare_checks_queued_run_without_mutating_queue(manager_server, monkeypatch):
    app, server, _, _ = manager_server
    module = importlib.import_module("ComfyUI_H3_Continuum_Join.project_manager")
    monkeypatch.setattr(module.ProjectManager, "prepare", lambda *args: {
        "run_name": "saved", "project_id": "", "storage_name": "saved", "revision_id": "take", "group": {"start": 1, "end": 1}})
    queue_item = [0, "prompt", {"42": {"class_type": "H3ContinuumSamplerV39", "inputs": {"run_name": "saved"}}}]
    server.prompt_queue.pending.append(queue_item)
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            uri = api.PREFIX + "/" + str(uuid.uuid4()) + "/prepare"
            response = await client.post(uri, json={"savepoint_id": str(uuid.uuid4())})
            assert response.status == 409
            assert server.prompt_queue.pending == [queue_item]
            server.prompt_queue.pending.clear()
            assert (await client.post(uri, json={"savepoint_id": str(uuid.uuid4())})).status == 200
    asyncio.run(scenario())


@pytest.mark.parametrize("class_type,inputs,expected", [
    ("SaveImage", {}, False),
    ("H3ContinuumSamplerV39", {"run_name": "other"}, False),
    ("H3ContinuumSamplerV38", {"run_name": "saved"}, True),
    ("H3ContinuumSamplerV39", {"run_name": ["1", 0]}, True),
    ("H3ContinuumSamplerV39", {}, True),
])
def test_queue_identity_boundary(manager_server, class_type, inputs, expected):
    _, server, _, _ = manager_server
    server.prompt_queue.running.append([0, "p", {"1": {"class_type": class_type, "inputs": inputs}}])
    assert api._run_busy(server, "saved") is expected


@pytest.mark.parametrize("accepted,expected", [(["other"], False), (["save"], True),
    (["save", "other"], True), ([], False), (["missing"], True)])
def test_only_upstream_of_accepted_outputs_blocks_preparation(manager_server, accepted, expected):
    _, server, _, _ = manager_server
    graph = {"sampler": {"class_type": "H3ContinuumSamplerV39", "inputs": {"run_name": "saved"}},
             "save": {"class_type": "SaveVideo", "inputs": {"video": ["sampler", 0]}},
             "other": {"class_type": "SaveImage", "inputs": {}}}
    server.prompt_queue.pending.append([0, "p", graph, {}, accepted])
    assert api._run_busy(server, "saved") is expected


def test_manager_registration_failure_does_not_break_existing_storage(tmp_path, monkeypatch):
    from .test_storage_api import api_server
    # Reuse the established production storage fixture (without invoking its
    # pytest wrapper) and force only the optional registration to fail.
    def broken(server):
        raise RuntimeError("optional Manager unavailable")
    monkeypatch.setattr(api, "register_routes", broken)
    app, manager, queue = api_server.__wrapped__(tmp_path, monkeypatch)
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            response = await client.get("/h3-continuum/storage/status")
            assert response.status == 200
            assert (await response.json())["path"] == ""
    asyncio.run(scenario())
