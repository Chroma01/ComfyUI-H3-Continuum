from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import json
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest
import torch

from ComfyUI_H3_Continuum_Join import run_storage as storage
from ComfyUI_H3_Continuum_Join import spectrum_signature as adapter
from . import test_issue31_attention_signature as attention_tests
from .test_issue31_attention_signature import core_attention
from . import test_v31_run_storage as signatures
from . import test_v38_review_run_storage as review


@pytest.fixture(params=["local", "public029"])
def spectrum(require_comfy_core, request):
    root = os.environ.get("H3_SPECTRUM_TEST_ROOT" if request.param == "local" else "H3_SPECTRUM_PUBLIC_TEST_ROOT")
    if not root:
        pytest.skip("real audited Spectrum checkout is not configured")
    package = types.ModuleType("issue31_spectrum_tests_" + request.param)
    package.__path__ = [root]
    sys.modules[package.__name__] = package
    prefix = package.__name__ + ".comfyui_spectrum_h3"
    sampling = importlib.import_module(prefix + ".sampling")
    runtime = importlib.import_module(prefix + ".runtime")
    config = importlib.import_module(prefix + ".config")
    return sampling, runtime, config


def binding(spectrum, **settings):
    sampling, runtime, config = spectrum
    return sampling.SpectrumH3Binding(runtime.SpectrumH3Runtime(config.SpectrumH3Config(**settings)))


def signature(value):
    result, safe = adapter.spectrum_binding_signature(value)
    assert safe, result.get("unsupported")
    return result


def test_recreated_runtime_and_transient_history_keep_identity(spectrum):
    a, b = binding(spectrum), binding(spectrum)
    before = signature(a)
    assert signature(b) == before
    a.runtime._run_counter += 8
    a.runtime._consecutive_forecasts = 3
    a.runtime._current_window = 3.25
    a.runtime.forecaster.update(0.0, torch.arange(12, dtype=torch.float32).reshape(1,12))
    a.runtime.forecaster.update(1.0, torch.arange(12, dtype=torch.float32).reshape(1,12) + 1)
    a.runtime.model_aware.anchor_count = 7
    a.runtime.stats.current_window = 4.0
    assert signature(a) == before


CHANGES = {
    "enabled": {"enabled": False}, "blend_weight": {"blend_weight": 0.6},
    "degree": {"degree": 2, "bootstrap_first_forecast": False},
    "ridge_lambda": {"ridge_lambda": 0.2}, "window_size": {"window_size": 3.0},
    "flex_window": {"flex_window": 1.0},
    "warmup_steps": {"warmup_steps": 2, "bootstrap_first_forecast": False},
    "tail_actual_steps": {"tail_actual_steps": 2}, "max_history": {"max_history": 9},
    "history_storage": {"history_storage": "vram"}, "debug": {"debug": True},
    "force_actual": {"force_actual": True},
    "bootstrap_first_forecast": {"bootstrap_first_forecast": False},
    "anchor_residual_feedback": {"anchor_residual_feedback": True, "offline_smoothing_replay": False},
    "selective_rollback_correction": {"selective_rollback_correction": True, "offline_smoothing_replay": False},
    "offline_smoothing_replay": {"offline_smoothing_replay": False},
    "audio_blend_weight": {"audio_blend_weight": 0.1},
    "offline_archive_storage": {"offline_archive_storage": "vram"},
    "model_aware_mode": {"model_aware_mode": "full"},
    "model_aware_risk_threshold": {"model_aware_risk_threshold": 0.5},
    "model_aware_trust_shrinkage": {"model_aware_mode": "full", "model_aware_trust_shrinkage": True},
    "model_aware_replay_generic_correction": {"model_aware_replay_generic_correction": True},
    "generic_correction_mode": {"generic_correction_mode": "legacy"},
    "generic_correction_limiter": {"generic_correction_limiter": "tanh"},
    "generic_correction_limit": {"generic_correction_limit": 0.3},
    "generic_correction_attenuation": {"generic_correction_attenuation": "general_confidence"},
    "sa_pece_forecast_policy": {"sa_pece_forecast_policy": "stable_start"},
}


@pytest.mark.parametrize("field", sorted(CHANGES))
def test_every_config_field_changes_identity(spectrum, field):
    before = signature(binding(spectrum))
    changed = signature(binding(spectrum, **CHANGES[field]))
    assert set(before["config"]) == set(CHANGES) == set(adapter.CONFIG_FIELDS)
    assert before != changed and before["config"][field] != changed["config"][field]


