from __future__ import annotations

import ast
import copy
import json
import hashlib
import subprocess
import sys
import types
from pathlib import Path

import pytest
import torch

from ComfyUI_H3_Continuum_Join import run_storage as storage
from . import test_v31_run_storage as signatures
from . import test_v38_review_run_storage as review

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def core_attention(require_comfy_core, monkeypatch):
    import comfy.ldm.modules.attention as attention
    import comfy.model_patcher as patcher
    # A CPU build may not advertise INT8. Inspect the real loaded definition;
    # registration here is a fixture, not an assertion that a CPU kernel runs.
    monkeypatch.setitem(attention.REGISTERED_ATTENTION_FUNCTIONS, "comfy_kitchen_int8",
                        attention.attention_comfy_kitchen_int8)
    return attention, patcher


def model_with(core, name):
    attention, patcher = core
    torch.manual_seed(31)
    model = signatures._Model()
    model.model_options["transformer_options"] = {}
    patcher.ModelPatcher.set_model_optimized_attention(
        model, attention.REGISTERED_ATTENTION_FUNCTIONS[name])
    return model


def observe(model):
    return storage._model_signature(model, "fixture")


def remake(core, monkeypatch, name, *, raw_code=None, defaults=None):
    attention, _ = core
    old = attention.REGISTERED_ATTENTION_FUNCTIONS[name]
    raw = old.__wrapped__
    new = types.FunctionType(raw_code or raw.__code__, raw.__globals__,
                             raw.__name__, raw.__defaults__ if defaults is None else defaults,
                             raw.__closure__)
    new.__module__, new.__qualname__ = raw.__module__, raw.__qualname__
    new.__kwdefaults__ = copy.copy(raw.__kwdefaults__)
    new.__dict__.update(raw.__dict__)
    wrapped = attention.wrap_attn(new)
    wrapped.container_function = old.container_function
    monkeypatch.setitem(attention.REGISTERED_ATTENTION_FUNCTIONS, name, wrapped)
    monkeypatch.setattr(attention, "attention_" + name, wrapped)
    return wrapped


@pytest.mark.parametrize("backend", ["pytorch", "comfy_kitchen_int8"])
def test_real_core_backend_is_finite_clone_stable_and_non_mutating(core_attention, monkeypatch, backend):
    model = model_with(core_attention, backend)
    wrapped = core_attention[0].REGISTERED_ATTENTION_FUNCTIONS[backend]
    override = model.model_options["transformer_options"]["optimized_attention_override"]
    original = (dict(vars(wrapped)), dict(vars(override)), copy.copy(model.model_options))
    watched = {wrapped.__code__, wrapped.__wrapped__.__code__}
    if wrapped.container_function:
        watched.add(wrapped.container_function.__code__)
    calls = []
    previous = sys.getprofile()
    sys.setprofile(lambda frame, event, arg: calls.append(frame.f_code.co_name)
                   if event == "call" and frame.f_code in watched else None)
    try:
        before, safe = observe(model)
    finally:
        sys.setprofile(previous)
    assert safe, before["model_options"]
    assert not calls
    assert original == (vars(wrapped), vars(override), model.model_options)
    cloned, cloned_safe = observe(copy.deepcopy(model))
    assert cloned_safe and cloned == before
    remake(core_attention, monkeypatch, backend)
    recreated, recreated_safe = observe(model_with(core_attention, backend))
    assert recreated_safe and recreated == before
    attention = before["model_options"]["transformer_options"]["optimized_attention_override"]
    assert attention["backend"] == backend
    assert attention["core_attention_signature_version"] == 1
    assert attention["wrapper"]["closure"][-1]["value"] == {"reference": "wrapper"}


def test_pytorch_and_kitchen_are_distinct(core_attention):
    a, safe_a = observe(model_with(core_attention, "pytorch"))
    b, safe_b = observe(model_with(core_attention, "comfy_kitchen_int8"))
    assert safe_a and safe_b and a != b


