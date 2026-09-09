"""云端 DeepSeek 多轮对话的 FastAPI 版本；原 909.py 保持不变。"""  # 文件功能说明

import json  # 把 Python 字典转换成发送给网页的 JSON 字符串
import os  # 读取 Windows 环境变量
import threading  # 创建延时任务，在服务器启动后自动打开网页
import webbrowser  # 调用电脑的默认浏览器
from pathlib import Path  # 安全地拼接和处理文件路径

from dotenv import load_dotenv  # 从项目的 .env 文件加载环境变量
from fastapi import FastAPI  # 导入 FastAPI Web 框架
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse  # 导入三种响应类型
from llama_index.core.llms import ChatMessage  # 表示一条 system、user 或 assistant 消息
from llama_index.core.memory import ChatMemoryBuffer  # 保存多轮对话历史
from llama_index.llms.deepseek import DeepSeek  # LlamaIndex 提供的 DeepSeek 客户端


BASE_DIR = Path(__file__).resolve().parent  # 获取当前 Python 文件所在的绝对目录
load_dotenv(BASE_DIR / ".env")  # 固定读取当前目录下的 .env，避免受运行目录影响

api_key = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量中取得 DeepSeek API Key
if not api_key:  # 如果没有读取到 API Key
    raise RuntimeError("没有找到 DEEPSEEK_API_KEY，请检查项目目录下的 .env")  # 立即停止并提示原因

app = FastAPI(title="DeepSeek 多轮对话")  # 创建 FastAPI 应用，title 会显示在 /docs 页面

llm = DeepSeek(  # 创建云端 DeepSeek 大模型客户端
    model="deepseek-v4-flash",  # 指定要调用的云端模型名称
    api_key=api_key,  # 把读取到的 API Key 交给客户端进行身份验证
    timeout=120.0,  # 最长等待模型回复 120 秒
    context_window=8000,  # 告诉 LlamaIndex 按 8000 token 的上下文窗口管理消息
)  # DeepSeek 客户端初始化结束

memory = ChatMemoryBuffer.from_defaults(token_limit=10000)  # 创建最多保存约 10000 token 的对话记忆
memory.put(ChatMessage(role="system", content="你是我的小苹果"))  # 写入系统提示词，设定 AI 的角色


@app.get("/", response_class=HTMLResponse)  # 浏览器访问根网址时执行下面的 index 函数
def index():  # 定义返回聊天网页的接口函数
    """返回现有聊天页面。"""  # 接口说明，会显示在 FastAPI 文档中
    return (BASE_DIR / "chat.html").read_text(encoding="utf-8")  # 读取并返回同目录的聊天网页


@app.get("/chat", response_class=PlainTextResponse)  # 注册普通非流式 GET 接口
def chat(question: str):  # question 是网址查询参数，例如 /chat?question=你好
    """普通非流式多轮对话。"""  # 接口说明，会显示在 /docs 中
    memory.put(ChatMessage(role="user", content=question))  # 把本次用户问题加入对话记忆
    response = llm.chat(memory.get())  # 把完整对话历史发给 DeepSeek，并等待完整回复
    answer = response.message.content or ""  # 提取回复正文；没有正文时使用空字符串
    memory.put(ChatMessage(role="assistant", content=answer))  # 把 AI 回复加入记忆供下一轮使用
    return answer  # 将完整文本一次性返回给网页


@app.get("/stream_chat")  # 注册流式 GET 接口，网页会逐段显示模型回复
def stream_chat(question: str):  # 接收网址中的 question 查询参数
    """以 SSE 格式流式返回多轮对话结果。"""  # 接口说明
    memory.put(ChatMessage(role="user", content=question))  # 先把用户问题保存到对话记忆
    response = llm.stream_chat(memory.get())  # 携带完整历史发起流式模型请求

    def generate():  # 定义生成器，FastAPI 会将每次 yield 的内容立即发给网页
        answer = ""  # 用来拼接 AI 的完整回答，方便最后写入记忆
        for chunk in response:  # 逐个读取模型返回的数据块
            delta = chunk.delta or ""  # 取得当前新增文本；空值时使用空字符串
            answer += delta  # 将当前文本块累加到完整回答中
            data = json.dumps({"content": delta}, ensure_ascii=False)  # 转成 JSON 并保留中文
            yield f"data: {data}\n\n"  # 按 SSE 协议格式将当前文本块发送给网页

        memory.put(ChatMessage(role="assistant", content=answer))  # 流式输出结束后保存完整 AI 回复
        yield "data: [DONE]\n\n"  # 通知网页本次流式回答已经结束

    return StreamingResponse(  # 创建支持持续发送数据的流式响应
        generate(),  # 将上面的生成器作为响应内容
        media_type="text/event-stream",  # 声明数据格式为 SSE
        headers={"Cache-Control": "no-cache"},  # 禁止缓存，避免流式内容被浏览器延迟
    )  # 返回流式响应对象


if __name__ == "__main__":  # 只有直接运行此文件时才启动服务器
    import uvicorn  # 导入运行 FastAPI 所需的 ASGI 服务器

    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8000")).start()  # 1.5 秒后打开网页
    uvicorn.run(app, host="127.0.0.1", port=8000)  # 在本机 8000 端口启动 FastAPI 服务
