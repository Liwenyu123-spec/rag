"""对话历史落盘：供一键清空与查询。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock

from semantic_search.app.config import PACKAGE_DIR

HISTORY_PATH = PACKAGE_DIR / "chat_history.json"
_LOCK = Lock()
_MAX_SESSIONS = 80
_MAX_MSG = 80
_MAX_TEXT = 4000


def _empty() -> dict:
    return {"sessions": []}


def _load() -> dict:
    if not HISTORY_PATH.is_file():
        return _empty()
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("sessions"), list):
            return data
    except Exception:
        pass
    return _empty()


def _dump(data: dict) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _clip_messages(messages: list) -> list:
    cleaned = []
    for item in (messages or [])[-_MAX_MSG:]:
        if not isinstance(item, dict):
            continue
        sources = []
        for src in (item.get("sources") or [])[:5]:
            if not isinstance(src, dict):
                continue
            sources.append(
                {
                    "rank": src.get("rank"),
                    "similarity": src.get("similarity"),
                    "document": str(src.get("document") or "")[:400],
                }
            )
        cleaned.append(
            {
                "role": item.get("role") or "user",
                "content": str(item.get("content") or "")[:_MAX_TEXT],
                "imageUrl": item.get("imageUrl") or "",
                "sources": sources,
            }
        )
    return cleaned


def upsert_session(payload: dict) -> dict:
    sid = str(payload.get("id") or "").strip()
    if not sid:
        raise ValueError("缺少会话 id")
    record = {
        "id": sid,
        "title": str(payload.get("title") or "未命名对话")[:80],
        "mode": str(payload.get("mode") or "ask"),
        "updated_at": int(payload.get("updated_at") or time.time() * 1000),
        "messages": _clip_messages(payload.get("messages") or []),
    }
    with _LOCK:
        data = _load()
        sessions = [s for s in data["sessions"] if s.get("id") != sid]
        sessions.insert(0, record)
        data["sessions"] = sessions[:_MAX_SESSIONS]
        _dump(data)
    return {"ok": True, "id": sid, "turns": len(record["messages"])}


def list_sessions() -> dict:
    with _LOCK:
        data = _load()
    items = []
    for s in data["sessions"]:
        msgs = s.get("messages") or []
        items.append(
            {
                "id": s.get("id"),
                "title": s.get("title") or "未命名对话",
                "mode": s.get("mode") or "ask",
                "updated_at": s.get("updated_at") or 0,
                "turns": len(msgs),
                "preview": next((m.get("content") for m in msgs if m.get("role") == "user"), "")[:80],
            }
        )
    return {"sessions": items, "total": len(items)}


def get_session(session_id: str) -> dict | None:
    sid = str(session_id or "").strip()
    with _LOCK:
        data = _load()
    for s in data["sessions"]:
        if s.get("id") == sid:
            return s
    return None


def delete_session(session_id: str) -> bool:
    sid = str(session_id or "").strip()
    with _LOCK:
        data = _load()
        before = len(data["sessions"])
        data["sessions"] = [s for s in data["sessions"] if s.get("id") != sid]
        if len(data["sessions"]) == before:
            return False
        _dump(data)
    return True


def clear_all() -> int:
    with _LOCK:
        data = _load()
        n = len(data["sessions"])
        _dump(_empty())
    return n
