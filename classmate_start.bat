@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   同学一键启动（本地网页，不被 Chrome 拦截）
echo ========================================
echo.

where ollama >nul 2>nul
if errorlevel 1 (
  echo [!] 未检测到 Ollama。请先安装: https://ollama.com/download
  echo     安装后打开 Ollama，再重新运行本脚本。
  pause
  exit /b 1
)

curl -s http://127.0.0.1:11434/api/tags >nul 2>nul
if errorlevel 1 (
  echo [!] Ollama 未在运行，请先打开 Ollama 托盘应用。
  pause
  exit /b 1
)

echo [1/3] 安装 Python 依赖...
python -m pip install -r requirements-ollama.txt -q
if errorlevel 1 (
  echo 依赖安装失败，请确认已安装 Python 3.10+ 并加入 PATH。
  pause
  exit /b 1
)

if not exist "frontend\dist\index.html" (
  echo [2/3] 缺少 frontend\dist，请先从 GitHub Release 下载完整压缩包。
  echo       https://github.com/Liwenyu123-spec/rag/releases
  pause
  exit /b 1
) else (
  echo [2/3] 前端已就绪。
)

echo [3/3] 启动本地服务 http://127.0.0.1:8002
echo       用自己的 Ollama 模型，右上角可切换。
echo.
python 910_ollama.py
pause
