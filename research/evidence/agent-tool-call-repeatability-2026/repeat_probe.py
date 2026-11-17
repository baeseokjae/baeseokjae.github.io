#!/usr/bin/env python3
"""Bounded, round-robin tool-call repeatability probe (research r1, 2026-11-15).

Differs from the first attempt in one way: calls are scheduled round-robin across
the four prompt shapes instead of conditioning-then-N, so a wall-clock cut cannot
leave a condition with zero samples. Append-only JSONL; hard budget; no signals.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:11434/api/chat"
D = os.environ.get("PROBE_DIR", ".")
OUT = os.path.join(D, "run.jsonl")
LOG = os.path.join(D, "probe.log")
BUDGET_S = float(os.environ.get("PROBE_BUDGET_S", "170"))
MAX_ROUNDS = int(os.environ.get("PROBE_MAX_ROUNDS", "8"))
MODEL = os.environ.get("PROBE_MODEL", "qwen3:0.6b")

TOOLS = [{
    "type": "function",
    "function": {
        "name": "stat_path",
        "description": "Stat a path inside the repository and return its size and sha256.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Repo-relative path"},
                "mode": {"type": "string", "enum": ["stat", "read", "hash"]},
                "max_bytes": {"type": "integer", "description": "Max bytes to read"},
            },
            "required": ["path", "mode"],
        },
    },
}]

ASK = "Check whether docs/config.md exists and get its hash. Use the tool."

REPO_LISTING = "Repository listing (paths only):\n" + "\n".join(
    f"{i:03d}  src/module_{i}/handlers/endpoint_{i}.py" for i in range(1, 41)
) + "\n" + "".join(f"{i:03d}  docs/page_{i}.md\n" for i in range(1, 45))

HISTORY_TURN = [
    {"role": "user", "content": "List the files under docs/. Use the tool."},
    {"role": "assistant", "content": "", "tool_calls": [{
        "function": {"name": "stat_path", "arguments": {"path": "docs", "mode": "stat"}}
    }]},
    {"role": "tool", "content": json.dumps({"entries": ["docs/config.md", "docs/page_1.md"], "mode": "stat"})},
]


def build(cond):
    if cond == "S1":
        return [{"role": "user", "content": ASK}], 0.0
    if cond == "S2":
        return HISTORY_TURN + [{"role": "user", "content": ASK}], 0.0
    if cond == "S3":
        return [{"role": "user", "content": REPO_LISTING + "\n\n" + ASK}], 0.0
    if cond == "S4":
        return [{"role": "user", "content": ASK}], 0.7
    raise ValueError(cond)


def post(messages, temperature, seed=42):
    body = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "tools": TOOLS,
        "options": {"temperature": temperature, "seed": seed,
                    "num_predict": 80, "num_ctx": 4096},
    }
    req = urllib.request.Request(BASE, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=150) as r:
        return json.loads(r.read().decode())


def norm(tc):
    fn = tc.get("function", {}) if isinstance(tc, dict) else {}
    args = fn.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {"__unparsed__": args}
    return fn.get("name"), (args if isinstance(args, dict) else {"__type__": type(args).__name__})


def main():
    t0 = time.time()
    done = 0
    with open(OUT, "a", encoding="utf-8") as fh, open(LOG, "a", encoding="utf-8") as log:
        conds = [c.strip() for c in os.environ.get("PROBE_ORDER", "S1,S2,S3,S4").split(",") if c.strip()]
        for rnd in range(MAX_ROUNDS):
            for cond in conds:
                if time.time() - t0 > BUDGET_S:
                    log.write(f"BUDGET_EXHAUSTED after {done} calls round={rnd}\n")
                    log.flush()
                    print(f"budget exhausted after {done} calls in round {rnd}")
                    return
                msgs, temp = build(cond)
                start = time.time()
                err = None
                payload = None
                try:
                    payload = post(msgs, temp)
                except Exception as exc:
                    err = f"{type(exc).__name__}: {exc}"
                wall = round(time.time() - start, 3)
                rec = {"model": MODEL, "condition": cond, "temperature": temp,
                       "seed": 42, "round": rnd,
                       "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start)),
                       "wall_s": wall, "error": err}
                if payload:
                    msg = payload.get("message", {}) or {}
                    tcs = msg.get("tool_calls") or []
                    rec["tool_call_count"] = len(tcs)
                    rec["content_prefix"] = (msg.get("content") or "")[:200]
                    rec["eval_count"] = payload.get("eval_count")
                    rec["prompt_eval_count"] = payload.get("prompt_eval_count")
                    rec["total_duration_ns"] = payload.get("total_duration")
                    rec["done_reason"] = payload.get("done_reason")
                    if tcs:
                        name, args = norm(tcs[0])
                        rec["tool_name"] = name
                        rec["arguments"] = args
                        rec["key_order"] = list(args.keys())
                        rec["sha256_byte"] = hashlib.sha256(json.dumps(args).encode()).hexdigest()
                        rec["sha256_semantic"] = hashlib.sha256(
                            json.dumps(args, sort_keys=True).encode()).hexdigest()
                        rec["raw_arguments"] = tcs[0].get("function", {}).get("arguments")
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                done += 1
                log.write(f"{cond} r{rnd} wall={wall}s err={err} tcs={rec.get('tool_call_count')}\n")
                log.flush()
    print(f"completed {done} calls in {round(time.time() - t0, 1)}s")


if __name__ == "__main__":
    main()
