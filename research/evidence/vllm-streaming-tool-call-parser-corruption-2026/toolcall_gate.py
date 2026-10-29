#!/usr/bin/env python3
"""Client-side gate for OpenAI-compatible streaming tool calls.

Purpose: decide, before your agent executes anything, whether the tool calls a
client reassembled from an SSE stream (a) round-trip as JSON, (b) carry every
argument the declared schema requires, and (c) keep the declared JSON types.
It also reports how many calls arrived, because a merged call is usually a
correct call count of N-1.

This is a client fixture check. It does not import, patch, or measure vLLM, and
its fixtures are constructed, not captured from a model server.

Run:  python3 toolcall_gate.py --selftest
      python3 toolcall_gate.py --fixture fixtures/sse_parallel_toolcalls.json \
          --tools fixtures/tool_schema.json
Exit: 0 when every clean split passes and every constructed corruption is
      caught; 1 otherwise; 2 on a usage/IO error.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

JSON_TYPES = {
    str: "string", bool: "boolean", int: "integer",
    float: "number", list: "array", dict: "object", type(None): "null",
}


def wire_events(payloads):
    """Wrap JSON payload strings as OpenAI-style SSE events (bytes)."""
    return b"".join(b"data: " + p.encode() + b"\n\n" for p in payloads) + b"data: [DONE]\n\n"


def read_events(chunks):
    """Byte-chunk-tolerant SSE reader: chunks may split anywhere, even mid-UTF-8.

    The buffer is decoded only after a complete event has been delimited, so a
    multi-byte character split across two TCP reads is not corrupted here.
    """
    buf, events = b"", []
    for chunk in chunks:
        buf += chunk
        while b"\n\n" in buf:
            raw, buf = buf.split(b"\n\n", 1)
            data = b"\n".join(
                line[len(b"data:"):].lstrip() for line in raw.splitlines()
                if line.startswith(b"data:")
            )
            if not data or data.strip() == b"[DONE]":
                continue
            events.append(json.loads(data.decode("utf-8")))
    if buf.strip():
        raise ValueError("stream ended inside an event (truncated SSE frame)")
    return events


def reassemble(events):
    """Accumulate delta.tool_calls by index, as the OpenAI Python client does."""
    calls = {}
    for event in events:
        for choice in event.get("choices", []):
            for delta in choice.get("delta", {}).get("tool_calls", []) or []:
                index = delta.get("index", 0)
                call = calls.setdefault(index, {"index": index, "id": None, "name": "", "arguments": ""})
                if delta.get("id"):
                    call["id"] = delta["id"]
                fn = delta.get("function") or {}
                if fn.get("name"):
                    call["name"] += fn["name"]
                if fn.get("arguments") is not None:
                    call["arguments"] += fn["arguments"]
    return [calls[i] for i in sorted(calls)]


def type_name(value):
    return JSON_TYPES.get(type(value), type(value).__name__)


def validate(calls, tools, expected_calls):
    issues = []

    def add(code, call, detail):
        issues.append({"code": code, "call": call, "detail": detail})

    if expected_calls is not None and len(calls) != expected_calls:
        add("CALL_COUNT_MISMATCH", None, f"expected {expected_calls} calls, reassembled {len(calls)}")
    for call in calls:
        label = call["name"] or f"index {call['index']}"
        spec = tools.get(call["name"])
        if spec is None:
            add("UNKNOWN_FUNCTION", label, "function name is not declared in the request")
            continue
        text = call["arguments"]
        if not text.strip():
            add("EMPTY_ARGUMENTS", label, "arguments string is empty or whitespace")
            continue
        try:
            args = json.loads(text, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
        except ValueError as exc:
            add("ARGUMENTS_NOT_JSON", label, f"arguments do not parse as JSON: {exc}; tail={text[-40:]!r}")
            continue
        if not isinstance(args, dict):
            add("ARGUMENTS_NOT_OBJECT", label, "arguments parsed to a non-object JSON value")
            continue
        props = spec.get("properties", {})
        for name in spec.get("required", []):
            if name not in args:
                add("MISSING_REQUIRED", label, f"required argument {name!r} is absent")
        for name, value in args.items():
            declared = props.get(name, {}).get("type")
            if declared is None:
                continue
            allowed = declared if isinstance(declared, list) else [declared]
            actual = type_name(value)
            if actual not in allowed:
                add("TYPE_MISMATCH", label,
                    f"argument {name!r} declared {declared}, received {actual} {value!r}")
            if "enum" in props.get(name, {}) and value not in props[name]["enum"]:
                add("ENUM_MISMATCH", label, f"argument {name!r} value {value!r} is outside the enum")
    return issues


def check(chunks, tools, expected_calls=None):
    calls = reassemble(read_events(chunks))
    return {"calls": calls, "issues": validate(calls, tools, expected_calls)}


# --- constructed fixtures ---------------------------------------------------
# Two parallel calls. Call 0 carries string, integer, boolean and array
# arguments; call 1 is a second function. The payloads below are hand-written
# OpenAI-compatible delta chunks, not model output.
CLEAN_PAYLOADS = [
    json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 0, "id": "call_a", "type": "function", "function": {"name": "get_weather", "arguments": '{"city": "Pari'}}]}}]}),
    json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 0, "function": {"arguments": 's", "days": 3, "metric": true, "tags": ["a", "b"]}'}}]}}]}),
    json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 1, "id": "call_b", "type": "function", "function": {"name": "search_docs", "arguments": '{"query": "ss'}}]}}]}),
    json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 1, "function": {"arguments": 'e framing", "limit": 5}'}}]}}]}),
    json.dumps({"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]}),
]


def variants():
    """Three corruption classes the reports describe, plus a dropped argument."""
    merged = copy.deepcopy(CLEAN_PAYLOADS)
    head = json.loads(merged[0])
    second = json.loads(merged[2])
    head["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"] += \
        second["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"]
    merged[0] = json.dumps(head)
    merged[2] = json.dumps({"choices": [{"index": 0, "delta": {}}]})
    merged[3] = json.dumps({"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]})

    truncated = copy.deepcopy(CLEAN_PAYLOADS)
    truncated[1] = json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 0, "function": {"arguments": 's", "days": 3, "metric": tr'}}]}}]})

    retyped = copy.deepcopy(CLEAN_PAYLOADS)
    retyped[1] = json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 0, "function": {"arguments": 's", "days": "3", "metric": "true", "tags": "[\\"a\\", \\"b\\"]"}'}}]}}]})

    dropped = copy.deepcopy(CLEAN_PAYLOADS)
    dropped[1] = json.dumps({"choices": [{"index": 0, "delta": {"tool_calls": [
        {"index": 0, "function": {"arguments": 's", "tags": ["a", "b"]}'}}]}}]})

    return {"merged_calls": merged, "truncated_arguments": truncated,
            "retyped_arguments": retyped, "dropped_non_string_arguments": dropped}


def selftest(tools_path):
    tools = json.loads(Path(tools_path).read_text())
    cases, failures = [], []
    clean = wire_events(CLEAN_PAYLOADS)
    boundary_failures = []
    for offset in range(len(clean) + 1):
        result = check([clean[:offset], clean[offset:]], tools, expected_calls=2)
        if result["issues"]:
            boundary_failures.append({"offset": offset, "issues": result["issues"]})
    cases.append({"case": "clean_stream_split_at_every_byte_offset",
                  "offsets": len(clean) + 1, "failures": len(boundary_failures),
                  "detected": not boundary_failures})
    if boundary_failures:
        failures.append(cases[-1])

    for name, payloads in variants().items():
        wire = wire_events(payloads)
        result = check([wire], tools, expected_calls=2)
        codes = sorted({i["code"] for i in result["issues"]})
        cases.append({"case": name, "detected": bool(codes), "codes": codes,
                      "call_count": len(result["calls"])})
        if not codes:
            failures.append(cases[-1])
    return {"cases": cases, "failures": failures,
            "summary": {"cases": len(cases), "failed": len(failures)}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture")
    ap.add_argument("--tools", default=str(Path(__file__).with_name("fixtures") / "tool_schema.json"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--expected-calls", type=int)
    args = ap.parse_args()
    try:
        if args.selftest:
            report = selftest(args.tools)
            print(json.dumps(report, indent=2))
            return 0 if not report["failures"] else 1
        if not args.fixture:
            ap.error("--fixture or --selftest is required")
        payloads = json.loads(Path(args.fixture).read_text())["payloads"]
        tools = json.loads(Path(args.tools).read_text())
        result = check([wire_events(payloads)], tools, args.expected_calls)
        print(json.dumps(result, indent=2))
        return 0 if not result["issues"] else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
