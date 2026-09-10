# RAG / 提示词策略聊天助手

## 直接打开网站就能用（推荐发给同学）

1. 安装并打开 [Ollama](https://ollama.com/download)
2. 执行：`ollama pull deepseek-r1:1.5b`
3. **第一次**在 Windows 上双击仓库里的 [`enable_ollama_cors.bat`](./enable_ollama_cors.bat)，然后**重启 Ollama**
4. 浏览器打开：

### https://liwenyu123-spec.github.io/rag/

网页跑在 GitHub 上，模型仍在对方自己电脑的 Ollama 里，**不需要 API Key，也不用装 Python**。

> 若页头提示连不上 Ollama：确认 Ollama 已打开，并已运行过 `enable_ollama_cors.bat`。

---

## 本地完整后端（可选）

需要 Python 时，双击 [`start_ollama.bat`](./start_ollama.bat)，或：

```bash
pip install -r requirements-ollama.txt
python 910_ollama.py
```

地址：http://127.0.0.1:8002

## 云端 DeepSeek

配置 `.env` 的 `DEEPSEEK_API_KEY` 后：`python 910.py` → http://127.0.0.1:8001

## 说明

| 方式 | 别人要做什么 | 打开哪里 |
|------|--------------|----------|
| **GitHub 网页** | 只开 Ollama | https://liwenyu123-spec.github.io/rag/ |
| 本地 bat | 装 Python + Ollama | http://127.0.0.1:8002 |
| 云端 API | 配 DeepSeek Key | http://127.0.0.1:8001 |

详细 Ollama 分享说明：[README-分享Ollama.md](./README-分享Ollama.md)
