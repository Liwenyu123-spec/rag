# -*- coding: utf-8 -*-
"""基础聊天：流式多轮，不走知识库。"""
from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from semantic_search.app.config import LLM_MODEL
from semantic_search.app.extra_llm import openai_client

router = APIRouter(prefix="/api/basic", tags=["基础聊天"])


class BasicChatRequest(BaseModel):
    messages: list[dict] = Field(..., min_length=1)


@router.post("/chat")
def chat(req: BasicChatRequest):
    stream = openai_client().chat.completions.create(
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
