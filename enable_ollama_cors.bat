@echo off
chcp 65001 >nul
echo 为 GitHub 网页开通本机 Ollama 跨域访问...
echo 设置 OLLAMA_ORIGINS=* （允许浏览器打开网站后调用 127.0.0.1:11434）
echo.
setx OLLAMA_ORIGINS "*" >nul
echo 已写入用户环境变量。请完全退出并重新打开 Ollama 后再访问网页。
echo.
echo 网站地址：
echo   https://liwenyu123-spec.github.io/rag/
echo.
echo 模型（如未拉取）：
echo   ollama pull deepseek-r1:1.5b
echo.
pause
