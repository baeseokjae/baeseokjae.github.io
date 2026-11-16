---
title: "The Agent Writes a Correction and Then Reads the Old Fact: Measuring the Memory Write-Visibility Window (2026)"
date: 2026-11-15T00:29:00+00:00
tags:
  - agent memory write visibility
  - read after write consistency
  - eventual consistency agent memory
  - vector index commit lag
  - embedding latency memory write
  - two-phase memory write
  - stale read agent memory
  - memory write visibility probe
description: "A memory write returns, the next turn reads the superseded value. An 11-configuration sweep shows when the stale read appears and how much of the window is the embedder."
draft: false
schema: "schema-agent-memory-write-visibility-window-2026"
---

Turn 18 of a support-agent transcript. The operator says staging moved from `db-08` to `db-09`. The agent calls its memory tool, gets a success response, and answers "noted — staging now points at `db-09`". Turn 19, a different question that touches the same fact. The agent answers `db-08`.

Nothing errored. The record store accepted the write, the embedding call was queued behind it, and the vector index had not committed when the next retrieval ran. The acknowledgement the agent trusted ("write succeeded") came from the source-of-truth store. The capability it depended on ("my next search returns this value") belongs to the derived index, which acknowledged nothing and was never asked.

This article measures that gap: how long it is, what it is made of, and how to check it in your own stack with one canary fact.

## Two stores, two acknowledgements, one wrong contract

Any memory system split into a record store plus a derived index has a window between "the write returned 200" and "a query can see it". The window exists whether or not anyone documents it; what varies is its length and whether the caller is told.

The shortest version of the problem is when the vector lives in the same transactional row as the fact. pgvector's own README states the design plainly: "Store your vectors with the rest of your data", and it advertises "ACID compliance, point-in-time recovery, JOINs, and all of the other great features of Postgres" from its [project page](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md). If the embedding is computed before the `INSERT` and stored in the same row, there is no separate index commit to wait for — the row is visible or it is not, atomically. Note what the same README says about approximate indexes: "you will see different results for queries after adding an approximate index", which is a recall statement, not a visibility one.

The window appears when the embedding cannot happen inside that transaction — because the embedder is a network call, a rate-limited API, or a GPU queue — and the system therefore splits the write into two phases: commit the record now, embed and index later. That split is not a bug. It is what makes ingestion non-blocking, and documented frameworks recommend exactly that shape. Graphiti's `add_episode` docstring, at tag v0.31.2, says: "It is recommended to run this method as a background process, such as in a queue … consider using FastAPI's background tasks or a dedicated task queue like Celery for this purpose" ([graphiti.py, lines 1410-1413](https://raw.githubusercontent.com/getzep/graphiti/v0.31.2/graphiti_core/graphiti.py)). The project states a calling recommendation and no timing. The consequence is left to the caller: a read issued after the request returns must not be assumed to see the episode.

So the reader's real question is not "is my store eventually consistent" — it is "how long is my window, and does my agent read inside it".

## What the sweep measured

The experiment puts three adapters behind the same two-method interface, `write(fact)` and `search(query)`, and drives a scripted 30-turn conversation over 12 seeded facts in four entity types (deploy target, token rotation, on-call owner, retention). Every turn updates one fact and then immediately performs the read that should surface it: 30 turns per configuration, 11 configurations, 330 recorded turns. The post-write read fires 50 ms after the write returns, because an agent's next turn starts in milliseconds, not seconds.

The commit schedule is simulated by a fake clock that advances 2000 ms per turn, so classification cannot depend on host jitter: the tick is free-running and is never allowed to commit retroactively at write time, which is exactly the accounting mistake a real queue hides. The cost injected into each commit is the measured latency of the real embedder on the same texts, not an assumed constant. The synchronous control — embed and upsert inline before `write()` returns — produced 0 stale reads in 30 turns, which is the check that the fixture asks the right question; if the control had shown stale reads, the fixture would have been broken and nothing here would be reportable.

Stale-value reads, by configuration:

