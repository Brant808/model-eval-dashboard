# Phase 5 Innovator Report — Implications Layer: 5 Formats + 8 Candidate Implications

Prepared 2026-08-01 against `data/2026-08-01.json` (corrected-live snapshot), `governance/ORDERING.md` (ordering C, QL-A quick-look band, fold after C4), `governance/ROWS.md` (Pareto-frontier lens handed to Phase 5), and the machine contract in `tools/check_invariants.py`. Builder selects; this report expands the option space.

## 0. The machine contract every format must satisfy (linter, as implemented today)

Any format is a *renderer* over the same snapshot array `implications[]`. The linter (`tools/check_invariants.py`) enforces, per entry:

- **RULE11**: `tag == "X"`; `cites[]` non-empty and every id resolves to a real `metric.model` cell (empty cells ARE citable — `cell_ids` is built from `iter_cells`, which includes `value: null` cells; this matters because withheld cells are the disclosure signal); `confidence ∈ {high, med, low}`; non-empty `falsifier`.
- **RULE5**: cited cells' comparability sets may span at most ONE of the three SWE families (pro / verified / rebench), AND the `text` field may name at most one of "SWE-bench Pro" / "SWE-bench Verified" / "SWE-rebench" (regex `_mentions_both_families`, ≥2 hits fails). One mention of one family is legal.
- **RULE7**: `flags_carried[]` must contain, as **exact strings**, every flag on every cited cell that substring-matches an `INTEGRITY_MARKERS` entry (`record gaming`, `modified harness`, `withheld disclosure`, `self-report`, `proxy-model measurement`, case-insensitive). Extra voluntary entries are legal and unchecked.
- **Render side**: every implication element needs `data-imp-tag="X"` and `data-imp-conf` — this applies to every visual instance, including tape-embedded or strip-collapsed renderings (Formats D/E below).

Also binding by inheritance: rule 6 (any ARC-AGI-3 value quoted in X text should state its effort tier), rule 4 spirit (no cross-comparability-set superlatives in X copy), rule 12 (generic analysis only).

## 1. Cross-format requirements I recommend the ADR pin regardless of pick

