# Red-team gate — Phase 5 (implications layer)

Run 2026-08-01 as part of the combined gate. Full attack text:
`phase-4-5-report.md`; independent rot demonstration also in
`phase-6-7-report.md` (Part 2, first BLOCKING). Dispositions below.

## Findings and dispositions

- **BLOCKING — IMP-1 single-evaluator overclaim** ("Opus 5 leads the
  frontier … confidence high" from two same-evaluator boards while Epoch,
  LiveBench, Vals and Arena rank differently on the same page; falsifier
  gerrymandered to AA-only observations; "largest top gap on the page" was a
  cross-set superlative). **RESOLVED**: rescoped to "leads on both
  Artificial Analysis boards — one evaluator", the cross-aggregator dissent
  is now cited in the same implication (epoch/livebench/vals cells added to
  cites), confidence high→med, the margin stated as the exact 111.74 delta,
  cross-set superlative deleted, falsifier covers both the AA flip and
  non-AA convergence.
- **BLOCKING — held-implication rot** (implications carried forward verbatim
  forever; demonstrated: cited cell moved, page still asserted the old
  number as answered/high, linter exit 0). **RESOLVED** mechanically:
  every implication pins `cite_values` at authorship; `collect()` flips any
  carried implication whose cited cells moved to `status: "under review"`
  (with `moved_cites`); the renderer badges it "UNDER REVIEW — cited cells
  moved"; the linter fails any snapshot ≥ 2026-08-01 where drift is not so
  marked; end-to-end drill `test_drill_implication_rot_flips_to_under_review`
  (modified-fixture refit) covers pipeline + linter + both polarities.
- **MAJOR — IMP-2 false dichotomy** (posed as preference-vs-judged when
  three non-preference boards also dissent). **RESOLVED**: reframed as
  "is the AA order the outlier?" with three readings, citing the non-AA
  boards; falsifier includes their next publishes.
- **MAJOR — IMP-5 equally-supported opposite reading** (price artifact vs
  demand lanes; pre-registered by innovator §10). **RESOLVED**: converted to
  OPEN with both readings named (token share overweights cheap tokens as
  spend share overweights expensive ones), cost-per-task cells cited,
  confidence low.
- **MINOR — IMP-4 five-way superlative cited one cell**. **RESOLVED**: all
  five aa-omniscience cells cited.
- **MINOR — implication cites render inert** (no one-tap verification).
  **DEFERRED** — RISK-011 rider: implement cite→row anchors if the Phase 9
  cold read flags verification friction.
- "Driver unresolved" carry convention unenforced — subsumed by the
  cite_values mechanism (a driver-resolution value change flips the citing
  implications to under review mechanically).

## Verifier criteria positions (ADR-006 records both)

- Empty-cell cites (imp-sol-integrity, imp-open-arc): legitimate when the
  emptiness IS the cited fact; rule 11 checks resolution, not population.
  The judgment validator stays stricter for machine-generated entries.
- Derived numbers in curated implications (ratios 13x/28-47x, rounded 44):
  permitted when every operand is a cited cell value; machine entries remain
  bound to the lexical no-new-facts scan. The one number outside policy
  (+112 for 111.74) was corrected to the exact delta.

## What held (attacked, survived)

IMP-3 Pareto (arithmetic + caveat verified), IMP-7 honest OPEN, IMP-8
rule-5-safe wording, all rule-7 verbatim carries exact, all falsifiers
except IMP-1's genuinely observable near-term.
