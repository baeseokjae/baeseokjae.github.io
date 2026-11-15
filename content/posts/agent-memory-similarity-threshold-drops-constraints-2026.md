---
date: 2026-11-14 00:00:00+00:00
lastmod: 2026-11-14 00:00:00+00:00
description: On a 12-fact fixture with two local Ollama embedders, one of four constraint queries scored 0.660 under all-minilm, below a 0.7 cosine cutoff, while descriptive facts scored 0.764-0.773. The same constraints all clear 0.90 on snowflake-arctic-embed:33m. Method, sweep and a probe you can run.
draft: false
schema: schema-agent-memory-similarity-threshold-drops-constraints-2026
tags:
- agent-memory
- embeddings
- retrieval
- cosine-similarity
- ollama
- rag
- evaluation
title: 'Your Similarity Cutoff Deletes the Rules First: Constraint Facts Score Below Descriptions in Local Embedders (2026)'
---

Your memory pipeline ends with a score gate: keep rows at or above 0.7 cosine similarity, drop the rest. You tuned that number on topical questions and it looked fine. Then someone asks "May I deploy to production on Friday?" and the agent retrieves nothing — not the wrong thing, nothing — because the one stored sentence that should have stopped the deploy scored 0.660.

That is the measurement in this article, scoped to what was actually run. On a 12-fact synthetic fixture with two local Ollama embedders, the prohibition "Deployment to production on Fridays is prohibited for all teams." scored 0.660 against "May I deploy to production on Friday?" under `all-minilm:latest`. The two descriptive facts in the same fixture scored 0.764 and 0.773 for their own questions. A 0.7 gate therefore keeps the descriptions and deletes the rule, and the ordering reverses on the second embedder — the same prohibition scores 0.949 under `snowflake-arctic-embed:33m`. The safe cutoff is a property of the encoder, not of your application.

The fixture is small and this is not an effect size. It is enough to show the effect exists, that it is embedder-dependent, and to justify spending twenty minutes measuring it on your own facts before you trust a threshold you inherited.

## What was measured, and what was not

The fixture is 12 facts and 6 queries, committed in the probe script: 6 constraints (two prohibitions, two requirements — who may rotate production keys, and migrations inside the maintenance window — one exception to the deployment freeze requiring engineering-director approval, and one exclusion of contractors from incident command) and 6 descriptive facts over the same entities — backups, on-call rotation, keys, GPU cluster, deployment pipeline, incident reviews. Four of the six queries target a constraint; two target a description. Each query has exactly one gold fact.

Scoring is exact cosine over the full returned vectors, with no ANN index in the loop, so approximate-search recall loss cannot be mistaken for the cutoff effect. The threshold sweep runs 0.20 to 0.90 in 0.05 steps. Both embedders run locally through Ollama's `/api/embed` at 384 dimensions (`all-minilm:latest`, digest `1b226e2802db`; `snowflake-arctic-embed:33m`, digest `e8db0186`); the harness sends the whole fact list and the whole query list in two batched calls per model, and re-running reproduces every score to three decimals.

Not measured, and not claimed here: an effect size, generality across embedders or corpora, any product's default cutoff, or the behaviour of any hosted vector database's approximate index. This article also does not claim that constraint facts are *always* penalised. It reports the direction found on this fixture and the sweep that exposes it.

## Result 1: the constraint is the only row under the gate

Under `all-minilm:latest`, the six gold scores split in a way that matters:

```
query  gold  score   rank  best descriptive competitor
q1     c1    0.660   1     d2 0.304   (Friday deployment prohibition)
q2     c2    0.857   1     d3 0.705   (key rotation ownership)
q3     c3    0.900   1     d4 0.411   (PII in notebooks)
q4     c5    0.821   1     d1 0.251   (long migration window)
q5     d1    0.764   1     —          (backups: where and when)
q6     d2    0.773   1     —          (on-call rotation)
```

Both descriptive gold scores (0.764, 0.773) sit above the constraint score for q1 (0.660). The gold fact is ranked first for all six queries, so this is not a ranking problem — it is a *magnitude* problem. Cosine similarity for "May I deploy on Friday?" against the rule that forbids it is lower than cosine similarity for "When do backups run?" against the sentence describing backups. Gate at 0.7 and q1 returns zero rows: the gold is 0.660, the next-best fact overall is another constraint (c4) at 0.338, and the best descriptive competitor is 0.304.

