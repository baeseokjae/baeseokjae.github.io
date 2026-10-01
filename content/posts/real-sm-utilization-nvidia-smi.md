---
title: "Real SM Utilization for NVIDIA: When nvidia-smi Lies"
date: 2026-10-01T01:23:38+00:00
tags:
  - NVIDIA SM utilization
  - nvidia-smi GPU utilization misleading
  - DCGM_FI_PROF_SM_ACTIVE
  - DCGM_FI_PROF_SM_OCCUPANCY
  - tensor core utilization metric
  - GPU utilization 100% but low throughput
  - SM activity vs SM occupancy
  - MIG GPU utilization monitoring per instance
draft: false
cover:
  image: "/images/real-sm-utilization-nvidia-smi.png"
  alt: "Real SM Utilization for NVIDIA: When nvidia-smi Lies"
  relative: false
schema: "schema-real-sm-utilization-nvidia-smi"
---

**nvidia-smi's GPU-Util is a duty cycle, not a measure of work.** It reports the percentage of the last sample window during which at least one kernel was running — nothing about how many of the GPU's streaming multiprocessors were busy, how full they were, or whether the Tensor Cores did anything. Real NVIDIA SM utilization comes from DCGM's profiling fields: `DCGM_FI_PROF_SM_ACTIVE` (breadth), `DCGM_FI_PROF_SM_OCCUPANCY` (depth), `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` (the work you pay for) and `DCGM_FI_PROF_DRAM_ACTIVE` (the bottleneck). Two of those four are commented out of dcgm-exporter's default counter file.

That is the whole argument, and the rest of this guide is about proving it, measuring around it, and knowing which number to put in front of a capacity decision.

The short version of why this matters: a single-thread kernel that occupies one SM of an H100's 132 reports 100% utilization. An H100 running vLLM in autoregressive decode can report 91% GPU-Util while doing productive arithmetic at 0.11% to 12.5% of its BF16 ceiling. And on an H100 inference pod measured in the wild, `DCGM_FI_DEV_GPU_UTIL` reads 100 while `PROF_SM_ACTIVE` reads 0.18, `PROF_SM_OCCUPANCY` reads 0.11, `PROF_PIPE_TENSOR_ACTIVE` reads 0.04 and `PROF_DRAM_ACTIVE` reads 0.71 — the unmistakable signature of a memory-bandwidth-bound workload with near-idle tensor cores ([devopsbeast](https://devopsbeast.com/blog/dcgm-prometheus-gpu-observability)).

## What Does nvidia-smi's GPU-Util Actually Measure?

