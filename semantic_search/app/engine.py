"""基于 ChromaDB 与阿里云千问 Embedding 的语义搜索引擎。"""

import uuid
from typing import List

import chromadb
from chromadb.utils import embedding_functions

from semantic_search.app.config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDING_API_BASE,
    EMBEDDING_MODEL,
)

SAMPLE_DOCUMENTS = [
    "FAISS是Meta开发的向量搜索库，支持大规模向量检索，具有高性能和丰富的索引类型",
    "Chroma是开源的向量数据库，专为LLM应用设计，支持多种嵌入模型和元数据过滤",
    "倒排索引是搜索引擎的核心数据结构，通过词到文档的映射实现快速全文检索",
    "向量数据库通过存储和检索高维向量实现语义搜索，是RAG应用的关键组件",
    "深度学习模型如BERT、RoBERTa可以生成高质量的文本嵌入向量，捕捉语义信息",
    "阿里云千问提供text-embedding系列模型，支持文档和查询向量的差异编码",
    "FAISS索引IVFFlat通过聚类技术将向量空间划分，大幅提升大规模检索效率",
]


class SemanticSearchEngine:
    """管理 Chroma 连接、文档向量化存储和相似度检索。"""

    def __init__(
        self,
        api_key: str,
        model_name: str = EMBEDDING_MODEL,
        persist_dir: str = CHROMA_PERSIST_DIR,
        collection_name: str = COLLECTION_NAME,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=model_name,
            api_base=EMBEDDING_API_BASE,
        )
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
        )
        print(f"搜索引擎已初始化，使用模型: {model_name}，持久化目录: {persist_dir}")

    def add_documents(self, texts: List[str]) -> int:
        """批量写入文档；Chroma 会自动调用嵌入函数向量化。"""
        if not texts:
            print("没有文档需要添加")
            return 0

        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(documents=texts, ids=ids)
        total = self.collection.count()
        print(f"成功添加 {len(texts)} 个文档，总计 {total} 个")
        return total

    def seed_if_empty(self, texts: List[str] | None = None) -> int:
        """集合为空时写入示例文档，避免服务重启重复灌入。"""
        if self.collection.count() > 0:
            return self.collection.count()
        docs = texts if texts is not None else SAMPLE_DOCUMENTS
        print("正在加载示例文档...")
        return self.add_documents(docs)

    def search(self, query: str, k: int = 5) -> List[dict]:
        """按语义相似度检索文档，返回排名、文本、相似度和距离。"""
        total = self.collection.count()
        if total == 0 or not query or not query.strip():
            return []

        k = min(k, total)
        if k == 0:
            return []

        results = self.collection.query(query_texts=[query], n_results=k)
        formatted_results = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 / (1 + distance)
            formatted_results.append(
                {
                    "rank": i + 1,
                    "index": i,
                    "document": results["documents"][0][i],
                    "similarity": round(similarity, 4),
                    "distance": round(float(distance), 4),
                }
            )
        return formatted_results

    def get_stats(self) -> dict:
        """返回文档数量、模型名称和持久化路径等状态。"""
        return {
            "total_documents": self.collection.count(),
            "dimension": "auto",
            "model_name": self.model_name,
            "persist_dir": self.persist_dir,
            "collection_name": self.collection_name,
            "index_type": "ChromaDB",
        }

    def clear_documents(self) -> None:
        """删除并重建集合，清空全部文档。"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
        )
