"""Tavily 网页搜索：把外搜结果变成和知识库相同的 NodeWithScore。"""

from __future__ import annotations

import hashlib
from typing import Any

import requests
from llama_index.core.schema import NodeWithScore, TextNode

from semantic_search.app.config import TAVILY_API_KEY, TAVILY_MAX_RESULTS

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def tavily_configured() -> bool:
    return bool((TAVILY_API_KEY or "").strip())


def search_web(query: str, *, max_results: int | None = None) -> dict[str, Any]:
    """调用 Tavily Search；失败时不抛给用户整段 traceback。"""
    q = (query or "").strip()
    key = (TAVILY_API_KEY or "").strip()
    n = max(1, min(int(max_results or TAVILY_MAX_RESULTS or 5), 8))
    if not q:
        return {"ok": False, "message": "搜索词为空", "nodes": [], "results": []}
    if not key:
        return {
            "ok": False,
            "message": "未配置 TAVILY_API_KEY，无法联网搜索",
            "nodes": [],
            "results": [],
        }
    try:
        resp = requests.post(
            TAVILY_SEARCH_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "query": q,
                "max_results": n,
                "search_depth": "basic",
                "include_answer": False,
            },
            timeout=25,
        )
        if resp.status_code == 401:
            return {"ok": False, "message": "Tavily Key 无效或已过期", "nodes": [], "results": []}
        if resp.status_code == 432 or resp.status_code == 429:
            return {"ok": False, "message": "Tavily 额度用完或请求过快", "nodes": [], "results": []}
        resp.raise_for_status()
        payload = resp.json() if resp.content else {}
    except requests.RequestException as exc:
        return {"ok": False, "message": f"联网搜索失败：{exc}", "nodes": [], "results": []}

    raw = payload.get("results") or []
    nodes: list[NodeWithScore] = []
    cards: list[dict] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        title = str(item.get("title") or url or "网页").strip()
        content = str(item.get("content") or item.get("snippet") or "").strip()
        if not (url or content):
            continue
        score = item.get("score")
        try:
            sim = float(score)
        except (TypeError, ValueError):
            sim = max(0.2, 1.0 - i * 0.08)
        text = f"{title}\n{content}\n来源：{url}".strip()
        nid = hashlib.md5(url.encode("utf-8", errors="ignore")).hexdigest() if url else f"web-{i}"
        node = TextNode(
            text=text,
            id_=nid,
            metadata={
                "file_name": title[:120],
                "url": url,
                "source_kind": "web",
            },
        )
        nodes.append(NodeWithScore(node=node, score=sim))
        cards.append({"title": title, "url": url, "snippet": content[:240]})

    if not nodes:
        return {"ok": False, "message": "联网搜索没有返回可用结果", "nodes": [], "results": []}
    return {
        "ok": True,
        "message": f"联网搜索到 {len(nodes)} 条",
        "query": q,
        "nodes": nodes,
        "results": cards,
        "total": len(nodes),
    }
