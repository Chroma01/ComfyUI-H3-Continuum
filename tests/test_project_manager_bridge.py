"""Manager opt-in bridge against the actual, unchanged Queue lifecycle fixture."""
import json
import os
from pathlib import Path
import shutil
import subprocess


def run_bridge(fixture=None):
    root = Path(__file__).resolve().parents[1]
    node = shutil.which("node")
    assert node, "Node.js is required for the frontend regression gate"
    result = subprocess.run(
        [node, str(root / "tests/frontend_project_manager_bridge.cjs"), *([str(fixture)] if fixture else [])],
        env={**os.environ, "H3_TEST_ROOT": str(root)},
        capture_output=True, text=True, encoding="utf-8", timeout=45,
    )
    records = json.loads(result.stdout)
    assert len(records) == (33 if fixture else 32), result.stdout + result.stderr
    assert result.returncode == 0 and all(item["pass"] for item in records), result.stdout + result.stderr


def test_project_manager_frontend_bridge():
    run_bridge()


def test_real_saved_take_to_manager_to_existing_javascript_review(tmp_path):
    from ComfyUI_H3_Continuum_Join.project_manager import ProjectManager
    from .test_project_manager import hashes, saved_fixture

    manager = ProjectManager(tmp_path / "user" / "projects", tmp_path / "runs")
    controller, project, saved = saved_fixture(tmp_path, manager, prefix=2)
    before = hashes(manager.runs_root)
    fixture = tmp_path / "manager-to-review.json"
    fixture.write_text(json.dumps({
        "target": manager.prepare(project["id"], saved["id"]),
        "history": json.loads((controller.run_root / "project.json").read_text(encoding="utf-8")),
    }), encoding="utf-8")
    run_bridge(fixture)
    assert hashes(manager.runs_root) == before
