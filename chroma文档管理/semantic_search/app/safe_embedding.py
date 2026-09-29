"""DashScope Embedding 安全封装：每批最多 10 条（API 硬限制）。

对齐 demo01_modular_rag.SafeDashScopeEmbedding。
"""  # 模块说明：分批调用，避免一次超 10 条报错

from __future__ import annotations  # 允许注解里写尚未定义的类型

from typing import Any, List  # 内层模型用 Any；向量与文本列表用 List

from llama_index.core.base.embeddings.base import BaseEmbedding  # 继承官方 Embedding 基类
from pydantic import PrivateAttr  # 用私有属性存内层模型与批大小


class SafeDashScopeEmbedding(BaseEmbedding):  # 包装 DashScope，自动按批上限切片
    """包装 DashScopeEmbedding，批量写入时自动按 10 条分批。"""

    _inner: Any = PrivateAttr(default=None)  # 真正的 DashScopeEmbedding 实例
    _batch_limit: int = PrivateAttr(default=10)  # 每批最多条数（API 限制）

    def __init__(  # 构造：创建内层模型并固定批上限
        self,
        *,
        model_name: str = "text-embedding-v3",  # 默认 DashScope 向量模型
        api_key: str | None = None,  # API Key；None 则走环境变量
        text_type: str = "document",  # 文本类型：document / query
        batch_limit: int = 10,  # 调用方也可改批大小（仍至少为 1）
        **kwargs: Any,  # 透传给 BaseEmbedding
    ):
        super().__init__(**kwargs)  # 先初始化基类字段
        from llama_index.embeddings.dashscope import DashScopeEmbedding  # 延迟导入，避免无依赖时拖垮模块

        self._inner = DashScopeEmbedding(  # 创建真实 Embedding 客户端
            model_name=model_name,  # 模型名
            api_key=api_key,  # 密钥
            text_type=text_type,  # document 或 query
        )
        self._batch_limit = max(1, int(batch_limit or 10))  # 批上限至少为 1

    @classmethod
    def class_name(cls) -> str:  # LlamaIndex 序列化/识别用类名
        return "SafeDashScopeEmbedding"  # 固定类名字符串

    def _get_query_embedding(self, query: str) -> List[float]:  # 单条查询向量
        return self._inner.get_query_embedding(query)  # 直接委托内层

    def _get_text_embedding(self, text: str) -> List[float]:  # 单条文档向量
        return self._inner.get_text_embedding(text)  # 直接委托内层

    def get_text_embedding_batch(  # 批量向量化：按批上限切片再合并
        self, texts: List[str], show_progress: bool = False  # 文本列表与是否显示进度
    ) -> List[List[float]]:  # 返回与 texts 对齐的向量列表
        limit = self._batch_limit  # 本实例的批大小
        all_embeddings: List[List[float]] = []  # 汇总各批结果
        for i in range(0, len(texts), limit):  # 步进 limit 切批
            batch = texts[i : i + limit]  # 当前这一批文本
            embs = self._inner.get_text_embedding_batch(  # 调 DashScope 本批向量化
                batch, show_progress=show_progress  # 透传进度条开关
            )
            if not embs:  # API 返回空则视为失败
                raise RuntimeError(f"DashScope 返回空 embedding（batch {i // limit + 1}）")  # 指出第几批
            all_embeddings.extend(embs)  # 追加到总结果
        return all_embeddings  # 完整向量列表

    async def _aget_query_embedding(self, query: str) -> List[float]:  # 异步查询向量（同步实现）
        return self._get_query_embedding(query)  # 复用同步路径

    async def _aget_text_embedding(self, text: str) -> List[float]:  # 异步文档向量（同步实现）
        return self._get_text_embedding(text)  # 复用同步路径
