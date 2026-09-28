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
                "术语定义（本章必背）",
                children=[
                    topic(
                        "Self-RAG",
                        children=[
                            topic("定义：Self-Reflective Retrieval-Augmented Generation，带自我反思的检索增强生成"),
                            topic("要点：模型边生成边输出反思标记，动态决定检索与校正"),
                        ],
                    ),
                    topic(
                        "Reflection Tokens（反思令牌）",
                        children=[
                            topic("定义：插入生成过程的特殊控制标记，表达模型对自己行为的判断"),
                            topic("四种：Retrieve / ISREL / ISSUP / ISUSE"),
                        ],
                    ),
                    topic(
                        "Retrieve（检索决策）",
                        children=[
                            topic("定义：判断当前问题是否需要外部检索的标记/步骤"),
                            topic("取值直觉：YES=去查库；NO=直接用模型内部知识回答"),
                        ],
                    ),
                    topic(
                        "ISREL（Is Relevant，相关性）",
                        children=[
                            topic("定义：判断检索到的片段是否与问题相关、足以支撑作答"),
                            topic("作用：过滤噪声文档，避免无关资料进生成"),
                        ],
                    ),
                    topic(
                        "ISSUP（Is Supported，支持度）",
                        children=[
                            topic("定义：判断生成内容是否被检索证据支撑（打幻觉）"),
                            topic("常见档：FULLY / PARTIALLY / NO"),
                        ],
                    ),
                    topic(
                        "ISUSE（Is Useful，有用性）",
                        children=[
                            topic("定义：判断最终回答对用户问题的帮助程度"),
                            topic("常见：1~5 分，用于监控或候选择优"),
                        ],
                    ),
                    topic(
                        "Critic / Generator（批评家 / 生成器）",
                        children=[
                            topic("批评家：负责打反思标签的模型（训练阶段老师）"),
                            topic("生成器：同时学习「写什么」和「如何自评」的主模型"),
                        ],
                    ),
                    topic(
                        "Adaptive Retrieval（自适应检索）",
                        children=[
                            topic("定义：按 Retrieve 概率/阈值动态决定是否检索，而非固定总查"),
                        ],
                    ),
                    topic(
                        "软约束 vs 硬约束",
                        children=[
                            topic("软约束：调令牌权重，引导生成倾向（如更抠证据）"),
                            topic("硬约束：直接丢弃不合格候选（如 No Support）"),
                        ],
                    ),
                    topic(
                        "幻觉 Hallucination",
                        children=[
                            topic("定义：模型生成看似合理但无事实依据或与资料矛盾的内容"),
                            topic("Self-RAG 用 ISSUP 专门压制这类错误"),
                        ],
                    ),
                    topic(
                        "元认知 Metacognition",
                        children=[
                            topic("定义：对自身认知过程的认知——知道自己知不知道、查不查、答得好不好"),
                            topic("Self-RAG 的价值叙事：让 LLM 具备初级元认知"),
                        ],
                    ),
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
                "术语定义（本章必背）",
                children=[
                    topic(
                        "Corrective RAG / CRAG",
                        children=[
                            topic("定义：Corrective Retrieval-Augmented Generation，修正增强检索生成"),
                            topic("公式：CRAG = 标准 RAG + 检索质量校验 + 自动修正/补充检索"),
                            topic("一句话：不假设「检索到的就是对的」，先评估再决定怎么用"),
                        ],
                    ),
                    topic(
                        "Retrieval Evaluator（检索评估器）",
                        children=[
                            topic("定义：对召回文档相对问题的正确性/相关性打分或分档的模块"),
                            topic("论文三档：Correct / Ambiguous / Incorrect"),
                            topic("工程常见：逐篇 yes/no 或 RELEVANT/IRRELEVANT"),
                        ],
                    ),
                    topic(
                        "Correct（正确）",
                        children=[
                            topic("定义：检索结果整体足以正确支撑回答"),
                            topic("后续：走 Knowledge Refinement，主要用内部精炼知识 k_in"),
                        ],
                    ),
                    topic(
                        "Ambiguous（模糊）",
                        children=[
                            topic("定义：部分有用但不充分，或相关度存疑"),
                            topic("后续：内部精炼 + 外部搜索，组合 k_in + k_ex"),
                        ],
                    ),
                    topic(
                        "Incorrect（不正确）",
                        children=[
                            topic("定义：检索结果基本无法支撑正确回答（跑题/错误/空）"),
                            topic("后续：侧重外部知识搜索，主要用 k_ex"),
                        ],
                    ),
                    topic(
                        "Knowledge Refinement（知识精炼）",
                        children=[
                            topic("定义：对内部文档做 Decompose→Filter→Recompose，去噪留精华"),
                            topic("产物：精炼内部知识 k_in"),
                        ],
                    ),
                    topic(
                        "Knowledge Searching（知识搜索）",
                        children=[
                            topic("定义：内部不足时重写查询并检索外部（如 Web）补充知识"),
                            topic("产物：外部知识 k_ex"),
                        ],
                    ),
                    topic(
                        "k_in / k_ex",
                        children=[
                            topic("k_in：来自内部知识库并经精炼的上下文"),
                            topic("k_ex：来自外部搜索并经选择的上下文"),
                        ],
                    ),
                    topic(
                        "库内修正 vs 完整 CRAG",
                        children=[
                            topic("库内修正：评估过滤 + 改写后仍查同一知识库（本仓库路线）"),
                            topic("完整 CRAG：不足时还可 Web 搜索（讲义 Tavily Workflow）"),
                        ],
                    ),
                    topic(
                        "confidently wrong（自信地犯错）",
                        children=[
                            topic("定义：检索看似相关实则答非所问，模型仍斩钉截铁给出错误答案"),
                            topic("CRAG 要防的典型失败模式"),
                        ],
                    ),
                    topic(
                        "检索相关性 ≠ 答案准确性",
                        children=[
                            topic("定义：向量相近或关键词重合，不等于文档能正确回答该问题"),
                            topic("例子：《蝙蝠侠之死》编剧 vs 1989《蝙蝠侠》编剧 Hamm"),
                        ],
                    ),
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
                "九、对照 chroma文档管理：代码级走读",
                note="主路径：RagAskService.ask → apply_crag → synthesize。启动 python chroma文档管理/run.py → :8003",
                children=[
                    topic(
                        "在 /ask 流水线中的精确位置",
                        children=[
                            topic("① prepare_retrieval_queries（Pre）"),
                            topic("② 每路 _build_retriever：向量+BM25 QueryFusion（Mid）"),
                            topic("③ 多 query 时 merge_nodes_rrf（查询间融合）"),
                            topic("④ apply_postprocessors：rerank→压缩→LongContextReorder（Post）"),
                            topic("⑤ apply_crag（本章）← 过滤无关；全无关则改写后 _retrieve_pipeline 再跑一遍 Mid+Post"),
                            topic("⑥ get_response_synthesizer(compact)+ASK_QA_PROMPT 生成；sources 用用户原问题对应的真实块"),
                        ],
                    ),
                    topic(
                        "crag.py 函数对照讲义",
                        children=[
                            topic("_is_relevant ≈ 讲义 Retrieval Evaluator（二值 RELEVANT/IRRELEVANT）"),
                            topic("filter_relevant_nodes ≈ 基础版 _filter_relevant + verbose 打印"),
                            topic("rewrite_query_for_retrieval ≈ 讲义 REWRITE_PROMPT（全无关才触发）"),
                            topic("apply_crag ≈ CorrectiveRAGQueryEngine.custom_query 的评估+修正段"),
                            topic("retrieve_fn 注入：保证重试仍走混合检索+三件套，不是裸向量"),
                            topic("无 LLM 时 _is_relevant 直接 True：避免把结果滤空"),
                        ],
                    ),
                    topic(
                        "crag 响应字段（前端 index.html 会展示）",
                        children=[
                            topic("enabled / message：是否开启、走了哪条分支"),
                            topic("before_count → after_count：过滤前后篇数"),
                            topic("retried + rewritten_query：是否纠错改写及新问句"),
                            topic("eval[]：每篇 rank/relevant/preview，便于作业演示与排障"),
                            topic("message 取值：filtered / rewrote_and_filtered / no_relevant_after_retry / …"),
                        ],
                    ),
                    topic(
                        "开关与默认",
                        children=[
                            topic("CRAG_ENABLED=true（默认开）"),
                            topic("CRAG_VERBOSE=true：终端打印 [CRAG] 文档 i：相关/无关"),
                            topic("评估模型=Settings.llm（与问答同一套，如 DeepSeek），非单独小评估器"),
                        ],
                    ),
                    topic(
                        "与讲义完整版（Workflow+Tavily）差距",
                        children=[
                            topic("已落地：库内评估过滤 + 一轮改写重检索（demo01 路线）"),
                            topic("未落地：Correct/Ambiguous/Incorrect 三档分流"),
                            topic("未落地：Knowledge Refinement 拆 strip→滤→重组"),
                            topic("未落地：Tavily / Web 外搜；Ambiguous 时 k_in+k_ex"),
                            topic("演进优先级：① strip 精炼 ② 三档 ③ 可选外搜（注意内网/合规）"),
                        ],
                    ),
                    topic(
                        "排障口诀（结合本项目）",
                        children=[
                            topic("after_count=0：看 eval 是否全 IRRELEVANT → 问法/库覆盖/阈值过严"),
                            topic("retried=true 仍空：改写句是否偏离；检查混合检索是否回退成纯向量"),
                            topic("相关篇被误杀：看 LLM 是否稳定；可临时 CRAG_ENABLED=0 对比"),
                            topic("延迟高：CRAG 每篇一次 complete；可先减小 k / RETRIEVE_CANDIDATES"),
                        ],
                    ),
                    topic("全文件/API 对照见第 13 章"),
                ],
            ),
        ],
    )

    ch13 = topic(
        "13 chroma文档管理：项目全链路对照",
        note=(
            "把第 08~12 章方法映射到本仓库搜索引擎。"
            "根目录：chroma文档管理/；包：semantic_search/；启动：python chroma文档管理/run.py → http://127.0.0.1:8003/"
        ),
        children=[
            topic(
                "〇、一张总图：用户问一句会发生什么",
                children=[
                    topic("浏览器 static/index.html → POST /ask {question,k,strategy}"),
                    topic("main.ask → RagAskService.ask（编排层）"),
                    topic("Pre：pre_retrieval.prepare_retrieval_queries"),
                    topic("Mid：engine._build_retriever → 向量±BM25；多 query 则 merge_nodes_rrf"),
                    topic("Post：retrieval_optimize.apply_postprocessors 三件套"),
                    topic("CRAG：crag.apply_crag（可改写重跑 Mid+Post）"),
                    topic("Gen：response_synthesizer + ASK_QA_PROMPT；返回 answer/sources/pre_retrieval/crag"),
                ],
            ),
            topic(
                "术语定义（项目里会碰到的词）",
                children=[
                    topic(
                        "Native RAG",
                        children=[
                            topic("定义：最朴素的检索增强：问句→向量检索 Top-K→塞进 Prompt→生成"),
                            topic("本项目底座仍是 Native，上面叠了 Pre/Mid/Post/CRAG"),
                        ],
                    ),
                    topic(
                        "SemanticSearchEngine",
                        children=[
                            topic("定义：engine.py 中的核心引擎类，管 Embedding/LLM/Chroma/分块/索引/检索"),
                        ],
                    ),
                    topic(
                        "RagAskService",
                        children=[
                            topic("定义：/ask 编排层，按 Pre→Mid→Post→CRAG→Gen 串完整作业链路"),
                        ],
                    ),
                    topic(
                        "Node / NodeWithScore",
                        children=[
                            topic("Node：LlamaIndex 里一块可检索文本（通常=一个 chunk）"),
                            topic("NodeWithScore：带检索分数的节点，融合/重排会改 score"),
                        ],
                    ),
                    topic(
                        "Chunk / 分块",
                        children=[
                            topic("定义：把长文档切成适合 embedding 与召回的小段"),
                            topic("本项目：Sentence / Token / Semantic 三种 splitter"),
                        ],
                    ),
                    topic(
                        "strategy（检索前策略）",
                        children=[
                            topic("定义：/ask 请求里控制查询怎么预处理的枚举"),
                            topic("取值：none / clean / rewrite（默认）/ hyde"),
                        ],
                    ),
                    topic(
                        "QueryFusionRetriever",
                        children=[
                            topic("定义：LlamaIndex 多检索器融合器；本项目用它做向量+BM25 同库混合"),
                            topic("mode=reciprocal_rerank 即按 RRF 融排名"),
                        ],
                    ),
                    topic(
                        "BM25",
                        children=[
                            topic("定义：经典稀疏关键词检索算法，擅长专名、编号、精确词面"),
                            topic("中文必须配合分词（本项目 jieba）"),
                        ],
                    ),
                    topic(
                        "RRF（Reciprocal Rank Fusion）",
                        children=[
                            topic("定义：用「排名倒数」融合多路结果，不依赖原始分数量纲"),
                            topic("本项目两处：路内 QueryFusion；多 query 时 merge_nodes_rrf"),
                        ],
                    ),
                    topic(
                        "node_postprocessors",
                        children=[
                            topic("定义：检索后、生成前的节点后处理器列表，按顺序串行"),
                            topic("本项目三件套：Rerank → 压缩 → LongContextReorder"),
                        ],
                    ),
                    topic(
                        "Cross-Encoder / Bi-Encoder",
                        children=[
                            topic("Bi-Encoder：查询与文档各自编码再比相似度，快，适合粗召回"),
                            topic("Cross-Encoder：query+doc 一起进模型打分，准但慢，适合精排"),
                        ],
                    ),
                    topic(
                        "SentenceEmbeddingOptimizer（上下文压缩）",
                        children=[
                            topic("定义：按句与查询的相似度裁掉低相关句子，减少噪声与 token"),
                        ],
                    ),
                    topic(
                        "LongContextReorder",
                        children=[
                            topic("定义：把最相关片段放到上下文首尾，对抗 Lost in the Middle"),
                        ],
                    ),
                    topic(
                        "Lost in the Middle",
                        children=[
                            topic("定义：长上下文里，模型对中间段落记忆/利用率明显低于首尾"),
                        ],
                    ),
                    topic(
                        "HyDE",
                        children=[
                            topic("定义：Hypothetical Document Embeddings，先生成假想答案文档再拿去检索"),
                            topic("注意：假想文只用于检索，不能当事实引用（本项目 sources 不用它）"),
                        ],
                    ),
                    topic(
                        "pre_retrieval / crag（响应字段）",
                        children=[
                            topic("pre_retrieval：检索前中间产物（原句/清洗/改写/HyDE/检索列表）"),
                            topic("crag：Corrective RAG 过程（过滤前后篇数、是否重试、评估明细）"),
                        ],
                    ),
                    topic(
                        "Chroma / Collection",
                        children=[
                            topic("Chroma：本项目使用的向量数据库"),
                            topic("Collection：一个命名向量集合（默认 native_rag）"),
                        ],
                    ),
                ],
            ),
            topic(
                "一、目录与职责（打开代码用）",
                children=[
                    topic("run.py：启动入口，挂 sys.path 后调 semantic_search.__main__"),
                    topic("app/main.py：FastAPI 路由 /ask /search /query /chat /ingest /upload …"),
                    topic("app/engine.py：Embedding/LLM/Chroma/分块/索引；_build_retriever / query / chat"),
                    topic("app/config.py：模型、分块、HYBRID/RERANK/COMPRESS/REORDER/CRAG 开关"),
                    topic("app/schemas.py：AskRequest/AskResponse、PreRetrievalInfo、CragInfo"),
                    topic("app/service/pre_retrieval.py：清洗 / 重写 / HyDE"),
                    topic("app/service/retrieval_optimize.py：混合召回 + 后处理三件套"),
                    topic("app/service/crag.py：Corrective RAG 库内修正"),
                    topic("app/service/rag_service.py：/ask 专用编排（Pre→Mid→Post→CRAG→Gen）"),
                    topic("static/index.html：问答 UI，展示策略过程、CRAG 过滤、来源卡片"),
                    topic("data/：默认灌库 md/txt；chroma_db/：向量持久化"),
                ],
            ),
            topic(
                "二、章节 ↔ 模块映射",
                children=[
                    topic(
                        "第 08 检索前 → pre_retrieval.py + /ask?strategy=",
                        children=[
                            topic("none：原句单路"),
                            topic("clean：去口语填充 + 术语表（电脑→笔记本电脑 等）"),
                            topic("rewrite（默认）：清洗句 + 改写句双路，防改歪"),
                            topic("hyde：清洗句 + 假想说明文双路；假想文只检索不当引用"),
                            topic("前端：pre_retrieval 盒子展示 original/clean/rewritten/hyde_doc"),
                        ],
                    ),
                    topic(
                        "第 09 检索中 → retrieval_optimize.build_hybrid_retriever",
                        children=[
                            topic("HYBRID_ENABLED：向量 as_retriever + BM25(jieba) → QueryFusionRetriever"),
                            topic("默认 mode=reciprocal_rerank（RRF）；失败回退纯向量"),
                            topic("粗排窗口：RETRIEVE_CANDIDATES（默认 20）给精排留余量"),
                            topic("/ask 多 query：路内融合后再 merge_nodes_rrf 做查询间融合"),
                        ],
                    ),
                    topic(
                        "第 10 检索后 → build_node_postprocessors / apply_postprocessors",
                        children=[
                            topic("Rerank：默认本地 SentenceTransformerRerank(bge-reranker-base)"),
                            topic("RERANK_PROVIDER=dashscope 才走千问 qwen3-rerank"),
                            topic("压缩：SentenceEmbeddingOptimizer + 中文切句 + COMPRESS_PERCENTILE"),
                            topic("排版：LongContextReorder 对抗 Lost in the Middle"),
                            topic("query/chat：挂在 RetrieverQueryEngine / chat_engine 的 node_postprocessors"),
                        ],
                    ),
                    topic(
                        "第 11 Self-RAG → 尚未成独立模块",
                        children=[
                            topic("缺口：Retrieve 门控、ISSUP 验据、ISUSE 打分"),
                            topic("可借用：CRAG 的相关性过滤 ≈ ISREL"),
                            topic("落地建议见第 11 章第九节"),
                        ],
                    ),
                    topic(
                        "第 12 CRAG → crag.py + rag_service 第⑤步",
                        children=[
                            topic("默认开启；全无关改写后 _retrieve_pipeline 重跑"),
                            topic("不联网：无 Tavily，属讲义基础版路线"),
                        ],
                    ),
                ],
            ),
            topic(
                "三、API 怎么选",
                children=[
                    topic("/ask：作业主链路，带 strategy + pre_retrieval + crag（推荐演示）"),
                    topic("/search：只检索不生成，看混合/后处理召回效果"),
                    topic("/query：一次性 RAG，有后处理，无 Pre 多策略、无 CRAG 编排"),
                    topic("/chat：多轮记忆；后处理挂引擎，会话键含 hybrid/rerank 标志"),
                    topic("/ingest /upload：灌库；会 _invalidate_retrieval_cache 重建 BM25"),
                    topic("/stats /health：看库规模与 hybrid_enabled/rerank_enabled 等"),
                ],
            ),
            topic(
                "四、环境变量开关速查（config.py）",
                children=[
                    topic("HYBRID_ENABLED / HYBRID_FUSION_MODE / RETRIEVE_CANDIDATES"),
                    topic("RERANK_ENABLED / RERANK_PROVIDER(local|dashscope|none) / RERANK_MODEL / RERANK_TOP_N"),
                    topic("COMPRESS_ENABLED / COMPRESS_PERCENTILE"),
                    topic("REORDER_ENABLED"),
                    topic("CRAG_ENABLED / CRAG_VERBOSE"),
                    topic("CHUNK_SIZE / CHUNK_OVERLAP / SIMILARITY_TOP_K"),
                    topic("EMBEDDING_* / LLM（DeepSeek 等）/ DASHSCOPE_API_KEY（仅千问路径需要）"),
                    topic("SEARCH_HOST / SEARCH_PORT（默认 8003）"),
                ],
            ),
            topic(
                "五、和讲义 Advanced 闭环四问对照",
                children=[
                    topic("查什么 → strategy 重写/HyDE（第 08）"),
                    topic("去哪查 → 同库向量+BM25（第 09）；未做多目录多路 channel"),
                    topic("查得准 → 本地 bge rerank（第 10）"),
                    topic("怎么用 → 压缩+长上下文重排+引用约束；错了再 CRAG 纠（第 10/12）"),
                    topic("查不查 → Self-RAG Retrieve 尚未接（第 11 缺口）"),
                ],
            ),
            topic(
                "六、效果不好时：按本项目排查",
                children=[
                    topic("① /stats 库是否为空；分块是否切断关键句"),
                    topic("② 换 strategy：rewrite↔hyde↔clean，看 pre_retrieval 双路是否合理"),
                    topic("③ 专名搜不到：确认 HYBRID_ENABLED 与 jieba/bm25 依赖"),
                    topic("④ 相关在后面：确认 RERANK_ENABLED 与本地 bge 是否加载成功"),
                    topic("⑤ 答案飘：看压缩是否过猛；Prompt 是否仍「仅依据上下文」"),
                    topic("⑥ CRAG 滤光：看 crag.eval；必要时 CRAG_VERBOSE 对照终端"),
                    topic("⑦ 延迟：降 k/候选；关 CRAG 或压缩做 A/B"),
                ],
            ),
            topic(
                "七、建议的下一刀改造（优先级）",
                children=[
                    topic("P0：Self-RAG Retrieve 门控（闲聊不查）"),
                    topic("P1：生成后 ISSUP 验据 + 不足则重写"),
                    topic("P2：CRAG strip 级 Knowledge Refinement（对齐论文 Correct 路径）"),
                    topic("P3：可选 Web 补充（仅公网场景；内网知识库慎开）"),
                    topic("P4：多目录多路召回 + channel 元数据（第 09 进阶）"),
                ],
            ),
        ],
    )
    return [ch11, ch12, ch13]
