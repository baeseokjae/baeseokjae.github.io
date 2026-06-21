---
cover:
  alt: 'Qwen 3 Full Model Lineup Guide 2026: 0.6B to 72B with Dual-Mode Thinking'
  image: /images/qwen-3-full-lineup-guide-2026.png
  relative: false
date: 2026-05-01 00:05:54+00:00
description: Complete guide to every Qwen 3 model from 0.6B to 235B — specs, VRAM
  requirements, dual-mode thinking, benchmarks vs. DeepSeek R1 and GPT-4o.
draft: false
schema: schema-qwen-3-full-lineup-guide-2026
tags:
- qwen3
- open-source-llm
- ai-models
- local-ai
- mixture-of-experts
title: 'Qwen 3 Full Model Lineup Guide 2026: 0.6B to 72B with Dual-Mode Thinking'
---

Qwen 3 is Alibaba's open-source LLM family released in 2026, spanning eight dense models (0.6B to 32B) and two MoE models (30B-A3B, 235B-A22B). All models run in both thinking and non-thinking modes, are licensed Apache 2.0, and were trained on 36 trillion tokens across 119 languages.

## What Is Qwen 3? Alibaba's Biggest Open-Source LLM Family Yet

Qwen 3 is a family of open-weight large language models developed by Alibaba's Qwen team, spanning from ultra-lightweight 0.6B edge models to the 235B-parameter MoE flagship that competes head-to-head with GPT-4o and Gemini 2.5 Pro. Unlike previous generations that separated chat models from reasoning models, every Qwen 3 model ships with a built-in dual-mode thinking system: flip a soft switch in your prompt and the same model either engages deep chain-of-thought reasoning or returns fast responses like a traditional assistant. Trained on 36 trillion tokens across 119 languages and dialects — up from 29 in Qwen 2.5 — the family covers code, math, STEM reasoning, and multilingual tasks under a single Apache 2.0 license. The flagship Qwen3-235B-A22B scores 95.6 on ArenaHard and 2056 on CodeForces Elo, outperforming DeepSeek-R1 on 17 of 23 benchmarks. For developers, this is the first open-source family where one model can genuinely replace both a reasoning specialist and a general-purpose chat model.

## The Full Qwen 3 Dense Model Lineup: 0.6B to 32B Explained

The Qwen 3 dense lineup includes six parameter tiers: 0.6B, 1.7B, 4B, 8B, 14B, and 32B. Every dense model supports a 128K token context window, dual-mode thinking, tool calling, and structured output. Efficiency improvements are dramatic compared to Qwen 2.5: the 8B matches the previous 14B in benchmarks, and the 32B matches the previous 72B. This means you can run the equivalent of last year's high-end model on hardware that used to only support mid-tier inference. All dense models are available on Hugging Face under the QwenLM organization and can be pulled directly via Ollama. The table below summarizes the core specs at full precision and Q4_K_M quantization for local deployment.

| Model | Parameters | Context | Q4 VRAM | Best For |
|---|---|---|---|---|
| Qwen3-0.6B | 0.6B | 32K | ~1 GB | Embedded/IoT |
| Qwen3-1.7B | 1.7B | 32K | ~1.4 GB | Mobile apps |
| Qwen3-4B | 4B | 128K | ~2.5 GB | Consumer GPU |
| Qwen3-8B | 8B | 128K | ~5–6 GB | Dev workstations |
| Qwen3-14B | 14B | 128K | ~10 GB | Mid-range server |
| Qwen3-32B | 32B | 128K | ~20 GB | High-performance server |

### Qwen3-0.6B and 1.7B — Edge Devices and Embedded Apps

Qwen3-0.6B and Qwen3-1.7B are designed for deployment contexts where RAM is measured in megabytes, not gigabytes. At Q4_K_M quantization, the 0.6B model runs in roughly 1 GB of memory — comfortably within Raspberry Pi 4 territory — while the 1.7B fits in 1.4 GB. Both models handle 119 languages, making them genuinely useful for multilingual edge applications without a network dependency. For classification, intent detection, short-form generation, or on-device text processing, these models punch above their weight class compared to Qwen 2.5 equivalents. The dual-mode thinking is present but limited in impact at this scale — thinking mode helps marginally on structured tasks but the model's capacity for complex reasoning is naturally capped by parameter count. Use these when network latency or data privacy prohibits cloud inference.

