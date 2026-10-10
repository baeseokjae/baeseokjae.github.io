---
title: "Agent Memory Write-Path Reliability: A Reproducible Evaluation Protocol"
date: 2026-10-08T09:55:00+00:00
tags:
  - agent memory write path reliability
  - agent memory evaluation protocol
  - memory write path testing
  - agent memory deletion test
  - contradiction handling memory
  - knowledge update staleness
  - zep graphiti temporal invalidation
  - mem0 delete semantics
  - letta memgpt memory
  - provenance traceability agent memory
  - confident wrong agent memory
  - memory benchmark gaps
description: "Recall benchmarks do not tell you whether a fact is recorded, updated, contradicted or deleted. A five-metric, artifact-hashed protocol for testing the agent-memory write path."
draft: false
cover:
  image: "/images/agent-memory-write-path-reliability-2026.png"
  alt: "Agent Memory Write-Path Reliability: A Reproducible Evaluation Protocol"
  relative: false
schema: "schema-agent-memory-write-path-reliability-2026"
---

Selecting an agent-memory system on retrieval quality is measuring half the system. The half that produces confidently-wrong agents in production is the write path — whether a fact is actually recorded, whether an update supersedes the old value, whether a contradiction is flagged or silently averaged, and whether a delete truly removes the fact from every store it touched. Almost nobody publishes how to measure that.

This article is a fixed, reproducible evaluation protocol for the write path, and it ships the working parts: a controlled dataset, a generic harness with a documented adapter contract, a scoring sheet, and deterministic tests that prove every promised measure is runnable. It reports no vendor numbers of its own. That is deliberate: the deliverable is the protocol, and it is built so the person who runs it publishes the result — never a vendor benchmark reused as if it were an independent measurement.

## Why the write path is the failure surface

Recall benchmarks answer one question: given a store that already contains the right fact, can the system retrieve it? They say nothing about how the fact got there, what happened when it changed, or whether it left when it was deleted. Those are the failure modes users actually experience:

- A deleted preference still surfaces because it was removed from the vector store but not from the entity or graph store.
- A corrected fact coexists with its stale twin, and retrieval returns whichever scored slightly higher.
- A contradiction between two sources is silently resolved by a summarizer, so the agent answers confidently with no record that the inputs disagreed.
- A fact is recorded, but nothing traces it back to the message that produced it, so no one can audit why the agent believes it.

Each of these is a *write-path* defect, and each survives every retrieval benchmark in current use. You can be at the top of a recall leaderboard and still ship an agent that insists a user's employer is a company they left two years ago.

## What the published benchmarks actually measure

The memory benchmarks that drive procurement today were built for retrieval and question answering, not for write correctness.

