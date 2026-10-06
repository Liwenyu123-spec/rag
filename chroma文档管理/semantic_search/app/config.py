"""语义搜索 / Native RAG 服务的路径与环境变量配置。"""  # 模块说明：集中管理路径、密钥、模型与服务参数

import os  # 读进程环境变量
import sys  # 判断是否 Windows，以及平台相关逻辑
from pathlib import Path  # 拼接项目内路径

from dotenv import load_dotenv  # 从 .env 文件加载键值到环境变量

APP_DIR = Path(__file__).resolve().parent  # 当前文件所在目录：.../semantic_search/app
PACKAGE_DIR = APP_DIR.parent  # 上一级：semantic_search 包目录
# 包现在在 rag/chroma文档管理/semantic_search/，再上一级才是仓库根目录
PROJECT_ROOT = PACKAGE_DIR.parent.parent  # rag 项目根目录（放 .env）

load_dotenv(PROJECT_ROOT / ".env")  # 优先加载仓库根目录 .env
load_dotenv(PACKAGE_DIR.parent / ".env")  # 项目目录 .env
load_dotenv(PACKAGE_DIR / ".env")  # 包目录 .env


def _reg_get(root, path: str, name: str) -> str | None:  # 从 Windows 注册表读单个环境变量
    """从 Windows 注册表读取用户/系统环境变量。"""  # 文档：注册表读取说明
    if sys.platform != "win32":  # 非 Windows 直接返回空
        return None  # 非 Windows 无注册表可读
    import winreg  # 仅在 Windows 才导入注册表模块

    try:  # 注册表可能不存在该键
        with winreg.OpenKey(root, path) as reg:  # 打开指定注册表键
            value, _ = winreg.QueryValueEx(reg, name)  # 读取名为 name 的值
            return (value or "").strip() or None  # 去掉空白；空串当成没有
    except OSError:  # 键不存在或无权读取
        return None  # 读失败当作没有该变量


def get_windows_env(name: str) -> str:  # 按优先级查找环境变量
    """进程环境 → .env → 用户变量 → 系统变量。"""  # 查找顺序说明
    value = os.getenv(name, "").strip()  # 1) 进程环境（含已 load 的 .env）
    if value:  # 找到就立刻返回
        return value  # 最高优先级命中
    if sys.platform != "win32":  # 非 Windows 没有注册表兜底
        return ""  # 直接空串
    import winreg  # Windows 注册表常量

    value = _reg_get(winreg.HKEY_CURRENT_USER, r"Environment", name)  # 2) 用户环境变量
    if value:  # 用户变量有值
        return value  # 直接返回
    return (  # 3) 系统环境变量；没有则空串
        _reg_get(  # 读系统级 Environment
            winreg.HKEY_LOCAL_MACHINE,  # 本机注册表根
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",  # 系统环境变量路径
            name,  # 变量名
        )  # 括号结束
        or ""  # 读不到就返回空串
    )  # 括号结束


DASHSCOPE_API_KEY = get_windows_env("DASHSCOPE_API_KEY")  # 阿里云千问 / 百炼 Key
DEEPSEEK_API_KEY = get_windows_env("DEEPSEEK_API_KEY")  # DeepSeek Key
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()  # DeepSeek API 根地址

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()  # 大模型提供方，默认 deepseek
LLM_MODEL = os.getenv(  # 大模型名称
    "LLM_MODEL",  # 环境变量名
    "deepseek-v4-flash" if LLM_PROVIDER == "deepseek" else "qwen-plus",  # 按提供方给默认模型名
)  # LLM_MODEL 赋值结束

# DeepSeek 没有公开 Embedding 接口；没有千问 Key 时用本地 HuggingFace / Chinese-CLIP。
_DEFAULT_CHINESE_CLIP = r"H:\二阶段\chinese-clip-vit-base-patch16"  # Bandizip 解压目标
if os.getenv("EMBEDDING_PROVIDER"):  # 若显式配置了向量化提供方
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()  # 用用户配置
elif Path(_DEFAULT_CHINESE_CLIP).is_dir() and (  # 本地已有 Chinese-CLIP 权重
    Path(_DEFAULT_CHINESE_CLIP) / "pytorch_model.bin"
).is_file():
    EMBEDDING_PROVIDER = "chinese_clip"  # 优先本地 Chinese-CLIP
elif DASHSCOPE_API_KEY:  # 有千问 Key 时默认走云端 Embedding
    EMBEDDING_PROVIDER = "dashscope"  # 云端千问向量化
else:  # 否则用本地 HuggingFace 模型
    EMBEDDING_PROVIDER = "huggingface"  # 本地 bge 等模型

if EMBEDDING_PROVIDER == "chinese_clip":  # Chinese-CLIP 本地目录
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", _DEFAULT_CHINESE_CLIP)  # 默认二阶段目录
elif EMBEDDING_PROVIDER == "huggingface":  # 本地向量模型默认名
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")  # 中文小模型，体积小
else:  # 千问向量模型默认名
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")  # 阿里云默认 embedding

