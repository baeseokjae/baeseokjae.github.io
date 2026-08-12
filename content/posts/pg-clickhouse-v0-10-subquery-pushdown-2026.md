---
title: "pg_clickhouse v0.10 Subquery Pushdown: 1000x Faster TPC-H Queries in 2026"
date: 2026-08-12T19:02:15+00:00
tags:
  - pg_clickhouse
  - ClickHouse
  - PostgreSQL
  - subquery pushdown
  - TPC-H
  - foreign data wrapper
description: "pg_clickhouse v0.10 pushes correlated subqueries into ClickHouse, cutting TPC-H Q17 from 32.7s to 37ms. Here's how it works and how to verify it."
draft: false
cover:
  image: "/images/pg-clickhouse-v0-10-subquery-pushdown-2026.png"
  alt: "pg_clickhouse v0.10 Subquery Pushdown: 1000x Faster TPC-H Queries"
  relative: false
schema: "schema-pg-clickhouse-v0-10-subquery-pushdown-2026"
---

pg_clickhouse v0.10, released August 11, 2026, finally pushes correlated subqueries (SubPlans) down into ClickHouse, moving the TPC-H scoreboard from 12 to 16 of 22 queries fully pushed down. The headline result is TPC-H Q17, which dropped from 32.7 seconds to 37 milliseconds — roughly 880x faster and beating native PostgreSQL's 2.1 seconds. This guide explains how subquery pushdown works, how to verify it with EXPLAIN, and what you need to upgrade to take advantage of it.

## What is pg_clickhouse and why does subquery pushdown matter?

pg_clickhouse is a PostgreSQL extension that lets you run analytics queries on ClickHouse from PostgreSQL without rewriting your SQL. It works as a foreign data wrapper (FDW): you define ClickHouse tables as foreign tables in Postgres, and the extension's planner hooks teach PostgreSQL to push as much of the query as possible down to ClickHouse as a single Remote SQL statement.

The whole point is to avoid the classic FDW failure mode: pulling rows back to Postgres and doing the heavy work locally. When pushdown works, ClickHouse does the aggregation, filtering, and joining, and Postgres only sees the final result. When it fails, Postgres falls back to fetching every row and evaluating the query one row at a time — which is catastrophically slow for analytics workloads.

Subquery pushdown is the missing piece that finally makes correlated subqueries run entirely on ClickHouse. Before v0.10, a correlated subquery like "average quantity per part" forced Postgres to make one ClickHouse round trip per outer row, evaluating the subquery locally each time. With v0.10, the whole comparison — including the subquery — ships to ClickHouse as a single Remote SQL statement.

## The TPC-H scoreboard: from 12 to 16 of 22 queries fully pushed down

The TPC-H benchmark is the standard stress test for analytics engines, and pg_clickhouse tracks how many of its 22 queries it can push down completely. The progress has been steady:

| Version | TPC-H queries fully pushed down |
|---------|--------------------------------|
| v0.1 (Dec 2025 launch) | 3 of 22 |
| v0.2 (Dec semi-join work) | 12 of 22 |
| v0.10 (Aug 2026) | 16 of 22 |

The jump from 3 to 12 came from teaching the planner to push a whole correlated EXISTS subquery down as a single LEFT SEMI JOIN instead of a nested loop with one ClickHouse round trip per outer row. The jump from 12 to 16 in v0.10 came from SubPlan (subquery) pushdown, which handles the correlated subqueries that the semi-join work couldn't reach.

Only 6 queries remain unpushed: Q13, Q15, Q16, Q18, Q20, and Q21. These are blocked by a deparser limitation — they have join trees on both sides of the query, which the current deparser can't translate into a single Remote SQL statement. That's a known roadmap item, not a fundamental blocker.

## The trophy case: TPC-H Q17 from 32.7s to 37ms

The most dramatic result in v0.10 is TPC-H Q17, a correlated subquery that averages `l_quantity` per part. Here's the before-and-after:

| Engine / version | Q17 execution time |
|------------------|--------------------|
| pg_clickhouse v0.3 (local eval per row) | 32.7 seconds |
| Native PostgreSQL | 2.1 seconds |
| pg_clickhouse v0.10 (fully pushed down) | 37 milliseconds |

That's roughly 880x faster than v0.3 and about 57x faster than native PostgreSQL. The reason is simple: in v0.3, Postgres evaluated the correlated subquery locally, making a ClickHouse round trip for every outer row. In v0.10, the entire query — outer query and subquery together — runs as one statement inside ClickHouse.

