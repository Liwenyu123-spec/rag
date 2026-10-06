"""把飞书讲义/复习笔记排除出检索库，避免示范问句抢走考勤制度。"""

from __future__ import annotations

import re
from pathlib import Path

_COURSE_NAME_RE = re.compile(
    r"(?:"
    r"^\d{2}[-_]"  # 00-Native / 02-提示词工程
    r"|RAG入门课"
    r"|详细复习笔记"
    r"|综合课件"
    r"|启动崩溃补丁"
    r"|面试题"
    r"|Modular-RAG"
    r"|GraphRAG"
    r"|Corrective-RAG"
    r"|Self-RAG"
    r"|多模态RAG"
    r"|项目对照"
    r")",
    re.IGNORECASE,
)

_COURSE_TEXT_RE = re.compile(
    r"(飞书文档：|CLEAR 原则|Prompt Engineering|本仓库 presets|"
    r"嗯那个帮我看看请假咋扣钱|加载器选择速查表|"
    r"检索前优化-Pre-retrieval|Native RAG基础)",
)

_KEEP_NAMES = {"kq.txt", "company_info.txt"}


def _source_blob(path: str | Path | None = None, metadata: dict | None = None) -> str:
    parts: list[str] = []
    if path:
        p = Path(str(path))
        parts.extend([p.name, str(p)])
    meta = metadata or {}
    for key in ("file_name", "filename", "file_path", "image_path"):
        val = meta.get(key)
        if val:
            parts.append(str(val))
            parts.append(Path(str(val)).name)
    return "\n".join(parts)


def is_course_note_path(path: str | Path) -> bool:
    name = Path(str(path)).name
    if name.lower() in _KEEP_NAMES:
        return False
    if name.lower() == "readme.md":
        return True
    return bool(_COURSE_NAME_RE.search(name))


def is_course_note(*, path: str | Path | None = None, metadata: dict | None = None, text: str = "") -> bool:
    blob = _source_blob(path, metadata)
    names = {Path(line.replace("\\", "/")).name.lower() for line in blob.splitlines() if line.strip()}
    if names & _KEEP_NAMES:
        return False
    if "readme.md" in names:
        return True
    if any(_COURSE_NAME_RE.search(name) for name in names):
        return True
    if blob and _COURSE_NAME_RE.search(blob):
        return True
    snippet = (text or "")[:1200]
    return bool(snippet and _COURSE_TEXT_RE.search(snippet))


def drop_course_note_nodes(nodes: list) -> list:
    kept = []
    for item in nodes:
        node = getattr(item, "node", item)
        meta = getattr(node, "metadata", None) or {}
        text = ""
        try:
            text = node.get_content() if hasattr(node, "get_content") else getattr(node, "text", "") or ""
        except Exception:
            text = str(getattr(node, "text", "") or "")
        if is_course_note(metadata=meta, text=text):
            continue
        kept.append(item)
    return kept
