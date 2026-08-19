---
title: "LLM Inference Engineering: From KV Cache to PagedAttention"
date: 2026-08-19T04:02:50+00:00
tags:
  - llm inference
  - kv cache
  - pagedattention
  - vllm
  - inference optimization
  - gpu
description: "LLM inference engineering optimizes prefill, decode, KV cache, and PagedAttention to cut memory waste and boost serving throughput by up to 24x."
draft: false
cover:
  image: "/images/llm-inference-engineering-guide.png"
  alt: "LLM Inference Engineering: From KV Cache to PagedAttention"
  relative: false
schema: "schema-llm-inference-engineering-guide"
---

LLM inference engineering is the discipline of making large language models run fast, cheap, and reliably in production. It centers on two phases — prefill and decode — and on the KV cache, the memory structure that stores attention keys and values. The single biggest win in the field is PagedAttention, which manages the KV cache like an operating system manages virtual memory, cutting memory waste from up to 60–80% down to near zero and boosting serving throughput by up to 24x over naive implementations.

## What Is LLM Inference Engineering (and Why It Matters)

LLM inference engineering is the practice of optimizing the serving stack that runs trained models — the batching, memory management, attention kernels, and hardware scheduling that turn a model checkpoint into a responsive API. It matters because inference cost and latency, not training, dominate the operating budget of deployed AI products. Every token a user sees must be generated, cached, and streamed back, and the difference between a well-engineered and a naive serving stack is often an order of magnitude in throughput.

The stakes are concrete. A model that serves 10x more requests on the same GPU hardware directly cuts cost per token and improves user experience. This is why companies like OpenAI, Anthropic, and Meta invest heavily in inference engineering teams, and why open-source projects like vLLM, TensorRT-LLM, and llama.cpp have become foundational infrastructure. Understanding inference engineering lets you choose the right serving framework, tune it correctly, and reason about GPU memory budgets instead of treating them as a black box.

## Inference Fundamentals — Prefill vs Decode Phases

Every LLM generation runs in two distinct phases with very different computational profiles. The **prefill phase** processes the entire input prompt in parallel, computing the key and value vectors for every input token at once. Because all tokens are processed simultaneously, prefill is highly parallelized and makes excellent use of GPU compute — it is compute-bound and fast relative to the number of tokens it handles.

The **decode phase** is where the model generates output tokens one at a time, autoregressively. Each new token depends on all previous tokens, so the GPU must process the full context sequentially. This phase is memory-bound and severely underutilizes GPU compute, as NVIDIA's inference optimization guide notes. The decode phase is typically the bottleneck in real serving workloads because it is serial and cannot be parallelized across tokens.

The practical consequence is that inference engineers must optimize the two phases differently. Prefill benefits from high-throughput matrix multiplication kernels and large batch sizes. Decode benefits from reducing memory traffic — which is exactly what the KV cache, attention optimizations, and quantization techniques in this guide address. Understanding which phase dominates your workload tells you which optimization to prioritize.

## The KV Cache — Why It's the Memory Bottleneck

During decode, the model needs the key and value vectors of every previous token to compute attention for the current token. Rather than recomputing these vectors on every step — which would be enormously wasteful — the inference engine stores them in a structure called the **KV cache**. This cache grows with every generated token and is the single largest memory consumer in LLM serving.

The problem is how traditional serving frameworks allocate this memory. Most reserve space for the **maximum** context length (for example, 2048 or 4096 tokens) for every request, regardless of how many tokens the request actually uses. Because real requests vary wildly in length, this reservation wastes up to 60–80% of KV-cache memory, as detailed in analyses of vLLM's design. The wasted memory is fragmented and cannot be reused by other requests, so the GPU fills up with idle reserved space while new requests are rejected.

The KV cache also grows and shrinks dynamically as requests generate tokens, which causes fragmentation and redundant duplication across requests that share prefixes. This is the core memory-management problem that PagedAttention was designed to solve. Before PagedAttention, engineers had to over-provision memory, accept low batch sizes, or implement complex custom allocators — all of which left significant performance on the table.

## PagedAttention — OS-Style Paging for the KV Cache

PagedAttention, introduced by the vLLM team at UC Berkeley, applies a classic operating-systems idea to the KV cache: **virtual memory paging**. Just as an OS stores process memory in fixed-size pages that can be scattered across physical RAM and tracked by a page table, PagedAttention stores the KV cache in fixed-size blocks that can be scattered across GPU memory and tracked by a block table.

