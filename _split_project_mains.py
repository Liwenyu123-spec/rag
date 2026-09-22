# -*- coding: utf-8 -*-
"""从旧日期文件生成四个项目目录下的入口。"""
from __future__ import annotations

import re
from pathlib import Path

root = Path(__file__).resolve().parent

# ---------- 1) 基础聊天机器人 ----------
basic = (root / "908.py").read_text(encoding="utf-8")
basic = basic.replace(
    'load_dotenv(Path(__file__).resolve().parent / ".env")',
    'BASE_DIR = Path(__file__).resolve().parent\n'
    'REPO_ROOT = BASE_DIR.parent\n'
    'load_dotenv(REPO_ROOT / ".env")\n'
    'load_dotenv(BASE_DIR / ".env")',
)
basic = basic.replace(
    'with open("index.html", encoding="utf-8") as f:',
    'with open(BASE_DIR / "index.html", encoding="utf-8") as f:',
)
basic = basic.replace(
    'with open("index2.html", encoding="utf-8") as f:',
    'with open(BASE_DIR / "index2.html", encoding="utf-8") as f:',
)
basic = (
    '"""项目：基础聊天机器人\\n\\n'
    '原文件：908.py。云端 DeepSeek + FastAPI 流式多轮聊天。\\n'
    '启动：python 基础聊天机器人/main.py\\n'
    '页面：http://127.0.0.1:8000/\\n'
    '"""\n'
    + basic
)
(root / "基础聊天机器人" / "main.py").write_text(basic, encoding="utf-8")
print("wrote 基础聊天机器人/main.py")

# ---------- 2) 带安全校验的聊天机器人（去掉文案接口） ----------
src910 = (root / "910.py").read_text(encoding="utf-8")
# 改文档头
src910 = re.sub(
    r'^""".*?"""',
    '"""项目：带安全校验的聊天机器人\\n\\n'
    '原文件：910.py（安全聊天部分）。\\n'
    '含：输入净化、强化 system、零样本/少样本/COT/ToT、多轮流式对话。\\n'
    '启动：python 带安全校验的聊天机器人/main.py\\n'
    '页面：http://127.0.0.1:8001/\\n'
    '"""',
    src910,
    count=1,
    flags=re.S,
)
src910 = src910.replace(
    'FRONTEND_DIST = BASE_DIR / "frontend" / "dist"',
    'REPO_ROOT = BASE_DIR.parent\n'
    'FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"',
)
src910 = src910.replace(
    'load_dotenv(BASE_DIR / ".env", override=True)',
    'load_dotenv(REPO_ROOT / ".env", override=True)\n'
    'load_dotenv(BASE_DIR / ".env", override=True)',
)
src910 = src910.replace(
    'app = FastAPI(title="DeepSeek 提示词策略 + 安全防护")',
    'app = FastAPI(title="带安全校验的聊天机器人")',
)
src910 = src910.replace(
    'page = BASE_DIR / "chat_910.html"',
    'page = BASE_DIR / "chat.html"',
)
# 删掉文案相关大段：从 self_consistency 到文件末尾的 if __name__ 之前，保留 if __name__
# 更稳妥：从 "# ---------- demo02" 删到 "# ---------- demo06" 之后的 compare/tool 也属于综合？
# 用户表格：安全校验聊天 vs 文案综合。所以安全项目保留 chat/stream/modes/system/sanitize。
# 文案项目保留 product_copy/social/self_consistency/compare。

cut_start = src910.find("# ---------- demo02：自我一致性")
if_main = src910.find('\nif __name__ == "__main__":')
if cut_start != -1 and if_main != -1:
    src910 = src910[:cut_start] + src910[if_main:]
src910 = src910.replace(
    'threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8001")).start()\n'
    '    # 用 8001，避免和正在运行的 909_fastapi.py(8000) 冲突\n'
    '    uvicorn.run(app, host="127.0.0.1", port=8001)',
    'threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8001")).start()\n'
    '    uvicorn.run(app, host="127.0.0.1", port=8001)',
)
(root / "带安全校验的聊天机器人" / "main.py").write_text(src910, encoding="utf-8")
print("wrote 带安全校验的聊天机器人/main.py")

# ---------- 3) 社交媒体文案和电商内容生成 ----------
full910 = (root / "910.py").read_text(encoding="utf-8")
# 提取公共头 + 净化函数 + 文案接口
# 简化：基于 910，去掉 chat 流式多轮记忆相关的前端 SPA，保留文案 API + 简易页

