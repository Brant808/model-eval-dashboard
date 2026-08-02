# RUNBOOK — Operating the Dashboard

Every procedure the operator (or a future agent) needs, in execution order,
keyboard-only. The constitution (`tools/check_invariants.py`) is the safety
net for all of them: after ANY procedure, `make all` must be green before
committing. Never weaken the linter to make a step pass.

## 0. Daily normal operation (no action)

The `daily-refresh` workflow (12:30 UTC) fetches, gates, and commits back
`data/` + `docs/`. GitHub Pages serves `docs/` from the branch, so a run that
fails the constitutional gate publishes nothing and the last green page keeps
serving. You only act when the health footer on the page shows a source DOWN
for more than ~3 days, or the Actions tab shows red runs.

## 1. Read the health footer

Bottom of the page, `Pipeline health`. Each source line is `S# ok (fetched …)`
or `S# DOWN: <error>`. `run_status: collected (degraded)` means at least one
source failed and its cells carry last-good values with the visible
`source down (last-good shown)` flag — the page is honest about it, no
emergency. `judgment_layer: off (mechanical)` is the designed default.

## 2. Force a refresh now

GitHub → repo → Actions → `daily-refresh` → Run workflow → Enter (accept the
default branch). Locally instead: `COLLECT=1 make all` then commit `data/` and
`docs/` and push.

## 3. A source died (site redesign, DNS gone, 4xx forever)

Symptoms: health line `S# DOWN: ParseFailure/FetchFailure …` for days; cells
carry `source down (last-good shown)` and eventually a staleness badge.

1. Reproduce: `COLLECT=1 FAIL_SOURCES= make fetch` locally, read stderr.
2. If it is a page-shape change: refetch the raw page into
   `collectors/fixtures/` (gzip it), fix ONLY the parser in `collectors/`,
   update the fixture test values if the source genuinely republished, run
   `make test`.
3. If the source is permanently gone: add `Sunset: YYYY-MM-DD` to its
   `governance/SOURCES.md` entry (the linter then bans newer snapshots from
   citing it), and either retire the metric (procedure 5) or repoint it to a
   replacement source (new S-entry, new collector, ADR).
4. Commit with an ADR note; push.

## 4. Add a model (column)

1. `collectors/model_map.py`: add the model to `MODELS` (id, name, vendor).
   Then add its per-source spelling to each collector's id/name map:
   `LLMSTATS_IDS` in `collectors/model_map.py`; `ECI_NAMES`, `LIVEBENCH_IDS`,
   `REBENCH_NAMES`, `VALS_KEYS` in `collectors/newrows.py`; the AA/Arena/ARC
   name maps in their own collector modules (grep the old model's id to find
   every map).
2. Nothing else: collectors emit cells for mapped models automatically; every
   unmapped metric renders an honest empty with the metric's default reason.
3. `COLLECT=1 make all`. The explainability test forces every new populated
   cell through tape/changelog — the pipeline writes those entries itself.
4. Watch-list promotion (e.g. Muse Spark): the promotion test case in
   `data/2026-08-01.json`'s `watch` block documents the trigger; when it
   fires, follow this procedure and delete the watch entry in the same commit.

## 5. Retire a metric (row)

1. Delete its entry from `collectors/registry.py::METRICS` and its collector
   emit (or the whole collector if single-metric).
2. Do NOT delete historical snapshots — they keep the row forever
   (history is constitutional). The next collected snapshot simply lacks the
   row; `diff_entries` records the removal in the changelog.
3. Remove the metric's brief from `data/briefs.json`; rewrite any implication
   citing it (linter will list them: run `make check`).
4. ADR required — a row that "earned its place" (Phase 2) needs a recorded
   reason to lose it.

## 6. Snapshot corrupted / bad data committed

1. Identify the last good dated snapshot: `git log --oneline -- data/`.
2. `git checkout <good-sha> -- data/<date>.json` (or delete the bad dated
   file if it should never have existed — it must not be silently edited:
   fix-forward with a new dated snapshot is the default; history rewrites
   only for rule-12 violations, credentials, or fabricated data).
3. `make fetch` re-materializes `data/latest.json` from the newest dated
   snapshot (SYNC rule keeps them byte-identical).
4. `make all`; commit with an explanation; push.

## 7. Replay / audit an old day

`PIPELINE_DATA_DIR` and `CHECK_ALLOW_OLD_LATEST=1` exist for this:

```
mkdir /tmp/replay && cp data/2026-07-31.seed.json /tmp/replay/
PIPELINE_DATA_DIR=/tmp/replay python3 -m collectors.run   # materialize
CHECK_ALLOW_OLD_LATEST=1 PIPELINE_DATA_DIR=/tmp/replay python3 tools/check_invariants.py --data-dir /tmp/replay
python3 site/render.py --data /tmp/replay/latest.json --out /tmp/replay/page.html
```

`CHECK_ALLOW_OLD_LATEST=1` suppresses only the 54-hour rot guard — every
constitutional rule still applies to the replayed day.

## 8. Judgment layer on/off

On: add repository secret `ANTHROPIC_API_KEY` (Settings → Secrets and
variables → Actions). Off: delete the secret. No code change either way; the
health footer states which mode produced the page and why, including when the
validator rejected the model's output.

## 9. Chaos drills (run quarterly)

```
OFFLINE=1        COLLECT=1 PIPELINE_DATE=… make fetch   # total network loss
FAIL_SOURCES=S1,S2 COLLECT=1 PIPELINE_DATE=… make fetch # partial loss
```

Both must produce a linter-green snapshot with loud degradation flags.
`tests/test_pipeline.py` runs the same drills in CI on every push.
