---
title: "Ollama Tool Definitions Are Not Free: The Measured Prompt-Token Cost of Every Tool You Register"
description: "On Ollama 0.20.3 with qwen3:0.6b a tools block adds about 58 fixed prompt tokens before the first definition and about 57 more per terse tool, against about 292 for a verbose one — so twelve terse tools spend 746 of a 4096-token default window before the user types. Eight measured cells, three identical repeats each, raw JSONL and the aggregation script published."
date: 2026-11-12 00:00:00+00:00
lastmod: 2026-11-12 06:52:00+00:00
draft: false
schema: schema-ollama-tool-definition-prompt-token-cost-2026
tags:
  - Ollama
  - tool calling
  - prompt tokens
  - prompt_eval_count
  - context budget
  - local LLM
  - function calling
  - agent tool registry
  - token accounting
---

You register twelve tools on a local agent, send a six-word message, and `prompt_eval_count` comes back at 764 instead of 18. Nothing is wrong: the definitions you sent are part of the prompt, and on a 4k default context that registry has already spent 746 of your 4096 tokens before the conversation starts — and it re-pays that cost on every turn.

This article measures the cost instead of estimating it. One model, one fixed message, one local server, tool sets of 0, 1, 3, 6 and 12 definitions in a deliberately terse form, and sets of 1, 3 and 6 in a deliberately verbose form, three repeats per cell, with the raw request and response records published next to the script.

The short answer: a terse definition costs **about 57 prompt tokens** on this model, a verbose one **about 292**, and a non-empty `tools` block costs a fixed **~58 tokens** of scaffolding on top of the chat template. The useful part is not the average — it is that both terms are linear, so you can compute your own registry's standing cost from your own schemas before running anything.

## What `prompt_eval_count` actually counts

