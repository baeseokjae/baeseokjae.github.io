---
title: "Ollama's Silent Context Truncation: What num_ctx Overflow Actually Drops"
date: 2026-10-31T15:28:00+00:00
tags:
  - "ollama silent truncation"
  - "ollama num_ctx overflow"
  - "prompt_eval_count misleading"
  - "ollama context window truncation"
  - "local llm agent history dropped"
  - "ollama api chat truncation"
  - "ollama prompt truncated no error"
  - "llm context overflow silent"
  - "ollama agent tool calling breaks"
  - "ollama generate head tail tokens"
description: "When a rendered conversation exceeds num_ctx, Ollama 0.20.3 drops whole messages from the front of /api/chat history and answers without an error, while prompt_eval_count reports only what was evaluated. Source reading plus a five-request probe."
draft: false
schema: "schema-ollama-silent-context-truncation-2026"
---

An agent on a local Ollama server stops acting on its own conversation mid-session: a tool result it received ten turns ago is treated as never having existed, and nothing in the API response says why. The usual suspects are the model, the sampler and the prompt wording. In Ollama 0.20.3 the likelier cause is the server. When the rendered conversation does not fit `num_ctx`, `/api/chat` removes whole messages from the front of the history, keeps the tail, and answers with a normal 200 response. `prompt_eval_count` then reports the size of the shortened prompt, not the size of the prompt you sent, so a dashboard built on that number shows a healthy, small request.

The part that is easy to get wrong — and that the earlier version of this article got wrong — is what survives. The `/api/chat` truncation loop re-collects every `role: "system"` message out of the prefix it is about to discard, so the system prompt and the tool definitions normally survive a clamp. What disappears is the middle and the front of the conversation. On `/api/generate` the client supplies one already-rendered string with no message structure to protect, and that is the path where the head of the prompt can be lost outright; the source reading says so, and the probe below does not settle it.

## What `num_ctx` caps, and where the cap is applied

