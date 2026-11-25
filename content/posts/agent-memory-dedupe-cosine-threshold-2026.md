---
date: 2026-11-24 00:00:00+00:00
lastmod: 2026-11-24 00:00:00+00:00
description: On a 40-pair fixture embedded by three local Ollama encoders, a 0.95 cosine dedupe gate merged a production fact into its staging twin, and tightening the gate removed duplicate capture faster than it removed false merges.
draft: false
schema: schema-agent-memory-dedupe-cosine-threshold-2026
tags:
- agent-memory
- embeddings
- cosine-similarity
- deduplication
- ollama
- evaluation
title: A 0.95 Memory Dedupe Threshold Merged Production Into Staging
cover:
  image: /images/agent-memory-dedupe-cosine-threshold-2026-presentation.png
  alt: 'Range plot of cosine scores for 16 paraphrase and 16 one-token-change memory pairs on three local encoders. On every encoder the highest-scoring critical pair sits above the highest-scoring paraphrase, so a single threshold cannot separate duplicates from facts that must not be merged.'
  caption: 'Measured on 40 hand-written infrastructure memory pairs (16 paraphrase, 16 one-token critical, 8 control), 2026-11-10. Dashed lines mark 0.95 and 0.99. Values from sweep.csv and results.jsonl.'
  relative: false
  hidden: false
images:
- /images/agent-memory-dedupe-cosine-threshold-2026-presentation.png
---

