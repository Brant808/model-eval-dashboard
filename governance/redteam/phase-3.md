# Red-Team Report — Phase 3 (Grouping & Ordering)

Gate run 2026-08-01: red-team performed cold 60-second reads of all four
ordering finalists (from the innovator's mocks) and attacked the two
brief-named hazards; verifier reproduced every decision-relevant claim in
ORDERING.md (grouping arithmetic exact, T2 trio deterministic from the
snapshot with the cross-vendor mobile pair, chip semantics faithful to
`compute_chips`, all Muse Spark sources verified live).

**Verifier: NO-as-is → YES on one condition, applied**: the Muse Spark "no AA
index" premise was refuted by our own S1 fixture (AA index 50.62, not
estimated; 4 independent sources, not 3) — D5/D3 corrected; the correction
strengthens T2 (Meta is in scope and simply ranks below the vendor cutoff).
Minors applied: intelligence-per-dollar materialized into the snapshot
(19.0/25.9/31.7/66.4/885.4 with derived_from + changelog); "group-1 source"
operationally pinned (independent ledger sources feeding C1–C3 rows).

**Red-team cold-read scores**: A 4 breaks · B 5 (one severe: a trio-truncated
"⚠highest" superlative that contradicts the snapshot) · C 6 (worst day-one:
pending-row density, budget exhausted before C3/C4, a false "three
methodologies agree" mock line) · D 3 (best day-one; brittle triage).
C retained for the only property that compounds — permanent domain semantics —
with D's fold stolen and the day-one costs removed by the stub/copy riders
below. Reversal recorded in ADR-005: if the Phase 6 rendered cold read still
fails, switch to D.

## BLOCKING (all resolved same-day, each with a regression test)

**B1 — latest.json lagged the corrected snapshot; quarantine unenforced.**
The live page showed naked 79.2/95.0 [V] cells (data-warn=0) and a
factually-wrong flag while `make check` was green, because nothing forced
latest == newest dated snapshot and warn-class flags on claim cells were
hand-maintained prose. Resolved: SYNC rule (latest must be byte-identical to
the newest dated snapshot); linter rule "populated V cell in a vendor-claims
set must carry a warn-class integrity marker" (snapshots ≥ 2026-08-01); the
claimed sub-band became a machine contract (`claim_v: true` metrics must
render `data-band="claimed"` + visible VENDOR-CLAIMED label — render-tested);
latest re-materialized and page rebuilt. Tests:
`test_gate3_latest_sync_enforced`, `test_gate3_vendor_claim_cell_requires_marker`,
`test_gate3_claim_band_renders`.

**B2 — position-9 "pre-refuted" rationale void until Phase 7 and paradoxical
after it.** Resolved: swe-bench-pro moved to C7's claimed band (below the
fold, beside swe-bench-verified); C3 holds swe-rebench alone (stub until its
collector lands). Reversal condition recorded: may return to C3 by ADR only
after swe-rebench is populated AND a rendered cold read proves the sub-band
carries the weight.

**B3 — field-#1 footnote recreated refused superlatives (4 of 5 crowning the
home model).** Resolved: footnote redefined as the CHIP-WINNER when
off-screen — full compute_chips eligibility, warn flags travel, no winner ⇒
no footnote, density cap 4/screenful; Phase 6 must encode it as a test.

## MAJOR (resolved as binding riders in ORDERING.md)

M1 default-view field-order misstatement → field-order caption on the
headline stat + rule label on the picker (T2 survives its steelman on these
riders). M2 QL-A fallback/laundered caveat → visible slot label + derived
cells now inherit parents' movement caveats (linter-enforced,
`test_gate3_derived_inherits_movement_caveats`). M3 Muse Spark thin column →
picker "early coverage: N of 20 rows" badges; catalog floors unified in
practice by the badge + collector-build checkpoint. M4 fold copy → points
downward, suppressed when C5–C7 moved. M5 C's day-one read → pending-row
stubs, no-triangulation-copy rule, rendered cold read re-run at the Phase 6
gate.

## MINOR (resolved)

Two-weight V legend made binding; jargon copy pass mandated; catalog
conditional seats + kimi-k2-6 pinned to a collector-build checkpoint;
RISK-009 (T2 AA-scoping reversal trigger); mock defects noted for the record
(mocks are not shipped copy; "self-run" deliberately remains note-class —
vendor-executed-but-audited is a caveat, not a named integrity condition —
recorded as a decision).

## Solid

D6 hysteresis survives launch day (promotion bypasses it); CO-LEAD +
provider-dedupe sound; T2 mechanics verified; rule-5 letter holds in all four
orderings; pipeline green throughout (85 tests after gate hardening).
