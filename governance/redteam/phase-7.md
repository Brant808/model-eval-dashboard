# Red-team gate — Phase 7 (autorefresh: collectors, pipeline, scheduler, judgment)

Run 2026-08-01. Full attack text: `phase-6-7-report.md` Part 2 (red-team,
8/8 validator bypasses demonstrated), `verifier-phase-4-5-7.md` §C/§D
(all 11 collectors reproduced against fixtures, judgment pin verified), and
`../innovator/phase-6-7-8.md` (defects D-1/D-2, riders 1–12).

## Findings and dispositions

- **BLOCKING — implication rot** (also filed under Phase 5): resolved via
  cite_values / under-review / linter rule / end-to-end drill. See
  `phase-5.md`.
- **BLOCKING — judgment validator left falsifier and flags_carried
  unvalidated** (fabricated falsifier numbers and a fabricated "record
  gaming" ⚠ accusation shipped through validated-looking channels,
  demonstrated end-to-end gate-green). **RESOLVED**: falsifier runs the same
  no-new-facts number scan; flags_carried must be a subset of the union of
  cited cells' flags (fabricated warning tags now impossible); regression
  tests added.
- **MAJOR — judgment upgrade path inert in CI** (innovator D-1: the `claude`
  CLI is never installed on the runner, so the promised secret-detect
  upgrade could never activate). **RESOLVED**: `run_model()` re-pointed at
  the Messages API over `requests` (already a dependency); the tamper pin
  now covers model id + max_tokens + prompt (LOCKED_MATERIAL).
- **MAJOR — no-new-facts validation is lexical only** (word-numbers,
  inverted orderings, cross-cell misattribution via pooled vocab, sign-flip
  deltas, vulgar fractions — 8/8 bypasses). **PARTIALLY RESOLVED /
  ACCEPTED**: signed/abs delta handling and source-id scrubbing tightened;
  the rest is RISK-011 — the validator is a number-grounding backstop, not a
  truth oracle; the mechanical default and the constitutional linter remain
  the containment. Reversal trigger recorded.
- **MAJOR — same-day rerun failed the gate** (cron + manual dispatch diffed
  today-vs-today, wiping tape/changelog; 38 EXPLAIN violations demonstrated).
  **RESOLVED**: `collect()` diffs against the newest snapshot dated BEFORE
  the run date; drill `test_drill_same_day_rerun_diffs_against_yesterday`.
- **MAJOR — tape promised ~72h but showed last-24h** (prior entries
  discarded each run; Thursday's move vanished Friday). **RESOLVED**: prior
  entries inside the 72h window carry forward, deduped; drill updated.
- **MAJOR — double reporting with judgment on** (judged + mechanical entry
  for the same cells; "no editorial layer" prefix contradicting the health
  footer). **RESOLVED**: judged entries supersede mechanical duplicates for
  covered cell sets; uncovered mechanical entries stay for explainability.
- **MAJOR — single-source chaos drill was dead code** (`if False`; the
  fresh+carried merge path had zero coverage). **RESOLVED**:
  COLLECTOR_FIXTURES_DIR serves recorded fixtures through the real fetch
  path; the drill now runs S2-down against ten live-parsing collectors and
  immediately caught real drift (llmstats self-report-source flags absent
  from hand-authored cells — aligned, plus METR proxy-marker gap from
  verifier §C.8, both fixed at the collector so overwrites can't shed
  rule-7 markers).
- **MAJOR — zombie sources never trip rule 9** (frozen content re-stamped
  fresh daily). **ACCEPTED** as RISK-012 with trigger: N identical days on a
  source that historically moved ⇒ implement last-value-change badging
  ("unchanged for Nd"). Epoch/LiveBench already carry explicit vintage
  labels; AA/Arena/OpenRouter are high-cadence and would surface via the
  watch/tape going quiet.
- **MINOR — partial source response blanks cells same-day** (slug rename
  indistinguishable from delisting). **ACCEPTED** as RISK-013 with trigger
  (first observed false blanking ⇒ N-day debounce carrying last-good+flag).
- **MINOR — flag-only changes invisible** in tape/changelog. **RESOLVED**:
  `diff_entries` emits `flags-changed` entries (gained/dropped, verbatim).
- **MINOR — [skip ci] booby trap**. **RESOLVED**: removed (no-op for
  schedule/dispatch; GITHUB_TOKEN pushes don't trigger push workflows).
- **MINOR — failed-gate day loses the snapshot**. **RESOLVED** twice over:
  data/ commits before build/tests (innovator rider 8), and red runs upload
  data/ as a 90-day forensic artifact.
- **MINOR — hang math** (4 hanging sources ≈ step timeout). **RESOLVED**:
  COLLECTOR_RETRIES/COLLECTOR_TIMEOUT_S env knobs, capped in CI (1 retry,
  45s).
- **MINOR — missing gate artifacts**. **RESOLVED** with this gate:
  innovator/phase-6-7-8.md, redteam/phase-{4,5,6,7}.md, ADR-006/007/008.
  ORDERING.md Phase-7 extensions: the no-column rule rides with RISK-010's
  catalog build; chip-reassignment explainability is inherent (chips derive
  from values; every value move is tape/changelog-covered) — recorded in
  ADR-007.

## Innovator riders adopted at this gate

Data-commit-before-build (rider 8), fetch-depth 1 (rider 7 fix), dual-cron
scheduler-miss guard (rider 9), Messages-API judgment transport (rider 1),
docs/.nojekyll (rider 2). Riders 3–6 and 10–12 recorded in RISKS.md with
their triggers.
