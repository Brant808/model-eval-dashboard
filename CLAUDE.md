# Frontier Model Eval Dashboard — Project Memory

A self-refreshing, single-file HTML dashboard tracking frontier model evals.
Governing document: `governance/BRIEF.md` (read it before non-trivial changes).
This build is governance-first: every phase ends with an adversarial gate.

## Constitutional Data Rules (invariants — `make check` enforces all 12)

1. Every populated cell carries a provenance tag: `I` (independent) or `V` (vendor-claimed).
2. Every populated cell carries a numbered source id resolving to a `governance/SOURCES.md` entry with URL, fetch method, retrieved-at timestamp.
3. Every empty cell carries an explicit reason from the fixed enum: `not published` | `not evaluated` | `settling` | `withheld` | `source down (last-good shown)`.
4. Lead chips only within a declared comparability set; never across mixed sets; shape + label, never color alone.
5. SWE-bench Pro and SWE-bench Verified NEVER appear in the same row, comparison, chip computation, or implication sentence.
6. Every ARC-AGI-3 value carries its effort tier.
7. Integrity flags render as visible warning tags on the cell and propagate into any implication citing that cell.
8. Tape entries are dated, within ~72h of build time, each with a source id.
9. Figures older than their source's freshness SLA render with a staleness badge. Stale never presented as fresh; blanks never silent.
10. Vendor-claimed values never earn a lead chip in competition with independent values.
11. Implications are tagged `X`, cite specific cell ids, carry confidence (high/med/low), and state a falsifier. No editorial claim without cited cells.
12. Published page: public benchmark data + generic analysis only. No personal context, credentials, or private decision framing in repo or page.

The pipeline may not publish a page that violates any rule. Never weaken
`tools/check_invariants.py` to make a build pass; fix the data or the renderer.

## Gate Protocol (every phase)

1. Builder drafts deliverable. 2. Innovator alternatives (design phases 2,3,5,6,7,8).
3. Red-team attacks -> `governance/redteam/phase-N.md` (BLOCKING/MAJOR/MINOR + failure scenario).
4. Verifier reproduces every number/claim. 5. Builder resolves BLOCKING+MAJOR or logs accepted risk in `governance/RISKS.md` with reversal trigger.
6. ADR to `governance/DECISIONS.md`. 7. Self-check vs exit criteria; if green, proceed.

Roles live in `.claude/agents/`: `red-team`, `verifier`, `innovator` (read/run/web only — they never edit source).

## Layout

```
collectors/       one module per source + collectors/fixtures/
data/             dated snapshots; 2026-07-31.seed.json; latest.json (copy)
raw/              cached raw responses (gitignored)
site/             render.py (pure function: data+history -> HTML) + template assets
docs/             built output: model-eval-monitor.html (+ index.html copy) — served by Pages
tests/            pytest: unit, invariant linter tests, e2e dry run
tools/            check_invariants.py (the linter), probe_connectivity.py, helpers
governance/       BRIEF, BUILDLOG, DECISIONS, RISKS, SOURCES, EVAL, RUNBOOK, HANDOFF, redteam/
.claude/          agents/, commands/, settings.json (hooks), hooks/
```

## Commands

- `make fetch`  — collectors -> `data/YYYY-MM-DD.json`, then refresh `data/latest.json` (Phase 0 stub: materialize latest from newest snapshot, no network)
- `make build`  — render `data/latest.json` -> `docs/model-eval-monitor.html` (+ index.html copy)
- `make check`  — invariant linter over all snapshots + built HTML
- `make test`   — pytest
- `make all`    — fetch build check test
- `make publish`— build + check gate for deploy (deploy itself is GitHub Actions)

## Canonical cell schema

```
{ value, unit, tag: "I"|"V", source_id, retrieved_at, effort_tier?, flags: [],
  comparability_set, stale: bool, empty_reason?, history_ref }
```

`value: null` == empty cell -> `empty_reason` required. Populated -> `tag` + `source_id` required.

## Engineering standards

- Renderer is deterministic: no wall-clock reads, no randomness, no network; all
  timestamps come from the snapshot. Two builds from identical data must be byte-identical.
- Every collector has recorded-fixture tests; parse failures must be LOUD (raise), never emit a guessed number.
- Every changed cell between consecutive snapshots must appear in tape or changelog (explainability test).
- Commit at every phase boundary with the ADR number in the message. Push always; the sandbox is ephemeral.
- Keep history snapshots forever.
- Working branch: `claude/frontier-model-eval-dashboard-urlfzc`. Never push elsewhere.
