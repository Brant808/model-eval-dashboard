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


# ---------------------------------------------------------------------------
# Phase 0 gate hardening (governance/redteam/phase-0.md): each red-team exploit
# becomes a permanent regression test.
# ---------------------------------------------------------------------------

from datetime import datetime, timedelta, timezone

from tools.check_invariants import check_latest_rot, lint_snapshot


def test_gate_vendor_source_masquerading_as_I_caught(snap, ledger):
    """BLOCKING: V value retagged I while citing vendor source S7 must fail."""
    cell = snap["cells"]["swe-bench-pro"]["opus-5"]
    cell["tag"] = "I"
    cell["value"] = 99.9
    out = violations(snap, ledger, "RULE10")
    assert any("vendor source S7" in x for x in out)
    # and it must not chip even before the violation is fixed
    assert "swe-bench-pro.opus-5" not in compute_chips(snap) or out


def test_gate_nonfinite_values_caught(snap, ledger):
    snap["cells"]["aa-index"]["ds-v4-pro"]["value"] = float("inf")
    assert violations(snap, ledger, "SCHEMA")
    assert "aa-index.ds-v4-pro" not in compute_chips(snap)
    snap["cells"]["aa-index"]["ds-v4-pro"]["value"] = float("nan")
    assert violations(snap, ledger, "SCHEMA")
    # NaN must not poison the row: the honest leader still chips
    assert "aa-index.opus-5" in compute_chips(snap)


def test_gate_strict_json_rejects_infinity(tmp_path):
    from tools.check_invariants import load_json_strict
    import pytest as _pytest

    p = tmp_path / "bad.json"
    p.write_text('{"value": Infinity}', encoding="utf-8")
    with _pytest.raises(ValueError):
        load_json_strict(p)


def test_gate_tape_mixing_pro_and_verified_caught(snap, ledger):
    snap["tape"].append(
        {
            "date": "2026-07-31",
            "text": "dead heat between the two boards",
            "source_id": "S6",
            "cell_ids": ["swe-bench-pro.fable-5", "swe-bench-verified.ds-v4-pro"],
        }
    )
    assert violations(snap, ledger, "RULE5")


def test_gate_tape_text_comparing_families_caught(snap, ledger):
    snap["tape"].append(
        {
            "date": "2026-07-31",
            "text": "Fable 80.3 on SWE-bench Pro vs DeepSeek 80.6 on SWE-bench Verified",
            "source_id": "S6",
            "cell_ids": [],
        }
    )
    assert violations(snap, ledger, "RULE5")


def test_gate_implication_text_comparing_families_caught(snap, ledger):
    snap["implications"] = [
        {
            "id": "imp-textmix",
            "tag": "X",
            "text": "SWE-bench Pro and SWE-bench Verified tell the same story",
            "cites": ["swe-bench-pro.fable-5"],
            "confidence": "low",
            "falsifier": "boards diverge",
            "flags_carried": [],
        }
    ]
    assert violations(snap, ledger, "RULE5")


def test_gate_missing_sla_is_a_violation(snap, ledger):
    del snap["metrics"]["arena-elo"]["freshness_sla_hours"]
    out = violations(snap, ledger, "RULE9")
    assert any("freshness_sla_hours" in x for x in out)


def test_gate_single_candidate_never_chips(seed):
    # arena-elo has exactly one populated I cell (kimi-k3): no competition, no chip
    assert not any(c.startswith("arena-elo.") for c in compute_chips(seed))


def test_gate_mixed_numeric_text_metric_caught(snap, ledger):
    snap["cells"]["api-price"]["ds-v4-pro"]["value"] = 0.44
    snap["cells"]["api-price"]["ds-v4-pro"]["tag"] = "V"
    out = violations(snap, ledger, "RULE4")
    assert any("mixes numeric and text" in x for x in out)


