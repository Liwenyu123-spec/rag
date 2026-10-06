"""基于 LlamaIndex Native RAG 的语义搜索引擎。

流程对应飞书讲义「01-Native_RAG」：
加载文档 → SentenceSplitter 分块 → Embedding → Chroma 存储 → DeepSeek 检索生成。
"""  # 模块说明：Native RAG 核心引擎实现

import re  # 正则：中文分句
from pathlib import Path  # 检查 data 目录、创建持久化路径
from typing import List  # 类型注解

from llama_index.core import Document, Settings, SimpleDirectoryReader  # 文档、全局设置、加载器
from llama_index.core.memory import ChatMemoryBuffer  # 多轮对话记忆缓冲区
from llama_index.core.node_parser import SemanticSplitterNodeParser, SentenceSplitter, TokenTextSplitter  # 三种分块器

from semantic_search.app.config import (  # 导入运行时配置常量
    CHROMA_PERSIST_DIR,  # Chroma 落盘目录
    CHUNK_OVERLAP,  # 分块重叠
    CHUNK_SIZE,  # 分块大小
    COLLECTION_NAME,  # 集合名
    COMPRESS_ENABLED,  # 上下文压缩开关
    CRAG_ENABLED,  # Corrective RAG 开关
    DASHSCOPE_API_KEY,  # 千问 Key
    DATA_DIR,  # 默认数据目录
    DEEPSEEK_API_KEY,  # DeepSeek Key
    DEEPSEEK_BASE_URL,  # DeepSeek API 地址
    EMBEDDING_MODEL,  # Embedding 模型名
    EMBEDDING_PROVIDER,  # Embedding 提供方
    HYBRID_ENABLED,  # 混合检索开关
    LLM_MODEL,  # 大模型名
    LLM_PROVIDER,  # 大模型提供方
    QDRANT_PATH,
    RAG_SYSTEM_PROMPT,  # 对话系统提示词
    REORDER_ENABLED,  # 长上下文重排开关
    RERANK_ENABLED,  # 重排开关
    RERANK_PROVIDER,  # 重排提供方
    SELF_RAG_ENABLED,  # Self-RAG 开关
    SIMILARITY_TOP_K,  # 默认 Top-K
    normalize_vector_backend,
)  # config 导入结束
from semantic_search.app.vector_backends import nodes_from_slot, open_chroma_slot, open_qdrant_slot
from semantic_search.app.service.retrieval_optimize import (  # 检索中/后优化工具
    apply_postprocessors,  # 对召回节点做重排/压缩/重排版
    build_hybrid_retriever,  # 构建向量或混合检索器
    build_node_postprocessors,  # 组装 NodePostprocessor 列表
    candidate_top_k,  # 粗排候选数计算
    nodes_from_index,  # 从索引拉出 BM25 语料节点
)  # retrieval_optimize 导入结束

SAMPLE_DOCUMENTS = [  # 空库时写入的示例知识，方便一启动就能搜
    "FAISS是Meta开发的向量搜索库，支持大规模向量检索，具有高性能和丰富的索引类型",  # 示例：FAISS
    "Chroma是开源的向量数据库，专为LLM应用设计，支持多种嵌入模型和元数据过滤",  # 示例：Chroma
    "倒排索引是搜索引擎的核心数据结构，通过词到文档的映射实现快速全文检索",  # 示例：倒排索引
    "向量数据库通过存储和检索高维向量实现语义搜索，是RAG应用的关键组件",  # 示例：向量库概念
    "深度学习模型如BERT、RoBERTa可以生成高质量的文本嵌入向量，捕捉语义信息",  # 示例：Embedding 模型
    "阿里云千问提供text-embedding系列模型，支持文档和查询向量的差异编码",  # 示例：千问 Embedding
    "FAISS索引IVFFlat通过聚类技术将向量空间划分，大幅提升大规模检索效率",  # 示例：IVFFlat
]  # SAMPLE_DOCUMENTS 结束

SUPPORTED_EXTS = [".pdf", ".txt", ".md", ".csv", ".docx", ".html", ".ipynb"]  # SimpleDirectoryReader 允许的扩展名


