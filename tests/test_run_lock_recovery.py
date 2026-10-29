"""Run exclusion must survive stale-owner recovery, failure and process exit."""
import json
import os
from pathlib import Path
import socket
import signal
import subprocess
import sys
import threading
import time

import pytest

from ComfyUI_H3_Continuum_Join import run_storage as rs


def owner(path, pid, hostname=None):
    value = {"pid": pid, "hostname": hostname or socket.gethostname(), "token": "old"}
    path.write_text(json.dumps(value), encoding="utf-8")
    return path.read_bytes()


def test_stale_recovery_cannot_delete_a_new_owner(tmp_path, monkeypatch):
    path = tmp_path / ".lock"
    owner(path, 999999999)
    original_read = rs._read_json
    first_read, second_done = threading.Event(), threading.Event()

    def controlled_read(p):
        value = original_read(p)
        if threading.current_thread().name == "first" and value.get("token") == "old":
            first_read.set()
            assert second_done.wait(5)
        return value

    monkeypatch.setattr(rs, "_read_json", controlled_read)
    monkeypatch.setattr(rs, "_pid_exists", lambda pid: pid == os.getpid())
    locks = [rs._RunLock(path), rs._RunLock(path)]
    outcomes = []

    def attempt(index):
        try:
            locks[index].acquire()
            outcomes.append("acquired")
        except rs.RunStorageError:
            outcomes.append("busy")
        except BaseException as exc:
            outcomes.append(repr(exc))
        finally:
            if index == 1:
                second_done.set()

    a = threading.Thread(target=attempt, args=(0,), name="first")
    b = threading.Thread(target=attempt, args=(1,), name="second")
    try:
        a.start()
        assert first_read.wait(5)
        b.start()
        b.join(5)
        second_done.set()
        a.join(5)
        assert not a.is_alive() and not b.is_alive()
        assert sorted(outcomes) == ["acquired", "busy"]
        winner = next(lock for lock in locks if lock.acquired)
        assert original_read(path)["token"] == winner.token
    finally:
        second_done.set()
        a.join(5)
        for lock in locks:
            lock.release()


@pytest.mark.parametrize("kind", ["live", "foreign", "unreadable"])
def test_legacy_owner_is_preserved_and_failed_guard_is_released(tmp_path, kind):
    path = tmp_path / ".lock"
    if kind == "unreadable":
        path.write_text("{bad", encoding="utf-8")
    else:
        owner(path, os.getpid(), "foreign-host" if kind == "foreign" else None)
    before = path.read_bytes()
    lock = rs._RunLock(path)
    with pytest.raises(rs.RunStorageError):
        lock.acquire()
    assert path.read_bytes() == before
    path.unlink()  # Remove only this test's synthetic protected owner.
    lock.acquire()
    lock.release()


def test_live_exclusion_release_reacquire_and_independent_runs(tmp_path):
    a, b = rs._RunLock(tmp_path / ".lock"), rs._RunLock(tmp_path / ".lock")
    other = rs._RunLock(tmp_path / "other" / ".lock")
    a.acquire()
    try:
        with pytest.raises(rs.RunStorageError):
            a.acquire()
        with pytest.raises(rs.RunStorageError):
            b.acquire()
        other.acquire()
        other.release()
    finally:
        a.release()
    guard = tmp_path / ".lock.guard"
    identity = guard.stat().st_ino
    b.acquire()
    b.release()
    b.release()
    assert guard.is_file() and guard.stat().st_ino == identity
    assert not (tmp_path / ".lock").exists()


def test_owner_failure_releases_guard(tmp_path, monkeypatch):
    lock = rs._RunLock(tmp_path / ".lock")
    with monkeypatch.context() as patch:
        patch.setattr(lock, "_acquire_owner", lambda: (_ for _ in ()).throw(OSError("write failed")))
        with pytest.raises(OSError, match="write failed"):
            lock.acquire()
    lock.acquire()
    lock.release()


def test_release_keeps_changed_owner_and_releases_guard(tmp_path):
    path = tmp_path / ".lock"
    lock = rs._RunLock(path)
    lock.acquire()
    replacement = owner(path, os.getpid())
    lock.release()
    assert path.read_bytes() == replacement
    path.unlink()
    lock.acquire()
    lock.release()


def test_process_exit_releases_guard_and_recovers_owner(tmp_path):
    root = Path(rs.__file__).parent
    script = '''
import importlib,sys,types
from pathlib import Path
root,path,ready=sys.argv[1:]
p=types.ModuleType("ComfyUI_H3_Continuum_Join");p.__path__=[root];sys.modules[p.__name__]=p
rs=importlib.import_module(p.__name__+".run_storage")
lock=rs._RunLock(Path(path));lock.acquire()
Path(ready).write_text("ready")
sys.stdin.read()
'''
    path, ready = tmp_path / ".lock", tmp_path / "ready"
    child = subprocess.Popen([sys.executable, "-B", "-c", script, str(root), str(path), str(ready)],
                             stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 45
        while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.05)
        assert ready.exists(), "child did not acquire the real Run lock"
        with pytest.raises(rs.RunStorageError):
            rs._RunLock(path).acquire()
        # Windows venv python.exe can be a launcher. Kill the actual owner,
        # whose PID the production lock records, rather than only its launcher.
        owner_pid = json.loads(path.read_text(encoding="utf-8"))["pid"]
        os.kill(owner_pid, signal.SIGTERM)
        child.wait(timeout=10)
        child.communicate(timeout=10)
        # Keep Popen's monitor handle alive: Windows can still open an exited
        # PID, so recovery must query its exit status rather than just existence.
        lock = rs._RunLock(path)
        lock.acquire()
        lock.release()
    finally:
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=10)
