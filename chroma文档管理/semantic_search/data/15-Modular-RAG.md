## 15 Modular RAG（模块化）
飞书：01_Modular RAG
https://ecnwvcdzorsp.feishu.cn/docx/DpNhdZLgRoqBGZxwdQfch7DFnRe
Gao 综述：把固定流水线变成可插拔、可编排的模块框架；课堂 demo01_modular_rag.py + 本仓库 presets / RagAskService。

### 〇、总览

#### 一句话：像搭积木一样组合查询改写、多路检索、融合、重排、压缩，用配置控制顺序与启停

#### 论文：Gao et al. Retrieval-Augmented Generation for Large Language Models: A Survey（2023/2024）

#### 从「一条固定流水线」走向「可编排框架」（orchestration）

#### 作业落点：chroma文档管理 的预设 + 勾选 = 线性可插拔 Modular RAG

### 术语定义（本章必背）

#### Modular RAG：把 RAG 拆成独立、可插拔、可重配置模块的架构范式

#### Orchestration（编排）：用流程控制模块的执行顺序、条件与分支

#### Module Type（模块类型）：Pre-Retrieval / Retrieval / Post-Retrieval / Generation

#### Module（模块）：类型下的功能单元，如 Hybrid Search、Rerank、Compress

#### Operator（算子）：模块下可替换实现，如 DashScopeRerank vs 本地 bge

#### Naive RAG：查询→向量检索→生成，无前后优化

#### Advanced RAG：在固定线性上加检索前/后优化（改写、重排、压缩）

#### QueryFusionRetriever：LlamaIndex 多路融合器，常用 RRF（reciprocal_rerank）

#### Multi-Query：LLM 生成多个查询变体再检索融合（num_queries>1）

#### HyDE：先写假想答案文档再检索；假想文不当事实引用

#### PRESETS：basic / hybrid_search / advanced / full_optimization 一键组合

### 第一部分：理论介绍

#### 1.1 什么是 Modular RAG？

##### 拆分：独立 + 可插拔 + 可重配置

##### 对比传统「向量检索 + 生成」：可增删替换模块，不绑死顺序

##### 三代对照（讲义示意图）

###### Naive RAG：查询 → 向量检索 → 大模型 → 答案

###### Advanced RAG：查询 →[检索前/改写]→ 向量检索 →[重排/压缩]→ 大模型 → 答案

###### Modular RAG：查询 →[改写]→[多路检索]→[融合]→[重排]→[压缩]→[生成]；中间可按配置增删换序

#### 1.2 RAG 的三个发展阶段

##### 第一代 Naive RAG（朴素）

###### 特征：检索 → 生成，一条直线流水线

###### 局限：检索质量差、召回不准、上下文冗余、易幻觉

##### 第二代 Advanced RAG（高级）

###### 特征：检索前后加入优化——查询改写、分块、重排、压缩

###### 局限：流程仍是固定线性，难以针对不同查询动态调整

##### 第三代 Modular RAG（模块化）

###### 特征：模块化 + 可编排；支持新模块、条件/分支/循环/自适应

###### 代价：工程复杂度更高，需要编排框架支撑

##### 两个关键突破

###### 新模块 New Modules：Search / Memory / Routing / Predict / Task Adapter 等

###### 新模式 New Patterns：条件、分支、循环、自适应（Rewrite-Retrieve-Read、Recursive、Self-RAG 等）

#### 1.3 核心模块（讲义落地的那一组）

##### Indexing：文档→切块→向量索引

##### Query Transformation：HyDE / Multi-Query / 清洗重写

##### Retrieval：稠密向量 + 稀疏 BM25（jieba）

##### Fusion：RRF / relative_score / simple

##### Reranking：Cross-Encoder 精排

##### Compression：句子级上下文压缩

##### Generation：RetrieverQueryEngine / synthesizer + LLM

##### 综述里还可有：多源 Search、Memory、Routing、Predict、Task Adapter（本仓库未全做）

#### 1.4 三层抽象：模块类型 → 模块 → 算子

##### 模块类型：Pre-Retrieval / Retrieval / Post-Retrieval / Generation

##### 模块：Query Transformation、Hybrid Search、Rerank、Compress …

##### 算子：同一模块换实现——HyDE vs Multi-Query vs Step-Back；DashScopeRerank vs SentenceTransformerRerank

##### 例子：Pre-Retrieval → Query Transformation → {HyDE, Multi-Query, Step-Back}

##### 工程含义：换重排算法、加一路检索 = 插拔算子，不必重写整条流水线

#### 1.5 编排：RAG Flow 的典型模式

##### 线性 Linear：改写→检索→融合→重排→压缩→生成（demo /ask 主路径）

##### 条件 Conditional：先路由——闲聊直接答、知识题才检索（本仓库 Self-RAG Retrieve）

##### 分支 Branching：多路检索/多数据源并行再融合（向量+BM25）

##### 循环 Loop：检索→生成→评估，不行就改写再检（CRAG、Self-RAG ISSUP）

##### 讲义主类先落地「线性可插拔」：config 开关启停，不改主流程代码

#### 1.6 模块化设计的优势

##### 可组合性：混合+重排，或纯向量

##### 可扩展性：新加一路检索器不影响其余模块

