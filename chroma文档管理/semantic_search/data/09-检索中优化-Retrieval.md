## 09 检索中优化（Retrieval）
飞书：03-检索中优化（Retrieval）。每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。密码文档目标：提升召回率和相关性。

### 〇、总览：方法地图

#### 目标：提升召回率 Recall + 相关性（少漏、少偏）

#### 两条主线：混合检索（同库多算法） / 多路召回（多源多通道）

#### 胶水：RRF / relative_score 加权 / Round-Robin

#### 落点：都在 RAG 第 4 步「检索召回」；前三步仍是加载→分块→向量化入库

#### 和检索前区别：第 08 章改「问什么」；本章改「怎么查、去哪查」

### 术语定义（本章必背）

#### Retrieval（检索中）：优化「怎么查、用什么算法/通道查」

#### 召回率 Recall：该找到的相关内容里实际找回来的比例（少漏）

#### 精确率 Precision：找回来的内容里真正相关的比例（少脏）

#### 稠密向量：几乎每维都有值，擅长语义/同义匹配

#### 稀疏检索（BM25等）：词面/倒排，擅长专名与编号

#### 混合检索 Hybrid：同库同时跑稠密+稀疏再融合

#### 多路召回 Multi-channel：多源/多索引各自召回再融合

#### RRF：倒数排名融合 score=Σ1/(k+rank)，不要求分数量纲一致

#### relative_score：各路分数归一化后再加权融合

#### Round-Robin：各路轮流取一条，简单保多样性

#### ColBERT：token 级多向量交互（MaxSim），更细更吃资源

#### SPLADE：学习型稀疏向量，兼顾词面与一点语义

### 指标预习：召回率 vs 精确率

#### 适用

##### 开口答「效果不好」前，先分清漏了还是脏了

#### 输入

##### 一次检索返回的候选列表 + 人工标注的相关集合（或抽检）

#### 分步分解

##### Step1 明确相关集合：哪些 chunk 本应被找到

##### Step2 算召回率：相关集合里有多少出现在 Top-K

##### Step3 算精确率：Top-K 里有多少真相关

##### Step4 漏得多 → 优先混合/多路/扩 K；脏得多 → 融合权重、后加重排

#### 输出

##### 口述结论：当前是「召回病」还是「精确病」

#### 完整例子

##### 相关文档 10 篇，Top-5 只中 2 篇 → 召回差，先扩召回手段

##### Top-5 中了 4 篇相关但夹 1 篇无关 → 精确还行，可微调或 rerank

#### 翻车点：只看生成答案对不对，不区分检索阶段指标，会改错模块

### 方法1：混合检索 Hybrid Search

#### 适用：同一知识库里，既有口语/同义表达，又有专名、错误码、型号

#### 输入

##### 同一份 nodes（同一分块结果）

##### 用户查询字符串

##### 稠密 Embedding 模型 + BM25（中文需分词器）

#### 分步分解

##### Step1 全局 Settings.embed_model（如 DashScope text-embedding-v3）

##### Step2 文档 → SentenceSplitter/语义分块 → nodes（两路吃同一份）

##### Step3 稠密路：VectorStoreIndex(nodes).as_retriever(top_k)

##### Step4 稀疏路：BM25Retriever.from_defaults(nodes, tokenizer=jieba)

##### Step5 QueryFusionRetriever([vector, bm25], mode=reciprocal_rerank)

##### Step6 取融合后 Top-N → 交给 RetrieverQueryEngine / LLM

#### 输出

##### 融合后的 NodeWithScore 列表（语义命中 + 关键词命中都可能进榜）

#### 完整例子（登录超时）

##### 单源：只搜产品文档

##### 向量捞到「session 过期」「身份验证失败」

##### BM25 捞到正文含「登录超时」的段落

##### RRF 后两者都可能进入最终 Top-N

#### 讲义代码逐行（混合检索）

##### Settings.embed_model = DashScopeEmbedding(text-embedding-v3)

###### 意思：全局指定稠密向量模型，后面建索引会自动用它

###### 为什么：查询和文档必须同一套 Embedding，否则两路向量不在同一空间

##### docs = [Document(text=t) for t in documents]

###### 意思：把纯字符串包成 LlamaIndex 的 Document

###### 为什么：分块器和索引只认 Document/Node，不认裸字符串

##### splitter = SentenceSplitter(chunk_size=200, chunk_overlap=20)

###### 意思：按句子边界切块，每块约 200 token，相邻块重叠 20

###### 为什么：两路检索必须吃同一份 nodes，切一次就够

##### nodes = splitter.get_nodes_from_documents(docs)

###### 意思：得到检索的基本单位 Node 列表

##### index = VectorStoreIndex(nodes)

###### 意思：对每个 Node 调 embed_model，建成稠密向量索引

##### vector_retriever = index.as_retriever(similarity_top_k=5)

###### 意思：语义路只返回最像的 5 条，不做生成

