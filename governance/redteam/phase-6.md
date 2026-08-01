# Red-team gate — Phase 6 (UI, rendered cold read)

Run 2026-08-01 (rendered in headless Chromium at 1440px and 390px; offline,
network-denied). Full attack text: `phase-6-7-report.md` Part 1. This gate
carried the ADR-005 reversal condition: ordering C stands only if the
rendered cold read passes.

## Cold-read verdict

PASS (conditional — conditions now resolved). Timed answers: (a) what moved
in ~72h — yes, ~15s via the tape; (b) trust per number — yes in the matrix
(I/V + [S#] + ⚠ + claim bands read without documentation), originally NO in
the quick-look band (resolved below); (c) what it means — yes (X-panel with
confidence/falsifier/cites; over-long noted); (d) ordering — was
unevaluable because the shipped page didn't render ordering C (resolved
below; re-verified post-migration: C1→C7 exactly, fold after C4);
(e) misleading spots — naked quick-look numbers and a legend claiming a
fold that didn't exist (both resolved).

## Findings and dispositions

- **BLOCKING — quick-look band stripped every trust signal** (no I/V tag,
  no ⚠, no staleness, empty cells as naked dashes; demonstrated: stale cell
  badged in the table, unbadged in the band, linter green — rule 9 violated
  exactly where the 60-second read starts). **RESOLVED**: ql state now
  carries tag/stale/warn/empty-reason per cell; the JS renders mini-badges
  (tag box, ⚠, STALE, "— <reason>"); the linter verifies the embedded ql
  state cell-for-cell against the snapshot (RULE1/3/7/9 classes), so a bare
  ql value is itself a violation now.
- **MAJOR — shipped page was neither ordering C nor D; legend promised a
  nonexistent fold** (seed-era groups + stranded one-row c-groups; claims
  row near the top; `data-fold` count 0). **RESOLVED**: snapshot migrated to
  the registry's C1..C7 groups (17 rows moved; throughput-ttft,
  context-window, deployment-terms to the brief layer with an on-page note);
  renderer orders groups canonically instead of first-seen (the registry
  interleaves — first live collect() would have re-broken it); fold renders
  after C4; re-render verified C1→C7 + fold + claims quarantined in C7.
- **MAJOR — ratified 12-model catalog (ORDERING.md D5) unimplemented; watch
  copy contradicted the decision record.** **PARTIALLY RESOLVED / DEFERRED**:
  watch copy corrected (entry RATIFIED at Phase 3, column build deferred);
  the catalog build itself is RISK-010 with trigger and scope — 7 columns of
  reasoned empties is a data-authoring phase of its own and the D6 empty
  rules make it mechanical. The ORDERING.md "no catalog model without a
  column" linter rule lands WITH that build (enforcing it now would fail by
  design).
- Found during gate hardening (not in the report, caught by the updated
  suite): the new ql badges + long caveat flags overflowed 236px at 390px
  after swapping to the heaviest-flag column — mobile table switched to
  fixed layout with overflow-wrap; Playwright test green again.

## X-panel length (noted, accepted)

~8 entries / ~3 iPhone screens. Accepted for now: two entries went OPEN at
this gate (denser signal), and the lens labels carry the scan. Revisit at
Phase 9 cold read if it still reads long.