@pytest.mark.parametrize("change", ["runtime_code", "wrapper_code", "wrapper_closure", "class_attribute", "source_digest"])
def test_implementation_changes_are_rejected(spectrum, monkeypatch, change):
    item = binding(spectrum)
    signature(item)
    if change == "runtime_code":
        old = spectrum[1].SpectrumH3Runtime.__init__
        monkeypatch.setattr(old, "__code__", old.__code__.replace(co_consts=old.__code__.co_consts + ("changed",)))
    elif change == "wrapper_code":
        old = spectrum[0].outer_sample_wrapper
        monkeypatch.setattr(old, "__code__", old.__code__.replace(co_consts=old.__code__.co_consts + ("changed",)))
    elif change == "wrapper_closure":
        old = spectrum[0].run_selective_rollback_euler
        assert old.__closure__
        cells = list(old.__closure__)
        cells[0] = (lambda value: lambda: value)(object()).__closure__[0]
        changed = types.FunctionType(old.__code__, old.__globals__, old.__name__, old.__defaults__, tuple(cells))
        changed.__module__, changed.__qualname__ = old.__module__, old.__qualname__
        monkeypatch.setattr(spectrum[0], "run_selective_rollback_euler", changed)
    elif change == "class_attribute":
        monkeypatch.setattr(spectrum[1].SpectrumH3Runtime, "extra_contract", 1, raising=False)
    else:
        source, _ = adapter._select_source_profile(Path(spectrum[0].__file__).resolve().parent)
        monkeypatch.setitem(source, "sampling.py", "f" * 64)
    after, safe = adapter.spectrum_binding_signature(item)
    assert not safe and after.get("unsupported")


@pytest.mark.parametrize("change", ["foreign_binding", "binding_subclass", "runtime_extra", "component_extra", "component_setting", "nan_config", "stats_replaced", "missing_runtime_field"])
def test_unknown_binding_and_additional_state_are_not_promoted(spectrum, change):
    item = binding(spectrum)
    if change == "foreign_binding":
        @dataclasses.dataclass(slots=True)
        class SpectrumH3Binding:
            runtime: object
        item = SpectrumH3Binding(item.runtime)
    elif change == "binding_subclass":
        class ExtraBinding(type(item)):
            pass
        item = ExtraBinding(item.runtime)
    elif change == "runtime_extra":
        item.runtime.unrecognized = object()
    elif change == "component_extra":
        item.runtime.forecaster.unrecognized = 1
    elif change == "component_setting":
        item.runtime.forecaster.degree += 1
    elif change == "stats_replaced":
        item.runtime.stats = object()
    elif change == "missing_runtime_field":
        del item.runtime._run_counter
    else:
        object.__setattr__(item.runtime.config, "blend_weight", float("nan"))
    assert adapter.spectrum_binding_signature(item)[1] is False


@pytest.mark.parametrize("backend", ["pytorch", "comfy_kitchen_int8"])
def test_attention_and_spectrum_remain_clone_stable(core_attention, spectrum, backend):
    model = attention_tests.model_with(core_attention, backend)
    original = attention_tests.observe(model)
    model.model_options["spectrum_h3_binding"] = binding(spectrum)
    combined = attention_tests.observe(model)
    assert original[1] and combined[1]
    assert combined[0]["model_options"]["transformer_options"] == original[0]["model_options"]["transformer_options"]
    model.model_options["spectrum_h3_binding"] = binding(spectrum)
    assert attention_tests.observe(model) == combined


@pytest.mark.parametrize("backend", [None, "pytorch", "comfy_kitchen_int8"])
def test_spectrum_absent_preserves_full_phase1_descriptor(core_attention, monkeypatch, backend):
    model = signatures._Model() if backend is None else attention_tests.model_with(core_attention, backend)
    current = attention_tests.observe(model)
    old = storage._observe_attention_model_options(model.model_options)
    assert storage._observe_model_options(model.model_options) == old
    # Independent Phase 1 implementation is frozen in the reviewed test fixture.
    source = (Path(__file__).parent / "fixtures" / "issue31_phase1_model_options.py.txt").read_text()
    scope = dict(vars(storage))
    exec(compile(source, "phase1_options_fixture", "exec"), scope)
    before = scope["_observe_model_options"](model.model_options)
    assert before == old
    torch.manual_seed(315)
    clip, vae = signatures._Clip(), signatures._VideoVAE()
    contract, safe, reasons = signatures._sampling_contract(model=model, clip=clip, video_vae=vae, reroll_from_chunk=0)
    with monkeypatch.context() as context:
        context.setattr(storage, "_observe_model_options", scope["_observe_model_options"])
        previous, previous_safe, previous_reasons = signatures._sampling_contract(model=model, clip=clip, video_vae=vae, reroll_from_chunk=0)
    assert safe == previous_safe and reasons == previous_reasons
    assert storage._canonical(contract) == storage._canonical(previous)
    assert storage.revision_identity(contract) == storage.revision_identity(previous)


