"""Self-RAG（讲义工程版）：用 LLM 在判断点显式提问，等价复现反思令牌闭环。

对齐飞书「05-其他优化」六步：
Retrieve → 检索 → ISREL → 生成 → ISSUP（不足则修正）→ ISUSE。

说明：真正 token 级 Self-RAG 需微调模型；本仓库用当前 Settings.llm 做批评家。
ISREL 与 CRAG 相关性过滤同构，编排层可共用一次结果，避免重复烧钱。
"""

from __future__ import annotations

from typing import Any, Optional

from llama_index.core import Settings
from llama_index.core.prompts import PromptTemplate

from semantic_search.app.config import SELF_RAG_ENABLED, SELF_RAG_VERBOSE

RETRIEVE_PROMPT = PromptTemplate(
    "判断回答下面的用户问题是否需要检索外部知识库。\n"
    "闲聊、问候、与知识库无关的常识/创意题 → NO；\n"
    "需要事实、政策、文档、专业细节支撑 → YES。\n"
    "只输出一个词：YES 或 NO。\n\n"
    "用户问题：{query}\n输出："
)

ISSUP_PROMPT = PromptTemplate(
    "判断下面的「回答」是否被「资料」充分支持。\n"
    "只输出一个词：FULLY（完全支持）/ PARTIALLY（部分支持）/ NO（无依据或矛盾）。\n\n"
    "用户问题：{query}\n资料：\n{context}\n\n回答：\n{answer}\n输出："
)

CORRECT_PROMPT = PromptTemplate(
    "请完全依据给定资料重写回答，不要臆造资料中没有的信息；"
    "资料不足时明确说明不知道。用简体中文完整回答。\n\n"
    "资料：\n{context}\n\n用户问题：{query}\n原回答：{answer}\n重写后："
)

ISUSE_PROMPT = PromptTemplate(
    "从用户角度给下面回答打分：对问题有多大帮助。\n"
    "只输出整数 1~5（5=非常有用，1=几乎没用）。\n\n"
    "用户问题：{query}\n回答：\n{answer}\n分数："
)


def _llm_text(prompt: str, llm: Any = None) -> str:
    model = llm or Settings.llm
    if model is None:
        return ""
    return (model.complete(prompt).text or "").strip()


def decide_retrieve(query: str, *, llm: Any = None, verbose: bool = False) -> bool:
    """Retrieve：要不要检索？YES→True，NO→False。无 LLM 时默认要检索。"""
    raw = _llm_text(RETRIEVE_PROMPT.format(query=query), llm=llm).upper()
    token = (raw.replace("：", " ").replace(":", " ").split() or ["YES"])[0]
    if token.startswith("NO"):
        need = False
    elif token.startswith("YES"):
        need = True
    elif "NO" in raw and "YES" not in raw:
        need = False
    else:
        need = True  # 解析失败保守：去检索
    if verbose:
        print(f"[Self-RAG] Retrieve={need}  raw={raw!r}")
    return need


def judge_issup(
    query: str,
    answer: str,
    context: str,
    *,
    llm: Any = None,
    verbose: bool = False,
) -> str:
    """ISSUP：返回 FULLY / PARTIALLY / NO。"""
    raw = _llm_text(
        ISSUP_PROMPT.format(query=query, context=(context or "")[:4000], answer=answer),
        llm=llm,
    ).upper()
    if "FULLY" in raw:
        level = "FULLY"
    elif "PARTIALLY" in raw or "PARTIAL" in raw:
        level = "PARTIALLY"
    elif "NO" in raw:
        level = "NO"
    else:
        level = "PARTIALLY"  # 不确定时当部分支持，触发修正更安全
    if verbose:
        print(f"[Self-RAG] ISSUP={level}  raw={raw!r}")
    return level


def correct_answer(
    query: str,
    answer: str,
    context: str,
    *,
    llm: Any = None,
    verbose: bool = False,
) -> str:
    """依据资料重写答案（硬约束修正）。"""
    fixed = _llm_text(
        CORRECT_PROMPT.format(
            query=query,
            context=(context or "")[:4000],
            answer=answer,
        ),
        llm=llm,
    )
    if verbose:
        print(f"[Self-RAG] corrected answer len={len(fixed)}")
    return fixed or answer


def judge_isuse(
    query: str,
    answer: str,
    *,
    llm: Any = None,
    verbose: bool = False,
) -> int:
    """ISUSE：1~5 有用性。"""
    raw = _llm_text(ISUSE_PROMPT.format(query=query, answer=answer), llm=llm)
    score = 3
    for ch in raw:
        if ch.isdigit():
            n = int(ch)
            if 1 <= n <= 5:
                score = n
                break
    if verbose:
        print(f"[Self-RAG] ISUSE={score}  raw={raw!r}")
    return score


def apply_self_rag_post_generate(
    query: str,
    answer: str,
    context: str,
    *,
    llm: Any = None,
    enabled: Optional[bool] = None,
    verbose: Optional[bool] = None,
) -> tuple[str, dict]:
    """生成后：ISSUP（不足则修正）→ ISUSE。返回 (最终答案, 过程信息)。"""
    use = SELF_RAG_ENABLED if enabled is None else bool(enabled)
    verb = SELF_RAG_VERBOSE if verbose is None else bool(verbose)
    info: dict = {
        "enabled": bool(use),
        "retrieve": None,  # 由编排层填写
        "skipped_retrieval": False,
        "isrel_shared_with_crag": False,
        "issup": None,
        "corrected": False,
        "isuse": None,
        "message": "skipped",
    }
    if not use:
        return answer, info

    issup = judge_issup(query, answer, context, llm=llm, verbose=verb)
    info["issup"] = issup
    final = answer
    if issup in {"PARTIALLY", "NO"} and (context or "").strip():
        final = correct_answer(query, answer, context, llm=llm, verbose=verb)
        info["corrected"] = final != answer
        info["message"] = "corrected" if info["corrected"] else "issup_weak_no_change"
    elif issup == "FULLY":
        info["message"] = "fully_supported"
    else:
        info["message"] = f"issup_{issup.lower()}"

    info["isuse"] = judge_isuse(query, final, llm=llm, verbose=verb)
    return final, info
