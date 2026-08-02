"""Arena collector (S2): official HF dataset via datasets-server filter API
(the sanctioned channel — arena.ai's own ToS bars scraping the site).
Board pinned to text_style_control / overall (the site default). Policy:
highest-rated variant per model family, variant recorded in flags."""

from __future__ import annotations

import json

from .base import CellValue, Collector, ParseFailure
from .model_map import ARENA_PREFIXES

ARENA_CAV = "private variant testing active (Arena)"

FILTER_URL = (
    "https://datasets-server.huggingface.co/filter"
    "?dataset=lmarena-ai%2Fleaderboard-dataset"
    "&config=text_style_control&split=latest"
    "&where=%22category%22%3D%27overall%27&limit=100"
)


class ArenaCollector(Collector):
    source_id = "S2"
    name = "arena"
    url = FILTER_URL
    fixture = "arena_hf_filter.json"

    def parse(self, raw: bytes) -> list[CellValue]:
        data = json.loads(raw.decode("utf-8"))
        rows = data.get("rows")
        if not isinstance(rows, list) or not rows:
            raise ParseFailure("Arena HF filter: rows[] missing/empty — API shape changed")
        best = {}
        publish = None
        for wrapper in rows:
            row = wrapper.get("row", wrapper)
            name = str(row.get("model_name", ""))
            rating = row.get("rating")
            if not isinstance(rating, (int, float)):
                continue
            publish = row.get("leaderboard_publish_date") or publish
            for prefix, model_id in ARENA_PREFIXES.items():
                if name.startswith(prefix):
                    cur = best.get(model_id)
                    if cur is None or rating > cur[0]:
                        best[model_id] = (round(rating, 1), name, row.get("rank"))
        out = []
        retrieved = f"{publish}T00:00:00Z" if publish else self.fetched_at
        for model_id, (rating, variant, rank) in best.items():
            flags = [ARENA_CAV, f"variant: {variant}" + (f" (rank {rank})" if rank else "")]
            out.append(CellValue("arena-elo", model_id, rating, "Elo", "I", "S2",
                                 "arena-text-style-control", retrieved, flags=flags))
        if not out:
            raise ParseFailure("Arena HF filter: parsed but no mapped models found")
        return out
