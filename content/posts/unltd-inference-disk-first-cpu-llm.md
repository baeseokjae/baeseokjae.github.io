---
title: "UNLTD Inference Review: Disk-First CPU-First LLM Inference in Rust"
date: 2026-10-01T01:34:55+00:00
tags:
  - unltd inference Rust
  - disk-first LLM inference
  - CPU-first LLM inference Rust
  - memory budget LLM inference
  - mmap GGUF inference
  - unltd-inference review
  - unltd-inference vs llama.cpp
description: "UNLTD Inference is a disk-first Rust runtime that runs GGUF models larger than its memory budget via mmap. An honest review of v1.0.0's real numbers."
draft: false
cover:
  image: "/images/unltd-inference-disk-first-cpu-llm.png"
  alt: "UNLTD Inference Review: Disk-First CPU-First LLM Inference in Rust"
  relative: false
schema: "schema-unltd-inference-disk-first-cpu-llm"
---

UNLTD Inference is a disk-first, CPU-first LLM runtime in Rust that runs GGUF models larger than its configured memory budget by memory-mapping weights instead of copying them to the heap. Version 1.0.0 validates one model, Ornith 1.0 9B Q4_K_M (5.63 GB), on Windows x86-64 with scalar kernels, and publishes ~73 s prefill and ~14.3 s per token.

That is the entire honest summary, and everything interesting about the project lives in the gap between the headline claim and the fine print. The headline is "a 5.63 GB model on a 3 GB budget." The fine print is that the budget governs about 113 MB of runtime-controlled memory while peak working set still reaches ~5.24 GB, and that "disk-first" here means memory-mapped files plus OS demand paging, the same mechanism llama.cpp has shipped by default for years.

This review covers what `unltdev/unltd-inference` actually implements, what its published numbers mean, where it sits against llama.cpp and the rest of the disk-backed inference field, and whether anyone should run it today. All performance and memory figures below come from the project's own README and checkpoint documents, and I label them as self-reported because nothing in this niche has been independently reproduced yet.

## What Is UNLTD Inference and Who Actually Built It?

