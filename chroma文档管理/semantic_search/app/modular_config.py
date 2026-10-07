"""Modular RAG 配置：YAML 默认编排 + 三层抽象（类型 → 模块 → 算子）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from semantic_search.app.config import (
    COMPRESS_ENABLED,
    CRAG_ENABLED,
    HYBRID_ENABLED,
    HYBRID_FUSION_MODE,
    REORDER_ENABLED,
    RERANK_ENABLED,
    SELF_RAG_ENABLED,
)

PACKAGE_DIR = Path(__file__).resolve().parents[1]
YAML_PATH = PACKAGE_DIR / "rag_config.yaml"

# YAML 缺失或未装 PyYAML 时的内置默认（与 rag_config.yaml 对齐）
_BUILTIN: dict[str, Any] = {
    "default_preset": "custom",
    "pre_retrieval": {"enabled": True, "operator": "rewrite"},
    "retrieval": {
        "hybrid": True,
        "fusion_mode": "reciprocal_rerank",
        "num_queries": 1,
    },
    "post_retrieval": {"rerank": True, "compress": True, "reorder": True},
    "generation": {"crag": True, "self_rag": False, "eval": False},
}


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """无 PyYAML 时解析本仓库这种两层 YAML（标量 + 一级嵌套）。"""
    root: dict[str, Any] = {}
    section: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section = line[:-1].strip()
            root[section] = {}
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        parsed: Any
        if value.lower() in {"true", "yes"}:
            parsed = True
        elif value.lower() in {"false", "no"}:
            parsed = False
        elif value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            parsed = int(value)
        else:
            parsed = value.strip("'\"")
        if line.startswith(" ") and section:
            root[section][key] = parsed
        else:
            section = None
            root[key] = parsed
    return root


def load_modular_yaml() -> dict[str, Any]:
    """读取 rag_config.yaml；失败则用内置默认。"""
    if not YAML_PATH.is_file():
        return dict(_BUILTIN)
    text = YAML_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    try:
        parsed = _parse_simple_yaml(text)
        return parsed if parsed else dict(_BUILTIN)
    except Exception:
        return dict(_BUILTIN)


def yaml_as_ask_defaults() -> dict[str, Any]:
    """把 YAML 转成 /ask 同名开关，供未传 preset 时垫底。"""
    cfg = load_modular_yaml()
    pre = cfg.get("pre_retrieval") or {}
    mid = cfg.get("retrieval") or {}
    post = cfg.get("post_retrieval") or {}
    gen = cfg.get("generation") or {}
    enabled = bool(pre.get("enabled", True))
    op = str(pre.get("operator") or "rewrite").strip().lower()
    return {
        "use_pre": enabled,
        "strategy": op if enabled else "none",
        "use_hybrid": bool(mid.get("hybrid", HYBRID_ENABLED)),
        "fusion_mode": str(mid.get("fusion_mode") or HYBRID_FUSION_MODE or "reciprocal_rerank"),
        "num_queries": int(mid.get("num_queries") or 1),
        "use_graph": bool(mid.get("graph", False)),
        "use_rerank": bool(post.get("rerank", RERANK_ENABLED)),
        "use_compress": bool(post.get("compress", COMPRESS_ENABLED)),
        "use_reorder": bool(post.get("reorder", REORDER_ENABLED)),
        "use_crag": bool(gen.get("crag", CRAG_ENABLED)),
        "use_self_rag": bool(gen.get("self_rag", SELF_RAG_ENABLED)),
        "use_eval": bool(gen.get("eval", False)),
        "use_web": False,
    }


def describe_module_graph(flags: dict[str, Any] | None = None) -> dict[str, Any]:
    """三层抽象：给 GET /modules 和作业讲解用。"""
    f = flags or yaml_as_ask_defaults()
    pre_on = bool(f.get("use_pre", True))
    strategy = str(f.get("strategy") or "rewrite")
    op_pre = {
        "none": "原句直出",
        "clean": "查询清洗",
        "rewrite": "清洗 + Query Rewriting",
        "hyde": "HyDE 假想文档（含原句）",
        "step_back": "Step-Back 上位问题（含原句）",
    }.get(strategy, strategy)
    hybrid = bool(f.get("use_hybrid", True))
    nq = int(f.get("num_queries") or 1)
    fusion = str(f.get("fusion_mode") or "reciprocal_rerank")
    layers = [
        {
            "module_type": "Pre-Retrieval",
            "module": "Query Transformation",
            "operator": op_pre if pre_on else "关闭（原句检索）",
            "enabled": pre_on,
        },
        {
            "module_type": "Retrieval",
            "module": "Hybrid Search" if hybrid else "Vector Search",
            "operator": (
                f"向量+BM25 · fusion={fusion}"
                + (f" · Multi-Query×{nq}" if nq > 1 else "")
            ),
            "enabled": True,
        },
        {
            "module_type": "Retrieval",
            "module": "GraphRAG",
            "operator": "Neo4j 子图召回，优先拼接在向量结果前",
            "enabled": bool(f.get("use_graph")),
        },
        {
            "module_type": "Post-Retrieval",
            "module": "Rerank",
            "operator": "Cross-Encoder / DashScopeRerank",
            "enabled": bool(f.get("use_rerank")),
        },
        {
            "module_type": "Post-Retrieval",
            "module": "Compress",
            "operator": "SentenceEmbeddingOptimizer",
            "enabled": bool(f.get("use_compress")),
        },
        {
            "module_type": "Post-Retrieval",
            "module": "LongContextReorder",
            "operator": "首尾重排（Lost in the Middle）",
            "enabled": bool(f.get("use_reorder")),
        },
        {
            "module_type": "Generation",
            "module": "Corrective RAG",
            "operator": "相关过滤 + 全无关改写重检（循环编排）",
            "enabled": bool(f.get("use_crag")),
        },
        {
            "module_type": "Generation",
            "module": "Self-RAG",
            "operator": "Retrieve 条件门控 + ISSUP/ISUSE",
            "enabled": bool(f.get("use_self_rag")),
        },
    ]
    flows = ["Linear（改写→检索→融合→后处理→生成）"]
    if f.get("use_graph"):
        flows.append("Branching（向量通道 ∥ 图谱通道再拼接）")
    if f.get("use_self_rag"):
        flows.append("Conditional（Retrieve 决定是否查库）")
    if f.get("use_crag") or f.get("use_self_rag"):
        flows.append("Loop（CRAG 重检 / ISSUP 修正）")
    return {
        "source": str(YAML_PATH) if YAML_PATH.is_file() else "builtin",
        "yaml": load_modular_yaml(),
        "flow_patterns": flows,
        "layers": layers,
    }
