"""RAG 评估：对齐飞书「01-RAG评估」LlamaIndex 内置评估器。

生成质量：Faithfulness / Relevancy / Correctness（LLM-as-judge）
检索质量：Hit Rate / MRR（关键词或 expected_texts 近似标注）
诊断：答案差先看检索 → 定位检索锅还是生成锅。
"""

from __future__ import annotations

from typing import Any, Optional

from llama_index.core import Settings
from llama_index.core.base.response.schema import Response
from llama_index.core.schema import NodeWithScore, TextNode

from semantic_search.app.config import EVAL_VERBOSE

# 飞书示例：贝壳科技 company_info.txt 配套评测集
DEFAULT_RETRIEVAL_CASES: list[dict] = [
    {
        "query": "贝壳科技总部在哪里？",
        "keywords": ["北京", "总部"],
        "reference": "贝壳科技总部地点是北京。",
    },
    {
        "query": "贝壳科技有多少员工？",
        "keywords": ["2000", "员工"],
        "reference": "贝壳科技员工人数为 2000 人。",
    },
    {
        "query": "公司上班和下班时间分别是几点？",
        "keywords": ["9:00", "18:00", "上班", "下班"],
        "reference": "上班时间早上9:00，下班时间晚上18:00。",
    },
    {
        "query": "公司主要做什么业务？",
        "keywords": ["AI", "大数据", "云计算", "业务"],
        "reference": "主要业务是 AI软件开发、大数据服务、云计算平台。",
    },
    {
        "query": "公司有哪些福利？",
        "keywords": ["五险一金", "年假", "福利"],
        "reference": "福利包括五险一金、带薪年假、节日福利、定期团建。",
    },
]


def _pass_score(result: Any) -> tuple[bool | None, float | None, str | None]:
    """从 LlamaIndex EvaluationResult 抽出 passing / score / feedback。"""
    if result is None:
        return None, None, None
    passing = getattr(result, "passing", None)
    score = getattr(result, "score", None)
    feedback = getattr(result, "feedback", None) or getattr(result, "response", None)
    try:
        score_f = float(score) if score is not None else None
    except (TypeError, ValueError):
        score_f = None
    return (
        bool(passing) if passing is not None else None,
        score_f,
        str(feedback).strip() if feedback else None,
    )


def _to_response(answer: str, sources: list[dict] | list[NodeWithScore]) -> Response:
    """把答案 + 来源拼成 LlamaIndex Response，供 evaluate_response 使用。"""
    nodes: list[NodeWithScore] = []
    for item in sources or []:
        if isinstance(item, NodeWithScore):
            nodes.append(item)
            continue
        if isinstance(item, dict):
            text = item.get("document") or item.get("text") or ""
            score = item.get("similarity")
            nodes.append(
                NodeWithScore(
                    node=TextNode(text=str(text)),
                    score=float(score) if score is not None else None,
                )
            )
    return Response(response=answer or "", source_nodes=nodes)


def evaluate_generation(
    question: str,
    answer: str,
    sources: list[dict] | list[NodeWithScore],
    *,
    reference: str | None = None,
    llm: Any = None,
    verbose: Optional[bool] = None,
) -> dict:
    """生成质量：Faithfulness + Relevancy（+ 可选 Correctness）。"""
    verb = EVAL_VERBOSE if verbose is None else bool(verbose)
    model = llm or Settings.llm
    info: dict = {
        "enabled": True,
        "faithfulness": None,
        "relevancy": None,
        "correctness": None,
        "diagnosis": None,
        "message": "ok",
    }
    if model is None:
        info["message"] = "no_llm"
        info["enabled"] = False
        return info

    try:
        from llama_index.core.evaluation import (
            CorrectnessEvaluator,
            FaithfulnessEvaluator,
            RelevancyEvaluator,
        )
    except ImportError as exc:
        info["message"] = f"import_error:{exc}"
        info["enabled"] = False
        return info

    response = _to_response(answer, sources)
    try:
        faith = FaithfulnessEvaluator(llm=model)
        faith_r = faith.evaluate_response(query=question, response=response)
        p, s, f = _pass_score(faith_r)
        info["faithfulness"] = {"passing": p, "score": s, "feedback": f}
        if verb:
            print(f"[Eval] Faithfulness passing={p} score={s}")
    except Exception as exc:  # noqa: BLE001
        info["faithfulness"] = {"passing": None, "score": None, "feedback": str(exc)}
        if verb:
            print(f"[Eval] Faithfulness 失败: {exc}")

    try:
        rel = RelevancyEvaluator(llm=model)
        rel_r = rel.evaluate_response(query=question, response=response)
        p, s, f = _pass_score(rel_r)
        info["relevancy"] = {"passing": p, "score": s, "feedback": f}
        if verb:
            print(f"[Eval] Relevancy passing={p} score={s}")
    except Exception as exc:  # noqa: BLE001
        info["relevancy"] = {"passing": None, "score": None, "feedback": str(exc)}
        if verb:
            print(f"[Eval] Relevancy 失败: {exc}")

    if reference and str(reference).strip():
        try:
            corr = CorrectnessEvaluator(llm=model)
            corr_r = corr.evaluate(
                query=question,
                response=answer,
                reference=str(reference).strip(),
            )
            p, s, f = _pass_score(corr_r)
            info["correctness"] = {"passing": p, "score": s, "feedback": f}
            if verb:
                print(f"[Eval] Correctness passing={p} score={s}")
        except Exception as exc:  # noqa: BLE001
            info["correctness"] = {"passing": None, "score": None, "feedback": str(exc)}
            if verb:
                print(f"[Eval] Correctness 失败: {exc}")

    info["diagnosis"] = diagnose_generation(info, has_sources=bool(sources))
    return info


