# RAG入门课
根据飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、Native RAG、Advanced RAG、检索前/中/后优化（Pre / Retrieval / Post-retrieval）、Self-RAG、Corrective RAG（CRAG）、RAG 评估、Modular RAG、知识图谱（Neo4j）、GraphRAG 使用（PropertyGraphIndex）、多模态 RAG（Chinese-CLIP）。

## 01 认知阶段：大模型介绍、调用、RAG
飞书文档：01-认知阶段（大模型介绍，调用，RAG）

### 术语定义（本章必背）

#### AI（人工智能）：让机器模拟人类智能的总称，含规则系统、搜索、机器学习等

#### 机器学习 ML：从数据自动学习规律，而不是纯手工写规则

#### 深度学习 DL：用深层神经网络自动提取特征的一类机器学习

#### 大模型 / LLM：参数规模极大、多基于 Transformer 的语言模型（如 GPT、DeepSeek）

#### 生成式 AI（GAI）：按提示生成文本/图像/音频/视频/代码等新内容

#### AGI（通用人工智能）：能像人一样完成任意智力任务的假想系统，目前未实现

#### Transformer：主流大模型骨干架构，核心是注意力机制

#### Token：模型处理文本的基本单位（子词/字等），计费与窗口常按 token 计

#### 上下文窗口 Context Window：一次能读入的最大 token 长度

#### 幻觉 Hallucination：生成看似合理但无依据或与事实不符的内容

#### 微调 Fine-tuning：在预训练模型上用领域数据继续训练以适配任务

#### Prompt / 提示词：给模型的指令与上下文输入（详见第 02 章）

#### API 调用：通过网络接口把 Prompt 发给云端/本地模型并取回结果

#### RAG：检索增强生成，先查外部知识再生成（详见第 03 章）

### 一、人工智能介绍

#### 1 从人工智能到大模型

##### 关系式：AI ⊃ 机器学习ML ⊃ 深度学习DL ⊃ 大模型LLM

##### 四层含义

###### 最外层 AI：最广，让机器模拟人类智能，含规则系统、搜索、专家系统、机器学习

###### 第二层 ML：从数据自动学习规律，含决策树、SVM、随机森林、浅层神经网络

###### 第三层 DL：深层神经网络自动提特征，含 CNN、RNN、Transformer

###### 最内层 大模型：数十亿至数万亿参数，基于 Transformer，如 GPT、Kimi、文心一言

##### 说明：大模型本质是深度学习的一种实现，因规模涌现和技术生态常被单独强调

#### 2 人工智能和生成式人工智能
AI 和 GAI 都是提出目标，GAI 的目标更具体

##### 2.1 人工智能 AI
跨计算机、数据、统计、工程、语言学、神经科学、哲学、心理学，研究能学习、推理、行动的机器

###### 历史上长期依赖非机器学习

###### 规则系统：IF-THEN 硬编码，如专家系统 MYCIN

###### 搜索算法：1997 深蓝击败卡斯帕罗夫，暴力搜索+符号主义

###### 知识图谱：结构化知识推理，如 Google Knowledge Graph

###### 符号主义 AI：逻辑推理、知识表示

###### 机器学习是主流实现方式

###### 2010年前传统ML：数据少，特征靠人工设计

###### 2010-2020 深度学习：自动特征提取，大数据驱动

###### 2020至今大模型：通用预训练，出现涌现能力

##### 2.1.3 生成式人工智能 GAI

###### 定义：按用户提示，学习海量数据模式，生成以前不存在的文本、图像、音频、视频、代码

###### 文本生成：ChatGPT、文心一言、DeepSeek

###### 图像生成：Midjourney、Stable Diffusion

###### 音频生成：Suno AI、语音合成

###### 视频生成：Sora

###### 当前状态：已成熟并广泛应用

##### 2.1.4 通用人工智能 AGI

###### 定义：假设中能像人一样理解和学习任何智力任务，不限特定领域

###### 跨领域迁移：学会下棋后把策略用到经济问题上

###### 常识推理：理解杯子推下桌子会摔碎

###### 元认知：知道自己不知道，再去学

###### 当前状态：理论探索阶段，现有系统远未达到，是长期目标

#### 2.2 机器学习和深度学习
都是手段，深度学习是更强的手段

##### 机器学习 ML

###### 核心理念：无需显式编程即可从数据学习

###### 监督学习：用已标注数据训练，如标了猫的照片

###### 无监督学习：无标签中找结构，如客户分群

###### 强化学习：与环境互动，靠奖励惩罚学策略，如游戏AI

###### 案例：垃圾邮件过滤、Netflix推荐、股市预测

##### 深度学习 DL

###### 模仿神经元分层：输入层、多个隐藏层、输出层

###### ANN：算法支柱，模拟信号传递

###### CNN：图像和视觉

###### RNN：序列，如时间序列、文本

###### 案例：人脸解锁、医疗影像、自动驾驶

###### 神经网络：拟人概念，分层是不同维度的信息处理，并非真模拟大脑

###### Transformer：ChatGPT、DeepSeek 等主流模型的架构

##### NLP 自然语言处理

###### 让机器理解、解释、生成人类语言，处理语气情感语境

###### 词嵌入：词变成向量，表示语义远近

###### Transformer：可大规模并行训练，是大模型核心

###### 情感分析：从社交文本判断情绪

###### 案例：ChatGPT、Google翻译、Siri Alexa 小艺

##### CV 计算机视觉

###### 让计算机看懂视觉世界：识别、定位、描述

###### 图像分类与目标检测：是什么、在哪里

###### 特征提取：边缘、轮廓等关键模式

###### 案例：安防行人检测、相册人脸分类、自动驾驶道路识别

#### 2.3 大模型和大语言模型

##### LLM 大语言模型

###### 用大量文本训练的深度学习模型，能生成或理解自然语言

###### 核心：大规模无监督训练，学习语言模式和结构

###### 能力：拼写语法、摘要、翻译、情感分析、对话、推荐

###### 预训练后具备通用建模和泛化能力

##### LM 大模型

###### 参数规模：通常数十亿到数千亿

###### 训练数据：互联网文本、书籍、代码等

###### 通用能力：理解、推理、生成、分类

###### 涌现能力：规模到一定程度后出现意想不到的能力

##### 对比表：大模型 vs 大语言模型

###### 范围：大模型更广、涵盖所有模态；LLM 更窄、专指文本语言

###### 输入输出：大模型可文本图像音频视频代码；LLM 主要处理文本

###### 关系：大模型是母集，LLM 是子集

###### 一句话：所有 LLM 都是大模型，但并非所有大模型都是 LLM

##### 大模型不止语言 多模态家族

###### 大语言模型：GPT-4、Kimi、Claude → 文本理解与生成

###### 视觉大模型：SAM、CLIP、Stable Diffusion → 图像理解、分割、生成

###### 多模态大模型：GPT-4o、Gemini、Kimi-VL → 同时处理图文音视频

###### 科学大模型：AlphaFold、GraphCast → 蛋白质结构、天气预报

#### 2.4 大模型的爆炸式发展

##### 有人把大模型发明类比为人类学会用火

##### 2021 斯坦福提出 Foundational Models 基础模型

##### 2022.11 OpenAI 发布 ChatGPT，对话交互，能写论文邮件脚本代码翻译

##### 随后百模大战，成为技术和公众热点

##### 2025 DeepSeek

##### 常把 2023 称为 AI 元年：问答、辅助编程、看图、创作进步极快

### 二、大模型介绍及其常用大模型

#### 1.1 基本概念

##### 超大参数神经网络，通常基于 Transformer

##### 在海量文本上自监督训练，通过预测下一个 token 学习语言和知识

##### 什么是 token

###### 模型处理文本的最小信息块，不完全等于字或词

###### 可以是完整英文单词、一个汉字、单词片段、标点或空格

###### 如 unbelievable 可能拆成 un + believ + able

###### 各模型分词方式不同

###### DeepSeek 约：1个英文字符≈0.3 token；1个中文字符≈0.6 token

###### 讲义对照表：英文 1 token≈0.75 个单词，Hello world≈2 tokens

###### 讲义对照表：中文 1 token≈1 个汉字，你好世界≈4 tokens

###### 经验另说：1000 token ≈ 750 英文词，或 400-500 汉字

###### 不同模型切法不一样，以上比例不要混用

###### 可视化：gpt-tokenizer.dev 可看 GPT 如何切 token

##### 为什么 token 重要

###### 计费单位：输入+输出都按 token 收费

###### 上下文限制：一次能处理的 token 有上限

###### 超出窗口会遗忘之前内容

###### 例子：15万汉字约20万 token，早期 4K 窗口读不完，百万级窗口可以

##### 类比：token 像乐高积木，先拆开理解，再拼成回复

#### 四个“大”

##### 参数量“大”

###### 从百万、千万到数亿、数百亿甚至万亿，单位 B=10亿

###### 参数即记忆单元，是存储和表达知识的载体

###### 参数越多，能拟合的模式越复杂，语义关系和知识更精细

###### 规模分级 讲义表

###### 小型 <1B：Phi-3 Mini 3.8B、TinyLlama 1.1B

###### 中型 1B-10B：Gemma 2 9B、Qwen2.5 7B

###### 大型 10B-100B：Llama 3 70B、GPT-3 175B

###### 超大规模 >100B：GPT-4 约1.76T、Llama 3 405B、DeepSeek V3 671B

###### 学生做题比喻

###### 参数 = 学生大脑里的解题套路

###### 小模型几百万：小学生，只会加减乘除，应用题读不懂

###### 中模型几亿：初中生，会解方程，复杂几何经常错

###### 大模型几百亿：高中生/大学生，微积分、物理建模都能做

###### 超大模型千亿：教授，能发论文、跨学科创新

##### 训练数据量“大”

###### 支撑庞大参数需要海量数据

###### 来源广：互联网爬取，文本图像音频视频多模态

###### 覆盖面广才有通用性，像人博览群书

##### 计算资源消耗“大”

###### GPU：图形处理器，数千 CUDA 核心，通用并行，图形、科学计算、AI

###### TPU：张量处理单元，脉动阵列，专为稠密矩阵乘优化，适合 Transformer

###### 训练周期：数周到数月，取决于规模和硬件

###### 电力和硬件成本高，微调和推理部署对工程能力要求也高

##### 应用范围广、效果提升大

###### NLP：生成、翻译、问答、对话

###### CV：图像理解、生成、多模态对齐

###### 语音：识别、合成、多模态交互

###### 长上下文理解与多轮对话，部分任务接近或超过人类水平

#### 1.2 常用大模型
有开源协议模型，也有闭源 API 按 token 收费

##### 国际阵营

###### OpenAI GPT 系列：综合均衡，擅长工具运用和 Agent 工作流

###### o 系列：推理专用，数学和复杂分析强，成本较高

###### Anthropic Claude：编程领先，超长上下文，安全敏感场景好

###### Google Gemini：原生多模态文本图像音频视频，窗口大、性价比高；Flash 更快更便宜

###### xAI Grok：文本生成榜靠前，与 X 平台深度集成

##### 国产阵营

###### DeepSeek R1/V3：开源代表，推理逼近闭源，训练成本低、性价比高

###### 月之暗面 Kimi：长文本专家，法律条文分析突出

###### 智谱 GLM：清华系，中英双语和 Agent 好，国产硬件适配好

###### 阿里通义千问 Qwen：开源生态强，中文场景优化好

###### 字节豆包：语音识别与实时交互，稀疏 MoE 降成本

###### 百度文心一言：文言文互译、方言交互

###### 商汤 SenseChat、MiniMax 角色扮演与创意写作

#### 2 大模型调用

##### 2.1 OpenAI

###### 开发平台：developers.openai.com

###### API Platform → Get started → Create an API Key

###### Key 放到环境变量后要重启 IDE

###### 现在不免费，需充值，常要可境外结算的 Visa

###### 没额度会报错；也可找国内中转，或直接用国内大模型

##### 2.2 阿里百炼 适合入门

###### 一站式大模型开发平台 Model Studio

###### 模型广场：通义千问、Llama、DeepSeek 等上百款

###### 统一 API：OpenAI 兼容，降低接入成本

###### 工具链：提示词、RAG 知识库、微调、智能体编排

###### 企业级：高并发、内容安全、用量监控

###### 为什么选它：国内直连低延迟、新人免费额度、从 turbo 到 max/R1 全覆盖、和 OSS/函数计算集成

###### 关键概念：API-KEY 身份凭证

###### Endpoint：https://dashscope.aliyuncs.com/compatible-mode/v1

###### 模型名：qwen-plus、qwen-max、deepseek-r1、qwen-turbo

###### 需注册并实名，支付宝可完成；控制台底部 API-KEY 管理里创建

##### 2.3 调用百炼

###### Python >= 3.8

###### 两种 SDK 二选一：DashScope 官方，或 OpenAI 多语言 SDK

###### 建议装 openai，以后换别的兼容服务也能用

###### Key 写入系统环境变量，代码用 os.getenv 读取

###### 若配置了 OPENAI_API_KEY，有的写法可省略显式传 key

##### 2.4 使用 OpenAI 库

###### 官方 Python SDK：聊天、绘图、语音等，不用自己拼 HTTP

###### 很多国产服务兼容这套调用方式

###### 基础三步

###### 创建 OpenAI 对象，设 base_url 和 api_key

###### 调用时必填 model 和 messages

###### 从返回里取文本结果

###### messages 四类

###### system：设角色、语气、目标、约束，一般放第一位

###### user：用户问题或指令，必填

###### assistant：模型历史回复，多轮时回传

###### tool：工具输出

###### 都是字典，key/value 按官方文档写

###### 流式输出 stream

###### 默认 false：整段生成完一次性返回

###### true：边生成边返回 chunk，要自己拼接

###### 推荐 true：阅读体验好，也降低超时风险

###### 附带历史：messages 是 list，把过往对话填回去，模型才知道上下文

### 三、大模型部署方式
按成本和控制权分三种：云端 API、云上自托管、本地/边缘

#### 1 云端 API

##### 直接调 OpenAI、Anthropic、Google、阿里云、腾讯云、火山引擎

##### 拿到 Key，后端或前端 HTTP 调用

##### 优点：不养模型和硬件、快速用顶级模型、扩展稳定由厂商保障

##### 缺点：数据出网要评估合规、费用随调用量和定价变、延迟受网络影响

#### 2 云上自托管

##### 在 AWS/阿里云/腾讯云上部署开源模型

##### 推理引擎：Transformer、vLLM、TGI、llama.cpp、Ollama

##### 对外服务：Nginx、FastAPI、gRPC

##### 优点：可控版本路由限流、细粒度监控日志、要私有化又想用云算力

##### 缺点：自己管下载、显存、扩容、监控，要 MLOps 能力

##### MLOps：把 DevOps 用到机器学习全生命周期自动化

##### 云上自托管服务器类型

###### 公有云 GPU 实例：AWS p3/p4/g4dn、阿里云 GN7/V100、腾讯云 GN10；按需或包年，完整控制权；适合生产、长期训练

###### GPU 裸金属：阿里云神龙、AWS Nitro Enclaves；无虚拟化开销，性能极致；适合大规模分布式训练

###### 容器化 GPU：AWS EKS、阿里云 ACK、Google GKE；K8s 编排弹性伸缩；适合微服务推理集群

###### Serverless GPU：SageMaker Serverless、Replicate；按调用付费零运维；适合轻量推理、突发流量

###### 算力租赁：AutoDL、恒源云、Featurize、vast.ai；按小时计费即开即用

#### 4 本地与边缘部署

##### 个人电脑、实验室、私有机房推理

##### 工具：Ollama、LM Studio、Mac 上 MLX LM、llama.cpp、vLLM

##### 常用中小模型 7B/14B，加量化降显存

##### 优点：数据不出本地、无 API 费、可离线

##### 挑战：要 GPU 或强 CPU，自己管模型文件和版本

##### 边缘：把一部分云能力下沉到离用户更近的地方

#### 5 Ollama
课上定位：知道即可，后面还要用 vLLM

##### 是什么：开源、跨平台、轻量的本地大模型运行管理引擎

##### 不是模型本身，是运行容器和调度工具：下载、加载、推理、资源管理、对外服务

##### 过去要配 CUDA、转模型、手写参数；现在一条命令拉模型、一条命令对话

##### 官网 ollama.com，默认装 C 盘，模型目录务必改走

##### 内存：7B 约 8G 可用，13B 约 16G，33B 约 32G；磁盘建议预留 50G

##### 支持纯 CPU；有 NVIDIA GPU 可加速

##### 装模型：官网选模型看体积，终端拉下来就能对话

##### 本地 HTTP 默认 http://localhost:11434/api

##### 默认只允许本机 127.0.0.1 访问

##### 局域网：环境变量 OLLAMA_HOST=0.0.0.0，OLLAMA_ORIGINS=* 防跨域

##### 或改 ~/.ollama/config.json，改完必须重启

##### 浏览器访问 ip:11434 看到 Ollama is running 即成功

##### Python 可普通调用、流式、接到 FastAPI；思考模型开始会短暂停顿无输出

### 四、大模型应用介绍

#### 定义

##### 以 LLM 为大脑，结合外部数据、记忆、工具，解决具体业务问题

##### 不只是聊天机器人，而是业务场景里的智能系统

#### 1 常见类型

##### Prompt Engineering：设计提示让输出符合格式逻辑，如文案、翻译。人要会说话对方才懂

##### Conversational AI：加 Memory，记住多轮上下文，如 ChatGPT、智能客服

##### RAG：外挂知识库，先检索私有资料再生成，解决没读过内部文档和幻觉

##### RAG 比喻：预训练像通识，入职后再学公司制度才能答内部问题

##### Agents：装手脚，能规划并调用工具查天气、跑代码、操作数据库

##### Agent 比喻：自己不行就找同事、其他部门、领导协调；拧螺丝=工具+记忆中的经验

#### 2 构建挑战

##### 数据连接：企业文档、数据库怎么接到 LLM

##### 上下文管理：长对话如何一致，面试常问 Agent 怎么记上下文

##### 工具调用：怎么调外部 API、数据库

##### 多步骤推理：决策链和任务分解

##### 可观察性：怎么调试和优化

#### 3 为什么需要框架

##### 不是只会写提示词，需要完整工具链

##### 类似 Web 要用 Django、FastAPI、Spring、Vue

##### LlamaIndex 等提供标准化、模块化组件

#### 4 LlamaIndex

##### 定位：把私有数据接到 LLM，做 RAG、机器人、文档理解、Agent

##### 官网 llamaindex.ai，中文文档 docs.llamaindex.org.cn，GitHub run-llama/llama_index

##### 六模块：Data Connectors、Index、Retriever、Query Engine、Agents、Workflows

#### 5 LlamaIndex 使用

##### 调用不同模型要单独装包

###### DeepSeek：llama-index-llms-deepseek

###### 千问不在默认列表，用 DashScope：llama-index-llms-dashscope

###### Ollama：llama-index-llms-ollama，模型必须本机已部署，ollama list 可查

###### 多模态要选支持多模态的模型，如 qwen3.5:4b

##### llm.complete：单轮纯字符串，无角色、无状态

##### llm.chat：消息列表可分 system/user/assistant，内置多轮，实际开发首选

##### stream_complete 是生成器，delta 是本段新增文本

##### 对照代码：见本章「五、代码详解」909.py 的 memory.put + stream_chat

##### 对话系统 Chatbot

###### 无记忆：每轮独立

###### 有记忆：Context + Memory 多轮连贯

###### 可接 OpenAI、Qwen、Ollama、Llama、Claude

###### 再接知识库就变成知识型 Chatbot

##### RAG 能力清单

###### Reader 文档加载，SimpleDirectoryReader 可读杂乱无结构文件

###### Splitter 分块，前面往往只配置，真正切分在建索引时

###### Embedding 向量化：语义近则向量近，语义远则向量远

###### 本地嵌入：Ollama 的 nomic-embed-text 或 qwen3-embedding:0.6b

###### 云端嵌入：DashScope 千问，pip install llama-index-embeddings-dashscope

###### 切分先用 Tokenizer 转 token 再按 token 数切块

###### VectorStoreIndex + Chroma 存储

###### Query Engine 查询；可加记忆做 RAG+多轮

##### 示例数据：考勤知识入库、了凡四训问答

#### 作业

##### FastAPI 提供接口

##### 页面上传文档，向量化后存向量库

##### 简易对话窗口能聊天

### 五、代码详解（仓库对照）
对照「基础聊天机器人」(原908) 与 909.py（LlamaIndex 多轮）。每条都是：代码 → 意思 → 注意点。

#### 1 读密钥

##### load_dotenv(脚本目录 / '.env')

###### 意思：把 .env 里的 KEY=值 读进 os.environ

###### 为什么：密钥不写死在代码里，换机器只改 .env

###### 注意：必须用脚本所在目录；用相对路径会受 IDE 工作目录影响读不到

##### api_key = os.getenv('DEEPSEEK_API_KEY')

###### 意思：从环境变量取出密钥字符串

###### 大坑：写成 api_key='DEEPSEEK_API_KEY' 会把字面量当密钥，一定报错

###### 兜底：基础聊天机器人还用 winreg 读 Windows 用户/系统变量

#### 2 创建客户端（还不发请求）

##### from openai import OpenAI

###### 意思：导入官方兼容 SDK（很多国产模型都能用这一套）

##### client = OpenAI(api_key=key, base_url='https://api.deepseek.com')

###### 意思：创建一个「会说话的客户端对象」，记下地址和密钥

###### 这一步只连配置，不会产生费用、也不会生成文字

###### 换百炼：base_url 改成 dashscope 的 compatible-mode/v1，model 改成 qwen-plus 等

#### 3 发对话请求

##### client.chat.completions.create(model=..., messages=..., stream=True)

###### 意思：真正向服务器发一轮聊天请求

###### model：用哪颗模型；messages：对话历史列表

###### stream=True：边生成边返回；False：等整段说完一次返回

###### messages 每条是字典，至少含 role（system/user/assistant）和 content

##### 非流式取全文：response.choices[0].message.content

###### 意思：从返回对象里取出助手说的整段文字

###### choices[0]：第一条候选（一般只用这一条）

#### 4 流式怎么拼字（打字机效果）

##### for chunk in stream: content = chunk.choices[0].delta.content

###### 意思：流式接口一次只给一小段新增字，叫 delta

###### 为什么用 for：要边收边推给前端，不能等全部结束

##### 必须 if content: 再拼接

###### 意思：有的 chunk 是空包，delta.content 是 None

###### 不判断直接 += 会报错或拼进 'None' 字符串

##### ai_result += content

###### 意思：自己攒完整回复，后面才能写入历史

###### 不攒的话：屏幕上有字，memory 里没有，下一轮会失忆

##### SSE：yield 'data: {json}\n\n'，最后 [DONE]

###### 意思：浏览器 EventSource 约定的格式，一行一个事件

###### FastAPI：StreamingResponse(..., media_type='text/event-stream')

#### 5 LlamaIndex 多轮（909.py）

##### llm = DeepSeek(model=..., api_key=..., timeout=120)

###### 意思：用 LlamaIndex 包装好的 DeepSeek 客户端

###### 后面用 llm.chat / stream_chat，不用自己拼 OpenAI 返回结构

##### memory = ChatMemoryBuffer.from_defaults(token_limit=10000)

###### 意思：一块「对话记事本」，按 token 上限自动裁旧消息

###### 10000：大约能记住很长一段多轮；太大费钱，太小易忘

##### memory.put(ChatMessage(role='system', content='...'))

###### 意思：先写入人设/规则，模型之后每轮都能看到

###### 一般只在启动时写一次，不要每轮重复塞

##### 每轮三步：put(user) → stream_chat(memory.get()) → put(assistant)

###### put(user)：先把用户话记下来，再问模型

###### memory.get()：把当前全部历史作为上下文交给模型

###### put(assistant)：把完整回复记回去，否则下一轮不知道自己说过什么

##### for r in llm.stream_chat(...): print(r.delta)

###### 意思：r.delta 是本块新增字，边打边显示

###### 要完整答案：自己 ai_result += (r.delta or '')

#### 6 三种调用怎么选

##### llm.complete('一段话')

###### 意思：单轮、无角色，输入输出都是纯字符串

###### 适合：内部小任务、改写、评分，不适合正式多轮客服

##### llm.chat(messages)

###### 意思：传入 system/user/assistant 列表，一次拿完整回复

###### 适合：正式对话、要人设、要历史

##### llm.stream_chat(messages)

###### 意思：和 chat 一样，但是一块块返回，体验更好、不易超时

###### 适合：网页/终端打字机效果

## 02 提示词工程
飞书文档：01-提示词。Prompt 是指令，Prompt Engineering 是优化指令的技术。

### 术语定义（本章必背）

