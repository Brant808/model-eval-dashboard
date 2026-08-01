#!/usr/bin/env python3
"""Judgment layer (Phase 7, optional tier). Mechanical tape is the shipped
default; this script upgrades tape/implications ONLY when every safeguard
passes, and degrades to mechanical loudly otherwise.

Safeguards, in order:
1. Runs only when ANTHROPIC_API_KEY is set and the `claude` CLI exists.
2. The prompt is LOCKED: its sha256 is pinned below. Editing the prompt
   without re-pinning is a hard failure (tamper-evident in diff review).
3. Output must parse as JSON and match the narrow schema.
4. No-new-facts validator: every cited cell must exist and be populated;
   every number in generated text must already exist in the cited cells
   (value, previous value, or delta — plus digits the cell itself carries
   in unit/flags/window labels/dates). The model may summarize and rank;
   it may not introduce a single fact the snapshot does not contain.
5. Integrity flags on cited cells must be carried verbatim (rule 7), and
   cites may not mix SWE-bench families (rule 5). The full constitutional
   linter still runs after this script — it stays the final authority.

Any rejection: keep the mechanical snapshot untouched, record the reason in
health.judgment_layer, exit 0 (the daily publish never depends on judgment).
Exit is nonzero only for local bugs (unreadable snapshot, pin mismatch).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("PIPELINE_DATA_DIR") or REPO / "data")
sys.path.insert(0, str(REPO))

from tools.check_invariants import integrity_flags, load_json_strict  # noqa: E402

DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(\.seed)?\.json$")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
CONFIDENCE = {"high", "med", "low"}

# Metric-id prefix -> SWE family (rule 5: families never co-cited).
SWE_FAMILIES = {"swe-bench-pro": "pro", "swe-bench-verified": "verified",
                "swe-rebench": "rebench"}

LOCKED_PROMPT = """\
You are the judgment layer of a model-eval dashboard. Input (stdin JSON):
{"snapshot_date", "metrics", "cells", "previous_cells", "mechanical_tape"}.

Task: return STRICT JSON, nothing else, shaped exactly:
{"tape": [{"date": "<snapshot_date>", "text": "...", "source_id": "S#",
           "cell_ids": ["metric.model", ...]}],
 "implications": [{"id": "IMP-#", "tag": "X", "text": "...",
                   "cites": ["metric.model", ...],
                   "confidence": "high|med|low", "falsifier": "...",
                   "flags_carried": ["..."]}]}

Rules you must obey (violations are discarded by a validator):
- Only restate facts present in the input cells. Never introduce a number
  that is not a cited cell's value, previous value, or their difference.
- Every tape entry's source_id must be a cited cell's source_id.
- Copy every integrity flag of every cited cell verbatim into flags_carried.
- Never cite or compare cells from different SWE-bench families
  (SWE-bench Pro / SWE-bench Verified / SWE-rebench) in one entry.
- Confidence reflects source independence and staleness of the cited cells.
- Each implication needs a concrete falsifier: what observation would kill it.
- Prefer 3-6 tape entries covering the largest genuine movements; return
  implications only when the evidence supports rewriting the current set,
  else return an empty implications list.
