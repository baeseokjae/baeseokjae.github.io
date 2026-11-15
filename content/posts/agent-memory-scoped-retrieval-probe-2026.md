---
title: "Scoped Agent Memory: Why a Post-Filtered Top-k Returns One or Two Rows and Ships the Rest to the Model (2026)"
date: 2026-11-14T19:12:40+00:00
lastmod: 2026-11-14T19:12:40+00:00
description: "A 12-tenant, 168-query probe of the search-then-filter pattern: the caller received 1.80 of the 5 requested rows on average while 3.20 of the unfiltered top-5 belonged to other tenants. Includes an adapter-agnostic probe, the exact fixture, and the CI assertions that keep the filter before ranking."
draft: false
tags:
  - agent memory isolation
  - post-filter top-k
  - multi-tenant vector store
  - scoped retrieval
  - under-filled context window
  - cross-tenant leakage
  - metadata pre-filter
  - agent memory probe
  - pgvector iterative scan
  - retrieval filter placement
schema: "schema-agent-memory-scoped-retrieval-probe-2026"
---

A team keeps every user's or tenant's memories in one vector collection and enforces isolation in application code. The search returns the nearest neighbours, then a list comprehension keeps the rows that belong to the caller:

```python
rows = store.search(query, k=5)
rows = [r for r in rows if r["tenant_id"] == caller]
```

That reads as correct. It is also the pattern this page measures, and on a synthetic 12-tenant store it produced two failures that raise nothing and log nothing. The caller received 1.80 of the 5 rows requested, on average, across 168 queries - minimum 1, and 98.2% of queries came back short. In the same fixture, 3.20 of the 5 rows in the unfiltered top-5 belonged to other tenants, which means any code path that assembles the prompt before filtering, or simply loses the filter in a refactor, hands other customers' facts to the model.

The probe, the fixture, the vectors and the per-query result rows behind every number below are downloadable, and the section on running it against your own store needs no labelled data.

## The two-line pattern that looks correct

The arithmetic is the whole story. A top-k search returns at most k rows. If j of those rows belong to other tenants, a post-filter can only return k minus j, and it cannot return anything else - the ranker has already discarded every row below position k, including the caller's own rows. Nothing about the store is broken in this scenario; the store answered the question it was asked. The bug is that the question was global and the answer was treated as scoped.

Two call paths make it worse. The first is prompt assembly: some code fetches context, formats it, and filters later, or filters only for display. The second is a second call site - a summariser, a tool wrapper, a background consolidation job - that was written from an older snippet without the filter. Both are invisible to a test that asserts the store returns k rows, because the store does.

At a coarse level the ceiling generalises to any store, embedder or index: post-filtering a top-k can never return more than the k rows that were ranked. How far below k it falls depends on how many foreign rows rank above the caller's rows, which is what the rest of this page measures.

## What 12 tenants actually return

The harness scores exact cosine over every document - no ANN index, so approximation error cannot be mistaken for the effect - and compares three strategies on the same vectors: `post_filter` (global top-k, then filter in application code), `scoped` (restrict the candidate set to the caller, then rank), and `leak` (hand the raw global top-k to the prompt with no filter).

The fixture is 30 synthetic tenants with 10 fact types each (database host, token lifetime, service owner, queue retry budget, region, cluster version, on-call day, log retention, API rate limit, cache bucket). Every row follows the same `"<fact> for <tenant>: <value>"` template - the confusable-pair condition - and every row carries the tenant slug, which is generous to the post-filter: a lexical matcher can find the caller's rows at all. Queries are 10 single-gold and 4 multi-fact per tenant (14 per tenant: 168 at 12 tenants, 420 at 30), while the store holds 10 fact rows per tenant. Each sweep truncates the store to n tenants and scores the same embedder output (all-minilm, 384 dimensions).

At k=5, mixed query set (single-gold plus multi-fact), post-filter versus scoped:

| tenants | queries | post-filter rows (mean) | queries short of k=5 | foreign rows in raw top-5 | scoped rows (mean) |
|---|---|---|---|---|---|
| 2 | 28 | 3.93 | 96.4% | 1.07 | 5.0 |
| 5 | 70 | 1.84 | 100% | 3.16 | 5.0 |
| 12 | 168 | 1.80 | 98.2% | 3.20 | 5.0 |
| 30 | 420 | 1.84 | 97.4% | 3.16 | 5.0 |

Two things in that table matter more than the exact digits. The under-fill is not a small-store problem: it is already near its floor at five tenants and stays there at thirty, because what drives it is how many foreign rows sit above the caller's rows in a global ranking, not how many documents exist. And the leak surface saturates at roughly a dozen tenants - by then the raw top-5 is about two-thirds other tenants' rows, so the marginal risk of adding tenants is small compared with the risk of having any shared collection at all.

