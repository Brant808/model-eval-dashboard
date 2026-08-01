#!/usr/bin/env python3
"""Renderer: pure function from snapshot (+ history) to a single self-contained
HTML page. No network, no wall-clock reads, no randomness — two runs on
identical data must be byte-identical (all timestamps come from the snapshot).

Phase 0 form: minimal page that honors the full data-attribute contract the
invariant linter checks (data-cell-id/tag/stale/warn/chip/set, tape and
implication attributes). Phase 6 replaces the presentation with the
Apple-compare UI on top of this same contract.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.check_invariants import compute_chips, integrity_flags, is_populated  # noqa: E402

GROUP_TITLES = {
    "independent-core": "Independent core",
    "frontier-headroom": "Frontier headroom",
    "daily-movers": "Daily movers",
    "lab-claimed": "Lab-claimed",
    "economics-deployment": "Economics and deployment",
}


def esc(s):
    return html.escape(str(s), quote=True)


def render_cell(metric_id, model_id, cell, chips):
    cid = f"{metric_id}.{model_id}"
    warn = "1" if integrity_flags(cell) else "0"
    stale = "1" if cell.get("stale") else "0"
    chip = "1" if cid in chips else "0"
    cset = cell.get("comparability_set", "")
    if is_populated(cell):
        tag = cell.get("tag", "")
        bits = [
            f'<td data-cell-id="{esc(cid)}" data-tag="{esc(tag)}" data-stale="{stale}" '
            f'data-warn="{warn}" data-chip="{chip}" data-set="{esc(cset)}">'
        ]
        value = cell.get("value")
        unit = cell.get("unit", "")
        shown = f"{value}" if unit in ("text", "") else f"{value} {unit}"
        bits.append(f'<span class="val">{esc(shown)}</span>')
        if cell.get("effort_tier"):
            bits.append(f'<span class="tier">tier: {esc(cell["effort_tier"])}</span>')
        bits.append(f'<span class="tag tag-{esc(tag)}">{esc(tag)}</span>')
        bits.append(f'<span class="src">[{esc(cell.get("source_id", ""))}]</span>')
        if chip == "1":
            bits.append('<span class="chip"><span class="chip-glyph">▲</span><span class="chip-label">LEAD</span></span>')
        if stale == "1":
            bits.append('<span class="stale-badge">STALE</span>')
        for f in cell.get("flags", []):
            klass = "warn-tag" if f in integrity_flags(cell) else "note-tag"
            marker = "⚠ " if klass == "warn-tag" else ""
            bits.append(f'<span class="{klass}">{marker}{esc(f)}</span>')
        bits.append("</td>")
        return "".join(bits)
    reason = cell.get("empty_reason", "")
    bits = [
        f'<td data-cell-id="{esc(cid)}" data-empty-reason="{esc(reason)}" '
        f'data-stale="{stale}" data-warn="{warn}" data-chip="0" data-set="{esc(cset)}">'
    ]
    bits.append(f'<span class="empty">— <em>{esc(reason)}</em></span>')
    for f in cell.get("flags", []):
        klass = "warn-tag" if f in integrity_flags(cell) else "note-tag"
        marker = "⚠ " if klass == "warn-tag" else ""
        bits.append(f'<span class="{klass}">{marker}{esc(f)}</span>')
    bits.append("</td>")
    return "".join(bits)


def render(snap) -> str:
    models = snap["models"]
    metrics = snap["metrics"]
    chips = compute_chips(snap)
    out = []
    out.append("<!DOCTYPE html>")
    out.append('<html lang="en"><head><meta charset="utf-8">')
    out.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    out.append("<title>Frontier Model Eval Monitor</title>")
    out.append("<style>")
    out.append(
        "body{background:#f7f5f0;color:#1a1a1a;font-family:'Public Sans',system-ui,"
        "-apple-system,'Segoe UI',sans-serif;margin:2rem;max-width:1200px}"
        "h1,h2{font-family:'Archivo','Public Sans',system-ui,sans-serif}"
        "code,.src,.val{font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace}"
        "table{border-collapse:collapse;width:100%;margin-bottom:1.5rem}"
        "td,th{border:1px solid #d8d4ca;padding:.4rem .6rem;vertical-align:top;font-size:.85rem}"
        "th{background:#eceadf;text-align:left}"
        ".tag{font-weight:700;border:1px solid;border-radius:3px;padding:0 .25rem;margin-left:.35rem;font-size:.7rem}"
        ".tag-I{color:#1e40c9;border-color:#1e40c9}.tag-V{color:#9a6b00;border-color:#9a6b00}"
        ".chip{margin-left:.35rem;font-size:.7rem;font-weight:700;color:#1e40c9}"
        ".stale-badge{background:#9a6b00;color:#fff;font-size:.65rem;padding:0 .3rem;margin-left:.35rem;border-radius:3px}"
        ".warn-tag{display:block;color:#8a2b00;font-size:.7rem;margin-top:.15rem}"
        ".note-tag{display:block;color:#666;font-size:.7rem;margin-top:.15rem}"
        ".empty em{color:#777}.src{color:#888;font-size:.7rem;margin-left:.3rem}"
        ".tier{display:block;font-size:.7rem;color:#444}"
        "footer{border-top:2px solid #1e40c9;margin-top:2rem;padding-top:.5rem;font-size:.8rem;color:#555}"
        ".tape li{margin-bottom:.3rem}"
    )
    out.append("</style></head><body>")
    out.append("<h1>Frontier Model Eval Monitor</h1>")
    out.append(
        f'<p class="meta">Snapshot <code>{esc(snap["snapshot_date"])}</code> '
        f'(generated {esc(snap["generated_at"])}). Provenance: '
        '<span class="tag tag-I">I</span> independent, '
        '<span class="tag tag-V">V</span> vendor-claimed.</p>'
    )

    # Today's tape
    out.append("<h2>Today's tape</h2><ul class=\"tape\">")
    for entry in snap.get("tape", []):
        out.append(
            f'<li data-tape-item="1" data-tape-date="{esc(entry["date"])}" '
            f'data-tape-src="{esc(entry["source_id"])}">'
            f'<strong>{esc(entry["date"])}</strong> — {esc(entry["text"])} '
            f'<span class="src">[{esc(entry["source_id"])}]</span></li>'
        )
    if not snap.get("tape"):
        out.append("<li><em>No moves recorded in the last 72 hours.</em></li>")
    out.append("</ul>")

    # Implications (Phase 5 populates)
    if snap.get("implications"):
        out.append('<h2>Read (interpretation layer)</h2><ul class="implications">')
        for imp in snap["implications"]:
            out.append(
                f'<li data-imp-id="{esc(imp["id"])}" data-imp-tag="{esc(imp.get("tag", ""))}" '
                f'data-imp-conf="{esc(imp.get("confidence", ""))}" '
                f'data-imp-falsifier="{esc(imp.get("falsifier", ""))}">'
                f'<strong>[X]</strong> {esc(imp["text"])} '
                f'<em>confidence: {esc(imp.get("confidence", ""))}; '
                f'reverses if: {esc(imp.get("falsifier", ""))}</em> '
                f'<span class="src">cites: {esc(", ".join(imp.get("cites", [])))}</span></li>'
            )
        out.append("</ul>")

    # Matrix by group (Phase 0 presentation; Phase 6 replaces with compare UI)
    groups = []
    for metric_id, meta in metrics.items():
        g = meta.get("group", "other")
        if g not in groups:
            groups.append(g)
    model_ids = list(models.keys())
    for g in groups:
        out.append(f"<h2>{esc(GROUP_TITLES.get(g, g))}</h2>")
        out.append("<table><thead><tr><th>Metric</th>")
        for mid in model_ids:
            out.append(f"<th>{esc(models[mid]['name'])}</th>")
        out.append("</tr></thead><tbody>")
        for metric_id, meta in metrics.items():
            if meta.get("group") != g:
                continue
            row_sets = sorted(
                {
                    c.get("comparability_set", "")
                    for c in snap["cells"].get(metric_id, {}).values()
                }
            )
            out.append(
                f'<tr data-metric="{esc(metric_id)}" data-row-set="{esc("|".join(row_sets))}">'
                f"<th>{esc(meta['name'])}</th>"
            )
            for mid in model_ids:
                cell = snap["cells"].get(metric_id, {}).get(mid)
                if cell is None:
                    out.append("<td>—</td>")
                else:
                    out.append(render_cell(metric_id, mid, cell, chips))
            out.append("</tr>")
        out.append("</tbody></table>")

    # Watch list
    if snap.get("watch"):
        out.append('<h2>New-model watch</h2><ul class="watch">')
        for w in snap["watch"]:
            out.append(
                f'<li><strong>{esc(w["name"])}</strong> (first seen {esc(w["first_seen"])}, '
                f'sources: {esc(", ".join(w["seen_in_sources"]))}) — {esc(w["note"])}</li>'
            )
        out.append("</ul>")

    # Health footer
    health = snap.get("health", {})
    out.append('<footer data-health="1">')
    out.append(
        f'<p>Pipeline health: run status <code>{esc(health.get("run_status", "unknown"))}</code>; '
        f'judgment layer <code>{esc(health.get("judgment_layer", "unknown"))}</code>; '
        f'data generated <code>{esc(snap["generated_at"])}</code>.</p>'
    )
    if health.get("sources"):
        out.append("<ul>")
        for sid, status in health["sources"].items():
            out.append(f"<li><code>{esc(sid)}</code>: {esc(status)}</li>")
        out.append("</ul>")
    out.append("</footer>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    snap = json.loads(Path(args.data).read_text(encoding="utf-8"))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(snap), encoding="utf-8")
    print(f"render: wrote {args.out} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
