# SOURCES — Provenance Ledger

Every `source_id` in any snapshot resolves to an entry here. Entries carry URL,
fetch method, retrieved-at, and a machine-read `Independence:` line — the
invariant linter enforces that no cell citing a `vendor`-classified source can
ever be tagged `I` (rule 10 hardening, Phase 0 gate).

Ledger status: **Phase 1 verified (2026-08-01), gate-corrected** — entries
S1–S13 were directly probed by the Phase 1 research pass and re-fetched by the
gate verifier (workflows `wf_3d319f0f`, `wf_23a0fe43`); S14 was verifier-probed;
S15–S17 are declared from AA-relayed data and probed at collector build.
`Retrieved-at` carries date-only precision except where a source declares its
own data vintage. Collector convention (Phase 7): `retrieved_at` on cells = the
source's own declared data vintage where it declares one (ARC `generatedAt`,
Arena `leaderboard_publish_date`, METR page LAST-UPDATED), else the fetch time.

Machine-read lines the linter enforces: `Independence:` (first word:
vendor ⇒ cells must be V), `Sunset: YYYY-MM-DD` (no newer snapshot may cite the
source), `Caveat-flags: a; b@metric-prefix` (cells citing the source must carry
these flags verbatim so the page renders the caveat — rule 7 at source level).

## Fetch-feasibility matrix

| id | Source | Best method | Endpoint | Auth | ToS posture | Cadence | SLA (h) | Grade | Breakage |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Artificial Analysis | json-api (+embedded-json fallback) | `/api/v2/language/models/free`; keyless: flight JSON in `/models` | free key (100 req/d) for API; none for embedded | robots open; attribution required on all tiers | same/next-day on releases; perf daily | 72 | A | low (API) / medium (embedded path — sole channel for GDPval + Omniscience) |
| S2 | Arena (text Elo) | json-api (official HF dataset) | HF `lmarena-ai/leaderboard-dataset`, config `text_style_control`, split `latest` | none | arena.ai ToS bars scraping the SITE; HF dataset (CC-BY-4.0) is the sanctioned channel | daily ~03:00 UTC, 1–2d lag | 96 | A | low |
| S3 | OpenRouter | json-api (undocumented frontend) | `/api/frontend/v1/rankings/market-share`, `.../task-spend` | none | robots open; ToS (upd. 2026-07-27) has anti-scraping clause — tension, see RISK-006 | market-share weekly buckets w/ intra-week updates; task-spend rolling 30d | 72 | B | medium |
| S4 | ARC Prize (ARC-AGI-3) | json-api | `arcprize.org/media/data/leaderboard/v3.json` | none | robots open; ToS boilerplate anti-datamine; fetching the frontend's own JSON 1×/day = low risk; optional written OK via published contact | file regenerated ~daily; results ≤30d post-release per policy | 1080 (45d) | A | medium |
| S5 | METR time horizons | csv/yaml (+embedded-json fallback) | `metr.org/assets/benchmark_results_1_1.yaml` (follow page `#raw-data-link`) | none | robots open; page invites data download | event-driven, 2–5 wk when active; currently paused since May 8 | 2160 (90d) | B | low |
| S6 | ~~"Morph-tracked SWE-bench Pro board"~~ **DEMOTED, do not collect** | none (bot-blocked) | morphllm.com/swe-bench-pro | n/a | robots.txt itself 429-challenged | editorial, >30d stale | — | D | high |
| S7 | Vendor disclosures (generic, seed-era) | manual | per-vendor pages | n/a | n/a | n/a | 336 | — | — |
| S8 | Terminal-Bench 2.1 | embedded-json (+github-data fallback) | `tbench.ai/leaderboard/terminal-bench/2.1`; `raw.githubusercontent.com/harbor-framework/terminal-bench-2-1` (Apache-2.0) | none | no robots.txt; data Apache-2.0 on GitHub | event-driven (submission merges); last row 2026-07-11 | 1080 (45d) | B | medium |
| S9 | Scale SEAL SWE-bench Pro (standardized public set) | embedded-json | `labs.scale.com/leaderboard/swe_bench_pro_public` | none | no robots.txt; no anti-automation text observed | batches every 1–3 months | 2160 (90d) | B | medium |
| S10 | Epoch AI Benchmarking Hub / ECI | csv | `epoch.ai/data/eci_benchmarks.csv` | none | CC-BY; pip client available | multiple updates/month | 336 (14d) | A | low |
| S11 | Vals AI (professional-domain benchmarks) | dom-scrape (SSR HTML) | `vals.ai/benchmarks` (+ per-board pages) | none | no restriction found; verify placement-payment question at gate | ~weekly–biweekly per board | 504 (21d) | B | high |
| S12 | LiveBench | github-data / HF datasets | LiveBench GitHub repo + HF datasets (site is JS-only) | none | open data | monthly question rotation | 1080 (45d) | B | medium |
| S13 | llm-stats SWE-bench Pro aggregate (ALL vendor self-reports) | embedded-json | `llm-stats.com/benchmarks/swe-bench-pro` | none | robots: pages allowed, `/api/` disallowed | near-continuous | 72 | B | medium |
| S14–S17 | Vendor pricing/model pages (Anthropic, OpenAI, Moonshot, DeepSeek) | dom/manual per page | see entries | none | public marketing pages | on release/price change | 336 | — | low |

