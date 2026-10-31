# Lifecycle-fit fixture — E2B / Daytona / Blaxel

Offline decision fixture for the article `e2b-vs-daytona-vs-blaxel-2026`. It scores a
workload's lifecycle requirements against **documented** capability flags. It makes no
network calls and prints no timing or price.

## Files

| File | Purpose |
|---|---|
| `capability-matrix.json` | Capability flags transcribed from each vendor's documentation on 2026-10-28, with the page each flag came from. |
| `workloads.json` | Three requirement profiles. Replace the `requires` keys with your own workload. |
| `lifecycle_fit.py` | Stdlib-only scorer. Deterministic; exit code 0 on a completed run. |
| `fit-report.json` | Output of the recorded run. |
| `fixture-run.txt` | Raw stdout of the recorded run. |

## Run

```bash
cd research/evidence/e2b-vs-daytona-vs-blaxel-2026/fixture
python3 lifecycle_fit.py
```

Requires Python 3.9+ and no packages.

## Verdicts

- `meets` — every required flag is documented as supported and no documented limit is exceeded.
- `verify` — no flag contradicts the requirement, but something is not stated on the checked page
  (for example, the continuous-session limit), so the answer must come from the vendor's current
  reference or a test of your own.
- `unmet` — the documentation states the capability is not supported, or a documented limit is
  exceeded.

## Limits

- Flags are vendor claims read on one date. Vendors change them; re-check the linked page.
- The matrix does not include price, latency, cold-start, throughput, isolation strength or
  reliability. None of those were measured for this article.
- `continuous_runtime_hours` is filled only where the vendor page states a number; an empty value
  is reported as `verify`, never guessed.
