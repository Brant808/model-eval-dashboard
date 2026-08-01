# RISKS — Living Register

Format: RISK-N | status | rationale | reversal trigger. Accepted risks are
decisions, not omissions: each one traces to a gate objection.

---

## RISK-001 — First name appears in governance docs in a repo that may become public
- Status: ACCEPTED (Phase 0)
- Context: Constitutional rule 12 bars personal context from repo and page. The
  commissioning brief (`governance/BRIEF.md`) names the reader by first name and
  describes reading habits; the brief itself instructed verbatim preservation.
  GitHub Pages on a free personal account requires a public repo.
- Rationale: a first name + "reads a dashboard in the morning" is minimal
  exposure; the brief is the audit trail for every decision here, and altering
  it would corrupt the governance record. The built PAGE carries zero personal
  context — the linter mechanically enforces name/email/credential absence on
  the page and credential/email absence repo-wide.
- Reversal trigger: reader objects, or repo must go public and reader prefers
  scrubbing — then redact the name from BRIEF.md (noted edit) or buy Pages
  privacy via a paid plan.

## RISK-002 — Cron and manual dispatch only activate after the PR merges
- Status: ACCEPTED (Phase 0, revisit Phase 7/9)
- Context: GitHub runs scheduled workflows and offers workflow_dispatch only
  from the default branch; all work lands on the session branch.
- Rationale: unavoidable given branch discipline. Mitigation: Phase 7 simulates
  the workflow's exact steps locally end-to-end; HANDOFF.md leads with
  "merge PR, then dispatch once and watch it go green."
- Reversal trigger: none needed; resolves itself at merge.

## RISK-003 — Hooks registered mid-session may not fire until a fresh session
- Status: ACCEPTED (Phase 0)
- Context: `.claude/settings.json` was created during this session; Claude Code
  loads hook config at session start.
- Rationale: the hook script is verified by direct invocation with a synthetic
  payload (same interface the hook runner uses). Future sessions get the hook
  automatically.
- Reversal trigger: if a future session shows the hook not firing on a real
  edit, debug the matcher/config then.

## RISK-004 — Repo write access denied from the sandbox (push 403)
- Status: OPEN (Phase 0) — retry at every phase boundary
- Context: `git push` via the platform git relay returns 403 on
  `git-receive-pack`, and the GitHub API returns "Resource not accessible by
  integration" for ref creation. Reads work. All work is committed locally.
- Impact if unresolved: the sandbox is ephemeral; unpushed work dies with it.
  Also blocks Definition-of-Done items (workflow merged, Pages live).
- Mitigation: retry push at each phase boundary; if still failing at Phase 9,
  HANDOFF gains a BLOCKER entry (grant the Claude GitHub App write access to
  brant808/model-eval-dashboard via claude.ai/settings or GitHub App settings,
  then push from a fresh session).
- Reversal trigger: first successful push closes this risk.

## RISK-005 — Bash-tool writes bypass the PostToolUse edit guard
- Status: ACCEPTED (Phase 0 gate, red-team M5)
- Context: Claude Code PostToolUse hooks fire on Edit/Write tool calls; a file
  written via Bash (sed/echo/redirect) skips the hook even on guarded paths.
- Rationale: the hook is a fast local tripwire, not the enforcement authority.
  The authority is `make check && make test`, which CI (Phase 7 workflow) runs
  on every push and before every publish; nothing reaches the published page
  without passing the linter in CI.
- Reversal trigger: if a Bash-written violation ever reaches a pushed commit
  without CI catching it, add a pre-commit git hook as a second tripwire.

## RISK-006 — OpenRouter ToS anti-scraping clause vs unauthenticated frontend endpoints
- Status: ACCEPTED (Phase 1, ADR-002)
- Context: openrouter.ai/rankings data loads from unauthenticated
  /api/frontend/v1/rankings/* JSON endpoints; robots.txt is permissive, but the
  ToS (updated 2026-07-27) contains a broad anti-scraping clause.
- Rationale: adoption/momentum is a standing lens of the dashboard; collection
  is one polite GET per endpoint per day with an honest identifying UA — the
  same requests the public page issues, no circumvention of any technical
  measure. Exposure is minimal and the failure mode is graceful.
- Reversal trigger: any 4xx block, robots change, or objection from OpenRouter
  ⇒ collector stands down permanently (cells go "source down (last-good
  shown)" then empty), and we request written permission or drop the rows.
- Amendment (Phase 1 gate): exposure is understated by the fetch-only framing —
  the dashboard also REPUBLISHES derived rankings figures daily, which is the
  use anti-scraping clauses most directly target. Posture: display derived
  percentages only (never bulk data), with visible attribution; the reversal
  trigger above covers takedown requests too. See also RISK-008 (fallback).

## RISK-007 — Vals AI funding/pay-for-placement not publicly disclosed
- Status: CLOSED (Phase 1 gate, 2026-08-01) — with a standing caveat flag
- Context: Vals AI is scouted-in for the professional-agentic axis; the Phase 1
  pass found no public funding disclosure.
- Resolution: the gate red-team resolved the premise — funding IS publicly
  discoverable (~$5M: Bloomberg Beta, Pear VC, 8VC, J12, Sequoia scout; no
  frontier-lab investors), and an active pay-for-placement search found no
  evidence. S11 now declares machine-read caveat flags ("VC-funded evaluator,
  no on-site funding disclosure") that every Vals cell must carry, and the
  ledger notes the Bloomberg-Beta-adjacent-to-Finance-Agent residual.
- Reversal trigger: credible evidence of pay-for-placement ⇒ source dropped.

## RISK-008 — Adoption lens has a single collectable source (OpenRouter)
- Status: ACCEPTED (Phase 1 gate)
- Context: S3 is the only adoption/usage source, and RISK-006 commits its
  collector to stand down permanently on any block or objection — a designed
  single point of permanent failure for one of the four standing lenses.
- Mitigation: S19 records the scouted fallback (HF download telemetry for
  open-weights models; vendor disclosures as V-tagged last resort). Residual
  accepted: no independent public fallback exists for closed-model adoption —
  if S3 dies, the adoption lens degrades to open-weights-only coverage and the
  page says so via empty-cell reasons.
- Reversal trigger: a second independent adoption source with closed-model
  coverage appears ⇒ collect it and close this risk.
