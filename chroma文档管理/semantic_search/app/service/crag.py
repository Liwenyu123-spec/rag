"""Corrective RAG（库内修正版）：相关性过滤 + 全无关时改写重检索。  # 模块一句话

对齐课上 demo01：不联网；用当前 Settings.llm（DeepSeek）做评估与改写。  # 约束说明
"""  # docstring 结束

from __future__ import annotations  # 延后注解

from typing import Any, Callable, List, Optional  # 类型工具

from llama_index.core import Settings  # 全局 LLM/Embedding
from llama_index.core.prompts import PromptTemplate  # Prompt 模板
from llama_index.core.schema import NodeWithScore  # 带分节点

from semantic_search.app.config import CRAG_ENABLED, CRAG_VERBOSE  # CRAG 开关与日志

RELEVANCE_PROMPT = PromptTemplate(  # 单篇相关/无关判别 Prompt
    "判断下面的文档片段是否与用户问题相关、能否帮助回答问题。\n"  # 任务说明
    "只输出一个词：RELEVANT 或 IRRELEVANT。\n\n"  # 输出约束
    "用户问题：{query}\n文档片段：{document}\n输出："  # 占位符
)  # RELEVANCE_PROMPT 结束
REWRITE_PROMPT = PromptTemplate(  # 全无关时的查询改写 Prompt
    "原始问题检索不到相关信息，请把它改写得更清晰、更具体，便于检索。\n"  # 改写目标
    "只输出改写后的问题。\n\n原始问题：{query}\n改写后："  # 输出约束
)  # REWRITE_PROMPT 结束


def _is_relevant(query: str, doc: str, llm: Any = None) -> bool:  # 单篇是否相关
    """单篇相关性判断。"""  # 文档字符串
    model = llm or Settings.llm  # 优先用传入 LLM
    if model is None:  # 没有模型
        return True  # 无 LLM 时不做过滤，避免把结果清空
    text = (doc or "")[:2000]  # 截断过长片段，省 token
    resp = model.complete(RELEVANCE_PROMPT.format(query=query, document=text)).text.strip().upper()  # 调模型并规范化
    # 模型偶发输出「NOT RELEVANT」等，优先看 IRRELEVANT  # 解析策略说明
    if "IRRELEVANT" in resp:  # 明确无关
        return False  # 丢弃
    if "RELEVANT" in resp:  # 明确相关
        return True  # 保留
    return False  # 解析不清当无关，偏保守过滤


def filter_relevant_nodes(  # 批量过滤
    query: str,  # 用户问题
    nodes: List[NodeWithScore],  # 候选节点
    *,  # 关键字参数
    llm: Any = None,  # 可选裁判模型
    verbose: bool = False,  # 是否打印每篇结果
) -> tuple[List[NodeWithScore], List[dict]]:  # 保留节点 + 明细
    """逐篇评估，返回相关节点 + 评估明细。"""  # 文档字符串
    kept: List[NodeWithScore] = []  # 相关列表
    details: List[dict] = []  # 评估日志
    for i, item in enumerate(nodes, 1):  # 从 1 编号遍历
        content = item.node.get_content() or ""  # 取文本
        ok = _is_relevant(query, content, llm=llm)  # 判相关
        details.append({"rank": i, "relevant": ok, "preview": content[:80]})  # 记明细
        if verbose:  # 需要终端日志
            print(f"  [CRAG] 文档 {i}：{'相关' if ok else '无关'}", flush=True)  # 打印状态
        if ok:  # 相关则留下
            kept.append(item)  # 加入保留列表
    return kept, details  # 返回二元组


def rewrite_query_for_retrieval(query: str, llm: Any = None) -> str:  # 改写查询
    """全无关时改写查询（内部修正）。"""  # 文档字符串
    model = llm or Settings.llm  # 取模型
    if model is None:  # 无模型
        return query  # 原样返回
    new_q = model.complete(REWRITE_PROMPT.format(query=query)).text.strip()  # 生成改写句
    return new_q or query  # 空则回退原问


