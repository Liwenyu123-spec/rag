## 06 Native RAG（基础RAG）
飞书文档：01-Native_RAG（基础RAG）https://ecnwvcdzorsp.feishu.cn/docx/WAyydkEX2o81xAxFkn1cJRqqnnY

### 术语定义（本章必背）

#### Native RAG：基础 RAG 流水线——加载→分块→向量化入库→检索 Top-K→拼 Prompt→生成

#### Indexing（索引/入库）：文档切块并 Embedding 后写入向量库

#### Search / Retrieval：问题向量化后召回最相关块

#### Generate：把检索块作为上下文，由 LLM 生成回答

#### Chunk / 分块：把长文档切成适合检索的小段

#### SentenceSplitter：按句子/长度切块（本仓库默认之一）

#### TokenTextSplitter：按 token 数切块

#### SemanticSplitter：按语义相似度变化点切块

#### LlamaIndex：本课程主用的 RAG 编排框架

#### VectorStoreIndex：LlamaIndex 中基于向量库的索引对象

#### RetrieverQueryEngine：检索器 + 响应合成器组成的问答引擎

#### ChatEngine：带多轮记忆的 RAG 对话引擎

#### Top-K / similarity_top_k：返回相似度最高的前 K 条

#### 数据质量：垃圾进垃圾出——脏文档会直接拖垮 RAG 效果

#### 本项目入口：python chroma文档管理/run.py → http://127.0.0.1:8003/

### 一、技术原理

#### 1 为什么需要RAG
大模型的局限性

##### 知识时效性：无法实时获取最新数据，如 GPT-3 知识停在 2021

##### 幻觉问题：基于概率生成，Prompt 上限即回答有效性上限

##### 垂直领域覆盖不足：医疗等行业资料多为机密，通用模型吃不到

#### 2 RAG原理（Native RAG 三步）

##### Indexing：文档向量化，写入向量库建索引

##### Search：问题 Embedding 后检索最相关文档片段

##### Generate：把片段塞进 Prompt，由 LLM 生成可读回答

### 二、RAG流程

#### 大致分三个阶段：数据准备 → 检索 → 生成（讲义有总流程图）

### 三、数据准备阶段

#### 1 数据准备

##### 原始数据常有：格式难识别、内容不一致、不完整、不合法

##### 第一性原理：加上下文能提准确性，但数据质量差会负向影响

#### 2 向量化 Embedding

##### 向量检索按语义相似度找内容，保障输出有效性

##### 选型可参考 MTEB Leaderboard：huggingface.co/spaces/mteb/leaderboard

##### 本地下载模型

###### HuggingFace：可设 HF_ENDPOINT=https://hf-mirror.com 镜像

###### hf download BAAI/bge-base-zh-v1.5 --local-dir ...

###### 环境变量 HF_HOME / TRANSFORMERS_CACHE 统一缓存目录

###### 国内更快：pip install modelscope 后 modelscope download

#### 3 知识存储

##### 向量化后写入向量库，不要只把向量扔内存里

##### 必须建立 embedding ↔ chunk 原文的映射，检索到向量才能拿出文本

##### 再记下 metadata：来源文件、页码、切分方式，方便引用和过滤

##### 本仓库落盘目录：semantic_search/chroma_db

### 四、LlamaIndex 的 RAG

#### 1 LlamaIndex 简介

##### 1.1 介绍

###### 原名 GPT Index，面向 LLM 的数据开发与编排框架

###### 打通私有数据与通用大模型：加载→切分→向量化→检索→生成

###### 可用极少代码接入文档、数据库、API，快速做生产级 RAG

##### 1.2 核心概念速览

###### Document：一篇原始文档，带 metadata（来源、文件名）

###### Node：切出来的块，检索的基本单位

###### Index：把 Node 编成可检索结构，课上主要是向量索引

###### Retriever：只负责找回 Node，不生成答案

###### QueryEngine：检索 + 拼 Prompt + 调用 LLM，一次问答

