## 10 检索后优化（Post-retrieval）
飞书：04-检索后优化（Post-retrieval）。每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 代码意思 → 翻车点。

### 〇、总览：方法地图

#### 目标：召回结果送入 LLM 前，做重排 + 精简 + 重排版，抬生成质量

#### 位置：第 4 步检索召回之后、第 5 步喂模型之前

#### 入口：node_postprocessors=[...]，按列表顺序串行加工 nodes

#### 三件套：Rerank → SentenceEmbeddingOptimizer → LongContextReorder

#### 和第 08/09 章：前改问句、中改召回；本章改「怎么用召回结果」

### 术语定义（本章必背）

#### Post-retrieval（检索后）：召回之后、喂 LLM 之前加工候选

#### Node Postprocessor：对 NodeWithScore 列表串行后处理的组件

#### Re-ranking：用更准模型对粗召回候选二次打分排序

#### 两阶段检索：粗召回（快广）+ 精排（慢准）

#### Bi-Encoder：查询/文档各自编码再比相似度，快

#### Cross-Encoder：query+doc 一起进模型打分，准但慢

#### 上下文压缩：只留与问题最相关的句子，丢掉冗余

#### SentenceEmbeddingOptimizer：按句-查询相似度裁剪的压缩器

#### LongContextReorder：最相关放首尾，对抗中间遗忘

#### Lost in the Middle：长上下文中模型对中间段落利用率偏低

#### Citation：答案标明来源，便于核查并抑制瞎编

### 方法1：两阶段检索与重排序 Re-ranking

#### 适用：粗召回有相关材料，但 Top-3/5 常被「沾边噪声」占坑

#### 输入

##### 用户问题 + 粗排候选（如 similarity_top_k=20~100）

##### 精排模型：API（DashScopeRerank）或本地 Cross-Encoder

#### 分步分解

##### Step1 Bi-Encoder/向量检索：快，从海量库捞 Top-N 候选

##### Step2 Cross-Encoder/Rerank：query+doc 一起打分，只精排候选

##### Step3 截断 top_n（常 3/5）交给生成

##### Step4（可选）后面再接压缩与长上下文重排

#### 输出

##### 按精排分排序的短名单；精确率↑，喂给模型的噪声↓

#### 完整例子（超市红烧肉）

##### 粗排：五花肉、酱油…也抓回红烧牛肉面、红烧鱼料——快但乱

##### 精排：逐个判断，真正做红烧肉必备的顶到最前

##### 口诀：先广撒网，再精挑细选

#### 原理口述

##### Bi-Encoder：查询/文档各自编码再比余弦，文档可离线预计算

##### Cross-Encoder：拼接后深层交互直接出相关性分，准但慢

##### 只用双塔：Top-5 易混入沾边货；只用交叉：百万库打不动

##### 两阶段 = 工业标准粗召回 + 精排

#### 讲义代码逐行（重排序）

##### pip：方式A dashscope-rerank / 方式B sentence-transformers

###### 意思：A 走 API 重排；B 本机加载 Cross-Encoder

###### 为什么：有网用 A 省事；内网/离线用 B

##### Settings.embed_model = DashScopeEmbedding(text-embedding-v3)

###### 意思：第 1 阶段粗排仍用同一套稠密向量模型

###### 为什么：查询向量和库里文档向量必须同一空间

##### index = VectorStoreIndex.from_documents(docs)

###### 意思：建库时就把每条 Document 向量化进索引

##### retriever = index.as_retriever(similarity_top_k=6)

###### 意思：Bi-Encoder 粗排，先捞 6 条候选（教学示例；生产常 20~50）

###### 为什么：要给第 2 阶段留「可选余地」，不能一上来就只留 3 条

##### DashScopeRerank(model="qwen3-rerank", top_n=3, api_key=...)

###### 意思：把粗排候选交给重排模型，query+doc 交互打分，只留 Top-3

###### top_n 意思：精排后的截断长度，也是最终进 Prompt 的条数上限

###### 注意：讲义旧名 gte-rerank 可能下线，以控制台当前模型名为准

