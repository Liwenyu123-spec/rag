from fastapi import FastAPI  # 导入 FastAPI 框架，用来写 Web 接口
from fastapi.responses import StreamingResponse, HTMLResponse  # StreamingResponse=流式返回；HTMLResponse=返回网页
from pydantic import BaseModel  # 用来定义请求体的数据结构，并自动校验
from openai import OpenAI  # DeepSeek 兼容 OpenAI 的 SDK，用来调用大模型
import os  # 读取环境变量（API Key）
import json  # 把 Python 字典转成 JSON 字符串，给前端用

app = FastAPI()  # 创建 FastAPI 应用实例，后面所有路由都挂在它上面

client = OpenAI(  # 创建云端 DeepSeek 客户端
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量里取密钥
    base_url="https://api.deepseek.com",  # DeepSeek 云端地址（不是本地 Ollama）
)


class ChatRequest(BaseModel):  # 定义前端 POST /chat 时传来的 JSON 结构
    # 多轮历史格式示例：[{"role":"user","content":"你好"},{"role":"assistant","content":"嗨"}]
    messages: list[dict]  # messages 必须是“字典组成的列表”


@app.get("/", response_class=HTMLResponse)  # 浏览器访问首页 / 时，返回 HTML 页面
def index():  # 处理首页请求的函数
    with open("index.html", encoding="utf-8") as f:  # 打开同目录下的前端页面文件
        return f.read()  # 把文件内容读出来返回给浏览器


@app.get("/page", response_class=HTMLResponse)  # 访问 /page 时返回第二个页面
def page():  # 处理 /page 的函数
    with open("index2.html", encoding="utf-8") as f:  # 打开第二个 HTML 文件
        return f.read()  # 返回页面内容


@app.post("/chat")  # 前端用 POST 方法调用这个聊天接口（才能传完整 messages）
def chat(req: ChatRequest):  # req 会自动把 JSON 解析成 ChatRequest 对象
    """前端传入完整对话历史，后端流式返回本轮助手回复。"""
    stream = client.chat.completions.create(  # 向 DeepSeek 发起一次对话请求
        model="deepseek-v4-flash",  # 使用的云端模型名
        messages=req.messages,  # 把前端传来的多轮历史原样交给模型
        stream=True,  # 开启流式输出：一点一点返回，而不是等整段说完
    )

    def generate():  # 生成器：边从模型收数据，边往前端推
        for chunk in stream:  # 遍历模型返回的每一个数据块
            content = chunk.choices[0].delta.content  # 取出这一小段新增文字（可能是 None）
            if content:  # 如果这小段真有字
                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"  # 按 SSE 格式推给前端
        yield "data: [DONE]\n\n"  # 全部推完后，告诉前端：本轮结束了

    return StreamingResponse(generate(), media_type="text/event-stream")  # 用 SSE 流式响应返回


if __name__ == "__main__":  # 只有直接运行本文件时才执行下面代码（被 import 时不执行）
    import subprocess  # 用来启动外部命令（打开 Cursor 内置浏览器）
    import threading  # 用来开后台线程，避免阻塞服务启动
    import time  # 用来 sleep 等待服务就绪
    import urllib.parse  # 用来把网址编码进 URI 参数
    import uvicorn  # ASGI 服务器，真正把 FastAPI 跑起来

    def open_in_cursor():  # 定义：在 Cursor 内部打开网页的函数
        time.sleep(1.2)  # 先等约 1.2 秒，让 uvicorn 有时间启动
        url = "http://127.0.0.1:8000/"  # 本机服务地址
        # 拼出 Cursor Simple Browser 的专用链接（不是系统 Chrome）
        uri = "cursor://vscode.simple-browser/show?" + urllib.parse.urlencode({"url": url})
        try:  # 优先尝试用 start 打开上面的 cursor:// 链接
            subprocess.Popen(["cmd", "/c", "start", "", uri], shell=False)  # Windows 下启动该 URI
        except Exception:  # 如果上面失败，走兜底方案
            # 兜底：尝试用 cursor 命令打开 Simple Browser
            subprocess.Popen(
                ["cursor", "--reuse-window", "--command", f"simpleBrowser.show {url}"],  # 复用当前窗口执行命令
                shell=False,  # 不走 shell，减少注入风险
            )

    threading.Thread(target=open_in_cursor, daemon=True).start()  # 后台线程去打开页面（daemon=随主程序退出）
    uvicorn.run(app, host="0.0.0.0", port=8000)  # 启动服务：监听所有网卡，端口 8000
