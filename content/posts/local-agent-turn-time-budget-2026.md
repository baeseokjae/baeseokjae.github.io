---
title: "Turn-Time Budget for a Local Coding Agent: what a measured tokens/second figure buys you in tool-call turns"
date: 2026-11-08T00:00:00+00:00
description: "One turn is prefill over the prompt plus decode over the output plus tool overhead. Using llama-bench's printed CPU rows for 7B Q4_0 at one thread, a 512-token prompt and 256-token output cost 82.98 s of prefill and 63.21 s of decode: 148.19 s per turn, 1.23 h for thirty turns, and a decode rate of at least 0.497 tok/s to fit a 600 s client timeout. A stdlib harness measures your own host and inverts the equation."
draft: false
schema: "schema-local-agent-turn-time-budget-2026"
tags:
  - local llm turn time
  - prefill vs decode
  - agent request timeout
  - ollama eval duration
  - llama bench pp tg
  - coding agent latency
  - token budget per turn
  - cpu inference speed
  - context length cost
  - minimum tokens per second
  - tool call overhead
  - local coding agent
---

Your local model answers a chat question in a couple of seconds and feels fine. You wire it into an agent that needs thirty tool calls to finish one refactor, and around the eighth request the client gives up with a read timeout, or the patch comes back cut in half because generation stopped mid-function. Nothing in the server log looks like an error. Restart the session with a shorter conversation and it completes.

The question that actually decides the fix is arithmetic: given the rate this machine produces, how long is one turn, how long is thirty turns, and what decode rate does the client timeout require? This article answers that with a formula, a worked example computed from llama.cpp's own printed benchmark rows, and a small harness you run against your own endpoint. It publishes no tokens-per-second table of its own, and the reason is at the end: the one place this project could run the measurement was too noisy to produce a number worth printing.

## One tokens/second figure is the wrong unit

A turn is not one number. It is two different operations with different costs. llama.cpp's benchmark tool states the split in its own flag list: prompt processing (`pp`) is "processing a prompt in batches", and text generation (`tg`) is "generating a sequence of tokens", measured as separate tests ([llama.cpp llama-bench README](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/llama-bench/README.md)). Prefill scales with how many tokens you send; decode scales with how many tokens you ask for back. They do not move together: in the CPU rows quoted further down, one thread gives 6.17 tok/s of prefill against 4.05 tok/s of decode, while 32 threads gives 59.00 against 16.41, so the ratio between the two is a property of the host and the batch size rather than of the model. This is also why a model-selection page that declines to rank models by speed is right to refuse ([best Ollama models for coding](/posts/best-ollama-models-coding-2026/)): a rate without a host, a prompt length and an output length is not a property of the model.

