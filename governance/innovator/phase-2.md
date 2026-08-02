# Phase 2 Innovator Report — Metric Candidates and Incumbent Audit

**Role:** innovator (read/run/web only). **Date:** 2026-08-01.
**Inputs:** `/home/user/model-eval-dashboard/governance/BRIEF.md` (Phase 2), `/home/user/model-eval-dashboard/CLAUDE.md`, `/home/user/model-eval-dashboard/governance/SOURCES.md` (Phase 1 ledger S1–S17), `/home/user/model-eval-dashboard/governance/BUILDLOG.md` (Phase 1 delta classification), `/home/user/model-eval-dashboard/data/2026-07-31.seed.json` (16 incumbent rows), plus live web verification performed today (marked "verified 2026-08-01" below; everything else cites the Phase 1 ledger).

**Binding constraints honored throughout:** 60-second daily scan; hard cap 22 rows; rule 5 (Pro/Verified never co-mingled); rule 10 (V never chips against I); every candidate names a source, fetch channel, provenance class, and comparability set.

---

## 1. Three materially different portfolio strategies

Before per-axis candidates, three genuinely shippable shapes for the final row set. They differ in kind: how many *sources* the daily read depends on, and whether the page's identity is "capability tracker," "signal maximalist," or "integrity instrument."

### Strategy A — Consolidated Aggregates
Lean hard on the two A-grade aggregators (AA + Epoch ECI). Add AA's own sub-indices (Agentic Index, hallucination-rate split, derived intelligence-per-dollar) instead of new boards; drop GDPval as redundant with the Agentic Index that contains it. ~15–16 rows, only 6 collector modules, everything 5/5 coverage, nothing partial.
- **FOR:** maximal robustness and scan speed — every row is populated for every column, no empty-cell noise; fewest breakage surfaces for Phase 7.
- **AGAINST:** the frontier-race read becomes hostage to AA's methodology choices (their graders, their task mix); a single methodology change moves half the page at once, and the "independent cross-check" is only one other source deep.
- **60s scan:** fastest of the three — dense, fully-populated matrix, zero "not evaluated" cells.

### Strategy B — Independent-Signal Maximalism
Add every live independent board with any target coverage: SWE-rebench, Vals, FAR.AI security, LiveBench, keep everything incumbent. ~21–22 rows, 10+ collectors, several rows at 1–2/5 coverage.
- **FOR:** no single aggregator can distort the read; new-model promotion (2-independent-source rule) gets more trigger surface; genuinely novel signals (jailbreak resistance, fresh-issue coding) appear nowhere else.
- **AGAINST:** blows the row cap or lives exactly at it with zero headroom for the next model release; sparse rows (FAR.AI 2/5, LiveBench 1/5) cost scan seconds while informing few daily decisions; collector maintenance burden roughly doubles.
- **60s scan:** worst — the eye must skip many reasoned-empty cells; 22 rows is readable only if grouping (Phase 3) is perfect.

### Strategy C — Integrity-Differentiated Portfolio (recommended)
Keep the fully-covered capability core (AA + ECI), add only new rows that either (a) expose a *gap between claimed and verified* (hallucination-rate split, vendor-vs-fresh-issue coding, strict-vs-weighted reliability) or (b) fill an axis nothing incumbent covers (quality-per-dollar). Cut incumbents that no longer differentiate. ~19 rows, 3 slots of headroom, HOLD-list with explicit promotion triggers.
- **FOR:** matches the reader's stated fourth lens (disclosure integrity) — this page's comparative advantage over AA's own site is exactly the provenance/integrity layer, so rows that surface claim-vs-reality gaps earn scan time twice; keeps headroom for the next frontier release.
- **AGAINST:** more judgment-laden than A (which rows count as "integrity-differentiating" is arguable); still adds two new DOM-ish collectors (SWE-rebench, Vals) with real breakage risk.
- **60s scan:** +3 net rows vs seed; scan cost concentrated in rows that answer "do I trust the headline numbers," which is what the reader scans *for*.

