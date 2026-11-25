---
title: "Qwen3 0.6B as an Agent Tool Router: 13 CPU Calls, 10-94 s Each"
description: "On a 2-core CPU box with Ollama 0.20.3, qwen3:0.6b returned the right tool and a schema-valid title/priority pair in 7 of 7 calls that were not cut off by the token cap, at 1, 4 and 8 tools - but each call took between 10.2 s and 94.3 s, and with a 128-token generation budget every 4- and 8-tool call came back empty with done_reason=length. Thirteen raw calls, the script and the JSONL are published."
date: 2026-11-24 00:00:00+00:00
lastmod: 2026-11-24 12:35:00+00:00
draft: false
schema: schema-qwen3-0-6b-agent-tool-router-2026
tags:
  - Qwen3 0.6B
  - agent tool router
  - tool calling
  - local LLM
  - Ollama
  - CPU inference latency
  - done_reason
  - small language model
  - agent turn budget
cover:
  image: "/images/qwen3-0-6b-agent-tool-router-2026.png"
  alt: "Horizontal dot plot of 13 measured qwen3:0.6b /api/chat wall times on a 2-core CPU box, one row per call in three groups (1, 4 and 8 tools); filled blue circles are the 7 calls that returned create_ticket with a valid title and priority (done_reason=stop), filled orange squares are the 6 calls that returned no tool call under the 128-token budget (done_reason=length); each marker is labelled with its own wall time in seconds."
  relative: false
---

The smallest Qwen3 checkpoint is 0.6B parameters and fits on a CPU in under a gigabyte of memory. That makes it tempting as the cheap routing layer of an agent: hand it eight tool definitions, let it pick `create_ticket`, let a bigger model do the actual work. Two numbers decide whether that idea survives contact with a real agent loop - how often it picks the right tool, and how long one call takes - and neither is on the model card.

This article reports both from a fixture that was run on one CPU-only box: 13 calls to `qwen3:0.6b` through Ollama's `/api/chat`, with 1, 4 and 8 tools registered, temperature 0, seed 7, and an explicit instruction naming the goal. The short answer: **selection was not the problem, generation budget and wall time were.** Every call that reached a normal stop chose `create_ticket` and filled both required arguments validly; no call ever chose a wrong tool. But the first sweep returned six empty responses in a row until the generation budget was raised, and the slowest single call took 94.3 s on 2 CPU cores.

