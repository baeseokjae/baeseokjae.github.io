---
title: "Elasticsearch as Agent Memory: three indices, hybrid RRF retrieval, and the 0.89 recall number Elastic published"
date: 2026-11-19T00:00:00+00:00
lastmod: 2026-11-19T00:00:00+00:00
description: "Map agent memory onto Elasticsearch with episodic, semantic and procedural indices, BM25 plus dense retrieval fused by RRF at rank_constant 30, supersession, and per-user document-level security, with the vendor-reported 0.89 recall@10 in its real scope."
tags:
  - agent memory
  - elasticsearch
  - hybrid retrieval
  - RRF
  - reranker
  - multi-tenant
  - retrieval evaluation
draft: false
schema: schema-persistent-agent-memory-on-elasticsearch-building-0-89-recall
cover:
  image: "/images/persistent-agent-memory-on-elasticsearch-building-0-89-recall.png"
  alt: "Elasticsearch as agent memory: three indices, hybrid retrieval, supersession and tenant isolation"
  relative: false
---

You build agent memory on Elasticsearch by splitting it into three indices — episodic events, semantic facts, procedural playbooks — writing each memory once into a BM25 field and a `semantic_text` field, recalling with a hybrid query that fuses 80 keyword and 80 dense candidates through reciprocal rank fusion at `rank_constant=30`, reranking the merged pool with a cross-encoder, hiding contradicted documents behind a `superseded_by` filter, and isolating tenants with a query-level security rule. That is the shape of the reference implementation Elastic Search Labs published on 2026-06-16, described in [Agent memory on Elasticsearch: hybrid retrieval and DLS](https://www.elastic.co/search-labs/blog/agent-memory-elasticsearch).

The number usually attached to that design — recall@10 of 0.89 — is the vendor's own eval result over 168 questions. It is not a measurement by this site, and nothing below claims to have reproduced it. The rest of this page is the layout, the query mechanics, the failure modes and the evaluation protocol you need to produce your own number on your own corpus.

## What the 0.89 actually measures, and what it does not

The vendor post reports R@10 averaging 0.89 over 168 QA-style questions, with zero cross-tenant leaks, and states that the reranker has serving-side variance: across four back-to-back runs R@10 landed at 0.85, 0.88, 0.89 and 0.893. Per type, semantic facts are the harder case at about 0.81, episodic averages 0.98 and procedural reaches 1.0. The evaluation is gated in CI at R@10 ≥ 0.85, R@5 ≥ 0.75 and leaks = 0, so a regression fails the build rather than being noticed later. Read the attribution precisely: **Elastic Search Labs reports** those figures for its own eval set; the spread across runs is 0.043.

| Reported figure | Value | Scope |
|---|---|---|
| R@10, overall | 0.89 averaged; 0.85 / 0.88 / 0.89 / 0.893 across four runs | Vendor QA-style eval, 168 questions |
| R@5, overall | ≥ 0.75 gate | Same eval; no per-run R@5 published in the post body |
| R@10, semantic | ≈ 0.81 | Same eval, semantic-fact subset |
| R@10, episodic | 0.98 | Same eval, episodic subset |
| R@10, procedural | 1.0 | Same eval, procedural subset |
| Cross-tenant leaks | 0 | Same eval |

What that number is not: it is not a benchmark of Elasticsearch against Qdrant, Weaviate or pgvector, and it is not measured on your documents. The post is explicit about how the eval is built — QA-style passage retrieval, in which an LLM writes two questions a user might plausibly ask whose answer is that doc, and the retriever then has to surface the source doc in the top-k — and it links [the full implementation](https://github.com/noamschwartz/atlas-memory-demo). The boundary is narrower than "no fixture exists" and wider than "you can re-run 0.89": the question set is LLM-generated and cached on disk (`qa_questions_cache.json`) so re-runs are deterministic against a fixed question set, which makes the protocol reproducible while leaving 0.89 tied to that generated set and the persona corpus behind it, not to a static fixture handed to readers. Treat 0.89 as evidence that a hybrid-plus-rerank pipeline on this engine reached high recall on one generated question set, and as a reason to build your own eval before you tune anything.

## Three indices, three lifecycles

The design separates memory by how it ages, not by topic. Each type gets its own index because each has a different write rate, a different staleness rule and a different update path; collapsing them into one index with a `type` field makes every decay and isolation filter branch on a value the engine cannot use for routing.

| Memory type | What it stores | Date field used for decay | Update rule |
|---|---|---|---|
| Episodic | Timestamped events from a session | `timestamp` (event time) | Written constantly, decays with age |
| Semantic | Distilled stable facts about a user | `last_used_at` (set at write, bumped on recall) | Curated, deduped, superseded on contradiction |
| Procedural | Multi-step playbooks with `success_count` / `failure_count` | none — exempt from decay | Counters updated when a fix is confirmed or rejected |

Alongside the three memory indices sits a fourth retrieval surface: the world data already in the cluster (product catalog, reference content). It is not memory, but it has to be recallable in the same query, which is why the isolation rule later has to admit documents that carry no `user_id` at all.

## One write, two retrieval legs

Each document is indexed twice from a single write. The raw text lands in the BM25 inverted index, and `copy_to` routes the same value into a `semantic_text` field that generates dense vectors through an inference endpoint. That keeps one source of truth while giving the query two independent signals:

- **BM25** anchors literal tokens that paraphrase destroys — version numbers, error codes, product names, exact identifiers.
- **Dense retrieval** catches the same intent expressed in different words, which is most of what an agent sees in conversation.

Both legs over-fetch 80 candidates. The two result sets are fused with reciprocal rank fusion, which combines rankings rather than scores, so the two legs never need their scores calibrated against each other. The reference implementation sets `rank_constant=30`, tighter than the documented default of 60; a lower constant increases the influence of the top-ranked documents from each leg. The [reciprocal rank fusion reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) documents `rank_constant` as an optional integer that must be at least 1 and defaults to 60, and requires two or more child retrievers.

A Jina v2 cross-encoder then scores the merged candidates directly against the query. That second stage is where the cost lands: it runs only on the fused pool, not on the corpus, which is why the pipeline stays affordable at conversation latency. It is also the source of the run-to-run variance the vendor reports, because a hosted reranker is not bit-for-bit deterministic across calls.

## Recency and reuse: gauss decay plus a use-count boost

Two multipliers adjust each result's score before the final ranking. The first is time decay: a gauss-shaped multiplier computed per index, with `offset=180d` (a flat zone where recent memories are not penalised), `scale=1825d` and `decay=0.5`. The second is a frequency refinement for semantic memory only: `1 + log10(1 + use_count) * 0.2`, roughly a 1.2× boost after ten recalls and 1.4× after a hundred.

The engineering detail worth copying is where the decay lives. Elasticsearch's native `gauss` decay takes one field name that must exist on every index in the search, and episodic decays on `timestamp` while semantic decays on `last_used_at`. The reference implementation therefore computes the same gauss shape in a Painless script that branches on `_index`, keeping the two date fields in one query. The [function score query reference](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query) documents the decay functions (`gauss`, `linear`, `exp`) and the `function_score` composition; a single `function_score` with `score_mode` and `boost_mode` both set to `multiply` is what the post shows for the combined factors.

Procedural memory is deliberately exempt: a playbook that worked two years ago is not stale, and its counters carry the signal instead. Semantic memory gets one more tilt — a catalog source prior of 0.85 so user memory wins near-ties against shared catalog text, without preventing the catalog from winning when it is clearly the better match.

What the post does not publish is an ablation: no run separates how much of the recall came from decay, from the use-count boost, or from the source prior. Keep the constants as a defensible starting point and change them only when your own eval set can show the change helps — the vendor itself says the scale should be tightened for fast-churn domains and loosened for personal-assistant memory where facts stay relevant for years.

## Contradictions: supersede, do not delete

Append-only memory rots, and overwriting destroys the audit trail. The reference protocol stamps the old document with `superseded_by` and `superseded_at` and writes the replacement with a confidence level that depends on which contradiction mode was passed: a `natural` update (moved house, upgraded plan, changed preference) is written at full confidence, while a `harsh` contradiction — the customer explicitly denying or correcting the prior fact — carries a small confidence penalty on the new assertion. Every recall then applies `must_not exists superseded_by`, so the contradicted document stops surfacing while the chain of how a belief changed stays queryable for debugging.

The post does not say what happens when two writers supersede the same document concurrently; the only pattern it shows is one writer calling `write_memory` with a `supersedes_id`, so concurrent supersession is the decision left to you. Where superseded documents live, it does specify. They accumulate in the index and stay invisible to recall behind the `must_not exists superseded_by` filter unless a query explicitly asks for them with `include_superseded=True`; in production a periodic reindex moves them into a separate archive index that Elasticsearch's Index Lifecycle Management ages through cold and frozen tiers using searchable snapshots, so the audit chain stays queryable on cold storage while the active semantic index stays hot and small. Explicit deletion is a separate path: `forget_memory` is reserved for a user asking to forget something, and supersession is not deletion — the old document stays in the index with its link to the replacement. What an explicit forget actually removes in this engine is a different measurement, and this page does not make it.

## Same-turn visibility is a storage decision

An agent that writes a memory and recalls it in the same turn hits the refresh gap: Elasticsearch's default asynchronous refresh, plus the inference cost of generating the embedding, can leave the just-written document invisible to the next query. The reference implementation passes `refresh=True` on every `write_memory` call, forcing the shard to refresh before the call returns.

That is the simple correct choice at low write volume and the wrong one at high write volume — the post says so explicitly and suggests shifting to asynchronous indexing plus an agent-layer "just-written" register that holds recent writes in the model's context until the index catches up. Pick per workload: single-conversation agents can afford the refresh, high-throughput ingestion cannot.

## Isolation: what the cluster guarantees, and what your code guarantees

The reference design puts the isolation rule in the cluster with document-level security. Each user gets an API key whose role descriptor carries a DLS query admitting documents whose `user_id` equals that user, plus documents that have no `user_id` field at all (the shared catalog). An agent using that key can run any query it likes and the cluster will not return another user's memories. The retriever also applies a `user_id` filter in code, explicitly as a second layer against configuration drift — a new index template without the DLS clause, a role edited and the clause dropped, an admin key reused by mistake. DLS is the architecture; the code filter is the cheap paranoia pass.

One boundary this page will not cross: which subscription tier includes document-level security was not confirmed during this check, and the reference post does not state it. Elasticsearch's subscription documentation is where that has to be settled for your deployment. Until you have confirmed it, the honest reading is that cluster-enforced isolation is available on tiers that include document-level security — not that a basic self-managed node enforces it. If your tier does not, the application-level filter is not a defence-in-depth extra; it is your only boundary, and it belongs in the repository's query builder rather than in each caller.

## Producing your own recall number

The vendor number is not portable, so the useful deliverable is the protocol. Five things make a recall measurement reusable:

1. **A pinned corpus snapshot.** Record the exact document set — commit hash or a content-addressed manifest — so the same questions always run against the same passages.
2. **One gold passage per question.** Recall is only meaningful if there is exactly one correct target per question, chosen before you see what the retriever returns.
3. **Recall@5 and recall@10 per memory type.** Aggregate numbers hide the pattern the vendor found: semantic facts are the weak slice while episodic and procedural are near-ceiling. Per-type reporting tells you where to tune.
4. **Three repeat runs and the spread.** A hosted reranker varies between calls; a single run is not a measurement. Report the range, not just the mean.
5. **A gate that fails loudly.** Copy the vendor's shape: floors on R@10 and R@5 plus an assertion that cross-tenant leaks equal zero, run in CI on every change to mappings, analyzers or retrieval parameters.

The public reference for all five is [the vendor's own harness](https://github.com/noamschwartz/atlas-memory-demo/blob/main/backend/scripts/atlas/eval_recall.py): it samples memory docs per persona across the three indices, generates two questions per doc, caches them in `qa_questions_cache.json` so re-runs are deterministic against a fixed question set, reports Recall@1 / Recall@5 / Recall@10 plus MRR capped at k=10, and runs a tenant-isolation sweep that takes one QA pair per owner and memory type, replays that pair's first question as each other user, and treats any hit as a leak — one cross-user query per sampled pair, not a full replay of the question set. Read it as the shape to copy rather than as proof that 0.89 reproduces: it ships the method, but its question set is LLM-generated and the persona corpus is its own. This article still ships no corpus, question set or score file — the source check described at the end is a private author record, not a downloadable dataset. Build the five pieces on your documents and you get a number with provenance, which is the only kind worth quoting.

## What to build first

Start smaller than the reference design. One tenant, one semantic index, BM25 plus dense retrieval with RRF, and a fifteen-question eval set is enough to prove the plumbing and to establish your baseline. Add the second and third indices when you can name the lifecycle difference they encode. Add decay, the use-count boost and the source prior only when the eval set exists to show each one helps — otherwise you are tuning constants you cannot defend.

Instrument three things from day one: which index answered each recall, whether the gold passage appeared in the reranked top five, and whether any recall returned a document belonging to another `user_id`. Those three signals turn an incident ("the agent forgot") into a diagnosis ("semantic recall dropped because the supersession filter now hides two of the three candidate facts").

Expect three failure modes in this order: semantic recall lagging episodic badly, because sibling facts collide; same-turn misses when a write is not refreshed before the recall; and isolation that fails open when a role descriptor is edited without the DLS clause. The first needs better extraction or a reranker, the second needs a refresh policy, and the third needs a test that asserts the leak count is zero rather than a reviewer's confidence.

## Sources and verification

Every external fact above was read from the linked page during this check. The source reads are timezone-aware UTC and are listed with the round that made them, because two of them were re-read after the first draft: the vendor architecture post at 2026-11-19T09:42:37Z (earlier reads at 2026-11-02T07:28:56Z and 07:37:01Z), the reciprocal rank fusion reference at 2026-11-02T07:28:59Z, and the function score reference at 2026-11-02T07:29:02Z. The vendor's eval harness was re-read as raw source at 2026-11-19T09:42:37Z; its docstring and its sweep function are the basis for the Recall@1/5/10, MRR and isolation-sweep description above. What was not done: no Elasticsearch cluster was started for this page, no recall run was performed, the harness was not executed, and the DLS subscription tier was not confirmed. The 0.89 figure therefore carries vendor attribution throughout, and the pipeline constants are described as the reference implementation's choices rather than as tuned results. Model names (Jina v5 embeddings via `semantic_text`, Jina v2 cross-encoder) are as stated in the vendor post and were not re-verified against model cards; pin the versions you actually deploy, because embedding and reranker behaviour changes with them.

For the conceptual split behind episodic, semantic and procedural memory, the [agent memory architecture guide](/posts/agent-memory-architecture-guide-2026/) covers the types without the Elasticsearch mechanics. If the question is whether to add a separate vector database instead of using the search engine you already run, the [vector database comparison](/posts/vector-database-comparison-2026/) frames that trade-off. And if you would rather not operate the store yourself, [agent memory on Cloudflare Workers](/posts/agent-memory-cloudflare-workers/) covers a managed substrate with different compaction semantics.
