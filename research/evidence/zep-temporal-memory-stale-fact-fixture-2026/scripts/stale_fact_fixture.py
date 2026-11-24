#!/usr/bin/env python3
"""Stale-fact fixture: does a store's temporal invalidation policy suppress superseded facts?

Four modelled store policies, two query modes, two extraction conditions, 30 scripted
cases = 16 cells x 30 evaluations. Deterministic, stdlib only, no network, no model.

What is modelled (and what is not):
  * The four policies are ~15-line stand-ins for design patterns, NOT implementations of
    Zep Cloud or Graphiti. Nothing here runs Graphiti, Neo4j, or any LLM extraction.
  * Ground truth is synthetic: every case has explicit valid-time windows, so the correct
    answer at any instant is known by construction.

Policies
  A append_only_recency   keeps every fact with its timestamps, but the query returns the
                          most recently *ingested* value (no supersession, no time predicate).
  B lww_upsert            one row per (entity, attribute), overwritten at ingest time; the
                          query returns the surviving row. No history.
  C bitemporal_invalidate supersession is stamped from valid-time order (an edge is closed at
                          the valid_from of its successor), and the query returns the edge open
                          at NOW. No query-time as-of predicate: both query modes use NOW.
  D bitemporal_asof       same store as C plus a query-time predicate evaluated at the asked-for
                          instant (valid_from <= T, invalid_at/valid_to after T).

Usage
  Run from the repository root; the script resolves its inputs and outputs relative to this
  evidence bundle, so the same command works wherever the directory is checked out.

  python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py --emit-fixtures
  python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py
  python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py --verify
"""
import argparse
import csv
import hashlib
import io
import json
import platform
import random
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

# Bundle root = research/evidence/<slug>/; the article's evidence files live below it.
ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "fixtures" / "stale_fact_cases.json"
CSV_PATH = ROOT / "results" / "stale_fact_matrix.csv"
RUN_PATH = ROOT / "first-party-fixture-run-2026-10-30.json"

NOW = date(2026, 10, 29)          # evaluation instant for "what is X now"
AS_OF = date(2026, 8, 1)          # evaluation instant for "what was X on 2026-08-01"
SEED = 20261030
MIS_EXTRACTION_RATE = 0.10        # 3 of 30 cases

POLICIES = ("append_only_recency", "lww_upsert", "bitemporal_invalidate", "bitemporal_asof")
QUERY_MODES = ("current", "as_of")
ARMS = ("clean", "mis_extraction_10pct")
NOTHING = "none"


# --------------------------------------------------------------------------- fixture data
def _ev(episode, value, valid_from, valid_to, ingested_at):
    return {"episode": episode, "value": value, "valid_from": valid_from,
            "valid_to": valid_to, "ingested_at": ingested_at}


