@echo off
chcp 65001 >nul
echo 正在后台启动 Ollama 网页桥接（可关闭本窗口）...
curl -sL "https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py" -o "%TEMP%\pna_proxy.py"
if errorlevel 1 (
  echo 下载失败，请检查网络。
  pause
  exit /b 1
)
start "" /B pythonw "%TEMP%\pna_proxy.py"
timeout /t 1 /nobreak >nul
echo.
echo 已在后台运行。现在可以：
echo   1. 关掉本黑窗口
echo   2. 打开 https://liwenyu123-spec.github.io/rag/
echo 关闭网页大约 1 分钟后桥接会自动退出。
echo.
pause
