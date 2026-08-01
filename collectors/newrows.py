"""Collectors for the Phase 2 additions: Epoch ECI (S10), LiveBench (S12),
SWE-rebench (S20), Vals Index (S11). Extraction specs pinned by the Phase 2/3
gate verifiers (governance/SOURCES.md entries)."""

from __future__ import annotations

import csv
import html as html_lib
import io
import json
import re
from datetime import datetime, timedelta, timezone

from .base import (CellValue, Collector, ParseFailure, balanced_json_array,
                   decode_flight_region, flight_text)

ECI_CAV = "mixed-provenance composite (incl. OpenAI-funded FrontierMath)"
VALS_CAV = "VC-funded evaluator, no on-site funding disclosure"

ECI_NAMES = {
    "Claude Fable 5": "fable-5",
    "Claude Opus 5": "opus-5",
    "GPT-5.6 Sol": "gpt-5-6-sol",
    "Kimi K3": "kimi-k3",
    "DeepSeek-V4-Pro": "ds-v4-pro",
}

LIVEBENCH_IDS = {
    "claude-fable-5-max-effort": "fable-5",
    "claude-opus-5-max-effort": "opus-5",
    "gpt-5.6-sol-max": "gpt-5-6-sol",
    "kimi-k3": "kimi-k3",
    "deepseek-v4-pro": "ds-v4-pro",
}

REBENCH_NAMES = {
    "Fable 5": "fable-5",
    "Opus 5": "opus-5",
    "GPT-5.6 Sol": "gpt-5-6-sol",
    "Kimi K3": "kimi-k3",
    "DeepSeek-V4 Pro": "ds-v4-pro",
}

VALS_KEYS = {
    "anthropic/claude-fable-5": "fable-5",
    "anthropic/claude-opus-5": "opus-5",
    "openai/gpt-5.6-sol": "gpt-5-6-sol",
    "kimi/kimi-k3": "kimi-k3",
    "deepseek/deepseek-v4-pro": "ds-v4-pro",
}


class EpochCollector(Collector):
    source_id = "S10"
    name = "epoch-eci"
    url = "https://epoch.ai/data/eci_scores.csv"

    def parse(self, raw: bytes) -> list[CellValue]:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        if not rows or "eci" not in rows[0]:
            raise ParseFailure("epoch eci_scores.csv: schema changed (no eci column)")
        best = {}
        for r in rows:
            model_id = ECI_NAMES.get((r.get("Model") or "").strip())
            if model_id is None:
                continue
            try:
                v = float(r["eci"])
            except (ValueError, TypeError):
                raise ParseFailure(f"epoch: non-numeric eci for {r.get('Model')!r}")
            flags = [ECI_CAV]
            if r.get("eci_ci_low") and r.get("eci_ci_high"):
                flags.append(f"95% CI {r['eci_ci_low']}–{r['eci_ci_high']}")
            # retrieved_at = when WE fetched the living board (staleness tracks
            # our copy of the source, not Epoch's per-model run date). The run
            # date is honest context and rides along as a visible flag.
            scored = (r.get("date") or "")[:10]
            if scored:
                flags.append(f"score dated {scored} (Epoch run date)")
            best[model_id] = CellValue("epoch-eci", model_id, round(v, 2), "index", "I", "S10",
                                       "epoch-eci", self.fetched_at, flags=flags)
        if not best:
            raise ParseFailure("epoch: parsed but no mapped models found")
        return list(best.values())


class LiveBenchCollector(Collector):
    source_id = "S12"
    name = "livebench"
    url = "https://livebench.ai/table_2026_06_25.csv"
    release = "2026-06-25"

    def parse(self, raw: bytes) -> list[CellValue]:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        if not rows:
            raise ParseFailure("livebench csv: empty")
        name_col = next((c for c in rows[0] if c.lower() in ("model", "model_name")), None)
        if name_col is None:
            raise ParseFailure("livebench csv: no model column — schema changed")
        out = []
        for r in rows:
            model_id = LIVEBENCH_IDS.get((r.get(name_col) or "").strip())
            if model_id is None:
                continue
            nums = []
            for c, v in r.items():
                if c == name_col:
                    continue
                try:
                    nums.append(float(v))
                except (ValueError, TypeError):
                    continue
            if not nums:
                raise ParseFailure(f"livebench: no numeric columns for {r.get(name_col)!r}")
            avg = round(sum(nums) / len(nums), 1)
            out.append(CellValue("livebench", model_id, avg, "index", "I", "S12",
                                 f"livebench-{self.release}",
                                 f"{self.release}T00:00:00Z",
                                 flags=[f"global average over {len(nums)} task columns, "
                                        f"release {self.release}"]))
        if not out:
            raise ParseFailure("livebench: parsed but no mapped models found")
        return out


