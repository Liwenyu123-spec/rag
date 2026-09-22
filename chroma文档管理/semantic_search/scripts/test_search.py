"""调用本地语义搜索 / Native RAG 接口。"""  # 脚本说明：手动测 /health、/search、/query

import json  # 把响应漂亮地格式化打印
import os  # 读环境变量里的主机和端口
import sys  # 请求失败时用非 0 退出码结束进程

import requests  # 发 HTTP 请求调用本地服务

HOST = os.getenv("SEARCH_HOST", "127.0.0.1")  # 服务地址，默认本机
PORT = int(os.getenv("SEARCH_PORT", "8001"))  # 服务端口，默认 8001
BASE_URL = f"http://{HOST}:{PORT}"  # 拼出接口根 URL


def main() -> None:  # 依次测健康检查、搜索、问答
    health = requests.get(f"{BASE_URL}/health", timeout=10)  # 先看引擎是否就绪
    print("健康检查:")  # 打印区块标题
    print(json.dumps(health.json(), indent=2, ensure_ascii=False))  # 中文友好的 JSON 输出
    print()  # 空行分隔

    response = requests.get(  # GET 语义搜索
        f"{BASE_URL}/search",  # 搜索接口
        params={"q": "向量搜索工具", "k": 3},  # 查询词和返回条数
        timeout=30,  # 最长等 30 秒
    )
    print("搜索结果:")  # 打印区块标题
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))  # 打印检索结果
    if not response.ok:  # HTTP 状态码不是 2xx
        sys.exit(1)  # 以失败码退出，方便脚本/CI 判断

    query = requests.get(  # GET 一次性 RAG 问答
        f"{BASE_URL}/query",  # 问答接口
        params={"q": "迟到怎么扣钱", "k": 3},  # 示例问题（依赖知识库内容）
        timeout=120,  # 调大模型可能较慢，给 120 秒
    )
    print()  # 空行
    print("RAG 问答:")  # 打印区块标题
    print(json.dumps(query.json(), indent=2, ensure_ascii=False))  # 打印答案和来源
    if not query.ok:  # 问答失败
        sys.exit(1)  # 失败退出


if __name__ == "__main__":  # 直接运行本脚本时执行
    main()  # 跑测试流程
