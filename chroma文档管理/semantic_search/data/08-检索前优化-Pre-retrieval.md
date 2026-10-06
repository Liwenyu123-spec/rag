## 08 检索前优化（Pre-retrieval）
每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。

### 〇、总览：方法地图

#### 查询侧：清洗 → 澄清 → 重写 / 扩展 / HyDE / Step-Back / 分解

#### 文档侧（离线）：分块 → 元数据 → 增强 → 多表示 / 路由规则

#### 原则：先判断病症，再选一种方法；不要一次全开

### 术语定义（本章必背）

#### Pre-retrieval（检索前优化）：进入检索前，优化「问什么」和「库怎么建」

#### 查询清洗：去口语废话与标点噪声，并做术语标准化

#### 查询重写：把口语/模糊问题改成更适合检索的表达，保留原意

#### 查询扩展：生成多个同义变体并行检索再合并，抬召回

#### HyDE：先生成假想答案文档再拿去向量检索（假想文不当事实引用）

#### Step-Back：把具体问题先退成更宽泛背景问题

#### 查询分解：复杂多跳/比较题拆成原子子问题分别检索再综合

#### Chunking（分块）：长文切成适合 embedding 与召回的片段

#### Overlap：相邻块保留重叠，减轻边界切断语义

#### 父子块/Small-to-Big：小块命中，返回父级大上下文

#### 元数据 Metadata：标题/时间/来源/权限等，供过滤与引用

#### 意图路由：按问题类型选择不同索引或工具

### 方法1：查询文本清洗

#### 适用：问题里废话多、口语多、术语不统一

#### 输入

##### 原始用户问题字符串

##### 可选：公司术语表（俚语→标准词）

#### 分步分解

##### Step1 去口语：删「帮我看看」「那个」「嗯啊」等无信息词

##### Step2 去标点噪音：多余空格、表情、重复符号

##### Step3 术语标准化：查表替换（电脑→笔记本电脑；年假→带薪年休假）

##### Step4 实体抽出：产品名、日期、工号单独列出（可给 BM25 用）

##### Step5 得到「干净查询」再进入改写或直接 embedding

#### 输出

##### clean_query：清洗后的问句

##### entities：抽出的关键词列表（可选）

#### 完整例子

##### 输入：嗯那个帮我看看请假咋扣钱啊???

##### Step1-2 后：请假咋扣钱

##### Step3 后：请假 如何 扣款

##### entities：['请假','扣款']

### 方法2：澄清反问

#### 适用：缺实体、多意图、指代不明（上次那个、这个）

#### 输入

##### 原始问题 + 可选多轮历史

#### 分步分解

##### Step1 判断是否模糊：缺类型？缺时间？有指代？多意图？

##### Step2 若清晰：跳过，进入重写/检索

##### Step3 若模糊：生成 1 个澄清问题返回前端，本轮先不检索或只轻量搜

##### Step4 用户补充后，拼成「完整问题」= 原问题 + 用户选择

##### Step5 用完整问题再走清洗/重写/检索

#### 输出

##### 分支A：clarify_question（反问文案）

##### 分支B：resolved_query（澄清后的完整查询）

#### 完整例子

##### 输入：请假扣钱吗

##### Step1：缺假期类型 → 模糊

##### Step3 反问：请问是事假、病假还是年假？

##### 用户答：事假 → resolved_query=事假是否扣钱及扣款规则

### 方法3：查询重写 Query Rewriting

#### 适用：口语、指代、缺关键词，但意图基本单一

#### 输入

##### clean_query（最好先清洗）

##### 可选：对话历史（用来解析「那个」「上次」）

#### 分步分解

##### Step1 准备改写 Prompt：角色=检索改写助手；只输出改写句；不解释

##### Step2 约束：补全实体、保留原意、可加同义术语、不要编造不存在的产品名

##### Step3 调 LLM（低温 0~0.3）得到 rewritten_query

##### Step4 用 rewritten_query 做 embedding

##### Step5（推荐）原句也 embedding，两路检索结果合并，防改歪

##### Step6 合并后的片段再交给生成

#### 输出

##### rewritten_query：检索用问句

##### 可选：retrieval_queries = [原句, 改写句]

#### 完整例子

##### 输入：上次那个产品的安全规范更新了吗

##### 历史里「那个产品」= 智能手表 X1

##### 改写：智能手表X1 安全规范 是否更新 最新版本

##### 操作：改写句检索 + 原句检索 → 合并 Top 片段 → 生成

#### LlamaIndex 落点

##### 自定义 BaseQueryTransform._run 里调 LLM

##### 或 TransformQueryEngine(base_engine, transform)

### 方法4：查询扩展 Multi-Query

#### 适用：用词不准、同义多、怕漏召回

#### 输入

##### 一条核心问题（可已清洗/改写）

##### 参数 N：变体个数，常用 3~5

#### 分步分解

##### Step1 Prompt：生成 N 个检索变体，覆盖同义词、不同句式、上下位词；每行一个

##### Step2 解析 LLM 输出为列表 variants[1..N]

##### Step3 对每个 variant 分别向量检索，各取 Top-K