def diagnose_generation(gen: dict, *, has_sources: bool) -> str:
    """飞书诊断口诀：答案差先看检索 / 再看生成。"""
    faith = (gen.get("faithfulness") or {}).get("passing")
    relev = (gen.get("relevancy") or {}).get("passing")
    if not has_sources:
        return "无召回来源：先查检索侧（分块 / Embedding / 混合检索 / 重排 / Top-K）"
    if faith is False and relev is False:
        return "忠实度与相关性均未通过：先查检索是否召回对文档，再查 Prompt/生成"
    if faith is False:
        return "忠实度未通过（可能幻觉）：优化上下文压缩/CRAG/Self-RAG ISSUP，或加强「只依据资料」Prompt"
    if relev is False:
        return "相关性未通过（答非所问）：优化查询重写/HyDE，或检查生成 Prompt"
    if faith is True and relev is True:
        return "生成侧忠实度与相关性通过；若仍不满意，用 Correctness（标准答案）做端到端打分"
    return "评估结果不完整，请查看各指标 feedback"


def _node_text(node: Any) -> str:
    if hasattr(node, "get_content"):
        return node.get_content() or ""
    if hasattr(node, "text"):
        return node.text or ""
    if hasattr(node, "node"):
        return _node_text(node.node)
    return str(node or "")


def _is_relevant_hit(texts: list[str], keywords: list[str]) -> tuple[bool, float]:
    """关键词命中：Hit + 第一个相关文档的 MRR 分量。"""
    kws = [k.lower() for k in keywords if k]
    if not kws:
        return False, 0.0
    for rank, text in enumerate(texts, 1):
        low = (text or "").lower()
        if any(k in low for k in kws):
            return True, 1.0 / rank
    return False, 0.0


def evaluate_retrieval_cases(
    cases: list[dict],
    retrieve_fn,
    *,
    verbose: Optional[bool] = None,
) -> dict:
    """批量检索评估：Hit Rate + MRR。

    cases 项：{"query": str, "keywords": [str, ...]}
    retrieve_fn(query) -> list[NodeWithScore] 或 list[dict]
    """
    verb = EVAL_VERBOSE if verbose is None else bool(verbose)
    if not cases:
        return {
            "hit_rate": 0.0,
            "mrr": 0.0,
            "total": 0,
            "results": [],
            "message": "empty_cases",
            "diagnosis": "请提供评测问题与 keywords",
        }

    results: list[dict] = []
    for item in cases:
        query = (item.get("query") or "").strip()
        keywords = list(item.get("keywords") or [])
        if not query:
            continue
        try:
            raw = list(retrieve_fn(query) or [])
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "query": query,
                    "hit": False,
                    "mrr": 0.0,
                    "retrieved_preview": [],
                    "error": str(exc),
                }
            )
            continue

        texts: list[str] = []
        previews: list[str] = []
        for n in raw:
            if isinstance(n, dict):
                t = n.get("document") or n.get("text") or ""
            else:
                t = _node_text(n)
            texts.append(t)
            previews.append((t or "")[:80])

        hit, mrr = _is_relevant_hit(texts, keywords)
        results.append(
            {
                "query": query,
                "hit": hit,
                "mrr": round(mrr, 4),
                "retrieved_preview": previews[:5],
            }
        )
        if verb:
            print(f"[Eval] {'HIT' if hit else 'MISS'} MRR={mrr:.3f} | {query[:40]}")

    n = len(results) or 1
    hit_rate = sum(1 for r in results if r.get("hit")) / n
    avg_mrr = sum(float(r.get("mrr") or 0) for r in results) / n
    diagnosis = (
        "检索 Hit Rate 偏低：优先调分块大小、Embedding、混合检索、重排、Top-K"
        if hit_rate < 0.7
        else "检索侧整体可用；若答案仍差，重点查生成 Faithfulness/Relevancy"
    )
    return {
        "hit_rate": round(hit_rate, 4),
        "mrr": round(avg_mrr, 4),
        "total": len(results),
        "results": results,
        "message": "ok",
        "diagnosis": diagnosis,
    }
