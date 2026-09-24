"""Native RAG FastAPI 应用：生命周期、路由与启动入口。"""  # 模块说明：本文件负责启动 Web 服务并挂路由

from __future__ import annotations  # 允许类型注解里使用尚未定义的类名写法

import sys  # 操作系统相关：用来改 Python 模块搜索路径
from contextlib import asynccontextmanager  # 提供异步上下文管理器装饰器，给 lifespan 用
from pathlib import Path  # 用面向对象方式拼接文件路径

# 支持 IDE 直接运行本文件。包在 chroma文档管理/semantic_search/，需把「chroma文档管理」加入 path
_PACKAGE_PARENT = Path(__file__).resolve().parents[2]  # .../chroma文档管理（semantic_search 的父目录）
if str(_PACKAGE_PARENT) not in sys.path:  # 路径尚未加入时
    sys.path.insert(0, str(_PACKAGE_PARENT))  # 插到最前，保证能 import semantic_search

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile  # FastAPI 应用、上传、查询参数
from fastapi.responses import FileResponse  # 直接把本地文件（前端 HTML）作为响应返回

from semantic_search.app.config import (  # 从配置模块导入密钥、模型、主机端口等常量
    DASHSCOPE_API_KEY,  # 阿里云百炼 / 千问 API Key
    DATA_DIR,  # 知识库文件落盘目录
    DEEPSEEK_API_KEY,  # DeepSeek API Key（优先读 Windows 环境变量）
    EMBEDDING_MODEL,  # 向量化模型名，如 BAAI/bge-small-zh-v1.5
    EMBEDDING_PROVIDER,  # 向量化提供方：huggingface 或 dashscope
    HOST,  # 服务监听地址，默认 127.0.0.1
    LLM_MODEL,  # 大模型名称，如 deepseek-v4-flash
    LLM_PROVIDER,  # 大模型提供方：deepseek 或 dashscope
    PORT,  # 服务端口，默认 8003
)
from semantic_search.app.engine import SUPPORTED_EXTS, SemanticSearchEngine  # 引擎 + 允许的文件扩展名
from semantic_search.app.schemas import (  # Pydantic 请求/响应模型，给接口做校验和文档
    AddDocumentsRequest,  # 追加纯文本文档的请求体
    AskRequest,  # 检索前优化 + RAG 问答请求体
    AskResponse,  # 检索前优化 + RAG 问答响应体
    ChatRequest,  # 多轮对话请求体
    ChatResponse,  # 多轮对话响应体
    DocumentResponse,  # 单条检索结果（文档片段 + 相似度）
    IngestRequest,  # 从本地文件/目录导入的请求体
    PreRetrievalInfo,  # 检索前优化中间信息
    QueryRequest,  # 一次性问答请求体
    QueryResponse,  # 一次性问答响应体（含来源）
    SearchRequest,  # 语义搜索请求体
    SearchResponse,  # 语义搜索响应体
)
from semantic_search.app.service import RagAskService  # 业务编排：pre-retrieval → 检索 → 生成

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"  # static 目录：放前端页面
INDEX_HTML = STATIC_DIR / "index.html"  # 前端入口 HTML 的完整路径


def _require_engine(app: FastAPI) -> SemanticSearchEngine:  # 从 app 取出已初始化的搜索引擎
    engine = getattr(app.state, "search_engine", None)  # lifespan 里挂到 app.state 上的引擎实例
    if engine is None:  # 没初始化成功（常见原因：缺 API Key）
        raise HTTPException(  # 返回 HTTP 503 给调用方
            status_code=503,  # 服务暂时不可用
            detail="搜索引擎未初始化，请检查 Windows 环境变量 DEEPSEEK_API_KEY",  # 错误说明
        )
    return engine  # 引擎可用，返回给路由函数继续用