def build_cases():
    """Build 30 cases over three change shapes. Deterministic; frozen into the fixtures file."""
    rng = random.Random(SEED)
    attrs = ["plan_tier", "data_region", "billing_owner", "support_level", "deploy_target",
             "sso_provider", "retention_days", "seat_count_band", "primary_contact", "api_scope"]
    shapes = ["value_update"] * 10 + ["contradiction"] * 10 + ["time_bounded"] * 10
    cases = []
    for index, shape in enumerate(shapes, start=1):
        attribute = attrs[(index - 1) % len(attrs)]
        entity = f"acct_{1000 + index}"
        if shape == "value_update":
            # In-order update: ingestion order agrees with valid-time order, so a store that ranks
            # by ingestion recency alone still answers the current question correctly. Four of the
            # ten changed before the as-of instant (already stable there), six after it.
            old = f"v{index}a"
            new = f"v{index}b"
            if index <= 4:
                events = [
                    _ev("e1", old, "2026-03-01", "2026-04-01", "2026-03-02T09:00:00Z"),
                    _ev("e2", new, "2026-04-01", None, "2026-04-02T11:30:00Z"),
                ]
            else:
                events = [
                    _ev("e1", old, "2026-03-01", "2026-09-01", "2026-03-02T09:00:00Z"),
                    _ev("e2", new, "2026-09-01", None, "2026-09-02T11:30:00Z"),
                ]
        elif shape == "contradiction":
            # A late-arriving correction for a historical window that was previously unknown
            # arrives after the current value was ingested, so ingestion order no longer agrees
            # with valid-time order. All three windows are disjoint.
            first = f"v{index}a"
            current = f"v{index}b"
            backfill = f"v{index}c"
            events = [
                _ev("e1", first, "2026-03-01", "2026-05-01", "2026-03-02T09:00:00Z"),
                _ev("e3", backfill, "2026-05-01", "2026-07-15", "2026-10-20T16:40:00Z"),
                _ev("e2", current, "2026-10-01", None, "2026-10-02T08:15:00Z"),
            ]
        else:
            # Time-bounded validity: the attribute lapsed, so the truthful current answer is "none".
            early = f"v{index}a"
            late = f"v{index}b"
            events = [
                _ev("e1", early, "2026-01-15", "2026-04-01", "2026-01-16T10:00:00Z"),
                _ev("e2", late, "2026-04-01", "2026-09-15", "2026-04-02T10:00:00Z"),
            ]
        cases.append({"case_id": f"c{index:02d}", "shape": shape, "entity": entity,
                      "attribute": attribute, "events": events})
    # Seeded mis-extraction: 3 of 30 cases, drawn only from shapes where the corruption can be
    # observed at query time (a corrupted "none" answer would be invisible).
    eligible = [c["case_id"] for c in cases if c["shape"] in ("value_update", "contradiction")]
    corrupted = sorted(rng.sample(eligible, round(MIS_EXTRACTION_RATE * len(cases))))
    for case in cases:
        case["mis_extracted"] = case["case_id"] in corrupted
    return cases


# --------------------------------------------------------------------------- helpers
def _d(value):
    return date.fromisoformat(value)


def _ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def truth(case, moment):
    """Ground truth: the value whose valid-time window contains `moment`, else "none"."""
    for event in case["events"]:
        start = _d(event["valid_from"])
        end = _d(event["valid_to"]) if event["valid_to"] else None
        if start <= moment and (end is None or end > moment):
            return event["value"]
    return NOTHING


def validate_cases(cases):
    """The fixture is only interpretable if ground truth is unambiguous: windows must be disjoint
    and exactly one event must cover each evaluation instant (or none, for a lapsed attribute)."""
    problems = []
    for case in cases:
        windows = [(_d(e["valid_from"]), _d(e["valid_to"]) if e["valid_to"] else None) for e in case["events"]]
        for i, (start_a, end_a) in enumerate(windows):
            for start_b, end_b in windows[i + 1:]:
                if (end_b is None or start_a < end_b) and (end_a is None or start_b < end_a):
                    problems.append(f"{case['case_id']}: overlapping windows")
        for moment in (NOW, AS_OF):
            covers = [e for e in case["events"]
                      if _d(e["valid_from"]) <= moment
                      and (e["valid_to"] is None or _d(e["valid_to"]) > moment)]
            if len(covers) > 1:
                problems.append(f"{case['case_id']}: {len(covers)} events cover {moment}")
    if problems:
        raise SystemExit("FIXTURE INVALID: " + "; ".join(problems))


def edges_for(case, corrupt):
    """Flatten the case into edges. With `corrupt`, the edge covering NOW is stored under a
    wrong attribute (the seeded extraction fault), so an attribute query cannot find it."""
    edges = []
    for event in case["events"]:
        edges.append({"attribute": case["attribute"], "value": event["value"],
                      "valid_from": _d(event["valid_from"]),
                      "valid_to": _d(event["valid_to"]) if event["valid_to"] else None,
                      "ingested_at": _ts(event["ingested_at"])})
    if corrupt:
        covering = [e for e in edges
                    if e["valid_from"] <= NOW and (e["valid_to"] is None or e["valid_to"] > NOW)]
        if covering:
            covering[-1]["attribute"] = covering[-1]["attribute"] + "__misextracted"
    return edges


