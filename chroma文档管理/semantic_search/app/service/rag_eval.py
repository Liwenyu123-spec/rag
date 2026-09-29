"""RAG 评估：对齐飞书「01-RAG评估」LlamaIndex 内置评估器。

生成质量：Faithfulness / Relevancy / Correctness（LLM-as-judge）
检索质量：Hit Rate / MRR（关键词或 expected_texts 近似标注）
诊断：答案差先看检索 → 定位检索锅还是生成锅。
"""  # 模块说明：生成与检索两侧评估入口

from __future__ import annotations  # 允许注解里使用尚未定义的前向类型

from typing import Any, Optional  # Any 接评估结果；Optional 表示可空开关

from llama_index.core import Settings  # 取全局 LLM 做 LLM-as-judge
from llama_index.core.base.response.schema import Response  # 评估器需要的 Response 结构
from llama_index.core.schema import NodeWithScore, TextNode  # 来源节点与文本节点类型

from semantic_search.app.config import EVAL_VERBOSE  # 评估过程是否打印日志

# 飞书示例：贝壳科技 company_info.txt 配套评测集
DEFAULT_RETRIEVAL_CASES: list[dict] = [  # 默认检索评测用例（query + keywords + reference）
    {  # 用例1：总部地点
        "query": "贝壳科技总部在哪里？",  # 评测问题
        "keywords": ["北京", "总部"],  # 命中判定关键词
        "reference": "贝壳科技总部地点是北京。",  # Correctness 用标准答案
    },  # 续行参数/元素
    {  # 用例2：员工人数
        "query": "贝壳科技有多少员工？",  # 评测问题
        "keywords": ["2000", "员工"],  # 命中判定关键词
        "reference": "贝壳科技员工人数为 2000 人。",  # Correctness 用标准答案
    },  # 续行参数/元素
    {  # 用例3：上下班时间
        "query": "公司上班和下班时间分别是几点？",  # 评测问题
        "keywords": ["9:00", "18:00", "上班", "下班"],  # 命中判定关键词
        "reference": "上班时间早上9:00，下班时间晚上18:00。",  # Correctness 用标准答案
    },  # 续行参数/元素
    {  # 用例4：主营业务
        "query": "公司主要做什么业务？",  # 评测问题
        "keywords": ["AI", "大数据", "云计算", "业务"],  # 命中判定关键词
        "reference": "主要业务是 AI软件开发、大数据服务、云计算平台。",  # Correctness 用标准答案
    },  # 续行参数/元素
    {  # 用例5：福利待遇
        "query": "公司有哪些福利？",  # 评测问题
        "keywords": ["五险一金", "年假", "福利"],  # 命中判定关键词
        "reference": "福利包括五险一金、带薪年假、节日福利、定期团建。",  # Correctness 用标准答案
    },  # 续行参数/元素
]  # 列表结束


def _pass_score(result: Any) -> tuple[bool | None, float | None, str | None]:  # 统一抽取评估三元组
    """从 LlamaIndex EvaluationResult 抽出 passing / score / feedback。"""  # 兼容不同评估器字段名
    if result is None:  # 评估器未返回结果
        return None, None, None  # 三项皆空
    passing = getattr(result, "passing", None)  # 是否通过（bool）
    score = getattr(result, "score", None)  # 数值分（可能缺失）
    feedback = getattr(result, "feedback", None) or getattr(result, "response", None)  # 文字反馈兜底
    try:  # 分数可能不是数字
        score_f = float(score) if score is not None else None  # 转 float 或保持 None
    except (TypeError, ValueError):  # 无法转成浮点
        score_f = None  # 记为无分数
    return (  # 规范化后的三元组
        bool(passing) if passing is not None else None,  # passing 转 bool；缺省则 None
        score_f,  # 数值分
        str(feedback).strip() if feedback else None,  # 反馈去空白；空则 None
    )  # 括号结束


