# -*- coding: utf-8 -*-
"""RAG 四合一综合平台启动入口（另存副本，不覆盖原四个项目）。

包含：
1. 基础聊天机器人          → http://127.0.0.1:8000/
2. 带安全校验的聊天机器人  → http://127.0.0.1:8001/
3. 社交媒体文案和电商内容  → http://127.0.0.1:8002/
4. chroma文档管理 / RAG    → http://127.0.0.1:8003/
5. 统一门户               → http://127.0.0.1:8100/

启动：
  python RAG四合一平台/run.py
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

PLATFORM_ROOT = Path(__file__).resolve().parent
APPS = PLATFORM_ROOT / "apps"
PORTAL_HTML = PLATFORM_ROOT / "portal" / "index.html"
PY = sys.executable

# 子服务定义：标题、端口、启动命令（在副本目录内）
SERVICES = [
    {
        "name": "基础聊天机器人",
        "port": 8000,
        "cwd": APPS / "基础聊天机器人",
        "args": [PY, "main.py"],
    },
    {
        "name": "带安全校验的聊天机器人",
        "port": 8001,
        "cwd": APPS / "带安全校验的聊天机器人",
        "args": [PY, "main.py"],
    },
    {
        "name": "社交媒体文案和电商内容生成",
        "port": 8002,
        "cwd": APPS / "社交媒体文案和电商内容生成",
        "args": [PY, "main.py"],
    },
    {
        "name": "chroma文档管理",
        "port": 8003,
        "cwd": APPS / "chroma文档管理",
        "args": [PY, "run.py"],
    },
]


def _spawn(svc: dict) -> subprocess.Popen:
    """后台启动一个子项目进程。"""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    # 避免子进程再弹多个浏览器（门户统一打开）
    env["RAG_PLATFORM_NO_BROWSER"] = "1"
    print(f"[启动] {svc['name']} → http://127.0.0.1:{svc['port']}/")
    return subprocess.Popen(
        svc["args"],
        cwd=str(svc["cwd"]),
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def build_portal_app() -> FastAPI:
    """仅提供统一门户首页。"""
    app = FastAPI(title="RAG 四合一综合平台门户")

    @app.get("/")
    def index():
        return FileResponse(PORTAL_HTML)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "rag-quad-portal", "port": 8100}

    return app


def main() -> None:
    missing = [s for s in SERVICES if not (s["cwd"] / s["args"][-1]).exists() and not (s["cwd"] / Path(s["args"][-1]).name).exists()]
    # run.py / main.py 存在性检查
    for s in SERVICES:
        script = s["cwd"] / s["args"][-1]
        if not script.is_file():
            raise FileNotFoundError(f"缺少子项目入口：{script}")

    if not PORTAL_HTML.is_file():
        raise FileNotFoundError(f"缺少门户页面：{PORTAL_HTML}")

    procs: list[subprocess.Popen] = []
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # 便于整体结束进程树

    for svc in SERVICES:
        print(f"[启动] {svc['name']} → http://127.0.0.1:{svc['port']}/")
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["RAG_PLATFORM_NO_BROWSER"] = "1"
        procs.append(
            subprocess.Popen(
                svc["args"],
                cwd=str(svc["cwd"]),
                env=env,
                stdout=sys.stdout,
                stderr=sys.stderr,
                creationflags=creationflags,
            )
        )
        time.sleep(0.8)

    portal = build_portal_app()

    def _open_browser():
        time.sleep(2.5)
        webbrowser.open("http://127.0.0.1:8100/")

    threading.Thread(target=_open_browser, daemon=True).start()

    print("=" * 56)
    print("RAG 四合一综合平台")
    print("门户: http://127.0.0.1:8100/")
    print("子服务: 8000 / 8001 / 8002 / 8003")
    print("原四个项目目录未被修改；本目录为另存副本。")
    print("=" * 56)

    try:
        uvicorn.run(portal, host="127.0.0.1", port=8100, log_level="info")
    finally:
        print("正在关闭子服务...")
        for p in procs:
            if p.poll() is None:
                if os.name == "nt":
                    p.send_signal(signal.CTRL_BREAK_EVENT) if hasattr(signal, "CTRL_BREAK_EVENT") else p.terminate()
                else:
                    p.terminate()
        for p in procs:
            try:
                p.wait(timeout=8)
            except Exception:
                p.kill()


if __name__ == "__main__":
    main()
