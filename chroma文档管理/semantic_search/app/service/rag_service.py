"""RAG 问答服务：检索前 → 检索中 → 检索后 → Corrective RAG → 生成。"""  # 模块说明：作业主链路编排

from __future__ import annotations  # 允许前向类型注解

from typing import TYPE_CHECKING, Optional  # 仅类型检查时导入，避免循环依赖

from llama_index.core import Settings  # 读取全局 Settings.llm
from llama_index.core.prompts import PromptTemplate  # 自定义问答 Prompt 模板
from llama_index.core.response_synthesizers import get_response_synthesizer  # 根据节点合成答案
from llama_index.core.schema import NodeWithScore  # 带相似度分数的检索节点

from semantic_search.app.config import (  # 系统提示、默认 Top-K、各优化开关默认值
    COMPRESS_ENABLED,
    CRAG_ENABLED,
    HYBRID_ENABLED,
    RAG_SYSTEM_PROMPT,
    REORDER_ENABLED,
    RERANK_ENABLED,
    SIMILARITY_TOP_K,
)
from semantic_search.app.service.crag import apply_crag  # Corrective RAG（库内修正）
from semantic_search.app.service.pre_retrieval import prepare_retrieval_queries  # 检索前优化入口
from semantic_search.app.service.retrieval_optimize import apply_postprocessors  # 检索后三件套

ASK_QA_PROMPT = PromptTemplate(  # /ask 专用：强制依据上下文、不懂就说不知道
    f"{RAG_SYSTEM_PROMPT}。只依据给定上下文回答；上下文没有的信息请明确说不知道。\n\n"  # 角色 + 约束
    "上下文：\n"  # 上下文标题
    "---------------------\n"  # 分隔线
    "{context_str}\n"  # 检索到的文档拼接占位
    "---------------------\n"  # 分隔线
    "问题：{query_str}\n"  # 用户问题占位
    "回答："  # 引导模型直接输出答案
)

if TYPE_CHECKING:  # 静态类型检查时才导入引擎，运行时不形成循环 import
    from semantic_search.app.engine import SemanticSearchEngine  # 引擎类型，仅注解用


def _node_key(node: NodeWithScore) -> str:  # 为 RRF 去重生成稳定键
    """用节点 id 或文本做去重键。"""  # 优先 id，没有则用文本前缀
    nid = getattr(node.node, "node_id", None) or getattr(node.node, "id_", None)  # 兼容不同字段名
    if nid:  # 有节点 id
        return str(nid)  # 用 id 字符串作键
    return (node.node.get_content() or "")[:200]  # 否则用正文前 200 字近似去重


def _format_source(rank: int, item: NodeWithScore) -> dict:  # 转成 API 统一的来源结构
    score = float(item.score or 0.0)  # 分数转 float，空则 0
    return {  # 与 DocumentResponse 字段对齐
        "rank": rank,  # 排名从 1 开始
        "index": rank - 1,  # 下标从 0 开始
        "document": item.node.get_content(),  # 命中文本
        "similarity": round(score, 4),  # 展示用相似度
        "distance": (  # 近似距离：分数在 0~1 用 1-score，否则用 1/(1+score)
            round(max(1.0 - score, 0.0), 4)  # 相似度型分数转距离
            if 0.0 <= score <= 1.0  # 判断是否像归一化相似度
            else round(1 / (1 + score), 4)  # 其他量纲的兜底换算
        ),
    }


def merge_nodes_rrf(  # Reciprocal Rank Fusion：多路召回融合
    ranked_lists: list[list[NodeWithScore]],  # 每一路检索的有序列表
    k: int,  # 融合后最终保留条数
    rrf_k: int = 60,  # RRF 平滑常数，常用 60
) -> list[NodeWithScore]:  # 返回按融合分排序的 Top-K
    """RRF 融合多路召回结果，再取 Top-K。"""  # 公式：sum 1/(rrf_k + rank)
    scores: dict[str, float] = {}  # 节点键 → 累积 RRF 分
    best: dict[str, NodeWithScore] = {}  # 节点键 → 保留的最佳原节点对象

    for nodes in ranked_lists:  # 遍历每一路召回
        for rank, item in enumerate(nodes, start=1):  # 路内排名从 1 计
            key = _node_key(item)  # 计算去重键
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)  # 累加 RRF 分
            prev = best.get(key)  # 看该键是否已有节点
            if prev is None or float(item.score or 0.0) > float(prev.score or 0.0):  # 保留原相似度更高者
                best[key] = item  # 更新代表节点

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)  # 按 RRF 分降序
    merged: list[NodeWithScore] = []  # 输出列表
    for key, rrf_score in ordered[:k]:  # 只取前 k 个
        node = best[key]  # 取出代表节点
        # 用 RRF 分覆盖展示分，便于前端理解融合排序
        node.score = rrf_score  # 写回分数字段供前端展示
        merged.append(node)  # 加入结果
    return merged  # 返回融合后的 Top-K


def _resolve_flag(override: Optional[bool], default: bool) -> bool:
    """请求显式传 True/False 则覆盖；None 跟从 .env 默认。"""
    return default if override is None else bool(override)


