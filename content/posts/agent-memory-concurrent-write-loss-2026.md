---
title: "Two Writers, One Memory: What Concurrent Agent Writes Actually Lose (2026)"
date: 2026-11-12T07:12:00+00:00
lastmod: 2026-11-25T12:24:00+00:00
description: "Four writer processes, 1,000 writes per cell over 25 keys, three locking configurations: an unconditional delete-then-insert replace lost 365-503 of every 1,000 attempted writes to stale overwrites, while a guarded UPSERT lost none. Stdlib harness, published summary cells and the exact SQL."
draft: false
tags:
  - concurrent agent memory writes
  - sqlite lost update
  - agent memory race condition
  - upsert vs read modify write
  - database is locked agent
  - wal mode busy timeout
  - multi-agent memory store
  - sqlite concurrency test
  - duplicate memory rows
  - agent memory write pattern
cover:
  image: /images/agent-memory-concurrent-write-loss-2026-presentation.png
  alt: 'Bar chart of lost-update writes per 1,000 attempts from this article''s own SQLite run: guarded UPSERT 0, client read-modify-write 0 to 1, delete-then-insert replace 365 to 503, read-modify-write without a unique index 0 to 3. Caption notes four processes, 25 keys and a single 2-vCPU host, and that every lost update was a client ordering pattern, not a store fault.'
  caption: 'Lost-update writes per 1,000 attempts, by write pattern · local fixture, not vendor data'
schema: "schema-agent-memory-concurrent-write-loss-2026"
---

Your planner and two worker subagents write observations into the same `memory` table. Nobody sees a problem, because the recall test runs one writer at a time and every assertion passes. Then a decision recorded at step 40 is silently replaced by the version from step 12, the same preference appears three times and occupies the top-k slots that should have surfaced the one fact that mattered, or a worker exits with `sqlite3.OperationalError: database is locked` and the harness records the write as completed because it never checked.

I ran that situation as a controlled experiment: four OS processes, 1,000 write attempts per cell, 25 keys, four write patterns, three locking configurations, three repeats each, Python's standard `sqlite3` only. The short answer is narrower than the usual warning about concurrency. SQLite never lost a committed row. Every loss I measured was a client pattern writing an older value after a newer one, and the pattern that did it is the one most memory libraries reach for when a fact is "replaced": delete the old row, insert the new one.

The guarded single-statement UPSERT lost nothing in any configuration. The delete-then-insert replace lost 36-50% of its attempted writes to a stale overwrite, and turning WAL on made that number slightly worse, because WAL removes lock waits, not ordering mistakes.

## Three failure modes, only one of which the store can prevent

The interesting part is that these are not variations of one problem. They fail at different layers, and each has a different fix.

A lost update is a correctness bug in the client's ordering logic. Two writers both compute the next state from a value they read earlier; the later commit carries the older intent. The store accepted both writes and reported success twice. Nothing in the database is corrupt, and no error appears in any log.

A duplicate row is a schema bug. Two processes both see no row for `(user_id, key)` and both insert. Without a uniqueness constraint the table now has two truths for one fact, and every subsequent read has to guess.

A dropped write is an error-handling bug. `SQLITE_BUSY` surfaces as an exception after the connection's wait budget expires. If the caller swallows it, retries it in a loop that ends in `pass`, or marks the batch complete because the process did not crash, the agent's memory is now missing an observation it will never look for again.

## What SQLite actually guarantees

SQLite serializes writers at the file level: one write transaction at a time per database file. That is the guarantee, and it is enough to make a single well-formed statement atomic. It is not enough to make a sequence of statements atomic, and it says nothing about which of two writers holds the newer fact.

