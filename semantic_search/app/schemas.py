"""语义搜索 API 的请求和响应模型。"""

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
