"""/ask 管线上的具体算子。每个类只做一件事，由 AskPipeline 顺序调用。"""

from __future__ import annotations

from llama_index.core.prompts import PromptTemplate
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.schema import NodeWithScore

from semantic_search.app.config import RAG_SYSTEM_PROMPT, SELF_RAG_VERBOSE
from semantic_search.app.knowledge_scope import DEFAULT_SCOPE, filter_nodes_by_scope, normalize_scope
from semantic_search.app.service.crag import apply_crag, filter_relevant_nodes
from semantic_search.app.service.pipeline import (
    AskContext,
    AskModule,
    context_from_nodes,
    empty_eval,
    format_source,
    merge_nodes_rrf,
)
from semantic_search.app.service.pre_retrieval import prepare_retrieval_queries
from semantic_search.app.service.rag_eval import evaluate_generation
from semantic_search.app.service.retrieval_optimize import apply_postprocessors
from semantic_search.app.service.self_rag import (
    apply_self_rag_post_generate,
    decide_retrieve,
    judge_isuse,
)

ASK_QA_PROMPT = PromptTemplate(
    f"{RAG_SYSTEM_PROMPT}。"
    "只依据给定上下文回答。上下文里可能同时有「知识库文档」和「网页搜索」片段；"
    "知识库优先，网页只作补充，引用网页时写出标题或网址。"
    "请把上下文中与问题相关的要点尽量归纳完整；"
    "仅当上下文完全没有相关信息时才说不知道，不要因为只命中部分片段就断言知识库没有。\n\n"
    "上下文：\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "问题：{query_str}\n"
    "回答："
)


class RetrieveGateModule(AskModule):
    """Self-RAG Retrieve：闲聊可不查库。"""

    name = "retrieve_gate"
    module_type = "Generation"

    def should_run(self, ctx: AskContext) -> bool:
        return bool(ctx.flags.get("use_self_rag"))

    def run(self, ctx: AskContext) -> None:
        ctx.self_rag["enabled"] = True
        need = decide_retrieve(ctx.question, llm=ctx.llm, verbose=SELF_RAG_VERBOSE)
        ctx.self_rag["retrieve"] = need
        if need:
            return
        ctx.skip_retrieve = True
        ctx.answer = ctx.llm.complete(ctx.question).text.strip()
        ctx.self_rag["skipped_retrieval"] = True
        ctx.self_rag["message"] = "no_retrieve_direct_answer"
        ctx.self_rag["isuse"] = judge_isuse(
            ctx.question, ctx.answer, llm=ctx.llm, verbose=SELF_RAG_VERBOSE
        )


class EmptyCorpusModule(AskModule):
    """向量库为空且未开图谱时直接提示。"""

    name = "empty_corpus"
    module_type = "Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        if ctx.flags.get("use_web"):
            return False
        return (not ctx.skip_retrieve) and ctx.corpus_size == 0 and not ctx.flags.get("use_graph")

    def run(self, ctx: AskContext) -> None:
        ctx.skip_retrieve = True
        ctx.answer = "知识库为空，请先上传或导入文档后再提问。"


class PreRetrievalModule(AskModule):
    name = "pre_retrieval"
    module_type = "Pre-Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        return not ctx.skip_retrieve

    def run(self, ctx: AskContext) -> None:
        strategy = ctx.flags.get("strategy") or "none"
        ctx.pre_retrieval = prepare_retrieval_queries(
            ctx.question, strategy, llm=ctx.llm
        )


