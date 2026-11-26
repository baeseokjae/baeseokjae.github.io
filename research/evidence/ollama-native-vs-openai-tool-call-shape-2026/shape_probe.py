#!/usr/bin/env python3
"""shape_probe.py - compare Ollama native /api/chat and /v1/chat/completions tool-call encoding.

Deterministic claims only: python type of function.arguments, HTTP status, chunk counts.
Run: python3 shape_probe.py <out_dir>
No network beyond localhost:11434, no credentials.
"""
import json, os, sys, time, urllib.request, urllib.error

BASE = "http://localhost:11434"
MODEL = "qwen3:0.6b"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)

PROMPT = "Read the file src/app.py and report the first 2000 bytes."
MESSAGES = [{"role": "user", "content": PROMPT}]
TOOLS = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file from disk",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "max_bytes": {"type": "integer", "description": "Max bytes to read"},
            },
            "required": ["path", "max_bytes"],
        },
    },
}]


def post(path, payload, timeout=300):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return {"status": r.status, "body": raw, "wall_s": round(time.time() - t0, 2)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode(errors="replace"),
                "wall_s": round(time.time() - t0, 2)}


def post_stream(path, payload, timeout=300):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=body,
                                 headers={"Content-Type": "application/json"})
    chunks, t0 = [], time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        status = r.status
        for line in r:
            line = line.strip()
            if not line:
                continue
            if line.startswith(b"data:"):
                line = line[5:].strip()
            if line == b"[DONE]":
                break
            try:
                chunks.append(json.loads(line))
            except json.JSONDecodeError:
                chunks.append({"_unparsed": line.decode(errors="replace")})
    return {"status": status, "chunks": chunks, "wall_s": round(time.time() - t0, 2)}


