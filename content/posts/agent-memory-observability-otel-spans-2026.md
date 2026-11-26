---
title: "Agent Memory Tracing: OpenTelemetry Spans for Write, Retrieve and Evict"
date: 2026-11-25T13:35:00+00:00
lastmod: 2026-11-25T13:35:00+00:00
description: "The GenAI semantic conventions already define a memory span with create_memory, search_memory and delete_memory operations. A stdlib SQLite fixture shows the attribute set that answers whether a fact was written, retrieved or evicted, plus the two attributes the spec leaves out."
draft: false
tags:
  - agent memory tracing
  - opentelemetry memory spans
  - gen_ai semantic conventions memory
  - create_memory search_memory delete_memory
  - agent memory observability
  - sqlite memory store instrumentation
  - otlp json span dump
  - stale memory answer diagnosis
  - memory eviction tracing
  - llm agent span attributes
cover:
  image: /images/agent-memory-observability-otel-spans-2026-cover.png
  alt: 'Diagram of three agent-memory traces drawn from the published span dump. Trace one has an invoke_agent parent and one create_memory child labelled record.count 51. Trace two has an invoke_agent parent with two search_memory children for the same query: the first returns the value UTC+8, the second returns UTC+9, with record.count 1 on both, and a callout to the left states that no write span exists between the two reads, so the changed value arrives without a recorded write. Trace three has an invoke_agent parent and one delete_memory child labelled evicted_reason=superseded_by_newer_value. A footer states that the layout is the fixture span shape, not a performance measurement, and that the two returned values come from the run log in method.md rather than from the span dump.'
  caption: 'Three traces from the fixture span dump · span shape only, not a performance measurement'
schema: "schema-agent-memory-observability-otel-spans-2026"
---

A memory-backed agent gives a stale answer and the stack shows a clean turn. The prompt was assembled, the tool returned, the model spoke, and every span on the trace is green. Nothing reports whether the fact was ever written, whether the retrieval that should have supplied it actually matched, or whether the record was quietly evicted two turns earlier. Those three causes produce the same user-visible symptom, and the usual log line — a query string and a hit count — cannot separate them.

This article is about the smallest instrumentation change that can: emit one span per memory operation, named and attributed the way the OpenTelemetry GenAI semantic conventions now define, and add the two attributes the convention deliberately leaves out. A stdlib Python wrapper over a local SQLite store demonstrates the shape on a 51-record fixture, and the span dump it produced is published alongside the script so the trace can be read before anything is wired into a real backend.

## Three questions a memory trace has to answer

For any fact that should have been recalled, ask, in trace order:

1. Was it written? Is there a `create_memory`, `update_memory` or `upsert_memory` span carrying that record at any point, not just this turn?
2. Was it retrieved? Is there a `search_memory` span in this turn whose candidate set included it, and did that search return it after ranking?
3. Was it evicted? Is there a `delete_memory` span for it, with a reason and a timestamp between the write and the bad answer?

If all three are absent, the fault is upstream of the memory subsystem — the agent never asked, or the extraction step never produced the fact. That is a different fix from "raise k", which is what teams usually try first. The value of tracing memory operations is that these four states stop looking identical.

## What the conventions already define

