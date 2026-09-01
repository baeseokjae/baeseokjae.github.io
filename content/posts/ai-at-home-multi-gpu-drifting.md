---
title: "Multi GPU Local Inference: How to Drift a Model Across Your Home GPUs"
date: 2026-09-01T04:01:49+00:00
tags:
  - multi-gpu
  - local inference
  - llama.cpp
  - vLLM
  - tensor parallel
  - pipeline parallel
  - home server
description: "Multi GPU local inference lets you run models that exceed one GPU's VRAM. Learn pipeline vs tensor parallel, llama.cpp and vLLM configs, and when it's worth it."
draft: false
cover:
  image: "/images/ai-at-home-multi-gpu-drifting.png"
  alt: "Multi GPU local inference: drifting a large model across multiple GPUs for home inference"
  relative: false
schema: "schema-ai-at-home-multi-gpu-drifting"
---

Multi GPU local inference means spreading a single large language model across two or more GPUs in your home server so you can run models that exceed the VRAM of any one card, or serve them faster. You do this by "drifting" the model's layers or tensors across your GPUs using either pipeline (layer) parallelism or tensor parallelism, configured through tools like llama.cpp and vLLM. The right strategy depends on your interconnect speed, your hardware mix, and whether your model architecture even supports the split.

## Why Run Local Inference Across Multiple GPUs

The single most common reason to run multi GPU local inference is VRAM capacity. A 70B-parameter model in 4-bit quantization needs roughly 40 GB of memory, which exceeds the 24 GB available on a single consumer RTX 4090 or RTX 3090. When your model does not fit in one GPU's VRAM, multi-GPU is the only way to run it locally without offloading to slow system RAM.

The second reason is throughput. Even when a model fits on one card, splitting it across multiple GPUs can increase tokens-per-second for concurrent requests, especially in a home server serving several users or agents at once. The official llama.cpp multi-GPU documentation lists exactly these two triggers: the model does not fit in a single GPU's VRAM, or you want more throughput.

There is also a growing hobbyist pull toward multi-GPU rigs. Projects like nanoslg, an educational multi-GPU LLM server claiming roughly 5x speedup, and LLMKube, which orchestrates local LLMs on Kubernetes with GPU acceleration, show that multi-GPU local inference is an active DIY space. The trend is moving from single-card experiments toward managed, containerized multi-GPU setups.

## How Multi-GPU Inference Works: Pipeline vs Tensor Parallelism

There are two fundamentally different ways to drift a model across GPUs, and they are not interchangeable.

**Pipeline (layer) parallelism** splits the model by layers. GPU 0 runs the first N layers, GPU 1 runs the next N, and so on. Each GPU holds a contiguous slice of the network, and activations flow from one GPU to the next in sequence. In llama.cpp this is the default and most compatible split mode, controlled with `--split-mode layer`. Because each GPU only needs to hold its own layers, pipeline parallelism is the natural choice when the goal is simply fitting a model that is too big for one card.

**Tensor parallelism** splits each individual layer's weight matrices across GPUs. All GPUs work on the same layer simultaneously, each computing a slice of the matrix multiplication, then exchanging partial results. This is faster per token because the work is parallelized within each layer, but it requires far more communication between GPUs and is much more sensitive to interconnect speed. In llama.cpp, tensor parallel is controlled with `--split-mode tensor` and `--tensor-split`, and it is explicitly marked experimental.

The practical difference matters for home rigs. Pipeline parallelism is forgiving of slow interconnects because GPUs only exchange activations once per layer boundary. Tensor parallelism exchanges data constantly within every layer, so it demands fast NVLink or at least high-bandwidth PCIe.

## Choosing Your Parallelism Strategy Based on Interconnect

Your interconnect is the single biggest factor in choosing between pipeline and tensor parallelism. The vLLM parallelism scaling documentation is explicit: for GPUs without NVLink interconnect, such as the L40S, prefer pipeline parallelism over tensor parallelism for higher throughput and lower communication overhead.

Here is a practical decision table for a home multi-GPU rig:

