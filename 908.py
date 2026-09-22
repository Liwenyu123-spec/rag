# -*- coding: utf-8 -*-
"""已迁移到「基础聊天机器人/main.py」。本文件仅作兼容跳转。"""
from pathlib import Path
import runpy

target = Path(__file__).resolve().parent / "基础聊天机器人" / "main.py"
print(f"提示：请改用 python 基础聊天机器人/main.py  （端口 8000）")
runpy.run_path(str(target), run_name="__main__")
