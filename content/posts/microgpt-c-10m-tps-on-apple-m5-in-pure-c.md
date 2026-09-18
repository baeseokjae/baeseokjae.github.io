---
title: "MicroGPT-C Pure C Inference Hits 10M TPS on Apple M5"
date: 2026-09-18T07:02:01+00:00
tags:
  - MicroGPT-C
  - pure C inference
  - Apple M5
  - NEON
  - AVX2
  - tiny language model
  - machine learning
description: "MicroGPT-C is a single-file, pure C char-level name generator that runs inference at 10.1M tokens/sec on Apple M5 Pro with NEON — what the benchmark really means."
draft: false
cover:
    image: "/images/microgpt-c-10m-tps-on-apple-m5-in-pure-c.png"
    alt: "MicroGPT-C Pure C Inference Hits 10M TPS on Apple M5"
    relative: false
schema: "schema-microgpt-c-10m-tps-on-apple-m5-in-pure-c"
---

MicroGPT-C is a dependency-free, single-file C implementation of a character-level transformer that runs inference at 10,168,430 tokens per second single-threaded on an Apple M5 Pro using NEON — a 4,192-parameter name generator, not a large language model. The headline number is real, but context matters: this measures raw matvec throughput on a tiny model, not general AI performance. Here is what the benchmark means, how the optimizations work, and why the Apple comparison is fair.

## What is MicroGPT-C (and what the 10M TPS claim actually is)

MicroGPT-C is a from-scratch GPT-style transformer written in a single C source file with no dependencies beyond the C standard library. It implements forward pass, backpropagation, Adam optimization, and sampling, and it is small enough to compile and run almost anywhere — macOS, Linux, and Windows (via MSYS2) all build it without extra tooling.

The model is small by design: just 4,192 parameters. It is trained on roughly 32,000 names and learns to generate plausible new names character by character. On the default split, it trains on 20,000 of those 32,033 names in a couple of seconds — not minutes, not hours.

So the "10M TPS" headline describes a character-level name generator, not a transformer with billions of parameters. That distinction drives most of the honest criticism the project has received on Hacker News, where commenters were quick to point out that "this is not an LLM." The number is real and the engineering is impressive, but the claim should never be read as "10 million tokens per second from a general-purpose language model." It is an inference benchmark of a deliberately minuscule model.

## The 10,168,430 tok/sec benchmark — hardware, backends, methodology

The flagship number comes from a single-threaded inference benchmark on an Apple M5 Pro using the ARM64 NEON SIMD kernels:

| Hardware | Backend | Tokens/sec | Median of runs |
|---|---|---|---|
| Apple M5 Pro | NEON (ARM64) | 10,168,430 | 15 |
| AMD Ryzen 5 5600H | AVX2 (x86-64) | 6,927,775 | 5 |
| Apple M5 Pro | Rosetta 2 (emulated) | 2,225,024 | — |
| AMD Ryzen 9 9800x3d | AVX2 (independent HN test) | 7,647,173 | — |

The 10.1M figure is the median of 15 runs, which reduces the chance the headline is a lucky outlier. The same code compiled for x86-64 with AVX2 on a Ryzen 5 5600H reaches 6.9M tokens/sec, and an independent tester on a Ryzen 9 9800x3d recorded 7,647,173 tokens/sec.

The project also documents that running the exact same binary under Rosetta 2 on Apple Silicon drops throughput to about 2,225,024 tokens/sec — roughly a third of native speed. That number is not a valid benchmark of the machine; it is a warning about what emulation does to tight SIMD loops.

## Apple M5 vs Ryzen 5 5600H: is the comparison fair?

Yes, and the reason it is fair is that the algorithm is identical on both platforms — only the SIMD kernels differ (NEON on ARM64, AVX2 on x86-64). There is no hidden hand-tuning that gives Apple an advantage; both backends run the same forward-pass logic.

| Factor | Apple M5 Pro (NEON) | Ryzen 5 5600H (AVX2) |
|---|---|---|
| SIMD width per core | 128-bit NEON | 128-bit (2×64-bit AVX) |
| Token throughput | 10,168,430 /s | 6,927,775 /s |
| Ratio vs Rosetta 2 | ~4.6× | — |

The M5 Pro's lead comes largely from its wide core and high issue rate: it can keep more in-flight work per cycle, which matters when the workload is issue-width-limited (more on that below). The Ryzen 5 5600H is a mid-range laptop chip, not the fastest x86 option, and the independent 9800x3d result confirms x86 can push higher — but the fundamental point stands: on identical logic, Apple's NEON path wins, and the margin is not an artificial artifact.

## The engineering behind the speed: inference-path optimizations

The performance isn't accidental. The project's `docs/PERFORMANCE.md` documents a set of concrete inference-path optimizations that push a tiny model through the CPU as fast as the hardware allows:

- **Column-major weight layout.** Storing weights column-major lets the matvec read contiguously into the SIMD accumulator, avoiding scattered loads.
- **Split accumulators.** The dot-product kernels split the accumulation across multiple registers to break the dependency chain that would otherwise stall the FMA pipeline.
- **Hoisted (token, position) prefix table.** Position-dependent values that change rarely are computed once and reused rather than recomputed per token.
- **Deferred RMS scale.** The RMSNorm scale is factored out and applied at the end instead of inside the inner loop.
- **Fused sampling.** Sampling is woven into the final output stage rather than a separate pass.
- **Padded vocab.** The vocabulary is padded to a multiple of four so SIMD lanes stay aligned on the 128-bit path.

