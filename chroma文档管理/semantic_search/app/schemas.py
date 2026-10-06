"""语义搜索 / Native RAG API 的请求和响应模型。"""  # 模块说明：给 FastAPI 做入参/出参校验

from typing import List  # 类型注解：列表

from pydantic import BaseModel, Field  # BaseModel 定义结构；Field 加约束和文档说明


class SearchRequest(BaseModel):  # POST /search 的请求体
    query: str = Field(..., description="搜索查询文本", min_length=1)  # 必填查询词，至少 1 字
    k: int = Field(5, description="返回结果数量", ge=1, le=100)  # Top-K，默认 5
    doc_scope: str | None = Field(
        "business",
        description="检索范围: business / course / all / .txt / .pdf / .md / .docx / .pptx",
    )


class DocumentResponse(BaseModel):  # 单条检索命中结果
    rank: int  # 排名，从 1 开始
    index: int  # 列表下标，从 0 开始
    document: str  # 来源文件名（不再回传路径和元数据）
    similarity: float  # 相似度分数（越高越相关）
    distance: float  # 距离（越小越近，常由 1-similarity 近似）
    file_name: str = ""  # 与 document 相同，便于前端展示


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
    doc_scope: str | None = Field("business", description="检索范围，同 /ask")


class QueryResponse(BaseModel):  # /query 的响应体
    question: str  # 原问题
    answer: str  # 大模型生成的答案
    sources: List[DocumentResponse] = Field(default_factory=list)  # 引用来源，默认空列表


class ChatRequest(BaseModel):  # POST /chat：多轮对话
    question: str = Field(..., description="用户问题", min_length=1)  # 本轮问题
    session_id: str = Field("default", description="会话 ID，相同 ID 会保留多轮记忆")  # 会话标识
    k: int = Field(5, description="检索条数", ge=1, le=100)  # 每轮检索条数
    doc_scope: str | None = Field("business", description="检索范围，同 /ask")


class ChatResponse(BaseModel):  # /chat 的响应体
    session_id: str  # 回显会话 ID
    question: str  # 本轮问题
    answer: str  # 本轮回答


class ConversationTurn(BaseModel):
    role: str = "user"
    content: str = ""
    imageUrl: str = ""
    sources: List[dict] = Field(default_factory=list)


class ConversationSaveRequest(BaseModel):
    id: str = Field(..., min_length=1, description="会话 ID")
    title: str | None = None
    mode: str | None = "ask"
    updated_at: int | None = None
    messages: List[ConversationTurn] = Field(default_factory=list)


class PreRetrievalInfo(BaseModel):  # 检索前优化中间产物（便于作业演示）
    strategy: str  # none / clean / rewrite / hyde / step_back
    original_query: str  # 用户原问题
    clean_query: str  # 清洗后
    rewritten_query: str | None = None  # 重写句（rewrite 策略）
    hyde_doc: str | None = None  # 假想文档（hyde 策略，仅用于检索）
    step_back_query: str | None = None  # Step-Back 上位问题（step_back 策略）
    retrieval_queries: List[str] = Field(default_factory=list)  # 实际用于检索的查询列表


class CragInfo(BaseModel):  # Corrective RAG 过程信息
    enabled: bool = False  # 是否启用了 CRAG
    rewritten_query: str | None = None  # 全无关时的改写句
    retried: bool = False  # 是否触发了改写重检索
    before_count: int = 0  # 过滤前篇数
    after_count: int = 0  # 过滤后篇数
    eval: List[dict] = Field(default_factory=list)  # 每篇相关/无关明细
    message: str = "skipped"  # filtered / rewrote_and_filtered / ...