| Adapter | Commit setting | Stale reads | Fresh reads |
|---|---|---|---|
| sync-control (inline embed + upsert) | — | 0/30 | 30/30 |
| two-phase async | 0 ms | 0/30 | 30/30 |
| two-phase async | 250 ms | 14/30 | 16/30 |
| two-phase async | 1000 ms | 15/30 | 15/30 |
| two-phase async | 5000 ms | 30/30 | 0/30 |
| batch flush | 1000 ms, N=1 | 0/30 | 30/30 |
| batch flush | 1000 ms, N=8 | 22/30 | 8/30 |
| batch flush | 1000 ms, N=32 | 22/30 | 8/30 |
| batch flush | 5000 ms, N=1 | 0/30 | 30/30 |
| batch flush | 5000 ms, N=8 | 30/30 | 0/30 |
| batch flush | 5000 ms, N=32 | 30/30 | 0/30 |

Two rows carry all the information. At a 250 ms commit interval, 14 of 30 corrections were invisible to the read that followed them — the interval exceeded the 50 ms read gap, so the read landed before the commit. At 5000 ms, every read landed before its commit. At 0 ms the two-phase adapter degenerates into the synchronous control and is clean.

The batch rows matter because "we buffer writes" is the usual proposed fix. Buffering with N=1 is the synchronous case and is clean at either tick. Buffering with N=8 or N=32 is not a fix at all: only one write lands per turn, so the count threshold is never reached inside a turn and the flush interval decides everything. At a 1000 ms tick, 22 of 30 reads were stale; at 5000 ms, all 30. A batch size of 32 behaves identically to 8 in this workload — the count threshold is simply never the trigger, so this run does not test whether a larger batch changes the window, only that the timer does.

## Decomposing the window

A stale read needs two conditions: the commit has not landed, and the read gap is shorter than the remaining wait. Three terms decide the outcome — the embedder, the commit interval, and the agent's turn gap — and on a CPU host the first is larger than most people budget for.

