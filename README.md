# RAG / 提示词策略聊天助手

## 同学已有 Ollama + 模型（不用下载整个项目）

1. 本机 Ollama 保持打开  
2. 终端运行一次（**之后可关掉黑窗口**）：

```bat
curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py -o %TEMP%\pna_proxy.py && start "" /B pythonw %TEMP%\pna_proxy.py
```

也可双击仓库里的 `start_bridge.bat`。

3. 打开：**https://liwenyu123-spec.github.io/rag/**  
4. **关掉网页大约 1 分钟后，桥接会自动停止**  

右上角可选自己的模型；「思考·关」更快。

## 完整下载本地启动（备选）

解压 [Release](https://github.com/Liwenyu123-spec/rag/releases/tag/ollama-share) 后双击 `classmate_start.bat` → http://127.0.0.1:8002

## 云端 DeepSeek

`.env` 配置 `DEEPSEEK_API_KEY` 后：`python 910.py`