EMBEDDING_API_BASE = os.getenv(  # OpenAI 兼容的 Embedding 接口地址（千问兼容模式）
    "EMBEDDING_API_BASE",  # 环境变量名
    "https://dashscope.aliyuncs.com/compatible-mode/v1",  # 默认兼容模式地址
)  # 括号结束

RAG_SYSTEM_PROMPT = os.getenv(  # 多轮 RAG 对话的系统提示词
    "RAG_SYSTEM_PROMPT",  # 环境变量名
    "你是一个知识库助手，根据检索的内容，用简体中文回答问题",  # 默认中文助手人设
)  # 括号结束

# Chinese-CLIP 维度与 bge/千问不同，默认换独立集合，避免旧向量混用
_default_collection = (
    "native_rag_chinese_clip" if EMBEDDING_PROVIDER == "chinese_clip" else "native_rag"
)
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", _default_collection)  # Chroma 集合名
CHROMA_PERSIST_DIR = os.getenv(  # Chroma 持久化目录
    "CHROMA_PERSIST_DIR",  # 环境变量名
    str(PACKAGE_DIR / "chroma_db"),  # 默认在包内 chroma_db/
)  # 持久化路径赋值结束
DATA_DIR = os.getenv("RAG_DATA_DIR", str(PACKAGE_DIR / "data"))  # 默认知识库文件目录

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))  # 分块大小
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))  # 分块重叠，减轻切断语义
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))  # 最终返回/精排后条数


def _env_bool(name: str, default: bool) -> bool:  # 读布尔型环境变量的小工具
    """读布尔环境变量：1/true/yes/on 为真。"""  # 函数说明
    raw = os.getenv(name)  # 取原始字符串；未设置则为 None
    if raw is None or not str(raw).strip():  # 未设置或全空白
        return default  # 回退到调用方默认值
    return str(raw).strip().lower() in {"1", "true", "yes", "on", "y"}  # 常见真值集合


# ----- 检索中 / 检索后优化（可用环境变量开关）-----
HYBRID_ENABLED = _env_bool("HYBRID_ENABLED", True)  # 同库：向量 + BM25 融合
HYBRID_FUSION_MODE = os.getenv("HYBRID_FUSION_MODE", "reciprocal_rerank").strip()  # 或 relative_score
RETRIEVE_CANDIDATES = int(os.getenv("RETRIEVE_CANDIDATES", "20"))  # 粗排候选数（给精排留窗口）
# 重排：默认本地 bge，不依赖千问；provider=dashscope 才需要 DASHSCOPE_API_KEY
RERANK_ENABLED = _env_bool("RERANK_ENABLED", True)  # 是否启用重排序
RERANK_PROVIDER = os.getenv("RERANK_PROVIDER", "local").strip().lower()  # local | dashscope | none
_DEFAULT_BGE_RERANKER = r"H:\二阶段\bge-reranker-base"
_PACKAGED_BGE_RERANKER = PACKAGE_DIR / "models" / "bge-reranker-base"


def _looks_like_hf_model_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    return any(
        (path / name).is_file()
        for name in ("config.json", "modules.json", "pytorch_model.bin", "model.safetensors")
    )


def _resolve_rerank_model() -> str:
    if (RERANK_PROVIDER or "local").strip().lower() in {"dashscope", "qwen", "aliyun"}:
        return os.getenv("RERANK_MODEL", "qwen3-rerank").strip()
    configured = (os.getenv("RERANK_MODEL") or "").strip()
    candidates = [
        Path(configured) if configured else None,
        Path(_DEFAULT_BGE_RERANKER),
        _PACKAGED_BGE_RERANKER,
    ]
    for item in candidates:
        if item is not None and _looks_like_hf_model_dir(item):
            return str(item.resolve())
    return configured or _DEFAULT_BGE_RERANKER


RERANK_MODEL = _resolve_rerank_model()
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "0"))  # 0 表示跟 SIMILARITY_TOP_K / 请求 k 一致
COMPRESS_ENABLED = _env_bool("COMPRESS_ENABLED", True)  # 句子级上下文压缩
COMPRESS_PERCENTILE = float(os.getenv("COMPRESS_PERCENTILE", "0.5"))  # 每片段保留相关句比例
REORDER_ENABLED = _env_bool("REORDER_ENABLED", True)  # 长上下文首尾重排版
# Corrective RAG：过滤无关片段；全无关则改写查询再搜一次（库内修正，不联网）
CRAG_ENABLED = _env_bool("CRAG_ENABLED", True)  # Corrective RAG 总开关
CRAG_VERBOSE = _env_bool("CRAG_VERBOSE", True)  # 终端打印每篇相关/无关
# Self-RAG（讲义工程版）：Retrieve 门控 + ISSUP 验据修正 + ISUSE 打分
SELF_RAG_ENABLED = _env_bool("SELF_RAG_ENABLED", False)  # 默认关，前端勾选开启
SELF_RAG_VERBOSE = _env_bool("SELF_RAG_VERBOSE", True)  # Self-RAG 过程日志
# RAG 评估（飞书 01-RAG评估）：生成侧 Faithfulness/Relevancy/Correctness
EVAL_VERBOSE = _env_bool("EVAL_VERBOSE", True)  # 评估过程日志

