#!/usr/bin/env python3
"""tool_schema_token_audit.py — marginal prompt-token cost of tool definitions on Ollama.

Posts /api/chat with stream=false against one pinned local model, a fixed user
message, and tool sets of 0/1/3/6/12 tools in a terse and a verbose form, then
repeats the 6-tool terse cell through the OpenAI-compatible endpoint.

Records prompt_eval_count, prompt_eval_cached_count, eval_count, total_duration
and wall time per request to JSONL. Every row is flushed immediately so an
interrupted run still leaves usable partial evidence.

Environment: Ollama 0.20.3, qwen3:0.6b, CPU-only, temperature 0, num_ctx 8192,
num_predict 8. Usage: python3 tool_schema_token_audit.py --out <empty dir> [--repeats 3] [--timeout 260]

Two operational notes:
  * The JSONL is opened in append mode, so pass a fresh, empty --out directory
    per run; otherwise rows from earlier runs accumulate in fixture-raw.jsonl and
    in the summary.
  * --timeout is the client-side socket timeout for one request. The recorded
    2026-11-12 run used 260 s: the verbose_12 attempt is stamped 260.1 s after
    the previous record. This constant previously read 120, which did not match
    the run; 260 is now the default and the value in force is printed at start.
    A timed-out request is written as an error row and the run continues.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HOST = os.environ.get("OLLAMA_HOST_URL", "http://127.0.0.1:11434")
MODEL = "qwen3:0.6b"
USER_MESSAGE = "Reply with the single word: ready."
NUM_CTX = 8192
NUM_PREDICT = 8
REQUEST_TIMEOUT = float(os.environ.get("AUDIT_REQUEST_TIMEOUT", "260"))
TOTAL_DEADLINE_S = float(os.environ.get("AUDIT_DEADLINE_S", "420"))

# Twelve tools. Sets of N always use the first N entries, so the 1/3/6/12 cells
# are nested and the slope across them is attributable to added definitions.
TERSE = [
    ("get_weather", "Get current weather for a city.",
     {"city": ("string", "City name")}, ["city"]),
    ("search_files", "Search a directory tree for a glob pattern.",
     {"root": ("string", "Directory to search"), "pattern": ("string", "Glob pattern")}, ["root", "pattern"]),
    ("read_file", "Read a text file and return its contents.",
     {"path": ("string", "File path")}, ["path"]),
    ("run_query", "Run a read-only SQL query and return rows.",
     {"sql": ("string", "SELECT statement")}, ["sql"]),
    ("send_email", "Send a plain-text email to one recipient.",
     {"to": ("string", "Recipient address"), "body": ("string", "Message body")}, ["to", "body"]),
    ("create_ticket", "Create an issue ticket in the tracker.",
     {"title": ("string", "Ticket title"), "priority": ("integer", "1 low to 5 high")}, ["title"]),
    ("list_events", "List calendar events in a date range.",
     {"start": ("string", "ISO start date"), "end": ("string", "ISO end date")}, ["start", "end"]),
    ("convert_currency", "Convert an amount between two currencies.",
     {"amount": ("number", "Amount to convert"), "currency": ("string", "ISO 4217 target")}, ["amount", "currency"]),
    ("translate_text", "Translate text into a target language.",
     {"text": ("string", "Text to translate"), "target": ("string", "ISO 639-1 code")}, ["text", "target"]),
    ("upload_asset", "Upload a local file to object storage.",
     {"path": ("string", "Local path"), "bucket": ("string", "Target bucket")}, ["path"]),
    ("fetch_url", "Fetch one URL and return its text body.",
     {"url": ("string", "Absolute URL")}, ["url"]),
    ("summarize_doc", "Summarise a document to a target length.",
     {"doc_id": ("string", "Document id"), "words": ("integer", "Target word count")}, ["doc_id"]),
]

VERBOSE_DESCRIPTION = (
    "This tool performs a complete read-and-report cycle for its domain and is intended to be preferred "
    "over ad-hoc shell work when the agent needs a structured, auditable result. It validates its input "
    "against the supplied schema, retries transient transport failures twice with exponential backoff, "
    "and returns a JSON object whose keys are documented in the schema. The caller should call it once "
    "per logical operation and must not batch unrelated requests into a single invocation, because each "
    "invocation is logged separately for cost attribution and is charged against the caller's turn budget. "
    "If the requested entity does not exist the tool returns an empty result set rather than an error."
)


def terse_tool(index):
    name, description, props, required = TERSE[index]
    return {"type": "function", "function": {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": {k: {"type": v[0], "description": v[1]} for k, v in props.items()},
            "required": required,
        },
    }}


def verbose_tool(index):
    name, _description, props, required = TERSE[index]
    nested = {
        "type": "object",
        "description": "Optional execution controls for this invocation.",
        "properties": {
            "timeout_ms": {"type": "integer", "minimum": 100, "maximum": 60000, "default": 10000,
                           "description": "Hard wall-clock limit for the operation in milliseconds."},
            "retry": {
                "type": "object",
                "description": "Retry policy applied to transient transport failures.",
                "properties": {
                    "max_attempts": {"type": "integer", "minimum": 1, "maximum": 5, "default": 2},
                    "backoff_ms": {"type": "integer", "minimum": 0, "default": 250},
                    "retry_on": {"type": "array", "items": {"type": "string",
                                                            "enum": ["timeout", "rate_limit", "connection_reset"]}},
                },
                "required": ["max_attempts"],
                "additionalProperties": False,
            },
            "dry_run": {"type": "boolean", "default": False,
                        "description": "Validate and plan the call without performing side effects."},
        },
        "additionalProperties": False,
    }
    parameters = {
        "type": "object",
        "description": "Arguments for the %s tool. All string values are UTF-8." % name,
        "properties": {k: {"type": v[0], "description": v[1]} for k, v in props.items()},
        "required": required,
        "additionalProperties": False,
    }
    parameters["properties"]["options"] = nested
    return {"type": "function", "function": {
        "name": name,
        "description": VERBOSE_DESCRIPTION,
        "parameters": parameters,
    }}


def tool_set(count, verbosity):
    builder = terse_tool if verbosity == "terse" else verbose_tool
    return [builder(i) for i in range(count)]


def post(path, payload):
    data = json.dumps(payload).encode()
    request = urllib.request.Request(HOST + path, data=data,
                                     headers={"Content-Type": "application/json"})
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        body = json.loads(response.read().decode())
    return body, time.monotonic() - started, data


def native_row(cell, verbosity, count, repeat):
    payload = {"model": MODEL, "messages": [{"role": "user", "content": USER_MESSAGE}],
               "stream": False,
               "options": {"num_ctx": NUM_CTX, "temperature": 0, "num_predict": NUM_PREDICT}}
    tools = tool_set(count, verbosity) if count else []
    if tools:
        payload["tools"] = tools
    try:
        body, wall, raw = post("/api/chat", payload)
    except Exception as exc:  # a timeout is data, not a crash: record and continue
        return {"surface": "native_api_chat", "cell": cell, "verbosity": verbosity if count else "none",
                "tool_count": count, "repeat": repeat, "error": type(exc).__name__ + ": " + str(exc),
                "prompt_eval_count": None, "at": datetime.now(timezone.utc).isoformat()}
    return {
        "surface": "native_api_chat", "cell": cell, "verbosity": verbosity if count else "none",
        "tool_count": count, "repeat": repeat,
        "request_sha256": hashlib.sha256(raw).hexdigest(),
        "tools_json_bytes": len(json.dumps(tools).encode()) if tools else 0,
        "prompt_eval_count": body.get("prompt_eval_count"),
        "prompt_eval_cached_count": body.get("prompt_eval_cached_count"),
        "eval_count": body.get("eval_count"),
        "total_duration_ns": body.get("total_duration"),
        "done_reason": body.get("done_reason"),
        "wall_s": round(wall, 3),
        "at": datetime.now(timezone.utc).isoformat(),
        "message_text": (body.get("message") or {}).get("content", ""),
    }


def openai_row(count, repeat):
    payload = {"model": MODEL, "messages": [{"role": "user", "content": USER_MESSAGE}],
               "stream": False, "temperature": 0, "max_tokens": NUM_PREDICT,
               "tools": tool_set(count, "terse")}
    body, wall, raw = post("/v1/chat/completions", payload)
    usage = body.get("usage") or {}
    return {
        "surface": "openai_v1_chat_completions", "cell": "terse_6_cross_surface", "verbosity": "terse",
        "tool_count": count, "repeat": repeat,
        "request_sha256": hashlib.sha256(raw).hexdigest(),
        "tools_json_bytes": len(json.dumps(payload["tools"]).encode()),
        "prompt_eval_count": usage.get("prompt_tokens"),
        "prompt_eval_cached_count": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
        "eval_count": usage.get("completion_tokens"),
        "total_duration_ns": None, "done_reason": (body.get("choices") or [{}])[0].get("finish_reason"),
        "wall_s": round(wall, 3),
        "at": datetime.now(timezone.utc).isoformat(),
        "message_text": ((body.get("choices") or [{}])[0].get("message") or {}).get("content", ""),
        "note": "num_ctx is not settable here; the server default context applies. Compare prompt_tokens, not num_ctx.",
    }


def describe(row):
    """One progress line per request; an error row has no wall time or count."""
    if row.get("error"):
        return "error=%s" % row["error"]
    return "prompt_eval_count=%s wall=%ss" % (row.get("prompt_eval_count"), row.get("wall_s"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".", help="directory for JSONL/CSV output")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=None,
                        help="client timeout per request in seconds (default 260, the value the recorded run used)")
    args = parser.parse_args()
    global REQUEST_TIMEOUT
    if args.timeout is not None:
        REQUEST_TIMEOUT = args.timeout
    os.makedirs(args.out, exist_ok=True)
    jsonl_path = os.path.join(args.out, "fixture-raw.jsonl")
    csv_path = os.path.join(args.out, "fixture-summary.csv")
    print(json.dumps({"request_timeout_s": REQUEST_TIMEOUT, "repeats": args.repeats,
                      "jsonl": jsonl_path, "jsonl_mode": "append"}), flush=True)
    deadline = time.monotonic() + TOTAL_DEADLINE_S
    rows = []
    plan = [("tools_0", "none", 0)]
    for count in (1, 3, 6, 12):
        plan.append(("terse_%d" % count, "terse", count))
    for count in (1, 3, 6, 12):
        plan.append(("verbose_%d" % count, "verbose", count))

    with open(jsonl_path, "a", encoding="utf-8") as handle:
        for cell, verbosity, count in plan:
            for repeat in range(1, args.repeats + 1):
                if time.monotonic() > deadline:
                    print(json.dumps({"stopped": "deadline", "cell": cell, "repeat": repeat}))
                    break
                row = native_row(cell, verbosity, count, repeat)
                rows.append(row)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                print("%-12s r%d %s" % (cell, repeat, describe(row)), flush=True)
            else:
                continue
            break

        # Cross-surface check last, so a short deadline loses only this cell.
        if time.monotonic() <= deadline:
            for repeat in range(1, args.repeats + 1):
                if time.monotonic() > deadline:
                    print(json.dumps({"stopped": "deadline", "cell": "terse_6_cross_surface", "repeat": repeat}))
                    break
                try:
                    row = openai_row(6, repeat)
                except Exception as exc:  # a timeout is data here too, not a crash
                    row = {"surface": "openai_v1_chat_completions", "cell": "terse_6_cross_surface",
                           "verbosity": "terse", "tool_count": 6, "repeat": repeat,
                           "error": type(exc).__name__ + ": " + str(exc),
                           "prompt_eval_count": None, "at": datetime.now(timezone.utc).isoformat()}
                rows.append(row)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                print("%-12s r%d %s" % ("openai_6", repeat, describe(row)), flush=True)

    # One aggregation implementation, published as aggregate_fixture.py, writes
    # the summary CSV from the same records. A missing sibling file is not fatal.
    try:
        from aggregate_fixture import aggregate_rows, write_summary
    except ImportError:  # pragma: no cover - only when the sibling file is absent
        print(json.dumps({"csv_skipped": "aggregate_fixture.py not found next to the driver",
                          "jsonl": jsonl_path}), flush=True)
    else:
        with open(csv_path, "w", newline="", encoding="utf-8") as handle:
            write_summary(aggregate_rows(rows), handle)
        print(json.dumps({"jsonl": jsonl_path, "csv": csv_path, "rows": len(rows)}))


if __name__ == "__main__":
    main()