Q17 isn't the only win. TPC-H Q2 dropped from 3,446ms in v0.3 to 24ms in v0.10, and Q22 dropped from 1,415ms to 45ms (pushed as multiple foreign scans). These are the same order-of-magnitude improvements: when a query stops round-tripping per row and runs entirely in ClickHouse, milliseconds replace seconds.

## How subquery (SubPlan) pushdown works

The core idea is elegant: subqueries in Postgres become subqueries in ClickHouse. When pg_clickhouse's planner hook encounters a SubPlan — a correlated subquery in the WHERE clause, SELECT list, or HAVING — it now translates that subquery into ClickHouse SQL and embeds it in the Remote SQL statement sent to the server.

Before v0.10, a correlated subquery was evaluated locally: Postgres would fetch the outer rows, then for each row issue a separate ClickHouse query to evaluate the subquery. That's the per-row round trip that made Q17 take 32.7 seconds. With SubPlan pushdown, the deparser builds one Remote SQL statement that contains the outer query and the subquery, and ClickHouse evaluates the whole thing in a single pass.

You can see this directly in the query plan. When you run EXPLAIN on a pushed-down query, the Remote SQL statement now shows the entire comparison — including the subquery — in one statement, rather than a separate foreign scan per subquery evaluation.

## Verifying pushdown with EXPLAIN (VERBOSE, COSTS OFF)

The most important practical skill is verifying that your query actually pushed down. The command is:

```sql
EXPLAIN (VERBOSE, COSTS OFF)
SELECT ... FROM clickhouse_table WHERE ...;
```

Look for the `Remote SQL` line in the output. If pushdown worked, you'll see a single foreign scan whose Remote SQL contains the full query — including the subquery. If pushdown failed, you'll see a nested loop or a separate foreign scan per row, which is the local-evaluation fallback.

For a correlated subquery, the telltale sign of success is that the subquery appears inside the Remote SQL statement rather than as a separate scan. If you see the subquery evaluated as its own foreign scan with a nested loop join, the query is running locally and you're paying the per-row round-trip cost.

## NOT IN and the IN/NULL semantics rabbit hole

The hardest part of subquery pushdown isn't the mechanics — it's getting the semantics right. ClickHouse evaluates `IN` under two-valued logic (true/false), while PostgreSQL uses three-valued logic (true/false/NULL). This difference can silently invert results for queries involving NULLs.

Here's the problem: in PostgreSQL, `x NOT IN (SELECT ...)` returns NULL (not true) when the subquery contains a NULL, because NULL comparisons are unknown. In ClickHouse's two-valued logic, the same expression might return true. If pg_clickhouse pushed the query down naively, results would silently change.

v0.10 solves this with compensating CASE guards. The extension tracks how each expression result is consumed and wraps nullable cases in a CASE expression that reproduces PostgreSQL's three-valued semantics. It also sets `transform_null_in 0` in the default `pg_clickhouse.session_settings`, so server profiles can't silently change IN semantics.

The practical takeaway: if you declare columns NOT NULL, pg_clickhouse can ship the cheaper unguarded form of the pushdown, because there's no NULL to worry about. Nullable columns force the guarded CASE form, which is still correct but slightly more expensive.

## Prerequisites: ClickHouse 25.8+ and the version gate

Subquery pushdown is not free — it requires a recent ClickHouse server. The correlated-subquery SQL shape that pg_clickhouse generates needs ClickHouse 25.8 or later. If you're running an older ClickHouse server, pg_clickhouse falls back to local evaluation, and you lose the speedup.

This is a key upgrade consideration. pg_clickhouse itself supports PostgreSQL 13+ and ClickHouse v23+ (minimum ClickHouse 23.3), but the headline subquery pushdown feature specifically requires ClickHouse 25.8+. If you're on an older ClickHouse, you'll still get the other v0.10 improvements, but Q17-style correlated subqueries will run locally.

## Maximizing pushdown: NOT NULL columns and IMPORT FOREIGN SCHEMA

To get the most out of pushdown, you want to maximize the number of queries that ship to ClickHouse in the cheap, unguarded form. The single biggest lever is declaring columns NOT NULL.

When you use `IMPORT FOREIGN SCHEMA`, pg_clickhouse auto-declares non-Nullable ClickHouse columns as NOT NULL in the foreign table definition. This maximizes pushdown because NOT NULL columns let the extension use the cheaper unguarded form of IN and NOT IN pushdown — no compensating CASE guards needed.

If you define foreign tables manually, declare your columns NOT NULL yourself where you know they can't be null. Every nullable column is a potential reason for pg_clickhouse to fall back to the guarded form or to local evaluation.

