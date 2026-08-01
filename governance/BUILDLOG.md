# BUILDLOG — Frontier Model Eval Dashboard

Running narrative. Newest entries appended at the bottom of each phase section.
Brief: `governance/BRIEF.md`. Rules: Section 2 of the brief (the "constitution").

## Execution Plan (written before Phase 0, 2026-08-01)

### Reading of the mission

One self-contained HTML page, rebuilt daily by CI with zero human input, that a
keyboard-first reader scans in under 60 seconds to learn: (a) what moved in ~72h,
(b) how much to trust each number, (c) what it means. Governance artifacts are
first-class deliverables. The repo is the only durable store; this sandbox dies.

### Standing architecture decisions (to be ratified per-phase by ADR)

- **Language**: Python 3.11 for collectors, linter, renderer, tests (stdlib +
  `requests` only; no heavyweight deps, keeps CI fast and deterministic).
- **Renderer**: pure function `data + history -> HTML string`, no clock reads, no
  network; all timestamps come from the snapshot, so identical inputs give
  byte-identical output.
- **Data flow**: `collectors/` -> `data/YYYY-MM-DD.json` (canonical cell schema)
  -> `site/render.py` -> `docs/model-eval-monitor.html` (+ `docs/index.html`
  copy for the clean Pages URL).
- **Invariant linter**: `tools/check_invariants.py` enforces all 12
  constitutional rules against every snapshot in `data/` AND the built HTML.
  `make check` fails the build (and therefore the publish) on any violation.
- **Scheduler/host**: GitHub Actions cron + GitHub Pages, per the brief's
  narrowed option space. Snapshots commit back to the repo (history for
  sparklines + repo activity to keep cron alive).
- **Judgment layer**: optional `claude -p` step; ships OFF (mechanical tape) and
  self-upgrades when `ANTHROPIC_API_KEY` secret exists. Schema-validated output;
  a validator rejects any number/model/fact not present in the day's snapshot.

### Phase-by-phase mapping to this workflow

| Phase | Builder work (main thread) | Gate mechanics |
|---|---|---|
| 0 Harness | Scaffold repo, CLAUDE.md, agents, hooks, Makefile, seed JSON, connectivity probe, working `make all` on seed | Red-team tries to sneak rule-violating data past `make check`; verifier exercises the hook path. Parallel subagents. |
| 1 Research | Live-verify all 6 primary sources + 2+ scouted candidates via web fetch/search; fetch-feasibility matrix; column proposal | Red-team attacks independence + machine-readability claims; verifier re-fetches one value per source. |
| 2 Metrics | Row-by-row decision-value audit vs kill criteria | Innovator proposes additions across 4 axes; red-team argues strongest cut case per row. |
| 3 Ordering | Relevance definition, group order, quick-look set, default trio, catalog scope, tie rules | Innovator: 3 orderings; red-team: cold 60s reads + the two named hazards (V-high-on-page, home-team default). |
| 4 Briefs | Metric + model brief content generated from data + research notes | Verifier fact-checks 3 random briefs sentence-by-sentence; red-team checks flag prominence. |
| 5 Implications | X-layer engine: cited cells, confidence, falsifier, carry-forward dates | Red-team writes strongest opposite reading per implication; verifier resolves citations. |
| 6 UI | Full Apple-compare page: pickers, sticky header, quick look, keyboard nav, tape, briefs, health footer | Automated checklist (offline, width, weight, determinism, contrast) + cold-read agents. |
| 7 Autorefresh | Collectors w/ fixtures, degraded-mode judgment hook, GitHub Actions workflow, new-model watch | Chaos drills as pytest fixtures + env flags; each drill is a repeatable test. |
| 8 Access | Pages deploy config, URL, HANDOFF steps (keyboard-only) | Red-team: deploy-failure behavior, 30-day rot simulation. |
| 9 E2E | Live run, seed diff w/ classified deltas, EVAL.md, RUNBOOK.md, final HANDOFF.md, PR | Verifier cold-read + countersign of every EVAL score. |

### Adaptations to the sandbox (logged up front, candidates for HANDOFF/RISKS)

1. **Cron + dispatch run on the default branch only.** All work lands on the
   session branch `claude/frontier-model-eval-dashboard-urlfzc`; GitHub only
   schedules workflows from the default branch, and `workflow_dispatch` is only
   offered for workflows present there. Therefore "workflow green on a manual
   dispatch" (Definition of Done) can only be satisfied after the PR merges.
   Mitigation: simulate the workflow's exact steps locally end-to-end in Phase 7,
   and put the dispatch-after-merge step at the top of HANDOFF.md.
2. **Pages enablement is a repo-settings action** only the human can take; it is
   a HANDOFF item with keyboard steps, not a blocker.
3. **`ANTHROPIC_API_KEY` secret** is human-only; ship degraded mode by default
   per the brief.
4. **Hooks registered mid-session may not fire until next session**; the gate
   verifies the hook script itself executes correctly when invoked as the hook
   runner would, and notes the session-restart caveat.
5. **Subagent roles**: red-team / verifier / innovator are defined in
   `.claude/agents/` as required deliverables. Gate runs use parallel subagents
   with those role prompts (the sandbox's agent registry may not hot-load new
   agent files mid-session; the prompts are duplicated into the gate tasks so the
   roles run either way).

### Commit discipline

Commit + push at every phase boundary; message carries the phase and ADR number.
Anything not pushed does not exist.

---

## Phase Log

### Phase 0 — Harness (started 2026-08-01)

- Saved brief verbatim to `governance/BRIEF.md`.
- Wrote this execution plan.
- Scaffolded: repo layout, CLAUDE.md, three role subagents, PostToolUse hook
  (guards collectors/site/tests edits with `make check && make test`),
  Makefile (all six targets live, not stubs), seed snapshot in canonical cell
  schema, SOURCES.md seed ledger (S0–S8), invariant linter enforcing all 12
  rules against data AND built HTML, Phase 0 renderer honoring the full
  data-attribute contract, 34 tests including negative "violate the
  constitution" tests for every rule.
- `make all` green end-to-end on seed data; second run byte-identical
  (md5 7cfe50ce…). Hook script verified by direct invocation (fires on
  site/ path, skips README) — RISK-003 notes the mid-session registration caveat.
- Connectivity probe: all six primary source domains reachable; zero HANDOFF
  network items; morphllm.com rate-limits (429) — collector backoff noted.
  Notable: lmarena.ai redirects to arena.ai, confirming the brief's domain.
- Gate: red-team + verifier subagents dispatched (results below).
- Gate results: verifier countersigned YES unconditional (31/31 MATCH).
  Red-team: 1 BLOCKING + 8 MAJOR + 4 MINOR, all demonstrated with exploits —
  all fixed in code same-day with permanent `test_gate_*` regression tests
  (provenance-vs-ledger enforcement, strict JSON/non-finite rejection, rule 5
  on tape + sentence text, mandatory SLAs, parser-based HTML anti-forgery,
  wider hook coverage, latest.json rot guard, removal-aware explainability,
  competition-required chips). One residual accepted (RISK-005: Bash-write
  hook bypass; CI is the authority). ADR-001 logged.
- Phase 0 exit criteria met: `make all` green on seed alone, twice,
  byte-identical (53 tests). Push blocked by RISK-004 (403) — commits local,
  retrying each boundary.

