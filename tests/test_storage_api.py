"""Real HTTP requests to the production routes, using a model-free server fixture."""
import asyncio
from pathlib import Path
import sys
import threading
from types import SimpleNamespace

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from ComfyUI_H3_Continuum_Join import storage_api, storage_settings


@pytest.fixture
def api_server(tmp_path, monkeypatch):
    user = tmp_path / "user"
    temp = tmp_path / "temp"
    temp.mkdir()
    def system_user(name):
        if not name.replace("_", "").isalnum():
            raise ValueError("Invalid system user name")
        return str(user / ("__" + name))
    monkeypatch.setitem(sys.modules, "folder_paths", SimpleNamespace(
        get_system_user_directory=system_user, get_temp_directory=lambda: str(temp)))
    monkeypatch.setitem(sys.modules, "comfy.cli_args", SimpleNamespace(args=SimpleNamespace(multi_user=False)))
    monkeypatch.setattr(storage_settings, "_MANAGER", None)
    queue = SimpleNamespace(mutex=threading.RLock(), running=[], pending=[])
    queue.get_current_queue = lambda: (queue.running, queue.pending)
    server = SimpleNamespace(routes=web.RouteTableDef(), prompt_queue=queue)
    manager = storage_api.register_routes(server)
    assert storage_api.register_routes(server) is None
    app = web.Application()
    app.add_routes(server.routes)
    return app, manager, queue


def test_http_validation_save_status_and_revision_conflict(api_server, tmp_path):
    app, manager, queue = api_server
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            status = await client.get("/h3-continuum/storage/status")
            assert status.status == 200
            state = await status.json()
            assert state["path"] == "" and not manager.config_file.exists()
            destination = str(tmp_path / "scratch disk")
            checked = await client.post("/h3-continuum/storage/validate", json={"path": destination})
            assert checked.status == 200 and not manager.config_file.exists()
            calls = [client.post("/h3-continuum/storage/settings", json={"path": destination, "revision": 0}) for _ in range(2)]
            responses = await asyncio.gather(*calls)
            assert sorted(r.status for r in responses) == [200, 409]
            status = await client.get("/h3-continuum/storage/status")
            state = await status.json()
            assert state["revision"] == 1 and state["path"] == destination
            assert len([r for r in state["roots"] if r["current"]]) == 2
            assert (await client.post("/h3-continuum/storage/cleanup", json={})).status == 200
    asyncio.run(scenario())


def test_http_rejects_busy_read_only_and_arbitrary_cleanup_paths(api_server, tmp_path):
    app, manager, queue = api_server
    protected = tmp_path / "accepted.safetensors"
    protected.write_bytes(b"keep")
    async def scenario():
        async with TestClient(TestServer(app)) as client:
            prefix = "/h3-continuum/storage/"
            assert (await client.post(prefix + "cleanup", json={"path": str(protected)})).status == 400
            assert (await client.post(prefix + "cleanup", data="{}")).status == 415
            queue.pending.append("queued")
            for action, data in (("settings", {"path": "", "revision": 0}), ("cleanup", {}), ("validate", {"path": ""})):
                assert (await client.post(prefix + action, json=data)).status == 409
            queue.pending.clear()
            with manager.operation():
                assert (await client.post(prefix + "cleanup", json={})).status == 409
            manager.read_only = True
            assert (await client.get(prefix + "status")).status == 200
            assert (await client.post(prefix + "settings", json={"path": "", "revision": 0})).status == 403
            assert (await client.post(prefix + "cleanup", json={})).status == 403
            assert protected.read_bytes() == b"keep"
    asyncio.run(scenario())
