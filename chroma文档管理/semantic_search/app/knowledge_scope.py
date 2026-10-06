"""知识库分类：文件后缀 + 制度/讲义，检索时按范围过滤。"""

from __future__ import annotations

import re
from pathlib import Path

_COURSE_NAME_RE = re.compile(
    r"(?:"
    r"^\d{2}[-_]"
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

SCOPE_OPTIONS = [
    ("business", "制度与业务"),
    ("course", "讲义课件"),
    ("all", "全部类型"),
    (".txt", "TXT"),
    (".pdf", "PDF"),
    (".md", "Markdown"),
    (".docx", "Word"),
    (".pptx", "PPT"),
    (".csv", "CSV"),
    (".html", "HTML"),
    (".ipynb", "Notebook"),
]

DEFAULT_SCOPE = "business"

_COURSE_QUERY_RE = re.compile(
    r"机器学习|深度学习|神经网络|支持向量机|决策树|随机森林|"
    r"KNN|k近邻|朴素贝叶斯|聚类|K-?Means|DBSCAN|PCA|"
    r"PyTorch|TensorFlow|BERT|Transformer|大模型|\bLLM\b|"
    r"\bRAG\b|检索增强|向量数据库|Embedding|嵌入向量|"
    r"Prompt|提示词|HyDE|GraphRAG|Self-RAG|CRAG|Modular|"
    r"课件|讲义|复习笔记",
    re.I,
)
_POLICY_QUERY_RE = re.compile(
    r"请假|扣钱|考勤|迟到|早退|加班|工资|打卡|入职|离职|"
    r"总部|贝壳|制度|社保|报销|出差",
    re.I,
)


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
    meta = metadata or {}
    if str(meta.get("doc_class") or "").lower() == "course":
        return True
    if str(meta.get("doc_class") or "").lower() in {"policy", "upload", "sample"}:
        return False
    blob = _source_blob(path, meta)
    names = {Path(line.replace("\\", "/")).name.lower() for line in blob.splitlines() if line.strip()}
    if names & _KEEP_NAMES:
        return False
    if "readme.md" in names:
        return True
    if any(_COURSE_NAME_RE.search(name) for name in names):
        return True
    snippet = (text or "")[:1200]
    return bool(snippet and _COURSE_TEXT_RE.search(snippet))


def infer_file_type(*, path: str | Path | None = None, metadata: dict | None = None) -> str:
    meta = metadata or {}
    raw = str(meta.get("file_type") or "").strip().lower()
    if raw.startswith(".") and len(raw) <= 8:
        return ".html" if raw == ".htm" else raw
    blob = _source_blob(path, meta)
    for line in blob.splitlines():
        suffix = Path(line.replace("\\", "/")).suffix.lower()
        if suffix:
            return ".html" if suffix == ".htm" else suffix
    return ".txt"


def classify_file(path: str | Path) -> dict[str, str]:
    p = Path(str(path))
    suffix = p.suffix.lower() or ".txt"
    if suffix == ".htm":
        suffix = ".html"
    name = p.name.lower()
    if name in _KEEP_NAMES:
        doc_class = "policy"
    elif is_course_note_path(p):
        doc_class = "course"
    else:
        doc_class = "upload"
    return {"file_type": suffix, "doc_class": doc_class}


def normalize_scope(scope: str | None) -> str:
    raw = (scope or DEFAULT_SCOPE).strip().lower() or DEFAULT_SCOPE
    aliases = {
        "policy": "business",
        "知识": "business",
        "制度": "business",
        "讲义": "course",
        "课件": "course",
        "*": "all",
        "any": "all",
        "md": ".md",
        "pdf": ".pdf",
        "txt": ".txt",
        "docx": ".docx",
        "pptx": ".pptx",
        "ppt": ".pptx",
        "csv": ".csv",
        "html": ".html",
        "htm": ".html",
        "ipynb": ".ipynb",
    }
    raw = aliases.get(raw, raw)
    if raw not in {"business", "course", "all"} and not raw.startswith("."):
        raw = "." + raw
    return raw


def resolve_query_scope(question: str, requested: str | None = None) -> tuple[str, str]:
    """默认「制度与业务」时，课件类问题自动改走讲义，避免库里有却检不到。"""
    want = normalize_scope(requested)
    text = question or ""
    if want != DEFAULT_SCOPE:
        return want, ""
    if _POLICY_QUERY_RE.search(text):
        return "business", ""
    if _COURSE_QUERY_RE.search(text):
        return "course", "问题更像课件内容，已自动检索「讲义课件」"
    return want, ""


def node_matches_scope(
    *,
    metadata: dict | None = None,
    text: str = "",
    path: str | Path | None = None,
    scope: str | None = None,
) -> bool:
    scope = normalize_scope(scope)
    meta = metadata or {}
    if scope == "all":
        return True
    if scope == "business":
        return not is_course_note(path=path, metadata=meta, text=text)
    if scope == "course":
        return is_course_note(path=path, metadata=meta, text=text)
    want = ".html" if scope == ".htm" else scope
    return infer_file_type(path=path, metadata=meta) == want


def filter_nodes_by_scope(nodes: list, scope: str | None = None) -> list:
    kept = []
    for item in nodes:
        node = getattr(item, "node", item)
        meta = getattr(node, "metadata", None) or {}
        text = ""
        try:
            text = node.get_content() if hasattr(node, "get_content") else getattr(node, "text", "") or ""
        except Exception:
            text = str(getattr(node, "text", "") or "")
        if node_matches_scope(metadata=meta, text=text, scope=scope):
            kept.append(item)
    return kept


def drop_course_note_nodes(nodes: list) -> list:
    return filter_nodes_by_scope(nodes, "business")
