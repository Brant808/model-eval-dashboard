# EVAL — Finished-Dashboard Scorecard (2026-08-01)

Builder scores with evidence; verifier countersign appended below (Phase 9
gate). Scale 1–5. Any dimension under 4 carries a remediation note or an
accepted-risk reference.

## 1. Trustworthiness — 5

Every populated cell carries I/V + numbered source resolving to a ledger
entry with URL/method/timestamp; vendor claims quarantined in C7 with
machine-enforced VENDOR-CLAIMED bands; integrity flags render on cells AND
propagate verbatim into implications (rule 7, linter + tests); vendor values
can never chip (rule 10 + ledger independence cross-check); the quick-look
band now carries the same trust metadata, verified cell-for-cell against
the snapshot. The layer most prone to quiet lying — carried editorial —
flips mechanically to "UNDER REVIEW" when cited cells move. Evidence:
`make check` (12 rules over every snapshot + the shipped HTML), 119 tests,
three adversarial gate reports with all BLOCKING/MAJOR findings resolved.

## 2. Scannability — 4

Cold read (red-team, rendered, timed): what-moved ~15s via the dated tape;
trust semantics read without documentation; X-panel lens labels carry the
scan. Ordering C1→C7 with the fold after C4 verified rendered. Held at 4,
not 5: the X-panel is ~3.4 iPhone screens (accepted at gate; three of the
eight entries are OPEN, which densifies signal) and implication cites are inert text
(RISK-011 rider). Remediation trigger: Phase 9+ cold reads.

## 3. Freshness — 4

Daily cron + retry cron, 72h-windowed tape with carry-forward, per-metric
SLA staleness with visible badges, health footer naming each
collector-backed source's state (8 of the 15 cited source ids today —
curated/no-collector sources have no state line; self-heals on the first
collectors.run, which builds health from all 11 collectors), same-day
re-run safe. Held at 4: rule 9 cannot see a frozen source
that keeps serving 200s (RISK-012, trigger recorded), and the page is only
as fresh as one run/day by design.

## 4. Comparability discipline — 5

Comparability sets on every cell and enforced against metric declarations;
chips computed only within sets, shape+label, CO-LEAD ties, disclaimed and
flagged-leader exclusions; the three SWE scales are machine-separated in
rows, tape, implications (cites AND text), briefs (per-sentence), and the
rendered page prose; ARC values carry effort tiers everywhere including
editorial mentions; cross-set superlatives banned from X copy at gate;
set renames blank carried values honestly rather than re-labeling.

## 5. Implication quality — 4

All 8 X-entries: cited, confidence-labeled, falsifiable, flag-carrying,
rot-guarded via cite_values pins. The gate rewrote the three weakest (IMP-1
evaluator scoping + cited dissent; IMP-2 reframed; IMP-5 to OPEN with the
opposite reading named). Held at 4: curated prose can still age between
gates in ways value-pins don't catch (a cited cell UNCHANGED while the
world moves — e.g. a new board appearing); the mechanical layer catches
value drift only. Accepted: mechanical mode is the shipped default.

## 6. Resilience — 4

Per-source degradation with last-good + loud flags; single-source,
total-loss, clock-advance, same-day-rerun, and implication-rot drills all
green in CI against recorded fixtures through the REAL fetch path; carry
hygiene migrates old cells across constitution changes; data commits before
build/tests; failed runs upload forensics; retries env-capped in CI; page
serves last-good on any failure. Held at 4: RISK-013 (healthy-source cell
vanishing blanks same-day, no debounce) and the judgment validator's
lexical bounds (RISK-011) are accepted-with-trigger, not solved.

## 7. Access latency — 4 (provisional: human toggle pending)

Page is 31.7 KB gzipped (153,848 B raw), self-contained, opens offline from file://, 2-up
at iPhone width with no horizontal scroll, keyboard-complete, selection
persists across reloads. Held at 4 pending the two human actions this
sandbox cannot perform: the Pages toggle and the live-URL verification from
both devices (HANDOFF steps; RISK-004 blocks the push that precedes them).
Becomes 5 when https://brant808.github.io/model-eval-dashboard/ loads cold
on cellular.

## Verifier countersign (2026-08-01, verbatim)

All verification complete. Here is my Phase 9 deliverable.

## Cold read

