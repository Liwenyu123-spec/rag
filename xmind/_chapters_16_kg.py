# -*- coding: utf-8 -*-
"""Chapter 16 知识图谱 — from Feishu 01-知识图谱."""


def make_chapter(topic):
    return topic(
        "16 知识图谱（Neo4j / GraphRAG）",
        note=(
            "飞书：01-知识图谱\n"
            "https://ecnwvcdzorsp.feishu.cn/docx/IYDbddFpSoRqwpxW8fJceOWjnBd\n"
            "密码：24V74&68\n"
            "环境：JDK + Neo4j Community + Python neo4j 驱动；"
            "与向量 RAG 并行的图谱通道。"
        ),
        children=[
            topic(
                "〇、总览",
                children=[
                    topic("一句话：用图（实体-关系-属性）存结构化知识，支持多跳推理；无大模型也可独立使用"),
                    topic("2012 谷歌提出 Knowledge Graph；与大数据、深度学习并称驱动 AI 的核心力量之一"),
                    topic("本仓库落点：先装 Neo4j + JDK，再用 Cypher / Python neo4j 做 GraphRAG 双通道"),
                ],
            ),
            topic(
                "术语定义（本章必背）",
                children=[
                    topic("知识图谱 KG：用图结构表示知识；节点=实体/概念，边=关系/属性"),
                    topic("实体 Entity：具体事物（人、公司、产品）；概念 Concept：抽象类型"),
                    topic("三元组 SPO：Subject-Predicate-Object，数据层基本单元"),
                    topic("模式层 Schema / 本体 Ontology：类型、属性、关系、约束的「骨架」"),
                    topic("数据层 Data Layer：具体实例与事实（「血肉」）"),
                    topic("GraphRAG：用图查询做全局聚合/多跳推理，而非只找相似文本"),
                    topic("实体链接 Entity Linking：把查询里的提及对齐到图谱实体"),
                    topic("Cypher：Neo4j 声明式图查询语言（类比 SQL）"),
                    topic("Neo4j：Java 实现的开源图数据库；社区版免费单点，企业版收费高可用"),
                ],
            ),
            topic(
                "一、知识图谱介绍",
                children=[
                    topic(
                        "1、没有大模型的知识图谱架构",
                        children=[
                            topic("用户查询（自然语言或结构化）"),
                            topic("关键词/规则匹配 → 实体识别"),
                            topic("或直接写 Cypher / SPARQL"),
                            topic("图数据库执行（Neo4j / JanusGraph）→ 精确结果"),
                            topic("模板化回答 / 直接展示图谱路径"),
                            topic("要点：KG 比大模型早很多年，传统上可独立使用"),
                        ],
                    ),
                    topic(
                        "2、大模型增强图谱 vs 传统方案",
                        children=[
                            topic("构建成本：传统高（人工 schema/规则）｜LLM 增强低（自动抽取）"),
                            topic("灵活性：传统低（预定义问法）｜LLM 高（开放域问答）"),
                            topic("准确率：传统极高（结构化查询）｜LLM 中等（有幻觉风险）"),
                            topic("推理深度：传统受图遍历步数限制｜LLM 可增强复杂推理"),
                            topic("维护成本：传统高｜LLM 增强相对低（可动态更新）"),
                            topic("响应速度：传统毫秒级｜LLM 秒级（含模型调用）"),
                            topic("可解释性：传统白盒可追溯路径｜LLM 灰盒"),
                        ],
                    ),
                    topic(
                        "3、介绍与定义",
                        children=[
                            topic(
                                "3.1 什么是知识图谱",
                                children=[
                                    topic(
                                        "3.1.1 什么是知识",
                                        children=[
                                            topic("数据：226.1cm、229cm —— 无语境的客观数值"),
                                            topic("信息：「姚明臂展 226.1cm」「身高 229cm」—— 事实陈述"),
                                            topic("知识：把属性整合抽象，形成对姚明的认知（比普通人高）"),
                                        ],
                                    ),
                                    topic(
                                        "3.1.2 什么是图谱",
                                        children=[
                                            topic("Graph：图论中事物与事物相互连接的结构"),
                                            topic("由节点 Vertex + 边 Edge 构成；多关系图可有多类节点/边"),
                                        ],
                                    ),
                                    topic(
                                        "3.1.3 知识图谱",
                                        children=[
                                            topic("本质：语义网络；节点=概念/实体，边=关系/属性"),
                                            topic("简化说法：实体 + 实体间关系"),
                                            topic("组成三件套：Entity / Relation / Attribute"),
                                        ],
                                    ),
                                    topic(
                                        "3.1.4 示例（苹果/乔布斯）",
                                        children=[
                                            topic("文本：「苹果创始人是乔布斯，1976 成立，总部库比蒂诺」"),
                                            topic("图：乔布斯─创始人→苹果─成立于→1976；苹果─总部→库比蒂诺"),
                                        ],
                                    ),
                                ],
                            ),
                            topic(
                                "3.2 知识图谱检索 vs 向量检索",
                                note="讲义表格多为插图；核心对比见下",
                                children=[
                                    topic("向量：语义相似、模糊召回，弱于精确关系与多跳"),
                                    topic("图谱：精确路径、多跳遍历、全局聚合；弱于开放语义"),
                                    topic("实践：二者互补 → 混合双通道"),
                                ],
                            ),
                            topic(
                                "3.3 在 RAG 中的三种应用模式",
                                children=[
                                    topic(
                                        "模式1 GraphRAG · 全局推理",
                                        children=[
                                            topic("例：公司所有产品的共同技术？"),
                                            topic("传统 RAG：需塞入大量产品文本，易漏、上下文爆炸"),
                                            topic("GraphRAG：公司─produces→产品─uses→技术 X，直接聚合"),
                                            topic("升级：从「找相似文本」→「执行图查询」"),
                                        ],
                                    ),
                                    topic(
                                        "模式2 实体链接增强 · 精准定位",
                                        children=[
                                            topic("例：乔布斯的创业伙伴？"),
                                            topic("向量：可能命中传记任意段落"),
                                            topic("图谱：识别实体→遍历联合创始人→沃兹尼亚克 + 文本"),
                                            topic("优势：消歧 + 精准召回关系型信息"),
                                        ],
                                    ),
                                    topic(
                                        "模式3 混合架构 · 向量+图谱双通道",
                                        children=[
                                            topic("向量通道：语义相似检索"),
                                            topic("图谱通道：实体识别 → 1~2 跳子图 → 对应文本"),
                                            topic("结果融合后再交给 LLM"),
                                        ],
                                    ),
                                ],
                            ),
                            topic(
                                "3.4 知识图谱构建流程",
                                children=[
                                    topic("1 实体抽取 NER：人名/地名/组织/产品（spaCy、BERT-NER、GPT）"),
                                    topic("2 关系抽取：「乔布斯」─创立→「苹果」"),
                                    topic("3 图谱存储：Neo4j / NebulaGraph / RDF 三元组"),
                                    topic("4 与向量库关联：实体/关系链回原文，支持图谱↔文本双向导航"),
                                ],
                            ),
                            topic(
                                "3.5 优势场景",
                                note="讲义多为表格/图；常见于多跳、关系查询、全局聚合",
                                children=[
                                    topic("多跳关系问答、股权穿透、依赖链路"),
                                    topic("需精确实体对齐、可解释路径的场景"),
                                    topic("与向量检索互补，而非替代"),
                                ],
                            ),
                            topic(
                                "3.6 典型应用",
                                children=[
                                    topic("搜索引擎 / 智能助手问答"),
                                    topic("金融：风控、评级、反欺诈"),
                                    topic("医疗：知识库、辅助诊断、药物研发"),
                                    topic("教育：知识点图谱、智能答疑"),
                                    topic("电商推荐 / 社交关系挖掘 / 物联网"),
                                    topic("商业 KG：工商股权投资关系分析"),
                                    topic("教育 KG：教材笔记→知识点组织→问答底座"),
                                ],
                            ),
                            topic(
                                "3.7 挑战",
                                note="讲义插图为主",
                                children=[
                                    topic("构建与维护成本、schema 演进"),
                                    topic("抽取噪声、实体对齐与冲突消解"),
                                    topic("与向量结果的融合策略设计"),
                                ],
                            ),
                            topic(
                                "3.8 与 Advanced / Modular RAG 对比",
                                children=[
                                    topic("已有：Multi-Query→混合检索→RRF→Rerank→LLM"),
                                    topic("升级：并行加「实体识别→图谱查询→子图召回」再融合"),
                                    topic("策略建议：图谱结果优先处理关系/多跳，向量结果补充语义"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            topic(
                "二、分层架构",
                children=[
                    topic("总述：模式层=骨架；数据层=血肉；相互依存"),
                    topic(
                        "1、模式层 Schema Layer",
                        children=[
                            topic("1.1 定义：概念模型与逻辑结构；类比数据库表结构设计"),
                            topic(
                                "1.2 关键组成（本体 Ontology）",
                                children=[
                                    topic("实体类型 Class：人 / 电影 / 公司"),
                                    topic("数据属性 Data Property：连实体→基本类型"),
                                    topic("对象属性 Object Property：连实体→实体（即关系）"),
                                    topic("关系类型 Relation Type：执导 / 就职于 / 位于"),
                                    topic("约束 Constraint：如一人一个出生日期、评分 1–10"),
                                ],
                            ),
                            topic(
                                "1.3 核心作用",
                                children=[
                                    topic("统一表示标准，减少歧义"),
                                    topic("支撑逻辑推理"),
                                    topic("简化查询；指导抽取与融合质量"),
                                ],
                            ),
                            topic(
                                "1.4 常见表示语言",
                                children=[
                                    topic("RDFS：基础模式定义"),
                                    topic("OWL：更强本体与推理"),
                                    topic("SHACL：RDF 数据约束"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "2、数据层 Data Layer",
                        children=[
                            topic("2.1 定义：模式的实例化；大量 SPO 三元组"),
                            topic(
                                "2.2 组成",
                                children=[
                                    topic("实体实例：吴京、《流浪地球2》"),
                                    topic("属性值实例：出生日期=1974-04-03"),
                                    topic("关系实例：吴京参演《流浪地球2》"),
                                ],
                            ),
                            topic("2.3 作用：承载内容、支撑问答/推荐/搜索、可持续扩实例"),
                        ],
                    ),
                    topic(
                        "3、两层关系",
                        children=[
                            topic("模板与实例：数据必须符合模式定义"),
                            topic("抽象与具体：模式是概括，数据是事实"),
                            topic("相互促进：数据积累可反馈扩展模式（如新增「客串」关系）"),
                        ],
                    ),
                ],
            ),
            topic(
                "三、技术架构",
                children=[
                    topic(
                        "1、数据获取",
                        children=[
                            topic("业务库表（结构化，半公开/内部）"),
                            topic("网络公开网页（非结构化）"),
                            topic("三种形态：结构化 / 半结构化 / 非结构化 → 不同处理法"),
                        ],
                    ),
                    topic(
                        "2、信息抽取 IE【核心】",
                        children=[
                            topic("目标：从异构源自动抽候选知识单元"),
                            topic(
                                "实体抽取 Entity Extraction",
                                children=[
                                    topic("NER：人/地/组织/日期/货币等"),
                                    topic("方法：规则、统计、深度学习"),
                                ],
                            ),
                            topic(
                                "关系抽取 Relation Extraction",
                                children=[
                                    topic("作者/工作/亲属等关系"),
                                    topic("方法：有监督统计或深度学习"),
                                ],
                            ),
                            topic(
                                "属性抽取 Attribute Extraction",
                                children=[
                                    topic("实体特征：职业、经纬度等"),
                                    topic("可把「实体-属性值」看作名词性关系 → 常转为关系抽取"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "3、知识融合 Knowledge Fusion",
                        children=[
                            topic("消除冗余、统一表达、解决冲突、知识扩展"),
                            topic("关键技术：指代消解、实体消歧/链接、实体对齐、关系对齐"),
                        ],
                    ),
                    topic(
                        "4、知识加工 Knowledge Processing",
                        children=[
                            topic("本体构建：定义层级与约束（人工或半自动）"),
                            topic("知识推理：规则 / TransE·RotatE 嵌入 / 路径推理 → 知识补全"),
                            topic("质量评估：可信度打分与人工甄别"),
                            topic("结果：零散事实 → 结构化、网络化、可推理的知识体系"),
                        ],
                    ),
                ],
            ),
            topic(
                "四、Neo4j 数据库",
                children=[
                    topic(
                        "1、介绍",
                        children=[
                            topic("Java 实现的开源 NoSQL 图库；2003 研发，2007 首版"),
                            topic("完整数据库特性：ACID、集群、备份与故障转移"),
                            topic("企业版：付费，高可用/热备份；社区版：免费，单点"),
                        ],
                    ),
                    topic(
                        "2、图数据概念",
                        children=[
                            topic("节点 Node：主数据元素；可有多属性、多标签（类比表/表名）"),
                            topic("关系 Relationship：有向；可有属性"),
                            topic("属性 Property：键值对；可索引与约束"),
                            topic("标签 Label：分组节点；建索引加速查找"),
                        ],
                    ),
                    topic(
                        "3、Windows 安装四步（讲义）",
                        children=[
                            topic(
                                "第一步：安装 JDK",
                                children=[
                                    topic("Oracle JDK 或 OpenJDK 17+"),
                                    topic("验证：java --version"),
                                ],
                            ),
                            topic(
                                "第二步：下载 Neo4j Community",
                                children=[
                                    topic("https://neo4j.com/deployment-center/?community"),
                                    topic("解压路径不要含中文"),
                                ],
                            ),
                            topic(
                                "第三步：环境变量",
                                children=[
                                    topic("新建 NEO4J_HOME = 解压目录"),
                                    topic("Path 追加 %NEO4J_HOME%\\bin"),
                                ],
                            ),
                            topic(
                                "第四步：启动",
                                children=[
                                    topic("cmd：neo4j console"),
                                    topic("浏览器：http://localhost:7474/"),
                                    topic("默认用户/密码均为 neo4j，首次登录须改密"),
                                    topic("若报错缺 Java → 先装好 JDK"),
                                ],
                            ),
                        ],
                    ),
                    topic(
                        "4、Cypher 简介",
                        children=[
                            topic("声明式图查询语言；Neo4j 是标准制定者（openCypher）"),
                            topic(
                                "4.1 基本符号",
                                children=[
                                    topic("() 节点；(n) 任意节点"),
                                    topic("(:Label) 如 (p:Person)"),
                                    topic("({key:value}) 如 (p:Person {name:'乔布斯'})"),
                                    topic("--> 有向关系；-[:TYPE]-> 带类型"),
                                    topic("-[:TYPE {prop:val}]-> 带属性关系"),
                                ],
                            ),
                            topic(
                                "4.2 CRUD 要点",
                                children=[
                                    topic("CREATE：创建节点/关系"),
                                    topic("MERGE：不存在才创建（条件创建）"),
                                    topic("MATCH … WHERE：查询与条件过滤"),
                                    topic("例：CREATE (a:Person {name:'张三疯', age:30})"),
                                    topic("例：先 MATCH 两节点再 CREATE 关系"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            topic(
                "五、本机环境清单",
                children=[
                    topic("JDK 17+（JAVA_HOME）"),
                    topic("Neo4j Community（NEO4J_HOME + neo4j console）"),
                    topic("Python：pip install neo4j（官方驱动）"),
                    topic("可选：llama-index 图谱相关包、spaCy NER（后续实验再加）"),
                ],
            ),
        ],
    )
