"""Seed snapshot conforms to the canonical cell schema."""

from tools.check_invariants import EMPTY_REASONS, is_populated, iter_cells

REQUIRED_KEYS = {"value", "unit", "flags", "comparability_set", "stale", "history_ref"}


def test_seed_top_level(seed):
    for key in ("schema_version", "snapshot_date", "generated_at", "models", "metrics", "cells", "tape"):
        assert key in seed


def test_every_cell_has_canonical_keys(seed):
    for metric_id, model_id, cell in iter_cells(seed):
        missing = REQUIRED_KEYS - set(cell)
        assert not missing, f"{metric_id}.{model_id} missing {missing}"
        assert isinstance(cell["flags"], list)
        assert isinstance(cell["stale"], bool)


def test_populated_cells_have_provenance(seed):
    for metric_id, model_id, cell in iter_cells(seed):
        if is_populated(cell):
            assert cell["tag"] in ("I", "V"), f"{metric_id}.{model_id}"
            assert cell["source_id"], f"{metric_id}.{model_id}"
            assert cell["retrieved_at"], f"{metric_id}.{model_id}"


def test_empty_cells_have_enum_reason(seed):
    for metric_id, model_id, cell in iter_cells(seed):
        if not is_populated(cell):
            assert cell.get("empty_reason") in EMPTY_REASONS, f"{metric_id}.{model_id}"


def test_every_metric_covers_every_model(seed):
    models = set(seed["models"])
    for metric_id in seed["metrics"]:
        assert set(seed["cells"][metric_id]) == models, metric_id


def test_seed_regression_values(seed):
    """Spot-check the transcription against the brief's stated numbers."""
    c = seed["cells"]
    assert c["aa-index"]["opus-5"]["value"] == 61
    assert c["aa-index"]["fable-5"]["value"] == 60
    assert c["aa-index"]["ds-v4-pro"]["value"] == 44
    assert c["gdpval-aa"]["opus-5"]["value"] == 1861
    assert c["cost-per-task"]["kimi-k3"]["value"] == 0.94
    assert c["swe-bench-pro"]["fable-5"]["value"] == 80.3
    assert c["swe-bench-pro"]["opus-5"]["tag"] == "V"  # launch claim, not board
    assert c["arc-agi-3"]["opus-5"]["effort_tier"] == "High"
    assert c["metr-horizon"]["gpt-5-6-sol"]["value"] == 11.3
    assert c["arena-elo"]["kimi-k3"]["value"] == 1547
    assert c["swe-bench-verified"]["fable-5"]["value"] == 95.0
    assert c["swe-bench-verified"]["gpt-5-6-sol"]["empty_reason"] == "withheld"
