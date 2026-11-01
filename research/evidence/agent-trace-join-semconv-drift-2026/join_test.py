#!/usr/bin/env python3
"""Join test for mixed-producer agent traces. Pure stdlib, no network, no SDK.

Reads the three source-derived span fixtures in ./fixtures/ and runs three
dashboards' queries three times - once keyed on `gen_ai.system`, once on
`gen_ai.provider.name`, and once through the join-key contract in the article
(explicit fallback chain from registry spelling to vendor-native identity).

It prints, per (key mode, query), how many of the fixture spans a query
actually returns. Nothing here asserts a fleet-wide failure rate: the fixtures
are documented-attribute inventories, not captures.

Usage:
    python3 join_test.py            # human-readable table
    python3 join_test.py --json OUT # table + machine-readable run record
"""
import argparse
import hashlib
import json
import pathlib
import time
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
FIXTURE_FILES = ["claude-code.json", "google-adk.json", "openai-agents-sdk.json"]

# --- key modes -------------------------------------------------------------
# Each mode maps a span record to (provider_identity, agent_identity).
# `None` means "this key cannot identify a fleet member for this span".


def _attr(span, name):
    return span.get("attributes", {}).get(name)


def _native(span, name):
    return span.get("span_data", {}).get(name)


def key_system(span):
    provider = _attr(span, "gen_ai.system")
    agent = _attr(span, "gen_ai.agent.name")
    return provider, agent


def key_provider_name(span):
    provider = _attr(span, "gen_ai.provider.name")
    agent = _attr(span, "gen_ai.agent.name")
    return provider, agent


def key_contract(span):
    # Contract clause 1: registry spelling first, then the deprecated spelling,
    # then the producer's own identity field, in that order.
    provider = (
        _attr(span, "gen_ai.provider.name")
        or _attr(span, "gen_ai.system")
        or _native(span, "provider")
    )
    # Contract clause 3: agent identity, registry spelling first, then vendor-native.
    agent = (
        _attr(span, "gen_ai.agent.name")
        or _attr(span, "agent_id")
        or _native(span, "agent_name")
    )
    return provider, agent


MODES = [
    ("gen_ai.system", key_system),
    ("gen_ai.provider.name", key_provider_name),
    ("contract_v1", key_contract),
]

# --- queries --------------------------------------------------------------
# required(span) -> bool : does this span carry the fields the dashboard needs?


def q_cost_by_agent(span):
    tokens = _attr(span, "gen_ai.usage.input_tokens")
    if tokens is None:
        native_usage = _native(span, "usage")
        tokens = native_usage.get("input_tokens") if isinstance(native_usage, dict) else None
    return tokens is not None


def q_tool_failure_rate(span):
    tool = _attr(span, "gen_ai.tool.name") or _native(span, "name")
    if tool is None:
        return False
    failed = _attr(span, "error.type") is not None or _attr(span, "otel.status_code") == "ERROR"
    return failed


def q_context_utilisation(span):
    return _attr(span, "gen_ai.request.max_tokens") is not None and _attr(
        span, "gen_ai.usage.input_tokens"
    ) is not None


QUERIES = [
    ("cost by agent", q_cost_by_agent),
    ("tool failure rate", q_tool_failure_rate),
    ("context utilisation", q_context_utilisation),
]


def load():
    spans = []
    for name in FIXTURE_FILES:
        doc = json.loads((FIXTURES / name).read_text())
        for span in doc["spans"]:
            spans.append(
                {
                    "producer": doc["producer"],
                    "label": doc["label"],
                    "span_id": span["span_id"],
                    "attributes": span.get("attributes", {}),
                    "span_data": span.get("span_data", {}),
                }
            )
    return spans


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args()
    started = time.monotonic()

    spans = load()
    results = []
    lines = []
    for mode_name, mapper in MODES:
        identified = []
        for span in spans:
            provider, agent = mapper(span)
            if provider is not None:
                identified.append(span["span_id"])
        lines.append(
            "%-20s identity coverage: %d/%d spans  %s"
            % (mode_name, len(identified), len(spans), ",".join(identified))
        )
        for query_name, predicate in QUERIES:
            matched = [
                s["span_id"]
                for s in spans
                if mapper(s)[0] is not None and mapper(s)[1] is not None and predicate(s)
            ]
            results.append(
                {
                    "key_mode": mode_name,
                    "query": query_name,
                    "matched_spans": matched,
                    "matched": len(matched),
                    "out_of": len(spans),
                    "producers_matched": sorted({s["producer"] for s in spans if s["span_id"] in matched}),
                }
            )
            lines.append(
                "  %-22s %d/%d spans matched  %s"
                % (query_name, len(matched), len(spans), ",".join(matched) or "-")
            )
    elapsed = time.monotonic() - started
    print("\n".join(lines))
    print("elapsed_seconds=%.3f fixture_spans=%d" % (elapsed, len(spans)))

    if args.json_out:
        record = {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "tool": "join_test.py",
            "tool_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            "elapsed_seconds": round(elapsed, 3),
            "fixture_spans": len(spans),
            "fixtures": {
                name: hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
                for name in FIXTURE_FILES
            },
            "methodology": (
                "Deterministic offline join over three source-derived span fixtures "
                "(documented attribute inventories, not runtime captures). For each key mode the "
                "tool resolves provider identity and agent identity, then counts how many spans a "
                "dashboard query would return. No span was emitted by a live SDK; no network access."
            ),
            "results": results,
        }
        pathlib.Path(args.json_out).write_text(json.dumps(record, indent=2) + "\n")
        print("wrote " + args.json_out)


if __name__ == "__main__":
    main()
