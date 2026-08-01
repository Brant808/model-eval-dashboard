# ROWS — Phase 2 Metric Registry (builder draft pending gate)

Survival rule (brief Phase 2): a row lives only if it answers "what decision or
judgment does this inform for a daily reader tracking the frontier race,
price-performance, adoption, and disclosure integrity." Hard cap 22.

Decision baseline: innovator Strategy C (`governance/innovator/phase-2.md`),
selected with modifications: LiveBench promoted from HOLD to ADD (its ≥3/5
coverage condition was gate-verified at 5/5), Epoch ECI displayed as published
(not recomputed) with its mixed-provenance caveat flag carried on every cell.

**Final set: 20 matrix rows (2 headroom). 3 seed rows demoted to the brief
layer (still collected, never matrix-rendered). Nothing deleted from the data
model.**

## Matrix rows

| # | Row (metric id) | Source / tag | Coverage | Decision value (the daily question it answers) |
|---|---|---|---|---|
| 1 | AA Intelligence Index v4.1 (`aa-index`) | S1 / I | 5/5 | Who leads the frontier race on the broadest independent composite, and did the order change overnight? |
| 2 | Epoch Capabilities Index (`epoch-eci`) | S10 / I +caveat | 5/5 | Does a second, differently-built aggregate corroborate the AA read — is a "lead" methodology-robust or aggregator-specific? |
| 3 | GDPval-AA v2 Elo (`gdpval-aa`) | S1 / I +Gemini-grader caveat | 5/5 | Who wins on judged real-economy deliverables, at Elo granularity (the sharpest single agentic-work signal)? Declared overlap: component of row 4. |
| 4 | AA Agentic Index (`aa-agentic-index`) | S1 / I | 5/5 | Who leads specifically on agentic work (GDPval + τ³-Banking composite) as opposed to benchmarks-at-large? Declared overlap with row 3 in both briefs. |
| 5 | Arena text Elo, Style Control (`arena-elo`) | S2 / I +private-variant caveat | 5/5 | What do blind human preferences say today — the fastest-moving daily signal and release-settling detector. |
| 6 | Terminal-Bench 2.1 (`terminal-bench`) | S8 / I +self-run caveat | 1/5 | Who actually completes real terminal/agent work under a verified harness (agent+model+effort tuples, reward-hacks deducted)? |
| 7 | SWE-rebench fresh-issue resolve rate (`swe-rebench`) | S20 / I | 4/5 | Do coding claims hold on issues filed AFTER training cutoffs — the contamination-free coding read the demoted "Morph board" was pretending to be. |
| 8 | SWE-bench Pro vendor claims (`swe-bench-pro`) | S13+S14 / V | 4/5 | What are labs CLAIMING on their own coding harnesses — and how big is the claim-vs-verified gap (S9 standardized runs ~20 pts colder)? Quarantined: all-V row, chip-ineligible by construction. |
| 9 | LiveBench (`livebench`) | S12 / I | 5/5 | When a launch posts a big number, does it survive monthly-rotated, ground-truth-scored questions (memorization vs capability)? |
| 10 | METR 50% time horizon (`metr-horizon`) | S5+S18 / I +flags | 2/5 | How long an autonomous task can the frontier actually sustain — the only absolute long-horizon measure anyone publishes. |
| 11 | ARC-AGI-3 (`arc-agi-3`) | S4 / I, effort tiers | 2/5 | How much genuine-novelty headroom exists beyond memorized skills, at what effort tier and cost — plus the field's loudest integrity theater (modified-harness saga). |
| 12 | SWE-bench Verified self-reports (`swe-bench-verified`) | S14/S17 / V | 2/5 populated + 1 withheld | Narrow retention (nearest kill: saturated, 95.0 near ceiling): who publishes, who WITHHOLDS — Sol's empty cell is the signal. First row cut if a slot is needed. |
| 13 | Disclosure watch (`disclosure-watch`) | S0 / I | 5/5 | Which lab currently owes the field an explanation — the page's disclosure-integrity differentiator. |
| 14 | AA-Omniscience index (`aa-omniscience`) | S1 / I +Gemini-grader caveat | 5/5 | Net knowledge quality: does the model know things without being penalized for confabulation? |
| 15 | AA-Omniscience hallucination rate (`aa-halluc-rate`) | S1 / I +Gemini-grader caveat | 5/5 | The deployment-safety split: when it doesn't know, does it guess? (A model can hide high confabulation inside a decent net index.) Direction: lower. |
| 16 | Cost per task (`cost-per-task`) | S1 / I | 5/5 | What does frontier work actually cost to run today (cache-aware, per II task)? |
| 17 | Intelligence per dollar (`intelligence-per-dollar`) | S1 / I, derived | 5/5 | The price-performance frontier in one number: index points per task-dollar (the open-weights-pressure gauge). Derived = aa-index ÷ cost-per-task; carries `derived` flag citing both parents; inherits worst-parent staleness/flags. |
| 18 | API list price (`api-price`) | S14–S17/S1 / V | 5/5 | Did anyone move list prices (price-war tape events land here)? |
| 19 | OpenRouter share (`openrouter-share`) | S3 / I +unit caveat | 4/5 + per-model spend flags | Where is real routed demand going — tokens (volume lane) vs spend (premium lane), provider AND per-model views? |
| 20 | Vals professional index (`vals-index`) | S11 / I +VC-funding caveat | 4/5 | Does frontier capability convert into completed professional work — with the strict-vs-weighted gap as the live reliability-under-repetition badge? |