#### Prompt（提示词）：给大模型的自然语言指令与上下文

#### Prompt Engineering（提示工程）：系统化设计、测试、优化提示词的方法

#### 角色 Role：在提示里规定 AI 身份与专业立场

#### 任务 Task：明确要求模型完成什么

#### 规则 Constraints：边界、禁止事项、判断标准

#### 输出格式 Output：长度、结构、示例、JSON 等

#### CLEAR 原则：Context / Length / Examples / Audience / Requirements 的提示设计口诀

#### Few-shot：在提示中给少量示例，引导输出风格与格式

#### Zero-shot：不给示例，只给任务说明

#### Chain-of-Thought（CoT）：要求模型逐步推理再给结论

#### 温度 Temperature：控制随机性；低更稳，高更发散

#### 系统提示 System Prompt：对话里长期生效的人设与规则（相对单次用户消息）

#### 提示注入 / Jailbreak：用恶意提示绕过安全规则的攻击手法

#### 防护：输入过滤、输出校验、权限隔离、拒绝越权指令

### 一、概述

#### 把 AI 当能力强但缺经验的新助手，指令清不清楚决定成果质量

#### 差提示：写一篇文章关于AI → 容易得到百科摘要式空文

#### 好提示：科技记者、800字、普通人用AI提效、25-40岁白领、具体案例、推荐3个工具、轻松幽默

#### 高质量提示通常含

##### 角色：身份、专业领域

##### 任务：明确要做什么

##### 规则：边界、禁止、判断标准

##### 输出：格式、长度、示例、JSON 结构

#### 提示工程是系统化设计、测试、优化提示词的学科，不只写一句话

### 1.2 设计原则

#### CLEAR 原则

##### Context 上下文：充分背景

##### Length 长度：明确输出多长

##### Examples 示例：给参考案例

##### Audience 受众：指定读者

##### Role 角色：定义 AI 身份

#### 优质 Prompt 特征

##### 目标明确具体

##### 包含必要约束

##### 提供参考框架

##### 指定输出格式

### 二、构成要素和技巧

#### 2.1 核心四要素

##### 角色 Role：你是一位资深营销专家，专注社交媒体内容创作

##### 任务 Task：请生成5个小红书标题，每个不超过20字

##### 上下文 Context：目标用户25-35岁都市女性，关注美妆和生活

##### 约束 Constraints：避免夸张营销词，保持自然真实

#### 2.2 基础技巧

##### 明确性：好=生成3个健康饮食微博；坏=写一些关于饮食的东西

##### 结构化：分点分段，便于执行

##### 示例引导：给输入输出样例，尤其复杂任务

### 三、调优实战技法

#### 环境准备

##### pip install openai dashscope

##### 用 OpenAI 兼容方式跑百炼/千问

##### Windows：此电脑→属性→高级系统设置→环境变量

##### 用户变量名 DASHSCOPE_API_KEY，值为 sk- 开头的 Key

##### 改完重启终端或 IDE

#### 零样本 Zero-Shot

##### 直接给任务指令，不提供示例

##### 适合简单明确、模型已具备相关知识的任务

#### 少样本 Few-Shot

##### 提供少量输入输出示例，让模型模仿格式和模式

##### 比只下指令效果更好

##### 情感例子：拍照好看→正面；物流太慢→负面；菜难吃→负面

#### 思维链 COT

##### 先展示推理过程再给最终答案

##### 适合复杂逻辑、数学题

##### 可在问题后加：请一步步思考

#### 自我一致性 Self-Consistency

##### 生成多个答案，投票或自评选出最优

##### 适合要高质量、多样化的输出，如选最佳口号

#### 思维树 ToT

##### 多分支思考路径，探索不同方案

##### 适合需要创造性解决的复杂任务

##### 过程：发散分支 → 评估剪枝 → 再执行

### 四、攻击防范
了解类型和防御思路即可，不要在生产里复现攻击细节

#### 4.1.1 提示注入

##### 在输入里嵌恶意指令，诱导模型做非预期行为

##### 直接注入：用户输入覆盖系统设定，如要求输出系统提示、绕过只答数学的限制

##### 间接注入：恶意指令藏在网页、PDF、简历等外部内容里，模型处理时触发

##### 其他手法：角色扮演劫持、编码混淆绕过关键词、把指令嵌进业务流程

##### 防御：过滤高风险指令用语、外部输入一律不可信、关键词+意图识别+输出再审+上下文隔离

#### 4.1.2 越狱 Jailbreak

##### 精心构造提示，绕过安全限制，诱导输出本该拦截的内容

##### 常见方向：无约束角色扮演、多轮逐步诱导、用故事幽默包装、对抗后缀干扰检测、学术研究幌子、自动化生成越狱提示

##### 防御：多层次内容审核、行为监控

#### 4.1.3 数据泄露

##### 巧妙提问套取训练或系统中的敏感信息

##### 相关风险还包括供应链工具、内部泄密、配置错误、社会工程、历史漏洞

##### 防御：拆分隐私、数据脱敏

#### 4.2 防范策略落地

##### 输入净化：content_sanitize.py

##### 多层审核：content_moderation.py

##### 安全沙箱：隔离执行高风险操作，限制系统权限和网络

### 五、实战案例

#### 5.1 优化过程通法

##### 先写清业务需求

##### 初始版往往效果一般

##### 再加角色和约束

##### 再加少样本

#### 5.2 电商产品描述 ecprompt.py

##### 输入：名称、核心卖点、目标人群

##### 输出：吸睛标题、痛点正文、小红书标签

##### system 角色：电商金牌文案专家

##### examples：完整的输入-思考-输出范例，锁语气和格式

##### COT：先分析痛点再转化卖点，避免空洞废话

##### temperature=0.7：太低死板，太高乱跑，0.7 是创意和稳定的平衡

#### 5.3 社交媒体内容策划

##### 需求：不是单篇文案，而是成体系选题和多角度发散

##### 输入宽泛主题如夏季减肥，扮演资深新媒体运营

##### ToT 三步：构思3个截然不同切入角度 → 评估爆款潜力与可行性 → 选出最佳并生成5个周更选题

##### 自我一致性：第二步回顾第一步并自我批判

##### 结构化输出：要求 Markdown 表格，方便进 Excel 或 Notion

##### 最后加自我反思 Self-Reflection

### 六、最佳实践

#### 设计原则

##### 明确：一次只交代一件主任务，避免又写文案又做分析

##### 完整：角色 + 任务 + 上下文 + 约束 + 输出格式尽量齐

##### 角色风格一致：system 人设不要和 user 指令打架

##### 考虑安全：外部用户输入不可直接拼进系统提示

#### 调优策略

##### 先零样本：确认模型会不会做，再决定要不要加示例

##### 再加复杂度：Few-Shot → COT → ToT，按失败点加，不一次堆满

##### 按输出迭代：先改格式，再改事实，再改语气

##### 建立评估标准：正确、完整、格式、安全四项打分

##### 记录有效模板：把跑通的 Prompt 存成可复用版本

#### 趋势

##### 自动生成/优化提示：用模型改模型的指令

##### 多模态提示：图+文一起当指令

##### 按反馈动态调：根据用户点踩实时改约束

##### 按用户特征个性化：同一任务对不同受众换角色和口吻

### 课后作业

#### 完成电商产品描述生成：标题 + 痛点正文 + 标签

#### 完成社交媒体内容策划：ToT 选题 + 表格输出

#### 对照：能说清自己加了角色、少样本还是思维链

### 七、代码详解（带安全校验 / 文案项目）
对应「带安全校验的聊天机器人」与「社交媒体文案和电商内容生成」（原 910.py）。每条：代码 → 意思 → 为什么。

#### 启动时做了什么

##### llm = DeepSeek(...) 只建一次

###### 意思：整个服务共用一个模型客户端

###### 为什么：每个请求都新建会又慢又浪费连接

##### rebuild_memory() → 新建 ChatMemoryBuffer + 写入安全 system

###### 意思：清空旧对话，并放入 BASE_SYSTEM_PROMPT

###### BASE_SYSTEM_PROMPT 作用：禁止透露系统指令、拒绝越权，这是安全底线

#### 零样本/少样本/COT/ToT 怎么接进代码

##### PROMPT_MODES = {'zero_shot': '...', 'cot': '...', ...}

###### 意思：四种策略各自是一段「前置说明文字」

###### 换模式 = 换这段文字，不换模型、不改接口

##### build_user_content(question, mode) → 策略 + '\n用户任务：' + 问题

###### 意思：把策略提示粘到用户问题前面，组成一条 user 消息

###### 真正发给模型的顺序：system（安全）→ 历史 → 这条带策略的 user

#### 输入净化 gate_user_input(text)

##### moderation_input：一堆正则扫 ignore previous / jailbreak 等

###### 意思：发现像「覆盖系统提示」的攻击句，直接判危险

###### 返回 None 表示拦截；返回清洗后的字符串表示通过

##### 拦截后返回固定话术，不解释原因

###### 意思：对外只说「无法回答」，不教对方怎么绕过

###### chat/stream_chat 都先过这一关，过不了就不调模型（省钱也更安全）

#### safe_messages(question, mode)

##### 失败返回 str（拒绝话术）

###### 意思：调用方看到是字符串就直接给前端，不再 llm.chat

##### 成功：确保有 system → put(user) → return memory.get()

###### 意思：返回「当前完整消息列表」，已经包含历史和本轮用户话

###### 接着：response = llm.chat(prepared)，再 put(assistant)

#### 电商文案 /product_copy

##### build_product_messages(product)

###### system：金牌文案 + 四步思维链（痛点→卖点→标题正文→标签）

###### user：先放两个完整示例（Few-Shot），再放本轮 name/features/audience

###### 为什么示例要完整：锁住语气和输出格式，少写废话

##### llm.chat(messages)，且不写入普通聊天 memory

###### 意思：文案是一次性任务，别污染客服多轮记忆

###### 三个字段分别 gate_user_input：防止注入藏在「卖点」里

#### 自我一致性 /self_consistency

##### 循环 N 次 llm.complete(不同角度 Prompt)

###### 意思：同一任务换说法各生成一个候选口号

###### 得到 candidates 列表

##### 再 llm.complete(评选 Prompt)

###### 意思：让模型从候选里挑一个，只输出最终口号

###### num 默认 2：少打几次 API，省时间省钱

#### 社交媒体 /social_plan（ToT 四次 complete）

##### 第1次：发散 3 个截然不同切入角度（干货/情感/争议）

##### 第2次：评估爆款与难度，选出最佳方向

##### 第3次：按选定方向生成一周选题表

##### 第4次：自我批判再润色

##### _complete_text(prompt) = llm.complete(prompt).text

###### 意思：小工具函数，专门拿完整字符串结果

###### 四阶段就是四次独立 complete，不是一次长对话

## 03 RAG整体认知
飞书文档：01-RAG整体认知。2020年 Facebook AI 提出，解决大模型答得快但不够准、不够新。

### 术语定义（本章必背）

#### RAG：Retrieval-Augmented Generation，检索增强生成

#### Retriever（检索器）：根据问题从知识库找出相关文档/片段

#### Generator（生成器）：基于检索上下文与问题生成最终回答的 LLM

#### 知识库 / Corpus：可检索的外部文档集合（可更新，不必重训模型）

#### Query：用户自然语言问题（可能口语、指代不明）

#### Embedding：把文本变成向量，便于语义相似度计算

#### Retrieval：在向量库/倒排索引中召回 Top-K 相关片段

#### Context：拼进 Prompt 的检索结果与约束说明

#### 引用 / Citation：答案标明来源片段，便于核查

#### 参数化知识：模型训练时写进权重的知识；RAG 额外使用非参数化外部知识

#### Native RAG：最简「检索→生成」流水线（见第 06 章）

#### Advanced RAG：在检索前/中/后系统优化（见第 07 章起）

#### 开卷考试比喻：模型是考生，RAG 是可翻的参考书

### 1 RAG 介绍

#### 1.1 是什么

##### 全称 Retrieval-Augmented Generation，检索增强生成

##### 生成前先从外部知识库检索相关文档，作为附加上下文再生成

##### 目标：更准确、更新、有据可查

##### 核心思想：给 LLM 配外挂知识库

##### 比喻：开卷考试。模型是闭卷考生，RAG 是可随时翻的参考书

##### 技术本质：检索器 Retriever + 生成器 Generator

#### 1.2 RAG 与纯大模型 LLM-only 对比表

##### 知识来源：纯模型只靠训练时记住的参数化知识；RAG=参数化知识+可随时更新的外部知识库

##### 知识时效：纯模型卡在训练截止日期，更新要重新微调；RAG 只需更新知识库文档，不必重训

##### 幻觉控制：纯模型容易对未知内容信口开河；RAG 有明确下文依据，可强制不知道就不答

##### 可解释性：纯模型无法溯源、难验证事实；RAG 可返回引用、支持核查

##### 领域适配：纯模型要大量微调数据和算力；RAG 只需准备领域文档，成本低

##### 上下文长度：纯模型受窗口限制；RAG 先检索筛选，可间接处理海量文档

##### 结论：RAG 不是替代大模型，而是给它装上实时、可信、可控的记忆外挂

#### 1.3 核心流程 Query → Embedding → Retrieval → Context → LLM → Answer

##### Query：自然语言问题，可能有错别字、口语、指代不明。如“上次那个产品的安全规范更新了吗”

##### Embedding：用与知识库相同的嵌入模型，把问题变成高维向量，如 768 或 1536 维，变成可运算的语义坐标

##### Retrieval：在向量库或倒排索引里算相似度，通常余弦相似度，召回 Top-K。这一步决定原材料质量，是成败瓶颈

##### Context：按相似度或时间等顺序拼接片段，加上“请仅根据以下资料回答”等约束；太多要裁剪以适配窗口

##### LLM：读完整 Prompt，当摘要者和解释者，而不是当记忆库

##### Answer：返回给用户，通常附来源片段便于人工核查

#### 1.4 三大痛点

##### 幻觉 核心痛点

###### 没有相关知识时编造看似合理的错误内容

###### RAG：强制只基于检索内容答，没有就提示无法回答，再加答案约束

##### 知识时效性差

###### 训练数据有截止日期，无法回答最新政策、新版语言特性

###### RAG：更新外部知识库即可，不必重新训练，成本低

##### 私有内网知识难落地

###### 闭源云模型要上传数据，处理不了涉密内部手册、校园内网通知

###### RAG：开源 LLM + 开源 Embedding + 本地向量库，数据不出内网，可用 FastAPI 封装

##### 误区：RAG 不能 100% 消幻觉。检索错了或 Prompt 约束不到位仍会编

#### 1.5 主流场景

##### 本地私有问答：笔记、公司手册，不联网

##### PDF 问答：论文、教材、说明书，提问后定位相关页再生成

##### 智能客服：FAQ、售后流程，标准化回答，可内网部署

##### 多知识库：PDF+Word+网页一次提问全检索，如校园通知+手册+FAQ

### 2 RAG 体系架构

#### 2.1 经典五步 先记做什么和为什么

##### 文档加载 Document Loading

###### 做什么：PDF/Word/TXT/网页加载成程序可处理的文本

###### 为什么：模型不能直接读本地文件

###### 后续：LangChain/LlamaIndex，尤其 PDF 解析难点

##### 文本分割 Text Splitting

###### 做什么：长文本切成 chunk

###### 为什么：有上下文窗口限制；小片段比整篇更好检索

###### 后续：chunk_size、chunk_overlap 调优

##### 向量化 Embedding

###### 做什么：文本块变成高维数值向量

###### 为什么：计算机用向量表示语义，才能语义检索

###### 后续：开源 BGE/M3E 本地部署或调用

##### 向量存储 Vector Storage

###### 做什么：向量写入向量数据库

###### 为什么：MySQL 等不擅长语义相似查询，向量库做了相似度优化，可达毫秒级

###### 后续：FAISS、Chroma 实操

##### 语义检索 + LLM 生成

###### 问题向量化

###### 在库中检索语义相似文本块

###### 文本块+问题拼成 Prompt 交给 LLM

###### 既要素材准，又要语言流畅

###### Prompt 要写：仅基于提供的检索内容回答，不要编造

#### 2.2 数据流拆解

##### 数据准备 Data Pipeline

###### 文档解析：按格式提取纯文本和结构，标题、表格

###### 数据清洗：去页眉页脚、广告、水印、乱码，规范空白

###### 切分 Chunking：按语义或长度切，加 overlap 防止关键句被切断，质量直接影响检索

###### 元数据：来源、时间、章节、标签，用于过滤和引用

##### 检索系统 Retriever

###### 向量检索：语义相似，鲁棒，主力

###### 稀疏检索 BM25：关键词，对专有名词、精确 ID 更好

###### 混合检索：两者互补

###### 输出：相关片段列表+相似度得分

##### 生成系统 Generator

###### 载体：GPT、Llama、文心一言等

###### 提示词：结构化注入检索结果，设禁止编造等约束

###### 后处理：格式化，添加引用标记

#### 2.3 五大范式 学霸养成记

##### Naive RAG 小学生会翻书

###### 流程：提问 → 关键词或基础语义搜 → 填进上下文 → 生成

###### 优点：简单、开发成本低、适合原型

###### 缺点：同义不同词可能搜不到；无关片段导致幻觉；硬切会长文语义断裂

###### 定位：Hello World，原型验证首选

##### Advanced RAG 初中生找得更准

###### 检索前：查询改写、扩展、HyDE，提高模糊问题命中率

###### 检索中：混合检索（向量 + BM25），专名和语义都照顾

###### 检索后：重排序 Re-ranking，精细模型二次打分，最相关的排前面

###### 定位：效果和成本的平衡点，工业界主流

###### 细节展开：见第 07 章；检索前见第 08 章；检索中见第 09 章

##### Modular RAG 高中生灵活用工具

###### 把检索器、生成器、重排器拆成可替换模块，像乐高

###### 路由 Routing 和调度 Scheduling：判断走向量库、传统库还是互联网

###### 定位：灵活可定制，是 LangChain、LlamaIndex 等框架基石

##### Graph RAG 大学生理解知识关系

###### 把段落提炼成实体-关系-实体三元组，用知识图谱

###### 多跳推理：顺藤摸瓜回答要多步的问题

###### 全局理解：能归纳主题，不只罗列片段，如从评价里归纳屏幕、续航

###### 代表：微软开源 GraphRAG，适合大规模摘要和复杂关系

###### 定位：从找相似跨越到做推理

##### Agentic RAG 研究生自己规划

###### 引入一个或多个 Agent，从被动工具变主动系统

###### 主智能体拆子任务，分别调向量搜、网页搜、API

###### 信息不足会自我反思并再检索

###### 定位：当前最前沿，从执行者变成会规划的思考者

#### 2.4 RAG vs 模型微调 怎么选

##### 领域知识增强时的第一选择：微调还是 RAG

##### 改知识：RAG 改文档即可；微调要重新训练，贵且慢

##### 改口吻风格、固定知识、要极低延迟：微调更合适

##### 要引用溯源、私有内网、知识常变：RAG 更合适

##### 可结合：微调让模型更会用检索资料，RAG 注入最新知识

##### 思考题：校园通知每月更新，该用 RAG，因为知识常变且不必重训

#### 2.5 局限与挑战

##### 检索质量决定上限

###### 最相关文件没召回，生成再强也没用

###### 后面 07/08 的改写、混合检索、重排序都是在抬这个上限

##### 上下文窗口

###### 答案分散在多处时可能被截断

###### 对策：父子块、上下文压缩、子查询分别答再综合

##### 检索噪声

###### 无关片段会误导模型，看起来像幻觉

###### 对策：重排序、去重、强制“没有依据就说不知道”

##### 延迟增加

###### 比纯 LLM 多一步检索，链路越长越慢

###### 对策：异步、缓存热门问、先小模型改写再检索

##### 依赖 Embedding 和切分

###### 中文和专业术语很敏感，切错/向量空间不一致会全崩

###### 写入和查询必须同一套 Embedding

## 04 Embedding 向量表示
飞书文档：02-大模型应用基础--Embeddings

### 术语定义（本章必背）

#### 向量 Vector：有大小和方向的数学对象，可写成一组有序数字

#### Embedding（嵌入）：用稠密数值向量表示对象（词/句/文档/图片等）

#### 维度 Dimension：向量有多少个数；常见 384/768/1024/1536 等

#### 词频向量：按词表统计出现次数的稀疏表示（教学用，现代多用神经网络嵌入）

#### 余弦相似度 Cosine Similarity：用夹角衡量方向像不像，约在 -1~1，越近 1 越像

#### 点积 Dot Product：对应维相乘再求和；是余弦公式的分子部分

#### 模长 / L2 范数：向量「长度」，各分量平方和再开方

#### 语义相似度：意思接近的文本，在嵌入空间里距离更近

#### Embedding 模型：专门把文本编码成向量的模型（如 bge、text-embedding-v3）

#### MTEB：衡量文本嵌入质量的公开榜单

#### 同空间原则：入库与查询必须用同一套 Embedding 模型，否则不可比

#### 本仓库常用：本地 BAAI/bge-small-zh-v1.5 或云端 text-embedding-v3

### 1 什么是 Embedding

#### 1.1 什么是向量

##### 有大小和方向的数学对象，可看成有向线段

##### 二维可写成 (x, y)，从原点到该点

##### Embedding：用数值向量表示一个对象

#### 1.2 用词频向量算句子相似度 五步

##### 句子A：这个程序代码太乱，那个代码规范

##### 句子B：这个程序代码不规范，那个更规范

##### Step1 分词：A=这个/程序/代码/太乱，那个/代码/规范；B=这个/程序/代码/不/规范，那个/更/规范

##### Step2 词表固定顺序：这个、程序、代码、太乱、那个、规范、不、更

##### Step3 词频：A 代码2 其余多数字1、不和更是0；B 规范2、代码1、太乱0、不1、更1

##### Step4 八维向量：A=(1,1,2,1,1,1,0,0)  B=(1,1,1,0,1,2,1,1)

##### 二维直觉：你好吗你好吗你好=(3,2)，你好=(1,0)

##### Step5 余弦相似度

###### 衡量方向像不像，范围约 -1 到 1，越接近 1 越像

###### 点积：对应维度相乘再全加。同一词两边都高则点积大

###### 本例点积=1+1+2+0+1+2+0+0=7

###### 模长：各分量平方和再开方，词频越高句子显得越长越丰富

###### 公式：点积 ÷ 两个模长的乘积

###### 结果约 0.737：代码/不/更 有差异，但这个、程序等多数词相同仍较像

###### 一句话：共同出现的词越多越频作分子，各自有多长作分母

#### 1.3 一个好的语义向量

##### 线性代数里的特征向量：被矩阵变换后方向不变只变长短

##### 比喻：橡皮泥里的铁丝，怎么捏方向大致不变

##### 词向量不是乱放的，语义关系编码成空间中跨词通用的方向

##### 性别轴：queen - king ≈ woman - man，所以 king - man + woman ≈ queen

##### 时态轴：walked - walking ≈ swam - swimming

##### 总结：词向量把语义变成算术

### 2 LLM 如何算词间距离

#### 先把词变成上下文感知的高维向量，再用余弦相似度量化亲疏

#### 距离越小含义越近，是语义搜索、聚类、情感分析的基础

#### 2.1 调百炼做文本向量化

##### OpenAI 兼容客户端，base_url 用 dashscope compatible-mode v1

##### 接口：client.embeddings.create，取出每条的 embedding

##### 课上模型：text-embedding-v3，维度可设 128 或 1024

##### 例子：查询“大模型应用真好”，去和一堆餐饮文档向量比

#### 2.2 用 numpy 算余弦

##### 公式：cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

##### a、b 必须是一维向量，且维度相同，否则点积会报错

##### 可对比：我爱你 vs 我恨你、vs 大模型有很多应用场景、vs python开发

##### 结果接近 1 更像，接近 0 不太像，接近 -1 语义相反

#### 2.3 代码详解：调百炼拿向量再算相似度

##### client = OpenAI(..., base_url='...dashscope.../compatible-mode/v1')

###### 意思：假装在调 OpenAI，实际打到阿里云百炼

###### 好处：代码和 DeepSeek/OpenAI 几乎一样，只改 base_url 和 model

##### resp = client.embeddings.create(model='text-embedding-v3', input=texts, dimensions=1024)

###### 意思：把多段文本一次性变成向量

###### input 可以是字符串列表：一次多句比 for 循环逐条调更省延迟

###### dimensions：向量长度，写入和查询必须相同

##### vec = resp.data[i].embedding

###### 意思：第 i 段文本对应的浮点数列表（如 1024 个数）

###### 和 texts[i] 一一对应，不要搞乱下标

##### 余弦：np.dot(a,b) / (norm(a)*norm(b))

###### 意思：比两个向量「方向」有多像，不比长短

