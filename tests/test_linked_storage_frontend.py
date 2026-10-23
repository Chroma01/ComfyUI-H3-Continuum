import json
import os
from pathlib import Path
import shutil
import subprocess


def test_linked_run_storage_preserves_regenerate_intent():
    node = shutil.which("node")
    assert node, "Node.js is required for frontend regression checks"
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([node, str(root / "tests/frontend_linked_storage.cjs")],
                            env={**os.environ, "H3_TEST_ROOT": str(root)},
                            capture_output=True, text=True, encoding="utf-8", timeout=40)
    assert result.returncode == 0, result.stdout + result.stderr
    records = json.loads(result.stdout)
    assert len(records) == 42
    assert all(item["pass"] for item in records), records
