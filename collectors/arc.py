"""ARC Prize collector (S4): official v3.json. One board row per (model, tier);
we surface each mapped model's best-scoring tier, tier recorded per rule 6."""

from __future__ import annotations

import json

from .base import CellValue, Collector, ParseFailure
from .model_map import ARC_PREFIXES, ARC_TIER_DISPLAY, ARC_TIERS


class ArcCollector(Collector):
    source_id = "S4"
    name = "arcprize"
    url = "https://arcprize.org/media/data/leaderboard/v3.json"

    def parse(self, raw: bytes) -> list[CellValue]:
        data = json.loads(raw.decode("utf-8"), parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
        rows = data.get("evaluations")
        if not isinstance(rows, list) or not rows:
            raise ParseFailure("ARC v3.json: evaluations[] missing/empty — shape changed")
        generated = data.get("generatedAt", self.fetched_at)
        retrieved = generated.split(".")[0] + "Z" if "." in generated else generated
        best = {}
        for row in rows:
            mid = row.get("modelId", "")
            score = row.get("score")
            if not isinstance(score, (int, float)):
                raise ParseFailure(f"ARC v3.json: non-numeric score in row {mid!r}")
            tier = None
            base = mid
            for t in ARC_TIERS:
                if mid.endswith("-" + t):
                    tier = ARC_TIER_DISPLAY[t]
                    base = mid[: -(len(t) + 1)]
                    break
            model_id = ARC_PREFIXES.get(base)
            if model_id is None or tier is None:
                continue
            pct = round(score * 100, 2)
            if model_id not in best or pct > best[model_id][0]:
                best[model_id] = (pct, tier, row.get("cost"))
        out = []
        for model_id, (pct, tier, cost) in best.items():
            flags = []
            if isinstance(cost, (int, float)):
                flags.append(f"run cost ${cost:,.0f}")
            out.append(CellValue("arc-agi-3", model_id, pct, "%", "I", "S4",
                                 "arc-agi-3-official", retrieved,
                                 effort_tier=tier, flags=flags))
        if not out:
            raise ParseFailure("ARC v3.json: parsed but no mapped models found")
        return out