###### ≈1 很像；≈0 没关系；≈-1 语义相反

###### 查询向量必须和文档用同一模型、同一维度，否则空间对不上

### 3 Embedding 的三大作用

#### 输入端语义编码

##### 模型不能直接处理原始文本

##### Embedding 层把 token 转为向量

##### 才能区分我爱你和我恨你在语义空间里的对立位置

##### 为后续注意力机制提供可计算表示

#### 语义检索与 RAG 应用层最常用

##### 知识库检索：问题向量化，在文档向量库里定位相关片段

##### 相似度匹配：判断两段是否在谈同一件事

##### 去重与聚类：发现语义重复内容

#### 跨模态理解基础

##### 文本和图像可共享同一 Embedding 空间

##### 一只橙色的猫 的文本和对应图片会靠近

##### 从而支持图文检索、零样本分类

### 4 如何得到 Embedding 了解

#### Word2Vec 两种架构

##### CBOW：用上下文预测中心词。给你相邻词，猜中间是什么。众人推举一个代表

##### Skip-gram：用中心词预测上下文。给你一个词，猜周围可能出现什么。一个代表辐射众人

#### 模型结构 三层网络

##### 关键词：One-hot、Multi-hot、隐藏层维度 N

##### 课上示意：词表大小 V=10，隐藏层 N=4

##### W 是 V×N：输入到隐藏，每一行就是一个词的词向量

##### W' 是 N×V：隐藏到输出

##### 输入 one-hot 只有当前词位置为 1

##### h = x @ W，等价于直接取出 W 的那一行

##### u = h @ W'，再 softmax 得到词表上的概率分布

#### Embedding 位于隐藏层权重矩阵 W，相当于词向量查找表

#### 和现代句向量的差别

##### Word2Vec：一个词一个向量，不管上下文（bank 河岸/银行会混）

##### 现在 RAG 用的是句子/段落 Embedding，同一词在不同句里向量不同

##### 课上实操走的是后者：text-embedding-v3、bge、nomic-embed-text

### 5 课上和项目常用模型

#### 云端：阿里云百炼 text-embedding-v3

##### 接口：embeddings.create，维度可设 128 或 1024

##### DashScopeEmbedding 可设 text_type=document 或 query

##### 限制：单条 ≤8192 tokens，batch size ≤10

#### 本地 HuggingFace：BAAI/bge-small-zh-v1.5

##### 本仓库 semantic_search 默认走这条，中文友好

##### 首次运行会下载权重，约百 MB 级

##### 可换 bge-base-zh-v1.5，效果更好、更吃内存

#### 本地 Ollama：nomic-embed-text / qwen3-embedding:0.6b

##### 适合数据不出本机

##### LlamaIndex 用 llama-index-embeddings-ollama

#### 必须遵守的对照原则

##### 写入和查询必须同一模型、同一维度，否则空间对不上

##### 换模型就要重建整个向量库，不能混着用

##### 选型可看 MTEB Leaderboard，中文优先看 C-MTEB

### 6 代码详解：项目里怎么挂 Embedding

#### Settings.embed_model = DashScopeEmbedding(...) 或 HuggingFaceEmbedding(...)

##### 意思：告诉 LlamaIndex「以后所有向量化都用这个模型」

##### DashScope：云端千问，要 api_key；text_type='document' 表示按文档侧编码

##### HuggingFace：本地下载 BAAI/bge-small-zh-v1.5，首次会拉权重

##### 为什么设全局：分块语义切分、写入、检索都会自动用同一模型，避免空间不一致

#### 写入 vs 查询

##### 有的云端模型区分 document / query 两种编码，别混用

##### 本仓库默认本地 bge：读写都走同一个 HuggingFaceEmbedding，简单不容易错

##### 换模型必须重建向量库，旧向量和新模型不在同一空间

## 05 向量数据库
飞书文档：03-大模型应用基础--向量数据库

### 术语定义（本章必背）

#### 向量数据库：专为高维向量存储与近邻检索优化的数据库

#### 向量检索 / 语义搜索：按向量相似度找「意思接近」的内容，而非纯关键词匹配

#### KNN / 精确近邻：对全部向量算距离再取最近，准但慢 O(N)

#### ANN（Approximate Nearest Neighbor）：近似近邻，牺牲少量精度换大幅速度

#### HNSW：基于多层小世界图的常见 ANN 索引结构

#### IVF：倒排文件式向量索引，先粗分桶再在桶内精查

#### Latency（延迟）：单次查询响应时间

#### Throughput / QPS：每秒能处理的查询数

#### Recall@K：返回的前 K 个里包含真正近邻的比例

#### FAISS：Meta 开源的向量相似度检索库（偏算法引擎）

#### Chroma：开发友好的向量库，本项目默认持久化方案

#### Collection：向量库里的一个命名集合/表

#### 持久化 Persist：把索引落盘，重启不丢

#### 元数据过滤：检索时可按文档属性（来源、时间等）硬过滤

### 第一部分 向量检索基础

#### 从传统搜索到向量搜索

##### 传统关键词/LIKE：不懂笔记本电脑和电脑相似

##### 多语言障碍：难跨语言搜

##### 语境缺失：不懂上下文

##### 向量方案：文本图像等变成高维数值向量，在空间里算相似性，才是语义理解

#### 向量：数学上有大小有方向；机器学习里是数据的数值化表示

#### 为什么要专门的向量数据库

##### 课上问题：100 万个 128 维向量里找最像的 10 个

##### 传统 SQL 按距离排序：要对全部向量算一遍，复杂度 O(N)

##### 高维空间里普通索引几乎帮不上忙

##### 近似搜索 ANN：牺牲少量精度换大幅速度

##### 专用索引：HNSW、IVF 等高维结构

##### 性能优化：GPU 加速、批量处理

#### 核心指标 讲义表

##### 查询延迟 Latency：单次响应时间。毫秒级适合实时，秒级适合离线批处理

##### 吞吐量 Throughput：每秒查询数 QPS，衡量并发

##### 准确率 Accuracy：近似搜和精确搜有多接近。Recall@K=前K个里包含真正近邻的比例

##### 存储：内存占用、索引磁盘大小

### 第二部分 FAISS

#### 简介

##### Facebook AI Similarity Search，2015 年起，解决高维向量快速检索

##### C++ 开发，提供 Python 接口

##### 支持平面、哈希、树形等索引，余弦、欧氏等度量

##### 场景：图像检索、文本匹配、视频推荐

##### 特点：可 GPU、单机十亿级、算法多、MIT 许可、被 Milvus Qdrant 等采用

#### 安装与第一个程序

##### 初学者：pip install faiss-cpu，或 conda-forge

##### 有 NVIDIA+CUDA 再装 faiss-gpu

##### 课上示例：10000 条、每条 128 维 float32 矩阵

##### 代码详解 对照 918.py IndexFlat

###### vectors = np.random.random((10000, 128)).astype('float32')

###### 意思：造 10000 条假向量，每条 128 维，当作「库里的文档向量」

###### astype('float32')：FAISS 只吃 float32，float64 会报错或行为怪异

###### index = faiss.IndexFlatL2(128)

###### 意思：建一个「暴力精确搜」索引，距离用欧氏距离 L2

###### 128 必须等于向量列数，对不上会直接报错

###### index.add(vectors)

###### 意思：把全部向量装进索引

###### 装完看 index.ntotal，应等于 10000

###### query 形状必须是 (1, 128)

###### 意思：一次查询也可以多条，所以第一维是「几条查询」

###### 传一维 (128,) 会维度错误；要用 query.reshape(1, -1)

###### D, I = index.search(query, k=5)

###### D：距离矩阵，D[0][i] 越小（L2）越像

###### I：下标矩阵，I[0][i] 是第 i 名在原 vectors 里的行号

###### 拿原文：用下标去你自己保存的 documents 列表里取

###### 局限：Flat 不能单独改一条，要更新通常整库重建

#### 索引选型决策树

##### 不到 100 万：精度要极高用 IndexFlat，否则 IndexIVFFlat

##### 100 万到 1 亿：要极速用 IndexHNSW，否则 IVFFlat 保精度

##### 超过 1 亿：内存紧用 IndexIVFPQ 压缩，否则 IVFFlat 加 GPU

#### IndexFlat 精确索引

##### FlatL2：欧氏距离

##### FlatIP：内积/点积

##### 余弦：先 faiss.normalize_L2，再用 IndexFlatIP

##### 适用：小于约 10 万、要极高精确、当其他索引的精度基准

#### IndexIVFFlat 倒排文件索引

##### 把向量空间划成多个聚类中心 Voronoi 区域

##### 每个向量分到最近中心，查询只搜最近几个中心

##### 代码详解 对照 918.py IVF

###### quantizer = faiss.IndexFlatL2(dimension)

###### 意思：底层用精确索引当「量尺」，给 IVF 算哪个簇最近

###### index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)

###### 意思：把空间切成 100 个簇（倒排桶）

###### nlist 常取约 sqrt(N)；太小每桶太大，太大要扫的桶变多

###### index.train(vectors) 必须先做

###### 意思：用 k-means 找到每个簇的中心

###### 不 train 就 add/search 会报错，这是 IVF 和 Flat 最大差别

###### index.add(vectors) → index.nprobe = 10 → search

###### add：把向量丢进最近的簇

###### nprobe：查询时搜几个最近簇；越大越准越慢，=nlist 就接近暴力搜

###### search 返回值仍是 D 距离、I 下标，用法和 Flat 一样

##### nlist：聚类中心数，通常取 sqrt(N)。太小每簇太大；太大要查的簇变多

##### nprobe：查几个簇。1 最快最糙；等于 nlist 就变精确搜

##### 正向索引：文档→词，搜苹果要扫 100 万篇，O(N)

##### 倒排索引：词→文档，直接取倒排表，接近 O(1)，课上说可提速约 100 倍

##### FAISS 里用簇代替词，思想一样

#### IndexHNSWFlat 分层可导航小世界

##### 基于图的 ANN，灵感来自高速公路和六度分隔

##### 多层图：上层稀疏快速跳跃，下层密集精细搜索

##### 课上参数：M=16 每个节点最大连接数

##### efConstruction=200：建索引时候选队列，越大质量越高、建得越慢

##### efSearch=50：查询时候选队列，越大越准、越慢

##### 被 Milvus、Pinecone、Qdrant、Weaviate 等广泛使用

##### 当前多数系统默认推荐，精度和速度较均衡

#### 选型补充：IVF 系列更适合超大规模且资源受限；还要看延迟敏感度和运维能力

### 常见向量库对照

#### Milvus：HNSW、IVF_FLAT/PQ/SQ、FLAT；分布式，冲千亿级

#### Pinecone：托管，内部优化 HNSW，自动扩展

#### Weaviate：HNSW；关键词+语义混合，模块化嵌模型

#### Qdrant：HNSW、FLAT；Rust，高级过滤和地理查询

#### Chroma：默认 HNSW 类 ANN，也可设欧氏或余弦；轻量，偏 LLM，可嵌入式

#### Faiss：FLAT、IVF、HNSW、PQ、LSH；高性能库，可 GPU，偏研究与大规模实验

#### Elasticsearch 向量插件：HNSW，全文+向量企业混合搜

#### Deep Lake：多模态存储与流式检索

#### Vearch：云原生分布式，推理和推荐

### 第三部分 Chroma

#### 定位

##### 开源 AI 原生向量库，为 LLM 应用设计，强调好写、快集成

##### 设计哲学：4 个核心 API 覆盖主要操作

##### 可接 OpenAI、HuggingFace 等嵌入

##### 原生支持向量和元数据关联查询

##### 与 LangChain、LlamaIndex 集成顺

##### 安装：pip install chromadb，或 conda-forge

#### 四种操作串起来

##### 1 创建客户端，相当于连上一个数据库实例

##### 2 create_collection，类似关系库里的表

##### 3 add：documents + metadatas + ids

##### 4 query：用自然语言查最相似的几条

##### 代码详解 对照 918.py（Chroma 四步）

###### client = chromadb.PersistentClient(path='./chroma_data')

###### 意思：打开/创建一个落盘的向量库目录

###### 和 Client() 区别：进程关掉数据还在

###### collection = client.get_or_create_collection('kaoqin')

###### 意思：有同名集合就打开，没有就新建（入门最省事）

###### 集合 ≈ 关系库里的一张表

###### collection.add(ids=..., documents=..., metadatas=...)

###### 意思：写入原文；没传 embeddings 时库会自动向量化

###### 三个 list 必须等长：第 i 个 id 对应第 i 段文档

###### 只传 embeddings：跳过嵌入，适合你已经用千问算好向量

###### 同一 id 再 add 会 DuplicateID → 先 delete(ids=...)

###### res = collection.query(query_texts=['年假几天'], n_results=3)

###### 意思：把问句向量化，取最像的 3 条

###### 看结果：res['documents'][0] 是文本列表

###### res['distances'][0] 是距离（越小越像，具体含义看 hnsw:space）

###### res['metadatas'][0] 可拿来源、分类等

###### where={'category': '年假'}

###### 意思：先按元数据硬过滤，再在子集里做向量搜

###### 适合：只要某类制度、某年通知，减少噪声

#### 三种客户端

##### Client()：内存临时库，进程结束数据就没了

##### PersistentClient(path=./chroma_data)：落到磁盘

##### HttpClient(host, port)：连远程 chroma run 服务

#### 集合 Collection

##### 基本结构：向量 Embeddings + 原文 Documents + 元数据 Metadata + id

##### create_collection：新建，已存在会报错

##### get_collection：取已有集合，不存在会报错

##### get_or_create_collection：有则取、无则建，入门最常用

##### list_collections 可看库里一共有多少集合

##### 课上示例集合名：kaoqin 考勤、ruzhi 入职、liaofan 了凡四训

#### add 添加

##### ids 必填：唯一标识，去重和更新删除用；已存在默认跳过不覆盖

##### documents：原文，会按集合的嵌入函数自动转向量

##### 没自定义嵌入时，默认 all-MiniLM-L6-v2，约 384 维

##### metadatas：键值对，供 where 过滤。常见 key：source category author url page date

##### embeddings：也可直接塞预计算向量，适合已用千问或 OpenAI 算好的场景

#### query 查询

##### query_texts：查询文本，自动转向量，可一次多个查询

##### query_embeddings：直接给向量，与 query_texts 二选一

##### n_results：每个查询返回几条，默认 10

##### where：按 metadata 过滤，如 category=年假，page>=5，$and 组合

##### where_document：$contains 对原文做包含匹配

##### include：documents / metadatas / embeddings / distances，默认文档、元数据、距离

##### 课上流程：问句向量化 → 和库中算 L2 → 取 Top-K

#### 距离函数 hnsw:space

##### 默认 L2 欧氏距离

##### 创建集合时 metadata 指定，三选一：l2、cosine、ip

##### 写法：metadata={"hnsw:space": "cosine"}

##### 一旦创建不能改，再改会 ValueError

#### 自定义嵌入

##### OpenAIEmbeddingFunction，模型如 text-embedding-ada-002

##### 千问：用 OpenAI 兼容接口桥接 DashScope，text-embedding-v3

##### 查询必须和写入用同一套嵌入，否则向量不在同一空间，检索会乱

#### 服务器模式

##### chroma run --path 存储路径 --host ip --port 端口，相当于启动 MySQL

##### 课上例子：chroma run --path .\chroma_data02\ --host 127.0.0.1 --port 8989

##### Python 用 HttpClient 连上去，再 list、add、query

#### 更新与删除

##### update：可改文档内容和元数据

##### delete：可按 id 列表删，也可先按元数据条件查出再删

### 第四部分 实战项目

#### 目标：自然语言查询，返回最相关文档

#### 技术栈：Chroma + 千问 DashScope 嵌入 + FastAPI

#### 依赖：pip install chromadb fastapi uvicorn

#### 阶段一 建库

##### 加载 → 分块 → get_embedding 向量化

##### add_documents：原文进 self.documents，向量进索引

#### 阶段二 检索 search

##### 问题向量化

##### 索引返回相似向量下标

##### 用下标从 self.documents 取原文

##### 原文+问题再交给大模型回答

#### 课上测试：GET /search?q=向量搜索工具&k=3

#### 参考：faiss.ai 、 docs.trychroma.com

#### 完整落地已迁到 semantic_search，代码详解见第 06 章

##### 启动：python -m semantic_search → http://127.0.0.1:8001/

##### 只检索：GET /search?q=...&k=3

##### 检索+生成：GET /query?q=...

## 06 Native RAG（基础RAG）
飞书文档：01-Native_RAG（基础RAG）https://ecnwvcdzorsp.feishu.cn/docx/WAyydkEX2o81xAxFkn1cJRqqnnY

### 术语定义（本章必背）

#### Native RAG：基础 RAG 流水线——加载→分块→向量化入库→检索 Top-K→拼 Prompt→生成

#### Indexing（索引/入库）：文档切块并 Embedding 后写入向量库

#### Search / Retrieval：问题向量化后召回最相关块

#### Generate：把检索块作为上下文，由 LLM 生成回答

#### Chunk / 分块：把长文档切成适合检索的小段

#### SentenceSplitter：按句子/长度切块（本仓库默认之一）

#### TokenTextSplitter：按 token 数切块

#### SemanticSplitter：按语义相似度变化点切块

#### LlamaIndex：本课程主用的 RAG 编排框架

#### VectorStoreIndex：LlamaIndex 中基于向量库的索引对象

#### RetrieverQueryEngine：检索器 + 响应合成器组成的问答引擎

#### ChatEngine：带多轮记忆的 RAG 对话引擎

#### Top-K / similarity_top_k：返回相似度最高的前 K 条

#### 数据质量：垃圾进垃圾出——脏文档会直接拖垮 RAG 效果

#### 本项目入口：python chroma文档管理/run.py → http://127.0.0.1:8003/

### 一、技术原理

#### 1 为什么需要RAG
大模型的局限性

##### 知识时效性：无法实时获取最新数据，如 GPT-3 知识停在 2021

##### 幻觉问题：基于概率生成，Prompt 上限即回答有效性上限

##### 垂直领域覆盖不足：医疗等行业资料多为机密，通用模型吃不到

#### 2 RAG原理（Native RAG 三步）

##### Indexing：文档向量化，写入向量库建索引

##### Search：问题 Embedding 后检索最相关文档片段

##### Generate：把片段塞进 Prompt，由 LLM 生成可读回答

### 二、RAG流程

#### 大致分三个阶段：数据准备 → 检索 → 生成（讲义有总流程图）

### 三、数据准备阶段

#### 1 数据准备

##### 原始数据常有：格式难识别、内容不一致、不完整、不合法

##### 第一性原理：加上下文能提准确性，但数据质量差会负向影响

#### 2 向量化 Embedding

##### 向量检索按语义相似度找内容，保障输出有效性

##### 选型可参考 MTEB Leaderboard：huggingface.co/spaces/mteb/leaderboard

##### 本地下载模型

###### HuggingFace：可设 HF_ENDPOINT=https://hf-mirror.com 镜像

###### hf download BAAI/bge-base-zh-v1.5 --local-dir ...

###### 环境变量 HF_HOME / TRANSFORMERS_CACHE 统一缓存目录

###### 国内更快：pip install modelscope 后 modelscope download

#### 3 知识存储

##### 向量化后写入向量库，不要只把向量扔内存里

##### 必须建立 embedding ↔ chunk 原文的映射，检索到向量才能拿出文本

##### 再记下 metadata：来源文件、页码、切分方式，方便引用和过滤

##### 本仓库落盘目录：semantic_search/chroma_db

### 四、LlamaIndex 的 RAG

#### 1 LlamaIndex 简介

##### 1.1 介绍

###### 原名 GPT Index，面向 LLM 的数据开发与编排框架

###### 打通私有数据与通用大模型：加载→切分→向量化→检索→生成

###### 可用极少代码接入文档、数据库、API，快速做生产级 RAG

##### 1.2 核心概念速览

###### Document：一篇原始文档，带 metadata（来源、文件名）

###### Node：切出来的块，检索的基本单位

###### Index：把 Node 编成可检索结构，课上主要是向量索引

###### Retriever：只负责找回 Node，不生成答案

###### QueryEngine：检索 + 拼 Prompt + 调用 LLM，一次问答

###### ChatEngine：QueryEngine + Memory，多轮对话

#### 2 文档加载

##### 2.1 SimpleDirectoryReader

###### 核心包内置通用加载器

###### 自动识别 .txt .pdf .docx .csv .md 等

###### 可 input_dir + recursive + required_exts 加载整目录

###### 可 input_files=[...] 加载指定文件列表

###### load_data() 得到 Document 列表，可看 metadata 与 text 预览

##### 2.2 专用加载器 llama-index-readers-file

###### pip install llama-index-readers-file，20+ 种精细解析

###### PDF

###### PDFReader：轻量，底层 pypdf，适合纯文本

###### PyMuPDFReader：高性能，特性更多

###### UnstructuredReader：擅长表格、标题等复杂结构

###### 依赖可选：unstructured[pdf]、PyMuPDF

###### 用 SimpleDirectoryReader 的 file_extractor={'.pdf': parser}

###### Word / PPT / CSV

###### DocxReader、PptxReader、PandasCSVReader

###### Word 常需 pip install docx2txt

###### Markdown / HTML / 代码 / 笔记

###### MarkdownReader：保留标题层级

###### HTMLTagReader、IPYNBReader、XMLReader

###### IPYNB 可装 nbconvert

###### 加载器选择：按格式选专用；通用杂糅文件先用 SimpleDirectoryReader

#### 3 文档分块

##### 3.1 基础切分器

###### TokenTextSplitter

###### 按 Token 数切分，严格控制上下文窗口

###### 先用 separator（如句号）切；超长再用 backup_separators

###### 仍超长则硬截断；最后合并并加 overlap

###### SentenceSplitter（默认推荐）

###### 优先保证句子完整，同时控制 chunk_size

###### 步骤1：paragraph_separator（默认\n\n\n）按段落切

###### 步骤2：secondary_chunking_regex 切成完整句子

###### 步骤3：累加句子直到接近 chunk_size 成一块

###### 步骤4：下一块带上上块末尾 overlap 句子

###### 单句本身 > chunk_size 时可能报错，需预处理

##### 3.2 语义切分 SemanticSplitterNodeParser

###### 先分句 → 组合成组合句 → Embedding 算相似度 → 按阈值切

###### buffer_size=1：组合句约含前后各1句+当前句

###### breakpoint_percentile_threshold 越高，切得越粗

###### 中文需自定义 chinese_sentence_splitter（。！？!?\n）

###### 可配 DashScopeEmbedding(text-embedding-v3)

###### 注意：需过滤空文本 clean_empty_text；参数要调优

##### 3.3 选择建议

###### 常规 RAG：SentenceSplitter，平衡上下文与精度

###### 长文要语义连贯：SemanticSplitterNodeParser

###### 代码库：CodeSplitter，避免切断函数中间

###### 句子级精确检索：SentenceWindowNodeParser + MetadataReplacementPostProcessor

#### 4 文档向量化并存储 Embedding

##### pip install llama-index-vector-stores-chroma

##### Settings.embed_model = DashScopeEmbedding(model_name=text-embedding-v3, text_type=document)

##### SimpleDirectoryReader 加载 → SentenceSplitter 分块

##### Chroma PersistentClient + get_or_create_collection

##### ChromaVectorStore → StorageContext → VectorStoreIndex(nodes)

##### 执行顺序：Index 遍历 node → embed_model 生成向量 → collection.add 写入

##### 千问限制：单条 ≤8192 tokens；batch size ≤10

#### 5 检索与大模型回复

##### 重新挂 Settings.embed_model（须与建库同一模型）

##### PersistentClient → get_collection → ChromaVectorStore

##### VectorStoreIndex.from_vector_store 恢复索引

##### as_query_engine：一次性检索+生成

##### as_chat_engine(chat_mode=condense_plus_context) + ChatMemoryBuffer：多轮

##### 项目落地：semantic_search 的 /search /query /chat /ingest

#### 6 对照本仓库 semantic_search 怎么用
讲义流程已接到 FastAPI + 前端

##### Indexing：前端上传 /upload 或 POST /ingest → data 目录 → 分块入库

##### 分块可选：sentence（推荐）/ token / semantic

##### Embedding：默认本地 bge-small-zh；有千问 Key 可改 dashscope

##### Search：前端「语义搜索」或 GET/POST /search

##### Generate：前端「一次性问答」/query、「多轮问答」/chat

##### 持久化目录：semantic_search/chroma_db

##### 启动：python chroma文档管理/run.py → http://127.0.0.1:8003/

#### 7 代码详解 engine.py / main.py（chroma文档管理）
对应 chroma文档管理/semantic_search/。每条：代码 → 它在流水线哪一步 → 得到什么。

##### 启动 lifespan

###### SemanticSearchEngine()

