---
title: "Listwise Reranking on a 0.6B Local Model: 1 Top-1 Gain out of 8 Queries, and 4 Answers That Would Not Parse"
date: 2026-11-21T17:34:13+00:00
lastmod: 2026-11-21T17:43:00+00:00
description: "An editorial fixture run on one 2-vCPU host with arctic-embed-s and qwen3:0.6b: listwise reranking moved 1 answer up and 1 down across 8 paired queries (2 rank changes), reached top-1 once against 0 for the plain embedder, and only 4/8 outputs parsed. Includes the reversed-order control, the failure taxonomy and measured per-query cost."
draft: false
tags:
  - listwise reranking local llm
  - qwen3 0.6b reranker
  - agent memory retrieval ranking
  - cross-encoder alternative cpu
  - reranker position bias
  - ollama rerank benchmark
  - hit rate at 1 measurement
  - arctic embed 33m
  - local retrieval latency cost
  - llm as reranker small model
cover:
  image: /images/agent-memory-listwise-rerank-local-llm-2026-presentation.png
  alt: 'Four-stage diagram: a question, the embedder returning ten candidates with a value-swapped near-duplicate first, a listwise rerank prompt to qwen3:0.6b, and the measured outcome per arm. Labels carry only values measured in this article.'
  caption: 'Listwise reranking on a 0.6B local model · measured on 8 paired queries, 2 vCPU, no GPU'
schema: "schema-agent-memory-listwise-rerank-local-llm-2026"
---

A vector store returns ten candidates. The sentence that answers the question is in there, at position three, behind a near-duplicate that states the same fact with the wrong number. Nothing errors. The agent answers confidently from the wrong value.

The standard fix in every guide is a cross-encoder reranker, which on a CPU-only box is a model you do not have. But a chat model is already loaded and resident. So the practical question is narrow enough to measure: if the top ten candidates go to a 0.6B local model with the instruction to return them best-first, does the correct answer reach position one, does the model reorder by relevance or by where the candidate sits in the prompt, and what does one query cost on a box that generates in the low teens of tokens per second?

This is a fixture-scale measurement of exactly that. It is an editorial experiment on one host, one embedder and one chat model. It is not a BEIR result and its numbers should not be compared with published retrieval benchmarks.

## What the run found

- On the 8 queries where the embedder put the answer at rank 2-10 and all three arms completed, the plain embedder scored hit@1 0/8 and MRR@10 0.438.
- The k=10 listwise arm moved 1 answer up, 1 down and left 6 unchanged; it ended at hit@1 1/8 with MRR@10 0.479.
- JSON output was not reliable: 4/8 k=10 responses parsed completely or partially, and only 1/8 returned every requested id exactly once.
- The reversed-order control ended at hit@1 0/8 with MRR@10 0.393; the k=10 arm minus the control is +1 hit@1 and +0.086 MRR.
- Coverage was cut short: the embedder arm recorded all 13 eligible queries, the k=10 arm 9 and the control 8, because the run was stopped while the control was still working. Every arm comparison below uses the 8 queries where all three arms have a row, and the unbalanced rows are still in the shipped results file.

The honest summary is that this model reordered the list and occasionally found the right answer, but it did not turn a rank-2 to rank-10 candidate set into a reliable top-1, and it failed to return a usable array often enough that a defensive parser is part of the price.

## What listwise reranking is, precisely

