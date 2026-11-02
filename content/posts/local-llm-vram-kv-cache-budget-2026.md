---
title: "Your 18GB GGUF Is Not an 18GB Budget: Sizing KV Cache and Context for a Local Coding Model"
date: 2026-11-01T13:00:00+00:00
tags:
  - local llm vram budget
  - kv cache size formula
  - ollama num_ctx memory
  - gguf file size vs ram
  - q8_0 kv cache flash attention
  - local coding model memory requirements
  - ollama context length default
  - gqa kv heads
  - vram calculator local llm
  - cpu ram local inference
  - large language model memory layout
  - local agent long context oom
description: "A GGUF file is the weights, not the budget. Run the KV-cache formula before you download, with a measured 0.5B check against it on a 12 GB CPU host and the q8_0 setting that saves nothing without Flash Attention."
draft: false
schema: "schema-local-llm-vram-kv-cache-budget-2026"
---

You download a 4-bit quantised model, the file is roughly 18 GB, you have 24 GB of VRAM, and the arithmetic looks settled. Then the agent session gets long, the server either dies or quietly starts answering with a fraction of the context you asked for, and the model that "fit yesterday" no longer fits.

The missing term is the key/value cache. It is not in the GGUF file, it is not on the model card, and it is allocated by the runtime at load time from the context length you set — not from the number of tokens you happen to send. On the 12 GB CPU box used for the measurements below, the same 0.5B model occupied 417 MB of reported model memory at a 2,048-token context and 794 MB at 32,768, with an identical file on disk.

This article gives you one formula to run before downloading, one measured check of that formula that you can repeat, and one warning about a setting that looks like it halves memory and does not.

## What the cache is, in one paragraph

Every transformer layer keeps, for every token in context, one key vector and one value vector per *key/value head*. The attention heads read them; they are not learned weights, they are state. The size is fixed by the model geometry and the cache element type:

```
bytes_per_token = 2 × n_layers × n_kv_heads × head_dim × bytes_per_element
```

The 2 is key plus value. `n_layers` and `n_kv_heads` come from the model's own `config.json`. `head_dim` is either an explicit field or `hidden_size / num_attention_heads`. `bytes_per_element` is 2 for f16 and about 1.0625 for q8_0, because q8_0 stores 32 values in 34 bytes — 8 bits each plus a scale.

Grouped-query attention is why this number is not as frightening as it looks. A model can have 64 attention heads and only 8 key/value heads; the cache scales with the second number. That is also why the per-token cost cannot be guessed from parameter count alone: two models of the same size can differ by 8x in cache cost depending on how aggressively they share KV heads.

Ollama's own documentation fixes the default that catches people: "By default, Ollama uses a context window size of 4096 tokens", overridable with `OLLAMA_CONTEXT_LENGTH` or per request with `num_ctx` ([Ollama FAQ](https://docs.ollama.com/faq)). A coding agent session with file contents and tool output routinely exceeds that. Either the runtime truncates, or you raise the context and the cache grows with it.

## Worked example one: the small model, measured

