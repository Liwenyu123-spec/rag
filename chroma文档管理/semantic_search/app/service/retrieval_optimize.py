"""检索中（混合召回）与检索后（重排/压缩/重排版）工具。"""  # 模块说明：混合检索与后处理流水线

from __future__ import annotations  # 允许注解里使用尚未定义的前向类型

import re  # 中英文句末切分用正则
from typing import TYPE_CHECKING, Any, List, Optional  # 类型注解与运行期可选依赖

from llama_index.core import Settings  # 取全局 embed_model 供压缩器用
from llama_index.core.schema import NodeWithScore, TextNode  # 召回节点与文本节点

from semantic_search.app.config import (  # 从配置读取检索/后处理开关与参数
    COMPRESS_ENABLED,  # 是否启用上下文压缩
    COMPRESS_PERCENTILE,  # 压缩保留百分位阈值
    DASHSCOPE_API_KEY,  # 千问重排所需 Key
    HYBRID_ENABLED,  # 是否默认开混合检索
    HYBRID_FUSION_MODE,  # 融合模式（如 reciprocal_rerank）
    REORDER_ENABLED,  # 是否启用长上下文重排版
    RERANK_ENABLED,  # 是否启用精排
    RERANK_MODEL,  # 重排模型名
    RERANK_PROVIDER,  # 重排提供方：local / dashscope
    RERANK_TOP_N,  # 精排保留条数上限
    RETRIEVE_CANDIDATES,  # 粗排候选数下限
    SIMILARITY_TOP_K,  # 默认最终 Top-K
)  # 括号结束

if TYPE_CHECKING:  # 仅类型检查导入，避免运行期循环依赖
    from llama_index.core.base.base_retriever import BaseRetriever  # 检索器基类注解
    from llama_index.core.indices.base import BaseIndex  # 索引基类注解
    from llama_index.core.postprocessor.types import BaseNodePostprocessor  # 后处理器注解


def chinese_sentence_splitter(text: str) -> List[str]:  # 中英文友好的句子切分
    """按中英文句末标点 / 空行切句（对齐 ModularRAG demo）。"""  # 供 SentenceEmbeddingOptimizer 用
    parts = re.split(r"[。！？；!?;]+|\n{2,}", text or "")  # 按句号问叹分号或空行切开
    return [p.strip() for p in parts if p.strip()]  # 去掉空白片段后返回


def candidate_top_k(final_k: int) -> int:  # 计算粗排候选数
    """粗排候选数：至少 final_k，且不小于配置的 RETRIEVE_CANDIDATES。"""  # 给重排留余量
    final_k = max(1, int(final_k or SIMILARITY_TOP_K))  # 规范化最终 K，至少为 1
    return max(final_k, RETRIEVE_CANDIDATES, final_k * 2)  # 取三者最大作为候选数


def rerank_top_n(final_k: int) -> int:  # 计算精排保留条数
    """精排保留条数。"""  # 受 RERANK_TOP_N 与 final_k 共同约束
    final_k = max(1, int(final_k or SIMILARITY_TOP_K))  # 规范化最终 K
    if RERANK_TOP_N and RERANK_TOP_N > 0:  # 配置了正的 TOP_N
        return max(1, min(RERANK_TOP_N, final_k) if RERANK_TOP_N < final_k else RERANK_TOP_N)  # 小于 final_k 则取较小者
    return final_k  # 未配置则等于最终 K


def nodes_from_index(index: "BaseIndex", collection: Any = None) -> List[TextNode]:  # 取出 BM25 语料节点
    """取出可供 BM25 使用的节点；docstore 为空时从 Chroma 回灌文本。"""  # 向量索引未必持久化 docstore
    docs = getattr(getattr(index, "docstore", None), "docs", None) or {}  # 尝试读内存 docstore
    if docs:  # docstore 有内容
        return list(docs.values())  # 直接返回节点列表

    if collection is None:  # 没有 Chroma collection 可回灌
        return []  # 无语料，调用方应回退纯向量

    try:  # 从 Chroma 拉文档与元数据
        data = collection.get(include=["documents", "metadatas"])  # 只要正文和 metadata
    except Exception as exc:  # noqa: BLE001  # 读库失败不抛穿
        print(f"警告: 从 Chroma 读取 BM25 语料失败: {exc}")  # 打警告
        return []  # 返回空，上层回退

    ids = data.get("ids") or []  # 文档 id 列表
    documents = data.get("documents") or []  # 正文列表
    metadatas = data.get("metadatas") or []  # 元数据列表
    nodes: List[TextNode] = []  # 组装结果
    for i, doc_id in enumerate(ids):  # 按 id 对齐下标
        text = (documents[i] if i < len(documents) else "") or ""  # 取对应正文
        text = text.strip()  # 去首尾空白
        if not text:  # 空文本对 BM25 无意义
            continue  # 跳过
        meta = metadatas[i] if i < len(metadatas) and isinstance(metadatas[i], dict) else {}  # 安全取 metadata
        nodes.append(TextNode(text=text, id_=str(doc_id), metadata=meta or {}))  # 建成 TextNode
    return nodes  # 返回可喂给 BM25 的节点


