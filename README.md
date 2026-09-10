# RAG / 提示词策略聊天助手

支持 **本地 Ollama**（推荐分享）与 **云端 DeepSeek**。

## 同学怎么用（本地 Ollama，无需 API Key）

1. 安装并打开 [Ollama](https://ollama.com/download)
2. 拉取模型：`ollama pull deepseek-r1:1.5b`
3. 安装 [Python 3.10+](https://www.python.org/downloads/)（勾选 Add to PATH）
4. 克隆或下载本仓库后，双击 **`start_ollama.bat`**
5. 浏览器打开 http://127.0.0.1:8002

更详细说明见：[README-分享Ollama.md](./README-分享Ollama.md)

```bash
git clone https://github.com/Liwenyu123-spec/rag.git
cd rag
# Windows：双击 start_ollama.bat
# 或手动：
pip install -r requirements-ollama.txt
python 910_ollama.py
```

## 云端 DeepSeek

配置 `.env` 中的 `DEEPSEEK_API_KEY` 后运行：

```bash
python 910.py
```

默认端口：http://127.0.0.1:8001

## 主要文件

| 文件 | 说明 |
|------|------|
| `910_ollama.py` | 本地 Ollama 后端 + 前端 |
| `910.py` | 云端 DeepSeek 后端 |
| `start_ollama.bat` | 一键启动（装依赖并打开浏览器） |
| `requirements-ollama.txt` | Ollama 版 Python 依赖 |
| `.env.example` | 环境变量示例 |
| `frontend/` | React 前端源码（已包含 `dist` 构建产物） |
