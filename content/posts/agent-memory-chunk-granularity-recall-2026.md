---
title: "Agent Memory Chunking: When Smaller Chunks Lose the Answer"
date: 2026-11-15T08:55:36+00:00
lastmod: 2026-11-19T17:30:35+00:00
description: "An 8-document, 13-question fixture on three local Ollama embedders: two-fact hit@1 falls from 13/15 with whole-document vectors to 0/15 at 3-sentence and single-sentence chunks, while mean top-3 context drops from 1,444 to 210 characters. Includes the probe script and fixture."
draft: false
tags:
  - chunk size agent memory
  - retrieval granularity
  - agent memory recall measurement
  - sentence chunking vs document chunking
  - ollama embedding models
  - two-fact retrieval
  - context cost per retrieval
  - vector store chunking
  - retrieval hit rate fixture
  - rag chunk boundary
cover:
  image: /images/agent-memory-chunk-granularity-recall-2026-presentation.png
  alt: 'Conceptual checklist for memory chunk granularity: a question that needs two facts, the chunk boundaries that separate them, and the retrieved evidence — smaller chunks can split a multi-fact answer. Conceptual diagram, not measurement data.'
  caption: 'Memory chunk granularity · conceptual checklist, not new measurement data'
schema: "schema-agent-memory-chunk-granularity-recall-2026"
---

An agent memory store is usually built by a chunker that nobody re-examines after the first week. One vector per conversation turn, per note, or per fixed block of text. The store looks healthy, because the questions used to check it are single-fact questions about a short note, and those pass at almost any granularity. Then a user asks a two-part question — "how do access-token and signing-key lifetimes compare?", "who owns the deploy key and how often does it rotate?" — and the retriever returns one half of the answer with no error at all. The other half is in a different chunk and did not fit in the top-k.

The opposite mistake is just as common. Keeping whole documents to preserve context means every retrieval drags 1,400 characters of mostly irrelevant prose into the prompt instead of 210.

This article measures the tradeoff instead of asserting it. On one host, with three locally served embedding models, an 8-document fixture and 13 questions, the short answer is:

- Single-fact recall did not degrade as chunks got smaller (21/24 pooled whole-document, 23/24 at 3-sentence windows, 23/24 at single sentences).
- Two-fact recall at k=1 collapsed from 13/15 to 0/15 the moment document-level vectors were replaced by 3-sentence windows, and stayed at 0/15 at sentence level.
- The two facts usually survived somewhere in a deeper ranking: both required sentences appeared in the top 8 for 15/15, 13/15 and 12/15 respectively.
- Mean characters in the top-3 retrieved chunks fell from 1,444 to 475 to 210 — about 6.9x less prompt context for the same k.

So the decision is not "smaller chunks retrieve better" or "bigger chunks preserve meaning". It is: what query shape do you serve, and can your retriever merge two chunks before the prompt budget closes?

## The two questions your chunker decides for you

A chunk boundary is a retrieval contract. Whatever else you configure, two properties of your system are fixed the moment the chunker runs.

The first is **composability**: can any single retrieved unit contain all the facts that one realistic question needs? A sentence chunk can answer "what is the retry interval" and can never answer "how does the retry interval compare with the escalation delay", because a comparison needs two sentences and one chunk holds one. Nothing errors. The ranker returns its best single sentence, which is a correct answer to half of the question.

The second is **context cost per retrieval**: how much text does k=3 hand to the model? With whole-document vectors, three hits are three documents. That is fine when documents are 480 characters and expensive when they are 8,000.

Both properties are measurable before you pick a chunk size, and neither is answered by vendor documentation. Vendor pages tell you the context window and the API shape, not what your boundaries do to your recall.

## What the fixture measures, and what it does not

Eight invented project documents (deploy, billing, auth, search, mobile, pipeline, support, infra), seven sentences each, 456–500 characters per document, 52–99 characters per sentence. Each document carries one needle fact, plus facts that only mean something when combined with an adjacent sentence. Eight single-fact questions (one per document) and five two-fact questions whose two required sentences sit on opposite sides of a 3-sentence window boundary.

