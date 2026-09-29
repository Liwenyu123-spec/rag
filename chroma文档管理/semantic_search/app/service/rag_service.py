"""RAG 问答服务：检索前 → 检索中 → 检索后 → CRAG → 生成 → Self-RAG。"""  # 模块说明：编排完整 RAG 问答链路

from __future__ import annotations  # 允许类型注解使用未定义的前向引用

from typing import TYPE_CHECKING, Optional  # 类型检查专用导入与可选类型

from llama_index.core import Settings  # LlamaIndex 全局 Settings（llm 等）
from llama_index.core.prompts import PromptTemplate  # 问答 Prompt 模板
from llama_index.core.response_synthesizers import get_response_synthesizer  # 根据节点合成最终回答
from llama_index.core.schema import NodeWithScore  # 带相似度分的检索节点

from semantic_search.app.config import (  # 从配置读取各优化开关与默认参数
    COMPRESS_ENABLED,  # 上下文压缩开关默认值
    CRAG_ENABLED,  # Corrective RAG 开关默认值
    HYBRID_ENABLED,  # 混合检索开关默认值
    HYBRID_FUSION_MODE,  # 混合检索融合模式默认值
    RAG_SYSTEM_PROMPT,  # 系统提示词前缀
    REORDER_ENABLED,  # Lost-in-the-middle 重排开关默认值
    RERANK_ENABLED,  # 重排序开关默认值
    SELF_RAG_ENABLED,  # Self-RAG 开关默认值
    SELF_RAG_VERBOSE,  # Self-RAG 是否打印详细日志
    SIMILARITY_TOP_K,  # 默认召回 Top-K
)
from semantic_search.app.service.crag import apply_crag, filter_relevant_nodes  # CRAG 纠错与相关性过滤
from semantic_search.app.service.pre_retrieval import prepare_retrieval_queries  # 检索前：清洗/改写/HyDE
from semantic_search.app.service.presets import apply_preset  # 按预设名合并各优化开关
from semantic_search.app.service.rag_eval import evaluate_generation  # 生成质量评估（忠实度等）
from semantic_search.app.service.retrieval_optimize import apply_postprocessors  # 检索后：重排/压缩/重排序
from semantic_search.app.service.self_rag import (  # Self-RAG：决定是否检索、生成后校验
    apply_self_rag_post_generate,  # 生成后 ISSUP/ISUSE 与纠正
    decide_retrieve,  # 生成前判断要不要查库
)

ASK_QA_PROMPT = PromptTemplate(  # 组装「上下文 + 问题 → 回答」的 QA 模板
    f"{RAG_SYSTEM_PROMPT}。只依据给定上下文回答；上下文没有的信息请明确说不知道。\n\n"  # 系统约束：忠实于上下文
    "上下文：\n"  # 上下文区块标题
    "---------------------\n"  # 上下文起始分隔线
    "{context_str}\n"  # 占位：检索到的上下文文本
    "---------------------\n"  # 上下文结束分隔线
    "问题：{query_str}\n"  # 占位：用户问题
    "回答："  # 引导模型输出答案
)  # PromptTemplate 构造结束


if TYPE_CHECKING:  # 仅类型检查时导入，避免运行时循环依赖
    from semantic_search.app.engine import SemanticSearchEngine  # 引擎类型注解用


def _node_key(node: NodeWithScore) -> str:  # 生成节点去重键
    """用节点 id 或文本做去重键。"""  # 优先 id，否则截取文本前缀
    nid = getattr(node.node, "node_id", None) or getattr(node.node, "id_", None)  # 尝试取节点唯一 id
    if nid:  # 有 id 则直接用
        return str(nid)  # 统一转成字符串键
    return (node.node.get_content() or "")[:200]  # 无 id 时用正文前 200 字兜底


