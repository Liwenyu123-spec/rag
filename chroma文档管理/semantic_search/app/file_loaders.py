"""对照讲义「加载器选择速查表」：按后缀接到专用 Reader。

图片仍走多模态 CLIP 图库（ImageReader 依赖本机 Tesseract，且与 CLIP 重复）。
"""

from __future__ import annotations

from typing import Any

SUPPORTED_EXTS = [
    ".txt",
    ".pdf",
    ".docx",
    ".pptx",
    ".csv",
    ".md",
    ".html",
    ".htm",
    ".ipynb",
]


def _try_reader(name: str, factory) -> Any | None:
    try:
        return factory()
    except Exception as exc:  # noqa: BLE001
        print(f"警告: {name} 不可用，将跳过或回退: {exc}")
        return None


def build_file_extractor() -> dict[str, Any]:
    """SimpleDirectoryReader(file_extractor=...) 用的后缀 → Reader。"""
    extractors: dict[str, Any] = {}
    labels: list[str] = []

    flat = _try_reader("FlatReader", lambda: _import_reader("FlatReader"))
    if flat is not None:
        extractors[".txt"] = flat
        labels.append(".txt→FlatReader")

    pdf = (
        _try_reader("PyMuPDFReader", lambda: _import_reader("PyMuPDFReader"))
        or _try_reader("UnstructuredReader", lambda: _import_reader("UnstructuredReader"))
        or _try_reader("PDFReader", lambda: _import_reader("PDFReader"))
    )
    if pdf is not None:
        extractors[".pdf"] = pdf
        labels.append(f".pdf→{type(pdf).__name__}")

    docx = _try_reader("DocxReader", lambda: _import_reader("DocxReader"))
    if docx is not None:
        extractors[".docx"] = docx
        labels.append(".docx→DocxReader")

    pptx = _try_reader("PptxReader", lambda: _import_reader("PptxReader"))
    if pptx is not None:
        extractors[".pptx"] = pptx
        labels.append(".pptx→PptxReader")

    csv = _try_reader("PandasCSVReader", lambda: _import_reader("PandasCSVReader"))
    if csv is not None:
        extractors[".csv"] = csv
        labels.append(".csv→PandasCSVReader")

    md = _try_reader("MarkdownReader", lambda: _import_reader("MarkdownReader"))
    if md is not None:
        extractors[".md"] = md
        labels.append(".md→MarkdownReader")

    html = _try_reader(
        "HTMLTagReader",
        lambda: _import_reader("HTMLTagReader", tag="body"),
    )
    if html is not None:
        extractors[".html"] = html
        extractors[".htm"] = html
        labels.append(".html→HTMLTagReader")

    ipynb = _try_reader("IPYNBReader", lambda: _import_reader("IPYNBReader"))
    if ipynb is not None:
        extractors[".ipynb"] = ipynb
        labels.append(".ipynb→IPYNBReader")

    print("文档加载器: " + (", ".join(labels) if labels else "SimpleDirectoryReader 默认"))
    return extractors


def _import_reader(name: str, **kwargs):
    from llama_index.readers.file import (
        DocxReader,
        FlatReader,
        HTMLTagReader,
        IPYNBReader,
        MarkdownReader,
        PandasCSVReader,
        PDFReader,
        PptxReader,
        PyMuPDFReader,
        UnstructuredReader,
    )

    cls = {
        "FlatReader": FlatReader,
        "PyMuPDFReader": PyMuPDFReader,
        "UnstructuredReader": UnstructuredReader,
        "PDFReader": PDFReader,
        "DocxReader": DocxReader,
        "PptxReader": PptxReader,
        "PandasCSVReader": PandasCSVReader,
        "MarkdownReader": MarkdownReader,
        "HTMLTagReader": HTMLTagReader,
        "IPYNBReader": IPYNBReader,
    }[name]
    return cls(**kwargs)


def make_directory_reader(*, input_files: list[str] | None = None, input_dir: str | None = None):
    from llama_index.core import SimpleDirectoryReader

    extractor = build_file_extractor()
    if input_files:
        return SimpleDirectoryReader(input_files=input_files, file_extractor=extractor)
    kwargs: dict[str, Any] = {
        "file_extractor": extractor,
        "required_exts": list(SUPPORTED_EXTS),
        "recursive": True,
    }
    if input_dir:
        kwargs["input_dir"] = input_dir
    return SimpleDirectoryReader(**kwargs)