def build_hybrid_retriever(  # 构建混合 / Multi-Query 检索器
    index: "BaseIndex",  # 向量索引
    *,  # 之后仅关键字参数
    final_k: int,  # 最终希望的 Top-K（用于推候选数）
    collection: Any = None,  # 可选 Chroma collection，供 BM25 回灌
    nodes_cache: Optional[List[Any]] = None,  # 可选预缓存节点，避免重复读库
    hybrid_enabled: Optional[bool] = None,  # 请求级覆盖混合开关
    num_queries: Optional[int] = None,  # Multi-Query 查询变体数
    fusion_mode: Optional[str] = None,  # 融合模式覆盖
) -> "BaseRetriever":  # 返回可 retrieve 的检索器
    """同库混合：稠密向量 + BM25，经 QueryFusionRetriever 融合。

    num_queries>1 时启用 Multi-Query（对齐 ModularRAG）：LLM 生成查询变体再融合。
    """  # 检索中阶段核心入口
    cand_k = candidate_top_k(final_k)  # 粗排候选数
    vector_retriever = index.as_retriever(similarity_top_k=cand_k)  # 稠密向量检索器

    use_hybrid = HYBRID_ENABLED if hybrid_enabled is None else bool(hybrid_enabled)  # 解析是否混合
    n_queries = max(1, int(num_queries if num_queries is not None else 1))  # Multi-Query 路数至少 1
    mode = (fusion_mode or HYBRID_FUSION_MODE or "reciprocal_rerank").strip()  # 融合模式默认 RRF

    if not use_hybrid:  # 不开混合则走纯向量（可挂 Multi-Query）
        # 纯向量也可挂 Multi-Query（只用一路检索器）
        if n_queries <= 1:  # 不需要多查询变体
            return vector_retriever  # 直接返回向量检索器
        try:  # 尝试包一层 QueryFusion 做 Multi-Query
            from llama_index.core.retrievers import QueryFusionRetriever  # 融合检索器

            return QueryFusionRetriever(  # 单路检索器 + 多查询变体
                retrievers=[vector_retriever],  # 仅向量一路
                similarity_top_k=cand_k,  # 融合后保留候选数
                num_queries=n_queries,  # LLM 生成的查询数
                mode=mode if mode != "simple" else "reciprocal_rerank",  # simple 时改用 RRF
                use_async=False,  # 同步执行，避免事件循环问题
            )  # 括号结束
        except Exception as exc:  # noqa: BLE001  # 构建失败则降级
            print(f"警告: Multi-Query 构建失败，回退纯向量: {exc}")  # 打警告
            return vector_retriever  # 回退纯向量

    try:  # 混合依赖：jieba 分词 + BM25 + 融合
        import jieba  # 中文分词，供 BM25 tokenizer
        from llama_index.core.retrievers import QueryFusionRetriever  # 融合检索器
        from llama_index.retrievers.bm25 import BM25Retriever  # 稀疏 BM25 检索
    except ImportError as exc:  # 缺依赖
        print(f"警告: 混合检索依赖缺失（jieba / bm25），回退纯向量: {exc}")  # 提示安装
        return vector_retriever  # 回退纯向量

    nodes = list(nodes_cache) if nodes_cache is not None else nodes_from_index(index, collection)  # 取 BM25 语料
    if len(nodes) < 2:  # 节点太少 BM25 意义不大
        print("警告: 可用于 BM25 的节点不足，回退纯向量检索")  # 打警告
        return vector_retriever  # 回退纯向量

    try:  # 构建 BM25 + 向量融合
        bm25_retriever = BM25Retriever.from_defaults(  # 稀疏检索器
            nodes=nodes,  # BM25 语料
            similarity_top_k=cand_k,  # 稀疏侧候选数
            tokenizer=lambda t: list(jieba.cut(t or "")),  # 中文分词 tokenizer
        )  # 括号结束
        return QueryFusionRetriever(  # 双路融合
            retrievers=[vector_retriever, bm25_retriever],  # 稠密 + 稀疏
            similarity_top_k=cand_k,  # 融合后候选数
            num_queries=n_queries,  # 可叠加 Multi-Query
            mode=mode,  # 融合模式
            use_async=False,  # 同步
        )  # 括号结束
    except Exception as exc:  # noqa: BLE001  # 构建失败降级
        print(f"警告: 构建混合检索器失败，回退纯向量: {exc}")  # 打警告
        return vector_retriever  # 回退纯向量


