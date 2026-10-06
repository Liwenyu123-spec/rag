# RAG 四合一平台（chroma文档管理）

一个端口、一个页面、四个模块：基础聊天、安全聊天、文案生成、知识库 RAG。  
原先独立的搜索引擎就是现在的「知识库 RAG」页签。

模块说明见：**[项目说明.md](./项目说明.md)**。

```powershell
python chroma文档管理/run.py
# 或（兼容旧命令）
python -m semantic_search
```

打开 http://127.0.0.1:8003/  
接口文档：http://127.0.0.1:8003/docs

顶部切换模块。知识库页签仍走 `POST /ask`，可选 GraphRAG。

| 模块 | 接口 |
|------|------|
| 基础聊天 | `POST /api/basic/chat`（SSE） |
| 安全聊天 | `GET /api/secure/stream_chat` |
| 文案与电商 | `/api/content/product_copy`、`social_plan`、`self_consistency` |
| 知识库 RAG | `/ask` `/search` `/query` `/chat` `/graph/*` |

```http
POST /ask
Content-Type: application/json

{
  "question": "沃兹尼亚克的母校是哪里？他和谁一起创立了苹果？",
  "k": 5,
  "preset": "graph_hybrid"
}
```

检索评估：`POST /eval/retrieval`（页面按钮「跑检索评估（基础 vs 当前）」）。
