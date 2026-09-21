"""调用本地语义搜索 / Native RAG 接口。"""

import json
import os
import sys

import requests

HOST = os.getenv("SEARCH_HOST", "127.0.0.1")
PORT = int(os.getenv("SEARCH_PORT", "8001"))
BASE_URL = f"http://{HOST}:{PORT}"


def main() -> None:
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    print("健康检查:")
    print(json.dumps(health.json(), indent=2, ensure_ascii=False))
    print()

    response = requests.get(
        f"{BASE_URL}/search",
        params={"q": "向量搜索工具", "k": 3},
        timeout=30,
    )
    print("搜索结果:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    if not response.ok:
        sys.exit(1)

    query = requests.get(
        f"{BASE_URL}/query",
        params={"q": "迟到怎么扣钱", "k": 3},
        timeout=120,
    )
    print()
    print("RAG 问答:")
    print(json.dumps(query.json(), indent=2, ensure_ascii=False))
    if not query.ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