##### SentenceTransformerRerank(model=..., top_n=3)

###### 意思：本地 Cross-Encoder 替代 API，接口同样挂到 node_postprocessors

###### 为什么：无外网、要控数据不出域时用

##### as_query_engine(similarity_top_k=6, node_postprocessors=[reranker])

###### 意思：引擎内部先 retrieve(6) → 再跑 reranker → 再拼 Prompt 调 LLM

###### 为什么：重排是「后处理器」，不改索引，只改召回结果名单

##### for n in response.source_nodes: print(n.score, n.text)

###### 意思：看精排后的分数与正文，确认噪声是否被挤出 Top

#### 翻车点

##### 粗排 top_k=3 再 rerank：精排几乎无事可做

##### 对全库跑 Cross-Encoder：延迟炸裂

##### 把 RRF 融合和 Cross-Encoder 精排当成同一步

### 方法2：上下文压缩 SentenceEmbeddingOptimizer

#### 适用：相关片段很长，里面夹杂天气/CI/CD/闲聊等噪声句

#### 输入

##### 已召回（最好已重排）的 nodes + 同一查询

#### 分步分解

##### Step1 把每个片段拆成句子（中文可用正则按。！？；切）

##### Step2 每句与查询算 embedding 相似度

##### Step3 percentile_cutoff / threshold_cutoff 丢掉低分句

##### Step4 只把保留句子拼回片段，再喂 LLM

#### 输出

##### 更短、更贴题的上下文；token↓、噪声↓、幻觉风险↓

#### 完整例子

##### 压缩前：显存要求夹在「办公自动化」「今天天气不错」中间

##### 压缩后：只留「Qwen2.5 最低 16GB 显存…」等相关句

#### 讲义代码逐行（上下文压缩）

##### 故意造「长片段+噪声」Document

###### 意思：同一段里混入显存要点和「天气/CI/CD」废话，方便观察裁剪效果

##### def chinese_sentence_splitter(text): re.split(...); return [s.strip() for s in ... if s.strip()]

###### 意思：按。！？；和换行把中文切成句子列表

###### 为什么：默认英文切句器遇中文常切不动或切错

##### SentenceEmbeddingOptimizer(embed_model=..., percentile_cutoff=0.5, tokenizer_fn=chinese_sentence_splitter)

###### 意思：每句与查询算 embedding 相似度，只留排名前 50% 的句子

###### percentile_cutoff 意思：按相对名次裁；threshold_cutoff 意思：按绝对分数裁

###### tokenizer_fn 意思：告诉优化器用你的中文切句函数

##### as_query_engine(..., node_postprocessors=[optimizer])

###### 意思：召回后先裁句，再把瘦身后的片段喂给 LLM

###### 为什么：不改索引内容，只改「这一次」送给模型的文本

##### 对比打印压缩前 retrieve() vs 压缩后 source_nodes

###### 意思：肉眼检查「天气不错」等噪声句是否被删掉

#### 和重排的关系

##### 重排：选哪些块、谁排前

##### 压缩：块里留哪几句

##### 常配合：先重排，再压缩

#### 翻车点：cutoff 过严，相关句也被裁光；过松等于没压缩

### 方法3：长上下文重排 LongContextReorder

#### 适用：喂给模型的片段较多/较长，担心中间内容被忽略

#### 输入

##### 已排序的 nodes（通常来自 reranker，相关度从高到低）

#### 分步分解

##### Step1 认识 Lost in the Middle：首尾易记、中间易丢

##### Step2 调用 LongContextReorder()（无构造参数）

##### Step3 把最相关挪到列表头尾，次相关塞中间

##### Step4 不改文本内容、不改选集，只改排列

#### 输出

##### 同一批片段，但顺序更贴合 LLM 注意力分布

#### 完整例子

##### rerank 后：1>2>3>4>5 相关度递减

##### reorder 后：最高分在首尾，较低分在中间

#### 讲义代码逐行（长上下文重排）

##### from llama_index.core.postprocessor import LongContextReorder

###### 意思：导入「只改顺序、不改内容」的后处理器

