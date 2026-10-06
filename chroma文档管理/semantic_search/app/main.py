"""Native RAG FastAPI 应用：生命周期、路由与启动入口。"""  # 模块说明：本文件负责启动 Web 服务并挂路由

from __future__ import annotations  # 允许类型注解里使用尚未定义的类名写法

import sys  # 操作系统相关：用来改 Python 模块搜索路径
from contextlib import asynccontextmanager  # 提供异步上下文管理器装饰器，给 lifespan 用
from pathlib import Path  # 用面向对象方式拼接文件路径

# 支持 IDE 直接运行本文件。包在 chroma文档管理/semantic_search/，需把「chroma文档管理」加入 path
_PACKAGE_PARENT = Path(__file__).resolve().parents[2]  # .../chroma文档管理（semantic_search 的父目录）
if str(_PACKAGE_PARENT) not in sys.path:  # 路径尚未加入时
    sys.path.insert(0, str(_PACKAGE_PARENT))  # 插到最前，保证能 import semantic_search

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile  # FastAPI 应用、上传、查询参数
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from semantic_search.app.config import (  # 从配置模块导入密钥、模型、主机端口等常量
    DASHSCOPE_API_KEY,  # 阿里云百炼 / 千问 API Key
    DATA_DIR,  # 知识库文件落盘目录
    DEEPSEEK_API_KEY,  # DeepSeek API Key（优先读 Windows 环境变量）
    EMBEDDING_MODEL,  # 向量化模型名，如 BAAI/bge-small-zh-v1.5
    EMBEDDING_PROVIDER,  # 向量化提供方：huggingface 或 dashscope
    GRAPH_RAG_ENABLED,  # GraphRAG 总开关
    HOST,  # 服务监听地址，默认 127.0.0.1
    IMAGE_EXTS,
    LLM_MODEL,  # 大模型名称，如 deepseek-v4-flash
    LLM_PROVIDER,  # 大模型提供方：deepseek 或 dashscope
    NEO4J_PASSWORD,  # Neo4j 密码
    PORT,  # 服务端口，默认 8003
    normalize_vector_backend,
)  # 括号结束
from semantic_search.app.engine import SUPPORTED_EXTS, SemanticSearchEngine  # 引擎 + 允许的文件扩展名
from semantic_search.app.service.mm_rag import is_image_path
from semantic_search.app.schemas import (  # Pydantic 请求/响应模型，给接口做校验和文档
    AddDocumentsRequest,  # 追加纯文本文档的请求体
    AskRequest,  # 可勾选优化方向的 RAG 问答请求体
    AskResponse,  # RAG 问答响应体（含 optimizations 回显）
    ChatRequest,  # 多轮对话请求体
    ChatResponse,  # 多轮对话响应体
    CragInfo,  # Corrective RAG 过程信息
    DocumentResponse,  # 单条检索结果（文档片段 + 相似度）
    GenerationEvalInfo,  # 生成质量评估
    GraphBuildRequest,  # GraphRAG 构建请求
    GraphInfo,  # 图谱通道过程
    GraphManualTripleRequest,  # 手工三元组
    GraphQueryRequest,  # GraphRAG 问答请求
    GraphRetrieveRequest,  # GraphRAG 仅检索请求
    IngestRequest,  # 从本地文件/目录导入的请求体
    OptimizeFlags,  # 本次实际生效的优化开关
    PreRetrievalInfo,  # 检索前优化中间信息
    RetrievalEvalBundle,  # 单套检索配置的评估汇总
    RetrievalEvalDelta,  # 基础 vs 当前的指标差
    RetrievalEvalFlags,  # 评估时实际检索开关
    RetrievalEvalItem,  # 单条检索评测结果
    RetrievalEvalRequest,  # 检索评测请求体
    RetrievalEvalResponse,  # 检索评测响应体
    SelfRagInfo,  # Self-RAG 过程信息
    QueryRequest,  # 一次性问答请求体
    QueryResponse,  # 一次性问答响应体（含来源）
    SearchRequest,  # 语义搜索请求体
    SearchResponse,  # 语义搜索响应体
)  # 括号结束
from semantic_search.app.modular_config import describe_module_graph, yaml_as_ask_defaults
from semantic_search.app.service.rag_service import RagAskService
from semantic_search.app.service.presets import PRESETS
from semantic_search.app.service.rag_eval import (
    DEFAULT_RETRIEVAL_CASES,
    compare_retrieval_runs,
    evaluate_retrieval_cases,
)
from semantic_search.app.routers import basic as basic_router
from semantic_search.app.routers import content as content_router
from semantic_search.app.routers import secure as secure_router

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"  # static 目录：放前端页面
INDEX_HTML = STATIC_DIR / "index.html"  # 前端入口 HTML 的完整路径


