# Red-team gate — Phase 4 (briefs)

Run 2026-08-01 as part of the combined Phase 4/5/6/7 gate. Full attack text:
`phase-4-5-report.md` (red-team) and `verifier-phase-4-5-7.md` (verifier,
three briefs checked sentence-by-sentence). Findings below are the Phase-4
subset with dispositions. Verifier countersign: YES, conditional — both
conditions resolved (see below).

## Findings and dispositions

- **MAJOR — rule 5 unenforced in the briefs layer** (a Pro-vs-Verified
  comparison in brief prose rendered gate-green; demonstrated).
  **RESOLVED**: `check_briefs()` lints every string in `data/briefs.json`
  per-sentence with the linter's own family regexes, and `check_html` runs a
  block-aware per-sentence family scan over the rendered page text (semicolon
  and mid-dot count as clause breaks so enumerations don't false-positive;
  `</dd>`-class boundaries prevent cross-element concatenation).
- **MAJOR — four briefs described live rows as future** ("Tracking on this
  page begins soon" against populated epoch-eci / vals-index / livebench /
  swe-rebench rows; the swe-rebench brief also claimed a GDPval stand-in the
  page no longer shows). **RESOLVED**: all four cadence sentences corrected;
  stand-in clause rewritten as a conditional fallback description; regression
  test `test_no_begins_soon_brief_for_a_populated_row` pins the class.
- **MAJOR — LiveBench Opus 5 dated before its launch** (retrieved_at =
  release date 2026-06-25 vs launch 2026-07-24 read as fabricated
  provenance). **RESOLVED**: LiveBench cells re-timestamped to fetch time
  (same convention as Epoch: living boards accrue models into dated
  releases); release date stays as comparability label + flag; brief harness
  sentence now explains the accrual.
- **MINOR — 38.3 quoted without tier statement** in the arc brief.
  **RESOLVED**: "(no declared effort tier)" added at both mentions (brief +
  IMP-6 text).
- **MINOR — orphan briefs unreachable** (aa-agentic-index, aa-halluc-rate).
  **RESOLVED**: explicit `_preregistered` allowlist in briefs.json +
  `test_every_brief_key_is_a_snapshot_metric_or_preregistered` (also fails
  when a pre-registered row goes live without leaving the allowlist).
- **MINOR — disclosure-watch partially self-citation**. **RESOLVED**: the
  brief now states the "withheld" classification is the pipeline's own
  timing inference (absence post-dates the METR flag), curated as S21.

## Verifier conditions

1. "begins soon" sentences — fixed (above).
2. ADR position on empty-cell cites and derived numbers — recorded in
   ADR-006.

Verifier mismatch A.2.7 (~270 vendor technical reports is
classification-dependent) accepted as hedged ("about", "counts drift").
