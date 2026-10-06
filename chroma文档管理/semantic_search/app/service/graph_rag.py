"""GraphRAG：LlamaIndex PropertyGraphIndex + Neo4j。

飞书默认千问；本仓库支持 DeepSeek 做抽取/生成。
Embedding：DeepSeek 无接口，默认 Chinese-CLIP / HuggingFace，也可千问。
"""

from __future__ import annotations

from typing import List, Literal, Tuple

from llama_index.core import Document
from llama_index.core.indices.property_graph import (
    PropertyGraphIndex,
    SchemaLLMPathExtractor,
    SimpleLLMPathExtractor,
)
from llama_index.core.types import PydanticProgramMode

try:
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
except ModuleNotFoundError as exc:  # 未装图谱包时，延迟到真正用 GraphRAG 再报
    Neo4jPropertyGraphStore = None  # type: ignore[misc, assignment]
    _GRAPH_STORE_IMPORT_ERROR = exc
else:
    _GRAPH_STORE_IMPORT_ERROR = None

from semantic_search.app.config import (
    DASHSCOPE_API_KEY,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    GRAPH_EMBED_MODEL,
    GRAPH_EMBED_PROVIDER,
    GRAPH_EXTRACTOR,
    GRAPH_LLM_MODEL,
    GRAPH_LLM_PROVIDER,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)

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
        if _GRAPH_STORE_IMPORT_ERROR is not None or Neo4jPropertyGraphStore is None:
            raise RuntimeError(
                "未安装 GraphRAG 依赖。请执行: pip install llama-index-graph-stores-neo4j"
            ) from _GRAPH_STORE_IMPORT_ERROR
        if not NEO4J_PASSWORD:
            raise RuntimeError(
                "未配置 NEO4J_PASSWORD。请在 .env 写入 Neo4j 密码。"
            )
        self.llm = self._init_llm()
        self.embed_model = self._init_embed()
        self.graph_store = Neo4jPropertyGraphStore(
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            url=NEO4J_URI,
        )
        self._index: PropertyGraphIndex | None = None

    def _init_llm(self):
        provider = GRAPH_LLM_PROVIDER
        if provider == "dashscope":
            if not DASHSCOPE_API_KEY:
                raise RuntimeError("GRAPH_LLM_PROVIDER=dashscope 但未配置 DASHSCOPE_API_KEY")
            from llama_index.llms.dashscope import DashScope

            llm = DashScope(
                model_name=GRAPH_LLM_MODEL,
                api_key=DASHSCOPE_API_KEY,
                temperature=0,
                timeout=60,
                max_tokens=4096,
            )
        else:
            if not DEEPSEEK_API_KEY:
                raise RuntimeError(
                    "GraphRAG 使用 DeepSeek，但未找到 DEEPSEEK_API_KEY。"
                    "也可设 GRAPH_LLM_PROVIDER=dashscope 改用千问。"
                )
            from llama_index.llms.deepseek import DeepSeek

            llm = DeepSeek(
                model=GRAPH_LLM_MODEL,
                api_key=DEEPSEEK_API_KEY,
                api_base=DEEPSEEK_BASE_URL,
                temperature=0,
                max_tokens=4096,
            )
        # Schema 抽取走纯 LLM JSON，避免默认 program 模式不兼容
        try:
            llm.pydantic_program_mode = PydanticProgramMode.LLM
        except Exception:  # noqa: BLE001
            pass
        return llm

    def _init_embed(self):
        provider = GRAPH_EMBED_PROVIDER
        if provider in {"chinese_clip", "cn_clip", "chinese-clip"}:
            from semantic_search.app.chinese_clip_embedding import ChineseCLIPEmbedding

            return ChineseCLIPEmbedding(model_path=GRAPH_EMBED_MODEL)
        if provider == "dashscope":
            if not DASHSCOPE_API_KEY:
                raise RuntimeError("GRAPH_EMBED_PROVIDER=dashscope 但未配置 DASHSCOPE_API_KEY")
            from llama_index.embeddings.dashscope import DashScopeEmbedding

            return DashScopeEmbedding(
                model_name=GRAPH_EMBED_MODEL,
                api_key=DASHSCOPE_API_KEY,
            )
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        return HuggingFaceEmbedding(model_name=GRAPH_EMBED_MODEL)

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
        except Exception as exc:  # noqa: BLE001
            ok = False
            message = f"{type(exc).__name__}: {exc}"
        return {
            "ready": ok,
            "message": message,
            "neo4j_uri": NEO4J_URI,
            "neo4j_username": NEO4J_USERNAME,
            "llm_provider": GRAPH_LLM_PROVIDER,
            "llm_model": GRAPH_LLM_MODEL,
            "embed_provider": GRAPH_EMBED_PROVIDER,
            "embed_model": GRAPH_EMBED_MODEL,
            "extractor": GRAPH_EXTRACTOR,
            "has_index": self._index is not None,
            "deepseek_configured": bool(DEEPSEEK_API_KEY),
            "dashscope_configured": bool(DASHSCOPE_API_KEY),
        }

    def _build_extractor(self, mode: str | None = None):
        mode = (mode or GRAPH_EXTRACTOR).strip().lower()
        if mode in {"schema", "schema_llm", "schemallmpathextractor"}:
            return SchemaLLMPathExtractor(
                llm=self.llm,
                possible_entities=DEFAULT_ENTITIES,
                possible_relations=DEFAULT_RELATIONS,
                kg_validation_schema=DEFAULT_VALIDATION_SCHEMA,
                strict=True,
                max_triplets_per_chunk=10,
            ), "schema"
        return (
            SimpleLLMPathExtractor(
                llm=self.llm,
                max_paths_per_chunk=10,
                num_workers=2,
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
            embed_model=self.embed_model,
            property_graph_store=self.graph_store,
            embed_kg_nodes=True,
            show_progress=True,
        )
        return {
            "message": "图谱构建完成，数据已写入 Neo4j",
            "documents": len(docs),
            "extractor": mode,
            "llm_provider": GRAPH_LLM_PROVIDER,
            "embed_provider": GRAPH_EMBED_PROVIDER,
            "neo4j_uri": NEO4J_URI,
        }

    def load_existing(self) -> dict:
        """从已有 Neo4j 图谱加载索引（不再重新抽文本）。"""
        self._index = PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
            embed_model=self.embed_model,
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
        engine = index.as_query_engine(
            include_text=True,
            similarity_top_k=k,
            llm=self.llm,
            embed_model=self.embed_model,
        )
        response = engine.query(question)
        return {
            "question": question,
            "answer": str(response),
            "k": k,
            "mode": "graph_rag",
            "llm_provider": GRAPH_LLM_PROVIDER,
        }

    def retrieve(self, question: str, *, k: int = 5) -> dict:
        """只检索子图/节点，不生成答案。"""
        index = self._ensure_index()
        retriever = index.as_retriever(
            include_text=True,
            similarity_top_k=k,
            embed_model=self.embed_model,
        )
        nodes = retriever.retrieve(question)
        items = []
        for i, node in enumerate(nodes):
            score = float(getattr(node, "score", 0.0) or 0.0)
            text = getattr(node, "text", None) or getattr(node.node, "text", "")
            items.append({"rank": i + 1, "text": text, "score": score})
        return {"question": question, "results": items, "total": len(items)}

    def retrieve_as_nodes(self, question: str, *, k: int = 5) -> tuple[list, dict]:
        """给向量通道融合用：图谱片段包装成 NodeWithScore。"""
        from llama_index.core.schema import NodeWithScore, TextNode

        try:
            data = self.retrieve(question, k=k)
        except Exception as exc:  # noqa: BLE001
            info = {
                "enabled": True,
                "ok": False,
                "message": f"图谱检索失败: {exc}",
                "total": 0,
                "results": [],
            }
            return [], info
        packed = []
        for item in data.get("results") or []:
            text = (item.get("text") or "").strip()
            if not text:
                continue
            node = TextNode(
                text=f"[图谱] {text}",
                metadata={"channel": "graph"},
            )
            packed.append(
                NodeWithScore(node=node, score=float(item.get("score") or 0.0))
            )
        info = {
            "enabled": True,
            "ok": True,
            "message": f"图谱召回 {len(packed)} 条",
            "total": len(packed),
            "results": data.get("results") or [],
        }
        return packed, info
