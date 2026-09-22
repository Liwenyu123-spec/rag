"""支持在 rag 目录执行: python -m semantic_search"""  # 包入口说明：用 python -m 启动服务

import uvicorn  # ASGI 服务器，真正监听 HTTP 端口

from semantic_search.app.config import HOST, PORT  # 从配置读取监听地址和端口


def main() -> None:  # 启动入口函数
    uvicorn.run(  # 阻塞运行，直到 Ctrl+C
        "semantic_search.app.main:app",  # 用字符串导入 FastAPI 应用实例
        host=HOST,  # 监听主机，默认 127.0.0.1
        port=PORT,  # 监听端口，默认 8001
        reload=False,  # 关闭热重载，避免重复加载大模型
    )


if __name__ == "__main__":  # 被 python -m semantic_search 执行时进入
    main()  # 调用上面的启动函数
