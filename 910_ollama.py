"""本地 Ollama 版本：功能与 910.py 对齐，前端共用 React dist。
不消耗 DeepSeek 云端额度；请先确认 Ollama 已启动且已拉取模型。
"""

import ast
import json
import math
import operator
import os
import re
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

MODEL_NAME = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

app = FastAPI(title="Ollama 提示词策略 + 安全防护")

llm = Ollama(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    request_timeout=180.0,
    context_window=8000,
)

BASE_SYSTEM_PROMPT = ""
current_system_prompt = BASE_SYSTEM_PROMPT

memory = ChatMemoryBuffer.from_defaults(token_limit=10000)


def rebuild_memory(system_prompt: str | None = None):
    """按当前 system prompt 重建服务端记忆。"""
    global memory, current_system_prompt
    if system_prompt is not None:
        current_system_prompt = system_prompt.strip()
    memory = ChatMemoryBuffer.from_defaults(token_limit=10000)
    if current_system_prompt:
        memory.put(ChatMessage(role="system", content=current_system_prompt))
    return current_system_prompt


# React 构建产物静态资源
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


# ---------- demo01：四种提示词策略 ----------
PROMPT_MODES = {
    "zero_shot": """请直接完成用户任务。
要求：突出核心卖点，文案风格清晰，必要时附带话题标签。""",

    "few_shot": """你是一位专业的文案策划师。请参考下面示例格式生成内容。

示例1：
输入：产品-智能手表，特点-健康监测、运动追踪、长续航
输出：你的私人健康管家来啦！24小时健康监测，精准运动追踪，超长续航不用频繁充电。#智能手表 #健康生活 #运动达人

示例2：
输入：产品-无线耳机，特点-降噪功能、高清音质、舒适佩戴
输出：沉浸式音乐体验，从此告别噪音干扰！高清音质还原每一个音符，人体工学设计久戴不累。#无线耳机 #降噪神器 #音乐爱好者

现在请按同样格式处理用户的任务。""",

    "cot": """请按以下步骤思考后再给出最终答案：
1. 目标受众分析
2. 核心卖点提炼（3个）
3. 内容结构设计（开头/中间/结尾）
4. 语言风格确定
5. 互动引导设计
最后输出完整结果。""",

    "tot": """请构建思维树，探索不同方向：
主干：用户任务的最优解决方案
分支1：内容创意方向（传统文化 / 现代生活 / 跨界合作）
分支2：平台策略方向（短视频 / 社交电商 / 私域）
分支3：用户互动方向（UGC / 体验活动 / KOL）
请为每个子分支给出具体方案并评估可行性，最后推荐最佳组合。""",
}


# ---------- demo03 + demo04：输入净化（多层防护第 1 层） ----------
def moderation_input(user_input: str):
    """对用户输入做安全检查；通过则返回净化后的文本，失败则返回以 Invalid 开头的错误。"""
    if not user_input or not isinstance(user_input, str):
        return "Invalid input"

    if len(user_input) > 1000:
        return "Invalid Input too long"

    dangerous_patterns = [
        r"ignore\s+(previous|all|above)\s+(instructions|prompts|rules)",
        r"forget\s+(all|previous|your)\s+(instructions|rules|constraints)",
        r"disregard\s+(previous|all)\s+instructions",
        r"override\s+(system|previous)\s+(prompt|instructions)",
        r"(you\s+are|act\s+as|pretend\s+to\s+be)\s+(system|developer|admin|administrator)",
        r"(new\s+role|new\s+instruction):\s*",
        r"system:\s*",
        r"assistant:\s*",
        r"user:\s*(?=\s*ignore|\s*override|\s*change)",
        r"output\s+(format|mode|as)",
        r"print\s+(the|your)\s+(system|prompt|instructions)",
        r"show\s+(me|your)\s+(system|prompt|instructions|rules)",
        r"reveal\s+(your|the)\s+(system|prompt|instructions)",
        r"<script>",
        r"javascript:",
        r"eval\(",
        r"exec\(",
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\b.*\b(FROM|INTO|TABLE)\b)",
        r"{%.*%}",
        r"\{\{.*\}\}",
        # 中文常见注入说法
        r"忽略(之前|以上|全部).*(指令|提示|规则)",
        r"忘记(你的|之前).*(指令|规则)",
        r"你现在是(系统|管理员|开发者)",
        r"告诉我(你的|系统)(提示词|指令|规则)",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return "Invalid input detected - potential security threat"

    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", user_input)

    if re.search(r"(.)\1{50,}", sanitized):
        return "Invalid input - repeated characters detected"

    return sanitized


