# Red-team report — Phase 4 (briefs) + Phase 5 (implications) gate

Scope: `/home/user/model-eval-dashboard/data/2026-08-01.json` (8 implications, cells), `/home/user/model-eval-dashboard/data/briefs.json`, rendered `/home/user/model-eval-dashboard/docs/model-eval-monitor.html`, against rules 5/6/7/11 and the pre-registered weak points in `/home/user/model-eval-dashboard/governance/innovator/phase-5.md`. Baseline `make check` and `make test` (111 passed) are green; every attack below was demonstrated against that green baseline.

---

## BLOCKING

### [BLOCKING] IMP-1 ("Opus 5 leads the frontier", high) is a single-evaluator claim contradicted by three uncited independent boards on the same page

- Artifact: `imp-race-judged`, `data/2026-08-01.json` lines 2237–2254; rendered X panel directly under the quick-look band.
- Failure scenario: The daily 60-second read opens with "Opus 5 leads the frontier on both judged boards … On composite and judged-work measures the race's top is Anthropic-internal — confidence high." Both cited boards (`aa-index`, `gdpval-aa`) are the **same evaluator**, source S1, and GDPval is Gemini-graded. Meanwhile the same snapshot's independent boards rank: Epoch ECI **Sol #1** (161.69 > Fable 161.55 > Opus 161.05), LiveBench **Fable #1** (Opus third), Vals **Fable #1**, Arena **Fable #1**. Across the page's six independent multi-model boards, Opus is #1 on exactly the two AA boards. The printed clause "on composite … measures the race's top is Anthropic-internal" is directly falsified by epoch-eci (a composite whose top is non-Anthropic). "The largest top gap on the page" is additionally a cross-comparability-set superlative (Elo vs index points vs %). The falsifier is gerrymandered to AA-only observations ("AA order flips … GDPval refit"), so the boards that currently contradict the claim can never falsify it. The reader — an industry insider — walks away with "Opus leads, high confidence" from a page whose own ledger (`governance/SOURCES.md` S10: "the Sol>Fable order DIFFERS from AA, which is exactly row 2's purpose") and epoch-eci brief ("disagreement is the strong signal … exactly what the row exists to surface") declare that dissent load-bearing. The implications layer suppresses the exact signal the row was added to surface.
- Evidence: rank orders computed from the snapshot (see table above, reproduced by script); `governance/SOURCES.md` lines 50–52 (S1 covers both cited rows) and 142–144; `governance/ROWS.md` line 21; briefs `epoch-eci.what`. Innovator pre-registered the IMP-1/IMP-2 tension; its defense ("explicit scoping") fails because the scoping sentence itself over-claims beyond the two cited boards.
- Suggested resolution: rescope text to "both Artificial Analysis boards (one evaluator)", delete "composite and judged-work measures … Anthropic-internal" and "largest top gap on the page", cite or cross-reference the aggregator dissent, drop confidence to med, and widen the falsifier to include the non-AA boards.

### [BLOCKING] Held-implication rot: implications carry forward verbatim with no "cited cell moved" detection — a stale "answered" read survives the linter

- Artifact: `collectors/run.py:278` (`"implications": prev.get("implications", [])`), `tools/check_invariants.py` (rule 11 block, lines 521–551 — no text/value or status consistency check), `site/render.py:503–535` (renders `status: "answered"` with no under-review state).
- Failure scenario: demonstrated. I copied the data dir, changed `aa-index.opus-5` from 60.69 to 59.0 (with a tape entry, so explainability passes, and the derived cell recomputed). IMP-1 still renders "Opus 5 leads … AA Index 60.69 …", status `answered`, confidence `high` — **linter exit 0**. The judgment layer ships off by default (`health.judgment_layer: "off (mechanical)"`, and it stays off until a human adds `ANTHROPIC_API_KEY`), so from the first real daily fetch onward the mechanical pipeline copies all 8 implications forward forever while cells move under them. The X panel will assert numbers that no longer exist anywhere in the data layer, presented as current answers, indefinitely, with `make check` green. This is the implications-layer equivalent of "stale presented as fresh" (rule 9), and it was pre-registered by the innovator as the required third carry-forward state (UNDER REVIEW); it is implemented nowhere.
- Evidence: scratch run at `/tmp/claude-0/.../scratchpad/attack2/` — `invariant linter: all 12 constitutional rules green` with IMP-1 text `60.69` vs cell value `59.0` in the same snapshot.
- Suggested resolution: linter rule — any implication whose cited cells' values differ from a recorded per-cite value snapshot (or whose text quotes a number absent from its cited cells) must carry `status: "under review"` and render a badge; pipeline sets it mechanically on carry-forward when a cited cell changed.

---

## MAJOR

### [MAJOR] Rule 5 is unenforced in the briefs layer: a Pro-vs-Verified comparison renders into the published page with `make check` green

