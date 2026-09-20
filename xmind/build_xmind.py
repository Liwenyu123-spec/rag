# -*- coding: utf-8 -*-
"""Build an XMind file (JSON format, XMind 2020+) plus Markdown/OPML backups."""
import json
import uuid
import zipfile
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent


def nid() -> str:
    return uuid.uuid4().hex[:16]


def topic(title, children=None, note=None):
    node = {"id": nid(), "class": "topic", "title": title}
    if note:
        node["notes"] = {"plain": {"content": note}}
    if children:
        node["children"] = {"attached": children}
    return node


TREE = topic(
    "RAG入门课",
    note=(
        "来源：5篇飞书讲义 + 1个百度网盘配套资料。\n"
        "主线：认识大模型 → 提示词 → RAG认知 → Embedding → 向量库 → 代码实战。\n"
        "建议按 01→09 目录对着讲义敲代码。"
    ),
    children=[
        topic(
            "01 认知阶段：大模型介绍、调用、RAG",
            note="飞书：01-认知阶段（大模型介绍，调用，RAG）",
            children=[
                topic(
                    "一、人工智能介绍",
                    children=[
                        topic(
                            "从人工智能到大模型",
                            children=[
                                topic("AI 最外层：规则系统、搜索、专家系统、机器学习"),
                                topic("ML 第二层：从数据学习，决策树、SVM、浅层网络"),
                                topic("DL 第三层：深层神经网络，CNN、RNN、Transformer"),
                                topic("大模型最内层：数十亿到万亿参数，基于 Transformer"),
                                topic("关系：AI ⊃ ML ⊃ DL ⊃ LLM"),
                            ],
                        ),
                        topic(
                            "人工智能 vs 生成式人工智能",
                            children=[
                                topic(
                                    "AI：让机器模拟智能、学习、推理、行动",
                                    children=[
                                        topic("早期：规则系统 MYCIN、搜索深蓝、知识图谱、符号主义"),
                                        topic("现代主流：机器学习尤其是深度学习"),
                                        topic("阶段：传统ML→深度学习→大模型涌现"),
                                    ],
                                ),
                                topic(
                                    "GAI 生成式AI：按提示生成文本图像音频视频代码",
                                    children=[
                                        topic("文本：ChatGPT、文心一言、DeepSeek"),
                                        topic("图像：Midjourney、Stable Diffusion"),
                                        topic("音频：Suno、语音合成"),
                                        topic("视频：Sora"),
                                        topic("状态：已成熟并广泛应用"),
                                    ],
                                ),
                                topic(
                                    "AGI 通用人工智能：能像人一样完成任意智力任务",
                                    children=[
                                        topic("特征：跨领域迁移、常识推理、元认知"),
                                        topic("状态：尚在理论探索，当前系统远未达到"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "机器学习与深度学习",
                            children=[
                                topic(
                                    "ML",
                                    children=[
                                        topic("监督学习：有标签数据"),
                                        topic("无监督学习：找隐藏结构"),
                                        topic("强化学习：奖励惩罚学策略"),
                                        topic("案例：垃圾邮件过滤、推荐系统"),
                                    ],
                                ),
                                topic(
                                    "DL",
                                    children=[
                                        topic("ANN 人工神经网络"),
                                        topic("CNN 图像视觉"),
                                        topic("RNN 序列文本"),
                                        topic("Transformer 是 GPT、DeepSeek 等主流架构"),
                                        topic("神经网络只是拟人概念，不是真的模拟大脑"),
                                    ],
                                ),
                                topic("NLP：词嵌入、Transformer、情感分析、翻译、语音助手"),
                                topic("CV：分类检测、特征提取、安防相册自动驾驶"),
                            ],
                        ),
                        topic(
                            "大模型 vs 大语言模型",
                            children=[
                                topic("LLM：海量文本预训练，理解并生成语言"),
                                topic("LM 大模型：参数大、数据大、通用强、有涌现"),
                                topic("所有 LLM 都是大模型，但大模型不只有语言"),
                                topic("已走向多模态：文本、视觉、语音"),
                            ],
                        ),
                        topic(
                            "爆炸式发展",
                            children=[
                                topic("2021 基础模型 Foundational Models"),
                                topic("2022.11 ChatGPT 引爆对话应用"),
                                topic("随后百模大战"),
                                topic("2025 DeepSeek"),
                                topic("常把 2023 称为 AI 元年"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "二、大模型介绍与调用",
                    children=[
                        topic(
                            "四个“大”",
                            children=[
                                topic("参数量大：记忆单元，单位 B=10亿"),
                                topic("训练数据大：互联网多源多模态"),
                                topic("算力消耗大：GPU/TPU 集群，训练数周到数月"),
                                topic("应用效果大：NLP、视觉、语音都有突破"),
                            ],
                        ),
                        topic(
                            "Token",
                            children=[
                                topic("模型读写的最小信息块，不一定是字或词"),
                                topic("DeepSeek 约：1英文字符≈0.3 token，1汉字≈0.6 token"),
                                topic("经验：1000 token ≈ 750 英文词 或 400-500 汉字"),
                                topic("重要性：计费单位、上下文上限、超出就遗忘"),
                            ],
                        ),
                        topic(
                            "国际阵营",
                            children=[
                                topic("OpenAI GPT 系列：综合强，擅长工具和 Agent"),
                                topic("o 系列：推理数学分析强，成本高"),
                                topic("Anthropic Claude：编程、长上下文、安全场景"),
                                topic("Google Gemini：原生多模态、性价比"),
                                topic("xAI Grok：与 X 平台集成"),
                            ],
                        ),
                        topic(
                            "国产阵营",
                            children=[
                                topic("DeepSeek：开源、推理强、训练成本低"),
                                topic("Kimi：长文本、法律条文"),
                                topic("智谱 GLM：中英双语、Agent、国产硬件"),
                                topic("通义千问 Qwen：开源生态、中文场景"),
                                topic("豆包：语音与实时交互、MoE"),
                                topic("文心一言、商汤、MiniMax 等"),
                            ],
                        ),
                        topic(
                            "怎么调用",
                            children=[
                                topic(
                                    "OpenAI 官方",
                                    children=[
                                        topic("developers.openai.com 创建 API Key"),
                                        topic("需充值，常要境外卡"),
                                        topic("也可走国内中转或直接用国产模型"),
                                    ],
                                ),
                                topic(
                                    "阿里百炼 推荐入门",
                                    children=[
                                        topic("国内直连、新人免费额度、模型全、生态完善"),
                                        topic("兼容 OpenAI 接口"),
                                        topic("Endpoint: dashscope compatible-mode v1"),
                                        topic("模型：qwen-turbo/plus/max、deepseek-r1"),
                                        topic("Key 放环境变量 DASHSCOPE_API_KEY"),
                                    ],
                                ),
                                topic(
                                    "OpenAI 库三步",
                                    children=[
                                        topic("1 创建客户端：base_url + api_key"),
                                        topic("2 调 chat：model + messages"),
                                        topic("3 取结果"),
                                        topic("messages：system / user / assistant / tool"),
                                        topic("stream=true 流式输出，防超时、体验更好"),
                                        topic("带上历史 messages 才能多轮不跑偏"),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                topic(
                    "三、部署方式",
                    children=[
                        topic(
                            "云端 API",
                            children=[
                                topic("优点：不养硬件、顶级模型、厂商保障"),
                                topic("缺点：数据出网、按量计费、网络延迟"),
                            ],
                        ),
                        topic(
                            "云上自托管",
                            children=[
                                topic("引擎：vLLM、TGI、llama.cpp、Ollama"),
                                topic("对外：Nginx、FastAPI、gRPC"),
                                topic("优点：可控、可监控、可私有化"),
                                topic("缺点：要自己运维显存扩容，需要 MLOps"),
                            ],
                        ),
                        topic(
                            "本地与边缘",
                            children=[
                                topic("工具：Ollama、LM Studio、MLX、llama.cpp、vLLM"),
                                topic("常用 7B/14B + 量化"),
                                topic("优点：隐私、无 API 费、可离线"),
                                topic("挑战：硬件和模型管理"),
                            ],
                        ),
                        topic(
                            "Ollama",
                            children=[
                                topic("定位：本地大模型运行容器，不训练只推理"),
                                topic("一条命令拉模型、一条命令对话"),
                                topic("改模型保存路径，别塞满 C 盘"),
                                topic("内存：7B约8G，13B约16G，33B约32G；盘预留50G"),
                                topic("默认只监听 127.0.0.1:11434"),
                                topic("局域网：OLLAMA_HOST=0.0.0.0，OLLAMA_ORIGINS=*"),
                                topic("Python 调本地 HTTP，可接 FastAPI 流式"),
                                topic("课上要求：知道即可，后面用 vLLM"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "四、大模型应用与 LlamaIndex",
                    children=[
                        topic(
                            "四种应用",
                            children=[
                                topic("Prompt 工程：会说话，格式和逻辑才稳"),
                                topic("对话系统：加 Memory，记住多轮上下文"),
                                topic("RAG：外挂知识库，先检索再生成，压幻觉"),
                                topic("Agent：规划 + 调工具 API，当手脚用"),
                            ],
                        ),
                        topic(
                            "构建难点",
                            children=[
                                topic("私有数据怎么接上 LLM"),
                                topic("长对话上下文怎么管"),
                                topic("怎么调外部 API 和数据库"),
                                topic("多步推理与任务分解"),
                                topic("可观察性：怎么调试优化"),
                            ],
                        ),
                        topic(
                            "LlamaIndex 六模块",
                            children=[
                                topic("Data Connectors 数据加载"),
                                topic("Index 索引"),
                                topic("Retriever 检索"),
                                topic("Query Engine 查询引擎"),
                                topic("Agents 智能体"),
                                topic("Workflows 工作流"),
                            ],
                        ),
                        topic(
                            "框架调用模型",
                            children=[
                                topic("DeepSeek / 千问 DashScope / Ollama 都要单独装包"),
                                topic("complete 单轮补全；chat 多轮对话，实际多用 chat"),
                            ],
                        ),
                        topic(
                            "RAG 在 LlamaIndex 里",
                            children=[
                                topic("建库：Reader 加载 → Splitter 切块 → Embedding → Chroma 存储"),
                                topic("检索：加载向量库 → 设回答模型 → Query Engine"),
                                topic("切分与向量化在建索引时真正执行，前面只是配置"),
                                topic("本地嵌入：nomic-embed-text 或 qwen3-embedding"),
                                topic("云端嵌入：DashScope 千问"),
                                topic("可加记忆做成知识型 Chatbot"),
                            ],
                        ),
                        topic(
                            "作业",
                            children=[
                                topic("FastAPI 提供接口"),
                                topic("页面上传文档，向量化入库"),
                                topic("简易对话窗口聊天"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        topic(
            "02 提示词工程",
            note="飞书：01-提示词",
            children=[
                topic(
                    "概述",
                    children=[
                        topic("Prompt：给 AI 的指令"),
                        topic("Prompt Engineering：设计、测试、优化指令的方法"),
                        topic("差例子：写一篇关于AI的文章"),
                        topic("好例子：角色+字数+读者+案例+工具+语气"),
                    ],
                ),
                topic(
                    "优质 Prompt 四要素",
                    children=[
                        topic("角色 Role：身份和专业领域"),
                        topic("任务 Task：要做什么、输出什么"),
                        topic("上下文 Context：受众、平台、背景"),
                        topic("约束 Constraints：格式、长度、禁忌、风格"),
                    ],
                ),
                topic(
                    "CLEAR 原则",
                    children=[
                        topic("Context 上下文"),
                        topic("Length 长度"),
                        topic("Examples 示例"),
                        topic("Audience 受众"),
                        topic("Role 角色"),
                    ],
                ),
                topic(
                    "基础技巧",
                    children=[
                        topic("明确：生成3条健康饮食微博，而不是写一些饮食"),
                        topic("结构化：分点分段"),
                        topic("示例引导：给输入输出样例"),
                    ],
                ),
                topic(
                    "调优实战技法",
                    children=[
                        topic("环境：pip install openai dashscope，配置 DASHSCOPE_API_KEY"),
                        topic("零样本 Zero-Shot：直接下指令，适合简单任务"),
                        topic("少样本 Few-Shot：给几个输入输出样例，锁格式风格"),
                        topic("思维链 COT：先一步步思考，适合复杂推理"),
                        topic("自我一致性：多生成几个再投票或自选最优"),
                        topic("思维树 ToT：多分支发散→评估剪枝→再执行"),
                    ],
                ),
                topic(
                    "攻击防范 了解即可",
                    children=[
                        topic("提示注入：输入里塞指令覆盖系统设定"),
                        topic("越狱 Jailbreak：绕过安全限制"),
                        topic("数据泄露：套取训练或系统敏感信息"),
                        topic("防御：输入净化、多层审核、沙箱限权、数据脱敏"),
                        topic("课上代码：content_sanitize.py、content_moderation.py"),
                    ],
                ),
                topic(
                    "案例",
                    children=[
                        topic(
                            "电商产品描述 ecprompt.py",
                            children=[
                                topic("角色：电商金牌文案专家"),
                                topic("少样本：输入-思考-输出范例"),
                                topic("COT：先分析痛点再转卖点"),
                                topic("temperature=0.7 平衡创意与稳定"),
                            ],
                        ),
                        topic(
                            "社交媒体内容策划",
                            children=[
                                topic("ToT：3个切入角度"),
                                topic("评估爆款潜力后选最佳"),
                                topic("输出一周5个选题 Markdown 表"),
                                topic("加自我反思一步"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "最佳实践",
                    children=[
                        topic("原则：明确、完整、一致、安全"),
                        topic("策略：先简单再复杂、迭代、量化评估、记有效模板"),
                        topic("趋势：自动生成提示、多模态、实时反馈、个性化"),
                    ],
                ),
            ],
        ),
        topic(
            "03 RAG整体认知",
            note="飞书：01-RAG整体认知",
            children=[
                topic(
                    "是什么",
                    children=[
                        topic("Retrieval-Augmented Generation 检索增强生成"),
                        topic("生成前先从外部知识库检索相关文档，再当上下文"),
                        topic("本质：检索器 Retriever + 生成器 Generator"),
                        topic("比喻：开卷考试，先翻书再答题"),
                        topic("不是替代大模型，是给它装实时可信可控的记忆外挂"),
                    ],
                ),
                topic(
                    "核心流程",
                    children=[
                        topic("Query：用户问题，可能口语、指代不明"),
                        topic("Embedding：同一套向量模型把问题变成高维坐标"),
                        topic("Retrieval：余弦相似度召回 Top-K，这一步决定原材料质量"),
                        topic("Context：拼接片段+约束提示，必要时裁剪适配窗口"),
                        topic("LLM：当摘要者和解释者，不是当记忆库"),
                        topic("Answer：返回答案，最好带来源便于核查"),
                    ],
                ),
                topic(
                    "三大痛点",
                    children=[
                        topic("幻觉：没知识就编。RAG 要求只基于检索内容，没有就说不知道"),
                        topic("时效差：训练有截止日期。RAG 更新知识库即可，不必重训"),
                        topic("私有数据：云端模型难接内网。RAG 可本地 LLM+嵌入+向量库"),
                        topic("误区：RAG 不能 100% 消幻觉，取决于检索精度和 Prompt 约束"),
                    ],
                ),
                topic(
                    "落地场景",
                    children=[
                        topic("本地私有问答：笔记、公司手册，不联网"),
                        topic("PDF 问答：论文教材说明书，先定位再生成"),
                        topic("智能客服：FAQ 售后流程，FastAPI 封接口"),
                        topic("多知识库：PDF+Word+网页一次提问全检索"),
                    ],
                ),
                topic(
                    "经典五步",
                    children=[
                        topic("1 文档加载：PDF/Word/TXT/网页变成文本"),
                        topic("2 文本分割：chunk_size 与 chunk_overlap，适配窗口、提高检索精度"),
                        topic("3 向量化 Embedding：文本变语义向量，常用 BGE/M3E"),
                        topic("4 向量存储：FAISS/Chroma，毫秒级相似检索"),
                        topic("5 检索+生成：问题向量化→召回→拼 Prompt→LLM 回答"),
                    ],
                ),
                topic(
                    "数据流三块",
                    children=[
                        topic("数据准备：解析、清洗页眉广告、切块重叠、提元数据"),
                        topic("检索系统：向量检索 + BM25 稀疏 + 混合检索"),
                        topic("生成系统：结构化注入检索结果、禁止编造、后处理加引用"),
                    ],
                ),
                topic(
                    "五大范式 学霸养成记",
                    children=[
                        topic("Naive RAG：小学生翻书。线性流程，原型快，检索粗、易幻觉"),
                        topic("Advanced RAG：初中生找得更准。查询改写、重排序，工业主流"),
                        topic("Modular RAG：高中生灵活用工具。模块路由调度，LangChain/LlamaIndex"),
                        topic("Graph RAG：大学生理解关系。实体关系多跳推理，微软 GraphRAG"),
                        topic("Agentic RAG：研究生自己规划。拆任务、调工具、不足再检索"),
                    ],
                ),
                topic(
                    "RAG vs 微调",
                    children=[
                        topic("知识常更新、要引用、要私有化 → RAG"),
                        topic("知识固定、要低延迟、要改风格口吻 → 微调更合适"),
                        topic("可结合：微调让模型更会用检索资料，RAG 注入新知识"),
                        topic("思考：校园通知每月更新，该用 RAG"),
                    ],
                ),
                topic(
                    "局限",
                    children=[
                        topic("检索质量决定上限，没召回到生成再强也没用"),
                        topic("上下文窗口：多处证据可能被截断"),
                        topic("检索噪声会误导模型"),
                        topic("多了检索环节，延迟变长，需缓存或异步"),
                        topic("中文和术语对 Embedding 与切分策略很敏感"),
                    ],
                ),
            ],
        ),
        topic(
            "04 Embedding 向量表示",
            note="飞书：02-大模型应用基础--Embeddings",
            children=[
                topic(
                    "向量是什么",
                    children=[
                        topic("有大小和方向的量，如二维 (x,y)"),
                        topic("Embedding：用数值向量表示一个对象"),
                    ],
                ),
                topic(
                    "余弦相似度",
                    children=[
                        topic("比的是方向像不像，范围约 -1 到 1，越近 1 越像"),
                        topic("点积：对应维度相乘再相加，共同高频词越多越大"),
                        topic("模长：句子有多长多丰富"),
                        topic("公式：点积 / (A模长 × B模长)"),
                        topic("词频例子：分词→词表→词频向量→算余弦"),
                        topic("一句话：共同词又多又频，除以各自有多长"),
                    ],
                ),
                topic(
                    "好的语义向量",
                    children=[
                        topic("语义关系被编码成空间中的方向，且跨词通用"),
                        topic("性别轴：king - man + woman ≈ queen"),
                        topic("时态轴：walked - walking ≈ swam - swimming"),
                        topic("词向量把语义变成算术"),
                    ],
                ),
                topic(
                    "LLM 里怎么用",
                    children=[
                        topic("把词变成上下文感知的高维向量，再用余弦衡量亲疏"),
                        topic("距离越小含义越近，是搜索聚类情感分析的基础"),
                    ],
                ),
                topic(
                    "三大作用",
                    children=[
                        topic("输入端语义编码：token→向量，注意力才能算"),
                        topic("RAG 语义检索：问题向量对文档向量，相似度匹配、去重聚类"),
                        topic("跨模态：图文可进同一空间，图文检索、零样本分类"),
                    ],
                ),
                topic(
                    "Word2Vec 了解",
                    children=[
                        topic("CBOW：用上下文猜中心词，众人推举一个代表"),
                        topic("Skip-gram：用中心词猜上下文，一个代表辐射众人"),
                        topic("结构：三层网络，One-hot / Multi-hot，隐藏层 N"),
                        topic("词向量就在隐藏层权重矩阵里，相当于查找表"),
                    ],
                ),
            ],
        ),
        topic(
            "05 向量数据库",
            note="飞书：03-大模型应用基础--向量数据库",
            children=[
                topic(
                    "第一部分 向量检索基础",
                    children=[
                        topic("传统关键词搜：不懂笔记本≈电脑，跨语言差，缺语境"),
                        topic("向量搜：文本图像变成高维向量，在空间里比远近"),
                        topic("为何专用库：近似搜索换速度，HNSW/IVF 专用索引，可 GPU 批量"),
                        topic("指标：延迟、召回精度、内存、索引磁盘占用"),
                    ],
                ),
                topic(
                    "第二部分 FAISS",
                    children=[
                        topic("Facebook 开源相似性搜索库，C++ 内核 + Python 接口"),
                        topic("可上十亿级向量，被 Milvus、Qdrant 等采用"),
                        topic(
                            "IndexFlat 精确搜",
                            children=[
                                topic("FlatL2 欧氏距离、FlatIP 内积、余弦=IP+向量归一化"),
                                topic("适合小于约10万、要极准、当精度基准"),
                            ],
                        ),
                        topic(
                            "IndexIVFFlat 倒排",
                            children=[
                                topic("先聚类成 Voronoi 区，查询只搜最近几个簇"),
                                topic("nlist 聚类中心数，常取 sqrt(N)"),
                                topic("nprobe 查几个簇：1最快最糙，等于 nlist 就变精确搜"),
                            ],
                        ),
                        topic(
                            "IndexHNSWFlat 图索引",
                            children=[
                                topic("分层可导航小世界，灵感来自六度分隔和高速公路"),
                                topic("上层快速跳、下层精细搜"),
                                topic("多数系统默认推荐，精度和速度较均衡"),
                            ],
                        ),
                        topic("选型：HNSW 通用；IVF 更适合超大规模且资源紧"),
                    ],
                ),
                topic(
                    "常见向量库对照",
                    children=[
                        topic("Milvus：分布式，海量，HNSW/IVF/FLAT"),
                        topic("Pinecone：全托管，内部偏 HNSW"),
                        topic("Weaviate：HNSW，关键词+语义混合"),
                        topic("Qdrant：Rust，过滤和地理查询"),
                        topic("Chroma：轻量，LLM 应用友好，可嵌入式"),
                        topic("Faiss：库不是完整数据库，研究与大规模实验"),
                        topic("ES 向量插件、Deep Lake、Vearch 等"),
                    ],
                ),
                topic(
                    "第三部分 Chroma",
                    children=[
                        topic("AI 原生向量库，4 个核心 API，对接 LangChain/LlamaIndex"),
                        topic(
                            "add 参数",
                            children=[
                                topic("ids 必填，唯一，重复默认跳过"),
                                topic("documents 原文，可自动嵌入"),
                                topic("metadatas 附加信息，供 where 过滤"),
                                topic("embeddings 也可直接塞预计算向量"),
                            ],
                        ),
                        topic(
                            "query 参数",
                            children=[
                                topic("query_texts 或 query_embeddings 二选一"),
                                topic("n_results 返回条数，默认 10"),
                                topic("where 按元数据过滤"),
                                topic("where_document 按原文包含过滤"),
                                topic("include 控制返回 documents/metadatas/embeddings/distances"),
                            ],
                        ),
                        topic("距离函数创建集合时指定，之后不能改：L2 / IP / cosine"),
                        topic("可换嵌入：OpenAI 或千问 DashScope"),
                        topic("可当 HTTP 服务跑，像启动 MySQL 再远程连"),
                        topic("支持 update / delete"),
                    ],
                ),
                topic(
                    "第四部分 实战",
                    children=[
                        topic("目标：自然语言查询，返回最相关文档"),
                        topic("技术栈：Chroma + 千问嵌入 + FastAPI"),
                        topic("阶段1：分块→get_embedding→和原文一起放进索引"),
                        topic("阶段2：问题向量化→索引得下标→从 documents 取回原文"),
                        topic("文档：faiss.ai 、 docs.trychroma.com"),
                    ],
                ),
            ],
        ),
        topic(
            "06 配套资料 百度网盘",
            note="https://pan.baidu.com/s/1YA63Bo8A_saNsCGlF4nccQ  提取码 mcq7\n文件夹：918-向量数据库",
            children=[
                topic(
                    "code / rag_pros0908 对着讲义敲",
                    children=[
                        topic("01_模型调用"),
                        topic("02_Ollama"),
                        topic("03_聊天机器人"),
                        topic("04_LlamaIndex框架"),
                        topic("05_提示词工程"),
                        topic("06_提示词综合案例"),
                        topic("07_聊天机器人安全校验"),
                        topic("08_向量"),
                        topic("09_向量数据库"),
                    ],
                ),
                topic("video：5 个视频，对应向量库那一课"),
                topic("另有 笔记 文件；.env 是密钥配置，不要提交公开仓库"),
            ],
        ),
        topic(
            "学习路径 从左到右",
            children=[
                topic("1 认知：搞懂 AI/LLM、百炼调用、Ollama、四种应用"),
                topic("2 提示词：四要素 + COT/Few-Shot，先跑电商和社媒案例"),
                topic("3 RAG认知：背下五步流程和检索决定上限"),
                topic("4 Embedding：会算余弦，知道向量是语义坐标"),
                topic("5 向量库：Flat/IVF/HNSW 选型，Chroma 增查改删"),
                topic("6 用网盘 01→09 把知识库问答作业做出来"),
            ],
        ),
    ],
)


def to_md(node, level=1) -> str:
    lines = [f"{'#' * min(level, 6)} {node['title']}"]
    note = node.get("notes", {}).get("plain", {}).get("content")
    if note:
        for nline in note.split("\n"):
            lines.append(nline)
    for child in node.get("children", {}).get("attached", []):
        lines.append("")
        lines.append(to_md(child, level + 1))
    return "\n".join(lines)


def to_opml_outline(node) -> str:
    title = (
        node["title"]
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    kids = node.get("children", {}).get("attached", [])
    if not kids:
        return f'    <outline text="{title}"/>'
    inner = "\n".join(to_opml_outline(c) for c in kids)
    return f'    <outline text="{title}">\n{inner}\n    </outline>'


def main():
    TREE["structureClass"] = "org.xmind.ui.logic.right"
    content = [
        {
            "id": nid(),
            "class": "sheet",
            "title": "RAG入门课",
            "rootTopic": TREE,
            "topicPositioning": "fixed",
        }
    ]
    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {},
        }
    }
    metadata = {
        "dataVersion": "2.0",
        "creator": {"name": "Cursor", "version": "1.0"},
    }

    xmind_path = OUT_DIR / "RAG入门课-从左到右.xmind"
    with zipfile.ZipFile(xmind_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))

    md_path = OUT_DIR / "RAG入门课-XMind导入.md"
    md_path.write_text(to_md(TREE), encoding="utf-8")

    opml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<opml version="2.0">\n'
        "  <head><title>RAG入门课</title></head>\n"
        "  <body>\n"
        f"{to_opml_outline(TREE)}\n"
        "  </body>\n"
        "</opml>\n"
    )
    opml_path = OUT_DIR / "RAG入门课-XMind导入.opml"
    opml_path.write_text(opml, encoding="utf-8")

    print(xmind_path)
    print(md_path)
    print(opml_path)


if __name__ == "__main__":
    main()
