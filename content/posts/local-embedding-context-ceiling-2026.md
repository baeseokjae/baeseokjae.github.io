---
title: "Your Embedding Server Stops at 2,048 Tokens: Measuring the Local Embedding Context Ceiling That Silently Empties Agent Memory (2026)"
date: 2026-11-01T00:16:00+00:00
lastmod: 2026-11-01T00:16:00+00:00
description: "Ollama 0.20.3 served an embedding model whose Modelfile asked for 8,192 tokens and allocated 2,048. Here is how to measure the real ceiling, prove which chunks were clipped, and size a chunker against the number the server actually uses."
draft: false
tags:
  - local embedding context ceiling
  - ollama embed context length
  - nomic-embed-text 2048 tokens
  - prompt_eval_count embeddings
  - agent memory ingestion
  - silent truncation embeddings
  - chunk size token budget
  - ollama truncate parameter
  - local rag pipeline
  - embedding context window
schema: "schema-local-embedding-context-ceiling-2026"
---

If your agent's memory is written through a local embedding endpoint, the context window that decides what gets remembered is not the one printed on the model card. On the machine used for this article, Ollama 0.20.3 allocated 2,048 prompt tokens to `nomic-embed-text:latest` while the installed model's own parameters said `num_ctx 8192`, and it accepted a 64,599-character document with HTTP 200 by silently evaluating only the first 2,048 tokens. The number that governs your ingest never appears in the embedding call, the client library, or the config file you wrote. It appears in `ollama ps`.