def _require_engine(app: FastAPI):  # 从 app 取出已初始化的搜索引擎
    engine = getattr(app.state, "search_engine", None)  # lifespan 里挂到 app.state 上的引擎实例
    if engine is None:  # 没初始化成功（常见原因：缺 API Key）
        raise HTTPException(  # 返回 HTTP 503 给调用方
            status_code=503,  # 服务暂时不可用
            detail="搜索引擎未初始化，请检查 Windows 环境变量 DEEPSEEK_API_KEY",  # 错误说明
        )  # 括号结束
    return engine  # 引擎可用，返回给路由函数继续用


def vector_backend_dep(
    request: Request,
    vector_backend: str | None = Query(None, description="chroma / qdrant"),
) -> str:
    return normalize_vector_backend(vector_backend or request.headers.get("x-vector-backend"))


def _bound_engine(app: FastAPI, backend: str):
    try:
        return _require_engine(app).bind(backend)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _try_init_graph_rag(app: FastAPI):
    """启动时或 Neo4j 后开时尝试连接图谱；失败不拖垮向量 RAG。"""
    existing = getattr(app.state, "graph_rag", None)
    if existing is not None:
        return existing
    if not GRAPH_RAG_ENABLED or not NEO4J_PASSWORD:
        return None
    if not (DEEPSEEK_API_KEY or DASHSCOPE_API_KEY):
        return None
    from semantic_search.app.service.graph_rag import GraphRagService, neo4j_bolt_reachable

    if not neo4j_bolt_reachable():
        app.state.graph_rag = None
        app.state.graph_rag_error = "Neo4j 未运行（Bolt 端口拒绝连接）。向量搜索不受影响。"
        if not getattr(app.state, "_logged_graph_skip", False):
            print("提示: Neo4j 未启动，已跳过 GraphRAG。搜索引擎可正常使用。")
            app.state._logged_graph_skip = True
        return None
    try:
        app.state.graph_rag = GraphRagService()
        app.state.graph_rag_error = None
        print("GraphRAG 已就绪（Neo4j + DeepSeek/千问可配）")
        return app.state.graph_rag
    except Exception as exc:  # noqa: BLE001
        app.state.graph_rag = None
        app.state.graph_rag_error = str(exc)
        print(f"警告: GraphRAG 初始化失败: {exc}")
        return None


def _require_graph_rag(app: FastAPI):
    service = _try_init_graph_rag(app)
    if service is None:
        extra = getattr(app.state, "graph_rag_error", None)
        raise HTTPException(
            status_code=503,
            detail=(
                "GraphRAG 未初始化。请先启动 Neo4j（neo4j console），配置 NEO4J_PASSWORD"
                " 与 DEEPSEEK_API_KEY。"
                + (f" 原因: {extra}" if extra else "")
            ),
        )
    return service


def _try_init_mm_rag(app: FastAPI):
    existing = getattr(app.state, "mm_rag", None)
    if existing is not None:
        return existing
    engine = getattr(app.state, "search_engine", None)
    if engine is None:
        return None
    try:
        from semantic_search.app.service.mm_rag import MultimodalRagService

        app.state.mm_rag = MultimodalRagService(engine)
        app.state.mm_rag_error = None
        seeded = app.state.mm_rag.ingest_data_dir()
        print(f"多模态 RAG 已就绪，图库 {seeded.get('total_images', 0)} 张")
        return app.state.mm_rag
    except Exception as exc:  # noqa: BLE001
        app.state.mm_rag = None
        app.state.mm_rag_error = str(exc)
        print(f"警告: 多模态 RAG 初始化失败: {exc}")
        return None


def _require_mm_rag(app: FastAPI):
    service = _try_init_mm_rag(app)
    if service is None:
        extra = getattr(app.state, "mm_rag_error", None)
        raise HTTPException(
            status_code=503,
            detail="多模态 RAG 未就绪，需要本地 Chinese-CLIP 权重。"
            + (f" 原因: {extra}" if extra else ""),
        )
    return service


@asynccontextmanager  # 把下面函数变成「启动时进入 / 关闭时退出」的生命周期钩子
async def lifespan(app: FastAPI):  # FastAPI 启动和关闭时都会走到这里
    print("=" * 50)  # 打印分隔线，方便在终端里辨认启动日志
    print("正在启动 RAG 四合一平台（当前搜索引擎 + 聊天/文案）...")

    llm_ready = (  # 判断当前配置下大模型密钥是否齐备
        (LLM_PROVIDER == "deepseek" and bool(DEEPSEEK_API_KEY))  # DeepSeek 模式需要 DEEPSEEK_API_KEY
        or (LLM_PROVIDER == "dashscope" and bool(DASHSCOPE_API_KEY))  # 千问模式需要 DASHSCOPE_API_KEY
    )  # 括号结束
    if llm_ready:  # 密钥齐了才真正创建引擎
        app.state.search_engine = SemanticSearchEngine()  # 初始化 Embedding、LLM、Chroma、索引
        total = app.state.search_engine.seed_if_empty()  # 库空时写入示例文档并加载 data 目录
        print(f"服务启动完成，当前文档数: {total}")  # 打印当前向量库文档数量
    else:  # 缺密钥：服务能起来，但检索/问答接口会 503
        app.state.search_engine = None  # 明确标记引擎不可用
        if LLM_PROVIDER == "deepseek":  # 按当前提供方打印对应提示
            print("错误: 未找到 DEEPSEEK_API_KEY（进程 / .env / Windows 用户环境变量）")  # DeepSeek 缺 Key
        else:  # 当前是 dashscope 提供方
            print("错误: 未找到 DASHSCOPE_API_KEY")  # 千问密钥缺失提示

    # GraphRAG：Neo4j 未开时稍后可在请求里重试连接
    app.state.graph_rag = None
    app.state.graph_rag_error = None
    _try_init_graph_rag(app)
    app.state.mm_rag = None
    app.state.mm_rag_error = None
    _try_init_mm_rag(app)

    print("=" * 50)  # 启动阶段结束分隔线
    yield  # 这里之后应用正式对外提供请求；yield 返回后进入关闭阶段
    print("正在关闭搜索引擎，清理资源...")  # 进程退出前打印清理提示


