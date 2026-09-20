"""语义搜索 FastAPI 应用：生命周期、路由与启动入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from semantic_search.app.config import DASHSCOPE_API_KEY, EMBEDDING_MODEL, HOST, PORT
from semantic_search.app.engine import SemanticSearchEngine
from semantic_search.app.schemas import (
    AddDocumentsRequest,
    DocumentResponse,
    SearchRequest,
    SearchResponse,
)


def _require_engine(app: FastAPI) -> SemanticSearchEngine:
    engine = getattr(app.state, "search_engine", None)
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="搜索引擎未初始化，请检查 API Key 配置",
        )
    return engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("正在启动语义搜索引擎...")

    if DASHSCOPE_API_KEY:
        app.state.search_engine = SemanticSearchEngine(
            api_key=DASHSCOPE_API_KEY,
            model_name=EMBEDDING_MODEL,
        )
        total = app.state.search_engine.seed_if_empty()
        print(f"服务启动完成，当前文档数: {total}")
    else:
        app.state.search_engine = None
        print("错误: 搜索引擎初始化失败，请设置 DASHSCOPE_API_KEY")

    print("=" * 50)
    yield
    print("正在关闭搜索引擎，清理资源...")


app = FastAPI(
    title="语义搜索引擎 - 千问向量化版(Chroma)",
    description="使用阿里云千问向量模型和 Chroma 构建的语义搜索服务",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """返回 API 基本信息和使用入口。"""
    return {
        "message": "语义搜索引擎API",
        "docs": "/docs",
        "health": "/health",
        "search": "/search?q=你的查询内容",
    }


@app.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., description="搜索查询", min_length=1),
    k: int = Query(5, description="返回结果数量", ge=1, le=100),
):
    """GET 搜索，适合浏览器直接访问。"""
    results = _require_engine(app).search(q, k)
    return SearchResponse(
        query=q,
        results=[DocumentResponse(**item) for item in results],
        total=len(results),
    )


@app.post("/search", response_model=SearchResponse)
async def search_post(request: SearchRequest):
    """POST 搜索，适合程序化调用。"""
    results = _require_engine(app).search(request.query, request.k)
    return SearchResponse(
        query=request.query,
        results=[DocumentResponse(**item) for item in results],
        total=len(results),
    )


@app.post("/documents")
async def add_documents(request: AddDocumentsRequest):
    """向向量库追加文档。"""
    engine = _require_engine(app)
    engine.add_documents(request.documents)
    return {
        "message": f"成功添加 {len(request.documents)} 个文档",
        "total_documents": engine.collection.count(),
    }


@app.get("/stats")
async def get_stats():
    """返回文档数量、模型与存储路径。"""
    return _require_engine(app).get_stats()


@app.get("/health")
async def health_check():
    """健康检查，用于确认服务与配置是否可用。"""
    engine = getattr(app.state, "search_engine", None)
    if engine is None:
        return {
            "status": "error",
            "message": "搜索引擎未初始化，请配置 DASHSCOPE_API_KEY 环境变量",
        }

    stats = engine.get_stats()
    return {
        "status": "ok",
        "service": "semantic-search-engine",
        "model": stats["model_name"],
        "total_documents": stats["total_documents"],
        "index_type": stats["index_type"],
    }


@app.delete("/documents")
async def clear_documents():
    """清空集合中的全部文档。"""
    _require_engine(app).clear_documents()
    return {"message": "所有文档已清空"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("语义搜索引擎 - 千问向量化版(Chroma)")
    print("=" * 50)
    if DASHSCOPE_API_KEY:
        print("API Key 已配置")
    else:
        print("警告: 未设置 DASHSCOPE_API_KEY 环境变量")
    print(f"使用模型: {EMBEDDING_MODEL}")
    print(f"API文档: http://{HOST}:{PORT}/docs")
    print(f"搜索示例: http://{HOST}:{PORT}/search?q=向量数据库")
    print("=" * 50)

    uvicorn.run(
        "semantic_search.app.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )
