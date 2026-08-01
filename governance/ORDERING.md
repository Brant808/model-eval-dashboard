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
3. **C3 Coding** — swe-rebench, swe-bench-pro (claimed sub-band)
4. **C4 Economics & adoption** — intelligence-per-dollar, cost-per-task, api-price, openrouter-share
   — *subtle fold marker after C4: "daily read ends here" (stolen from Ordering D)*
5. **C5 Knowledge & reliability** — aa-omniscience, aa-halluc-rate, livebench
6. **C6 Headroom** — arc-agi-3, metr-horizon
7. **C7 Integrity & disclosure** — disclosure-watch, swe-bench-verified (claimed sub-band)

Riders (binding, from the innovator's own conditions + ROWS.md obligations):
- **Claim-V quarantine styling is a precondition**: rows 8 and 20(#12 verified)
  render inside a tinted "VENDOR-CLAIMED" sub-band with "claimed" in the row
  name; warn-class ⚠ self-report flags (already linter-enforced). C places
  row 8 at position 9 deliberately — directly under swe-rebench so the claim
  arrives pre-refuted; without the styling C is unsafe and the gate must kill it.
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
Scope: vendors with AA Index coverage (stated scoping; keeps un-indexed
watch models out of the rule).
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
- Every direction-bearing row whose field leader is outside the current
  selection renders a **"field #1: <model> <value> [tag]"** footnote — the
  Phase 6 field-awareness mechanism; rule-10-safe because a V value can never
  win the field-wide computation.

## D5 — Picker catalog: rule S2+ (lineage + promotion + field seats)

Catalog = current five + direct predecessors + distinct-price siblings +
watch-promoted + field seats (best model per major absent vendor iff it meets
the 3-independent-source floor):

- Current: fable-5, opus-5, gpt-5-6-sol, kimi-k3, ds-v4-pro
- Lineage: opus-4-8 (Opus line), sonnet-5 (Anthropic mid line), gpt-5-5
  (OpenAI predecessor), kimi-k2-6 (Moonshot predecessor)
- Price-point siblings: gpt-5-6-terra, gpt-5-6-luna
- Watch-promoted today: **muse-spark-1-1** (Meta — Scale S9 + Arena + TB = 3
  independent sources; the promotion rule's first public test). Enters the
  catalog, NOT the default (no AA index value → outside T2's stated scope).
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