Ollama exposes the same split per request. Its generate endpoint returns `prompt_eval_count` ("Number of input tokens in the prompt"), `prompt_eval_cached_count` ("Number of prompt tokens read from the cache"), `prompt_eval_duration` ("Time spent evaluating uncached prompt tokens in nanoseconds"), `eval_count` ("Number of output tokens generated in the response") and `eval_duration` ("Time spent generating tokens in nanoseconds") ([Ollama API reference, generate](https://docs.ollama.com/api/generate.md)). That is everything needed to derive two rates for one real request instead of trusting a headline figure someone measured on a different machine:

| Field in the response | What it counts | Rate you derive |
| --- | --- | --- |
| `prompt_eval_count` | total input tokens: cached plus newly evaluated | — |
| `prompt_eval_cached_count` | the cached subset of those tokens (optional in the response) | — |
| `prompt_eval_duration` | nanoseconds spent evaluating the uncached remainder | prefill tok/s = (count − cached) ÷ (duration ÷ 1e9) |
| `eval_count` | tokens actually generated | — |
| `eval_duration` | nanoseconds spent generating them | decode tok/s = count ÷ (duration ÷ 1e9) |

Three caution notes are built into those definitions. First, `prompt_eval_count` is the *whole* prompt, cached tokens included, while `prompt_eval_duration` times only the ones the server actually evaluated — so dividing the count by the duration overstates prefill on any prefix-cache hit. Ollama's own metrics printer subtracts the cached count before dividing (`uncached := max(0, m.PromptEvalCount-cached)` then `uncached / duration` in [`api/types.go`](https://raw.githubusercontent.com/ollama/ollama/main/api/types.go)), and the server builder shows why the two numbers disagree: the count is `CacheN + PromptN` while the duration is `PromptMS` ([`llm/llama_server.go`](https://raw.githubusercontent.com/ollama/ollama/main/llm/llama_server.go)). Second, `prompt_eval_cached_count` is optional, so a missing value has to be treated as 0 — the no-cache case — which is what the harness below does. Third, `prompt_eval_duration` excludes network and client time. All three are reasons to derive the prefill numerator as a subtraction and to add overhead explicitly rather than hope the server accounted for it.

## The turn equation

For a single stream, with no queueing:

```
turn_s = prompt_tokens / prefill_tps + output_tokens / decode_tps + tool_overhead_s
```

Three terms, three different levers. `tool_overhead_s` is everything between the model finishing and the next request starting: tool execution, file reads, transport, retry backoff. On a local host it is often the smallest term, and that is exactly why it misleads people — it is the term that hides the retry multiplier later.

Worked example. The inputs are llama-bench's own printed sample rows for `llama 7B mostly Q4_0`, backend `CPU`, 1 thread: `pp 64` at 6.17 ± 0.07 tok/s and `tg 16` at 4.05 ± 0.02 tok/s ([llama-bench README table](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/llama-bench/README.md)). They are upstream sample output, not a measurement made for this article and not a description of any reader's machine. The scenario is declared: a 512-token prompt, a 256-token output, 2 s of tool overhead per turn.

| Term | Arithmetic | Seconds | Share of turn |
| --- | --- | --- | --- |
| Prefill | 512 ÷ 6.17 | 82.98 | 56% |
| Decode | 256 ÷ 4.05 | 63.21 | 43% |
| Tool overhead | declared | 2.00 | 1% |
| **Turn** | sum | **148.19** | 100% |

Prefill is more than half of that turn. That is the finding most tokens/second headlines erase: a page that quotes one number cannot tell you whether the dominant cost is reading your prompt or writing the answer.

## What thirty turns cost

Multiply, assuming a prompt that does not grow:

| Turns | Task time | Hours |
| --- | --- | --- |
| 10 | 1,481.9 s | 0.41 |
| 30 | 4,445.8 s | 1.23 |
| 50 | 7,409.6 s | 2.06 |

The assumption is the problem. An agent loop appends every tool result to the conversation, so the prompt grows each turn and the task time grows faster than the turn count suggests. Holding decode and overhead fixed at the values above, a 1,024-token prompt costs 231.17 s per turn and a 4,096-token prompt costs 729.07 s per turn. All of the extra 580.9 s went to prefill: 4,096 ÷ 6.17 = 663.86 s of it.

## Inverting the equation

The useful form runs backwards. If the client's per-request budget is `T`, the prompt costs `P` seconds to prefill and overhead is `H`, the slowest decode rate that still fits one turn is:

```
min_decode_tps = output_tokens / (T - P - H)
```

At the same inputs: 256 ÷ (600 − 82.98 − 2) = **0.497 tok/s**. The 600 s figure is a real default, not an illustration — openai-python ships `DEFAULT_TIMEOUT = httpx2.Timeout(timeout=600, connect=5.0)` and `DEFAULT_MAX_RETRIES = 2` ([openai-python `_constants.py`](https://raw.githubusercontent.com/openai/openai-python/main/src/openai/_constants.py)). Two retries mean one slow turn can occupy up to three times its own latency: 3 × 148.19 = 444.6 s for a turn that was already inside budget.

There is a harder limit above the decode floor. Prefill alone consumes the whole 600 s budget at 6.17 × 600 = 3,702 prompt tokens. Past that point the minimum decode rate stops existing: at a 4,096-token prompt the turn is 729.07 s, and no amount of decode speed saves it. The same arithmetic at 8,192 prompt tokens gives 1,327.7 s of prefill — before the first output token is generated. This is the failure mode that looks like a model problem and is actually a context problem, and it is why [deciding whether the model fits your card](/posts/local-llm-vram-kv-cache-sizing-2026/) is only step one: fitting is not the same as finishing a turn.

## Where the time goes, and the order to fix it

Given a measured prefill and decode rate, the terms rank predictably:

1. **Prompt length.** It multiplies prefill, and prefill is the largest term in the worked example. Sending whole files instead of retrieved spans is the usual cause.
2. **Output tokens.** It multiplies decode. A capped `num_predict` turns a 63.21 s decode term into 31.60 s at 128 tokens, and the turn into 116.59 s.
3. **Retries.** Two retries turn one over-budget turn into three, which is how a task that should take 1.23 h becomes a session that looks hung.
4. **The timeout itself.** Raising it hides the problem until the next context growth, and it is the only lever that costs nothing to describe and costs the most to rely on.

If prefill alone exceeds the request budget, shortening the output is the wrong first fix. The turn stays over budget no matter how few tokens you ask for. Cut context, or move the model off CPU, or raise `T` — in that order of cheapness.

## Measure your own host

The harness is one stdlib file, `turn_budget.py`, with a three-prompt fixture and a test file. It does not download models and does not set server variables; it talks to an endpoint you already have running:

```
python3 turn_budget.py measure --model <your-tag> --jsonl "$TMPDIR/runs.jsonl" --repeats 3
python3 turn_budget.py summarise --jsonl "$TMPDIR/runs.jsonl"
python3 turn_budget.py compute --jsonl "$TMPDIR/runs.jsonl" \
    --turns 30 --output-tokens 256 --tool-overhead 2 --timeout 600
```

Three design rules matter more than the code. First, rates are derived from the per-request counters above — prefill from `prompt_eval_count` minus `prompt_eval_cached_count`, over the uncached-only `prompt_eval_duration` — never from a headline figure or from the raw count. Second, every record is written and `fsync`ed before the next request starts — a run killed at its cap still leaves usable evidence, which is exactly how an earlier attempt of this project lost seven of nine records. Third, the summary applies a spread gate: repeats that disagree by more than 10% are reported as `rejected_noisy` and the medians are not printed as a baseline. `compute` refuses a rejected run file for the same reason.

Run the arithmetic without a server, or reproduce the numbers above with no endpoint at all:

```
python3 turn_budget.py example
python3 turn_budget.py compute --prefill-tps 6.17 --decode-tps 4.05 \
    --prompt-tokens 512 --output-tokens 256 --tool-overhead 2 --turns 30 --timeout 600
```

The 24 unit tests pin every figure in this article: 82.98 s of prefill, 63.21 s of decode, 148.19 s per turn, 4,445.8 s over thirty turns, the 0.497 tok/s floor, 3,702 prompt tokens at the timeout, and the round trip where feeding the minimum decode rate back into the turn equation returns exactly 600 s. They also pin the cache accounting — a 64-token prompt with 32 tokens served from the prefix cache has to produce the same rate as a 32-token uncached prompt, a missing `prompt_eval_cached_count` has to be treated as 0, and a fully cached prompt has to be refused instead of reported. They run with `python3 test_turn_budget.py`, need no network, and use a synthetic response to exercise the JSONL path including a failed request.

## The negative result behind the missing baseline

This project tried to publish a measured baseline and could not. The attempt ran on a shared 2-vCPU, 11 GB sandbox against `qwen3-vl:2b` (`Q4_K_M`, digest `0635d9d857d497aeadba3d7d27485746c50554446f9f6ec01ef39788221adbe`) with three fixtures and three repeats inside a declared 110 s run budget. Two of nine records completed; both were recovered from the script's stdout after its own 130 s kill cap ended the run — the method note documents the two limits separately. Decode came out at 1.615 and 3.165 tok/s — a 96% spread — and prefill at 3.781 and 228.859 tok/s, the slower one including cold model load. That fails the same 10% gate the shipped script enforces, so those figures are recorded as a rejected run and appear nowhere in this article as a baseline or a hardware comparison.

The 228.859 tok/s figure is also cache-affected and is not a prefill measurement. It was computed the old way, by dividing `prompt_eval_count` — which counts cached tokens as well as newly evaluated ones — by the uncached-only `prompt_eval_duration`; both records show a 32-token `prompt_eval_count` for the same fixture, and neither captured `prompt_eval_cached_count`, so how much of that 32 was served from the prefix cache cannot be recovered. The corrected formula can only put the true uncached rate at or below 228.859 tok/s, and how far below depends on a cached count nobody recorded — which is the whole reason the run is published as rejected rather than quoted.

The useful part of that failure is the shape of it: the same fixture and token counts took 79.8 s and 16.9 s on the same host minutes apart. A single run on a machine with co-resident services is not a measurement, and the gate exists because the obvious alternative — average the two and print 2.39 tok/s — would have produced a confident, wrong number.

## What this cannot tell you

The worked example rests on CPU rows printed in a README with no CPU model named, at a `pp` batch of 64 tokens and a 16-token `tg` run, so it supports "CPU prefill can dominate a long-context turn" and nothing more precise. No GPU was measured for this article and no cross-hardware table is offered; GPU rates, batch sizes and backend flags change both terms by orders of magnitude, and a comparison built from mixed sources would be worse than no comparison. A different tokenizer changes `prompt_tokens` for the same text, so a reader who copies the 512-token scenario with different content will get a different prefill term — derive token counts from the response, not from word counts.

## Reader deliverables

The harness, fixture, tests and the worked-example output are published files in this site's repository, not a private directory:

- Measurement harness — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/turn_budget.py
- Three-prompt fixture — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/fixtures/prompts.json
- Arithmetic tests — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/test_turn_budget.py
- Test run record (command, exit code, 24 tests, no network) — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/test-run.json
- Worked-example output, as printed by the script — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/worked-example.json
- Rejected run records from the failed baseline attempt — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/runs.jsonl
- Method and host notes for that attempt — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-turn-time-budget-2026/method.md

None of these files contain credentials, hostnames or personal data; they are text the script reads and writes. The fixture is invented test prose, and the run records carry the model digest, request options and derived rates only.

## If you only remember one thing

The number to measure twice is not tokens per second. It is prompt tokens in, output tokens out, and a timeout — because `turn_s = prompt_tokens / prefill_tps + output_tokens / decode_tps + overhead` has an inverse, and the inverse is the only version that tells you whether your agent will finish. If your measured prefill puts the prompt alone past the client's budget, the model's decode speed is irrelevant; a second concurrent session cannot fix that either, as the [single-stream concurrency measurements](/posts/local-llm-concurrent-agent-sessions-2026/) show, and neither can [the payback calculation](/posts/local-llm-rig-cost-payback-2026/) that consumes this page's rate as an input.

## Sources

- Ollama API reference, generate endpoint (`prompt_eval_count`, `prompt_eval_cached_count`, `prompt_eval_duration`, `eval_count`, `eval_duration`) — https://docs.ollama.com/api/generate.md
- Ollama server source, `llm/llama_server.go` (`promptEvalCount()` returns `CacheN + PromptN`; `PromptEvalCachedCount` is `CacheN`; `PromptEvalDuration` is `PromptMS`) — https://raw.githubusercontent.com/ollama/ollama/main/llm/llama_server.go
- Ollama API source, `api/types.go` (metrics printer computes the prompt eval rate as `(PromptEvalCount - cached) / PromptEvalDuration`) — https://raw.githubusercontent.com/ollama/ollama/main/api/types.go
- llama.cpp llama-bench README (`pp`/`tg` definitions and the printed CPU rows for 7B Q4_0 at 1 thread) — https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/llama-bench/README.md
- openai-python `_constants.py` (`DEFAULT_TIMEOUT` 600 s, `DEFAULT_MAX_RETRIES` 2) — https://raw.githubusercontent.com/openai/openai-python/main/src/openai/_constants.py