app = FastAPI(  # 创建 FastAPI 应用实例
    title="RAG 四合一平台",
    description="基础聊天 + 安全聊天 + 文案生成 + 知识库 RAG（LlamaIndex / DeepSeek / Chroma / 可选 GraphRAG）",
    version="3.0.0",
    lifespan=lifespan,
)
app.include_router(basic_router.router)
app.include_router(secure_router.router)
app.include_router(content_router.router)


@app.get("/")  # 浏览器访问根路径时走这个函数
async def root():  # 返回前端问答 / 搜索页面
    """返回前端问答 / 搜索页面。"""  # OpenAPI 文档里显示的接口说明
    if not INDEX_HTML.is_file():  # 前端文件不存在时避免返回空白错误
        raise HTTPException(status_code=404, detail="前端页面缺失：semantic_search/static/index.html")  # 404 提示缺文件
    return FileResponse(
        INDEX_HTML,
        media_type="text/html; charset=utf-8",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Content-Type": "text/html; charset=utf-8",
        },
    )


@app.get("/api")  # JSON 形式的服务入口说明（以前根路径返回的内容挪到这里）
async def api_info():  # 方便程序或调试查看有哪些入口
    """返回 API 基本信息和使用入口。"""  # OpenAPI 文档说明
    return {  # 返回一个字典，FastAPI 会自动转成 JSON
        "message": "RAG 四合一平台 API",
        "ui": "/",
        "docs": "/docs",
        "health": "/health",
        "basic_chat": "POST /api/basic/chat",
        "secure_chat": "GET /api/secure/stream_chat",
        "content": "POST /api/content/product_copy | social_plan | GET self_consistency",
        "search": "/search?q=你的查询内容",
        "query": "/query?q=根据知识库回答问题",
        "ask": "POST /ask",
        "modules": "GET /modules",
        "eval_retrieval": "POST /eval/retrieval",
        "chat": "POST /chat",
        "ingest": "POST /ingest",
        "graph_status": "GET /graph/status",
        "graph_build": "POST /graph/build",
        "graph_triple": "POST /graph/triple",
        "graph_load": "POST /graph/load",
        "graph_query": "POST /graph/query",
        "graph_retrieve": "POST /graph/retrieve",
        "mm_status": "GET /mm/status",
        "mm_search": "POST /mm/search",
        "mm_ask": "POST /mm/ask",
    }  # 字典/集合结束


@app.get("/modules")
async def list_modules():
    """Modular RAG 三层抽象 + 当前 AskPipeline 注册表。"""
    from semantic_search.app.service.ask_modules import default_ask_modules
    from semantic_search.app.service.pipeline import AskPipeline

    data = describe_module_graph(yaml_as_ask_defaults())
    data["pipeline"] = AskPipeline(default_ask_modules()).describe()
    return data


