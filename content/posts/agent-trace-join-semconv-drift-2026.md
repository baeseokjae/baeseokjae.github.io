---
date: 2026-10-31 13:10:00+00:00
description: Two independently instrumented agents can both look correct and still fail to join in one trace view. A version-pinned look at the gen_ai.system to gen_ai.provider.name drift, three producers, and a six-clause join-key contract you can test offline.
draft: false
schema: schema-agent-trace-join-semconv-drift-2026
tags:
- open-telemetry
- observability
- ai-agents
- distributed-tracing
- multi-agent
title: 'Agent Traces That Don''t Join: gen_ai.system vs gen_ai.provider.name and a Join-Key Contract for Mixed-Framework Fleets (2026)'
---

A team runs a LangGraph service, an OpenAI Agents SDK worker, and a coding-agent CLI with telemetry switched on this quarter. Every producer is instrumented, every span arrives, and the per-agent cost dashboard still covers exactly one of the three. The others are not erroring; they are simply invisible to the `group by` everyone wrote, because the attribute that identifies a provider is spelled differently by each producer and, in one case, is not an attribute at all. The instrumentation guide already on this site, [OpenTelemetry for AI agents](https://baeseokjae.github.io/posts/ai-agent-observability-opentelemetry-2026/), teaches how to emit those spans and predates the rename described below; this post is about what happens after the spans exist. The architecture question that led readers to the site is answered structurally in the [multi-agent system design guide](https://baeseokjae.github.io/posts/multi-agent-system-design-guide-2026/), which covers how to decompose the fleet but not what the telemetry contract between its members has to say.

## What actually changed, dated

The GenAI semantic conventions no longer live in the main OpenTelemetry conventions repository. The repository `open-telemetry/semantic-conventions-genai` reports `created_at` of 2026-05-05T03:08:44Z to the GitHub API, which is when the GenAI documents were split out; a 2025-era link into `semantic-conventions/docs/gen-ai` therefore points at a different artifact generation, not at the current registry. The provenance call is reproducible: https://api.github.com/repos/open-telemetry/semantic-conventions-genai

In the registry file at commit `6f98aef`, checked 2026-10-31, `gen_ai.provider.name` occupies a single table row (line 39) marked Development, with well-known values `openai`, `gcp.gen_ai` and `gcp.vertex_ai`. The exact attribute id `gen_ai.system` has no row at all. The only substring matches in that file are `gen_ai.system_instructions` (lines 67 and 316) and `gen_ai.system_instructions_ref` (lines 68 and 336), which are prompt-content attributes, not provider identity. The spans document at the same commit behaves the same way: nine substring hits, all of them `system_instructions*`, and no span section that instructs an emitter to set `gen_ai.system`. Both pins:

- https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/6f98aef121ae3d5f224c5084d9fb4433bc6f7f67/docs/registry/attributes/gen-ai.md
- https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/6f98aef121ae3d5f224c5084d9fb4433bc6f7f67/docs/gen-ai/gen-ai-spans.md

That is a bounded grep of two files, not a registry-wide crawl, and `gen_ai.provider.name` is still Development, so it can change without a major version. The claim it supports is narrow and sufficient: the current registry does not define `gen_ai.system`, and a query that filters on it is filtering on an identifier the registry no longer maintains.

## Three producers, three states, not two

The tempting story is a rename: old spelling on one side, new spelling on the other, one sed command to fix it. The pinned artifacts do not support that. They show three states, which is why the fix belongs in a normalisation layer rather than in a find-and-replace.

| Producer | Pinned at | Provider identity | Agent identity | State |
|---|---|---|---|---|
| Claude Code CLI | docs page, Traces (beta), checked 2026-10-31 | `gen_ai.system` = `anthropic`, "Always" | `agent_id`, `parent_agent_id`, `query_source_safe` | old spelling only |
| openllmetry (Traceloop SemConv helpers) | commit `8d9c93f` | `LLM_SYSTEM = "gen_ai.system"` | none in this module | old spelling only |
| Google ADK (Python) | commit `8cd3b12` | both `gen_ai.system` and `gen_ai.provider.name` | `gen_ai.agent.name` | dual-emit |
| OpenAI Agents SDK (Python) | commit `e355d69` | none: own span data schema | `agent_name`, `turn` | neither |

Claude Code's monitoring page is the clearest case because it is a table, not code. The row for `gen_ai.system` says the value is always `anthropic` and labels the attribute as an "OpenTelemetry GenAI semantic convention", while the same table pairs `gen_ai.request.model`, `gen_ai.response.id`, `gen_ai.response.finish_reasons` and `gen_ai.tool.call.id`. A grep of the saved page returns one occurrence of `gen_ai.system` in the table and none of `gen_ai.provider.name`. The page is beta and unpinned, so the row must be re-checked on any later date it is cited: https://docs.claude.com/en/docs/claude-code/monitoring-usage

The Traceloop helper module is the library-level version of the same state. Line 154 defines `LLM_SYSTEM = "gen_ai.system"` under a comment saying the constant was removed from `SpanAttributes` in v0.5.0 and now needs migrating to its upstream `GEN_AI_*` counterpart, with the migration still on a TODO. The constant exists and downstream instrumentations import it; whether a given instrumentation still emits it is a separate question this file cannot answer: https://raw.githubusercontent.com/traceloop/openllmetry/8d9c93f37b352131f5871dcb6ecf5e79c19aeb40/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py

Google ADK shows what the overlap window looks like in practice. It imports both `GEN_AI_SYSTEM` and `GEN_AI_PROVIDER_NAME`, sets `gen_ai.system` to `gcp.vertex.agent` on one path, and sets `GEN_AI_PROVIDER_NAME` from a resolver on its common attributes, with a comment stating that both are kept for consumers because schema v1 keeps `gen_ai.system` only. That comment also attributes the replacement to semantic conventions version 1.37; treat that as ADK's reading of the boundary rather than the registry changelog, which is the artifact that would settle it: https://raw.githubusercontent.com/google/adk-python/8cd3b12c8a5d658c5e0d3ea0731d8be34a092a4a/src/google/adk/telemetry/tracing.py

The OpenAI Agents SDK is the state that breaks every key-based assumption. Its span model is a set of `SpanData` subclasses with slots rather than an attribute bag: `AgentSpanData` carries `name`, `handoffs`, `tools`; `TurnSpanData` carries `turn`, `agent_name`, `usage`; `FunctionSpanData` carries `name`, `input`, `output`. Grepping the span data model and span construction for `gen_ai.` returns nothing. Agent and provider identity therefore live in the producer's own keys, and a backend that only indexes OpenTelemetry attributes has nothing to key on unless the exporter maps them or a resource attribute carries the service identity: https://raw.githubusercontent.com/openai/openai-agents-python/e355d69152d4f4730dfb03b63dbce53e8d9f5d8c/src/agents/tracing/span_data.py

## Why the dashboard goes quiet instead of breaking

A group-by that filters on a missing attribute does not raise; it returns the subset that has the attribute. That is the whole failure mode, and it has three distinct causes visible in the matrix above. When identity is an attribute with the old spelling, a new-spelling filter drops the producer. When identity is dual-emitted, the same producer can appear under two keys and inflate counts if both are summed. When identity is carried in a private span schema, no OpenTelemetry attribute filter can see it at all, so the producer is absent from every query that is not built on that schema.

The cost of this is organisational rather than technical. A missing third of the fleet reads as a quiet week: no errors, no gaps in the time series, just fewer rows. A tool-failure dashboard that silently covers one producer will report a lower failure rate during exactly the incident that broke a different producer, and nothing in the chart says which population it measured.

## The join-key contract: six clauses

A contract is only useful if it can be checked, so each clause below is a property of the emitted spans rather than a policy statement.

1. **One provider key, version-pinned.** Name the attribute and the conventions revision it comes from, e.g. `gen_ai.provider.name` as defined at a specific registry commit, not "the GenAI conventions" as a floating reference. A pin is what makes the contract reviewable a quarter later.
2. **An explicit dual-emit window with an end date.** ADK's approach is correct in shape and incomplete without an owner and an exit: both spellings during migration, with the retirement tracked. Without the end date, "both" becomes the permanent contract and the ambiguity never resolves.
3. **A fallback chain, not a single key.** Resolution order must be written down: registry spelling, then the retired spelling, then the producer's own identity field, then a resource attribute. The chain must be applied at ingest, so the stored record has one canonical field and dashboards never need to know the producer.
4. **Agent identity separate from provider identity.** `gen_ai.agent.name` where available; `agent_id` (Claude Code) or `agent_name` (OpenAI Agents SDK) otherwise. Provider identity answers "which vendor billed this"; agent identity answers "which component spent it". Conflating them is why per-agent cost dashboards end up grouped by model.
5. **A tool-call join id shared across producers.** `gen_ai.tool.call.id` is documented by one producer and absent from another's attribute set, so tool spans can be matched to LLM spans only by trace and time unless the id is mandated for both.
6. **Cost attribution keys that survive the rename.** Token counts plus a model identifier plus a price table reference, all on the same span. A provider key that resolves correctly but sits on a span without `gen_ai.usage.input_tokens` still yields an empty cost row.

Clauses 3 to 6 are the reason a rename alone does not fix the dashboard. The registry only governs clause 1.

## The join test, and what it actually returned

The test is a pure-standard-library script with no network access and no SDK: it loads three span fixtures built from the pinned sources above, resolves identity three ways, and counts how many spans each of three dashboard queries returns. Run against nine fixture spans on 2026-10-31, it printed:

- `gen_ai.system` key: identity coverage 5 of 9 spans (both Claude Code spans, all three ADK spans).
- `gen_ai.provider.name` key: identity coverage 3 of 9 spans (ADK only).
- Contract fallback chain: identity coverage 5 of 9 spans, unchanged, because the four OpenAI spans carry no provider identity inside span data for any clause to fall back to. That gap has to be closed with a resource attribute, which is clause 3's last resort and is not observable from a span data model.
- Cost by agent: 1 of 9 spans under the `gen_ai.system` key, 2 of 9 under the contract, because the fallback finds `agent_id` and input tokens on the Claude Code request span.
- Tool failure rate: 1 of 9 spans under every key, because only the ADK tool span carries both a documented tool name and an error attribute.
- Context utilisation: 1 of 9 spans under every key, because only the ADK model span carries a documented request limit alongside input tokens.

Those numbers are the honest form of this article's argument, and they are less flattering than "one key fixes it". Provider identity is a necessary clause and not a sufficient one: after the fallback chain is in place, two of the three dashboards still cover one producer, because the attributes those dashboards need are absent from the documented sets of the other two producers. A join-key contract without clauses 4 to 6 produces a correctly keyed, still-partial dashboard.

The fixtures are documented-attribute inventories, not runtime captures: each file records which producer, which pinned source, and which fields are attested versus assumed, and the Claude Code fixture explicitly notes that no `gen_ai.tool.name`, `gen_ai.usage.output_tokens` or `gen_ai.request.max_tokens` row appears in the documented set. Running it yourself takes one command, and the fixtures are small enough to read:

- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-trace-join-semconv-drift-2026/join_test.py
- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-trace-join-semconv-drift-2026/drift-matrix.csv
- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-trace-join-semconv-drift-2026/PINNED-SOURCES.md

If you want the single-producer baseline first, the [OpenTelemetry tracing walkthrough for one harness](https://baeseokjae.github.io/posts/opentelemetry-tracing-for-deepseek-harness/) shows the same attributes emitted by one stack, where none of this drift is visible.

## Migration order for a mixed fleet

Do the ingest-side change before the producer-side change. Add the canonical field and the resolution chain at the collector, backfill from stored spans where the raw attributes still exist, and only then change emitters. Doing it in the other order means a window in which old and new spellings both arrive and neither is authoritative, which is precisely the state that produces double-counted spend.

Second, treat the dual-emit window as a dated deprecation with a query that fails when it expires, for example a check that counts spans carrying the retired spelling. A dual-emit window with no failure condition is a permanent fork.

Third, for producers whose identity is not in attributes, close the gap with resource attributes rather than with per-producer dashboard logic. One `service.name` per producer, resolved once at ingest, keeps dashboards producer-agnostic; a dashboard with a producer-specific branch will be forgotten the next time a producer is added.

## Limits of this evidence

Every artifact was checked on one date, 2026-10-31. The Claude Code page is unpinned and beta, so its rows should be re-read before any later citation. The registry files were grepped, not read end to end, and the registry-wide question of whether `gen_ai.system` survives as an alias elsewhere is not settled by these two files. The OpenAI finding is an absence in a span data model, not a measurement of what its OTLP export path finally sends. No live SDK capture was produced for this post and no fleet telemetry was observed, so the join failure here is demonstrated from pinned schemas and fixtures; no failure rate is claimed.

## Choosing a backend is a separate decision

None of the above depends on which backend receives the spans. If the open question is still which one to run, the [LLM observability tools comparison](https://baeseokjae.github.io/posts/llm-observability-tools-comparison-2026/) covers that decision on its own terms. What this post adds is the requirement to bring to that decision: a backend can only join what your producers actually emit, and today's producers do not agree on the key.
