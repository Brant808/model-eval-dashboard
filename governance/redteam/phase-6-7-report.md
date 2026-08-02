# Red-team report — Phase 6 (UI cold read) + Phase 7 (autorefresh)

`make all`: green, 111 tests, and the rebuilt page is byte-identical to the committed tree (clean `git status` after a full run). Rendered and exercised the page in headless Chromium at 1440px and 390px: offline open, 2-up mobile, keyboard picker swap (`1`, type, Enter), hash persistence (`#m=...`) all work. The linter has real depth — it caught my own half-crafted staleness injection via the derived-cell rule before I fixed my attack. Those parts are solid. The following are not.

---

## PART 1 — Cold read (docs/model-eval-monitor.html, JS state)

**[BLOCKING] Quick-look band strips every trust signal and will present stale values as fresh, gate-green**
- Artifact: `/home/user/model-eval-dashboard/site/render.py` lines 465–501, 789–800 (`state.ql` = `fmt_value` only).
- Failure scenario: the first numbers the reader sees each morning (the headline band, above everything) carry no I/V tag, no source id, no warning marker, and empty cells render as a naked `—` with no reason. The day any quick-look source exceeds its SLA (AA stalls >72h), the table cell gets a STALE badge but the band shows the same number unbadged at the top of the page — rule 9's "stale never presented as fresh" violated exactly where the 60-second read starts. The linter cannot see it: `ql-num` divs are filled by JS from a state JSON that contains only formatted value strings.
- Evidence: demonstrated — crafted a stale `aa-index.opus-5` + `intelligence-per-dollar.opus-5` in a scratch snapshot, re-rendered; table cell shows `data-stale="1"` + STALE badge; `state.ql` shows bare `"60.69 index"`; `check_invariants.py` exits 0 ("all 12 constitutional rules green"). Screenshot `desktop-top.png`: band shows no tags today either.
- Suggested resolution: put tag/stale/warn/empty-reason into the ql state and render mini-badges; add an HTML-side linter check that ql state values for stale/V cells carry markers.

**[MAJOR] Shipped page implements neither ADR-005 ordering C nor the trust order; the legend lies about a fold that doesn't exist**
- Artifact: `/home/user/model-eval-dashboard/data/2026-08-01.json` (seed-era groups) vs `collectors/registry.py` (c1–c7); `site/render.py` FOLD_AFTER={"c4-econ"}, legend text line 436–442.
- Failure scenario: the page renders 9 groups: five seed-era groups, then four stranded one-row c-groups ("Overall intelligence" — Epoch ECI — is SIXTH, below Lab-claimed and Economics). The VENDOR-CLAIMED SWE-bench Pro row sits in group 2 near the top; there is no fold marker anywhere (`grep -c "data-fold"` = 0) while the legend promises claims are "quarantined below the fold." ADR-005's reversal condition ("if the Phase 6 rendered cold read fails, switch to D") cannot even be evaluated: what ships is not ordering C. Bonus rot: the first live `collect()` run silently re-groups the entire page from the registry and drops 3 rows to the brief layer with no on-page explanation.
- Evidence: screenshots at scroll 0/900/1800/2700/3600; group extraction from latest.json; `governance/DECISIONS.md` ADR-005; `governance/ORDERING.md`.
- Suggested resolution: migrate the snapshot's metric groups to c1–c7 now (or render group order from the registry), restore the fold, and re-run the cold read on the actual ratified layout before invoking/waiving the ADR-005 reversal.