Under `snowflake-arctic-embed:33m` the same texts order the other way: constraints score 0.942 to 0.980, descriptions 0.897 to 0.923. The Friday prohibition scores 0.949. Every constraint gold clears 0.90; the descriptive q5 gold at 0.897 is the one row that falls below that gate.

## Result 2: the sweep shows where recall breaks, and it breaks differently per embedder

Constraint recall is the fraction of constraint-targeted queries whose gold fact survives the gate. At 0.70 under `all-minilm:latest` it is 0.75 — three of four — and overall recall is 0.833.

```
threshold   all-minilm constraint recall   snowflake-arctic-embed constraint recall
0.20-0.65   1.00                            1.00
0.70        0.75                            1.00
0.75        0.75                            1.00
0.80        0.75                            1.00
0.85        0.50                            1.00
0.90        0.25                            1.00
```

Nothing changes between 0.20 and 0.65 on either model. The first loss under all-minilm is exactly the q1 score of 0.660 crossing a 0.70 gate; the second loss at 0.85 is q4 at 0.821, and at 0.90 only q3 at 0.900 remains. Under snowflake the constraint set is intact to 0.90; at that threshold the *description* q5 at 0.897 is what falls out, which is the mirror image of the all-minilm failure.

Two operational consequences follow. First, on these fixtures a cutoff up to 0.65 is safe for both embedders, and the failure is not "thresholds are bad" but "this threshold was never validated against the fact type that matters". Second, a cutoff copied from a notebook tuned on another encoder is a different number in practice: the same 0.7 that costs one of four constraints under all-minilm costs nothing under snowflake.

## Result 3: the failure mode here is an empty retrieval

The planning assumption for this article was that a descriptive fact would outrank the rule and get returned in its place. That is not what happened. Across all 15 thresholds on both embedders, the count of queries where the gold constraint was dropped *while a descriptive fact survived above the same gate* was zero. On q1 the next-best descriptive fact scored 0.304; the next-best fact overall was c4, another constraint, at 0.338.

That distinction changes the symptom but not the risk. A wrong-but-plausible description at least gives the model something to reason about, and a careful agent may notice the mismatch. Zero rows gives it nothing, and the failure is silent: the prompt simply contains no memory, and the model answers from its prior. Which of these two you get depends on how densely your store covers the query's topic. If your facts are thick around deployment, you will get substitution; if they are sparse, as here, you get emptiness. Both are the same gate deleting the same row.

## Why raising top-k or adding MMR does not fix it

`top_k` is applied to the candidates that already passed the score filter. Raising it from 5 to 50 changes how many survivors you keep; it cannot restore a row that was removed before ranking. The same applies to MMR or any diversity reranker placed after the filter, and to hybrid search weighted by a vector score that still has to clear the threshold.

The failure sits upstream of every ranking control you have. Either the row clears the gate or it does not, so the only levers that work are (a) lowering the gate, with the precision cost that implies for topical queries, (b) making constraint rows score higher for constraint-shaped questions, or (c) taking constraint rows out of the similarity gate entirely.

There is a secondary trap worth naming: cosine similarity is not one portable number. Qdrant's collections documentation states that cosine similarity is implemented as a dot product over vectors normalised at upload, so the value you see is only comparable inside a store that documents that normalisation; Chroma's collection configuration documents that `space` "defines the distance function of the embedding space" and that its default is squared L2, with cosine and inner product as opt-in alternatives. A 0.7 cutoff moved from a cosine collection to an L2 collection is not the same filter, and a similarity of 0.7 is not a distance of 0.7. Check the metric before you compare scores across stores, and never compare a similarity against a distance threshold.

## Measure your own sweep before you pick a number

The probe behind this article is a single file with the fixture inline: `threshold_probe.py`. It needs a local Ollama and nothing else — no API key, no network beyond `127.0.0.1`, no vector database. Replace the `FACTS` and `QUERIES` lists with your own rows and mark each fact `constraint` or `description`, then run it against whichever model you serve:

```
python3 threshold_probe.py > probe_results.json
```

It prints, per embedder, the gold score and rank for every query, the best-scoring descriptive competitor, and constraint recall at each threshold in the sweep. Three numbers are worth reading before you set a gate:

1. **The lowest constraint gold score.** Any cutoff above it deletes a rule.
2. **Constraint recall at your current threshold.** Below 1.0 means a rule-bearing question already returns nothing.
3. **The gap between your descriptive floor and your constraint floor.** If the constraint floor is lower, a gate tuned on descriptions is mis-tuned for rules by construction.