### Qwen3-4B — The Consumer GPU Sweet Spot

Qwen3-4B hits a sweet spot that few models have achieved before: a 128K context window, dual-mode thinking, and full tool calling support in a package that runs on a 4GB GPU at Q4 quantization. On a machine with an RTX 3050 or even integrated GPU with shared VRAM, you can run a model that matches Qwen 2.5-7B performance while handling long documents. For solo developers building local AI tools — RAG pipelines, document summarizers, personal assistants — the 4B is often the right default before you know your workload profile. At ~2.5 GB Q4, it also leaves headroom for the rest of your application stack on consumer hardware.

### Qwen3-8B — Best Value for Server Deployment

Qwen3-8B is the workhorse model for most production deployments. It requires 5–6 GB VRAM at Q4 quantization and matches the benchmark performance of Qwen 2.5-14B — a model that needed 10 GB. On an RTX 3060 12GB or a single A10G cloud instance, you get genuine high-quality inference with 128K context, thinking mode for complex tasks, and fast non-thinking mode for high-throughput pipelines. For API serving on a budget, the 8B delivers the best quality-per-dollar across the dense lineup. If you're building an application where the LLM makes decisions, calls tools, or processes long documents at scale, start here before sizing up.

### Qwen3-14B and 32B — High-Performance Reasoning

Qwen3-14B and 32B are the upper tier of the dense lineup, designed for server deployments where quality is the priority. The 14B needs ~10 GB VRAM at Q4 — accessible on RTX 3090/4080 — while the 32B requires ~20 GB, placing it on A100 40GB or dual consumer GPU setups. In benchmarks, Qwen3-32B effectively matches Qwen2.5-72B, meaning you get last year's largest open model on hardware that costs a fraction as much. Thinking mode on 32B is where you get genuinely competitive performance against closed-source reasoning models — complex multi-step math, code generation with verification, and research-grade writing become reliable at this tier.

## MoE Models Explained: Qwen3-30B-A3B and 235B-A22B

Mixture-of-Experts (MoE) models are a fundamentally different architecture from dense transformers: instead of activating all parameters for every token, they route each token through a small subset of specialized "expert" sub-networks. Qwen 3's MoE models use 128 total experts with 8 activated per token. The result is that Qwen3-30B-A3B — which has 30 billion total parameters — only activates 3 billion during inference, making it roughly as fast as a 3B dense model while achieving quality comparable to an 8B dense model. This changes the economics of deployment: you can run flagship-tier quality at a fraction of the compute cost if you can afford to load the full model into VRAM for the routing layer. Qwen3-235B-A22B takes this further: 235B total parameters, 22B active per forward pass, with performance that exceeds DeepSeek-R1 on 17 of 23 benchmarks and scores 2056 on CodeForces Elo — above both DeepSeek-R1 and Gemini 2.5 Pro at that metric.

### What Is Mixture of Experts and Why It Matters for Deployment

MoE architecture matters for deployment because it decouples total model capacity from per-token compute cost. In a dense model, doubling parameters doubles inference FLOPs. In a well-designed MoE model, you can double total parameters while keeping active parameters — and therefore latency and throughput — roughly constant. The tradeoff is storage and VRAM for loading all expert weights. For Qwen3-30B-A3B, you need to load 30B parameters into memory but only pay for 3B parameters worth of compute per forward pass. On hardware with fast memory but constrained compute (e.g., Mac Studio with M3 Ultra), MoE models can be dramatically faster than same-quality dense models. The 128-expert, 8-active configuration in Qwen 3 gives high expert specialization with manageable routing overhead.

### Qwen3-30B-A3B: 3B Inference Speed, 30B Quality

Qwen3-30B-A3B is the practical MoE choice for developers who want quality above the 8B dense tier without paying for a full 32B inference budget. Total VRAM requirement is ~20 GB to load all expert weights, but inference speed is closer to a 3B model due to sparse activation. This makes it particularly attractive on Apple Silicon — an M3 Max with 128 GB unified memory can run this model comfortably with faster throughput than a similarly-specced dense 30B. In practice, expect reasoning quality between the 8B and 14B dense models on general tasks, with thinking mode pushing it closer to 32B on structured reasoning problems. It's the right pick when you've outgrown the 8B but can't justify the VRAM of the 32B dense.

