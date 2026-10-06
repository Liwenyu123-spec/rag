## 12 Corrective RAG（CRAG）
飞书：06-其他优化（CorrectiveRAG）
https://ecnwvcdzorsp.feishu.cn/docx/TO92dU6QWoTXYjxHT6icY53Dnsf
定位：检索后优化（Post-Retrieval）的评估与修正阶段；管「查错了怎么办」。

### 〇、总览

#### 一句话：检索失手时要有自知之明 + 自我纠错，而不是照单全收

#### CRAG = 标准 RAG + 检索质量校验 + 自动修正 / 补充检索

#### 论文叙事：多基准准确率 +4%~37%，且无需再训现有 LLM

#### 阶段归属：Post-Retrieval —— 检索结果评估与修正

#### 和第 10 章：Rerank/压缩改「怎么用」；CRAG 改「用不用、不够就纠」

### 术语定义（本章必背）

#### Corrective RAG / CRAG

##### 定义：Corrective Retrieval-Augmented Generation，修正增强检索生成

##### 公式：CRAG = 标准 RAG + 检索质量校验 + 自动修正/补充检索

##### 一句话：不假设「检索到的就是对的」，先评估再决定怎么用

#### Retrieval Evaluator（检索评估器）

##### 定义：对召回文档相对问题的正确性/相关性打分或分档的模块

##### 论文三档：Correct / Ambiguous / Incorrect

##### 工程常见：逐篇 yes/no 或 RELEVANT/IRRELEVANT

#### Correct（正确）

##### 定义：检索结果整体足以正确支撑回答

##### 后续：走 Knowledge Refinement，主要用内部精炼知识 k_in

#### Ambiguous（模糊）

##### 定义：部分有用但不充分，或相关度存疑

##### 后续：内部精炼 + 外部搜索，组合 k_in + k_ex

#### Incorrect（不正确）

##### 定义：检索结果基本无法支撑正确回答（跑题/错误/空）

##### 后续：侧重外部知识搜索，主要用 k_ex

#### Knowledge Refinement（知识精炼）

##### 定义：对内部文档做 Decompose→Filter→Recompose，去噪留精华

##### 产物：精炼内部知识 k_in

#### Knowledge Searching（知识搜索）

##### 定义：内部不足时重写查询并检索外部（如 Web）补充知识

##### 产物：外部知识 k_ex

#### k_in / k_ex

##### k_in：来自内部知识库并经精炼的上下文

##### k_ex：来自外部搜索并经选择的上下文

#### 库内修正 vs 完整 CRAG

##### 库内修正：评估过滤 + 改写后仍查同一知识库（本仓库路线）

##### 完整 CRAG：不足时还可 Web 搜索（讲义 Tavily Workflow）

#### confidently wrong（自信地犯错）

##### 定义：检索看似相关实则答非所问，模型仍斩钉截铁给出错误答案

##### CRAG 要防的典型失败模式

#### 检索相关性 ≠ 答案准确性

##### 定义：向量相近或关键词重合，不等于文档能正确回答该问题

##### 例子：《蝙蝠侠之死》编剧 vs 1989《蝙蝠侠》编剧 Hamm

### 一、为什么需要 CRAG

#### 传统 RAG 困境

##### 本质：把检索器结果当绝对真理，无条件喂给生成器

##### 现实：查询不清、库覆盖不全、语义偏差 → 不相关甚至误导

##### 局限：照单全收，没有质量评估关卡

#### 演讲助手比喻

##### 助手资料靠谱 → 演讲精彩

##### 资料错或不相关还照搬 → 翻车

#### 正例：准确文档 → 正确回答

##### 问：亨利·菲尔登的职业是什么？

##### 检索：亨利·费登…是保守党政治家（准确，绿色）

##### 生成：政治家 ✓ —— 文档明确含答案

#### 反例：不准确文档 → 错误回答

##### 问：《蝙蝠侠之死》的编剧是谁？

##### 检索：1989 电影《蝙蝠侠》编剧 Hamm（看似相关实答非所问）

##### 生成：哈姆 ✗ —— 检索相关性 ≠ 答案准确性

##### 警示：confidently wrong（自信地犯错）

#### 解决思路

##### 在检索与生成之间插入文档质量校验关卡

##### 相关且准确 → 用于生成

##### 不相关/不准确 → 丢弃或补充检索（Web 等）

##### 全部不准确 → 重写查询重检索，或回答无法确定