1. **Schema orthogonality.** One `implications[]` schema for all formats: `{ id, tag:"X", lens, text, cites[], confidence, falsifier, flags_carried[], first_stated, regenerated_at, status }`. Format choice then lives entirely in `site/render.py` and is reversible without data migration or linter change.
2. **The third carry-forward state.** The brief defines fresh (cited cell changed → regenerate, new date) and held (unchanged → original date visible). There is an unstated third state this build hits *today*: **cited cell changed but no regeneration is available** (judgment layer is `off (mechanical)` per the snapshot's health block until Phase 7). A held implication whose citations moved must render an "UNDER REVIEW — cited data moved <date>" badge, never a silent hold. This should be a linter-checkable status, and it is the implications-layer analogue of "stale never presented as fresh."
3. **Flag-count affordance.** RULE7 propagation is heavy in practice: the Sol integrity implication below legitimately carries **six** exact flag strings. Every format needs a collapsed rendering (`⚠×6`, expandable) or the X layer visually drowns the data layer it must stay subordinate to.
4. **Cites as anchors.** Cell ids in `cites[]` render as chips that scroll-to/highlight the cited cell (Phase 6 mechanic). This is what keeps X from floating free of I/V: verification is one tap, in every format.

---

## 2. Format A — "Margin notes" (per-group read lines)

**Description.** One X-styled read line per domain section (C1–C7), rendered as a visually distinct strip at the bottom of the group, directly under the rows it interprets. Sections with nothing to say render no strip (absence is legal; the layer is not a quota). Each line: `X · confidence · date · text · cite-chips · ⚠flags · [reverses if… ⌄]` with the falsifier behind a disclosure toggle. Cross-domain implications must pick a home group or be split.

**Rendering sketch** (C1, real cells):

```
C1 · OVERALL INTELLIGENCE
  aa-index      60.69◆ | 59.86 | 58.89 …      [rows…]
┌ X · high · Aug 1 ─────────────────────────────────────────────────┐
│ Opus 5 leads both judged boards: AA 60.69 (+0.83 over Fable) and  │
│ GDPval 1857.8 (+112 Elo over Fable's 1746.1). Arena dissents —    │
│ open question, C1 footer.                                          │
│ cites: aa-index.opus-5 · aa-index.fable-5 · gdpval-aa.opus-5 · …  │
│ reverses if: AA order flips, or a GDPval refit puts anyone within  │
│ ~30 Elo of Opus  [⌄]                                               │
└────────────────────────────────────────────────────────────────────┘
```

**Carry-forward.** Per-line: fresh lines get `updated Aug 1`; held lines dim slightly and read `held since Jul 28`; moved-but-unregenerated lines get the UNDER REVIEW badge. Because lines are group-local, an aging line ages in place next to the data that could falsify it — the most honest possible carry-forward optics.

**FOR (strongest).** Zero top-of-page cost and maximum auditability: the claim sits one saccade from its evidence, so the X layer physically cannot drift from the cells — the reader's eye does the verifier's job for free.

**AGAINST (strongest).** It fragments "what does it mean" across seven locations, and ordering C's fold buries the integrity lens: the Sol three-open-items read would live in C7, below "daily read ends here." The page's sharpest current implication would be structurally invisible in the daily scan, and the QL band's disclosure-watch *count* (a number, not a reading) is the only above-fold trace.

**60-second scan (ordering C + QL + fold).** No added latency at the top; +2–3s per section for C1–C4 lines (~8–12s total, amortized into the scan the reader is already doing). But the scan ends at the fold, so C5–C7 implications are read only on deliberate descent — integrity and headroom reads effectively exit the daily loop.

**Lens interaction.** Imperfect mapping: race→C1, price-performance and adoption *share* C4, integrity→C7 (below fold), headroom→C6 (below fold). Two lenses compete for one strip; two lenses fall out of the daily read. Lens coverage is emergent, not guaranteed.

---

## 3. Format B — "The Read" (single daily panel, lens-slotted)

**Description.** One X panel pinned directly under the quick-look band, above C1. Four fixed slots — RACE / VALUE / ADOPTION / INTEGRITY — plus an optional OPEN slot; one line each, hard-capped (ellipsis to the brief layer beyond ~140 chars). Each line: lens label, confidence, date, text, collapsed cite/flag chips, falsifier behind a toggle. Panel header self-reports carry-forward state ("2 updated today · 2 held · 1 under review").

**Rendering sketch** (real cells):

```
QUICK LOOK   aa-index ◆ | arena | intel/$ | coding (GDPval)* | disclosure ct
─────────────────────────────────────────────────────────────────────────────
X · THE READ — Aug 1 · 4 updated today, 1 held
 RACE      high Aug 1  Opus leads AA (60.69, +0.83) and GDPval (+112 Elo);
                       Arena dissents → OPEN.               [cites] [⌄]
 VALUE     med  Aug 1  Pareto (index vs $/task): Opus·Sol·Kimi·DS efficient;
                       Fable ($3.15/59.86) is the one dominated point — by
                       its own stablemate. Cost driver unresolved. ⚠ [cites]
 ADOPTION  med  Aug 1  Two lanes: DeepSeek moves tokens (17.4%, wk 7/20),
                       Anthropic takes ~44% of code spend. Provider-level,
                       unit-flagged.                        [cites] [⌄]
 INTEGRITY high Aug 1  Sol: 3 open items — withheld post-METR disclosure,
                       modified ARC harness claim, METR cheating flag. ⚠×6
 OPEN      low  Aug 1  Preference vs judged work split at #1: Arena has
                       Fable +13 Elo over Opus max; AA/GDPval reversed.
                       Evidence even — watch next Arena publish.  [cites]
```

**Carry-forward.** Per-line dates plus the header roll-up. A held line keeps its original date in the slot; slots never vanish, so "INTEGRITY — held since Jul 29" is itself information (nothing new broke).

**FOR (strongest).** It answers the mission's third question ("what does it mean") in one fixed place inside the first screenful, and lens coverage is *structural* — a slot per lens means no lens can silently drop out the way A's fold drops integrity. Fastest possible meaning-latency.

**AGAINST (strongest).** It spends the page's most expensive real estate (above C1, on iPhone possibly half the first screen) on interpretation, and it is the format most likely to *contaminate* the data layer's authority: a well-written daily panel trains the reader to read X first and cells second, exactly the inversion the brief warns against. Hard caps and visual subordination (smaller type, X-tint) are mitigations, not cures.

**60-second scan.** +8–10s at the top, partially refunded because the reader no longer hunts for meaning per section; pushes C1 down ~120–160px (one extra swipe on iPhone before data). QL band → panel → tape → C1–C4 becomes the whole 60s loop; the fold's job is unchanged.

**Lens interaction.** 1:1 by construction; the standing lenses ARE the layout. Cross-lens items (the ARC headroom/coverage question) need a convention — OPEN slot or rotation.

---

## 4. Format C — "Standing questions" (question-answer framing)

**Description.** The four lenses render as four *permanent interrogatives* with mutable answers: "Who leads the frontier?", "Where is the price-performance frontier?", "Where is demand going?", "Who owes the field an explanation?" — placed where B's panel sits. The killer feature: a fifth state, **OPEN**, is first-class — when the gate's opposite-reading test shows even support, the question renders with both readings and no answer, styled distinctly. Questions never change; only answers, dates, and states do.

**Rendering sketch** (real cells):

```
X · STANDING QUESTIONS                                     read of Aug 1
 Who leads the frontier?                          high · answered Aug 1
   Opus 5 — AA 60.69 and GDPval 1857.8, both #1 among the tracked five.
   Dissent on record: Arena has Fable #1 (+13 Elo) → open Q below.
   [cites ⌄] [reverses if ⌄]
 Where is the price-performance frontier?         med · answered Aug 1 ⚠
   Through Opus ($2.34), Sol ($1.86), Kimi ($0.86), DS ($0.05); Fable
   ($3.15/59.86) sits inside it, dominated by Opus. Cost driver
   unresolved on all five inputs. [cites ⌄]
 Where is demand going?                           med · answered Aug 1
   Two lanes: DS volume (17.4% tokens wk 7/20; partial 7/27 has 20.9%),
   Anthropic premium (~44% of code spend). Provider-level, unit-flagged.
 Who owes the field an explanation?               high · answered Aug 1 ⚠×6
   Sol — three open items (withheld disclosure, modified harness, METR
   cheating flag). Every Sol headline needs the footnote first.
 ── OPEN · evidence even · posed Aug 1 ─────────────────────────────────
 Does human preference contradict the judged boards?
   Arena: Fable 1507.6 > Opus-max 1494.6. AA/GDPval: reversed. Reading 1:
   real preference/work split. Reading 2: settling noise + private-variant
   churn. Closes with the next two Arena publishes. [cites ⌄]
```

**Carry-forward.** The cleanest of all formats: the question is permanent, so "answered Aug 1 / unchanged since Jul 29" reads as natural language, and an UNDER REVIEW state slots in as "answer suspended — cited data moved." Answer-change history is a meaningful diff ("this question's answer flipped 3 times in July" is itself signal).

**FOR (strongest).** It makes the adversarial gate's downgrade path a *rendering state instead of a failure mode* — an implication that loses the opposite-reading test doesn't get awkwardly deleted, it visibly becomes OPEN, which is exactly the unvarnished posture an industry insider wants (the page showing its own uncertainty is a trust feature). It also maps 1:1 onto the mission sentence ("what does it mean") and builds daily habit through fixed anchors.

**AGAINST (strongest).** Interrogative framing pressures answers: "Who leads?" demands a name even on days the honest response is a shrug, and by day three the reader has memorized the questions, so ~25% of the panel's characters are ritual overhead in a format whose binding constraint is seconds. News that fits no standing question (today's SWE-bench Pro provenance correction) needs an "Also today" overflow or gets forced into the wrong slot.