class AskRequest(BaseModel):  # POST /ask：基础 RAG + 可选优化链路
    question: str = Field(..., description="用户问题", min_length=1)  # 必填用户问题
    k: int = Field(5, description="检索条数", ge=1, le=100)  # 最终返回来源条数
    doc_scope: str | None = Field(
        "business",
        description="检索范围: business=制度与业务 / course=讲义 / all=全部 / .txt .pdf .md .docx .pptx",
    )
    # ----- ModularRAG 风格预设（basic / hybrid_search / advanced / full_optimization）-----
    preset: str | None = Field(  # 一键预设名，可空
        None,  # 默认不指定预设
        description="一键预设；与下方开关同时传时，显式开关优先覆盖预设",  # OpenAPI 字段说明
    )  # preset 字段结束
    # ----- 检索前 -----
    use_pre: bool | None = Field(None, description="是否启用检索前优化；null 跟预设/.env")  # 检索前总开关
    strategy: str | None = Field(  # 检索前策略名
        None,  # 默认跟预设或 .env
        description="检索前策略: none / clean / rewrite / hyde / step_back",  # OpenAPI 字段说明
    )  # strategy 字段结束
    # ----- 检索中 / 检索后 / CRAG（勾选开关；None 表示跟从预设或 .env）-----
    use_hybrid: bool | None = Field(None, description="混合检索 向量+BM25；null=跟配置")  # 混合检索开关
    fusion_mode: str | None = Field(  # 多路融合策略
        None,  # 默认跟配置
        description="融合策略: reciprocal_rerank / relative_score / simple",  # OpenAPI 字段说明
    )  # fusion_mode 字段结束
    num_queries: int | None = Field(  # Multi-Query 变体数量
        None,  # 默认跟配置
        ge=1,  # 至少 1
        le=8,  # 最多 8
        description="Multi-Query 变体数；1=不做查询扩展，>1=LLM 生成多查询（对齐 ModularRAG）",  # OpenAPI 字段说明
    )  # num_queries 字段结束
    use_rerank: bool | None = Field(None, description="重排序；null=跟配置")  # 重排开关
    use_compress: bool | None = Field(None, description="上下文压缩；null=跟配置")  # 压缩开关
    use_reorder: bool | None = Field(None, description="长上下文重排；null=跟配置")  # 长上下文重排开关
    use_crag: bool | None = Field(None, description="Corrective RAG；null=跟配置")  # CRAG 开关
    use_self_rag: bool | None = Field(  # Self-RAG 开关
        None,  # 默认跟配置
        description="Self-RAG：Retrieve 门控 + ISSUP 验据修正 + ISUSE；null=跟配置",  # OpenAPI 字段说明
    )  # use_self_rag 字段结束
    use_graph: bool | None = Field(
        None,
        description="知识图谱双通道：Neo4j 子图召回后与向量结果拼接；null=跟配置",
    )
    # ----- RAG 评估（飞书：生成质量）-----
    use_eval: bool | None = Field(  # 是否做生成质量评估
        False,  # 默认关闭评估
        description="是否对本次回答做 Faithfulness/Relevancy（+可选 Correctness）评估",  # OpenAPI 字段说明
    )  # use_eval 字段结束
    compare_baseline: bool | None = Field(
        True,
        description="同时跑一遍基础 RAG（关闭检索前/后优化），对照查询、召回与答案差别",
    )
    reference: str | None = Field(  # 标准答案（算 Correctness 用）
        None,  # 默认不提供
        description="标准答案；提供时额外算 Correctness（1~5）",  # OpenAPI 字段说明
    )  # reference 字段结束


class OptimizeFlags(BaseModel):  # 本次实际生效的优化开关（回显给前端）
    preset: str | None = None  # 实际采用的预设名
    use_pre: bool = True  # 是否启用了检索前优化
    strategy: str = "rewrite"  # 实际检索前策略
    use_hybrid: bool = True  # 是否混合检索
    fusion_mode: str = "reciprocal_rerank"  # 实际融合策略
    num_queries: int = 1  # 实际 Multi-Query 数
    use_rerank: bool = True  # 是否重排
    use_compress: bool = True  # 是否上下文压缩
    use_reorder: bool = True  # 是否长上下文重排
    use_crag: bool = True  # 是否 Corrective RAG
    use_self_rag: bool = False  # 是否 Self-RAG
    use_graph: bool = False  # 是否向量+图谱双通道
    use_eval: bool = False  # 是否做了生成评估
    doc_scope: str = "business"
    scope_note: str = ""
    ran_modules: List[str] = Field(default_factory=list)  # 本次实际跑过的管线模块名


class SelfRagInfo(BaseModel):  # Self-RAG 过程信息（作业演示）
    enabled: bool = False  # 是否启用了 Self-RAG
    retrieve: bool | None = None  # True=需要检索；False=直接答；None=未跑
    skipped_retrieval: bool = False  # 是否跳过了检索
    isrel_shared_with_crag: bool = False  # 是否复用了 CRAG 的相关判定
    issup: str | None = None  # FULLY / PARTIALLY / NO
    corrected: bool = False  # 是否做了验据修正
    isuse: int | None = None  # 1~5
    message: str = "skipped"  # 过程摘要文案


class MetricScore(BaseModel):  # 单项评估分数结构
    passing: bool | None = None  # 是否通过阈值
    score: float | None = None  # 数值分数
    feedback: str | None = None  # 评估反馈文本


class GenerationEvalInfo(BaseModel):  # 生成质量评估汇总
    enabled: bool = False  # 是否跑了生成评估
    faithfulness: MetricScore | None = None  # 忠实度（是否胡编）
    relevancy: MetricScore | None = None  # 相关性（是否答非所问）
    correctness: MetricScore | None = None  # 正确性（相对标准答案）
    diagnosis: str | None = None  # 简短诊断结论
    message: str = "skipped"  # 过程摘要文案


class GraphInfo(BaseModel):  # 图谱通道过程信息
    enabled: bool = False
    ok: bool = False
    message: str = "skipped"
    total: int = 0
    results: List[dict] = Field(default_factory=list)


class AskResponse(BaseModel):  # /ask 的响应体
    question: str  # 原问题
    answer: str  # 最终自然语言答案
    sources: List[DocumentResponse] = Field(default_factory=list)  # 真实知识库引用来源
    pre_retrieval: PreRetrievalInfo  # 检索前优化过程信息
    crag: CragInfo | None = None  # Corrective RAG 过程（可选）
    self_rag: SelfRagInfo | None = None  # Self-RAG 过程（可选）
    graph: GraphInfo | None = None  # 知识图谱通道
    generation_eval: GenerationEvalInfo | None = None  # 生成质量评估
    optimizations: OptimizeFlags | None = None  # 本次实际开启的优化项
    comparison: dict | None = None  # 优化前基础 RAG vs 当前优化对照


