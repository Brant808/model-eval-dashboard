#!/usr/bin/env python3
"""Pipeline fetch entry point (`make fetch`).

Modes:
- default (offline): materialize `data/latest.json` from the newest dated
  snapshot — byte-identical copy, no network. Keeps local `make all`
  deterministic and test-friendly.
- COLLECT=1: the real daily pipeline — run every collector, merge normalized
  cells into a new dated snapshot with honest degradation (per-source failure
  -> last-good + stale + "source down" flag; per-cell absence -> reasoned
  empty), apply curated overrides, generate mechanical tape + changelog
  (explainability-complete by construction), refresh the watch list, then
  materialize latest.json.

Chaos-drill hooks (Phase 7 gate): FAIL_SOURCES="S2,S4" forces those collectors
to fail; OFFLINE=1 fails them all. PIPELINE_DATE / PIPELINE_NOW pin the clock
for reproducible runs (CI passes real values; tests pin).

latest.json is a copy, not a symlink (CI/Pages friendliness).
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = Path(os.environ["PIPELINE_DATA_DIR"]) if os.environ.get("PIPELINE_DATA_DIR") else REPO / "data"
sys.path.insert(0, str(REPO))

from collectors import registry  # noqa: E402
from collectors.base import FetchFailure, ParseFailure  # noqa: E402
from collectors.model_map import MODELS  # noqa: E402
from tools.check_invariants import (  # noqa: E402
    integrity_flags,
    load_json_strict,
    parse_iso,
)
from tools.make_changelog import diff_entries  # noqa: E402

DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(\.seed)?\.json$")

SOURCE_DOWN_FLAG = "source down (last-good shown)"


def newest_dated_snapshot() -> Path:
    candidates = sorted(p for p in DATA.glob("*.json") if DATED_RE.match(p.name))
    if not candidates:
        print("fetch: no dated snapshots in data/", file=sys.stderr)
        sys.exit(1)
    return candidates[-1]


def materialize_latest() -> Path:
    src = newest_dated_snapshot()
    dst = DATA / "latest.json"
    shutil.copyfile(src, dst)
    print(f"fetch: materialized {dst} from {src.name}")
    return dst


def all_collectors(now):
    from collectors.aa import AACollector
    from collectors.arc import ArcCollector
    from collectors.arena import ArenaCollector
    from collectors.llmstats import LlmStatsCollector
    from collectors.metr import MetrCollector
    from collectors.openrouter import OpenRouterCollector
    from collectors.newrows import (
        EpochCollector,
        LiveBenchCollector,
        SweRebenchCollector,
        ValsCollector,
    )
    from collectors.tbench import TbenchCollector

    return [
        AACollector(now=now),
        ArenaCollector(now=now),
        OpenRouterCollector(now=now),
        ArcCollector(now=now),
        MetrCollector(now=now),
        LlmStatsCollector(now=now),
        TbenchCollector(now=now),
        EpochCollector(now=now),
        LiveBenchCollector(now=now),
        SweRebenchCollector(now=now),
        ValsCollector(now=now),
    ]


def cell_from_value(cv, meta) -> dict:
    cell = {
        "value": cv.value,
        "unit": cv.unit,
        "tag": cv.tag,
        "source_id": cv.source_id,
        "retrieved_at": cv.retrieved_at,
        "flags": list(cv.flags),
        "comparability_set": cv.comparability_set,
        "stale": False,
        "history_ref": f"{cv.metric_id}.{cv.model_id}",
    }
    if cv.effort_tier is not None:
        cell["effort_tier"] = cv.effort_tier
    if cv.derived_from:
        cell["derived_from"] = list(cv.derived_from)
    if cv.value_disclaimed:
        cell["value_disclaimed"] = True
    return cell


def empty_cell(metric_id, model_id, meta, reason, flags=None) -> dict:
    return {
        "value": None,
        "unit": meta["unit"],
        "tag": None,
        "source_id": None,
        "retrieved_at": None,
        "flags": list(flags or []),
        "comparability_set": meta["comparability_set"],
        "stale": False,
        "empty_reason": reason,
        "history_ref": f"{metric_id}.{model_id}",
    }


def recompute_stale(cell, meta, now):
    if cell.get("value") is None or not cell.get("retrieved_at"):
        return
    age = now - parse_iso(cell["retrieved_at"])
    cell["stale"] = age > timedelta(hours=meta["freshness_sla_hours"])


def pick_default_trio(cells, models):
    """ORDERING.md D3, rule T2: top model per vendor, top-3 vendors by their
    best model's AA index, slots ordered by AA index."""
    best_per_vendor = {}
    for model_id, cell in cells.get("aa-index", {}).items():
        v = cell.get("value")
        if not isinstance(v, (int, float)):
            continue
        vendor = models[model_id]["vendor"]
        if vendor not in best_per_vendor or v > best_per_vendor[vendor][1]:
            best_per_vendor[vendor] = (model_id, v)
    ranked = sorted(best_per_vendor.values(), key=lambda t: -t[1])
    return [m for m, _ in ranked[:3]]


def mechanical_tape(prev, cells, date_str, metrics):
    """Loud, uneditorialized tape: one entry per source-group of changed cells,
    plus per-cell changelog entries handled by diff_entries downstream."""
    entries = []
    prev_cells = prev.get("cells", {})
    by_source = {}
    for metric_id, row in cells.items():
        for model_id, cell in row.items():
            old = prev_cells.get(metric_id, {}).get(model_id, {})
            if old.get("value") == cell.get("value"):
                continue
            sid = cell.get("source_id") or old.get("source_id")
            if not sid:
                continue
            by_source.setdefault(sid, []).append(
                (f"{metric_id}.{model_id}",
                 f"{metrics[metric_id]['name']} [{MODELS[model_id]['name']}]: "
                 f"{old.get('value')!r} -> {cell.get('value')!r}")
            )
    for sid in sorted(by_source):
        moved = by_source[sid]
        ids = [cid for cid, _ in moved]
        text = "Mechanical tape (no editorial layer): " + "; ".join(t for _, t in moved[:6])
        if len(moved) > 6:
            text += f"; +{len(moved) - 6} more (see changelog)"
        entries.append({"date": date_str, "text": text, "source_id": sid, "cell_ids": ids})
    return entries