class SweRebenchCollector(Collector):
    source_id = "S20"
    name = "swe-rebench"
    url = "https://swe-rebench.com/"

    def parse(self, raw: bytes) -> list[CellValue]:
        html = raw.decode("utf-8", errors="strict")
        txt = flight_text(html)
        items = balanced_json_array(txt, '"items":')
        if not items:
            raise ParseFailure("swe-rebench: items[] not found — page shape changed")
        # newest non-degenerate window shared across items: pick max `from`
        # among keys where from < to (degenerate X:X buckets are cumulative
        # placeholders, not windows).
        # GLOBAL headline window: latest end, then longest span, across all
        # items — every cell reads at the same window (comparability set).
        all_keys = set()
        for m in items:
            if isinstance(m, dict):
                for k in ((m.get("rangeStats") or {}).get("all") or {}):
                    if ":" in k and int(k.split(":")[0]) < int(k.split(":")[1]):
                        all_keys.add(k)
        if not all_keys:
            raise ParseFailure("swe-rebench: no non-degenerate windows found")
        # headline window: among windows carried by the MAPPED frontier
        # models (>=2 of them), latest end then longest span — old models
        # carry legacy windows and tiny sub-buckets that must not win.
        from collections import Counter

        counts = Counter()
        for m in items:
            if not isinstance(m, dict):
                continue
            name = str(m.get("modelName") or "")
            if not any(name.startswith(label) for label in REBENCH_NAMES):
                continue
            for k in ((m.get("rangeStats") or {}).get("all") or {}):
                if k in all_keys:
                    counts[k] += 1
        shared = [k for k, n in counts.items() if n >= 2]
        if not shared:
            raise ParseFailure("swe-rebench: mapped models share no window")
        key = max(shared, key=lambda k: (int(k.split(":")[1]),
                                         int(k.split(":")[1]) - int(k.split(":")[0])))
        start_ms, _end_ms = (int(x) for x in key.split(":"))
        window_start = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)

        out = []
        for m in items:
            if not isinstance(m, dict):
                continue
            name = str(m.get("modelName") or "")
            model_id = None
            for label, mid in REBENCH_NAMES.items():
                if name.startswith(label):
                    model_id = mid
                    break
            if model_id is None:
                continue
            windows = ((m.get("rangeStats") or {}).get("all")) or {}
            if key not in windows:
                continue  # not measured in the headline window -> honest empty
            w = windows[key]
            rate = w.get("resolvedRate") if isinstance(w, dict) else None
            if not isinstance(rate, (int, float)):
                continue
            flags = [f"agent/effort variant: {name}"]
            sem = w.get("sem") if isinstance(w, dict) else None
            if isinstance(sem, (int, float)):
                flags.append(f"±{round(sem, 2)} SEM")
            rel = ((m.get("release") or {}).get("date") or "")[:10]
            if rel:
                try:
                    rel_dt = datetime.fromisoformat(rel).replace(tzinfo=timezone.utc)
                    if rel_dt > window_start:
                        flags.append(
                            "potential contamination: released after the issue-window start "
                            f"({rel} > {window_start.date()}) — board-flagged"
                        )
                except ValueError:
                    pass
            ws = window_start.date().isoformat()
            cv = CellValue("swe-rebench", model_id, round(rate, 1), "%", "I", "S20",
                           f"swe-rebench-window-{ws}", self.fetched_at, flags=flags)
            # best variant per model (mirrors TB best-per-model policy)
            existing = next((c for c in out if c.model_id == model_id), None)
            if existing is None:
                out.append(cv)
            elif cv.value > existing.value:
                out[out.index(existing)] = cv
        if not out:
            raise ParseFailure("swe-rebench: parsed but no mapped models found")
        return out


class ValsCollector(Collector):
    source_id = "S11"
    name = "vals-index"
    url = "https://www.vals.ai/benchmarks/vals_index"

    def parse(self, raw: bytes) -> list[CellValue]:
        html = raw.decode("utf-8", errors="strict")
        m = re.search(r'<astro-island[^>]*props="([^"]*benchmarkView[^"]*)"', html)
        if not m:
            raise ParseFailure("vals: astro-island props not found — page shape changed")
        props = json.loads(html_lib.unescape(m.group(1)))

        def undress(node):
            """Astro serializes as [type, value]; unwrap recursively."""
            if isinstance(node, list) and len(node) == 2 and node[0] in (0, 1):
                return undress(node[1]) if node[0] == 0 else [undress(x) for x in node[1]]
            if isinstance(node, dict):
                return {k: undress(v) for k, v in node.items()}
            return node

        data = undress(props)

        def find_overall(node):
            if isinstance(node, dict):
                if "overall" in node and isinstance(node["overall"], dict):
                    sample = next(iter(node["overall"].values()), None)
                    if isinstance(sample, dict) and "accuracy" in sample:
                        return node["overall"]
                for v in node.values():
                    r = find_overall(v)
                    if r is not None:
                        return r
            return None

        overall = find_overall(data)
        if not overall:
            raise ParseFailure("vals: tasks.overall accuracy map not found — shape changed")
        out = []
        for key, mid in VALS_KEYS.items():
            row = overall.get(key)
            if not isinstance(row, dict):
                continue
            acc = row.get("accuracy")
            if not isinstance(acc, (int, float)):
                raise ParseFailure(f"vals: non-numeric accuracy for {key!r}")
            out.append(CellValue("vals-index", mid, round(acc, 1), "index", "I", "S11",
                                 "vals-index-composite", self.fetched_at,
                                 flags=[VALS_CAV, "weighted composite (Vals Index)"]))
        if not out:
            raise ParseFailure("vals: parsed but no mapped models found")
        return out
