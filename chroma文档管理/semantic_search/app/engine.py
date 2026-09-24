"""基于 LlamaIndex Native RAG 的语义搜索引擎。

流程对应飞书讲义「01-Native_RAG」：
加载文档 → SentenceSplitter 分块 → Embedding → Chroma 存储 → DeepSeek 检索生成。
"""  # 模块说明：Native RAG 核心引擎实现

import re  # 正则：中文分句
from pathlib import Path  # 检查 data 目录、创建持久化路径
from typing import List  # 类型注解

import chromadb  # 向量数据库客户端
from llama_index.core import Document, Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex  # 文档、全局设置、加载器、存储与索引
from llama_index.core.memory import ChatMemoryBuffer  # 多轮对话记忆缓冲区
from llama_index.core.node_parser import SemanticSplitterNodeParser, SentenceSplitter, TokenTextSplitter  # 三种分块器
from llama_index.vector_stores.chroma import ChromaVectorStore  # LlamaIndex 对 Chroma 的适配层

from semantic_search.app.config import (  # 导入运行时配置常量
    CHROMA_PERSIST_DIR,  # Chroma 落盘目录
    CHUNK_OVERLAP,  # 分块重叠
    CHUNK_SIZE,  # 分块大小
    COLLECTION_NAME,  # 集合名
    DASHSCOPE_API_KEY,  # 千问 Key
    DATA_DIR,  # 默认数据目录
    DEEPSEEK_API_KEY,  # DeepSeek Key
    DEEPSEEK_BASE_URL,  # DeepSeek API 地址
    EMBEDDING_MODEL,  # Embedding 模型名
    EMBEDDING_PROVIDER,  # Embedding 提供方
    LLM_MODEL,  # 大模型名
    LLM_PROVIDER,  # 大模型提供方
    RAG_SYSTEM_PROMPT,  # 对话系统提示词
    SIMILARITY_TOP_K,  # 默认 Top-K
)

SAMPLE_DOCUMENTS = [  # 空库时写入的示例知识，方便一启动就能搜
    "FAISS是Meta开发的向量搜索库，支持大规模向量检索，具有高性能和丰富的索引类型",  # 示例：FAISS
    "Chroma是开源的向量数据库，专为LLM应用设计，支持多种嵌入模型和元数据过滤",  # 示例：Chroma
    "倒排索引是搜索引擎的核心数据结构，通过词到文档的映射实现快速全文检索",  # 示例：倒排索引
    "向量数据库通过存储和检索高维向量实现语义搜索，是RAG应用的关键组件",  # 示例：向量库概念
    "深度学习模型如BERT、RoBERTa可以生成高质量的文本嵌入向量，捕捉语义信息",  # 示例：Embedding 模型
    "阿里云千问提供text-embedding系列模型，支持文档和查询向量的差异编码",  # 示例：千问 Embedding
    "FAISS索引IVFFlat通过聚类技术将向量空间划分，大幅提升大规模检索效率",  # 示例：IVFFlat
]

SUPPORTED_EXTS = [".pdf", ".txt", ".md", ".csv", ".docx", ".html", ".ipynb"]  # SimpleDirectoryReader 允许的扩展名


def clean_empty_text(documents: List[Document]) -> List[Document]:  # 过滤空文档
    """过滤空文本，避免后续 embedding / 切分报错。"""
    clean_docs = []  # 存放清洗后的文档
    for doc in documents:  # 逐条检查
        text = (doc.text or "").strip()  # 去掉首尾空白
        if text:  # 有实质内容才保留
            clean_docs.append(Document(text=text, metadata=doc.metadata))  # 重建 Document，保留元数据
    return clean_docs  # 返回过滤后的文档列表


def chinese_sentence_splitter(text: str) -> List[str]:  # 语义分块用的中文分句函数
    """适配中文句号、感叹号、问号、换行分句。"""
    parts = re.split(r"(?<=[。！？!?\n])\s*", text)  # 在中英文句末标点后切开
    return [p.strip() for p in parts if p.strip()]  # 去掉空句