@app.post("/ask", response_model=AskResponse)  # 作业主接口：可勾选优化方向的 RAG 问答
async def ask(request: AskRequest, backend: str = Depends(vector_backend_dep)):  # 请求体含 question / k / 各优化开关
    """基础 RAG + ModularRAG 预设 / 勾选优化 + 可选生成评估。

    preset: basic / hybrid_search / advanced / full_optimization（对齐 demo01）
    显式开关会覆盖预设对应项。
    """  # OpenAPI 多行说明：预设与开关优先级
    strategy = (request.strategy or "").strip().lower() if request.strategy else None  # 规范化策略名；空则 None
    if strategy and strategy not in {"none", "clean", "rewrite", "hyde", "step_back"}:
        raise HTTPException(
            status_code=400,
            detail="strategy 只能是 none / clean / rewrite / hyde / step_back",
        )
    if request.preset and request.preset not in {
        "basic",
        "hybrid_search",
        "advanced",
        "full_optimization",
        "custom",
        "step_back",
        "graph_hybrid",
    }:
        raise HTTPException(
            status_code=400,
            detail="preset 只能是 basic / hybrid_search / advanced / full_optimization / custom / step_back / graph_hybrid",
        )
    try:  # 业务层可能抛 ValueError / RuntimeError
        want_graph = bool(request.use_graph) or request.preset == "graph_hybrid"
        payload = RagAskService(
            _bound_engine(app, backend),
            graph_rag=_try_init_graph_rag(app) if want_graph else getattr(app.state, "graph_rag", None),
        ).ask(  # 编排：检索前→检索→生成→可选评估
            request.question,  # 用户问题
            k=request.k,  # Top-K
            strategy=strategy,  # 检索前策略
            preset=request.preset,  # 一键预设
            use_pre=request.use_pre,  # 检索前总开关
            use_hybrid=request.use_hybrid,  # 混合检索
            fusion_mode=request.fusion_mode,  # 融合策略
            num_queries=request.num_queries,  # Multi-Query 数
            use_rerank=request.use_rerank,  # 重排
            use_compress=request.use_compress,  # 压缩
            use_reorder=request.use_reorder,  # 长上下文重排
            use_crag=request.use_crag,  # CRAG
            use_self_rag=request.use_self_rag,  # Self-RAG
            use_graph=request.use_graph,
            use_eval=request.use_eval,  # 生成评估
            reference=request.reference,  # 标准答案（Correctness）
        )  # ask 调用结束
    except ValueError as exc:  # 参数/策略非法
        raise HTTPException(status_code=400, detail=str(exc)) from exc  # 转成 400
    except RuntimeError as exc:  # 引擎/LLM 不可用
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # 转成 503

    opts = payload.get("optimizations")  # 实际生效的优化开关字典
    gen_eval = payload.get("generation_eval")  # 生成评估结果字典（可能为空）
    return AskResponse(  # 组装结构化响应
        question=payload["question"],  # 原问题
        answer=payload["answer"],  # 最终答案
        sources=[DocumentResponse(**item) for item in payload["sources"]],  # 引用来源列表
        pre_retrieval=PreRetrievalInfo(**payload["pre_retrieval"]),  # 检索前过程
        crag=CragInfo(**(payload.get("crag") or {})),  # CRAG 过程；缺省空字典
        self_rag=SelfRagInfo(**(payload.get("self_rag") or {})),  # Self-RAG 过程
        graph=GraphInfo(**(payload.get("graph") or {})),
        generation_eval=GenerationEvalInfo(**gen_eval) if gen_eval else None,  # 有评估才包装
        optimizations=OptimizeFlags(**opts) if opts else None,  # 有开关回显才包装
    )  # AskResponse 结束


@app.post("/eval/retrieval", response_model=RetrievalEvalResponse)  # 检索质量评估接口
async def eval_retrieval(request: RetrievalEvalRequest, backend: str = Depends(vector_backend_dep)):  # 请求体含 k / 开关 / cases
    """检索质量评估：Hit Rate / MRR / Precision@K / Recall@K。

    默认走与 /ask 相同的检索链（检索前、混合、后处理、可选 CRAG）。
    compare=true 时同时跑 basic 预设做 A/B。
    """
    engine = _bound_engine(app, backend)
    service = RagAskService(engine)
    cases = (
        [c.model_dump() for c in request.cases]
        if request.cases
        else list(DEFAULT_RETRIEVAL_CASES)
    )
    k = max(1, min(request.k, max(engine.collection.count(), 1)))
    strategy = (request.strategy or "none").strip().lower()
    if strategy and strategy not in {"none", "clean", "rewrite", "hyde", "step_back"}:
        raise HTTPException(status_code=400, detail="strategy 只能是 none / clean / rewrite / hyde / step_back")

    current_flags = {
        "use_pre": bool(request.use_pre) if request.use_pre is not None else False,
        "strategy": strategy if request.use_pre else "none",
        "use_hybrid": True if request.use_hybrid is None else bool(request.use_hybrid),
        "fusion_mode": (request.fusion_mode or "reciprocal_rerank").strip(),
        "num_queries": max(1, int(request.num_queries or 1)),
        "use_rerank": False if request.use_rerank is None else bool(request.use_rerank),
        "use_compress": False if request.use_compress is None else bool(request.use_compress),
        "use_reorder": False if request.use_reorder is None else bool(request.use_reorder),
        "use_crag": False if request.use_crag is None else bool(request.use_crag),
    }
    basic = PRESETS["basic"]
    baseline_flags = {
        "use_pre": bool(basic.get("use_pre", False)),
        "strategy": str(basic.get("strategy") or "none"),
        "use_hybrid": bool(basic.get("use_hybrid", True)),
        "fusion_mode": str(basic.get("fusion_mode") or "simple"),
        "num_queries": max(1, int(basic.get("num_queries") or 1)),
        "use_rerank": bool(basic.get("use_rerank", False)),
        "use_compress": bool(basic.get("use_compress", False)),
        "use_reorder": bool(basic.get("use_reorder", False)),
        "use_crag": bool(basic.get("use_crag", False)),
    }

    def _make_retrieve(flags: dict):
        def _retrieve(q: str):
            return service.retrieve_for_eval(q, k, **flags)

        return _retrieve

    def _bundle(label: str, payload: dict, flags: dict) -> RetrievalEvalBundle:
        return RetrievalEvalBundle(
            label=label,
            hit_rate=payload["hit_rate"],
            mrr=payload["mrr"],
            precision_at_k=payload.get("precision_at_k") or 0.0,
            recall_at_k=payload.get("recall_at_k") or 0.0,
            total=payload["total"],
            results=[RetrievalEvalItem(**r) for r in payload["results"]],
            diagnosis=payload.get("diagnosis"),
            flags=RetrievalEvalFlags(**flags),
        )

    current_payload = evaluate_retrieval_cases(
        cases, _make_retrieve(current_flags), flags=current_flags
    )
    current = _bundle("current", current_payload, current_flags)
    baseline = None
    delta = None
    if request.compare:
        baseline_payload = evaluate_retrieval_cases(
            cases, _make_retrieve(baseline_flags), flags=baseline_flags
        )
        baseline = _bundle("baseline", baseline_payload, baseline_flags)
        delta = RetrievalEvalDelta(**compare_retrieval_runs(baseline_payload, current_payload))

    return RetrievalEvalResponse(
        hit_rate=current.hit_rate,
        mrr=current.mrr,
        precision_at_k=current.precision_at_k,
        recall_at_k=current.recall_at_k,
        total=current.total,
        results=current.results,
        message=current_payload.get("message") or "ok",
        diagnosis=current.diagnosis,
        compared=bool(request.compare),
        current=current,
        baseline=baseline,
        delta=delta,
    )


