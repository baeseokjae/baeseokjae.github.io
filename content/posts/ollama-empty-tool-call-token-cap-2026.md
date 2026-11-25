---
title: "Ollama Returns an Empty Response? Check the Token Limit"
date: 2026-11-08T22:05:00+00:00
description: "A tool-calling turn can return HTTP 200 with empty content and no tool_calls: the token cap fired mid-call. Read done_reason=length, and why raising the cap did not help here."
draft: false
schema: "schema-ollama-empty-tool-call-token-cap-2026"
cover:
  image: /images/ollama-empty-tool-call-token-cap-2026-presentation.png
  alt: 'Conceptual checklist for an empty tool-call response: HTTP 200 with empty content, then inspect the stop reason, then check the token usage. Raising the token cap is not a guaranteed fix.'
  caption: 'Raising the token cap is not a guaranteed fix. Conceptual illustration; see article for evidence and limits.'
  relative: false
  hidden: false
images:
  - /images/ollama-empty-tool-call-token-cap-2026-presentation.png
lastmod: '2026-11-25T14:55:56+00:00'
tags:
  - ollama done_reason length
  - ollama empty response
  - tool_calls empty
  - num_predict
  - max_tokens
  - openai compatible ollama
  - local llm agent loop
  - function calling truncation
  - ollama api chat
  - qwen2.5 tool calling
---

An agent sends a request with a `tools` array and a modest output cap. The server answers HTTP 200, the body parses, and the assistant message is empty: `content` is `""`, `tool_calls` is absent, and no error field explains it. The loop logs "model returned no content", retries the identical request, and the next turn is empty in the same way. The operator starts suspecting the model, the quantisation or the chat template, because nothing in the client raised an exception.

The response already contains the diagnosis. Read the stop reason and the token count before anything else: `done_reason` is `"length"` on the native `/api/chat` surface, `finish_reason` is `"length"` through `/v1/chat/completions`, and `eval_count` (native) or `usage.completion_tokens` (compatible surface) equals the cap that was set. The cap fired while the model was still emitting its tool-call preamble. In the chat handler a parsed call is emitted when the parser closes it: it is attached to the streaming chunk that completed it, or to the aggregated non-streaming response once generation is over. A call still incomplete when generation ends is never emitted at all, because the final chunk carries only whatever text the parser was holding outside the call. So the partial call is dropped rather than returned, and the response looks like an ordinary completed turn with nothing in it.

That is the whole diagnostic, and it fits in one response. The rest of this article is the fixture that produced it, the server code path behind it, and a negative result that matters for the obvious fix: on this fixture, raising the cap from 8 to 64 tokens did not restore the call.

## The fields that separate a truncated call from a finished turn

Both surfaces expose the same state with different names. The native handler returns `done_reason` and `eval_count`; the OpenAI-compatible handler maps `max_tokens` onto the same internal cap and returns `finish_reason` plus `usage`. The tools documentation for [Ollama v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/docs/api.md) shows the normal shapes of a streamed and a final `/api/chat` response, and the [OpenAI-compatibility page](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/docs/api/openai-compatibility.mdx) lists `max_tokens` and `tools` as supported parameters.

| What to read | Native `POST /api/chat` | `POST /v1/chat/completions` |
|---|---|---|
| why generation stopped | `done_reason` | `choices[0].finish_reason` |
| tokens actually generated | `eval_count` | `usage.completion_tokens` |
| call present | `message.tool_calls` | `message.tool_calls` |
| the limit you set | `options.num_predict` | `max_tokens` |

Three combinations are worth memorising, because they lead to different actions:

- `length` plus a token count equal to your cap: the cap fired. Any partial call was dropped. This is the case measured here.
- `stop` with a non-empty `content` and no `tool_calls`: the model answered in prose instead of calling a tool. Raising the cap will not change that.
- `tool_calls` present: a call was parsed and returned. Whatever goes wrong after this is argument or client-side validation, not truncation.

The `num_predict` option is documented in the [v0.20.3 Modelfile reference](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/docs/modelfile.mdx) as the maximum number of tokens to predict, defaulting to `-1` for unbounded generation. The cap in a failing request is therefore the caller's own number, not a hidden model limit.

## What the measured run shows

The fixture is deliberately small and boring: `qwen2.5:0.5b` (Q4_K_M, 397 MB, 4096-token context) on Ollama 0.20.3, one `create_ticket` tool schema with three required fields (`title`, `priority` as an enum, `summary`), temperature 0, seed 7. Two prompt variants were used: A with a long operator preamble and a detailed customer message, B with a one-sentence preamble and a short request. Caps of 8, 16, 24, 32, 40 and 48 tokens were requested on both variants and both API surfaces, five repetitions per cell, with one extra repetition in the native variant-A cell at cap 24 and one further cell at 64 on the native surface. The run recorded 129 requests in total. The table below counts every request per cap, so its rows already include the two native streaming cells at caps 16 and 48; the remaining 127 requests are the graded cells.

