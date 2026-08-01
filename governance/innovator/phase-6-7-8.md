# Innovator report — Decisions 6, 7, 8 (ratification pressure + pre-registered reversals)

Written to stand alone for consumption into ADR-006/007/008. Inputs read: `/home/user/model-eval-dashboard/governance/BRIEF.md` (Phases 6–8), `/home/user/model-eval-dashboard/site/render.py`, `/home/user/model-eval-dashboard/docs/model-eval-monitor.html` (154,199 bytes; 30.7 KB gzipped), `/home/user/model-eval-dashboard/.github/workflows/daily.yml`, `/home/user/model-eval-dashboard/tools/judgment.py`, `/home/user/model-eval-dashboard/governance/{DECISIONS,ORDERING,RISKS,BUILDLOG}.md`, `/home/user/model-eval-dashboard/data/latest.json`. GitHub-behavior claims are grounded against current GitHub docs (links in "Grounding notes" at the end).

Two defects discovered while preparing alternatives are flagged inline because they bear on ratification: **(D-1)** the shipped judgment-layer upgrade path is dead on arrival in CI, and **(D-2)** `docs/.nojekyll` is missing for the branch-deploy candidate. Details under Decisions 7 and 8.

---

## Decision 6 — Compare paradigm

Shipped (per `site/render.py` and the Phase 6 commit `a1f1180`): Apple-compare with three picker slots (2-up at iPhone width), all catalog columns statically rendered with JS doing only visibility flips, sticky compare header, QL-A quick-look band, groups C1–C7 with a fold after C4, field-wide chips + field-#1 footnotes, global tape, slide-over briefs, full keyboard nav, URL-hash + localStorage persistence.

The five options below differ in **information hierarchy and interaction model**, not styling. All must preserve the constitution (tags, chips, quarantine bands, tape, empty reasons) — none of these options relaxes a data rule.

### 6-A (shipped) — Apple-compare: state-first, trio-scoped, picker-swapped

**Sketch.** The page's primary object is the *current state of three chosen models*, read top-to-bottom through relevance-ordered groups. Field awareness is delegated to three secondary devices: the global tape, movement dots on picker entries, and chip-winner-off-screen footnotes. All columns render statically; JS flips `display` per column class, so swaps are <100ms with no layout shift and the no-JS/`file://` fallback shows the full matrix.

**Strongest FOR.** It matches how the daily question is actually asked: "how do the models I care about stand against each other today?" — and the persistence mechanics mean day two opens exactly where day one ended. It is also the brief's named reference pattern, already gate-hardened (T2 default trio, CO-LEAD, footnote density cap).

**Strongest AGAINST.** It is state-first on a page whose stated first question is *"what moved in the last 72 hours"* — movement is served by a text strip at the top rather than by the page's primary structure, and a move in a non-selected model is only discoverable via tape/dot/footnote indirection. Three devices doing one job (field awareness) is a smell.

**60-second scan.** Strong for trio-state; adequate for field-movement (tape read costs ~10–15s of the budget; dot/footnote scanning is incidental). Scales linearly in page weight with catalog size (5 columns = 154 KB; ~13–14 catalog models projects to roughly 300–400 KB raw, still far under the 1.5 MB cap).

**Adoption trigger (to keep it).** Phase 6's rendered cold read passes: what-moved answered in <60s even when the mover is off-trio. That test is already in the gate suite.

### 6-B — Change-first briefing ("inverted pyramid")

**Sketch.** Invert the hierarchy: the page leads with a *delta panel* — yesterday-to-today changes rendered as first-class rows (cell id, old → new, delta chip, tag, source, flag), grouped by lens, followed by the X-layer read, and only then the compare matrix, collapsed to the quick-look band by default with a keyboard toggle (`m`) to expand the full trio matrix. The tape stops being a strip and becomes the page's skeleton; unchanged state is one keystroke away instead of always-on. Everything below the delta panel is identical to 6-A (same renderer components, reordered and one `<details>` wrapper added).

**Strongest FOR.** It makes the page answer its three questions in their stated order — moved / trust / meaning — with zero scanning of unchanged cells; on a quiet day the entire read is 15 seconds ("nothing moved, judgment layer off, sources ok"). The explainability invariant (every changed cell in tape/changelog) already produces exactly the data this layout needs; the renderer would be *presenting* an artifact the constitution already forces it to compute.