###### 意思：一次性挂好 Embedding、LLM、Chroma、空/旧索引

###### 缺 API Key 时引擎可为 None，页面能开，/query 会 503

###### seed_if_empty()

###### 意思：库是空的才灌示例文档 + 扫描 data 目录

###### 为什么：第一次启动就能搜，不用手工入库

##### 入库：文件 → 块 → 向量

###### SimpleDirectoryReader(...).load_data()

###### 意思：把 PDF/TXT/MD 等读成 Document 列表

###### 每个 Document 带 text + metadata（文件名等）

###### clean_empty_text(docs)

###### 意思：丢掉空内容，避免后面 embedding 报错

###### splitter.get_nodes_from_documents(docs)

###### 意思：切成 Node（检索的基本单位=chunk）

###### sentence/token/semantic 三种切法由 _splitter(mode) 决定

###### index.insert_nodes(nodes)

###### 意思：对每个 Node 调 embed_model 得向量，再写入 Chroma

###### 之后要 _reset_chat_engines()：知识变了，旧多轮引擎不能继续用

##### 三种分块器（构造时在说什么）

###### SentenceSplitter(chunk_size, chunk_overlap, ...)

###### 意思：尽量按句子边界凑满约 chunk_size 个 token

###### overlap：下一块带上上块尾巴，防止关键句被切断

###### TokenTextSplitter(...)

###### 意思：严格按 token 数切，控制上下文更硬

###### SemanticSplitterNodeParser(buffer_size=1, breakpoint=95, ...)

###### 意思：算相邻句向量相似度，主题一变就切开

###### 更慢但语义更整；中文要自定义分句函数

##### 只检索 search（不调大模型）

###### retriever = index.as_retriever(similarity_top_k=k)

###### 意思：只要「找片段」的工具，不做生成

###### results = retriever.retrieve(query)

###### 意思：返回 NodeWithScore 列表

###### item.node.get_content() → 原文；item.score → 相似度

###### 对应接口：GET/POST /search

##### 一次性问答 query

###### engine = index.as_query_engine(similarity_top_k=k)

###### 意思：检索 + 拼 Prompt + 调 LLM，一条龙

###### response = engine.query(question)

###### str(response) → 给用户的答案文字

###### response.source_nodes → 引用了哪些片段（可展示来源）

###### 对应接口：GET/POST /query

##### 多轮问答 chat

###### as_chat_engine(chat_mode='condense_plus_context', memory=..., ...)

###### condense_plus_context 意思：先把「结合上文的问题」改写成独立问句，再检索

###### 为什么：用户说「那扣多少」时，检索要用改写后的完整问题

###### memory 按 session_id 复用

###### 意思：同一浏览器会话共用一块记忆

###### 换 session_id = 新对话；对应 POST /chat

##### 重启后如何找回索引

###### collection.count() > 0 → VectorStoreIndex.from_vector_store(...)

###### 意思：Chroma 里已有向量，挂上去就能搜，不必重切分

###### 空库 → VectorStoreIndex(nodes=[], storage_context=...)

###### 意思：先占个空索引，以后 insert_nodes 再往里填

###### 铁律：Settings.embed_model 必须和建库时同一个

## 07 Advanced RAG（高级RAG）
飞书：Advance RAG。答辩重点：Native→Advanced 差在哪；检索前/中/后各治什么病；HyDE/扩展/分解/重排怎么选。

### 〇、答辩开场 60 秒说清

#### 一句话定义

##### Advanced RAG = 在 Native RAG 的「检索→生成」两端，对查询、召回、精排、上下文使用做系统优化

##### 不是换一个更强的 LLM，而是把「送进模型的原材料」做对

#### 和 Native 的对比（老师最爱问）

##### Native：用户原句 → 向量 Top-K → 直接塞 Prompt → 生成

##### Advanced：先改查询/多路召回 → 再重排压缩 → 再带约束生成

##### Native 像小学生翻书找关键词；Advanced 像会改题意、会对照目录、会划重点的学生

##### 代价：延迟↑、费用↑、链路更复杂；收益：召回↑、噪声↓、幻觉↓

#### 闭环四问（按时间线背）

##### 查什么（Pre）：改写 / 扩展 / HyDE / 分解 / 分块与元数据

##### 去哪查（Retrieval）：混合检索、多路召回、路由不同索引

##### 查得准（Post 前半）：重排序，把最相关的顶到前面

##### 怎么用（Post 后半）：压缩、动态 Top-K、引用约束 Prompt

#### 工业界优先三件套（性价比排序）

##### ① 查询改写或 HyDE：治「问法和文档不像」

##### ② 混合检索（向量+BM25）：治「专名/编号搜不到」

##### ③ 重排序 rerank：治「召回有了但前几名不相关」

##### 先别一上来上 GraphRAG / Agent，Native 没稳先别叠高级模块

### 术语定义（Advanced 总览必背）

#### RAG（Retrieval-Augmented Generation）

##### 定义：检索增强生成——先从外部知识库取相关资料，再让 LLM 基于资料生成答案

#### Native RAG

##### 定义：最简流水线：提问→向量检索 Top-K→拼 Prompt→生成，中间少优化

#### Advanced RAG

##### 定义：在 Native 上对检索前/中/后系统优化，形成可组合的增强链路

#### Pre / Mid / Post-retrieval

##### Pre：优化问句与索引准备（查什么）

##### Mid：优化召回算法与通道（怎么查）

##### Post：优化已召回材料再喂模型（怎么用）

#### Embedding（嵌入）

##### 定义：把文本映射到向量空间，使语义相近的文本距离更近

#### Top-K

##### 定义：检索返回相似度最高的前 K 条候选

#### Self-RAG

##### 定义：生成过程中自我决定是否检索、资料好不好、答案有无依据（见第 11 章）

#### Corrective RAG（CRAG）

##### 定义：评估检索质量，差则改写/外搜纠正后再生成（见第 12 章）

#### RAG-Fusion

##### 定义：多查询并行检索 + RRF 融排名的完整打法

#### Agentic RAG

##### 定义：由 Agent 规划检索步骤与工具调用的灵活 RAG 形态

#### GraphRAG

##### 定义：基于实体关系图做检索/摘要，适合多跳与全局主题

### 一、检索前优化（Pre-retrieval）
目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章；检索中见第 09 章。

#### 查询重写 Query Rewriting

##### 做什么：口语/指代不明 → 检索友好、术语齐全的问句

##### 例子：「上次那个产品的安全规范」→「某某产品 最新 安全规范 文档」

##### 治的病：指代、口语、缺关键词导致向量飘

##### 风险：改写过头偏离原意 → 可 include_original 保留原句一起搜

##### 口述口诀：先把题读懂，再去翻书

#### 查询扩展 Query Expansion / Multi-Query

##### 做什么：同一意图生成多个近义/不同句式变体，并行检索再合并

##### 治的病：用户用词不专业、同义不同词、召回偏低

##### 合并常用 RRF，避免某一路分数尺度不同抢排名

##### 和改写区别：改写≈改成更好的一句；扩展≈变成多句一起查

#### HyDE 假设文档检索

##### 做什么：先让 LLM 写一篇「假想答案」，用这篇去向量库搜

##### 为什么有效：知识库存的是「答案体」文档，假想答案和它更像，短问句不像

##### 适合：问句极短、用户表述和文档风格差很大

##### 不适合：事实极严、模型瞎编会带偏检索（务必 include_original）

##### 代价：多一次 LLM，延迟和费用都上去

##### 口述对比：改写是改问题；HyDE 是先编一份答案再去找真答案

#### 子查询分解 Decomposition

##### 做什么：复杂题拆成多个原子子问题，分别检索再综合

##### 例子：比较 A/B 2023 营收增长 → 分别查营收 → 算增长率 → 再对比

##### 治的病：一次检索塞不下的多跳/比较题

##### 和扩展区别：扩展是近义变体；分解是不同侧面的子问题

#### 文档侧（离线也算检索前）

##### 分块：句子/语义/父子块，决定「能不能被命中」和「命中后有没有上下文」

##### 文档增强：摘要、关键词、假设问题一并入库，提高可检索性

##### 元数据：时间/分类/来源，给过滤和引用用

### 二、检索中优化（Retrieval）
飞书：03-检索中优化（Retrieval）。目标：提升召回率与相关性。细节专训见第 09 章。

#### 先搞清：检索 vs 召回；召回率 vs 精确率

##### 检索召回 = 从海量知识库里，把和用户问题相关的内容找出来

##### 检索：拿着问题去向量库/文档库搜索

##### 召回：把匹配度高的片段捞回来

##### 召回率 Recall

###### 该找到的相关内容，有没有全部找出来

###### 高：相关的基本都捞到，不漏；低：很多相关文档没搜到

##### 精确率 Precision

###### 召回来的内容里，有多少真有用、不跑偏

###### 高：捞回来都很相关；低：一堆噪音

##### 检索中优化主攻：先抬召回率（别漏），再靠融合/后重排抬精确率

#### 混合检索 Hybrid Search（同库多算法）

##### 问题：单一检索方式总有盲区

##### 公式一句话：混合检索 = 稠密向量 + 稀疏向量 → 结果融合 → 取长补短

##### 稠密 vs 稀疏（口述）

###### 稠密：几乎每维都有值，「按意思翻译」；语义/同义强（笔记本≈电脑）

###### 稀疏：多数为 0，「按关键词翻译」；专名/编号/错误码强

###### 同一份文档两种翻译官 → 两套排名互补

##### 场景口诀（登录超时）

###### 只在「产品文档」这一个数据源里搜

###### 向量：找到 session过期 / 身份验证失败 等同义

###### BM25：精确命中「登录超时」字眼

###### 再用 RRF 等融合两路排名

##### 代码落点：标准 RAG 第 4 步「检索召回」——做一个更强更准的召回

##### LlamaIndex：同一份 nodes → vector_retriever + BM25Retriever → QueryFusionRetriever

##### 中文坑：BM25 默认英文分词无效，必须 tokenizer=jieba（或 language=chinese 组合）

#### RRF 倒数排名融合（常考）

##### 全称 Reciprocal Rank Fusion

##### 公式：score(doc) = Σ 1/(k + rank_i)，k 常取 60

##### k 的作用：缓和「第一名」过度碾压，避免排名靠前波动过大

##### 算例（讲义）

###### 文档A：稠密第2 + 稀疏第5 → 1/62 + 1/65 ≈ 0.0315

###### 文档B：稠密第1 + 稀疏第20 → 1/61 + 1/80 ≈ 0.0289

###### 结论：A > B——单路第一不如两路都靠前均衡

##### 关键优点：不要求各路原始分数同一量纲（cosine 0~1 vs BM25 0~∞）

##### LlamaIndex：mode='reciprocal_rerank'；加权归一化则用 relative_score

#### 多路召回 Multi-channel（多源多通道）

##### 问题：单一索引/单一字段覆盖不全

##### 定义：多个独立检索通道 → 各自召回 → 去重融合 → 扩大覆盖面

##### 一句话：多条赛道先各自捞一批候选，保召回率、少漏

##### 四步流程

###### ① 准备多路原始文档（技术库/FAQ/社区/工单…）

###### ② 每路按「要解决的问题」选索引：语义用稠密，术语用 BM25

###### ③ 同一用户问题各路出 Top-K

###### ④ 融合得最终 Top-N：RRF（首选）/ 归一化加权 / 轮询 Round-Robin

##### 选型注意

###### 不是看文档长短，而是看这一路要治什么病

###### FAQ 短、关键词强 → 常配 BM25；长文/口语 → 稠密向量

###### 实践中一路里还可再套混合检索（见嵌套架构）

##### 代码：tech/faq/community 三路 Retriever + QueryFusionRetriever（可 relative_score 加权）

##### 同样落在 RAG 第 4 步检索召回

#### 混合检索 vs 多路召回（别混！）

##### 混合：横向不变、纵向加深——同一数据源，两种算法互补

##### 多路：纵向可单算法、横向扩源——多个数据源一起搜

##### 工业嵌套（常一起用）

###### 外层多路召回：产品文档 / 工单 / 规范 / FAQ

###### 内层每路混合检索：向量 + BM25 + RRF

###### 最后融合排序 + 去重

##### 口诀：多路=横向扩数据源；混合=纵向抬单源质量；不是互斥选项

#### 进阶略知：SPLADE / ColBERT

##### SPLADE：学出来的稀疏向量，比纯 BM25 多一点语义

##### ColBERT：token 级交互（MaxSim），更细但更吃存储算力

##### 答辩：知道「单向量会丢细粒度」即可

### 三、检索后优化（Post-retrieval）
飞书：04-检索后优化（Post-retrieval）。目标：召回之后、喂 LLM 之前，做重排+精简+重排版。细节专训见第 10 章。

#### 位置与入口

##### 标准 5 步：加载→分块→入库→检索召回 →【本章】→ 喂给大模型

##### LlamaIndex：统一用 Node Postprocessor，串在 node_postprocessors=[...]

##### 多个后处理器按列表顺序逐级加工召回 nodes

#### 重排序 Re-ranking（粗排+精排）

##### 定义：对召回候选再用更准更贵的模型二次打分，把最相关顶到前面

##### 超市口诀：先快速抓一车，再仔细挑最好的放最上面

##### Bi-Encoder 双塔粗排：快，文档向量可预计算，精度一般

##### Cross-Encoder 交叉精排：query+doc 一起进模型，准但慢，只打几十~几百条

##### 工业标配：Top-20~100 粗召回 → rerank → Top-3/5 给 LLM

##### 讲义实现：DashScopeRerank(qwen3-rerank) 或本地 SentenceTransformerRerank

#### 上下文压缩 Contextual Compression

##### 问题：片段里往往只有一两句有用，整段硬塞浪费 token 还易幻觉

##### 一句话：重排管「哪些片段」；压缩管「片段里留哪几句」

##### LlamaIndex：SentenceEmbeddingOptimizer（按句与查询算相似度裁剪）

##### 常用：percentile_cutoff=0.5 或 threshold_cutoff；中文可自定义切句

#### 长上下文重排 Long-Context Reorder

##### Lost in the Middle：模型对首尾记得清，中间易丢

##### 做法：最相关放头尾，次相关塞中间——只改顺序不改内容与选集

##### LlamaIndex：LongContextReorder()，通常接在 reranker 之后

#### 三件套串联

##### ① Rerank 精排 → ② SentenceEmbeddingOptimizer 压缩 → ③ LongContextReorder 排版

##### 生成侧仍要：仅依据资料回答 + 引用编号（最后一道闸）

### 四、进阶范式对比（别混）

#### Self-RAG

##### 模型自己决定：要不要检索、检索结果够不够、要不要再查

##### 治的病：过度检索（闲聊也查）和检索不足

##### 专训见第 11 章（四种反思令牌 Retrieve/ISREL/ISSUP/ISUSE）

#### Corrective RAG（CRAG）

##### 先评估检索质量：相关 / 模糊 / 不相关

##### 差则纠正：换查询或转外部网页搜索，再生成

##### 治的病：知识库覆盖不全、内部库答不了的新资讯

##### 专训见第 12 章（评估器 + 精炼 + 外搜 / 本仓库库内修正版）

#### RAG-Fusion

##### = Multi-Query + 多路检索 + RRF 融合

##### 重点在「融排名」，不是融原始分数

#### Adaptive / Graph / Agentic

##### Adaptive：按难度动态选策略深度

##### GraphRAG：实体关系，适合多跳与全局摘要

##### Agentic：Agent 规划检索与工具，最灵活也最难控

#### 一张对比表（口述用）

##### Self-RAG：管「查不查」

##### Corrective：管「查错了怎么办」

##### RAG-Fusion：管「多问法怎么合成一张榜」

##### Rerank：管「榜上谁该排第一」

### 五、排障决策树（老师问「效果不好怎么办」）

#### ① Native 不稳：先查 Embedding 是否一致、分块是否切断、Top-K 是否乱

#### ② 问句和文档不像：加查询改写或 HyDE

#### ③ 专名/编号搜不到：加 BM25 混合检索

#### ④ 相关材料在后面几名：加 rerank

#### ⑤ 材料对但答案飘：压 Prompt、加引用、压缩上下文

#### ⑥ 比较/多跳题：子查询分解

#### ⑦ 本仓库现状：已叠混合检索/后处理/CRAG；Self-RAG 四令牌仍可按需加

### 六、和本仓库 / 第 08~12 章的关系

#### 第 07 章：Advanced 全景（前/中/后 + 进阶范式）

#### 第 08 章：检索前专训（改写/HyDE/分块…）

#### 第 09 章：检索中专训（混合/多路/RRF）

#### 第 10 章：检索后专训（Rerank/压缩/长上下文重排）

#### 第 11 章：Self-RAG 专训（查不查 + 生成反思）

#### 第 12 章：CRAG 专训（查错了怎么办 + 库内/外搜修正）

#### 第 13 章：chroma文档管理 全链路文件/API/开关对照

#### 第 14 章：RAG 评估（Hit/MRR + Faithfulness 等，量化优化）

#### 第 15 章：Modular RAG（模块化编排 + 配置驱动，对齐飞书 01）

#### 第 16 章：知识图谱理论 + Neo4j/Cypher

#### 第 17 章：GraphRAG 使用（PropertyGraphIndex + 抽取器）

#### 第 18 章：多模态 RAG（Chinese-CLIP / 图文检索）

## 08 检索前优化（Pre-retrieval）
每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。

### 〇、总览：方法地图

#### 查询侧：清洗 → 澄清 → 重写 / 扩展 / HyDE / Step-Back / 分解

#### 文档侧（离线）：分块 → 元数据 → 增强 → 多表示 / 路由规则

#### 原则：先判断病症，再选一种方法；不要一次全开

### 术语定义（本章必背）

#### Pre-retrieval（检索前优化）：进入检索前，优化「问什么」和「库怎么建」

#### 查询清洗：去口语废话与标点噪声，并做术语标准化

#### 查询重写：把口语/模糊问题改成更适合检索的表达，保留原意

#### 查询扩展：生成多个同义变体并行检索再合并，抬召回

#### HyDE：先生成假想答案文档再拿去向量检索（假想文不当事实引用）

#### Step-Back：把具体问题先退成更宽泛背景问题

#### 查询分解：复杂多跳/比较题拆成原子子问题分别检索再综合

#### Chunking（分块）：长文切成适合 embedding 与召回的片段

#### Overlap：相邻块保留重叠，减轻边界切断语义

#### 父子块/Small-to-Big：小块命中，返回父级大上下文

#### 元数据 Metadata：标题/时间/来源/权限等，供过滤与引用

#### 意图路由：按问题类型选择不同索引或工具

### 方法1：查询文本清洗

#### 适用：问题里废话多、口语多、术语不统一

#### 输入

##### 原始用户问题字符串

##### 可选：公司术语表（俚语→标准词）

#### 分步分解

##### Step1 去口语：删「帮我看看」「那个」「嗯啊」等无信息词

##### Step2 去标点噪音：多余空格、表情、重复符号

##### Step3 术语标准化：查表替换（电脑→笔记本电脑；年假→带薪年休假）

##### Step4 实体抽出：产品名、日期、工号单独列出（可给 BM25 用）

##### Step5 得到「干净查询」再进入改写或直接 embedding

#### 输出

##### clean_query：清洗后的问句

##### entities：抽出的关键词列表（可选）

#### 完整例子

##### 输入：嗯那个帮我看看请假咋扣钱啊???

##### Step1-2 后：请假咋扣钱

##### Step3 后：请假 如何 扣款

##### entities：['请假','扣款']

### 方法2：澄清反问

#### 适用：缺实体、多意图、指代不明（上次那个、这个）

#### 输入

##### 原始问题 + 可选多轮历史

#### 分步分解

##### Step1 判断是否模糊：缺类型？缺时间？有指代？多意图？

##### Step2 若清晰：跳过，进入重写/检索

##### Step3 若模糊：生成 1 个澄清问题返回前端，本轮先不检索或只轻量搜

##### Step4 用户补充后，拼成「完整问题」= 原问题 + 用户选择

##### Step5 用完整问题再走清洗/重写/检索

#### 输出

##### 分支A：clarify_question（反问文案）

##### 分支B：resolved_query（澄清后的完整查询）

#### 完整例子

##### 输入：请假扣钱吗

##### Step1：缺假期类型 → 模糊

##### Step3 反问：请问是事假、病假还是年假？

##### 用户答：事假 → resolved_query=事假是否扣钱及扣款规则

### 方法3：查询重写 Query Rewriting

#### 适用：口语、指代、缺关键词，但意图基本单一

#### 输入

##### clean_query（最好先清洗）

##### 可选：对话历史（用来解析「那个」「上次」）

#### 分步分解

##### Step1 准备改写 Prompt：角色=检索改写助手；只输出改写句；不解释

##### Step2 约束：补全实体、保留原意、可加同义术语、不要编造不存在的产品名

##### Step3 调 LLM（低温 0~0.3）得到 rewritten_query

##### Step4 用 rewritten_query 做 embedding

##### Step5（推荐）原句也 embedding，两路检索结果合并，防改歪

##### Step6 合并后的片段再交给生成

#### 输出

##### rewritten_query：检索用问句

##### 可选：retrieval_queries = [原句, 改写句]

#### 完整例子

##### 输入：上次那个产品的安全规范更新了吗

##### 历史里「那个产品」= 智能手表 X1

##### 改写：智能手表X1 安全规范 是否更新 最新版本

##### 操作：改写句检索 + 原句检索 → 合并 Top 片段 → 生成

#### LlamaIndex 落点

##### 自定义 BaseQueryTransform._run 里调 LLM

##### 或 TransformQueryEngine(base_engine, transform)

### 方法4：查询扩展 Multi-Query

#### 适用：用词不准、同义多、怕漏召回

#### 输入

##### 一条核心问题（可已清洗/改写）

##### 参数 N：变体个数，常用 3~5

#### 分步分解

##### Step1 Prompt：生成 N 个检索变体，覆盖同义词、不同句式、上下位词；每行一个

##### Step2 解析 LLM 输出为列表 variants[1..N]

##### Step3 对每个 variant 分别向量检索，各取 Top-K

##### Step4 融合：RRF（按排名加分）或去重保留最高分

##### Step5 取融合后 Top-M 作为最终检索结果

##### Step6 再进入生成或重排

#### 输出

##### variants：N 条查询字符串

##### fused_nodes：融合后的文档块列表

#### 完整例子

##### 输入：请假怎么扣钱

##### 变体1：事假扣款规则

##### 变体2：病假是否带薪

##### 变体3：考勤制度 旷工 罚款

##### 变体4：年假提前离职如何折算

##### 四路检索 → RRF 合并 → 把事假/考勤相关块顶上来

#### LlamaIndex 落点

##### QueryFusionRetriever(..., num_queries=4, mode='reciprocal_rerank')

#### 和重写区别：重写≈改成更好的一句；扩展≈变成多句一起查

### 方法5：HyDE 假设文档检索

#### 适用：问句很短，或用户说法和文档风格差很大

#### 输入

##### 用户原问题

##### 同一套 Embedding 模型（必须与建库一致）

#### 分步分解

##### Step1 Prompt：请写一段「可能回答该问题」的文档片段，用说明文/制度口吻，不要对话

##### Step2 LLM 生成 hypo_doc（假想答案文档）

##### Step3 对 hypo_doc 做 embedding → hypo_vec

##### Step4 用 hypo_vec 在向量库 search Top-K → 得到真实文档块

##### Step5（强烈建议）对原问题再 search 一路

##### Step6 两路结果合并/去重

##### Step7 只用真实文档块生成答案；假想文档绝不当事实引用

#### 输出

##### hypo_doc：仅用于检索的中间产物

##### real_chunks：库里的真实片段

#### 完整例子

##### 输入：年假怎么算

##### Step2 假想：员工入职满一年享有带薪年假…按工龄递增…

##### Step4 用这段去搜 → 命中《考勤手册》年假条款真文

##### Step7 根据真文回答，并引用考勤手册

#### LlamaIndex 落点

##### hyde = HyDEQueryTransform(include_original=True)

##### engine = TransformQueryEngine(base_engine, hyde)

##### include_original=True 即自动做 Step5

#### 翻车点：假想胡编会带偏 → 必须保留原查询；多一次 LLM 更慢更贵

### 方法6：Step-Back 后退提问

#### 适用：细节问题缺少背景，直接搜容易碎片化

#### 输入

##### 具体问题 specific_q

#### 分步分解

##### Step1 Prompt：把具体问题改写成更抽象的背景/原理问题

##### Step2 得到 step_back_q

##### Step3 用 step_back_q 检索 → 背景材料 background_chunks

##### Step4 用 specific_q 检索 → 细节材料 detail_chunks

##### Step5 生成时同时塞入背景+细节，先背景后细节回答

#### 输出

