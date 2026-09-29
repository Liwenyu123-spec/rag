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
    """从 Windows 注册表读取用户/系统环境变量。"""
    if sys.platform != "win32":  # 非 Windows 直接返回空
        return None  # 非 Windows 无注册表可读
    import winreg  # 仅在 Windows 才导入注册表模块

    try:
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
        )
        or ""  # 读不到就返回空串
    )


DASHSCOPE_API_KEY = get_windows_env("DASHSCOPE_API_KEY")  # 阿里云千问 / 百炼 Key
DEEPSEEK_API_KEY = get_windows_env("DEEPSEEK_API_KEY")  # DeepSeek Key
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()  # DeepSeek API 根地址

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()  # 大模型提供方，默认 deepseek
LLM_MODEL = os.getenv(  # 大模型名称
    "LLM_MODEL",  # 环境变量名
    "deepseek-v4-flash" if LLM_PROVIDER == "deepseek" else "qwen-plus",  # 按提供方给默认模型名
)  # LLM_MODEL 赋值结束

# DeepSeek 没有公开 Embedding 接口；没有千问 Key 时用本地 HuggingFace。
if os.getenv("EMBEDDING_PROVIDER"):  # 若显式配置了向量化提供方
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()  # 用用户配置
elif DASHSCOPE_API_KEY:  # 有千问 Key 时默认走云端 Embedding
    EMBEDDING_PROVIDER = "dashscope"  # 云端千问向量化
else:  # 否则用本地 HuggingFace 模型
    EMBEDDING_PROVIDER = "huggingface"  # 本地 bge 等模型

if EMBEDDING_PROVIDER == "huggingface":  # 本地向量模型默认名
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")  # 中文小模型，体积小
else:  # 千问向量模型默认名
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")  # 阿里云默认 embedding

EMBEDDING_API_BASE = os.getenv(  # OpenAI 兼容的 Embedding 接口地址（千问兼容模式）
    "EMBEDDING_API_BASE",  # 环境变量名
    "https://dashscope.aliyuncs.com/compatible-mode/v1",  # 默认兼容模式地址
)

RAG_SYSTEM_PROMPT = os.getenv(  # 多轮 RAG 对话的系统提示词
    "RAG_SYSTEM_PROMPT",  # 环境变量名
    "你是一个知识库助手，根据检索的内容，用简体中文回答问题",  # 默认中文助手人设
)

COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "native_rag")  # Chroma 集合名
CHROMA_PERSIST_DIR = os.getenv(  # Chroma 持久化目录
    "CHROMA_PERSIST_DIR",  # 环境变量名
    str(PACKAGE_DIR / "chroma_db"),  # 默认在包内 chroma_db/
)  # 持久化路径赋值结束
DATA_DIR = os.getenv("RAG_DATA_DIR", str(PACKAGE_DIR / "data"))  # 默认知识库文件目录

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))  # 分块大小
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))  # 分块重叠，减轻切断语义
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))  # 最终返回/精排后条数


def _env_bool(name: str, default: bool) -> bool:
    """读布尔环境变量：1/true/yes/on 为真。"""
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on", "y"}


# ----- 检索中 / 检索后优化（可用环境变量开关）-----
HYBRID_ENABLED = _env_bool("HYBRID_ENABLED", True)  # 同库：向量 + BM25 融合
HYBRID_FUSION_MODE = os.getenv("HYBRID_FUSION_MODE", "reciprocal_rerank").strip()  # 或 relative_score
RETRIEVE_CANDIDATES = int(os.getenv("RETRIEVE_CANDIDATES", "20"))  # 粗排候选数（给精排留窗口）
# 重排：默认本地 bge，不依赖千问；provider=dashscope 才需要 DASHSCOPE_API_KEY
RERANK_ENABLED = _env_bool("RERANK_ENABLED", True)
RERANK_PROVIDER = os.getenv("RERANK_PROVIDER", "local").strip().lower()  # local | dashscope | none
RERANK_MODEL = os.getenv(
    "RERANK_MODEL",
    "BAAI/bge-reranker-base" if os.getenv("RERANK_PROVIDER", "local").strip().lower() != "dashscope" else "qwen3-rerank",
).strip()
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "0"))  # 0 表示跟 SIMILARITY_TOP_K / 请求 k 一致
COMPRESS_ENABLED = _env_bool("COMPRESS_ENABLED", True)  # 句子级上下文压缩
COMPRESS_PERCENTILE = float(os.getenv("COMPRESS_PERCENTILE", "0.5"))  # 每片段保留相关句比例
REORDER_ENABLED = _env_bool("REORDER_ENABLED", True)  # 长上下文首尾重排版
# Corrective RAG：过滤无关片段；全无关则改写查询再搜一次（库内修正，不联网）
CRAG_ENABLED = _env_bool("CRAG_ENABLED", True)
CRAG_VERBOSE = _env_bool("CRAG_VERBOSE", True)  # 终端打印每篇相关/无关
# Self-RAG（讲义工程版）：Retrieve 门控 + ISSUP 验据修正 + ISUSE 打分
SELF_RAG_ENABLED = _env_bool("SELF_RAG_ENABLED", False)  # 默认关，前端勾选开启
SELF_RAG_VERBOSE = _env_bool("SELF_RAG_VERBOSE", True)

HOST = os.getenv("SEARCH_HOST", "127.0.0.1")  # Web 服务监听地址
PORT = int(os.getenv("SEARCH_PORT", "8003"))  # 默认 8003，避免和「带安全校验的聊天机器人」8001 冲突
