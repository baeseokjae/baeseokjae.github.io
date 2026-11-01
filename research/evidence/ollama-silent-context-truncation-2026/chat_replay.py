#!/usr/bin/env python3
"""Re-run the two chat cells of the truncation probe and keep the full replies.

The first run (runs.csv, 2026-10-31 15:24-15:26 UTC) truncated each reply to 120
characters for display. This capture repeats the same two chat requests and
stores the complete response objects so the quoted replies are auditable.

Usage: python3 capture_chat.py --out <path>/chat-replies.json
"""
import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone

BASE = "http://127.0.0.1:11434"
MODEL = "qwen2.5:0.5b"
PAD = ("filler sentence used only to consume context window budget without "
       "adding meaning; it is repeated to reach the target prompt length. ")


def pad(words):
    text = PAD
    while len(text.split()) < words:
        text += PAD
    return text


def chat_messages():
    msgs = [{"role": "system", "content": "Your codename is BANANA-42. Begin every reply with that codename on its own line."}]
    for i in range(1, 13):
        role = "user" if i % 2 else "assistant"
        msgs.append({"role": role, "content": f"MSG-{i:02d}\n{pad(45)}"})
    msgs.append({"role": "user", "content": "List every MSG-xx label that is present in this conversation, in order, one per line, and nothing else."})
    return msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    msgs = chat_messages()
    records = []
    for num_ctx in (2048, 512):
        body = {"model": MODEL, "messages": msgs, "stream": False,
                "options": {"num_ctx": num_ctx, "temperature": 0, "num_predict": 32}}
        req = urllib.request.Request(BASE + "/api/chat", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        started = time.time()
        started_iso = datetime.now(timezone.utc).isoformat()
        with urllib.request.urlopen(req, timeout=420) as response:
            data = json.load(response)
        wall_ms = round((time.time() - started) * 1000)
        reply = data.get("message", {}).get("content", "")
        records.append({
            "fixture": f"chat-replay-{num_ctx}",
            "request_num_ctx": num_ctx,
            "started_at": started_iso,
            "wall_ms": wall_ms,
            "response": data,
            "reply_full": reply,
            "codename_present": "BANANA-42" in reply,
        })
        print(json.dumps({"num_ctx": num_ctx, "prompt_eval_count": data.get("prompt_eval_count"),
                          "eval_count": data.get("eval_count"), "wall_ms": wall_ms,
                          "reply": reply}, ensure_ascii=False))
    with open(args.out, "w") as handle:
        json.dump({"model": MODEL, "endpoint": "/api/chat", "captured_at":
                   datetime.now(timezone.utc).isoformat(), "records": records}, handle,
                  indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
