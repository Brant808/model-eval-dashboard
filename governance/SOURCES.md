# SOURCES — Provenance Ledger

Every `source_id` in any snapshot resolves to an entry here. Entries carry URL,
fetch method, and retrieved-at. The invariant linter (rule 2) parses this file.

Status of this ledger: **seed-stage**. Phase 1 upgrades every entry with live
verification, machine-readable endpoint, ToS/robots posture, freshness SLA, and
a source grade. Until then, `Method: seed` means the value was transcribed from
the approved v2 brief (`governance/BRIEF.md`, Section 1) dated 2026-07-31.

---

### S0 — Approved v2 brief (seed snapshot)
- URL: governance/BRIEF.md
- Method: seed (manual transcription from the approved v2 spec of 2026-07-31)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: n/a (transcription vehicle; underlying provenance carried per-cell via S1–S7)
- Notes: used only for seed cells with no better per-source attribution (disclosure-watch synthesis).

### S1 — Artificial Analysis
- URL: https://artificialanalysis.ai
- Method: seed (live method TBD Phase 1)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: independent third-party evaluator (funding/methodology check in Phase 1)
- Covers: AA Intelligence Index, GDPval-AA, cost per task, throughput/TTFT, AA-Omniscience
- Freshness SLA: provisional 168h (Phase 1 sets final)

### S2 — Arena (text leaderboard)
- URL: https://arena.ai
- Method: seed (live method TBD Phase 1; current domain to be confirmed)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: independent crowdsourced pairwise preference
- Covers: Arena text Elo
- Freshness SLA: provisional 72h

### S3 — OpenRouter rankings
- URL: https://openrouter.ai/rankings
- Method: seed (live method TBD Phase 1)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: independent usage telemetry (marketplace operator; not an evaluator)
- Covers: provider token share
- Freshness SLA: provisional 48h

### S4 — ARC Prize (ARC-AGI-3)
- URL: https://arcprize.org
- Method: seed (live method TBD Phase 1)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: independent nonprofit leaderboard
- Covers: ARC-AGI-3 with effort tiers
- Freshness SLA: provisional 336h

### S5 — METR time horizons
- URL: https://metr.org/time-horizons
- Method: seed (live method TBD Phase 1)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: independent research org
- Covers: 50% task-completion time horizon
- Freshness SLA: provisional 720h

### S6 — Morph-tracked SWE-bench Pro board
- URL: TBD (exact board domain confirmed in Phase 1)
- Method: seed (live method TBD Phase 1)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: independent tracked leaderboard
- Covers: SWE-bench Pro
- Freshness SLA: provisional 336h

### S7 — Vendor disclosures (lab blogs, model cards, pricing pages)
- URL: per-vendor pages (Anthropic, OpenAI, Moonshot, DeepSeek); split into per-vendor entries in Phase 1
- Method: seed (live method TBD Phase 1)
- Retrieved-at: 2026-07-31T00:00:00Z
- Independence: vendor-claimed — every cell citing S7 must be tagged V
- Covers: SWE-bench Verified self-reports, list prices, context windows, deployment terms, launch claims
- Freshness SLA: provisional 336h

### S8 — Terminal-Bench leaderboard
- URL: TBD (confirmed in Phase 1; seed carries no Terminal-Bench values)
- Method: none yet (no seed values)
- Retrieved-at: n/a (no values retrieved)
- Independence: independent academic/community harness (verify in Phase 1)
- Covers: Terminal-Bench 2.1
- Freshness SLA: provisional 336h
