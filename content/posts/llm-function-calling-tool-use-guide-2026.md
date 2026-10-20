---
cover:
  alt: 'LLM Function Calling and Tool Use: Provider Mapping and Safe Execution'
  image: /images/llm-function-calling-tool-use-guide-2026.png
  relative: false
date: 2026-04-27 14:36:31+00:00
description: Map OpenAI, Claude, and Gemini tool-call protocols, validate arguments and authorization, and reproduce an offline application-boundary check.
draft: false
schema: schema-llm-function-calling-tool-use-guide-2026
tags:
- llm function calling
- tool use
- OpenAI
- Anthropic
- Google Gemini
- AI agents
- production
title: 'LLM Function Calling and Tool Use: Provider Mapping and Safe Execution'
lastmod: '2026-10-20T07:02:10.628622+00:00'
---

Function calling gives your application a structured proposal to run a tool. For a custom client-side function, your code decides whether to execute it and returns the result. The important production boundary is that decision, not whether the generated arguments look like valid JSON.

This guide maps the protocols and supplies a small application-boundary example. Provider-hosted tools have different execution responsibilities; do not treat every tool as a local Python callback.

## Keep each provider's call and result pair intact

| API surface | Model-side request | Application result correspondence |
|---|---|---|
| OpenAI Responses custom function | `function_call` item with name, arguments, and call ID | `function_call_output` carrying the same `call_id` |
| Claude Messages client tool | `tool_use` block with ID, name, and input | `tool_result` referencing `tool_use_id` |
| Gemini Interactions function | `function_call` step | `function_result` referencing `call_id` |

Sources: [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling.md), [Claude tool-call handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls), and [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling). The Gemini row refers to the Interactions examples in the current documentation; do not paste those envelopes into a different API surface.

Claude's client-tool results belong immediately after the corresponding tool-use turn, with result blocks before any additional text in that user message. Preserve all required identifiers and typed items when adapting a conversation between providers.

## Validate three different things

**Shape:** Does the tool name exist, and do the arguments have the expected fields and types? Reject unexpected fields. Be careful with language-specific type behavior, such as Python treating Boolean values as integers.

**Authority:** May the authenticated requester perform this action on this resource? Derive identity from the application session. A model-supplied tenant, user ID, or claim of approval is data, not proof of permission.

**Intent and effect:** Is the requested operation within the user's task, and what will actually change? For side effects, bind confirmation to the concrete action, use an idempotency key, and reconcile uncertain results before retrying.

Keep these checks separate in logs. A schema failure, an authorization denial, and a failed downstream service require different fixes.

## Run a read-only boundary example

Download [tool_boundary.py](/research/content-quality-2026-10/tool_boundary.py). It exposes one synthetic record lookup and accepts only `record_id` in the generated arguments. The tenant is supplied by trusted application code.

```bash
python3 tool_boundary.py
```

The [execution record](/research/content-quality-2026-10/offline-results.json) shows twelve deterministic cases passing. Two valid reads succeed; requests including a cross-tenant record, forged tenant argument, unknown tool, wrong type, and malformed JSON are rejected. A shared error is used for unavailable and unauthorized records.

The fixture demonstrates application behavior under specific inputs. It contains no live model request, so it does not measure a provider's tool-selection accuracy or resistance to prompt injection.

## Bound the loop, including failures

Set limits before starting the run: total requests, tool calls, elapsed time, and allowed spend. Count unsuccessful attempts. Validate an entire parallel batch before dispatch so a duplicate identifier or excessive batch cannot partially execute.

The [Responses tutorial](/posts/openai-responses-api-tutorial-2026/) includes a bounded example with mock tests. It returns each tool result to the matching call and stops on incomplete responses, missing final text, and exhausted budgets.

For a write-capable tool, retry policy needs more care than a read-only example. After a network timeout, query the operation status using the same application request identifier. Do not create a fresh operation simply because the model asked again.

| Failure | Application response |
|---|---|
| Unknown function | Reject; never resolve arbitrary names through `eval` or dynamic imports |
| Invalid arguments | Return a bounded structured error without secrets |
| Access denied | Stop that action; do not try a more privileged identity |
| Downstream timeout | Reconcile state before retrying a side effect |
| Repeated unsuccessful calls | Stop at the budget and explain the unresolved task |
| Tool output contains instructions | Keep it as untrusted data; do not promote it into system guidance |

## Parallelism has a workload-dependent benefit

If independent tools take three and five seconds, their sequential waiting time is eight seconds; perfect parallel scheduling reduces that component to five seconds. Model time, queueing, validation, and aggregation still add latency. Dependencies or rate limits can remove the advantage.

Measure the complete workflow with the same task and success criteria. A published acceleration result for one execution system does not justify a universal multiplier for all function-calling applications.

## Revision note

**Updated October 20, 2026.** Removed unsupported universal speed and token-overhead claims. Replaced mixed provider assumptions with a named-API mapping, explicit authorization boundaries, failure handling, and an executed offline fixture.

## Primary sources

Checked October 20, 2026: [responses functions](https://developers.openai.com/api/docs/guides/function-calling.md); [claude tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls); [gemini functions](https://ai.google.dev/gemini-api/docs/function-calling).