@asynccontextmanager  # 把下面函数变成「启动时进入 / 关闭时退出」的生命周期钩子
async def lifespan(app: FastAPI):  # FastAPI 启动和关闭时都会走到这里
    print("=" * 50)  # 打印分隔线，方便在终端里辨认启动日志
    print("正在启动 Native RAG 语义搜索引擎...")  # 提示开始初始化

    llm_ready = (  # 判断当前配置下大模型密钥是否齐备
        (LLM_PROVIDER == "deepseek" and bool(DEEPSEEK_API_KEY))  # DeepSeek 模式需要 DEEPSEEK_API_KEY
        or (LLM_PROVIDER == "dashscope" and bool(DASHSCOPE_API_KEY))  # 千问模式需要 DASHSCOPE_API_KEY
    )
    if llm_ready:  # 密钥齐了才真正创建引擎
        app.state.search_engine = SemanticSearchEngine()  # 初始化 Embedding、LLM、Chroma、索引
        total = app.state.search_engine.seed_if_empty()  # 库空时写入示例文档并加载 data 目录
        print(f"服务启动完成，当前文档数: {total}")  # 打印当前向量库文档数量
    else:  # 缺密钥：服务能起来，但检索/问答接口会 503
        app.state.search_engine = None  # 明确标记引擎不可用
        if LLM_PROVIDER == "deepseek":  # 按当前提供方打印对应提示
            print("错误: 未找到 DEEPSEEK_API_KEY（进程 / .env / Windows 用户环境变量）")  # DeepSeek 缺 Key
        else:
            print("错误: 未找到 DASHSCOPE_API_KEY")  # 千问密钥缺失提示

    print("=" * 50)  # 启动阶段结束分隔线
    yield  # 这里之后应用正式对外提供请求；yield 返回后进入关闭阶段
    print("正在关闭搜索引擎，清理资源...")  # 进程退出前打印清理提示


app = FastAPI(  # 创建 FastAPI 应用实例
    title="Native RAG 语义搜索引擎",  # 出现在 /docs 顶部的标题
    description="LlamaIndex + DeepSeek + Chroma：基础 RAG + 检索前优化（清洗/重写/HyDE）",  # API 文档说明
    version="2.1.0",  # 接口版本号
    lifespan=lifespan,  # 绑定上面的启动/关闭钩子
)


@app.get("/")  # 浏览器访问根路径时走这个函数
async def root():  # 返回前端问答 / 搜索页面
    """返回前端问答 / 搜索页面。"""  # OpenAPI 文档里显示的接口说明
    if not INDEX_HTML.is_file():  # 前端文件不存在时避免返回空白错误
        raise HTTPException(status_code=404, detail="前端页面缺失：semantic_search/static/index.html")  # 404 提示缺文件
    return FileResponse(  # 把 index.html 返回给浏览器，并禁止缓存以免改样式不生效
        INDEX_HTML,  # 前端入口文件路径
        headers={  # 响应头：禁止浏览器缓存旧页面
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",  # HTTP/1.1 禁缓存
            "Pragma": "no-cache",  # 兼容旧代理
        },
    )


@app.get("/api")  # JSON 形式的服务入口说明（以前根路径返回的内容挪到这里）
async def api_info():  # 方便程序或调试查看有哪些入口
    """返回 API 基本信息和使用入口。"""
    return {  # 返回一个字典，FastAPI 会自动转成 JSON
        "message": "Native RAG 语义搜索引擎 API",  # 服务简介
        "ui": "/",  # 前端页面地址
        "docs": "/docs",  # Swagger 交互文档
        "health": "/health",  # 健康检查
        "search": "/search?q=你的查询内容",  # GET 搜索示例
        "query": "/query?q=根据知识库回答问题",  # GET 问答示例
        "ask": "POST /ask",  # 检索前优化 + RAG 最终答案（作业主接口）
        "chat": "POST /chat",  # 多轮对话接口
        "ingest": "POST /ingest",  # 本地文件导入接口
    }


