"""使用本地 Ollama 的多轮流式对话版本。"""

from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama

# 初始化本地模型：不需要 API Key，也不消耗 DeepSeek 云端额度
llm = Ollama(
    model="deepseek-r1:1.5b",
    base_url="http://127.0.0.1:11434",
    request_timeout=120.0,
    context_window=8000,
)

# 保存多轮对话历史
memory = ChatMemoryBuffer.from_defaults(token_limit=10000)
memory.put(ChatMessage(role="system", content="你是我的小苹果"))

print(memory.get()[0].blocks[0].text)

while True:
    input_txt = input("请输入您的问题(exit退出)：")

    if input_txt == "exit":
        print("bye，下次再见！")
        break

    # 保存用户消息
    memory.put(ChatMessage(role="user", content=input_txt))

    # 携带完整历史调用本地模型
    response = llm.stream_chat(memory.get())

    ai_result = ""
    for chunk in response:
        delta = chunk.delta or ""
        ai_result += delta
        print(delta, end="", flush=True)

    print("\n", "=" * 100)

    # 保存 AI 回复，供下一轮使用
    memory.put(ChatMessage(role="assistant", content=ai_result))
    print("一轮对话完毕，看一下存储的内容：", memory.get())
