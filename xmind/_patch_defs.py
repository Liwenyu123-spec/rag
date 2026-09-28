# -*- coding: utf-8 -*-
"""Insert 术语定义 sections into chapters 07-10 of build_xmind.py."""
from pathlib import Path

p = Path(__file__).resolve().parent / "build_xmind.py"
build = p.read_text(encoding="utf-8")

# ---- ch08 after 〇、总览 ----
old08 = '''                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("查询侧：清洗 → 澄清 → 重写 / 扩展 / HyDE / Step-Back / 分解"),
                        topic("文档侧（离线）：分块 → 元数据 → 增强 → 多表示 / 路由规则"),
                        topic("原则：先判断病症，再选一种方法；不要一次全开"),
                    ],
                ),
                topic(
                    "方法1：查询文本清洗",'''

new08 = '''                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("查询侧：清洗 → 澄清 → 重写 / 扩展 / HyDE / Step-Back / 分解"),
                        topic("文档侧（离线）：分块 → 元数据 → 增强 → 多表示 / 路由规则"),
                        topic("原则：先判断病症，再选一种方法；不要一次全开"),
                    ],
                ),
                topic(
                    "术语定义（本章必背）",
                    children=[
                        topic(
                            "Pre-retrieval（检索前优化）",
                            children=[
                                topic("定义：进入向量库检索之前，优化「问什么」和「库怎么建」"),
                                topic("两侧：查询侧（在线）+ 文档侧（多离线）"),
                            ],
                        ),
                        topic(
                            "查询清洗 Query Cleaning",
                            children=[
                                topic("定义：去掉口语废话、标点噪声，并做术语标准化"),
                            ],
                        ),
                        topic(
                            "查询重写 Query Rewriting",
                            children=[
                                topic("定义：把口语/模糊问题改写成更适合检索的表达，保留原意"),
                            ],
                        ),
                        topic(
                            "查询扩展 Query Expansion",
                            children=[
                                topic("定义：生成多个同义/近义变体，多路检索再合并，抬召回"),
                            ],
                        ),
                        topic(
                            "HyDE（Hypothetical Document Embeddings）",
                            children=[
                                topic("定义：先让 LLM 写一篇「假想答案文档」，再用该文档去向量检索"),
                                topic("原因：短问句与长文档分布差异大，假想文更像库里的文档"),
                            ],
                        ),
                        topic(
                            "Step-Back（后退提问）",
                            children=[
                                topic("定义：把具体问题先退成更宽泛的背景问题，补全局知识再答细问"),
                            ],
                        ),
                        topic(
                            "查询分解 Query Decomposition / Sub-Question",
                            children=[
                                topic("定义：复杂多跳/比较题拆成多个原子子问题，分别检索再综合"),
                            ],
                        ),
                        topic(
                            "Chunking（分块）",
                            children=[
                                topic("定义：长文切成适合 embedding 与召回的片段"),
                                topic("常见：固定长度+overlap、按句、按语义、父子块"),
                            ],
                        ),
                        topic(
                            "Overlap（重叠窗口）",
                            children=[
                                topic("定义：相邻块保留一段重叠文本，减轻边界切断语义"),
                            ],
                        ),
                        topic(
                            "父子块 / Small-to-Big",
                            children=[
                                topic("定义：小块负责命中，返回时合并到父级大上下文"),
                            ],
                        ),
                        topic(
                            "元数据 Metadata",
                            children=[
                                topic("定义：附着在文档/块上的结构化字段（标题、时间、来源、权限等）"),
                                topic("用途：预过滤、路由、引用展示"),
                            ],
                        ),
                        topic(
                            "意图路由 Intent Routing",
                            children=[
                                topic("定义：按问题类型选择不同索引或工具（FAQ vs 技术文档）"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法1：查询文本清洗",'''

if old08 not in build:
    raise SystemExit("ch08 anchor not found")
build = build.replace(old08, new08, 1)

