"""Chroma / Qdrant 双后端：同一套 Embedding，两套独立持久化集合。"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import TextNode


def _payload_text(payload: dict | None) -> str:
    if not payload:
        return ""
    if payload.get("text"):
        return str(payload["text"])
    raw = payload.get("_node_content")
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            return str(data.get("text") or data.get("content") or raw)
        except Exception:
            return raw
    return str(payload.get("document") or payload.get("file_name") or "")


def _as_point_id(raw: str) -> str:
    hex_id = uuid.uuid5(uuid.NAMESPACE_URL, raw).hex
    return str(uuid.UUID(hex=hex_id))


@dataclass
class VectorSlot:
    name: str
    index: VectorStoreIndex
    persist_label: str
    kind: str
    raw_client: Any = None
    collection_name: str = ""
    extra: dict = field(default_factory=dict)

    def has_metadata(self, key: str, value: str) -> bool:
        return False

    def get(self, include: list | None = None) -> dict:
        raise NotImplementedError

    def query(self, query_embeddings: list, n_results: int = 5) -> dict:
        raise NotImplementedError

    def upsert(self, ids, embeddings, documents, metadatas) -> None:
        raise NotImplementedError

    def rebuild_empty_index(self) -> VectorStoreIndex:
        raise NotImplementedError


class ChromaSlot(VectorSlot):
    kind = "chroma"

    def __init__(self, collection, index: VectorStoreIndex, persist_label: str, name: str = "chroma"):
        super().__init__(
            name=name,
            index=index,
            persist_label=persist_label,
            kind="chroma",
            raw_client=collection._client if hasattr(collection, "_client") else None,
            collection_name=collection.name,
        )
        self.collection = collection

    def count(self) -> int:
        return int(self.collection.count() or 0)

    def has_metadata(self, key: str, value: str) -> bool:
        if not value:
            return False
        try:
            data = self.collection.get(where={key: str(value)}, limit=1, include=[])
            return bool(data.get("ids"))
        except Exception:
            return False

    def get(self, include: list | None = None) -> dict:
        return self.collection.get(include=include or ["documents", "metadatas"])

    def query(self, query_embeddings: list, n_results: int = 5) -> dict:
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results)

    def upsert(self, ids, embeddings, documents, metadatas) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def rebuild_empty_index(self) -> VectorStoreIndex:
        from llama_index.vector_stores.chroma import ChromaVectorStore

        name = self.collection.name
        client = self.raw_client
        if client is not None:
            try:
                client.delete_collection(name)
            except Exception:
                pass
            self.collection = client.get_or_create_collection(name=name)
        store = ChromaVectorStore(chroma_collection=self.collection)
        self.index = VectorStoreIndex(nodes=[], storage_context=StorageContext.from_defaults(vector_store=store))
        return self.index


class QdrantSlot(VectorSlot):
    kind = "qdrant"

    def __init__(self, client, collection_name: str, index: VectorStoreIndex, persist_label: str, name: str = "qdrant"):
        super().__init__(
            name=name,
            index=index,
            persist_label=persist_label,
            kind="qdrant",
            raw_client=client,
            collection_name=collection_name,
        )
        self.client = client

    def _exists(self) -> bool:
        try:
            names = [c.name for c in self.client.get_collections().collections]
            return self.collection_name in names
        except Exception:
            return False

    def count(self) -> int:
        if not self._exists():
            return 0
        try:
            return int(self.client.count(self.collection_name, exact=True).count)
        except Exception:
            return 0

    def has_metadata(self, key: str, value: str) -> bool:
        if not value or not self._exists():
            return False
        try:
            from qdrant_client.http.models import FieldCondition, Filter, MatchValue

            records, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(key=key, match=MatchValue(value=str(value)))]
                ),
                limit=1,
                with_payload=False,
                with_vectors=False,
            )
            return bool(records)
        except Exception:
            return False

    def get(self, include: list | None = None) -> dict:
        ids, documents, metadatas = [], [], []
        if not self._exists():
            return {"ids": ids, "documents": documents, "metadatas": metadatas}
        offset = None
        while True:
            records, offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=128,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for rec in records:
                payload = rec.payload or {}
                text = _payload_text(payload)
                ids.append(str(rec.id))
                documents.append(text)
                metadatas.append(payload if isinstance(payload, dict) else {})
            if offset is None:
                break
        return {"ids": ids, "documents": documents, "metadatas": metadatas}

    def query(self, query_embeddings: list, n_results: int = 5) -> dict:
        empty = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        if not query_embeddings or not self._exists() or self.count() == 0:
            return empty
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embeddings[0],
            limit=max(1, n_results),
            with_payload=True,
        )
        ids, docs, metas, dists = [], [], [], []
        for hit in hits:
            payload = hit.payload or {}
            ids.append(str(hit.id))
            docs.append(_payload_text(payload))
            metas.append(payload if isinstance(payload, dict) else {})
            score = float(hit.score or 0.0)
            dists.append(max(1.0 - score, 0.0))
        return {"ids": [ids], "documents": [docs], "metadatas": [metas], "distances": [dists]}

    def upsert(self, ids, embeddings, documents, metadatas) -> None:
        from qdrant_client.http.models import Distance, PointStruct, VectorParams

        if not embeddings:
            return
        dim = len(embeddings[0])
        if not self._exists():
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
        points = []
        for i, nid in enumerate(ids):
            payload = dict(metadatas[i] if i < len(metadatas) and isinstance(metadatas[i], dict) else {})
            payload["text"] = documents[i] if i < len(documents) else ""
            payload["doc_id"] = str(nid)
            points.append(
                PointStruct(
                    id=_as_point_id(str(nid)),
                    vector=embeddings[i],
                    payload=payload,
                )
            )
        self.client.upsert(collection_name=self.collection_name, points=points)

    def rebuild_empty_index(self) -> VectorStoreIndex:
        from llama_index.vector_stores.qdrant import QdrantVectorStore

        try:
            if self._exists():
                self.client.delete_collection(self.collection_name)
        except Exception as exc:  # noqa: BLE001
            print(f"警告: 删除 Qdrant 集合失败: {exc}")
        store = QdrantVectorStore(client=self.client, collection_name=self.collection_name)
        self.index = VectorStoreIndex(nodes=[], storage_context=StorageContext.from_defaults(vector_store=store))
        return self.index


def open_chroma_slot(persist_dir: str, collection_name: str) -> ChromaSlot:
    import chromadb
    from llama_index.vector_stores.chroma import ChromaVectorStore

    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name=collection_name)
    store = ChromaVectorStore(chroma_collection=collection)
    if collection.count() > 0:
        index = VectorStoreIndex.from_vector_store(vector_store=store)
    else:
        index = VectorStoreIndex(nodes=[], storage_context=StorageContext.from_defaults(vector_store=store))
    slot = ChromaSlot(collection, index, persist_label=persist_dir)
    slot.raw_client = client
    return slot


def open_qdrant_slot(persist_dir: str, collection_name: str, client=None) -> QdrantSlot:
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient

    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    if client is None:
        client = QdrantClient(path=persist_dir)
    store = QdrantVectorStore(client=client, collection_name=collection_name)
    names = []
    try:
        names = [c.name for c in client.get_collections().collections]
    except Exception:
        names = []
    if collection_name in names:
        try:
            n = client.count(collection_name, exact=True).count
        except Exception:
            n = 0
        if n > 0:
            index = VectorStoreIndex.from_vector_store(vector_store=store)
        else:
            index = VectorStoreIndex(nodes=[], storage_context=StorageContext.from_defaults(vector_store=store))
    else:
        index = VectorStoreIndex(nodes=[], storage_context=StorageContext.from_defaults(vector_store=store))
    return QdrantSlot(client, collection_name, index, persist_label=persist_dir)


def nodes_from_slot(slot: VectorSlot) -> list[TextNode]:
    docs = getattr(getattr(slot.index, "docstore", None), "docs", None) or {}
    if docs:
        return list(docs.values())
    data = slot.get(include=["documents", "metadatas"])
    nodes: list[TextNode] = []
    ids = data.get("ids") or []
    documents = data.get("documents") or []
    metadatas = data.get("metadatas") or []
    for i, doc_id in enumerate(ids):
        text = ((documents[i] if i < len(documents) else "") or "").strip()
        if not text:
            continue
        meta = metadatas[i] if i < len(metadatas) and isinstance(metadatas[i], dict) else {}
        nodes.append(TextNode(text=text, id_=str(doc_id), metadata=meta or {}))
    return nodes
