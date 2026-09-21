"""语义搜索 / Native RAG API 的请求和响应模型。"""

from typing import List

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索查询文本", min_length=1)
    k: int = Field(5, description="返回结果数量", ge=1, le=100)


class DocumentResponse(BaseModel):
    rank: int
    index: int
    document: str
    similarity: float
    distance: float


class SearchResponse(BaseModel):
    query: str
    results: List[DocumentResponse]
    total: int


class AddDocumentsRequest(BaseModel):
    documents: List[str] = Field(..., description="要添加的文档列表", min_length=1)
    splitter: str = Field("sentence", description="切分方式: sentence / token / semantic")


class IngestRequest(BaseModel):
    input_dir: str | None = Field(None, description="要加载的目录，默认用 RAG_DATA_DIR")
    input_files: List[str] | None = Field(None, description="要加载的文件路径列表")
    splitter: str = Field("sentence", description="切分方式: sentence / token / semantic")


class QueryRequest(BaseModel):
    question: str = Field(..., description="用户问题", min_length=1)
    k: int = Field(5, description="检索条数", ge=1, le=100)


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[DocumentResponse] = Field(default_factory=list)


class ChatRequest(BaseModel):
    question: str = Field(..., description="用户问题", min_length=1)
    session_id: str = Field("default", description="会话 ID，相同 ID 会保留多轮记忆")
    k: int = Field(5, description="检索条数", ge=1, le=100)


class ChatResponse(BaseModel):
    session_id: str
    question: str
    answer: str
