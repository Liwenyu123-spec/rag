"""业务服务层：检索前优化 + RAG 问答编排。"""  # 包说明：对外暴露编排服务类

from semantic_search.app.service.rag_service import RagAskService  # 导入问答编排服务

__all__ = ["RagAskService"]  # 限制 from ...service import * 时仅导出该类
