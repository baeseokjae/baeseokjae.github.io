# Runnable capacity-value model — ai-coding-enterprise-roi-guide-2026

This directory holds a deterministic, offline model that converts *measured*
released work hours into a modeled annual capacity value, plus the study-design
material it is paired with in the article. It is a planning model, not a
measurement of any enterprise result.

## Reproduce

```
python3 roi-model.py --inputs inputs.example.csv \
  --assumptions assumptions.json --out expected-output.csv
```

Verified run: 2026-10-25, CPython 3.12.3, Linux x86_64, no network access, no
third-party packages.

| Item | Value |
|---|---|
| interpreter | CPython 3.12.3 |
| command | see above, executed from this directory |
| output file | `expected-output.csv` (458 bytes) |
| output sha256 | `b406e56d7e55d4ae6270a8794e23f0cb62991f1676b5122c95e2f2b608117819` |
| repeat run | identical sha256 (byte-for-byte) |

## Expected output

```
scenario,headcount,gross_capacity_hours_year,review_overhead_hours_year,net_capacity_hours_year,realization_pct,modeled_benefit_usd_year,incremental_cost_usd_year,modeled_roi_pct,modeled_payback_months,benefit_is_cash
low-realization,20,1840,460,1380,25,20700,25800,-19.77,14.96,no
base,20,1840,460,1380,50,41400,25800,60.47,7.48,no
high-realization,20,1840,460,1380,75,62100,25800,140.70,4.99,no
review-heavy,20,1840,1380,460,50,13800,25800,-46.51,22.43,no
```

## Inputs

`inputs.example.csv` is synthetic. One row per scenario:

| Column | Unit |
|---|---|
| `scenario` | label, echoed to output |
| `headcount` | developers in scope |
| `loaded_hourly_rate_usd` | USD per hour, fully burdened |
| `measured_capacity_hours_per_dev_week` | hours per developer per week, measured on eligible tasks |
| `realization_pct` | 0-100, share of released capacity counted as useful |
| `review_overhead_hours_per_dev_week` | hours per developer per week of added review, subtracted from capacity |
| `annual_tool_cost_per_seat_usd` | USD per seat per year |
| `annual_enablement_cost_usd` | USD per year, one-time setup amortized by the reader, not by the model |

## Assumptions

Every inference is named in `assumptions.json` with `is_assumption: true`.
Notably: 46 working weeks; review overhead is subtracted rather than added as a
cost, to avoid counting the same hours twice; `realization_pct` values are
scenario dials, not benchmarks; no vendor ROI figure is embedded as a default;
`benefit_is_cash` is always `no`.

## Limits

- Single-period rate. No discounting, NPV or IRR. Multi-year cases need an
  explicit discount rate applied outside this file.
- Values capacity, not cash. Nothing here establishes avoided expenditure or
  revenue, so a positive `modeled_roi_pct` is not a realized return.
- Takes capacity and cost as inputs. It does not estimate either, and it cannot
  detect selection effects, task-mix drift or confounding in the measurement
  that fed it.
- Rejects any row where review overhead exceeds measured capacity (exit 2),
  because net negative capacity is not a benefit.
- Deterministic by construction: fixed column order, fixed formatting, input
  order preserved, `not_reached` instead of NaN for zero benefit.

## Pairing with the study-design table

The article pairs this model with a per-study table (population, design,
metric, what the study cannot establish) built only from cited primary sources:
the Forrester TEI study commissioned by GitHub (Enterprise Cloud, composite
organization), METR's July 2025 RCT and its February 2026 design update, and
DORA's five delivery metrics. The table's job is to stop a modeled number and a
measured study from being read as the same kind of evidence.
