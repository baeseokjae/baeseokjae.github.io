# Fixture: does a read-only debugging envelope actually refuse the write?

Files in this directory:

| File | What it is |
|---|---|
| `envelope.json` | The policy file: deny-by-default tool allowlist, per-tool guards, scope (environment, database, service, row cap, statement timeout). |
| `fixture_check.py` | Self-contained runner (Python standard library only, no network, no API key, no model). Seeds a six-row SQLite database, probes the database layer, then drives nine tool calls through the policy gate and writes the audit record. |
| `observed.json` | The record of one run on 2026-11-16: every database probe, every tool call with its decision and rule, the audit record per call, and the before/after table fingerprint. |

## Rerun

```sh
cd research/evidence/hyperprobe-readonly-debugging-agents-2026
python3 fixture_check.py
```

The script rebuilds `fixture.db` from the seed SQL on every run and overwrites
`observed.json`. It prints a summary and exits 0. A run took 5.6 ms of measured
work on the host that produced `observed.json` (Python 3.12.3, SQLite 3.45.1,
Linux). That
number is the fixture's own wall clock and says nothing about probe overhead in
a running service.

## What the run measures

1. **Database layer.** With `PRAGMA query_only = ON`, six of seven statements
   are refused: five raise `OperationalError: attempt to write a readonly
   database` (INSERT, UPDATE, DELETE, CREATE TABLE, CREATE TEMP TABLE) and the
   sixth, an insert into the temp table that was never created, raises
   `no such table: scratch`. The `SELECT` through the view returns rows.
2. **Policy layer.** Nine calls: four allowed, five refused, four distinct
   rules fired (`TOOL_DENIED`, `SQL_NOT_SELECT`, `SQL_MULTI_STATEMENT`,
   `EXPR_CALL`). Every refusal is returned to the caller as a message that
   names the rule.
3. **Audit record.** Thirteen fields are declared: `session_id`, `seq`, `ts_utc`,
   `actor_agent_id`, `actor_model_id`, `policy_sha256`, `tool`, `args_sha256`,
   `decision`, `rule_id`, `scope`, `result_sha256`, `result_bytes`. That set has no
   run ID separate from the session, and no redaction-event, retention/immutability or
   side-effect-assertion field, so it cannot answer the last three questions in the
   article's audit-field table. Nine of the thirteen declared fields are non-null on
   every record. The four that are null somewhere are the interesting part:
   `actor_model_id` (no model ran), `rule_id` (null on the allowed path, so the
   record cannot say which rule let a call through), and `result_sha256` /
   `result_bytes` (null on denials, so a denied call carries no evidence that
   nothing ran).
4. **Integrity.** The orders table fingerprint is identical before and after
   the session, and all six rows remain.

## What this run does not measure

- It is a scripted client. Which tools a language model chooses, whether it
  retries after a refusal, and how it reacts to the refusal message were not
  observed. No model was invoked, locally or remotely.
- The expression guard is a small AST check written for this fixture. It is not
  `Runtime.evaluate`'s `throwOnSideEffect`, and it is not any vendor's
  implementation.
- SQLite's `query_only` is not PostgreSQL's `SET TRANSACTION READ ONLY`. The
  PostgreSQL documentation permits writes into temporary tables inside a
  read-only transaction; this fixture's engine refused the temp-table create.
  The two mechanisms are compared in the article, never substituted for one
  another.
- Single process, single file, no concurrency: no latency, throughput or
  overhead claim is supported.

## Data

All rows are synthetic (`a@example.invalid` … `f@example.invalid`), and the log
fixture is three invented lines. No customer data, no vendor data, no
credentials, and nothing downloaded from a third party is included.
