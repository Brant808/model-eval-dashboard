# EVAL — Finished-Dashboard Scorecard (2026-08-01)

Builder scores with evidence; verifier countersign appended below (Phase 9
gate). Scale 1–5. Any dimension under 4 carries a remediation note or an
accepted-risk reference.

## 1. Trustworthiness — 5

Every populated cell carries I/V + numbered source resolving to a ledger
entry with URL/method/timestamp; vendor claims quarantined in C7 with
machine-enforced VENDOR-CLAIMED bands; integrity flags render on cells AND
propagate verbatim into implications (rule 7, linter + tests); vendor values
can never chip (rule 10 + ledger independence cross-check); the quick-look
band now carries the same trust metadata, verified cell-for-cell against
the snapshot. The layer most prone to quiet lying — carried editorial —
flips mechanically to "UNDER REVIEW" when cited cells move. Evidence:
`make check` (12 rules over every snapshot + the shipped HTML), 119 tests,
three adversarial gate reports with all BLOCKING/MAJOR findings resolved.

## 2. Scannability — 4

Cold read (red-team, rendered, timed): what-moved ~15s via the dated tape;
trust semantics read without documentation; X-panel lens labels carry the
scan. Ordering C1→C7 with the fold after C4 verified rendered. Held at 4,
not 5: the X-panel is ~3 iPhone screens (accepted at gate; two entries went
OPEN which densified signal) and implication cites are inert text
(RISK-011 rider). Remediation trigger: Phase 9+ cold reads.

## 3. Freshness — 4

Daily cron + retry cron, 72h-windowed tape with carry-forward, per-metric
SLA staleness with visible badges, health footer naming every source's
state, same-day re-run safe. Held at 4: rule 9 cannot see a frozen source
that keeps serving 200s (RISK-012, trigger recorded), and the page is only
as fresh as one run/day by design.

## 4. Comparability discipline — 5

Comparability sets on every cell and enforced against metric declarations;
chips computed only within sets, shape+label, CO-LEAD ties, disclaimed and
flagged-leader exclusions; the three SWE scales are machine-separated in
rows, tape, implications (cites AND text), briefs (per-sentence), and the
rendered page prose; ARC values carry effort tiers everywhere including
editorial mentions; cross-set superlatives banned from X copy at gate;
set renames blank carried values honestly rather than re-labeling.

## 5. Implication quality — 4

All 8 X-entries: cited, confidence-labeled, falsifiable, flag-carrying,
rot-guarded via cite_values pins. The gate rewrote the three weakest (IMP-1
evaluator scoping + cited dissent; IMP-2 reframed; IMP-5 to OPEN with the
opposite reading named). Held at 4: curated prose can still age between
gates in ways value-pins don't catch (a cited cell UNCHANGED while the
world moves — e.g. a new board appearing); the mechanical layer catches
value drift only. Accepted: mechanical mode is the shipped default.

## 6. Resilience — 4

Per-source degradation with last-good + loud flags; single-source,
total-loss, clock-advance, same-day-rerun, and implication-rot drills all
green in CI against recorded fixtures through the REAL fetch path; carry
hygiene migrates old cells across constitution changes; data commits before
build/tests; failed runs upload forensics; retries env-capped in CI; page
serves last-good on any failure. Held at 4: RISK-013 (healthy-source cell
vanishing blanks same-day, no debounce) and the judgment validator's
lexical bounds (RISK-011) are accepted-with-trigger, not solved.

## 7. Access latency — 4 (provisional: human toggle pending)

Page is 30.7 KB gzipped, self-contained, opens offline from file://, 2-up
at iPhone width with no horizontal scroll, keyboard-complete, selection
persists across reloads. Held at 4 pending the two human actions this
sandbox cannot perform: the Pages toggle and the live-URL verification from
both devices (HANDOFF steps; RISK-004 blocks the push that precedes them).
Becomes 5 when https://brant808.github.io/model-eval-dashboard/ loads cold
on cellular.

## Verifier countersign

(appended by the Phase 9 verifier)
