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

### Phase 1 — Research (2026-08-01)

Nine parallel research agents live-verified every brief source plus scouted
candidates (workflow `wf_3d319f0f`, 312 tool calls). Full detail in
`governance/SOURCES.md` (ledger + fetch-feasibility matrix). Headlines:

**Source verdicts.**
- Artificial Analysis: grade A. Index still v4.1. Documented API v2 (free key
  covers index/cost/speed/TTFT) + keyless embedded-JSON fallback carrying ALL
  five metric families. All five models + context windows (~1M each) verified.
- Arena: canonical domain is arena.ai (brief was right; lmarena.ai redirects).
  Site ToS bars scraping; the OFFICIAL HuggingFace dataset (CC-BY-4.0) is the
  sanctioned machine channel. Style Control is the default board and reorders
  the top vs raw — collector must pin board variant.
- OpenRouter: unauthenticated frontend JSON endpoints found (market-share,
  task-spend). ToS updated Jul 27 has an anti-scraping clause → RISK-006.
  Task-spend gives PER-MODEL spend share — better than the seed's
  provider-level-only view; Kimi K3 becomes capturable.
- ARC Prize: canonical JSON (v3.json) their own frontend loads. Sol's official
  7.8 is tier **Max** (seed tier resolved). **Fable 5 has NO verified ARC-AGI-3
  score** — seed's 16.6 traces to nothing official (X post: "~20% on Public
  Demo", non-comparable).
- METR: machine-readable YAML. Fable's number is really Mythos Preview (early)
  at 17.4h [8.5–55.1] with "unreliable above 16h" notice. Sol's 11.3h lives
  ONLY in a June 26 NDA'd blog post; METR's term is "cheating", not "record
  gaming". Last site update May 8 (~12 weeks) — irregular cadence priced into
  a 90d SLA.
- **"Morph-tracked board" REFUTED**: morphllm.com is a bot-blocked editorial/SEO
  page republishing Scale SEAL (independent, but covers none of our 5 models)
  and llm-stats (100% vendor self-reports; 0 of 43 verified). The seed's
  I-tagged SWE-bench Pro cells were vendor-grade all along. S6 demoted;
  replaced by S13 (llm-stats, vendor-classified) + S9 (Scale standardized).
- Terminal-Bench 2.1: live, embedded-JSON + Apache-2.0 GitHub data. Scores are
  agent+model+effort tuples. Fable 5 #1 (83.8±1.2); Sol repo-only (76.2, not
  displayed); Opus 5 / Kimi K3 / DS V4 Pro absent.
- Scouted: **INCLUDE Epoch ECI** (CSV, CC-BY, 5/5 coverage — second independent
  aggregate so the frontier-race read never rests on AA alone), **INCLUDE
  Vals AI** (professional agentic + strict-vs-weighted reliability gap; 4/5),
  **INCLUDE LiveBench conditionally** (contamination-resistant; promote only if
  ≥3/5 coverage at collector time). **EXCLUDE Scale SEAL as a general source**
  (Meta owns ~49% — kept only as S9 for the standardized SWE-Pro view with
  conflict flag), **EXCLUDE standalone HLE** (duplicates AA fetch), **EXCLUDE
  HAL** (paused; 0/5 coverage).

**Seed-vs-live delta classification (the pipeline's first adversarial trial —
final classification re-run against fetch day in Phase 9):**

