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
    note="根据6篇飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、Native RAG（基础RAG）。",
    children=[
        topic(
            "01 认知阶段：大模型介绍、调用、RAG",
            note="飞书文档：01-认知阶段（大模型介绍，调用，RAG）",
            children=[
                topic(
                    "一、人工智能介绍",
                    children=[
                        topic(
                            "1 从人工智能到大模型",
                            children=[
                                topic("关系式：AI ⊃ 机器学习ML ⊃ 深度学习DL ⊃ 大模型LLM"),
                                topic(
                                    "四层含义",
                                    children=[
                                        topic("最外层 AI：最广，让机器模拟人类智能，含规则系统、搜索、专家系统、机器学习"),
                                        topic("第二层 ML：从数据自动学习规律，含决策树、SVM、随机森林、浅层神经网络"),
                                        topic("第三层 DL：深层神经网络自动提特征，含 CNN、RNN、Transformer"),
                                        topic("最内层 大模型：数十亿至数万亿参数，基于 Transformer，如 GPT、Kimi、文心一言"),
                                    ],
                                ),
                                topic("说明：大模型本质是深度学习的一种实现，因规模涌现和技术生态常被单独强调"),
                            ],
                        ),
                        topic(
                            "2 人工智能和生成式人工智能",
                            note="AI 和 GAI 都是提出目标，GAI 的目标更具体",
                            children=[
                                topic(
                                    "2.1 人工智能 AI",
                                    note="跨计算机、数据、统计、工程、语言学、神经科学、哲学、心理学，研究能学习、推理、行动的机器",
                                    children=[
                                        topic(
                                            "历史上长期依赖非机器学习",
                                            children=[
                                                topic("规则系统：IF-THEN 硬编码，如专家系统 MYCIN"),
                                                topic("搜索算法：1997 深蓝击败卡斯帕罗夫，暴力搜索+符号主义"),
                                                topic("知识图谱：结构化知识推理，如 Google Knowledge Graph"),
                                                topic("符号主义 AI：逻辑推理、知识表示"),
                                            ],
                                        ),
                                        topic(
                                            "机器学习是主流实现方式",
                                            children=[
                                                topic("2010年前传统ML：数据少，特征靠人工设计"),
                                                topic("2010-2020 深度学习：自动特征提取，大数据驱动"),
                                                topic("2020至今大模型：通用预训练，出现涌现能力"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "2.1.3 生成式人工智能 GAI",
                                    children=[
                                        topic("定义：按用户提示，学习海量数据模式，生成以前不存在的文本、图像、音频、视频、代码"),
                                        topic("文本生成：ChatGPT、文心一言、DeepSeek"),
                                        topic("图像生成：Midjourney、Stable Diffusion"),
                                        topic("音频生成：Suno AI、语音合成"),
                                        topic("视频生成：Sora"),
                                        topic("当前状态：已成熟并广泛应用"),
                                    ],
                                ),
                                topic(
                                    "2.1.4 通用人工智能 AGI",
                                    children=[
                                        topic("定义：假设中能像人一样理解和学习任何智力任务，不限特定领域"),
                                        topic("跨领域迁移：学会下棋后把策略用到经济问题上"),
                                        topic("常识推理：理解杯子推下桌子会摔碎"),
                                        topic("元认知：知道自己不知道，再去学"),
                                        topic("当前状态：理论探索阶段，现有系统远未达到，是长期目标"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2.2 机器学习和深度学习",
                            note="都是手段，深度学习是更强的手段",
                            children=[
                                topic(
                                    "机器学习 ML",
                                    children=[
                                        topic("核心理念：无需显式编程即可从数据学习"),
                                        topic("监督学习：用已标注数据训练，如标了猫的照片"),
                                        topic("无监督学习：无标签中找结构，如客户分群"),
                                        topic("强化学习：与环境互动，靠奖励惩罚学策略，如游戏AI"),
                                        topic("案例：垃圾邮件过滤、Netflix推荐、股市预测"),
                                    ],
                                ),
                                topic(
                                    "深度学习 DL",
                                    children=[
                                        topic("模仿神经元分层：输入层、多个隐藏层、输出层"),
                                        topic("ANN：算法支柱，模拟信号传递"),
                                        topic("CNN：图像和视觉"),
                                        topic("RNN：序列，如时间序列、文本"),
                                        topic("案例：人脸解锁、医疗影像、自动驾驶"),
                                        topic("神经网络：拟人概念，分层是不同维度的信息处理，并非真模拟大脑"),
                                        topic("Transformer：ChatGPT、DeepSeek 等主流模型的架构"),
                                    ],
                                ),
                                topic(
                                    "NLP 自然语言处理",
                                    children=[
                                        topic("让机器理解、解释、生成人类语言，处理语气情感语境"),
                                        topic("词嵌入：词变成向量，表示语义远近"),
                                        topic("Transformer：可大规模并行训练，是大模型核心"),
                                        topic("情感分析：从社交文本判断情绪"),
                                        topic("案例：ChatGPT、Google翻译、Siri Alexa 小艺"),
                                    ],
                                ),
                                topic(
                                    "CV 计算机视觉",
                                    children=[
                                        topic("让计算机看懂视觉世界：识别、定位、描述"),
                                        topic("图像分类与目标检测：是什么、在哪里"),
                                        topic("特征提取：边缘、轮廓等关键模式"),
                                        topic("案例：安防行人检测、相册人脸分类、自动驾驶道路识别"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2.3 大模型和大语言模型",
                            children=[
                                topic(
                                    "LLM 大语言模型",
                                    children=[
                                        topic("用大量文本训练的深度学习模型，能生成或理解自然语言"),
                                        topic("核心：大规模无监督训练，学习语言模式和结构"),
                                        topic("能力：拼写语法、摘要、翻译、情感分析、对话、推荐"),
                                        topic("预训练后具备通用建模和泛化能力"),
                                    ],
                                ),
                                topic(
                                    "LM 大模型",
                                    children=[
                                        topic("参数规模：通常数十亿到数千亿"),
                                        topic("训练数据：互联网文本、书籍、代码等"),
                                        topic("通用能力：理解、推理、生成、分类"),
                                        topic("涌现能力：规模到一定程度后出现意想不到的能力"),
                                    ],
                                ),
                                topic(
                                    "对比表：大模型 vs 大语言模型",
                                    children=[
                                        topic("范围：大模型更广、涵盖所有模态；LLM 更窄、专指文本语言"),
                                        topic("输入输出：大模型可文本图像音频视频代码；LLM 主要处理文本"),
                                        topic("关系：大模型是母集，LLM 是子集"),
                                        topic("一句话：所有 LLM 都是大模型，但并非所有大模型都是 LLM"),
                                    ],
                                ),
                                topic(
                                    "大模型不止语言 多模态家族",
                                    children=[
                                        topic("大语言模型：GPT-4、Kimi、Claude → 文本理解与生成"),
                                        topic("视觉大模型：SAM、CLIP、Stable Diffusion → 图像理解、分割、生成"),
                                        topic("多模态大模型：GPT-4o、Gemini、Kimi-VL → 同时处理图文音视频"),
                                        topic("科学大模型：AlphaFold、GraphCast → 蛋白质结构、天气预报"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2.4 大模型的爆炸式发展",
                            children=[
                                topic("有人把大模型发明类比为人类学会用火"),
                                topic("2021 斯坦福提出 Foundational Models 基础模型"),
                                topic("2022.11 OpenAI 发布 ChatGPT，对话交互，能写论文邮件脚本代码翻译"),
                                topic("随后百模大战，成为技术和公众热点"),
                                topic("2025 DeepSeek"),
                                topic("常把 2023 称为 AI 元年：问答、辅助编程、看图、创作进步极快"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "二、大模型介绍及其常用大模型",
                    children=[
                        topic(
                            "1.1 基本概念",
                            children=[
                                topic("超大参数神经网络，通常基于 Transformer"),
                                topic("在海量文本上自监督训练，通过预测下一个 token 学习语言和知识"),
                                topic(
                                    "什么是 token",
                                    children=[
                                        topic("模型处理文本的最小信息块，不完全等于字或词"),
                                        topic("可以是完整英文单词、一个汉字、单词片段、标点或空格"),
                                        topic("如 unbelievable 可能拆成 un + believ + able"),
                                        topic("各模型分词方式不同"),
                                        topic("DeepSeek 约：1个英文字符≈0.3 token；1个中文字符≈0.6 token"),
                                        topic("讲义对照表：英文 1 token≈0.75 个单词，Hello world≈2 tokens"),
                                        topic("讲义对照表：中文 1 token≈1 个汉字，你好世界≈4 tokens"),
                                        topic("经验另说：1000 token ≈ 750 英文词，或 400-500 汉字"),
                                        topic("不同模型切法不一样，以上比例不要混用"),
                                        topic("可视化：gpt-tokenizer.dev 可看 GPT 如何切 token"),
                                    ],
                                ),
                                topic(
                                    "为什么 token 重要",
                                    children=[
                                        topic("计费单位：输入+输出都按 token 收费"),
                                        topic("上下文限制：一次能处理的 token 有上限"),
                                        topic("超出窗口会遗忘之前内容"),
                                        topic("例子：15万汉字约20万 token，早期 4K 窗口读不完，百万级窗口可以"),
                                    ],
                                ),
                                topic("类比：token 像乐高积木，先拆开理解，再拼成回复"),
                            ],
                        ),
                        topic(
                            "四个“大”",
                            children=[
                                topic(
                                    "参数量“大”",
                                    children=[
                                        topic("从百万、千万到数亿、数百亿甚至万亿，单位 B=10亿"),
                                        topic("参数即记忆单元，是存储和表达知识的载体"),
                                        topic("参数越多，能拟合的模式越复杂，语义关系和知识更精细"),
                                        topic(
                                            "规模分级 讲义表",
                                            children=[
                                                topic("小型 <1B：Phi-3 Mini 3.8B、TinyLlama 1.1B"),
                                                topic("中型 1B-10B：Gemma 2 9B、Qwen2.5 7B"),
                                                topic("大型 10B-100B：Llama 3 70B、GPT-3 175B"),
                                                topic("超大规模 >100B：GPT-4 约1.76T、Llama 3 405B、DeepSeek V3 671B"),
                                            ],
                                        ),
                                        topic(
                                            "学生做题比喻",
                                            children=[
                                                topic("参数 = 学生大脑里的解题套路"),
                                                topic("小模型几百万：小学生，只会加减乘除，应用题读不懂"),
                                                topic("中模型几亿：初中生，会解方程，复杂几何经常错"),
                                                topic("大模型几百亿：高中生/大学生，微积分、物理建模都能做"),
                                                topic("超大模型千亿：教授，能发论文、跨学科创新"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "训练数据量“大”",
                                    children=[
                                        topic("支撑庞大参数需要海量数据"),
                                        topic("来源广：互联网爬取，文本图像音频视频多模态"),
                                        topic("覆盖面广才有通用性，像人博览群书"),
                                    ],
                                ),
                                topic(
                                    "计算资源消耗“大”",
                                    children=[
                                        topic("GPU：图形处理器，数千 CUDA 核心，通用并行，图形、科学计算、AI"),
                                        topic("TPU：张量处理单元，脉动阵列，专为稠密矩阵乘优化，适合 Transformer"),
                                        topic("训练周期：数周到数月，取决于规模和硬件"),
                                        topic("电力和硬件成本高，微调和推理部署对工程能力要求也高"),
                                    ],
                                ),
                                topic(
                                    "应用范围广、效果提升大",
                                    children=[
                                        topic("NLP：生成、翻译、问答、对话"),
                                        topic("CV：图像理解、生成、多模态对齐"),
                                        topic("语音：识别、合成、多模态交互"),
                                        topic("长上下文理解与多轮对话，部分任务接近或超过人类水平"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "1.2 常用大模型",
                            note="有开源协议模型，也有闭源 API 按 token 收费",
                            children=[
                                topic(
                                    "国际阵营",
                                    children=[
                                        topic("OpenAI GPT 系列：综合均衡，擅长工具运用和 Agent 工作流"),
                                        topic("o 系列：推理专用，数学和复杂分析强，成本较高"),
                                        topic("Anthropic Claude：编程领先，超长上下文，安全敏感场景好"),
                                        topic("Google Gemini：原生多模态文本图像音频视频，窗口大、性价比高；Flash 更快更便宜"),
                                        topic("xAI Grok：文本生成榜靠前，与 X 平台深度集成"),
                                    ],
                                ),
                                topic(
                                    "国产阵营",
                                    children=[
                                        topic("DeepSeek R1/V3：开源代表，推理逼近闭源，训练成本低、性价比高"),
                                        topic("月之暗面 Kimi：长文本专家，法律条文分析突出"),
                                        topic("智谱 GLM：清华系，中英双语和 Agent 好，国产硬件适配好"),
                                        topic("阿里通义千问 Qwen：开源生态强，中文场景优化好"),
                                        topic("字节豆包：语音识别与实时交互，稀疏 MoE 降成本"),
                                        topic("百度文心一言：文言文互译、方言交互"),
                                        topic("商汤 SenseChat、MiniMax 角色扮演与创意写作"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2 大模型调用",
                            children=[
                                topic(
                                    "2.1 OpenAI",
                                    children=[
                                        topic("开发平台：developers.openai.com"),
                                        topic("API Platform → Get started → Create an API Key"),
                                        topic("Key 放到环境变量后要重启 IDE"),
                                        topic("现在不免费，需充值，常要可境外结算的 Visa"),
                                        topic("没额度会报错；也可找国内中转，或直接用国内大模型"),
                                    ],
                                ),
                                topic(
                                    "2.2 阿里百炼 适合入门",
                                    children=[
                                        topic("一站式大模型开发平台 Model Studio"),
                                        topic("模型广场：通义千问、Llama、DeepSeek 等上百款"),
                                        topic("统一 API：OpenAI 兼容，降低接入成本"),
                                        topic("工具链：提示词、RAG 知识库、微调、智能体编排"),
                                        topic("企业级：高并发、内容安全、用量监控"),
                                        topic("为什么选它：国内直连低延迟、新人免费额度、从 turbo 到 max/R1 全覆盖、和 OSS/函数计算集成"),
                                        topic("关键概念：API-KEY 身份凭证"),
                                        topic("Endpoint：https://dashscope.aliyuncs.com/compatible-mode/v1"),
                                        topic("模型名：qwen-plus、qwen-max、deepseek-r1、qwen-turbo"),
                                        topic("需注册并实名，支付宝可完成；控制台底部 API-KEY 管理里创建"),
                                    ],
                                ),
                                topic(
                                    "2.3 调用百炼",
                                    children=[
                                        topic("Python >= 3.8"),
                                        topic("两种 SDK 二选一：DashScope 官方，或 OpenAI 多语言 SDK"),
                                        topic("建议装 openai，以后换别的兼容服务也能用"),
                                        topic("Key 写入系统环境变量，代码用 os.getenv 读取"),
                                        topic("若配置了 OPENAI_API_KEY，有的写法可省略显式传 key"),
                                    ],
                                ),
                                topic(
                                    "2.4 使用 OpenAI 库",
                                    children=[
                                        topic("官方 Python SDK：聊天、绘图、语音等，不用自己拼 HTTP"),
                                        topic("很多国产服务兼容这套调用方式"),
                                        topic(
                                            "基础三步",
                                            children=[
                                                topic("创建 OpenAI 对象，设 base_url 和 api_key"),
                                                topic("调用时必填 model 和 messages"),
                                                topic("从返回里取文本结果"),
                                            ],
                                        ),
                                        topic(
                                            "messages 四类",
                                            children=[
                                                topic("system：设角色、语气、目标、约束，一般放第一位"),
                                                topic("user：用户问题或指令，必填"),
                                                topic("assistant：模型历史回复，多轮时回传"),
                                                topic("tool：工具输出"),
                                                topic("都是字典，key/value 按官方文档写"),
                                            ],
                                        ),
                                        topic(
                                            "流式输出 stream",
                                            children=[
                                                topic("默认 false：整段生成完一次性返回"),
                                                topic("true：边生成边返回 chunk，要自己拼接"),
                                                topic("推荐 true：阅读体验好，也降低超时风险"),
                                            ],
                                        ),
                                        topic("附带历史：messages 是 list，把过往对话填回去，模型才知道上下文"),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                topic(
                    "三、大模型部署方式",
                    note="按成本和控制权分三种：云端 API、云上自托管、本地/边缘",
                    children=[
                        topic(
                            "1 云端 API",
                            children=[
                                topic("直接调 OpenAI、Anthropic、Google、阿里云、腾讯云、火山引擎"),
                                topic("拿到 Key，后端或前端 HTTP 调用"),
                                topic("优点：不养模型和硬件、快速用顶级模型、扩展稳定由厂商保障"),
                                topic("缺点：数据出网要评估合规、费用随调用量和定价变、延迟受网络影响"),
                            ],
                        ),
                        topic(
                            "2 云上自托管",
                            children=[
                                topic("在 AWS/阿里云/腾讯云上部署开源模型"),
                                topic("推理引擎：Transformer、vLLM、TGI、llama.cpp、Ollama"),
                                topic("对外服务：Nginx、FastAPI、gRPC"),
                                topic("优点：可控版本路由限流、细粒度监控日志、要私有化又想用云算力"),
                                topic("缺点：自己管下载、显存、扩容、监控，要 MLOps 能力"),
                                topic("MLOps：把 DevOps 用到机器学习全生命周期自动化"),
                                topic(
                                    "云上自托管服务器类型",
                                    children=[
                                        topic("公有云 GPU 实例：AWS p3/p4/g4dn、阿里云 GN7/V100、腾讯云 GN10；按需或包年，完整控制权；适合生产、长期训练"),
                                        topic("GPU 裸金属：阿里云神龙、AWS Nitro Enclaves；无虚拟化开销，性能极致；适合大规模分布式训练"),
                                        topic("容器化 GPU：AWS EKS、阿里云 ACK、Google GKE；K8s 编排弹性伸缩；适合微服务推理集群"),
                                        topic("Serverless GPU：SageMaker Serverless、Replicate；按调用付费零运维；适合轻量推理、突发流量"),
                                        topic("算力租赁：AutoDL、恒源云、Featurize、vast.ai；按小时计费即开即用"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "4 本地与边缘部署",
                            children=[
                                topic("个人电脑、实验室、私有机房推理"),
                                topic("工具：Ollama、LM Studio、Mac 上 MLX LM、llama.cpp、vLLM"),
                                topic("常用中小模型 7B/14B，加量化降显存"),
                                topic("优点：数据不出本地、无 API 费、可离线"),
                                topic("挑战：要 GPU 或强 CPU，自己管模型文件和版本"),
                                topic("边缘：把一部分云能力下沉到离用户更近的地方"),
                            ],
                        ),
                        topic(
                            "5 Ollama",
                            note="课上定位：知道即可，后面还要用 vLLM",
                            children=[
                                topic("是什么：开源、跨平台、轻量的本地大模型运行管理引擎"),
                                topic("不是模型本身，是运行容器和调度工具：下载、加载、推理、资源管理、对外服务"),
                                topic("过去要配 CUDA、转模型、手写参数；现在一条命令拉模型、一条命令对话"),
                                topic("官网 ollama.com，默认装 C 盘，模型目录务必改走"),
                                topic("内存：7B 约 8G 可用，13B 约 16G，33B 约 32G；磁盘建议预留 50G"),
                                topic("支持纯 CPU；有 NVIDIA GPU 可加速"),
                                topic("装模型：官网选模型看体积，终端拉下来就能对话"),
                                topic("本地 HTTP 默认 http://localhost:11434/api"),
                                topic("默认只允许本机 127.0.0.1 访问"),
                                topic("局域网：环境变量 OLLAMA_HOST=0.0.0.0，OLLAMA_ORIGINS=* 防跨域"),
                                topic("或改 ~/.ollama/config.json，改完必须重启"),
                                topic("浏览器访问 ip:11434 看到 Ollama is running 即成功"),
                                topic("Python 可普通调用、流式、接到 FastAPI；思考模型开始会短暂停顿无输出"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "四、大模型应用介绍",
                    children=[
                        topic(
                            "定义",
                            children=[
                                topic("以 LLM 为大脑，结合外部数据、记忆、工具，解决具体业务问题"),
                                topic("不只是聊天机器人，而是业务场景里的智能系统"),
                            ],
                        ),
                        topic(
                            "1 常见类型",
                            children=[
                                topic("Prompt Engineering：设计提示让输出符合格式逻辑，如文案、翻译。人要会说话对方才懂"),
                                topic("Conversational AI：加 Memory，记住多轮上下文，如 ChatGPT、智能客服"),
                                topic("RAG：外挂知识库，先检索私有资料再生成，解决没读过内部文档和幻觉"),
                                topic("RAG 比喻：预训练像通识，入职后再学公司制度才能答内部问题"),
                                topic("Agents：装手脚，能规划并调用工具查天气、跑代码、操作数据库"),
                                topic("Agent 比喻：自己不行就找同事、其他部门、领导协调；拧螺丝=工具+记忆中的经验"),
                            ],
                        ),
                        topic(
                            "2 构建挑战",
                            children=[
                                topic("数据连接：企业文档、数据库怎么接到 LLM"),
                                topic("上下文管理：长对话如何一致，面试常问 Agent 怎么记上下文"),
                                topic("工具调用：怎么调外部 API、数据库"),
                                topic("多步骤推理：决策链和任务分解"),
                                topic("可观察性：怎么调试和优化"),
                            ],
                        ),
                        topic(
                            "3 为什么需要框架",
                            children=[
                                topic("不是只会写提示词，需要完整工具链"),
                                topic("类似 Web 要用 Django、FastAPI、Spring、Vue"),
                                topic("LlamaIndex 等提供标准化、模块化组件"),
                            ],
                        ),
                        topic(
                            "4 LlamaIndex",
                            children=[
                                topic("定位：把私有数据接到 LLM，做 RAG、机器人、文档理解、Agent"),
                                topic("官网 llamaindex.ai，中文文档 docs.llamaindex.org.cn，GitHub run-llama/llama_index"),
                                topic("六模块：Data Connectors、Index、Retriever、Query Engine、Agents、Workflows"),
                            ],
                        ),
                        topic(
                            "5 LlamaIndex 使用",
                            children=[
                                topic(
                                    "调用不同模型要单独装包",
                                    children=[
                                        topic("DeepSeek：llama-index-llms-deepseek"),
                                        topic("千问不在默认列表，用 DashScope：llama-index-llms-dashscope"),
                                        topic("Ollama：llama-index-llms-ollama，模型必须本机已部署，ollama list 可查"),
                                        topic("多模态要选支持多模态的模型，如 qwen3.5:4b"),
                                    ],
                                ),
                                topic("llm.complete：单轮纯字符串，无角色、无状态"),
                                topic("llm.chat：消息列表可分 system/user/assistant，内置多轮，实际开发首选"),
                                topic("stream_complete 是生成器，delta 是本段新增文本"),
                                topic(
                                    "对话系统 Chatbot",
                                    children=[
                                        topic("无记忆：每轮独立"),
                                        topic("有记忆：Context + Memory 多轮连贯"),
                                        topic("可接 OpenAI、Qwen、Ollama、Llama、Claude"),
                                        topic("再接知识库就变成知识型 Chatbot"),
                                    ],
                                ),
                                topic(
                                    "RAG 能力清单",
                                    children=[
                                        topic("Reader 文档加载，SimpleDirectoryReader 可读杂乱无结构文件"),
                                        topic("Splitter 分块，前面往往只配置，真正切分在建索引时"),
                                        topic("Embedding 向量化：语义近则向量近，语义远则向量远"),
                                        topic("本地嵌入：Ollama 的 nomic-embed-text 或 qwen3-embedding:0.6b"),
                                        topic("云端嵌入：DashScope 千问，pip install llama-index-embeddings-dashscope"),
                                        topic("切分先用 Tokenizer 转 token 再按 token 数切块"),
                                        topic("VectorStoreIndex + Chroma 存储"),
                                        topic("Query Engine 查询；可加记忆做 RAG+多轮"),
                                    ],
                                ),
                                topic("示例数据：考勤知识入库、了凡四训问答"),
                            ],
                        ),
                        topic(
                            "作业",
                            children=[
                                topic("FastAPI 提供接口"),
                                topic("页面上传文档，向量化后存向量库"),
                                topic("简易对话窗口能聊天"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        topic(
            "02 提示词工程",
            note="飞书文档：01-提示词。Prompt 是指令，Prompt Engineering 是优化指令的技术。",
            children=[
                topic(
                    "一、概述",
                    children=[
                        topic("把 AI 当能力强但缺经验的新助手，指令清不清楚决定成果质量"),
                        topic("差提示：写一篇文章关于AI → 容易得到百科摘要式空文"),
                        topic("好提示：科技记者、800字、普通人用AI提效、25-40岁白领、具体案例、推荐3个工具、轻松幽默"),
                        topic(
                            "高质量提示通常含",
                            children=[
                                topic("角色：身份、专业领域"),
                                topic("任务：明确要做什么"),
                                topic("规则：边界、禁止、判断标准"),
                                topic("输出：格式、长度、示例、JSON 结构"),
                            ],
                        ),
                        topic("提示工程是系统化设计、测试、优化提示词的学科，不只写一句话"),
                    ],
                ),
                topic(
                    "1.2 设计原则",
                    children=[
                        topic(
                            "CLEAR 原则",
                            children=[
                                topic("Context 上下文：充分背景"),
                                topic("Length 长度：明确输出多长"),
                                topic("Examples 示例：给参考案例"),
                                topic("Audience 受众：指定读者"),
                                topic("Role 角色：定义 AI 身份"),
                            ],
                        ),
                        topic(
                            "优质 Prompt 特征",
                            children=[
                                topic("目标明确具体"),
                                topic("包含必要约束"),
                                topic("提供参考框架"),
                                topic("指定输出格式"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "二、构成要素和技巧",
                    children=[
                        topic(
                            "2.1 核心四要素",
                            children=[
                                topic("角色 Role：你是一位资深营销专家，专注社交媒体内容创作"),
                                topic("任务 Task：请生成5个小红书标题，每个不超过20字"),
                                topic("上下文 Context：目标用户25-35岁都市女性，关注美妆和生活"),
                                topic("约束 Constraints：避免夸张营销词，保持自然真实"),
                            ],
                        ),
                        topic(
                            "2.2 基础技巧",
                            children=[
                                topic("明确性：好=生成3个健康饮食微博；坏=写一些关于饮食的东西"),
                                topic("结构化：分点分段，便于执行"),
                                topic("示例引导：给输入输出样例，尤其复杂任务"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "三、调优实战技法",
                    children=[
                        topic(
                            "环境准备",
                            children=[
                                topic("pip install openai dashscope"),
                                topic("用 OpenAI 兼容方式跑百炼/千问"),
                                topic("Windows：此电脑→属性→高级系统设置→环境变量"),
                                topic("用户变量名 DASHSCOPE_API_KEY，值为 sk- 开头的 Key"),
                                topic("改完重启终端或 IDE"),
                            ],
                        ),
                        topic(
                            "零样本 Zero-Shot",
                            children=[
                                topic("直接给任务指令，不提供示例"),
                                topic("适合简单明确、模型已具备相关知识的任务"),
                            ],
                        ),
                        topic(
                            "少样本 Few-Shot",
                            children=[
                                topic("提供少量输入输出示例，让模型模仿格式和模式"),
                                topic("比只下指令效果更好"),
                                topic("情感例子：拍照好看→正面；物流太慢→负面；菜难吃→负面"),
                            ],
                        ),
                        topic(
                            "思维链 COT",
                            children=[
                                topic("先展示推理过程再给最终答案"),
                                topic("适合复杂逻辑、数学题"),
                                topic("可在问题后加：请一步步思考"),
                            ],
                        ),
                        topic(
                            "自我一致性 Self-Consistency",
                            children=[
                                topic("生成多个答案，投票或自评选出最优"),
                                topic("适合要高质量、多样化的输出，如选最佳口号"),
                            ],
                        ),
                        topic(
                            "思维树 ToT",
                            children=[
                                topic("多分支思考路径，探索不同方案"),
                                topic("适合需要创造性解决的复杂任务"),
                                topic("过程：发散分支 → 评估剪枝 → 再执行"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "四、攻击防范",
                    note="了解类型和防御思路即可，不要在生产里复现攻击细节",
                    children=[
                        topic(
                            "4.1.1 提示注入",
                            children=[
                                topic("在输入里嵌恶意指令，诱导模型做非预期行为"),
                                topic("直接注入：用户输入覆盖系统设定，如要求输出系统提示、绕过只答数学的限制"),
                                topic("间接注入：恶意指令藏在网页、PDF、简历等外部内容里，模型处理时触发"),
                                topic("其他手法：角色扮演劫持、编码混淆绕过关键词、把指令嵌进业务流程"),
                                topic("防御：过滤高风险指令用语、外部输入一律不可信、关键词+意图识别+输出再审+上下文隔离"),
                            ],
                        ),
                        topic(
                            "4.1.2 越狱 Jailbreak",
                            children=[
                                topic("精心构造提示，绕过安全限制，诱导输出本该拦截的内容"),
                                topic("常见方向：无约束角色扮演、多轮逐步诱导、用故事幽默包装、对抗后缀干扰检测、学术研究幌子、自动化生成越狱提示"),
                                topic("防御：多层次内容审核、行为监控"),
                            ],
                        ),
                        topic(
                            "4.1.3 数据泄露",
                            children=[
                                topic("巧妙提问套取训练或系统中的敏感信息"),
                                topic("相关风险还包括供应链工具、内部泄密、配置错误、社会工程、历史漏洞"),
                                topic("防御：拆分隐私、数据脱敏"),
                            ],
                        ),
                        topic(
                            "4.2 防范策略落地",
                            children=[
                                topic("输入净化：content_sanitize.py"),
                                topic("多层审核：content_moderation.py"),
                                topic("安全沙箱：隔离执行高风险操作，限制系统权限和网络"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "五、实战案例",
                    children=[
                        topic(
                            "5.1 优化过程通法",
                            children=[
                                topic("先写清业务需求"),
                                topic("初始版往往效果一般"),
                                topic("再加角色和约束"),
                                topic("再加少样本"),
                            ],
                        ),
                        topic(
                            "5.2 电商产品描述 ecprompt.py",
                            children=[
                                topic("输入：名称、核心卖点、目标人群"),
                                topic("输出：吸睛标题、痛点正文、小红书标签"),
                                topic("system 角色：电商金牌文案专家"),
                                topic("examples：完整的输入-思考-输出范例，锁语气和格式"),
                                topic("COT：先分析痛点再转化卖点，避免空洞废话"),
                                topic("temperature=0.7：太低死板，太高乱跑，0.7 是创意和稳定的平衡"),
                            ],
                        ),
                        topic(
                            "5.3 社交媒体内容策划",
                            children=[
                                topic("需求：不是单篇文案，而是成体系选题和多角度发散"),
                                topic("输入宽泛主题如夏季减肥，扮演资深新媒体运营"),
                                topic("ToT 三步：构思3个截然不同切入角度 → 评估爆款潜力与可行性 → 选出最佳并生成5个周更选题"),
                                topic("自我一致性：第二步回顾第一步并自我批判"),
                                topic("结构化输出：要求 Markdown 表格，方便进 Excel 或 Notion"),
                                topic("最后加自我反思 Self-Reflection"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "六、最佳实践",
                    children=[
                        topic("设计原则：明确、完整、角色风格一致、考虑安全"),
                        topic("调优策略：先零样本再加复杂度、按输出迭代、建立评估标准、记录有效模板"),
                        topic("趋势：自动生成优化提示、多模态提示、按反馈动态调、按用户特征个性化"),
                    ],
                ),
                topic(
                    "课后作业",
                    children=[
                        topic("完成电商产品描述生成"),
                        topic("完成社交媒体内容策划"),
                    ],
                ),
            ],
        ),
        topic(
            "03 RAG整体认知",
            note="飞书文档：01-RAG整体认知。2020年 Facebook AI 提出，解决大模型答得快但不够准、不够新。",
            children=[
                topic(
                    "1 RAG 介绍",
                    children=[
                        topic(
                            "1.1 是什么",
                            children=[
                                topic("全称 Retrieval-Augmented Generation，检索增强生成"),
                                topic("生成前先从外部知识库检索相关文档，作为附加上下文再生成"),
                                topic("目标：更准确、更新、有据可查"),
                                topic("核心思想：给 LLM 配外挂知识库"),
                                topic("比喻：开卷考试。模型是闭卷考生，RAG 是可随时翻的参考书"),
                                topic("技术本质：检索器 Retriever + 生成器 Generator"),
                            ],
                        ),
                        topic(
                            "1.2 RAG 与纯大模型 LLM-only 对比表",
                            children=[
                                topic("知识来源：纯模型只靠训练时记住的参数化知识；RAG=参数化知识+可随时更新的外部知识库"),
                                topic("知识时效：纯模型卡在训练截止日期，更新要重新微调；RAG 只需更新知识库文档，不必重训"),
                                topic("幻觉控制：纯模型容易对未知内容信口开河；RAG 有明确下文依据，可强制不知道就不答"),
                                topic("可解释性：纯模型无法溯源、难验证事实；RAG 可返回引用、支持核查"),
                                topic("领域适配：纯模型要大量微调数据和算力；RAG 只需准备领域文档，成本低"),
                                topic("上下文长度：纯模型受窗口限制；RAG 先检索筛选，可间接处理海量文档"),
                                topic("结论：RAG 不是替代大模型，而是给它装上实时、可信、可控的记忆外挂"),
                            ],
                        ),
                        topic(
                            "1.3 核心流程 Query → Embedding → Retrieval → Context → LLM → Answer",
                            children=[
                                topic("Query：自然语言问题，可能有错别字、口语、指代不明。如“上次那个产品的安全规范更新了吗”"),
                                topic("Embedding：用与知识库相同的嵌入模型，把问题变成高维向量，如 768 或 1536 维，变成可运算的语义坐标"),
                                topic("Retrieval：在向量库或倒排索引里算相似度，通常余弦相似度，召回 Top-K。这一步决定原材料质量，是成败瓶颈"),
                                topic("Context：按相似度或时间等顺序拼接片段，加上“请仅根据以下资料回答”等约束；太多要裁剪以适配窗口"),
                                topic("LLM：读完整 Prompt，当摘要者和解释者，而不是当记忆库"),
                                topic("Answer：返回给用户，通常附来源片段便于人工核查"),
                            ],
                        ),
                        topic(
                            "1.4 三大痛点",
                            children=[
                                topic(
                                    "幻觉 核心痛点",
                                    children=[
                                        topic("没有相关知识时编造看似合理的错误内容"),
                                        topic("RAG：强制只基于检索内容答，没有就提示无法回答，再加答案约束"),
                                    ],
                                ),
                                topic(
                                    "知识时效性差",
                                    children=[
                                        topic("训练数据有截止日期，无法回答最新政策、新版语言特性"),
                                        topic("RAG：更新外部知识库即可，不必重新训练，成本低"),
                                    ],
                                ),
                                topic(
                                    "私有内网知识难落地",
                                    children=[
                                        topic("闭源云模型要上传数据，处理不了涉密内部手册、校园内网通知"),
                                        topic("RAG：开源 LLM + 开源 Embedding + 本地向量库，数据不出内网，可用 FastAPI 封装"),
                                    ],
                                ),
                                topic("误区：RAG 不能 100% 消幻觉。检索错了或 Prompt 约束不到位仍会编"),
                            ],
                        ),
                        topic(
                            "1.5 主流场景",
                            children=[
                                topic("本地私有问答：笔记、公司手册，不联网"),
                                topic("PDF 问答：论文、教材、说明书，提问后定位相关页再生成"),
                                topic("智能客服：FAQ、售后流程，标准化回答，可内网部署"),
                                topic("多知识库：PDF+Word+网页一次提问全检索，如校园通知+手册+FAQ"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "2 RAG 体系架构",
                    children=[
                        topic(
                            "2.1 经典五步 先记做什么和为什么",
                            children=[
                                topic(
                                    "文档加载 Document Loading",
                                    children=[
                                        topic("做什么：PDF/Word/TXT/网页加载成程序可处理的文本"),
                                        topic("为什么：模型不能直接读本地文件"),
                                        topic("后续：LangChain/LlamaIndex，尤其 PDF 解析难点"),
                                    ],
                                ),
                                topic(
                                    "文本分割 Text Splitting",
                                    children=[
                                        topic("做什么：长文本切成 chunk"),
                                        topic("为什么：有上下文窗口限制；小片段比整篇更好检索"),
                                        topic("后续：chunk_size、chunk_overlap 调优"),
                                    ],
                                ),
                                topic(
                                    "向量化 Embedding",
                                    children=[
                                        topic("做什么：文本块变成高维数值向量"),
                                        topic("为什么：计算机用向量表示语义，才能语义检索"),
                                        topic("后续：开源 BGE/M3E 本地部署或调用"),
                                    ],
                                ),
                                topic(
                                    "向量存储 Vector Storage",
                                    children=[
                                        topic("做什么：向量写入向量数据库"),
                                        topic("为什么：MySQL 等不擅长语义相似查询，向量库做了相似度优化，可达毫秒级"),
                                        topic("后续：FAISS、Chroma 实操"),
                                    ],
                                ),
                                topic(
                                    "语义检索 + LLM 生成",
                                    children=[
                                        topic("问题向量化"),
                                        topic("在库中检索语义相似文本块"),
                                        topic("文本块+问题拼成 Prompt 交给 LLM"),
                                        topic("既要素材准，又要语言流畅"),
                                        topic("Prompt 要写：仅基于提供的检索内容回答，不要编造"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2.2 数据流拆解",
                            children=[
                                topic(
                                    "数据准备 Data Pipeline",
                                    children=[
                                        topic("文档解析：按格式提取纯文本和结构，标题、表格"),
                                        topic("数据清洗：去页眉页脚、广告、水印、乱码，规范空白"),
                                        topic("切分 Chunking：按语义或长度切，加 overlap 防止关键句被切断，质量直接影响检索"),
                                        topic("元数据：来源、时间、章节、标签，用于过滤和引用"),
                                    ],
                                ),
                                topic(
                                    "检索系统 Retriever",
                                    children=[
                                        topic("向量检索：语义相似，鲁棒，主力"),
                                        topic("稀疏检索 BM25：关键词，对专有名词、精确 ID 更好"),
                                        topic("混合检索：两者互补"),
                                        topic("输出：相关片段列表+相似度得分"),
                                    ],
                                ),
                                topic(
                                    "生成系统 Generator",
                                    children=[
                                        topic("载体：GPT、Llama、文心一言等"),
                                        topic("提示词：结构化注入检索结果，设禁止编造等约束"),
                                        topic("后处理：格式化，添加引用标记"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2.3 五大范式 学霸养成记",
                            children=[
                                topic(
                                    "Naive RAG 小学生会翻书",
                                    children=[
                                        topic("流程：提问 → 关键词或基础语义搜 → 填进上下文 → 生成"),
                                        topic("优点：简单、开发成本低、适合原型"),
                                        topic("缺点：同义不同词可能搜不到；无关片段导致幻觉；硬切会长文语义断裂"),
                                        topic("定位：Hello World，原型验证首选"),
                                    ],
                                ),
                                topic(
                                    "Advanced RAG 初中生找得更准",
                                    children=[
                                        topic("检索前：查询改写、扩展，提高模糊问题命中率"),
                                        topic("检索后：重排序 Re-ranking，精细模型二次打分，最相关的排前面"),
                                        topic("定位：效果和成本的平衡点，工业界主流"),
                                    ],
                                ),
                                topic(
                                    "Modular RAG 高中生灵活用工具",
                                    children=[
                                        topic("把检索器、生成器、重排器拆成可替换模块，像乐高"),
                                        topic("路由 Routing 和调度 Scheduling：判断走向量库、传统库还是互联网"),
                                        topic("定位：灵活可定制，是 LangChain、LlamaIndex 等框架基石"),
                                    ],
                                ),
                                topic(
                                    "Graph RAG 大学生理解知识关系",
                                    children=[
                                        topic("把段落提炼成实体-关系-实体三元组，用知识图谱"),
                                        topic("多跳推理：顺藤摸瓜回答要多步的问题"),
                                        topic("全局理解：能归纳主题，不只罗列片段，如从评价里归纳屏幕、续航"),
                                        topic("代表：微软开源 GraphRAG，适合大规模摘要和复杂关系"),
                                        topic("定位：从找相似跨越到做推理"),
                                    ],
                                ),
                                topic(
                                    "Agentic RAG 研究生自己规划",
                                    children=[
                                        topic("引入一个或多个 Agent，从被动工具变主动系统"),
                                        topic("主智能体拆子任务，分别调向量搜、网页搜、API"),
                                        topic("信息不足会自我反思并再检索"),
                                        topic("定位：当前最前沿，从执行者变成会规划的思考者"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2.4 RAG vs 模型微调 怎么选",
                            children=[
                                topic("领域知识增强时的第一选择：微调还是 RAG"),
                                topic("改知识：RAG 改文档即可；微调要重新训练，贵且慢"),
                                topic("改口吻风格、固定知识、要极低延迟：微调更合适"),
                                topic("要引用溯源、私有内网、知识常变：RAG 更合适"),
                                topic("可结合：微调让模型更会用检索资料，RAG 注入最新知识"),
                                topic("思考题：校园通知每月更新，该用 RAG，因为知识常变且不必重训"),
                            ],
                        ),
                        topic(
                            "2.5 局限与挑战",
                            children=[
                                topic("检索质量决定上限：最相关文件没召回，生成再强也没用"),
                                topic("上下文窗口：答案分散在多处时可能被截断"),
                                topic("检索噪声：无关片段会误导模型"),
                                topic("延迟增加：比纯 LLM 多一步检索，需要异步或缓存"),
                                topic("依赖 Embedding 和切分策略，中文和专业术语很敏感"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        topic(
            "04 Embedding 向量表示",
            note="飞书文档：02-大模型应用基础--Embeddings",
            children=[
                topic(
                    "1 什么是 Embedding",
                    children=[
                        topic(
                            "1.1 什么是向量",
                            children=[
                                topic("有大小和方向的数学对象，可看成有向线段"),
                                topic("二维可写成 (x, y)，从原点到该点"),
                                topic("Embedding：用数值向量表示一个对象"),
                            ],
                        ),
                        topic(
                            "1.2 用词频向量算句子相似度 五步",
                            children=[
                                topic("句子A：这个程序代码太乱，那个代码规范"),
                                topic("句子B：这个程序代码不规范，那个更规范"),
                                topic("Step1 分词：A=这个/程序/代码/太乱，那个/代码/规范；B=这个/程序/代码/不/规范，那个/更/规范"),
                                topic("Step2 词表固定顺序：这个、程序、代码、太乱、那个、规范、不、更"),
                                topic("Step3 词频：A 代码2 其余多数字1、不和更是0；B 规范2、代码1、太乱0、不1、更1"),
                                topic("Step4 八维向量：A=(1,1,2,1,1,1,0,0)  B=(1,1,1,0,1,2,1,1)"),
                                topic("二维直觉：你好吗你好吗你好=(3,2)，你好=(1,0)"),
                                topic(
                                    "Step5 余弦相似度",
                                    children=[
                                        topic("衡量方向像不像，范围约 -1 到 1，越接近 1 越像"),
                                        topic("点积：对应维度相乘再全加。同一词两边都高则点积大"),
                                        topic("本例点积=1+1+2+0+1+2+0+0=7"),
                                        topic("模长：各分量平方和再开方，词频越高句子显得越长越丰富"),
                                        topic("公式：点积 ÷ 两个模长的乘积"),
                                        topic("结果约 0.737：代码/不/更 有差异，但这个、程序等多数词相同仍较像"),
                                        topic("一句话：共同出现的词越多越频作分子，各自有多长作分母"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "1.3 一个好的语义向量",
                            children=[
                                topic("线性代数里的特征向量：被矩阵变换后方向不变只变长短"),
                                topic("比喻：橡皮泥里的铁丝，怎么捏方向大致不变"),
                                topic("词向量不是乱放的，语义关系编码成空间中跨词通用的方向"),
                                topic("性别轴：queen - king ≈ woman - man，所以 king - man + woman ≈ queen"),
                                topic("时态轴：walked - walking ≈ swam - swimming"),
                                topic("总结：词向量把语义变成算术"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "2 LLM 如何算词间距离",
                    children=[
                        topic("先把词变成上下文感知的高维向量，再用余弦相似度量化亲疏"),
                        topic("距离越小含义越近，是语义搜索、聚类、情感分析的基础"),
                        topic(
                            "2.1 调百炼做文本向量化",
                            children=[
                                topic("OpenAI 兼容客户端，base_url 用 dashscope compatible-mode v1"),
                                topic("接口：client.embeddings.create，取出每条的 embedding"),
                                topic("课上模型：text-embedding-v3，维度可设 128 或 1024"),
                                topic("例子：查询“大模型应用真好”，去和一堆餐饮文档向量比"),
                            ],
                        ),
                        topic(
                            "2.2 用 numpy 算余弦",
                            children=[
                                topic("点积 np.dot，再除以两个 L2 范数的乘积"),
                                topic("可对比：我爱你 vs 我恨你、vs 大模型有很多应用场景、vs python开发"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "3 Embedding 的三大作用",
                    children=[
                        topic(
                            "输入端语义编码",
                            children=[
                                topic("模型不能直接处理原始文本"),
                                topic("Embedding 层把 token 转为向量"),
                                topic("才能区分我爱你和我恨你在语义空间里的对立位置"),
                                topic("为后续注意力机制提供可计算表示"),
                            ],
                        ),
                        topic(
                            "语义检索与 RAG 应用层最常用",
                            children=[
                                topic("知识库检索：问题向量化，在文档向量库里定位相关片段"),
                                topic("相似度匹配：判断两段是否在谈同一件事"),
                                topic("去重与聚类：发现语义重复内容"),
                            ],
                        ),
                        topic(
                            "跨模态理解基础",
                            children=[
                                topic("文本和图像可共享同一 Embedding 空间"),
                                topic("一只橙色的猫 的文本和对应图片会靠近"),
                                topic("从而支持图文检索、零样本分类"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "4 如何得到 Embedding 了解",
                    children=[
                        topic(
                            "Word2Vec 两种架构",
                            children=[
                                topic("CBOW：用上下文预测中心词。给你相邻词，猜中间是什么。众人推举一个代表"),
                                topic("Skip-gram：用中心词预测上下文。给你一个词，猜周围可能出现什么。一个代表辐射众人"),
                            ],
                        ),
                        topic(
                            "模型结构 三层网络",
                            children=[
                                topic("关键词：One-hot、Multi-hot、隐藏层维度 N"),
                                topic("课上示意：词表大小 V=10，隐藏层 N=4"),
                                topic("W 是 V×N：输入到隐藏，每一行就是一个词的词向量"),
                                topic("W' 是 N×V：隐藏到输出"),
                                topic("输入 one-hot 只有当前词位置为 1"),
                                topic("h = x @ W，等价于直接取出 W 的那一行"),
                                topic("u = h @ W'，再 softmax 得到词表上的概率分布"),
                            ],
                        ),
                        topic("Embedding 位于隐藏层权重矩阵 W，相当于词向量查找表"),
                    ],
                ),
            ],
        ),
        topic(
            "05 向量数据库",
            note="飞书文档：03-大模型应用基础--向量数据库",
            children=[
                topic(
                    "第一部分 向量检索基础",
                    children=[
                        topic(
                            "从传统搜索到向量搜索",
                            children=[
                                topic("传统关键词/LIKE：不懂笔记本电脑和电脑相似"),
                                topic("多语言障碍：难跨语言搜"),
                                topic("语境缺失：不懂上下文"),
                                topic("向量方案：文本图像等变成高维数值向量，在空间里算相似性，才是语义理解"),
                            ],
                        ),
                        topic("向量：数学上有大小有方向；机器学习里是数据的数值化表示"),
                        topic(
                            "为什么要专门的向量数据库",
                            children=[
                                topic("课上问题：100 万个 128 维向量里找最像的 10 个"),
                                topic("传统 SQL 按距离排序：要对全部向量算一遍，复杂度 O(N)"),
                                topic("高维空间里普通索引几乎帮不上忙"),
                                topic("近似搜索 ANN：牺牲少量精度换大幅速度"),
                                topic("专用索引：HNSW、IVF 等高维结构"),
                                topic("性能优化：GPU 加速、批量处理"),
                            ],
                        ),
                        topic(
                            "核心指标 讲义表",
                            children=[
                                topic("查询延迟 Latency：单次响应时间。毫秒级适合实时，秒级适合离线批处理"),
                                topic("吞吐量 Throughput：每秒查询数 QPS，衡量并发"),
                                topic("准确率 Accuracy：近似搜和精确搜有多接近。Recall@K=前K个里包含真正近邻的比例"),
                                topic("存储：内存占用、索引磁盘大小"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "第二部分 FAISS",
                    children=[
                        topic(
                            "简介",
                            children=[
                                topic("Facebook AI Similarity Search，2015 年起，解决高维向量快速检索"),
                                topic("C++ 开发，提供 Python 接口"),
                                topic("支持平面、哈希、树形等索引，余弦、欧氏等度量"),
                                topic("场景：图像检索、文本匹配、视频推荐"),
                                topic("特点：可 GPU、单机十亿级、算法多、MIT 许可、被 Milvus Qdrant 等采用"),
                            ],
                        ),
                        topic(
                            "安装与第一个程序",
                            children=[
                                topic("初学者：pip install faiss-cpu，或 conda-forge"),
                                topic("有 NVIDIA+CUDA 再装 faiss-gpu"),
                                topic("流程：随机向量 → 创建索引 → add → search → 返回结果"),
                                topic("课上示例：10000 条、每条 128 维 float32 矩阵"),
                            ],
                        ),
                        topic(
                            "索引选型决策树",
                            children=[
                                topic("不到 100 万：精度要极高用 IndexFlat，否则 IndexIVFFlat"),
                                topic("100 万到 1 亿：要极速用 IndexHNSW，否则 IVFFlat 保精度"),
                                topic("超过 1 亿：内存紧用 IndexIVFPQ 压缩，否则 IVFFlat 加 GPU"),
                            ],
                        ),
                        topic(
                            "IndexFlat 精确索引",
                            children=[
                                topic("FlatL2：欧氏距离"),
                                topic("FlatIP：内积/点积"),
                                topic("余弦：先 faiss.normalize_L2，再用 IndexFlatIP"),
                                topic("适用：小于约 10 万、要极高精确、当其他索引的精度基准"),
                            ],
                        ),
                        topic(
                            "IndexIVFFlat 倒排文件索引",
                            children=[
                                topic("把向量空间划成多个聚类中心 Voronoi 区域"),
                                topic("每个向量分到最近中心，查询只搜最近几个中心"),
                                topic("必须先 index.train，内部是 k-means；不训练不能搜"),
                                topic("quantizer 常用底层 IndexFlatL2"),
                                topic("nlist：聚类中心数，通常取 sqrt(N)。太小每簇太大；太大要查的簇变多"),
                                topic("nprobe：查几个簇。1 最快最糙；等于 nlist 就变精确搜"),
                                topic("正向索引：文档→词，搜“苹果”要扫 100 万篇，O(N)"),
                                topic("倒排索引：词→文档，直接取倒排表，接近 O(1)，课上说可提速约 100 倍"),
                                topic("FAISS 里用簇代替词，思想一样"),
                            ],
                        ),
                        topic(
                            "IndexHNSWFlat 分层可导航小世界",
                            children=[
                                topic("基于图的 ANN，灵感来自高速公路和六度分隔"),
                                topic("多层图：上层稀疏快速跳跃，下层密集精细搜索"),
                                topic("课上参数：M=16 每个节点最大连接数"),
                                topic("efConstruction=200：建索引时候选队列，越大质量越高、建得越慢"),
                                topic("efSearch=50：查询时候选队列，越大越准、越慢"),
                                topic("被 Milvus、Pinecone、Qdrant、Weaviate 等广泛使用"),
                                topic("当前多数系统默认推荐，精度和速度较均衡"),
                            ],
                        ),
                        topic("选型补充：IVF 系列更适合超大规模且资源受限；还要看延迟敏感度和运维能力"),
                    ],
                ),
                topic(
                    "常见向量库对照",
                    children=[
                        topic("Milvus：HNSW、IVF_FLAT/PQ/SQ、FLAT；分布式，冲千亿级"),
                        topic("Pinecone：托管，内部优化 HNSW，自动扩展"),
                        topic("Weaviate：HNSW；关键词+语义混合，模块化嵌模型"),
                        topic("Qdrant：HNSW、FLAT；Rust，高级过滤和地理查询"),
                        topic("Chroma：默认 HNSW 类 ANN，也可设欧氏或余弦；轻量，偏 LLM，可嵌入式"),
                        topic("Faiss：FLAT、IVF、HNSW、PQ、LSH；高性能库，可 GPU，偏研究与大规模实验"),
                        topic("Elasticsearch 向量插件：HNSW，全文+向量企业混合搜"),
                        topic("Deep Lake：多模态存储与流式检索"),
                        topic("Vearch：云原生分布式，推理和推荐"),
                    ],
                ),
                topic(
                    "第三部分 Chroma",
                    children=[
                        topic(
                            "定位",
                            children=[
                                topic("开源 AI 原生向量库，为 LLM 应用设计，强调好写、快集成"),
                                topic("设计哲学：4 个核心 API 覆盖主要操作"),
                                topic("可接 OpenAI、HuggingFace 等嵌入"),
                                topic("原生支持向量和元数据关联查询"),
                                topic("与 LangChain、LlamaIndex 集成顺"),
                                topic("安装：pip install chromadb，或 conda-forge"),
                            ],
                        ),
                        topic(
                            "四种操作串起来",
                            children=[
                                topic("1 创建客户端，相当于连上一个数据库实例"),
                                topic("2 create_collection，类似关系库里的表"),
                                topic("3 add：documents + metadatas + ids"),
                                topic("4 query：用自然语言查最相似的几条"),
                            ],
                        ),
                        topic(
                            "三种客户端",
                            children=[
                                topic("Client()：内存临时库，进程结束数据就没了"),
                                topic("PersistentClient(path=./chroma_data)：落到磁盘"),
                                topic("HttpClient(host, port)：连远程 chroma run 服务"),
                            ],
                        ),
                        topic(
                            "集合 Collection",
                            children=[
                                topic("基本结构：向量 Embeddings + 原文 Documents + 元数据 Metadata + id"),
                                topic("create_collection：新建，已存在会报错"),
                                topic("get_collection：取已有集合，不存在会报错"),
                                topic("get_or_create_collection：有则取、无则建，入门最常用"),
                                topic("list_collections 可看库里一共有多少集合"),
                                topic("课上示例集合名：kaoqin 考勤、ruzhi 入职、liaofan 了凡四训"),
                            ],
                        ),
                        topic(
                            "add 添加",
                            children=[
                                topic("ids 必填：唯一标识，去重和更新删除用；已存在默认跳过不覆盖"),
                                topic("documents：原文，会按集合的嵌入函数自动转向量"),
                                topic("没自定义嵌入时，默认 all-MiniLM-L6-v2，约 384 维"),
                                topic("metadatas：键值对，供 where 过滤。常见 key：source category author url page date"),
                                topic("embeddings：也可直接塞预计算向量，适合已用千问或 OpenAI 算好的场景"),
                            ],
                        ),
                        topic(
                            "query 查询",
                            children=[
                                topic("query_texts：查询文本，自动转向量，可一次多个查询"),
                                topic("query_embeddings：直接给向量，与 query_texts 二选一"),
                                topic("n_results：每个查询返回几条，默认 10"),
                                topic("where：按 metadata 过滤，如 category=年假，page>=5，$and 组合"),
                                topic("where_document：$contains 对原文做包含匹配"),
                                topic("include：documents / metadatas / embeddings / distances，默认文档、元数据、距离"),
                                topic("课上流程：问句向量化 → 和库中算 L2 → 取 Top-K"),
                            ],
                        ),
                        topic(
                            "距离函数 hnsw:space",
                            children=[
                                topic("默认 L2 欧氏距离"),
                                topic("创建集合时 metadata 指定，三选一：l2、cosine、ip"),
                                topic("写法：metadata={\"hnsw:space\": \"cosine\"}"),
                                topic("一旦创建不能改，再改会 ValueError"),
                            ],
                        ),
                        topic(
                            "自定义嵌入",
                            children=[
                                topic("OpenAIEmbeddingFunction，模型如 text-embedding-ada-002"),
                                topic("千问：用 OpenAI 兼容接口桥接 DashScope，text-embedding-v3"),
                                topic("查询必须和写入用同一套嵌入，否则向量不在同一空间，检索会乱"),
                            ],
                        ),
                        topic(
                            "服务器模式",
                            children=[
                                topic("chroma run --path 存储路径 --host ip --port 端口，相当于启动 MySQL"),
                                topic("课上例子：chroma run --path .\\chroma_data02\\ --host 127.0.0.1 --port 8989"),
                                topic("Python 用 HttpClient 连上去，再 list、add、query"),
                            ],
                        ),
                        topic(
                            "更新与删除",
                            children=[
                                topic("update：可改文档内容和元数据"),
                                topic("delete：可按 id 列表删，也可先按元数据条件查出再删"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "第四部分 实战项目",
                    children=[
                        topic("目标：自然语言查询，返回最相关文档"),
                        topic("技术栈：Chroma + 千问 DashScope 嵌入 + FastAPI"),
                        topic("依赖：pip install chromadb fastapi uvicorn"),
                        topic(
                            "阶段一 建库",
                            children=[
                                topic("加载 → 分块 → get_embedding 向量化"),
                                topic("add_documents：原文进 self.documents，向量进索引"),
                            ],
                        ),
                        topic(
                            "阶段二 检索 search",
                            children=[
                                topic("问题向量化"),
                                topic("索引返回相似向量下标"),
                                topic("用下标从 self.documents 取原文"),
                                topic("原文+问题再交给大模型回答"),
                            ],
                        ),
                        topic("课上测试：GET /search?q=向量搜索工具&k=3"),
                        topic("参考：faiss.ai 、 docs.trychroma.com"),
                    ],
                ),
            ],
        ),
        topic(
            "06 Native RAG（基础RAG）",
            note="飞书文档：01-Native_RAG（基础RAG）https://ecnwvcdzorsp.feishu.cn/docx/WAyydkEX2o81xAxFkn1cJRqqnnY",
            children=[
                topic(
                    "一、技术原理",
                    children=[
                        topic(
                            "1 为什么需要RAG",
                            note="大模型的局限性",
                            children=[
                                topic("知识时效性：无法实时获取最新数据，如 GPT-3 知识停在 2021"),
                                topic("幻觉问题：基于概率生成，Prompt 上限即回答有效性上限"),
                                topic("垂直领域覆盖不足：医疗等行业资料多为机密，通用模型吃不到"),
                            ],
                        ),
                        topic(
                            "2 RAG原理（Native RAG 三步）",
                            children=[
                                topic("Indexing：文档向量化，写入向量库建索引"),
                                topic("Search：问题 Embedding 后检索最相关文档片段"),
                                topic("Generate：把片段塞进 Prompt，由 LLM 生成可读回答"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "二、RAG流程",
                    children=[
                        topic("大致分三个阶段：数据准备 → 检索 → 生成（讲义有总流程图）"),
                    ],
                ),
                topic(
                    "三、数据准备阶段",
                    children=[
                        topic(
                            "1 数据准备",
                            children=[
                                topic("原始数据常有：格式难识别、内容不一致、不完整、不合法"),
                                topic("第一性原理：加上下文能提准确性，但数据质量差会负向影响"),
                            ],
                        ),
                        topic(
                            "2 向量化 Embedding",
                            children=[
                                topic("向量检索按语义相似度找内容，保障输出有效性"),
                                topic("选型可参考 MTEB Leaderboard：huggingface.co/spaces/mteb/leaderboard"),
                                topic(
                                    "本地下载模型",
                                    children=[
                                        topic("HuggingFace：可设 HF_ENDPOINT=https://hf-mirror.com 镜像"),
                                        topic("hf download BAAI/bge-base-zh-v1.5 --local-dir ..."),
                                        topic("环境变量 HF_HOME / TRANSFORMERS_CACHE 统一缓存目录"),
                                        topic("国内更快：pip install modelscope 后 modelscope download"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "3 知识存储",
                            children=[
                                topic("向量化后写入向量库"),
                                topic("建立 embedding 与文档切片 chunk 的映射"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "四、LlamaIndex 的 RAG",
                    children=[
                        topic(
                            "1 LlamaIndex 简介",
                            children=[
                                topic(
                                    "1.1 介绍",
                                    children=[
                                        topic("原名 GPT Index，面向 LLM 的数据开发与编排框架"),
                                        topic("打通私有数据与通用大模型：加载→切分→向量化→检索→生成"),
                                        topic("可用极少代码接入文档、数据库、API，快速做生产级 RAG"),
                                    ],
                                ),
                                topic("1.2 核心概念速览：Document / Node / Index / Retriever / QueryEngine / ChatEngine"),
                            ],
                        ),
                        topic(
                            "2 文档加载",
                            children=[
                                topic(
                                    "2.1 SimpleDirectoryReader",
                                    children=[
                                        topic("核心包内置通用加载器"),
                                        topic("自动识别 .txt .pdf .docx .csv .md 等"),
                                        topic("可 input_dir + recursive + required_exts 加载整目录"),
                                        topic("可 input_files=[...] 加载指定文件列表"),
                                        topic("load_data() 得到 Document 列表，可看 metadata 与 text 预览"),
                                    ],
                                ),
                                topic(
                                    "2.2 专用加载器 llama-index-readers-file",
                                    children=[
                                        topic("pip install llama-index-readers-file，20+ 种精细解析"),
                                        topic(
                                            "PDF",
                                            children=[
                                                topic("PDFReader：轻量，底层 pypdf，适合纯文本"),
                                                topic("PyMuPDFReader：高性能，特性更多"),
                                                topic("UnstructuredReader：擅长表格、标题等复杂结构"),
                                                topic("依赖可选：unstructured[pdf]、PyMuPDF"),
                                                topic("用 SimpleDirectoryReader 的 file_extractor={'.pdf': parser}"),
                                            ],
                                        ),
                                        topic(
                                            "Word / PPT / CSV",
                                            children=[
                                                topic("DocxReader、PptxReader、PandasCSVReader"),
                                                topic("Word 常需 pip install docx2txt"),
                                            ],
                                        ),
                                        topic(
                                            "Markdown / HTML / 代码 / 笔记",
                                            children=[
                                                topic("MarkdownReader：保留标题层级"),
                                                topic("HTMLTagReader、IPYNBReader、XMLReader"),
                                                topic("IPYNB 可装 nbconvert"),
                                            ],
                                        ),
                                        topic("加载器选择：按格式选专用；通用杂糅文件先用 SimpleDirectoryReader"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "3 文档分块",
                            children=[
                                topic(
                                    "3.1 基础切分器",
                                    children=[
                                        topic(
                                            "TokenTextSplitter",
                                            children=[
                                                topic("按 Token 数切分，严格控制上下文窗口"),
                                                topic("先用 separator（如句号）切；超长再用 backup_separators"),
                                                topic("仍超长则硬截断；最后合并并加 overlap"),
                                            ],
                                        ),
                                        topic(
                                            "SentenceSplitter（默认推荐）",
                                            children=[
                                                topic("优先保证句子完整，同时控制 chunk_size"),
                                                topic("步骤1：paragraph_separator（默认\\n\\n\\n）按段落切"),
                                                topic("步骤2：secondary_chunking_regex 切成完整句子"),
                                                topic("步骤3：累加句子直到接近 chunk_size 成一块"),
                                                topic("步骤4：下一块带上上块末尾 overlap 句子"),
                                                topic("单句本身 > chunk_size 时可能报错，需预处理"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "3.2 语义切分 SemanticSplitterNodeParser",
                                    children=[
                                        topic("先分句 → 组合成组合句 → Embedding 算相似度 → 按阈值切"),
                                        topic("buffer_size=1：组合句约含前后各1句+当前句"),
                                        topic("breakpoint_percentile_threshold 越高，切得越粗"),
                                        topic("中文需自定义 chinese_sentence_splitter（。！？!?\\n）"),
                                        topic("可配 DashScopeEmbedding(text-embedding-v3)"),
                                        topic("注意：需过滤空文本 clean_empty_text；参数要调优"),
                                    ],
                                ),
                                topic(
                                    "3.3 选择建议",
                                    children=[
                                        topic("常规 RAG：SentenceSplitter，平衡上下文与精度"),
                                        topic("长文要语义连贯：SemanticSplitterNodeParser"),
                                        topic("代码库：CodeSplitter，避免切断函数中间"),
                                        topic("句子级精确检索：SentenceWindowNodeParser + MetadataReplacementPostProcessor"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "4 文档向量化并存储 Embedding",
                            children=[
                                topic("pip install llama-index-vector-stores-chroma"),
                                topic("Settings.embed_model = DashScopeEmbedding(model_name=text-embedding-v3, text_type=document)"),
                                topic("SimpleDirectoryReader 加载 → SentenceSplitter 分块"),
                                topic("Chroma PersistentClient + get_or_create_collection"),
                                topic("ChromaVectorStore → StorageContext → VectorStoreIndex(nodes)"),
                                topic("执行顺序：Index 遍历 node → embed_model 生成向量 → collection.add 写入"),
                                topic("千问限制：单条 ≤8192 tokens；batch size ≤10"),
                            ],
                        ),
                        topic(
                            "5 检索与大模型回复",
                            children=[
                                topic("重新挂 Settings.embed_model（须与建库同一模型）"),
                                topic("PersistentClient → get_collection → ChromaVectorStore"),
                                topic("VectorStoreIndex.from_vector_store 恢复索引"),
                                topic("as_query_engine：一次性检索+生成"),
                                topic("as_chat_engine(chat_mode=condense_plus_context) + ChatMemoryBuffer：多轮"),
                                topic("项目落地：semantic_search 的 /search /query /chat /ingest"),
                            ],
                        ),
                    ],
                ),
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


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def to_opml_outline(node, indent=4) -> str:
    title = escape_xml(node["title"])
    kids = node.get("children", {}).get("attached", [])
    pad = " " * indent
    if not kids:
        return f'{pad}<outline text="{title}"/>'
    inner = "\n".join(to_opml_outline(c, indent + 2) for c in kids)
    return f'{pad}<outline text="{title}">\n{inner}\n{pad}</outline>'


def _collect_titles(node, prefix="") -> list[str]:
    """把子树标题展平成文本行，塞进备注用。"""
    lines = [f"{prefix}{node['title']}"]
    for child in node.get("children", {}).get("attached", []):
        lines.extend(_collect_titles(child, prefix + "· "))
    return lines


def compact_tree(node, max_depth=3, depth=0):
    """限制展开深度：更深层的内容收到备注，导图不会拉得很长。"""
    import copy

    node = copy.deepcopy(node)
    kids = node.get("children", {}).get("attached", [])
    if not kids:
        return node

    if depth >= max_depth:
        detail_lines = []
        for child in kids:
            detail_lines.extend(_collect_titles(child))
        old_note = node.get("notes", {}).get("plain", {}).get("content", "")
        merged = (old_note + "\n\n" if old_note else "") + "\n".join(detail_lines)
        node["notes"] = {"plain": {"content": merged.strip()}}
        node.pop("children", None)
        return node

    node["children"] = {
        "attached": [compact_tree(child, max_depth, depth + 1) for child in kids]
    }
    return node


def main():
    # 放射状地图布局（比「从左到右」短很多）；细节压到第 3 层备注里
    visual = compact_tree(TREE, max_depth=3)
    visual["structureClass"] = "org.xmind.ui.map.unbalanced"
    content = [
        {
            "id": nid(),
            "class": "sheet",
            "title": "RAG入门课",
            "rootTopic": visual,
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

    xmind_path = OUT_DIR / "RAG入门课.xmind"
    with zipfile.ZipFile(xmind_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))

    # Markdown / OPML 仍保留完整细节，方便搜索阅读
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
    (OUT_DIR / "RAG入门课-XMind导入.opml").write_text(opml, encoding="utf-8")
    print(xmind_path)
    print(md_path)
    print("layout=map.unbalanced, visual_depth<=3 (details in notes)")


if __name__ == "__main__":
    main()
