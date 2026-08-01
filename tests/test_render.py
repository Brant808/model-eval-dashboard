"""Renderer determinism and HTML-contract tests."""

import copy
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# `site/` is mandated by the brief's repo layout but shadows the stdlib `site`
# module, so load the renderer by file path instead of package import.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("site_render", REPO / "site" / "render.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
render = _mod.render

from tools.check_invariants import check_html, load_sources_ledger  # noqa: E402


def test_render_is_deterministic(seed):
    assert render(seed) == render(seed)


def test_render_subprocess_byte_identical(seed, tmp_path):
    """Two separate interpreter runs produce byte-identical output (catches
    dict-order and hash-seed nondeterminism that in-process runs can hide)."""
    data = tmp_path / "snap.json"
    data.write_text(json.dumps(seed), encoding="utf-8")
    outs = []
    for i in range(2):
        out = tmp_path / f"out{i}.html"
        subprocess.run(
            [sys.executable, str(REPO / "site" / "render.py"), "--data", str(data), "--out", str(out)],
            check=True,
            env={"PYTHONHASHSEED": "random", "PATH": "/usr/bin:/bin:/usr/local/bin"},
            capture_output=True,
        )
        outs.append(out.read_bytes())
    assert outs[0] == outs[1]


def test_rendered_page_passes_html_invariants(seed, tmp_path):
    p = tmp_path / "page.html"
    p.write_text(render(seed), encoding="utf-8")
    ledger = load_sources_ledger(REPO / "governance" / "SOURCES.md")
    assert check_html(p, seed, ledger) == []


def test_rendered_page_shows_required_elements(seed):
    html = render(seed)
    assert "tape" in html and 'data-tape-item="1"' in html
    assert 'data-health="1"' in html
    assert "chip-glyph" in html and "chip-label" in html  # shape + label, not color alone
    assert "STALE" not in html.replace("STALE</span> = older", "")  # nothing stale in seed (legend text aside)
    assert "⚠" in html  # integrity flags visible (Sol METR/ARC flags)
    assert "data-empty-reason" in html  # blanks are never silent


def _flip_attr_in_cell(html, cell_id, attr, old, new):
    """Flip one data-attr inside the td carrying cell_id, order-agnostic."""
    import re as _re

    pat = _re.compile(r'<td[^>]*data-cell-id="' + _re.escape(cell_id) + r'"[^>]*>')
    m = pat.search(html)
    assert m, f"cell {cell_id} not found — renderer contract changed"
    tag = m.group(0)
    forged_tag = tag.replace(f'{attr}="{old}"', f'{attr}="{new}"')
    assert forged_tag != tag, f"{attr}={old} not present in {cell_id}"
    return html[: m.start()] + forged_tag + html[m.end():]


def test_forged_chip_on_vendor_cell_is_caught(seed, tmp_path):
    """Render output where a V cell displays a chip -> linter must object."""
    html = render(seed)
    forged = _flip_attr_in_cell(html, "swe-bench-pro.opus-5", "data-chip", "0", "1")
    p = tmp_path / "forged.html"
    p.write_text(forged, encoding="utf-8")
    ledger = load_sources_ledger(REPO / "governance" / "SOURCES.md")
    out = check_html(p, seed, ledger)
    assert any(x.startswith("RULE10") for x in out)


def test_hidden_warning_tag_is_caught(seed, tmp_path):
    """Render output where an integrity-flagged cell hides its warning -> caught."""
    html = render(seed)
    forged = _flip_attr_in_cell(html, "metr-horizon.gpt-5-6-sol", "data-warn", "1", "0")
    p = tmp_path / "forged.html"
    p.write_text(forged, encoding="utf-8")
    ledger = load_sources_ledger(REPO / "governance" / "SOURCES.md")
    out = check_html(p, seed, ledger)
    assert any(x.startswith("RULE7") for x in out)


