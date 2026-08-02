# Phase 3 Innovator Report — Relevance Orderings, Quick-Look Set, Default Trio, Catalog Scope, Chips, Promotion Mechanics

**Role:** innovator (read/run/web only; never edits source). **Date:** 2026-08-01.
**Inputs:** `/home/user/model-eval-dashboard/governance/BRIEF.md` (Phase 3 + Phase 6), `/home/user/model-eval-dashboard/governance/ROWS.md` (20-row Phase 2 draft, assumed to survive its gate roughly intact), `/home/user/model-eval-dashboard/data/2026-08-01.json` (all mock values), `/home/user/model-eval-dashboard/CLAUDE.md` (rules 1, 4, 5, 7, 10), `/home/user/model-eval-dashboard/governance/BUILDLOG.md` (Phase 1 landscape), `/home/user/model-eval-dashboard/governance/innovator/phase-2.md` (SWE-rebench and AA-Agentic values verified 2026-08-01), `/home/user/model-eval-dashboard/tools/check_invariants.py` (`compute_chips` contract).

**Binding context.** Phase 3 is a directive change: group position no longer encodes trust (the seed's "ordered by trust in the number" is dead). Ordering encodes *relevance*; trust rides entirely on per-cell I/V tags, warning tags, and staleness badges — which makes those tags load-bearing at any page position. The binding constraint remains the 60-second daily scan, and the two named hazards are (H1) a vendor-claimed number sitting high because it is relevant, and (H2) a default trio that flatters the home team.

**Row shorthand** (ROWS.md numbering): R1 aa-index, R2 epoch-eci, R3 gdpval-aa, R4 aa-agentic-index, R5 arena-elo, R6 terminal-bench, R7 swe-rebench, **R8 swe-bench-pro (V)**, R9 livebench, R10 metr-horizon, R11 arc-agi-3, **R12 swe-bench-verified (V)**, R13 disclosure-watch, R14 aa-omniscience, R15 aa-halluc-rate, R16 cost-per-task, R17 intelligence-per-dollar, **R18 api-price (V)**, R19 openrouter-share, R20 vals-index.

**A distinction the ADR should adopt before choosing an ordering (used throughout): two kinds of V.**
- **Authority-V** (R18 api-price): the vendor is the ground truth of its own list price. V here means "first-party fact," not "unverified claim." Placing it high is low-hazard.
- **Claim-V** (R8 swe-bench-pro, R12 swe-bench-verified): the vendor grading its own homework. V here means "unverified performance claim." Placing these high is exactly hazard H1.

Rule 1's binary tag stays binary; this is a *styling-weight* distinction (claim-V rows get quarantine styling — sub-band header "vendor-claimed," tinted row field, "claimed" in the row name — authority-V gets the plain V badge). If the builder rejects two-tier styling, the orderings below that place R8 high need cold-read proof at the gate.

All mocks use the same trio — **Opus 5 / GPT-5.6 Sol / Kimi K3** (the cross-vendor default candidate from §Decision 2) — so the orderings, not the trio, are what varies. Chips shown are **field-wide** per the current linter contract; rows whose field leader is outside the trio show a "field #1" footnote, which is itself an option under Decision 4. `[I]`/`[V]` = provenance tag, `⚠` = integrity/warning flag, `·d` = derived.

---

## Part 1 — Four materially different relevance orderings

### Ordering A — "Decision-Frequency" (act-daily first)

**Operational definition of relevance:** expected frequency with which a change in the row alters something the reader does or says *that same day* (what he tests, cites, routes work to, or flags to colleagues). Score ≈ (how often the number actually changes) × (probability a change triggers an action). Rows he acts on daily (race position, price-performance, adoption) outrank context he consults occasionally (headroom, annual-cadence boards) regardless of domain.

**Full 20-row grouping and order:**

| Group | Rows in order |
|---|---|
| A1. The race today | R1 aa-index, R2 epoch-eci, R5 arena-elo, R3 gdpval-aa, R4 aa-agentic-index |
| A2. Price-performance & adoption | R17 intelligence-per-dollar, R16 cost-per-task, **R18 api-price (V)**, R19 openrouter-share |
| A3. Coding: fresh vs claimed | R7 swe-rebench, R6 terminal-bench, **R8 swe-bench-pro (V, "claimed" sub-band)** |
| A4. Reliability & knowledge | R9 livebench, R14 aa-omniscience, R15 aa-halluc-rate, R20 vals-index |
| A5. Headroom | R10 metr-horizon, R11 arc-agi-3 |
| A6. Integrity & disclosure | R13 disclosure-watch, **R12 swe-bench-verified (V)** |

**Daily-read mock (first screenful, quick-look Set QL-A from Decision 1):**

```
TAPE ▸ 08-01 AA refresh: GDPval refit, cost-per-task moved on all five (driver unresolved) · 07-31 DS V4 Flash 0731 debuts at AA 50 (watch) · 07-30 OpenAI cuts Luna to $0.20/$1.20

QUICK LOOK          Claude Opus 5         GPT-5.6 Sol            Kimi K3
AA Index            60.69 [I] ◆FIELD-LEAD 58.89 [I]              57.11 [I]
Arena Elo           1494.6 [I]            1484.9 [I]             1485.8 [I]     field #1: Fable 5 1507.6 [I] (not in view)
Intel per $  ·d     25.9 [I·d]            31.7 [I·d]             66.4 [I·d]     field #1: DS V4 Pro 885 [I·d] (not in view)
SWE-rebench (fresh) 63.4 [I]              62.3 [I]               — not evaluated
Disclosure items    0 [I]                 3 open ⚠ [I]           0 [I]

A1 · THE RACE TODAY
AA Index v4.1       60.69 [I] ◆           58.89 [I]              57.11 [I]
Epoch ECI ⚑caveat   (collector lands Phase 7 — registry row)
Arena Elo (SC)      1494.6 [I] ⚑variants  1484.9 [I] ⚑added 7/31 1485.8 [I] ⚑renamed    field #1: Fable 5 1507.6
GDPval-AA v2        1857.8 [I] ◆ ⚑Gemini  1732.5 [I] ⚑Gemini     1687.43 [I] ⚑Gemini
AA Agentic Index    55 [I]                54 [I]                 (pending collector)

A2 · PRICE-PERFORMANCE & ADOPTION
Intel per $  ·d     25.9 [I·d]            31.7 [I·d]             66.4 [I·d]    field #1: DS V4 Pro 885
Cost per task       $2.34 [I] ⚑driver?    $1.86 [I] ⚑+79% vs seed $0.86 [I] ⚑driver?
API list price      $5/$25 [V]            $5/$30 [V] ⚑Luna cut    $3/$15 [V]   vendor-listed fact
OpenRouter share    9.1% [I] ⚑provider-lvl 6.9% [I] ⚑provider-lvl — not published (≈1.4% spend)
```

- **0–15s (quick look + tape):** Opus leads the composite race; Fable holds Arena #1 off-screen; value frontier (DeepSeek at 885 pts/$) is off-screen; Sol carries 3 open integrity items; a price cut happened in the Sol line. That is already "what moved / what do I trust / what it means" in skeleton.
- **15–40s (A1):** the race order is Opus > Sol > Kimi on both the composite and judged work; Arena disagrees (Fable #1) — release-settling caveat visible on Sol's cell.
- **40–60s (A2):** price-performance inverts the race: Kimi delivers 2.6× Sol's intelligence-per-dollar; the whole cost row wears the "driver unresolved" caveat, so no action on it today.

**Quick-look implication (today):** "Opus leads the race; the value frontier is entirely open-weights and off-screen; Sol is the integrity story."

**FOR (strongest):** it is the literal reading of the brief's directive — "what he acts on daily ranks above context he checks occasionally" — and it front-loads the two lenses (race, price-performance) that drive most daily actions, with adoption and integrity one scroll away.
**AGAINST (strongest):** "decision frequency" is a judgment about the reader, not a property of the data; when his focus shifts (say, a coding-claims war breaks out), the ordering is stale and only an ADR can move a group. Group semantics also mix domains (A2 holds both price and adoption), so wayfinding by topic is weaker than C's.
**60-second scan effect:** strong. The first two groups answer the two highest-frequency questions with 9 rows; the scan ends at A2 on most days, with tape + quick-look covering everything below the fold.
**H1 check (V rows):** R18 sits at overall position 8 — high, but it is authority-V (a list price), and the price-war tape entry is the very thing he wants near the top; plain V badge suffices. R8 sits at position 12 inside a labeled "claimed" sub-band directly below two I coding rows — the 80.0 [V] vs 64.5 [I] Fable gap becomes self-quarantining *if* the sub-band styling lands. R12 is at position 20, minimal risk.

---

### Ordering B — "Volatility-Weighted" (what moves, first)

**Operational definition of relevance:** the probability that the row changed since yesterday's snapshot, estimated from source cadence (freshness SLA) and observed churn in history; rows are grouped into cadence classes, fastest first. Relevance = expected daily delta salience: a row that never moves cannot be the reason he opened the page today. Note this ordering is *self-maintaining*: cadence classes can be recomputed from history rather than legislated.

**Full 20-row grouping and order:**

| Group | Rows in order |
|---|---|
| B1. Moves within the week | R5 arena-elo, R19 openrouter-share, R16 cost-per-task, R17 intelligence-per-dollar, **R18 api-price (V, event-driven)** |
| B2. Aggregate refresh (72h–monthly) | R1 aa-index, R3 gdpval-aa, R4 aa-agentic-index, R14 aa-omniscience, R15 aa-halluc-rate, R2 epoch-eci |
| B3. Release-event driven | R7 swe-rebench, R9 livebench, R20 vals-index, **R8 swe-bench-pro (V)**, R13 disclosure-watch |
| B4. Slow structural | R6 terminal-bench, R10 metr-horizon, R11 arc-agi-3, **R12 swe-bench-verified (V)** |

**Daily-read mock (first screenful; same quick-look band as A, omitted here for space — identical 0–15s read):**

```
B1 · MOVED / MOVES THIS WEEK
Arena Elo (SC)      1494.6 [I] ⚑variants   1484.9 [I] ⚑added 7/31  1485.8 [I]      field #1: Fable 5 1507.6
OpenRouter share    9.1% [I] Δwk −         6.9% [I] Δwk +1.7pp*     — not published  field #1: DeepSeek 17.4% (#2 behind xiaomi 19.1%)
Cost per task       $2.34 [I] ⚑driver?     $1.86 [I] ⚑+79% vs seed  $0.86 [I]
Intel per $  ·d     25.9 [I·d]             31.7 [I·d]               66.4 [I·d]      field #1: DS V4 Pro 885
API list price      $5/$25 [V]             $5/$30 [V] ⚑Luna cut 7/30 $3/$15 [V]
                                            (*partial week 07-27)
B2 · AGGREGATE REFRESH
AA Index v4.1       60.69 [I] ◆            58.89 [I]                57.11 [I]
GDPval-AA v2        1857.8 [I] ◆ ⚑Gemini   1732.5 [I] ⚑Gemini       1687.43 [I] ⚑Gemini
AA Agentic Index    55 [I]                 54 [I]                   (pending collector)
AA-Omniscience      31.27 [I] ◆ ⚑Gemini    21.7 [I] ⚑halluc 0.888   18.42 [I] ⚑Gemini
Hallucination rate ↓ 0.501 [I] ◆           0.888 [I] ⚠highest       0.509 [I]
Epoch ECI ⚑caveat   (collector lands Phase 7)
```

- **0–15s:** identical quick-look read to A.
- **15–40s (B1):** everything that plausibly changed overnight in one block: Arena settling, the OpenRouter xiaomi/DeepSeek fight (footnote), the unexplained cost swing, the Luna price cut. This *is* the tape, expanded into rows.
- **40–60s (B2):** the slower race standings confirm nothing reordered at board precision; Omniscience/hallucination read lands earlier than in any other ordering (Sol's 0.888 ⚠ inside the first minute).

**Quick-look implication (today):** "Four of the five things that moved this week are price/adoption facts; the race itself didn't reorder."

**FOR (strongest):** it directly serves question #1 of the reader's three ("what moved in the last 72 hours") — the page opens on exactly the rows most likely to differ from yesterday, and the ordering can be recomputed from history instead of debated.
**AGAINST (strongest):** it is structurally redundant with Today's tape, which already surfaces movement globally — spending the ordering axis on the tape's job wastes it; and volatility ≠ importance (Arena jitter tops the page daily while a once-a-quarter METR revision — the highest-stakes single number on the page — is buried in B4 at position 18). Group membership also drifts as cadences change, so the reader's spatial memory decays.
**60-second scan effect:** fastest on "what moved," weakest on "who leads": on a quiet day B1 is five rows of no-change and the race read starts at second ~35. Spatial stability is the worst of the four.
**H1 check (V rows):** R18 at overall position 5 is the highest V placement in any ordering — but it is authority-V and event-driven; a price row near the top during a live price war is the point. R8 at position 15 inside B3, adjacent to disclosure-watch — acceptable, but B3 mixes I and claim-V rows without a sub-band, so it needs the quarantine styling more than A does. R12 at position 20.

---

### Ordering C — "Capability-Domain Hybrid" (Apple-faithful sections, frequency-ordered)

**Operational definition of relevance:** two-level. Rows are grouped by *stable capability domain* (the way Apple groups by chip / display / battery — semantics that never move), and the domains themselves are ordered by decision frequency: the domains he acts on daily (overall standing, agentic work, coding, economics) precede the ones he consults occasionally (knowledge, headroom, integrity). Within a domain: independent composite first, then judged/event boards, then claimed.

**Full 20-row grouping and order:**

| Group | Rows in order |
|---|---|
| C1. Overall intelligence | R1 aa-index, R2 epoch-eci, R5 arena-elo |
| C2. Agentic & real-economy work | R3 gdpval-aa, R4 aa-agentic-index, R20 vals-index, R6 terminal-bench |
| C3. Coding | R7 swe-rebench, **R8 swe-bench-pro (V, "claimed" sub-band)** |
| C4. Economics & adoption | R17 intelligence-per-dollar, R16 cost-per-task, **R18 api-price (V)**, R19 openrouter-share |
| C5. Knowledge & reliability | R14 aa-omniscience, R15 aa-halluc-rate, R9 livebench |
| C6. Headroom | R11 arc-agi-3, R10 metr-horizon |
| C7. Integrity & disclosure | R13 disclosure-watch, **R12 swe-bench-verified (V)** |

(Builder option: swap C3 before C2 for this keyboard-first, coding-centric reader; that moves R8 to overall position 5 — see H1 note. R12 stays in C7, not C3: its Phase 2 decision value is *who withholds*, an integrity signal, and keeping it two groups away from R8 keeps rule 5 adjacency risk at zero.)

**Daily-read mock (first screenful):**

```
QUICK LOOK   (same band as Ordering A — 0–15s read identical)

C1 · OVERALL INTELLIGENCE
AA Index v4.1       60.69 [I] ◆FIELD-LEAD  58.89 [I]               57.11 [I]
Epoch ECI ⚑caveat   (collector lands Phase 7 — registry row)
Arena Elo (SC)      1494.6 [I] ⚑variants   1484.9 [I] ⚑added 7/31  1485.8 [I]     field #1: Fable 5 1507.6

C2 · AGENTIC & REAL-ECONOMY WORK
GDPval-AA v2        1857.8 [I] ◆ ⚑Gemini   1732.5 [I] ⚑Gemini      1687.43 [I] ⚑Gemini
AA Agentic Index    55 [I]                 54 [I]                  (pending collector)
Vals professional   (pending collector — registry row)
Terminal-Bench 2.1  — not published        — not published*        — not published   field #1: Fable 5 83.8 [I] ⚑self-run
                                            (*76.2 in submissions repo, not on canonical board)
```

- **0–15s:** identical quick-look read.
- **15–40s (C1):** the general-intelligence verdict from three *independent, differently built* reads (composite, second aggregate, human preference) in three rows — the strongest trust-triangulation opening of any ordering.
- **40–60s (C2):** who wins judged real work (Opus by ~125 Elo over Sol); also the most honest screenful on the page — two pending collectors and a 1/5-coverage row show the empty-cell discipline working, at the cost of scan seconds.

**Quick-look implication (today):** "Three independent methodologies agree on the Opus > Sol > Kimi order; on judged real-economy work the gap is wide; coding and value reads are one scroll down."

**FOR (strongest):** it is the most faithful implementation of the named reference — Apple's compare page is domain-sectioned, and domains give permanent spatial memory (coding is *always* the third section, this year and next), which compounds daily-scan speed over months; it also produces the page's single best integrity exhibit: swe-rebench 64.5 [I] directly above SWE-Pro-claimed 80.0 [V] (for Fable) makes the ~20-point claim-vs-fresh gap visible in one glance without violating rule 5 (different benchmarks, declared different sets).
**AGAINST (strongest):** seven groups is the most section chrome of any option (7 headers for 20 rows; C3 is a 2-row group), and the daily movers are scattered — Arena sits in C1, OpenRouter in C4, price in C4 — so "what moved" is assembled from three places (tape must carry that load alone). Early screenfuls also spend rows on pending collectors and 1/5-coverage boards.
**60-second scan effect:** good and — uniquely — *improving over time*: stable section semantics turn the daily scan into saccades to known coordinates. Day-one cost: the C2 screenful spends ~8 seconds on empty/pending cells.
**H1 check (V rows):** R8 at overall position 9 (position 5 if C3 moves up) — **the highest claim-V placement across all four orderings, and deliberately so**: it sits in a labeled "claimed" sub-band immediately below its independent counter-read, so the V value arrives pre-refuted rather than pre-trusted. This is the one placement where the quarantine styling is *load-bearing rather than advisory* — if the tinted sub-band + "claimed" row label is not adopted, C is unsafe and the red-team cold read will (correctly) kill it. R18 at position 12, authority-V, plain badge. R12 at position 20 behind disclosure-watch, whose "withheld" cell for Sol is the row's actual payload.

---

### Ordering D — "Act / Audit Two-Band" (binary triage, one fold)

**Operational definition of relevance:** binary, not scalar. For each row ask: "would a change here alter what I do *today*?" Yes → **TODAY band** (above one hard visual fold). No → **AUDIT band** (the verification layer: rows he consults to check whether a headline claim survives — occasionally, or when the tape points at them). Within each band, a fixed frequency order with thin sub-labels instead of full group headers. This is a different *information architecture* (2 bands, 1 fold), not a different sort key.

**Full 20-row grouping and order:**

| Band | Rows in order |
|---|---|
| TODAY (9) | R1 aa-index, R5 arena-elo, R3 gdpval-aa, R7 swe-rebench, R17 intelligence-per-dollar, R16 cost-per-task, **R18 api-price (V)**, R19 openrouter-share, R13 disclosure-watch |
| AUDIT (11) | R2 epoch-eci, R4 aa-agentic-index, R9 livebench, R20 vals-index, R6 terminal-bench, **R8 swe-bench-pro (V)**, R14 aa-omniscience, R15 aa-halluc-rate, R11 arc-agi-3, R10 metr-horizon, **R12 swe-bench-verified (V)** |

**Daily-read mock (first screenful):**

```
QUICK LOOK   (same band — 0–15s read identical)

━━ TODAY — the daily read ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AA Index v4.1       60.69 [I] ◆            58.89 [I]               57.11 [I]
Arena Elo (SC)      1494.6 [I] ⚑variants   1484.9 [I] ⚑added 7/31  1485.8 [I]    field #1: Fable 5 1507.6
GDPval-AA v2        1857.8 [I] ◆ ⚑Gemini   1732.5 [I] ⚑Gemini      1687.43 [I] ⚑Gemini
SWE-rebench (fresh) 63.4 [I]               62.3 [I]                — not evaluated  field #1: Fable 5 64.5 [I]
Intel per $  ·d     25.9 [I·d]             31.7 [I·d]              66.4 [I·d]    field #1: DS V4 Pro 885
Cost per task       $2.34 [I] ⚑driver?     $1.86 [I] ⚑+79%         $0.86 [I]
API list price      $5/$25 [V]             $5/$30 [V] ⚑Luna cut    $3/$15 [V]
OpenRouter share    9.1% [I] ⚑provider-lvl 6.9% [I]                — not published
Disclosure watch    none noted [I]         3 open ⚠⚠⚠ [I]          none noted [I]
━━ AUDIT — the verification layer (10 rows: aggregates, claims, slow boards) ━━
Epoch ECI ⚑caveat   (collector lands Phase 7) ...
```

- **0–15s:** identical quick-look read.
- **15–40s:** race + judged work + fresh-issue coding + value, i.e. all four daily lenses, inside one uninterrupted band with zero section breaks to parse.
- **40–60s:** price/adoption/integrity complete the TODAY band; on most days the scan legitimately *ends at the fold* — everything below is on-demand.

**Quick-look implication (today):** "The whole daily read is nine rows; nothing below the fold changed unless the tape says so."

**FOR (strongest):** it is the purest execution of the binding constraint — the 60-second scan is made *structural* (the fold is the 60-second mark), and the AUDIT band gives claim-V rows a natural quarantine home without any bespoke styling: "below the fold" *is* the quarantine.
**AGAINST (strongest):** the binary triage is brittle and opinionated — R7 in TODAY but R6 in AUDIT, R13 in TODAY but R14 in AUDIT are single-person judgment calls with no mechanical justification, and every future row forces a fresh fold decision; it also departs furthest from the named Apple reference (Apple has many sections, not two bands), and an 11-row undifferentiated AUDIT band scans poorly on the rare day he does need it.
**60-second scan effect:** best-in-class on speed (nine rows, one header, done), worst-in-class on wayfinding below the fold.
**H1 check (V rows):** R18 at position 7 in TODAY — authority-V, fine, and its two I price-neighbors (R17, R16) frame it. R8 at position ~17 and R12 at position 20, both deep in AUDIT — the *lowest* claim-V exposure of any ordering; D is the safe choice if the gate finds V styling under-weighted.

---

## Part 2 — The other Phase 3 decisions

### Decision 1 — Quick-look stat set (4–6 stats leading the page)

Selection constraints that matter more than taste: a quick-look stat must (a) be populated for essentially every catalog model (a headline band of "not evaluated" is dead weight — this kills metr-horizon, 2/5 coverage, paused source, Fable's value measured on Mythos Preview), (b) be I-tagged or derived-from-I (a V stat in the headline band is hazard H1 at maximum amplitude — this kills api-price as a *quick-look* stat), and (c) cover the four lenses so the band alone answers "who leads / what's it worth / is it adopted / do I trust them."

**Set QL-A — "Four lenses, five stats" (used in the mocks above):**
`aa-index` (race) · `arena-elo` (race, fast axis + settling detector) · `intelligence-per-dollar` (value, one number instead of two price rows) · `swe-rebench` (does capability hold on fresh work — the page's signature integrity-adjacent capability stat) · `disclosure-watch count` (integrity).
*Rationale:* every lens present; four of five are 5/5 or 4/5 coverage; nothing V-tagged. Fallback until the swe-rebench collector lands in Phase 7: substitute `gdpval-aa`.
*Cost:* adoption lens (openrouter-share) is absent — covered only by tape.

**Set QL-B — "Movement-first, five stats":**
`arena-elo` · `aa-index` · `cost-per-task` · `openrouter-share` · `disclosure-watch count`.
*Rationale:* optimized for "what changed overnight" — these are the five highest-churn populated rows; pairs naturally with Orderings B and D.
*Cost:* no coding/agentic capability stat at all in the band; cost-per-task currently wears a "driver unresolved" caveat, which would put a flagged number in the headline band on day one (arguably honest, arguably noisy); openrouter-share's provider-level caveat means Fable and Opus show the same 9.1%.

**Set QL-C — "Capability-depth, six stats":**
`aa-index` · `arena-elo` · `swe-rebench` · `metr-horizon` · `intelligence-per-dollar` · `disclosure-watch count`.
*Rationale:* adds the only absolute long-horizon measure to the headline band.
*Cost:* metr-horizon violates constraint (a) — in the default trio it renders as one flagged 11.3h [⚠ cheating] + two "not evaluated"; a quick-look band should not open the page with two blanks and the page's most heavily flagged number. Included to make the rejection explicit, since the assignment names it: **recommend against** until METR resumes publication and coverage reaches ≥4/5.

*Innovator lean:* QL-A. It is the only set where the band alone answers all three of the reader's questions, and it contains zero V cells and zero structurally empty cells for the current five columns (one "not evaluated" for Kimi on swe-rebench, which is itself signal).

### Decision 2 — Default compare trio: argue the RULE, not the trio

The hazard is outcome-perception (H2): the reader works in the industry; two home-team columns on first load reads as flattery even if the rule was mechanical. Candidate rules, each fully deterministic from the snapshot:

| Rule | Today's output | Slot order (mobile shows first 2) |
|---|---|---|
| **T1.** Top-3 models by AA index | Opus 5, Fable 5, Sol | Opus, Fable |
| **T2.** Top model per vendor, top-3 vendors by their best model's AA index | Opus 5, Sol, Kimi K3 | Opus, Sol |
| **T3.** Top-3 by Arena Elo (style control) | Fable 5, Opus 5, Kimi K3 | Fable, Opus |
| **T4.** Capability leader (AA #1) + value leader (intel/$ #1) + biggest 72h mover (largest normalized Δ among I-tagged group-1 rows) | Opus 5, DS V4 Pro, Sol (cost +79% mover) | Opus, DS |
| **T5.** One per camp: best US-closed, best US-challenger, best open-weights (by AA) | Opus 5, Sol, Kimi K3 | same as T2 today |

**Why T2 (top model per vendor) is the most defensible rule:**
1. *Rule-neutral AND outcome-clean.* T1 and T3 are rule-neutral but outcome-suspect — both put two Anthropic models in the default today (T3 also reorders weekly with Arena jitter, churning the first-load view). T2 cannot produce a same-vendor pair by construction, so no future data drift can ever make the default look like home cooking. The defense of the default never has to mention today's scores — that is what "justified on neutral grounds" means.
2. *Information-maximal.* Same-vendor columns correlate heavily (shared training stack, pricing philosophy, disclosure posture); Opus vs Fable spends a third of the page on within-family deltas. Three vendors maximize what the trio teaches per row. Apple's own default compares three *different* Macs, not two configurations of one.
3. *Stable.* Vendor leaders change on releases (weeks-to-months), not on daily jitter; contrast T3 (weekly churn) and T4 (daily churn by construction).
4. *Honest cost, cheaply paid.* The real objection: it hides the actual #2 model (Fable, AA 59.86 > Kimi 57.11) from first load. Mitigations already on the page: Fable appears in the quick-look "field #1" footnotes (Arena, swe-rebench, terminal-bench), in tape, and is one picker keystroke away; and the persisted URL-hash selection means the default only ever governs the *first-ever* load.

T4 is the strongest alternative — "the field state in three columns" (leader, value frontier, mover) is a genuinely different and attractive philosophy — but it needs a mover definition robust to caveated cells (today's mover is Sol's +79% cost swing, which carries a "driver unresolved" flag: the default trio would be selected *by* a number the page itself does not yet trust), and it churns daily. Viable as a labeled secondary preset ("Field state") in the picker, not as the first-load default.

Slot-order note: whatever rule wins must also order slots (mobile shows slots 1–2). T2 ordered by AA index gives Opus + Sol on iPhone — cross-vendor even at 2-up width. T1/T3 give an all-Anthropic mobile pair, compounding H2 on the device he reads at breakfast.

### Decision 3 — Picker catalog scope (which older models stay selectable)

Candidates from Phase 1 research: Opus 4.8 / 4.7 / 4.6, Sonnet 5, Mythos Preview, GPT-5.5 / Terra / Luna, Grok 4.5, Muse Spark 1.1, Gemini 3.1 Pro / 3.6 Flash, GLM-5.2, Kimi K2.6, DS V4 Flash 0731 (watch), Qwen3.8-Max (preview — watch only).

Hard constraint to keep in view: every catalog model needs all 20 rows collected or reasoned-empty, ships embedded in the page (Phase 6: picker swap <100ms, page <1.5MB), and appears in field-wide chip computation. Catalog size is a collector-cost and QA multiplier, roughly linear.

**Rule S1 — Coverage floor:** a model is selectable iff ≥3 matrix rows are populated from *independent* sources (fresh per SLA).
Estimated pass list today (needs collector-time verification, flagged as such): Opus 4.8, Sonnet 5, Terra, Luna, Muse Spark 1.1 (Scale S9 + Arena + TB = exactly 3), Gemini 3.6 Flash, Grok 4.5 (borderline), Kimi K2.6 (borderline). Fails: DS V4 Flash 0731 (1 source — stays watch), Mythos Preview (METR only), Opus 4.7/4.6, GLM-5.2 (likely), Gemini 3.1 Pro (likely borderline). Catalog ≈ 11–13.
- **FOR:** guarantees no picker choice ever lands on a near-empty column (the Apple analog: every selectable Mac has a full spec sheet); mechanical and linter-checkable; automatically admits laterals like Muse Spark and Gemini Flash, which answers the Phase 1 "Google absence-as-signal" open item by making Google's best *visible and comparable*.
- **AGAINST:** coverage counts drift — models can silently enter/exit the picker as sources refresh or go stale, which is spooky UX; and it obliges collectors to fetch ~8 extra models across ~6 sources from day one.

**Rule S2 — Lineage + promotion:** catalog = current five columns + the direct predecessor of each (Opus 4.8; Sonnet 5 for the Fable line; GPT-5.5; Kimi K2.6; DS predecessor per registry call) + line-siblings with distinct price points (Terra, Luna) + any watch-promoted model (Muse Spark 1.1 qualifies today at 2+ independent group-1 sources). Catalog = 11–12, fixed membership, grouped in the picker exactly like Apple's "current / older" split.
- **FOR:** bounded, predictable, semantically clean ("compare against what it replaced" is the reader's actual legacy question — is Opus 5 really better than 4.8?); "direct predecessor" gives each old model an obvious picker label; zero drift.
- **AGAINST:** excludes data-rich laterals (Grok 4.5, Gemini 3.6 Flash, GLM-5.2) even when independent boards cover them — Google stays structurally invisible except in tape; and "direct predecessor" requires a per-vendor registry judgment (is Fable 5's predecessor Sonnet 5 or Mythos Preview? — needs an ADR line either way).

**Hybrid worth pricing (S2+):** S2's lineage skeleton **plus** a standing "field seats" clause: the best model per major absent vendor *iff* it meets S1's 3-source floor (adds Gemini 3.6 Flash and possibly Grok 4.5; ~13 total). Costs two collector targets; buys the cross-vendor field view and kills the "why is Google not even selectable" question. If the builder wants one rule, S2+ is the innovator lean; between the two named rules, S2 for predictability.

### Decision 4 — Chip ties, and trio-relative vs field-wide

Current linter contract (`compute_chips`, `/home/user/model-eval-dashboard/tools/check_invariants.py`): chip = leader within a declared comparability set, computed field-wide over I-tagged, populated, non-stale, finite-numeric cells; ≥2 eligible competitors required; direction-"none" never chips; **ties: all tied leaders chip ("Phase 3 may tighten")**.

**Tie handling — three options:**
1. *All tied chip (status quo).* Honest; but the live tie case exposes a flaw: `openrouter-share` Fable 9.1 = Opus 9.1 is not a tie between models — it is **one provider-level number duplicated across two columns** (flagged as such on the cells). Under the status quo both chip, manufacturing a fake "co-lead." Whatever tie rule wins, provider-level rows must either dedupe by provider before chip computation or be declared chip-ineligible; this is a linter tightening, not a styling choice.
2. *No chip on tie.* Cleanest rows, but hides real information (two ahead of a third) and makes chips flicker as decimals settle around ties.
3. *Tied leaders chip with a distinct "CO-LEAD" label* (same glyph, different label — shape+label per rule 4). Keeps honesty, kills the "two winners?" confusion. **Lean: option 3 + the provider-dedupe fix.**

**Trio-relative vs field-wide — both sides honestly:**
- *Field-wide (status quo).* A chip means "best in the tracked field" — a strong, constitutionally aligned semantic (rules 4/10 are enforced field-wide by the linter; the built page's chips and the linter's recomputation stay one and the same). Crucially, the *absence* of a chip in the visible trio is itself field-awareness: in the default Opus/Sol/Kimi view, the Arena row shows no chip because Fable leads off-screen — which is exactly the Phase 6 requirement that field movement stay discoverable from within a 3-model view. Cost: rows where the leader is off-screen read as strangely chipless ("dead rows"), and a naive reader may crown the visible max anyway.
- *Trio-relative.* Matches Apple's mental model (compare what's on screen) and always gives each row a visible anchor; recomputes trivially under the 100ms swap budget. Cost: a chip would crown mid-field models (Kimi "leads" intel/$ in the default trio while the field leader is 13× better off-screen), the chip's meaning changes with every picker swap, and the linter's field-wide chip contract would need a parallel visual grammar to avoid rule-4/10 ambiguity about what a chip *is*.
- *Recommended synthesis:* keep field-wide chips as the only *chips*, and give every direction-bearing row whose field leader is outside the current selection a small **"field #1: <model> <value> [tag]"** footnote (as mocked throughout Part 1). This resolves dead rows without diluting chip semantics, doubles as the Phase 6 field-awareness mechanism, and — because the leader is named with its own I/V tag — stays inside rule 10 (a V value can never be named field #1 against I competition, since it can never win the field-wide computation).

### Decision 5 — How new models enter the catalog and the default

Entry pipeline (Phase 7 fixes the promotion *threshold*; Phase 3 fixes the *mechanics*):
1. **Watch → catalog:** a watch item auto-promotes when seen in ≥2 independent group-1 sources (brief). On the promoting build: picker gains the model under an "Added <date>" divider with a movement dot; a tape entry announces the addition (rule 8 source-id'd); the addition note renders per spec. All 20 rows must materialize as cells or reasoned-empties in that same snapshot — the linter should enforce "no catalog model without a full column."
2. **Chip shock is expected and must be explained:** a promoted model immediately joins field-wide chip computation and can strip a chip from a trio member overnight (Muse Spark could plausibly take a TB or Scale-set chip). The explainability test already forces every changed cell into tape/changelog; the ADR should extend that to *chip reassignments caused by catalog membership changes* so the reader never sees a chip vanish silently.
3. **Never touch the user's selection:** URL hash / localStorage selection always wins; promotion never edits slots.
4. **Default trio recompute — three options:**
   - *M1 Event-driven + hysteresis (lean):* the default is the rule's (Decision 2) output, recomputed only when (a) catalog membership changes, or (b) the rule's output differs for N consecutive daily snapshots (N=3 proposed — kills decimal-jitter churn; today's Fable/Sol gap is under 1 index point, exactly the jitter zone). Deterministic from snapshot history; renderer stays pure.
   - *M2 Live:* recompute every build. Always current; first-load view can churn daily under T3/T4-style rules (harmless under T2, which changes only on releases — note the interaction: the more stable the Decision-2 rule, the cheaper M2 becomes).
   - *M3 ADR-pinned:* default changes only by ADR. Maximal governance honesty, guaranteed rot; a September release would leave a stale default until someone writes a document.
5. **Test case, decidable now:** Muse Spark 1.1 already sits at 2+ independent sources (Scale S9, Arena, TB — snapshot watch entry). It should enter the **catalog** at Phase 6/7 launch, and under rule T2 it does **not** enter the default (no AA index value yet; T2 should be scoped to AA-covered vendors, with the scoping stated in the ADR). DS V4 Flash 0731 (1 source) stays a watch/tape item — the promotion rule visibly doing its job on day one.
6. **Retirement:** a superseded model moves to the picker's "older" group (Apple keeps old Macs selectable); cells persist forever (history is constitutional); it exits chip eligibility only if its cells go stale past SLA — which the existing non-stale condition in `compute_chips` already handles with zero new code.

---

## Part 3 — Comparison table and recommendation

| | A. Decision-frequency | B. Volatility-weighted | C. Domain hybrid | D. Act/Audit two-band |
|---|---|---|---|---|
| Relevance definition | freq(change) × P(action) | P(changed since yesterday) | stable domains, frequency-ordered | binary: act-today vs audit |
| Groups | 6 | 4 (cadence classes) | 7 | 2 bands + sub-labels |
| Seconds to "who leads" | ~20 | ~35 | ~20 | ~18 |
| Seconds to "what moved" | tape + A2 (~45) | ~20 (B1 *is* the movers) | tape only (~15 via tape) | tape + TODAY (~40) |
| Spatial memory over months | medium (groups move with his habits) | weak (membership drifts with cadence) | **strongest** (domains never move) | strong above fold, weak below |
| Claim-V exposure (R8/R12) | pos 12 (sub-band) / 20 | pos 15 / 20 | **pos 9 (sub-band, load-bearing) / 20** | pos ~17 / 20 (lowest) |
| Authority-V (R18) | pos 8 | pos 5 (highest) | pos 12 | pos 7 |
| Distinct failure mode | ordering rots when his focus shifts | duplicates the tape; buries METR at 18 | section chrome; movers scattered | brittle binary triage; Apple-unlike |
| Apple-compare fidelity | medium | low | **high** | low |
| Redundancy with tape | low | **high** | none | low |

**Recommendation (builder decides).** **Ordering C**, with three riders: (1) the claim-V quarantine styling (tinted "vendor-claimed" sub-band + "claimed" in the row name) is a *precondition*, not a nice-to-have — C places R8 at position 9 on purpose, as a pre-refuted exhibit under swe-rebench, and without the styling C fails hazard H1 at the gate; (2) adopt the "field #1" footnote from Decision 4 so C's scattered movers and off-screen leaders stay discoverable from any trio; (3) if the red-team's cold read shows the 7 headers costing more than ~5 seconds, collapse C5+C6 into one "Knowledge & headroom" section (6 groups) before abandoning C — its stable-domain advantage is the only property here that compounds over months of daily reads. Runner-up: **A** (safest all-around, weakest long-run spatial memory). **D**'s fold concept is worth stealing regardless of winner: whichever ordering ships, place a subtle "daily read ends here" rule after the second group. **B** should lose: it spends the ordering axis re-doing the tape's job.

For the remaining ADR lines, the innovator leans recorded above: quick-look **QL-A**; default-trio rule **T2** (top model per vendor by AA index, slots ordered by AA — the only rule that is both rule-neutral and outcome-clean, today yielding Opus 5 / GPT-5.6 Sol / Kimi K3); catalog rule **S2+** (lineage + promotion + 3-source field seats), or S2 if one of the two named rules must win; chips **field-wide only, ties chip with a CO-LEAD label, provider-level rows deduped before computation** (a required linter tightening either way); promotion mechanics **M1** (event-driven recompute with 3-snapshot hysteresis), with Muse Spark 1.1 entering the catalog-not-default as the rule's first public test.

---

**Key file paths for the ADR:** `/home/user/model-eval-dashboard/governance/ROWS.md` (row numbering used throughout), `/home/user/model-eval-dashboard/data/2026-08-01.json` (every mock value), `/home/user/model-eval-dashboard/tools/check_invariants.py` (`compute_chips` — the tie clause "Phase 3 may tighten" and the provider-dedupe gap flagged in Decision 4), `/home/user/model-eval-dashboard/governance/innovator/phase-2.md` (source of the swe-rebench 64.5/63.4/62.3/40.2 and AA-Agentic 55/54 values, verified 2026-08-01; collectors land Phase 7).

Two verification notes for the red-team/verifier: (1) intelligence-per-dollar figures in the mocks are my own division of snapshot cells (e.g. Opus 60.69 ÷ $2.34 = 25.9; DS 44.27 ÷ $0.05 = 885.4) — the derived-cell convention in ROWS.md computes these in the pipeline, so treat my arithmetic as illustrative; (2) epoch-eci, livebench, vals-index, and (partially) aa-agentic-index render as "pending collector" in the mocks because they are registry rows without snapshot cells today — the mocks show them honestly rather than inventing values, which is itself a preview of how the first post-Phase-7 page will look if orderings place them high.
