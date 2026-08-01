#!/usr/bin/env python3
"""Pipeline fetch entry point (`make fetch`).

Phase 0 form: no live collectors exist yet, so this materializes
`data/latest.json` as a byte-identical copy of the newest dated snapshot.
Phase 7 adds per-source collector modules; this entry point then runs them to
produce today's `data/YYYY-MM-DD.json` before materializing latest.json.

latest.json is a copy, not a symlink: symlinks are fragile across CI
checkouts, Pages deploys, and non-POSIX tooling.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(\.seed)?\.json$")


def newest_dated_snapshot() -> Path:
    candidates = sorted(p for p in DATA.glob("*.json") if DATED_RE.match(p.name))
    if not candidates:
        print("fetch: no dated snapshots in data/", file=sys.stderr)
        sys.exit(1)
    return candidates[-1]


def materialize_latest() -> Path:
    src = newest_dated_snapshot()
    dst = DATA / "latest.json"
    shutil.copyfile(src, dst)
    print(f"fetch: materialized {dst.relative_to(REPO)} from {src.name}")
    return dst


def main():
    materialize_latest()


if __name__ == "__main__":
    main()