@app.post("/ask", response_model=AskResponse)  # 作业主接口：提问 → 检索前优化 → 检索 → 生成
async def ask(request: AskRequest):  # 请求体含 question / k / strategy
    """基础 RAG + 检索前优化：返回知识库检索后模型生成的最终答案。  # OpenAPI 长说明

    strategy 可选：
    - none: 不做优化，原问题直接检索
    - clean: 仅查询清洗
    - rewrite: 清洗 + 查询重写（默认，双路检索）
    - hyde: 清洗 + HyDE 假想文档检索（双路，假想文不当引用）
    """  # docstring 结束
    strategy = (request.strategy or "rewrite").strip().lower()  # 默认 rewrite，统一小写
    if strategy not in {"none", "clean", "rewrite", "hyde"}:  # 非法策略直接 400
        raise HTTPException(  # 参数错误
            status_code=400,  # Bad Request
            detail="strategy 只能是 none / clean / rewrite / hyde",  # 提示合法取值
        )
    try:  # 业务异常转 HTTP 状态码
        payload = RagAskService(_require_engine(app)).ask(  # 编排层：优化→检索→生成
            request.question,  # 用户原问题
            k=request.k,  # Top-K
            strategy=strategy,  # 检索前策略
        )
    except ValueError as exc:  # 如空问题
        raise HTTPException(status_code=400, detail=str(exc)) from exc  # 转 400
    except RuntimeError as exc:  # 如缺 LLM
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # 转 503

    return AskResponse(  # 组装带 pre_retrieval 的完整响应
        question=payload["question"],  # 原问题
        answer=payload["answer"],  # 最终答案
        sources=[DocumentResponse(**item) for item in payload["sources"]],  # 真实引用来源
        pre_retrieval=PreRetrievalInfo(**payload["pre_retrieval"]),  # 检索前优化过程
    )


@app.get("/search", response_model=SearchResponse)  # GET 语义搜索，响应按 SearchResponse 校验
async def search_get(  # 适合浏览器地址栏直接试
    q: str = Query(..., description="搜索查询", min_length=1),  # 必填查询词，至少 1 个字符
    k: int = Query(5, description="返回结果数量", ge=1, le=100),  # 返回条数，默认 5，范围 1~100
):
    """GET 搜索，只检索相似文档，不调用大模型。"""
    results = _require_engine(app).search(q, k)  # 调用引擎做向量检索
    return SearchResponse(  # 包装成统一响应结构
        query=q,  # 回显用户查询
        results=[DocumentResponse(**item) for item in results],  # 把每条 dict 转成 DocumentResponse
        total=len(results),  # 本次返回条数
    )


@app.post("/search", response_model=SearchResponse)  # POST 语义搜索，适合前端 / 程序化调用
async def search_post(request: SearchRequest):  # 请求体是 JSON：{"query":"...","k":5}
    """POST 搜索，适合程序化调用。"""
    results = _require_engine(app).search(request.query, request.k)  # 用请求体里的参数检索
    return SearchResponse(  # 返回检索结果列表
        query=request.query,  # 回显查询文本
        results=[DocumentResponse(**item) for item in results],  # 结构化结果
        total=len(results),  # 结果数量
    )


@app.get("/query", response_model=QueryResponse)  # GET 一次性 RAG 问答
async def query_get(  # 检索后交给大模型生成答案，并带来源
    q: str = Query(..., description="用户问题", min_length=1),  # 必填问题
    k: int = Query(5, description="检索条数", ge=1, le=100),  # 检索 Top-K
):
    """一次性 RAG 问答：检索后交给大模型生成。"""
    try:  # 引擎缺 LLM 时会抛 RuntimeError
        payload = _require_engine(app).query(q, k)  # 执行「检索 + 生成」
    except RuntimeError as exc:  # 捕获引擎层业务错误
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # 转成 503 给客户端
    return QueryResponse(  # 组装问答响应
        question=payload["question"],  # 原问题
        answer=payload["answer"],  # 模型生成的答案
        sources=[DocumentResponse(**item) for item in payload["sources"]],  # 引用的知识片段
    )


@app.post("/query", response_model=QueryResponse)  # POST 一次性 RAG 问答
async def query_post(request: QueryRequest):  # JSON 体：question + k
    """一次性 RAG 问答。"""
    try:
        payload = _require_engine(app).query(request.question, request.k)  # 用请求体参数问答
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # LLM 不可用时返回 503
    return QueryResponse(  # 返回问题、答案、来源
        question=payload["question"],  # 原问题
        answer=payload["answer"],  # 模型答案
        sources=[DocumentResponse(**item) for item in payload["sources"]],  # 引用来源
    )


