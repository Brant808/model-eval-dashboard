"""Recorded-fixture tests for every collector (brief Phase 7 standard):
parse real captured responses offline, assert exact values, and prove that
malformed/shape-shifted input fails LOUD (raises), never emits a guess."""

import gzip
from datetime import datetime, timezone
from pathlib import Path

import pytest

from collectors.aa import AACollector
from collectors.arc import ArcCollector
from collectors.arena import ArenaCollector
from collectors.base import ParseFailure
from collectors.llmstats import LlmStatsCollector
from collectors.metr import MetrCollector
from collectors.openrouter import OpenRouterCollector
from collectors.tbench import TbenchCollector

FIX = Path(__file__).resolve().parent.parent / "collectors" / "fixtures"
NOW = datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc)


def load(name):
    p = FIX / name
    if name.endswith(".gz"):
        return gzip.decompress(p.read_bytes())
    return p.read_bytes()


def by_key(cells):
    return {(c.metric_id, c.model_id): c for c in cells}


# --- Artificial Analysis -----------------------------------------------------

def test_aa_parses_all_metric_families():
    cells = AACollector(now=NOW).parse(load("aa_models.html.gz"))
    d = by_key(cells)
    assert d[("aa-index", "opus-5")].value == 60.69
    assert d[("aa-index", "fable-5")].value == 59.86
    assert d[("gdpval-aa", "opus-5")].value == 1857.8
    assert d[("gdpval-aa", "ds-v4-pro")].value == 1304.49
    assert d[("cost-per-task", "fable-5")].value == 3.15
    assert d[("aa-omniscience", "fable-5")].value == 40.15
    assert d[("aa-halluc-rate", "gpt-5-6-sol")].value == 88.8
    assert d[("aa-agentic-index", "fable-5")].value == 52.81
    assert d[("context-window", "kimi-k3")].value == 1048576
    # derived row: value + parent citation flags
    ipd = d[("intelligence-per-dollar", "ds-v4-pro")]
    assert ipd.value > 100  # DeepSeek's cheap-token lane dominates this ratio
    assert any(f.startswith("derived:") for f in ipd.flags)
    assert any("parents: aa-index.ds-v4-pro" in f for f in ipd.flags)
    # provenance discipline
    assert d[("gdpval-aa", "fable-5")].tag == "I"
    assert "Gemini-graded (AA judge panel)" in d[("gdpval-aa", "fable-5")].flags
    assert d[("api-price", "fable-5")].tag == "V"


def test_aa_shape_change_fails_loud():
    with pytest.raises(ParseFailure):
        AACollector(now=NOW).parse(b"<html>redesigned page, no flight payload</html>")


# --- ARC Prize ----------------------------------------------------------------

def test_arc_best_tier_per_model():
    cells = ArcCollector(now=NOW).parse(load("arc_v3.json"))
    d = by_key(cells)
    opus = d[("arc-agi-3", "opus-5")]
    assert opus.value == 30.16 and opus.effort_tier == "High"
    sol = d[("arc-agi-3", "gpt-5-6-sol")]
    assert sol.value == 7.78 and sol.effort_tier == "Max"
    assert ("arc-agi-3", "fable-5") not in d  # absent from verified board -> honest empty
    assert all(c.effort_tier for c in cells)  # rule 6 at the source


def test_arc_malformed_fails_loud():
    with pytest.raises(ParseFailure):
        ArcCollector(now=NOW).parse(b'{"version":"v3","evaluations":[]}')
    with pytest.raises(ParseFailure):
        ArcCollector(now=NOW).parse(
            b'{"evaluations":[{"modelId":"anthropic-claude-opus-5-high","score":"NaNish"}]}'
        )


# --- METR ----------------------------------------------------------------------

