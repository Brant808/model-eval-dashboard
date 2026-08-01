"""Judgment-layer validator tests (Phase 7). The layer itself is optional and
off by default; what MUST hold is that when it runs, nothing un-grounded can
get through. These tests attack the validator directly with a synthetic
snapshot — no CLI, no network."""

import hashlib

from tools.judgment import LOCKED_MATERIAL, PROMPT_SHA256, validate_entry

SNAP = {
    "snapshot_date": "2026-08-01",
    "metrics": {
        "aa-index": {"name": "AA Intelligence Index"},
        "swe-bench-pro": {"name": "SWE-bench Pro (claimed)"},
        "swe-rebench": {"name": "SWE-rebench"},
    },
    "models": {"fable-5": {"name": "Fable 5"}, "opus-5": {"name": "Opus 5"}},
    "cells": {
        "aa-index": {
            "fable-5": {"value": 59.86, "source_id": "S1", "flags": [],
                        "unit": "index", "comparability_set": "aa-index-4-0",
                        "retrieved_at": "2026-08-01T09:00:00Z"},
            "opus-5": {"value": 60.69, "source_id": "S1", "flags": [],
                       "unit": "index", "comparability_set": "aa-index-4-0",
                       "retrieved_at": "2026-08-01T09:00:00Z"},
        },
        "swe-bench-pro": {
            "fable-5": {"value": 80.0, "source_id": "S13",
                        "flags": ["aggregated vendor self-reports (0 of 43 verified)"],
                        "unit": "%", "comparability_set": "swe-bench-pro-claims",
                        "retrieved_at": "2026-08-01T09:00:00Z"},
        },
        "swe-rebench": {
            "fable-5": {"value": 64.5, "source_id": "S20", "flags": [],
                        "unit": "%", "comparability_set": "swe-rebench-window-2026-05-15",
                        "retrieved_at": "2026-08-01T09:00:00Z"},
        },
    },
}
PREV = {"aa-index": {"fable-5": {"value": 59.2}}}


def tape(**kw):
    base = {"date": "2026-08-01", "text": "AA Intelligence Index [Fable 5]: 59.86",
            "source_id": "S1", "cell_ids": ["aa-index.fable-5"]}
    base.update(kw)
    return base


def imp(**kw):
    base = {"id": "IMP-9", "tag": "X", "text": "Fable 5 leads on the AA index at 59.86.",
            "cites": ["aa-index.fable-5"], "confidence": "med",
            "falsifier": "A rescore drops Fable 5 below Opus 5 on S1.",
            "flags_carried": []}
    base.update(kw)
    return base


def test_prompt_pin_matches_source():
    # the pin covers prompt + model + max_tokens (transport tamper-evidence)
    assert hashlib.sha256(LOCKED_MATERIAL.encode()).hexdigest() == PROMPT_SHA256


def test_negative_cell_value_matches_unsigned_text():
    snap = {"snapshot_date": "2026-08-01",
            "metrics": {"aa-halluc": {"name": "AA Hallucination"}},
            "models": {"ds-v4-pro": {"name": "DeepSeek V4 Pro"}},
            "cells": {"aa-halluc": {"ds-v4-pro": {
                "value": -10.02, "source_id": "S1", "flags": [], "unit": "index",
                "comparability_set": "aa-halluc", "retrieved_at": "2026-08-01T09:00:00Z"}}}}
    e = {"date": "2026-08-01", "text": "DeepSeek V4 Pro sits at 10.02 below zero",
         "source_id": "S1", "cell_ids": ["aa-halluc.ds-v4-pro"]}
    assert validate_entry(e, "tape", snap, {}) is None


def test_grounded_tape_entry_accepted():
    assert validate_entry(tape(), "tape", SNAP, PREV) is None


def test_delta_and_model_name_digits_allowed():
    e = tape(text="Fable 5 moved 0.66 to 59.86 on the AA Intelligence Index")
    assert validate_entry(e, "tape", SNAP, PREV) is None


def test_invented_number_rejected():
    e = tape(text="Fable 5 hits 61.2 on the AA index")
    assert "no-new-facts" in validate_entry(e, "tape", SNAP, PREV)


def test_missing_or_empty_cite_rejected():
    e = tape(cell_ids=["aa-index.kimi-k3"])
    assert "missing or empty" in validate_entry(e, "tape", SNAP, PREV)


def test_foreign_source_id_rejected():
    e = tape(source_id="S13")
    assert "not among cited" in validate_entry(e, "tape", SNAP, PREV)


def test_rule5_family_mixing_rejected():
    e = imp(cites=["swe-bench-pro.fable-5", "swe-rebench.fable-5"],
            text="Fable 5 agrees across SWE boards",
            flags_carried=["aggregated vendor self-reports (0 of 43 verified)"])
    assert "rule 5" in validate_entry(e, "implication", SNAP, PREV)


def test_rule7_integrity_flag_must_be_carried_verbatim():
    e = imp(cites=["swe-bench-pro.fable-5"], text="Fable 5 claims 80 on Pro.")
    assert "rule 7" in validate_entry(e, "implication", SNAP, PREV)
    e = imp(cites=["swe-bench-pro.fable-5"], text="Fable 5 claims 80 on Pro.",
            flags_carried=["aggregated vendor self-reports (0 of 43 verified)"])
    assert validate_entry(e, "implication", SNAP, PREV) is None


def test_fabricated_falsifier_number_rejected():
    e = imp(falsifier="reverses if Fable 5 drops below 87.3 on the AA Intelligence Index")
    assert "falsifier number" in validate_entry(e, "implication", SNAP, PREV)


def test_fabricated_carried_flag_rejected():
    e = imp(flags_carried=["record gaming: fabricated accusation against Fable 5"])
    assert "absent from cited cells" in validate_entry(e, "implication", SNAP, PREV)


def test_source_id_citations_are_not_numbers():
    e = tape(text="AA Intelligence Index [Fable 5]: 59.86 per source S1")
    assert validate_entry(e, "tape", SNAP, PREV) is None


def test_implication_hygiene_fields():
    assert "tag" in validate_entry(imp(tag="editorial"), "implication", SNAP, PREV)
    assert "confidence" in validate_entry(imp(confidence="certain"), "implication", SNAP, PREV)
    assert "falsifier" in validate_entry(imp(falsifier="  "), "implication", SNAP, PREV)
