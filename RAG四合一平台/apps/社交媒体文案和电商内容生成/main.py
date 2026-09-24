"""项目：社交媒体文案和电商内容生成综合案例

原文件：910.py（文案部分）。
含：电商产品描述、社交媒体 ToT 策划、自我一致性口号评选。
启动：python 社交媒体文案和电商内容生成/main.py
页面：http://127.0.0.1:8002/
"""

import json
import os
import re
import threading
import webbrowser
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from llama_index.core.llms import ChatMessage
from llama_index.llms.deepseek import DeepSeek
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
load_dotenv(REPO_ROOT / ".env", override=True)
load_dotenv(BASE_DIR / ".env", override=True)

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("没有找到 DEEPSEEK_API_KEY，请检查项目目录下的 .env")

app = FastAPI(title="社交媒体文案和电商内容生成")

llm = DeepSeek(
    model="deepseek-v4-flash",
    api_key=api_key,
    timeout=120.0,
    context_window=8000,
)

SAFE_REJECT_REPLY = "非常抱歉，我目前无法回答这个问题。"


def moderation_input(user_input: str):
    """简易输入净化（复用原 910 思路）。"""
    patterns = [
        r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"jailbreak",
        r"DAN\s+mode",
        r"override\s+(system|previous)\s+(prompt|instructions)",
        r"(you\s+are|act\s+as|pretend\s+to\s+be)\s+(system|developer|admin|administrator)",
        r"system:\s*",
        r"print\s+(the|your)\s+(system|prompt|instructions)",
        r"show\s+(me|your)\s+(system|prompt|instructions|rules)",
        r"reveal\s+(your|the)\s+(system|prompt|instructions)",
    ]
    text = user_input or ""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return None
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    if re.search(r"(.)\1{50,}", sanitized):
        return None
    return sanitized


def gate_user_input(user_input: str) -> tuple[str | None, str | None]:
    cleaned = moderation_input(user_input)
    if cleaned is None:
        return None, SAFE_REJECT_REPLY
    return cleaned, None


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>文案生成综合案例</title>
  <style>
    body{font-family:Microsoft YaHei,sans-serif;max-width:860px;margin:32px auto;padding:0 16px;color:#0f172a}
    h1{font-size:22px} section{border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin:16px 0}
    label{display:block;margin:8px 0 4px;font-size:14px;color:#475569}
    input,textarea{width:100%;box-sizing:border-box;padding:8px 10px;border:1px solid #cbd5e1;border-radius:8px}
    button{margin-top:12px;padding:8px 14px;border:0;border-radius:8px;background:#0f172a;color:#fff;cursor:pointer}
    pre{white-space:pre-wrap;background:#f8fafc;padding:12px;border-radius:8px;min-height:80px}
  </style>
</head>
<body>
  <h1>社交媒体文案和电商内容生成</h1>
  <section>
    <h2>电商产品描述</h2>
    <label>产品名称</label><input id="name" value="无线降噪耳机"/>
    <label>核心卖点</label><input id="features" value="40dB深度降噪, 30小时续航"/>
    <label>目标人群</label><input id="audience" value="通勤上班族"/>
    <button onclick="genProduct()">生成文案</button>
    <pre id="productOut">结果会显示在这里</pre>
  </section>
  <section>
    <h2>社交媒体策划（ToT）</h2>
    <label>主题</label><input id="topic" value="夏季减肥"/>
    <button onclick="genSocial()">生成策划</button>
    <pre id="socialOut">结果会显示在这里（较慢）</pre>
  </section>
  <section>
    <h2>自我一致性口号</h2>
    <label>任务</label><input id="slogan" value="为户外运动鞋写一句广告口号"/>
    <button onclick="genSlogan()">评选口号</button>
    <pre id="sloganOut">结果会显示在这里</pre>
  </section>
<script>
async function genProduct(){
  const body={name:name.value,features:features.value,audience:audience.value};
  productOut.textContent='生成中...';
  const r=await fetch('/product_copy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const j=await r.json(); productOut.textContent=j.result||JSON.stringify(j,null,2);
}
async function genSocial(){
  socialOut.textContent='生成中，可能需要几十秒...';
  const r=await fetch('/social_plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:topic.value})});
  const j=await r.json();
  socialOut.textContent=[j.ideas,j.evaluation,j.plan].filter(Boolean).join('\n\n——\n\n')||JSON.stringify(j,null,2);
}
async function genSlogan(){
  sloganOut.textContent='生成中...';
  const r=await fetch('/self_consistency?question='+encodeURIComponent(slogan.value)+'&num=2');
  const j=await r.json();
  sloganOut.textContent='候选:\n'+(j.candidates||[]).map((c,i)=>`${i+1}. ${c}`).join('\n')+'\n\n最佳: '+(j.final||'');
}
</script>
</body></html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


@app.get("/health")
def health():
    return {"ok": True, "project": "社交媒体文案和电商内容生成", "model": "deepseek-v4-flash"}


# ---------- demo02：自我一致性（多角度生成候选，再评选最优） ----------
@app.get("/self_consistency")
def self_consistency(question: str = Query(..., min_length=1), num: int = Query(2, ge=2, le=5)):
    """默认只生成 2 个候选再评选，缩短等待时间。"""
    cleaned, err = gate_user_input(question)
    if err:
        return JSONResponse({"error": err}, status_code=400)

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
        cleaned, err = gate_user_input(value)
        if err:
            return JSONResponse({"error": err}, status_code=400)

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


@app.get("/copywriting")
def copywriting_alias(
    name: str = Query(..., min_length=1),
    features: str = Query(..., min_length=1),
    audience: str = Query(..., min_length=1),
):
    """老师案例 06 接口别名：/copywriting → /product_copy。"""
    return product_copy(ProductInfo(name=name, features=features, audience=audience))


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
    cleaned, err = gate_user_input(body.topic)
    if err:
        return JSONResponse({"error": err}, status_code=400)

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


@app.get("/social")
def social_alias(topic: str = Query(..., min_length=1)):
    """老师案例 06 接口别名：/social → /social_plan。"""
    return social_plan(SocialTopic(topic=topic))


@app.get("/social_plan_stream")
def social_plan_stream(topic: str = Query(..., min_length=1)):
    """社交媒体策划流式阶段输出，方便前端显示进度。"""
    cleaned, err = gate_user_input(topic)
    if err:

        def reject():
            yield f"data: {json.dumps({'stage': 'error', 'content': err}, ensure_ascii=False)}\n\n"
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



if __name__ == "__main__":
    import uvicorn

    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8002")).start()
    uvicorn.run(app, host="127.0.0.1", port=8002)
