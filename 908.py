
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










