#!/usr/bin/env python3
"""Deterministic truncation-policy survival matrix (Part A).

Fixture: 400 KB line-oriented log-shaped payload with one evidence line
planted at a given fraction of the payload. Budget: 20 KB chars per policy.
No model is involved; every number in the JSON is reproducible by rerunning
this script with the same PYTHONHASHSEED-free deterministic fixture.
"""
import json
import re
import hashlib
import platform
import time
import sys

BUDGET = 20_000          # characters kept by every policy
PAYLOAD_BYTES = 400_000  # target fixture size in bytes
EVIDENCE = "EVIDENCE-MARKER-7f3a build_id=8412 shard=blue-17 status=FAILED"
POSITIONS = [0.0, 0.25, 0.5, 0.75, 1.0]


def build_payload(target_bytes=PAYLOAD_BYTES, evidence_at=0.5):
    """Deterministic log-shaped fixture; evidence line inserted at fraction."""
    lines, total = [], 0
    i = 0
    evidence_line = f"2026-11-22T17:12:{i % 60:02d}Z ERROR {EVIDENCE}\n"
    while total < target_bytes:
        i += 1
        svc = ("build", "test", "deploy", "cache")[i % 4]
        line = (f"2026-11-22T17:{(i // 60) % 60:02d}:{i % 60:02d}Z INFO "
                f"[{svc}] step={i:06d} elapsed_ms={(i * 37) % 9000} "
                f"msg=\"worker {i % 97} processed chunk {i * 13 % 100003}\"\n")
        lines.append(line)
        total += len(line)
    text = "".join(lines)
    if evidence_at >= 1.0:
        cut = len(text)
    else:
        cut = int(len(text) * evidence_at)
        if cut > 0:
            cut = text.find("\n", cut) + 1
            if cut <= 0:
                cut = len(text)
    text = text[:cut] + evidence_line + text[cut:]
    return text, evidence_line


def head(text, budget=BUDGET):
    return text[:budget], [[0, len(text[:budget])]]


def tail(text, budget=BUDGET):
    out = text[-budget:]
    return out, [[len(text) - len(out), len(text)]]


def head_tail(text, budget=BUDGET):
    half = budget // 2
    out = text[:half] + "\n[...snip...]\n" + text[-half:]
    return out, [[0, half], [len(text) - half, len(text)]]


def middle_out(text, budget=BUDGET):
    """Keep a window centred on the payload midpoint (drop both ends)."""
    start = max(0, (len(text) - budget) // 2)
    return text[start:start + budget], [[start, start + budget]]


def match_centred(text, budget=BUDGET):
    """Keep a window centred on the first line matching the harness regex."""
    m = re.search(r"^(?=.*\b(?:ERROR|FATAL|Exception)\b).*$",
                  text, re.MULTILINE)
    if not m:
        return text[:budget], [[0, budget]]
    centre = (m.start() + m.end()) // 2
    start = max(0, min(centre - budget // 2, len(text) - budget))
    return text[start:start + budget], [[start, start + budget]]


POLICIES = {
    "head-N": head,
    "tail-N": tail,
    "head+tail": head_tail,
    "middle-out": middle_out,
    "match-centred": match_centred,
}


def main():
    started = time.time()
    rows = []
    fixtures = {}
    for frac in POSITIONS:
        text, ev = build_payload(evidence_at=frac)
        fixtures[str(frac)] = hashlib.sha256(text.encode()).hexdigest()
        ev_off = text.find(ev)
        for name, fn in POLICIES.items():
            out, spans = fn(text)
            survived = ev in out
            rows.append({
                "policy": name,
                "evidence_position_frac": frac,
                "payload_chars": len(text),
                "payload_bytes": len(text.encode()),
                "evidence_line_offset": ev_off,
                "kept_chars": len(out),
                "evidence_survived": survived,
                "kept_spans": spans,
                "marker_present": "[...snip...]" in out,
            })
    matrix = {}
    for r in rows:
        matrix.setdefault(r["policy"], {})[str(r["evidence_position_frac"])] = \
            r["evidence_survived"]
    result = {
        "experiment": "part-a-deterministic-truncation-survival",
        "budget_chars": BUDGET,
        "payload_target_bytes": PAYLOAD_BYTES,
        "policies": list(POLICIES),
        "positions": POSITIONS,
        "fixture_sha256": fixtures,
        "survival_matrix": matrix,
        "rows": rows,
        "observed": {
            "payload_chars_first": rows[0]["payload_chars"],
            "payload_bytes_first": rows[0]["payload_bytes"],
            "elapsed_s": round(time.time() - started, 3),
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "host": platform.node(),
            "note": "single host, CPU-only, stdlib-only; no model",
        },
    }
    print(json.dumps(result["survival_matrix"], indent=1))
    print(json.dumps(result["observed"]))
    with open(sys.argv[1] if len(sys.argv) > 1 else "part_a_results.json", "w") as f:
        json.dump(result, f, indent=1)


if __name__ == "__main__":
    main()