Three granularities of the same corpus:

- whole document: 8 vectors per model
- non-overlapping 3-sentence windows: 24 vectors (sentences 1–3, 4–6, 7)
- single sentences: 56 vectors

Three embedders served by local Ollama 0.20.3 through `/api/embed`: all-minilm:latest (384-d), snowflake-arctic-embed:33m (384-d) and nomic-embed-text:latest (768-d). Cosine on L2-normalised vectors, a deterministic full sort, no generation, no re-ranker, no hybrid search, no metadata filters. Each row reports single-fact hit@1 (the needle sentence is inside the top-1 chunk), two-fact hit@1 (both required sentences are inside the top-1 chunk), and the mean character count of the top-3 chunks. The full sweep took 54 seconds.

What this does **not** measure: answer quality, latency, throughput, token counts, production recall, or user satisfaction. hit@1 here means "the right text was in the returned chunk". Nothing else.

## Result 1: fine chunks cost nothing on single-fact questions

Pooled over the three embedders and the eight single-fact questions — 24 model-question pairs per granularity:

| Granularity | Vectors per model | Single-fact hit@1 | Two-fact hit@1 | Both facts in top 8 | Mean top-3 chars |
| --- | --- | --- | --- | --- | --- |
| Whole document | 8 | 21/24 | 13/15 | 15/15 | 1,444 |
| 3-sentence windows | 24 | 23/24 | 0/15 | 13/15 | 475 |
| Single sentence | 56 | 23/24 | 0/15 | 12/15 | 210 |

Per model, single-fact hit@1 moved 8/8 → 8/8 → 8/8 (all-minilm), 6/8 → 7/8 → 8/8 (arctic-33m) and 7/8 → 8/8 → 7/8 (nomic). Those are one-query swings on an eight-question set. The honest reading is "no measurable damage from finer chunks", not "fine chunks beat documents". Anyone who has read a single-fact recall table will recognise the shape: at 480-character documents, the whole-document vector is not diluted enough to hurt, and the small deficits are noise.

This is the result that makes chunking decisions go wrong. A team shrinks chunks, reruns its single-fact regression suite, sees 8/8 unchanged, and concludes the change was free. It was not free. The cost is simply invisible to that test suite.

## Result 2: fine chunks lose the two-fact answer completely at k=1

Same fixture, five two-fact questions, top-1 only:

| Granularity | Two-fact hit@1 (pooled) | all-minilm | arctic-33m | nomic |
| --- | --- | --- | --- | --- |
| Whole document | 13/15 | 4/5 | 4/5 | 5/5 |
| 3-sentence windows | 0/15 | 0/5 | 0/5 | 0/5 |
| Single sentence | 0/15 | 0/5 | 0/5 | 0/5 |

Two mechanisms produce that zero, and they are not equally general.

At **sentence granularity** the zero is structural: one sentence cannot contain two sentences, so no ranking can ever satisfy the condition. Any corpus, any embedder, any question shape. If your questions ever require two facts, single-sentence chunks at k=1 are guaranteed to fail, and the failure is silent because the top hit is still a sensible sentence.

At **3-sentence windows** the zero is constructed. The five pairs were deliberately placed to straddle a window boundary, so each question's two sentences necessarily land in different windows. That is a worst case, and a corpus whose two-fact answers happen to fall inside one window would score differently. It is also not an artificial worry: any fixed-width window will straddle some fraction of real co-reference pairs, and the fraction grows as the window shrinks.

At **top-3** the loss softens but does not disappear: both required sentences appear among the three returned chunks for 15/15 whole-document, 10/15 at 3-sentence windows and 8/15 at single sentences. A retriever that merges its top-3 into one context window recovers some of the damage — but only if it merges, and only if the ranker put both halves inside k.

