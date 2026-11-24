---
title: "Agent Memory Provenance: can you tell a tool-fetched fact from a user's?"
date: 2026-11-08T22:18:00+00:00
lastmod: 2026-11-24T12:13:20+00:00
description: "Two memory records, one from the user and one from a fetched page, arrive as the same string. Read at pinned mem0 and Graphiti commits, then measured on a 12-record fixture: the tool-sourced share of recall, the token cost of provenance fields, and whether purge-by-source is provable on every surface the store exposes."
draft: false
tags:
  - agent memory provenance
  - tool-sourced memory
  - prompt injection memory
  - memory trust tier
  - purge by source
  - mem0 memory schema
  - graphiti episodic node
  - memory audit read back
  - agent memory reliability
  - llm agent security
schema: "schema-agent-memory-provenance-tool-source-test-2026"
cover:
  image: /images/agent-memory-provenance-tool-source-test-2026-presentation.png
  alt: 'Diagram of one measured fixture, three write policies. P1 verbatim recalls 25 of 25 slots but cannot attribute any of them because the store has no source column, at 69.0 whitespace tokens per assembled block. P2 provenance-tagged recalls the same 25 slots and labels 11 of them as tool-sourced, at 76.2 tokens. P3 adds a trust tier and quotes untrusted records as evidence, also labelling 11 of 25, at 101.6 tokens. A lower strip shows the purge-by-source read-back: recall 0 of the 4 purged records, live table 0 rows, audit log still returning 4 texts until the audit rows themselves are purged. Conceptual diagram of fixture output, not a vendor benchmark.'
  caption: 'One fixture, three write policies: attribution and token cost, plus the surfaces a purge must cover · measured 2026-11-08'
---

An agent writes to long-term memory from two channels: what the user said, and what a tool returned. A ticket comment, a PDF, a fetched runbook page and the user's own sentence all arrive as strings, and the extraction step turns each into a fact. The store usually keeps the fact. Most schemas do not keep the channel.

That produces a question an operator cannot answer from the store: of the memories assembled into this prompt, which ones came from outside the trust boundary? And its operational twin: when the page turns out to be wrong, can I purge everything that came from that URL and prove the purge worked?

This article reads what two widely used stores actually record at pinned commits, then measures the question on a twelve-record fixture you can re-run. The fixture is the evidence. The vendor reading is three files: two from mem0 — the `MemoryItem` record type and the recall filter builder — and Graphiti's node module. No vendor behaviour is claimed as measured.

## What the schemas record at the pinned commits

mem0's public memory record at commit `f1791da` is `MemoryItem` in [`mem0/configs/base.py`](https://raw.githubusercontent.com/mem0ai/mem0/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/configs/base.py). It carries `id`, the extracted `memory` text, a `hash`, a free-form `metadata` dict, a `score` and `created_at`/`updated_at`. There is no field for the channel a fact arrived through, no source URI, and no trust tier.

