"""METR collector (S5): versioned YAML of time-horizon results. Asserts suite
version from file CONTENT (gate note: the page toggles the same href between
v1.0/v1.1 files). The Sol blog-only figure (S18) is NOT collected here — it is
a curated override with its own provenance (data/overrides.json)."""

from __future__ import annotations

import yaml

from .base import CellValue, Collector, ParseFailure
from .model_map import METR_KEYS

EXPECTED_SUITE = "1.1"


class MetrCollector(Collector):
    source_id = "S5"
    name = "metr"
    url = "https://metr.org/assets/benchmark_results_1_1.yaml"

    def parse(self, raw: bytes) -> list[CellValue]:
        data = yaml.safe_load(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ParseFailure("METR yaml: top level is not a mapping")
        suite = str(data.get("benchmark_name", ""))
        if EXPECTED_SUITE not in suite:
            raise ParseFailure(
                f"METR yaml: expected suite v{EXPECTED_SUITE}, benchmark_name={suite!r} — "
                "the page's raw-data link may have toggled to another suite version"
            )
        results = data.get("results")
        if not isinstance(results, dict):
            raise ParseFailure("METR yaml: results mapping missing — shape changed")
        out = []
        for key, (model_id, extra_flags) in METR_KEYS.items():
            row = results.get(key)
            if row is None:
                continue
            metrics = row.get("metrics") or {}
            p50 = metrics.get("p50_horizon_length") or {}
            est, lo, hi = p50.get("estimate"), p50.get("ci_low"), p50.get("ci_high")
            if not isinstance(est, (int, float)):
                raise ParseFailure(f"METR yaml: {key} p50 estimate missing/non-numeric")
            hours = round(est / 60.0, 1)
            flags = list(extra_flags)
            if isinstance(lo, (int, float)) and isinstance(hi, (int, float)):
                flags.append(f"95% CI {round(lo/60.0,1)}–{round(hi/60.0,1)}h")
            if hours > 16:
                flags.append("METR: measurements above 16h are unreliable with the current task suite")
            if metrics.get("is_sota"):
                flags.append("is_sota on TH-1.1")
            out.append(CellValue("metr-horizon", model_id, hours, "hours", "I", "S5",
                                 "metr-50pct-horizon", self.fetched_at, flags=flags))
        if not out:
            raise ParseFailure("METR yaml: parsed but no mapped models found")
        return out
