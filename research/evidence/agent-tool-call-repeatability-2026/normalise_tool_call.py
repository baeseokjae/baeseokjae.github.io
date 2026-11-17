#!/usr/bin/env python3
"""Normalise an emitted tool call into a stable, comparable form.

The point is narrow. A harness that compares tool calls as serialised text
asserts on JSON key order, which carries no meaning and which the measurement
in research/evidence/agent-tool-call-repeatability-2026/run.jsonl shows can
change between identical requests. This helper discards key order (and the
dict/JSON-string representation difference) and keeps the parts that carry
meaning: the tool name and the argument values.

normalise_tool_call(message, required=None) -> (name, args, digest, problems)

- message: the assistant message object from an Ollama /api/chat response,
  i.e. the dict that carries "tool_calls".
- required: argument names the calling code depends on. Any that are absent are
  reported in problems. Nothing is invented to fill them.
- digest: sha256 over the canonical JSON of {"name", "arguments"} with sorted
  keys and no whitespace. Equal digests mean equal name+arguments.

No network access. Standard library only.
"""
import hashlib
import json


def normalise_tool_call(message, required=None):
    calls = (message or {}).get("tool_calls") or []
    if not calls:
        return None, {}, None, ["no_tool_call"]
    function = calls[0].get("function") or {}
    name = function.get("name")
    args = function.get("arguments")
    problems = []

    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            problems.append("arguments_not_json")
            args = {}
    if not isinstance(args, dict):
        problems.append("arguments_not_object")
        args = {}

    for key in required or []:
        if key not in args:
            problems.append("missing:" + key)

    canonical = json.dumps(
        {"name": name, "arguments": args}, sort_keys=True, separators=(",", ":")
    )
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    return name, args, digest, problems


# --- self-test: the four shapes a normaliser has to survive ------------------
TESTS = [
    # 1. plain semantic call, arguments already an object
    ({"tool_calls": [{"function": {"name": "stat_path",
                                   "arguments": {"path": "docs/config.md", "mode": "hash"}}}]},
     None, []),
    # 2. same call, different key order (the observed byte flip)
    ({"tool_calls": [{"function": {"name": "stat_path",
                                   "arguments": {"mode": "hash", "path": "docs/config.md"}}}]},
     None, []),
    # 3. missing required argument
    ({"tool_calls": [{"function": {"name": "stat_path", "arguments": {"mode": "hash"}}}]},
     ["path", "mode"], ["missing:path"]),
    # 4. arguments emitted as a JSON string
    ({"tool_calls": [{"function": {"name": "stat_path",
                                   "arguments": '{"path": "docs/config.md", "mode": "hash"}'}}]},
     None, []),
    # 5. no tool call at all
    ({"content": "I cannot do that."}, None, ["no_tool_call"]),
]


def main():
    digests = []
    for index, (message, required, expected) in enumerate(TESTS, 1):
        name, args, digest, problems = normalise_tool_call(message, required)
        ok = problems == expected
        digests.append(digest)
        print(
            "case %d %s name=%s args=%s problems=%s"
            % (index, "PASS" if ok else "FAIL", name, json.dumps(args, sort_keys=True), problems)
        )
        if not ok:
            raise SystemExit("self-test failed on case %d: expected %s" % (index, expected))

    # cases 1, 2 and 4 are the same call written three ways and must collapse
    same = digests[0] == digests[1] == digests[3]
    print("collapsed_cases_1_2_4=%s digest=%s" % (same, (digests[0] or "")[:16]))
    print("missing_argument_differs_from_complete=%s" % (digests[2] != digests[0]))
    if not same or digests[2] == digests[0]:
        raise SystemExit("normalisation did not separate the cases")


if __name__ == "__main__":
    main()
