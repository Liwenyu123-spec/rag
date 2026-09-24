# v1.1.2 Windows 安装包启动即崩溃：`Unable to configure formatter 'default'`

安装 [v1.1.2](https://github.com/aaGlaming/My-Owned-RAG/releases/tag/v1.1.2) 后打开「My RAG 知识库」，立刻弹出未处理异常。源码直接 `python run.py` 正常，只有安装包会炸。当前 `main` 分支也还没修。

## 现象

```
Unhandled exception in script
Failed to execute script 'run' due to unhandled exception:
Unable to configure formatter 'default'

File "run.py", line 38, in <module>
File "logging\config.py", line 560, in configure
File "logging\config.py", line 672, in configure_formatter
File "logging\config.py", line 490, in configure_custom
File "uvicorn\logging.py", line 42, in __init__
AttributeError: 'NoneType' object has no attribute 'isatty'
```

## 原因

桌面壳（Tauri）会拉起 PyInstaller 打出来的 `my_rag_backend.exe`。

`backend/my_rag_backend.spec` 里是 `console=False`。PyInstaller 无控制台模式下 `sys.stdout` / `sys.stderr` 为 `None`（和 `pythonw.exe` 一样）。Tauri 那边还有 `CREATE_NO_WINDOW`，被壳拉起时同样没有 TTY。

项目使用的 `uvicorn==0.52.4` 在初始化默认 formatter 时直接调用：

```python
self.use_colors = sys.stdout.isatty()
```

没有判断 `stdout is None`，所以一进 `uvicorn.run()` 就崩。这是打包问题，不是使用者环境问题。

v1.1.2 修了「安装后找不到 `my_rag_backend.exe`」，但 exe 起来就会撞这个。

`console=False` 建议保留，GUI 不该再弹黑框。在入口把空的 stdout/stderr 补上即可。

## 补丁

只改 `backend/run.py`：在 import uvicorn **之前** 补上空流，并给 `uvicorn.run(..., use_colors=False)`。

`backend/my_rag_backend.spec` 的 `console=False`、Tauri 的 `CREATE_NO_WINDOW` 都不用动。

完整替换 `backend/run.py` 如下：

```python
"""桌面应用 / 独立后端入口：启动 FastAPI。

由 Tauri 拉起时设置 MYRAG_EMBEDDED=1，不再额外打开浏览器。
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path

# PyInstaller noconsole / pythonw / Tauri CREATE_NO_WINDOW 下 stdout/stderr 为 None。
# uvicorn.logging.ColourizedFormatter 会调用 sys.stdout.isatty()，不补会直接崩溃。
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8", errors="replace")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8", errors="replace")

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR))

import uvicorn  # noqa: E402


def open_browser() -> None:
    import time

    time.sleep(2)
    webbrowser.open("http://127.0.0.1:18932")


if __name__ == "__main__":
    embedded = os.environ.get("MYRAG_EMBEDDED") == "1"
    if not embedded:
        threading.Thread(target=open_browser, daemon=True).start()

    print("=" * 50)
    print(" My RAG 知识库")
    print(" 访问地址: http://127.0.0.1:18932")
    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=18932,
        log_level="info",
        use_colors=False,
    )
```

## 验证

```powershell
.\scripts\pack-windows.ps1
```

装新包后打开应用，确认：

- 不再弹出 `Unable to configure formatter 'default'`
- 后端能监听 `127.0.0.1:18932`
- 主窗口能打开知识库界面

修完请发 **v1.1.3**。现在这份安装包使用者装完是打不开的。
