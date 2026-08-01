#!/usr/bin/env python3
"""Invariant linter: enforces the 12 constitutional data rules (CLAUDE.md /
governance/BRIEF.md section 2) against every snapshot in data/ and the built
HTML page. `make check` runs this; the pipeline may not publish on violation.

Never weaken a check to make a build pass. Fix the data or the renderer.

Exit code 0 = green. Nonzero = violations printed one per line as
  RULE<N> <where>: <what>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

EMPTY_REASONS = {
    "not published",
    "not evaluated",
    "settling",
    "withheld",
    "source down (last-good shown)",
}

# Rule 7's named integrity conditions (substring match against cell flags).
INTEGRITY_MARKERS = ("record gaming", "modified harness", "withheld disclosure")

# Rule 5 families: these comparability-set prefixes may never meet.
PRO_PREFIX = "swe-bench-pro"
VERIFIED_PREFIX = "swe-bench-verified"

# Rule 12 banned content. Name ban applies to the built page (RISK-001 covers
# the commissioning brief in governance/). Credentials + email banned repo-wide.
PAGE_BANNED = [
    re.compile(r"\bBrant\b"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
]
REPO_BANNED = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

# Repo-wide personal-contact scan: any email address is banned unless the
# domain is on the infrastructure allowlist. Deliberately generic so the
# linter never has to contain the personal string it exists to keep out.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
EMAIL_DOMAIN_ALLOWLIST = {"anthropic.com", "users.noreply.github.com", "example.com"}

TAPE_WINDOW_HOURS = 78  # "~72 hours" with slack for date-granularity entries


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def load_sources_ledger(path: Path):
    """Parse SOURCES.md into {source_id: {url, method, retrieved}}."""
    ledger = {}
    if not path.exists():
        return ledger
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+(S\d+)\b", line)
        if m:
            current = m.group(1)
            ledger[current] = {"url": None, "method": None, "retrieved": None}
            continue
        if current:
            lm = re.match(r"^-\s*(URL|Method|Retrieved-at):\s*(.+)$", line)
            if lm:
                ledger[current][lm.group(1).split("-")[0].lower()] = lm.group(2).strip()
    return ledger


def iter_cells(snap):
    for metric_id, row in snap.get("cells", {}).items():
        for model_id, cell in row.items():
            yield metric_id, model_id, cell


def is_populated(cell) -> bool:
    return cell.get("value") is not None


def integrity_flags(cell):
    return [
        f
        for f in cell.get("flags", [])
        if any(marker in f.lower() for marker in INTEGRITY_MARKERS)
    ]


def compute_chips(snap):
    """Recompute which cells legitimately hold a lead chip.

    Contract (rules 4 + 10, ratified in ADR-001): a chip marks the leader within
    a single declared comparability set, computed ONLY over independent (I),
    populated, non-stale numeric cells. Vendor-claimed values never compete.
    Ties: all tied leaders chip (Phase 3 may tighten). Metrics with
    direction "none" never chip.
    """
    chips = set()
    for metric_id, meta in snap.get("metrics", {}).items():
        direction = meta.get("direction", "none")
        if direction not in ("higher", "lower"):
            continue
        row = snap.get("cells", {}).get(metric_id, {})
        candidates = {}
        for model_id, cell in row.items():
            if not is_populated(cell) or cell.get("tag") != "I" or cell.get("stale"):
                continue
            v = cell.get("value")
            if not isinstance(v, (int, float)):
                continue
            if cell.get("comparability_set") != meta.get("comparability_set"):
                continue  # off-set cells never compete (rule 4)
            candidates[model_id] = v
        if not candidates:
            continue
        best = max(candidates.values()) if direction == "higher" else min(candidates.values())
        for model_id, v in candidates.items():
            if v == best:
                chips.add(f"{metric_id}.{model_id}")
    return chips


def check_snapshot(snap, snap_name, ledger):
    v = []
    gen = parse_iso(snap["generated_at"])
    metrics = snap.get("metrics", {})
    model_ids = set(snap.get("models", {}).keys())
    cell_ids = set()

    for metric_id, model_id, cell in iter_cells(snap):
        cid = f"{metric_id}.{model_id}"
        cell_ids.add(cid)
        where = f"{snap_name}:{cid}"
        meta = metrics.get(metric_id)
        if meta is None:
            v.append(f"SCHEMA {where}: cell references undeclared metric")
            continue
        if model_id not in model_ids:
            v.append(f"SCHEMA {where}: cell references undeclared model")
        if cell.get("comparability_set") != meta.get("comparability_set"):
            v.append(
                f"RULE4 {where}: cell comparability_set "
                f"{cell.get('comparability_set')!r} != metric set "
                f"{meta.get('comparability_set')!r}"
            )
        if is_populated(cell):
            # Rule 1
            if cell.get("tag") not in ("I", "V"):
                v.append(f"RULE1 {where}: populated cell lacks I/V provenance tag")
            # Rule 2
            sid = cell.get("source_id")
            if not sid or not re.fullmatch(r"S\d+", str(sid)):
                v.append(f"RULE2 {where}: populated cell lacks numbered source id")
            elif sid not in ledger:
                v.append(f"RULE2 {where}: source id {sid} not in SOURCES.md ledger")
            else:
                entry = ledger[sid]
                if not entry.get("url") or not entry.get("method") or not entry.get("retrieved"):
                    v.append(
                        f"RULE2 {where}: ledger entry {sid} missing URL/method/retrieved-at"
                    )
            if not cell.get("retrieved_at"):
                v.append(f"RULE2 {where}: populated cell lacks retrieved_at")
            else:
                # Rule 9 (data side): stale must be truthful vs the SLA
                sla = meta.get("freshness_sla_hours")
                if sla:
                    age = gen - parse_iso(cell["retrieved_at"])
                    if age > timedelta(hours=sla) and not cell.get("stale"):
                        v.append(
                            f"RULE9 {where}: value is {age} old (SLA {sla}h) but not marked stale"
                        )
            # Rule 6
            if "arc-agi" in metric_id and not cell.get("effort_tier"):
                v.append(f"RULE6 {where}: ARC-AGI value without effort tier")
        else:
            # Rule 3
            reason = cell.get("empty_reason")
            if reason not in EMPTY_REASONS:
                v.append(
                    f"RULE3 {where}: empty cell reason {reason!r} not in enum {sorted(EMPTY_REASONS)}"
                )

    # Rule 5 (data side): no metric row mixes Pro and Verified sets
    for metric_id, meta in metrics.items():
        sets_in_row = {
            c.get("comparability_set")
            for c in snap.get("cells", {}).get(metric_id, {}).values()
        } | {meta.get("comparability_set")}
        has_pro = any(s and s.startswith(PRO_PREFIX) for s in sets_in_row)
        has_ver = any(s and s.startswith(VERIFIED_PREFIX) for s in sets_in_row)
        if has_pro and has_ver:
            v.append(f"RULE5 {snap_name}:{metric_id}: row mixes SWE-bench Pro and Verified")

    # Rule 8: tape entries dated, in-window, sourced
    for i, entry in enumerate(snap.get("tape", [])):
        where = f"{snap_name}:tape[{i}]"
        d = entry.get("date")
        if not d:
            v.append(f"RULE8 {where}: tape entry has no date")
        else:
            day = datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
            if gen - day > timedelta(hours=TAPE_WINDOW_HOURS):
                v.append(f"RULE8 {where}: tape entry dated {d} is outside ~72h of build time")
            if day - gen > timedelta(hours=26):
                v.append(f"RULE8 {where}: tape entry dated {d} is in the future")
        sid = entry.get("source_id")
        if not sid or sid not in ledger:
            v.append(f"RULE8 {where}: tape entry source id {sid!r} unresolved")
        for cid in entry.get("cell_ids", []):
            if cid not in cell_ids:
                v.append(f"RULE8 {where}: tape cites unknown cell {cid}")

    # Rule 11: implications
    for i, imp in enumerate(snap.get("implications", [])):
        where = f"{snap_name}:implications[{i}]"
        if imp.get("tag") != "X":
            v.append(f"RULE11 {where}: implication not tagged X")
        cites = imp.get("cites", [])
        if not cites:
            v.append(f"RULE11 {where}: implication cites no cells")
        unknown = [c for c in cites if c not in cell_ids]
        if unknown:
            v.append(f"RULE11 {where}: implication cites unknown cells {unknown}")
        if imp.get("confidence") not in ("high", "med", "low"):
            v.append(f"RULE11 {where}: confidence {imp.get('confidence')!r} invalid")
        if not (imp.get("falsifier") or "").strip():
            v.append(f"RULE11 {where}: implication states no falsifier")
        # Rule 5 (implication side)
        cited_sets = set()
        for c in cites:
            m_id, _, mo_id = c.partition(".")
            cell = snap.get("cells", {}).get(m_id, {}).get(mo_id)
            if cell:
                cited_sets.add(cell.get("comparability_set"))
        if any(s and s.startswith(PRO_PREFIX) for s in cited_sets) and any(
            s and s.startswith(VERIFIED_PREFIX) for s in cited_sets
        ):
            v.append(f"RULE5 {where}: implication mixes SWE-bench Pro and Verified")
        # Rule 7 (propagation side): integrity flags on cited cells must be carried
        carried = set(imp.get("flags_carried", []))
        for c in cites:
            m_id, _, mo_id = c.partition(".")
            cell = snap.get("cells", {}).get(m_id, {}).get(mo_id)
            if cell:
                for f in integrity_flags(cell):
                    if f not in carried:
                        v.append(
                            f"RULE7 {where}: cites flagged cell {c} without carrying flag {f!r}"
                        )
    return v


TAG_RE = re.compile(r"<[a-zA-Z][^>]*>")


def html_tag_attrs(tag_html):
    return dict(re.findall(r'([a-zA-Z0-9_-]+)="([^"]*)"', tag_html))


def check_html(html_path: Path, snap, ledger):
    """HTML-side checks. The renderer's contract: every rendered cell element
    carries data-cell-id / data-tag / data-stale / data-warn / data-chip /
    data-set attributes; tape items carry data-tape-date / data-tape-src;
    implications carry data-imp-tag / data-imp-conf / data-imp-falsifier."""
    v = []
    if not html_path.exists():
        return v  # build-time check runs after render; absence handled by make
    html = html_path.read_text(encoding="utf-8")
    name = html_path.name

    # Index rendered cell elements
    rendered = {}
    for tag in TAG_RE.findall(html):
        attrs = html_tag_attrs(tag)
        if "data-cell-id" in attrs:
            rendered[attrs["data-cell-id"]] = attrs

    chips_expected = compute_chips(snap)

    for metric_id, model_id, cell in iter_cells(snap):
        cid = f"{metric_id}.{model_id}"
        attrs = rendered.get(cid)
        if attrs is None:
            continue  # not every cell must render (Phase 3 may cut rows)
        where = f"{name}:{cid}"
        if is_populated(cell):
            if attrs.get("data-tag") != cell.get("tag"):
                v.append(f"RULE1 {where}: rendered tag {attrs.get('data-tag')!r} != data tag")
        else:
            if attrs.get("data-empty-reason") not in EMPTY_REASONS:
                v.append(f"RULE3 {where}: rendered empty cell lacks enum reason (blank is silent)")
        # Rule 7: integrity-flagged cells must render a visible warning tag
        if integrity_flags(cell) and attrs.get("data-warn") != "1":
            v.append(f"RULE7 {where}: integrity-flagged cell rendered without warning tag")
        # Rule 9: stale cells must render a staleness badge
        if cell.get("stale") and attrs.get("data-stale") != "1":
            v.append(f"RULE9 {where}: stale cell rendered without staleness badge")
        # Rules 4 + 10: chips
        if attrs.get("data-chip") == "1":
            if cid not in chips_expected:
                if cell.get("tag") == "V":
                    v.append(f"RULE10 {where}: vendor-claimed cell rendered with a lead chip")
                else:
                    v.append(f"RULE4 {where}: chip rendered outside computed comparability leaders")
            if attrs.get("data-set") != cell.get("comparability_set"):
                v.append(f"RULE4 {where}: chip element set mismatch")

    # Rule 4: chips must use shape + label, never color alone
    for m in re.finditer(r'<[^>]*data-chip="1"[^>]*>', html):
        seg = html[m.start() : m.start() + 600]
        if "chip-glyph" not in seg or "chip-label" not in seg:
            v.append(f"RULE4 {name}: chip without shape glyph + text label near byte {m.start()}")

    # Rule 5 (render side): no single row element mixes the two families
    for m in re.finditer(r'<tr[^>]*data-row-set="([^"]*)"[^>]*>', html):
        s = m.group(1)
        if PRO_PREFIX in s and VERIFIED_PREFIX in s:
            v.append(f"RULE5 {name}: rendered row mixes Pro and Verified sets")

    # Rule 8 (render side): tape items carry date + source
    for m in re.finditer(r"<[^>]*data-tape-item[^>]*>", html):
        attrs = html_tag_attrs(m.group(0))
        if not attrs.get("data-tape-date"):
            v.append(f"RULE8 {name}: tape item without date")
        if not attrs.get("data-tape-src"):
            v.append(f"RULE8 {name}: tape item without source id")

    # Rule 11 (render side)
    for m in re.finditer(r"<[^>]*data-imp-id[^>]*>", html):
        attrs = html_tag_attrs(m.group(0))
        if attrs.get("data-imp-tag") != "X":
            v.append(f"RULE11 {name}: implication element not tagged X")
        if not attrs.get("data-imp-conf"):
            v.append(f"RULE11 {name}: implication element without confidence")

    # Rule 12 (page side)
    for pat in PAGE_BANNED + REPO_BANNED:
        if pat.search(html):
            v.append(f"RULE12 {name}: banned pattern {pat.pattern!r} present in page")
    return v


def check_repo_hygiene():
    """Rule 12 repo side: no credentials or personal email anywhere tracked."""
    v = []
    skip_dirs = {".git", "raw", "__pycache__", ".pytest_cache", "node_modules"}
    for p in REPO.rglob("*"):
        if p.is_dir() or any(part in skip_dirs for part in p.parts):
            continue
        if p.suffix in {".png", ".jpg", ".woff", ".woff2", ".ico", ".gz", ".zip"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pat in REPO_BANNED:
            if pat.search(text) and p.name != "check_invariants.py":
                v.append(f"RULE12 {p.relative_to(REPO)}: banned pattern {pat.pattern!r}")
        for m in EMAIL_RE.finditer(text):
            if m.group(1).lower() not in EMAIL_DOMAIN_ALLOWLIST:
                v.append(
                    f"RULE12 {p.relative_to(REPO)}: personal email address present "
                    f"(domain {m.group(1)})"
                )
    return v


def check_explainability(snapshots):
    """Every changed cell between consecutive dated snapshots must appear in the
    newer snapshot's tape cell_ids or changelog."""
    v = []
    dated = sorted(
        (name, s) for name, s in snapshots.items() if re.match(r"\d{4}-\d{2}-\d{2}", name)
    )
    for (older_name, older), (newer_name, newer) in zip(dated, dated[1:]):
        explained = set()
        for entry in newer.get("tape", []):
            explained.update(entry.get("cell_ids", []))
        for entry in newer.get("changelog", []):
            if isinstance(entry, dict):
                explained.update(entry.get("cell_ids", []))
                if "cell_id" in entry:
                    explained.add(entry["cell_id"])
        for metric_id, model_id, cell in iter_cells(newer):
            cid = f"{metric_id}.{model_id}"
            old_cell = older.get("cells", {}).get(metric_id, {}).get(model_id)
            if old_cell is None:
                continue  # new row/model: noted via tape/watch conventions, checked elsewhere
            if old_cell.get("value") != cell.get("value") and cid not in explained:
                v.append(
                    f"EXPLAIN {older_name}->{newer_name}:{cid}: value changed "
                    f"({old_cell.get('value')!r} -> {cell.get('value')!r}) but appears in "
                    "neither tape nor changelog"
                )
    return v


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(REPO / "data"))
    ap.add_argument("--html", default=str(REPO / "docs" / "model-eval-monitor.html"))
    ap.add_argument("--sources", default=str(REPO / "governance" / "SOURCES.md"))
    ap.add_argument("--snapshot", help="lint a single snapshot file only")
    args = ap.parse_args(argv)

    ledger = load_sources_ledger(Path(args.sources))
    violations = []

    if args.snapshot:
        p = Path(args.snapshot)
        snap = json.loads(p.read_text(encoding="utf-8"))
        violations += check_snapshot(snap, p.name, ledger)
    else:
        snapshots = {}
        data_dir = Path(args.data_dir)
        for p in sorted(data_dir.glob("*.json")):
            try:
                snapshots[p.stem.replace(".seed", "")] = json.loads(
                    p.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as e:
                violations.append(f"SCHEMA {p.name}: invalid JSON ({e})")
        for name, snap in snapshots.items():
            if name == "latest":
                continue  # copy of a dated snapshot; linted under its date
            violations += check_snapshot(snap, name, ledger)
        latest = snapshots.get("latest")
        if latest is not None:
            violations += check_snapshot(latest, "latest", ledger)
            violations += check_html(Path(args.html), latest, ledger)
        violations += check_explainability(snapshots)
        violations += check_repo_hygiene()

    if violations:
        print(f"INVARIANT LINTER: {len(violations)} violation(s)", file=sys.stderr)
        for viol in violations:
            print(f"  {viol}", file=sys.stderr)
        return 1
    print("invariant linter: all 12 constitutional rules green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