class RagAskService:  # 面向 /ask 的业务编排类
    """面向作业接口的编排层：pre + mid + post + CRAG + generate。"""  # 类说明

    def __init__(self, engine: SemanticSearchEngine):  # 注入已初始化的搜索引擎
        self.engine = engine  # 保存引擎引用，复用 index / collection

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

    def ask(  # 主流程：提问 → 按勾选优化 → 生成
        self,  # 服务实例
        question: str,  # 用户原问题
        k: int = SIMILARITY_TOP_K,  # 最终返回的来源条数
        strategy: str = "rewrite",  # 检索前策略（use_pre=True 时生效）
        *,
        use_pre: bool = True,  # 是否启用检索前优化
        use_hybrid: Optional[bool] = None,  # 混合检索
        use_rerank: Optional[bool] = None,  # 重排
        use_compress: Optional[bool] = None,  # 压缩
        use_reorder: Optional[bool] = None,  # 长上下文重排
        use_crag: Optional[bool] = None,  # Corrective RAG
    ) -> dict:  # 返回 question/answer/sources/pre_retrieval/crag/optimizations
        """接收用户提问 → 按勾选开关跑优化链路 → 模型生成。"""  # 方法说明
        self.engine._require_llm()  # 没有大模型则直接报错（问答依赖 LLM）
        question = (question or "").strip()  # 规范化问题
        if not question:  # 空问题不允许
            raise ValueError("问题不能为空")  # 交给路由转成 400

        # 解析本次实际生效的开关
        effective_strategy = (strategy or "rewrite").strip().lower() if use_pre else "none"
        if effective_strategy not in {"none", "clean", "rewrite", "hyde"}:
            effective_strategy = "rewrite" if use_pre else "none"
        flag_hybrid = _resolve_flag(use_hybrid, HYBRID_ENABLED)
        flag_rerank = _resolve_flag(use_rerank, RERANK_ENABLED)
        flag_compress = _resolve_flag(use_compress, COMPRESS_ENABLED)
        flag_reorder = _resolve_flag(use_reorder, REORDER_ENABLED)
        flag_crag = _resolve_flag(use_crag, CRAG_ENABLED)
        optimizations = {
            "use_pre": bool(use_pre),
            "strategy": effective_strategy,
            "use_hybrid": flag_hybrid,
            "use_rerank": flag_rerank,
            "use_compress": flag_compress,
            "use_reorder": flag_reorder,
            "use_crag": flag_crag,
        }

        empty_crag = {
            "enabled": False,
            "rewritten_query": None,
            "retried": False,
            "before_count": 0,
            "after_count": 0,
            "eval": [],
            "message": "skipped",
        }

        total = self.engine.collection.count()  # 当前知识库条数
        if total == 0:  # 空库无法检索
            return {  # 友好提示，并带回空的 pre_retrieval 结构
                "question": question,  # 回显问题
                "answer": "知识库为空，请先上传或导入文档后再提问。",  # 提示用户先入库
                "sources": [],  # 无来源
                "pre_retrieval": {  # 仍返回结构，方便前端统一渲染
                    "strategy": effective_strategy,  # 用户选择的策略
                    "original_query": question,  # 原问题
                    "clean_query": question,  # 空库时未真正清洗流程，原样回填
                    "rewritten_query": None,  # 无重写
                    "hyde_doc": None,  # 无 HyDE
                    "retrieval_queries": [],  # 未发起检索
                },
                "crag": empty_crag,
                "optimizations": optimizations,
            }

        k = max(1, min(k, total))  # Top-K 夹在 [1, 库容量] 之间
        prep = prepare_retrieval_queries(question, effective_strategy, llm=Settings.llm)  # 检索前
        queries = prep["retrieval_queries"] or [question]  # 若列表空则退回原问题

        # 检索中：对每个（改写后的）查询用（可选混合）检索器召回，再做查询间 RRF
        ranked_lists: list[list[NodeWithScore]] = []  # 收集每一路召回结果
        retriever = self.engine._build_retriever(k, hybrid_enabled=flag_hybrid)
        for q in queries:  # 对每个检索查询各跑一路
            ranked_lists.append(list(retriever.retrieve(q)))  # 保存该路命中列表

        # 候选窗口略放大，留给检索后精排；最终仍截到 k
        fuse_k = max(k, min(total, k * 2))
        fused = merge_nodes_rrf(ranked_lists, k=fuse_k) if len(ranked_lists) > 1 else (
            ranked_lists[0][:fuse_k] if ranked_lists else []
        )

        # 检索后：按勾选跑重排 / 压缩 / 长上下文重排
        fused = apply_postprocessors(
            fused,
            question,
            k,
            rerank_enabled=flag_rerank,
            compress_enabled=flag_compress,
            reorder_enabled=flag_reorder,
        )

        # Corrective RAG：可关闭；开启则过滤无关，全无关则改写后重走「混合+后处理」
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
            enabled=flag_crag,
        )

        if not fused:  # 检索为空或 CRAG 过滤后为空
            return {  # 告诉用户换问法或检查库
                "question": question,  # 回显问题
                "answer": "知识库中没有足够相关信息回答该问题（Corrective RAG 过滤后为空）。"
                if flag_crag
                else "知识库中没有检索到相关信息，请换个问法或先导入文档。",
                "sources": [],  # 无来源
                "pre_retrieval": prep,  # 仍返回优化过程，便于排查
                "crag": crag_info,
                "optimizations": optimizations,
            }

        # 用真实文档块生成答案；HyDE 假想文档不当作引用
        synthesizer = get_response_synthesizer(  # 创建回答合成器
            response_mode="compact",  # compact：压缩上下文后一次生成
            text_qa_template=ASK_QA_PROMPT,  # 使用上面定义的问答模板
        )
        # 始终用用户原问题生成，避免被改写句带偏表述
        response = synthesizer.synthesize(query=question, nodes=fused)  # 基于融合节点生成最终答案

        sources = [_format_source(i + 1, item) for i, item in enumerate(fused)]  # 格式化引用来源
        return {  # 组装 /ask 响应字典
            "question": question,  # 原问题
            "answer": str(response).strip(),  # 最终自然语言答案
            "sources": sources,  # 真实知识库片段
            "pre_retrieval": prep,  # 检索前优化中间信息
            "crag": crag_info,
            "optimizations": optimizations,
        }