#### 一句话对比：传统假设「检索到的就是对的」；CRAG 质疑「检索到的真的对吗？」

### 二、工作流程（论文三档）

#### ① 用户提问

#### ② 初步检索：知识库召回候选文档

#### ③ 检索质量评估（灵魂）

##### 轻量级 Retrieval Evaluator 给文档 / 整体结果打分

##### 三档：Correct（绿）/ Ambiguous（黄）/ Incorrect（红）

#### ④ 按档位组合内部精炼知识 / 外部搜索知识 → 生成

#### 为什么要用

##### 大幅降低幻觉

##### 私有库 + 公共知识混合题尤其好

##### 比普通 RAG 更鲁棒、更准确

### 三、技术解构：三阶段架构

#### Stage1 Retrieval

##### 问题 x → 检索器 → 文档 d1, d2, …

#### Stage2 Knowledge Correction（知识修正）

##### 6.1 Retrieval Evaluator

###### 问：检索文档对 x 是否正确？

###### 输出 Correct / Ambiguous / Incorrect

###### 对应第一张图：Accurate vs Inaccurate Documents

##### 6.2 Knowledge Refinement（Correct 路径）

###### Decompose：文档拆成 strip 片段

###### Filter：丢掉不相关片段

###### Recompose：重组为精炼内部知识 k_in

###### 即使 Correct，也可能泥沙俱下，要去噪

##### 6.3 Knowledge Searching（Ambiguous / Incorrect）

###### Rewrite：重写查询（更像搜索引擎问法）

###### 例子：Death of a Batman; screenwriter; Wikipedia

###### Web Search → 候选 k1…kn → Select → 外部知识 k_ex

###### 类比 Workflow 的 transform_query + Tavily

#### Stage3 Generation — 三种输入组合

##### Correct → 主要用 k_in（纯内部精炼）

##### Ambiguous → k_in + k_ex（内部+外部）

##### Incorrect → 主要用 k_ex（纯外部）

##### 工程简化：Document(relevant_text + search_text)；哪路空=没用哪路

### 四、基础版代码：内部修正（不过网）
讲义第二节：相关性过滤 + 全无关则改写重检索。覆盖「评估 + 内部修正」。

#### 流程四步

##### [1] retriever.retrieve(query) 多召回（如 top_k=5）

##### [2] 逐篇 RELEVANT / IRRELEVANT 过滤（CRAG 核心）

##### [3] 若全部无关：REWRITE_PROMPT 改写 → 再检索再过滤

##### [4] 仍无关则拒答；否则拼 context 生成

#### 关键 Prompt

##### RELEVANCE：只输出 RELEVANT 或 IRRELEVANT

##### REWRITE：写得更清晰具体，只输出改写后问题

##### ANSWER：仅依据资料回答

#### 实现要点

##### 继承 CustomQueryEngine，封装评估+修正+生成

##### 评估 LLM 低温（讲义 qwen；本仓库可用 DeepSeek）

##### verbose 打印每篇相关/无关，便于调试

#### 使用说明

##### 本地 data/*.txt 当知识库

##### 环境变量：讲义 DASHSCOPE；完整版再加 TAVILY_API_KEY

### 五、完整版：Workflow + Web 搜索
内部不足时转向 Tavily 等外部搜索；官方 Pack 写死 gpt-4，讲义手写 Workflow 换成通义。

#### 与基础版差别

##### 基础版：全无关 → 还在同一库里改写重查

##### 完整版：出现不相关 → 重写查询 + Web 补充外部知识

#### 事件驱动步骤

##### ingest：documents → VectorStoreIndex（首次 run）

##### prepare：存 index / Tavily / query_str

##### retrieve：similarity_top_k=5 候选

##### eval_relevance：逐篇 LLM yes/no（评估器）

##### extract_relevant_texts：只留 yes 文本

##### transform_query：有 no → 重写 + Tavily.search

##### query_result：内外文本合并 SummaryIndex 再生成

#### 工程简化说明

##### 论文三档 → 工程常简化为逐篇 yes/no

##### 只要有一篇 no，就触发 Web（Ambiguous+Incorrect 合并）

##### 想还原三档：改 eval 输出 correct/ambiguous/incorrect，分三条路径

#### Workflow 概念速记

##### Event：step 间数据载体

##### @step：收 Event 出新 Event

##### Context.store：跨 step 共享字典

##### run()：入口，参数变成 StartEvent

### 六、核心知识点总结

#### Corrective RAG = 普通 RAG + 检索质量评估 + 自动修正