**[MAJOR] Ratified picker catalog (ORDERING.md D5) unimplemented; page text contradicts the decision record**
- Artifact: `/home/user/model-eval-dashboard/collectors/model_map.py` (5 models, all "current"); page New-model watch text.
- Failure scenario: ADR-005/D5 ratifies ~12 models (opus-4-8, sonnet-5, gpt-5-5, kimi-k2-6, terra, luna, and Muse Spark 1.1 as "Enters the catalog"). The picker offers only the 5 current models; "Recent & superseded" group is empty; the Apple mechanic "picker draws from the full catalog" is unmet, and the page's watch item says "Phase 3 decides catalog entry" — Phase 3 already decided yes. A reader cross-checking the governance record finds the page contradicting it.
- Evidence: `python3 -c "from collectors.model_map import MODELS..."` → 5 models; `governance/ORDERING.md` lines 99–126; screenshot desktop-3600 (watch section).
- Suggested resolution: either build the ratified catalog columns (cells or reasoned empties per D6) or write the deferral into an ADR/RISK with a trigger, and fix the watch copy.

**Cold-read answers (timed, ~55s to answer a–c):**
- (a) What moved in ~72h: **Yes** — tape is first, dated, sourced. Today's entries are long correction essays but scannable via bold dates.
- (b) Trust per number: **Yes in the table** — I/V boxes, `[S#]`, ⚠ blocks, tinted VENDOR-CLAIMED bands and the withheld/warn empties read instantly without documentation; the legend is compact and sufficient. **No in the quick-look band** (objection above).
- (c) What it means: **Yes** — X-panel is visually distinct, lens-labeled, every entry shows confidence, "reverses if", and cites. It is over-long (8 entries, ~700 words; ~3 screens on iPhone) but the bold lens labels rescue the scan.
- (d) Relevance-first ordering: **cannot be judged as ratified** — the page renders a hybrid that is neither ordering C nor trust order (objection above). The five seed-era groups that lead the page happen to read fine; the four orphan groups at the bottom confuse.
- (e) Actively misleading at first glance: the quick-look band's naked numbers/blank dashes; the legend's false "below the fold" claim; nothing else — chips are labeled ▲LEAD, dots carry "moved" text, field-#1 footnotes are honest.

---

## PART 2 — Pipeline attack

**[BLOCKING] Implications never regenerate or invalidate: the page ships refuted "confidence high" claims after cells move, gate-green**
- Artifact: `/home/user/model-eval-dashboard/collectors/run.py` line 278 (`"implications": prev.get("implications", [])`); no rule-11 consistency check in `tools/check_invariants.py`.
- Failure scenario: mechanical mode (the shipped default) carries implications forward verbatim forever. AA refits values within days; the X-panel then asserts numbers and orderings the table above contradicts. Demonstrated the worst case: stubbed an AA refit where the order flips (Fable 60.1 > Opus 59.5) — the implication's own stated falsifier fired — and the page still says "Opus 5 leads the frontier… AA Index 60.69 vs Fable 59.86 … confidence high"; full linter: 0 violations. The brief conditions carry-forward on "cited cell unchanged"; nothing implements that condition.
- Evidence: scratch run `dblrun`/`dbl` (StubAA collector, `collect("2026-08-02")`), grep of `imp-race-judged`, `check_invariants.py` exit 0 with REQUIRE_HTML=1.
- Suggested resolution: in `collect()`, mark any implication whose cited cell values changed since `first_stated` as OPEN/"cited data changed" (or drop it), and add a linter rule reusing the judgment vocab check: numbers in implication text must exist in cited cells' current values.

**[BLOCKING] Judgment validator leaves two rendered channels unvalidated: fabricated numbers in `falsifier`, fabricated integrity flags in `flags_carried`**
- Artifact: `/home/user/model-eval-dashboard/tools/judgment.py` `validate_entry` (checks numbers only in `text`; checks `flags_carried` is a superset, never a subset).
- Failure scenario: with judgment enabled, a hallucinating or prompt-injected model (cell `flags` strings are scraped from live sources and fed into its input) ships fabricated content through validated-looking channels: "reverses if Opus 5 drops below 87.3 or Anthropic loses its 45% enterprise share" renders in the X-panel; a fabricated `flags_carried` entry "record gaming (METR: cheating): Opus 5 flagged for benchmark manipulation" renders as an official ⚠ warning tag. Both injected into a scratch snapshot: full constitutional gate green, content confirmed present in the rendered HTML.
- Evidence: `attack_judgment.py` cases D/E → ACCEPTED; end-to-end `gate/` experiment: linter exit 0, greps show the fabrications on the page.
- Suggested resolution: run the no-new-facts number scan over `falsifier` (and tape/implication `text` already covered), and require `flags_carried` ⊆ union of cited cells' flags.

