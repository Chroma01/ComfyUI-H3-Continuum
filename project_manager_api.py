"""Optional Project / Take management routes; never part of sampling execution."""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
import re


PREFIX = "/h3-continuum/project-manager/projects"
MAX_REQUEST_BYTES = 65536


def _queued_nodes(entry):
    """Core stores the complete graph and the accepted output IDs separately."""
    output = entry[2]
    if len(entry) < 5:
        return output.values()  # Legacy/unknown queue metadata: conservative.
    targets = entry[4]
    if not isinstance(targets, (list, tuple)):
        return output.values()
    pending = [str(item) for item in targets]
    reached = set()
    while pending:
        node_id = pending.pop()
        if node_id in reached:
            continue
        if node_id not in output or not isinstance(output[node_id], dict):
            return output.values()
        reached.add(node_id)
        inputs = output[node_id].get("inputs", {})
        if not isinstance(inputs, dict):
            return output.values()
        for value in inputs.values():
            if (isinstance(value, list) and len(value) == 2
                    and isinstance(value[0], (str, int)) and type(value[1]) is int):
                pending.append(str(value[0]))
    return [output[node_id] for node_id in reached]


def _request_directory(server, request, folder_paths):
    """Keep management metadata in Core's validated public user profile."""
    users = getattr(server, "user_manager", None)
    if users is not None:
        user_id = users.get_request_user_id(request)
    else:
        from comfy.cli_args import args
        if getattr(args, "multi_user", False):
            raise KeyError("User validation unavailable")
        user_id = "default"
    if not isinstance(user_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", user_id) or user_id.startswith("__"):
        raise KeyError("Unknown user")
    public_directory = getattr(folder_paths, "get_public_user_directory", None)
    root = public_directory(user_id) if public_directory else Path(folder_paths.get_user_directory()) / user_id
    if root is None:
        raise KeyError("Unknown user")
    return Path(root) / "h3_continuum" / "project_manager" / "projects"


def _run_busy(server, storage_name):
    """Read the existing Queue only; never wrap, cancel or submit a prompt."""
    from .run_storage import resolve_run_storage_name
    queue = getattr(server, "prompt_queue", None)
    if queue is None:
        return True
    running, pending = queue.get_current_queue()
    for entry in [*running, *pending]:
        if not isinstance(entry, (list, tuple)) or len(entry) < 3 or not isinstance(entry[2], dict):
            return True
        for value in _queued_nodes(entry):
            if not isinstance(value, dict) or not str(value.get("class_type", "")).startswith("H3ContinuumSampler"):
                continue
            inputs = value.get("inputs", {})
            if not isinstance(inputs, dict):
                return True
            name, project_id = inputs.get("run_name", ""), inputs.get("project_id", "")
            if not isinstance(name, str) or not isinstance(project_id, str):
                return True
            try:
                resolved = resolve_run_storage_name(project_id=project_id, legacy_run_name=name)
            except (ValueError, RuntimeError):
                return True
            if resolved.casefold() == storage_name.casefold():
                return True
    return False


def register_routes(server):
    if server is None or getattr(server, "_h3_project_manager_registered", False):
        return
    from aiohttp import web

    async def handle(request, operation):
        # Imports and disk access are lazy: a disabled/unused Manager adds no
        # metadata files and has no dependency in generation or Review.
        from .project_manager import ProjectManager, ProjectManagerError
        import folder_paths
        try:
            directory = _request_directory(server, request, folder_paths)
            manager = ProjectManager(directory, Path(folder_paths.get_output_directory()) / "h3_continuum" / "runs")
            if operation in {"create", "mutate", "prepare"}:
                if request.content_type != "application/json":
                    return web.json_response({"error": "Use application/json"}, status=415)
                raw = await request.read()
                if len(raw) > MAX_REQUEST_BYTES:
                    return web.json_response({"error": "Management request is too large"}, status=413)
                body = json.loads(raw)
                if not isinstance(body, dict):
                    raise ValueError("Request must be a JSON object")
            else:
                body = {}
            project_id = request.match_info.get("project_id", "")
            if operation == "list":
                value = await asyncio.to_thread(manager.list_projects)
            elif operation == "get":
                value = await asyncio.to_thread(manager.get, project_id)
            elif operation == "create":
                if set(body) != {"name", "project_id", "operation_id"}:
                    raise ValueError("Expected name, project_id and operation_id")
                value = await asyncio.to_thread(manager.create, **body)
            elif operation == "mutate":
                required = {"revision", "operation_id", "action"}
                if not required <= set(body):
                    raise ValueError("Expected revision, operation_id and action")
                value = await asyncio.to_thread(manager.mutate, project_id, **body)
            else:
                if set(body) != {"savepoint_id"}:
                    raise ValueError("Expected savepoint_id")
                value = await asyncio.to_thread(manager.prepare, project_id, body["savepoint_id"])
                if _run_busy(server, value["storage_name"]):
                    raise ProjectManagerError("This Run is queued or running; wait before preparing Review", status=409)
            return web.json_response(value, headers={"Cache-Control": "no-store"})
        except KeyError:
            return web.json_response({"error": "Unknown user or invalid management data"}, status=403)
        except (ProjectManagerError, ValueError, TypeError, OSError) as exc:
            error = {"error": str(exc)}
            if isinstance(exc, ProjectManagerError) and exc.code is not None:
                error["code"] = exc.code
            return web.json_response(error, status=getattr(exc, "status", 400))
        except Exception:
            logging.getLogger("h3_continuum.project_manager").exception("Project / Take request failed")
            return web.json_response({"error": "Project / Take management is unavailable; see server log"}, status=500)

    async def listing(request):
        return await handle(request, "list")

    async def getting(request):
        return await handle(request, "get")

    async def creating(request):
        return await handle(request, "create")

    async def mutating(request):
        return await handle(request, "mutate")

    async def preparing(request):
        return await handle(request, "prepare")

    server.routes.get(PREFIX)(listing)
    server.routes.post(PREFIX)(creating)
    server.routes.get(PREFIX + "/{project_id}")(getting)
    server.routes.post(PREFIX + "/{project_id}/operations")(mutating)
    server.routes.post(PREFIX + "/{project_id}/prepare")(preparing)
    server._h3_project_manager_registered = True
