# -*- coding: utf-8 -*-
"""Chapter 17 GraphRAG 使用 — from Feishu 02_GraphRag的使用."""


def make_chapter(topic):
    return topic(
        "17 GraphRAG 的使用（LlamaIndex + Neo4j）",
        note=(
            "飞书：02_GraphRag的使用\n"
            "https://ecnwvcdzorsp.feishu.cn/docx/N1g7d1g9GodJ5wxvjKicYDJrnVc\n"
            "密码：2763X6#3\n"
            "第 16 章是理论+Cypher；本章把文档→抽三元组→Neo4j→自然语言问答打通。\n"
            "本仓库：graph_rag.py；LLM 默认 DeepSeek，Embedding 默认 Chinese-CLIP（DeepSeek 无向量接口）。"
        ),
        children=[
            topic(
                "〇、总览：和上一章怎么接",
                children=[
                    topic("上一章：知识图谱理论、构建流程（NER→关系抽取→入库）、手写 Cypher 操作 Neo4j"),
                    topic("本章：用 LlamaIndex PropertyGraphIndex 自动从非结构化文本抽三元组并问答"),
                    topic("讲义默认千问 DashScope；本仓库可用 DeepSeek 抽取/生成 + 本地 Chinese-CLIP 向量"),
                    topic(
                        "核心工作流",
                        children=[
                            topic("Documents → kg_extractors（LLM 抽三元组）"),
                            topic("实体-关系-实体 + 文本块 → Neo4jPropertyGraphStore（+ 实体节点向量）"),
                            topic("as_query_engine / as_retriever → 实体检索 + 图遍历 → LLM 生成"),
                        ],
                    ),
                ],
            ),
            topic(
                "术语定义（本章必背）",
                children=[
                    topic("PropertyGraphIndex：LlamaIndex 属性图索引，管抽取、落库、问答"),
                    topic("Neo4jPropertyGraphStore：把属性图接到 Neo4j Bolt"),
                    topic("SimpleLLMPathExtractor：开放式抽路径，不限类型，噪声大"),
                    topic("SchemaLLMPathExtractor：限定实体/关系/合法三元组，生产更稳"),
                    topic("embed_kg_nodes：给图谱节点做向量，才能语义召回实体"),
                    topic("from_existing：从已有 Neo4j 加载索引，不再重新扫文档"),
                    topic("LLMSynonymRetriever：用 LLM 把问句关键词扩成同义词去匹配实体"),
                    topic("VectorContextRetriever：用向量语义召回相关实体，再沿图走邻居"),
                ],
            ),
            topic(
                "1、环境准备",
                children=[
                    topic("pip：llama-index-core / llms-dashscope / embeddings-dashscope / graph-stores-neo4j"),
                    topic("本仓库还可能用 llama-index-llms-deepseek + 本地 Chinese-CLIP"),
                    topic("Neo4j 已启动：bolt://localhost:7687，用户名密码配好"),
                    topic("需 APOC 插件（部分图存储操作依赖）"),
                    topic("讲义：DASHSCOPE_API_KEY；本仓库：DEEPSEEK_API_KEY + NEO4J_PASSWORD"),
                ],
            ),
            topic(
                "2、全局配置：LLM + Embedding",
                children=[
                    topic("讲义：Settings.llm = DashScope(qwen-plus)；Settings.embed_model = DashScopeEmbedding(text-embedding-v4)"),
                    topic("抽取对指令遵循要求高，不要用过小的模型"),
                    topic("Embedding 给每个实体节点做向量，用于语义召回"),
                    topic("本仓库注意：不要用全局 Settings 冲掉向量引擎的模型；GraphRagService 用自己的 llm/embed_model"),
                    topic("DeepSeek 无 Embedding API → 图谱向量用 Chinese-CLIP / HuggingFace / 千问"),
                ],
            ),
            topic(
                "3、连接 Neo4j 图存储",
                children=[
                    topic("Neo4jPropertyGraphStore(username, password, url=bolt://localhost:7687)"),
                    topic("Bolt 是 7687，浏览器是 7474，不要填错"),
                    topic("密码必须是首次改密后的密码，空密码连不上"),
                ],
            ),
            topic(
                "4、自动构建知识图谱",
                children=[
                    topic(
                        "方式一 SimpleLLMPathExtractor（开放式）",
                        children=[
                            topic("不限定实体/关系类型，LLM 自由抽路径"),
                            topic("适合探索、demo、schema 未定"),
                            topic("风险：类型乱、关系名不统一、噪声三元组多"),
                            topic("参数例：max_paths_per_chunk、num_workers"),
                        ],
                    ),
                    topic(
                        "方式二 SchemaLLMPathExtractor（生产推荐）",
                        children=[
                            topic("possible_entities：如 PERSON / COMPANY / SCHOOL / LOCATION"),
                            topic("possible_relations：如 CO_FOUNDED / STUDIED_AT / LOCATED_AT"),
                            topic("kg_validation_schema：合法三元组，如 PERSON-CO_FOUNDED-COMPANY"),
                            topic("strict=True：不符合 schema 的丢掉"),
                            topic("max_triplets_per_chunk：每块最多抽几条"),
                        ],
                    ),
                    topic(
                        "from_documents 要点",
                        children=[
                            topic("kg_extractors=[抽取器]"),
                            topic("property_graph_store=graph_store"),
                            topic("embed_kg_nodes=True：节点可语义检索"),
                            topic("show_progress=True"),
                            topic("示例文本：乔布斯/沃兹/苹果/库比蒂诺"),
                        ],
                    ),
                    topic("空库不要 from_existing；先 build 再问答"),
                    topic("前端也可手工写入三元组（不走 LLM 抽取）"),
                ],
            ),
            topic(
                "5、自然语言问答",
                children=[
                    topic("加载：PropertyGraphIndex.from_existing(property_graph_store, embed_kg_nodes=True)"),
                    topic("Embedding 必须与构建时一致，否则向量对不上"),
                    topic(
                        "as_query_engine",
                        children=[
                            topic("include_text=True：答案带来源文本"),
                            topic("similarity_top_k：召回实体/子图条数"),
                            topic("内部：同义词实体匹配 + 向量召回实体 + 图遍历邻居 + LLM 生成"),
                            topic("例：沃兹尼亚克的母校？和谁一起创立苹果？"),
                        ],
                    ),
                    topic(
                        "as_retriever",
                        children=[
                            topic("只拿子图/节点，自己后续处理或与向量通道融合"),
                            topic("本仓库 /ask 双通道：图谱片段标 [图谱] 拼在向量结果前"),
                        ],
                    ),
                    topic("只走图：前端「图谱问答」→ POST /graph/query"),
                ],
            ),
            topic(
                "6、LlamaIndex 方案 vs 手写 Cypher",
                children=[
                    topic("Cypher：精确路径、毫秒级、白盒可解释；要会写 MATCH，问法受 schema 限制"),
                    topic("LlamaIndex GraphRAG：自然语言、自动抽取、开放问法；抽取可能幻觉、速度秒级"),
                    topic("实践：schema 约束抽取 + 必要时手工三元组/Cypher 补洞 + 向量通道补语义"),
                    topic("不要用 GraphRAG 替代所有向量检索：多跳/关系题走图，模糊语义走向量"),
                ],
            ),
            topic(
                "和本仓库的对应",
                children=[
                    topic("graph_rag.py：build_from_texts / files / add_manual_triple / query / retrieve"),
                    topic("路由：/graph/build /triple /load /query /retrieve"),
                    topic("AskPipeline 的 graph_retrieve 模块；预设 graph_hybrid"),
                    topic("Neo4j 未开：向量 RAG 照常用，图谱跳过"),
                ],
            ),
        ],
    )