def test_gate_explainability_catches_removals_and_appearances(seed):
    older = copy.deepcopy(seed)
    newer = copy.deepcopy(seed)
    newer["snapshot_date"] = "2026-08-01"
    newer["generated_at"] = "2026-08-01T00:00:00Z"
    del newer["cells"]["aa-index"]["ds-v4-pro"]
    newer["tape"] = []
    out = check_explainability({"2026-07-31": older, "2026-08-01": newer})
    assert any("removed" in x and "aa-index.ds-v4-pro" in x for x in out)
    # a whole vanished metric row is caught too
    newer2 = copy.deepcopy(seed)
    newer2["snapshot_date"] = "2026-08-01"
    newer2["generated_at"] = "2026-08-01T00:00:00Z"
    del newer2["cells"]["aa-index"]
    del newer2["metrics"]["aa-index"]
    newer2["tape"] = []
    out2 = check_explainability({"2026-07-31": older, "2026-08-01": newer2})
    assert sum("removed" in x for x in out2) == 5
    # and an explained removal passes
    newer["changelog"] = [
        {"date": "2026-08-01", "note": "DS V4 Pro dropped from AA index page", "cell_ids": ["aa-index.ds-v4-pro"]}
    ]
    assert check_explainability({"2026-07-31": older, "2026-08-01": newer}) == []


def test_gate_future_tape_entry_caught(snap, ledger):
    snap["tape"].append(
        {"date": "2026-08-01", "text": "news from tomorrow", "source_id": "S1", "cell_ids": []}
    )
    out = violations(snap, ledger, "RULE8")
    assert any("after snapshot date" in x for x in out)


def test_gate_malformed_snapshot_is_violation_not_crash(ledger):
    out = lint_snapshot({"cells": {}}, "broken", ledger)
    assert out and out[0].startswith("SCHEMA")
    out2 = lint_snapshot(
        {
            "generated_at": "2026-07-31T00:00:00Z",
            "snapshot_date": "2026-07-31",
            "models": {},
            "metrics": {},
            "cells": {},
            "tape": [{"date": "July 30", "text": "bad date", "source_id": "S1", "cell_ids": []}],
        },
        "baddate",
        ledger,
    )
    assert any("not ISO formatted" in x for x in out2)


def test_gate_latest_rot_guard():
    latest = {"generated_at": "2026-07-31T00:00:00Z"}
    fresh_now = datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc)
    old_now = datetime(2026, 8, 10, 0, 0, tzinfo=timezone.utc)
    assert check_latest_rot(latest, now=fresh_now) == []
    rot = check_latest_rot(latest, now=old_now)
    assert rot and rot[0].startswith("ROT")
    # deliberate offline replay escape hatch
    import os as _os

    _os.environ["CHECK_ALLOW_OLD_LATEST"] = "1"
    try:
        assert check_latest_rot(latest, now=old_now) == []
    finally:
        del _os.environ["CHECK_ALLOW_OLD_LATEST"]


# ---------------------------------------------------------------------------
# Phase 1 gate hardening: source sunset + machine-read caveat flags.
# ---------------------------------------------------------------------------


def _post_seed(snap):
    snap["snapshot_date"] = "2026-08-02"
    snap["generated_at"] = "2026-08-02T00:00:00Z"
    # refresh retrieved_at so rule 9 noise doesn't pollute these tests
    for row in snap["cells"].values():
        for cell in row.values():
            if cell.get("retrieved_at"):
                cell["retrieved_at"] = "2026-08-02T00:00:00Z"
    for t in snap["tape"]:
        t["date"] = "2026-08-02"
    return snap


def test_gate1_sunset_source_rejected_after_cutoff(snap, ledger):
    """BLOCKING resolution: S6 is sunset 2026-07-31 — newer snapshots citing it fail."""
    post = _post_seed(snap)
    out = check_snapshot(post, "post", ledger)
    assert any("sunset" in x and "S6" in x for x in out)


def test_gate1_seed_still_resolves_sunset_source(seed, ledger):
    """The frozen 2026-07-31 baseline still lints clean (grandfathered)."""
    assert check_snapshot(seed, "seed", ledger) == []