##### 可替换性：换 embedding / rerank 算子

##### 可测试性：模块可独立测、独立评估（接第 14 章）

##### 可优化性：针对瓶颈模块专项优化

### 第二部分：LlamaIndex 完整实现（= demo01_modular_rag.py）
讲义用 DashScope；本仓库问答默认可 DeepSeek，向量可本地 bge / 千问 SafeDashScopeEmbedding。

#### 能力清单（讲义打勾项）

##### jieba 中文分词 BM25

##### HyDE / Multi-Query

##### 向量 + BM25 多路

##### QueryFusionRetriever RRF

##### 重排（讲义 DashScopeRerank；本仓库默认可本地 bge）

##### SentenceEmbeddingOptimizer 压缩

##### RetrieverQueryEngine + LLM 生成

##### 配置驱动模块开关

#### 2.1～2.2 环境与全局配置

##### pip：llama-index-core、bm25、jieba；可选 dashscope embedding/llm/rerank

##### Settings.embed_model + Settings.llm

##### SafeDashScopeEmbedding：每批≤10，避开千问批量硬限制

##### LLM temperature 宜偏低，便于改写/判断稳定

#### 2.3 Indexing

##### Document → SentenceSplitter → VectorStoreIndex

##### nodes 要留给 BM25 复用，避免重复分块

##### 本仓库：engine.py 切块写入 Chroma

#### 2.4 Retrieval：向量 + BM25

##### 路1：index.as_retriever 稠密语义

##### 路2：BM25Retriever + jieba.cut 关键词

##### 本仓库：retrieval_optimize.build_hybrid_retriever

#### 2.5 Fusion + Multi-Query

##### QueryFusionRetriever(retrievers, mode, num_queries)

##### num_queries=1：只多路融合；>1：再生成查询变体

##### mode：reciprocal_rerank（RRF）/ relative_score / simple

##### 本仓库：AskRequest.num_queries + fusion_mode

#### 2.6 HyDE

##### 讲义：HyDEQueryTransform(include_original=True) 包一层 TransformQueryEngine

##### 本仓库：strategy=hyde，清洗句+假想文档双路检索，假想文不进 sources

#### 2.7～2.8 重排与压缩

##### node_postprocessors 串行：先精排再压缩

##### 讲义重排：DashScopeRerank(qwen3.7-text-rerank)

##### 压缩：SentenceEmbeddingOptimizer + 中文分句；percentile_cutoff=0.5

##### 本仓库另加 LongContextReorder（对抗 Lost in the Middle）

#### 2.9 ModularRAG 主类 + PRESETS

##### index_documents：Indexing → 两路检索 → Fusion → postprocessors → QueryEngine → 可选 HyDE 外包

##### query()：query_engine.query，打印 source_nodes 与答案

##### basic：simple 融合，关重排/压缩/HyDE

##### hybrid_search：RRF，关后处理

##### advanced：num_queries=3 + 重排 + 压缩

##### full_optimization：再开 HyDE

##### 本仓库 presets.py 同名四档，并映射 use_pre/CRAG 等作业开关

#### 2.10 调用测试：preset=full_optimization，对示例库问 RAG/Python/ML/BM25

### 第三部分：用配置驱动模块编排

#### 3.1 代码字典控制逻辑

##### 三个模块类：检索前 / 检索中 / 检索后，各自只干一类事

##### 主类按 config 字典 if 开关组装，不写死流水线

##### 调用文件只传配置 + 提问

#### 3.2 完整案例目录（讲义 rag_tools）

##### shared.py：共享 LLM/Embedding/工具

##### before_refine.py：检索前

##### middle_refine.py：检索中

##### after_refine.py：检索后

##### rag_main.py：主类编排

##### main.py：入口

##### 对照本仓库

###### before ≈ pre_retrieval.py

###### middle ≈ retrieval_optimize.build_hybrid_retriever

###### after ≈ apply_postprocessors + crag/self_rag

###### rag_main ≈ rag_service.RagAskService

###### main ≈ app/main.py + static/index.html 勾选

#### 3.3 YAML 读配置

##### 讲义：YAML 描述开关，代码读取后交给主类

##### 本仓库：.env（HYBRID/RERANK/…）+ 请求体 JSON 覆盖 + 前端预设

#### 3.4 强类型配置类

##### 讲义：dataclass / 类型化 Config，减少字典拼写错误

##### 本仓库：Pydantic AskRequest / OptimizeFlags（OpenAPI 即文档）

### 对照 chroma文档管理（交作业用）

#### 线性可插拔：/ask 按勾选组装，对应讲义 ModularRAG

#### 条件：Self-RAG Retrieve 闲聊不检索

#### 分支：向量+BM25 融合

#### 循环：CRAG 改写重检；ISSUP 不足则重写答案

#### 预设四档名称与 demo01 对齐，full_optimization 本仓库还叠了 CRAG

#### 未按讲义做：YAML 配置文件、Step-Back 算子、TransformQueryEngine 外包 HyDE

#### 多出来：Chroma 持久化、Web 勾选、CRAG、Self-RAG、Hit/MRR 评估

#### 演示：页面选 full_optimization 或 advanced，看「本次优化」标签讲模块插拔\n