`num_ctx` is documented as a plain integer option — "Context length size (number of tokens)" — with no stated overflow behaviour ([generate reference](https://docs.ollama.com/api/generate.md), [chat reference](https://docs.ollama.com/api/chat.md)). The FAQ gives a default of 4096 tokens, overridable with `OLLAMA_CONTEXT_LENGTH` ([FAQ](https://docs.ollama.com/faq.md)). That single number is only the floor: in v0.20.3 the server picks the default from total VRAM — 262,144 tokens at 47 GiB or more, 32,768 at 23 GiB or more, otherwise 4,096 ([routes.go, v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/server/routes.go)). Guides that still repeat "defaults to 2048" are describing an older build; do not size a production cap from them.

The option travels from the HTTP request into `chatPrompt`, which renders the conversation into a single string and then decides whether it fits. The cap is applied to that rendered string, not to each message, which is why the failure is message-shaped: a message is either rendered or it is not.

## Reading the truncation loop

The v0.20.3 source is explicit about intent. The function comment reads: "chatPrompt truncates any messages that exceed the context window of the model, making sure to always include 1) the latest message and 2) system messages" ([prompt.go, v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/server/prompt.go)). The loop itself walks an index from the first message forward, and on each iteration it re-collects system messages from the portion it is about to skip before rendering the remaining slice:

```go
for i := 0; i <= lastMsgIdx; i++ {
    // Collect system messages from the portion we're about to skip
    system = make([]api.Message, 0)
    for j := range i {
        if msgs[j].Role == "system" {
            system = append(system, msgs[j])
        }
    }
    p, err := renderPrompt(m, append(system, msgs[i:]...), tools, think)
    ...
```

Two consequences follow directly from that loop, and both contradict the most common diagnosis. First, the system prompt is not what disappears on `/api/chat`, so a long tool list is not discarded by the same mechanism that discards an early turn. Second, tool definitions are passed to `renderPrompt` on every candidate slice, so they are re-rendered rather than dropped between iterations. The current `main` branch keeps the same loop and the same stated intent, though the return value was renamed: where v0.20.3 returns `images []llm.ImageData` and describes "the prompt and images", `main` returns `media []llm.MediaData` and describes "the prompt and media" ([prompt.go, main](https://raw.githubusercontent.com/ollama/ollama/main/server/prompt.go)).

What does disappear is the front of the history: earlier user turns, earlier tool results, earlier assistant messages. An agent that "forgets" a tool result it received ten turns ago is often not hallucinating — that message was never rendered. The same code also explains why a system prompt that is itself larger than `num_ctx` cannot be rescued by this loop: when no slice fits, the loop exits at the last message and renders anyway, and whatever the runner does next is a layer this reading did not trace.

## The silent part

There is no status code, no warning field, and no error object. The only trace is a debug-level server log line, which is invisible at default verbosity. `prompt_eval_count` is documented as "Number of tokens in the prompt" ([chat reference](https://docs.ollama.com/api/chat.md)) — an accurate description of the prompt that was evaluated, and a misleading description of the prompt that was sent.

This is a documented, intentional clamp, not a bug. The defect is the absence of feedback: a client cannot distinguish "your 1,032-token prompt was evaluated" from "your 1,032-token prompt was cut to 465 tokens and then evaluated". Anything that derives prefill throughput, cache behaviour, or context headroom from that number inherits the error. The [prefill-monitoring walkthrough](/posts/ollama-llmwatch-live-prefill-progress-monitoring/) on this site uses `prompt_eval_count` as the prompt size, which holds only while the prompt fits — a boundary worth stating next to that formula.

## What a five-request probe shows

I ran five requests against a local Ollama 0.20.3 daemon with `qwen2.5:0.5b` (Q4_K_M, 494M params), `temperature: 0`, `num_predict: 32`, on a 2-vCPU Neoverse-N1 host with 11 GB RAM and no GPU. The chat fixture is a system message plus twelve numbered messages `MSG-01` … `MSG-12` and a final instruction to list the labels in order; the generate fixture is one prompt with a head sentinel and a tail sentinel. Every request completed; nothing timed out.

| Fixture | Endpoint | num_ctx | prompt_eval_count | eval_count | wall | Model echoed |
|---|---|---|---|---|---|---|
| chat-fits-2048 | /api/chat | 2048 | 1032 | 32 | 52.9 s | MSG-01, MSG-02, MSG-03, … in order |
| chat-clamp-512 (rep 1) | /api/chat | 512 | 465 | 15 | 19.5 s | MSG-08, MSG-10, MSG-12 |
| chat-clamp-512 (rep 2) | /api/chat | 512 | 465 | 15 | 1.1 s | MSG-08, MSG-10, MSG-12 |
| gen-sentinel-1024 | /api/generate | 1024 | 529 | 11 | 18.2 s | head sentinel only |
| gen-sentinel-256 | /api/generate | 256 | 256 | 11 | 9.2 s | garbled tail fragment |

Three things are worth reading out of that table. The fitting control reported 1,032 tokens for a prompt that fits in 2,048 — the submitted length, measured by the server itself, which is what makes it a control. The clamped run of the identical conversation reported 465, or 45% of 1,032, and running it a second time reported the same 465. And the clamped count is 465 rather than 512, which is what message-level dropping looks like: the loop removes whole messages until the remainder fits, so it lands below the cap instead of exactly on it.

The two chat replies are worth quoting in full, because the first run's record kept only their first 120 characters. I repeated those two requests at 15:32–15:35 UTC and kept the complete response objects; both `prompt_eval_count` values reproduced exactly, 1,032 and 465. The control replied `MSG-01 MSG-02 MSG-03 MSG-04 MSG-05 MSG-06 MSG-` and was cut off by the 32-token output cap, not by anything the server removed. The clamped run replied `MSG-08 MSG-10 MSG-12` and stopped by itself after 15 tokens, well under the cap. Read literally, that reply begins seven labels into the conversation and contains no label from `MSG-01` to `MSG-07`.

It is not, however, a transcript of the surviving window. A contiguous front drop that kept `MSG-08` onward should also have kept `MSG-09` and `MSG-11`, and neither appears. Two readings fit: the model stopped listing labels it did have, or something narrower than whole messages survived. This record cannot separate them, so I use the reply as an illustration that the head was gone and the tail was not, and treat the token counts — not the reply — as the measurement. A 494M-parameter model is a weak instrument for enumerating its own context.

The sentinel cells are weaker still, and I am not going to dress them up. In the fitting 1,024-token cell the model echoed the head sentinel and dropped the tail one, so "the tail always survives" is not something this fixture can establish — the model fails to echo both sentinels even when nothing is truncated. At `num_ctx=256` the head sentinel was absent and the reply contained a mangled tail fragment (`SENTINEL-009917` for `SENTINEL-TAIL-9917`), which is consistent with the head being cut and the tail surviving in damaged form, but consistent is all it is. Treat the generate-path question as open: the source reading says the head is unprotected there, and this probe does not settle it either way.

The system-prompt echo check failed for the same reason and is reported as a negative result: the fixture asked the model to open every reply with a codename carried in the system message, and it failed to do so in the fitting control as well as in the clamped cell. An instruction-following failure that reproduces in the control proves nothing about message loss, and nothing in this probe shows a system message being dropped on `/api/chat` — the source reading says it would not be.

One timing deserves a warning rather than an explanation. The second clamped request returned in 1.1 s against 19.5 s for the first, which looks like a cache hit; the 0.20.3 response object carries `total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`, `eval_count` and `eval_duration`, and no cached-token field, so this article does not claim one.

## Detecting the clamp from the client

The server will not tell you, so measure it yourself. Render the exact string you would send, tokenize it, and compare it to `num_ctx` before the request goes out; or compare the server's `prompt_eval_count` against your own count for a prompt you know fits. A `prompt_eval_count` that is stable across sessions of visibly different length, or that is suspiciously just under `num_ctx`, is the signature.

Two more practical checks:

- Log the number of messages you send and the index of the first one. If the model's behaviour looks like it lost the opening of the conversation, you have a message-level drop, and the fix is history trimming you control rather than a bigger window you hope for.
- Put a distinctive marker in the earliest user message and a second one in the system message, then ask for both on a short prompt. On `/api/chat` a surviving system marker next to a missing user marker is the drop; if both markers vanish on a short request, you have a model that will not follow that instruction and no information.

Client-side trimming discipline — deciding what to drop before the request leaves your process, as argued in [why a local model feels dumber](/posts/local-llm-feels-dumber/) — is the only version of this you can see, and it is the reason to summarise or evict history deliberately rather than fill the window and trust the server.

## Fixing it

Raise `num_ctx` only as far as the host can actually hold: the KV cache grows with the window, and on a machine with no GPU the cost shows up as time, not as an error. Prefer trimming history in the client where the trim is visible and loggable, keep the system message short enough that it fits on its own, and re-check the metric boundary whenever you upgrade — the tiering in `routes.go` means the default window on a given machine may not be the number in the FAQ.

None of this makes the clamp a bug, and no "best `num_ctx`" number belongs in an article: the useful output is a detection habit, not a table. What remains open is the raw `/api/generate` path, where the head-versus-tail question needs a fixture the model can echo reliably — a task for a better instrument than a 494M-parameter model.

## Reproduce it

The probe driver, the fixture list, the five result rows and the full chat replies are published with this article: [ollama_ctx_probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-silent-context-truncation-2026/ollama_ctx_probe.py), [prompt-fixtures.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-silent-context-truncation-2026/prompt-fixtures.jsonl), [runs.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-silent-context-truncation-2026/runs.csv) and [chat-replies.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-silent-context-truncation-2026/chat-replies.json), with the replay script in [chat_replay.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-silent-context-truncation-2026/chat_replay.py). All numbers above come from one host with one quantised model; the script reproduces the shape of the result elsewhere, not the timings. If you want the API surface itself, the [Ollama API integration guide](/posts/ollama-api-local-llm-integration-developer-guide-2026/) covers the request options, and the [Devstral setup guide](/posts/devstral-small-2-local-setup-guide-2026/) covers the neighbouring failure modes.
