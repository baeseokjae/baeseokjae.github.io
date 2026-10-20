"""Small offline calculations and validation examples, not product benchmarks."""
from datetime import date
from decimal import Decimal, InvalidOperation


def nonnegative(value):
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("Expected a finite nonnegative number") from error
    if not n.is_finite() or n < 0:
        raise ValueError("Expected a finite nonnegative number")
    return n


def count(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Expected a nonnegative integer count")
    return value


def usage_cost(uncached_input, cached_input, output, input_rate, cached_rate,
               output_rate, tool_calls=0, tool_rate_per_thousand=0):
    """Token categories are disjoint. Rates are user-supplied USD assumptions."""
    tokens = [count(v) for v in (uncached_input, cached_input, output)]
    rates = [nonnegative(v) for v in (input_rate, cached_rate, output_rate)]
    token_cost = sum(Decimal(t) * r for t, r in zip(tokens, rates)) / Decimal(1_000_000)
    tools = Decimal(count(tool_calls)) * nonnegative(tool_rate_per_thousand) / Decimal(1000)
    return token_cost + tools


def confusion(tp, fp, fn, tn):
    tp, fp, fn, tn = [count(v) for v in (tp, fp, fn, tn)]
    def ratio(a, b):
        return None if b == 0 else a / b
    return {
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "false_positive_rate": ratio(fp, fp + tn),
        "accuracy": ratio(tp + tn, tp + fp + fn + tn),
        "alerts": tp + fp,
    }


def retrieval(expected, returned):
    """Set metrics for manually labeled symbols; duplicates do not increase credit."""
    expected, returned = set(expected), set(returned)
    hits = len(expected & returned)
    return {"hits": hits,
            "precision": hits / len(returned) if returned else None,
            "recall": hits / len(expected) if expected else None}


def validate_invoice(record):
    """Application checks after extraction, not proof of image-reading accuracy."""
    if set(record) != {"invoice_id", "invoice_date", "currency", "total", "source_page"}:
        raise ValueError("Unexpected or missing fields")
    if not isinstance(record["invoice_id"], str) or not record["invoice_id"].strip():
        raise ValueError("Missing invoice identifier")
    date.fromisoformat(record["invoice_date"])
    if record["currency"] not in {"USD", "EUR", "KRW"}:
        raise ValueError("Unsupported currency in this example")
    total = nonnegative(record["total"])
    if record["currency"] == "KRW" and total != total.to_integral_value():
        raise ValueError("This example requires whole-won totals")
    if count(record["source_page"]) < 1:
        raise ValueError("Source pages start at one")
    return True


def validate_prompt_graph(graph):
    """Check basic API-prompt references, not ComfyUI types, models, or execution."""
    if not isinstance(graph, dict) or not graph:
        raise ValueError("Expected a nonempty node dictionary")
    edges = {}
    for key, node in graph.items():
        if not isinstance(key, str) or not isinstance(node, dict):
            raise ValueError("Node IDs must be strings")
        if not isinstance(node.get("class_type"), str) or not isinstance(node.get("inputs"), dict):
            raise ValueError("Missing node type or inputs")
        edges[key] = []
        for value in node["inputs"].values():
            if isinstance(value, list):
                if len(value) != 2 or not isinstance(value[0], str):
                    raise ValueError("Expected [node_id, output_index]")
                count(value[1])
                if value[0] not in graph:
                    raise ValueError("Missing referenced node")
                edges[key].append(value[0])
    seen, visiting = set(), set()
    def visit(node):
        if node in visiting:
            raise ValueError("Cycle in prompt graph")
        if node in seen:
            return
        visiting.add(node)
        for other in edges[node]:
            visit(other)
        visiting.remove(node)
        seen.add(node)
    for node in edges:
        visit(node)
    return True


def quest_allowed(action, player):
    """The game owns quest state; dialogue text cannot grant an item."""
    if action.get("kind") != "grant_reward" or action.get("quest") != "bridge_repair":
        return False
    return (player.get("bridge_repaired") is True
            and player.get("reward_claimed") is False
            and action.get("item") == "bridge_badge")
