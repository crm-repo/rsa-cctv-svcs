from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.request
import urllib.error

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
BACKEND_ORIGIN = "http://127.0.0.1:8000"
HOST = "127.0.0.1"
PORT = 5500

class RsaLocalProxy(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean_path = path.split("?", 1)[0].split("#", 1)[0].lstrip("/")
        if not clean_path:
            clean_path = "index.html"
        return str(FRONTEND_ROOT / clean_path)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy_to_backend()
        else:
            super().do_GET()

    def do_POST(self):
        self.proxy_or_404()

    def do_PUT(self):
        self.proxy_or_404()

    def do_PATCH(self):
        self.proxy_or_404()

    def do_DELETE(self):
        self.proxy_or_404()

    def proxy_or_404(self):
        if self.path.startswith("/api/"):
            self.proxy_to_backend()
        else:
            self.send_error(404, "Not found")

    def proxy_to_backend(self):
        target = BACKEND_ORIGIN + self.path
        body = None
        headers = {}

        for key, value in self.headers.items():
            if key.lower() not in {"host", "content-length"}:
                headers[key] = value

        if self.command in {"POST", "PUT", "PATCH"}:
            length = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(length) if length else None

        req = urllib.request.Request(target, data=body, headers=headers, method=self.command)

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in {"transfer-encoding", "connection"}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as err:
            self.send_response(err.code)
            for key, value in err.headers.items():
                if key.lower() not in {"transfer-encoding", "connection"}:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(err.read())
        except Exception as exc:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Local proxy error: {exc}".encode("utf-8"))

print(f"Serving frontend from {FRONTEND_ROOT}")
print(f"Proxying /api/* to {BACKEND_ORIGIN}")
print(f"Open http://{HOST}:{PORT}/index.html")
ThreadingHTTPServer((HOST, PORT), RsaLocalProxy).serve_forever()