Pointwise rerankers score one candidate at a time. Listwise rerankers take the candidate set as input and emit a permutation of it. The formulation this experiment copies is the zero-shot one: a language model receives the candidate documents with identifiers and generates a reordered list of those identifiers, with no task-specific relevance labels and no training step (Ma et al., [Zero-Shot Listwise Document Reranking with a Large Language Model](https://arxiv.org/abs/2305.02156)).

The reason the technique is interesting on small models comes from a different paper. Sun et al. distilled a ChatGPT reranker into a 440M model and reported that the distilled 440M model outperforms a 3B supervised model on BEIR, which is the strongest published argument that reranking ability survives compression ([Is ChatGPT Good at Search?](https://arxiv.org/abs/2304.09542)). Both papers rank with models far larger than the one tested here, and neither reports a 752M-parameter local model on a hand-built fixture. That gap is what this run looks at.

One structural detail matters for anyone copying the method: published listwise rerankers handle long candidate lists with a sliding window over permutation prompts, because model context and output length are bounded. At k=10 this experiment uses a single call with no window, which is a simplification and not equivalent to a sliding-window reranker over 100 candidates.

## Why a reranker is supposed to help at all

The premise is not controversial in the literature. Across 18 heterogeneous zero-shot IR datasets, reranking and late-interaction systems gave the best average zero-shot effectiveness while BM25 remained a robust baseline, and the paper is explicit that the reranking systems pay for that with high computational cost ([BEIR](https://arxiv.org/abs/2104.08663)). That is the trade the reader is being asked to make: accuracy for compute. The measurement below asks what the accuracy half of that trade looks like when the compute is a fraction of a CPU core and the model is small.

## The fixture, and the gate it never passed

The plan called for 120 authored facts in 30 paraphrase clusters, each cluster holding four surface forms of one fact, plus 30 queries whose answer sits at embedder rank 2-10 for at least 60% of queries. A pre-run script had to prove that before any scoring, because a fixture where the embedder is already right cannot test a reranker.

The construction gate failed on all four builds. Each build's gate output is shipped with this article, so the numbers below are the builders' own measurements rather than a remembered narrative:

- v1, 120 documents (the four surface forms, no decoys): hit@1 30/30, saturated. Nothing to improve and no result to publish.
- v2, 180 documents (two value-perturbed near-miss decoys per cluster): hit@1 19/30, with 11 of 30 answers at rank 2-10.
- v3, 210 documents (adds one near-duplicate per cluster that differs from the answer surface only in the value): hit@1 17/30, 13 of 30 at rank 2-10.
- v4, 221 documents (attempts the value substitution on two surface forms per cluster instead of one): hit@1 17/30, 13 of 30 at rank 2-10 - identical answer ranks to v3, because the second near-duplicate never outranked the answer. This is the build the reranker was scored on.

The 221-document figure in the last build is not two decoys per cluster. The substitution only matches when the surface form contains the exact value string, so 41 of the 60 attempts produced a near-duplicate: 19 clusters ended with one and 11 with two, and the shipped fixture records exactly that split. Of the 221 documents, 120 are answer surface forms, 60 are the v2 near-miss decoys and 41 are value-swapped near-duplicates.

The final build still misses the 60% construction target: 13/30 queries sit in the 2-10 band, not 18/30. The anti-saturation clause is met and the construction target is not. Rather than tune decoys until a histogram looked right, the experiment ran on the eligible queries in fixture order and stopped part-way through the arms. The embedder arm has a row for all 13 eligible queries (C01, C02, C07, C09, C11, C14, C15, C16, C18, C19, C23, C25, C26); the k=10 arm reached 9 of them and the control 8, because the run was stopped while the control was working on C18. That leaves one unpaired k=10 row (C18) and four baseline-only rows (C19, C23, C25, C26) in the shipped results file, and every arm comparison in this article uses only the 8 queries - C01, C02, C07, C09, C11, C14, C15, C16 - that have all three rows. The 17 saturated queries are excluded from the comparison and their baseline ranks are still in the v4 gate file, so a reader can see what was dropped.

Each cluster is an operations fact of the kind an agent memory store actually holds: a rebuild duration, a retention window, an error code, a column type. The value-swapped decoy is the whole point. Without it the embedder separates topics; with it, the embedder has to separate two sentences that share every word except the number, which is the failure the reader is trying to fix.

## Four arms

Every arm holds the store, the encoder and the candidate set fixed and varies only the ranking stage.

- A: the embedder's own order. snowflake-arctic-embed:33m (33M parameters, 384 dimensions, 512-token context in the Ollama build), brute-force cosine over all 221 documents, k=10. No model call.
- B: listwise rerank of the top 10 by qwen3:0.6b with thinking disabled, temperature 0, seed 42, num_ctx 4096, JSON-constrained output, prompt asking for a JSON array of candidate ids best-first.
- D: the reversed-order control. The identical ten candidates, presented in reverse order, same prompt. If a model ranks by position rather than relevance, B and D diverge.

A k=20 arm was planned and dropped. Three exploratory calls were made on this contended 2-vCPU host, but their outputs and timings were not retained, so this article reports no k=20 measurement at all; a three-query probe would not have been comparable to the other arms in any case.

The control is the part that makes a gain interpretable. LLM judges are known to carry position, verbosity and self-enhancement biases ([Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)), and while that paper studies pairwise judging of chat answers rather than passage ranking, it is the reason a position control is included instead of trusting a single ordering.

## Results

The table below covers the 8 paired queries, same fixture, same host, one run.

| arm | hit@1 | MRR@10 | moved up / down / same | parsed |
|---|---|---|---|---|
| A embedder order (k=10) | 0/8 | 0.438 | - | n/a |
| B listwise rerank (k=10) | 1/8 | 0.479 | 1 / 1 / 6 | 4/8 |
| D reversed-order control | 0/8 | 0.393 | - | 3/8 |

Three things in that table deserve to be stated plainly.

First, the top-1 count barely moves: 1 of 8 answers reached rank 1 under the k=10 arm, 0 under the embedder alone and 0 under the reversed-order control. The candidates were tight by construction - with a value-swapped near-duplicate in the list, the model had to decide which of two nearly identical sentences answered the question, and it did that rarely.

Second, aggregate MRR@10 went from 0.438 to 0.479 across these 8 queries, so the reordering was on average a small gain. Movement was not noise-free in either direction: C01 dropped from rank 2 to rank 3 and C14 rose from rank 2 to rank 1, so the arm changed rank for 2 of the 8 queries and left 6 unchanged.

Third, the control is the number to read before the gain. The k=10 arm and the reversed-order arm differ by +1 hit@1 and +0.086 MRR, so most of what the model did reproduced under a reversed prompt. That is a weak positive: the model is not simply echoing the input order. It is also not evidence of relevance skill: one top-1 answer out of 8, against 0 under the control, is not a ranking stage you would put in a query path.

## The parse failures are a result, not an incident

Only 1 of 8 k=10 responses returned the requested array with every id exactly once. The rest split into three failure modes, each visible in the raw output files:

- Object wrapper: the model returned `{"candidates": [3,1,2,...]}` instead of a bare array even with JSON output enabled. Recoverable with a tolerant parser, which is what the harness does.
- Truncated list: valid JSON with some ids missing, so the harness appends the missing ids at the end. This silently degrades the arm, because a short list is not a full ranking.
- Invalid ids: values outside 1..k or repeated entries. The harness falls back to the embedder's order for that query.

A 752M-parameter model asked for a strict array format is at the edge of what an instruction can enforce, and the practical lesson is that any local reranker needs a defensive parser plus a documented fallback order. A silent fallback to the embedder order is the right behaviour, because it is never worse than the baseline. It also means a naive evaluation that counts exceptions as successes will overstate the reranker.

## What a query costs on this host

The cost model is deliberately mechanical so it can be recomputed on other hardware.

- Median prompt size: 260 tokens for the k=10 arm, measured by the server's prompt_eval_count rather than estimated from characters.
- Median output: 116 tokens per query.
- Median wall clock per reranked query: 26.0 s, with a worst case of 137.3 s on this contended 2-vCPU host.
- Median generation speed: 9.6 tokens/s.

The tokens/s figure is worth flagging because it contradicts the planning assumption. The plan carried a 5.7 tokens/s observation from an earlier run; this run measured a median of 9.6 tokens/s on the same model with thinking disabled, and individual queries varied by more than 3x as the box was shared. Wall clock on a CPU box is not a stable property of the model, which is why the token counts are published next to it.

To recompute the bill on different hardware, take the measured prompt and output token counts, divide the output count by the tokens/s of your box, add the prefill time for the prompt, and multiply by the number of queries per turn. The Ollama API exposes eval_count and eval_duration for exactly this ([Ollama API docs](https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md)), and if your client omits them you are estimating rather than measuring.

## The decision rule this measurement supports

Spending latency on a ranking stage is worth it when the ranking stage is better than the retriever at the specific thing that is failing. On this fixture the failing thing was a value-level distinction between two sentences with nearly identical wording, and a 752M-parameter model with a one-line instruction did not resolve it.

The rule that follows is narrower than "do not rerank" and more useful than "always rerank":

- If your top-1 errors are topic-level (the wrong document entirely), a listwise pass over 10-20 candidates is cheap enough to try, and the parse-failure rate you measure is the real cost, not the token count.
- If your top-1 errors are value-level (right document, wrong number), this measurement gives you no reason to expect a small model to fix them, and you should fix the write path, the chunk boundary or the encoder instead.
- If you cannot afford a defensive parser and a fallback order, do not put the model in the query path at all.

If you want the encoder lever measured on the same kind of fixture, the embedding-swap piece in this cluster does that with the store held fixed; the chunk-granularity piece isolates the split; and the Elasticsearch build shows what a hosted reranker stage looks like when the budget allows one. Those three pages are the honest alternatives to this one, and none of them is a substitute for it, because each changes a different lever:

- [agent-memory-embedding-swap-recall-2026](https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/) changes the encoder.
- [agent-memory-chunk-granularity-recall-2026](https://baeseokjae.github.io/posts/agent-memory-chunk-granularity-recall-2026/) changes the split.
- [persistent-agent-memory-on-elasticsearch-building-0-89-recall](https://baeseokjae.github.io/posts/persistent-agent-memory-on-elasticsearch-building-0-89-recall/) builds a hosted reranking stage.
- [vector-database-rag-alternative-2026](https://baeseokjae.github.io/posts/vector-database-rag-alternative-2026/) carries the literature's hybrid+rerank numbers, which is the comparison this fixture cannot make.
- [vector-database-comparison-2026](https://baeseokjae.github.io/posts/vector-database-comparison-2026/) is where store choice belongs, and [local-agent-turn-time-budget-2026](https://baeseokjae.github.io/posts/local-agent-turn-time-budget-2026/) is where the per-query second you just spent has to be accounted for.

## Versions, and what this run does not support

- Host: 2 vCPU, no GPU, ollama 0.20.3. Model digests qwen3:0.6b 7df6b6e09427 and snowflake-arctic-embed:33m e8db018629b4.
- qwen3:0.6b is 523 MB at Q4_K_M and reports 752M parameters in Ollama ([qwen3:0.6b](https://ollama.com/library/qwen3:0.6b)), while the upstream card lists 0.6B total and 0.44B non-embedding parameters with a 32,768-token context ([Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)). The runtime context used here was num_ctx 4096, not the card's maximum.
- The embedder is arctic-embed-s: 33M parameters, 384 dimensions, vendor-reported 51.98 MTEB retrieval NDCG@10, distinct from the 22M -xs at 50.15 ([model card](https://huggingface.co/Snowflake/snowflake-arctic-embed-s)). That vendor score is not this fixture's baseline and is not used as one.
- 8 paired queries is too few for a significance claim, and none is made here; the counts are published exactly so a reader can see how little they support.
- Nothing here generalises to hosted cross-encoders, GPU serving, larger local models or other quantizations.
- The reversed-order control detects order sensitivity; it cannot attribute it to position, length or recency.

## Reproduce it

The fixture, query set, the four builders with each build's gate output, the harness, the per-query results and the verbatim model output are committed with this article under `research/evidence/agent-memory-listwise-rerank-local-llm-2026/`:

- [fixture.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/fixture.json) - 30 clusters, their four surface forms, the near-miss decoys and the 41 value-swapped near-duplicates.
- [queries.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/queries.json) - the 30 queries.
- [build_fixture_v4.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/build_fixture_v4.py) - the builder of record for the 221-document fixture, with [build_fixture.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/build_fixture.py) (v1 facts and queries), [build_fixture_v2.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/build_fixture_v2.py) and [build_fixture_v3.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/build_fixture_v3.py) for the earlier builds.
- [prerun_gate.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/prerun_gate.json) - the 221-document build's gate: baseline rank per query and the verdict.
- [prerun_gate_v1.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/prerun_gate_v1.json), [prerun_gate_v2.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/prerun_gate_v2.json) and [prerun_gate_v3.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/prerun_gate_v3.json) - the gate output of each earlier build, so the build history above is verifiable rather than remembered.
- [rerank_bench.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/rerank_bench.py) - the harness for arms A, B and D.
- [results.csv](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/results.csv) - one row per query per completed arm, with token counts and wall clock, including the 13 embedder rows, the 9 k=10 rows and the 8 control rows.
- [raw output](https://github.com/baeseokjae/baeseokjae.github.io/tree/main/research/evidence/agent-memory-listwise-rerank-local-llm-2026/raw) - the verbatim response for every query in every completed model arm.

Run it with `ollama pull qwen3:0.6b`, `ollama pull snowflake-arctic-embed:33m`, then `PYTHONPATH=. python3 build_fixture_v4.py evidence` followed by `python3 rerank_bench.py --evidence evidence --out run1 --arms B,D --minrank 2 --maxrank 10`. The `PYTHONPATH=.` is required because the v4 builder imports the fact list, the decoys and the value pairs from the earlier builders in the same directory. Expect the same parse failures; they are the point of the raw directory. Re-running the v4 builder on the same host and embedder reproduced the shipped fixture.json, queries.json and gate measurements byte for byte.
