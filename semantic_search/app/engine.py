"""基于 LlamaIndex Native RAG 的语义搜索引擎。

流程对应飞书讲义「01-Native_RAG」：
加载文档 → SentenceSplitter 分块 → 千问 Embedding → Chroma 存储 → 检索 / 大模型生成。
"""

import re
from pathlib import Path
from typing import List

import chromadb
from llama_index.core import Document, Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import SemanticSplitterNodeParser, SentenceSplitter, TokenTextSplitter
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from semantic_search.app.config import (
    CHROMA_PERSIST_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DATA_DIR,
    DEEPSEEK_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_PROVIDER,
    RAG_SYSTEM_PROMPT,
    SIMILARITY_TOP_K,
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

SUPPORTED_EXTS = [".pdf", ".txt", ".md", ".csv", ".docx", ".html", ".ipynb"]


def clean_empty_text(documents: List[Document]) -> List[Document]:
    """过滤空文本，避免后续 embedding / 切分报错。"""
    clean_docs = []
    for doc in documents:
        text = (doc.text or "").strip()
        if text:
            clean_docs.append(Document(text=text, metadata=doc.metadata))
    return clean_docs


def chinese_sentence_splitter(text: str) -> List[str]:
    """适配中文句号、感叹号、问号、换行分句。"""
    parts = re.split(r"(?<=[。！？!?\n])\s*", text)
    return [p.strip() for p in parts if p.strip()]


class SemanticSearchEngine:
    """LlamaIndex + Chroma + 千问 Embedding 的 Native RAG 引擎。"""

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
        self.llm_model = LLM_MODEL
        self._memories: dict[str, ChatMemoryBuffer] = {}
        self._chat_engines: dict[str, object] = {}

        Settings.embed_model = DashScopeEmbedding(
            model_name=model_name,
            api_key=api_key,
            text_type="document",
        )
        Settings.llm = self._init_llm()
        Settings.node_parser = self._sentence_splitter()

        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = self._load_or_create_index()
        print(
            f"搜索引擎已初始化，Embedding: {model_name}，"
            f"LLM: {self.llm_model}，持久化目录: {persist_dir}"
        )

    def _init_llm(self):
        """讲义默认千问 qwen-plus；也可切到项目里已有的 DeepSeek。"""
        if LLM_PROVIDER == "deepseek":
            from llama_index.llms.deepseek import DeepSeek

            if not DEEPSEEK_API_KEY:
                print("警告: 未设置 DEEPSEEK_API_KEY，/query 和 /chat 将不可用")
                return None
            return DeepSeek(model=LLM_MODEL, api_key=DEEPSEEK_API_KEY, timeout=120.0)

        from llama_index.llms.dashscope import DashScope

        return DashScope(model_name=LLM_MODEL, api_key=self.api_key, max_tokens=2048)

    def _sentence_splitter(self) -> SentenceSplitter:
        return SentenceSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            paragraph_separator="\n\n\n",
            secondary_chunking_regex="[^,.;。]+[,.;。]?",
        )

    def _token_splitter(self) -> TokenTextSplitter:
        return TokenTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    def _semantic_splitter(self) -> SemanticSplitterNodeParser:
        return SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            sentence_splitter=chinese_sentence_splitter,
            embed_model=Settings.embed_model,
        )

    def _splitter(self, mode: str = "sentence"):
        if mode == "token":
            return self._token_splitter()
        if mode == "semantic":
            return self._semantic_splitter()
        return self._sentence_splitter()

    def _load_or_create_index(self) -> VectorStoreIndex:
        if self.collection.count() > 0:
            return VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
        return VectorStoreIndex(nodes=[], storage_context=self.storage_context)

    def _reset_chat_engines(self) -> None:
        self._chat_engines.clear()

    def _require_llm(self) -> None:
        if Settings.llm is None:
            raise RuntimeError("大模型未初始化，请检查 LLM_PROVIDER 与对应 API Key")

    def add_documents(self, texts: List[str], splitter: str = "sentence") -> int:
        """把纯文本写成 Document，切分后写入向量库。"""
        if not texts:
            print("没有文档需要添加")
            return 0

        documents = clean_empty_text([Document(text=text) for text in texts])
        nodes = self._splitter(splitter).get_nodes_from_documents(documents)
        if not nodes:
            print("切分后没有节点，跳过写入")
            return self.collection.count()

        self.index.insert_nodes(nodes)
        self._reset_chat_engines()
        total = self.collection.count()
        print(f"成功添加 {len(texts)} 个文档 / {len(nodes)} 个节点，总计 {total} 个")
        return total

    def ingest_files(
        self,
        input_files: List[str] | None = None,
        input_dir: str | None = None,
        splitter: str = "sentence",
    ) -> dict:
        """用 SimpleDirectoryReader 加载本地文件或目录后建索引。"""
        kwargs: dict = {"required_exts": SUPPORTED_EXTS, "recursive": True}
        if input_files:
            kwargs = {"input_files": input_files}
        elif input_dir:
            kwargs["input_dir"] = input_dir
        else:
            kwargs["input_dir"] = DATA_DIR

        reader = SimpleDirectoryReader(**kwargs)
        documents = clean_empty_text(reader.load_data())
        print(f"加载了 {len(documents)} 个文档")
        nodes = self._splitter(splitter).get_nodes_from_documents(documents)
        print(f"切分为 {len(nodes)} 个节点")
        if nodes:
            self.index.insert_nodes(nodes)
            self._reset_chat_engines()
        total = self.collection.count()
        print(f"向量化和存储完成，文档数: {total}")
        return {
            "loaded_documents": len(documents),
            "nodes": len(nodes),
            "total_documents": total,
        }

    def seed_if_empty(self, texts: List[str] | None = None) -> int:
        """集合为空时写入示例文档，并加载 data 目录中的本地文件。"""
        if self.collection.count() > 0:
            return self.collection.count()

        docs = texts if texts is not None else SAMPLE_DOCUMENTS
        print("正在加载示例文档...")
        self.add_documents(docs)

        data_dir = Path(DATA_DIR)
        has_files = data_dir.is_dir() and any(p.is_file() for p in data_dir.rglob("*"))
        if has_files:
            print(f"正在从数据目录加载: {data_dir}")
            self.ingest_files(input_dir=str(data_dir))
        return self.collection.count()

    def search(self, query: str, k: int = SIMILARITY_TOP_K) -> List[dict]:
        """只检索，不调用大模型。"""
        total = self.collection.count()
        if total == 0 or not query or not query.strip():
            return []

        k = min(k, total)
        if k == 0:
            return []

        retriever = self.index.as_retriever(similarity_top_k=k)
        results = retriever.retrieve(query)
        formatted_results = []
        for i, item in enumerate(results):
            score = float(item.score or 0.0)
            similarity = round(score, 4)
            distance = round(max(1.0 - score, 0.0), 4) if 0.0 <= score <= 1.0 else round(1 / (1 + score), 4)
            formatted_results.append(
                {
                    "rank": i + 1,
                    "index": i,
                    "document": item.node.get_content(),
                    "similarity": similarity,
                    "distance": distance,
                }
            )
        return formatted_results

    def query(self, question: str, k: int = SIMILARITY_TOP_K) -> dict:
        """一次性问答：检索 + 生成。"""
        self._require_llm()
        engine = self.index.as_query_engine(similarity_top_k=k)
        response = engine.query(question)
        sources = []
        for i, item in enumerate(getattr(response, "source_nodes", []) or []):
            score = float(item.score or 0.0)
            sources.append(
                {
                    "rank": i + 1,
                    "index": i,
                    "document": item.node.get_content(),
                    "similarity": round(score, 4),
                    "distance": round(max(1.0 - score, 0.0), 4) if 0.0 <= score <= 1.0 else round(1 / (1 + score), 4),
                }
            )
        return {"question": question, "answer": str(response), "sources": sources}

    def chat(self, question: str, session_id: str = "default", k: int = SIMILARITY_TOP_K) -> dict:
        """多轮对话：带 ChatMemoryBuffer。"""
        self._require_llm()
        key = f"{session_id}:{k}"
        if key not in self._chat_engines:
            memory = self._memories.setdefault(
                session_id,
                ChatMemoryBuffer.from_defaults(token_limit=10000),
            )
            self._chat_engines[key] = self.index.as_chat_engine(
                chat_mode="condense_plus_context",
                memory=memory,
                similarity_top_k=k,
                system_prompt=RAG_SYSTEM_PROMPT,
            )
        response = self._chat_engines[key].chat(question)
        return {
            "session_id": session_id,
            "question": question,
            "answer": str(response),
        }

    def get_stats(self) -> dict:
        """返回文档数量、模型名称和持久化路径等状态。"""
        return {
            "total_documents": self.collection.count(),
            "dimension": "auto",
            "model_name": self.model_name,
            "llm_provider": LLM_PROVIDER,
            "llm_model": self.llm_model,
            "persist_dir": self.persist_dir,
            "collection_name": self.collection_name,
            "index_type": "LlamaIndex + ChromaDB",
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "data_dir": DATA_DIR,
        }

    def clear_documents(self) -> None:
        """删除并重建集合，清空全部文档。"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex(nodes=[], storage_context=self.storage_context)
        self._memories.clear()
        self._reset_chat_engines()