| Cell / claim | Seed | Live 2026-08-01 | Class |
|---|---|---|---|
| arena-elo.kimi-k3 | 1547 #2 | 1485.3 #12; OVERALL style-control history max 1486.82, best rank 8 (verifier). K3-max hit 1540–1542 RANK 1 on the industry_legal_and_government category board Jul 26–30 (gate) | **likely category-board conflation of a real number** (gate-rescoped; not "never existed") |
| swe-bench-pro.fable-5 | 80.3 (I) | 80.0, self-reported; 80.3 was Mythos 5's number | **misattribution + provenance error (I→V)** |
| swe-bench-pro.gpt-5-6-sol | 64.6 (I) | 64.6 self-reported | **provenance error (I→V)** |
| swe-bench-pro.ds-v4-pro | not published | 55.4 on aggregate ("V4-Pro-Max") | **seed gap** |
| arc-agi-3.fable-5 | 16.6 | absent from verified board; "~20% Public Demo" only | **unverifiable provenance → becomes empty("not published") + note** |
| arc-agi-3.gpt-5-6-sol tier | unspecified | Max ($25,064/run) | **resolved** |
| metr-horizon.fable-5 | ≥16h | 17.4h [8.5–55.1], Mythos Preview (early), >16h-unreliable notice | **imprecision corrected** |
| gdpval.opus-5 / sol | 1861 / ~1748 | 1857.8 / 1732.5 | **real movement (Elo refit)** |
| gdpval.ds-v4-pro | not published | 1304.49 | **new data** |
| cost-per-task (all) | 2.75/2.03/1.04/0.94 | 3.15/2.34/1.86/0.86 (+DS 0.05) | **movement, driver unresolved** (gate-downgraded: both endpoints nominally v4.1; no price/endpoint/effort driver identified for +55–79% swings; cells carry the unresolved flag until a driver is named) |
| openrouter anthropic | ~13% | 9.1% (wk 07-20) | **movement, unit-comparability unresolved** (gate-downgraded: seed unit unknown vs endpoint's unlabeled counts; the ambiguity flag propagates into any tape/implication citing these cells) |
| openrouter deepseek | ~16% #1 | 17.4% #2 behind xiaomi 19.1%; 20.9% #1 partial wk | **movement, unit-comparability unresolved + seed gap (xiaomi)** |
| aa-index all 5 | 61/60/59/57/44 | 60.69/59.86/58.89/57.11/44.27 | **match (display rounding)** |
| DS V4 Flash 0731 = 50 | tape item | confirmed verbatim by AA article | **match** |
| Opus 5 79.2 Pro claim | not on board | still not on any board | **match** |

**Landscape / column proposal (input to Phases 2–3, rationale gate-corrected):**
keep the five columns (Fable 5, Opus 5, GPT-5.6 Sol, Kimi K3, DS V4 Pro). The
honest rationale is COVERAGE DENSITY plus camp representation, not score
proximity: the top-4 are the AA index top-4; DS V4 Pro (AA 44) is kept over its
higher-scoring sibling Flash 0731 (AA 50) because Pro has multi-source coverage
today (GDPval, Arena, cost, SWE-Pro aggregate, Verified) while Flash has one
independent source and would be a column of empty cells — the earlier "no
Google within ~9 pts" proximity argument is withdrawn (it contradicted the
fifth column). Explicit open items handed to Phases 2–3: (a) Gemini 3.6 Flash
(AA 50) and Google's structural absence — absence-as-signal belongs somewhere
visible (tape/watch), (b) DS Flash 0731 promotion path (currently 1 group-1
source), (c) Muse Spark 1.1 (Meta): Scale-standardized #1, Arena #8, TB #8 —
strongest catalog candidate, decide catalog vs column at Phase 3.
Catalog/watch candidates for Phase 3: Opus 4.8 / 4.7 / 4.6 (Arena top-5,
boards), Mythos Preview (METR/llm-stats), Sonnet 5, GPT-5.5 / Terra / Luna,
Grok 4.5, Muse Spark 1.1 (Meta — Scale #1, Arena #8, TB #8), Gemini 3.1 Pro /
3.6 Flash, GLM-5.2, Kimi K2.6, DS V4 Flash 0731 (watch: 1 independent group-1
source so far), Qwen3.8-Max (preview only — watch), Gemini 3.5 Pro (unreleased
— watch). Integrity items for the disclosure-watch row: HF agent-intrusion
disclosure (Jul 28), NIST AITE launch (Jul 27), SWE-bench Pro verification gap
(Jul 25), Sol ARC modified-harness claim (Jul 30), Sol METR cheating flag.

**Phase 1 gate (2026-08-01):** verifier countersigned YES — all 12 collectable
sources live-fetched and parsed via the ledger's claimed methods, 3 spot-claims
reproduced verbatim. Red-team: 1 BLOCKING + 10 MAJOR + 5 MINOR, all resolved
same-day (redteam/phase-1.md): two new constitution mechanisms (source Sunset,
machine-read Caveat-flags — both linter-enforced with negative tests), honest
independence restatements (AA lab-revenue, Epoch/OpenAI, TB self-run-audited,
Vals cap table), delta downgrades where evidence was thin, and the corrected
snapshot `data/2026-08-01.json` (all values gate-verified) so the page stopped
rendering the refuted 80.3-as-independent immediately. 57 tests green;
`make all` green over seed + corrected snapshot with full explainability
(8 tape entries + 21 changelog entries). ADR-003. Phase 1 CLOSED.

### Phase 2 — Metric Selection (2026-08-01)

Innovator: 3 portfolio strategies + candidates across all 4 mandated axes
(governance/innovator/phase-2.md). Builder selected the
integrity-differentiated portfolio: **20 matrix rows** (13 kept incumbents + 6
adds + LiveBench promoted at gate-verified 5/5 coverage), 3 seed rows demoted
to the brief layer, 2 headroom, HOLDs with named machine-checkable triggers.
Registry: governance/ROWS.md.

Gate: red-team 3 BLOCKING + 9 MAJOR + 6 MINOR (all demonstrated; all resolved
same-day — chip-integrity semantics rebuilt with value_disclaimed +
flagged-leader-no-chip + chip_eligible opt-out, caveat scopes extended to the
new metric ids, factual flag errors fixed, SWE-rebench made a third separated
scale, derived-cell enforcement added, disclosure-watch re-sourced to curated
S21). Verifier: every displayable number reproduced against primary sources;
countersigned after three conditions landed (Vals 5/5, window-relative
SWE-rebench contamination flags, Sol flag fix); located the ECI value channel
(eci_scores.csv) where Sol>Fable — row 2's disagreement purpose demonstrated
live. 76 tests green. ADR-004. Phase 2 CLOSED.
