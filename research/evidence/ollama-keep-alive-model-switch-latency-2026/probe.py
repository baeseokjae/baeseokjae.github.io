#!/usr/bin/env python3
"""Alternating two-model probe against a dedicated Ollama instance.

Usage: probe.py <base_url> <config_label> <keep_alive> <calls> <out.jsonl>

Alternates coder (text) and vision model, num_predict=64, temperature=0, seed=42,
captures /api/ps before and after every call. Stdlib only.
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE, LABEL, KEEP_ALIVE, CALLS, OUT = (
    sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])

CODER = "qwen2.5:0.5b"
VISION = "qwen3-vl:2b"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return json.loads(r.read().decode())


def post(path, payload, timeout=300):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode()), r.status, time.time() - t0, None
    except urllib.error.HTTPError as e:
        return None, e.code, time.time() - t0, e.read().decode()[:400]
    except Exception as e:  # noqa: BLE001
        return None, None, time.time() - t0, repr(e)


def resident():
    ps = get("/api/ps")
    return [{"name": m.get("name") or m.get("model"),
             "size_vram": m.get("size_vram", 0),
             "size": m.get("size", 0),
             "expires_at": m.get("expires_at")} for m in ps.get("models", [])]


def ka_value():
    raw = KEEP_ALIVE
    if raw == "0":
        return 0
    if raw == "-1":
        return -1
    return raw  # e.g. "5m"


out = open(OUT, "a", encoding="utf-8")
for i in range(CALLS):
    model = CODER if i % 2 == 0 else VISION
    before = resident()
    body, status, wall, err = post("/api/generate", {
        "model": model,
        "prompt": "Reply with the single word ok.",
        "stream": False,
        "keep_alive": ka_value(),
        "options": {"num_predict": 64, "temperature": 0, "seed": 42},
    })
    after = resident()
    rec = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": LABEL, "keep_alive": KEEP_ALIVE, "call_index": i,
        "model": model, "http_status": status, "wall_s": round(wall, 4),
        "error": err,
        "resident_before": [m["name"] for m in before],
        "resident_after": [m["name"] for m in after],
        "ps_size_vram_after_mb": {m["name"]: round(m["size_vram"] / 1048576)
                                  for m in after},
    }
    if body:
        for k in ("total_duration", "load_duration", "prompt_eval_count",
                  "prompt_eval_duration", "eval_count", "eval_duration",
                  "done_reason"):
            rec[k] = body.get(k)
        rec["response_text"] = (body.get("response") or "").strip()[:60]
        td, ld = body.get("total_duration") or 0, body.get("load_duration") or 0
        rec["load_share"] = round(ld / td, 4) if td else None
    out.write(json.dumps(rec) + "\n")
    out.flush()
    print(json.dumps({k: rec.get(k) for k in
                      ("config", "call_index", "model", "http_status",
                       "load_duration", "total_duration", "load_share",
                       "resident_after")}), flush=True)
out.close()
