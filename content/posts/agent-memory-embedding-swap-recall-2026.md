---
title: "Swap the Embedding Model, Keep the Store: Agent Memory That Returns the Wrong Neighbour Without an Error"
date: 2026-11-02T15:40:00+00:00
lastmod: 2026-11-02T15:58:22+00:00
description: "A 40-document recall harness shows what happens when the encoder behind an existing vector store changes: same-width swaps return wrong neighbours with no exception, while width mismatches fail loudly. Includes the guard that records encoder id, digest and dimension per vector."
draft: false
tags:
  - embedding model swap agent memory
  - vector store recall regression
  - same dimension different embedding space
  - ollama embedding models
  - recall at k harness
  - embedding migration checklist
  - vector space guard
  - pgvector dimension mismatch
  - silent retrieval failure
  - agent memory retrieval integrity
schema: "schema-agent-memory-embedding-swap-recall-2026"
---

An agent memory store can survive an embedding-model change while quietly returning the wrong fact. Nothing in the stack raises, because nothing in the stack compares the encoder that wrote a vector with the encoder that now reads it. In a 40-document fixture with 15 single-answer queries, one encoder on both sides ranked the labelled document first for 15 of 15 queries. Replacing the document encoder with a different model of the same width dropped that to 1 of 15, and no call failed. Replacing it with a model of a different width failed all 15 queries with a length error — the loud case, and the easy one.

That contrast is the whole point. The dimension check most teams already have catches one of these two failures. The other one changes what your agent believes.

## The failure: neighbours come back, the space does not

The scenario is ordinary maintenance. A team moves memory embeddings from a hosted model to a local one, upgrades a model version, or switches providers during an outage. The write path keeps running, the table keeps its shape, and `search(query, k=5)` keeps returning five rows. If the new encoder has the same output width as the old one, even a strict database column will accept the new vectors: a `vector(384)` column takes 384 floats from any model on earth.

What changed is not the schema. It is the coordinate system. Cosine similarity only means something when both vectors were produced by the same function; compare two different functions and the ranking is noise with a plausible-looking shape. The agent does not report "no match" — it reports the nearest row in a meaningless space, phrased fluently. That is worse than an outage, because an outage is visible.

