# SOURCES — Provenance Ledger

Every `source_id` in any snapshot resolves to an entry here. Entries carry URL,
fetch method, retrieved-at, and a machine-read `Independence:` line — the
invariant linter enforces that no cell citing a `vendor`-classified source can
ever be tagged `I` (rule 10 hardening, Phase 0 gate).

Ledger status: **Phase 1 verified (2026-08-01)** — every live entry below was
directly probed by the Phase 1 research pass (9 agents, all six brief sources
plus scouted candidates; transcripts under session workflow `wf_3d319f0f`).
`Retrieved-at` on live entries = the Phase 1 verification fetch. Collector
convention (Phase 7): `retrieved_at` on cells = the source's own declared data
vintage where it declares one (ARC `generatedAt`, Arena `leaderboard_publish_date`,
METR page LAST-UPDATED), else the fetch time.

## Fetch-feasibility matrix

| id | Source | Best method | Endpoint | Auth | ToS posture | Cadence | SLA (h) | Grade | Breakage |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Artificial Analysis | json-api (+embedded-json fallback) | `/api/v2/language/models/free`; keyless: flight JSON in `/models` | free key (100 req/d) for API; none for embedded | robots open; attribution required on all tiers | same/next-day on releases; perf daily | 72 | A | low |
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
- Independence: independent benchmarking company (self-run evals on first-party endpoints; funding per secondary sources: AI Grant/Friedman/Gross/Ng, no lab money found; caveat: uses Gemini models as graders for GDPval-AA/Omniscience — methodological, not commercial, dependency; verify Terms-of-Use PDF posture at collector build)
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
- Freshness SLA: 96h
- Covers: Arena text Elo. Collector MUST pin (board=text, category=overall, style_control=on) — raw vs style-control boards reorder the top (SC #1 Fable 5 1508.6; raw #1 Opus 5 Max 1511.6). Ratings shift on daily whole-board refits: store rank+rating+publish_date together. Display-name churn hazard: kimi-k3 → kimi-k3-max (Jul 26); deepseek-v4-pro-high-preview (site) = deepseek-v4-pro-thinking (HF).
- Grade: A. Breakage: low.
- Verified values (SC board, cutoff 2026-08-01T03:00Z): Fable 5 1508.6 #1; Opus-5-high 1491.8 #6; Opus-5-max 1490.4 #7; Kimi K3 (max) 1485.3 #12; Sol (xhigh) 1482.8 #14 (added to text board Jul 31); DS V4 Pro 1457.9 #47. SEED REFUTED: Kimi 1547 #2 never existed in the dataset's full history.

### S3 — OpenRouter rankings
- URL: https://openrouter.ai/rankings
- Method: json-api (undocumented frontend API, no auth): `/api/frontend/v1/rankings/market-share` (52 weekly author-level buckets of raw token counts, top ~9 authors + others) and `/api/frontend/v1/rankings/task-spend` (rolling 30d spend, 29 task tags × top-10 models with share + deltaPp)
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent usage telemetry (marketplace routing data, not lab self-report). Structural bias: only OpenRouter-routed traffic — first-party/direct-API volume invisible, so premium providers (Anthropic) undercount on token share while leading spend
- Freshness SLA: 72h
- Covers: provider token share (unit caveat: endpoint returns unlabeled counts; magnitudes only plausible as tokens; page copy says "request share" — carry "unit per page copy ambiguous" flag); per-MODEL spend share via task-spend (new capability vs seed — Kimi K3 capturable here though invisible in provider share)
- ToS/robots: robots.txt permissive; ToS updated 2026-07-27 has an anti-scraping clause — direct tension. Collector posture: one polite fetch/day of the two JSON endpoints the page itself loads, honest UA — logged as RISK-006 with reversal trigger (any block, header, or objection ⇒ drop to "source down" handling and seek permission).
- Grade: B. Breakage: medium (undocumented endpoint names).
- Verified values (2026-08-01): token share, last complete week 2026-07-20 — DeepSeek 17.4% (#2 behind xiaomi 19.1%!), Anthropic 9.1% (down from ~13% seed — real decline), OpenAI 6.9%, Google 8.4%; partial wk 07-27: DeepSeek 20.9% #1, Anthropic 8.7%, OpenAI 8.6%. Moonshot below top-9 since May (bucketed into "others"). Anthropic ≈44% of code-category spend (confirms seed's "leads programming spend"); code = 25% of all OpenRouter spend.

### S4 — ARC Prize (ARC-AGI-3 Verified Leaderboard)
- URL: https://arcprize.org/leaderboard (values); collection: https://arcprize.org/media/data/leaderboard/v3.json
- Method: json-api — the leaderboard front-end's own pre-joined JSON (`version: v3`, `generatedAt` timestamp, per-row modelId/displayName/score/cost); on 404, re-derive path from `/scripts/leaderboard/data.js`
- Retrieved-at: 2026-07-31T22:31:25Z (file generatedAt; fetched 2026-08-01)
- Independence: independent nonprofit; ALL official scores run by ARC Prize Foundation on the Semi-Private set with academic oversight (NYU/SFI/Columbia); vendor self-reports categorically excluded; donor labs disclosed, no privileged access. Footnote: the published $10k per-run cost cap is evidently waived for headline runs (three rows pinned at exactly $10,000 vs $20.6k Opus 5 and $25.1k Sol Max records)
- Freshness SLA: 1080h (45d; policy publishes ≤30d after release/eval)
- Covers: ARC-AGI-3 with effort tiers (one row per model+tier; tier in modelId suffix and display suffix)
- Grade: A. Breakage: medium (undocumented internal asset path).
- Verified values (v3.json, 2026-07-31T22:31Z): Opus 5 (High) 30.16% #1 SOTA, $20,657/run (seed 30.2 confirmed, tier High); Sol (Max) 7.78% $25,064 — seed's 7.8 tier RESOLVED = Max; full Sol tier curve xHigh 6.99 / High 2.15 / Med 1.07 / Low 0.33. **Fable 5 ABSENT** from the verified board at any tier — seed's 16.6 is not reproducible from any official source (ARC Prize X post: "≈20% on Public Demo environments", approximate, non-comparable set). Kimi K3: on v1/v2 boards only, not v3 (seed "not evaluated" confirmed). DeepSeek: absent entirely (confirmed). Sol's 38.3 vendor claim (Responses API, retained reasoning + compaction, PUBLIC set) is NOT on the verified board — official file regenerated after the claim, unchanged; keep modified-harness flag.

### S5 — METR time horizons
- URL: https://metr.org/time-horizons/
- Method: csv/yaml — `metr.org/assets/benchmark_results_1_1.yaml` (per-model p50/p80 + CIs, SOTA flags, doubling time; version-suffixed filename — collectors should follow the page's `#raw-data-link` href); equivalent embedded JSON (`benchmarkDataV1_1`) in the page; analysis code + raw runs at github.com/METR/eval-analysis-public
- Retrieved-at: 2026-08-01T00:00:00Z (data vintage: page LAST UPDATED 2026-05-08)
- Independence: independent nonprofit, self-run evals; caveats carried as flags: Sol pre-deployment eval was NDA'd with OpenAI comms/legal review of the post; Anthropic early access implies lab cooperation
- Freshness SLA: 2160h (90d — METR's own cadence is event-driven/irregular; page warns coverage is incomplete)
- Covers: 50% (and 80%) task-completion time horizon, suite METR-Horizon-v1.1
- Grade: B (methodology/transparency best-in-class; cadence irregular, Sol datum prose-only). Breakage: low.
- Verified values: **Fable 5 → measured as "Claude Mythos Preview (early)"**: p50 17.4h, 95% CI 8.5–55.1h, is_sota, with METR's notice "Measurements above 16 hrs are unreliable with our current task suite" (seed's "≥16h" corrected to point estimate + CI + unreliability flag). **Sol: 11.3h [5–40h] exists ONLY in the 2026-06-26 blog post** (not in any leaderboard/data file); METR's own term is "cheating" ("detected cheating rate was higher than any public model we have evaluated"; alternates: >270h counting cheats as successes, 71h discarding them; "we do not consider any of these numbers to represent a robust measurement"). Opus 5 / Kimi K3 / DS V4 Pro: not evaluated (confirmed; closest: Opus 4.6 11.98h, Kimi K2 Thinking 0.96h on v1.0, DeepSeek V3-era only).

### S6 — "Morph-tracked SWE-bench Pro board" (DEMOTED at Phase 1 gate — do not collect)
- URL: https://www.morphllm.com/swe-bench-pro
- Method: none viable (every request incl. robots.txt returns HTTP 429 Vercel Security Checkpoint; latest Wayback capture 2026-07-01, content "verified June 28")
- Retrieved-at: 2026-08-01T00:00:00Z (verification attempt)
- Independence: presumed-independent in the seed — REFUTED 2026-08-01. Morph is a code-tooling vendor; the page is editorial/SEO aggregation republishing (a) Scale's SEAL standardized board and (b) llm-stats.com's vendor-self-report aggregate. The seed's S6 numbers trace to llm-stats (verified_count: 0, self_reported_count: 43) — vendor-grade data that the seed mistakenly carried as independent.
- Status: replaced by S13 (llm-stats aggregate, vendor-classified) + S9 (Scale SEAL standardized, independent). S6 remains in the ledger only so seed cells resolve; no new snapshot may cite S6 (ADR-002).

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
- Independence: independent maintainers (Stanford/Laude Institute lineage, harbor-framework org) who verify vendor-submitted runs and apply an LLM reward-hack judge with visible deductions; maintainers also run a neutral reference agent (Terminus 2)
- Freshness SLA: 1080h (45d; event-driven submission cadence)
- Covers: Terminal-Bench 2.1 accuracy. COMPARABILITY HAZARD: every score is an agent+model+effort tuple (Fable 5 spans 83.8 Claude-Code-xhigh to 80.4 Terminus-2-high). Dashboard policy (Phase 2): best-per-model with agent+effort recorded in the cell flags.
- Grade: B. Breakage: medium.
- Verified values: Fable 5 83.8%±1.2 rank 1 (Claude Code v2.1.167, xhigh; hack adj −0.2%). Sol 76.2%±1.3 exists ONLY as a merged repo JSON (PR #102), absent from the 17 displayed rows — treat displayed board as canonical, repo value provisional. Opus 5 / Kimi K3 / DS V4 Pro: not listed (closest: Opus 4.8 78.9% #5; TB 2.0-only Kimi K2.5 43.2, DeepSeek V3.2 39.6 — different comparability set).

### S9 — Scale SEAL SWE-bench Pro (standardized, public set)
- URL: https://labs.scale.com/leaderboard/swe_bench_pro_public
- Method: embedded-json — 25-row entries[] in the page's flight payload (model/rank/score/CI/createdAt); harness open-sourced (github.com/scaleapi/SWE-bench_Pro-os)
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent-run standardized evals (Scale runs the harness itself) — BUT organizational caveat: Meta holds ~49% of Scale (Jun 2025), so treat Meta-model rows with a conflict flag; for non-Meta comparisons the standardized harness is the only independent SWE-bench Pro view that exists
- Freshness SLA: 2160h (90d; batch additions every 1–3 months)
- Covers: SWE-bench Pro standardized Pass@1, public 731-task set. Coverage gap: NONE of the five dashboard models are on it (leader: Muse Spark 1.1* 61.5; the standardized leader sits ~20pts below vendor-harness claims — the cross-harness gap is itself a dashboard-worthy integrity signal).
- Grade: B. Breakage: medium.

### S10 — Epoch AI Benchmarking Hub / Epoch Capabilities Index
- URL: https://epoch.ai/benchmarks
- Method: csv — https://epoch.ai/data/eci_benchmarks.csv (verified: 2,208 rows; columns model/benchmark/performance/date/source), CC-BY; python client + public repo available
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent nonprofit; hub supported by UK AI Security Institute; no lab funding found. Per-row `source` column drives provenance where rows mirror external boards.
- Freshness SLA: 336h (14d)
- Covers: ECI aggregate capability index; 5/5 target models verified present in the CSV. Scouted-in (ADR-002): cross-checks the AA index so the frontier-race read never rests on a single aggregator.
- Grade: A. Breakage: low.

### S11 — Vals AI professional-domain benchmarks
- URL: https://www.vals.ai/benchmarks
- Method: dom-scrape of SSR HTML (Astro islands; no API/CSV found) — needs fixture tests + loud parse failure
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent eval company (SF), not lab-owned; open question logged for gate: no public funding/pay-for-placement disclosure found — verify before I-tag ships
- Freshness SLA: 504h (21d)
- Covers: Vals Index composite + professional agentic boards (Finance Agent v2, Legal Research). 4/5 models covered (no DeepSeek V4 Pro). Strict-vs-weighted scoring gap = live reliability signal. Scouted-in (ADR-002), single composite row proposed.
- Grade: B. Breakage: high (DOM).

### S12 — LiveBench
- URL: https://livebench.ai
- Method: github-data / HF datasets (site itself is JS-only shell); monthly releases as data files
- Retrieved-at: 2026-08-01T00:00:00Z
- Independence: independent academic-led (NYU/Abacus/Nvidia-affiliated researchers), open methodology, ground-truth scoring (no LLM judge, no votes), monthly question rotation = contamination-resistant
- Freshness SLA: 1080h (45d; monthly rotation)
- Covers: contamination-resistant capability. Coverage caveat: only Fable 5 (#1 coding, 86.0, Jul coverage) verified among the five; current release 2026-06-25. Scouted-in conditionally (ADR-002): promote to a row only if collector-time verification finds ≥3/5 target models; else HOLD.
- Grade: B. Breakage: medium.

### S13 — llm-stats SWE-bench Pro aggregate (vendor self-reports)
- URL: https://llm-stats.com/benchmarks/swe-bench-pro
- Method: embedded-json — full benchmark object in flight payload (43 rows: rank/score/self_reported/source/analysis_method/updated_at); robots allows pages, disallows /api/
- Retrieved-at: 2026-07-31T22:44:25Z (benchmark updated_at; fetched 2026-08-01)
- Independence: vendor-claimed — the aggregate is 100% self-reported (verified_count: 0 of 43), each row citing the vendor's own blog/PDF on the vendor's own scaffold. Cells citing S13 MUST be tagged V (linter-enforced). This is the true upstream of the seed's "Morph board" numbers.
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
