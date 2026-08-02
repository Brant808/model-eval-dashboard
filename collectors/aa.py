"""Artificial Analysis collector (S1) — keyless embedded-JSON channel.

Feeds: aa-index, aa-agentic-index, gdpval-aa, cost-per-task, aa-omniscience,
aa-halluc-rate, intelligence-per-dollar (derived), throughput-ttft (brief
layer), context-window (brief layer), api-price relays.

If AA_API_KEY is present in the environment, Phase 7 may prefer the documented
API v2 for the free-tier fields; the embedded channel remains the fallback and
the sole channel for GDPval/Omniscience.
"""

from __future__ import annotations

from .base import (
    CellValue,
    Collector,
    ParseFailure,
    balanced_json_array,
    decode_flight_region,
)
from .model_map import AA_SLUGS

GEM = "Gemini-graded (AA judge panel)"


class AACollector(Collector):
    source_id = "S1"
    name = "artificialanalysis"
    url = "https://artificialanalysis.ai/models"
    fixture = "aa_models.html.gz"

    def parse(self, raw: bytes) -> list[CellValue]:
        html = raw.decode("utf-8", errors="strict")
        txt = decode_flight_region(html, 'initialModels\\":')
        models = balanced_json_array(txt, 'initialModels":')
        by_slug = {m.get("slug"): m for m in models if isinstance(m, dict)}
        out = []
        for slug, model_id in AA_SLUGS.items():
            m = by_slug.get(slug)
            if m is None:
                continue  # honest empty downstream

            def num(v):
                return round(v, 2) if isinstance(v, (int, float)) else None

            ii = num(m.get("intelligenceIndex"))
            if ii is not None:
                out.append(CellValue("aa-index", model_id, ii, "index", "I", "S1",
                                     "aa-index-v4.1", self.fetched_at))
            agentic = num(m.get("agenticIndex"))
            if agentic is not None:
                out.append(CellValue("aa-agentic-index", model_id, agentic, "index", "I", "S1",
                                     "aa-agentic-index-v4.1", self.fetched_at, flags=[GEM]))
            gdpval = num(m.get("gdpval"))
            if gdpval is not None:
                out.append(CellValue("gdpval-aa", model_id, gdpval, "Elo", "I", "S1",
                                     "gdpval-aa-v2", self.fetched_at, flags=[GEM]))
            cpt = m.get("intelligenceIndexCostPerTask") or {}
            cost_total = (cpt.get("cost") or {}).get("total")
            if isinstance(cost_total, (int, float)):
                cost_total = round(cost_total, 2)
                out.append(CellValue("cost-per-task", model_id, cost_total, "USD/task", "I", "S1",
                                     "aa-cost-per-task", self.fetched_at))
                if ii is not None and cost_total > 0:
                    out.append(CellValue(
                        "intelligence-per-dollar", model_id, round(ii / cost_total, 1),
                        "index pts per task-USD", "I", "S1", "aa-intelligence-per-usd",
                        self.fetched_at,
                        flags=[f"derived: aa-index ({ii}) ÷ cost-per-task (${cost_total})"],
                        derived_from=[f"aa-index.{model_id}", f"cost-per-task.{model_id}"],
                    ))
            omni = num(m.get("omniscience"))
            if omni is not None:
                out.append(CellValue("aa-omniscience", model_id, omni, "index", "I", "S1",
                                     "aa-omniscience", self.fetched_at, flags=[GEM]))
            ob = m.get("omniscienceBreakdown") or {}
            hall = ob.get("hallucinationRate")
            if isinstance(hall, (int, float)):
                out.append(CellValue("aa-halluc-rate", model_id, round(hall * 100, 1), "%", "I", "S1",
                                     "aa-omniscience-halluc", self.fetched_at, flags=[GEM]))
            ctx = m.get("contextWindowTokens")
            if isinstance(ctx, int):
                out.append(CellValue("context-window", model_id, ctx, "tokens", "V", "S1",
                                     "context-window", self.fetched_at,
                                     flags=["vendor-declared window as listed by AA"]))
            pin, pout = m.get("price1mInputTokens"), m.get("price1mOutputTokens")
            if isinstance(pin, (int, float)) and isinstance(pout, (int, float)):
                def fmt(p):
                    return f"${pin:g} / ${pout:g}"
                out.append(CellValue("api-price", model_id, fmt(pin), "USD/Mtok in/out", "V", "S1",
                                     "list-price", self.fetched_at,
                                     flags=["list price as relayed by AA data"]))
            ttfa = (m.get("timeToFirstAnswerToken") or {}).get("total")
            if isinstance(ttfa, (int, float)):
                out.append(CellValue("throughput-ttft", model_id, f"TTFA {round(ttfa, 1)} s",
                                     "s", "I", "S1", "aa-throughput", self.fetched_at))
        if not out:
            raise ParseFailure("AA: page parsed but produced no mapped model rows")
        return out
