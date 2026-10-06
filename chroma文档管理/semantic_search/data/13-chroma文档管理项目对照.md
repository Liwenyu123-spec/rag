## 13 chroma文档管理：项目全链路对照
把第 08~12 章方法映射到本仓库搜索引擎。根目录：chroma文档管理/；包：semantic_search/；启动：python chroma文档管理/run.py → http://127.0.0.1:8003/

### 〇、一张总图：用户问一句会发生什么

#### 浏览器 static/index.html → POST /ask {question,k,strategy}

#### main.ask → RagAskService.ask（编排层）

#### Pre：pre_retrieval.prepare_retrieval_queries

#### Mid：engine._build_retriever → 向量±BM25；多 query 则 merge_nodes_rrf

#### Post：retrieval_optimize.apply_postprocessors 三件套

#### CRAG：crag.apply_crag（可改写重跑 Mid+Post）

#### Gen：response_synthesizer + ASK_QA_PROMPT；返回 answer/sources/pre_retrieval/crag

### 术语定义（项目里会碰到的词）

#### Native RAG

##### 定义：最朴素的检索增强：问句→向量检索 Top-K→塞进 Prompt→生成

##### 本项目底座仍是 Native，上面叠了 Pre/Mid/Post/CRAG

#### SemanticSearchEngine

##### 定义：engine.py 中的核心引擎类，管 Embedding/LLM/Chroma/分块/索引/检索

#### RagAskService

##### 定义：/ask 编排层，按 Pre→Mid→Post→CRAG→Gen 串完整作业链路

#### Node / NodeWithScore

##### Node：LlamaIndex 里一块可检索文本（通常=一个 chunk）

##### NodeWithScore：带检索分数的节点，融合/重排会改 score

#### Chunk / 分块

##### 定义：把长文档切成适合 embedding 与召回的小段

##### 本项目：Sentence / Token / Semantic 三种 splitter

#### strategy（检索前策略）

##### 定义：/ask 请求里控制查询怎么预处理的枚举

##### 取值：none / clean / rewrite（默认）/ hyde

#### QueryFusionRetriever

##### 定义：LlamaIndex 多检索器融合器；本项目用它做向量+BM25 同库混合

##### mode=reciprocal_rerank 即按 RRF 融排名

#### BM25

##### 定义：经典稀疏关键词检索算法，擅长专名、编号、精确词面

##### 中文必须配合分词（本项目 jieba）

#### RRF（Reciprocal Rank Fusion）

##### 定义：用「排名倒数」融合多路结果，不依赖原始分数量纲

##### 本项目两处：路内 QueryFusion；多 query 时 merge_nodes_rrf

#### node_postprocessors

##### 定义：检索后、生成前的节点后处理器列表，按顺序串行

##### 本项目三件套：Rerank → 压缩 → LongContextReorder

#### Cross-Encoder / Bi-Encoder

##### Bi-Encoder：查询与文档各自编码再比相似度，快，适合粗召回

##### Cross-Encoder：query+doc 一起进模型打分，准但慢，适合精排

#### SentenceEmbeddingOptimizer（上下文压缩）

##### 定义：按句与查询的相似度裁掉低相关句子，减少噪声与 token

#### LongContextReorder

##### 定义：把最相关片段放到上下文首尾，对抗 Lost in the Middle

#### Lost in the Middle

##### 定义：长上下文里，模型对中间段落记忆/利用率明显低于首尾

#### HyDE

##### 定义：Hypothetical Document Embeddings，先生成假想答案文档再拿去检索

##### 注意：假想文只用于检索，不能当事实引用（本项目 sources 不用它）

#### pre_retrieval / crag（响应字段）

##### pre_retrieval：检索前中间产物（原句/清洗/改写/HyDE/检索列表）

##### crag：Corrective RAG 过程（过滤前后篇数、是否重试、评估明细）

#### Chroma / Collection

##### Chroma：本项目使用的向量数据库

##### Collection：一个命名向量集合（默认 native_rag）

### 一、目录与职责（打开代码用）

#### run.py：启动入口，挂 sys.path 后调 semantic_search.__main__

#### app/main.py：FastAPI 路由 /ask /search /query /chat /ingest /upload …

#### app/engine.py：Embedding/LLM/Chroma/分块/索引；_build_retriever / query / chat

#### app/config.py：模型、分块、HYBRID/RERANK/COMPRESS/REORDER/CRAG 开关

#### app/schemas.py：AskRequest/AskResponse、PreRetrievalInfo、CragInfo

#### app/service/pre_retrieval.py：清洗 / 重写 / HyDE

#### app/service/retrieval_optimize.py：混合召回 + 后处理三件套

#### app/service/crag.py：Corrective RAG 库内修正

#### app/service/rag_service.py：/ask 专用编排（Pre→Mid→Post→CRAG→Gen）

#### static/index.html：问答 UI，展示策略过程、CRAG 过滤、来源卡片

#### data/：默认灌库 md/txt；chroma_db/：向量持久化