def test_metr_parses_mythos_preview_as_fable_base():
    cells = MetrCollector(now=NOW).parse(load("metr_1_1.yaml"))
    d = by_key(cells)
    fable = d[("metr-horizon", "fable-5")]
    assert fable.value == 17.4
    assert any("Mythos Preview" in f for f in fable.flags)
    assert any("CI 8.5–55.1h" in f for f in fable.flags)
    assert any("unreliable" in f for f in fable.flags)


def test_metr_wrong_suite_or_shape_fails_loud():
    with pytest.raises(ParseFailure):
        MetrCollector(now=NOW).parse(b"just: a\nrandom: yaml\n")


# --- Arena ----------------------------------------------------------------------

def test_arena_highest_variant_per_family():
    cells = ArenaCollector(now=NOW).parse(load("arena_hf_filter.json"))
    d = by_key(cells)
    assert d[("arena-elo", "fable-5")].value == 1507.6
    assert d[("arena-elo", "opus-5")].value == 1494.6  # max variant beats high
    assert any("variant: claude-opus-5-max" in f for f in d[("arena-elo", "opus-5")].flags)
    assert d[("arena-elo", "kimi-k3")].value == 1485.8
    for c in cells:
        assert "private variant testing active (Arena)" in c.flags
        assert c.comparability_set == "arena-text-style-control"


def test_arena_shape_change_fails_loud():
    with pytest.raises(ParseFailure):
        ArenaCollector(now=NOW).parse(b'{"rows": []}')


# --- OpenRouter -------------------------------------------------------------------

def test_openrouter_last_complete_week_shares():
    cells = OpenRouterCollector(now=NOW).parse(load("openrouter_market_share.json"))
    d = by_key(cells)
    assert d[("openrouter-share", "ds-v4-pro")].value == 17.4
    assert d[("openrouter-share", "fable-5")].value == 9.1
    assert d[("openrouter-share", "opus-5")].value == 9.1  # provider-level on both
    assert d[("openrouter-share", "gpt-5-6-sol")].value == 6.9
    assert ("openrouter-share", "kimi-k3") not in d  # below top-N -> honest empty
    for c in cells:
        assert any("unit per page copy ambiguous" in f for f in c.flags)


def test_openrouter_shape_change_fails_loud():
    with pytest.raises(ParseFailure):
        OpenRouterCollector(now=NOW).parse(b'{"data": [{"x": "w", "ys": {}}]}')


# --- llm-stats ----------------------------------------------------------------------

def test_llmstats_vendor_claims():
    cells = LlmStatsCollector(now=NOW).parse(load("llmstats_swe_pro.html.gz"))
    d = by_key(cells)
    assert d[("swe-bench-pro", "fable-5")].value == 80.0
    assert d[("swe-bench-pro", "gpt-5-6-sol")].value == 64.6
    assert d[("swe-bench-pro", "ds-v4-pro")].value == 55.4
    assert ("swe-bench-pro", "opus-5") not in d  # launch claim not on the aggregate
    for c in cells:
        assert c.tag == "V"
        assert "aggregated vendor self-reports (0 of 43 verified)" in c.flags


def test_llmstats_shape_change_fails_loud():
    with pytest.raises(ParseFailure):
        LlmStatsCollector(now=NOW).parse(b"<html>nope</html>")


# --- Terminal-Bench ------------------------------------------------------------------

def test_tbench_best_displayed_row_per_model():
    cells = TbenchCollector(now=NOW).parse(load("tbench_21.html.gz"))
    d = by_key(cells)
    fable = d[("terminal-bench", "fable-5")]
    assert fable.value == 83.8
    assert any("Claude Code" in f and "xhigh" in f for f in fable.flags)
    assert "self-run by vendor, log-audited by maintainers" in fable.flags
    assert ("terminal-bench", "gpt-5-6-sol") not in d  # repo-only row is not displayed


def test_tbench_shape_change_fails_loud():
    with pytest.raises(ParseFailure):
        TbenchCollector(now=NOW).parse(b"<html>redesign</html>")