Instrumentation recipes for agent memory often invent span names such as `memory.write` and `memory.retrieve`. Do not — the vocabulary exists. The GenAI semantic conventions in `open-telemetry/semantic-conventions-genai` define a memory span whose `gen_ai.operation.name` is one of `create_memory_store`, `search_memory`, `create_memory`, `update_memory`, `upsert_memory`, `delete_memory` or `delete_memory_store`, with the first and last covering store lifecycle rather than records ([span definitions](https://github.com/open-telemetry/semantic-conventions-genai/blob/e6658f14c9d9ea0760825f029cb82e7673f48fab/docs/gen-ai/gen-ai-spans.md)). The same file fixes span naming and error handling: the span name should be the operation name, and span status follows the general recording-errors rules, with `error.type` conditionally required on failure.

Every statement in this article about the convention is pinned to commit `e6658f14` of that repository, dated 2026-11-06, and that document carries **Development** status, not Stable. Names can still move. Treat this as "the current proposed vocabulary", check the commit you build against, and do not hard-code the strings in more than one place in your codebase.

Span kind is `CLIENT` for an out-of-process memory service and may be `INTERNAL` for a store running in the same process. The fixture below uses `INTERNAL` for that reason. This choice changes how a backend draws the service edge; it does not change the attribute set.

The shape that matters is the hierarchy: one trace per agent turn, an `invoke_agent` parent, and memory operations as child spans under the turn that performed them. That is what lets you ask "was there a write for this record before this read" as a query rather than a manual grep.

## The attribute set, and the one that is easy to misread

The memory span table in the [attribute registry](https://github.com/open-telemetry/semantic-conventions-genai/blob/e6658f14c9d9ea0760825f029cb82e7673f48fab/docs/registry/attributes/gen-ai.md) and the [memory span reference report](https://github.com/open-telemetry/semantic-conventions-genai/blob/e6658f14c9d9ea0760825f029cb82e7673f48fab/reference/reports/memory-span.md) agree on the levels:

- Required: `gen_ai.operation.name`.
- Conditionally required: `error.type` if the operation ended in an error, `gen_ai.memory.record.id`, `gen_ai.memory.store.id` if applicable, `gen_ai.provider.name`, and `server.port` if `server.address` is set.
- Recommended: `gen_ai.memory.record.count`, `server.address`.
- Opt-in, gated: `gen_ai.memory.query.text`, `gen_ai.memory.records`.

`gen_ai.memory.record.count` is the trap. Its meaning is operation-specific: for `search_memory` it is the number of records returned, for `create_memory` the number attempted, and likewise for update, upsert and delete. A zero therefore means "search returned nothing" on one span and "delete matched nothing" on another. Reading `record.count` without `gen_ai.operation.name` in the same query produces exactly the confusion this instrumentation is meant to remove.

## A runnable wrapper with no dependencies

The published script is a single 142-line standard library file importing `hashlib`, `json`, `os`, `random`, `sqlite3`, `time` and `uuid`. It writes span dictionaries in OTLP/JSON shape instead of using the OpenTelemetry SDK, because the run interpreter had no SDK installed and the point is the attribute contract, not the exporter. The same attribute set maps onto `tracer.start_as_current_span(...)` one-for-one when you do add the SDK.

```python
def search_memory(con, rec, trace, parent, query, top_k=3):
    st, t0 = _now(), time.perf_counter()
    cur = con.execute("SELECT key, value FROM memory WHERE ns=? AND value LIKE ? LIMIT ?",
                      (NAMESPACE, f"%{query}%", top_k))
    hits = cur.fetchall()
    attrs = {"gen_ai.operation.name": {"stringValue": "search_memory"},
             "gen_ai.provider.name": {"stringValue": PROVIDER},
             "gen_ai.memory.store.id": {"stringValue": STORE_ID},
             "gen_ai.memory.record.count": {"intValue": str(len(hits))},
             "gen_ai.memory.query.text": {"stringValue": query},   # Opt-In in the spec
             "memory.hit": {"boolValue": bool(hits)},
             "memory.candidate_count": {"intValue": str(len(hits))},
             "memory.op.duration_ms": {"doubleValue": (time.perf_counter() - t0) * 1000}}
    return rec.span(trace, parent, "search_memory", 1, st, _now(), attrs), hits
```

Record keys are replaced by a 16-hex SHA-256 prefix before they reach an attribute (`memory.key_hash`, and `gen_ai.memory.record.id` on delete). That keeps keys usable for correlation across spans while keeping raw identifiers out of a dump that may be shipped to a backend.

## Reading the dump

Three traces, seven spans. The fixture writes 51 synthetic facts in one `create_memory` batch, searches the same query twice with a value change in between, then deletes one record.

| Trace | Span | Attributes in the dump, plus the value the run log records as returned (†) |
| --- | --- | --- |
| 1 | `invoke_agent memory-fixture` | `gen_ai.operation.name=invoke_agent` |
| 1 | `create_memory` | `record.count=51`, `store.id=fixture-store`, duration 11.85 ms |
| 2 | `search_memory` (first) | `record.count=1`, `memory.hit=true`, 0.13 ms; returned `user timezone is UTC+8` † |
| 2 | `search_memory` (second) | `record.count=1`, `memory.hit=true`, 0.11 ms; returned `user timezone is UTC+9 (Asia/Seoul)` † |
| 3 | `delete_memory` | `record.id` (16-hex prefix), `record.count=1`, `memory.evicted_reason=superseded_by_newer_value`, 12.13 ms |

† The returned value is not a span attribute. The dump carries `gen_ai.memory.query.text`, the counts, the hit flag and the durations, and no record content, because `gen_ai.memory.records` is opt-in and was left off in this run. The two returned strings come from the stdout captured in `method.md`.

The interesting row is the pair in trace 2. The same query returns two different values inside one trace, and no write span sits between them: the underlying table was updated directly, so the trace records a read whose answer changed without a corresponding `create_memory` or `update_memory`. That is the staleness signature in its cheapest form. In production it usually appears as a read in turn 40 returning a value written in turn 3 by a path that was never instrumented, and the trace is what makes the missing write visible as a gap instead of a mystery.

After the delete, 50 of the 51 records remain. The delete span carries the reason because the application put it there — not the convention.

## The two attributes the spec leaves out

The memory span table has no attribute for a retrieval hit/miss flag and none for why a record was evicted. Absence here is checked against the complete attribute tables and the reference report at that commit; it says nothing about what a future revision may add. Until then, name your additions outside the `gen_ai.*` namespace so a future convention attribute does not collide with an application one:

- `memory.hit` (bool) on `search_memory`: did the ranked result set contain at least one record? `record.count` alone cannot tell a filtered-out record from a miss when you also post-filter by namespace or freshness.
- `memory.candidate_count` (int): how many candidates the search considered before the top-k cut. The fixture sets it to the returned count because its `LIKE` query has no separate candidate stage; with a vector index this is the number before truncation, and it is the number that tells you whether raising k would help.
- `memory.evicted_reason` (string) on `delete_memory`: `superseded_by_newer_value`, `ttl_expired`, `user_requested`, `capacity`. Without it, an eviction looks the same as a cleanup job and as a bug.

Keep record identifiers in attributes, never in span names. Span names are indexed and aggregated; putting a key hash in the name multiplies the series count by the number of records and makes every dashboard unreadable within a week.

## Four failure signatures and the queries that find them

With the spans above in a backend, each failure mode becomes a query rather than a debugging session:

1. **Never written.** No `create_memory`, `update_memory` or `upsert_memory` span exists for the record at any time before the bad answer. Look upstream at extraction; the memory store is not at fault.
2. **Written, never retrieved.** A write exists, but no `search_memory` span in the failing turn returned it — and `memory.hit=true` with `candidate_count` far above `record.count` says the record was a candidate that lost the ranking cut.
3. **Retrieved zero.** `search_memory` with `record.count=0` and `memory.hit=false`: the query, the namespace filter or the store id is wrong. Compare `gen_ai.memory.store.id` against the store the write used; a typo in a namespace produces a permanent, silent empty result.
4. **Evicted before the read.** A `delete_memory` span with `record.id` matching the missing record falls between the write and the read. `memory.evicted_reason=superseded_by_newer_value` means the fix is a read that honours recency, not a bigger k.

The one-line form of query 2 is: filter `gen_ai.operation.name = search_memory`, group by `gen_ai.memory.record.id` (or your key hash), and look for turns where the record is absent while a write span for it exists earlier.

## Content capture and privacy

`gen_ai.memory.query.text` and `gen_ai.memory.records` are opt-in and the spec says instrumentations should not capture them by default; capture should be gated. That gate matters more for memory than for most telemetry, because a memory record is a user fact by construction. The practical rules that held for this fixture:

- Hash record keys. A 16-hex prefix is enough to join spans and too short to reverse a guessable key set only if the keys are not low-entropy strings; if they are, use a keyed hash.
- Leave `gen_ai.memory.query.text` off in production, or capture it only under an explicit debug flag with a retention window. The fixture records it deliberately, and the published dump says so.
- Do not put record contents in attributes. `gen_ai.memory.records` exists, is opt-in, and is the wrong default for anything a user typed.
- Send memory spans to the same backend as the rest of the turn so the parent-child relation survives. A memory span in a separate pipeline cannot answer "what did this turn read".

## Limits

The measurement here is one synthetic fixture: 51 records, substring matching, no vector index, single process, Python 3.12 with sqlite3, run on 2026-11-16. Nothing in it measures recall quality, latency at scale or cost. OTLP/JSON was produced and is ingestible by shape, but it was not replayed into an OpenTelemetry Collector in this run, so the Collector path is documented API usage rather than a tested pipeline. No framework was checked to see whether it emits these spans today; the convention lists `aws-bedrock-agentcore` and `google-adk` as supporting libraries, and that is the extent of the claim.

For the surrounding picture, see the existing pages on [OpenTelemetry for agent observability](https://baeseokjae.github.io/posts/ai-agent-observability-opentelemetry-2026/), on [Langfuse with a DeepSeek harness](https://baeseokjae.github.io/posts/langfuse-for-deepseek-harness-opentelemetry-based-agent-observability/) for the exporter and backend side, on [agent memory frameworks](https://baeseokjae.github.io/posts/best-ai-agent-memory-frameworks-2026/) and on [memory architecture](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) for where write, retrieve and evict sit in a larger design. The [OpenTelemetry docs page for GenAI agent spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) returns HTTP 200 with a moved notice that points to the repository above rather than serving the definitions itself; the repository is the source to cite. Public discussion of this gap is recent — see the thread ["Agent memory needs its OpenTelemetry moment"](https://news.ycombinator.com/item?id=50411467) — but engagement counts are not evidence that any specific backend emits these spans.

## Files

The fixture is published with this article: [`memory_spans.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-observability-otel-spans-2026/memory_spans.py) (the wrapper), [`spans.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-observability-otel-spans-2026/spans.json) (the OTLP/JSON dump quoted above), [`method.md`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-observability-otel-spans-2026/method.md) (environment, exact output and reproduce command) and [`make_cover.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-observability-otel-spans-2026/make_cover.py) (the diagram source). The fixture database [`memory.sqlite`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-observability-otel-spans-2026/memory.sqlite) is committed beside them, and `python3 memory_spans.py .` in a copy of that directory regenerates both the database and the dump.
