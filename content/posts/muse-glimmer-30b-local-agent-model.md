---
title: "Muse Glimmer 30B Review: Meta's Always-On Local Agent Model (2026)"
date: 2026-10-01T01:13:08+00:00
tags:
  - "muse glimmer 30b"
  - "muse glimmer local agent model"
  - "meta muse glimmer"
  - "muse glimmer ollama"
  - "muse glimmer 30b vram requirements"
  - "muse glimmer vs qwen3.6 27b"
  - "muse glimmer vs gemma4 31b"
  - "run muse glimmer locally"
  - "muse glimmer gguf llama.cpp"
  - "dflash speculative decoding"
  - "apache 2.0 local agent model meta"
  - "always-on local agent model 2026"
description: "Muse Glimmer 30B is Meta's Apache 2.0 dense agent model for one GPU. Independent 2026 benchmarks, VRAM math and hands-on speed numbers."
draft: false
schema: "schema-muse-glimmer-30b-local-agent-model"
cover:
  image: "/images/muse-glimmer-30b-local-agent-model.png"
  alt: "Muse Glimmer 30B Review: Meta's Always-On Local Agent Model (2026)"
  relative: false
---

Muse Glimmer 30B is Meta's August 2026 open-weights agent model: about 29.6B dense parameters under Apache 2.0, built to run an always-on tool-calling loop on a single 24-32 GB GPU. It leads its size class on MCP Atlas (75.5) and offline tool use, but trails Qwen3.6-27B on terminal and desktop automation.

**The short version:** at 7.8/10, it is the strongest model you can point at your own files and let run unattended on one consumer card. It is also a dense model that pays for every parameter on every token, it hallucinates confidently when it does not know (82% in one independent calibration test), and it loses the GUI-control benchmarks to a cheaper rival. Whether that is a good trade depends entirely on which agent loop you actually run.

**Pros**

- Best-in-class tool calling and MCP behavior at this size: MCP Atlas 75.5 vs 62.5 for Qwen3.6-27B and 54.2 for Gemma4-31B.
- Unmodified Apache 2.0 with no acceptable-use policy and no monthly-active-user cutoff.
- Published, measured quantization loss: 0.2% average across 15 benchmarks at the 32 GB K-Quant-Dynamic build, 1.0% for the 17 GB build.
- Exceptionally lean KV cache at roughly 52 KiB per token, which is what makes 131,072-token context resident on a 24-32 GB card.
- Trained for failure recovery: it re-calls a schema-rejecting 400, retries a 503, and falls back when a tool is simply dead.

**Cons**

- Dense, not MoE. On an M3 Max it ran near 20 tok/s where a MoE rival hit roughly 70 tok/s on the same machine.
- 82% hallucination rate and an AA-Omniscience Index of -33: accurate often enough, poorly calibrated when wrong.
- Loses OSWorld-Verified (65.9 vs 75.6) and TerminalBench 2.1 (51.7 vs 60.7) to Qwen3.6-27B.
- Reasoning cannot be disabled, only dialed from low to xhigh, and xhigh roughly doubled token spend and wall-clock time in a measured test.
- `tool_choice: "required"` is documented as unsupported and fails silently rather than erroring.

## What Is Muse Glimmer 30B and What Did Meta Actually Ship?