content_head = '''"""项目：社交媒体文案和电商内容生成综合案例

原文件：910.py（文案部分）。
含：电商产品描述、社交媒体 ToT 策划、自我一致性口号评选。
启动：python 社交媒体文案和电商内容生成/main.py
页面：http://127.0.0.1:8002/
"""

import json
import os
import re
import threading
import webbrowser
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from llama_index.core.llms import ChatMessage
from llama_index.llms.deepseek import DeepSeek
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
load_dotenv(REPO_ROOT / ".env", override=True)
load_dotenv(BASE_DIR / ".env", override=True)

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("没有找到 DEEPSEEK_API_KEY，请检查项目目录下的 .env")

app = FastAPI(title="社交媒体文案和电商内容生成")

llm = DeepSeek(
    model="deepseek-v4-flash",
    api_key=api_key,
    timeout=120.0,
    context_window=8000,
)

SAFE_REJECT_REPLY = "非常抱歉，我目前无法回答这个问题。"


def moderation_input(user_input: str):
    """简易输入净化（复用原 910 思路）。"""
    patterns = [
        r"ignore\\s+(all\\s+)?(previous|above|prior)\\s+(instructions?|prompts?|rules?)",
        r"jailbreak",
        r"DAN\\s+mode",
        r"override\\s+(system|previous)\\s+(prompt|instructions)",
        r"(you\\s+are|act\\s+as|pretend\\s+to\\s+be)\\s+(system|developer|admin|administrator)",
        r"system:\\s*",
        r"print\\s+(the|your)\\s+(system|prompt|instructions)",
        r"show\\s+(me|your)\\s+(system|prompt|instructions|rules)",
        r"reveal\\s+(your|the)\\s+(system|prompt|instructions)",
    ]
    text = user_input or ""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return None
    sanitized = re.sub(r"[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f]", "", text)
    if re.search(r"(.)\\1{50,}", sanitized):
        return None
    return sanitized


def gate_user_input(user_input: str) -> tuple[str | None, str | None]:
    cleaned = moderation_input(user_input)
    if cleaned is None:
        return None, SAFE_REJECT_REPLY
    return cleaned, None


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>文案生成综合案例</title>
  <style>
    body{font-family:Microsoft YaHei,sans-serif;max-width:860px;margin:32px auto;padding:0 16px;color:#0f172a}
    h1{font-size:22px} section{border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin:16px 0}
    label{display:block;margin:8px 0 4px;font-size:14px;color:#475569}
    input,textarea{width:100%;box-sizing:border-box;padding:8px 10px;border:1px solid #cbd5e1;border-radius:8px}
    button{margin-top:12px;padding:8px 14px;border:0;border-radius:8px;background:#0f172a;color:#fff;cursor:pointer}
    pre{white-space:pre-wrap;background:#f8fafc;padding:12px;border-radius:8px;min-height:80px}
  </style>
</head>
<body>
  <h1>社交媒体文案和电商内容生成</h1>
  <section>
    <h2>电商产品描述</h2>
    <label>产品名称</label><input id="name" value="无线降噪耳机"/>
    <label>核心卖点</label><input id="features" value="40dB深度降噪, 30小时续航"/>
    <label>目标人群</label><input id="audience" value="通勤上班族"/>
    <button onclick="genProduct()">生成文案</button>
    <pre id="productOut">结果会显示在这里</pre>
  </section>
  <section>
    <h2>社交媒体策划（ToT）</h2>
    <label>主题</label><input id="topic" value="夏季减肥"/>
    <button onclick="genSocial()">生成策划</button>
    <pre id="socialOut">结果会显示在这里（较慢）</pre>
  </section>
  <section>
    <h2>自我一致性口号</h2>
    <label>任务</label><input id="slogan" value="为户外运动鞋写一句广告口号"/>
    <button onclick="genSlogan()">评选口号</button>
    <pre id="sloganOut">结果会显示在这里</pre>
  </section>
<script>
async function genProduct(){
  const body={name:name.value,features:features.value,audience:audience.value};
  productOut.textContent='生成中...';
  const r=await fetch('/product_copy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const j=await r.json(); productOut.textContent=j.result||JSON.stringify(j,null,2);
}
async function genSocial(){
  socialOut.textContent='生成中，可能需要几十秒...';
  const r=await fetch('/social_plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:topic.value})});
  const j=await r.json();
  socialOut.textContent=[j.ideas,j.evaluation,j.plan].filter(Boolean).join('\\n\\n——\\n\\n')||JSON.stringify(j,null,2);
}
async function genSlogan(){
  sloganOut.textContent='生成中...';
  const r=await fetch('/self_consistency?question='+encodeURIComponent(slogan.value)+'&num=2');
  const j=await r.json();
  sloganOut.textContent='候选:\\n'+(j.candidates||[]).map((c,i)=>`${i+1}. ${c}`).join('\\n')+'\\n\\n最佳: '+(j.final||'');
}
</script>
</body></html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


@app.get("/health")
def health():
    return {"ok": True, "project": "社交媒体文案和电商内容生成", "model": "deepseek-v4-flash"}

'''

