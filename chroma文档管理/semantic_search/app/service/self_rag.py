"""Self-RAG（讲义工程版）：用 LLM 在判断点显式提问，等价复现反思令牌闭环。

对齐飞书「05-其他优化」六步：
Retrieve → 检索 → ISREL → 生成 → ISSUP（不足则修正）→ ISUSE。

说明：真正 token 级 Self-RAG 需微调模型；本仓库用当前 Settings.llm 做批评家。
ISREL 与 CRAG 相关性过滤同构，编排层可共用一次结果，避免重复烧钱。
"""  # 模块 docstring：Self-RAG 工程版说明

from __future__ import annotations  # 延后注解求值

from typing import Any, Optional  # 类型：任意对象、可选值

from llama_index.core import Settings  # 全局 Settings.llm
from llama_index.core.prompts import PromptTemplate  # Prompt 模板类

from semantic_search.app.config import SELF_RAG_ENABLED, SELF_RAG_VERBOSE  # Self-RAG 开关与日志

RETRIEVE_PROMPT = PromptTemplate(  # Retrieve：要不要检索
    "判断回答下面的用户问题是否需要检索外部知识库。\n"  # 任务
    "闲聊、问候、与知识库无关的常识/创意题 → NO；\n"  # NO 场景
    "需要事实、政策、文档、专业细节支撑 → YES。\n"  # YES 场景
    "只输出一个词：YES 或 NO。\n\n"  # 输出约束
    "用户问题：{query}\n输出："  # 占位
)  # RETRIEVE_PROMPT 结束

ISSUP_PROMPT = PromptTemplate(  # ISSUP：答案是否被资料支持
    "判断下面的「回答」是否被「资料」充分支持。\n"  # 任务
    "只输出一个词：FULLY（完全支持）/ PARTIALLY（部分支持）/ NO（无依据或矛盾）。\n\n"  # 三档
    "用户问题：{query}\n资料：\n{context}\n\n回答：\n{answer}\n输出："  # 占位
)  # ISSUP_PROMPT 结束

CORRECT_PROMPT = PromptTemplate(  # 不足时按资料重写
    "请完全依据给定资料重写回答，不要臆造资料中没有的信息；"  # 硬约束
    "资料不足时明确说明不知道。用简体中文完整回答。\n\n"  # 拒答策略
    "资料：\n{context}\n\n用户问题：{query}\n原回答：{answer}\n重写后："  # 占位
)  # CORRECT_PROMPT 结束

ISUSE_PROMPT = PromptTemplate(  # ISUSE：有用性 1~5
    "从用户角度给下面回答打分：对问题有多大帮助。\n"  # 任务
    "只输出整数 1~5（5=非常有用，1=几乎没用）。\n\n"  # 分制
    "用户问题：{query}\n回答：\n{answer}\n分数："  # 占位
)  # ISUSE_PROMPT 结束


def _llm_text(prompt: str, llm: Any = None) -> str:  # 统一取模型文本输出
    model = llm or Settings.llm  # 优先外部传入
    if model is None:  # 无可用模型
        return ""  # 空串
    return (model.complete(prompt).text or "").strip()  # complete 后去空白


def decide_retrieve(query: str, *, llm: Any = None, verbose: bool = False) -> bool:  # Retrieve 门控
    """Retrieve：要不要检索？YES→True，NO→False。无 LLM 时默认要检索。"""  # 文档字符串
    raw = _llm_text(RETRIEVE_PROMPT.format(query=query), llm=llm).upper()  # 调模型并大写
    token = (raw.replace("：", " ").replace(":", " ").split() or ["YES"])[0]  # 取首词
    if token.startswith("NO"):  # 明确不要检索
        need = False  # 跳过检索
    elif token.startswith("YES"):  # 明确要检索
        need = True  # 走检索
    elif "NO" in raw and "YES" not in raw:  # 文中仅出现 NO
        need = False  # 当不检索
    else:  # 其它模糊输出
        need = True  # 解析失败保守：去检索
    if verbose:  # 调试日志
        print(f"[Self-RAG] Retrieve={need}  raw={raw!r}")  # 打印判定
    return need  # 返回是否检索