## What else is new in v0.10: aggregates, drivers, and the new query/perform API

Subquery pushdown is the headline, but v0.10 ships a lot more:

- **Broadened pushdown**: statistical aggregates (`corr`, `covar_pop`/`covar_samp`, `stddev`, `var`, `any_value`), ordered-set aggregates (`percentile_cont`/`percentile_disc` → `quantiles`/`quantileExactLow`), partitionwise aggregation, `encode(bytea, ...)`, 3-arg `ltrim`/`rtrim`/`btrim`, and interval arithmetic on date/timestamp.
- **Driver rebuild**: the binary driver is rebuilt on the ClickHouse/clickhouse-c C client (v0.3.1), the HTTP driver now uses the Native format, `fetch_size` is deprecated, inserts flush at 64MiB, and per-scan connections fix concurrency crashes.
- **New API surface**: `clickhouse_query(server, sql)` and `clickhouse_server_version(server)` functions, plus a `CALL clickhouse_perform(server, sql)` procedure. `clickhouse_raw_query()` is deprecated.

One important architectural note: builtin function pushdown has been opt-in since v0.3.0, to preserve PostgreSQL semantics (for example, trig functions raise an error in Postgres but return NaN in ClickHouse). The pushdown list is deliberately conservative so you can trust it.

## What's left: the 6 remaining TPC-H queries and the roadmap

The 6 remaining TPC-H queries — Q13, Q15, Q16, Q18, Q20, and Q21 — are blocked by a deparser limitation: they have join trees on both sides of the query, which the current deparser can't translate into a single Remote SQL statement. This is a known, well-scoped roadmap item rather than a fundamental limitation.

The broader roadmap from the original launch post also included ClickBench pushdown, all aggregates and functions, comprehensive subquery pushdown, server/user-level settings, all ClickHouse data types, lightweight DELETE/UPDATE, and batch COPY. Subquery pushdown in v0.10 is a major step on that path.

## Getting started: Docker quickstart and a minimal example

The fastest way to try pg_clickhouse v0.10 is the official Docker image:

```bash
docker run ghcr.io/clickhouse/pg_clickhouse:18
```

Then, in PostgreSQL, create the extension and import your ClickHouse schema:

```sql
CREATE EXTENSION pg_clickhouse;

IMPORT FOREIGN SCHEMA public
  FROM SERVER clickhouse_svr
  INTO public;
```

With the foreign tables in place, you can run analytics queries directly from Postgres. To confirm subquery pushdown is working, run your query through `EXPLAIN (VERBOSE, COSTS OFF)` and check that the Remote SQL contains the subquery. If you're on ClickHouse 25.8+ and your columns are declared NOT NULL, you should see the full query — subquery included — pushed down as a single foreign scan.

## FAQ

**What is pg_clickhouse subquery pushdown?**
It's a feature in pg_clickhouse v0.10 that translates correlated subqueries (SubPlans) in PostgreSQL into subqueries in ClickHouse, so the entire query runs as one Remote SQL statement instead of Postgres evaluating the subquery locally with a round trip per outer row.

**How much faster is pg_clickhouse v0.10 for TPC-H queries?**
TPC-H Q17 dropped from 32.7 seconds (v0.3, local evaluation) to 37 milliseconds (v0.10, fully pushed down) — roughly 880x faster and beating native PostgreSQL's 2.1 seconds. Q2 dropped from 3,446ms to 24ms, and Q22 from 1,415ms to 45ms.

**Does pg_clickhouse subquery pushdown require a specific ClickHouse version?**
Yes. The correlated-subquery SQL shape requires ClickHouse 25.8 or later. On older ClickHouse servers, pg_clickhouse falls back to local evaluation. pg_clickhouse itself supports PostgreSQL 13+ and ClickHouse v23+.

**How do I verify that a query was pushed down?**
Run `EXPLAIN (VERBOSE, COSTS OFF)` and inspect the Remote SQL line. If pushdown worked, the full query — including the subquery — appears in a single foreign scan's Remote SQL. If it failed, you'll see a nested loop or a separate foreign scan per row.

**Why does NOT IN behave differently in ClickHouse and PostgreSQL?**
ClickHouse uses two-valued logic (true/false) while PostgreSQL uses three-valued logic (true/false/NULL), which can silently invert results for NULLs. v0.10 adds compensating CASE guards and sets `transform_null_in 0` by default to preserve PostgreSQL semantics. Declaring columns NOT NULL enables the cheaper unguarded pushdown form.
