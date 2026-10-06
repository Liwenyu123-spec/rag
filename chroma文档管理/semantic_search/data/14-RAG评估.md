## 14 RAG评估
飞书：01-RAG评估
https://ecnwvcdzorsp.feishu.cn/docx/EfLrdJBgvoneojxavWxctJKfngc
优化做完必须评估：量化收益、定位检索/生成瓶颈、驱动下一轮优化。

### 〇、总览

#### 一句话：RAG 优化完毕后必须评估——量化效果、找瓶颈、驱动优化

#### 三大评测面：检索 / 生成 / 端到端，缺一不可

#### 诊断口诀：答案差先看检索指标 → 检索锅还是生成锅

#### 工具线：LlamaIndex 内置评估器（快）→ RAGAS（系统基准，了解）

#### 和本仓库：可用 /ask 输出 + 评测集对比 Pre/Mid/Post/CRAG 开关前后

### 术语定义（本章必背）

#### RAG 评估：用可复现指标衡量检索与生成质量，并对比优化前后

#### LLM-as-a-judge：用大模型当裁判，对照问题/答案/上下文自动打分

#### Ground Truth / Reference：人工或自动标注的标准答案/正确节点

#### Hit Rate（命中率）：Top-K 里是否至少命中一个相关文档

#### MRR（平均倒数排名）：第一个相关文档排名倒数的平均值

#### Faithfulness（忠实度）：答案论断能否被召回上下文支撑（防幻觉）

#### Relevancy / Answer Relevancy（相关性）：答案是否切题、答到点子上

#### Correctness（正确性）：相对标准答案的正确程度（常 1~5 分）

#### Context Precision：召回上下文的排序质量（相关的是否靠前）

#### Context Recall：召回上下文相对参考答案的信息完整度

#### RetrieverEvaluator：LlamaIndex 检索评估器（Hit Rate / MRR）

#### BatchEvalRunner：LlamaIndex 异步批量评估，适合 A/B 对比

#### RAGAS：专业 RAG 评估框架，多数指标可免人工标注

#### garbage in, garbage out：检索错了，再强的生成也救不回来

### 一、为什么要评估 RAG？

#### 三个核心环节都可能出问题

##### 1 检索 Retrieval

###### 问：召回的文档对不对、全不全？

###### 检索错了 → garbage in, garbage out

##### 2 生成 Generation

###### 问：有没有忠实使用召回资料？还是自己编（幻觉）？

##### 3 端到端 End-to-End

###### 问：最终答案准不准、切不切题、全不完整？

#### 评估目标：量化质量 → 定位瓶颈 → 驱动优化

#### 关键诊断思路（必背）

##### 最终答案很差时，先看检索指标

##### 检索没召回正确文档 → 锅在检索侧：分块 / Embedding / 重排 / 混合检索

##### 检索召回了对但答案仍错 → 锅在生成侧：Prompt / 上下文压缩 / 换模型

#### 还能量化优化收益：比如加重排后 Hit Rate / Faithfulness 提升了多少

### 二、核心评估指标

#### 两大类：检索质量 + 生成质量，正好对应两个环节

#### 2.1 检索质量 Retrieval Quality

##### 衡量：召回的文档对不对

##### 前提：带标注的数据集（每题标注哪些文档/节点正确）

##### Hit Rate（命中率）

###### 定义：检索结果中是否包含至少一个相关文档

###### 公式直觉：命中题数 / 总题数

###### 高=少漏；低=经常捞不到正确答案所在块

##### MRR（Mean Reciprocal Rank，平均倒数排名）

###### 定义：第一个相关文档排名倒数的平均值

###### 公式直觉：Σ (1/rank_first_hit) / N；没命中记 0

###### 高=相关文档排得靠前；低=相关的在很后面或没有

##### 常用组合：Hit Rate + MRR；LlamaIndex RetrieverEvaluator 内置

##### 还可关注：Precision@K / Recall@K（与第 09 章召回率/精确率同思路）

#### 2.2 生成质量 Generation Quality

##### 衡量：答案好不好

##### LlamaIndex 三维互补；前两个常可不需人工标准答案

##### Faithfulness 忠实度

###### 只关心：答案有没有出处、是否被上下文支撑

###### 注意：答错题但忠于资料也可能算忠实 → 必须和相关性一起看

##### Relevancy 相关性

###### 关心：答没答到点子上、是否切题

##### Correctness 正确性

###### 需要 reference 标准答案，最接近考试打分

###### 常见输出：1~5 分 + feedback 评语

#### 2.3 在项目周期怎么使用

##### 开发期（快速迭代）

###### 多用 Faithfulness + Relevancy（免标注、反馈快）

###### 小样本 Hit Rate / MRR 盯检索改造（分块/重排/混合）

##### 上线前（卡质量门禁）

###### 加上 Correctness + 黄金问答集

###### BatchEvalRunner：基础 RAG vs 优化 RAG 对比分数

##### 上线后（回归）

###### 固定评测集，每次改链路后复跑，防止「优化 A 坏了 B」

###### 指标掉点 → 回滚或定位是检索侧还是生成侧

##### 原则：同一套题、同一裁判温度，前后才可对比

### 三、示例代码（LlamaIndex 内置评估器）
讲义用通义千问当裁判；本仓库可用 DeepSeek 等同理替换 Settings.llm。

