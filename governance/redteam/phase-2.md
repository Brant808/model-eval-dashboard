# Red-Team Report — Phase 2 (Metric Selection)

Gate run 2026-08-01: red-team attacked `governance/ROWS.md` per the brief
(strongest cut case per row; most tempting rejected candidate; integrity
quarantine; overlap; derived-cell convention; row-cap stress). Verifier
reproduced every number a shipped row would display against primary sources —
all values MATCH; countersign was **NO as-is with three named conditions, all
applied same-day** (row 20 coverage 4/5→5/5 with DeepSeek live on the Vals
board at 55.6 #19; SWE-rebench decontamination rescoped to window-relative with
the board's own "Potential contamination" flags made a mandatory mechanical
collector rule; Sol omniscience flag corrected). Verifier bonuses: the ECI
composite VALUE channel located (`epoch.ai/data/eci_scores.csv` — where Sol
161.69 > Fable 161.55, differing from AA's order: row 2's disagreement signal
demonstrated live), Vals astro-island and SWE-rebench flight-payload extraction
specs pinned for Phase 7.

Red-team findings: **3 BLOCKING, 9 MAJOR, 6 MINOR.** Resolutions:

## BLOCKING (all resolved in code/data with regression tests)

**B1 — chips could be manufactured from disclaimed data** (the shipped METR
LEAD existed only because METR's own-disclaimed Sol figure supplied the
competition; a flagged cell could even WIN a chip). Resolved with a principled
two-part rule in `compute_chips`: publisher-disclaimed values
(`value_disclaimed: true`) neither win nor count as competition;
integrity-flagged values may compete (their value is sound; the flag warns
about context) but never win — and if the true leader is flagged, no chip at
all (crowning second place would lie about the max). METR row now chipless;
ARC's legitimate Opus record chip survives. Metrics can also opt out via
`chip_eligible: false` — applied to openrouter-share (provider aggregates in
model columns never chip; resolves M9's fake "DS V4 Pro leads adoption").
Tests: `test_gate2_disclaimed_values_cannot_legitimize_chips`,
`test_gate2_flagged_leader_awards_no_chip`.

**B2 — caveat machinery didn't cover the Phase 2 metric ids.** S1's
Gemini-grader scope extended to `@aa-halluc-rate` and `@aa-agentic-index`
(collector emits the flag; fixture-tested); S3 gained a machine-read
`Caveat-flags:` line matching the unit-ambiguity string already on cells;
ROWS.md row 4 now declares the caveat.

**B3 — factually wrong "highest of the five" flags.** Sol's hallucination flag
corrected to "second-highest (DS V4 Pro: 0.940)"; Fable's disambiguated
("accuracy 0.614 — highest accuracy of the five"); DS marked as the actual
highest hallucination rate.

## MAJOR (all resolved)

- **M1 row-8 quarantine glyph-deep** → `INTEGRITY_MARKERS` extended with
  "self-report": every vendor-claim cell now renders warn-class (⚠) and
  propagates into implications; ROWS.md re-words quarantine as a BINDING
  Phase 3/6 obligation (tinted "claimed" sub-band + row label) rather than an
  accomplished fact.
- **M2 SWE-rebench not rule-5-separated** → third family added to the linter
  (sets + tape + implication text, pairwise across pro/verified/rebench);
  row 7 reworded to window-over-window-vs-itself.
  Test: `test_gate2_rebench_is_a_third_separated_scale`.
- **M3 derived cells unenforced** → `derived_from` schema field + `DERIVATIONS`
  registry: linter recomputes the quotient, enforces worst-parent staleness and
  integrity-flag inheritance. Test: `test_gate2_derived_cell_enforcement`.
- **M4 ECI corroboration oversold** → row 2 rewritten: partially-overlapping
  second read; agreement weak, disagreement strong (now demonstrated live).
- **M5 disclosure-watch on seed-only S0** → new S21 curated ledger entry
  (method, SLA, per-item primary sourcing); snapshot cells re-cited.
- **M6 row-4 coverage inferred** → resolved empirically: all five carry
  `agenticIndex` in the recorded fixture (Opus 55.26, Sol 54.00, Fable 52.81,
  Kimi 50.07, DS 36.36 — verifier live-matched).
- **M7 METR proxy misattribution as a footnote** → "proxy-model measurement"
  is now an INTEGRITY_MARKER (warn-class, propagates) and the Fable METR cell
  is `value_disclaimed` (with the >16h-unreliable notice) — chipless.
- **M8 FAR.AI OR-trigger could force-promote the uncollectable** → trigger now
  requires a machine-readable endpoint AND (coverage OR differentiating
  spread); collectability named the hard gate.
- **M9 provider-level chip** → resolved by `chip_eligible: false` (B1) plus a
  Phase 6 obligation to render provider figures deduped.

## MINOR (all resolved)

Saturation flag on the 95.0 cell (+ warn-class self-report flags on the
Verified row); row 8 wording "claim-vs-standardized (S9)"; Opus launch-claim
cell flagged provisional-in-set; LiveBench cell pinned to GLOBAL AVERAGE and
Vals to the WEIGHTED composite; rotation-day set changes pre-classified as
methodology-change with cross-set delta suppression (Phase 6/7 obligation);
coverage fractions denominated against the current column set.

## Standing observations adopted into the registry

The honest-redundancy accounting (≈15–16 independent signals of 20; S1
concentration at 7 rows named as accepted exposure; cut order 12 → fold 3→4 →
17) now lives in ROWS.md. Row 11's ARC cell treatment confirmed as the
template. The FAR.AI HOLD survived the red-team's own strongest-case attack on
its stated grounds (0/—/0/—/— differentiates nothing in-matrix; no endpoint).

## Exit

Final row set: 20 rows, per-row decision-value statements, Pro/Verified (and
now rebench) separation preserved and machine-enforced. Linter + 76 tests
green over seed + corrected snapshot + rebuilt page. Phase 2 CLOSED (ADR-004).
