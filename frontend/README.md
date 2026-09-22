# 前端开发说明

对应后端项目：**带安全校验的聊天机器人**（端口 8001）。

> 电商文案 / 社交媒体策划弹窗若要单独跑，请启动 `社交媒体文案和电商内容生成/main.py`（端口 8002）。

## 开发模式（热更新）

终端 1：启动后端
```powershell
conda activate llm
python 带安全校验的聊天机器人/main.py
```

终端 2：启动前端
```powershell
cd frontend
npm run dev
```

浏览器打开 http://127.0.0.1:5173 （会代理 API 到 8001）

## 生产模式（由 FastAPI 直接提供页面）

```powershell
cd frontend
npm run build
conda activate llm
python 带安全校验的聊天机器人/main.py
```

浏览器打开 http://127.0.0.1:8001
