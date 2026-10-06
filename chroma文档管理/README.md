# chroma文档管理综合案例（FastAPI 工程化）

模块说明见：**[项目说明.md](./项目说明.md)**。

```powershell
python chroma文档管理/run.py
# 或（兼容旧命令）
python -m semantic_search
```

打开 http://127.0.0.1:8003/  
代码在 `chroma文档管理/semantic_search/`。

## 主流程（POST /ask）

浏览器默认「RAG 知识库问答」：可选预设或勾选检索前/中/后、Self-RAG、CRAG、**知识图谱双通道**、生成评估。  
前端调用 `POST /ask`，返回答案、来源、各模块过程信息（含 `graph`）。

图谱相关：

- 侧栏可 `neo4j console` 之后「用示例构建图谱」
- 模式「图谱问答」走 `POST /graph/query`
- 预设 `graph_hybrid` = 向量 RAG + Neo4j 子图

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