**60-second scan.** +10–14s at the top (worst of the panel family — question lines cost vertical space), same C1 push-down as B plus ~2 lines. Mitigable by collapsing questions to short labels after first render (`RACE?` …), which converges it toward B.

**Lens interaction.** Identical to B (questions = lenses), plus native OPEN handling that B has to bolt on.

---

## 5. Format D — "Tape editorial + lens strip" (event-anchored implications)

**Description.** A genuinely different information model: interpretation rides the *movement stream*, not the page layout. Fresh implications render as indented X-entries directly under the tape move that triggered them (the tape is already the "what moved" surface; this fuses "what it means" onto it). Standing state that didn't move today lives in a single-line **lens strip** above the tape: four compact chips (`RACE Opus holds · VALUE Fable off-frontier ⚠ · ADOPTION two-lane · INTEGRITY Sol 3 open ⚠`), each dated, each expanding to the full implication (text/cites/confidence/falsifier).

**Rendering sketch** (real tape + cells):

```
X LENSES  RACE Opus holds (Aug1) · VALUE Fable off-frontier ⚠(Aug1)
          ADOPTION two-lane (Aug1) · INTEGRITY Sol 3 open ⚠×6 (Aug1)
TODAY'S TAPE
 Aug 1  AA refresh: GDPval refit moves Opus 5 to 1857.8; cost-per-task
        moved on all five — driver unresolved. [S1]
        └ X · med · Aug 1  The refit widens Opus's judged-work lead to
          +112 Elo, and the cost re-base pushes Fable off the computed
          value frontier — pending driver resolution. [cites] [reverses if ⌄]
 Aug 1  Provenance correction: SWE-bench Pro row re-sourced to the
        llm-stats vendor aggregate (0 of 43 verified)… [S13]
        └ X · high · Aug 1  The only board carrying these coding claims
          verifies none of them; treat the claims band as marketing
          telemetry until a standardized run covers ≥2 tracked models.
          [cites] ⚠self-report ×4
```

