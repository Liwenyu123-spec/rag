# -*- coding: utf-8 -*-
"""极简桥接：让 GitHub 网页能访问本机 Ollama（绕过 Chrome 拦截）。

同学已有 Ollama + 模型时，无需下载整个项目。本机执行：

  curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py | python

或：

  python pna_proxy.py

然后打开 https://liwenyu123-spec.github.io/rag/ ，保持终端窗口运行。
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN = ("127.0.0.1", 18789)
OLLAMA = "http://127.0.0.1:11434"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _cors(self) -> None:
        origin = self.headers.get("Origin", "*") or "*"
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        req_headers = self.headers.get(
            "Access-Control-Request-Headers",
            "Content-Type, Authorization",
        )
        self.send_header("Access-Control-Allow-Headers", req_headers)
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._proxy()

    def do_POST(self) -> None:  # noqa: N802
        self._proxy()

    def _proxy(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length) if length else None
        url = OLLAMA + self.path
        req = urllib.request.Request(url, data=body, method=self.command)
        ctype = self.headers.get("Content-Type")
        if ctype:
            req.add_header("Content-Type", ctype)
        try:
            resp = urllib.request.urlopen(req, timeout=600)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header(
                "Content-Type", e.headers.get("Content-Type", "application/json")
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        except Exception as e:  # noqa: BLE001
            payload = json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8")
            self.send_response(502)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(resp.status)
        self._cors()
        ct = resp.headers.get("Content-Type", "application/json")
        self.send_header("Content-Type", ct)
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        try:
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                self.wfile.write(b"%x\r\n" % len(chunk))
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        finally:
            resp.close()


def main() -> None:
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=3) as r:
            tags = json.loads(r.read().decode("utf-8"))
        n = len(tags.get("models") or [])
        print(f"已连接到 Ollama，本机模型数：{n}")
    except Exception as e:  # noqa: BLE001
        print(f"警告：连不上 Ollama（{OLLAMA}）：{e}")
        print("请先打开 Ollama 应用。")

    httpd = ThreadingHTTPServer(LISTEN, Handler)
    print("=" * 56)
    print(f"  桥接已启动：http://{LISTEN[0]}:{LISTEN[1]}")
    print("  请保持本窗口运行，然后用浏览器打开：")
    print("  https://liwenyu123-spec.github.io/rag/")
    print("  用完后按 Ctrl+C 结束。")
    print("=" * 56)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
