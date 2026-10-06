"""Modular RAG 编排内核：上下文 + 模块协议 + 线性管线。

新优化只要实现 AskModule 并挂进 default_ask_pipeline()，不必改主编排循环。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from llama_index.core.schema import NodeWithScore


def empty_graph() -> dict:
    return {
        "enabled": False,
        "ok": False,
        "message": "skipped",
        "total": 0,
        "results": [],
    }


def empty_crag() -> dict:
    return {
        "enabled": False,
        "rewritten_query": None,
        "retried": False,
        "before_count": 0,
        "after_count": 0,
        "eval": [],
        "message": "skipped",
    }


def empty_self_rag() -> dict:
    return {
        "enabled": False,
        "retrieve": None,
        "skipped_retrieval": False,
        "isrel_shared_with_crag": False,
        "issup": None,
        "corrected": False,
        "isuse": None,
        "message": "skipped",
    }


def empty_eval() -> dict:
    return {
        "enabled": False,
        "faithfulness": None,
        "relevancy": None,
        "correctness": None,
        "diagnosis": None,
        "message": "skipped",
    }


def empty_pre(question: str, strategy: str) -> dict:
    return {
        "strategy": strategy,
        "original_query": question,
        "clean_query": question,
        "rewritten_query": None,
        "hyde_doc": None,
        "step_back_query": None,
        "retrieval_queries": [],
    }


def node_key(node: NodeWithScore) -> str:
    nid = getattr(node.node, "node_id", None) or getattr(node.node, "id_", None)
    if nid:
        return str(nid)
    return (node.node.get_content() or "")[:200]


def format_source(rank: int, item: NodeWithScore) -> dict:
    score = float(item.score or 0.0)
    return {
        "rank": rank,
        "index": rank - 1,
        "document": item.node.get_content(),
        "similarity": round(score, 4),
        "distance": (
            round(max(1.0 - score, 0.0), 4)
            if 0.0 <= score <= 1.0
            else round(1 / (1 + score), 4)
        ),
    }


def merge_nodes_rrf(
    ranked_lists: list[list[NodeWithScore]],
    k: int,
    rrf_k: int = 60,
) -> list[NodeWithScore]:
    scores: dict[str, float] = {}
    best: dict[str, NodeWithScore] = {}
    for nodes in ranked_lists:
        for rank, item in enumerate(nodes, start=1):
            key = node_key(item)
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)
            prev = best.get(key)
            if prev is None or float(item.score or 0.0) > float(prev.score or 0.0):
                best[key] = item
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    merged: list[NodeWithScore] = []
    for key, rrf_score in ordered[:k]:
        node = best[key]
        node.score = rrf_score
        merged.append(node)
    return merged


def context_from_nodes(nodes: list[NodeWithScore]) -> str:
    parts = []
    for i, item in enumerate(nodes, 1):
        text = (item.node.get_content() or "").strip()
        if text:
            parts.append(f"[{i}] {text}")
    return "\n\n".join(parts)


@dataclass
class AskContext:
    """一次 /ask 的共享状态，各 AskModule 只读写这里。"""

    engine: Any
    question: str
    k: int
    llm: Any
    graph_rag: Any = None
    reference: Optional[str] = None
    flags: dict = field(default_factory=dict)
    corpus_size: int = 0
    skip_retrieve: bool = False
    nodes: list = field(default_factory=list)
    answer: str = ""
    sources: list = field(default_factory=list)
    pre_retrieval: dict = field(default_factory=dict)
    crag: dict = field(default_factory=dict)
    self_rag: dict = field(default_factory=dict)
    graph: dict = field(default_factory=dict)
    generation_eval: dict = field(default_factory=dict)
    ran_modules: list[str] = field(default_factory=list)

    def to_response(self) -> dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "sources": self.sources,
            "pre_retrieval": self.pre_retrieval,
            "crag": self.crag,
            "self_rag": self.self_rag,
            "graph": self.graph,
            "generation_eval": self.generation_eval,
            "optimizations": {
                **self.flags,
                "ran_modules": list(self.ran_modules),
            },
        }


class AskModule(ABC):
    """可插拔算子：name + 类型 + 是否运行 + 执行。"""

    name: str = "module"
    module_type: str = "Retrieval"

    def should_run(self, ctx: AskContext) -> bool:
        return True

    @abstractmethod
    def run(self, ctx: AskContext) -> None:
        raise NotImplementedError


class AskPipeline:
    """按注册顺序跑模块；should_run 为假则跳过。"""

    def __init__(self, modules: list[AskModule]):
        self.modules = list(modules)

    def run(self, ctx: AskContext) -> AskContext:
        for mod in self.modules:
            if not mod.should_run(ctx):
                continue
            mod.run(ctx)
            ctx.ran_modules.append(mod.name)
        return ctx

    def describe(self) -> list[dict[str, str]]:
        return [
            {"name": m.name, "module_type": m.module_type}
            for m in self.modules
        ]
