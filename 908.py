import os
import sys
import winreg
from openai import OpenAI

# Windows 终端默认 GBK，避免打印 emoji 时报错
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get_user_env(name: str) -> str | None:
    """读当前进程环境；若为空则从 Windows 用户环境变量读取（解决 Cursor 未完全重启）。"""
    value = os.getenv(name)
    if value:
        return value
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value or None
    except OSError:
        return None


api_key = get_user_env("DEEPSEEK_API_KEY")
base_url = get_user_env("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"

if not api_key:
    raise SystemExit(
        "未找到 DEEPSEEK_API_KEY。请在系统用户环境变量中设置，"
        "或在本终端执行: $env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User')"
    )

print("API key loaded:", f"len={len(api_key)}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "user", "content": "你是谁？"}
    ],
)
print(response.choices[0].message.content)