---

### S0 — Approved v2 brief (seed snapshot)
- URL: governance/BRIEF.md
- Method: seed (manual transcription from the approved v2 spec of 2026-07-31)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: n/a (transcription vehicle; underlying provenance carried per-cell via S1–S7)
- Notes: seed-only. Phase 1 refuted parts of the seed (see Delta Classification in BUILDLOG): Arena Kimi 1547 (transcription error), SWE-bench Pro provenance (vendor aggregate, not independent), ARC Fable 16.6 (not on the verified board).

### S1 — Artificial Analysis
- URL: https://artificialanalysis.ai
- Method: json-api — documented Data API v2 (`/api/v2/language/models/free`, x-api-key header, free tier 100 req/day) covers AA Index + cost-per-task + output speed + TTFT/TTFA; GDPval-AA and AA-Omniscience are Pro-gated in the API but present keyless in the `/models` page embedded flight JSON (`initialModels`), which is the Phase 7 fallback channel
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent evaluator with disclosed lab-revenue exposure (gate-corrected 2026-08-01): AA runs its own evals on first-party endpoints, but its business model is enterprise insight subscriptions AND private custom benchmarking sold to AI companies — i.e., ranked labs can be paying customers, separated from the public leaderboard only by AA's stated policy ("no one pays to be on the leaderboard"; "mystery shopper" accounts). Equity per secondary sources: AI Grant/Friedman/Gross/Ng. Methodological dependency: Gemini models are the graders for GDPval-AA and AA-Omniscience (LLM-judge family bias risk — escalates to a conflict if a Google model is ever scored by its own family; auto-escalation noted in RUNBOOK). Terms-of-Use PDF posture: verify at collector build.
- Caveat-flags: Gemini-graded (AA judge panel)@gdpval-aa; Gemini-graded (AA judge panel)@aa-omniscience; Gemini-graded (AA judge panel)@aa-halluc-rate; Gemini-graded (AA judge panel)@aa-agentic-index
- Freshness SLA: 72h
- Covers: AA Intelligence Index v4.1 (confirmed current version, "June 2026—current"), GDPval-AA v2 Elo, cost per task (v4.1 cache-aware methodology), throughput/TTFT, AA-Omniscience, context windows, list prices
- Grade: A. Breakage: low (documented API) / medium (embedded-JSON path).
- Verified values 2026-08-01: AA Index — Opus 5 (max) 60.69 #1, Fable 5 (w/ fallback) 59.86 #2-by-slug (#3 counting effort variants), Sol (max) 58.89, Kimi K3 (max) 57.11, DS V4 Pro 44.27; GDPval — 1857.8 / 1746.06 / 1732.5 / 1687.43 / 1304.49 (DS newly published); cost/task $2.34 / $3.15 / $1.86 / $0.86 / $0.05; Omniscience 31.27 / 40.15 / 21.7 / 18.42 / −10.02; context windows all ≈1M.
- Attribution required on all tiers (visible footer link satisfies).

