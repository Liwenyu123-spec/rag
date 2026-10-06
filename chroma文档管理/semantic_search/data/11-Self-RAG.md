## 11 Self-RAG（其他优化）
飞书：05-其他优化（Self-RAG）
https://ecnwvcdzorsp.feishu.cn/docx/TXQtdZ8Ino1KFZxfifkcWAjOneg
定位：Post-Retrieval / 生成阶段的动态自我校正；管「查不查、资料好不好、答案有没有依据」。

### 〇、总览

#### 一句话：让模型自己判断要不要检索、检索结果好不好、答案有没有证据、回答有没有用

#### 论文：Asai et al. 2023；反思标记 Reflection Tokens 是核心

#### 定位：第 3 阶段（Post-Retrieval / 生成），不是简单后处理，而是边生成边反思的闭环

#### 效果叙事：7B/13B 经 Self-RAG 训练后，事实准确率可超过未增强的大模型

#### 和第 07 章：Self-RAG 治「过度检索 / 检索不足」；与 CRAG（第 12 章）互补

### 术语定义（本章必背）

#### Self-RAG

##### 定义：Self-Reflective Retrieval-Augmented Generation，带自我反思的检索增强生成

##### 要点：模型边生成边输出反思标记，动态决定检索与校正

#### Reflection Tokens（反思令牌）

##### 定义：插入生成过程的特殊控制标记，表达模型对自己行为的判断

##### 四种：Retrieve / ISREL / ISSUP / ISUSE

#### Retrieve（检索决策）

##### 定义：判断当前问题是否需要外部检索的标记/步骤

##### 取值直觉：YES=去查库；NO=直接用模型内部知识回答

#### ISREL（Is Relevant，相关性）

##### 定义：判断检索到的片段是否与问题相关、足以支撑作答

##### 作用：过滤噪声文档，避免无关资料进生成

#### ISSUP（Is Supported，支持度）

##### 定义：判断生成内容是否被检索证据支撑（打幻觉）

##### 常见档：FULLY / PARTIALLY / NO

#### ISUSE（Is Useful，有用性）

##### 定义：判断最终回答对用户问题的帮助程度

##### 常见：1~5 分，用于监控或候选择优

#### Critic / Generator（批评家 / 生成器）

##### 批评家：负责打反思标签的模型（训练阶段老师）

##### 生成器：同时学习「写什么」和「如何自评」的主模型

#### Adaptive Retrieval（自适应检索）

##### 定义：按 Retrieve 概率/阈值动态决定是否检索，而非固定总查

#### 软约束 vs 硬约束

##### 软约束：调令牌权重，引导生成倾向（如更抠证据）

##### 硬约束：直接丢弃不合格候选（如 No Support）

#### 幻觉 Hallucination

##### 定义：模型生成看似合理但无事实依据或与资料矛盾的内容

##### Self-RAG 用 ISSUP 专门压制这类错误

#### 元认知 Metacognition

##### 定义：对自身认知过程的认知——知道自己知不知道、查不查、答得好不好

##### Self-RAG 的价值叙事：让 LLM 具备初级元认知

### 一、什么是 Self-RAG

#### 1 介绍

##### 全称：Self-Reflective Retrieval-Augmented Generation

##### 核心：生成过程中输出反思标记，智能控制检索与生成

##### 能力：何时查资料、资料是否相关、内容是否可信、据此自动调整行为

#### 2 在 RAG 流程中的定位

##### Pre-Retrieval：查询重写、路由、意图

##### Retrieval：向量 / 混合 / 重排

##### Post-Retrieval：压缩、生成、后处理 ← Self-RAG 主要落在这里

##### 不是「生成完再改一次」，而是生成过程中的动态自我校正

### 二、背景：传统 RAG 三个致命缺陷

#### 盲目检索

##### 不管要不要查，都固定捞 Top-K，易冗余与噪声

##### 闲聊也查库 = 浪费延迟 + 引入无关片段

#### 无法评估

##### 不判断：资料相关吗？答案真有证据吗？

##### 结果：自信地犯错（confidently wrong）