_local_reranker = None
_local_reranker_key: tuple | None = None


def _build_reranker(top_n: int) -> Any | None:  # 按配置构建重排器
    """构建重排器：默认本地 bge；仅 RERANK_PROVIDER=dashscope 时用千问。"""  # 本地优先，省 Key
    from pathlib import Path

    provider = (RERANK_PROVIDER or "local").strip().lower()  # 规范化提供方名

    if provider in {"dashscope", "qwen", "aliyun"}:  # 走云侧重排
        if not DASHSCOPE_API_KEY:  # 缺 Key
            print("警告: RERANK_PROVIDER=dashscope 但未配置 DASHSCOPE_API_KEY，跳过重排")  # 提示配置
            return None  # 跳过重排
        try:  # 初始化千问重排
            from llama_index.postprocessor.dashscope_rerank import DashScopeRerank  # 千问后处理器

            print(f"重排: DashScopeRerank({RERANK_MODEL}), top_n={top_n}")  # 日志
            return DashScopeRerank(  # 返回云侧重排器
                model=RERANK_MODEL,  # 模型名
                top_n=top_n,  # 保留条数
                api_key=DASHSCOPE_API_KEY,  # API Key
            )  # 括号结束
        except Exception as ext:  # noqa: BLE001  # 初始化失败
            print(f"警告: 初始化 DashScopeRerank 失败，跳过重排: {ext}")  # 打警告
            return None  # 跳过重排

    global _local_reranker, _local_reranker_key
    model_name = RERANK_MODEL or r"H:\二阶段\bge-reranker-base"
    model_path = Path(model_name)
    cache_key = (str(model_path.resolve()) if model_path.exists() else model_name, int(top_n))
    if _local_reranker is not None and _local_reranker_key and _local_reranker_key[0] == cache_key[0]:
        _local_reranker.top_n = top_n
        return _local_reranker

    if not model_path.is_dir():
        print(
            f"警告: 本地重排模型不存在（{model_path}），跳过重排。"
            "请将 bge-reranker-base 放到该目录，避免运行时访问 Hugging Face。"
        )
        return None

    try:
        from llama_index.core.postprocessor import SentenceTransformerRerank
        from sentence_transformers import CrossEncoder

        print(f"重排: 本地 SentenceTransformerRerank({model_path}), top_n={top_n}")
        reranker = SentenceTransformerRerank(model=str(model_path.resolve()), top_n=top_n)
        reranker._model = CrossEncoder(
            str(model_path.resolve()),
            max_length=getattr(reranker._model, "max_length", 512),
            device=reranker.device,
            trust_remote_code=True,
            local_files_only=True,
        )
        _local_reranker = reranker
        _local_reranker_key = cache_key
        return reranker
    except Exception as exc:  # noqa: BLE001
        print(f"警告: 本地重排初始化失败（可 pip install sentence-transformers）: {exc}")
        return None