@pytest.mark.parametrize("entry_point", ["review", "head", "import", "compatible", "take"])
def test_old_unsafe_spectrum_history_is_unmodified(tmp_path, core_attention, spectrum, monkeypatch, entry_point):
    model = attention_tests.model_with(core_attention, "pytorch")
    model.model_options["spectrum_h3_binding"] = binding(spectrum)
    with monkeypatch.context() as ctx:
        ctx.setattr(storage, "_observe_model_options", storage._observe_attention_model_options)
        old, safe, reasons = signatures._sampling_contract(model=model, reroll_from_chunk=0)
    assert not safe and reasons
    source = review._persist(tmp_path, old, prefix=1, review_unit=(1,1), updated_utc="2026-10-15T00:00:00+00:00")
    source.manifest["resume_safe"] = False
    source.manifest["resume_disabled_reasons"] = reasons
    source._write_manifest()
    before = {str(p):p.read_bytes() for p in source.run_root.rglob("*") if p.is_file()}
    current, current_safe, _ = signatures._sampling_contract(model=model, reroll_from_chunk=0)
    assert current_safe and storage.revision_identity(current) != storage.revision_identity(old)
    reader = review._controller(tmp_path, old)
    reader.configure_review(generation_mode=review.GENERATION_MODE_REVIEW, review_action=review.REVIEW_ACTION_CONTINUE)
    assert not storage._reusable_manifest(source.manifest)
    if entry_point == "review": assert not reader._load_validated_review_prefix(old,resume_safe=True).entries
    elif entry_point == "head": assert reader.find_latest_review_head(old,resume_safe=True) is None
    elif entry_point == "import": assert reader._find_plan_import(old,resume_safe=True) is None
    elif entry_point == "compatible": assert reader._compatible_plan_prefix(source.manifest,old,resume_safe=True)==([],[])
    else:
        reader.take_group=1;reader.take_revision_id=review._project(source)["canonical_head_revision_id"]
        with pytest.raises(storage.RunStorageError,match="read-only"):reader._validated_take_selection(old,resume_safe=True)
    assert before=={str(p):p.read_bytes() for p in source.run_root.rglob("*") if p.is_file()}


def test_imports_and_profile_cache_do_not_change_identity(spectrum, monkeypatch):
    item=binding(spectrum);before=signature(item)
    prefix=spectrum[0].__name__.rsplit('.',1)[0]
    importlib.import_module(prefix+'.experiments')
    aware=importlib.import_module(prefix+'.model_aware')
    monkeypatch.setitem(aware._PROFILE_CACHE,('temporary',),object())
    assert signature(item)==before



def test_imported_original_implementation_changes_are_rejected(spectrum, monkeypatch):
    item=binding(spectrum);signature(item)
    module=importlib.import_module(spectrum[0].__name__.rsplit('.',1)[0]+'.generic_correction')
    old=module._ORIGINAL_FORECASTER_UPDATE
    changed=types.FunctionType(old.__code__.replace(co_consts=old.__code__.co_consts+('changed imported original',)),old.__globals__,old.__name__,old.__defaults__,old.__closure__)
    changed.__module__,changed.__qualname__=old.__module__,old.__qualname__
    monkeypatch.setattr(module,'_ORIGINAL_FORECASTER_UPDATE',changed)
    assert adapter.spectrum_binding_signature(item)[1] is False


@pytest.mark.parametrize('backend',['pytorch','comfy_kitchen_int8'])
def test_spectrum_same_settings_reuse_and_changed_settings_reject(tmp_path,core_attention,spectrum,backend):
    model=attention_tests.model_with(core_attention,backend)
    model.model_options['spectrum_h3_binding']=binding(spectrum)
    torch.manual_seed(315);clip,vae=signatures._Clip(),signatures._VideoVAE()
    contract,safe,_=signatures._sampling_contract(model=model,clip=clip,video_vae=vae,reroll_from_chunk=0);assert safe
    source=review._persist(tmp_path,contract,prefix=1,review_unit=(1,1),updated_utc='2026-10-15T00:00:00+00:00')
    before={str(p):p.read_bytes() for p in source.run_root.rglob('*') if p.is_file()}
    reader=review._controller(tmp_path,contract);reader.configure_review(generation_mode=review.GENERATION_MODE_REVIEW,review_action=review.REVIEW_ACTION_CONTINUE)
    assert len(reader._load_validated_review_prefix(contract,resume_safe=True).entries)==1
    model.model_options['spectrum_h3_binding']=binding(spectrum,blend_weight=0.6)
    changed,changed_safe,_=signatures._sampling_contract(model=model,clip=clip,video_vae=vae,reroll_from_chunk=0);assert changed_safe
    other=review._controller(tmp_path,changed);other.configure_review(generation_mode=review.GENERATION_MODE_REVIEW,review_action=review.REVIEW_ACTION_CONTINUE)
    assert not other._load_validated_review_prefix(changed,resume_safe=True).entries
    assert before=={str(p):p.read_bytes() for p in source.run_root.rglob('*') if p.is_file()}


