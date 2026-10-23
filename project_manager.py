"""Optional Project/Take labels, separate from generation and immutable Run data.

Nothing is created on construction. Only explicit management requests write here;
Run Storage is read-only. Generation never imports or depends on this module.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat
import time
import uuid

from .branch_provenance import PhysicalGroup, make_group_revision, resolve_chain


class ProjectManagerError(ValueError):
    def __init__(self, message, status=400, *, code=None):
        super().__init__(message)
        self.status = status
        self.code = code


MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_OPERATIONS = 4096
MAX_ITEMS = 4096


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _uuid(value):
    try:
        result = uuid.UUID(value)
        if not result.int or str(result) != value:
            raise ValueError()
        return str(result)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ProjectManagerError("Expected a canonical non-nil UUID") from exc


def _name(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 160 or any(ord(c) < 32 for c in value):
        raise ProjectManagerError("Name must contain 1-160 printable characters")
    return value.strip()


def _component(value):
    from .run_storage import sanitize_run_name
    if not isinstance(value, str):
        raise ProjectManagerError("Invalid Run Storage name")
    try:
        return sanitize_run_name(value)
    except (ValueError, RuntimeError) as exc:
        raise ProjectManagerError("Invalid Run Storage name") from exc


def _path(root, *parts):
    """Reject links/junctions inside the server-selected roots, including the root."""
    root = Path(root).absolute()
    target = root.joinpath(*parts)
    if not target.absolute().is_relative_to(root) or any(p in ("", ".", "..") for p in parts):
        raise ProjectManagerError("Path escaped its storage root")
    for current in (root, *[root.joinpath(*parts[:i]) for i in range(1, len(parts) + 1)]):
        try:
            details = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(details.st_mode) or getattr(details, "st_file_attributes", 0) & 0x400:
            raise ProjectManagerError("Linked storage paths are not supported")
    if not target.resolve().is_relative_to(root.resolve()):
        raise ProjectManagerError("Path escaped its storage root")
    return target


def _read(path):
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_JSON_BYTES + 1)
        if len(data) > MAX_JSON_BYTES:
            raise ProjectManagerError("Metadata exceeds the supported size")
        value = json.loads(data.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except FileNotFoundError as exc:
        raise ProjectManagerError("Saved metadata is missing", 404) from exc
    except (UnicodeError, ValueError) as exc:
        raise ProjectManagerError("Saved metadata is invalid; the original file was preserved", 409) from exc


def _signature(path):
    value = path.stat()
    return value.st_size, value.st_mtime_ns, value.st_ctime_ns, value.st_ino


def _sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class ProjectManager:
    def __init__(self, directory, runs_root):
        self.directory = Path(directory)
        self.runs_root = Path(runs_root)

    def _file(self, project_id):
        return _path(self.directory, _uuid(project_id) + ".json")

    @contextmanager
    def _lock(self, project_id):
        # OS locks release after process exit. Never break another writer's lock.
        _path(self.directory).mkdir(parents=True, exist_ok=True)
        path = _path(self.directory, _uuid(project_id) + ".lock")
        with path.open("a+b") as stream:
            if path.stat().st_size == 0:
                stream.write(b"\0")
                stream.flush()
            deadline = time.monotonic() + 2.0
            acquired = False
            while not acquired:
                try:
                    stream.seek(0)
                    if os.name == "nt":
                        import msvcrt
                        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise ProjectManagerError("Project is being updated; retry after refreshing", 423) from exc
                    time.sleep(0.02)
            try:
                yield
            finally:
                stream.seek(0)
                if os.name == "nt":
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _write(self, value):
        path = self._file(value["id"])
        temporary = _path(self.directory, f".{value['id']}-{uuid.uuid4().hex}.tmp")
        payload = (_canonical(value) + "\n").encode("utf-8")
        if len(payload) > MAX_JSON_BYTES:
            raise ProjectManagerError("Project metadata is full; create another Project", 409)
        try:
            with temporary.open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            if os.name != "nt":
                descriptor = os.open(self.directory, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        finally:
            temporary.unlink(missing_ok=True)

    def get(self, project_id):
        value = _read(self._file(project_id))
        try:
            if (value.get("schema_version") != 1 or value.get("id") != project_id
                    or type(value.get("revision")) is not int or value["revision"] < 1
                    or type(value.get("archived")) is not bool
                    or _name(value.get("name")) != value["name"]
                    or not all(isinstance(value.get(k), list) for k in ("attempts", "savepoints", "operations"))):
                raise ValueError()
            attempts = {}
            for item in value["attempts"]:
                _uuid(item["id"])
                if (item["id"] in attempts or _name(item["name"]) != item["name"]
                        or type(item["archived"]) is not bool):
                    raise ValueError()
                if item["project_id"]:
                    parsed = _uuid(item["project_id"])
                    if item["run_name"] != "" or item["storage_name"] != "run_" + uuid.UUID(parsed).hex:
                        raise ValueError()
                elif item["storage_name"] != _component(item["run_name"]):
                    raise ValueError()
                attempts[item["id"]] = item
            seen = set()
            for item in value["savepoints"]:
                _uuid(item["id"])
                snapshot = item["snapshot"]
                if (item["id"] in seen or item["attempt_id"] not in attempts
                        or _name(item["name"]) != item["name"] or type(item["archived"]) is not bool
                        or type(item["generation_reusable"]) is not bool
                        or not isinstance(snapshot, dict) or snapshot.get("revision_id") != item["revision_id"]
                        or snapshot.get("group") != item["group"]
                        or snapshot.get("run_name") != attempts[item["attempt_id"]]["storage_name"]
                        or not isinstance(snapshot.get("ancestry"), list) or not snapshot["ancestry"]
                        or not isinstance(snapshot.get("raw"), list) or not snapshot["raw"]):
                    raise ValueError()
                group = item["group"]
                if (set(group) != {"start", "end", "physical_group"}
                        or any(type(number) is not int for number in group.values())
                        or group["start"] < 1 or group["end"] < group["start"]
                        or group["physical_group"] != group["start"]):
                    raise ValueError()
                for record in snapshot["raw"]:
                    _component(record["storage_revision_id"])
                    _component(record["filename"])
                    if (type(record["file_size"]) is not int or record["file_size"] < 0
                            or not isinstance(record["file_sha256"], str) or len(record["file_sha256"]) != 64):
                        raise ValueError()
                if snapshot["ancestry"][-1]["revision_id"] != item["revision_id"]:
                    raise ValueError()
                seen.add(item["id"])
            seen = set()
            for operation in value["operations"]:
                _uuid(operation["id"])
                if (operation["id"] in seen or not isinstance(operation["fingerprint"], str)
                        or len(operation["fingerprint"]) != 64 or not isinstance(operation["result"], dict)
                        or not isinstance(operation["result"].get("action"), str)):
                    raise ValueError()
                seen.add(operation["id"])
            if not value["operations"] or value["revision"] != len(value["operations"]):
                raise ValueError()
        except (ValueError, TypeError, KeyError, AttributeError, IndexError) as exc:
            raise ProjectManagerError("Unsupported or damaged Project metadata; original preserved", 409) from exc
        return value

    def list_projects(self):
        root = _path(self.directory)
        projects, errors = [], []
        if not root.exists():
            return {"projects": [], "errors": []}
        for path in sorted(root.glob("*.json")):
            try:
                value = self.get(path.stem)
                projects.append({k: value[k] for k in ("id", "name", "revision", "archived")})
            except (ProjectManagerError, OSError) as exc:
                errors.append({"id": path.stem, "error": str(exc)})
        return {"projects": projects, "errors": errors}

    @staticmethod
    def _replay(project, operation_id, fingerprint):
        for op in project["operations"]:
            if op["id"] == operation_id:
                if op["fingerprint"] != fingerprint:
                    raise ProjectManagerError("Operation ID was already used for a different request", 409)
                result = deepcopy(project)
                result["last_result"] = deepcopy(op["result"])
                return result
        return None

    @staticmethod
    def _record(project, operation_id, fingerprint, result):
        # Never silently evict idempotency keys and later repeat an old mutation.
        if len(project["operations"]) >= MAX_OPERATIONS:
            raise ProjectManagerError("Project operation journal is full; create another Project", 409)
        project["operations"].append({"id": operation_id, "fingerprint": fingerprint, "result": result})
        project["last_result"] = result

    def create(self, name, project_id, operation_id):
        project_id, operation_id, name = _uuid(project_id), _uuid(operation_id), _name(name)
        fingerprint = _digest({"action": "create", "name": name})
        with self._lock(project_id):
            if self._file(project_id).exists():
                old = self.get(project_id)
                replay = self._replay(old, operation_id, fingerprint)
                if replay is not None:
                    return replay
                raise ProjectManagerError("Project already exists", 409)
            project = {"schema_version": 1, "id": project_id, "name": name, "revision": 1,
                       "attempts": [], "savepoints": [], "archived": False, "operations": []}
            self._record(project, operation_id, fingerprint, {"action": "create"})
            self._write(project)
            return deepcopy(project)

    @staticmethod
    def _item(project, collection, item_id):
        _uuid(item_id)
        for item in project[collection]:
            if item["id"] == item_id:
                return item
        raise ProjectManagerError("Selected item no longer exists", 404)

    def _capture(self, run_name, revision_id):
        """Verify a fixed prefix without a Run lock, tensor loads or storage writes."""
        from .run_storage import _manifest_sampling_identity, _reusable_manifest
        run_name = _component(run_name)
        if not isinstance(revision_id, str) or len(revision_id) != 24 or any(c not in "0123456789abcdef" for c in revision_id):
            raise ProjectManagerError("Select a valid saved Take revision")
        readset = []

        def metadata(path):
            before = _signature(path)
            value = _read(path)
            if _signature(path) != before:
                raise ProjectManagerError("Saved data changed during inspection; retry", 409)
            readset.append((path, before))
            return value

        try:
            project = metadata(_path(self.runs_root, run_name, "project.json"))
            if project.get("run_name") != run_name or project.get("branch_provenance_version") != 1:
                raise ProjectManagerError("Run history has no supported immutable Take provenance", 409)
            catalog = {}
            for item in project.get("group_revisions", []):
                key = item.get("revision_id")
                if key in catalog:
                    raise ProjectManagerError("Duplicate Take identity in Run history", 409)
                catalog[key] = item
            chain = resolve_chain(catalog, revision_id)
            manifests, pinned, raw, reusable = {}, [], [], True
            for index, item in enumerate(chain):
                source = _component(item["storage_revision_id"])
                if source not in manifests:
                    manifest = metadata(_path(self.runs_root, run_name, "revisions", source, "manifest.json"))
                    if manifest.get("revision_id") != source:
                        raise ProjectManagerError("Saved manifest directory identity mismatch", 409)
                    _manifest_sampling_identity(manifest)
                    manifests[source] = manifest
                manifest = manifests[source]
                contract = manifest["contract"]
                persisted = manifest.get("branch_provenance")
                if persisted is not None and (not isinstance(persisted, dict)
                        or persisted.get("version") != 1
                        or list(persisted.get("active_chain") or [])[:index + 1]
                        != [ancestor["revision_id"] for ancestor in chain[:index + 1]]):
                    raise ProjectManagerError("Saved Take ancestry disagrees with its producer", 409)
                if (item["generation_contract_sha256"] != manifest["contract_sha256"]
                        or item["lineage_sha256"] != contract.get("nonce_lineage_sha256")):
                    raise ProjectManagerError("Saved Take disagrees with its producing contract", 409)
                group = item["group"]
                records = manifest.get("chunks", [])[group["start"] - 1:group["end"]]
                boundary = int(contract.get("reroll_from_chunk", 0))
                nonce = int(contract.get("effective_reroll_nonce", 0))
                rebuilt = make_group_revision(
                    parent_revision_id=item["parent_revision_id"], group=PhysicalGroup(**group),
                    variation_nonce=nonce if boundary > 0 and group["start"] >= boundary else 0,
                    created_utc=item["created_utc"], storage_revision_id=source,
                    generation_contract_sha256=manifest["contract_sha256"],
                    lineage_sha256=contract["nonce_lineage_sha256"], records=records)
                if rebuilt["revision_id"] != item["revision_id"]:
                    raise ProjectManagerError("Saved Take records changed or are incomplete", 409)
                reusable = reusable and _reusable_manifest(manifest)
                pinned.append({"revision_id": item["revision_id"], "parent_revision_id": item["parent_revision_id"],
                               "group": group, "storage_revision_id": source,
                               "generation_contract_sha256": item["generation_contract_sha256"]})
                for record in item["records"]:
                    filename = _component(record["filename"])
                    if record["storage_revision_id"] != source:
                        raise ProjectManagerError("Physical group has multiple storage sources", 409)
                    path = _path(self.runs_root, run_name, "revisions", source, "chunks", filename)
                    before = _signature(path)
                    if before[0] != record["file_size"] or _sha(path) != record["file_sha256"]:
                        raise ProjectManagerError("Saved raw data failed its size/SHA-256 check", 409)
                    if _signature(path) != before:
                        raise ProjectManagerError("Saved raw data changed during inspection", 409)
                    readset.append((path, before))
                    raw.append({"storage_revision_id": source, "filename": filename,
                                "file_size": record["file_size"], "file_sha256": record["file_sha256"]})
            snapshot = {"run_name": run_name, "revision_id": revision_id, "group": chain[-1]["group"],
                        "ancestry": pinned, "raw": raw}
            self._verify_readset(readset)
            return snapshot, bool(reusable), readset
        except ProjectManagerError:
            raise
        except (OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError) as exc:
            raise ProjectManagerError("Saved Take integrity could not be verified", 409) from exc

    @staticmethod
    def _verify_readset(readset):
        for path, expected in readset:
            try:
                if _signature(path) != expected:
                    raise OSError()
            except OSError as exc:
                raise ProjectManagerError("Saved data changed or disappeared; refresh and retry", 409) from exc

    def mutate(self, project_id, revision, operation_id, action, **payload):
        project_id, operation_id = _uuid(project_id), _uuid(operation_id)
        if type(revision) is not int or revision < 1:
            raise ProjectManagerError("Expected the current Project revision")
        fields = {
            "rename_project": {"name"}, "archive_project": {"archived"}, "new_attempt": {"name"},
            "attach_attempt": {"name", "run_name"}, "rename_attempt": {"attempt_id", "name"},
            "archive_attempt": {"attempt_id", "archived"},
            "savepoint": {"attempt_id", "name", "revision_id"},
            "rename_savepoint": {"savepoint_id", "name"}, "archive_savepoint": {"savepoint_id", "archived"},
        }
        if action not in fields or set(payload) != fields[action]:
            raise ProjectManagerError("Unexpected Project operation fields")
        if "name" in payload:
            payload["name"] = _name(payload["name"])
        if "archived" in payload and type(payload["archived"]) is not bool:
            raise ProjectManagerError("archived must be a boolean")
        fingerprint = _digest({"action": action, "payload": payload, "revision": revision})
        before = self.get(project_id)
        replay = self._replay(before, operation_id, fingerprint)
        if replay is not None:
            return replay
        captured = None
        if action == "savepoint":
            attempt = self._item(before, "attempts", payload["attempt_id"])
            captured = self._capture(attempt["storage_name"], payload["revision_id"])
        if action == "attach_attempt":
            payload["run_name"] = _component(payload["run_name"])
            run = _read(_path(self.runs_root, payload["run_name"], "project.json"))
            if run.get("run_name") != payload["run_name"]:
                raise ProjectManagerError("Run history identity mismatch", 409)
        with self._lock(project_id):
            project = self.get(project_id)
            replay = self._replay(project, operation_id, fingerprint)
            if replay is not None:
                return replay
            if project["revision"] != revision:
                raise ProjectManagerError("Project changed in another tab; refresh before saving", 409,
                                          code="project_revision_conflict")
            result = {"action": action}
            if action in ("rename_project", "archive_project"):
                project.update(payload)
            elif action in ("new_attempt", "attach_attempt"):
                if len(project["attempts"]) >= MAX_ITEMS:
                    raise ProjectManagerError("Project attempt limit reached", 409)
                fresh = str(uuid.uuid4()) if action == "new_attempt" else ""
                run_name = "" if fresh else payload["run_name"]
                storage_name = "run_" + uuid.UUID(fresh).hex if fresh else run_name
                if fresh and _path(self.runs_root, storage_name).exists():
                    raise ProjectManagerError("New Run identity already exists; retry", 409)
                if any(item["storage_name"] == storage_name for item in project["attempts"]):
                    raise ProjectManagerError("This Run is already attached to the Project", 409)
                attempt = {"id": str(uuid.uuid4()), "name": payload["name"], "run_name": run_name,
                           "project_id": fresh, "storage_name": storage_name, "archived": False}
                project["attempts"].append(attempt)
                result["attempt_id"] = attempt["id"]
            elif action == "savepoint":
                if len(project["savepoints"]) >= MAX_ITEMS:
                    raise ProjectManagerError("Project savepoint limit reached", 409)
                snapshot, reusable, readset = captured
                self._verify_readset(readset)
                item = {"id": str(uuid.uuid4()), "name": payload["name"], "attempt_id": payload["attempt_id"],
                        "revision_id": snapshot["revision_id"], "group": snapshot["group"],
                        "archived": False, "generation_reusable": reusable, "snapshot": snapshot}
                project["savepoints"].append(item)
                result["savepoint_id"] = item["id"]
            else:
                collection = "attempts" if action.endswith("attempt") else "savepoints"
                item_key = "attempt_id" if collection == "attempts" else "savepoint_id"
                item = self._item(project, collection, payload[item_key])
                field = "name" if action.startswith("rename") else "archived"
                item[field] = payload[field]
                result[item_key] = item["id"]
            project["revision"] += 1
            self._record(project, operation_id, fingerprint, result)
            self._write(project)
            return deepcopy(project)

    def prepare(self, project_id, savepoint_id):
        project = self.get(project_id)
        saved = self._item(project, "savepoints", savepoint_id)
        attempt = self._item(project, "attempts", saved["attempt_id"])
        snapshot, reusable, _ = self._capture(attempt["storage_name"], saved["revision_id"])
        if snapshot != saved["snapshot"]:
            raise ProjectManagerError("The saved endpoint or its ancestry has changed", 409)
        if not reusable or saved.get("generation_reusable") is not True:
            raise ProjectManagerError("This saved Take is read-only for Sampling v6; use a new attempt", 409)
        return {"run_name": attempt["run_name"], "project_id": attempt["project_id"],
                "storage_name": attempt["storage_name"], "revision_id": saved["revision_id"],
                "group": snapshot["group"], "generation_reusable": True}
