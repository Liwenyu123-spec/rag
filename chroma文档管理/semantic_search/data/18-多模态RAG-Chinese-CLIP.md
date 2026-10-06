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

#### 落点：chinese_clip_embedding.py；图谱通道也可配 GRAPH_EMBED_PROVIDER=chinese_clip\n