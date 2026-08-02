# ORDERING — Phase 3 Decisions (builder selection pending gate)

Inputs: `governance/innovator/phase-3.md` (4 orderings with mocks, 3 quick-look
sets, 5 trio rules, 2+1 catalog rules, chip/promotion mechanics),
`governance/ROWS.md` (20 rows, quarantine obligations), the brief's Phase 3
directive (relevance-first; trust rides on tags) and its two named hazards.

## D1 — Ordering: C, "Capability-Domain Hybrid" (with riders)

Stable domain sections (Apple-faithful: semantics never move), domains ordered
by decision frequency; within a domain: independent composite → judged/event
boards → claimed.

1. **C1 Overall intelligence** — aa-index, epoch-eci, arena-elo
2. **C2 Agentic & real-economy work** — gdpval-aa, aa-agentic-index, vals-index, terminal-bench
3. **C3 Coding** — swe-rebench (alone until its collector lands; renders as a one-line stub meanwhile)
4. **C4 Economics & adoption** — intelligence-per-dollar, cost-per-task, api-price, openrouter-share
   — *subtle fold marker after C4: "daily read ends here" (stolen from Ordering D)*
5. **C5 Knowledge & reliability** — aa-omniscience, aa-halluc-rate, livebench
6. **C6 Headroom** — arc-agi-3, metr-horizon
7. **C7 Integrity & disclosure** — disclosure-watch, swe-bench-pro (claimed sub-band), swe-bench-verified (claimed sub-band)