Raising k does not fix it. At 12 tenants on the same query set, post-filtering returned 1.55 of 3 rows at k=3, 1.80 of 5 at k=5, and 2.23 of 10 at k=10, with 100% of queries short at k=10 and 7.77 of the 10 unfiltered rows belonging to other tenants. A larger k costs latency and prompt budget and returns a fraction of what was asked for.

Three means in this family circulate and they are not interchangeable. 1.80 of 5 is the 12-tenant store over the 168-query mixed set. 1.57 is the same store and same k restricted to the 120 single-gold queries. 1.38 is those same 120 single-gold queries scored against the full 300-document, 30-tenant store, where more foreign rows compete for the five slots. The last is the reader-facing probe's selftest population, not the sweep result. An independent exact-cosine rescoring from the committed vectors reproduced the file's per-query counts on 120 of 120 single-gold rows at 12 tenants and k=5, and reproduced all three means.

## Why the model never sees the missing row

Under-fill has no failure signal. The call returns a list, the list is shorter than requested, and every downstream consumer treats "three memories" as the context that exists. An agent asked to assemble five relevant memories from a store holding the fact answers that it does not have it, and the stored fact never appears in the trace. The retrieval layer reports success because it was never asked whether the result was complete.

The recall cost is real on the population where it can be measured, but it is not a general gold loss. On single-gold queries at 12 tenants and k=5 (120 queries), the gold row survived in context 100% of the time under both post-filtering and scoped retrieval - no measured gold loss, because the single gold row did rank inside the global top-5 even when the returned set averaged 1.57 rows. On multi-fact queries (48 at 12 tenants) the gap opens to 87.5% versus 100%, a loss of one query in eight, because two gold rows now compete for the few slots that survive the filter. That is worth fixing, but it is not a collapse, and a page that described post-filtering as making retrieval fail outright would be overstating what the fixture shows.

The leak side is the sharper problem. The `leak` strategy - the raw top-k, no filter - has the same gold-in-context rates (100% on single-gold queries, 87.5% on multi-fact queries, 96.4% over the mixed 168-query set) because filtering never helped the gold row's rank; what changes is that up to 3.20 of those 5 rows are another tenant's facts, with the caller's tenant slug and values in the same prompt window. In the reader-facing probe's selftest over the 300-document store, the raw top-5 averaged 3.62 foreign rows, 72.3% of the returned set.

## Where the filter has to sit

The filter belongs before ranking, in one of two forms: restrict the candidate set to the caller and rank inside it, or pass the tenant predicate into the store's query so the engine restricts what it ranks. Both make the caller's own rows eligible for every slot. A list comprehension after top-k does neither.

Database documentation describes the same arithmetic at the engine level, and it is worth reading carefully because the mechanism differs from application code. pgvector's README states that with approximate indexes filtering is applied *after* the index is scanned, and gives the consequence: if a condition matches 10% of rows, with HNSW and the default `hnsw.ef_search` of 40, only about 4 rows will match on average. The same README documents iterative index scans, which scan more of the index when needed, and the CHANGELOG lists "Added support for iterative index scans" under 0.8.0 (2024-10-30). Read at those pinned pages, that is a database filtering after its own ANN scan - the same shape of failure as filtering after top-k, not evidence about how any other engine behaves, and not applicable to exact sequential scans.

The two other patterns in this article are documented as query-time filters rather than measured fill behaviour. Chroma's metadata filtering page describes `where` in `get` and `query` as filtering records by their metadata, with a query for `page = 10` touching only records whose `page` field is 10. Qdrant's multitenancy guide describes keeping tenants in one collection by adding a tenant payload field with a keyword payload index and `is_tenant: true`, then filtering by that field so each tenant only sees its own data. Both establish where the filter travels; neither page states what happens to the number of results when the filter is selective, and this article claims no fill or performance behaviour for either product.

## Five minutes: run the probe on your store

The downloadable `isolation_probe.py` takes a three-method adapter - `search(query, k)` returning rows with a `tenant` field, `search_scoped(query, tenant, k)`, and an optional `write(tenant, text)` for canaries - and prints PASS/FAIL per assertion. It needs no labelled data: under-fill is measured by asking for k rows and counting what comes back, and the leak surface is measured by planting two canary facts per tenant and counting foreign rows in a raw top-k.

The assertions are deliberately split between the store and the application:

- A1 fill: `len(search(q, k)) == k` for every query and k.
- A1b post-filter fill: `len([r for r in search(q, k) if r.tenant == caller]) == k` - this is the one that fails when the application filters after top-k even though the store is correct.
- A2 scope: every row of `search_scoped(q, tenant, k)` has that tenant.
- A3 agreement: the post-filtered ids are a subset of the scoped ids for the same query.
- A4 no gold loss: when gold ids are supplied, they survive in the scoped results.

