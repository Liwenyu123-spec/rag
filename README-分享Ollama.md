# 分享给同学：每人在自己电脑打开 Ollama，双击或运行本目录的 start_ollama.bat 即可。

## 别人怎么用（最简）

1. **安装 [Ollama](https://ollama.com/download)**，打开应用（托盘图标常驻）。
2. **拉取模型**（任选其一，需与 `.env` / 默认一致）：

```bash
ollama pull deepseek-r1:1.5b
```

机器更好可换更大模型，例如：

```bash
ollama pull qwen2.5:3b
```

然后在项目根目录复制 `.env.example` 为 `.env`，改成：

```env
OLLAMA_MODEL=qwen2.5:3b
```

3. **安装 Python 3.10+**（勾选 Add to PATH）。
4. **把整个项目文件夹发给对方**（或 git clone）。
5. **双击 `start_ollama.bat`**  
   - 会自动装依赖、必要时构建前端、打开浏览器  
   - 地址默认：http://127.0.0.1:8002  
6. **不需要 DeepSeek API Key**，也不消耗云端额度。

## 原理

| 角色 | 说明 |
|------|------|
| Ollama | 在对方电脑本地跑大模型 |
| `910_ollama.py` | 本机 FastAPI，把网页请求转给本机 Ollama |
| `frontend/dist` | 打包好的聊天界面，由 FastAPI 直接提供 |

每人各自跑一套：**代码在自己电脑 + Ollama 在自己电脑**，互不影响。

## 手动启动（不用 bat）

```bash
pip install -r requirements-ollama.txt
cd frontend && npm install && npm run build && cd ..
python 910_ollama.py
```

## 常见问题

- **连不上模型**：先打开 Ollama，浏览器访问 http://127.0.0.1:11434 ，应有响应。
- **提示找不到模型**：执行 `ollama pull <模型名>`，并保证与 `OLLAMA_MODEL` 一致。
- **页面空白**：确认存在 `frontend/dist/index.html`，没有就执行上面的 `npm run build`。
- **端口占用**：在 `.env` 里改 `PORT=8003`。
- **只要云端 DeepSeek**：用 `python 910.py`，并在 `.env` 配置 `DEEPSEEK_API_KEY`（端口 8001）。

## 开发调试前端

另开终端：

```bash
python 910_ollama.py
cd frontend
# 把 vite.config.ts 里代理目标改成 8002 后
npm run dev
```
