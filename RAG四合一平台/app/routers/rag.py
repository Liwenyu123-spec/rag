# -*- coding: utf-8 -*-
"""模块4：Chroma 文档管理 / Native RAG（复用 apps/chroma文档管理 副本引擎）。"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from app.config import CHROMA_APP_ROOT, DEEPSEEK_API_KEY

router = APIRouter(prefix="/api/rag", tags=["知识库RAG"])

if str(CHROMA_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(CHROMA_APP_ROOT))

from semantic_search.app.engine import SUPPORTED_EXTS, SemanticSearchEngine  # noqa: E402
from semantic_search.app.service import RagAskService  # noqa: E402


class SearchBody(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=100)


class QueryBody(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=100)


class AskBody(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=100)
    strategy: str = Field("rewrite")


class RagChatBody(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str = Field("platform")
    k: int = Field(5, ge=1, le=100)


def _engine(request: Request) -> SemanticSearchEngine:
    engine = getattr(request.app.state, "rag_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="RAG 引擎未初始化，请检查 DEEPSEEK_API_KEY")
    return engine


@router.get("/status")
def rag_status(request: Request):
    engine = getattr(request.app.state, "rag_engine", None)
    if engine is None:
        return {
            "status": "error",
            "message": "RAG 未初始化" if DEEPSEEK_API_KEY else "缺少 DEEPSEEK_API_KEY",
        }
    stats = engine.get_stats()
    return {
        "status": "ok",
        "total_documents": stats["total_documents"],
        "model": stats["model_name"],
        "llm_model": stats["llm_model"],
        "llm_provider": stats["llm_provider"],
    }


@router.post("/search")
def rag_search(request: Request, body: SearchBody):
    return {"query": body.query, "results": _engine(request).search(body.query, body.k)}


@router.post("/query")
def rag_query(request: Request, body: QueryBody):
    try:
        return _engine(request).query(body.question, body.k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/ask")
def rag_ask(request: Request, body: AskBody):
    strategy = (body.strategy or "rewrite").strip().lower()
    if strategy not in {"none", "clean", "rewrite", "hyde"}:
        raise HTTPException(status_code=400, detail="strategy 只能是 none/clean/rewrite/hyde")
    try:
        return RagAskService(_engine(request)).ask(body.question, k=body.k, strategy=strategy)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/chat")
def rag_chat(request: Request, body: RagChatBody):
    try:
        return _engine(request).chat(body.question, session_id=body.session_id, k=body.k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/upload")
async def rag_upload(
    request: Request,
    files: list[UploadFile] = File(...),
    splitter: str = Form("sentence"),
):
    if splitter not in {"sentence", "token", "semantic"}:
        raise HTTPException(status_code=400, detail="splitter 无效")
    from semantic_search.app.config import DATA_DIR

    upload_dir = Path(DATA_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved, skipped = [], []
    for item in files:
        name = Path(item.filename or "upload.bin").name
        if Path(name).suffix.lower() not in SUPPORTED_EXTS:
            skipped.append(name)
            continue
        target = upload_dir / name
        target.write_bytes(await item.read())
        saved.append(str(target.resolve()))
    if not saved:
        raise HTTPException(status_code=400, detail=f"无可用文件；跳过: {skipped}")
    result = _engine(request).ingest_files(input_files=saved, splitter=splitter)
    return {
        "message": "上传并索引完成",
        "saved_files": [Path(p).name for p in saved],
        "skipped_files": skipped,
        **result,
    }