| Interconnect | Recommended strategy | Why |
|---|---|---|
| NVLink (e.g. RTX 3090/4090 pairs, A100/H100) | Tensor parallel | Low-latency high-bandwidth links make per-layer data exchange cheap |
| PCIe Gen 4/5, no NVLink (e.g. L40S, mixed consumer cards) | Pipeline (layer) parallel | Activations exchanged once per layer boundary; far less chatter |
| Mixed or unknown interconnect | Pipeline (layer) parallel | Default and most compatible; safest fallback |
| Multi-node (two separate machines) | Pipeline parallel + tensor parallel | Set tensor_parallel_size per node, pipeline_parallel_size to node count |

The rule of thumb: if your GPUs are not NVLink-connected, tensor parallelism will likely bottleneck on communication and deliver worse throughput than a well-tuned pipeline split. This is why vLLM's guidance for L40S-class hardware points away from tensor parallel.

## Setting Up Multi-GPU Inference with llama.cpp

llama.cpp supports four split modes: `none`, `layer` (pipeline, the default), `row` (deprecated), and `tensor` (experimental). For a home rig, you will almost always use `layer` or `tensor`.

The key command-line flags are:

- `--split-mode none|layer|row|tensor` — how to distribute the model
- `--tensor-split` — comma-separated fraction of work per GPU (e.g. `1,1` for two equal GPUs)
- `--main-gpu` — which GPU handles the main compute and output
- `--n-gpu-layers` — how many layers to offload to GPU (relevant when mixing GPU and CPU)
- `--device` — target a specific device
- `--flash-attn` — required for tensor parallel

A basic two-GPU pipeline split looks like:

```bash
llama-server -m model.gguf \
  --split-mode layer \
  --n-gpu-layers 99 \
  --flash-attn
```

For tensor parallel across two equal GPUs:

```bash
llama-server -m model.gguf \
  --split-mode tensor \
  --tensor-split 1,1 \
  --flash-attn
```

There are important constraints on tensor parallel in llama.cpp. It requires flash attention and a non-quantized KV cache (f32/f16/bf16); a quantized KV cache is not implemented for tensor split. It is also not implemented for MoE or hybrid architectures such as Grok, DeepSeek2, and Mistral4, nor for state-space models like Mamba and Mamba2. If you are running any of those, you must use layer (pipeline) splitting.

NCCL support in llama.cpp is selected at build time with `-DGGML_CUDA_NCCL=ON` (the default), and NCCL is not automatically distributed with CUDA, so you may need to install it separately for multi-GPU tensor parallel to work.

## Setting Up Multi-GPU Inference with vLLM

vLLM offers a more production-oriented path to multi GPU local inference. Its parallelism model is: single GPU, single-node multi-GPU tensor parallel, or multi-node tensor plus pipeline parallel.

The two settings that matter are `tensor_parallel_size` and `pipeline_parallel_size`. vLLM recommends setting `tensor_parallel_size` to the number of GPUs per node and `pipeline_parallel_size` to the number of nodes. For a single machine with four GPUs, that means:

```bash
vllm serve meta-llama/Llama-2-70B \
  --tensor-parallel-size 4 \
  --pipeline-parallel-size 1
```

For a two-node setup with four GPUs each:

```bash
vllm serve meta-llama/Llama-2-70B \
  --tensor-parallel-size 4 \
  --pipeline-parallel-size 2
```

vLLM uses Ray for multi-node inference and native Python multiprocessing for single-node inference by default. For a home server, the single-node multiprocessing path is simpler and avoids the overhead of a Ray cluster.

The practical takeaway from vLLM's guidance mirrors llama.cpp: for uneven GPU splits, use pipeline parallelism with `tensor_parallel_size=1`, and for GPUs without NVLink, prefer pipeline over tensor for throughput.

## Handling Uneven GPU Splits and Mixed Hardware

Home rigs rarely have identical GPUs. You might pair a 24 GB RTX 3090 with a 16 GB RTX 4080, or mix an older card with a newer one. Both llama.cpp and vLLM handle this, but differently.

