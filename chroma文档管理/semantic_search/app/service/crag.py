"""Corrective RAG（库内修正版）：相关性过滤 + 全无关时改写重检索。

对齐课上 demo01：不联网、不依赖千问；用当前 Settings.llm（如 DeepSeek）做评估与改写。
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional

from llama_index.core import Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import NodeWithScore

from semantic_search.app.config import CRAG_ENABLED, CRAG_VERBOSE

RELEVANCE_PROMPT = PromptTemplate(
    "判断下面的文档片段是否与用户问题相关、能否帮助回答问题。\n"
    "只输出一个词：RELEVANT 或 IRRELEVANT。\n\n"
    "用户问题：{query}\n文档片段：{document}\n输出："
)
REWRITE_PROMPT = PromptTemplate(
    "原始问题检索不到相关信息，请把它改写得更清晰、更具体，便于检索。\n"
    "只输出改写后的问题。\n\n原始问题：{query}\n改写后："
)


def _is_relevant(query: str, doc: str, llm: Any = None) -> bool:
    """单篇相关性判断。"""
    model = llm or Settings.llm
    if model is None:
        return True  # 无 LLM 时不做过滤，避免把结果清空
    text = (doc or "")[:2000]
    resp = model.complete(RELEVANCE_PROMPT.format(query=query, document=text)).text.strip().upper()
    # 模型偶发输出「NOT RELEVANT」等，优先看 IRRELEVANT
    if "IRRELEVANT" in resp:
        return False
    if "RELEVANT" in resp:
        return True
    return False


def filter_relevant_nodes(
    query: str,
    nodes: List[NodeWithScore],
    *,
    llm: Any = None,
    verbose: bool = False,
) -> tuple[List[NodeWithScore], List[dict]]:
    """逐篇评估，返回相关节点 + 评估明细。"""
    kept: List[NodeWithScore] = []
    details: List[dict] = []
    for i, item in enumerate(nodes, 1):
        content = item.node.get_content() or ""
        ok = _is_relevant(query, content, llm=llm)
        details.append({"rank": i, "relevant": ok, "preview": content[:80]})
        if verbose:
            print(f"  [CRAG] 文档 {i}：{'相关' if ok else '无关'}")
        if ok:
            kept.append(item)
    return kept, details


def rewrite_query_for_retrieval(query: str, llm: Any = None) -> str:
    """全无关时改写查询（内部修正）。"""
    model = llm or Settings.llm
    if model is None:
        return query
    new_q = model.complete(REWRITE_PROMPT.format(query=query)).text.strip()
    return new_q or query


def apply_crag(
    question: str,
    nodes: List[NodeWithScore],
    *,
    retrieve_fn: Callable[[str], List[NodeWithScore]],
    llm: Any = None,
    enabled: Optional[bool] = None,
    verbose: Optional[bool] = None,
) -> tuple[List[NodeWithScore], dict]:
    """对已召回节点做 Corrective RAG。

    retrieve_fn(query) -> nodes：改写后重检索用（应已含混合检索 + 后处理）。
    返回：(最终节点, crag 过程信息)
    """
    use = CRAG_ENABLED if enabled is None else enabled
    verb = CRAG_VERBOSE if verbose is None else verbose
    info: dict = {
        "enabled": bool(use),
        "rewritten_query": None,
        "retried": False,
        "before_count": len(nodes),
        "after_count": len(nodes),
        "eval": [],
        "message": "skipped",
    }
    if not use:
        return nodes, info
    if not nodes:
        info["message"] = "empty_input"
        info["after_count"] = 0
        return nodes, info

    if verb:
        print(f"[CRAG] 相关性过滤，候选 {len(nodes)} 篇...")
    kept, details = filter_relevant_nodes(question, nodes, llm=llm, verbose=verb)
    info["eval"] = details

    if kept:
        info["after_count"] = len(kept)
        info["message"] = "filtered"
        return kept, info

    # 全部无关 → 改写 + 重检索（只再来一轮，对齐 demo01）
    if verb:
        print("[CRAG] 全部无关，改写查询并重检索...")
    new_query = rewrite_query_for_retrieval(question, llm=llm)
    info["rewritten_query"] = new_query
    info["retried"] = True
    if verb:
        print(f"[CRAG] 改写后：{new_query}")

    try:
        retry_nodes = list(retrieve_fn(new_query) or [])
    except Exception as exc:  # noqa: BLE001
        print(f"[CRAG] 重检索失败: {exc}")
        info["message"] = f"retry_failed:{exc}"
        info["after_count"] = 0
        return [], info

    kept2, details2 = filter_relevant_nodes(question, retry_nodes, llm=llm, verbose=verb)
    info["eval"] = details + [
        {**d, "round": 2} for d in details2
    ]
    info["after_count"] = len(kept2)
    info["message"] = "rewrote_and_filtered" if kept2 else "no_relevant_after_retry"
    return kept2, info