###### 为什么：top_k 是「这一路的候选窗口」，后面还要和 BM25 融合

##### bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5, tokenizer=...)

###### 意思：用同一批 nodes 建关键词检索器，也取 5 条

###### tokenizer=lambda text: list(jieba.cut(text))

###### 意思：先用 jieba 把中文切成词，BM25 才能按词频打分

###### 为什么：默认英文分词按空格切，中文整句会变成一个 token，BM25 失效

##### QueryFusionRetriever(retrievers=[vector, bm25], mode='reciprocal_rerank')

###### 意思：同一个问题同时问两路，再用 RRF 按名次合成一张榜

###### 为什么：cosine 分和 BM25 分不能直接相加，只比排名更稳

##### RetrieverQueryEngine.from_args(retriever=...)

###### 意思：融合后的片段再拼进 Prompt，交给 LLM 生成

###### 为什么：混合检索只替换第 4 步召回，第 5 步生成不变

#### 翻车点

##### 中文不用 jieba：BM25 把整句当一个词，等于废掉

##### 直接加原始分数：cosine 与 BM25 量纲不同，必须 RRF 或先归一化

##### K 太小：两路都没机会进融合窗口

### 方法2：RRF 融合公式深挖

#### 适用：任意多路检索结果要合成一张公平榜单时

#### 输入

##### 各路已排序的文档列表（只要排名，不要原始分）

#### 分步分解

##### Step1 对每一路，给文档记名次 rank_i（从 1 起）

##### Step2 对每个文档累加 1/(k + rank_i)，默认 k=60

##### Step3 按总分降序截断 Top-N

##### Step4 去重：同一 doc id 只保留一条，分数已是累加结果

#### 输出

##### 跨路可比的综合排名；「两路都靠前」优于「一路第一、一路很差」

#### 完整例子

##### A：稠密2 + 稀疏5 → ≈0.0315

##### B：稠密1 + 稀疏20 → ≈0.0289

##### A 胜出：均衡优于偏科

#### 和 relative_score 对比

##### RRF：只看名次，最稳，工业首选

##### relative_score：先 min-max 归一化再加权，适合「明知 FAQ 更权威就给 1.2 权重」

##### Round-Robin：轮流取各路结果，偏多样性（搜索首页）

#### 翻车点：把 RRF 和「加权平均原始分」当成一回事

### 方法3：多路召回 Multi-channel Retrieval

#### 适用：知识分散在多个库/字段——技术文档、FAQ、社区、工单、手册

#### 输入

##### ≥2 个独立 Document 列表或独立索引

##### 每路一个 Retriever（可向量可 BM25）

##### 同一用户问题

#### 分步分解

##### Step1 分库：按业务切 tech_docs / faq_docs / community_docs…

##### Step2 分索引：每路 VectorStoreIndex 或 BM25Retriever

##### Step3 分检索：QueryFusionRetriever 并发调各路

##### Step4 融合：relative_score 加权 或 reciprocal_rerank

##### Step5 RetrieverQueryEngine 把融合结果交给 LLM

#### 输出

##### 带来源通道 metadata（如 channel=tech/faq）的融合候选

##### 覆盖面大于单库，召回率通常上升

#### 完整例子（讲义三路）

##### 路1 技术文档：稠密向量（长文语义）

##### 路2 FAQ：BM25 + jieba（短问答、关键词强）

##### 路3 社区讨论：稠密向量（口语）

##### 权重示例 [1.0, 1.2, 0.8]：FAQ 略加权

##### 问题「Qwen 部署需要多少显存？」→ 三路都可能贡献片段

#### 讲义代码逐行（三路召回）

##### Settings.embed_model / Settings.llm = DashScope(...)

###### 意思：Embedding 负责检索向量，LLM（如 qwen）负责最后生成

###### 为什么：检索阶段可以不调 LLM；生成阶段才用 qwen3.7-max

##### Document(..., metadata={"id": "...", "channel": "tech"})

###### 意思：每条原文带上来源标签，检索结果能看出出自哪一路

###### 为什么：三路混在一起后，没有 channel 就无法排查是哪库答偏了

##### tech_index = VectorStoreIndex.from_documents(tech_docs)

###### 意思：技术文档单独建一个稠密索引，和 FAQ、社区互不共用

###### 为什么：多路召回的关键是「分库分索引」，不是把所有文档塞进一个库

##### faq_retriever = BM25Retriever.from_defaults(nodes=faq_index.docstore...)

###### 意思：FAQ 这一路不用向量，改用 BM25 抓短问答里的关键词

###### docstore.docs.values() 意思：把索引里已经切好的 Node 拿出来给 BM25

###### tokenizer=jieba 意思：中文 FAQ 也必须先分词

##### community_retriever = community_index.as_retriever(similarity_top_k=3)

###### 意思：社区口语再走稠密向量，每路先各取 3 条

##### QueryFusionRetriever(retrievers=[tech, faq, community], retriever_weights=[1.0, 1.2, 0.8], mode='relative_score', num_queries=1, similarity_top_k=5)

