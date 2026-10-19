import pytest


@pytest.mark.parametrize("case", [
    "v6 read-only reports saved preview source and keeps actions disabled",
    "preview setting remedies preserve generation VAE guidance",
    "missing compatibility metadata is not mislabeled v5 or a known KJ error",
    "unknown saved reasons do not expose paths or unbounded text",
    "history reasons follow the selected Take rather than the canonical revision",
    "saved compatibility metadata controls Review with optional real backend vectors",
])
def test_readonly_reason_with_real_frontend(review_queue_results, case):
    assert review_queue_results[case]["pass"]
