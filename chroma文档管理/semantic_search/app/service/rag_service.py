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
    HYBRID_FUSION_MODE,
    RAG_SYSTEM_PROMPT,
    REORDER_ENABLED,
    RERANK_ENABLED,
    SELF_RAG_ENABLED,
    SELF_RAG_VERBOSE,
    SIMILARITY_TOP_K,
)
from semantic_search.app.service.crag import apply_crag, filter_relevant_nodes
from semantic_search.app.service.pre_retrieval import prepare_retrieval_queries
from semantic_search.app.service.presets import apply_preset
from semantic_search.app.service.rag_eval import evaluate_generation
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


def _empty_eval() -> dict:
    return {
        "enabled": False,
        "faithfulness": None,
        "relevancy": None,
        "correctness": None,
        "diagnosis": None,
        "message": "skipped",
    }


def _maybe_generation_eval(
    *,
    enabled: bool,
    question: str,
    answer: str,
    sources: list,
    reference: Optional[str],
) -> dict:
    if not enabled:
        return _empty_eval()
    return evaluate_generation(
        question,
        answer,
        sources,
        reference=reference,
        llm=Settings.llm,
    )


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
        num_queries: int = 1,
        fusion_mode: str | None = None,
    ) -> list[NodeWithScore]:
        """单查询：混合召回 + 检索后处理（供 CRAG 重试复用）。"""
        retriever = self.engine._build_retriever(
            k,
            hybrid_enabled=use_hybrid,
            num_queries=num_queries,
            fusion_mode=fusion_mode,
        )
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
        strategy: Optional[str] = None,
        *,
        preset: Optional[str] = None,
        use_pre: Optional[bool] = None,
        use_hybrid: Optional[bool] = None,
        fusion_mode: Optional[str] = None,
        num_queries: Optional[int] = None,
        use_rerank: Optional[bool] = None,
        use_compress: Optional[bool] = None,
        use_reorder: Optional[bool] = None,
        use_crag: Optional[bool] = None,
        use_self_rag: Optional[bool] = None,
        use_eval: Optional[bool] = False,
        reference: Optional[str] = None,
    ) -> dict:
        """按预设 / 勾选开关跑优化链路并生成答案（对齐 ModularRAG）。"""
        self.engine._require_llm()
        question = (question or "").strip()
        if not question:
            raise ValueError("问题不能为空")

        resolved = apply_preset(
            preset,
            {
                "use_pre": use_pre,
                "strategy": strategy,
                "use_hybrid": use_hybrid,
                "fusion_mode": fusion_mode,
                "num_queries": num_queries,
                "use_rerank": use_rerank,
                "use_compress": use_compress,
                "use_reorder": use_reorder,
                "use_crag": use_crag,
                "use_self_rag": use_self_rag,
                "use_eval": use_eval,
            },
        )
        # 显式请求字段覆盖预设；未传则用预设；都没有则跟 .env / 默认
        if use_pre is not None:
            flag_pre = bool(use_pre)
        elif "use_pre" in resolved:
            flag_pre = bool(resolved["use_pre"])
        else:
            flag_pre = True

        raw_strategy = strategy if strategy is not None else resolved.get("strategy")
        effective_strategy = str(raw_strategy or ("rewrite" if flag_pre else "none")).strip().lower()
        if effective_strategy not in {"none", "clean", "rewrite", "hyde"}:
            effective_strategy = "rewrite" if flag_pre else "none"
        if not flag_pre:
            effective_strategy = "none"

        flag_hybrid = _resolve_flag(
            resolved.get("use_hybrid", use_hybrid), HYBRID_ENABLED
        )
        flag_rerank = _resolve_flag(
            resolved.get("use_rerank", use_rerank), RERANK_ENABLED
        )
        flag_compress = _resolve_flag(
            resolved.get("use_compress", use_compress), COMPRESS_ENABLED
        )
        flag_reorder = _resolve_flag(
            resolved.get("use_reorder", use_reorder), REORDER_ENABLED
        )
        flag_crag = _resolve_flag(resolved.get("use_crag", use_crag), CRAG_ENABLED)
        flag_self = _resolve_flag(
            resolved.get("use_self_rag", use_self_rag), SELF_RAG_ENABLED
        )
        flag_eval = bool(resolved.get("use_eval", use_eval) or False)
        flag_num_queries = max(1, int(resolved.get("num_queries") or num_queries or 1))
        flag_fusion = (
            resolved.get("fusion_mode")
            or fusion_mode
            or HYBRID_FUSION_MODE
            or "reciprocal_rerank"
        )
        preset_name = (preset or "").strip().lower() or None
        if preset_name and preset_name not in {
            "basic",
            "hybrid_search",
            "advanced",
            "full_optimization",
        }:
            preset_name = None

        optimizations = {
            "preset": preset_name,
            "use_pre": flag_pre,
            "strategy": effective_strategy,
            "use_hybrid": flag_hybrid,
            "fusion_mode": flag_fusion,
            "num_queries": flag_num_queries,
            "use_rerank": flag_rerank,
            "use_compress": flag_compress,
            "use_reorder": flag_reorder,
            "use_crag": flag_crag,
            "use_self_rag": flag_self,
            "use_eval": flag_eval,
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
                    "generation_eval": _maybe_generation_eval(
                        enabled=flag_eval,
                        question=question,
                        answer=answer,
                        sources=[],
                        reference=reference,
                    ),
                    "optimizations": optimizations,
                }

        total = self.engine.collection.count()
        if total == 0:
            empty_ans = "知识库为空，请先上传或导入文档后再提问。"
            return {
                "question": question,
                "answer": empty_ans,
                "sources": [],
                "pre_retrieval": empty_pre,
                "crag": _empty_crag(),
                "self_rag": self_info,
                "generation_eval": _empty_eval(),
                "optimizations": optimizations,
            }

        k = max(1, min(k, total))
        prep = prepare_retrieval_queries(question, effective_strategy, llm=Settings.llm)
        queries = prep["retrieval_queries"] or [question]

        ranked_lists: list[list[NodeWithScore]] = []
        retriever = self.engine._build_retriever(
            k,
            hybrid_enabled=flag_hybrid,
            num_queries=flag_num_queries,
            fusion_mode=flag_fusion,
        )
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
                    num_queries=flag_num_queries,
                    fusion_mode=flag_fusion,
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
            no_hit = (
                "知识库中没有足够相关信息回答该问题（Corrective RAG / ISREL 过滤后为空）。"
                if (flag_crag or flag_self)
                else "知识库中没有检索到相关信息，请换个问法或先导入文档。"
            )
            return {
                "question": question,
                "answer": no_hit,
                "sources": [],
                "pre_retrieval": prep,
                "crag": crag_info,
                "self_rag": self_info,
                "generation_eval": _maybe_generation_eval(
                    enabled=flag_eval,
                    question=question,
                    answer=no_hit,
                    sources=[],
                    reference=reference,
                ),
                "optimizations": optimizations,
            }

        synthesizer = get_response_synthesizer(
            response_mode="compact",
            text_qa_template=ASK_QA_PROMPT,
        )
        response = synthesizer.synthesize(query=question, nodes=fused)
        answer = str(response).strip()

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
            "generation_eval": _maybe_generation_eval(
                enabled=flag_eval,
                question=question,
                answer=answer,
                sources=sources,
                reference=reference,
            ),
            "optimizations": optimizations,
        }
