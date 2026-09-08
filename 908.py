#  openai 连接大模型  api_key  配置环境变量  OPENAI_API_KEY
#                   base_url  模型地址
#                   model  模型名称
#                   messages  消息列表   (system[系统角色],user[用户提问],assistant[模型回复])



import os
from openai import OpenAI

# print(os.getenv("OPENAI_API_KEY"))

client = OpenAI(
    # api_key="sk-ws-H.PDHHERR.lgQO.MEQCIGET36rc1phtq9Suq-3asbT4JvjOT_EX_alcyS9p9nZOAiBAwf3gg1zYmIUhW-jzKW07VAYNAbc288iBG5v2JNVcjQ",
    # api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen3.8-27b",
    messages=[
        {"role":"system","content":"你是一个经验丰富的中学数学老师"},
        {"role":"user","content":"请用通俗的语言解释一下高等数学的基本概念"}
    ]
)
print(response.choices[0].message.content)