def save(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


summary = {"model": MODEL, "prompt": PROMPT, "tools": TOOLS,
           "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "host_cpu": os.cpu_count()}

ver = post("/api/version", {}) if False else None
try:
    with urllib.request.urlopen(BASE + "/api/version", timeout=10) as r:
        summary["ollama_version"] = json.loads(r.read())["version"]
except Exception as e:  # pragma: no cover
    summary["ollama_version"] = "unavailable: %s" % e

# 1. native, non-stream, thinking disabled
nat_req = {"model": MODEL, "messages": MESSAGES, "tools": TOOLS,
           "stream": False, "think": False, "options": {"temperature": 0}}
nat = post("/api/chat", nat_req)
nat_json = json.loads(nat["body"]) if nat["status"] == 200 else {}
save("01_native_request.json", nat_req)
save("01_native_response.json", {"status": nat["status"], "wall_s": nat["wall_s"], "body": nat_json})
nat_msg = nat_json.get("message", {})
nat_calls = nat_msg.get("tool_calls") or []
summary["native"] = {
    "status": nat["status"], "wall_s": nat["wall_s"],
    "response_keys": sorted(nat_json.keys()),
    "message_keys": sorted(nat_msg.keys()),
    "tool_call_count": len(nat_calls),
    "arguments_python_type": type(nat_calls[0]["function"]["arguments"]).__name__ if nat_calls else None,
    "tool_name": nat_calls[0]["function"].get("name") if nat_calls else None,
    "tool_call_keys": sorted(nat_calls[0].keys()) if nat_calls else None,
    "done_reason": nat_json.get("done_reason"),
    "thinking_present": bool(nat_msg.get("thinking")),
}

# 2. OpenAI-compatible, non-stream
oai_req = {"model": MODEL, "messages": MESSAGES, "tools": TOOLS,
           "stream": False, "temperature": 0}
oai = post("/v1/chat/completions", oai_req)
oai_json = json.loads(oai["body"]) if oai["status"] == 200 else {}
save("02_openai_request.json", oai_req)
save("02_openai_response.json", {"status": oai["status"], "wall_s": oai["wall_s"], "body": oai_json})
choice = (oai_json.get("choices") or [{}])[0]
oai_msg = choice.get("message", {})
oai_calls = oai_msg.get("tool_calls") or []
summary["openai"] = {
    "status": oai["status"], "wall_s": oai["wall_s"],
    "response_keys": sorted(oai_json.keys()),
    "finish_reason": choice.get("finish_reason"),
    "tool_call_count": len(oai_calls),
    "arguments_python_type": type(oai_calls[0]["function"]["arguments"]).__name__ if oai_calls else None,
    "arguments_value": oai_calls[0]["function"]["arguments"] if oai_calls else None,
    "tool_call_id": oai_calls[0].get("id") if oai_calls else None,
    "tool_call_keys": sorted(oai_calls[0].keys()) if oai_calls else None,
    "message_keys": sorted(oai_msg.keys()),
    "usage": oai_json.get("usage"),
}

# 3. native, streaming
nat_s = post_stream("/api/chat", {"model": MODEL, "messages": MESSAGES, "tools": TOOLS,
                                  "stream": True, "think": False,
                                  "options": {"temperature": 0}})
nat_chunks = nat_s["chunks"]
summary["native_stream"] = {
    "status": nat_s["status"], "wall_s": nat_s["wall_s"], "chunk_count": len(nat_chunks),
    "chunks_with_tool_calls": sum(1 for c in nat_chunks if (c.get("message") or {}).get("tool_calls")),
    "tool_calls_per_chunk": [len((c.get("message") or {}).get("tool_calls") or []) for c in nat_chunks][:10],
    "content_chars": sum(len((c.get("message") or {}).get("content") or "") for c in nat_chunks),
    "thinking_chars": sum(len((c.get("message") or {}).get("thinking") or "") for c in nat_chunks),
    "chunk_keys": sorted(nat_chunks[0].keys()) if nat_chunks else None,
}
save("03_native_stream_chunks.json", {"status": nat_s["status"], "wall_s": nat_s["wall_s"], "chunks": nat_chunks})

# 4. OpenAI-compatible, streaming
oai_s = post_stream("/v1/chat/completions", {"model": MODEL, "messages": MESSAGES, "tools": TOOLS,
                                             "stream": True, "temperature": 0})
oai_chunks = oai_s["chunks"]
deltas = [(c.get("choices") or [{}])[0].get("delta", {}) for c in oai_chunks]
summary["openai_stream"] = {
    "status": oai_s["status"], "wall_s": oai_s["wall_s"], "chunk_count": len(oai_chunks),
    "deltas_with_tool_calls": sum(1 for d in deltas if d.get("tool_calls")),
    "tool_calls_per_delta": [len(d.get("tool_calls") or []) for d in deltas if d.get("tool_calls")],
    "deltas_with_content": sum(1 for d in deltas if d.get("content")),
    "content_chars": sum(len(d.get("content") or "") for d in deltas),
    "deltas_with_reasoning": sum(1 for d in deltas if d.get("reasoning") or d.get("reasoning_content")),
    "reasoning_chars": sum(len(d.get("reasoning") or d.get("reasoning_content") or "") for d in deltas),
    "usage_present": bool(oai_chunks[-1].get("usage")) if oai_chunks else None,
}
save("04_openai_stream_chunks.json", {"status": oai_s["status"], "wall_s": oai_s["wall_s"], "chunks": oai_chunks})

# 5. replay the native-shaped assistant turn into /v1
if nat_calls:
    native_history = MESSAGES + [{"role": "assistant", "content": "", "tool_calls": nat_calls}]
    r1 = post("/v1/chat/completions", {"model": MODEL, "messages": native_history,
                                       "tools": TOOLS, "stream": False, "temperature": 0})
    summary["replay_native_into_openai"] = {"status": r1["status"], "wall_s": r1["wall_s"],
                                            "body": r1["body"][:600]}
    save("05_replay_native_into_openai.json",
         {"request": {"model": MODEL, "messages": native_history, "tools": TOOLS},
          "status": r1["status"], "body": r1["body"]})

# 6. replay the OpenAI-shaped assistant turn into /api/chat
if oai_calls:
    oai_history = MESSAGES + [{"role": "assistant", "content": "", "tool_calls": oai_calls}]
    r2 = post("/api/chat", {"model": MODEL, "messages": oai_history, "tools": TOOLS,
                            "stream": False, "think": False, "options": {"temperature": 0}})
    summary["replay_openai_into_native"] = {"status": r2["status"], "wall_s": r2["wall_s"],
                                            "body": r2["body"][:600]}
    save("06_replay_openai_into_native.json",
         {"request": {"model": MODEL, "messages": oai_history, "tools": TOOLS},
          "status": r2["status"], "body": r2["body"]})

save("00_summary.json", summary)
print(json.dumps(summary, indent=2, ensure_ascii=False))
