# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parent / "build_xmind.py"
build = p.read_text(encoding="utf-8")

# colors: add ch13
old_c = '''    ("#CA8A04", "#FEF9C3"),  # 11 金（Self-RAG）
    ("#9333EA", "#F3E8FF"),  # 12 紫（CRAG）
]'''
new_c = '''    ("#CA8A04", "#FEF9C3"),  # 11 金（Self-RAG）
    ("#9333EA", "#F3E8FF"),  # 12 紫（CRAG）
    ("#0F766E", "#CCFBF1"),  # 13 深青（项目对照）
]'''
if old_c not in build:
    raise SystemExit("colors not found")
build = build.replace(old_c, new_c, 1)

old09 = '''                        topic(
                            "和本仓库",
                            children=[
                                topic("当前 chroma文档管理 ≈ 单路稠密 Native"),
                                topic("最小改法：同 nodes 加 BM25 + QueryFusionRetriever(mode=reciprocal_rerank)"),
                                topic("有多目录知识时再拆多路并打 channel 元数据"),
                            ],
                        ),'''
new09 = '''                        topic(
                            "和本仓库",
                            children=[
                                topic("已落地：HYBRID_ENABLED + BM25(jieba) + QueryFusionRetriever(reciprocal_rerank)"),
                                topic("代码：retrieval_optimize.build_hybrid_retriever；失败回退纯向量"),
                                topic("未做：多目录多路 channel；见第 13 章演进 P4"),
                            ],
                        ),'''
if old09 not in build:
    raise SystemExit("ch09 本仓库 block not found")
build = build.replace(old09, new09, 1)

old10 = '''                        topic(
                            "和本仓库",
                            children=[
                                topic("Native 查询引擎默认无 node_postprocessors"),
                                topic("最小改法：as_query_engine(..., node_postprocessors=[DashScopeRerank(...)])"),
                                topic("再视情况加 SentenceEmbeddingOptimizer 与 LongContextReorder"),
                            ],
                        ),'''
new10 = '''                        topic(
                            "和本仓库",
                            children=[
                                topic("已落地三件套：本地 bge-reranker → SentenceEmbeddingOptimizer → LongContextReorder"),
                                topic("代码：retrieval_optimize.build_node_postprocessors；/ask 走 apply_postprocessors"),
                                topic("默认不依赖千问重排；RERANK_PROVIDER=dashscope 才用 API"),
                            ],
                        ),'''
if old10 not in build:
    raise SystemExit("ch10 本仓库 block not found")
build = build.replace(old10, new10, 1)

# update main comment
build = build.replace(
    "    # 追加 Self-RAG / CRAG 专训章（飞书 05/06）",
    "    # 追加 Self-RAG / CRAG / 项目全链路对照（飞书 05/06 + chroma文档管理）",
    1,
)

# also point ch07 to ch13
old_map_line = '                        topic("chroma文档管理：Native 底座 + 已叠混合/后处理/CRAG"),'
new_map_line = '                        topic("第 13 章：chroma文档管理 全链路文件/API/开关对照"),'
if old_map_line in build:
    build = build.replace(old_map_line, new_map_line, 1)

p.write_text(build, encoding="utf-8")
print("ok")
