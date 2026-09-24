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
        "根据飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、"
        "Native RAG、Advanced RAG、检索前优化（Pre-retrieval）、检索中优化（Retrieval）。"
    ),
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
                                topic("对照代码：见本章「五、代码详解」909.py 的 memory.put + stream_chat"),
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
                topic(
                    "五、代码详解（仓库对照）",
                    note="对照「基础聊天机器人」(原908) 与 909.py（LlamaIndex 多轮）。每条都是：代码 → 意思 → 注意点。",
                    children=[
                        topic(
                            "1 读密钥",
                            children=[
                                topic(
                                    "load_dotenv(脚本目录 / '.env')",
                                    children=[
                                        topic("意思：把 .env 里的 KEY=值 读进 os.environ"),
                                        topic("为什么：密钥不写死在代码里，换机器只改 .env"),
                                        topic("注意：必须用脚本所在目录；用相对路径会受 IDE 工作目录影响读不到"),
                                    ],
                                ),
                                topic(
                                    "api_key = os.getenv('DEEPSEEK_API_KEY')",
                                    children=[
                                        topic("意思：从环境变量取出密钥字符串"),
                                        topic("大坑：写成 api_key='DEEPSEEK_API_KEY' 会把字面量当密钥，一定报错"),
                                        topic("兜底：基础聊天机器人还用 winreg 读 Windows 用户/系统变量"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "2 创建客户端（还不发请求）",
                            children=[
                                topic(
                                    "from openai import OpenAI",
                                    children=[
                                        topic("意思：导入官方兼容 SDK（很多国产模型都能用这一套）"),
                                    ],
                                ),
                                topic(
                                    "client = OpenAI(api_key=key, base_url='https://api.deepseek.com')",
                                    children=[
                                        topic("意思：创建一个「会说话的客户端对象」，记下地址和密钥"),
                                        topic("这一步只连配置，不会产生费用、也不会生成文字"),
                                        topic("换百炼：base_url 改成 dashscope 的 compatible-mode/v1，model 改成 qwen-plus 等"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "3 发对话请求",
                            children=[
                                topic(
                                    "client.chat.completions.create(model=..., messages=..., stream=True)",
                                    children=[
                                        topic("意思：真正向服务器发一轮聊天请求"),
                                        topic("model：用哪颗模型；messages：对话历史列表"),
                                        topic("stream=True：边生成边返回；False：等整段说完一次返回"),
                                        topic("messages 每条是字典，至少含 role（system/user/assistant）和 content"),
                                    ],
                                ),
                                topic(
                                    "非流式取全文：response.choices[0].message.content",
                                    children=[
                                        topic("意思：从返回对象里取出助手说的整段文字"),
                                        topic("choices[0]：第一条候选（一般只用这一条）"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "4 流式怎么拼字（打字机效果）",
                            children=[
                                topic(
                                    "for chunk in stream: content = chunk.choices[0].delta.content",
                                    children=[
                                        topic("意思：流式接口一次只给一小段新增字，叫 delta"),
                                        topic("为什么用 for：要边收边推给前端，不能等全部结束"),
                                    ],
                                ),
                                topic(
                                    "必须 if content: 再拼接",
                                    children=[
                                        topic("意思：有的 chunk 是空包，delta.content 是 None"),
                                        topic("不判断直接 += 会报错或拼进 'None' 字符串"),
                                    ],
                                ),
                                topic(
                                    "ai_result += content",
                                    children=[
                                        topic("意思：自己攒完整回复，后面才能写入历史"),
                                        topic("不攒的话：屏幕上有字，memory 里没有，下一轮会失忆"),
                                    ],
                                ),
                                topic(
                                    "SSE：yield 'data: {json}\\n\\n'，最后 [DONE]",
                                    children=[
                                        topic("意思：浏览器 EventSource 约定的格式，一行一个事件"),
                                        topic("FastAPI：StreamingResponse(..., media_type='text/event-stream')"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "5 LlamaIndex 多轮（909.py）",
                            children=[
                                topic(
                                    "llm = DeepSeek(model=..., api_key=..., timeout=120)",
                                    children=[
                                        topic("意思：用 LlamaIndex 包装好的 DeepSeek 客户端"),
                                        topic("后面用 llm.chat / stream_chat，不用自己拼 OpenAI 返回结构"),
                                    ],
                                ),
                                topic(
                                    "memory = ChatMemoryBuffer.from_defaults(token_limit=10000)",
                                    children=[
                                        topic("意思：一块「对话记事本」，按 token 上限自动裁旧消息"),
                                        topic("10000：大约能记住很长一段多轮；太大费钱，太小易忘"),
                                    ],
                                ),
                                topic(
                                    "memory.put(ChatMessage(role='system', content='...'))",
                                    children=[
                                        topic("意思：先写入人设/规则，模型之后每轮都能看到"),
                                        topic("一般只在启动时写一次，不要每轮重复塞"),
                                    ],
                                ),
                                topic(
                                    "每轮三步：put(user) → stream_chat(memory.get()) → put(assistant)",
                                    children=[
                                        topic("put(user)：先把用户话记下来，再问模型"),
                                        topic("memory.get()：把当前全部历史作为上下文交给模型"),
                                        topic("put(assistant)：把完整回复记回去，否则下一轮不知道自己说过什么"),
                                    ],
                                ),
                                topic(
                                    "for r in llm.stream_chat(...): print(r.delta)",
                                    children=[
                                        topic("意思：r.delta 是本块新增字，边打边显示"),
                                        topic("要完整答案：自己 ai_result += (r.delta or '')"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "6 三种调用怎么选",
                            children=[
                                topic(
                                    "llm.complete('一段话')",
                                    children=[
                                        topic("意思：单轮、无角色，输入输出都是纯字符串"),
                                        topic("适合：内部小任务、改写、评分，不适合正式多轮客服"),
                                    ],
                                ),
                                topic(
                                    "llm.chat(messages)",
                                    children=[
                                        topic("意思：传入 system/user/assistant 列表，一次拿完整回复"),
                                        topic("适合：正式对话、要人设、要历史"),
                                    ],
                                ),
                                topic(
                                    "llm.stream_chat(messages)",
                                    children=[
                                        topic("意思：和 chat 一样，但是一块块返回，体验更好、不易超时"),
                                        topic("适合：网页/终端打字机效果"),
                                    ],
                                ),
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
                        topic(
                            "设计原则",
                            children=[
                                topic("明确：一次只交代一件主任务，避免又写文案又做分析"),
                                topic("完整：角色 + 任务 + 上下文 + 约束 + 输出格式尽量齐"),
                                topic("角色风格一致：system 人设不要和 user 指令打架"),
                                topic("考虑安全：外部用户输入不可直接拼进系统提示"),
                            ],
                        ),
                        topic(
                            "调优策略",
                            children=[
                                topic("先零样本：确认模型会不会做，再决定要不要加示例"),
                                topic("再加复杂度：Few-Shot → COT → ToT，按失败点加，不一次堆满"),
                                topic("按输出迭代：先改格式，再改事实，再改语气"),
                                topic("建立评估标准：正确、完整、格式、安全四项打分"),
                                topic("记录有效模板：把跑通的 Prompt 存成可复用版本"),
                            ],
                        ),
                        topic(
                            "趋势",
                            children=[
                                topic("自动生成/优化提示：用模型改模型的指令"),
                                topic("多模态提示：图+文一起当指令"),
                                topic("按反馈动态调：根据用户点踩实时改约束"),
                                topic("按用户特征个性化：同一任务对不同受众换角色和口吻"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "课后作业",
                    children=[
                        topic("完成电商产品描述生成：标题 + 痛点正文 + 标签"),
                        topic("完成社交媒体内容策划：ToT 选题 + 表格输出"),
                        topic("对照：能说清自己加了角色、少样本还是思维链"),
                    ],
                ),
                topic(
                    "七、代码详解（带安全校验 / 文案项目）",
                    note="对应「带安全校验的聊天机器人」与「社交媒体文案和电商内容生成」（原 910.py）。每条：代码 → 意思 → 为什么。",
                    children=[
                        topic(
                            "启动时做了什么",
                            children=[
                                topic(
                                    "llm = DeepSeek(...) 只建一次",
                                    children=[
                                        topic("意思：整个服务共用一个模型客户端"),
                                        topic("为什么：每个请求都新建会又慢又浪费连接"),
                                    ],
                                ),
                                topic(
                                    "rebuild_memory() → 新建 ChatMemoryBuffer + 写入安全 system",
                                    children=[
                                        topic("意思：清空旧对话，并放入 BASE_SYSTEM_PROMPT"),
                                        topic("BASE_SYSTEM_PROMPT 作用：禁止透露系统指令、拒绝越权，这是安全底线"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "零样本/少样本/COT/ToT 怎么接进代码",
                            children=[
                                topic(
                                    "PROMPT_MODES = {'zero_shot': '...', 'cot': '...', ...}",
                                    children=[
                                        topic("意思：四种策略各自是一段「前置说明文字」"),
                                        topic("换模式 = 换这段文字，不换模型、不改接口"),
                                    ],
                                ),
                                topic(
                                    "build_user_content(question, mode) → 策略 + '\\n用户任务：' + 问题",
                                    children=[
                                        topic("意思：把策略提示粘到用户问题前面，组成一条 user 消息"),
                                        topic("真正发给模型的顺序：system（安全）→ 历史 → 这条带策略的 user"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "输入净化 gate_user_input(text)",
                            children=[
                                topic(
                                    "moderation_input：一堆正则扫 ignore previous / jailbreak 等",
                                    children=[
                                        topic("意思：发现像「覆盖系统提示」的攻击句，直接判危险"),
                                        topic("返回 None 表示拦截；返回清洗后的字符串表示通过"),
                                    ],
                                ),
                                topic(
                                    "拦截后返回固定话术，不解释原因",
                                    children=[
                                        topic("意思：对外只说「无法回答」，不教对方怎么绕过"),
                                        topic("chat/stream_chat 都先过这一关，过不了就不调模型（省钱也更安全）"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "safe_messages(question, mode)",
                            children=[
                                topic(
                                    "失败返回 str（拒绝话术）",
                                    children=[
                                        topic("意思：调用方看到是字符串就直接给前端，不再 llm.chat"),
                                    ],
                                ),
                                topic(
                                    "成功：确保有 system → put(user) → return memory.get()",
                                    children=[
                                        topic("意思：返回「当前完整消息列表」，已经包含历史和本轮用户话"),
                                        topic("接着：response = llm.chat(prepared)，再 put(assistant)"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "电商文案 /product_copy",
                            children=[
                                topic(
                                    "build_product_messages(product)",
                                    children=[
                                        topic("system：金牌文案 + 四步思维链（痛点→卖点→标题正文→标签）"),
                                        topic("user：先放两个完整示例（Few-Shot），再放本轮 name/features/audience"),
                                        topic("为什么示例要完整：锁住语气和输出格式，少写废话"),
                                    ],
                                ),
                                topic(
                                    "llm.chat(messages)，且不写入普通聊天 memory",
                                    children=[
                                        topic("意思：文案是一次性任务，别污染客服多轮记忆"),
                                        topic("三个字段分别 gate_user_input：防止注入藏在「卖点」里"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "自我一致性 /self_consistency",
                            children=[
                                topic(
                                    "循环 N 次 llm.complete(不同角度 Prompt)",
                                    children=[
                                        topic("意思：同一任务换说法各生成一个候选口号"),
                                        topic("得到 candidates 列表"),
                                    ],
                                ),
                                topic(
                                    "再 llm.complete(评选 Prompt)",
                                    children=[
                                        topic("意思：让模型从候选里挑一个，只输出最终口号"),
                                        topic("num 默认 2：少打几次 API，省时间省钱"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "社交媒体 /social_plan（ToT 四次 complete）",
                            children=[
                                topic("第1次：发散 3 个截然不同切入角度（干货/情感/争议）"),
                                topic("第2次：评估爆款与难度，选出最佳方向"),
                                topic("第3次：按选定方向生成一周选题表"),
                                topic("第4次：自我批判再润色"),
                                topic(
                                    "_complete_text(prompt) = llm.complete(prompt).text",
                                    children=[
                                        topic("意思：小工具函数，专门拿完整字符串结果"),
                                        topic("四阶段就是四次独立 complete，不是一次长对话"),
                                    ],
                                ),
                            ],
                        ),
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
                                        topic("检索前：查询改写、扩展、HyDE，提高模糊问题命中率"),
                                        topic("检索中：混合检索（向量 + BM25），专名和语义都照顾"),
                                        topic("检索后：重排序 Re-ranking，精细模型二次打分，最相关的排前面"),
                                        topic("定位：效果和成本的平衡点，工业界主流"),
                                        topic("细节展开：见第 07 章；检索前见第 08 章；检索中见第 09 章"),
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
                                topic(
                                    "检索质量决定上限",
                                    children=[
                                        topic("最相关文件没召回，生成再强也没用"),
                                        topic("后面 07/08 的改写、混合检索、重排序都是在抬这个上限"),
                                    ],
                                ),
                                topic(
                                    "上下文窗口",
                                    children=[
                                        topic("答案分散在多处时可能被截断"),
                                        topic("对策：父子块、上下文压缩、子查询分别答再综合"),
                                    ],
                                ),
                                topic(
                                    "检索噪声",
                                    children=[
                                        topic("无关片段会误导模型，看起来像幻觉"),
                                        topic("对策：重排序、去重、强制“没有依据就说不知道”"),
                                    ],
                                ),
                                topic(
                                    "延迟增加",
                                    children=[
                                        topic("比纯 LLM 多一步检索，链路越长越慢"),
                                        topic("对策：异步、缓存热门问、先小模型改写再检索"),
                                    ],
                                ),
                                topic(
                                    "依赖 Embedding 和切分",
                                    children=[
                                        topic("中文和专业术语很敏感，切错/向量空间不一致会全崩"),
                                        topic("写入和查询必须同一套 Embedding"),
                                    ],
                                ),
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
                                topic("公式：cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))"),
                                topic("a、b 必须是一维向量，且维度相同，否则点积会报错"),
                                topic("可对比：我爱你 vs 我恨你、vs 大模型有很多应用场景、vs python开发"),
                                topic("结果接近 1 更像，接近 0 不太像，接近 -1 语义相反"),
                            ],
                        ),
                        topic(
                            "2.3 代码详解：调百炼拿向量再算相似度",
                            children=[
                                topic(
                                    "client = OpenAI(..., base_url='...dashscope.../compatible-mode/v1')",
                                    children=[
                                        topic("意思：假装在调 OpenAI，实际打到阿里云百炼"),
                                        topic("好处：代码和 DeepSeek/OpenAI 几乎一样，只改 base_url 和 model"),
                                    ],
                                ),
                                topic(
                                    "resp = client.embeddings.create(model='text-embedding-v3', input=texts, dimensions=1024)",
                                    children=[
                                        topic("意思：把多段文本一次性变成向量"),
                                        topic("input 可以是字符串列表：一次多句比 for 循环逐条调更省延迟"),
                                        topic("dimensions：向量长度，写入和查询必须相同"),
                                    ],
                                ),
                                topic(
                                    "vec = resp.data[i].embedding",
                                    children=[
                                        topic("意思：第 i 段文本对应的浮点数列表（如 1024 个数）"),
                                        topic("和 texts[i] 一一对应，不要搞乱下标"),
                                    ],
                                ),
                                topic(
                                    "余弦：np.dot(a,b) / (norm(a)*norm(b))",
                                    children=[
                                        topic("意思：比两个向量「方向」有多像，不比长短"),
                                        topic("≈1 很像；≈0 没关系；≈-1 语义相反"),
                                        topic("查询向量必须和文档用同一模型、同一维度，否则空间对不上"),
                                    ],
                                ),
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
                        topic(
                            "和现代句向量的差别",
                            children=[
                                topic("Word2Vec：一个词一个向量，不管上下文（bank 河岸/银行会混）"),
                                topic("现在 RAG 用的是句子/段落 Embedding，同一词在不同句里向量不同"),
                                topic("课上实操走的是后者：text-embedding-v3、bge、nomic-embed-text"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "5 课上和项目常用模型",
                    children=[
                        topic(
                            "云端：阿里云百炼 text-embedding-v3",
                            children=[
                                topic("接口：embeddings.create，维度可设 128 或 1024"),
                                topic("DashScopeEmbedding 可设 text_type=document 或 query"),
                                topic("限制：单条 ≤8192 tokens，batch size ≤10"),
                            ],
                        ),
                        topic(
                            "本地 HuggingFace：BAAI/bge-small-zh-v1.5",
                            children=[
                                topic("本仓库 semantic_search 默认走这条，中文友好"),
                                topic("首次运行会下载权重，约百 MB 级"),
                                topic("可换 bge-base-zh-v1.5，效果更好、更吃内存"),
                            ],
                        ),
                        topic(
                            "本地 Ollama：nomic-embed-text / qwen3-embedding:0.6b",
                            children=[
                                topic("适合数据不出本机"),
                                topic("LlamaIndex 用 llama-index-embeddings-ollama"),
                            ],
                        ),
                        topic(
                            "必须遵守的对照原则",
                            children=[
                                topic("写入和查询必须同一模型、同一维度，否则空间对不上"),
                                topic("换模型就要重建整个向量库，不能混着用"),
                                topic("选型可看 MTEB Leaderboard，中文优先看 C-MTEB"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "6 代码详解：项目里怎么挂 Embedding",
                    children=[
                        topic(
                            "Settings.embed_model = DashScopeEmbedding(...) 或 HuggingFaceEmbedding(...)",
                            children=[
                                topic("意思：告诉 LlamaIndex「以后所有向量化都用这个模型」"),
                                topic("DashScope：云端千问，要 api_key；text_type='document' 表示按文档侧编码"),
                                topic("HuggingFace：本地下载 BAAI/bge-small-zh-v1.5，首次会拉权重"),
                                topic("为什么设全局：分块语义切分、写入、检索都会自动用同一模型，避免空间不一致"),
                            ],
                        ),
                        topic(
                            "写入 vs 查询",
                            children=[
                                topic("有的云端模型区分 document / query 两种编码，别混用"),
                                topic("本仓库默认本地 bge：读写都走同一个 HuggingFaceEmbedding，简单不容易错"),
                                topic("换模型必须重建向量库，旧向量和新模型不在同一空间"),
                            ],
                        ),
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
                                topic("课上示例：10000 条、每条 128 维 float32 矩阵"),
                                topic(
                                    "代码详解 对照 918.py IndexFlat",
                                    children=[
                                        topic(
                                            "vectors = np.random.random((10000, 128)).astype('float32')",
                                            children=[
                                                topic("意思：造 10000 条假向量，每条 128 维，当作「库里的文档向量」"),
                                                topic("astype('float32')：FAISS 只吃 float32，float64 会报错或行为怪异"),
                                            ],
                                        ),
                                        topic(
                                            "index = faiss.IndexFlatL2(128)",
                                            children=[
                                                topic("意思：建一个「暴力精确搜」索引，距离用欧氏距离 L2"),
                                                topic("128 必须等于向量列数，对不上会直接报错"),
                                            ],
                                        ),
                                        topic(
                                            "index.add(vectors)",
                                            children=[
                                                topic("意思：把全部向量装进索引"),
                                                topic("装完看 index.ntotal，应等于 10000"),
                                            ],
                                        ),
                                        topic(
                                            "query 形状必须是 (1, 128)",
                                            children=[
                                                topic("意思：一次查询也可以多条，所以第一维是「几条查询」"),
                                                topic("传一维 (128,) 会维度错误；要用 query.reshape(1, -1)"),
                                            ],
                                        ),
                                        topic(
                                            "D, I = index.search(query, k=5)",
                                            children=[
                                                topic("D：距离矩阵，D[0][i] 越小（L2）越像"),
                                                topic("I：下标矩阵，I[0][i] 是第 i 名在原 vectors 里的行号"),
                                                topic("拿原文：用下标去你自己保存的 documents 列表里取"),
                                            ],
                                        ),
                                        topic("局限：Flat 不能单独改一条，要更新通常整库重建"),
                                    ],
                                ),
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
                                topic(
                                    "代码详解 对照 918.py IVF",
                                    children=[
                                        topic(
                                            "quantizer = faiss.IndexFlatL2(dimension)",
                                            children=[
                                                topic("意思：底层用精确索引当「量尺」，给 IVF 算哪个簇最近"),
                                            ],
                                        ),
                                        topic(
                                            "index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)",
                                            children=[
                                                topic("意思：把空间切成 100 个簇（倒排桶）"),
                                                topic("nlist 常取约 sqrt(N)；太小每桶太大，太大要扫的桶变多"),
                                            ],
                                        ),
                                        topic(
                                            "index.train(vectors) 必须先做",
                                            children=[
                                                topic("意思：用 k-means 找到每个簇的中心"),
                                                topic("不 train 就 add/search 会报错，这是 IVF 和 Flat 最大差别"),
                                            ],
                                        ),
                                        topic(
                                            "index.add(vectors) → index.nprobe = 10 → search",
                                            children=[
                                                topic("add：把向量丢进最近的簇"),
                                                topic("nprobe：查询时搜几个最近簇；越大越准越慢，=nlist 就接近暴力搜"),
                                                topic("search 返回值仍是 D 距离、I 下标，用法和 Flat 一样"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic("nlist：聚类中心数，通常取 sqrt(N)。太小每簇太大；太大要查的簇变多"),
                                topic("nprobe：查几个簇。1 最快最糙；等于 nlist 就变精确搜"),
                                topic("正向索引：文档→词，搜苹果要扫 100 万篇，O(N)"),
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
                                topic(
                                    "代码详解 对照 918.py（Chroma 四步）",
                                    children=[
                                        topic(
                                            "client = chromadb.PersistentClient(path='./chroma_data')",
                                            children=[
                                                topic("意思：打开/创建一个落盘的向量库目录"),
                                                topic("和 Client() 区别：进程关掉数据还在"),
                                            ],
                                        ),
                                        topic(
                                            "collection = client.get_or_create_collection('kaoqin')",
                                            children=[
                                                topic("意思：有同名集合就打开，没有就新建（入门最省事）"),
                                                topic("集合 ≈ 关系库里的一张表"),
                                            ],
                                        ),
                                        topic(
                                            "collection.add(ids=..., documents=..., metadatas=...)",
                                            children=[
                                                topic("意思：写入原文；没传 embeddings 时库会自动向量化"),
                                                topic("三个 list 必须等长：第 i 个 id 对应第 i 段文档"),
                                                topic("只传 embeddings：跳过嵌入，适合你已经用千问算好向量"),
                                                topic("同一 id 再 add 会 DuplicateID → 先 delete(ids=...)"),
                                            ],
                                        ),
                                        topic(
                                            "res = collection.query(query_texts=['年假几天'], n_results=3)",
                                            children=[
                                                topic("意思：把问句向量化，取最像的 3 条"),
                                                topic("看结果：res['documents'][0] 是文本列表"),
                                                topic("res['distances'][0] 是距离（越小越像，具体含义看 hnsw:space）"),
                                                topic("res['metadatas'][0] 可拿来源、分类等"),
                                            ],
                                        ),
                                        topic(
                                            "where={'category': '年假'}",
                                            children=[
                                                topic("意思：先按元数据硬过滤，再在子集里做向量搜"),
                                                topic("适合：只要某类制度、某年通知，减少噪声"),
                                            ],
                                        ),
                                    ],
                                ),
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
                        topic(
                            "完整落地已迁到 semantic_search，代码详解见第 06 章",
                            children=[
                                topic("启动：python -m semantic_search → http://127.0.0.1:8001/"),
                                topic("只检索：GET /search?q=...&k=3"),
                                topic("检索+生成：GET /query?q=..."),
                            ],
                        ),
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
                                topic("向量化后写入向量库，不要只把向量扔内存里"),
                                topic("必须建立 embedding ↔ chunk 原文的映射，检索到向量才能拿出文本"),
                                topic("再记下 metadata：来源文件、页码、切分方式，方便引用和过滤"),
                                topic("本仓库落盘目录：semantic_search/chroma_db"),
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
                                topic(
                                    "1.2 核心概念速览",
                                    children=[
                                        topic("Document：一篇原始文档，带 metadata（来源、文件名）"),
                                        topic("Node：切出来的块，检索的基本单位"),
                                        topic("Index：把 Node 编成可检索结构，课上主要是向量索引"),
                                        topic("Retriever：只负责找回 Node，不生成答案"),
                                        topic("QueryEngine：检索 + 拼 Prompt + 调用 LLM，一次问答"),
                                        topic("ChatEngine：QueryEngine + Memory，多轮对话"),
                                    ],
                                ),
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
                        topic(
                            "6 对照本仓库 semantic_search 怎么用",
                            note="讲义流程已接到 FastAPI + 前端",
                            children=[
                                topic("Indexing：前端上传 /upload 或 POST /ingest → data 目录 → 分块入库"),
                                topic("分块可选：sentence（推荐）/ token / semantic"),
                                topic("Embedding：默认本地 bge-small-zh；有千问 Key 可改 dashscope"),
                                topic("Search：前端「语义搜索」或 GET/POST /search"),
                                topic("Generate：前端「一次性问答」/query、「多轮问答」/chat"),
                                topic("持久化目录：semantic_search/chroma_db"),
                                topic("启动：python chroma文档管理/run.py → http://127.0.0.1:8003/"),
                            ],
                        ),
                        topic(
                            "7 代码详解 engine.py / main.py（chroma文档管理）",
                            note="对应 chroma文档管理/semantic_search/。每条：代码 → 它在流水线哪一步 → 得到什么。",
                            children=[
                                topic(
                                    "启动 lifespan",
                                    children=[
                                        topic(
                                            "SemanticSearchEngine()",
                                            children=[
                                                topic("意思：一次性挂好 Embedding、LLM、Chroma、空/旧索引"),
                                                topic("缺 API Key 时引擎可为 None，页面能开，/query 会 503"),
                                            ],
                                        ),
                                        topic(
                                            "seed_if_empty()",
                                            children=[
                                                topic("意思：库是空的才灌示例文档 + 扫描 data 目录"),
                                                topic("为什么：第一次启动就能搜，不用手工入库"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "入库：文件 → 块 → 向量",
                                    children=[
                                        topic(
                                            "SimpleDirectoryReader(...).load_data()",
                                            children=[
                                                topic("意思：把 PDF/TXT/MD 等读成 Document 列表"),
                                                topic("每个 Document 带 text + metadata（文件名等）"),
                                            ],
                                        ),
                                        topic(
                                            "clean_empty_text(docs)",
                                            children=[
                                                topic("意思：丢掉空内容，避免后面 embedding 报错"),
                                            ],
                                        ),
                                        topic(
                                            "splitter.get_nodes_from_documents(docs)",
                                            children=[
                                                topic("意思：切成 Node（检索的基本单位=chunk）"),
                                                topic("sentence/token/semantic 三种切法由 _splitter(mode) 决定"),
                                            ],
                                        ),
                                        topic(
                                            "index.insert_nodes(nodes)",
                                            children=[
                                                topic("意思：对每个 Node 调 embed_model 得向量，再写入 Chroma"),
                                                topic("之后要 _reset_chat_engines()：知识变了，旧多轮引擎不能继续用"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "三种分块器（构造时在说什么）",
                                    children=[
                                        topic(
                                            "SentenceSplitter(chunk_size, chunk_overlap, ...)",
                                            children=[
                                                topic("意思：尽量按句子边界凑满约 chunk_size 个 token"),
                                                topic("overlap：下一块带上上块尾巴，防止关键句被切断"),
                                            ],
                                        ),
                                        topic(
                                            "TokenTextSplitter(...)",
                                            children=[
                                                topic("意思：严格按 token 数切，控制上下文更硬"),
                                            ],
                                        ),
                                        topic(
                                            "SemanticSplitterNodeParser(buffer_size=1, breakpoint=95, ...)",
                                            children=[
                                                topic("意思：算相邻句向量相似度，主题一变就切开"),
                                                topic("更慢但语义更整；中文要自定义分句函数"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "只检索 search（不调大模型）",
                                    children=[
                                        topic(
                                            "retriever = index.as_retriever(similarity_top_k=k)",
                                            children=[
                                                topic("意思：只要「找片段」的工具，不做生成"),
                                            ],
                                        ),
                                        topic(
                                            "results = retriever.retrieve(query)",
                                            children=[
                                                topic("意思：返回 NodeWithScore 列表"),
                                                topic("item.node.get_content() → 原文；item.score → 相似度"),
                                                topic("对应接口：GET/POST /search"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "一次性问答 query",
                                    children=[
                                        topic(
                                            "engine = index.as_query_engine(similarity_top_k=k)",
                                            children=[
                                                topic("意思：检索 + 拼 Prompt + 调 LLM，一条龙"),
                                            ],
                                        ),
                                        topic(
                                            "response = engine.query(question)",
                                            children=[
                                                topic("str(response) → 给用户的答案文字"),
                                                topic("response.source_nodes → 引用了哪些片段（可展示来源）"),
                                                topic("对应接口：GET/POST /query"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "多轮问答 chat",
                                    children=[
                                        topic(
                                            "as_chat_engine(chat_mode='condense_plus_context', memory=..., ...)",
                                            children=[
                                                topic("condense_plus_context 意思：先把「结合上文的问题」改写成独立问句，再检索"),
                                                topic("为什么：用户说「那扣多少」时，检索要用改写后的完整问题"),
                                            ],
                                        ),
                                        topic(
                                            "memory 按 session_id 复用",
                                            children=[
                                                topic("意思：同一浏览器会话共用一块记忆"),
                                                topic("换 session_id = 新对话；对应 POST /chat"),
                                            ],
                                        ),
                                    ],
                                ),
                                topic(
                                    "重启后如何找回索引",
                                    children=[
                                        topic(
                                            "collection.count() > 0 → VectorStoreIndex.from_vector_store(...)",
                                            children=[
                                                topic("意思：Chroma 里已有向量，挂上去就能搜，不必重切分"),
                                            ],
                                        ),
                                        topic(
                                            "空库 → VectorStoreIndex(nodes=[], storage_context=...)",
                                            children=[
                                                topic("意思：先占个空索引，以后 insert_nodes 再往里填"),
                                            ],
                                        ),
                                        topic("铁律：Settings.embed_model 必须和建库时同一个"),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        topic(
            "07 Advanced RAG（高级RAG）",
            note=(
                "飞书：Advance RAG。答辩重点：Native→Advanced 差在哪；"
                "检索前/中/后各治什么病；HyDE/扩展/分解/重排怎么选。"
            ),
            children=[
                topic(
                    "〇、答辩开场 60 秒说清",
                    children=[
                        topic(
                            "一句话定义",
                            children=[
                                topic("Advanced RAG = 在 Native RAG 的「检索→生成」两端，对查询、召回、精排、上下文使用做系统优化"),
                                topic("不是换一个更强的 LLM，而是把「送进模型的原材料」做对"),
                            ],
                        ),
                        topic(
                            "和 Native 的对比（老师最爱问）",
                            children=[
                                topic("Native：用户原句 → 向量 Top-K → 直接塞 Prompt → 生成"),
                                topic("Advanced：先改查询/多路召回 → 再重排压缩 → 再带约束生成"),
                                topic("Native 像小学生翻书找关键词；Advanced 像会改题意、会对照目录、会划重点的学生"),
                                topic("代价：延迟↑、费用↑、链路更复杂；收益：召回↑、噪声↓、幻觉↓"),
                            ],
                        ),
                        topic(
                            "闭环四问（按时间线背）",
                            children=[
                                topic("查什么（Pre）：改写 / 扩展 / HyDE / 分解 / 分块与元数据"),
                                topic("去哪查（Retrieval）：混合检索、多路召回、路由不同索引"),
                                topic("查得准（Post 前半）：重排序，把最相关的顶到前面"),
                                topic("怎么用（Post 后半）：压缩、动态 Top-K、引用约束 Prompt"),
                            ],
                        ),
                        topic(
                            "工业界优先三件套（性价比排序）",
                            children=[
                                topic("① 查询改写或 HyDE：治「问法和文档不像」"),
                                topic("② 混合检索（向量+BM25）：治「专名/编号搜不到」"),
                                topic("③ 重排序 rerank：治「召回有了但前几名不相关」"),
                                topic("先别一上来上 GraphRAG / Agent，Native 没稳先别叠高级模块"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "一、检索前优化（Pre-retrieval）",
                    note="目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章；检索中见第 09 章。",
                    children=[
                        topic(
                            "查询重写 Query Rewriting",
                            children=[
                                topic("做什么：口语/指代不明 → 检索友好、术语齐全的问句"),
                                topic("例子：「上次那个产品的安全规范」→「某某产品 最新 安全规范 文档」"),
                                topic("治的病：指代、口语、缺关键词导致向量飘"),
                                topic("风险：改写过头偏离原意 → 可 include_original 保留原句一起搜"),
                                topic("口述口诀：先把题读懂，再去翻书"),
                            ],
                        ),
                        topic(
                            "查询扩展 Query Expansion / Multi-Query",
                            children=[
                                topic("做什么：同一意图生成多个近义/不同句式变体，并行检索再合并"),
                                topic("治的病：用户用词不专业、同义不同词、召回偏低"),
                                topic("合并常用 RRF，避免某一路分数尺度不同抢排名"),
                                topic("和改写区别：改写≈改成更好的一句；扩展≈变成多句一起查"),
                            ],
                        ),
                        topic(
                            "HyDE 假设文档检索",
                            children=[
                                topic("做什么：先让 LLM 写一篇「假想答案」，用这篇去向量库搜"),
                                topic("为什么有效：知识库存的是「答案体」文档，假想答案和它更像，短问句不像"),
                                topic("适合：问句极短、用户表述和文档风格差很大"),
                                topic("不适合：事实极严、模型瞎编会带偏检索（务必 include_original）"),
                                topic("代价：多一次 LLM，延迟和费用都上去"),
                                topic("口述对比：改写是改问题；HyDE 是先编一份答案再去找真答案"),
                            ],
                        ),
                        topic(
                            "子查询分解 Decomposition",
                            children=[
                                topic("做什么：复杂题拆成多个原子子问题，分别检索再综合"),
                                topic("例子：比较 A/B 2023 营收增长 → 分别查营收 → 算增长率 → 再对比"),
                                topic("治的病：一次检索塞不下的多跳/比较题"),
                                topic("和扩展区别：扩展是近义变体；分解是不同侧面的子问题"),
                            ],
                        ),
                        topic(
                            "文档侧（离线也算检索前）",
                            children=[
                                topic("分块：句子/语义/父子块，决定「能不能被命中」和「命中后有没有上下文」"),
                                topic("文档增强：摘要、关键词、假设问题一并入库，提高可检索性"),
                                topic("元数据：时间/分类/来源，给过滤和引用用"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "二、检索中优化（Retrieval）",
                    note=(
                        "飞书：03-检索中优化（Retrieval）。目标：提升召回率与相关性。"
                        "细节专训见第 09 章。"
                    ),
                    children=[
                        topic(
                            "先搞清：检索 vs 召回；召回率 vs 精确率",
                            children=[
                                topic("检索召回 = 从海量知识库里，把和用户问题相关的内容找出来"),
                                topic("检索：拿着问题去向量库/文档库搜索"),
                                topic("召回：把匹配度高的片段捞回来"),
                                topic(
                                    "召回率 Recall",
                                    children=[
                                        topic("该找到的相关内容，有没有全部找出来"),
                                        topic("高：相关的基本都捞到，不漏；低：很多相关文档没搜到"),
                                    ],
                                ),
                                topic(
                                    "精确率 Precision",
                                    children=[
                                        topic("召回来的内容里，有多少真有用、不跑偏"),
                                        topic("高：捞回来都很相关；低：一堆噪音"),
                                    ],
                                ),
                                topic("检索中优化主攻：先抬召回率（别漏），再靠融合/后重排抬精确率"),
                            ],
                        ),
                        topic(
                            "混合检索 Hybrid Search（同库多算法）",
                            children=[
                                topic("问题：单一检索方式总有盲区"),
                                topic("公式一句话：混合检索 = 稠密向量 + 稀疏向量 → 结果融合 → 取长补短"),
                                topic(
                                    "稠密 vs 稀疏（口述）",
                                    children=[
                                        topic("稠密：几乎每维都有值，「按意思翻译」；语义/同义强（笔记本≈电脑）"),
                                        topic("稀疏：多数为 0，「按关键词翻译」；专名/编号/错误码强"),
                                        topic("同一份文档两种翻译官 → 两套排名互补"),
                                    ],
                                ),
                                topic(
                                    "场景口诀（登录超时）",
                                    children=[
                                        topic("只在「产品文档」这一个数据源里搜"),
                                        topic("向量：找到 session过期 / 身份验证失败 等同义"),
                                        topic("BM25：精确命中「登录超时」字眼"),
                                        topic("再用 RRF 等融合两路排名"),
                                    ],
                                ),
                                topic("代码落点：标准 RAG 第 4 步「检索召回」——做一个更强更准的召回"),
                                topic("LlamaIndex：同一份 nodes → vector_retriever + BM25Retriever → QueryFusionRetriever"),
                                topic("中文坑：BM25 默认英文分词无效，必须 tokenizer=jieba（或 language=chinese 组合）"),
                            ],
                        ),
                        topic(
                            "RRF 倒数排名融合（常考）",
                            children=[
                                topic("全称 Reciprocal Rank Fusion"),
                                topic("公式：score(doc) = Σ 1/(k + rank_i)，k 常取 60"),
                                topic("k 的作用：缓和「第一名」过度碾压，避免排名靠前波动过大"),
                                topic(
                                    "算例（讲义）",
                                    children=[
                                        topic("文档A：稠密第2 + 稀疏第5 → 1/62 + 1/65 ≈ 0.0315"),
                                        topic("文档B：稠密第1 + 稀疏第20 → 1/61 + 1/80 ≈ 0.0289"),
                                        topic("结论：A > B——单路第一不如两路都靠前均衡"),
                                    ],
                                ),
                                topic("关键优点：不要求各路原始分数同一量纲（cosine 0~1 vs BM25 0~∞）"),
                                topic("LlamaIndex：mode='reciprocal_rerank'；加权归一化则用 relative_score"),
                            ],
                        ),
                        topic(
                            "多路召回 Multi-channel（多源多通道）",
                            children=[
                                topic("问题：单一索引/单一字段覆盖不全"),
                                topic("定义：多个独立检索通道 → 各自召回 → 去重融合 → 扩大覆盖面"),
                                topic("一句话：多条赛道先各自捞一批候选，保召回率、少漏"),
                                topic(
                                    "四步流程",
                                    children=[
                                        topic("① 准备多路原始文档（技术库/FAQ/社区/工单…）"),
                                        topic("② 每路按「要解决的问题」选索引：语义用稠密，术语用 BM25"),
                                        topic("③ 同一用户问题各路出 Top-K"),
                                        topic("④ 融合得最终 Top-N：RRF（首选）/ 归一化加权 / 轮询 Round-Robin"),
                                    ],
                                ),
                                topic(
                                    "选型注意",
                                    children=[
                                        topic("不是看文档长短，而是看这一路要治什么病"),
                                        topic("FAQ 短、关键词强 → 常配 BM25；长文/口语 → 稠密向量"),
                                        topic("实践中一路里还可再套混合检索（见嵌套架构）"),
                                    ],
                                ),
                                topic("代码：tech/faq/community 三路 Retriever + QueryFusionRetriever（可 relative_score 加权）"),
                                topic("同样落在 RAG 第 4 步检索召回"),
                            ],
                        ),
                        topic(
                            "混合检索 vs 多路召回（别混！）",
                            children=[
                                topic("混合：横向不变、纵向加深——同一数据源，两种算法互补"),
                                topic("多路：纵向可单算法、横向扩源——多个数据源一起搜"),
                                topic(
                                    "工业嵌套（常一起用）",
                                    children=[
                                        topic("外层多路召回：产品文档 / 工单 / 规范 / FAQ"),
                                        topic("内层每路混合检索：向量 + BM25 + RRF"),
                                        topic("最后融合排序 + 去重"),
                                    ],
                                ),
                                topic("口诀：多路=横向扩数据源；混合=纵向抬单源质量；不是互斥选项"),
                            ],
                        ),
                        topic(
                            "进阶略知：SPLADE / ColBERT",
                            children=[
                                topic("SPLADE：学出来的稀疏向量，比纯 BM25 多一点语义"),
                                topic("ColBERT：token 级交互（MaxSim），更细但更吃存储算力"),
                                topic("答辩：知道「单向量会丢细粒度」即可"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "三、检索后优化（Post-retrieval）",
                    note="目标：提高精排质量与生成可用性——捞上来的材料怎么用。召回靠第 09 章抬上来，这里负责精排与怎么喂给模型。",
                    children=[
                        topic(
                            "重排序 Re-ranking（性价比之王）",
                            children=[
                                topic("召回：双塔/向量，快，但 query-doc 没深度交互"),
                                topic("精排：交叉编码器，query+doc 一起进模型打分，慢但准"),
                                topic("标准流程：召回 Top-20~50 → rerank → 只留 Top-3/5 给 LLM"),
                                topic("常用：bge-reranker、Cohere Rerank；也可用 LLM 当裁判（更贵）"),
                                topic("口述口诀：先广撒网，再精挑细选"),
                            ],
                        ),
                        topic(
                            "上下文压缩 / 去重 / 动态 Top-K",
                            children=[
                                topic("压缩：块里只有一两句有用，抽句段，别整块硬塞"),
                                topic("去重：重复块、过期块、低分块丢掉"),
                                topic("动态 K：高分很少就少送，别为了凑满 5 条硬塞噪声"),
                            ],
                        ),
                        topic(
                            "生成侧约束",
                            children=[
                                topic("Prompt：仅根据下列资料回答；没有依据就说不知道"),
                                topic("引用：资料编号，答案里标注来源，抑制瞎编"),
                                topic("这是「最后一道闸」，检索错了它救不了 100%，但能少胡说八道"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "四、进阶范式对比（别混）",
                    children=[
                        topic(
                            "Self-RAG",
                            children=[
                                topic("模型自己决定：要不要检索、检索结果够不够、要不要再查"),
                                topic("治的病：过度检索（闲聊也查）和检索不足"),
                            ],
                        ),
                        topic(
                            "Corrective RAG（CRAG）",
                            children=[
                                topic("先评估检索质量：相关 / 模糊 / 不相关"),
                                topic("差则纠正：换查询或转外部网页搜索，再生成"),
                                topic("治的病：知识库覆盖不全、内部库答不了的新资讯"),
                            ],
                        ),
                        topic(
                            "RAG-Fusion",
                            children=[
                                topic("= Multi-Query + 多路检索 + RRF 融合"),
                                topic("重点在「融排名」，不是融原始分数"),
                            ],
                        ),
                        topic(
                            "Adaptive / Graph / Agentic",
                            children=[
                                topic("Adaptive：按难度动态选策略深度"),
                                topic("GraphRAG：实体关系，适合多跳与全局摘要"),
                                topic("Agentic：Agent 规划检索与工具，最灵活也最难控"),
                            ],
                        ),
                        topic(
                            "一张对比表（口述用）",
                            children=[
                                topic("Self-RAG：管「查不查」"),
                                topic("Corrective：管「查错了怎么办」"),
                                topic("RAG-Fusion：管「多问法怎么合成一张榜」"),
                                topic("Rerank：管「榜上谁该排第一」"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "五、排障决策树（老师问「效果不好怎么办」）",
                    children=[
                        topic("① Native 不稳：先查 Embedding 是否一致、分块是否切断、Top-K 是否乱"),
                        topic("② 问句和文档不像：加查询改写或 HyDE"),
                        topic("③ 专名/编号搜不到：加 BM25 混合检索"),
                        topic("④ 相关材料在后面几名：加 rerank"),
                        topic("⑤ 材料对但答案飘：压 Prompt、加引用、压缩上下文"),
                        topic("⑥ 比较/多跳题：子查询分解"),
                        topic("⑦ 本仓库现状：仍是 Native；最值得先加改写或 bge-reranker"),
                    ],
                ),
                topic(
                    "六、和本仓库 / 第 08、09 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：把「检索前」拆开练：策略选择 + LlamaIndex 落地"),
                        topic("第 09 章：把「检索中」拆开练：混合检索 / 多路召回 / RRF + 代码落点"),
                        topic("chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块"),
                    ],
                ),
            ],
        ),
        topic(
            "08 检索前优化（Pre-retrieval）",
            note="每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。",
            children=[
                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("查询侧：清洗 → 澄清 → 重写 / 扩展 / HyDE / Step-Back / 分解"),
                        topic("文档侧（离线）：分块 → 元数据 → 增强 → 多表示 / 路由规则"),
                        topic("原则：先判断病症，再选一种方法；不要一次全开"),
                    ],
                ),
                topic(
                    "方法1：查询文本清洗",
                    children=[
                        topic("适用：问题里废话多、口语多、术语不统一"),
                        topic(
                            "输入",
                            children=[
                                topic("原始用户问题字符串"),
                                topic("可选：公司术语表（俚语→标准词）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 去口语：删「帮我看看」「那个」「嗯啊」等无信息词"),
                                topic("Step2 去标点噪音：多余空格、表情、重复符号"),
                                topic("Step3 术语标准化：查表替换（电脑→笔记本电脑；年假→带薪年休假）"),
                                topic("Step4 实体抽出：产品名、日期、工号单独列出（可给 BM25 用）"),
                                topic("Step5 得到「干净查询」再进入改写或直接 embedding"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("clean_query：清洗后的问句"),
                                topic("entities：抽出的关键词列表（可选）"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("输入：嗯那个帮我看看请假咋扣钱啊???"),
                                topic("Step1-2 后：请假咋扣钱"),
                                topic("Step3 后：请假 如何 扣款"),
                                topic("entities：['请假','扣款']"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法2：澄清反问",
                    children=[
                        topic("适用：缺实体、多意图、指代不明（上次那个、这个）"),
                        topic(
                            "输入",
                            children=[
                                topic("原始问题 + 可选多轮历史"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 判断是否模糊：缺类型？缺时间？有指代？多意图？"),
                                topic("Step2 若清晰：跳过，进入重写/检索"),
                                topic("Step3 若模糊：生成 1 个澄清问题返回前端，本轮先不检索或只轻量搜"),
                                topic("Step4 用户补充后，拼成「完整问题」= 原问题 + 用户选择"),
                                topic("Step5 用完整问题再走清洗/重写/检索"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("分支A：clarify_question（反问文案）"),
                                topic("分支B：resolved_query（澄清后的完整查询）"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("输入：请假扣钱吗"),
                                topic("Step1：缺假期类型 → 模糊"),
                                topic("Step3 反问：请问是事假、病假还是年假？"),
                                topic("用户答：事假 → resolved_query=事假是否扣钱及扣款规则"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法3：查询重写 Query Rewriting",
                    children=[
                        topic("适用：口语、指代、缺关键词，但意图基本单一"),
                        topic(
                            "输入",
                            children=[
                                topic("clean_query（最好先清洗）"),
                                topic("可选：对话历史（用来解析「那个」「上次」）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 准备改写 Prompt：角色=检索改写助手；只输出改写句；不解释"),
                                topic("Step2 约束：补全实体、保留原意、可加同义术语、不要编造不存在的产品名"),
                                topic("Step3 调 LLM（低温 0~0.3）得到 rewritten_query"),
                                topic("Step4 用 rewritten_query 做 embedding"),
                                topic("Step5（推荐）原句也 embedding，两路检索结果合并，防改歪"),
                                topic("Step6 合并后的片段再交给生成"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("rewritten_query：检索用问句"),
                                topic("可选：retrieval_queries = [原句, 改写句]"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("输入：上次那个产品的安全规范更新了吗"),
                                topic("历史里「那个产品」= 智能手表 X1"),
                                topic("改写：智能手表X1 安全规范 是否更新 最新版本"),
                                topic("操作：改写句检索 + 原句检索 → 合并 Top 片段 → 生成"),
                            ],
                        ),
                        topic(
                            "LlamaIndex 落点",
                            children=[
                                topic("自定义 BaseQueryTransform._run 里调 LLM"),
                                topic("或 TransformQueryEngine(base_engine, transform)"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法4：查询扩展 Multi-Query",
                    children=[
                        topic("适用：用词不准、同义多、怕漏召回"),
                        topic(
                            "输入",
                            children=[
                                topic("一条核心问题（可已清洗/改写）"),
                                topic("参数 N：变体个数，常用 3~5"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 Prompt：生成 N 个检索变体，覆盖同义词、不同句式、上下位词；每行一个"),
                                topic("Step2 解析 LLM 输出为列表 variants[1..N]"),
                                topic("Step3 对每个 variant 分别向量检索，各取 Top-K"),
                                topic("Step4 融合：RRF（按排名加分）或去重保留最高分"),
                                topic("Step5 取融合后 Top-M 作为最终检索结果"),
                                topic("Step6 再进入生成或重排"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("variants：N 条查询字符串"),
                                topic("fused_nodes：融合后的文档块列表"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("输入：请假怎么扣钱"),
                                topic("变体1：事假扣款规则"),
                                topic("变体2：病假是否带薪"),
                                topic("变体3：考勤制度 旷工 罚款"),
                                topic("变体4：年假提前离职如何折算"),
                                topic("四路检索 → RRF 合并 → 把事假/考勤相关块顶上来"),
                            ],
                        ),
                        topic(
                            "LlamaIndex 落点",
                            children=[
                                topic("QueryFusionRetriever(..., num_queries=4, mode='reciprocal_rerank')"),
                            ],
                        ),
                        topic("和重写区别：重写≈改成更好的一句；扩展≈变成多句一起查"),
                    ],
                ),
                topic(
                    "方法5：HyDE 假设文档检索",
                    children=[
                        topic("适用：问句很短，或用户说法和文档风格差很大"),
                        topic(
                            "输入",
                            children=[
                                topic("用户原问题"),
                                topic("同一套 Embedding 模型（必须与建库一致）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 Prompt：请写一段「可能回答该问题」的文档片段，用说明文/制度口吻，不要对话"),
                                topic("Step2 LLM 生成 hypo_doc（假想答案文档）"),
                                topic("Step3 对 hypo_doc 做 embedding → hypo_vec"),
                                topic("Step4 用 hypo_vec 在向量库 search Top-K → 得到真实文档块"),
                                topic("Step5（强烈建议）对原问题再 search 一路"),
                                topic("Step6 两路结果合并/去重"),
                                topic("Step7 只用真实文档块生成答案；假想文档绝不当事实引用"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("hypo_doc：仅用于检索的中间产物"),
                                topic("real_chunks：库里的真实片段"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("输入：年假怎么算"),
                                topic("Step2 假想：员工入职满一年享有带薪年假…按工龄递增…"),
                                topic("Step4 用这段去搜 → 命中《考勤手册》年假条款真文"),
                                topic("Step7 根据真文回答，并引用考勤手册"),
                            ],
                        ),
                        topic(
                            "LlamaIndex 落点",
                            children=[
                                topic("hyde = HyDEQueryTransform(include_original=True)"),
                                topic("engine = TransformQueryEngine(base_engine, hyde)"),
                                topic("include_original=True 即自动做 Step5"),
                            ],
                        ),
                        topic("翻车点：假想胡编会带偏 → 必须保留原查询；多一次 LLM 更慢更贵"),
                    ],
                ),
                topic(
                    "方法6：Step-Back 后退提问",
                    children=[
                        topic("适用：细节问题缺少背景，直接搜容易碎片化"),
                        topic(
                            "输入",
                            children=[
                                topic("具体问题 specific_q"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 Prompt：把具体问题改写成更抽象的背景/原理问题"),
                                topic("Step2 得到 step_back_q"),
                                topic("Step3 用 step_back_q 检索 → 背景材料 background_chunks"),
                                topic("Step4 用 specific_q 检索 → 细节材料 detail_chunks"),
                                topic("Step5 生成时同时塞入背景+细节，先背景后细节回答"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("step_back_q"),
                                topic("background_chunks + detail_chunks"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("specific_q：Qwen2.5-7B 上下文窗口多长"),
                                topic("step_back_q：主流大语言模型上下文窗口一般是什么量级"),
                                topic("先检索通识，再检索该型号说明，最后综合"),
                            ],
                        ),
                        topic("和 HyDE 区别：Step-Back 产出的是更宽的「问题」；HyDE 产出假想「答案文档」"),
                    ],
                ),
                topic(
                    "方法7：子查询分解 Decomposition",
                    children=[
                        topic("适用：比较题、多跳题、要多个信息点才能答"),
                        topic(
                            "输入",
                            children=[
                                topic("复杂原问题 complex_q"),
                                topic("可选：多个 QueryEngine/工具（不同库）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 LLM 分解：输出 JSON 子问题列表，每个可独立检索"),
                                topic("Step2 校验：子问题是否原子、是否覆盖原问题所需信息"),
                                topic("Step3 路由：每个子问题选哪个工具/索引（靠 tool description）"),
                                topic("Step4 并发检索（或并发问答）得到 sub_results[]"),
                                topic("Step5 综合 Prompt：根据子结果回答原问题，标注每条证据来源"),
                                topic("Step6 输出最终答案 + 引用"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("sub_questions[]"),
                                topic("sub_results[]"),
                                topic("final_answer + citations"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("complex_q：比较 A/B 公司 2023 营收增长谁快"),
                                topic("子问1：A 公司 2023 营收是多少"),
                                topic("子问2：B 公司 2023 营收是多少"),
                                topic("子问3：A、B 相对 2022 的增长率"),
                                topic("分别检索年报片段 → LLM 算增长并对比 → 给出结论"),
                            ],
                        ),
                        topic(
                            "LlamaIndex 落点",
                            children=[
                                topic("QueryEngineTool.from_defaults(..., description='查A公司财务')"),
                                topic("SubQuestionQueryEngine.from_defaults(query_engine_tools=tools)"),
                                topic("description 不准 → 路由错库（最常见失败）"),
                            ],
                        ),
                        topic("和扩展区别：扩展=同义多说法；分解=不同信息点"),
                    ],
                ),
                topic(
                    "方法8：句子分块 SentenceSplitter",
                    children=[
                        topic("适用：大多数中文文档的默认方案（离线建库）"),
                        topic(
                            "输入",
                            children=[
                                topic("Document 列表（load_data 得到）"),
                                topic("参数：chunk_size、chunk_overlap"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 按段落分隔符粗切（如多个换行）"),
                                topic("Step2 再按句子边界细切（。！？等）"),
                                topic("Step3 把句子累加，直到接近 chunk_size（按 token）"),
                                topic("Step4 输出一块；下一块带上上块末尾 overlap 句子"),
                                topic("Step5 所有块变成 Node，再 embedding 入库"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("nodes[]：每块含 text + metadata"),
                            ],
                        ),
                        topic(
                            "操作命令",
                            children=[
                                topic("splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)"),
                                topic("nodes = splitter.get_nodes_from_documents(docs)"),
                                topic("index.insert_nodes(nodes)"),
                            ],
                        ),
                        topic("调参：缺上下文 → 加大 chunk 或 overlap；检不中 → 块可能太大或要改查询"),
                    ],
                ),
                topic(
                    "方法9：语义分块 SemanticSplitter",
                    children=[
                        topic("适用：长文、主题多变，希望按语义边界切"),
                        topic(
                            "输入",
                            children=[
                                topic("长文档 + embed_model（与检索同一套）"),
                                topic("buffer_size、breakpoint_percentile_threshold"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 中文分句（自定义：按。！？和换行切）"),
                                topic("Step2 用滑动窗口组成「组合句」（buffer_size 控制前后各几句）"),
                                topic("Step3 对组合句 embedding，算相邻组合句相似度"),
                                topic("Step4 相似度下跌超过阈值（百分位）→ 在此处切开"),
                                topic("Step5 得到语义块 Node → 入库"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("按主题相对完整的块（块大小不固定）"),
                            ],
                        ),
                        topic(
                            "操作要点",
                            children=[
                                topic("SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95, ...)"),
                                topic("先 clean_empty_text；千问 embedding 注意 batch≤10"),
                                topic("更慢更贵（要算很多句向量）"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法10：父子块 Parent-Child",
                    children=[
                        topic("适用：既要检索准，又要生成时有完整上下文"),
                        topic(
                            "输入",
                            children=[
                                topic("文档 + 两级大小，如父 2048、子 512"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 HierarchicalNodeParser 切出父大块、子小块，建立父子关系"),
                                topic("Step2 只对叶子小块做 embedding，建向量索引"),
                                topic("Step3 父块原文放进 docstore（不靠向量找父块）"),
                                topic("Step4 查询时：向量检索命中小块"),
                                topic("Step5 AutoMergingRetriever：把命中的小块合并回父块（或更大上下文）"),
                                topic("Step6 把合并后的大上下文交给 LLM 生成"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("检索命中：小块；生成输入：父块/合并块"),
                            ],
                        ),
                        topic(
                            "操作要点",
                            children=[
                                topic("parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512])"),
                                topic("retriever = AutoMergingRetriever(leaf_retriever, storage_context)"),
                            ],
                        ),
                        topic("解决的矛盾：小块好中、大块好答"),
                    ],
                ),
                topic(
                    "方法11：元数据预过滤",
                    children=[
                        topic("适用：用户带时间/类别/来源限制"),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 建库时给 Node 打 metadata（category/year/source/page）"),
                                topic("Step2 查询时解析约束（只要 2024、只要年假）"),
                                topic("Step3 构造 where 条件"),
                                topic("Step4 向量检索只在过滤后的子集里做"),
                                topic("Step5 无约束则 where 为空，全库搜"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("入库：metadata={'category':'年假','year':2024}"),
                                topic("问题：2024 年年假怎么请"),
                                topic("where={'category':'年假','year':2024} → 再向量搜"),
                            ],
                        ),
                        topic("口述：先缩小书架，再找相似书"),
                    ],
                ),
                topic(
                    "方法12：意图路由",
                    children=[
                        topic("适用：多个知识库/集合，问题类型不同"),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 准备多库：制度库、FAQ 库、技术文档库"),
                                topic("Step2 为每个库写清 description（给路由用）"),
                                topic("Step3 分类：规则 / 小模型 / LLM 判断问题类型"),
                                topic("Step4 只调用对应库的 retriever/query_engine"),
                                topic("Step5 或多工具交给 SubQuestionQueryEngine 自动路由"),
                            ],
                        ),
                        topic("翻车点：description 写糊 → 路由乱；要写「查什么 / 不查什么」"),
                    ],
                ),
                topic(
                    "方法13：权限过滤",
                    children=[
                        topic("适用：多租户、按部门/角色可见"),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 文档 metadata 写入 allowed_roles / dept"),
                                topic("Step2 请求带上当前用户角色"),
                                topic("Step3 检索前 where 加上角色条件"),
                                topic("Step4 再向量搜；无权限文档根本不会进候选集"),
                            ],
                        ),
                        topic("铁律：不能先搜出敏感段再靠 Prompt「别泄露」"),
                    ],
                ),
                topic(
                    "方法14：文档增强（摘要/关键词/假设问题）",
                    children=[
                        topic("适用：正文不好搜，需要额外「入口」"),
                        topic(
                            "分步分解（离线）",
                            children=[
                                topic("Step1 对每个 chunk 调 LLM 生成：一句话摘要、关键词、2 个假设用户问题"),
                                topic("Step2 把假设问题也做成可检索向量（或与 chunk 同 id 关联）"),
                                topic("Step3 可选：摘要单独一路向量"),
                                topic("Step4 在线检索时可匹配「假设问题」或「摘要」（类似反向 HyDE）"),
                                topic("Step5 命中后仍返回原 chunk 正文给生成"),
                            ],
                        ),
                        topic("输出：更易被问句命中的索引，而不改变最终依据仍是原文"),
                    ],
                ),
                topic(
                    "方法怎么串起来（推荐顺序）",
                    children=[
                        topic(
                            "离线",
                            children=[
                                topic("加载 → 清洗空文 → 分块(8/9/10选一) → 打元数据 → 可选增强 → 同一 Embedding 入库"),
                            ],
                        ),
                        topic(
                            "在线",
                            children=[
                                topic("1 清洗（方法1）"),
                                topic("2 模糊？→ 澄清（方法2）"),
                                topic("3 复杂比较？→ 分解（方法7）"),
                                topic("4 否则三选一：重写(3) / 扩展(4) / HyDE(5)；缺背景加 Step-Back(6)"),
                                topic("5 有类别时间？→ 预过滤(11)；多库？→ 路由(12)；有权限？→(13)"),
                                topic("6 进入检索中（第 09 章混合/多路）→ 再重排生成（检索后）"),
                            ],
                        ),
                        topic(
                            "本仓库最小改法",
                            children=[
                                topic("先在 query() 前加方法1+3（清洗+重写）"),
                                topic("再试 HyDEQueryTransform(include_original=True)"),
                                topic("专名多再加混合检索；回答飘再加重排"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        topic(
            "09 检索中优化（Retrieval）",
            note=(
                "飞书：03-检索中优化（Retrieval）。每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。"
                "密码文档目标：提升召回率和相关性。"
            ),
            children=[
                topic(
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
                    "指标预习：召回率 vs 精确率",
                    children=[
                        topic(
                            "适用",
                            children=[
                                topic("开口答「效果不好」前，先分清漏了还是脏了"),
                            ],
                        ),
                        topic(
                            "输入",
                            children=[
                                topic("一次检索返回的候选列表 + 人工标注的相关集合（或抽检）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 明确相关集合：哪些 chunk 本应被找到"),
                                topic("Step2 算召回率：相关集合里有多少出现在 Top-K"),
                                topic("Step3 算精确率：Top-K 里有多少真相关"),
                                topic("Step4 漏得多 → 优先混合/多路/扩 K；脏得多 → 融合权重、后加重排"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("口述结论：当前是「召回病」还是「精确病」"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("相关文档 10 篇，Top-5 只中 2 篇 → 召回差，先扩召回手段"),
                                topic("Top-5 中了 4 篇相关但夹 1 篇无关 → 精确还行，可微调或 rerank"),
                            ],
                        ),
                        topic("翻车点：只看生成答案对不对，不区分检索阶段指标，会改错模块"),
                    ],
                ),
                topic(
                    "方法1：混合检索 Hybrid Search",
                    children=[
                        topic("适用：同一知识库里，既有口语/同义表达，又有专名、错误码、型号"),
                        topic(
                            "输入",
                            children=[
                                topic("同一份 nodes（同一分块结果）"),
                                topic("用户查询字符串"),
                                topic("稠密 Embedding 模型 + BM25（中文需分词器）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 全局 Settings.embed_model（如 DashScope text-embedding-v3）"),
                                topic("Step2 文档 → SentenceSplitter/语义分块 → nodes（两路吃同一份）"),
                                topic("Step3 稠密路：VectorStoreIndex(nodes).as_retriever(top_k)"),
                                topic("Step4 稀疏路：BM25Retriever.from_defaults(nodes, tokenizer=jieba)"),
                                topic("Step5 QueryFusionRetriever([vector, bm25], mode=reciprocal_rerank)"),
                                topic("Step6 取融合后 Top-N → 交给 RetrieverQueryEngine / LLM"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("融合后的 NodeWithScore 列表（语义命中 + 关键词命中都可能进榜）"),
                            ],
                        ),
                        topic(
                            "完整例子（登录超时）",
                            children=[
                                topic("单源：只搜产品文档"),
                                topic("向量捞到「session 过期」「身份验证失败」"),
                                topic("BM25 捞到正文含「登录超时」的段落"),
                                topic("RRF 后两者都可能进入最终 Top-N"),
                            ],
                        ),
                        topic(
                            "讲义代码逐行（混合检索）",
                            children=[
                                topic(
                                    "Settings.embed_model = DashScopeEmbedding(text-embedding-v3)",
                                    children=[
                                        topic("意思：全局指定稠密向量模型，后面建索引会自动用它"),
                                        topic("为什么：查询和文档必须同一套 Embedding，否则两路向量不在同一空间"),
                                    ],
                                ),
                                topic(
                                    "docs = [Document(text=t) for t in documents]",
                                    children=[
                                        topic("意思：把纯字符串包成 LlamaIndex 的 Document"),
                                        topic("为什么：分块器和索引只认 Document/Node，不认裸字符串"),
                                    ],
                                ),
                                topic(
                                    "splitter = SentenceSplitter(chunk_size=200, chunk_overlap=20)",
                                    children=[
                                        topic("意思：按句子边界切块，每块约 200 token，相邻块重叠 20"),
                                        topic("为什么：两路检索必须吃同一份 nodes，切一次就够"),
                                    ],
                                ),
                                topic(
                                    "nodes = splitter.get_nodes_from_documents(docs)",
                                    children=[
                                        topic("意思：得到检索的基本单位 Node 列表"),
                                    ],
                                ),
                                topic(
                                    "index = VectorStoreIndex(nodes)",
                                    children=[
                                        topic("意思：对每个 Node 调 embed_model，建成稠密向量索引"),
                                    ],
                                ),
                                topic(
                                    "vector_retriever = index.as_retriever(similarity_top_k=5)",
                                    children=[
                                        topic("意思：语义路只返回最像的 5 条，不做生成"),
                                        topic("为什么：top_k 是「这一路的候选窗口」，后面还要和 BM25 融合"),
                                    ],
                                ),
                                topic(
                                    "bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5, tokenizer=...)",
                                    children=[
                                        topic("意思：用同一批 nodes 建关键词检索器，也取 5 条"),
                                        topic("tokenizer=lambda text: list(jieba.cut(text))"),
                                        topic("意思：先用 jieba 把中文切成词，BM25 才能按词频打分"),
                                        topic("为什么：默认英文分词按空格切，中文整句会变成一个 token，BM25 失效"),
                                    ],
                                ),
                                topic(
                                    "QueryFusionRetriever(retrievers=[vector, bm25], mode='reciprocal_rerank')",
                                    children=[
                                        topic("意思：同一个问题同时问两路，再用 RRF 按名次合成一张榜"),
                                        topic("为什么：cosine 分和 BM25 分不能直接相加，只比排名更稳"),
                                    ],
                                ),
                                topic(
                                    "RetrieverQueryEngine.from_args(retriever=...)",
                                    children=[
                                        topic("意思：融合后的片段再拼进 Prompt，交给 LLM 生成"),
                                        topic("为什么：混合检索只替换第 4 步召回，第 5 步生成不变"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "翻车点",
                            children=[
                                topic("中文不用 jieba：BM25 把整句当一个词，等于废掉"),
                                topic("直接加原始分数：cosine 与 BM25 量纲不同，必须 RRF 或先归一化"),
                                topic("K 太小：两路都没机会进融合窗口"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法2：RRF 融合公式深挖",
                    children=[
                        topic("适用：任意多路检索结果要合成一张公平榜单时"),
                        topic(
                            "输入",
                            children=[
                                topic("各路已排序的文档列表（只要排名，不要原始分）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 对每一路，给文档记名次 rank_i（从 1 起）"),
                                topic("Step2 对每个文档累加 1/(k + rank_i)，默认 k=60"),
                                topic("Step3 按总分降序截断 Top-N"),
                                topic("Step4 去重：同一 doc id 只保留一条，分数已是累加结果"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("跨路可比的综合排名；「两路都靠前」优于「一路第一、一路很差」"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("A：稠密2 + 稀疏5 → ≈0.0315"),
                                topic("B：稠密1 + 稀疏20 → ≈0.0289"),
                                topic("A 胜出：均衡优于偏科"),
                            ],
                        ),
                        topic(
                            "和 relative_score 对比",
                            children=[
                                topic("RRF：只看名次，最稳，工业首选"),
                                topic("relative_score：先 min-max 归一化再加权，适合「明知 FAQ 更权威就给 1.2 权重」"),
                                topic("Round-Robin：轮流取各路结果，偏多样性（搜索首页）"),
                            ],
                        ),
                        topic("翻车点：把 RRF 和「加权平均原始分」当成一回事"),
                    ],
                ),
                topic(
                    "方法3：多路召回 Multi-channel Retrieval",
                    children=[
                        topic("适用：知识分散在多个库/字段——技术文档、FAQ、社区、工单、手册"),
                        topic(
                            "输入",
                            children=[
                                topic("≥2 个独立 Document 列表或独立索引"),
                                topic("每路一个 Retriever（可向量可 BM25）"),
                                topic("同一用户问题"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 分库：按业务切 tech_docs / faq_docs / community_docs…"),
                                topic("Step2 分索引：每路 VectorStoreIndex 或 BM25Retriever"),
                                topic("Step3 分检索：QueryFusionRetriever 并发调各路"),
                                topic("Step4 融合：relative_score 加权 或 reciprocal_rerank"),
                                topic("Step5 RetrieverQueryEngine 把融合结果交给 LLM"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("带来源通道 metadata（如 channel=tech/faq）的融合候选"),
                                topic("覆盖面大于单库，召回率通常上升"),
                            ],
                        ),
                        topic(
                            "完整例子（讲义三路）",
                            children=[
                                topic("路1 技术文档：稠密向量（长文语义）"),
                                topic("路2 FAQ：BM25 + jieba（短问答、关键词强）"),
                                topic("路3 社区讨论：稠密向量（口语）"),
                                topic("权重示例 [1.0, 1.2, 0.8]：FAQ 略加权"),
                                topic("问题「Qwen 部署需要多少显存？」→ 三路都可能贡献片段"),
                            ],
                        ),
                        topic(
                            "讲义代码逐行（三路召回）",
                            children=[
                                topic(
                                    "Settings.embed_model / Settings.llm = DashScope(...)",
                                    children=[
                                        topic("意思：Embedding 负责检索向量，LLM（如 qwen）负责最后生成"),
                                        topic("为什么：检索阶段可以不调 LLM；生成阶段才用 qwen3.7-max"),
                                    ],
                                ),
                                topic(
                                    'Document(..., metadata={"id": "...", "channel": "tech"})',
                                    children=[
                                        topic("意思：每条原文带上来源标签，检索结果能看出出自哪一路"),
                                        topic("为什么：三路混在一起后，没有 channel 就无法排查是哪库答偏了"),
                                    ],
                                ),
                                topic(
                                    "tech_index = VectorStoreIndex.from_documents(tech_docs)",
                                    children=[
                                        topic("意思：技术文档单独建一个稠密索引，和 FAQ、社区互不共用"),
                                        topic("为什么：多路召回的关键是「分库分索引」，不是把所有文档塞进一个库"),
                                    ],
                                ),
                                topic(
                                    "faq_retriever = BM25Retriever.from_defaults(nodes=faq_index.docstore...)",
                                    children=[
                                        topic("意思：FAQ 这一路不用向量，改用 BM25 抓短问答里的关键词"),
                                        topic("docstore.docs.values() 意思：把索引里已经切好的 Node 拿出来给 BM25"),
                                        topic("tokenizer=jieba 意思：中文 FAQ 也必须先分词"),
                                    ],
                                ),
                                topic(
                                    "community_retriever = community_index.as_retriever(similarity_top_k=3)",
                                    children=[
                                        topic("意思：社区口语再走稠密向量，每路先各取 3 条"),
                                    ],
                                ),
                                topic(
                                    "QueryFusionRetriever(retrievers=[tech, faq, community], retriever_weights=[1.0, 1.2, 0.8], mode='relative_score', num_queries=1, similarity_top_k=5)",
                                    children=[
                                        topic("retrievers 意思：三路检索器放进同一个融合器，一次 query 并发去搜"),
                                        topic("weights 意思：FAQ 权重 1.2 略高，社区 0.8 略低——你更信哪路就抬哪路"),
                                        topic("mode=relative_score 意思：先把每路分数 min-max 拉到同一尺度再加权"),
                                        topic("为什么：cosine 大约 0~1，BM25 可以很大，不归一化 FAQ 会霸榜或被淹没"),
                                        topic("num_queries=1 意思：这次不让模型再改写出多个问法，只用用户原句"),
                                        topic("similarity_top_k=5 意思：三路合并去重后，最终只留 5 条给生成"),
                                        topic("use_async=False 意思：教学示例用同步调用，方便单步调试"),
                                    ],
                                ),
                                topic(
                                    "query_engine.query(question) → response.source_nodes / response.response",
                                    children=[
                                        topic("source_nodes 意思：融合后真正喂给模型的片段，可打印 channel 和 id"),
                                        topic("response 意思：模型根据这些片段写出的最终回答"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "翻车点",
                            children=[
                                topic("路数盲目加到 5+：延迟和费用线性涨，2~3 路通常够"),
                                topic("各路 top_k 过大又不融合截断：噪音淹没生成"),
                                topic("忘记写 channel/id 元数据：出了错无法追哪一路在捣乱"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法4：混合 × 多路 嵌套架构",
                    children=[
                        topic("适用：企业多知识库，且每库内部既有语义又有术语需求"),
                        topic(
                            "输入",
                            children=[
                                topic("多个数据源；每源内部可再配向量+BM25"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 外层按数据源开多路召回"),
                                topic("Step2 每一路内部做混合检索（向量+BM25+RRF）"),
                                topic("Step3 外层再 RRF/加权融合 + 去重"),
                                topic("Step4 可选：再接 rerank（检索后）压到 Top-3/5"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("横向覆盖全，纵向每源也准——工业级检索骨架"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("外层：产品文档 / 客服工单 / 技术规范"),
                                topic("内层：每库 Hybrid"),
                                topic("用户问「登录超时怎么处理」：文档给规范说法，工单给个案经验"),
                            ],
                        ),
                        topic("翻车点：一上来就上嵌套，Native 单路都没稳——先单库混合，再拆多路"),
                    ],
                ),
                topic(
                    "方法5：中文 BM25 分词配置",
                    children=[
                        topic("适用：所有要用 BM25 的中文 RAG"),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 安装 jieba + llama-index-retrievers-bm25"),
                                topic("Step2 方案A：tokenizer=lambda t: list(jieba.cut(t))"),
                                topic("Step3 方案B：def tokenize_text(t): return list(jieba.cut(t)) 再传入"),
                                topic("Step4 方案C（讲义推荐组合）：language='chinese', skip_stemming=True, 中英 token_pattern"),
                                topic("Step5 自测：对含专名的短问，看 BM25 是否单独能命中"),
                            ],
                        ),
                        topic(
                            "代码逐行",
                            children=[
                                topic(
                                    "def tokenize_text(text): return list(jieba.cut(text))",
                                    children=[
                                        topic("意思：输入一整句，输出词列表，例如「登录超时怎么处理」→ ['登录','超时','怎么','处理']"),
                                    ],
                                ),
                                topic(
                                    "tokenizer=tokenize_text",
                                    children=[
                                        topic("意思：把函数本身交给 BM25，让它在检索时自己去调用"),
                                        topic("为什么：写成 tokenize_text() 会立刻执行，传进去的是词列表，检索时会报错"),
                                    ],
                                ),
                                topic(
                                    "language='chinese'",
                                    children=[
                                        topic("意思：停用词表用中文，去掉「的/了/吗」这类无信息词"),
                                    ],
                                ),
                                topic(
                                    "skip_stemming=True",
                                    children=[
                                        topic("意思：关闭英文词干还原（running→run）"),
                                        topic("为什么：中文没有词干，开着会乱改字"),
                                    ],
                                ),
                                topic(
                                    'token_pattern=r"(?u)\\b\\w+\\b|[\\u4e00-\\u9fa5]"',
                                    children=[
                                        topic("意思：英文按单词切，中文至少按汉字切，避免整句粘成一块"),
                                        topic("为什么：这是不用 jieba 时的保底切法；有 jieba 时优先用 jieba"),
                                    ],
                                ),
                            ],
                        ),
                        topic("输出：稀疏路真正按「词」计分，而不是整句一个 token"),
                        topic("翻车点：tokenizer=tokenize_text() 多写了括号——传入的是列表不是函数"),
                    ],
                ),
                topic(
                    "方法怎么串起来（推荐顺序）",
                    children=[
                        topic(
                            "诊断",
                            children=[
                                topic("专名/编号搜不到 → 先上方法1 混合（同库加 BM25）"),
                                topic("资料散落多系统 → 再上方法3 多路"),
                                topic("两路分数对不齐 → 方法2 RRF；要偏科加权 → relative_score"),
                                topic("多库且每库都难搜 → 方法4 嵌套"),
                            ],
                        ),
                        topic(
                            "标准 RAG 五步中的位置",
                            children=[
                                topic("1 加载 2 分块 3 向量化入库 —— 不变"),
                                topic("4 检索召回 —— 替换为 Hybrid / Multi-channel / 嵌套"),
                                topic("5 喂给大模型 —— 可再接第 07 章重排与压缩"),
                            ],
                        ),
                        topic(
                            "和本仓库",
                            children=[
                                topic("当前 chroma文档管理 ≈ 单路稠密 Native"),
                                topic("最小改法：同 nodes 加 BM25 + QueryFusionRetriever(mode=reciprocal_rerank)"),
                                topic("有多目录知识时再拆多路并打 channel 元数据"),
                            ],
                        ),
                        topic(
                            "和第 08 章衔接",
                            children=[
                                topic("先 Pre：清洗/重写/HyDE 得到更好 query"),
                                topic("再 Mid：用本章方法去查"),
                                topic("再 Post：rerank + 约束生成"),
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


# 各章柔和配色：主色（章标题）+ 浅底（一级小节）
CHAPTER_COLORS = [
    ("#2563EB", "#DBEAFE"),  # 01 蓝
    ("#059669", "#D1FAE5"),  # 02 绿
    ("#D97706", "#FDE68A"),  # 03 琥珀
    ("#0891B2", "#CFFAFE"),  # 04 青
    ("#E11D48", "#FFE4E6"),  # 05 玫红
    ("#7C3AED", "#EDE9FE"),  # 06 紫
    ("#EA580C", "#FFEDD5"),  # 07 橙
    ("#0D9488", "#CCFBF1"),  # 08 青绿
    ("#4F46E5", "#E0E7FF"),  # 09 靛
]


def style_topic(
    fill: str,
    font_color: str,
    bold: bool = False,
    size: str = "12pt",
    border: str | None = None,
    line: str | None = None,
) -> dict:
    props = {
        "svg:fill": fill,
        "fo:color": font_color,
        "fo:font-family": "Microsoft YaHei",
        "fo:font-size": size,
        "shape-class": "org.xmind.topicShape.roundedRect",
        "border-line-width": "1.5pt",
        "border-line-color": border or fill,
        "line-class": "org.xmind.branchConnection.roundedElbow",
        "line-color": line or "#94A3B8",
        "line-width": "1.5pt",
        "fo:font-style": "normal",
    }
    if bold:
        props["fo:font-weight"] = "bold"
    return {"id": nid(), "properties": props}


def paint_chapter(node: dict, accent: str, soft: str, depth: int = 0) -> None:
    """章内放射布局 + 同色系深浅分层。"""
    if depth == 0:
        node["style"] = style_topic(accent, "#FFFFFF", bold=True, size="16pt", line=accent)
        node["structureClass"] = "org.xmind.ui.map.unbalanced"
    elif depth == 1:
        node["style"] = style_topic(soft, "#0F172A", bold=True, size="12pt", border=accent, line=accent)
        node["structureClass"] = "org.xmind.ui.map.unbalanced"
    elif depth == 2:
        node["style"] = style_topic("#FFFFFF", "#1E293B", bold=True, size="11pt", border=soft, line=soft)
        node["structureClass"] = "org.xmind.ui.map.unbalanced"
    else:
        node["style"] = style_topic("#FFFFFF", "#475569", bold=False, size="11pt", border="#E2E8F0", line=soft)
    for child in node.get("children", {}).get("attached", []):
        paint_chapter(child, accent, soft, depth + 1)


def make_overview(chapters: list) -> dict:
    """总览：顺时针放射，各章不同颜色；小节下再露出一层要点。"""
    children = []
    for i, ch in enumerate(chapters):
        accent, soft = CHAPTER_COLORS[i % len(CHAPTER_COLORS)]
        sections = ch.get("children", {}).get("attached", [])
        section_nodes = []
        for s in sections:
            grand = s.get("children", {}).get("attached", [])
            kids = []
            for g in grand[:6]:
                title = g["title"]
                if len(title) > 26:
                    title = title[:26] + "…"
                kn = topic(title)
                kn["style"] = style_topic("#FFFFFF", "#64748B", size="10pt", border="#E2E8F0", line=soft)
                kids.append(kn)
            sn = topic(s["title"], children=kids or None)
            sn["style"] = style_topic("#FFFFFF", "#334155", size="11pt", border=soft, line=soft)
            if kids:
                sn["structureClass"] = "org.xmind.ui.map.unbalanced"
            section_nodes.append(sn)
        node = topic(ch["title"], children=section_nodes or None)
        node["style"] = style_topic(accent, "#FFFFFF", bold=True, size="12pt", line=accent)
        node["structureClass"] = "org.xmind.ui.map.unbalanced"
        children.append(node)

    root = topic(
        "RAG入门课",
        note="总览看章节结构。底部切换画布查看各章完整细节（放射布局）。",
        children=children,
    )
    root["structureClass"] = "org.xmind.ui.map.clockwise"
    root["style"] = style_topic("#0F172A", "#FFFFFF", bold=True, size="18pt", line="#64748B")
    return root


def shorten_sheet_title(title: str) -> str:
    t = title.strip()
    if "（" in t:
        t = t.split("（")[0].strip()
    if t.startswith("0") and " " in t:
        num, rest = t.split(" ", 1)
        return f"{num} {rest[:18]}".strip()
    return t[:20]


def make_sheet(title: str, root: dict) -> dict:
    return {
        "id": nid(),
        "class": "sheet",
        "title": title,
        "rootTopic": root,
        "topicPositioning": "fixed",
    }


def main():
    import copy

    chapters = copy.deepcopy(TREE.get("children", {}).get("attached", []))
    sheets = [make_sheet("00 总览", make_overview(chapters))]

    for i, ch in enumerate(chapters):
        accent, soft = CHAPTER_COLORS[i % len(CHAPTER_COLORS)]
        chapter = copy.deepcopy(ch)
        paint_chapter(chapter, accent, soft, depth=0)
        sheets.append(make_sheet(shorten_sheet_title(chapter["title"]), chapter))

    content = sheets
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
    print(f"sheets={len(sheets)}; colored chapters; radial layout")


if __name__ == "__main__":
    main()