##### Step4 融合：RRF（按排名加分）或去重保留最高分

##### Step5 取融合后 Top-M 作为最终检索结果

##### Step6 再进入生成或重排

#### 输出

##### variants：N 条查询字符串

##### fused_nodes：融合后的文档块列表

#### 完整例子

##### 输入：请假怎么扣钱

##### 变体1：事假扣款规则

##### 变体2：病假是否带薪

##### 变体3：考勤制度 旷工 罚款

##### 变体4：年假提前离职如何折算

##### 四路检索 → RRF 合并 → 把事假/考勤相关块顶上来

#### LlamaIndex 落点

##### QueryFusionRetriever(..., num_queries=4, mode='reciprocal_rerank')

#### 和重写区别：重写≈改成更好的一句；扩展≈变成多句一起查

### 方法5：HyDE 假设文档检索

#### 适用：问句很短，或用户说法和文档风格差很大

#### 输入

##### 用户原问题

##### 同一套 Embedding 模型（必须与建库一致）

#### 分步分解

##### Step1 Prompt：请写一段「可能回答该问题」的文档片段，用说明文/制度口吻，不要对话

##### Step2 LLM 生成 hypo_doc（假想答案文档）

##### Step3 对 hypo_doc 做 embedding → hypo_vec

##### Step4 用 hypo_vec 在向量库 search Top-K → 得到真实文档块

##### Step5（强烈建议）对原问题再 search 一路

##### Step6 两路结果合并/去重

##### Step7 只用真实文档块生成答案；假想文档绝不当事实引用

#### 输出

##### hypo_doc：仅用于检索的中间产物

##### real_chunks：库里的真实片段

#### 完整例子

##### 输入：年假怎么算

##### Step2 假想：员工入职满一年享有带薪年假…按工龄递增…

##### Step4 用这段去搜 → 命中《考勤手册》年假条款真文

##### Step7 根据真文回答，并引用考勤手册

#### LlamaIndex 落点

##### hyde = HyDEQueryTransform(include_original=True)

##### engine = TransformQueryEngine(base_engine, hyde)

##### include_original=True 即自动做 Step5

#### 翻车点：假想胡编会带偏 → 必须保留原查询；多一次 LLM 更慢更贵

### 方法6：Step-Back 后退提问

#### 适用：细节问题缺少背景，直接搜容易碎片化

#### 输入

##### 具体问题 specific_q

#### 分步分解

##### Step1 Prompt：把具体问题改写成更抽象的背景/原理问题

##### Step2 得到 step_back_q

##### Step3 用 step_back_q 检索 → 背景材料 background_chunks

##### Step4 用 specific_q 检索 → 细节材料 detail_chunks

##### Step5 生成时同时塞入背景+细节，先背景后细节回答

#### 输出

##### step_back_q

##### background_chunks + detail_chunks

#### 完整例子

##### specific_q：Qwen2.5-7B 上下文窗口多长

##### step_back_q：主流大语言模型上下文窗口一般是什么量级

##### 先检索通识，再检索该型号说明，最后综合

#### 和 HyDE 区别：Step-Back 产出的是更宽的「问题」；HyDE 产出假想「答案文档」

### 方法7：子查询分解 Decomposition

#### 适用：比较题、多跳题、要多个信息点才能答

#### 输入

##### 复杂原问题 complex_q

##### 可选：多个 QueryEngine/工具（不同库）

#### 分步分解

##### Step1 LLM 分解：输出 JSON 子问题列表，每个可独立检索

##### Step2 校验：子问题是否原子、是否覆盖原问题所需信息

##### Step3 路由：每个子问题选哪个工具/索引（靠 tool description）

##### Step4 并发检索（或并发问答）得到 sub_results[]

##### Step5 综合 Prompt：根据子结果回答原问题，标注每条证据来源

##### Step6 输出最终答案 + 引用

#### 输出

##### sub_questions[]

##### sub_results[]

##### final_answer + citations

#### 完整例子

##### complex_q：比较 A/B 公司 2023 营收增长谁快

##### 子问1：A 公司 2023 营收是多少

##### 子问2：B 公司 2023 营收是多少

##### 子问3：A、B 相对 2022 的增长率

##### 分别检索年报片段 → LLM 算增长并对比 → 给出结论

#### LlamaIndex 落点

##### QueryEngineTool.from_defaults(..., description='查A公司财务')

##### SubQuestionQueryEngine.from_defaults(query_engine_tools=tools)

##### description 不准 → 路由错库（最常见失败）

#### 和扩展区别：扩展=同义多说法；分解=不同信息点

### 方法8：句子分块 SentenceSplitter

#### 适用：大多数中文文档的默认方案（离线建库）

#### 输入

##### Document 列表（load_data 得到）

##### 参数：chunk_size、chunk_overlap

#### 分步分解

##### Step1 按段落分隔符粗切（如多个换行）

##### Step2 再按句子边界细切（。！？等）

##### Step3 把句子累加，直到接近 chunk_size（按 token）

##### Step4 输出一块；下一块带上上块末尾 overlap 句子

##### Step5 所有块变成 Node，再 embedding 入库

#### 输出