##### step_back_q

##### background_chunks + detail_chunks

#### 完整例子

##### specific_q：Qwen2.5-7B 上下文窗口多长

##### step_back_q：主流大语言模型上下文窗口一般是什么量级

##### 先检索通识，再检索该型号说明，最后综合

#### 和 HyDE 区别：Step-Back 产出的是更宽的「问题」；HyDE 产出假想「答案文档」

### 方法7：子查询分解 Decomposition

#### 适用：比较题、多跳题、要多个信息点才能答

#### 输入

##### 复杂原问题 complex_q

##### 可选：多个 QueryEngine/工具（不同库）

#### 分步分解

##### Step1 LLM 分解：输出 JSON 子问题列表，每个可独立检索

##### Step2 校验：子问题是否原子、是否覆盖原问题所需信息

##### Step3 路由：每个子问题选哪个工具/索引（靠 tool description）

##### Step4 并发检索（或并发问答）得到 sub_results[]

##### Step5 综合 Prompt：根据子结果回答原问题，标注每条证据来源

##### Step6 输出最终答案 + 引用

#### 输出

##### sub_questions[]

##### sub_results[]

##### final_answer + citations

#### 完整例子

##### complex_q：比较 A/B 公司 2023 营收增长谁快

##### 子问1：A 公司 2023 营收是多少

##### 子问2：B 公司 2023 营收是多少

##### 子问3：A、B 相对 2022 的增长率

##### 分别检索年报片段 → LLM 算增长并对比 → 给出结论

#### LlamaIndex 落点

##### QueryEngineTool.from_defaults(..., description='查A公司财务')

##### SubQuestionQueryEngine.from_defaults(query_engine_tools=tools)

##### description 不准 → 路由错库（最常见失败）

#### 和扩展区别：扩展=同义多说法；分解=不同信息点

### 方法8：句子分块 SentenceSplitter

#### 适用：大多数中文文档的默认方案（离线建库）

#### 输入

##### Document 列表（load_data 得到）

##### 参数：chunk_size、chunk_overlap

#### 分步分解

##### Step1 按段落分隔符粗切（如多个换行）

##### Step2 再按句子边界细切（。！？等）

##### Step3 把句子累加，直到接近 chunk_size（按 token）

##### Step4 输出一块；下一块带上上块末尾 overlap 句子

##### Step5 所有块变成 Node，再 embedding 入库

#### 输出

##### nodes[]：每块含 text + metadata

#### 操作命令

##### splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)

##### nodes = splitter.get_nodes_from_documents(docs)

##### index.insert_nodes(nodes)

#### 调参：缺上下文 → 加大 chunk 或 overlap；检不中 → 块可能太大或要改查询

### 方法9：语义分块 SemanticSplitter

#### 适用：长文、主题多变，希望按语义边界切

#### 输入

##### 长文档 + embed_model（与检索同一套）

##### buffer_size、breakpoint_percentile_threshold

#### 分步分解

##### Step1 中文分句（自定义：按。！？和换行切）

##### Step2 用滑动窗口组成「组合句」（buffer_size 控制前后各几句）

##### Step3 对组合句 embedding，算相邻组合句相似度

##### Step4 相似度下跌超过阈值（百分位）→ 在此处切开

##### Step5 得到语义块 Node → 入库

#### 输出

##### 按主题相对完整的块（块大小不固定）

#### 操作要点

##### SemanticSplitterNodeParser(buffer_size=1, breakpoint_percentile_threshold=95, ...)

##### 先 clean_empty_text；千问 embedding 注意 batch≤10

##### 更慢更贵（要算很多句向量）

### 方法10：父子块 Parent-Child

#### 适用：既要检索准，又要生成时有完整上下文

#### 输入

##### 文档 + 两级大小，如父 2048、子 512

#### 分步分解

##### Step1 HierarchicalNodeParser 切出父大块、子小块，建立父子关系

##### Step2 只对叶子小块做 embedding，建向量索引

##### Step3 父块原文放进 docstore（不靠向量找父块）

##### Step4 查询时：向量检索命中小块

##### Step5 AutoMergingRetriever：把命中的小块合并回父块（或更大上下文）

##### Step6 把合并后的大上下文交给 LLM 生成

#### 输出

##### 检索命中：小块；生成输入：父块/合并块

#### 操作要点

##### parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512])

##### retriever = AutoMergingRetriever(leaf_retriever, storage_context)

#### 解决的矛盾：小块好中、大块好答

### 方法11：元数据预过滤

#### 适用：用户带时间/类别/来源限制

#### 分步分解

##### Step1 建库时给 Node 打 metadata（category/year/source/page）

##### Step2 查询时解析约束（只要 2024、只要年假）

##### Step3 构造 where 条件

##### Step4 向量检索只在过滤后的子集里做

##### Step5 无约束则 where 为空，全库搜

#### 完整例子

##### 入库：metadata={'category':'年假','year':2024}

##### 问题：2024 年年假怎么请

##### where={'category':'年假','year':2024} → 再向量搜

#### 口述：先缩小书架，再找相似书

### 方法12：意图路由

#### 适用：多个知识库/集合，问题类型不同

#### 分步分解

##### Step1 准备多库：制度库、FAQ 库、技术文档库

##### Step2 为每个库写清 description（给路由用）

##### Step3 分类：规则 / 小模型 / LLM 判断问题类型

##### Step4 只调用对应库的 retriever/query_engine

##### Step5 或多工具交给 SubQuestionQueryEngine 自动路由

#### 翻车点：description 写糊 → 路由乱；要写「查什么 / 不查什么」

### 方法13：权限过滤

#### 适用：多租户、按部门/角色可见

#### 分步分解

##### Step1 文档 metadata 写入 allowed_roles / dept

##### Step2 请求带上当前用户角色

##### Step3 检索前 where 加上角色条件

##### Step4 再向量搜；无权限文档根本不会进候选集

#### 铁律：不能先搜出敏感段再靠 Prompt「别泄露」

### 方法14：文档增强（摘要/关键词/假设问题）

#### 适用：正文不好搜，需要额外「入口」

#### 分步分解（离线）

##### Step1 对每个 chunk 调 LLM 生成：一句话摘要、关键词、2 个假设用户问题

##### Step2 把假设问题也做成可检索向量（或与 chunk 同 id 关联）

##### Step3 可选：摘要单独一路向量

##### Step4 在线检索时可匹配「假设问题」或「摘要」（类似反向 HyDE）

##### Step5 命中后仍返回原 chunk 正文给生成

#### 输出：更易被问句命中的索引，而不改变最终依据仍是原文

### 方法怎么串起来（推荐顺序）

#### 离线

##### 加载 → 清洗空文 → 分块(8/9/10选一) → 打元数据 → 可选增强 → 同一 Embedding 入库

#### 在线

##### 1 清洗（方法1）

##### 2 模糊？→ 澄清（方法2）

##### 3 复杂比较？→ 分解（方法7）

##### 4 否则三选一：重写(3) / 扩展(4) / HyDE(5)；缺背景加 Step-Back(6)

##### 5 有类别时间？→ 预过滤(11)；多库？→ 路由(12)；有权限？→(13)

##### 6 进入检索中（第 09 章混合/多路）→ 再重排生成（检索后）

#### 本仓库已落地 / 怎么调

##### /ask 默认 strategy=rewrite：清洗+重写双路（pre_retrieval.py）

##### 可改 strategy=hyde / clean / none；假想文档只检索不当引用

##### 后面已接混合检索、后处理三件套、CRAG；细节见第 13 章

## 09 检索中优化（Retrieval）
飞书：03-检索中优化（Retrieval）。每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。密码文档目标：提升召回率和相关性。

### 〇、总览：方法地图

#### 目标：提升召回率 Recall + 相关性（少漏、少偏）

#### 两条主线：混合检索（同库多算法） / 多路召回（多源多通道）

#### 胶水：RRF / relative_score 加权 / Round-Robin

#### 落点：都在 RAG 第 4 步「检索召回」；前三步仍是加载→分块→向量化入库

#### 和检索前区别：第 08 章改「问什么」；本章改「怎么查、去哪查」

### 术语定义（本章必背）

#### Retrieval（检索中）：优化「怎么查、用什么算法/通道查」

#### 召回率 Recall：该找到的相关内容里实际找回来的比例（少漏）

#### 精确率 Precision：找回来的内容里真正相关的比例（少脏）

#### 稠密向量：几乎每维都有值，擅长语义/同义匹配

#### 稀疏检索（BM25等）：词面/倒排，擅长专名与编号

#### 混合检索 Hybrid：同库同时跑稠密+稀疏再融合

#### 多路召回 Multi-channel：多源/多索引各自召回再融合

#### RRF：倒数排名融合 score=Σ1/(k+rank)，不要求分数量纲一致

#### relative_score：各路分数归一化后再加权融合

#### Round-Robin：各路轮流取一条，简单保多样性

#### ColBERT：token 级多向量交互（MaxSim），更细更吃资源

#### SPLADE：学习型稀疏向量，兼顾词面与一点语义

### 指标预习：召回率 vs 精确率

#### 适用

##### 开口答「效果不好」前，先分清漏了还是脏了

#### 输入

##### 一次检索返回的候选列表 + 人工标注的相关集合（或抽检）

#### 分步分解

##### Step1 明确相关集合：哪些 chunk 本应被找到

##### Step2 算召回率：相关集合里有多少出现在 Top-K

##### Step3 算精确率：Top-K 里有多少真相关

##### Step4 漏得多 → 优先混合/多路/扩 K；脏得多 → 融合权重、后加重排

#### 输出

##### 口述结论：当前是「召回病」还是「精确病」

#### 完整例子

##### 相关文档 10 篇，Top-5 只中 2 篇 → 召回差，先扩召回手段

##### Top-5 中了 4 篇相关但夹 1 篇无关 → 精确还行，可微调或 rerank

#### 翻车点：只看生成答案对不对，不区分检索阶段指标，会改错模块

### 方法1：混合检索 Hybrid Search

#### 适用：同一知识库里，既有口语/同义表达，又有专名、错误码、型号

#### 输入

##### 同一份 nodes（同一分块结果）

##### 用户查询字符串

##### 稠密 Embedding 模型 + BM25（中文需分词器）

#### 分步分解

##### Step1 全局 Settings.embed_model（如 DashScope text-embedding-v3）

##### Step2 文档 → SentenceSplitter/语义分块 → nodes（两路吃同一份）

##### Step3 稠密路：VectorStoreIndex(nodes).as_retriever(top_k)

##### Step4 稀疏路：BM25Retriever.from_defaults(nodes, tokenizer=jieba)

##### Step5 QueryFusionRetriever([vector, bm25], mode=reciprocal_rerank)

##### Step6 取融合后 Top-N → 交给 RetrieverQueryEngine / LLM

#### 输出

##### 融合后的 NodeWithScore 列表（语义命中 + 关键词命中都可能进榜）

#### 完整例子（登录超时）

##### 单源：只搜产品文档

##### 向量捞到「session 过期」「身份验证失败」

##### BM25 捞到正文含「登录超时」的段落

##### RRF 后两者都可能进入最终 Top-N

#### 讲义代码逐行（混合检索）

##### Settings.embed_model = DashScopeEmbedding(text-embedding-v3)

###### 意思：全局指定稠密向量模型，后面建索引会自动用它

###### 为什么：查询和文档必须同一套 Embedding，否则两路向量不在同一空间

##### docs = [Document(text=t) for t in documents]

###### 意思：把纯字符串包成 LlamaIndex 的 Document

###### 为什么：分块器和索引只认 Document/Node，不认裸字符串

##### splitter = SentenceSplitter(chunk_size=200, chunk_overlap=20)

###### 意思：按句子边界切块，每块约 200 token，相邻块重叠 20

###### 为什么：两路检索必须吃同一份 nodes，切一次就够

##### nodes = splitter.get_nodes_from_documents(docs)

###### 意思：得到检索的基本单位 Node 列表

##### index = VectorStoreIndex(nodes)

###### 意思：对每个 Node 调 embed_model，建成稠密向量索引

##### vector_retriever = index.as_retriever(similarity_top_k=5)

###### 意思：语义路只返回最像的 5 条，不做生成

###### 为什么：top_k 是「这一路的候选窗口」，后面还要和 BM25 融合

##### bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5, tokenizer=...)

###### 意思：用同一批 nodes 建关键词检索器，也取 5 条

###### tokenizer=lambda text: list(jieba.cut(text))

###### 意思：先用 jieba 把中文切成词，BM25 才能按词频打分

###### 为什么：默认英文分词按空格切，中文整句会变成一个 token，BM25 失效

##### QueryFusionRetriever(retrievers=[vector, bm25], mode='reciprocal_rerank')

###### 意思：同一个问题同时问两路，再用 RRF 按名次合成一张榜

###### 为什么：cosine 分和 BM25 分不能直接相加，只比排名更稳

##### RetrieverQueryEngine.from_args(retriever=...)

###### 意思：融合后的片段再拼进 Prompt，交给 LLM 生成

###### 为什么：混合检索只替换第 4 步召回，第 5 步生成不变

#### 翻车点

##### 中文不用 jieba：BM25 把整句当一个词，等于废掉

##### 直接加原始分数：cosine 与 BM25 量纲不同，必须 RRF 或先归一化

##### K 太小：两路都没机会进融合窗口

### 方法2：RRF 融合公式深挖

#### 适用：任意多路检索结果要合成一张公平榜单时

#### 输入

##### 各路已排序的文档列表（只要排名，不要原始分）

#### 分步分解

##### Step1 对每一路，给文档记名次 rank_i（从 1 起）

##### Step2 对每个文档累加 1/(k + rank_i)，默认 k=60

##### Step3 按总分降序截断 Top-N

##### Step4 去重：同一 doc id 只保留一条，分数已是累加结果

#### 输出

##### 跨路可比的综合排名；「两路都靠前」优于「一路第一、一路很差」

#### 完整例子

##### A：稠密2 + 稀疏5 → ≈0.0315

##### B：稠密1 + 稀疏20 → ≈0.0289

##### A 胜出：均衡优于偏科

#### 和 relative_score 对比

##### RRF：只看名次，最稳，工业首选

##### relative_score：先 min-max 归一化再加权，适合「明知 FAQ 更权威就给 1.2 权重」

##### Round-Robin：轮流取各路结果，偏多样性（搜索首页）

#### 翻车点：把 RRF 和「加权平均原始分」当成一回事

### 方法3：多路召回 Multi-channel Retrieval

#### 适用：知识分散在多个库/字段——技术文档、FAQ、社区、工单、手册

#### 输入

##### ≥2 个独立 Document 列表或独立索引

##### 每路一个 Retriever（可向量可 BM25）

##### 同一用户问题

#### 分步分解

##### Step1 分库：按业务切 tech_docs / faq_docs / community_docs…

##### Step2 分索引：每路 VectorStoreIndex 或 BM25Retriever

##### Step3 分检索：QueryFusionRetriever 并发调各路

##### Step4 融合：relative_score 加权 或 reciprocal_rerank

##### Step5 RetrieverQueryEngine 把融合结果交给 LLM

#### 输出

##### 带来源通道 metadata（如 channel=tech/faq）的融合候选

##### 覆盖面大于单库，召回率通常上升

#### 完整例子（讲义三路）

##### 路1 技术文档：稠密向量（长文语义）

##### 路2 FAQ：BM25 + jieba（短问答、关键词强）

##### 路3 社区讨论：稠密向量（口语）

##### 权重示例 [1.0, 1.2, 0.8]：FAQ 略加权

##### 问题「Qwen 部署需要多少显存？」→ 三路都可能贡献片段

#### 讲义代码逐行（三路召回）

##### Settings.embed_model / Settings.llm = DashScope(...)

###### 意思：Embedding 负责检索向量，LLM（如 qwen）负责最后生成

###### 为什么：检索阶段可以不调 LLM；生成阶段才用 qwen3.7-max

##### Document(..., metadata={"id": "...", "channel": "tech"})

###### 意思：每条原文带上来源标签，检索结果能看出出自哪一路

###### 为什么：三路混在一起后，没有 channel 就无法排查是哪库答偏了

##### tech_index = VectorStoreIndex.from_documents(tech_docs)

###### 意思：技术文档单独建一个稠密索引，和 FAQ、社区互不共用

###### 为什么：多路召回的关键是「分库分索引」，不是把所有文档塞进一个库

##### faq_retriever = BM25Retriever.from_defaults(nodes=faq_index.docstore...)

###### 意思：FAQ 这一路不用向量，改用 BM25 抓短问答里的关键词

###### docstore.docs.values() 意思：把索引里已经切好的 Node 拿出来给 BM25

###### tokenizer=jieba 意思：中文 FAQ 也必须先分词

##### community_retriever = community_index.as_retriever(similarity_top_k=3)

###### 意思：社区口语再走稠密向量，每路先各取 3 条

##### QueryFusionRetriever(retrievers=[tech, faq, community], retriever_weights=[1.0, 1.2, 0.8], mode='relative_score', num_queries=1, similarity_top_k=5)

###### retrievers 意思：三路检索器放进同一个融合器，一次 query 并发去搜

###### weights 意思：FAQ 权重 1.2 略高，社区 0.8 略低——你更信哪路就抬哪路

###### mode=relative_score 意思：先把每路分数 min-max 拉到同一尺度再加权

###### 为什么：cosine 大约 0~1，BM25 可以很大，不归一化 FAQ 会霸榜或被淹没

###### num_queries=1 意思：这次不让模型再改写出多个问法，只用用户原句

###### similarity_top_k=5 意思：三路合并去重后，最终只留 5 条给生成

###### use_async=False 意思：教学示例用同步调用，方便单步调试

##### query_engine.query(question) → response.source_nodes / response.response

###### source_nodes 意思：融合后真正喂给模型的片段，可打印 channel 和 id

###### response 意思：模型根据这些片段写出的最终回答

#### 翻车点

##### 路数盲目加到 5+：延迟和费用线性涨，2~3 路通常够

##### 各路 top_k 过大又不融合截断：噪音淹没生成

##### 忘记写 channel/id 元数据：出了错无法追哪一路在捣乱

### 方法4：混合 × 多路 嵌套架构

#### 适用：企业多知识库，且每库内部既有语义又有术语需求

#### 输入

##### 多个数据源；每源内部可再配向量+BM25

#### 分步分解

##### Step1 外层按数据源开多路召回

##### Step2 每一路内部做混合检索（向量+BM25+RRF）

##### Step3 外层再 RRF/加权融合 + 去重

##### Step4 可选：再接 rerank（检索后）压到 Top-3/5

#### 输出

##### 横向覆盖全，纵向每源也准——工业级检索骨架

#### 完整例子

##### 外层：产品文档 / 客服工单 / 技术规范

##### 内层：每库 Hybrid

##### 用户问「登录超时怎么处理」：文档给规范说法，工单给个案经验

#### 翻车点：一上来就上嵌套，Native 单路都没稳——先单库混合，再拆多路

### 方法5：中文 BM25 分词配置

#### 适用：所有要用 BM25 的中文 RAG

#### 分步分解

##### Step1 安装 jieba + llama-index-retrievers-bm25

##### Step2 方案A：tokenizer=lambda t: list(jieba.cut(t))

##### Step3 方案B：def tokenize_text(t): return list(jieba.cut(t)) 再传入

##### Step4 方案C（讲义推荐组合）：language='chinese', skip_stemming=True, 中英 token_pattern

##### Step5 自测：对含专名的短问，看 BM25 是否单独能命中

#### 代码逐行

##### def tokenize_text(text): return list(jieba.cut(text))

###### 意思：输入一整句，输出词列表，例如「登录超时怎么处理」→ ['登录','超时','怎么','处理']

##### tokenizer=tokenize_text

###### 意思：把函数本身交给 BM25，让它在检索时自己去调用

###### 为什么：写成 tokenize_text() 会立刻执行，传进去的是词列表，检索时会报错

##### language='chinese'

###### 意思：停用词表用中文，去掉「的/了/吗」这类无信息词

##### skip_stemming=True

###### 意思：关闭英文词干还原（running→run）

###### 为什么：中文没有词干，开着会乱改字

##### token_pattern=r"(?u)\b\w+\b|[\u4e00-\u9fa5]"

###### 意思：英文按单词切，中文至少按汉字切，避免整句粘成一块

###### 为什么：这是不用 jieba 时的保底切法；有 jieba 时优先用 jieba

#### 输出：稀疏路真正按「词」计分，而不是整句一个 token

#### 翻车点：tokenizer=tokenize_text() 多写了括号——传入的是列表不是函数

### 方法怎么串起来（推荐顺序）

#### 诊断

##### 专名/编号搜不到 → 先上方法1 混合（同库加 BM25）

##### 资料散落多系统 → 再上方法3 多路

##### 两路分数对不齐 → 方法2 RRF；要偏科加权 → relative_score

##### 多库且每库都难搜 → 方法4 嵌套

#### 标准 RAG 五步中的位置

##### 1 加载 2 分块 3 向量化入库 —— 不变

##### 4 检索召回 —— 替换为 Hybrid / Multi-channel / 嵌套

##### 5 喂给大模型之前 —— 接第 10 章 node_postprocessors 三件套

#### 和本仓库

##### 已落地：HYBRID_ENABLED + BM25(jieba) + QueryFusionRetriever(reciprocal_rerank)

##### 代码：retrieval_optimize.build_hybrid_retriever；失败回退纯向量

##### 未做：多目录多路 channel；见第 13 章演进 P4

#### 和第 08 章衔接

##### 先 Pre：清洗/重写/HyDE 得到更好 query

##### 再 Mid：用本章方法去查

##### 再 Post：第 10 章 rerank → 压缩 → 长上下文重排 → 约束生成

## 10 检索后优化（Post-retrieval）
飞书：04-检索后优化（Post-retrieval）。每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 代码意思 → 翻车点。

### 〇、总览：方法地图

#### 目标：召回结果送入 LLM 前，做重排 + 精简 + 重排版，抬生成质量

#### 位置：第 4 步检索召回之后、第 5 步喂模型之前

#### 入口：node_postprocessors=[...]，按列表顺序串行加工 nodes

#### 三件套：Rerank → SentenceEmbeddingOptimizer → LongContextReorder

#### 和第 08/09 章：前改问句、中改召回；本章改「怎么用召回结果」

### 术语定义（本章必背）

#### Post-retrieval（检索后）：召回之后、喂 LLM 之前加工候选

#### Node Postprocessor：对 NodeWithScore 列表串行后处理的组件

#### Re-ranking：用更准模型对粗召回候选二次打分排序

#### 两阶段检索：粗召回（快广）+ 精排（慢准）

#### Bi-Encoder：查询/文档各自编码再比相似度，快

#### Cross-Encoder：query+doc 一起进模型打分，准但慢

#### 上下文压缩：只留与问题最相关的句子，丢掉冗余

#### SentenceEmbeddingOptimizer：按句-查询相似度裁剪的压缩器

#### LongContextReorder：最相关放首尾，对抗中间遗忘

#### Lost in the Middle：长上下文中模型对中间段落利用率偏低

#### Citation：答案标明来源，便于核查并抑制瞎编

### 方法1：两阶段检索与重排序 Re-ranking

#### 适用：粗召回有相关材料，但 Top-3/5 常被「沾边噪声」占坑

#### 输入

##### 用户问题 + 粗排候选（如 similarity_top_k=20~100）

##### 精排模型：API（DashScopeRerank）或本地 Cross-Encoder

#### 分步分解

##### Step1 Bi-Encoder/向量检索：快，从海量库捞 Top-N 候选

##### Step2 Cross-Encoder/Rerank：query+doc 一起打分，只精排候选

##### Step3 截断 top_n（常 3/5）交给生成

##### Step4（可选）后面再接压缩与长上下文重排

#### 输出

##### 按精排分排序的短名单；精确率↑，喂给模型的噪声↓

#### 完整例子（超市红烧肉）

##### 粗排：五花肉、酱油…也抓回红烧牛肉面、红烧鱼料——快但乱

##### 精排：逐个判断，真正做红烧肉必备的顶到最前

##### 口诀：先广撒网，再精挑细选

#### 原理口述

##### Bi-Encoder：查询/文档各自编码再比余弦，文档可离线预计算

##### Cross-Encoder：拼接后深层交互直接出相关性分，准但慢

##### 只用双塔：Top-5 易混入沾边货；只用交叉：百万库打不动

##### 两阶段 = 工业标准粗召回 + 精排

#### 讲义代码逐行（重排序）

##### pip：方式A dashscope-rerank / 方式B sentence-transformers

###### 意思：A 走 API 重排；B 本机加载 Cross-Encoder

###### 为什么：有网用 A 省事；内网/离线用 B

##### Settings.embed_model = DashScopeEmbedding(text-embedding-v3)

###### 意思：第 1 阶段粗排仍用同一套稠密向量模型