def build_node_postprocessors(  # 组装后处理器流水线
    final_k: int,  # 最终 Top-K，影响精排条数
    *,  # 之后仅关键字参数
    rerank_enabled: Optional[bool] = None,  # 请求级覆盖重排开关
    compress_enabled: Optional[bool] = None,  # 请求级覆盖压缩开关
    reorder_enabled: Optional[bool] = None,  # 请求级覆盖重排版开关
) -> List["BaseNodePostprocessor"]:  # 有序后处理器列表
    """按配置（可被请求覆盖）组装：重排 → 压缩 → 长上下文重排。"""  # 顺序固定，先精排再压缩
    processors: List[Any] = []  # 结果列表
    top_n = rerank_top_n(final_k)  # 精排保留条数
    do_rerank = RERANK_ENABLED if rerank_enabled is None else bool(rerank_enabled)  # 是否重排
    do_compress = COMPRESS_ENABLED if compress_enabled is None else bool(compress_enabled)  # 是否压缩
    do_reorder = REORDER_ENABLED if reorder_enabled is None else bool(reorder_enabled)  # 是否重排版

    if do_rerank and RERANK_PROVIDER not in {"", "none", "off", "false"}:  # 开着重排且未显式关闭提供方
        reranker = _build_reranker(top_n)  # 尝试构建重排器
        if reranker is not None:  # 构建成功
            processors.append(reranker)  # 加入流水线

    if do_compress:  # 启用句级嵌入压缩
        try:  # 初始化压缩器
            from llama_index.core.postprocessor import SentenceEmbeddingOptimizer  # 按句相关度裁剪

            processors.append(  # 加入压缩后处理器
                SentenceEmbeddingOptimizer(  # 句嵌入优化器
                    embed_model=Settings.embed_model,  # 与检索同套嵌入
                    percentile_cutoff=COMPRESS_PERCENTILE,  # 保留高分百分位
                    tokenizer_fn=chinese_sentence_splitter,  # 中文切句函数
                )  # 括号结束
            )  # 括号结束
        except Exception as exc:  # noqa: BLE001  # 初始化失败则跳过压缩
            print(f"警告: 初始化 SentenceEmbeddingOptimizer 失败，跳过压缩: {exc}")  # 打警告

    if do_reorder:  # 启用长上下文重排版（中间位置偏见缓解）
        try:  # 初始化重排版
            from llama_index.core.postprocessor import LongContextReorder  # 头尾重排

            processors.append(LongContextReorder())  # 加入流水线
        except Exception as exc:  # noqa: BLE001  # 失败则跳过
            print(f"警告: 初始化 LongContextReorder 失败，跳过重排版: {exc}")  # 打警告

    return processors  # 返回组装好的后处理器列表


def apply_postprocessors(  # 对已召回节点串行跑后处理
    nodes: List[NodeWithScore],  # 粗排召回节点
    query: str,  # 当前查询串
    final_k: int,  # 最终截断条数
    processors: Optional[List["BaseNodePostprocessor"]] = None,  # 可外部注入处理器链
    *,  # 之后仅关键字参数
    rerank_enabled: Optional[bool] = None,  # 未注入时传给 build
    compress_enabled: Optional[bool] = None,  # 未注入时传给 build
    reorder_enabled: Optional[bool] = None,  # 未注入时传给 build
) -> List[NodeWithScore]:  # 处理后的 Top-K 节点
    """对已召回节点串行跑后处理器（供 /ask 手工 synthesize 路径使用）。"""  # 与引擎 QueryEngine 路径对齐
    if not nodes:  # 无节点可处理
        return []  # 直接空列表
    procs = processors if processors is not None else build_node_postprocessors(  # 有注入用注入，否则现建
        final_k,  # 最终 K
        rerank_enabled=rerank_enabled,  # 重排覆盖
        compress_enabled=compress_enabled,  # 压缩覆盖
        reorder_enabled=reorder_enabled,  # 重排版覆盖
    )  # 括号结束
    current = list(nodes)  # 可变副本，避免改动调用方列表
    for proc in procs:  # 按顺序跑每个后处理器
        try:  # 优先用 query_str 关键字
            current = list(proc.postprocess_nodes(current, query_str=query))  # 标准调用
        except TypeError:  # 少数后处理器签名不同
            # 少数后处理器只接受 query_bundle
            from llama_index.core.schema import QueryBundle  # 延迟导入 QueryBundle

            current = list(proc.postprocess_nodes(current, query_bundle=QueryBundle(query_str=query)))  # 包成 Bundle 再调
        except Exception as exc:  # noqa: BLE001  # 单步失败不中断整链
            print(f"警告: 后处理器 {type(proc).__name__} 失败，跳过该步: {exc}")  # 打警告并继续
    return current[: max(1, int(final_k or SIMILARITY_TOP_K))]  # 最终截断到 Top-K（至少 1）
