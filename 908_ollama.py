# 本地 Ollama 多轮对话版（不影响 908.py 的云端 DeepSeek）
from fastapi import FastAPI  # Web 框架
from fastapi.responses import StreamingResponse, HTMLResponse  # 流式响应 / 返回网页
from pydantic import BaseModel  # 校验前端传来的 JSON
import ollama  # 本地 Ollama 官方 Python 客户端
import json  # 把字典转成 JSON 字符串

app = FastAPI()  # 创建应用

# 连接本机 Ollama（默认端口 11434）
# 若要用局域网其他机器，改成如：http://192.168.x.x:11434
client = ollama.Client(host="http://127.0.0.1:11434")

# 你本机已下载的模型；可用命令 ollama list 查看
MODEL_NAME = "deepseek-r1:1.5b"


class ChatRequest(BaseModel):  # 与云端版相同的请求结构，方便前端复用思路
    # 多轮历史：[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]
    messages: list[dict]


@app.get("/", response_class=HTMLResponse)  # 首页：本地对话页面
def index():
    with open("index_ollama.html", encoding="utf-8") as f:  # 读 Ollama 专用前端
        return f.read()


@app.post("/chat")  # 多轮聊天接口（POST，可传完整 messages）
def chat(req: ChatRequest):
    """前端传入完整对话历史，后端用本地 Ollama 流式返回本轮回复。"""
    stream = client.chat(  # 调用本地模型
        model=MODEL_NAME,  # 本地模型名
        messages=req.messages,  # 多轮历史原样传入
        stream=True,  # 流式输出
    )

    def generate():  # 边收边推给浏览器
        for chunk in stream:  # Ollama 每个 chunk 结构与 OpenAI 不同
            content = chunk.get("message", {}).get("content")  # 取出本段文字
            if content:  # 有内容再推
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"  # 本轮结束标记

    return StreamingResponse(generate(), media_type="text/event-stream")  # SSE 流


if __name__ == "__main__":  # 直接运行本文件时启动
    import subprocess
    import threading
    import time
    import urllib.parse
    import webbrowser
    import uvicorn

    # 用 8001，避免和云端版 908.py（8000）抢端口
    PORT = 8001

    def open_page():
        time.sleep(1.5)
        url = f"http://127.0.0.1:{PORT}/"
        print(f"正在打开本地 Ollama 对话页: {url}")
        uri = "cursor://vscode.simple-browser/show?" + urllib.parse.urlencode({"url": url})
        try:
            subprocess.Popen(["cmd", "/c", "start", "", uri], shell=False)
        except Exception as e:
            print("Cursor 内置浏览器启动失败:", e)
        try:
            subprocess.Popen(["cursor", "-r", uri], shell=False)
        except Exception:
            pass
        time.sleep(0.5)
        webbrowser.open(url)

    threading.Thread(target=open_page, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=PORT)
