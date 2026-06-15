from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / "frontend"
BACKEND = "http://127.0.0.1:8000"

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0].lstrip("/") or "index.html"
        return str(ROOT / clean)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        return self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        return self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        return self.send_error(404)

    def proxy(self):
        body = None
        if "Content-Length" in self.headers:
            body = self.rfile.read(int(self.headers["Content-Length"]))
        req = urllib.request.Request(BACKEND + self.path, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length"):
                req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                self.send_response(res.status)
                for k, v in res.headers.items():
                    if k.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(res.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())

print(f"Serving frontend from {ROOT}")
print(f"Proxying /api/* to {BACKEND}")
print("Open http://127.0.0.1:5500/index.html")
ThreadingHTTPServer(("127.0.0.1", 5500), Handler).serve_forever()