@app.get("/search", response_model=SearchResponse)  # GET 语义搜索，响应按 SearchResponse 校验
async def search_get(  # 适合浏览器地址栏直接试
    q: str = Query(..., description="搜索查询", min_length=1),  # 必填查询词，至少 1 个字符
    k: int = Query(5, description="返回结果数量", ge=1, le=100),  # 返回条数，默认 5，范围 1~100
    backend: str = Depends(vector_backend_dep),
):  # 参数列表结束
    """GET 搜索，只检索相似文档，不调用大模型。"""  # OpenAPI 接口说明
    results = _bound_engine(app, backend).search(q, k)  # 调用引擎做向量检索
    return SearchResponse(  # 包装成统一响应结构
        query=q,  # 回显用户查询
        results=[DocumentResponse(**item) for item in results],  # 把每条 dict 转成 DocumentResponse
        total=len(results),  # 本次返回条数
    )  # 括号结束


@app.post("/search", response_model=SearchResponse)  # POST 语义搜索，适合前端 / 程序化调用
async def search_post(request: SearchRequest, backend: str = Depends(vector_backend_dep)):  # 请求体是 JSON：{"query":"...","k":5}
    """POST 搜索，适合程序化调用。"""  # OpenAPI 接口说明
    results = _bound_engine(app, backend).search(request.query, request.k)  # 用请求体里的参数检索
    return SearchResponse(  # 返回检索结果列表
        query=request.query,  # 回显查询文本
        results=[DocumentResponse(**item) for item in results],  # 结构化结果
        total=len(results),  # 结果数量
    )  # 括号结束


@app.get("/query", response_model=QueryResponse)  # GET 一次性 RAG 问答
async def query_get(  # 检索后交给大模型生成答案，并带来源
    q: str = Query(..., description="用户问题", min_length=1),  # 必填问题
    k: int = Query(5, description="检索条数", ge=1, le=100),  # 检索 Top-K
    backend: str = Depends(vector_backend_dep),
):  # 参数列表结束
    """一次性 RAG 问答：检索后交给大模型生成。"""  # OpenAPI 接口说明
    try:  # 引擎缺 LLM 时会抛 RuntimeError
        payload = _bound_engine(app, backend).query(q, k)  # 执行「检索 + 生成」
    except RuntimeError as exc:  # 捕获引擎层业务错误
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # 转成 503 给客户端
    return QueryResponse(  # 组装问答响应
        question=payload["question"],  # 原问题
        answer=payload["answer"],  # 模型生成的答案
        sources=[DocumentResponse(**item) for item in payload["sources"]],  # 引用的知识片段
    )  # 括号结束


@app.post("/query", response_model=QueryResponse)  # POST 一次性 RAG 问答
async def query_post(request: QueryRequest, backend: str = Depends(vector_backend_dep)):  # JSON 体：question + k
    """一次性 RAG 问答。"""  # OpenAPI 接口说明
    try:  # 引擎缺 LLM 时会抛 RuntimeError
        payload = _bound_engine(app, backend).query(request.question, request.k)  # 用请求体参数问答
    except RuntimeError as exc:  # 捕获引擎层业务错误
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # LLM 不可用时返回 503
    return QueryResponse(  # 返回问题、答案、来源
        question=payload["question"],  # 原问题
        answer=payload["answer"],  # 模型答案
        sources=[DocumentResponse(**item) for item in payload["sources"]],  # 引用来源
    )  # 括号结束


