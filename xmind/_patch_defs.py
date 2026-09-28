# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parent / "build_xmind.py"
build = p.read_text(encoding="utf-8")
n = 0

def must_replace(old, new, label):
    global build, n
    if old not in build:
        raise SystemExit(f"missing: {label}")
    build = build.replace(old, new, 1)
    n += 1
    print("ok", label)

# ch07
old07 = '''                topic(
                    "一、检索前优化（Pre-retrieval）",
                    note="目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章；检索中见第 09 章。",
                    children=['''
new07 = '''                topic(
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
                    note="目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章；检索中见第 09 章。",
                    children=['''
must_replace(old07, new07, "ch07")

# ch08
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
                        topic("Pre-retrieval（检索前优化）：进入检索前，优化「问什么」和「库怎么建」"),
                        topic("查询清洗：去口语废话与标点噪声，并做术语标准化"),
                        topic("查询重写：把口语/模糊问题改成更适合检索的表达，保留原意"),
                        topic("查询扩展：生成多个同义变体并行检索再合并，抬召回"),
                        topic("HyDE：先生成假想答案文档再拿去向量检索（假想文不当事实引用）"),
                        topic("Step-Back：把具体问题先退成更宽泛背景问题"),
                        topic("查询分解：复杂多跳/比较题拆成原子子问题分别检索再综合"),
                        topic("Chunking（分块）：长文切成适合 embedding 与召回的片段"),
                        topic("Overlap：相邻块保留重叠，减轻边界切断语义"),
                        topic("父子块/Small-to-Big：小块命中，返回父级大上下文"),
                        topic("元数据 Metadata：标题/时间/来源/权限等，供过滤与引用"),
                        topic("意图路由：按问题类型选择不同索引或工具"),
                    ],
                ),
                topic(
                    "方法1：查询文本清洗",'''
must_replace(old08, new08, "ch08")

# ch09
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
                        topic("Retrieval（检索中）：优化「怎么查、用什么算法/通道查」"),
                        topic("召回率 Recall：该找到的相关内容里实际找回来的比例（少漏）"),
                        topic("精确率 Precision：找回来的内容里真正相关的比例（少脏）"),
                        topic("稠密向量：几乎每维都有值，擅长语义/同义匹配"),
                        topic("稀疏检索（BM25等）：词面/倒排，擅长专名与编号"),
                        topic("混合检索 Hybrid：同库同时跑稠密+稀疏再融合"),
                        topic("多路召回 Multi-channel：多源/多索引各自召回再融合"),
                        topic("RRF：倒数排名融合 score=Σ1/(k+rank)，不要求分数量纲一致"),
                        topic("relative_score：各路分数归一化后再加权融合"),
                        topic("Round-Robin：各路轮流取一条，简单保多样性"),
                        topic("ColBERT：token 级多向量交互（MaxSim），更细更吃资源"),
                        topic("SPLADE：学习型稀疏向量，兼顾词面与一点语义"),
                    ],
                ),
                topic(
                    "指标预习：召回率 vs 精确率",'''
must_replace(old09, new09, "ch09")

# ch10
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
                        topic("Post-retrieval（检索后）：召回之后、喂 LLM 之前加工候选"),
                        topic("Node Postprocessor：对 NodeWithScore 列表串行后处理的组件"),
                        topic("Re-ranking：用更准模型对粗召回候选二次打分排序"),
                        topic("两阶段检索：粗召回（快广）+ 精排（慢准）"),
                        topic("Bi-Encoder：查询/文档各自编码再比相似度，快"),
                        topic("Cross-Encoder：query+doc 一起进模型打分，准但慢"),
                        topic("上下文压缩：只留与问题最相关的句子，丢掉冗余"),
                        topic("SentenceEmbeddingOptimizer：按句-查询相似度裁剪的压缩器"),
                        topic("LongContextReorder：最相关放首尾，对抗中间遗忘"),
                        topic("Lost in the Middle：长上下文中模型对中间段落利用率偏低"),
                        topic("Citation：答案标明来源，便于核查并抑制瞎编"),
                    ],
                ),
                topic(
                    "方法1：两阶段检索与重排序 Re-ranking",'''
must_replace(old10, new10, "ch10")

p.write_text(build, encoding="utf-8")
print("done", n)
