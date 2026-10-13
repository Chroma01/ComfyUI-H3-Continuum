"""Scratch relocation and cleanup regressions with real small CPU mappings."""
from __future__ import annotations

import gc
import json
import os
import subprocess
import sys
from pathlib import Path
import threading
import weakref
from types import SimpleNamespace

import pytest
import torch

from ComfyUI_H3_Continuum_Join import storage_settings as settings
from ComfyUI_H3_Continuum_Join import storage_fs as fs
from ComfyUI_H3_Continuum_Join import storage_memory as memory
from ComfyUI_H3_Continuum_Join.decode_cache.store import DecodeStore
from ComfyUI_H3_Continuum_Join.decode_cache import store as store_module
from ComfyUI_H3_Continuum_Join.tools import p20_file_backed_tensor_poc as backing
from ComfyUI_H3_Continuum_Join.v3 import file_backed_buffer as buffer


@pytest.fixture
def manager(tmp_path, monkeypatch):
    finalize, decode = tmp_path / "default-final", tmp_path / "default-decode"
    decode.mkdir()
    value = settings.StorageSettings(tmp_path / "user" / "settings.json",
        default_finalize=lambda: finalize, default_decode=lambda: decode)
    monkeypatch.setattr(settings, "_MANAGER", value)
    monkeypatch.setenv("H3_DECODE_CACHE_TEMP_DIR", str(decode))
    return value


def cache():
    value = DecodeStore(memory_probe=lambda: 10**12, headroom_bytes=0)
    value.configure("Auto", 1024**2, 1024**2, 0)
    return value


def cache_put(store, name="first"):
    x = torch.arange(24, dtype=torch.float32).reshape(2, 3, 4)
    result = store.put(name, x, "video", {}, (), store.epoch)
    assert result is not None
    return result[0]


def total_removed(result):
    return sum(row["removed_files"] for row in result["roots"])


def test_default_and_explicit_internal_paths_keep_their_precedence(manager, tmp_path, monkeypatch):
    monkeypatch.setattr(buffer.tempfile, "gettempdir", lambda: str(tmp_path))
    import sys
    monkeypatch.setitem(sys.modules, "folder_paths", SimpleNamespace(get_temp_directory=lambda: str(tmp_path)))
    assert buffer.resolve_backing_root() == tmp_path / "h3-continuum-v35-file-backed"
    manager.save(str(tmp_path / "日本語 scratch"), 0)
    assert buffer.resolve_backing_root() == tmp_path / "日本語 scratch/h3-continuum-scratch/finalize"
    assert buffer.resolve_backing_root(tmp_path / "injected") == tmp_path / "injected"
    store = cache()
    output = cache_put(store)
    assert store.root.parent == tmp_path / "日本語 scratch/h3-continuum-scratch/decode"
    assert not list(manager.default_decode().iterdir())
    del output
    store.close()


def test_validation_does_not_activate_a_path_and_settings_survive_reload(manager, tmp_path):
    destination = str(tmp_path / "other disk")
    manager.validate(destination)
    assert manager.status()["path"] == "" and not manager.config_file.exists()
    manager.save(destination, 0)
    restored = settings.StorageSettings(manager.config_file, default_finalize=manager.default_finalize,
                                        default_decode=manager.default_decode)
    assert restored.status()["path"] == destination
    with pytest.raises(settings.StorageBusy, match="refresh"):
        manager.save("", 0)
    manager.save("", 1)
    assert manager.status()["path"] == ""