class VectorRetrieveModule(AskModule):
    name = "vector_retrieve"
    module_type = "Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        return (not ctx.skip_retrieve) and ctx.corpus_size > 0

    def run(self, ctx: AskContext) -> None:
        flags = ctx.flags
        queries = ctx.pre_retrieval.get("retrieval_queries") or [ctx.question]
        retriever = ctx.engine._build_retriever(
            max(ctx.k * 4, 20),
            hybrid_enabled=bool(flags.get("use_hybrid")),
            num_queries=max(1, int(flags.get("num_queries") or 1)),
            fusion_mode=flags.get("fusion_mode"),
            doc_scope=flags.get("doc_scope"),
        )
        ranked: list[list[NodeWithScore]] = [
            filter_nodes_by_scope(list(retriever.retrieve(q)), flags.get("doc_scope"))
            for q in queries
        ]
        fuse_k = max(ctx.k, min(ctx.corpus_size, ctx.k * 2))
        ctx.nodes = (
            merge_nodes_rrf(ranked, k=fuse_k)
            if len(ranked) > 1
            else (ranked[0][:fuse_k] if ranked else [])
        )
        if ctx.nodes or normalize_scope(flags.get("doc_scope")) == "all":
            return
        wide = ctx.engine._build_retriever(
            max(ctx.k * 4, 20),
            hybrid_enabled=bool(flags.get("use_hybrid")),
            num_queries=max(1, int(flags.get("num_queries") or 1)),
            fusion_mode=flags.get("fusion_mode"),
            doc_scope="all",
        )
        ctx.nodes = filter_nodes_by_scope(list(wide.retrieve(queries[0])), "all")[:fuse_k]
        if ctx.nodes:
            flags["doc_scope"] = "all"
            flags["scope_note"] = ((flags.get("scope_note") or "") + "；当前范围无命中，已扩大到全部文档").strip("；")


class PostRetrieveModule(AskModule):
    name = "post_retrieve"
    module_type = "Post-Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        return (not ctx.skip_retrieve) and bool(ctx.nodes)

    def run(self, ctx: AskContext) -> None:
        flags = ctx.flags
        ctx.nodes = apply_postprocessors(
            ctx.nodes,
            ctx.question,
            ctx.k,
            rerank_enabled=bool(flags.get("use_rerank")),
            compress_enabled=bool(flags.get("use_compress")),
            reorder_enabled=bool(flags.get("use_reorder")),
        )


class CragModule(AskModule):
    name = "crag"
    module_type = "Generation"

    def should_run(self, ctx: AskContext) -> bool:
        if ctx.skip_retrieve or ctx.corpus_size == 0:
            return False
        return bool(ctx.flags.get("use_crag") or ctx.flags.get("use_self_rag"))

    def run(self, ctx: AskContext) -> None:
        flags = ctx.flags
        retrieve_fn = getattr(ctx, "retrieve_retry", None)
        if flags.get("use_crag"):
            ctx.nodes, ctx.crag = apply_crag(
                ctx.question,
                ctx.nodes,
                retrieve_fn=retrieve_fn,
                llm=ctx.llm,
                enabled=True,
            )
            if flags.get("use_self_rag"):
                ctx.self_rag["isrel_shared_with_crag"] = True
            return
        if flags.get("use_self_rag") and ctx.nodes:
            ctx.nodes, details = filter_relevant_nodes(
                ctx.question, ctx.nodes, llm=ctx.llm, verbose=SELF_RAG_VERBOSE
            )
            ctx.crag = {
                "enabled": False,
                "rewritten_query": None,
                "retried": False,
                "before_count": len(details),
                "after_count": len(ctx.nodes),
                "eval": details,
                "message": "self_rag_isrel_only",
            }


class GraphRetrieveModule(AskModule):
    name = "graph_retrieve"
    module_type = "Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        return (not ctx.skip_retrieve) and bool(ctx.flags.get("use_graph"))

    def run(self, ctx: AskContext) -> None:
        if ctx.graph_rag is None:
            ctx.graph = {
                "enabled": True,
                "ok": False,
                "message": "图谱未就绪：请先 neo4j console，并在侧栏构建/加载图谱",
                "total": 0,
                "results": [],
            }
            return
        graph_nodes, info = ctx.graph_rag.retrieve_as_nodes(ctx.question, k=ctx.k)
        ctx.graph = info
        if graph_nodes:
            ctx.nodes = list(graph_nodes) + list(ctx.nodes)


