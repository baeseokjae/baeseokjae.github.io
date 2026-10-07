---
cover:
  alt: RockB — AI tools and engineering guides
  image: /images/og-default.png
  relative: false
date: 2026-05-01 00:05:54+00:00
description: 'The original Qwen3 lineup: verified dense and MoE sizes, context limits, thinking controls,
  and memory estimates for local deployment.'
draft: false
schema: schema-qwen-3-full-lineup-guide-2026
tags:
- qwen3
- open-source-llm
- ai-models
- local-ai
- mixture-of-experts
title: 'Qwen 3 Model Guide 2026: Original Lineup, Sizes, Context and Memory'
lastmod: 2026-10-08T00:55:31+09:00
---

Qwen3's original open-weight release arrived on April 29, 2025. It contains six dense models and two mixture-of-experts (MoE) models. This guide covers that release; later Qwen3 updates and Qwen3.x families must be checked against their own model cards. [Source: Qwen's release announcement](https://qwenlm.github.io/blog/qwen3/).

> **Correction — October 7, 2026:** The previous version gave the wrong release year, dense-model count and size range. It also mixed advertised context limits with runtime memory requirements. Those claims have been corrected; unsupported benchmark rankings and hardware-speed promises have been removed.

## The Original Qwen3 Lineup

| Model | Architecture | Total / active parameters | Advertised context at launch |
|---|---|---|---|
| Qwen3-0.6B | Dense | 0.6B | 32K |
| Qwen3-1.7B | Dense | 1.7B | 32K |
| Qwen3-4B | Dense | 4B | 32K |
| Qwen3-8B | Dense | 8B class | Up to 128K with extension |
| Qwen3-14B | Dense | 14B | Up to 128K with extension |
| Qwen3-32B | Dense | 32B | Up to 128K with extension |
| Qwen3-30B-A3B | MoE | 30B total / 3B active | Up to 128K with extension |
| Qwen3-235B-A22B | MoE | 235B total / 22B active | Up to 128K with extension |

The launch list does not contain a Qwen3-72B model. A reference to Qwen2.5-72B in a comparison is a different model family, not another row in this lineup. The original models were released under Apache 2.0; review the license terms when redistributing them. [Source: original model list](https://qwenlm.github.io/blog/qwen3/).

### Context Capacity Is Version- and Runtime-Specific

The [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B) specifies 32,768 native tokens and 131,072 with YaRN. A serving configuration must actually enable the supported extension; an advertised maximum is not a promise that every runtime defaults to it. Later checkpoints can have different limits or separate thinking and instruction variants.

Before deployment, record the full checkpoint name, quantization, runtime version, configured context and output limit. Reserve room for both the prompt and the answer. Testing whether a model can accept a long prompt is different from testing whether it can reliably use information near the beginning of that prompt.

## Dense and MoE Models: Compute and Memory Are Different Constraints

The active-parameter count describes how much of an MoE model participates in a token's computation. It does not describe the size of all stored weights. A 30B-total model is not a 3B download, and an 80B-total model from a later family does not become a small-memory model merely because its active count is low.

Plan separately for weight storage, resident weights, KV cache, temporary buffers and the rest of the application. CPU offloading can make a model usable when it does not fit entirely in GPU memory, but changes the latency and throughput tradeoff. Do not promise the speed of a dense model with the same active-parameter count without measurements on the intended runtime and hardware.

### Weight-Only Arithmetic for Hardware Planning

The following estimates use the size labels as rounded parameter counts. They are arithmetic examples, not measured VRAM requirements or exact download sizes.

| Model size | Approximate 16-bit weights | Idealized 4-bit weights |
|---|---|---|
| 4B | 8 GB | 2 GB |
| 8B | 16 GB | 4 GB |
| 14B | 28 GB | 7 GB |
| 32B | 64 GB | 16 GB |
| 30B total MoE | 60 GB | 15 GB |
| 235B total MoE | 470 GB | 117.5 GB |

Calculation: `parameters × bits per weight ÷ 8`, using decimal GB. Real formats add overhead and may mix precisions. Runtime allocations are additional. In particular, a 14B model's roughly 28 GB of 16-bit weights cannot fit in a machine with only 16 GB of total memory.

On unified-memory hardware, the operating system and other applications share the same pool. On a discrete GPU, system RAM and VRAM are separate resources. Measure the actual deployment instead of treating either memory label as fully available to the model.

## Thinking Controls Depend on the Backend

The original Transformers chat template provides `enable_thinking`. With thinking enabled, `/think` and `/no_think` act as prompt-level switches; setting `enable_thinking=False` disables thinking in that template. These are not universal API parameters for every hosting provider. See the [Qwen3-8B usage instructions](https://huggingface.co/Qwen/Qwen3-8B).

Current Ollama exposes a `think` field for models that support it and separates thinking output from the answer. A generation-length cap is not automatically a separate thinking-only budget. Consult the model's capabilities and the [Ollama thinking documentation](https://docs.ollama.com/capabilities/thinking) before relying on a control.

Longer reasoning can consume more tokens and time; it does not guarantee a better answer. For a coding task, evaluate the resulting patch and tests. A plausible explanation is not a substitute for checking whether the code runs.

## Running an Original Qwen3 Model with Ollama

For a broader shortlist, compare the [Ollama coding model options](/posts/best-ollama-models-coding-2026/). For hardware planning across model families, see the [local LLM model and memory guide](/posts/best-local-llm-models-2026/).

Install the appropriate package from [Ollama's download page](https://ollama.com/download). This example selects the 8B tag rather than assuming that an unqualified family name identifies the desired checkpoint:

```bash
ollama pull qwen3:8b
ollama show qwen3:8b
ollama run qwen3:8b
ollama ps
```

`ollama show` helps inspect the chosen artifact; `ollama ps` shows the loaded model and CPU/GPU placement. Download duration and generation speed depend on the artifact, connection and hardware, so there is no universal five-minute setup or tokens-per-second guarantee.

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "Explain a binary search boundary case."}],
  "think": true,
  "stream": false
}'
```

This is a documentation-based example, not a performance test performed for this article. For MoE models, use the exact available tag from the [Ollama Qwen3 tag list](https://ollama.com/library/qwen3/tags), such as `qwen3:30b`, and check which checkpoint it currently resolves to. Some family tags now select later updates. Record the model ID/digest for repeatable comparisons.

Ollama also provides [compatibility with parts of the OpenAI API](https://docs.ollama.com/api/openai-compatibility). Test the endpoints, tool calls and output handling used by your application; changing a base URL is not proof of full compatibility.

## How to Choose a Size Without Inventing a Ranking

Begin with a model that fits the intended memory and context budget. Define a small set of representative tasks and the tests that decide whether each result is correct. Compare the candidate with a smaller model before increasing size.

For each run, save the prompt, checkpoint, quantization, runtime configuration, elapsed time, peak memory and result. Keep failed runs. Separate first-token delay from answer completion time, and separate single-request performance from concurrent serving.

Published benchmarks can help select candidates, but compare the same task definition and evaluation setup. Model version, reasoning budget, tool harness and sampling policy can change the result. This article does not reproduce the earlier cross-model benchmark table because its values and evaluation conditions were not sufficiently documented.

## FAQ

### Does every original Qwen3 model have the same context window?

No. Use the launch table for the original release and the exact model card for deployment. Later versions and runtime settings can differ from both.

### Does a low active-parameter count guarantee low VRAM use?

No. Total stored weights still matter, together with cache and runtime allocations. Offloading changes where those weights reside; it does not remove them.

### Which model is best for coding?

This guide establishes the original lineup and deployment constraints, not a measured coding leaderboard. Compare candidates on your own code, tests and latency limits before choosing one.

### Is local inference automatically private?

A local model can keep inference on the machine, but tools, remote backends and integrations may still transmit data. Check the complete application and network behavior rather than inferring privacy from a model name.
