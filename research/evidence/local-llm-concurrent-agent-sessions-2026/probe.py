#!/usr/bin/env python3
"""Bounded concurrency probe against a local Ollama server.

Records, per request: wall-clock ms, HTTP status, verbatim error text,
response character length, eval counts. Total deadline enforced; partial
results are flushed to JSON after every cell.

Env: OLLAMA_PROBE_BASE (default http://127.0.0.1:11434), OLLAMA_PROBE_LABEL,
OLLAMA_PROBE_DEADLINE (epoch seconds), OLLAMA_PROBE_OUT, OLLAMA_PROBE_NUMCTX
"""
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

BASE = os.environ.get("OLLAMA_PROBE_BASE", "http://127.0.0.1:11434")
LABEL = os.environ.get("OLLAMA_PROBE_LABEL", "default")
OUT = os.environ.get("OLLAMA_PROBE_OUT", "probe.json")
DEADLINE = float(os.environ.get("OLLAMA_PROBE_DEADLINE", str(time.time() + 150)))
NUMCTX = int(os.environ.get("OLLAMA_PROBE_NUMCTX", "2048"))
MODEL = os.environ.get("OLLAMA_PROBE_MODEL", "qwen2.5:0.5b")

PROMPT = (
    "You are a coding assistant inside an automated pipeline. "
    "Write a numbered list of exactly six short sentences about Python virtual environments. "
    "Do not use markdown headings."
)

results = {
    "label": LABEL,
    "base": BASE,
    "model": MODEL,
    "num_ctx": NUMCTX,
    "num_predict": 64,
    "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "cells": [],
    "notes": [
        "Wall time is measured client-side around a single non-streaming /api/generate call.",
        "num_predict=64, temperature=0, single fixed prompt; CPU-only host.",
        "Ollama version is recorded in the accompanying method.md; flags are whatever the "
        "server process was started with, not changed per request.",
    ],
}


def flush():
    tmp = OUT + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(results, fh, indent=1)
    os.replace(tmp, OUT)


def one_request():
    body = json.dumps(
        {
            "model": MODEL,
            "prompt": PROMPT,
            "stream": False,
            "keep_alive": "5m",
            "options": {"num_ctx": NUMCTX, "num_predict": 64, "temperature": 0, "seed": 7},
        }
    ).encode()
    req = urllib.request.Request(
        BASE + "/api/generate", data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    rec = {"wall_ms": None, "status": None, "error": None, "resp_chars": None,
           "eval_count": None, "prompt_eval_count": None, "total_duration_ns": None}
    try:
        with urllib.request.urlopen(req, timeout=max(5, DEADLINE - time.time())) as r:
            raw = r.read()
            rec["status"] = r.status
            try:
                d = json.loads(raw)
                rec["resp_chars"] = len(d.get("response", ""))
                rec["eval_count"] = d.get("eval_count")
                rec["prompt_eval_count"] = d.get("prompt_eval_count")
                rec["total_duration_ns"] = d.get("total_duration")
                rec["done_reason"] = d.get("done_reason")
            except Exception:
                rec["resp_chars"] = len(raw)
    except urllib.error.HTTPError as e:
        rec["status"] = e.code
        try:
            rec["error"] = e.read().decode("utf-8", "replace")[:400]
        except Exception:
            rec["error"] = "<unreadable body>"
    except Exception as e:  # noqa: BLE001
        rec["status"] = 0
        rec["error"] = f"{type(e).__name__}: {e}"[:400]
    rec["wall_ms"] = round((time.time() - t0) * 1000, 1)
    return rec


def cell(n, rep):
    if time.time() + max(6, n * 3) > DEADLINE:
        return None
    recs = [None] * n
    threads = []

    def worker(i):
        recs[i] = one_request()

    # single barrier so all threads start in the same instant
    gate = threading.Barrier(n + 1)

    def runner(i):
        gate.wait()
        recs[i] = one_request()

    for i in range(n):
        t = threading.Thread(target=runner, args=(i,))
        t.start()
        threads.append(t)
    gate.wait()
    for t in threads:
        t.join()
    walls = sorted(r["wall_ms"] for r in recs if r)
    entry = {
        "n": n,
        "rep": rep,
        "requests": recs,
        "min_ms": walls[0] if walls else None,
        "max_ms": walls[-1] if walls else None,
        "statuses": sorted({r["status"] for r in recs if r}),
    }
    results["cells"].append(entry)
    flush()
    print(json.dumps({k: entry[k] for k in ("n", "rep", "min_ms", "max_ms", "statuses")}), flush=True)
    return entry


mode = sys.argv[1] if len(sys.argv) > 1 else "main"
try:
    if mode == "warmup":
        print("warmup", json.dumps(one_request()), flush=True)
    else:
        plan = [(1, 1), (2, 1), (4, 1), (1, 2), (4, 2)]
        if mode == "n4":
            plan = [(4, 1), (4, 2), (1, 1)]
        for n, rep in plan:
            if time.time() + 5 > DEADLINE:
                results["truncated"] = True
                break
            cell(n, rep)
finally:
    results["ended_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    flush()
    print("saved", OUT, flush=True)
