# -*- coding: utf-8 -*-
"""本机桥接：GitHub 网页 ↔ Ollama。

- 可后台运行（不必一直开着黑窗口）
- 网页打开时会心跳；关闭网页约 60 秒后自动退出

推荐启动（Windows，启动后可关终端）：

  curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py -o %TEMP%\\pna_proxy.py && start "" /B pythonw %TEMP%\\pna_proxy.py

或有控制台时：

  python pna_proxy.py
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN = ("127.0.0.1", 18789)
OLLAMA = "http://127.0.0.1:11434"
# 网页关闭后多久无心跳则退出（秒）
IDLE_EXIT_SEC = 60

_last_hit = time.time()
_lock = threading.Lock()
_httpd: ThreadingHTTPServer | None = None


def _touch() -> None:
    global _last_hit
    with _lock:
        _last_hit = time.time()


def _idle_watcher() -> None:
    while True:
        time.sleep(5)
        with _lock:
            idle = time.time() - _last_hit
        if idle >= IDLE_EXIT_SEC:
            _log(f"已 {int(idle)} 秒无网页心跳，自动退出桥接。")
            if _httpd is not None:
                threading.Thread(target=_httpd.shutdown, daemon=True).start()
            return


def _log(msg: str) -> None:
    # pythonw 无控制台时写到临时日志，方便排查
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    try:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()
    except Exception:
        pass
    try:
        path = os.path.join(os.environ.get("TEMP", "."), "pna_proxy.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        _log(fmt % args)

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
        _touch()
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/__ping"):
            return self._ping()
        if self.path.startswith("/__shutdown"):
            return self._shutdown()
        self._proxy()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/__ping"):
            return self._ping()
        if self.path.startswith("/__shutdown"):
            return self._shutdown()
        self._proxy()

    def _json(self, code: int, obj: dict) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _ping(self) -> None:
        _touch()
        self._json(200, {"ok": True, "idle_exit_sec": IDLE_EXIT_SEC})

    def _shutdown(self) -> None:
        _touch()
        self._json(200, {"ok": True, "bye": True})
        if _httpd is not None:
            threading.Thread(target=_httpd.shutdown, daemon=True).start()

    def _proxy(self) -> None:
        _touch()
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
            self._json(502, {"error": str(e)})
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
                _touch()
                self.wfile.write(b"%x\r\n" % len(chunk))
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        finally:
            resp.close()


def main() -> None:
    global _httpd
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=3) as r:
            tags = json.loads(r.read().decode("utf-8"))
        n = len(tags.get("models") or [])
        _log(f"已连接 Ollama，模型数：{n}")
    except Exception as e:  # noqa: BLE001
        _log(f"警告：连不上 Ollama：{e}")

    # 若端口已被占用，说明桥接已在跑
    try:
        _httpd = ThreadingHTTPServer(LISTEN, Handler)
    except OSError:
        _log(f"端口 {LISTEN[1]} 已被占用，可能桥接已在运行。")
        return

    threading.Thread(target=_idle_watcher, daemon=True).start()
    _log(f"桥接已启动 http://{LISTEN[0]}:{LISTEN[1]} （后台可关黑窗口）")
    _log(f"打开网页后保持使用；关闭网页约 {IDLE_EXIT_SEC} 秒后自动退出")
    try:
        # 有控制台时打印提示
        if sys.stdout and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            print("=" * 56)
            print(f"  桥接：http://{LISTEN[0]}:{LISTEN[1]}")
            print("  可关闭本窗口（若用 pythonw / start /B 启动）。")
            print("  打开：https://liwenyu123-spec.github.io/rag/")
            print(f"  关闭网页约 {IDLE_EXIT_SEC} 秒后自动停止。")
            print("=" * 56)
    except Exception:
        pass
    try:
        _httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _log("桥接已停止。")


if __name__ == "__main__":
    main()
