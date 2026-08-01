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