The per-axis candidates below are the parts list; §6 shows Strategy C's arithmetic.

---

## 2. Candidates by axis

Provenance/coverage below: "5/5" = Fable 5, Opus 5, GPT-5.6 Sol, Kimi K3, DS V4 Pro all populated. Verification status marked per candidate.

### Axis 1 — Long-horizon / agentic capability

| # | Candidate | Source / endpoint | Prov. | Comparability set | Coverage | Rec |
|---|---|---|---|---|---|---|
| A1 | **AA Agentic Index** (v4.1 sub-index = GDPval-AA v2 + τ³-Banking) | S1 — same fetch as AA Index: API v2 / embedded flight JSON on `/models`; sub-index page `/models/capabilities/agentic` | I | `aa-agentic-index-v4.1` | 5/5 expected (Opus 5 = 55, Sol = 54 directly verified 2026-08-01; remainder inferred — the sub-index is a mandatory 25% component of the v4.1 composite that Phase 1 verified 5/5) | **ADD** |
| A2 | **SWE-rebench resolved rate** (continuously refreshed, post-cutoff GitHub issues) | NEW S18 — `swe-rebench.com` (Nebius team); site board + dedicated HF dataset; paper arXiv:2505.20411 | I | `swe-rebench-window` (window-stamped: scores only comparable within the same issue window) | 4/5 verified 2026-08-01: Fable 64.5 #1, Opus 5 63.4 #3, Sol 62.3 #5, DS V4 Pro 40.2 #14; **Kimi K3 absent** | **ADD** |
| A3 | τ³-Banking standalone row | AA agentic page (I) or llm-stats board (V) | I or V | `tau3-banking` | llm-stats board verified 2026-08-01: **2 models, 0/5 target coverage, 0 verified results** | **REJECT** standalone |
| A4 | Vals Finance Agent v2 (separate from the composite) | S11 — vals.ai per-board pages, DOM scrape | I* (RISK-007 funding question open) | `vals-finance-agent-v2` | 4/5 (no DeepSeek) | **REJECT as separate row** — fold into the single Vals composite row (R1) per ADR-002 |

