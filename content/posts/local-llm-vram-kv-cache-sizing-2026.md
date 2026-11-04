---
title: "Local LLM VRAM Planning 2026: The KV Cache Math Behind the Context You Can Actually Serve"
date: 2026-11-03T06:29:00+00:00
lastmod: 2026-11-03T06:50:12+00:00
tags:
  - local llm vram planning
  - kv cache bytes per token
  - gguf q4_k_m size
  - context length memory
  - gqa kv heads
  - hybrid attention sliding window
  - gemma 4 31b memory
  - qwen3-8b context
  - vram calculator
  - local llm concurrency memory
  - llama.cpp context size
description: "Does this model, quant and context fit your card? Compute weights plus KV from the model's own config at a pinned revision, with a per-model table, a hybrid-attention counterexample and a runnable planner."
draft: false
schema: "schema-local-llm-vram-kv-cache-sizing-2026"
---

A model card says 40,960 tokens. The Q4_K_M file is 4.68 GiB. The card has 12 GB. You set `-c 40960`, and one of three things happens: the load fails, the runtime spills layers to CPU and tokens per second collapse, or the server starts and silently serves a shorter context than you asked for.

Which of the three you get depends on a number that appears in none of those three places — the key/value cache the runtime allocates at load time from the context you request. This page computes it for four specific models from their own `config.json` at a pinned revision, turns it into a "largest context that fits this card" table, and ships a planner you can run offline.

If you searched for benchmark charts, this page will disappoint you on purpose. There are no throughput measurements here: this environment has no GPU, and inventing a tokens-per-second table is worse than saying so. What is here is arithmetic you can check in a minute, plus the one failure mode that arithmetic gets wrong.

## The budget is three terms

```
resident ≈ GGUF file size + KV cache at your context + runtime overhead
```

Only the first term is on the download page. The third term — compute buffers, CUDA context, the graph allocator — is machine- and backend-specific; the planner below takes it as a declared allowance and prints it separately, so you can see what you are assuming rather than have it hidden in a fudge factor.

The middle term is the one that changes with context:

```
bytes_per_token = 2 × n_layers × n_kv_heads × head_dim × bytes_per_element
```

Two for key plus value. `n_layers`, `n_key_value_heads` and `head_dim` come from the model's `config.json` — not from the parameter count, and not from the size of the file. Two 8B-class models can differ by 8× here depending on how many heads share keys and values.

