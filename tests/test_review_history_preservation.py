"""Failure boundaries must never reopen an already published Take."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest
import torch

from ComfyUI_H3_Continuum_Join import graph_contract, run_storage as rs
from ComfyUI_H3_Continuum_Join.project_manager import ProjectManager
from . import test_v38_review_run_storage as cases


def _open(root, contract, *, safe=True):
    # Sampling/Core observation is synthetic; persistence and provenance are real.
    rs.build_sampling_contract = lambda **kwargs: (copy.deepcopy(contract), safe, [])
    graph_contract.build_upstream_graph_contract = lambda *a, **k: ({}, True, [])
    c = rs.RunStorageController("phase-d-review")
    c.run_root = root / "runs" / c.run_name
    c.revisions_root = c.run_root / "revisions"
    c.lock = rs._RunLock(c.run_root / ".lock")
    c.configure_review(generation_mode="Review Each Chunk", review_action="Continue / Next")
    return c


def _prepare(c, contract):
    return c.prepare(
        model=None, model_fingerprint_value="", clip=None, video_vae=None,
        sampler=None, sigmas=torch.ones(2),
        prompt_plan={"prompts": [f"prompt {i+1}" for i in range(contract["chunk_count"])]},
        width=96, height=64, chunk_seconds=5, continuity="", audio_continuity=True,
        base_seed=1234, reroll_from_chunk=0, reroll_nonce=0, first_frame_hash="",
        last_frame_hash="", identity_hash="", strict_compatibility=False,
        existing_session=None, conditioning_mode="t2va",
    )


def _fingerprints(c):
    return {str(p.relative_to(c.run_root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [c._manifest_path(), *c.revision_root.glob("chunks/*.safetensors")]}


def _saved(tmp_path, prefix=1, chunks=3):
    contract = cases._contract(chunks=chunks)
    old = cases._persist(tmp_path, contract, prefix=prefix, review_unit=(prefix, prefix),
                         updated_utc="2026-09-03T00:00:01+00:00")
    runs = tmp_path / "runs"
    runs.mkdir()
    old.run_root.rename(runs / old.run_name)
    old.run_root = runs / old.run_name
    old.revisions_root = old.run_root / "revisions"
    old.revision_root = old.revisions_root / old.revision_id
    manager = ProjectManager(tmp_path / "management", runs)
    uid = lambda: str(uuid.uuid4())
    p = manager.create("Synthetic Project", uid(), uid())
    p = manager.mutate(p["id"], p["revision"], uid(), "attach_attempt",
                       name="Trial", run_name=old.run_name)
    p = manager.mutate(p["id"], p["revision"], uid(), "savepoint",
                       attempt_id=p["attempts"][0]["id"], name="Saved",
                       revision_id=cases._project(old)["canonical_head_revision_id"])
    return old, contract, manager, p["id"], p["savepoints"][0]["id"]


@pytest.fixture(autouse=True)
def restore_observers(monkeypatch):
    # _open also runs in a child process; retain the original globals in pytest.
    monkeypatch.setattr(rs, "build_sampling_contract", rs.build_sampling_contract)
    monkeypatch.setattr(graph_contract, "build_upstream_graph_contract", graph_contract.build_upstream_graph_contract)


@pytest.mark.parametrize("prefix", [1, 3])
def test_failed_continue_preserves_take_and_named_savepoint(tmp_path, prefix):
    old, contract, manager, project_id, point = _saved(tmp_path, prefix)
    before = _fingerprints(old)
    saved = manager.prepare(project_id, point)
    ids = [v["revision_id"] for v in cases._project(old)["group_revisions"]]
    c = _open(tmp_path, contract)
    with pytest.raises(RuntimeError, match="injected"):
        with c:
            session = _prepare(c, contract)
            assert len(session["chunks"]) == prefix
            assert _fingerprints(old) == before
            assert manager.prepare(project_id, point) == saved
            assert [v["revision_id"] for v in cases._project(old)["group_revisions"]] == ids
            raise RuntimeError("injected interruption")
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point) == saved
    fresh = _open(tmp_path, contract)
    fresh.prompts = [f"prompt {i+1}" for i in range(3)]
    fresh.configure_review(generation_mode="Review Each Chunk", review_action="Continue / Next",
                           take_action="Use This Take", take_group=prefix,
                           take_revision_id=saved["revision_id"])
    assert fresh._validated_take_selection(contract)["validated_prefix_count"] == prefix


def test_successful_continue_preserves_old_ids_and_publishes_new_chain(tmp_path):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    saved = manager.prepare(project_id, point)
    c = _open(tmp_path, contract)
    with c:
        session = _prepare(c, contract)
        assert c.revision_id != old.revision_id
        assert c.contract == contract
        new = cases._entry(1, contract)
        c.commit_group((new,), positions=(1,))
        c.mark_review_group(start=2, end=2, physical_group=2)
        c.finalize(session={"session_id": "synthetic", "chunks": session["chunks"] + [new]},
                   report="", review_pause_metadata=c.review_pause_metadata())
    project = cases._project(c)
    assert len(project["group_revisions"]) == 2
    assert project["canonical_chain"][0] == saved["revision_id"]
    assert project["canonical_storage_revision_id"] == c.revision_id
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point) == saved
    assert manager._capture(old.run_name, project["canonical_head_revision_id"])[0]


def test_durable_unfinished_group_is_resumed_but_not_listed_as_a_take(tmp_path):
    old, contract, manager, project_id, point = _saved(tmp_path, chunks=4)
    before = _fingerprints(old)
    c = _open(tmp_path, contract)
    with pytest.raises(RuntimeError, match="injected"):
        with c:
            _prepare(c, contract)
            c.commit_group((cases._entry(1, contract),), positions=(1,))
            raise RuntimeError("injected after raw commit")
    assert len(cases._project(old)["group_revisions"]) == 1
    fresh = _open(tmp_path, contract)
    with fresh:
        session = _prepare(fresh, contract)
        assert len(session["chunks"]) == 2
        assert fresh.revision_id == c.revision_id
        assert fresh.effective_reroll_nonce == c.effective_reroll_nonce == 0
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point)["generation_reusable"] is True


def test_project_publication_failure_does_not_downgrade_sealed_manifest(tmp_path, monkeypatch):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    c = _open(tmp_path, contract)
    with pytest.raises(OSError, match="publication"):
        with c:
            session = _prepare(c, contract)
            new = cases._entry(1, contract)
            c.commit_group((new,), positions=(1,))
            c.mark_review_group(start=2, end=2, physical_group=2)
            def fail(**kwargs):
                raise OSError("project publication")
            monkeypatch.setattr(c, "_write_project", fail)
            c.finalize(session={"session_id": "synthetic", "chunks": session["chunks"] + [new]},
                       report="", review_pause_metadata=c.review_pause_metadata())
    disk = json.loads(c._manifest_path().read_text())
    assert disk["status"] == "review_ready"
    assert len(disk["branch_provenance"]["active_chain"]) == 2
    old._write_project()
    assert len(cases._project(old)["group_revisions"]) == 2
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point)["generation_reusable"] is True


def test_abrupt_process_exit_leaves_published_history_intact(tmp_path):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    code = """
import json,os,sys,runpy,importlib.util,types
from pathlib import Path
sys.path.insert(0,sys.argv[1])
runpy.run_path(str(Path(sys.argv[1])/'tests'/'conftest.py'))
import torch
def no_cuda(*a,**k): raise AssertionError('CUDA prohibited in crash fixture')
torch.cuda._lazy_init=no_cuda; torch.cuda.init=no_cuda; torch._C._cuda_init=no_cuda
package=types.ModuleType('history_cases');package.__path__=[str(Path(sys.argv[1])/'tests')]
sys.modules['history_cases']=package
spec=importlib.util.spec_from_file_location('history_cases.history',Path(sys.argv[1])/'tests'/'test_review_history_preservation.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
_open,_prepare=module._open,module._prepare
contract=json.loads(sys.argv[3])
with _open(Path(sys.argv[2]),contract) as c:
    _prepare(c,contract)
    os._exit(23)
"""
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-B", "-c", code, str(root), str(tmp_path), json.dumps(contract)],
                            cwd=root, capture_output=True, text=True, timeout=60)
    assert result.returncode == 23, result.stdout + result.stderr
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point)["generation_reusable"] is True
    # Windows runners can retain an exited process object. This fixture tests
    # history durability, not PID probing: remove only the lock of our child,
    # whose exit has been awaited above. Never touch a user Run lock.
    lock_path = old.run_root / ".lock"
    assert json.loads(lock_path.read_text())["pid"] != os.getpid()
    lock_path.unlink()
    with _open(tmp_path, contract) as fresh:
        assert len(_prepare(fresh, contract)["chunks"]) == 1


def test_unsafe_contract_does_not_reuse_safe_history(tmp_path):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    with _open(tmp_path, contract, safe=False) as c:
        assert _prepare(c, contract) is None
        assert c.reused_count == 0
        assert rs._reusable_manifest(c.manifest) is False
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point)["generation_reusable"] is True


@pytest.mark.parametrize("action", ["Use This Take", "Continue From Here"])
def test_explicit_take_actions_preserve_original_savepoint_on_failure(tmp_path, action):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    saved = manager.prepare(project_id, point)
    c = _open(tmp_path, contract)
    c.configure_review(generation_mode="Review Each Chunk", review_action="Continue / Next",
                       take_action=action, take_group=1, take_revision_id=saved["revision_id"])
    with pytest.raises(RuntimeError, match="explicit"):
        with c:
            _prepare(c, contract)
            if action == "Continue From Here":
                c.commit_group((cases._entry(1, c.contract),), positions=(1,))
                # Even an unfinished selected branch has internally consistent
                # provenance, without publishing the new group as an accepted Take.
                assert len(c._validated_review_head(c.manifest, current_contract=c.contract)["entries"]) == 2
            raise RuntimeError("explicit action failure")
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point) == saved


@pytest.mark.parametrize("timing", ["before", "after"])
def test_atomic_seal_failure_keeps_old_take_and_never_downgrades_published_seal(tmp_path, monkeypatch, timing):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    c = _open(tmp_path, contract)
    with pytest.raises(OSError, match="seal"):
        with c:
            session = _prepare(c, contract)
            new = cases._entry(1, contract)
            c.commit_group((new,), positions=(1,))
            c.mark_review_group(start=2, end=2, physical_group=2)
            write = c._write_manifest
            def fail():
                if timing == "after":
                    write()
                raise OSError("seal durability failure")
            monkeypatch.setattr(c, "_write_manifest", fail)
            c.finalize(session={"session_id": "synthetic", "chunks": session["chunks"] + [new]},
                       report="", review_pause_metadata=c.review_pause_metadata())
    disk = json.loads(c._manifest_path().read_text())
    assert disk["status"] == ("in_progress" if timing == "before" else "review_ready")
    assert len(cases._project(old)["group_revisions"]) == (1 if timing == "before" else 2)
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point)["generation_reusable"] is True


def test_incompatible_working_child_is_not_overwritten(tmp_path):
    old, contract, manager, project_id, point = _saved(tmp_path)
    before = _fingerprints(old)
    child_id = rs._continuation_revision_identity(old.manifest)
    path = old.revisions_root / child_id / "manifest.json"
    rs._write_json(path, dict(old.manifest, revision_id=child_id, status="in_progress", contract_sha256="invalid"))
    child_before = path.read_bytes()
    with pytest.raises(rs.RunStorageError, match="collision"):
        with _open(tmp_path, contract) as c:
            _prepare(c, contract)
    assert path.read_bytes() == child_before
    assert _fingerprints(old) == before
    assert manager.prepare(project_id, point)["generation_reusable"] is True
