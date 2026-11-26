#!/usr/bin/env python3
"""Normalise an assistant tool-call message from either Ollama surface.

/api/chat returns tool_call.function.arguments as a JSON object; the
OpenAI-compatible /v1/chat/completions returns the same call as a JSON string.
This adapter accepts both, validates the decoded mapping against the tool
schema that was sent, and returns (name, {arg: value}).

Run `python3 normalise_tool_call.py --selftest` for the four observed cases.
Standard library only.
"""
import json
import sys

# The schema that accompanied every request in the 2026-11-15 probe.
READ_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "max_bytes": {"type": "integer"},
    },
    "required": ["path", "max_bytes"],
}


class ToolCallShapeError(ValueError):
    """The message carries no usable single tool call."""


def _decode(args):
    """Return the argument mapping from an object or a JSON string."""
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        decoded = json.loads(args)  # raises json.JSONDecodeError on bad JSON
        if not isinstance(decoded, dict):
            raise ToolCallShapeError("arguments decoded to %s, not an object" % type(decoded).__name__)
        return decoded
    raise ToolCallShapeError("arguments is %s" % type(args).__name__)


def _unwrap(mapping):
    """Undo the one nested wrapper models occasionally invent."""
    if "arguments" in mapping and isinstance(mapping["arguments"], (dict, str)) and len(mapping) <= 2:
        return _decode(mapping["arguments"])
    if "function" in mapping and isinstance(mapping["function"], dict):
        inner = mapping["function"]
        if "arguments" in inner:
            return _decode(inner["arguments"])
    return mapping


def _validate(mapping, schema):
    required = schema.get("required", [])
    missing = [key for key in required if key not in mapping]
    if missing:
        raise ToolCallShapeError("missing required argument(s): %s" % ", ".join(missing))
    for key, spec in schema.get("properties", {}).items():
        if key not in mapping:
            continue
        want = spec.get("type")
        value = mapping[key]
        if want == "string" and not isinstance(value, str):
            raise ToolCallShapeError("%s should be a string, got %s" % (key, type(value).__name__))
        if want == "integer" and (isinstance(value, bool) or not isinstance(value, int)):
            raise ToolCallShapeError("%s should be an integer, got %s" % (key, type(value).__name__))
    return mapping


def normalise_tool_call(message, schema=READ_FILE_SCHEMA):
    """message: assistant message dict from /api/chat or /v1/chat/completions."""
    calls = message.get("tool_calls") or []
    if len(calls) != 1:
        raise ToolCallShapeError("expected exactly 1 tool call, found %d" % len(calls))
    call = calls[0]
    function = call.get("function") or {}
    name = function.get("name")
    if not name:
        raise ToolCallShapeError("tool call has no function name")
    arguments = _validate(_unwrap(_decode(function.get("arguments"))), schema)
    return name, arguments


CASES = [
    (
        "native object arguments (as returned by /api/chat on 0.20.3)",
        {"role": "assistant", "content": "", "tool_calls": [
            {"id": "call_3nn9ernp", "function": {"index": 0, "name": "read_file",
             "arguments": {"path": "src/app.py", "max_bytes": 2000}}}]},
        ("read_file", {"path": "src/app.py", "max_bytes": 2000}),
    ),
    (
        "OpenAI-compatible string arguments (as returned by /v1/chat/completions)",
        {"role": "assistant", "content": "", "tool_calls": [
            {"id": "call_im2sam5h", "index": 0, "type": "function",
             "function": {"name": "read_file",
                          "arguments": "{\"path\":\"src/app.py\",\"max_bytes\":2000}"}}]},
        ("read_file", {"path": "src/app.py", "max_bytes": 2000}),
    ),
    (
        "model-invented nested wrapper around string arguments",
        {"role": "assistant", "content": "", "tool_calls": [
            {"id": "call_x", "function": {"name": "read_file",
             "arguments": {"arguments": "{\"path\":\"src/app.py\",\"max_bytes\":100}"}}}]},
        ("read_file", {"path": "src/app.py", "max_bytes": 100}),
    ),
    (
        "empty tool_calls (a truncated or prose turn)",
        {"role": "assistant", "content": "I will read it."},
        ToolCallShapeError,
    ),
]


def selftest():
    failures = 0
    for label, message, expected in CASES:
        try:
            got = normalise_tool_call(message)
            ok = got == expected
        except ToolCallShapeError as exc:
            got = "ToolCallShapeError: %s" % exc
            ok = expected is ToolCallShapeError
        failures += 0 if ok else 1
        print("%-4s %s -> %r" % ("ok" if ok else "FAIL", label, got))
    print("%d/%d cases passed" % (len(CASES) - failures, len(CASES)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else 0)
