---
title: "AA AgentPerf Local: What Replaying Real Agent Trajectories Measures (and What It Cannot)"
date: 2026-10-15T00:30:00+00:00
tags:
  - AA-AgentPerf-Local
  - agentperf-local
  - agent trajectory replay benchmark
  - local LLM serving benchmark 2026
  - agentic inference throughput
  - KV cache prefill cost
  - Ollama ignore_eos
  - DGX Spark vs RTX 5090
  - Qwen3.8-27B local serving
  - speculative decoding MTP DFlash DSpark
  - benchmark comparability
  - local inference hardware 2026
description: "AA-AgentPerf-Local replays 8 recorded agent tasks and 168 model turns to measure local serving speed on agent-shaped traffic. What the replay measures, the comparability rules, and the vendor's launch results."
draft: false
schema: "schema-aa-agentperf-local-llm-serving-benchmark-2026"
---

AA-AgentPerf-Local is an open-source tool from Artificial Analysis that replays recorded agent trajectories against a local OpenAI-compatible server and reports throughput and latency. The short answer to what it measures: serving speed on agent-shaped traffic - requests that carry the whole conversation so far, with long prompts and heavy key-value cache reuse - and deliberately nothing about output quality. The short answer to what it cannot do: it cannot give you a portable number. A result from it is only comparable if the context size was full, the output policy was `exact`, and the tool mode is stated. Miss any of those and you have an indicative run, not a benchmark.

That distinction is the whole point of this review. If you are sizing local inference for coding agents, the number you quote in a purchasing meeting has to travel with its conditions.

## What the default replay actually is

The default workload is `agentperf-default-v1`: eight recorded agent tasks spanning 168 model turns. It uses the `exact` output policy, which makes every turn generate its recorded number of tokens, so every system does the same work. Each request carries the full conversation so far, so context grows to roughly 56K tokens, and the largest single turn in the default replay needs about 58,000 tokens. Tool execution is skipped by default; the intent is to isolate inference speed rather than to simulate a working day.

A second replay exists for install checks. `--replay aa-mini-v1` selects a six-turn synthetic replay, which the project describes as a quick install check whose results are not comparable.

One structural caveat is worth stating early: the eight tasks behind `agentperf-default-v1` are the vendor's recorded set. The public documentation we read defines their shape (task count, turn count, token behaviour) but does not enumerate them, so you cannot rebuild an identical workload from the docs alone - you replay the shipped trajectory set or you record your own with `convert`.

## Why agent-shaped traffic breaks single-prompt benchmarks

A single-prompt tokens-per-second figure tells you almost nothing about an agent workload, and the vendor's own numbers show why (VENDOR RESULTS, Artificial Analysis' announcement page, not our measurement):

- Between 73% and 93% of prompt tokens were served from the KV cache, so most of the prompt is never recomputed - decode is not the only bottleneck.
- Reading each turn's new input during prefill still consumed a substantial share of end-to-end completion time - the vendor reports 22-41% for Qwen3.8-27B.
- Each session still carried roughly 196K new input tokens against about 31K output tokens.
- When a tool returned a large file, the vendor measured the agent pausing up to 24 seconds on the Ryzen AI Halo and 39 seconds on the MacBook Pro before replying, against about 2 seconds on the GeForce RTX 5090.

Two practical consequences follow. First, a workload that is mostly cache hits is still prefill-sensitive: the tokens you do have to read dominate wall-clock time, which is why low-precision compute and prefill throughput matter as much as memory bandwidth. Second, agent turns are bursty and long-tailed. A mean latency hides the turn where a tool dumped a file into context and the agent stalled for half a minute.

## The comparability contract: the part most reviews skip

The tool enforces a contract, and the contract is the most useful thing in the documentation.

A full run needs a 65,536-token context at batch size 1. Every catalog profile launches at that context, and an attached server that serves more, such as 131,072 tokens, also counts as full. Anything below is marked `reduced: true` and is not comparable with full-context results. The default replay's largest turn needs about 58,000 tokens, so it only runs at the full 65,536; below that, the documented fallback is `aa-mini-v1`, which needs 8,192.

The `exact` policy sends `ignore_eos`, which is not part of the OpenAI API. Before the replay, `run` and `managed-run` check that the server honours it; if it does not, they stop and name the flag to change, and the TUI switches to the `recorded` policy instead and says so. This matters more than it looks: it means the tool refuses to silently publish a number that is not comparable.

The sharpest edge of this rule is Ollama. Ollama cannot honour `ignore_eos`. The tool detects Ollama before the run and warns, the run then uses the `recorded` policy, which lets the model stop on its own and reports end-to-end latency as a normalized estimate - and that result is not directly comparable with `exact` runs. In other words, the most widely installed local server on developer machines cannot produce a comparable AgentPerf run. If your plan was "install Ollama, run the agent benchmark, compare to the published charts", the tool itself will tell you why that comparison does not hold.

