# -*- coding: utf-8 -*-
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