# ---- ch09 after 〇、总览 ----
old09 = '''                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("目标：提升召回率 Recall + 相关性（少漏、少偏）"),
                        topic("两条主线：混合检索（同库多算法） / 多路召回（多源多通道）"),
                        topic("胶水：RRF / relative_score 加权 / Round-Robin"),
                        topic("落点：都在 RAG 第 4 步「检索召回」；前三步仍是加载→分块→向量化入库"),
                        topic("和检索前区别：第 08 章改「问什么」；本章改「怎么查、去哪查」"),
                    ],
                ),
                topic(
                    "指标预习：召回率 vs 精确率",'''

new09 = '''                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("目标：提升召回率 Recall + 相关性（少漏、少偏）"),
                        topic("两条主线：混合检索（同库多算法） / 多路召回（多源多通道）"),
                        topic("胶水：RRF / relative_score 加权 / Round-Robin"),
                        topic("落点：都在 RAG 第 4 步「检索召回」；前三步仍是加载→分块→向量化入库"),
                        topic("和检索前区别：第 08 章改「问什么」；本章改「怎么查、去哪查」"),
                    ],
                ),
                topic(
                    "术语定义（本章必背）",
                    children=[
                        topic(
                            "Retrieval（检索中优化）",
                            children=[
                                topic("定义：在「怎么查、用什么算法/通道查」上优化，抬召回与相关性"),
                            ],
                        ),
                        topic(
                            "召回率 Recall",
                            children=[
                                topic("定义：该找到的相关内容里，实际找回来的比例（少漏）"),
                            ],
                        ),
                        topic(
                            "精确率 Precision",
                            children=[
                                topic("定义：找回来的内容里，真正相关的比例（少脏）"),
                            ],
                        ),
                        topic(
                            "稠密向量 Dense Embedding",
                            children=[
                                topic("定义：文本编成几乎每维都有值的向量，擅长语义/同义匹配"),
                            ],
                        ),
                        topic(
                            "稀疏检索 Sparse（如 BM25）",
                            children=[
                                topic("定义：基于词面统计的倒排检索，多数维度为 0，擅长专名/编号"),
                            ],
                        ),
                        topic(
                            "混合检索 Hybrid Search",
                            children=[
                                topic("定义：同一知识库上同时跑稠密+稀疏（或多种算法），再融合结果"),
                                topic("口诀：同库多算法，取长补短"),
                            ],
                        ),
                        topic(
                            "多路召回 Multi-channel",
                            children=[
                                topic("定义：多个独立数据源/索引通道各自召回，再去重融合"),
                                topic("口诀：多源多赛道，先保召回"),
                            ],
                        ),
                        topic(
                            "RRF 倒数排名融合",
                            children=[
                                topic("定义：Reciprocal Rank Fusion；score=Σ 1/(k+rank)，k 常取 60"),
                                topic("优点：不要求各路原始分数同一量纲"),
                            ],
                        ),
                        topic(
                            "relative_score 融合",
                            children=[
                                topic("定义：先把各路分数归一化再加权求和的融合方式"),
                            ],
                        ),
                        topic(
                            "Round-Robin（轮询融合）",
                            children=[
                                topic("定义：各路结果轮流取一条拼成最终列表，简单保多样性"),
                            ],
                        ),
                        topic(
                            "ColBERT / 多向量表示",
                            children=[
                                topic("定义：文档按 token 级多向量存储，查询时做细粒度 MaxSim 交互"),
                            ],
                        ),
                        topic(
                            "SPLADE 等学习稀疏向量",
                            children=[
                                topic("定义：模型学出的稀疏表示，可走倒排，兼顾词面与一点语义"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "指标预习：召回率 vs 精确率",'''

if old09 not in build:
    raise SystemExit("ch09 anchor not found")
build = build.replace(old09, new09, 1)