def build_user_content(question: str, mode: str) -> str:
    """把策略提示词拼到用户问题前面（demo01）。"""
    strategy = PROMPT_MODES.get(mode, PROMPT_MODES["zero_shot"])
    return f"{strategy}\n\n用户任务：\n{question}"


@app.get("/")
def index():
    """与云端版共用 React 前端。"""
    spa = FRONTEND_DIST / "index.html"
    if spa.exists():
        return FileResponse(spa)
    page = BASE_DIR / "chat_910.html"
    if not page.exists():
        page = BASE_DIR / "chat.html"
    return HTMLResponse(page.read_text(encoding="utf-8"))


@app.post("/reset")
def reset_memory():
    """新建对话时清空服务端记忆（保留当前 system prompt）。"""
    rebuild_memory()
    return {"ok": True, "system_prompt": current_system_prompt}


class SystemPromptBody(BaseModel):
    content: str = Field(default="", description="可编辑的系统提示词")


@app.get("/system_prompt")
def get_system_prompt():
    return {"content": current_system_prompt}


@app.post("/system_prompt")
def set_system_prompt(body: SystemPromptBody):
    """更新 system prompt，并重建服务端记忆。"""
    cleaned = body.content.strip()
    if len(cleaned) > 4000:
        return JSONResponse({"error": "System prompt too long"}, status_code=400)
    for pattern in [
        r"<script>",
        r"javascript:",
        r"eval\(",
        r"exec\(",
    ]:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return JSONResponse({"error": "Invalid system prompt"}, status_code=400)
    prompt = rebuild_memory(cleaned)
    return {"ok": True, "content": prompt}


@app.get("/modes")
def list_modes():
    """返回可选提示词模式，方便前端下拉框展示。"""
    return {
        "modes": [
            {"id": "zero_shot", "name": "零样本"},
            {"id": "few_shot", "name": "少样本"},
            {"id": "cot", "name": "思维链"},
            {"id": "tot", "name": "思维树"},
        ],
        "backend": "ollama",
        "model": MODEL_NAME,
    }


@app.get("/chat", response_class=PlainTextResponse)
def chat(
    question: str = Query(..., min_length=1),
    mode: str = Query("zero_shot"),
):
    """普通非流式多轮对话：先净化，再按策略组装提示词。"""
    cleaned = moderation_input(question)
    if cleaned.startswith("Invalid"):
        return cleaned

    user_content = build_user_content(cleaned, mode)
    memory.put(ChatMessage(role="user", content=user_content))
    response = llm.chat(memory.get())
    answer = response.message.content or ""
    memory.put(ChatMessage(role="assistant", content=answer))
    return answer