QDRANT_PATH = os.getenv("QDRANT_PATH", str(PACKAGE_DIR / "qdrant_db"))
DEFAULT_VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "chroma").strip().lower() or "chroma"


def normalize_vector_backend(name: str | None) -> str:
    raw = (name or DEFAULT_VECTOR_BACKEND or "chroma").strip().lower()
    if raw in {"qdrant", "qd", "qdrant_client"}:
        return "qdrant"
    return "chroma"


HOST = os.getenv("SEARCH_HOST", "127.0.0.1")  # Web 服务监听地址
PORT = int(os.getenv("SEARCH_PORT", "8003"))  # 默认 8003，避免和「带安全校验的聊天机器人」8001 冲突

# ----- GraphRAG（PropertyGraphIndex + Neo4j；LLM 可用 DeepSeek / 千问）-----
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687").strip()  # Bolt，不是 7474
NEO4J_USERNAME = (
    os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER") or "neo4j"
).strip()  # 默认 neo4j
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "").strip()  # 必填：首次改密后的密码
# Graph LLM：有 DeepSeek 默认用 deepseek；显式设 GRAPH_LLM_PROVIDER=dashscope 才用千问
if os.getenv("GRAPH_LLM_PROVIDER"):
    GRAPH_LLM_PROVIDER = os.getenv("GRAPH_LLM_PROVIDER", "").strip().lower()
elif DEEPSEEK_API_KEY:
    GRAPH_LLM_PROVIDER = "deepseek"
elif DASHSCOPE_API_KEY:
    GRAPH_LLM_PROVIDER = "dashscope"
else:
    GRAPH_LLM_PROVIDER = "deepseek"
GRAPH_LLM_MODEL = os.getenv(
    "GRAPH_LLM_MODEL",
    "deepseek-v4-flash" if GRAPH_LLM_PROVIDER == "deepseek" else "qwen-plus",
).strip()
# Graph Embedding：DeepSeek 无向量接口；默认本地 Chinese-CLIP / HF，有千问也可用 dashscope
_DEFAULT_CHINESE_CLIP_GRAPH = r"H:\二阶段\chinese-clip-vit-base-patch16"
if os.getenv("GRAPH_EMBED_PROVIDER"):
    GRAPH_EMBED_PROVIDER = os.getenv("GRAPH_EMBED_PROVIDER", "").strip().lower()
elif Path(_DEFAULT_CHINESE_CLIP_GRAPH).is_dir() and (
    Path(_DEFAULT_CHINESE_CLIP_GRAPH) / "pytorch_model.bin"
).is_file():
    GRAPH_EMBED_PROVIDER = "chinese_clip"
elif DASHSCOPE_API_KEY:
    GRAPH_EMBED_PROVIDER = "dashscope"
else:
    GRAPH_EMBED_PROVIDER = "huggingface"
if GRAPH_EMBED_PROVIDER == "chinese_clip":
    GRAPH_EMBED_MODEL = os.getenv("GRAPH_EMBED_MODEL", _DEFAULT_CHINESE_CLIP_GRAPH).strip()
elif GRAPH_EMBED_PROVIDER == "dashscope":
    GRAPH_EMBED_MODEL = os.getenv("GRAPH_EMBED_MODEL", "text-embedding-v4").strip()
else:
    GRAPH_EMBED_MODEL = os.getenv("GRAPH_EMBED_MODEL", "BAAI/bge-small-zh-v1.5").strip()
GRAPH_EXTRACTOR = os.getenv("GRAPH_EXTRACTOR", "simple").strip().lower()  # simple | schema
GRAPH_RAG_ENABLED = _env_bool("GRAPH_RAG_ENABLED", True)  # 总开关：缺依赖时可关

# ----- 多模态 RAG（Chinese-CLIP 图像塔 + 可选千问 VL 看图）-----
IMAGE_COLLECTION_NAME = os.getenv("CHROMA_IMAGE_COLLECTION", "native_rag_clip_images")
IMAGE_DIR = os.getenv("RAG_IMAGE_DIR", str(Path(DATA_DIR) / "images"))
VL_MODEL = os.getenv("VL_MODEL", "qwen-vl-plus").strip()
DASHSCOPE_COMPAT_BASE = os.getenv(
    "DASHSCOPE_COMPAT_BASE",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
).strip()
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")
