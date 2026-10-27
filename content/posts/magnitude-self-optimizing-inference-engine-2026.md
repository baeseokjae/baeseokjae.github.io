---
title: "Magnitude Review 2026: A Self-Optimizing Inference Engine for Agent Workloads"
date: 2026-10-01T22:03:22+00:00
lastmod: 2026-10-24T15:50:06+00:00
tags:
  - magnitude self-optimizing inference engine
  - magnitude inference engine
  - magnitude ai review
  - magnitude local inference server
  - self-optimizing inference engine
  - magnitude vs llama.cpp
  - magnitude vs ollama
  - magnitude vs mlx
  - magnitude seismic kernel tuning
  - local inference engine for agents
  - hardware-tuned llm kernels
  - magnitude kv cache 8-bit keys 4-bit values
  - magnitude speculative decoding dflash
  - magnitude port 10100 openai anthropic endpoint
  - magnitude review 2026
description: "Magnitude is an Apache-2.0 local inference engine that measures its own kernels once on your machine, then assesses each model from GGUF headers alone before download, and rewires your coding agent to use it. The real numbers."
draft: false
cover:
  image: "/images/magnitude-self-optimizing-inference-engine-2026.png"
  alt: "Magnitude Review 2026: A Self-Optimizing Inference Engine for Agent Workloads"
  relative: false
schema: "schema-magnitude-self-optimizing-inference-engine-2026"
---