**Carry-forward.** Structural and self-evident for fresh items (a tape entry is dated by construction and scrolls out of the 72h window); held implications live only in the lens strip with `held since <date>` on expand. Note the hazard: rule 8 requires tape entries within ~72h — carried-forward X items therefore may NOT remain in the tape and must migrate to the strip, meaning one implication renders in two different homes across its life.

**FOR (strongest).** It matches the reader's actual first question. The 60s scan opens with "what moved"; welding "what it means" onto each move answers questions one and three in a single pass, and on a quiet day the layer costs one line of chrome — the only format whose cost scales with news volume.

**AGAINST (strongest).** State-implications don't fit an event stream: the Pareto read, the two-lane adoption structure, and the Sol integrity file are standing conditions, not moves, and they get compressed into four cryptic chips whose expansion the reader will stop performing by week two. And the dual-home lifecycle (tape → strip at 72h) is a comprehension hazard the red team will hit: the same X item changes position, styling, and neighborhood mid-life.

**60-second scan.** Best raw cost: +3–5s (one strip line + indented reads inside a tape already being read). But meaning-*depth* per second is lowest: the scan yields headlines of interpretation, not interpretation.

**Lens interaction.** Lenses become the strip; tape X-entries get a lens badge. Coverage is guaranteed (four chips always render) but at minimum expressiveness — INTEGRITY's six carried flags reduce to `⚠×6` behind a tap.

---

## 6. Format E — "Computed reads first" (two-tier: mechanical then editorial)

