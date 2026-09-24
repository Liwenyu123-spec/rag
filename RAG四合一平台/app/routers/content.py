# -*- coding: utf-8 -*-
"""模块3：社交媒体文案 / 电商内容生成。"""
from __future__ import annotations

import json

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from llama_index.core.llms import ChatMessage
from llama_index.llms.deepseek import DeepSeek
from pydantic import BaseModel, Field

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
from app.security import gate

router = APIRouter(prefix="/api/content", tags=["文案生成"])
_llm: DeepSeek | None = None


def _llm_or_raise() -> DeepSeek:
    global _llm
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY")
    if _llm is None:
        _llm = DeepSeek(
            model=LLM_MODEL,
            api_key=DEEPSEEK_API_KEY,
            api_base=DEEPSEEK_BASE_URL,
            timeout=120.0,
            context_window=8000,
        )
    return _llm


class ProductInfo(BaseModel):
    name: str = Field(..., min_length=1)
    features: str = Field(..., min_length=1)
    audience: str = Field(..., min_length=1)


class SocialTopic(BaseModel):
    topic: str = Field(..., min_length=1)


def build_product_messages(product: ProductInfo) -> list[ChatMessage]:
    system_role = """你是一位拥有10年经验的电商金牌文案专家。
请按思维链：1分析人群痛点 2卖点转化 3情感化标题正文 4提取标签。"""
    examples = """
### 示例
输入：无线降噪耳机 / 40dB降噪,30小时续航 / 通勤上班族
输出：
标题：地铁秒变静音舱，通勤族的续命神器！
正文：早高峰太吵？40dB深度降噪一键专注。30小时续航告别电量焦虑。
标签：#通勤必备 #降噪耳机 #职场好物
"""
    info = json.dumps(product.model_dump(), ensure_ascii=False)
    return [
        ChatMessage(role="system", content=system_role),
        ChatMessage(role="user", content=examples + f"\n\n请生成文案：{info}\n输出："),
    ]


@router.post("/product_copy")
def product_copy(product: ProductInfo):
    for value in (product.name, product.features, product.audience):
        _, err = gate(value)
        if err:
            return JSONResponse({"error": err}, status_code=400)
    try:
        response = _llm_or_raise().chat(build_product_messages(product))
        return {"product": product.model_dump(), "result": response.message.content or ""}
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=500)


@router.get("/self_consistency")
def self_consistency(question: str = Query(..., min_length=1), num: int = Query(2, ge=2, le=5)):
    cleaned, err = gate(question)
    if err:
        return JSONResponse({"error": err}, status_code=400)
    base = f"你是创意文案专家。任务：{cleaned}\n要求：口号不超过15字，只输出一句。"
    angles = ["自由探索", "可靠品质", "冒险精神", "轻便舒适", "陪伴旅途"]
    candidates = []
    llm = _llm_or_raise()
    for i in range(num):
        text = (llm.complete(base + f"\n请从「{angles[i]}」角度给出口号：").text or "").strip()
        candidates.append(text)
    final = (
        llm.complete(
            f"从以下口号选最佳并只输出口号：\n"
            + "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
        ).text
        or ""
    ).strip()
    return {"candidates": candidates, "final": final}


@router.post("/social_plan")
def social_plan(body: SocialTopic):
    cleaned, err = gate(body.topic)
    if err:
        return JSONResponse({"error": err}, status_code=400)
    llm = _llm_or_raise()
    try:
        ideas = (
            llm.complete(
                f"你是小红书/抖音运营总监。主题：**{cleaned}**。\n"
                "提出3个方向：A干货科普 B情感故事 C争议挑战。简述每个核心思路。"
            ).text
            or ""
        )
        evaluation = (
            llm.complete(
                f"基于方向：\n{ideas}\n请评估爆款率与执行难度，选出最推荐方向并说明理由。"
            ).text
            or ""
        )
        plan = (
            llm.complete(
                f"采用策略：\n{evaluation}\n生成下周5条内容日历（Markdown表格："
                "星期|选题标题|封面建议|文案结构），标题要有爆款感。"
            ).text
            or ""
        )
        return {"topic": cleaned, "ideas": ideas, "evaluation": evaluation, "plan": plan}
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=500)
