# -*- coding: utf-8 -*-
"""Add chapter 10 Post-retrieval from Feishu; expand ch07 post section."""
from pathlib import Path

BUILD = Path(__file__).resolve().parent / "xmind" / "build_xmind.py"
text = BUILD.read_text(encoding="utf-8")

# 1) root note
old_root = (
    '"Native RAG、Advanced RAG、检索前优化（Pre-retrieval）、检索中优化（Retrieval）。"'
)
new_root = (
    '"Native RAG、Advanced RAG、检索前/中/后优化（Pre / Retrieval / Post-retrieval）。"'
)
if old_root not in text:
    raise SystemExit("root note not found")
text = text.replace(old_root, new_root, 1)

# 2) expand ch07 post-retrieval
START = '                topic(\n                    "三、检索后优化（Post-retrieval）",'
END = '                topic(\n                    "四、进阶范式对比（别混）",'
i0, i1 = text.find(START), text.find(END)
if i0 < 0 or i1 <= i0:
    raise SystemExit(f"ch07 post markers missing {i0=} {i1=}")

NEW_POST = r'''                topic(
                    "三、检索后优化（Post-retrieval）",
                    note=(
                        "飞书：04-检索后优化（Post-retrieval）。"
                        "目标：召回之后、喂 LLM 之前，做重排+精简+重排版。细节专训见第 10 章。"
                    ),
                    children=[
                        topic(
                            "位置与入口",
                            children=[
                                topic("标准 5 步：加载→分块→入库→检索召回 →【本章】→ 喂给大模型"),
                                topic("LlamaIndex：统一用 Node Postprocessor，串在 node_postprocessors=[...]"),
                                topic("多个后处理器按列表顺序逐级加工召回 nodes"),
                            ],
                        ),
                        topic(
                            "重排序 Re-ranking（粗排+精排）",
                            children=[
                                topic("定义：对召回候选再用更准更贵的模型二次打分，把最相关顶到前面"),
                                topic("超市口诀：先快速抓一车，再仔细挑最好的放最上面"),
                                topic("Bi-Encoder 双塔粗排：快，文档向量可预计算，精度一般"),
                                topic("Cross-Encoder 交叉精排：query+doc 一起进模型，准但慢，只打几十~几百条"),
                                topic("工业标配：Top-20~100 粗召回 → rerank → Top-3/5 给 LLM"),
                                topic("讲义实现：DashScopeRerank(qwen3-rerank) 或本地 SentenceTransformerRerank"),
                            ],
                        ),
                        topic(
                            "上下文压缩 Contextual Compression",
                            children=[
                                topic("问题：片段里往往只有一两句有用，整段硬塞浪费 token 还易幻觉"),
                                topic("一句话：重排管「哪些片段」；压缩管「片段里留哪几句」"),
                                topic("LlamaIndex：SentenceEmbeddingOptimizer（按句与查询算相似度裁剪）"),
                                topic("常用：percentile_cutoff=0.5 或 threshold_cutoff；中文可自定义切句"),
                            ],
                        ),
                        topic(
                            "长上下文重排 Long-Context Reorder",
                            children=[
                                topic("Lost in the Middle：模型对首尾记得清，中间易丢"),
                                topic("做法：最相关放头尾，次相关塞中间——只改顺序不改内容与选集"),
                                topic("LlamaIndex：LongContextReorder()，通常接在 reranker 之后"),
                            ],
                        ),
                        topic(
                            "三件套串联",
                            children=[
                                topic("① Rerank 精排 → ② SentenceEmbeddingOptimizer 压缩 → ③ LongContextReorder 排版"),
                                topic("生成侧仍要：仅依据资料回答 + 引用编号（最后一道闸）"),
                            ],
                        ),
                    ],
                ),
'''
text = text[:i0] + NEW_POST + text[i1:]

# 3) relation section
old_rel = '''                topic(
                    "六、和本仓库 / 第 08、09 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：把「检索前」拆开练：策略选择 + LlamaIndex 落地"),
                        topic("第 09 章：把「检索中」拆开练：混合检索 / 多路召回 / RRF + 代码落点"),
                        topic("chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块"),
                    ],
                ),'''
new_rel = '''                topic(
                    "六、和本仓库 / 第 08、09、10 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：检索前专训（改写/HyDE/分块…）"),
                        topic("第 09 章：检索中专训（混合/多路/RRF）"),
                        topic("第 10 章：检索后专训（Rerank/压缩/长上下文重排）"),
                        topic("chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块"),
                    ],
                ),'''