class RetrievalEvalCase(BaseModel):  # 单条检索评测样例
    query: str = Field(..., min_length=1)  # 评测查询，至少 1 字
    keywords: List[str] = Field(default_factory=list, description="命中判定关键词")  # 命中判定用关键词
    reference: str | None = Field(None, description="标准答案片段；无 expected_texts 时作召回标注")
    expected_texts: List[str] = Field(default_factory=list, description="应出现在召回中的黄金片段")
    expected_ids: List[str] = Field(default_factory=list, description="相关节点 ID（优先于关键词）")


class RetrievalEvalRequest(BaseModel):  # POST /eval/retrieval 请求体
    k: int = Field(5, ge=1, le=100)  # 检索 Top-K
    compare: bool = Field(True, description="是否同时跑基础 RAG 做 A/B")
    use_pre: bool | None = Field(None, description="当前配置：检索前优化")
    strategy: str | None = Field(None, description="当前配置：none / clean / rewrite / hyde / step_back")
    use_hybrid: bool | None = Field(True, description="是否混合检索")  # 混合检索开关
    fusion_mode: str | None = Field(None, description="融合策略")
    num_queries: int | None = Field(None, ge=1, le=8, description="Multi-Query 变体数")
    use_rerank: bool | None = Field(False, description="是否重排")  # 重排开关
    use_compress: bool | None = Field(False)  # 压缩开关，默认关
    use_reorder: bool | None = Field(False)  # 长上下文重排开关，默认关
    use_crag: bool | None = Field(False, description="是否走 CRAG（评估会变慢）")
    cases: List[RetrievalEvalCase] | None = Field(  # 自定义评测集
        None,  # 为空则用默认集
        description="自定义评测集；为空则用 company_info 默认集",  # OpenAPI 字段说明
    )  # cases 字段结束


class RetrievalEvalItem(BaseModel):  # 单条检索评测结果
    query: str  # 本条查询
    hit: bool  # 是否命中（关键词出现在检索结果中）
    mrr: float  # 本条 Mean Reciprocal Rank
    precision: float = 0.0  # 本条 Precision@K
    recall: float = 0.0  # 本条 Recall@K
    first_hit_rank: int | None = None  # 第一个相关文档排名
    relevant_in_k: int = 0  # Top-K 中相关篇数
    retrieved_preview: List[str] = Field(default_factory=list)  # 检索结果预览片段
    error: str | None = None  # 本条评测出错信息


class RetrievalEvalFlags(BaseModel):
    use_pre: bool = False
    strategy: str = "none"
    use_hybrid: bool = True
    fusion_mode: str = "simple"
    num_queries: int = 1
    use_rerank: bool = False
    use_compress: bool = False
    use_reorder: bool = False
    use_crag: bool = False


class RetrievalEvalBundle(BaseModel):
    label: str = "current"
    hit_rate: float
    mrr: float
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    total: int
    results: List[RetrievalEvalItem] = Field(default_factory=list)
    diagnosis: str | None = None
    flags: RetrievalEvalFlags | None = None


class RetrievalEvalDelta(BaseModel):
    hit_rate: float = 0.0
    mrr: float = 0.0
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0


class RetrievalEvalResponse(BaseModel):  # /eval/retrieval 响应体
    hit_rate: float  # 当前配置整体命中率（兼容旧前端）
    mrr: float  # 当前配置整体 MRR
    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    total: int  # 评测样例总数
    results: List[RetrievalEvalItem] = Field(default_factory=list)  # 当前配置逐条明细
    message: str = "ok"  # 状态文案
    diagnosis: str | None = None  # 简短诊断（检索瓶颈提示）
    note: str = "当前配置 vs 基础 RAG；Hit / MRR / Precision@K / Recall@K"
    compared: bool = False
    current: RetrievalEvalBundle | None = None
    baseline: RetrievalEvalBundle | None = None
    delta: RetrievalEvalDelta | None = None


# ----- GraphRAG（Neo4j PropertyGraphIndex）-----
class GraphBuildRequest(BaseModel):
    texts: List[str] | None = Field(
        None,
        description="待抽取文本；为空则用讲义苹果/乔布斯示例",
    )
    extractor: str = Field(
        "simple",
        description="simple=SimpleLLMPathExtractor；schema=SchemaLLMPathExtractor",
    )


class GraphQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="自然语言问题")
    k: int = Field(5, ge=1, le=50, description="similarity_top_k")


class GraphRetrieveRequest(BaseModel):
    question: str = Field(..., min_length=1, description="自然语言问题")
    k: int = Field(5, ge=1, le=50, description="similarity_top_k")


class GraphManualTripleRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="头实体")
    relation: str = Field(..., min_length=1, description="关系")
    object: str = Field(..., min_length=1, description="尾实体")
    subject_label: str = Field("entity", description="头实体类型，如 PERSON")
    object_label: str = Field("entity", description="尾实体类型，如 COMPANY")