def test_switch_keeps_old_finalize_alias_and_both_cache_mappings(manager, tmp_path):
    manager.save(str(tmp_path / "disk-a"), 0)
    with buffer.allocate_file_backed_image((2, 3, 4), dtype=torch.float32) as allocation:
        allocation.tensor.copy_(torch.arange(24).reshape(2, 3, 4))
        output = allocation.publish()
    alias = output[1:]
    old_final = allocation.record.data_path
    del output, allocation
    store = cache()
    first = cache_put(store)
    old_cache = store.entries["first"].path
    manager.save(str(tmp_path / "disk-b"), 1)
    second = cache_put(store, "second")
    assert old_cache.parent != store.entries["second"].path.parent
    assert torch.equal(first, second)
    result = manager.cleanup()
    assert total_removed(result) == 0
    assert old_cache.exists() and old_final.exists()
    assert alias.sum() == sum(range(12, 24))
    del first, second, alias
    gc.collect()
    result = manager.cleanup()
    assert total_removed(result) == 4  # one bin/sidecar pair and two npy files
    assert not old_cache.exists() and not old_final.exists()
    assert not store.contains("first") and not store.contains("second")
    assert cache_put(store, "third").sum() == sum(range(24))
    store.close()


def test_status_is_read_only_and_unknown_files_and_runs_are_protected(manager, tmp_path):
    manager.save(str(tmp_path / "disk"), 0)
    root = buffer.resolve_backing_root()
    unknown = root / (backing.FILE_PREFIX + "a" * 32 + ".bin")
    unknown.write_bytes(b"orphan")
    run = tmp_path / "saved-run.safetensors"
    run.write_bytes(b"accepted take")
    store = cache()
    tensor = cache_put(store)
    path = store.entries["first"].path
    del tensor
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    report = manager.status()
    assert any(row["deletable_bytes"] > 0 for row in report["roots"])
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert store.contains("first") and path.exists()
    manager.cleanup()
    assert unknown.read_bytes() == b"orphan" and run.read_bytes() == b"accepted take"
    assert not path.exists()


def test_changed_mount_is_not_recreated_or_replaced_by_default(manager, tmp_path):
    manager.save(str(tmp_path / "disk"), 0)
    scratch = tmp_path / "disk/h3-continuum-scratch"
    scratch.rename(tmp_path / "detached")
    with pytest.raises(OSError):
        buffer.allocate_file_backed_image((1,), dtype=torch.float32)
    store = cache()
    with pytest.raises(OSError):
        cache_put(store)
    assert not scratch.exists()
    assert not list(manager.default_decode().iterdir())


@pytest.mark.parametrize("kind", ["finalize", "decode"])
def test_symlink_substitution_protects_the_target(manager, tmp_path, kind):
    manager.save(str(tmp_path / "disk"), 0)
    target = tmp_path / "disk/h3-continuum-scratch" / kind
    moved = tmp_path / "kept"
    target.rename(moved)
    try:
        target.symlink_to(moved, target_is_directory=True)
    except OSError:
        pytest.skip("OS does not allow creating symbolic links")
    report = manager.cleanup()
    assert any(row["errors"] for row in report["roots"] if row["kind"] == kind and row["current"])
    assert moved.exists()


@pytest.mark.parametrize("read_only,busy", [(True, False), (False, True)])
def test_server_enforces_read_only_and_busy(manager, tmp_path, read_only, busy):
    manager.read_only = read_only
    manager.busy = lambda: busy
    for action in (lambda: manager.validate(str(tmp_path / "disk")),
                   lambda: manager.save(str(tmp_path / "disk"), 0), manager.cleanup):
        with pytest.raises(settings.StorageError):
            action()
    assert not manager.config_file.exists()


def test_active_operation_blocks_maintenance_and_freezes_configuration(manager, tmp_path):
    entered, release = threading.Event(), threading.Event()
    errors = []
    def work():
        try:
            with manager.operation():
                entered.set()
                assert release.wait(3)
        except Exception as error:
            errors.append(error)
    worker = threading.Thread(target=work)
    worker.start()
    assert entered.wait(3)
    try:
        with pytest.raises(settings.StorageBusy):
            manager.save(str(tmp_path / "disk"), 0)
        with pytest.raises(settings.StorageBusy):
            manager.cleanup()
    finally:
        release.set()
        worker.join(3)
    assert not errors and not worker.is_alive()
    manager.save(str(tmp_path / "disk"), 0)