For attached servers the tool reads the context at the start of the run: `meta.n_ctx` from llama.cpp, `max_model_len` from vLLM and SGLang, or `maximum_context_tokens` from the Splash status endpoint. A server that reports none of them is recorded as not comparable.

## Tool time: three modes, three different questions

Tool execution is skipped by default, so the default result answers "how fast does this machine serve the model turns". Two opt-in modes answer different questions:

- `run --tool-mode fixed_delay` sleeps after each turn for the tool time recorded there - useful when you want end-to-end session time to include realistic tool gaps without running anything.
- `run --tool-mode live` runs the recorded shell commands in Docker containers, so tool time is real. It is opt-in, needs Docker and prebuilt images, and the docs are explicit that the recorded commands are untrusted input and Docker is not a security boundary; Docker daemon access is equivalent to root on most hosts, the task workspace is mounted read-write under the output directory, containers have no network by default but a replay manifest can ask for one, and `--live-network none` forces no network.

The build path matters for planning: the SWE-bench validation image script is arm64-only, so a live tool-mode run is not a same-day exercise on every laptop.

## How to run it on your own box

The documented path is short. Install with `uv tool install agentperf-local` (or run it without installing via `uvx agentperf-local`; `pipx install agentperf-local` also works), then either point `run` at a server you already have:

```console
agentperf-local run \
  --base-url http://127.0.0.1:8080/v1 \
  --model served-model \
  --output-dir results/my-server
```

or let the tool download, start and stop a pinned recipe itself:

```console
agentperf-local managed-run \
  --profile-id qwen38-27b-q4-k-m \
  --framework llama-cpp \
  --output-dir results/qwen38-27b
```

Typical base URLs for attached servers are `http://127.0.0.1:8080/v1` for llama.cpp, `http://127.0.0.1:1234/v1` for LM Studio, `http://127.0.0.1:8000/v1` for vLLM and `http://127.0.0.1:30000/v1` for SGLang. API keys are passed by variable name with `--api-key-env`; no flag takes a literal key. `deployment-options --profile-id <id>` shows which frameworks can serve a recipe on that machine, and `doctor` prints local hardware facts without identifiers. Submission is optional and nothing is uploaded unless you ask.

The pinned recipes are the part worth copying even if you never use the tool: each is a YAML file pinning a model, a quantization and a framework version, and `managed-run` verifies each file's SHA-256 before serving. The Splash recipe is a good example - it pins Splash 1.2.1 and the `incoai/Qwen3.8-27B-Splash` package by commit, so it never resolves a newer revision.

## The vendor's launch results, with the label they need (VENDOR RESULTS)

These rows are Artificial Analysis' own published results. We did not reproduce them, and every figure below is attributed to the vendor's announcement page and results page.

The launch hardware set is NVIDIA DGX Spark (128 GB), AMD Ryzen AI Halo (128 GB), MacBook Pro M5 Pro (64 GB) and NVIDIA GeForce RTX 5090 (32 GB), chosen to span CUDA, ROCm, Vulkan and Metal. The launch models are Qwen3.5-9B, Qwen3.8-27B, Qwen3.6-35B-A3B and Ling 3.0 Flash (124B total, 5B active), each benchmarked at 4-bit quantizations. All 14 published serving configs use speculative decoding (MTP, DFlash or DSpark), and where an official off-the-shelf config existed for a system and model pair the vendor used it.

The headline findings as the vendor states them:

- Completion time tracked each model's active parameter count most closely: Qwen3.6-35B-A3B (3B active) was fastest on every system, 2.5-3.3x faster than the dense Qwen3.8-27B; but Ling 3.0 Flash (5B active) still finished behind Qwen3.5-9B on all hardware that supports it.
- The GeForce RTX 5090 was the fastest system for every model that fits in its 32 GB, with completion times more than 3.5x faster than the other systems, and more than 5x faster decode than the unified-memory devices - 1,792 GB/s of memory bandwidth against 256-307 GB/s.
- The DGX Spark and the Ryzen AI Halo are broadly similar systems at the same $4,000 launch MSRP, yet the Spark was 1.4-1.7x faster on three of four models and tied on Qwen3.5-9B. The vendor attributes the gap, which is far larger than their 7% bandwidth difference, to the Spark's greater low-precision compute for prefill and its more mature CUDA software for MoE and speculative decoding.
- The MacBook Pro (M5 Pro, 64 GB, 20-core GPU) finished within 2-9% of the Ryzen AI Halo on Qwen3.6-35B-A3B and Qwen3.8-27B while being 21% slower on Qwen3.5-9B, with the highest bandwidth of the three unified-memory systems at 307 GB/s.
- Speculative decoding raised Qwen3.8-27B decode speeds roughly 30-120% above the bandwidth-constrained roofline on the most successful configs.
- On price, the vendor states that most hardware is significantly inflated versus launch MSRP, that the page defaults to launch MSRP with custom price entry allowed, and that at current market prices the MacBook Pro is the cheapest and the RTX 5090 system by far the most expensive.

