---
title: "GPU Offload in Rust: Portable, Safe, and Fast (2026 Guide)"
date: 2026-10-01T03:17:47+00:00
tags:
  - GPU offload Rust
  - Rust GPU offload
  - rustc GPU offload
  - std::offload Rust
  - gpu_offload feature flag
  - Rust GPU kernels
  - write GPU kernels in Rust
  - Rust CUDA alternative
  - wgpu compute shader Rust
  - CubeCL Rust kernels
  - safe GPU kernels Rust
  - noalias Rust GPU
  - Rust vs CUDA performance
  - cuda-oxide Rust PTX
  - rust-gpu SPIR-V
  - rustc offload tracking issue 131513
description: "GPU offload in Rust now means rustc compiling safe Rust kernels to CUDA and HIP via LLVM Offload. How it works, what it costs, and which path to pick."
draft: false
cover:
    image: "/images/gpu-offload-in-rust-portable-safe-fast.png"
    alt: "GPU Offload in Rust: Portable, Safe, and Fast (2026 Guide)"
    relative: false
schema: "schema-gpu-offload-in-rust-portable-safe-fast"
---

GPU offload in Rust is the practice of compiling Rust code into GPU kernels instead of writing them in CUDA C++ or HIP. In 2026 there are four real ways to do it: `wgpu` with WGSL shaders, CubeCL's `#[cube]` kernels, rustc's experimental `std::offload` built on LLVM Offload, and vendor-specific paths such as `cudarc` or NVIDIA's `cuda-oxide`. Only the rustc path promises safe Rust kernels with automatic data movement — and it is still nightly-only.

The rest of this guide is about choosing between those four, understanding what the new research actually proved, and avoiding the one mistake that costs more than any kernel-level tuning you will ever do: moving data on every kernel launch.

## What does "GPU offload in Rust" actually mean in 2026?

The phrase covers at least three different things today, and conflating them is why most discussions of "Rust on the GPU" go nowhere.

**Host-side offload.** Your Rust program allocates device memory, uploads buffers, and launches kernels that were written in CUDA, HIP or WGSL. This is mature. `cudarc` (0.19.10, roughly 9.0M downloads) is the thin, unsafe binding layer; `candle` (21,127 stars) and Burn (16,008 stars) sit on top of it. Your Rust is memory-safe; your kernel is not Rust.

**Rust-as-shader-language.** The kernel itself is Rust, compiled to SPIR-V, PTX or WGSL by a dedicated compiler. This is what Rust GPU, Rust CUDA, and CubeCL do. This is the half of the ecosystem that is still moving.

**Compiler-integrated offload.** The kernel is Rust, and the *rustc you already use* compiles it, using the same LLVM Offload infrastructure that OpenMP already uses for C++ and Fortran. This is the new research result, and it is the only one of the three where the type system drives data movement.

If you are trying to decide what to install this afternoon, that taxonomy is your decision tree. If you want to understand where the field is heading, read on.

## What did the rustc GPU offload research actually prove?

The paper "GPU Offload in Rust: Portable, Safe, and Fast" (Drehwald, Dominguez, Sala, Aspuru-Guzik, Doerfert; arXiv:2608.13759, submitted 13 August 2026) asks a blunt question: does Rust's memory safety cost you GPU performance? The answer is that it does not — with two large asterisks.

The thesis inverts the usual sales pitch. Ownership is normally framed as a tax you pay for correctness. On the GPU, LLVM does not see it that way: a Rust `&T` carries `noalias` metadata, which is the same information C++ programmers write by hand as `restrict` and routinely forget. Safe Rust references give the optimizing backend restrict-style information for free. Safety is the input to optimization, not a deduction from it.

The prototype is not a side project bolted onto the toolchain. It is built into rustc on top of LLVM's Offload infrastructure — the same infrastructure already shipping for OpenMP. The evaluation ported RAJAPerf to pure Rust and ran on AMD MI250X, NVIDIA H100, and RTX A2000-class hardware, compiled with a rustc based on LLVM 23.1.0-rc1.

Results, stated honestly:

| Platform | Rust vs baseline (whole benchmark runtime) | Worst cases |
|---|---|---|
| AMD MI250X | 32% faster to 43% slower vs RAJA | unroll-sensitive micro-benchmarks |
| NVIDIA H100 | 11% faster to 46% slower vs base CUDA | FIR (-44%), LTIMES (-46%) |

On AMD, the same two micro-benchmarks are where Rust *beats* base HIP by 15% (FIR) and 32% (LTIMES). That spread is a compiler-unrolling artifact, not a portability artifact — the same kernel wins on one backend and loses on the other depending on how the loop got unrolled. Anyone quoting a single number from this paper is quoting a specific kernel on a specific backend.

The more consequential number is not in the kernel results at all. Using the automatic interface naively can be **more than 400x slower** than the explicit interface on MI250X. We will come back to that, because it is the single most actionable finding in the paper.

## How does the type system replace data-mapping pragmas?

In OpenMP you write mapping clauses by hand: `map(to: a)`, `map(tofrom: b)`, and you get them wrong in exactly the places nobody notices until the numbers are subtly wrong. The rustc offload work derives those clauses from the borrow checker instead.

The rule is small and the consequences are large:

| Rust type in the kernel signature | OpenMP mapping | Meaning |
|---|---|---|
| `&T`, `*const T` | MapTo | device-only, read-only on the GPU |
| `&mut T`, `*mut T` | MapToFrom | bidirectional, written back |
| scalars up to 64 bits | by value | passed in the launch parameters |

A `&[f32; 1024]` moves only to the device. A `&mut [f64]` moves both ways. The host-side dispatch wrapper — generated by the `#[offload_kernel]` attribute — emits the runtime calls with a simplified type tree describing each layout, and the direction comes from the mutability in the signature you already had to write.

This is worth pausing on, because it changes what a bug looks like. In CUDA, forgetting the writeback direction is a silent host-device divergence: the kernel computes, the host reads stale bytes, and you debug it three hours later. Here it is a compile error, because the same `&` versus `&mut` distinction that the borrow checker enforces on the host is what generates the transfer.

You do not get this for free in the general case, though. The documented limitations of `std::offload` include: only types supported by the current device-mapping implementation, no generics in kernels, and no `dyn Trait`. The canonical example in the standard library docs still dereferences a raw pointer inside an `unsafe` block. Type-driven mapping is the design goal; the escape hatch is still there for the cases it does not cover.

## How do you write a kernel without raw pointers?

Dropping to `unsafe` for every mutable argument would defeat the point, which is why the design adds a partitioning abstraction.

Instead of passing `*mut [f64]` and indexing it with a thread ID, you take a `Region<T, PartitioningStrategy>`. A `Region` hands each thread a disjoint subregion — `Linear1D` is the common strategy — so the indexing you perform is ordinary safe slice indexing even though the underlying memory is shared mutable data across threads.

The catch is honest and explicit in the design: `PartitioningStrategy` is itself an `unsafe trait`. Its implementors must guarantee that the subregions they produce are actually disjoint. The unsafe obligation has not been eliminated; it has been moved out of every kernel body and into the strategy, where it is written once, reviewed once, and then reused across every kernel that needs it.

That is the right place for it. A kernel body is copied and modified constantly. A partitioning strategy is a small, stable piece of logic with a single invariant, which is exactly the kind of code where an unsafe contract can be audited.

## Why can the automatic interface be 400x slower than the explicit one?

Because the cost was never in your kernel.

The design offers three interfaces:

- **Interface A — compiler-managed offload.** Data movement is automatic, derived from the types as described above.
- **Interface B — vendor library interoperability.** Your Rust kernels call cuBLAS or rocBLAS calls rather than reimplementing them.
- **Interface C — explicit type-staged memory control.** You manage transfers through `preload` and `preload_mut` handles.

Interface A is the nicest to write and, used naively per kernel launch, more than 400x slower than Interface C on MI250X. The mechanism is entirely mundane: transfer-per-kernel-launch. If a benchmark loop launches 55 kernels and each launch synchronously pulls its data across PCIe, you have turned a compute problem into a bandwidth problem with a barrier between every step.