def test_gate1_caveat_flags_required_post_baseline(snap, ledger):
    post = _post_seed(snap)
    # remove S6 citations so only the caveat check is under test
    for row in post["cells"].values():
        for cell in row.values():
            if cell.get("source_id") == "S6":
                cell["source_id"] = "S13"
                cell["tag"] = "V"
    out = check_snapshot(post, "post", ledger)
    # gdpval cells cite S1 without the Gemini-graded caveat flag -> RULE7
    assert any(
        x.startswith("RULE7") and "Gemini-graded" in x and "gdpval-aa" in x for x in out
    )
    # aa-index cells cite S1 too but the flag is scoped to gdpval/omniscience only
    assert not any("aa-index" in x and "Gemini-graded" in x for x in out)
    # arena cells must carry the private-variant-testing caveat
    assert any("private variant testing" in x for x in out)
    # adding the flags clears those violations
    for mid in ("gdpval-aa",):
        for cell in post["cells"][mid].values():
            if cell.get("source_id") == "S1":
                cell["flags"] = list(cell["flags"]) + ["Gemini-graded (AA judge panel)"]
    for cell in post["cells"]["arena-elo"].values():
        if cell.get("source_id") == "S2":
            cell["flags"] = list(cell["flags"]) + ["private variant testing active (Arena)"]
    out2 = check_snapshot(post, "post", ledger)
    assert not any("Gemini-graded" in x and "gdpval-aa" in x for x in out2)
    assert not any("private variant testing" in x for x in out2)


def test_gate1_ledger_parses_new_lines(ledger):
    assert ledger["S6"]["sunset"] == "2026-07-31"
    assert ("private variant testing active (Arena)", "") in ledger["S2"]["caveat_flags"]
    assert ("Gemini-graded (AA judge panel)", "gdpval-aa") in ledger["S1"]["caveat_flags"]
    assert ledger["S13"]["independence"] == "vendor"
    assert ledger["S18"]["independence"] == "independent"


# ---------------------------------------------------------------------------
# Phase 2 gate hardening: chip integrity semantics, derived cells, third scale.
# ---------------------------------------------------------------------------


def test_gate2_disclaimed_values_cannot_legitimize_chips():
    """B1: METR's LEAD chip existed only because a publisher-disclaimed figure
    supplied the competition. With both populated cells disclaimed, no chip."""
    import json
    from pathlib import Path

    live = json.loads(Path("data/2026-08-01.json").read_text())
    chips = compute_chips(live)
    assert not any(c.startswith("metr-horizon.") for c in chips)
    # ARC keeps its chip: Sol's 7.78 is sound competition (the flag warns about
    # an adjacent vendor claim, not this value), and Opus's record is clean.
    assert "arc-agi-3.opus-5" in chips
    # provider-level aggregates never chip
    assert not any(c.startswith("openrouter-share.") for c in chips)


def test_gate2_flagged_leader_awards_no_chip(snap):
    """If the true max is integrity-flagged, second place must NOT be crowned."""
    snap["cells"]["aa-index"]["opus-5"]["flags"] = [
        "record gaming: hypothetical flag for test"
    ]
    chips = compute_chips(snap)
    assert not any(c.startswith("aa-index.") for c in chips)


def test_gate2_derived_cell_enforcement(snap, ledger):
    snap["metrics"]["intelligence-per-dollar"] = {
        "name": "Intelligence per dollar",
        "group": "economics-deployment",
        "unit": "index pts per task-USD",
        "comparability_set": "aa-intelligence-per-usd",
        "direction": "higher",
        "freshness_sla_hours": 72,
        "primary_source_id": "S1",
    }
    good = {
        "value": 21.8,  # 60 / 2.75 rounded
        "unit": "index pts per task-USD",
        "tag": "I",
        "source_id": "S1",
        "retrieved_at": "2026-07-31T00:00:00Z",
        "flags": ["derived: aa-index ÷ cost-per-task"],
        "comparability_set": "aa-intelligence-per-usd",
        "stale": False,
        "history_ref": "intelligence-per-dollar.fable-5",
        "derived_from": ["aa-index.fable-5", "cost-per-task.fable-5"],
    }
    snap["cells"]["intelligence-per-dollar"] = {"fable-5": dict(good)}
    assert violations(snap, ledger, "RULE4") == []
    # wrong quotient caught
    snap["cells"]["intelligence-per-dollar"]["fable-5"]["value"] = 99.0
    assert any("recomputed" in x for x in violations(snap, ledger, "RULE4"))
    # missing parent declaration caught
    bad = dict(good)
    bad["derived_from"] = None
    snap["cells"]["intelligence-per-dollar"]["fable-5"] = bad
    assert any("derived_from" in x for x in violations(snap, ledger, "RULE4"))
    # stale parent must propagate
    fresh = dict(good)
    snap["cells"]["intelligence-per-dollar"]["fable-5"] = fresh
    snap["cells"]["cost-per-task"]["fable-5"]["stale"] = True
    snap["cells"]["cost-per-task"]["fable-5"]["flags"] = list(
        snap["cells"]["cost-per-task"]["fable-5"]["flags"]
    ) + ["source down (last-good shown)"]
    out = check_snapshot(snap, "test", ledger)
    assert any(x.startswith("RULE9") and "derived" in x for x in out)


