#!/usr/bin/env python3
"""Offline fixture test for probe.py: a stdlib mock Ollama server that replays
one tool-calling response when no constraint is present and one schema-shaped
response when a constraint is present, so probe.py's request/parse/classify
path can be exercised without a live model.

This is a local fixture check of the harness mechanics. It is NOT a measurement
of any Ollama build: nothing here is graded by a model. The vendor measurement
is results.jsonl, produced against Ollama 0.20.3 on 2026-11-10.

Run: python3 fixture_test.py            (writes fixture_output.txt)
Exit code 0 = all assertions passed.
"""
import importlib.util
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixture_output.txt")

TOOL_CALL_REPLY = {
    "model": "fixture",
    "message": {"role": "assistant", "content": "",
                "tool_calls": [{"function": {"name": "get_weather",
                                             "arguments": {"city": "Lisbon"}}}]},
    "done_reason": "stop", "eval_count": 22,
}
CONSTRAINED_TWO_FIELD = {"model": "fixture",
                         "message": {"role": "assistant",
                                     "content": '{"city":"Lisbon","temperature_c":10}'},
                         "done_reason": "stop", "eval_count": 17}
CONSTRAINED_ENUM = {"model": "fixture",
                    "message": {"role": "assistant", "content": '{"decision":"use_tool"}'},
                    "done_reason": "stop", "eval_count": 10}
CONSTRAINED_JSON = {"model": "fixture",
                    "message": {"role": "assistant",
                                "content": '{"name": "get_weather", "arguments": {"city": "Lisbon"}}'},
                    "done_reason": "stop", "eval_count": 19}


