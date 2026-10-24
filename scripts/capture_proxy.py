#!/usr/bin/env python3
"""Logging proxy that captures Topcoder's exact API requests.

Point Topcoder at it, run any mode, and read the captured JSON:

    python3 capture_proxy.py &                 # 127.0.0.1:8787, ./captures
    TOPCODER_BASE_URL=http://127.0.0.1:8787 \
    TOPCODER_API_KEY=sk-test topcoder -p "hi"

Each capture holds {path, headers, body_raw, body_json}. The system prompt and
tool schemas are body_json["system"] and body_json["tools"].

Env overrides: CC_PROXY_PORT, CC_PROXY_OUT.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("CC_PROXY_PORT", "8787"))
OUT = os.environ.get("CC_PROXY_OUT", os.path.join(os.getcwd(), "captures"))
os.makedirs(OUT, exist_ok=True)
counter = {"n": 0}

SSE = [
    ("message_start", {"type": "message_start", "message": {
        "id": "msg_proxy", "type": "message", "role": "assistant", "model": "proxy",
        "content": [], "stop_reason": None, "stop_sequence": None,
        "usage": {"input_tokens": 1, "output_tokens": 1}}}),
    ("content_block_start", {"type": "content_block_start", "index": 0,
                             "content_block": {"type": "text", "text": ""}}),
    ("content_block_delta", {"type": "content_block_delta", "index": 0,
                             "delta": {"type": "text_delta", "text": "ok"}}),
    ("content_block_stop", {"type": "content_block_stop", "index": 0}),
    ("message_delta", {"type": "message_delta",
                       "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                       "usage": {"output_tokens": 1}}),
    ("message_stop", {"type": "message_stop"}),
]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        counter["n"] += 1
        idx = counter["n"]
        rec = {"idx": idx, "path": self.path, "method": self.command,
               "headers": dict(self.headers),
               "body_raw": body.decode("utf-8", "replace")}
        try:
            rec["body_json"] = json.loads(body)
        except Exception:
            rec["body_json"] = None
        path = os.path.join(OUT, f"req-{idx:03d}.json")
        with open(path, "w") as f:
            json.dump(rec, f, indent=2)
        print(f"[capture_proxy] {self.command} {self.path} -> {path}", file=sys.stderr)

        if "/count_tokens" in self.path:
            payload = json.dumps({"input_tokens": 100}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            for ev, data in SSE:
                self.wfile.write(f"event: {ev}\ndata: {json.dumps(data)}\n\n".encode())
                self.wfile.flush()
        except Exception:
            pass


if __name__ == "__main__":
    print(f"[capture_proxy] listening on 127.0.0.1:{PORT}, writing to {OUT}", file=sys.stderr)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
