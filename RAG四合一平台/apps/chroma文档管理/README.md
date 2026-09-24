# chroma文档管理综合案例（FastAPI 工程化）

```powershell
python chroma文档管理/run.py
# 或（兼容旧命令）
python -m semantic_search
```

打开 http://127.0.0.1:8003/

代码在 `chroma文档管理/semantic_search/`。

## 作业主流程：基础 RAG + 检索前优化

1. 浏览器打开对话页（默认「知识库问答」模式）
2. 侧栏可选检索前策略：`rewrite`（清洗+重写）/ `hyde` / `clean` / `none`
3. 前端调用 `POST /ask`，返回最终答案 + 来源 + 检索前中间信息

接口示例：

```http
POST /ask
Content-Type: application/json

{
  "question": "嗯那个帮我看看请假咋扣钱啊???",
  "k": 5,
  "strategy": "rewrite"
}
```
