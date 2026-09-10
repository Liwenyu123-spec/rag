@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   启动本地 Ollama 聊天助手
echo ========================================
echo.

where ollama >nul 2>nul
if errorlevel 1 (
  echo [提示] 未检测到 ollama 命令。请先安装: https://ollama.com/download
  echo        安装后打开 Ollama，再重新运行本脚本。
  echo.
) else (
  echo [1/4] 检查 Ollama 服务...
  curl -s http://127.0.0.1:11434/api/tags >nul 2>nul
  if errorlevel 1 (
    echo       连不上 11434，请先打开 Ollama 应用。
  ) else (
    echo       Ollama 已在运行。
  )
)

echo [2/4] 安装 Python 依赖...
python -m pip install -r requirements-ollama.txt -q
if errorlevel 1 (
  echo 依赖安装失败，请确认已安装 Python 3.10+ 并加入 PATH。
  pause
  exit /b 1
)

if not exist "frontend\dist\index.html" (
  echo [3/4] 构建前端...
  where npm >nul 2>nul
  if errorlevel 1 (
    echo 未找到 npm，且没有 frontend\dist。请安装 Node.js 后执行:
    echo   cd frontend ^&^& npm install ^&^& npm run build
    pause
    exit /b 1
  )
  pushd frontend
  call npm install
  call npm run build
  popd
) else (
  echo [3/4] 已有 frontend\dist，跳过构建。
)

echo [4/4] 启动服务（默认 http://127.0.0.1:8002 ）...
echo       可在 .env 中改 OLLAMA_MODEL / PORT
echo.
python 910_ollama.py
pause
