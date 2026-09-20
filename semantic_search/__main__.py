"""支持在 rag 目录执行: python -m semantic_search"""

import uvicorn

from semantic_search.app.config import HOST, PORT


def main() -> None:
    uvicorn.run(
        "semantic_search.app.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