##### nodes[]：每块含 text + metadata

#### 操作命令

##### splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)

##### nodes = splitter.get_nodes_from_documents(docs)

##### index.insert_nodes(nodes)

#### 调参：缺上下文 → 加大 chunk 或 overlap；检不中 → 块可能太大或要改查询

### 方法9：语义分块 SemanticSplitter

#### 适用：长文、主题多变，希望按语义边界切

#### 输入

##### 长文档 + embed_model（与检索同一套）

##### buffer_size、breakpoint_percentile_threshold

#### 分步分解

##### Step1 中文分句（自定义：按。！？和换行切）

##### Step2 用滑动窗口组成「组合句」（buffer_size 控制前后各几句）

##### Step3 对组合句 embedding，算相邻组合句相似度

##### Step4 相似度下跌超过阈值（百分位）→ 在此处切开

##### Step5 得到语义块 Node → 入库

#### 输出

##### 按主题相对完整的块（块大小不固定）

#### 操作要点

##### SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95, ...)

##### 先 clean_empty_text；千问 embedding 注意 batch≤10

##### 更慢更贵（要算很多句向量）

### 方法10：父子块 Parent-Child

#### 适用：既要检索准，又要生成时有完整上下文

#### 输入

##### 文档 + 两级大小，如父 2048、子 512

#### 分步分解

##### Step1 HierarchicalNodeParser 切出父大块、子小块，建立父子关系

##### Step2 只对叶子小块做 embedding，建向量索引

##### Step3 父块原文放进 docstore（不靠向量找父块）

##### Step4 查询时：向量检索命中小块

##### Step5 AutoMergingRetriever：把命中的小块合并回父块（或更大上下文）

##### Step6 把合并后的大上下文交给 LLM 生成

#### 输出

##### 检索命中：小块；生成输入：父块/合并块

#### 操作要点

##### parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512])

##### retriever = AutoMergingRetriever(leaf_retriever, storage_context)

#### 解决的矛盾：小块好中、大块好答

### 方法11：元数据预过滤

#### 适用：用户带时间/类别/来源限制

#### 分步分解

##### Step1 建库时给 Node 打 metadata（category/year/source/page）

##### Step2 查询时解析约束（只要 2024、只要年假）

##### Step3 构造 where 条件

##### Step4 向量检索只在过滤后的子集里做

##### Step5 无约束则 where 为空，全库搜

#### 完整例子

##### 入库：metadata={'category':'年假','year':2024}

##### 问题：2024 年年假怎么请

##### where={'category':'年假','year':2024} → 再向量搜

#### 口述：先缩小书架，再找相似书

### 方法12：意图路由

#### 适用：多个知识库/集合，问题类型不同

#### 分步分解

##### Step1 准备多库：制度库、FAQ 库、技术文档库

##### Step2 为每个库写清 description（给路由用）

##### Step3 分类：规则 / 小模型 / LLM 判断问题类型

##### Step4 只调用对应库的 retriever/query_engine

##### Step5 或多工具交给 SubQuestionQueryEngine 自动路由

#### 翻车点：description 写糊 → 路由乱；要写「查什么 / 不查什么」

### 方法13：权限过滤

#### 适用：多租户、按部门/角色可见

#### 分步分解

##### Step1 文档 metadata 写入 allowed_roles / dept

##### Step2 请求带上当前用户角色

##### Step3 检索前 where 加上角色条件

##### Step4 再向量搜；无权限文档根本不会进候选集

#### 铁律：不能先搜出敏感段再靠 Prompt「别泄露」

### 方法14：文档增强（摘要/关键词/假设问题）

#### 适用：正文不好搜，需要额外「入口」

#### 分步分解（离线）

##### Step1 对每个 chunk 调 LLM 生成：一句话摘要、关键词、2 个假设用户问题

##### Step2 把假设问题也做成可检索向量（或与 chunk 同 id 关联）

##### Step3 可选：摘要单独一路向量

##### Step4 在线检索时可匹配「假设问题」或「摘要」（类似反向 HyDE）

##### Step5 命中后仍返回原 chunk 正文给生成

#### 输出：更易被问句命中的索引，而不改变最终依据仍是原文

### 方法怎么串起来（推荐顺序）

#### 离线

##### 加载 → 清洗空文 → 分块(8/9/10选一) → 打元数据 → 可选增强 → 同一 Embedding 入库

#### 在线

##### 1 清洗（方法1）

##### 2 模糊？→ 澄清（方法2）

##### 3 复杂比较？→ 分解（方法7）

##### 4 否则三选一：重写(3) / 扩展(4) / HyDE(5)；缺背景加 Step-Back(6)

##### 5 有类别时间？→ 预过滤(11)；多库？→ 路由(12)；有权限？→(13)

##### 6 进入检索中（第 09 章混合/多路）→ 再重排生成（检索后）

#### 本仓库已落地 / 怎么调

##### /ask 默认 strategy=rewrite：清洗+重写双路（pre_retrieval.py）

##### 可改 strategy=hyde / clean / none；假想文档只检索不当引用

##### 后面已接混合检索、后处理三件套、CRAG；细节见第 13 章\n