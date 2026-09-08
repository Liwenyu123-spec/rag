from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


class ChatRequest(BaseModel):
    # 多轮历史：[{role: user/assistant/system, content: ...}, ...]
    messages: list[dict]


@app.get("/", response_class=HTMLResponse)
def index():
    with open("index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/page", response_class=HTMLResponse)
def page():
    with open("index2.html", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
def chat(req: ChatRequest):
    """前端传入完整对话历史，后端流式返回本轮助手回复。"""
    stream = client.chat.completions.create(
        model="deepseek-v4-flash",
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


if __name__ == "__main__":
    import threading
    import time
    import webbrowser
    import uvicorn

    def open_browser():
        time.sleep(1.2)  # 等服务先起来
        webbrowser.open("http://127.0.0.1:8000/")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
