"""语义搜索 / Native RAG API 的请求和响应模型。"""  # 模块说明：给 FastAPI 做入参/出参校验

from typing import List  # 类型注解：列表

from pydantic import BaseModel, Field  # BaseModel 定义结构；Field 加约束和文档说明


class SearchRequest(BaseModel):  # POST /search 的请求体
    query: str = Field(..., description="搜索查询文本", min_length=1)  # 必填查询词，至少 1 字
    k: int = Field(5, description="返回结果数量", ge=1, le=100)  # Top-K，默认 5


class DocumentResponse(BaseModel):  # 单条检索命中结果
    rank: int  # 排名，从 1 开始
    index: int  # 列表下标，从 0 开始
    document: str  # 命中的文本片段
    similarity: float  # 相似度分数（越高越相关）
    distance: float  # 距离（越小越近，常由 1-similarity 近似）


class SearchResponse(BaseModel):  # /search 的响应体
    query: str  # 回显用户查询
    results: List[DocumentResponse]  # 命中列表
    total: int  # 本次返回条数


class AddDocumentsRequest(BaseModel):  # POST /documents：追加纯文本
    documents: List[str] = Field(..., description="要添加的文档列表", min_length=1)  # 至少一个字符串
    splitter: str = Field("sentence", description="切分方式: sentence / token / semantic")  # 分块策略


class IngestRequest(BaseModel):  # POST /ingest：SimpleDirectoryReader 导入本地文件
    input_dir: str | None = Field(None, description="要加载的目录，默认用 RAG_DATA_DIR")  # 目录路径，可空
    input_files: List[str] | None = Field(None, description="要加载的文件路径列表")  # 文件列表，可空
    splitter: str = Field("sentence", description="切分方式: sentence / token / semantic")  # 分块策略


class QueryRequest(BaseModel):  # POST /query：一次性 RAG 问答
    question: str = Field(..., description="用户问题", min_length=1)  # 必填问题
    k: int = Field(5, description="检索条数", ge=1, le=100)  # 检索 Top-K


class QueryResponse(BaseModel):  # /query 的响应体
    question: str  # 原问题
    answer: str  # 大模型生成的答案
    sources: List[DocumentResponse] = Field(default_factory=list)  # 引用来源，默认空列表


class ChatRequest(BaseModel):  # POST /chat：多轮对话
    question: str = Field(..., description="用户问题", min_length=1)  # 本轮问题
    session_id: str = Field("default", description="会话 ID，相同 ID 会保留多轮记忆")  # 会话标识
    k: int = Field(5, description="检索条数", ge=1, le=100)  # 每轮检索条数


class ChatResponse(BaseModel):  # /chat 的响应体
    session_id: str  # 回显会话 ID
    question: str  # 本轮问题
    answer: str  # 本轮回答


class PreRetrievalInfo(BaseModel):  # 检索前优化中间产物（便于作业演示）
    strategy: str  # none / clean / rewrite / hyde
    original_query: str  # 用户原问题
    clean_query: str  # 清洗后
    rewritten_query: str | None = None  # 重写句（rewrite 策略）
    hyde_doc: str | None = None  # 假想文档（hyde 策略，仅用于检索）
    retrieval_queries: List[str] = Field(default_factory=list)  # 实际用于检索的查询列表


class AskRequest(BaseModel):  # POST /ask：基础 RAG + 检索前优化
    question: str = Field(..., description="用户问题", min_length=1)  # 必填用户问题
    k: int = Field(5, description="检索条数", ge=1, le=100)  # 最终返回来源条数
    strategy: str = Field(  # 检索前策略名
        "rewrite",  # 默认：清洗 + 重写双路检索
        description="检索前策略: none / clean / rewrite / hyde",  # OpenAPI 说明
    )  # 策略字段结束


class AskResponse(BaseModel):  # /ask 的响应体
    question: str  # 原问题
    answer: str  # 检索后由模型生成的最终答案
    sources: List[DocumentResponse] = Field(default_factory=list)  # 真实知识库引用来源
    pre_retrieval: PreRetrievalInfo  # 检索前优化过程信息