@app.get("/stream_chat")
def stream_chat(
    question: str = Query(..., min_length=1),
    mode: str = Query("zero_shot"),
):
    """流式多轮对话：同样先做输入净化。"""
    cleaned = moderation_input(question)
    if cleaned.startswith("Invalid"):

        def reject():
            data = json.dumps({"content": cleaned}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(reject(), media_type="text/event-stream")

    user_content = build_user_content(cleaned, mode)
    memory.put(ChatMessage(role="user", content=user_content))
    response = llm.stream_chat(memory.get())

    def generate():
        answer = ""
        for chunk in response:
            delta = chunk.delta or ""
            answer += delta
            data = json.dumps({"content": delta}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        memory.put(ChatMessage(role="assistant", content=answer))
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


# ---------- demo02：自我一致性（多角度生成候选，再评选最优） ----------
@app.get("/self_consistency")
def self_consistency(question: str = Query(..., min_length=1), num: int = Query(2, ge=2, le=5)):
    """默认只生成 2 个候选再评选，缩短等待时间。"""
    cleaned = moderation_input(question)
    if cleaned.startswith("Invalid"):
        return JSONResponse({"error": cleaned}, status_code=400)

    base_prompt = f"""你是一位创意文案专家。
任务：{cleaned}
要求：简洁有力，突出核心价值。口号不超过15个字。"""

    angle_prompts = [
        "请从「自由探索」的角度给出一个方案，只输出一句口号：",
        "请从「可靠品质」的角度给出一个方案，只输出一句口号：",
        "请从「冒险精神」的角度给出一个方案，只输出一句口号：",
        "请从「轻便舒适」的角度给出一个方案，只输出一句口号：",
        "请从「陪伴旅途」的角度给出一个方案，只输出一句口号：",
    ]

    candidates = []
    for i in range(num):
        varied = base_prompt + "\n" + angle_prompts[i]
        result = llm.complete(varied)
        candidates.append((result.text or "").strip())

    evaluation_prompt = f"""请从以下{len(candidates)}个方案中选择最佳的一个，并只输出最终口号：
{chr(10).join([f"{i + 1}. {c}" for i, c in enumerate(candidates)])}
"""
    final = llm.complete(evaluation_prompt)
    return {
        "candidates": candidates,
        "final": (final.text or "").strip(),
    }


# ---------- demo05：电商产品描述（Few-Shot + CoT） ----------
class ProductInfo(BaseModel):
    name: str = Field(..., min_length=1, description="产品名称")
    features: str = Field(..., min_length=1, description="产品卖点")
    audience: str = Field(..., min_length=1, description="目标人群")


def build_product_messages(product: ProductInfo) -> list[ChatMessage]:
    system_role = """你是一位拥有10年经验的电商金牌文案专家。
你的任务是为用户提供的产品撰写极具吸引力的产品描述。
请遵循以下思维链步骤进行思考：
1. 分析目标人群画像，确定他们的核心痛点。
2. 将产品卖点转化为解决痛点的方案。
3. 运用情感化语言撰写标题和正文。
4. 提取高流量关键词作为标签。"""

    examples = """
### 示例 1
输入：{"name": "无线降噪耳机", "features": "40dB深度降噪, 30小时续航", "audience": "通勤上班族"}
思考过程：通勤族痛点是地铁嘈杂和电量焦虑 -> 卖点转化为"地铁静音舱"和"一周一充" -> 风格要高级且实用。
输出：
    标题：地铁秒变静音舱，通勤族的续命神器！
    正文：早高峰的地铁太吵？这款耳机拥有40dB深度降噪，一键开启专注模式。30小时超长续航，告别电量焦虑，让上班路变成你的私人音乐厅。
    标签：#通勤必备 #降噪耳机 #职场好物

### 示例 2
输入：{"name": "低脂鸡胸肉", "features": "0淀粉, 嫩滑不柴", "audience": "减脂健身人群"}
思考过程：健身人群怕胖但怕肉柴 -> 强调"0负担"和"口感好" -> 风格要健康有食欲。
输出：
    标题：谁说减脂只能吃草？这块肉嫩到爆汁！
    正文：拒绝干柴口感！独家低温慢煮工艺，锁住肉汁。0淀粉添加，高蛋白低脂肪，每一口都是对身材的负责，好吃不胖。
    标签：#减脂餐 #健身食谱 #低卡零食
"""

    product_info = {
        "name": product.name,
        "features": product.features,
        "audience": product.audience,
    }
    user_input = f"""请根据以下产品信息，按照上述逻辑生成文案：
产品信息：{json.dumps(product_info, ensure_ascii=False)}
输出："""

    return [
        ChatMessage(role="system", content=system_role),
        ChatMessage(role="user", content=examples + "\n\n" + user_input),
    ]


@app.post("/product_copy")
def product_copy(product: ProductInfo):
    """电商产品描述生成：Few-Shot + CoT，不写入多轮 memory。"""
    for value in (product.name, product.features, product.audience):
        cleaned = moderation_input(value)
        if cleaned.startswith("Invalid"):
            return JSONResponse({"error": cleaned}, status_code=400)

    messages = build_product_messages(product)
    try:
        response = llm.chat(messages)
        text = response.message.content or ""
        return {
            "product": product.model_dump(),
            "result": text,
        }
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=500)


# ---------- demo06：社交媒体策划（ToT 四阶段） ----------
class SocialTopic(BaseModel):
    topic: str = Field(..., min_length=1, description="内容主题")


def _complete_text(prompt: str, temperature_hint: str = "") -> str:
    """用 LlamaIndex complete 生成一段文本。"""
    full = prompt if not temperature_hint else f"{prompt}\n\n（生成风格提示：{temperature_hint}）"
    result = llm.complete(full)
    return (result.text or "").strip()


@app.post("/social_plan")
def social_plan(body: SocialTopic):
    """社交媒体 ToT 策划：发散 → 评估 → 日历 → 优化。耗时较长。"""
    cleaned = moderation_input(body.topic)
    if cleaned.startswith("Invalid"):
        return JSONResponse({"error": cleaned}, status_code=400)

    try:
        ideas = _complete_text(
            f"""你是一位拥有百万粉丝的小红书/抖音运营总监。
我们的主题是：**{cleaned}**。

请进行头脑风暴，提出3个截然不同的内容策划方向（分支）：
- 分支 A：干货科普类（强调专业度）
- 分支 B：情感共鸣/故事类（强调人设和情绪）
- 分支 C：争议/挑战类（强调互动和流量）

请简要描述每个方向的核心思路。""",
            "创意发散",
        )

        evaluation = _complete_text(
            f"""基于刚才提出的三个方向：
{ideas}

请以“爆款率”和“执行难度”为标准进行评估：
1. 分析每个方向的潜在风险。
2. 选出**最推荐的一个方向**，并说明理由。""",
            "理性分析",
        )

        draft_plan = _complete_text(
            f"""我们决定采用以下策略：
{evaluation}

请基于这个策略，为我生成一份**下周的内容发布日历**（包含5条内容）。

输出格式要求（Markdown 表格）：
| 星期 | 选题标题 (包含爆款关键词) | 封面图建议 | 核心文案结构 |
| :--- | :--- | :--- | :--- |
要求：标题要足够吸引人，文案结构要包含“黄金前3秒”的设计。""",
            "执行落地",
        )

        plan = _complete_text(
            f"""这是生成的初稿计划：
{draft_plan}

请作为一名挑剔的“审核编辑”进行审查：
1. 指出其中哪个标题最没有吸引力，并给出修改建议。
2. 优化整个计划的语气，使其更具网感（使用更多 Emoji 和流行语）。
请输出优化后的最终版本。""",
            "润色优化",
        )

        return {
            "topic": cleaned,
            "ideas": ideas,
            "evaluation": evaluation,
            "plan": plan,
        }
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=500)


