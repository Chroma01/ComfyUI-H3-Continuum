"""Management writes must never alter existing Run data or generation identity."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import pytest

from ComfyUI_H3_Continuum_Join import project_manager as pm
from ComfyUI_H3_Continuum_Join.run_storage import resolve_run_storage_name
from .test_v38_review_run_storage import _contract, _entry, _persist, _persist_resolved_branch, _project, _resolve


def uid():
    return str(uuid.uuid4())


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def manager(tmp_path):
    return pm.ProjectManager(tmp_path / "user" / "projects", tmp_path / "runs")


def create(manager):
    return manager.create("Practice", uid(), uid())


def change(manager, project, action, **kwargs):
    return manager.mutate(project["id"], project["revision"], uid(), action, **kwargs)


def run_fixture(tmp_path, manager, *, prefix=2, terminal=False):
    controller = _persist(tmp_path / "producer", _contract(chunks=3, terminal=terminal),
                          prefix=prefix, review_unit=(2, 3) if terminal and prefix == 3 else (prefix, prefix),
                          updated_utc="2026-10-23T00:00:00Z")
    controller._write_project()
    manager.runs_root.mkdir(parents=True, exist_ok=True)
    controller.run_root.rename(manager.runs_root / controller.run_name)
    controller.run_root = manager.runs_root / controller.run_name
    controller.revisions_root = controller.run_root / "revisions"
    controller.revision_root = controller.revisions_root / controller.revision_id
    project = json.loads((controller.run_root / "project.json").read_text())
    return controller, project


def saved_fixture(tmp_path, manager, *, prefix=2):
    controller, history = run_fixture(tmp_path, manager, prefix=prefix)
    project = change(manager, create(manager), "attach_attempt", name="Existing", run_name=controller.run_name)
    attempt = project["attempts"][0]
    project = change(manager, project, "savepoint", attempt_id=attempt["id"], name="Chosen prefix",
                     revision_id=history["canonical_head_revision_id"])
    return controller, project, project["savepoints"][0]


def test_unused_manager_creates_nothing(manager):
    assert manager.list_projects() == {"projects": [], "errors": []}
    assert not manager.directory.exists() and not manager.runs_root.exists()


def test_new_attempt_is_independent_and_has_no_run_files(manager):
    project = change(manager, create(manager), "new_attempt", name="Try A")
    project = change(manager, project, "new_attempt", name="Try B")
    first, second = project["attempts"]
    assert first["run_name"] == second["run_name"] == ""
    assert first["project_id"] != second["project_id"]
    assert first["storage_name"] == resolve_run_storage_name(project_id=first["project_id"], legacy_run_name="")
    assert not manager.runs_root.exists()


def test_create_and_mutation_are_idempotent(manager):
    project_id, op = uid(), uid()
    initial = manager.create("Project", project_id, op)
    assert manager.create("Project", project_id, op) == initial
    operation = uid()
    value = manager.mutate(project_id, initial["revision"], operation, "new_attempt", name="A")
    assert manager.mutate(project_id, initial["revision"], operation, "new_attempt", name="A") == value
    with pytest.raises(pm.ProjectManagerError, match="different request"):
        manager.mutate(project_id, initial["revision"], operation, "new_attempt", name="B")


def test_replay_after_later_update_keeps_current_revision(manager):
    project = create(manager)
    operation = uid()
    first = manager.mutate(project["id"], 1, operation, "new_attempt", name="A")
    latest = change(manager, first, "rename_project", name="Updated")
    replay = manager.mutate(project["id"], 1, operation, "new_attempt", name="A")
    assert replay["revision"] == latest["revision"]
    assert replay["name"] == "Updated" and len(replay["attempts"]) == 1
    assert replay["last_result"]["attempt_id"] == first["attempts"][0]["id"]


def test_same_revision_two_writers_only_one_succeeds(manager):
    project = create(manager)
    def write(name):
        try:
            return manager.mutate(project["id"], 1, uid(), "rename_project", name=name)["revision"]
        except pm.ProjectManagerError as error:
            return error.status
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(write, ["A", "B"]))
    assert sorted(results) == [2, 409]
    assert manager.get(project["id"])["revision"] == 2


def test_failed_atomic_replace_preserves_previous_json(manager, monkeypatch):
    project = create(manager)
    before = manager._file(project["id"]).read_bytes()
    def fail(*args):
        raise OSError("disk failure")
    monkeypatch.setattr(pm.os, "replace", fail)
    with pytest.raises(OSError, match="disk failure"):
        change(manager, project, "rename_project", name="Never committed")
    assert manager._file(project["id"]).read_bytes() == before
    assert not list(manager.directory.glob("*.tmp"))


def test_corrupt_project_is_reported_and_never_overwritten(manager):
    project = create(manager)
    path = manager._file(project["id"])
    path.write_bytes(b"{partial")
    result = manager.list_projects()
    assert result["projects"] == [] and len(result["errors"]) == 1
    with pytest.raises(pm.ProjectManagerError, match="invalid"):
        change(manager, project, "rename_project", name="No")
    assert path.read_bytes() == b"{partial"


@pytest.mark.parametrize("project_id", ["../outside", "", "0" * 32, "00000000-0000-0000-0000-000000000000", None])
def test_project_paths_require_uuid(manager, project_id):
    with pytest.raises(pm.ProjectManagerError):
        manager.get(project_id)
    assert not manager.directory.exists()


@pytest.mark.parametrize("run_name", ["../outside", "C:\\outside", "a/b", "NUL", None])
def test_attach_path_traversal_rejected(manager, run_name):
    project = create(manager)
    with pytest.raises(pm.ProjectManagerError):
        change(manager, project, "attach_attempt", name="No", run_name=run_name)
    assert manager.get(project["id"])["revision"] == 1


@pytest.mark.parametrize("action,payload", [
    ("rename_project", {"name": "Yes", "path": "other"}),
    ("archive_project", {"archived": 1}), ("new_attempt", {"name": ""}),
    ("delete_project", {}), ("savepoint", {"attempt_id": uid(), "name": "X"}),
])
def test_strict_fields(manager, action, payload):
    project = create(manager)
    with pytest.raises(pm.ProjectManagerError):
        change(manager, project, action, **payload)
    assert manager.get(project["id"])["revision"] == 1


def test_journal_never_evicts_old_keys(manager, monkeypatch):
    project = create(manager)
    monkeypatch.setattr(pm, "MAX_OPERATIONS", 1)
    with pytest.raises(pm.ProjectManagerError, match="journal is full"):
        change(manager, project, "rename_project", name="No")
    assert manager.get(project["id"]) == project


def test_labels_archive_and_prepare_do_not_change_takes(tmp_path, manager):
    controller, project, saved = saved_fixture(tmp_path, manager)
    before = hashes(manager.runs_root)
    project = change(manager, project, "rename_savepoint", savepoint_id=saved["id"], name="Favourite")
    project = change(manager, project, "archive_attempt", attempt_id=project["attempts"][0]["id"], archived=True)
    project = change(manager, project, "archive_project", archived=True)
    result = manager.prepare(project["id"], saved["id"])
    assert result["revision_id"] == saved["revision_id"] and result["group"]["end"] == 2
    assert result["run_name"] == controller.run_name and result["project_id"] == ""
    assert hashes(manager.runs_root) == before


def test_append_keeps_savepoint_endpoint_and_resume_valid(tmp_path, manager):
    controller, project, saved = saved_fixture(tmp_path, manager, prefix=1)
    original_saved = deepcopy(saved)
    controller.commit_group((_entry(1, controller.contract),), positions=(1,))
    controller.review_execution.next_review_unit_start = 2
    controller.review_execution.next_review_unit_end = 2
    controller.review_execution.next_review_physical_group = 2
    controller.pending_review_pause_metadata = None
    controller.mark_review_group(start=2, end=2, physical_group=2)
    controller.finalize(session={"chunks": [_entry(index, controller.contract) for index in range(2)]},
                        report="continued", review_pause_metadata=controller.review_pause_metadata())
    result = manager.prepare(project["id"], saved["id"])
    assert result["group"]["end"] == 1
    assert manager.get(project["id"])["savepoints"][0] == original_saved


def test_raw_corruption_is_rejected_without_touching_metadata(tmp_path, manager):
    controller, project, saved = saved_fixture(tmp_path, manager)
    raw = next(controller.run_root.rglob("*.safetensors"))
    content = raw.read_bytes()
    raw.write_bytes(content[:-1] + bytes([content[-1] ^ 1]))
    before = hashes(manager.directory)
    with pytest.raises(pm.ProjectManagerError, match="SHA-256"):
        manager.prepare(project["id"], saved["id"])
    assert hashes(manager.directory) == before


def test_missing_raw_does_not_silently_retarget_savepoint(tmp_path, manager):
    controller, project, saved = saved_fixture(tmp_path, manager)
    next(controller.run_root.rglob("*.safetensors")).unlink()
    with pytest.raises(pm.ProjectManagerError, match="integrity"):
        manager.prepare(project["id"], saved["id"])
    assert manager.get(project["id"])["savepoints"][0] == saved


def test_unknown_saved_signature_stays_readonly(tmp_path, manager):
    controller, history = run_fixture(tmp_path, manager)
    controller.manifest["resume_safe"] = False
    controller._write_manifest()
    controller._write_project()
    project = change(manager, create(manager), "attach_attempt", name="Unsafe", run_name=controller.run_name)
    project = change(manager, project, "savepoint", attempt_id=project["attempts"][0]["id"], name="History",
                     revision_id=history["canonical_head_revision_id"])
    saved = project["savepoints"][0]
    assert saved["generation_reusable"] is False
    with pytest.raises(pm.ProjectManagerError, match="read-only"):
        manager.prepare(project["id"], saved["id"])
    # Management labels never turn an old unsafe savepoint reusable.
    controller.manifest["resume_safe"] = True
    controller._write_manifest()
    with pytest.raises(pm.ProjectManagerError, match="read-only"):
        manager.prepare(project["id"], saved["id"])


def test_changed_manifest_contract_rejected(tmp_path, manager):
    controller, project, saved = saved_fixture(tmp_path, manager)
    controller.manifest["contract"]["global"]["base_seed"] += 1
    controller._write_manifest()
    with pytest.raises(pm.ProjectManagerError, match="integrity"):
        manager.prepare(project["id"], saved["id"])


def test_changed_ancestry_rejected(tmp_path, manager):
    controller, project, saved = saved_fixture(tmp_path, manager)
    path = controller.run_root / "project.json"
    history = json.loads(path.read_text())
    history["group_revisions"][-1]["parent_revision_id"] = None
    path.write_text(json.dumps(history))
    with pytest.raises(pm.ProjectManagerError, match="integrity"):
        manager.prepare(project["id"], saved["id"])


def test_source_changes_between_validation_and_save_hold_operation(tmp_path, manager, monkeypatch):
    controller, history = run_fixture(tmp_path, manager)
    project = change(manager, create(manager), "attach_attempt", name="A", run_name=controller.run_name)
    before = hashes(manager.directory)
    original = manager._capture
    def capture_then_change(*args):
        result = original(*args)
        path = controller.run_root / "project.json"
        path.write_bytes(path.read_bytes() + b"\n")
        return result
    monkeypatch.setattr(manager, "_capture", capture_then_change)
    with pytest.raises(pm.ProjectManagerError, match="changed"):
        change(manager, project, "savepoint", attempt_id=project["attempts"][0]["id"], name="Hold",
               revision_id=history["canonical_head_revision_id"])
    assert hashes(manager.directory) == before


def test_terminal_pair_is_one_savepoint(tmp_path, manager):
    controller, history = run_fixture(tmp_path, manager, prefix=3, terminal=True)
    project = change(manager, create(manager), "attach_attempt", name="Pair", run_name=controller.run_name)
    project = change(manager, project, "savepoint", attempt_id=project["attempts"][0]["id"], name="All",
                     revision_id=history["canonical_head_revision_id"])
    saved = project["savepoints"][0]
    assert saved["group"] == {"start": 2, "end": 3, "physical_group": 2}
    assert len(saved["snapshot"]["ancestry"]) == 2
    assert manager.prepare(project["id"], saved["id"])["group"] == saved["group"]


def test_reparse_paths_rejected_without_reading_target(tmp_path, manager, monkeypatch):
    project = create(manager)
    real = Path.lstat
    def linked(path, *args, **kwargs):
        if path == manager.directory:
            class Stat:
                st_mode = 0o040755
                st_file_attributes = 0x400
            return Stat()
        return real(path, *args, **kwargs)
    monkeypatch.setattr(Path, "lstat", linked)
    with pytest.raises(pm.ProjectManagerError, match="Linked"):
        manager.get(project["id"])


def test_actual_old_v5_fixture_is_preserved_and_never_promoted(manager):
    source = Path(__file__).parent / "fixtures" / "v39_sampling_v5"
    history = json.loads((source / "project.json").read_text())
    run_name = history["run_name"]
    shutil.copytree(source, manager.runs_root / run_name)
    before = hashes(manager.runs_root)
    project = change(manager, create(manager), "attach_attempt", name="Legacy", run_name=run_name)
    project = change(manager, project, "savepoint", attempt_id=project["attempts"][0]["id"], name="Read-only",
                     revision_id=history["canonical_head_revision_id"])
    assert project["savepoints"][0]["generation_reusable"] is False
    with pytest.raises(pm.ProjectManagerError, match="read-only"):
        manager.prepare(project["id"], project["savepoints"][0]["id"])
    assert hashes(manager.runs_root) == before


@pytest.mark.parametrize("damage", ["attempt_type", "duplicate_attempt", "storage_identity", "archive_type", "journal_id", "journal_revision"])
def test_corrupt_nested_metadata_is_not_rewritten(manager, damage):
    project = change(manager, create(manager), "new_attempt", name="A")
    bad = deepcopy(project)
    if damage == "attempt_type":
        bad["attempts"][0] = "not an object"
    elif damage == "duplicate_attempt":
        bad["attempts"].append(deepcopy(bad["attempts"][0]))
    elif damage == "storage_identity":
        bad["attempts"][0]["storage_name"] = "some-other-run"
    elif damage == "archive_type":
        bad["attempts"][0]["archived"] = "false"
    elif damage == "journal_id":
        bad["operations"][1]["id"] = bad["operations"][0]["id"]
    else:
        bad["revision"] += 1
    path = manager._file(project["id"])
    path.write_text(json.dumps(bad))
    before = path.read_bytes()
    with pytest.raises(pm.ProjectManagerError, match="damaged"):
        change(manager, project, "rename_project", name="Not saved")
    assert path.read_bytes() == before


def test_os_lock_excludes_another_process_and_releases_on_exit(manager):
    project = create(manager)
    root = Path(__file__).resolve().parents[1]
    script = '''
import importlib.util, pathlib, sys, types
root, directory, runs, project_id = sys.argv[1:]
package = types.ModuleType("fixture_package")
package.__path__ = [root]
sys.modules["fixture_package"] = package
from fixture_package.project_manager import ProjectManager
with ProjectManager(directory, runs)._lock(project_id):
    print("locked", flush=True)
    sys.stdin.readline()
'''
    process = subprocess.Popen([sys.executable, "-B", "-c", script, str(root), str(manager.directory),
                                str(manager.runs_root), project["id"]], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert process.stdout.readline().strip() == "locked"
        with pytest.raises(pm.ProjectManagerError) as caught:
            change(manager, project, "rename_project", name="Blocked")
        assert caught.value.status == 423
    finally:
        process.communicate("release\n", timeout=15)
    assert process.returncode == 0
    assert change(manager, project, "rename_project", name="After release")["name"] == "After release"


def test_explicit_older_take_branch_with_mixed_producers_is_pinnable(tmp_path, manager):
    # Actual RunStorage writes and Take selection, not a fabricated provenance DAG.
    work = tmp_path / "branch_producer"
    original = _persist(work, _contract(chunks=3), prefix=2, review_unit=(2, 2),
                        updated_utc="2026-10-23T00:00:00Z")
    original_history = _project(original)
    first = original_history["canonical_chain"][0]
    old_head = original_history["canonical_head_revision_id"]
    original_files = hashes(original.revisions_root)
    selected, resolved, nonce, decision = _resolve(work, _contract(chunks=3),
        take_action="Continue From Here", take_group=1, take_revision_id=first)
    assert decision == "branch_from_take" and nonce > 0
    branch = _persist_resolved_branch(selected, resolved, new_positions=(1,))
    history = _project(branch)
    assert history["canonical_chain"][0] == first
    assert history["canonical_head_revision_id"] != old_head
    assert len({record["storage_revision_id"] for record in branch.manifest["chunks"]}) == 2
    after_branch = hashes(branch.revisions_root)
    assert all(after_branch[path] == digest for path, digest in original_files.items())
    manager.runs_root.mkdir(parents=True, exist_ok=True)
    branch.run_root.rename(manager.runs_root / branch.run_name)
    protected = hashes(manager.runs_root)
    project = change(manager, create(manager), "attach_attempt", name="Mixed source", run_name=branch.run_name)
    project = change(manager, project, "savepoint", attempt_id=project["attempts"][0]["id"], name="New Chunk 2",
                     revision_id=history["canonical_head_revision_id"])
    saved = project["savepoints"][0]
    assert len({record["storage_revision_id"] for record in saved["snapshot"]["raw"]}) == 2
    prepared = manager.prepare(project["id"], saved["id"])
    assert prepared["revision_id"] == history["canonical_head_revision_id"]
    assert prepared["group"] == {"start": 2, "end": 2, "physical_group": 2}
    # The older Chunk 2 remains independently selectable and pinnable.
    project = change(manager, project, "savepoint", attempt_id=project["attempts"][0]["id"], name="Old Chunk 2",
                     revision_id=old_head)
    assert manager.prepare(project["id"], project["savepoints"][1]["id"])["revision_id"] == old_head
    assert hashes(manager.runs_root) == protected