def invalidate_by_valid_time(edges):
    """Stamp invalid_at from valid-time order: an edge is closed at its successor's valid_from.
    This is the bitemporal part - it does not look at ingestion order at all."""
    for edge in edges:
        successors = [other for other in edges
                      if other is not edge
                      and other["valid_from"] >= edge["valid_from"]
                      and (edge["valid_to"] is None or other["valid_from"] <= edge["valid_to"])]
        edge["invalid_at"] = min((s["valid_from"] for s in successors), default=None)
    return edges


def _answer(edge):
    return edge["value"] if edge else NOTHING


# --------------------------------------------------------------------------- policies
def policy_append_only_recency(edges, attribute, moment, mode):
    rows = [e for e in edges if e["attribute"] == attribute]
    if not rows:
        return NOTHING
    return _answer(max(rows, key=lambda e: e["ingested_at"]))


def policy_lww_upsert(edges, attribute, moment, mode):
    rows = [e for e in edges if e["attribute"] == attribute]
    if not rows:
        return NOTHING
    return _answer(max(rows, key=lambda e: e["ingested_at"]))


def _active(edges, attribute, moment):
    rows = [e for e in edges
            if e["attribute"] == attribute
            and e["valid_from"] <= moment
            and (e["valid_to"] is None or e["valid_to"] > moment)
            and (e["invalid_at"] is None or e["invalid_at"] > moment)]
    return max(rows, key=lambda e: e["valid_from"]) if rows else None


def policy_bitemporal_invalidate(edges, attribute, moment, mode):
    rows = invalidate_by_valid_time(edges)
    return _answer(_active(rows, attribute, NOW))       # no query-time as-of predicate


def policy_bitemporal_asof(edges, attribute, moment, mode):
    rows = invalidate_by_valid_time(edges)
    return _answer(_active(rows, attribute, moment))    # predicate evaluated at the asked instant


IMPLEMENTATIONS = {
    "append_only_recency": policy_append_only_recency,
    "lww_upsert": policy_lww_upsert,
    "bitemporal_invalidate": policy_bitemporal_invalidate,
    "bitemporal_asof": policy_bitemporal_asof,
}


# --------------------------------------------------------------------------- evaluation
def evaluate(cases):
    """Return one row per (policy, query_mode, extraction_arm) cell."""
    cells = {}
    for policy in POLICIES:
        for mode in QUERY_MODES:
            moment = NOW if mode == "current" else AS_OF
            clean_correct = {}
            for case in cases:
                edges = edges_for(case, corrupt=False)
                answer = IMPLEMENTATIONS[policy](edges, case["attribute"], moment, mode)
                clean_correct[case["case_id"]] = answer == truth(case, moment)
            for arm in ARMS:
                correct = superseded = extraction = policy_errors = 0
                for case in cases:
                    corrupt = arm == "mis_extraction_10pct" and case["mis_extracted"]
                    edges = edges_for(case, corrupt=corrupt)
                    answer = IMPLEMENTATIONS[policy](edges, case["attribute"], moment, mode)
                    expected = truth(case, moment)
                    if answer == expected:
                        correct += 1
                        continue
                    if answer != NOTHING and answer in [e["value"] for e in case["events"]]:
                        superseded += 1
                    if corrupt and clean_correct[case["case_id"]]:
                        extraction += 1        # the fault only appears once the fact is mis-stored
                    else:
                        policy_errors += 1     # wrong even with a clean store
                cells[(policy, mode, arm)] = {
                    "policy": policy,
                    "query_mode": mode,
                    "extraction_arm": arm,
                    "evaluations": len(cases),
                    "exact_correct": correct,
                    "exact_accuracy_pct": round(100.0 * correct / len(cases), 1),
                    "stale_returns": superseded,
                    "stale_return_rate_pct": round(100.0 * superseded / len(cases), 1),
                    "extraction_attributable_errors": extraction,
                    "policy_attributable_errors": policy_errors,
                }
    return [cells[(p, m, a)] for p in POLICIES for m in QUERY_MODES for a in ARMS]