class SemanticSearchEngine:  # Native RAG 引擎主体
    """LlamaIndex + Chroma 的 Native RAG 引擎，默认用 Windows 环境里的 DeepSeek。"""

    def __init__(  # 初始化：Embedding、LLM、Chroma、索引
        self,  # 引擎实例自身
        persist_dir: str = CHROMA_PERSIST_DIR,  # 向量库持久化路径
        collection_name: str = COLLECTION_NAME,  # 集合名
        model_name: str = EMBEDDING_MODEL,  # Embedding 模型名
    ):  # 构造函数签名结束
        self.model_name = model_name  # 记下 Embedding 模型，供 /stats 展示
        self.persist_dir = persist_dir  # 记下持久化目录
        self.collection_name = collection_name  # 记下集合名
        self.llm_model = LLM_MODEL  # 记下当前 LLM 模型名
        self._memories: dict[str, ChatMemoryBuffer] = {}  # session_id → 对话记忆
        self._chat_engines: dict[str, object] = {}  # session+k → chat_engine 缓存

        Settings.embed_model = self._init_embed_model()  # 设置全局 Embedding
        Settings.llm = self._init_llm()  # 设置全局 LLM（可能为 None）
        Settings.node_parser = self._sentence_splitter()  # 默认按句子分块

        Path(persist_dir).mkdir(parents=True, exist_ok=True)  # 确保持久化目录存在
        self.client = chromadb.PersistentClient(path=persist_dir)  # 打开/创建本地 Chroma
        self.collection = self.client.get_or_create_collection(name=self.collection_name)  # 拿到集合
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)  # 包成 LlamaIndex 向量存储
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)  # 存储上下文
        self.index = self._load_or_create_index()  # 有数据则加载，无数据则建空索引
        print(  # 启动日志
            f"搜索引擎已初始化，Embedding: {EMBEDDING_PROVIDER}/{model_name}，"  # Embedding 提供方与模型
            f"LLM: {LLM_PROVIDER}/{self.llm_model}，持久化目录: {persist_dir}"  # LLM 与 Chroma 路径
        )  # print 结束

    def _init_embed_model(self):  # 按配置选择 Embedding 实现
        """DeepSeek 不做向量化；优先本地 HuggingFace，有千问 Key 时仍可用千问。"""
        if EMBEDDING_PROVIDER == "dashscope":  # 云端千问 Embedding
            from llama_index.embeddings.dashscope import DashScopeEmbedding  # 延迟导入，避免无关依赖报错

            if not DASHSCOPE_API_KEY:  # 选了千问却没 Key
                raise RuntimeError("EMBEDDING_PROVIDER=dashscope 但未找到 DASHSCOPE_API_KEY")  # 配置冲突直接报错
            return DashScopeEmbedding(  # 创建千问向量化客户端
                model_name=self.model_name,  # 如 text-embedding-v3
                api_key=DASHSCOPE_API_KEY,  # 鉴权
                text_type="document",  # 文档侧编码（相对 query 侧）
            )

        from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # 本地模型

        print(f"使用本地 Embedding 模型: {self.model_name}")  # 首次可能下载权重
        return HuggingFaceEmbedding(model_name=self.model_name)  # 如 BAAI/bge-small-zh-v1.5

    def _init_llm(self):  # 按配置选择大模型；失败则返回 None
        """默认使用 Windows 环境变量里的 DEEPSEEK_API_KEY。"""  # 方法说明
        if LLM_PROVIDER == "dashscope":  # 千问对话
            from llama_index.llms.dashscope import DashScope  # 延迟导入千问 LLM

            if not DASHSCOPE_API_KEY:  # 没 Key：搜索还能用，问答不可用
                print("警告: 未设置 DASHSCOPE_API_KEY，/query 和 /chat 将不可用")  # 提示缺 Key
                return None  # LLM 置空，仅检索可用
            return DashScope(model_name=LLM_MODEL, api_key=DASHSCOPE_API_KEY, max_tokens=2048)  # 创建千问 LLM

        from llama_index.llms.deepseek import DeepSeek  # DeepSeek 对话

        if not DEEPSEEK_API_KEY:  # 没 Key
            print("警告: 未找到 DEEPSEEK_API_KEY（进程/.env/Windows 用户变量），/query 和 /chat 将不可用")  # 提示缺 Key
            return None  # LLM 置空
        return DeepSeek(  # 创建 DeepSeek LLM
            model=LLM_MODEL,  # 模型名
            api_key=DEEPSEEK_API_KEY,  # 鉴权
            api_base=DEEPSEEK_BASE_URL,  # API 根地址
            timeout=120.0,  # 超时秒数
        )

    def _sentence_splitter(self) -> SentenceSplitter:  # 按句子/标点分块（默认）
        return SentenceSplitter(  # 构造默认分块器
            chunk_size=CHUNK_SIZE,  # 块大小
            chunk_overlap=CHUNK_OVERLAP,  # 块重叠
            paragraph_separator="\n\n\n",  # 段落分隔符
            secondary_chunking_regex="[^,.;。]+[,.;。]?",  # 二级切分正则
        )

    def _token_splitter(self) -> TokenTextSplitter:  # 按 token 数分块
        return TokenTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)  # 严格按 token 控制长度

    def _semantic_splitter(self) -> SemanticSplitterNodeParser:  # 按语义断点分块（更慢更准）
        return SemanticSplitterNodeParser(  # 构造语义分块器
            buffer_size=1,  # 断点检测窗口
            breakpoint_percentile_threshold=95,  # 相似度百分位阈值
            sentence_splitter=chinese_sentence_splitter,  # 先用中文分句
            embed_model=Settings.embed_model,  # 用当前 Embedding 算句向量
        )

    def _splitter(self, mode: str = "sentence"):  # 根据模式名返回对应分块器
        if mode == "token":  # 按 token 切
            return self._token_splitter()  # TokenTextSplitter
        if mode == "semantic":  # 按语义断点切
            return self._semantic_splitter()  # SemanticSplitterNodeParser
        return self._sentence_splitter()  # 默认 sentence

    def _load_or_create_index(self) -> VectorStoreIndex:  # 有存量向量则挂载，否则建空索引
        if self.collection.count() > 0:  # Chroma 里已有数据
            return VectorStoreIndex.from_vector_store(vector_store=self.vector_store)  # 从向量库恢复索引
        return VectorStoreIndex(nodes=[], storage_context=self.storage_context)  # 空索引，后续 insert

    def _reset_chat_engines(self) -> None:  # 知识库变更后清掉旧 chat_engine，避免用过期上下文
        self._chat_engines.clear()  # 清空缓存字典

    def _require_llm(self) -> None:  # 问答前检查 LLM 是否可用
        if Settings.llm is None:  # 全局 LLM 未初始化
            raise RuntimeError("大模型未初始化，请检查 LLM_PROVIDER 与对应 API Key")  # 交给路由转 503

    def add_documents(self, texts: List[str], splitter: str = "sentence") -> int:  # 追加纯文本并索引
        """把纯文本写成 Document，切分后写入向量库。"""  # 方法说明
        if not texts:  # 空列表直接返回
            print("没有文档需要添加")  # 提示跳过
            return 0  # 当前不做写入

        documents = clean_empty_text([Document(text=text) for text in texts])  # 文本 → Document 并去空
        nodes = self._splitter(splitter).get_nodes_from_documents(documents)  # 切成节点（chunk）
        if not nodes:  # 切完没有内容
            print("切分后没有节点，跳过写入")
            return self.collection.count()

        self.index.insert_nodes(nodes)  # 向量化并写入 Chroma
        self._reset_chat_engines()  # 索引变了，重建对话引擎
        total = self.collection.count()  # 当前总量
        print(f"成功添加 {len(texts)} 个文档 / {len(nodes)} 个节点，总计 {total} 个")
        return total

    def ingest_files(  # 对应讲义 SimpleDirectoryReader
        self,
        input_files: List[str] | None = None,  # 指定文件列表
        input_dir: str | None = None,  # 或指定目录
        splitter: str = "sentence",  # 分块模式
    ) -> dict:
        """用 SimpleDirectoryReader 加载本地文件或目录后建索引。"""
        kwargs: dict = {"required_exts": SUPPORTED_EXTS, "recursive": True}  # 目录模式默认参数
        if input_files:  # 有文件列表时只用文件列表（讲义 input_files 写法）
            kwargs = {"input_files": input_files}
        elif input_dir:  # 指定目录
            kwargs["input_dir"] = input_dir
        else:  # 都没传则用配置里的 DATA_DIR
            kwargs["input_dir"] = DATA_DIR

        reader = SimpleDirectoryReader(**kwargs)  # 创建加载器
        documents = clean_empty_text(reader.load_data())  # 读文件成 Document 列表
        print(f"加载了 {len(documents)} 个文档")
        nodes = self._splitter(splitter).get_nodes_from_documents(documents)  # 分块
        print(f"切分为 {len(nodes)} 个节点")
        if nodes:  # 有节点才写入
            self.index.insert_nodes(nodes)  # Embedding + 存 Chroma
            self._reset_chat_engines()
        total = self.collection.count()
        print(f"向量化和存储完成，文档数: {total}")
        return {  # 返回统计给 API
            "loaded_documents": len(documents),  # 本次加载文档数
            "nodes": len(nodes),  # 本次切出的节点数
            "total_documents": total,  # 写入后集合总量
        }

    def seed_if_empty(self, texts: List[str] | None = None) -> int:  # 启动时若库空则灌入示例 + data
        """集合为空时写入示例文档，并加载 data 目录中的本地文件。"""
        if self.collection.count() > 0:  # 已有数据则不重复灌入
            return self.collection.count()

        docs = texts if texts is not None else SAMPLE_DOCUMENTS  # 可用自定义文本覆盖示例
        print("正在加载示例文档...")
        self.add_documents(docs)  # 写入示例知识

        data_dir = Path(DATA_DIR)  # 默认数据目录
        has_files = data_dir.is_dir() and any(p.is_file() for p in data_dir.rglob("*"))  # 目录里是否有文件
        if has_files:  # 有则再用 SimpleDirectoryReader 导入
            print(f"正在从数据目录加载: {data_dir}")
            self.ingest_files(input_dir=str(data_dir))
        return self.collection.count()

    def search(self, query: str, k: int = SIMILARITY_TOP_K) -> List[dict]:  # 只检索，不生成
        """只检索，不调用大模型。"""
        total = self.collection.count()  # 库里有多少条
        if total == 0 or not query or not query.strip():  # 空库或空查询
            return []

        k = min(k, total)  # Top-K 不能超过库容量
        if k == 0:
            return []

        retriever = self.index.as_retriever(similarity_top_k=k)  # 创建检索器
        results = retriever.retrieve(query)  # 向量相似度检索
        formatted_results = []  # 转成 API 友好结构
        for i, item in enumerate(results):  # 逐条格式化
            score = float(item.score or 0.0)  # LlamaIndex 分数
            similarity = round(score, 4)  # 当作相似度展示
            distance = round(max(1.0 - score, 0.0), 4) if 0.0 <= score <= 1.0 else round(1 / (1 + score), 4)  # 近似距离
            formatted_results.append(  # 追加一条结构化结果
                {
                    "rank": i + 1,  # 排名
                    "index": i,  # 下标
                    "document": item.node.get_content(),  # 文本内容
                    "similarity": similarity,  # 相似度
                    "distance": distance,  # 近似距离
                }
            )
        return formatted_results

    def query(self, question: str, k: int = SIMILARITY_TOP_K) -> dict:  # 一次性 RAG：检索 + 生成
        """一次性问答：检索 + 生成。"""
        self._require_llm()  # 没 LLM 就抛错
        engine = self.index.as_query_engine(similarity_top_k=k)  # 查询引擎（内部会检索再生成）
        response = engine.query(question)  # 执行问答
        sources = []  # 收集引用来源
        for i, item in enumerate(getattr(response, "source_nodes", []) or []):  # 遍历命中节点
            score = float(item.score or 0.0)  # 取出分数
            sources.append(  # 追加来源卡片字段
                {
                    "rank": i + 1,  # 排名
                    "index": i,  # 下标
                    "document": item.node.get_content(),  # 原文片段
                    "similarity": round(score, 4),  # 相似度
                    "distance": round(max(1.0 - score, 0.0), 4) if 0.0 <= score <= 1.0 else round(1 / (1 + score), 4),  # 近似距离
                }
            )
        return {"question": question, "answer": str(response), "sources": sources}  # 问题、答案、来源

    def chat(self, question: str, session_id: str = "default", k: int = SIMILARITY_TOP_K) -> dict:  # 多轮 RAG
        """多轮对话：带 ChatMemoryBuffer。"""
        self._require_llm()
        key = f"{session_id}:{k}"  # 同一会话 + 同一 k 共用一个 chat_engine
        if key not in self._chat_engines:  # 首次创建
            memory = self._memories.setdefault(  # 按 session_id 复用记忆
                session_id,
                ChatMemoryBuffer.from_defaults(token_limit=10000),  # 记忆 token 上限
            )
            self._chat_engines[key] = self.index.as_chat_engine(  # 压缩问题 + 检索上下文
                chat_mode="condense_plus_context",  # 先改写问题再检索
                memory=memory,  # 挂上多轮记忆
                similarity_top_k=k,  # 每轮检索条数
                system_prompt=RAG_SYSTEM_PROMPT,  # 系统角色
            )
        response = self._chat_engines[key].chat(question)  # 发本轮消息
        return {  # 组装多轮响应
            "session_id": session_id,  # 回显会话
            "question": question,  # 本轮问题
            "answer": str(response),  # 本轮回答
        }

    def get_stats(self) -> dict:  # 供 /stats、/health 使用
        """返回文档数量、模型名称和持久化路径等状态。"""
        return {  # 供 /stats、/health 展示
            "total_documents": self.collection.count(),  # 集合条数
            "dimension": "auto",  # 维度由 Embedding 模型决定
            "model_name": self.model_name,  # Embedding 模型
            "embedding_provider": EMBEDDING_PROVIDER,  # Embedding 提供方
            "llm_provider": LLM_PROVIDER,  # LLM 提供方
            "llm_model": self.llm_model,  # LLM 模型名
            "persist_dir": self.persist_dir,  # Chroma 持久化目录
            "collection_name": self.collection_name,  # 集合名
            "index_type": "LlamaIndex + ChromaDB",  # 索引类型说明
            "chunk_size": CHUNK_SIZE,  # 分块大小
            "chunk_overlap": CHUNK_OVERLAP,  # 分块重叠
            "data_dir": DATA_DIR,  # 默认数据目录
        }

    def clear_documents(self) -> None:  # 清空知识库
        """删除并重建集合，清空全部文档。"""
        self.client.delete_collection(self.collection_name)  # 删掉旧集合
        self.collection = self.client.get_or_create_collection(name=self.collection_name)  # 重建空集合
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)  # 重新绑定向量存储
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)  # 新存储上下文
        self.index = VectorStoreIndex(nodes=[], storage_context=self.storage_context)  # 空索引
        self._memories.clear()  # 清对话记忆
        self._reset_chat_engines()  # 清 chat_engine 缓存