###### ChatEngine：QueryEngine + Memory，多轮对话

#### 2 文档加载

##### 2.1 SimpleDirectoryReader

###### 核心包内置通用加载器

###### 自动识别 .txt .pdf .docx .csv .md 等

###### 可 input_dir + recursive + required_exts 加载整目录

###### 可 input_files=[...] 加载指定文件列表

###### load_data() 得到 Document 列表，可看 metadata 与 text 预览

##### 2.2 专用加载器 llama-index-readers-file

###### pip install llama-index-readers-file，20+ 种精细解析

###### PDF

###### PDFReader：轻量，底层 pypdf，适合纯文本

###### PyMuPDFReader：高性能，特性更多

###### UnstructuredReader：擅长表格、标题等复杂结构

###### 依赖可选：unstructured[pdf]、PyMuPDF

###### 用 SimpleDirectoryReader 的 file_extractor={'.pdf': parser}

###### Word / PPT / CSV

###### DocxReader、PptxReader、PandasCSVReader

###### Word 常需 pip install docx2txt

###### Markdown / HTML / 代码 / 笔记

###### MarkdownReader：保留标题层级

###### HTMLTagReader、IPYNBReader、XMLReader

###### IPYNB 可装 nbconvert

###### 加载器选择：按格式选专用；通用杂糅文件先用 SimpleDirectoryReader

#### 3 文档分块

##### 3.1 基础切分器

###### TokenTextSplitter

###### 按 Token 数切分，严格控制上下文窗口

###### 先用 separator（如句号）切；超长再用 backup_separators

###### 仍超长则硬截断；最后合并并加 overlap

###### SentenceSplitter（默认推荐）

###### 优先保证句子完整，同时控制 chunk_size

###### 步骤1：paragraph_separator（默认\n\n\n）按段落切

###### 步骤2：secondary_chunking_regex 切成完整句子

###### 步骤3：累加句子直到接近 chunk_size 成一块

###### 步骤4：下一块带上上块末尾 overlap 句子

###### 单句本身 > chunk_size 时可能报错，需预处理

##### 3.2 语义切分 SemanticSplitterNodeParser

###### 先分句 → 组合成组合句 → Embedding 算相似度 → 按阈值切

###### buffer_size=1：组合句约含前后各1句+当前句

###### breakpoint_percentile_threshold 越高，切得越粗

###### 中文需自定义 chinese_sentence_splitter（。！？!?\n）

###### 可配 DashScopeEmbedding(text-embedding-v3)

###### 注意：需过滤空文本 clean_empty_text；参数要调优

##### 3.3 选择建议

###### 常规 RAG：SentenceSplitter，平衡上下文与精度

###### 长文要语义连贯：SemanticSplitterNodeParser

###### 代码库：CodeSplitter，避免切断函数中间

###### 句子级精确检索：SentenceWindowNodeParser + MetadataReplacementPostProcessor

#### 4 文档向量化并存储 Embedding

##### pip install llama-index-vector-stores-chroma

##### Settings.embed_model = DashScopeEmbedding(model_name=text-embedding-v3, text_type=document)

##### SimpleDirectoryReader 加载 → SentenceSplitter 分块

##### Chroma PersistentClient + get_or_create_collection

##### ChromaVectorStore → StorageContext → VectorStoreIndex(nodes)

##### 执行顺序：Index 遍历 node → embed_model 生成向量 → collection.add 写入

##### 千问限制：单条 ≤8192 tokens；batch size ≤10

#### 5 检索与大模型回复

##### 重新挂 Settings.embed_model（须与建库同一模型）

##### PersistentClient → get_collection → ChromaVectorStore

##### VectorStoreIndex.from_vector_store 恢复索引

##### as_query_engine：一次性检索+生成

##### as_chat_engine(chat_mode=condense_plus_context) + ChatMemoryBuffer：多轮

##### 项目落地：semantic_search 的 /search /query /chat /ingest

#### 6 对照本仓库 semantic_search 怎么用
讲义流程已接到 FastAPI + 前端

