@echo off
chcp 65001 >nul
echo ========================================
echo   允许网页访问本机 Ollama（可选）
echo ========================================
echo.
echo 说明：GitHub 网页在 Chrome 下仍可能被安全策略拦截。
echo       同学更推荐直接运行 classmate_start.bat / start_ollama.bat
echo.
echo 正在设置 OLLAMA_ORIGINS=* ...
setx OLLAMA_ORIGINS "*" >nul
echo.
echo 请务必：
echo   1. 右键托盘 Ollama 图标 -^> Quit Ollama 完全退出
echo   2. 再重新打开 Ollama
echo   3. 确认已拉取模型： ollama pull deepseek-r1:1.5b
echo.
echo 然后打开： https://liwenyu123-spec.github.io/rag/
echo 若仍连不上，请改用本地： classmate_start.bat
echo.
pause