| Cap | Requests | Empty content, no `tool_calls` | Complete calls | Stop reason |
|---|---|---|---|---|
| 8 | 20 | 20 | 0 | `length` |
| 16 | 21 | 21 | 0 | `length` |
| 24 | 21 | 21 | 0 | `length` |
| 32 | 20 | 20 | 0 | `length` |
| 40 | 20 | 20 | 0 | `length` |
| 48 | 21 | 21 | 0 | `length` |
| 64 | 5 | 5 | 0 | `length` |
| 96 | 1 | 0 | 1 | `stop` |

Every request at caps 8 through 64 returned HTTP 200 with `content` of length zero, no `tool_calls`, and a stop reason of `length`. On the native surface `eval_count` equalled the cap in every one of those requests; on the compatible surface `usage.completion_tokens` equalled `max_tokens` in all 60 compatible requests. The empty message is not a client serialisation artefact: the same state appears in the raw JSON body, on both surfaces, with the token accounting that proves generation happened.

The single exception in the log is one request at 96 tokens on the native surface with variant A: a complete `create_ticket` call, `done_reason` `"stop"`, `eval_count` 95. It is one observation, not a boundary. No repetition was made at 96, variant B was not tested there, and the compatible surface never reached a complete call inside the tested range. Treat it as evidence that the fixture can complete at a larger cap, not as a value to copy.

## Why the content is empty rather than truncated

The intuitive model of a token cap is "the answer gets cut off", and for plain text that is what happens: you receive a partial sentence. With a `tools` array the observable is different, because a partial tool call has nowhere to go in the response schema.

In the chat handler of [`server/routes.go` at v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/server/routes.go), the branch that runs when the request carries a `tools` array hands each chunk to the tool parser (`toolCalls, content := toolParser.Add(res.Message.Content)`, line 2493). When the parser closes a call, that branch attaches the calls to the chunk that completed them and empties the content (`res.Message.ToolCalls = toolCalls; res.Message.Content = ""`, lines 2496-2501). When it has not closed one, the final chunk carries whatever text the parser is still holding and nothing else - `if r.Done { res.Message.Content = toolParser.Content(); ch <- res }`, lines 2513-2515 - and a non-streaming call then attaches the collected calls only when at least one closed call was parsed: `if len(toolCalls) > 0 { resp.Message.ToolCalls = toolCalls }`, lines 2608-2610. A generation stopped at the cap still reports done, but an unterminated call never becomes an entry in that slice, so the attachment is skipped and the message goes out with empty content. (The older `/api/generate` path applies the same rule in `GenerateHandler` with a different field, `if cr.Done && len(toolCalls) > 0 { res.ToolCalls = toolCalls }` at lines 584-585; every measurement in this article is on the chat path, where `/api/chat` and the `/v1/chat/completions` wrapper are both served by `ChatHandler`.) The response that reaches the client is a normal completion carrying an empty `content` string and no `tool_calls`. Nothing in that payload is marked as an error, because from the server's point of view nothing failed: the client's limit was honoured exactly.

The compatible layer inherits the same shape. In [`openai/openai.go` at v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/openai/openai.go), `max_tokens` is copied into the internal `num_predict` option, and for a non-streaming response the finish reason is rewritten to `tool_calls` only when the response actually carries tool calls; otherwise the underlying `done_reason` string is returned unchanged. Streaming applies the same rule in `toChunk`, which reports `tool_calls` when the chunk itself carries calls or when an earlier chunk already sent one (`toolCallSent`), so the rewrite tracks calls having been emitted rather than calls present in the final message alone. A dropped partial call therefore keeps `finish_reason: "length"` instead of being rewritten into something a client might notice.

This is why the failure is so quiet in an agent loop. A text-generation client that checks only for empty content can treat the turn as a no-op; a tool-calling client that checks only for `tool_calls` sees "no call" and often assumes the model chose not to act. The stop reason is the field that separates those cases, and it is present in every response.

## The negative result: raising the cap did not fix it on this fixture

The obvious remedy is to raise the limit. On this fixture it did not work over an eightfold range. Twenty graded runs at 48 tokens - five per cell across the two prompt variants and the two surfaces - plus the one streaming request at that cap produced zero complete calls, and five runs at 64 on the native surface also produced zero. The first and only complete call in the log came at 96 tokens, in a single run.