### 二、章节 ↔ 模块映射

#### 第 08 检索前 → pre_retrieval.py + /ask?strategy=

##### none：原句单路

##### clean：去口语填充 + 术语表（电脑→笔记本电脑 等）

##### rewrite（默认）：清洗句 + 改写句双路，防改歪

##### hyde：清洗句 + 假想说明文双路；假想文只检索不当引用

##### 前端：pre_retrieval 盒子展示 original/clean/rewritten/hyde_doc

#### 第 09 检索中 → retrieval_optimize.build_hybrid_retriever

##### HYBRID_ENABLED：向量 as_retriever + BM25(jieba) → QueryFusionRetriever

##### 默认 mode=reciprocal_rerank（RRF）；失败回退纯向量

##### 粗排窗口：RETRIEVE_CANDIDATES（默认 20）给精排留余量

##### /ask 多 query：路内融合后再 merge_nodes_rrf 做查询间融合

#### 第 10 检索后 → build_node_postprocessors / apply_postprocessors

##### Rerank：默认本地 SentenceTransformerRerank(bge-reranker-base)

##### RERANK_PROVIDER=dashscope 才走千问 qwen3-rerank

##### 压缩：SentenceEmbeddingOptimizer + 中文切句 + COMPRESS_PERCENTILE

##### 排版：LongContextReorder 对抗 Lost in the Middle

##### query/chat：挂在 RetrieverQueryEngine / chat_engine 的 node_postprocessors

#### 第 11 Self-RAG → 尚未成独立模块

##### 缺口：Retrieve 门控、ISSUP 验据、ISUSE 打分

##### 可借用：CRAG 的相关性过滤 ≈ ISREL

##### 落地建议见第 11 章第九节

#### 第 12 CRAG → crag.py + rag_service 第⑤步

##### 默认开启；全无关改写后 _retrieve_pipeline 重跑

##### 不联网：无 Tavily，属讲义基础版路线

### 三、API 怎么选

#### /ask：作业主链路，带 strategy + pre_retrieval + crag（推荐演示）

#### /search：只检索不生成，看混合/后处理召回效果

#### /query：一次性 RAG，有后处理，无 Pre 多策略、无 CRAG 编排

#### /chat：多轮记忆；后处理挂引擎，会话键含 hybrid/rerank 标志

#### /ingest /upload：灌库；会 _invalidate_retrieval_cache 重建 BM25

#### /stats /health：看库规模与 hybrid_enabled/rerank_enabled 等

### 四、环境变量开关速查（config.py）

#### HYBRID_ENABLED / HYBRID_FUSION_MODE / RETRIEVE_CANDIDATES

#### RERANK_ENABLED / RERANK_PROVIDER(local|dashscope|none) / RERANK_MODEL / RERANK_TOP_N

#### COMPRESS_ENABLED / COMPRESS_PERCENTILE

#### REORDER_ENABLED

#### CRAG_ENABLED / CRAG_VERBOSE

#### CHUNK_SIZE / CHUNK_OVERLAP / SIMILARITY_TOP_K

#### EMBEDDING_* / LLM（DeepSeek 等）/ DASHSCOPE_API_KEY（仅千问路径需要）

#### SEARCH_HOST / SEARCH_PORT（默认 8003）

### 五、和讲义 Advanced 闭环四问对照

#### 查什么 → strategy 重写/HyDE（第 08）

#### 去哪查 → 同库向量+BM25（第 09）；未做多目录多路 channel

#### 查得准 → 本地 bge rerank（第 10）

#### 怎么用 → 压缩+长上下文重排+引用约束；错了再 CRAG 纠（第 10/12）

#### 查不查 → Self-RAG Retrieve 尚未接（第 11 缺口）

### 六、效果不好时：按本项目排查

#### ① /stats 库是否为空；分块是否切断关键句

#### ② 换 strategy：rewrite↔hyde↔clean，看 pre_retrieval 双路是否合理

#### ③ 专名搜不到：确认 HYBRID_ENABLED 与 jieba/bm25 依赖

#### ④ 相关在后面：确认 RERANK_ENABLED 与本地 bge 是否加载成功

#### ⑤ 答案飘：看压缩是否过猛；Prompt 是否仍「仅依据上下文」

#### ⑥ CRAG 滤光：看 crag.eval；必要时 CRAG_VERBOSE 对照终端

#### ⑦ 延迟：降 k/候选；关 CRAG 或压缩做 A/B

### 七、建议的下一刀改造（优先级）

#### P0：Self-RAG Retrieve 门控（闲聊不查）

#### P1：生成后 ISSUP 验据 + 不足则重写

#### P2：CRAG strip 级 Knowledge Refinement（对齐论文 Correct 路径）

#### P3：可选 Web 补充（仅公网场景；内网知识库慎开）

#### P4：多目录多路召回 + channel 元数据（第 09 进阶）

#### P5：接第 14 章评估闭环——开关 A/B + Hit/MRR/Faithfulness 回归\n