###### 为什么：查询向量和库里文档向量必须同一空间

##### index = VectorStoreIndex.from_documents(docs)

###### 意思：建库时就把每条 Document 向量化进索引

##### retriever = index.as_retriever(similarity_top_k=6)

###### 意思：Bi-Encoder 粗排，先捞 6 条候选（教学示例；生产常 20~50）

###### 为什么：要给第 2 阶段留「可选余地」，不能一上来就只留 3 条

##### DashScopeRerank(model="qwen3-rerank", top_n=3, api_key=...)

###### 意思：把粗排候选交给重排模型，query+doc 交互打分，只留 Top-3

###### top_n 意思：精排后的截断长度，也是最终进 Prompt 的条数上限

###### 注意：讲义旧名 gte-rerank 可能下线，以控制台当前模型名为准

##### SentenceTransformerRerank(model=..., top_n=3)

###### 意思：本地 Cross-Encoder 替代 API，接口同样挂到 node_postprocessors

###### 为什么：无外网、要控数据不出域时用

##### as_query_engine(similarity_top_k=6, node_postprocessors=[reranker])

###### 意思：引擎内部先 retrieve(6) → 再跑 reranker → 再拼 Prompt 调 LLM

###### 为什么：重排是「后处理器」，不改索引，只改召回结果名单

##### for n in response.source_nodes: print(n.score, n.text)

###### 意思：看精排后的分数与正文，确认噪声是否被挤出 Top

#### 翻车点

##### 粗排 top_k=3 再 rerank：精排几乎无事可做

##### 对全库跑 Cross-Encoder：延迟炸裂

##### 把 RRF 融合和 Cross-Encoder 精排当成同一步

### 方法2：上下文压缩 SentenceEmbeddingOptimizer

#### 适用：相关片段很长，里面夹杂天气/CI/CD/闲聊等噪声句

#### 输入

##### 已召回（最好已重排）的 nodes + 同一查询

#### 分步分解

##### Step1 把每个片段拆成句子（中文可用正则按。！？；切）

##### Step2 每句与查询算 embedding 相似度

##### Step3 percentile_cutoff / threshold_cutoff 丢掉低分句

##### Step4 只把保留句子拼回片段，再喂 LLM

#### 输出

##### 更短、更贴题的上下文；token↓、噪声↓、幻觉风险↓

#### 完整例子

##### 压缩前：显存要求夹在「办公自动化」「今天天气不错」中间

##### 压缩后：只留「Qwen2.5 最低 16GB 显存…」等相关句

#### 讲义代码逐行（上下文压缩）

##### 故意造「长片段+噪声」Document

###### 意思：同一段里混入显存要点和「天气/CI/CD」废话，方便观察裁剪效果

##### def chinese_sentence_splitter(text): re.split(...); return [s.strip() for s in ... if s.strip()]

###### 意思：按。！？；和换行把中文切成句子列表

###### 为什么：默认英文切句器遇中文常切不动或切错

##### SentenceEmbeddingOptimizer(embed_model=..., percentile_cutoff=0.5, tokenizer_fn=chinese_sentence_splitter)

###### 意思：每句与查询算 embedding 相似度，只留排名前 50% 的句子

###### percentile_cutoff 意思：按相对名次裁；threshold_cutoff 意思：按绝对分数裁

###### tokenizer_fn 意思：告诉优化器用你的中文切句函数

##### as_query_engine(..., node_postprocessors=[optimizer])

###### 意思：召回后先裁句，再把瘦身后的片段喂给 LLM

###### 为什么：不改索引内容，只改「这一次」送给模型的文本

##### 对比打印压缩前 retrieve() vs 压缩后 source_nodes

###### 意思：肉眼检查「天气不错」等噪声句是否被删掉

#### 和重排的关系

##### 重排：选哪些块、谁排前

##### 压缩：块里留哪几句

##### 常配合：先重排，再压缩

#### 翻车点：cutoff 过严，相关句也被裁光；过松等于没压缩

### 方法3：长上下文重排 LongContextReorder

#### 适用：喂给模型的片段较多/较长，担心中间内容被忽略

#### 输入

##### 已排序的 nodes（通常来自 reranker，相关度从高到低）

#### 分步分解

##### Step1 认识 Lost in the Middle：首尾易记、中间易丢

##### Step2 调用 LongContextReorder()（无构造参数）

##### Step3 把最相关挪到列表头尾，次相关塞中间

##### Step4 不改文本内容、不改选集，只改排列

#### 输出

##### 同一批片段，但顺序更贴合 LLM 注意力分布

#### 完整例子

##### rerank 后：1>2>3>4>5 相关度递减

##### reorder 后：最高分在首尾，较低分在中间

#### 讲义代码逐行（长上下文重排）

##### from llama_index.core.postprocessor import LongContextReorder

###### 意思：导入「只改顺序、不改内容」的后处理器

##### reranker = DashScopeRerank(model="qwen3-rerank", top_n=5, api_key=api_key)

###### 意思：先精排出 Top-5，默认相关度从高到低

##### reorder = LongContextReorder()

###### 意思：实例化排版器，构造函数无参数

###### 为什么：策略固定——最相关放首尾，次相关塞中间

##### as_query_engine(similarity_top_k=8, node_postprocessors=[reranker, reorder])

###### 意思：粗召回 8 → rerank 留 5 → reorder 重排版 → 再生成

###### 列表顺序=执行顺序：必须先精排再排版，不能写反

##### 观察 source_nodes 顺序

###### 意思：最高分应出现在列表头部和尾部，中间是次相关

###### 为什么：对抗 Lost in the Middle，让模型更吃首尾信息

#### 翻车点：片段很少（≤3）时收益有限；别指望它能「救回」没召回的内容

### 方法4：三件套串成完整检索后链

#### 适用：要上工业级 Post-retrieval 默认链路时

#### 分步分解

##### Step1 粗召回 similarity_top_k 调大（如 8~50）

##### Step2 DashScopeRerank / Cross-Encoder → top_n

##### Step3 SentenceEmbeddingOptimizer 裁句

##### Step4 LongContextReorder 首尾排版

##### Step5 LLM 生成；Prompt 约束仅依据资料 + 引用

#### 推荐挂法

##### node_postprocessors=[reranker, compressor, reorder]

##### 口诀：先选块 → 再削句 → 最后排版

#### 讲义代码逐行（三件套完整链）

##### Settings.embed_model / Settings.llm = DashScope(...)

###### 意思：embedding 服务检索与压缩相似度；llm 只负责最后生成

##### reranker = DashScopeRerank(..., top_n=5)

###### 意思：第 1 环——决定哪些块留下、谁更相关

##### compressor = SentenceEmbeddingOptimizer(percentile_cutoff=0.5, tokenizer_fn=...)

###### 意思：第 2 环——块内去噪声句，缩短上下文

##### reorder = LongContextReorder()

###### 意思：第 3 环——把高相关块挪到首尾

##### as_query_engine(similarity_top_k=20, node_postprocessors=[reranker, compressor, reorder])

###### 意思：一次 query 走完：粗召回→精排→裁句→排版→生成

###### 为什么写这个顺序：先决定「要哪些块」，再「削句子」，最后「摆位置」

###### 写反会怎样：先 reorder 再 rerank＝排版结果又被打乱；先压缩再 rerank＝在噪声块上白算相似度

##### response.source_nodes / response.response

###### source_nodes 意思：最终真正进 Prompt 的片段（已精排+已压缩+已排版）

###### response 意思：模型基于这条加工后的上下文写出的答案

#### 输出

##### 短、准、好读的上下文，生成更稳、更省 token

#### 翻车点

##### 三件套一次全开却不评测：延迟↑费用↑，先只上 rerank

##### 顺序挂反：先 reorder 再 rerank 失去精排意义

### 方法怎么串起来（推荐顺序）

#### 诊断

##### 相关材料在后面几名 → 方法1 重排

##### 材料对但废话多/超窗口 → 方法2 压缩

##### 片段多、答案漏中间要点 → 方法3 长上下文重排

##### 要完整工业链 → 方法4 三件套

#### 和本仓库

##### 已落地三件套：本地 bge-reranker → SentenceEmbeddingOptimizer → LongContextReorder

##### 代码：retrieval_optimize.build_node_postprocessors；/ask 走 apply_postprocessors

##### 默认不依赖千问重排；RERANK_PROVIDER=dashscope 才用 API

#### 和第 08/09 章衔接

##### Pre（08）改问句 → Mid（09）混合/多路召回 → Post（10）三件套 → 生成

##### 召回上限由 08/09 决定；本章抬的是「已召回材料的利用率」

#### 五、小结（讲义）

##### 重排：抬精确率

##### 压缩：降噪声与 token

##### 长上下文重排：对抗 Lost in the Middle

##### 三者都通过 node_postprocessors 接入，是工业级 RAG 标准检索后手段

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

#### 详见第 13 章：项目全链路文件/API/开关对照表

## 12 Corrective RAG（CRAG）
飞书：06-其他优化（CorrectiveRAG）
https://ecnwvcdzorsp.feishu.cn/docx/TO92dU6QWoTXYjxHT6icY53Dnsf
定位：检索后优化（Post-Retrieval）的评估与修正阶段；管「查错了怎么办」。

### 〇、总览

#### 一句话：检索失手时要有自知之明 + 自我纠错，而不是照单全收

#### CRAG = 标准 RAG + 检索质量校验 + 自动修正 / 补充检索

#### 论文叙事：多基准准确率 +4%~37%，且无需再训现有 LLM

#### 阶段归属：Post-Retrieval —— 检索结果评估与修正

#### 和第 10 章：Rerank/压缩改「怎么用」；CRAG 改「用不用、不够就纠」

### 术语定义（本章必背）

#### Corrective RAG / CRAG

##### 定义：Corrective Retrieval-Augmented Generation，修正增强检索生成

##### 公式：CRAG = 标准 RAG + 检索质量校验 + 自动修正/补充检索

##### 一句话：不假设「检索到的就是对的」，先评估再决定怎么用

#### Retrieval Evaluator（检索评估器）

##### 定义：对召回文档相对问题的正确性/相关性打分或分档的模块

##### 论文三档：Correct / Ambiguous / Incorrect

##### 工程常见：逐篇 yes/no 或 RELEVANT/IRRELEVANT

#### Correct（正确）

##### 定义：检索结果整体足以正确支撑回答

##### 后续：走 Knowledge Refinement，主要用内部精炼知识 k_in

#### Ambiguous（模糊）

##### 定义：部分有用但不充分，或相关度存疑

##### 后续：内部精炼 + 外部搜索，组合 k_in + k_ex

#### Incorrect（不正确）

##### 定义：检索结果基本无法支撑正确回答（跑题/错误/空）

##### 后续：侧重外部知识搜索，主要用 k_ex

#### Knowledge Refinement（知识精炼）

##### 定义：对内部文档做 Decompose→Filter→Recompose，去噪留精华

##### 产物：精炼内部知识 k_in

#### Knowledge Searching（知识搜索）

##### 定义：内部不足时重写查询并检索外部（如 Web）补充知识

##### 产物：外部知识 k_ex

#### k_in / k_ex

##### k_in：来自内部知识库并经精炼的上下文

##### k_ex：来自外部搜索并经选择的上下文

#### 库内修正 vs 完整 CRAG

##### 库内修正：评估过滤 + 改写后仍查同一知识库（本仓库路线）

##### 完整 CRAG：不足时还可 Web 搜索（讲义 Tavily Workflow）

#### confidently wrong（自信地犯错）

##### 定义：检索看似相关实则答非所问，模型仍斩钉截铁给出错误答案

##### CRAG 要防的典型失败模式

#### 检索相关性 ≠ 答案准确性

##### 定义：向量相近或关键词重合，不等于文档能正确回答该问题

##### 例子：《蝙蝠侠之死》编剧 vs 1989《蝙蝠侠》编剧 Hamm

### 一、为什么需要 CRAG

#### 传统 RAG 困境

##### 本质：把检索器结果当绝对真理，无条件喂给生成器

##### 现实：查询不清、库覆盖不全、语义偏差 → 不相关甚至误导

##### 局限：照单全收，没有质量评估关卡

#### 演讲助手比喻

##### 助手资料靠谱 → 演讲精彩

##### 资料错或不相关还照搬 → 翻车

#### 正例：准确文档 → 正确回答

##### 问：亨利·菲尔登的职业是什么？

##### 检索：亨利·费登…是保守党政治家（准确，绿色）

##### 生成：政治家 ✓ —— 文档明确含答案

#### 反例：不准确文档 → 错误回答

##### 问：《蝙蝠侠之死》的编剧是谁？

##### 检索：1989 电影《蝙蝠侠》编剧 Hamm（看似相关实答非所问）

##### 生成：哈姆 ✗ —— 检索相关性 ≠ 答案准确性

##### 警示：confidently wrong（自信地犯错）

#### 解决思路

##### 在检索与生成之间插入文档质量校验关卡

##### 相关且准确 → 用于生成

##### 不相关/不准确 → 丢弃或补充检索（Web 等）

##### 全部不准确 → 重写查询重检索，或回答无法确定

#### 一句话对比：传统假设「检索到的就是对的」；CRAG 质疑「检索到的真的对吗？」

### 二、工作流程（论文三档）

#### ① 用户提问

#### ② 初步检索：知识库召回候选文档

#### ③ 检索质量评估（灵魂）

##### 轻量级 Retrieval Evaluator 给文档 / 整体结果打分

##### 三档：Correct（绿）/ Ambiguous（黄）/ Incorrect（红）

#### ④ 按档位组合内部精炼知识 / 外部搜索知识 → 生成

#### 为什么要用

##### 大幅降低幻觉

##### 私有库 + 公共知识混合题尤其好

##### 比普通 RAG 更鲁棒、更准确

### 三、技术解构：三阶段架构

#### Stage1 Retrieval

##### 问题 x → 检索器 → 文档 d1, d2, …

#### Stage2 Knowledge Correction（知识修正）

##### 6.1 Retrieval Evaluator

###### 问：检索文档对 x 是否正确？

###### 输出 Correct / Ambiguous / Incorrect

###### 对应第一张图：Accurate vs Inaccurate Documents

##### 6.2 Knowledge Refinement（Correct 路径）

###### Decompose：文档拆成 strip 片段

###### Filter：丢掉不相关片段

###### Recompose：重组为精炼内部知识 k_in

###### 即使 Correct，也可能泥沙俱下，要去噪

##### 6.3 Knowledge Searching（Ambiguous / Incorrect）

###### Rewrite：重写查询（更像搜索引擎问法）

###### 例子：Death of a Batman; screenwriter; Wikipedia

###### Web Search → 候选 k1…kn → Select → 外部知识 k_ex

###### 类比 Workflow 的 transform_query + Tavily

#### Stage3 Generation — 三种输入组合

##### Correct → 主要用 k_in（纯内部精炼）

##### Ambiguous → k_in + k_ex（内部+外部）

##### Incorrect → 主要用 k_ex（纯外部）

##### 工程简化：Document(relevant_text + search_text)；哪路空=没用哪路

### 四、基础版代码：内部修正（不过网）
讲义第二节：相关性过滤 + 全无关则改写重检索。覆盖「评估 + 内部修正」。

#### 流程四步

##### [1] retriever.retrieve(query) 多召回（如 top_k=5）

##### [2] 逐篇 RELEVANT / IRRELEVANT 过滤（CRAG 核心）

##### [3] 若全部无关：REWRITE_PROMPT 改写 → 再检索再过滤

##### [4] 仍无关则拒答；否则拼 context 生成

#### 关键 Prompt

##### RELEVANCE：只输出 RELEVANT 或 IRRELEVANT

##### REWRITE：写得更清晰具体，只输出改写后问题

##### ANSWER：仅依据资料回答

#### 实现要点

##### 继承 CustomQueryEngine，封装评估+修正+生成

##### 评估 LLM 低温（讲义 qwen；本仓库可用 DeepSeek）

##### verbose 打印每篇相关/无关，便于调试

#### 使用说明

##### 本地 data/*.txt 当知识库

##### 环境变量：讲义 DASHSCOPE；完整版再加 TAVILY_API_KEY

### 五、完整版：Workflow + Web 搜索
内部不足时转向 Tavily 等外部搜索；官方 Pack 写死 gpt-4，讲义手写 Workflow 换成通义。

#### 与基础版差别

##### 基础版：全无关 → 还在同一库里改写重查

##### 完整版：出现不相关 → 重写查询 + Web 补充外部知识

#### 事件驱动步骤

##### ingest：documents → VectorStoreIndex（首次 run）

##### prepare：存 index / Tavily / query_str

##### retrieve：similarity_top_k=5 候选

##### eval_relevance：逐篇 LLM yes/no（评估器）

##### extract_relevant_texts：只留 yes 文本

##### transform_query：有 no → 重写 + Tavily.search

##### query_result：内外文本合并 SummaryIndex 再生成

#### 工程简化说明

##### 论文三档 → 工程常简化为逐篇 yes/no

##### 只要有一篇 no，就触发 Web（Ambiguous+Incorrect 合并）

##### 想还原三档：改 eval 输出 correct/ambiguous/incorrect，分三条路径

#### Workflow 概念速记

##### Event：step 间数据载体

##### @step：收 Event 出新 Event

##### Context.store：跨 step 共享字典

##### run()：入口，参数变成 StartEvent

### 六、核心知识点总结

#### Corrective RAG = 普通 RAG + 检索质量评估 + 自动修正

#### 评估器：Correct / Ambiguous / Incorrect（工程可简化 yes/no）

#### 修正手段：知识精炼（内部去噪）+ Web 搜索（外部补充）

#### 收益：幻觉↓、过时信息↓、无关检索↓；私有+公共混合场景尤佳

### 七、CRAG vs Self-RAG

#### Self-RAG：管「查不查」+ 生成侧自我反思（Retrieve/ISREL/ISSUP/ISUSE）

#### CRAG：管「查错了怎么办」——评估检索质量并纠正/外搜

#### Self-RAG 重生成过程元认知；CRAG 重检索结果纠错与外部补充

#### 不互斥：可先 CRAG 保证资料靠谱，再 Self-RAG 保证生成有据

#### 口述口诀：Self-RAG=查不查；Corrective=查错了怎么办；Rerank=榜上谁第一

### 八、实战启示与场景

#### 工程指导

##### 不要迷信检索器：质量评估是安全带

##### 轻量专用评估器（论文 0.77B）可优于大而全 LLM 做相关性

##### 内部答不了就外搜，别闭门造车幻觉

##### 知识粒度：整篇硬塞不如拆 strip 再筛

#### 应用场景

##### 企业问答：库匹配差时补权威来源，避免不懂装懂

##### 医疗咨询：精炼+外搜降低错误信息

##### 教育辅导：检索差时动态拿最新资料

### 九、对照 chroma文档管理：代码级走读
主路径：RagAskService.ask → apply_crag → synthesize。启动 python chroma文档管理/run.py → :8003

#### 在 /ask 流水线中的精确位置

##### ① prepare_retrieval_queries（Pre）

##### ② 每路 _build_retriever：向量+BM25 QueryFusion（Mid）

##### ③ 多 query 时 merge_nodes_rrf（查询间融合）

##### ④ apply_postprocessors：rerank→压缩→LongContextReorder（Post）

##### ⑤ apply_crag（本章）← 过滤无关；全无关则改写后 _retrieve_pipeline 再跑一遍 Mid+Post

##### ⑥ get_response_synthesizer(compact)+ASK_QA_PROMPT 生成；sources 用用户原问题对应的真实块

#### crag.py 函数对照讲义

##### _is_relevant ≈ 讲义 Retrieval Evaluator（二值 RELEVANT/IRRELEVANT）

##### filter_relevant_nodes ≈ 基础版 _filter_relevant + verbose 打印

##### rewrite_query_for_retrieval ≈ 讲义 REWRITE_PROMPT（全无关才触发）

##### apply_crag ≈ CorrectiveRAGQueryEngine.custom_query 的评估+修正段

##### retrieve_fn 注入：保证重试仍走混合检索+三件套，不是裸向量

##### 无 LLM 时 _is_relevant 直接 True：避免把结果滤空

#### crag 响应字段（前端 index.html 会展示）

##### enabled / message：是否开启、走了哪条分支

##### before_count → after_count：过滤前后篇数

##### retried + rewritten_query：是否纠错改写及新问句

##### eval[]：每篇 rank/relevant/preview，便于作业演示与排障

##### message 取值：filtered / rewrote_and_filtered / no_relevant_after_retry / …

#### 开关与默认

##### CRAG_ENABLED=true（默认开）

##### CRAG_VERBOSE=true：终端打印 [CRAG] 文档 i：相关/无关

##### 评估模型=Settings.llm（与问答同一套，如 DeepSeek），非单独小评估器

#### 与讲义完整版（Workflow+Tavily）差距

##### 已落地：库内评估过滤 + 一轮改写重检索（demo01 路线）

##### 未落地：Correct/Ambiguous/Incorrect 三档分流

##### 未落地：Knowledge Refinement 拆 strip→滤→重组

##### 未落地：Tavily / Web 外搜；Ambiguous 时 k_in+k_ex

##### 演进优先级：① strip 精炼 ② 三档 ③ 可选外搜（注意内网/合规）

#### 排障口诀（结合本项目）

##### after_count=0：看 eval 是否全 IRRELEVANT → 问法/库覆盖/阈值过严

##### retried=true 仍空：改写句是否偏离；检查混合检索是否回退成纯向量

##### 相关篇被误杀：看 LLM 是否稳定；可临时 CRAG_ENABLED=0 对比

##### 延迟高：CRAG 每篇一次 complete；可先减小 k / RETRIEVE_CANDIDATES

#### 全文件/API 对照见第 13 章

## 13 chroma文档管理：项目全链路对照
把第 08~12 章方法映射到本仓库搜索引擎。根目录：chroma文档管理/；包：semantic_search/；启动：python chroma文档管理/run.py → http://127.0.0.1:8003/

### 〇、一张总图：用户问一句会发生什么

#### 浏览器 static/index.html → POST /ask {question,k,strategy}

#### main.ask → RagAskService.ask（编排层）

#### Pre：pre_retrieval.prepare_retrieval_queries

#### Mid：engine._build_retriever → 向量±BM25；多 query 则 merge_nodes_rrf

#### Post：retrieval_optimize.apply_postprocessors 三件套

#### CRAG：crag.apply_crag（可改写重跑 Mid+Post）

#### Gen：response_synthesizer + ASK_QA_PROMPT；返回 answer/sources/pre_retrieval/crag

### 术语定义（项目里会碰到的词）

#### Native RAG

##### 定义：最朴素的检索增强：问句→向量检索 Top-K→塞进 Prompt→生成

##### 本项目底座仍是 Native，上面叠了 Pre/Mid/Post/CRAG

#### SemanticSearchEngine

##### 定义：engine.py 中的核心引擎类，管 Embedding/LLM/Chroma/分块/索引/检索

#### RagAskService

##### 定义：/ask 编排层，按 Pre→Mid→Post→CRAG→Gen 串完整作业链路

#### Node / NodeWithScore

##### Node：LlamaIndex 里一块可检索文本（通常=一个 chunk）

##### NodeWithScore：带检索分数的节点，融合/重排会改 score

#### Chunk / 分块

##### 定义：把长文档切成适合 embedding 与召回的小段

##### 本项目：Sentence / Token / Semantic 三种 splitter

#### strategy（检索前策略）

##### 定义：/ask 请求里控制查询怎么预处理的枚举

##### 取值：none / clean / rewrite（默认）/ hyde

#### QueryFusionRetriever

##### 定义：LlamaIndex 多检索器融合器；本项目用它做向量+BM25 同库混合

##### mode=reciprocal_rerank 即按 RRF 融排名

#### BM25

##### 定义：经典稀疏关键词检索算法，擅长专名、编号、精确词面

##### 中文必须配合分词（本项目 jieba）

#### RRF（Reciprocal Rank Fusion）

##### 定义：用「排名倒数」融合多路结果，不依赖原始分数量纲

##### 本项目两处：路内 QueryFusion；多 query 时 merge_nodes_rrf

#### node_postprocessors

##### 定义：检索后、生成前的节点后处理器列表，按顺序串行

##### 本项目三件套：Rerank → 压缩 → LongContextReorder

#### Cross-Encoder / Bi-Encoder

##### Bi-Encoder：查询与文档各自编码再比相似度，快，适合粗召回

##### Cross-Encoder：query+doc 一起进模型打分，准但慢，适合精排

#### SentenceEmbeddingOptimizer（上下文压缩）

##### 定义：按句与查询的相似度裁掉低相关句子，减少噪声与 token

#### LongContextReorder

##### 定义：把最相关片段放到上下文首尾，对抗 Lost in the Middle

#### Lost in the Middle

