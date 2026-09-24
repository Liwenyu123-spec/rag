03-检索中优化（Retrieval）
目标：提升召回率和相关性
召回的意思：
检索召回 = 从海量知识库 / 文档里，把和用户问题「相关的内容找出来」的过程。
检索：拿着用户问题，去向量库 / 文档库里搜索
召回：把匹配度高、相关的片段 / 文档给捞回来、拿出来
行业里常说的两个指标（RAG 必懂）
1.
召回率（Recall）
该找到的相关内容，有没有全部找出来
•
召回率高：相关的基本都捞出来了，不漏
召回率低：很多相关文档没搜到，漏了
2.
精确率（Precision）
召回来的内容里，有多少是真的有用、不跑偏
精确率高：捞回来的都很相关，没垃圾内容
精确率低：捞一堆不相关的噪音
一、混合检索（Hybrid Search）
1.1 核心概念
问题：单一检索方式总有盲区
混合检索 = 稠密向量 + 稀疏向量 → 结果融合 → 取长补短。
1.2 原理图解
稠密向量：每个维度都包含有意义的信息，向量中几乎没有零值。因此，存储时需要为每个维度分配空间。
稀疏向量：大多数元素为零，只有少数几个维度有非零值。存储时，通常只记录有值的位置索引和对应的值，非常节省空间。
核心一句话：
稠密向量 = 「按意思翻译」的数字串；稀疏向量 = 「按关键词翻译」的数字串。同一份文档用两种翻译官转，就有了两种检索排名—— 这两种排名互补，合起来搜得更准。
代码解读：
1、分了 3 条独立的检索通道
每路一个 VectorStoreIndex 或 BM25Retriever，独立工作：
第 1 路：技术文档库 → tech_index.as_retriever(...)（稠密向量）
第 2 路：FAQ 库 → BM25Retriever.from_defaults(...)（BM25 关键词）
3.
第 3 路：社区讨论库 → community_index.as_retriever(...)（稠密向量）
这 3 路互相独立、各自检索、各自返回结果→ 典型的 多路召回（Multi-Channel Retrieval）。
2、代码里的每一步，对应多路召回的标准流程
分库 → 三份 Document 列表
分索引 → 三个 VectorStoreIndex / BM25Retriever
分检索 → QueryFusionRetriever 内部并发调用三路
4.
自动去重 + 融合 → relative_score 归一化加权 / reciprocal_rerank RRF
5.
顶层 RetrieverQueryEngine 把融合结果交给 LLM 生成最终回答
3、先多路召回 → 再融合排序
多路召回（多数据源、多算法、多通道）+ 融合（RRF / 归一化加权 / 轮询）
多路召回（3路分别搜）
↓
混合排序（加权融合排序）
工业级 RAG 检索架构！
2.4 多路召回检索的代码放在RAG的哪块？
解释：
多路召回在RAG 的【检索阶段】
完整的代码
把多路召回封装成标准 RAG 检索函数：
代码块
Python
复制
"""
多路召回集成到 RAG 完整流程 - LlamaIndex 实现
三路独立索引 + QueryFusionRetriever 加权融合 + qwen3.7-max 生成回答
import os
import jieba
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.llms.dashscope import DashScope
from llama_index.retrievers.bm25 import BM25Retriever
# ====================== 1. 全局配置 ======================
api_key = os.getenv("DASHSCOPE_API_KEY")
Settings.embed_model = DashScopeEmbedding(
model_name="text-embedding-v3",
api_key=api_key,
)
Settings.llm = DashScope(
model_name="qwen3.7-max",
temperature=0.1,
# ====================== 2. 三路数据源 ======================
tech_docs = [
Document(text="Qwen2.5 部署指南。Qwen2.5 支持 vLLM 部署，需要至少 24GB 显存，推荐使用 A100 或 RTX 4090。",
metadata={"id": "tech_001", "channel": "tech"}),
Document(text="模型量化技术。AWQ 和 GPTQ 量化可将显存需求降低 50%，适合消费级显卡。",
metadata={"id": "tech_002", "channel": "tech"}),
Document(text="Docker 部署大模型。使用 Docker 可以隔离环境，简化依赖安装，支持快速扩缩容。",
metadata={"id": "tech_003", "channel": "tech"}),
Document(text="分布式推理。多卡并行推理需要 NCCL 通信库，支持张量并行和流水线并行。",
metadata={"id": "tech_004", "channel": "tech"}),
]
faq_docs = [
Document(text="Q: Qwen 需要什么 GPU？ A: 最低需要 16GB 显存，推荐 24GB 以上。",
metadata={"id": "faq_001", "channel": "faq"}),
Document(text="Q: vLLM 怎么安装？ A: pip install vllm，需要 CUDA 11.8 以上。",
metadata={"id": "faq_002", "channel": "faq"}),
Document(text="Q: Mac 能跑 Qwen 吗？ A: M 系列芯片可以，但速度较慢，建议量化后运行。",
metadata={"id": "faq_003", "channel": "faq"}),
Document(text="Q: 部署报错 OOM 怎么办？ A: 减小 batch size，启用梯度检查点，或使用量化模型。",
metadata={"id": "faq_004", "channel": "faq"}),
community_docs = [
Document(text="我用 3090 24G 跑 Qwen-14B 没问题，int8 量化后更稳。",
metadata={"id": "com_001", "channel": "community"}),
Document(text="A100 80G 可以直接跑 Qwen-72B，不用量化，速度飞快。",
metadata={"id": "com_002", "channel": "community"}),
Document(text="别用 Docker 了，直接 conda 安装更省事，我踩过坑。",
metadata={"id": "com_003", "channel": "community"}),
Document(text="vLLM 的 prefix caching 真的香，重复查询快 3 倍。",
metadata={"id": "com_004", "channel": "community"}),
# ====================== 3. 三路索引 + 三路检索器 ======================
tech_index = VectorStoreIndex.from_documents(tech_docs)
faq_index = VectorStoreIndex.from_documents(faq_docs)
community_index = VectorStoreIndex.from_documents(community_docs)
tech_retriever = tech_index.as_retriever(similarity_top_k=3)
faq_retriever = BM25Retriever.from_defaults(
nodes=list(faq_index.docstore.docs.values()),
similarity_top_k=3,
tokenizer=lambda t: list(jieba.cut(t)),
community_retriever = community_index.as_retriever(similarity_top_k=3)
# ====================== 4. 加权融合的多路召回 ======================
# relative_score 模式会先把每路分数 min-max 归一化再加权融合，
# 避免 cosine(0~1) 与 BM25(0~∞) 量纲不同导致的不公平。
multi_recall_retriever = QueryFusionRetriever(
retrievers=[tech_retriever, faq_retriever, community_retriever],
retriever_weights=[1.0, 1.2, 0.8],
similarity_top_k=5,
num_queries=1,
mode="relative_score",
use_async=False,
# ====================== 5. 组装 RAG 查询引擎 ======================
query_engine = RetrieverQueryEngine.from_args(retriever=multi_recall_retriever)
# ====================== 6. 测试 ======================
if __name__ == "__main__":
question = "Qwen 部署需要多少显存？"
三、混合检索和多路召回的区别
response = query_engine.query(question)
print("=" * 60)
print(f"用户问题：{question}")
print("\n召回的参考资料：")
for n in response.source_nodes:
print(f"  [{n.metadata.get('channel')}] {n.metadata.get('id')}: {n.text[:60]}")
print("\n" + "=" * 60)
print("Qwen 最终回答：")
print(response.response)
具体场景对比
假设你有一个企业内部知识库，包含：产品文档、技术规范、客服工单、员工手册。
场景 A：用户搜索 "登录超时怎么处理"
混合检索的做法：
只在「产品文档」这一个数据源里搜
同时用两种方式算相关性：
◦
向量检索：理解语义，找到"session过期""身份验证失败"等同义表达
关键词检索（BM25）：精确匹配"登录超时"这个字眼
最后把两个分数融合（比如 RRF），排出最终顺序
→ 特点：数据源没变，但用两种算法互相补短板，避免向量检索漏掉精确术语、或关键词检索漏掉同义改写。
多路召回的做法：
同时从多个独立数据源各搜一把：
路1：产品文档库 → 搜"登录超时"
路2：客服工单库 → 搜"登录超时"
路3：技术规范库 → 搜"登录超时"
路4：员工 FAQ → 搜"登录超时"
四路结果合并，去掉重复文档，再排序
→ 特点：每一路可能只用一种算法（比如都用向量），但覆盖的数据范围扩大了
实际系统中两者经常一起用
真实架构通常是嵌套关系：
多路召回（外层）
├── 路1：产品文档 → 内部做混合检索（向量 + 关键词）
├── 路2：客服工单 → 内部做混合检索（向量 + 关键词）
├── 路3：技术规范 → 内部做混合检索（向量 + 关键词）
└── 融合排序 + 去重
也就是说：多路召回是横向扩展数据源，混合检索是纵向深化单源质量。两者解决的是不同维度的问题，不是互斥选项。