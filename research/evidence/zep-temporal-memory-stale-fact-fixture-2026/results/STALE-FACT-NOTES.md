# STALE-FACT-NOTES — zep-temporal-memory-stale-fact-fixture-2026

Everything in `results/stale_fact_matrix.csv` is produced by `scripts/stale_fact_fixture.py`
from `fixtures/stale_fact_cases.json`. No network, no model, no graph database, no vendor
runtime. Python 3.12.3 standard library only.

The three directories below this file's parent are the article's evidence bundle:
`research/evidence/zep-temporal-memory-stale-fact-fixture-2026/`. The script resolves its
inputs and outputs relative to that bundle, so it runs the same way from any checkout.

## Commands

```bash
# regenerate the frozen case file (deterministic; the committed file must match build_cases())
python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py --emit-fixtures

# produce results/stale_fact_matrix.csv and the run record
python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py

# re-derive the 16 cells and compare byte for byte with the published CSV; exit 1 on mismatch
python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py --verify
```

Observed on the write-stage machine (Linux 6.17.0-1019-oracle, aarch64, 2 vCPU, Python 3.12.3):
evaluation loop 0.0042 s (the only timing the script records), whole process wall 0.056-0.057 s
(median 0.0568 s over 5 external repeats, interpreter start to exit), max RSS 17 MB. 480 evaluations.
Sub-0.1 s figures are host- and load-dependent; an independent review re-measurement on the same
host gave 0.07 s. See `timing` in the run record for the samples and the method.

Re-executed 2026-11-24 during the relocation check (scratch copy, same host class): evaluation loop
0.0051 s, whole process wall 0.07 s, max RSS 17 MB, and a CSV byte-identical to the published one
(sha256 `c1d96ab3...3548`). That re-run is recorded in `verification-2026-11-24.json`; the
2026-10-30 numbers above stay as the historical measurement they were.

## Hashes (generated, not hand-written)

| file | sha256 |
|---|---|
| `scripts/stale_fact_fixture.py` | `60956cdac03f6c3a3d34bb6a117162c6617550988eaaa84b16e5f10c1fab003a` |
| `fixtures/stale_fact_cases.json` | `2dcccbe5ca58d4801531955635e7f7d75a3e7237cebd1d6aae35200f65e2b285` |
| `results/stale_fact_matrix.csv` | `c1d96ab3fe5b0112e6705f0f22ffa936ce4927517c58b06b4f19da97f9953548` |

The run record — `first-party-fixture-run-2026-10-30.json` in this bundle — carries the script
hash at run time plus the same input/output hashes, and is re-emitted by every non-verify run.
It is a historical record: its `inputs.scripts/...` hash is the pre-relocation script, which is
kept byte-for-byte at `history/stale_fact_fixture-2026-10-30.py`.

## Relocation 2026-11-24

The script, case file, CSV and these notes were moved from the repository root (`scripts/`,
`fixtures/`, `results/`) into this bundle so that every reader-facing evidence file lives under
`research/evidence/<slug>/`. The only change to the script is path resolution: `RUN_PATH` now sits
at the bundle root instead of a repo-root `research/evidence/...` path, and the usage/command
strings name the new invocation. No policy, case, seed or evaluation logic changed, which is why
the re-derived CSV is byte-identical. `--verify` was re-run on a scratch copy, and a tampered copy
of the CSV still fails with `MISMATCH` and exit 1.

## Design

* 30 cases: 10 in-order updates, 10 late-arriving corrections (a historical window ingested after
  the current value), 10 time-bounded validity (attribute lapsed).
* Evaluation instants: NOW = 2026-10-29 (current-truth queries) and AS_OF = 2026-08-01 (point-in-time).
* Ground truth is defined by the cases' valid-time windows; `validate_cases()` refuses to run if a
  case has overlapping windows or more than one event covering an evaluation instant. It does not
  require one: 20 of the 60 case-instant pairs have no covering event (the ten late-arriving
  corrections at AS_OF, inside the 2026-07-15..2026-10-01 gap; the ten time-bounded cases at NOW),
  and there `truth()` returns `none` — the deliberate "no active fact" answer.
* Four modelled policies (stand-ins for patterns, **not** product implementations):
  1. `append_only_recency` — every fact kept, query returns the most recently ingested value.
  2. `lww_upsert` — one row per (entity, attribute), overwritten at ingest.
  3. `bitemporal_invalidate` — supersession stamped from valid-time order (edge closed at its
     successor's `valid_from`), query returns the edge open at NOW. No as-of predicate.
  4. `bitemporal_asof` — same store, plus a query-time predicate evaluated at the asked instant.
* Extraction arms: `clean`, and `mis_extraction_10pct` where 3 of 30 cases (seeded, seed 20261030)
  have the edge covering NOW stored under a wrong attribute.
* Attribution rule: an error is extraction-attributable only if the same policy answered the same
  case correctly with a clean store; otherwise it is policy-attributable.

## Artifacts a reader should not over-read

1. `append_only_recency` and `lww_upsert` are identical in all 16 cells. Under ingestion-time ranking
   with no temporal predicate, keeping history and overwriting it answer the same way. This is a
   property of the modelled policies, not a copy-paste error; the two functions are separate.
2. The `mis_extraction_10pct` arm raises the as-of score of the recency policies (46.7% → 50.0%) and
   of `bitemporal_invalidate` (13.3% → 20.0%). Removing a fact changes the ranking, and a coarse
   policy can accidentally become right. Single-cell deltas are not quality signals.
3. Under both bitemporal policies the 3 arm errors return *no* current fact, so `stale_returns` stays
   0 while exact accuracy falls to 90%. Mis-filed facts surface as silence, not as stale values.
4. The 10% arm is a seeded synthetic condition, not a measured extraction-error rate of any product.

## Scope

Nothing here measures Zep Cloud, Graphiti, Neo4j, FalkorDB or Neptune behaviour, extraction quality,
latency or cost. The paper's DMR (94.8% vs 93.4%) and LongMemEval (up to +18.5%, 90% latency
reduction) figures are vendor-reported and are not reproduced by this fixture.

## Privacy

All files here are first-party: scripted synthetic cases, generated CSV, our own script, and run
records describing this machine. No third-party downloads, no credentials, no personal data.
The `history/` directory keeps the prior approved receipt, the r2 review report and the
pre-relocation script so earlier findings stay auditable; those files are not offered as
reader downloads.
