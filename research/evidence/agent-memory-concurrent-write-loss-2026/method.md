# Method - multi-process agent-memory write harness

Artifact: `sqlite_concurrency_matrix.py` (stdlib sqlite3 + multiprocessing, no service, no network).
Run date: 2026-11-12T07:03:16Z. Host: 2 vCPU / 11 GB, kernel 6.17.0-1019-oracle. Python 3.12.3, sqlite3 3.45.1.

## Fixture
One table `memory(id INTEGER PRIMARY KEY, user_id, key, text, seq, updated_at)` over 25 keys (`k00`..`k24`),
1000 intents total (4 writers x 250), per key a monotonically increasing `seq`; intents are shuffled into each
writer's queue, so a key's newest value is not the last one written. Seed 20261112. See `fixture_intents.jsonl`.

## What each pattern does
- P1: `INSERT ... ON CONFLICT(user_id,key) DO UPDATE ... WHERE excluded.seq >= memory.seq` (guard inside the statement)
- P2: `SELECT id,seq` then `UPDATE`/`INSERT`, with a 2 ms sleep between the read and the write (synthetic stand-in
  for embedding/extraction work). The client skips an obviously stale value it *read*. The follow-up write is not
  uniformly unguarded: the row-found branch issues a plain `UPDATE ... WHERE id=?` that carries no `seq` comparison,
  while the row-missing branch attempts an `INSERT` whose `IntegrityError` fallback re-runs the write as
  `UPDATE ... WHERE user_id=? AND key=? AND seq<=?` and so does carry the ordering guard.
- P3: `BEGIN IMMEDIATE; DELETE ...; INSERT ...; COMMIT` - unconditional replace, last writer wins regardless of seq.
- P4: P2 shape on a table with no UNIQUE index.

## Configurations
`journal_mode=delete, busy_timeout=0.1s`; `journal_mode=WAL, busy_timeout=5s`; `journal_mode=WAL, busy_timeout=30s`.
PRAGMA synchronous=FULL. Four writer processes start together; every attempt is logged to JSONL.

## Scoring
- lost-update write: a write that reported success, was not skipped as stale, and whose `seq` is greater than the
  value finally stored for that key (i.e. a newer value was later overwritten by an older one).
- lost-update keys: keys whose final `seq` is below the highest intent generated for that key.
- duplicate keys: keys with more than one row.
- dropped writes: any exception (SQLITE_BUSY surfaces as `OperationalError: database is locked`), counted separately
  and never counted as a completed write.
- p95 latency is over all attempts in the cell, including the wait that ends in a lock error.

## Reproduce

```bash
# main matrix: 4 writers x 250 intents = 1,000 attempts per cell, 3 repeats => 36 cells
python3 sqlite_concurrency_matrix.py --out ./traces --writers 4 --writes 250 --repeats 3

# sensitivity: same 1,000 attempts per cell, synthetic gap raised to 10 ms,
# read-modify-write patterns only
python3 sqlite_concurrency_matrix.py --out ./sensitivity --writers 4 --writes 250 --repeats 1 \
    --patterns P2_read_modify_write,P4_rmw_no_index --rmw-delay-ms 10
```

Each `--out` directory gets one `<pattern>__<config>__r<repeat>.jsonl` trace per cell plus an appended `summary.csv`
whose rows are the columns of the two tables below. `--patterns` selects a subset, `--rmw-delay-ms` is the read-to-write
gap, and the seed, key count, table schema and the three locking configurations are fixed in the script. Note on
provenance: the recorded run's logs (`raw/run.log`, `raw/run_repeats.log`, `sensitivity/run.log`) contain only the
per-cell summary JSON, not the argv line, so the flags above are the configuration those cells necessarily encode
(writers=4, writes_requested=1000, read-modify-write patterns only, 10 ms gap) rather than a captured shell history.
Repeat the cells on your own hardware before trusting the millisecond figures; the ordering results are the part
that reproduces.

## Measured matrix (3 repeats, 2 ms gap)
| pattern | config | cells | writes seen | locked/other errors | lost-update writes | keys w/ stale final | duplicate keys | p95 write latency (s) |
|---|---|---|---|---|---|---|---|---|
| P1_upsert | delete_bt100ms | 3 | 1000 / 1000 | 7-16 | 0 | 0 | 0 | 0.004-0.007 |
| P1_upsert | wal_bt5s | 3 | 1000 / 1000 | 0 | 0 | 0 | 0 | 0.002-0.003 |
| P1_upsert | wal_bt30s | 3 | 1000 / 1000 | 0 | 0 | 0 | 0 | 0.003-0.004 |
| P2_read_modify_write | delete_bt100ms | 3 | 1000 / 1000 | 0-2 | 0 | 0 | 0 | 0.014-0.018 |
| P2_read_modify_write | wal_bt5s | 3 | 1000 / 1000 | 0 | 0-1 | 0-1 | 0 | 0.006-0.008 |
| P2_read_modify_write | wal_bt30s | 3 | 1000 / 1000 | 0 | 0-1 | 0-1 | 0 | 0.006-0.008 |
| P3_delete_insert | delete_bt100ms | 3 | 1000 / 1000 | 70-113 | 365-451 | 24-25 | 0 | 0.101-0.103 |
| P3_delete_insert | wal_bt5s | 3 | 1000 / 1000 | 0 | 446-503 | 24-25 | 0 | 0.003-0.005 |
| P3_delete_insert | wal_bt30s | 3 | 1000 / 1000 | 0 | 430-446 | 24 | 0 | 0.003-0.005 |
| P4_rmw_no_index | delete_bt100ms | 3 | 1000 / 1000 | 3-5 | 0-1 | 0-1 | 1 | 0.01-0.021 |
| P4_rmw_no_index | wal_bt5s | 3 | 1000 / 1000 | 0 | 0-3 | 0-3 | 3-4 | 0.005-0.0095 |
| P4_rmw_no_index | wal_bt30s | 3 | 1000 / 1000 | 0 | 0-2 | 0-2 | 4-10 | 0.006-0.008 |

The P4/wal_bt5s upper bound is the recorded 0.009512 s (`raw/summary.csv`, repeat 2); the article table rounds the
same cell to 0.010 s.

## Sensitivity (1 repeat, 10 ms gap, read-modify-write patterns only)
| pattern | config | writes seen | lost-update writes | duplicate keys | p95 (s) |
|---|---|---|---|---|---|
| P2_read_modify_write | delete_bt100ms | 1000/1000 | 0 | 0 | 0.025 |
| P2_read_modify_write | wal_bt5s | 1000/1000 | 1 | 0 | 0.015 |
| P2_read_modify_write | wal_bt30s | 1000/1000 | 0 | 0 | 0.015 |
| P4_rmw_no_index | delete_bt100ms | 1000/1000 | 1 | 3 | 0.021 |
| P4_rmw_no_index | wal_bt5s | 1000/1000 | 0 | 3 | 0.015 |
| P4_rmw_no_index | wal_bt30s | 1000/1000 | 0 | 5 | 0.015 |

## Not run
SIGKILL/WAL-replay torn-row test; single-writer queue baseline; any vendor cloud store.