## Result 3: the facts are usually still there, just not together

The most useful number in the run is the top-8 check. Both required sentences appeared somewhere in ranks 1–8 for 15/15, 13/15 and 12/15 across the three granularities. At sentence level, twelve of fifteen two-fact questions had both halves one deeper ranking away.

That reframes the fix. If your retriever can see the fragments, the problem is assembly, not indexing, and assembly is cheaper than re-chunking a live store:

- **Merge before the prompt.** Retrieve 8–10 chunks, then concatenate neighbours from the same source document (or group by document id) before the model sees them. This converts a ranking problem into a grouping problem.
- **Two-stage retrieval.** Retrieve wide at fine granularity, then re-rank or expand the winning chunks to their parent window. The classic parent-document pattern.
- **Keep a dual index.** Fine chunks for precision, whole documents for context, and choose per query shape.

All three need the store to record what the chunk *is*: source document id, sentence offsets, the encoder's identity and digest, and the vector's dimension. Without that metadata you cannot expand a hit to its neighbours, and you cannot tell whether a stored vector is comparable to a query vector. [The write-path article covers the record each chunk needs](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/).

## Result 4: what coarse chunks cost in prompt characters

Mean characters of the top-3 retrieved chunks, averaged over the eight single-fact queries per row: 1,444 for whole documents, 475 for 3-sentence windows, 210 for single sentences. That is 6.9x less text for the same k.

Two cautions, both of which matter more than the ratio itself.