That is the whole finding, and it is narrower than it sounds. If you are comparing advertised context on hosted APIs, [that comparison already exists](https://baeseokjae.github.io/posts/llm-context-window-comparison-2026/) and this article will not repeat it. This one measures the endpoint under your own ingest loop: what it allocates, when it clips without complaint, and how to prove after the fact which of your chunks were shortened before they ever became vectors.

## The symptom: memory that only remembers page one

A local memory pipeline looks healthy while it fails. The chat model and the embedder run on the same box, the ingest job walks a document directory, chunks the text, posts each chunk to `/api/embed`, and writes the returned vector to a store. Short notes — preferences, a name, a one-line decision — come back perfectly. Long documents do not. Ask about something from page six of a design doc and the agent answers from page one, or says it does not know.

Every layer you inspect looks fine. The chunker split the document. The HTTP calls returned 200. The index has a row for every chunk. The store answers queries in milliseconds. So the diagnosis drifts to the retriever, then to the embedding model's quality, then to prompt construction — three hypotheses that all cost real time and all miss the actual defect, which is that the vector for a long chunk was computed from its first two thousand tokens and nothing in the pipeline recorded that.

## Find the allocation, not the parameter

Two Ollama commands disagree about the same model, and the disagreement is the point. `ollama show` reports what the model's Modelfile asks for:

```
  Model
    architecture        nomic-bert
    parameters          137M
    context length      2048
    embedding length    768
    quantization        F16

  Parameters
    num_ctx    8192
```

`ollama ps` reports what the server actually reserved while the model was loaded, immediately after the probes below:

```
NAME                       ID              SIZE      PROCESSOR    CONTEXT    UNTIL
nomic-embed-text:latest    0a109f422b47    565 MB    100% CPU     2048       4 minutes from now
```

Both outputs are from the same host on 2026-11-01. The Modelfile asks for 8,192; the loaded runner serves 2,048. Ollama's own [context-length documentation](https://raw.githubusercontent.com/ollama/ollama/main/docs/context-length.mdx) describes memory-tiered defaults for chat models and tells you to check `ollama ps` rather than assume, but the tiers it lists are VRAM bands — under 24 GiB, 24 to 48 GiB, 48 GiB and above — and this host runs CPU-only, so those bands do not literally decide the value here. Treat 2,048 as an observation about this install, not a rule that other machines will match. The reason to check `ollama ps` instead of a config is that the allocation is a property of the running server, and any documentation you read — including this article — is second-hand to that.

If you are new to the endpoint itself, read the [Ollama API integration guide](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/) first; it covers the request and response shape, including `prompt_eval_count`, which is the field this whole measurement depends on.

## Measure the ceiling with prompt_eval_count

The `/api/embed` response tells you how many prompt tokens the server actually evaluated. That single integer turns "the input was too long" into an exact boundary, because a truncated call succeeds and reports the cap.

```bash
curl -s http://127.0.0.1:11434/api/embed \
  -d '{"model":"nomic-embed-text","input":"<long text>"}' | \
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("prompt_eval_count"), len(d["embeddings"][0]))'
```

Run that against inputs of growing length and read the number back. A token ladder of synthetic filler on this host produced the values below; the character counts are for that filler, not prose, so the ratio understates what real English costs.

| Words | Characters | prompt_eval_count | Chars per token |
| --- | --- | --- | --- |
| 50 | 377 | 58 | 6.50 |
| 100 | 755 | 114 | 6.62 |
| 200 | 1,511 | 226 | 6.69 |
| 400 | 3,023 | 450 | 6.72 |
| 1,200 | 9,071 | 1,346 | 6.74 |
| 3,400 | 25,703 | 2,048 | capped |

The last row is the ceiling announcing itself: a document that should have cost roughly 3,800 tokens reported 2,048. Two re-measurements on 2026-11-01 confirm it on much larger inputs — 22,799 characters returned 200 with `prompt_eval_count` 2,048 in 20.28 s, and 64,599 characters returned 200 with `prompt_eval_count` 2,048 in 17.21 s. The second call was faster than the first despite carrying nearly three times the text, because everything past the first 2,048 tokens was discarded before evaluation.

The binary search is trivial once you trust that field: send the same paragraph padded to increasing word counts, read `prompt_eval_count`, and stop when the reported count stops tracking the input. On this install the answer is exactly 2,048. It is worth saying what this does *not* establish: it is not a statement about nomic-embed-text's quality, about other Ollama releases, or about any other runtime. It is what one server on one CPU-only host allocated on one date.

## Why nothing errored

The endpoint can be made to fail loudly, and by default it does not. Ollama's [API reference](https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md) documents the parameter that decides this: `truncate` "truncates the end of each input to fit within context length. Returns error if `false` and context length is exceeded. Defaults to `true`."

Send the same oversized document with `"truncate": false` and the answer changes shape entirely:

```
HTTP/1.1 400 Bad Request
{"error":"the input length exceeds the context length"}
```

That request returned in 0.02 s. So the honest framing is not "the embedding server hides errors." The server has a loud mode, and the loud mode costs one extra JSON key. The default is quiet because truncating is a reasonable convenience for search snippets and an unreasonable one for memory ingest, and nothing in the request marks which of those you are doing.

This distinction matters for diagnosis. If your client sends `truncate: false` — it is a per-request field you control — you get an exception you can catch, log and retry. If it leaves the default alone, you get a vector, a 200, and a memory that quietly covers less than you think. Both pipelines index the same number of rows.

## What a clipped vector costs: the tail-sentinel test

Row counts cannot detect this failure, and neither can eyeballing similarity scores. The test that does detect it is per-chunk and cheap: put a unique phrase at the end of each source document, embed and store the document, then query the store with each document's own tail phrase and check whether that document comes back first. A pass means the tail survived tokenisation. A failure means the vector was built from a prefix.

On eight synthetic documents — four at 600 words, four at 3,000 words — the store ended with eight rows for eight documents, zero swallowed errors, and four rows whose `prompt_eval_count` had pinned at 2,048. Querying each document's own tail phrase returned the correct document in 3 of 8 cases. The number is not a recall rate and should not be quoted as one: the eight documents shared an identical filler body, so the vectors differed mainly by their tails, and the intact 600-word documents also produced misses that the truncation cannot explain. What the fixture demonstrates is the shape of the evidence — one query per chunk, a pass or fail per chunk, a coverage count you can put in a log line — not a ranking of anything. In a corpus of real, distinct documents the misses would concentrate on clipped chunks rather than spread across all of them, but that is an expectation, not a measurement.

Build the test into ingest rather than running it once. A sentinel at the tail of each chunk costs a few tokens and turns "recall feels bad" into "these 37 chunks out of 900 were stored without their endings."

## The row-count illusion

Here is the loop that produces silent loss, written the way it usually appears:

```python
for doc in documents:
    for chunk in split(doc.text, 1000):
        try:
            vec = embed(chunk)          # 200 OK, silently clipped
            index.add(chunk_id, vec)
        except Exception:
            log.warning("embed failed for %s", chunk_id)   # never fires
```

Every layer reports success. `index_rows == corpus_rows` holds exactly, because a clipped chunk is still a chunk. The warning branch is dead code under the default, which is why the log is empty and why the run looks clean. The only artefact that carries the truth is `prompt_eval_count` on each response, and most ingest loops discard the response body once the vector is extracted.

If you want to see the failure on your own box without a corpus, write a document that is deliberately longer than the ceiling, embed it, and compare the vector against the vector of its own first half. If the two are nearly identical, the tail did not enter the computation. That comparison is a stronger signal than any timing difference, and it needs no ground truth.

## Sizing chunks against the measured number

A fixed character chunker is the usual culprit, because characters are not the unit the endpoint enforces. On this install the filler text ran about 6.7 characters per token, so a 1,000-character chunk costs roughly 150 tokens and is safe, while a 20,000-character chunk costs about 3,000 and is not. Prose is denser than that filler, because real sentences produce more tokens per character than repeated ordinary words, so the same character count can cost noticeably more than this ratio predicts. Measure the ratio on your own text rather than importing one from a table.

The guard that prevents the failure has three parts, and none of them are elaborate:

1. Count tokens per chunk before sending, using the model's own tokenizer or a `prompt_eval_count` probe on the first batch, and record the number next to the chunk.
2. Fail the document, not the process, when a chunk exceeds the measured ceiling — do not clamp and continue. A partially indexed document is worse than a missing one, because it answers confidently from its opening pages.
3. Write the ceiling into the index metadata when the collection is created. When someone later upgrades the runtime or swaps the embedder, the stored number is the baseline to re-measure, and the mismatch is detectable without reading this article again.

Send `truncate: false` on the ingest path even after you have sized the chunks. It converts the silent case into a thrown error, which is the only behaviour a retry loop can act on. Keep the default on the query path if you like; a clipped search query degrades gracefully in a way a clipped document does not.

## Where this sits in the write path

This is a precondition failure, not a write-path defect in the usual sense. The [write-path reliability protocol](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/) asks whether a fact was recorded, superseded, contradicted or deleted; every one of those questions assumes the chunk reached the embedder intact. Here it did not: the write succeeded, the content did not. That is why the failure survives write-path testing and retrieval benchmarks alike — it happens before either can observe it.

It is also not a model-quality problem, which is the diagnosis [the local-models quality piece](https://baeseokjae.github.io/posts/local-llm-feels-dumber/) addresses. The embedder is doing exactly what it was configured to do. Its allocation is small, the input exceeded it, and the documented default clipped. Changing quantisation, sampling or the chat model will not move this number.

On the hardware side, the [local model selection guide](https://baeseokjae.github.io/posts/best-local-llm-models-2026/) is the right place to start when choosing what to run. Just remember that the context figure quoted for a chat model and the context the embedder is served with are separate allocations, read from separate lines of `ollama ps`.

## Limits and what to measure on your own box

Every number here is scoped to Ollama 0.20.3, `nomic-embed-text:latest` (`0a109f422b47`, F16, 137M parameters, 768 dimensions), CPU-only, on 2026-11-01. No second embedder was measured, so the 2,048 figure must not be generalised to other models or runtimes — other servers allocate differently and must be measured the same way. Elapsed times include shared-host CPU time and are indicative, not throughput benchmarks. The eight-document fixture was measured on 2026-10-31 and was not re-run on 2026-11-01; only the ceiling, the 400 body and the runtime allocation were re-measured on the later date.

Two vendor documents bracket the gap, and both were fetched on 2026-11-01. The model card states that nomic-embed-text-v1.5 has an 8,192-token sequence length and "natively supports scaling of the sequence length past 2048 tokens" via RoPE parameters, per the [model README](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5/raw/main/README.md). The same repository's [config.json](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5/raw/main/config.json) ships `max_position_embeddings: 2048` alongside `n_positions: 8192`. Those two files are the reason the brochure number and the config number disagree before any runtime is involved; the runtime adds a third number. Reading the card alone would have predicted 8,192 tokens of usable input on this box. The server used a quarter of that.

## How this was checked

The measurements above come from scripts that posted to the local `/api/embed` endpoint and parsed `prompt_eval_count`, plus the raw `ollama show` and `ollama ps` output captured on the same host. The scripts and raw JSON responses are an author-side working record kept with the article's research material; they are not published for download, so nothing in this article depends on you being able to fetch them. The commands in the sections above are the reproduction path: send padded text, read `prompt_eval_count`, send the same text with `truncate: false`, and check `ollama ps` while the model is loaded. If the last of those three prints a number larger than the second-to-last one reports, you have a different allocation than the one documented here, and the measurement — not this article — is the authority.
