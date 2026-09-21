"""语义搜索 / Native RAG 服务的路径与环境变量配置。"""

import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = APP_DIR.parent
PROJECT_ROOT = PACKAGE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PACKAGE_DIR / ".env")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
EMBEDDING_API_BASE = os.getenv(
    "EMBEDDING_API_BASE",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "dashscope").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus" if LLM_PROVIDER == "dashscope" else "deepseek-v4-flash")
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
