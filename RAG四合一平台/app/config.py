# -*- coding: utf-8 -*-
"""共享配置：密钥、模型、路径。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PLATFORM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLATFORM_ROOT.parent
CHROMA_APP_ROOT = PLATFORM_ROOT / "apps" / "chroma文档管理"

load_dotenv(REPO_ROOT / ".env", override=True)
load_dotenv(PLATFORM_ROOT / ".env", override=True)


def get_api_key() -> str:
    key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if key:
        return key
    if sys.platform == "win32":
        import winreg

        for root, path in (
            (winreg.HKEY_CURRENT_USER, r"Environment"),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ),
        ):
            try:
                with winreg.OpenKey(root, path) as reg:
                    value, _ = winreg.QueryValueEx(reg, "DEEPSEEK_API_KEY")
                    if value:
                        return str(value).strip()
            except OSError:
                pass
    return ""


DEEPSEEK_API_KEY = get_api_key()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-flash").strip()
HOST = os.getenv("PLATFORM_HOST", "127.0.0.1")
PORT = int(os.getenv("PLATFORM_PORT", "8100"))