if old_rel not in text:
    raise SystemExit("relation section not found")
text = text.replace(old_rel, new_rel, 1)

# 4) ch09 pipeline mention ch10
text = text.replace(
    'topic("5 喂给大模型 —— 可再接第 07 章重排与压缩")',
    'topic("5 喂给大模型之前 —— 接第 10 章 node_postprocessors 三件套")',
    1,
)
text = text.replace(
    'topic("再 Post：rerank + 约束生成")',
    'topic("再 Post：第 10 章 rerank → 压缩 → 长上下文重排 → 约束生成")',
    1,
)

# 5) insert chapter 10
CH10 = r'''
        topic(
            "10 检索后优化（Post-retrieval）",
            note=(
                "飞书：04-检索后优化（Post-retrieval）。"
                "每种方法按：适用场景 → 输入 → 分步分解 → 输出 → 完整例子 → 代码意思 → 翻车点。"
            ),
            children=[
                topic(
                    "〇、总览：方法地图",
                    children=[
                        topic("目标：召回结果送入 LLM 前，做重排 + 精简 + 重排版，抬生成质量"),
                        topic("位置：第 4 步检索召回之后、第 5 步喂模型之前"),
                        topic("入口：node_postprocessors=[...]，按列表顺序串行加工 nodes"),
                        topic("三件套：Rerank → SentenceEmbeddingOptimizer → LongContextReorder"),
                        topic("和第 08/09 章：前改问句、中改召回；本章改「怎么用召回结果」"),
                    ],
                ),
                topic(
                    "方法1：两阶段检索与重排序 Re-ranking",
                    children=[
                        topic("适用：粗召回有相关材料，但 Top-3/5 常被「沾边噪声」占坑"),
                        topic(
                            "输入",
                            children=[
                                topic("用户问题 + 粗排候选（如 similarity_top_k=20~100）"),
                                topic("精排模型：API（DashScopeRerank）或本地 Cross-Encoder"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 Bi-Encoder/向量检索：快，从海量库捞 Top-N 候选"),
                                topic("Step2 Cross-Encoder/Rerank：query+doc 一起打分，只精排候选"),
                                topic("Step3 截断 top_n（常 3/5）交给生成"),
                                topic("Step4（可选）后面再接压缩与长上下文重排"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("按精排分排序的短名单；精确率↑，喂给模型的噪声↓"),
                            ],
                        ),
                        topic(
                            "完整例子（超市红烧肉）",
                            children=[
                                topic("粗排：五花肉、酱油…也抓回红烧牛肉面、红烧鱼料——快但乱"),
                                topic("精排：逐个判断，真正做红烧肉必备的顶到最前"),
                                topic("口诀：先广撒网，再精挑细选"),
                            ],
                        ),
                        topic(
                            "原理口述",
                            children=[
                                topic("Bi-Encoder：查询/文档各自编码再比余弦，文档可离线预计算"),
                                topic("Cross-Encoder：拼接后深层交互直接出相关性分，准但慢"),
                                topic("只用双塔：Top-5 易混入沾边货；只用交叉：百万库打不动"),
                                topic("两阶段 = 工业标准粗召回 + 精排"),
                            ],
                        ),
                        topic(
                            "讲义代码逐行",
                            children=[
                                topic(
                                    "依赖",
                                    children=[
                                        topic("方式A API：llama-index-postprocessor-dashscope-rerank"),
                                        topic("方式B 本地：sentence-transformers + SentenceTransformerRerank"),
                                    ],
                                ),
                                topic(
                                    "Settings.embed_model = DashScopeEmbedding(text-embedding-v3)",
                                    children=[
                                        topic("意思：粗排仍用本章同一套 embedding"),
                                    ],
                                ),
                                topic(
                                    "retriever = index.as_retriever(similarity_top_k=6)",
                                    children=[
                                        topic("意思：第 1 阶段多召回一些，给精排留候选空间"),
                                        topic("为什么：top_k 太小，精排没有可选余地"),
                                    ],
                                ),
                                topic(
                                    'DashScopeRerank(model="qwen3-rerank", top_n=3)',
                                    children=[
                                        topic("意思：用通义重排模型对候选二次打分，只留 Top-3"),
                                        topic("注意：讲义提到旧名 gte-rerank 可能下线，以当前可用模型名为准"),
                                    ],
                                ),
                                topic(
                                    "SentenceTransformerRerank（本地备选）",
                                    children=[
                                        topic("意思：离线 Cross-Encoder，不依赖重排 API"),
                                        topic("为什么：内网/无外网时用方式 B"),
                                    ],
                                ),
                                topic(
                                    "as_query_engine(..., node_postprocessors=[reranker])",
                                    children=[
                                        topic("意思：检索后先过 reranker，再把精排结果拼进 Prompt 生成"),
                                    ],
                                ),
                                topic(
                                    "response.source_nodes",
                                    children=[
                                        topic("意思：打印精排后真正用于生成的片段与 score"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "翻车点",
                            children=[
                                topic("粗排 top_k=3 再 rerank：精排几乎无事可做"),
                                topic("对全库跑 Cross-Encoder：延迟炸裂"),
                                topic("把 RRF 融合和 Cross-Encoder 精排当成同一步"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法2：上下文压缩 SentenceEmbeddingOptimizer",
                    children=[
                        topic("适用：相关片段很长，里面夹杂天气/CI/CD/闲聊等噪声句"),
                        topic(
                            "输入",
                            children=[
                                topic("已召回（最好已重排）的 nodes + 同一查询"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 把每个片段拆成句子（中文可用正则按。！？；切）"),
                                topic("Step2 每句与查询算 embedding 相似度"),
                                topic("Step3 percentile_cutoff / threshold_cutoff 丢掉低分句"),
                                topic("Step4 只把保留句子拼回片段，再喂 LLM"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("更短、更贴题的上下文；token↓、噪声↓、幻觉风险↓"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("压缩前：显存要求夹在「办公自动化」「今天天气不错」中间"),
                                topic("压缩后：只留「Qwen2.5 最低 16GB 显存…」等相关句"),
                            ],
                        ),
                        topic(
                            "讲义代码逐行",
                            children=[
                                topic(
                                    "SentenceEmbeddingOptimizer(percentile_cutoff=0.5)",
                                    children=[
                                        topic("意思：每个片段只留相关度排名前 50% 的句子"),
                                        topic("也可 threshold_cutoff=0.7：按绝对相似度门槛裁"),
                                    ],
                                ),
                                topic(
                                    "chinese_sentence_splitter = re.split(r'[。！？；\\n!?；]', text)",
                                    children=[
                                        topic("意思：按中英文句号问号感叹号分号换行切句"),
                                        topic("为什么：默认英文切句对中文不友好"),
                                    ],
                                ),
                                topic(
                                    "node_postprocessors=[..., optimizer]",
                                    children=[
                                        topic("意思：压缩器作为后处理链一环，常放在 rerank 之后"),
                                    ],
                                ),
                            ],
                        ),
                        topic(
                            "和重排的关系",
                            children=[
                                topic("重排：选哪些块、谁排前"),
                                topic("压缩：块里留哪几句"),
                                topic("常配合：先重排，再压缩"),
                            ],
                        ),
                        topic("翻车点：cutoff 过严，相关句也被裁光；过松等于没压缩"),
                    ],
                ),
                topic(
                    "方法3：长上下文重排 LongContextReorder",
                    children=[
                        topic("适用：喂给模型的片段较多/较长，担心中间内容被忽略"),
                        topic(
                            "输入",
                            children=[
                                topic("已排序的 nodes（通常来自 reranker，相关度从高到低）"),
                            ],
                        ),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 认识 Lost in the Middle：首尾易记、中间易丢"),
                                topic("Step2 调用 LongContextReorder()（无构造参数）"),
                                topic("Step3 把最相关挪到列表头尾，次相关塞中间"),
                                topic("Step4 不改文本内容、不改选集，只改排列"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("同一批片段，但顺序更贴合 LLM 注意力分布"),
                            ],
                        ),
                        topic(
                            "完整例子",
                            children=[
                                topic("rerank 后：1>2>3>4>5 相关度递减"),
                                topic("reorder 后：最高分在首尾，较低分在中间"),
                            ],
                        ),
                        topic(
                            "讲义代码逐行",
                            children=[
                                topic(
                                    "reranker = DashScopeRerank(..., top_n=5)",
                                    children=[
                                        topic("意思：先精排出 Top-5（高→低）"),
                                    ],
                                ),
                                topic(
                                    "reorder = LongContextReorder()",
                                    children=[
                                        topic("意思：实例化排版器，无需传参"),
                                    ],
                                ),
                                topic(
                                    "as_query_engine(similarity_top_k=8, node_postprocessors=[reranker, reorder])",
                                    children=[
                                        topic("意思：先粗召回 8 → 精排留 5 → 再首尾重排版"),
                                        topic("列表顺序就是执行顺序，不能颠倒乱挂"),
                                    ],
                                ),
                            ],
                        ),
                        topic("翻车点：片段很少（≤3）时收益有限；别指望它能「救回」没召回的内容"),
                    ],
                ),
                topic(
                    "方法4：三件套串成完整检索后链",
                    children=[
                        topic("适用：要上工业级 Post-retrieval 默认链路时"),
                        topic(
                            "分步分解",
                            children=[
                                topic("Step1 粗召回 similarity_top_k 调大（如 8~50）"),
                                topic("Step2 DashScopeRerank / Cross-Encoder → top_n"),
                                topic("Step3 SentenceEmbeddingOptimizer 裁句"),
                                topic("Step4 LongContextReorder 首尾排版"),
                                topic("Step5 LLM 生成；Prompt 约束仅依据资料 + 引用"),
                            ],
                        ),
                        topic(
                            "推荐挂法",
                            children=[
                                topic("node_postprocessors=[reranker, compressor, reorder]"),
                                topic("口诀：先选块 → 再削句 → 最后排版"),
                            ],
                        ),
                        topic(
                            "输出",
                            children=[
                                topic("短、准、好读的上下文，生成更稳、更省 token"),
                            ],
                        ),
                        topic(
                            "翻车点",
                            children=[
                                topic("三件套一次全开却不评测：延迟↑费用↑，先只上 rerank"),
                                topic("顺序挂反：先 reorder 再 rerank 失去精排意义"),
                            ],
                        ),
                    ],
                ),
                topic(
                    "方法怎么串起来（推荐顺序）",
                    children=[
                        topic(
                            "诊断",
                            children=[
                                topic("相关材料在后面几名 → 方法1 重排"),
                                topic("材料对但废话多/超窗口 → 方法2 压缩"),
                                topic("片段多、答案漏中间要点 → 方法3 长上下文重排"),
                                topic("要完整工业链 → 方法4 三件套"),
                            ],
                        ),
                        topic(
                            "和本仓库",
                            children=[
                                topic("Native 查询引擎默认无 node_postprocessors"),
                                topic("最小改法：as_query_engine(..., node_postprocessors=[DashScopeRerank(...)])"),
                                topic("再视情况加 SentenceEmbeddingOptimizer 与 LongContextReorder"),
                            ],
                        ),
                        topic(
                            "和第 08/09 章衔接",
                            children=[
                                topic("Pre（08）改问句 → Mid（09）混合/多路召回 → Post（10）三件套 → 生成"),
                                topic("召回上限由 08/09 决定；本章抬的是「已召回材料的利用率」"),
                            ],
                        ),
                        topic(
                            "五、小结（讲义）",
                            children=[
                                topic("重排：抬精确率"),
                                topic("压缩：降噪声与 token"),
                                topic("长上下文重排：对抗 Lost in the Middle"),
                                topic("三者都通过 node_postprocessors 接入，是工业级 RAG 标准检索后手段"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
'''