##### Indexing：前端上传 /upload 或 POST /ingest → data 目录 → 分块入库

##### 分块可选：sentence（推荐）/ token / semantic

##### Embedding：默认本地 bge-small-zh；有千问 Key 可改 dashscope

##### Search：前端「语义搜索」或 GET/POST /search

##### Generate：前端「一次性问答」/query、「多轮问答」/chat

##### 持久化目录：semantic_search/chroma_db

##### 启动：python chroma文档管理/run.py → http://127.0.0.1:8003/

#### 7 代码详解 engine.py / main.py（chroma文档管理）
对应 chroma文档管理/semantic_search/。每条：代码 → 它在流水线哪一步 → 得到什么。

##### 启动 lifespan

###### SemanticSearchEngine()

###### 意思：一次性挂好 Embedding、LLM、Chroma、空/旧索引

###### 缺 API Key 时引擎可为 None，页面能开，/query 会 503

###### seed_if_empty()

###### 意思：库是空的才灌示例文档 + 扫描 data 目录

###### 为什么：第一次启动就能搜，不用手工入库

##### 入库：文件 → 块 → 向量

###### SimpleDirectoryReader(...).load_data()

###### 意思：把 PDF/TXT/MD 等读成 Document 列表

###### 每个 Document 带 text + metadata（文件名等）

###### clean_empty_text(docs)

###### 意思：丢掉空内容，避免后面 embedding 报错

###### splitter.get_nodes_from_documents(docs)

###### 意思：切成 Node（检索的基本单位=chunk）

###### sentence/token/semantic 三种切法由 _splitter(mode) 决定

###### index.insert_nodes(nodes)

###### 意思：对每个 Node 调 embed_model 得向量，再写入 Chroma

###### 之后要 _reset_chat_engines()：知识变了，旧多轮引擎不能继续用

##### 三种分块器（构造时在说什么）

###### SentenceSplitter(chunk_size, chunk_overlap, ...)

###### 意思：尽量按句子边界凑满约 chunk_size 个 token

###### overlap：下一块带上上块尾巴，防止关键句被切断

###### TokenTextSplitter(...)

###### 意思：严格按 token 数切，控制上下文更硬

###### SemanticSplitterNodeParser(buffer_size=1, breakpoint=95, ...)

###### 意思：算相邻句向量相似度，主题一变就切开

###### 更慢但语义更整；中文要自定义分句函数

##### 只检索 search（不调大模型）

###### retriever = index.as_retriever(similarity_top_k=k)

###### 意思：只要「找片段」的工具，不做生成

###### results = retriever.retrieve(query)

###### 意思：返回 NodeWithScore 列表

###### item.node.get_content() → 原文；item.score → 相似度

###### 对应接口：GET/POST /search

##### 一次性问答 query

###### engine = index.as_query_engine(similarity_top_k=k)

###### 意思：检索 + 拼 Prompt + 调 LLM，一条龙

###### response = engine.query(question)

###### str(response) → 给用户的答案文字

###### response.source_nodes → 引用了哪些片段（可展示来源）

###### 对应接口：GET/POST /query

##### 多轮问答 chat

###### as_chat_engine(chat_mode='condense_plus_context', memory=..., ...)

###### condense_plus_context 意思：先把「结合上文的问题」改写成独立问句，再检索

###### 为什么：用户说「那扣多少」时，检索要用改写后的完整问题

###### memory 按 session_id 复用

###### 意思：同一浏览器会话共用一块记忆

###### 换 session_id = 新对话；对应 POST /chat

##### 重启后如何找回索引

###### collection.count() > 0 → VectorStoreIndex.from_vector_store(...)

###### 意思：Chroma 里已有向量，挂上去就能搜，不必重切分

###### 空库 → VectorStoreIndex(nodes=[], storage_context=...)

###### 意思：先占个空索引，以后 insert_nodes 再往里填

###### 铁律：Settings.embed_model 必须和建库时同一个\n