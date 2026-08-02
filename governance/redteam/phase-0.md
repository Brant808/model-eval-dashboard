# Red-Team Report — Phase 0 (Harness)

Gate run 2026-08-01, red-team + verifier subagents (transcripts under the
session workflow `wf_598173d3`). Verifier countersigned Phase 0 **YES,
unconditional** — 31/31 checks MATCH (seed fidelity to the brief, pipeline
determinism, hook behavior, probe reproduction, render contract).

Red-team findings: **1 BLOCKING, 8 MAJOR, 4 MINOR** — every one demonstrated
with a working exploit, not speculated. Builder resolution below each.
All BLOCKING and MAJOR objections were **fixed in code** the same day and each
fix carries a permanent regression test (`tests/test_invariants.py` /
`tests/test_render.py`, `test_gate_*`). Post-fix: linter green, 53/53 tests.

---

## BLOCKING

### B1. Rule 10 rested entirely on the honesty of the tag
A vendor value retagged `I` (while still citing vendor source S7) won the LEAD
chip and every check stayed green — the exact lie rule 10 exists to prevent.
**Fix:** `SOURCES.md` `Independence:` lines are now machine-read; a cell citing
a vendor-classified source with tag `I` is a RULE10 violation.
Test: `test_gate_vendor_source_masquerading_as_I_caught`. **RESOLVED.**

## MAJOR

### M1. Infinity/NaN passed every check; Inf chipped, NaN silently deleted a row's chip
**Fix:** strict JSON parse (`parse_constant` raises) in linter and renderer;
non-finite populated values are SCHEMA violations; `compute_chips` only
considers finite numerics. Tests: `test_gate_nonfinite_values_caught`,
`test_gate_strict_json_rejects_infinity`. **RESOLVED.**

### M2. Rule 5 unenforced for tape cell_ids and sentence text
**Fix:** tape entries citing both families, and tape/implication TEXT naming
both "SWE-bench Pro" and "SWE-bench Verified", are RULE5 violations.
Tests: `test_gate_tape_mixing_*`, `test_gate_*_text_comparing_families_caught`.
**RESOLVED.**

### M3. Deleting `freshness_sla_hours` silently disabled rule 9
**Fix:** every metric must declare a positive finite SLA or it is itself a
RULE9 violation. Test: `test_gate_missing_sla_is_a_violation`. **RESOLVED.**

### M4. check_html forgeable (quote style, duplicate ids, fabricated cells, wrong value text)
**Fix:** rewritten on `html.parser` (quote-agnostic); duplicate rendered cell
ids and cell ids absent from the snapshot are violations; displayed text must
contain the snapshot value; chip glyph/label counted inside the parsed cell,
and chip visuals inside a non-chip cell are "visual forgery" violations.
Tests: `test_gate_single_quoted_chip_forgery_caught`,
`test_gate_duplicate_cell_id_caught`, `test_gate_fabricated_cell_caught`,
`test_gate_wrong_displayed_value_caught`, `test_gate_orphan_lead_visual_caught`.
**RESOLVED.**

### M5. Hook guarded neither the linter, data, Makefile, SOURCES.md, nor its own config
**Fix:** hook path filter extended to `tools/`, `data/`, `Makefile`,
`governance/SOURCES.md`, `.claude/settings.json`, `.claude/hooks/`.
Bash-tool writes still bypass PostToolUse hooks by design — accepted as
RISK-005 (CI runs identical checks on every push and is the authority).
**RESOLVED (residual accepted as RISK-005).**

### M6. No wall-clock check: a rotted pipeline republishes old latest.json as fresh forever
**Fix:** full-run mode fails when `latest.json` `generated_at` exceeds 54h
(`ROT` violation) unless `CHECK_ALLOW_OLD_LATEST=1` (deliberate offline
replays, documented for RUNBOOK). Test: `test_gate_latest_rot_guard`.
**RESOLVED.**

### M7. Explainability missed removals (and unexplained appearances)
**Fix:** the check iterates the union of old and new cells; removed and
newly-appearing cells must be explained in tape or changelog.
Test: `test_gate_explainability_catches_removals_and_appearances`. **RESOLVED.**

### M8. A lone numeric among text values won an uncontested LEAD chip
**Fix:** chips require ≥2 eligible competitors; a direction-bearing metric
mixing numeric and text values is a RULE4 violation. Tests:
`test_gate_single_candidate_never_chips`, `test_gate_mixed_numeric_text_metric_caught`.
**RESOLVED** (visible effect: arena-elo's single-value chip is gone from the page).

## MINOR

### m1. Hygiene bypasses (filename-based exemption, split/encoded emails, case-sensitive name ban)
**Fix:** exemption is by exact path `tools/check_invariants.py` only; repo scan
also runs on whitespace-collapsed text; page scan runs on entity-decoded,
whitespace-collapsed text; name ban is case-insensitive.
Test: `test_gate_lowercase_name_and_encoded_email_caught`. **RESOLVED.**

### m2. Malformed snapshot crashed the linter instead of reporting a violation
**Fix:** `lint_snapshot` wrapper converts parse errors into SCHEMA violations
and continues; malformed tape dates are RULE8 violations.
Test: `test_gate_malformed_snapshot_is_violation_not_crash`. **RESOLVED.**

### m3. Tape entries dated tomorrow passed (26h future slack)
**Fix:** tape dates after `snapshot_date` are RULE8 violations.
Test: `test_gate_future_tape_entry_caught`. **RESOLVED.**

### m4. `make -j publish` raced build/check; missing HTML silently skipped checks
**Fix:** `publish` uses serialized recursive `$(MAKE) build` then
`REQUIRE_HTML=1 $(MAKE) check`; with `REQUIRE_HTML=1` a missing page is a hard
violation; otherwise absence prints a stderr notice instead of silence.
**RESOLVED.**

## Solid (attacks that failed against the Phase 0 harness as shipped)

- Tape citing nonexistent cells; future-dated (+2d) tape; implications citing
  unknown cells; cells referencing undeclared models — all caught.
- Straightforward chip forgery (double-quoted) caught by RULE10 + RULE4.
- Off-enum empty reasons caught (blanks never silent).
- Invalid JSON in any data file is a SCHEMA violation; serial `make publish`
  cannot ship from a corrupt latest.json.
- Hook genuinely fires and runs `make check && make test` for guarded paths.
- Renderer determinism holds under `PYTHONHASHSEED=random` (subprocess test).
- Red-team left the working tree clean (verified via `git status --porcelain`).
