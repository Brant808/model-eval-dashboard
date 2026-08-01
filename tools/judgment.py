#!/usr/bin/env python3
"""Judgment layer (Phase 7, optional tier). Mechanical tape is the shipped
default; this script upgrades tape/implications ONLY when every safeguard
passes, and degrades to mechanical loudly otherwise.

Safeguards, in order:
1. Runs only when ANTHROPIC_API_KEY is set (one Messages-API call).
2. The prompt, model id and token cap are LOCKED: their combined sha256 is
   pinned below. Editing any of them without re-pinning is a hard failure
   (tamper-evident in diff review).
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
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("PIPELINE_DATA_DIR") or REPO / "data")
sys.path.insert(0, str(REPO))

from tools.check_invariants import integrity_flags, load_json_strict  # noqa: E402

DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(\.seed)?\.json$")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
# Source-id citations ("S13") are references, not facts — scrubbed before the
# number scan so "source S13" doesn't need 13 to be a cell value.
SOURCE_ID_RE = re.compile(r"\bS\d+\b")
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
MODEL = "claude-opus-5"
MAX_TOKENS = 4096
# The pin covers transport parameters too, not just the prompt text — editing
# the model or token cap without re-pinning is the same tamper as editing the
# prompt (gate finding, innovator phases 6-8, defect D-1 rider).
LOCKED_MATERIAL = f"model={MODEL}\nmax_tokens={MAX_TOKENS}\n{LOCKED_PROMPT}"
PROMPT_SHA256 = "3351aa4557b55513a41c541ab2b95a36c7f698892c200532dacd9fc0d8b137c4"


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
            # abs() because NUM_RE has no sign: text saying "10.02" must match
            # a cell valued -10.02 (verifier gate finding, negative values).
            for y in (x, abs(x)):
                vocab.add(_norm(str(y)))
                vocab.add(_norm(f"{y:.2f}"))
                vocab.add(_norm(f"{y:.1f}"))
                vocab.add(_norm(f"{round(y)}"))

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
    cited_flags = set()  # union of cited cells' flags: the only legal flags_carried pool
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
        cited_flags.update(cell.get("flags", []))
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
    for tok in NUM_RE.findall(SOURCE_ID_RE.sub(" ", text)):
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
        # Falsifier and flags_carried are rendered channels too — a fabricated
        # number or a fabricated ⚠ accusation would ship looking validated
        # (phase-7 red-team BLOCKING, demonstrated end-to-end).
        for tok in NUM_RE.findall(SOURCE_ID_RE.sub(" ", str(entry.get("falsifier") or ""))):
            if _norm(tok) not in vocab:
                return (f"implication: falsifier number {tok!r} not present in "
                        f"cited cells (no-new-facts)")
        carried = entry.get("flags_carried") or []
        for f in carried:
            if f not in cited_flags:
                return f"implication: flags_carried contains a flag absent from cited cells: {f!r}"
        for f in needed_flags:
            if f not in carried:
                return f"implication: integrity flag not carried verbatim: {f!r} (rule 7)"
    return None


def run_model(payload: str) -> str:
    """One Messages-API call over requests (already a pipeline dependency).
    Gate finding (innovator D-1): the CLI transport was inert in CI — the
    runner never installs it — so the upgrade path could never activate."""
    import requests

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01"},
        json={"model": MODEL, "max_tokens": MAX_TOKENS,
              "system": LOCKED_PROMPT,
              "messages": [{"role": "user", "content": payload}]},
        timeout=480,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"messages API {resp.status_code}: {resp.text[:300]}")
    text = "".join(b.get("text", "") for b in (resp.json().get("content") or [])
                   if isinstance(b, dict))
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise RuntimeError("model returned no JSON object")
    return text[start : end + 1]


def degrade(snap: dict, path: Path, reason: str):
    snap["health"]["judgment_layer"] = f"off (mechanical — {reason})"
    write_snapshot(snap, path)
    print(f"judgment: degraded to mechanical — {reason}", file=sys.stderr)


def write_snapshot(snap: dict, path: Path):
    path.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copyfile(path, DATA / "latest.json")  # SYNC rule


def main():
    if hashlib.sha256(LOCKED_MATERIAL.encode()).hexdigest() != PROMPT_SHA256:
        sys.exit("judgment: prompt/model/max_tokens edited without re-pinning PROMPT_SHA256")
    path = newest_dated()
    snap = load_json_strict(path)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("judgment: ANTHROPIC_API_KEY not set — mechanical mode stands")
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

    # A judged entry supersedes the mechanical line for the same cells —
    # otherwise every move is reported twice while the header claims an
    # editorial layer is on (gate finding). Uncovered mechanical entries stay
    # for explainability.
    covered = {cid for e in tape for cid in e.get("cell_ids", [])}
    snap["tape"] = tape + [
        e for e in snap["tape"]
        if not (e.get("text", "").startswith("Mechanical tape")
                and e.get("cell_ids") and set(e["cell_ids"]) <= covered)
    ]
    # Implications are all-or-nothing: a partially valid set reads as complete.
    if imps and imp_ok:
        snap["implications"] = imps
    snap["health"]["judgment_layer"] = (
        f"on ({MODEL}; pin {PROMPT_SHA256[:12]}; input {input_sha[:12]}; "
        f"{len(rejected)} entries rejected by validator)"
    )
    write_snapshot(snap, path)
    print(f"judgment: accepted {len(tape)} tape entries, "
          f"{len(imps) if imps and imp_ok else 0} implications; {len(rejected)} rejected")


if __name__ == "__main__":
    main()
