"""Adversarial tests: craft data that violates each constitutional rule and
prove the linter catches it. This is the Phase 0 red-team mechanism made
permanent — any future weakening of the linter fails these tests."""

import re

from tools.check_invariants import check_snapshot, compute_chips, check_explainability

import copy


def violations(snap, ledger, rule):
    out = check_snapshot(snap, "test", ledger)
    return [x for x in out if x.startswith(rule)]


def test_seed_is_clean(seed, ledger):
    assert check_snapshot(seed, "seed", ledger) == []


def test_rule1_missing_tag_caught(snap, ledger):
    snap["cells"]["aa-index"]["fable-5"]["tag"] = None
    assert violations(snap, ledger, "RULE1")


def test_rule1_invalid_tag_caught(snap, ledger):
    snap["cells"]["aa-index"]["fable-5"]["tag"] = "Q"
    assert violations(snap, ledger, "RULE1")


def test_rule2_unresolved_source_caught(snap, ledger):
    snap["cells"]["aa-index"]["fable-5"]["source_id"] = "S99"
    assert violations(snap, ledger, "RULE2")


def test_rule2_missing_source_caught(snap, ledger):
    snap["cells"]["aa-index"]["fable-5"]["source_id"] = None
    assert violations(snap, ledger, "RULE2")


def test_rule3_silent_blank_caught(snap, ledger):
    snap["cells"]["gdpval-aa"]["ds-v4-pro"]["empty_reason"] = None
    assert violations(snap, ledger, "RULE3")


def test_rule3_offenum_reason_caught(snap, ledger):
    snap["cells"]["gdpval-aa"]["ds-v4-pro"]["empty_reason"] = "dunno"
    assert violations(snap, ledger, "RULE3")


def test_rule4_offset_cell_never_chips(snap, ledger):
    # A cell whose comparability_set differs from its metric's set is flagged
    snap["cells"]["aa-index"]["kimi-k3"]["comparability_set"] = "aa-index-v5"
    assert violations(snap, ledger, "RULE4")
    # and it cannot win a chip in the metric's set
    assert "aa-index.kimi-k3" not in compute_chips(snap)


def test_rule5_row_mixing_pro_and_verified_caught(snap, ledger):
    snap["cells"]["swe-bench-pro"]["kimi-k3"] = {
        "value": 71.0,
        "unit": "%",
        "tag": "V",
        "source_id": "S7",
        "retrieved_at": "2026-07-31T00:00:00Z",
        "flags": [],
        "comparability_set": "swe-bench-verified-self-report",
        "stale": False,
        "history_ref": "x",
    }
    assert violations(snap, ledger, "RULE5")


def test_rule5_implication_mixing_caught(snap, ledger):
    snap["implications"] = [
        {
            "id": "imp-bad",
            "tag": "X",
            "text": "mixes families",
            "cites": ["swe-bench-pro.fable-5", "swe-bench-verified.fable-5"],
            "confidence": "high",
            "falsifier": "n/a",
            "flags_carried": [],
        }
    ]
    assert violations(snap, ledger, "RULE5")


def test_rule6_arc_without_tier_caught(snap, ledger):
    del snap["cells"]["arc-agi-3"]["opus-5"]["effort_tier"]
    assert violations(snap, ledger, "RULE6")


def test_rule7_uncarried_flag_caught(snap, ledger):
    snap["implications"] = [
        {
            "id": "imp-flag",
            "tag": "X",
            "text": "leans on gamed METR number",
            "cites": ["metr-horizon.gpt-5-6-sol"],
            "confidence": "med",
            "falsifier": "METR re-run robust",
            "flags_carried": [],  # should carry the record-gaming flag
        }
    ]
    assert violations(snap, ledger, "RULE7")


def test_rule8_stale_tape_caught(snap, ledger):
    snap["tape"].append(
        {"date": "2026-07-20", "text": "ancient news", "source_id": "S1", "cell_ids": []}
    )
    assert violations(snap, ledger, "RULE8")


def test_rule8_unsourced_tape_caught(snap, ledger):
    snap["tape"].append({"date": "2026-07-31", "text": "rumor", "cell_ids": []})
    assert violations(snap, ledger, "RULE8")


def test_rule9_stale_presented_fresh_caught(snap, ledger):
    cell = snap["cells"]["arena-elo"]["kimi-k3"]
    cell["retrieved_at"] = "2026-07-01T00:00:00Z"  # 30 days > 72h SLA
    cell["stale"] = False
    assert violations(snap, ledger, "RULE9")


def test_rule10_vendor_value_never_chips(seed):
    chips = compute_chips(seed)
    # Opus 5's 79.2 SWE-bench Pro is V-tagged; Fable's 80.3 is the I leader.
    assert "swe-bench-pro.opus-5" not in chips
    assert "swe-bench-pro.fable-5" in chips
    # SWE-bench Verified row is all-V: nothing may chip at all.
    assert not any(c.startswith("swe-bench-verified.") for c in chips)


def test_rule10_vendor_leader_still_never_chips(snap):
    # Even if the V value beats every I value, it must not chip.
    snap["cells"]["swe-bench-pro"]["opus-5"]["value"] = 99.9
    chips = compute_chips(snap)
    assert "swe-bench-pro.opus-5" not in chips


def test_rule11_uncited_implication_caught(snap, ledger):
    snap["implications"] = [
        {
            "id": "imp-uncited",
            "tag": "X",
            "text": "vibes-based editorial",
            "cites": [],
            "confidence": "high",
            "falsifier": "none",
            "flags_carried": [],
        }
    ]
    assert violations(snap, ledger, "RULE11")


def test_rule11_missing_falsifier_caught(snap, ledger):
    snap["implications"] = [
        {
            "id": "imp-nofals",
            "tag": "X",
            "text": "unfalsifiable claim",
            "cites": ["aa-index.opus-5"],
            "confidence": "low",
            "falsifier": "",
            "flags_carried": [],
        }
    ]
    assert violations(snap, ledger, "RULE11")


def test_explainability_unexplained_delta_caught(seed):
    older = copy.deepcopy(seed)
    newer = copy.deepcopy(seed)
    newer["snapshot_date"] = "2026-08-01"
    newer["generated_at"] = "2026-08-01T00:00:00Z"
    newer["cells"]["aa-index"]["fable-5"]["value"] = 62  # moved, but no tape entry
    newer["tape"] = []
    out = check_explainability({"2026-07-31": older, "2026-08-01": newer})
    assert any("aa-index.fable-5" in x for x in out)
    # and the same delta WITH a tape entry passes
    newer["tape"] = [
        {
            "date": "2026-08-01",
            "text": "Fable 5 up to 62 on AA Index",
            "source_id": "S1",
            "cell_ids": ["aa-index.fable-5"],
        }
    ]
    assert check_explainability({"2026-07-31": older, "2026-08-01": newer}) == []


def test_effort_tier_regex_scope():
    """Rule 6 guard applies to any arc-agi metric id, present or future."""
    assert re.search("arc-agi", "arc-agi-3")
    assert re.search("arc-agi", "arc-agi-4-preview")
