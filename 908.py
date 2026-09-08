
# # import os
# # from openai import OpenAI



# # client = OpenAI(
# #     api_key=os.getenv("DEEPSEEK_API_KEY"),
# #     base_url="https://api.deepseek.com"
# # )

# # response = client.chat.completions.create(
# #     model="deepseek-v4-flash",
# #     messages=[
# #         {"role":"user","content":"你是谁？"}
# #     ]
# # )
# # print(response.choices[0].message.content)





# from fastapi import FastAPI
# import os
# import requests

# app = FastAPI()


# @app.get("/")
# def home():
#     return {
#         "用法": "打开 http://127.0.0.1:8000/docs 点接口测试，最简单",
#         "示例": "http://127.0.0.1:8000/deepseek-v4-flash?prompt=你是谁",
#         "文档": "http://127.0.0.1:8000/docs",
#     }


# @app.get("/deepseek-v4-flash")
# def deepseek_v4_flash(prompt: str):
#     print("接收到的问题是：", prompt)
#     response = requests.post(
#         "https://api.deepseek.com/v1/chat/completions",
#         headers={
#             "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
#             "Content-Type": "application/json",
#         },
#         json={
#             "model": "deepseek-v4-flash",
#             "messages": [{"role": "user", "content": prompt}],
#         },
#     )
#     return response.json()


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from openai import OpenAI
import os
import json

app = FastAPI()

# 云端 DeepSeek（OpenAI 兼容接口）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


@app.get("/", response_class=HTMLResponse)
def index():
    print("index")
    with open("index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/page", response_class=HTMLResponse)
def page():
    print("page")
    with open("index2.html", encoding="utf-8") as f:
        return f.read()


@app.get("/chat")
def chat(q: str):
    stream = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": q}],
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
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)





def chat_with_ai(prompt):
    """通义千问对话函数"""
    msg = {
        "role": Role.SYSTEM, "content": prompt
    }
    messages.append(msg)
    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=messages,
            temperature=0.1 # 创造性，值越高它的发散力越大，值越低就越文中
        )
        return response.output.text
    except Exception as e:
        return f"出错啦！异常信息为：{e}"

def main():
    while True:
        content = input("你好，我是千问，你说出你的问题：")
        print(chat_with_ai(content))
        if input("是否结束：Y or N").upper() == "Y":
            print("程序结束！")
            break
main()