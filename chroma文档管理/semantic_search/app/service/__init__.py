"""业务服务层：检索前优化 + RAG 问答编排 + GraphRAG。

注意：不要在这里顶层 import graph_rag。
`from semantic_search.app.service.xxx import ...` 会先执行本文件；
若此时加载 Neo4j 依赖，未安装 llama-index-graph-stores-neo4j 时向量引擎也起不来。
"""

from semantic_search.app.service.rag_service import RagAskService
from semantic_search.app.service.pipeline import AskModule, AskPipeline

__all__ = ["RagAskService", "GraphRagService", "AskModule", "AskPipeline"]


def __getattr__(name: str):
    if name == "GraphRagService":
        from semantic_search.app.service.graph_rag import GraphRagService

        return GraphRagService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
