"""GraphRAG：LlamaIndex PropertyGraphIndex + Neo4j。

抽取与生成使用 DeepSeek。Embedding 用本地 Chinese-CLIP / HuggingFace。
"""

from __future__ import annotations

import re
import socket
from typing import List, Literal, Tuple
from urllib.parse import urlparse

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


def neo4j_bolt_reachable(uri: str | None = None, timeout: float = 0.2) -> bool:
    """只探测 Bolt 端口是否在听，不走 Neo4j 驱动重试。"""
    parsed = urlparse(uri or NEO4J_URI)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 7687
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


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
        if not neo4j_bolt_reachable():
            raise RuntimeError(
                f"Neo4j 未在 {NEO4J_URI} 监听。向量搜索可继续用；需要图谱时再执行 neo4j console。"
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
        if not DEEPSEEK_API_KEY:
            raise RuntimeError("GraphRAG 使用 DeepSeek，但未找到 DEEPSEEK_API_KEY。")
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
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        return HuggingFaceEmbedding(model_name=GRAPH_EMBED_MODEL)

    def _driver(self):
        from neo4j import GraphDatabase

        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def _run_cypher(self, query: str, **params) -> list[dict]:
        """执行只读/写 Cypher，返回字典行。"""
        driver = self._driver()
        try:
            with driver.session() as session:
                result = session.run(query, **params)
                return [dict(record) for record in result]
        finally:
            driver.close()

    def graph_counts(self) -> dict:
        """节点 / 关系数量与示例三元组。"""
        try:
            rows = self._run_cypher(
                "MATCH (n) WITH count(n) AS nodes "
                "OPTIONAL MATCH ()-[r]->() WITH nodes, count(r) AS rels "
                "RETURN nodes, rels"
            )
            nodes = int((rows[0] or {}).get("nodes") or 0) if rows else 0
            rels = int((rows[0] or {}).get("rels") or 0) if rows else 0
            samples = self._run_cypher(
                "MATCH (a)-[r]->(b) "
                "RETURN coalesce(a.name, a.id, elementId(a)) AS subject, "
                "type(r) AS relation, "
                "coalesce(b.name, b.id, elementId(b)) AS object "
                "LIMIT 8"
            )
            return {"node_count": nodes, "rel_count": rels, "sample_triples": samples}
        except Exception as exc:  # noqa: BLE001
            return {"node_count": 0, "rel_count": 0, "sample_triples": [], "error": str(exc)}

    @staticmethod
    def browser_url() -> str:
        """Neo4j Browser 常见地址（HTTP 7474）。"""
        parsed = urlparse(NEO4J_URI)
        host = parsed.hostname or "127.0.0.1"
        return f"http://{host}:7474"

    def status(self) -> dict:
        """连通性与配置摘要（不回显密码）。"""
        ok = True
        message = "ok"
        counts = {"node_count": 0, "rel_count": 0, "sample_triples": []}
        try:
            driver = self._driver()
            driver.verify_connectivity()
            driver.close()
            counts = self.graph_counts()
        except Exception as exc:  # noqa: BLE001
            ok = False
            message = f"{type(exc).__name__}: {exc}"
        return {
            "ready": ok,
            "message": message,
            "neo4j_uri": NEO4J_URI,
            "neo4j_username": NEO4J_USERNAME,
            "browser_url": self.browser_url(),
            "node_count": counts.get("node_count", 0),
            "rel_count": counts.get("rel_count", 0),
            "sample_triples": counts.get("sample_triples") or [],
            "llm_provider": GRAPH_LLM_PROVIDER,
            "llm_model": GRAPH_LLM_MODEL,
            "embed_provider": GRAPH_EMBED_PROVIDER,
            "embed_model": GRAPH_EMBED_MODEL,
            "extractor": GRAPH_EXTRACTOR,
            "has_index": self._index is not None,
            "deepseek_configured": bool(DEEPSEEK_API_KEY),
        }

    def clear_graph(self) -> dict:
        """清空 Neo4j 中全部节点与关系（学习用重置）。"""
        before = self.graph_counts()
        self._run_cypher("MATCH (n) DETACH DELETE n")
        self._index = None
        after = self.graph_counts()
        return {
            "message": "已清空 Neo4j 图谱",
            "deleted_nodes": int(before.get("node_count") or 0),
            "deleted_rels": int(before.get("rel_count") or 0),
            "node_count": int(after.get("node_count") or 0),
            "rel_count": int(after.get("rel_count") or 0),
        }

    def delete_by_file_hint(self, file_name: str) -> dict:
        """按文件名尽力清理图谱侧痕迹（属性或文本含文件名）。"""
        want = (file_name or "").strip()
        if not want:
            return {"deleted_nodes": 0, "message": "文件名为空"}
        stem = want.rsplit(".", 1)[0]
        try:
            counted = self._run_cypher(
                "MATCH (n) "
                "WHERE any(k IN keys(n) WHERE toLower(toString(n[k])) CONTAINS toLower($fname)) "
                "   OR toLower(toString(coalesce(n.name, ''))) CONTAINS toLower($stem) "
                "RETURN count(n) AS n",
                fname=want,
                stem=stem,
            )
            deleted = int((counted[0] or {}).get("n") or 0) if counted else 0
            if deleted:
                self._run_cypher(
                    "MATCH (n) "
                    "WHERE any(k IN keys(n) WHERE toLower(toString(n[k])) CONTAINS toLower($fname)) "
                    "   OR toLower(toString(coalesce(n.name, ''))) CONTAINS toLower($stem) "
                    "DETACH DELETE n",
                    fname=want,
                    stem=stem,
                )
                self._index = None
            return {
                "deleted_nodes": deleted,
                "message": f"图谱侧按文件名清理 {deleted} 个节点",
                "file_name": want,
            }
        except Exception as exc:  # noqa: BLE001
            return {"deleted_nodes": 0, "message": f"图谱清理跳过: {exc}", "file_name": want}

    def _mention_candidates(self, question: str) -> list[str]:
        """从问题里抽出可能实体名（轻量，不强制 LLM）。"""
        q = (question or "").strip()
        if not q:
            return []
        known = [
            "乔布斯", "沃兹尼亚克", "苹果公司", "苹果", "里德学院",
            "加州大学伯克利分校", "伯克利", "库比蒂诺", "贝壳科技",
        ]
        hits = [name for name in known if name in q]
        # 再抓「X创立/毕业于」等模式里的专名碎片
        for m in re.finditer(r"([\u4e00-\u9fffA-Za-z0-9]{2,12})(?:创立|创建|毕业于|位于|和|与)", q):
            name = m.group(1)
            if name not in hits and name not in {"什么", "哪些", "谁", "哪里", "公司"}:
                hits.append(name)
        if hits:
            return hits[:6]
        # 兜底：问 LLM 抽 1~3 个实体（失败则空）
        try:
            raw = self.llm.complete(
                "从问题中抽出最多3个实体名，用英文逗号分隔，不要解释。\n问题：" + q
            ).text.strip()
            parts = [p.strip() for p in re.split(r"[,，、]", raw) if p.strip()]
            return parts[:3]
        except Exception:  # noqa: BLE001
            return []

    def explain_paths(self, question: str, *, hops: int = 2, limit: int = 20) -> dict:
        """围绕问题实体做 1~2 跳路径证据（Cypher）。"""
        hops = max(1, min(int(hops or 2), 3))
        mentions = self._mention_candidates(question)
        paths: list[dict] = []
        seen: set[tuple[str, str, str]] = set()
        if not mentions:
            # 无实体时给全局样例边，避免前端空白
            for row in (self.graph_counts().get("sample_triples") or [])[:limit]:
                key = (str(row.get("subject")), str(row.get("relation")), str(row.get("object")))
                if key in seen:
                    continue
                seen.add(key)
                paths.append({
                    "subject": key[0],
                    "relation": key[1],
                    "object": key[2],
                    "path": f"{key[0]} —[{key[1]}]→ {key[2]}",
                    "hops": 1,
                })
            return {
                "mentions": [],
                "paths": paths,
                "message": "未识别到实体，展示图谱样例边",
            }

        _ = hops  # 对外保留参数；Cypher 用固定 1..2 兼容更多 Neo4j 版本
        for name in mentions:
            try:
                rows = self._run_cypher(
                    "MATCH (a)-[rel]->(b) "
                    "WHERE toLower(toString(coalesce(a.name, a.id, ''))) CONTAINS toLower($name) "
                    "   OR toLower(toString(coalesce(b.name, b.id, ''))) CONTAINS toLower($name) "
                    "RETURN coalesce(a.name, a.id) AS subject, type(rel) AS relation, "
                    "coalesce(b.name, b.id) AS object "
                    "LIMIT $lim",
                    name=name,
                    lim=limit,
                )
            except Exception:  # noqa: BLE001
                rows = []
            for row in rows:
                subj = str(row.get("subject") or "")
                rel = str(row.get("relation") or "")
                obj = str(row.get("object") or "")
                key = (subj, rel, obj)
                if not subj or not obj or key in seen:
                    continue
                seen.add(key)
                paths.append({
                    "subject": subj,
                    "relation": rel,
                    "object": obj,
                    "path": f"{subj} —[{rel}]→ {obj}",
                    "hops": 1,
                    "anchor": name,
                })
                if len(paths) >= limit:
                    break
            if len(paths) >= limit:
                break
        return {
            "mentions": mentions,
            "paths": paths,
            "message": f"识别实体 {mentions}，找到 {len(paths)} 条关系边",
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
            llm=self.llm,
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

    def build_from_files(
        self,
        file_paths: List[str],
        *,
        extractor: str | None = None,
    ) -> dict:
        """读取本地文件，分块后抽三元组写入 Neo4j。"""
        from semantic_search.app.file_loaders import make_directory_reader
        from llama_index.core.node_parser import SentenceSplitter

        paths = [p for p in file_paths if p]
        if not paths:
            raise ValueError("没有可导入图谱的文件")
        docs = make_directory_reader(input_files=paths).load_data()
        if not docs:
            raise ValueError("文件中没有可读文本")
        nodes = SentenceSplitter(chunk_size=512, chunk_overlap=64).get_nodes_from_documents(docs)
        texts = [n.get_content().strip() for n in nodes if (n.get_content() or "").strip()]
        result = self.build_from_texts(texts, extractor=extractor)
        result["source_files"] = [str(p) for p in paths]
        result["chunks"] = len(texts)
        result["message"] = "已从上传文件抽取三元组并写入 Neo4j"
        return result

    def load_existing(self) -> dict:
        """从已有 Neo4j 图谱加载索引（不再重新抽文本）。"""
        self._index = PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
            llm=self.llm,
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
        evidence = self.explain_paths(question, hops=2, limit=16)
        return {
            "question": question,
            "answer": str(response),
            "k": k,
            "mode": "graph_rag",
            "llm_provider": GRAPH_LLM_PROVIDER,
            "mentions": evidence.get("mentions") or [],
            "paths": evidence.get("paths") or [],
            "evidence_message": evidence.get("message") or "",
            "browser_url": self.browser_url(),
        }

    def retrieve(self, question: str, *, k: int = 5) -> dict:
        """只检索子图/节点，不生成答案。"""
        index = self._ensure_index()
        # 索引已绑定 embed_model，这里再传会触发 "multiple values for keyword argument"
        retriever = index.as_retriever(
            include_text=True,
            similarity_top_k=k,
        )
        nodes = retriever.retrieve(question)
        items = []
        for i, node in enumerate(nodes):
            score = float(getattr(node, "score", 0.0) or 0.0)
            text = getattr(node, "text", None) or getattr(node.node, "text", "")
            items.append({"rank": i + 1, "text": text, "score": score})
        evidence = self.explain_paths(question, hops=2, limit=16)
        return {
            "question": question,
            "results": items,
            "total": len(items),
            "mentions": evidence.get("mentions") or [],
            "paths": evidence.get("paths") or [],
            "evidence_message": evidence.get("message") or "",
        }

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
                "paths": [],
                "mentions": [],
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
        # 把路径边也塞进上下文，方便生成时引用
        for p in (data.get("paths") or [])[:8]:
            line = p.get("path") or f"{p.get('subject')} -[{p.get('relation')}]-> {p.get('object')}"
            node = TextNode(
                text=f"[图谱路径] {line}",
                metadata={"channel": "graph", "source_kind": "graph_path"},
            )
            packed.append(NodeWithScore(node=node, score=0.9))
        info = {
            "enabled": True,
            "ok": True,
            "message": f"图谱召回 {len(data.get('results') or [])} 条，路径 {len(data.get('paths') or [])} 条",
            "total": len(packed),
            "results": data.get("results") or [],
            "paths": data.get("paths") or [],
            "mentions": data.get("mentions") or [],
            "evidence_message": data.get("evidence_message") or "",
        }
        return packed, info

    def add_manual_triple(
        self,
        subject: str,
        relation: str,
        obj: str,
        *,
        subject_label: str = "entity",
        object_label: str = "entity",
    ) -> dict:
        """手工写入一条三元组（头实体-关系-尾实体），不经过 LLM 抽取。"""
        from llama_index.core.graph_stores.types import EntityNode, Relation

        subj = (subject or "").strip()
        rel_raw = (relation or "").strip()
        obj_name = (obj or "").strip()
        if not subj or not rel_raw or not obj_name:
            raise ValueError("头实体、关系、尾实体都不能为空")
        src_label = _neo4j_label(subject_label, default="entity")
        dst_label = _neo4j_label(object_label, default="entity")
        rel_label = _neo4j_label(rel_raw, default="RELATED_TO")

        src_emb = self.embed_model.get_text_embedding(subj)
        dst_emb = self.embed_model.get_text_embedding(obj_name)
        src = EntityNode(
            name=subj,
            label=src_label,
            embedding=src_emb,
            properties={"source": "manual"},
        )
        dst = EntityNode(
            name=obj_name,
            label=dst_label,
            embedding=dst_emb,
            properties={"source": "manual"},
        )
        rel = Relation(
            label=rel_label,
            source_id=src.id,
            target_id=dst.id,
            properties={"source": "manual", "raw": rel_raw},
        )
        self.graph_store.upsert_nodes([src, dst])
        self.graph_store.upsert_relations([rel])
        try:
            self.load_existing()
        except Exception:  # noqa: BLE001
            self._index = None
        return {
            "message": "已手工写入三元组",
            "subject": subj,
            "subject_label": src_label,
            "relation": rel_label,
            "object": obj_name,
            "object_label": dst_label,
        }


def _neo4j_label(raw: str, *, default: str) -> str:
    text = re.sub(r"[^\w]+", "_", (raw or "").strip(), flags=re.UNICODE).strip("_")
    if not text:
        return default
    if text[0].isdigit():
        text = "N_" + text
    return text[:64]