def _to_response(answer: str, sources: list[dict] | list[NodeWithScore]) -> Response:  # 拼成评估用 Response
    """把答案 + 来源拼成 LlamaIndex Response，供 evaluate_response 使用。"""  # 适配 API 返回的 dict 来源
    nodes: list[NodeWithScore] = []  # 收集带分节点
    for item in sources or []:  # 遍历来源；空则跳过
        if isinstance(item, NodeWithScore):  # 已经是标准节点
            nodes.append(item)  # 直接加入
            continue  # 处理下一项
        if isinstance(item, dict):  # API /ask 返回的来源字典
            text = item.get("document") or item.get("text") or ""  # 取正文文本
            score = item.get("similarity")  # 相似度分
            nodes.append(  # 包装成 NodeWithScore
                NodeWithScore(  # LlamaIndex 带分节点
                    node=TextNode(text=str(text)),  # 文本节点承载正文
                    score=float(score) if score is not None else None,  # 有分则转 float
                )  # 括号结束
            )  # 括号结束
    return Response(response=answer or "", source_nodes=nodes)  # 组装完整 Response


def evaluate_generation(  # 生成质量评估入口
    question: str,  # 用户问题
    answer: str,  # 模型答案
    sources: list[dict] | list[NodeWithScore],  # 召回来源（dict 或节点）
    *,  # 之后仅关键字参数
    reference: str | None = None,  # 可选标准答案，启用 Correctness
    llm: Any = None,  # 可注入评判 LLM；默认 Settings.llm
    verbose: Optional[bool] = None,  # 是否打印过程；None 跟配置
) -> dict:  # 返回各指标与诊断字典
    """生成质量：Faithfulness + Relevancy（+ 可选 Correctness）。"""  # LLM-as-judge 三件套
    verb = EVAL_VERBOSE if verbose is None else bool(verbose)  # 解析是否打日志
    model = llm or Settings.llm  # 实际用于评判的模型
    info: dict = {  # 结果骨架
        "enabled": True,  # 默认认为评估可用
        "faithfulness": None,  # 忠实度结果占位
        "relevancy": None,  # 相关性结果占位
        "correctness": None,  # 正确性结果占位
        "diagnosis": None,  # 诊断文案占位
        "message": "ok",  # 状态消息
    }  # 字典/集合结束
    if model is None:  # 没有可用 LLM
        info["message"] = "no_llm"  # 标记缺模型
        info["enabled"] = False  # 关闭评估
        return info  # 提前返回

    try:  # 按需导入评估器，避免硬依赖启动失败
        from llama_index.core.evaluation import (  # LlamaIndex 内置评估器
            CorrectnessEvaluator,  # 相对标准答案打分
            FaithfulnessEvaluator,  # 是否忠实于上下文
            RelevancyEvaluator,  # 答案是否相关问题
        )  # 括号结束
    except ImportError as exc:  # 包缺失或版本不兼容
        info["message"] = f"import_error:{exc}"  # 记录导入错误
        info["enabled"] = False  # 关闭评估
        return info  # 提前返回

    response = _to_response(answer, sources)  # 转成评估器需要的 Response
    try:  # 忠实度评估
        faith = FaithfulnessEvaluator(llm=model)  # 构建忠实度评估器
        faith_r = faith.evaluate_response(query=question, response=response)  # 对问答跑评估
        p, s, f = _pass_score(faith_r)  # 抽出 passing/score/feedback
        info["faithfulness"] = {"passing": p, "score": s, "feedback": f}  # 写入结果
        if verb:  # 需要日志时
            print(f"[Eval] Faithfulness passing={p} score={s}")  # 打印忠实度摘要
    except Exception as exc:  # noqa: BLE001  # 单指标失败不拖垮整体
        info["faithfulness"] = {"passing": None, "score": None, "feedback": str(exc)}  # 记录异常信息
        if verb:  # 需要日志时
            print(f"[Eval] Faithfulness 失败: {exc}")  # 打印失败原因

    try:  # 相关性评估
        rel = RelevancyEvaluator(llm=model)  # 构建相关性评估器
        rel_r = rel.evaluate_response(query=question, response=response)  # 对问答跑评估
        p, s, f = _pass_score(rel_r)  # 抽出三元组
        info["relevancy"] = {"passing": p, "score": s, "feedback": f}  # 写入结果
        if verb:  # 需要日志时
            print(f"[Eval] Relevancy passing={p} score={s}")  # 打印相关性摘要
    except Exception as exc:  # noqa: BLE001  # 单指标失败不拖垮整体
        info["relevancy"] = {"passing": None, "score": None, "feedback": str(exc)}  # 记录异常信息
        if verb:  # 需要日志时
            print(f"[Eval] Relevancy 失败: {exc}")  # 打印失败原因

    if reference and str(reference).strip():  # 有标准答案才跑 Correctness
        try:  # 正确性评估
            corr = CorrectnessEvaluator(llm=model)  # 构建正确性评估器
            corr_r = corr.evaluate(  # 相对 reference 打分
                query=question,  # 问题
                response=answer,  # 模型答案（字符串）
                reference=str(reference).strip(),  # 标准答案去空白
            )  # 括号结束
            p, s, f = _pass_score(corr_r)  # 抽出三元组
            info["correctness"] = {"passing": p, "score": s, "feedback": f}  # 写入结果
            if verb:  # 需要日志时
                print(f"[Eval] Correctness passing={p} score={s}")  # 打印正确性摘要
        except Exception as exc:  # noqa: BLE001  # 单指标失败不拖垮整体
            info["correctness"] = {"passing": None, "score": None, "feedback": str(exc)}  # 记录异常
            if verb:  # 需要日志时
                print(f"[Eval] Correctness 失败: {exc}")  # 打印失败原因

    info["diagnosis"] = diagnose_generation(info, has_sources=bool(sources))  # 根据指标给诊断建议
    return info  # 返回完整评估字典