def judge_issup(  # ISSUP 评估
    query: str,  # 问题
    answer: str,  # 初稿答案
    context: str,  # 召回资料拼接
    *,  # 关键字参数分隔
    llm: Any = None,  # 可选模型
    verbose: bool = False,  # 是否打印
) -> str:  # 返回档位字符串
    """ISSUP：返回 FULLY / PARTIALLY / NO。"""  # 文档字符串
    raw = _llm_text(  # 调裁判模型
        ISSUP_PROMPT.format(query=query, context=(context or "")[:4000], answer=answer),  # 截断上下文
        llm=llm,  # 传入模型
    ).upper()  # 大写便于匹配
    if "FULLY" in raw:  # 完全支持
        level = "FULLY"  # 档位
    elif "PARTIALLY" in raw or "PARTIAL" in raw:  # 部分支持
        level = "PARTIALLY"  # 档位
    elif "NO" in raw:  # 无支持
        level = "NO"  # 档位
    else:  # 解析失败
        level = "PARTIALLY"  # 不确定时当部分支持，触发修正更安全
    if verbose:  # 日志
        print(f"[Self-RAG] ISSUP={level}  raw={raw!r}")  # 打印
    return level  # 返回档位


def correct_answer(  # 按资料硬修正
    query: str,  # 问题
    answer: str,  # 原回答
    context: str,  # 资料
    *,  # 关键字参数
    llm: Any = None,  # 模型
    verbose: bool = False,  # 日志
) -> str:  # 重写后文本
    """依据资料重写答案（硬约束修正）。"""  # 文档字符串
    fixed = _llm_text(  # 生成修正稿
        CORRECT_PROMPT.format(  # 填模板
            query=query,  # 问题
            context=(context or "")[:4000],  # 截断资料
            answer=answer,  # 原答
        ),  # format 结束
        llm=llm,  # 模型
    )  # _llm_text 结束
    if verbose:  # 日志
        print(f"[Self-RAG] corrected answer len={len(fixed)}")  # 打印长度
    return fixed or answer  # 空则保留原答


def judge_isuse(  # 有用性打分
    query: str,  # 问题
    answer: str,  # 最终答
    *,  # 关键字参数
    llm: Any = None,  # 模型
    verbose: bool = False,  # 日志
) -> int:  # 1~5 整数
    """ISUSE：1~5 有用性。"""  # 文档字符串
    raw = _llm_text(ISUSE_PROMPT.format(query=query, answer=answer), llm=llm)  # 调模型
    score = 3  # 默认中档
    for ch in raw:  # 扫描输出字符
        if ch.isdigit():  # 找到数字
            n = int(ch)  # 转整型
            if 1 <= n <= 5:  # 合法分
                score = n  # 采用
                break  # 取第一个合法分
    if verbose:  # 日志
        print(f"[Self-RAG] ISUSE={score}  raw={raw!r}")  # 打印
    return score  # 返回分数


def apply_self_rag_post_generate(  # 生成后闭环
    query: str,  # 问题
    answer: str,  # 初稿
    context: str,  # 资料
    *,  # 关键字参数
    llm: Any = None,  # 模型
    enabled: Optional[bool] = None,  # 覆盖开关
    verbose: Optional[bool] = None,  # 覆盖日志
) -> tuple[str, dict]:  # (最终答案, 过程信息)
    """生成后：ISSUP（不足则修正）→ ISUSE。返回 (最终答案, 过程信息)。"""  # 文档字符串
    use = SELF_RAG_ENABLED if enabled is None else bool(enabled)  # 是否启用
    verb = SELF_RAG_VERBOSE if verbose is None else bool(verbose)  # 是否打印
    info: dict = {  # 过程信息默认结构
        "enabled": bool(use),  # 开关回显
        "retrieve": None,  # 由编排层填写
        "skipped_retrieval": False,  # 是否跳过检索
        "isrel_shared_with_crag": False,  # ISREL 是否与 CRAG 共用
        "issup": None,  # 支持度档位
        "corrected": False,  # 是否重写过
        "isuse": None,  # 有用性分
        "message": "skipped",  # 状态码
    }  # info 结束
    if not use:  # 未启用
        return answer, info  # 原样返回

    issup = judge_issup(query, answer, context, llm=llm, verbose=verb)  # 验据
    info["issup"] = issup  # 记录档位
    final = answer  # 默认不改
    if issup in {"PARTIALLY", "NO"} and (context or "").strip():  # 不足且有资料
        final = correct_answer(query, answer, context, llm=llm, verbose=verb)  # 重写
        info["corrected"] = final != answer  # 是否真变了
        info["message"] = "corrected" if info["corrected"] else "issup_weak_no_change"  # 状态
    elif issup == "FULLY":  # 完全支持
        info["message"] = "fully_supported"  # 状态
    else:  # 其它
        info["message"] = f"issup_{issup.lower()}"  # 兜底状态串

    info["isuse"] = judge_isuse(query, final, llm=llm, verbose=verb)  # 打有用性分
    return final, info  # 返回最终答与信息
