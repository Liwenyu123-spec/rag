"""深度思考：先推理再作答，对齐 DeepSeek 输入框的 DeepThink。"""

from __future__ import annotations

import re
from typing import Any

from semantic_search.app.service.pipeline import context_from_nodes

_THINK_PROMPT = """你是知识库助手。请先深入思考，再给出最终答案。
规则：
1. 只依据上下文，不要编造知识库没有的事实。
2. 思考过程写推理、对照资料、取舍原因，不要写成给用户的最终答复。
3. 最终答案用简体中文，归纳完整、条理清楚。

必须严格按下面格式输出：
<think>
逐步分析。
</think>
<answer>
面向用户的最终答案。
</answer>

上下文：
{context}

问题：{question}
"""


def parse_think_output(raw: str) -> tuple[str, str]:
    text = (raw or "").strip()
    tagged = re.search(r"<think>(.*?)</think>\s*<answer>(.*?)</answer>", text, re.S | re.I)
    if tagged:
        return tagged.group(2).strip(), tagged.group(1).strip()
    labeled = re.search(r"(?:思考|推理)[：:]\s*([\s\S]*?)\n\s*(?:最终答案|答案)[：:]\s*([\s\S]+)", text)
    if labeled:
        return labeled.group(2).strip(), labeled.group(1).strip()
    return text, ""


def run_deep_think(question: str, nodes: list, llm: Any) -> tuple[str, str]:
    context = context_from_nodes(nodes) or "（无检索结果）"
    prompt = _THINK_PROMPT.format(context=context[:8000], question=question)
    raw = str(llm.complete(prompt)).strip()
    answer, thinking = parse_think_output(raw)
    if not answer:
        answer = raw
    return answer, thinking
