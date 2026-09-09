"""云端 DeepSeek 多轮对话的 FastAPI 版本；原 909.py 保持不变。"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.deepseek import DeepSeek


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("没有找到 DEEPSEEK_API_KEY，请检查项目目录下的 .env")

app = FastAPI(title="DeepSeek 多轮对话")

llm = DeepSeek(
    model="deepseek-v4-flash",
    api_key=api_key,
    timeout=120.0,
    context_window=8000,
)

# 保存多轮对话历史。此版本适合本机单人使用。
memory = ChatMemoryBuffer.from_defaults(token_limit=10000)
memory.put(ChatMessage(role="system", content="你是我的小苹果"))


@app.get("/", response_class=HTMLResponse)
def index():
    """返回现有聊天页面。"""
    return (BASE_DIR / "chat.html").read_text(encoding="utf-8")


@app.get("/chat", response_class=PlainTextResponse)
def chat(question: str):
    """普通非流式多轮对话。"""
    memory.put(ChatMessage(role="user", content=question))
    response = llm.chat(memory.get())
    answer = response.message.content or ""
    memory.put(ChatMessage(role="assistant", content=answer))
    return answer


@app.get("/stream_chat")
def stream_chat(question: str):
    """以 SSE 格式流式返回多轮对话结果。"""
    memory.put(ChatMessage(role="user", content=question))
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