@app.get("/social_plan_stream")
def social_plan_stream(topic: str = Query(..., min_length=1)):
    """社交媒体策划流式阶段输出，方便前端显示进度。"""
    cleaned = moderation_input(topic)
    if cleaned.startswith("Invalid"):

        def reject():
            yield f"data: {json.dumps({'stage': 'error', 'content': cleaned}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(reject(), media_type="text/event-stream")

    def generate():
        try:
            yield f"data: {json.dumps({'stage': 1, 'title': '发散方向', 'content': '正在构思 3 个策划分支…'}, ensure_ascii=False)}\n\n"
            ideas = _complete_text(
                f"""你是一位拥有百万粉丝的小红书/抖音运营总监。
我们的主题是：**{cleaned}**。
请提出3个截然不同的内容策划方向：干货科普 / 情感故事 / 争议挑战。简要描述每个方向。""",
                "创意发散",
            )
            yield f"data: {json.dumps({'stage': 1, 'title': '发散方向', 'content': ideas}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'stage': 2, 'title': '评估剪枝', 'content': '正在评估爆款率与执行难度…'}, ensure_ascii=False)}\n\n"
            evaluation = _complete_text(
                f"""基于以下三个方向：\n{ideas}\n\n请评估风险并选出最推荐的一个方向，说明理由。""",
                "理性分析",
            )
            yield f"data: {json.dumps({'stage': 2, 'title': '评估剪枝', 'content': evaluation}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'stage': 3, 'title': '内容日历', 'content': '正在生成下周 5 条内容日历…'}, ensure_ascii=False)}\n\n"
            draft_plan = _complete_text(
                f"""策略：\n{evaluation}\n\n请生成下周内容发布日历（5条），Markdown 表格：星期|选题标题|封面图建议|核心文案结构。标题要吸引人，含黄金前3秒。""",
                "执行落地",
            )
            yield f"data: {json.dumps({'stage': 3, 'title': '内容日历', 'content': draft_plan}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'stage': 4, 'title': '审核优化', 'content': '正在润色标题与网感…'}, ensure_ascii=False)}\n\n"
            plan = _complete_text(
                f"""初稿：\n{draft_plan}\n\n请作为审核编辑：指出最弱标题并给修改建议；整体语气更有网感（Emoji/流行语）。输出最终版。""",
                "润色优化",
            )
            yield f"data: {json.dumps({'stage': 4, 'title': '最终策划', 'content': plan, 'done': True}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'stage': 'error', 'content': f'API error: {e}'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


