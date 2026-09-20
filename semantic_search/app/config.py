"""语义搜索服务的路径与环境变量配置。"""

import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = APP_DIR.parent
PROJECT_ROOT = PACKAGE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PACKAGE_DIR / ".env")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
EMBEDDING_API_BASE = os.getenv(
    "EMBEDDING_API_BASE",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "semantic_search")
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    str(PACKAGE_DIR / "chroma_data"),
)
HOST = os.getenv("SEARCH_HOST", "127.0.0.1")
PORT = int(os.getenv("SEARCH_PORT", "8001"))