The H100 numbers show the second-order effect. On the same workload, RAJA issues 55 host-to-device transfers totalling 468 MB; Rust issues 53 transfers totalling 423 MB — *fewer* transfers and *fewer* bytes — yet Rust's transfers take 46 ms against RAJA's 16 ms. Fewer bytes did not mean less time, because memory-kind and asynchronous-transfer differences dominate the raw byte count. Copying less data slowly loses to copying more data concurrently.

The practical rule: decide your data residency for the whole computation, not per launch. `preload` the buffers your algorithm needs for its lifetime and reuse them across launches. Treat Interface A as a convenience for single-shot kernels and small experiments.

## Why does the toolchain need a cargo wrapper?

The compilation model is deliberately two-pass: the device pass compiles kernels for `nvptx64` or `amdgcn-amd-amdhsa`, then a separate host pass compiles for `x86-64` and emits calls into the OpenMP offload runtime, carrying a simplified type tree describing layouts.

Single-pass was rejected for a structural reason: rustc expects one target per invocation. Rather than teaching every symbol in the compiler that it might have two implementations, the design keeps host and device target semantics independent and pays for that with explicit cross-pass communication. The cost is visible to users — kernel artifacts must be handed to the second rustc invocation by path, so a small cargo wrapper is required. The design rationale upstream is that a roughly five-line wrapper beats that degree of compiler surgery.

Cross-pass monomorphization is the interesting technical problem it creates. Generic Rust functions get instantiated for concrete types, and the device pass has to know which instantiations to produce. The solution is a new rustc query that serializes kernel `DefId`s plus their concrete type substitutions during the host pass, so the device pass can seed its monomorphization roots correctly.

The current rough edges are documented rather than hidden. Kernels still need `#[cfg(target_os = "")]` annotations. The device pass does not yet use rustc's query system, so kernels are always recompiled rather than incrementally cached. And, per the rustc dev guide, users currently still need to invoke another compiler — clang — to finish the process.

## How do you try it today?

The feature is real and documented, not rumor. `std::offload` is a nightly-only experimental API gated behind the `gpu_offload` feature flag, tracking issue rust-lang/rust#131513, opened 2024-10-10, labelled `C-tracking-issue` and `B-experimental`, and still open as of 2026-09-15.

The usage pattern is two steps:

1. Annotate the kernel function with `#[offload_kernel]`. This generates the host-side dispatch wrapper alongside the device-side kernel.
2. Launch it with the `core::intrinsics::offload` intrinsic, specifying grid and block dimensions.

Be aware of what that second step implies. Launching is currently restricted to intrinsic usage, which the standard library documentation itself describes as discouraged outside of `std`. There is no ergonomic launch macro yet. You are using a compiler-internal surface that will change.

Prerequisites to plan for: a nightly toolchain, a cargo wrapper to hand artifacts between the two passes, clang in the pipeline, and GPU toolchains for whichever backend you target.

## If you cannot use nightly, what are the alternatives?

This is where most readers actually live, and the honest answer is that the choice is really about *where the kernel is written*.

| Path | Kernel language | Backends | Status | Pick it when |
|---|---|---|---|---|
| **wgpu** 30.0.1 | WGSL (not Rust) | Vulkan, Metal, DX12, OpenGL, WebGPU | Stable; ~37.8M downloads, 18.2k stars | You need portability and stability, including the browser |
| **CubeCL** 0.11.0-pre.4 | Rust via `#[cube]` | CUDA, ROCm/HIP, Metal, Vulkan/SPIR-V, WebGPU/WGSL, CPU SIMD | Pre-release but production-backed by Burn; ~1.31M downloads, 2.4k stars | You want Rust kernels today across several backends |
| **rustc `std::offload`** | Rust | nvptx64, amdgcn (Intel later) | Nightly, experimental, issue #131513 open | You are researching, prototyping, or contributing |
| **cudarc / cuda-oxide** | Rust → PTX (oxide) or C++ kernels (cudarc) | NVIDIA only | cudarc 0.19.10, ~9.0M downloads; cuda-oxide 3.6k stars | You are NVIDIA-locked and want the vendor path |
| **Rust GPU / Rust CUDA** | Rust | SPIR-V/Vulkan, Metal, DX12, WebGPU (rust-gpu); NVIDIA (rust-cuda) | rust-gpu 3.4k stars at Rust-GPU/rust-gpu; rust-cuda 5.4k stars | You want Rust shaders without nightly rustc |

