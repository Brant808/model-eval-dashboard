---
description: Run the full pipeline (fetch, build, check, test) and summarize what moved
---

Run `make all`. Then:

1. If any step failed, diagnose and report the failing step, the source involved,
   and whether the page degraded correctly (last-good + staleness badge) — do not
   silently retry more than once.
2. If it succeeded, diff `data/latest.json` against the previous dated snapshot
   and summarize: cells changed, tape entries generated, any new integrity flags,
   any staleness. Confirm the invariant linter is green.
3. Report the built page location (`docs/model-eval-monitor.html`) and its size.
