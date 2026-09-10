# RAG / 提示词策略聊天助手

## 同学已有 Ollama + 模型（不用下载整个项目）

1. 本机 Ollama 保持打开  
2. 打开 **PowerShell**（Win 键搜 powershell），粘贴下面整段回车：

```powershell
curl.exe -sL "https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py" -o "$env:TEMP\pna_proxy.py"; Start-Process pythonw -ArgumentList "$env:TEMP\pna_proxy.py" -WindowStyle Hidden; Start-Sleep 1; try { (Invoke-RestMethod http://127.0.0.1:18789/__ping).ok } catch { "启动失败：请确认已安装 Python，并已打开 Ollama" }
```

成功会显示 `True`。若提示没有 `pythonw`，把命令里的 `pythonw` 改成 `python`。

> 注意：以前那条带 `%TEMP%` 的是 **CMD** 写法，在 PowerShell 里会没反应。

3. 打开 https://liwenyu123-spec.github.io/rag/ （黑窗口可关）  
4. 关掉网页约 1 分钟后桥接自动停  

也可双击 `start_bridge.bat`（会有成功提示）。

## 完整下载本地启动（备选）

解压 [Release](https://github.com/Liwenyu123-spec/rag/releases/tag/ollama-share) 后双击 `classmate_start.bat` → http://127.0.0.1:8002

## 云端 DeepSeek

`.env` 配置 `DEEPSEEK_API_KEY` 后：`python 910.py`
