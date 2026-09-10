@echo off
chcp 65001 >nul
echo 正在后台启动桥接...
where curl.exe >nul 2>nul
if errorlevel 1 (
  echo 未找到 curl.exe，请用 Windows 10/11 自带终端，或安装 curl。
  pause
  exit /b 1
)

curl.exe -sL "https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py" -o "%TEMP%\pna_proxy.py"
if not exist "%TEMP%\pna_proxy.py" (
  echo 下载失败，请检查网络能否打开 GitHub。
  pause
  exit /b 1
)

where pythonw >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo 未找到 Python。请先安装 Python 并勾选 Add to PATH。
    pause
    exit /b 1
  )
  start "" /B python "%TEMP%\pna_proxy.py"
) else (
  start "" /B pythonw "%TEMP%\pna_proxy.py"
)

timeout /t 2 /nobreak >nul
curl.exe -s http://127.0.0.1:18789/__ping
echo.
echo.
echo 若上一行出现 "ok": true ，说明已成功，可关闭本窗口。
echo 然后打开: https://liwenyu123-spec.github.io/rag/
echo 关掉网页约 1 分钟后桥接会自动退出。
echo 若失败：请确认已安装 Python、已打开 Ollama。
echo.
pause
