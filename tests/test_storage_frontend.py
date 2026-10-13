from pathlib import Path
import shutil
import subprocess


def test_storage_settings_frontend_lifecycle():
    node = shutil.which("node")
    assert node, "Node.js is required for frontend regression checks"
    script = Path(__file__).with_name("frontend_storage_settings.mjs")
    result = subprocess.run([node, str(script)], text=True, encoding="utf-8",
                            capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "100 reopen cycles passed" in result.stdout
