"""语义搜索 / Native RAG 服务的路径与环境变量配置。"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = APP_DIR.parent
PROJECT_ROOT = PACKAGE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PACKAGE_DIR / ".env")


def _reg_get(root, path: str, name: str) -> str | None:
    """从 Windows 注册表读取用户/系统环境变量。"""
    if sys.platform != "win32":
        return None
    import winreg

    try:
        with winreg.OpenKey(root, path) as reg:
            value, _ = winreg.QueryValueEx(reg, name)
            return (value or "").strip() or None
    except OSError:
        return None


def get_windows_env(name: str) -> str:
    """进程环境 → .env → 用户变量 → 系统变量。"""
    value = os.getenv(name, "").strip()
    if value:
        return value
    if sys.platform != "win32":
        return ""
    import winreg

    value = _reg_get(winreg.HKEY_CURRENT_USER, r"Environment", name)
    if value:
        return value
    return (
        _reg_get(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            name,
        )
        or ""
    )


DASHSCOPE_API_KEY = get_windows_env("DASHSCOPE_API_KEY")
DEEPSEEK_API_KEY = get_windows_env("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "deepseek-v4-flash" if LLM_PROVIDER == "deepseek" else "qwen-plus",
)

# DeepSeek 没有公开 Embedding 接口；没有千问 Key 时用本地 HuggingFace。
if os.getenv("EMBEDDING_PROVIDER"):
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()
elif DASHSCOPE_API_KEY:
    EMBEDDING_PROVIDER = "dashscope"
else:
    EMBEDDING_PROVIDER = "huggingface"

if EMBEDDING_PROVIDER == "huggingface":
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
else:
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

EMBEDDING_API_BASE = os.getenv(
    "EMBEDDING_API_BASE",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)

RAG_SYSTEM_PROMPT = os.getenv(
    "RAG_SYSTEM_PROMPT",
    "你是一个知识库助手，根据检索的内容，用简体中文回答问题",
)

COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "native_rag")
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    str(PACKAGE_DIR / "chroma_db"),
)
DATA_DIR = os.getenv("RAG_DATA_DIR", str(PACKAGE_DIR / "data"))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))

HOST = os.getenv("SEARCH_HOST", "127.0.0.1")
PORT = int(os.getenv("SEARCH_PORT", "8001"))
