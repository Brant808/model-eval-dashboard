# CLAUDE CODE BUILD BRIEF: Frontier Model Eval Dashboard (Adversarially Governed Rebuild)

> Saved verbatim from the commissioning message, 2026-08-01. This is the governing document for this repository.

## 0. Mission

You are building a production-grade, self-refreshing frontier model evaluation dashboard for Brant. It replaces a chat-refreshed v2 HTML artifact with a versioned repo, a deterministic data pipeline, an optional LLM judgment layer, and a zero-input daily refresh. The finished product is a single self-contained HTML page Brant reads in under 60 seconds each morning, from iPhone or Mac, that answers three questions: what moved in the last 72 hours, how much can I trust each number, and what does it mean.

This build is governance-first. Every phase ends with an adversarial gate. You do not advance until the gate passes. Rigor is a deliverable equal to the dashboard itself: the decision log, red-team reports, and invariant checks are shipped artifacts, not scaffolding.

Operating agreement: once started, proceed through all phases autonomously. Do not pause to ask permission between phases. Stop only at genuine blockers (missing credentials, paid accounts, destructive ambiguity). Batch every human-required action into `governance/HANDOFF.md` rather than interrupting, unless it hard-blocks the autorefresh objective. Spend your thinking budget at gates and architecture decisions, not on boilerplate. Use maximum extended thinking at every gate.

## 1. Inherited State (inherit, then interrogate)

The v2 spec below was approved 2026-07-31. It is your starting position, not your conclusion. Every element of it must survive its phase gate or be replaced with a logged decision.

### v2 Spec

* Output: `model-eval-monitor.html`, a single self-contained HTML page. No build-time or view-time network dependency.
* Visual frame: chalk background, cobalt and amber accents, Archivo + Public Sans + IBM Plex Mono, matrix table with slide-over evaluation briefs (click any metric name or model name), and a "Today's tape" strip of dated moves from the last ~72 hours.
* Model columns: Claude Fable 5, Claude Opus 5, GPT-5.6 Sol, Kimi K3, DeepSeek V4 Pro. Newly released frontier models get added as columns with the addition noted.
* Row groups, ordered by trust in the number:
   1. Independent core: AA Intelligence Index v4.1, GDPval-AA v2, Terminal-Bench 2.1, cost per task, throughput/TTFT
   2. Frontier headroom: SWE-bench Pro (Morph-tracked board), ARC-AGI-3 (with effort tier), METR 50% time horizon
   3. Daily movers: Arena text Elo, OpenRouter provider token share
   4. Lab-claimed: SWE-bench Verified self-reports, disclosure watch row
   5. Economics and deployment: API list price, context window, AA-Omniscience factuality, deployment and data terms
* Live primary sources: artificialanalysis.ai, arena.ai, openrouter.ai/rankings, arcprize.org, metr.org/time-horizons, the Morph SWE-bench Pro board.
* UI directive update (this revision): the all-models matrix presentation above is superseded by the Apple-compare paradigm specified in Phase 6. Visual identity, slide-over briefs, Today's tape, and every data rule carry forward unchanged.

### Seed Snapshot (as of 2026-07-31; regression baseline, NOT current truth)

