"""对齐 demo01_modular_rag.ModularRAG.PRESETS：一键组装优化组合。"""

from __future__ import annotations

# 与课堂 ModularRAG 预设同名；额外映射到本仓库的 Ask 开关。
PRESETS: dict[str, dict] = {
    "basic": {
        "use_pre": False,
        "strategy": "none",
        "use_hybrid": True,
        "fusion_mode": "simple",
        "num_queries": 1,
        "use_rerank": False,
        "use_compress": False,
        "use_reorder": False,
        "use_crag": False,
        "use_self_rag": False,
        "use_eval": False,
    },
    "hybrid_search": {
        "use_pre": False,
        "strategy": "none",
        "use_hybrid": True,
        "fusion_mode": "reciprocal_rerank",
        "num_queries": 1,
        "use_rerank": False,
        "use_compress": False,
        "use_reorder": False,
        "use_crag": False,
        "use_self_rag": False,
        "use_eval": False,
    },
    "advanced": {
        "use_pre": True,
        "strategy": "rewrite",
        "use_hybrid": True,
        "fusion_mode": "reciprocal_rerank",
        "num_queries": 3,  # Multi-Query：LLM 生成查询变体
        "use_rerank": True,
        "use_compress": True,
        "use_reorder": True,
        "use_crag": False,
        "use_self_rag": False,
        "use_eval": False,
    },
    "full_optimization": {
        "use_pre": True,
        "strategy": "hyde",
        "use_hybrid": True,
        "fusion_mode": "reciprocal_rerank",
        "num_queries": 3,
        "use_rerank": True,
        "use_compress": True,
        "use_reorder": True,
        "use_crag": True,
        "use_self_rag": False,
        "use_eval": False,
    },
}

PRESET_LABELS = {
    "basic": "基础（向量+BM25 简单融合）",
    "hybrid_search": "混合检索（RRF）",
    "advanced": "进阶（多查询+重排+压缩）",
    "full_optimization": "全优化（HyDE+多查询+后处理+CRAG）",
    "custom": "自定义（下方勾选）",
}


def apply_preset(preset: str | None, overrides: dict) -> dict:
    """以预设为底，用 overrides 里非 None 的字段覆盖。"""
    name = (preset or "").strip().lower()
    base = dict(PRESETS[name]) if name in PRESETS else {}
    for key, value in overrides.items():
        if value is not None:
            base[key] = value
    # 未选预设且无覆盖时，保留调用方自己传的键
    if not base:
        return {k: v for k, v in overrides.items() if v is not None}
    return base