class WebSearchModule(AskModule):
    name = "web_search"
    module_type = "Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        return bool(ctx.flags.get("use_web")) and not ctx.skip_retrieve

    def run(self, ctx: AskContext) -> None:
        from semantic_search.app.service.web_search import search_web

        prep = ctx.pre_retrieval or {}
        queries = prep.get("retrieval_queries") or []
        query = str((queries[0] if queries else "") or ctx.question).strip()
        print(f"[联网] 正在请求 Tavily：{query[:80]}", flush=True)
        info = search_web(query, max_results=min(ctx.k, 5))
        print(f"[联网] {info.get('message') or '结束'}", flush=True)
        ctx.web = {
            "enabled": True,
            "ok": bool(info.get("ok")),
            "message": info.get("message") or "",
            "query": info.get("query") or query,
            "total": int(info.get("total") or 0),
            "results": info.get("results") or [],
        }
        web_nodes = list(info.get("nodes") or [])
        if web_nodes:
            ctx.nodes = list(ctx.nodes) + web_nodes


class GenerateModule(AskModule):
    name = "generate"
    module_type = "Generation"

    def should_run(self, ctx: AskContext) -> bool:
        return not ctx.skip_retrieve

    def run(self, ctx: AskContext) -> None:
        if not ctx.nodes:
            flags = ctx.flags
            if flags.get("use_web"):
                ctx.answer = "知识库和联网搜索都没有足够相关的信息。可换个问法，或确认 Tavily 额度/网络。"
            elif flags.get("use_crag") or flags.get("use_self_rag"):
                ctx.answer = "知识库中没有足够相关信息回答该问题（Corrective RAG / ISREL 过滤后为空）。"
            else:
                ctx.answer = "知识库中没有检索到相关信息，请换个问法、先导入文档，或勾选「联网」。"
            ctx.sources = []
            return
        n = len(ctx.nodes)
        if ctx.flags.get("use_think"):
            print(f"[生成] 深度思考中（{n} 段上下文）…", flush=True)
            from semantic_search.app.service.deep_think import run_deep_think

            answer, thinking = run_deep_think(ctx.question, ctx.nodes, ctx.llm)
            ctx.answer = answer
            ctx.thinking = thinking
        else:
            print(f"[生成] 正在调用 DeepSeek（{n} 段上下文）…", flush=True)
            synthesizer = get_response_synthesizer(
                response_mode="compact",
                text_qa_template=ASK_QA_PROMPT,
                llm=ctx.llm,
            )
            ctx.answer = str(synthesizer.synthesize(query=ctx.question, nodes=ctx.nodes)).strip()
        print("[生成] 回答已完成", flush=True)
        ctx.sources = [format_source(i + 1, item) for i, item in enumerate(ctx.nodes)]


class SelfRagPostModule(AskModule):
    name = "self_rag_post"
    module_type = "Generation"

    def should_run(self, ctx: AskContext) -> bool:
        return bool(ctx.flags.get("use_self_rag")) and (not ctx.skip_retrieve) and bool(ctx.nodes)

    def run(self, ctx: AskContext) -> None:
        context = context_from_nodes(ctx.nodes)
        ctx.answer, post_info = apply_self_rag_post_generate(
            ctx.question,
            ctx.answer,
            context,
            llm=ctx.llm,
            enabled=True,
        )
        ctx.self_rag.update(post_info)
        ctx.self_rag["enabled"] = True
        ctx.self_rag["retrieve"] = True
        ctx.self_rag["skipped_retrieval"] = False


class EvalModule(AskModule):
    name = "generation_eval"
    module_type = "Generation"

    def run(self, ctx: AskContext) -> None:
        if not ctx.flags.get("use_eval"):
            ctx.generation_eval = empty_eval()
            return
        if ctx.answer.startswith("知识库为空"):
            ctx.generation_eval = empty_eval()
            return
        ctx.generation_eval = evaluate_generation(
            ctx.question,
            ctx.answer,
            ctx.sources,
            reference=ctx.reference,
            llm=ctx.llm,
        )


def default_ask_modules() -> list[AskModule]:
    """默认 /ask 算子顺序。增删模块只改这一处。"""
    return [
        RetrieveGateModule(),
        EmptyCorpusModule(),
        PreRetrievalModule(),
        VectorRetrieveModule(),
        PostRetrieveModule(),
        CragModule(),
        GraphRetrieveModule(),
        WebSearchModule(),
        GenerateModule(),
        SelfRagPostModule(),
        EvalModule(),
    ]