In llama.cpp, `--tensor-split` lets you weight the work by GPU capacity. For a 24 GB and 16 GB pair, you might use `--tensor-split 3,2` to give the larger card more layers. In vLLM, the guidance is to use pipeline parallelism (`tensor_parallel_size=1`) for uneven splits, because tensor parallelism assumes roughly equal compute across GPUs and will stall on the slowest card.

Mixed hardware also changes your memory planning. The total usable VRAM is the sum of all cards, but the effective throughput is bounded by the slowest GPU in a tensor-parallel configuration. If your goal is purely fitting a large model, pipeline parallelism with weighted splits is the more forgiving path.

## Common Pitfalls and How to Avoid Them

Several mistakes trip up first-time multi-GPU builders:

**Tensor parallel on unsupported architectures.** MoE models (Grok, DeepSeek2, Mistral4) and state-space models (Mamba, Mamba2) do not support tensor parallel in llama.cpp. Check your model architecture before choosing a split mode, or you will get silent failures or crashes.

**Missing flash attention.** Tensor parallel in llama.cpp requires `--flash-attn` and a non-quantized KV cache. If you are using a quantized KV cache, tensor split will not work.

**Slow interconnect with tensor parallel.** On PCIe-only rigs without NVLink, tensor parallelism can be slower than a single GPU because communication overhead dominates. Prefer pipeline parallelism.

**NCCL not installed.** llama.cpp builds NCCL support by default, but NCCL itself is not bundled with CUDA. On a fresh install, multi-GPU tensor parallel may fail until you install NCCL.

**Uneven GPUs in tensor parallel.** Tensor parallel stalls on the slowest card. Use weighted `--tensor-split` in llama.cpp or switch to pipeline parallelism in vLLM for mixed hardware.

## When Multi-GPU Is (and Isn't) Worth It

Multi GPU local inference is not always the right answer. It is worth it when your model does not fit in a single GPU's VRAM and you want to keep inference fully local, or when you need higher throughput for concurrent requests and your interconnect can support it.

It is not worth it when a single GPU already fits the model comfortably, or when your interconnect is too slow to justify the added complexity. A 7B or 13B model on one 24 GB card will often outperform a poorly configured multi-GPU split of the same model. The added power draw, heat, and configuration complexity only pay off when the model genuinely exceeds single-GPU capacity or you have a real concurrency need.

## Conclusion: Building Your Home Multi-GPU Inference Rig

Multi GPU local inference is the practical way to drift large models across your home GPUs. Start with pipeline (layer) parallelism, which is the default and most compatible in llama.cpp and the recommended choice for PCIe-only rigs in vLLM. Move to tensor parallelism only when you have NVLink-connected GPUs, a supported model architecture, flash attention enabled, and a real throughput need.

Check your interconnect first, then your model architecture, then your split mode. For most home servers, a well-tuned pipeline split across two or three GPUs is the sweet spot: it fits models that exceed single-card VRAM without the communication overhead that makes tensor parallel fragile on consumer hardware.

## FAQ

**What is multi GPU local inference?**
Multi GPU local inference is running a single large language model across two or more GPUs in your own hardware, using pipeline or tensor parallelism, so you can fit models that exceed one GPU's VRAM or serve them faster.

**What is the difference between pipeline and tensor parallelism?**
Pipeline (layer) parallelism splits the model by layers, with each GPU running a contiguous slice. Tensor parallelism splits each layer's weight matrices across GPUs, which is faster per token but requires far more inter-GPU communication.

**Does multi GPU inference work with any model?**
No. In llama.cpp, tensor parallel is not implemented for MoE or hybrid architectures like Grok, DeepSeek2, and Mistral4, nor for state-space models like Mamba. Pipeline (layer) parallelism is the most compatible option.

**Do I need NVLink for multi GPU inference?**
Not for pipeline parallelism, which works fine over PCIe. Tensor parallelism benefits strongly from NVLink, and vLLM recommends pipeline parallelism for GPUs without NVLink, such as the L40S.

**How much VRAM do I need to run a 70B model locally?**
A 70B model in 4-bit quantization needs roughly 40 GB of VRAM, which exceeds a single 24 GB consumer card. Spreading it across two or more GPUs with multi GPU local inference lets you run it fully locally.