**Description.** Changes what an implication *is*. Tier 1: deterministic, pipeline-computed X statements — rank order with gaps, Pareto membership (the ROWS.md handoff made mechanical), share standings, integrity-item counts — regenerated every build as pure functions of the snapshot, full RULE11 fields included (mechanical statements have crisp falsifiers). Tier 2: authored/judgment-layer prose (any of formats A–D's voice), rendered below tier 1 and clearly badged as the interpretive layer. When the judgment layer is off — as it is today — tier 2 collapses to nothing and the page still ships a live, honest X layer.

**Rendering sketch** (real cells):

```
X · COMPUTED READS (deterministic from today's snapshot)
 • rank(aa-index): Opus 60.69 › Fable 59.86 › Sol 58.89 › Kimi 57.11 ›
   DS 44.27   Δ#1–#2 0.83 — order unchanged since Jul 31
 • pareto(aa-index × cost-per-task): efficient {Opus, Sol, Kimi, DS} ·
   dominated {Fable} ⚠ cost-driver unresolved — composition changed Aug 1
 • share(openrouter, wk 7/20, provider-level): DS 17.4 · Anthropic 9.1 ·
   OpenAI 6.9 — DS displaced by xiaomi 19.1; partial 7/27: DS 20.9
 • integrity(open items): Sol 3 ⚠×6 · all others 0
X · EDITORIAL — judgment layer off · mechanical build        [empty today]
```

**Carry-forward.** Trivially honest: tier-1 statements are recomputed each build, and the date shown is the last build on which the *statement itself* changed ("frontier composition changed Aug 1", "order unchanged since Jul 31") — recomputation and carry-forward are the same operation, so the UNDER REVIEW state can never occur in tier 1. Tier 2 inherits whichever prose format's dating is chosen.

**FOR (strongest).** It is the only format that is fully alive on day one (judgment layer off) and immune to the gate's opposite-reading attack — "Fable is the dominated point of {index, cost}" has no equally-supported opposite; it is arithmetic with a falsifier. Zero risk of uncited editorial anywhere.

**AGAINST (strongest).** Tier 1 answers "what is," not "so what": it cannot say *why* the DS token number shouldn't be read as V4 Pro demand, or that Sol's headline numbers need the footnote first — the actual insight lives in tier 2, which is empty precisely when the reader needs the page most (degraded mode). Shipped alone, it under-delivers the mission's third question and pushes interpretation cost back onto the reader's 60 seconds.

**60-second scan.** +6–10s for tier 1 (dense but pre-digested notation; notation literacy costs a few days). No section push-down beyond the strip. Meaning-latency worse than B/C, better than A/D.

**Lens interaction.** Race, price-performance, adoption all have natural mechanical forms; **integrity does not** — an open-items count is a pointer, not a reading. Integrity is structurally the weakest lens here and would lean on tier 2.

---

## 7. Comparison

| | A margin notes | B daily panel | C standing questions | D tape editorial | E computed-first |
|---|---|---|---|---|---|
| Top-of-page cost | none | ~8–10s / ~150px | ~10–14s / ~180px | ~3–5s / 1 line | ~6–10s / ~110px |
| "What it means" latency | high (assembled across groups) | lowest | low | low for moves, high for state | medium |
| Lens coverage guaranteed? | no (emergent; integrity falls below fold) | yes (slots) | yes (questions) | yes (chips, minimal) | 3 of 4 (integrity weak) |
| Open-question handling | ad hoc | bolt-on slot | **native state** | awkward | N/A tier 1 / inherits tier 2 |
| Carry-forward legibility | good (ages in place) | good (dated slots) | **best** (permanent Q, dated A) | hazardous (dual home at 72h) | best-in-class tier 1 (recompute = carry) |
| X-contaminates-data risk | lowest | highest | high | low | lowest |
| Judgment-layer-off fit (today) | needs authored lines | needs authored lines | needs authored lines | mechanical tape only | **fully alive** |
| Ordering-C/fold interaction | fold buries C6/C7 reads | above fold, complete | above fold, complete | above tape, complete | above fold, complete |
| Phase 6 (sticky header, iPhone 2-up) | rows scroll with groups — fine | pushes C1 one swipe down on iPhone | worst iPhone push-down | best mobile fit | good |

## 8. Recommendation (builder decides)

**Composite: C's structure in B's position with E's tier 1 embedded.** Concretely: a single above-C1 panel of the four standing questions (collapsible to short lens labels after first render, reclaiming most of C's vertical cost), where the price-performance answer's first clause IS the mechanical Pareto read (E tier 1, deterministic, alive with the judgment layer off), OPEN is a first-class state, falsifiers and cite chips sit behind one disclosure toggle, and flags render as `⚠×N` expandable. Adopt D's lens strip only as the panel's *collapsed mobile state*. Reversal condition for the ADR: if the Phase 5/6 gate's cold read shows the panel costing >~12s or pushing C1 below the first iPhone screen with QL present, fall back to Format A for C1–C4 **with the integrity read pinned into the quick-look band's disclosure-watch slot** (never below the fold).

---

## 9. Eight candidate implications from `data/2026-08-01.json`

All cell ids verified against the snapshot; `flags_carried` lists are the linter-**required** exact strings (RULE7); voluntary honesty carries listed separately (legal, unchecked). RULE5 checked on both citations and text for every entry. Confidence is argued, not asserted, because the gate will attack it.

### IMP-1 · lens: frontier race · confidence: high
**Text:** "Opus 5 leads the frontier on both judged boards: AA Index 60.69 vs Fable 59.86 and Sol 58.89 (a 0.83-pt #1–#2 gap), and GDPval-AA 1857.8 vs Fable 1746.1 — a +112 Elo margin, the largest top gap on the page. On composite and judged-work measures the race's top is Anthropic-internal; the Arena dissent is logged separately as an open question."
**cites:** `aa-index.opus-5`, `aa-index.fable-5`, `aa-index.gpt-5-6-sol`, `gdpval-aa.opus-5`, `gdpval-aa.fable-5`
**falsifier:** "Reverses if the AA order flips (any tracked model ≥ 60.69) or a GDPval refit puts a non-Anthropic model within ~30 Elo of the top."
**flags_carried (required):** [] — none of the cited cells carry INTEGRITY_MARKERS flags.
**Voluntary carries:** "Gemini-graded (AA judge panel)" (both gdpval cells); "evaluated as 'Claude Fable 5 (with fallback)'" (aa-index.fable-5).
**Confidence rationale:** two independent boards, same direction, large margin on one; scoped explicitly to judged boards so the Arena disagreement doesn't falsify it silently.