@app.post("/chat", response_model=ChatResponse)  # 多轮对话接口
async def chat(request: ChatRequest, backend: str = Depends(vector_backend_dep)):  # 相同 session_id 会共用记忆缓冲区
    """多轮 RAG 对话，相同 session_id 会保留记忆。"""  # OpenAPI 接口说明
    try:  # 引擎缺 LLM 时会抛 RuntimeError
        payload = _bound_engine(app, backend).chat(  # 调用带记忆的 chat_engine
            request.question,  # 本轮用户问题
            session_id=request.session_id,  # 会话 ID，前端可随机生成并保持不变
            k=request.k,  # 每轮检索条数
        )  # chat 调用结束
    except RuntimeError as exc:  # 捕获引擎层业务错误
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # 引擎未就绪
    return ChatResponse(**payload)  # payload 字段与 ChatResponse 对齐，直接展开


@app.post("/documents")  # 向向量库追加纯文本（不是读文件）
async def add_documents(request: AddDocumentsRequest, backend: str = Depends(vector_backend_dep)):  # documents 是字符串列表
    """向向量库追加纯文本文档。"""  # OpenAPI 接口说明
    engine = _bound_engine(app, backend)  # 拿到可用引擎
    engine.add_documents(request.documents, splitter=request.splitter)  # 切分后写入索引
    return {  # 返回操作结果摘要
        "message": f"成功添加 {len(request.documents)} 个文档",  # 本次提交的文档条数
        "total_documents": engine.collection.count(),  # 写入后集合总条数
    }  # 字典/集合结束


@app.post("/ingest")  # 对应讲义 SimpleDirectoryReader：从本地文件/目录导入
async def ingest_documents(request: IngestRequest, backend: str = Depends(vector_backend_dep)):  # 可传 input_files 或 input_dir
    """从本地目录或文件列表加载文档（SimpleDirectoryReader）。"""  # OpenAPI 接口说明
    engine = _bound_engine(app, backend)  # 确保引擎已初始化
    result = engine.ingest_files(  # 内部：SimpleDirectoryReader → 切分 → insert_nodes
        input_files=request.input_files,  # 指定文件列表时优先用这个
        input_dir=request.input_dir,  # 否则加载目录；都空则用默认 DATA_DIR
        splitter=request.splitter,  # sentence / token / semantic
    )  # ingest_files 结束
    return {"message": "文档加载并索引完成", **result}  # 合并 loaded_documents、nodes 等统计