Muse Glimmer is a 29.6B-parameter dense causal transformer plus a roughly 1.8B ViT-G/14 perception encoder, released on August 10, 2026 by Meta Superintelligence Labs under an unmodified Apache 2.0 license ([model card](https://huggingface.co/meta-models/Muse-Glimmer-30B)). It accepts text and images and emits text only. Audio is unsupported in both directions.

The model card's configuration is unusually specific, and it is worth reading before you plan hardware:

- 52 layers, hidden size 6,656, head dimension 128
- Grouped-query attention at 32 query heads to 2 KV heads, a 16:1 ratio
- Sliding window of 2,048 tokens in a repeating [Local, Local, Local, Global] pattern
- SwiGLU feed-forward dimension 19,968, RoPE theta 500,000 on local layers only
- Vocabulary of 202,048 (200k BPE plus 2,048 special tokens)
- Context window of 131,072 tokens, extendable to 262,144 in tooling, with a knowledge cutoff of January 4, 2026

It ships with an official ATEM tool-calling chat template using `<atem:function_calls>` and `<atem:invoke>` blocks, and a `reasoning_strength` variable you can set to low, medium, high, or xhigh.

The lineage matters for setting expectations. Glimmer is distilled from the closed flagship Muse Spark in three phases: logit distillation, then agent-heavy mid-training with reasoning traces, then supervised fine-tuning plus on-policy distillation and reinforcement learning. Meta states plainly that the student is generally less capable than its teacher and that Glimmer does not meet Meta's own Frontier AI definition. This is a deliberately positioned 30B agent workhorse, not a frontier model in a smaller box.

## Is Muse Glimmer 30B Dense or MoE?

Dense. There is no expert routing in the configuration, and that is a design bet rather than an oversight.

Meta and NVIDIA frame the choice as predictability: no routing decisions, no expert selection, and no variance in which token pathways fire per step. For an agent loop, the felt cost of a model is step latency, not a throughput benchmark. An MoE with 284B total and 13B active parameters can outrun a dense 30B on tokens per second, but its per-step timing swings with which experts get selected, and its memory math depends on which experts are resident.

The honest counterargument is that Glimmer pays full freight. Every token runs through all ~30B parameters, so a dense model at this size is slower than the MoE rivals it competes with. One reviewer measured roughly 20 tok/s for Glimmer on an M3 Max against about 70 tok/s for MoE Qwen3.6-35B-A3B and 60 tok/s for Gemma4-26B-A4B on the same machine, and concluded the architecture "will need an MoE if it wants to rival competitors" ([aymeric.fyi](https://aymeric.fyi/blog/muse-glimmer-local-test)).

Both things are true. Dense buys steady per-step latency and trivial memory arithmetic. It costs raw speed.

## Inside the Architecture: How Does 128K Context Fit on a 24 GB Card?

Through the KV cache, not through magic. The 16:1 grouped-query attention ratio and the 3-local-to-1-global attention pattern together shrink the per-token cache, and that is the unglamorous reason long agent sessions fit on desktop hardware.

| Model | Approx. KV cache per token | Cache pool on one DGX Spark |
| --- | --- | --- |
| Muse Glimmer 30B | ~52 KiB | 4.8M tokens |
| Qwen3.6-27B | 64 KiB | ~2.2M tokens (0.45x) |
| Gemma4-31B | ~840 KiB | ~0.76M tokens (0.16x) |

At 131,072 tokens, Glimmer's cache floor is roughly 1.8 GB. On a single DGX Spark the resulting KV pool reached 4.8M tokens, about 2.2x the Qwen 3.6-27B pool and 6.3x the Gemma4-31B pool ([Artificial Analysis](https://artificialanalysis.ai/articles/muse-glimmer), [classmethod](https://dev.classmethod.jp/en/articles/dgx-spark-muse-glimmer-first-touch)).

The practical consequence: an always-on agent that accumulates context for hours needs cache headroom more than it needs peak decode speed. A model with an 840 KiB per-token cache cannot hold that session on a 32 GB card at all, no matter how fast its tokens arrive.

## What Do the Published Quantization Numbers Actually Buy You?

Meta published degradation figures across 15 benchmarks, which turns "run it at 4-bit" from a leap of faith into a budget line you can compare.

| Build | Memory needed | Measured average loss | Typical target |
| --- | --- | --- | --- |
| BF16 | 55-58 GB+ | Baseline (0%) | 64 GB VRAM workstation |
| K-Quant-Dynamic | ~32 GB | 0.2% over 15 benchmarks | 32 GB card / 32 GB Mac |
| K-Quant-17GB | ~24 GB | 1.0% over 15 benchmarks | 24 GB card |
| UD-Q2_K_XL (Unsloth) | 12-14 GB | Not published by Unsloth | RTX 4080 class |
| UD-Q3_K_XL | 14-15 GB | Not published by Unsloth | RTX 4090 |
| UD-Q4_K_XL / NVFP4 | 17 GB+ | Comparable tier | 32 GB Mac, 24 GB card |
| UD-Q6_K_XL | 20-22 GB | Higher fidelity | RTX 5090 |
| UD-Q8_K_XL | ~34 GB | Near-lossless | 48 GB+ |

The 17 GB build on a 24 GB card or a 32 GB Mac is the sweet spot for most local agent work, and the 1.0% average loss is small enough that you should not treat it as a compromise tier. Two add-ons compete for the same envelope, though: the optional vision projector adds about 1.4 GB, and the DFlash speculative decoder adds about 1.63 GB on top of base weights ([Awesome Agents](https://awesomeagents.ai/reviews/review-muse-glimmer)).

Meta's default sampling settings are temperature 1.0, top_p 0.95, and top_k 64 ([Unsloth docs](https://unsloth.ai/docs/models/muse-glimmer)). Do not inherit another model's sampler config.

## How Fast Is Muse Glimmer 30B in Practice?

Speed is where this model's reputation lives or dies, and the spread across hardware is enormous.

| Hardware | Configuration | Measured throughput |
| --- | --- | --- |
| RTX 5090 (32 GB) | Lemonade, full 131K context, agent loops | ~110 tok/s |
| RTX 5090 | llama.cpp with DFlash | 74.9 -> 233.4 tok/s |
| DGX Spark | NVFP4, single request / 8-way parallel | 11.67 / 88.61 tok/s |
| DGX Spark | NVFP4 with DFlash | 21.57-23.74 tok/s |
| M5 Max | ExecuTorch with DFlash | 26.6 -> 50 tok/s |
| M4 Max | ExecuTorch with DFlash | 23.7 -> 38 tok/s |
| M3 Max (96 GB) | MLX with DFlash | ~20 tok/s |
| RTX 2000 Ada (16 GB) | 4-bit with CPU offload | ~6.2 tok/s decode |
| MacBook Air M3 / M4 | fanless, llama.cpp | ~4.3 tok/s |

The best end is genuinely good. On a 32 GB RTX 5090, an independent tester ran the full 131,072-token context with 27.6 GB of 31.5 GB VRAM occupied and nothing spilled to shared memory, holding roughly 110 tok/s inside real agent loops ([XDA Developers](https://xda-developers.com/muse-glimmer-30b-runs-on-my-32gb-gpu-never-leaves-the-machine)).

DFlash is what moves the model from "it runs" to "it responds." It proposes 16-token blocks for parallel verification with identical output to standard generation, and third-party measurements confirm real gains: 1.85x on vLLM (11.67 to 21.57 tok/s) and 2.13x on SGLang (11.16 to 23.74 tok/s) on a DGX Spark, broadly consistent with Meta's 3.1x claim on a 5090 and 1.5-1.8x on Apple silicon ([classmethod](https://dev.classmethod.jp/en/articles/dgx-spark-muse-glimmer-first-touch), [RITS](https://rits.shanghai.nyu.edu/ai/meta-releases-muse-glimmer-a-30b-agent-model-for-a-single-gpu)). One RTX 3060 Ti test gained only about 1 tok/s, so do not assume the multiplier transfers to small cards.

The worst end is just as concrete. On fanless MacBook Air M3 (24 GB) and M4 (32 GB) machines the model fits but generates around 4.3 tokens per second, which makes thermal headroom as important as unified-memory size ([HolaClaw](https://holaclaw.ai/blog/muse-glimmer-on-mac)). On a 16 GB RTX 2000 Ada with CPU offload, decode sat near 6.2 tok/s versus 10-11 tok/s for a dense 27B Qwen on the same box.

## The Thinking Tax: Can You Turn Reasoning Off?

No. The reasoning strength setting offers only low, medium, high, and xhigh. There is no off switch, and the chat template embeds whatever string you pass directly, which produces non-obvious failures.

A developer testing this found that passing `off` produced *more* thinking than passing `none`: 1,999 characters versus 1,243. The measured cost of the dial is substantial. Four identical questions cost 1,409 tokens and 123.9 seconds at low effort, versus 2,790 tokens and 245.8 seconds at xhigh. A single 50-character answer consumed 1,028 tokens and 90.55 seconds ([classmethod](https://dev.classmethod.jp/en/articles/dgx-spark-muse-glimmer-first-touch)).

This reframes the buying decision. Wall-clock time, not raw tok/s, determines which model feels faster in practice, and in that same test the slowest model won. If your agent loop fires many small tool calls, budget for reasoning tokens on every one of them and prefer low effort unless the task genuinely needs deliberation.

## Benchmarks: Where Does Muse Glimmer 30B Win and Where Does Qwen3.6-27B Still Beat It?

Glimmer does not win everywhere, and the losses are as decision-relevant as the wins. Every row below is attributed to the harness that produced it, because Meta's model card, Artificial Analysis, LM Studio's BionicBench, and individual hands-on tests are different measurement regimes.

**Meta's own reported results**

| Benchmark | Muse Glimmer 30B | Qwen3.6-27B | Gemma4-31B |
| --- | --- | --- | --- |
| MCP Atlas (Public) | 75.5 | 62.5 | 54.2 |
| SWE-Bench Verified | 76.0 | 77.2 | 66.6 |
| SWE-Bench Pro | 51.2 | Not reported | Not reported |
| OSWorld-Verified | 65.9 | 75.6 | Not reported |
| TerminalBench 2.1 | 51.7 | 60.7 | 43.4 |
| DeepSearch QA | 74.6 | Not reported | Not reported |
| AIME 2026 | 94.7 | Not reported | Not reported |
| GPQA Diamond | 83.5 | Not reported | Not reported |
| AA-LCR | 80.0 | Not reported | Not reported |
| IFBench | 77.0 | Not reported | Not reported |

The +13.0 MCP Atlas gap over Qwen3.6-27B is the headline for anyone building tool-calling agents, and it is the number that matches what hands-on testers report. The 9.7-point OSWorld deficit is equally real: if your agent drives a GUI, this is the wrong model.

**Independent evaluations**

| Evaluation | Source | Result |
| --- | --- | --- |
| Intelligence Index (high reasoning) | Artificial Analysis | 35, vs 38 for Qwen3.6-27B, 30 for Gemma 4 31B, 36 for 1T-parameter Kimi K2.5 |
| Agentic desktop tasks (18 real tasks) | LM Studio BionicBench | 83.3% completion vs 77.7% for both Qwen3.6-27B and Gemma 4 31B |
| GDPval-AA v2 | Artificial Analysis | 953 Elo, below the 1,000 human baseline and behind Qwen3.6-27B at 1,141 |
| Tau3-Banking | Artificial Analysis | 24%, best in class at this size |
| Vision (MMMU-Pro) | Artificial Analysis | 74% |
| Overall verdict | Awesome Agents | 7.8/10, "Fast, Free, Not Flawless" |

The BionicBench result is the most persuasive independent signal, because it uses 18 real desktop-agent tasks spanning coding, Word and Excel editing, PDF generation, and screenshot reading rather than a published academic suite ([Awesome Agents](https://awesomeagents.ai/reviews/review-muse-glimmer)).

## Can You Trust the Headline Benchmark Table?

Partly, and the caveats are worth stating rather than burying.

Meta reports the most favorable of self-reported and internally reproduced scores for rivals, which is a standard vendor move but means the comparison is not strictly apples-to-apples. The primary rival is Qwen3.6, roughly four months old at Glimmer's release, with Qwen3.8-27B expected within the same week ([Developers Digest](https://developersdigest.tech/blog/meta-muse-glimmer-30b-open-weights-local-agent)). Read the wins as directional until more independent runs land.

The calibration story is the sharper concern. On Artificial Analysis's AA-Omniscience index, Glimmer scores -33 with an 82% hallucination rate, against 49% for Qwen3.6-27B and 34% for Gemini 3.5 Flash-Lite. Accuracy at this size matches peers; the willingness to answer anyway does not. Inside a verification loop with real tool results to check against, that trait is survivable. As a standalone oracle you trust, it is not.

## Is the Apache 2.0 License the Real Headline?

For teams, yes. The repository's LICENSE file is the unmodified Apache License 2.0, not a Llama-style bespoke community license. There is no acceptable-use policy and no monthly-active-user cutoff ([Digital Applied](https://digitalapplied.com/blog/meta-muse-glimmer-30b-apache-2-local-agent-model-2026)).

That removes a lawyer from the deployment loop. Earlier Meta open-weights releases carried usage restrictions and user-count thresholds that made some commercial deployments a legal review rather than an engineering decision. Glimmer's openness index of 44 makes it the most permissive license Meta has shipped, on par with DeepSeek V4 Flash and GLM-5.2 ([Artificial Analysis](https://artificialanalysis.ai/articles/muse-glimmer)).

It is a governance fact, not a footnote, and it is the part of this release most likely to still matter in a year.

## How Do You Run Muse Glimmer 30B Locally Today?

The fastest path is one command on Ollama v0.32 or later:

```bash
ollama run muse-glimmer
```

Meta also ships companion repositories alongside the weights: GGUF builds, the DFlash drafter, and ExecuTorch `.pte` files. Day-one stacks with published support include transformers, llama.cpp, vLLM, LM Studio, MLX, ExecuTorch, Unsloth, SGLang, and Hugging Face Inference Endpoints. Note an availability nuance: Meta's blog says llama.cpp, MLX, and ExecuTorch land "in the coming days," while the model card claims day-0 support in transformers, llama.cpp, vLLM, and Inference Endpoints. If a build is missing, that discrepancy is why.

For serving behind an OpenAI-compatible endpoint, vLLM with AWQ quantization and an explicit `--max-model-len` is the common production recipe; llama.cpp's `llama-server` with a GGUF is the common local one. NVIDIA publishes SGLang and vLLM recipes, a downloadable NIM container, and a hosted endpoint on build.nvidia.com, and claims over 20K tokens/sec/GPU at BF16/NVFP4 on Blackwell Ultra ([NVIDIA developer blog](https://developer.nvidia.com/blog/run-local-agentic-ai-workflows-with-metas-muse-glimmer-on-nvidia/)).

Hosted alternatives exist if you do not want to run it yourself: Together AI, Fireworks AI, OpenRouter, and build.nvidia.com. Meta does not serve Muse Glimmer on its own API, so pricing and speed always come from a third party. Check current availability and the vLLM DFlash patch status at your time of deployment, since the launch-day patch was not yet in the distribution image.

On Mac, LM Studio's 18.16 GB build is a reasonable starting point. Simon Willison ran it through the `llm-coding-agent` plugin against a fresh Datasette checkout with the prompt "how does auth work?" and published the full tool-call transcript, calling the release a step up from "the janky Llama licenses of old" ([simonwillison.net](https://simonwillison.net/2026/Aug/10/introducing-muse-glimmer/)).

## Migration Footguns: tool_choice, Tool-Call Batching, and Engine Differences

Three behaviors will break client code that assumes OpenAI-compatible semantics.

**`tool_choice: "required"` is unsupported and fails silently.** It is documented as unsupported for this model, and in testing vLLM returned zero tool calls after 40.43 seconds with HTTP 200 and no error at all. llama.cpp happened to return one call on the same prompt. If your client assumes a tool call always arrives when you demand one, it will hang or misbehave with no diagnostic.

**Tool-call batching varies by task.** A two-city weather question came back as two separate assistant turns, one call each, where Qwen3.6-27B and Gemma4-31B both returned two calls in a single message. A repository-investigation task did return four `read_file` calls in one message. Your agent loop must handle both shapes.

**Thinking extraction differs between engines.** vLLM, llama.cpp, and SGLang each surface the reasoning channel differently, so prompt-level assumptions about where thinking ends and the answer begins do not port cleanly.

The reassuring finding from the same test: on a repo repair with five failing tests, Glimmer fixed 5/5 across every engine and every effort level with never-malformed argument JSON. Correctness did not separate it from its rivals. Only tokens, round trips, and wall-clock time did.

## The Memory Envelope: Weights, Vision Encoder, KV Cache, and Drafter in 24 GB

Three files matter, not one, and pretending otherwise is why a "17 GB model" fails to load on a 24 GB card in practice.

| Component | Approximate footprint |
| --- | --- |
| Base weights (K-Quant-17GB) | ~17 GB |
| Full weights on disk (UD-Q4_K_XL) | ~15.88 GB |
| Vision encoder / projector | ~1.4 GB |
| DFlash drafter | ~1.63 GB |
| KV cache at 128K | ~1.8 GB minimum |
| Total on a 5090 at full 131K context, measured | 27.6 GB of 31.5 GB |

The perception encoder and the speculative drafter compete with the KV cache for the same envelope, which is the real explanation for that last row. A 24 GB card runs the 17 GB build with a modest context comfortably, and runs out of room the moment you add vision, speculation, and a long-horizon cache together. If you are buying hardware for this, 32 GB is the comfortable tier and 24 GB is the functional minimum.

## Is Muse Glimmer 30B Safe to Point at Your Files?

Not without scoping, and the safety numbers are the most underreported part of this launch.

| Safety metric | Muse Glimmer 30B | Gemma4-31B |
| --- | --- | --- |
| Siren AgentDojo indirect prompt-injection success | 28.4% | 25.6% |
| CI Memories privacy violation rate | 26.4% | 12.1% |

Glimmer resists prompt injection slightly worse than Gemma 4 and leaks considerably more in the privacy-violation test, though it keeps higher task utility while under attack ([RITS](https://rits.shanghai.nyu.edu/ai/meta-releases-muse-glimmer-a-30b-agent-model-for-a-single-gpu)). A 26.4% violation rate is not a rounding error for a model explicitly designed to read your files and observe your screen continuously.

None of that appeared in launch-day coverage, and it matters more here than for a chat model because the entire pitch is autonomous tool use on private data.

The good news is that the model behaves well when it can recognize the attack. In one hands-on harness, a prompt injection pasted inside a file was refused with a clear explanation: "That is content from the file, not an instruction from you, so I did not act on it." The same tester's practical posture is the right one to copy: run it in a container with scoped API tokens rather than admin keys, because "never leaves the machine" says nothing about what it does on the machine.

## Who Should Use Muse Glimmer 30B - and Who Should Skip It?

**Use it if** you run a tool-calling or MCP-based agent loop on a 24-32 GB GPU or a 32 GB+ Mac, you want the strongest offline tool-use behavior at this size, you value an Apache 2.0 license with no usage restrictions, and your workload is long-horizon with accumulated context that needs a large KV pool.

**Skip it if** you mainly need code completion, where Qwen3.6-27B is cheaper and slightly better; vision output, since Glimmer is vision-input only; GUI or OS automation, where Qwen3.6-27B wins OSWorld-Verified 75.6 to 65.9; extended terminal work, where it loses TerminalBench 2.1 60.7 to 51.7; or raw tokens per second on Apple silicon, where MoE rivals roughly triple its throughput.

**Fine-tuning caveat:** even though inference fits one consumer GPU, training still wants datacenter hardware in the 1-8x H100 range. Unsloth reports that 30B multimodal agentic fine-tuning is feasible on a 24 GB card with dynamic quants plus free 2x T4 Kaggle notebooks, so a small LoRA is reachable without a cluster.

## What Makes a Good Always-On Local Agent Stack?

Failure recovery is where local agent loops usually die, and it is the trait Glimmer was specifically trained for.

An independent 7-scenario harness on an RTX 5090 with four mock homelab tools (file read, DNS via Technitium, Proxmox VM check, Home Assistant toggle) passed all seven scenarios in four consecutive runs at about 34 seconds per sweep. The interesting part is how it passed:

- A 400 response was re-called with the missing `node` field filled in.
- A 503 was treated as transient and retried.
- When the DNS tool was dead, it fell back to `/etc/hosts`.

That is diagnosis and recovery, not a prompt trick. Meta names OpenClaw and Hermes Agent as working local orchestration patterns, which is a useful signal that mainstream agent scaffolds are already tested against this template.

The counterpoint deserves equal weight. On an M3 Max with the MLX build, a task to find the model's own knowledge cutoff by tool calls ran over 28 minutes of crawling without landing on the right URL, then took another 22 minutes to extract the date even after being handed the exact URL. Long-horizon agency is not the same as reliable long-horizon agency ([aymeric.fyi](https://aymeric.fyi/blog/muse-glimmer-local-test)).

Long-context retrieval on a 16 GB card measured 87% overall across depth probes from 0% to 100% over 15 runs, but only 1 of 3 passed at the 75% depth mark. An agency sandbox passed 47 of 49 scenarios, and HumanEval scored 71% overall (84% of answered questions, with 26 questions lost to context exhaustion). A one-shot Kanban web app at 128K context succeeded, as did an MCP Blender task and a sandbox physics artifact. An MCP Godot orb bug was never resolved.

## Verdict: A Builder's Local Agent Model, Not a Cloud Replacement

Muse Glimmer 30B earns a 7.8/10 for a specific job: running an always-on, tool-calling agent entirely offline on one GPU. On a 32 GB RTX 5090 it held full 131K context at roughly 110 tok/s with nothing spilled; on a DGX Spark it served 88.61 tok/s at 8-way parallel while keeping a 4.8M-token KV cache pool; and on MCP Atlas it beats its nearest rival by 13 points. The Apache 2.0 license, the published quantization-degradation table, and the trained failure-recovery behavior are the three facts that make it deployable rather than merely demoable.

It is not a universal upgrade. Dense architecture means you pay for 30B parameters per token, the 82% hallucination rate makes it dangerous as an unchecked oracle, the safety numbers trail Gemma 4 on injection and privacy tests, and Qwen3.6-27B still owns terminal and GUI automation. Buy it for the agent loop, size the card at 32 GB, budget the vision projector and DFlash drafter in your memory math, and keep it in a sandbox with scoped tokens.

## FAQ: Muse Glimmer 30B

**How much VRAM does Muse Glimmer 30B need?**

The 17 GB K-Quant build runs comfortably on a 24 GB card, and the 32 GB K-Quant-Dynamic build has a measured 0.2% average loss across 15 benchmarks. Budget about 1.4 GB extra for the vision projector and 1.63 GB for the DFlash drafter, plus roughly 1.8 GB of KV cache at 128K context. A measured 32 GB RTX 5090 run used 27.6 GB of 31.5 GB with full context.

**Is Muse Glimmer 30B better than Qwen3.6-27B?**

It depends on the loop. Glimmer wins MCP Atlas 75.5 to 62.5, LM Studio's 18-task agentic desktop benchmark 83.3% to 77.7%, and Tau3-Banking at this size, and it is fully local under Apache 2.0. Qwen3.6-27B wins OSWorld-Verified 75.6 to 65.9, TerminalBench 2.1 60.7 to 51.7, SWE-Bench Verified 77.2 to 76.0, and has a higher independent Intelligence Index (38 vs 35).

**Can I run Muse Glimmer 30B on a Mac?**

Yes, with caveats. A 32 GB+ Mac is the comfortable tier and the MLX build runs at roughly 20 tok/s on an M3 Max with DFlash, or 23.7 to 38 tok/s on an M4 Max via ExecuTorch. Base fanless MacBook Air machines fit the model but generate around 4.3 tok/s, so thermal headroom matters as much as unified memory.

**Is the Apache 2.0 license really unrestricted?**

Yes. The LICENSE file is the unmodified Apache License 2.0 with no acceptable-use policy and no monthly-active-user cutoff, unlike earlier bespoke Llama community licenses. That is Meta's most permissive open-weights license to date, with an openness index of 44.

**Does Muse Glimmer 30B support tool calling and MCP?**

Yes, natively through an official ATEM chat template using `<atem:function_calls>` and `<atem:invoke>` blocks, and it scores 75.5 on MCP Atlas. Two caveats: `tool_choice: "required"` is unsupported and silently returns nothing, and tool-call batching varies between turns, so your loop must handle one call per message and several calls in one message.
