# DECISIONS — Architecture Decision Records

Numbered ADRs. Format: context, options considered, choice, rejected-because,
reversal condition. One or more per phase; the phase-boundary commit message
carries the ADR number.

---

## ADR-001 — Phase 0: harness architecture and gate resolutions (2026-08-01)

**Context.** The brief mandates a governance-first build: repo scaffold,
constitutional rules as automated checks, adversarial gate before any product
work. Everything downstream (collectors, renderer, CI) sits on these choices.

**Options considered.**
1. *Language*: (a) Python 3.11 stdlib+requests; (b) Node 22; (c) mixed.
2. *Invariant enforcement*: (a) one linter script over data + built HTML with
   negative tests; (b) JSON Schema validation only; (c) checks embedded in the
   renderer.
3. *latest.json*: (a) copy; (b) symlink.
4. *Chip semantics* (rules 4/10 need an operational definition): (a) leader
   among independent, populated, non-stale, finite numeric cells sharing the
   metric's comparability set, requiring ≥2 competitors, ties all chip;
   (b) leader among all populated cells with V allowed when no I exists;
   (c) no chips until Phase 3.
5. *HTML checking*: (a) regex over renderer-emitted attributes; (b) stdlib
   html.parser indexing; (c) external DOM lib (bs4).

**Choices.** 1(a) — single runtime, deterministic, CI-fast; Node adds nothing
here (rejected b: two runtimes to keep deterministic; c: worst of both).
2(a) — schema validation alone cannot express cross-cell rules like chip
legitimacy or Pro/Verified separation (rejected b); embedding checks in the
renderer lets a renderer bug disable its own audit (rejected c).
3(a) copy — symlinks break on some CI checkouts and Pages deploys (rejected b).
4(a) — V values never chip even unopposed (rule 10's spirit: a vendor claim is
never presented as a lead), and uncontested "leads" are misleading superlatives
(gate finding M8); (b) violates rule 10; (c) would ship a Phase 0 page with no
comparability discipline to test against.
5(b) — the gate proved regex checking is quote-style-forgeable (finding M4);
bs4 adds a dependency for what stdlib does (rejected a, c).

**Gate resolutions.** Verifier countersigned unconditionally (31/31 MATCH).
All 13 red-team findings resolved in code with permanent regression tests —
see `governance/redteam/phase-0.md`. One residual accepted: RISK-005
(Bash-write hook bypass; CI is the authority). RISK-001 (name in governance
docs), RISK-002 (cron activates at merge), RISK-003 (mid-session hook load),
RISK-004 (push 403, open) logged.

**Reversal conditions.** Python choice reverses if a collector needs a
headless browser (would add a Node/Playwright sidecar, not replace Python).
Chip semantics revisit at Phase 3 (tie handling, per-trio vs field-wide).
Linter architecture reverses only if the single-file linter exceeds ~1kloc or
needs sandboxed execution of untrusted input.

## ADR-002 — Phase 1: source grounding, re-sourcing SWE-bench Pro, scouted additions (2026-08-01)

**Context.** Phase 1 live-verified every brief source. Most held up; the
"Morph-tracked SWE-bench Pro board" did not — it is a bot-blocked editorial
page whose numbers are llm-stats' 100%-self-reported aggregate, i.e. the seed
carried vendor-grade data with an independent tag. Two brief-listed channels
have ToS friction (arena.ai, openrouter.ai).

**Options considered.**
1. *SWE-bench Pro sourcing*: (a) keep "Morph board" as S6; (b) drop the metric
   entirely; (c) split into S13 llm-stats aggregate (kept, honestly V-tagged) +
   S9 Scale SEAL standardized (kept, independent, no target-model coverage yet,
   Meta-ownership conflict flag).
2. *Arena channel*: (a) scrape arena.ai embedded JSON (fresher, ToS-barred);
   (b) official HuggingFace dataset CC-BY-4.0 (1–2d lag, sanctioned).
3. *OpenRouter*: (a) drop the metric; (b) poll the page DOM; (c) one polite
   daily fetch of the two frontend JSON endpoints the page itself loads,
   honest UA, with a stand-down reversal trigger.
4. *Scouted sources*: include/exclude per candidate (Epoch ECI, Vals, LiveBench,
   Scale SEAL general, HLE standalone, HAL).
5. *ARC channel*: (a) DOM; (b) v3.json the frontend loads, daily, honest UA.