This design eliminates the two biggest sources of waste. First, because blocks are allocated on demand as tokens are generated, the engine no longer reserves memory for the maximum context length — it only uses what each request actually needs. Second, because blocks are non-contiguous and tracked by a table, memory fragmentation disappears; freed blocks can be reused by any other request. The result is near-zero waste in KV-cache memory, as the PagedAttention paper reports.

The throughput gains are dramatic. vLLM with PagedAttention delivers up to 24x higher throughput than HuggingFace Transformers and up to 3.5x higher than Text Generation Inference (TGI) without any model architecture changes, according to the vLLM blog. The academic paper reports 2–4x higher throughput at the same latency compared to FasterTransformer and Orca, with the improvement growing for longer sequences, larger models, and complex decoding algorithms. PagedAttention also enables flexible sharing of KV cache within and across requests, which is valuable for parallel sampling and beam search.

## Attention Optimizations — GQA, MQA, and FlashAttention

Beyond memory allocation, inference engineers optimize the attention computation itself. Two families of techniques matter most: reducing the KV cache footprint through shared attention heads, and reducing memory movement through fused kernels.

**Multi-query attention (MQA)** and **grouped-query attention (GQA)** reduce the KV cache by sharing key and value heads across multiple query heads. In standard multi-head attention, every query head has its own key and value heads, which multiplies the cache size. MQA uses a single key/value head shared by all query heads, while GQA uses a small group of key/value heads shared by several query heads each. Both dramatically shrink the KV cache with minimal accuracy loss, and GQA in particular has become the default in modern models like Llama 2 and Llama 3.

**FlashAttention** takes a different approach: it fuses the attention computation into a single kernel that never materializes the full attention matrix in memory. Because attention is IO-bound — the bottleneck is moving data between GPU memory and compute units, not the arithmetic itself — FlashAttention minimizes memory movement and delivers large speedups. It is now a standard building block in nearly every modern inference stack.

These techniques are complementary. GQA and MQA reduce how much KV cache you need to store, while FlashAttention reduces how much memory traffic the attention computation generates. Together with PagedAttention, they form the core of a modern, memory-efficient inference engine.

## Speculative Decoding — Draft-and-Verify for Faster Generation

The decode phase is serial and memory-bound, which makes it hard to speed up directly. **Speculative decoding** attacks this problem by having a small, fast **draft model** propose a sequence of tokens, which a large **target model** then verifies in parallel. Because the target model can check multiple proposed tokens at once, the GPU's parallelism is finally put to use during decode.

The key insight is that verifying tokens in parallel is much cheaper than generating them one at a time. When the draft model is accurate, the target model accepts several tokens per step, effectively generating multiple tokens per forward pass. Google's research on speculative decoding reports meaningful speedups, and the technique is now widely deployed in production serving systems, including Cloudflare's Workers AI, which combines speculative decoding with KV cache compression.

Speculative decoding is complementary to the memory optimizations above. It does not reduce the KV cache size, but it reduces the number of serial decode steps, which lowers latency and improves throughput. In practice, the best inference stacks combine PagedAttention for memory efficiency, GQA/FlashAttention for attention efficiency, and speculative decoding for decode-phase speed.

## KV Cache Quantization — Squeezing More Into Less VRAM

Quantization reduces the memory footprint of the KV cache by storing keys and values at lower precision. Instead of storing every value as a 16-bit or 32-bit float, the engine stores them as INT8, INT4, or even 3.5-bit values, dramatically shrinking the cache and allowing larger batch sizes or longer contexts on the same GPU.

The tradeoff is accuracy. Aggressive quantization can degrade output quality, but modern techniques achieve near-zero accuracy loss at INT8 and INT4, and even 3.5-bit quantization is viable for many workloads. Projects like Huawei's KVarN provide native vLLM backends for KV-cache quantization, making it practical to deploy in production. The choice of precision is a classic latency-versus-quality tradeoff that inference engineers tune per workload.

KV cache quantization is especially valuable for long-context applications, where the cache can grow to dominate memory. By shrinking the cache, quantization enables longer sequences, larger batches, and lower cost per token — all without changing the model architecture. It is one of the most impactful levers available to a production inference engineer.

## Hands-On: Running vLLM and Measuring Throughput

