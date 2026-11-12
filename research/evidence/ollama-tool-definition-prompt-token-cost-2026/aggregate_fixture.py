#!/usr/bin/env python3
"""aggregate_fixture.py — turn fixture-raw.jsonl into the published summary CSV.

`tool_schema_token_audit.py` writes one JSONL row per request. This module is
the aggregation step that produces `fixture-summary.csv`:

    surface, cell, tool_count, n_ok, n_attempts, median, min, max,
    full_range, tools_json_bytes, errors

One row per cell, in first-seen order. A cell with no successful request is
still emitted (n_ok=0, empty statistics, the error strings joined by "; "),
because a failed cell is evidence and dropping it would hide the 12-tool
verbose attempt. `median` is `statistics.median` of the successful
`prompt_eval_count` values, so for three identical repeats it is that value.

Usage:
    python3 aggregate_fixture.py --raw fixture-raw.jsonl --csv fixture-summary.csv
    python3 aggregate_fixture.py --raw fixture-raw.jsonl          # CSV to stdout

The same functions are imported by the driver, so the CSV a run prints and the
CSV this script regenerates from the run's JSONL are produced by one
implementation. Stdlib only.
"""
import argparse
import csv
import json
import statistics
import sys

COLUMNS = ["surface", "cell", "tool_count", "n_ok", "n_attempts", "median", "min",
           "max", "full_range", "tools_json_bytes", "errors"]


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def aggregate_rows(rows):
    """Group per-request records by (surface, cell) and summarise each group."""
    order, groups = [], {}
    for row in rows:
        key = (row.get("surface"), row.get("cell"))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    summary = []
    for key in order:
        group = groups[key]
        values = [r.get("prompt_eval_count") for r in group
                  if isinstance(r.get("prompt_eval_count"), (int, float))]
        errors = sorted({r["error"] for r in group if r.get("error")})
        byte_values = [r.get("tools_json_bytes") for r in group
                       if isinstance(r.get("tools_json_bytes"), int)]
        summary.append({
            "surface": key[0],
            "cell": key[1],
            "tool_count": group[0].get("tool_count"),
            "n_ok": len(values),
            "n_attempts": len(group),
            "median": statistics.median(values) if values else "",
            "min": min(values) if values else "",
            "max": max(values) if values else "",
            "full_range": (max(values) - min(values)) if values else "",
            "tools_json_bytes": byte_values[0] if byte_values else "",
            "errors": "; ".join(errors),
        })
    return summary


def write_summary(summary, stream):
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(summary)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Aggregate fixture-raw.jsonl into the summary CSV.")
    parser.add_argument("--raw", default="fixture-raw.jsonl", help="input JSONL (appended by the driver)")
    parser.add_argument("--csv", default=None, help="output CSV path; omit to write to stdout")
    args = parser.parse_args(argv)

    summary = aggregate_rows(load_rows(args.raw))
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as handle:
            write_summary(summary, handle)
        print(json.dumps({"csv": args.csv, "cells": len(summary), "rows": sum(r["n_attempts"] for r in summary)}))
    else:
        write_summary(summary, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
