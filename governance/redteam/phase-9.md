# Verification gate — Phase 9 (end-to-end)

The Phase 9 gate is verification-shaped: the adversarial pressure is the
live run + the Definition-of-Done checklist + an independent cold read and
EVAL countersign (full text appended to `../EVAL.md` when delivered).

## Evidence ledger

- **Live e2e**: 11/11 sources fetched over the real network (sandboxed data
  dir); data gate and rendered-page gate green. Round 1 red — two carry-path
  defects found LOUDLY and fixed (`harden_carried_cell`, cite_values
  baselining); round 2 green. Drift vs the curated snapshot classified in
  BUILDLOG (17 cells, four classes, no unexplained delta).
- **Determinism**: `make all` twice consecutively, outputs byte-identical.
- **Chaos drills** (CI-repeatable): total loss, single-source loss through
  the real fetch path, clock-advance staleness, same-day re-run,
  implication rot end-to-end, brief promotion. All green.
- **Governance completeness**: ADR-001..008 (≥1 per phase), redteam/
  phase-0..9, RISKS.md current (001–014), EVAL.md, RUNBOOK.md, HANDOFF.md
  consolidated with ordered human actions.
- **Known blocker**: RISK-004 (push 403) — every phase boundary is
  committed locally; HANDOFF step 1 is the unblock. Items that require the
  human side (Pages toggle, live-URL check from both devices, first
  dispatched run) are explicitly provisional in EVAL dimension 7.

## Cold read + countersign

Delivered by the independent Phase 9 verifier; recorded in EVAL.md
("Verifier countersign") verbatim. Any DISPUTE there is binding: a disputed
score keeps the verifier's number and, if under 4, its remediation note.
