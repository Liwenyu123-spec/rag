# -*- coding: utf-8 -*-
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