# ---------- 多模式对比（同一问题，多种提示词策略并排） ----------
class CompareBody(BaseModel):
    question: str = Field(..., min_length=1)
    modes: list[str] = Field(default_factory=lambda: ["zero_shot", "cot", "tot"])


@app.post("/compare")
def compare_modes(body: CompareBody):
    """不写入多轮 memory，独立跑多种策略便于课堂对比。"""
    cleaned = moderation_input(body.question)
    if cleaned.startswith("Invalid"):
        return JSONResponse({"error": cleaned}, status_code=400)

    modes = [m for m in body.modes if m in PROMPT_MODES] or ["zero_shot", "cot", "tot"]
    results: dict[str, str] = {}
    try:
        for mode in modes:
            messages: list[ChatMessage] = []
            if current_system_prompt:
                messages.append(ChatMessage(role="system", content=current_system_prompt))
            messages.append(ChatMessage(role="user", content=build_user_content(cleaned, mode)))
            response = llm.chat(messages)
            results[mode] = response.message.content or ""
        return {"question": cleaned, "modes": modes, "results": results}
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=500)


# ---------- 纯文本工具调用演示（ReAct 风格，不依赖多模态） ----------
DEMO_NOTES = [
    {"id": "n1", "title": "提示词策略", "body": "零样本直接做；少样本给示例；思维链分步想；思维树多分支再选。"},
    {"id": "n2", "title": "自我一致性", "body": "同一任务多角度生成候选，再评选最优口号或方案。"},
    {"id": "n3", "title": "输入净化", "body": "拦截提示词注入、脚本与危险 SQL 模式，降低越权风险。"},
]

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _safe_eval_math(expr: str) -> str:
    expr = expr.strip().replace("^", "**")
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        return f"表达式语法错误: {e}"

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _SAFE_OPS:
            return _SAFE_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _SAFE_OPS:
            return _SAFE_OPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {"sqrt", "abs", "round"}:
            fn = {"sqrt": math.sqrt, "abs": abs, "round": round}[n.func.id]
            return fn(*[_eval(a) for a in n.args])
        raise ValueError("仅支持数字与 + - * / ** % 及 sqrt/abs/round")

    try:
        return str(_eval(node))
    except Exception as e:
        return f"计算失败: {e}"


