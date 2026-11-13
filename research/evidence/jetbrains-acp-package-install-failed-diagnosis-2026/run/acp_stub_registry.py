#!/usr/bin/env python3
"""Loopback stub ACP registry for injectable install-defect experiments.

It serves only the contract documented in the ACP registry FORMAT.md: one
index document whose `agents` entries carry inline `distribution` blocks, plus
artifact files addressed by URL. Nothing about JetBrains IDE internals is
modelled or claimed.

Every request is appended to a JSONL transcript with method, path, HTTP status,
response bytes and latency in milliseconds, so a defect's server-side signature
can be inspected rather than assumed.

Usage:  python3 acp_stub_registry.py --root FIXTURE_DIR --log TRANSCRIPT.jsonl
Prints `PORT <n>` on stdout once bound (port 0 = ephemeral), then serves until
terminated.
"""
import argparse
import http.server
import json
import time
from pathlib import Path


class Handler(http.server.BaseHTTPRequestHandler):
    root = Path(".")
    log_path = None

    def log_message(self, *args):  # silence stderr access log; transcript is the record
        pass

    def _send(self, status, body, ctype="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        return status, len(body)

    def do_GET(self):
        started = time.perf_counter()
        status, size = 404, 0
        path = self.path.split("?", 1)[0]
        try:
            if path == "/registry-for-jetbrains.json":
                target = self.root / "registry-for-jetbrains.json"
                if target.is_file():
                    status, size = self._send(200, target.read_bytes())
                else:
                    status, size = self._send(404, b'{"error":"index not found"}')
            elif path.startswith("/artifacts/"):
                base = (self.root / "artifacts").resolve()
                target = (base / path[len("/artifacts/"):]).resolve()
                if str(target).startswith(str(base)) and target.is_file():
                    status, size = self._send(200, target.read_bytes(), "application/octet-stream")
                else:
                    status, size = self._send(404, b'{"error":"artifact not found"}')
            else:
                status, size = self._send(404, b'{"error":"unknown path"}')
        finally:
            record = {
                "ts": round(time.time(), 3),
                "method": self.command,
                "path": path,
                "status": status,
                "bytes": size,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
            with open(self.log_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    Handler.root = args.root.resolve()
    Handler.log_path = args.log
    args.log.parent.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"PORT {server.server_address[1]}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
