---
title: "Ollama dimensions for Agent Memory: What Cutting Vector Width Costs in Recall"
date: 2026-11-21T15:40:00+00:00
lastmod: 2026-11-21T16:17:00+00:00
description: "Measured on Ollama 0.20.3: the dimensions option returns normalise(full[:d]), and cutting 384 to 128 dims costs 1.7 points recall@5 in a 50-fact store but 10.0 points at 800 facts. Fixture, scripts and raw rows published."
draft: false
tags:
  - ollama dimensions option
  - agent memory embedding size
  - vector truncation recall
  - matryoshka embeddings
  - embedding dimension reduction
  - recall at 5 measurement
  - local embedding model memory
  - vector store size savings
  - snowflake arctic embed 33m
  - nomic embed text dimensions
cover:
  image: /images/agent-memory-embedding-dimensions-recall-curve-2026-presentation.png
  alt: "Line chart of recall@5 against stored vector width (384, 256, 128, 64 dims) for snowflake-arctic-embed:33m at three index sizes. The 50-fact store stays at 0.983 and 0.967 for 384 and 128 dims; the 800-fact store falls from 0.650 to 0.550 over the same 3x byte cut."
  caption: "Recall@5 vs stored width by index size · local fixture, ollama 0.20.3"
schema: "schema-agent-memory-embedding-dimensions-recall-curve-2026"
---

Your agent memory table has become the biggest thing you own. The embedding model is small, the code is small, but a million stored vectors at 384 float32 dimensions is 1.5 GB of payload before any index overhead, and Ollama's embed API exposes a `dimensions` option that looks like a free discount: ask for 128 instead of 384 and the payload drops to one third.

The discount is real. The question is what it does to retrieval, and the documentation does not answer it. The embed API reference declares the parameter in a single line — "Number of dimensions to generate embeddings for" — and says nothing about how the shorter vector is produced. If your agent memory is full of near-duplicate facts (the same preference restated four ways, the same project detail rephrased across sessions), the shorter vector is exactly where those paraphrases start colliding, and the failure mode is silent: the wrong paraphrase wins the top-k, and only questions that need one specific variant come back wrong.

This article answers that with two measurements made on one machine. First, what the option actually computes. Second, what it costs, as a curve over (vector width × index size) rather than a single number.

The short version:

- On ollama 0.20.3 the option is prefix truncation followed by renormalisation. A request for d dimensions returns `normalise(full[:d])` to float32 rounding, with a maximum absolute difference of 1.3e-07 across eight model/width probes. It does not re-embed at the lower width.
- Cutting 384 → 128 dims (a 3x payload cut) costs 1.7 points recall@5 in a 50-fact index and 10.0 points in an 800-fact index of the same facts. The cost is not a flat percentage; it is a function of how crowded the store is.
- Below 128 dims the arctic-embed:33m curve flattened on this fixture: 128 and 64 dims produced identical recall@5 (0.550) at 800 facts, and 0.967 at 50 facts.

Those numbers come from a synthetic fixture I built for this article on a 2 vCPU host with no GPU. They are not a benchmark of any embedder, and a single 384-dim encoder family cannot tell you what a hosted API would do. They are enough to show the shape of the trade, and the fixture and raw rows are published so you can rerun them against your own corpus.

## What the dimensions option actually computes

The mechanism matters because it decides whether truncation is reversible. Two behaviours are possible: the server could re-embed the text with a shorter output layer, or it could compute the full vector and slice. They produce different vectors, and only the second one lets you keep the full vector and derive the short one later.

This run compared the API output at d ∈ {32, 64, 128, 256} against `normalise(full[:d])` computed from the same model's full-width vector, using five probe texts per model. For snowflake-arctic-embed:33m (384 native dims) the largest absolute difference was 6.3e-08 at d=32 and 1.29e-07 at d=256. For nomic-embed-text:latest (768 native) it was 7.5e-08 at d=32 and 7e-08 at d=256. Every returned vector was unit length to within 2.6e-07, and every request returned exactly the number of dimensions asked for.

So on this version, the option is a lossy slice plus renormalisation. Three consequences follow:

- The information in dimensions d+1..N is gone from what you store. You cannot recover it by re-normalising later, and you cannot "upgrade" a truncated index in place — you would have to re-embed from the text, which means you still need the text — and how much of that text one embedding covers at ingest is a boundary this site [measured separately](/posts/local-embedding-context-ceiling-2026/).
- Keeping the full vector while indexing the short one is possible and cheap on the write side, because the short vector is derived, not separately computed. That is what makes a two-index or index-plus-rerank strategy viable. Whether a paraphrase gets written to the table at all is a different control: the dedupe threshold on that write path is [measured here](/posts/agent-memory-similarity-threshold-drops-constraints-2026/), and it sets how much crowding this width question ever has to answer.
- Because the operation is a plain prefix, its quality depends entirely on how much of the semantic content the encoder packed into the first d dims — which is a property of training, not of Ollama.

