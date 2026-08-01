#!/usr/bin/env python3
"""Invariant linter: enforces the 12 constitutional data rules (CLAUDE.md /
governance/BRIEF.md section 2) against every snapshot in data/ and the built
HTML page. `make check` runs this; the pipeline may not publish on violation.

Never weaken a check to make a build pass. Fix the data or the renderer.

Hardened after the Phase 0 red-team gate (governance/redteam/phase-0.md):
- source-ledger independence is enforced against cell tags (a vendor source can
  never yield an I-tagged cell), so rule 10 no longer trusts the tag alone;
- non-finite numbers are rejected everywhere (strict JSON parse + isfinite);
- rule 5 covers tape cell_ids and benchmark-name mentions in tape/implication
  text, not just rows and citation sets;
- a metric without a freshness SLA is itself a violation (rule 9 cannot be
  disabled by omission);
- the HTML checker parses with html.parser (quote-agnostic), rejects duplicate
  or fabricated cell ids, and verifies displayed value text against the data;
- chips require >=2 independent competitors; mixed numeric/text values in a
  direction-bearing metric are a violation;
- explainability covers removed and newly-appearing cells, not just changes;
- in full-run mode latest.json older than MAX_LATEST_AGE_HOURS fails loudly
  (set CHECK_ALLOW_OLD_LATEST=1 for deliberate offline replays);
- malformed snapshots become SCHEMA violations instead of tracebacks.

Exit code 0 = green. Nonzero = violations printed one per line.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import math
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
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
# Phase 2 gate additions: "self-report" (vendor claims render warn-class, not
# note-class) and "proxy-model measurement" (a value measured on a different
# model than the column it sits in).
INTEGRITY_MARKERS = (
    "record gaming",
    "modified harness",
    "withheld disclosure",
    "self-report",
    "proxy-model measurement",
)

# Rule 5 families: these may never meet in a row, comparison, chip set, tape
# entry, or implication sentence. Phase 2 gate: SWE-rebench is a THIRD scale
# that must never be conflated with either SWE-bench family.
PRO_PREFIX = "swe-bench-pro"
VERIFIED_PREFIX = "swe-bench-verified"
REBENCH_PREFIX = "swe-rebench"
PRO_NAME_RE = re.compile(r"swe.?bench\s+pro", re.IGNORECASE)
VERIFIED_NAME_RE = re.compile(r"swe.?bench\s+verified", re.IGNORECASE)
REBENCH_NAME_RE = re.compile(r"swe.?rebench", re.IGNORECASE)

# Derived metrics: metric_id -> (numerator metric, denominator metric,
# rounding digits). Cells of these metrics must declare derived_from parents;
# the linter recomputes the value and enforces worst-parent staleness and
# integrity-flag inheritance (Phase 2 gate, derived-cell convention).
DERIVATIONS = {
    "intelligence-per-dollar": ("aa-index", "cost-per-task", 1),
}

# Rule 12 banned content. Name ban applies to the built page (RISK-001 covers
# the commissioning brief in governance/). Credentials banned repo-wide.
PAGE_BANNED = [
    re.compile(r"\bbrant\b", re.IGNORECASE),
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
# Applied to whitespace-collapsed text so line-split addresses are caught too.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
EMAIL_DOMAIN_ALLOWLIST = {"anthropic.com", "users.noreply.github.com", "example.com"}

TAPE_WINDOW_HOURS = 78  # "~72 hours" back-window with slack for date-granularity entries
MAX_LATEST_AGE_HOURS = 54  # full-run rot guard: daily cadence + slack

# The linter itself is exempt from the credential-pattern scan (it contains the
# patterns) — by exact repo-relative path only, so a stray copy elsewhere is
# still scanned.
HYGIENE_EXEMPT_PATHS = {"tools/check_invariants.py"}


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _reject_nonfinite_const(name):
    raise ValueError(f"non-finite JSON constant {name!r} is banned in snapshots")


def load_json_strict(path: Path):
    """JSON load that refuses NaN/Infinity (they silently corrupt chips)."""
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_nonfinite_const)


# Cells in snapshots dated on/after this date must carry their source's
# declared caveat flags (the seed of 2026-07-31 is a frozen historical baseline
# and is grandfathered; everything the pipeline produces is not).
CAVEAT_ENFORCE_FROM = "2026-08-01"


def load_sources_ledger(path: Path):
    """Parse SOURCES.md into
    {source_id: {url, method, retrieved, independence, sunset, caveat_flags}}.

    Machine-read lines (Phase 1 gate hardening):
    - Independence: value starting 'vendor' => cells citing it must be tagged V;
      'independent' => I or V allowed; anything else is neutral.
    - Sunset: YYYY-MM-DD => no snapshot dated after this may cite the source
      (used to retire refuted sources like S6 without rewriting the seed).
    - Caveat-flags: semicolon-separated flags, each optionally scoped with
      '@metric-prefix'. Every populated cell citing the source (in snapshots
      dated >= CAVEAT_ENFORCE_FROM, within scope) must carry the flag verbatim
      in its flags[] so the page renders the caveat (rule 7 at source level).
    """
    ledger = {}
    if not path.exists():
        return ledger
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+(S\d+)\b", line)
        if m:
            current = m.group(1)
            ledger[current] = {
                "url": None,
                "method": None,
                "retrieved": None,
                "independence": "neutral",
                "sunset": None,
                "caveat_flags": [],
            }
            continue
        if current:
            lm = re.match(r"^-\s*(URL|Method|Retrieved-at|Independence|Sunset|Caveat-flags):\s*(.+)$", line)
            if lm:
                key = lm.group(1).lower()
                val = lm.group(2).strip()
                if key == "retrieved-at":
                    ledger[current]["retrieved"] = val
                elif key == "independence":
                    low = val.lower()
                    if low.startswith("vendor"):
                        ledger[current]["independence"] = "vendor"
                    elif low.startswith("independent"):
                        ledger[current]["independence"] = "independent"
                    else:
                        ledger[current]["independence"] = "neutral"
                elif key == "sunset":
                    dm = re.match(r"\d{4}-\d{2}-\d{2}", val)
                    ledger[current]["sunset"] = dm.group(0) if dm else val
                elif key == "caveat-flags":
                    flags = []
                    for part in val.split(";"):
                        part = part.strip()
                        if not part:
                            continue
                        if "@" in part:
                            flag, _, scope = part.rpartition("@")
                            flags.append((flag.strip(), scope.strip()))
                        else:
                            flags.append((part, ""))
                    ledger[current]["caveat_flags"] = flags
                else:
                    ledger[current][key] = val
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


def _mentions_both_families(text: str) -> bool:
    """True if the text co-mingles two or more of the three SWE scales."""
    hits = sum(
        1
        for pat in (PRO_NAME_RE, VERIFIED_NAME_RE, REBENCH_NAME_RE)
        if pat.search(text)
    )
    return hits >= 2


def _family_of(set_name):
    if not set_name:
        return None
    if set_name.startswith(REBENCH_PREFIX):
        return "rebench"
    if set_name.startswith(PRO_PREFIX):
        return "pro"
    if set_name.startswith(VERIFIED_PREFIX):
        return "verified"
    return None


def compute_chips(snap):
    """Recompute which cells legitimately hold a lead chip.

    Contract (rules 4 + 10, ADR-001 as tightened by the Phase 2 gate ADR-004):
    a chip marks the leader within a single declared comparability set,
    computed over independent (I), populated, non-stale, finite-numeric cells
    that share the metric's set. Vendor-claimed values never compete.
    Two integrity refinements (Phase 2 gate, BLOCKING B1):
    - a cell whose VALUE its own publisher disclaims (`value_disclaimed: true`,
      e.g. METR's Sol figure) neither wins nor counts as competition — a
      superlative must not be manufactured from disclaimed data;
    - a cell carrying integrity flags may count as competition (its value is
      sound; the flag warns about context) but may never WIN; and if the true
      leader is integrity-flagged, NO chip is awarded for that metric (crowning
      second place would lie about the max).
    Metrics may opt out entirely via meta chip_eligible: false (e.g.
    provider-level aggregates rendered in model columns). A lead requires
    COMPETITION: fewer than 2 eligible candidates -> no chip. Ties: all tied
    leaders chip (rendered as CO-LEAD when more than one — Phase 3).
    Metrics with direction "none" never chip.
    """
    chips = set()
    for metric_id, meta in snap.get("metrics", {}).items():
        direction = meta.get("direction", "none")
        if direction not in ("higher", "lower"):
            continue
        if meta.get("chip_eligible") is False:
            continue
        row = snap.get("cells", {}).get(metric_id, {})
        candidates = {}
        for model_id, cell in row.items():
            if not is_populated(cell) or cell.get("tag") != "I" or cell.get("stale"):
                continue
            if cell.get("value_disclaimed"):
                continue  # publisher-disclaimed values cannot compete at all
            v = cell.get("value")
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
                continue
            if cell.get("comparability_set") != meta.get("comparability_set"):
                continue  # off-set cells never compete (rule 4)
            candidates[model_id] = (v, bool(integrity_flags(cell)))
        if len(candidates) < 2:
            continue  # a "lead" over nobody is a misleading superlative
        values = [v for v, _ in candidates.values()]
        best = max(values) if direction == "higher" else min(values)
        leaders = {m: flagged for m, (v, flagged) in candidates.items() if v == best}
        if any(leaders.values()):
            continue  # true leader is integrity-flagged: no chip at all
        for model_id in leaders:
            chips.add(f"{metric_id}.{model_id}")
    return chips


def check_snapshot(snap, snap_name, ledger):
    v = []
    gen = parse_iso(snap["generated_at"])
    snap_date = snap.get("snapshot_date", "")
    metrics = snap.get("metrics", {})
    model_ids = set(snap.get("models", {}).keys())
    cell_ids = set()

    # Rule 9 precondition: every metric must declare a positive freshness SLA —
    # omission would silently disable staleness checking.
    for metric_id, meta in metrics.items():
        sla = meta.get("freshness_sla_hours")
        if not isinstance(sla, (int, float)) or isinstance(sla, bool) or not math.isfinite(sla) or sla <= 0:
            v.append(
                f"RULE9 {snap_name}:{metric_id}: metric lacks a positive freshness_sla_hours "
                f"(got {sla!r}) — staleness checking would be silently disabled"
            )

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
            val = cell.get("value")
            if isinstance(val, float) and not math.isfinite(val):
                v.append(f"SCHEMA {where}: non-finite value {val!r}")
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
                # Rule 10 hardening: the tag must be consistent with the
                # source's declared independence — a vendor source can never
                # produce an I-tagged (chip-eligible) cell.
                if entry.get("independence") == "vendor" and cell.get("tag") == "I":
                    v.append(
                        f"RULE10 {where}: cell cites vendor source {sid} but is tagged I "
                        "(vendor values must be V and never compete for chips)"
                    )
                # Source sunset: a retired/refuted source may not feed any
                # snapshot dated after its sunset date (Phase 1 gate, BLOCKING).
                sunset = entry.get("sunset")
                if sunset and snap_date and snap_date > sunset:
                    v.append(
                        f"RULE2 {where}: source {sid} was sunset on {sunset} and may not "
                        "be cited by newer snapshots"
                    )
                # Source-level caveat flags must reach the cell (rule 7 at the
                # source level) for all post-baseline snapshots.
                if snap_date and snap_date >= CAVEAT_ENFORCE_FROM:
                    for flag, scope in entry.get("caveat_flags", []):
                        if scope and not metric_id.startswith(scope):
                            continue
                        if flag not in cell.get("flags", []):
                            v.append(
                                f"RULE7 {where}: cell cites {sid} but does not carry its "
                                f"declared caveat flag {flag!r}"
                            )
            if not cell.get("retrieved_at"):
                v.append(f"RULE2 {where}: populated cell lacks retrieved_at")
            else:
                # Rule 9 (data side): stale must be truthful vs the SLA
                sla = meta.get("freshness_sla_hours")
                if isinstance(sla, (int, float)) and not isinstance(sla, bool) and sla > 0:
                    age = gen - parse_iso(cell["retrieved_at"])
                    if age > timedelta(hours=sla) and not cell.get("stale"):
                        v.append(
                            f"RULE9 {where}: value is {age} old (SLA {sla}h) but not marked stale"
                        )
            # Rule 6
            if "arc-agi" in metric_id and not cell.get("effort_tier"):
                v.append(f"RULE6 {where}: ARC-AGI value without effort tier")
            # Phase 3 gate: a populated V cell in a vendor-claims family set
            # must carry a warn-class integrity marker — claim cells may never
            # render with note-class-only treatment. (Seed grandfathered, like
            # the caveat rule.)
            cset = cell.get("comparability_set") or ""
            if (
                snap_date
                and snap_date >= CAVEAT_ENFORCE_FROM
                and cell.get("tag") == "V"
                and ("self-report" in cset or "vendor" in cset)
                and not integrity_flags(cell)
            ):
                v.append(
                    f"RULE7 {where}: vendor-claim cell (set {cset!r}) carries no "
                    "warn-class integrity marker"
                )
            # Derived cells (Phase 2 gate): parents declared, value recomputed,
            # worst-parent staleness, integrity flags inherited.
            if metric_id in DERIVATIONS:
                num_m, den_m, digits = DERIVATIONS[metric_id]
                parents = cell.get("derived_from") or []
                want = [f"{num_m}.{model_id}", f"{den_m}.{model_id}"]
                if parents != want:
                    v.append(
                        f"RULE4 {where}: derived cell must declare derived_from {want}, "
                        f"got {parents}"
                    )
                else:
                    pn = snap.get("cells", {}).get(num_m, {}).get(model_id)
                    pd = snap.get("cells", {}).get(den_m, {}).get(model_id)
                    if not pn or not pd or not is_populated(pn) or not is_populated(pd):
                        v.append(f"RULE4 {where}: derived cell has unpopulated parent(s)")
                    else:
                        nv, dv = pn.get("value"), pd.get("value")
                        if isinstance(nv, (int, float)) and isinstance(dv, (int, float)) and dv:
                            expect = round(nv / dv, digits)
                            got = cell.get("value")
                            if not isinstance(got, (int, float)) or abs(got - expect) > 0.51 * 10 ** -digits + 1e-9:
                                v.append(
                                    f"RULE4 {where}: derived value {got!r} != recomputed "
                                    f"{expect!r} from parents"
                                )
                        parent_stale = bool(pn.get("stale")) or bool(pd.get("stale"))
                        if bool(cell.get("stale")) != parent_stale:
                            v.append(
                                f"RULE9 {where}: derived cell stale={cell.get('stale')} but "
                                f"OR(parents.stale)={parent_stale}"
                            )
                        inherit = integrity_flags(pn) + integrity_flags(pd) + [
                            f for f in (pn.get("flags", []) + pd.get("flags", []))
                            if "unresolved" in f.lower()
                        ]
                        for pf in inherit:
                            if pf not in cell.get("flags", []):
                                v.append(
                                    f"RULE7 {where}: derived cell missing inherited parent "
                                    f"flag {pf!r} (integrity + movement caveats propagate)"
                                )
        else:
            # Rule 3
            reason = cell.get("empty_reason")
            if reason not in EMPTY_REASONS:
                v.append(
                    f"RULE3 {where}: empty cell reason {reason!r} not in enum {sorted(EMPTY_REASONS)}"
                )

    # Rule 4: a direction-bearing metric must not mix numeric and text values —
    # a lone parsed number among strings would win an uncontested chip.
    for metric_id, meta in metrics.items():
        if meta.get("direction") not in ("higher", "lower"):
            continue
        kinds = set()
        for cell in snap.get("cells", {}).get(metric_id, {}).values():
            if not is_populated(cell):
                continue
            val = cell.get("value")
            numeric = isinstance(val, (int, float)) and not isinstance(val, bool)
            kinds.add("numeric" if numeric else "text")
        if kinds == {"numeric", "text"}:
            v.append(
                f"RULE4 {snap_name}:{metric_id}: direction-bearing metric mixes numeric and "
                "text values — chip competition would be distorted"
            )

    # Rule 5 (data side): no metric row mixes any two of the three SWE scales
    for metric_id, meta in metrics.items():
        sets_in_row = {
            c.get("comparability_set")
            for c in snap.get("cells", {}).get(metric_id, {}).values()
        } | {meta.get("comparability_set")}
        families = {f for f in (_family_of(s) for s in sets_in_row) if f}
        if len(families) >= 2:
            v.append(
                f"RULE5 {snap_name}:{metric_id}: row mixes SWE scales {sorted(families)}"
            )

    def cited_sets(ids):
        out = set()
        for c in ids:
            m_id, _, mo_id = c.partition(".")
            cell = snap.get("cells", {}).get(m_id, {}).get(mo_id)
            if cell:
                out.add(cell.get("comparability_set"))
        return out

    def mixes_families(sets_):
        return len({f for f in (_family_of(s) for s in sets_) if f}) >= 2

    # Rule 8: tape entries dated, in-window, sourced; rule 5 on tape too
    for i, entry in enumerate(snap.get("tape", [])):
        where = f"{snap_name}:tape[{i}]"
        d = entry.get("date")
        if not d:
            v.append(f"RULE8 {where}: tape entry has no date")
        else:
            try:
                day = datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
            except ValueError:
                v.append(f"RULE8 {where}: tape entry date {d!r} is not ISO formatted")
                day = None
            if day is not None:
                if gen - day > timedelta(hours=TAPE_WINDOW_HOURS):
                    v.append(f"RULE8 {where}: tape entry dated {d} is outside ~72h of build time")
                if snap_date and d > snap_date:
                    v.append(f"RULE8 {where}: tape entry dated {d} is after snapshot date {snap_date}")
        sid = entry.get("source_id")
        if not sid or sid not in ledger:
            v.append(f"RULE8 {where}: tape entry source id {sid!r} unresolved")
        elif ledger[sid].get("sunset") and snap_date and snap_date > ledger[sid]["sunset"]:
            v.append(f"RULE8 {where}: tape cites sunset source {sid}")
        for cid in entry.get("cell_ids", []):
            if cid not in cell_ids:
                v.append(f"RULE8 {where}: tape cites unknown cell {cid}")
        if mixes_families(cited_sets(entry.get("cell_ids", []))):
            v.append(f"RULE5 {where}: tape entry cites both SWE-bench Pro and Verified cells")
        if _mentions_both_families(entry.get("text", "")):
            v.append(f"RULE5 {where}: tape entry text compares SWE-bench Pro with Verified")

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
        # Rule 5 (implication side): citations AND sentence text
        if mixes_families(cited_sets(cites)):
            v.append(f"RULE5 {where}: implication mixes SWE-bench Pro and Verified")
        if _mentions_both_families(imp.get("text", "")):
            v.append(f"RULE5 {where}: implication text compares SWE-bench Pro with Verified")
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
        # Rot detection (phase-4/5/7 gate, red-team BLOCKING): a carried
        # implication whose cited cells moved since it was stated is a stale
        # editorial claim presented as current — the rule-9 sin at the X
        # layer. Every implication pins the values it was stated against;
        # any drift forces the visible "under review" state.
        if snap_date and snap_date >= CAVEAT_ENFORCE_FROM:
            pinned = imp.get("cite_values")
            if not isinstance(pinned, dict):
                v.append(f"RULE11 {where}: implication lacks cite_values pin (rot detection)")
            else:
                missing = [c for c in cites if c not in pinned]
                if missing:
                    v.append(f"RULE11 {where}: cite_values missing pins for {missing}")
                moved = []
                for c in cites:
                    if c not in pinned or c not in cell_ids:
                        continue
                    m_id, _, mo_id = c.partition(".")
                    cur = snap.get("cells", {}).get(m_id, {}).get(mo_id, {}).get("value")
                    if cur != pinned[c]:
                        moved.append(c)
                if moved and imp.get("status") != "under review":
                    v.append(
                        f"RULE11 {where}: cited cells moved since stated ({moved}) "
                        f"but status is {imp.get('status')!r}, not 'under review'"
                    )
    return v


# Sentence boundaries for rule-5 prose scans. Semicolons and mid-dots split
# too: enumerations ("TB: not published; SWE-bench Pro: not published; …")
# are independent statements, while a genuine cross-scale comparison sits
# inside one clause and still trips the check.
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?;])\s+|\s·\s")


def check_briefs(briefs_path):
    """Rule 5 on the third prose surface (phase-4/5 gate, red-team MAJOR):
    briefs ship on the page, and authorial discipline is not a contract — a
    Pro-vs-Verified comparison in brief prose rendered gate-green before this
    check existed."""
    if not briefs_path.exists():
        return []
    v = []
    briefs = load_json_strict(briefs_path)

    def walk(node, where):
        if isinstance(node, dict):
            for k, val in node.items():
                walk(val, f"{where}.{k}")
        elif isinstance(node, list):
            for i, val in enumerate(node):
                walk(val, f"{where}[{i}]")
        elif isinstance(node, str):
            for sent in _SENT_SPLIT_RE.split(node):
                if _mentions_both_families(sent):
                    v.append(
                        f"RULE5 briefs{where}: sentence compares SWE-bench scales: {sent[:90]!r}"
                    )

    walk(briefs, "")
    return v


def lint_snapshot(snap, snap_name, ledger):
    """check_snapshot wrapped so malformed data becomes a violation, not a
    traceback that aborts all remaining checks."""
    try:
        return check_snapshot(snap, snap_name, ledger)
    except (KeyError, ValueError, TypeError, AttributeError) as e:
        return [f"SCHEMA {snap_name}: snapshot malformed, checks aborted for this file ({type(e).__name__}: {e})"]


class PageIndexer(HTMLParser):
    """Indexes the rendered page: cell elements (attrs + text + chip marks),
    tape items, implication items, duplicate ids, and full visible text.
    Parser-based, so attribute quoting style cannot be used to evade checks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = []  # {id, attrs, text, chip_glyphs, chip_labels}
        self.cell_ids_seen = []
        self.tape_items = []
        self.imp_items = []
        self.text_parts = []
        self._open_cell = None
        self._cell_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self._open_cell is not None:
            self._cell_depth += 1
            klass = a.get("class", "")
            if "chip-glyph" in klass:
                self._open_cell["chip_glyphs"] += 1
            if "chip-label" in klass:
                self._open_cell["chip_labels"] += 1
        if "data-cell-id" in a and self._open_cell is None:
            self._open_cell = {
                "id": a["data-cell-id"],
                "attrs": a,
                "text": [],
                "chip_glyphs": 0,
                "chip_labels": 0,
            }
            self._cell_depth = 0
            self.cell_ids_seen.append(a["data-cell-id"])
        if "data-tape-item" in a:
            self.tape_items.append(a)
        if "data-imp-id" in a:
            self.imp_items.append(a)

    def handle_endtag(self, tag):
        if self._open_cell is not None:
            if self._cell_depth == 0:
                cell = self._open_cell
                cell["text"] = "".join(cell["text"])
                self.cells.append(cell)
                self._open_cell = None
            else:
                self._cell_depth -= 1

    def handle_data(self, data):
        self.text_parts.append(data)
        if self._open_cell is not None:
            self._open_cell["text"].append(data)


def check_html(html_path: Path, snap, ledger, require=False):
    """HTML-side checks against the renderer contract."""
    v = []
    if not html_path.exists():
        if require:
            return [f"BUILD {html_path.name}: built page missing but required (run make build first)"]
        print(f"note: {html_path} absent — HTML-side checks skipped", file=sys.stderr)
        return v
    raw = html_path.read_text(encoding="utf-8")
    name = html_path.name

    parser = PageIndexer()
    parser.feed(raw)

    # Duplicate or fabricated cell ids
    seen = set()
    for cid in parser.cell_ids_seen:
        if cid in seen:
            v.append(f"SCHEMA {name}:{cid}: duplicate rendered cell id")
        seen.add(cid)
    snap_cell_ids = {f"{m}.{mo}" for m, mo, _ in iter_cells(snap)}
    for cid in seen - snap_cell_ids:
        v.append(f"SCHEMA {name}:{cid}: rendered cell does not exist in the snapshot")

    chips_expected = compute_chips(snap)
    rendered = {c["id"]: c for c in parser.cells}

    for metric_id, model_id, cell in iter_cells(snap):
        cid = f"{metric_id}.{model_id}"
        rc = rendered.get(cid)
        if rc is None:
            continue  # not every cell must render (Phase 3 may cut rows)
        attrs, text = rc["attrs"], rc["text"]
        where = f"{name}:{cid}"
        if is_populated(cell):
            if attrs.get("data-tag") != cell.get("tag"):
                v.append(f"RULE1 {where}: rendered tag {attrs.get('data-tag')!r} != data tag")
            # Displayed value must match the data (anti-forgery, anti-drift)
            if str(cell.get("value")) not in text:
                v.append(
                    f"SCHEMA {where}: rendered text does not contain the snapshot value "
                    f"{cell.get('value')!r}"
                )
        else:
            if attrs.get("data-empty-reason") not in EMPTY_REASONS:
                v.append(f"RULE3 {where}: rendered empty cell lacks enum reason (blank is silent)")
            elif attrs["data-empty-reason"] not in text:
                v.append(f"RULE3 {where}: empty reason not visible in cell text")
        # Rule 7: integrity-flagged cells must render a visible warning tag
        if integrity_flags(cell):
            if attrs.get("data-warn") != "1":
                v.append(f"RULE7 {where}: integrity-flagged cell rendered without warning tag")
            if "⚠" not in text:
                v.append(f"RULE7 {where}: integrity-flagged cell has no visible warning marker")
        # Rule 9: stale cells must render a visible staleness badge
        if cell.get("stale"):
            if attrs.get("data-stale") != "1":
                v.append(f"RULE9 {where}: stale cell rendered without staleness attribute")
            if "STALE" not in text:
                v.append(f"RULE9 {where}: stale cell has no visible STALE badge")
        # Rules 4 + 10: chips
        if attrs.get("data-chip") == "1":
            if cid not in chips_expected:
                if cell.get("tag") == "V":
                    v.append(f"RULE10 {where}: vendor-claimed cell rendered with a lead chip")
                else:
                    v.append(f"RULE4 {where}: chip rendered outside computed comparability leaders")
            if attrs.get("data-set") != cell.get("comparability_set"):
                v.append(f"RULE4 {where}: chip element set mismatch")

    # Chip shape+label discipline, and no orphan chip visuals in non-chip cells
    for rc in parser.cells:
        where = f"{name}:{rc['id']}"
        is_chip = rc["attrs"].get("data-chip") == "1"
        if is_chip and (rc["chip_glyphs"] < 1 or rc["chip_labels"] < 1):
            v.append(f"RULE4 {where}: chip without shape glyph + text label (color alone is banned)")
        if not is_chip and (rc["chip_glyphs"] or rc["chip_labels"]):
            v.append(f"RULE4 {where}: chip visuals present on a non-chip cell (visual forgery)")

    # Rule 8 (render side): tape items carry date + source
    for a in parser.tape_items:
        if not a.get("data-tape-date"):
            v.append(f"RULE8 {name}: tape item without date")
        if not a.get("data-tape-src"):
            v.append(f"RULE8 {name}: tape item without source id")

    # Rule 11 (render side)
    for a in parser.imp_items:
        if a.get("data-imp-tag") != "X":
            v.append(f"RULE11 {name}: implication element not tagged X")
        if not a.get("data-imp-conf"):
            v.append(f"RULE11 {name}: implication element without confidence")

    # Rule 12 (page side): scan entity-decoded, whitespace-collapsed text so
    # encodings and line splits cannot hide banned content.
    flat = re.sub(r"\s+", " ", html_lib.unescape(raw))
    for pat in PAGE_BANNED + REPO_BANNED:
        if pat.search(flat):
            v.append(f"RULE12 {name}: banned pattern {pat.pattern!r} present in page")

    # Quick-look state contract (phase-6 gate BLOCKING): the ql band renders
    # from embedded JSON, invisible to the DOM checks above — a stale or
    # vendor-claimed value showed naked at the top of the page, gate-green.
    # Verify the state block cell-for-cell against the snapshot.
    m = re.search(r'<script id="state" type="application/json">(.*?)</script>', raw, re.S)
    if m:
        try:
            state_ql = json.loads(m.group(1)).get("ql", {})
        except json.JSONDecodeError:
            state_ql = None
            v.append(f"SCHEMA {name}: embedded state JSON does not parse")
        if state_ql is not None:
            for metric_id, row in state_ql.items():
                for model_id, entry in row.items():
                    cell = snap.get("cells", {}).get(metric_id, {}).get(model_id)
                    where = f"{name}:ql:{metric_id}.{model_id}"
                    if cell is None:
                        v.append(f"SCHEMA {where}: ql state entry for nonexistent cell")
                        continue
                    if not isinstance(entry, dict):
                        v.append(f"RULE9 {where}: ql entry is a bare value (no trust metadata)")
                        continue
                    if is_populated(cell):
                        if entry.get("tag") != cell.get("tag"):
                            v.append(f"RULE1 {where}: ql tag {entry.get('tag')!r} != cell tag")
                        if bool(entry.get("stale")) != bool(cell.get("stale")):
                            v.append(f"RULE9 {where}: ql staleness does not match cell (stale never presented as fresh)")
                        if bool(entry.get("warn")) != bool(integrity_flags(cell)):
                            v.append(f"RULE7 {where}: ql warn marker does not match cell integrity flags")
                    else:
                        if entry.get("v") is not None:
                            v.append(f"RULE3 {where}: ql shows a value for an empty cell")
                        elif entry.get("reason") not in EMPTY_REASONS:
                            v.append(f"RULE3 {where}: ql empty entry lacks enum reason (blank is silent)")

    # Rule 5 (page prose side, phase-4/5 gate): no sentence on the page may
    # co-mingle two SWE scales, whatever surface wrote it — brief prose
    # demonstrated a gate-green bypass before this check. Script/style bodies
    # are data (linted at the snapshot layer), and block-element boundaries
    # count as sentence breaks so adjacent rows/labels can't concatenate into
    # false positives.
    prose = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    prose = re.sub(
        r"</(?:td|th|li|p|h[1-6]|tr|div|section|details|summary|button|figcaption|dd|dt|dl)>",
        ".\n", prose, flags=re.I,
    )
    prose = html_lib.unescape(re.sub(r"<[^>]+>", " ", prose))
    for sent in _SENT_SPLIT_RE.split(prose):
        if _mentions_both_families(sent):
            clean = " ".join(sent.split())[:90]
            v.append(f"RULE5 {name}: page sentence compares SWE-bench scales: {clean!r}")
    return v


def check_repo_hygiene():
    """Rule 12 repo side: no credentials or personal email anywhere tracked."""
    v = []
    skip_dirs = {".git", "raw", "__pycache__", ".pytest_cache", "node_modules"}
    for p in REPO.rglob("*"):
        if p.is_dir() or any(part in skip_dirs for part in p.parts):
            continue
        rel = str(p.relative_to(REPO))
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        flat = re.sub(r"\s+", "", text)  # catch line-split addresses/keys
        if rel not in HYGIENE_EXEMPT_PATHS:
            for pat in REPO_BANNED:
                if pat.search(text) or pat.search(flat):
                    v.append(f"RULE12 {rel}: banned pattern {pat.pattern!r}")
        # The collapsed scan reassembles identifiers followed by decorators
        # into fake addresses in source code, so it applies to prose/data
        # files only; code files get the plain-text scan.
        sources = (text,) if p.suffix in {".py", ".js", ".sh"} else (text, flat)
        for source in sources:
            for m in EMAIL_RE.finditer(source):
                if m.group(1).lower() not in EMAIL_DOMAIN_ALLOWLIST:
                    v.append(
                        f"RULE12 {rel}: personal email address present (domain {m.group(1)})"
                    )
                    break
            else:
                continue
            break
    return v


def check_explainability(snapshots):
    """Every changed, removed, or newly-appearing cell between consecutive
    dated snapshots must appear in the newer snapshot's tape or changelog."""
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
        old_cells = {f"{m}.{mo}": c for m, mo, c in iter_cells(older)}
        new_cells = {f"{m}.{mo}": c for m, mo, c in iter_cells(newer)}
        for cid in sorted(set(old_cells) | set(new_cells)):
            if cid in explained:
                continue
            if cid not in new_cells:
                if old_cells[cid].get("value") is None:
                    continue  # an empty cell disappearing is schema churn, not data
                v.append(
                    f"EXPLAIN {older_name}->{newer_name}:{cid}: cell removed but appears in "
                    "neither tape nor changelog"
                )
            elif cid not in old_cells:
                if new_cells[cid].get("value") is None:
                    continue  # a new empty cell explains itself via empty_reason
                v.append(
                    f"EXPLAIN {older_name}->{newer_name}:{cid}: cell newly appeared but appears "
                    "in neither tape nor changelog"
                )
            elif old_cells[cid].get("value") != new_cells[cid].get("value"):
                v.append(
                    f"EXPLAIN {older_name}->{newer_name}:{cid}: value changed "
                    f"({old_cells[cid].get('value')!r} -> {new_cells[cid].get('value')!r}) "
                    "but appears in neither tape nor changelog"
                )
    return v


def check_latest_rot(latest, now=None):
    """Full-run rot guard: a frozen pipeline must fail check, not republish
    old data as fresh forever. CHECK_ALLOW_OLD_LATEST=1 permits deliberate
    offline replays (documented in RUNBOOK)."""
    if latest is None:
        return []
    if os.environ.get("CHECK_ALLOW_OLD_LATEST") == "1":
        return []
    now = now or datetime.now(timezone.utc)
    try:
        age = now - parse_iso(latest["generated_at"])
    except (KeyError, ValueError):
        return ["SCHEMA latest: generated_at missing or unparseable"]
    if age > timedelta(hours=MAX_LATEST_AGE_HOURS):
        return [
            f"ROT latest: latest.json generated_at is {age} old (max {MAX_LATEST_AGE_HOURS}h) — "
            "the pipeline has not produced fresh data; refusing to treat it as current "
            "(set CHECK_ALLOW_OLD_LATEST=1 only for deliberate offline replays)"
        ]
    return []


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
        try:
            snap = load_json_strict(p)
        except (json.JSONDecodeError, ValueError) as e:
            violations.append(f"SCHEMA {p.name}: invalid JSON ({e})")
            snap = None
        if snap is not None:
            violations += lint_snapshot(snap, p.name, ledger)
    else:
        snapshots = {}
        data_dir = Path(args.data_dir)
        snapshot_name = re.compile(r"^(\d{4}-\d{2}-\d{2}(\.seed)?|latest)\.json$")
        for p in sorted(data_dir.glob("*.json")):
            if not snapshot_name.match(p.name):
                continue  # auxiliary files (e.g. overrides.json) are not snapshots
            try:
                snapshots[p.stem.replace(".seed", "")] = load_json_strict(p)
            except (json.JSONDecodeError, ValueError) as e:
                violations.append(f"SCHEMA {p.name}: invalid JSON ({e})")
        for name, snap in snapshots.items():
            if name == "latest":
                continue  # copy of a dated snapshot; linted under its date
            violations += lint_snapshot(snap, name, ledger)
        latest = snapshots.get("latest")
        if latest is not None:
            violations += lint_snapshot(latest, "latest", ledger)
            # Phase 3 gate BLOCKING-1: latest.json must be byte-identical to the
            # newest dated snapshot — a lagging latest silently publishes
            # uncorrected data while every other check stays green.
            dated = sorted(
                p for p in data_dir.glob("*.json")
                if re.match(r"^\d{4}-\d{2}-\d{2}(\.seed)?\.json$", p.name)
            )
            if dated:
                newest = dated[-1]
                if (data_dir / "latest.json").read_bytes() != newest.read_bytes():
                    violations.append(
                        f"SYNC latest.json is not byte-identical to {newest.name} — "
                        "run make fetch before build/check"
                    )
            violations += check_html(
                Path(args.html), latest, ledger,
                require=os.environ.get("REQUIRE_HTML") == "1",
            )
            violations += check_latest_rot(latest)
        elif os.environ.get("REQUIRE_HTML") == "1":
            violations.append("BUILD latest.json missing — nothing to publish")
        violations += check_explainability(snapshots)
        violations += check_repo_hygiene()
        violations += check_briefs(data_dir / "briefs.json")

    if violations:
        print(f"INVARIANT LINTER: {len(violations)} violation(s)", file=sys.stderr)
        for viol in violations:
            print(f"  {viol}", file=sys.stderr)
        return 1
    print("invariant linter: all 12 constitutional rules green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
