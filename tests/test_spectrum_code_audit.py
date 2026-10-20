"""Supplemental code audits retain legacy identities and reject altered implementations."""
import importlib
import json
from pathlib import Path
import sys
import types

import pytest

from ComfyUI_H3_Continuum_Join import spectrum_signature as adapter
from .test_issue31_spectrum_signature import binding, signature, spectrum


def _sample(a, *, b=2):
    return a + b


@pytest.mark.parametrize("field", adapter._CODE_AUDIT_FIELDS)
def test_each_code_field_remains_observable(field):
    code = _sample.__code__
    replacements = {
        "co_argcount": 0, "co_posonlyargcount": 1, "co_kwonlyargcount": 0,
        "co_nlocals": code.co_nlocals + 1, "co_stacksize": code.co_stacksize + 1,
        "co_flags": code.co_flags ^ 0x40, "co_code": code.co_code + b"\x09\x00",
        "co_consts": code.co_consts + ("changed",), "co_names": code.co_names + ("foreign",),
        "co_varnames": ("other",) + code.co_varnames[1:], "co_freevars": ("foreign",),
        "co_cellvars": ("foreign",), "co_name": "other", "co_qualname": "other",
        "co_linetable": code.co_linetable + b"\0", "co_exceptiontable": code.co_exceptiontable + b"\0",
    }
    kwargs = {field: replacements[field]}
    if field == "co_nlocals":
        kwargs["co_varnames"] = code.co_varnames + ("extra",)
    assert adapter._stable_code_digest(code.replace(**kwargs)) != adapter._stable_code_digest(code)


def test_constant_bits_and_types_are_preserved():
    assert adapter._code_audit_value(0.0) != adapter._code_audit_value(-0.0)
    assert adapter._code_audit_value(True) != adapter._code_audit_value(1)
    assert adapter._code_audit_value((1,)) != adapter._code_audit_value(frozenset([1]))
    with pytest.raises(ValueError, match="unsupported code audit constant"):
        adapter._code_audit_value([])
    code = _sample.__code__
    assert adapter._stable_code_digest(code.replace(co_filename="elsewhere", co_firstlineno=999)) == adapter._stable_code_digest(code)


def test_second_import_keeps_complete_legacy_identity(spectrum):
    before = signature(binding(spectrum))
    root = Path(spectrum[0].__file__).resolve().parent.parent
    namespace = types.ModuleType("supplemental_" + spectrum[0].__name__.split('.')[0])
    namespace.__path__ = [str(root)]
    sys.modules[namespace.__name__] = namespace
    prefix = namespace.__name__ + ".comfyui_spectrum_h3"
    sampling = importlib.import_module(prefix + ".sampling")
    runtime = importlib.import_module(prefix + ".runtime")
    config = importlib.import_module(prefix + ".config")
    item = sampling.SpectrumH3Binding(runtime.SpectrumH3Runtime(config.SpectrumH3Config()))
    assert signature(item) == before


def test_fallback_returns_original_identity(spectrum, monkeypatch):
    item = binding(spectrum)
    before = signature(item)
    monkeypatch.setattr(adapter, "_code_digest", lambda code: "0" * 64)
    assert signature(item) == before


@pytest.mark.parametrize("change", ["code", "default", "kwdefault", "member", "runtime"])
def test_fallback_does_not_certify_changed_provider(spectrum, monkeypatch, change):
    item = binding(spectrum)
    signature(item)
    monkeypatch.setattr(adapter, "_code_digest", lambda code: "0" * 64)
    assert adapter.spectrum_binding_signature(item)[1]
    function = spectrum[1].SpectrumH3Runtime.__init__
    if change == "code":
        monkeypatch.setattr(function, "__code__", function.__code__.replace(co_consts=function.__code__.co_consts + ("changed",)))
    elif change == "default":
        monkeypatch.setattr(function, "__defaults__", (12345,))
    elif change == "kwdefault":
        monkeypatch.setattr(function, "__kwdefaults__", {"foreign": True})
    elif change == "member":
        monkeypatch.setattr(spectrum[1].SpectrumH3Runtime, "foreign", 1, raising=False)
    else:
        item.runtime.foreign = True
    descriptor, safe = adapter.spectrum_binding_signature(item)
    assert not safe and descriptor.get("unsupported")


@pytest.mark.parametrize("change", ["missing", "malformed", "version", "python", "provenance", "modules"])
def test_bad_supplemental_profile_stays_unsafe(spectrum, monkeypatch, change):
    item = binding(spectrum)
    signature(item)
    monkeypatch.setattr(adapter, "_code_digest", lambda code: "0" * 64)
    assert adapter.spectrum_binding_signature(item)[1]
    read = Path.read_bytes
    def replacement(path):
        if path.name.startswith("spectrum_code_audit_v1_"):
            if change == "missing":
                raise FileNotFoundError(str(path))
            if change == "malformed":
                return b"{invalid"
            value = json.loads(read(path))
            if change == "version": value["format_version"] = 999
            elif change == "python": value["python_minor"] = [3, 99]
            elif change == "provenance": value["profiles"] = {}
            else:
                for profile in value["profiles"].values(): profile["modules"] = {}
            return json.dumps(value).encode()
        return read(path)
    monkeypatch.setattr(Path, "read_bytes", replacement)
    assert not adapter.spectrum_binding_signature(item)[1]
