"""Preserve audited Spectrum identity across harmless newline/runtime differences."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys
import types

import pytest

from ComfyUI_H3_Continuum_Join import spectrum_signature as adapter
from .test_issue31_spectrum_signature import binding, signature, spectrum


def _relocate_provider(spectrum, tmp_path, monkeypatch, *, crlf=False):
    folder = Path(spectrum[0].__file__).resolve().parent
    for path in folder.glob("*.py"):
        data = path.read_bytes()
        if crlf:
            data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        (tmp_path / path.name).write_bytes(data)
    prefix = spectrum[0].__name__.rsplit(".", 1)[0]
    for name, module in tuple(sys.modules.items()):
        if name == prefix or name.startswith(prefix + "."):
            original = getattr(module, "__file__", None)
            if original and Path(original).resolve().parent == folder:
                monkeypatch.setattr(module, "__file__", str(tmp_path / Path(original).name))
    return prefix


def test_source_digest_normalizes_only_crlf(tmp_path):
    path = tmp_path / "provider.py"
    source = b"def value():\n    return 'unchanged'\n"
    path.write_bytes(source)
    expected = hashlib.sha256(source).hexdigest()
    assert adapter._source_digest(path) == expected
    path.write_bytes(source.replace(b"\n", b"\r\n"))
    assert adapter._source_digest(path) == expected
    path.write_bytes(source.replace(b"unchanged", b"changed"))
    assert adapter._source_digest(path) != expected


@pytest.mark.parametrize("newlines", ["all", "one"])
def test_crlf_preserves_full_existing_descriptor(spectrum, tmp_path, monkeypatch, newlines):
    item = binding(spectrum)
    before = signature(item)
    _relocate_provider(spectrum, tmp_path, monkeypatch, crlf=newlines == "all")
    if newlines == "one":
        path = tmp_path / "config.py"
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert signature(item) == before


def test_module_closure_crlf_keeps_original_digest(spectrum, tmp_path, monkeypatch):
    prefix = spectrum[0].__name__.rsplit(".", 1)[0]
    module = importlib.import_module(prefix + ".runtime")
    before = adapter._callable_value(module, provider_prefix=prefix)
    _relocate_provider(spectrum, tmp_path, monkeypatch, crlf=True)
    assert adapter._callable_value(module, provider_prefix=prefix) == before


@pytest.mark.parametrize("change", ["code", "extra_file"])
def test_real_source_changes_remain_unsafe(spectrum, tmp_path, monkeypatch, change):
    item = binding(spectrum)
    signature(item)
    _relocate_provider(spectrum, tmp_path, monkeypatch, crlf=True)
    if change == "code":
        path = tmp_path / "config.py"
        path.write_bytes(path.read_bytes() + b"\nUNKNOWN_ADDITIONAL_SETTING = True\n")
    else:
        (tmp_path / "unimported_helper.py").write_text("pass\n", encoding="utf-8")
    descriptor, safe = adapter.spectrum_binding_signature(item)
    assert not safe and descriptor.get("unsupported")


@pytest.mark.parametrize("version,suffix", [((3, 12, 10), "_py312"), ((3, 13, 12), "")])
def test_runtime_selects_explicit_audited_profile(monkeypatch, version, suffix):
    monkeypatch.setattr(adapter, "sys", types.SimpleNamespace(version_info=version))
    for name in ("spectrum_provider_v1.json", "spectrum_provider_v029.json"):
        assert adapter._runtime_metadata_file(name) == Path(name).stem + suffix + ".json"


@pytest.mark.parametrize("version", [(3, 10, 0), (3, 11, 0), (3, 14, 0)])
def test_unaudited_python_runtime_stays_unsafe(monkeypatch, version):
    monkeypatch.setattr(adapter, "sys", types.SimpleNamespace(version_info=version))
    with pytest.raises(ValueError, match="unsupported provider Python runtime"):
        adapter._runtime_metadata_file("spectrum_provider_v029.json")


def test_original_py313_profile_bytes_and_new_profile_packaging():
    root = Path(adapter.__file__).parent
    original = {
        "spectrum_provider_v1.json": "0efc8d65cb6f59042457ad843fe1b77a4bee45e59d3732f5c83fbc75a31ae77b",
        "spectrum_provider_v029.json": "8f786989af6339be8cec8f2bf602da89344cf96202d29c980af5c07175eea3d3",
    }
    for name, digest in original.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
        old = json.loads((root / name).read_text(encoding="utf-8"))
        current = json.loads((root / (Path(name).stem + "_py312.json")).read_text(encoding="utf-8"))
        assert old["format"] == current["format"] == "audited_spectrum_loaded_implementation_v1"
        assert set(old["modules"]) == set(current["modules"])
        assert old != current