@pytest.mark.parametrize("backend", ["pytorch", "comfy_kitchen_int8"])
@pytest.mark.parametrize("change", ["code", "defaults", "helper"])
def test_attention_implementation_changes_identity(core_attention, monkeypatch, backend, change):
    before, safe = observe(model_with(core_attention, backend))
    assert safe
    attention, _ = core_attention
    if change == "code":
        raw = attention.REGISTERED_ATTENTION_FUNCTIONS[backend].__wrapped__
        def change_constant(c):
            if isinstance(c, tuple):
                return tuple(change_constant(v) for v in c)
            return "changed_scale" if c == "scale" else c
        constants = tuple(change_constant(c) for c in raw.__code__.co_consts)
        assert constants != raw.__code__.co_consts
        remake(core_attention, monkeypatch, backend, raw_code=raw.__code__.replace(co_consts=constants))
    elif change == "defaults":
        raw = attention.REGISTERED_ATTENTION_FUNCTIONS[backend].__wrapped__
        remake(core_attention, monkeypatch, backend, defaults=(17,) + raw.__defaults__[1:])
    else:
        helper = attention._heads_from_dim
        constants = tuple(2 if c == 0 else c for c in helper.__code__.co_consts)
        monkeypatch.setattr(attention, "_heads_from_dim",
                            types.FunctionType(helper.__code__.replace(co_consts=constants),
                                               helper.__globals__, helper.__name__))
    after, after_safe = observe(model_with(core_attention, backend))
    assert after_safe and after != before


@pytest.mark.parametrize("slot", ["inner", "outer"])
@pytest.mark.parametrize("kind", ["function", "opaque", "none"])
def test_container_changes_are_recorded_and_cannot_be_certified(core_attention, monkeypatch, slot, kind):
    model = model_with(core_attention, "comfy_kitchen_int8")
    before, safe = observe(model)
    assert safe
    target = (core_attention[0].attention_comfy_kitchen_int8 if slot == "inner" else
              model.model_options["transformer_options"]["optimized_attention_override"])
    class Opaque:
        __slots__ = ()
        def __call__(self, *args):
            raise AssertionError("signature must not invoke container")
    def replacement(*args):
        raise AssertionError("signature must not invoke container")
    value = {"function": replacement, "opaque": Opaque(), "none": None}[kind]
    monkeypatch.setattr(target, "container_function", value)
    after, safe_after = observe(model)
    assert after != before and not safe_after


def test_unrelated_opaque_cfg_is_not_promoted(core_attention):
    model = model_with(core_attention, "pytorch")
    assert observe(model)[1]
    model.model_options["sampler_cfg_function"] = object()
    assert not observe(model)[1]
    contract, safe, reasons = signatures._sampling_contract(model=model)
    assert contract and not safe and reasons
    assert contract["global"]["sampling_contract_version"] == 6


def test_unregistered_or_foreign_setter_keeps_generic_policy(core_attention, monkeypatch):
    attention, patcher = core_attention
    model = model_with(core_attention, "pytorch")
    callback = model.model_options["transformer_options"]["optimized_attention_override"]
    monkeypatch.delitem(attention.REGISTERED_ATTENTION_FUNCTIONS, "pytorch")
    assert storage._observe_model_options(model.model_options) == storage._observe(model.model_options)
    assert not observe(model)[1]
    def foreign(_, *args, **kwargs):
        return None
    model.model_options["transformer_options"]["optimized_attention_override"] = foreign
    assert storage._observe_model_options(model.model_options) == storage._observe(model.model_options)
    assert model.model_options["transformer_options"]["optimized_attention_override"] is foreign
    assert callback is not foreign


def test_missing_provider_and_unknown_native_binding_are_unsafe(core_attention, monkeypatch):
    model = model_with(core_attention, "pytorch")
    monkeypatch.setattr(torch.nn.functional, "scaled_dot_product_attention", lambda *a: 0)
    result, safe = observe(model)
    assert not safe
    assert "observation_error" in result["model_options"]["transformer_options"]["optimized_attention_override"]