Two warnings for anyone following older tutorials.

First, the **original `EmbarkStudios/rust-gpu` repository is archived and read-only** — last pushed 2025-10-31, with 107 open issues. Development continues at `Rust-GPU/rust-gpu` (3,383 stars, active as of 2026-09-30). The archived repository still outranks its active successor in search results, which is a reliable way to spend an afternoon on a dead issue tracker. A July 2025 demo showed one shared Rust codebase — a bitonic sort — running on CUDA, SPIR-V/Vulkan, Metal, DirectX 12, WebGPU and a CPU fallback with no shader language involved. That is the capability the successor repo carries.

Second, **Rust CUDA requires raw pointers for all mutable arguments.** At 5.4k stars it is the most popular Rust-to-NVIDIA path, and its kernels are not memory-safe. That is precisely the gap the rustc offload work exists to close, and it is worth being clear-eyed that a popular crate is not the same thing as a safe one.

If you want the middle ground, CubeCL is the pragmatic choice. A single `#[cube]` function is JIT-compiled for whichever backend is present, and it powers the Burn deep-learning framework, so it is load-bearing rather than experimental. Its portability model is the part worth internalizing: four orthogonal axes — Vector, Plane, CubeDim, CubeCount — so a kernel reads the runtime maxima and specializes itself. The README calls out hardcoding `warpSize == 32` as *the* classic CUDA antipattern, because AMD's wavefronts are 64 lanes wide. If your Rust kernel assumes 32, it is not portable, it is just untested.

Even `wgpu`, the stable baseline, has a documented ceiling: no tensor cores through WebGPU, and Firefox still ships WebGPU disabled by default. Compute in `wgpu` also means writing WGSL — your Rust host is memory-safe, your shader is a different language, which is exactly the split the offload work is trying to remove.

## What does safe Rust actually cost on the GPU?

Less than you would guess, and it is measurable.

Average kernel register usage on an RTX 2070 across 13 RAJAPerf kernels was 33 registers for Rust versus 28 for RAJA-CUDA. That is about five extra registers, attributed to bounds checks. Crucially, the paper measured **no runtime impact** from bounds checking in these kernels at the sizes tested.

The reason is worth understanding if you are porting CPU Rust. On the CPU, the idiomatic iterator pattern lets the optimizer prove that indexing is in bounds and eliminate the check entirely. In a GPU kernel you index explicitly with thread and block IDs, which defeats that analysis. So the checks survive into the generated code — and yet the cost is hidden by memory latency, because a kernel with enough occupancy has spare cycles to burn on arithmetic while waiting for the memory subsystem.

The real performance lever on the GPU is not the bounds check. It is unrolling and fast-math.

Fast-math is the subtler story. C++ programmers reach for `-ffast-math`, which enables `nnan` and `ninf` — assumptions that would be undefined behavior in safe Rust and therefore cannot be turned on globally. The paper's answer is experimental algebraic floating-point operations: a safe alternative that produced a **2x speedup on the FIR kernel** and roughly 20% on DEL_DOT_VEC_2D, VOL3D and MATVEC3D on an RTX A2000. That is a large win from a mechanism most Rust GPU discussions never mention — and it is why the unroll-sensitive micro-benchmarks swing so dramatically between backends.

## What are the limits to know before committing?

- **No generics and no `dyn Trait` in kernels.** Kernels are monomorphized across passes, and only concrete substitutions currently make the trip.
- **A device ABI mismatch is a live landmine.** On `x86_64` and `amdgcn`, a slice lowers as a `(ptr, len)` pair; on `nvptx64` it lowers as `[i64; 2]`. The divergence is documented in the paper as the reason cross-boundary ABI validation must be settled before struct support can be added. It is also a good illustration of why "portable" here means the compiler does the porting, not that the layouts are identical.
- **No `std` on the device.** You are in `no_std` territory on the GPU side.
- **No safe fast-math.** As above, the 2x FIR result depends on experimental algebraic float ops, not a compiler flag.
- **It is nightly.** Feature flags, a cargo wrapper, and clang in the loop. The `gpu_offload` flag is tracking issue #131513, open since October 2024, last updated 2026-09-15.
- **Vendor kernels still need the vendor.** Interface B deliberately lets you call cuBLAS/rocBLAS rather than reimplementing them, which is the right engineering call and also a reminder that no portable abstraction covers everything.