def test_stale_cell_renders_badge(seed, tmp_path):
    stale_snap = copy.deepcopy(seed)
    cell = stale_snap["cells"]["arena-elo"]["kimi-k3"]
    cell["stale"] = True
    cell["flags"] = list(cell["flags"]) + ["source down (last-good shown)"]
    html = render(stale_snap)
    assert '<span class="stale-badge">STALE</span>' in html
    import re as _re

    m = _re.search(r'<td[^>]*data-cell-id="arena-elo.kimi-k3"[^>]*>', html)
    assert m and 'data-stale="1"' in m.group(0)


# ---------------------------------------------------------------------------
# Phase 0 gate hardening: HTML forgeries the old regex checker missed.
# ---------------------------------------------------------------------------


def _check(html_text, seed, tmp_path, fname="f.html"):
    p = tmp_path / fname
    p.write_text(html_text, encoding="utf-8")
    ledger = load_sources_ledger(REPO / "governance" / "SOURCES.md")
    return check_html(p, seed, ledger)


def test_gate_single_quoted_chip_forgery_caught(seed, tmp_path):
    import re as _re

    html = render(seed)
    pat = _re.compile(r'<td[^>]*data-cell-id="swe-bench-pro.opus-5"[^>]*>')
    m = pat.search(html)
    assert m
    tag = m.group(0).replace('data-chip="0"', "data-chip='1'")
    forged = html[: m.start()] + tag + html[m.end():]
    out = _check(forged, seed, tmp_path)
    assert any(x.startswith("RULE10") for x in out)


def test_gate_duplicate_cell_id_caught(seed, tmp_path):
    html = render(seed)
    dup = (
        '<td data-cell-id="aa-index.fable-5" data-tag="I" data-stale="0" data-warn="0" '
        'data-chip="1" data-set="aa-index-v4.1"><span class="val">60 index</span>'
        '<span class="chip"><span class="chip-glyph">▲</span><span class="chip-label">LEAD</span></span></td>'
    )
    forged = html.replace('<footer class="health"', dup + '<footer class="health"')
    assert forged != html
    out = _check(forged, seed, tmp_path)
    assert any("duplicate rendered cell id" in x for x in out)


def test_gate_fabricated_cell_caught(seed, tmp_path):
    html = render(seed)
    fake = (
        '<td data-cell-id="fake-bench.opus-5" data-tag="I" data-stale="0" data-warn="0" '
        'data-chip="0" data-set="fake"><span class="val">99.9 %</span></td>'
    )
    forged = html.replace('<footer class="health"', fake + '<footer class="health"')
    assert forged != html
    out = _check(forged, seed, tmp_path)
    assert any("does not exist in the snapshot" in x for x in out)


def test_gate_wrong_displayed_value_caught(seed, tmp_path):
    html = render(seed)
    forged = html.replace('<span class="val">60 index</span>', '<span class="val">82 index</span>')
    assert forged != html
    out = _check(forged, seed, tmp_path)
    assert any("does not contain the snapshot value" in x for x in out)


def test_gate_orphan_lead_visual_caught(seed, tmp_path):
    """A visible LEAD badge inside a non-chip cell is visual forgery."""
    html = render(seed)
    forged = html.replace(
        '<span class="val">79.2 %</span>',
        '<span class="val">79.2 %</span><span class="chip"><span class="chip-glyph">▲</span>'
        '<span class="chip-label">LEAD</span></span>',
    )
    assert forged != html
    out = _check(forged, seed, tmp_path)
    assert any("visual forgery" in x for x in out)


def test_gate_lowercase_name_and_encoded_email_caught(seed, tmp_path):
    html = render(seed)
    forged = html.replace(
        "</body>", "<p>brant&#39;s dashboard — mail me at foo&#64;bar-example.net</p></body>"
    )
    out = _check(forged, seed, tmp_path)
    assert sum(x.startswith("RULE12") for x in out) >= 2
