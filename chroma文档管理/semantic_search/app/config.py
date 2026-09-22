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
        return None
    import winreg  # 仅在 Windows 才导入注册表模块

    try:
        with winreg.OpenKey(root, path) as reg:  # 打开指定注册表键
            value, _ = winreg.QueryValueEx(reg, name)  # 读取名为 name 的值
            return (value or "").strip() or None  # 去掉空白；空串当成没有
    except OSError:  # 键不存在或无权读取
        return None


def get_windows_env(name: str) -> str:  # 按优先级查找环境变量
    """进程环境 → .env → 用户变量 → 系统变量。"""
    value = os.getenv(name, "").strip()  # 1) 进程环境（含已 load 的 .env）
    if value:  # 找到就立刻返回
        return value
    if sys.platform != "win32":  # 非 Windows 没有注册表兜底
        return ""
    import winreg  # Windows 注册表常量

    value = _reg_get(winreg.HKEY_CURRENT_USER, r"Environment", name)  # 2) 用户环境变量
    if value:
        return value
    return (  # 3) 系统环境变量；没有则空串
        _reg_get(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            name,
        )
        or ""
    )


DASHSCOPE_API_KEY = get_windows_env("DASHSCOPE_API_KEY")  # 阿里云千问 / 百炼 Key
DEEPSEEK_API_KEY = get_windows_env("DEEPSEEK_API_KEY")  # DeepSeek Key
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()  # DeepSeek API 根地址

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()  # 大模型提供方，默认 deepseek
LLM_MODEL = os.getenv(  # 大模型名称
    "LLM_MODEL",
    "deepseek-v4-flash" if LLM_PROVIDER == "deepseek" else "qwen-plus",  # 按提供方给默认模型名
)

# DeepSeek 没有公开 Embedding 接口；没有千问 Key 时用本地 HuggingFace。
if os.getenv("EMBEDDING_PROVIDER"):  # 若显式配置了向量化提供方
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()  # 用用户配置
elif DASHSCOPE_API_KEY:  # 有千问 Key 时默认走云端 Embedding
    EMBEDDING_PROVIDER = "dashscope"
else:  # 否则用本地 HuggingFace 模型
    EMBEDDING_PROVIDER = "huggingface"

if EMBEDDING_PROVIDER == "huggingface":  # 本地向量模型默认名
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
else:  # 千问向量模型默认名
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

EMBEDDING_API_BASE = os.getenv(  # OpenAI 兼容的 Embedding 接口地址（千问兼容模式）
    "EMBEDDING_API_BASE",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
)

RAG_SYSTEM_PROMPT = os.getenv(  # 多轮 RAG 对话的系统提示词
    "RAG_SYSTEM_PROMPT",
    "你是一个知识库助手，根据检索的内容，用简体中文回答问题",
)

COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "native_rag")  # Chroma 集合名
CHROMA_PERSIST_DIR = os.getenv(  # Chroma 持久化目录
    "CHROMA_PERSIST_DIR",
    str(PACKAGE_DIR / "chroma_db"),  # 默认在包内 chroma_db/
)
DATA_DIR = os.getenv("RAG_DATA_DIR", str(PACKAGE_DIR / "data"))  # 默认知识库文件目录

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))  # 分块大小
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))  # 分块重叠，减轻切断语义
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))  # 默认检索返回条数

HOST = os.getenv("SEARCH_HOST", "127.0.0.1")  # Web 服务监听地址
PORT = int(os.getenv("SEARCH_PORT", "8001"))  # Web 服务端口
