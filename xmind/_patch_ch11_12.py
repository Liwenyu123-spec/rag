# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(__file__).resolve().parent
build_path = root / "build_xmind.py"
build = build_path.read_text(encoding="utf-8")

old_note = (
    '"根据飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、"\n'
    '        "Native RAG、Advanced RAG、检索前/中/后优化（Pre / Retrieval / Post-retrieval）。"'
)
new_note = (
    '"根据飞书讲义整理：认知阶段、提示词、RAG整体认知、Embedding、向量数据库、"\n'
    '        "Native RAG、Advanced RAG、检索前/中/后优化（Pre / Retrieval / Post-retrieval）、"\n'
    '        "Self-RAG、Corrective RAG（CRAG）。"'
)
if old_note not in build:
    raise SystemExit("TREE note not found")
build = build.replace(old_note, new_note, 1)

old_self = """                        topic(
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
                        ),"""
new_self = """                        topic(
                            "Self-RAG",
                            children=[
                                topic("模型自己决定：要不要检索、检索结果够不够、要不要再查"),
                                topic("治的病：过度检索（闲聊也查）和检索不足"),
                                topic("专训见第 11 章（四种反思令牌 Retrieve/ISREL/ISSUP/ISUSE）"),
                            ],
                        ),
                        topic(
                            "Corrective RAG（CRAG）",
                            children=[
                                topic("先评估检索质量：相关 / 模糊 / 不相关"),
                                topic("差则纠正：换查询或转外部网页搜索，再生成"),
                                topic("治的病：知识库覆盖不全、内部库答不了的新资讯"),
                                topic("专训见第 12 章（评估器 + 精炼 + 外搜 / 本仓库库内修正版）"),
                            ],
                        ),"""
if old_self not in build:
    raise SystemExit("ch07 Self/CRAG block not found")
build = build.replace(old_self, new_self, 1)

old_map = """                topic(
                    "六、和本仓库 / 第 08、09、10 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：检索前专训（改写/HyDE/分块…）"),
                        topic("第 09 章：检索中专训（混合/多路/RRF）"),
                        topic("第 10 章：检索后专训（Rerank/压缩/长上下文重排）"),
                        topic("chroma文档管理 项目 = Native 底座；Advanced 是往上叠模块"),
                    ],
                ),"""
new_map = """                topic(
                    "六、和本仓库 / 第 08~12 章的关系",
                    children=[
                        topic("第 07 章：Advanced 全景（前/中/后 + 进阶范式）"),
                        topic("第 08 章：检索前专训（改写/HyDE/分块…）"),
                        topic("第 09 章：检索中专训（混合/多路/RRF）"),
                        topic("第 10 章：检索后专训（Rerank/压缩/长上下文重排）"),
                        topic("第 11 章：Self-RAG 专训（查不查 + 生成反思）"),
                        topic("第 12 章：CRAG 专训（查错了怎么办 + 库内/外搜修正）"),
                        topic("chroma文档管理：Native 底座 + 已叠混合/后处理/CRAG"),
                    ],
                ),"""
if old_map not in build:
    raise SystemExit("ch07 map block not found")
build = build.replace(old_map, new_map, 1)

old_native = 'topic("⑦ 本仓库现状：仍是 Native；最值得先加改写或 bge-reranker"),'
new_native = 'topic("⑦ 本仓库现状：已叠混合检索/后处理/CRAG；Self-RAG 四令牌仍可按需加"),'
if old_native in build:
    build = build.replace(old_native, new_native, 1)

old_colors = """CHAPTER_COLORS = [
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
]"""
new_colors = """CHAPTER_COLORS = [
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
    ("#CA8A04", "#FEF9C3"),  # 11 金（Self-RAG）
    ("#9333EA", "#F3E8FF"),  # 12 紫（CRAG）
]"""
if old_colors not in build:
    raise SystemExit("CHAPTER_COLORS not found")
build = build.replace(old_colors, new_colors, 1)

old_main_line = '    chapters = copy.deepcopy(TREE.get("children", {}).get("attached", []))'
new_main_block = '''    # 追加 Self-RAG / CRAG 专训章（飞书 05/06）
    from _chapters_11_12 import chapters as _extra_chapters

    if not any(c.get("title", "").startswith("11 ") for c in TREE.get("children", {}).get("attached", [])):
        TREE.setdefault("children", {}).setdefault("attached", []).extend(_extra_chapters(topic))

    chapters = copy.deepcopy(TREE.get("children", {}).get("attached", []))'''
if old_main_line not in build:
    raise SystemExit("main chapters line not found")
if "from _chapters_11_12 import chapters" not in build:
    build = build.replace(old_main_line, new_main_block, 1)

build_path.write_text(build, encoding="utf-8")
print("patched", build_path)
