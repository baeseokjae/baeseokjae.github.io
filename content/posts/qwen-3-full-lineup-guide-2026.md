---
cover:
  alt: RockB — AI tools and engineering guides
  image: /images/og-default.png
  relative: false
date: 2026-05-01 00:05:54+00:00
description: 'The original Qwen3 lineup: verified dense and MoE sizes, context limits,
  thinking controls, and memory estimates for local deployment.'
draft: false
lastmod: 2026-11-01T15:52:30+00:00
schema: schema-qwen-3-full-lineup-guide-2026
tags:
- qwen3
- open-source-llm
- ai-models
- local-ai
- mixture-of-experts
title: 'Qwen 3 Model Guide 2026: Original Lineup, Sizes, Context and Memory'
---

Qwen3's original open-weight release is dated 29 April 2025 on the Qwen blog. It contains six dense models and two mixture-of-experts (MoE) models. This guide covers that release only. Later Qwen3 refreshes and the Qwen3.x families have their own cards, sizes and licenses, and a tag name you copy from this page today may not resolve to the checkpoint described here. [Source: Qwen's release announcement](https://qwenlm.github.io/blog/qwen3/).

> **Refresh note — 1 November 2026:** Per-checkpoint context now follows the launch table verbatim, the Qwen3-8B card's native-versus-YaRN wording is quoted separately, and the Ollama section documents tag drift with values observed on 1 November 2026. The earlier correction — wrong release year, wrong dense-model count and size range, and advertised context mixed with runtime memory — still applies to versions of this page published before 7 October 2026.

## The Original Qwen3 Lineup

The launch table prints layer counts and a context value for every checkpoint. Those values are reproduced below as published; the MoE rows also list 128 experts total with 8 activated.

| Model | Architecture | Total / active parameters | Layers | Context in the launch table |
|---|---|---|---|---|
| Qwen3-0.6B | Dense | 0.6B | 28 | 32K |
| Qwen3-1.7B | Dense | 1.7B | 28 | 32K |
| Qwen3-4B | Dense | 4B | 36 | 32K |
| Qwen3-8B | Dense | 8B | 36 | 128K |
| Qwen3-14B | Dense | 14B | 40 | 128K |
| Qwen3-32B | Dense | 32B | 64 | 128K |
| Qwen3-30B-A3B | MoE | 30B total / 3B active | 48 | 128K |
| Qwen3-235B-A22B | MoE | 235B total / 22B active | 94 | 128K |

The launch post lists the six dense checkpoints as open-weighted under Apache 2.0. The two MoE checkpoints ship under their own model-card terms, so read the card for the exact weights you plan to host instead of carrying the dense-model license across the whole family.

The launch list does not contain a Qwen3-72B. A reference to Qwen2.5-72B in a comparison is a different family, not another row here.

### Context Capacity Is Per-Checkpoint and Per-Runtime

The 32K in the table for 0.6B, 1.7B and 4B is not a placeholder for "128K with extension". Those three checkpoints are advertised at 32K, and the 8B, 14B, 32B and MoE rows at 128K.

The [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B) states the same limit in more precise terms: 32,768 tokens natively and 131,072 tokens with YaRN. Those are one checkpoint, two configurations. Enabling the extension is a server-side change to the serving runtime, not a property the model turns on by itself, and the runtime you use may ship a shorter default.

Treat both numbers as advertised capacity, not as measured long-context recall. A runtime that accepts a 128K prompt has not been shown to retrieve an instruction placed near the start of one. If your application depends on the long window, test retrieval at the depth you actually use before committing to it.

## Dense and MoE Models: Compute and Memory Are Different Constraints

The active-parameter count estimates how much of the model takes part in computing one token. It says nothing about how many weights you must store. A 30B-total MoE is not a 3B download, and a large model does not become small because few experts fire per token.

The Qwen3-2507 refresh makes the gap easy to see. The [Qwen3-30B-A3B-Instruct-2507 card](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507) reports 30.5B parameters in total and 3.3B activated, with 29.9B non-embedding, 48 layers, 128 experts, and 262,144 tokens of native context. The activated figure stayed near the 2025 model's shape; the footprint did not shrink.

Plan separately for weight storage, resident weights, KV cache, temporary buffers and the rest of the application. Offloading moves weights to host memory rather than deleting them, and it changes the latency and throughput trade-off. Do not assume the speed of a dense model with the same active-parameter count without measuring on the hardware you intend to use.

### Weight-Only Arithmetic for Planning

The figures below come from a short arithmetic check: parameters × bits per weight ÷ 8, in decimal GB. It was computed on 2026-10-31 with Python 3.12.3, no CUDA device and no model weights downloaded. It is a private local author check of the formula, not a published dataset, and it reports no VRAM, bandwidth or throughput result.

| Checkpoint | Parameter count used | 16-bit weights | 4-bit weights |
|---|---|---|---|
| Qwen3-4B | 4.0B | 8.0 GB | 2.0 GB |
| Qwen3-8B | 8.2B (from the card) | 16.4 GB | 4.1 GB |
| Qwen3-14B | 14.0B | 28.0 GB | 7.0 GB |
| Qwen3-32B | 32.0B | 64.0 GB | 16.0 GB |
| Qwen3-30B-A3B | 30.5B | 61.0 GB | 15.25 GB |
| Qwen3-235B-A22B | 235.0B | 470.0 GB | 117.5 GB |

Only the 8B row uses a card-level total; the rest use rounded label sizes, which understates the MoE rows. Every row excludes KV cache, activation buffers, tokenizer and framework overhead, and real quantized formats add per-block scales and may mix precisions. The arithmetic is one line, so redo it with your own numbers rather than trusting the table.

The practical consequence: a 14B checkpoint's roughly 28 GB of 16-bit weights cannot fit in a machine with 16 GB of total memory, and a 30B MoE's 61 GB does not fit in 64 GB of VRAM once the cache and the rest of the stack are counted. On unified-memory hardware the operating system shares that pool; on a discrete GPU, system RAM and VRAM are separate resources.

## Thinking Controls Depend on the Backend

The original Transformers chat template for Qwen3-8B contains a branch that writes an empty think block when `enable_thinking` is defined and set to false. That is a template-level switch. The `/think` and `/no_think` markers used with the same template are prompt-level switches. Neither is a universal request parameter, and a hosted API may expose something else entirely.

Ollama handles it differently: thinking-capable models emit a `thinking` field that separates the reasoning trace from the final answer, and the available controls are declared per model. `POST /api/show` returns a top-level `thinking` object with the supported `values` and a `default`, and `values: [false]` means the model does not support thinking at all. Query the model you loaded instead of assuming a boolean flag. [Source: Ollama thinking documentation](https://docs.ollama.com/capabilities/thinking).

Longer reasoning spends more tokens and time and does not guarantee a better answer. For a coding task, judge the patch and its tests, not the explanation of the patch.

## Running an Original Qwen3 Model with Ollama

Ollama's library page is a live surface: the tag you type resolves to whatever artifact the library serves at that moment. On 1 November 2026 the [qwen3 tag list](https://ollama.com/library/qwen3/tags) reported `qwen3:30b` at 19GB with a 256K context window, `qwen3:235b` at 142GB with 256K, `qwen3:32b` at 20GB with 40K, and `qwen3:14b` at 9.3GB with 40K. Those numbers are a single-day observation, not a specification, and the page's download counter read 42.1M when it was fetched on 1 November 2026.

Note the mismatch worth caring about: the launch table advertises 128K for Qwen3-32B, while the `qwen3:32b` artifact on that day reported 40K. A tag is a packaging decision by the library, not a synonym for the checkpoint. The `30b` and `235b` tags report 256K, which is longer than the 2025 launch values, because they now serve later artifacts under the same name.

So pin what you actually ran. Install from the [Ollama download page](https://ollama.com/download), pull an explicit tag, and record the digest:

```bash
ollama pull qwen3:8b
ollama run qwen3:8b
ollama ps
```

The tag list prints a digest beside each tag — `ad815644918f` sits next to `qwen3:30b` — so quote the digest shown for the tag you pulled whenever you compare results, because the tag name alone can resolve to a different artifact later; `ollama ps` shows what is loaded and its CPU/GPU split. Download time and generation speed depend on the artifact, connection and hardware, so no setup-time or tokens-per-second number is claimed here.

A single request, as documented rather than as a performance test:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "Explain a binary search boundary case."}],
  "think": true,
  "stream": false
}'
```

For MoE checkpoints use the exact tag from the list and check which checkpoint it resolves to before you publish results. If you need the April 2025 weights specifically, look for a tag or a Hugging Face revision that still points at them rather than assuming the family name does.

If you want to run one dense checkpoint end to end, the [Qwen3-32B local deployment guide](/posts/qwen-3-32b-local-guide-2026/) walks through that path; for a wider shortlist, see the [Ollama coding model options](/posts/best-ollama-models-coding-2026/).

## Later Refreshes and Families (bounded note)

Two things sit outside the table above and are worth knowing before you quote this page.

Qwen3-2507 is a refresh with separate checkpoints rather than an update to the April files. Of that refresh only Qwen3-30B-A3B-Instruct-2507 was re-opened for this revision, where it reports 30.5B total, 3.3B activated and 262,144 native context. Other 2507 variants, their sizes and their dates were not re-verified here, so this page does not state them.

The [Qwen organisation listing](https://huggingface.co/Qwen) also carries later families, including Qwen3.8-27B and a Qwen3.8-Flash-Next collection whose page timestamp reads 2026-08-26. A collection timestamp is not an announcement date, and the listing carries no license or parameter data, so nothing here should be read as a Qwen3.8 specification.

## How to Choose a Size Without Inventing a Ranking

Work through constraints in this order: does the checkpoint fit in the memory you can dedicate after the OS and the rest of the stack; does its native context cover your prompts without an extension you cannot verify; is the license acceptable for how you redistribute or serve it; does your runtime expose the thinking control you need. Only then compare quality.

For each candidate, save the prompt, the exact checkpoint and digest, the quantization, the runtime version, the configured context and output limits, elapsed time, peak memory and the result. Keep failed runs. Separate first-token delay from completion time, and single-request behaviour from concurrent serving. A smaller model that fits and passes your tests beats a larger one that spills to host memory, and this page makes no claim about which size wins on any benchmark.

## FAQ

### Does every original Qwen3 model have the same context window?

No. The 0.6B, 1.7B and 4B checkpoints are advertised at 32K; the 8B, 14B, 32B and both MoE checkpoints at 128K. The 8B card restates that as 32,768 native tokens and 131,072 with YaRN, which requires a runtime setting.

### Does a low active-parameter count mean low memory use?

No. Active parameters describe compute per token; the stored weights still scale with the total. A 30B-total MoE needs roughly the memory of a 30B dense model for weights alone.

### Does `qwen3:30b` still mean the April 2025 MoE model?

Not necessarily. On 1 November 2026 that tag reported 19GB and a 256K context window, which does not match the 2025 launch values. Compare the digest the tag page currently lists against the one you recorded, or pull from a pinned revision.

### Is local inference automatically private?

A local model can keep inference on the machine, but tools, remote backends and integrations may still transmit data. Check the whole application and its network behaviour rather than inferring privacy from a model name.

### Where should a team start if it needs agent-grade output?

That is a task-fit question, not a lineup question. The [local coding model task-success notes](/posts/local-coding-model-agent-task-success-2026/) cover how to decide whether a local checkpoint is good enough for agent work, and the [local LLM size and memory guide](/posts/best-local-llm-models-2026/) covers the memory side across families.