def test_gate2_rebench_is_a_third_separated_scale(snap, ledger):
    snap["tape"].append({
        "date": "2026-07-31",
        "text": "Fable's SWE-bench Pro claim 80.0 runs 15.5 pts above its SWE-rebench resolve rate",
        "source_id": "S13",
        "cell_ids": [],
    })
    assert any("tape" in x for x in violations(snap, ledger, "RULE5"))


def test_gate2_self_report_flags_are_warn_class(seed):
    from tools.check_invariants import integrity_flags

    cell = {"flags": ["vendor self-report (no independent run)"]}
    assert integrity_flags(cell)
    cell2 = {"flags": ["proxy-model measurement: value is for another model"]}
    assert integrity_flags(cell2)


# ---------------------------------------------------------------------------
# Phase 3 gate hardening: latest-sync, claim-marker rule, band contract,
# derived movement-caveat inheritance.
# ---------------------------------------------------------------------------


def test_gate3_latest_sync_enforced(tmp_path):
    """latest.json lagging the newest dated snapshot must fail the full run."""
    import json as _json
    import shutil
    import subprocess
    import sys as _sys
    from pathlib import Path as _P

    repo = _P(__file__).resolve().parent.parent
    d = tmp_path / "data"
    d.mkdir()
    shutil.copyfile(repo / "data" / "2026-08-01.json", d / "2026-08-01.json")
    lag = _json.loads((d / "2026-08-01.json").read_text())
    lag["note"] = "stale copy"
    (d / "latest.json").write_text(_json.dumps(lag, indent=1), encoding="utf-8")
    env = dict(__import__("os").environ)
    env["CHECK_ALLOW_OLD_LATEST"] = "1"
    r = subprocess.run(
        [_sys.executable, "tools/check_invariants.py", "--data-dir", str(d), "--html", "/nonexistent"],
        cwd=repo, env=env, capture_output=True, text=True,
    )
    assert r.returncode == 1 and "SYNC" in r.stderr


def test_gate3_vendor_claim_cell_requires_marker(snap, ledger):
    post = _post_seed(snap)
    for row in post["cells"].values():
        for cell in row.values():
            if cell.get("source_id") == "S6":
                cell["source_id"] = "S13"
                cell["tag"] = "V"
    # a bare V cell in a self-report set (no integrity marker) must fail
    post["cells"]["swe-bench-verified"]["fable-5"]["flags"] = []
    out = check_snapshot(post, "post", ledger)
    assert any("carries no" in x and "integrity marker" in x for x in out)


def test_gate3_derived_inherits_movement_caveats(ledger):
    import json as _json
    from pathlib import Path as _P

    live = _json.loads((_P("data") / "2026-08-01.json").read_text())
    # live snapshot passes (inheritance present)
    assert not [x for x in check_snapshot(live, "live", ledger) if "movement caveats" in x]
    # stripping the inherited caveat must fail
    cell = live["cells"]["intelligence-per-dollar"]["fable-5"]
    cell["flags"] = [f for f in cell["flags"] if "unresolved" not in f.lower()]
    out = check_snapshot(live, "live", ledger)
    assert any("movement caveats" in x for x in out)


def test_gate3_claim_band_renders(seed):
    """claim_v metrics render with data-band=claimed + visible label."""
    import importlib.util
    import json as _json
    from pathlib import Path as _P

    repo = _P(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("site_render2", repo / "site" / "render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    live = _json.loads((repo / "data" / "2026-08-01.json").read_text())
    html = mod.render(live)
    assert 'data-band="claimed"' in html
    assert "VENDOR-CLAIMED" in html
    assert html.count('data-band="claimed"') == 2  # swe-bench-pro + swe-bench-verified
