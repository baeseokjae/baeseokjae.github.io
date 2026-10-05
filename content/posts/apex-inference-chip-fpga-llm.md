---
title: "Apex Inference Chip Review: 0.56 tok/s and the Truth About FPGA LLM Inference"
date: 2026-10-01T05:22:22+00:00
tags:
  - fpga llm inference
  - apex inference chip
  - apex tinynpu
  - running an llm on an fpga
  - kv cache compression in hardware
  - int4 kv cache fpga
  - bit-exact rtl verification
  - golden model rtl verification
  - qwen2.5-0.5b fpga
  - aws f2 fpga llm
  - lattice ecp5 llm accelerator
  - fpga vs gpu energy per token
  - joules per token llm
  - on-chip llm weights
  - systolic array transformer accelerator
  - edge llm inference hardware 2026
description: "The APEX (tinyNPU) chip runs a real LLM on an FPGA at 0.56 tok/s — measured, not projected. A review of what silicon proved and what is still a model."
draft: false
cover:
  image: "/images/apex-inference-chip-fpga-llm.png"
  alt: "Apex Inference Chip Review: 0.56 tok/s and the Truth About FPGA LLM Inference"
  relative: false
schema: "schema-apex-inference-chip-fpga-llm"
---

The Apex Inference Chip (SigmanticAI's APEX, or tinyNPU) does run a real LLM on an FPGA, and it does so at **0.56 tokens per second** on its fastest measured image — roughly 1.78 seconds per token, confirmed on two separate builds. That number is deliberately slow, honestly published, and the entire point of the project is the verification trail behind it.

That paragraph is the honest summary, and this review exists because almost every other sentence about this repository can be made misleading with one small edit. Strip the words "measured on silicon" and APEX looks like a hardware failure. Strip "one decoder layer" and it looks like a chip. Strip "projected from an analytic model" and its 7B performance claims look like results. The repository itself refuses to let you do any of those things, which is why it is worth your time even if you never build a bitstream.

A quick note on scope before we start: this is a review of a research artifact, not a product. The repo was created on 2026-08-17, last pushed on 2026-08-18, and sits at 580 stars and 13 forks as of 2026-10-01. It is Apache-2.0, roughly 72,000 lines of SystemVerilog, Python and documentation. It is a tile, not a chip — no DRAM controller, no PCIe, no network-on-chip, by explicit charter.

## What Is the "Apex Inference Chip"? Three Different Things Share the Name

Anyone searching for "apex inference chip" will land on the wrong project, and it is worth resolving that in the first minute because two of the three are commercial and one is open source.

- **SigmanticAI/apex-inference-chip (APEX, tinyNPU).** The subject of this review. An Apache-2.0 RTL inference tile whose tagline — running a real LLM on an FPGA — is the article title above.
- **Apex Compute (apexcompute.com).** A separate commercial startup shipping a "Unified Engine" FPGA prototype. Different company, different artifact, different numbers. Its Kintex UltraScale+ design closes timing at 366 MHz with 78,348 CLB LUTs, 197 DSP slices and 1.05 MB of on-chip SRAM, and claims Gemma 3 1B decode at 15.63 tokens/second against 7.59 on an NVIDIA Jetson Orin Nano. Those are its own prototype claims and are not comparable to APEX's tile-level measurements.
- **SigmanticAI (sigmanticai.com).** The YC-backed vendor that supplied the Polaris Engine verification tooling used to build APEX. It is the tool vendor, not the artifact — a distinction that matters when we get to conflicts of interest.

If you arrived here looking for Apex Compute, the numbers you want are in the second bullet. Everything below is about the open tile.

## The 60-Second Version: What SigmanticAI Shipped and What It Measured

APEX implements **one transformer decoder layer** — all seven matrix jobs of it — on a single INT8 systolic GEMM engine, time-multiplexed. The seven jobs are the QKV projections, the two attention products, the output projection, and the FFN gate/up and down projections. There is no second engine, no separate attention unit, and no FP16 datapath for K or V anywhere in the design.

Two facts define the artifact:

1. **A model actually ran end-to-end on silicon.** On 2026-08-11, on an AWS F2 VU47P instance (AFI `agfi-0500f4afe435b5e71`), the prompt "The capital of France is" produced " Paris. It" under greedy decode, token-identical to the host-golden reference. All 72 walked chains completed, zero refused, and every walked value was bit-exact: 144/144 QKV INT32 accumulators and 896/896 first-round FP16 values per chain.
2. **The published speed is 0.56 tokens/second.** That is the fastest registered image, designated A0, running at 62.5 MHz with a steady 1.78 s/token. The reference image, A2 at 15.625 MHz, does 0.25 tok/s.

Both statements are about Qwen2.5-0.5B. The 7B model has never run on silicon here — more on that below, because it is the single most important caveat in this review.

## Inside the Tile: One Decoder Layer, One GEMM Engine, Seven Jobs

The design decision that makes APEX interesting is also the one that makes it slow: everything is funneled through one matrix engine, the MXE. A single INT8 systolic array performs every projection in the decoder layer by time-slicing. That is a hardware-efficiency trade, not a throughput play — you buy area and utilization predictability, and you pay in latency.

The KV-cache codec, called KVQ, lives inside the datapath rather than beside it. It uses per-channel INT4 keys, per-token INT4 values, and a single FP16 "outlier lane" to catch the values that INT4 would destroy, with three precision tiers — KVQ8, KVQ4 and KVQ4+ — and a TIP importance unit that promotes or demotes tokens between tiers as generation proceeds. The repo's claim is architectural: there is no FP16 copy of K or V anywhere in the design, so the cache is never expanded back to full precision between RoPE and the store.

That matters because of where the bottleneck actually sits. The 2026 SoK paper "The KV Cache Is the New Memory Wall" (arXiv 2609.30854) makes the case quantitatively: Llama-3-70B in BF16 has a 140 GB weight footprint, which already exceeds one accelerator's 80 GB of HBM, and a *single* 128k-token sequence adds 42 GB of KV cache on top. At long context, the binding resource stops being the weights and becomes the cache.

## The Architectural Bet: The KV Cache Is Compressed Inside the Datapath

There is a second, subtler reason the placement matters. arXiv 2603.17280, "The 1/W Law," measures how tokens per watt behave as context grows: it halves every time the context window doubles on identical hardware. An H100 holds 256 concurrent sequences at 4K context for 17.6 tokens per watt, but only 16 sequences at 64K for 1.5 tokens per watt. The 40x spread that operators attribute to software inefficiency is, in that framing, mostly a context-window effect.

If that is true, then compressing the KV cache is not a memory optimization — it is a *power* optimization. APEX's TIP unit exists precisely because the SoK finding is that accuracy degrades below 4-bit precision and turns discontinuous for eviction on position-sensitive tasks. Moving tokens between precision tiers is an attempt to buy that back.

The repo is candid that the codec method itself is not novel. Per-channel INT4 keys with per-token INT4 values and an FP16 outlier is the KIVI and KVQuant recipe, and hardware-native KV compression predates APEX in Titanus (GLSVLSI'25) and Kelle (MICRO'25). What APEX claims is the integrated, verified hardware implementation — the codec and the GEMM engine and the bit-exact test trail in one open repository. That is a real but narrower claim than "invented KV compression in hardware," and the repository says so in as many words.

## The Methodological Bet: Bit-Exact or It Does Not Ship

This is the actual product. The verification surface is roughly **twice** the RTL surface: 27,760 lines of SystemVerilog and SVH testbenches plus 21,043 lines of Python, measured against about 22,000 lines of RTL and 5,884 lines of golden Python. The golden NumPy model is the arbiter, not the spec.

The discipline shows up in three places:

- **Exhaustive sweeps instead of spot checks.** The SiLU activation is verified over 65,536 input patterns, bit-exact against golden. The W4B feeder runs a 4,063,104-point operand sweep. Several suites carry between four and nine asserted mutant kills, and a surviving mutant fails the build — the testbenches are themselves mutation-tested.
- **Compositional verification, L1 to L3.** Block-level tests roll up into pipeline tests and then into full-layer composition. The L3 full-layer attention replay passed 28 cases across 152,883 checks, spanning mixed CQ-8, CQ-4+ and TIP-auto precision tiers at head dimensions 64 and 128 with sequence lengths up to 128.
- **Zero tolerated mismatches.** The tile smoke test reports `cycles=67507 checks=2176 errors=0` at D=64 and `cycles=209741 checks=4240 errors=0` at D=128. A machine-generated STATUS.md, produced by `scripts/gen_status.py` under an anti-fabrication rule, carries the raw evidence.

One caveat deserves its own line, because it is the most common misreading of this project: bit-exactness is relative to a fixed-point golden model the team wrote. Bit-exact against golden is not the same as numerically correct against the float behavior of the original model. The codec's own accuracy is measured separately on HellaSwag across 10,042 documents with paired statistics and its own honest caveats.

## The Synthesis Toolchain Was Lying: How Silicon Caught It

This is the best story in the repository, and the one that most cleanly justifies the whole approach.

During bring-up of the walked-attention path, the FPGA produced **wrong values** while the Verilator simulation twin produced correct ones on the same stimulus. The natural first instinct — assume the RTL is wrong, or the testbench is wrong — was eliminated by the differential itself. Two implementations of the same source disagreed; one of them was running on silicon. The team traced the divergence and isolated a **synthesis toolchain defect**, not an RTL bug and not a testbench bug.

The resulting rule is now the repo's operating principle: hardware truth comes from silicon-versus-simulation differential evidence, not from synthesis reports. Most open RTL never touches silicon at all, and the projects that do tend to trust the synthesis log as ground truth. APEX committed to the opposite — and the toolchain it caught is not named in the material I could verify, so treat "which vendor" as unreported rather than inferred.

That the toolchain in question is the vendor's own Polaris Engine tooling is a genuine conflict-of-interest surface for a project whose headline value is verification. The mitigations are structural: machine-generated status files, committed logs, mutation gates that fail the build, and a public traceability register. Whether that is enough is a judgment call, but the conflict is disclosed rather than hidden.

## How Fast Is It, Really? 0.56 tok/s and the 140x Ladder

The headline number is 0.56 tokens per second, and the repo's own optimization document shows a **140x climb** from a host-driven baseline of 0.004 tok/s to that figure. The ladder is worth understanding because it tells you where the time actually goes.

On the walked path, the arithmetic performed inside the tile accounted for **8.53%** of per-token MACs — 44,040,192 of 516,196,352. The remaining wall was dominated by per-chain host transport: 24 executor invocations per token at roughly 0.5 seconds each. The tile's own walk window is about **36 ms** on the A2 reference image.

In other words, the tile is not the bottleneck. The host orchestration around it is. That is the correct attribution, and it is the attribution the repo makes; a review that quotes 0.56 tok/s without it is describing a transport problem as a hardware problem.

| Image | Clock | Steady decode | Model | Status |
|---|---|---|---|---|
| A0 (fastest registered) | 62.5 MHz | 0.56 tok/s (1.78 s/token) | Qwen2.5-0.5B | Measured on silicon, confirmed on two builds |
| A2 (reference) | 15.625 MHz | 0.25 tok/s | Qwen2.5-0.5B | Measured; tile walk window ~36 ms |
| 7B end-state | — | "reading speed" at ~3 W | Qwen2.5-7B | **Projected** from an analytic model, never run on silicon |

## Measured vs Projected: Read This Before Quoting Any Number

The repository's own rule is that a number is either measured on hardware or simulation, or it is a projection from a calibrated analytic model — and it says which. Applying that filter to the claims gives you this split:

| Claim | Measured or projected | Notes |
|---|---|---|
| 0.56 tok/s on Qwen2.5-0.5B | Measured | A0 image, 62.5 MHz, two builds, all gates passing |
| Bit-exact walked tokens, 72/72 chains | Measured | AFI `agfi-0500f4afe435b5e71`, 2026-08-11 |
| AWS F2 timing closure at 250 MHz shell clock | Measured | Vivado zero-error P&R on VU47P; BAR0 CSR probe all pass |
| Lattice ECP5-85F build via yosys/nextpnr | Measured | Second independent hardware existence proof |
| L3 replay: 28 cases, 152,883 checks | Measured | Mixed KVQ tiers, D=64/128, T≤128 |
| 7B at reading speed on ~3 W, 32k–64k context | **Projected** | Three unbuilt dependencies: native W4 weight path, hardware layer walker, wide LPDDR |
| 5–10x less energy per token than a desktop GPU | **Projected** | Derived from the same analytic model |
| Faster than a GPU | **Explicitly not claimed** | README states it is "never a speed win over GPUs" |

Three load-bearing pieces of the 7B projection do not exist yet. The native-W4 weight path is not committed end-to-end. The hardware layer walker that would remove the host from the token loop is not built. The wide LPDDR interface that would feed weights at the required rate is not built. And Qwen2.5-7B has run only through the software-verified golden pipeline — never through silicon. Any article that presents the 7B figures as results is repeating a projection as a measurement.

## The FPGA Reality Check: 0.56 tok/s vs 59,965 tok/s

Here is where a naive reader concludes that FPGAs are slow. They are not; they are differently shaped, and the two families are easy to contrast.

TerEffic (arXiv 2502.16473) keeps weights fully on-chip and reaches **16,300 tokens/second** on a 370M ternary model — 192x the throughput of a Jetson Orin Nano, at 455 tokens/second/watt. With HBM assistance it does 727 tok/s on a 2.7B model, three times an A100. Separately, a Taalas-style build on a $250 Xilinx Kria KV260 keeps a 3.16M-parameter INT4 transformer entirely in on-chip memory and measures **59,965 tok/s** on the fabric, bit-exact, with zero DRAM in the token loop. The same board's Arm cores manage 11 tok/s and an RTX 3050 Ti laptop manages 719 tok/s.

The structural insight behind those numbers is that decode is memory-bandwidth-bound: you read every weight once per token, so arithmetic is cheap and *reading* is the cost. Once weights live on-chip, the memory wall disappears and throughput explodes. The crossover is honest and published — around 6.3M parameters on that KV260 design, past which you spill to DDR and you are back at the wall. Long context spills the KV cache the same way.

APEX chose the opposite path. It keeps DRAM weight streaming and host transport in the loop by design, because its subject is a single verified decoder layer reachable from a host, not a deployed inference service. Comparing 0.56 tok/s to 59,965 tok/s is not comparing two attempts at the same goal; it is comparing a tile bring-up to a product.

## Energy per Token: The Axis Where FPGAs Actually Win

When throughput is conceded, energy is the remaining argument, and it holds up better than the speed claims in this space. A ternary-engine writeup (nicholi.ai, June 2026) measures an RTX 3060 at **3.67 joules per token**, a six-year-old desktop CPU at 4.62 J/token, and a $130 Arty A7-35T FPGA at roughly **1.6 J/token** — about 2.3x better than the GPU. System power is ~0.489 W versus 86.4 W measured for the 3060.

Two things about that comparison are worth internalizing. First, the FPGA there is explicitly *slower* than the GPU, and the author refuses the "40x faster" headline for exactly that reason. Second, the wattage is a Vivado estimate, not a current-probe reading, so the J/token figures are measured cycle counts multiplied by an estimated wattage. The author says so. That honesty is the correct template, and it is the standard to apply to every watt claim in this space — including Apex Compute's 4.5 W versus 7 W comparison and APEX's own ~3 W projection.

## Where APEX Sits in the 2026 FPGA LLM Inference Landscape

| Project | What it is | Headline measurement | Keeps on-chip? |
|---|---|---|---|
| SigmanticAI APEX (tinyNPU) | One verified decoder layer, INT8 systolic GEMM, in-datapath INT4 KV | 0.56 tok/s (Qwen2.5-0.5B, measured) | No — DRAM streaming + host |
| TerEffic (arXiv 2502.16473) | Fully on-chip ternary weights | 16,300 tok/s (370M model) | Yes |
| LUT-LLM (arXiv 2511.06174) | Table-lookup instead of arithmetic, vector-quantized | First 1B+ model on FPGA without arithmetic compute | Yes (memory-based compute) |
| KV260 Taalas-style build | 3.16M-param INT4 transformer fully resident | 59,965 tok/s on a $250 board | Yes |
| ternfpga / Arty A7-35T | Multiply-free ternary engine, energy-first | ~1.6 J/token, 1,423 MB/s sustained | Partly — 0.7B capped near 8 tok/s |
| Apex Compute (name collision) | Commercial Unified Engine prototype | 15.63 tok/s (Gemma 3 1B), vendor-claimed | Unclear — prototype claims only |
| Design Conductor 2.0 (arXiv 2605.05170) | Agent-built TurboQuant KV accelerator (VerTQ) | 240-cycle pipeline, 125 MHz, 5.7 mm² TSMC 16FF | Design, not a running LLM |

That last row is the one that reframes the whole question. If an autonomous multi-agent harness can architect, implement, verify, timing-optimize and FPGA-map a KV-compression accelerator in roughly 80 hours, then "we built an accelerator" is no longer a differentiated claim in 2026. What remains scarce is an open, reproducible, bit-exact evidence trail — which is exactly what APEX is selling. Its differentiated claim is not the architecture. It is the receipt.

For market context, the FPGA market itself is growing but modest: Mordor Intelligence puts 2026 at USD 11.02 billion at a 9.35% CAGR to 2031, The Business Research Company has 2026 at USD 10.83 billion, and MarketsandMarkets runs USD 11.73 billion (2025) to USD 19.34 billion by 2030 at 10.5%. The AI-FPGA sub-segment is smaller and faster — USD 2.00 billion in 2025, USD 2.10 billion in 2026, heading to USD 8.50 billion by 2034 at 17.4%. Edge AI overall runs from USD 24.9 billion (2025) to USD 30.0 billion (2026) and USD 118.7 billion by 2033 at 21.7%. One gap worth stating plainly: no source I could verify gives a 2026 figure for FPGA share of LLM inference specifically. That number is not separately reported, and anyone quoting one is extrapolating.

## Honest Limitations, as Published by the Project Itself

Most projects bury this section. APEX publishes it. The known quality limits are:

- **CQ-8 worst end-to-end error** of 3.5e-01 against the value scale.
- **CQ-4 is documented as out of quality budget** on outlier-bearing data — end-to-end absolute error of 1.421e-01, which is 7.1% of the value scale. This is the stated reason the TIP tier-select unit exists.
- **24 documented limitations** in TRACEABILITY.md, indexed L-T1 through L-S3.

Add the caveats the repository does not get to choose: the codec method is prior art (KIVI, KVQuant), hardware-native KV compression predates it (Titanus, Kelle), the whole artifact is built with the vendor's own verification tooling, and the headline throughput number was still being corrected in the final three commits before last push — reference image first, then fastest, then confirmed on two builds.

## Reproduce It Yourself in Three Commands

You do not have to take any of this on faith, and that is the strongest thing about the project. Three checks, in ascending cost:

1. **`make -C golden test`** — validates the NumPy golden model locally, for free. If the golden model is wrong, everything downstream is wrong, so this is the right first check.
2. **The F2 walked demo** — the verified reference image (`agfi-030a812cd224b409d`) rebuilds the whole design in about **$2 and 30 minutes** on an `f2.6xlarge`, and a 193-check battery ran with zero failures before that README section was committed.
3. **The KV codec accuracy matrix** — the HellaSwag-based comparison across KVQ8, KVQ4 and KVQ4+ tiers.

One disclosure: I did not build the bitstream myself for this review. The "$2 and 30 minutes" figure and the F2 measurements are the team's, quoted from the repository, not independently reproduced here. Neither was the ECP5 build. If you need those verified, command two above is where to spend the money.

## Verdict: Who Should Read This Repo, and Who Should Not

**Read it if** you build RTL and want a working model of what verification-first development looks like at full scale — the mutation gates, the L1-to-L3 compositional rollup, the machine-generated status file, the silicon-versus-simulation differential that caught a toolchain bug. Read it if you work on KV-cache compression and want to see the codec moved into the datapath rather than bolted beside it. Read it if you are evaluating any FPGA inference vendor and need a calibrated sense of what "measured" should mean.

**Skip it if** you want a fast LLM on an FPGA. This is 0.56 tokens per second on a 0.5B model with the host in the loop, and the 7B numbers do not exist on silicon yet. If throughput is your goal, the fully on-chip family — TerEffic, the KV260 build — is the one to study, and if you need a product today, a GPU is still the answer.

The fair one-line verdict: APEX is not an inference accelerator you deploy, it is a verification artifact you learn from. Its 0.56 tok/s is published precisely because the project would rather be slow and provable than fast and unverifiable — and in a field where an agent harness can now generate accelerators faster than anyone can verify them, that inversion of priorities is the interesting part.

## FAQ

### What is the Apex Inference Chip, and is it a real chip?

It is not a chip. APEX (also called tinyNPU) is an open-source Apache-2.0 RTL design from SigmanticAI implementing a single transformer decoder layer as a reusable tile. By explicit charter it has no DRAM controller, no PCIe block and no network-on-chip, so it cannot be dropped into a system as a standalone accelerator. It has been built and run on two real targets — a Lattice ECP5-85F using the open yosys/nextpnr flow, and an AWS F2 VU47P instance using Vivado — which makes it more than a simulation-only design, but less than a product.

### How fast is FPGA LLM inference on APEX?

0.56 tokens per second on the fastest measured image (A0 at 62.5 MHz, a steady 1.78 seconds per token on Qwen2.5-0.5B) and 0.25 tok/s on the reference image at 15.625 MHz. The full optimization ladder climbed 140x from a 0.004 tok/s host-driven baseline. Only 8.53% of per-token arithmetic happens inside the tile; the rest of the wall is host transport, at 24 executor invocations per token of roughly half a second each. The tile's own walk window is about 36 ms.

### Has the 7B model actually run on the APEX FPGA?

No. Qwen2.5-0.5B is the FPGA-measured model. Qwen2.5-7B has run only through the software-verified golden pipeline and has never executed on silicon. The much-quoted 7B figures — reading-speed generation at roughly 3 W with 32k–64k context held flat by KV compression, and 5–10x lower energy per token than a desktop GPU — are projected from a calibrated analytic model and depend on three unbuilt pieces: the native-W4 weight path, the hardware layer walker, and a wide LPDDR interface.

### What makes APEX different from other FPGA LLM projects?

Verification discipline, not throughput. The verification surface is roughly twice the RTL surface — 27,760 lines of SystemVerilog testbenches plus 21,043 lines of Python against about 22,000 lines of RTL. Testbenches are mutation-tested so a surviving mutant fails the build; SiLU is checked over 65,536 patterns bit-exact; the W4B feeder runs a 4,063,104-point operand sweep; and a full-layer replay passed 28 cases across 152,883 checks. The KV codec method itself is prior art from KIVI and KVQuant, and hardware KV compression predates it in Titanus and Kelle — the claim is the integrated, verified implementation.

### Can I reproduce the Apex Inference Chip results myself?

Yes, at three levels of cost. `make -C golden test` validates the NumPy golden model locally for free. The pre-built AWS F2 reference image (`agfi-030a812cd224b409d`) rebuilds the full design in about $2 and 30 minutes on an f2.6xlarge, with the repository reporting a 193-check battery at zero failures. The KV codec accuracy matrix on HellaSwag is the third check. Note that this review did not independently rebuild the bitstream — the cost and timing figures are the project's own, taken from the committed README and status files rather than reproduced here.
