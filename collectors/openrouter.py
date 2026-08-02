"""OpenRouter collector (S3): frontend rankings JSON (RISK-006 posture — one
polite GET per endpoint per day; permanent stand-down on any block).
Provider token share from the last COMPLETE weekly bucket."""

from __future__ import annotations

import json

from .base import CellValue, Collector, ParseFailure
from .model_map import OPENROUTER_AUTHORS

UNIT_AMB = "unit per page copy ambiguous (counts consistent with tokens)"


class OpenRouterCollector(Collector):
    source_id = "S3"
    name = "openrouter"
    url = "https://openrouter.ai/api/frontend/v1/rankings/market-share"
    fixture = "openrouter_market_share.json"

    def parse(self, raw: bytes) -> list[CellValue]:
        data = json.loads(raw.decode("utf-8"))
        buckets = data.get("data")
        if not isinstance(buckets, list) or len(buckets) < 2:
            raise ParseFailure("OpenRouter market-share: data[] missing/short — shape changed")
        complete = buckets[-2]  # last bucket is the in-progress week
        week = complete.get("x", "")
        ys = complete.get("ys")
        if not isinstance(ys, dict) or not ys:
            raise ParseFailure("OpenRouter market-share: ys{} missing — shape changed")
        total = sum(v for v in ys.values() if isinstance(v, (int, float)))
        if total <= 0:
            raise ParseFailure("OpenRouter market-share: zero weekly total")
        out = []
        for author, (model_ids, provider) in OPENROUTER_AUTHORS.items():
            v = ys.get(author)
            if not isinstance(v, (int, float)):
                continue  # below top-N -> honest empty downstream
            share = round(100.0 * v / total, 1)
            for model_id in model_ids:
                out.append(CellValue(
                    "openrouter-share", model_id, share, "% tokens", "I", "S3",
                    "openrouter-provider-share", self.fetched_at,
                    flags=[f"provider-level: {provider} total, not per-model",
                           UNIT_AMB, f"week {week} (last complete)"],
                ))
        if not out:
            raise ParseFailure("OpenRouter market-share: parsed but no mapped providers found")
        return out
