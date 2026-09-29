"""RAG 问答服务：检索前 → 检索中 → 检索后 → CRAG → 生成 → Self-RAG。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from llama_index.core import Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.schema import NodeWithScore

from semantic_search.app.config import (
    COMPRESS_ENABLED,
    CRAG_ENABLED,
    HYBRID_ENABLED,
    RAG_SYSTEM_PROMPT,
    REORDER_ENABLED,
    RERANK_ENABLED,
    SELF_RAG_ENABLED,
    SELF_RAG_VERBOSE,
    SIMILARITY_TOP_K,
)
from semantic_search.app.service.crag import apply_crag, filter_relevant_nodes
from semantic_search.app.service.pre_retrieval import prepare_retrieval_queries
from semantic_search.app.service.retrieval_optimize import apply_postprocessors
from semantic_search.app.service.self_rag import (
    apply_self_rag_post_generate,
    decide_retrieve,
)

ASK_QA_PROMPT = PromptTemplate(
    f"{RAG_SYSTEM_PROMPT}。只依据给定上下文回答；上下文没有的信息请明确说不知道。\n\n"
    "上下文：\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "问题：{query_str}\n"
    "回答："
)

if TYPE_CHECKING:
    from semantic_search.app.engine import SemanticSearchEngine


def _node_key(node: NodeWithScore) -> str:
    """用节点 id 或文本做去重键。"""
    nid = getattr(node.node, "node_id", None) or getattr(node.node, "id_", None)
    if nid:
        return str(nid)
    return (node.node.get_content() or "")[:200]


def _format_source(rank: int, item: NodeWithScore) -> dict:
    score = float(item.score or 0.0)
    return {
        "rank": rank,
        "index": rank - 1,
        "document": item.node.get_content(),
        "similarity": round(score, 4),
        "distance": (
            round(max(1.0 - score, 0.0), 4)
            if 0.0 <= score <= 1.0
            else round(1 / (1 + score), 4)
        ),
    }


def merge_nodes_rrf(
    ranked_lists: list[list[NodeWithScore]],
    k: int,
    rrf_k: int = 60,
) -> list[NodeWithScore]:
    """RRF 融合多路召回结果，再取 Top-K。"""
    scores: dict[str, float] = {}
    best: dict[str, NodeWithScore] = {}

    for nodes in ranked_lists:
        for rank, item in enumerate(nodes, start=1):
            key = _node_key(item)
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)
            prev = best.get(key)
            if prev is None or float(item.score or 0.0) > float(prev.score or 0.0):
                best[key] = item

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    merged: list[NodeWithScore] = []
    for key, rrf_score in ordered[:k]:
        node = best[key]
        node.score = rrf_score
        merged.append(node)
    return merged


def _resolve_flag(override: Optional[bool], default: bool) -> bool:
    """请求显式传 True/False 则覆盖；None 跟从 .env 默认。"""
    return default if override is None else bool(override)


def _empty_crag() -> dict:
    return {
        "enabled": False,
        "rewritten_query": None,
        "retried": False,
        "before_count": 0,
        "after_count": 0,
        "eval": [],
        "message": "skipped",
    }


def _empty_self_rag() -> dict:
    return {
        "enabled": False,
        "retrieve": None,
        "skipped_retrieval": False,
        "isrel_shared_with_crag": False,
        "issup": None,
        "corrected": False,
        "isuse": None,
        "message": "skipped",
    }


def _context_from_nodes(nodes: list[NodeWithScore]) -> str:
    parts = []
    for i, item in enumerate(nodes, 1):
        text = (item.node.get_content() or "").strip()
        if text:
            parts.append(f"[{i}] {text}")
    return "\n\n".join(parts)


class RagAskService:
    """编排：Retrieve? → Pre/Mid/Post → CRAG≈ISREL → 生成 → ISSUP/ISUSE。"""

    def __init__(self, engine: SemanticSearchEngine):
        self.engine = engine

    def _retrieve_pipeline(
        self,
        query: str,
        k: int,
        *,
        use_hybrid: bool,
        use_rerank: bool,
        use_compress: bool,
        use_reorder: bool,
    ) -> list[NodeWithScore]:
        """单查询：混合召回 + 检索后处理（供 CRAG 重试复用）。"""
        retriever = self.engine._build_retriever(k, hybrid_enabled=use_hybrid)
        nodes = list(retriever.retrieve(query))
        return apply_postprocessors(
            nodes,
            query,
            k,
            rerank_enabled=use_rerank,
            compress_enabled=use_compress,
            reorder_enabled=use_reorder,
        )

    def ask(
        self,
        question: str,
        k: int = SIMILARITY_TOP_K,
        strategy: str = "rewrite",
        *,
        use_pre: bool = True,
        use_hybrid: Optional[bool] = None,
        use_rerank: Optional[bool] = None,
        use_compress: Optional[bool] = None,
        use_reorder: Optional[bool] = None,
        use_crag: Optional[bool] = None,
        use_self_rag: Optional[bool] = None,
    ) -> dict:
        """按勾选开关跑优化链路并生成答案。"""
        self.engine._require_llm()
        question = (question or "").strip()
        if not question:
            raise ValueError("问题不能为空")

        effective_strategy = (strategy or "rewrite").strip().lower() if use_pre else "none"
        if effective_strategy not in {"none", "clean", "rewrite", "hyde"}:
            effective_strategy = "rewrite" if use_pre else "none"
        flag_hybrid = _resolve_flag(use_hybrid, HYBRID_ENABLED)
        flag_rerank = _resolve_flag(use_rerank, RERANK_ENABLED)
        flag_compress = _resolve_flag(use_compress, COMPRESS_ENABLED)
        flag_reorder = _resolve_flag(use_reorder, REORDER_ENABLED)
        flag_crag = _resolve_flag(use_crag, CRAG_ENABLED)
        flag_self = _resolve_flag(use_self_rag, SELF_RAG_ENABLED)
        optimizations = {
            "use_pre": bool(use_pre),
            "strategy": effective_strategy,
            "use_hybrid": flag_hybrid,
            "use_rerank": flag_rerank,
            "use_compress": flag_compress,
            "use_reorder": flag_reorder,
            "use_crag": flag_crag,
            "use_self_rag": flag_self,
        }

        empty_pre = {
            "strategy": effective_strategy,
            "original_query": question,
            "clean_query": question,
            "rewritten_query": None,
            "hyde_doc": None,
            "retrieval_queries": [],
        }
        self_info = _empty_self_rag()
        self_info["enabled"] = flag_self

        # ----- Self-RAG Retrieve：要不要查库？-----
        if flag_self:
            need_retrieve = decide_retrieve(
                question, llm=Settings.llm, verbose=SELF_RAG_VERBOSE
            )
            self_info["retrieve"] = need_retrieve
            if not need_retrieve:
                answer = Settings.llm.complete(question).text.strip()
                self_info["skipped_retrieval"] = True
                self_info["message"] = "no_retrieve_direct_answer"
                # 无资料时仍可打有用性分
                from semantic_search.app.service.self_rag import judge_isuse

                self_info["isuse"] = judge_isuse(
                    question, answer, llm=Settings.llm, verbose=SELF_RAG_VERBOSE
                )
                return {
                    "question": question,
                    "answer": answer,
                    "sources": [],
                    "pre_retrieval": empty_pre,
                    "crag": _empty_crag(),
                    "self_rag": self_info,
                    "optimizations": optimizations,
                }

        total = self.engine.collection.count()
        if total == 0:
            return {
                "question": question,
                "answer": "知识库为空，请先上传或导入文档后再提问。",
                "sources": [],
                "pre_retrieval": empty_pre,
                "crag": _empty_crag(),
                "self_rag": self_info,
                "optimizations": optimizations,
            }

        k = max(1, min(k, total))
        prep = prepare_retrieval_queries(question, effective_strategy, llm=Settings.llm)
        queries = prep["retrieval_queries"] or [question]

        ranked_lists: list[list[NodeWithScore]] = []
        retriever = self.engine._build_retriever(k, hybrid_enabled=flag_hybrid)
        for q in queries:
            ranked_lists.append(list(retriever.retrieve(q)))

        fuse_k = max(k, min(total, k * 2))
        fused = (
            merge_nodes_rrf(ranked_lists, k=fuse_k)
            if len(ranked_lists) > 1
            else (ranked_lists[0][:fuse_k] if ranked_lists else [])
        )

        fused = apply_postprocessors(
            fused,
            question,
            k,
            rerank_enabled=flag_rerank,
            compress_enabled=flag_compress,
            reorder_enabled=flag_reorder,
        )

        # CRAG ≈ ISREL；Self-RAG 开启且未开 CRAG 时单独做相关性过滤
        if flag_crag:
            fused, crag_info = apply_crag(
                question,
                fused,
                retrieve_fn=lambda q: self._retrieve_pipeline(
                    q,
                    k,
                    use_hybrid=flag_hybrid,
                    use_rerank=flag_rerank,
                    use_compress=flag_compress,
                    use_reorder=flag_reorder,
                ),
                llm=Settings.llm,
                enabled=True,
            )
            if flag_self:
                self_info["isrel_shared_with_crag"] = True
        else:
            crag_info = _empty_crag()
            if flag_self and fused:
                fused, details = filter_relevant_nodes(
                    question, fused, llm=Settings.llm, verbose=SELF_RAG_VERBOSE
                )
                crag_info = {
                    "enabled": False,
                    "rewritten_query": None,
                    "retried": False,
                    "before_count": len(details),
                    "after_count": len(fused),
                    "eval": details,
                    "message": "self_rag_isrel_only",
                }

        if not fused:
            return {
                "question": question,
                "answer": (
                    "知识库中没有足够相关信息回答该问题（Corrective RAG / ISREL 过滤后为空）。"
                    if (flag_crag or flag_self)
                    else "知识库中没有检索到相关信息，请换个问法或先导入文档。"
                ),
                "sources": [],
                "pre_retrieval": prep,
                "crag": crag_info,
                "self_rag": self_info,
                "optimizations": optimizations,
            }

        synthesizer = get_response_synthesizer(
            response_mode="compact",
            text_qa_template=ASK_QA_PROMPT,
        )
        response = synthesizer.synthesize(query=question, nodes=fused)
        answer = str(response).strip()

        # Self-RAG：ISSUP → 不足则修正 → ISUSE
        if flag_self:
            context = _context_from_nodes(fused)
            answer, post_info = apply_self_rag_post_generate(
                question,
                answer,
                context,
                llm=Settings.llm,
                enabled=True,
            )
            self_info.update(post_info)
            self_info["enabled"] = True
            self_info["retrieve"] = True
            self_info["skipped_retrieval"] = False

        sources = [_format_source(i + 1, item) for i, item in enumerate(fused)]
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "pre_retrieval": prep,
            "crag": crag_info,
            "self_rag": self_info,
            "optimizations": optimizations,
        }
