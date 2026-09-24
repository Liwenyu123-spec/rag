# -*- coding: utf-8 -*-
"""RAG 四合一综合平台（单体）启动入口。

一个进程、一个端口、一个页面，左侧切换四个功能：
1. 基础聊天
2. 安全校验聊天
3. 文案 / 电商内容
4. 知识库 RAG

启动：
  python RAG四合一平台/run.py

页面：
  http://127.0.0.1:8100/
"""
from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

PLATFORM_ROOT = Path(__file__).resolve().parent
if str(PLATFORM_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_ROOT))

from app.config import HOST, PORT  # noqa: E402


def main() -> None:
    import os

    os.chdir(PLATFORM_ROOT)

    def _open():
        time.sleep(2.0)
        webbrowser.open(f"http://{HOST}:{PORT}/")

    threading.Thread(target=_open, daemon=True).start()
    print("=" * 56)
    print("RAG 四合一综合平台（单体）")
    print(f"打开: http://{HOST}:{PORT}/")
    print("左侧切换：基础聊天 / 安全聊天 / 文案 / 知识库RAG")
    print("原四个项目目录未被覆盖。")
    print("=" * 56)
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
