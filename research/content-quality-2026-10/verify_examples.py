"""Offline checks of teaching examples. No API calls, API keys, or SDK required."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace as NS
from cost_calculator import calculate
from responses_example import answer, INSTRUCTIONS
from tool_boundary import run_checks


class FakeClient:
    def __init__(self, responses):
        self.queue = list(responses)
        self.requests = []
        self.responses = self

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.queue.pop(0)


def response(identifier, calls=(), text="", status="completed"):
    return NS(id=identifier, status=status, output=list(calls), output_text=text)


def call(identifier="call-a", arguments='{"record_id":"demo-a"}'):
    return NS(type="function_call", call_id=identifier, name="get_record", arguments=arguments)


def expect_error(fn):
    try:
        fn()
    except (RuntimeError, ValueError):
        return
    raise AssertionError("Expected an error")


def main():
    checks = run_checks()
    client = FakeClient([response("r1", [call()]), response("r2", text="Documentation")])
    assert answer(client, "example-model", "demo-a", authenticated_tenant="team-a") == "Documentation"
    first, second = client.requests
    assert "previous_response_id" not in first
    assert second["previous_response_id"] == "r1"
    assert first["instructions"] == second["instructions"] == INSTRUCTIONS
    assert second["input"][0]["call_id"] == "call-a"
    assert json.loads(second["input"][0]["output"])["ok"] is True
    duplicate = FakeClient([response("r1", [call(), call()])])
    expect_error(lambda: answer(duplicate, "example", "q", authenticated_tenant="team-a"))
    loop = FakeClient([response("r1", [call("a")]), response("r2", [call("b")])])
    expect_error(lambda: answer(loop, "example", "q", authenticated_tenant="team-a", max_requests=2))
    too_many = FakeClient([response("r1", [call("a"), call("b")])])
    expect_error(lambda: answer(too_many, "example", "q", authenticated_tenant="team-a", max_tool_calls=1))
    incomplete = FakeClient([response("r1", [call()], status="incomplete")])
    expect_error(lambda: answer(incomplete, "example", "q", authenticated_tenant="team-a"))
    no_text = FakeClient([response("r1")])
    expect_error(lambda: answer(no_text, "example", "q", authenticated_tenant="team-a"))
    team = calculate(seats=10, seat_price=20, metered=100,
                     incremental_review_hours=12, hourly_rate=60, accepted_tasks=100)
    assert team["economic_cost"] == "1020.00"
    assert team["recurring_cash"] == "300.00"
    assert team["economic_cost_per_accepted_task"] == "10.20"
    home = calculate(seats=1, seat_price=0, energy="1.20", hardware=600)
    assert home["economic_cost"] == "17.87"
    assert home["economic_cost_per_accepted_task"] is None
    for kwargs in [{"seat_price": -1}, {"seat_price": "NaN"},
                   {"seat_price": 1, "amortization_months": 0},
                   {"seat_price": 1, "accepted_tasks": True}]:
        expect_error(lambda kwargs=kwargs: calculate(seats=1, **kwargs))
    weights = [{"parameters_billion": n, "bf16_GB": n * 2, "four_bit_GB": n / 2}
               for n in (9, 35, 397)]
    here = Path(__file__).parent
    files = ["tool_boundary.py", "responses_example.py", "cost_calculator.py", "verify_examples.py"]
    print(json.dumps({
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "scope": "Offline deterministic dispatch, mock Responses transport, and arithmetic. No live model, product account, database, or GPU benchmark.",
        "boundary_checks": checks,
        "responses_checks": ["call ID correspondence", "instruction repetition",
                            "duplicate IDs rejected", "request budget", "tool budget",
                            "incomplete response rejected", "empty/refusal path stops"],
        "cost_examples": {"team": team, "home": home},
        "weight_memory_lower_bounds_decimal_GB": weights,
        "file_sha256": {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in files},
        "passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