## Demoted to brief layer (collected, not matrix-rendered)

- `throughput-ttft` — operational tuning detail; no daily race/price/adoption/integrity decision. Lives in model briefs + possible quick-look stat (Phase 3 decides).
- `context-window` — converged (all five ≈1M); differentiates nothing daily. Model briefs.
- `deployment-terms` — near-zero churn, manual curation; Phase 4 model-brief field per the brief's own template.

## Rejected / held (with named triggers)

- **REJECT** τ³-Banking standalone (0/5 coverage, unverified board), Vals per-domain rows (composite + badge covers the axis in one slot), AA cost-to-run raw (duplicates row 16 at another scale), Pareto-frontier categorical row (interpretation, not data → handed to Phase 5 as the price-performance lens's mechanical form).
- **HOLD** FAR.AI Security Leaderboard — novel jailbreak-resistance signal (Fable 0 universal jailbreaks vs Grok 448 under 1,500 attacks) but 2/5 coverage and NO machine-readable endpoint (hash-named JS bundle). Triggers: data endpoint appears OR coverage ≥3/5. Its launch feeds disclosure-watch/tape meanwhile.
- **HOLD** τ³ pass^k — the canonical repetition-consistency metric; nobody publishes per-model pass^k today. Trigger: AA or τ³ maintainers publish it for ≥3/5.
- **HOLD** Scale SEAL standardized SWE-Pro as a ROW — the independent coding view (S9) covers 0/5 target models; it serves the page today as the claim-vs-verified gap exhibit inside row 8's brief. Trigger: ≥2/5 target-model coverage.

## Kill-criteria audit of survivors

Every kept row was audited against: saturated / unmaintained source / confirmed
contamination / no decision value / duplicative signal. Flagged nearest-to-kill:
row 12 (saturated + pure V — retained narrowly for withholding signal; first
out), row 10 (source paused since May 8 — priced via 90d SLA + flags; sole
absolute long-horizon measure so retained), rows 3/4 (declared overlap — both
retained for Elo granularity vs composite view; if the cap ever binds, row 3
folds into row 4's brief).

## New instrumentation this phase requires

- New ledger entry S20 (SWE-rebench) — added to SOURCES.md.
- New metric ids: `epoch-eci`, `aa-agentic-index`, `swe-rebench`, `livebench`,
  `aa-halluc-rate`, `intelligence-per-dollar` (derived), `vals-index`.
  They enter snapshots when their collectors land (Phase 7); until then they
  are registry entries here. Comparability sets: `epoch-eci`,
  `aa-agentic-index-v4.1`, `swe-rebench-window-<start>` (window-stamped),
  `livebench-<release>` (release-stamped), `aa-omniscience-halluc` (lower),
  `aa-intelligence-per-usd`, `vals-index-composite`.
- Derived-cell convention (row 17): value computed in the pipeline (not the
  renderer), flag `derived: aa-index ÷ cost-per-task` plus parent cell ids,
  stale = OR(parents.stale), integrity flags = union(parents').
