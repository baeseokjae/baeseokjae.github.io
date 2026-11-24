---
title: "Agent Memory Multi-Hop Recall: One Retrieval Misses Half of a Two-Hop Answer"
date: 2026-11-24T11:22:00+00:00
lastmod: 2026-11-24T11:22:00+00:00
description: "A 120-fact local store and three Ollama embedders: single-hop facts land in the top-5 for 19-20 of 20 questions, but both facts for a two-hop question land for only 3-5 of 20. Top-20 recovers 14 of 20, and one-shot decomposition recovers 4 of 20. Coverage is measured per question; reader accuracy is not claimed."
draft: false
tags:
  - agent memory multi-hop recall
  - two-hop questions local rag
  - bridge fact retrieval
  - ollama embedding models comparison
  - vector store top-k recall
  - local agent memory measurement
  - decomposition vs single-shot retrieval
  - in-process cosine ranking python
  - exact cosine retrieval fixture
  - longmemeval multi-hop
cover:
  image: /images/agent-memory-multi-hop-recall-2026-cover.png
  alt: 'Conceptual two-lane diagram. Lane A is the measured single-shot top-5 shape: the question asks which database holds orders-api; the retrieved set contains the fact that orders-api runs in eu-west but not the bridging fact that eu-west data lives in aurora-eu-1, which ranks below the five-slot cut, so only one of the two facts arrives. Lane B is marked as not measured in this run and shows an iterative split: a first retrieval returns the region for orders-api, that region goes into a second query, and only the second call can reach the database fact, at the cost of another round trip. Conceptual diagram of retrieval shape, not measurement data.'
  caption: 'Retrieval shape for a two-hop question · conceptual diagram, not measurement data'
schema: "schema-agent-memory-multi-hop-recall-2026"
---

Your agent memory store answers single-fact questions well enough to look healthy. Ask which region a service runs in and the right row comes back with a good similarity score. Then someone asks which database holds that service's data — a question the store can only answer by joining two rows — and the agent either returns half of it with no trace of doubt or says it has nothing.

Three different faults produce that same answer, and the stack usually cannot tell them apart: the second fact was never written; it was written but ranked outside the k rows you retrieve; or both rows reached the prompt and the model failed to join them. Each fault has a different fix, and the fix you pick first is usually the wrong one, because nothing in a normal retrieval log reports which of the three happened.

This article measures the middle fault on a small, fully published fixture: 120 short facts forming 40 two-hop chains, 20 two-hop and 20 single-hop questions, three local embedding models served by Ollama, exact cosine ranking with no ANN library, and a 0.5B model as the decomposition rewriter. The short version:

- Single-hop facts stayed in the top-5: 20/20 questions for `all-minilm:latest`, 19/20 for `snowflake-arctic-embed:33m` and 19/20 for `nomic-embed-text:latest`.
- Both facts needed by a two-hop question reached the top-5 for only 3/20, 5/20 and 5/20 questions respectively.
- Raising k to 20 recovered both facts for 14/20 questions on every one of the three encoders, at roughly four times the facts in the prompt.
- The first hop was usually in the top-5 (17-18 of 20 questions) while the second hop's median rank was 11 to 14. The bridge is not missing from the store; it is below a five-slot cut.
- One-shot decomposition — ask a 0.5B model to split the question, then retrieve each part — recovered both facts for 4 of 20, against 3 of 20 for a plain top-5: it restates the question because the intermediate entity is not in the input.
- Reader-side accuracy is not claimed. The reader stage did not complete inside this run's budget: the run ended before `results-reader.json` was written, so no reader row exists for this run and no accuracy, token or per-call latency figure is reported. What is measured and published is coverage, which is deterministic and computed without a reader model.

The fixture, the probe and the per-question rows are published; the raw files are listed at the end.

## What "multi-hop" means here, operationally

