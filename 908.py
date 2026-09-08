
# import os
# from openai import OpenAI



# client = OpenAI(
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     base_url="https://api.deepseek.com"
# )

# response = client.chat.completions.create(
#     model="deepseek-v4-flash",
#     messages=[
#         {"role":"user","content":"你是谁？"}
#     ]
# )
# print(response.choices[0].message.content)





from fastapi import FastAPI
import os
import requests

app = FastAPI()


@app.get("/")
def home():
    return {
        "用法": "打开 http://127.0.0.1:8000/docs 点接口测试，最简单",
        "示例": "http://127.0.0.1:8000/deepseek-v4-flash?prompt=你是谁",
        "文档": "http://127.0.0.1:8000/docs",
    }


@app.get("/deepseek-v4-flash")
def deepseek_v4_flash(prompt: str):
    print("接收到的问题是：", prompt)
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)