* AA Index v4.1: Opus 5 = 61 (#1), Fable 5 = 60, Sol = 59, Kimi K3 = 57, DS V4 Pro = 44. DS V4 Flash 0731 hit 50 on Jul 31.
* GDPval-AA v2 Elo: Opus 5 = 1861, Sol ~1748, Fable ~1747, Kimi = 1687.
* Cost per task: Kimi $0.94, Sol $1.04, Opus 5 $2.03, Fable $2.75.
* SWE-bench Pro (Morph-tracked): Fable 80.3, Opus 4.8 = 69.2, Sol 64.6. Opus 5 at 79.2 is a launch claim not yet on the board.
* ARC-AGI-3: Opus 5 = 30.2 High (record, Jul 24), Fable 16.6, Sol 7.8 official vs 38.3 vendor-claimed on a modified harness (Jul 30).
* METR 50% horizon: Mythos Preview (Fable base) at 16h or more. Sol ~11.3h, flagged non-robust with record gaming, CI 5 to 40h. Opus 5, K3, DS V4 not yet measured.
* Movers: Arena in flux (Fable #1 in a mid-July snapshot, Kimi 1547 at #2, Opus 5 and Sol settling). OpenRouter: DeepSeek ~16% (#1 provider), Anthropic ~13% (premium lane, leads programming spend), OpenAI ~8%.
* List prices per Mtok in/out: Fable $10/$50, Opus 5 $5/$25, Sol $5/$30 (Terra $2/$12, Luna $0.20/$1.20 after the Jul 30 cut; input rate jumps past 272K context), Kimi $3/$15, DS $0.44/$0.87.
* SWE-bench Verified (lab-claimed): Fable 95.0, DS 80.6, Sol withheld post-METR.

Encode this snapshot verbatim as `data/2026-07-31.seed.json` in the canonical cell schema (Section 5). Your first live fetch will be diffed against it; every delta must be classified as real movement, methodology change, or parse error. That diff is the pipeline's first adversarial trial.

If a prior `model-eval-monitor.html` exists in the working directory, treat it as a reference implementation to mine, not a constraint. If absent, build from this spec without blocking.

## 2. Constitutional Data Rules

These are invariants. They are encoded as automated checks (`make check`) that run on every build, and the pipeline may not publish a page that violates any of them.

1. Every populated cell carries a provenance tag: I (independent) or V (vendor-claimed).
2. Every populated cell carries a numbered source id resolving to a `SOURCES.md` ledger entry with URL, fetch method, and retrieved-at timestamp.
3. Every empty cell carries an explicit reason from a fixed enum: not published, not evaluated, settling, withheld, source down (last-good shown).
4. Lead chips are awarded only within a declared comparability set. No chip may span mixed sets. Chips use shape plus label, never color alone.
5. SWE-bench Pro and SWE-bench Verified never appear in the same row, comparison, chip computation, or implication sentence.
6. Every ARC-AGI-3 value carries its effort tier.
7. Integrity flags (record gaming, modified harness, withheld disclosure) render as visible warning tags on the cell and propagate into any implication citing that cell.
8. Tape entries are dated, fall within ~72 hours of build time, and each carries a source id.
9. Any figure older than its source's declared freshness SLA renders with a staleness badge. Stale values are never presented as fresh; blanks are never silent.
10. Vendor-claimed values never earn a lead chip in competition with independent values.
11. Implications are tagged X (interpretation), cite the specific cell ids they derive from, carry a confidence level, and state a falsifier. No editorial claim without cited cells.
12. The published page contains only public benchmark data and generic analysis. No personal context, credentials, or private decision framing appears in the repo or the page.

## 3. Governance Operating System

### Roles (define as Claude Code subagents in `.claude/agents/`)

* builder (you, main thread): architecture, implementation, integration, final calls.
* red-team: attacks each phase deliverable using that phase's checklist plus free-form attack. Outputs objections classified BLOCKING, MAJOR, MINOR, each with a concrete failure scenario. Tool scope: read, web search/fetch, run tests. Cannot edit source.
* verifier: independently reproduces factual claims. Re-fetches numbers from primary sources, reruns code, fact-checks briefs sentence by sentence. Reports match/mismatch with evidence. Cannot edit source.
* innovator: for design phases, generates at least 3 materially different alternatives per major decision before the builder converges. Alternatives must be real options with tradeoffs, not strawmen.

### Gate Protocol (every phase)

1. Builder drafts the phase deliverable.
2. Innovator produces alternatives (design phases 2, 3, 5, 6, 7, 8). Builder selects with written rationale.
3. Red-team attacks. Objections logged to `governance/redteam/phase-N.md`.
4. Verifier reproduces every number and factual claim in the deliverable.
5. Builder resolves all BLOCKING and MAJOR objections, or converts them to accepted risks in `governance/RISKS.md` with rationale and a reversal trigger.
6. Write an ADR to `governance/DECISIONS.md`: context, options considered, choice, rejected-because, and the condition that would reverse the decision.
7. Ultrathink self-check against the phase exit criteria. If green, proceed immediately.

### Governance Artifacts (all shipped)

`governance/DECISIONS.md` (numbered ADRs), `governance/RISKS.md` (living register), `governance/redteam/phase-N.md`, `governance/SOURCES.md` (provenance ledger), `governance/EVAL.md` (final self-evaluation), `governance/RUNBOOK.md`, `governance/HANDOFF.md`, `governance/BUILDLOG.md` (running narrative, updated each phase).

## 4. Phase Plan

### Phase 0: Harness

Objective: repo scaffold and governance machinery before any product work. Deliverables: repo layout (Section 5), `CLAUDE.md` project memory encoding the constitutional rules and gate protocol, subagent definitions, `Makefile` with `fetch`, `build`, `check`, `test`, `publish`, `all` targets (stubs acceptable), a PostToolUse hook in `.claude/settings.json` that runs `make check && make test` after edits to collectors, renderer, or template, the seed snapshot committed and pushed, and a connectivity probe that attempts one fetch against each primary source domain from this sandbox, logging any blocked domain to `governance/HANDOFF.md` with the environment network setting to change. Gate: red-team attempts to violate a constitutional rule and confirm the (stub) checks would catch it once implemented; verifier confirms hooks fire. Exit: `make all` runs end to end on seed data alone.

### Phase 1: Research

Objective: verify the world before trusting the spec. The seed is 2026-07-31 vintage; assume drift. Work: confirm each primary source is live and identify its current version (AA index version may have moved past v4.1; confirm current domains for Arena and the Morph board; confirm METR's current publication). Identify machine-readable endpoints (JSON APIs, embedded state, CSV) versus DOM scraping for each, and check ToS/robots posture for automated access. Detect frontier model releases since Jul 31 that qualify for columns. Scout at least 2 candidate sources not in the current list and write include/exclude rationale for each. Grade every source: freshness cadence, stability, independence, breakage risk. Deliverables: `governance/SOURCES.md` ledger plus a fetch-feasibility matrix; a proposed column list for the current landscape. Adversarial gate: red-team challenges each source's independence and each "machine-readable" claim; verifier live-fetches one real value from every source and confirms it parses. Exit: every planned cell has a named source, fetch method, and freshness SLA, or a documented reason it cannot.

### Phase 2: Metric Selection

Objective: every row earns its place. Rule: a metric survives only if it answers "what decision or judgment does this inform for a daily reader tracking the frontier race, price-performance, adoption, and disclosure integrity." Kill criteria: saturated (leaders within noise of ceiling), unmaintained source, confirmed contamination, no decision value, duplicative signal. Innovation: innovator surveys the current eval landscape and proposes candidate additions across at least these axes: long-horizon/agentic capability, reliability and consistency under repetition, safety/robustness signal, efficiency frontier position (quality per dollar). Each candidate gets an add/hold/reject with rationale. Constraint: the matrix must stay scannable in 60 seconds. Hard cap of 22 rows; exceeding it requires cutting something and logging the tradeoff. Adversarial gate: red-team argues the strongest case for cutting each incumbent row and for the most tempting rejected candidate; specifically attacks metrics carrying known integrity issues (METR gaming flags, vendor-modified ARC harnesses) and asks whether presentation adequately quarantines them. Exit: final row set with per-row decision-value statement, all Pro/Verified separation preserved.

### Phase 3: Grouping and Ordering

Objective: groups ordered by decision relevance, descending. This is a directive change from the inherited spec: the reader has specified relevance-first ordering in the style of Apple's compare page, so group position no longer encodes trust. Trust is now carried entirely by the per-cell I/V tags, warning tags, and staleness badges from Section 2, which makes those tags load-bearing; they must read instantly. Work: define "relevance" operationally (what he acts on daily ranks above context he checks occasionally), then order groups, and rows within each group, by it. Draft the "Quick look" stat set for Phase 6: the 4 to 6 highest-signal metrics that lead the page. Decide the default compare trio, the picker catalog scope (which superseded and legacy models remain selectable, the way Apple keeps older Macs in its picker), tie handling for chips, and how newly promoted models enter the catalog and the default. Innovation: innovator drafts at least 3 relevance orderings (decision-frequency, volatility-weighted, capability-domain hybrids) and mocks the daily read for each. Adversarial gate: red-team performs a cold 60-second read of a mockup for each finalist and reports where comprehension breaks. It must specifically attack two hazards: a vendor-claimed number sitting high on the page because it is relevant (do the V tag and warning treatment carry enough weight to prevent it being misread as independent?), and the default trio flattering the home team (the reader works in the industry and needs the unvarnished view, so the default must be justified on neutral grounds). Exit: ADR selecting the ordering, the quick-look set, the default trio, and the catalog scope, with losing alternatives preserved in the record.

### Phase 4: Model and Metric Detail Layer (slide-over briefs)

Objective: the click-through layer that makes every number auditable. Metric brief template: what it measures, harness and version, publication cadence, independence status, known integrity issues, comparability caveats, current value with 30-day sparkline once history accrues, numbered sources, last-verified date. Model brief template: release date, context window, pricing and recent price moves, deployment and data terms, eval coverage map including gaps (what this model has not been measured on, and why per the empty-cell enum). Adversarial gate: verifier selects 3 briefs at random and fact-checks every sentence against primary sources. Any sentence that cannot be verified is cut or explicitly tagged as claim. Red-team checks that briefs surface integrity flags at least as prominently as the headline number. Exit: all briefs pass spot-check with zero unverifiable sentences.

### Phase 5: Implications Layer

Objective: turn cells into "so what" without contaminating the data's integrity. Design: implications live in a visually distinct interpretation layer tagged X, separate from I/V data. Each implication cites cell ids, carries confidence (high/med/low), and states its falsifier ("reverses if ..."). Standing lenses: frontier race position, price-performance frontier, adoption and share momentum, disclosure and integrity watch. Implications regenerate only when a cited cell changes; otherwise they carry forward with their original date visible. Innovation: innovator proposes at least 3 formats (per-group read lines, a single daily read panel, question-answer framing) and the builder selects for scannability. Adversarial gate: for each drafted implication, red-team writes the strongest opposite reading from the same cells. If the opposite reading is equally supported, the implication is downgraded to an open question or reframed. Verifier confirms every citation resolves and no implication mixes Pro/Verified or leans on a flagged cell without carrying the flag. Exit: zero uncited editorial claims anywhere on the page.

### Phase 6: UI (Apple-compare paradigm)

Reference pattern: Apple's Mac compare page (apple.com/mac/compare) is the reader's stated best-in-class comparison UI. Adopt its mechanics, not its skin. The mechanics to reproduce:

* Three side-by-side model slots on desktop, each headed by a picker that swaps any catalog model into that slot. The picker draws from the full catalog (current frontier plus recent and superseded models per the Phase 3 catalog decision), grouped the way Apple separates current from older Macs.
* Sticky compare header: model names and pickers stay pinned while scrolling, so every row reads against its column at any depth.
* A "Quick look" band at the top: the 4 to 6 highest-signal stats per selected model (the Phase 3 quick-look set) before the detailed groups, mirroring Apple's headline row of chip, memory, and battery.
* Grouped detail sections below, ordered most relevant to least per Phase 3, each with a clear section header and rows aligned across the three columns.
* Selection persists across refreshes and days via URL hash (shareable, bookmarkable) with a localStorage fallback, so the daily open lands on his chosen trio with fresh data. First-ever load shows the Phase 3 default trio. This is a plain browser page, so both persistence mechanisms are available.
* Mobile: 2 slots side by side at iPhone width with the same pickers; the third slot is reachable by swapping.
* Field awareness: the compare view shows 3 models, but movement anywhere in the field must stay discoverable. Today's tape remains global across all catalog models, and any model whose cells changed in the last 72 hours gets a movement dot on its picker entry. The innovator may propose an all-models overflow view as an addition, judged against the 60-second scan.

Preserve: chalk background, cobalt and amber accents, Archivo + Public Sans + IBM Plex Mono, slide-over briefs on any metric or model name, Today's tape. Fonts must not break the self-contained constraint: embed subsets or define a graceful system fallback stack, and prove offline rendering either way. Also required: delta-since-yesterday chips, 30-day sparklines in briefs, a pipeline-health footer (last run time, per-source status), and full keyboard navigation extended to the compare mechanics (1/2/3 to focus a slot, arrow or j/k row traversal, Enter to open a brief or picker, Esc to close, / to filter within a picker). The reader is keyboard-first; keyboard nav is not optional. Innovation: innovator proposes at least 3 further upgrades; each must survive the objection "does this slow the 60-second scan." Adversarial gate, all must pass: opens from `file://` with network disabled; renders correctly at iPhone Safari width (~390px) with the 2-up compare working and at desktop; picker swap completes under 100ms with no layout shift; sticky header holds through every group; a newly added catalog model appears in pickers without layout collapse; long-tape stress test; contrast meets WCAG AA; chips and movement dots distinguishable without color; total page weight under 1.5 MB; interactions under 100ms; two consecutive builds from identical data are byte-identical; and a cold read confirms field-wide movement is discoverable within 60 seconds even when the moved model is not in the selected trio. Exit: all checks green and encoded as repeatable tests where automatable.

### Phase 7: Autorefresh (zero input, ever)

Objective: the dashboard updates daily with no human action and degrades loudly, never silently. Architecture (mandatory separation):

* Collectors: one deterministic module per source (Python or Node, builder's call). Each has recorded-fixture tests, a per-source timeout (~60s), retry with backoff, honest User-Agent, and raw-response caching to `raw/` for reparse. Output: normalized cells into `data/YYYY-MM-DD.json`. Prefer documented endpoints over DOM scraping wherever Phase 1 found them.
* Judgment layer (tape editorial line, implication refresh, new-integrity-flag detection): runs `claude -p` headless with a locked prompt file and schema-validated JSON output. Hard rule: the judgment layer may interpret and arrange collected data but may never introduce a number, model, or fact not present in the day's snapshot. Store the input hash and output for every run. If the LLM call is unavailable, degrade to a mechanical tape of cell diffs with no editorial line, and badge the page accordingly.
* Renderer: a pure function from data plus history to HTML. No fetching at render time.
* New-model watch: a candidate model auto-promotes into the picker catalog only when it appears in at least 2 independent group-1 sources; before that it appears in the tape as a watch item. Additions are noted on the page per spec.

Scheduler (ADR still required, but the option space is narrowed): this build runs in an ephemeral cloud sandbox, so nothing may depend on the build machine surviving. GitHub Actions cron is the scheduler and GitHub Pages the host. The ADR covers the specifics: cron time (a UTC hour landing before the reader's Pacific morning), committing daily snapshots back to the repo versus artifact-only (commit-back is presumptively right: it accrues history for sparklines AND counts as repo activity, which prevents GitHub from auto-disabling scheduled workflows on inactive repos), Pages deploy method, an Actions `concurrency` group in place of a lockfile, per-job timeouts, and retry strategy. Include a `workflow_dispatch` trigger so a real run can be observed on demand during Phase 9 instead of waiting for the cron. Runs must be non-interactive end to end with secrets outside the repo. Judgment layer credentials: a headless Claude call in CI requires an `ANTHROPIC_API_KEY` repository secret, which only the human can add. Ship in degraded mechanical-tape mode by default (cell diffs, no editorial line, page badged accordingly) so day one works with zero secrets, and have the workflow detect the secret and upgrade to the editorial layer automatically once it exists. Record the secret step in `governance/HANDOFF.md`. Failure semantics: per-source failure shows last-good value with staleness badge and reason; a failed workflow run surfaces in the page's health footer and through GitHub's own failed-run notifications to the repo owner, which cost zero setup. The page self-reports its own health; no other monitoring is required. Adversarial gate (chaos drills, all must pass, simulated via fixtures and environment flags where the sandbox requires): kill network mid-run; feed one source malformed HTML; simulate a source silently changing its DOM (assert the parse fails loudly rather than emitting a wrong number); trigger two overlapping runs and confirm the concurrency group serializes or cancels them; advance the clock past a freshness SLA and confirm staleness badging; run the full pipeline twice consecutively and confirm the second run is byte-identical or every delta is explained. Exit: the workflow committed and green on a manual dispatch completing with zero interaction, plus all drills green.

### Phase 8: Easy Access

Objective: one tap on iPhone, one keyboard-launched open on Mac, with zero dependence on any machine the reader owns. Decision: GitHub Pages serving the built page from this repo is the presumptive answer, since the repo is already the pipeline's home and Pages survives every device state. The ADR covers the deploy method (deploy-from-branch versus an Actions deploy step), the final URL, and confirmation that publishing is acceptable: Pages from a personal repo is effectively public, which constitutional rule 12 already accounts for by keeping all personal context out of the page and the repo. An innovator pass may still propose alternatives, but any option that depends on the reader's own hardware being awake is disqualified by default. Adversarial gate: red-team tests a cold load on cellular, behavior when a Pages deploy fails mid-update (the previous version must remain served), and a simulated 30-day no-maintenance window (link rot, token expiry, and scheduled-workflow auto-disablement with its mitigation from Phase 7). Exit: the live URL documented, with iPhone home-screen steps and the one-time Pages settings toggle written into `governance/HANDOFF.md` as keyboard steps.

### Phase 9: End-to-End Verification, Self-Evaluation, Handoff

Work: full pipeline run against live sources; diff against the seed snapshot with every delta classified; verifier performs a cold 60-second read and must correctly answer what moved, what is trustworthy, and what it means, from the page alone. `governance/EVAL.md`: score the finished dashboard 1 to 5 with evidence on trustworthiness, scannability, freshness, comparability discipline, implication quality, resilience, and access latency. The verifier countersigns or disputes each score. Any dimension under 4 gets a remediation note or an accepted-risk entry. `governance/RUNBOOK.md`: how to add a model, add or retire a metric, replace a dead source, force a refresh, read the health footer, and recover from a corrupted snapshot. `governance/HANDOFF.md`: the complete batched list of human actions (repo/auth setup if not already done, any secret to place, iPhone home-screen add), each with exact commands or keyboard steps. Exit: Definition of Done (Section 7) fully checked.

## 5. Engineering Standards

Repo layout:

```
collectors/          one module per source, plus fixtures in collectors/fixtures/
data/                dated snapshots; 2026-07-31.seed.json; latest.json symlink or copy
raw/                 cached raw responses (gitignored if large)
site/                template + renderer; output model-eval-monitor.html at repo root or docs/
tests/               unit, invariant linter, e2e dry run
governance/          all artifacts from Section 3
.claude/             agents/, settings.json (hooks), commands/ (/refresh, /gate, /redteam)
Makefile             fetch | build | check | test | publish | all
```

Canonical cell schema (used in snapshots and rendered data attributes):

```
{ value, unit, tag: "I"|"V", source_id, retrieved_at, effort_tier?, flags: [],
  comparability_set, stale: bool, empty_reason?, history_ref }
```

Standards: every collector has recorded-fixture tests; the invariant linter (`make check`) enforces all 12 constitutional rules against both the data files and the built HTML; the renderer is deterministic; every changed cell between consecutive snapshots must appear in the tape or the changelog (an "explainability" test enforces this); commits at every phase boundary with the ADR number in the message; keep history snapshots forever (they are small and power sparklines and diffs).

## 6. Environment Facts

This build runs as a Claude Code cloud session: an ephemeral, isolated, Anthropic-managed sandbox attached to a GitHub repository, controlled from the reader's browser or phone. Consequences: nothing may depend on this machine after the session ends; the repo is the only durable store, so commit and push at every phase boundary; git operations go through the platform's proxy and push to the session's working branch, so finish by ensuring everything is pushed and, if working on a branch, open a PR and say so plainly in the final summary. Outbound network runs through a proxy with configurable limits, so Phase 0 must probe fetchability of every primary source domain and log any blocked domain to `governance/HANDOFF.md` with the environment setting to change. There is no local scheduler, no local notification channel, and no laptop to lean on: scheduling, hosting, and alerting all route through GitHub per Phases 7 and 8. The reader is keyboard-first and prefers keyboard-only interaction everywhere; any instruction you write for the human must use keyboard steps, never mouse steps.

## 7. Definition of Done

`make all` completes twice consecutively with zero prompts, second run byte-identical or fully delta-explained. Scheduler workflow merged and green on one manually dispatched run. All Phase 7 chaos drills green. Invariant linter green on the shipped page. Phase 6 UI checklist green including offline open, iPhone width, keyboard navigation, and the compare pickers with persisted selection. Access verified via the live Pages URL from both devices. Governance complete: at least one ADR per phase, red-team report per phase, current risk register, countersigned EVAL.md, RUNBOOK.md, HANDOFF.md. The cold-read test passes: a fresh reader answers "what moved, what do I trust, what does it mean" in under 60 seconds from the page alone.

## 8. First Actions

1. Ultrathink an execution plan mapping these phases to your workflow; write it to `governance/BUILDLOG.md`.
2. Scaffold Phase 0: repo, CLAUDE.md, subagents, hooks, Makefile stubs, seed snapshot.
3. Run the Phase 0 gate, log ADR-001, and proceed into Phase 1 research without waiting.