def clean_empty_text(documents: List[Document]) -> List[Document]:  # 过滤空文档
    """过滤空文本，避免后续 embedding / 切分报错。"""  # 文档：空文本过滤
    clean_docs = []  # 存放清洗后的文档
    for doc in documents:  # 逐条检查
        text = (doc.text or "").strip()  # 去掉首尾空白
        if text:  # 有实质内容才保留
            clean_docs.append(Document(text=text, metadata=doc.metadata))  # 重建 Document，保留元数据
    return clean_docs  # 返回过滤后的文档列表


def chinese_sentence_splitter(text: str) -> List[str]:  # 语义分块用的中文分句函数
    """适配中文句号、感叹号、问号、换行分句。"""  # 文档：中文分句规则
    parts = re.split(r"(?<=[。！？!?\n])\s*", text)  # 在中英文句末标点后切开
    return [p.strip() for p in parts if p.strip()]  # 去掉空句


class SemanticSearchEngine:  # Native RAG 引擎主体
    """LlamaIndex 引擎：Chroma 与 Qdrant 两套向量库并存，按 bind(backend) 切换。"""  # 类说明

    def __init__(  # 初始化：Embedding、LLM、双向量库
        self,  # 引擎实例自身
        persist_dir: str = CHROMA_PERSIST_DIR,  # Chroma 持久化路径
        collection_name: str = COLLECTION_NAME,  # 集合名
        model_name: str = EMBEDDING_MODEL,  # Embedding 模型名
    ):  # 构造函数签名结束
        self.model_name = model_name  # 记下 Embedding 模型，供 /stats 展示
        self.persist_dir = persist_dir  # 记下 Chroma 持久化目录
        self.collection_name = collection_name  # 记下集合名
        self.llm_model = LLM_MODEL  # 记下当前 LLM 模型名
        self.backend_name = "chroma"
        self._memories: dict[str, ChatMemoryBuffer] = {}  # session_id → 对话记忆
        self._chat_engines: dict[str, object] = {}  # backend+session+k → chat_engine 缓存
        self._bm25_nodes_cache: dict[str, list | None] = {"chroma": None, "qdrant": None}

        Settings.embed_model = self._init_embed_model()  # 设置全局 Embedding
        Settings.llm = self._init_llm()  # 设置全局 LLM（可能为 None）
        Settings.node_parser = self._sentence_splitter()  # 默认按句子分块

        chroma_slot = open_chroma_slot(persist_dir, collection_name)
        self.chroma_client = chroma_slot.raw_client
        self.slots = {"chroma": chroma_slot}
        self.qdrant_ready = False
        self.qdrant_error = None
        self.qdrant_client = None
        try:
            qdrant_slot = open_qdrant_slot(QDRANT_PATH, collection_name)
            self.slots["qdrant"] = qdrant_slot
            self.qdrant_client = qdrant_slot.client
            self.qdrant_ready = True
            print(f"Qdrant 本机库已就绪: {QDRANT_PATH}（{qdrant_slot.count()} 条）")
        except Exception as exc:  # noqa: BLE001
            self.qdrant_error = str(exc)
            print(f"警告: Qdrant 初始化失败，仅能使用 Chroma: {exc}")

        print(  # 启动日志
            f"搜索引擎已初始化，Embedding: {EMBEDDING_PROVIDER}/{model_name}，"  # Embedding 提供方与模型
            f"LLM: {LLM_PROVIDER}/{self.llm_model}，Chroma: {persist_dir}"
        )  # print 结束
        print(  # 检索优化开关汇总日志
            "检索优化: "  # 前缀文案
            f"hybrid={HYBRID_ENABLED}, rerank={RERANK_ENABLED}/{RERANK_PROVIDER}, "  # 混合与重排
            f"compress={COMPRESS_ENABLED}, reorder={REORDER_ENABLED}, "  # 压缩与重排版
            f"crag={CRAG_ENABLED}, self_rag={SELF_RAG_ENABLED}"  # CRAG 与 Self-RAG
        )  # 优化开关日志结束

    def bind(self, backend: str | None) -> "SemanticSearchEngine":
        name = normalize_vector_backend(backend)
        if name == "qdrant" and not self.qdrant_ready:
            raise RuntimeError(self.qdrant_error or "Qdrant 不可用")
        bound = object.__new__(SemanticSearchEngine)
        bound.__dict__ = {**self.__dict__, "backend_name": name}
        return bound

    def _slot(self):
        slot = self.slots.get(self.backend_name)
        if slot is None:
            raise RuntimeError(f"向量后端不可用: {self.backend_name}")
        return slot

    @property
    def index(self):
        return self._slot().index

    @index.setter
    def index(self, value) -> None:
        self._slot().index = value

    @property
    def collection(self):
        return self._slot()

    @property
    def client(self):
        return self._slot().raw_client

    def _init_embed_model(self):  # 按配置选择 Embedding 实现
        """DeepSeek 不做向量化；支持 Chinese-CLIP / HuggingFace / 千问。"""  # 方法说明
        if EMBEDDING_PROVIDER in {"chinese_clip", "cn_clip", "chinese-clip"}:  # 本地 Chinese-CLIP
            from semantic_search.app.chinese_clip_embedding import ChineseCLIPEmbedding  # 文本塔封装

            print(f"使用本地 Chinese-CLIP Embedding: {self.model_name}")  # 启动日志
            return ChineseCLIPEmbedding(model_path=self.model_name)  # 目录含 pytorch_model.bin

        if EMBEDDING_PROVIDER == "dashscope":  # 云端千问 Embedding
            from semantic_search.app.safe_embedding import SafeDashScopeEmbedding  # 分批安全封装

            if not DASHSCOPE_API_KEY:  # 选了千问却没 Key
                raise RuntimeError("EMBEDDING_PROVIDER=dashscope 但未找到 DASHSCOPE_API_KEY")  # 配置冲突直接报错
            print(f"使用 SafeDashScopeEmbedding（分批≤10）: {self.model_name}")  # 提示当前 Embedding
            return SafeDashScopeEmbedding(  # 对齐 ModularRAG：避免批量超限
                model_name=self.model_name,  # 如 text-embedding-v3
                api_key=DASHSCOPE_API_KEY,  # 鉴权
                text_type="document",  # 文档侧编码（相对 query 侧）
            )  # SafeDashScopeEmbedding 结束

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
        )  # DeepSeek 结束

    def _sentence_splitter(self) -> SentenceSplitter:  # 按句子/标点分块（默认）
        return SentenceSplitter(  # 构造默认分块器
            chunk_size=CHUNK_SIZE,  # 块大小
            chunk_overlap=CHUNK_OVERLAP,  # 块重叠
            paragraph_separator="\n\n\n",  # 段落分隔符
            secondary_chunking_regex="[^,.;。]+[,.;。]?",  # 二级切分正则
        )  # SentenceSplitter 结束

    def _token_splitter(self) -> TokenTextSplitter:  # 按 token 数分块
        return TokenTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)  # 严格按 token 控制长度

    def _semantic_splitter(self) -> SemanticSplitterNodeParser:  # 按语义断点分块（更慢更准）
        return SemanticSplitterNodeParser(  # 构造语义分块器
            buffer_size=1,  # 断点检测窗口
            breakpoint_percentile_threshold=95,  # 相似度百分位阈值
            sentence_splitter=chinese_sentence_splitter,  # 先用中文分句
            embed_model=Settings.embed_model,  # 用当前 Embedding 算句向量
        )  # SemanticSplitterNodeParser 结束

    def _splitter(self, mode: str = "sentence"):  # 根据模式名返回对应分块器
        if mode == "token":  # 按 token 切
            return self._token_splitter()  # TokenTextSplitter
        if mode == "semantic":  # 按语义断点切
            return self._semantic_splitter()  # SemanticSplitterNodeParser
        return self._sentence_splitter()  # 默认 sentence

    def _invalidate_retrieval_cache(self) -> None:  # 入库变更后清缓存
        """入库变更后清空当前后端的 BM25 语料与对话引擎缓存。"""  # 方法说明
        self._bm25_nodes_cache[self.backend_name] = None
        prefix = f"{self.backend_name}:"
        for key in [k for k in list(self._chat_engines) if str(k).startswith(prefix)]:
            self._chat_engines.pop(key, None)

    def _bm25_nodes(self) -> list:  # 获取 BM25 语料节点
        """懒加载 BM25 节点列表。"""  # 方法说明
        cached = self._bm25_nodes_cache.get(self.backend_name)
        if cached is None:  # 尚未缓存
            cached = nodes_from_slot(self._slot())
            self._bm25_nodes_cache[self.backend_name] = cached
        return cached  # 返回缓存列表

    def _build_retriever(  # 构建检索器（可覆盖混合开关）
        self,  # 引擎实例
        k: int = SIMILARITY_TOP_K,  # 最终返回条数
        *,  # 其后只能关键字传参
        hybrid_enabled: bool | None = None,  # None 跟全局配置
        num_queries: int | None = None,  # Multi-Query 数
        fusion_mode: str | None = None,  # 融合策略名
    ):  # 签名结束
        """检索中：按配置（可被请求覆盖）构建纯向量或 向量+BM25 融合检索器。"""  # 方法说明
        use_hybrid = HYBRID_ENABLED if hybrid_enabled is None else bool(hybrid_enabled)  # 解析实际开关
        return build_hybrid_retriever(  # 委托给 retrieval_optimize
            self.index,  # 向量索引
            final_k=k,  # 最终条数
            collection=self.collection,  # 当前向量后端（Duck typing: .get）
            nodes_cache=self._bm25_nodes() if use_hybrid else None,  # 混合时才喂 BM25 语料
            hybrid_enabled=use_hybrid,  # 是否混合
            num_queries=num_queries,  # Multi-Query
            fusion_mode=fusion_mode,  # 融合策略
        )  # build_hybrid_retriever 结束

    def _build_postprocessors(  # 组装检索后处理器
        self,  # 引擎实例
        k: int = SIMILARITY_TOP_K,  # 最终条数
        *,  # 其后只能关键字传参
        rerank_enabled: bool | None = None,  # None 跟全局
        compress_enabled: bool | None = None,  # None 跟全局
        reorder_enabled: bool | None = None,  # None 跟全局
    ) -> list:  # 返回处理器列表
        """检索后：重排 → 压缩 → 长上下文重排（可被请求覆盖）。"""  # 方法说明
        return build_node_postprocessors(  # 委托组装
            k,  # Top-N / 条数
            rerank_enabled=rerank_enabled,  # 重排开关
            compress_enabled=compress_enabled,  # 压缩开关
            reorder_enabled=reorder_enabled,  # 重排版开关
        )  # build_node_postprocessors 结束

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
            print("切分后没有节点，跳过写入")  # 提示跳过
            return self.collection.count()  # 返回当前总量

        self.index.insert_nodes(nodes)  # 向量化并写入 Chroma
        self._invalidate_retrieval_cache()  # 索引变了，重建 BM25 / 对话引擎
        total = self.collection.count()  # 当前总量
        print(f"成功添加 {len(texts)} 个文档 / {len(nodes)} 个节点，总计 {total} 个")  # 写入成功日志
        return total  # 返回总量

    def ingest_files(  # 对应讲义 SimpleDirectoryReader
        self,  # 引擎实例
        input_files: List[str] | None = None,  # 指定文件列表
        input_dir: str | None = None,  # 或指定目录
        splitter: str = "sentence",  # 分块模式
    ) -> dict:  # 返回统计字典
        """用 SimpleDirectoryReader 加载本地文件或目录后建索引。"""  # 方法说明
        kwargs: dict = {"required_exts": SUPPORTED_EXTS, "recursive": True}  # 目录模式默认参数
        if input_files:  # 有文件列表时只用文件列表（讲义 input_files 写法）
            text_files = [
                p for p in input_files if Path(p).suffix.lower() in SUPPORTED_EXTS
            ]
            if not text_files:
                return {"loaded_documents": 0, "nodes": 0, "total_documents": self.collection.count()}
            kwargs = {"input_files": text_files}  # 覆盖为仅文件列表
        elif input_dir:  # 指定目录
            kwargs["input_dir"] = input_dir  # 追加目录参数
        else:  # 都没传则用配置里的 DATA_DIR
            kwargs["input_dir"] = DATA_DIR  # 默认数据目录

        reader = SimpleDirectoryReader(**kwargs)  # 创建加载器
        documents = clean_empty_text(reader.load_data())  # 读文件成 Document 列表
        print(f"加载了 {len(documents)} 个文档")  # 加载日志
        nodes = self._splitter(splitter).get_nodes_from_documents(documents)  # 分块
        print(f"切分为 {len(nodes)} 个节点")  # 分块日志
        if nodes:  # 有节点才写入
            self.index.insert_nodes(nodes)  # Embedding + 存 Chroma
            self._invalidate_retrieval_cache()  # 清 BM25 / chat 缓存
        total = self.collection.count()  # 写入后总量
        print(f"向量化和存储完成，文档数: {total}")  # 完成日志
        return {  # 返回统计给 API
            "loaded_documents": len(documents),  # 本次加载文档数
            "nodes": len(nodes),  # 本次切出的节点数
            "total_documents": total,  # 写入后集合总量
        }  # return 结束

    def seed_if_empty(self, texts: List[str] | None = None) -> int:  # 启动时若库空则灌入示例 + data
        """集合为空时写入示例文档，并加载 data 目录中的本地文件。"""  # 方法说明
        if self.collection.count() > 0:  # 已有数据则不重复灌入
            return self.collection.count()  # 直接返回现有总量

        docs = texts if texts is not None else SAMPLE_DOCUMENTS  # 可用自定义文本覆盖示例
        print("正在加载示例文档...")  # 灌入提示
        self.add_documents(docs)  # 写入示例知识（默认 Chroma）

        data_dir = Path(DATA_DIR)  # 默认数据目录
        has_files = data_dir.is_dir() and any(p.is_file() for p in data_dir.rglob("*"))  # 目录里是否有文件
        if has_files:  # 有则再用 SimpleDirectoryReader 导入
            print(f"正在从数据目录加载: {data_dir}")  # 目录导入提示
            self.ingest_files(input_dir=str(data_dir))  # 导入 data 目录
        return self.collection.count()  # 返回最终总量

    def search(self, query: str, k: int = SIMILARITY_TOP_K) -> List[dict]:  # 只检索，不调用大模型
        """只检索：混合召回 + 可选检索后处理，不调用大模型。"""  # 方法说明
        total = self.collection.count()  # 库里有多少条
        if total == 0 or not query or not query.strip():  # 空库或空查询
            return []  # 无结果

        k = min(k, total)  # Top-K 不能超过库容量
        if k == 0:  # 极端兜底
            return []  # 无结果

        retriever = self._build_retriever(k)  # 检索中：向量 / 混合
        results = list(retriever.retrieve(query))  # 粗排候选
        results = apply_postprocessors(results, query, k)  # 检索后：重排/压缩/排版
        formatted_results = []  # 转成 API 友好结构
        for i, item in enumerate(results):  # 逐条格式化
            score = float(item.score or 0.0)  # LlamaIndex 分数
            similarity = round(score, 4)  # 当作相似度展示
            distance = round(max(1.0 - score, 0.0), 4) if 0.0 <= score <= 1.0 else round(1 / (1 + score), 4)  # 近似距离
            formatted_results.append(  # 追加一条结构化结果
                {  # 单条命中字典
                    "rank": i + 1,  # 排名
                    "index": i,  # 下标
                    "document": item.node.get_content(),  # 文本内容
                    "similarity": similarity,  # 相似度
                    "distance": distance,  # 近似距离
                }  # 字典结束
            )  # append 结束
        return formatted_results  # 返回格式化列表

    def query(self, question: str, k: int = SIMILARITY_TOP_K) -> dict:  # 一次性 RAG：检索 + 生成
        """一次性问答：走与 /ask 相同的 AskPipeline，预设 basic。"""
        self._require_llm()
        from semantic_search.app.service.rag_service import RagAskService

        payload = RagAskService(self).ask(
            question,
            k,
            preset="basic",
            use_graph=False,
            use_eval=False,
            use_self_rag=False,
        )
        return {
            "question": payload["question"],
            "answer": payload["answer"],
            "sources": payload["sources"],
        }

    def chat(self, question: str, session_id: str = "default", k: int = SIMILARITY_TOP_K) -> dict:  # 多轮 RAG
        """多轮对话：带 ChatMemoryBuffer；检索侧与 query 共用混合/后处理。"""  # 方法说明
        self._require_llm()  # 没 LLM 就抛错
        # 缓存键带上优化开关，改配置后会重建引擎
        key = (  # backend + session + k + 优化开关组合键
            f"{self.backend_name}:{session_id}:{k}:h{int(HYBRID_ENABLED)}:r{int(RERANK_ENABLED)}"  # 后端、会话、k、混合、重排
            f":c{int(COMPRESS_ENABLED)}:o{int(REORDER_ENABLED)}"  # 压缩、重排版
        )  # key 赋值结束
        if key not in self._chat_engines:  # 首次创建
            memory = self._memories.setdefault(  # 按 session_id 复用记忆
                session_id,  # 会话 ID
                ChatMemoryBuffer.from_defaults(token_limit=10000),  # 记忆 token 上限
            )  # setdefault 结束
            # condense_plus_context 主要吃 similarity_top_k；后处理尽量挂上
            chat_kwargs = dict(  # 创建 chat_engine 的参数
                chat_mode="condense_plus_context",  # 先浓缩问题再带上下文
                memory=memory,  # 多轮记忆
                similarity_top_k=candidate_top_k(k),  # 粗排候选数
                system_prompt=RAG_SYSTEM_PROMPT,  # 系统提示词
            )  # dict 结束
            postprocessors = self._build_postprocessors(k)  # 检索后处理器
            if postprocessors:  # 有处理器才挂上
                chat_kwargs["node_postprocessors"] = postprocessors  # 写入参数
            try:  # 新版 LlamaIndex 支持 node_postprocessors
                self._chat_engines[key] = self.index.as_chat_engine(**chat_kwargs)  # 创建并缓存
            except TypeError:  # 旧版不支持该参数
                # 旧版 LlamaIndex 若不支持 node_postprocessors，降级为仅调大候选
                chat_kwargs.pop("node_postprocessors", None)  # 去掉不兼容参数
                self._chat_engines[key] = self.index.as_chat_engine(**chat_kwargs)  # 降级创建
        response = self._chat_engines[key].chat(question)  # 发本轮消息
        return {  # 组装多轮响应
            "session_id": session_id,  # 回显会话
            "question": question,  # 本轮问题
            "answer": str(response),  # 本轮回答
        }  # return 结束

    def get_stats(self) -> dict:  # 供 /stats、/health 使用
        """返回文档数量、模型名称和持久化路径等状态。"""  # 方法说明
        chroma_n = self.slots["chroma"].count() if "chroma" in self.slots else 0
        qdrant_n = self.slots["qdrant"].count() if self.qdrant_ready else 0
        return {  # 供 /stats、/health 展示
            "total_documents": self.collection.count(),  # 当前选中后端条数
            "chroma_documents": chroma_n,
            "qdrant_documents": qdrant_n,
            "qdrant_ready": self.qdrant_ready,
            "qdrant_error": self.qdrant_error,
            "active_backend": self.backend_name,
            "dimension": "auto",  # 维度由 Embedding 模型决定
            "model_name": self.model_name,  # Embedding 模型
            "embedding_provider": EMBEDDING_PROVIDER,  # Embedding 提供方
            "llm_provider": LLM_PROVIDER,  # LLM 提供方
            "llm_model": self.llm_model,  # LLM 模型名
            "persist_dir": self.persist_dir,  # Chroma 持久化目录
            "qdrant_path": QDRANT_PATH,
            "collection_name": self.collection_name,  # 集合名
            "index_type": f"LlamaIndex + {self.backend_name}",
            "chunk_size": CHUNK_SIZE,  # 分块大小
            "chunk_overlap": CHUNK_OVERLAP,  # 分块重叠
            "data_dir": DATA_DIR,  # 默认数据目录
            "hybrid_enabled": HYBRID_ENABLED,  # 混合检索是否开启
            "rerank_enabled": RERANK_ENABLED,  # 重排是否开启
            "compress_enabled": COMPRESS_ENABLED,  # 压缩是否开启
            "reorder_enabled": REORDER_ENABLED,  # 长上下文重排是否开启
        }  # return 结束

    def clear_documents(self) -> None:  # 清空当前后端知识库
        """删除并重建当前向量后端的集合。"""  # 方法说明
        self.index = self._slot().rebuild_empty_index()
        self._memories.clear()  # 清对话记忆
        self._invalidate_retrieval_cache()  # 清 BM25 / chat_engine 缓存