## Which Rust GPU path should you pick?

If you are shipping today and the kernel is not the product: use **wgpu**. It is stable, the most-used GPU crate in the Rust catalog at ~37.8M downloads, and covers Vulkan, Metal, DirectX 12, OpenGL and the browser from one compute API. Accept that you are writing WGSL and that tensor cores are off the table.

If your kernel is the product and you need Rust: use **CubeCL**. One `#[cube]` function, JIT-compiled across CUDA, ROCm, Metal, Vulkan/SPIR-V, WebGPU and CPU SIMD, with the four-axis portability model that stops you from hardcoding a warp size. It is pre-release, but Burn depends on it.

If you are NVIDIA-locked: **cudarc** for host-side control, or **cuda-oxide** for vendor-supported Rust-to-PTX. NVIDIA shipping two Rust kernel tracks — `cuda-oxide` (3,635 stars, pushed 2026-10-01) and `cuTile Rust` (1,042 stars) — is the strongest single signal that Rust GPU kernels have moved from community experiment into vendor roadmaps.

If you are exploring the frontier, or contributing: build **rustc's `std::offload`** on nightly. Follow tracking issue #131513. Understand that "portable, safe, and fast" is currently a research result plus a nightly preview, not a production path — and that the research result is genuinely strong: a safe Rust kernel that lands within roughly one unrolling decision of hand-tuned CUDA, with data direction derived from the borrow checker instead of written by hand.

And whichever path you choose, profile your transfers before you tune anything. The 400x figure is the paper's real headline, and it applies to every entry in that table.

## FAQ

**Is GPU offload in Rust production-ready in 2026?**
Not via rustc. `std::offload` is a nightly-only experimental API behind the `gpu_offload` flag (tracking issue #131513, open since October 2024) and currently requires clang in the pipeline. For production work, `wgpu` is stable today and CubeCL is usable with the caveat that it is at a pre-release version.

**Can safe Rust kernels match hand-tuned CUDA performance?**
Close, with caveats. On H100, Rust Offload ranged from 11% faster to 46% slower than base CUDA across RAJAPerf; on the AMD MI250X it ranged from 32% faster to 43% slower than RAJA. The worst cases — FIR and LTIMES — are unroll-sensitive micro-benchmarks where the same kernels *beat* base HIP by 15% and 32% on AMD. The spread is a compiler-unrolling artifact, not an inherent safety penalty.

**Does Rust's memory safety cost GPU performance?**
Measured cost is about five extra registers per kernel (33 vs 28 on an RTX 2070 across 13 kernels) attributable to bounds checks, with no runtime impact measured in those kernels. Bounds checks survive into GPU code because explicit thread/block indexing defeats the optimizer analysis that eliminates them on the CPU, but memory latency hides the cost at useful occupancy levels.

**Why is the automatic data-movement interface so much slower?**
Because it transfers per kernel launch. Used naively it can be over 400x slower than explicit type-staged memory control on MI250X. Even where Rust moved fewer bytes than RAJA on H100 (423 MB vs 468 MB), its transfers took 46 ms against RAJA's 16 ms due to memory-kind and async-transfer differences. Declare data residency for the whole computation and reuse buffers.

**Which is the best Rust GPU crate to start with today?**
Depends on where you want the kernel written. For stability and maximum portability including the browser, `wgpu` (30.0.1, ~37.8M downloads) with WGSL. For Rust kernels across multiple backends today, CubeCL (`#[cube]`, powering Burn). For NVIDIA-specific work, `cudarc` or `cuda-oxide`. For compiler-integrated safe kernels, nightly rustc and tracking issue #131513.
