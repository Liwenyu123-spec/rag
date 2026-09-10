# RAG / 提示词策略聊天助手

## 同学怎么用（推荐，不会卡住）

Chrome 从 GitHub 网页访问本机 Ollama **经常被浏览器安全策略拦截**，看起来像卡住。请让同学用本地启动：

1. 安装并打开 [Ollama](https://ollama.com/download)
2. `ollama pull deepseek-r1:1.5b`（或任意自己的模型）
3. 下载 [Release 压缩包](https://github.com/Liwenyu123-spec/rag/releases/tag/ollama-share)
4. 解压后双击 **`classmate_start.bat`**（或 `start_ollama.bat`）
5. 自动打开 http://127.0.0.1:8002 — 右上角可选本机模型

## 在线页（仅作说明 / 检测）

https://liwenyu123-spec.github.io/rag/

连不上时页面会显示黄条指引；能连上才可网页直连（部分浏览器仍会拦）。

## 云端 DeepSeek

`.env` 配置 `DEEPSEEK_API_KEY` 后：`python 910.py` → http://127.0.0.1:8001