def collect(date_str: str, now: datetime) -> Path:
    prev_path = newest_dated_snapshot()
    prev = load_json_strict(prev_path)
    fail_sources = set(filter(None, os.environ.get("FAIL_SOURCES", "").split(",")))
    offline = os.environ.get("OFFLINE") == "1"

    observed = {}  # (metric_id, model_id) -> CellValue
    health = {}
    for collector in all_collectors(now):
        sid = collector.source_id
        try:
            if offline or sid in fail_sources:
                raise FetchFailure(f"{sid}: simulated failure (chaos drill)")
            for cv in collector.collect(date_str):
                observed[(cv.metric_id, cv.model_id)] = cv
            health[sid] = f"ok (fetched {now.strftime('%Y-%m-%dT%H:%M:%SZ')})"
        except (FetchFailure, ParseFailure) as e:
            health[sid] = f"DOWN: {type(e).__name__}: {e}"
            print(f"fetch: {sid} degraded — {e}", file=sys.stderr)

    # Curated overrides (their own provenance; e.g. METR Sol blog cell S18,
    # disclosure-watch S21). Never overwritten by collectors.
    overrides_path = DATA / "overrides.json"
    overrides = load_json_strict(overrides_path) if overrides_path.exists() else {"cells": {}}

    models = dict(MODELS)
    metrics_meta = {}
    cells = {}
    for metric_id, meta in registry.METRICS.items():
        m = {
            "name": meta["name"],
            "group": meta["group"],
            "unit": meta["unit"],
            "comparability_set": meta["comparability_set"],
            "direction": meta["direction"],
            "freshness_sla_hours": meta["freshness_sla_hours"],
            "primary_source_id": meta["primary_source_id"],
        }
        for opt in ("chip_eligible", "brief_layer", "claim_v"):
            if opt in meta:
                m[opt] = meta[opt]
        metrics_meta[metric_id] = m

        row = {}
        for model_id in models:
            ov = overrides.get("cells", {}).get(metric_id, {}).get(model_id)
            if ov is not None:
                cell = json.loads(json.dumps(ov))  # deep copy
            elif (metric_id, model_id) in observed:
                cell = cell_from_value(observed[(metric_id, model_id)], meta)
            else:
                prev_cell = prev.get("cells", {}).get(metric_id, {}).get(model_id)
                if prev_cell and prev_cell.get("value") is not None:
                    # Decide by the CELL's own source, not the metric's primary:
                    # a row can mix sources (e.g. SWE-Pro aggregate S13 + a
                    # vendor launch claim S14).
                    cell_src = prev_cell.get("source_id")
                    if cell_src not in health:
                        # No collector for this source (vendor pages, curated
                        # blog cells): event-driven — carry forward unchanged.
                        cell = json.loads(json.dumps(prev_cell))
                    elif health[cell_src].startswith("DOWN"):
                        cell = json.loads(json.dumps(prev_cell))
                        if SOURCE_DOWN_FLAG not in cell["flags"]:
                            cell["flags"] = list(cell["flags"]) + [SOURCE_DOWN_FLAG]
                    else:
                        # Source fetched fine but this cell vanished from it:
                        # honest empty; diff_entries records the removal.
                        cell = empty_cell(metric_id, model_id, meta,
                                          meta["empty_default"],
                                          ["value no longer published by source"])
                else:
                    reason = meta["empty_default"]
                    if prev_cell and prev_cell.get("value") is None:
                        reason = prev_cell.get("empty_reason", reason)
                    cell = empty_cell(metric_id, model_id, meta, reason, [])
            recompute_stale(cell, meta, now)
            row[model_id] = cell
        cells[metric_id] = row

    snap = {
        "schema_version": 1,
        "kind": "collected",
        "snapshot_date": date_str,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Collected snapshot (mechanical pipeline).",
        "models": models,
        "metrics": metrics_meta,
        "cells": cells,
        "tape": [],
        "watch": prev.get("watch", []),
        "changelog": [],
        "notes": [],
        "implications": prev.get("implications", []),
        "health": {
            "run_status": "collected" + (" (degraded)" if any(v.startswith("DOWN") for v in health.values()) else ""),
            "judgment_layer": "off (mechanical)",
            "sources": dict(sorted(health.items())),
        },
        "default_trio": pick_default_trio(cells, models),
    }

    snap["tape"] = mechanical_tape(prev, cells, date_str, metrics_meta)
    # Explainability: everything the tape didn't cover goes to the changelog.
    snap["changelog"] = diff_entries(prev, snap)

    out = DATA / f"{date_str}.json"
    out.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"fetch: wrote {out} "
          f"({sum(1 for v in health.values() if not v.startswith('DOWN'))}/{len(health)} sources ok)")
    return out


def main():
    if os.environ.get("COLLECT") == "1":
        date_str = os.environ.get("PIPELINE_DATE") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now_env = os.environ.get("PIPELINE_NOW")
        now = parse_iso(now_env) if now_env else datetime.now(timezone.utc)
        collect(date_str, now)
    materialize_latest()


if __name__ == "__main__":
    main()