- Artifact: `tools/check_invariants.py:844–847` (snapshot filename regex excludes `briefs.json` as "auxiliary"); `check_html` (lines 619–718) has no family-name scan over page text; `site/render.py:673–717` renders brief prose verbatim into the page.
- Failure scenario: demonstrated. I set the `swe-bench-pro` brief's `what` to "Fable 5 scores 80.0 on SWE-bench Pro but 95.0 on SWE-bench Verified — the 15-point gap shows Verified is the easier scale…", rendered, and ran the linter over data + HTML: **green, exit 0**, sentence present in the page. Rule 5's machine contract covers rows, tape, and implications but not the third prose surface that ships on the page. Today's briefs are clean purely by authorial discipline (my per-sentence sweep of all briefs/implications/tape found zero co-mentions); any future edit — including the Phase 7 judgment layer or a Phase 9 touch-up — can rot this silently. Rule 6 (ARC tier in prose) and rule 11 grounding are likewise unchecked in briefs.
- Evidence: `/tmp/claude-0/.../scratchpad/attack1/` — `grep -c "easier scale" …/model-eval-monitor.html` → 1; `LINTER EXIT: 0`. Contrast: the same sentence placed in an implication is caught (`RULE5 … implication text compares SWE-bench Pro with Verified` — verified in attack 3).
- Suggested resolution: lint `briefs.json` (per-sentence `_mentions_both_families`) and/or add a page-level per-sentence family scan to `check_html`.

### [MAJOR] IMP-2's OPEN question is a false dichotomy the page's own new rows already answer past

- Artifact: `imp-open-preference`, `data/2026-08-01.json` lines 2255–2274.
- Failure scenario: the question is posed as "does **human preference** contradict the judged boards?" with reading 2 = "Arena settling noise." But the dissent is not preference-only: Epoch (composite, Sol #1), LiveBench (ground-truth, Fable #1), Vals (professional composite, Fable #1) all disagree with the AA order and none is a preference board or subject to Arena's variant churn. Reading 2 cannot explain them, and the falsifier ("next two Arena publishes") cannot close the actual question. A reader who watches Arena settle toward Opus will wrongly conclude the judged-board story is confirmed while three non-preference boards still dissent. The genuinely open question supported by the cells is "is the AA order the outlier?" — and the implication as framed steers away from it.
- Evidence: rank orders above; IMP-2 cites only arena/aa/gdpval cells, none of the four new rows.
- Suggested resolution: reframe as "is the AA order the outlier?" (or add a third reading), citing epoch-eci/livebench/vals cells, with a falsifier that includes those boards' next publishes.

### [MAJOR] Four briefs describe live rows as future — "Tracking on this page begins soon" is false on the shipped page

- Artifact: `data/briefs.json` — `epoch-eci.cadence`, `vals-index.cadence`, `livebench.cadence`, `swe-rebench.cadence`; all four rows are populated in `data/2026-08-01.json` and render with values.
- Failure scenario: reader clicks the live Epoch ECI row (5/5 populated values on screen), the slide-over says tracking "begins soon." Worse, the `swe-rebench` brief states "until then the quick-look coding slot shows GDPval, visibly labeled as a stand-in" — the built page's quick-look band actually shows `data-ql="swe-rebench"` (fallback at `site/render.py:470` not triggered). Phase 4's exit criterion is zero unverifiable sentences; these four are demonstrably false against the page they ship on. Each such catch trains the reader to distrust every other brief sentence.
- Evidence: `grep 'data-ql=' docs/model-eval-monitor.html` → `swe-rebench` present, no GDPval stand-in label; changelog entries "row activated at Phase 7 collector build" for all four rows. (Cause: Phase 4 briefs were written before the Phase 7 collector commit `7e34360` activated the rows; briefs were not re-swept.)
- Suggested resolution: update the four cadence sentences and delete the stand-in clause; add a test that "begins soon" phrasing never coexists with a populated row of the same id.

### [MAJOR] IMP-5's "two-lane demand" reading is matched by an equally supported price-artifact opposite reading — which IMP-4 on the same page supplies the evidence for

- Artifact: `imp-adoption-lanes`, `data/2026-08-01.json` lines 2319–2335 (pre-registered by the innovator as a likely downgrade).
- Failure scenario: "DeepSeek moves volume … Anthropic monetizes code" is read as demand momentum (the lens is "adoption momentum", confidence med). Opposite reading from cells on the same page: at $0.05/task and $0.44/$0.87 per Mtok, token share is a near-free-tier price artifact (cheap tokens are overweighted exactly as Anthropic's ~44% code-**spend** share is overweighted by the field's highest list price, $10/$50); the metric's own brief additionally declares the structural undercount ("premium providers undercount on token share while leading spend"). IMP-4 itself prices DS as a 60× cost outlier — so two implications read together hand the reader the ammunition against IMP-5's frame without acknowledging it. Also, the cited week itself has DS **displaced from #1** by xiaomi, which strains "moves volume" as momentum. Per the phase's own gate rule, an equally supported opposite reading forces reframe or OPEN.
- Evidence: `cost-per-task.ds-v4-pro` ($0.05), `api-price` row, `openrouter-share.*` flags, briefs `openrouter-share.independence`; innovator §10 concession.
- Suggested resolution: add one clause naming the price-artifact reading (shares weight tokens/dollars, not customers) or downgrade to OPEN; cheapest fix is a sentence, not a rewrite.

### [MAJOR] LiveBench Opus 5 score is dated a month before Opus 5 existed, per the page's own release dates

- Artifact: `data/2026-08-01.json` lines 1520–1531 (`livebench.opus-5`: value 80.5, `retrieved_at: "2026-06-25T00:00:00Z"`); briefs `livebench.harness` ("the release current at the 2026-08-01 check was dated 2026-06-25 and covered all five tracked models") vs briefs `opus-5.release` ("launched 2026-07-24", corroborated by S14, S20, and the ARC record date).
- Failure scenario: the metric brief's "Current values" list renders "Claude Opus 5: 80.5 [S12] · as of 2026-06-25" one click away from the model brief stating the model launched 2026-07-24. To the target reader this reads as fabricated provenance. Either the score was added to the 2026-06-25 release later (then `retrieved_at` misstates the datum's date and the brief sentence needs the board-updates-within-release explanation) or the score is misattributed. Same backdating pattern (retrieved_at = source vintage, not fetch time) exists on terminal-bench and metr cells but only here does it produce a visible impossibility.
- Evidence: files above; `site/render.py:707` renders `as of {retrieved_at[:10]}` in the brief.
- Suggested resolution: record the actual fetch date (or a separate `data_vintage` field) and add one brief sentence explaining that LiveBench releases accrue models after the rotation date.