#### 1 准备有干扰信息的文档

##### 文件：data/company_info.txt（贝壳科技示例）

##### 正文含：上班 9:00-18:00、员工 2000、业务 AI/大数据/云计算 等

##### 故意掺干扰

###### 合作公司上班 10:00-19:00（易混淆）

###### 子公司员工 300、业务销售（易混淆）

###### 考勤曾调整又恢复（噪声句）

##### 目的：逼出「捞到干扰句 → 幻觉/答错」的真实场景，方便评估器抓问题

#### 2 生成质量：Faithfulness + Relevancy + Correctness

##### 依赖：llama-index-core + dashscope llm/embedding（讲义）

##### 裁判模型：温度设 0，保证打分稳定可复现

##### 三个评估器

###### FaithfulnessEvaluator：答案是否被召回上下文支撑

###### RelevancyEvaluator：答案+上下文是否切题

###### CorrectnessEvaluator：答案 vs reference，1~5 分

##### 调用要点

###### evaluate_response(query, response)：自动从 response.source_nodes 取上下文

###### 忠实度/相关性：.passing + .score(0/1)

###### 正确性：.evaluate(..., reference=...) → .score(1~5) + .feedback

##### 示例 qa_pairs

###### 上下班时间？→ 9:00-18:00，午休 12:00-13:00

###### 员工总数？→ 2000人

###### 主营业务？→ AI软件开发、大数据服务、云计算平台

#### 3 检索质量：Hit Rate + MRR

##### 意义：生成评估只说「答案好不好」，定位不了检索锅还是生成锅

##### RetrieverEvaluator / 或手写：aretrieve → 判断是否命中 → 算 Hit/MRR

##### 讲义手写版流程

###### SentenceSplitter(chunk_size=120, overlap=20) 建节点

###### retriever = index.as_retriever(similarity_top_k=2)

###### 每题配 keywords：命中任一关键词即视为相关（简化 Ground Truth）

###### Hit Rate = 命中次数/总题数

###### MRR：第一个相关文档的 1/rank，未命中为 0，再平均

##### 生产更稳：用节点 ID 作黄金标准，而不是关键词模糊匹配

##### 调 top_k / 分块 / 重排后复跑 → 量化检索优化是否有效

#### 4 对比「基础 RAG vs 优化 RAG」：批量评估

##### 最大用处：量化优化收益（前后分数差）

##### 工具：BatchEvalRunner 异步批量跑，比逐题 evaluate 快

##### 讲义对比设定

###### 基础：similarity_top_k=2 的朴素 query_engine

###### 优化：加重排或上下文压缩，过滤干扰句

###### 同一套问题跑 Faithfulness / Relevancy 等，打印对比表

##### 和本仓库对照：关/开 HYBRID、RERANK、COMPRESS、CRAG 做四组 A/B

### 四、RAGAS 等专业评估框架（了解）

#### 4.1 RAGAS 是什么

##### 全称：Retrieval Augmented Generation Assessment

##### 专门为 RAG 流水线设计的自动化评估框架

##### 核心理念三点

###### Reference-free：多数指标免人工标准答案，用 LLM-as-a-judge

###### 检索+生成分别诊断：指标明确归侧，方便定位瓶颈

###### 与 LlamaIndex / LangChain 无缝集成，复用现有引擎

##### 定位：LlamaIndex 内置=轻量快接入；RAGAS=系统、指标更丰富的基准

#### 4.2 RAGAS 核心指标（四个最常用）

##### Faithfulness（生成侧）

###### 把答案拆成若干 claim（论断）

###### 逐条看能否由上下文支撑

###### 分数 = 被支撑论断数 / 总论断数

##### Answer Relevancy（生成侧）

###### 让 LLM 根据答案反向生成可能的问题

###### 算这些问题与原始问题的相似度 → 越接近越切题

##### Context Precision（检索侧）

###### 对照 reference，看召回上下文的排序质量

###### 相关片段是否靠前

##### Context Recall（检索侧）

###### 对照 reference，看召回上下文的信息完整度

###### 答对所需信息有没有被捞全

### 五、小结与评估闭环

#### ① 先看检索指标：定位是检索还是生成的问题

#### ② 针对性优化：分块 / 重排 / 压缩 / Prompt / CRAG…

#### ③ 同一套评估复跑：对比前后分数，量化收益

#### ④ 固化评测集：上线后做回归，防止越改越差

### 六、和本仓库 chroma文档管理 怎么接

#### 现状

##### 主链路已有 Pre/Mid/Post/CRAG，但没有独立评估脚本模块

##### 可先用讲义脚本对 data/ 或导出的问答集评测

#### 最小落地建议

##### 准备 20~50 条黄金问答（含 reference）

##### 对 /ask 的 answer + sources 跑 Faithfulness/Relevancy/Correctness

##### 对 _build_retriever 跑 Hit Rate/MRR（节点 ID 标注更好）

##### 开关矩阵：rewrite/hyde × hybrid × rerank × compress × crag

#### 诊断映射到第 08~13 章

##### Hit/MRR 低 → 08 改写/HyDE、09 混合、10 重排

##### Faithfulness 低 → 10 压缩、Prompt 约束、12 CRAG 过滤噪声

##### Relevancy 低 → 改写问句、提高精排、检查干扰文档

##### Correctness 低但检索好 → 换生成模型/加强「仅依据资料」\n