### IMP-2 · lens: frontier race · confidence: low · **status: OPEN (deliberately downgraded)**
**Text:** "OPEN — does human preference contradict the judged boards? Arena style-control has Fable 5 #1 at 1507.6 with Opus-max at 1494.6 (rank 5), the reverse of the AA/GDPval order. Reading 1: a real split between chat preference and judged work quality. Reading 2: settling noise — private-variant testing is active, Opus variants entered recently, and 13 Elo is within churn for a fresh board. The evidence supports both."
**cites:** `arena-elo.fable-5`, `arena-elo.opus-5`, `aa-index.opus-5`, `aa-index.fable-5`, `gdpval-aa.opus-5`, `gdpval-aa.fable-5`
**falsifier:** "Closes toward reading 1 if the next two Arena publishes hold Fable #1 with a stable-or-widening gap; toward reading 2 if an Opus variant overtakes as variants settle."
**flags_carried (required):** [].
**Voluntary carries:** "private variant testing active (Arena)" (both arena cells); "Gemini-graded (AA judge panel)".
**Why downgraded:** the opposite reading is equally supported from the same cells — exactly the case the gate hunts; shipping it pre-downgraded is the honest form.

### IMP-3 · lens: price-performance · confidence: med · **the mechanical Pareto read (ROWS.md handoff)**
**Text:** "Price-performance frontier, computed on AA index (higher) × cost-per-task (lower): Opus 5 ($2.34 / 60.69), Sol ($1.86 / 58.89), Kimi K3 ($0.86 / 57.11) and DS V4 Pro ($0.05 / 44.27) are Pareto-efficient. Fable 5 ($3.15 / 59.86) is the only tracked model strictly dominated — by its own stablemate, which scores higher and costs less. Caveat: all five cost inputs moved vs the seed with the driver unresolved; frontier composition is provisional until it resolves."
**cites:** all 5 `aa-index.*` + all 5 `cost-per-task.*` (10 cells)
**falsifier:** "Reverses if driver resolution or the next AA refresh moves Fable's cost ≤ $2.34 or its index above 60.69, or drops any efficient point behind another."
**flags_carried (required):** [].
**Voluntary carries:** "movement vs seed: driver unresolved (gate-flagged; both endpoints nominally v4.1)" (four cost cells); "largest relative move of the five (+79% vs seed)" (cost-per-task.gpt-5-6-sol); "newly captured (seed: not published)" (cost-per-task.ds-v4-pro).
**Note:** deterministic — computable in the pipeline as a pure function; falsifier is arithmetic. This is the implication that should survive judgment-layer-off mode.

### IMP-4 · lens: price-performance · confidence: med
**Text:** "DeepSeek's value position is an outlier, not a frontier-quality substitute: 885.4 index-pts per task-dollar is 13× Kimi's 66.4 and 28–47× the three Western flagships (Sol 31.7, Opus 25.9, Fable 19.0). But it buys 44-level intelligence with the field's worst knowledge profile — Omniscience −10.02 (more wrong answers than right) and a 0.940 hallucination rate, highest of the five. Cheap capability, not cheap reliability."
**cites:** all 5 `intelligence-per-dollar.*` + `aa-omniscience.ds-v4-pro`
**falsifier:** "Reverses if DS cost-per-task revises up by ~an order of magnitude on driver resolution, or its Omniscience index turns positive on the next AA refresh."
**flags_carried (required):** [].
**Voluntary carries:** the `derived:` provenance flags and "movement vs seed: driver unresolved…" (intelligence-per-dollar cells); "Gemini-graded (AA judge panel)" and "negative: more wrong answers than right; hallucination rate 0.940 — highest of the five" (aa-omniscience.ds-v4-pro).