Two readings of that result are tempting and both are wrong. The first is that 96 is the required cap; with n=1 and one variant it supports no such constant, and the same schema on another model or template will spend a different number of tokens before the call closes. The second is that the cap value is irrelevant, which over-reads a single model. What the run does establish is narrower and still useful: the empty state is stable from 8 to 64 tokens, so a retry loop that bumps the cap by a small increment will keep producing identical empty turns while burning time, and a diagnostic that relies on "it will work with a bigger number" has no measured basis here.

The practical consequence is to stop treating the cap as the variable to tune and treat the empty response as the signal to inspect. If the stop reason is `length`, the request needs a different shape - a shorter preamble, a smaller schema, or a generation budget sized to the template - not the same request submitted again with a larger number.

## A check you can run on one response

The detection step needs no server logs and no framework instrumentation. Take the response object your client already has, pass in the cap you sent, and check the three fields together:

```python
def capped_without_call(resp, cap, native=True):
    """cap is the limit you sent, not a field the server echoes back."""
    if native:
        reason, tokens = resp.get("done_reason"), resp.get("eval_count")
        message = resp.get("message") or {}
    else:
        choice = (resp.get("choices") or [{}])[0]
        reason, tokens = choice.get("finish_reason"), (resp.get("usage") or {}).get("completion_tokens")
        message = choice.get("message") or {}
    return (reason == "length"
            and not message.get("content")
            and not message.get("tool_calls")
            and cap is not None and tokens == cap)
```

`cap` is an argument because the response does not carry it. In [`api/types.go` at v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/api/types.go), `ChatResponse` (line 534 onward) has no `options` field - `Options` is declared on `ChatRequest` (line 168) - and the compatible body exposes `usage.completion_tokens` but never `max_tokens`, so the limit has to come from the request you sent and be compared against the token count the server reports. Pass the `num_predict` value you set, or the `max_tokens` you passed to the wrapper; the two are the same number after the mapping described above.

The predicate is a reading aid, not a fix: it tells you that the cap fired and the call was dropped. Log `done_reason`, `eval_count` and the configured cap on every turn, not only on errors, so the state is visible the first time it happens rather than after a retry storm. When the predicate is true, do not resubmit the identical request; change the prompt or the budget first, or surface the state to the operator.

Two neighbours are worth reading alongside this one. The [Ollama API integration guide](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/) covers the request and response fields this article relies on, and the [function-calling guide](https://baeseokjae.github.io/posts/llm-function-calling-tool-use-guide-2026/) explains `finish_reason` as the signal for detecting a call; this piece is the case where that signal reads `length` instead. For the prompt-side failure that looks similar but is not the same, the [context-truncation diagnosis](https://baeseokjae.github.io/posts/ollama-silent-context-truncation-2026/) covers a prompt that is cut before generation starts, and the [concurrent-session logging checklist](https://baeseokjae.github.io/posts/local-llm-concurrent-agent-sessions-2026/) already names `length` plus `num_predict` as the stop signal for text turns, though not for a discarded tool call. Readers running the same loop against a different engine can compare the parser behaviour in the [vLLM streaming tool-call case](https://baeseokjae.github.io/posts/vllm-streaming-tool-call-parser-corruption-2026/), and the [local agent guide](https://baeseokjae.github.io/posts/local-ai-agents-guide-2026/) covers the retry structure in which one empty turn becomes a stall.

## Fixture, reproduction and limits

The run used two stdlib `urllib` scripts against the local daemon at `127.0.0.1:11434`, no SDK. Each request recorded the HTTP status, wall time, content length, presence of `tool_calls`, JSON-parseability of the arguments and whether every required key was present, plus `done_reason`/`finish_reason` and `eval_count`/`usage.completion_tokens`. The graded table, the raw request log, the environment capture and the method note are kept with the draft as a private local author verification; they are not offered here as a downloadable dataset or a reusable harness, so no reader-access promise is made for those files. The fixture is described completely enough to rebuild: one model tag, one tool schema, two prompts, one sampling setting, and the caps listed above.

The limits are the honest part of this result. It is one host (2 vCPU, recorded load average 4.64 before the sweep and 3.47 and 2.73 at two in-run checkpoints), one model, one quantisation, one tool schema, two prompt variants, and 129 requests. Requests went to a shared local daemon rather than a dedicated server instance, so wall times are provenance only and no throughput or latency claim is drawn from them. The single 96-token completion is one run on one variant, and no boundary is asserted across variants or surfaces. Nothing here measures how often this happens across models, and no prevalence figure is implied. What is supported is the diagnostic: a `length` stop with a token count equal to the cap and an empty message is the signature of a capped generation whose partial tool call was discarded, and on this fixture raising the cap across an eightfold range did not restore the call.
