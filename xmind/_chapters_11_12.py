# -*- coding: utf-8 -*-
"""Chapters 11 Self-RAG + 12 CRAG for build_xmind (from Feishu 05/06)."""


def chapters(topic):
    """Return [ch11, ch12] topic nodes. Caller passes topic() factory."""
    ch11 = topic(
        "11 Self-RAG（其他优化）",
        note=(
            "飞书：05-其他优化（Self-RAG）\n"
            "https://ecnwvcdzorsp.feishu.cn/docx/TXQtdZ8Ino1KFZxfifkcWAjOneg\n"
            "定位：Post-Retrieval / 生成阶段的动态自我校正；管「查不查、资料好不好、答案有没有依据」。"
        ),
        children=[
            topic(
                "〇、总览",
                children=[
                    topic("一句话：让模型自己判断要不要检索、检索结果好不好、答案有没有证据、回答有没有用"),
                    topic("论文：Asai et al. 2023；反思标记 Reflection Tokens 是核心"),
                    topic("定位：第 3 阶段（Post-Retrieval / 生成），不是简单后处理，而是边生成边反思的闭环"),
                    topic("效果叙事：7B/13B 经 Self-RAG 训练后，事实准确率可超过未增强的大模型"),
                    topic("和第 07 章：Self-RAG 治「过度检索 / 检索不足」；与 CRAG（第 12 章）互补"),
                ],
            ),
            topic(
                "一、什么是 Self-RAG",
                children=[
                    topic(
                        "1 介绍",
                        children=[
                            topic("全称：Self-Reflective Retrieval-Augmented Generation"),
                            topic("核心：生成过程中输出反思标记，智能控制检索与生成"),
                            topic("能力：何时查资料、资料是否相关、内容是否可信、据此自动调整行为"),
                        ],
                    ),
                    topic(
                        "2 在 RAG 流程中的定位",
                        children=[
                            topic("Pre-Retrieval：查询重写、路由、意图"),
                            topic("Retrieval：向量 / 混合 / 重排"),
                            topic("Post-Retrieval：压缩、生成、后处理 ← Self-RAG 主要落在这里"),
                            topic("不是「生成完再改一次」，而是生成过程中的动态自我校正"),
                        ],
                    ),
                ],
            ),
            topic(
                "二、背景：传统 RAG 三个致命缺陷",
                children=[
                    topic(
                        "盲目检索",
                        children=[
                            topic("不管要不要查，都固定捞 Top-K，易冗余与噪声"),
                            topic("闲聊也查库 = 浪费延迟 + 引入无关片段"),
                        ],
                    ),
                    topic(
                        "无法评估",
                        children=[
                            topic("不判断：资料相关吗？答案真有证据吗？"),
                            topic("结果：自信地犯错（confidently wrong）"),
                        ],
                    ),
                    topic(
                        "缺乏灵活性",
                        children=[
                            topic("写代码要严证据，写诗歌要流畅——传统 RAG 无法按场景调"),
                        ],
                    ),
                    topic(
                        "课堂比喻",
                        children=[
                            topic("不管题难不难，一律发 5 本参考书"),
                            topic("不标哪本有用，也不查答案是否来自书本"),
                        ],
                    ),
                ],
            ),
            topic(
                "三、核心思想：四种反思令牌",
                note="一句话：Retrieve 管查不查；ISREL 管资料好不好；ISSUP 管答案有没有依据；ISUSE 管答案有没有用。",
                children=[
                    topic(
                        "Retrieve（检索决策）",
                        children=[
                            topic("问：这句话 / 这个问题需要查资料吗？"),
                            topic("例子：「苹果是什么」可不查；「iPhone 15 发布日」要查"),
                            topic("工程：_need_retrieve → YES/NO；NO 则直接用 LLM 内部知识答"),
                        ],
                    ),
                    topic(
                        "ISREL（相关性评估）",
                        children=[
                            topic("问：检索片段与问题相关、足以作答吗？"),
                            topic("例子：问 Python，捞到 C++ 教程 → IRRELEVANT，过滤掉"),
                            topic("工程：_is_relevant → RELEVANT / IRRELEVANT，过滤噪声"),
                        ],
                    ),
                    topic(
                        "ISSUP（支持度评估）",
                        children=[
                            topic("问：生成内容有证据支撑吗？（打幻觉）"),
                            topic("FULLY / PARTIALLY / NO"),
                            topic("例子：38 万公里要有数据；「月亮很美」是主观可不苛求"),
                            topic("不足时：_correct 强制贴合资料重写"),
                        ],
                    ),
                    topic(
                        "ISUSE（有用性评估）",
                        children=[
                            topic("问：回答对用户有帮助吗？打 1~5 分"),
                            topic("例子：问做蛋糕，答「我饿了」→ 真实但没用"),
                            topic("工程：常用于日志/监控，也可参与候选择优"),
                        ],
                    ),
                ],
            ),
            topic(
                "四、Self-RAG vs 传统 RAG",
                children=[
                    topic("传统：先检索后生成的固定流水线"),
                    topic("Self-RAG：边检索、边生成、边反思校正的动态闭环"),
                    topic("传统：总是检索；Self-RAG：按需检索"),
                    topic("传统：照单全收；Self-RAG：ISREL 过滤 + ISSUP 验据"),
                ],
            ),
            topic(
                "五、讲义代码流程（LlamaIndex + 批评家 LLM）",
                note="用通用 LLM 在判断点显式提问，等价复现 token 级反思闭环（真正 token 级需微调 selfrag_llama2_7b）。",
                children=[
                    topic(
                        "依赖与配置",
                        children=[
                            topic("pip：llama-index-core + dashscope llm/embedding"),
                            topic("Settings.llm 低温（如 0.1）：分类判断要稳"),
                            topic("批评家角色：qwen-plus / qwen-max 扮演四个判断点"),
                        ],
                    ),
                    topic(
                        "CustomQueryEngine 封装",
                        children=[
                            topic("继承 CustomQueryEngine，对外仍是标准 query()"),
                            topic("内部：Retrieve → 检索 → ISREL → 生成 → ISSUP → 修正 → ISUSE"),
                        ],
                    ),
                    topic(
                        "custom_query 六步",
                        children=[
                            topic("① Retrieve：要不要检索？NO → 直接 complete(query)"),
                            topic("② 检索：retriever.retrieve(query)"),
                            topic("③ ISREL：逐篇过滤无关片段"),
                            topic("④ 用相关上下文生成初稿"),
                            topic("⑤ ISSUP：不足则 _correct 重写贴合资料"),
                            topic("⑥ ISUSE：打分（日志/择优）"),
                        ],
                    ),
                    topic(
                        "四个 _judge Prompt 要点",
                        children=[
                            topic("只输出规定词：YES/NO、RELEVANT/IRRELEVANT、FULLY/PARTIALLY/NO、1~5"),
                            topic("修正器 Prompt：完全依据资料、不臆造、无幻觉、完整回答"),
                        ],
                    ),
                ],
            ),
            topic(
                "六、进一步理解（训练与推理原理）",
                children=[
                    topic(
                        "1 反思令牌 = 模型的内心独白",
                        children=[
                            topic("真正 Self-RAG：生成文本的同时吐出特殊 token"),
                            topic("讲义工程版：在判断点用单独 LLM 调用模拟同样闭环"),
                        ],
                    ),
                    topic(
                        "2 两阶段训练：外部批评 → 自我监督",
                        children=[
                            topic(
                                "阶段1：Critic（批评家）",
                                children=[
                                    topic("用强模型（讲义：qwen3.7-max / 论文：GPT-4）生成反思标签"),
                                    topic("训小模型学会同一套判断标准（如 Llama2-7B）"),
                                    topic("比喻：专家批改 → 培养会批改的助教"),
                                ],
                            ),
                            topic(
                                "阶段2：Generator（生成器）",
                                children=[
                                    topic("在训练数据中插入反思令牌 + 检索文档"),
                                    topic("同时学「该说什么」和「该如何评价自己」"),
                                    topic("检索文档 masked：不进损失，只当上下文"),
                                    topic("比喻：例题同时给正确答案和解题思路"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "3 推理时自适应",
                        children=[
                            topic("Adaptive Retrieval：按 Retrieve 概率 / 阈值决定是否查"),
                            topic("简单题直接答，难题才翻书"),
                            topic(
                                "Critique-guided Beam Search",
                                children=[
                                    topic("综合：语言模型流畅度 + ISREL + ISSUP + ISUSE"),
                                    topic("加权选最佳路径，不是只看下一词概率"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "4 硬约束 vs 软约束",
                        children=[
                            topic("软约束：调反思令牌权重（如抬高 ISSUP → 更抠证据）"),
                            topic("硬约束：直接丢掉 No Support 等不合格候选"),
                            topic("比喻：软=告诉评委更看重哪项；硬=不合格直接刷掉"),
                        ],
                    ),
                ],
            ),
            topic(
                "七、实战启示",
                children=[
                    topic(
                        "工程实践",
                        children=[
                            topic("数据：多样化指令数据，约 15 万样本量级，覆盖 QA/事实核查"),
                            topic("模型：7B 多数够用；13B 推理更好；资源紧选 7B"),
                            topic("检索器：论文默认 Contriever-MS MARCO；时效题要更新知识库"),
                        ],
                    ),
                    topic(
                        "场景适配",
                        children=[
                            topic("高事实：医疗/法律/核查 → 高 ISSUP、更勤检索"),
                            topic("创造性：故事/诗歌 → 降检索频率、抬 ISUSE"),
                            topic("混合长文：事实段严验，观点段放宽"),
                        ],
                    ),
                    topic(
                        "成本效益",
                        children=[
                            topic("训练成本低于完整 RLHF（批评家可离线）"),
                            topic("推理：少做无用检索，但仍比纯生成慢（多轮评估）"),
                        ],
                    ),
                ],
            ),
            topic(
                "八、局限与展望",
                children=[
                    topic("局限：批评家偏见会传导；检索器差仍救不了；多模型调用实时性差"),
                    topic("展望：多模态、自然语言式动态反思、按用户个性化权重、与 RL 结合"),
                    topic("总结金句：价值不只在准确率，更在让模型有「元认知 / 自知之明」"),
                ],
            ),
            topic(
                "九、对照 chroma文档管理 搜索引擎（现状 / 缺口 / 怎么接）",
                note="项目路径：chroma文档管理/semantic_search/。主问答入口 /ask → RagAskService.ask。",
                children=[
                    topic(
                        "现状：哪些「像」Self-RAG，哪些还不是",
                        children=[
                            topic(
                                "已有近似能力（分散在别的模块）",
                                children=[
                                    topic("ISREL 近似：crag.py 逐篇 RELEVANT/IRRELEVANT（但挂在 CRAG，不是生成中反思）"),
                                    topic("生成约束近似：ASK_QA_PROMPT「只依据上下文，没有就说不知道」"),
                                    topic("检索前策略：strategy=none/clean/rewrite/hyde（人指定，不是模型 Decide Retrieve）"),
                                ],
                            ),
                            topic(
                                "尚未实现的四令牌",
                                children=[
                                    topic("Retrieve：闲聊也会走混合检索+CRAG（无「要不要查」门控）"),
                                    topic("ISSUP：生成后无 FULLY/PARTIALLY/NO 验据，无自动 _correct 重写"),
                                    topic("ISUSE：无 1~5 有用性打分与候选择优"),
                                    topic("无 Critique-guided Beam Search / 软硬约束权重"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "四令牌 → 建议落点（文件级）",
                        children=[
                            topic("Retrieve → rag_service.ask 开头：LLM YES/NO；NO 则 Settings.llm.complete(原问) 直接返回"),
                            topic("ISREL → 可复用 crag.filter_relevant_nodes（已存在），或生成前再滤一轮"),
                            topic("ISSUP+_correct → synthesizer 之后：判支持度，不足则贴合 sources 重写 answer"),
                            topic("ISUSE → 写入 AskResponse 扩展字段，前端日志区展示（index.html 已有 pre/crag 盒子可仿）"),
                        ],
                    ),
                    topic(
                        "最小可落地改造顺序（不改训练也能用）",
                        children=[
                            topic("① 加 Retrieve 门控：降闲聊延迟与噪声（性价比最高）"),
                            topic("② 生成后 ISSUP：抑制「资料不够却自信编」"),
                            topic("③ ISUSE 仅打日志：先观测再决定是否参与择优"),
                            topic("④ 真正 token 级 Self-RAG 需微调模型，本仓库用「判断点显式询问」即可"),
                        ],
                    ),
                    topic(
                        "和 CRAG 怎么分工（本仓库推荐）",
                        children=[
                            topic("CRAG（已上线）：检索后滤噪声 + 全无关改写重查"),
                            topic("Self-RAG（待加）：检索前 Decide + 生成后验据"),
                            topic("顺序建议：Retrieve? → Pre/Mid/Post → CRAG → 生成 → ISSUP/ISUSE"),
                            topic("避免重复烧钱：ISREL 与 CRAG 评估可共用一次结果"),
                        ],
                    ),
                    topic("详见第 13 章：项目全链路文件/API/开关对照表"),
                ],
            ),
        ],
    )

    ch12 = topic(
        "12 Corrective RAG（CRAG）",
        note=(
            "飞书：06-其他优化（CorrectiveRAG）\n"
            "https://ecnwvcdzorsp.feishu.cn/docx/TO92dU6QWoTXYjxHT6icY53Dnsf\n"
            "定位：检索后优化（Post-Retrieval）的评估与修正阶段；管「查错了怎么办」。"
        ),
        children=[
            topic(
                "〇、总览",
                children=[
                    topic("一句话：检索失手时要有自知之明 + 自我纠错，而不是照单全收"),
                    topic("CRAG = 标准 RAG + 检索质量校验 + 自动修正 / 补充检索"),
                    topic("论文叙事：多基准准确率 +4%~37%，且无需再训现有 LLM"),
                    topic("阶段归属：Post-Retrieval —— 检索结果评估与修正"),
                    topic("和第 10 章：Rerank/压缩改「怎么用」；CRAG 改「用不用、不够就纠」"),
                ],
            ),
            topic(
                "一、为什么需要 CRAG",
                children=[
                    topic(
                        "传统 RAG 困境",
                        children=[
                            topic("本质：把检索器结果当绝对真理，无条件喂给生成器"),
                            topic("现实：查询不清、库覆盖不全、语义偏差 → 不相关甚至误导"),
                            topic("局限：照单全收，没有质量评估关卡"),
                        ],
                    ),
                    topic(
                        "演讲助手比喻",
                        children=[
                            topic("助手资料靠谱 → 演讲精彩"),
                            topic("资料错或不相关还照搬 → 翻车"),
                        ],
                    ),
                    topic(
                        "正例：准确文档 → 正确回答",
                        children=[
                            topic("问：亨利·菲尔登的职业是什么？"),
                            topic("检索：亨利·费登…是保守党政治家（准确，绿色）"),
                            topic("生成：政治家 ✓ —— 文档明确含答案"),
                        ],
                    ),
                    topic(
                        "反例：不准确文档 → 错误回答",
                        children=[
                            topic("问：《蝙蝠侠之死》的编剧是谁？"),
                            topic("检索：1989 电影《蝙蝠侠》编剧 Hamm（看似相关实答非所问）"),
                            topic("生成：哈姆 ✗ —— 检索相关性 ≠ 答案准确性"),
                            topic("警示：confidently wrong（自信地犯错）"),
                        ],
                    ),
                    topic(
                        "解决思路",
                        children=[
                            topic("在检索与生成之间插入文档质量校验关卡"),
                            topic("相关且准确 → 用于生成"),
                            topic("不相关/不准确 → 丢弃或补充检索（Web 等）"),
                            topic("全部不准确 → 重写查询重检索，或回答无法确定"),
                        ],
                    ),
                    topic("一句话对比：传统假设「检索到的就是对的」；CRAG 质疑「检索到的真的对吗？」"),
                ],
            ),
            topic(
                "二、工作流程（论文三档）",
                children=[
                    topic("① 用户提问"),
                    topic("② 初步检索：知识库召回候选文档"),
                    topic(
                        "③ 检索质量评估（灵魂）",
                        children=[
                            topic("轻量级 Retrieval Evaluator 给文档 / 整体结果打分"),
                            topic("三档：Correct（绿）/ Ambiguous（黄）/ Incorrect（红）"),
                        ],
                    ),
                    topic("④ 按档位组合内部精炼知识 / 外部搜索知识 → 生成"),
                    topic(
                        "为什么要用",
                        children=[
                            topic("大幅降低幻觉"),
                            topic("私有库 + 公共知识混合题尤其好"),
                            topic("比普通 RAG 更鲁棒、更准确"),
                        ],
                    ),
                ],
            ),
            topic(
                "三、技术解构：三阶段架构",
                children=[
                    topic(
                        "Stage1 Retrieval",
                        children=[
                            topic("问题 x → 检索器 → 文档 d1, d2, …"),
                        ],
                    ),
                    topic(
                        "Stage2 Knowledge Correction（知识修正）",
                        children=[
                            topic(
                                "6.1 Retrieval Evaluator",
                                children=[
                                    topic("问：检索文档对 x 是否正确？"),
                                    topic("输出 Correct / Ambiguous / Incorrect"),
                                    topic("对应第一张图：Accurate vs Inaccurate Documents"),
                                ],
                            ),
                            topic(
                                "6.2 Knowledge Refinement（Correct 路径）",
                                children=[
                                    topic("Decompose：文档拆成 strip 片段"),
                                    topic("Filter：丢掉不相关片段"),
                                    topic("Recompose：重组为精炼内部知识 k_in"),
                                    topic("即使 Correct，也可能泥沙俱下，要去噪"),
                                ],
                            ),
                            topic(
                                "6.3 Knowledge Searching（Ambiguous / Incorrect）",
                                children=[
                                    topic("Rewrite：重写查询（更像搜索引擎问法）"),
                                    topic("例子：Death of a Batman; screenwriter; Wikipedia"),
                                    topic("Web Search → 候选 k1…kn → Select → 外部知识 k_ex"),
                                    topic("类比 Workflow 的 transform_query + Tavily"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "Stage3 Generation — 三种输入组合",
                        children=[
                            topic("Correct → 主要用 k_in（纯内部精炼）"),
                            topic("Ambiguous → k_in + k_ex（内部+外部）"),
                            topic("Incorrect → 主要用 k_ex（纯外部）"),
                            topic("工程简化：Document(relevant_text + search_text)；哪路空=没用哪路"),
                        ],
                    ),
                ],
            ),
            topic(
                "四、基础版代码：内部修正（不过网）",
                note="讲义第二节：相关性过滤 + 全无关则改写重检索。覆盖「评估 + 内部修正」。",
                children=[
                    topic(
                        "流程四步",
                        children=[
                            topic("[1] retriever.retrieve(query) 多召回（如 top_k=5）"),
                            topic("[2] 逐篇 RELEVANT / IRRELEVANT 过滤（CRAG 核心）"),
                            topic("[3] 若全部无关：REWRITE_PROMPT 改写 → 再检索再过滤"),
                            topic("[4] 仍无关则拒答；否则拼 context 生成"),
                        ],
                    ),
                    topic(
                        "关键 Prompt",
                        children=[
                            topic("RELEVANCE：只输出 RELEVANT 或 IRRELEVANT"),
                            topic("REWRITE：写得更清晰具体，只输出改写后问题"),
                            topic("ANSWER：仅依据资料回答"),
                        ],
                    ),
                    topic(
                        "实现要点",
                        children=[
                            topic("继承 CustomQueryEngine，封装评估+修正+生成"),
                            topic("评估 LLM 低温（讲义 qwen；本仓库可用 DeepSeek）"),
                            topic("verbose 打印每篇相关/无关，便于调试"),
                        ],
                    ),
                    topic(
                        "使用说明",
                        children=[
                            topic("本地 data/*.txt 当知识库"),
                            topic("环境变量：讲义 DASHSCOPE；完整版再加 TAVILY_API_KEY"),
                        ],
                    ),
                ],
            ),
            topic(
                "五、完整版：Workflow + Web 搜索",
                note="内部不足时转向 Tavily 等外部搜索；官方 Pack 写死 gpt-4，讲义手写 Workflow 换成通义。",
                children=[
                    topic(
                        "与基础版差别",
                        children=[
                            topic("基础版：全无关 → 还在同一库里改写重查"),
                            topic("完整版：出现不相关 → 重写查询 + Web 补充外部知识"),
                        ],
                    ),
                    topic(
                        "事件驱动步骤",
                        children=[
                            topic("ingest：documents → VectorStoreIndex（首次 run）"),
                            topic("prepare：存 index / Tavily / query_str"),
                            topic("retrieve：similarity_top_k=5 候选"),
                            topic("eval_relevance：逐篇 LLM yes/no（评估器）"),
                            topic("extract_relevant_texts：只留 yes 文本"),
                            topic("transform_query：有 no → 重写 + Tavily.search"),
                            topic("query_result：内外文本合并 SummaryIndex 再生成"),
                        ],
                    ),
                    topic(
                        "工程简化说明",
                        children=[
                            topic("论文三档 → 工程常简化为逐篇 yes/no"),
                            topic("只要有一篇 no，就触发 Web（Ambiguous+Incorrect 合并）"),
                            topic("想还原三档：改 eval 输出 correct/ambiguous/incorrect，分三条路径"),
                        ],
                    ),
                    topic(
                        "Workflow 概念速记",
                        children=[
                            topic("Event：step 间数据载体"),
                            topic("@step：收 Event 出新 Event"),
                            topic("Context.store：跨 step 共享字典"),
                            topic("run()：入口，参数变成 StartEvent"),
                        ],
                    ),
                ],
            ),
            topic(
                "六、核心知识点总结",
                children=[
                    topic("Corrective RAG = 普通 RAG + 检索质量评估 + 自动修正"),
                    topic("评估器：Correct / Ambiguous / Incorrect（工程可简化 yes/no）"),
                    topic("修正手段：知识精炼（内部去噪）+ Web 搜索（外部补充）"),
                    topic("收益：幻觉↓、过时信息↓、无关检索↓；私有+公共混合场景尤佳"),
                ],
            ),
            topic(
                "七、CRAG vs Self-RAG",
                children=[
                    topic("Self-RAG：管「查不查」+ 生成侧自我反思（Retrieve/ISREL/ISSUP/ISUSE）"),
                    topic("CRAG：管「查错了怎么办」——评估检索质量并纠正/外搜"),
                    topic("Self-RAG 重生成过程元认知；CRAG 重检索结果纠错与外部补充"),
                    topic("不互斥：可先 CRAG 保证资料靠谱，再 Self-RAG 保证生成有据"),
                    topic("口述口诀：Self-RAG=查不查；Corrective=查错了怎么办；Rerank=榜上谁第一"),
                ],
            ),
            topic(
                "八、实战启示与场景",
                children=[
                    topic(
                        "工程指导",
                        children=[
                            topic("不要迷信检索器：质量评估是安全带"),
                            topic("轻量专用评估器（论文 0.77B）可优于大而全 LLM 做相关性"),
                            topic("内部答不了就外搜，别闭门造车幻觉"),
                            topic("知识粒度：整篇硬塞不如拆 strip 再筛"),
                        ],
                    ),
                    topic(
                        "应用场景",
                        children=[
                            topic("企业问答：库匹配差时补权威来源，避免不懂装懂"),
                            topic("医疗咨询：精炼+外搜降低错误信息"),
                            topic("教育辅导：检索差时动态拿最新资料"),
                        ],
                    ),
                ],
            ),
            topic(
                "九、和本仓库 chroma文档管理 的对齐",
                children=[
                    topic(
                        "实现：semantic_search/app/service/crag.py",
                        children=[
                            topic("对齐课上 demo01 基础版：库内修正，不联网、不依赖千问 rerank"),
                            topic("评估/改写：Settings.llm（如 DeepSeek）"),
                            topic("filter_relevant_nodes：逐篇 RELEVANT/IRRELEVANT"),
                            topic("全无关 → rewrite_query_for_retrieval → retrieve_fn 再走混合+后处理"),
                            topic("只再来一轮，避免死循环"),
                        ],
                    ),
                    topic(
                        "接入位置",
                        children=[
                            topic("rag_service.ask：Pre → Mid(hybrid) → Post(三件套) → CRAG → 生成"),
                            topic("配置：CRAG_ENABLED / CRAG_VERBOSE（.env）"),
                            topic("响应：AskResponse.crag 带回评估明细与是否改写重试"),
                        ],
                    ),
                    topic(
                        "与完整版差距 / 可选演进",
                        children=[
                            topic("已有：评估过滤 + 改写重检索（内部）"),
                            topic("未接：Tavily Web、三档路径、Knowledge Refinement 拆 strip"),
                            topic("下一步：Ambiguous 时合并外搜；或先上 strip 级精炼"),
                        ],
                    ),
                ],
            ),
        ],
    )
    return [ch11, ch12]