The tag used here is `qwen2.5:0.5b` at Q4_K_M. Its own config gives `num_hidden_layers` 24, `num_key_value_heads` 2, `num_attention_heads` 14 and `hidden_size` 896, so `head_dim` is 896 / 14 = 64 ([Qwen2.5-0.5B config.json](https://huggingface.co/Qwen/Qwen2.5-0.5B/raw/main/config.json)).

That yields 2 × 24 × 2 × 64 × 2 = 12,288 bytes per token, or 12.00 KiB. At a 32,768-token context the cache alone is 384 MiB — comparable to the model itself, on a model whose file is about 400 MB.

This is the shape of the problem in miniature: at a context the model advertises, the cache can be the same order of magnitude as the weights. Nobody notices on a 0.5B model because 384 MiB is noise. Scale the geometry up and the same term decides whether the card is big enough.

## Worked example two: a 32B model, computed not measured

Take Qwen3-32B, whose config was fetched and read for this article: 64 layers, 64 attention heads, 8 key/value heads, `head_dim` 128, 40,960 maximum positions ([Qwen3-32B config.json](https://huggingface.co/Qwen/Qwen3-32B/raw/main/config.json)).

2 × 64 × 8 × 128 × 2 = 262,144 bytes per token = 256 KiB for f16. With q8_0 packing at 34 bytes per 32 elements the same geometry costs 136 KiB per token.

| Context | f16 cache | q8_0 cache (with Flash Attention) |
|---|---|---|
| 8,192 tokens | 2 GiB | 1.06 GiB |
| 32,768 tokens | 8 GiB | 4.25 GiB |
| 40,960 tokens | 10 GiB | 5.31 GiB |

Every number in that table is **computed** from the config and the formula. None of it was measured on a 32B model — this host has no GPU and 12 GB of RAM. It is arithmetic you can redo in a spreadsheet in a minute, and that is the point: the term is predictable before you download anything.

Note what changed the number: not the parameter count, but 8 KV heads instead of 64, and a quantised cache. A dense 32B model without grouped-query attention would have cost eight times more per token and would not fit at that context on any consumer card.

## The measured check on this machine

The probe starts a private Ollama server, forces one load per cell at a requested `num_ctx`, reads the runner's `VmRSS` from `/proc/<pid>/status`, and confirms what the server actually honoured with `ollama ps`. Nothing else runs, so the only moving part is the cache allocation.

| num_ctx | KV type | Flash Attention | runner VmRSS | `ollama ps` SIZE |
|---|---|---|---|---|
| 2,048 | f16 | off | 494,748 kB | 417 MB |
| 8,192 | f16 | off | 567,752 kB | 492 MB |
| 32,768 | f16 | off | 862,668 kB | 794 MB |
| 2,048 | q8_0 | off | 494,220 kB | 417 MB |
| 8,192 | q8_0 | off | 568,064 kB | 492 MB |
| 32,768 | q8_0 | off | 862,896 kB | 794 MB |
| 8,192 | q8_0 | on | 521,648 kB | 442 MB |
| 32,768 | q8_0 | on | 678,308 kB | 593 MB |

The reported context matched the requested context in all eight rows, so no row is secretly a measurement of a different context.

From 2,048 to 32,768 tokens, f16 grew by 367,920 kB over 30,720 tokens: 11.98 KiB per token against 12.00 computed, an error of minus 0.20 percent. Subtracting the slope leaves a base of about 470 MB that barely moves across contexts (720 kB spread on eight rows), which is the Q4_K_M weights plus graph and allocator overhead. The slope is the portable part; the base is not.

## The trap: a setting that looks like half the memory

`OLLAMA_KV_CACHE_TYPE=q8_0` with default settings produced the same slope as f16: 12.00 KiB per token, 228 kB apart at 32,768 tokens, which is noise. The knob did nothing.

Ollama's documentation says why, in the sentence most people skim: the K/V cache "can be quantized to significantly reduce memory usage **when Flash Attention is enabled**". Re-running the same two cells with `OLLAMA_FLASH_ATTENTION=1` halved the slope: 156,660 kB over 24,576 tokens is 6.37 KiB per token against 6.38 computed, and 0.532x the f16 slope. The saving is real — but only after the precondition is met.

Two practical consequences. First, verify a memory setting by its effect on resident memory, not by the name of the flag; a quantised cache type on a backend that cannot run Flash Attention is inert, and you will only find out when the box swaps. Second, compare slopes, not single readings: the base also moved with Flash Attention (567,752 kB to 521,648 kB at 8,192 tokens), so a one-point comparison would have been misleading in the opposite direction.

## Turning it into a budget

The budget is three terms, and only one of them is on the download page:

```
resident ≈ weights (GGUF bytes) + KV cache at your context + runtime overhead
```

Work the numbers in the same unit before you buy anything. For a 32B-class model at a 32,768-token context, the cache term alone is 8 GiB at f16 or 4.25 GiB at q8_0 with Flash Attention. If your file is the 18 GB the title refers to — a figure this article takes from the reader's rule of thumb and does **not** verify for any specific 31B release — then 18 + 8 + 2 GB of overhead is 28 GB, which does not fit a 24 GB card at full context. The same model with a quantised cache lands near 24 GB: still on the edge, and still not something to plan around without measuring your own box.

Three corrections that change the answer more often than a bigger GPU:

- **Parallel slots multiply the cache.** `OLLAMA_NUM_PARALLEL` defaults to 1, and the docs state that required memory scales with it. A shared server sized for one user's context is not sized for four.
- **The context default is 4,096, not the model's maximum.** A setup that "fit yesterday" may have fit because the runtime was quietly using a small context. Raising `num_ctx` to the model's [advertised maximum](https://baeseokjae.github.io/posts/llm-context-window-comparison-2026/) is where the memory goes.
- **Quantising the cache is not free of preconditions.** It needs Flash Attention, which needs a backend and device that support it. Check the effect, not the flag.

When the total does not fit, the levers in order of cost are: lower the context to what the agent actually uses, quantise the cache if Flash Attention is available, reduce parallel slots, and only then move to a smaller model.

## Doing it on your own machine in ten minutes

The probe is small enough to read before you run it. It starts its own server on a free loopback port so it does not disturb a running instance, samples the runner's resident set after each load, records what `ollama ps` reports as the honoured context, and writes one CSV row per cell.

Files, all first-party and published with the article:

| File | What it is |
|---|---|
| [kv_budget_probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-budget-2026/scripts/kv_budget_probe.py) | The probe: context and cache-type matrix, RSS sampling, `ollama ps` cross-check |
| [kv_budget_prompt.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-budget-2026/kv_budget_prompt.txt) | The fixed 30-token fixture with a head and a tail token, kept for replay and hashing; the probe sends a 1-token generation because the allocation happens at load |
| [kv-budget-2026-11-01.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-budget-2026/kv-budget-2026-11-01.csv) | The eight measured rows behind the table above |
| [kv-budget-formula-check.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-budget-2026/kv-budget-formula-check.md) | Measured slope against the config-derived slope, with the residual explained |
| [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-budget-2026/method.md) | Server flags, sampling points, host, and what was deliberately not measured |

Point it at a model that fits your box. Two cells are enough to get your own slope: the same cache type at two contexts, resident memory at each, difference divided by the context difference. If your slope is within a quarter of the formula, you can trust the arithmetic for the model you actually want; if it is not, the runtime is allocating something the formula does not describe and the formula's answer for a bigger model is not safe to use.

## What this does and does not establish

Measured, on one CPU-only host with one model tag: the cache is allocated at load from `num_ctx`, it grows linearly at the formula's rate within 0.20 percent for f16 and 0.01 percent for q8_0 with Flash Attention, and the q8_0 setting is inert without Flash Attention.

Not measured, and not claimed: any throughput or tokens-per-second figure, any quality comparison, any GPU-backend behaviour, any multi-slot configuration, and any resident-memory number for a 32B or 27B model. The 32B figures are computed from its published config, and the 27B family is absent on purpose: the `google/gemma-3-27b-it` config returned HTTP 401 on both attempts, so its geometry is unverified here and no number for it appears in this article. One sample per cell was taken; repeat-run spread between identical configurations was 228 kB against a 368 MB slope, which is enough for a slope and not enough for sub-percent claims about the constant overhead.

The one-sentence version: the file you download is the smallest term in the budget, and the term that grows is the one nobody puts on the model card. Compute it before you download, then confirm it on your own machine with two loads.

If you have not chosen the model yet, [the model-selection comparison](https://baeseokjae.github.io/posts/best-local-llm-models-2026/) and [the coding-model shortlist](https://baeseokjae.github.io/posts/best-ollama-models-coding-2026/) are the better starting points; [the inference-engineering guide](https://baeseokjae.github.io/posts/llm-inference-engineering-guide/) explains PagedAttention and serving-side batching, which this article deliberately does not re-explain; and [the 31B local setup guide](https://baeseokjae.github.io/posts/gemma-4-local-setup-guide-2026/) covers the download half of the question.