# 从 910 截取文案相关函数体（从 demo02 到 compare 之前或 social_plan_stream 结束）
m = re.search(
    r"(# ---------- demo02：自我一致性.*?)(?=\n# ---------- demo0[0-9]|\n@app\.(get|post)\(\"/compare|\nif __name__)",
    full910,
    flags=re.S,
)
# 更简单：从 demo02 到 if __name__
start = full910.find("# ---------- demo02：自我一致性")
end = full910.find('\nif __name__ == "__main__":')
body = full910[start:end] if start != -1 and end != -1 else ""

# 去掉 compare / tool_chat 等偏安全聊天的大 demo（若存在）
for marker in [
    '\n# ---------- demo07',
    '\n@app.post("/compare',
    '\n@app.get("/compare',
    '\n@app.post("/tool_chat',
    '\n@app.get("/tool_chat',
]:
    idx = body.find(marker)
    if idx != -1:
        body = body[:idx]
        break

content_tail = '''

if __name__ == "__main__":
    import uvicorn

    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8002")).start()
    uvicorn.run(app, host="127.0.0.1", port=8002)
'''

(root / "社交媒体文案和电商内容生成" / "main.py").write_text(
    content_head + "\n" + body + content_tail, encoding="utf-8"
)
print("wrote 社交媒体文案和电商内容生成/main.py")

# ---------- 4) chroma 启动器 + 根目录兼容入口 ----------
run_py = '''# -*- coding: utf-8 -*-
"""项目：chroma文档管理综合案例（FastAPI 工程化）

原目录：semantic_search/
启动：python chroma文档管理/run.py
页面：http://127.0.0.1:8001/
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from semantic_search.__main__ import main

if __name__ == "__main__":
    main()
'''
(root / "chroma文档管理" / "run.py").write_text(run_py, encoding="utf-8")
print("wrote chroma文档管理/run.py")

# 根目录兼容：旧命令 python -m semantic_search / python 908.py 等
shim_pkg = root / "semantic_search"
shim_pkg.mkdir(exist_ok=True)
(shim_pkg / "__init__.py").write_text(
    '"""兼容入口：真实代码在 chroma文档管理/semantic_search。"""\n',
    encoding="utf-8",
)
(shim_pkg / "__main__.py").write_text(
    '''# -*- coding: utf-8 -*-
"""兼容：python -m semantic_search → 跳转到 chroma文档管理。"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "chroma文档管理"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# 清掉当前这个空壳包，改用项目目录里的真包
sys.modules.pop("semantic_search", None)
sys.modules.pop("semantic_search.__main__", None)

runpy.run_module("semantic_search.__main__", run_name="__main__")
''',
    encoding="utf-8",
)
print("wrote root semantic_search shim")

# 旧文件改成跳转提示
redirects = {
    "908.py": ("基础聊天机器人", "main.py", 8000),
    "910.py": ("带安全校验的聊天机器人", "main.py", 8001),
}
for old, (folder, entry, port) in redirects.items():
    (root / old).write_text(
        f'''# -*- coding: utf-8 -*-
"""已迁移到「{folder}/{entry}」。本文件仅作兼容跳转。"""
from pathlib import Path
import runpy

target = Path(__file__).resolve().parent / "{folder}" / "{entry}"
print(f"提示：请改用 python {folder}/{entry}  （端口 {port}）")
runpy.run_path(str(target), run_name="__main__")
''',
        encoding="utf-8",
    )
    print("rewrote shim", old)

readme = root / "基础聊天机器人" / "README.md"
readme.write_text(
    "# 基础聊天机器人\n\n```powershell\npython 基础聊天机器人/main.py\n```\n\n打开 http://127.0.0.1:8000/\n",
    encoding="utf-8",
)
(root / "带安全校验的聊天机器人" / "README.md").write_text(
    "# 带安全校验的聊天机器人\n\n```powershell\npython 带安全校验的聊天机器人/main.py\n```\n\n打开 http://127.0.0.1:8001/\n\n前端工程仍在仓库根目录 `frontend/`（`npm run build` 后由本服务托管）。\n",
    encoding="utf-8",
)
(root / "社交媒体文案和电商内容生成" / "README.md").write_text(
    "# 社交媒体文案和电商内容生成综合案例\n\n```powershell\npython 社交媒体文案和电商内容生成/main.py\n```\n\n打开 http://127.0.0.1:8002/\n",
    encoding="utf-8",
)
(root / "chroma文档管理" / "README.md").write_text(
    "# chroma文档管理综合案例（FastAPI 工程化）\n\n```powershell\npython chroma文档管理/run.py\n# 或（兼容旧命令）\npython -m semantic_search\n```\n\n打开 http://127.0.0.1:8001/\n\n代码在 `chroma文档管理/semantic_search/`。\n",
    encoding="utf-8",
)
print("done")