### Qwen3-235B-A22B: The Open-Source Flagship

Qwen3-235B-A22B is Alibaba's answer to GPT-4o and Gemini 2.5 Pro — a 235B-parameter MoE model that activates 22B parameters per forward pass, available under Apache 2.0 license with no usage restrictions. Running it locally requires a multi-GPU setup with at least 140 GB of total VRAM (multiple A100 80GB GPUs or an H100 system), but via cloud APIs like Alibaba DashScope or community endpoints, you can access it at competitive rates. On ArenaHard, it scores 95.6 compared to Gemini 2.5 Pro's 96.4, and it leads the field on CodeForces Elo at 2056. For organizations that need frontier-level reasoning without API lock-in, the 235B-A22B is the first open-source option that genuinely competes across the board.

## Dual-Mode Thinking: How to Switch and When to Use Each Mode

Dual-mode thinking is Qwen 3's defining feature: every model in the family can operate either in a deep chain-of-thought reasoning mode or a fast response mode, controlled by soft switches embedded in the prompt. This eliminates the fragmentation that plagued previous generations, where you had to maintain separate model deployments — one reasoning model for complex tasks, one chat model for speed. With Qwen 3, a single deployed model handles both workloads. The thinking mode uses internal chain-of-thought tokens (enclosed in `<think>...</think>` tags) before generating the final answer; the non-thinking mode skips this entirely and returns a direct response, cutting latency by 40–60% on typical inference hardware. In production, most teams implement a simple routing layer: classify the incoming task complexity, then inject `/think` or `/no_think` accordingly, giving them latency optimization without running two separate model instances.

### Thinking Mode — Deep Reasoning for Complex Tasks

To enable thinking mode, add `/think` to the system prompt or user message. The model will generate a detailed internal reasoning trace before producing its final answer. This is optimal for: multi-step math problems, code debugging where root cause is non-obvious, structured planning tasks, research synthesis, and any problem where correctness matters more than speed. The reasoning trace itself is useful for debugging model behavior — you can inspect why the model reached a conclusion. Thinking mode adds latency proportional to reasoning complexity; a simple arithmetic problem might add 200 tokens of chain-of-thought, while a complex coding problem might generate 2,000+ thinking tokens before the answer appears. Budget for this in timeout configurations.

### Non-Thinking Mode — Fast Responses for Simple Tasks

Non-thinking mode is activated with `/no_think` in the prompt. The model skips chain-of-thought entirely and responds directly, with latency comparable to a standard autoregressive decode. Use non-thinking mode for: conversational responses, intent classification, entity extraction, summarization of clear inputs, simple Q&A, and any high-throughput application where latency targets are tight. Most production deployments use non-thinking mode as the default and selectively enable thinking for flagged high-complexity requests. If you're building a chatbot where 90% of messages are "how do I reset my password" style queries, thinking mode on every request is wasted compute.

### How to Control Thinking Budget (Token Limits and API Flags)

Thinking budget refers to the maximum number of chain-of-thought tokens allowed before the model is forced to begin its final answer. Controlling it lets you tune the quality-vs-cost tradeoff. Via the Qwen 3 API (DashScope and compatible endpoints), pass `thinking_budget` as an integer in the API parameters — values typically range from 512 to 16,384 tokens. In Ollama and local inference, use the `num_predict` parameter or system prompt instructions: "Think for at most 1000 tokens before answering." A thinking budget of 1,024 tokens handles most coding and math tasks; bump to 4,096 for complex multi-step proofs or architecture design questions. Setting it to 0 is equivalent to non-thinking mode. For cost-sensitive production workloads, start at 1,024 and profile before increasing.