MultiHop-RAG defines the problem as queries that "require retrieving and reasoning over multiple pieces of supporting evidence" and reports that existing retrieval-augmented systems answer them unsatisfactorily ([arXiv:2401.15391](https://arxiv.org/abs/2401.15391)). That is an English news knowledge base with 2023-2024 systems, so its numbers are not this article's numbers — it is the definition that matters: the evidence is plural, and the pieces have to be joined.

LongMemEval splits long-term memory into information extraction, multi-session reasoning, temporal reasoning, knowledge updates and abstention, and its abstract reports a roughly 30% accuracy drop for commercial assistants and long-context models on information that must be remembered across sustained interactions ([arXiv:2410.10813](https://arxiv.org/abs/2410.10813)). Multi-session reasoning is the capability area closest to this test. No LongMemEval or LoCoMo score is reused or re-derived here; the fixture is this site's own.

For this fixture the operational definition is narrower and easier to check. A question names one entity and asks for a property that is not stored on that entity. The store contains a chain: entity A → intermediate B, and B → answer. The question never names B. To answer, a retriever must return both rows; a reader must then apply the second to the first. "Which database holds the data for orders-api?" is answerable only if the store returns both "orders-api runs in eu-west" and "eu-west stores primary data in aurora-eu-1". Nothing in the question mentions a region, so a single similarity search over the question text has to be lucky to rank both.

## The fixture: 120 facts, 40 chains, 40 questions

Everything is synthetic and deterministic, so the probe can be rerun and compared line by line.

- 40 invented services (`orders-api`, `billing-worker`, …), 8 regions, 8 owning teams.
- 120 facts of 7 to 12 words (mean 9.2): 40 service→region, 40 service→team, 8 region→database, 8 team→on-call rotation, plus 24 distractors that sit on the same entities (cost centre per region, incident queue per team, language per service) so that "region" or "team" alone does not identify a unique row.
- 20 two-hop questions: 12 ask for a database through a service's region, 8 ask for an on-call rotation through a service's owning team. They are written in three phrasings (templated, natural, keyword-ish) to avoid measuring one prompt template.
- 20 single-hop controls on the same store: 10 "which region does X run in", 10 "which team owns X". A store or reader that fails these is broken in a way that has nothing to do with question shape.

The store is a flat list of 120 vectors held in the probe process, ranked by exact cosine in pure Python (`math` only, no numpy, no ANN index, deterministic full sort). That choice is deliberate: an approximate index would add a second variable to a question about ranking.

## Four arms, and what each isolates

Every arm runs against the same store, the same facts and the same 40 questions.

1. **top-5** — embed the question, take five nearest facts. The default most local setups ship with.
2. **top-20** — same, twenty facts. Tests whether k is the whole problem.
3. **decomposition** — one call to the local reader model asking it to split the question into sub-questions, each sub-question embedded and retrieved separately at k=5, results unioned and deduplicated, capped at 10 facts. This is the fix most write-ups recommend.
4. **oracle** — the two gold facts placed in the prompt, nothing else. This arm was designed to bound what the reader can do when retrieval is perfect. It is not reported here: the reader stage did not complete (see “Why there is no accuracy column”), so no accuracy column appears in this article.

Arms 1 to 3 are retrieval measurements: they need no model beyond the embedder, they are deterministic, and every id is recorded. That is deliberately where this article puts its weight.

## Bridge coverage before accuracy

Accuracy mixes two failures. Coverage isolates one: does the retrieved set contain both facts the answer needs, regardless of what the reader says?

| Encoder (dimensions) | Single-hop fact in top-5 | Both facts in top-5 | Both facts in top-20 |
|---|---|---|---|
| `all-minilm:latest` (384) | 20/20 | 3/20 | 14/20 |
| `snowflake-arctic-embed:33m` (384) | 19/20 | 5/20 | 14/20 |
| `nomic-embed-text:latest` (768) | 19/20 | 5/20 | 14/20 |

Three encoders spanning two widths and three training recipes agree on the shape: single-hop retrieval is close to saturated, two-hop coverage at k=5 is 15-25%, and one deeper cut fixes most of it. This is the first number an operator should produce for their own store, because it decides whether the next hour is spent on retrieval or on prompting.

The 14/20 at k=20 is not a rounding artifact of one encoder: all three land on 14, and the overlap is real but partial — two encoders share 12 of those 14 questions, `snowflake-arctic-embed` and `nomic-embed-text` share 11, and only 11 questions are covered by all three. Six questions stay uncovered on each encoder even at 20 facts, and the six are not the same six, which is a different problem: the second fact is ranked below 20, or, in one case on `all-minilm`, was not returned in the top 50 at all.

## Where the second fact actually sits

The median rank of the second hop was 11 for `all-minilm` and `snowflake-arctic-embed:33m`, and 14 for `nomic-embed-text`. Across the three encoders the second hop's ranks spread from 2 to 45 — 2-41, 2-40 and 3-45 per encoder. In the same questions, the first hop was in the top-5 for 18, 17 and 18 of 20 respectively.

That asymmetry is the mechanism. The question text resembles the first fact closely — the service name is in both — so the first hop ranks high. The second fact never mentions the service; it says which database the *region* uses. Its similarity to the question is carried only by the shared concept "database", which is why it lands in the teens rather than nowhere. If your store never returns the bridge at any depth, the failure is upstream — chunking, write path or encoder — and the [chunk granularity fixture](https://baeseokjae.github.io/posts/agent-memory-chunk-granularity-recall-2026/) and the [embedding swap test](https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/) cover those separately. The [architecture guide](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) puts the same class of weakness in one line about pure vector stores: "Fails for temporal queries and entity relationship tracking." The [Elasticsearch hybrid walkthrough](https://baeseokjae.github.io/posts/persistent-agent-memory-on-elasticsearch-building-0-89-recall/) is the cluster-scale answer: fuse a lexical channel with a dense one so that a row sharing only a keyword can still surface.

## Why there is no accuracy column

The planned reader arms (`qwen2.5:0.5b` at temperature 0, seed 42, an `UNKNOWN` escape and a published normalised-substring grading rule) did not complete inside this run's budget. The probe writes `results-reader.json` after every finished row and again at the end of the reader stage; neither happened here, so no reader row exists for this run and there is nothing to report — not an accuracy, not a prompt-token count, not a per-call time. Rather than publish a subset of cells as if it were the table, the article reports no reader accuracy at all.

The one generation workload this run did record is the 20 decomposition rewrites, one per two-hop question: 0.88 to 4.6 seconds each and 47.2 seconds in total at 60 max tokens (`decomposition.json`). Those are rewrites, not answers over retrieved facts, so they do not bound the cost of a 40-question, four-arm reader grid, and no such bound is claimed here. The probe takes `--deadline-epoch` for exactly this reason: its default budget is 900 seconds, it skips any remaining decomposition calls 240 seconds before the deadline, and the reader loop stops 120 seconds before it — a reserve too small for a four-arm reader grid on a shared 2-vCPU host.

So of the three causes in the introduction, this article measures one: the bridging fact ranked below the cut. It does not measure "both facts reached the prompt and the model failed to join them", and it does not separate a store that never wrote the second fact from a store that writes it and ranks it badly — the published fixture contains both facts, which is what makes the coverage numbers meaningful in the first place.

What the reader arms would have added is the oracle-versus-top-5 gap: how much of the accuracy loss is retrieval and how much is joining. The probe in the evidence directory implements all four arms, so that gap is reproducible on a host that is not contended. The grading rule is in the probe, not in the prose: lowercase, replace non-alphanumerics with spaces, remove whitespace, and check whether the gold value appears in the answer.

## Why one-shot decomposition did not fix coverage

The decomposition arm was the one meant to answer "raise k or split the question" in accuracy terms, and it bought almost nothing. The union of its sub-query retrievals contained both required facts for 4 of the 20 two-hop questions, against 3 of 20 for a plain top-5 on the same encoder — one question out of twenty, on a subset that averaged 6.5 facts instead of 5.

The reason is visible in the rewrites themselves. All 20 questions produced parseable sub-query lines (none failed to parse; 44 sub-queries in total, 2.2 per question, capped at 4), but **0 of the 20 sets named the intermediate entity** the second hop needs — no region, no team. A one-shot rewriter sees only the question, and the question never contains the bridge, so the most it can do is restate the question in two ways or ask what the entity is:

```
Q:  I need to find the database behind inventory-api - if it went down, which cluster would I look at?
1. Which cluster is associated with the inventory-api?
2. What is the inventory-api?
3. How can I check if the inventory-api has gone down?
4. Which cluster should I look at if the inventory-api goes down?
```

All four sub-queries point at the same fact. The second hop never gets a query of its own, because nothing in the input suggests one. On one question the model refused outright — "orders-api is not mentioned in the question" — when the service name was, in fact, the whole question.

That is a structural limit rather than a complaint about a 0.5B model. Decomposition fixes multi-hop coverage only when the split is iterative: retrieve hop 1, put the intermediate entity into the next query, retrieve again. A single rewrite pass cannot introduce a value it has never seen. If you are evaluating "decomposition" as a fix for a two-hop failure, the first thing to check is whether your implementation is a loop or a single pass; this fixture says a single pass at this model size changes the coverage count by one question while costing one rewrite call and 2.2 retrieval calls per question (44 sub-queries over 20 questions, capped at 4).

## Ten lines to audit your own store

The measurement above is a fixture result; the transferable part is the check. This snippet is not the probe — it is the smallest version you can paste next to your own store, and it answers only the coverage question: for a question you already know needs two rows, are both rows in the set you would have sent?

```python
import json, math, urllib.request

def embed(texts):  # swap for your store's embedding client; shape stays the same
    req = urllib.request.Request("http://127.0.0.1:11434/api/embed",
        json.dumps({"model": "all-minilm", "input": texts}).encode(),
        {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["embeddings"]

def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))

# store_vectors: [(fact_id, vector)] for your own rows; question: the text you already know needs two rows
q = embed([question])[0]
ranked = sorted(((cos(q, v), fact_id) for fact_id, v in store_vectors), reverse=True)[:5]
print([fact_id for _, fact_id in ranked])   # are both required fact ids in this list?
```

Run it on twenty questions whose answers you already know need two rows. Two outputs matter. If both ids are absent from the top-5 for most questions, k is your first lever and the table above says roughly how much it buys. If both ids are present and the answer is still wrong, retrieval is not your problem and raising k will not fix it — the [context management write-up](https://baeseokjae.github.io/posts/agentic-workflow-context-management-2026/) covers what the prompt does with facts it already has.

Two cautions on reading the output. First, the check is per fact id, not per text: if your store writes two near-duplicate rows for the same fact, coverage will look better than the join does. Second, a five-slot cut is not a free parameter — raising it to 20 multiplied the facts in the prompt by four in this fixture, and this run records no token or latency measurement for that trade, so the count is the only part of it in evidence here.

## What this fixture does not tell you

- The store holds 120 facts and is scanned exactly. A production store with 10^5 to 10^6 vectors usually runs an approximate index, and recall of the index is a second, unmeasured loss on top of the ranking measured here.
- The rewriter is 0.5B parameters and the reader grid is not reported at all. A larger model may join the two facts more reliably once both are present, but that is an accuracy claim this run does not make; the coverage columns are the part that transfers.
- The fixture's questions are synthetic, three phrasings per shape. Real user questions carry more surface variation and, sometimes, the intermediate entity itself.
- Single run, one 2-vCPU aarch64 host, no retries: these are mechanism results with per-question rows published, not benchmark scores. One pair of arms is a reading, not a trend.
- Decomposition is tested as a single rewrite pass. A two-stage loop — retrieve, then ask again with the intermediate entity in hand — is not measured here and is the obvious next test.
- No monetary cost is stated. Everything ran locally; unknown cost is unknown, and no paid API was used.

## Evidence and reproduction

First-party artifacts, all published under this repository's `research/evidence/agent-memory-multi-hop-recall-2026/` directory:

- [`multihop_probe.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-multi-hop-recall-2026/multihop_probe.py) — stdlib-only probe: fixture builder, Ollama embedding calls, exact cosine ranking, arms, grading.
- [`fixture.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-multi-hop-recall-2026/fixture.json) — the 120 facts, 20 two-hop and 20 single-hop questions with gold values and the fact ids each answer needs.
- [`results-retrieval.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-multi-hop-recall-2026/results-retrieval.json) — per-question ranks, top-5 and top-20 id lists for all three encoders, and the measured embedding dimensions.
- [`decomposition.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-multi-hop-recall-2026/decomposition.json) — the raw rewrite each question produced and the sub-queries parsed from it.
- [`METHOD.md`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-multi-hop-recall-2026/METHOD.md) — host, model digests, grading rule, deviations.

Reproduce on any host with Ollama and the three models pulled:

```
python3 multihop_probe.py --out ./out --reader qwen2.5:0.5b --deadline-epoch $(( $(date +%s) + 5400 ))
```

`--deadline-epoch` is not decorative: the probe's default budget is 900 seconds, it stops decomposing 240 seconds before the deadline, and its reader loop breaks 120 seconds before it — not enough for a four-arm reader grid on a contended 2-vCPU host. The probe writes `fixture.json`, `results-retrieval.json`, `decomposition.json`, `results-reader.json` and `summary.json`; this run ended before the reader stage, which is why the last two are missing here rather than withheld. Embedding dimensions are recorded under `dims` in `results-retrieval.json` — 384, 384 and 768, measured by the probe — and the model digests in `METHOD.md` and `ollama-tags.json`. [Ollama's `/api/embed` documentation](https://docs.ollama.com/api/embed) is the endpoint contract. The two library pages ([`all-minilm`](https://ollama.com/library/all-minilm), [`nomic-embed-text`](https://ollama.com/library/nomic-embed-text)) give footprint and context window — 46 MB with 512 tokens, 274 MB with 2K tokens — but no embedding dimensions; the nomic page additionally repeats the vendor's own claim that it surpasses OpenAI's `text-embedding-ada-002` and `text-embedding-3-small`, a comparison this article does not test.

The useful conclusion is not "local stores cannot do multi-hop". It is that coverage and accuracy fail separately, that the bridge usually sits just past a five-slot cut, and that the audit which tells you which failure you have is ten lines long.
