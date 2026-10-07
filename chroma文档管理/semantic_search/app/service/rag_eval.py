"""RAG 评估：对齐飞书「01-RAG评估」LlamaIndex 内置评估器。

生成质量：Faithfulness / Relevancy / Correctness（LLM-as-judge）
检索质量：Hit Rate / MRR / Precision@K / Recall@K（expected_ids / expected_texts / keywords）
诊断：答案差先看检索 → 定位检索锅还是生成锅。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from llama_index.core import Settings
from llama_index.core.base.response.schema import Response
from llama_index.core.schema import NodeWithScore, TextNode

from semantic_search.app.config import DATA_DIR, EVAL_VERBOSE

_FALLBACK_CASES: list[dict] = [
    {
        "query": "贝壳科技总部在哪里？",
        "keywords": ["北京", "总部"],
        "expected_texts": ["总部地点：北京"],
        "reference": "贝壳科技总部地点是北京。",
    },
    {
        "query": "贝壳科技有多少员工？",
        "keywords": ["2000", "员工"],
        "expected_texts": ["员工人数：2000人"],
        "reference": "贝壳科技员工人数为 2000 人。",
    },
    {
        "query": "公司上班和下班时间分别是几点？",
        "keywords": ["9:00", "18:00"],
        "expected_texts": ["上班时间：早上9:00", "下班时间：晚上18:00"],
        "reference": "上班时间早上9:00，下班时间晚上18:00。",
    },
    {
        "query": "公司主要做什么业务？",
        "keywords": ["AI", "大数据", "云计算"],
        "expected_texts": ["公司主要业务：AI软件开发、大数据服务、云计算平台"],
        "reference": "主要业务是 AI软件开发、大数据服务、云计算平台。",
    },
    {
        "query": "公司有哪些福利？",
        "keywords": ["五险一金", "年假", "团建"],
        "expected_texts": ["公司福利：五险一金、带薪年假、节日福利、定期团建"],
        "reference": "福利包括五险一金、带薪年假、节日福利、定期团建。",
    },
    {
        "query": "子公司有多少员工？",
        "keywords": ["300", "子公司"],
        "expected_texts": ["子公司员工数量为 300 人"],
        "reference": "子公司员工数量为 300 人。",
    },
]

RETRIEVAL_CASES_PATH = Path(DATA_DIR) / "eval" / "retrieval_cases.json"
GRAPH_CASES_PATH = Path(DATA_DIR) / "eval" / "graph_cases.json"


def load_retrieval_casebook() -> dict:
    """读取可配置评测集；JSON 坏了或缺失时回退内置题。"""
    meta = {
        "name": "内置贝壳科技样题",
        "doc_scope": "business",
        "description": "默认评测集",
        "source": "builtin",
        "path": str(RETRIEVAL_CASES_PATH),
        "cases": list(_FALLBACK_CASES),
    }
    path = RETRIEVAL_CASES_PATH
    if not path.is_file():
        return meta
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        meta["description"] = f"读取 {path.name} 失败，已用内置题：{exc}"
        return meta
    cases = raw.get("cases") if isinstance(raw, dict) else None
    if not isinstance(cases, list) or not cases:
        meta["description"] = f"{path.name} 无有效 cases，已用内置题"
        return meta
    cleaned = []
    for item in cases:
        if not isinstance(item, dict):
            continue
        q = str(item.get("query") or "").strip()
        if not q:
            continue
        cleaned.append({
            "query": q,
            "keywords": [str(k).strip() for k in (item.get("keywords") or []) if str(k).strip()],
            "expected_texts": [str(t).strip() for t in (item.get("expected_texts") or []) if str(t).strip()],
            "expected_ids": [str(i).strip() for i in (item.get("expected_ids") or []) if str(i).strip()],
            "reference": str(item.get("reference") or "").strip() or None,
        })
    if not cleaned:
        meta["description"] = f"{path.name} cases 为空，已用内置题"
        return meta
    return {
        "name": str(raw.get("name") or path.stem),
        "doc_scope": str(raw.get("doc_scope") or "business"),
        "description": str(raw.get("description") or ""),
        "source": "file",
        "path": str(path),
        "cases": cleaned,
    }


def get_default_retrieval_cases() -> list[dict]:
    return list(load_retrieval_casebook()["cases"])


# 兼容旧 import
DEFAULT_RETRIEVAL_CASES = get_default_retrieval_cases()


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


def _text_contains_gold(doc: str, gold: str) -> bool:
    """宽松片段匹配：黄金句出现在召回里，或召回核心句出现在黄金句里。"""
    a = " ".join((doc or "").lower().split())
    b = " ".join((gold or "").lower().split())
    if not a or not b:
        return False
    if b in a or a in b:
        return True
    # 去掉常见标点后再比一次，兼容分块切断
    for ch in "：:，,。.;；、 ":
        a = a.replace(ch, "")
        b = b.replace(ch, "")
    return bool(a and b and (b in a or a in b))


def gold_mode_of(expected_ids: list[str], expected_texts: list[str], keywords: list[str]) -> str:
    if expected_ids:
        return "expected_ids"
    if expected_texts:
        return "expected_texts"
    if keywords:
        return "keywords"
    return "none"


def _doc_is_relevant(
    text: str,
    nid: str | None,
    keywords: list[str],
    expected_texts: list[str],
    expected_ids: list[str],
) -> bool:
    """单篇是否相关：ID > 黄金片段 > 关键词（避免宽关键词误命中）。"""
    if expected_ids:
        return bool(nid and nid in expected_ids)
    if expected_texts:
        return any(_text_contains_gold(text, t) for t in expected_texts)
    low = (text or "").lower()
    return any(k.lower() in low for k in keywords)


def _label_recall(texts: list[str], keywords: list[str], expected_texts: list[str]) -> float | None:
    """标签级 Recall：优先按黄金片段，否则按关键词。"""
    labels = expected_texts or keywords
    if not labels:
        return None
    if expected_texts:
        hit = sum(1 for lab in labels if any(_text_contains_gold(t, lab) for t in texts))
    else:
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
        "gold_mode": gold_mode_of(expected_ids, expected_texts, keywords),
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
                    "gold_mode": gold_mode_of(expected_ids, expected_texts, keywords),
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
                "gold_mode": scored.get("gold_mode") or "none",
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


def load_graph_casebook() -> dict:
    """读取图谱评测集。"""
    meta = {
        "name": "内置图谱样题",
        "description": "",
        "source": "builtin",
        "path": str(GRAPH_CASES_PATH),
        "cases": [
            {
                "query": "乔布斯创立了什么公司？",
                "keywords": ["苹果", "创立"],
                "expected_entities": ["乔布斯", "苹果"],
            }
        ],
    }
    if not GRAPH_CASES_PATH.is_file():
        return meta
    try:
        raw = json.loads(GRAPH_CASES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        meta["description"] = f"读取失败：{exc}"
        return meta
    cases = raw.get("cases") if isinstance(raw, dict) else None
    if not isinstance(cases, list) or not cases:
        return meta
    cleaned = []
    for item in cases:
        if not isinstance(item, dict):
            continue
        q = str(item.get("query") or "").strip()
        if not q:
            continue
        cleaned.append({
            "query": q,
            "keywords": [str(k).strip() for k in (item.get("keywords") or []) if str(k).strip()],
            "expected_entities": [
                str(e).strip() for e in (item.get("expected_entities") or []) if str(e).strip()
            ],
        })
    if not cleaned:
        return meta
    return {
        "name": str(raw.get("name") or GRAPH_CASES_PATH.stem),
        "description": str(raw.get("description") or ""),
        "source": "file",
        "path": str(GRAPH_CASES_PATH),
        "cases": cleaned,
    }


def evaluate_graph_cases(graph_service: Any, cases: list[dict] | None = None) -> dict:
    """图谱评测：问题 → retrieve + 路径，看关键词/实体是否出现。"""
    book = load_graph_casebook()
    items = cases if cases is not None else list(book.get("cases") or [])
    results: list[dict] = []
    for item in items:
        query = str(item.get("query") or "").strip()
        if not query:
            continue
        keywords = [str(k).strip() for k in (item.get("keywords") or []) if str(k).strip()]
        entities = [
            str(e).strip() for e in (item.get("expected_entities") or []) if str(e).strip()
        ]
        try:
            retrieved = graph_service.retrieve(query, k=5)
            evidence = {
                "paths": retrieved.get("paths") or [],
                "mentions": retrieved.get("mentions") or [],
            }
            blob_parts = [
                *(r.get("text") or "" for r in (retrieved.get("results") or [])),
                *(p.get("path") or "" for p in (evidence.get("paths") or [])),
                " ".join(evidence.get("mentions") or []),
            ]
            blob = "\n".join(blob_parts).lower()
            kw_hit = any(k.lower() in blob for k in keywords) if keywords else False
            ent_hit = all(e.lower() in blob for e in entities) if entities else kw_hit
            hit = bool(kw_hit or ent_hit)
            results.append({
                "query": query,
                "hit": hit,
                "keyword_hit": kw_hit,
                "entity_hit": ent_hit,
                "paths": (evidence.get("paths") or [])[:4],
                "preview": (retrieved.get("results") or [{}])[0].get("text", "")[:120]
                if retrieved.get("results")
                else "",
            })
        except Exception as exc:  # noqa: BLE001
            results.append({
                "query": query,
                "hit": False,
                "keyword_hit": False,
                "entity_hit": False,
                "paths": [],
                "preview": "",
                "error": str(exc),
            })
    n = len(results)
    hit_rate = (sum(1 for r in results if r.get("hit")) / n) if n else 0.0
    return {
        "casebook_name": book.get("name") or "",
        "total": n,
        "hit_rate": round(hit_rate, 4),
        "results": results,
        "message": "ok" if n else "empty_cases",
        "diagnosis": (
            "图谱关系题命中偏低：先用示例建图，或检查 Schema/实体名是否对齐"
            if hit_rate < 0.6
            else "图谱侧对样题基本可用；可与向量 basic 对照看多跳题差距"
        ),
    }
