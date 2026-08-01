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

### From Phase 1 (optional, non-blocking)

- **Optional — Artificial Analysis free API key.** The collector ships on the
  keyless embedded-JSON channel. A free API key (100 req/day) upgrades it to
  the documented, more stable endpoint for index/cost/speed/TTFT. Keyboard
  steps: open https://artificialanalysis.ai/api-key-management-redirect, create
  a free key, then in GitHub: repo → Settings → Secrets and variables →
  Actions → New repository secret, name `AA_API_KEY`, paste, Enter. The
  workflow auto-detects it.
- **Optional — ARC Prize written permission.** We fetch the same leaderboard
  JSON their site loads, once daily. Their ToS has boilerplate anti-datamining
  language; a one-line email to the address on arcprize.org's rate-limits doc
  asking for written OK to poll v3.json daily removes all ambiguity.