Embedding one short fact through a local Ollama endpoint (all-minilm, 384 dimensions; endpoint shape per the [Ollama `/api/embed` reference](https://docs.ollama.com/api/embed)) is not free. Across 42 unique texts, sequential calls, no batching, on a 2 vCPU host: median 264.5 ms, p95 427.8 ms, minimum 34.9 ms, maximum 981.6 ms, 11.06 s total. An earlier run of the same harness on the same host measured 24 texts at a median of 260.5 ms, p95 429.2 ms, minimum 31.4 ms. The spread is host contention, not model variance, and both runs are single-host — so quote a distribution, not a number, and do not treat either median as the model's cost. The floor is what matters for design: 34.9 ms is already more than half of a 50 ms read gap, before any queue, network hop, or commit interval is added.

That is the composition the two-store design invites: write accepted at t=0, embedder takes tens to hundreds of milliseconds, the index commits on its own tick, and the next turn's read happens 50 ms later. The window is not one bad component. It is the sum of a term you measured once (the embedder) and a term you configured (the tick), evaluated against a read gap you probably never wrote down.

## The real-tick runs: what a 1 s interval actually costs

The sweep above models time. Two runs measured it with a real thread, a real 1 s tick and the real embedder, polling the index every 10 ms for up to 10 s after writing one canary fact into a fresh store:

- Run A: 1085.3, 1206.6, 1180.5, 1002.6, 1291.3 ms — median 1180.5 ms, range 1002.6-1291.3 ms (n=5).
- Run B, minutes later on the same host: 987.9, 987.6, 994.0, 1006.7, 990.2 ms — median 990.2 ms, range 987.6-1006.7 ms (n=5).

The two runs differ by up to ~190 ms in the observed range. That spread is the honest uncertainty here, and it is why this article gives ranges rather than a single "the window is 990 ms".

In this configuration the tick offset dominates, not the model. The worker thread starts 50 ms before the write and ticks every 1000 ms, so the canary written just after a tick waits almost the whole interval; the short canary text then embeds in tens of milliseconds, which is why Run B clusters at 987-1007 ms rather than at interval-plus-median-latency. Run A's higher and wider range reflects a different worker start offset and a slower embed on those trials. The sweep is where the full measured per-text distribution is injected into the commit timeline; the live runs confirm the order of magnitude on real wall-clock time and show how much of the window is scheduling rather than the embedder.

## Which reads must be read-your-writes

Not every read needs to see the write it follows. Splitting the two is the difference between a working design and a store nobody can reason about:

- **Read-your-writes required:** the fact the agent just corrected, the constraint it just added, the identity or permission it just changed, and anything the agent will quote back to the user in the same session as confirmation. These reads are inside the window by construction.
- **Eventual is fine:** background enrichment, summarization passes, analytics over accumulated memory, and cross-session recall where the fact is minutes old. Nobody is holding a turn open for those.

The design rule that follows: route the first class through the path that acknowledged the write — read the record store directly for the fact id you just wrote, or make the index commit before returning when the caller asks for it. The cost of a synchronous commit is the embedder term, and the embedder term is measurable (tens to hundreds of milliseconds above); the cost of a stale read is an agent repeating a wrong hostname to a customer.

## Measure it in your own stack

One canary fact and a poll loop answer the question for any adapter. The probe below needs only the two methods your store already has, and returns the write-to-visible window in milliseconds:

```python
import time

def visibility_window(adapter, fact_id, new_value, deadline_s=10.0, poll_ms=10):
    t0 = time.perf_counter()
    adapter.write(fact_id, new_value)
    while time.perf_counter() - t0 < deadline_s:
        if adapter.search(fact_id) == new_value:
            return (time.perf_counter() - t0) * 1000.0
        time.sleep(poll_ms / 1000)
    return None  # never became visible inside the deadline
```

Write a value the store cannot already hold (a timestamped token), then read the two assertions:

1. `visibility_window(...) is not None` — the write is visible to a read at all, inside your deadline. `None` is a failure, not a slow success.
2. A second read, issued after the window, returns the new value and not the value it superseded — an update replaces what it replaces, rather than accumulating alongside it.

Run it against the adapter your agent actually uses, at the turn gap your agent actually has, and compare the measured window with that gap. If the window is longer, the read is inside it and no amount of retry logic fixes the classification: the store was telling the truth about a commit it had not made yet.

Run the same probe in CI against a fixed canary and you have the regression check that a later "just make it async" refactor cannot quietly defeat. A per-store visibility budget — the measured window asserted below a threshold, per configuration — turns the window from folklore into a number that fails a build when it grows.

## Evidence and how these numbers were checked

The harness, fixture and raw per-turn records for this article are in the site repository: [sweep.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-write-visibility-window-2026/sweep.py) (fixture, three adapters, sweep, live poll), [fixture.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-write-visibility-window-2026/fixture.jsonl), [results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-write-visibility-window-2026/results.jsonl) (330 rows, one per turn per configuration), [environment.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-write-visibility-window-2026/environment.json) and [run.log](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-write-visibility-window-2026/run.log).

Every count in the table above was recomputed from those 330 rows on 2026-11-15, not restated from earlier prose, and the three primary sources were re-read and re-hashed in the same pass. Two figures from an earlier draft did not survive that check and are withdrawn rather than corrected in place: a visibility range described as "987.4-990.2 ms", which appears in neither preserved run, and an embedder median of "31.1 ms", which appears in no record at all. One artifact detail is worth stating because it looks like a contradiction: `run.log`'s summary lines report zero stale-value reads at every interval, and its stale outcomes sit in a `no_or_wrong_result` column. That run predates the harness fix that replaced top-1 ranking with a keyed read, so a superseded fact could come back as a different-ranked result rather than as the old value; its live-poll trials and embed distribution are used here, its aggregate counts are not.

## What this does not cover

The fixture is keyed: the read asks for a specific fact id, which removes retrieval quality from the result and makes the stale/fresh classification exact. An open-ended top-k search adds a second failure mode — a different fact ranking first — that this run deliberately excludes. The commit schedule is modelled rather than produced by a real queue, so real queue backpressure, retries and multi-worker contention are outside the measurement; two-writer conflicts are a separate problem, and the delete, encoder-swap and embedder-context paths are covered by their own tests. No named memory framework was observed directly here: the only product-level claim is the quoted Graphiti docstring at its pinned tag, and nothing in this article asserts that any vendor is or is not eventually consistent — that would have to be read from its code or documentation at a specific version.

If your store shows a stale read in the probe, the useful next step is not a retry loop around the model. It is to move the read that matters onto the path that acknowledged the write, and to keep the probe running so the window stays a number you know.