Scoping is the same story. `_build_filters_and_metadata` in [`mem0/memory/main.py`](https://raw.githubusercontent.com/mem0ai/mem0/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/memory/main.py) constructs the recall filter from `user_id`, `agent_id`, `run_id` and an optional `actor_id`, and raises when none is supplied. Those are tenancy and actor identifiers. A recall filter built from them cannot express "only records whose source was the user" as distinct from "records a tool fetched". The metadata dict is free-form, so a caller can store a source key by convention — but that is a convention the record type does not guarantee and the default filter does not use.

Graphiti is the interesting contrast. `EpisodicNode` in [`graphiti_core/nodes.py`](https://raw.githubusercontent.com/getzep/graphiti/024b83679e48e41d59a7d1714ac0870aff2e4676/graphiti_core/nodes.py) declares `source: EpisodeType`, `source_description: str` and `content: str`. A channel label exists and is required. `EpisodeType` is a format enum with four members at `nodes.py:74-77` — `message`, `json`, `text` and `fact_triple` — so it distinguishes how the text arrived, not whether to trust it, and `source_description` is free text rather than a URI. That label sits on the episodic type (`nodes.py:318`), which is a distinct class from the `EntityNode` at `nodes.py:499` with its `summary` and `name_embedding` fields; I did not read the search path, so this article does not state what recall returns, nor whether it filters on episode source.

So the pinned schemas give three different starting points: no channel field at all, a channel field that is not a trust field, and a free-form metadata escape hatch. None of them is a source-authority field you can filter on.

## The fixture: one store, three write policies

The fixture is twelve records in stdlib SQLite. Eight are user-stated facts about a fictional deployment process. Four come from one simulated tool result — a fetched runbook page — and deliberately include a benign correction of a user fact, an invented approval constraint, an injected directive appended to a plausible sentence, and a duplicate of something the user already said. Five fixed queries run against the store, top-5 retrieved by cosine similarity over local embeddings, and the recalled block is what the agent would see.

Three policies write the same twelve records:

- **P1, verbatim.** `memory(id, text, vec)`. The schema a store has when provenance was not designed in.
- **P2, provenance-tagged.** Adds `source_type`, `source_uri`, `session_id` and `written_at` at write time, and labels each recalled record in the assembled prompt.
- **P3, provenance plus trust tier.** P2 plus a `trust_tier` column, with untrusted records admitted to the prompt only as quoted evidence, and purge-by-source as a supported operation.

The ranking is identical across all three, which is the first result and the point of the exercise. Provenance changes what the prompt can say about a record, not which records come back. All three policies recall the same 25 records across the five queries, and by the fixture's own ground truth 11 of those 25 — 44% — originated in the tool channel.

What differs is what the assembled prompt can tell the reader:

| Policy | Channel visible at read time | Tool-sourced records attributable | Mean whitespace tokens per block |
|---|---|---|---|
| P1 verbatim | no | 0 of 25 | 69.0 |
| P2 provenance-tagged | yes, labelled per record | 11 of 25 | 76.2 |
| P3 provenance + trust tier | yes, quoted and labelled | 11 of 25 | 101.6 |

Under P1 the tool-sourced records are indistinguishable from the user's own statements, and not merely unlabelled: the store has no column that would answer the question, so the count is zero because the measurement is impossible, not because nothing was retrieved. Under P2 the same prompt names the source of every recalled record, at a cost of 7.2 whitespace tokens per block over P1 — about 10%. Under P3 the quoting and trust labels cost 32.6 tokens per block, roughly 47% over P1; that is the price of making an untrusted record look like evidence rather than instruction, and it is paid on every turn the memory block is assembled.

On the query "where are staging deploy announcements posted", P1's top-5 is the injected record at rank 1, a user fact at rank 2, the invented approval constraint at rank 3, and the correction at rank 5. Three of the five records handed to the model came from the tool channel, and in P1's assembled block they read exactly like the two the user actually said.

## Why delete-by-id is not delete-by-source

The purge test is where the three policies stop being cosmetic. The operation an operator needs when a source is wrong is "remove everything written from this URI", and the fixture asks each policy to perform it and then reads every surface the store exposes.

Under P1 the operation is not expressible as a query. There is no source column, so there is no predicate to select on. What the probe does instead: it starts from the four tool texts it already knows, and resolves them to memory ids through the store's own `audit` table — `SELECT memory_id FROM audit WHERE text IN (…)`. So the store does supply the text-to-id lookup. What it cannot supply is the source knowledge: which of those texts arrived from that URI. That part is external bookkeeping, and P1 has no field to hold it. Given that mapping, the four records are removed, recall over the same five queries returns none of them, and the live table returns zero rows.

Under P2 and P3 the same purge is one predicate, `source_uri = <url>`, and it selects the same four records. Recall afterwards returns none of them and the live table returns zero rows.

Then the read-back catches all three policies. The append-only `audit` table — the store's own write log, present in the fixture's P1 schema too — still returns all four texts after the purge. A purge scoped to the memory table removes a fact from recall and leaves its text readable in the log that recorded the write. Only when the purge is extended to the audit rows does the count reach zero. That is the same shape as the mem0 history finding: success on the primary surface, text intact on the audit surface.

The honest formulation is therefore narrower than "purge by source works in P3". What P3 buys is a source-scoped predicate that makes purge-by-source *expressible and checkable*; whether the result is readable on every surface still depends on defining the purge over every surface, audit log included. A store that offers purge-by-source without a purge-by-source audit path has moved the leak, not closed it.

## One small-model observation

The optional model arm used the P1 block for the query above, with the injected directive at rank 1 among the recalled notes, as the only context for a local `qwen2.5:0.5b` generation asking for a two-sentence summary of the deployment rules. In three runs of the same prompt the output contained the injected phrase all three times, including the first line of the reply.

Read that narrowly. It is one 0.5-billion-parameter model, one prompt, three runs. It is not an attack-success rate, it says nothing about larger models or about any store, and the result is partly a property of the task as posed: the directive sat in the context with the same standing as the deployment facts, so a model that summarises its context repeated it. The measurement supports one operational sentence — a directive that reaches the prompt unquoted is content the model may treat as instruction — and nothing beyond it.

## What a schema can prove, and what it cannot

Three things follow from the fixture, and each has a boundary.

First, provenance is a write-time decision with a read-time payoff. Nothing reconstructs a channel after the fact: P1's store cannot answer the question even though the fixture knows the answer. Adding the columns later leaves every existing record unattributed, so the question is what your store does with the records written before you cared.

Second, provenance does not change retrieval. All three policies recalled the same 25 records, so buying a provenance field does not buy better recall and should not be justified as a retrieval improvement. It buys the ability to label the recalled block and to select records for deletion by where they came from.

Third, purge-by-source is a claim about surfaces, not a method call. Recall, live rows and the audit log are three separate reads, and the fixture shows a purge that satisfies two of them while the third still returns the text. Anyone who reports "purged by source" should be able to name which surfaces they read back.

The limits are real. Twelve synthetic records and five fixed queries are not a benchmark, the embedding ranking is one local model's, and the whitespace token counts are a proxy for a BPE tokenizer, useful for the ratio between policies rather than as an absolute. mem0 and Graphiti were read at one commit each on 2026-11-08 and neither SDK was installed: every statement about them is about what the pinned file declares, not about how a deployment behaves. Graphiti's recall-time filtering of episode source is unread and therefore unclaimed. Letta was dropped rather than described from memory because the source path guessed for it did not exist.

## Reproducing it

The fixture, probe and runner are published with the article, and the run record names the embedding model, the vector digest and the elapsed time so a re-run can be compared rather than trusted.

    research/evidence/agent-memory-provenance-tool-source-test-2026/
      fixture.py       twelve records, three schemas, stdlib sqlite3 only
      probe.py         embeddings, cosine recall, purge and read-back
      run.sh           records tool versions, then runs probe.py
      results/run-record.json, results/results.jsonl, results/summary.csv

Run `sh run.sh <output-dir>` against a local Ollama with `nomic-embed-text` and `qwen2.5:0.5b`; the stores, the per-query rows and the purge read-back are written into the output directory. Every file this article relies on is downloadable from the repository: [fixture.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/fixture.py), [probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/probe.py), [run.sh](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/run.sh), [results/run-record.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/results/run-record.json), [results/results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/results/results.jsonl), [results/summary.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/results/summary.csv) and [results/environment.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-provenance-tool-source-test-2026/results/environment.txt). The three third-party source files read for the vendor section are kept privately for verification and are not redistributed; the links above point upstream instead.

## Where this sits in the memory cluster

This is the provenance dimension the existing memory work does not measure. [agent-memory-write-path-reliability-2026](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/) defines the record/update/contradict/delete protocol and lists missing traceability as a defect; the fixture here turns that defect into a counted quantity. [agent-memory-delete-semantics-test-2026](https://baeseokjae.github.io/posts/agent-memory-delete-semantics-test-2026/) traces what a delete removes and shows the audit table still returns the text; that is the surface which breaks this purge too, and the reason source-scoped purges need a stated surface list. [agent-memory-architecture-guide-2026](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) is where the trust boundary sits in the layering, and [agent-memory-embedding-swap-recall-2026](https://baeseokjae.github.io/posts/agent-memory-embedding-swap-recall-2026/) covers the other way recall changes while the text stays the same. [all-ai-jailbreaks-prompt-injection-archive-2026](https://baeseokjae.github.io/posts/all-ai-jailbreaks-prompt-injection-archive-2026/) catalogues the hostile text; this piece follows one such string into storage and back out. For the products whose schemas are read above, see [mem0-agent-memory-guide-2026](https://baeseokjae.github.io/posts/mem0-agent-memory-guide-2026/) and [zep-ai-agent-memory-review-2026](https://baeseokjae.github.io/posts/zep-ai-agent-memory-review-2026/).

Search demand for this exact question is unmeasured in the query exports behind this site, so the piece is scoped as an experiment rather than a demand claim.

## Sources

Read on 2026-11-08 at the pinned commits named, then re-fetched on 2026-11-24T12:11:54Z: all three files were byte-identical to the copies used for the first reading, so the statements about these commits still hold. The fixture measurement itself stays dated 2026-11-08 and was not re-run for this re-check.

- mem0 `MemoryItem` record type — https://raw.githubusercontent.com/mem0ai/mem0/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/configs/base.py
- mem0 recall filter construction — https://raw.githubusercontent.com/mem0ai/mem0/f1791daa86d469249c9b002f62644d58a1eb96a0/mem0/memory/main.py
- Graphiti `EpisodicNode` fields — https://raw.githubusercontent.com/getzep/graphiti/024b83679e48e41d59a7d1714ac0870aff2e4676/graphiti_core/nodes.py
