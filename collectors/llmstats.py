"""llm-stats collector (S13): SWE-bench Pro vendor-claim aggregate from the
page's embedded flight payload. ALL rows are vendor self-reports -> tag V,
caveat flag mandatory (ledger-enforced)."""

from __future__ import annotations

from .base import CellValue, Collector, ParseFailure, balanced_json_array, decode_flight_region
from .model_map import LLMSTATS_IDS

LLMS_CAV = "aggregated vendor self-reports (0 of 43 verified)"


class LlmStatsCollector(Collector):
    source_id = "S13"
    name = "llmstats-swe-pro"
    url = "https://llm-stats.com/benchmarks/swe-bench-pro"
    fixture = "llmstats_swe_pro.html.gz"

    def parse(self, raw: bytes) -> list[CellValue]:
        html = raw.decode("utf-8", errors="strict")
        # Anchor on the benchmark statistics block, then take the "models"
        # array that follows it (a bare 'models' anchor collides with
        # total_models/child_benchmarks).
        txt = decode_flight_region(html, "self_reported_count")
        rows = balanced_json_array(txt, '"models":')
        if not rows:
            raise ParseFailure("llm-stats: models[] empty — shape changed")
        out = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            model_id = LLMSTATS_IDS.get(str(row.get("model_id", "")))
            if model_id is None:
                continue
            score = row.get("score")
            if not isinstance(score, (int, float)):
                raise ParseFailure(f"llm-stats: non-numeric score for {row.get('model_id')!r}")
            if row.get("verified") is True:
                # would be a big (good) methodology change — surface it loudly
                raise ParseFailure(
                    f"llm-stats: row {row.get('model_id')!r} claims verified=true — "
                    "source semantics changed, re-review provenance before collecting"
                )
            flags = [LLMS_CAV]
            src = row.get("self_reported_source")
            if src:
                flags.append(f"self-report source: {src}")
            out.append(CellValue("swe-bench-pro", model_id, round(score * 100, 1), "%", "V", "S13",
                                 "swe-bench-pro-vendor-aggregate", self.fetched_at, flags=flags))
        if not out:
            raise ParseFailure("llm-stats: parsed but no mapped models found")
        return out