def _format_source(rank: int, item: NodeWithScore) -> dict:  # 把检索节点格式化成前端 source 结构
    score = float(item.score or 0.0)  # 相似度分数，缺省按 0
    return {  # 组装单条溯源信息
        "rank": rank,  # 排名（从 1 起）
        "index": rank - 1,  # 零基下标，便于前端索引
        "document": item.node.get_content(),  # 节点原文内容
        "similarity": round(score, 4),  # 相似度保留四位小数
        "distance": (  # 由相似度推导距离，兼容不同分数区间
            round(max(1.0 - score, 0.0), 4)  # [0,1] 区间：距离 = 1 - 相似度
            if 0.0 <= score <= 1.0  # 判断是否为归一化相似度
            else round(1 / (1 + score), 4)  # 非归一化：用 1/(1+score) 映射
        ),  # distance 计算结束
    }  # 返回字典


def merge_nodes_rrf(  # 多路召回结果的 Reciprocal Rank Fusion
    ranked_lists: list[list[NodeWithScore]],  # 多路各自的排序列表
    k: int,  # 融合后保留的 Top-K
    rrf_k: int = 60,  # RRF 平滑常数，常用 60
) -> list[NodeWithScore]:  # 返回融合后的节点列表
    """RRF 融合多路召回结果，再取 Top-K。"""  # 文档：RRF 融合说明
    scores: dict[str, float] = {}  # 各节点累计 RRF 分数
    best: dict[str, NodeWithScore] = {}  # 同键保留原始 score 最高的节点对象

    for nodes in ranked_lists:  # 遍历每一路召回
        for rank, item in enumerate(nodes, start=1):  # 该路内按名次累加
            key = _node_key(item)  # 用去重键标识节点
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)  # RRF 公式累加
            prev = best.get(key)  # 已见过的同键节点
            if prev is None or float(item.score or 0.0) > float(prev.score or 0.0):  # 无记录或当前原始分更高
                best[key] = item  # 更新为更优节点对象

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)  # 按 RRF 分降序
    merged: list[NodeWithScore] = []  # 输出列表
    for key, rrf_score in ordered[:k]:  # 只取 Top-K
        node = best[key]  # 取出对应节点
        node.score = rrf_score  # 用 RRF 分覆盖 score，便于后续排序展示
        merged.append(node)  # 加入结果
    return merged  # 返回融合结果


def _resolve_flag(override: Optional[bool], default: bool) -> bool:  # 解析布尔开关：请求覆盖 vs 默认
    """请求显式传 True/False 则覆盖；None 跟从 .env 默认。"""  # 文档：覆盖规则
    return default if override is None else bool(override)  # None 用默认，否则强制转 bool


def _empty_crag() -> dict:  # 构造「未跑 CRAG」时的占位信息
    return {  # 空 CRAG 结构，前端可统一解析
        "enabled": False,  # 未启用
        "rewritten_query": None,  # 无改写查询
        "retried": False,  # 未重试检索
        "before_count": 0,  # 纠错前节点数
        "after_count": 0,  # 纠错后节点数
        "eval": [],  # 无逐条评估明细
        "message": "skipped",  # 标记为跳过
    }  # 返回占位字典


def _empty_self_rag() -> dict:  # 构造「未跑 Self-RAG」时的占位信息
    return {  # 空 Self-RAG 结构
        "enabled": False,  # 未启用
        "retrieve": None,  # 是否检索尚未判定
        "skipped_retrieval": False,  # 是否跳过了检索
        "isrel_shared_with_crag": False,  # 相关性是否与 CRAG 共用
        "issup": None,  # 支持度判定占位
        "corrected": False,  # 是否做过答案纠正
        "isuse": None,  # 有用性判定占位
        "message": "skipped",  # 标记为跳过
    }  # 返回占位字典


def _empty_eval() -> dict:  # 构造「未跑生成评估」时的占位信息
    return {  # 空评估结构
        "enabled": False,  # 未启用
        "faithfulness": None,  # 忠实度
        "relevancy": None,  # 相关性
        "correctness": None,  # 正确性
        "diagnosis": None,  # 诊断说明
        "message": "skipped",  # 标记为跳过
    }  # 返回占位字典


