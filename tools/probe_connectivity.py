#!/usr/bin/env python3
"""Phase 0 connectivity probe: one fetch against each primary source domain
from this sandbox. Results go to governance/probe-results.md; blocked domains
must be copied into governance/HANDOFF.md with the environment setting to
change (the build script does this).

Honest User-Agent per the brief. 20s timeout per domain. This is a
reachability probe, not a scraper — one GET per domain, no retries.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent

USER_AGENT = (
    "model-eval-dashboard-probe/0.1 (+https://github.com/brant808/model-eval-dashboard; "
    "daily eval dashboard; contact via repo issues)"
)

# Primary source domains from the brief, plus candidate domains whose exact
# home Phase 1 must confirm (Arena and the Morph board have moved before).
TARGETS = [
    ("artificialanalysis.ai", "https://artificialanalysis.ai/"),
    ("arena.ai (brief's stated domain)", "https://arena.ai/"),
    ("lmarena.ai (candidate current Arena domain)", "https://lmarena.ai/"),
    ("openrouter.ai rankings", "https://openrouter.ai/rankings"),
    ("arcprize.org", "https://arcprize.org/"),
    ("metr.org time horizons", "https://metr.org/time-horizons"),
    ("morphllm.com (candidate Morph board home)", "https://morphllm.com/"),
    ("swebench.com (SWE-bench official)", "https://www.swebench.com/"),
    ("github.com raw (fixtures/data fallback)", "https://raw.githubusercontent.com/"),
]


def probe(url: str):
    try:
        r = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=20,
            allow_redirects=True,
        )
        return r.status_code, f"{len(r.content)} bytes, final URL {r.url}"
    except requests.RequestException as e:
        return None, f"{type(e).__name__}: {e}"


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Connectivity Probe Results",
        "",
        f"Probed at {now} from the build sandbox (outbound via platform proxy).",
        "One GET per domain, 20s timeout, honest User-Agent.",
        "",
        "| Target | Status | Detail |",
        "|---|---|---|",
    ]
    blocked = []
    for name, url in TARGETS:
        status, detail = probe(url)
        shown = str(status) if status else "BLOCKED/ERROR"
        lines.append(f"| {name} | {shown} | {detail} |")
        print(f"  {name}: {shown} — {detail}")
        if status is None or status in (403, 407, 451):
            blocked.append((name, url, detail))
    lines.append("")
    if blocked:
        lines.append("## Blocked domains (HANDOFF items)")
        lines.append("")
        for name, url, detail in blocked:
            lines.append(
                f"- `{url}` ({name}): {detail}. Fix: add the domain to the Claude Code "
                "environment's network allowlist (claude.ai/code -> environment settings "
                "-> Network access), or accept degraded last-good rendering for this source."
            )
    else:
        lines.append("All probed domains reachable from the sandbox.")
    out = REPO / "governance" / "probe-results.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"probe: wrote {out.relative_to(REPO)}; {len(blocked)} blocked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
