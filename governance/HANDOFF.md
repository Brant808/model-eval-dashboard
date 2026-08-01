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

### From Phase 7

- **BLOCKER — grant push access (RISK-004).** Every `git push` from this
  session returns 403 at the relay, and the GitHub API refuses writes
  ("Resource not accessible by integration"). All work is committed locally
  on `claude/frontier-model-eval-dashboard-urlfzc`. Keyboard steps to fix:
  open https://github.com/settings/installations, Tab to the Claude GitHub
  App, Enter → Configure, grant **Read and write** access to
  `Brant808/model-eval-dashboard` (repository contents + pull requests),
  Save. Then re-run the session's push, or from any clone with your own
  credentials: `git push -u origin claude/frontier-model-eval-dashboard-urlfzc`.
- **Optional — judgment layer key.** The page ships in mechanical-tape mode
  by default (designed). To turn on the validated `claude -p` judgment tier:
  repo → Settings → Secrets and variables → Actions → New repository secret,
  name `ANTHROPIC_API_KEY`, paste a key, Enter. The workflow detects it; the
  health footer will say which mode produced each page. Delete the secret to
  turn it back off. Never commit the key anywhere.
- **After merge — first scheduled run.** The `daily-refresh` workflow only
  fires on the default branch. After merging the PR: repo → Actions →
  `daily-refresh` → Run workflow → Enter, and check the run goes green and
  commits back `data/<today>.json` + rebuilt `docs/`.

### From Phase 8

- **Turn on GitHub Pages (one-time, ~30s).** Repo → Settings → Pages
  (left sidebar; on small screens press `.` to open github.dev is NOT needed —
  the Pages form is plain HTML, fully keyboard-reachable). Under
  "Build and deployment": Source = **Deploy from a branch**; Branch = the
  default branch, folder = **/docs**; Save (Tab to Save, Enter). Within ~2
  minutes the page serves at
  https://brant808.github.io/model-eval-dashboard/ — bookmark it.
- **iPhone home-screen icon.** Open the URL in Safari → Share →
  "Add to Home Screen" → Add. The page is self-contained and renders its
  last-fetched state offline once cached.

### Phase 9 consolidation — do these in order

1. **BLOCKER — grant push access** (details in the Phase 7 section above).
   Until then the branch exists only in the (ephemeral) sandbox.
2. **Merge the PR** (or push + open it if the session could not — see the
   final summary). Review gate: `make all` green locally is pre-verified.
3. **Turn on Pages** (Phase 8 section above: Settings → Pages → Deploy from
   a branch → default branch → /docs → Save).
4. **Dispatch the first run**: Actions → daily-refresh → Run workflow →
   Enter. Verify: run green; a `data/<today>.json` commit and (if anything
   changed) a docs/ commit appear; the page at
   https://brant808.github.io/model-eval-dashboard/ shows today's
   generated_at in the health footer. This also confirms the managed Pages
   build ran (first-deploy verification — a gate rider asked for explicit
   confirmation once).
5. **Optional**: `ANTHROPIC_API_KEY` secret for the judgment tier (Phase 7
   section); `AA_API_KEY` (Phase 1 section); ARC permission email (Phase 1
   section).
6. **iPhone**: open the URL in Safari → Share → Add to Home Screen → Add.
   (Recorded honestly: this one step is a touch gesture; every Mac/GitHub
   step above is keyboard-only. CLI alternative for step 3:
   `gh api -X POST repos/Brant808/model-eval-dashboard/pages -f build_type=legacy -f 'source[branch]=main' -f 'source[path]=/docs'`.)
