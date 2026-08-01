---
description: Run the adversarial gate protocol for a phase (usage - /gate N)
---

Run the gate protocol from `CLAUDE.md` for phase $ARGUMENTS:

1. Confirm the phase deliverable is drafted and committed.
2. If a design phase (2, 3, 5, 6, 7, 8): launch the `innovator` subagent for the
   open design decisions; record alternatives.
3. Launch the `red-team` subagent against the deliverable with the phase's gate
   checklist from `governance/BRIEF.md`. Write its report to
   `governance/redteam/phase-$ARGUMENTS.md`.
4. Launch the `verifier` subagent to reproduce every number and factual claim.
5. Resolve all BLOCKING and MAJOR objections, or convert to accepted risks in
   `governance/RISKS.md` with rationale + reversal trigger.
6. Write the ADR to `governance/DECISIONS.md`.
7. Self-check against the phase exit criteria in the brief. If green: commit,
   push, update `governance/BUILDLOG.md`, proceed to the next phase.
