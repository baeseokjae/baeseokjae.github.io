# Method — scoped-retrieval probe (agent-memory-scoped-retrieval-probe-2026)

Run date: 2026-11-14 (UTC). Host: Linux 6.17.0-1019-oracle, 2 vCPU runner.
All numbers in `summary.json` come from the commands below; nothing here is estimated.

## Environment

| item | value |
|---|---|
| python | 3.12.3 (/home/ubuntu/blog-automation/.venv/bin/python) |
| ollama | 0.20.3, local endpoint http://127.0.0.1:11434 |
| embedding model | all-minilm:latest, digest 1b226e2802db, 384 dimensions |
| scoring | exact cosine over every document, no ANN index |
| network | local endpoint only, no external API, no credentials |
| wall clock | 35 s for the full sweep when scoring committed vectors offline |

## Fixture

Generated, deterministic, no real data. 30 tenants (`northwind` … `zorg`), 10 fact
types each (database host, token lifetime, service owner, queue retry budget, region,
cluster version, on-call day, log retention, API rate limit, cache bucket).
Values are drawn from three templates per fact type using a pure integer hash of
(tenant index, fact index), so no two tenants share an identical row, but every row
follows the same `"<fact> for <tenant>: <value>"` template — the confusable-pair
condition. Every row carries the tenant slug, which is deliberately generous to the
post-filter strategy: a lexical matcher can find gold at all.

Queries per tenant: 10 single-gold ("What is the database host for northwind?") and
4 multi-fact pairs ("For northwind, what are the database host and the on-call
handover day?"), 14 per tenant, 168 at 12 tenants and 420 at 30 tenants. The store
holds 10 fact rows per tenant: 120 documents at 12 tenants, 300 at 30.

## Strategies compared on the same vectors

- `post_filter` — global top-k over the whole store, then keep rows whose tenant
  matches the caller (the list-comprehension pattern under test).
- `scoped` — restrict the candidate set to the caller's tenant, then rank.
- `leak` — the raw global top-k handed to the prompt with no filter at all.

## Reproduce

    cd research/evidence/agent-memory-scoped-retrieval-probe-2026
    # full re-embed (needs local ollama with all-minilm)
    python3 harness.py --out .
    # rescore the committed vectors, no network
    python3 harness.py --out . --offline --vectors vectors.json
    # reader-facing probe exercised against the reference adapter
    python3 isolation_probe.py --selftest --tenants northwind,contoso,globex

`harness.py` writes `fixture.jsonl`, `vectors.json`, `results.jsonl` (one row per
query × strategy × k) and `summary.json` (per-configuration aggregates). Re-running
on the committed vectors reproduces identical counts; the only nondeterminism in the
pipeline would be the embedding server, and its output is committed.

## Limits

- Tenants are synthetic and disjoint. Real stores mix tenants with wildly unequal
  document counts, and per-tenant over-representation changes both the under-fill
  distribution and the foreign-row share.
- The fixture is a flat, exact-cosine scan. A production ANN index adds approximation
  error on top of the effect measured here; the direction is not necessarily additive.
- Scores come from one small embedding model (384 dimensions). Larger models separate
  tenants better, which shrinks the leak surface but does not change the fill
  arithmetic: after top-k, at most k rows survive, and fewer when foreign rows rank
  inside k.