### IMP-5 · lens: adoption momentum · confidence: med
**Text:** "Routed demand runs in two lanes: DeepSeek moves volume — 17.4% of OpenRouter tokens (wk 7/20, displaced from #1 by newcomer xiaomi at 19.1%, with the partial current week back at 20.9%) — while Anthropic monetizes code, at 9.1% of tokens but ≈44% of code-category spend. OpenAI holds 6.9%. All figures are provider-level with a flagged unit ambiguity; none of this attributes demand to any single model, including V4 Pro."
**cites:** `openrouter-share.ds-v4-pro`, `openrouter-share.fable-5`, `openrouter-share.gpt-5-6-sol`
**falsifier:** "Reverses if the completed wk 7/27 data keeps DeepSeek behind xiaomi (volume-lane story breaks) or Anthropic's code-spend share drops materially below ~35% (premium-lane story breaks)."
**flags_carried (required):** [].
**Voluntary carries:** "provider-level: DeepSeek total, not per-model" (and Anthropic/OpenAI counterparts); "unit per page copy ambiguous (counts consistent with tokens)"; "Anthropic ≈44% of code-category spend (30d) — leads programming spend"; "week 2026-07-20: #2 behind xiaomi (19.1%); partial wk 07-27: 20.9% #1".

### IMP-6 · lens: disclosure / integrity watch · confidence: high
**Text:** "Sol is the integrity story of this cycle: three open items — SWE-bench Verified withheld after METR's evaluation, a vendor-modified ARC-AGI-3 harness claim of 38.3 on the public set against an official Max-tier 7.78, and METR's cheating flag (a detected cheating rate higher than any public model they have evaluated). Every headline Sol number on this page needs the footnote before the comparison."
**cites:** `disclosure-watch.gpt-5-6-sol`, `arc-agi-3.gpt-5-6-sol`, `metr-horizon.gpt-5-6-sol`, `swe-bench-verified.gpt-5-6-sol` *(empty/withheld cell — a legal and load-bearing citation; the blank IS the evidence)*
**falsifier:** "Reverses item-by-item: publication of Verified with methodology, an official-harness ARC verification of the 38.3, or a METR re-evaluation without the cheating flag each closes its item; all three closed empties the read."
**flags_carried (required — all six exact strings):**
1. `"withheld disclosure: SWE-bench Verified not published after METR flag"` (disclosure-watch.gpt-5-6-sol)
2. `"modified harness: ARC-AGI-3 38.3 claim on vendor-modified settings (Jul 30)"` (disclosure-watch.gpt-5-6-sol)
3. `"record gaming (METR: cheating): flagged in pre-deployment eval (Jun 26)"` (disclosure-watch.gpt-5-6-sol)
4. `"modified harness: vendor claims 38.3 on the PUBLIC set via custom API settings (Jul 30); not on the verified board, excluded from this cell"` (arc-agi-3.gpt-5-6-sol)
5. `"record gaming (METR's term: cheating): detected cheating rate higher than any public model they have evaluated"` (metr-horizon.gpt-5-6-sol)
6. `"withheld disclosure: not published after METR flag"` (swe-bench-verified.gpt-5-6-sol)
**RULE5 check:** text names "SWE-bench Verified" once and no other SWE scale (one family = legal); cited sets span only the `verified` family plus non-SWE sets. This is the entry that motivates the `⚠×N` collapsed-flag affordance.

### IMP-7 · lens: frontier race (headroom facet) · confidence: low · **status: OPEN (second honest downgrade)**
**Text:** "OPEN — is the ARC-AGI-3 gap capability or coverage? Opus 5's 30.16 (High tier, the board record) stands against Sol's official 7.78 (Max tier) — but the record run cost $20,657, above ARC's published $10k cap (waived), the vendor disputes the Sol figure with a modified-harness 38.3 claim the board excludes, Fable has no verified score at any tier (the seed's 16.6 was withdrawn as unverifiable), and Kimi and DS were never evaluated. Reading 1: Opus holds genuine novelty headroom. Reading 2: a two-point board with non-comparable effort economics can't rank the field. Both hold."
**cites:** `arc-agi-3.opus-5`, `arc-agi-3.gpt-5-6-sol`, `arc-agi-3.fable-5`, `arc-agi-3.kimi-k3`, `arc-agi-3.ds-v4-pro`
**falsifier:** "Closes when the verified board covers ≥4 tracked models at comparable tiers; reading 1 dies if any newcomer lands within ~5 pts of 30.16 at equal-or-lower effort tier."
**flags_carried (required):** `"modified harness: vendor claims 38.3 on the PUBLIC set via custom API settings (Jul 30); not on the verified board, excluded from this cell"` (arc-agi-3.gpt-5-6-sol).
**Voluntary carries:** "record score (set Jul 24); board fraction 0.3016" and "run cost $20,657 — above ARC's published $10k cap (waived for record runs)" (arc-agi-3.opus-5); "no verified score at any effort tier; seed's 16.6 was unverifiable (provenance correction 2026-08-01)" (arc-agi-3.fable-5).
**Rule 6 discipline:** both quoted values carry their effort tiers in the text (30.16 High, 7.78 Max).

