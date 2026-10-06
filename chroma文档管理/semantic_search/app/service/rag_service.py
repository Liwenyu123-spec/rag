"""RAG 问答服务：解析开关后交给 AskPipeline，不再把算子写死在 ask() 里。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from llama_index.core import Settings
from llama_index.core.schema import NodeWithScore

from semantic_search.app.config import (
    COMPRESS_ENABLED,
    CRAG_ENABLED,
    HYBRID_ENABLED,
    HYBRID_FUSION_MODE,
    REORDER_ENABLED,
    RERANK_ENABLED,
    SELF_RAG_ENABLED,
    SIMILARITY_TOP_K,
)
from semantic_search.app.knowledge_scope import DEFAULT_SCOPE, filter_nodes_by_scope, normalize_scope
from semantic_search.app.service.ask_modules import default_ask_modules
from semantic_search.app.service.crag import apply_crag
from semantic_search.app.modular_config import yaml_as_ask_defaults
from semantic_search.app.service.pipeline import (
    AskContext,
    AskPipeline,
    empty_crag,
    empty_graph,
    empty_pre,
    empty_self_rag,
    merge_nodes_rrf,
)
from semantic_search.app.service.pre_retrieval import prepare_retrieval_queries
from semantic_search.app.service.presets import apply_preset
from semantic_search.app.service.retrieval_optimize import apply_postprocessors

# 兼容旧 import：merge_nodes_rrf 仍可从本模块导入
__all__ = ["RagAskService", "merge_nodes_rrf"]

LEGAL_PRESETS = {
    "basic",
    "hybrid_search",
    "advanced",
    "full_optimization",
    "step_back",
    "graph_hybrid",
    "custom",
}


if TYPE_CHECKING:
    from semantic_search.app.engine import SemanticSearchEngine
    from semantic_search.app.service.graph_rag import GraphRagService


def _resolve_flag(override: Optional[bool], default: bool) -> bool:
    return default if override is None else bool(override)


class RagAskService:
    """只负责：解析配置 → 构造 AskContext → 跑注册管线。"""

    def __init__(
        self,
        engine: SemanticSearchEngine,
        graph_rag: Optional["GraphRagService"] = None,
        pipeline: AskPipeline | None = None,
    ):
        self.engine = engine
        self.graph_rag = graph_rag
        self.pipeline = pipeline or AskPipeline(default_ask_modules())

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
        doc_scope: str | None = None,
    ) -> list[NodeWithScore]:
        scope = normalize_scope(doc_scope)
        retriever = self.engine._build_retriever(
            max(k * 4, 20),
            hybrid_enabled=use_hybrid,
            num_queries=num_queries,
            fusion_mode=fusion_mode,
            doc_scope=scope,
        )
        nodes = filter_nodes_by_scope(list(retriever.retrieve(query)), scope)
        return apply_postprocessors(
            nodes,
            query,
            k,
            rerank_enabled=use_rerank,
            compress_enabled=use_compress,
            reorder_enabled=use_reorder,
        )

    def retrieve_for_eval(
        self,
        question: str,
        k: int,
        *,
        use_pre: bool,
        strategy: str,
        use_hybrid: bool,
        fusion_mode: str | None,
        num_queries: int,
        use_rerank: bool,
        use_compress: bool,
        use_reorder: bool,
        use_crag: bool,
    ) -> list[NodeWithScore]:
        """检索评估仍复用同一套检索算子，不走生成模块。"""
        question = (question or "").strip()
        if not question:
            return []
        total = self.engine.collection.count()
        if total == 0:
            return []
        k = max(1, min(k, total))
        effective = (strategy or "none").strip().lower()
        if not use_pre:
            effective = "none"
        if effective not in {"none", "clean", "rewrite", "hyde", "step_back"}:
            effective = "rewrite" if use_pre else "none"
        prep = prepare_retrieval_queries(question, effective, llm=Settings.llm)
        queries = prep["retrieval_queries"] or [question]
        ranked_lists: list[list[NodeWithScore]] = []
        retriever = self.engine._build_retriever(
            max(k * 4, 20),
            hybrid_enabled=use_hybrid,
            num_queries=max(1, int(num_queries or 1)),
            fusion_mode=fusion_mode,
            doc_scope=DEFAULT_SCOPE,
        )
        for q in queries:
            ranked_lists.append(filter_nodes_by_scope(list(retriever.retrieve(q)), DEFAULT_SCOPE))
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
            rerank_enabled=use_rerank,
            compress_enabled=use_compress,
            reorder_enabled=use_reorder,
        )
        if use_crag:
            fused, _ = apply_crag(
                question,
                fused,
                retrieve_fn=lambda q: self._retrieve_pipeline(
                    q,
                    k,
                    use_hybrid=use_hybrid,
                    use_rerank=use_rerank,
                    use_compress=use_compress,
                    use_reorder=use_reorder,
                    num_queries=max(1, int(num_queries or 1)),
                    fusion_mode=fusion_mode,
                ),
                llm=Settings.llm,
                enabled=True,
            )
        return fused

    def _resolve_flags(
        self,
        *,
        question: str,
        k: int,
        strategy: Optional[str],
        preset: Optional[str],
        use_pre: Optional[bool],
        use_hybrid: Optional[bool],
        fusion_mode: Optional[str],
        num_queries: Optional[int],
        use_rerank: Optional[bool],
        use_compress: Optional[bool],
        use_reorder: Optional[bool],
        use_crag: Optional[bool],
        use_self_rag: Optional[bool],
        use_graph: Optional[bool],
        use_eval: Optional[bool],
        doc_scope: Optional[str] = None,
    ) -> dict:
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
                "use_graph": use_graph,
                "use_eval": use_eval,
            },
        )
        for key, value in yaml_as_ask_defaults().items():
            resolved.setdefault(key, value)

        if use_pre is not None:
            flag_pre = bool(use_pre)
        elif "use_pre" in resolved:
            flag_pre = bool(resolved["use_pre"])
        else:
            flag_pre = True

        raw_strategy = strategy if strategy is not None else resolved.get("strategy")
        effective_strategy = str(raw_strategy or ("rewrite" if flag_pre else "none")).strip().lower()
        if effective_strategy not in {"none", "clean", "rewrite", "hyde", "step_back"}:
            effective_strategy = "rewrite" if flag_pre else "none"
        if not flag_pre:
            effective_strategy = "none"

        preset_name = (preset or "").strip().lower() or None
        if preset_name and preset_name not in LEGAL_PRESETS:
            preset_name = None

        return {
            "preset": preset_name,
            "use_pre": flag_pre,
            "strategy": effective_strategy,
            "use_hybrid": _resolve_flag(resolved.get("use_hybrid", use_hybrid), HYBRID_ENABLED),
            "fusion_mode": (
                resolved.get("fusion_mode")
                or fusion_mode
                or HYBRID_FUSION_MODE
                or "reciprocal_rerank"
            ),
            "num_queries": max(1, int(resolved.get("num_queries") or num_queries or 1)),
            "use_rerank": _resolve_flag(resolved.get("use_rerank", use_rerank), RERANK_ENABLED),
            "use_compress": _resolve_flag(resolved.get("use_compress", use_compress), COMPRESS_ENABLED),
            "use_reorder": _resolve_flag(resolved.get("use_reorder", use_reorder), REORDER_ENABLED),
            "use_crag": _resolve_flag(resolved.get("use_crag", use_crag), CRAG_ENABLED),
            "use_self_rag": _resolve_flag(resolved.get("use_self_rag", use_self_rag), SELF_RAG_ENABLED),
            "use_graph": _resolve_flag(resolved.get("use_graph", use_graph), False),
            "use_eval": bool(resolved.get("use_eval", use_eval) or False),
            "doc_scope": normalize_scope(doc_scope or resolved.get("doc_scope")),
        }

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
        use_graph: Optional[bool] = None,
        use_eval: Optional[bool] = False,
        reference: Optional[str] = None,
        doc_scope: Optional[str] = None,
        compare_baseline: bool | None = True,
    ) -> dict:
        """解析开关后跑默认 AskPipeline。"""
        self.engine._require_llm()
        question = (question or "").strip()
        if not question:
            raise ValueError("问题不能为空")

        flags = self._resolve_flags(
            question=question,
            k=k,
            strategy=strategy,
            preset=preset,
            use_pre=use_pre,
            use_hybrid=use_hybrid,
            fusion_mode=fusion_mode,
            num_queries=num_queries,
            use_rerank=use_rerank,
            use_compress=use_compress,
            use_reorder=use_reorder,
            use_crag=use_crag,
            use_self_rag=use_self_rag,
            use_graph=use_graph,
            use_eval=use_eval,
            doc_scope=doc_scope,
        )
        total = self.engine.collection.count()
        if total > 0:
            k = max(1, min(k, total))
        else:
            k = max(1, k)

        ctx = AskContext(
            engine=self.engine,
            graph_rag=self.graph_rag,
            question=question,
            k=k,
            llm=Settings.llm,
            reference=reference,
            flags=flags,
            corpus_size=total,
            pre_retrieval=empty_pre(question, flags["strategy"]),
            crag=empty_crag(),
            self_rag=empty_self_rag(),
            graph=empty_graph(),
        )
        ctx.self_rag["enabled"] = bool(flags.get("use_self_rag"))
        ctx.retrieve_retry = lambda q: self._retrieve_pipeline(  # type: ignore[attr-defined]
            q,
            k,
            use_hybrid=bool(flags["use_hybrid"]),
            use_rerank=bool(flags["use_rerank"]),
            use_compress=bool(flags["use_compress"]),
            use_reorder=bool(flags["use_reorder"]),
            num_queries=int(flags["num_queries"]),
            fusion_mode=flags.get("fusion_mode"),
            doc_scope=flags.get("doc_scope"),
        )
        self.pipeline.run(ctx)
        current = ctx.to_response()
        if compare_baseline:
            current["comparison"] = self._compare_with_baseline(question, k, flags, current, reference)
        else:
            current["comparison"] = {"enabled": False, "message": "未开启优化对照"}
        return current

    def _flags_look_optimized(self, flags: dict) -> bool:
        if flags.get("use_pre") and flags.get("strategy") not in {None, "", "none"}:
            return True
        if int(flags.get("num_queries") or 1) > 1:
            return True
        if flags.get("use_rerank") or flags.get("use_compress") or flags.get("use_reorder"):
            return True
        if flags.get("use_crag") or flags.get("use_self_rag") or flags.get("use_graph"):
            return True
        fusion = str(flags.get("fusion_mode") or "")
        if flags.get("use_hybrid") and fusion not in {"", "simple"}:
            return True
        return False

    def _compare_with_baseline(
        self,
        question: str,
        k: int,
        flags: dict,
        current: dict,
        reference: Optional[str],
    ) -> dict:
        if not self._flags_look_optimized(flags):
            return {
                "enabled": False,
                "message": "当前配置与基础 RAG 相同，没有可对照的优化项。请勾选检索前/后优化后再问。",
            }
        baseline_flags = {
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
            "use_graph": False,
            "use_eval": False,
            "doc_scope": flags.get("doc_scope"),
            "preset": "basic",
        }
        baseline = self.ask(
            question,
            k,
            strategy="none",
            preset="basic",
            use_pre=False,
            use_hybrid=True,
            fusion_mode="simple",
            num_queries=1,
            use_rerank=False,
            use_compress=False,
            use_reorder=False,
            use_crag=False,
            use_self_rag=False,
            use_graph=False,
            use_eval=False,
            reference=None,
            doc_scope=flags.get("doc_scope"),
            compare_baseline=False,
        )
        return _diff_ask_runs(baseline, current, flags)


def _snip(text: str, n: int = 180) -> str:
    raw = " ".join((text or "").split())
    return raw if len(raw) <= n else raw[:n] + "…"


def _src_key(src: dict) -> str:
    return _snip(str(src.get("document") or ""), 96)


def _diff_ask_runs(baseline: dict, current: dict, flags: dict) -> dict:
    b_ans = str(baseline.get("answer") or "").strip()
    c_ans = str(current.get("answer") or "").strip()
    b_pre = baseline.get("pre_retrieval") or {}
    c_pre = current.get("pre_retrieval") or {}
    b_q = b_pre.get("retrieval_queries") or [b_pre.get("original_query") or ""]
    c_q = c_pre.get("retrieval_queries") or [c_pre.get("original_query") or ""]
    b_src = baseline.get("sources") or []
    c_src = current.get("sources") or []
    b_keys = [_src_key(s) for s in b_src]
    c_keys = [_src_key(s) for s in c_src]
    b_set, c_set = set(b_keys), set(c_keys)
    overlap = len(b_set & c_set)
    union = len(b_set | c_set) or 1
    changes: list[str] = []
    if flags.get("use_pre") and flags.get("strategy") not in {None, "", "none"}:
        rewritten = c_pre.get("rewritten_query") or c_pre.get("step_back_query") or c_pre.get("hyde_doc")
        if rewritten:
            changes.append(
                f"检索前（{flags.get('strategy')}）：「{_snip(b_pre.get('original_query') or '', 40)}」→「{_snip(str(rewritten), 60)}」"
            )
        elif c_q and b_q and c_q[0] != b_q[0]:
            changes.append(f"检索查询变化：{_snip(b_q[0], 40)} → {_snip(c_q[0], 40)}")
        else:
            changes.append("已开检索前优化，查询句可能已清洗/重写")
    if int(flags.get("num_queries") or 1) > 1:
        changes.append(f"Multi-Query：{len(c_q)} 路查询再融合")
    if flags.get("use_hybrid"):
        changes.append(f"混合检索：{flags.get('fusion_mode') or 'reciprocal_rerank'}")
    if flags.get("use_rerank"):
        changes.append("检索后重排序已改变片段顺序/去留")
    if flags.get("use_compress"):
        changes.append("上下文压缩：可能删掉低相关句子")
    if flags.get("use_crag"):
        crag = current.get("crag") or {}
        changes.append(f"CRAG：{crag.get('before_count', '?')} → {crag.get('after_count', '?')} 篇（{crag.get('message') or ''}）")
    only_opt = [k for k in c_keys if k not in b_set]
    only_base = [k for k in b_keys if k not in c_set]
    if only_opt:
        changes.append(f"优化后新召回 {len(only_opt)} 条")
    if only_base:
        changes.append(f"优化后不再召回 {len(only_base)} 条")
    if b_ans != c_ans:
        changes.append("最终答案已改变")
    else:
        changes.append("答案文本与基础 RAG 相同（召回或查询仍可能不同）")
    return {
        "enabled": True,
        "message": "已对照基础 RAG（关闭检索前/后优化）",
        "answer_changed": b_ans != c_ans,
        "query_changed": list(b_q) != list(c_q),
        "source_overlap": overlap,
        "source_union": union,
        "changes": changes,
        "baseline_answer": b_ans,
        "baseline_queries": [str(q) for q in b_q if q],
        "current_queries": [str(q) for q in c_q if q],
        "baseline_sources": [{"rank": s.get("rank"), "preview": _snip(s.get("document") or "")} for s in b_src],
        "current_sources": [{"rank": s.get("rank"), "preview": _snip(s.get("document") or "")} for s in c_src],
        "only_in_optimized": only_opt[:5],
        "only_in_baseline": only_base[:5],
    }