**[MAJOR] No-new-facts validation is lexical only: word-numbers, inverted orderings, misattribution, sign-flips, and sub-Unicode digits all pass**
- Artifact: `tools/judgment.py` `NUM_RE`/`cell_number_vocabulary`.
- Failure scenario: all demonstrated ACCEPTED against the real snapshot: "gains sixty-one points"; "Kimi K3 overtakes Opus 5" (cells say opposite); Opus's 60.69 attributed to Sol (cross-cell vocab is pooled); "cost falls 0.4" when it rose 0.4 (delta is `abs()`); "shipped 2026 successful deployments" (date digits always allowed); "leads by ⅔" (vulgar fractions aren't `\d`). BUILDLOG's claim "nothing un-grounded can get through" is overstated.
- Evidence: `attack_judgment.py` cases A/B/C/F/G/H — 8/8 bypasses.
- Suggested resolution: log as an accepted risk with reversal trigger (validator is a number-grounding backstop, not a truth oracle) and tighten what's cheap: per-cell (not pooled) vocab binding, signed deltas, and strip date-digit allowance from entry text.

**[MAJOR] Any second run in the same calendar day fails the constitutional gate — including the Phase 9 observed manual dispatch**
- Artifact: `/home/user/model-eval-dashboard/collectors/run.py` `collect()` — `prev_path = newest_dated_snapshot()` includes today's own snapshot; output overwrites `data/<today>.json`.
- Failure scenario: cron runs 12:30 UTC and commits; human dispatches at 20:00 to observe a run (the workflow_dispatch exists precisely for this). `collect()` diffs today against today, produces an empty tape/changelog, wiping the explanation of yesterday→today changes; `make check` fails on EXPLAIN; run red. Loud, not corrupting (nothing commits), but guarantees spurious red runs and a failed Phase 9 exit criterion whenever anything moved that morning.
- Evidence: demonstrated — two `collect("2026-08-02")` calls; run 2 tape=0/changelog=0; linter: **38 EXPLAIN violations**, exit 1.
- Suggested resolution: diff against the newest snapshot dated **before** `date_str`, and merge (don't discard) an existing same-day tape.

**[MAJOR] The judgment upgrade path can never activate: workflow installs no `claude` CLI**
- Artifact: `.github/workflows/daily.yml` (pip install only); `requirements.txt`; `tools/judgment.py` line 213 (`shutil.which("claude")`).
- Failure scenario: HANDOFF tells the human "add the ANTHROPIC_API_KEY secret… the workflow detects it." On ubuntu-latest there is no `claude` binary, so every run degrades to "off (mechanical — claude CLI not installed)". The one promised human action silently buys nothing (health footer states the reason, but only if the human knows to look).
- Evidence: grep of workflow/requirements — no npm/CLI install step; `governance/HANDOFF.md` lines 45–50.
- Suggested resolution: add `npm install -g @anthropic-ai/claude-code` (or switch judgment.py to the HTTP API) inside the key-guarded step, or correct HANDOFF.

**[MAJOR] After the first mechanical run, the tape header "last ~72h" is false — it shows last-24h only, and movement dots inherit the gap**
- Artifact: `collectors/run.py` `mechanical_tape()` (diffs vs previous snapshot only, prior tape discarded: `"tape": []`); `site/render.py` `moved_models()` (dots derive from tape+changelog).
- Failure scenario: Thursday's move disappears from Friday's page even though it's inside the promised 72h window; a model that moved two days ago loses its "moved" dot. The reader's core question (a) is answered for the wrong window while the label still says ~72h. Rule 8 caps age but nothing guarantees coverage.
- Evidence: code read of `mechanical_tape` + `moved_models`; current page only spans 72h because the snapshot is hand-made.
- Suggested resolution: carry forward prior tape entries still inside the 78h window (dedup by cell_ids+date), or relabel the tape "since yesterday's build".

**[MAJOR] With judgment ON, every move is reported twice and mechanical entries still say "no editorial layer"**
- Artifact: `tools/judgment.py` line 254 (`snap["tape"] = tape + snap["tape"]`); `collectors/run.py` line 178 (mechanical text prefix).
- Failure scenario: the tape doubles in length (judged entry + "Mechanical tape (no editorial layer): …" for the same cells) while the health footer says the judgment layer is on — self-contradictory labeling, and the 60-second scan pays for every move twice.
- Evidence: code read; prefix text at run.py:178, prepend at judgment.py:254.
- Suggested resolution: replace mechanical entries whose cell_ids are covered by accepted judged entries (keep uncovered ones for explainability), and drop the "no editorial layer" prefix when judgment is on.

**[MAJOR] The single-source-failure chaos drill is dead code — the fresh+carried merge path has zero test coverage**
- Artifact: `/home/user/model-eval-dashboard/tests/test_pipeline.py` lines 64–74: `run_pipeline(..., {"FAIL_SOURCES": "S2", ...}) if False else run_pipeline(..., {"OFFLINE": "1"})`.
- Failure scenario: the brief's drill "feed one source malformed HTML / one source down while the rest succeed" is claimed green in BUILDLOG but actually re-runs the all-down drill. Every offline test carries all cells forward, so the riskiest path in `collect()` — fresh observations merged with carried/emptied cells — is never executed by any test (my scratch runs above were its first exercise, and they surfaced the same-day-rerun bug).
- Evidence: file read; `if False` literal.
- Suggested resolution: fix the drill to `FAIL_SOURCES="S2"` with the other collectors stubbed/fixtured, asserting S2 cells carry `source down (last-good shown)` while S1 cells refresh.

**[MAJOR] "Zombie" sources never trip rule 9: retrieved_at is our fetch time for most collectors**
- Artifact: `collectors/base.py` line 73 (`fetched_at = now`), e.g. `collectors/aa.py` passing `self.fetched_at` for every cell.
- Failure scenario: a source that keeps serving frozen content (AA stops refitting, Arena stops publishing but the JSON endpoint stays up) is re-stamped fresh daily forever; the STALE badge can never appear. BUILDLOG explicitly weighed this for Epoch and added a visible "score dated" flag — AA/Arena/OpenRouter/llm-stats got no such mitigation.
- Evidence: code read; BUILDLOG Phase 7 paragraph; health line "S5 ok (data vintage 2026-05-08…)" shows the vintage idea exists but only ad hoc.
- Suggested resolution: track last-value-change date per cell (history already exists) and badge "unchanged for Nd" past a threshold, or stamp source-declared vintages where available.

**[MINOR] Partial source response blanks cells instead of last-good** — `collectors/run.py` lines 251–255: if AA renames a slug or A/B-drops a model row, the flagship cell becomes `— not published` for the day (loud, but the brief promised last-good semantics for source trouble; a slug rename is indistinguishable from genuine delisting). Demonstrated in the stub run ("59.86 -> None"). Fix: require N consecutive absent days before blanking, carrying last-good+flag meanwhile.

**[MINOR] Flag-only changes are invisible to tape/changelog** — `mechanical_tape`/`diff_entries` compare `value` only; an integrity flag appearing or disappearing (a trust-state change, and "new-integrity-flag detection" is a named judgment duty that mechanical mode lacks entirely) leaves no trace. Fix: include flag-set changes in `diff_entries`.

**[MINOR] `[skip ci]` is a no-op today but a Phase 8 booby trap** — daily.yml:82. The only workflow is schedule/dispatch-triggered, which `[skip ci]` never suppresses, so it currently does nothing. GitHub docs say skip instructions apply only to push/pull_request-triggered workflows; the built-in Pages branch deploy should therefore run — but if Phase 8 ever adds a push-triggered deploy workflow, the daily commit would suppress its own deploy. Verify Pages actually deploys on the first real dispatched commit; then delete the marker or comment why it stays.

**[MINOR] A failed-gate day loses that day's snapshot entirely** — commit step runs only after the gate; on a red gate the runner's `data/<date>.json` evaporates, leaving a permanent history gap ("keep snapshots forever") and no forensic artifact. Fix: `actions/upload-artifact` for `data/` + linter output on failure.

**[MINOR] Hang math can convert per-source degradation into whole-run loss** — `base.py`: 4 attempts × 60s + 40s backoff ≈ 280s per hanging source, sequential over 11 collectors vs the 15-min fetch step timeout: ~4 hanging sources kill the entire run (no page, no degraded cells) even though per-source degradation exists precisely for this. Fix: cap total per-collector wall time (~90s) or reduce retries in CI.

**[MINOR] Gate-protocol artifacts missing for this gate** — no `governance/innovator/phase-6.md`/`phase-7.md` (both are mandated innovator phases), no ADR-006/007 (the brief says the scheduler ADR is "still required"), no `redteam/phase-4..7` until this report, and ORDERING.md's promised Phase 7 extensions (no-catalog-model-without-column linter rule; chip-reassignment explainability) are unimplemented. Fix: land them with the gate resolution.

Not objections (checked and solid): concurrency group serializes schedule/dispatch correctly; secret scoped to one step; gate ordering (check before commit) means a red run publishes nothing; push-retry loop fails loud under bash `-e` on rebase conflict; `raw/` gitignored; repo-hygiene and rot-guard checks behave as documented; snapshot↔registry comparability sets are aligned (no first-run rule-4 trap); mobile 2-up, sticky header, keyboard nav, and hash/localStorage persistence all verified working.

---

**Counts: 3 BLOCKING · 8 MAJOR · 6 MINOR**

**COLD-READ VERDICT: PASS (conditional)** — (a) what moved: yes, ~15s via the tape; (b) trust: yes in the matrix (I/V + [S#] + ⚠ + claim bands read instantly, no docs needed) but the quick-look band carries zero trust metadata; (c) meaning: yes, X-panel with confidence/falsifier/cites, though over-long; (d) ordering: **unevaluable as ratified** — the shipped page renders a seed-era/c-group hybrid, not ADR-005's ordering C, so the C→D reversal condition must be re-tested on a regrouped render before it can be invoked or waived; (e) misleading spots: naked quick-look numbers and the legend's claim of a fold that does not exist.

Sources: [GitHub Docs — Skipping workflow runs](https://docs.github.com/actions/managing-workflow-runs/skipping-workflow-runs), [GitHub Changelog — skip pull request and push workflows](https://github.blog/changelog/2021-02-08-github-actions-skip-pull-request-and-push-workflows-with-skip-ci/)

Key files: `/home/user/model-eval-dashboard/site/render.py`, `/home/user/model-eval-dashboard/collectors/run.py`, `/home/user/model-eval-dashboard/tools/judgment.py`, `/home/user/model-eval-dashboard/.github/workflows/daily.yml`, `/home/user/model-eval-dashboard/tests/test_pipeline.py`, `/home/user/model-eval-dashboard/governance/ORDERING.md`. Attack scripts and rendered evidence: `/tmp/claude-0/-home-user-model-eval-dashboard/455bef83-e499-5358-96c4-59d7f44dc560/scratchpad/` (`attack_judgment.py`, `gate/`, `dbl/`, `ql/`, screenshots).
