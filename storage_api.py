"""ComfyUI endpoints for server-owned temporary storage settings."""
from __future__ import annotations

import asyncio
from contextlib import nullcontext
import logging
from pathlib import Path
import sys
import tempfile
import os

from .storage_settings import StorageSettings, StorageError, install_manager


def register_routes(server=None):
    if server is None:
        module = sys.modules.get("server")
        server = getattr(getattr(module, "PromptServer", None), "instance", None)
    if server is None or getattr(server, "_h3_storage_registered", False):
        return
    import folder_paths
    from aiohttp import web
    from comfy.cli_args import args

    system_directory = getattr(folder_paths, "get_system_user_directory", None)
    if system_directory:
        directory = Path(system_directory("h3_continuum"))
    else:
        directory = Path(folder_paths.get_user_directory()) / (getattr(folder_paths, "SYSTEM_USER_PREFIX", "__") + "h3_continuum")

    def busy():
        queue = getattr(server, "prompt_queue", None)
        if queue is None:
            return True
        running, waiting = queue.get_current_queue()
        return bool(running or waiting)

    manager = StorageSettings(
        directory / "temporary-storage.json",
        default_finalize=lambda: Path(folder_paths.get_temp_directory()) / "h3-continuum-v35-file-backed",
        default_decode=lambda: os.environ.get("H3_DECODE_CACHE_TEMP_DIR") or tempfile.gettempdir(),
        busy=busy,
        queue_guard=lambda: getattr(getattr(server, "prompt_queue", None), "mutex", nullcontext()),
        read_only=bool(getattr(args, "multi_user", False)),
    )

    async def handle(request, operation):
        try:
            # Use Core's existing user validation; a profile is not an admin role.
            user_manager = getattr(server, "user_manager", None)
            if user_manager is not None:
                user_manager.get_request_user_id(request)
            if operation == "status":
                value = await asyncio.to_thread(manager.status)
            else:
                if request.content_type != "application/json":
                    return web.json_response({"error": "Use application/json"}, status=415)
                body = await request.json()
                if not isinstance(body, dict):
                    raise StorageError("Request must be a JSON object")
                allowed = {"validate": {"path"}, "settings": {"path", "revision"}, "cleanup": set()}[operation]
                if set(body) - allowed:
                    raise StorageError("Unexpected storage request fields")
                if operation == "validate":
                    value = await asyncio.to_thread(manager.validate, body.get("path", ""))
                elif operation == "settings":
                    value = await asyncio.to_thread(manager.save, body.get("path", ""), body.get("revision"))
                else:
                    value = await asyncio.to_thread(manager.cleanup)
            return web.json_response(value, headers={"Cache-Control": "no-store"})
        except KeyError:
            return web.json_response({"error": "Unknown user or invalid storage metadata"}, status=403)
        except (StorageError, OSError, ValueError) as exc:
            return web.json_response({"error": str(exc)}, status=getattr(exc, "status", 400))
        except Exception:
            logging.getLogger("h3_continuum.storage").exception("Temporary storage request failed")
            return web.json_response({"error": "Temporary storage request failed; see server log"}, status=500)

    async def status(request):
        return await handle(request, "status")

    async def validate(request):
        return await handle(request, "validate")

    async def settings(request):
        return await handle(request, "settings")

    async def cleanup(request):
        return await handle(request, "cleanup")

    server.routes.get("/h3-continuum/storage/status")(status)
    server.routes.post("/h3-continuum/storage/validate")(validate)
    server.routes.post("/h3-continuum/storage/settings")(settings)
    server.routes.post("/h3-continuum/storage/cleanup")(cleanup)
    server._h3_storage_registered = True
    install_manager(manager)
    return manager