Riders (binding, from the innovator's own conditions + ROWS.md obligations):
- **Claim-V quarantine (gate-hardened, BLOCKING-2 resolution)**: the
  vendor-claims rows (swe-bench-pro, swe-bench-verified) live in C7's claimed
  sub-band — BELOW the fold — not in C3. The earlier position-9
  "arrives pre-refuted" rationale was struck at the gate: it was void until
  SWE-rebench has cells and relied on an unstated cross-scale comparison the
  page itself bans. Reversal condition: after Phase 7 populates swe-rebench
  AND a rendered cold read demonstrates the sub-band styling carries the
  weight, the claims row may move to C3 by ADR. The band is now a machine
  contract: metrics with `claim_v: true` must render `data-band="claimed"` +
  visible VENDOR-CLAIMED label (linter/HTML-tested), every claim cell carries
  a warn-class self-report marker (linter rule, snapshots ≥ 2026-08-01), and
  latest.json must be byte-identical to the newest dated snapshot (SYNC rule)
  so corrections can never lag onto the page.
- **Authority-V vs claim-V**: api-price keeps the plain V badge (first-party
  fact); only claim-V rows get quarantine treatment. Rule 1's binary tag is
  untouched — this is styling weight.
- **Field-#1 footnote** (D4 below) carries C's scattered-movers cost.
- Fallback pre-approved: if the gate's cold read shows 7 headers costing >~5s,
  collapse C5+C6 into "Knowledge & headroom" (6 groups) before abandoning C.

Rejected: A (decision-frequency — safest but ordering rots when the reader's
focus shifts; groups mix domains so wayfinding is weaker), B (volatility —
duplicates the tape's job and buries METR at 18), D (act/audit — best speed,
but brittle single-person triage and furthest from the named Apple reference;
its fold survives as a rider).

## D2 — Quick-look set: QL-A ("four lenses, five stats")

`aa-index` · `arena-elo` · `intelligence-per-dollar` · `swe-rebench` ·
`disclosure-watch count`. Zero V cells, zero structurally-empty cells for
current columns (Kimi's swe-rebench "not evaluated" is itself signal).
Until the swe-rebench collector lands (Phase 7), the band substitutes
`gdpval-aa` in that slot (declared fallback, not silent).
Rejected: QL-B (no capability stat in the band; flagged cost number in the
headline), QL-C (metr in the band = two blanks + the page's most-flagged
number up top).

## D3 — Default trio rule: T2 — top model per vendor, top-3 vendors by their best model's AA Index

Today: **Claude Opus 5 / GPT-5.6 Sol / Kimi K3**, slots ordered by AA Index
(mobile 2-up shows Opus + Sol — cross-vendor even at iPhone width).
Scope: vendors with AA Index coverage (stated scoping). Gate note: this
scope excludes almost nobody in practice (even watch-promoted Muse Spark is
AA-indexed at 50.62) — the operative filter is the top-3-vendor cutoff, which
is the point: rule-driven, outcome-blind.
Why the RULE, not the trio: it is the only candidate that is both rule-neutral
and outcome-clean — it cannot produce a same-vendor pair by construction, so
no data drift can ever make the first load look like home cooking (hazard H2:
the reader needs the unvarnished view; today's alternatives T1/T3 would open
with two Anthropic columns). Cost accepted: the actual AA #2 (Fable 5) is not
in the default — it remains one keystroke away, appears in field-#1 footnotes
and tape, and the default only governs the first-ever load (URL-hash +
localStorage persistence wins thereafter). T4 ("field state": leader + value
frontier + mover) is adopted as a labeled secondary preset in the picker, not
the default (its mover input is currently a driver-unresolved number).

## D4 — Chips: field-wide only; CO-LEAD on ties; field-#1 footnotes

- Chips remain FIELD-WIDE (linter and page share one truth; a chip means
  "best in the tracked field"). Trio-relative chips rejected: they would crown
  mid-field models and change meaning on every swap.
- Ties: all tied leaders chip, rendered **CO-LEAD** (same glyph, distinct
  label — shape+label per rule 4).
- Provider-level rows never chip (`chip_eligible: false`, ADR-004).
- **Field-#1 footnote (gate-redefined, BLOCKING-3 resolution)**: a footnote
  renders ONLY for the current CHIP-WINNER when it is off-screen — full
  compute_chips eligibility applies (I-only, non-disclaimed, non-stale, ≥2
  competitors, flagged-leader ⇒ nothing, chip_eligible respected; warn flags
  travel with the footnote). Rows with no legitimate chip get NO footnote —
  the footnote may never recreate a superlative the chip contract refuses
  (as specced before the gate it would have crowned disclaimed/single-
  candidate/all-V/provider-level "leaders", four of five naming the home
  model). Density cap: if >4 footnotes would render in one screenful, Phase 6
  collapses them into the group header. Encoded as a Phase 6 test.

## D5 — Picker catalog: rule S2+ (lineage + promotion + field seats)

Catalog = current five + direct predecessors + distinct-price siblings +
watch-promoted + field seats (best model per major absent vendor iff it meets
the 3-independent-source floor):

- Current: fable-5, opus-5, gpt-5-6-sol, kimi-k3, ds-v4-pro
- Lineage: opus-4-8 (Opus line), sonnet-5 (Anthropic mid line), gpt-5-5
  (OpenAI predecessor), kimi-k2-6 (Moonshot predecessor)
- Price-point siblings: gpt-5-6-terra, gpt-5-6-luna
- Watch-promoted today: **muse-spark-1-1** (Meta — AA S1 (index 50.62, not
  estimated, per the recorded fixture) + Scale S9 + Arena S2 + TB S8 = 4
  independent sources; the promotion rule's first public test). Enters the
  catalog, NOT the default: Meta is IN T2's scope, but its best AA (50.62)
  ranks below the #3 vendor cutoff (Moonshot/Kimi 57.11). (Gate-corrected —
  the earlier 'no AA index' premise was refuted by our own S1 fixture.)
- Field seats (conditional on the 3-source floor at collector build):
  grok-4-5 (AA + Arena + SWE-rebench + TB — expected pass), gemini-3-6-flash
  (AA + ? — verify; this is how "Google absence-as-signal" becomes a visible,
  comparable fact instead of a silent hole).
- Stays watch (not catalog): ds-v4-flash-0731 (1 independent source),
  mythos-preview (METR only), qwen3-8-max (unreleased), gemini-3-5-pro
  (unreleased).

Picker grouping mirrors Apple: "Current frontier" / "Recent & superseded"
(+ "Added <date>" divider on promotion day). DS-line predecessor omitted
(V3.2-era coverage too thin to render honestly) — recorded as the rule's
first scoping judgment.

## D6 — Promotion mechanics: M1 (event-driven + hysteresis)

Operational pin (gate): a **"group-1 source"** for the promotion floor is an
independent-classified ledger source feeding a CAPABILITY-domain matrix row
(groups C1–C3): S1, S2, S10, S11, S8, S20, S12. Vendor sources and S9 (no
matrix row) never count. Muse Spark passes on S1+S2+S8 (3); DS V4 Flash 0731
has S1 only (1) and stays watch.

- Watch → catalog at ≥2 independent group-1 sources (brief). On promotion:
  picker entry under an "Added <date>" divider + movement dot, tape entry with
  source id, page addition note; all 20 rows materialize as cells or
  reasoned empties in the same snapshot (Phase 7 adds the linter rule: no
  catalog model without a full column).
- Chip reassignments caused by catalog membership changes must appear in
  tape/changelog (extends explainability; Phase 7).
- Default trio recomputes only when catalog membership changes or the T2
  output differs for 3 consecutive snapshots (kills decimal-jitter churn).
  User selection (URL hash / localStorage) always wins; promotion never edits
  slots.
- Retirement: superseded models move to the "older" picker group; cells
  persist forever; staleness (existing non-stale chip condition) retires them
  from chip eligibility automatically.


## Gate riders (Phase 3 red-team, binding on Phases 4–6)

- **Field-order caption**: the quick-look headline stat carries a one-line
  field order ("field: 1 Opus 60.69 · 2 Fable 59.86 · 3 Sol 58.89 …") and the
  picker states the default rule ("default: top model per vendor") — the
  default view must never misstate field order in either direction (T2
  otherwise hides the field #2 entirely).
- **QL fallback labeling**: until SWE-rebench lands, the band's coding slot is
  visibly labeled ("coding slot: GDPval until SWE-rebench tracking begins");
  derived band values inherit parents' movement caveats (linter-enforced).
- **Pending rows render as one-line stubs** at group bottom ("tracking begins
  soon"), never as full empty rows; no "methodologies agree" copy until Epoch
  is populated (and Arena's disagreement is stated when present).
- **Fold copy**: "below: slow boards and claims — the tape flags any change"
  (points downward, never asserts completeness); marker suppressed/restyled on
  builds where a C5–C7 cell changed.
- **Two-weight V legend**: api-price carries a "vendor-listed fact" caption;
  the legend explains both V weights in two lines.
- **Picker coverage badges**: thin catalog columns show "early coverage:
  N of 20 rows"; catalog conditional seats (grok-4-5, gemini-3-6-flash) and
  the kimi-k2-6 lineage seat are pinned at a named collector-build checkpoint.
- **Jargon copy pass**: no internal governance vocabulary in reader-facing
  copy ("collector lands Phase 7" → "tracking begins soon", etc.).
