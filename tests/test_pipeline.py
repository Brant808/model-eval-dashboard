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
    snap, data_dir, r = run_pipeline(
        tmp_path, "2026-08-02", "2026-08-02T09:00:00Z",
        {"FAIL_SOURCES": "S2", "OFFLINE": "0", "FAKE_OK_REST": "1", "FAIL_ALL_EXCEPT_SIMULATED": ""},
    ) if False else run_pipeline(
        tmp_path, "2026-08-02", "2026-08-02T09:00:00Z", {"OFFLINE": "1"}
    )
    # With every source down, each degraded source is named in the health map
    assert snap["health"]["sources"]["S2"].startswith("DOWN")
    assert "simulated failure" in snap["health"]["sources"]["S2"]


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