The best way to understand these concepts is to measure them. vLLM is the reference implementation of PagedAttention and is straightforward to run locally. Install it with `pip install vllm`, then start a server with a model such as Llama-3-8B:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192
```

To measure the throughput gain, run the same generation workload through both vLLM and HuggingFace Transformers and compare tokens-per-second and requests-per-second. The vLLM team's benchmarks show up to 24x higher throughput than HuggingFace Transformers on the same hardware, so the difference should be dramatic. You can also experiment with the `--block-size` parameter to see how block size affects memory granularity and throughput.

A useful experiment is to monitor GPU memory utilization while serving concurrent requests. With a naive implementation, you will see memory reserved for maximum context length and requests rejected as the cache fills. With vLLM's PagedAttention, memory is allocated on demand and utilization stays high, allowing a much larger batch of concurrent requests. This hands-on comparison makes the theory concrete and is the fastest way to internalize why PagedAttention matters.

## Production Serving Best Practices and Tuning

In production, inference engineering is about balancing throughput, latency, and cost under real traffic. Several practices consistently matter. First, use **continuous batching**, which adds and removes requests from the batch as they finish, rather than waiting for a full batch to complete. This keeps the GPU busy and is a major throughput lever. Second, tune **GPU memory utilization** — vLLM's `--gpu-memory-utilization` flag controls how much VRAM is reserved for the KV cache versus model weights and activations.

Third, choose the right **block size** for your workload. Smaller blocks reduce memory waste for short requests but add overhead; larger blocks are more efficient for long contexts. Fourth, enable **speculative decoding** and **KV cache quantization** where accuracy allows, as both reduce the dominant costs of the decode phase. Fifth, monitor the right metrics: tokens per second, time to first token (prefill latency), inter-token latency, and GPU memory utilization.

Finally, match the serving framework to your needs. vLLM is excellent for high-throughput serving with PagedAttention. TensorRT-LLM offers deep NVIDIA kernel optimization. llama.cpp is ideal for CPU and edge deployment. The best engineers benchmark their specific workload across frameworks rather than assuming one is universally best, because the optimal choice depends on your model, hardware, and traffic pattern.

## The Learning Path — From KV Cache to Production Inference Engineer

Becoming an inference engineer is a progression from fundamentals to production systems. Start by understanding the prefill and decode phases and why decode is memory-bound. Then study the KV cache and its fragmentation problem, which motivates everything that follows. Next, learn PagedAttention and how OS-style paging solves the memory waste problem — this is the conceptual core of modern serving.

From there, layer on the attention optimizations: GQA and MQA to shrink the cache, and FlashAttention to reduce memory movement. Add speculative decoding to speed up the serial decode phase, and KV cache quantization to squeeze more into limited VRAM. Finally, get hands-on: run vLLM, benchmark it against naive serving, and tune block size, memory utilization, and batching for your workload.

The field rewards hands-on experimentation. Every optimization in this guide is measurable, and the fastest way to learn is to run the benchmarks yourself. By the end of this path, you will be able to reason about GPU memory budgets, choose the right serving stack, and tune it for real production traffic — the core skills of an LLM inference engineer.

## FAQ

**What is LLM inference engineering?**
LLM inference engineering is the practice of optimizing how trained language models are served in production — covering batching, memory management, attention kernels, and hardware scheduling — to maximize throughput and minimize latency and cost per token.

**What is the KV cache in LLM inference?**
The KV cache stores the key and value vectors of all previous tokens during generation, so the model does not recompute them at every decode step. It is the largest memory consumer in LLM serving and grows with every generated token.

**How does PagedAttention improve LLM inference?**
PagedAttention manages the KV cache in fixed-size, non-contiguous blocks tracked by a block table, like OS virtual memory paging. This eliminates the 60–80% memory waste from reserving maximum context length and removes fragmentation, enabling up to 24x higher throughput.

**What is the difference between prefill and decode in LLM inference?**
Prefill processes the entire input prompt in parallel and is compute-bound, while decode generates output tokens one at a time and is memory-bound. Decode is typically the bottleneck because it is serial and underutilizes GPU compute.

**What are the best LLM inference optimization techniques?**
The most impactful techniques are PagedAttention for memory efficiency, grouped-query attention (GQA) and multi-query attention (MQA) to shrink the KV cache, FlashAttention to reduce memory movement, speculative decoding to speed up decode, and KV cache quantization to reduce VRAM usage.