**Choices.** 1(c) — the metric survives with honest provenance; the ~20-pt
vendor-vs-standardized gap becomes a first-class integrity signal instead of a
hidden contamination (rejected a: unfetchable, stale, mislabeled; rejected b:
premature — Phase 2 decides row survival with correct tags in hand).
2(b) — constitution rule 12 aside, building a pipeline on a ToS-barred channel
is exactly the silent-rot risk the brief bans; the official dataset is the
same data, licensed (rejected a).
3(c) with RISK-006 — the endpoints are unauthenticated, load-bearing for the
page, and polled once daily with an honest UA; any block or objection flips
the source to "source down (last-good shown)" (rejected a: adoption-momentum
is a standing lens; rejected b: DOM is strictly worse under the same ToS).
4 — INCLUDE Epoch ECI (independent cross-check of the AA index; 5/5 coverage,
CSV/CC-BY); INCLUDE Vals AI (only live independent professional-agentic signal;
funding-disclosure question logged for the gate); INCLUDE LiveBench conditional
on ≥3/5 coverage at collector build; EXCLUDE Scale SEAL as a general source
(Meta ~49% ownership fails independence for a trust-ranked matrix; retained
narrowly as S9 with conflict flag), EXCLUDE standalone HLE (duplicates the AA
fetch), EXCLUDE HAL (paused, 0/5 coverage).
5(b).

**Seed corrections adopted** (regression baseline preserved; corrections land
in the first live snapshot and are classified in BUILDLOG): Fable ARC-AGI-3 →
no official score; Fable SWE-Pro 80.0 (V) not 80.3 (I); Sol SWE-Pro V-tag;
METR Fable = Mythos Preview 17.4h [8.5–55.1]; Arena Kimi 1547 = seed error.

**Reversal conditions.** S13/S9 split reverses if a genuinely independent
SWE-bench Pro board with target-model coverage appears (watch: Scale adds the
five). RISK-006 trigger stands down OpenRouter collection. LiveBench flips
INCLUDE↔HOLD on measured coverage. Arena flips to a faster channel only if
Arena publishes a sanctioned API.

## ADR-003 — Phase 1 gate resolutions: sunset + caveat-flag mechanisms, corrected 2026-08-01 snapshot (2026-08-01)

**Context.** The Phase 1 gate (redteam/phase-1.md) proved the ledger's prose
corrections had no machine teeth: the refuted S6 still fed an I-tagged, chipped
80.3 on the built page, and every independence caveat lived in text no
collector or linter reads.

**Options considered.**
1. *Retiring refuted sources*: (a) reclassify S6 as vendor (breaks the frozen
   seed's lint); (b) rewrite the seed's tags (corrupts the regression
   baseline the brief mandates verbatim); (c) a machine-read `Sunset:` line —
   seed grandfathered, all newer snapshots banned from citing the source.
2. *Caveat visibility*: (a) keep caveats as ledger prose + Phase 4 briefs;
   (b) machine-read `Caveat-flags:` (metric-scopable) that the linter requires
   verbatim on citing cells from 2026-08-01 onward.
3. *When to correct the page*: (a) defer to the first Phase 7 live snapshot;
   (b) build a gate-verified corrected snapshot immediately.

**Choices.** 1(c), 2(b), 3(b). The seed stays byte-honest as history; the
constitution gains two enforcement surfaces (both with negative tests); and
`data/2026-08-01.json` — every value from the gate verifier's live re-fetches —
became `latest.json`, so the page stopped showing a vendor number as the
independent leader today, not at Phase 9. Rejected 1(a)/1(b) as history
rewriting; 2(a) because rule 7 needs something to propagate mechanically;
3(a) because a knowingly-wrong publishable artifact is exactly what the
constitution exists to prevent.

**Also ratified at this gate:** S10 Epoch downgraded A→B with mixed-provenance
caveat; S1 AA independence restated (lab-revenue exposure + Gemini-grader flag
enforced on GDPval/Omniscience cells); S8 TB restated (self-run, log-audited);
RISK-007 closed with cap-table evidence; RISK-008 accepted (adoption
single-source residual, S19 contingency); LiveBench conditional resolved to
INCLUDE (gate-verified 5/5 coverage); delta classifications downgraded where
evidence was thin (cost-per-task driver unresolved; OpenRouter unit-comparability
unresolved; Arena Kimi reclassified category-board conflation).

**Reversal conditions.** Sunset/caveat mechanisms are permanent constitution
machinery; individual caveat flags retire when their factual basis changes
(e.g., AA drops Gemini graders; TB re-executes submissions; Scale divests).

## ADR-004 — Phase 2: the 20-row registry and chip-integrity semantics (2026-08-01)

**Context.** Every row must earn its place against the four daily lenses under
a 22-row cap. Innovator produced three portfolio strategies and per-axis
candidates (governance/innovator/phase-2.md); the gate stress-tested the
selection (governance/redteam/phase-2.md).

**Options considered.** (1) Portfolio shape: consolidated-aggregates (~15 rows,
6 collectors, AA-hostage) vs independent-signal maximalism (~22 rows, sparse,
double the breakage) vs integrity-differentiated (19–20 rows: fully-covered
capability core + rows that expose claimed-vs-verified gaps). (2) LiveBench
ADD vs HOLD. (3) GDPval/Agentic overlap: keep both declared vs fold. (4) Chip
integrity: ignore flags (status quo) vs blunt exclusion (flags kill candidacy)
vs two-part rule (disclaimed values never compete; flagged values compete but
never win; flagged true-leader ⇒ no chip). (5) Derived row 17: X-layer vs
data-row-with-enforced-derivation.

**Choices.** (1) Integrity-differentiated, 20 rows + 3 demotions to the brief
layer (throughput, context-window, deployment-terms — collected, not
matrix-rendered); adds: epoch-eci, aa-agentic-index, swe-rebench, livebench,
aa-halluc-rate, intelligence-per-dollar; upgrades at +0 rows: TB stderr badge,
OpenRouter per-model spend flags. Rejected consolidation (single-aggregator
hostage — the very failure Phase 1 exposed) and maximalism (blows scan budget
on sparse rows). (2) LiveBench ADD — its ≥3/5 condition resolved at 5/5,
gate-verified twice. (3) Keep both with declared overlap (Elo granularity +
composite view); fold order recorded if the cap binds. (4) The two-part rule —
blunt exclusion demonstrably killed a legitimate chip (Opus's verified ARC
record) because a competitor carried a contextual warning; ignoring flags
demonstrably manufactured a LEAD from METR-disclaimed data. `value_disclaimed`
separates "this value is disclaimed" from "this cell carries a warning-worthy
story". (5) Data row with machine-enforced derivation (parents declared,
quotient recomputed, worst-parent staleness, flag inheritance) — arithmetic on
two cited I cells is not editorial; unenforced convention was the hazard.

