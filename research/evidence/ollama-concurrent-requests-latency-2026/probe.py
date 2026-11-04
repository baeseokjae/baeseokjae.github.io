#!/usr/bin/env python3
"""Bounded concurrency probe for Ollama /api/generate.

Stdlib only (urllib + threading). One fixed prompt, temperature 0,
num_predict fixed. Sends N simultaneous requests, records per-request
timings from the response body and appends sanitized rows to a JSONL
file.

Usage:
  python3 probe.py --label A-n2 --base-url http://127.0.0.1:11434 \
      --concurrency 2 --reps 5 --out results.jsonl [--num-predict 64]
"""
import argparse
import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PROMPT = ("Write a plain-text checklist of five steps for backing up a small "
          "PostgreSQL database on Linux. One short line per step. No preamble.")


def one_request(base_url, model, num_predict):
    payload = {
        "model": model,
        "prompt": PROMPT,
        "stream": False,
        "options": {"temperature": 0, "num_predict": num_predict, "seed": 42},
        "keep_alive": "5m",
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        base_url + "/api/generate", data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read().decode())
            status = resp.status
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.read().decode()[:300],
                "wall_s": round(time.perf_counter() - t0, 3)}
    wall = time.perf_counter() - t0
    return {
        "status": status,
        "wall_s": round(wall, 3),
        "total_duration_ns": body.get("total_duration"),
        "load_duration_ns": body.get("load_duration"),
        "prompt_eval_duration_ns": body.get("prompt_eval_duration"),
        "eval_duration_ns": body.get("eval_duration"),
        "eval_count": body.get("eval_count"),
        "prompt_eval_count": body.get("prompt_eval_count"),
        "done_reason": body.get("done_reason"),
        "response_chars": len(body.get("response", "")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:11434")
    ap.add_argument("--model", default="qwen2.5:0.5b")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--num-predict", type=int, default=64)
    ap.add_argument("--out", default="results.jsonl")
    args = ap.parse_args()

    # warm-up: one serial request so the model is loaded before measurements
    warm = one_request(args.base_url, args.model, args.num_predict)

    rows = []
    for rep in range(args.reps):
        lock = threading.Lock()
        results = []
        barrier = threading.Barrier(args.concurrency)

        def worker():
            barrier.wait()
            r = one_request(args.base_url, args.model, args.num_predict)
            with lock:
                results.append(r)

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            for _ in range(args.concurrency):
                ex.submit(worker)
        wall = time.perf_counter() - t0

        ok = [r for r in results if r.get("status") == 200]
        total_tokens = sum(r.get("eval_count") or 0 for r in ok)
        row = {
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "label": args.label,
            "base_url": args.base_url,
            "model": args.model,
            "concurrency": args.concurrency,
            "rep": rep,
            "batch_wall_s": round(wall, 3),
            "requests_ok": len(ok),
            "aggregate_tokens_per_s": round(total_tokens / wall, 2) if wall else None,
            "requests": results,
        }
        rows.append(row)
        with open(args.out, "a") as f:
            f.write(json.dumps(row) + "\n")

    print(json.dumps({"label": args.label, "rows": len(rows),
                      "warmup": warm, "first_row": rows[0]}, indent=2))


if __name__ == "__main__":
    main()