def test_signature_stable_across_processes_and_module_aliases(spectrum,core_attention):
    root=str(Path(spectrum[0].__file__).resolve().parents[1])
    core_root=str(Path(core_attention[1].__file__).resolve().parents[1])
    adapter_path=str(Path(adapter.__file__).resolve())
    script=r"""
import os,sys,types,importlib,importlib.util,json,hashlib
os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.path.insert(0,CORE_ROOT)
import torch
torch.cuda._lazy_init=lambda: (_ for _ in ()).throw(RuntimeError('CUDA forbidden'))
from comfy.cli_args import args
args.cpu=True
package=types.ModuleType('process_alias_'+os.environ['PYTHONHASHSEED']);package.__path__=[PROVIDER_ROOT];sys.modules[package.__name__]=package
prefix=package.__name__+'.comfyui_spectrum_h3'
s=importlib.import_module(prefix+'.sampling');r=importlib.import_module(prefix+'.runtime');c=importlib.import_module(prefix+'.config')
spec=importlib.util.spec_from_file_location('process_adapter',ADAPTER_FILE);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
value,safe=a.spectrum_binding_signature(s.SpectrumH3Binding(r.SpectrumH3Runtime(c.SpectrumH3Config())))
assert safe,value.get('unsupported')
print(hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest())
"""
    script=script.replace('CORE_ROOT',repr(core_root)).replace('PROVIDER_ROOT',repr(root)).replace('ADAPTER_FILE',repr(adapter_path))
    outputs=[]
    for seed in ('13','71'):
        env=dict(os.environ,PYTHONHASHSEED=seed,PYTHONDONTWRITEBYTECODE='1')
        output=subprocess.check_output([sys.executable,'-c',script],env=env,text=True)
        outputs.append(output.strip().splitlines()[-1])
    assert outputs[0]==outputs[1]


def test_core_node_registration_location_is_not_generation_identity(spectrum,monkeypatch):
    item=binding(spectrum);before=signature(item)
    prefix=spectrum[0].__name__.rsplit('.',1)[0]
    for suffix in ['nodes','objective_media_nodes']:
        module=importlib.import_module(prefix+'.'+suffix)
        for cls in module.NODE_CLASS_MAPPINGS.values():
            monkeypatch.setattr(cls,'RELATIVE_PYTHON_MODULE','custom_nodes.test_location',raising=False)
    assert signature(item)==before


def test_original_local_profile_descriptor_is_unchanged(spectrum):
    item=binding(spectrum)
    source, _ = adapter._select_source_profile(Path(spectrum[0].__file__).resolve().parent)
    if source is not adapter.SUPPORTED_SOURCE:
        pytest.skip("original descriptor fixture covers the pre-existing local profile")
    scope={"__file__":adapter.__file__}
    fixture=Path(__file__).parent/"fixtures"/"issue31_local_spectrum_signature.py.txt"
    exec(compile(fixture.read_text(),str(fixture),"exec"),scope)
    assert scope["spectrum_binding_signature"](item)==adapter.spectrum_binding_signature(item)

def test_foreign_provider_file_set_stays_unsafe(tmp_path):
    (tmp_path/"unknown.py").write_text("pass")
    with pytest.raises(ValueError,match="unsupported provider source set"):
        adapter._select_source_profile(tmp_path)


def test_foreign_module_closure_is_rejected():
    with pytest.raises(ValueError, match="unsupported provider module closure"):
        adapter._callable_value(types.ModuleType("foreign_provider"),provider_prefix="known.comfyui_spectrum_h3")

def test_unloaded_module_cannot_impersonate_provider():
    with pytest.raises(ValueError, match="provider module closure is not loaded"):
        adapter._callable_value(types.ModuleType("known.comfyui_spectrum_h3.runtime"),provider_prefix="known.comfyui_spectrum_h3")

def test_loaded_implementation_profiles_are_packaged():
    root=Path(adapter.__file__).parent
    for filename in ["spectrum_provider_v1.json","spectrum_provider_v029.json"]:
        assert json.loads((root/filename).read_text())["format"]=="audited_spectrum_loaded_implementation_v1"
    assert len(adapter.SUPPORTED_SOURCE)==44 and len(adapter.PUBLIC_SOURCE_029)==55