def v1_wrap(payload):
    """Reshape a native reply into the /v1/chat/completions envelope."""
    msg = payload["message"]
    return {"choices": [{"message": {"role": "assistant", "content": msg.get("content", ""),
                                     "tool_calls": msg.get("tool_calls")},
                         "finish_reason": payload["done_reason"]}],
            "usage": {"completion_tokens": payload["eval_count"]}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/version":
            return self._send({"version": "fixture-0"})
        self._send({"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        req = json.loads(self.rfile.read(length) or b"{}")
        # Replay rule: a constraint of any shape suppresses the call, which is
        # the behaviour the live run recorded. The rule is fixed in this file,
        # so a passing test proves the harness classifies, not that Ollama does.
        if "response_format" in req:
            reply = CONSTRAINED_TWO_FIELD
        elif isinstance(req.get("format"), dict):
            schema = req["format"]
            reply = CONSTRAINED_ENUM if "decision" in schema.get("properties", {}) else CONSTRAINED_TWO_FIELD
        elif req.get("format") == "json":
            reply = CONSTRAINED_JSON
        else:
            reply = TOOL_CALL_REPLY
        self._send(v1_wrap(reply) if self.path.startswith("/v1/") else reply)


def load_probe():
    spec = importlib.util.spec_from_file_location("probe", os.path.join(HERE, "probe.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:%d" % server.server_address[1]

    probe = load_probe()
    probe.BASE = base  # redirect every request at the fixture instead of a model server
    lines = []
    failures = []

    def check(name, cond, detail):
        lines.append("%-52s %s  %s" % (name, "PASS" if cond else "FAIL", detail))
        if not cond:
            failures.append(name)

    for cfg, kind, extra in probe.CONFIGS:
        rec = probe.run_one("fixture", cfg, kind, extra, 0)
        if cfg == "a_tools_only":
            check("a tools only: 1 call, name, args", rec["n_calls"] == 1 and rec.get("call_name") == "get_weather"
                  and json.loads(rec["call_args"])["city"] == "Lisbon",
                  "n_calls=%s call_name=%s args=%s" % (rec["n_calls"], rec.get("call_name"), rec.get("call_args")))
        elif cfg == "b_tools_format_two_field":
            check("b schema sent: 0 calls, JSON, two-field valid, fabricated",
                  rec["n_calls"] == 0 and rec["content_json"] and rec["content_schema_valid"]
                  and rec["fabrication_signal"],
                  "n_calls=%s json=%s valid=%s fab=%s content=%s" % (
                      rec["n_calls"], rec["content_json"], rec["content_schema_valid"],
                      rec["fabrication_signal"], rec["content"]))
        elif cfg == "c_tools_format_enum":
            check("c enum sent: parses, reference-schema check fails",
                  rec["n_calls"] == 0 and rec["content_json"] and not rec["content_schema_valid"]
                  and rec["schema_reason"] == "missing:city,temperature_c",
                  "json=%s reference_valid=%s reason=%s content=%s" % (
                      rec["content_json"], rec["content_schema_valid"], rec["schema_reason"], rec["content"]))
            check("c enum sent: reply satisfies the enum it was sent",
                  json.loads(rec["content"])["decision"] == "use_tool",
                  "decision=%s" % json.loads(rec["content"])["decision"])
        elif cfg == "d_tools_format_json":
            pseudo = json.loads(rec["content"])
            check("d bare json: parses as a pseudo-call, 0 calls",
                  rec["n_calls"] == 0 and rec["content_json"] and pseudo.get("name") == "get_weather",
                  "n_calls=%s parsed_name=%s" % (rec["n_calls"], pseudo.get("name")))
        elif cfg == "e_format_only":
            check("e no tools: constrained reply, no call, fabricated",
                  rec["n_calls"] == 0 and rec["content_schema_valid"] and rec["fabrication_signal"],
                  "n_calls=%s valid=%s fab=%s" % (rec["n_calls"], rec["content_schema_valid"],
                                                  rec["fabrication_signal"]))
        elif cfg == "f_v1_tools_response_format":
            check("f /v1 response_format: 0 calls, envelope parsed",
                  rec["endpoint"] == "/v1/chat/completions" and rec["n_calls"] == 0
                  and rec["done_reason"] == "stop" and rec["eval_count"] == 17,
                  "endpoint=%s n_calls=%s finish=%s eval=%s" % (
                      rec["endpoint"], rec["n_calls"], rec["done_reason"], rec["eval_count"]))
        check("   %s http_status" % cfg, rec["http_status"] == 200, "status=%s" % rec["http_status"])

    # The canary from the article must fire on this fixture and stay silent if
    # the constrained request also calls.
    canary_src = '''
def canary(base, model, tool, schema, prompt):
    def ask(extra):
        body = {"model": model, "stream": False,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0, "seed": 7},
                "tools": [tool], **extra}
        req = urllib.request.Request(base + "/api/chat",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        return len((d.get("message") or {}).get("tool_calls") or []), d
    bare = ask({})[0]
    constrained, resp = ask({"format": schema})
    if bare and not constrained:
        raise RuntimeError("canary fired: bare=%d constrained=%d" % (bare, constrained))
'''
    import types
    urllib_pkg = types.SimpleNamespace(request=__import__("urllib.request", fromlist=["urllib.request"]))
    ns = {"json": json, "urllib": urllib_pkg}
    exec(canary_src, ns)
    fired = False
    try:
        ns["canary"](base, "fixture", probe.TOOLS[0], probe.SCHEMAS["two_field"], probe.PROMPT)
    except RuntimeError as exc:
        fired = "canary fired" in str(exc)
    check("article canary raises on a suppressed call", fired, "RuntimeError raised=%s" % fired)

    server.shutdown()

    header = ["# fixture_test.py output (local fixture check, not a vendor measurement)",
              "# run at %s UTC; mock server on 127.0.0.1 ephemeral port; no model involved" %
              time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "# probe.py sha256 %s" % __import__("hashlib").sha256(
                  open(os.path.join(HERE, "probe.py"), "rb").read()).hexdigest(),
              ""]
    body = "\n".join(header + lines + ["", "RESULT: %d checks, %d failed" % (len(lines), len(failures))])
    with open(OUT, "w") as fh:
        fh.write(body + "\n")
    print(body)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
