# RAG / 提示词策略聊天助手

## 同学已有 Ollama + 模型（不用下载整个项目）

1. 本机 Ollama 保持打开  
2. 终端执行一行（保持窗口运行）：

```bash
curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py | python
```

3. 浏览器打开：**https://liwenyu123-spec.github.io/rag/**  
4. 右上角选择自己的模型即可  

> 原因：Chrome 会拦截网页直连 `11434`；这个小桥接只做转发并加上允许头，不改你的模型。

## 完整下载本地启动（备选）

解压 [Release](https://github.com/Liwenyu123-spec/rag/releases/tag/ollama-share) 后双击 `classmate_start.bat` → http://127.0.0.1:8002

## 云端 DeepSeek

`.env` 配置 `DEEPSEEK_API_KEY` 后：`python 910.py`