# ---- ch10 after 〇、总览 ----
old10 = '''                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("目标：召回结果送入 LLM 前，做重排 + 精简 + 重排版，抬生成质量"),
                        topic("位置：第 4 步检索召回之后、第 5 步喂模型之前"),
                        topic("入口：node_postprocessors=[...]，按列表顺序串行加工 nodes"),
                        topic("三件套：Rerank → SentenceEmbeddingOptimizer → LongContextReorder"),
                        topic("和第 08/09 章：前改问句、中改召回；本章改「怎么用召回结果」"),
                    ],
                ),
                topic(
                    "方法1：两阶段检索与重排序 Re-ranking",'''

new10 = '''                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("目标：召回结果送入 LLM 前，做重排 + 精简 + 重排版，抬生成质量"),
                        topic("位置：第 4 步检索召回之后、第 5 步喂模型之前"),
                        topic("入口：node_postprocessors=[...]，按列表顺序串行加工 nodes"),
                        topic("三件套：Rerank → SentenceEmbeddingOptimizer → LongContextReorder"),
                        topic("和第 08/09 章：前改问句、中改召回；本章改「怎么用召回结果」"),
                    ],
                ),
                topic(
                    "术语定义（本章必背）",
                    children=[
                        topic(
                            "Post-retrieval（检索后优化）",
                            children=[
                                topic("定义：召回之后、喂给 LLM 之前，对候选做重排/压缩/重排版等加工"),
                            ],
                        ),
                        topic(
                            "Node Postprocessor",
                            children=[
                                topic("定义：LlamaIndex 中对 NodeWithScore 列表做后处理的组件接口"),
                                topic("串法：node_postprocessors=[...] 按列表顺序执行"),
                            ],
                        ),
                        topic(
                            "Re-ranking（重排序）",
                            children=[
                                topic("定义：用更准（通常更贵）的模型对粗召回候选二次打分排序"),
                                topic("目标：抬精确率，把最相关顶到前面"),
                            ],
                        ),
                        topic(
                            "两阶段检索",
                            children=[
                                topic("定义：粗召回（快、广）+ 精排（慢、准）的工业标配链路"),
                            ],
                        ),
                        topic(
                            "Bi-Encoder（双塔）",
                            children=[
                                topic("定义：查询与文档各自编码再比向量相似度；文档可离线预计算"),
                            ],
                        ),
                        topic(
                            "Cross-Encoder（交叉编码器）",
                            children=[
                                topic("定义：把 query 与 doc 拼在一起进模型直接出相关性分；准但慢"),
                            ],
                        ),
                        topic(
                            "Contextual Compression（上下文压缩）",
                            children=[
                                topic("定义：只保留片段里与问题最相关的句子，丢掉冗余"),
                                topic("和重排区别：重排选「哪些块」；压缩选「块里哪几句」"),
                            ],
                        ),
                        topic(
                            "SentenceEmbeddingOptimizer",
                            children=[
                                topic("定义：按句 embedding 与查询相似度做裁剪的压缩后处理器"),
                                topic("常用：percentile_cutoff / threshold_cutoff"),
                            ],
                        ),
                        topic(
                            "Long-Context Reorder（长上下文重排）",
                            children=[
                                topic("定义：调整已选片段顺序，最相关放首尾，减轻中间遗忘"),
                                topic("注意：只改顺序，不改选集与内容"),
                            ],
                        ),
                        topic(
                            "Lost in the Middle",
                            children=[
                                topic("定义：长上下文中，模型对中间段落的利用显著弱于首尾"),
                            ],
                        ),
                        topic(
                            "Citation / 引用溯源",
                            children=[
                                topic("定义：让答案标明来自哪条资料，便于核查并抑制瞎编"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法1：两阶段检索与重排序 Re-ranking",'''

if old10 not in build:
    raise SystemExit("ch10 anchor not found")
build = build.replace(old10, new10, 1)

# ---- ch07: after 核心定位 block's first children area - find "核心定位" ----
old07 = '''                topic(
                    "核心定位",
                    children=[
                        topic(
                            "相对 Native RAG 多了什么",
                            children=[
                                topic("Native：提问 → 向量检索 Top-K → 塞进 Prompt → 生成"),
                                topic("Advanced：检索前改查询、检索中多路召回、检索后重排压缩"),
                                topic("不是检索一次就完事，每个环节都尽量优化"),
                            ],
                        ),'''

