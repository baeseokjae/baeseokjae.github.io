---
cover:
  alt: 'OpenAI Responses API Tutorial 2026: State, Tool Calls, and Cost Boundaries'
  image: /images/openai-responses-api-tutorial-2026.png
  relative: false
date: 2026-04-21 00:11:38+00:00
description: Build a bounded Python Responses API loop, handle tool call IDs and errors, and understand conversation-state billing with reproducible offline checks.
draft: false
schema: schema-openai-responses-api-tutorial-2026
tags:
- openai
- api
- python
- ai-agents
- tutorial
title: 'OpenAI Responses API Tutorial 2026: State, Tool Calls, and Cost Boundaries'
lastmod: '2026-10-20T07:02:10.628622+00:00'
---

The Responses API combines model output with conversation state and tool workflows. The engineering work is in deciding what state to retain, which tool calls to accept, and how to stop a run that cannot finish.

This tutorial includes a small read-only Python example and reproducible offline checks. The checks use a fake transport; they do not establish live model availability, response quality, latency, or cost. Running the optional live example requires an API account and incurs usage.

## Understand state before optimizing cost

`previous_response_id` links a request to earlier response context. It does **not** make that context free: OpenAI's [conversation-state guide](https://developers.openai.com/api/docs/guides/conversation-state.md) says previous input tokens in the chain remain billable as input.

Repeat stable top-level `instructions` on follow-up requests; the prior response ID does not carry them forward automatically. The [migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses.md) also states that the Assistants API sunset occurred on August 26, 2026. New implementation work should use a currently supported API.

Use response usage records and the applicable pricing schedule to measure cost. A shorter request body is a transport convenience, not evidence of reduced billable context.

## Start with a text request

In a dedicated Python environment, install the current OpenAI Python package and record the installed version in your project's dependency lock file. Set `OPENAI_API_KEY` through your normal secret-management mechanism and select a model your account can access in `OPENAI_MODEL`.

```python
import os
from openai import OpenAI

with OpenAI(timeout=30.0, max_retries=0) as client:
    response = client.responses.create(
        model=os.environ["OPENAI_MODEL"],
        instructions="Give a concise explanation for a Python developer.",
        input="What is an idempotency key?",
    )
    if response.status != "completed":
        raise RuntimeError(f"Unfinished response: {response.status}")
    print(response.output_text)
```

`output_text` is a convenience for text output. A tool workflow must inspect the typed output items as well. Do not assume the first output item is a message with text in its first content slot.

## A bounded function-calling loop

Download [responses_example.py](/research/content-quality-2026-10/responses_example.py) and [tool_boundary.py](/research/content-quality-2026-10/tool_boundary.py) into the same directory. The example exposes one synthetic record lookup. It does not execute arbitrary Python functions selected by a model.

The loop performs the following steps:

1. Send the request with a tool declaration and stable instructions.
2. Require a completed response before dispatching a tool.
3. Collect `function_call` items and validate the batch's call identifiers and budget.
4. Dispatch only the allowed tool, using an authenticated tenant supplied by application code.
5. Return each result as `function_call_output` with the original `call_id`.
6. Continue with `previous_response_id`, repeating the instructions, until final text or a configured limit.

This follows the transport described in the [function-calling guide](https://developers.openai.com/api/docs/guides/function-calling.md). Strict schema mode helps constrain the argument shape; the application must still check permissions, resource ownership, and business rules. The demo rejects unknown keys, malformed arguments, missing records, and cross-tenant access.

The example allows at most four API requests and eight tool calls. Those are illustrative application limits, not API limits. A response containing duplicate call IDs fails before dispatch. SDK retries are disabled in the live entry point so an invisible retry policy does not obscure the example's request budget.

## Reproduce the checks without an API key

Also download [cost_calculator.py](/research/content-quality-2026-10/cost_calculator.py) and [verify_examples.py](/research/content-quality-2026-10/verify_examples.py), then run:

```bash
python3 verify_examples.py
```

The [saved run record](/research/content-quality-2026-10/offline-results.json) includes source hashes and the Python version. It confirms call-ID correspondence, repeated instructions, request and tool budgets, rejection of duplicate IDs, incomplete-response handling, and the empty-text stopping path. The boundary fixture separately passes twelve deterministic cases.

These checks can catch application regressions. They do not call OpenAI, verify an account's model access, or measure model compliance. Add a small authenticated smoke test in your own environment before relying on the integration.

## State, streaming, and failure handling in a real service

The downloadable live example sets `store=True` and uses synthetic records. Before sending real user data, review OpenAI's [data controls](https://developers.openai.com/api/docs/guides/your-data.md) and choose a compatible retention and state strategy.

For streaming, the [streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses.md) documents events such as `response.output_text.delta` and `response.completed`. Do not wait for an invented `response.done` event or treat a partial text delta as successful completion.

## Production checklist

Associate conversation state with both the authenticated user and a conversation identifier. Serialize concurrent writes or use version checks so simultaneous turns cannot overwrite each other's state. Store only the identifiers and records your retention policy permits.

Handle refusal, incomplete output, timeout, rate limits, and tool failure as distinct outcomes. A timeout does not prove a side effect failed; write-capable tools need idempotency and reconciliation. A model's final sentence is not your transaction log.

Keep an API-compatible endpoint configured at its documented API root. Do not append `/responses` to a client's base URL and expect it to behave as a normal root. Compatibility with one endpoint also does not establish support for hosted tools, storage, or every Responses feature.

## Revision note

**Updated October 20, 2026.** Corrected the false claim that previous_response_id makes earlier context free, the streaming completion event, unsafe output indexing, and blanket schema guarantees. Replaced the earlier examples with a bounded read-only loop and an explicit offline verification record.

## Primary sources

Checked October 20, 2026: [responses state](https://developers.openai.com/api/docs/guides/conversation-state.md); [responses migration](https://developers.openai.com/api/docs/guides/migrate-to-responses.md); [responses functions](https://developers.openai.com/api/docs/guides/function-calling.md); [responses data](https://developers.openai.com/api/docs/guides/your-data.md); [responses stream](https://developers.openai.com/api/docs/guides/streaming-responses.md).