@app.post("/upload")  # 前端上传文件：保存到 data 目录后写入向量库和/或 Neo4j
async def upload_documents(  # multipart：files + splitter + target
    files: list[UploadFile] = File(..., description="要导入的文件，可多选"),
    splitter: str = Form("sentence", description="切分方式: sentence / token / semantic"),
    target: str = Form("chroma", description="chroma / neo4j / both"),
    extractor: str = Form("simple", description="图谱抽取器：simple / schema"),
    backend: str = Depends(vector_backend_dep),
):
    """浏览器上传文件 → 落盘 → 写入 Chroma 和/或 Neo4j 图谱。"""
    target = (target or "chroma").strip().lower()
    if target not in {"chroma", "neo4j", "both"}:
        raise HTTPException(status_code=400, detail="target 只能是 chroma / neo4j / both")
    if not files:
        raise HTTPException(status_code=400, detail="请至少选择一个文件")
    if splitter not in {"sentence", "token", "semantic"}:
        raise HTTPException(status_code=400, detail="splitter 只能是 sentence / token / semantic")

    upload_dir = Path(DATA_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[str] = []
    image_paths: list[str] = []
    skipped: list[str] = []
    allowed = set(SUPPORTED_EXTS) | set(IMAGE_EXTS)
    for item in files:
        name = Path(item.filename or "upload.bin").name
        suffix = Path(name).suffix.lower()
        if suffix not in allowed:
            skipped.append(name)
            continue
        dest_dir = upload_dir / "images" if is_image_path(name) else upload_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        target_path = dest_dir / name
        content = await item.read()
        target_path.write_bytes(content)
        if is_image_path(name):
            image_paths.append(str(target_path.resolve()))
        else:
            saved_paths.append(str(target_path.resolve()))

    if not saved_paths and not image_paths:
        raise HTTPException(
            status_code=400,
            detail=(
                f"没有可导入的文件。支持: {', '.join(SUPPORTED_EXTS + list(IMAGE_EXTS))}；"
                f"已跳过: {skipped}"
            ),
        )

    payload: dict = {
        "saved_files": [Path(p).name for p in saved_paths],
        "saved_images": [Path(p).name for p in image_paths],
        "skipped_files": skipped,
        "splitter": splitter,
        "target": target,
    }
    parts: list[str] = []

    if image_paths:
        mm = _require_mm_rag(app)
        payload["multimodal"] = mm.ingest_paths(image_paths, backend=backend)
        parts.append(f"已写入图库 {payload['multimodal'].get('indexed', 0)} 张")

    if target in {"chroma", "both"} and saved_paths:
        engine = _bound_engine(app, backend)
        chroma_result = engine.ingest_files(input_files=saved_paths, splitter=splitter)
        payload.update(chroma_result)
        parts.append(f"已写入向量库（{backend}）")

    if target in {"neo4j", "both"} and saved_paths:
        graph = _require_graph_rag(app)
        graph_result = graph.build_from_files(saved_paths, extractor=extractor)
        payload["graph"] = graph_result
        parts.append("已写入 Neo4j 图谱")

    payload["message"] = "；".join(parts) or "上传完成"
    return payload


@app.get("/stats")  # 查看知识库与模型配置统计
async def get_stats():  # 统计接口
    """返回文档数量、模型与存储路径。"""  # 接口说明
    return _require_engine(app).get_stats()  # 直接返回引擎统计字典


@app.get("/graph/status")
async def graph_status():
    """GraphRAG / Neo4j 连通性与配置摘要。"""
    service = _try_init_graph_rag(app)
    if service is None:
        return {
            "ready": False,
            "message": getattr(app.state, "graph_rag_error", None)
            or "GraphRAG 未初始化（需 NEO4J_PASSWORD + DeepSeek/千问 Key + Neo4j）",
            "deepseek_configured": bool(DEEPSEEK_API_KEY),
            "dashscope_configured": bool(DASHSCOPE_API_KEY),
            "neo4j_password_configured": bool(NEO4J_PASSWORD),
        }
    return service.status()


@app.post("/graph/triple")
async def graph_add_triple(request: GraphManualTripleRequest):
    """手工写入一条三元组到 Neo4j，不走 LLM 抽取。"""
    try:
        return _require_graph_rag(app).add_manual_triple(
            request.subject,
            request.relation,
            request.object,
            subject_label=request.subject_label,
            object_label=request.object_label,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"写入三元组失败: {exc}") from exc


@app.post("/graph/build")
async def graph_build(request: GraphBuildRequest):
    """从文本抽取三元组写入 Neo4j（Simple / Schema 抽取器）。"""
    try:
        return _require_graph_rag(app).build_from_texts(
            request.texts, extractor=request.extractor
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"图谱构建失败: {exc}") from exc


@app.post("/graph/load")
async def graph_load():
    """从已有 Neo4j 图谱加载 PropertyGraphIndex。"""
    try:
        return _require_graph_rag(app).load_existing()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"加载图谱失败: {exc}") from exc


@app.post("/graph/query")
async def graph_query(request: GraphQueryRequest):
    """GraphRAG 自然语言问答。"""
    try:
        return _require_graph_rag(app).query(request.question, k=request.k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"GraphRAG 问答失败: {exc}") from exc


@app.post("/graph/retrieve")
async def graph_retrieve(request: GraphRetrieveRequest):
    """只检索图谱子图/节点，不生成答案。"""
    try:
        return _require_graph_rag(app).retrieve(request.question, k=request.k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"图谱检索失败: {exc}") from exc


@app.get("/mm/status")
async def mm_status():
    """多模态图库与视觉模型是否可用。"""
    service = _try_init_mm_rag(app)
    if service is None:
        return {
            "ready": False,
            "message": getattr(app.state, "mm_rag_error", None) or "多模态未初始化",
            "dashscope_configured": bool(DASHSCOPE_API_KEY),
        }
    return service.status()


@app.get("/mm/files/{name}")
async def mm_file(name: str):
    """预览图库中的图片。"""
    try:
        path = _require_mm_rag(app).resolve_image(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="图片不存在") from exc
    return FileResponse(path)


@app.post("/mm/search")
async def mm_search(
    query: str = Form(""),
    k: int = Form(5),
    image: UploadFile | None = File(None),
    backend: str = Depends(vector_backend_dep),
):
    """以文搜图或以上传图搜图（可选同时以图搜文）。"""
    mm = _require_mm_rag(app)
    query_image_path = None
    if image is not None and image.filename:
        content = await image.read()
        if content:
            query_image_path = str(mm.save_query_image(image.filename, content))
    if query_image_path:
        images = mm.search_images_by_image(query_image_path, k=k, backend=backend)
        texts = mm.search_texts_by_image(query_image_path, k=k, backend=backend)
        task = "image2image"
    elif (query or "").strip():
        images = mm.search_images_by_text(query.strip(), k=k, backend=backend)
        texts = []
        task = "text2image"
    else:
        raise HTTPException(status_code=400, detail="请输入查询文本或上传一张图片")
    return {
        "task": task,
        "query": query,
        "images": images,
        "texts": texts,
        "total": len(images),
        "sources": images + texts,
    }


