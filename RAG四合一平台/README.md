# RAG 四合一综合平台（单体另存）

把四个项目合成 **一个大应用**：同一个进程、同一个端口、同一个页面，左侧切换模块。

原目录保持不动：
- `基础聊天机器人/`
- `带安全校验的聊天机器人/`
- `社交媒体文案和电商内容生成/`
- `chroma文档管理/`

## 启动

```powershell
python RAG四合一平台/run.py
```

打开：**http://127.0.0.1:8100/**

| 左侧模块 | 能力 |
|----------|------|
| 基础聊天 | 通用流式多轮 |
| 安全校验聊天 | 输入净化 + CoT/ToT 等策略 |
| 文案与电商内容 | 产品文案 / ToT 策划 / 口号 |
| 知识库 RAG | 上传文档、检索、问答 |

## 结构

```
RAG四合一平台/
  run.py
  app/                 # 单体 FastAPI
    main.py
    routers/           # basic / secure / content / rag
  static/index.html    # 统一前端
  apps/chroma文档管理/ # RAG 引擎副本（被 rag 路由复用）
```