Method: rendered `/home/user/model-eval-dashboard/docs/model-eval-monitor.html` in headless Chromium (`/opt/pw-browsers/chromium`) via `file://` with no network, at 1280px, 390px (iPhone), and with JavaScript disabled. Answers below come from the page alone.

**(a) What moved in the last ~72h** (from the dated tape, ~15s): SWE-bench Pro was re-sourced to the llm-stats vendor aggregate and re-tagged V across the board (Fable corrected 80.3→80.0, DS V4 Pro appears at 55.4); Fable's ARC-AGI-3 16.6 was withdrawn — it has no official score at any tier (Sol official 7.78 Max, Opus record 30.16); AA refresh moved GDPval-AA (Opus 1857.8, Sol 1732.5, DS debuts 1304.49) and cost-per-task on all five models with the driver unresolved; METR corrected Fable-base to 17.4h; DeepSeek V4 Flash 0731 debuted at AA 50; Arena text settled (Fable #1 1507.6, Sol added at 1484.9, Kimi's seed 1547 reclassified as category-board conflation); DeepSeek was displaced from OpenRouter #1 by xiaomi (19.1% vs 17.4%); OpenAI cut Luna to $0.20/$1.20.

**(b) Trust vs discount** (~15s): I trust the I-tagged cells with [S#] ids — AA Index, Arena Elo, Epoch, LiveBench, Vals, SWE-rebench, ARC verified board. I discount: everything in the VENDOR-CLAIMED band (SWE-bench Pro claims — "0 of 43 verified", ⚠ tags; Opus 79.2 is a launch claim on no board); every Sol headline (3 open disclosure items: withheld SWE-bench Verified, modified-harness ARC claim, METR cheating flag — the ⚠s propagate into the implications citing them); Sol's METR 11.3h ("blog-only", "not a robust measurement"); and the cost-per-task / intelligence-per-dollar family ("driver unresolved" flags on all five). Signals used: I/V tags, numbered source ids, ⚠ warning tags, the VENDOR-CLAIMED quarantine band below the fold, effort-tier labels on ARC, judge-provenance notes ("Gemini-graded"), and the absence of any STALE badge.

**(c) Two takeaways** (~25s): (1) Opus 5's lead is evaluator-scoped — it leads both AA boards (60.69, 1857.8) but Epoch, LiveBench, Vals, and Arena all put Fable or Sol ahead; the page itself labels this confidence **med** with the split held as an OPEN question (confidence low). (2) Sol is the integrity story — three open disclosure items mean no Sol headline is comparable without a footnote; confidence **high**, with per-item closers stated. (Bonus read: DeepSeek is cheap capability, not cheap reliability — 885.4 pts/$ against a −10.02 Omniscience and 0.940 hallucination rate, confidence med.)

**Confirmations:**
- Group order renders **Overall intelligence → Agentic & real-economy work → Coding → Economics & adoption → [fold: "below: slow boards and claims — the tape flags any change"] → Knowledge & reliability → Headroom → Integrity & disclosure** = C1→C7 with the fold after Economics. CONFIRMED.
- Quick-look band shows boxed **I** tags on all 15 values, a **⚠** under Sol's "3 open items", and an honest "— not evaluated" blank. No STALE badges appear because zero cells are stale (`data-stale="1"` count = 0 in the HTML; no `stale: true` in `data/latest.json`); the badge machinery is proven by `test_stale_cell_renders_badge` and the clock-advance drill. CONFIRMED.
- No-JS/static state: all **5** model columns of every row are in the static DOM and visible with JS disabled (verified cell-by-cell on the aa-index row: Fable 59.86, Opus 60.69, Sol 58.89, Kimi 57.11, DS 44.27 all `display: table-cell`). CONFIRMED, two caveats: the static thead carries only the 3 default picker labels, so the 4th/5th data columns are unlabeled without JS, and the quick-look band renders empty labels without JS (values are JS-hydrated from the embedded `<script id="state">` blob).

**Verdict: PASS — ~55 seconds** (tape ~15s, trust triage ~15s, takeaways ~25s). The X-panel is long (measured 2,882px at 390px width = 3.4 iPhone screens) but lens tags and confidence labels make it skimmable within budget.

## Countersign

Notes: `make check` → "all 12 constitutional rules green" over every snapshot + shipped HTML (`tools/check_invariants.py` main() lints all dated snapshots, latest, HTML, explainability, hygiene, briefs). `make test` → **119 passed**. No web re-fetch was possible or required: every claim in EVAL.md is repo/page-scoped and was rerun locally.

1. **Trustworthiness — COUNTERSIGN — 5.** Reproduced: 12/12 rules green, 119/119 tests; ql-state cross-check exists in the linter (`check_invariants.py:780-813` — tag/stale/warn/empty verified against snapshot cells); RULE10 + ledger cross-check at line 347; forged-chip/hidden-warning renderer forgeries caught (`tests/test_render.py`); rot flip drill passes; derived cells recompute correctly (60.69/2.34=25.9 etc., machine-checked at line 422).
2. **Scannability — COUNTERSIGN — 4.** My own timed cold read PASSED at ~55s with what-moved in ~15s; C1→C7 + fold verified rendered; X-panel measured 3.4 iPhone screens (EVAL says ~3, and says "two entries went OPEN" — the shipped page has **3** OPEN of 8; a nit, not a score change).
3. **Freshness — COUNTERSIGN — 4, with one evidence correction.** Two crons verified (`.github/workflows/daily.yml`: 12:30 + 13:15 UTC retry), per-metric `freshness_sla_hours` on all 20 metrics, tape all within 72h of 2026-08-01T09:00Z, clock-advance drill passes; but "health footer naming every source's state" is overstated — the shipped footer names 8 sources while cells cite 15 ids (S10/S11/S12/S20 have registered collectors yet no footer state; self-heals on the next `collectors.run`, which builds health from all 11 collectors).
4. **Comparability discipline — COUNTERSIGN — 5.** RULE4/RULE5 enforcement verified at every claimed surface (rows :476, tape :517-519, implication cites+text :538-540, briefs :609, rendered page prose :830); chips shape+label :755, vendor-never-chips :744, CO-LEAD :254, ARC tier RULE6 :381; ARC editorial mentions on the page do carry tiers ("30.16 (High tier)", "7.78 (Max tier)") — though tier-in-prose is editorial discipline, not a machine rule.
5. **Implication quality — COUNTERSIGN — 4.** 8/8 entries in `data/latest.json` carry cites, confidence, falsifier, `cite_values` pins; `flags_carried` (6/7/1) matches the rendered ⚠×6/⚠×7/⚠ badges exactly; `test_drill_implication_rot_flips_to_under_review` PASSED; the acknowledged residual (pins catch value drift only) is accurately stated.
6. **Resilience — COUNTERSIGN — 4.** All 7 drills in `tests/test_pipeline.py` pass and genuinely invoke `collectors.run` with `COLLECTOR_FIXTURES_DIR` (real fetch/merge path, not mocks); `daily.yml` confirms data-commit before build/tests, forensics `upload-artifact` on failure, `COLLECTOR_RETRIES: "1"`; RISK-011/012/013 all present in `governance/RISKS.md` with triggers.
7. **Access latency — COUNTERSIGN — 4, with one figure correction.** Current build is **31,760 B gzipped (31.7 KB; 31,651 B at gzip -9), 153,848 B raw** — the "30.7 KB" figure is stale from the innovator's earlier measurement (154,199 B raw / 30,721 B gz); immaterial against the 1.5 MB budget. Self-contained verified (no external src/link/@import/font; only 2 inline scripts); opened offline from `file://` with zero JS errors; 390px width shows 2-up with scrollWidth = clientWidth = 390 (no horizontal scroll); all 15 UI-gate tests pass including keyboard nav and hash/localStorage persistence. Provisional-4 pending the two human steps is the right call.

Summary: the page and pipeline are trustworthy as shipped — every mechanical claim in EVAL.md reproduced, all gates green, and my independent cold read passes the 60-second Definition of Done. Two evidence sentences need correcting in EVAL.md before archive (health footer covers 8 of 15 cited sources; page is 31.7 KB gzipped, not 30.7), and the no-JS state, while rendering all five data columns, leaves two of them header-unlabeled and the quick-look band empty — worth a line in HANDOFF, none score-changing. I would countersign the deliverable as-is: **YES**, on condition the two stale evidence figures in `governance/EVAL.md` are corrected at the Phase 9 ADR.

VERIFIER: countersigned 7/7, disputed 0/7