def apply_crag(  # CRAG 主入口
    question: str,  # 原问题
    nodes: List[NodeWithScore],  # 已召回节点
    *,  # 关键字参数
    retrieve_fn: Callable[[str], List[NodeWithScore]],  # 改写后重检索回调
    llm: Any = None,  # 裁判/改写模型
    enabled: Optional[bool] = None,  # 覆盖开关
    verbose: Optional[bool] = None,  # 覆盖日志
) -> tuple[List[NodeWithScore], dict]:  # 最终节点 + 过程信息
    """对已召回节点做 Corrective RAG。  # 文档说明

    retrieve_fn(query) -> nodes：改写后重检索用（应已含混合检索 + 后处理）。  # 回调约定
    返回：(最终节点, crag 过程信息)  # 返回值
    """  # docstring 结束
    use = CRAG_ENABLED if enabled is None else enabled  # 解析是否启用
    verb = CRAG_VERBOSE if verbose is None else verbose  # 解析是否打印
    info: dict = {  # 过程信息骨架
        "enabled": bool(use),  # 是否开启
        "rewritten_query": None,  # 改写句（若有）
        "retried": False,  # 是否重检索
        "before_count": len(nodes),  # 过滤前数量
        "after_count": len(nodes),  # 过滤后数量（初值同前）
        "eval": [],  # 每篇评估明细
        "message": "skipped",  # 状态码字符串
    }  # info 结束
    if not use:  # 未启用
        return nodes, info  # 原样返回
    if not nodes:  # 输入空
        info["message"] = "empty_input"  # 标记空输入
        info["after_count"] = 0  # 后数量为 0
        return nodes, info  # 返回空

    if verb:  # 日志开
        print(f"[CRAG] 相关性过滤，候选 {len(nodes)} 篇...")  # 提示开始过滤
    kept, details = filter_relevant_nodes(question, nodes, llm=llm, verbose=verb)  # 首轮过滤
    info["eval"] = details  # 写入明细

    if kept:  # 还有相关篇
        info["after_count"] = len(kept)  # 更新数量
        info["message"] = "filtered"  # 仅过滤成功
        if verb:
            print(f"[CRAG] 保留 {len(kept)} 篇，接着生成回答…", flush=True)
        return kept, info  # 直接用过滤结果

    # 全部无关 → 改写 + 重检索（只再来一轮，对齐 demo01）  # 纠错分支
    if verb:  # 日志
        print("[CRAG] 全部无关，改写查询并重检索...")  # 提示纠错
    new_query = rewrite_query_for_retrieval(question, llm=llm)  # 改写问题
    info["rewritten_query"] = new_query  # 记录改写
    info["retried"] = True  # 标记已重试
    if verb:  # 日志
        print(f"[CRAG] 改写后：{new_query}")  # 打印新查询

    try:  # 重检索可能失败
        retry_nodes = list(retrieve_fn(new_query) or [])  # 调回调拿新节点
    except Exception as exc:  # noqa: BLE001  # 捕获一切业务异常
        print(f"[CRAG] 重检索失败: {exc}")  # 打印错误
        info["message"] = f"retry_failed:{exc}"  # 写入失败信息
        info["after_count"] = 0  # 无结果
        return [], info  # 返回空列表

    kept2, details2 = filter_relevant_nodes(question, retry_nodes, llm=llm, verbose=verb)  # 第二轮过滤（仍用原问判相关）
    info["eval"] = details + [  # 合并两轮明细
        {**d, "round": 2} for d in details2  # 第二轮加 round=2
    ]  # eval 赋值结束
    info["after_count"] = len(kept2)  # 最终篇数
    info["message"] = "rewrote_and_filtered" if kept2 else "no_relevant_after_retry"  # 状态文案
    return kept2, info  # 返回纠错后结果