### S2 — Arena (text leaderboard; formerly LMArena)
- URL: https://arena.ai/leaderboard (values); collection channel: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- Method: json-api — official HuggingFace dataset (CC-BY-4.0), config `text_style_control` (matches the site's default Style Control board), split `latest`; parquet or datasets-server filter API; committed daily ~03:00–03:05 UTC with 1–2 day lag vs site
- Retrieved-at: 2026-08-01T03:00:00Z
- Independence: independent crowdsourced pairwise preference (Bradley–Terry), not vendor-run; caveats: VC-funded company with commercial lab relationships; "Leaderboard Illusion" critique (private variant testing — demonstrably still active via anonymized codenames); style bias mitigated by Style Control (default board)
- Caveat-flags: private variant testing active (Arena)
- Attribution: HF dataset is CC-BY-4.0 — page must attribute Arena/LMArena, link the license, and note any transformation.
- Freshness SLA: 96h
- Covers: Arena text Elo. Collector MUST pin (board=text, category=overall, style_control=on) — raw vs style-control boards reorder the top (SC #1 Fable 5 1508.6; raw #1 Opus 5 Max 1511.6). Ratings shift on daily whole-board refits: store rank+rating+publish_date together. Display-name churn hazard: kimi-k3 → kimi-k3-max (Jul 26); deepseek-v4-pro-high-preview (site) = deepseek-v4-pro-thinking (HF).
- Grade: A. Breakage: low.
- Verified values (SC board, cutoff 2026-08-01T03:00Z): Fable 5 1508.6 #1; Opus-5-high 1491.8 #6; Opus-5-max 1490.4 #7; Kimi K3 (max) 1485.3 #12; Sol (xhigh) 1482.8 #14 (added to text board Jul 31); DS V4 Pro 1457.9 #47. SEED REFUTED: Kimi 1547 #2 never existed in the dataset's full history.

### S3 — OpenRouter rankings
- URL: https://openrouter.ai/rankings
- Method: json-api (undocumented frontend API, no auth): `/api/frontend/v1/rankings/market-share` (52 weekly author-level buckets of raw token counts, top ~9 authors + others) and `/api/frontend/v1/rankings/task-spend` (rolling 30d spend, 29 task tags × top-10 models with share + deltaPp)
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent usage telemetry (marketplace routing data, not lab self-report). Structural bias: only OpenRouter-routed traffic — first-party/direct-API volume invisible, so premium providers (Anthropic) undercount on token share while leading spend
- Caveat-flags: unit per page copy ambiguous (counts consistent with tokens)
- Freshness SLA: 72h
- Covers: provider token share (unit caveat: endpoint returns unlabeled counts; magnitudes only plausible as tokens; page copy says "request share" — carry "unit per page copy ambiguous" flag); per-MODEL spend share via task-spend (new capability vs seed — Kimi K3 capturable here though invisible in provider share)
- ToS/robots: robots.txt permissive; ToS updated 2026-07-27 has an anti-scraping clause — direct tension. Collector posture: one polite fetch/day of the two JSON endpoints the page itself loads, honest UA — logged as RISK-006 with reversal trigger (any block, header, or objection ⇒ drop to "source down" handling and seek permission).
- Grade: B. Breakage: medium (undocumented endpoint names).
- Verified values (2026-08-01): token share, last complete week 2026-07-20 — DeepSeek 17.4% (#2 behind xiaomi 19.1%!), Anthropic 9.1% (down from ~13% seed — real decline), OpenAI 6.9%, Google 8.4%; partial wk 07-27: DeepSeek 20.9% #1, Anthropic 8.7%, OpenAI 8.6%. Moonshot below top-9 since May (bucketed into "others"). Anthropic ≈44% of code-category spend (confirms seed's "leads programming spend"); code = 25% of all OpenRouter spend.

### S4 — ARC Prize (ARC-AGI-3 Verified Leaderboard)
- URL: https://arcprize.org/leaderboard (values); collection: https://arcprize.org/media/data/leaderboard/v3.json
- Method: json-api — the leaderboard front-end's own pre-joined JSON: top-level keys `{version, generatedAt, datasets, evaluations}`; rows live under `evaluations[]` with `modelId` / `modelDisplayName` / `score` (a 0–1 FRACTION — multiply by 100 for display; 0.3016 = 30.16%) / `cost`; on 404, re-derive path from `/scripts/leaderboard/data.js` (gate-corrected field names/units)
- Retrieved-at: 2026-07-31T22:31:25Z (file generatedAt; fetched 2026-08-01)
- Independence: independent nonprofit; ALL official scores run by ARC Prize Foundation on the Semi-Private set with academic oversight (NYU/SFI/Columbia); vendor self-reports categorically excluded; donor labs disclosed, no privileged access. Footnote: the published $10k per-run cost cap is evidently waived for headline runs (three rows pinned at exactly $10,000 vs $20.6k Opus 5 and $25.1k Sol Max records)
- Freshness SLA: 1080h (45d; policy publishes ≤30d after release/eval)
- Covers: ARC-AGI-3 with effort tiers (one row per model+tier; tier in modelId suffix and display suffix)
- Grade: A. Breakage: medium (undocumented internal asset path).
- Verified values (v3.json, 2026-07-31T22:31Z): Opus 5 (High) 30.16% #1 SOTA, $20,657/run (seed 30.2 confirmed, tier High); Sol (Max) 7.78% $25,064 — seed's 7.8 tier RESOLVED = Max; full Sol tier curve xHigh 6.99 / High 2.15 / Med 1.07 / Low 0.33. **Fable 5 ABSENT** from the verified board at any tier — seed's 16.6 is not reproducible from any official source (ARC Prize X post: "≈20% on Public Demo environments", approximate, non-comparable set). Kimi K3: on v1/v2 boards only, not v3 (seed "not evaluated" confirmed). DeepSeek: absent entirely (confirmed). Sol's 38.3 vendor claim (Responses API, retained reasoning + compaction, PUBLIC set) is NOT on the verified board — official file regenerated after the claim, unchanged; keep modified-harness flag.

### S5 — METR time horizons
- URL: https://metr.org/time-horizons/
- Method: csv/yaml — `metr.org/assets/benchmark_results_1_1.yaml` (per-model p50/p80 + CIs, SOTA flags, doubling time; version-suffixed filename — collectors should follow the page's `#raw-data-link` href AND assert the suite version from file CONTENT, since page JS toggles the same href between the v1.0 and v1.1 files); equivalent embedded JSON (`benchmarkDataV1_1`) in the page; analysis code + raw runs at github.com/METR/eval-analysis-public
- Retrieved-at: 2026-08-01T00:00:00Z (data vintage: page LAST UPDATED 2026-05-08)
- Independence: independent nonprofit, self-run evals; caveats carried as flags: Sol pre-deployment eval was NDA'd with OpenAI comms/legal review of the post; Anthropic early access implies lab cooperation
- Freshness SLA: 2160h (90d — METR's own cadence is event-driven/irregular; page warns coverage is incomplete)
- Covers: 50% (and 80%) task-completion time horizon, suite METR-Horizon-v1.1
- Grade: B (methodology/transparency best-in-class; cadence irregular, Sol datum prose-only). Breakage: low.
- Verified values: **Fable 5 → measured as "Claude Mythos Preview (early)"**: p50 17.4h, 95% CI 8.5–55.1h, is_sota, with METR's notice "Measurements above 16 hrs are unreliable with our current task suite" (seed's "≥16h" corrected to point estimate + CI + unreliability flag). **Sol: 11.3h [5–40h] exists ONLY in the 2026-06-26 blog post** (not in any leaderboard/data file); METR's own term is "cheating" ("detected cheating rate was higher than any public model we have evaluated"; alternates: >270h counting cheats as successes, 71h discarding them; "we do not consider any of these numbers to represent a robust measurement"). Opus 5 / Kimi K3 / DS V4 Pro: not evaluated (confirmed; closest: Opus 4.6 11.98h, Kimi K2 Thinking 0.96h on v1.0, DeepSeek V3-era only).

### S6 — "Morph-tracked SWE-bench Pro board" (DEMOTED and SUNSET at Phase 1 gate — do not collect)
- URL: https://www.morphllm.com/swe-bench-pro
- Method: none viable (every request incl. robots.txt returns HTTP 429 Vercel Security Checkpoint; latest Wayback capture 2026-07-01, content "verified June 28")
- Retrieved-at: 2026-08-01T00:00:00Z (verification attempt)
- Sunset: 2026-07-31
- Independence: presumed-independent in the seed — REFUTED 2026-08-01 (classification deliberately neutral so the frozen 2026-07-31 seed still resolves; the Sunset line is the machine-enforced ban). Morph is a code-tooling vendor; the page is editorial/SEO aggregation republishing (a) Scale's SEAL standardized board and (b) llm-stats.com's vendor-self-report aggregate. The seed's S6 numbers trace to llm-stats (verified_count: 0, self_reported_count: 43) — vendor-grade data that the seed mistakenly carried as independent.
- Status: replaced by S13 (llm-stats aggregate, vendor-classified) + S9 (Scale SEAL standardized, independent). The linter rejects any snapshot dated after 2026-07-31 that cites S6 (Phase 1 gate BLOCKING resolution); the corrected 2026-08-01 snapshot re-sources and re-tags these cells.

### S7 — Vendor disclosures (generic, seed-era)
- URL: per-vendor pages (see S14–S17 for the split introduced in Phase 1)
- Method: seed (manual transcription); Phase 7 collectors cite S14–S17 instead
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: vendor-claimed — every cell citing S7 must be tagged V (linter-enforced)
- Freshness SLA: 336h

### S8 — Terminal-Bench 2.1 (official board)
- URL: https://www.tbench.ai/leaderboard/terminal-bench/2.1
- Method: embedded-json — full leaderboard in the page's RSC flight payload AND as SSR HTML table (no JS needed); fallback github-data: per-submission JSONs (Apache-2.0) at github.com/harbor-framework/terminal-bench-2-1 (raw.githubusercontent reachable from sandbox; api.github.com is not)
- Retrieved-at: 2026-08-01T00:00:00Z (board updated_at 2026-07-14; newest row 2026-07-11)
- Independence: independent maintainers (Stanford/Laude Institute lineage, harbor-framework org) — gate-corrected 2026-08-01: submitters RUN THEIR OWN trials ("you must run at least 5 trials per task and upload them", repo README); maintainer verification is log-level review plus an LLM reward-hack judge with visible deductions, NOT re-execution. Materially weaker than evaluator-executed sources (ARC/METR/AA); maintainers do also run a neutral reference agent (Terminus 2) on some rows.
- Caveat-flags: self-run by vendor, log-audited by maintainers
- Freshness SLA: 1080h (45d; event-driven submission cadence)
- Covers: Terminal-Bench 2.1 accuracy. COMPARABILITY HAZARD: every score is an agent+model+effort tuple (Fable 5 spans 83.8 Claude-Code-xhigh to 80.4 Terminus-2-high). Dashboard policy (Phase 2): best-per-model with agent+effort recorded in the cell flags.
- Grade: B. Breakage: medium.
- Verified values: Fable 5 83.8%±1.2 rank 1 (Claude Code v2.1.167, xhigh; hack adj −0.2%). Sol 76.2%±1.3 exists ONLY as a merged repo JSON (PR #102), absent from the 17 displayed rows — treat displayed board as canonical, repo value provisional. Opus 5 / Kimi K3 / DS V4 Pro: not listed (closest: Opus 4.8 78.9% #5; TB 2.0-only Kimi K2.5 43.2, DeepSeek V3.2 39.6 — different comparability set).

### S9 — Scale SEAL SWE-bench Pro (standardized, public set)
- URL: https://labs.scale.com/leaderboard/swe_bench_pro_public
- Method: embedded-json — 25-row entries[] in the page's flight payload (model/rank/score/CI/createdAt); harness open-sourced (github.com/scaleapi/SWE-bench_Pro-os)
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent-run standardized evals (Scale runs the harness itself) — BUT organizational caveat: Meta holds ~49% of Scale (Jun 2025), so treat Meta-model rows with a conflict flag; for non-Meta comparisons the standardized harness is the only independent SWE-bench Pro view that exists
- Caveat-flags: operator conflict — Meta owns ~49% of Scale
- Freshness SLA: 2160h (90d; batch additions every 1–3 months)
- Covers: SWE-bench Pro standardized Pass@1, public 731-task set. Coverage gap: NONE of the five dashboard models are on it (leader: Muse Spark 1.1* 61.5; the standardized leader sits ~20pts below vendor-harness claims — the cross-harness gap is itself a dashboard-worthy integrity signal).
- Grade: B. Breakage: medium.

### S10 — Epoch AI Benchmarking Hub / Epoch Capabilities Index
- URL: https://epoch.ai/benchmarks
- Method: csv — VALUE channel (gate-located): https://epoch.ai/data/eci_scores.csv (219 rows; columns Model,eci,eci_ci_low,eci_ci_high,date — verified: Sol 161.69, Fable 161.55, Opus 5 161.05, Kimi 157.39, DS V4 Pro 148.90; note the Sol>Fable order DIFFERS from AA, which is exactly row 2's purpose). Provenance channel: https://epoch.ai/data/eci_benchmarks.csv (2,207 data rows; model/benchmark/performance/date/source). CC-BY; python client + public repo available
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent nonprofit with disclosed lab entanglement (gate-corrected 2026-08-01): OpenAI funded FrontierMath — an ECI component (~150 rows in the live CSV; count drifts, 165 at first fetch) — with dataset access and a disclosure controversy (Jan 2025, TechCrunch et al.); the hub is supported by the UK AI Security Institute. Per-row provenance is MIXED: 670 rows "Epoch evaluations" (evaluator-run), ~270 rows sourced to vendor technical reports, 322 rows with an empty source column, plus rows mirroring GDPval (OpenAI-built), METR (already our S5 — double-count hazard for "two aggregators agree"), Vals, ARC. The per-row `source` column MUST drive per-cell handling; the composite carries a caveat flag.
- Caveat-flags: mixed-provenance composite (incl. OpenAI-funded FrontierMath)
- Attribution: data CC-BY — page must attribute Epoch AI and link the license.
- Freshness SLA: 336h (14d)
- Covers: ECI aggregate capability index; 5/5 target models verified in the CSV (2,207 data rows: Fable 16, Opus 5 17, Sol 19, Kimi 14, DS-V4-Pro 14). Scouted-in (ADR-002) as a cross-check of the AA index — with the caveat above, it is a partially-overlapping second read, not a fully independent one; Phase 2 decides whether the row computes over Epoch-run rows only.
- Grade: B (downgraded from A at the Phase 1 gate). Breakage: low.

### S11 — Vals AI professional-domain benchmarks
- URL: https://www.vals.ai/benchmarks
- Method: dom-scrape of SSR HTML (Astro islands; no API/CSV found) — needs fixture tests + loud parse failure
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent eval company (SF), not lab-owned. Gate-resolved 2026-08-01 (RISK-007): funding IS publicly discoverable — ~$5M from Bloomberg Beta, Pear VC, 8VC, J12, Sequoia scout (no frontier-lab investors); a pay-for-placement search found no evidence and Vals publicly claims neutral third-party posture with private datasets. Residual caveat: Bloomberg Beta money adjacent to Vals' Finance Agent benchmark.
- Caveat-flags: VC-funded evaluator, no on-site funding disclosure
- Freshness SLA: 504h (21d)
- Covers: Vals Index composite (weighted; cell value) + strict-vs-weighted gap badge from per-board tasks.overall vs tasks.all_pass. Coverage gate-corrected 2026-08-01: 5/5 (Vals Index v1.2, upd. 7/31: Fable 75.1 #1, Opus 74.8 #2, Kimi 74.7 #3, Sol 73.1 #4, DS V4 Pro 55.6 #19). Extraction: astro-island props JSON in SSR HTML (HTML-unescape → JSON; [0,x]=scalar, [1,[...]]=array), keys like anthropic/claude-fable-5. Strict-vs-weighted scoring gap = live reliability signal. Scouted-in (ADR-002), single composite row proposed.
- Grade: B. Breakage: high (DOM).

### S12 — LiveBench
- URL: https://livebench.ai
- Method: csv — `https://livebench.ai/table_{release}.csv` with release like `2026_06_25` (pattern taken from the site JS bundle; current file verified: `table_2026_06_25.csv`, 36 rows). Discover the current release string from the site bundle or by probing recent dates; fail loud if the pattern moves.
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent academic-led (NYU/Abacus/Nvidia-affiliated researchers), open methodology, ground-truth scoring (no LLM judge, no votes), monthly question rotation = contamination-resistant
- Freshness SLA: 1080h (45d; monthly rotation)
- Covers: contamination-resistant capability. Gate-verified 2026-08-01: the 2026-06-25 release covers **5/5** target models (claude-fable-5-max-effort, claude-opus-5-max-effort, gpt-5.6-sol-max, kimi-k3, deepseek-v4-pro); Fable coding avg 86.0 rank 1 reproduces. ADR-002's ≥3/5 condition is met ⇒ resolves to INCLUDE (Phase 2 decides the row).
- Grade: B. Breakage: medium.

### S13 — llm-stats SWE-bench Pro aggregate (vendor self-reports)
- URL: https://llm-stats.com/benchmarks/swe-bench-pro
- Method: embedded-json — full benchmark object in flight payload (43 rows: rank/score/self_reported/source/analysis_method/updated_at); robots allows pages, disallows /api/
- Retrieved-at: 2026-07-31T22:44:25Z (benchmark updated_at; fetched 2026-08-01)
- Independence: vendor-claimed — the aggregate is 100% self-reported (verified_count: 0 of 43), each row citing the vendor's own blog/PDF on the vendor's own scaffold. Cells citing S13 MUST be tagged V (linter-enforced). This is the true upstream of the seed's "Morph board" numbers.
- Caveat-flags: aggregated vendor self-reports (0 of 43 verified)
- Freshness SLA: 72h
- Covers: SWE-bench Pro vendor-claim aggregate. Verified values (2026-07-31 file): Fable 5 80.0 #1 (seed's "80.3" was Mythos 5's number — misattribution), Mythos Preview 77.8 #2, Opus 4.8 69.2 #3, Grok 4.5 64.7 #4, Sol 64.6 #5, DS-V4-Pro-Max 55.4 #29 (seed said "not published" — wrong), Opus 5 NOT on board (79.2 launch claim still un-ingested — seed status holds), no Kimi K3 row (confirmed).
- Grade: B (as a vendor-claim tracker; it is honest about self_reported). Breakage: medium.

### S14 — Anthropic model/pricing pages
- URL: https://www.anthropic.com/pricing, model cards/announcements (e.g. anthropic.com/news/claude-opus-5)
- Method: page fetch + manual verification at build; values tagged V
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: vendor
- Freshness SLA: 336h

### S15 — OpenAI model/pricing pages
- URL: https://openai.com/api/pricing, openai.com/index/gpt-5-6
- Method: page fetch + manual verification at build; values tagged V
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: vendor
- Freshness SLA: 336h

### S16 — Moonshot AI model/pricing pages
- URL: https://platform.moonshot.ai (Kimi K3 docs/pricing)
- Method: page fetch + manual verification at build; values tagged V
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: vendor
- Freshness SLA: 336h

### S17 — DeepSeek model/pricing pages
- URL: https://api-docs.deepseek.com (pricing), deepseek.com announcements
- Method: page fetch + manual verification at build; values tagged V
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: vendor
- Freshness SLA: 336h

### S18 — METR pre-deployment evaluation of GPT-5.6 Sol (blog post)
- URL: https://metr.org/blog/2026-06-26-gpt-5-6-sol/
- Method: page fetch (prose-only figure; NOT present in any METR data file — verified by gate)
- Retrieved-at: 2026-06-26T00:00:00Z (publication date; verifier re-fetched 2026-08-01)
- Independence: independent nonprofit evaluator, with disclosed constraints on this specific publication: conducted under a standard NDA; OpenAI's comms and legal team required review and approval of the post; METR itself says it "shouldn't be interpreted as robust formal oversight."
- Caveat-flags: blog-only figure — not on the METR leaderboard; NDA'd pre-deployment eval — vendor reviewed the publication
- Freshness SLA: 2160h (90d, matching S5)
- Covers: the Sol 50%-horizon figure only (11.3h [5–40h] standard methodology; >270h counting detected cheating as success; 71h [13–11,400h] discarding cheating runs; METR: "we do not consider any of these numbers to represent a robust measurement").

### S19 — Adoption-signal fallback (contingency, NOT collected)
- URL: https://huggingface.co/models (open-weights download/like telemetry); vendor usage disclosures as published
- Method: none yet — contingency ledger entry only (Phase 1 gate: the adoption lens must not have an undocumented single point of permanent failure)
- Retrieved-at: 2026-08-01T00:00:00Z (scouting date)
- Independence: independent platform telemetry (HF) / vendor-claimed (disclosures)
- Freshness SLA: n/a until activated
- Covers: if RISK-006 fires and S3 stands down, HF download stats can partially cover OPEN-WEIGHTS adoption (Kimi, DeepSeek); no independent public fallback exists for closed-model adoption — that residual is RISK-008.

### S20 — SWE-rebench (fresh-issue coding board)
- URL: https://swe-rebench.com
- Method: embedded-json (gate-pinned): the site's Next.js flight payload (self.__next_f.push) carries model objects with per-window {resolvedRate, sem, passN, instanceCosts} keyed by "<startMs>:<endMs>" (current 1778803200000:1782864000000) plus release.date for the contamination rule. The HF dataset nebius/SWE-rebench-leaderboard is the TASK SET, not scores (its card points the July 2026 split to Harbour Hub — channel-drift watch). Paper arXiv:2505.20411
- Retrieved-at: 2026-08-01T00:00:00Z (innovator verification fetch)
- Independence: independent — run by the Nebius team (GPU cloud, not a frontier lab). Decontamination is WINDOW-RELATIVE (gate-corrected 2026-08-01): issues post-date the window start, so only models released BEFORE the window start are contamination-clean; the board's own legend flags later releases as "Potential contamination" — current window (2026-05-15 → 2026-07-01) flags Fable 5 (rel. 06-09), Sol (rel. 06-26), and Opus 5 (rel. 07-24, after the window even closed); DS V4 Pro (rel. 04-24) is clean. Collector rule: derive the flag mechanically as release.date > window_start; every affected cell must carry it (rule 7).
- Freshness SLA: 1080h (45d; window cadence)
- Covers: fresh-issue resolved rate. Verified 2026-08-01 (twice — innovator + gate verifier): Fable 5 64.5±1.4 #1, Opus 5 63.4±1.4 #3 (Grok 4.5 63.8 #2), GPT-5.6 Sol 62.3±1.8 #5, DS V4 Pro 40.2±1.3 #14; Kimi K3 absent. Comparability: window-stamped set (`swe-rebench-window-<start>`) — scores comparable only within one issue window. NOT SWE-bench Pro and NOT SWE-bench Verified: display name must prevent conflation ("SWE-rebench (fresh issues)").
- Grade: B (estimate; confirm at collector build). Breakage: medium.

### S21 — Disclosure watch (curated editorial synthesis)
- URL: governance/ROWS.md (row definition); underlying primary sources named inside each open item's flag text (METR blog S18, ARC Prize S4, vendor pages S14–S17)
- Method: curated — each open item is added/retired by a governed edit (or by the Phase 7 judgment layer, which may only cite facts present in the day's snapshot); every item's flag text names its primary source
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent-of-vendors synthesis maintained by this pipeline; it is meta-observation of disclosure conduct, not a benchmark result
- Freshness SLA: 720h
- Covers: the disclosure-watch row only. Phase 1's S0 was a seed-only transcription vehicle and no longer sources this row.
