#!/usr/bin/env python3
"""Explainability helper: diff two snapshots and emit changelog entries for
every changed / appeared / removed cell NOT already explained by the newer
snapshot's tape. Used by Phase 7's pipeline and by hand during rebuilds.

Usage: python3 tools/make_changelog.py OLD.json NEW.json
Prints a JSON array of changelog entries to stdout (date = new snapshot date).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.check_invariants import iter_cells, load_json_strict  # noqa: E402


def diff_entries(older, newer):
    explained = set()
    for entry in newer.get("tape", []):
        explained.update(entry.get("cell_ids", []))
    old_cells = {f"{m}.{mo}": c for m, mo, c in iter_cells(older)}
    new_cells = {f"{m}.{mo}": c for m, mo, c in iter_cells(newer)}
    date = newer.get("snapshot_date", "")
    out = []
    for cid in sorted(set(old_cells) | set(new_cells)):
        if cid in explained:
            continue
        if cid not in new_cells:
            if old_cells[cid].get("value") is None:
                continue  # an empty cell disappearing is schema churn, not data
            out.append({"date": date, "cell_ids": [cid], "note": "cell removed", "class": "removed"})
        elif cid not in old_cells:
            nv = new_cells[cid].get("value")
            if nv is None:
                continue  # a new empty cell explains itself via empty_reason
            out.append(
                {"date": date, "cell_ids": [cid], "note": f"cell newly populated: {nv!r}", "class": "appeared"}
            )
        else:
            ov, nv = old_cells[cid].get("value"), new_cells[cid].get("value")
            if ov != nv:
                out.append(
                    {"date": date, "cell_ids": [cid], "note": f"value {ov!r} -> {nv!r}", "class": "changed"}
                )
            else:
                # Flag-set changes are trust-state changes (an integrity flag
                # appearing/disappearing) — invisible before this (gate MINOR:
                # "new-integrity-flag detection is a named judgment duty that
                # mechanical mode lacked entirely").
                of, nf = set(old_cells[cid].get("flags", [])), set(new_cells[cid].get("flags", []))
                if of != nf:
                    gained, lost = sorted(nf - of), sorted(of - nf)
                    bits = ([f"flags gained: {g}" for g in gained]
                            + [f"flags dropped: {l}" for l in lost])
                    out.append({"date": date, "cell_ids": [cid],
                                "note": "; ".join(bits), "class": "flags-changed"})
    return out


def main():
    older = load_json_strict(Path(sys.argv[1]))
    newer = load_json_strict(Path(sys.argv[2]))
    print(json.dumps(diff_entries(older, newer), indent=2))


if __name__ == "__main__":
    main()