---

## MINOR

### [MINOR] IMP-4's five-way superlatives cite only one of the five compared cells
"Field's worst knowledge profile… highest of the five" rests on a flag string on `aa-omniscience.ds-v4-pro` alone; the four comparison cells are uncited (rule 11 spirit). Fix: add the other four `aa-omniscience.*` ids to `cites` (they carry no linter-enforced flags, so it's free).

### [MINOR] "Largest top gap on the page" (IMP-1) is a cross-set superlative
Elo gaps are not comparable to index-point or percent gaps across comparability sets — the innovator's own contract (§0, rule 4 spirit) bans this in X copy. Fix: "largest #1–#2 gap of the two AA boards" or delete. (Listed separately so it survives even if IMP-1 is rescoped.)

### [MINOR] The 38.3 modified-harness ARC figure is quoted without any tier statement in IMP-6 and the arc brief
Rule 6 says every ARC-AGI-3 value carries its effort tier; the linter enforces it only on cells. 7.78 carries "Max-tier" in both texts, 38.3 carries nothing. Fix: append "(custom settings, no declared tier)" in both places.

### [MINOR] Orphan briefs: `aa-agentic-index` and `aa-halluc-rate` are unreachable dead content
`site/render.py:674` iterates snapshot metrics only; these briefs never render and nothing checks briefs↔metrics key sync (the inverse of the "begins soon" rot). Fix: a test that every briefs key exists in the snapshot or is explicitly marked pre-registered.

### [MINOR] IMP-6's "withheld" pillar is partially self-citation
`disclosure-watch.gpt-5-6-sol` (S21) is the pipeline's own curated judgment tagged `I`, and the withheld-vs-not-published distinction (3 of 5 models lack a Verified score; only Sol's absence is "withheld") is an editorial timing inference presented as data. The other two items stand on S4/S18, so the read survives; the brief does disclose curation. Fix: note the inference basis ("absence post-dates the METR flag") in the disclosure-watch brief or the flag text.

### [MINOR] Implication cites render as inert text, not anchors
`site/render.py:532` prints `cites aa-index.opus-5, …` as a plain span; the innovator's cross-format requirement 4 (one-tap verification keeps X tethered to I/V) is unmet. Fix in Phase 6: link cites to `data-cell-id` targets.

---

## What held up (checked and solid)

IMP-3's Pareto read (dominance holds at both cost endpoints, caveat in text, arithmetic verified), IMP-7 (honest OPEN, tiers stated, flag carried), IMP-8 (facts match cell flags, rule-5-safe wording), rule 7 mechanical carry (all six IMP-6 strings and all four IMP-8 strings verbatim-exact against cell flags), all falsifiers except IMP-1's are genuinely observable near-term, all implication arithmetic (0.83, +112, 13×/28–47×, Pareto set) reproduces, the shipped briefs/implications/tape pass a per-sentence three-family rule-5 sweep with zero co-mentions, brief SLA numbers all match snapshot `freshness_sla_hours`, and the linter demonstrably catches rule-5 text and rule-7 carry violations inside implications (attack 3). The api-price brief's claim about plain-V styling and legend is true against the renderer. The pre-registered "driver unresolved" carry convention was confirmed unenforced (attack 2a: a high-confidence cost implication with no caveat passes) — that finding is subsumed under BLOCKING-2's fix if the builder adds a note-class carry check, otherwise it should be logged in `governance/RISKS.md`.

## Counts

- BLOCKING: 2
- MAJOR: 5
- MINOR: 6

Attack artifacts (throwaway, reproducible): `/tmp/claude-0/-home-user-model-eval-dashboard/455bef83-e499-5358-96c4-59d7f44dc560/scratchpad/attack{1,2,3}/`. No source or data files in the repo were modified.