#### 评估器：Correct / Ambiguous / Incorrect（工程可简化 yes/no）

#### 修正手段：知识精炼（内部去噪）+ Web 搜索（外部补充）

#### 收益：幻觉↓、过时信息↓、无关检索↓；私有+公共混合场景尤佳

### 七、CRAG vs Self-RAG

#### Self-RAG：管「查不查」+ 生成侧自我反思（Retrieve/ISREL/ISSUP/ISUSE）

#### CRAG：管「查错了怎么办」——评估检索质量并纠正/外搜

#### Self-RAG 重生成过程元认知；CRAG 重检索结果纠错与外部补充

#### 不互斥：可先 CRAG 保证资料靠谱，再 Self-RAG 保证生成有据

#### 口述口诀：Self-RAG=查不查；Corrective=查错了怎么办；Rerank=榜上谁第一

### 八、实战启示与场景

#### 工程指导

##### 不要迷信检索器：质量评估是安全带

##### 轻量专用评估器（论文 0.77B）可优于大而全 LLM 做相关性

##### 内部答不了就外搜，别闭门造车幻觉

##### 知识粒度：整篇硬塞不如拆 strip 再筛

#### 应用场景

##### 企业问答：库匹配差时补权威来源，避免不懂装懂

##### 医疗咨询：精炼+外搜降低错误信息

##### 教育辅导：检索差时动态拿最新资料

### 九、对照 chroma文档管理：代码级走读
主路径：RagAskService.ask → apply_crag → synthesize。启动 python chroma文档管理/run.py → :8003

#### 在 /ask 流水线中的精确位置

##### ① prepare_retrieval_queries（Pre）

##### ② 每路 _build_retriever：向量+BM25 QueryFusion（Mid）

##### ③ 多 query 时 merge_nodes_rrf（查询间融合）

##### ④ apply_postprocessors：rerank→压缩→LongContextReorder（Post）

##### ⑤ apply_crag（本章）← 过滤无关；全无关则改写后 _retrieve_pipeline 再跑一遍 Mid+Post

##### ⑥ get_response_synthesizer(compact)+ASK_QA_PROMPT 生成；sources 用用户原问题对应的真实块

#### crag.py 函数对照讲义

##### _is_relevant ≈ 讲义 Retrieval Evaluator（二值 RELEVANT/IRRELEVANT）

##### filter_relevant_nodes ≈ 基础版 _filter_relevant + verbose 打印

##### rewrite_query_for_retrieval ≈ 讲义 REWRITE_PROMPT（全无关才触发）

##### apply_crag ≈ CorrectiveRAGQueryEngine.custom_query 的评估+修正段

##### retrieve_fn 注入：保证重试仍走混合检索+三件套，不是裸向量

##### 无 LLM 时 _is_relevant 直接 True：避免把结果滤空

#### crag 响应字段（前端 index.html 会展示）

##### enabled / message：是否开启、走了哪条分支

##### before_count → after_count：过滤前后篇数

##### retried + rewritten_query：是否纠错改写及新问句

##### eval[]：每篇 rank/relevant/preview，便于作业演示与排障

##### message 取值：filtered / rewrote_and_filtered / no_relevant_after_retry / …

#### 开关与默认

##### CRAG_ENABLED=true（默认开）

##### CRAG_VERBOSE=true：终端打印 [CRAG] 文档 i：相关/无关

##### 评估模型=Settings.llm（与问答同一套，如 DeepSeek），非单独小评估器

#### 与讲义完整版（Workflow+Tavily）差距

##### 已落地：库内评估过滤 + 一轮改写重检索（demo01 路线）

##### 未落地：Correct/Ambiguous/Incorrect 三档分流

##### 未落地：Knowledge Refinement 拆 strip→滤→重组

##### 未落地：Tavily / Web 外搜；Ambiguous 时 k_in+k_ex

##### 演进优先级：① strip 精炼 ② 三档 ③ 可选外搜（注意内网/合规）

#### 排障口诀（结合本项目）

##### after_count=0：看 eval 是否全 IRRELEVANT → 问法/库覆盖/阈值过严

##### retried=true 仍空：改写句是否偏离；检查混合检索是否回退成纯向量

##### 相关篇被误杀：看 LLM 是否稳定；可临时 CRAG_ENABLED=0 对比

##### 延迟高：CRAG 每篇一次 complete；可先减小 k / RETRIEVE_CANDIDATES

#### 全文件/API 对照见第 13 章\n