##### reranker = DashScopeRerank(model="qwen3-rerank", top_n=5, api_key=api_key)

###### 意思：先精排出 Top-5，默认相关度从高到低

##### reorder = LongContextReorder()

###### 意思：实例化排版器，构造函数无参数

###### 为什么：策略固定——最相关放首尾，次相关塞中间

##### as_query_engine(similarity_top_k=8, node_postprocessors=[reranker, reorder])

###### 意思：粗召回 8 → rerank 留 5 → reorder 重排版 → 再生成

###### 列表顺序=执行顺序：必须先精排再排版，不能写反

##### 观察 source_nodes 顺序

###### 意思：最高分应出现在列表头部和尾部，中间是次相关

###### 为什么：对抗 Lost in the Middle，让模型更吃首尾信息

#### 翻车点：片段很少（≤3）时收益有限；别指望它能「救回」没召回的内容

### 方法4：三件套串成完整检索后链

#### 适用：要上工业级 Post-retrieval 默认链路时

#### 分步分解

##### Step1 粗召回 similarity_top_k 调大（如 8~50）

##### Step2 DashScopeRerank / Cross-Encoder → top_n

##### Step3 SentenceEmbeddingOptimizer 裁句

##### Step4 LongContextReorder 首尾排版

##### Step5 LLM 生成；Prompt 约束仅依据资料 + 引用

#### 推荐挂法

##### node_postprocessors=[reranker, compressor, reorder]

##### 口诀：先选块 → 再削句 → 最后排版

#### 讲义代码逐行（三件套完整链）

##### Settings.embed_model / Settings.llm = DashScope(...)

###### 意思：embedding 服务检索与压缩相似度；llm 只负责最后生成

##### reranker = DashScopeRerank(..., top_n=5)

###### 意思：第 1 环——决定哪些块留下、谁更相关

##### compressor = SentenceEmbeddingOptimizer(percentile_cutoff=0.5, tokenizer_fn=...)

###### 意思：第 2 环——块内去噪声句，缩短上下文

##### reorder = LongContextReorder()

###### 意思：第 3 环——把高相关块挪到首尾

##### as_query_engine(similarity_top_k=20, node_postprocessors=[reranker, compressor, reorder])

###### 意思：一次 query 走完：粗召回→精排→裁句→排版→生成

###### 为什么写这个顺序：先决定「要哪些块」，再「削句子」，最后「摆位置」

###### 写反会怎样：先 reorder 再 rerank＝排版结果又被打乱；先压缩再 rerank＝在噪声块上白算相似度

##### response.source_nodes / response.response

###### source_nodes 意思：最终真正进 Prompt 的片段（已精排+已压缩+已排版）

###### response 意思：模型基于这条加工后的上下文写出的答案

#### 输出

##### 短、准、好读的上下文，生成更稳、更省 token

#### 翻车点

##### 三件套一次全开却不评测：延迟↑费用↑，先只上 rerank

##### 顺序挂反：先 reorder 再 rerank 失去精排意义

### 方法怎么串起来（推荐顺序）

#### 诊断

##### 相关材料在后面几名 → 方法1 重排

##### 材料对但废话多/超窗口 → 方法2 压缩

##### 片段多、答案漏中间要点 → 方法3 长上下文重排

##### 要完整工业链 → 方法4 三件套

#### 和本仓库

##### 已落地三件套：本地 bge-reranker → SentenceEmbeddingOptimizer → LongContextReorder

##### 代码：retrieval_optimize.build_node_postprocessors；/ask 走 apply_postprocessors

##### 默认不依赖千问重排；RERANK_PROVIDER=dashscope 才用 API

#### 和第 08/09 章衔接

##### Pre（08）改问句 → Mid（09）混合/多路召回 → Post（10）三件套 → 生成

##### 召回上限由 08/09 决定；本章抬的是「已召回材料的利用率」

#### 五、小结（讲义）

##### 重排：抬精确率

##### 压缩：降噪声与 token

##### 长上下文重排：对抗 Lost in the Middle

##### 三者都通过 node_postprocessors 接入，是工业级 RAG 标准检索后手段\n