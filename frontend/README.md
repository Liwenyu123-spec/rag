# 前端开发说明

## 开发模式（热更新）

终端 1：启动后端
```powershell
conda activate llm
python 910.py
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
python 910.py
```

浏览器打开 http://127.0.0.1:8001