WAL mode changes reader/writer blocking, not writer/writer ordering. The SQLite documentation is explicit that WAL gives more concurrency because readers do not block writers and writers do not block readers, and equally explicit that this is "mostly" true: a query against a WAL-mode database can still return `SQLITE_BUSY`, so applications should be prepared for that (https://sqlite.org/wal.html#sometimes_queries_return_sqlite_busy_in_wal_mode).

`busy_timeout` is a wait budget, not a queue. It is the per-connection number of milliseconds a lock conflict waits before surfacing as an error (https://sqlite.org/pragma.html#pragma_busy_timeout). When it expires, your code decides what happens next, and in too many harnesses that decision is "log and continue".

`BEGIN DEFERRED` does not take the write lock until the first write statement runs, and that upgrade can itself return `SQLITE_BUSY`; `BEGIN IMMEDIATE` takes the write lock up front (https://sqlite.org/lang_transaction.html). This is the difference between a transaction that fails at a predictable point and one that fails halfway through a read-modify-write.

`UPSERT` exists only in relation to a uniqueness constraint. `INSERT ... ON CONFLICT(user_id, key) DO UPDATE` requires a PRIMARY KEY or UNIQUE constraint on the conflict target (https://sqlite.org/lang_UPSERT.html). Without the index, the same statement raises `ON CONFLICT clause does not match any PRIMARY KEY or UNIQUE constraint` — I hit exactly that in the harness's first smoke run, where the statement failed until the schema was corrected. The index is not an optimization for this design; it is the thing that makes the design expressible.

And a scope limit that matters for anyone running agents on shared infrastructure: SQLite's locking assumes all processes reach the same file on the same host. Network filesystems are outside that assumption (https://sqlite.org/whentouse.html).

## The harness

The point of building it was to stop arguing from the docs. The artifact is `sqlite_concurrency_matrix.py`, standard library only: `sqlite3`, `multiprocessing`, `json`, no service, no network, no paid API. One table, `memory(id INTEGER PRIMARY KEY, user_id, key, text, seq, updated_at)`, over 25 keys, and a fixture of 1,000 intents (4 writers x 250) where each key carries a monotonically increasing `seq`. Intents are shuffled into each writer's queue, so the newest value for a key is almost never the last one written — that shuffle is what makes ordering errors visible at all. Seed is fixed at 20261112.

Four patterns, each a shape that real memory code uses:

- P1 — one statement: `INSERT ... ON CONFLICT(user_id,key) DO UPDATE SET ... WHERE excluded.seq >= memory.seq`. The ordering guard lives inside the statement, so it is evaluated under the same lock that performs the write.
- P2 — client-side read-modify-write: `SELECT id, seq`, then `UPDATE` or `INSERT`, with a 2 ms pause between the two to stand in for the work a library does in between (embedding, LLM extraction, fact reconciliation). The client skips a value it already read as stale. On the row-found path the write is a plain `UPDATE ... WHERE id=?` with no version check, so nothing stops it from overwriting a newer commit that landed during the pause. On the row-missing path it attempts an `INSERT`; if a unique index makes that insert lose the race, the `IntegrityError` fallback re-runs the write as an `UPDATE ... WHERE user_id=? AND key=? AND seq<=?`, so that branch does carry the ordering guard.
- P3 — delete-then-insert "replace" inside `BEGIN IMMEDIATE ... COMMIT`: unconditional, last writer wins regardless of `seq`.
- P4 — the P2 shape against a table with no UNIQUE index, to isolate what the constraint is buying.

Three configurations: rollback journal with `busy_timeout=0.1s`; WAL with `busy_timeout=5s`; WAL with `busy_timeout=30s`. `synchronous=FULL` throughout. Each cell is 1,000 attempted writes from four processes started together, repeated three times.

Scoring is deliberately conservative. A write counts as a lost update only if it reported success, was not skipped as stale, and its `seq` is greater than the value finally stored for that key — that is, a newer value was later overwritten by an older one. "Keys with stale final" counts keys whose final `seq` is below the highest intent generated for that key. Dropped writes are counted separately and never counted as completed. Latency percentiles include the wait that ends in a lock error.

## Results

Per-cell counts from three repeats, 1,000 attempts each:

| pattern | config | locked/other errors | lost-update writes | keys w/ stale final | duplicate keys | p95 write latency (s) |
|---|---|---|---|---|---|---|
| P1_upsert | delete_bt100ms | 7-16 | 0 | 0 | 0 | 0.004-0.007 |
| P1_upsert | wal_bt5s | 0 | 0 | 0 | 0 | 0.002-0.003 |
| P1_upsert | wal_bt30s | 0 | 0 | 0 | 0 | 0.003-0.004 |
| P2_read_modify_write | delete_bt100ms | 0-2 | 0 | 0 | 0 | 0.014-0.018 |
| P2_read_modify_write | wal_bt5s | 0 | 0-1 | 0-1 | 0 | 0.006-0.008 |
| P2_read_modify_write | wal_bt30s | 0 | 0-1 | 0-1 | 0 | 0.006-0.008 |
| P3_delete_insert | delete_bt100ms | 70-113 | 365-451 | 24-25 | 0 | 0.101-0.103 |
| P3_delete_insert | wal_bt5s | 0 | 446-503 | 24-25 | 0 | 0.003-0.005 |
| P3_delete_insert | wal_bt30s | 0 | 430-446 | 24 | 0 | 0.003-0.005 |
| P4_rmw_no_index | delete_bt100ms | 3-5 | 0-1 | 0-1 | 1 | 0.010-0.021 |
| P4_rmw_no_index | wal_bt5s | 0 | 0-3 | 0-3 | 3-4 | 0.005-0.010 |
| P4_rmw_no_index | wal_bt30s | 0 | 0-2 | 0-2 | 4-10 | 0.006-0.008 |

Four things in that table are worth the price of the experiment.

The delete-then-insert replace is the only pattern that loses a large share of its writes, and WAL does not help it. At the 0.1 s configuration it lost 365-451 of 1,000 attempts; with WAL at 5 s it lost 446-503, at 30 s 430-446. The lock configuration changed the error count from 70-113 to zero and left the loss rate untouched, because the loss is not caused by waiting. Deleting the old row and inserting the new one under `BEGIN IMMEDIATE` is atomic per key, but it is not ordered: whichever transaction commits second wins, and the second committer is frequently the writer that started earlier with an older observation. Final state was stale for 24 or 25 of the 25 keys in every P3 cell.

The guarded UPSERT lost nothing, anywhere. Zero lost updates, zero duplicate keys, 25 rows at the end of every cell, at all three configurations and all three repeats. Because the `WHERE excluded.seq >= memory.seq` clause is part of the same statement as the write, no other writer can interleave between the comparison and the row update. This is not a performance trick; it is the only pattern in the matrix whose ordering check and write are indivisible.

The unique index, not the UPSERT syntax, is what prevents duplicates. P4 keeps P2's client logic but drops the constraint, and duplicate keys appear immediately: 1 at the 0.1 s configuration, 3-4 with WAL at 5 s, 4-10 at 30 s. WAL's extra write concurrency makes the window wider, not narrower, which is the honest reading of that column rather than a WAL defect.

Client-side read-modify-write is not, at this scale, the main loser — but one of its two write paths is still an unguarded window. P2 produced 0 lost updates in the rollback-journal configuration and 0-1 in the WAL cells, both with a 2 ms gap and in the separate one-repeat 10 ms sensitivity run. The harness's stale-skip check after the read is doing most of that work: it discards a value it already saw as outdated, and its insert-race fallback carries an `AND seq<=` guard. What remains unguarded is the `UPDATE ... WHERE id=?` branch taken when the row already existed at read time: that statement never compares the stored `seq`, so it will happily overwrite a newer commit. The residual 0-1 is exactly that case — the value it read was still current, another writer committed a newer one during the pause, and the UPDATE landed on top. Do not read this row as "read-modify-write is safe"; read it as "this particular client guard removes most of the risk at this level of contention, except on the one branch where the write carries no version."

Dropped writes tracked the wait budget, not the journal mode. At the 0.1 s `busy_timeout`, 7-16 of 1,000 P1 writes and 70-113 of 1,000 P3 writes raised `OperationalError: database is locked`; every cell with a 5 s or 30 s budget completed all 1,000. p95 latency for P3 at 0.1 s sat at 0.101-0.103 s, i.e. the full timeout spent waiting before failing — a useful signature, because it means a latency graph pinned at your timeout value is not "slow writes", it is a queue of failed ones. This run never encountered the residual WAL busy cases the documentation warns about; that is a statement about this workload, not evidence that WAL cannot return `SQLITE_BUSY`.

## Choosing between a queue, per-agent stores, and an UPSERT

Given those four results, the three options a team actually debates sort cleanly.

A single writer with a queue removes the entire class of problem, and it is the right default when write volume is low and one process can own the table. It also serializes your throughput behind one task, and it does not survive the thing that actually happens in production: a retried run and the run it replaced both alive for a few seconds, each believing it owns the writer role.

Per-agent stores trade one contention point for a merge problem. They make P3-style replace patterns harmless inside each store and guarantee that no two writers touch the same row — at the cost of a read path that has to reconcile N stores, which is the same ordering question moved to query time with less information available.

An UPSERT with a sequence or version guard is what the matrix supports when more than one process must write. The requirements are concrete: a UNIQUE or PRIMARY KEY constraint on `(user_id, key)`; a monotonically increasing version column written by the client, not by wall-clock time, because two hosts can agree on the second and disagree on the order; the ordering comparison inside the same statement as the write; and a check on the returned row count so a guard that rejects an older write is visible rather than silent.

Whatever you choose, log the three things this experiment needed to see the failures at all. Log the intended `seq` or version next to the accepted one. Log every `OperationalError` with its pattern name, so a batch of 70-113 locked writes cannot be mistaken for a successful run. And keep the row count per key in your health output, because the duplicate-key column in the table above is invisible in any recall or relevance metric — it only shows up when you count rows.

If you want the ordering question in its broader context — which failures belong to the write path at all, and how to attribute them — the write-path reliability protocol sets out a serial, single-operator write path and its failure taxonomy at https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/; that protocol assumes one writer by construction, which is precisely the assumption this experiment removes. The delete-then-insert pattern above is also what a naive "replace" does after a delete test, so the read-back methodology in https://baeseokjae.github.io/posts/agent-memory-delete-semantics-test-2026/ is the right companion check; the other way a store quietly returns the wrong neighbour is an embedding swap, covered at https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/. If your agents coordinate through locks rather than a shared table, https://baeseokjae.github.io/posts/peerbridge-mcp-coordination-2026/ covers that layer instead.

## What this does not measure

The experiment is SQLite 3.45.1 through Python 3.12.3's standard library, on one 2 vCPU / 11 GB Linux host, four processes on one filesystem. It is evidence about SQLite locking semantics and about client write patterns. No vendor memory service, cloud or self-hosted, was tested, and nothing here should be read as a claim about how any product serializes writes.

The 2 ms and 10 ms gaps in P2 and P4 are synthetic stand-ins for the work a library performs between reading a fact and writing it back. They are not measured vendor latencies, and a real embedding call of 200 ms would widen that window considerably — which is the direction the sensitivity run hints at, not a magnitude it establishes.

Each cell is 1,000 attempts over 25 keys, so two writers collide on a key often, and the rates are per-attempt at this scale only. Zero counts over 1,000 attempts bound a rate loosely; "P1 lost nothing here" is not a proof for all loads. The planned SIGKILL / WAL-replay torn-row test was not run in this attempt, so nothing in this article speaks to crash recovery. The fixture uses 250 intents per writer rather than the 500 originally planned, a reduction made to fit the attempt budget with writers and configurations unchanged; it changes how often two writers touch the same key.

## Reproduce it

Everything below is first-party and runs on a laptop with no credentials and no network. The harness is https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-concurrent-write-loss-2026/sqlite_concurrency_matrix.py, the fixture is https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-concurrent-write-loss-2026/fixture_intents.jsonl, and the method with the exact commands and per-cell notes is https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-concurrent-write-loss-2026/method.md.

The summary rows behind the table are https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-concurrent-write-loss-2026/raw/summary.csv (one row per cell per repeat) and the 10 ms sensitivity cells are https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-concurrent-write-loss-2026/sensitivity/summary.csv. The per-write JSONL traces from the recorded run (36 cell files, about 3.3 MB) are not in the repository; they are regenerated by the command below, and https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-concurrent-write-loss-2026/raw-records-manifest.json is the recorded run's inventory — host, versions and a SHA-256 per trace file — so you can compare your own trace set against what the run that produced this article actually wrote.

```bash
python3 sqlite_concurrency_matrix.py --out ./traces --writers 4 --writes 250 --repeats 3
```

Writer count, per-writer intent count, seed, key count and the three locking configurations are set in the script; the flags above reproduce the matrix in this article exactly. The script writes one JSONL record per attempted write (pattern, config, writer, key, intended `seq`, outcome, latency) plus a per-cell summary row, so a failed write appears as a failed write and not as an absent line. Point it at your own schema and your own contention level before you trust any of the numbers above for your workload; the whole matrix takes under two minutes on the host used here, and one cell's trace is around 90-100 KB, small enough to diff between runs.

The one-line version: the race is not in the store, it is in whichever of your write paths deletes a row and inserts another one, or reads a value and writes it back without carrying the version it read. Add the uniqueness constraint, put the ordering comparison inside the statement, and log what the guard rejected.