def test_ownerless_legacy_cache_is_never_swept(manager):
    root = manager.default_decode() / "h3-decode-cache-old"
    root.mkdir()
    path = root / ("b" * 32 + ".npy")
    path.write_bytes(b"unattributed")
    manager.cleanup()
    assert path.read_bytes() == b"unattributed"


def test_dead_cache_owner_only_authorizes_registered_files(manager, monkeypatch):
    store = cache()
    tensor = cache_put(store)
    path = store.entries["first"].path
    unknown = path.parent / ("c" * 32 + ".npy")
    unknown.write_bytes(b"not ours")
    second = cache_put(store, "second")
    # Isolate the crash-recovery path: the real mapping remains protected until
    # released; only then simulate a terminated writer with no live store.
    del tensor, second
    manager._stores.clear()
    manager._cache_states.clear()
    monkeypatch.setattr(fs, "owner_alive", lambda owner: False)
    result = manager.cleanup()
    assert total_removed(result) == 2
    assert not path.exists() and unknown.read_bytes() == b"not ours"


def test_deleted_helper_keeps_mapping_until_last_alias_is_released(manager):
    store = cache()
    output = cache_put(store)
    view = output[1:]
    path = store.entries["first"].path
    ref = weakref.ref(store)
    del output, store
    gc.collect()
    assert ref() is None and path.exists()
    assert total_removed(manager.cleanup()) == 0
    assert view.sum() == sum(range(12, 24))
    del view
    gc.collect()
    assert total_removed(manager.cleanup()) == 1
    assert not path.exists()


@pytest.mark.parametrize("owner", [{}, {"pid": 1, "created": float("nan")}, {"pid": -1, "created": 1}])
def test_unknown_process_ownership_is_protected(owner):
    assert fs.owner_alive(owner)


@pytest.mark.parametrize("path", ["relative/folder", "\\\\server\\share", "//server/share", "bad\0path"])
def test_invalid_destinations_do_not_change_settings(manager, path):
    with pytest.raises(settings.StorageError):
        manager.save(path, 0)
    assert manager.status()["path"] == ""


def test_existing_unknown_scratch_folder_is_not_adopted(manager, tmp_path):
    root = tmp_path / "disk/h3-continuum-scratch"
    root.mkdir(parents=True)
    (root / "important").write_text("keep")
    with pytest.raises(settings.StorageError, match="unknown"):
        manager.save(str(tmp_path / "disk"), 0)
    assert (root / "important").read_text() == "keep"


