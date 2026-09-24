# -*- coding: utf-8 -*-
"""四合一单体应用：一个端口、一个页面、四个功能模块。"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PLATFORM_ROOT = Path(__file__).resolve().parents[1]
if str(PLATFORM_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_ROOT))

from app.config import CHROMA_APP_ROOT, DEEPSEEK_API_KEY, HOST, LLM_MODEL, PORT  # noqa: E402
from app.routers import basic, content, rag, secure  # noqa: E402

STATIC_DIR = PLATFORM_ROOT / "static"
INDEX_HTML = STATIC_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 56)
    print("RAG 四合一综合平台（单体）启动中...")
    app.state.rag_engine = None
    if DEEPSEEK_API_KEY and CHROMA_APP_ROOT.is_dir():
        if str(CHROMA_APP_ROOT) not in sys.path:
            sys.path.insert(0, str(CHROMA_APP_ROOT))
        from semantic_search.app.engine import SemanticSearchEngine

        app.state.rag_engine = SemanticSearchEngine()
        total = app.state.rag_engine.seed_if_empty()
        print(f"RAG 引擎就绪，文档数: {total}")
    else:
        print("警告: RAG 引擎未启动（检查 DEEPSEEK_API_KEY 或 apps/chroma文档管理）")
    print(f"统一入口: http://{HOST}:{PORT}/")
    print("=" * 56)
    yield
    print("正在关闭四合一平台...")


app = FastAPI(
    title="RAG 四合一综合平台",
    description="基础聊天 + 安全聊天 + 文案生成 + 知识库RAG（单端口单体应用）",
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(basic.router)
app.include_router(secure.router)
app.include_router(content.router)
app.include_router(rag.router)


@app.get("/")
def index():
    if not INDEX_HTML.is_file():
        return {"error": "缺少 static/index.html"}
    return FileResponse(
        INDEX_HTML,
        headers={"Cache-Control": "no-store"},
    )


@app.get("/health")
def health():
    rag_ok = getattr(app.state, "rag_engine", None) is not None
    return {
        "status": "ok",
        "service": "rag-quad-monolith",
        "model": LLM_MODEL,
        "modules": ["basic", "secure", "content", "rag"],
        "rag_ready": rag_ok,
        "has_api_key": bool(DEEPSEEK_API_KEY),
    }


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
