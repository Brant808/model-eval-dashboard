# Red-team gate — Phase 8 (publishing/access)

Covered by the combined 2026-08-01 gate: the innovator swept the publishing
decision space with web-grounded platform facts (`../innovator/phase-6-7-8.md`,
Decision 8 + riders), and red-team B attacked the deploy semantics inside
the pipeline report (`phase-6-7-report.md` Part 2: partial-failure states,
[skip ci]/Pages interaction, branch assumptions, commit-back push races).

## Findings and dispositions

- **Defect D-2 — docs/.nojekyll missing** (branch-deploy runs the managed
  Jekyll build; underscore assets silently vanish, Jekyll errors block
  deploys). **RESOLVED**: `docs/.nojekyll` committed.
- **Partial-failure serving state** ("fetch ok, gate fails — what's on
  Pages?"). **RESOLVED by construction**: the gate precedes the docs commit
  and the docs commit is the only deploy trigger; a red run publishes
  nothing and the previous deployment keeps serving (double last-good:
  no-push + Pages' last-successful-deploy).
- **[skip ci] vs the managed Pages build**. **RESOLVED**: marker removed;
  GITHUB_TOKEN pushes don't trigger push workflows, and the managed
  pages-build-deployment is not suppressible by commit markers. First-
  dispatch verification step added to HANDOFF (rider).
- **Branch assumption** (cron fires only on the default branch).
  **RESOLVED**: recorded in HANDOFF ("after merge — first scheduled run")
  and RISK-002 (accepted since Phase 0).
- **Stale-serving pathologies of branch deploys** (community-reported).
  **ACCEPTED**: RISK-014h mirror trigger + ADR-008 reversal conditions
  (flip to 8-B Actions deploy together with 7-B).
- **Keyboard-only constraint**. **RESOLVED with one honest exception**:
  every GitHub/Mac step is keyboard-navigable (plus a `gh api` one-liner);
  iPhone Add-to-Home-Screen is a touch gesture, recorded as such
  (RISK-014i) rather than papered over.

ADR-008 records the decision, the rejected space (8-B/8-C/8-D/8-E, Netlify
disqualified on pricing evidence), and the paired-reversal rule.
