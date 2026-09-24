# -*- coding: utf-8 -*-
"""Patch build_xmind.py: expand mid-retrieval in ch07 + add ch09 from Feishu doc."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "xmind" / "build_xmind.py"
text = BUILD.read_text(encoding="utf-8")

# --- 1) root note ---
old_root_note = (
    '"根据8篇飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、"\n'
    '        "Native RAG、Advanced RAG、检索前优化（Pre-retrieval）。"'
)
new_root_note = (
    '"根据飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、"\n'
    '        "Native RAG、Advanced RAG、检索前优化（Pre-retrieval）、检索中优化（Retrieval）。"'
)
if old_root_note not in text:
    raise SystemExit("root note marker not found")
text = text.replace(old_root_note, new_root_note, 1)

# --- 2) cross-ref in earlier chapter ---
text = text.replace(
    'topic("细节展开：见第 07 章；检索前专训见第 08 章")',
    'topic("细节展开：见第 07 章；检索前见第 08 章；检索中见第 09 章")',
    1,
)

# --- 3) replace ch07 mid-retrieval section ---
START = '                topic(\n                    "二、检索中优化（Retrieval）",'
END = '                topic(\n                    "三、检索后优化（Post-retrieval）",'

i0 = text.find(START)
i1 = text.find(END)
if i0 < 0 or i1 < 0 or i1 <= i0:
    raise SystemExit(f"ch07 mid markers not found {i0=} {i1=}")

NEW_MID = r'''                topic(
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
'''

text = text[:i0] + NEW_MID + text[i1:]

# --- 4) update ch07 section 六 ---
old_rel = '''                topic(
                    "六、和本仓库 / 第 08 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：把「检索前」拆开练：策略选择 + LlamaIndex 落地"),
                        topic("chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块"),
                    ],
                ),'''
new_rel = '''                topic(
                    "六、和本仓库 / 第 08、09 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：把「检索前」拆开练：策略选择 + LlamaIndex 落地"),
                        topic("第 09 章：把「检索中」拆开练：混合检索 / 多路召回 / RRF + 代码落点"),
                        topic("chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块"),
                    ],
                ),'''
if old_rel not in text:
    raise SystemExit("ch07 relation section not found")
text = text.replace(old_rel, new_rel, 1)

# --- 5) enrich ch07 pre-retrieval note + post slightly ---
text = text.replace(
    'note="目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章。"',
    'note="目标：进向量库之前，把「问句」和「文档形态」准备好。细节专训见第 08 章；检索中见第 09 章。"',
    1,
)
text = text.replace(
    'note="目标：提高精排质量与生成可用性——捞上来的材料怎么用。"',
    'note="目标：提高精排质量与生成可用性——捞上来的材料怎么用。召回靠第 09 章抬上来，这里负责精排与怎么喂给模型。"',
    1,
)

# --- 6) insert chapter 09 before TREE close ---
CH09 = r'''
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
                            "代码要点（讲义）",
                            children=[
                                topic("依赖：llama-index-core / embeddings-dashscope / retrievers-bm25 / jieba"),
                                topic("两路必须同一 nodes，避免「向量一块、BM25 另一块」对不齐"),
                                topic("tokenizer=lambda t: list(jieba.cut(t))；或 def tokenize 再传入（传函数本身）"),
                                topic("可选 HF_ENDPOINT=hf-mirror.com（若本地还下 BGE 等模型）"),
                                topic("进阶整包：语义分块 + DashScope 批处理包装 + RRF + Qwen 生成"),
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
                            "代码解读口诀",
                            children=[
                                topic("分了 3 条独立通道，互不共享索引状态"),
                                topic("标准流程：分库 → 分索引 → 分检索 → 去重融合 → 生成"),
                                topic("先多路召回保覆盖，再融合排序保可用"),
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
'''

marker = "            ],\n        ),\n\n    ],\n)"
# The end of ch08 is:            ],\n        ),\n\n    ],\n)
# Insert CH09 before `    ],\n)` that closes TREE children
end_marker = "\n    ],\n)\n\n\ndef to_md"
idx = text.rfind(end_marker)
if idx < 0:
    raise SystemExit("TREE end marker not found")
# We need to insert after the closing of chapter 08 topic, before TREE's children list closes.
# Structure: ... ch08 ... ),  \n\n    ],\n)
insert_at = text.rfind("\n    ],\n)\n\n\ndef to_md")
# Find the `        ),` that closes ch08 - it's right before `    ],`
close_tree_children = text.rfind("\n    ],\n)", 0, insert_at + 20)
# Actually insert_at points to start of `\n    ],\n)\n\n\ndef to_md`
# Before that should be `        ),` closing last chapter
text = text[:insert_at] + ",\n" + CH09 + text[insert_at:]

# --- 7) CHAPTER_COLORS add 09 ---
old_colors = '''CHAPTER_COLORS = [
    ("#2563EB", "#DBEAFE"),  # 01 蓝
    ("#059669", "#D1FAE5"),  # 02 绿
    ("#D97706", "#FDE68A"),  # 03 琥珀
    ("#0891B2", "#CFFAFE"),  # 04 青
    ("#E11D48", "#FFE4E6"),  # 05 玫红
    ("#7C3AED", "#EDE9FE"),  # 06 紫
    ("#EA580C", "#FFEDD5"),  # 07 橙
    ("#0D9488", "#CCFBF1"),  # 08 青绿
]'''
new_colors = '''CHAPTER_COLORS = [
    ("#2563EB", "#DBEAFE"),  # 01 蓝
    ("#059669", "#D1FAE5"),  # 02 绿
    ("#D97706", "#FDE68A"),  # 03 琥珀
    ("#0891B2", "#CFFAFE"),  # 04 青
    ("#E11D48", "#FFE4E6"),  # 05 玫红
    ("#7C3AED", "#EDE9FE"),  # 06 紫
    ("#EA580C", "#FFEDD5"),  # 07 橙
    ("#0D9488", "#CCFBF1"),  # 08 青绿
    ("#4F46E5", "#E0E7FF"),  # 09 靛
]'''
if old_colors not in text:
    raise SystemExit("CHAPTER_COLORS not found")
text = text.replace(old_colors, new_colors, 1)

# --- 8) ch08 pipeline mention 09 ---
text = text.replace(
    'topic("6 进入向量检索（检索中）→ 再重排生成（检索后）")',
    'topic("6 进入检索中（第 09 章混合/多路）→ 再重排生成（检索后）")',
    1,
)

BUILD.write_text(text, encoding="utf-8")
print("patched", BUILD)
