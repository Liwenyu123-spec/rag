# -*- coding: utf-8 -*-
"""一次性：把四个项目按中文名拆到独立目录。"""
from __future__ import annotations

import shutil
from pathlib import Path

root = Path(__file__).resolve().parent

WANTED = [
    "基础聊天机器人",
    "带安全校验的聊天机器人",
    "社交媒体文案和电商内容生成",
    "chroma文档管理",
]
SKIP = {
    ".git",
    ".github",
    ".cursor",
    ".idea",
    ".vscode",
    "frontend",
    "xmind",
    "chroma_data",
    "__pycache__",
}

# 1) 从乱码目录里救回 semantic_search
for p in list(root.iterdir()):
    if not p.is_dir() or p.name in SKIP or p.name in WANTED:
        continue
    nested = p / "semantic_search"
    if nested.is_dir() and not (root / "semantic_search").exists():
        shutil.move(str(nested), str(root / "semantic_search"))
        print("restored semantic_search from", repr(p.name))

# 2) 删除之前建错编码的空/半空项目目录
for p in list(root.iterdir()):
    if not p.is_dir() or p.name in SKIP or p.name in WANTED:
        continue
    kids = {c.name for c in p.iterdir()} if p.exists() else set()
    markers = {"index.html", "index2.html", "chat.html", "semantic_search"}
    if kids <= markers:
        print("removing garbled", repr(p.name))
        shutil.rmtree(p, ignore_errors=True)

# 3) 用正确 Unicode 建目录
for name in WANTED:
    (root / name).mkdir(exist_ok=True)
    print("mkdir", repr(name))

# 4) 迁入 chroma
src = root / "semantic_search"
dst = root / "chroma文档管理" / "semantic_search"
if src.exists() and not dst.exists():
    shutil.move(str(src), str(dst))
    print("moved semantic_search")
elif dst.exists():
    print("chroma already has semantic_search")
else:
    print("WARNING: semantic_search missing")

# 5) 复制前端静态页
shutil.copy2(root / "index.html", root / "基础聊天机器人" / "index.html")
shutil.copy2(root / "index2.html", root / "基础聊天机器人" / "index2.html")
shutil.copy2(root / "chat_910.html", root / "带安全校验的聊天机器人" / "chat.html")
print("copied html")

for name in WANTED:
    p = root / name
    print("OK", repr(name), [c.name for c in p.iterdir()])