def test_mmap_failure_does_not_activate_destination(manager, tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("mapping unsupported")
    monkeypatch.setattr(settings.mmap, "mmap", fail)
    with pytest.raises(OSError):
        manager.save(str(tmp_path / "disk"), 0)
    assert manager.status()["path"] == ""
    assert not list(tmp_path.rglob(".h3-probe-*"))


def test_manual_ram_uses_real_bytes_and_never_falls_back(monkeypatch, tmp_path):
    gib = 1024**3
    monkeypatch.setattr(buffer, "_system_memory_bytes", lambda: (16*gib, 32*gib))
    buffer.preflight_manual_buffer("RAM", 5*gib)  # no Auto 4 GiB cap
    monkeypatch.setattr(buffer, "_system_memory_bytes", lambda: (6*gib, 32*gib))
    with pytest.raises(RuntimeError, match="RAM buffer needs"):
        buffer.preflight_manual_buffer("RAM", 3*gib, tmp_path)
    assert not list(tmp_path.iterdir())
    monkeypatch.setattr(buffer, "_system_memory_bytes", lambda: (None, None))
    with pytest.raises(RuntimeError, match="unavailable"):
        buffer.preflight_manual_buffer("RAM", 1)


def test_manual_disk_and_auto_disk_shortage_are_explicit(monkeypatch, tmp_path):
    monkeypatch.setattr(buffer, "_disk_free_bytes", lambda path: 1024)
    with pytest.raises(RuntimeError, match="Disk-backed buffer needs"):
        buffer.preflight_manual_buffer("Disk-backed", 1024, tmp_path)
    assert not list(tmp_path.iterdir())


def test_cgroup_v2_uses_most_restrictive_ancestor(tmp_path):
    mount = tmp_path / "cgroup"
    child = mount / "nested"
    child.mkdir(parents=True)
    (mount / "memory.max").write_text("1000")
    (mount / "memory.current").write_text("900")
    (child / "memory.max").write_text("500")
    (child / "memory.current").write_text("200")
    proc = tmp_path / "cgroups"; proc.write_text("0::/nested\n")
    mounts = tmp_path / "mounts"; mounts.write_text(f"1 0 0:1 / {mount} rw - cgroup2 cgroup rw\n")
    assert list(memory._cgroup_limits(proc, mounts)) == [(300, 500), (100, 1000)]


def test_real_terminated_cache_writer_is_reclaimed(manager, tmp_path):
    manager.save(str(tmp_path / "disk"), 0)
    repository = Path(__file__).resolve().parents[1]
    script = '''
import os,sys,types
from pathlib import Path
import torch
package=types.ModuleType("storage_child")
package.__path__=[sys.argv[1]]
sys.modules[package.__name__]=package
from storage_child import storage_settings as settings
from storage_child.decode_cache.store import DecodeStore
manager=settings.StorageSettings(Path(sys.argv[2]),default_finalize=lambda:Path(sys.argv[3]),default_decode=lambda:Path(sys.argv[3]))
settings.install_manager(manager)
store=DecodeStore(memory_probe=lambda:10**12,headroom_bytes=0)
store.configure("Auto",1024**2,1024**2,0)
output=store.put("entry",torch.ones(2,3,4),"video",{},(),store.epoch)
assert output is not None
os._exit(0)
'''
    subprocess.run([sys.executable, "-c", script, str(repository), str(manager.config_file), str(tmp_path)],
                   check=True, timeout=30)
    cache_root = tmp_path / "disk/h3-continuum-scratch/decode"
    assert len(list(cache_root.rglob("*.npy"))) == 1
    assert total_removed(manager.cleanup()) == 1
    assert not list(cache_root.iterdir())


def test_existing_manager_refuses_replaced_root_before_deletion(tmp_path):
    root = tmp_path / "original"
    manager = backing.StorageLifetimeManager(root)
    with manager.allocate((2,), dtype=torch.float32) as allocation:
        allocation.tensor.fill_(3)
        output = allocation.publish()
    record = allocation.record
    del allocation, output
    moved = tmp_path / "detached"
    root.rename(moved)
    root.mkdir()
    protected = root / record.data_path.name
    protected.write_bytes(b"replacement data")
    with pytest.raises(backing.FileBackedPoCError, match="changed"):
        manager.collect_ready()
    assert protected.read_bytes() == b"replacement data"


def test_failed_unpublished_cache_write_remains_cleanable(manager, monkeypatch):
    store = cache()
    def broken_blocks(tensor):
        yield b"partial"
        raise OSError("writer interrupted")
    original_unlink = Path.unlink
    def busy_temp(path, *args, **kwargs):
        if path.suffix == ".tmp":
            raise PermissionError("temporarily locked")
        return original_unlink(path, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(store_module, "tensor_blocks", broken_blocks)
        patch.setattr(Path, "unlink", busy_temp)
        with pytest.raises(OSError, match="writer interrupted"):
            cache_put(store)
    assert not store.entries
    assert len(list(store.root.glob("*.tmp"))) == 1
    assert total_removed(manager.cleanup()) == 1
    assert not list(store.root.glob("*.tmp"))


def test_two_processes_cannot_overwrite_the_same_settings_revision(manager, tmp_path):
    repository = Path(__file__).resolve().parents[1]
    script = '''
import sys,types
from pathlib import Path
package=types.ModuleType("storage_child")
package.__path__=[sys.argv[1]]
sys.modules[package.__name__]=package
from storage_child import storage_settings as settings
manager=settings.StorageSettings(Path(sys.argv[2]),default_finalize=lambda:Path(sys.argv[3]),default_decode=lambda:Path(sys.argv[3]))
sys.stdin.read(1)
try:
 manager.save("",0)
 print("saved")
except settings.StorageBusy:
 print("conflict")
'''
    command = [sys.executable, "-c", script, str(repository), str(manager.config_file), str(tmp_path)]
    children = [subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True) for _ in range(2)]
    try:
        for child in children:
            child.stdin.write("x"); child.stdin.flush()
        outputs = [child.communicate(timeout=15) for child in children]
        assert all(child.returncode == 0 for child in children), outputs
        assert sorted(out.strip() for out, err in outputs) == ["conflict", "saved"]
        assert manager.status()["revision"] == 1
    finally:
        for child in children:
            if child.poll() is None:
                child.kill(); child.wait()


def test_cleanup_reports_a_failed_unlink_and_can_retry(manager, monkeypatch):
    store = cache()
    output = cache_put(store)
    path = store.entries["first"].path
    del output
    original = Path.unlink
    def denied(value, *args, **kwargs):
        if value == path:
            raise PermissionError("file locked")
        return original(value, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", denied)
        result = manager.cleanup()
    assert total_removed(result) == 0 and path.exists()
    assert any(row["errors"] for row in result["roots"])
    assert total_removed(manager.cleanup()) == 1 and not path.exists()


def test_finalize_startup_also_preserves_ownerless_files(manager, tmp_path):
    manager.save(str(tmp_path / "disk"), 0)
    root = buffer.resolve_backing_root()
    orphan = root / (backing.FILE_PREFIX + "d" * 32 + ".bin")
    orphan.write_bytes(b"unknown ownership")
    with buffer.allocate_file_backed_image((1,), dtype=torch.float32) as allocation:
        allocation.tensor.fill_(1)
        output = allocation.publish()
    assert output.item() == 1
    assert orphan.read_bytes() == b"unknown ownership"


@pytest.mark.parametrize("suffix", [".bin", ".json"])
def test_finalize_cleanup_does_not_follow_file_links(manager, tmp_path, monkeypatch, suffix):
    manager.save(str(tmp_path / "disk"), 0)
    with buffer.allocate_file_backed_image((1,), dtype=torch.float32) as allocation:
        output = allocation.publish()
    record = allocation.record
    del allocation, output
    target = record.data_path if suffix == ".bin" else record.metadata_path
    outside = tmp_path / ("outside" + suffix)
    target.rename(outside)
    try:
        target.symlink_to(outside)
    except OSError:
        pytest.skip("File symlinks are unavailable")
    before = outside.read_bytes()
    assert total_removed(manager.cleanup()) == 0
    assert target.is_symlink() and outside.read_bytes() == before


def test_finalize_failed_delete_keeps_ownership_for_retry(manager, tmp_path, monkeypatch):
    manager.save(str(tmp_path / "disk"), 0)
    with buffer.allocate_file_backed_image((1,), dtype=torch.float32) as allocation:
        output = allocation.publish()
    record = allocation.record
    del allocation, output
    original = Path.unlink
    def denied(value, *args, **kwargs):
        if value == record.data_path:
            raise PermissionError("file locked")
        return original(value, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", denied)
        result = manager.cleanup()
    assert total_removed(result) == 0 and record.metadata_path.exists()
    assert any(row["errors"] for row in result["roots"])
    assert total_removed(manager.cleanup()) == 2
