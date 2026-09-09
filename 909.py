# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse, HTMLResponse
# from pathlib import Path
# import ollama
# import json

# app = FastAPI()

# client = ollama.Client(host="http://127.0.0.1:11434")

# # 本地 Ollama 模型名（和 ollama list 里显示的一致）
# MODEL_NAME = "deepseek-r1:1.5b"
# BASE_DIR = Path(__file__).resolve().parent  # 脚本所在目录，避免找不到 html

# # 访问静态页面
# @app.get("/", response_class=HTMLResponse)
# def index():
#     print("chat")
#     with open(BASE_DIR / "chat.html", encoding="utf-8") as f:
#         return f.read()

# # 对话  非流式输出
# @app.get("/chat")
# def chat(question: str):

#     print("用户传递的问题：",question)

#     response = client.chat(
#         model=MODEL_NAME,
#         messages=[
#             {"role":"user","content":question}
#         ]
#     )

#     result = response["message"]["content"]

#     print("模型的回复",result)

#     return result

# # 对话   流式输出
# @app.get("/stream_chat")
# def stream_chat(question: str):
#     response = client.chat(
#         model=MODEL_NAME,
#         messages=[
#             {"role": "user", "content": question}
#         ],
#         stream=True
#     )
#     # 生成流式输出
#     def generate():
#         for chunk in response:
#             content = chunk["message"]["content"]
#             #       data: {"content":"你好"}
#             yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
#         yield "data: [DONE]\n\n"

#     # 返回流式响应       通常前后端分离开发时服务端返回的是json  application/json
#     return StreamingResponse(generate(), media_type="text/event-stream")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.deepseek import DeepSeek
from dotenv import load_dotenv
from pathlib import Path
import os

# 固定读取脚本旁边的 .env，避免 IDE 工作目录不同导致密钥丢失
load_dotenv(Path(__file__).resolve().parent / ".env")

# 初始化云端 DeepSeek
llm = DeepSeek(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    timeout=120.0,
    context_window=8000,
)

# 1、定义一个 memory 对象，用于存储对话历史，并设置 token 限制为 10000
memory = ChatMemoryBuffer.from_defaults(token_limit=10000)

# 2、将系统提示词保存到 memory 中，设定 AI 的角色和行为
memory.put(ChatMessage(role="system", content="你是我的小苹果"))

# 打印查看当前 memory 中的第一条消息内容（即系统提示词）
print(memory.get()[0].blocks[0].text)

# 进入无限循环，实现多轮对话交互
while True:
    # 获取用户输入
    input_txt = input("请输入您的问题(exit退出)：")
    
    # 如果用户输入 "exit"，则退出循环
    if input_txt == "exit":
        print("bye，下次再见！")
        break
    
    # 创建用户消息对象
    user_msg = ChatMessage(role="user", content=input_txt)
    
    # 3、将用户的提问保存到 memory 中
    memory.put(user_msg)
    
    # 调用大模型进行流式聊天，传入完整的 memory 历史记录作为上下文
    res = llm.stream_chat(memory.get())
    
    ai_result = ""  # 用于累积 AI 的完整回复
    # 遍历流式返回的结果，逐块打印并累积结果
    for r in res:
        delta = r.delta or ""         # 个别数据块可能没有文本
        ai_result += delta            # 累积每一块的文本
        print(delta, end="", flush=True)  # 实时打印每一块文本

    print("\n", "=" * 100)  # 打印分隔线

    # 4、将 AI 的完整回复保存到 memory 中，以便后续对话使用
    memory.put(ChatMessage(role="assistant", content=ai_result))

    # 打印当前 memory 中存储的所有对话历史，用于调试或查看
    print("一轮对话完毕，看一下存储的内容：", memory.get())