#### 缺乏灵活性

##### 写代码要严证据，写诗歌要流畅——传统 RAG 无法按场景调

#### 课堂比喻

##### 不管题难不难，一律发 5 本参考书

##### 不标哪本有用，也不查答案是否来自书本

### 三、核心思想：四种反思令牌
一句话：Retrieve 管查不查；ISREL 管资料好不好；ISSUP 管答案有没有依据；ISUSE 管答案有没有用。

#### Retrieve（检索决策）

##### 问：这句话 / 这个问题需要查资料吗？

##### 例子：「苹果是什么」可不查；「iPhone 15 发布日」要查

##### 工程：_need_retrieve → YES/NO；NO 则直接用 LLM 内部知识答

#### ISREL（相关性评估）

##### 问：检索片段与问题相关、足以作答吗？

##### 例子：问 Python，捞到 C++ 教程 → IRRELEVANT，过滤掉

##### 工程：_is_relevant → RELEVANT / IRRELEVANT，过滤噪声

#### ISSUP（支持度评估）

##### 问：生成内容有证据支撑吗？（打幻觉）

##### FULLY / PARTIALLY / NO

##### 例子：38 万公里要有数据；「月亮很美」是主观可不苛求

##### 不足时：_correct 强制贴合资料重写

#### ISUSE（有用性评估）

##### 问：回答对用户有帮助吗？打 1~5 分

##### 例子：问做蛋糕，答「我饿了」→ 真实但没用

##### 工程：常用于日志/监控，也可参与候选择优

### 四、Self-RAG vs 传统 RAG

#### 传统：先检索后生成的固定流水线

#### Self-RAG：边检索、边生成、边反思校正的动态闭环

#### 传统：总是检索；Self-RAG：按需检索

#### 传统：照单全收；Self-RAG：ISREL 过滤 + ISSUP 验据

### 五、讲义代码流程（LlamaIndex + 批评家 LLM）
用通用 LLM 在判断点显式提问，等价复现 token 级反思闭环（真正 token 级需微调 selfrag_llama2_7b）。

#### 依赖与配置

##### pip：llama-index-core + dashscope llm/embedding

##### Settings.llm 低温（如 0.1）：分类判断要稳

##### 批评家角色：qwen-plus / qwen-max 扮演四个判断点

#### CustomQueryEngine 封装

##### 继承 CustomQueryEngine，对外仍是标准 query()

##### 内部：Retrieve → 检索 → ISREL → 生成 → ISSUP → 修正 → ISUSE

#### custom_query 六步

##### ① Retrieve：要不要检索？NO → 直接 complete(query)

##### ② 检索：retriever.retrieve(query)

##### ③ ISREL：逐篇过滤无关片段

##### ④ 用相关上下文生成初稿

##### ⑤ ISSUP：不足则 _correct 重写贴合资料

##### ⑥ ISUSE：打分（日志/择优）

#### 四个 _judge Prompt 要点

##### 只输出规定词：YES/NO、RELEVANT/IRRELEVANT、FULLY/PARTIALLY/NO、1~5

##### 修正器 Prompt：完全依据资料、不臆造、无幻觉、完整回答

### 六、进一步理解（训练与推理原理）

#### 1 反思令牌 = 模型的内心独白

##### 真正 Self-RAG：生成文本的同时吐出特殊 token

##### 讲义工程版：在判断点用单独 LLM 调用模拟同样闭环

#### 2 两阶段训练：外部批评 → 自我监督

##### 阶段1：Critic（批评家）

###### 用强模型（讲义：qwen3.7-max / 论文：GPT-4）生成反思标签

###### 训小模型学会同一套判断标准（如 Llama2-7B）

###### 比喻：专家批改 → 培养会批改的助教

##### 阶段2：Generator（生成器）

###### 在训练数据中插入反思令牌 + 检索文档

###### 同时学「该说什么」和「该如何评价自己」

###### 检索文档 masked：不进损失，只当上下文

###### 比喻：例题同时给正确答案和解题思路

#### 3 推理时自适应