NVIDIA documents it in one sentence. `utilization.gpu` is the "percent of time over the past sample period during which one or more kernels was executing on the GPU. The sample period may be between 1 second and 1/6 second depending on the product" ([NVIDIA nvidia-smi documentation](https://docs.nvidia.com/deploy/nvidia-smi/)). The NVML API says the same thing about `nvmlUtilization_t.gpu`: a binary busy/not-busy flag averaged over time.

Read that definition carefully, because it contains three limits that never go away:

- **"one or more kernels"** — one kernel or ten thousand kernels produce the same 100%. The metric cannot see how many SMs were involved.
- **"was executing"** — a kernel counts as executing whether it is doing useful math or stalled on memory. The flag is set when the work is resident, not when it is progressing.
- **"the past sample period"** — the window is 1 second to 1/6 second, depending on the product. Short kernels can vanish entirely between samples or be smeared across them.

There is no FLOP term, no byte term, no SM term, and no Tensor Core term anywhere in the definition. GPU-Util answers exactly one question — "did anything run?" — and answers it about an interval, not about an instant.

The same is true of the sibling column. In `nvidia-smi dmon`, the `sm` value in the `u` group is *not* the GPU-Util column: it is the percentage of time at least one SM was busy, which is a somewhat better proxy but still says nothing about occupancy or Tensor Core usage ([syseng.io](https://syseng.io/blog/hpc-gpu-utilization-myth)).

## The One-Thread Experiment That Proves the Metric Lies

You do not need a hypothesis. You need twenty seconds and a kernel with `gridDim=1, blockDim=1`.

NVIDIA's own developer forums record the canonical result: a kernel launched with a single thread on a single SM makes nvidia-smi print GPU-Util 100% on a Tesla V100, while the remaining SMs sit completely idle ([NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/some-questions-on-gpu-utilization/191025)). The ETH EASL systems group reproduced the same behaviour with a stronger twist: a single thread block drives nvidia-smi and NVML utilization to at or near 100%, yet running *two instances of the same kernel simultaneously takes the same wall-clock time* — proving the GPU had spare capacity while reporting full utilization ([ETH EASL gpu-util-interference](https://github.com/eth-easl/gpu-util-interference/blob/af1fa502/pitfalls/pitfall_nvidia_smi/README.md)).

On an H100 with 132 SMs, the arithmetic is blunt: one busy SM out of 132 is 0.76% of the machine. The published reproduction of this experiment shows GPU_UTIL at 100%, SM Active at 0.76% — exactly 1/132 — Tensor at roughly zero, MFU near zero, and zero tokens per second generated ([dev.to](https://dev.to/alialp/your-gpus-are-lying-to-you-the-brutal-economics-of-ai-on-kubernetes-id6)).

The same arithmetic explains the metric's blindness in the other direction, stated most cleanly by the syseng.io analysis: a kernel using 5% of SMs for 100% of the time reports 100%; a kernel using 100% of the SMs for 50% of the time reports 50%. The metric sorts those two cases backwards relative to how much of the machine each one uses.

For reference, the SM counts that make these ratios concrete:

| GPU | Streaming multiprocessors |
|---|---|
| H100 SXM / NVL | 132 |
| A100 | 108 |
| RTX 4090 | 128 |

Sources: [packet.ai](https://packet.ai/blog/gpu-utilization-the-lie-your-dashboard-tells), with the H100 count corroborated in arXiv:2609.12923.

## SM Utilization vs SM Activity vs SM Occupancy: Getting the Terms Right

Three different quantities get called "SM utilization" in the same meeting, and confusing them produces the wrong fix.

| Term | What it counts | Where it comes from |
|---|---|---|
| SM activity | Fraction of time at least one warp was active on an SM, averaged over all SMs | `DCGM_FI_PROF_SM_ACTIVE` (field 1002), Nsight Systems SM Active |
| SM occupancy | Warps resident on an SM relative to the theoretical maximum warps per cycle | `DCGM_FI_PROF_SM_OCCUPANCY` (field 1003), Nsight Compute achieved occupancy |
| SM "utilization" as most tools report it | Elapsed-cycle pipeline throughput, maxed over SM sub-pipelines | Nsight Compute `sm__throughput.avg.pct_of_peak_sustained_elapsed` |

NVIDIA's DCGM profiling documentation defines `PROF_SM_ACTIVE` as the ratio of cycles an SM has at least one warp assigned, computed from the number of cycles and elapsed cycles ([DCGM Field Identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-api/dcgm-api-field-ids.html)). `PROF_SM_OCCUPANCY` is the ratio of warps resident on an SM to the theoretical maximum warps per elapsed cycle. Two caveats are documented explicitly and both are load-bearing:

- **"Active" does not mean "computing."** Warps stalled waiting on memory requests are still counted as active, so SM activity alone cannot tell a compute-bound kernel from a memory-bound one ([DCGM profiling module docs](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html)).
- **SM activity is insensitive to threads-per-block.** A kernel using N blocks for the whole interval, N/5 blocks for the whole interval, and N blocks for one fifth of the interval all report the same 0.2. Disambiguating how *full* the SMs are requires PROF_SM_OCCUPANCY.

"Occupancy" itself is a two-denominator word, and the two denominators differ by roughly 5x. The architectural limit is 64 warps per SM; the kernel's own resource cap is typically 8–12 warps per SM. In the KTH analysis of Hopper inference, FlashAttention-3's main kernel runs at 7.6 warps/SM — which is 12% of the architectural limit but 95% of its resource cap ([arXiv:2609.12923](https://arxiv.org/abs/2609.12923)). Two engineers can look at the same kernel and one says "occupancy is only 12%" while the other says "occupancy is near saturation." Both are right. Always state the denominator before drawing a conclusion from the number.

And the third term is the trap in plain sight: Nsight Compute's `sm__throughput.avg.pct_of_peak_sustained_elapsed` is a pipeline-throughput proxy over elapsed cycles — the maximum over SM sub-pipelines, assuming ideal SMSP load balance. It is *not* `sm__cycles_active` ("≥1 warp resident") and it is not an occupancy counter, despite being labelled "SM utilization" on most dashboards ([NVIDIA Nsight Compute Compute Triage Guide](https://docs.nvidia.com/nsight-compute/ComputeTriage/)).

## The Metric Ladder: Five Numbers, Least to Most Honest

If you remember one table from this article, make it this one. It ranks GPU metrics from the one that lies most convincingly to the one that survives scrutiny.

| Metric | Question it answers | Honesty |
|---|---|---|
| `DCGM_FI_DEV_GPU_UTIL` | Was a kernel resident at some point in this window? | The liar — a duty cycle |
| `DCGM_FI_PROF_GR_ENGINE_ACTIVE` | Was the graphics/compute engine active? | Higher precision than GPU_UTIL, works on MIG |
| `DCGM_FI_PROF_SM_ACTIVE` | How many SMs had at least one live warp? (breadth) | Honest about the machine, blind to batching |
| `DCGM_FI_PROF_SM_OCCUPANCY` | How full are the warp slots? (depth) | Honest, needs a stated denominator |
| `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` | Are the Tensor Cores firing? (the money metric) | The one procurement should see |
| `DCGM_FI_PROF_DRAM_ACTIVE` | Is HBM the wall? (the bottleneck) | Names the ceiling |
| MFU from measured throughput | Useful FLOPs over peak FLOPs | The number that survives scrutiny |

NVIDIA's own position, stated in [DCGM issue #64](https://github.com/NVIDIA/DCGM/issues/64), is that `DCGM_FI_DEV_GPU_UTIL` is roughly equal to `DCGM_FI_PROF_GR_ENGINE_ACTIVE`, that GR_ENGINE_ACTIVE is higher-precision and works on MIG, that `DCGM_FI_DEV_MEM_COPY_UTIL` should be avoided (CUDA kernel-based copies bypass the copy engine, and it does not work on MIG), and that `DCGM_FI_PROF_DRAM_ACTIVE` is the accurate DRAM bandwidth metric.

One more honest counter from the same analysis applies to every row of that table: the KTH team validated against a real workload and found the raw NVML GPM SM utilization and SM occupancy counters differ from Nsight Compute reference values by 28.35 and 8.74 percentage points respectively, improving to 2.31 and 0.95 percentage points after post-processing — and they report NVIDIA's documentation is inaccurate in places ([RWTH Aachen](https://publications.rwth-aachen.de/record/1035634/files/1035634.pdf)). Every "true" metric here is still a proxy. Choose the proxy whose failure mode you understand.

## The Metrics That Tell the Truth: DCGM Field IDs and Copy-Paste Commands

DCGM's profiling fields are the practical answer for live monitoring. The four you need, with their canonical field IDs:

| Field ID | Name | Meaning |
|---|---|---|
| 1002 | `DCGM_FI_PROF_SM_ACTIVE` | Ratio of cycles an SM has ≥1 warp assigned, averaged over all SMs |
| 1003 | `DCGM_FI_PROF_SM_OCCUPANCY` | Ratio of resident warps to theoretical maximum warps per elapsed cycle |
| 1004 | `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` | Tensor pipe activity — is real matmul work happening |
| 1005 | `DCGM_FI_PROF_DRAM_ACTIVE` | DRAM activity — is HBM the ceiling |

Read them live with a single command:

```bash
dcgmi dmon -e 1002,1003,1004,1005 -c 10 -d 1000
```

That samples all four fields ten times at one-second intervals. The `-c` and `-d` flags matter: keep the duration short and the interval explicit, because DCGM profiling carries a small sampling overhead and on older GPUs some field groups cannot be collected concurrently. Before you build a dashboard on a field, verify it is co-collectable with `dcgmi profile -l -i 0`, which lists which fields can be watched together without extra replay passes ([DCGM profiling docs](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html)).

For a broader first look that includes clocks, power and memory controller state:

```bash
nvidia-smi dmon -s pucvmet -d 1
```

This gives power, GPU temperature, SM utilization, memory utilization, encoder, decoder, memory clock and processor clock in one stream. The `sm` column here is the percentage of time at least one SM was busy — better than GPU-Util, still silent on occupancy and Tensor Cores.

And for a read-only quick check of the lying metric itself, so you can quote both numbers side by side:

```bash
nvidia-smi --query-gpu=utilization.gpu,utilization.memory --format=csv,noheader,nounits -l 2
```

Two warnings before you run any of this in production. DCGM profiling fields are ratios of active cycles, are not available on every GPU, require the profiling module loaded and sufficient privileges, and on Ampere-and-older hardware some field groups cannot be watched concurrently because DCGM multiplexes with statistical sampling. A blank or errored field means "verify GPU support," not "the GPU is idle" ([netdata.cloud](https://netdata.cloud/guides/nvidia-gpu/nvidia-gpu-memory-bandwidth-bound)).

## Step 1 — Read SM Activity and SM Occupancy Together

These two numbers are only meaningful as a pair, because they fail in opposite directions.

`SM_ACTIVE` is breadth: how much of the machine had something resident. `SM_OCCUPANCY` is depth: how full each SM's warp slots were. A workload can be broad and shallow (every SM has one lonely warp — typically a latency-bound or memory-stalled kernel) or narrow and deep (one SM packed with warps — typically a poorly parallelised kernel or a serial section).

NVIDIA publishes thresholds for the breadth number, and they are the most useful rules of thumb in the whole stack: **an SM activity of 0.8 or greater is necessary but not sufficient for effective GPU use, and a value below 0.5 likely indicates ineffective GPU usage** ([DCGM profiling docs](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html)).

The "necessary but not sufficient" phrasing is the point. Two kernels can post identical SM activity of 0.2 and be completely different situations — and here is the demonstration NVIDIA itself uses: a kernel using N blocks for the whole interval, N/5 blocks for the whole interval, and N blocks for one fifth of the interval all report the same 0.2. Breadth alone cannot separate "using a fifth of the machine continuously" from "using the whole machine a fifth of the time." Only occupancy plus a look at the timeline separates them.

The practical read:

| SM_ACTIVE | SM_OCCUPANCY | Likely diagnosis |
|---|---|---|
| ≥ 0.8 | healthy for the kernel's resource cap | The SMs have work; check whether the work is the right kind (Step 2) |
| ≥ 0.8 | very low | Broad but shallow — latency-bound, memory-stalled, or tiny blocks |
| < 0.5 | any | Ineffective GPU usage per NVIDIA's own threshold — and note this can coexist with GPU-Util at 100% |
| ~1/132, ~1/108 or ~1/128 | near zero | The one-thread case: something is running, nothing is being computed |

And remember the semantic that makes these numbers less flattering than they look: warps stalled on memory are counted as active. High SM activity does not mean high throughput. The KTH team measured a case where batching improved throughput 50x while SM activity moved only from 54.59% to 62.07% ([dev.to](https://dev.to/alialp/your-gpus-are-lying-to-you-the-brutal-economics-of-ai-on-kubernetes-id6)).

## Step 2 — Check Tensor Core Activity: The Metric You Actually Pay For

Tensor Core utilization is the closest thing to an invoice in this whole article. If you bought an H100 for its BF16 matmul throughput and `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` is near zero, you are paying H100 prices for a GPU behaving like a memory device.

A sustained low Tensor Pipe Active value on a matmul-heavy workload is the smoking gun for one of two things: FP32 arithmetic where BF16/FP16 (with autocast) was intended, or custom kernels that never target the Tensor Cores at all. Both are fixable in the kernel or the dtype, not with hardware.

Context for what "low" means in production: the H100 inference pod example reads `PIPE_TENSOR_ACTIVE` at 0.04 while GPU-Util says 100. The batch-1 vLLM 7B measurement reads Tensor Active at 1.62% with GPU-Util at 90%. Move to batch-64 and Tensor Active rises to 11.18% — still low, but MFU rises from 0.23% to 11.6% and throughput from 148 to 7,485 tokens per second ([dev.to](https://dev.to/alialp/your-gpus-are-lying-to-you-the-brutal-economics-of-ai-on-kubernetes-id6)).

Note the direction of the lie in that last comparison: GPU-Util *fell* from 90% to 85% while the machine produced 50x more useful work. If your autoscaler or your capacity review reads GPU-Util, it is being told that the batch-64 configuration is the less busy one.

## Step 3 — Check DRAM Activity to Name the Bottleneck

`DCGM_FI_PROF_DRAM_ACTIVE` tells you whether you are at the memory wall. It is a time-based activity ratio, not a bandwidth measurement — there is no NVML API that returns GB/s, only how much of the time DRAM was busy ([netdata.cloud](https://netdata.cloud/guides/nvidia-gpu/nvidia-gpu-memory-bandwidth-bound)).

On HBM parts with a fixed memory clock, multiplying the ratio by theoretical peak is a reasonable estimate. A DRAM-active ratio of 0.9 on an A100 80GB implies roughly 1.8 TB/s in flight against about 2 TB/s of theoretical HBM bandwidth. That is a GPU that is busy at its architectural ceiling, not one that is wasting itself.

This is where a lot of capacity mistakes get made. The memory-bound signature is the *combination*, never the single metric: DRAM active high (~0.9) while SM active and Tensor active sit low, with GPU-Util still reading 100%. Teams that read the utilization percentage alone see "the GPU is maxed out, buy more GPUs" when the correct reading is "the algorithm is at the roofline, change the algorithm."

The governing concept is arithmetic intensity — FLOPs per byte transferred. Elementwise operations, reductions, normalisation, unfused attention, embedding lookups and moderate-batch inference all live in the low-intensity regime. The roofline ridge points quantify how far: an A100 needs roughly 156 FLOP per byte to become compute-bound, and an H100 SXM roughly 295 ([The LLM Stack](https://prakashkagitha.github.io/llm-stack-book/04-kernels-efficiency/01-roofline-performance.html)). Batch-1 autoregressive decode uses each weight byte exactly once, which is why it cannot get anywhere near that ratio no matter how the kernels are written.

## Classifying the Four States: Compute-Bound, Memory-Bound, Starved and Padded

Plot Tensor Active against DRAM Active on the same graph and you get a 30-second triage that covers most real incidents:

| Tensor Active | DRAM Active | Diagnosis | First fix to try |
|---|---|---|---|
| High | Moderate | Compute-bound — this is what you bought | Optimise the kernel; consider sparsity or lower precision |
| Low | High (~0.9) | Memory-bandwidth-bound — at the architectural ceiling | Batching, quantisation, KV-cache placement, fused kernels |
| Low | Low, GPU_UTIL 100% | Stall — launch overhead or host/CPU starvation | Nsight Systems timeline; fix the dataloader or the launch pattern |
| Low | Low, GPU_UTIL low | Genuinely idle or waiting | Check the pipeline and the scheduler before the GPU |

Two lookalikes must be ruled out before you accept the "starved" verdict, because both masquerade as idle silicon. **HBM thermal throttling** looks like a busy GPU doing less work: check `temperature.memory` against its max and `clocks.current.memory` against its max. **Host starvation** looks like a starved GPU and is caused by the CPU or the PCIe path: low SM *and* low DRAM, bursty PCIe counters, high host CPU.

A third case deserves its own row but usually gets misclassified as "broken." That is the padded case: on Hopper, BF16 GMMA executes in fixed 64-row fragments, so small-batch decode fills a tiny fraction of each fragment with real token rows while the hardware charges the full fragment as utilisation. Usefulness, not activity, is what is missing — see the MFU section below.

## Prefill vs Decode: Why the Same GPU Shows Opposite Profiles

The single most useful framing for LLM serving: one model, two resource profiles, and they are opposites.

| Phase | SM activity measured (H100 NVL, vLLM) | Why |
|---|---|---|
| Cold prefill | 73–97%, mean 92% | Large tile sizes, heavy matmul, high arithmetic intensity |
| Warm prefill with prefix-cache hits | 8–11% at small token counts, mean 33% | cuBLASLt switches to smaller thread-block tiles |
| Autoregressive decode | 0.11%–12.5% of the 835 TFLOP/s dense BF16 ceiling, while the dashboard reads 91% | Fixed 64-row GMMA fragments with mostly zero-padded rows |

All three rows are from arXiv:2609.12923, a profiling study of vLLM with FlashAttention-3 and cuBLASLt on an H100 NVL across four production models ([arXiv:2609.12923](https://arxiv.org/abs/2609.12923)).

The physics behind the decode row is worth restating because it kills the most common misdiagnosis. Decoding one token means reading the entire weight matrix — about 15 GB for a 7B model in BF16 — to do roughly 15.2 GFLOP of arithmetic. At 2.2 TB/s, reading those weights takes about 6.8 ms; the math takes about 15 microseconds. Decode is a memory problem wearing a compute costume, which is why "buy a bigger GPU" so often fails to improve it, and why the fixes that work are batching, quantisation and KV-cache placement.

The study's recommendation follows directly: replace `sm_busy_pct` in your dashboards with useful-FLOP efficiency and HBM bandwidth saturation (Nsight Compute's `dram__bytes.sum.per_second` against 3.9 TB/s on H100).

## The Default-Config Trap: Why Your Dashboard Cannot See SM_ACTIVE

This one has an unusually clean failure mode, and it is worth checking today rather than after the next incident.

In dcgm-exporter's shipped default counter set (`etc/default-counters.csv`), **`DCGM_FI_PROF_SM_ACTIVE` and `DCGM_FI_PROF_SM_OCCUPANCY` are commented out** — the lines are prefixed with `#` — while `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` and `DCGM_FI_PROF_DRAM_ACTIVE` are enabled ([verified directly from NVIDIA/dcgm-exporter](https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/etc/default-counters.csv)). A default install therefore cannot see real SM utilization until the counters file is edited, no matter how good the dashboard is.

The operational consequence is worse than a missing metric. Many teams believe they monitor SM efficiency and in fact never enabled it. The series is simply absent — and a missing series graphs as silence, not as zero. Nobody gets paged by a gap in a line that was never drawn.

The fix is one line in the counters file, then a restart:

```
# DCGM_FI_PROF_SM_ACTIVE and DCGM_FI_PROF_SM_OCCUPANCY: remove the leading '#' in etc/default-counters.csv
```

Two follow-ups while you are in there. First, expect a small sampling overhead and confirm the fields are co-collectable on your hardware with `dcgmi profile -l -i 0`. Second, expect `DCGM_FI_PROF_SM_ACTIVE` on MIG instances to occasionally read *above* 1.0 — the DCGM issue tracker has an open report of SMACT showing ~1.29 (129%) on a MIG device, with tensor activity showing the same overshoot ([NVIDIA/DCGM issue #152](https://github.com/NVIDIA/DCGM/issues/152)). MIG per-instance PROF values need care before being plotted as percentages.

## No DCGM Allowed? NVML GPM on Driver v520 or Newer

Plenty of environments cannot run DCGM at all: managed training containers, restricted Kubernetes pods without `CAP_SYS_ADMIN`, platforms where the profiling module is simply unavailable. For those, NVML v520+ added GPU Performance Monitoring (GPM) metrics that expose DCGM-like signals through the NVML driver interface — SM utilization, SM occupancy, tensor and memory-bandwidth signals — with no DCGM service required.

The enums you will actually use:

| Enum | Meaning |
|---|---|
| `NVML_GPM_METRIC_GRAPHICS_UTIL` (1) | Graphics engine utilisation |
| `NVML_GPM_METRIC_SM_UTIL` (2) | "Percentage of SMs that were busy" |
| `NVML_GPM_METRIC_SM_OCCUPANCY` (3) | SM occupancy |
| SM cycles active (249) / MMA (250) / HMMA (252) / FP32 (259) / FP16 (260) | Per-pipe `*_CYCLES_ACTIVE` counters |

Enum values and field IDs are from the [NVML API reference](https://docs.nvidia.com/deploy/nvml-api/group__nvmlGpmEnums.html).

The honest caveat comes from the group that validated them: the RWTH Aachen study checked NVML GPM against Nsight Compute over four weeks of job data plus targeted benchmarks and found raw SM utilization and SM occupancy differing from the reference by 28.35 and 8.74 percentage points, improving to 2.31 and 0.95 percentage points after post-processing ([RWTH Aachen](https://publications.rwth-aachen.de/record/1035634/files/1035634.pdf)). GPM is a genuinely useful escape hatch for locked-down containers, but treat the raw counters as inputs to a corrected calculation, not as truth.

## Going Per-Kernel with Nsight Compute (and the sm__throughput Trap)

Once the four-quadrant read tells you what to look for, go per-kernel. Nsight Compute is the right tool and `sm__throughput.avg.pct_of_peak_sustained_elapsed` is the wrong headline, for the reasons established earlier: it is elapsed-cycle pipeline throughput with ideal load-balance assumed, it charges zero-padded tensor cycles as real work, and it is not an occupancy counter.

Two calibrations from NVIDIA's own triage guide are worth having in the room: values below roughly 60% sit in the low/latency-risk regime, above roughly 80% in the high/near-limit regime, and any `pct_of_peak_sustained_*` significantly above 100% or negative must be treated as untrustworthy because of multi-pass replay inaccuracy ([Nsight Compute Compute Triage Guide](https://docs.nvidia.com/nsight-compute/ComputeTriage/)).

The metric to prefer for the "is my expensive silicon doing useful work" question is useful-FLOP efficiency: FLOPs applied to non-padded token rows divided by peak. That is the number that survives scrutiny, and on H100 decode it lands between 0.11% and 12.5% against a dashboard reading of 91%.

## MIG and Multi-Tenant Traps: When GPU-Level Metrics Are Actively Wrong

On MIG-enabled GPUs, the problem stops being precision and becomes correctness. nvidia-smi reports at the physical-GPU level while workloads run inside instances, so a GPU-level utilisation number describes the wrong entity entirely when tenants run in MIG instances. Worse, on MIG-enabled GPUs the standard NVML/nvidia-smi path does not currently support querying encoder, decoder, jpeg, ofa, gpu and memory utilization at all ([nvidia-smi documentation](https://docs.nvidia.com/deploy/nvidia-smi/)).

The A100's partitioning explains the naming and the arithmetic: an A100 has 7 compute (SM) slices and 8 memory slices, which is why MIG profiles are named `{compute}g.{memory}gb` ([whatap.io](https://whatap.io/en/blog/mig-gpu-usage-monitoring)).

What to do instead:

- Reconstruct per-instance utilisation as the sum of each instance's `DCGM_FI_PROF_GR_ENGINE_ACTIVE` multiplied by its compute-slice ratio on a 7-slice device.
- Attribute metrics with the `GPU_I_ID` and `GPU_I_PROFILE` labels, or per-tenant cost attribution is not meaningful.
- Sanity-check any per-instance PROF value above 1.0 rather than plotting it as a percentage.

Per-process attribution on non-MIG hardware has its own documented limit: NVIDIA support states that process utilization is calculated only for a single running process on the GPU and is not supported for concurrent running processes ([NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/questions-on-per-process-gpu-utilization/265460/1)). If several processes share a card, per-process utilisation numbers are not a basis for chargeback.

## Reading the Numbers in Dollars: Utilization vs MFU

MFU is where the conversation leaves metric plumbing and becomes a business number.

**MFU = (model FLOPs per step × steps per second) / (peak FLOPs of the GPU × number of GPUs)**, where model FLOPs per step for a dense transformer is about 6 × parameters × tokens, using the dense peak rather than the "with sparsity" figure ([CoreWeave](https://docs.coreweave.com/products/sunk/optimize_workloads/measuring-mfu-and-job-performance)).

Calibrate against reported reality before declaring anything broken. GPT-3 175B on V100 reached 21.3% MFU; Megatron-Turing NLG 530B on 2,240 A100s reached 30.2%; PaLM 540B on 6,144 TPU v4 reached 46.2%; Llama 3 405B on 8,192–16,384 H100s reached 38–43% in BF16. Most LLM training runs land at 35–45%, including frontier-scale runs — so a fleet sitting at 100% reported utilisation and 40% MFU is normal, not broken.

Typical bands by configuration help you spot a real problem:

| Configuration | Typical MFU |
|---|---|
| Well-optimised dense transformer, single GPU | 0.50–0.70 |
| Multi-GPU DDP, small model | 0.40–0.60 |
| Tensor parallel (Megatron-style) | 0.45–0.65 |
| Pipeline parallel | 0.30–0.50 |
| MoE training | 0.20–0.40 |

A dense transformer below 0.20 MFU almost always indicates a fixable bottleneck ([TechnoLynx](https://technolynx.com/post/model-flops-utilization-ai-training)).

Then price it. The published billed-hour breakdown for a batch-1 vLLM workload reads: `gpu_util_pct_avg 86.2`, `sm_active 57.9`, `tensor_active 6.8`, `mfu 5.89`, billed cost $4.42, cost that did work $0.26, cost of idle silicon $4.16 — an idle proportion of 94.1%. The same card at batch-64 produced roughly 50x the tokens at a *lower* utilization reading ([dev.to](https://dev.to/alialp/your-gpus-are-lying-to-you-the-brutal-economics-of-ai-on-kubernetes-id6)).

Fleet-level numbers say the same thing at scale. Average enterprise GPU utilisation is around 5% across 23,000 production clusters, and only about 7% of teams achieve above 85% utilisation — idle most of the time, and inefficient when busy ([gpuaas.com](https://gpuaas.com/blog/gpu-utilization-misleading-metric-2026)). A study of 118,276 jobs on Perlmutter at NERSC, joining DCGM telemetry sampled every ten seconds to scheduler records, found mean peak GPU utilisation of 71.77% but mean peak GPU *memory* utilisation of only 28.64%, with 37.12% of jobs never exceeding 15% memory utilisation ([optops.ai](https://optops.ai/resources/blogs/gpu-utilization-metrics-dcgm-mig)).

For contrast on what is achievable when someone actually instruments this: NVIDIA's own engineering teams joined real-time DCGM telemetry with Slurm job metadata to build a per-job GPU idle-waste metric and reported reducing GPU waste from roughly 5.5% to about 1% on internal research clusters. That is one organisation's internal result and not an industry benchmark, but it demonstrates the size of the prize that becomes visible only after you stop reading the duty-cycle number.

## Prometheus and Grafana: Queries and Alerts Worth Wiring Up

Two alert expressions cover most of the value, and neither pages someone for a busy GPU.

The first is the procurement-ticket detector — a GPU that reports very high utilisation while the Tensor Cores are effectively silent:

```promql
DCGM_FI_DEV_GPU_UTIL > 90
and on(gpu, Hostname) DCGM_FI_PROF_PIPE_TENSOR_ACTIVE < 0.1
```

Sustained, this means you are paying compute prices for memory-bound or stalled work. It should open a ticket about batching, precision or the dataloader — not a purchase order.

The second is the breadth alert that catches the dataloader-bound training loop:

```promql
DCGM_FI_DEV_GPU_UTIL > 90
and on(gpu, Hostname) DCGM_FI_PROF_SM_ACTIVE < 0.3
```

A healthy dense-matmul training step sits at 70–90% occupancy. A dataloader-bound step shows occupancy in single digits while utilisation reads 100%, because a small fetch/decode kernel keeps the busy flag set while the real matmul and attention kernels wait on data ([syseng.io](https://syseng.io/blog/hpc-gpu-utilization-myth)).

Both queries depend on the PROF series actually existing — see the default-config trap above. If the series is missing, `and on(...)` matches nothing, the alert never fires, and the dashboard looks clean.

One more pattern worth graphing rather than alerting on: host-to-device copies run on dedicated copy engines, not SMs, so `utilization.gpu` reads 0% during a transfer, while `utilization.memory` measures the memory controller rather than the copy engine and can also stay low. A dataloader-bound training loop therefore shows a sawtooth, not a plateau ([netdata.cloud](https://netdata.cloud/guides/nvidia-gpu/nvidia-gpu-low-utilization-data-starvation)). The sawtooth is the diagnosis, and it is invisible on a one-minute average.

## What to Do When SM Activity Is Genuinely Low

Most of this article is about measuring correctly. This section is about the case where the honest metrics confirm the GPU is underused, because that is the case where teams reach for a hardware purchase they do not need.

Work down this list before adding silicon:

1. **Is DRAM_ACTIVE near 1.0 while SM_ACTIVE is modest?** Then you are memory-bandwidth-bound and at the architectural ceiling. No operational knob adds HBM bandwidth: raising SM clocks, raising the power limit, or running more GPUs with the same kernel shape does nothing. The fixes are algorithmic — larger batches, quantisation, KV-cache placement, fused kernels.
2. **Is Tensor Active low on a matmul-heavy workload?** Check the dtype and autocast path. FP32 where BF16 was intended, or custom kernels that never target Tensor Cores, produce exactly this signature and cost nothing to fix.
3. **Is SM_ACTIVE high but throughput low?** The warps are present and stalled. Go to Nsight Systems on a few iterations and look at the timeline rather than the counters.
4. **Is SM_ACTIVE low, DRAM low, GPU-Util 100% and PCIe bursty?** You are host-starved. Fix the dataloader, the input pipeline, or the launch pattern.
5. **Is temperature.memory near max with clocks.current.memory below max?** You are thermally throttled on HBM. This is a cooling and power problem, not a code problem.
6. **Is the workload MIG-partitioned?** Then validate per-instance attribution before concluding anything about efficiency.

Then verify the fix the honest way: re-measure MFU, not GPU-Util. A successful optimisation can *lower* the utilisation percentage while raising throughput, and if the dashboard is the acceptance criterion, you will reject good work.

## A 30-Second Triage Runbook

For the next time someone says the GPU is at 100% and the job is slow:

```bash
# 1. The lie, and the memory controller
nvidia-smi --query-gpu=utilization.gpu,utilization.memory --format=csv,noheader,nounits -l 2

# 2. The truth: breadth, depth, tensor work, DRAM
dcgmi dmon -e 1002,1003,1004,1005 -c 10 -d 1000

# 3. Confirm what can be co-collected on this GPU
dcgmi profile -l -i 0

# 4. Rule out thermal throttling and clock capping
nvidia-smi --query-gpu=clocks.current.memory,clocks.max.memory,temperature.memory,power.draw,power.limit --format=csv,noheader
```

Then classify with the four-quadrant table: tensor high and DRAM moderate is compute-bound; DRAM high and tensor low is memory-bound; both low with GPU-Util at 100% is a stall. If the answer is "the SMs are mostly idle but the number says 100," you have reproduced the one-thread illusion at production scale — and the fix is in the workload, not in the fleet.

Only after the quadrant tells you what to look for should you spend time in Nsight Compute. Utilisation is a tripwire, not a diagnosis; it is only discriminative at the extremes.

## DCGM Field-ID Reference Table (and the Common Mis-Mapping)

Field IDs are worth stating precisely, because a widely copied error is in circulation: several popular blog posts map 1004 to SM activity and 1005 to SM occupancy. The official DCGM field table disagrees.

| Field ID | Correct name | Commonly mislabelled as |
|---|---|---|
| 1002 | `DCGM_FI_PROF_SM_ACTIVE` | — |
| 1003 | `DCGM_FI_PROF_SM_OCCUPANCY` | — |
| 1004 | `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` | "SM activity" |
| 1005 | `DCGM_FI_PROF_DRAM_ACTIVE` | "SM occupancy" |
| — | `DCGM_FI_PROF_GR_ENGINE_ACTIVE` | — |

Copying those blog posts produces a mislabelled dashboard that looks entirely plausible: the graphs move, the panel titles are wrong, and the conclusions drawn from them are wrong in a way nobody notices until a capacity decision goes bad.

Sampling rates are the other practical limit. DCGM profiling metrics can be collected at up to 10 Hz; Nsight Systems GPU metrics (GR_ACTIVE, SM_ACTIVE) can be collected up to 200 kHz, though not sustainably on all GPUs ([NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/gpu-utilization/368787)). And if power draw is part of your diagnosis, know its blind spot: on A100 and H100, nvidia-smi reports the average of only the past 25 ms every 100 ms — meaning 75% of the runtime is not sampled at all, and the reported value can lag actual activity ([arXiv:2312.02741](https://arxiv.org/html/2312.02741)).

## FAQ

**What does "100% GPU utilization" in nvidia-smi actually mean?**

It means that at some point during the last sample window — between 1 second and 1/6 second, depending on the product — at least one kernel was executing on the GPU. It is a time-based duty cycle with no weighting for how much of the hardware the kernel used, how full the SMs were, or whether the Tensor Cores did any work. One thread looping on one SM of an H100's 132 is enough to produce a 100% reading.

**How do I measure real NVIDIA SM utilization?**

Enable and read `DCGM_FI_PROF_SM_ACTIVE` (field 1002) for breadth and `DCGM_FI_PROF_SM_OCCUPANCY` (1003) for depth, then add `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` (1004) and `DCGM_FI_PROF_DRAM_ACTIVE` (1005) to classify the bottleneck. A single command does all four: `dcgmi dmon -e 1002,1003,1004,1005 -c 10 -d 1000`. NVIDIA's threshold for SM activity is 0.8 or greater being necessary but not sufficient, and below 0.5 likely indicating ineffective GPU usage.

**Why is SM_ACTIVE missing from my DCGM Prometheus metrics?**

Because it ships disabled. In dcgm-exporter's `etc/default-counters.csv`, the `DCGM_FI_PROF_SM_ACTIVE` and `DCGM_FI_PROF_SM_OCCUPANCY` lines are commented out with a leading `#`, while the tensor and DRAM PROF counters are enabled. Remove the `#`, restart the exporter, and confirm with `dcgmi profile -l -i 0` that the fields are co-collectable on your GPU. Until then, the series is absent rather than zero, and a missing series fires no alerts.

**Is a GPU that reports 100% utilization with only 40% MFU broken?**

No — that is the normal state of large-scale training and of LLM inference. Reported large-scale pretraining MFU sits between 21.3% (GPT-3 175B on V100) and 46.2% (PaLM 540B on 6,144 TPU v4), with Llama 3 405B at 38–43% in BF16. A fleet reporting 100% utilisation at 40% MFU is working as designed; the utilisation number is simply not a measure of useful work. Sign off capacity decisions on MFU and on DRAM saturation, not on the duty cycle.

**Can I get SM utilization on MIG, or without DCGM installed?**

Both are possible but need care. On MIG, GPU-level metrics describe the wrong entity: reconstruct per-instance utilisation from each instance's `DCGM_FI_PROF_GR_ENGINE_ACTIVE` times its compute-slice ratio, and use the `GPU_I_ID` and `GPU_I_PROFILE` labels for attribution — noting that per-instance PROF values can read above 1.0. Without DCGM, NVML v520+ exposes GPM metrics (`NVML_GPM_METRIC_SM_UTIL`, `NVML_GPM_METRIC_SM_OCCUPANCY`) through the driver interface with no DCGM service and no `CAP_SYS_ADMIN`; raw values differ from Nsight Compute reference by tens of percentage points and need post-processing before they are trustworthy.

## The Short Version

nvidia-smi's GPU-Util is a duty cycle: did something run in the last window, yes or no. It cannot see breadth, depth, tensor work or bandwidth, and it is gameable by construction — anything that adds small kernels, a keep-alive kernel or non-overlapping streams raises the number without adding throughput. Stop asking "is the GPU busy" with one number and start asking three separate questions: how many SMs have a live warp (SM_ACTIVE), how full is each SM's warp slots (SM_OCCUPANCY), and are the units that cost money actually firing (PIPE_TENSOR_ACTIVE) — with DRAM_ACTIVE to name the ceiling. Fix the dcgm-exporter counters file, wire the two alert expressions, and put MFU in front of any capacity decision. The utilisation metric was never a lie about the hardware; it was an answer to a different question than the one everyone is asking it.
