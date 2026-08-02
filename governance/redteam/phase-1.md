# Red-Team Report — Phase 1 (Research)

Gate run 2026-08-01 (workflow `wf_23a0fe43`): red-team attacked source
independence + machine-readability claims; verifier live-fetched one value from
every collectable source (S1–S5, S8–S14) plus 3 BUILDLOG spot-claims — **all 15
checks MATCH; countersign YES**, with two builder notes (LiveBench 2026-06-25
release covers 5/5 target models → ADR-002 conditional resolves to INCLUDE;
Arena datasets-server filter column is `model_name`, not `model`).

Red-team findings: **1 BLOCKING, 10 MAJOR, 5 MINOR** — key exploits
demonstrated live. Builder resolutions below; all landed same-day.

## BLOCKING

### B1. S6 "neutral" classification let the refuted 80.3 ship I-tagged with a chip; nothing banned future S6 citations
**Resolved (three parts):**
1. New machine-read `Sunset:` ledger line + linter rule: any snapshot dated
   after 2026-07-31 citing S6 (cells or tape) fails. Test:
   `test_gate1_sunset_source_rejected_after_cutoff`.
2. The frozen seed stays grandfathered (its historical encoding is the
   regression baseline the brief demands) — `test_gate1_seed_still_resolves_…`.
3. The substantive fix, per the red-team's own recommendation: built the
   corrected snapshot `data/2026-08-01.json` NOW (every value gate-verified),
   re-sourcing SWE-bench Pro to S13 with V tags. The built page renders
   `swe-bench-pro.fable-5` as `data-tag="V" data-chip="0"` value 80.0, and
   `arc-agi-3.fable-5` as an explicit empty cell. Verified post-build.

## MAJOR (all resolved)

1. **Vals I-tag while RISK-007 open, register premise stale** → RISK-007 CLOSED
   with the gate's cap-table findings (~$5M; Bloomberg Beta/Pear/8VC/J12; no lab
   investors; placement attack failed); S11 now declares machine-read caveat
   flags every Vals cell must carry.
2. **Epoch "no lab funding found" false; ECI not a clean cross-check** → S10
   independence line rewritten (OpenAI-funded FrontierMath component, mixed
   per-row provenance incl. vendor TRs and unsourced rows, METR double-count
   hazard); grade A→B; caveat flag "mixed-provenance composite"; Phase 2
   decides Epoch-run-rows-only computation.
3. **AA lab-revenue exposure understated; Gemini-grader caveat prose-only** →
   S1 independence line rewritten (private benchmarking sold to labs; stated
   leaderboard-separation policy); caveat flag "Gemini-graded (AA judge
   panel)" now machine-enforced on all gdpval-aa and aa-omniscience cells.
4. **Source caveats invisible to the pipeline** → new machine-read
   `Caveat-flags:` ledger line (optionally metric-scoped) + linter rule: cells
   citing a source must carry its declared caveats verbatim (snapshots ≥
   2026-08-01). Declared for S1, S2, S8, S9, S10, S11, S13, S18. Tests:
   `test_gate1_caveat_flags_required_post_baseline`, `…_ledger_parses_new_lines`.
5. **TB "independent" overstates (self-run, log-audited)** → S8 corrected +
   caveat flag "self-run by vendor, log-audited by maintainers" on all S8 cells.
6. **Arena Kimi refutation overclaimed** → rescoped everywhere: overall
   style-control history max 1486.82/best rank 8 (verifier); K3-max ~1542 rank 1
   on the industry_legal_and_government category board Jul 26–30; delta
   reclassified "likely category-board conflation of a real number".
7. **Cost-per-task "+55–79% = real movement" uncited** → downgraded to
   "movement, driver unresolved"; flag carried on the cells and in tape text.
8. **OpenRouter deltas vs unit ambiguity** → downgraded to "movement,
   unit-comparability unresolved"; ambiguity flag on every share cell and in
   the tape entry.
9. **Column rationale internally inconsistent** → rewritten as coverage-density
   + camp representation; proximity argument withdrawn; explicit Phase 2/3
   decision items for Gemini 3.6 Flash, DS Flash 0731, Muse Spark 1.1 (now a
   watch entry at 2+ independent sources).
10. **Adoption lens single-source with a designed kill trigger** → S19
    contingency entry (HF telemetry for open-weights; vendor disclosures) +
    RISK-008 accepting the closed-model residual; RISK-006 amended for
    republication exposure.

## MINOR (all resolved)

- Retrieved-at placeholders → header scoped honestly (S1–S13 probed; S14
  verifier-probed; S15–S17 declared, probe at collector build; date-only
  precision noted).
- RISK-006 republication sentence added; derived-figures-only posture.
- CC-BY attribution lines added to S2 and S10.
- Matrix S1 breakage split (low API / medium embedded for GDPval+Omniscience).
- S4 field names + fraction unit corrected; S5 version-assertion note; S12
  endpoint pinned (`livebench.ai/table_{release}.csv`) and coverage updated to
  gate-verified 5/5.

## Solid (attacks that failed)

ARC claims reproduce exactly (incl. the three $10,000 cap-pinned rows); Arena
HF channel + CC-BY-4.0 license verified; the 80.3→Mythos-5 misattribution
traces verbatim to the live llm-stats payload; llm-stats vendor classification
correct (0/43 verified); METR/Epoch/OpenRouter endpoints live as described;
Vals pay-for-placement attack failed; AA embedded fallback confirmed; repo left
clean by both agents.