The model card for [Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) declares 0.6B total parameters, 0.44B non-embedding, 28 layers and a 32,768-token native context ([model card README](https://huggingface.co/Qwen/Qwen3-0.6B/raw/main/README.md)). It states nothing about tool-selection accuracy or per-call latency, which is why a fixture is needed rather than a spec comparison.

## The fixture: one schema, one instruction, three registry sizes

The target function is a single `create_ticket` definition with two required properties: a `title` string and a `priority` string restricted to an enum of `low`, `medium`, `high` and `urgent`. Filler functions are drawn from a fixed pool of 23 unrelated definitions so that the registry sizes 1, 4 and 8 differ in how many candidates compete, not in what the target looks like.

Every call posts to `http://127.0.0.1:11434/api/chat` with `stream: false`, `temperature: 0`, `seed: 7`, and `num_predict` set to 128 in the first sweep and 512 in the second. The instruction is explicit: create a ticket titled "Invoice mismatch" with priority high. Each response is checked against three things - `done_reason`, the length of `content`, and the number of entries in `message.tool_calls` - and the arguments are then validated per key: `title` must be a non-empty string, `priority` must be one of the four enum values. The [Ollama chat API reference](https://docs.ollama.com/api/chat.md) defines the fields this reads: `tool_calls` as "Tool calls requested by the assistant", `done_reason` as the "Reason the response finished", `eval_count` as the "Number of tokens generated in the response", and `total_duration` in nanoseconds.

The tested configuration, from the environment snapshot taken at collection time: `qwen3:0.6b`, Q4_K_M, 522 MB on disk, manifest digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`, Ollama 0.20.3, `nproc` 2, 11,927 MB RAM, and `size_vram: 0` in `/api/ps`, so nothing ran on a GPU. The same snapshot reports a runtime `context_length` of 4096 - the server's effective window, not the 32,768 the card declares. Every prompt in this fixture was far below 4096 tokens, so the declared context was not exercised and this article makes no truncation claim from it.

## Result 1: the right tool, with arguments that validate

| Registry size | Generation budget | Calls | Correct tool + valid arguments | Wrong tool | No call |
|---|---|---|---|---|---|
| 1 tool | 128 | 3 | 3 of 3 | 0 | 0 |
| 4 tools | 128 | 3 | 0 of 3 | 0 | 3 |
| 8 tools | 128 | 3 | 0 of 3 | 0 | 3 |
| 4 tools | 512 | 2 | 2 of 2 | 0 | 0 |
| 8 tools | 512 | 2 | 2 of 2 | 0 | 0 |

Of the 13 measured calls, 7 were allowed to reach a tool call, and all 7 returned `create_ticket` with `{"title": "Invoice mismatch", "priority": "high"}` - the correct tool, both required keys present, the enum value inside its allowed set. Six calls returned no tool call at all, and every one of those six sat in the 128-token sweep. No call in the whole run selected a wrong function, and none returned malformed arguments.

That result is narrower than it sounds. A degenerate one-tool registry proves only that the model emits a valid call when there is nothing to choose between; four and eight tools are the interesting cases, and each of those has a sample of two successful calls at the working budget. The honest statement is "no routing error was observed in 7 calls, not a measured accuracy rate", and the failure taxonomy this fixture can price is limited to "no call" and "call truncated before it surfaced".

## Result 2: the empty response that is really a budget truncation

The first sweep used `num_predict: 128` and, with 4 and 8 tools registered, produced six responses in a row with `done_reason: "length"`, an empty `content` string, and zero `tool_calls`. That signature is easy to misread as "the model had nothing to say", and it is the single most useful thing this fixture found: at the same prompt shape, the same cells succeed as soon as the budget is raised to 512.

The arithmetic points at the thinking trace rather than at routing. `eval_count` came back at exactly 128 in all six truncated calls - the cap, to the token - and the generated tokens were not in `content` and not in a tool call. Qwen3's chat template enables thinking by default, which the model card states in its quickstart as `enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.` The Ollama reference also defines a separate `thinking` field, "Optional deliberate thinking trace when `think` is enabled". So the 128-token budget was spent on reasoning that never reached an answer.

The check a reader can apply without server logs is three fields on the response: `done_reason` (a value of `length` means you hit the cap), the length of `content`, and `len(message.tool_calls)`. `done_reason: "length"` with empty content and no tool call is a budget failure, not a model opinion. Raise `num_predict`, and re-test the same cell before concluding anything about the model's ability.

## Result 3: wall time, and the turn budget it implies

| Registry size | Calls | Min | Median | Max |
|---|---|---|---|---|
| 1 tool | 3 | 17.92 s | 19.44 s | 29.14 s |
| 4 tools | 5 | 10.19 s | 11.91 s | 24.26 s |
| 8 tools | 5 | 10.94 s | 32.54 s | 94.35 s |

Across all 13 calls the wall time ranged from 10.19 s to 94.35 s, with an overall median of 20.92 s. The worst observation was a single 8-tool call at 94.35 s that returned the correct tool and valid arguments; it was not an error, just a slow sample. Tokens per second, computed as `eval_count` divided by `eval_duration`, ranged from 1.42 to 14.71 on the same box.

Do not read that table as a curve. The cell medians are not monotonic - the 4-tool median is lower than the 1-tool median - and with three to five samples per cell on a shared 2-core host, neither the drop nor the rise is evidence of a per-tool-count latency effect. What the data does support is the spread within a fixed configuration: identical prompts, identical seed, identical temperature, and a 9x difference between the fastest and slowest call. Prompt length does not explain the medians either: prompt tokens rose from 187 to 315 to 487 across the three registry sizes, yet the 4-tool median (11.91 s) sits 7.53 s below the 1-tool median (19.44 s) with 128 more prompt tokens, while the 8-tool median (32.54 s) is 13.10 s above the 1-tool median with a 10.94-94.35 s range.

Turn-budget arithmetic is where this number becomes a decision. Five router calls at the 8-tool median of 32.54 s is about 163 s of pure routing per turn, before a single token of the actual task. Substitute the slowest observed call and the same five-call turn is 471 s. A sub-1B router does not remove the cost of tool selection; it moves that cost from a per-token bill to wall time on your own machine.

## Prompt cost grows with the registry, not with the model

`prompt_eval_count` rose from 187 tokens at one tool to 315 at four and 487 at eight, which is roughly 43 prompt tokens per added definition on this model and template. Registry size therefore costs twice: more prompt tokens to evaluate, and - in this fixture - a wider latency spread. The token side of that trade-off is measured in detail in [the tool-definition prompt-token analysis](https://baeseokjae.github.io/posts/ollama-tool-definition-prompt-token-cost-2026/), and the request/response fields used here are the ones documented for [the tools parameter in the same API](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/). For the model's place in the wider lineup, including the weight-only memory arithmetic, see [the Qwen3 lineup guide](https://baeseokjae.github.io/posts/qwen-3-full-lineup-guide-2026/).

## Reproduce it on your own registry

The fixture is standard-library Python: `urllib` against `127.0.0.1:11434`, no SDK, an append-only JSONL so a deadline leaves usable partial evidence. The five files are published in this site's repository under `research/evidence/qwen3-0-6b-agent-tool-router-2026/`:

- [probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/qwen3-0-6b-agent-tool-router-2026/probe.py) - the probe, with the target schema and the filler pool
- [run.sh](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/qwen3-0-6b-agent-tool-router-2026/run.sh) - the sweep driver that records `ollama --version`, `nproc`, `free -m`, the model digest and the `/api/ps` row
- [results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/qwen3-0-6b-agent-tool-router-2026/results.jsonl) - one JSON line per call, 13 rows
- [summary.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/qwen3-0-6b-agent-tool-router-2026/summary.csv) - per-cell counts and wall-time distribution
- [env.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/qwen3-0-6b-agent-tool-router-2026/env.json) - host, model and runtime snapshot at collection time

To run it, `cd` into that directory with a local Ollama serving `qwen3:0.6b` and call `PROBE_DEADLINE_EPOCH=$(date +%s --date="+15 min") ./run.sh`. Substituting your own `TARGET` definition and filler pool is the intended use: the fixture is a pattern for measuring your registry, not a claim about yours. Two caveats about the published data are worth stating plainly. First, `num_predict` is not stored as a per-row field in `results.jsonl`, so the two sweeps are separated by append time: the nine 128-token rows were written up to 08:28:16Z and the four 512-token rows from 08:29:07Z onward, which is also what the `env.json` note records. Second, the timestamps in `results.jsonl` are the moment each response was recorded, so the first call completed at 08:24:54Z and the last at 08:31:33Z on 2026-11-10; the calls were not re-run for this article, and the two primary sources above were re-opened on 2026-11-24.

## What this does not establish

- Tool counts 12 and 24 were never measured. The deadline arrived during the 8-tool sweep, and one call in that cell already took 94 s, so there is no curve beyond eight tools and no claim about a dozen-tool registry.
- The ambiguous-instruction prompt shape and the 3-turn loop (call, tool result, second call) were not run. Nothing here says a returned tool result is carried correctly into the next turn; that question needs its own fixture.
- The `qwen2.5:0.5b` control model was not re-run in this attempt, so no cross-model comparison table exists.
- Samples are three to five calls per registry size on one host with 2 CPU cores and no GPU, and the 4- and 8-tool cells hold only two calls each at the working 512-token budget. Wall time is not transferable to other hardware, and no accuracy rate is claimed - only counts.
- Nothing here justifies buying a GPU or paying for an API. The only cost statement the data supports is wall time on a machine you already have.

## The operational checklist this fixture suggests

1. Measure your own p50 and worst case at your real registry size before committing a sub-1B router to a loop. Two minutes of probing beats a leaderboard.
2. Set `num_predict` with headroom for the thinking trace, and re-run any cell that returns `done_reason: "length"` before drawing a conclusion from it.
3. Log `done_reason`, `content` length and `tool_calls` count on every routing call, and treat an empty tool-call list as a failure with a named cause rather than as silence.
4. Budget routing in seconds, not tokens, if the model runs on your own CPU: five 8-tool calls at the median observed here already cost more than two and a half minutes of a turn.
