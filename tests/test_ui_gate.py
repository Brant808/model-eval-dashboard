"""Phase 6 UI gate — every automatable checklist item from the brief, encoded
as repeatable tests. Browser checks run offline against file:// with network
denied (any external request fails the test)."""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "model-eval-monitor.html"


@pytest.fixture(scope="module")
def html():
    assert PAGE.exists(), "build the page first (make build)"
    return PAGE.read_text(encoding="utf-8")


# ---------- static checks ----------

def test_page_weight_under_budget(html):
    assert PAGE.stat().st_size < 1_500_000  # brief: total page weight < 1.5 MB


def test_page_is_self_contained(html):
    """No build- or view-time network dependency: no external fetches at all."""
    assert "<script src" not in html
    assert "<link " not in html  # no stylesheets/preloads/favicons from network
    assert "@import" not in html
    assert not re.search(r'url\(\s*[\'"]?https?://', html)
    assert not re.search(r'src="https?://', html)
    assert "@font-face" not in html  # fallback-stack strategy, nothing fetched


def test_double_build_byte_identical(tmp_path):
    outs = []
    for i in range(2):
        out = tmp_path / f"b{i}.html"
        subprocess.run(
            [sys.executable, "site/render.py", "--data", "data/latest.json",
             "--out", str(out)],
            cwd=REPO, check=True, capture_output=True,
            env={"PYTHONHASHSEED": "random", "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        outs.append(out.read_bytes())
    assert outs[0] == outs[1]


def test_claimed_band_contract(html):
    assert html.count('data-band="claimed"') == 2
    assert "VENDOR-CLAIMED" in html


def test_movement_dots_are_shape_plus_label(html):
    # dots must be distinguishable without color: glyph + a text label
    assert '<span class="dot"' in html
    assert 'class="dot-label"' in html


def test_embedded_state_parses_and_trio_matches_snapshot(html):
    m = re.search(r'<script id="state" type="application/json">(.*?)</script>', html, re.S)
    assert m
    state = json.loads(m.group(1))
    snap = json.loads((REPO / "data" / "latest.json").read_text())
    assert state["trio"] == snap.get("default_trio", state["trio"])
    assert set(state["models"]) == set(snap["models"])


def test_contrast_wcag_aa():
    """Contrast for the page's core text/background pairs (WCAG AA >= 4.5:1
    normal text, >= 3:1 for large/bold UI text)."""

    def lum(hexc):
        r, g, b = (int(hexc[i : i + 2], 16) / 255 for i in (1, 3, 5))
        def f(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

    def ratio(a, b):
        la, lb = lum(a), lum(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    chalk, card, claim = "#f7f5f0", "#fffdf8", "#f3ead9"
    assert ratio("#1a1a1a", chalk) >= 4.5   # body ink on chalk
    assert ratio("#1e40c9", chalk) >= 4.5   # cobalt accents/text
    assert ratio("#8a2b00", chalk) >= 4.5   # warn text
    assert ratio("#8a2b00", claim) >= 4.5   # warn text on claimed band
    assert ratio("#1a1a1a", claim) >= 4.5   # ink on claimed band
    assert ratio("#555555", card) >= 4.5    # meta text on card
    assert ratio("#9a6b00", chalk) >= 3.0   # amber V tag (bold UI text)
    assert ratio("#ffffff", "#9a6b00") >= 3.0  # badge text on amber


# ---------- browser checks (offline, file://) ----------

@pytest.fixture(scope="module")
def page():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")
    with sync_playwright() as pw:
        # environment contract: use the preinstalled browser, never download
        browser = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        ctx = browser.new_context()
        # hard network denial: any non-file request aborts AND fails the test
        external = []
        def route_all(route):
            if route.request.url.startswith("file://"):
                route.fallback()
            else:
                external.append(route.request.url)
                route.abort()
        ctx.route("**/*", route_all)
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(PAGE.resolve().as_uri())
        pg.wait_for_load_state("load")
        yield pg, external, errors
        browser.close()


def test_offline_open_no_network_no_js_errors(page):
    pg, external, errors = page
    assert external == [], f"page attempted network requests: {external}"
    assert errors == [], f"JS errors: {errors}"
    assert pg.title() == "Frontier Model Eval Monitor"


def test_default_trio_and_hidden_columns(page):
    pg, _, _ = page
    snap = json.loads((REPO / "data" / "latest.json").read_text())
    trio = snap["default_trio"]
    for m in trio:
        vis = pg.eval_on_selector(f"td.col-{m}", "el => el.style.display")
        assert vis == "", m
    hidden = [m for m in snap["models"] if m not in trio]
    for m in hidden:
        vis = pg.eval_on_selector(f"td.col-{m}", "el => el.style.display")
        assert vis == "none", m


def test_picker_swap_under_100ms_no_layout_shift(page):
    pg, _, _ = page
    width_before = pg.eval_on_selector("table.compare", "el => el.offsetWidth")
    ms = pg.evaluate(
        """() => {
        const t0 = performance.now();
        document.querySelector('#picker-0 .pbtn').click();
        const opt = document.querySelector('#picker-0 .opt[data-pick="fable-5"]');
        opt.click();
        return performance.now() - t0;
        }"""
    )
    assert ms < 100, f"picker swap took {ms}ms"
    width_after = pg.eval_on_selector("table.compare", "el => el.offsetWidth")
    assert width_before == width_after  # zero layout shift
    assert "fable-5" in pg.evaluate("() => location.hash")


def test_selection_persists_via_hash_and_localstorage(page):
    pg, _, _ = page
    stored = pg.evaluate("() => localStorage.getItem('mev-trio')")
    assert stored and "fable-5" in stored
    pg.reload()
    pg.wait_for_load_state("load")
    btn = pg.text_content("#picker-0 .pbtn")
    assert "Fable 5" in btn  # survived reload via hash/localStorage


def test_keyboard_nav_core(page):
    pg, _, _ = page
    # Esc closes an open brief
    pg.click('button[data-brief="metric:aa-index"]')
    assert pg.eval_on_selector("#brief-metric-aa-index", "el => !el.hidden")
    pg.keyboard.press("Escape")
    assert pg.eval_on_selector("#brief-metric-aa-index", "el => el.hidden")
    # j moves row focus
    pg.keyboard.press("j")
    focused = pg.evaluate("() => document.activeElement.className")
    assert "rowbtn" in focused
    # 2 opens the second picker
    pg.keyboard.press("Escape")
    pg.keyboard.press("2")
    assert pg.eval_on_selector("#picker-1", "el => el.classList.contains('open')")
    pg.keyboard.press("Escape")


def test_iphone_width_two_up(page):
    pg, _, _ = page
    pg.set_viewport_size({"width": 390, "height": 844})
    # third slot hidden at mobile width; first two visible
    assert pg.eval_on_selector(
        "th[data-slot='2']", "el => getComputedStyle(el).display"
    ) == "none"
    assert pg.eval_on_selector(
        "th[data-slot='0']", "el => getComputedStyle(el).display"
    ) != "none"
    # no horizontal overflow
    overflow = pg.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 2, f"horizontal overflow {overflow}px at 390px"
    pg.set_viewport_size({"width": 1200, "height": 900})


def test_sticky_header_holds_at_depth(page):
    pg, _, _ = page
    pg.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.6)")
    top = pg.eval_on_selector(
        "thead.sticky th", "el => el.getBoundingClientRect().top"
    )
    assert -1 <= top <= 60, f"sticky header not pinned (top={top})"
    pg.evaluate("() => window.scrollTo(0, 0)")


def test_field_footnotes_capped_and_only_offscreen_winners(page):
    pg, _, _ = page
    shown = pg.evaluate(
        """() => Array.from(document.querySelectorAll('.fnrow'))
             .filter(tr => !tr.hidden)
             .map(tr => tr.getAttribute('data-fn-model'))"""
    )
    assert len(shown) <= 4
    hash_ = pg.evaluate("() => location.hash")
    for m in shown:
        assert m not in hash_
