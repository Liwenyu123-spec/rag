from fastapi import FastAPI  # 导入 FastAPI 框架，用来写 Web 接口
from fastapi.responses import StreamingResponse, HTMLResponse  # StreamingResponse=流式返回；HTMLResponse=返回网页
from pydantic import BaseModel  # 用来定义请求体的数据结构，并自动校验
from openai import OpenAI  # DeepSeek 兼容 OpenAI 的 SDK，用来调用大模型
from dotenv import load_dotenv  # 读取项目目录 .env（各 IDE 通用兜底）
import os  # 读取环境变量（API Key）
import json  # 把 Python 字典转成 JSON 字符串，给前端用
import winreg  # 从 Windows 注册表读用户/系统环境变量


load_dotenv()  # 自动加载同目录 .env；不依赖 IDE 是否注入环境变量


def _reg_get(root, path, name):  # 从注册表读一个环境变量
    try:
        with winreg.OpenKey(root, path) as reg:
            value, _ = winreg.QueryValueEx(reg, name)
            return value or None
    except OSError:
        return None


def get_deepseek_api_key():  # 进程 → .env(已 load) → 用户变量 → 系统变量
    key = os.getenv("DEEPSEEK_API_KEY")
    if key:
        return key
    key = _reg_get(winreg.HKEY_CURRENT_USER, r"Environment", "DEEPSEEK_API_KEY")
    if key:
        return key
    return _reg_get(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        "DEEPSEEK_API_KEY",
    )


app = FastAPI()  # 创建 FastAPI 应用实例，后面所有路由都挂在它上面

client = OpenAI(  # 创建云端 DeepSeek 客户端
    api_key="DEEPSEEK_API_KEY",  # 兼容 Cursor / PyCharm / 任意 IDE
    base_url="https://api.deepseek.com",
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
    import subprocess  # 用来启动外部命令
    import threading  # 用来开后台线程，避免阻塞服务启动
    import time  # 用来 sleep 等待服务就绪
    import urllib.parse  # 用来把网址编码进 URI 参数
    import webbrowser  # 系统浏览器兜底（最稳）
    import uvicorn  # ASGI 服务器，真正把 FastAPI 跑起来

    def open_page():  # 启动后自动打开页面
        time.sleep(1.5)  # 等服务先起来
        url = "http://127.0.0.1:8000/"  # 本机地址
        print(f"正在打开页面: {url}")  # 终端里提示一下

        # 方法1：尝试用 Cursor 内置 Simple Browser
        uri = "cursor://vscode.simple-browser/show?" + urllib.parse.urlencode({"url": url})
        try:
            subprocess.Popen(["cmd", "/c", "start", "", uri], shell=False)
        except Exception as e:
            print("Cursor 内置浏览器启动失败:", e)

        # 方法2：再尝试 cursor 命令行
        try:
            subprocess.Popen(["cursor", "-r", uri], shell=False)
        except Exception:
            pass

        # 方法3：兜底打开系统默认浏览器（保证你一定能看到页面）
        time.sleep(0.5)
        webbrowser.open(url)

    threading.Thread(target=open_page, daemon=True).start()  # 后台去打开页面
    uvicorn.run(app, host="0.0.0.0", port=8000)  # 启动服务：端口 8000
