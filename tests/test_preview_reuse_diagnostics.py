"""Saved reason projection and real-provider Review continuation, CPU only."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
import torch

from ComfyUI_H3_Continuum_Join import run_storage as storage
from ComfyUI_H3_Continuum_Join import preview_override_signature as adapter
from . import test_v31_run_storage as signatures
from . import test_v38_review_run_storage as review
from .test_issue31_preview_override_signature import kj, wrapper, model_with


def prepare_kwargs(model):
    return dict(model=model, model_fingerprint_value="f" * 64, clip=signatures._Clip(),
        video_vae=signatures._VideoVAE(), sampler=signatures._Sampler(), sigmas=torch.tensor([1., 0.]),
        prompt_plan={"chunks": 3, "hashes": [str(i) * 64 for i in (1, 2, 3)],
                     "mode": "list", "prompts": ["prompt 1", "prompt 2", "prompt 3"]},
        width=96, height=64, chunk_seconds=5., continuity="Balanced", audio_continuity=True,
        base_seed=1, reroll_from_chunk=0, reroll_nonce=0, first_frame_hash="a" * 64,
        last_frame_hash="", identity_hash="fixture", strict_compatibility=True,
        existing_session=None, conditioning_mode="i2va")


def controller_at(path):
    controller = storage.RunStorageController("preview-reuse-test")
    controller.run_root = path
    controller.revisions_root = path / "revisions"
    controller.set_prompt_graph(signatures._prompt_graph(), "42")
    controller.configure_review(generation_mode=review.GENERATION_MODE_REVIEW,
                                review_action=review.REVIEW_ACTION_CONTINUE)
    return controller


@pytest.mark.parametrize("setting", [None, "vae", "audio_vae", "tiny_vae"])
def test_real_provider_saved_take_and_separate_controller_continue(kj, tmp_path, setting):
    item = wrapper(kj)
    if setting is not None:
        setattr(item, setting, "taeh3" if setting == "tiny_vae" else object())
    kwargs = prepare_kwargs(model_with(item))
    source = controller_at(tmp_path)
    source.prepare(**kwargs)
    entry = review._entry(0, source.contract)
    source.commit_group((entry,), positions=(0,))
    source.mark_review_group(start=1, end=1, physical_group=1)
    source.finalize(session={"session_id": "fixture", "chunks": [entry]}, report="CPU fixture",
                    review_pause_metadata=source.review_pause_metadata())
    project = review._project(source)
    take = project["group_revisions"][0]
    expected_safe = setting is None
    assert take["generation_reusable"] is expected_safe
    assert take["sampling_contract_version"] == 6
    if expected_safe:
        assert "resume_disabled_reasons" not in take
    else:
        expected = "KJ preview VAE/Audio VAE or Tiny VAE is outside the supported configuration"
        assert expected in source.manifest["resume_disabled_reasons"]
        assert expected in take["resume_disabled_reasons"]
        assert take["resume_disabled_reasons"] == project["revisions"][0]["resume_disabled_reasons"]
    original_raw = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.rglob("*.safetensors")}
    original_identity = storage.revision_identity(source.contract)
    item.frames.append(object())
    again = controller_at(tmp_path)
    session = again.prepare(**kwargs)
    assert again.reused_count == int(expected_safe)
    assert len((session or {}).get("chunks", [])) == int(expected_safe)
    assert again.review_execution.next_review_unit_start == (2 if expected_safe else 1)
    if expected_safe:
        assert storage.revision_identity(again.contract) == original_identity
    assert original_raw and all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest
                                for p, digest in original_raw.items())


@pytest.mark.parametrize("failure,expected", [
    ("provider source is outside the audited profile", "KJ/Core preview implementation is outside the audited source profiles"),
    ("Core approximate VAE is outside Phase A", "Core approximate-VAE preview is outside the supported configuration"),
    ("loaded code differs from audited source", "KJ preview runtime code or state could not be verified"),
    ("private /local/path exception", "KJ preview runtime code or state could not be verified"),
])
def test_reason_classification_uses_only_observed_slot(failure, expected):
    descriptor = {"wrappers": {"outer_sample": {"kj_preview_override": [
        {"adapter": "kj_preview_override_v1", "unsupported": failure}]}}}
    before = copy.deepcopy(descriptor)
    assert adapter.preview_override_reuse_reasons(descriptor) == [expected]
    assert descriptor == before
    assert adapter.preview_override_reuse_reasons({"other": descriptor}) == []


def test_reasons_do_not_enter_sampling_identity(kj, monkeypatch):
    item = wrapper(kj)
    item.tiny_vae = "taeh3"
    model, clip, vae = model_with(item), signatures._Clip(), signatures._VideoVAE()
    original, safe, reasons = signatures._sampling_contract(model=model, clip=clip, video_vae=vae)
    assert not safe and any(reason in adapter.PREVIEW_REUSE_REASONS for reason in reasons)
    monkeypatch.setattr(storage, "preview_override_reuse_reasons", lambda descriptor: [])
    current, safe, generic = signatures._sampling_contract(model=model, clip=clip, video_vae=vae)
    assert not safe and len(generic) < len(reasons)
    assert storage._canonical(original) == storage._canonical(current)
    assert storage.revision_identity(original) == storage.revision_identity(current)


def test_projection_sanitizes_and_omits_safe_or_missing_reasons():
    contract, safe, _ = signatures._sampling_contract(reroll_from_chunk=0)
    assert safe
    manifest = {"sampling_contract_version": 6, "resume_safe": True, "contract": contract,
                "resume_disabled_reasons": list(adapter.PREVIEW_REUSE_REASONS)}
    assert storage._project_resume_diagnostics(manifest) == {}
    manifest["resume_safe"] = False
    private = "C:/Users/private/file.py" + "x" * 2000
    manifest["resume_disabled_reasons"] = [private] * 12
    projected = storage._project_resume_diagnostics(manifest)["resume_disabled_reasons"]
    assert projected == [storage._UNKNOWN_REUSE_REASON]
    assert private not in json.dumps(projected) and max(map(len, projected)) <= 256
    manifest.pop("resume_disabled_reasons")
    assert storage._project_resume_diagnostics(manifest) == {}


def test_project_reason_belongs_to_its_saved_revision(tmp_path):
    contract, safe, _ = signatures._sampling_contract(reroll_from_chunk=0)
    assert safe
    source = review._persist(tmp_path, contract, prefix=1, review_unit=(1, 1),
                            updated_utc="2026-10-19T00:00:00+00:00")
    source.manifest["resume_safe"] = False
    source.manifest["resume_disabled_reasons"] = ["KJ preview runtime code or state could not be verified"]
    source._write_manifest()
    manifest_before = source._manifest_path().read_bytes()
    source._write_project()
    project = review._project(source)
    assert project["group_revisions"][0]["resume_disabled_reasons"] == source.manifest["resume_disabled_reasons"]
    assert source._manifest_path().read_bytes() == manifest_before


@pytest.mark.parametrize("display_id", [None, "display-node"])
def test_public_node_uses_core_hidden_display_id(kj, monkeypatch, display_id):
    has_display_mapping = "dynprompt" in kj.ModelPreviewOverrideKJ.execute.__code__.co_names
    from comfy_api.latest import io
    # Full-suite helpers can put the plugin ahead of Core; both contain nodes.py.
    core_root = Path(kj.latent_preview.__file__).resolve().parent
    monkeypatch.syspath_prepend(str(core_root))
    from comfy_execution.graph import DynamicPrompt
    import nodes as core_nodes
    assert Path(core_nodes.__file__).resolve() == core_root / "nodes.py"
    node_class = kj.ModelPreviewOverrideKJ
    dynprompt = None
    if display_id is not None:
        dynprompt = DynamicPrompt({display_id: {}})
        dynprompt.add_ephemeral_node("generated-node", {}, display_id, display_id)
    hidden = io.HiddenHolder.from_dict({io.Hidden.unique_id: "generated-node", io.Hidden.dynprompt: dynprompt})
    monkeypatch.setattr(node_class, "hidden", hidden)
    class Model:
        def clone(self):
            return self

        def add_wrapper_with_key(self, kind, key, value):
            self.wrapper = value
    model = Model()
    node_class.execute(model, 512, 80, True, 1, 12)
    assert model.wrapper.node_id == ((display_id or "generated-node") if has_display_mapping else "generated-node")
    assert adapter.preview_override_signature(model.wrapper)[1]
