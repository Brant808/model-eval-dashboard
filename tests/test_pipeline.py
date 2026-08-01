"""Chaos drills as repeatable tests (brief Phase 7 gate): the pipeline must
degrade loudly, never silently. All runs are offline (OFFLINE/FAIL_SOURCES
simulate outages; no network in tests) in a temp data dir."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def run_pipeline(tmp_path, date, now, env_extra):
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    for f in ("2026-08-01.json", "overrides.json"):
        shutil.copyfile(REPO / "data" / f, data_dir / f)
    env = dict(os.environ)
    env.update({
        "PIPELINE_DATA_DIR": str(data_dir),
        "COLLECT": "1",
        "PIPELINE_DATE": date,
        "PIPELINE_NOW": now,
        **env_extra,
    })
    r = subprocess.run(
        [sys.executable, "-m", "collectors.run"],
        cwd=REPO, env=env, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    return json.loads((data_dir / f"{date}.json").read_text()), data_dir, r


def lint(data_dir):
    env = dict(os.environ)
    env["CHECK_ALLOW_OLD_LATEST"] = "1"
    r = subprocess.run(
        [sys.executable, "tools/check_invariants.py", "--data-dir", str(data_dir),
         "--html", "/nonexistent"],
        cwd=REPO, env=env, capture_output=True, text=True,
    )
    return r


def test_drill_total_network_loss_degrades_loudly(tmp_path):
    snap, data_dir, r = run_pipeline(
        tmp_path, "2026-08-02", "2026-08-02T09:00:00Z", {"OFFLINE": "1"}
    )
    assert "(degraded)" in snap["health"]["run_status"]
    assert all(v.startswith("DOWN") for v in snap["health"]["sources"].values())
    # last-good carried with the loud flag, values intact
    cell = snap["cells"]["aa-index"]["fable-5"]
    assert cell["value"] == 59.86
    assert "source down (last-good shown)" in cell["flags"]
    # the degraded snapshot still satisfies the constitution
    out = lint(data_dir)
    assert out.returncode == 0, out.stderr


def test_drill_single_source_failure_isolated(tmp_path):
    """THE drill from the brief: one source down while the rest succeed.
    Exercises the real fresh+carried merge path in collect() — the other ten
    collectors parse their recorded fixtures via COLLECTOR_FIXTURES_DIR (this
    drill was dead code before that hook existed: `if False` shipped)."""
    snap, data_dir, r = run_pipeline(
        tmp_path, "2026-08-02", "2026-08-02T09:00:00Z",
        {"FAIL_SOURCES": "S2",
         "COLLECTOR_FIXTURES_DIR": str(REPO / "collectors" / "fixtures")},
    )
    # the failed source is named, the rest are healthy
    assert snap["health"]["sources"]["S2"].startswith("DOWN")
    assert "simulated failure" in snap["health"]["sources"]["S2"]
    assert snap["health"]["sources"]["S1"].startswith("ok")
    assert "(degraded)" in snap["health"]["run_status"]
    # S2 cells: last-good carried with the loud flag
    arena = snap["cells"]["arena-elo"]["fable-5"]
    assert arena["value"] == 1507.6
    assert "source down (last-good shown)" in arena["flags"]
    # S1 cells: genuinely fresh (re-stamped at this run's fetch time)
    aa = snap["cells"]["aa-index"]["fable-5"]
    assert aa["value"] == 59.86
    assert aa["retrieved_at"].startswith("2026-08-02")
    assert "source down (last-good shown)" not in aa["flags"]
    # the merged snapshot still satisfies the constitution
    out = lint(data_dir)
    assert out.returncode == 0, out.stderr


def test_drill_same_day_rerun_diffs_against_yesterday(tmp_path):
    """Cron then manual dispatch on the same day: the second run must diff
    against YESTERDAY, not against its own first run (which wiped the
    tape/changelog and failed explainability — phase-7 gate, demonstrated)."""
    env = {"FAIL_SOURCES": "",
           "COLLECTOR_FIXTURES_DIR": str(REPO / "collectors" / "fixtures")}
    snap1, data_dir, _ = run_pipeline(tmp_path, "2026-08-02", "2026-08-02T09:00:00Z", env)
    snap2, _, _ = run_pipeline(tmp_path, "2026-08-02", "2026-08-02T20:00:00Z", env)
    assert snap1["cells"].keys() == snap2["cells"].keys()
    # identical inputs -> identical explanation set, not an empty one
    assert {e["note"] for e in snap2["changelog"]} == {e["note"] for e in snap1["changelog"]}
    assert lint(data_dir).returncode == 0


def test_drill_implication_rot_flips_to_under_review(tmp_path):
    """A cited cell moving at the SOURCE must flip the carried implication to
    the visible 'under review' state (gate BLOCKING: refuted 'confidence
    high' claims shipped gate-green forever in mechanical mode). The drill
    refits AA inside a modified fixture — the honest end-to-end path."""
    import gzip
    import re as _re

    fx = tmp_path / "fixtures"
    shutil.copytree(REPO / "collectors" / "fixtures", fx)
    html = gzip.decompress((fx / "aa_models.html.gz").read_bytes()).decode()
    # the payload stores full precision (60.6918…); hit every Opus variant's
    # index field so best-variant selection can't restore the old rounding
    # the parser reads `intelligenceIndex` inside the initialModels flight
    # region; the value appears escaped and unescaped — cover both forms,
    # every Opus variant, without touching artificialAnalysisIntelligenceIndex
    refit, n = _re.subn(
        r'((?<![A-Za-z])intelligenceIndex\\?":)60\.6\d+', r"\g<1>59.0091", html
    )
    assert n >= 1, "AA fixture no longer contains the opus index value"
    (fx / "aa_models.html.gz").write_bytes(gzip.compress(refit.encode()))

    snap2, data_dir, _ = run_pipeline(
        tmp_path, "2026-08-02", "2026-08-02T09:00:00Z",
        {"COLLECTOR_FIXTURES_DIR": str(fx), "FAIL_SOURCES": ""},
    )
    assert snap2["cells"]["aa-index"]["opus-5"]["value"] == 59.01
    imp = next(i for i in snap2["implications"] if i["id"] == "imp-race-judged")
    assert imp["status"] == "under review"
    assert "aa-index.opus-5" in imp["moved_cites"]
    # linter accepts the flagged state but rejects the same drift unflagged
    assert lint(data_dir).returncode == 0
    imp["status"] = "answered"
    (data_dir / "2026-08-02.json").write_text(json.dumps(snap2))
    shutil.copyfile(data_dir / "2026-08-02.json", data_dir / "latest.json")
    out = lint(data_dir)
    assert out.returncode == 1
    assert "not 'under review'" in out.stderr


def test_drill_clock_advance_forces_staleness(tmp_path):
    """Advance the clock past every SLA: carried values MUST badge stale."""
    snap, data_dir, r = run_pipeline(
        tmp_path, "2026-08-20", "2026-08-20T09:00:00Z", {"OFFLINE": "1"}
    )
    cell = snap["cells"]["aa-index"]["fable-5"]  # 72h SLA, retrieved 08-01
    assert cell["stale"] is True
    assert cell["value"] == 59.86  # stale never silently blanks
    out = lint(data_dir)
    assert out.returncode == 0, out.stderr  # stale marked = constitutional


def test_drill_second_run_is_stable_and_explained(tmp_path):
    """Run twice on the same inputs: second snapshot must equal the first
    except self-referential fields, and produce zero unexplained deltas."""
    snap1, data_dir, _ = run_pipeline(
        tmp_path, "2026-08-02", "2026-08-02T09:00:00Z", {"OFFLINE": "1"}
    )
    env = dict(os.environ)
    env.update({
        "PIPELINE_DATA_DIR": str(data_dir), "COLLECT": "1", "OFFLINE": "1",
        "PIPELINE_DATE": "2026-08-03", "PIPELINE_NOW": "2026-08-03T09:00:00Z",
    })
    r = subprocess.run([sys.executable, "-m", "collectors.run"], cwd=REPO, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    snap2 = json.loads((data_dir / "2026-08-03.json").read_text())
    assert {m: {k: c["value"] for k, c in row.items()} for m, row in snap1["cells"].items()} == \
           {m: {k: c["value"] for k, c in row.items()} for m, row in snap2["cells"].items()}
    # nothing moved -> no NEW mechanical entries for this date; prior entries
    # still inside the 72h window carry forward (the tape header promises
    # ~72h of movement, not since-yesterday — phase-7 gate rider)
    assert not any(e["date"] == "2026-08-03" for e in snap2["tape"])
    assert all(e in snap1["tape"] for e in snap2["tape"])
    out = lint(data_dir)
    assert out.returncode == 0, out.stderr


def test_drill_malformed_source_fails_loud_not_wrong():
    """A source that returns garbage must raise ParseFailure (handled as
    source-down by the runner), never emit a guessed number."""
    from datetime import datetime, timezone

    from collectors.arc import ArcCollector
    from collectors.base import ParseFailure

    with pytest.raises(ParseFailure):
        ArcCollector(now=datetime(2026, 8, 2, tzinfo=timezone.utc)).parse(
            b'{"unexpected": "redesign"}'
        )