Magnitude is an Apache-2.0 local inference engine that measures its own numerical kernels once on your machine, assesses each model's speed from GGUF headers alone before anything is downloaded, then serves the model on port 10100 and rewrites your coding agent's config to use it. "Self-optimizing" here means a kernel autotuner under a fixed precision policy, not a learning system. The claims below were re-verified against the live [repository](https://github.com/magnitudedev/magnitude/blob/main/README.md), its [Apache-2.0 license](https://github.com/magnitudedev/magnitude/blob/main/LICENSE), the [product documentation](https://docs.magnitude.dev/introduction.md) and the [launch thread](https://news.ycombinator.com/item?id=49911995) on 8 October 2026, and re-checked again on 24 October 2026 after the engine changed how it estimates speed. This is a source-verification review, not a hands-on benchmark: every figure is either the vendor's own artifact or a named third party's self-reported measurement.

That reading of the title matters more than the marketing number attached to it. Magnitude AI (YC S25) launched on Hacker News on 30 September 2026 with the claim "up to 2x faster than llama.cpp," and the repository's own benchmark script does support that number — for one machine, one model, one phase, and one baseline configuration. The more interesting parts of the project are the ones nobody put in the headline: a published α = 8 admission rule that makes the speed claim auditable, an ownership model that splits "what the model means" from "how the arithmetic runs," and a catalog that estimates your tokens per second from measured kernel rates before it lets you download 20 GB of model you cannot afford.

This review covers what Magnitude actually is, what the 92% decode figure covers, how it compares to the local inference tools you already run, and who should wait.

## What Is Magnitude, and What Does "Self-Optimizing" Actually Mean?

Magnitude is three things stacked. First, an assessment step in two stages. A measurement job runs once per machine in its own worker process, only while no model is loaded, loading or being optimized, and times the engine's own kernels — weight-format throughput, matrix throughput, attention cost per history layout, and launch and step cost — storing each point under that machine's hardware and driver so it is never measured twice while both stay the same. Every model assessment after that reads only GGUF headers, from the catalog's header bundle before download or the installed files after, and ranks complete configurations — model, quantization, context size and estimated tokens per second. The [decode-speed estimator](https://raw.githubusercontent.com/magnitudedev/magnitude/2f1a8495651d72ae820fe2cd8abcf8304fa79320/inference/engine/executor/src/assessment/estimate.rs) states the mechanism in its module doc: a model's decode speed comes from "its per-call demand and what the engine's kernels measurably achieve on its executor." The [assessment service](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/inference/service/server/src/assessment/assessor.rs) holds the other half of the line — it "reads only GGUF headers ... opens no device and loads no model" — and the [performance-estimation doc](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/design/icn/performance-estimation.md) says it structurally: "Only the measurement job measures ... the service never measures," and "per-model estimation opens no device and runs no model, benchmark or tuning." The [2026-10-20 change](https://github.com/magnitudedev/magnitude/commit/2f1a8495651d72ae820fe2cd8abcf8304fa79320) that introduced this replaced the memory-bandwidth table the earlier version of this review described; the numbers are no longer a published peak but timings of the engine's own kernels on your machine.

Second, an inference engine written in Rust around Seismic, a compiler and runtime for numerical kernels that owns compilation, device resources and execution across CPU, Metal, CUDA and Vulkan. Third, a Connections flow that rewrites a supported harness's config so the agent points at `http://127.0.0.1:10100`.

Two consequences are visible to a reader, not just to the codebase. Until the machine has been measured, a fitting model's speed shows as pending, and as unavailable with the reason when a figure it needs cannot be measured on that machine; a model with no speed estimate ranks after every model that has one. And the measurement is short: the same commit reports a cold job of 8.7 s on an RTX 3090 through Vulkan (7.8 s through CUDA), 10.6 s on a GB10 through Vulkan (7.2 s through CUDA) and 7.3 s on an M4 Pro. Those are the vendor's own single-run figures with no repetition count, variance or thermal state published, and we did not run the engine ourselves.

The self-optimizing part is an autotuner, and it is honest about its constraints. Magnitude ships authored numerical programs, compiles several physical variants of each one for your device, measures them, and keeps the fastest variant that still passes a fixed numerical check. That check is published in the repository's [precision documentation](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/precision.md), and it is one caller policy rather than a per-dtype table of tolerances: the engine's standard is α = 8, set "to admit every technique with a measured effect on speed," and a candidate passes when it moved the default's result by no more than α times the movement that storage-resolution noise causes at that same output or written state. The document is explicit that the per-operation allowances which follow from input resolution "are not handwritten tolerances or a table of model-specific permissions," and it separates admission from model quality: what the admitted error costs downstream is a measured property, established by evaluation, not something the tuner asserts.

Nothing learns, nothing phones home after a model is downloaded, and no accuracy is traded for throughput. That is a narrower claim than "the AI tunes itself," and it is a much stronger one. It is also the reason the 92% is auditable rather than aspirational — you can inspect the rule the tuner was not allowed to break.

Tuning cost is disclosed too. A co-founder in the launch thread described it as a one-time process of roughly a minute whenever you download a new model, after which tuning any longer asymptotes. Time varies with hardware.

## Is Magnitude Really 2x Faster Than llama.cpp?

Partly, and the qualifier is doing real work — with one more caveat: the claim itself has moved. The 30 September 2026 launch claim was "up to 2x faster than llama.cpp." The [current README](https://raw.githubusercontent.com/magnitudedev/magnitude/2f1a8495651d72ae820fe2cd8abcf8304fa79320/README.md) now says "It's over 2x faster than Ollama," described as an average across popular local models, a repositioning the repository dates to [13 October 2026](https://github.com/magnitudedev/magnitude/commit/00268e253bf99f3a5e759d21b8ea2a785065cb7a), with the benchmark updates that followed. Both are top lines. The four numbers behind the llama.cpp claim live in [`scripts/benchmark-chart.py`](https://github.com/magnitudedev/magnitude/blob/main/scripts/benchmark-chart.py) in the repository, and they are not uniform:

| Hardware / backend | Phase | llama.cpp | Magnitude | Delta |
|---|---|---|---|---|
| Mac M4 Pro 48 GB, Metal | Prefill | 466 tok/s | 507 tok/s | +9% |
| Mac M4 Pro 48 GB, Metal | Decode | 30 tok/s | 57 tok/s | +92% |
| DGX Spark, CUDA | Prefill | 2,033 tok/s | 2,507 tok/s | +23% |
| DGX Spark, CUDA | Decode | 49 tok/s | 58 tok/s | +19% |

The caption for that chart, verbatim from the script, is: Qwen 3.6 35B A3B, 4-bit, 64k context, no speculative decoding.

So "2x" is the Metal decode number on one Mac. The same artifact shows single-digit prefill improvement on that machine and a 19% decode improvement on CUDA. Any review that prints 2x without those four rows is repeating a top line the vendor's own data table does not generalize.

The method deserves credit for being stated. The benchmark is a prose-repetition task: the text of Moby Dick up to 64k context, then asking the model to repeat the last section. llama.cpp was configured with no speculative decoding, default prefill batch sizes, flash attention on, and a 16-bit KV cache. The team said they tried 8-bit keys with 4-bit values on llama.cpp and that it "bombed decode speed for llama.cpp in our testing" — which is a fair reason to leave it out, and also a reminder that the baseline is a conservative one.

Counter-evidence arrived in the same thread and belongs in the same section. An M5 Max owner measured MLX at 175 tok/s against Magnitude's 161, and the team acknowledged a Metal 4 matmul optimization gap on M5 and newer silicon. A 5070 Ti owner measured llama.cpp about 20-30% faster at decode on that card, and a second M5 Max owner reported both prefill and decode roughly 2x faster from llama.cpp. The honest generalization is "faster than llama.cpp on the configurations the vendor measured, on hardware the vendor likes" — not "faster than local inference."

One more thing the headline hides: the gain is a bundle of three shipped accelerations — device-tuned kernels, KV cache quantized to 8-bit keys and 4-bit values, and a per-model assigned draft model for speculative decoding — while the baseline ran with 16-bit KV and no speculation. No ablation separating the three has been published. Attribute the delta to the bundle, and say plainly that the split is unmeasured. If you want the underlying prefill-versus-decode mechanics, they are covered in our guide to [LLM inference engineering](https://baeseokjae.github.io/posts/llm-inference-engineering-guide/).

## How Does Magnitude Compare to llama.cpp, Ollama, LM Studio and MLX?

The axis that matters is not tokens per second. It is who chooses the model, and whether the tool is shaped for an agent or for a human at a prompt.

| Tool | Who picks model / quant / context | Tunes kernels on your device | Rewrites your agent config | Where it wins |
|---|---|---|---|---|
| Magnitude | Measures its own kernels once per machine, then ranks models from GGUF headers | Yes (Seismic autotuner) | Yes, one-click Connections | Agent serving on supported desktop hardware |
| llama.cpp | You pick the GGUF and launch flags | No (pre-built kernels) | No | Maximum control, widest hardware and model coverage |
| Ollama | You name a model tag | No | Partially (OpenAI-compatible port) | Simplest path to a model you already chose |
| LM Studio | You | No | Partially | GUI-first local use, broad model browsing |
| MLX | You | No (Apple-authored kernels) | No | Apple Silicon throughput, especially newer M-series |
| vLLM | You | No | No | Multi-user production throughput, not single-machine agents |

The practical consequence is that Magnitude is not a model runner so much as a model chooser that also runs the model. Ollama and LM Studio execute whatever tag you name; Magnitude decides which model, quantization and context size your machine should run by assessing it first, then tunes for that configuration and normalizes reasoning formats, tool-call formats, chat templates and history conventions so a harness can switch models without model-specific code. If you want the simplest way to run a model you picked, Ollama is still the smaller tool — our [Ollama vs LM Studio comparison](https://baeseokjae.github.io/posts/ollama-vs-lm-studio-local-ai-2026/) covers that choice.

Two boundaries worth stating. Magnitude is single-machine and single-user by design: models load on demand, unload when idle or under memory pressure, and sessions share prefix caches. It is not a production serving layer, and it does not try to be — that is [vLLM's territory](https://baeseokjae.github.io/posts/vllm-vs-ollama-production-2026/). And the machine-specific recommendation only matters if your model choices are constrained anyway; the [catalog](https://github.com/magnitudedev/magnitude/blob/main/inference/catalog/models.json) holds 23 models as of 8 October 2026, every entry GGUF-based and pinned to a specific Hugging Face repository and quantization variant, each carrying an Artificial Analysis Intelligence Index score measured against a frontier of Claude Opus 5.5 at 57.6 (methodology 4.3.2, as of 29 September 2026). Examples include Qwen3.8 27B at 33.7 — about 59% of the frontier — Qwen3.6 35B-A3B at 18.2, Gemma 4 31B at 19.0, and Nemotron 3.5 Lightning 30B-A3B at 12.9 with an NVFP4 QAT build. Our roundup of [the best local LLM models](https://baeseokjae.github.io/posts/best-local-llm-models-2026/) is the companion piece for what those models actually are.

## What Hardware Does Magnitude Support, and Where Does It Not Work Yet?

The compatibility floor is published, which is rarer than it should be. From the repository's [compatibility documentation](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/compatibility.md):

| Backend | Requirement |
|---|---|
| Metal | macOS 15 on arm64 (Apple Silicon) |
| CUDA | Compute capability 8.0 (Ampere) or newer, driver R525 / CUDA 12.0+ |
| Vulkan | Vulkan 1.3 device with a current vendor driver |
| CPU fallback | x86-64-v2 or AArch64 with glibc 2.35 on Linux |

Platforms are macOS (Apple Silicon and Intel), Windows x64 and Linux x64/arm64, with Windows agents inside [WSL documented separately](https://docs.magnitude.dev/api/windows-wsl.md). Intel Macs run CPU only. Phones and mobile GPUs are explicitly out of scope, as is hardware older than roughly the last seven or eight years. One documentation nuance to know: the [hardware page prose](https://docs.magnitude.dev/hardware.md) says "Vulkan 1.1 or later" while the enforced floor in compatibility.md is Vulkan 1.3 — treat 1.3 as the requirement.

The not-yet list is where you should focus if you are buying time. Multi-GPU is unsupported — the team confirmed it is on the near-term roadmap, and an [open issue documents a dual-GPU machine](https://github.com/magnitudedev/magnitude/issues) where Magnitude detected each card twice and then refused to use the second. The open-issue list on 8 October 2026 is concentrated in hardware detection and unsupported-model load: #142 "Stuck in assessing models" (12 comments), #148 a CPU-only Intel N100 whose first inference never completes, #151 an AMD Vulkan iGPU auto-selected despite a manifest declaring `backend=cpu`, #154 where 0.2.3 selects the AMD iGPU as the primary device on hybrid machines and excludes dGPU VRAM from the fit calculation, and #160 `attention_project_gemv` asking for 512 threads per threadgroup where the M1 Max pipeline allows 448. The launch thread's "this model couldn't start" report (#149) has since been closed with 17 comments; it is the kind of first-run failure the hardware-detection bugs above can produce.

Hardware detection bugs on hybrid iGPU/dGPU laptops and some CPU-only machines are the current weak spot, not throughput.

## How Do You Connect Magnitude to Your Coding Agent?

The service listens on port 10100 and speaks two dialects, per the [API overview](https://docs.magnitude.dev/api/overview.md) and [endpoint reference](https://docs.magnitude.dev/api/endpoints.md). OpenAI-compatible endpoints live under `http://127.0.0.1:10100/inference/v1` — `/chat/completions` and `/responses`, plus `/models` and `/health`. The Anthropic-compatible surface is `http://127.0.0.1:10100/inference/anthropic/v1/messages` with a matching `count_tokens` endpoint, where `max_tokens` is required.

No API key is needed from localhost. Remote access requires `network.enabled` plus an `apiKey` in `~/.magnitude/config.json`, and only inference is exposed remotely — the documented pattern, in the [remote-server guide](https://docs.magnitude.dev/remote-server.md), is a dedicated Mac Studio or DGX Spark running inference while your laptop runs the agent. `magnitude serve` gives you the same thing headless on macOS, Windows and Linux, which is what makes the project a genuine llama.cpp competitor rather than a desktop app with good UX.

Supported harnesses as of this writing are Pi, OpenCode, Hermes, OpenClaw, Codex, Claude Code, Oh My Pi and Cline ([integrations overview](https://docs.magnitude.dev/integrations/overview.md)); every other app connects through the OpenAI-compatible base URL. Connections rewrites the harness's own config file — useful, and worth knowing before you wonder why your agent's settings changed. If you prefer to wire things by hand and see the cost of doing so, our [Aider + Ollama walkthrough](https://baeseokjae.github.io/posts/aider-ollama-local-coding-2026/) shows the manual version, and [best Ollama models for coding](https://baeseokjae.github.io/posts/best-ollama-models-coding-2026/) covers the workload this engine targets.

## What Is Seismic, and Why Is the Engine Built Around It?

Seismic is Magnitude's numerical compiler and runtime, and it exists to own a boundary. The [inference README](https://github.com/magnitudedev/magnitude/blob/main/inference/README.md) states the split precisely: the engine owns model interpretation, generation, scheduling and state; Seismic owns numerical compilation, device resources and execution on CPU, Metal, CUDA and Vulkan. The [engine overview](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/engine/overview.md) enumerates the owners inside the engine — chat and transport, the service handling admission, batching, fairness and capacity negotiation, generation, model execution, logical state with history visibility, sharing, checkpoints, forks and commitment, then Seismic libraries and the Seismic toolchain. The [Seismic overview](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/seismic/overview.md) describes the same boundary from the other side: Seismic turns authored computational structure into implementations selected for a particular hardware and backend.

Hand-written kernels exist for eight model families (common, dflash, gemma4, lfm2, llama, muse_glimmer, nemotron_h and qwen35). The frozen previous implementation lives under `old-inference/`, where llama.cpp is retained as a preservation reference and, more usefully, as a source of independent numerical fixtures — an external comparator neither engine controls.

That is the part of the repository that makes the performance claim credible. Parity is checked at primitive boundaries against upstream llama.cpp tests, official tools such as llama-bench and llama-perplexity, differential cases against a thin native C++ oracle, and an external comparator. The repository's [evaluation contract](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/design/inference/evaluation.md) draws the same boundary explicitly: "a faster end-to-end answer does not establish faster model execution, and a faster kernel does not establish better serving," and execution parity "requires matched rendered input and generated work." A correctness failure invalidates the matching speed claim. Ownership tables per subsystem, an explicit optimality argument for the compiler, the published α = 8 admission policy, and four parity evidence lanes are not normal launch material. They are what let a reader audit the number instead of trusting it.

## What Are the Real Limitations in October 2026?

The catalog held 29 models on 24 October 2026, up from the 23 entries in the 8 October 2026 snapshot this review was verified against, and the hand-written kernels cover eight families. Anything outside that set is not going to receive the same attention, and model switching can break in-flight requests — a real consideration if your workflow swaps models mid-session rather than per-session.

There is no authentication story beyond a local API key, no rate limiting, and no multi-tenancy. There is no fine-tuning (the founders confirmed in the launch thread that training is not supported), no moderation and no image generation; this is chat-completions-shaped inference only. The hybrid inference cloud the founders describe is roadmap, not shipped.

Adoption is hard to measure and easy to overstate. The `@magnitudedev/cli` [npm package recorded 5,635 downloads](https://api.npmjs.org/downloads/point/last-month/@magnitudedev/cli) in the 30 days ending 4 October 2026 (237 in the last week), as read on 8 October 2026, but the docs say no npm installation is required because the desktop installer bundles the CLI — so npm undercounts real installs by an unknown factor. Re-reading the same endpoint on 24 October 2026 returned 586 downloads for the 30 days ending 22 October 2026; the window differs and we did not establish the cause, so that figure is reported as a later observation and not as a correction to the 5,635. For scale on 8 October 2026 the [repository metadata](https://api.github.com/repos/magnitudedev/magnitude) was read: ollama/ollama sits at 182,551 stars, llama.cpp at 130,661, vLLM at 93,378, MLX at 28,686. Magnitude had 6,496 stars, 444 forks, 37 open issues and 12 named contributors, with 1,164 commits since its first on 13 July 2026 and [76 releases](https://github.com/magnitudedev/magnitude/releases) to date. It is roughly three months old. The Rust half of the repository (32.2 MB) is more than three times the TypeScript half (9.7 MB), which tells you where the work has gone.

The pace is worth noting without treating it as stability: the newest release is `@magnitudedev/cli@0.2.6` (5 October 2026), and 0.2.0 through 0.2.6 all landed inside about six days. Fast releases are good news for a young engine and bad news for anyone who needs a frozen target.

## Who Should Run Magnitude, and Who Should Wait?

Run it if you are on Apple Silicon or an Ampere-or-newer NVIDIA GPU with roughly 24 GB or more, you drive a coding agent rather than a chat window, you have a repository or document class that cannot leave the building, and you would rather have a metadata-derived recommendation than an afternoon of GGUF guesswork. The assessment's real product is a decision you can trust before the download — the speed figure comes from one short measurement of the engine's own kernels on that machine plus header-only assessment of each model, never from a benchmark of somebody else's machine — and the Connections flow removes the config-writing chore entirely.

Wait if you need multi-user throughput (use vLLM), a multi-GPU box, an unsupported chip, any model rather than one of the 29 catalogued on 24 October 2026, or a sub-second experience without a GPU. Also wait if a cluster of hardware-detection issues on hybrid iGPU/dGPU laptops would hit your exact machine — check the open issues against your hardware before installing.

The open question is business model, and it is worth naming rather than burying. The engine, catalog and client are Apache-2.0 today with no paid tier and no license-gated features, and everything runs offline after a download. The founders have said they plan to monetize through per-token pricing on a hybrid inference cloud that passes on the same efficiency gains, with local-to-cloud switching that does not break a prefix cache. That is a coherent wedge. It is also unproven, so treat "free forever" as a stated plan rather than a contract. For the broader economics of running local at all, our [local rig cost-payback analysis](https://baeseokjae.github.io/posts/local-llm-rig-cost-payback-2026/) is the prerequisite reading, and the [local AI model serving frameworks guide](https://baeseokjae.github.io/posts/local-ai-model-serving-frameworks-2026/) covers the rest of the local stack — harness choices move cost, engine choices move tokens per second.

## FAQ

**What is Magnitude?**

Magnitude is an Apache-2.0 local inference engine and desktop app from Magnitude AI (YC S25). It measures its own numerical kernels once on your machine — a job of roughly 7 to 11 seconds on the machines the vendor reports, run only while no model is loaded — then assesses each model from GGUF headers alone, opening no device and loading no model, and ranks complete model, quantization and context configurations for that machine. It compiles and tunes its kernels on the device, serves the model on localhost:10100 and rewrites your coding agent's config to use it. The engine is Rust around Seismic, its numerical compiler and runtime for CPU, Metal, CUDA and Vulkan.

**Is "up to 2x faster than llama.cpp" true?**

The launch claim — "up to 2x faster than llama.cpp," posted on 30 September 2026 and since replaced in the README by "over 2x faster than Ollama" — is true for exactly the two configurations Magnitude published: Qwen 3.6 35B-A3B at 4-bit, 64k context, no speculative decoding — decode 30 to 57 tok/s (+92%) on an M4 Pro 48 GB via Metal, and 49 to 58 tok/s (+19%) on a DGX Spark via CUDA, where prefill gains were +9% and +23%. Both engines used the same settings family, with llama.cpp on flash attention, default prefill batches, no speculative decoding and 16-bit KV. It is a vendor benchmark on two machines, not a guarantee for yours, and independent users have measured MLX faster on an M5 Max (175 vs 161 tok/s) and llama.cpp 20-30% faster on a 5070 Ti.

**Does Magnitude replace Ollama or LM Studio?**

They solve overlapping but different problems. Ollama and LM Studio run whatever model tag you name; Magnitude decides which model, quantization and context size your machine should run by assessing it first, then tunes kernels and speculation for that configuration and wires itself into your agent harness. Magnitude also normalizes reasoning formats, tool-call formats and chat templates so a harness can switch models without model-specific code. If you want the simplest way to run a model you already picked, Ollama is still the smaller tool; if you want a metadata-derived recommendation plus agent-shaped serving, that is Magnitude's job.

**What hardware do I need, and what does it not support?**

Magnitude supports Apple Silicon Macs on macOS 15 or newer (Metal), NVIDIA GPUs from Ampere (compute capability 8.0) with driver R525 or newer, Vulkan 1.3 devices on Windows and Linux, and CPU-only fallback on x86-64-v2 or AArch64 with glibc 2.35 on Linux. Intel Macs run CPU only. Out of scope as of October 2026: phones and mobile GPUs, older CUDA cards, and multi-GPU systems — the team confirmed multi-GPU is near-term roadmap, and open issues #142, #148, #151, #154 and #160 document hardware detection and model-load failures on hybrid iGPU/dGPU machines and some CPU-only systems.

**Is Magnitude still open source if the company plans an inference cloud?**

The engine, catalog and client code are Apache-2.0 today with no paid tier or license-gated features, and model weights carry their own separate licenses. The founders have said they plan to charge per token for a hybrid inference cloud that passes on the same efficiency gains, and that switching between local and cloud workloads should not break a prefix cache. That plan does not currently gate anything locally — everything runs offline after a model is downloaded — but it is the stated direction, so treat "free forever" as a plan rather than a contract.

## Primary sources

- [Repository README](https://github.com/magnitudedev/magnitude/blob/main/README.md)
- [Benchmark chart script](https://github.com/magnitudedev/magnitude/blob/main/scripts/benchmark-chart.py)
- [Precision policy](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/precision.md)
- [Compatibility floors](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/compatibility.md)
- [Decode-speed estimator (pinned at 2f1a8495)](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/inference/engine/executor/src/assessment/estimate.rs)
- [Metadata-only assessment overview](https://github.com/magnitudedev/magnitude/blob/main/inference/engine/executor/src/assessment/mod.rs)
- [Generation-performance estimation (pinned at 2f1a8495)](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/design/icn/performance-estimation.md)
- [Per-model assessment service](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/inference/service/server/src/assessment/assessor.rs)
- [Evaluation and measurement boundaries](https://github.com/magnitudedev/magnitude/blob/2f1a8495651d72ae820fe2cd8abcf8304fa79320/design/inference/evaluation.md)
- [Change 2f1a8495: estimate decode speed from measured kernels](https://github.com/magnitudedev/magnitude/commit/2f1a8495651d72ae820fe2cd8abcf8304fa79320)
- [Change 00268e25: reposition as 2x faster than Ollama](https://github.com/magnitudedev/magnitude/commit/00268e253bf99f3a5e759d21b8ea2a785065cb7a)
- [Integrations overview](https://docs.magnitude.dev/integrations/overview.md)
- [Engine overview](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/engine/overview.md)
- [Seismic overview](https://github.com/magnitudedev/magnitude/blob/main/inference/docs/seismic/overview.md)
- [Inference README](https://github.com/magnitudedev/magnitude/blob/main/inference/README.md)
- [Model catalog](https://github.com/magnitudedev/magnitude/blob/main/inference/catalog/models.json)
- [Repository license](https://github.com/magnitudedev/magnitude/blob/main/LICENSE)
- [Launch HN thread](https://news.ycombinator.com/item?id=49911995)
- [Product documentation](https://docs.magnitude.dev/introduction.md)
