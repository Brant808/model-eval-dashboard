#!/usr/bin/env python3
"""Renderer: pure function from snapshot (+ history + briefs) to a single
self-contained HTML page — the Apple-compare paradigm per ADR-005.

Purity contract: no network, no wall-clock, no randomness; all timestamps come
from the snapshot; two runs on identical inputs are byte-identical.

Mechanics (governance/ORDERING.md, ratified with gate riders):
- three compare slots with filterable pickers (2-up at iPhone width), sticky
  compare header, quick-look band (QL-A w/ labeled fallback), grouped sections
  C1..C7 with the fold marker after C4, claimed sub-bands (machine contract:
  data-band="claimed"), field-wide chips + CO-LEAD, field-#1 footnotes
  (chip-winner-only, density-capped), movement dots, global tape, slide-over
  briefs, X-layer implications panel, pipeline-health footer, full keyboard
  navigation (1/2/3 slots, j/k rows, Enter, Esc, / filter).
- ALL catalog columns are rendered statically (linter contract + no-JS
  fallback shows the full matrix); JS only toggles column visibility, so
  picker swaps are class flips: <100ms, zero layout shift.
- Fonts: Archivo / Public Sans / IBM Plex Mono with full system fallback
  stacks — no @font-face, no fetches (self-contained + offline by
  construction).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.check_invariants import (  # noqa: E402
    compute_chips,
    integrity_flags,
    is_populated,
    parse_iso,
)

GROUP_TITLES = {
    "c1-overall": "Overall intelligence",
    "c2-agentic": "Agentic & real-economy work",
    "c3-coding": "Coding",
    "c4-econ": "Economics & adoption",
    "c5-knowledge": "Knowledge & reliability",
    "c6-headroom": "Headroom",
    "c7-integrity": "Integrity & disclosure",
    # seed-era names render too (renderer works for any snapshot)
    "independent-core": "Independent core",
    "frontier-headroom": "Frontier headroom",
    "daily-movers": "Daily movers",
    "lab-claimed": "Lab-claimed",
    "economics-deployment": "Economics and deployment",
}
FOLD_AFTER = {"c4-econ"}
QUICK_LOOK = ["aa-index", "arena-elo", "intelligence-per-dollar", "swe-rebench", "disclosure-watch"]
QUICK_LOOK_FALLBACKS = {"swe-rebench": "gdpval-aa"}
FOOTNOTE_CAP = 4


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_value(cell):
    v = cell.get("value")
    unit = cell.get("unit", "")
    if unit in ("text", "") or isinstance(v, str):
        return str(v)
    return f"{v} {unit}"


def default_trio(snap):
    if snap.get("default_trio"):
        return list(snap["default_trio"])[:3]
    best = {}
    for mid, cell in snap.get("cells", {}).get("aa-index", {}).items():
        v = cell.get("value")
        if isinstance(v, (int, float)):
            vendor = snap["models"][mid]["vendor"]
            if vendor not in best or v > best[vendor][1]:
                best[vendor] = (mid, v)
    ranked = [m for m, _ in sorted(best.values(), key=lambda t: -t[1])]
    return (ranked + [m for m in snap["models"] if m not in ranked])[:3]


def moved_models(snap):
    """Models with any cell change inside the tape window (movement dots)."""
    gen = parse_iso(snap["generated_at"])
    moved = set()
    for entry in snap.get("tape", []) + snap.get("changelog", []):
        d = entry.get("date")
        if not d:
            continue
        try:
            day = parse_iso(d + "T00:00:00Z")
        except ValueError:
            continue
        if gen - day > timedelta(hours=78):
            continue
        for cid in entry.get("cell_ids", []):
            _, _, model = cid.partition(".")
            if model in snap.get("models", {}):
                moved.add(model)
    return moved


def build_history(history_dir, snap):
    """history_ref -> [[date, value], ...] across dated snapshots (sparklines)."""
    out = {}
    if not history_dir:
        return out
    for p in sorted(Path(history_dir).glob("*.json")):
        if not re.match(r"^\d{4}-\d{2}-\d{2}(\.seed)?\.json$", p.name):
            continue
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            continue
        date = s.get("snapshot_date", p.stem)
        for metric_id, row in s.get("cells", {}).items():
            for model_id, cell in row.items():
                v = cell.get("value")
                if isinstance(v, (int, float)):
                    out.setdefault(f"{metric_id}.{model_id}", []).append([date, v])
    return out


def render_cell(metric_id, model_id, cell, chips, n_winners):
    cid = f"{metric_id}.{model_id}"
    warn = "1" if integrity_flags(cell) else "0"
    stale = "1" if cell.get("stale") else "0"
    chip = "1" if cid in chips else "0"
    cset = cell.get("comparability_set", "")
    attrs = (
        f'data-cell-id="{esc(cid)}" data-stale="{stale}" data-warn="{warn}" '
        f'data-chip="{chip}" data-set="{esc(cset)}" class="cell col-{esc(model_id)}"'
    )
    bits = []
    if is_populated(cell):
        tag = cell.get("tag", "")
        title = "independent" if tag == "I" else "vendor-claimed"
        chip_label = "CO-LEAD" if n_winners > 1 else "LEAD"
        bits.append(f'<td data-tag="{esc(tag)}" {attrs}>')
        bits.append(f'<span class="val">{esc(fmt_value(cell))}</span>')
        if cell.get("effort_tier"):
            bits.append(f'<span class="tier">tier: {esc(cell["effort_tier"])}</span>')
        bits.append(f'<span class="tag tag-{esc(tag)}" title="{title}">{esc(tag)}</span>')
        bits.append(f'<span class="src">[{esc(cell.get("source_id", ""))}]</span>')
        if chip == "1":
            bits.append(
                '<span class="chip"><span class="chip-glyph">▲</span>'
                f'<span class="chip-label">{chip_label}</span></span>'
            )
        if stale == "1":
            bits.append('<span class="stale-badge">STALE</span>')
        ifl = set(integrity_flags(cell))
        for f in cell.get("flags", []):
            if f in ifl:
                bits.append(f'<span class="warn-tag">⚠ {esc(f)}</span>')
            else:
                bits.append(f'<span class="note-tag">{esc(f)}</span>')
    else:
        reason = cell.get("empty_reason", "")
        bits.append(f'<td data-empty-reason="{esc(reason)}" {attrs}>')
        bits.append(f'<span class="empty">— <em>{esc(reason)}</em></span>')
        for f in cell.get("flags", []):
            klass = "warn-tag" if f in integrity_flags(cell) else "note-tag"
            marker = "⚠ " if klass == "warn-tag" else ""
            bits.append(f'<span class="{klass}">{marker}{esc(f)}</span>')
    bits.append("</td>")
    return "".join(bits)


CSS = """
:root{--chalk:#f7f5f0;--ink:#1a1a1a;--cobalt:#1e40c9;--amber:#9a6b00;--line:#d8d4ca;
--warn:#8a2b00;--claim-bg:#f3ead9;--card:#fffdf8}
*{box-sizing:border-box}
body{background:var(--chalk);color:var(--ink);margin:0;padding:0 12px 4rem;
font-family:'Public Sans','Helvetica Neue',Arial,system-ui,-apple-system,'Segoe UI',sans-serif;
font-size:15px;line-height:1.35}
h1,h2,h3{font-family:'Archivo','Arial Narrow','Helvetica Neue',Arial,system-ui,sans-serif;letter-spacing:-.01em}
code,.val,.src,.ql-num{font-family:'IBM Plex Mono',ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace}
a{color:var(--cobalt)}
.wrap{max-width:1080px;margin:0 auto}
header.page{padding:1rem 0 .4rem;border-bottom:3px solid var(--cobalt)}
header.page h1{margin:0;font-size:1.35rem}
.meta{color:#555;font-size:.8rem;margin:.25rem 0}
.legend{font-size:.72rem;color:#444;margin:.3rem 0;line-height:1.6}
.tag{font-weight:700;border:1px solid;border-radius:3px;padding:0 .28rem;margin-left:.3rem;font-size:.68rem;display:inline-block}
.tag-I{color:var(--cobalt);border-color:var(--cobalt)}
.tag-V{color:var(--amber);border-color:var(--amber)}
.tape{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--amber);
padding:.5rem .8rem;margin:.8rem 0;font-size:.82rem}
.tape ul{margin:.3rem 0 0;padding-left:1.1rem}
.tape li{margin-bottom:.3rem}
.tape .src{color:#888;font-size:.7rem}
.qlook{display:grid;grid-template-columns:12rem repeat(3,1fr);gap:.1rem 8px;background:var(--card);
border:1px solid var(--line);padding:.6rem .8rem;margin:.8rem 0;font-size:.85rem}
.qlook .ql-h{font-weight:700;font-size:.75rem;color:#555;text-transform:uppercase;letter-spacing:.04em}
.qlook .ql-num{font-size:1.02rem;font-weight:600}
/* trust badges added to ql cells must wrap inside their grid track, never
   widen it (390px two-up overflowed when the badges landed) */
.qlook>div{min-width:0;overflow-wrap:anywhere}
.ql-cap{grid-column:1/-1;font-size:.7rem;color:#666;border-top:1px dashed var(--line);margin-top:.3rem;padding-top:.3rem}
.ql-slot-label{font-size:.66rem;color:#666;text-transform:none;letter-spacing:0}
table.compare{border-collapse:collapse;width:100%;margin:0 0 .4rem}
table.compare th,table.compare td{border:1px solid var(--line);padding:.38rem .5rem;vertical-align:top;
font-size:.83rem;text-align:left;width:24%}
table.compare th.rowh{width:28%;background:#efece3;font-weight:600}
table.compare th.grouph{background:var(--chalk)}
thead.sticky th{position:sticky;top:0;background:var(--chalk);z-index:5;border-bottom:2px solid var(--cobalt)}
.picker{width:100%;position:relative}
.picker>button{width:100%;text-align:left;font:inherit;font-weight:700;padding:.3rem .4rem;
background:var(--card);border:1px solid var(--line);border-radius:4px;cursor:pointer}
.picker>button:focus{outline:2px solid var(--cobalt)}
.picker .pop{display:none;position:absolute;left:0;right:0;top:100%;background:#fff;
border:1px solid var(--line);z-index:20;max-height:16rem;overflow:auto;box-shadow:0 4px 14px rgba(0,0,0,.15)}
.picker.open .pop{display:block}
.picker input{width:100%;border:0;border-bottom:1px solid var(--line);padding:.3rem .4rem;font:inherit}
.picker .grp{font-size:.65rem;color:#777;text-transform:uppercase;padding:.25rem .4rem 0}
.picker .opt{display:block;width:100%;text-align:left;border:0;background:none;font:inherit;
padding:.3rem .5rem;cursor:pointer}
.picker .opt:hover,.picker .opt:focus{background:#eef1fb}
.dot{display:inline-block;width:.5em;height:.5em;border-radius:50%;background:var(--amber);
border:1px solid var(--ink);margin-right:.3rem;vertical-align:baseline}
.dot-label{font-size:.62rem;color:var(--amber);font-weight:700}
tr[data-band=claimed] td,tr[data-band=claimed] th.rowh{background:var(--claim-bg)}
.claim-band-label{background:var(--amber);color:#fff;font-size:.6rem;padding:.05rem .3rem;
border-radius:3px;letter-spacing:.05em;display:inline-block;margin-right:.3rem}
.val{font-weight:600}
.tier{display:block;font-size:.7rem;color:#444}
.src{color:#999;font-size:.68rem;margin-left:.25rem}
.chip{margin-left:.3rem;font-size:.68rem;font-weight:700;color:var(--cobalt);white-space:nowrap}
.stale-badge{background:var(--amber);color:#fff;font-size:.62rem;padding:0 .3rem;margin-left:.3rem;border-radius:3px}
.warn-tag{display:block;color:var(--warn);font-size:.7rem;margin-top:.15rem}
.note-tag{display:block;color:#666;font-size:.7rem;margin-top:.15rem}
.empty em{color:#777}
.fieldnote{font-size:.7rem;color:#555;border-left:3px solid var(--line)}
.fold{text-align:center;color:#777;font-size:.72rem;border-bottom:2px dashed var(--amber);
padding:.35rem 0 .25rem}
.imps{background:#eef1fb;border:1px solid var(--cobalt);border-radius:4px;padding:.6rem .8rem;margin:1rem 0}
.imps h2{margin:.1rem 0 .4rem;font-size:.9rem}
.imps ul{margin:0;padding-left:1.1rem}
.imps li{margin-bottom:.45rem;font-size:.82rem}
.imps .x{font-weight:800;color:var(--cobalt)}
.imps em{color:#444;font-size:.76rem}
.rowbtn,.modelbtn{background:none;border:0;font:inherit;font-weight:inherit;color:inherit;
cursor:pointer;text-decoration:underline dotted;padding:0;text-align:left}
.brief{position:fixed;top:0;right:0;bottom:0;width:min(30rem,92vw);background:#fff;
border-left:3px solid var(--cobalt);box-shadow:-6px 0 20px rgba(0,0,0,.2);z-index:50;
transform:translateX(105%);transition:transform .12s ease-out;overflow:auto;padding:1rem}
.brief.open{transform:none}
.brief h3{margin-top:0}
.brief .close{float:right;font-size:.9rem;background:none;border:1px solid var(--line);
border-radius:4px;cursor:pointer;padding:.1rem .5rem}
.brief dl{font-size:.82rem}
.brief dt{font-weight:700;margin-top:.5rem}
.brief dd{margin:0 0 .2rem}
.spark{stroke:var(--cobalt);fill:none;stroke-width:1.5}
.sparkdot{fill:var(--amber)}
footer.health{border-top:2px solid var(--cobalt);margin-top:1.6rem;padding-top:.5rem;font-size:.78rem;color:#555}
footer.health code{font-size:.74rem}
.kbd{font-size:.68rem;color:#777;margin:.4rem 0 0}
kbd{border:1px solid var(--line);border-bottom-width:2px;border-radius:3px;padding:0 .25rem;
font-size:.68rem;background:#fff}
@media (max-width:700px){
  .hide-mobile-slot{display:none!important}
  .qlook{grid-template-columns:7.2rem repeat(2,1fr);font-size:.78rem}
  table.compare th,table.compare td{font-size:.76rem;padding:.3rem .35rem}
  /* fixed layout: long flag strings (contamination/accrual caveats) must
     wrap inside their column, never widen the table — a swap to the model
     with the heaviest flag load overflowed 236px at 390px (gate catch) */
  table.compare{table-layout:fixed;width:100%}
  table.compare th,table.compare td{overflow-wrap:anywhere}
  body{font-size:14px}
}
@media (prefers-reduced-motion:reduce){.brief{transition:none}}
"""

JS = r"""
(function(){
"use strict";
var stateEl=document.getElementById('state');
if(!stateEl){return;}
var state=JSON.parse(stateEl.textContent);
var slots=state.trio.slice(0,3);
function readSaved(){
  var m=(location.hash.match(/m=([a-zA-Z0-9,\-]+)/)||[])[1];
  if(m){var arr=m.split(',').filter(function(x){return state.models.indexOf(x)>=0;});
    if(arr.length>=2){return arr.slice(0,3);}}
  try{var ls=localStorage.getItem('mev-trio');
    if(ls){var a=JSON.parse(ls).filter(function(x){return state.models.indexOf(x)>=0;});
      if(a.length>=2){return a.slice(0,3);}}}catch(e){}
  return null;
}
function fill(arr){var out=arr.slice(0,3);
  state.models.forEach(function(m){if(out.length<3&&out.indexOf(m)<0){out.push(m);}});
  return out;}
var saved=readSaved(); if(saved){slots=fill(saved);}
function persist(){
  try{localStorage.setItem('mev-trio',JSON.stringify(slots));}catch(e){}
  var h='m='+slots.join(',');
  if(location.hash.slice(1)!==h){history.replaceState(null,'','#'+h);}
}
function apply(){
  state.models.forEach(function(m){
    var show=slots.indexOf(m);
    document.querySelectorAll('.col-'+m).forEach(function(td){
      td.style.display=show<0?'none':'';
      td.classList.toggle('hide-mobile-slot',show===2);
    });
  });
  document.querySelectorAll('.picker').forEach(function(p){
    var i=+p.getAttribute('data-slot');
    var b=p.querySelector('.pbtn');
    var movedMark=state.moved.indexOf(slots[i])>=0?
      '<span class="dot" aria-hidden="true"></span><span class="dot-label">moved </span>':'';
    b.innerHTML=movedMark+state.names[slots[i]]+' <span style="float:right">▾</span>';
    var th=p.closest('th'); if(th){th.classList.toggle('hide-mobile-slot',i===2);}
  });
  document.querySelectorAll('.ql-model').forEach(function(el){
    var i=+el.getAttribute('data-slot');el.textContent=state.names[slots[i]]||'';
    el.classList.toggle('hide-mobile-slot',i===2);
  });
  document.querySelectorAll('[data-ql]').forEach(function(el){
    var mid=el.getAttribute('data-ql'),i=+el.getAttribute('data-slot');
    var c=(state.ql[mid]||{})[slots[i]];
    el.classList.toggle('hide-mobile-slot',i===2);
    if(!c){el.textContent='';el.removeAttribute('data-tag');el.removeAttribute('data-stale');el.removeAttribute('data-warn');return;}
    if(c.v===null||c.v===undefined){
      el.innerHTML='<span class="ql-empty">— '+(c.reason||'not published')+'</span>';
      el.setAttribute('data-tag','');el.setAttribute('data-stale','0');el.setAttribute('data-warn','0');
      return;
    }
    var h=c.v+(c.tag?' <span class="tag tag-'+c.tag+'">'+c.tag+'</span>':'');
    if(c.warn){h+='<span class="warn-tag" title="integrity flag on this cell — see the table row">⚠</span>';}
    if(c.stale){h+='<span class="stale-badge">STALE</span>';}
    el.innerHTML=h;
    el.setAttribute('data-tag',c.tag||'');
    el.setAttribute('data-stale',c.stale?'1':'0');
    el.setAttribute('data-warn',c.warn?'1':'0');
  });
  var shown=0;
  document.querySelectorAll('.fnrow').forEach(function(tr){
    var w=tr.getAttribute('data-fn-model');
    var show=slots.indexOf(w)<0&&shown<state.fncap;
    tr.hidden=!show; if(show){shown++;}
  });
  persist();
}
function closePops(){document.querySelectorAll('.picker.open').forEach(function(p){p.classList.remove('open');});}
document.querySelectorAll('.picker').forEach(function(p){
  var slot=+p.getAttribute('data-slot');
  var btn=p.querySelector('.pbtn'),inp=p.querySelector('input');
  function filter(q){q=q.toLowerCase();
    p.querySelectorAll('.opt').forEach(function(o){
      o.style.display=o.textContent.toLowerCase().indexOf(q)>=0?'':'none';});}
  function pick(m){
    var other=slots.indexOf(m);
    if(other>=0&&other!==slot){slots[other]=slots[slot];}
    slots[slot]=m;closePops();apply();btn.focus();
  }
  btn.addEventListener('click',function(){var o=p.classList.contains('open');closePops();
    if(!o){p.classList.add('open');inp.value='';filter('');inp.focus();}});
  inp.addEventListener('input',function(){filter(inp.value);});
  inp.addEventListener('keydown',function(e){
    if(e.key==='Enter'){var first=null;
      p.querySelectorAll('.opt').forEach(function(o){
        if(!first&&o.style.display!=='none'){first=o;}});
      if(first){pick(first.getAttribute('data-pick'));}e.preventDefault();}
    if(e.key==='Escape'){closePops();btn.focus();e.stopPropagation();}
  });
  p.querySelectorAll('.opt').forEach(function(o){
    o.addEventListener('click',function(){pick(o.getAttribute('data-pick'));});
  });
});
var briefOpen=null;
function openBrief(id){var el=document.getElementById(id);if(!el){return;}
  if(briefOpen){closeBrief();}
  el.hidden=false;requestAnimationFrame(function(){el.classList.add('open');});
  briefOpen=el;el.querySelector('.close').focus();}
function closeBrief(){if(!briefOpen){return;}var el=briefOpen;el.classList.remove('open');
  el.hidden=true;briefOpen=null;}
document.querySelectorAll('[data-brief]').forEach(function(b){
  b.addEventListener('click',function(){
    var t=b.getAttribute('data-brief').split(':');openBrief('brief-'+t[0]+'-'+t[1]);});
});
document.querySelectorAll('.brief .close').forEach(function(c){
  c.addEventListener('click',closeBrief);
});
var rows=Array.prototype.slice.call(document.querySelectorAll('tr.mrow'));
var cur=-1;
function focusRow(i){
  if(i<0||i>=rows.length){return;}
  if(cur>=0){rows[cur].style.outline='';}
  cur=i;var r=rows[cur];r.style.outline='2px solid #1e40c9';
  r.scrollIntoView({block:'nearest'});
  var rb=r.querySelector('.rowbtn');if(rb){rb.focus({preventScroll:true});}
}
document.addEventListener('keydown',function(e){
  if(e.target.tagName==='INPUT'){return;}
  if(e.key==='Escape'){closeBrief();closePops();return;}
  if(briefOpen){return;}
  if(e.key==='1'||e.key==='2'||e.key==='3'){
    var p=document.getElementById('picker-'+(+e.key-1));
    if(p){p.querySelector('.pbtn').click();e.preventDefault();}return;}
  if(e.key==='j'||e.key==='ArrowDown'){focusRow(cur+1);e.preventDefault();}
  if(e.key==='k'||e.key==='ArrowUp'){focusRow(cur-1);e.preventDefault();}
  if(e.key==='/'){var open=document.querySelector('.picker.open input');
    if(open){open.focus();}else{var pk=document.getElementById('picker-0');
      if(pk){pk.querySelector('.pbtn').click();}}
    e.preventDefault();}
});
document.addEventListener('click',function(e){
  if(!e.target.closest('.picker')){closePops();}
});
window.addEventListener('hashchange',function(){var h=readSaved();if(h){slots=fill(h);apply();}});
apply();
})();
"""


def render(snap, history=None, briefs=None) -> str:
    briefs = briefs or {"metrics": {}, "models": {}}
    history = history or {}
    models = snap["models"]
    metrics = snap["metrics"]
    cells = snap["cells"]
    chips = compute_chips(snap)
    trio = default_trio(snap)
    moved = moved_models(snap)
    model_ids = list(models.keys())

    out = []
    A = out.append
    A("<!DOCTYPE html>")
    A('<html lang="en"><head><meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1">')
    A("<title>Frontier Model Eval Monitor</title>")
    A(f"<style>{CSS}</style></head><body>")
    A('<div class="wrap">')

    # ---------- header + legend ----------
    A('<header class="page"><h1>Frontier Model Eval Monitor</h1>')
    A(
        f'<p class="meta">Data generated <code>{esc(snap["generated_at"])}</code> · '
        f'snapshot <code>{esc(snap["snapshot_date"])}</code></p>'
    )
    A(
        '<p class="legend"><span class="tag tag-I">I</span> measured independently &nbsp; '
        '<span class="tag tag-V">V</span> vendor-declared — plain V is a first-party fact '
        '(e.g. a list price, marked “vendor-listed fact”); rows under '
        '<span class="claim-band-label">VENDOR-CLAIMED</span> are performance claims graded '
        'by the vendor itself, quarantined below the fold. '
        '▲LEAD = best in the tracked field among independent, unflagged values '
        '(▲CO-LEAD when tied); ⚠ = integrity warning; '
        '<span class="stale-badge">STALE</span> = older than the source’s freshness window. '
        'Blanks always state their reason.</p>'
    )
    A(
        '<p class="kbd">Keys: <kbd>1</kbd><kbd>2</kbd><kbd>3</kbd> pick a column · '
        "<kbd>j</kbd>/<kbd>k</kbd> move rows · <kbd>Enter</kbd> open details · "
        "<kbd>/</kbd> filter a picker · <kbd>Esc</kbd> close</p>"
    )
    A("</header>")

    # ---------- tape ----------
    A('<div class="tape"><strong>Today’s tape</strong> — field-wide moves, last ~72h')
    A("<ul>")
    for entry in snap.get("tape", []):
        A(
            f'<li data-tape-item="1" data-tape-date="{esc(entry["date"])}" '
            f'data-tape-src="{esc(entry["source_id"])}">'
            f'<strong>{esc(entry["date"])}</strong> — {esc(entry["text"])} '
            f'<span class="src">[{esc(entry["source_id"])}]</span></li>'
        )
    if not snap.get("tape"):
        A("<li><em>No moves recorded in the last 72 hours.</em></li>")
    A("</ul></div>")

    # ---------- quick look ----------
    ql_rows = []
    for mid in QUICK_LOOK:
        actual = mid
        label_extra = ""
        if mid not in cells and mid in QUICK_LOOK_FALLBACKS:
            actual = QUICK_LOOK_FALLBACKS[mid]
            label_extra = (
                ' <span class="ql-slot-label">(slot: GDPval until SWE-rebench '
                "tracking begins)</span>"
            )
        if actual in cells and actual in metrics:
            ql_rows.append((actual, label_extra))
    A('<div class="qlook" id="qlook">')
    A('<div class="ql-h">Quick look</div>')
    for i in range(3):
        A(f'<div class="ql-h ql-model" data-slot="{i}"></div>')
    for actual, extra in ql_rows:
        A(f'<div class="ql-h">{esc(metrics[actual].get("name", actual))}{extra}</div>')
        for i in range(3):
            A(f'<div class="ql-num" data-ql="{esc(actual)}" data-slot="{i}"></div>')
    aa = cells.get("aa-index", {})
    ranked = sorted(
        (
            (models[m]["name"], c.get("value"))
            for m, c in aa.items()
            if isinstance(c.get("value"), (int, float))
        ),
        key=lambda t: -t[1],
    )
    if ranked:
        cap = " · ".join(f"{i + 1} {esc(n)} {v}" for i, (n, v) in enumerate(ranked))
        A(
            f'<div class="ql-cap">Field order (AA Index): {cap}. '
            "Default columns: top model per vendor.</div>"
        )
    A("</div>")

    # ---------- implications (X layer) ----------
    if snap.get("implications"):
        A('<div class="imps"><h2>Read — interpretation layer (X)</h2><ul>')
        for imp in snap["implications"]:
            fl = imp.get("flags_carried", [])
            if len(fl) > 2:
                flags_txt = (
                    f'<details><summary class="warn-tag">⚠×{len(fl)} integrity flags '
                    "carried (expand)</summary>"
                    + "".join(f'<span class="warn-tag">⚠ {esc(f)}</span>' for f in fl)
                    + "</details>"
                )
            else:
                flags_txt = "".join(f'<span class="warn-tag">⚠ {esc(f)}</span>' for f in fl)
            lens = imp.get("lens", "")
            status = imp.get("status")
            if status == "OPEN":
                open_badge = '<span class="claim-band-label" style="background:#555">OPEN</span> '
            elif status == "under review":
                # rot state (gate rider): cited cells moved since this was
                # stated; the read is suspect until re-adjudicated
                open_badge = ('<span class="claim-band-label" style="background:#8a2b00">'
                              "UNDER REVIEW — cited cells moved</span> ")
            else:
                open_badge = ""
            A(
                f'<li data-imp-id="{esc(imp["id"])}" data-imp-tag="{esc(imp.get("tag", ""))}" '
                f'data-imp-conf="{esc(imp.get("confidence", ""))}" '
                f'data-imp-falsifier="{esc(imp.get("falsifier", ""))}">'
                f'<span class="x">[X{(" · " + esc(lens)) if lens else ""}]</span> {open_badge}'
                f'{esc(imp["text"])} '
                f'<em>confidence {esc(imp.get("confidence", ""))} · since '
                f'{esc(imp.get("first_stated", imp.get("date", snap["snapshot_date"])))} · '
                f'reverses if: {esc(imp.get("falsifier", ""))}</em> '
                f'<span class="src">cites {esc(", ".join(imp.get("cites", [])))}</span>'
                f"{flags_txt}</li>"
            )
        A("</ul></div>")

    # ---------- compare table ----------
    # Canonical C1..C7 order (ADR-005), NOT first-seen order: the registry
    # dict interleaves groups (SWE-Pro's c7 entry sits between c3 and c4
    # metrics), which rendered "Integrity" fourth on the shipped page
    # (phase-6 gate BLOCKING — the page was neither ordering C nor D).
    groups = []
    for metric_id, meta in metrics.items():
        if meta.get("brief_layer"):
            continue
        g = meta.get("group", "other")
        if g not in groups:
            groups.append(g)
    canon = list(GROUP_TITLES)
    groups.sort(key=lambda g: (canon.index(g) if g in canon else len(canon), g))

    def picker_html(slot):
        opts = []
        current = [m for m in model_ids if models[m].get("status", "current") == "current"]
        older = [m for m in model_ids if models[m].get("status", "current") != "current"]
        for label, group in (("Current frontier", current), ("Recent & superseded", older)):
            if not group:
                continue
            opts.append(f'<div class="grp">{esc(label)}</div>')
            for m in group:
                dot = (
                    '<span class="dot" aria-hidden="true"></span>'
                    '<span class="dot-label">moved </span>'
                    if m in moved
                    else ""
                )
                opts.append(
                    f'<button class="opt" data-pick="{esc(m)}" role="option">{dot}'
                    f"{esc(models[m]['name'])}</button>"
                )
        return (
            f'<div class="picker" id="picker-{slot}" data-slot="{slot}">'
            f'<button class="pbtn" aria-haspopup="listbox" '
            f'title="change model (key {slot + 1})">{esc(models[model_ids[min(slot, len(model_ids)-1)]]["name"])}</button>'
            f'<div class="pop" role="listbox">'
            f'<input type="text" placeholder="/ filter…" aria-label="filter models">'
            + "".join(opts)
            + "</div></div>"
        )

    A('<table class="compare"><thead class="sticky"><tr>')
    A('<th class="rowh">Metric</th>')
    for i in range(3):
        A(f'<th data-slot="{i}">{picker_html(i)}</th>')
    A("</tr></thead>")

    for g in groups:
        A(f'<tbody class="grp" data-group="{esc(g)}">')
        A(
            f'<tr class="grow"><th class="rowh grouph" colspan="4">'
            f"<h2 style=\"margin:.2rem 0;font-size:.95rem\">{esc(GROUP_TITLES.get(g, g))}</h2></th></tr>"
        )
        for metric_id, meta in metrics.items():
            if meta.get("group") != g or meta.get("brief_layer"):
                continue
            row_cells = cells.get(metric_id, {})
            row_sets = sorted({c.get("comparability_set", "") for c in row_cells.values()})
            claim = ' data-band="claimed"' if meta.get("claim_v") else ""
            band_label = (
                '<span class="claim-band-label">VENDOR-CLAIMED</span>'
                if meta.get("claim_v")
                else ""
            )
            price_cap = (
                ' <span class="note-tag">vendor-listed fact</span>'
                if metric_id == "api-price"
                else ""
            )
            winners = sorted(c for c in chips if c.startswith(metric_id + "."))
            A(
                f'<tr data-metric="{esc(metric_id)}" '
                f'data-row-set="{esc("|".join(row_sets))}"{claim} class="mrow">'
                f'<th class="rowh">{band_label}'
                f'<button class="rowbtn" data-brief="metric:{esc(metric_id)}">'
                f"{esc(meta['name'])}</button>{price_cap}</th>"
            )
            for model_id in model_ids:
                cell = row_cells.get(model_id)
                if cell is None:
                    A(f'<td class="cell col-{esc(model_id)}">—</td>')
                else:
                    A(render_cell(metric_id, model_id, cell, chips, len(winners)))
            A("</tr>")
            if winners:
                w_model = winners[0].split(".", 1)[1]
                w_cell = row_cells.get(w_model, {})
                A(
                    f'<tr class="fnrow" data-fn-metric="{esc(metric_id)}" '
                    f'data-fn-model="{esc(w_model)}" hidden>'
                    f'<td colspan="4" class="fieldnote">▲ field #1: '
                    f"{esc(models[w_model]['name'])} {esc(fmt_value(w_cell))} "
                    f'<span class="tag tag-{esc(w_cell.get("tag", ""))}">'
                    f'{esc(w_cell.get("tag", ""))}</span> (not in view)</td></tr>'
                )
        A("</tbody>")
        if g in FOLD_AFTER:
            A(
                '<tbody><tr><td colspan="4" class="fold" data-fold="1">below: slow boards '
                "and claims — the tape flags any change</td></tr></tbody>"
            )
    A("</table>")

    # ---------- watch ----------
    if snap.get("watch"):
        A('<section class="grp"><h2 style="font-size:.95rem">New-model watch</h2><ul>')
        for w in snap["watch"]:
            srcs = (
                f", sources {esc(', '.join(w['seen_in_sources']))}"
                if w.get("seen_in_sources")
                else ""
            )
            A(
                f'<li><strong>{esc(w["name"])}</strong> (first seen {esc(w["first_seen"])}'
                f"{srcs}) — {esc(w['note'])}</li>"
            )
        A("</ul></section>")

    # ---------- briefs (slide-overs) ----------
    def spark_svg(ref):
        pts = history.get(ref, [])
        if len(pts) < 2:
            return "<em>sparkline appears once history accrues</em>"
        vals = [v for _, v in pts][-30:]
        lo, hi = min(vals), max(vals)
        rng = (hi - lo) or 1.0
        w, h = 180, 36
        step = w / max(len(vals) - 1, 1)
        coords = " ".join(
            f"{round(i * step, 1)},{round(h - 4 - (v - lo) / rng * (h - 8), 1)}"
            for i, v in enumerate(vals)
        )
        lx, ly = coords.rsplit(" ", 1)[-1].split(",")
        return (
            f'<svg width="{w}" height="{h}" role="img" aria-label="trend, {len(vals)} points">'
            f'<polyline class="spark" points="{coords}"/>'
            f'<circle class="sparkdot" cx="{lx}" cy="{ly}" r="2.5"/></svg>'
        )

    mb = briefs.get("metrics", {})
    for metric_id, meta in metrics.items():
        b = mb.get(metric_id, {})
        A(
            f'<aside class="brief" id="brief-metric-{esc(metric_id)}" role="dialog" '
            f'aria-label="{esc(meta["name"])} details" hidden>'
        )
        A('<button class="close" aria-label="close">✕ esc</button>')
        A(f"<h3>{esc(meta['name'])}</h3><dl>")
        for key, label in (
            ("what", "What it measures"),
            ("harness", "Harness & version"),
            ("cadence", "Cadence & freshness"),
            ("independence", "Independence"),
        ):
            if b.get(key):
                A(f"<dt>{esc(label)}</dt><dd>{esc(b[key])}</dd>")
        if b.get("integrity"):
            A("<dt>Known integrity issues</dt>")
            for item in b["integrity"]:
                A(f'<dd><span class="warn-tag">⚠ {esc(item)}</span></dd>')
        if b.get("comparability"):
            A(f"<dt>Comparability</dt><dd>{esc(b['comparability'])}</dd>")
        A("<dt>Current values</dt>")
        for model_id in model_ids:
            cell = cells.get(metric_id, {}).get(model_id)
            if cell is None:
                continue
            shown = (
                fmt_value(cell)
                if is_populated(cell)
                else f"— {cell.get('empty_reason', '')}"
            )
            src = f" [{cell.get('source_id')}]" if cell.get("source_id") else ""
            ret = f" · as of {cell['retrieved_at'][:10]}" if cell.get("retrieved_at") else ""
            A(
                f"<dd><strong>{esc(models[model_id]['name'])}</strong>: {esc(shown)}"
                f"{esc(src)}{esc(ret)} {spark_svg(f'{metric_id}.{model_id}')}</dd>"
            )
        A(
            f"<dt>Freshness SLA</dt><dd>{esc(meta.get('freshness_sla_hours', '?'))}h · "
            f"primary source {esc(meta.get('primary_source_id', ''))} "
            f"(full provenance ledger ships in the repo)</dd>"
        )
        A("</dl></aside>")

    modb = briefs.get("models", {})
    for model_id, m in models.items():
        b = modb.get(model_id, {})
        A(
            f'<aside class="brief" id="brief-model-{esc(model_id)}" role="dialog" '
            f'aria-label="{esc(m["name"])} details" hidden>'
        )
        A('<button class="close" aria-label="close">✕ esc</button>')
        A(f"<h3>{esc(m['name'])}</h3><dl>")
        A(f"<dt>Vendor</dt><dd>{esc(m['vendor'])}</dd>")
        for key, label in (
            ("release", "Release"),
            ("context_window", "Context window"),
            ("pricing", "Pricing"),
            ("price_moves", "Recent price moves"),
            ("deployment_terms", "Deployment & data terms"),
        ):
            if b.get(key):
                A(f"<dt>{esc(label)}</dt><dd>{esc(b[key])}</dd>")
        A("<dt>Eval coverage</dt>")
        pop = sum(
            1
            for mid2 in metrics
            if is_populated(cells.get(mid2, {}).get(model_id, {}))
        )
        A(f"<dd>{pop} of {len(metrics)} tracked metrics populated.</dd>")
        if b.get("coverage_gaps"):
            A(f"<dd>{esc(b['coverage_gaps'])}</dd>")
        for mid2 in metrics:
            cell = cells.get(mid2, {}).get(model_id)
            if cell is not None and not is_populated(cell):
                A(
                    f"<dd><em>{esc(metrics[mid2]['name'])}: "
                    f"{esc(cell.get('empty_reason', ''))}</em></dd>"
                )
        A("</dl></aside>")

    # ---------- health footer ----------
    health = snap.get("health", {})
    A('<footer class="health" data-health="1">')
    A(
        f'<p>Pipeline health: run <code>{esc(health.get("run_status", "unknown"))}</code> · '
        f'judgment layer <code>{esc(health.get("judgment_layer", "unknown"))}</code> · '
        f'data generated <code>{esc(snap["generated_at"])}</code> · '
        "constitution: 12 rules enforced at build (the page cannot publish on violation).</p>"
    )
    if health.get("sources"):
        A(
            "<p>Sources: "
            + " · ".join(
                f"<code>{esc(sid)}</code> "
                + ("DOWN" if str(status).startswith("DOWN") else "ok")
                for sid, status in health["sources"].items()
            )
            + "</p>"
        )
    A(
        "<p>Attribution: Artificial Analysis · Arena/LMArena leaderboard data (CC-BY-4.0) · "
        "Epoch AI (CC-BY) · ARC Prize · METR · Terminal-Bench (Apache-2.0 data) · llm-stats · "
        "OpenRouter · Scale · SWE-rebench (Nebius) · Vals AI · LiveBench.</p>"
    )
    A("</footer>")
    A("</div>")

    # ---------- embedded state + JS ----------
    state = {
        "models": model_ids,
        "names": {m: models[m]["name"] for m in model_ids},
        "trio": trio,
        "moved": sorted(moved),
        # Quick-look cells carry the same trust metadata as table cells —
        # a naked number at the top of the page presented a stale/claimed
        # value as fresh, gate-green (phase-6 red-team BLOCKING). The linter
        # verifies this state block against the snapshot cell-for-cell.
        "ql": {
            actual: {
                m: (
                    {
                        "v": fmt_value(cells[actual][m]),
                        "tag": cells[actual][m].get("tag"),
                        "stale": 1 if cells[actual][m].get("stale") else 0,
                        "warn": 1 if integrity_flags(cells[actual][m]) else 0,
                    }
                    if is_populated(cells[actual].get(m, {}))
                    else {
                        "v": None,
                        "reason": cells[actual][m].get("empty_reason", "not published"),
                    }
                )
                for m in model_ids
                if m in cells.get(actual, {})
            }
            for actual, _ in ql_rows
        },
        "fncap": FOOTNOTE_CAP,
    }
    A(
        f'<script id="state" type="application/json">'
        f"{json.dumps(state, sort_keys=True)}</script>"
    )
    A("<script>" + JS + "</script>")
    A("</body></html>")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--briefs", default=str(REPO / "data" / "briefs.json"))
    ap.add_argument("--history-dir", default=str(REPO / "data"))
    args = ap.parse_args(argv)

    def reject(c):
        raise ValueError(f"non-finite constant {c!r}")

    snap = json.loads(Path(args.data).read_text(encoding="utf-8"), parse_constant=reject)
    briefs = {}
    bp = Path(args.briefs)
    if bp.exists():
        briefs = json.loads(bp.read_text(encoding="utf-8"), parse_constant=reject)
    history = build_history(args.history_dir, snap)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(snap, history, briefs), encoding="utf-8")
    print(f"render: wrote {args.out} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