def test_no_override_existing_v6_contract_is_byte_equivalent(monkeypatch):
    torch.manual_seed(31)
    model, clip, vae = signatures._Model(), signatures._Clip(), signatures._VideoVAE()
    model.model_options = {"transformer_options": {}, "disable_cfg1_optimization": True}
    # Fixed v3.9.1 source, before the Attention signature repair; also works in ZIP installs.
    fixture = ROOT / "tests/fixtures/issue31_v391_model_signature.py.txt"
    provenance = json.loads((ROOT / "tests/fixtures/issue31_v391_model_signature.json").read_text(encoding="utf-8"))
    original_bytes = fixture.read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == provenance["fixture_sha256"]
    original = original_bytes.decode("utf-8")
    node = next(n for n in ast.parse(original).body if isinstance(n, ast.FunctionDef) and n.name == "_model_signature")
    scope = dict(vars(storage))
    exec(compile(ast.Module(body=[node], type_ignores=[]), "original_model_signature.py", "exec"), scope)
    before, safe_before, _ = signatures._sampling_contract(model=model, clip=clip, video_vae=vae, reroll_from_chunk=0)
    with monkeypatch.context() as context:
        context.setattr(storage, "_model_signature", scope["_model_signature"])
        legacy, safe_legacy, _ = signatures._sampling_contract(model=model, clip=clip, video_vae=vae, reroll_from_chunk=0)
    assert safe_before and safe_legacy
    assert storage._canonical(before) == storage._canonical(legacy)
    assert storage.revision_identity(before) == storage.revision_identity(legacy)
    assert storage.SAMPLING_CONTRACT_VERSION == 6 and storage.RUNTIME_SIGNATURE_VERSION == 1


def test_ordinary_custom_override_keeps_existing_descriptor():
    model = signatures._Model()
    model.model_options = {"transformer_options": {"optimized_attention_override": lambda x: x}}
    assert storage._observe_model_options(model.model_options) == storage._observe(model.model_options)