##### 定义：长上下文里，模型对中间段落记忆/利用率明显低于首尾

#### HyDE

##### 定义：Hypothetical Document Embeddings，先生成假想答案文档再拿去检索

##### 注意：假想文只用于检索，不能当事实引用（本项目 sources 不用它）

#### pre_retrieval / crag（响应字段）

##### pre_retrieval：检索前中间产物（原句/清洗/改写/HyDE/检索列表）

##### crag：Corrective RAG 过程（过滤前后篇数、是否重试、评估明细）

#### Chroma / Collection

##### Chroma：本项目使用的向量数据库

##### Collection：一个命名向量集合（默认 native_rag）

### 一、目录与职责（打开代码用）

#### run.py：启动入口，挂 sys.path 后调 semantic_search.__main__

#### app/main.py：FastAPI 路由 /ask /search /query /chat /ingest /upload …

#### app/engine.py：Embedding/LLM/Chroma/分块/索引；_build_retriever / query / chat

#### app/config.py：模型、分块、HYBRID/RERANK/COMPRESS/REORDER/CRAG 开关

#### app/schemas.py：AskRequest/AskResponse、PreRetrievalInfo、CragInfo

#### app/service/pre_retrieval.py：清洗 / 重写 / HyDE

#### app/service/retrieval_optimize.py：混合召回 + 后处理三件套

#### app/service/crag.py：Corrective RAG 库内修正

#### app/service/rag_service.py：/ask 专用编排（Pre→Mid→Post→CRAG→Gen）

#### static/index.html：问答 UI，展示策略过程、CRAG 过滤、来源卡片

#### data/：默认灌库 md/txt；chroma_db/：向量持久化

### 二、章节 ↔ 模块映射

#### 第 08 检索前 → pre_retrieval.py + /ask?strategy=

##### none：原句单路

##### clean：去口语填充 + 术语表（电脑→笔记本电脑 等）

##### rewrite（默认）：清洗句 + 改写句双路，防改歪

##### hyde：清洗句 + 假想说明文双路；假想文只检索不当引用

##### 前端：pre_retrieval 盒子展示 original/clean/rewritten/hyde_doc

#### 第 09 检索中 → retrieval_optimize.build_hybrid_retriever

##### HYBRID_ENABLED：向量 as_retriever + BM25(jieba) → QueryFusionRetriever

##### 默认 mode=reciprocal_rerank（RRF）；失败回退纯向量

##### 粗排窗口：RETRIEVE_CANDIDATES（默认 20）给精排留余量

##### /ask 多 query：路内融合后再 merge_nodes_rrf 做查询间融合

#### 第 10 检索后 → build_node_postprocessors / apply_postprocessors

##### Rerank：默认本地 SentenceTransformerRerank(bge-reranker-base)

##### RERANK_PROVIDER=dashscope 才走千问 qwen3-rerank

##### 压缩：SentenceEmbeddingOptimizer + 中文切句 + COMPRESS_PERCENTILE

##### 排版：LongContextReorder 对抗 Lost in the Middle

##### query/chat：挂在 RetrieverQueryEngine / chat_engine 的 node_postprocessors

#### 第 11 Self-RAG → 尚未成独立模块

##### 缺口：Retrieve 门控、ISSUP 验据、ISUSE 打分

##### 可借用：CRAG 的相关性过滤 ≈ ISREL

##### 落地建议见第 11 章第九节

#### 第 12 CRAG → crag.py + rag_service 第⑤步

##### 默认开启；全无关改写后 _retrieve_pipeline 重跑

##### 不联网：无 Tavily，属讲义基础版路线

### 三、API 怎么选

#### /ask：作业主链路，带 strategy + pre_retrieval + crag（推荐演示）

#### /search：只检索不生成，看混合/后处理召回效果

#### /query：一次性 RAG，有后处理，无 Pre 多策略、无 CRAG 编排

#### /chat：多轮记忆；后处理挂引擎，会话键含 hybrid/rerank 标志

#### /ingest /upload：灌库；会 _invalidate_retrieval_cache 重建 BM25

#### /stats /health：看库规模与 hybrid_enabled/rerank_enabled 等

### 四、环境变量开关速查（config.py）

#### HYBRID_ENABLED / HYBRID_FUSION_MODE / RETRIEVE_CANDIDATES

#### RERANK_ENABLED / RERANK_PROVIDER(local|dashscope|none) / RERANK_MODEL / RERANK_TOP_N

#### COMPRESS_ENABLED / COMPRESS_PERCENTILE

#### REORDER_ENABLED

#### CRAG_ENABLED / CRAG_VERBOSE

#### CHUNK_SIZE / CHUNK_OVERLAP / SIMILARITY_TOP_K

#### EMBEDDING_* / LLM（DeepSeek 等）/ DASHSCOPE_API_KEY（仅千问路径需要）

#### SEARCH_HOST / SEARCH_PORT（默认 8003）

### 五、和讲义 Advanced 闭环四问对照

#### 查什么 → strategy 重写/HyDE（第 08）

#### 去哪查 → 同库向量+BM25（第 09）；未做多目录多路 channel

#### 查得准 → 本地 bge rerank（第 10）

#### 怎么用 → 压缩+长上下文重排+引用约束；错了再 CRAG 纠（第 10/12）

#### 查不查 → Self-RAG Retrieve 尚未接（第 11 缺口）

### 六、效果不好时：按本项目排查

#### ① /stats 库是否为空；分块是否切断关键句

#### ② 换 strategy：rewrite↔hyde↔clean，看 pre_retrieval 双路是否合理

#### ③ 专名搜不到：确认 HYBRID_ENABLED 与 jieba/bm25 依赖

#### ④ 相关在后面：确认 RERANK_ENABLED 与本地 bge 是否加载成功

#### ⑤ 答案飘：看压缩是否过猛；Prompt 是否仍「仅依据上下文」

#### ⑥ CRAG 滤光：看 crag.eval；必要时 CRAG_VERBOSE 对照终端

#### ⑦ 延迟：降 k/候选；关 CRAG 或压缩做 A/B

### 七、建议的下一刀改造（优先级）

#### P0：Self-RAG Retrieve 门控（闲聊不查）

#### P1：生成后 ISSUP 验据 + 不足则重写

#### P2：CRAG strip 级 Knowledge Refinement（对齐论文 Correct 路径）

#### P3：可选 Web 补充（仅公网场景；内网知识库慎开）

#### P4：多目录多路召回 + channel 元数据（第 09 进阶）

#### P5：接第 14 章评估闭环——开关 A/B + Hit/MRR/Faithfulness 回归

## 14 RAG评估
飞书：01-RAG评估
https://ecnwvcdzorsp.feishu.cn/docx/EfLrdJBgvoneojxavWxctJKfngc
优化做完必须评估：量化收益、定位检索/生成瓶颈、驱动下一轮优化。

### 〇、总览

#### 一句话：RAG 优化完毕后必须评估——量化效果、找瓶颈、驱动优化

#### 三大评测面：检索 / 生成 / 端到端，缺一不可

#### 诊断口诀：答案差先看检索指标 → 检索锅还是生成锅

#### 工具线：LlamaIndex 内置评估器（快）→ RAGAS（系统基准，了解）

#### 和本仓库：可用 /ask 输出 + 评测集对比 Pre/Mid/Post/CRAG 开关前后

### 术语定义（本章必背）

#### RAG 评估：用可复现指标衡量检索与生成质量，并对比优化前后

#### LLM-as-a-judge：用大模型当裁判，对照问题/答案/上下文自动打分

#### Ground Truth / Reference：人工或自动标注的标准答案/正确节点

#### Hit Rate（命中率）：Top-K 里是否至少命中一个相关文档

#### MRR（平均倒数排名）：第一个相关文档排名倒数的平均值

#### Faithfulness（忠实度）：答案论断能否被召回上下文支撑（防幻觉）

#### Relevancy / Answer Relevancy（相关性）：答案是否切题、答到点子上

#### Correctness（正确性）：相对标准答案的正确程度（常 1~5 分）

#### Context Precision：召回上下文的排序质量（相关的是否靠前）

#### Context Recall：召回上下文相对参考答案的信息完整度

#### RetrieverEvaluator：LlamaIndex 检索评估器（Hit Rate / MRR）

#### BatchEvalRunner：LlamaIndex 异步批量评估，适合 A/B 对比

#### RAGAS：专业 RAG 评估框架，多数指标可免人工标注

#### garbage in, garbage out：检索错了，再强的生成也救不回来

### 一、为什么要评估 RAG？

#### 三个核心环节都可能出问题

##### 1 检索 Retrieval

###### 问：召回的文档对不对、全不全？

###### 检索错了 → garbage in, garbage out

##### 2 生成 Generation

###### 问：有没有忠实使用召回资料？还是自己编（幻觉）？

##### 3 端到端 End-to-End

###### 问：最终答案准不准、切不切题、全不完整？

#### 评估目标：量化质量 → 定位瓶颈 → 驱动优化

#### 关键诊断思路（必背）

##### 最终答案很差时，先看检索指标

##### 检索没召回正确文档 → 锅在检索侧：分块 / Embedding / 重排 / 混合检索

##### 检索召回了对但答案仍错 → 锅在生成侧：Prompt / 上下文压缩 / 换模型

#### 还能量化优化收益：比如加重排后 Hit Rate / Faithfulness 提升了多少

### 二、核心评估指标

#### 两大类：检索质量 + 生成质量，正好对应两个环节

#### 2.1 检索质量 Retrieval Quality

##### 衡量：召回的文档对不对

##### 前提：带标注的数据集（每题标注哪些文档/节点正确）

##### Hit Rate（命中率）

###### 定义：检索结果中是否包含至少一个相关文档

###### 公式直觉：命中题数 / 总题数

###### 高=少漏；低=经常捞不到正确答案所在块

##### MRR（Mean Reciprocal Rank，平均倒数排名）

###### 定义：第一个相关文档排名倒数的平均值

###### 公式直觉：Σ (1/rank_first_hit) / N；没命中记 0

###### 高=相关文档排得靠前；低=相关的在很后面或没有

##### 常用组合：Hit Rate + MRR；LlamaIndex RetrieverEvaluator 内置

##### 还可关注：Precision@K / Recall@K（与第 09 章召回率/精确率同思路）

#### 2.2 生成质量 Generation Quality

##### 衡量：答案好不好

##### LlamaIndex 三维互补；前两个常可不需人工标准答案

##### Faithfulness 忠实度

###### 只关心：答案有没有出处、是否被上下文支撑

###### 注意：答错题但忠于资料也可能算忠实 → 必须和相关性一起看

##### Relevancy 相关性

###### 关心：答没答到点子上、是否切题

##### Correctness 正确性

###### 需要 reference 标准答案，最接近考试打分

###### 常见输出：1~5 分 + feedback 评语

#### 2.3 在项目周期怎么使用

##### 开发期（快速迭代）

###### 多用 Faithfulness + Relevancy（免标注、反馈快）

###### 小样本 Hit Rate / MRR 盯检索改造（分块/重排/混合）

##### 上线前（卡质量门禁）

###### 加上 Correctness + 黄金问答集

###### BatchEvalRunner：基础 RAG vs 优化 RAG 对比分数

##### 上线后（回归）

###### 固定评测集，每次改链路后复跑，防止「优化 A 坏了 B」

###### 指标掉点 → 回滚或定位是检索侧还是生成侧

##### 原则：同一套题、同一裁判温度，前后才可对比

### 三、示例代码（LlamaIndex 内置评估器）
讲义用通义千问当裁判；本仓库可用 DeepSeek 等同理替换 Settings.llm。

#### 1 准备有干扰信息的文档

##### 文件：data/company_info.txt（贝壳科技示例）

##### 正文含：上班 9:00-18:00、员工 2000、业务 AI/大数据/云计算 等

##### 故意掺干扰

###### 合作公司上班 10:00-19:00（易混淆）

###### 子公司员工 300、业务销售（易混淆）

###### 考勤曾调整又恢复（噪声句）

##### 目的：逼出「捞到干扰句 → 幻觉/答错」的真实场景，方便评估器抓问题

#### 2 生成质量：Faithfulness + Relevancy + Correctness

##### 依赖：llama-index-core + dashscope llm/embedding（讲义）

##### 裁判模型：温度设 0，保证打分稳定可复现

##### 三个评估器

###### FaithfulnessEvaluator：答案是否被召回上下文支撑

###### RelevancyEvaluator：答案+上下文是否切题

###### CorrectnessEvaluator：答案 vs reference，1~5 分

##### 调用要点

###### evaluate_response(query, response)：自动从 response.source_nodes 取上下文

###### 忠实度/相关性：.passing + .score(0/1)

###### 正确性：.evaluate(..., reference=...) → .score(1~5) + .feedback

##### 示例 qa_pairs

###### 上下班时间？→ 9:00-18:00，午休 12:00-13:00

###### 员工总数？→ 2000人

###### 主营业务？→ AI软件开发、大数据服务、云计算平台

#### 3 检索质量：Hit Rate + MRR

##### 意义：生成评估只说「答案好不好」，定位不了检索锅还是生成锅

##### RetrieverEvaluator / 或手写：aretrieve → 判断是否命中 → 算 Hit/MRR

##### 讲义手写版流程

###### SentenceSplitter(chunk_size=120, overlap=20) 建节点

###### retriever = index.as_retriever(similarity_top_k=2)

###### 每题配 keywords：命中任一关键词即视为相关（简化 Ground Truth）

###### Hit Rate = 命中次数/总题数

###### MRR：第一个相关文档的 1/rank，未命中为 0，再平均

##### 生产更稳：用节点 ID 作黄金标准，而不是关键词模糊匹配

##### 调 top_k / 分块 / 重排后复跑 → 量化检索优化是否有效

#### 4 对比「基础 RAG vs 优化 RAG」：批量评估

##### 最大用处：量化优化收益（前后分数差）

##### 工具：BatchEvalRunner 异步批量跑，比逐题 evaluate 快

##### 讲义对比设定

###### 基础：similarity_top_k=2 的朴素 query_engine

###### 优化：加重排或上下文压缩，过滤干扰句

###### 同一套问题跑 Faithfulness / Relevancy 等，打印对比表

##### 和本仓库对照：关/开 HYBRID、RERANK、COMPRESS、CRAG 做四组 A/B

### 四、RAGAS 等专业评估框架（了解）

#### 4.1 RAGAS 是什么

##### 全称：Retrieval Augmented Generation Assessment

##### 专门为 RAG 流水线设计的自动化评估框架

##### 核心理念三点

###### Reference-free：多数指标免人工标准答案，用 LLM-as-a-judge

###### 检索+生成分别诊断：指标明确归侧，方便定位瓶颈

###### 与 LlamaIndex / LangChain 无缝集成，复用现有引擎

##### 定位：LlamaIndex 内置=轻量快接入；RAGAS=系统、指标更丰富的基准

#### 4.2 RAGAS 核心指标（四个最常用）

##### Faithfulness（生成侧）

###### 把答案拆成若干 claim（论断）

###### 逐条看能否由上下文支撑

###### 分数 = 被支撑论断数 / 总论断数

##### Answer Relevancy（生成侧）

###### 让 LLM 根据答案反向生成可能的问题

###### 算这些问题与原始问题的相似度 → 越接近越切题

##### Context Precision（检索侧）

###### 对照 reference，看召回上下文的排序质量

###### 相关片段是否靠前

##### Context Recall（检索侧）

###### 对照 reference，看召回上下文的信息完整度

###### 答对所需信息有没有被捞全

### 五、小结与评估闭环

#### ① 先看检索指标：定位是检索还是生成的问题

#### ② 针对性优化：分块 / 重排 / 压缩 / Prompt / CRAG…

#### ③ 同一套评估复跑：对比前后分数，量化收益

#### ④ 固化评测集：上线后做回归，防止越改越差

### 六、和本仓库 chroma文档管理 怎么接

#### 现状

##### 主链路已有 Pre/Mid/Post/CRAG，但没有独立评估脚本模块

##### 可先用讲义脚本对 data/ 或导出的问答集评测

#### 最小落地建议

##### 准备 20~50 条黄金问答（含 reference）

##### 对 /ask 的 answer + sources 跑 Faithfulness/Relevancy/Correctness

##### 对 _build_retriever 跑 Hit Rate/MRR（节点 ID 标注更好）

##### 开关矩阵：rewrite/hyde × hybrid × rerank × compress × crag

#### 诊断映射到第 08~13 章

##### Hit/MRR 低 → 08 改写/HyDE、09 混合、10 重排

##### Faithfulness 低 → 10 压缩、Prompt 约束、12 CRAG 过滤噪声

##### Relevancy 低 → 改写问句、提高精排、检查干扰文档

##### Correctness 低但检索好 → 换生成模型/加强「仅依据资料」

## 15 Modular RAG（模块化）
飞书：01_Modular RAG
https://ecnwvcdzorsp.feishu.cn/docx/DpNhdZLgRoqBGZxwdQfch7DFnRe
Gao 综述：把固定流水线变成可插拔、可编排的模块框架；课堂 demo01_modular_rag.py + 本仓库 presets / RagAskService。

### 〇、总览

#### 一句话：像搭积木一样组合查询改写、多路检索、融合、重排、压缩，用配置控制顺序与启停

#### 论文：Gao et al. Retrieval-Augmented Generation for Large Language Models: A Survey（2023/2024）

#### 从「一条固定流水线」走向「可编排框架」（orchestration）

#### 作业落点：chroma文档管理 的预设 + 勾选 = 线性可插拔 Modular RAG

### 术语定义（本章必背）

#### Modular RAG：把 RAG 拆成独立、可插拔、可重配置模块的架构范式

#### Orchestration（编排）：用流程控制模块的执行顺序、条件与分支

#### Module Type（模块类型）：Pre-Retrieval / Retrieval / Post-Retrieval / Generation

#### Module（模块）：类型下的功能单元，如 Hybrid Search、Rerank、Compress

#### Operator（算子）：模块下可替换实现，如 DashScopeRerank vs 本地 bge

#### Naive RAG：查询→向量检索→生成，无前后优化

#### Advanced RAG：在固定线性上加检索前/后优化（改写、重排、压缩）

#### QueryFusionRetriever：LlamaIndex 多路融合器，常用 RRF（reciprocal_rerank）

#### Multi-Query：LLM 生成多个查询变体再检索融合（num_queries>1）

#### HyDE：先写假想答案文档再检索；假想文不当事实引用

#### PRESETS：basic / hybrid_search / advanced / full_optimization 一键组合

### 第一部分：理论介绍

#### 1.1 什么是 Modular RAG？

##### 拆分：独立 + 可插拔 + 可重配置

##### 对比传统「向量检索 + 生成」：可增删替换模块，不绑死顺序

##### 三代对照（讲义示意图）

###### Naive RAG：查询 → 向量检索 → 大模型 → 答案

###### Advanced RAG：查询 →[检索前/改写]→ 向量检索 →[重排/压缩]→ 大模型 → 答案

###### Modular RAG：查询 →[改写]→[多路检索]→[融合]→[重排]→[压缩]→[生成]；中间可按配置增删换序

#### 1.2 RAG 的三个发展阶段

##### 第一代 Naive RAG（朴素）

###### 特征：检索 → 生成，一条直线流水线

###### 局限：检索质量差、召回不准、上下文冗余、易幻觉

##### 第二代 Advanced RAG（高级）

###### 特征：检索前后加入优化——查询改写、分块、重排、压缩

###### 局限：流程仍是固定线性，难以针对不同查询动态调整

##### 第三代 Modular RAG（模块化）

###### 特征：模块化 + 可编排；支持新模块、条件/分支/循环/自适应

###### 代价：工程复杂度更高，需要编排框架支撑

##### 两个关键突破

###### 新模块 New Modules：Search / Memory / Routing / Predict / Task Adapter 等

###### 新模式 New Patterns：条件、分支、循环、自适应（Rewrite-Retrieve-Read、Recursive、Self-RAG 等）

#### 1.3 核心模块（讲义落地的那一组）

##### Indexing：文档→切块→向量索引

##### Query Transformation：HyDE / Multi-Query / 清洗重写

##### Retrieval：稠密向量 + 稀疏 BM25（jieba）

##### Fusion：RRF / relative_score / simple

##### Reranking：Cross-Encoder 精排

##### Compression：句子级上下文压缩

##### Generation：RetrieverQueryEngine / synthesizer + LLM

##### 综述里还可有：多源 Search、Memory、Routing、Predict、Task Adapter（本仓库未全做）

#### 1.4 三层抽象：模块类型 → 模块 → 算子

##### 模块类型：Pre-Retrieval / Retrieval / Post-Retrieval / Generation

##### 模块：Query Transformation、Hybrid Search、Rerank、Compress …

##### 算子：同一模块换实现——HyDE vs Multi-Query vs Step-Back；DashScopeRerank vs SentenceTransformerRerank

##### 例子：Pre-Retrieval → Query Transformation → {HyDE, Multi-Query, Step-Back}

##### 工程含义：换重排算法、加一路检索 = 插拔算子，不必重写整条流水线

#### 1.5 编排：RAG Flow 的典型模式

##### 线性 Linear：改写→检索→融合→重排→压缩→生成（demo /ask 主路径）

##### 条件 Conditional：先路由——闲聊直接答、知识题才检索（本仓库 Self-RAG Retrieve）

##### 分支 Branching：多路检索/多数据源并行再融合（向量+BM25）

##### 循环 Loop：检索→生成→评估，不行就改写再检（CRAG、Self-RAG ISSUP）

##### 讲义主类先落地「线性可插拔」：config 开关启停，不改主流程代码

#### 1.6 模块化设计的优势

##### 可组合性：混合+重排，或纯向量

##### 可扩展性：新加一路检索器不影响其余模块

##### 可替换性：换 embedding / rerank 算子

##### 可测试性：模块可独立测、独立评估（接第 14 章）

##### 可优化性：针对瓶颈模块专项优化

### 第二部分：LlamaIndex 完整实现（= demo01_modular_rag.py）
讲义用 DashScope；本仓库问答默认可 DeepSeek，向量可本地 bge / 千问 SafeDashScopeEmbedding。

#### 能力清单（讲义打勾项）

##### jieba 中文分词 BM25

##### HyDE / Multi-Query

##### 向量 + BM25 多路

##### QueryFusionRetriever RRF

##### 重排（讲义 DashScopeRerank；本仓库默认可本地 bge）

##### SentenceEmbeddingOptimizer 压缩

##### RetrieverQueryEngine + LLM 生成

##### 配置驱动模块开关

#### 2.1～2.2 环境与全局配置

##### pip：llama-index-core、bm25、jieba；可选 dashscope embedding/llm/rerank

##### Settings.embed_model + Settings.llm

##### SafeDashScopeEmbedding：每批≤10，避开千问批量硬限制

##### LLM temperature 宜偏低，便于改写/判断稳定

#### 2.3 Indexing

##### Document → SentenceSplitter → VectorStoreIndex

##### nodes 要留给 BM25 复用，避免重复分块

##### 本仓库：engine.py 切块写入 Chroma

#### 2.4 Retrieval：向量 + BM25

##### 路1：index.as_retriever 稠密语义

##### 路2：BM25Retriever + jieba.cut 关键词

##### 本仓库：retrieval_optimize.build_hybrid_retriever

#### 2.5 Fusion + Multi-Query

##### QueryFusionRetriever(retrievers, mode, num_queries)

##### num_queries=1：只多路融合；>1：再生成查询变体

##### mode：reciprocal_rerank（RRF）/ relative_score / simple

##### 本仓库：AskRequest.num_queries + fusion_mode

#### 2.6 HyDE

##### 讲义：HyDEQueryTransform(include_original=True) 包一层 TransformQueryEngine

##### 本仓库：strategy=hyde，清洗句+假想文档双路检索，假想文不进 sources

#### 2.7～2.8 重排与压缩

##### node_postprocessors 串行：先精排再压缩

##### 讲义重排：DashScopeRerank(qwen3.7-text-rerank)

##### 压缩：SentenceEmbeddingOptimizer + 中文分句；percentile_cutoff=0.5

##### 本仓库另加 LongContextReorder（对抗 Lost in the Middle）

#### 2.9 ModularRAG 主类 + PRESETS

##### index_documents：Indexing → 两路检索 → Fusion → postprocessors → QueryEngine → 可选 HyDE 外包

##### query()：query_engine.query，打印 source_nodes 与答案

##### basic：simple 融合，关重排/压缩/HyDE

##### hybrid_search：RRF，关后处理

##### advanced：num_queries=3 + 重排 + 压缩

##### full_optimization：再开 HyDE

##### 本仓库 presets.py 同名四档，并映射 use_pre/CRAG 等作业开关

#### 2.10 调用测试：preset=full_optimization，对示例库问 RAG/Python/ML/BM25