def diagnose_generation(gen: dict, *, has_sources: bool) -> str:  # 根据评估结果给排查建议
    """飞书诊断口诀：答案差先看检索 / 再看生成。"""  # 定位检索锅还是生成锅
    faith = (gen.get("faithfulness") or {}).get("passing")  # 忠实度是否通过
    relev = (gen.get("relevancy") or {}).get("passing")  # 相关性是否通过
    if not has_sources:  # 根本没有召回来源
        return "无召回来源：先查检索侧（分块 / Embedding / 混合检索 / 重排 / Top-K）"  # 优先查检索
    if faith is False and relev is False:  # 两项都挂
        return "忠实度与相关性均未通过：先查检索是否召回对文档，再查 Prompt/生成"  # 双查
    if faith is False:  # 仅忠实度挂（可能幻觉）
        return "忠实度未通过（可能幻觉）：优化上下文压缩/CRAG/Self-RAG ISSUP，或加强「只依据资料」Prompt"  # 抑幻觉
    if relev is False:  # 仅相关性挂（答非所问）
        return "相关性未通过（答非所问）：优化查询重写/HyDE，或检查生成 Prompt"  # 对准问题
    if faith is True and relev is True:  # 两项都过
        return "生成侧忠实度与相关性通过；若仍不满意，用 Correctness（标准答案）做端到端打分"  # 可再端到端
    return "评估结果不完整，请查看各指标 feedback"  # 指标缺失时的兜底文案


def _node_text(node: Any) -> str:  # 从多种节点形态抽出纯文本
    if hasattr(node, "get_content"):  # LlamaIndex 标准节点
        return node.get_content() or ""  # 取内容；空则空串
    if hasattr(node, "text"):  # 带 text 属性的简易对象
        return node.text or ""  # 直接取 text
    if hasattr(node, "node"):  # NodeWithScore 包装
        return _node_text(node.node)  # 递归解包内层节点
    return str(node or "")  # 最后兜底转字符串


def _is_relevant_hit(texts: list[str], keywords: list[str]) -> tuple[bool, float]:  # 关键词近似标注
    """关键词命中：Hit + 第一个相关文档的 MRR 分量。"""  # Hit Rate / MRR 的单题计算
    kws = [k.lower() for k in keywords if k]  # 非空关键词统一小写
    if not kws:  # 没有可用关键词
        return False, 0.0  # 记未命中、MRR=0
    for rank, text in enumerate(texts, 1):  # 从第 1 名开始扫召回列表
        low = (text or "").lower()  # 文档文本小写
        if any(k in low for k in kws):  # 任一关键词出现即视为相关
            return True, 1.0 / rank  # Hit=True；MRR=1/排名
    return False, 0.0  # 全程未命中