"""
PROMPT_SHA256 = "806440216fc603cc9fa68e06903cfa6da66c8b5d23f468d3976479334faae5ab"


def newest_dated() -> Path:
    snaps = sorted(p for p in DATA.glob("*.json") if DATED_RE.match(p.name))
    if not snaps:
        sys.exit("judgment: no dated snapshots")
    return snaps[-1]


def cell_number_vocabulary(cell: dict, prev: dict | None) -> set[str]:
    """Every numeric string a text is allowed to use when citing this cell."""
    vocab: set[str] = set()

    def add(x):
        if isinstance(x, (int, float)):
            vocab.add(_norm(str(x)))
            vocab.add(_norm(f"{x:.2f}"))
            vocab.add(_norm(f"{x:.1f}"))
            vocab.add(_norm(f"{round(x)}"))

    for c in (cell, prev or {}):
        add(c.get("value"))
        for field in ("unit", "comparability_set", "effort_tier",
                      "retrieved_at", "empty_reason"):
            for tok in NUM_RE.findall(str(c.get(field) or "")):
                vocab.add(_norm(tok))
        for f in c.get("flags", []):
            for tok in NUM_RE.findall(f):
                vocab.add(_norm(tok))
    v_now, v_prev = cell.get("value"), (prev or {}).get("value")
    if isinstance(v_now, (int, float)) and isinstance(v_prev, (int, float)):
        add(abs(round(v_now - v_prev, 2)))
    return vocab


def _norm(num: str) -> str:
    """Normalize numeric strings so 9.10 == 9.1 == 9.100."""
    return num.rstrip("0").rstrip(".") if "." in num else num


def swe_family(cell_id: str) -> str | None:
    for prefix, fam in SWE_FAMILIES.items():
        if cell_id.startswith(prefix + "."):
            return fam
    return None


def validate_entry(entry: dict, kind: str, snap: dict, prev_cells: dict) -> str | None:
    """Return a rejection reason, or None if the entry is admissible."""
    cites = entry.get("cell_ids") if kind == "tape" else entry.get("cites")
    if not cites or not isinstance(cites, list):
        return f"{kind}: no cites"
    cells, vocab, families, source_ids, needed_flags = snap["cells"], set(), set(), set(), []
    # Digits that are names, not facts: model/metric display names ("Fable 5",
    # "GPT-5.6 Sol", "ARC-AGI-3") and the snapshot date itself.
    for tok in NUM_RE.findall(str(snap.get("snapshot_date") or "")):
        vocab.add(_norm(tok))
    for cid in cites:
        metric_id, _, model_id = str(cid).partition(".")
        cell = cells.get(metric_id, {}).get(model_id)
        if cell is None or cell.get("value") is None:
            return f"{kind}: cite {cid} missing or empty"
        vocab |= cell_number_vocabulary(cell, prev_cells.get(metric_id, {}).get(model_id))
        for label in (snap.get("metrics", {}).get(metric_id, {}).get("name", ""),
                      snap.get("models", {}).get(model_id, {}).get("name", "")):
            for tok in NUM_RE.findall(str(label)):
                vocab.add(_norm(tok))
        source_ids.add(cell.get("source_id"))
        needed_flags += integrity_flags(cell)
        fam = swe_family(str(cid))
        if fam:
            families.add(fam)
    if len(families) > 1:
        return f"{kind}: mixes SWE-bench families {sorted(families)} (rule 5)"

    text = str(entry.get("text") or "")
    if not text:
        return f"{kind}: empty text"
    for tok in NUM_RE.findall(text):
        if _norm(tok) not in vocab:
            return f"{kind}: number {tok!r} not present in cited cells (no-new-facts)"

    if kind == "tape":
        if entry.get("date") != snap["snapshot_date"]:
            return "tape: date != snapshot_date"
        if entry.get("source_id") not in source_ids:
            return f"tape: source_id {entry.get('source_id')!r} not among cited cells' sources"
    else:
        if entry.get("tag") != "X":
            return "implication: tag must be X"
        if entry.get("confidence") not in CONFIDENCE:
            return f"implication: bad confidence {entry.get('confidence')!r}"
        if not str(entry.get("falsifier") or "").strip():
            return "implication: falsifier required"
        carried = entry.get("flags_carried") or []
        for f in needed_flags:
            if f not in carried:
                return f"implication: integrity flag not carried verbatim: {f!r} (rule 7)"
    return None


def run_model(payload: str) -> str:
    proc = subprocess.run(
        ["claude", "-p", LOCKED_PROMPT, "--output-format", "json"],
        input=payload, capture_output=True, text=True, timeout=480,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {proc.stderr[:400]}")
    out = json.loads(proc.stdout)
    result = out.get("result") if isinstance(out, dict) else None
    if not isinstance(result, str):
        raise RuntimeError("claude CLI: unexpected wrapper shape")
    start, end = result.find("{"), result.rfind("}")
    if start < 0 or end <= start:
        raise RuntimeError("claude CLI: no JSON object in result")
    return result[start : end + 1]


def degrade(snap: dict, path: Path, reason: str):
    snap["health"]["judgment_layer"] = f"off (mechanical — {reason})"
    write_snapshot(snap, path)
    print(f"judgment: degraded to mechanical — {reason}", file=sys.stderr)


def write_snapshot(snap: dict, path: Path):
    path.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copyfile(path, DATA / "latest.json")  # SYNC rule


def main():
    if hashlib.sha256(LOCKED_PROMPT.encode()).hexdigest() != PROMPT_SHA256:
        sys.exit("judgment: prompt was edited without re-pinning PROMPT_SHA256")
    path = newest_dated()
    snap = load_json_strict(path)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("judgment: ANTHROPIC_API_KEY not set — mechanical mode stands")
        return
    if shutil.which("claude") is None:
        degrade(snap, path, "claude CLI not installed")
        return

    dated = sorted(p for p in DATA.glob("*.json") if DATED_RE.match(p.name))
    prev_cells = load_json_strict(dated[-2])["cells"] if len(dated) > 1 else {}
    payload = json.dumps({
        "snapshot_date": snap["snapshot_date"],
        "metrics": snap["metrics"],
        "cells": snap["cells"],
        "previous_cells": prev_cells,
        "mechanical_tape": snap["tape"],
    }, ensure_ascii=False)
    input_sha = hashlib.sha256(payload.encode()).hexdigest()

    try:
        proposed = json.loads(run_model(payload))
    except Exception as e:  # noqa: BLE001 — any model-side failure degrades
        degrade(snap, path, f"model call failed: {e}")
        return

    tape, rejected = [], []
    for entry in proposed.get("tape") or []:
        reason = validate_entry(entry, "tape", snap, prev_cells)
        (rejected if reason else tape).append(reason or entry)
    imps, imp_ok = [], True
    for entry in proposed.get("implications") or []:
        reason = validate_entry(entry, "implication", snap, prev_cells)
        if reason:
            rejected.append(reason)
            imp_ok = False
        else:
            imps.append(entry)

    for r in rejected:
        print(f"judgment: REJECTED — {r}", file=sys.stderr)
    if not tape:
        degrade(snap, path, f"all {len(rejected)} proposed entries rejected"
                if rejected else "model returned no tape")
        return

    snap["tape"] = tape + snap["tape"]
    # Implications are all-or-nothing: a partially valid set reads as complete.
    if imps and imp_ok:
        snap["implications"] = imps
    snap["health"]["judgment_layer"] = (
        f"on (claude -p; prompt {PROMPT_SHA256[:12]}; input {input_sha[:12]}; "
        f"{len(rejected)} entries rejected by validator)"
    )
    write_snapshot(snap, path)
    print(f"judgment: accepted {len(tape)} tape entries, "
          f"{len(imps) if imps and imp_ok else 0} implications; {len(rejected)} rejected")


if __name__ == "__main__":
    main()
