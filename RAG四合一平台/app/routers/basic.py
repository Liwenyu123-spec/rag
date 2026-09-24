# -*- coding: utf-8 -*-
"""模块1：基础聊天（流式多轮，前端自带 messages）。"""
from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL

router = APIRouter(prefix="/api/basic", tags=["基础聊天"])

_client: OpenAI | None = None


def _client_or_raise() -> OpenAI:
    global _client
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY")
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


class BasicChatRequest(BaseModel):
    messages: list[dict] = Field(..., min_length=1)


@router.post("/chat")
def chat(req: BasicChatRequest):
    """流式返回助手回复（SSE）。"""
    stream = _client_or_raise().chat.completions.create(
        model=LLM_MODEL,
        messages=req.messages,
        stream=True,
    )

    def generate():
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
