---
cover:
  alt: Devstral Small 2 local setup fit check across 16GB, 24GB and Apple unified memory
  image: /images/devstral-small-2-local-setup-guide-2026.png
  relative: false
date: 2026-04-30 06:04:25+00:00
lastmod: 2026-11-16 15:17:22+00:00
description: Devstral Small 2 is a 24B model whose Q4_K_M blob Ollama labels 15GB is 14.14 GiB of weights. Fit table for 16GB, 24GB and Apple unified memory with a KV-cache budget computed from the official config, and three setup paths.
draft: false
schema: schema-devstral-small-2-local-setup-guide-2026
tags:
- devstral small 2
- local AI
- mistral
- coding agent
- ollama
- vllm
- llama.cpp
title: 'Devstral Small 2 Local Setup 2026: Fit Check First - 24B at Q4 Is a 14.1 GiB Blob, So What Actually Runs on 16GB, 24GB and Apple Unified Memory'
---

Devstral Small 2 is a 24B coding model from Mistral AI. The number that decides whether you can run it is not the parameter count but the weight file: the Q4_K_M blob that Ollama serves for this model is listed on the tag page as "15GB", and the registry manifest behind that label is 15,177,370,240 bytes — 14.14 GiB ([Ollama tag page](https://ollama.com/library/devstral-small-2/tags), checked 2026-11-02T16:42:04Z; [registry manifest](https://registry.ollama.ai/v2/library/devstral-small-2/manifests/24b-instruct-2512-q4_K_M), checked 2026-11-02T16:55:25Z). Those two numbers are the same file described in two units, and the difference between them decides the 16GB case: 14.14 GiB of weights inside a 16 GiB budget leaves about 0.66 GiB for KV cache and runtime overhead, which is about 4,300 tokens of context at the very most — not a usable coding-agent configuration. That is why the fit check comes before the install commands in this version of the guide.

This is a refresh of the April 2026 setup guide. Three things in the original were wrong and are corrected here: the model was released on December 9, 2025, not December 10; the CPU path was described twice with incompatible memory figures; and the fit table mixed the tag page's decimal-GB labels with binary-GiB memory budgets, which understated every total. The three setup methods, the quant table and the troubleshooting section are kept.

## Does Devstral Small 2 Fit Your Machine?

The table below is the decision. Weight sizes are the exact model-layer byte counts from the Ollama registry manifests, converted to GiB; the tag page prints the same blobs as 15GB, 26GB and 48GB in decimal units. Context limits are computed from the official checkpoint config plus a 1.2 GiB runtime overhead allowance (computed, not measured - the arithmetic is in the next section).

| Memory you have | Q4_K_M (14.14 GiB) | Q8_0 (24.13 GiB) | FP16 (44.73 GiB) |
|---|---|---|---|
| 8GB | No - weights exceed it | No | No |
| 12GB | No - weights exceed it | No | No |
| 16GB | About 4,300 tokens at most, i.e. not usable | No | No |
| 24GB | Yes: about 56,800 tokens | No - 25.96 GiB at 4096 | No |
| 32GB | Yes: about 109,200 tokens | Yes, short context only: about 43,700 tokens | No |
| 48GB | Yes: about 214,000 tokens | Yes: about 148,600 tokens | Yes at 4096 only: 46.56 GiB total, 13,500-token ceiling |
| 64GB | Yes: about 318,900 tokens | Yes: about 253,400 tokens | Yes: about 118,400 tokens |
| 96GB or more | Yes, the full 393,216-token position limit at 75.34 GiB | Yes: the full 393,216-token position limit at 85.33 GiB | Yes: about 328,000 tokens |

Three consequences worth stating plainly, because the old page left them ambiguous:

- A 16GB GPU is not a Devstral Small 2 card, but not for the reason the old page gave. The weights do fit: 14.14 GiB of Q4_K_M plus 1.2 GiB of assumed overhead and a 4,096-token KV cache totals 15.96 GiB, which is 40 MiB under a 16 GiB budget. Forty megabytes is not a working margin - desktop drivers and the display reserve take more than that before the model loads - and it caps context at about 4,300 tokens at the very most. There is no configuration where this model is resident and useful in 16 GiB.
- A 16GB system-RAM laptop with no GPU is not a Devstral Small 2 machine either. The previous FAQ claimed 0.5-2 tokens per second at 4096 context on exactly that configuration. That figure is withdrawn: it was never measured, and the exact arithmetic leaves 0.66 GiB for KV cache after weights and overhead, about 4,300 tokens, before the operating system itself is counted.
- Apple Silicon works because unified memory is one pool. A 32GB Mac can host the Q4_K_M build with a usable context; a 16GB Mac hits the same 0.66 GiB ceiling a 16GB PC does.

If your machine is the 16GB row, the honest options are a smaller coding model, a hosted endpoint, or a machine with more memory. This guide will not invent a tokens-per-second figure to make the 16GB case look workable.

## Why the Weight Blob Is the Number That Decides

Three separate quantities get conflated in most "can I run it" answers: the weight file, the KV cache, and the runtime's own overhead.

The weight file is fixed by the quantisation you pick. Ollama publishes three local sizes for this model, and they are very different products in memory terms: Q4_K_M, Q8_0 and FP16. The tag page prints them as 15GB, 26GB and 48GB ([Ollama tag page](https://ollama.com/library/devstral-small-2/tags)). Those are decimal labels; the registry manifests give the byte counts that matter when you compare against VRAM, which is sold in binary units. The model layers are 15,177,370,240 bytes (14.14 GiB), 25,909,742,208 bytes (24.13 GiB) and 48,032,074,336 bytes (44.73 GiB) respectively, from the [Q4_K_M](https://registry.ollama.ai/v2/library/devstral-small-2/manifests/24b-instruct-2512-q4_K_M), [Q8_0](https://registry.ollama.ai/v2/library/devstral-small-2/manifests/24b-instruct-2512-q8_0) and [FP16](https://registry.ollama.ai/v2/library/devstral-small-2/manifests/24b-instruct-2512-fp16) manifests, checked 2026-11-02T16:55:25Z and re-checked byte-identically 2026-11-16. Each manifest also carries a 3,418-byte chat template layer and a 21-byte params layer (3,439 bytes beyond the weights), plus a separate 420-byte container-image config blob outside that layer sum - immaterial here.

That conversion is not pedantry. Reading "15GB" as 15 GiB makes a 16GB machine look 0.86 GiB worse off than it is, and the same mistake in the other direction - treating a 24 GiB card as 24 GB - quietly overstates how much context fits. Both errors appeared in the previous version of this table; every figure below is now derived from bytes.

The KV cache is proportional to context length. From the official checkpoint config ([config.json](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/raw/main/config.json), checked 2026-11-02T16:42:33Z), the text stack is 40 layers with 32 attention heads and 8 key/value heads at head dimension 128, and `sliding_window` is null, meaning every layer attends over the full context rather than a sliding window.

That gives 2 x 40 layers x 8 KV heads x 128 = 81,920 values per token. At two bytes per value (f16 KV, the llama.cpp default) that is 160 KiB per token, or 156.25 MiB per 1,000 tokens - 5.0 GiB at 32K context and 60 GiB at the 393,216-token position limit. An fp8 KV cache halves these figures, which is the single cheapest lever if you are close to a memory ceiling.

Runtime overhead is the softest term. The calculator behind this table assumes 1.2 GiB for CUDA context, graph buffers and fragmentation. That is an assumption, not a measurement, and on a 24GB card it shifts the maximum usable context by a few thousand tokens. It does not change the Q4_K_M or Q8_0 verdicts from 24GB up. It does decide the two tight cells: with exact bytes the arithmetic puts 4,096 tokens of Q4_K_M at 15.96 GiB, so the 16GB cell turns on whether 40 MiB survives the driver and display reserve, and FP16 on a 48 GiB card clears 4,096 tokens by only 1.45 GiB - a larger overhead allowance would sink that cell too.

## What Is Devstral Small 2?

Devstral Small 2 is Mistral's 24B open-weight coding model, released December 9, 2025 under Apache 2.0, and Mistral reports 68.0% on SWE-bench Verified for it. That score is vendor-reported: the launch post states the number and names no harness, so treat it as the vendor's own figure rather than an independently reproduced result. Mistral's launch post describes the model as placing "firmly among models up to five times its size while being capable of running locally on consumer hardware" ([Mistral launch post](https://mistral.ai/news/devstral-2-vibe-cli), checked 2026-11-02T16:55:32Z).

The checkpoint is a model using the Mistral3 architecture that carries a 24-layer Pixtral vision tower alongside the text stack, and Ollama's registry lists these tags as accepting text and image input. Coding is still the reviewed use case; neither source says anything about vision quality, and this guide makes no claim about it.

### Context length: 256K, 384K, or 393,216?

All three numbers are in circulation and they come from different places:

- Mistral's model card lists **Context 256k** ([model documentation](https://docs.mistral.ai/models/devstral-small-2-25-12), checked 2026-11-02T16:42:04Z).
- Ollama's tag page lists a **384K context window** for the local tags.
- The checkpoint's `max_position_embeddings` is **393216**, which is 384K in binary units.

Treat 256K as the vendor card figure and 384K as the registry/config figure. Do not treat either as a tested ceiling on your hardware: the KV math above shows that the position limit needs 60 GiB of cache on its own.

### API deprecation, and what it does and does not change for self-hosting

Mistral's documentation marks Devstral Small 2 as **deprecated**, with a deprecation date of 2/27/2026 and **Mistral Medium 3.5** named as the replacement ([model documentation](https://docs.mistral.ai/models/devstral-small-2-25-12), checked 2026-11-02T16:42:04Z). The launch post gives the post-free-period API prices as "$0.40/$2.00 per million tokens (input/output) for Devstral 2 and $0.10/$0.30 for Devstral Small 2", so the Small 2 figure is $0.10 input and $0.30 output per million tokens ([Mistral launch post](https://mistral.ai/news/devstral-2-vibe-cli), checked 2026-11-02T16:55:32Z).

Deprecation governs the hosted endpoint. It does not touch the licence or the downloadable weights, which remain Apache 2.0, and the Ollama registry still serves all three local tags. What changes is the framing: this is no longer "the cheapest way to use Devstral Small 2 through an API", it is the model you run yourself precisely because the API path is closing. Any guide that still pitches the hosted endpoint as the default is out of date.

## The Memory Budget, Computed

For Q4_K_M, weights 14.14 GiB plus 1.2 GiB overhead plus the KV term:

| Context | KV cache | Total |
|---|---|---|
| 4,096 | 0.62 GiB | 15.96 GiB |
| 16,384 | 2.50 GiB | 17.84 GiB |
| 32,768 | 5.00 GiB | 20.34 GiB |
| 131,072 | 20.00 GiB | 35.34 GiB |
| 393,216 | 60.00 GiB | 75.34 GiB |

Every figure in that table is computed from a published blob size and the official config; none is a measurement of a running 24B model. To redo it for another quant, substitute the model-layer bytes divided by 1,073,741,824 and keep the 156.25 MiB per 1,000 tokens term (160 KiB per token; the round 160 MiB figure you may have seen elsewhere is per 1,024 tokens), or half it if you run an fp8 KV cache. For Q8_0 (24.13 GiB) that gives 25.96 GiB total at 4,096 and 27.83 GiB at 16,384, and the full 393,216-token position limit at 85.33 GiB; for FP16 (44.73 GiB) it gives 46.56 GiB at 4,096 and 48.43 GiB at 16,384, which is why FP16 needs a 48 GiB card for even a short context and a 64 GiB card for anything useful. Any budget beyond the position limit buys nothing: 393,216 is where the checkpoint's positions stop, so a 128 GiB card caps out at the same 393,216 tokens as a 96 GiB one.

The author's calculator script, its outputs and the CPU probe log are private working files kept with this article's research notes for the review run; they are not published downloads, so treat these numbers as reproducible arithmetic rather than as a packaged tool. The script reads the three byte counts and the KV configuration as constants and prints the two tables above; anyone can reproduce them by hand from the numbers quoted in this section.

## Path A: Ollama (the 24GB floor)

Ollama is the shortest path and the only one that needs no build step. The explicit Q4_K_M tag matters: the `latest` tag currently resolves to the same manifest digest (24277f07f62d), and that manifest carries the same 15,177,370,240-byte weights layer (c580819bed79), but pinning the tag protects you from a future default change.

```bash
ollama pull devstral-small-2:24b-instruct-2512-q4_K_M
ollama run devstral-small-2:24b-instruct-2512-q4_K_M
```

That is a 15GB download, 14.14 GiB once it is on disk. Once the model is resident, Ollama exposes an OpenAI-compatible endpoint on `localhost:11434`, so any client that speaks that API can use it. Keep the context setting deliberate: a custom Modelfile with `PARAMETER num_ctx 32768` costs 5 GiB of KV cache on top of the weights, while the default short context costs almost nothing. On a 24GB card, 32K is roughly the practical ceiling before you start evicting.

```dockerfile
FROM devstral-small-2:24b-instruct-2512-q4_K_M
PARAMETER num_ctx 32768
```

Build it with `ollama create devstral-32k -f Modelfile` and run `devstral-32k`. If you have 32GB of VRAM, raise `num_ctx`; the table above tells you how far.

## Path B: vLLM, when you have the card for it

vLLM is the right tool for a shared server, and the wrong tool for a single 24GB card. The published checkpoint ([mistralai/Devstral-Small-2-24B-Instruct-2512](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512)) ships FP8 weights with a `quantization_config` that excludes the vision tower, the multimodal projector and `lm_head` from quantisation. FP8 weights for a 24B model are on the order of 24GB before any KV cache, so a 24GB card cannot hold this checkpoint and a usable context at the same time - that is arithmetic from the config, not a benchmark.

Where vLLM earns its keep is tensor parallelism across two or more cards, or a 48GB-plus card where the FP8 checkpoint plus your context fits. Use `--max-model-len` to state your context budget explicitly rather than letting the default claim the full position limit.

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Devstral-Small-2-24B-Instruct-2512 \
  --served-model-name devstral-small-2 \
  --max-model-len 16384 \
  --port 8000
```

This guide quotes no vLLM throughput figure. The old version's "60-80 tokens per second on an A100" and "25-35 on a 4090" numbers had no primary source behind them and were not measured on hardware this author has access to, so they are removed rather than relabelled.

## Path C: llama.cpp and the 16GB partial-offload reality

llama.cpp is the path people reach for when the card is small, and it is worth being precise about what partial offload buys you. With `--n-gpu-layers`, some transformer layers run on the GPU and the rest on CPU. On a 16GB card the Q4_K_M weights are 14.14 GiB, which leaves under 2 GiB of VRAM for cache and compute buffers, so the offloadable share is small - a handful of the 40 layers, not the majority. Every token then crosses the PCIe boundary for the CPU-resident layers, and the result is a working model, not a fast one. This guide does not give a tokens-per-second number for that arrangement because it was not measured here.

```bash
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j"$(nproc)"

./build/bin/llama-server \
  --model /path/to/devstral-small-2-q4_K_M.gguf \
  --n-gpu-layers 20 \
  --ctx-size 16384 \
  --port 8080
```

The GGUF file is the same Q4_K_M blob Ollama serves, 15,177,370,240 bytes. If you already pulled it through Ollama, the weights file sits in Ollama's blob store under the layer digest `sha256:c580819bed79...` (the `24277f07f62d` that the tag page shows is the manifest digest, not the weights file) and can be pointed at directly instead of being downloaded twice. If you are building your own quant, start from the FP8 checkpoint and expect 44.7 GiB of FP16 weights in memory during conversion.

`--n-gpu-layers` is the dial, and there is no formula for the right value: raise it until the model stops fitting, back off one layer, and check that context allocation still succeeds. That is a memory exercise, not a speed guarantee.

## What the CPU Path Actually Costs

The original article's hardware table claimed 1-3 tokens per second for a 64GB-RAM CPU-only machine, and the FAQ claimed 0.5-2 tokens per second at 4096 context for a 16GB-RAM laptop. Neither number had a measurement behind it, and they cannot both describe the same 24B model at the same time.

So that this guide contains at least one real measurement instead of two invented ones, a probe was run on the host used for this refresh: 2 vCPU, 11 GiB of RAM, no GPU, Ollama 0.20.3, generating with `qwen2.5:0.5b` in Q4. The recorded result was 7.95 tokens per second generation over 118 tokens and 6.96 tokens per second prompt processing over 43 tokens, with a 7.1-second load. Those figures are a private local author verification of the tooling path, logged with the exact command output for the review run; they are not published as a downloadable dataset.

Read that number for what it is: a 0.5B model on a two-core VM, which proves the CPU toolchain works and says nothing about a 24B model. Scaling 7.95 tokens per second by the parameter ratio would produce a number that no one measured, so it is not produced here. The 24B model cannot be loaded on 11 GiB of RAM at all; the 14.14 GiB Q4_K_M weight file exceeds it before any cache is allocated. The correct conclusion for the 64GB CPU configuration is that it is the one configuration in the old table that could plausibly host the model - 318,900 tokens of computed context headroom at Q4_K_M - and its throughput remains unmeasured.

## Connecting an agent to the local server

Both paths expose an OpenAI-compatible endpoint, so the client configuration is the same shape: point the tool at `http://localhost:11434/v1` for Ollama or `http://localhost:8000/v1` for vLLM, set the model name to `devstral-small-2`, and use any placeholder API key. Mistral's own terminal agent, Vibe CLI, is documented alongside the launch post ([mistral.ai/news/devstral-2-vibe-cli](https://mistral.ai/news/devstral-2-vibe-cli)); check its current documentation for install steps rather than assuming a package name, since the tooling around it has moved faster than the model.

For OpenHands, the container needs the host endpoint explicitly, because `localhost` inside a container is the container:

```bash
docker run -it \
  -e LLM_API_KEY=ollama \
  -e LLM_BASE_URL=http://host.docker.internal:11434/v1 \
  -e LLM_MODEL=devstral-small-2 \
  -v /your/workspace:/workspace \
  -p 3000:3000 \
  ghcr.io/all-hands-ai/openhands:latest
```

On Linux, `host.docker.internal` needs `--add-host=host.docker.internal:host-gateway`. Use the image tag your installed OpenHands documentation specifies; `latest` moves.

What the harness buys you is the thing the model was tuned for: multi-file reads, patch output, shell execution and iteration on failing tests. Without a tool harness, Devstral Small 2 is a chat model that you paste files into, and most of its coding advantage disappears.

## Troubleshooting

**"CUDA out of memory" at load.** The Q4_K_M weights are 14.14 GiB, so a 16GB card has under 2 GiB left after the weights and cannot hold a runtime context on top. Reduce `--ctx-size`/`--max-model-len` first; if that does not help, move to a smaller quant or a larger card. Do not expect a context reduction to rescue a 16GB card - at 4,096 tokens the total is 15.96 GiB, which leaves 40 MiB and no headroom for the driver.

**Ollama reports no GPU on Linux.** Run `nvidia-smi` to confirm the driver is visible, then check `ollama run <model> --verbose` output for the backend it selected. A missing GPU backend usually means the driver or CUDA runtime changed after Ollama was installed; reinstalling from the official script re-detects it.

**Context errors during inference.** Your prompt exceeded `num_ctx` (Ollama) or `--max-model-len` (vLLM). Raise the setting only if the memory table says you have room; otherwise trim the prompt. A 32K context on Q4_K_M costs 5 GiB of cache, which is the usual reason a 24GB card starts swapping.

**Slow generation on a Mac.** Confirm Metal is in use via verbose output. If the model is spilling out of unified memory, raising context makes it worse, not better: drop `num_ctx` before adding tokens.

**vLLM will not load the checkpoint.** The repository ships FP8 weights with a vision tower; if you are short on memory, that is a capacity problem rather than a tokenizer problem, and no flag fixes it.

## FAQ

**Can it run on a 16GB laptop with no GPU?** Not usefully. The Q4_K_M weights are 14.14 GiB, the KV cache at 4096 context adds 0.62 GiB, and the 1.2 GiB overhead allowance takes the total to 15.96 GiB - technically inside 16 GiB, but with 40 MiB spare and before the operating system's own residency. In practice that is about 4,300 tokens of context at the very most, and an mmap-based llama.cpp run may start and thrash well below that. No throughput figure is quoted here because none was measured. The previous version's "0.5-2 tokens per second" answer was unsupported and is withdrawn.

**Is Apache 2.0 really free for commercial use?** Yes. Apache 2.0 permits commercial use, modification and redistribution, with the licence and notice requirements it specifies. The API deprecation does not change this, because it applies to Mistral's hosted endpoint rather than to the weights.

**Which quant should I pick?** Q4_K_M on 24GB, Q8_0 if you have 32GB or more, FP16 only at 64GB and above if you want a context you can actually work in. A 48GB card does fit FP16 at 4,096 tokens - 46.56 GiB total - but the ceiling there is about 13,500 tokens. The fit table is the decision; anything below 24GB is not a Devstral Small 2 machine for this model.

**What context length is realistic?** 32K on a 24GB card, and much more if you have the memory for it. The vendor card says 256K, the registry says 384K and the config says 393,216 positions - but nobody has published a measured 393,216-token run on consumer hardware, and this guide does not claim one.

**Can I fine-tune it?** Apache 2.0 gives you the right to. QLoRA on a single large GPU is the usual route, and the tooling question is better answered by the fine-tuning framework's own documentation than by this page; no fine-tuning run was performed for this refresh.

**Why does the page no longer quote tokens per second for GPUs?** Because those numbers were estimates presented as measurements. The only throughput figure in this version comes from a 0.5B probe on a two-core VM, and it is labelled as such.
