#!/usr/bin/env python3
"""Bounded probe: what does an Ollama server do when the prompt exceeds num_ctx?

Two request shapes are exercised against a local Ollama daemon:

  chat      /api/chat    -- labelled messages MSG-01..MSG-12 plus a system
                            message carrying a codename. Records
                            prompt_eval_count, eval_count, wall_ms and the
                            raw reply so a reader can see which labels the
                            model echoed back.
  generate  /api/generate-- one raw prompt string with a head sentinel and a
                            tail sentinel. Records the same metrics plus
                            whether each sentinel appears in the reply.

The script does not decide which tokens the server kept; it only records what
the API reported and what the model produced. Retention claims belong to the
server source (server/prompt.go chatPrompt) and to the prompt_eval_count
comparison between a fitting and a non-fitting request.

Usage:
  python3 scripts/ollama_ctx_probe.py --out research/evidence/<slug>/runs.csv \
      --fixtures research/evidence/<slug>/prompt-fixtures.jsonl

Every request is bounded by --timeout seconds; a cell that times out is
recorded as status=timeout rather than retried.
"""
import argparse
import csv
import json
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:11434"
MODEL = "qwen2.5:0.5b"
PAD = ("filler sentence used only to consume context window budget without "
       "adding meaning; it is repeated to reach the target prompt length. ")


def pad(words):
    text = PAD
    while len(text.split()) < words:
        text += PAD
    return text


def post(path, body, timeout):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.load(response)
    return data, round((time.time() - started) * 1000)


def chat_messages():
    msgs = [{"role": "system", "content": "Your codename is BANANA-42. Begin every reply with that codename on its own line."}]
    for i in range(1, 13):
        role = "user" if i % 2 else "assistant"
        msgs.append({"role": role, "content": f"MSG-{i:02d}\n{pad(45)}"})
    msgs.append({"role": "user", "content": "List every MSG-xx label that is present in this conversation, in order, one per line, and nothing else."})
    return msgs


def generate_prompt(head, tail, words):
    return (f"{head}\n{pad(words)}\n"
            "Reply with the two sentinel strings you were given, one per line, nothing else.\n"
            f"{tail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--timeout", type=int, default=420)
    args = ap.parse_args()

    msgs = chat_messages()
    head, tail = "SENTINEL-HEAD-7731", "SENTINEL-TAIL-9917"
    gprompt = generate_prompt(head, tail, 420)

    fixtures = [
        {"id": "chat-fits-2048", "shape": "chat", "num_ctx": 2048, "rep": 1,
         "note": "control cell; the same conversation must fit without truncation"},
        {"id": "chat-clamp-512-r1", "shape": "chat", "num_ctx": 512, "rep": 1},
        {"id": "chat-clamp-512-r2", "shape": "chat", "num_ctx": 512, "rep": 2},
        {"id": "gen-sentinel-1024", "shape": "generate", "num_ctx": 1024, "rep": 1,
         "head": head, "tail": tail},
        {"id": "gen-sentinel-256", "shape": "generate", "num_ctx": 256, "rep": 1,
         "head": head, "tail": tail},
    ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fx = Path(args.fixtures)
    fx.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in fixtures))

    rows = []
    for f in fixtures:
        options = {"num_ctx": f["num_ctx"], "temperature": 0, "num_predict": 32}
        try:
            if f["shape"] == "chat":
                data, wall = post("/api/chat", {"model": MODEL, "messages": msgs,
                                                "stream": False, "options": options},
                                  args.timeout)
                reply = data.get("message", {}).get("content", "")
                extra = {"codename_ok": "BANANA-42" in reply}
            else:
                data, wall = post("/api/generate", {"model": MODEL, "prompt": gprompt,
                                                    "stream": False, "options": options},
                                  args.timeout)
                reply = data.get("response", "")
                extra = {"head_ok": head in reply, "tail_ok": tail in reply}
            row = {"fixture": f["id"], "shape": f["shape"], "num_ctx": f["num_ctx"],
                   "rep": f["rep"], "status": "ok",
                   "prompt_eval_count": data.get("prompt_eval_count"),
                   "eval_count": data.get("eval_count"),
                   "wall_ms": wall,
                   "reply_head": " ".join(reply.split())[:120]}
            row.update(extra)
        except Exception as exc:  # timeout or transport error: record, do not retry
            row = {"fixture": f["id"], "shape": f["shape"], "num_ctx": f["num_ctx"],
                   "rep": f["rep"], "status": "timeout", "prompt_eval_count": "",
                   "eval_count": "", "wall_ms": "", "reply_head": type(exc).__name__}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    fields = ["fixture", "shape", "num_ctx", "rep", "status", "prompt_eval_count",
              "eval_count", "wall_ms", "codename_ok", "head_ok", "tail_ok", "reply_head"]
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
