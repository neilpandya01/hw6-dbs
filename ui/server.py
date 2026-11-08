#!/usr/bin/env python3
"""Local server for the day page. Read-only: serves ui/ and plan/today.json. No deploy needed.

Usage: python3 ui/server.py [port]      then open http://127.0.0.1:8000
Add ?sample to the page URL to preview with ui/sample-plan.json (made-up data).
"""
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

UI = Path(__file__).resolve().parent
PLAN = UI.parent / "plan" / "today.json"
SAMPLE = UI / "sample-plan.json"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/plan":
            src = SAMPLE if "sample" in parse_qs(url.query, keep_blank_values=True) else PLAN
            if not src.exists():
                return self.send_json(404, {"error": "no plan saved yet"})
            try:
                json.loads(src.read_text())
            except json.JSONDecodeError:
                return self.send_json(503, {"error": "plan is mid-write, retry"})
            return self.send_bytes(200, src.read_bytes())
        if url.path in ("/", ""):
            self.path = "/index.html"
        elif url.path not in ("/index.html",):
            return self.send_json(404, {"error": "not found"})
        return super().do_GET()

    def send_json(self, code, obj):
        self.send_bytes(code, json.dumps(obj).encode())

    def send_bytes(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Day page: http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