###### retrievers 意思：三路检索器放进同一个融合器，一次 query 并发去搜

###### weights 意思：FAQ 权重 1.2 略高，社区 0.8 略低——你更信哪路就抬哪路

###### mode=relative_score 意思：先把每路分数 min-max 拉到同一尺度再加权

###### 为什么：cosine 大约 0~1，BM25 可以很大，不归一化 FAQ 会霸榜或被淹没

###### num_queries=1 意思：这次不让模型再改写出多个问法，只用用户原句

###### similarity_top_k=5 意思：三路合并去重后，最终只留 5 条给生成

###### use_async=False 意思：教学示例用同步调用，方便单步调试

##### query_engine.query(question) → response.source_nodes / response.response

###### source_nodes 意思：融合后真正喂给模型的片段，可打印 channel 和 id

###### response 意思：模型根据这些片段写出的最终回答

#### 翻车点

##### 路数盲目加到 5+：延迟和费用线性涨，2~3 路通常够

##### 各路 top_k 过大又不融合截断：噪音淹没生成

##### 忘记写 channel/id 元数据：出了错无法追哪一路在捣乱

### 方法4：混合 × 多路 嵌套架构

#### 适用：企业多知识库，且每库内部既有语义又有术语需求

#### 输入

##### 多个数据源；每源内部可再配向量+BM25

#### 分步分解

##### Step1 外层按数据源开多路召回

##### Step2 每一路内部做混合检索（向量+BM25+RRF）

##### Step3 外层再 RRF/加权融合 + 去重

##### Step4 可选：再接 rerank（检索后）压到 Top-3/5

#### 输出

##### 横向覆盖全，纵向每源也准——工业级检索骨架

#### 完整例子

##### 外层：产品文档 / 客服工单 / 技术规范

##### 内层：每库 Hybrid

##### 用户问「登录超时怎么处理」：文档给规范说法，工单给个案经验

#### 翻车点：一上来就上嵌套，Native 单路都没稳——先单库混合，再拆多路

### 方法5：中文 BM25 分词配置

#### 适用：所有要用 BM25 的中文 RAG

#### 分步分解

##### Step1 安装 jieba + llama-index-retrievers-bm25

##### Step2 方案A：tokenizer=lambda t: list(jieba.cut(t))

##### Step3 方案B：def tokenize_text(t): return list(jieba.cut(t)) 再传入

##### Step4 方案C（讲义推荐组合）：language='chinese', skip_stemming=True, 中英 token_pattern

##### Step5 自测：对含专名的短问，看 BM25 是否单独能命中

#### 代码逐行

##### def tokenize_text(text): return list(jieba.cut(text))

###### 意思：输入一整句，输出词列表，例如「登录超时怎么处理」→ ['登录','超时','怎么','处理']

##### tokenizer=tokenize_text

###### 意思：把函数本身交给 BM25，让它在检索时自己去调用

###### 为什么：写成 tokenize_text() 会立刻执行，传进去的是词列表，检索时会报错

##### language='chinese'

###### 意思：停用词表用中文，去掉「的/了/吗」这类无信息词

##### skip_stemming=True

###### 意思：关闭英文词干还原（running→run）

###### 为什么：中文没有词干，开着会乱改字

##### token_pattern=r"(?u)\b\w+\b|[\u4e00-\u9fa5]"

###### 意思：英文按单词切，中文至少按汉字切，避免整句粘成一块

###### 为什么：这是不用 jieba 时的保底切法；有 jieba 时优先用 jieba

#### 输出：稀疏路真正按「词」计分，而不是整句一个 token

#### 翻车点：tokenizer=tokenize_text() 多写了括号——传入的是列表不是函数

### 方法怎么串起来（推荐顺序）

#### 诊断

##### 专名/编号搜不到 → 先上方法1 混合（同库加 BM25）

##### 资料散落多系统 → 再上方法3 多路

##### 两路分数对不齐 → 方法2 RRF；要偏科加权 → relative_score

##### 多库且每库都难搜 → 方法4 嵌套

#### 标准 RAG 五步中的位置

##### 1 加载 2 分块 3 向量化入库 —— 不变

##### 4 检索召回 —— 替换为 Hybrid / Multi-channel / 嵌套

##### 5 喂给大模型之前 —— 接第 10 章 node_postprocessors 三件套

#### 和本仓库

##### 已落地：HYBRID_ENABLED + BM25(jieba) + QueryFusionRetriever(reciprocal_rerank)

##### 代码：retrieval_optimize.build_hybrid_retriever；失败回退纯向量

##### 未做：多目录多路 channel；见第 13 章演进 P4

#### 和第 08 章衔接

##### 先 Pre：清洗/重写/HyDE 得到更好 query

##### 再 Mid：用本章方法去查

##### 再 Post：第 10 章 rerank → 压缩 → 长上下文重排 → 约束生成\n