"""DashScope Embedding 安全封装：每批最多 10 条（API 硬限制）。

对齐 demo01_modular_rag.SafeDashScopeEmbedding。
"""

from __future__ import annotations

from typing import Any, List

from llama_index.core.base.embeddings.base import BaseEmbedding
from pydantic import PrivateAttr


class SafeDashScopeEmbedding(BaseEmbedding):
    """包装 DashScopeEmbedding，批量写入时自动按 10 条分批。"""

    _inner: Any = PrivateAttr(default=None)
    _batch_limit: int = PrivateAttr(default=10)

    def __init__(
        self,
        *,
        model_name: str = "text-embedding-v3",
        api_key: str | None = None,
        text_type: str = "document",
        batch_limit: int = 10,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        from llama_index.embeddings.dashscope import DashScopeEmbedding

        self._inner = DashScopeEmbedding(
            model_name=model_name,
            api_key=api_key,
            text_type=text_type,
        )
        self._batch_limit = max(1, int(batch_limit or 10))

    @classmethod
    def class_name(cls) -> str:
        return "SafeDashScopeEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._inner.get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._inner.get_text_embedding(text)

    def get_text_embedding_batch(
        self, texts: List[str], show_progress: bool = False
    ) -> List[List[float]]:
        limit = self._batch_limit
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), limit):
            batch = texts[i : i + limit]
            embs = self._inner.get_text_embedding_batch(
                batch, show_progress=show_progress
            )
            if not embs:
                raise RuntimeError(f"DashScope 返回空 embedding（batch {i // limit + 1}）")
            all_embeddings.extend(embs)
        return all_embeddings

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)