UNLTD Inference is an Apache-2.0 Rust workspace for CPU-only GGUF inference whose central design claim is that a model can be larger than the configured runtime memory budget and still run correctly. The public repository is [unltdev/unltd-inference](https://github.com/unltdev/unltd-inference), version 1.0.0 was released on 2026-08-18, and the repository itself was created on 2026-08-19 - a single-author research release, not a project with a community behind it.

The provenance numbers matter more than any benchmark here, because they set the confidence level for everything else. Checked directly against the GitHub REST API on 1 October 2026: 21 commits, one release, **1 star, 0 forks, 0 open issues**, no merged feature pull requests, and no third-party reproduction of any kind. The "disk-first LLM inference" phrase returns exactly one repository on GitHub search, and even the broader "out-of-core LLM inference" query returns six. This is a category with roughly one occupant.

The architecture is a deliberately one-directional eight-crate workspace: `unltd-tensor` at the bottom, then `unltd-core`, then `model-loader`, `architectures`, `memory` and `tokenizer` in parallel, topped by `unltd-generation` and `unltd-cli`. Dependencies are few and deliberately unglamorous - `memmap2`, `half`, `bytemuck`, `serde`, `clap`, `rayon`, `regex` - with MSRV Rust 1.80, edition 2021, thin LTO and `codegen-units=1` in release. There is no Candle, no BLAS, no framework, no GPU path and no Python binding.

The one model validated end to end in v1.0.0 is Ornith 1.0 9B Q4_K_M at 5,629,108,704 bytes. The forward path is a Qwen3.5-compatible hybrid: 32 layers made of 24 recurrent GatedDeltaNet layers plus 8 full-attention layers, M-RoPE positional encoding, and a GPT-2 byte-level BPE tokenizer rebuilt from GGUF metadata. That choice of validation artifact is credible rather than convenient - the Ornith 1.0 9B GGUF has roughly 2.6 million downloads on Hugging Face - though the family has already moved on to Ornith 1.5, whose 9B GGUF shows about 5.05 million downloads, so the validated model is a generation behind the current default.

## How Does a Model Larger Than the Memory Budget Still Run?

The mechanism is memory mapping, not streaming. Weights are exposed as whole-file `memmap2` views; the runtime never copies them into the heap, never dequantizes them into a cache, and never holds a second representation. When a tensor is needed, the kernel faults the relevant pages in from disk; when memory pressure rises, the kernel evicts them and they are read again later.

This is worth stating plainly because "disk-first" sounds like a scheduling policy and is not one. Version 1.0.0 explicitly does **not** implement layer streaming, prefetching, double buffering, expert streaming or MoE execution. The README lists all five as unimplemented. Disk-first in this release means what llama.cpp has done by default for years: `mmap` the container, let demand paging do the work.

What the runtime does add is accounting. Before allocating anything, it computes the memory it intends to control - KV cache, attention and compute scratch, runtime state - and compares that total against the budget you passed. If the configuration cannot fit, it refuses. Running the CLI with `--memory-budget 32M` against the validated model, where the minimum viable controlled budget is 113.06 MB, prints `REFUSING TO RUN` with the full number breakdown and exits with code 2. The CLI contract is explicit: exit 1 for load or usage errors, exit 2 for budget refusal, exit 3 for `RUN INVALID`.

That refusal path is the actual product idea, and it is rarer than it sounds. Most runtimes discover their memory limits by being killed by the OOM killer mid-generation. This one tells you before it allocates a byte. For a full walkthrough of how runtimes typically manage this, see our [LLM inference engineering guide](/posts/llm-inference-engineering-guide/).

## What Does the --memory-budget Actually Control?

This is the section that decides whether you find the project impressive or misleading, so it deserves precision. The budget governs **runtime-controlled memory only**: KV cache, scratch buffers, runtime state and controlled caches. It does not govern process RSS, it does not govern mapped virtual bytes, and it does not govern the OS page cache.

| Quantity | Value in the validated run | Governed by --memory-budget? |
|---|---|---|
| Model file on disk | 5.63 GB | No (read-only mmap) |
| Controlled runtime memory | ~113.19 MB | Yes |
| KV cache at tested context | ~524 KB | Yes |
| Minimum viable controlled budget | 113.06 MB | Yes (floor) |
| Peak working set (RSS) | ~5.24 GB | No |
| Mapped virtual address space | whole model file | No |
| OS page cache | unbounded, kernel-managed | No |

Read the third and fifth rows together and the headline claim becomes legible. "A 5.63 GB model runs on a 4 GB budget" is true, and it is also true that the working set peaked at about 5.24 GB during that same run. The weights contribute zero bytes to the controlled budget because they are mapped views, so what you are really buying is not memory savings - it is memory *enumeration*. The project says so itself, repeatedly, in its own documentation.

That distinction is the difference between a real engineering contribution and marketing. Explicit memory accounting is genuinely useful when you are deploying onto a device whose RAM ceiling you cannot violate, because you now have a number you can validate up front instead of a crash you discover at runtime. It is not useful if you interpreted "disk-first" as "uses less memory than llama.cpp," because on RSS the two are indistinguishable by construction. Readers planning hardware around this should also read the cost model in our [local LLM rig cost payback analysis](/posts/local-llm-rig-cost-payback-2026/), which is the honest constraint most "run a big model on a small machine" claims omit.

## How Fast Is UNLTD Inference, Really?

Slow, and honestly documented as slow. On the validated setup - Ornith 1.0 9B Q4_K_M, Windows x86-64, scalar kernels, single-threaded - the published numbers are roughly **73 seconds of prefill** and **~14.3 seconds per decoded token**. That is about 0.07 tokens per second.

| Runtime | Model | Hardware / budget | Decode throughput |
|---|---|---|---|
| UNLTD Inference v1.0.0 | Ornith 1.0 9B Q4_K_M (5.63 GB) | Windows x86-64, 3-4 GB budget, scalar | ~14.3 s/token (~0.07 tok/s) |
| llama.cpp | same class, resident in RAM | same class CPU | tens of tok/s (typical) |
| kimi-k3-in-c | Kimi K3 2.78T MoE (1.56 TB) | 8.24 GB peak RSS | ~32.69 s/token |
| kimi-k3-in-c | Kimi K3 2.78T MoE | 127.92 GB peak RSS | ~10.69 s/token |
| WARP | Kimi K3 2.78T MoE | 64 GB MacBook Pro, 17.56 GB expert cache | ~0.60 tok/s |
| ramvamp | Qwen3-30B-A3B Q4_K_M (17.35 GiB) | Linux x86_64, NVMe, 3 GB cgroup | ~2 tok/s (1.43-2.19 by context) |

Three causes explain the gap, and all three are stated in the README rather than excavated: no SIMD (the Q4_K/Q6_K/Q8_0 kernels are scalar reference implementations), no multithreading, and every token touching a weight file that does not fit in RAM. Compare it to a resident 9B on the same class of CPU and the deficit is two orders of magnitude. Compare it to another engine that is genuinely reading weights off disk at a hard memory ceiling and it lands in the same order of magnitude - which is the fairer comparison and the one that makes the number look like physics rather than a defect.

The performance discipline around the claim is more interesting than the number. The project inherits its measurement protocol from `kimi-k3-in-c`, which recorded a **33% noise floor** on identical runs - 14.78, 14.67 and 20.14 seconds per token, with nothing changed between them. That is why unltd-inference mandates a machine manifest per run (exact CPU, RAM, SSD model and firmware, kernel, commit), at minimum three repetitions reported as median with range, budgets enforced by cgroup `MemoryMax` plus `MemorySwapMax=0` rather than by the program, and peak RSS taken from `getrusage` instead of from the plan. Any single-run streaming benchmark without that protocol is anecdote, including any number in this article that you cannot trace to a manifest.

## How Does It Validate Correctness Against llama.cpp?

With an oracle comparison that publishes its own failure point, which is unusual and worth crediting. The tokenizer is bit-exact against llama.cpp for the validated prompt. The first eleven greedy decoding steps match the llama.cpp oracle exactly. After that, output diverges, and the project says so in the README, attributing it to scalar reference kernels versus AVX2/repacked kernels producing argmax flips on near-ties.

The test suite is 107 passing tests with zero failures, distributed as tensor 35, tokenizer 27, model-loader 17, memory 13, generation 11 and architectures 4. That is a real suite, not a smoke test, and it is concentrated in the parts most likely to be silently wrong in a from-scratch numeric implementation.

The candour extends to scope. Exactly one model is validated, on exactly one platform - Windows x86-64 - and the README states that Linux is not validated end to end in v1.0.0 (the CLI examples are PowerShell). There is no sampling at all: greedy only, temperature fixed at zero. There is no MoE execution, no GPU, no SIMD and no multithreading. Publishing a limitations list that would make most launch posts unpublishable is the strongest trust signal in the repository, and it is the reason the numbers above are worth reading at all.

## How Does UNLTD Inference Compare to llama.cpp?

llama.cpp is the baseline every disk-first runtime is measured against, and it is a brutal one: roughly 130,000 stars, 23,900 forks, 146 registered GGUF architectures and more than 28,500 published GGUFs, with memory mapping on by default. A model larger than your RAM already "just works" there with zero configuration, because the OS page cache is the policy.

| Dimension | UNLTD Inference v1.0.0 | llama.cpp |
|---|---|---|
| Over-RAM execution | Yes, via mmap + demand paging | Yes, via mmap + demand paging |
| Explicit memory budget | Yes - validated, refuses impossible configs | No (RSS/page cache are implicit) |
| Layer / expert streaming | Not implemented | Not implemented (PR #26003 closed, unmerged) |
| SIMD kernels | No (scalar reference) | Yes (AVX2 and friends) |
| Multithreading | No | Yes |
| Sampling | No (greedy only) | Full sampler stack |
| Architecture coverage | 1 validated | 146 registered |
| Server / API surface | None | Built-in server |
| Maturity | 1 star, single author | 130k stars, large community |

The skeptic's argument, made in the [Hacker News thread on running Kimi K3 at 0.50 tok/s](https://news.ycombinator.com/item?id=49130892), is that a custom engine adds nothing here because stock llama.cpp can already map an oversized GGUF. The strongest counter-argument in that thread is that engines which manage their own backing cache - the way database engines do - gain roughly 10x, because the runtime knows the token's access pattern while the kernel pages in only on demand. Both positions are correct about different things, and unltd-inference v1.0.0 has not yet earned the second one.

Where llama.cpp's own behaviour is documented and checkable: for MoE models at 100-150% of RAM, [community measurements in llama.cpp discussion #18758](https://github.com/ggml-org/llama.cpp/discussions/18758) found mmap beating direct I/O, because prefetch attempts to read the whole model into RAM and thrashes while `O_DIRECT` bypasses caching and makes repeat loads at least ten times slower. The incumbent's only runtime-level over-RAM streaming attempt, [PR #26003 "lazy-experts"](https://github.com/ggml-org/llama.cpp/pull/26003), was opened on 2026-07-22 with 160 additions across 9 files and remains **closed and unmerged**. That gap - not throughput, not language, not coverage - is the honest reason a new runtime is worth writing in 2026.

## How Does It Compare to ramvamp, ALLM, WARP and kimi-k3-in-c?

This is the comparison that actually decides the review, because these projects implement the thesis unltd-inference has on its roadmap.

| Project | Language | What it really does | Strongest published result |
|---|---|---|---|
| [ramvamp](https://github.com/y0sif/ramvamp) | Rust | Streams routed MoE experts from NVMe with io_uring + O_DIRECT under a hard cgroup ceiling | Qwen3-30B-A3B Q4_K_M (17.35 GiB) in a 3 GB cgroup at ~2 tok/s, KL 1.04e-2 vs llama.cpp, 8/8 top-1 agreement |
| [ALLM](https://github.com/mithun50/ALLM) | Rust | Layerwise streaming through a byte-budgeted LRU cache with a background prefetch thread | 0.5B model: 8.5 tok/s at 256 MiB cache, 2.2 tok/s at 64 MiB; llama.cpp at 32-36 tok/s on the same box |
| [WARP](https://github.com/sqliteai/waste) | C | Keeps the trunk resident, streams selected experts from a repacked container with a bounded expert LRU | Full 2.78T Kimi K3 at ~0.6 tok/s on 64 GB, 38% expert-cache hit ratio |
| [kimi-k3-in-c](https://github.com/FareedKhan-dev/kimi-k3-in-c) | C99 | Pinned trunk prefix, 2-slot ring with a reader thread, `O_DIRECT` pread, never dequantizing to cache | 2.78T model across an 8.24 GB to 224 GB memory ladder with byte-identical output |
| [PRIMA.CPP](https://arxiv.org/html/2504.08791v1) | C++ | Distributed 70B-scale inference with piped-ring parallelism and prefetch | Memory pressure below 6%, beating llama.cpp, exo and dllama on 30B+ models |
| UNLTD Inference v1.0.0 | Rust | mmap + OS demand paging with explicit accounting | 5.63 GB model on a 3 GB budget, ~113 MB controlled, ~14.3 s/token |

The pattern across that table is that every project which actually streams implements a real I/O policy, and the ones that only map files rely on the kernel. ramvamp is the cleanest counterexample to anyone who thinks unltd-inference's approach is the state of the art: it runs a 30B MoE inside 3 GB with swap disabled, keeps only about 1,023 MiB of common weights resident, fetches routed experts with `io_uring` plus `O_DIRECT` so misses cost the memory budget nothing, sustains roughly 1.6 GB/s at decode read geometry, and validates against llama.cpp at a mean full-vocabulary KL of 1.04e-2 with 8/8 top-1 agreement. It also ships an OpenAI-compatible serving surface on loopback, which unltd-inference does not have at all.

kimi-k3-in-c is the intellectual parent, and the project says as much: unltd-inference's design decisions came out of a source-level audit of it, and the audit's adopt/reject table is written down. Adopted: pin the trunk, never dequantize weights into a cache (a packed 17.55 MB slot versus 132 MB unpacked is a 7.5x capacity difference), and use explicit reads when `mmap` makes RSS unmeasurable at 1.56 TB scale. Rejected: inheriting the C99 engine wholesale instead of rewriting under a memory budget contract.

## Why Is "It Is Written in Rust" Not the Value Proposition?

Because Rust is not the differentiator and the ecosystem already proves it. A pure-Rust llama.cpp alternative exists in [cool-japan/oxillama](https://github.com/cool-japan/oxillama) - roughly 165,000 lines of code, 20 architectures and 25 quantization types - and there is even a Rust port of the Kimi K3 engine. Language choice is a solved question in this niche.

The crate landscape is also a poorer fit than it looks. Candle is the obvious candidate for a Rust inference runtime, and a detailed [Rust ecosystem gap analysis](https://blog.victorbona.dev/compendium/cpu-llm-inference/rust-ecosystem) rates its CPU backend as actively unsuitable for over-RAM work: tensors are `Arc<RwLock<CpuStorage>>` (reference-counted, write-locked, heap-allocated), dense ops run through ndarray, k-quant SIMD is thin, and there is **no mmap at all** - every weight lands in a `Vec<u8>`, so streaming is structurally impossible. The same source estimates Candle's CPU path at roughly 60-70% of llama.cpp throughput on Q4_K_M.

That analysis reaches the split unltd-inference follows by instinct: build the inference core from scratch, take infrastructure from crates. Its target specification - 9B parameters, 2 vCPUs, 6 GB RAM, 2-5 tok/s - is nearly identical to unltd-inference's validated regime, which makes a from-scratch Rust core defensible rather than NIH. The value is in memory policy and instrumentation, not in the borrow checker. If you are choosing between Rust runtimes for everyday local work, our comparison of [local AI model serving frameworks](/posts/local-ai-model-serving-frameworks-2026/) is the more practical starting point.

## Why Does On-Disk Layout Beat the Syscall Choice?

Because the most under-reported lever in disk-first inference is not which I/O primitive you call, it is how the bytes are arranged on disk. The measurements from llama.cpp discussion #18758 make the case: replaying the exact per-token read pattern cold, a co-activation-ordered expert layout cut reads per token from **1,418 to 775**, and an interleaved layout cut it to roughly **370** - a 2.23x improvement in cold decode I/O, achieved purely by file layout. Separately, reading explicit slices beat page faults by 13-14% end to end on both stock and rewritten files, because 16 KiB faults plus the kernel's readahead are blind to structure.

The corollary is a warning that any "explicit memory control beats the OS" claim has to survive. On an 8 GB M2 MacBook Air, a 460-line user-space LRU expert cache measured **2.4x slower** than 15 lines of `madvise` prefetch - 0.24 versus 0.57 tok/s - according to the [llama-cpp-expert-sniper writeup](https://huggingface.co/waltgrace/llama-cpp-expert-sniper). The cache duplicated data and stole RAM from the page cache. In the same experiment, stock llama.cpp produced 0 tok/s of indefinite thrashing on a 10.6 GB MoE model, while even a no-op evaluation callback reached 0.46 tok/s simply because it incidentally warmed mapped pages. The lesson is blunt: do not fight the OS page cache, coach it.

Two more measurements round out the picture. For a fully offloaded **dense** model the mmap strategy collapses entirely, because every token logically touches the whole weight file and per-token latency approaches model size divided by storage bandwidth - which is exactly unltd-inference's regime at 9B dense, and exactly why 14.3 s/token is normal there rather than embarrassing. And `mmap` does not wear out an SSD: evicted read-only mapped pages are re-read, not written back, so a disk-first weight workload is a read workload while the KV cache and context are the write side. That correction, raised in both the HN thread and [llama.cpp discussion #19163](https://github.com/ggml-org/llama.cpp/discussions/19163), defuses the most common objection to this entire design space.

## What Is Missing in v1.0.0 and What Is on the Roadmap?

Almost everything that would make it a runtime you would use daily.

- **SIMD kernels.** Q4_K, Q6_K and Q8_0 are scalar reference paths; there is no AVX2 and no NEON.
- **Multithreading.** Single-threaded execution, with `rayon` in the dependency list but not in the hot path.
- **Sampling.** Greedy only, temperature fixed at zero - no top-k, top-p, repetition penalty or grammar support.
- **Layer and expert streaming.** Prefetch, double buffering and MoE execution are explicitly absent; this is the gap ramvamp and WARP fill.
- **MoE support.** None, which excludes exactly the model class where disk-first execution is most attractive.
- **Platform breadth.** Windows x86-64 is the only validated target; Linux is declared unvalidated.
- **Serving surface.** No HTTP server, no OpenAI-compatible API, no bindings - CLI only.
- **Independent verification.** Nothing in this article has been reproduced by anyone other than the author.

Set against that list, the roadmap is the interesting artifact. The direction the project has committed to - Direct I/O as an *opt-in and measured* option rather than as dogma - is the right lesson to have taken from the `madvise`-versus-LRU result above. Whether the project executes on it is a different question from whether its design instincts are sound.

## Should You Use UNLTD Inference? The Verdict

Not as a daily driver, and the project does not pretend otherwise. At ~0.07 tokens per second it is roughly two orders of magnitude slower than a resident 9B model on the same class of CPU, single-threaded, scalar, Windows-only, and validated on exactly one architecture. Two-thirds of Hugging Face model downloads are models at or under 1B parameters and 78.2% are at or under 7B, with the median model around 900M parameters - a 7B model at 4-bit is about 4 GB, so the overwhelming majority of what people actually run fits in commodity RAM. Disk-first execution is a research and constrained-deployment technique, not a mainstream need.

Where it does earn a place:

1. **As a reference architecture.** If you are writing your own over-RAM inference runtime in any language, the crate boundaries, the budget-contract design and the adopt/reject audit table are a free blueprint.
2. **As a measurement instrument.** The exit-code contract, the machine manifest, the median-of-3 protocol and the cgroup-enforced budget are a template you can reuse for any memory-constrained benchmark, which is the transferable lesson the project's own documentation argues for.
3. **As a cautionary case study in claim reading.** "Runs a 5.63 GB model on a 4 GB budget" and "peak working set ~5.24 GB" are both true, and learning to hold both in your head at once is the skill this genre of article exists to teach.
4. **As a signal about where the field is going.** llama.cpp's over-RAM expert streaming PR is closed and unmerged; the projects actually shipping disk-backed inference are small, single-author and MoE-focused. That is the interesting 2026 story, and unltd-inference is a clean, honest, incomplete entry in it.

If you need disk-backed inference in production today, look at ramvamp for MoE serving and at llama.cpp's default mmap for everything else. If you want to understand how memory-budgeted inference should be reasoned about, read unltd-inference's documentation - it is better than its throughput by a wide margin.

## FAQ

### What is unltd inference written in Rust?

UNLTD Inference (`unltdev/unltd-inference`) is an Apache-2.0 Rust workspace of eight crates for CPU-only GGUF inference, with MSRV Rust 1.80, edition 2021 and a minimal dependency set including `memmap2`, `half`, `bytemuck`, `clap` and `rayon`. It is a from-scratch inference core rather than a wrapper over Candle or llama.cpp bindings.

### Can unltd-inference really run a model larger than its memory budget?

Yes, and this is the project's central validated claim - but the budget governs runtime-controlled memory only. In the validated v1.0.0 run, a 5.63 GB model executed under a 3-4 GB budget with about 113.19 MB of controlled runtime memory (minimum viable budget 113.06 MB), while peak process working set still reached roughly 5.24 GB because the mapped model file counts toward RSS. The weights contribute zero bytes to the controlled budget because they are memory-mapped views, never heap copies.

### How is unltd-inference different from llama.cpp?

Not through speed or coverage. llama.cpp has roughly 130,000 stars, 146 registered GGUF architectures and mmap enabled by default, which already lets an oversized model run on a small machine. unltd-inference's differentiators are explicit pre-validated memory accounting (it prints `REFUSING TO RUN` and exits 2 rather than failing at runtime), a published oracle-comparison workflow against llama.cpp, and a determinism-across-memory-budgets measurement protocol. It is slower, narrower and far less mature.

### What are unltd-inference's biggest limitations in v1.0.0?

Scalar-only kernels with no SIMD or AVX2, no multithreading, greedy decoding only (temperature zero), no MoE execution, no layer or expert streaming or prefetching, no GPU path, and Windows x86-64 as the only end-to-end validated platform - Linux is explicitly not validated. Generation also diverges from the llama.cpp oracle after about eleven greedy steps, which the project documents openly as an argmax near-tie flip caused by scalar-versus-AVX2 numeric accumulation.

### Should I use unltd-inference for local LLM inference?

Not for interactive work. Published throughput is roughly 73 seconds of prefill and about 14.3 seconds per token (~0.07 tok/s), which is two orders of magnitude off a resident model of the same size and makes it usable only as a batch or research workload. Its real value is as a correctness-first reference implementation you can study, plus a reusable measurement protocol for memory-constrained benchmarking. For actual daily local inference, a resident 9B quantized model on llama.cpp or Ollama remains the practical choice - see our guide to [the best local LLM models](/posts/best-local-llm-models-2026/) for current options.
