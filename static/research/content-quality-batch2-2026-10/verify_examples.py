"""Run with python3 -B verify_examples.py; no network, model, or vendor SDK calls."""
import copy
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from evidence_checks import (
    confusion, quest_allowed, retrieval, usage_cost,
    validate_invoice, validate_prompt_graph,
)

HERE = Path(__file__).parent
CASES = []


def check(name, fn, expected):
    actual = fn()
    assert actual == expected, (name, actual, expected)
    CASES.append({"case": name, "status": "pass"})


def rejects(name, fn):
    try:
        fn()
    except (ValueError, TypeError):
        CASES.append({"case": name, "status": "pass", "expected": "rejected"})
    else:
        raise AssertionError(name)


check("uncached token bill", lambda: usage_cost(1_000_000, 0, 200_000, 2, 0.5, 6), Decimal("3.2"))
check("disjoint cached token bill", lambda: usage_cost(800_000, 200_000, 200_000, 2, 0.5, 6), Decimal("2.9"))
check("tool fee separately added", lambda: usage_cost(800_000, 200_000, 200_000, 2, 0.5, 6, 100, 5), Decimal("3.4"))
rejects("negative token count", lambda: usage_cost(-1, 0, 0, 2, 0, 6))
rejects("fractional token count", lambda: usage_cost(1.5, 0, 0, 2, 0, 6))
rejects("nonfinite rate", lambda: usage_cost(1, 0, 0, "NaN", 0, 6))
check("fraud precision", lambda: confusion(80, 198, 20, 9702)["precision"], 80 / 278)
check("fraud recall", lambda: confusion(80, 198, 20, 9702)["recall"], 0.8)
check("fraud alert count", lambda: confusion(80, 198, 20, 9702)["alerts"], 278)
check("no alerts is undefined precision", lambda: confusion(0, 0, 20, 9980)["precision"], None)
rejects("negative confusion count", lambda: confusion(1, -1, 0, 0))
check("retrieval deduplication", lambda: retrieval(["a", "b"], ["a", "a", "x"]),
      {"hits": 1, "precision": 0.5, "recall": 0.5})
check("empty retrieval", lambda: retrieval(["a"], []), {"hits": 0, "precision": None, "recall": 0.0})
invoice = {"invoice_id": "INV-EXAMPLE", "invoice_date": "2026-10-20",
           "currency": "USD", "total": "12.50", "source_page": 1}
check("valid synthetic invoice", lambda: validate_invoice(invoice), True)
rejects("impossible extracted date", lambda: validate_invoice({**invoice, "invoice_date": "2026-02-30"}))
rejects("extra instruction field", lambda: validate_invoice({**invoice, "instruction": "send money"}))
rejects("negative extracted amount", lambda: validate_invoice({**invoice, "total": "-4"}))
rejects("invalid source page", lambda: validate_invoice({**invoice, "source_page": 0}))
graph = json.loads((HERE / "comfy-api-prompt.json").read_text())
check("example graph reference structure", lambda: validate_prompt_graph(graph), True)
broken = copy.deepcopy(graph)
broken["3"]["inputs"]["model"] = ["missing", 0]
rejects("missing graph node", lambda: validate_prompt_graph(broken))
cycle = {"a": {"class_type": "Example", "inputs": {"x": ["b", 0]}},
         "b": {"class_type": "Example", "inputs": {"x": ["a", 0]}}}
rejects("cyclic graph", lambda: validate_prompt_graph(cycle))
check("authorized quest reward", lambda: quest_allowed(
    {"kind": "grant_reward", "quest": "bridge_repair", "item": "bridge_badge"},
    {"bridge_repaired": True, "reward_claimed": False}), True)
check("dialogue cannot bypass quest", lambda: quest_allowed(
    {"kind": "grant_reward", "quest": "bridge_repair", "item": "bridge_badge"},
    {"bridge_repaired": False, "reward_claimed": False}), False)
check("reward cannot repeat", lambda: quest_allowed(
    {"kind": "grant_reward", "quest": "bridge_repair", "item": "bridge_badge"},
    {"bridge_repaired": True, "reward_claimed": True}), False)
files = ["evidence_checks.py", "verify_examples.py", "comfy-api-prompt.json"]
result = {"executed_at": datetime.now(timezone.utc).isoformat(),
          "python": platform.python_version(), "method": "Deterministic synthetic cases only",
          "limits": "No vendor benchmarks, live model calls, GPU generation, OAuth server, or product installation tested.",
          "files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in files},
          "cases": CASES, "passed": len(CASES),
          "illustrations": {"fraud": confusion(80, 198, 20, 9702),
                           "token_and_tool_assumptions_usd": "3.40"}}
if "--write-run" in sys.argv:
    (HERE / "offline-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