MemGPT introduced the *Deep Memory Retrieval* (DMR) benchmark alongside virtual context management, framing evaluation as whether a system can answer questions over a large conversation history ([MemGPT paper, arXiv:2310.08560](https://arxiv.org/abs/2310.08560)). LoCoMo added a very-long-term conversational dataset — 300 turns and roughly 9K tokens per conversation across up to 35 sessions — and scored question answering, event summarization and multimodal dialogue generation ([LoCoMo paper, arXiv:2402.17753](https://arxiv.org/abs/2402.17753)). Zep reports out-performing MemGPT on DMR (94.8% versus 93.4%) and improvements of up to 18.5% on LongMemEval with a reported 90% latency reduction, through its Graphiti temporal knowledge graph ([Zep paper, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)).

The closest to write correctness is LongMemEval, which explicitly defines five core long-term memory abilities: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention. It embeds 500 curated questions in scalable chat histories and reports that commercial assistants and long-context models show a 30% accuracy drop on memorizing information across sustained interactions ([LongMemEval paper, arXiv:2410.10813](https://arxiv.org/abs/2410.10813)).

Two of those five abilities — knowledge updates and abstention — touch the write path, which is why LongMemEval is the right benchmark to build on rather than duplicate. But it scores *end-to-end answer accuracy*, not the state of each written fact. A team cannot read the LongMemEval output and learn whether one specific deleted fact stopped surfacing, or whether one specific contradiction was flagged. The write path is the unmeasured variable inside a benchmark that comes closest to touching it.

## The five quantities that define write-path reliability

A write-path evaluation needs a small number of quantities that map to the four things a memory system must do — record, update, resolve contradictions, delete — plus the audit trail. These five are measurable per fact and are scripted in the harness below:

1. **Write success** — after ingest, does an exact-match query return the fact? Measured as the share of ingests that are retrievable immediately afterward. A system that reports success but does not make the fact retrievable has failed at step one.
2. **Staleness after update** — after a fact changes, does the *old* value stop surfacing on a "what is true now" query, and does the *new* value surface? Measured as the share of updates where the stale value is gone and the current value is served.
3. **Contradiction handling** — when two sources assert incompatible values without an explicit update, is the conflict flagged, retained as history, or silently collapsed? Measured as the share of contradictions that leave an auditable trace rather than a single confident answer.
4. **Deletion effectiveness** — after a delete, does the fact disappear from *every* path that could surface it: exact-match, semantic search, and any entity or graph store the delete touched? Measured as the share of deletes with no residual surface.
5. **Provenance traceability** — can a derived fact be traced back to the raw record that produced it? Measured as the share of facts with an intact lineage from the returned memory to its source episode or message.

The protocol also scores a sixth, cross-cutting signal — **out-of-scope abstention** — because a system that fabricates a plausible memory for a question whose answer was never ingested will also fabricate on the deletion and staleness probes. The first four quantities are behavioural and must be measured against the running system. Provenance is partly structural and can be read from the API surface, but a route existing is not evidence that it returns usable lineage, so it is scored the same way: by querying.

## The protocol you can actually run

The protocol is published in full, as files, so that two independent operators get comparable results. Everything lives under the article's evidence directory in the site repository:

- **Dataset** — [dataset.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/dataset.json): 40 write units across four types — 12 stable facts, 8 updates, 6 contradictions (12 assertions), 8 deletions — plus 6 out-of-scope probes whose answers are never ingested.
- **Adapter contract + harness** — [adapters.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/adapters.py) defines the one interface a system must implement; [run_protocol.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/run_protocol.py) drives any adapter through the fixed order and writes `transcript.json` and `scores.json`.
- **Scoring sheet + tests** — [test_protocol.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/test_protocol.py) checks every promised measure deterministically; [fixture_report.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/fixture_report.py) regenerates the fixture score sheet; [README.md](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/README.md) documents how to point the harness at a real system.

The adapter is deliberately small. Point it at the system's own *documented* write API:

```python
class MemoryAdapter(ABC):
    def write(self, item_id, text, scope): ...            # ingest one fact under a stable id
    def update(self, item_id, new_text, scope): ...       # supersede the current value
    def delete(self, item_id, scope): ...                 # remove from every store it touched
    def retrieve_exact(self, item_id, scope): ...         # str | None
    def query(self, question, scope): ...                 # str | None  (answer or abstain)
    def semantic_hit(self, text, scope): ...              # bool: search still surfaces it
    def provenance(self, item_id, scope): ...             # list[str]; [] means no lineage
    def contradiction_trace(self, question, scope): ...   # {"flagged": bool, "values": list[str]}
```

Run it in three commands (Python 3.12, standard library only):

```bash
python3 test_protocol.py                                             # fixture unit tests
python3 run_protocol.py --adapter fixture-reference --out $TMPDIR/out   # reference run
python3 run_protocol.py --adapter fixture-write     --out $TMPDIR/out   # one defect injected
```

The harness emits `transcript.json` — the ordered, sanitized request/response log — and `scores.json`, which carries the per-item rows (the raw `pass`/detail for every fact) plus the six aggregate rates and a `transcript_sha256`. Every "this system failed on delete" statement you make must map to a transcript line and that hash; without it, it is an anecdote.

## Fixture self-check (fixture only — not a vendor measurement)

Before the protocol is trustworthy, the harness and scorer must be. The shipped package includes a deterministic in-memory double — a synthetic adapter, **not a vendor system** — used purely to prove the machinery runs with no credentials, network or hosting. Running `python3 fixture_report.py` executes the ten deterministic unit tests and scores the reference double plus one single-defect double per measure. The recorded output is [fixture-tests.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/fixture-tests.txt) alongside [fixture-report.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/fixture-report.json), with the run's environment, commands and hashes recorded in [first-party-run.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/first-party-run.json).

On 2026-10-08 (UTC) that run reported `RESULT: ran=10 failures=0 errors=0`, with the captured stdout hashed as `e07922fac4babc5d119a0433ccd327e2cc62c995d85eefdaa98a4fdfa26c14c4`. The capture normalizes only the wall-clock elapsed line (`Ran 10 tests in <elapsed>s`) so the recorded file is byte-reproducible across machines; every test outcome and the result line are preserved verbatim. The reference double scores 1.0 on all six measures (write-success 40/40, staleness 8/8, contradiction 6/6, deletion 8/8, provenance 20/20, out-of-scope 6/6). Each single-defect double then drops exactly its own measure and no other: the dropped-write double lands at write-success 39/40; the never-supersede double at staleness 0/8; the silent-collapse double at contradiction 5/6; the residue double at deletion 7/8; the no-lineage double at provenance 19/20; the fabricating double at out-of-scope 5/6. That is the property a scorer must have: a known injection moves its own column and leaves the others alone.

Read this for what it is. These are **fixture results**, produced by a synthetic double to validate the harness. They are not benchmarks of mem0, Graphiti, Letta or any other system, and no live-vendor run was performed while writing this article. When you point the same harness at a real system, you generate the vendor scores yourself; until then, that score sheet is a template.

## How the candidate systems differ, and why that changes the test

The three most-referenced open systems differ in exactly the way a write-path test is built to detect.

**mem0** exposes the write path as first-class routes. Its OpenAPI spec (info version `v1`) documents collection write and delete on `/v1/memories/`, per-memory update and delete on `/v1/memories/{memory_id}/` (get, put, delete), and a per-memory history route `/v1/memories/{memory_id}/history/` ([mem0 OpenAPI spec](https://raw.githubusercontent.com/mem0ai/mem0/main/docs/openapi.json)). That history route is the one to probe for provenance — but the route existing is not proof it answers usefully.

The delete itself is a multi-store, two-phase operation. In the SDK's `_delete_memory`, deletion removes the vector record, then writes a `DELETE` row into the history database with `is_deleted=1`, and — unless skipped — removes the memory from the entity store. `delete_all` batches, requires at least one filter, and stops when it sees a repeated batch ([mem0 memory/main.py](https://raw.githubusercontent.com/mem0ai/mem0/main/mem0/memory/main.py)). That structure is the reason a single vector-store query can over-report deletion success: the vector record can be gone while entity-store cleanup did not run. A deletion-effectiveness test must query both the retrieval path and the entity or graph path — which is why the harness scores `retrieve_exact` and `semantic_hit` separately.

**Graphiti**, Zep's open-source engine, takes the opposite design stance on updates. Facts carry validity windows; when information changes, old facts are *invalidated, not deleted*, and every entity and relationship traces back to the episodes — the raw data — that produced it. Its own comparison table lists "automatic fact invalidation with temporal history preserved" for contradiction handling and "bi-temporal tracking" with sub-second latency claims ([Graphiti README](https://raw.githubusercontent.com/getzep/graphiti/main/README.md)). This design makes the staleness test *different*, not easier: an invalidated fact should not surface on a "what is true now" query but should still be recoverable as history, so the scoring sheet must distinguish "stale value gone from current answers" from "stale value erased entirely". One of those is correctness; the other may be data loss, and the harness records both.

The public code surface you can fetch is retrieval-side: `graphiti_core/search/search.py` defines `search`, `edge_search`, `node_search`, `episode_search` and `community_search` with rerankers ([Graphiti search.py](https://raw.githubusercontent.com/getzep/graphiti/main/graphiti_core/search/search.py)). That tells you where the write path is *not* — it must be driven through ingestion and invalidation directly, rather than inferred from a search API.

**Letta** carries the MemGPT lineage, and its README states the current source now lives in `letta-ai/letta-code` while the historical `letta-ai/letta` tree keeps the retired V1 API server on an `archive` branch, with existing tags and releases preserved for reproducibility ([Letta README](https://raw.githubusercontent.com/letta-ai/letta/main/README.md)). The practical consequence for a test: pin a concrete package version, not a project name. "Letta" and "MemGPT" have each referred to different codebases at different times, so a result attributed to either without a version tag is not reproducible.

Pinned versions as of 2026-10-08: mem0 release `ts-v3.3.1` (published 2026-09-25), Graphiti `v0.30.2` (2026-09-08), Letta `0.16.8` (2026-05-14). All three repositories are Apache-2.0, and each had commits pushed within days of that date: mem0 66,806 stars, Graphiti 31,547, Letta 25,074 ([mem0 latest release](https://api.github.com/repos/mem0ai/mem0/releases/latest), [Graphiti latest release](https://api.github.com/repos/getzep/graphiti/releases/latest), [Letta latest release](https://api.github.com/repos/letta-ai/letta/releases/latest), [mem0 repo](https://api.github.com/repos/mem0ai/mem0), [Graphiti repo](https://api.github.com/repos/getzep/graphiti), [Letta repo](https://api.github.com/repos/letta-ai/letta)).

## Reading vendor numbers honestly

Vendor benchmark figures are not cross-comparable without a pinned model stack, and the vendors sometimes say so themselves. mem0's README reports a new memory algorithm with LoCoMo 92.5 (from 71.4), LongMemEval 94.4 (from 67.8) and BEAM 64.1 at 1M tokens — and states those scores "reflect Mem0's managed platform, which includes proprietary optimizations not available in the open-source SDK; open-source users should expect" lower results ([mem0 README](https://raw.githubusercontent.com/mem0ai/mem0/main/README.md)). That footnote is the whole point of the discipline this protocol enforces: a self-reported, platform-specific number is a vendor claim, and it is never a substitute for a result the operator produced on the exact version being deployed.

The same caution applies to the Zep figures above. They are the authors' measurements on a documented setup, not an independent reproduction, and benchmark results apply to the version and harness they were measured on — not automatically to a later release or a different hosting mode.

## Running the protocol on your stack

The protocol is deliberately small enough to run in an afternoon per system:

1. Keep the shipped [dataset.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/agent-memory-write-path-reliability-2026/protocol/dataset.json) unchanged, and pin one system version plus one model in the transcript header.
2. Implement `MemoryAdapter` against the system's *documented* write API — ingest, update, delete, and a query path for each. Do not infer write behaviour from a search endpoint.
3. Run `run_protocol.py` against your adapter, save `transcript.json`, and record its hash with the exact date, commit or release tag, and model.
4. Score the rates from the raw rows, then re-read the deletion rows by hand once — multi-store deletes are where the automated check is most likely to be wrong.
5. Repeat for a second system with the same dataset, and publish both score sheets together.

What a failing score looks like in production is specific and worth naming in advance. A high write-success rate with a low staleness rate means the agent will keep citing superseded facts. A low contradiction rate means it will answer confidently where its inputs disagreed. A low deletion rate means a "forget this" instruction will appear to work and then resurface weeks later. A low provenance rate means no incident involving a bad memory can be root-caused. Report all five; a single headline number hides which failure you are buying.

## Limitations and what this protocol cannot tell you

- **It is a protocol plus a fixture self-check, not a vendor result.** The only numbers reported here come from the synthetic double and prove the harness runs; no run against a live vendor system was performed while writing, and none is implied.
- **Demand figures are carried, not re-measured.** The cluster-level search impressions that motivate this topic come from the operator's own Google Search Console and Bing exports, not from a third-party volume tool, and no keyword-difficulty number is asserted anywhere here.
- **Vendor benchmark figures are attributed, not reproduced.** The mem0 and Zep numbers above are the vendors' own published claims, scoped to their setups and dates.
- **API route presence is not behavioural evidence.** A documented delete route does not tell you the delete is complete across stores; that is exactly what the protocol measures.
- **Fixture adapters are doubles, not systems.** The in-memory reference adapter is a synthetic control for the scorer; its 1.0 rates are a self-test of the harness, never a claim about any product.
- **Version and time bounds.** Results are only meaningful pinned to a version and date; write-path semantics can change between releases.
- **What it leaves out.** Multi-tenant isolation, latency and cost under concurrent load, and long-horizon fact churn are out of scope. This protocol measures whether individual facts are correctly written, updated, contradicted, deleted and traced — not how the system performs under production traffic.

## Related reading

For the retrieval and architecture side of the same cluster, see the [agent memory architecture guide](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) and the [Zep and Graphiti review](https://baeseokjae.github.io/posts/zep-ai-agent-memory-review-2026/). Both cover how these systems retrieve; this protocol covers whether they write correctly in the first place.

## Primary sources

Primary artifacts were fetched on 2026-10-08 (UTC); raw bytes and hashes are recorded with the research brief that accompanies this article.

- Zep paper (DMR 94.8% vs 93.4%, LongMemEval up to 18.5%, 90% latency reduction; published 2025-01-20) — https://arxiv.org/abs/2501.13956
- MemGPT paper (Deep Memory Retrieval; virtual context management; published 2023-10-12) — https://arxiv.org/abs/2310.08560
- LoCoMo paper (300 turns, ~9K tokens, up to 35 sessions; published 2024-02-27) — https://arxiv.org/abs/2402.17753
- LongMemEval paper (five abilities, 500 questions, 30% accuracy drop; published 2024-10-14) — https://arxiv.org/abs/2410.10813
- Graphiti README (validity windows, invalidation not deletion, episode provenance) — https://raw.githubusercontent.com/getzep/graphiti/main/README.md
- mem0 README (April 2026 algorithm table: LoCoMo 92.5, LongMemEval 94.4, BEAM 64.1; managed-platform caveat) — https://raw.githubusercontent.com/mem0ai/mem0/main/README.md
- Letta README (MemGPT successor; current source in letta-ai/letta-code; retired V1 API on the archive branch) — https://raw.githubusercontent.com/letta-ai/letta/main/README.md
- mem0 OpenAPI spec (write/update/delete/history routes; info version v1) — https://raw.githubusercontent.com/mem0ai/mem0/main/docs/openapi.json
- mem0 SDK memory/main.py (two-phase multi-store delete; delete_all filter guard and repeated-batch stop) — https://raw.githubusercontent.com/mem0ai/mem0/main/mem0/memory/main.py
- Graphiti search/search.py (retrieval-side module: search, edge_search, node_search, episode_search, community_search) — https://raw.githubusercontent.com/getzep/graphiti/main/graphiti_core/search/search.py
- mem0 latest release (ts-v3.3.1, 2026-09-25) — https://api.github.com/repos/mem0ai/mem0/releases/latest
- Graphiti latest release (v0.30.2, 2026-09-08) — https://api.github.com/repos/getzep/graphiti/releases/latest
- Letta latest release (0.16.8, 2026-05-14) — https://api.github.com/repos/letta-ai/letta/releases/latest
- mem0 repository metadata (66,806 stars, Apache-2.0, last push 2026-10-07) — https://api.github.com/repos/mem0ai/mem0
- Graphiti repository metadata (31,547 stars, Apache-2.0, last push 2026-10-07) — https://api.github.com/repos/getzep/graphiti
- Letta repository metadata (25,074 stars, Apache-2.0, last push 2026-09-10) — https://api.github.com/repos/letta-ai/letta
