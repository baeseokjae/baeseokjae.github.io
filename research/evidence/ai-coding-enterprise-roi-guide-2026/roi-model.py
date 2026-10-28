#!/usr/bin/env python3
"""Deterministic, offline capacity-value model for an AI coding tool rollout.

What this model is
------------------
It converts measured *active work hours released* into a modeled annual value,
then divides by the stated incremental cost. It is a planning model.

What this model is not
----------------------
It is not a measurement of any enterprise result, not a forecast, and not an
investment recommendation. Capacity released is not cash saved unless
expenditure was actually avoided or reduced. No vendor benchmark is embedded as
a default: every value is read from the input CSV, and every inference is named
in assumptions.json.

Reproducibility
---------------
stdlib only, no network, no randomness, no timestamps, no locale-dependent
formatting. Rows are emitted in input order with fixed decimal formatting, so
the same inputs produce a byte-identical output file.

Usage
-----
    python3 roi-model.py --inputs inputs.example.csv \
        --assumptions assumptions.json --out expected-output.csv

Exit codes
----------
0  success
2  invalid input (missing column, non-numeric value, negative value, cost <= 0)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import NoReturn

REQUIRED_COLUMNS = (
    "scenario",
    "headcount",
    "loaded_hourly_rate_usd",
    "measured_capacity_hours_per_dev_week",
    "realization_pct",
    "review_overhead_hours_per_dev_week",
    "annual_tool_cost_per_seat_usd",
    "annual_enablement_cost_usd",
)

OUTPUT_COLUMNS = (
    "scenario",
    "headcount",
    "gross_capacity_hours_year",
    "review_overhead_hours_year",
    "net_capacity_hours_year",
    "realization_pct",
    "modeled_benefit_usd_year",
    "incremental_cost_usd_year",
    "modeled_roi_pct",
    "modeled_payback_months",
    "benefit_is_cash",
)

BENEFIT_IS_CASH = "no"


def fail(message: str) -> NoReturn:
    sys.stderr.write("error: " + message + "\n")
    raise SystemExit(2)


def number(row: dict, column: str, row_index: int) -> float:
    raw = (row.get(column) or "").strip()
    if raw == "":
        fail(f"row {row_index}: column {column!r} is empty")
    try:
        value = float(raw)
    except ValueError:
        fail(f"row {row_index}: column {column!r} is not numeric: {raw!r}")
    if value != value or value in (float("inf"), float("-inf")):
        fail(f"row {row_index}: column {column!r} is not finite")
    if value < 0:
        fail(f"row {row_index}: column {column!r} must not be negative")
    return value


def load_assumptions(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    weeks = payload.get("working_weeks_per_year")
    if not isinstance(weeks, int) or not 1 <= weeks <= 53:
        fail("assumptions: working_weeks_per_year must be an integer 1..53")
    assumptions = payload.get("assumptions") or []
    if not isinstance(assumptions, list) or not assumptions:
        fail("assumptions: 'assumptions' must be a non-empty list")
    for item in assumptions:
        if not item.get("name") or not item.get("statement"):
            fail("assumptions: every entry needs 'name' and 'statement'")
        if item.get("is_assumption") is not True:
            fail("assumptions: every entry must be labelled is_assumption=true")
    return payload


def compute(row: dict, row_index: int, weeks: int) -> dict:
    headcount = number(row, "headcount", row_index)
    rate = number(row, "loaded_hourly_rate_usd", row_index)
    capacity = number(row, "measured_capacity_hours_per_dev_week", row_index)
    realization = number(row, "realization_pct", row_index)
    review = number(row, "review_overhead_hours_per_dev_week", row_index)
    tool = number(row, "annual_tool_cost_per_seat_usd", row_index)
    enablement = number(row, "annual_enablement_cost_usd", row_index)

    if headcount <= 0:
        fail(f"row {row_index}: headcount must be greater than zero")
    if realization > 100:
        fail(f"row {row_index}: realization_pct must be 0..100")
    if review > capacity:
        fail(
            f"row {row_index}: review overhead exceeds measured capacity; "
            "the model would report negative net capacity as a benefit"
        )

    gross_hours = headcount * capacity * weeks
    review_hours = headcount * review * weeks
    net_hours = gross_hours - review_hours
    modeled_benefit = net_hours * rate * (realization / 100.0)
    incremental_cost = headcount * tool + enablement
    if incremental_cost <= 0:
        fail(f"row {row_index}: incremental cost must be greater than zero")

    roi_pct = (modeled_benefit - incremental_cost) / incremental_cost * 100.0
    if modeled_benefit > 0:
        payback_months = incremental_cost / (modeled_benefit / 12.0)
    else:
        payback_months = float("nan")

    return {
        "scenario": (row.get("scenario") or "").strip(),
        "headcount": headcount,
        "gross_capacity_hours_year": gross_hours,
        "review_overhead_hours_year": review_hours,
        "net_capacity_hours_year": net_hours,
        "realization_pct": realization,
        "modeled_benefit_usd_year": modeled_benefit,
        "incremental_cost_usd_year": incremental_cost,
        "modeled_roi_pct": roi_pct,
        "modeled_payback_months": payback_months,
        "benefit_is_cash": BENEFIT_IS_CASH,
    }


def fmt(value: float) -> str:
    if isinstance(value, float) and value != value:
        return "not_reached"
    if float(value).is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.2f}"


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(description="Deterministic AI coding capacity-value model")
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--assumptions", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    payload = load_assumptions(args.assumptions)
    weeks = payload["working_weeks_per_year"]

    with open(args.inputs, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        missing = [column for column in REQUIRED_COLUMNS if column not in header]
        if missing:
            fail("inputs: missing columns: " + ", ".join(missing))
        rows = list(reader)
    if not rows:
        fail("inputs: no data rows")

    results = [compute(row, index + 2, weeks) for index, row in enumerate(rows)]

    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(OUTPUT_COLUMNS)
        for result in results:
            line = []
            for column in OUTPUT_COLUMNS:
                value = result[column]
                line.append(value if isinstance(value, str) else fmt(value))
            writer.writerow(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