FIELDS = ["policy", "query_mode", "extraction_arm", "evaluations", "exact_correct",
          "exact_accuracy_pct", "stale_returns", "stale_return_rate_pct",
          "extraction_attributable_errors", "policy_attributable_errors"]


def render_csv(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--emit-fixtures", action="store_true", help="rewrite the frozen case file")
    parser.add_argument("--verify", action="store_true", help="re-derive and compare the published CSV")
    parser.add_argument("--csv", default=str(CSV_PATH), help="CSV path (default: results/stale_fact_matrix.csv)")
    args = parser.parse_args(argv)

    if args.emit_fixtures:
        cases = build_cases()
        validate_cases(cases)
        payload = json.dumps({"seed": SEED, "now": NOW.isoformat(), "as_of": AS_OF.isoformat(),
                              "mis_extraction_rate": MIS_EXTRACTION_RATE,
                              "cases": cases}, indent=2) + "\n"
        CASES_PATH.parent.mkdir(parents=True, exist_ok=True)
        CASES_PATH.write_text(payload)
        print(f"wrote {CASES_PATH.relative_to(ROOT)} sha256={sha256_bytes(payload.encode())}")
        return 0

    frozen = json.loads(CASES_PATH.read_text())
    cases = frozen["cases"]
    validate_cases(cases)
    if cases != build_cases():
        print("FIXTURE DRIFT: fixtures/stale_fact_cases.json no longer matches build_cases()", file=sys.stderr)
        return 2

    started = time.perf_counter()
    rows = evaluate(cases)
    elapsed = time.perf_counter() - started
    rendered = render_csv(rows)

    if args.verify:
        published = Path(args.csv).read_text()
        if published != rendered:
            print(f"MISMATCH: re-derived CSV differs from {args.csv}", file=sys.stderr)
            return 1
        print(f"verified {len(rows)} cells against {args.csv} sha256={sha256_bytes(published.encode())}")
        return 0

    target = Path(args.csv)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered)
    total_stale = sum(r["stale_returns"] for r in rows)
    record = {
        "run_id": f"stale-fact-fixture-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": "python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": None,
        "evaluation_instant": NOW.isoformat(),
        "as_of_instant": AS_OF.isoformat(),
        "seed": SEED,
        "cases": len(cases),
        "cells": len(rows),
        "evaluations": len(cases) * len(rows),
        "elapsed_seconds": round(elapsed, 4),
        "stale_returns_total": total_stale,
        "inputs": {"fixtures/stale_fact_cases.json": sha256_bytes(CASES_PATH.read_bytes()),
                   "scripts/stale_fact_fixture.py": sha256_bytes(Path(__file__).read_bytes())},
        "outputs": {str(target.relative_to(ROOT)): sha256_bytes(rendered.encode())},
        "methodology": ("Deterministic stdlib-only fixture. 30 scripted facts with explicit valid-time "
                        "windows; ground truth is defined by those windows. Four modelled store policies, "
                        "two query instants and a seeded 10% mis-extraction arm are evaluated in 16 cells. "
                        "No product, model or graph database is executed and no network call is made."),
    }
    try:
        import os
        record["cpu_count"] = os.cpu_count()
    except Exception:  # pragma: no cover
        pass
    RUN_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUN_PATH.write_text(json.dumps(record, indent=2) + "\n")
    print(rendered, end="")
    print(f"wrote {target.relative_to(ROOT)} sha256={sha256_bytes(rendered.encode())} "
          f"elapsed={elapsed:.4f}s run_record={RUN_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
