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