Read those rows as vendor-run numbers under the vendor's own configs. The announcement page does not publish per-run raw traces, and no third party has replicated them.

## What we checked on our own hardware (and what it is not)

To verify that the client behaves as documented rather than to measure any hardware, we ran a bounded smoke run on our build box on 2026-10-15 between 00:12:32Z and 00:13:46Z: `agentperf-local` 0.3.3, the six-turn `aa-mini-v1` replay, against Ollama 0.20.3 serving qwen2.5:0.5b on an aarch64 box with 2 vCPUs, about 12 GiB of memory and no supported accelerator. We measured 6 successful turns out of 6, zero failures, 5 tool calls and 67.5 seconds of measured replay time.

The interesting output was not the timing. The client emitted both comparability guards on its own: the documented warning that Ollama cannot honour `ignore_eos` so the run uses the `recorded` policy and reports a normalized latency estimate, and a second warning that the endpoint did not prove its context window, so the run was recorded with `reduced: true` and marked not eligible for ranking. Every one of the six turns was additionally flagged as short output - 29 generated tokens against a 256-token target in the example we inspected - because a 0.5B model cannot follow a recorded trajectory.

That is exactly the evidence trail you want from a benchmarking tool, and it is also why none of those numbers may be quoted as a performance result. This was not the 168-turn workload, not full context, not an `exact`-policy run and not a hardware benchmark; it is a private local author check that the install path and the guard rails work. If you want a number that means something, you have to produce it on your own hardware.

## How to read any AgentPerf number honestly

Before you compare two results, or quote one, check that the following travel with the number: the tool version and client (Python or the experimental Rust client), the replay ID (`agentperf-default-v1` or something else), the context in tokens and whether `reduced: true` was recorded, the output policy (`exact` or `recorded`), the tool mode (none, fixed_delay or live), the model and quantization, the serving framework and the pinned recipe or config, and the hardware. If the run was submitted, `run --attached-server FILE` is what makes a run on a server you started traceable.

If any item is missing, treat the result as directional. Two numbers produced under different output policies, different context sizes or different tool modes are not a comparison; they are two different experiments.

## Limitations we are stating up front

- Every hardware, model, price and percentage figure in the vendor-results section is the vendor's own published claim, labelled as such; nothing in this article is an independent replication.
- We did not run the default 168-turn replay, no managed pinned recipe, no vLLM, SGLang or Splash target, no `fixed_delay` or `live` tool-mode run, and no power measurement (the tool's GPU power sampling is NVIDIA-only).
- The recorded task set behind `agentperf-default-v1` is not enumerated in the public documentation we read, so the workload cannot be independently reconstructed from the docs alone.
- The project is young and moving: the tool was first published in late September 2026 and the package version we checked, 0.3.3, was released on 2026-10-01. Star counts, open issues, recipes and hardware rows will date quickly.

For the surrounding decisions, see our companion pieces on [local AI model serving frameworks](/posts/local-ai-model-serving-frameworks-2026/), [vLLM versus Ollama in production](/posts/vllm-vs-ollama-production-2026/), [LLM benchmarks and API hosting](/posts/llm-benchmarks-api-hosting-comparison-2026/) and [LLM inference engineering](/posts/llm-inference-engineering-guide/).

## Sources

- Project repository (Apache-2.0): https://github.com/ArtificialAnalysis/aa-agentperf-local
- README as read on 2026-10-15: https://raw.githubusercontent.com/ArtificialAnalysis/aa-agentperf-local/main/README.md
- Licence file: https://github.com/ArtificialAnalysis/aa-agentperf-local/blob/main/LICENSE
- Package metadata: https://github.com/ArtificialAnalysis/aa-agentperf-local/blob/main/pyproject.toml
- Repository metadata (created/pushed dates, stars, issues): https://api.github.com/repos/ArtificialAnalysis/aa-agentperf-local
- Releases endpoint: https://api.github.com/repos/ArtificialAnalysis/aa-agentperf-local/releases
- Published package metadata: https://pypi.org/pypi/agentperf-local/json
- Vendor announcement (VENDOR RESULTS quoted above): https://artificialanalysis.ai/articles/aa-agentperf-local
- Vendor laptops and workstations results page: https://artificialanalysis.ai/hardware-inference-stack/laptops-workstations