end_marker = "\n    ],\n)\n\n\ndef to_md"
idx = text.rfind(end_marker)
if idx < 0:
    raise SystemExit("TREE end not found")
# Ensure comma after ch09 closing before insert
# ch09 ends with `        ),` then `    ],`
close = text.rfind("        ),", 0, idx)
# insert CH10 before `    ],`
text = text[:idx] + ",\n" + CH10 + text[idx:]

# Fix possible double-comma / orphan comma like last time
text = text.replace("        ),\n,\n\n        topic(\n            \"10 ", "        ),\n        topic(\n            \"10 ", 1)
# If we inserted `,\n\n        topic` after `        ),` that already had no comma — check
# Pattern after insert may be: `        ),\n,\n\n        topic(` which is valid (comma after ),)
# Or `        ),\n,\n        topic` - also ok
# Bad pattern: lone comma line without being list separator - fix if `),\n,\n\n    ],`
if "\n,\n\n    ],\n)" in text:
    text = text.replace("\n,\n\n    ],\n)", "\n    ],\n)", 1)

# 6) colors
old_colors = '''CHAPTER_COLORS = [
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
new_colors = old_colors[:-1] + '    ("#BE123C", "#FFE4E6"),  # 10 玫红深\n]'
# safer explicit
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
    ("#BE123C", "#FECDD3"),  # 10 玫
]'''
if old_colors not in text:
    raise SystemExit("CHAPTER_COLORS not found")
text = text.replace(old_colors, new_colors, 1)

BUILD.write_text(text, encoding="utf-8")
print("patched ok")