This is a different failure from the one where long inputs are clipped before they become vectors. [That truncation problem is measured here](https://baeseokjae.github.io/posts/local-embedding-context-ceiling-2026/). The swap problem happens after a correct write: the vector is complete, the row is intact, and only its provenance is wrong.

## What actually changes when the encoder changes

Three properties decide whether two encoders share a space, and a dimension check tests only the third.

The training objective and data decide the geometry. [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) is documented as mapping sentences to a 384-dimensional dense space for semantic search; a different 384-dimensional model is trained on a different objective and arranges the same words differently.

The input convention decides the point, even for one model. [nomic-embed-text-v1.5's card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) requires a task instruction prefix — `search_document: ` for stored text and `search_query: ` for queries — and says the prefix is mandatory. Feeding that model unprefixed text produces a vector that is valid, 768-dimensional, and not the vector the model was trained to produce for retrieval.

The width decides only whether the error is loud. Ollama's [embed API reference](https://github.com/ollama/ollama/blob/main/docs/api.md) documents a `dimensions` parameter that sets the number of dimensions for the embedding, so width is not necessarily fixed per model: a client can request a shorter vector from the same weights, and a store keyed only on `(model, width)` would accept that output as if it belonged to the full-width space.

Input length is a separate lever in the same API and does not touch width. The reference's `truncate` option defaults to `true` and clips the end of each *input* to fit the model's context length — the vector still comes out at full width. That is the write-time information loss measured in [the embedding input-length article](https://baeseokjae.github.io/posts/local-embedding-context-ceiling-2026/), and it can occur with no model change at all. Keep the two apart: clipping changes what the model saw, a swap changes which function produced the vector.

## The harness: 40 documents, 15 queries, three encoders

The measurement is deliberately small so it can be re-run on a laptop. The fixture is 40 synthetic agent-memory statements — deployment windows, retention periods, ports, contact preferences, identifiers — and 15 questions, each with exactly one defensible gold document. No real user data is involved. The baseline result is also the fixture's label check: if a competent encoder cannot put the gold document first for every query, the labels are ambiguous and the fixture is not usable.

Documents and queries are embedded through the local Ollama endpoint, stored as plain Python lists, and scored by brute-force cosine over every query-document pair. There is no ANN index, so no approximation error can be confused with the effect being measured. Encoders are pinned by digest rather than tag, because `:latest` can be repointed: nomic-embed-text `0a109f422b47` at 768 dimensions, all-minilm `1b226e2802db` at 384, and snowflake-arctic-embed:33m `e8db018629b4` at 384, read from the host's tag list on 2026-11-02 with Ollama 0.20.3. nomic was called with the prefixes its card requires; the two 384-dimension models were called without any task prefix, so the swap rows do not separate a prefix effect from a space effect.

Five configurations were scored: a matched baseline, both directions of a same-width cross-model swap, a half-migrated store, and a cross-width query. Each produced one record per query plus an aggregate.

## The result matrix

| Configuration | Document encoder | Query encoder | Width | recall@1 | recall@5 |
|---|---|---|---|---|---|
| Baseline | nomic-embed-text | nomic-embed-text | 768/768 | 15/15 | 15/15 |
| Same-width swap A | all-minilm | snowflake-arctic-embed:33m | 384/384 | 1/15 | 2/15 |
| Same-width swap B | snowflake-arctic-embed:33m | all-minilm | 384/384 | 1/15 | 3/15 |
| Half-migrated store | nomic + all-minilm (20/20) | nomic-embed-text | 768+384 / 768 | 7/15 | 7/15 |
| Cross-width | nomic-embed-text | all-minilm | 768/384 | — | — |

The two same-width rows are the alarming ones. Recall at rank one fell from 15 of 15 to 1 of 15 in both directions, and the best of the two still missed 12 of 15 gold documents inside the top five. No embedding call raised, every vector came back at the recorded width, and this harness kept its vectors in a plain Python list, so no column type was consulted at all — but the 384-dimension vectors would have satisfied a `vector(384)` column just as readily, because their width was correct; no width constraint anywhere in this stack would have rejected them. If the only monitoring you have is "the query returned k rows", this failure is invisible.

The mixed store is the migration-in-progress case. Twenty documents were embedded by all-minilm and twenty by nomic, alternating; queries used nomic, so half the table belonged to the query's space and half did not. Recall@1 came out at 7 of 15 — better than the full swap, because the matching half was reachable, and still less than half of the baseline. The harness skipped 300 query-document comparisons (20 mismatched documents across 15 queries) rather than pretending to score them. In a real store the same state is worse than a ranking problem: part of the table cannot be served at all, and nothing in the application knows which part.

## The loud failure is the safe one

Querying the 768-dimension store with the 384-dimension encoder raised `ValueError: vector length mismatch: 384 vs 768` for all 15 queries. That is the outcome to want. A width mismatch stops the request at the first comparison, which is why a schema like [pgvector's `vector(n)` column](https://github.com/pgvector/pgvector) is worth having: it fixes the width at write time, so a differently sized vector is rejected on insert instead of discovered on query.

Two caveats keep this from being a complete defence. First, the exception text above belongs to this harness's pure-Python cosine; the failure is client-dependent. A client that pads, slices or truncates to the stored width — or a provider that honours a `dimensions` parameter — will return ranked neighbours with no error at all. Second, the width is the only property a database column checks. Same-width models pass every constraint in the stack, which is exactly the configuration that measured 1 of 15.

One hypothesis was tested and dropped rather than published as a maybe: whether Ollama's native `/api/embed` and its OpenAI-compatible `/v1/embeddings` return different spaces for the same input. For one model and one input string, the vectors were identical to six decimal places (cosine 1.0, 384 dimensions on both paths). There is no endpoint-divergence warning to give here.

## The guard: one identifier per vector, checked before scoring

The fix is not a better model. It is provenance: every vector records which encoder produced it, and every query refuses to run against a store written by a different one. A model tag alone is insufficient, because tags move; a digest alone is insufficient, because width can change under one model through `dimensions`. Concatenate them.

```sql
CREATE TABLE memory_vectors (
  doc_id      TEXT NOT NULL,
  encoder_id  TEXT NOT NULL,          -- e.g. nomic-embed-text:latest@0a109f42:768
  dim         INTEGER NOT NULL,
  content_sha TEXT NOT NULL,
  vector      BLOB NOT NULL,          -- packed float32
  PRIMARY KEY (doc_id, encoder_id)
);
```

The `content_sha` column answers a second question the recall harness cannot: whether the stored vector still corresponds to the text it is supposed to represent. If the document changed and the vector did not, the row is stale even though its encoder id matches.

The read path then becomes a refusal rather than a hope:

```python
def require_same_space(store_encoder_id, store_dim, query_encoder_id, query_dim):
    problems = []
    if query_encoder_id != store_encoder_id:
        problems.append(f"encoder mismatch: store={store_encoder_id} query={query_encoder_id}")
    if query_dim != store_dim:
        problems.append(f"dimension mismatch: store={store_dim} query={query_dim}")
    if problems:
        raise RuntimeError("refusing cross-space search: " + "; ".join(problems))
```

During a migration, "refuse" would take the feature down, so the guard also needs a read-only mode that reports exposure instead of blocking: count rows by `encoder_id`, return the fraction the target encoder can actually serve, and fail the migration gate until that fraction is 1.0 with exactly one encoder id present.

```python
def reindex_state(rows, target_dim):
    total = len(rows)
    live = sum(1 for r in rows if r["dim"] == target_dim)
    return {"total": total, "servable": live,
            "silently_unreachable": total - live,
            "ready": total == live and len({r["encoder_id"] for r in rows}) == 1}
```

That function is the difference between the mixed-store row and a migration you can reason about. It converts "we re-embedded most of the table" into a number.

## Migration checklist

1. Build a shadow index under a new `encoder_id`. Write both encoders' vectors for new documents ("dual write") so the old path keeps serving while the new one fills.
2. Run a labelled recall check against both indexes before cutover, on the same queries. Compare recall@5, not just "does search return rows". A drop from 15/15 to 1/15 is what a cross-space query looks like when nobody is looking for it.
3. Backfill by `content_sha`, not by `updated_at`: a row whose text did not change still needs a new vector, and a row whose text changed twice needs one vector, not three.
4. Cut over by changing the stored `encoder_id` the reader expects — the guard will refuse mixed states — then delete the old rows only after the new index serves the full table.
5. Keep the labelled query set. It is the only regression test that fails when a future model swap reintroduces the silent case: the width check in this harness raised on every cross-width pair — the whole of the last configuration and the mismatched half of the mixed store — while every same-width comparison returned a full ranking.

For stores that expose a fixed vector width, an insert at the wrong width fails at the column. That covers only part of step 3: a same-width vector from another model is accepted by every schema constraint, so the rest is enforced only by the `encoder_id` check, which is why the check belongs in the read path and not in a deployment checklist.

## Reproduce it in a few minutes

The measured run used the 40-document fixture described above; the scoring loop is small enough to paste, and swapping in your own documents and queries is the intended use. The core is a brute-force cosine over two lists of vectors:

```python
from math import sqrt

def cosine(a, b):
    if len(a) != len(b):
        raise ValueError(f"vector length mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = sqrt(sum(x * x for x in a)), sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

def recall_at_k(docs, queries, k):
    hits = 0
    for q in queries:
        ranked = sorted(docs, key=lambda d: cosine(q["vector"], d["vector"]), reverse=True)
        hits += q["gold"] in [d["id"] for d in ranked[:k]]
    return hits / len(queries)
```

Embed `docs` and `queries` with the same model first, confirm recall@1 is at or near 1.0, and only then re-embed the documents with the candidate model and re-run against the original query vectors. The difference between those two numbers is the cost of the swap on your corpus.

The evidence behind the numbers in this article — fixture, harness, per-configuration JSONL and the digest ledger — is a private author-side working record kept with the run; it is not offered as a download from this page. What is reproducible without it is the procedure above and the two guard functions, which are complete as written.

## Limitations

The fixture has 40 documents and 15 single-answer queries, and the baseline is saturated at 15 of 15. The measured collapse therefore shows that cross-space ranking is near-random on this fixture; it does not estimate the size of the drop on a larger, harder corpus, where a matched encoder would also miss some queries. All numbers come from a single run on one 2-vCPU host with Ollama 0.20.3, two 384-dimension open models and one 768-dimension model. No proprietary embedder, reranker, hybrid BM25 leg or ANN index was involved, so nothing here measures approximation error, latency or the cost of re-embedding a production table.

The mixed-store result depends on a lenient client: this harness skips width-mismatched pairs, while pgvector would reject them at the column type and an application-level store might accept them silently. The 768-vs-384 exception text is Python-specific for the same reason. The 384-dimension pair was embedded without task prefixes, so part of that drop may belong to input convention rather than to a different vector space; the two causes are not separated here, which is another reason to treat the number as a demonstration of the failure mode rather than a measurement of any model. And no search-demand data supports the topic: the memory cluster has measured impressions, but no embedding-migration query appears in the samples behind this page, so treat it as an unmeasured failure mode rather than a searched-for one.

If you are still choosing a store rather than migrating one, [the store comparison](https://baeseokjae.github.io/posts/mem0-vs-zep-production-guide-2026/) and [the Zep review](https://baeseokjae.github.io/posts/zep-ai-agent-memory-review-2026/) cover that decision. If you are designing the write path this guard sits on, [the write-path reliability protocol](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/) is the companion piece, and [the architecture guide](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) puts the vector layer in context.
