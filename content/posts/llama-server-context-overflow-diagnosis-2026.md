---
date: 2026-10-30 06:16:38+00:00
description: Four different llama.cpp server mechanisms produce a dead or damaged agent turn at the context line. Here is how to tell them apart from the error payload, the finish_reason and the server log, and how to attribute the overflow to a named section of your prompt.
draft: false
lastmod: '2026-10-30T06:16:38+00:00'
schema: schema-llama-server-context-overflow-diagnosis-2026
tags:
- llama-cpp
- llama-server
- context-window
- local-llm
- ai-agents
- debugging
title: 'llama-server Context Overflow: Reading the "exceeds the available context size" Error and Finding Which Part of Your Agent''s Prompt Caused It (2026)'
---

An agent that has been working against a self-hosted llama.cpp server for twenty or forty turns eventually stops working, and the symptom is almost never specific enough to act on: a half-written answer, an empty completion, a tool call that never arrives, or a request that never gets a reply at all. The tempting response is to raise `-c`, which is exactly the fix that KV memory may not allow, and which does nothing for the two of the four failure modes below that are not really about running out of room.

This article maps four distinct mechanisms in the server, each with the source location that produces it, and then gives a procedure for attributing the overflow to a named section of the request. Everything here is read from `tools/server` at a pinned commit plus upstream reports; the companion question of which advertised window a model actually supports is covered separately in the [context-window comparison](https://baeseokjae.github.io/posts/llm-context-window-comparison-2026/), and where llama-server sits among other local servers is covered in the [serving-framework survey](https://baeseokjae.github.io/posts/local-ai-model-serving-frameworks-2026/).

The code citations below are against commit `369dcf309c8b274370e692ac2d42d9708597ae04` (2026-10-29). `server-context.cpp` at that commit is byte-identical to the same file at the `v0.8.0` release tag target `8642541b255bfb5dc39cd351a178be09013a55d6` (sha256 `26acff2657377779f0b48317c043c97b6e9022eaf89d8d956d8ae2a8b2e6e38d`, 304170 bytes), so the shift logic described in Outcome 3 is shipped behaviour rather than unreleased master. Byte equality of one file is not proof that a released binary behaves identically, but it does rule out the possibility that the tag predates this code.

## The four ways a turn dies at the context line

| Outcome | What the client sees | Where it comes from | What tells it apart |
| --- | --- | --- | --- |
| Arrival rejection | an error before any token; `n_prompt_tokens` and `n_ctx` in the body | request-size check on admission | the error message itself |
| Clean limit stop | text ending mid-sentence, `finish_reason: "length"` | generation-side capacity check | `finish_reason` alone cannot distinguish it from a `max_tokens` cut |
| Middle-slice shift | no error; generation continues over a prompt with a slice removed | `--context-shift` compaction | the `slot context shift` warning's `n_keep`, which fixes where the hole is |
| Checkpoint re-prefill | slow but correct; nothing overflows | checkpoint invalidation on hybrid, recurrent and SWA models | `prompt_n` on every turn |

Match your symptom to a row before you change a flag. Two of the four rows are silent, which is why "the model got dumber after twenty turns" and "the server rejected my request" are sometimes the same problem and sometimes not.

## Outcome 1: the request is rejected before a single token

On the chat path the server compares the tokenised request against the slot's context size on admission and refuses anything at or above the limit, in `server-context.cpp` around line 4081:

```
if (slot.task->n_tokens() >= slot.n_ctx) {
    send_error(slot, string_format("request (%d tokens) exceeds the available context size (%d tokens), try increasing it", ...),
               ERROR_TYPE_EXCEED_CONTEXT_SIZE);
    slot.release();
```

Three details matter when you are reading your own logs. The comparison is `>=`, not `>`, so a prompt exactly equal to `n_ctx` is rejected. The slot is released before decoding, so nothing was generated and no partial answer exists to inspect. And this branch only applies to prompts the scheduler is allowed to split: a task that must be processed in one batch — an embedding-style request, a reranker whose pooling is not `LAST`, a decision over a non-causal context — takes the parallel branch above it, which uses a strict `>` test and different wording, "input (N tokens) is larger than the max context size (M tokens). skipping". That is why grepping for the chat message turns up nothing on an embeddings endpoint, and why the two messages are not interchangeable.

The rejection is at least self-diagnosing, because the error object carries the two numbers that define the gap. In `server-task.cpp` the error serializer adds them only for this error type:

```
if (err_type == ERROR_TYPE_EXCEED_CONTEXT_SIZE) {
    res["n_prompt_tokens"] = n_prompt_tokens;
    res["n_ctx"]           = n_ctx;
}
```

So the useful log line from a client is not "context exceeded" but the pair of numbers: if `n_prompt_tokens` is 1.2× `n_ctx` you have a prompt-building bug (a re-injected reasoning block, a tool schema repeated per turn, a transcript that grows without bound), and if it is 1.01× you have a near-miss that a small history cap will fix. Upstream has both shapes: a report of a prompt at roughly three times the configured window being accepted and then hard-failing ([#28848](https://github.com/ggml-org/llama.cpp/issues/28848), closed as not planned on 2026-10-29), and reports of long interactions simply stopping ([#19636](https://github.com/ggml-org/llama.cpp/issues/19636), closed as duplicate). The request to truncate history server-side instead of returning an error was filed in November 2025 and closed without the behaviour changing ([#17284](https://github.com/ggml-org/llama.cpp/issues/17284)).

## Outcome 2: generation stops and the stream says "length"

If the prompt fits at admission but the answer would push past the window, the interesting thing happens during generation. With context shift at its default — disabled — `process_token` checks capacity after each token and, on running out, marks the slot rather than raising an error:

```
if (!params_base.ctx_shift && slot.prompt.n_tokens() + 1 >= slot.n_ctx) {
    slot.truncated      = true;
    slot.stop           = STOP_TYPE_LIMIT;
    slot.has_next_token = false;
```

There is also a later guard in `pre_decode` that sends `send_error(slot, "context shift is disabled", ...)` if generation somehow reaches the boundary, and the source labels it as redundant: "we should never get here, because generation should already stopped in process_token()". So the common case is a clean stop rather than a broken connection, and the only trace it leaves in the stream is the finish reason discussed next.

The clean stop is where the diagnosis gets hard, because the OpenAI-compatible chat stream collapses the cause. In `to_json_oaicompat_chat_stream()` the finish reason starts at `"length"` and is only replaced when the stop was a stop-word or end-of-sequence:

```
std::string finish_reason = "length";
if (stop == STOP_TYPE_WORD || stop == STOP_TYPE_EOS) {
    finish_reason = oaicompat_msg.tool_calls.empty() ? "stop" : "tool_calls";
}
```

Everything that is not a word or an EOS — including the capacity limit above — reports `"length"`. The two fields that would name the cause, `truncated` and `stop_type`, exist only in the native `/completion` serializer `to_json_non_oaicompat()`, which is not what an OpenAI-compatible chat client receives. The practical consequence is blunt: on the `/v1/chat/completions` path, `finish_reason: "length"` cannot tell you whether the server ran out of context or your client's `max_tokens` was simply too small. The discriminator has to come from elsewhere — a `n_prompt_tokens` versus `n_ctx` comparison on the next request, the server stdout, or the native endpoint during a debugging session.

## Outcome 3: --context-shift deletes a hole, not the tail

Enabling context shift does not make the server truncate the oldest turns, nor the newest: it deletes one contiguous slice at a position set by `n_keep`, then continues. The whole block is worth reading because the default is the variant that lands at the front of your prompt:

```
int n_keep = slot.task->params.n_keep < 0 ? slot.task->n_tokens() : slot.task->params.n_keep;

if (add_bos_token) {
    n_keep += 1;
}

n_keep = std::min(slot.n_ctx - 4, n_keep);
const int n_left    = slot.prompt.n_tokens() - n_keep;
int       n_discard = slot.task->params.n_discard ? slot.task->params.n_discard : (n_left / 2);
n_discard = std::clamp(n_discard, 0, std::max(0, n_left - 1));
SLT_WRN(slot, "slot context shift, n_keep = %d, n_left = %d, n_discard = %d\n", n_keep, n_left, n_discard);
slot.mem.seq_rm (slot.id, n_keep            , n_keep + n_discard);
slot.mem.seq_add(slot.id, n_keep + n_discard, slot.prompt.tokens.pos_next(), -n_discard);
```

Read the default literally, because it decides *where* the hole lands, and the answer is the one nobody expects. The field `n_keep` defaults to `0` — the [README](https://raw.githubusercontent.com/ggml-org/llama.cpp/369dcf309c8b274370e692ac2d42d9708597ae04/tools/server/README.md) says "By default, this value is set to `0`, meaning no tokens are kept. Use `-1` to retain all tokens from the prompt", and `common.h` initialises `n_keep = 0` on the params struct — so a request that omits the field arrives with zero. The ternary takes the `else` arm and keeps 0, or 1 when the chat template sets `add_bos_token` and the BOS token is added immediately after the branch. `n_left` is then the whole prompt, `n_discard` defaults to half of it, and `seq_rm` removes `[0 or 1, n_discard)`: the head of the request goes first. In an agent request that means the system message and the tool schemas at position zero, then the oldest turns in order. On a prompt that is mostly history, your agent loses its instructions before it loses its oldest tool output, and what continues to be generated is an answer the model is no longer being told how to format.

The other two settings move the boundary, and they are the ones people assume are the default. `n_keep = -1` is the explicit keep-all variant: the ternary substitutes `slot.task->n_tokens()`, the entire incoming request, so `n_left` is only what has been generated since admission and the removed range `[n_keep, n_keep + n_discard)` starts exactly at the end of the request. The first half of the answer already streaming to your client is deleted while the conversation in the request survives intact; nothing in the request is touched, but the text you already showed the user no longer corresponds to the state the model continues from.

An explicit positive keep count is the third case, and the only one that gives a middle-of-history slice. With `n_keep` set to a value smaller than the prompt — the `--keep N` flag or the request field — everything up to `n_keep` survives, the next `n_discard` tokens of history are removed, and the tail of the conversation is kept. That is the configuration where an agent loses the middle of its transcript and keeps answering plausibly, with the system prompt and tool schemas still in place.

Nothing in the stream announces any of the three. The only artefact is the `slot context shift, n_keep = ..., n_left = ..., n_discard = ...` warning on the server's stderr, and the three numbers tell you which variant you got: an `n_keep` of 0 or 1 means the deleted range began at the head of the prompt, an `n_keep` close to the size of the request means it began inside the generated text, and a value between the two means it began in the history.

Two configurations refuse to shift at all rather than shift badly. A task with more than one completion — `n_cmpl > 1` — becomes a parent task plus child slots launched by `launch_slots_with_parent_task()` (`server-context.cpp` lines 2674-2710 in the same file), which share one prompt; the guard `if (slot.task->is_parent() || slot.task->is_child())` at lines 3784-3786 rejects either of them with `send_error(slot, "context shift cannot be used for shared prompt", ...)`. A multimodal context aborts with `not supported by multimodal` if the auto-disable path is ever bypassed. Context shift is not a safety net for shared-prompt multi-completion requests, nor for vision models.

## Outcome 4: nothing overflows and it is still slow

The fourth mechanism does not involve overflow at all, and mistaking it for one is expensive because the fix is the opposite of raising `-c`. On hybrid and recurrent architectures the context checkpoints that make incremental prefill possible are invalidated, and on `/slots` restore they are not persisted, so the server reprocesses the whole prompt every turn while the numbers stay comfortably inside the window. Three upstream reports cover the parts: checkpoints always invalidated on hybrid/recurrent models ([#24055](https://github.com/ggml-org/llama.cpp/issues/24055)), no KV reuse from `/slots` restore on hybrid/recurrent and sliding-window models because checkpoints are not serialised ([#28194](https://github.com/ggml-org/llama.cpp/issues/28194)), and no checkpoint created at the end of the system prompt, so a client that renders its own prompts re-prefills where a client that lets the server render does not — the reporter compares `prompt_n` of 1214 against 9 for the same content ([#30783](https://github.com/ggml-org/llama.cpp/issues/30783)). All three are issue reports, not measurements reproduced here.

The discriminator is `prompt_n` in the response `timings`, or the per-turn timing block in the server log. Stable `prompt_n` near the size of the newly added content means reuse is working. `prompt_n` growing with the length of the whole conversation means every turn is a cold prefill, and the answer is a prompt-cache or architecture problem, not a context-size problem.

## Attributing the window to a named section of your prompt

Once you know which outcome you hit, the next question is which part of the request consumed the window, because "raise `-c`" is not available when the KV cache is what is binding. A cheap way to answer it is to tokenise the request yourself, per section, and compare against the server's own `n_ctx` from `GET /props`.

Capture one real request body from your client — the exact JSON that the agent sends, tools array included — and run it through the tokenizer for the same model:

```
curl -s http://127.0.0.1:8080/props | jq '{n_ctx: .default_generation_settings.n_ctx}'
curl -s http://127.0.0.1:8080/tokenize -d @request.json | jq '.tokens | length'
```

Then split the body and repeat: the `tools` array alone, the `messages` array, and the `messages[*].content` of each assistant turn that carries a reasoning echo. The expected ranking is tool JSON schemas and accumulated history ahead of the system prompt, but the ratios differ enough between frameworks that guessing is unreliable, and the only way to see the section you did not think of is to count it.

Two rules make the count trustworthy. Use the tokenizer the server uses, not an approximation from a different model family, or the per-section split will be right in relative terms and wrong in the absolute terms you need against `n_ctx`. And keep the request you measured: if you later trim a section and the total does not drop by roughly the amount you removed, your client is rebuilding the payload, and the number you measured is not the number the server received.

For per-turn accounting across a whole run rather than one request, the trajectory-monitor approach in [agent trajectory monitoring for tool calls and token spend](https://baeseokjae.github.io/posts/agent-trajectory-monitor-tool-calls-token-spend/) records the same numbers over time, which is what distinguishes a prompt that grows linearly from one that grows per tool call.

## What to change before you raise -c

Order the fixes by cost, not by comfort. The cheapest change is the one that does not touch the server at all.

Cap history at a section boundary your agent understands — a completed tool call, not an arbitrary token offset — so the truncation you perform is one you can reason about. Prune the tool schemas the current turn cannot use; a large tool surface is resent on every request and is invisible in a transcript. Treat `--context-shift` as a setting that needs a deliberate `--keep`: with the request default `n_keep` of 0 the shift deletes the leading slice, system message and tool schemas first, while `--keep -1` protects the whole request and puts the hole inside the answer you are streaming, and only an explicit positive keep-region that covers the system prompt and the tool schemas makes the deletion land on older turns instead. Only then look at `-c`: the README documents `-c` as defaulting to 0 (take the model's own training context), `--context-shift` as disabled by default, and `--kv-unified-per-slot N` as sizing the shared pool to `n_parallel * N` when `-c` is unset, which is the flag that makes per-slot limits predictable when you run several agents against one process. Context checkpoints default to 32 with a minimum spacing of 8192 tokens, so on a model with a long prompt and no checkpoint at the system-prompt boundary, raising `-c` buys memory pressure without buying reuse.

The client-side half of this — what to keep in a working set, when to compact — is covered in [context engineering for coding agents](https://baeseokjae.github.io/posts/context-engineering-ai-coding-agents-2026/) and in the [token-waste reduction guide](https://baeseokjae.github.io/posts/coding-agent-token-waste-reduction-guide-2026/). This article is deliberately only about what the server does when you cross the line, which is a different question from what you should have sent.

## What the server does and does not tell you

The contract, as read at the pinned commit:

- Arrival rejection is explicit and carries `n_prompt_tokens` and `n_ctx`.
- A generation-time capacity stop on the OpenAI-compatible chat stream is reported as `finish_reason: "length"`, indistinguishable from a `max_tokens` cut.
- The native `/completion` response adds `truncated` and `stop_type`, which is why a one-off reproduction against `/completion` is worth the trouble when the chat path is ambiguous.
- `--context-shift` reports itself only as a `slot context shift, n_keep = ..., n_left = ..., n_discard = ...` warning on stderr, and the values are the only way to know whether the discard landed in the request or in the generated text.
- Checkpoint behaviour is not surfaced at all except through `prompt_n` and the timing block.

The closing caveat is the one that costs people days: a clean stream is not proof of an intact prompt. Outcome 2 and Outcome 3 both produce plausible text, and only the log distinguishes "the model gave a short answer" from "the server deleted a slice of the prompt, or of the answer, and kept going".

Upstream may change any of this; the behaviour described here is pinned to the commit named above, and between `369dcf30` and the later master `36a0e2ffc0b352b774f8d71c43668b75b3061ef5` the shift block and the admission test were unchanged, so no safe tail truncation landed in that window either.

### Primary sources

- `tools/server/server-context.cpp` at 369dcf30 — https://raw.githubusercontent.com/ggml-org/llama.cpp/369dcf309c8b274370e692ac2d42d9708597ae04/tools/server/server-context.cpp
- `tools/server/server-task.cpp` at 369dcf30 — https://raw.githubusercontent.com/ggml-org/llama.cpp/369dcf309c8b274370e692ac2d42d9708597ae04/tools/server/server-task.cpp
- server README (flag defaults) at 369dcf30 — https://raw.githubusercontent.com/ggml-org/llama.cpp/369dcf309c8b274370e692ac2d42d9708597ae04/tools/server/README.md
- `common/common.h` (the `n_keep = 0` default on `common_params`) at 369dcf30 — https://raw.githubusercontent.com/ggml-org/llama.cpp/369dcf309c8b274370e692ac2d42d9708597ae04/common/common.h
- same file at later master 36a0e2ff — https://raw.githubusercontent.com/ggml-org/llama.cpp/36a0e2ffc0b352b774f8d71c43668b75b3061ef5/tools/server/server-context.cpp
- same file at v0.8.0 tag target 8642541b — https://raw.githubusercontent.com/ggml-org/llama.cpp/8642541b255bfb5dc39cd351a178be09013a55d6/tools/server/server-context.cpp
- upstream reports, states as fetched on 2026-10-30: [#17284](https://github.com/ggml-org/llama.cpp/issues/17284) (closed), [#19636](https://github.com/ggml-org/llama.cpp/issues/19636) (closed), [#25566](https://github.com/ggml-org/llama.cpp/issues/25566) (closed), [#28848](https://github.com/ggml-org/llama.cpp/issues/28848) (closed as not planned), [#30783](https://github.com/ggml-org/llama.cpp/issues/30783) (open), [#24055](https://github.com/ggml-org/llama.cpp/issues/24055) (open), [#28194](https://github.com/ggml-org/llama.cpp/issues/28194) (open).

Incidence, as a reader-pain proxy only: a GitHub issue search for the exact error string returned 17 issues spanning 2025-02-23 to 2026-09-30, and a title search for "context size" among issues created after 2026-07-01 returned 10. Both are text-match counts read on 2026-10-30 at 06:12 UTC; they include issues that merely quote the string, and no search volume or traffic estimate is claimed.

### Verification note

Every quoted excerpt above was checked against the saved raw response for the URL it is attributed to, at the fetched bytes, and the issue states were read from the GitHub API responses on 2026-10-30 between 06:11 and 06:13 UTC. No llama.cpp build was executed for this article: there is no server binary or GGUF weights in the authoring environment, so no token counts, timings, `finish_reason` values or shift log lines are presented as observed. The procedures in the attribution section are commands for you to run against your own server; they are not a dataset shipped with this page.