```python
# Example: Qwen3 via OpenAI-compatible API with thinking budget
import openai

client = openai.OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="YOUR_DASHSCOPE_KEY"
)

# Thinking mode with budget control
response = client.chat.completions.create(
    model="qwen3-8b",
    messages=[
        {"role": "user", "content": "/think Solve step by step: ..."}
    ],
    extra_body={"thinking_budget": 2048}
)

# Non-thinking mode for fast responses
response_fast = client.chat.completions.create(
    model="qwen3-8b",
    messages=[
        {"role": "user", "content": "/no_think Summarize this text: ..."}
    ]
)
```

## Qwen 3 Benchmark Performance vs. DeepSeek R1, Gemini 2.5 Pro, and GPT-4o

Qwen 3 benchmark results position the flagship 235B-A22B MoE model among the top three publicly available models as of mid-2026, with the dense lineup showing efficiency improvements that make smaller models competitive with previous-generation larger ones. The headline number: Qwen3-235B-A22B outperforms DeepSeek-R1 on 17 of 23 benchmarks and achieves a CodeForces Elo of 2056 — the highest among open-weight models and above Gemini 2.5 Pro on competitive programming. For the 8B dense model, matching Qwen2.5-14B means developers who were previously GPU-constrained to the 7B tier now effectively have 14B-quality inference within the same hardware budget. These aren't cherry-picked metrics: the efficiency gains hold across coding (HumanEval, LiveCodeBench), math (MATH-500, AIME), and general reasoning (MMLU, ArenaHard).

| Model | ArenaHard | MATH-500 | CodeForces Elo | MMLU |
|---|---|---|---|---|
| Qwen3-235B-A22B (thinking) | 95.6 | 97.2 | 2056 | 89.4 |
| Qwen3-32B (thinking) | 93.1 | 95.8 | 1970 | 88.2 |
| DeepSeek-R1 | 91.8 | 97.3 | 2029 | 90.8 |
| Gemini 2.5 Pro | 96.4 | 97.6 | 1994 | 91.1 |
| GPT-4o | 89.0 | 91.0 | 1796 | 88.7 |
| Qwen3-8B (thinking) | 82.4 | 90.2 | 1810 | 82.5 |

Key takeaway: Qwen3-235B-A22B in thinking mode is the best open-weight model for competitive programming and general reasoning, narrowly trailing Gemini 2.5 Pro on ArenaHard while leading on CodeForces. The 32B dense model in thinking mode surpasses GPT-4o on every listed metric while running locally on a dual-GPU consumer setup.

## VRAM and Hardware Requirements: Which GPU Do You Need?

Hardware requirements for Qwen 3 span from 1 GB for the smallest edge model to multi-GPU server setups for the 235B flagship. The figures below are for Q4_K_M quantization (practical for local deployment) and full BF16 precision (for production serving). Apple Silicon users get unified memory advantages: M2/M3 Pro Macs can run the 14B at full precision in 16 GB unified memory, which would require a dedicated GPU with the same VRAM otherwise. MoE models require loading all expert weights into VRAM for the routing layer, so despite low active parameters, storage requirements are high — plan for full model size in VRAM even though only a fraction is used per forward pass.

| Model | Q4 VRAM | BF16 VRAM | Recommended GPU |
|---|---|---|---|
| Qwen3-0.6B | ~1 GB | ~1.2 GB | Any (CPU viable) |
| Qwen3-1.7B | ~1.4 GB | ~3.4 GB | GTX 1660 / M1 |
| Qwen3-4B | ~2.5 GB | ~8 GB | RTX 3060 6GB+ |
| Qwen3-8B | ~5–6 GB | ~16 GB | RTX 3060 12GB |
| Qwen3-14B | ~10 GB | ~28 GB | RTX 3090 / 4080 |
| Qwen3-32B | ~20 GB | ~64 GB | A100 40GB or 2× RTX 4090 |
| Qwen3-30B-A3B | ~20 GB total | ~60 GB total | A100 40GB |
| Qwen3-235B-A22B | ~120+ GB | 470 GB+ | 4× A100 80GB / H100 |

For most developers, the practical tier is 8B on an RTX 3060 12GB or 14B on an RTX 3090. The 4B is the entry point for GPU-only inference on budget hardware. CPU inference via llama.cpp is viable for models up to 8B with acceptable latency; above that, expect 30+ seconds per response on typical server CPUs.

## Which Qwen 3 Model Is Right for You? Use Case Decision Guide