**Gate resolutions.** 3 BLOCKING + 9 MAJOR + 6 MINOR red-team findings and 3
verifier conditions — all resolved same-day (see redteam/phase-2.md).
INTEGRITY_MARKERS extended (self-report, proxy-model measurement); SWE-rebench
made a third linter-separated scale; S21 (disclosure-watch curated), corrected
S10/S11/S20 entries with pinned Phase 7 extraction specs.

**Reversal conditions.** Row 12 is first out when a HOLD trigger fires (then
fold 3→4, then 17). LiveBench reverts to HOLD if a rotation drops coverage
below 3 columns. Chip semantics revisit only if Phase 3's cold reads show
CO-LEAD/field-footnote confusion. FAR.AI/τ³-pass^k/SEAL enter on their named
triggers.

## ADR-005 — Phase 3: relevance ordering, quick-look, default trio, catalog, chips (2026-08-01)

**Context.** The brief's directive change: relevance-first ordering in the
Apple-compare style, trust carried entirely by per-cell tags/badges. Innovator
produced four materially different orderings with mocks, three quick-look
sets, five trio rules, and catalog/chip/promotion mechanics
(governance/innovator/phase-3.md); the gate cold-read all four and attacked
the two named hazards (governance/redteam/phase-3.md).

**Options and choices.**
1. *Ordering*: A decision-frequency / B volatility / C domain-hybrid /
   D act-audit fold. **C chosen** — stable domain semantics are the only
   property that compounds over months of daily reads; B rejected
   (duplicates the tape, buries METR), A runner-up (ordering rots with the
   reader's focus), D's fold adopted as a rider. Gate-priced honestly: C had
   the WORST day-one cold read (6 breaks) and ships only with the riders
   (pending-row stubs, no-triangulation copy, fold pointing downward);
   reversal condition — if the Phase 6 rendered cold read fails again,
   switch to D.
2. *Vendor-claims placement*: pre-refuted-at-position-9 REJECTED at gate
   (void until Phase 7; paradoxical after). Claims rows live in C7's
   machine-contracted claimed band (`claim_v` ⇒ `data-band="claimed"` +
   VENDOR-CLAIMED label + warn-class markers + SYNC rule). Return to C3 only
   by ADR after a rendered cold read proves the styling.
3. *Quick-look*: QL-A (aa-index, arena-elo, intelligence-per-dollar,
   swe-rebench→gdpval labeled fallback, disclosure count) — the only set
   covering all four lenses with zero V and zero structural blanks; QL-B/C
   rejected (no capability stat / METR blanks in the headline).
4. *Default trio*: rule T2 (top model per vendor, top-3 vendors by best AA) —
   the only rule-neutral AND outcome-clean candidate; cannot produce a
   same-vendor pair, so the first load can never look home-cooked. Riders:
   field-order caption + on-page rule label so hiding the field #2 never
   misstates the order; T4 becomes a labeled "Field state" preset. Today:
   Opus 5 / GPT-5.6 Sol / Kimi K3 (mobile pair cross-vendor). RISK-009 logs
   the AA-scoping reversal trigger.
5. *Catalog*: S2+ (lineage + promotion + field seats), ~13–14 models; Muse
   Spark 1.1 is the promotion rule's first public test (catalog yes on 4
   sources, default no — below the vendor cutoff); DS Flash 0731 stays watch
   (1 source). Conditional seats pinned to a collector-build checkpoint;
   thin columns get coverage badges.
