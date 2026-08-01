"""Canonical model ids and per-source name/slug mappings.

Adding a catalog model = one entry here per source that covers it (plus the
snapshot models{} entry). Collectors must NEVER guess: an unmapped source row
is ignored (and surfaces via the new-model watch), a mapped-but-missing row
yields no CellValue so the runner writes an honest empty cell.
"""

MODELS = {
    "fable-5": {"name": "Claude Fable 5", "vendor": "Anthropic", "status": "current"},
    "opus-5": {"name": "Claude Opus 5", "vendor": "Anthropic", "status": "current"},
    "gpt-5-6-sol": {"name": "GPT-5.6 Sol", "vendor": "OpenAI", "status": "current"},
    "kimi-k3": {"name": "Kimi K3", "vendor": "Moonshot AI", "status": "current"},
    "ds-v4-pro": {"name": "DeepSeek V4 Pro", "vendor": "DeepSeek", "status": "current"},
}

# Artificial Analysis /models embedded JSON: slug -> model id
AA_SLUGS = {
    "claude-fable-5": "fable-5",
    "claude-opus-5": "opus-5",
    "gpt-5-6-sol": "gpt-5-6-sol",
    "kimi-k3": "kimi-k3",
    "deepseek-v4-pro": "ds-v4-pro",
}

# ARC Prize v3.json: modelId prefix (tier suffix stripped) -> model id
ARC_PREFIXES = {
    "anthropic-claude-fable-5": "fable-5",
    "anthropic-claude-opus-5": "opus-5",
    "openai-gpt-5-6-sol": "gpt-5-6-sol",
    "moonshot-kimi-k3": "kimi-k3",
    "deepseek-deepseek-v4-pro": "ds-v4-pro",
}
ARC_TIERS = ("low", "medium", "high", "xhigh", "max")
ARC_TIER_DISPLAY = {"low": "Low", "medium": "Medium", "high": "High", "xhigh": "xHigh", "max": "Max"}

# METR yaml result keys -> (model id, extra flags)
METR_KEYS = {
    "claude_mythos_preview_early_inspect": (
        "fable-5",
        # exact snapshot flag: the "proxy-model measurement" integrity marker
        # must survive collector rebuilds (verifier gate finding C.8 — the
        # leaner collector flag would have silently dropped rule-7 propagation
        # and the chip-exclusion disclaimer on the first COLLECT=1 overwrite)
        ["proxy-model measurement: value is for Claude Mythos Preview (early), not Fable 5 itself"],
    ),
}

# Arena HF dataset model_name prefixes -> model id (highest-rated variant wins)
ARENA_PREFIXES = {
    "claude-fable-5": "fable-5",
    "claude-opus-5": "opus-5",
    "gpt-5.6-sol": "gpt-5-6-sol",
    "kimi-k3": "kimi-k3",
    "deepseek-v4-pro": "ds-v4-pro",
}

# OpenRouter market-share author keys -> model ids that display the provider figure
OPENROUTER_AUTHORS = {
    "anthropic": (["fable-5", "opus-5"], "Anthropic"),
    "openai": (["gpt-5-6-sol"], "OpenAI"),
    "deepseek": (["ds-v4-pro"], "DeepSeek"),
    "moonshotai": (["kimi-k3"], "Moonshot"),
}

# llm-stats SWE-bench Pro model_id -> model id (note: llm-stats uses dots)
LLMSTATS_IDS = {
    "claude-fable-5": "fable-5",
    "claude-opus-5": "opus-5",
    "gpt-5.6-sol": "gpt-5-6-sol",
    "kimi-k3": "kimi-k3",
    "deepseek-v4-pro-max": "ds-v4-pro",
}

# Terminal-Bench display model names -> model id
TBENCH_NAMES = {
    "Fable 5": "fable-5",
    "Claude Opus 5": "opus-5",
    "GPT-5.6 Sol": "gpt-5-6-sol",
    "Kimi K3": "kimi-k3",
    "DeepSeek V4 Pro": "ds-v4-pro",
}
