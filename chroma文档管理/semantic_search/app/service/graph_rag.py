"""GraphRAG：LlamaIndex PropertyGraphIndex + Neo4j + 千问（对齐飞书 02_GraphRag的使用）。

流程：Documents → kg_extractors 抽三元组 → Neo4jPropertyGraphStore → as_query_engine。
"""

from __future__ import annotations

from typing import List, Literal, Tuple

from llama_index.core import Document, Settings
from llama_index.core.indices.property_graph import (
    PropertyGraphIndex,
    SchemaLLMPathExtractor,
    SimpleLLMPathExtractor,
)
from llama_index.core.types import PydanticProgramMode
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.dashscope import DashScope

from semantic_search.app.config import (
    DASHSCOPE_API_KEY,
    GRAPH_EMBED_MODEL,
    GRAPH_EXTRACTOR,
    GRAPH_LLM_MODEL,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)

# 飞书文档推荐的演示 Schema（方式二）
DEFAULT_ENTITIES = Literal["PERSON", "COMPANY", "SCHOOL", "LOCATION"]
DEFAULT_RELATIONS = Literal["CO_FOUNDED", "STUDIED_AT", "LOCATED_AT"]
DEFAULT_VALIDATION_SCHEMA: List[Tuple[str, str, str]] = [
    ("PERSON", "CO_FOUNDED", "COMPANY"),
    ("PERSON", "STUDIED_AT", "SCHOOL"),
    ("COMPANY", "LOCATED_AT", "LOCATION"),
]

SAMPLE_GRAPH_TEXTS = [
    "乔布斯和沃兹尼亚克于1976年共同创立了苹果公司，总部位于库比蒂诺。",
    "沃兹尼亚克毕业于加州大学伯克利分校。乔布斯曾就读于里德学院。",
]


class GraphRagService:
    """封装 Neo4j 连接、图谱构建与自然语言问答。"""

    def __init__(self) -> None:
        if not DASHSCOPE_API_KEY:
            raise RuntimeError(
                "GraphRAG 需要 DASHSCOPE_API_KEY（飞书要求千问抽取/生成）。"
                "请在仓库根目录 .env 或 Windows 用户环境变量中配置。"
            )
        if not NEO4J_PASSWORD:
            raise RuntimeError(
                "未配置 NEO4J_PASSWORD。请在 .env 写入 Neo4j 密码（首次登录后改过的密码）。"
            )

        self._configure_dashscope()
        self.graph_store = Neo4jPropertyGraphStore(
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            url=NEO4J_URI,
        )
        self._index: PropertyGraphIndex | None = None

    def _configure_dashscope(self) -> None:
        """对齐讲义：LLM=qwen-plus，Embedding=text-embedding-v4。"""
        llm = DashScope(
            model_name=GRAPH_LLM_MODEL,
            api_key=DASHSCOPE_API_KEY,
            temperature=0,
            timeout=60,
            max_tokens=4096,
        )
        # SchemaLLMPathExtractor 在新版需走 LLM 模式，避免默认 program 不兼容
        llm.pydantic_program_mode = PydanticProgramMode.LLM
        Settings.llm = llm
        Settings.embed_model = DashScopeEmbedding(
            model_name=GRAPH_EMBED_MODEL,
            api_key=DASHSCOPE_API_KEY,
        )

    def status(self) -> dict:
        """连通性与配置摘要（不回显密码）。"""
        ok = True
        message = "ok"
        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            driver.verify_connectivity()
            driver.close()
        except Exception as exc:  # noqa: BLE001 — 状态接口要吞掉并回报
            ok = False
            message = f"{type(exc).__name__}: {exc}"
        return {
            "ready": ok,
            "message": message,
            "neo4j_uri": NEO4J_URI,
            "neo4j_username": NEO4J_USERNAME,
            "llm_model": GRAPH_LLM_MODEL,
            "embed_model": GRAPH_EMBED_MODEL,
            "extractor": GRAPH_EXTRACTOR,
            "has_index": self._index is not None,
            "dashscope_configured": bool(DASHSCOPE_API_KEY),
        }

    def _build_extractor(self, mode: str | None = None):
        mode = (mode or GRAPH_EXTRACTOR).strip().lower()
        if mode in {"schema", "schema_llm", "schemallmpathextractor"}:
            return SchemaLLMPathExtractor(
                llm=Settings.llm,
                possible_entities=DEFAULT_ENTITIES,
                possible_relations=DEFAULT_RELATIONS,
                kg_validation_schema=DEFAULT_VALIDATION_SCHEMA,
                strict=True,
                max_triplets_per_chunk=10,
            ), "schema"
        return (
            SimpleLLMPathExtractor(
                llm=Settings.llm,
                max_paths_per_chunk=10,
                num_workers=4,
            ),
            "simple",
        )

    def build_from_texts(
        self,
        texts: List[str] | None = None,
        *,
        extractor: str | None = None,
    ) -> dict:
        """从文本列表抽取三元组并写入 Neo4j。"""
        docs = [Document(text=t.strip()) for t in (texts or SAMPLE_GRAPH_TEXTS) if (t or "").strip()]
        if not docs:
            raise ValueError("texts 为空，无法构建图谱")
        kg_extractor, mode = self._build_extractor(extractor)
        self._index = PropertyGraphIndex.from_documents(
            docs,
            kg_extractors=[kg_extractor],
            embed_model=Settings.embed_model,
            property_graph_store=self.graph_store,
            embed_kg_nodes=True,
            show_progress=True,
        )
        return {
            "message": "图谱构建完成，数据已写入 Neo4j",
            "documents": len(docs),
            "extractor": mode,
            "neo4j_uri": NEO4J_URI,
        }

    def load_existing(self) -> dict:
        """从已有 Neo4j 图谱加载索引（不再重新抽文本）。"""
        self._index = PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
            embed_kg_nodes=True,
        )
        return {"message": "已从 Neo4j 加载图谱索引", "neo4j_uri": NEO4J_URI}

    def _ensure_index(self) -> PropertyGraphIndex:
        if self._index is None:
            self.load_existing()
        assert self._index is not None
        return self._index

    def query(self, question: str, *, k: int = 5) -> dict:
        """自然语言 GraphRAG 问答。"""
        index = self._ensure_index()
        engine = index.as_query_engine(include_text=True, similarity_top_k=k)
        response = engine.query(question)
        return {
            "question": question,
            "answer": str(response),
            "k": k,
            "mode": "graph_rag",
        }

    def retrieve(self, question: str, *, k: int = 5) -> dict:
        """只检索子图/节点，不生成答案。"""
        index = self._ensure_index()
        retriever = index.as_retriever(include_text=True, similarity_top_k=k)
        nodes = retriever.retrieve(question)
        items = []
        for i, node in enumerate(nodes):
            score = float(getattr(node, "score", 0.0) or 0.0)
            text = getattr(node, "text", None) or getattr(node.node, "text", "")
            items.append(
                {
                    "rank": i + 1,
                    "text": text,
                    "score": score,
                }
            )
        return {"question": question, "results": items, "total": len(items)}
