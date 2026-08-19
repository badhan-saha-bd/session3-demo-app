import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def response_for(path: str):
    if path == "/health":
        return 200, {"status": "ok"}
    if path == "/":
        return 200, {
            "application": "Hello From BJIT Academy",
            "message": "Hello from session 3",
            "delivery": "Jenkins automated pipeline",
        }
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, payload = response_for(self.path)
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"request: {self.address_string()} {format % args}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"listening on 0.0.0.0:{port}", flush=True)
    server.serve_forever()
