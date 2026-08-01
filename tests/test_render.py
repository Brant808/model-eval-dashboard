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
    assert "Today's tape" in html
    assert 'data-tape-item="1"' in html
    assert 'data-health="1"' in html
    assert "chip-glyph" in html and "chip-label" in html  # shape + label, not color alone
    assert "STALE" not in html  # nothing stale in seed at seed time
    assert "⚠" in html  # integrity flags visible (Sol METR/ARC flags)
    assert "data-empty-reason" in html  # blanks are never silent


def test_forged_chip_on_vendor_cell_is_caught(seed, tmp_path):
    """Render output where a V cell displays a chip -> linter must object."""
    html = render(seed)
    # forge: flip the V-tagged SWE-bench Pro launch-claim cell's chip attr
    forged = html.replace(
        'data-cell-id="swe-bench-pro.opus-5" data-tag="V" data-stale="0" data-warn="0" data-chip="0"',
        'data-cell-id="swe-bench-pro.opus-5" data-tag="V" data-stale="0" data-warn="0" data-chip="1"',
    )
    assert forged != html, "forgery target not found — renderer contract changed"
    p = tmp_path / "forged.html"
    p.write_text(forged, encoding="utf-8")
    ledger = load_sources_ledger(REPO / "governance" / "SOURCES.md")
    out = check_html(p, seed, ledger)
    assert any(x.startswith("RULE10") for x in out)


def test_hidden_warning_tag_is_caught(seed, tmp_path):
    """Render output where an integrity-flagged cell hides its warning -> caught."""
    html = render(seed)
    forged = html.replace(
        'data-cell-id="metr-horizon.gpt-5-6-sol" data-tag="I" data-stale="0" data-warn="1"',
        'data-cell-id="metr-horizon.gpt-5-6-sol" data-tag="I" data-stale="0" data-warn="0"',
    )
    assert forged != html
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
    assert "STALE" in html
    assert 'data-cell-id="arena-elo.kimi-k3" data-tag="I" data-stale="1"' in html