### 第三部分：用配置驱动模块编排

#### 3.1 代码字典控制逻辑

##### 三个模块类：检索前 / 检索中 / 检索后，各自只干一类事

##### 主类按 config 字典 if 开关组装，不写死流水线

##### 调用文件只传配置 + 提问

#### 3.2 完整案例目录（讲义 rag_tools）

##### shared.py：共享 LLM/Embedding/工具

##### before_refine.py：检索前

##### middle_refine.py：检索中

##### after_refine.py：检索后

##### rag_main.py：主类编排

##### main.py：入口

##### 对照本仓库

###### before ≈ pre_retrieval.py

###### middle ≈ retrieval_optimize.build_hybrid_retriever

###### after ≈ apply_postprocessors + crag/self_rag

###### rag_main ≈ rag_service.RagAskService

###### main ≈ app/main.py + static/index.html 勾选

#### 3.3 YAML 读配置

##### 讲义：YAML 描述开关，代码读取后交给主类

##### 本仓库：.env（HYBRID/RERANK/…）+ 请求体 JSON 覆盖 + 前端预设

#### 3.4 强类型配置类

##### 讲义：dataclass / 类型化 Config，减少字典拼写错误

##### 本仓库：Pydantic AskRequest / OptimizeFlags（OpenAPI 即文档）

### 对照 chroma文档管理（交作业用）

#### 线性可插拔：/ask 按勾选组装，对应讲义 ModularRAG

#### 条件：Self-RAG Retrieve 闲聊不检索

#### 分支：向量+BM25 融合

#### 循环：CRAG 改写重检；ISSUP 不足则重写答案

#### 预设四档名称与 demo01 对齐，full_optimization 本仓库还叠了 CRAG

#### 未按讲义做：YAML 配置文件、Step-Back 算子、TransformQueryEngine 外包 HyDE

#### 多出来：Chroma 持久化、Web 勾选、CRAG、Self-RAG、Hit/MRR 评估

#### 演示：页面选 full_optimization 或 advanced，看「本次优化」标签讲模块插拔

## 16 知识图谱（Neo4j / GraphRAG）
飞书：01-知识图谱
https://ecnwvcdzorsp.feishu.cn/docx/IYDbddFpSoRqwpxW8fJceOWjnBd
密码：24V74&68
环境：JDK + Neo4j Community + Python neo4j 驱动；与向量 RAG 并行的图谱通道。

### 〇、总览

#### 一句话：用图（实体-关系-属性）存结构化知识，支持多跳推理；无大模型也可独立使用

#### 2012 谷歌提出 Knowledge Graph；与大数据、深度学习并称驱动 AI 的核心力量之一

#### 本仓库落点：先装 Neo4j + JDK，再用 Cypher / Python neo4j 做 GraphRAG 双通道

### 术语定义（本章必背）

#### 知识图谱 KG：用图结构表示知识；节点=实体/概念，边=关系/属性

#### 实体 Entity：具体事物（人、公司、产品）；概念 Concept：抽象类型

#### 三元组 SPO：Subject-Predicate-Object，数据层基本单元

#### 模式层 Schema / 本体 Ontology：类型、属性、关系、约束的「骨架」

#### 数据层 Data Layer：具体实例与事实（「血肉」）

#### GraphRAG：用图查询做全局聚合/多跳推理，而非只找相似文本

#### 实体链接 Entity Linking：把查询里的提及对齐到图谱实体

#### Cypher：Neo4j 声明式图查询语言（类比 SQL）

#### Neo4j：Java 实现的开源图数据库；社区版免费单点，企业版收费高可用

### 一、知识图谱介绍

#### 1、没有大模型的知识图谱架构

##### 用户查询（自然语言或结构化）

##### 关键词/规则匹配 → 实体识别

##### 或直接写 Cypher / SPARQL

##### 图数据库执行（Neo4j / JanusGraph）→ 精确结果

##### 模板化回答 / 直接展示图谱路径

##### 要点：KG 比大模型早很多年，传统上可独立使用

#### 2、大模型增强图谱 vs 传统方案

##### 构建成本：传统高（人工 schema/规则）｜LLM 增强低（自动抽取）

##### 灵活性：传统低（预定义问法）｜LLM 高（开放域问答）

##### 准确率：传统极高（结构化查询）｜LLM 中等（有幻觉风险）

##### 推理深度：传统受图遍历步数限制｜LLM 可增强复杂推理

##### 维护成本：传统高｜LLM 增强相对低（可动态更新）

##### 响应速度：传统毫秒级｜LLM 秒级（含模型调用）

##### 可解释性：传统白盒可追溯路径｜LLM 灰盒

#### 3、介绍与定义

##### 3.1 什么是知识图谱

###### 3.1.1 什么是知识

###### 数据：226.1cm、229cm —— 无语境的客观数值

###### 信息：「姚明臂展 226.1cm」「身高 229cm」—— 事实陈述

###### 知识：把属性整合抽象，形成对姚明的认知（比普通人高）

###### 3.1.2 什么是图谱

###### Graph：图论中事物与事物相互连接的结构

###### 由节点 Vertex + 边 Edge 构成；多关系图可有多类节点/边

###### 3.1.3 知识图谱

###### 本质：语义网络；节点=概念/实体，边=关系/属性

###### 简化说法：实体 + 实体间关系

###### 组成三件套：Entity / Relation / Attribute

###### 3.1.4 示例（苹果/乔布斯）

###### 文本：「苹果创始人是乔布斯，1976 成立，总部库比蒂诺」

###### 图：乔布斯─创始人→苹果─成立于→1976；苹果─总部→库比蒂诺

##### 3.2 知识图谱检索 vs 向量检索
讲义表格多为插图；核心对比见下

###### 向量：语义相似、模糊召回，弱于精确关系与多跳

###### 图谱：精确路径、多跳遍历、全局聚合；弱于开放语义

###### 实践：二者互补 → 混合双通道

##### 3.3 在 RAG 中的三种应用模式

###### 模式1 GraphRAG · 全局推理

###### 例：公司所有产品的共同技术？

###### 传统 RAG：需塞入大量产品文本，易漏、上下文爆炸

###### GraphRAG：公司─produces→产品─uses→技术 X，直接聚合

###### 升级：从「找相似文本」→「执行图查询」

###### 模式2 实体链接增强 · 精准定位

###### 例：乔布斯的创业伙伴？

###### 向量：可能命中传记任意段落

###### 图谱：识别实体→遍历联合创始人→沃兹尼亚克 + 文本

###### 优势：消歧 + 精准召回关系型信息

###### 模式3 混合架构 · 向量+图谱双通道

###### 向量通道：语义相似检索

###### 图谱通道：实体识别 → 1~2 跳子图 → 对应文本

###### 结果融合后再交给 LLM

##### 3.4 知识图谱构建流程

###### 1 实体抽取 NER：人名/地名/组织/产品（spaCy、BERT-NER、GPT）

###### 2 关系抽取：「乔布斯」─创立→「苹果」

###### 3 图谱存储：Neo4j / NebulaGraph / RDF 三元组

###### 4 与向量库关联：实体/关系链回原文，支持图谱↔文本双向导航

##### 3.5 优势场景
讲义多为表格/图；常见于多跳、关系查询、全局聚合

###### 多跳关系问答、股权穿透、依赖链路

###### 需精确实体对齐、可解释路径的场景

###### 与向量检索互补，而非替代

##### 3.6 典型应用

###### 搜索引擎 / 智能助手问答

###### 金融：风控、评级、反欺诈

###### 医疗：知识库、辅助诊断、药物研发

###### 教育：知识点图谱、智能答疑

###### 电商推荐 / 社交关系挖掘 / 物联网

###### 商业 KG：工商股权投资关系分析

###### 教育 KG：教材笔记→知识点组织→问答底座

##### 3.7 挑战
讲义插图为主

###### 构建与维护成本、schema 演进

###### 抽取噪声、实体对齐与冲突消解

###### 与向量结果的融合策略设计

##### 3.8 与 Advanced / Modular RAG 对比

###### 已有：Multi-Query→混合检索→RRF→Rerank→LLM

###### 升级：并行加「实体识别→图谱查询→子图召回」再融合

###### 策略建议：图谱结果优先处理关系/多跳，向量结果补充语义

### 二、分层架构

#### 总述：模式层=骨架；数据层=血肉；相互依存

#### 1、模式层 Schema Layer

##### 1.1 定义：概念模型与逻辑结构；类比数据库表结构设计

##### 1.2 关键组成（本体 Ontology）

###### 实体类型 Class：人 / 电影 / 公司

###### 数据属性 Data Property：连实体→基本类型

###### 对象属性 Object Property：连实体→实体（即关系）

###### 关系类型 Relation Type：执导 / 就职于 / 位于

###### 约束 Constraint：如一人一个出生日期、评分 1–10

##### 1.3 核心作用

###### 统一表示标准，减少歧义

###### 支撑逻辑推理

###### 简化查询；指导抽取与融合质量

##### 1.4 常见表示语言

###### RDFS：基础模式定义

###### OWL：更强本体与推理

###### SHACL：RDF 数据约束

#### 2、数据层 Data Layer

##### 2.1 定义：模式的实例化；大量 SPO 三元组

##### 2.2 组成

###### 实体实例：吴京、《流浪地球2》

###### 属性值实例：出生日期=1974-04-03

###### 关系实例：吴京参演《流浪地球2》

##### 2.3 作用：承载内容、支撑问答/推荐/搜索、可持续扩实例

#### 3、两层关系

##### 模板与实例：数据必须符合模式定义

##### 抽象与具体：模式是概括，数据是事实

##### 相互促进：数据积累可反馈扩展模式（如新增「客串」关系）

### 三、技术架构

#### 1、数据获取

##### 业务库表（结构化，半公开/内部）

##### 网络公开网页（非结构化）

##### 三种形态：结构化 / 半结构化 / 非结构化 → 不同处理法

#### 2、信息抽取 IE【核心】

##### 目标：从异构源自动抽候选知识单元

##### 实体抽取 Entity Extraction

###### NER：人/地/组织/日期/货币等

###### 方法：规则、统计、深度学习

##### 关系抽取 Relation Extraction

###### 作者/工作/亲属等关系

###### 方法：有监督统计或深度学习

##### 属性抽取 Attribute Extraction

###### 实体特征：职业、经纬度等

###### 可把「实体-属性值」看作名词性关系 → 常转为关系抽取

#### 3、知识融合 Knowledge Fusion

##### 消除冗余、统一表达、解决冲突、知识扩展

##### 关键技术：指代消解、实体消歧/链接、实体对齐、关系对齐

#### 4、知识加工 Knowledge Processing

##### 本体构建：定义层级与约束（人工或半自动）

##### 知识推理：规则 / TransE·RotatE 嵌入 / 路径推理 → 知识补全

##### 质量评估：可信度打分与人工甄别

##### 结果：零散事实 → 结构化、网络化、可推理的知识体系

### 四、Neo4j 数据库

#### 1、介绍

##### Java 实现的开源 NoSQL 图库；2003 研发，2007 首版

##### 完整数据库特性：ACID、集群、备份与故障转移

##### 企业版：付费，高可用/热备份；社区版：免费，单点

#### 2、图数据概念

##### 节点 Node：主数据元素；可有多属性、多标签（类比表/表名）

##### 关系 Relationship：有向；可有属性

##### 属性 Property：键值对；可索引与约束

##### 标签 Label：分组节点；建索引加速查找

#### 3、Windows 安装四步（讲义）

##### 第一步：安装 JDK

###### Oracle JDK 或 OpenJDK 17+

###### 验证：java --version

##### 第二步：下载 Neo4j Community

###### https://neo4j.com/deployment-center/?community

###### 解压路径不要含中文

##### 第三步：环境变量

###### 新建 NEO4J_HOME = 解压目录

###### Path 追加 %NEO4J_HOME%\bin

##### 第四步：启动

###### cmd：neo4j console

###### 浏览器：http://localhost:7474/

###### 默认用户/密码均为 neo4j，首次登录须改密

###### 若报错缺 Java → 先装好 JDK

#### 4、Cypher 简介

##### 声明式图查询语言；Neo4j 是标准制定者（openCypher）

##### 4.1 基本符号

###### () 节点；(n) 任意节点

###### (:Label) 如 (p:Person)

###### ({key:value}) 如 (p:Person {name:'乔布斯'})

###### --> 有向关系；-[:TYPE]-> 带类型

###### -[:TYPE {prop:val}]-> 带属性关系

##### 4.2 CRUD 要点

###### CREATE：创建节点/关系

###### MERGE：不存在才创建（条件创建）

###### MATCH … WHERE：查询与条件过滤

###### 例：CREATE (a:Person {name:'张三疯', age:30})

###### 例：先 MATCH 两节点再 CREATE 关系

### 五、本机环境清单

#### JDK 17+（JAVA_HOME）

#### Neo4j Community（NEO4J_HOME + neo4j console）

#### Python：pip install neo4j（官方驱动）

#### 可选：llama-index 图谱相关包、spaCy NER（后续实验再加）

## 17 GraphRAG 的使用（LlamaIndex + Neo4j）
飞书：02_GraphRag的使用
https://ecnwvcdzorsp.feishu.cn/docx/N1g7d1g9GodJ5wxvjKicYDJrnVc
密码：2763X6#3
第 16 章是理论+Cypher；本章把文档→抽三元组→Neo4j→自然语言问答打通。
本仓库：graph_rag.py；LLM 默认 DeepSeek，Embedding 默认 Chinese-CLIP（DeepSeek 无向量接口）。

### 〇、总览：和上一章怎么接

#### 上一章：知识图谱理论、构建流程（NER→关系抽取→入库）、手写 Cypher 操作 Neo4j

#### 本章：用 LlamaIndex PropertyGraphIndex 自动从非结构化文本抽三元组并问答

#### 讲义默认千问 DashScope；本仓库可用 DeepSeek 抽取/生成 + 本地 Chinese-CLIP 向量

#### 核心工作流

##### Documents → kg_extractors（LLM 抽三元组）

##### 实体-关系-实体 + 文本块 → Neo4jPropertyGraphStore（+ 实体节点向量）

##### as_query_engine / as_retriever → 实体检索 + 图遍历 → LLM 生成

### 术语定义（本章必背）

#### PropertyGraphIndex：LlamaIndex 属性图索引，管抽取、落库、问答

#### Neo4jPropertyGraphStore：把属性图接到 Neo4j Bolt

#### SimpleLLMPathExtractor：开放式抽路径，不限类型，噪声大

#### SchemaLLMPathExtractor：限定实体/关系/合法三元组，生产更稳

#### embed_kg_nodes：给图谱节点做向量，才能语义召回实体

#### from_existing：从已有 Neo4j 加载索引，不再重新扫文档

#### LLMSynonymRetriever：用 LLM 把问句关键词扩成同义词去匹配实体

#### VectorContextRetriever：用向量语义召回相关实体，再沿图走邻居

### 1、环境准备

#### pip：llama-index-core / llms-dashscope / embeddings-dashscope / graph-stores-neo4j

#### 本仓库还可能用 llama-index-llms-deepseek + 本地 Chinese-CLIP

#### Neo4j 已启动：bolt://localhost:7687，用户名密码配好

#### 需 APOC 插件（部分图存储操作依赖）

#### 讲义：DASHSCOPE_API_KEY；本仓库：DEEPSEEK_API_KEY + NEO4J_PASSWORD

### 2、全局配置：LLM + Embedding

#### 讲义：Settings.llm = DashScope(qwen-plus)；Settings.embed_model = DashScopeEmbedding(text-embedding-v4)

#### 抽取对指令遵循要求高，不要用过小的模型

#### Embedding 给每个实体节点做向量，用于语义召回

#### 本仓库注意：不要用全局 Settings 冲掉向量引擎的模型；GraphRagService 用自己的 llm/embed_model

#### DeepSeek 无 Embedding API → 图谱向量用 Chinese-CLIP / HuggingFace / 千问

### 3、连接 Neo4j 图存储

#### Neo4jPropertyGraphStore(username, password, url=bolt://localhost:7687)

#### Bolt 是 7687，浏览器是 7474，不要填错

#### 密码必须是首次改密后的密码，空密码连不上

### 4、自动构建知识图谱

#### 方式一 SimpleLLMPathExtractor（开放式）

##### 不限定实体/关系类型，LLM 自由抽路径

##### 适合探索、demo、schema 未定

##### 风险：类型乱、关系名不统一、噪声三元组多

##### 参数例：max_paths_per_chunk、num_workers

#### 方式二 SchemaLLMPathExtractor（生产推荐）

##### possible_entities：如 PERSON / COMPANY / SCHOOL / LOCATION

##### possible_relations：如 CO_FOUNDED / STUDIED_AT / LOCATED_AT

##### kg_validation_schema：合法三元组，如 PERSON-CO_FOUNDED-COMPANY

##### strict=True：不符合 schema 的丢掉

##### max_triplets_per_chunk：每块最多抽几条

#### from_documents 要点

##### kg_extractors=[抽取器]

##### property_graph_store=graph_store

##### embed_kg_nodes=True：节点可语义检索

##### show_progress=True

##### 示例文本：乔布斯/沃兹/苹果/库比蒂诺

#### 空库不要 from_existing；先 build 再问答

#### 前端也可手工写入三元组（不走 LLM 抽取）

### 5、自然语言问答

#### 加载：PropertyGraphIndex.from_existing(property_graph_store, embed_kg_nodes=True)

#### Embedding 必须与构建时一致，否则向量对不上

#### as_query_engine

##### include_text=True：答案带来源文本

##### similarity_top_k：召回实体/子图条数

##### 内部：同义词实体匹配 + 向量召回实体 + 图遍历邻居 + LLM 生成

##### 例：沃兹尼亚克的母校？和谁一起创立苹果？

#### as_retriever

##### 只拿子图/节点，自己后续处理或与向量通道融合

##### 本仓库 /ask 双通道：图谱片段标 [图谱] 拼在向量结果前

#### 只走图：前端「图谱问答」→ POST /graph/query

### 6、LlamaIndex 方案 vs 手写 Cypher

#### Cypher：精确路径、毫秒级、白盒可解释；要会写 MATCH，问法受 schema 限制

#### LlamaIndex GraphRAG：自然语言、自动抽取、开放问法；抽取可能幻觉、速度秒级

#### 实践：schema 约束抽取 + 必要时手工三元组/Cypher 补洞 + 向量通道补语义

#### 不要用 GraphRAG 替代所有向量检索：多跳/关系题走图，模糊语义走向量

### 和本仓库的对应

#### graph_rag.py：build_from_texts / files / add_manual_triple / query / retrieve

#### 路由：/graph/build /triple /load /query /retrieve

#### AskPipeline 的 graph_retrieve 模块；预设 graph_hybrid

#### Neo4j 未开：向量 RAG 照常用，图谱跳过

## 18 多模态 RAG（LlamaIndex + Chinese-CLIP）
飞书：01_多模态RAG(llamaxIndex)
https://ecnwvcdzorsp.feishu.cn/docx/FlQQdIjlpo5o3IxjyTtcZiXgnNy
密码：8&2L3413
本仓库已有 ChineseCLIPEmbedding（文本塔），用于向量/图谱 embedding；完整图文索引与看图作答是本课进阶，可继续接到 LlamaIndex MultiModal。

### 第一部分：课程概述与预备知识

#### 1、什么是多模态 RAG（MRAG）

##### 传统 RAG 主要处理纯文本；PDF/手册里的图、表、扫描件常被丢掉或变成无意义占位

##### MRAG：同时处理文本、图像、音频、视频等，跨模态对齐到统一/可比较空间

##### 核心能力：以文搜图、以图搜图、图文混合问答

##### 严格「以图搜文」需要图和文在同一向量空间；实践常是以图搜图再带描述，或先 LMM 看图成文再检索

#### 2、为什么需要

##### 企业文档约 50%~80% 关键信息在图表/流程/截图里

##### 用户会问「架构图里网关在哪一层」「第 12 页红按钮做什么」——离开图像答不了

##### 电商以图搜商品、医疗以影像找相似病例

##### LMM 能看图说话，比只靠 OCR 二手文字更靠谱

##### 一句话：检索和生成都建立在文档的全部信息上，不只文字

#### 3、技术架构三大件

##### 多模态编码器：把文本/图像编到统一或可比较向量空间

##### 向量库：常分文本集合 + 图像集合，做跨模态近邻检索

##### 多模态大模型 LMM：吃图文混合上下文再生成

##### 数据流：解析→图文分块→向量化→入库→跨模态检索→重排/融合→图文 Prompt→LMM→输出

### 第二部分：关键流程模块

#### 1 文档解析与分块：PDF 抽图+抽文；图块保留视觉，文本块保留段落；元数据绑页码/图号

#### 2 Embedding：文本塔 + 图像塔（CLIP 类）；维数必须一致才能比

#### 3 存储：向量 + 元数据（路径、caption、bbox）；图文可分 collection

#### 4 语义检索：文查文、文查图、图查图；以图搜文要同一空间或走转换路径

#### 5 融合：多路召回（文/图）再 RRF 或加权

#### 6 构建多模态 Prompt：文本片段 + 图像一起塞给 LMM

#### 7 LMM 生成：看图+读文作答，要求引用图号/页码

#### 8 输出：答案 + 引用图/文来源

### 第三部分：核心技术原理

#### 1、统一向量空间（基石）

##### 对比学习：图文配对拉近、非配对推远（CLIP）

##### 同一空间才能「文字描述」命中「图片」

##### 中文要用中文 CLIP（Chinese-CLIP），英文 CLIP 对中文对齐差

#### 2、两种检索策略

##### 策略 A：双塔 CLIP——查询编一次，和库里向量做 ANN

##### 策略 B：先把图变成文字（caption/OCR）再走纯文本 RAG，实现简单但损失视觉细节

##### 选择：要精细看图选 A+LMM；只要图意大意选 B 更快

#### 3、多模态大模型 LMM：GPT-4o、Qwen-VL、Gemini 等，负责看图作答而不是只做检索

#### 4、进阶 ColPali / late-interaction

##### 把整页当图像，用视觉 token 与查询 late interaction

##### 适合扫描件、复杂版式，少依赖 OCR

##### 代价：算力和存储高于双塔 CLIP

### 第四部分：LlamaIndex 实现——图文双向检索

#### 1、为什么不用内置 ClipEmbedding

##### 官方 CLIP 以英文为主，中文 query/文档对齐差

##### 课程用自定义 Chinese-CLIP 接到 LlamaIndex BaseEmbedding

#### 2、环境准备

##### transformers + torch；本地权重如 chinese-clip-vit-base-patch16

##### LlamaIndex MultiModalVectorStoreIndex / 图像加载器

##### 本仓库：H:\二阶段\chinese-clip-vit-base-patch16；chinese_clip_embedding.py

#### 3、自定义 Chinese-CLIP

##### 文本：get_text_features → pooler_output（注意不要把 BaseModelOutput 当 tensor）

##### 图像：get_image_features；两边 L2 归一化后才能余弦比较

##### 维数：ViT-Base Patch16 常见 512 维，和纯文本 bge 维数不同，勿混进同一 Chroma 集合

#### 4、构建多模态索引：文本节点 + 图像节点分存或同空间双集合

#### 5、图文双向检索：以文搜图 / 以图搜图；元数据带回原图路径

#### 6、接入 LMM 看图作答：把召回图+文组成多模态消息

### 第五部分：进阶优化与实践

#### 1 文档解析：高分辨率渲染、表格单独抽、图注当 caption

#### 2 检索策略

##### 2.1 嵌入空间对齐：同一套 CLIP，不要文用 bge、图用 CLIP 却硬比

##### 2.2 索引结构：文集合 / 图集合 / 可选多表示

##### 2.3 查询理解：图问句可先改写或生成 caption

##### 2.4 跨模态重排：用 LMM 或跨模态 reranker 打分

##### 2.5 融合：RRF / 加权；图文证据都保留

##### 2.6 场景：手册看图问答、以图搜商品、扫描试卷

#### 3、常见问题

##### 中文差：换 Chinese-CLIP，不要用英文 CLIP

##### 维数冲突：CLIP 512 与 bge 384/768 不能塞同一 collection

##### 只开了文本塔：本仓库当前默认用 CLIP 做文本 embedding，完整看图检索需再接图像塔+LMM

##### 解析把图丢掉：检查 PDF loader 是否 extract 图像

### 和前面章节 / 本仓库

#### 第 04 章 Embedding、第 05 章向量库：MRAG 是它们的跨模态扩展

#### 第 06 章 Native RAG 仍是文本主链路；MRAG 不替代文字 RAG

#### 第 16/17 章图谱：关系走图，版式/截图走多模态

#### 落点：chinese_clip_embedding.py；图谱通道也可配 GRAPH_EMBED_PROVIDER=chinese_clip