All verification complete. Here is the full report.

---

# VERIFIER REPORT — Combined Phase 4+5+7 Gate

Repo: `/home/user/model-eval-dashboard` @ f5f18c7 (branch `claude/frontier-model-eval-dashboard-urlfzc`). All checks reproduced locally; no source or data files edited. Baseline context: `make check` reports "invariant linter: all 12 constitutional rules green"; full `make test` = 111 passed.

## A. BRIEFS (Phase 4) — `/home/user/model-eval-dashboard/data/briefs.json`

Both requested briefs exist (`swe-rebench`, `epoch-eci`) — no substitution needed. Per-sentence SWE-family co-mention scan of all three briefs using the linter's own `_mentions_both_families` regexes: **zero single-sentence co-mentions of SWE-bench Pro / Verified / SWE-rebench** (scan script in scratchpad, "scan complete" with no hits).

### A.1 Metric brief "swe-rebench"

1. **VERIFIED** — "Resolved rate on freshly collected GitHub issues, tracked window-over-window against itself … third, fully separated coding scale." Matches SOURCES.md S20 ("fresh-issue resolved rate", "NOT SWE-bench Pro and NOT SWE-bench Verified") and governance/ROWS.md row 7.
2. **VERIFIED** — harness: "run by the Nebius team … methodology paper (arXiv:2505.20411); collection reads the site's embedded data payload (source S20)." All three facts verbatim in S20 (Method: embedded-json flight payload; "Paper arXiv:2505.20411"; "run by the Nebius team").
3. **VERIFIED** — "stale after 45 days": S20 Freshness SLA 1080h (45d); snapshot metric `freshness_sla_hours: 1080`.
4. **MISMATCH (stale claim contradicted by current cells)** — "Tracking on this page begins soon — until then the quick-look coding slot shows GDPval, visibly labeled as a stand-in." The current snapshot `data/2026-08-01.json` has the swe-rebench row **populated** (fable 64.5, opus 63.4, sol 62.3, ds 40.2; changelog entries "row activated at Phase 7 collector build"). `site/render.py:470` only applies the GDPval fallback `if mid not in cells` — so the built page now shows SWE-rebench, not GDPval. The fallback mechanism itself is real (render.py `QUICK_LOOK_FALLBACKS`, ORDERING.md "QL fallback labeling" rider), but the "begins soon / until then" statement is outdated by Phase 7 in the same release.
5. **VERIFIED** — independence: "Nebius is a GPU cloud company, not a frontier lab (source S20)." Verbatim substance of S20.
6. **VERIFIED** — integrity: "window current at the 2026-08-01 check (2026-05-15 to 2026-07-01) flagged Fable 5, Sol, and Opus 5 … DeepSeek V4 Pro was the only clean covered model." Reproduced three ways: (a) fixture window key `1778803200000:1782864000000` = 2026-05-15T00:00Z → 2026-07-01T00:00Z (computed); (b) collector run on `collectors/fixtures/swe_rebench.html.gz` emits contamination flags on exactly fable/opus/sol (release dates 06-09, 07-24, 06-26 > 05-15) and not on ds-v4-pro; (c) S20 ledger text.
7. **VERIFIED** — "flag derived mechanically (release date after window start)": matches `collectors/newrows.py` (`rel_dt > window_start`) and S20 collector rule.
8. **VERIFIED** — comparability: "window-stamped … rotation treated as methodology change … cross-window delta chips suppressed": snapshot set `swe-rebench-window-2026-05-15`; governance/ROWS.md lines 70–73 verbatim ("pre-classifies rotation-day changes as 'methodology change, not movement' and suppresses cross-set delta chips"); the cross-scale ban is rule 5 / S20.

### A.2 Metric brief "epoch-eci"