These are exactly the tricks you use when your model is too small to hide inefficiency behind compute: with 4,192 parameters, every wasted instruction shows up in the throughput number.

## Why it's issue-width-limited, not waiting on stalls

One of the most insightful findings in the project's documentation is that roughly half the per-token time — about 240 of ~500 cycles — goes to the MLP, and that the workload is **issue-width-limited**, not stall-limited.

This distinction matters for anyone trying to make it faster. An issue-width-limited loop means the CPU's execution units are busy; the bottleneck is how many instructions the core can dispatch, not how often it has to wait for data. If the machine were stall-limited, you could speed it up by improving cache locality, prefetching, or reducing memory latency. Because it is issue-width-limited, the only real lever is to execute fewer instructions — which points directly at batching.

The MLP dominating the cycle budget also tells you where optimization effort should go: that half of the work is the highest-leverage target.

## The honest limits: 4,192 params, a name generator, not an LLM

It is worth being blunt about what this project is and is not:

| Capacity | MicroGPT-C | A typical small LLM |
|---|---|---|
| Parameters | 4,192 | 1B–70B+ |
| Task | Character-level name generation | General language modeling |
| Training data | ~32,000 names | Multi-trillion-token corpora |

The model generalizes well for its size — it scores 2.2054 nats/char on the training names and 2.2039 on unseen names, edging out an interpolated trigram that has roughly five times the parameters. That is a genuinely good result for a 4K-parameter model.

But "generalizes" here means "invents plausible-sounding names," not "holds a conversation." Anyone quoting the 10M TPS figure should carry that qualification with it. The honest takeaway is not that we've cracked 10M-token LLM inference — it's that a tiny, carefully-simd-optimized C model can saturate a modern CPU core's issue width.

## Rosetta 2 vs native: a benchmark cautionary tale

The project's own documentation makes a point that anyone reading benchmarks should absorb: the same binary measuring 2,225,024 tokens/sec under Rosetta 2 is not a real M5 performance number. Rosetta 2 translates x86-64 instructions to ARM64 at runtime, and for a tight SIMD loop that constant translation overhead is brutal — roughly a third of native throughput.

The lesson is general: **before trusting any Apple Silicon benchmark, ask whether it ran native ARM64 or under Rosetta 2.** MicroGPT-C's honesty in publishing this number is a good model for the industry. The gap between 2.2M and 10.1M is not "Apple's silicon is slow"; it is what dynamic binary translation does to code that was compiled for a different instruction set.

## What would make it faster: batching and the roadmap

Because the workload is issue-width-limited, the single clearest path to higher throughput is **batching** — turning every per-token matrix-vector product (matvec) into a matrix-matrix product (matmul). A matvec on a 4K-parameter model leaves SIMD lanes underutilized on the dimension that varies between tokens; a matmul amortizes the per-row work across the whole batch and feeds the FMA pipeline far more efficiently.

The project itself flags batching as the stated ceiling-raiser. Other possible directions include:
- **Arm SME** (Scalable Matrix Extension), which a HN commenter noted could fit the network in the ZA tile register for even faster on-chip work.
- **CUDA kernels** for GPU offload, where one commenter's napkin math suggested ~2 billion tokens/sec on a 5090.
- **Reducing MLP cycles**, given that half the time is spent there.

Each of these attacks a different layer of the bottleneck, but batching is the one that follows most directly from the issue-width-limited diagnosis.

## Verdict and bottom line

| Claim | Verdict |
|---|---|
| "10M TPS on Apple M5 in pure C" | True, and reproducible — median of 15 runs, 10,168,430 tok/sec |
| "This is an LLM" | False — it's a 4,192-parameter char-level name generator |
| "The Apple vs AMD comparison is fair" | Yes — identical algorithm, only SIMD kernels differ |
| "A cautionary Rosetta 2 example" | Genuinely useful — emulation costs ~3× throughput |

MicroGPT-C is an excellent demonstration of what disciplined, dependency-free C plus targeted SIMD optimization can do on a modern chip. The 10M TPS number is real and worth understanding — but only as a tiny-model inference result, not as a general LLM breakthrough. If you dig into the performance documentation, you'll find a compact masterclass in how to saturate a CPU's issue width, and a clear, honest roadmap (batching) for going even faster. The engineering is the story.

## FAQ

**Is MicroGPT-C really 10 million tokens per second on Apple M5?**
Yes, for inference at 10,168,430 tokens/sec single-threaded using NEON on an Apple M5 Pro, as a median of 15 runs. The caveat is that it is a 4,192-parameter character-level name generator, not a large language model.

**Is the Apple M5 vs AMD comparison fair?**
Yes. Both run the identical algorithm; only the SIMD kernels differ (NEON on ARM64, AVX2 on x86-64), so the comparison isolates CPU throughput rather than differences in the model.

**Does MicroGPT-C require any dependencies?**
No. It is a single C file using only the C standard library, and builds on macOS, Linux, and Windows via MSYS2.

**Why is batching the next step to make it faster?**
The workload is issue-width-limited, meaning the CPU is busy and only executes fewer instructions per token will help. Turning per-token matvecs into batched matmuls is the direct way to do that.

**Should I quote the 10M TPS number as proof of fast LLM inference?**
No. Quote it as evidence of what a well-optimized tiny C model can do on a modern CPU core, and always add the qualifier that it is a 4K-parameter name generator rather than an LLM.
