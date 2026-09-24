# -*- coding: utf-8 -*-  # 声明源文件用 UTF-8 编码，避免中文注释乱码
"""项目：chroma文档管理综合案例（FastAPI 工程化）

原目录：semantic_search/
启动：python chroma文档管理/run.py
页面：http://127.0.0.1:8003/
"""  # 模块说明：本文件是项目启动入口
from __future__ import annotations  # 允许类型注解使用未定义的前向引用写法

import sys  # 修改模块搜索路径，保证能 import semantic_search
from pathlib import Path  # 用路径对象定位本文件所在目录

HERE = Path(__file__).resolve().parent  # 当前脚本目录：chroma文档管理/
if str(HERE) not in sys.path:  # 若该目录还不在 Python 搜索路径里
    sys.path.insert(0, str(HERE))  # 插到最前面，才能找到同级的 semantic_search 包

from semantic_search.__main__ import main  # 复用包内统一的 uvicorn 启动函数

if __name__ == "__main__":  # 仅在直接运行本文件时进入（被 import 时不启动服务）
    main()  # 启动 Native RAG 语义搜索 Web 服务