Choosing the right Qwen 3 model depends on your deployment target, VRAM budget, and latency requirements. The efficiency improvements over Qwen 2.5 mean the decision tree has shifted: where you previously needed a 14B for reliable coding tasks, an 8B now suffices; where you needed a 72B for complex reasoning, a 32B (or the 30B-A3B MoE) gets there. The MoE models are best on hardware with fast memory bandwidth but constrained compute (Apple Silicon, NVMe-backed CPU inference); dense models are better on traditional CUDA GPU setups where VRAM per compute is balanced. Use the following framework: first lock your VRAM budget, then check whether thinking mode or tool calling is required, then choose dense vs. MoE based on your memory bandwidth profile.

**Use case quick guide:**

- **Embedded / IoT / mobile**: Qwen3-0.6B or 1.7B — Apache 2.0, runs on-device, 119-language support
- **Local dev on consumer GPU (4–8 GB)**: Qwen3-4B or 8B — best quality-per-VRAM in the lineup
- **Production API serving, single GPU**: Qwen3-8B — highest throughput per dollar on A10G/L4
- **High-quality local reasoning, 24 GB GPU**: Qwen3-14B in thinking mode — matches last-gen 70B on most tasks
- **Frontier quality, open-weight, local**: Qwen3-32B or 30B-A3B on 40+ GB VRAM
- **Maximum quality, no hardware limit**: Qwen3-235B-A22B via DashScope API or self-hosted multi-GPU

## Key Features Across the Whole Family: Multilingual, Tool Calling, Long Context

Every Qwen 3 model — from 0.6B to 235B — ships with a consistent feature set that distinguishes it from prior open-source generations. The 119-language training corpus (up from 29 in Qwen 2.5) includes not just major European and Asian languages but regional dialects and low-resource languages, making Qwen 3 genuinely usable for global applications without separate localization models. Tool calling and structured output (JSON mode) are fully supported across all tiers, making function-calling workflows reliable even on the 4B model — important for agent frameworks like LangChain, LlamaIndex, and AutoGen that depend on structured outputs. Context window is 32,768 tokens for the two smallest models (0.6B and 1.7B) and 128K for all others, covering most real-world long-document use cases without chunking overhead. All models support the OpenAI-compatible chat completions API format, enabling drop-in replacement in existing pipelines.

| Feature | 0.6B / 1.7B | 4B–32B Dense | 30B-A3B / 235B-A22B MoE |
|---|---|---|---|
| Thinking mode | ✓ | ✓ | ✓ |
| Tool calling | ✓ | ✓ | ✓ |
| Context window | 32K | 128K | 128K |
| Languages | 119 | 119 | 119 |
| License | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| JSON/structured output | ✓ | ✓ | ✓ |

## How to Run Qwen 3 Locally with Ollama (Quick Start)

Running Qwen 3 locally via Ollama takes under five minutes from a cold start, and all models from 0.6B to 32B are available in the official Ollama library. Ollama handles quantization automatically — by default it pulls Q4_K_M, the best quality-per-VRAM balance for most hardware. Install Ollama from ollama.com, then use `ollama pull` to download your chosen model. The Ollama model tags follow the pattern `qwen3:SIZE`, where SIZE is the parameter count (e.g., `qwen3:8b`, `qwen3:4b`, `qwen3:32b`). The MoE models are tagged as `qwen3:30b-a3b` and `qwen3:235b-a22b`. After pulling, interact via the Ollama CLI, the REST API on `localhost:11434`, or any OpenAI-compatible client pointed at the Ollama endpoint.

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the 8B model (recommended starting point)
ollama pull qwen3:8b

# Run interactively
ollama run qwen3:8b

# Use thinking mode in the prompt
# >>> /think What is the time complexity of quicksort?

# API call with curl
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [
    {"role": "user", "content": "/think Explain merge sort step by step"}
  ]
}'

# Pull MoE model (needs 20+ GB VRAM)
ollama pull qwen3:30b-a3b