**A1 rationale (decision value):** the daily question "who is winning *agentic* work, as opposed to benchmarks-at-large" is currently answered only by GDPval Elo — one component. The Agentic Index adds τ³-Banking (multi-step tool-calling under policy constraints — the hardest τ³ domain) at zero new-collector cost. **Duplication warning for the builder:** GDPval-AA v2 is *inside* this index. Two honest options: (i) keep both rows and declare the overlap in both briefs (my recommendation — GDPval's Elo granularity and its own movement are worth a row; the index is the composite view), or (ii) swap Agentic Index in for the GDPval row, freeing one slot. Price both in §6.
**60s effect:** +1 row, always fully populated, same source family — near-zero added scan cost.

**A2 rationale:** this is the strongest single find of this pass. Phase 1 demoted the "Morph board" and left the dashboard with *no independent, target-covering* software-engineering signal (S9 Scale covers 0/5; S13 is 100% vendor self-reports). SWE-rebench fills exactly that hole: independently run (Nebius — a GPU cloud, not a frontier lab), *contamination-free by construction* (only issues filed after model cutoffs; current window 2026-05-15 → 2026-07-01), with 4/5 coverage today and cost/token data attached. Daily decision informed: "are vendor coding claims (S13's 80–95%) holding up on fresh, unseen work (60–65%)?" — the claim-vs-fresh gap is a standing disclosure-integrity read.
**Rule-5 note:** SWE-rebench is neither SWE-bench Pro nor Verified; it must get its own comparability set and a display name that cannot be misread as either ("SWE-rebench (fresh issues)"), and the linter's Pro/Verified separation must be extended so no chip or implication ever treats it as the same scale.
**Collector caveat:** fetch channel (embedded JSON vs HF dataset) needs a collector-time probe; grade estimate B, breakage medium; SLA 45d (window cadence).
**60s effect:** +1 row, one empty cell (Kimi: "not evaluated").

### Axis 2 — Reliability / consistency under repetition

| # | Candidate | Source / endpoint | Prov. | Comparability set | Coverage | Rec |
|---|---|---|---|---|---|---|
| R1 | **Vals composite with strict-vs-weighted reliability gap** rendered as the cell's badge (gap = points lost when partial credit is removed) | S11 — vals.ai SSR HTML | I* (RISK-007) | `vals-index-composite` | 4/5 (no DeepSeek) | **ADD** (one row; the reliability gap rides as a per-cell flag/badge, not a second row) |
| R2 | Terminal-Bench run-to-run stderr (the ±x.x already in S8's payload) surfaced as a consistency badge on the incumbent TB row | S8 — same payload, zero new fetch | I | `terminal-bench-2.1` (unchanged) | matches TB coverage (Fable displayed; Sol provisional) | **ADD as flag, +0 rows** |
| R3 | LiveBench cross-rotation stability (score drift across monthly question swaps) | S12 — GitHub/HF data files | I | `livebench-rotation` | 1/5 verified (Fable only; current release 2026-06-25) | **HOLD** — ADR-002 trigger stands: promote only if ≥3/5 at collector time |
| R4 | τ³-Banking pass^k (probability of succeeding on *all* k repeats — the canonical repetition-consistency metric of the τ family) | none collectable today: AA publishes the index not pass^k; llm-stats τ³ board is 2 models / unverified | — | — | 0/5 | **HOLD with named trigger:** promote the day AA or the τ³ maintainers publish per-model pass^k for ≥3/5 |

**R1 rationale:** strict-vs-weighted is the only *live, independent* repetition-adjacent signal with meaningful coverage: it answers "does this model complete professional agent tasks *fully*, or only mostly," which is the daily adoption question for anyone deploying agents. Keeping it as a badge inside one Vals row (rather than two Vals rows) buys the axis for one slot. Honest caveats carried on the row: DOM scrape (highest breakage in the portfolio), RISK-007 independence question must close before the I tag ships.
**60s effect:** +1 row, one empty cell (DeepSeek), badge legible at a glance.

**R2 rationale:** free. The ± is already in the S8 payload; rendering it costs no slot and converts an invisible number into a "how repeatable is this score" cue. No kill-criteria exposure.

### Axis 3 — Safety / robustness signal

| # | Candidate | Source / endpoint | Prov. | Comparability set | Coverage | Rec |
|---|---|---|---|---|---|---|
| S-1 | **AA-Omniscience hallucination rate** (share of questions attempted-and-wrong — the calibration split, distinct from the incumbent index which nets accuracy against abstention) | S1 — omniscience family; Pro-gated in API, present in keyless `/models` flight JSON per Phase 1 ledger; split confirmed as a separately-tracked published metric (verified 2026-08-01; per-model values for the five need collector-time extraction — the public page excerpt surfaces only its own top/bottom lists) | I | `aa-omniscience-halluc-rate` (direction: lower) | 5/5 expected (index side verified 5/5 in Phase 1; Fable 5 = 40 top of index re-verified today) | **ADD** |
| S-2 | **FAR.AI AI Security Leaderboard** — universal-jailbreak resistance across CBRNE+cyber (launched 2026-07-29) | NEW S19 — `leaderboard.far.ai`; press data: Grok 4.5 = 448 universal jailbreaks found ($58 avg cost-to-jailbreak), Gemini 3.1 Pro = 249 ($278), **Fable 5 = 0, Sol = 0** under 1,500 attacks each | I (independent research nonprofit) | `far-ai-security-v1` | 2/5 (Fable, Sol; Opus 5/Kimi/DS not tested) | **HOLD** — see below |
| S-3 | METR detected-cheating rate as its own row | S5 — prose-only (Sol figure lives in a single NDA'd blog post), no per-model data file | I | — | 1/5 | **REJECT as row** — keep as cell flags on the METR row, where it already lives |

**S-1 rationale:** the assignment's safety axis is best served by the metric that moves daily *deployment* decisions: "when this model doesn't know, does it guess?" The incumbent omniscience index can mask that (a model can score decently by abstaining a lot or by knowing a lot while also confabulating). The split is the direct signal, 5/5 coverage, zero new source risk — it rides the existing S1 collector. This also gives the safety axis an always-populated row, so the axis doesn't depend on the sparse S-2.
**60s effect:** +1 fully-populated row. Consider rendering adjacent to the omniscience index row so the pair reads as "knowledge / calibration" in one eye movement.

**S-2 rationale for HOLD, not ADD:** the signal is genuinely novel and independent (first public ranking of safeguard robustness under standardized attack; a hundredfold cost-to-jailbreak spread is decision-relevant for anyone deploying in regulated contexts) — but it fails collectability today on two grounds I verified directly: (a) coverage 2/5, and (b) machine-readability is poor — the board is a client-side Vite SPA whose data is compiled into a hash-named JS bundle; my bundle scan found **no JSON/CSV endpoint at all** (verified 2026-08-01). A collector would be parsing minified JS that changes filename every deploy. **Promotion trigger (log in HOLD list):** FAR.AI publishes a data file or API, *or* coverage reaches 3/5 — whichever comes first; until then, feed its launch and findings into the disclosure-watch row and tape (the "0 universal jailbreaks vs 448" spread is tape-worthy today).
**60s effect if added prematurely:** a 3-empty-cell row costing scan time daily to inform a decision that changes at most monthly. That is the wrong trade; HOLD is the discipline the row cap exists to enforce.

### Axis 4 — Efficiency frontier position (quality per dollar)

Three materially different mechanisms — a derived ratio row, a categorical frontier row, and a revealed-preference row:

| # | Candidate | Source / endpoint | Prov. | Comparability set | Coverage | Rec |
|---|---|---|---|---|---|---|
| E1 | **Intelligence per dollar** — derived: AA Index ÷ AA cost per task, computed deterministically by the renderer from two already-cited cells, cell flagged `derived from aa-index + cost-per-task` with both parent cell ids | S1 (both parents) | I (derived from two I cells; carries a `derived` flag) | `aa-intelligence-per-usd` | 5/5 (both parents verified 5/5 in Phase 1, incl. DS cost $0.05 → DS ~880 pts/$ vs Fable ~19 pts/$) | **ADD** |
| E2 | Pareto-frontier position — categorical cell per model: "on frontier" / "dominated by {model}", computed from (AA Index, cost per task) across the catalog | S1 (derived) | I-derived, but reads as interpretation | `aa-cost-capability-frontier` | 5/5 | **REJECT as data row; recommend to Phase 5** as a standing implications lens ("price-performance frontier" is already a named lens in the brief — this is its natural mechanical form) |
| E3 | OpenRouter per-model task-spend share (rolling 30d, per task tag — revealed-preference "what people actually pay for") | S3 — `/api/frontend/v1/rankings/task-spend` | I | `openrouter-task-spend` | varies by tag; Kimi K3 becomes capturable (invisible in the incumbent provider-share row) | **ADD as an upgrade to the incumbent openrouter-share row** (+0 rows): render provider token share + per-model code-spend share in the adoption row pair |
| E4 | AA "cost to run Intelligence Index" as a separate raw row | S1 | I | `aa-cost-to-run` | 5/5 | **REJECT** — same signal as the incumbent cost-per-task row at a different scale; duplicative |

**E1 rationale:** the reader's second standing lens is price-performance, and today the page makes him do the division himself across two rows. One derived row collapses it: "DeepSeek delivers ~45× the index-points-per-dollar of the frontier leaders" is *the* open-weights-pressure number, refreshed daily. Constitutional posture: this is arithmetic, not interpretation — deterministic, renderer-computed, both parents cited on the cell, `derived` flag rendered visibly; it must inherit staleness/flags from whichever parent is worse (builder should encode that inheritance rule in the linter). If red-team judges any derivation to be rule-11 territory, the fallback is E2's lens form — but then the efficiency axis has no data row, which I'd argue is the worse outcome for the 60-second scan.
**60s effect:** +1 fully-populated row that *replaces* mental math — arguably net-negative scan cost.

---

## 3. Incumbent audit — one line each (kill criteria: saturated / unmaintained source / confirmed contamination / no decision value / duplicative signal)

1. **aa-index** — no kill criterion; the frontier-race anchor; keep (ECI add is its cross-check).
2. **gdpval-aa** — partial *duplicative signal* if A1 (Agentic Index) is added, since GDPval is a component; keep for Elo granularity but declare the overlap in both briefs.
3. **terminal-bench** — no kill criterion, but thin coverage (1 displayed + 1 provisional of 5) and 45d cadence; keep with agent+effort tuple policy and the R2 stderr badge.
4. **cost-per-task** — no kill criterion; parent of E1; keep.
5. **throughput-ttft** — *no daily decision value*: operational latency detail that informs deployment tuning, not the race/price/adoption/integrity lenses; brief-layer material. **WEAKEST-3.**
6. **swe-bench-pro** — provenance collapsed at Phase 1 (I→V; S13 is 0-of-43 verified) and near-duplicative with swe-bench-verified as "vendor coding claims"; survives *only* if reframed as the vendor-claims row whose brief carries the ~20-pt vendor-vs-standardized gap (S9) as an integrity exhibit — and A2 (SWE-rebench) becomes the independent coding row it was pretending to be.
7. **arc-agi-3** — no kill criterion; 2/5 coverage but highest integrity-theater value on the page (modified-harness saga); keep, Fable cell becomes empty("not published") per Phase 1.
8. **metr-horizon** — *unmaintained source* partially applies (paused since May 8; Sol datum prose-only and NDA'd); keep as the only long-horizon absolute measure, priced by the 90d SLA and cheating/CI flags — expect the red-team attack named in the brief.
9. **arena-elo** — no kill criterion; the daily mover; Style-Control pinning and Leaderboard-Illusion caveat already priced in S2.
10. **openrouter-share** — no kill criterion; adoption lens; upgrade with E3 per-model task-spend (Kimi becomes visible); RISK-006 posture unchanged.
11. **swe-bench-verified** — *saturated* plausibly applies (leader 95.0, within noise of the ceiling on a 500-task set) and it is pure V; residual value is disclosure behavior (Sol's "withheld" cell is genuinely informative); keep narrowly, first in line if a slot is ever needed.
12. **disclosure-watch** — no kill criterion; the page's differentiator; now has a real feed (HF intrusion disclosure, NIST AITE, SWE-Pro verification gap, Sol ARC/METR items, FAR.AI launch).
13. **api-price** — no kill criterion; price cuts are tape events; keep.
14. **context-window** — *no decision value / converged*: Phase 1 verified all five at ≈1M — a row where every cell says the same thing differentiates nothing; brief-layer material. **WEAKEST-3.**
15. **aa-omniscience** — no kill criterion; keep and pair with the S-1 hallucination split.
16. **deployment-terms** — *no daily decision value in matrix form*: never populated in the seed, manual curation, near-zero churn; belongs in model briefs (Phase 4 template already requires it there). **WEAKEST-3.**

**Three weakest incumbents: throughput-ttft, context-window, deployment-terms** — all three demote to the Phase 4 brief/quick-look layer rather than being deleted from the data model (the collector cost of keeping them in snapshots is ~zero; the cost being cut is *scan* cost). Fourth-weakest, explicitly: swe-bench-verified (saturated + V), retained only for its withholding signal.

---

## 4. Row budget arithmetic (cap = 22)

| Move | Rows |
|---|---|
| Incumbent rows (seed) | 16 |
| Cut to brief layer: throughput-ttft, context-window, deployment-terms | −3 → **13** |
| ADD Epoch ECI (S10; ADR-002 include; frontier-race cross-check, 5/5) | +1 → 14 |
| ADD A1 AA Agentic Index (S1, 5/5) | +1 → 15 |
| ADD A2 SWE-rebench (new S18, 4/5) | +1 → 16 |
| ADD R1 Vals composite w/ strict-gap badge (S11, 4/5; ADR-002 include) | +1 → 17 |
| ADD S-1 Omniscience hallucination rate (S1, 5/5) | +1 → 18 |
| ADD E1 Intelligence per dollar (S1-derived, 5/5) | +1 → **19** |
| E3 task-spend + R2 stderr badge (upgrades to existing rows) | +0 |
| **Headroom under cap** | **3** |

Variant if the builder swaps A1 in *for* GDPval (dedup option): 18 rows, 4 headroom.
HOLD list with named promotion triggers (consumes headroom only when triggered): LiveBench (≥3/5 coverage), FAR.AI security (data endpoint exists or ≥3/5), τ³ pass^k (per-model publication ≥3/5), AA Coding Index (only if a coding-claims row is cut).

---

## 5. Summary comparison

| Candidate | Axis | Source | Prov. | Coverage | New collector? | Rec |
|---|---|---|---|---|---|---|
| AA Agentic Index | agentic | S1 | I | 5/5 | no | ADD |
| SWE-rebench | agentic + integrity | S18 (new) | I | 4/5 | yes (med risk) | ADD |
| Vals composite + strict-gap | reliability | S11 | I* | 4/5 | yes (high risk) | ADD |
| TB stderr badge | reliability | S8 | I | as TB | no | ADD (+0 rows) |
| Omniscience halluc. rate | safety | S1 | I | 5/5 | no | ADD |
| Intelligence per $ | efficiency | S1 derived | I+flag | 5/5 | no | ADD |
| OpenRouter task-spend | efficiency/adoption | S3 | I | partial | no | ADD (+0 rows) |
| FAR.AI security | safety | S19 (new) | I | 2/5 | yes (no endpoint) | HOLD |
| LiveBench | reliability | S12 | I | 1/5 | yes | HOLD |
| τ³ pass^k | reliability | none | — | 0/5 | — | HOLD |
| τ³-Banking standalone | agentic | llm-stats | V | 0/5 | — | REJECT |
| AA cost-to-run raw | efficiency | S1 | I | 5/5 | no | REJECT (dup) |
| Pareto frontier row | efficiency | S1 derived | X-ish | 5/5 | no | REJECT as row → Phase 5 lens |

**Recommendation:** Strategy C — 13 incumbents kept + 6 adds = 19 rows, 3 headroom, every axis covered by at least one fully-verified ADD, and every HOLD carrying a named, checkable promotion trigger. The builder decides; the option space above is complete enough to defend whichever shape survives the gate.

**Red-team handoff notes:** (1) E1's derived-cell status is the most attackable constitutional surface — pre-write the flag-inheritance rule; (2) A2 requires extending rule-5-style set separation to a third SWE-family scale; (3) R1 ships I-tagged only if RISK-007 closes; (4) A1/GDPval overlap must be declared in both briefs or red-team will call it double-counting.

Sources consulted today: [AA Intelligence Index v4.1 article](https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-1), [AA agentic leaderboard](https://artificialanalysis.ai/models/capabilities/agentic), [AA-Omniscience](https://artificialanalysis.ai/evaluations/omniscience), [AA-Omniscience methodology paper](https://arxiv.org/html/2511.13029v1), [FAR.AI leaderboard launch (PRNewswire)](http://www.prnewswire.com/news-releases/farai-launches-ai-security-leaderboard-revealing-hundredfold-gap-in-frontier-ai-model-safeguards-302838216.html), [FAR.AI leaderboard](https://leaderboard.far.ai), [SWE-rebench](https://swe-rebench.com/), [τ³-bench overview](https://benchmarkingagents.com/tau3-bench/), [llm-stats τ³-Banking board](https://llm-stats.com/benchmarks/tau3-banking), [Adam Gleave on the AI Security Leaderboard](https://www.cognitiverevolution.ai/is-offense-or-defense-dominant-far-ai-s-adam-gleave-on-the-ai-security-leaderboard/).
