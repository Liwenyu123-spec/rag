# RAG入门课
根据8篇飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、Native RAG、Advanced RAG、检索前优化（Pre-retrieval）。

## 01 认知阶段：大模型介绍、调用、RAG
飞书文档：01-认知阶段（大模型介绍，调用，RAG）

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

###### 细节展开：见第 07 章；检索前专训见第 08 章

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

### 一、检索前优化（Pre-retrieval）
目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章。

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
目标：提高召回率 Recall——相关材料尽量被捞上来。

#### 混合检索 Hybrid（必会口述）

##### 稠密向量：语义相近，「笔记本≈电脑」能中

##### 稀疏/关键词 BM25：专名、错误码、SKU、法规条款号能中

##### 一句话：语义负责懂人话，关键词负责抓铁证

##### 融合：分数归一化加权，或更稳的 RRF（按排名融合）

##### 什么时候必须上：制度库、工单号、产品型号多的场景

#### 多路召回

##### 不同 Embedding / 不同 chunk 大小 / 不同索引并行

##### 先求并集保召回，再交给重排去噪

##### 路数 2~3 通常够；再多延迟和费用线性涨

#### 稀疏向量 SPLADE / 多向量 ColBERT

##### SPLADE：学出来的稀疏向量，比纯 BM25 多一点语义

##### ColBERT：token 级交互（MaxSim），更细但更吃存储算力

##### 答辩：知道「单向量会丢细粒度」即可，不必深挖公式

#### RRF 倒数排名融合（常考）

##### 分数 ≈ Σ 1/(k + 排名)，k 常取 60

##### 关键优点：不要求各路原始分数在同一量纲

##### LlamaIndex：mode='reciprocal_rerank'

##### 口述：谁经常排很前，谁最终就靠前，不管它原始分是 0.9 还是 12

### 三、检索后优化（Post-retrieval）
目标：提高精排质量与生成可用性——捞上来的材料怎么用。

#### 重排序 Re-ranking（性价比之王）

##### 召回：双塔/向量，快，但 query-doc 没深度交互

##### 精排：交叉编码器，query+doc 一起进模型打分，慢但准

##### 标准流程：召回 Top-20~50 → rerank → 只留 Top-3/5 给 LLM

##### 常用：bge-reranker、Cohere Rerank；也可用 LLM 当裁判（更贵）

##### 口述口诀：先广撒网，再精挑细选

#### 上下文压缩 / 去重 / 动态 Top-K

##### 压缩：块里只有一两句有用，抽句段，别整块硬塞

##### 去重：重复块、过期块、低分块丢掉

##### 动态 K：高分很少就少送，别为了凑满 5 条硬塞噪声

#### 生成侧约束

##### Prompt：仅根据下列资料回答；没有依据就说不知道

##### 引用：资料编号，答案里标注来源，抑制瞎编

##### 这是「最后一道闸」，检索错了它救不了 100%，但能少胡说八道

### 四、进阶范式对比（别混）

#### Self-RAG

##### 模型自己决定：要不要检索、检索结果够不够、要不要再查

##### 治的病：过度检索（闲聊也查）和检索不足

#### Corrective RAG（CRAG）

##### 先评估检索质量：相关 / 模糊 / 不相关

##### 差则纠正：换查询或转外部网页搜索，再生成

##### 治的病：知识库覆盖不全、内部库答不了的新资讯

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

#### ⑦ 本仓库现状：仍是 Native；最值得先加改写或 bge-reranker

### 六、和本仓库 / 第 08 章的关系

#### 第 07 章：Advanced 全景（前/中/后 + 进阶范式）

#### 第 08 章：把「检索前」拆开练：策略选择 + LlamaIndex 落地

#### chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块

## 08 检索前优化（Pre-retrieval）
每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 翻车点。

### 〇、总览：方法地图

#### 查询侧：清洗 → 澄清 → 重写 / 扩展 / HyDE / Step-Back / 分解

#### 文档侧（离线）：分块 → 元数据 → 增强 → 多表示 / 路由规则

#### 原则：先判断病症，再选一种方法；不要一次全开

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

##### 6 进入向量检索（检索中）→ 再重排生成（检索后）

#### 本仓库最小改法

##### 先在 query() 前加方法1+3（清洗+重写）

##### 再试 HyDEQueryTransform(include_original=True)

##### 专名多再加混合检索；回答飘再加重排