# Use with OpenAI SDK (drop-in replacement)
# base_url="http://localhost:11434/v1", api_key="ollama"
```

For thinking mode with budget control via Ollama's REST API, use the `options.num_predict` parameter to cap thinking token generation. The Ollama server exposes OpenAI-compatible endpoints, so any existing toolchain (LangChain, LlamaIndex, OpenWebUI) works without code changes — just update the base URL.

## Conclusion: Qwen 3 Is the Most Complete Open-Source LLM Family in 2026

Qwen 3 is the most complete open-source LLM family in 2026 not because any single model is the best in its class in isolation, but because the full lineup eliminates the usual compromises: you can start with a 4B on a consumer GPU, scale to 8B on a budget server, graduate to 32B for high-stakes reasoning, and hit frontier quality with the 235B-A22B — all on the same API format, same feature set, and Apache 2.0 license. The dual-mode thinking system removes the model-per-workload fragmentation that complicated earlier deployments. Efficiency gains over Qwen 2.5 mean the hardware bar to run quality models has dropped substantially. For most developers, the 8B is the default pick: 5–6 GB Q4 VRAM, 128K context, thinking mode, tool calling, and performance that exceeded the previous-generation 14B. Add thinking budget control from day one, route simple queries to non-thinking mode, and size up only when profiling shows the quality gap. The era of needing a closed-source API for serious LLM work is ending, and Qwen 3 is a major reason why.

---

## FAQ

The following questions cover the most common points of confusion developers encounter when evaluating Qwen 3 for the first time. Whether you're deciding between dense and MoE models, trying to understand the Apache 2.0 license scope, or figuring out how to enable thinking mode in an existing pipeline, these answers are based on the official Qwen 3 release documentation and real deployment experience. Each answer is self-contained — you don't need to read the full article to use these as a quick reference. The Qwen 3 family was released in April 2026 covering eight dense models (0.6B to 32B) and two MoE models (30B-A3B and 235B-A22B), all trained on 36 trillion tokens across 119 languages under Apache 2.0. If your question isn't answered here, the most current specifications are maintained in the official Qwen 3 technical report on arXiv (2505.09388) and the QwenLM GitHub organization.

### What is the difference between Qwen 3 dense and MoE models?

Dense models activate all parameters for every token, giving predictable latency proportional to parameter count. MoE models have a larger total parameter count but only activate a small subset (8 out of 128 experts) per token, making inference as fast as a much smaller model while retaining the quality of a larger one. For deployment, dense models are simpler and more predictable; MoE models need full weight loading in VRAM but cost less compute per forward pass.

### Can I use Qwen 3 for commercial projects?

Yes. All Qwen 3 models are released under the Apache 2.0 license, which allows commercial use, modification, and redistribution without royalties or usage restrictions. You can use Qwen 3 in production SaaS products, sell services built on it, and fine-tune the models without special permission from Alibaba.

### How do I enable thinking mode in Qwen 3?

Add `/think` at the beginning of your user message or system prompt. The model will generate internal chain-of-thought reasoning enclosed in `<think>...</think>` tags before producing the final answer. To disable it and get fast responses, use `/no_think` instead. You can also control the maximum thinking token budget via the `thinking_budget` API parameter (DashScope) or the `num_predict` option in Ollama.

### Which Qwen 3 model should I use for coding tasks?

For local deployment, Qwen3-8B in thinking mode is the best value: it fits in 5–6 GB Q4 VRAM and scores 1810 on CodeForces Elo — above GPT-4o. For the highest quality coding, Qwen3-32B in thinking mode reaches 1970 CodeForces Elo on 20 GB VRAM, and the 235B-A22B leads all open-weight models at 2056. For simple code completion or refactoring without deep reasoning, use non-thinking mode on any tier to cut latency.

### How does Qwen 3 compare to DeepSeek R1?

Qwen3-235B-A22B outperforms DeepSeek-R1 on 17 of 23 benchmarks including ArenaHard (95.6 vs 91.8) and CodeForces Elo (2056 vs 2029). DeepSeek-R1 leads on MATH-500 (97.3 vs 97.2) and MMLU (90.8 vs 89.4). For practical deployment, Qwen 3 has an advantage in multilingual support (119 vs ~30 languages), the dual-mode non-thinking fast path, and availability across all model sizes — DeepSeek-R1 is a single large model without a matched lightweight family.