#!/usr/bin/env python3
"""Bounded tool-selection probe against a local Ollama /api/chat.

stdlib only (urllib). Appends one JSON line per call to results.jsonl so a
deadline hit leaves usable partial evidence. No SDK, no network beyond
127.0.0.1:11434.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:11434"
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results.jsonl")
DEADLINE = float(os.environ.get("PROBE_DEADLINE_EPOCH", "0")) or None

TARGET = {
    "type": "function",
    "function": {
        "name": "create_ticket",
        "description": "Create a single support ticket in the tracker.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short ticket title"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Ticket priority",
                },
            },
            "required": ["title", "priority"],
        },
    },
}

FILLERS = [
    ("search_kb", "Search the internal knowledge base for an article.", {"query": {"type": "string"}}),
    ("get_weather", "Return the current weather for a city.", {"city": {"type": "string"}}),
    ("send_email", "Send an email message to one recipient.", {"to": {"type": "string"}, "body": {"type": "string"}}),
    ("list_orders", "List recent orders for a customer.", {"customer_id": {"type": "string"}}),
    ("refund_order", "Issue a refund for an order.", {"order_id": {"type": "string"}}),
    ("translate_text", "Translate text between languages.", {"text": {"type": "string"}, "target_lang": {"type": "string"}}),
    ("summarize_doc", "Summarize a document by id.", {"doc_id": {"type": "string"}}),
    ("schedule_meeting", "Book a meeting on a calendar.", {"attendee": {"type": "string"}, "when": {"type": "string"}}),
    ("lookup_user", "Look up a user profile by email.", {"email": {"type": "string"}}),
    ("create_invoice", "Create an invoice line item.", {"amount": {"type": "number"}, "currency": {"type": "string"}}),
    ("delete_file", "Delete a file by path.", {"path": {"type": "string"}}),
    ("run_query", "Run a read-only SQL query.", {"sql": {"type": "string"}}),
    ("check_stock", "Check warehouse stock for a SKU.", {"sku": {"type": "string"}}),
    ("post_status", "Post a status update to a channel.", {"channel": {"type": "string"}, "text": {"type": "string"}}),
    ("parse_invoice", "Parse an uploaded invoice PDF.", {"file_id": {"type": "string"}}),
    ("assign_owner", "Assign an issue to a teammate.", {"issue_id": {"type": "string"}, "owner": {"type": "string"}}),
    ("estimate_shipping", "Estimate shipping cost and days.", {"zip": {"type": "string"}, "weight_kg": {"type": "number"}}),
    ("list_incidents", "List open incidents by severity.", {"severity": {"type": "string"}}),
    ("close_incident", "Close an incident with a resolution note.", {"incident_id": {"type": "string"}, "resolution": {"type": "string"}}),
    ("fetch_metrics", "Fetch a metric time series.", {"metric": {"type": "string"}, "window": {"type": "string"}}),
    ("create_webhook", "Register a webhook URL.", {"url": {"type": "string"}, "event": {"type": "string"}}),
    ("rotate_key", "Rotate an API key.", {"key_id": {"type": "string"}}),
    ("export_csv", "Export a report to CSV.", {"report": {"type": "string"}}),
]

PROMPTS = {
    "explicit": "Call the create_ticket tool for a customer who says their invoice is wrong. "
                "Title it 'Invoice mismatch'. Priority is high.",
    "ambiguous": "A customer reports a billing problem that needs a human to follow up. "
                 "Record it in the tracker for the support team.",
}


def build_tools(n):
    tools = [TARGET]
    for name, desc, props in FILLERS[: max(0, n - 1)]:
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": {"type": "object", "properties": props,
                               "required": list(props.keys())},
            },
        })
    return tools


def post(path, payload, timeout):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode())
        return {"ok": True, "status": 200, "body": body, "wall_s": round(time.time() - t0, 3)}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error_body": e.read().decode()[:800],
                "wall_s": round(time.time() - t0, 3)}
    except Exception as e:  # timeout / conn reset
        return {"ok": False, "status": None, "error_body": f"{type(e).__name__}: {e}",
                "wall_s": round(time.time() - t0, 3)}


def validate(args):
    """Explicit per-key schema validation for create_ticket."""
    out = {"parsed": args is not None, "has_title": False, "has_priority": False,
           "priority_in_enum": False, "valid": False}
    if not isinstance(args, dict):
        return out
    t = args.get("title")
    p = args.get("priority")
    out["has_title"] = isinstance(t, str) and len(t.strip()) > 0
    out["has_priority"] = isinstance(p, str) and len(p.strip()) > 0
    out["priority_in_enum"] = p in ("low", "medium", "high", "urgent")
    out["valid"] = out["has_title"] and out["has_priority"] and out["priority_in_enum"]
    return out


def one_call(model, n_tools, shape, rep, phase="single", messages=None, timeout=180):
    if DEADLINE and time.time() > DEADLINE:
        return None
    tools = build_tools(n_tools)
    msgs = messages or [{"role": "user", "content": PROMPTS[shape]}]
    payload = {
        "model": model,
        "messages": msgs,
        "tools": tools,
        "stream": False,
        "options": {"temperature": 0, "seed": 7,
                    "num_predict": int(os.environ.get("PROBE_NUM_PREDICT", "128"))},
    }
    r = post("/api/chat", payload, timeout)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": model, "n_tools": n_tools, "prompt_shape": shape,
        "rep": rep, "phase": phase,
        "http_status": r["status"], "ok": r["ok"], "wall_s": r["wall_s"],
    }
    if not r["ok"]:
        rec["error"] = r.get("error_body")
        rec["correct_tool"] = False
        rec["failure"] = "http_error"
        return rec, None

    b = r["body"]
    msg = b.get("message") or {}
    calls = msg.get("tool_calls") or []
    content = msg.get("content") or ""
    rec.update({
        "done_reason": b.get("done_reason"),
        "n_calls": len(calls),
        "content_len": len(content),
        "eval_count": b.get("eval_count"),
        "prompt_eval_count": b.get("prompt_eval_count"),
        "eval_duration_ns": b.get("eval_duration"),
        "total_duration_ns": b.get("total_duration"),
        "load_duration_ns": b.get("load_duration"),
    })
    if b.get("eval_count") and b.get("eval_duration"):
        rec["tok_per_s"] = round(b["eval_count"] / (b["eval_duration"] / 1e9), 2)

    if not calls:
        rec["fn_name"] = None
        rec["correct_tool"] = False
        rec["failure"] = "no_tool_call" if not content.strip() else "content_only"
        return rec, msg

    fn = ((calls[0].get("function") or {}) if isinstance(calls[0], dict) else {})
    name = fn.get("name")
    args = fn.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = None
    rec["fn_name"] = name
    rec["args"] = args
    rec["correct_tool"] = name == "create_ticket"
    rec["schema"] = validate(args)
    if not rec["correct_tool"]:
        rec["failure"] = "wrong_tool"
    elif not rec["schema"]["valid"]:
        rec["failure"] = "malformed_args"
    else:
        rec["failure"] = None
    return rec, msg


def main():
    model = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    counts = [int(x) for x in (sys.argv[3].split(",") if len(sys.argv) > 3 else ["1", "4", "8"])]
    shapes = sys.argv[4].split(",") if len(sys.argv) > 4 else ["explicit"]
    loop = (sys.argv[5] == "loop") if len(sys.argv) > 5 else False

    # warm load so the first measured call is not a cold-start artifact
    post("/api/chat", {"model": model, "messages": [{"role": "user", "content": "hi"}],
                       "stream": False, "options": {"num_predict": 8}}, 180)

    with open(RESULTS, "a") as f:
        for n in counts:
            for shape in shapes:
                for rep in range(reps):
                    out = one_call(model, n, shape, rep)
                    if out is None:
                        print(json.dumps({"stopped": "deadline", "at_n_tools": n}), flush=True)
                        return
                    rec, _ = out
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    print(json.dumps({k: rec.get(k) for k in
                                      ("model", "n_tools", "prompt_shape", "rep",
                                       "correct_tool", "failure", "wall_s", "done_reason")}),
                          flush=True)
        if loop:
            # 3-turn loop: call -> tool result -> second call must reference it
            msgs = [{"role": "user", "content": PROMPTS["explicit"]}]
            rec1, msg1 = one_call(model, 4, "explicit", 0, phase="loop_turn1", messages=msgs)
            if rec1:
                f.write(json.dumps(rec1) + "\n")
                f.flush()
                print(json.dumps({"loop_turn1": rec1.get("failure") or "ok"}), flush=True)
            if msg1 and msg1.get("tool_calls"):
                tc = msg1["tool_calls"][0]
                msgs = msgs + [
                    {"role": "assistant", "content": msg1.get("content") or "",
                     "tool_calls": [tc]},
                    {"role": "tool", "tool_name": "create_ticket",
                     "content": json.dumps({"ticket_id": "TCK-4471", "status": "open",
                                            "created": "2026-11-10T08:00:00Z"})},
                    {"role": "user", "content": "Confirm the ticket id you just created."},
                ]
                rec2, msg2 = one_call(model, 4, "explicit", 0, phase="loop_turn2", messages=msgs)
                if rec2:
                    txt = ((msg2 or {}).get("content") or "")
                    rec2["carried_ticket_id"] = "TCK-4471" in txt
                    rec2["reply_excerpt"] = txt[:200]
                    f.write(json.dumps(rec2) + "\n")
                    f.flush()
                    print(json.dumps({"loop_turn2_carried": rec2["carried_ticket_id"],
                                      "n_calls": rec2.get("n_calls"),
                                      "wall_s": rec2.get("wall_s")}), flush=True)


if __name__ == "__main__":
    main()