1. **VERIFIED** — "partially re-ingests boards this page already shows (GDPval, METR, Vals, ARC)": fixture `collectors/fixtures/epoch_eci.csv` contains GDPval (11 rows), METR Time Horizons (37), ARC-AGI/ARC-AGI-2 (64/63), and rows sourced to `vals.ai/benchmarks/proof_bench`; also S10 verbatim.
2. **VERIFIED** — "its top order disagreed with AA's (Sol above Fable 5)": fixture `epoch_eci_scores.csv` Sol 161.69 > Fable 161.55; AA fixture parses Fable 59.86 > Sol 58.89 (Opus 60.69 #1). Cross-aggregator dissent confirmed.
3. **VERIFIED** — harness: "score file (eci_scores.csv) with … provenance file (eci_benchmarks.csv), both CC-BY (source S10). Displays the index as published rather than recomputing": S10 entry; `EpochCollector.parse` only maps names and `round(v, 2)`.
4. **VERIFIED** — "hub updates multiple times per month … stale after 14 days": S10 "multiple updates/month", SLA 336h; snapshot metric 336.
5. **MISMATCH (stale claim contradicted by current cells)** — "Tracking on this page begins soon." All five `epoch-eci` cells in `data/2026-08-01.json` are populated (161.55 / 161.05 / 161.69 / 157.39 / 148.9) with changelog "row activated at Phase 7 collector build".
6. **VERIFIED** — independence sentence (OpenAI-funded FrontierMath, Jan-2025 disclosure controversy, UK AISI support): verbatim substance of S10. FrontierMath as ECI component also reproduced from fixture: 150 FrontierMath rows (S10 says "~150 … count drifts").
7. **VERIFIED (with caveat)** — "roughly 670 … Epoch-run, about 270 … vendor technical reports, 322 … empty source (counts drift)". Fixture recount of `epoch_eci.csv` (2,207 data rows, matching S10's 2,207): sources containing "Epoch" = **670 exact**; empty source = **322 exact**. The "~270 vendor technical reports" reproduces from SOURCES.md S10 verbatim, but a naive fixture count of sources titled "…Technical Report" yields 313 — the ~270 is classification-dependent; the brief's "about"/"counts drift" hedges cover it. Not counted as a mismatch. "Every cell will carry the mixed-provenance caveat flag" — all 5 snapshot cells carry it verbatim.
8. **VERIFIED** — double-count hazard (METR/S5) and comparability sentences: S10 verbatim substance.

### A.3 Model brief "kimi-k3"

1. **VERIFIED** — "No release date is recorded in this repository's sources — absent from the fresh-issue board": swe_rebench fixture contains zero "K3" occurrences; grep of governance + snapshot finds no Kimi K3 release date (the Epoch 2026-07-16 date is explicitly labeled "Epoch run date" on the cell).
2. **VERIFIED** — "display name changed from kimi-k3 to kimi-k3-max around Jul 26 (source S2)": S2 "kimi-k3 → kimi-k3-max (Jul 26)"; snapshot arena cell flag; Arena fixture parses variant "kimi-k3-max (rank 11)".
3. **VERIFIED** — "AA lists it as the #1 open-weights model at max effort (flag on its index cell)": snapshot `aa-index.kimi-k3` flag "#1 open-weights model (max)", source S1.
4. **VERIFIED** — context window "1,048,576 … above the flat 1,000,000 the other four declare": snapshot cells 1048576 vs 1000000×4; AA fixture parse reproduces 1048576.
5. **VERIFIED** — pricing (relayed via AA, probe pending, S1+S16): snapshot `api-price.kimi-k3` = "$3 / $15", tag V, source S1, flag "list price as relayed by AA data; vendor page probe at collector build"; S16 is Moonshot pricing.
6. **VERIFIED** — "price_moves: none recorded in the current tape window": no Kimi tape entries in snapshot.
7. **VERIFIED** — deployment terms "not published": snapshot cell empty, reason "not published".
8. **VERIFIED** — coverage_gaps, every clause: "widest gap set of the five" (empty-cell count: kimi 8 vs fable 2 / sol 3 / opus 4 / ds 4 — computed); TB 2.1 "not published" (cell); coding-claims aggregate "not published — no row" (cell + S13 "no Kimi K3 row (confirmed)" + llmstats fixture parses only fable/sol/ds); verified-set row "not published" (cell); ARC "not evaluated — scored on ARC-AGI-1/2 only" (cell flag + S4); METR "not evaluated" (cell); OpenRouter "not published — below top-9 since May, bucketed into 'others'; per-model spend via task-spend" (cell flags + S3); absent from fresh-issue board (fixture + cell). No SWE-family co-mention in any single sentence.

## B. IMPLICATIONS (Phase 5) — 8 implications in `data/2026-08-01.json`

Checked mechanically with a script using the repo's own `integrity_flags`, `_mentions_both_families`, and `tools/judgment.py` vocabulary logic, seed = `data/2026-07-31.seed.json`. The task's five substring markers match `INTEGRITY_MARKERS` in `tools/check_invariants.py` exactly.

1. **VERIFIED (all 8)** — criterion (2): confidence ∈ {high, med, low} on every implication (high×3, med×3, low×2) and every falsifier non-empty.
2. **VERIFIED (all 8)** — criterion (3): flags_carried complete and verbatim. `imp-sol-integrity` carries all 6 integrity flags of its 4 cited cells (3 from disclosure-watch, 1 modified-harness from arc, 1 record-gaming from metr, 1 withheld-disclosure from swe-bench-verified). `imp-open-arc` carries the 1 required (modified harness on arc sol). `imp-coding-claims` carries all 4 unique self-report flags of its cites. The other five implications cite cells with zero marker-bearing flags, matching their empty flags_carried.
3. **VERIFIED (all 8)** — criterion (4): no implication mixes SWE families in cites (imp-sol-integrity = verified only; imp-coding-claims = pro only; all others = none) or in text (linter regex scan: zero hits).
4. **MISMATCH (criterion 1, qualified)** — `imp-sol-integrity` cites `swe-bench-verified.gpt-5-6-sol`, which is an **empty** cell (`value: null`, `empty_reason: "withheld"`). The task requires every cite resolve to a populated cell. Context: the emptiness IS the cited fact (the text is about the withholding); the repo's own linter (RULE11) only requires cites resolve to known cell ids and passes this; the stricter `tools/judgment.py` validator would reject it ("cite missing or empty") but only governs machine-generated entries.
5. **MISMATCH (criterion 1, qualified)** — `imp-open-arc` cites three empty cells: `arc-agi-3.fable-5` (null, "not published"), `arc-agi-3.kimi-k3` (null, "not evaluated"), `arc-agi-3.ds-v4-pro` (null, "not evaluated"). Same qualification: the text explicitly discusses these as coverage gaps, and the linter passes it.
6. **MISMATCH (criterion 5, qualified)** — `imp-race-judged`: "0.83-pt gap" = 60.69 − 59.86 (exact cross-cell delta of cited values, but not a per-cell value/prev/delta); "+112 Elo margin" — actual 1857.8 − 1746.06 = **111.74**, stated as 112 (rounded, exists nowhere in any cell or seed). No fabricated facts; arithmetic correct to rounding.
7. **VERIFIED (borderline, noted)** — `imp-open-preference`: "13 Elo" = 1507.6 − 1494.6 = exactly 13.0, a cross-cell delta of two cited values. Passes if "their delta" includes deltas between cited cells; fails the strict per-cell reading. Not counted as a mismatch.
8. **MISMATCH (criterion 5, qualified)** — `imp-ds-value`: "13x" (885.4/66.4 = 13.33), "28-47x" (885.4/31.7 = 27.93; 885.4/19.0 = 46.60) are **ratios**, not values/deltas; "44-level" is a rounding of 44.27 (present only inside a cited cell's derived flag). "-10.02" and "0.940" are exact cited-cell values. No fabricated numbers; all derivable, but outside the stated grounding rule.
9. **VERIFIED** — `imp-pareto` and `imp-adoption-lanes`: every number in text is an exact cited-cell value or flag figure (script found zero out-of-vocabulary tokens).
10. **Observation (not counted)** — `tools/judgment.py` `NUM_RE` drops minus signs, so its no-new-facts check flags "10.02" in text against a cell valued −10.02 (false positive demonstrated on imp-ds-value). Latent validator bug for negative values; harmless today since Phase 5 implications are curated, not machine-validated.

## C. COLLECTORS (Phase 7)

1. **VERIFIED** — All 11 collectors' `parse()` ran against their recorded fixtures without error (script `run_collectors.py` in scratchpad): AA 50 cells, ARC 2, METR 1, Arena 5, OpenRouter 4, llm-stats 3, Tbench 1, Epoch 5, LiveBench 5, SWE-rebench 4, Vals 5. `python3 -m pytest tests/test_collectors.py -q` = **16 passed**.
2. **VERIFIED** — epoch-eci: parser output Sol **161.69** > Fable **161.55** (also Opus 161.05, Kimi 157.39, DS 148.9), identical to fixture CSV rows and to SOURCES.md S10.
3. **VERIFIED** — livebench: exactly **5 models**, fable **83.4** (opus 80.5, sol 81.6, kimi 79.5, ds 72.6), each flag "global average over 23 task columns, release 2026-06-25".
4. **VERIFIED** — swe-rebench: fable **64.5**, opus **63.4**, sol **62.3**, ds **40.2**; contamination flags on fable/opus/sol **only** (ds clean, per release 2026-04-24 < window start); kimi absent (fixture has zero "K3" strings); all cells `comparability_set = swe-rebench-window-2026-05-15`.
5. **VERIFIED** — vals: fable **75.1**, ds **55.6** (opus 74.8, kimi 74.7, sol 73.1), all with the VC-funded caveat flag.
6. **VERIFIED** — snapshot-vs-parser agreement for all four rows: field-by-field comparison (value, unit, tag, source_id, comparability_set, retrieved_at, **flags including order**) shows **exact match on all 19 populated cells**; `swe-rebench.kimi-k3` empty in snapshot ("not evaluated") consistent with parser emitting nothing.
7. **VERIFIED** — epoch retrieved_at convention: all five snapshot epoch cells carry `retrieved_at: 2026-08-01T09:00:00Z` (= collector `fetched_at` for NOW=2026-08-01T09:00Z) and score-dated flags matching the fixture CSV `date` column per model: fable **2026-06-09**, opus **2026-07-24**, sol **2026-07-09**, kimi **2026-07-16**, ds **2026-04-24**. CI flags also match the CSV's ci_low/ci_high verbatim.
8. **Observation (out of required scope, not counted)** — for rows built manually at Phase 1 (not the four Phase-7 rows), the collectors emit leaner flags than the snapshot cells carry; notably `collectors/metr.py` emits "measured on Claude Mythos Preview (early)…" without the "proxy-model measurement" integrity marker and with `value_disclaimed: False`, whereas the snapshot's `metr-horizon.fable-5` carries the marker and `value_disclaimed: true`. If a future collector-built snapshot replaces that cell, it would silently drop a rule-7 marker and the chip-exclusion disclaimer. Worth a builder fix before the collectors overwrite Phase-1 cells.

## D. JUDGMENT VALIDATOR (Phase 7)

1. **VERIFIED** — Independently computed `sha256(LOCKED_PROMPT)` = `806440216fc603cc9fa68e06903cfa6da66c8b5d23f468d3976479334faae5ab` = `PROMPT_SHA256` pinned at `tools/judgment.py:75`. Match.
2. **VERIFIED** — `python3 -m pytest tests/test_judgment.py -q` → **9 passed in 0.02s** (covers: pin match, grounded-entry acceptance, delta/name-digit allowance, invented-number rejection, empty-cite rejection, foreign source_id rejection, rule-5 family-mix rejection, rule-7 verbatim-flag enforcement, confidence/falsifier/tag hygiene).

## Summary

Every number I could reproduce, reproduced: all 11 collectors parse their fixtures to exactly the claimed values, the four Phase-7 snapshot rows agree with parser output byte-for-byte down to flag order and Epoch run-date flags, the judgment prompt pin is genuine, and both test suites plus `make check` pass. The kimi-k3 brief is fully grounded. The six mismatches split into two substantive and four qualified: (substantive) the swe-rebench and epoch-eci briefs still say "tracking on this page begins soon" while the shipped snapshot has both rows live — two stale sentences the renderer will display against populated data; (qualified) two implications cite honest-empty cells whose emptiness is the subject of the text (the repo's own linter permits this; the task criterion does not), and two implications contain derived figures (a rounded 112 vs 111.74, ratios 13x/28-47x, a rounded 44) that are correct arithmetic on cited values but fall outside the letter of the value/prev/delta grounding rule. Nothing is fabricated and nothing miscites a source. I would countersign: **YES, conditional** — fix or renderer-suppress the two "begins soon" sentences in `data/briefs.json` (the only claims a reader would see contradicted on the page), and log an ADR position on empty-cell cites and derived-number policy for implications so the criterion and the linter agree.

VERIFIER VERDICT: 6 mismatches