# The above might not match exactly - let me check what's actually in the file
if old07 not in build:
    # try alternate - read a snippet
    idx = build.find('"核心定位"')
    print("core定位 idx", idx)
    print(repr(build[idx:idx+400]))
    raise SystemExit("ch07 anchor not found exactly")

new07 = '''                topic(
                    "核心定位",
                    children=[
                        topic(
                            "相对 Native RAG 多了什么",
                            children=[
                                topic("Native：提问 → 向量检索 Top-K → 塞进 Prompt → 生成"),
                                topic("Advanced：检索前改查询、检索中多路召回、检索后重排压缩"),
                                topic("不是检索一次就完事，每个环节都尽量优化"),
                            ],
                        ),'''

# We'll insert definitions as sibling after 核心定位 instead
# Find closing of 核心定位 section - better approach: insert after 核心定位 entire topic

marker07 = '                topic(\n                    "核心定位",'
# We'll replace a unique following section start
# Actually insert before "一、检索前优化"
old07b = '''                topic(
                    "一、检索前优化（Pre-retrieval）",
                    note="目标：让查询更精准，让文档库更适合检索。专训见第 08 章。",'''

# Check if this exists
if old07b not in build:
    idx = build.find("一、检索前优化（Pre-retrieval）")
    print("ch07 pre idx", idx)
    print(repr(build[idx-80:idx+200]))
    raise SystemExit("ch07b not found")

new07b = '''                topic(
                    "术语定义（Advanced 总览必背）",
                    children=[
                        topic(
                            "RAG（Retrieval-Augmented Generation）",
                            children=[
                                topic("定义：检索增强生成——先从外部知识库取相关资料，再让 LLM 基于资料生成答案"),
                            ],
                        ),
                        topic(
                            "Native RAG",
                            children=[
                                topic("定义：最简流水线：提问→向量检索 Top-K→拼 Prompt→生成，中间少优化"),
                            ],
                        ),
                        topic(
                            "Advanced RAG",
                            children=[
                                topic("定义：在 Native 上对检索前/中/后系统优化，形成可组合的增强链路"),
                            ],
                        ),
                        topic(
                            "Pre / Mid / Post-retrieval",
                            children=[
                                topic("Pre：优化问句与索引准备（查什么）"),
                                topic("Mid：优化召回算法与通道（怎么查）"),
                                topic("Post：优化已召回材料再喂模型（怎么用）"),
                            ],
                        ),
                        topic(
                            "Embedding（嵌入）",
                            children=[
                                topic("定义：把文本映射到向量空间，使语义相近的文本距离更近"),
                            ],
                        ),
                        topic(
                            "Top-K",
                            children=[
                                topic("定义：检索返回相似度最高的前 K 条候选"),
                            ],
                        ),
                        topic(
                            "Self-RAG",
                            children=[
                                topic("定义：生成过程中自我决定是否检索、资料好不好、答案有无依据（见第 11 章）"),
                            ],
                        ),
                        topic(
                            "Corrective RAG（CRAG）",
                            children=[
                                topic("定义：评估检索质量，差则改写/外搜纠正后再生成（见第 12 章）"),
                            ],
                        ),
                        topic(
                            "RAG-Fusion",
                            children=[
                                topic("定义：多查询并行检索 + RRF 融排名的完整打法"),
                            ],
                        ),
                        topic(
                            "Agentic RAG",
                            children=[
                                topic("定义：由 Agent 规划检索步骤与工具调用的灵活 RAG 形态"),
                            ],
                        ),
                        topic(
                            "GraphRAG",
                            children=[
                                topic("定义：基于实体关系图做检索/摘要，适合多跳与全局主题"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "一、检索前优化（Pre-retrieval）",
                    note="目标：让查询更精准，让文档库更适合检索。专训见第 08 章。",'''

build = build.replace(old07b, new07b, 1)

p.write_text(build, encoding="utf-8")
print("patched definitions into ch07-10")
