#!/usr/bin/env python3
"""Bounded probe: does a JSON `format` constraint suppress tool calling on a
self-hosted Ollama server? stdlib only, no third-party deps.

Records one NDJSON row per request to results.jsonl (append-only) and a
summary.json. Total wall-clock budget is enforced by DEADLINE_S; partial
results are kept.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:11434"
OUT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(OUT, "results.jsonl")
SUMMARY = os.path.join(OUT, "summary.json")
DEADLINE_S = float(os.environ.get("PROBE_DEADLINE_S", "150"))
T0 = time.time()

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current air temperature for a city from the weather service.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]

# The answer exists only behind the tool: the model cannot know it.
PROMPT = ("What is the current temperature in Lisbon right now? "
          "You must use the get_weather tool to find out.")

SCHEMAS = {
    "two_field": {
        "type": "object",
        "properties": {"city": {"type": "string"}, "temperature_c": {"type": "number"}},
        "required": ["city", "temperature_c"],
    },
    "enum_only": {
        "type": "object",
        "properties": {"decision": {"type": "string", "enum": ["use_tool", "answer_directly"]}},
        "required": ["decision"],
    },
}

CONFIGS = [
    ("a_tools_only", "api", {"tools": TOOLS}),
    ("b_tools_format_two_field", "api", {"tools": TOOLS, "format": SCHEMAS["two_field"]}),
    ("c_tools_format_enum", "api", {"tools": TOOLS, "format": SCHEMAS["enum_only"]}),
    ("d_tools_format_json", "api", {"tools": TOOLS, "format": "json"}),
    ("e_format_only", "api", {"format": SCHEMAS["two_field"]}),
    ("f_v1_tools_response_format", "v1", {"tools": TOOLS,
                                          "response_format": {"type": "json_schema",
                                                              "json_schema": {"name": "weather",
                                                                              "schema": SCHEMAS["two_field"]}}}),
]

MODELS = os.environ.get("PROBE_MODELS", "qwen2.5:0.5b").split(",")
REPS = int(os.environ.get("PROBE_REPS", "3"))


def post(path, payload, timeout):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # timeout, connection reset
        return -1, repr(e)


def count_numberish(text):
    """True if content carries a temperature value the tool alone could supply."""
    import re
    return bool(re.search(r"\b\d{1,3}(\.\d+)?\s*(°\s*[CF]|C\b|F\b|degrees)", text or "", re.I)
                or re.search(r'"(temperature_c|temperature|temp)"\s*:\s*-?\d', text or "", re.I))


def validate(obj):
    if not isinstance(obj, dict):
        return False, "not_object"
    miss = [k for k in ("city", "temperature_c") if k not in obj]
    if miss:
        return False, "missing:" + ",".join(miss)
    if not isinstance(obj.get("temperature_c"), (int, float)):
        return False, "temperature_c_not_number"
    return True, "ok"


def run_one(model, cfg, kind, extra, rep):
    payload = {"model": model, "messages": [{"role": "user", "content": PROMPT}],
               "stream": False, "options": {"temperature": 0, "seed": 7}}
    payload.update(extra)
    path = "/api/chat" if kind == "api" else "/v1/chat/completions"
    t = time.time()
    status, raw = post(path, payload, timeout=60)
    wall = round(time.time() - t, 3)
    rec = {"ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "model": model, "config": cfg, "endpoint": path, "rep": rep,
           "http_status": status, "wall_s": wall}
    try:
        d = json.loads(raw)
    except Exception:
        rec.update(parse_error=True, raw_head=raw[:300])
        return rec
    if kind == "api":
        msg = d.get("message") or {}
        content = msg.get("content") or ""
        calls = msg.get("tool_calls") or []
        rec["done_reason"] = d.get("done_reason")
        rec["eval_count"] = d.get("eval_count")
    else:
        ch = (d.get("choices") or [{}])[0]
        msg = ch.get("message") or {}
        content = msg.get("content") or ""
        calls = msg.get("tool_calls") or []
        rec["done_reason"] = ch.get("finish_reason")
        rec["eval_count"] = (d.get("usage") or {}).get("completion_tokens")
    rec["n_calls"] = len(calls)
    if calls:
        fn = (calls[0].get("function") or {})
        rec["call_name"] = fn.get("name")
        args = fn.get("arguments")
        rec["call_args"] = args if isinstance(args, str) else json.dumps(args)
    rec["content_len"] = len(content)
    rec["content"] = content[:600]
    rec["content_json"] = False
    try:
        obj = json.loads(content)
        rec["content_json"] = True
        ok, why = validate(obj)
        rec["content_schema_valid"] = ok
        rec["schema_reason"] = why
    except Exception:
        rec["content_schema_valid"] = False
        rec["schema_reason"] = "not_json"
    rec["fabrication_signal"] = bool(rec["n_calls"] == 0 and count_numberish(content))
    return rec


def main():
    meta = {"models": MODELS, "reps": REPS, "deadline_s": DEADLINE_S,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "host_ollama_version": json.loads(
                urllib.request.urlopen(BASE + "/api/version", timeout=5).read())["version"]}
    with open(os.path.join(OUT, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    done = 0
    with open(RESULTS, "a") as fh:
        for model in MODELS:
            for cfg, kind, extra in CONFIGS:
                for rep in range(REPS):
                    if time.time() - T0 > DEADLINE_S:
                        print("DEADLINE reached after %d runs" % done)
                        return
                    rec = run_one(model, cfg, kind, extra, rep)
                    fh.write(json.dumps(rec) + "\n")
                    fh.flush()
                    done += 1
                    print("%-28s %-14s r%d http=%s calls=%d valid=%s wall=%.2fs"
                          % (cfg, model, rep, rec.get("http_status"), rec.get("n_calls", -1),
                             rec.get("content_schema_valid"), rec.get("wall_s", -1)))
    print("completed %d runs in %.1fs" % (done, time.time() - T0))


if __name__ == "__main__":
    main()