##### Adaptive Retrieval：按 Retrieve 概率 / 阈值决定是否查

##### 简单题直接答，难题才翻书

##### Critique-guided Beam Search

###### 综合：语言模型流畅度 + ISREL + ISSUP + ISUSE

###### 加权选最佳路径，不是只看下一词概率

#### 4 硬约束 vs 软约束

##### 软约束：调反思令牌权重（如抬高 ISSUP → 更抠证据）

##### 硬约束：直接丢掉 No Support 等不合格候选

##### 比喻：软=告诉评委更看重哪项；硬=不合格直接刷掉

### 七、实战启示

#### 工程实践

##### 数据：多样化指令数据，约 15 万样本量级，覆盖 QA/事实核查

##### 模型：7B 多数够用；13B 推理更好；资源紧选 7B

##### 检索器：论文默认 Contriever-MS MARCO；时效题要更新知识库

#### 场景适配

##### 高事实：医疗/法律/核查 → 高 ISSUP、更勤检索

##### 创造性：故事/诗歌 → 降检索频率、抬 ISUSE

##### 混合长文：事实段严验，观点段放宽

#### 成本效益

##### 训练成本低于完整 RLHF（批评家可离线）

##### 推理：少做无用检索，但仍比纯生成慢（多轮评估）

### 八、局限与展望

#### 局限：批评家偏见会传导；检索器差仍救不了；多模型调用实时性差

#### 展望：多模态、自然语言式动态反思、按用户个性化权重、与 RL 结合

#### 总结金句：价值不只在准确率，更在让模型有「元认知 / 自知之明」

### 九、对照 chroma文档管理 搜索引擎（现状 / 缺口 / 怎么接）
项目路径：chroma文档管理/semantic_search/。主问答入口 /ask → RagAskService.ask。

#### 现状：哪些「像」Self-RAG，哪些还不是

##### 已有近似能力（分散在别的模块）

###### ISREL 近似：crag.py 逐篇 RELEVANT/IRRELEVANT（但挂在 CRAG，不是生成中反思）

###### 生成约束近似：ASK_QA_PROMPT「只依据上下文，没有就说不知道」

###### 检索前策略：strategy=none/clean/rewrite/hyde（人指定，不是模型 Decide Retrieve）

##### 尚未实现的四令牌

###### Retrieve：闲聊也会走混合检索+CRAG（无「要不要查」门控）

###### ISSUP：生成后无 FULLY/PARTIALLY/NO 验据，无自动 _correct 重写

###### ISUSE：无 1~5 有用性打分与候选择优

###### 无 Critique-guided Beam Search / 软硬约束权重

#### 四令牌 → 建议落点（文件级）

##### Retrieve → rag_service.ask 开头：LLM YES/NO；NO 则 Settings.llm.complete(原问) 直接返回

##### ISREL → 可复用 crag.filter_relevant_nodes（已存在），或生成前再滤一轮

##### ISSUP+_correct → synthesizer 之后：判支持度，不足则贴合 sources 重写 answer

##### ISUSE → 写入 AskResponse 扩展字段，前端日志区展示（index.html 已有 pre/crag 盒子可仿）

#### 最小可落地改造顺序（不改训练也能用）

##### ① 加 Retrieve 门控：降闲聊延迟与噪声（性价比最高）

##### ② 生成后 ISSUP：抑制「资料不够却自信编」

##### ③ ISUSE 仅打日志：先观测再决定是否参与择优

##### ④ 真正 token 级 Self-RAG 需微调模型，本仓库用「判断点显式询问」即可

#### 和 CRAG 怎么分工（本仓库推荐）

##### CRAG（已上线）：检索后滤噪声 + 全无关改写重查

##### Self-RAG（待加）：检索前 Decide + 生成后验据

##### 顺序建议：Retrieve? → Pre/Mid/Post → CRAG → 生成 → ISSUP/ISUSE

##### 避免重复烧钱：ISREL 与 CRAG 评估可共用一次结果

#### 详见第 13 章：项目全链路文件/API/开关对照表\n