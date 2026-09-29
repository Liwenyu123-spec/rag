"""检索中（混合召回）与检索后（重排/压缩/重排版）工具。"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, List, Optional

from llama_index.core import Settings
from llama_index.core.schema import NodeWithScore, TextNode

from semantic_search.app.config import (
    COMPRESS_ENABLED,
    COMPRESS_PERCENTILE,
    DASHSCOPE_API_KEY,
    HYBRID_ENABLED,
    HYBRID_FUSION_MODE,
    REORDER_ENABLED,
    RERANK_ENABLED,
    RERANK_MODEL,
    RERANK_PROVIDER,
    RERANK_TOP_N,
    RETRIEVE_CANDIDATES,
    SIMILARITY_TOP_K,
)

if TYPE_CHECKING:
    from llama_index.core.base.base_retriever import BaseRetriever
    from llama_index.core.indices.base import BaseIndex
    from llama_index.core.postprocessor.types import BaseNodePostprocessor


def chinese_sentence_splitter(text: str) -> List[str]:
    """按中英文句末标点切句，供 SentenceEmbeddingOptimizer 使用。"""
    parts = re.split(r"[。！？；\n!?;]+", text or "")
    return [p.strip() for p in parts if p.strip()]


def candidate_top_k(final_k: int) -> int:
    """粗排候选数：至少 final_k，且不小于配置的 RETRIEVE_CANDIDATES。"""
    final_k = max(1, int(final_k or SIMILARITY_TOP_K))
    return max(final_k, RETRIEVE_CANDIDATES, final_k * 2)


def rerank_top_n(final_k: int) -> int:
    """精排保留条数。"""
    final_k = max(1, int(final_k or SIMILARITY_TOP_K))
    if RERANK_TOP_N and RERANK_TOP_N > 0:
        return max(1, min(RERANK_TOP_N, final_k) if RERANK_TOP_N < final_k else RERANK_TOP_N)
    return final_k


def nodes_from_index(index: "BaseIndex", collection: Any = None) -> List[TextNode]:
    """取出可供 BM25 使用的节点；docstore 为空时从 Chroma 回灌文本。"""
    docs = getattr(getattr(index, "docstore", None), "docs", None) or {}
    if docs:
        return list(docs.values())

    if collection is None:
        return []

    try:
        data = collection.get(include=["documents", "metadatas"])
    except Exception as exc:  # noqa: BLE001
        print(f"警告: 从 Chroma 读取 BM25 语料失败: {exc}")
        return []

    ids = data.get("ids") or []
    documents = data.get("documents") or []
    metadatas = data.get("metadatas") or []
    nodes: List[TextNode] = []
    for i, doc_id in enumerate(ids):
        text = (documents[i] if i < len(documents) else "") or ""
        text = text.strip()
        if not text:
            continue
        meta = metadatas[i] if i < len(metadatas) and isinstance(metadatas[i], dict) else {}
        nodes.append(TextNode(text=text, id_=str(doc_id), metadata=meta or {}))
    return nodes


def build_hybrid_retriever(
    index: "BaseIndex",
    *,
    final_k: int,
    collection: Any = None,
    nodes_cache: Optional[List[Any]] = None,
    hybrid_enabled: Optional[bool] = None,
) -> "BaseRetriever":
    """同库混合：稠密向量 + BM25，经 QueryFusionRetriever 融合。失败则回退纯向量。"""
    cand_k = candidate_top_k(final_k)
    vector_retriever = index.as_retriever(similarity_top_k=cand_k)

    use_hybrid = HYBRID_ENABLED if hybrid_enabled is None else bool(hybrid_enabled)
    if not use_hybrid:
        return vector_retriever

    try:
        import jieba
        from llama_index.core.retrievers import QueryFusionRetriever
        from llama_index.retrievers.bm25 import BM25Retriever
    except ImportError as exc:
        print(f"警告: 混合检索依赖缺失（jieba / bm25），回退纯向量: {exc}")
        return vector_retriever

    nodes = list(nodes_cache) if nodes_cache is not None else nodes_from_index(index, collection)
    if len(nodes) < 2:
        print("警告: 可用于 BM25 的节点不足，回退纯向量检索")
        return vector_retriever

    try:
        bm25_retriever = BM25Retriever.from_defaults(
            nodes=nodes,
            similarity_top_k=cand_k,
            tokenizer=lambda t: list(jieba.cut(t or "")),
        )
        mode = HYBRID_FUSION_MODE or "reciprocal_rerank"
        return QueryFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            similarity_top_k=cand_k,
            num_queries=1,
            mode=mode,
            use_async=False,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"警告: 构建混合检索器失败，回退纯向量: {exc}")
        return vector_retriever


def _build_reranker(top_n: int) -> Any | None:
    """构建重排器：默认本地 bge；仅 RERANK_PROVIDER=dashscope 时用千问。"""
    provider = (RERANK_PROVIDER or "local").strip().lower()

    if provider in {"dashscope", "qwen", "aliyun"}:
        if not DASHSCOPE_API_KEY:
            print("警告: RERANK_PROVIDER=dashscope 但未配置 DASHSCOPE_API_KEY，跳过重排")
            return None
        try:
            from llama_index.postprocessor.dashscope_rerank import DashScopeRerank

            print(f"重排: DashScopeRerank({RERANK_MODEL}), top_n={top_n}")
            return DashScopeRerank(
                model=RERANK_MODEL,
                top_n=top_n,
                api_key=DASHSCOPE_API_KEY,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"警告: 初始化 DashScopeRerank 失败，跳过重排: {exc}")
            return None

    # 默认：本地 Cross-Encoder，不需要千问 Key
    try:
        from llama_index.core.postprocessor import SentenceTransformerRerank

        model_name = RERANK_MODEL or "BAAI/bge-reranker-base"
        print(f"重排: 本地 SentenceTransformerRerank({model_name}), top_n={top_n}")
        return SentenceTransformerRerank(model=model_name, top_n=top_n)
    except Exception as exc:  # noqa: BLE001
        print(f"警告: 本地重排初始化失败（可 pip install sentence-transformers）: {exc}")
        return None


def build_node_postprocessors(
    final_k: int,
    *,
    rerank_enabled: Optional[bool] = None,
    compress_enabled: Optional[bool] = None,
    reorder_enabled: Optional[bool] = None,
) -> List["BaseNodePostprocessor"]:
    """按配置（可被请求覆盖）组装：重排 → 压缩 → 长上下文重排。"""
    processors: List[Any] = []
    top_n = rerank_top_n(final_k)
    do_rerank = RERANK_ENABLED if rerank_enabled is None else bool(rerank_enabled)
    do_compress = COMPRESS_ENABLED if compress_enabled is None else bool(compress_enabled)
    do_reorder = REORDER_ENABLED if reorder_enabled is None else bool(reorder_enabled)

    if do_rerank and RERANK_PROVIDER not in {"", "none", "off", "false"}:
        reranker = _build_reranker(top_n)
        if reranker is not None:
            processors.append(reranker)

    if do_compress:
        try:
            from llama_index.core.postprocessor import SentenceEmbeddingOptimizer

            processors.append(
                SentenceEmbeddingOptimizer(
                    embed_model=Settings.embed_model,
                    percentile_cutoff=COMPRESS_PERCENTILE,
                    tokenizer_fn=chinese_sentence_splitter,
                )
            )
        except Exception as exc:  # noqa: BLE001
            print(f"警告: 初始化 SentenceEmbeddingOptimizer 失败，跳过压缩: {exc}")

    if do_reorder:
        try:
            from llama_index.core.postprocessor import LongContextReorder

            processors.append(LongContextReorder())
        except Exception as exc:  # noqa: BLE001
            print(f"警告: 初始化 LongContextReorder 失败，跳过重排版: {exc}")

    return processors


def apply_postprocessors(
    nodes: List[NodeWithScore],
    query: str,
    final_k: int,
    processors: Optional[List["BaseNodePostprocessor"]] = None,
    *,
    rerank_enabled: Optional[bool] = None,
    compress_enabled: Optional[bool] = None,
    reorder_enabled: Optional[bool] = None,
) -> List[NodeWithScore]:
    """对已召回节点串行跑后处理器（供 /ask 手工 synthesize 路径使用）。"""
    if not nodes:
        return []
    procs = processors if processors is not None else build_node_postprocessors(
        final_k,
        rerank_enabled=rerank_enabled,
        compress_enabled=compress_enabled,
        reorder_enabled=reorder_enabled,
    )
    current = list(nodes)
    for proc in procs:
        try:
            current = list(proc.postprocess_nodes(current, query_str=query))
        except TypeError:
            # 少数后处理器只接受 query_bundle
            from llama_index.core.schema import QueryBundle

            current = list(proc.postprocess_nodes(current, query_bundle=QueryBundle(query_str=query)))
        except Exception as exc:  # noqa: BLE001
            print(f"警告: 后处理器 {type(proc).__name__} 失败，跳过该步: {exc}")
    return current[: max(1, int(final_k or SIMILARITY_TOP_K))]
