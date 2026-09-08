
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




import ollama
from fastapi import FastAPI
import requests
app = FastAPI()

@app.get("/deepseek-v4-flash")
def deepseek_v4_flash(prompt: str):
    print("接收到的问题是：", prompt)
    response = requests.post("http://localhost:11434/v1/chat/completions", json={
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": prompt}]
    })
    return response.json()

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
        