Exercised against the committed reference adapter over the full 300-document fixture and 120 single-gold queries at 12 tenants, A1, A2, A3 and A4 passed on all 120 queries while A1b failed on 119 of 120 at k=5. That is the point of the split: an integration test that asserts store-level fill stays green while the assembled context is short by four rows on almost every request.

## The assertions that keep it fixed

The probe is a one-off check; the regression guard is the assertion, in CI, on the assembled context rather than on the store:

```python
rows = retrieve_context(query, tenant, k=5)
assert len(rows) == 5, f"under-filled: {len(rows)} of 5"
assert {r["tenant_id"] for r in rows} == {tenant}, "foreign row in context"
assert {r["id"] for r in rows} == {r["id"] for r in store.search_scoped(query, tenant, 5)}
```

Each line catches a different regression. The length assertion fails the moment the filter moves after the ranking, or when the store's own ANN scan under-returns on a selective predicate. The set assertion fails when a call site loses the filter entirely. The equality assertion fails when scoped and post-filtered retrieval disagree, which is exactly the state a partial refactor produces - and it also catches a scoped call that silently ignores the tenant argument. Run them on a fixture with at least a dozen tenants and several facts per tenant; with two tenants the under-fill is mild enough (3.93 of 5 here) that a regression can pass unnoticed.

## What this does not show

The fixture is synthetic, with equal per-tenant document counts and one shared row template. Real stores have unequal per-tenant counts, near-duplicate rows across tenants and mixed languages, all of which move both the fill distribution and the foreign share. One embedder was used (all-minilm, 384 dimensions); a model that separates tenants more sharply shrinks the leak surface and raises the returned count, while the ceiling - at most k rows survive a post-filter of a top-k - is model-independent. Scoring was exact cosine over the full set with no ANN index, so the index's own under-return is not included here and the two effects are not simply additive. There was no generation step, so this page can speak to what reaches the context window and not to answer quality; no answer-accuracy or task-success improvement is claimed.

No claim is made about how common cross-tenant leakage is, or that any named product does this by default. The measured claim concerns the application-level pattern implemented in the harness: query globally, filter afterwards. Vendor statements are limited to the four pages opened for this article, each scoped to what that page says. The demand behind this page is an editorial experiment, not search-data evidence - no search volume, keyword difficulty, traffic or ranking improvement is claimed.

Everything needed to reproduce the numbers is published as first-party material under `research/evidence/agent-memory-scoped-retrieval-probe-2026/` in the site repository: the fixture, the committed embeddings, the harness, the reader probe, the per-query results, the per-configuration summary, the independent rescoring output, the environment record and the method. The fetched pgvector and Chroma pages and the extracted Qdrant page text were kept locally for verification and are not republished; the links above point at the originals.

## Sources and downloads

Primary pages read for this article (HTTP 200 on 2026-11-14, excerpts saved):

- pgvector README, sections on filtering and iterative index scans: [https://raw.githubusercontent.com/pgvector/pgvector/master/README.md](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md)
- pgvector CHANGELOG, 0.8.0 release section: [https://raw.githubusercontent.com/pgvector/pgvector/master/CHANGELOG.md](https://raw.githubusercontent.com/pgvector/pgvector/master/CHANGELOG.md)
- Chroma documentation, metadata filtering: [https://docs.trychroma.com/docs/querying-collections/metadata-filtering.md](https://docs.trychroma.com/docs/querying-collections/metadata-filtering.md)
- Qdrant documentation, multitenancy - partition by payload: [https://qdrant.tech/documentation/guides/multiple-partitions/](https://qdrant.tech/documentation/guides/multiple-partitions/)

First-party files (synthetic data, no credentials, no customer data):

- Probe: [isolation_probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/isolation_probe.py)
- Harness: [harness.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/harness.py)
- Fixture: [fixture.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/fixture.jsonl)
- Committed vectors (6.1 MB): [vectors.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/vectors.json)
- Per-query results: [results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/results.jsonl)
- Per-configuration aggregates: [summary.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/summary.json)
- Independent rescoring: [recheck.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/recheck.json)
- Probe selftest output: [probe_selftest.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/probe_selftest.txt)
- Environment record: [env.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/env.json)
- Method and commands: [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-scoped-retrieval-probe-2026/method.md)

Related pages on this site: the delete-path companion is [Delete Returns 200](https://baeseokjae.github.io/posts/agent-memory-delete-semantics-test-2026/), which shows that scope enforcement in `delete()` is the caller's responsibility in the same way; [the write-path reliability review](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/) treats scope as an input argument to every protocol method, which is the assumption this probe tests; [the agent-memory scoping guide](https://baeseokjae.github.io/posts/mem0-agent-memory-guide-2026/) covers user, session and agent scope choice rather than filter placement; [the embedding-swap recall test](https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/) is the other silent retrieval failure, caused by a changed encoder instead of a filter position; and [the architecture guide](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) covers where the store sits in the stack.