def evaluate_retrieval_cases(  # 批量检索评估入口
    cases: list[dict],  # 评测集：query + keywords
    retrieve_fn,  # 检索回调：query -> 节点列表
    *,  # 之后仅关键字参数
    verbose: Optional[bool] = None,  # 是否打印每题 HIT/MISS
) -> dict:  # 返回 Hit Rate / MRR 与明细
    """批量检索评估：Hit Rate + MRR。

    cases 项：{"query": str, "keywords": [str, ...]}
    retrieve_fn(query) -> list[NodeWithScore] 或 list[dict]
    """  # 用关键词近似标注，不必人工标 expected_ids
    verb = EVAL_VERBOSE if verbose is None else bool(verbose)  # 解析是否打日志
    if not cases:  # 空评测集
        return {  # 返回空结果结构
            "hit_rate": 0.0,  # 命中率为 0
            "mrr": 0.0,  # MRR 为 0
            "total": 0,  # 题目数为 0
            "results": [],  # 无明细
            "message": "empty_cases",  # 状态：空用例
            "diagnosis": "请提供评测问题与 keywords",  # 提示补数据
        }  # 字典/集合结束

    results: list[dict] = []  # 逐题结果列表
    for item in cases:  # 遍历每道评测题
        query = (item.get("query") or "").strip()  # 取问题并去空白
        keywords = list(item.get("keywords") or [])  # 取关键词列表
        if not query:  # 空问题跳过
            continue  # 不计入统计
        try:  # 调用外部检索函数
            raw = list(retrieve_fn(query) or [])  # 保证得到列表
        except Exception as exc:  # noqa: BLE001  # 单题检索失败不中断整批
            results.append(  # 记录失败明细
                {  # 执行本行逻辑
                    "query": query,  # 原问题
                    "hit": False,  # 记未命中
                    "mrr": 0.0,  # MRR 记 0
                    "retrieved_preview": [],  # 无预览
                    "error": str(exc),  # 错误信息
                }  # 字典/集合结束
            )  # 括号结束
            continue  # 继续下一题

        texts: list[str] = []  # 全文列表（供命中判定）
        previews: list[str] = []  # 短预览（供展示）
        for n in raw:  # 遍历召回项
            if isinstance(n, dict):  # dict 来源格式
                t = n.get("document") or n.get("text") or ""  # 取正文
            else:  # 节点对象
                t = _node_text(n)  # 统一抽文本
            texts.append(t)  # 加入全文列表
            previews.append((t or "")[:80])  # 截前 80 字作预览

        hit, mrr = _is_relevant_hit(texts, keywords)  # 关键词判定 Hit/MRR
        results.append(  # 写入本题结果
            {  # 执行本行逻辑
                "query": query,  # 原问题
                "hit": hit,  # 是否命中
                "mrr": round(mrr, 4),  # MRR 保留四位
                "retrieved_preview": previews[:5],  # 最多展示 5 条预览
            }  # 字典/集合结束
        )  # 括号结束
        if verb:  # 需要日志时
            print(f"[Eval] {'HIT' if hit else 'MISS'} MRR={mrr:.3f} | {query[:40]}")  # 打印单题摘要

    n = len(results) or 1  # 分母至少为 1，避免除零
    hit_rate = sum(1 for r in results if r.get("hit")) / n  # Hit Rate = 命中题数 / 总题数
    avg_mrr = sum(float(r.get("mrr") or 0) for r in results) / n  # 平均 MRR
    diagnosis = (  # 按 Hit Rate 给诊断
        "检索 Hit Rate 偏低：优先调分块大小、Embedding、混合检索、重排、Top-K"  # 偏低时查检索侧
        if hit_rate < 0.7  # 阈值 0.7
        else "检索侧整体可用；若答案仍差，重点查生成 Faithfulness/Relevancy"  # 可用则转查生成
    )  # 括号结束
    return {  # 汇总返回
        "hit_rate": round(hit_rate, 4),  # Hit Rate 四位小数
        "mrr": round(avg_mrr, 4),  # 平均 MRR 四位小数
        "total": len(results),  # 有效题数
        "results": results,  # 逐题明细
        "message": "ok",  # 正常完成
        "diagnosis": diagnosis,  # 诊断建议
    }  # 字典/集合结束
