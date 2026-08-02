"""Machine form of the ratified metric registry (governance/ROWS.md) and
ordering (governance/ORDERING.md). run.py builds snapshots from this; the
renderer reads groups/order from the snapshot it is given (staying pure).

Matrix rows render in the compare table; brief-layer metrics are collected and
appear only in briefs/quick-look. Group ids follow ORDERING.md D1.
"""

GROUPS = [
    ("c1-overall", "Overall intelligence"),
    ("c2-agentic", "Agentic & real-economy work"),
    ("c3-coding", "Coding"),
    ("c4-econ", "Economics & adoption"),
    ("c5-knowledge", "Knowledge & reliability"),
    ("c6-headroom", "Headroom"),
    ("c7-integrity", "Integrity & disclosure"),
    ("brief-layer", "Brief layer (not matrix-rendered)"),
]

# metric_id -> meta. Order within this dict IS render order (top to bottom).
METRICS = {
    # C1
    "aa-index": dict(name="AA Intelligence Index v4.1", group="c1-overall", unit="index",
                     comparability_set="aa-index-v4.1", direction="higher",
                     freshness_sla_hours=72, primary_source_id="S1",
                     empty_default="not published"),
    "epoch-eci": dict(name="Epoch Capabilities Index", group="c1-overall", unit="index",
                      comparability_set="epoch-eci", direction="higher",
                      freshness_sla_hours=336, primary_source_id="S10",
                      empty_default="not published"),
    "arena-elo": dict(name="Arena text Elo (Style Control board)", group="c1-overall", unit="Elo",
                      comparability_set="arena-text-style-control", direction="higher",
                      freshness_sla_hours=96, primary_source_id="S2",
                      empty_default="not published"),
    # C2
    "gdpval-aa": dict(name="GDPval-AA v2", group="c2-agentic", unit="Elo",
                      comparability_set="gdpval-aa-v2", direction="higher",
                      freshness_sla_hours=72, primary_source_id="S1",
                      empty_default="not published"),
    "aa-agentic-index": dict(name="AA Agentic Index", group="c2-agentic", unit="index",
                             comparability_set="aa-agentic-index-v4.1", direction="higher",
                             freshness_sla_hours=72, primary_source_id="S1",
                             empty_default="not published"),
    "vals-index": dict(name="Vals professional index", group="c2-agentic", unit="index",
                       comparability_set="vals-index-composite", direction="higher",
                       freshness_sla_hours=504, primary_source_id="S11",
                       empty_default="not published"),
    "terminal-bench": dict(name="Terminal-Bench 2.1", group="c2-agentic", unit="%",
                           comparability_set="terminal-bench-2.1", direction="higher",
                           freshness_sla_hours=1080, primary_source_id="S8",
                           empty_default="not published"),
    # C3
    "swe-rebench": dict(name="SWE-rebench (fresh issues)", group="c3-coding", unit="%",
                        comparability_set="swe-rebench-window-2026-05-15", direction="higher",
                        freshness_sla_hours=1080, primary_source_id="S20",
                        empty_default="not evaluated"),
    "swe-bench-pro": dict(name="SWE-bench Pro (vendor claims)", group="c7-integrity", unit="%",
                          comparability_set="swe-bench-pro-vendor-aggregate", direction="higher",
                          freshness_sla_hours=72, primary_source_id="S13",
                          empty_default="not published", claim_v=True),
    # C4
    "intelligence-per-dollar": dict(name="Intelligence per dollar", group="c4-econ",
                                    unit="index pts per task-USD",
                                    comparability_set="aa-intelligence-per-usd", direction="higher",
                                    freshness_sla_hours=72, primary_source_id="S1",
                                    empty_default="not published"),
    "cost-per-task": dict(name="Cost per task", group="c4-econ", unit="USD/task",
                          comparability_set="aa-cost-per-task", direction="lower",
                          freshness_sla_hours=72, primary_source_id="S1",
                          empty_default="not published"),
    "api-price": dict(name="API list price (in/out per Mtok)", group="c4-econ",
                      unit="USD/Mtok in/out", comparability_set="list-price", direction="lower",
                      freshness_sla_hours=336, primary_source_id="S14",
                      empty_default="not published"),
    "openrouter-share": dict(name="OpenRouter provider token share", group="c4-econ",
                             unit="% tokens", comparability_set="openrouter-provider-share",
                             direction="higher", freshness_sla_hours=72, primary_source_id="S3",
                             empty_default="not published", chip_eligible=False),
    # C5
    "aa-omniscience": dict(name="AA-Omniscience index", group="c5-knowledge", unit="index",
                           comparability_set="aa-omniscience", direction="higher",
                           freshness_sla_hours=72, primary_source_id="S1",
                           empty_default="not published"),
    "aa-halluc-rate": dict(name="AA-Omniscience hallucination rate", group="c5-knowledge",
                           unit="%", comparability_set="aa-omniscience-halluc", direction="lower",
                           freshness_sla_hours=72, primary_source_id="S1",
                           empty_default="not published"),
    "livebench": dict(name="LiveBench global average", group="c5-knowledge", unit="index",
                      comparability_set="livebench-2026-06-25", direction="higher",
                      freshness_sla_hours=1080, primary_source_id="S12",
                      empty_default="not published"),
    # C6
    "arc-agi-3": dict(name="ARC-AGI-3", group="c6-headroom", unit="%",
                      comparability_set="arc-agi-3-official", direction="higher",
                      freshness_sla_hours=1080, primary_source_id="S4",
                      empty_default="not evaluated"),
    "metr-horizon": dict(name="METR 50% time horizon", group="c6-headroom", unit="hours",
                         comparability_set="metr-50pct-horizon", direction="higher",
                         freshness_sla_hours=2160, primary_source_id="S5",
                         empty_default="not evaluated"),
    # C7
    "disclosure-watch": dict(name="Disclosure watch", group="c7-integrity", unit="text",
                             comparability_set="disclosure-watch", direction="none",
                             freshness_sla_hours=720, primary_source_id="S21",
                             empty_default="not published"),
    "swe-bench-verified": dict(name="SWE-bench Verified (self-reported)", group="c7-integrity",
                               unit="%", comparability_set="swe-bench-verified-self-report",
                               direction="higher", freshness_sla_hours=336,
                               primary_source_id="S14", empty_default="not published",
                               claim_v=True),
    # Brief layer (collected, not matrix-rendered)
    "throughput-ttft": dict(name="Throughput / TTFA", group="brief-layer", unit="s",
                            comparability_set="aa-throughput", direction="none",
                            freshness_sla_hours=72, primary_source_id="S1",
                            empty_default="not published", brief_layer=True),
    "context-window": dict(name="Context window", group="brief-layer", unit="tokens",
                           comparability_set="context-window", direction="higher",
                           freshness_sla_hours=336, primary_source_id="S1",
                           empty_default="not published", brief_layer=True),
    "deployment-terms": dict(name="Deployment and data terms", group="brief-layer", unit="text",
                             comparability_set="deployment-terms", direction="none",
                             freshness_sla_hours=720, primary_source_id="S14",
                             empty_default="not published", brief_layer=True),
}

# Quick-look band (ORDERING.md D2, QL-A). swe-rebench substitutes gdpval-aa
# until its collector lands — the fallback is declared, not silent.
QUICK_LOOK = ["aa-index", "arena-elo", "intelligence-per-dollar", "swe-rebench", "disclosure-watch"]
QUICK_LOOK_FALLBACKS = {"swe-rebench": "gdpval-aa"}

# Default compare trio rule T2 (ORDERING.md D3): computed from data at build
# time by pick_default_trio() in run.py; never hardcode the trio itself.
DEFAULT_TRIO_RULE = "top-model-per-vendor-by-aa-index-top3"