@app.post("/mm/ask")
async def mm_ask(
    question: str = Form(""),
    k: int = Form(5),
    image: UploadFile | None = File(None),
    backend: str = Depends(vector_backend_dep),
):
    """多模态问答：CLIP 召回图片后，有千问 Key 则用 VL 看图作答。"""
    mm = _require_mm_rag(app)
    query_image_path = None
    if image is not None and image.filename:
        content = await image.read()
        if content:
            query_image_path = str(mm.save_query_image(image.filename, content))
    if not (question or "").strip() and not query_image_path:
        raise HTTPException(status_code=400, detail="请输入问题或上传图片")
    try:
        return mm.ask(question, query_image_path=query_image_path, k=k, backend=backend)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/health")  # 健康检查：前端侧栏会轮询这个接口
async def health_check():  # 健康检查接口
    """健康检查，用于确认服务与配置是否可用。"""  # 接口说明
    engine = getattr(app.state, "search_engine", None)  # 不强制抛错，方便前端显示状态
    graph = getattr(app.state, "graph_rag", None)  # 健康检查不重连 Neo4j，避免未启动时驱动重试刷屏
    mm = getattr(app.state, "mm_rag", None)
    if engine is None:  # 引擎没起来
        return {  # 返回 error 状态而不是抛异常
            "status": "error",  # 前端侧栏显示红点
            "message": "搜索引擎未初始化，请在 Windows 用户环境变量中配置 DEEPSEEK_API_KEY",
            "graph_rag_ready": graph is not None,
            "mm_ready": mm is not None,
            "modules": ["basic", "secure", "content", "rag"],
        }

    stats = engine.get_stats()  # 读取运行时统计
    mm_status_data = mm.status() if mm is not None else {"ready": False, "image_count": 0}
    return {  # 精简字段给前端展示
        "status": "ok",  # 一切正常
        "service": "rag-quad-platform",
        "modules": ["basic", "secure", "content", "rag"],
        "model": stats["model_name"],  # Embedding 模型名
        "llm_provider": stats["llm_provider"],  # LLM 提供方
        "llm_model": stats["llm_model"],  # LLM 模型名
        "total_documents": stats["total_documents"],  # 当前默认后端文档数
        "chroma_documents": stats.get("chroma_documents", 0),
        "qdrant_documents": stats.get("qdrant_documents", 0),
        "qdrant_ready": stats.get("qdrant_ready", False),
        "index_type": stats["index_type"],  # 索引类型说明
        "graph_rag_ready": graph is not None,
        "mm_ready": bool(mm_status_data.get("ready")),
        "image_count": mm_status_data.get("image_count", 0),
        "chroma_images": mm_status_data.get("chroma_images", 0),
        "qdrant_images": mm_status_data.get("qdrant_images", 0),
        "vl_ready": bool(mm_status_data.get("vl_ready")),
    }  # 字典/集合结束


@app.delete("/documents")  # 清空向量集合（危险操作，调试用）
async def clear_documents(backend: str = Depends(vector_backend_dep)):  # 清空接口
    """清空当前向量后端中的全部文档。"""  # 接口说明
    _bound_engine(app, backend).clear_documents()  # 删除集合内全部向量与文档
    return {"message": f"{backend} 中的文档已清空"}  # 确认清空成功


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":  # 只有直接运行本文件时才进入（python -m 也会走到 __main__.py）
    import uvicorn  # ASGI 服务器，用来真正监听端口

    print("=" * 50)  # 启动横幅分隔线
    print("RAG 四合一平台 - 聊天 / 文案 / 知识库 RAG")
    print("=" * 50)  # 横幅下部分隔线
    if DEEPSEEK_API_KEY:  # 启动前快速自检 Key 是否读到
        print("DeepSeek API Key 已从 Windows 环境读取")  # Key 已就绪
    else:  # 没读到 Key
        print("警告: 未找到 DEEPSEEK_API_KEY（进程 / .env / Windows 用户变量）")  # 没有 Key 也能启动，但问答不可用
    print(f"Embedding: {EMBEDDING_PROVIDER} / {EMBEDDING_MODEL}")  # 打印当前向量化配置
    print(f"LLM: {LLM_PROVIDER} / {LLM_MODEL}")  # 打印当前大模型配置
    print(f"前端页面: http://{HOST}:{PORT}/")  # 浏览器打开这个地址看 UI
    print(f"API文档: http://{HOST}:{PORT}/docs")  # Swagger 调试地址
    print(f"搜索示例: http://{HOST}:{PORT}/search?q=向量数据库")  # GET 搜索试玩链接
    print(f"问答示例: http://{HOST}:{PORT}/query?q=迟到怎么扣钱")  # GET 问答试玩链接
    print("=" * 50)  # 启动信息结束分隔线

    uvicorn.run(  # 启动 HTTP 服务（阻塞运行，直到 Ctrl+C）
        "semantic_search.app.main:app",  # 用导入字符串加载 app，避免重复创建
        host=HOST,  # 监听地址
        port=PORT,  # 监听端口
        reload=False,  # 关闭热重载，避免重复加载大模型
    )  # uvicorn.run 结束
