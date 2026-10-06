"""多模态 RAG：Chinese-CLIP 图文向量 + 可选千问 VL 看图作答。

对齐飞书「01_多模态RAG」主路径（不做 ColPali）：
- 图像塔入库独立 Chroma 集合
- 以文搜图 / 以图搜图 / 以图搜文（仅文本库也是 CLIP 时）
- 召回图片后交给 qwen-vl-plus（有 DASHSCOPE_API_KEY）看图作答
"""

from __future__ import annotations

import base64
import hashlib
import mimetypes
import shutil
from pathlib import Path

from semantic_search.app.config import (
    CHROMA_PERSIST_DIR,
    DASHSCOPE_API_KEY,
    DASHSCOPE_COMPAT_BASE,
    DATA_DIR,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    IMAGE_COLLECTION_NAME,
    IMAGE_DIR,
    IMAGE_EXTS,
    LLM_MODEL,
    QDRANT_PATH,
    SIMILARITY_TOP_K,
    VL_MODEL,
    _DEFAULT_CHINESE_CLIP,
    normalize_vector_backend,
)
from semantic_search.app.vector_backends import ChromaSlot, open_qdrant_slot


def is_image_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTS


class MultimodalRagService:
    def __init__(self, engine, persist_dir: str = CHROMA_PERSIST_DIR):
        self.engine = engine
        self.image_dir = Path(IMAGE_DIR)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.clip = self._init_clip()
        self.image_slots = {}
        chroma_client = getattr(engine, "chroma_client", None) or engine.client
        try:
            img_col = chroma_client.get_collection(name=IMAGE_COLLECTION_NAME)
        except Exception:
            img_col = chroma_client.get_or_create_collection(
                name=IMAGE_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        dummy_index = getattr(engine.slots["chroma"], "index", None)
        self.image_slots["chroma"] = ChromaSlot(img_col, dummy_index, persist_label=persist_dir)
        self.image_slots["chroma"].raw_client = chroma_client
        if getattr(engine, "qdrant_ready", False) and engine.qdrant_client is not None:
            try:
                self.image_slots["qdrant"] = open_qdrant_slot(
                    QDRANT_PATH, IMAGE_COLLECTION_NAME, client=engine.qdrant_client
                )
            except Exception as exc:  # noqa: BLE001
                print(f"警告: Qdrant 图库初始化失败: {exc}")
        self.persist_dir = persist_dir
        self.collection = self.image_slots["chroma"]

    def _img(self, backend: str | None = None):
        name = normalize_vector_backend(backend)
        slot = self.image_slots.get(name)
        if slot is None:
            raise RuntimeError(f"图库后端不可用: {name}")
        return slot

    def _text_slot(self, backend: str | None = None):
        return self.engine.bind(backend).collection

    def _init_clip(self):
        current = None
        try:
            from llama_index.core import Settings

            current = Settings.embed_model
        except Exception:
            current = None
        from semantic_search.app.chinese_clip_embedding import ChineseCLIPEmbedding

        if isinstance(current, ChineseCLIPEmbedding):
            return current
        path = EMBEDDING_MODEL if EMBEDDING_PROVIDER == "chinese_clip" else _DEFAULT_CHINESE_CLIP
        if not Path(path).is_dir():
            raise RuntimeError(f"多模态需要本地 Chinese-CLIP 目录，未找到: {path}")
        print(f"多模态：加载 Chinese-CLIP 图像塔 {path}")
        return ChineseCLIPEmbedding(model_path=path)

    def status(self, backend: str | None = None) -> dict:
        slot = self._img(backend)
        chroma_n = self.image_slots["chroma"].count() if "chroma" in self.image_slots else 0
        qdrant_n = self.image_slots["qdrant"].count() if "qdrant" in self.image_slots else 0
        return {
            "ready": True,
            "image_count": slot.count(),
            "chroma_images": chroma_n,
            "qdrant_images": qdrant_n,
            "active_backend": normalize_vector_backend(backend),
            "image_dir": str(self.image_dir),
            "collection": IMAGE_COLLECTION_NAME,
            "clip_model": getattr(self.clip, "model_name", None) or str(self.clip.model_path),
            "text_embed_is_clip": EMBEDDING_PROVIDER in {"chinese_clip", "cn_clip", "chinese-clip"},
            "vl_ready": bool(DASHSCOPE_API_KEY),
            "vl_model": VL_MODEL if DASHSCOPE_API_KEY else None,
            "message": (
                f"当前图库 {slot.count()} 张（Chroma {chroma_n} / Qdrant {qdrant_n}）；"
                + ("千问 VL 可看图作答" if DASHSCOPE_API_KEY else "未配置 DASHSCOPE_API_KEY，看图作答将退回纯文本 LLM")
            ),
        }

    def list_images(self, backend: str | None = None) -> list[dict]:
        slot = self._img(backend)
        try:
            data = slot.get(include=["metadatas", "documents"])
        except Exception:
            return []
        metas = data.get("metadatas") or []
        docs = data.get("documents") or []
        items = []
        seen = set()
        for i, raw in enumerate(metas):
            meta = raw if isinstance(raw, dict) else {}
            name = str(meta.get("file_name") or (docs[i] if i < len(docs) else "") or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            items.append({"file_name": name, "kind": "image"})
        return items

    def resolve_image(self, name: str) -> Path:
        safe = Path(name).name
        path = (self.image_dir / safe).resolve()
        if not str(path).startswith(str(self.image_dir.resolve())):
            raise FileNotFoundError(name)
        if not path.is_file():
            raise FileNotFoundError(name)
        return path

    def ingest_paths(self, paths: list[str], backend: str | None = None) -> dict:
        saved: list[str] = []
        skipped: list[str] = []
        skipped_duplicates: list[str] = []
        seen: set[str] = set()
        slot = self._img(backend)
        for raw in paths:
            src = Path(raw)
            if not src.is_file() or not is_image_path(src) or src.name.startswith("_query"):
                skipped.append(src.name)
                continue
            digest = hashlib.sha256(src.read_bytes()).hexdigest()
            if digest in seen or slot.has_metadata("file_hash", digest) or slot.has_metadata("file_name", src.name):
                skipped_duplicates.append(src.name)
                print(f"跳过重复图片: {src.name}")
                continue
            seen.add(digest)
            dest = self.image_dir / src.name
            if src.resolve() != dest.resolve():
                shutil.copy2(src, dest)
            saved.append(str(dest))
        indexed = 0
        if saved:
            indexed = self._index_files(saved, backend=backend)
        return {
            "saved_images": [Path(p).name for p in saved],
            "skipped_files": skipped,
            "skipped_duplicates": skipped_duplicates,
            "indexed": indexed,
            "total_images": slot.count() if indexed or skipped_duplicates else self._img(backend).count(),
            "backend": normalize_vector_backend(backend),
        }

    def ingest_data_dir(self, root: str | None = None, backend: str | None = None) -> dict:
        base = Path(root or DATA_DIR)
        if not base.is_dir():
            return {"indexed": 0, "total_images": self._img(backend).count()}
        files = [
            str(p)
            for p in base.rglob("*")
            if p.is_file() and is_image_path(p) and not p.name.startswith("_query")
        ]
        if not files:
            return {"indexed": 0, "total_images": self._img(backend).count()}
        return self.ingest_paths(files, backend=backend)

    def _index_files(self, paths: list[str], backend: str | None = None) -> int:
        ids, embeddings, documents, metadatas = [], [], [], []
        for path in paths:
            p = Path(path)
            emb = self.clip.get_image_embedding(str(p))
            nid = hashlib.md5(p.name.encode("utf-8")).hexdigest()
            ids.append(nid)
            embeddings.append(emb)
            documents.append(p.name)
            metadatas.append(
                {
                    "file_name": p.name,
                    "image_path": str(p.resolve()),
                    "file_hash": hashlib.sha256(p.read_bytes()).hexdigest(),
                    "kind": "image",
                }
            )
        self._img(backend).upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"多模态：写入 {len(ids)} 张图片到 {normalize_vector_backend(backend)}，图库共 {self._img(backend).count()} 张")
        return len(ids)

    def _format_image_hits(self, raw: dict) -> list[dict]:
        ids = (raw.get("ids") or [[]])[0]
        docs = (raw.get("documents") or [[]])[0]
        metas = (raw.get("metadatas") or [[]])[0]
        dists = (raw.get("distances") or [[]])[0]
        hits = []
        for i, nid in enumerate(ids):
            dist = float(dists[i]) if i < len(dists) else 1.0
            similarity = round(max(1.0 - dist, 0.0), 4)
            name = (metas[i] or {}).get("file_name") or (docs[i] if i < len(docs) else nid)
            hits.append(
                {
                    "rank": i + 1,
                    "index": i,
                    "id": nid,
                    "file_name": name,
                    "url": f"/mm/files/{name}",
                    "document": f"[图片] {name}",
                    "similarity": similarity,
                    "distance": round(dist, 4),
                    "kind": "image",
                }
            )
        return hits

    def search_images_by_text(self, query: str, k: int = SIMILARITY_TOP_K, backend: str | None = None) -> list[dict]:
        total = self._img(backend).count()
        if total == 0 or not (query or "").strip():
            return []
        k = min(max(k, 1), total)
        emb = self.clip.get_text_embedding(query.strip())
        raw = self._img(backend).query(query_embeddings=[emb], n_results=k)
        return self._format_image_hits(raw)

    def search_images_by_image(self, image_path: str, k: int = SIMILARITY_TOP_K, backend: str | None = None) -> list[dict]:
        total = self._img(backend).count()
        if total == 0:
            return []
        k = min(max(k, 1), total)
        emb = self.clip.get_image_embedding(image_path)
        raw = self._img(backend).query(query_embeddings=[emb], n_results=k)
        return self._format_image_hits(raw)

    def search_texts_by_image(self, image_path: str, k: int = SIMILARITY_TOP_K, backend: str | None = None) -> list[dict]:
        """以图搜文：仅当文本库也是同一套 CLIP 向量时有效。"""
        if EMBEDDING_PROVIDER not in {"chinese_clip", "cn_clip", "chinese-clip"}:
            return []
        text_slot = self._text_slot(backend)
        total = text_slot.count()
        if total == 0:
            return []
        k = min(max(k, 1), total)
        emb = self.clip.get_image_embedding(image_path)
        raw = text_slot.query(query_embeddings=[emb], n_results=k)
        ids = (raw.get("ids") or [[]])[0]
        docs = (raw.get("documents") or [[]])[0]
        dists = (raw.get("distances") or [[]])[0]
        hits = []
        for i, _nid in enumerate(ids):
            dist = float(dists[i]) if i < len(dists) else 1.0
            text = docs[i] if i < len(docs) else ""
            hits.append(
                {
                    "rank": i + 1,
                    "index": i,
                    "document": text,
                    "similarity": round(max(1.0 - dist, 0.0), 4),
                    "distance": round(dist, 4),
                    "kind": "text",
                }
            )
        return hits

    def save_query_image(self, filename: str, content: bytes) -> Path:
        suffix = Path(filename or "query.jpg").suffix.lower()
        if suffix not in IMAGE_EXTS:
            suffix = ".jpg"
        dest = self.image_dir / f"_query{suffix}"
        dest.write_bytes(content)
        return dest

    def _image_data_url(self, path: Path) -> str:
        mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"

    def _vl_answer(self, question: str, image_paths: list[Path], text_bits: list[str]) -> str:
        from openai import OpenAI

        parts: list[dict] = []
        ctx = "\n\n".join(text_bits[:6]) if text_bits else "（没有文本资料）"
        prompt = (
            "你是多模态知识库助手。请结合用户问题和下面检索到的图片/文本作答，"
            "用简体中文。看不清的细节不要编造。\n\n"
            f"问题：{question}\n\n文本资料：\n{ctx}"
        )
        parts.append({"type": "text", "text": prompt})
        for path in image_paths[:4]:
            parts.append({"type": "image_url", "image_url": {"url": self._image_data_url(path)}})
        client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_COMPAT_BASE)
        resp = client.chat.completions.create(
            model=VL_MODEL,
            messages=[{"role": "user", "content": parts}],
            max_tokens=1024,
        )
        return (resp.choices[0].message.content or "").strip()

    def _vl_describe(self, question: str, image_path: Path) -> str:
        from openai import OpenAI

        prompt = (
            "请只分析用户刚刚上传的这一张图片，用简体中文详细说明："
            "1）图中有哪些主体、人物或物体；2）场景和环境；"
            "3）图上可见的文字；4）颜色、构图和显著细节。"
            "看不清的不要编造。不要提知识库里其他图片。\n\n"
            f"用户问题：{question}"
        )
        client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_COMPAT_BASE)
        resp = client.chat.completions.create(
            model=VL_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": self._image_data_url(image_path)}},
                ],
            }],
            max_tokens=1024,
        )
        return (resp.choices[0].message.content or "").strip()

    def describe(
        self,
        question: str,
        query_image_path: str,
        *,
        k: int = SIMILARITY_TOP_K,
        backend: str | None = None,
    ) -> dict:
        q = (question or "").strip() or "请详细分析这张图片里有什么"
        path = Path(query_image_path)
        image_hits = []
        try:
            image_hits = self.search_images_by_image(str(path), k=k, backend=backend)
        except Exception:
            image_hits = []
        vl_used = False
        if DASHSCOPE_API_KEY and path.is_file():
            try:
                answer = self._vl_describe(q, path)
                vl_used = True
            except Exception as exc:  # noqa: BLE001
                answer = self._text_fallback_answer(q, image_hits, [])
                answer = f"（千问 VL 调用失败：{exc}，已退回文本模型）\n\n{answer}"
        else:
            answer = self._text_fallback_answer(q, image_hits, [])
            if not DASHSCOPE_API_KEY:
                answer = (
                    "还不能真正看图：请在环境变量配置 DASHSCOPE_API_KEY（千问 VL，如 qwen-vl-plus）。\n"
                    "当前只会把图片写入图库，并用 CLIP 找相似图。\n\n"
                    + answer
                )
        return {
            "question": q,
            "answer": answer,
            "sources": image_hits,
            "images": image_hits,
            "vl_used": vl_used,
            "vl_model": VL_MODEL if vl_used else None,
            "message": "已分析用户上传的图片" if vl_used else "未配置视觉模型，无法描述图像内容",
        }

    def _text_fallback_answer(self, question: str, image_hits: list[dict], text_hits: list[dict]) -> str:
        names = "、".join(h.get("file_name") or "" for h in image_hits[:5]) or "无"
        texts = "\n".join((h.get("document") or "")[:400] for h in text_hits[:4]) or "无"
        prompt = (
            "当前没有视觉大模型，只能根据图片文件名和文本检索结果回答。"
            "请说明你看不到图像内容。\n"
            f"问题：{question}\n检索到的图片：{names}\n文本：\n{texts}"
        )
        if not DEEPSEEK_API_KEY:
            return (
                "未配置 DASHSCOPE_API_KEY（qwen-vl）也未配置 DEEPSEEK_API_KEY，无法生成看图答案。"
                f"检索到图片：{names}"
            )
        from openai import OpenAI

        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return (resp.choices[0].message.content or "").strip()

    def ask(
        self,
        question: str,
        *,
        query_image_path: str | None = None,
        k: int = SIMILARITY_TOP_K,
        backend: str | None = None,
    ) -> dict:
        q = (question or "").strip() or "请描述这些图片"
        image_hits: list[dict] = []
        text_hits: list[dict] = []
        if query_image_path:
            image_hits = self.search_images_by_image(query_image_path, k=k, backend=backend)
            text_hits = self.search_texts_by_image(query_image_path, k=k, backend=backend)
        if q:
            by_text = self.search_images_by_text(q, k=k, backend=backend)
            seen = {h["file_name"] for h in image_hits}
            for hit in by_text:
                if hit["file_name"] not in seen:
                    image_hits.append(hit)
                    seen.add(hit["file_name"])
        image_hits = image_hits[:k]
        look_paths: list[Path] = []
        if query_image_path:
            look_paths.append(Path(query_image_path))
        for hit in image_hits:
            try:
                look_paths.append(self.resolve_image(hit["file_name"]))
            except FileNotFoundError:
                continue
        # 去重
        uniq: list[Path] = []
        used = set()
        for p in look_paths:
            key = str(p.resolve())
            if key in used:
                continue
            used.add(key)
            uniq.append(p)
        text_bits = [h.get("document") or "" for h in text_hits]
        vl_used = False
        if DASHSCOPE_API_KEY and uniq:
            try:
                answer = self._vl_answer(q, uniq, text_bits)
                vl_used = True
            except Exception as exc:  # noqa: BLE001
                answer = self._text_fallback_answer(q, image_hits, text_hits)
                answer = f"（千问 VL 调用失败：{exc}，已退回文本模型）\n\n{answer}"
        else:
            answer = self._text_fallback_answer(q, image_hits, text_hits)

        sources = list(image_hits)
        for i, hit in enumerate(text_hits[:k], start=len(sources) + 1):
            item = dict(hit)
            item["rank"] = i
            sources.append(item)
        return {
            "question": q,
            "answer": answer,
            "sources": sources,
            "images": image_hits,
            "vl_used": vl_used,
            "vl_model": VL_MODEL if vl_used else None,
            "message": "LMM 看图作答" if vl_used else "未走视觉模型，仅用文件名与文本",
        }
