"""Reject a gap in capped Review before any sampling or persistence."""
import pytest

from ComfyUI_H3_Continuum_Join import graph_contract, run_storage as rs
from ComfyUI_H3_Continuum_Join.v3.review_control import ReviewControlError
from . import test_v38_review_control as control
from . import test_v38_review_execution_cap as cap
from . import test_v38_review_run_storage as storage


def _resolve(prefix, target, *, chunks=6, terminal=False, **kwargs):
    return control._resolve(
        configured_chunks=chunks, validated_prefix_count=prefix,
        terminal_merge_enabled=terminal,
        terminal_pair_start=chunks-1 if terminal else None,
        latest_review_unit=(control._review_unit(chunks-1, chunks) if terminal and prefix == chunks
                            else control._review_unit(prefix) if prefix else None),
        latest_revision_status="complete" if prefix == chunks else "review_ready" if prefix else None,
        manual_regenerate_from=target, **kwargs,
    )


@pytest.mark.parametrize("prefix,target", [(0, 2), (0, 6), (1, 3), (2, 4)])
@pytest.mark.parametrize("as_int", [True, False])
def test_gap_is_rejected_for_literal_or_resolved_external_int(prefix, target, as_int):
    with pytest.raises(ReviewControlError, match="accepted prefix"):
        _resolve(prefix, target if as_int else f"Chunk {target}")


@pytest.mark.parametrize("prefix,target", [(0, 1), (1, 2), (2, 1), (2, 3), (6, 6)])
def test_existing_group_or_next_frontier_is_allowed(prefix, target):
    result = _resolve(prefix, target)
    assert result.next_review_unit_start == target
    assert result.effective_regenerate_from == target


@pytest.mark.parametrize("target", [2, 3])
def test_terminal_pair_is_checked_by_physical_start(target):
    with pytest.raises(ReviewControlError, match="accepted prefix"):
        _resolve(0, target, chunks=3, terminal=True)
    result = _resolve(1, target, chunks=3, terminal=True)
    assert (result.next_review_unit_start, result.next_review_unit_end) == (2, 3)
    assert result.effective_regenerate_from == target


@pytest.mark.parametrize("options", [dict(generation_mode="Full Run"), dict(review_action="Finish Remaining")])
def test_uncapped_modes_keep_the_existing_future_boundary_behavior(options):
    assert _resolve(0, 6, **options).max_new_physical_groups is None


def test_real_orchestration_rejects_gap_without_sample_commit_or_revision(tmp_path, monkeypatch):
    runtime = cap._install_fake_runtime(monkeypatch)
    c = rs.RunStorageController("synthetic-future-boundary")
    c.run_root = tmp_path / "run"
    c.revisions_root = c.run_root / "revisions"
    c.configure_review(generation_mode="Review Each Chunk", review_action="Continue / Next", manual_regenerate_from=6)

    def contract_fixture(**kwargs):
        contract = storage._contract(chunks=kwargs["prompt_plan"]["chunks"])
        contract["global"]["base_seed"] = kwargs["base_seed"]
        contract["prompt_hashes"] = kwargs["prompt_plan"]["hashes"]
        contract["nonce_lineage_sha256"] = rs._nonce_lineage_hash(contract)
        return rs._apply_reroll_branch_contract(contract, boundary=6, requested_nonce=0, effective_nonce=0), True, []

    monkeypatch.setattr(rs, "build_sampling_contract", contract_fixture)
    monkeypatch.setattr(graph_contract, "build_upstream_graph_contract", lambda *a, **k: ({}, True, []))
    monkeypatch.setattr(rs, "get_active_run_storage", lambda: c)
    with pytest.raises(ReviewControlError, match="accepted prefix"):
        cap._run_sequence(runtime, chunks=6)
    assert runtime.samples == []
    assert c.manifest is None
    assert not c.revisions_root.exists()
