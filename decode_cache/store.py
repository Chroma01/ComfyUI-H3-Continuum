"""Private, disposable decoded tensors. No Run Storage or global GPU lifecycle access."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import threading
import uuid
import weakref
from contextlib import nullcontext
from collections import OrderedDict
from dataclasses import dataclass, field

import numpy as np
import torch

from .identity import CacheBypass, tensor_blocks, tensor_digest

if "." in __package__:
    from .. import storage_settings, storage_fs
    from ..storage_memory import system_memory_bytes
else:  # The existing standalone cache test/probe entry points remain supported.
    storage_settings = storage_fs = None
    system_memory_bytes = None

MiB = 1024**2
GiB = 1024**3


def available_ram():
    if system_memory_bytes is not None:
        return system_memory_bytes()[0] or 0
    try:
        import psutil  # already provided by ComfyUI; optional for cache operation
        return int(psutil.virtual_memory().available)
    except (ImportError, OSError, AttributeError):
        return 0  # unknown headroom must not trigger RAM retention


@dataclass
class Entry:
    shape: tuple
    dtype: str
    digest: str
    payload_bytes: int
    guards: tuple
    extra: dict
    tensor: torch.Tensor | None = None
    path: Path | None = None
    file_bytes: int = 0
    leases: list = field(default_factory=list)

    def live(self):
        self.leases[:] = [ref for ref in self.leases if ref() is not None]
        return bool(self.leases)


def _cleanup_private_files(state):
    """Best effort at object/process exit; never close arrays still owned downstream."""
    with state.get("lock", nullcontext()):
        _cleanup_private_files_locked(state)


def _cleanup_private_files_locked(state):
    for path, entry in list(state["entries"].items()):
        if not entry.live():
            try:
                if path.parent in state.get("identities", {}):
                    storage_fs.check_identity(path.parent, state["identities"][path.parent])
                path.unlink(missing_ok=True)
                state["entries"].pop(path, None)
            except OSError:
                pass
    for root, owner in state.get("owners", {}).items():
        try:
            storage_fs.check_identity(root, owner["identity"])
            for name in owner["files"]:
                path = root / name
                if path not in state["entries"] and storage_fs.regular_file(path):
                    try:
                        path.unlink()
                    except OSError:
                        pass
        except OSError:
            pass
    for root, expected in state.get("identities", {}).items():
        storage_settings.remove_empty_cache_root(root, expected)
    if state["root"] is not None and state["root"] not in state.get("identities", {}):
        try:
            state["root"].rmdir()
        except OSError:
            pass


class DecodeStore:
    """One store per Helper instance. Auto uses disk for video and small RAM for audio.

    RAM hits return a clone. Disk hits return a new copy-on-write mmap, never
    a writable shared backing file. Already-returned results outlive eviction.
    """

    def __init__(self, temp_parent=None, memory_probe=available_ram, disk_probe=shutil.disk_usage,
                 headroom_bytes=2*GiB, interrupt=None):
        self._lock = threading.RLock()
        self.entries = OrderedDict()
        self.retired = []
        self.root = None
        self.temp_parent = temp_parent if temp_parent is not None else (os.environ.get("H3_DECODE_CACHE_TEMP_DIR") or None)
        self._explicit_parent = temp_parent is not None
        self._default_parent = self.temp_parent
        self._owners = {}
        self._scratch_token = uuid.uuid4().hex
        self.memory_probe = memory_probe
        self.disk_probe = disk_probe
        self.headroom_bytes = headroom_bytes
        self.interrupt = interrupt or (lambda: None)
        self.ram_limit = 512*MiB
        self.disk_limit = 16*GiB
        self.mode = "Auto"
        self.reset_token = 0
        self.epoch = 0
        self.max_entries = 256
        # Finalizer state has only paths, disk-entry metadata and weak leases;
        # no decoded RAM tensor, VAE, store, node, or GPU model is retained.
        self._cleanup_state = {"root": None, "entries": {}, "identities": {},
                               "lock": self._lock, "owners": self._owners}
        weakref.finalize(self, _cleanup_private_files, self._cleanup_state)

    def operation(self):
        manager = storage_settings.get_manager() if storage_settings else None
        return manager.operation() if manager else nullcontext()

    def configure(self, mode, ram_limit, disk_limit, reset_token):
        with self._lock:
            settings = (mode, int(ram_limit), int(disk_limit), int(reset_token))
            if settings != (self.mode, self.ram_limit, self.disk_limit, self.reset_token):
                self.clear()
                self.mode, self.ram_limit, self.disk_limit, self.reset_token = settings
            self._reap()
            if self.memory_probe() < self.headroom_bytes:
                for key, entry in list(self.entries.items()):
                    if entry.tensor is not None:
                        self._drop(key)

    @property
    def ram_bytes(self):
        return sum(e.payload_bytes for e in self.entries.values() if e.tensor is not None)

    @property
    def disk_bytes(self):
        return sum(e.file_bytes for e in self.entries.values() if e.path is not None) + sum(e.file_bytes for e in self.retired)

    def _delete(self, entry):
        if entry.path is None:
            return True
        if entry.live():
            return False
        try:
            if entry.path.parent in self._owners:
                storage_fs.check_identity(entry.path.parent, self._owners[entry.path.parent]["identity"])
            entry.path.unlink(missing_ok=True)
            self._cleanup_state["entries"].pop(entry.path, None)
            return True
        except OSError:
            return False

    def _drop(self, key):
        entry = self.entries.pop(key)
        if entry.path is not None and not self._delete(entry):
            self.retired.append(entry)

    def _reap(self):
        self.retired[:] = [e for e in self.retired if not self._delete(e)]
        for key, entry in list(self.entries.items()):
            if not all(ref() is not None for ref in entry.guards):
                self._drop(key)

    def clear(self):
        with self._lock:
            self.epoch += 1
            for key in list(self.entries):
                self._drop(key)
            self._reap()

    def close(self):
        self.clear()
        for root, owner in self._owners.items():
            storage_settings.remove_empty_cache_root(root, owner["identity"])
        if self.root is not None:
            try:
                self.root.rmdir()  # only an empty helper-owned directory
            except OSError:
                pass

    def _directory(self):
        manager = storage_settings.get_manager() if storage_settings else None
        if manager is not None:
            manager.register_store(self)
            default = self._default_parent or tempfile.gettempdir()
            parent = Path(default).resolve() if self._explicit_parent else manager.resolve("decode", default)
            if self.root is not None and self.root.parent != parent:
                self.root = None
            self.temp_parent = parent
        if self.root is None:
            self.root = Path(tempfile.mkdtemp(prefix=f"h3-decode-cache-{os.getpid()}-", dir=self.temp_parent))
            self._cleanup_state["root"] = self.root
            if manager is not None:
                owner = storage_settings.create_cache_owner(self.root)
                self._owners[self.root] = owner
                self._cleanup_state["identities"][self.root] = owner["identity"]
                manager.record_root("decode", self.root.parent)
        if self.root in self._owners:
            storage_fs.check_identity(self.root, self._owners[self.root]["identity"])
        return self.root

    def _ram_room(self, size):
        while self.ram_bytes + size > self.ram_limit:
            victim = next((k for k, e in self.entries.items() if e.tensor is not None), None)
            if victim is None:
                return False
            self._drop(victim)
        # Budget is additional retention only, not a claim about whole-process RSS.
        return self.memory_probe() >= self.headroom_bytes + 2*size

    def _disk_room(self, size):
        self._reap()
        while self.disk_bytes + size > self.disk_limit:
            victim = next((k for k, e in self.entries.items() if e.path is not None and not e.live()), None)
            if victim is None:
                return False
            self._drop(victim)
        root = self._directory()
        return self.disk_probe(root).free >= size + 256*MiB

    def _read_disk(self, entry):
        path = entry.path
        if path is not None and path.parent in self._owners:
            storage_fs.check_identity(path.parent, self._owners[path.parent]["identity"])
        if path is None or path.is_symlink() or path.stat().st_size != entry.file_bytes:
            raise CacheBypass("disk cache file missing/changed")
        # Verify the exact serialized payload before exposing a mapping.
        # Header/size are also checked; pickle is never allowed.
        array = np.load(path, mmap_mode="c", allow_pickle=False, max_header_size=4096)
        if tuple(array.shape) != entry.shape or array.dtype.str != entry.dtype or not array.flags.c_contiguous:
            raise CacheBypass("disk cache header mismatch")
        if array.nbytes != entry.payload_bytes:
            raise CacheBypass("disk cache size mismatch")
        raw = memoryview(array).cast("B")
        h = hashlib.sha256()
        for start in range(0, len(raw), 8*MiB):
            self.interrupt()
            h.update(raw[start:start+8*MiB])
        if h.hexdigest() != entry.digest:
            raise CacheBypass("disk cache checksum mismatch")
        entry.leases.append(weakref.ref(array))
        # mode='c' makes writable, private pages. mode='r' is NOT used.
        return torch.from_numpy(array)

    def get(self, key):
        with self._lock:
            self._reap()
            entry = self.entries.get(key)
            if entry is None:
                return None
            if not all(ref() is not None for ref in entry.guards):
                self._drop(key)
                return None
            self.entries.move_to_end(key)
            if entry.tensor is not None:
                if self.memory_probe() < self.headroom_bytes + entry.payload_bytes:
                    self._drop(key)
                    return None
                if (tuple(entry.tensor.shape) != entry.shape
                        or entry.tensor.numpy().dtype.str != entry.dtype
                        or tensor_digest(entry.tensor, self.interrupt) != entry.digest):
                    self._drop(key)
                    raise CacheBypass("RAM cache checksum/header mismatch")
                # Independent storage protects the cache from in-place seam/color edits.
                return entry.tensor.clone(), deepcopy(entry.extra)
            try:
                tensor = self._read_disk(entry)
            except Exception:
                self._drop(key)
                raise
            return tensor, deepcopy(entry.extra)

    def put(self, key, tensor, stream, extra, guards, expected_epoch):
        with self._lock:
            if expected_epoch != self.epoch or self.mode == "Off":
                return None
            if (not isinstance(tensor, torch.Tensor) or tensor.device.type != "cpu"
                    or tensor.layout != torch.strided or tensor.is_nested or tensor.numel() == 0):
                return None
            if tensor.dtype not in (torch.float16, torch.float32, torch.float64):
                return None  # never silently downcast decoded output
            size = tensor.numel() * tensor.element_size()
            if not all(ref() is not None for ref in guards):
                return None
            if key in self.entries:
                self._drop(key)
            while len(self.entries) >= self.max_entries:
                self._drop(next(iter(self.entries)))
            use_ram = self.mode == "RAM" or (stream == "audio" and size <= 16*MiB)
            if use_ram and self._ram_room(size):
                stored = tensor.detach().clone(memory_format=torch.contiguous_format)
                self.entries[key] = Entry(tuple(stored.shape), stored.numpy().dtype.str,
                    tensor_digest(stored, self.interrupt), size, guards, deepcopy(extra), tensor=stored)
                return None  # original MISS output is independently owned
            if self.mode != "Auto" or self.disk_limit == 0 or size+4096 > self.disk_limit:
                return None
            if not self._disk_room(size+4096):
                return None
            root = self._directory()
            filename = uuid.uuid4().hex
            if root in self._owners:
                storage_settings.register_cache_file(root, self._owners[root], filename)
            temp = root / (filename + ".tmp")
            final = root / (filename + ".npy")
            dtype = {torch.float16: np.dtype("float16"), torch.float32: np.dtype("float32"),
                     torch.float64: np.dtype("float64")}[tensor.dtype]
            h = hashlib.sha256()
            try:
                with open(temp, "xb") as f:
                    np.lib.format.write_array_header_1_0(f, {
                        "descr": dtype.str, "fortran_order": False, "shape": tuple(tensor.shape)})
                    for block in tensor_blocks(tensor):
                        self.interrupt()
                        h.update(block)
                        if f.write(block) != len(block):
                            raise OSError("short cache write")
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp, final)
                entry = Entry(tuple(tensor.shape), dtype.str, h.hexdigest(), size, guards,
                              deepcopy(extra), path=final, file_bytes=final.stat().st_size)
                self.entries[key] = entry
                self._cleanup_state["entries"][final] = entry
                # Returning a COW mapping releases the large anonymous MISS output
                # after this call rather than keeping an extra private RAM copy.
                return self.get(key)
            except BaseException:
                if key in self.entries:
                    self._drop(key)
                for path in (temp, final):
                    try:
                        path.unlink(missing_ok=True)
                    except OSError:
                        pass
                raise

    def contains(self, key):
        with self._lock:
            return key in self.entries

    def inspect_scratch(self, *, cleanup=False, parent):
        """Pure status unless explicitly cleaning; preserve aliases and RAM entries."""
        with self._lock:
            result = {}
            removed = {"removed_files": 0, "removed_bytes": 0, "errors": []}
            entries = [(key, entry) for key, entry in self.entries.items()]
            entries += [(None, entry) for entry in self.retired]
            for key, entry in entries:
                path = entry.path
                if path is None or path.parent.parent != Path(parent):
                    continue
                try:
                    if path.parent in self._owners:
                        storage_fs.check_identity(path.parent, self._owners[path.parent]["identity"])
                    if not path.is_file() or path.is_symlink():
                        continue
                    size = path.stat().st_size
                    live = any(ref() is not None for ref in entry.leases)
                    if cleanup and not live and self._delete(entry):
                        if key is not None:
                            self.entries.pop(key, None)
                        else:
                            self.retired = [item for item in self.retired if item is not entry]
                        removed["removed_files"] += 1
                        removed["removed_bytes"] += size
                    else:
                        result[str(path)] = "in_use" if live else "deletable"
                        if cleanup and not live:
                            removed["errors"].append(f"Could not delete {path.name}; file retained")
                except OSError as exc:
                    result[str(path)] = "unknown"
                    if cleanup:
                        removed["errors"].append(str(exc))
            # An interrupted unpublished write can leave a registered .tmp.
            # The store lock proves no writer is active here; the entry ledger
            # continues to protect any published mapping, including retired ones.
            for root, owner in self._owners.items():
                if root.parent != Path(parent):
                    continue
                try:
                    storage_fs.check_identity(root, owner["identity"])
                    for name in owner["files"]:
                        path = root / name
                        if path in self._cleanup_state["entries"] or not storage_fs.regular_file(path):
                            continue
                        size = path.stat().st_size
                        if cleanup:
                            try:
                                path.unlink()
                                removed["removed_files"] += 1
                                removed["removed_bytes"] += size
                            except OSError as exc:
                                result[str(path)] = "deletable"
                                removed["errors"].append(str(exc))
                        else:
                            result[str(path)] = "deletable"
                except OSError:
                    pass
            if cleanup:
                for root, owner in self._owners.items():
                    if root.parent == Path(parent) and root != self.root:
                        storage_settings.remove_empty_cache_root(root, owner["identity"])
            result[f"__removed_{self._scratch_token}"] = removed
            return result

    def stats(self):
        with self._lock:
            self._reap()
            return {"entries": len(self.entries), "ram_bytes": self.ram_bytes,
                    "disk_bytes": self.disk_bytes, "pending_delete_files": len(self.retired)}