def _maybe_generation_eval(  # 按需做生成质量评估，否则返回空结构
    *,  # 强制关键字参数，避免位置传参混淆
    enabled: bool,  # 是否启用评估
    question: str,  # 用户问题
    answer: str,  # 模型回答
    sources: list,  # 溯源列表（作上下文）
    reference: Optional[str],  # 可选参考答案
) -> dict:  # 返回评估字典
    if not enabled:  # 未开启则直接跳过
        return _empty_eval()  # 返回空评估占位
    return evaluate_generation(  # 调用评估服务
        question,  # 问题
        answer,  # 答案
        sources,  # 来源上下文
        reference=reference,  # 参考答案（可空）
        llm=Settings.llm,  # 用全局 LLM 打分
    )  # 返回真实评估结果


def _context_from_nodes(nodes: list[NodeWithScore]) -> str:  # 把节点列表拼成带序号的上下文字符串
    parts = []  # 存放各段「[i] 文本」
    for i, item in enumerate(nodes, 1):  # 从 1 编号
        text = (item.node.get_content() or "").strip()  # 取正文并去空白
        if text:  # 非空才加入
            parts.append(f"[{i}] {text}")  # 带序号拼接
    return "\n\n".join(parts)  # 段与段之间空一行


class RagAskService:  # RAG 问答编排服务
    """编排：Retrieve? → Pre/Mid/Post → CRAG≈ISREL → 生成 → ISSUP/ISUSE。"""  # 链路总览

    def __init__(self, engine: SemanticSearchEngine):  # 注入语义搜索引擎
        self.engine = engine  # 保存引擎引用，供检索与 LLM 使用

    def _retrieve_pipeline(  # 单查询完整检索管线（混合 + 后处理）
        self,  # 实例
        query: str,  # 检索查询串
        k: int,  # Top-K
        *,  # 后续为关键字参数
        use_hybrid: bool,  # 是否混合检索
        use_rerank: bool,  # 是否重排
        use_compress: bool,  # 是否压缩
        use_reorder: bool,  # 是否 Lost-in-the-middle 重排
        num_queries: int = 1,  # 查询扩展条数
        fusion_mode: str | None = None,  # 融合模式
    ) -> list[NodeWithScore]:  # 返回处理后的节点
        """单查询：混合召回 + 检索后处理（供 CRAG 重试复用）。"""  # 供 CRAG lambda 复用
        retriever = self.engine._build_retriever(  # 按开关构建检索器
            k,  # Top-K
            hybrid_enabled=use_hybrid,  # 混合检索
            num_queries=num_queries,  # 多查询数
            fusion_mode=fusion_mode,  # 融合模式
        )  # 检索器构建结束
        nodes = list(retriever.retrieve(query))  # 执行召回并转成列表
        return apply_postprocessors(  # 检索后处理
            nodes,  # 原始召回
            query,  # 查询（压缩/重排可能用到）
            k,  # 最终保留条数
            rerank_enabled=use_rerank,  # 重排开关
            compress_enabled=use_compress,  # 压缩开关
            reorder_enabled=use_reorder,  # 重排序开关
        )  # 返回后处理后的节点

    def ask(  # 对外主入口：按开关跑整条 RAG 并返回答案
        self,  # 实例
        question: str,  # 用户问题
        k: int = SIMILARITY_TOP_K,  # 默认 Top-K
        strategy: Optional[str] = None,  # 检索前策略名
        *,  # 后续优化开关均为关键字参数
        preset: Optional[str] = None,  # 预设名（basic/advanced 等）
        use_pre: Optional[bool] = None,  # 是否启用检索前处理
        use_hybrid: Optional[bool] = None,  # 是否混合检索
        fusion_mode: Optional[str] = None,  # 融合模式覆盖
        num_queries: Optional[int] = None,  # 查询扩展数
        use_rerank: Optional[bool] = None,  # 是否重排
        use_compress: Optional[bool] = None,  # 是否压缩
        use_reorder: Optional[bool] = None,  # 是否重排序
        use_crag: Optional[bool] = None,  # 是否 CRAG
        use_self_rag: Optional[bool] = None,  # 是否 Self-RAG
        use_eval: Optional[bool] = False,  # 是否生成评估（默认关）
        reference: Optional[str] = None,  # 评估用参考答案
    ) -> dict:  # 返回含答案、溯源、各阶段元信息的字典
        """按预设 / 勾选开关跑优化链路并生成答案（对齐 ModularRAG）。"""  # 文档：主流程说明
        self.engine._require_llm()  # 确保 LLM 已配置，否则后续无法生成
        question = (question or "").strip()  # 规范化问题文本
        if not question:  # 空问题直接拒绝
            raise ValueError("问题不能为空")  # 抛业务错误给调用方

        resolved = apply_preset(  # 用预设填充未显式传入的开关
            preset,  # 预设名
            {  # 请求侧传入的原始开关字典
                "use_pre": use_pre,  # 检索前
                "strategy": strategy,  # 策略
                "use_hybrid": use_hybrid,  # 混合
                "fusion_mode": fusion_mode,  # 融合
                "num_queries": num_queries,  # 多查询
                "use_rerank": use_rerank,  # 重排
                "use_compress": use_compress,  # 压缩
                "use_reorder": use_reorder,  # 重排序
                "use_crag": use_crag,  # CRAG
                "use_self_rag": use_self_rag,  # Self-RAG
                "use_eval": use_eval,  # 评估
            },  # 原始开关结束
        )  # 得到合并后的 resolved
        # 显式请求字段覆盖预设；未传则用预设；都没有则跟 .env / 默认
        if use_pre is not None:  # 请求显式传了 use_pre
            flag_pre = bool(use_pre)  # 以请求为准
        elif "use_pre" in resolved:  # 否则看预设是否提供
            flag_pre = bool(resolved["use_pre"])  # 用预设值
        else:  # 都没有
            flag_pre = True  # 默认开启检索前处理

        raw_strategy = strategy if strategy is not None else resolved.get("strategy")  # 策略：请求优先于预设
        effective_strategy = str(raw_strategy or ("rewrite" if flag_pre else "none")).strip().lower()  # 规范化策略名
        if effective_strategy not in {"none", "clean", "rewrite", "hyde"}:  # 非法策略名
            effective_strategy = "rewrite" if flag_pre else "none"  # 回退到合理默认
        if not flag_pre:  # 关闭检索前时强制 none
            effective_strategy = "none"  # 不做清洗/改写/HyDE

        flag_hybrid = _resolve_flag(  # 解析混合检索开关
            resolved.get("use_hybrid", use_hybrid), HYBRID_ENABLED  # 预设/请求 vs .env 默认
        )  # 得到 flag_hybrid
        flag_rerank = _resolve_flag(  # 解析重排开关
            resolved.get("use_rerank", use_rerank), RERANK_ENABLED  # 同上
        )  # 得到 flag_rerank
        flag_compress = _resolve_flag(  # 解析压缩开关
            resolved.get("use_compress", use_compress), COMPRESS_ENABLED  # 同上
        )  # 得到 flag_compress
        flag_reorder = _resolve_flag(  # 解析重排序开关
            resolved.get("use_reorder", use_reorder), REORDER_ENABLED  # 同上
        )  # 得到 flag_reorder
        flag_crag = _resolve_flag(resolved.get("use_crag", use_crag), CRAG_ENABLED)  # 解析 CRAG 开关
        flag_self = _resolve_flag(  # 解析 Self-RAG 开关
            resolved.get("use_self_rag", use_self_rag), SELF_RAG_ENABLED  # 同上
        )  # 得到 flag_self
        flag_eval = bool(resolved.get("use_eval", use_eval) or False)  # 评估开关（缺省 False）
        flag_num_queries = max(1, int(resolved.get("num_queries") or num_queries or 1))  # 多查询数至少为 1
        flag_fusion = (  # 融合模式：预设 → 请求 → 配置 → 默认 reciprocal_rerank
            resolved.get("fusion_mode")  # 预设优先
            or fusion_mode  # 其次请求参数
            or HYBRID_FUSION_MODE  # 再次 .env
            or "reciprocal_rerank"  # 最终兜底
        )  # 得到 flag_fusion
        preset_name = (preset or "").strip().lower() or None  # 规范化预设名，空则 None
        if preset_name and preset_name not in {  # 未知预设名则作废
            "basic",  # 基础
            "hybrid_search",  # 混合检索
            "advanced",  # 进阶
            "full_optimization",  # 全开优化
        }:  # 合法预设集合
            preset_name = None  # 非法则清空

        optimizations = {  # 回传本次实际生效的优化开关，便于前端展示
            "preset": preset_name,  # 生效预设
            "use_pre": flag_pre,  # 检索前
            "strategy": effective_strategy,  # 策略
            "use_hybrid": flag_hybrid,  # 混合
            "fusion_mode": flag_fusion,  # 融合
            "num_queries": flag_num_queries,  # 多查询
            "use_rerank": flag_rerank,  # 重排
            "use_compress": flag_compress,  # 压缩
            "use_reorder": flag_reorder,  # 重排序
            "use_crag": flag_crag,  # CRAG
            "use_self_rag": flag_self,  # Self-RAG
            "use_eval": flag_eval,  # 评估
        }  # optimizations 结束

        empty_pre = {  # 跳过检索时的空 pre_retrieval 结构
            "strategy": effective_strategy,  # 仍记录策略名
            "original_query": question,  # 原始问题
            "clean_query": question,  # 未清洗时等同原文
            "rewritten_query": None,  # 无改写
            "hyde_doc": None,  # 无 HyDE 文档
            "retrieval_queries": [],  # 无检索查询列表
        }  # empty_pre 结束
        self_info = _empty_self_rag()  # 先放 Self-RAG 占位
        self_info["enabled"] = flag_self  # 标记本次是否启用 Self-RAG

        # ----- Self-RAG Retrieve：要不要查库？-----
        if flag_self:  # 启用 Self-RAG 时先问「要不要检索」
            need_retrieve = decide_retrieve(  # LLM 判定是否需要查库
                question, llm=Settings.llm, verbose=SELF_RAG_VERBOSE  # 问题 + LLM + 日志开关
            )  # 得到 yes/no
            self_info["retrieve"] = need_retrieve  # 记录判定结果
            if not need_retrieve:  # 判定为不需要检索
                answer = Settings.llm.complete(question).text.strip()  # 直接让 LLM 答，不查库
                self_info["skipped_retrieval"] = True  # 标记跳过了检索
                self_info["message"] = "no_retrieve_direct_answer"  # 说明原因
                from semantic_search.app.service.self_rag import judge_isuse  # 延迟导入有用性判定

                self_info["isuse"] = judge_isuse(  # 评估直接回答是否有用
                    question, answer, llm=Settings.llm, verbose=SELF_RAG_VERBOSE  # 问、答、LLM
                )  # 写入 isuse
                return {  # 早退：无溯源的直接回答
                    "question": question,  # 原问题
                    "answer": answer,  # 直接生成答案
                    "sources": [],  # 无检索来源
                    "pre_retrieval": empty_pre,  # 空检索前信息
                    "crag": _empty_crag(),  # 未跑 CRAG
                    "self_rag": self_info,  # Self-RAG 元信息
                    "generation_eval": _maybe_generation_eval(  # 按需评估
                        enabled=flag_eval,  # 是否评估
                        question=question,  # 问题
                        answer=answer,  # 答案
                        sources=[],  # 无来源
                        reference=reference,  # 参考答案
                    ),  # 评估结果
                    "optimizations": optimizations,  # 生效开关
                }  # 早退返回结束

        total = self.engine.collection.count()  # 知识库文档/块数量
        if total == 0:  # 空库无法检索
            empty_ans = "知识库为空，请先上传或导入文档后再提问。"  # 友好提示文案
            return {  # 早退：空库响应
                "question": question,  # 原问题
                "answer": empty_ans,  # 提示文案
                "sources": [],  # 无来源
                "pre_retrieval": empty_pre,  # 空检索前
                "crag": _empty_crag(),  # 未跑 CRAG
                "self_rag": self_info,  # Self-RAG 状态
                "generation_eval": _empty_eval(),  # 不评估空库提示
                "optimizations": optimizations,  # 生效开关
            }  # 空库返回结束

        k = max(1, min(k, total))  # Top-K 夹在 [1, total]
        prep = prepare_retrieval_queries(question, effective_strategy, llm=Settings.llm)  # 检索前处理得到多查询等
        queries = prep["retrieval_queries"] or [question]  # 实际用于召回的查询列表

        ranked_lists: list[list[NodeWithScore]] = []  # 收集每路召回结果
        retriever = self.engine._build_retriever(  # 构建本轮检索器
            k,  # Top-K
            hybrid_enabled=flag_hybrid,  # 混合开关
            num_queries=flag_num_queries,  # 多查询数
            fusion_mode=flag_fusion,  # 融合模式
        )  # 检索器就绪
        for q in queries:  # 对每个检索查询各召回一路
            ranked_lists.append(list(retriever.retrieve(q)))  # 追加该路节点列表

        fuse_k = max(k, min(total, k * 2))  # 融合候选池略大于最终 k，给后处理留余量
        fused = (  # 多路则 RRF，单路则截断，空则 []
            merge_nodes_rrf(ranked_lists, k=fuse_k)  # 多路 RRF 融合
            if len(ranked_lists) > 1  # 是否多于一路
            else (ranked_lists[0][:fuse_k] if ranked_lists else [])  # 单路截断或空
        )  # 得到融合候选

        fused = apply_postprocessors(  # 检索后：重排 / 压缩 / 重排序
            fused,  # 融合后的节点
            question,  # 用原问题做后处理查询
            k,  # 最终条数
            rerank_enabled=flag_rerank,  # 重排
            compress_enabled=flag_compress,  # 压缩
            reorder_enabled=flag_reorder,  # 重排序
        )  # 后处理完成

        if flag_crag:  # 启用 Corrective RAG
            fused, crag_info = apply_crag(  # 评估相关性，必要时改写重试
                question,  # 原问题
                fused,  # 当前节点
                retrieve_fn=lambda q: self._retrieve_pipeline(  # 重试检索回调
                    q,  # 改写后的查询
                    k,  # Top-K
                    use_hybrid=flag_hybrid,  # 同主流程混合开关
                    use_rerank=flag_rerank,  # 同重排
                    use_compress=flag_compress,  # 同压缩
                    use_reorder=flag_reorder,  # 同重排序
                    num_queries=flag_num_queries,  # 同多查询
                    fusion_mode=flag_fusion,  # 同融合
                ),  # lambda 结束
                llm=Settings.llm,  # 评估用 LLM
                enabled=True,  # 显式启用
            )  # 得到过滤后节点与 CRAG 元信息
            if flag_self:  # 同时开 Self-RAG 时标记相关性已共用
                self_info["isrel_shared_with_crag"] = True  # CRAG 的评估≈ISREL
        else:  # 未开 CRAG
            crag_info = _empty_crag()  # 先用空结构
            if flag_self and fused:  # Self-RAG 单独做 ISREL 过滤
                fused, details = filter_relevant_nodes(  # 过滤不相关节点
                    question, fused, llm=Settings.llm, verbose=SELF_RAG_VERBOSE  # 问、节点、LLM
                )  # 得到过滤结果与明细
                crag_info = {  # 借用 crag 字段回传 ISREL 明细（未真正跑 CRAG）
                    "enabled": False,  # CRAG 本身未开
                    "rewritten_query": None,  # 无改写
                    "retried": False,  # 无重试
                    "before_count": len(details),  # 过滤前条数（明细长度）
                    "after_count": len(fused),  # 过滤后条数
                    "eval": details,  # 逐条相关性明细
                    "message": "self_rag_isrel_only",  # 说明仅做了 ISREL
                }  # 自定义 crag_info 结束

        if not fused:  # 过滤后无可用上下文
            no_hit = (  # 按是否做过纠错/相关性过滤选择提示文案
                "知识库中没有足够相关信息回答该问题（Corrective RAG / ISREL 过滤后为空）。"  # CRAG/Self-RAG 过滤空
                if (flag_crag or flag_self)  # 走过相关性过滤
                else "知识库中没有检索到相关信息，请换个问法或先导入文档。"  # 普通未命中
            )  # no_hit 文案确定
            return {  # 早退：无命中
                "question": question,  # 原问题
                "answer": no_hit,  # 提示文案
                "sources": [],  # 无来源
                "pre_retrieval": prep,  # 真实检索前信息
                "crag": crag_info,  # CRAG/ISREL 元信息
                "self_rag": self_info,  # Self-RAG 状态
                "generation_eval": _maybe_generation_eval(  # 可对提示文案做评估
                    enabled=flag_eval,  # 是否评估
                    question=question,  # 问题
                    answer=no_hit,  # 「答案」实为提示
                    sources=[],  # 无来源
                    reference=reference,  # 参考答案
                ),  # 评估结果
                "optimizations": optimizations,  # 生效开关
            }  # 无命中返回结束

        synthesizer = get_response_synthesizer(  # 构建回答合成器
            response_mode="compact",  # compact：压缩上下文后生成
            text_qa_template=ASK_QA_PROMPT,  # 使用本模块 QA 模板
        )  # 合成器就绪
        response = synthesizer.synthesize(query=question, nodes=fused)  # 基于节点生成回答
        answer = str(response).strip()  # 转字符串并去空白

        if flag_self:  # Self-RAG 生成后：支持度/纠正/有用性
            context = _context_from_nodes(fused)  # 拼上下文字符串供校验
            answer, post_info = apply_self_rag_post_generate(  # ISSUP / 纠正 / ISUSE
                question,  # 问题
                answer,  # 初稿答案
                context,  # 上下文
                llm=Settings.llm,  # LLM
                enabled=True,  # 启用后处理
            )  # 可能得到纠正后的答案
            self_info.update(post_info)  # 合并后处理元信息
            self_info["enabled"] = True  # 确认启用
            self_info["retrieve"] = True  # 本路径确实做了检索
            self_info["skipped_retrieval"] = False  # 未跳过检索

        sources = [_format_source(i + 1, item) for i, item in enumerate(fused)]  # 格式化溯源列表
        return {  # 正常路径最终返回
            "question": question,  # 原问题
            "answer": answer,  # 最终答案（可能经 Self-RAG 纠正）
            "sources": sources,  # 溯源
            "pre_retrieval": prep,  # 检索前元信息
            "crag": crag_info,  # CRAG 元信息
            "self_rag": self_info,  # Self-RAG 元信息
            "generation_eval": _maybe_generation_eval(  # 按需评估最终答案
                enabled=flag_eval,  # 是否评估
                question=question,  # 问题
                answer=answer,  # 最终答案
                sources=sources,  # 来源上下文
                reference=reference,  # 参考答案
            ),  # 评估结果
            "optimizations": optimizations,  # 生效开关
        }  # 正常返回结束
