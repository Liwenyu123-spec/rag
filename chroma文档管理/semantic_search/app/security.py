# -*- coding: utf-8 -*-
"""公共安全净化（安全聊天 / 文案模块复用）。"""
from __future__ import annotations

import re

SAFE_REJECT_REPLY = "非常抱歉，我目前无法回答这个问题。"

_DANGEROUS = [
    r"ignore\s+(previous|all|above)\s+(instructions|prompts|rules)",
    r"forget\s+(all|previous|your)\s+(instructions|rules|constraints)",
    r"jailbreak",
    r"DAN\s+mode",
    r"override\s+(system|previous)\s+(prompt|instructions)",
    r"(you\s+are|act\s+as|pretend\s+to\s+be)\s+(system|developer|admin|administrator)",
    r"print\s+(the|your)\s+(system|prompt|instructions)",
    r"show\s+(me|your)\s+(system|prompt|instructions|rules)",
    r"reveal\s+(your|the)\s+(system|prompt|instructions)",
    r"<script>",
    r"javascript:",
    r"eval\(",
    r"exec\(",
    r"忽略(之前|以上|全部).*(指令|提示|规则)",
    r"忘记(你的|之前).*(指令|规则)",
    r"你现在是(系统|管理员|开发者)",
    r"告诉我(你的|系统)(提示词|指令|规则)",
]


def moderation_input(user_input: str) -> str | None:
    """通过返回净化文本；失败返回 None。"""
    if not user_input or not isinstance(user_input, str):
        return None
    if len(user_input) > 2000:
        return None
    for pattern in _DANGEROUS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return None
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", user_input)
    if re.search(r"(.)\1{50,}", sanitized):
        return None
    return sanitized.strip() or None


def gate(user_input: str) -> tuple[str | None, str | None]:
    cleaned = moderation_input(user_input)
    if cleaned is None:
        return None, SAFE_REJECT_REPLY
    return cleaned, None