**Strongest AGAINST.** Change-blindness to slow rot: a model that drifts one place per week never headlines, and the reader loses the ambient re-anchoring that a daily pass over full state provides. Also, on high-churn days (methodology refits touch 20 cells) the delta panel is *worse* than a matrix — 45 changelog entries read slower than 20 rows scanned columnwise (today's snapshot has 45 changelog entries; this is not hypothetical).

**60-second scan.** Best-in-class on quiet and normal days; degrades on refit days unless the panel collapses same-source mass-changes into one line ("S1 refit moved 5 AA cells: …"), which is a required sub-feature, not an option.

**Adoption trigger.** The Phase 6/9 cold read fails on "what moved" while passing on trio-state; or the reader is observed skipping the matrix (only reading tape + quick look) on most mornings. Partial adoption is cheap: promote the delta panel above quick-look without demoting the matrix.

### 6-C — Full-field matrix (v2 lineage): everything visible, nothing swapped

**Sketch.** Drop pickers and trio scoping. One dense grid, all catalog models × 20 rows, sticky header and sticky first column, horizontal scroll on mobile with snap-to-column; column order = field order (AA Index) so position itself encodes rank; the tape shrinks to a two-line ticker because the field is *on screen*. Compare is done by eye across adjacent columns, aided by a keyboard "pin" (press `p` on a column to freeze it at the left edge).

**Strongest FOR.** Zero indirection: field awareness is not a feature bolted onto a trio view — it *is* the view, and the three devices 6-A needs (dots, footnotes, field-order caption) all become unnecessary, deleting the very complexity the Phase 3 gate spent three BLOCKING findings taming (footnote superlatives, hidden field #2, caption riders).

**Strongest AGAINST.** It dies on the phone, which is half the stated use: 13–14 columns at 390px means either illegible type or heavy horizontal scrolling, and Apple's own compare page exists precisely because dense grids fail mobile. The 60-second budget gets spent on navigation instead of comprehension.

**60-second scan.** Excellent on a wide desktop monitor; fails at iPhone width. Also raises chip/flag visual density to the point where the load-bearing I/V/warn tags (which Phase 3 made carry all trust semantics) compete with 14 columns of ink.

**Adoption trigger.** Only if the reader's device mix changes to desktop-dominant AND the catalog stays ≤8 models. Not otherwise competitive; its honest role is as the no-JS fallback — which 6-A already ships for free (static all-columns render).

### 6-D — Per-metric leaderboard cards (small multiples)

**Sketch.** No model columns at all. Each metric renders as a compact card: metric name, then the ranked field as a horizontal strip — leader first with chip, each entry `name · value · tag`, flagged/stale entries visibly marked, claimed metrics rendered as quarantined cards in a C7 band. Cards sit in the same C1–C7 group order with the same fold; a model filter (`/`) highlights one model's position across every card, replacing the trio concept with "trace my model through the field." Briefs, tape, X-layer unchanged.

**Strongest FOR.** It is the native shape of the underlying data — every metric *is* a leaderboard — so "who leads, by how much, over whom" needs no chips-plus-footnotes machinery: rank is position. Cross-model gaps (the actual frontier-race question) are visible per metric in a way three fixed columns never show, and a new catalog model costs one entry per strip, not a column that stresses layout.

**Strongest AGAINST.** It destroys the model-profile read: "how does Opus 5 look overall" requires visually chasing one name through 20 strips, which is precisely the job columns do for free. It is also the furthest from the reader's named best-in-class reference, and comparability-set discipline gets harder to *see* (a strip mixing two comparability sets must split visually, where a table row carries `data-row-set` naturally).

**60-second scan.** Excellent for "state of the race per metric"; poor for "state of a model." Since the reader's daily anchor per the brief is model-vs-model, this trades the primary read to improve the secondary one.

**Adoption trigger.** The catalog grows past ~10 models with real coverage (columns stop scaling) AND observed usage shows metric-centric questions dominating (reader keeps asking "who leads X," rarely "show me model Y"). Also viable as an *overflow view* behind one keystroke (`f` for "field view") rather than a replacement — that variant survives the "does it slow the scan" objection because it costs nothing until invoked.

### 6-E — Trend-first monitor (point-on-trend cells)

**Sketch.** Keep 6-A's exact trio/picker/group skeleton, but change what a cell *is*: each populated cell renders a 30-day inline sparkline with the current value as the terminal point, delta-since-yesterday as slope emphasis, staleness as a flatlined gray tail. The sparklines currently buried in briefs (`spark_svg` in `/home/user/model-eval-dashboard/site/render.py`) become the matrix's primary ink; today's number is annotation on a trajectory. Tape and quick look unchanged.

**Strongest FOR.** The dashboard's real subject is *movement*, and trend-in-cell answers "what moved AND does it matter" in one glance — a 0.8-point AA drift reads as noise on a flat line, a genuine regime change reads as a knee; no other option encodes significance-of-change visually.

**Strongest AGAINST.** It is premature by construction: there are two snapshots of history (seed + 2026-08-01), so every sparkline is a two-point line for weeks — the page would lead with its weakest asset. It also roughly doubles cell rendering complexity and SVG weight, and the trust tags/flags that Phase 3 made load-bearing must now compete with a chart in every cell.

**60-second scan.** Once ≥3 weeks of history accrue: potentially the fastest "what moved and does it matter" read of all five. Today: strictly worse than 6-A.

**Adoption trigger.** Calendar + evidence: ≥21 daily snapshots accrued AND the reader is observed opening briefs mainly for sparklines. Cheap partial adoption: sparklines in quick-look band only (5 metrics × 3 models = 15 small SVGs, ~10 KB).

### Comparison

| | Primary read | Field awareness | Mobile (390px) | Movement salience | Weight/scaling | Distance from shipped |
|---|---|---|---|---|---|---|
| **6-A shipped** | trio state | indirect (tape+dots+footnotes) | good (2-up) | medium | linear in catalog, fine | — |
| **6-B change-first** | deltas | direct (deltas are global) | good | best (quiet days), worst (refit days, needs collapsing) | same as A | small (reorder + collapse) |
| **6-C full field** | field state | native | fails | medium | poor past ~8 models | medium (delete pickers) |
| **6-D metric cards** | race per metric | native | good | medium | best scaling | large (new renderer core) |
| **6-E trend-first** | trajectories | indirect (as A) | okay | best (after history accrues) | heavier cells | medium (cell renderer) |

**Ranked recommendation.** (1) **Ratify 6-A**, it is genuinely the right skeleton for a model-vs-model daily anchor and is the only option already gate-hardened; (2) pre-register **6-B as the named reversal** if the cold read fails on "what moved" — it is the cheapest materially-different fallback and shares 90% of the renderer; (3) adopt **6-E's quick-look-band-only variant on the 21-snapshot trigger** (it upgrades A without changing its IA); (4) hold **6-D as the overflow "field view"** candidate the brief explicitly invites, judged then against the 60-second objection; (5) reject 6-C except as the no-JS fallback A already provides.

---

## Decision 7 — Refresh architecture

Shipped (`/home/user/model-eval-dashboard/.github/workflows/daily.yml`): single workflow, cron `30 12 * * *` + `workflow_dispatch`, concurrency group `daily-refresh` (no cancel), per-step timeouts, fetch → optional judgment → build → `REQUIRE_HTML=1 make check` → tests → commit `data/ docs/` back to the serving branch with rebase-retry push. Commit-back **is** the deploy under the Phase 8 branch-deploy candidate; a failed gate publishes nothing.

**Flagged defect D-1 (bears on ratification of the shipped judgment placement).** `tools/judgment.py:213` degrades when `shutil.which("claude") is None`, and `daily.yml` installs only `pip install -r requirements.txt` — the Claude Code CLI is never installed in the runner. Consequence: even after the human adds `ANTHROPIC_API_KEY`, every CI run will degrade with "claude CLI not installed." The advertised secret-detect-and-upgrade path cannot ever activate as shipped. This is fixable inside any of the options below (install the CLI via npm in the workflow, or re-point `run_model()` at the Messages API over `requests`, which is already a dependency), but the ADR must not describe the shipped path as working.

### The history-growth question, answered concretely first

Measured today: snapshot 71,179 B (11.6 KB zlib-compressed), built page 154,199 B (30.7 KB gzipped); `docs/index.html` is a byte-identical copy, so git stores **one** blob for both. Worst case (git stores whole compressed blobs daily, no deltification): ~42 KB/day ≈ **15 MB/year**. Realistic case (git packs day-over-day deltas; the diff between consecutive pages/snapshots is dozens of lines): **~2–6 MB/year for data + docs combined**. Against GitHub's 1 GB recommended repo size and 1 GB Pages site cap, the shipped design has **decades** of headroom; catalog growth to 14 columns roughly doubles the daily delta, still decades. The genuine costs of commit-back history are not storage: they are (a) CI checkout time — `daily.yml` uses `fetch-depth: 0`, a full-history clone that grows forever, and is unnecessary: sparkline history comes from `data/*.json` in the working tree at HEAD, not from git history, so `fetch-depth: 1` suffices (with the push-retry rebase switched to a fresh `fetch --deepen` or re-fetch, since shallow rebases can miss merge bases); and (b) `git log` noise, which is cosmetic. Separately: **artifact-only history is constitutionally disqualified** — Actions artifacts retain at most 90 days on public repos, and rule "keep history snapshots forever" therefore requires `data/` commit-back (or an external store, which violates zero-cost/zero-dependency). The open question is only whether **docs/** rides along.

### 7-A (shipped) — Single cron, commit-back data + docs to the serving branch

**Sketch.** As shipped above. The serving branch's `docs/` is simultaneously the deploy target, the audit trail of every published page, and the offline `file://` copy in any clone.

**Strongest FOR.** One moving part and the strongest possible last-good semantics: publish is `git push`, so any failure — fetch, gate, tests — upstream of the push publishes nothing and the previous page keeps serving with zero deploy-specific logic; the daily data commit also doubles as the activity heartbeat against GitHub's 60-day scheduled-workflow auto-disable (a new dated `data/YYYY-MM-DD.json` exists every day, so the "no changes to publish" early-exit will essentially never starve the heartbeat). The committed page also lets `make check` lint the *exact served artifact* at any later date, and lets the verifier diff what was actually published on any historical day.

**Strongest AGAINST.** It couples three concerns (data history, page artifact, deploy trigger) into one branch: a rebuilt-page-only change pollutes data history's `git log`, the served branch must accept bot pushes forever (interacts badly with any future branch protection), and the docs/ blobs are pure derived state — committing renderer output next to its inputs is the classic build-artifact-in-repo smell, tolerated only because Pages branch-deploy demands it.

**Evidence it is right.** The measured growth numbers above (storage is a non-issue), plus the first month of green runs where every "page differs from yesterday" is explained by a data diff in the same commit.

### 7-B — Data-only commit-back + Actions-Pages deploy (no docs/ in git)

**Sketch.** Same single cron and job order, but the workflow commits **only `data/`** (and `governance/` health notes if any), then builds the page in-runner and deploys it via the official `actions/upload-pages-artifact` + `actions/deploy-pages` path, with Pages source switched to "GitHub Actions." `docs/` leaves the repo entirely (or holds a README stub). Because the renderer is a pure function (two builds from identical data are byte-identical — already a tested invariant), any historical page is reproducible on demand from the committed snapshot, so no audit trail is lost, only precomputed.

**Strongest FOR.** It cleanly separates constitutional history (data, kept forever) from derived artifact (page, rebuilt at will): repo history growth drops to ~12 KB/day worst case, `git log` reads as a pure data changelog, and deploys become atomic environment deployments that only replace the site on success — deploy failure semantics equal to A's, without a bot ever committing build output. It also escapes the branch-deploy 10-builds/hour soft limit and the hidden Jekyll `pages-build-deployment` workflow entirely.

**Strongest AGAINST.** The served page no longer exists anywhere at rest: post-hoc verification ("what exactly was on the page on Oct 3?") requires re-running the renderer against that day's snapshot and *trusting* renderer determinism across renderer versions — which is only true modulo the renderer code that was HEAD that day, so the reproduction needs `git checkout <that day's commit>` first. That is a real weakening of the verifier's job compared to diffing a committed HTML file, and offline `file://` reading from a clone requires a build step.

**Evidence it is right.** Any of: repo pack size or CI checkout time actually becoming annoying (see RIDERS for thresholds); a branch-protection requirement landing on the default branch; or the Jekyll/branch-deploy pipeline misbehaving (see D-2 under Decision 8).

### 7-C — Split fetch and publish schedules (two workflows, decoupled failure domains)

**Sketch.** Workflow 1 ("fetch," cron e.g. 11:45 UTC): collectors → snapshot → gate over data only → commit `data/`. Workflow 2 ("publish," cron 12:30 UTC, plus `workflow_dispatch`): checkout, build, full gate with `REQUIRE_HTML=1`, tests, deploy (commit docs/ or Actions-Pages). Chaining publish off the data push is *not* automatic — pushes made with `GITHUB_TOKEN` deliberately do not trigger `push` workflows — so the honest wiring is either two crons, a `workflow_run` trigger, or an explicit `repository_dispatch` from workflow 1. A variant fetches 2–3× daily (sources update at different hours; Arena's HF dataset lags 1–2 days, OpenRouter is weekly, AA is intraday) while publishing once, pre-morning.

**Strongest FOR.** Failure isolation with retry asymmetry: a flaky source at 11:45 can be retried at 12:10 without touching the publish path, and a renderer bug can never block snapshot capture (today, a failing UI test in `make test` blocks the *data commit* too — the shipped design forfeits a day of history over a CSS regression; that is a genuine architectural criticism of 7-A worth recording in the ADR even if 7-C is rejected). Multiple fetches per day also capture intraday source states the once-daily design flattens.

**Strongest AGAINST.** Two schedules, two concurrency groups, and an inter-workflow contract (which snapshot does publish build? what if fetch 2 lands mid-publish?) — the coordination complexity is the very thing the ephemeral-sandbox constraint argues against, and the concrete benefit is small while sources are dailies and weeklies. Multi-fetch also multiplies snapshot files per day, which the `DATED_RE`/latest.json machinery and the "keep forever" rule weren't specced for.

**Evidence it is right.** Observed pattern of partial-failure days where one flaky source cost the whole run, or a real need for intraday freshness (e.g., a launch week). Cheap intermediate: keep one workflow but make the data commit happen *before* build/test, so page-side failures can't lose the snapshot — that captures 7-C's best property inside 7-A's shape.

### 7-D — Event/webhook-driven refresh

**Sketch.** Trigger runs from source-side events instead of (or in addition to) cron: `repository_dispatch` fired by anything that can send an authenticated POST — e.g., a HF-dataset-update watcher for Arena, an RSS-to-webhook bridge for METR/ARC announcements — plus a low-frequency cron as backstop.

**Strongest FOR.** Freshness tracks reality instead of a clock: launch-day numbers land on the page hours earlier, which is exactly when the dashboard matters most.

**Strongest AGAINST.** None of the primary sources offers webhooks; every event path therefore requires a *third* system doing polling somewhere else (which is just cron with extra infrastructure, likely non-free, violating zero-recurring-cost), and each inbound dispatch needs a PAT-bearing caller — a standing credential with repo scope, a worse security posture than zero inbound triggers. This option space is honestly empty in 2026 for these sources; it should be recorded as *considered and structurally unavailable*, not as a strawman.

**Evidence it would become right.** A primary source ships webhooks or a push channel (watch item; none announced as of 2026-08-01).

### 7-E — Judgment-layer placement (orthogonal sub-decision; four real options)

1. **In-run, `claude -p` CLI (shipped)** — currently inert per defect D-1; fixing it means adding a Node setup + `npm install -g @anthropic-ai/claude-code` to the runner (~30–60s/run, a new supply-chain surface) purely to shell out to an API the repo can call directly. FOR: identical behavior local vs CI. AGAINST: heaviest dependency for the least reason.
2. **In-run, direct Anthropic Messages API via `requests`** — swap `run_model()`'s subprocess for one HTTPS POST; every safeguard (locked-prompt hash, schema, no-new-facts validator, all-or-nothing implications) is transport-independent and survives unchanged. FOR: smallest diff that makes the upgrade path real; no new toolchain. AGAINST: the prompt-lock now covers only the prompt text, not CLI-version behavior drift — pin the `model` and `max_tokens` request fields into the hashed material to compensate.
3. **Post-publish editorial workflow** — mechanical page publishes at 12:30 unconditionally; a second job (or `workflow_run` follow-on) attempts judgment and, on validator pass, commits the upgraded snapshot + rebuilt page minutes later. FOR: the LLM is fully outside the critical path — its 480s timeout can never delay the morning page, and the mechanical/editorial page states are separately observable commits (nice for the verifier). AGAINST: two publishes per day (double Pages builds, double tape states), and the shipped design already achieves non-blocking via `|| echo` degradation — the isolation gain is marginal.
4. **No LLM, ever (mechanical-permanent)** — delete the upgrade path; implications only change by human-authored snapshot edits at gates. FOR: removes the only non-deterministic component and the only secret from the entire pipeline; the validator-quarantined LLM is still an LLM writing editorial lines the reader may over-trust. AGAINST: forfeits the brief's stated judgment tier and leaves implications going stale between gate sessions with only their "since <date>" label as mitigation.

### Comparison

| | Moving parts | Repo growth | Last-good guarantee | Snapshot-loss risk | Freshness | Distance from shipped |
|---|---|---|---|---|---|---|
| **7-A shipped** | 1 workflow | ~2–6 MB/yr (measured basis) | push-or-nothing (strongest, simplest) | page-side failure loses the day's data commit | daily | — |
| **7-B data-only + Actions deploy** | 1 workflow + Pages env | ~1–2 MB/yr | atomic deploy on success | same as A unless commit moved earlier | daily | small (workflow + Pages toggle) |
| **7-C split fetch/publish** | 2 workflows + contract | as A/B | as chosen deploy | eliminated | intraday possible | medium |
| **7-D event-driven** | external infra | — | — | — | best in theory | structurally unavailable |
| **7-E.2 API judgment** | −1 toolchain vs shipped intent | — | unchanged | unchanged | unchanged | tiny |

**Ranked recommendation.** (1) **Ratify 7-A's skeleton** — single cron at an off-hour minute (12:30 is correctly off the top-of-hour load spike), commit-back as heartbeat and history, concurrency group, push-as-publish — **with three riders**: move the `data/` commit ahead of build/tests (steals 7-C's only decisive advantage), change `fetch-depth: 0` → `1` (removes the one real growth cost), and resolve D-1 by adopting **7-E.2** (direct API call) as the judgment transport. (2) Pre-register **7-B** as the reversal for docs/ churn or branch-protection triggers — note it pairs with Decision 8-B and should be flipped *together* with it, never separately. (3) Record 7-C as rejected-with-salvage (the early-commit rider) and 7-D as structurally unavailable with a watch trigger. On judgment placement, 7-E.4 (mechanical-permanent) deserves an honest line in the ADR as the security-maximal option that was declined because the validator architecture (locked prompt, no-new-facts, all-or-nothing) is exactly the containment that makes the LLM tier acceptable.

---

## Decision 8 — Publishing / access

Candidate: GitHub Pages **deploy-from-branch**, serving `/docs` on the default branch; URL `https://brant808.github.io/model-eval-dashboard/` (project site; `docs/index.html` copy already makes the bare URL resolve). Constraints: zero recurring cost, no reader login, one-tap iPhone, last-good on failure, keyboard-only human setup.

Grounded platform facts common to 8-A/8-B: Pages on GitHub Free requires a **public** repository (already priced in by rule 12 and RISK-001); published sites ≤1 GB, soft 100 GB/month bandwidth (this page is 30.7 KB gzipped — a reader would need ~100M loads/month to feel it); branch deploys have a soft 10-builds/hour limit which one build/day never approaches; every branch deploy runs GitHub's own `pages-build-deployment` (Jekyll) workflow.

**Flagged defect D-2 (bears on 8-A).** `/home/user/model-eval-dashboard/docs/` contains no `.nojekyll` file. Branch-deploy will therefore run Jekyll over `docs/` on every publish. Today's two plain HTML files pass through Jekyll unharmed (no YAML front matter, no underscore-prefixed paths), but this leaves a standing failure class (Jekyll build errors block deploys; underscore-named assets silently vanish) that one empty file removes. Add `docs/.nojekyll` before the Phase 8 gate's deploy-failure drill.

### 8-A (candidate) — Deploy-from-branch, `/docs` on default branch

**Sketch.** One-time Settings → Pages toggle (source: deploy from branch; branch: default; folder: `/docs`). Every push that touches `docs/` triggers GitHub's managed build-and-deploy; no workflow YAML owned by us on the publish side.

**Strongest FOR.** Minimal owned surface: the deploy pipeline is GitHub's problem, the one-time setup is a two-field settings form (keyboard-navigable), and last-good semantics stack twice — a failed pipeline run never pushes (so no deploy is even attempted), and if the managed Pages build itself fails, the site keeps serving the last successful deployment. It also keeps the served artifact in-repo, which Decision 7-A's audit argument depends on.

**Strongest AGAINST.** It hard-couples Decision 7 to commit-back of build artifacts forever (you cannot take docs/ out of git without changing deploy method), inserts the opaque Jekyll step (D-2), and offers the weakest deploy observability of the GitHub options — the `pages-build-deployment` run is not ours to add checks to, and its rare pathologies (stale serving despite green runs) are documented in community reports rather than guarantees.

**Adoption evidence.** It is the brief's presumptive answer; ratification evidence is simply the Phase 8 gate passing: cold cellular load, mid-update-failure drill showing last-good, and the 30-day no-maintenance simulation (the 60-day auto-disable mitigation from Phase 7's daily commit is the load-bearing piece there).

### 8-B — Actions-based Pages deploy (official `upload-pages-artifact` + `deploy-pages`)

**Sketch.** Pages source set to "GitHub Actions"; `daily.yml` gains `pages: write` + `id-token: write` permissions and two steps after the gate: upload `docs/` (or the build output directly) as a Pages artifact, then `deploy-pages` into the `github-pages` environment. Works with or without committing docs/ — which is exactly why it is the required partner of Decision 7-B.

**Strongest FOR.** The deploy becomes an explicit, observable step in *our* gated workflow: the constitutional gate and the deploy are in one dependency chain with no managed Jekyll build in between, deployments are atomic environment deployments that replace the site only on success, and it is the only GitHub option that ever permits taking derived HTML out of git.

**Strongest AGAINST.** More owned YAML and two more permission grants in the workflow token; and if docs/ also stays committed (8-B without 7-B), you carry both costs — artifact churn in git *and* deploy steps — for no benefit. It also puts deploy inside the same job whose timeout/failure now has one more way to occur, though upstream-gate failure still simply means no deploy attempt.

**Adoption evidence.** Any 8-A trigger firing: a Jekyll-layer failure, a stale-serving incident, a branch-protection need, or adoption of 7-B. Switching is a settings toggle plus ~10 workflow lines; it is the natural pre-registered reversal.

### 8-C — Separate `gh-pages` branch (orphan, single-commit, force-pushed)

**Sketch.** Default branch carries only source + data; the daily job builds the page and force-pushes it as a single orphan commit to `gh-pages`; Pages deploys from `gh-pages` root.

**Strongest FOR.** Gets docs/ churn out of the main branch's history while keeping the simple branch-deploy mechanics — main's `git log` is pure data/source, and the served branch's history is deliberately disposable (data remains the authoritative, forever-kept record).

**Strongest AGAINST.** It is strictly dominated in 2026: 8-B achieves the same history separation with official, atomic tooling and no standing force-push (a daily `push --force` from CI is both a footgun and the exact pattern branch-protection and audit hygiene argue against). Its era was pre-`deploy-pages`; choosing it now would be adopting the legacy workaround after the vendor shipped the real feature.

**Adoption evidence.** Only if 8-B's `github-pages` environment path were unavailable (e.g., an enterprise policy blocking environment deployments — not applicable to a personal repo). Include in the ADR as considered-and-dominated.

### 8-D — External free static host (Cloudflare Pages primary; Netlify assessed and disqualified)

**Sketch.** Cloudflare Pages, either git-integrated (Cloudflare watches the repo and redeploys on push — free tier: 500 builds/month, 20k files, 25 MiB/file; static asset serving with no bandwidth metering on Pages) or direct-upload from `daily.yml` via `wrangler pages deploy` with a `CLOUDFLARE_API_TOKEN` secret. URL `<project>.pages.dev`, custom domain free.

**Strongest FOR.** Independence from the single vendor that currently holds scheduler, host, repo, and notification channel: a GitHub Pages incident takes the page down at exactly 05:30 Pacific with no recourse, while a Cloudflare mirror gives a second URL on disjoint infrastructure — and Cloudflare's static tier is genuinely unmetered where GitHub's is a 100 GB soft limit.

**Strongest AGAINST.** A second account, a second credential in repo secrets (direct-upload variant), a second dashboard that can rot during the 30-day no-maintenance window, and a second ToS — all spent insuring against a low-probability outage for a one-reader page whose failure mode ("read it an hour later") is benign. **Netlify is disqualified on current pricing**: the free plan is now credit-based (300 credits/month, deploys 15 credits each), so ~30 deploys/month costs ~450 credits — daily deploys exceed the free tier by construction. Zero-recurring-cost fails.

**Adoption evidence.** Repeated GitHub Pages availability incidents at read time, a Pages throttle (HTTP 429s), or GitHub pricing/policy change. Best adopted as *mirror*, not replacement (keep the canonical URL; add `wrangler` upload as a non-blocking final step).

### 8-E — Repo-direct serving (raw / CDN proxies) — rejected, for the record

`raw.githubusercontent.com` serves HTML as `text/plain` (won't render); third-party wrappers (raw.githack, jsDelivr et al.) restrict or de-prioritize HTML serving and add an unaccountable dependency. No option here meets "keeps serving last-good under a failed build" any better than Pages, and all fail basic reliability posture. Considered and rejected; listed so the ADR shows the option space was actually swept.

**Access-layer notes common to all options (for HANDOFF).** One-tap iPhone = Safari → share sheet → Add to Home Screen on the final URL; note honestly in HANDOFF that this specific step is touch-gesture on iOS (VoiceOver-keyboard workarounds exist, but the natural flow is two taps) — the keyboard-only constraint is fully satisfiable for every *Mac and GitHub* setup step (Settings → Pages is form-navigable; `gh api` can even set the Pages source entirely from the CLI: `gh api -X POST repos/Brant808/model-eval-dashboard/pages -f build_type=legacy -f 'source[branch]=main' -f 'source[path]=/docs'`, or `build_type=workflow` for 8-B). Since the page is fully self-contained, an offline-tolerant home-screen open could later be added via a service worker — but that adds cache-invalidation risk to a daily-refresh page and should not ship in Phase 8.

### Comparison

| | Recurring cost | Owned surface | Last-good on failed build | History coupling | Setup (keyboard-only) | Vendor concentration |
|---|---|---|---|---|---|---|
| **8-A branch-deploy (candidate)** | $0 | none (managed) | yes (double: no-push + last-deploy) | forces docs/ in git | 1 settings form / 1 `gh api` call | max |
| **8-B Actions deploy** | $0 | ~10 YAML lines + 2 perms | yes (atomic env deploy) | none (enables 7-B) | 1 toggle + workflow edit | max |
| **8-C gh-pages branch** | $0 | force-push script | yes | main clean, branch churn | medium | max |
| **8-D Cloudflare mirror** | $0 (CF Pages) | account + token | yes | none | signup + token (keyboard OK) | reduced |
| Netlify | fails free tier at daily deploys | — | — | — | — | — |

**Ranked recommendation.** (1) **Ratify 8-A** with the `.nojekyll` rider (D-2) — for a one-page, one-build-per-day site, the managed path's near-zero owned surface beats 8-B's observability gains, and the double last-good guarantee is the strongest on offer; (2) pre-register **8-B as the paired reversal with 7-B** (one trigger flips both; never flip one alone); (3) hold **8-D (Cloudflare, direct-upload mirror)** behind an availability trigger, explicitly as mirror-not-replacement; (4) record 8-C as dominated and 8-E as rejected. Netlify's disqualification is worth one grounded sentence in the ADR so the "other free hosts" question stays closed on evidence, not vibes.

---

## RIDERS — reversal triggers and fixes for `governance/RISKS.md`

Concrete, observable, and pre-registered. D-1 and D-2 are defects to fix before their gates, not accepted risks.

1. **FIX (Phase 7, blocking the ADR-as-written): judgment upgrade path inert in CI.** `daily.yml` never installs the `claude` CLI; `tools/judgment.py:213` therefore always degrades in Actions even with the secret present. Fix by either installing the CLI in the workflow or re-pointing `run_model()` at the Messages API via `requests` (recommended; pin model id into the hashed prompt material). Verification: a dispatched run with the secret set produces `health.judgment_layer: on (...)`.
2. **FIX (Phase 8, before the deploy-failure drill): add `docs/.nojekyll`.** Removes the managed Jekyll build class of deploy failures under 8-A.
3. **Compare-paradigm reversal (6-A → 6-B).** Trigger: the Phase 6/9 rendered cold read fails specifically on "what moved in 72h" while trio-state reads pass, OR the reader reports/observes matrix-skipping (tape + quick-look only) on ≥5 of 7 consecutive mornings. Action: promote the delta panel above quick-look, collapse matrix behind a keystroke; refit-day mass-change collapsing is a precondition of the flip.
4. **Trend-cell upgrade (6-E-lite).** Trigger: ≥21 dated snapshots in `data/`. Action: sparklines into the quick-look band only; full 6-E only if a later cold read shows the reader opening briefs primarily for trend context.
5. **Field-view overflow (6-D-as-addition).** Trigger: catalog reaches ≥10 models with ≥50% row coverage each, OR the field-#1 footnote density cap (4) binds on ≥3 consecutive builds. Action: add keystroke-gated per-metric leaderboard view; judged against the 60-second objection at that gate.
6. **Page-weight guard for the static-all-columns render.** Trigger: built page >1.0 MB raw (early warning at two-thirds of the 1.5 MB cap) or picker swap >100 ms measured on iPhone-class hardware. Action: move superseded-model columns from static render to JS-hydrated from the embedded state JSON (keeps no-JS fallback for current models only).
7. **History-growth / commit-back reversal (7-A/8-A → 7-B/8-B, flipped together).** Trigger (any): `git count-objects -vH` size-pack >150 MB; scheduled-run checkout step >60 s after the `fetch-depth: 1` fix; branch protection required on the serving branch; or a `pages-build-deployment` failure/stale-serving incident not explained by our own push. Action: Pages source → GitHub Actions, add upload/deploy steps, stop committing `docs/`, record that historical pages are thereafter reproduced via `git checkout <day> && make build` (renderer determinism is the load-bearing invariant — note it in the ADR).
8. **Snapshot-loss guard (salvaged from rejected 7-C).** Trigger: any run where collectors succeeded but a downstream build/test failure prevented the `data/` commit (observable as a red run with no data commit that day). Action: reorder the workflow to commit `data/` immediately after the data-only gate, before build/tests. Consider adopting preemptively at the Phase 7 gate — it costs one step reorder.
9. **Scheduler-miss guard.** Trigger: page `generated_at` older than 26 h on ≥2 occasions in any 14-day window (GitHub documents that scheduled events can be delayed or dropped under load). Action: add a second cron entry ~45 min later as an idempotent retry (concurrency group already serializes; an unchanged day publishes nothing).
10. **Auto-disable heartbeat watch.** The 60-day scheduled-workflow auto-disable is mitigated by the daily dated-snapshot commit; residual risk is a sustained all-sources-down stretch producing no commits. Trigger: ≥7 consecutive runs ending "no changes to publish." Action: add an explicit heartbeat (commit a one-line health note, or a workflow that calls the enable-workflow API monthly). Also note RISK-002 dependency: cron and dispatch activate only after merge to the default branch — the first observed green dispatched run post-merge closes this.
11. **Host-availability mirror (8-D).** Trigger: ≥2 GitHub Pages availability incidents intersecting the reader's 05:30–08:00 Pacific window in any 90 days, or sustained HTTP 429s from Pages. Action: add non-blocking `wrangler pages deploy` mirror step with `CLOUDFLARE_API_TOKEN` secret; canonical URL unchanged; HANDOFF gains the token setup as keyboard steps.
12. **HANDOFF honesty note (rule-of-constraints, not a trigger).** iPhone Add-to-Home-Screen is a touch gesture; record it as the one non-keyboard human step, with every Mac/GitHub step keyboard-only (including the optional `gh api` Pages-source command under Decision 8's notes).

## Grounding notes (GitHub/host behavior claims)

- Scheduled workflows auto-disabled after 60 days of no repository activity in public repos; disabled by default in forks: [Disabling and enabling a workflow](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/disabling-and-enabling-a-workflow), [Events that trigger workflows — schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) (also: schedule runs on the default branch's latest commit; delays/drops during high load, worst at the top of the hour).
- `GITHUB_TOKEN` pushes do not trigger new `push` workflow runs (anti-recursion): [Triggering a workflow](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow).
- Pages limits — 1 GB site, 100 GB/month soft bandwidth, soft 10 builds/hour for branch deploys (not applicable to custom Actions workflows), 10-minute deployment timeout: [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).
- Publishing sources — branch deploy (root or `/docs`) vs. Actions (`actions/upload-pages-artifact` + `actions/deploy-pages`, `github-pages` environment); branch deploys always run a managed `pages-build-deployment` workflow: [Configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
- Pages on GitHub Free requires a public repository: [Quickstart for GitHub Pages](https://docs.github.com/en/pages/quickstart), [GitHub's plans](https://docs.github.com/get-started/learning-about-github/githubs-products).
- Actions artifact retention: 90-day default; public repos max 90 days (private up to 400) — why artifact-only history is constitutionally disqualified: [Configuring the retention period](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization).
- Stale-serving pathologies of branch deploys are community-reported, not guaranteed behavior: [GitHub Community discussion #200884](https://github.com/orgs/community/discussions/200884), [#152753](https://github.com/orgs/community/discussions/152753).
- Cloudflare Pages free tier (500 builds/month, 20k files, 25 MiB/file): [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/).
- Netlify free plan now credit-based (300 credits/month; deploys 15 credits each → daily deploys exceed the tier): [Netlify billing FAQ for credit-based plans](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/billing-faq-for-credit-based-plans/), [Introducing Netlify's Free plan](https://www.netlify.com/blog/introducing-netlify-free-plan/).
- Local measurements (this repo, 2026-08-01): page 154,199 B raw / 30,721 B gzipped; snapshot 71,179 B raw / 11,602 B zlib; `docs/index.html` byte-identical to `model-eval-monitor.html` (single git blob). Growth bounds derive from these.