It is characters, not tokens. No tokenizer was run, so this is not a cost figure and should not be converted into one. If you need tokens, measure them; the Ollama embed response carries `prompt_eval_count` specifically so you do not have to guess ([embed API reference](https://docs.ollama.com/api/embed)).

The ratio is a property of *your* document lengths, not a constant. These documents are 482 characters on average, so a whole-document chunk is about six sentences' worth of prose — the coarse setting here is only mildly coarse. At 8,000-character documents the same table would show a far larger ratio, and at 200-character notes it would nearly vanish. The transferable finding is the direction and the mechanism, not 6.9.

## Does the embedder change the answer?

No — the shape held on all three models. Every embedder went 4/5-or-5/5 → 0/5 → 0/5 on two-fact hit@1 while staying flat on single-fact recall. That consistency is why the effect reads as a property of the chunk boundary rather than of one model's geometry.

The nomic row needs a specific caveat. nomic-embed-text-v1.5's [model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) states that the text must carry a task instruction prefix: `search_document: ` for indexed text and `search_query: ` for queries. This harness sent no prefixes to any model, and Ollama's own [nomic-embed-text library page](https://ollama.com/library/nomic-embed-text) shows an example without them. So nomic's absolute numbers here are not a fair model comparison and must not be read as a ranking. The prefix omission applies in code to all three rows equally, but only nomic documents the requirement — meaning nomic is the row most likely to be depressed by the choice.

The practical consequence: choose the chunk size before you choose the embedder. The boundary failure shows up on every model tested; the encoder choice changes absolute recall, not whether a two-sentence question can be answered by a one-sentence chunk.

One sizing check belongs here, because it explains why truncation is not a confound in this run. all-minilm and snowflake-arctic-embed:33m both publish a 512-token context window on their Ollama library pages ([all-minilm](https://ollama.com/library/all-minilm), [snowflake-arctic-embed](https://ollama.com/library/snowflake-arctic-embed)), and `/api/embed` defaults to `truncate: true`, silently clipping longer inputs. At roughly 482 characters per document — on the order of 120 tokens at a rule-of-thumb 4 characters per token — no indexed chunk here came close to that ceiling. That is a sizing argument, not a measurement: `prompt_eval_count` was not recorded in this run. The truncation ceiling itself is a different failure and is [measured separately](https://baeseokjae.github.io/posts/local-embedding-context-ceiling-2026/).

This also separates the result from the encoder-side failure measured in [the embedding-swap harness](https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/), where replacing an encoder with a same-width model turned ranking into noise. Here the encoder is fixed within each row and only the boundary moves, which is the only way to attribute the change to chunking.

## A decision procedure for your own corpus

The fixture is small on purpose: it makes the mechanism visible in under a minute, and it is meant to be replaced by your own documents. The harness is published — point it at your corpus, not at mine.

To reproduce this exact run you need Ollama serving the three models locally. Then:

```
python3 chunk_probe2.py fixture.json results2.json
```

`chunk_probe2.py` records each needle's rank to depth 8 and reports `both_in_top8` alongside hit@1 and hit@3; `chunk_probe.py` is the earlier hits-only sweep. Both read the fixture JSON, call `http://127.0.0.1:11434/api/embed` only, and print one row per (model, granularity).

The published files, all original and inspectable before you run them:

- [chunk_probe2.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-chunk-granularity-recall-2026/chunk_probe2.py) — the probe, parameterised by fixture and output path
- [fixture.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-chunk-granularity-recall-2026/fixture.json) — 8 documents, 8 single-fact and 5 two-fact questions
- [results2.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-chunk-granularity-recall-2026/results2.json) — the raw per-row output behind every number above
- [environment.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-chunk-granularity-recall-2026/environment.json) — model names, digests, host and scoring settings
- [METHOD.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-chunk-granularity-recall-2026/METHOD.md) — method, commands and known deviations

Note that the fixture text ships with the probe and is entirely invented; nothing in it comes from a customer, a vendor, or a public benchmark.

The procedure to apply to your own store:

1. **Write your real question shapes down first**, separated into single-fact and multi-fact. If you have no multi-fact questions in that list, this entire article is not your problem yet — but your users will find some.
2. **Build a labelled set of 30–100 questions** over your own documents, each with the sentence or span that answers it. Thirty is enough to see a collapse from 13/15 to 0/15; it is not enough to resolve a two-query difference.
3. **Run candidate chunk sizes** with the embedder you actually deploy, at your real k. Report hit@1 *per question shape*, never pooled across shapes — pooling is exactly how a two-fact regression hides inside a flat single-fact score.
4. **Read the two numbers together.** If multi-fact hit@1 collapses but deep-rank coverage holds, fix assembly: raise k and merge by parent document. If coverage also collapses at your k, the chunker is too fine for that query shape and the boundary has to move.
5. **Report the context cost of whatever you choose.** Doubling k to recover assembly costs prompt characters on every turn; measure it in characters or tokens, not in vibes.

## Limitations

- Eight documents, thirteen questions, three embedders: a fixture sized to expose a mechanism in under a minute, not a benchmark. No production recall, answer-quality, latency or satisfaction claim follows from it.
- The five two-fact pairs were placed to straddle a window boundary by construction, so 0/15 at fine granularity is a designed worst case.
- Retrieval only: no generation, no re-ranker, no hybrid BM25, no metadata filters.
- Character counts are not tokens, and the 6.9x ratio must not be converted to token cost without measuring a tokenizer.
- nomic-embed-text ran without its required task prefixes, so its absolute numbers are not a fair model comparison.
- Single-fact differences between granularities are one-query swings on an eight-question set and are not statistically meaningful.
- One host (2 vCPU, 11 GiB, Ollama 0.20.3), localhost only; elapsed times are load-in dominated and are not throughput figures.
- Embeddings are reproducible only for an identical model digest. Any rerun with a different digest is a different experiment, and results2.json records the digests it ran against.

The result should be falsifiable in public: rerun the fixture, and if 3-sentence windows do not beat whole-document chunks on single-fact hit@1 for at least two of three embedders — or if two-fact hit@1 does not fall when moving from whole documents to sentence chunks — then this fixture is not reproducing and you should trust your own numbers over this table.

If you are still choosing where memory lives at all, [the framework comparison](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) covers the vendor side. This article assumes you already have a store and asks the smaller question that decides whether it works: how big is a vector's worth of truth.