@pytest.mark.parametrize("backend", ["pytorch", "comfy_kitchen_int8"])
def test_same_backend_reuses_prefix_but_changed_backend_does_not(tmp_path, core_attention, backend):
    model = model_with(core_attention, backend)
    torch.manual_seed(31)
    clip, vae = signatures._Clip(), signatures._VideoVAE()
    contract, safe, _ = signatures._sampling_contract(model=model, clip=clip, video_vae=vae, reroll_from_chunk=0)
    assert safe
    source = review._persist(tmp_path, contract, prefix=1, review_unit=(1, 1),
                             updated_utc="2026-10-14T00:00:00+00:00")
    before_files = {str(p):p.read_bytes() for p in source.run_root.rglob("*") if p.is_file()}
    same, same_safe, _ = signatures._sampling_contract(model=copy.deepcopy(model), clip=clip, video_vae=vae, reroll_from_chunk=0)
    assert same_safe and storage.revision_identity(same) == storage.revision_identity(contract)
    reader = review._controller(tmp_path, same)
    reader.configure_review(generation_mode=review.GENERATION_MODE_REVIEW, review_action=review.REVIEW_ACTION_CONTINUE)
    prefix = reader._load_validated_review_prefix(same, resume_safe=same_safe)
    assert len(prefix.entries) == 1
    other = "pytorch" if backend == "comfy_kitchen_int8" else "comfy_kitchen_int8"
    changed, changed_safe, _ = signatures._sampling_contract(model=model_with(core_attention, other),
                                                            clip=clip, video_vae=vae, reroll_from_chunk=0)
    assert changed_safe and storage.revision_identity(changed) != storage.revision_identity(contract)
    changed_reader = review._controller(tmp_path, changed)
    changed_reader.configure_review(generation_mode=review.GENERATION_MODE_REVIEW, review_action=review.REVIEW_ACTION_CONTINUE)
    assert not changed_reader._load_validated_review_prefix(changed, resume_safe=changed_safe).entries
    assert before_files == {str(p):p.read_bytes() for p in source.run_root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("entry_point", ["review", "head", "import", "compatible", "take"])
def test_old_unsafe_attention_manifest_stays_read_only_and_unmodified(tmp_path, core_attention, monkeypatch, entry_point):
    model = model_with(core_attention, "pytorch")
    options = model.model_options
    # Original depth-limited observation, producing the old unsafe v6 contract.
    with monkeypatch.context() as context:
        context.setattr(storage, "_observe_model_options", storage._observe)
        old, old_safe, reasons = signatures._sampling_contract(model=model, reroll_from_chunk=0)
    assert not old_safe and reasons
    source = review._persist(tmp_path, old, prefix=1, review_unit=(1, 1),
                             updated_utc="2026-10-14T00:00:00+00:00")
    source.manifest["resume_safe"] = False
    source.manifest["resume_disabled_reasons"] = reasons
    source._write_manifest()
    before = {str(p):p.read_bytes() for p in source.run_root.rglob("*") if p.is_file()}
    reader = review._controller(tmp_path, old)
    reader.configure_review(generation_mode=review.GENERATION_MODE_REVIEW, review_action=review.REVIEW_ACTION_CONTINUE)
    assert storage._reusable_manifest(source.manifest) is False
    if entry_point == "review":
        assert not reader._load_validated_review_prefix(old, resume_safe=True).entries
    elif entry_point == "head":
        assert reader.find_latest_review_head(old, resume_safe=True) is None
    elif entry_point == "import":
        assert reader._find_plan_import(old, resume_safe=True) is None
    elif entry_point == "compatible":
        assert reader._compatible_plan_prefix(source.manifest, old, resume_safe=True) == ([], [])
    else:
        reader.take_group = 1
        reader.take_revision_id = review._project(source)["canonical_head_revision_id"]
        with pytest.raises(storage.RunStorageError, match="read-only"):
            reader._validated_take_selection(old, resume_safe=True)
    assert before == {str(p):p.read_bytes() for p in source.run_root.rglob("*") if p.is_file()}


def test_provider_policy_changes_are_observed(core_attention, monkeypatch):
    import comfy_kitchen.sage_attention as kitchen_attention
    model = model_with(core_attention, "comfy_kitchen_int8")
    before, safe = observe(model)
    assert safe
    monkeypatch.setattr(kitchen_attention, "LARGE_CTA_K", kitchen_attention.LARGE_CTA_K + 1)
    after, safe_after = observe(model)
    assert safe_after and before != after
@pytest.mark.parametrize("slot", ["setter_globals", "raw_globals", "wrapper_code"])
def test_lookalike_core_structure_is_not_promoted(core_attention, monkeypatch, slot):
    attention, _ = core_attention
    model = model_with(core_attention, "pytorch")
    if slot == "setter_globals":
        value = model.model_options["transformer_options"]["optimized_attention_override"]
        value = types.FunctionType(value.__code__, dict(value.__globals__), value.__name__,
                                   value.__defaults__, value.__closure__)
        model.model_options["transformer_options"]["optimized_attention_override"] = value
    elif slot == "raw_globals":
        wrapped = attention.attention_pytorch
        raw = wrapped.__wrapped__
        new = types.FunctionType(raw.__code__, dict(raw.__globals__), raw.__name__,
                                 raw.__defaults__, raw.__closure__)
        wrapped = attention.wrap_attn(new)
        monkeypatch.setitem(attention.REGISTERED_ATTENTION_FUNCTIONS, "pytorch", wrapped)
        monkeypatch.setattr(attention, "attention_pytorch", wrapped)
        model = model_with(core_attention, "pytorch")
    else:
        wrapped = attention.attention_pytorch
        monkeypatch.setattr(wrapped, "__code__", wrapped.__code__.replace(
            co_consts=wrapped.__code__.co_consts + ("unrecognized wrapper",)))
    assert not observe(model)[1]


def test_torch_dispatch_flag_changes_identity(core_attention):
    model = model_with(core_attention, "pytorch")
    enabled = torch.backends.cuda.math_sdp_enabled()
    before, safe = observe(model)
    assert safe
    try:
        torch.backends.cuda.enable_math_sdp(not enabled)
        after, after_safe = observe(model)
        assert after_safe and after != before
    finally:
        torch.backends.cuda.enable_math_sdp(enabled)


@pytest.mark.parametrize("backend", ["pytorch", "comfy_kitchen_int8"])
def test_signature_is_stable_in_separate_processes_and_hash_seeds(core_attention, backend):
    import os
    import comfy
    core_root = str(Path(core_attention[1].__file__).resolve().parent.parent)
    script = r"""
import importlib.util,json,os,sys
sys.path.insert(0,CORE_ROOT)
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import torch
torch.cuda._lazy_init=lambda: (_ for _ in ()).throw(RuntimeError("CUDA forbidden"))
from comfy.cli_args import args
args.cpu=True
from comfy.ldm.modules import attention
from comfy import model_patcher
name="ComfyUI_H3_Continuum_Join"
spec=importlib.util.spec_from_file_location(name,ROOT+"/__init__.py",submodule_search_locations=[ROOT])
sys.modules[name]=importlib.util.module_from_spec(spec)
from ComfyUI_H3_Continuum_Join import run_storage as s
from types import SimpleNamespace
class Model:
    def __init__(self):
        self.model=SimpleNamespace(diffusion_model=torch.nn.Linear(2,2))
        self.wrappers={}
        self.patches={}
        self.model_options={"transformer_options":{}}
    def model_dtype(self): return torch.float32
    def model_size(self): return 4
torch.manual_seed(31)
model=Model()
attention.REGISTERED_ATTENTION_FUNCTIONS["comfy_kitchen_int8"]=attention.attention_comfy_kitchen_int8
model_patcher.ModelPatcher.set_model_optimized_attention(model,attention.REGISTERED_ATTENTION_FUNCTIONS[BACKEND])
descriptor,safe=s._model_signature(model,"fixture")
assert safe,descriptor["model_options"]
print(s._hash(descriptor))
"""
    script = "CORE_ROOT="+repr(core_root)+"\nROOT="+repr(str(ROOT))+"\nBACKEND="+repr(backend)+"\n"+script
    results = []
    for seed in ("1", "93017"):
        result = subprocess.run([sys.executable, "-B", "-c", script],
                                env={**os.environ, "CUDA_VISIBLE_DEVICES":"-1", "PYTHONHASHSEED":seed},
                                capture_output=True, text=True, timeout=90)
        assert result.returncode == 0, result.stderr + result.stdout
        results.append(result.stdout.strip().splitlines()[-1])
    assert results[0] == results[1]
def test_unobservable_global_helper_state_stays_unsafe(core_attention, monkeypatch):
    attention, _ = core_attention
    model = model_with(core_attention, "pytorch")
    before, safe = observe(model)
    assert safe
    scope = vars(attention)
    exec("def issue31_helper(*args):\n    return ISSUE31_UNOBSERVABLE_STATE", scope)
    try:
        monkeypatch.setattr(attention, "ISSUE31_UNOBSERVABLE_STATE", object(), raising=False)
        monkeypatch.setattr(attention, "_heads_from_dim", scope["issue31_helper"])
        after, after_safe = observe(model)
        assert after != before and not after_safe
    finally:
        scope.pop("issue31_helper", None)


def test_fallback_pytorch_implementation_changes_kitchen_identity(core_attention, monkeypatch):
    attention, _ = core_attention
    model = model_with(core_attention, "comfy_kitchen_int8")
    before, safe = observe(model)
    assert safe
    raw = attention.attention_pytorch.__wrapped__
    remake(core_attention, monkeypatch, "pytorch", defaults=(19,) + raw.__defaults__[1:])
    after, after_safe = observe(model)
    assert after != before