6. *Chips*: field-wide only; CO-LEAD label on ties; provider rows never chip;
   field-#1 footnote = chip-winner-when-off-screen (gate-redefined, B3) with
   a density cap. Trio-relative chips rejected (meaning would change per swap).
7. *Promotion*: M1 event-driven + 3-snapshot hysteresis (launch day bypasses
   via catalog-membership recompute); "group-1 source" pinned as independent
   ledger sources feeding C1–C3 rows.

**Gate.** Verifier countersigned after one condition (Muse Spark premise
corrected from our own fixture); red-team 3 BLOCKING + 5 MAJOR + 5 MINOR all
resolved same-day, three with permanent linter rules + tests (SYNC,
claim-marker, band contract, derived movement-caveat inheritance).

**Reversal conditions.** Ordering C↔D at the Phase 6 rendered cold read;
claims-row C7→C3 per condition 2; T2 scoping per RISK-009; catalog seats at
the collector-build checkpoint.

## ADR-006 — Phases 4+5: briefs and implications as gated, rot-proof prose layers (2026-08-01)

**Decision.** The content layers ship with the same machine discipline as
cells:

1. *Briefs* (data/briefs.json) are curated, repo-grounded prose, linted:
   rule 5 per-sentence over every string, key-sync against the snapshot
   (`_preregistered` allowlist for pre-authored rows), and "begins soon"
   phrasing banned for populated rows. The rendered page's prose gets the
   same per-sentence family scan (block-aware; semicolons/mid-dots split
   enumerations) — authorial discipline is no longer the only defense on any
   surface a reader sees.
2. *Implications* pin `cite_values` at authorship. Any cited-cell drift
   flips the carried implication to visible "under review" (pipeline sets
   it, renderer badges it, linter enforces it from 2026-08-01; seed
   grandfathered). This is the third carry-forward state the innovator
   pre-registered, now mechanical.
3. *Empty-cell cites are legitimate* when the emptiness is the subject
   (withheld/not-evaluated reads). Rule 11 requires cites to RESOLVE, not to
   be populated. The judgment validator stays stricter for machine entries —
   asymmetry is intentional (curated prose is gate-reviewed; machine prose
   is not).
4. *Derived-number policy*: curated implications may state ratios and
   roundings when every operand is a cited cell value; machine entries are
   bound to the lexical no-new-facts scan. Exact deltas preferred (the +112
   became 111.74 under this rule).
5. Gate rewrites: IMP-1 rescoped to its single evaluator with the
   cross-aggregator dissent cited (high→med); IMP-2 reframed to "is the AA
   order the outlier?"; IMP-5 to OPEN with the price-artifact reading named.
   Editorial superlatives across comparability sets are banned in X copy.

**Rejected.** Free-prose briefs (unlintable), implication regeneration by
LLM in the daily loop (mechanical default stands; judgment tier optional),
dropping moved-cite implications silently (the reader must SEE the state).

**Reversal conditions.** Cite→row anchors if the Phase 9 cold read flags
verification friction (RISK-011); X-panel length revisited at Phase 9.

## ADR-007 — Phase 7: autorefresh architecture (2026-08-01)

**Decision.** Single GitHub Actions workflow, cron 12:30 UTC (+13:15
idempotent retry against documented schedule drops), workflow_dispatch,
concurrency-grouped, fetch-depth 1, per-step timeouts.
Order: fetch (11 collectors, honest per-source degradation, env-capped
retries in CI) → optional judgment → data-only constitutional gate → commit
data/ → build → full gate (REQUIRE_HTML=1) → tests → commit docs/. The
docs commit IS the deploy (pairs with ADR-008); the data commit precedes
build/tests so a renderer or UI-test failure can never cost a day of
history; a red run publishes nothing, keeps serving last-good, and uploads
data/ as a forensic artifact. Commit-back doubles as the 60-day
scheduled-workflow heartbeat. Measured growth basis: ~2–6 MB/year realistic
(innovator report) — decades of headroom; artifact-only history is
constitutionally disqualified (90-day retention vs keep-forever).