@app.post("/chat", response_model=ChatResponse)  # 多轮对话接口
async def chat(request: ChatRequest):  # 相同 session_id 会共用记忆缓冲区
    """多轮 RAG 对话，相同 session_id 会保留记忆。"""
    try:
        payload = _require_engine(app).chat(  # 调用带记忆的 chat_engine
            request.question,  # 本轮用户问题
            session_id=request.session_id,  # 会话 ID，前端可随机生成并保持不变
            k=request.k,  # 每轮检索条数
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc  # 引擎未就绪
    return ChatResponse(**payload)  # payload 字段与 ChatResponse 对齐，直接展开


@app.post("/documents")  # 向向量库追加纯文本（不是读文件）
async def add_documents(request: AddDocumentsRequest):  # documents 是字符串列表
    """向向量库追加纯文本文档。"""
    engine = _require_engine(app)  # 拿到可用引擎
    engine.add_documents(request.documents, splitter=request.splitter)  # 切分后写入索引
    return {  # 返回操作结果摘要
        "message": f"成功添加 {len(request.documents)} 个文档",  # 本次提交的文档条数
        "total_documents": engine.collection.count(),  # 写入后集合总条数
    }


@app.post("/ingest")  # 对应讲义 SimpleDirectoryReader：从本地文件/目录导入
async def ingest_documents(request: IngestRequest):  # 可传 input_files 或 input_dir
    """从本地目录或文件列表加载文档（SimpleDirectoryReader）。"""
    engine = _require_engine(app)  # 确保引擎已初始化
    result = engine.ingest_files(  # 内部：SimpleDirectoryReader → 切分 → insert_nodes
        input_files=request.input_files,  # 指定文件列表时优先用这个
        input_dir=request.input_dir,  # 否则加载目录；都空则用默认 DATA_DIR
        splitter=request.splitter,  # sentence / token / semantic
    )
    return {"message": "文档加载并索引完成", **result}  # 合并 loaded_documents、nodes 等统计


@app.post("/upload")  # 前端上传文件：保存到 data 目录后自动分块入库
async def upload_documents(  # multipart：files + splitter
    files: list[UploadFile] = File(..., description="要导入的文件，可多选"),  # 上传文件列表
    splitter: str = Form("sentence", description="切分方式: sentence / token / semantic"),  # 分块策略表单字段
):  # 函数签名结束
    """浏览器上传文件 → 落盘到 DATA_DIR → SimpleDirectoryReader 分块索引。"""  # 接口说明
    if not files:  # 一个文件都没选
        raise HTTPException(status_code=400, detail="请至少选择一个文件")  # 参数错误
    if splitter not in {"sentence", "token", "semantic"}:  # 限制合法分块模式
        raise HTTPException(status_code=400, detail="splitter 只能是 sentence / token / semantic")  # 非法策略

    upload_dir = Path(DATA_DIR)  # 与讲义 data 目录一致
    upload_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在

    saved_paths: list[str] = []  # 本次成功保存的绝对路径
    skipped: list[str] = []  # 扩展名不支持而跳过的文件名
    for item in files:  # 逐个处理上传文件
        name = Path(item.filename or "upload.bin").name  # 只用文件名，防止路径穿越
        suffix = Path(name).suffix.lower()  # 扩展名小写
        if suffix not in SUPPORTED_EXTS:  # 不在白名单则跳过
            skipped.append(name)  # 记录跳过的文件名
            continue  # 处理下一个上传文件
        target = upload_dir / name  # 落盘路径：semantic_search/data/xxx
        content = await item.read()  # 读上传内容
        target.write_bytes(content)  # 写入磁盘
        saved_paths.append(str(target.resolve()))  # 记录绝对路径给 ingest

    if not saved_paths:  # 全都跳过了
        raise HTTPException(  # 没有可入库文件
            status_code=400,  # Bad Request
            detail=f"没有可导入的文件。支持扩展名: {', '.join(SUPPORTED_EXTS)}；已跳过: {skipped}",  # 说明原因
        )

    engine = _require_engine(app)  # 拿到引擎
    result = engine.ingest_files(input_files=saved_paths, splitter=splitter)  # 加载→分块→向量化
    return {  # 上传结果摘要
        "message": "上传并索引完成",  # 操作说明
        "saved_files": [Path(p).name for p in saved_paths],  # 成功保存的文件名
        "skipped_files": skipped,  # 扩展名不支持而跳过的
        "splitter": splitter,  # 本次使用的分块策略
        **result,  # 合并 loaded_documents / nodes / total_documents
    }


@app.get("/stats")  # 查看知识库与模型配置统计
async def get_stats():  # 统计接口
    """返回文档数量、模型与存储路径。"""  # 接口说明
    return _require_engine(app).get_stats()  # 直接返回引擎统计字典


@app.get("/health")  # 健康检查：前端侧栏会轮询这个接口
async def health_check():  # 健康检查接口
    """健康检查，用于确认服务与配置是否可用。"""  # 接口说明
    engine = getattr(app.state, "search_engine", None)  # 不强制抛错，方便前端显示状态
    if engine is None:  # 引擎没起来
        return {  # 返回 error 状态而不是抛异常
            "status": "error",  # 前端侧栏显示红点
            "message": "搜索引擎未初始化，请在 Windows 用户环境变量中配置 DEEPSEEK_API_KEY",  # 缺 Key 提示
        }

    stats = engine.get_stats()  # 读取运行时统计
    return {  # 精简字段给前端展示
        "status": "ok",  # 一切正常
        "service": "native-rag-search-engine",  # 服务标识
        "model": stats["model_name"],  # Embedding 模型名
        "llm_provider": stats["llm_provider"],  # LLM 提供方
        "llm_model": stats["llm_model"],  # LLM 模型名
        "total_documents": stats["total_documents"],  # 向量库文档数
        "index_type": stats["index_type"],  # 索引类型说明
    }


@app.delete("/documents")  # 清空向量集合（危险操作，调试用）
async def clear_documents():  # 清空接口
    """清空集合中的全部文档。"""  # 接口说明
    _require_engine(app).clear_documents()  # 删除集合内全部向量与文档
    return {"message": "所有文档已清空"}  # 确认清空成功


if __name__ == "__main__":  # 只有直接运行本文件时才进入（python -m 也会走到 __main__.py）
    import uvicorn  # ASGI 服务器，用来真正监听端口

    print("=" * 50)  # 启动横幅分隔线
    print("Native RAG 语义搜索引擎 - LlamaIndex + DeepSeek + Chroma")  # 打印产品名
    print("=" * 50)
    if DEEPSEEK_API_KEY:  # 启动前快速自检 Key 是否读到
        print("DeepSeek API Key 已从 Windows 环境读取")
    else:
        print("警告: 未找到 DEEPSEEK_API_KEY（进程 / .env / Windows 用户变量）")  # 没有 Key 也能启动，但问答不可用
    print(f"Embedding: {EMBEDDING_PROVIDER} / {EMBEDDING_MODEL}")  # 打印当前向量化配置
    print(f"LLM: {LLM_PROVIDER} / {LLM_MODEL}")  # 打印当前大模型配置
    print(f"前端页面: http://{HOST}:{PORT}/")  # 浏览器打开这个地址看 UI
    print(f"API文档: http://{HOST}:{PORT}/docs")  # Swagger 调试地址
    print(f"搜索示例: http://{HOST}:{PORT}/search?q=向量数据库")  # GET 搜索试玩链接
    print(f"问答示例: http://{HOST}:{PORT}/query?q=迟到怎么扣钱")  # GET 问答试玩链接
    print("=" * 50)

    uvicorn.run(  # 启动 HTTP 服务（阻塞运行，直到 Ctrl+C）
        "semantic_search.app.main:app",  # 用导入字符串加载 app，避免重复创建
        host=HOST,  # 监听地址
        port=PORT,  # 监听端口
        reload=False,  # 关闭热重载，避免重复加载大模型
    )
