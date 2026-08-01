# HANDOFF — Batched Human Actions

Everything that requires the human, in one place, with keyboard steps. Nothing
here blocks the build unless marked BLOCKER. Final consolidated version is
written in Phase 9; items accrue here as phases discover them.

## Pending items

(accruing — see phase sections below)

### From Phase 0

- **No blocked domains.** The connectivity probe (`governance/probe-results.md`,
  2026-08-01) reached all primary source domains through the sandbox proxy:
  artificialanalysis.ai, arena.ai (lmarena.ai redirects there), openrouter.ai,
  arcprize.org, metr.org, morphllm.com, swebench.com — all 200 except
  morphllm.com which returned 429 (rate-limited, reachable; collectors will use
  backoff). No environment network setting needs changing.