*Judgment tier*: off by default; activates only on the ANTHROPIC_API_KEY
secret via one Messages-API call (`requests`) — the CLI transport was inert
in CI (innovator D-1). Tamper pin covers prompt + model + max_tokens.
Output survives only if it parses, matches the narrow schema, cites
populated cells, introduces no number absent from cited cells (text AND
falsifier; source-ids scrubbed; abs/negative handled), carries integrity
flags verbatim, invents no flags (subset rule), and never mixes SWE
families. Judged tape supersedes mechanical duplicates. All-or-nothing
implication replacement. Every rejection degrades loudly into the health
footer. Chip-reassignment explainability is inherent: chips derive from
values and every value move is tape/changelog-covered; flag-set changes now
emit changelog entries too.

**Rejected.** 7-B data-only + Actions-Pages deploy (pre-registered reversal,
flips together with 8-B); 7-C split fetch/publish (salvaged its one decisive
advantage — early data commit); 7-D event-driven (structurally unavailable:
no source webhooks; would add standing credentials); 7-E.1 CLI-in-runner
(heaviest dependency for no reason); 7-E.4 mechanical-permanent (declined:
the validator architecture is exactly the containment that makes the tier
acceptable — but it remains the security-maximal option on record).

**Reversal conditions.** RISK-010 (catalog build trigger), RISK-011
(validator limits), RISK-012 (zombie sources), RISK-013 (blanking debounce),
plus innovator riders 6/7/9/10/11 recorded in RISKS.md.

## ADR-008 — Phase 8: publishing via Pages deploy-from-branch /docs (2026-08-01)

**Decision.** GitHub Pages, source "Deploy from a branch", default branch,
folder /docs, with `docs/.nojekyll` (innovator D-2: removes the managed
Jekyll build failure class). URL:
https://brant808.github.io/model-eval-dashboard/ (docs/index.html copy makes
the bare URL resolve). Double last-good: a failed pipeline never pushes, and
a failed managed Pages build keeps serving the previous deployment. Setup is
one keyboard-navigable settings form (HANDOFF); zero recurring cost; page is
30.7 KB gzipped against a 100 GB/month soft cap.

**Rejected.** 8-B Actions-Pages deploy (pre-registered reversal, flips
together with 7-B — never separately); 8-C gh-pages orphan branch
(dominated: legacy workaround, standing force-push); 8-D external hosts
(Cloudflare Pages held as mirror-not-replacement behind an availability
trigger; Netlify disqualified on credit-based free tier — daily deploys
exceed it by construction); 8-E raw/CDN serving (text/plain, unaccountable
third parties).

**Reversal conditions.** Flip 7-B+8-B together on any of: pack size >150 MB,
checkout >60s, branch protection on the serving branch, or a
pages-build-deployment failure/stale-serve not explained by our own push.
Cloudflare mirror on ≥2 Pages incidents intersecting the reader's morning
window in 90 days (RISKS.md).

## ADR-009 — Phase 9: verification close-out (2026-08-01)

**Decision.** The build is DONE to the extent the sandbox can make it so.
Evidence of record: live e2e 11/11 sources with both gates green (after two
loud carry-path catches, fixed); `make all` twice byte-identical; all chaos
drills green in CI through the real fetch path; independent cold read PASS
at ~55s answering moved/trust/meaning from the page alone; EVAL.md
countersigned 7/7, disputed 0/7 — the two stale evidence figures the
countersign was conditioned on are corrected in place (health-footer
coverage 8/15 source ids until first collectors.run; page 31.7 KB gzipped).
No-JS state caveat recorded (all five data columns render; two are
header-unlabeled and the quick-look band is JS-hydrated) — noscript is the
fallback, not the product; noted in HANDOFF.

**Blocked-by-human items (not waivable from here).** RISK-004 push 403 ⇒
branch unpushed, PR unopenable, Pages toggle + live-URL verification + one
dispatched green run pending. HANDOFF §Phase 9 lists them in execution
order; EVAL dimension 7 stays provisional-4 until they land.

**Reversal conditions.** None new — this ADR records outcomes. Standing
reversals live in ADR-005..008 and RISKS.md (001–014).