The [embed API reference](https://docs.ollama.com/api/embed) documents none of this. It is a measurement, and it is version-scoped: it holds for ollama 0.20.3 on this host with these two models, and the honest reading is "verified here, re-verify on your version".

## Why the safe width depends on the encoder, not on your storage target

Prefix truncation keeps information only if the encoder was trained so that early dimensions carry most of the signal. Matryoshka Representation Learning (MRL) does exactly that: it trains nested sub-vectors so a single embedding can be truncated to a smaller width and still be useful, a property described in the [MRL paper](https://arxiv.org/abs/2205.13147) as encoding "information at different granularities".

The two encoders in this run sit on opposite sides of that line, and the difference is visible in vendor material rather than in any Ollama documentation:

- The [Snowflake arctic-embed repository](https://github.com/Snowflake-Labs/arctic-embed) claims MRL training for arctic-embed-m-v1.5, saying it delivers retrieval performance "even when vectors are truncated to 256 dimensions". The arctic-embed-s section, which carries the 33m parameters and 384 dimensions that the Ollama `snowflake-arctic-embed:33m` tag matches, makes no MRL claim at all.
- The [nomic-embed-text-v1.5 model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) documents MRL usage explicitly: take the layer-normalised output, slice to the target width, L2-normalise. Its example `matryoshka_dim` is 512 out of 768.

That is the reason this article measures the plain 384-dim encoder at three index sizes and the MRL 768-dim encoder at the full index only: they are different questions. For a non-MRL encoder, truncation is information loss that you hope the corpus can absorb. For an MRL encoder it is a supported operating mode whose cost still has to be measured, because "trained for it" is not "free".

And if the width curve you measure turns out unacceptable, the encoder is the other lever: swapping models at a fixed width is a different trade with its own measured cost, covered in [what an encoder swap actually buys](/posts/agent-memory-embedding-swap-recall-2026/). Shrinking a vector and replacing the model that produced it are not substitutes, and only one of them is reversible from stored data.

## The fixture: 800 paraphrased facts, 40 queries, targets always indexed

The experiment holds the encoder, the chunk text, the metric and the query set fixed and varies only the stored width. Chunking is the other lever that decides what sits inside one vector, and it is held constant here because this site already [measured how splitting the same content changes recall](/posts/agent-memory-chunk-granularity-recall-2026/); changing both at once would confound the width effect.

The corpus is 800 fact strings: 200 subjects, each expressed in four surface-form paraphrases of the same fact, and each variant carries a unique codename so a scorer can tell which variant a query is supposed to match. The query set is 40 questions: 20 cluster-level, where any of the four variants is a correct answer, and 20 exact-paraphrase, where one specific variant is correct. Index sizes are 50, 200 and 800 facts, with three distractor orderings per cell, and every query's target facts are guaranteed to be present in the index being searched.

That presence guarantee needs stating because the first scoring pass in this run did not have it. It sampled each index as a random subset of the 800 facts, which meant some query targets were simply absent — an automatic miss that made recall look *worse* at small index sizes for the wrong reason. Those rows are preserved unedited as [results.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/results.csv) and published with the rest of the evidence for audit; no claim here uses them. Every number in this article comes from the presence-guaranteed re-score for the 384-dim encoder, or from the full-index cells, where presence is guaranteed by construction.

What the fixture is not: real prose. Template-generated paraphrases have cleaner semantic separation than messy notes, so the absolute recall values are optimistic. The direction and relative size of the width effect are the transferable part.

## The measured curve

Recall@1, recall@5 and MRR for `snowflake-arctic-embed:33m` (384 native dims), cosine on normalised vectors, deterministic full sort, mean of three distractor seeds. Bytes per vector are float32 payload only: 4 × width.

| Index size | Width | Bytes/vector | R@1 | R@5 | MRR |
|---|---|---|---|---|---|
| 50 facts | 384 | 1,536 | 0.708 | 0.983 | 0.813 |
| 50 facts | 256 | 1,024 | 0.725 | 0.975 | 0.821 |
| 50 facts | 128 | 512 | 0.683 | 0.967 | 0.790 |
| 50 facts | 64 | 256 | 0.658 | 0.967 | 0.776 |
| 200 facts | 384 | 1,536 | 0.617 | 0.783 | 0.681 |
| 200 facts | 256 | 1,024 | 0.567 | 0.783 | 0.652 |
| 200 facts | 128 | 512 | 0.558 | 0.692 | 0.626 |
| 200 facts | 64 | 256 | 0.525 | 0.767 | 0.618 |
| 800 facts | 384 | 1,536 | 0.575 | 0.650 | 0.599 |
| 800 facts | 256 | 1,024 | 0.525 | 0.575 | 0.549 |
| 800 facts | 128 | 512 | 0.500 | 0.550 | 0.532 |
| 800 facts | 64 | 256 | 0.500 | 0.550 | 0.526 |

Read the 384 row down instead of across and the point of the article appears: adding 16x more facts to the same index costs more recall (0.983 → 0.650 R@5) than cutting the vector to a third of its width at the largest size. Width is not the dominant lever in this fixture. Crowding is.

## At 800 facts, three times the savings costs ten points

At the largest index size, 384 → 128 dims cuts the vector payload from 1,536 to 512 bytes — exactly one third — and recall@5 falls from 0.650 to 0.550, with recall@1 from 0.575 to 0.500 and MRR from 0.599 to 0.532. Ten points of recall@5 and 7.5 points of recall@1 for a 3x storage cut, with no seed variance at all: all three distractor orderings produce the identical 0.550 at both widths, because the ordering only permutes the distractor set and the corpus is dense enough that the same candidates win.

At 50 facts the same 3x cut costs 1.7 points of recall@5 (0.983 → 0.967) and 2.5 points of recall@1 (0.708 → 0.683). The 50-fact store is close to the recall@5 ceiling, which compresses any difference there — you cannot lose ten points when you only had 1.7 to lose. So the honest statement is not "truncation is cheap" or "truncation is expensive"; it is that the cost grows with how many near-duplicate candidates compete for the same top-k slots, and a store of hundreds of paraphrased facts per subject is where it starts to bite.

The 200-fact row is the awkward one, and worth reporting rather than smoothing: 384 and 256 tie at 0.783 R@5, 128 drops to 0.692, and 64 recovers to 0.767. A non-monotone wobble of that size, on 40 queries, is inside the noise this fixture can resolve — 40 queries means one query is 2.5 points, and the three seeds differ by up to 5 points in that cell. Treat the 128 dip at 200 facts as unresolved rather than as a real property of the encoder.

## Below 128 dims the curve flattened

At 800 facts, going from 128 to 64 dims halves the payload again (512 → 256 bytes) and changes nothing measurable: R@1 0.500, R@5 0.550, MRR 0.532 → 0.526, identical across all three seeds. The gradual part of the loss is between 384 and 128; past that, this fixture says you are buying bytes at no measured additional cost.

That is a plateau, not a licence. At 128 and 64 the absolute numbers are already poor (half the queries miss the top-1 slot), so equal scores are equally consistent with a floor as with equal information content — once the right variant has fallen out of the candidate set, it stays out at any width below. Read the plateau as "this fixture cannot distinguish 128 from 64", which is a much weaker statement than "64 dims is fine", and one that only a corpus with more headroom could settle.

## The MRL encoder on the same fixture

The same 800-fact index, embedded by `nomic-embed-text:latest` (768 native dims):

| Width | Bytes/vector | R@1 | R@5 | MRR |
|---|---|---|---|---|
| 768 | 3,072 | 0.175 | 0.325 | 0.246 |
| 256 | 1,024 | 0.100 | 0.325 | 0.186 |
| 128 | 512 | 0.150 | 0.375 | 0.234 |
| 64 | 256 | 0.075 | 0.150 | 0.108 |

Two things stand out. First, the absolute recall is far below the 384-dim encoder's, and the likely reason is in this run's setup rather than in the model: nomic-embed-text-v1.5 requires its task-instruction prefixes (`search_document:` at index time, `search_query:` at query time), and this run embedded raw text for both encoders to keep them symmetric. The vendor card is explicit that the prefix is mandatory, so these absolute values understate nomic considerably. Width comparisons *within* this model are still internally consistent, because every width saw the same unprefixed text.

Second, the MRL model's width curve here is not the clean monotone decay that "trained for truncation" might suggest: R@5 is flat at 768 and 256 (0.325), *higher* at 128 (0.375), then collapses at 64 (0.150). At 40 queries those first three cells differ by two queries or fewer, so the ordering among them is not resolvable. What is resolvable is the drop at 64 dims, which is large and consistent: the MRL property does not extend indefinitely, and where it stops depends on the model — 64 is past the useful point for this encoder on this fixture, while the non-MRL 384-dim encoder had already flattened by 128.

The practical point is not "which encoder is better". It is that the width you can safely cut to is an encoder-specific number you have to measure, and vendor MRL claims are a reason to test, not a substitute for testing.

## The decision rule

Three options, in the order I would try them. If you have not yet established that vector width is the constraint, start from the [agent-memory architecture guide](/posts/agent-memory-architecture-guide-2026/) or the [framework comparison](/posts/best-ai-agent-memory-frameworks-2026/); the rest of this section assumes that decision is made and only sizes the vector.

**Cut width only if the index is small or the recall budget is loose.** If your store holds tens of facts per subject and your questions are cluster-level (any paraphrase is a correct answer), the measured cost was 1.7 points R@5 for a 3x payload cut, which is a reasonable trade. If your store holds hundreds of paraphrases per subject and your questions need one specific variant, the measured cost was 10 points R@5, and the byte saving will not pay for the retrieval failures it buys.

**Keep the full vector and index two widths if you need the storage win and the recall.** Because the short vector is `normalise(full[:d])`, you can store 384-dim vectors and additionally index 128-dim copies (or a coarse 64-dim pass) without a second embed call. Search the narrow index first for candidate generation, then rescore the candidates at full width. That buys the hot-path cost reduction without discarding the information, at the price of keeping both payloads — worth it when the narrow pass is what is hitting memory limits, not when the whole table is.

**Add reranking instead of shrinking, if the failure is ordering.** The 200-fact wobble and the flat 128/64 cells both suggest candidates often survive to a deeper rank. A cross-encoder rerank over the top-20 at full width addresses ordering; truncation addresses payload. They are not substitutes.

Whichever you pick, state the savings honestly. A 3x reduction in vector payload is not a 3x smaller database: HNSW or IVF graph overhead stays roughly constant per vector (how stores differ on that overhead is compared in [this store-level comparison](/posts/vector-database-comparison-2026/)), and quantization (int8 or binary) can reach a smaller payload *at full width* without the truncation question at all. This experiment measured neither, so it cannot tell you which is the better byte.

## Reproduce it

Everything is derived from local files, no hosted API and no paid tooling:

- [fixture.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/fixture.json) — 800 facts (200 subjects × 4 paraphrases with codenames) and the 40 queries
- [run-2-presence-guaranteed-score.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/run-2-presence-guaranteed-score.py) — the scoring pass behind every table here
- [results-arctic-presence-guaranteed.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/results-arctic-presence-guaranteed.csv) — one row per (width, index size, seed, query)
- [semantics-check.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/semantics-check.json) — the `normalise(full[:d])` comparison, 8 probes
- [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/method.md) — exact commands, seeds and environment
- [results.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-embedding-dimensions-recall-curve-2026/results.csv) — the superseded first scoring pass, published unedited for audit (sha256 `d75a16cf3f1f4fd4a4dba7c915c79456b63c985a2921a961ee8527ccca1abf01`); it sampled random index subsets, so its small-store rows are automatic misses, and no number in this article comes from it

The environment block, so the scope is checkable: ollama 0.20.3, Linux aarch64, 2 vCPU, 11.0 GiB RAM, no GPU. `snowflake-arctic-embed:33m` digest e8db018629b498a0a1a2eadbe8ab29477c1d7c4b6ba8ff2a69b0a6ed193713be (67 MB, F16, BERT family, 384 native dims), `nomic-embed-text:latest` digest 0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f (768 native dims). Full-width embedding cost 0.035 s per text at p50 for the 33M model and 0.154 s per text for the 768-dim model, batches of 32 facts and 8 queries per call, model resident, single host, no repeats — indicative only, not a serving benchmark.

## Limits

- Fixture scale: 800 facts, 40 queries, index sizes up to 800. A controlled editorial experiment, not an MTEB-style benchmark or a vendor evaluation.
- Template-generated paraphrases are cleaner than real notes, so absolute recall is optimistic. Transfer the direction and relative size of the width effect, not the levels.
- One non-MRL 384-dim encoder across three index sizes, one MRL 768-dim encoder at the full index only, one host, CPU only. No GPU serving, hosted embedding APIs, quantization, reranking or ANN overhead was measured, and no storage or recall improvement is claimed for any hosted service.
- The `normalise(full[:d])` equivalence is version-scoped to ollama 0.20.3 as installed here. Re-check it on your version before relying on derivable short vectors.
- The task prefixes nomic requires were omitted for symmetry, which depresses that model's absolute numbers; its width comparison is unaffected.
- The first, confounded scoring pass is published unedited as `results.csv` in the evidence directory (last item under Reproduce, sha256 `d75a16cf…`) and is not the basis of any claim in this article.

The takeaway I would act on: measure the width curve on your own corpus before you cut, and expect the answer to depend on how many paraphrases compete in your store, not on a vendor's truncation-friendly training claim.
