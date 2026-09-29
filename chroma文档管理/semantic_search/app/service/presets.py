"""对齐 demo01_modular_rag.ModularRAG.PRESETS：一键组装优化组合。"""  # 模块说明：预设表与合并逻辑

from __future__ import annotations  # 允许延后求值的类型注解写法

# 与课堂 ModularRAG 预设同名；额外映射到本仓库的 Ask 开关。  # 说明注释：命名对齐 demo
PRESETS: dict[str, dict] = {  # 预设名 → 开关字典
    "basic": {  # 基础预设：两路检索简单融合、无后处理
        "use_pre": False,  # 关闭检索前优化
        "strategy": "none",  # 无清洗/重写/HyDE
        "use_hybrid": True,  # 仍启用向量+BM25
        "fusion_mode": "simple",  # 简单去重拼接融合
        "num_queries": 1,  # 不做 Multi-Query
        "use_rerank": False,  # 不重排
        "use_compress": False,  # 不压缩
        "use_reorder": False,  # 不长上下文重排
        "use_crag": False,  # 不开 CRAG
        "use_self_rag": False,  # 不开 Self-RAG
        "use_eval": False,  # 不做生成评估
    },  # basic 结束
    "hybrid_search": {  # 混合检索预设：RRF 融合
        "use_pre": False,  # 关闭检索前
        "strategy": "none",  # 原句检索
        "use_hybrid": True,  # 向量+BM25
        "fusion_mode": "reciprocal_rerank",  # RRF 倒数排名融合
        "num_queries": 1,  # 单查询
        "use_rerank": False,  # 无精排
        "use_compress": False,  # 无压缩
        "use_reorder": False,  # 无重排版
        "use_crag": False,  # 无 CRAG
        "use_self_rag": False,  # 无 Self-RAG
        "use_eval": False,  # 无评估
    },  # hybrid_search 结束
    "advanced": {  # 进阶：多查询 + 重排 + 压缩
        "use_pre": True,  # 开检索前
        "strategy": "rewrite",  # 清洗+重写
        "use_hybrid": True,  # 混合检索
        "fusion_mode": "reciprocal_rerank",  # RRF
        "num_queries": 3,  # Multi-Query：LLM 生成查询变体
        "use_rerank": True,  # 开重排
        "use_compress": True,  # 开压缩
        "use_reorder": True,  # 开长上下文重排
        "use_crag": False,  # 本档默认关 CRAG
        "use_self_rag": False,  # 关 Self-RAG
        "use_eval": False,  # 关评估
    },  # advanced 结束
    "full_optimization": {  # 全优化：HyDE + 多查询 + 后处理 + CRAG
        "use_pre": True,  # 开检索前
        "strategy": "hyde",  # HyDE 假想文档
        "use_hybrid": True,  # 混合检索
        "fusion_mode": "reciprocal_rerank",  # RRF
        "num_queries": 3,  # Multi-Query
        "use_rerank": True,  # 重排
        "use_compress": True,  # 压缩
        "use_reorder": True,  # 长上下文重排
        "use_crag": True,  # 开 CRAG
        "use_self_rag": False,  # Self-RAG 仍默认关（可前端勾）
        "use_eval": False,  # 评估默认关
    },  # full_optimization 结束
}  # PRESETS 结束

PRESET_LABELS = {  # 前端展示用中文标签
    "basic": "基础（向量+BM25 简单融合）",  # basic 文案
    "hybrid_search": "混合检索（RRF）",  # hybrid 文案
    "advanced": "进阶（多查询+重排+压缩）",  # advanced 文案
    "full_optimization": "全优化（HyDE+多查询+后处理+CRAG）",  # full 文案
    "custom": "自定义（下方勾选）",  # 自定义档
}  # PRESET_LABELS 结束


def apply_preset(preset: str | None, overrides: dict) -> dict:  # 合并预设与请求覆盖项
    """以预设为底，用 overrides 里非 None 的字段覆盖。"""  # 函数文档字符串
    name = (preset or "").strip().lower()  # 规范化预设名
    base = dict(PRESETS[name]) if name in PRESETS else {}  # 有预设则拷贝底表，否则空字典
    for key, value in overrides.items():  # 遍历调用方覆盖项
        if value is not None:  # 仅非 None 才覆盖（None 表示跟预设/.env）
            base[key] = value  # 写入覆盖值
    # 未选预设且无覆盖时，保留调用方自己传的键  # 兜底说明
    if not base:  # 既无预设又几乎无覆盖
        return {k: v for k, v in overrides.items() if v is not None}  # 只返回显式值
    return base  # 返回合并后的开关字典
