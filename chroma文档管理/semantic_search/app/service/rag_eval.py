"""RAG 评估：对齐飞书「01-RAG评估」LlamaIndex 内置评估器。

生成质量：Faithfulness / Relevancy / Correctness（LLM-as-judge）
检索质量：Hit Rate / MRR / Precision@K / Recall@K（关键词、reference、expected_ids）
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


def _node_id(node: Any) -> str | None:
    """抽出节点 id，供 expected_ids 标注。"""
    if isinstance(node, dict):
        nid = node.get("node_id") or node.get("id") or node.get("id_")
        return str(nid) if nid else None
    inner = getattr(node, "node", node)
    nid = getattr(inner, "node_id", None) or getattr(inner, "id_", None)
    return str(nid) if nid else None


def _gold_from_case(item: dict) -> tuple[list[str], list[str], list[str]]:
    """从评测样例抽出 keywords / expected_texts / expected_ids。"""
    keywords = [str(k).strip() for k in (item.get("keywords") or []) if str(k).strip()]
    texts = [str(t).strip() for t in (item.get("expected_texts") or []) if str(t).strip()]
    ref = str(item.get("reference") or "").strip()
    if ref and not texts:
        texts.append(ref)
    ids = [str(i).strip() for i in (item.get("expected_ids") or []) if str(i).strip()]
    return keywords, texts, ids


def _doc_is_relevant(
    text: str,
    nid: str | None,
    keywords: list[str],
    expected_texts: list[str],
    expected_ids: list[str],
) -> bool:
    """单篇是否相关：有 expected_ids 时只看节点 ID，否则看关键词 / 标准片段。"""
    if expected_ids:
        return bool(nid and nid in expected_ids)
    low = (text or "").lower()
    if any(k.lower() in low for k in keywords):
        return True
    if any(t.lower() in low for t in expected_texts):
        return True
    return False


def _label_recall(texts: list[str], keywords: list[str], expected_texts: list[str]) -> float | None:
    """标签级 Recall：关键词 + 标准片段有多少出现在 Top-K 正文里。"""
    labels = [x for x in (keywords + expected_texts) if x]
    if not labels:
        return None
    blob = "\n".join(texts).lower()
    hit = sum(1 for lab in labels if lab.lower() in blob)
    return hit / len(labels)


def _id_recall(retrieved_ids: list[str | None], expected_ids: list[str]) -> float | None:
    """节点 ID 级 Recall：黄金节点有多少出现在 Top-K。"""
    if not expected_ids:
        return None
    got = {i for i in retrieved_ids if i}
    return sum(1 for i in expected_ids if i in got) / len(expected_ids)


def score_retrieved(
    texts: list[str],
    retrieved_ids: list[str | None],
    keywords: list[str],
    expected_texts: list[str],
    expected_ids: list[str],
) -> dict:
    """单题：Hit / MRR / Precision@K / Recall@K。"""
    n = len(texts)
    relevant_flags = [
        _doc_is_relevant(
            texts[i],
            retrieved_ids[i] if i < len(retrieved_ids) else None,
            keywords,
            expected_texts,
            expected_ids,
        )
        for i in range(n)
    ]
    first_rank = next((i + 1 for i, ok in enumerate(relevant_flags) if ok), None)
    hit = first_rank is not None
    mrr = (1.0 / first_rank) if first_rank else 0.0
    rel_n = sum(1 for ok in relevant_flags if ok)
    precision = (rel_n / n) if n else 0.0
    id_r = _id_recall(retrieved_ids, expected_ids)
    lab_r = _label_recall(texts, keywords, expected_texts)
    if id_r is not None:
        recall = id_r
    elif lab_r is not None:
        recall = lab_r
    else:
        recall = 1.0 if hit else 0.0
    return {
        "hit": hit,
        "mrr": round(mrr, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "first_hit_rank": first_rank,
        "relevant_in_k": rel_n,
    }


def diagnose_retrieval(
    hit_rate: float,
    mrr: float,
    precision_at_k: float,
    recall_at_k: float,
) -> str:
    """按检索指标给优化建议。"""
    if hit_rate < 0.7:
        return "检索 Hit Rate 偏低：优先调分块、Embedding、混合检索、重排、Top-K、检索前改写"
    if recall_at_k < 0.5:
        return "能命中但 Recall@K 偏低：相关信息没捞全，可增大 Top-K / 开混合检索 / Multi-Query"
    if precision_at_k < 0.4:
        return "Precision@K 偏低：噪声多，可开重排、压缩或 CRAG 过滤"
    if mrr < 0.5:
        return "能命中但相关文档偏后：优先开重排 / RRF 融合"
    return "检索侧整体可用；若答案仍差，重点查生成 Faithfulness/Relevancy"


def compare_retrieval_runs(baseline: dict, current: dict) -> dict:
    """当前配置相对基础 RAG 的指标差（正数=提升）。"""
    keys = ("hit_rate", "mrr", "precision_at_k", "recall_at_k")
    return {
        key: round(float(current.get(key) or 0) - float(baseline.get(key) or 0), 4)
        for key in keys
    }


def evaluate_retrieval_cases(  # 批量检索评估入口
    cases: list[dict],  # 评测集：query + keywords
    retrieve_fn,  # 检索回调：query -> 节点列表
    *,  # 之后仅关键字参数
    verbose: Optional[bool] = None,  # 是否打印每题 HIT/MISS
    flags: dict | None = None,  # 本轮实际检索开关（回显）
) -> dict:  # 返回 Hit Rate / MRR / Precision / Recall 与明细
    """批量检索评估：Hit Rate + MRR + Precision@K + Recall@K。

    cases 项：query、keywords，可选 reference / expected_texts / expected_ids。
    retrieve_fn(query) -> list[NodeWithScore] 或 list[dict]
    """
    verb = EVAL_VERBOSE if verbose is None else bool(verbose)
    empty = {
        "hit_rate": 0.0,
        "mrr": 0.0,
        "precision_at_k": 0.0,
        "recall_at_k": 0.0,
        "total": 0,
        "results": [],
        "message": "empty_cases",
        "diagnosis": "请提供评测问题与 keywords / expected_ids",
        "flags": flags or {},
    }
    if not cases:
        return empty

    results: list[dict] = []
    for item in cases:
        query = (item.get("query") or "").strip()
        if not query:
            continue
        keywords, expected_texts, expected_ids = _gold_from_case(item)
        try:
            raw = list(retrieve_fn(query) or [])
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "query": query,
                    "hit": False,
                    "mrr": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "first_hit_rank": None,
                    "relevant_in_k": 0,
                    "retrieved_preview": [],
                    "error": str(exc),
                }
            )
            continue

        texts: list[str] = []
        ids: list[str | None] = []
        previews: list[str] = []
        for n in raw:
            if isinstance(n, dict):
                t = n.get("document") or n.get("text") or ""
            else:
                t = _node_text(n)
            texts.append(t)
            ids.append(_node_id(n))
            previews.append((t or "")[:80])

        scored = score_retrieved(texts, ids, keywords, expected_texts, expected_ids)
        results.append(
            {
                "query": query,
                "hit": scored["hit"],
                "mrr": scored["mrr"],
                "precision": scored["precision"],
                "recall": scored["recall"],
                "first_hit_rank": scored["first_hit_rank"],
                "relevant_in_k": scored["relevant_in_k"],
                "retrieved_preview": previews[:5],
            }
        )
        if verb:
            print(
                f"[Eval] {'HIT' if scored['hit'] else 'MISS'} "
                f"MRR={scored['mrr']:.3f} P={scored['precision']:.3f} "
                f"R={scored['recall']:.3f} | {query[:40]}"
            )

    n = len(results)
    if not n:
        return empty
    hit_rate = sum(1 for r in results if r.get("hit")) / n
    avg_mrr = sum(float(r.get("mrr") or 0) for r in results) / n
    avg_p = sum(float(r.get("precision") or 0) for r in results) / n
    avg_r = sum(float(r.get("recall") or 0) for r in results) / n
    return {
        "hit_rate": round(hit_rate, 4),
        "mrr": round(avg_mrr, 4),
        "precision_at_k": round(avg_p, 4),
        "recall_at_k": round(avg_r, 4),
        "total": n,
        "results": results,
        "message": "ok",
        "diagnosis": diagnose_retrieval(hit_rate, avg_mrr, avg_p, avg_r),
        "flags": flags or {},
    }
