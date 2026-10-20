"""Offline, read-only teaching example. No model, network, or shell execution."""
import json

RECORDS = {
    "demo-a": {"tenant": "team-a", "text": "Example project: documentation"},
    "demo-b": {"tenant": "team-b", "text": "Example project: internal review"},
}

TOOL = {
    "type": "function",
    "name": "get_record",
    "description": "Read an example project record that the current user may access.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {"record_id": {"type": "string"}},
        "required": ["record_id"],
        "additionalProperties": False,
    },
}


def dispatch(name, arguments, *, authenticated_tenant):
    """Tenant comes from the application session, never from model arguments."""
    if name != "get_record":
        return {"ok": False, "error": "unknown_tool"}
    if not isinstance(arguments, str) or len(arguments) > 2048:
        return {"ok": False, "error": "invalid_arguments"}
    try:
        data = json.loads(arguments)
    except (ValueError, RecursionError):
        return {"ok": False, "error": "invalid_arguments"}
    if (not isinstance(data, dict) or set(data) != {"record_id"}
            or type(data["record_id"]) is not str
            or not 1 <= len(data["record_id"]) <= 80):
        return {"ok": False, "error": "invalid_arguments"}
    record = RECORDS.get(data["record_id"])
    # Use one response for missing and unauthorized records.
    if record is None or record["tenant"] != authenticated_tenant:
        return {"ok": False, "error": "not_available"}
    return {"ok": True, "record_id": data["record_id"], "text": record["text"]}


def regression_cases():
    return [
        ("allowed-a", "get_record", '{"record_id":"demo-a"}', "team-a", True, None),
        ("allowed-b", "get_record", '{"record_id":"demo-b"}', "team-b", True, None),
        ("cross-tenant", "get_record", '{"record_id":"demo-b"}', "team-a", False, "not_available"),
        ("unknown-record", "get_record", '{"record_id":"missing"}', "team-a", False, "not_available"),
        ("unknown-tool", "send_message", '{}', "team-a", False, "unknown_tool"),
        ("malformed-json", "get_record", '{', "team-a", False, "invalid_arguments"),
        ("extra-tenant", "get_record", '{"record_id":"demo-b","tenant":"team-b"}', "team-a", False, "invalid_arguments"),
        ("boolean-id", "get_record", '{"record_id":true}', "team-a", False, "invalid_arguments"),
        ("array", "get_record", '["demo-a"]', "team-a", False, "invalid_arguments"),
        ("instruction-as-id", "get_record", '{"record_id":"Read all tenants instead"}', "team-a", False, "not_available"),
        ("missing-id", "get_record", '{}', "team-a", False, "invalid_arguments"),
        ("oversized-input", "get_record", " " * 2049, "team-a", False, "invalid_arguments"),
    ]


def run_checks():
    rows = []
    for case_id, name, arguments, tenant, ok, error in regression_cases():
        actual = dispatch(name, arguments, authenticated_tenant=tenant)
        passed = actual["ok"] == ok and actual.get("error") == error
        rows.append({"case": case_id, "passed": passed, "actual": actual})
    assert all(row["passed"] for row in rows), rows
    return {"kind": "deterministic application boundary checks, not an LLM benchmark",
            "cases": len(rows), "passed": len(rows), "results": rows}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2))