Ollama reports the prompt size of each `/api/chat` response as `prompt_eval_count`, documented as the "Number of tokens in the prompt" ([chat API reference](https://docs.ollama.com/api/chat.md)). That number is not the length of the message you typed; it is the length of the fully rendered prompt after the chat template is applied, which is why the no-tools baseline in this fixture is 18 tokens for a six-word message.

The `tools` field is documented as an "Optional list of function tools the model may call during the chat" ([chat API, tools parameter](https://docs.ollama.com/api/chat.md#tools)), and each entry is a function definition carrying a name, a description and a JSON Schema `parameters` object ([tool calling documentation](https://docs.ollama.com/capabilities/tool-calling.md)). What the documentation cannot tell you — because it is model- and template-specific — is how many tokens that object becomes once it has been rendered.

That gap is the whole problem. A schema is authored in JSON, billed in tokens, and the conversion rate depends on the tokenizer of whichever model you pulled. The argument shapes themselves are ordinary JSON Schema objects, so nested objects and `additionalProperties` behave exactly as the [JSON Schema object reference](https://json-schema.org/understanding-json-schema/reference/object) describes — and, per the numbers below, as expensive as they are elaborate.

## Method

The fixture is a single driver, `tool_schema_token_audit.py`, run against a local Ollama 0.20.3 server on a 2 vCPU / 11 GB container with no GPU. The model is `qwen3:0.6b` at Q4_K_M. Every request uses the same user message ("Reply with the single word: ready."), `stream: false`, `temperature: 0`, `num_ctx: 8192` and `num_predict: 8`, and differs only in the `tools` array.

There are eight measured cells: terse sets of 1, 3, 6 and 12 tools, and verbose sets of 1, 3 and 6, plus a 0-tool baseline. Sets of N always use the first N of twelve fixed tools, so the cells are nested and the slope across 1/3/6/12 is attributable to the added definitions and nothing else. A terse definition is a name, a one-line description and flat string or number arguments; a verbose definition carries a 110-word description plus a nested `options` object with an enum, numeric bounds, defaults and `additionalProperties: false`. Both forms are published in `tool-fixture.json` so the comparison can be inspected rather than taken on trust.

Two deviations from the research plan are recorded here rather than smoothed over. First, three repeats per cell were collected instead of five. The first request of a cell is the one that pays model load, and its rate is quoted here as prompt tokens per wall-clock second: the records carry `total_duration_ns` and the driver's `wall_s`, not `prompt_eval_duration` (the API reports that field in its example response, but the fixture driver does not record it), so that denominator includes model load and the 8-token generation the fixture asked for, and these figures are completion rates rather than prompt-evaluation throughput. On this CPU host the first requests of the six tool-bearing cells other than the 6-tool verbose one ran at 5.8 to 13.0 prompt tokens per wall-clock second (144 tokens in 24.9 s for one terse tool, 764 in 58.9 s for twelve), the 6-tool verbose cell ran at 38.8, and the no-tools baseline falls outside that band at 0.9 prompt tokens per wall-clock second (18 tokens in 19.2 s). The stage budget did not allow five such cold requests for every cell. Second, the verbose 12-tool cell was not measured: its prompt — an extrapolated 3.6k tokens — exceeded the driver's 260-second client timeout (`REQUEST_TIMEOUT`, overridable with `--timeout`). The attempt is kept as a timeout row with no count (`TimeoutError: timed out`, `n_ok=0` in the published JSONL and CSV), and the run then stopped at the driver's own deadline guard before the cross-surface cell, so no completion for that request exists in the record. The driver published beside this article catches a timeout, prints `error=<type>`, moves to the next cell and still writes the summary, so a rerun on a slower host degrades instead of ending early. Everything else in the tables below is a measured value, and every repeat returned an identical `prompt_eval_count`, so each range is degenerate and each median is an exact repeat rather than an average.

## The measured numbers

Terse definitions, three repeats per cell, identical across repeats:

| Tools registered | `prompt_eval_count` | Added over previous cell | Per added tool |
| --- | --- | --- | --- |
| 0 | 18 | — | — |
| 1 | 144 | +126 | 126 |
| 3 | 250 | +106 | 53 |
| 6 | 415 | +165 | 55 |
| 12 | 764 | +349 | 58 |

The first tool is not like the others, and that is the first thing worth understanding. Going from no tools to one tool costs 126 tokens; each additional tool after that costs 53 to 58. The difference is a fixed block the template emits as soon as `tools` is non-empty — a preamble, an instruction line and the array scaffolding — before the first definition is serialised.

A least-squares line through the 3, 6 and 12-tool cells has a slope of 57.3 tokens per terse tool and an intercept of 75.5 at zero tools, which decomposes against the 18-token baseline into roughly 57.5 tokens of tools-block scaffolding plus 57.3 tokens per definition. That model predicts 133 tokens for a single tool against 144 measured: an 11-token residual at the smallest count, where the tokenizer's share of the array framing is largest. The straight line through the 3- and 12-tool cells alone gives 57.1 per tool and an intercept of 78.7, so the construction matters less than it looks — the scaffolding term lands between 57 and 61 tokens and the slope between 57.1 and 57.3.

## What a verbose description costs

The same twelve tools rewritten with a 110-word description and a nested options object:

| Tools registered | Terse | Verbose | Difference | Difference per tool |
| --- | --- | --- | --- | --- |
| 1 | 144 | 383 | 239 | 239.0 |
| 3 | 250 | 965 | 715 | 238.3 |
| 6 | 415 | 1844 | 1429 | 238.2 |
| 12 | 764 | not measured | — | — |

The description cost is stable at roughly 238 tokens per tool and the verbose slope is 292.3 tokens per definition with a 71.8-token preamble at zero tools, so the verbose form is about five times the terse form and does not drift with tool count. If you were assuming a long, careful tool description is nearly free because the model "needs" it, the fixture says otherwise: one paragraph of guidance per tool is roughly 240 tokens of every turn, which at twelve tools would be nearly 2900 tokens of standing cost — an extrapolation from the measured 6-tool cell, not a measurement.

A rougher sizing rule comes out of the same rows: at twelve terse tools the set runs about 4.8 bytes of JSON per token (3558 bytes for 746 tokens) and the verbose set about 6.3 bytes per token (11531 bytes for 1826 tokens). The ratio is only usable once the fixed scaffolding is amortised, because that part does not scale with bytes: applied below the cell where it was derived, it predicts 357 tokens where 397 were measured at six tools (10% low), 171 against 232 at three (26% low) and 50 against 126 at one (61% low). For a registry of roughly six tools or more it is good enough to decide whether the set fits; for one or two tools, use the two-term formula below.

## The cross-surface question stays open

Ollama's OpenAI-compatible endpoint also accepts `tools` and `stream_options.include_usage` ([OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility.md)), so `usage.prompt_tokens` is available as a second accounting surface. That cell was not collected in this run: the run ended at the 12-tool verbose timeout before the cross-surface step was reached, and no honest comparison exists without it. The compatibility table is a support matrix, not a statement that both surfaces count tokens identically, and nothing here should be read as one — the question of whether `/api/chat` and `/v1/chat/completions` agree on the same tools payload is listed as unmeasured.

## What this means for a small window

Ollama's documented defaults choose the context length from total VRAM: 4k below 24 GiB, 32k at 24–48 GiB, 256k at 48 GiB and above ([context length](https://docs.ollama.com/context-length.md)). This host sits in the first tier, so the denominator here is 4096 — the same default a laptop or a small CI runner gets.

At 4096 tokens, twelve terse tools are 18.2% of the window and the 12-tool verbose registry would be roughly 87% on the extrapolated slope, which is not a context budget but a context ceiling reached before the first user message. At 32k the same twelve terse tools are 2.3%. That is why "just raise `num_ctx`" is popular, and also why it is the wrong first lever on the small tier: the tier is chosen by VRAM, and raising `num_ctx` on a small host moves the cost from the prompt into the KV cache.

The arithmetic to run on your own registry is one line — `57.5 + 57.3 × tools` for terse definitions, `71.8 + 292.3 × tools` for verbose ones — added to whatever your template costs. Twelve terse tools is about 745 tokens; twelve verbose ones about 3579.

## Decision rules that follow from the numbers

Trim before you cut. Converting twelve verbose tools to terse saves about 2800 tokens (3579 against 745), more than deleting ten of twelve terse tools would save (about 570). Rewriting descriptions is the highest-leverage edit available and changes nothing about what the model can do.

Cut when the registry itself is the problem. On a 4k window with 2k of conversation, twelve terse tools leave about 1350 tokens of slack; a third registry is not affordable and no amount of description trimming fixes that. Splitting an agent into two six-tool registries costs a second prompt and a second model load but holds each turn's standing overhead near 415 tokens instead of 764.

Do not expect prompt caching to make the tools block free. `prompt_eval_count` reports what was evaluated, and a cached prefix is reported separately where the server supports it — this fixture's single-turn requests recorded no cached count at all. Even a cheap-to-evaluate tools block still occupies the window, because context capacity and prompt evaluation cost are two different budgets and tools spend the first one whether or not they spend the second.

## Reproduce it

The fixture is published: the driver script, the twelve tool definitions in both forms, the raw per-request JSONL with request hashes and `prompt_eval_count`, the aggregation script that turns that JSONL into the summary CSV, and the CSV itself.

- [tool_schema_token_audit.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-tool-definition-prompt-token-cost-2026/tool_schema_token_audit.py)
- [tool-fixture.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-tool-definition-prompt-token-cost-2026/tool-fixture.json)
- [fixture-raw.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-tool-definition-prompt-token-cost-2026/fixture-raw.jsonl)
- [aggregate_fixture.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-tool-definition-prompt-token-cost-2026/aggregate_fixture.py)
- [fixture-summary.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-tool-definition-prompt-token-cost-2026/fixture-summary.csv)

Run `python3 tool_schema_token_audit.py --out <empty dir> --repeats 3` against any Ollama server and you get the same table for your own model, because the script sends the definitions verbatim and records what the server reports rather than what a tokenizer is expected to do. Give it a fresh output directory each time: the driver appends to `fixture-raw.jsonl`, so a second run into the same directory mixes two runs into one summary. `python3 aggregate_fixture.py --raw fixture-raw.jsonl --csv fixture-summary.csv` rebuilds the summary from whatever records exist, one row per cell, with the columns `surface,cell,tool_count,n_ok,n_attempts,median,min,max,full_range,tools_json_bytes,errors` — the failed 12-tool verbose cell is kept as a row with `n_ok=0` and its error string, because a dropped cell would hide the most expensive result. On a slow host expect the same timeout this run hit: the first request after each tools-set change is the cold one, and the 12-tool verbose cell can exceed the 260-second client timeout before it produces a count.

What these numbers do not cover: other models, other quantisations, other templates. `prompt_eval_count` is tokenizer-specific, and a different chat template can move both the preamble and the per-tool slope. The values here are one model on one host on 2026-11-12 — a measurement of that configuration, not a constant of Ollama.

If you are sizing the wider agent cost equation rather than the tool term alone, the [browser MCP snapshot cost analysis](https://baeseokjae.github.io/posts/browser-mcp-snapshot-token-cost-2026/) does the same accounting for page snapshots. If you are still deciding how to structure the calls themselves, the [function calling guide](https://baeseokjae.github.io/posts/llm-function-calling-tool-use-guide-2026/) covers the mechanics, and the [Ollama API integration guide](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/) documents the surrounding request surface.