def _tool_weather(city: str) -> str:
    catalog = {
        "北京": "晴，18~26℃，东北风 2 级",
        "上海": "多云，20~27℃，东南风 3 级",
        "广州": "阵雨，24~31℃，湿度 80%",
        "深圳": "阴，23~30℃，偏南风",
        "杭州": "晴转多云，19~28℃",
        "成都": "小雨，17~23℃",
    }
    key = city.strip() or "北京"
    for name, info in catalog.items():
        if name in key:
            return f"{name}：{info}（演示数据）"
    return f"{key}：晴间多云，22℃ 左右（演示默认数据）"


def _tool_note_search(query: str) -> str:
    q = query.strip().lower()
    hits = [
        n
        for n in DEMO_NOTES
        if q in n["title"].lower() or q in n["body"].lower()
    ]
    if not hits:
        hits = DEMO_NOTES
    return "\n".join([f"- {n['title']}：{n['body']}" for n in hits[:3]])


def run_tool(name: str, arg: str) -> str:
    name = name.strip().lower()
    if name in {"calculator", "calc", "math"}:
        return _safe_eval_math(arg)
    if name in {"weather", "天气"}:
        return _tool_weather(arg)
    if name in {"now", "time", "datetime", "时间"}:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if name in {"note_search", "notes", "笔记"}:
        return _tool_note_search(arg)
    return f"未知工具：{name}。可用：calculator / weather / now / note_search"


class ToolChatBody(BaseModel):
    question: str = Field(..., min_length=1)


@app.post("/tool_chat")
def tool_chat(body: ToolChatBody):
    """纯文本 ReAct：模型输出 TOOL 或 FINAL，服务端执行本地工具。"""
    cleaned = moderation_input(body.question)
    if cleaned.startswith("Invalid"):
        return JSONResponse({"error": cleaned}, status_code=400)

    system = """你是带工具能力的助手。只能通过下列工具获取外部信息，不要编造工具结果。

可用工具：
1) calculator — 参数：数学表达式，如 12*(3+4)
2) weather — 参数：城市名，如 北京
3) now — 参数：任意（可空），返回当前时间
4) note_search — 参数：关键词，搜索本地课堂笔记

输出格式（严格二选一，不要多余解释）：
TOOL: 工具名 | 参数
或
FINAL: 最终中文回答

需要信息时先 TOOL，拿到结果后再 FINAL。"""

    transcript = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=cleaned),
    ]
    steps: list[dict] = []
    try:
        for _ in range(4):
            response = llm.chat(transcript)
            text = (response.message.content or "").strip()
            transcript.append(ChatMessage(role="assistant", content=text))

            tool_match = re.search(r"TOOL\s*[:：]\s*([^|\n]+)\|\s*(.+)", text, re.I | re.S)
            final_match = re.search(r"FINAL\s*[:：]\s*(.+)", text, re.I | re.S)

            if tool_match:
                tool_name = tool_match.group(1).strip()
                tool_arg = tool_match.group(2).strip()
                result = run_tool(tool_name, tool_arg)
                steps.append({"type": "tool", "name": tool_name, "arg": tool_arg, "result": result})
                transcript.append(
                    ChatMessage(role="user", content=f"工具结果（{tool_name}）：{result}\n请继续，需要则再 TOOL，否则 FINAL。")
                )
                continue

            if final_match:
                answer = final_match.group(1).strip()
                steps.append({"type": "final", "content": answer})
                return {"question": cleaned, "steps": steps, "answer": answer}

            # 模型没按格式：把整段当最终答案
            steps.append({"type": "final", "content": text})
            return {"question": cleaned, "steps": steps, "answer": text}

        answer = steps[-1]["content"] if steps and steps[-1].get("type") == "final" else "工具调用轮次用尽，请换个问法。"
        return {"question": cleaned, "steps": steps, "answer": answer}
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8002")).start()
    # 8002：避免和 909(8000)、910 云端(8001) 冲突
    uvicorn.run(app, host="127.0.0.1", port=8002)