Your agent memory layer writes a fact the same way a semantic cache writes an answer: embed the incoming record, compare it with what is already stored, and skip the insert if the cosine similarity clears a threshold. The number that circulates for that threshold is 0.92–0.95. [This site's own backend guide](https://baeseokjae.github.io/posts/ai-for-backend-developers-2026/) recommends exactly that band for semantic caching, with a code default of 0.93, and the advice transfers into memory layers by copy-paste because the code shape is identical.

The tolerance is not identical. A cache that returns the wrong cached answer costs one bad response; a dedupe gate that merges two different facts deletes one of them, and the agent will keep answering with the survivor. The measurement below is about that second failure: can a cosine threshold tell a duplicate memory from a memory that differs by one token, and does raising the threshold fix the merges it gets wrong?

## The short answer

On a 40-pair fixture embedded locally by three Ollama encoders, no threshold separated the two populations. The single most similar pair of the whole fixture was a *critical* pair on every encoder — two sentences that must not be merged — and it scored above the highest-scoring true paraphrase on the same encoder. At 0.95, `snowflake-arctic-embed:33m` merged 14 of 16 critical pairs and 6 of 16 paraphrases. Raising the gate to 0.99 on that encoder removed the last 6 duplicate merges and still merged 11 critical pairs. Tightening the threshold costs deduplication faster than it removes false merges, and a sweep from 0.80 to 0.999 never finds an operating point where both errors are acceptable.

That result is from 40 hand-written pairs — 80 single-sentence facts — on one host on 2026-11-10, with prompt-free embedding calls. It is a mechanism demonstration with exact counts, not an error rate for your store. The fixture, the runner and the raw per-pair scores are published with this article so you can run the same comparison against your own encoder before you trust a number.

## The gate, and where 0.92 came from

The pattern is three lines: embed, take the maximum cosine against existing memories, drop the write if the maximum is at or above tau. It exists because near-duplicate writes are real — an agent that extracts the same preference twice, or a summariser that rephrases a stored fact, will otherwise fill the top-k with copies of one sentence. Something has to collapse them.

The threshold is usually inherited from semantic caching practice, where this site's own guide publishes the 0.92–0.95 band, and that is a defensible choice for a cache, where a false hit produces one wrong answer a user can retry. A memory write is different in one specific way: the record that loses the merge is gone. There is no retry path from the agent's next answer, because the agent cannot distinguish "this fact was never stored" from "this fact is false".

This is also not the same question as the read-side cutoff. [A previous measurement on this site](https://baeseokjae.github.io/posts/agent-memory-similarity-threshold-drops-constraints-2026/) showed that a 0.7 retrieval cutoff can drop a stored constraint that scores low against its own question — the failure happens on the way out of the store. This article is about the way in: two facts that both belong in the store, one of which the gate refuses to insert. [The write-path protocol](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/) that defines record, update, contradiction and delete has no measured quantity for the merge decision; this is one attempt to supply it.

## What a memory layer stores, and what one token changes

The fixture is 16 paraphrase pairs (same fact, different wording — a gate should merge these), 16 critical pairs (identical sentence, one critical token changed — a gate must never merge these), and 8 controls (unrelated topics — a gate must never merge these). Every pair has a one-line provenance note in `pairs.json` saying why a real memory layer would hold both sentences. The categories were fixed before the first embedding call: port, TTL, region, retry count, retention, API version, primary-versus-replica, feature flag.

The critical pairs are the ordinary shape of infrastructure memory, not adversarial strings:

- `The checkout service uses port 5432 in production.` against `... in staging.` (C01)
- `The session cache TTL is 60 seconds.` against `... 600 seconds.` (C03)
- `Object storage buckets live in ap-southeast-2.` against `... ap-southeast-1.` (C06)
- `The payment client retries 3 times before failing.` against `... 5 times.` (C07)
- `The internal REST endpoint for orders is /api/v2/orders.` against `... /api/v1/orders.` (C11)
- `Analytics queries hit the read replica, not the primary.` against `Analytics queries hit the primary, not the read replica.` (C14)

A memory layer that loses C01 will tell a deploy check that staging's port is production's port. A layer that loses C14 will answer the read-routing question backwards while quoting a stored sentence that reads correctly. Neither merge raises an exception, and neither is visible in a recall benchmark run on a store that was cleaned before the benchmark started.

## The measurement

Three encoders ran through a local Ollama daemon's [`/api/embed`](https://docs.ollama.com/api/embed): [`all-minilm:latest`](https://ollama.com/library/all-minilm) (384 dimensions, 512-token context), [`snowflake-arctic-embed:33m`](https://ollama.com/library/snowflake-arctic-embed) (384 dimensions, 512-token context) and [`nomic-embed-text:latest`](https://ollama.com/library/nomic-embed-text) (768 dimensions, 2K-token context). Dimensions and context windows come from the registry pages and the model cards: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) documents a 384-dimensional output, the [arctic-embed family card](https://huggingface.co/Snowflake/snowflake-arctic-embed-xs) documents the 22m/384 size class that the registry's tag rail extends, and [`nomic-embed-text`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) documents 768 dimensions. All 80 texts per encoder went in one batch call; cosine was computed on the raw returned vectors with no normalisation, whitening or per-store calibration.

The run recorded Ollama 0.20.3 on 2 vCPU and 11.9 GiB of RAM, F16 weights, and a `prompt_eval_count` of 1120, 1120 and 1082. That field is the **per-request total across all 80 inputs**, not a per-input count: 1120 tokens for 80 sentences is about 14 tokens each, against 626 words across the 80 fixture texts and 12 words in the longest one. No single input came anywhere near the 512-token window of `all-minilm` or `snowflake-arctic-embed:33m`, so [`/api/embed`](https://docs.ollama.com/api/embed)'s default `truncate=true` had nothing to cut — the counts are the `embed_call` rows in `results.jsonl`. The three batch calls took 0.87 s, 2.59 s and 6.41 s of wall time for all 80 texts. The measurement date was 2026-11-10; the seven external pages cited here were re-fetched and re-read on 2026-11-24, and the numbers below are the 2026-11-10 run, not a re-run.

| Encoder | Paraphrase min / median / max | Critical min / median / max | Highest critical − lowest paraphrase | Control max |
|---|---|---|---|---|
| all-minilm:latest | 0.6466 / 0.8651 / 0.9240 | 0.6559 / 0.9528 / 0.9934 | −0.3468 | 0.2689 |
| snowflake-arctic-embed:33m | 0.8790 / 0.9376 / 0.9853 | 0.9315 / 0.9958 / 0.9979 | −0.1189 | 0.7150 |
| nomic-embed-text:latest | 0.6614 / 0.8336 / 0.9545 | 0.7594 / 0.9649 / 0.9918 | −0.3304 | 0.6128 |

A negative margin means the classes overlap: the lowest paraphrase on each encoder scores below the highest critical pair, and the critical distribution reaches further up than the paraphrase distribution does. A separating threshold needs the opposite ordering — every paraphrase above every critical pair, or at least a clean gap between them.

The single most similar pair in the fixture was critical on all three encoders, and on each encoder it outscored the best paraphrase:

| Encoder | Highest critical pair | Cosine | Highest paraphrase pair | Cosine |
|---|---|---|---|---|
| all-minilm:latest | C14 (replica/primary swap) | 0.9934 | P10 (backups retained vs kept) | 0.9240 |
| snowflake-arctic-embed:33m | C07 (retries 3 vs 5) | 0.9979 | P15 (flag enabled vs on) | 0.9853 |
| nomic-embed-text:latest | C06 (ap-southeast-2 vs -1) | 0.9918 | P15 (flag enabled vs on) | 0.9545 |

That ordering is the whole problem in one row. The pairs the gate most wants to merge are the ones it must not merge, because a one-token change barely moves the embedding: `production` and `staging` occupy the same slot in the same sentence, so the vectors differ mostly in that one direction. The specific identity of the top pair moves between encoders — the swap, the retry count, the region suffix — so the correct statement is per encoder, not a universal maximum.

At the commonly recommended 0.95, on this fixture:

- `all-minilm:latest` merged 8 of 16 critical pairs and 0 of 16 paraphrases.
- `snowflake-arctic-embed:33m` merged 14 of 16 critical pairs and 6 of 16 paraphrases — including C01, production versus staging, at 0.9572.
- `nomic-embed-text:latest` merged 9 of 16 critical pairs and 2 of 16 paraphrases.

No control pair merged at any threshold from 0.80 to 0.999 on any encoder. The gate is not indiscriminate; it is specifically blind to the differences that infrastructure memory is made of.

## Raising the threshold fixes the wrong side

The sweep tested 41 thresholds from 0.80 to 0.995 in 0.005 steps, plus 0.999, recording duplicate capture (paraphrases at or above tau, of 16), false merges (critical pairs at or above tau, of 16), controls merged (of 8) and F1. Six rows per encoder are reproduced here; the full matrix is in `sweep.csv`.

| tau | all-minilm dup / false / F1 | arctic-33m dup / false / F1 | nomic dup / false / F1 |
|---|---|---|---|
| 0.80 | 12 / 15 / 0.558 | 16 / 16 / 0.667 | 10 / 14 / 0.500 |
| 0.90 | 4 / 13 / 0.242 | 14 / 16 / 0.609 | 3 / 13 / 0.188 |
| 0.92 | 2 / 10 / 0.143 | 12 / 16 / 0.545 | 2 / 13 / 0.129 |
| 0.95 | 0 / 8 / 0.000 | 6 / 14 / 0.333 | 2 / 9 / 0.148 |
| 0.97 | 0 / 5 / 0.000 | 2 / 12 / 0.133 | 0 / 7 / 0.000 |
| 0.99 | 0 / 1 / 0.000 | 0 / 11 / 0.000 | 0 / 1 / 0.000 |

Two things follow directly from the table. First, the best F1 on every encoder is at 0.80, the lowest threshold tested — the sweep never finds a good operating point above it, and on two encoders the F1 at 0.80 is itself under 0.56 because the false merges are already 14 or 15 of 16. Second, the walk from 0.95 to 0.99 trades the wrong thing. On `snowflake-arctic-embed:33m`, raising the gate discards the last 6 duplicate captures and 3 of the 14 false merges; 11 false merges survive at 0.99. On the other two encoders the same walk removes 7 and 8 of the false merges, and both also give up their duplicate captures: `all-minilm` captures 0 duplicates at either threshold and still merges C14, the replica/primary swap, at 0.99; `nomic-embed-text` captures 2 duplicates at 0.95 and none at 0.99, where it still merges C06, the region suffix. So 0.99 on those two encoders collapses no duplicates while retaining one false merge each.

A reader who tuned 0.92 to 0.95 to 0.99 in that order would end up with no deduplication and, on one encoder, most of the dangerous merges intact. The threshold window where both error types are non-zero is 0.80–0.92 on all-minilm, 0.80–0.985 on arctic-33m and 0.80–0.95 on nomic; the useful range is the part of the sweep where the gate still does something.

## What it costs when a fact disappears

Pair scores are abstract. The store arm turns them into the reader's actual symptom. A 30-fact store (the `a` side of the 16 critical pairs plus the `a` side of 14 paraphrase pairs) receives 30 subsequent writes: 14 paraphrases, which are true duplicates, and 16 critical variants, which are distinct facts. Each write is compared with everything already stored and dropped when the maximum cosine is at or above tau.

| Gate | Encoder | Store size after | Duplicates collapsed (of 14) | Distinct facts lost (of 16) |
|---|---|---|---|---|
| none | any | 60 | 0 | 0 |
| 0.95 | all-minilm:latest | 52 | 0 | 8 |
| 0.95 | snowflake-arctic-embed:33m | 42 | 4 | 14 |
| 0.95 | nomic-embed-text:latest | 51 | 0 | 9 |
| 0.99 | all-minilm:latest | 59 | 0 | 1 |
| 0.99 | snowflake-arctic-embed:33m | 49 | 0 | 11 |
| 0.99 | nomic-embed-text:latest | 59 | 0 | 1 |

On `snowflake-arctic-embed:33m` at 0.95 the gate collapses 4 duplicates and suppresses 14 distinct facts: the store grows by 12 rows where an ungated store grows by 30, and most of what is missing is not duplication. At 0.99 the same encoder still loses 11 distinct facts and collapses nothing. The two encoders that look tolerable at 0.99 are tolerable because they collapse no duplicates at all there: their stores keep 59 of the 60 rows, which is the ungated store minus one false merge, carrying the gate's latency for no deduplication.

The symptom in production is not a failed write. It is an agent that answers with the value from whichever variant it stored first, confidently, and cannot be corrected by re-asking, because the second fact was never inserted. This is the same class of loss as [a write that never becomes visible inside the read window](https://baeseokjae.github.io/posts/agent-memory-write-visibility-window-2026/), and the opposite of [a fact that must be deleted](https://baeseokjae.github.io/posts/agent-memory-delete-semantics-test-2026/): here the deletion is a side effect of an insert elsewhere.

The store arm is one store, one write order, 30 scripted writes drawn from the same 40 pairs. Write order and store size change which facts collide, so read its counts as an exact demonstration of the failure mode, not as an expected loss rate.

## A guard that helps, and where it fails

Cosine alone leaves no usable operating point, so the obvious next step is a second, cheaper check. The guard tested here merges only when the cosine clears tau *and* the critical-token multiset is identical on both texts, where a critical token is a number, an `/api/vN` path segment, a region code of the form `xx-name-N`, an environment word (production/prod, staging/stage, development/dev, normalised), `primary`/`replica`, `enabled`/`disabled`, or `port`.

| tau | Encoder | False merges without guard | False merges with guard | Duplicate capture without / with guard |
|---|---|---|---|---|
| 0.95 | all-minilm:latest | 8 | 1 | 0 / 0 |
| 0.95 | snowflake-arctic-embed:33m | 14 | 1 | 6 / 4 |
| 0.95 | nomic-embed-text:latest | 9 | 1 | 2 / 0 |
| 0.99 | all-minilm:latest | 1 | 1 | 0 / 0 |
| 0.99 | snowflake-arctic-embed:33m | 11 | 1 | 0 / 0 |
| 0.99 | nomic-embed-text:latest | 1 | 0 | 0 / 0 |

The guard does most of what it promises at 0.95: it blocks 7 of 8, 13 of 14 and 8 of 9 false merges. It does not do the rest, and both of its failure modes are instructive.

The first failure is C14, the replica/primary swap. `Analytics queries hit the read replica, not the primary.` and `Analytics queries hit the primary, not the read replica.` carry the same multiset `{primary, replica}`, so the order-blind comparison passes and the merge goes through on all three encoders. Catching a swap needs position or a relation — which token is the subject of which verb — not a bag of tokens.

The second failure is the other direction: the guard blocks true duplicates whose rephrasing changes the token inventory. `The billing API binds to port 8443.` against `Billing API listens on 8443.` drops the word `port`; `Object storage buckets live in ap-southeast-2.` against `S3 buckets are provisioned in ap-southeast-2.` adds a bare digit token from `S3`; `checkout_new_ui flag is enabled in production.` against `The checkout_new_ui feature flag is on in production.` replaces `enabled` with `on`. All four such paraphrases (P02, P06, P15, P16) are rejected on every encoder, which is why guard duplicate capture falls to 0–4 of 16 rather than staying at the raw 0–6.

At 0.99 the combination is safe and useless: one false merge remains on two encoders (C14 again), and no duplicate is collapsed on any encoder. At 0.95 it removes most false merges but also blocks four true duplicates, so it is not a drop-in replacement for the gate either. Published alone, either version would be a prescription tested only on the cases where it works, so both are here.

## What to do in your own store this week

1. **Measure separability before you pick a number.** The 40 pairs, the stdlib-only runner and the sweep are published below. Swapping the fixture for 40 of your own facts and re-running against your encoder takes minutes and answers the question for your store, which is the only store where the answer matters.
2. **Fail open.** When the score is in the ambiguous band, insert. A duplicate costs a slot in the top-k; a false merge costs a fact. If you must choose an error, choose the recoverable one.
3. **Treat numbers, regions, versions, ports, environments and flag polarity as merge blockers, not merge signals.** They are exactly the tokens that barely move a cosine score, and they are exactly the tokens whose loss changes an answer.
4. **Record the write you skipped, with its score and the row it matched.** A merge decision you cannot audit cannot be corrected, and the wrong merges above are invisible in aggregate metrics.
5. **Set `truncate: false`** on [`/api/embed`](https://docs.ollama.com/api/embed) if you store long memories. With the default, an input longer than the context window is silently cut before it is compared, so the vector that gets gated is not the vector of the sentence you stored. Nothing in this run hit that limit; it is a documented behaviour of the endpoint, not a result here.
6. **Do not read this as encoder selection.** Encoders differ in margin and in which pair scores highest, and the same family of gate failure appeared on all three. [A recall comparison after an encoder swap](https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/) is the query-time version of this problem; the write-time version does not have a winner among these three.

## What this does not show

- 40 hand-written pairs (80 single-sentence facts) in infrastructure vocabulary, authored before any embedding call, on one host, in one run on 2026-11-10. Not a sample from a real agent transcript, and not a rate for any deployment.
- Prompt-free `/api/embed` calls. [`nomic-embed-text-v1.5`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) documents mandatory task-instruction prefixes — including `clustering:` for "remove semantic duplicates" — and the arctic family documents a query prefix for queries. None was used, so those columns describe the un-prefixed call shape only, not those models' best case.
- Cosine on raw vectors, no normalisation or per-store calibration. A rescaled space may order pairs differently.
- The store arm reuses the pair fixture with one write order; it is a mechanism demonstration, not a recall benchmark.
- One guard implementation, with a position-blind token comparison as its demonstrated defect. Relational, slot-based or schema-aware guards were not tested.
- No claim about how Mem0, Zep, Graphiti or any product implements deduplication — no vendor source was read for this run. The subject is cosine gating as a technique. For where deduplication sits in a broader architecture, see [the three-layer memory model](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) and [the framework comparison](https://baeseokjae.github.io/posts/best-ai-agent-memory-frameworks-2026/), both of which list entity deduplication as a product strength without quantifying false merges; this article measures the primitive underneath that claim.
- No search-volume, prevalence or "most teams" claim. No recommended threshold is published here; the finding is that this fixture has no good operating point.

## Evidence and reproduction

The measurement is original first-party work, dated 2026-11-10, and has not been re-run. Every result file below is the byte-for-byte output of that run, hashed in `CHECKSUMS.txt` and in this article's review record, and published under `research/evidence/agent-memory-dedupe-cosine-threshold-2026/` in the site repository. The single exception is `run.sh`: it gained one `mkdir -p "$OUT"` line on 2026-11-24 so that the documented command stops dying on a missing `./evidence` directory. Its current hash is the one in `CHECKSUMS.txt`, and no measured file changed.

- [`run_experiment.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/run_experiment.py) — stdlib-only runner: batch embedding calls, cosine, the 41-point sweep, the store arm and the token guard.
- [`run.sh`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/run.sh) — captures `ollama --version`, `nproc`, `free -m` and `ollama show` for each model, then runs the experiment; it creates the output directory (the only file here changed after the run).
- [`pairs.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/pairs.json) — the 40 pairs with class and provenance note; the file to replace with your own facts.
- [`results.jsonl`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/results.jsonl) — per-call records (model, dimension, wall seconds, `prompt_eval_count`) and all 120 per-pair cosines with the guard verdict.
- [`sweep.csv`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/sweep.csv) — 41 thresholds × 3 encoders: duplicate capture, false merge, controls merged, precision, recall, F1.
- [`summary.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/summary.json) — derived class ranges, separation margins, best operating point, store arm and guard arm.
- [`METHOD.md`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/METHOD.md) — fixture design, runner behaviour, environment actually used, and the design deviations.
- [`environment.txt`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/environment.txt) — the captured host and model snapshot.
- [`CHECKSUMS.txt`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-dedupe-cosine-threshold-2026/CHECKSUMS.txt) — the SHA256 of every artifact, written at collection time and updated once, on 2026-11-24, for the `run.sh` line; every measured digest is the original.

To reproduce: pull the three tags into a local Ollama, then run `./run.sh` from that directory — it creates `./evidence`, or writes into the directory you pass as its argument; no network and no API key are involved. If you change the pairs, change them before the first embedding call and record why each pair belongs in a memory layer — the fixture's value is that its categories were fixed before any score was seen.
