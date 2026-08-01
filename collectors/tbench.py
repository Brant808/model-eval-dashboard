"""Terminal-Bench collector (S8): official 2.1 board from the page's embedded
flight payload (SSR — no JS needed). Scores are agent+model+effort tuples;
policy (ROWS.md): best-per-model from the DISPLAYED board only, tuple recorded
in flags. Repo-only submissions are ignored (displayed board is canonical)."""

from __future__ import annotations

from .base import CellValue, Collector, ParseFailure, balanced_json_array, decode_flight_region
from .model_map import TBENCH_NAMES

TB_CAV = "self-run by vendor, log-audited by maintainers"


class TbenchCollector(Collector):
    source_id = "S8"
    name = "terminal-bench"
    url = "https://www.tbench.ai/leaderboard/terminal-bench/2.1"

    def parse(self, raw: bytes) -> list[CellValue]:
        html = raw.decode("utf-8", errors="strict")
        txt = decode_flight_region(html, 'rows\\":[')
        rows = balanced_json_array(txt, 'rows":')
        if not rows:
            raise ParseFailure("tbench: rows[] empty — shape changed")
        def label(v):
            """metadata display fields are {url, label} objects."""
            if isinstance(v, dict):
                return str(v.get("label", ""))
            return str(v or "")

        best = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            meta = row.get("metadata", row)
            metrics = row.get("metrics", row)
            display = label(meta.get("model_display"))
            model_id = TBENCH_NAMES.get(display)
            if model_id is None:
                continue
            acc = metrics.get("accuracy")
            if not isinstance(acc, (int, float)):
                raise ParseFailure(f"tbench: non-numeric accuracy for {display!r}")
            acc = round(acc, 1)
            agent = label(meta.get("agent_display")) or "?"
            effort = meta.get("reasoning_effort") or "?"
            stderr = metrics.get("accuracy_stderr")
            cur = best.get(model_id)
            if cur is None or acc > cur.value:
                flags = [TB_CAV, f"agent+model+effort tuple: {agent}, effort {effort}"]
                if isinstance(stderr, (int, float)):
                    flags.append(f"±{round(stderr, 1)}% stderr over {metrics.get('n_trials', '?')} trials")
                best[model_id] = CellValue("terminal-bench", model_id, acc, "%", "I", "S8",
                                           "terminal-bench-2.1", self.fetched_at, flags=flags)
        if not best:
            raise ParseFailure("tbench: parsed but no mapped models found")
        return list(best.values())