Qwen3-8B, read from [its config](https://huggingface.co/Qwen/Qwen3-8B/raw/main/config.json) at revision `b968826d9c46dd6066d109eabc6255188de91218`: 36 layers, 8 KV heads, head_dim 128, and `max_position_embeddings` 40,960. That is 2 × 36 × 8 × 128 × 2 = 147,456 bytes per token — 144 KiB — which is 0.56 GiB at 4,096 tokens and 5.62 GiB at the native 40,960.

Same model, same file, a cache five times larger than the weights at the context the card advertises. That is the whole trap in one number.

## Four models, computed from their own configs

Every row below is computed at batch size 1 with an f16 cache, from the config fields saved at the revisions read on 2026-11-03, and the GGUF sizes are the published file sizes in the same repositories. None of it is a measured load.

| Model | Layers | KV heads × head dim | Native ctx | f16 KV B/token | KV at 8k | KV at native | Q4_K_M file |
|---|---|---|---|---|---|---|---|
| Qwen3-8B | 36 | 8 × 128 | 40,960 | 147,456 | 1.12 GiB | 5.62 GiB | 4.68 GiB |
| Qwen3-14B | 40 | 8 × 128 | 40,960 | 163,840 | 1.25 GiB | 6.25 GiB | 8.38 GiB |
| Devstral-Small-2507 | 40 | 8 × 128 | 131,072 | 163,840 | 1.25 GiB | 20.0 GiB | 13.35 GiB |
| Gemma 4 31B (hybrid) | 60 | 16 × 256 | 262,144 | see below | 1.41 GiB | 20.8 GiB | 17.07 GiB |

Config sources: [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B/raw/main/config.json), [Devstral-Small-2507](https://huggingface.co/mistralai/Devstral-Small-2507/raw/main/config.json), [Gemma 4 31B](https://huggingface.co/google/gemma-4-31B-it/raw/main/config.json). The file-size column comes from one mirror per model, each an `/api/models/<repo>/tree/main?blobs=true` listing read on 2026-11-03: the [unsloth Qwen3-8B GGUF tree](https://huggingface.co/api/models/unsloth/Qwen3-8B-GGUF/tree/main?blobs=true) behind 4.68 GiB, the [unsloth Qwen3-14B GGUF tree](https://huggingface.co/api/models/unsloth/Qwen3-14B-GGUF/tree/main?blobs=true) behind 8.38 GiB, the [unsloth Devstral GGUF tree](https://huggingface.co/api/models/unsloth/Devstral-Small-2507-GGUF/tree/main?blobs=true) behind 13.35 GiB, and the [unsloth Gemma 4 31B GGUF tree](https://huggingface.co/api/models/unsloth/gemma-4-31B-it-GGUF/tree/main?blobs=true) behind 17.07 GiB. Another quantiser's Q4_K_M is a different file with a different byte size, so treat the mirror as part of the number.

Read the Devstral row before you buy: a 13.35 GiB file whose native context needs 20 GiB of cache on top. The weights fit 24 GB comfortably; the context does not.

## Quantisation moves the left-hand term, not the right-hand one

Going from BF16 to Q4_K_M shrinks the file by roughly 3.3× for Qwen3-8B (15.26 GiB to 4.68 GiB). It does not touch the cache unless you also quantise the cache. With q8_0 packing — 32 elements in 34 bytes, 1.0625 bytes per element — the same 40,960-token context costs 2.99 GiB instead of 5.62, and the whole plan lands at 8.67 GiB including a 1 GiB allowance.

Ollama documents that this only works with Flash Attention enabled, and that the setting is global rather than per model ([Ollama FAQ](https://docs.ollama.com/faq)). A quantised cache type on a backend that cannot run Flash Attention is inert — the flag is accepted, the memory does not move. The CPU-only probe published with [the budget article](https://baeseokjae.github.io/posts/local-llm-vram-kv-cache-budget-2026/) shows exactly that: the same slope with `OLLAMA_KV_CACHE_TYPE=q8_0` until Flash Attention was turned on, then half.

## Where the single-slope formula fails: Gemma 4 31B

Take the naive rule to Gemma 4 31B and you get 2 × 60 × 16 × 256 × 2 = 983,040 bytes per token, or 240 GiB at its 262,144-token maximum. That number is correct arithmetic and a wrong plan. The config declares a `layer_types` list in which only 10 of 60 layers are full attention, with `global_head_dim` 512 and 4 global KV heads; the other 50 slide over a 1,024-token window.

A sliding layer does not grow with context. It holds one window, ever. So the cost is a slope plus a fixed term:

- 10 full layers: 2 × 10 × 4 × 512 × 2 = 81,920 bytes per token
- 50 sliding layers: 2 × 50 × 16 × 256 × 2 × 1,024 = 800 MiB fixed, per slot
- at 32,768 tokens: 2.50 GiB + 0.78 GiB = 3.28 GiB, not 30 GiB

This is the correction that matters most for 2026 models: if `layer_types` or `sliding_window` appears in a config, the per-token formula alone overestimates the cache by an order of magnitude, and a planner built on it will tell you a 24 GB card cannot run a 31B at 32k when the arithmetic says it can.

## Largest context that fits, at a declared 1 GiB overhead

Computed with the same fixtures: file size plus f16 cache plus 1 GiB for compute buffers and CUDA context, capped at the model's native context. If your runtime's overhead is larger, subtract it and recompute — the planner does this for you.

| Q4_K_M | 8 GiB | 12 GiB | 16 GiB | 24 GiB | 48 GiB |
|---|---|---|---|---|---|
| Qwen3-8B | 16,893 | 40,960 | 40,960 | 40,960 | 40,960 |
| Qwen3-14B | does not fit | 17,170 | 40,960 | 40,960 | 40,960 |
| Devstral-Small-2507 | does not fit | does not fit | 10,813 | 63,242 | 131,072 |
| Gemma 4 31B (hybrid) | does not fit | does not fit | does not fit | 67,485 | 262,144 |

Capped cells are written as the native context, not as the larger number the formula would allow. An 8 GiB card holds Qwen3-8B at 16,893 tokens and nothing else in this set; a 12 GB card holds it at the full 40,960 with about 0.7 GiB to spare, which is not a margin to plan a desktop session around once the display compositor takes its share.

## Concurrency multiplies the cache, not the weights

Four parallel slots at 32,768 tokens on Qwen3-8B is 18 GiB of cache against 4.5 GiB for one slot — the weights are loaded once, the cache is allocated per slot. A server sized for one user's long context is not sized for four users' long contexts, and the difference is not in the file size anyone quotes.

## The planner

`plan.py` reads a fixture of the four configs above and prints the breakdown, exiting non-zero on overflow so it can gate a launch script:

```
$ python3 plan.py --model qwen3-8b --quant Q4_K_M --context 40960 --vram 12
model    : qwen3-8b (Qwen/Qwen3-8B, native 40960 tokens, dense)
weights  : 4.68 GiB  (Q4_K_M GGUF file)
kv       : 5.62 GiB  (f16, 147,456 B/token x 40960)
overhead : 1.00 GiB  (declared allowance, not measured)
total    : 11.30 GiB
device   : 12.00 GiB  margin +0.70 GiB
verdict  : fits at the declared allowance
```

Full output of the two-slot run, unedited (the verdict line goes to stderr, so it prints before the buffered stdout when the terminal interleaves them):

```
$ python3 plan.py --model gemma-4-31b-it --quant Q4_K_M --context 32768 --parallel 2 --vram 24
model    : gemma-4-31b-it (google/gemma-4-31B-it, native 262144 tokens, hybrid)
weights  : 17.07 GiB  (Q4_K_M GGUF file)
kv       : 6.56 GiB  (f16, 81,920 B/token x 32768 + 0.78 GiB fixed window per slot, x2 slots)
overhead : 1.00 GiB  (declared allowance, not measured)
total    : 24.63 GiB
device   : 24.00 GiB  margin -0.63 GiB
verdict  : DOES NOT FIT - lower context, quantise the KV cache, or reduce parallel slots
```

Two slots on the hybrid model is the difference between fitting 24 GB and not: one slot totals 21.35 GiB, two slots 24.63 GiB.

Files, first-party and published with the article:

| File | What it is |
|---|---|
| [plan.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-sizing-2026/plan.py) | The planner: weights + KV + declared overhead, hybrid-aware, non-zero exit on overflow |
| [plan-fixtures.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-sizing-2026/plan-fixtures.json) | The four configs and their published GGUF sizes, with the Qwen3-8B revision pinned |
| [test_plan.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-vram-kv-cache-sizing-2026/test_plan.py) | Six tests (14 assertions) pinning 147,456 B/token, 5.62 GiB at 40,960, the 4× slot multiplier and the hybrid fixed term |

To add your own model, copy a config object into the fixtures file. The planner reads six fixture fields and nothing else; `num_hidden_layers`, `num_key_value_heads`, `head_dim` and `gguf_gib` drive the arithmetic, and the other two are for display:

- `num_hidden_layers`, `num_key_value_heads`, `head_dim` — from the model's `config.json`
- `max_position_embeddings` — from `config.json`; printed in the header and used only to cap the "fits" search
- `gguf_gib` — an object of `{"Q4_K_M": 4.68, ...}`, one entry per quant you intend to plan for, each value being the published file size in bytes divided by 1024³
- `repo` — the model id, printed in the header; if you omit it the printer says `repo not recorded` instead of failing

`hybrid` is the only optional block, and it needs all five of `full_layers`, `sliding_layers`, `window`, `global_head_dim`, `global_kv_heads`. Add it only if the config carries `layer_types` or `sliding_window`: the mere presence of the key switches the model onto the hybrid branch, so a `hybrid` block invented for a dense model produces a wrong total rather than a denser one. `revision` is optional bookkeeping, never read by the arithmetic.

`plan.py --list` shows what loaded, and `python3 plan.py --model <name> --quant <quant> --context <n> --vram <GiB>` prints the breakdown and exits 1 when the total exceeds the card.

## What this page does not establish

Every number above is arithmetic from published configs and file sizes, not an observed successful load: no GPU was available for this run. The formula itself was validated on a CPU-only host against a 0.5B model in the budget article — 11.98 KiB per token measured against 12.00 computed, and 6.37 against 6.38 for q8_0 with Flash Attention — which validates the arithmetic, not GPU behaviour, and not any large model.

Also out of scope: throughput, quality, tokens per second, vendor performance claims, whether a given runtime honours `layer_types` rather than allocating a uniform cache per layer, and vision projectors, which ship as separate `mmproj` files in the Gemma repositories and are not in any figure here.

Two gated repositories stayed gated: [meta-llama/Llama-3.3-70B-Instruct](https://huggingface.co/api/models/meta-llama/Llama-3.3-70B-Instruct) reports `gated: manual` and both it and `google/gemma-3-27b-it` returned 401 for `config.json` from this host. Neither has a per-token figure here, and neither appears in any table above; the 70B is named only because it was the fifth repo the fixture plan asked for and could not be measured the same way.

If your runtime reports a served context shorter than the one you requested, that is a different failure from the one this page predicts — [the truncation diagnosis](https://baeseokjae.github.io/posts/ollama-silent-context-truncation-2026/) and [the overflow diagnosis](https://baeseokjae.github.io/posts/llama-server-context-overflow-diagnosis-2026/) cover it. Once the model fits, [the payback model](https://baeseokjae.github.io/posts/local-llm-rig-cost-payback-2026/) turns a throughput number into a purchase decision, and [the model-list page](https://baeseokjae.github.io/posts/best-local-llm-models-2026/) is the place to choose between these four.