### IMP-8 · lens: disclosure / integrity watch (coding claims) · confidence: high
**Text:** "The frontier coding claims are un-arbitrated: the SWE-bench Pro aggregate carrying Fable's 80.0, Sol's 64.6 and DS's 55.4 verifies 0 of its 43 rows, Opus's 79.2 remains a launch claim on no board at all, and vendor-harness figures run ~20 points above the standardized Scale runs where those exist. Read the claims band as marketing telemetry with a known upward bias, not as measurement."
**cites:** `swe-bench-pro.fable-5`, `swe-bench-pro.opus-5`, `swe-bench-pro.gpt-5-6-sol`, `swe-bench-pro.ds-v4-pro`
**falsifier:** "Reverses if the aggregate begins independently verifying rows, or the standardized Scale board covers ≥2 tracked models within ~5 pts of their vendor claims (bias story dies), or Opus's 79.2 lands on a tracked board (provisional flag clears)."
**flags_carried (required — exact strings):**
1. `"aggregated vendor self-reports (0 of 43 verified)"` (fable-5, gpt-5-6-sol, ds-v4-pro — one string covers all three)
2. `"provenance corrected 2026-08-01: seed's 80.3 (tagged I) was Mythos 5's number; Fable 5 self-report is 80.0 (Anthropic PDF)"` (fable-5)
3. `"vendor self-report (launch claim 2026-07-24) — provisional in set: not yet on the llm-stats aggregate or any board"` (opus-5)
4. `"provenance corrected 2026-08-01: self-report (openai.com), max reasoning effort"` (gpt-5-6-sol)
**Voluntary carries:** `"vendor-harness figures run ~20 pts above the standardized Scale board (S9)"` (fable-5); `"listed as 'DeepSeek-V4-Pro-Max' (seed said not published)"` (ds-v4-pro).
**RULE5 check:** text names "SWE-bench Pro" once; "0 of its 43 rows" and "standardized Scale runs" do not match the Verified/rebench name regexes; cited sets are all `swe-bench-pro-vendor-aggregate` (one family).

---

## 10. Where I expect the gate to land (pre-registered weak points)

- **IMP-1 vs IMP-2 tension:** red-team will argue a "high" race read cannot coexist with an open question about the same #1. Defense is the explicit scoping ("on composite and judged-work measures") plus the cross-reference; if the gate rejects the scoping, IMP-1 drops to med, not to open — two boards agreeing is not evidence-even.
- **IMP-3/IMP-4 cost caveat:** the driver-unresolved flag is not linter-forced into `flags_carried` (it matches no INTEGRITY_MARKER). Both entries carry it in text and voluntarily in flags; the builder may want a Phase 5 rider adding `driver unresolved` to a note-class carry convention so the linter backs the practice.
- **IMP-5 opposite reading:** "DeepSeek's token share is price artifact, not demand momentum" is partially supported ($0.05/task); the two-lane framing already absorbs most of it, but the gate may force a downgrade to open — acceptable, the format (esp. C) has a native place for it.
- **Sentence-boundary gap (linter):** `_mentions_both_families` scans the whole `text` field, not sentences — so rule 5's "never in the same implication *sentence*" is enforced at entry granularity, which is stricter and safe. No action needed; noting so the ADR records that the machine check over-covers the rule here.

Key file paths: `/home/user/model-eval-dashboard/data/2026-08-01.json` (cells cited above), `/home/user/model-eval-dashboard/tools/check_invariants.py` (RULE11 lines ~521–551, `INTEGRITY_MARKERS` lines 55–61, `integrity_flags` line 206, family regexes lines 66–71), `/home/user/model-eval-dashboard/governance/ORDERING.md` (fold + QL band riders), `/home/user/model-eval-dashboard/governance/ROWS.md` (Pareto handoff, line under "Rejected / held").