A 6-fact fixture is enough to find your own q1; the run takes seconds. Two caveats about the artifact: it is a fixture-in-code script rather than a library with a CLI, and the two model tags are hard-coded in `EMBEDDERS`, so you edit those lines to match what your host serves. The published methodology records the host, the model tags, the dimensions and the exact command.

## What to do instead

**Store polarity as a field, not as a sentence.** If a memory row carries `kind: constraint` with a scope ("production", "all teams", "Fridays"), you can retrieve constraints for a query that asks permission with a metadata filter and skip the similarity gate for that subset. This is the fix that survives an encoder swap, because it does not depend on how a particular model scores a modal verb.

**Route constraint facts around the gate.** Take the top-k by score, then union in all constraint rows that match the query's entities, then rank. The gate's job — removing noise — is preserved for the open-ended recall path where it was tuned.

**Pin the cutoff per embedder, after measuring.** If you keep a single numeric gate, derive it from the sweep rather than from a tutorial, and re-derive it when the encoder or its version changes. On this fixture the defensible statement is that a gate at or below 0.65 lost nothing under either embedder; every number above that is a claim requiring its own measurement. Scores are encoder-specific and, as the version pin in any model card suggests, encoder-version-specific too — the same reasoning as swapping encoders on an existing store, where the vectors, not just the cutoff, change meaning.

**Do not delete the gate to solve this.** Without it, a top-k over a large store returns weak matches for every query and the prompt fills with noise. The finding is that one number cannot serve both fact types, not that filtering is wrong.

## Limitations and what would falsify this

The fixture is 12 facts and 6 queries with four constraint queries, on one host, on one day, with two local 384-dimension embedders. Four of six queries target constraints, so the constraint median is not a population estimate. The article reports this run's numbers only; an earlier 8-fact planning probe reported a different descriptive-survivor pattern, and that pattern is not what this fixture produced, so it is not repeated here as a finding. ANN-index behaviour is out of scope by design: exact cosine was used precisely so that approximation error could not be confused with the cutoff.

Three results would overturn the practical recommendation. If constraint recall tracks descriptive recall across the whole sweep on both embedders for your corpus, then your gate is fine and only the numbers in this article are fixture-specific. If the constraint-versus-description gap closes once facts are embedded as multi-sentence documents rather than single sentences, then the effect is a property of short-fact embedding and should be stated that way. If a reranker placed before the filter recovers the dropped constraint without a score change, then the fix is architectural rather than metadata. Each of these is testable with the same probe and a different fixture.

What is already established by the run: a 0.7 cosine gate deleted one of four rules on this fixture under one embedder and none under another, the deletion was an empty retrieval rather than a wrong answer, and raising `top_k` cannot undo it. That is a narrow claim, and it is enough to justify checking your own cutoff against your own constraint facts before the next permission question arrives.

Method, fixture hash, per-query scores and the raw sweep are in the [probe results](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-similarity-threshold-drops-constraints-2026/probe_results.json), the [probe script](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-similarity-threshold-drops-constraints-2026/threshold_probe.py) and the [method notes](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-similarity-threshold-drops-constraints-2026/method.md), with file hashes in the [manifest](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-similarity-threshold-drops-constraints-2026/raw-records-manifest.json). These are first-party files created for this article, containing no customer data and no third-party downloads.

For where this sits in the wider picture, see the [agent memory framework comparison](/posts/agent-memory-comparison-2026/) for retrieval-quality metrics, the [mem0 configuration guide](/posts/mem0-agent-memory-guide-2026/) where a similarity threshold appears as a setting without a measured cost, [what changes when you swap encoders](/posts/agent-memory-embedding-swap-recall-2026/), [the other silent embedder failure at the context ceiling](/posts/local-embedding-context-ceiling-2026/), and [what deletion actually removes](/posts/agent-memory-delete-semantics-test-2026/) if you decide to prune rule rows rather than retrieve them.

Primary sources for the store-level claims: Qdrant's [collections documentation](https://qdrant.tech/documentation/concepts/collections/) on cosine-as-normalised-dot-product, Chroma's [collection configuration docs](https://docs.trychroma.com/docs/collections/configure) on the `space` parameter and its squared-L2 default, and the Ollama model pages for [all-minilm](https://ollama.com/library/all-minilm) and [snowflake-arctic-embed](https://ollama.com/library/snowflake-arctic-embed) for the model families used here.
