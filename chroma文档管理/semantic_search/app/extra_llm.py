# -*- coding: utf-8 -*-
"""四合一附加模块共用的 DeepSeek 客户端。"""
from __future__ import annotations

from fastapi import HTTPException
from openai import OpenAI

from semantic_search.app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL

_openai: OpenAI | None = None
_llama_llm = None


def require_deepseek_key() -> str:
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="未配置 DEEPSEEK_API_KEY")
    return DEEPSEEK_API_KEY


def openai_client() -> OpenAI:
    global _openai
    require_deepseek_key()
    if _openai is None:
        _openai = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _openai


def llama_deepseek():
    global _llama_llm
    require_deepseek_key()
    if _llama_llm is None:
        from llama_index.llms.deepseek import DeepSeek

        _llama_llm = DeepSeek(
            model=LLM_MODEL,
            api_key=DEEPSEEK_API_KEY,
            api_base=DEEPSEEK_BASE_URL,
            timeout=120.0,
            context_window=8000,
        )
    return _llama_llm
