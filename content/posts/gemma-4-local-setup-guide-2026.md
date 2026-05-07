---
title: "Run Gemma 4 Locally in 2026: 31B Dense Setup Guide with Ollama"
date: 2026-05-07T06:04:01+00:00
tags: ["Gemma 4", "Ollama", "local LLM", "AI setup", "open source AI"]
description: "Step-by-step guide to running Gemma 4 31B Dense locally with Ollama — hardware requirements, installation, Open WebUI, and API usage."
draft: false
cover:
  image: "/images/gemma-4-local-setup-guide-2026.png"
  alt: "Run Gemma 4 Locally in 2026: 31B Dense Setup Guide with Ollama"
  relative: false
schema: "schema-gemma-4-local-setup-guide-2026"
---

Gemma 4 31B Dense runs locally on a single RTX 4090 or Mac M3 Max using Ollama — no API key, no data leaving your machine. Install Ollama, run `ollama pull gemma4:31b`, and you have a model that scores 87.1% on MMLU, beating GPT-4o's 86.5%, running entirely on your hardware.

## What Is Gemma 4 31B Dense and Why Run It Locally?

Gemma 4 31B Dense is a 31-billion-parameter language model released by Google DeepMind on April 2, 2026, under the Apache 2.0 license. Unlike mixture-of-experts architectures that distribute parameters across sparse expert layers, the 31B Dense model activates all 31 billion parameters on every token — giving it more reliable reasoning depth than larger MoE models with similar active parameter counts. In benchmark testing, Gemma 4 31B scores 87.1% on MMLU (beating GPT-4o's 86.5%), 89.2% on AIME 2026, and 84.3% on GPQA Diamond — outperforming Llama 4 Scout's 109B MoE model on the harder science benchmarks. Running it locally means zero API costs, complete data privacy, no rate limits, and the ability to integrate with any tool via the OpenAI-compatible REST endpoint that Ollama exposes on `localhost:11434`. For developers, researchers, or privacy-conscious users, this is the highest-performing open model available for on-device inference as of mid-2026.

### Dense vs. MoE: Why the Architecture Matters for Local Inference

A dense model like Gemma 4 31B activates every parameter on every forward pass. An MoE model like Llama 4 Scout (109B total, ~17B active) routes each token through only a subset of expert layers. For local inference, the dense architecture has a decisive advantage: total VRAM needed corresponds directly to the active parameter count. With Q4_K_M quantization — Ollama's default — Gemma 4 31B fits in approximately 24GB VRAM, which is exactly what a single RTX 4090 or RTX 6000 Ada provides. A 109B MoE model at the same quantization still requires routing infrastructure and substantially more memory even if active parameters are lower, making it harder to run on consumer hardware without CPU offloading.

## Gemma 4 Model Variants: E2B, E4B, 26B, and 31B Compared

Gemma 4 ships in four variants with meaningfully different hardware requirements and capability profiles. The E2B (2B Edge) and E4B (4B Edge) models are designed for mobile and embedded deployment — they feature native audio input and a 128K context window, making them unique among the family. The 26B and 31B models target server and workstation deployment, both supporting a 256K token context window and excelling at multi-step reasoning, coding, and mathematics. The 31B Dense specifically is the flagship for local deployment: it is natively trained on over 140 languages, released under Apache 2.0, and achieves GPT-4o-class performance on a single high-end consumer GPU. The choice between variants comes down almost entirely to available VRAM, since quality scales predictably across the lineup.

| Variant | Active Params | VRAM (Q4_K_M) | VRAM (FP16) | Context | Best For |
|---------|--------------|----------------|-------------|---------|----------|
| E2B | 2B | ~1.5 GB | ~4 GB | 128K | Mobile, edge devices |
| E4B | 4B | ~2.8 GB | ~8 GB | 128K | Laptop CPU/integrated GPU |
| 12B | 12B | ~6.6 GB | ~24 GB | 128K | RTX 3060, M2 MacBook |
| 26B | 26B | ~14 GB | ~52 GB | 256K | RTX 3090, M3 Pro |
| 31B | 31B | ~18–24 GB | ~62 GB | 256K | RTX 4090, M3 Max, M4 Ultra |

### Which Variant Should You Pick?

If you have 24GB VRAM (RTX 4090, RTX 6000 Ada) or 32GB+ unified memory (M3 Max, M4 Pro/Max), run the 31B. If you have 16GB VRAM (RTX 4080, A4000), run the 26B at Q4_K_M. For anything with 8–12GB VRAM (RTX 3060 12GB, RTX 4060 Ti 16GB), the 12B variant is the correct choice — it requires only 6.6GB VRAM at Q4 quantization and delivers strong coding and reasoning performance. The E2B and E4B are specifically for devices without a discrete GPU.

## Hardware Requirements for Gemma 4 31B (VRAM, RAM, CPU)

Gemma 4 31B Dense requires 24GB VRAM at Q4_K_M quantization or 62GB VRAM at full FP16 precision. In practice, Q4_K_M is the correct target for consumer hardware: Ollama defaults to this quantization automatically, reducing memory usage by approximately 55–60% compared to FP16, with only a marginal quality drop that is typically imperceptible in conversational and coding tasks. The minimum viable GPU is a single RTX 4090 (24GB). For Mac users, the M3 Max (36GB or 48GB unified memory) and M4 Pro/Max provide excellent performance because Apple Silicon shares memory between CPU and GPU — you can run the 31B comfortably with 36GB total unified memory. Linux workstations with dual RTX 3090s (24GB each) can also run the 31B by splitting the model across GPUs, though this requires additional configuration and results in slower inference than a single 4090.

| GPU / Platform | VRAM / Unified Memory | Gemma 4 31B (Q4)? | Notes |
|----------------|----------------------|---------------------|-------|
| RTX 4090 | 24 GB | Yes | Ideal single-GPU setup |
| RTX 6000 Ada | 48 GB | Yes | Runs FP16 too |
| RTX 4080 | 16 GB | No | Use 26B instead |
| RTX 3090 x2 | 48 GB total | Yes | Slower, split model |
| M3 Max 36GB | 36 GB unified | Yes | Excellent tok/s |
| M4 Max 64GB | 64 GB unified | Yes | Can run FP16 |
| M2 MacBook Pro 16GB | 16 GB unified | No | Use 12B instead |

**System RAM:** Ollama also uses system RAM for the context cache. Aim for at least 32GB system RAM when running 31B. CPU doesn't significantly affect generation speed once the model is loaded into VRAM — but fast NVMe SSD storage (PCIe 4.0+) reduces initial model load time from cold.

## Step 1 — Install Ollama on Mac, Windows, or Linux

Ollama is the fastest path to running Gemma 4 31B locally, providing a one-command model download, automatic quantization selection, and an OpenAI-compatible REST API out of the box. It abstracts away model sharding, quantization configuration, and the llama.cpp backend — you get a clean CLI and HTTP interface without needing to understand the internals. As of May 2026, Ollama supports CUDA (NVIDIA), ROCm (AMD), Metal (Apple Silicon), and CPU-only inference. Installation is straightforward across all three major operating systems, and the entire setup from zero to running model takes under 10 minutes on a fast internet connection. Ollama version 0.5+ is required for Gemma 4 support — older versions do not have the model architecture registered.

**Mac:**
```bash
brew install ollama
# or download the .dmg from ollama.com
ollama serve  # starts the background server
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
# Automatically installs CUDA drivers if NVIDIA GPU detected
# Service starts automatically via systemd
```

**Windows:**
Download the installer from [ollama.com](https://ollama.com). The installer configures a background Windows service and adds `ollama` to PATH. CUDA support requires NVIDIA drivers 525.85+.

**Verify the install:**
```bash
ollama --version
# Should output: ollama version 0.5.x or higher
```

## Step 2 — Pull and Run the Gemma 4 31B Model with Ollama

Pulling Gemma 4 31B downloads approximately 18–20GB of model weights in Q4_K_M format. Ollama handles quantization and model registration automatically — no manual GGUF conversion or configuration required. The model is pulled from Ollama's model registry, which mirrors the Hugging Face checkpoint in a pre-quantized GGUF format. On a 500 Mbps connection, the download takes roughly 5–7 minutes. Once complete, the model is cached locally in `~/.ollama/models/` and subsequent loads are instant. The Gemma 4 31B Ollama tag is `gemma4:31b` — note this differs from the Hugging Face naming convention.

```bash
# Pull the 31B Dense model (Q4_K_M by default, ~18GB)
ollama pull gemma4:31b

# Run an interactive chat session
ollama run gemma4:31b

# Example prompt after model loads:
>>> Explain the difference between dense and MoE transformer architectures.
```

**Other variants:**
```bash
ollama pull gemma4:2b    # E2B edge model
ollama pull gemma4:4b    # E4B edge model
ollama pull gemma4:12b   # 12B standard
ollama pull gemma4:26b   # 26B standard
```

**Check which models are installed:**
```bash
ollama list
```

**Stop a running model session:**
```bash
# In the chat, press Ctrl+D or type /bye
# To stop the background Ollama server:
ollama stop gemma4:31b
```

### Running Multiple Prompts via the CLI

```bash
# Non-interactive single prompt
ollama run gemma4:31b "Write a Python function that parses JSON from a REST API response"

# Pipe stdin for batch processing
echo "Summarize this text: $(cat document.txt)" | ollama run gemma4:31b
```

## Step 3 — Set Up Open WebUI for a ChatGPT-Like Interface

Open WebUI is an open-source browser interface that connects directly to Ollama, providing a polished chat experience with conversation history, model switching, file uploads, and system prompt configuration — all running locally. It runs as a Docker container and takes under 2 minutes to set up once Docker is installed. The interface is accessible at `http://localhost:3000` and supports multiple users, making it useful for team deployments on a local network where a shared Gemma 4 instance is hosted on a single powerful machine. Open WebUI automatically detects all models registered in Ollama, so switching between the 12B and 31B variants is a dropdown selection in the interface.

**Prerequisites:** Docker Desktop (Mac/Windows) or Docker Engine (Linux).

```bash
# Pull and start Open WebUI with Ollama auto-detection
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

# Access at: http://localhost:3000
```

On first launch, create an admin account (local only — no external services involved). Under Settings → Models, Gemma 4 31B should appear automatically if Ollama is running. Select it as the default model and start chatting.

## Using the Gemma 4 31B Local API (OpenAI-Compatible)

Ollama exposes an OpenAI-compatible REST API at `http://localhost:11434/v1`, allowing any tool or application that supports the OpenAI SDK to use Gemma 4 31B as a drop-in replacement. This means you can point VS Code extensions like Continue, Python scripts using the `openai` library, or LangChain pipelines directly at your local Gemma 4 31B instance without modifying code — just change the base URL and set the API key to any non-empty string (Ollama ignores it but the SDK requires a value). This makes Gemma 4 31B an immediately usable private coding assistant with zero monthly cost, zero rate limits, and no data ever leaving your machine.

**Python (OpenAI SDK):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required but ignored by Ollama
)

response = client.chat.completions.create(
    model="gemma4:31b",
    messages=[
        {"role": "user", "content": "Review this Python function for bugs: def parse(x): return x['data']"}
    ]
)
print(response.choices[0].message.content)
```

**curl:**
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:31b",
    "messages": [{"role": "user", "content": "Hello, Gemma 4!"}]
  }'
```

**Native Ollama API (also available):**
```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma4:31b", "prompt": "Explain gradient descent"}'
```

### Streaming Responses

```python
stream = client.chat.completions.create(
    model="gemma4:31b",
    messages=[{"role": "user", "content": "Write a FastAPI endpoint for user authentication"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

## Gemma 4 31B Benchmarks: How It Stacks Up Against GPT-4o and Llama 4

Gemma 4 31B Dense achieves state-of-the-art results for its parameter count, posting 87.1% on MMLU versus GPT-4o's 86.5% — a meaningful reversal given the cost difference (free vs. API pricing). On GPQA Diamond, a graduate-level science benchmark that measures genuine reasoning depth, Gemma 4 31B scores 84.3%, compared to Llama 4 Scout's 74.3% despite Scout having a 109B total parameter count. The AIME 2026 score of 89.2% places it among the top tier of math-capable models available to run without an API. As of April 2026, Gemma 4 31B ranks #3 on the Chatbot Arena (LMSYS) leaderboard — the only fully open model in the top five. This makes it the strongest option for teams that need GPT-4o-class reasoning performance in an air-gapped or privacy-first deployment.

| Benchmark | Gemma 4 31B | GPT-4o | Llama 4 Scout (109B MoE) | Claude 3.7 Sonnet |
|-----------|-------------|--------|--------------------------|-------------------|
| MMLU | 87.1% | 86.5% | 83.2% | 88.3% |
| GPQA Diamond | 84.3% | 83.4% | 74.3% | 84.8% |
| AIME 2026 | 89.2% | 83.1% | 67.4% | 86.5% |
| HumanEval | 85.4% | 87.0% | 79.3% | 86.1% |
| Arena Rank | #3 | #2 | #7 | #1 |

*Benchmarks sourced from Google DeepMind release notes and third-party evaluations, April–May 2026.*

## Optimization Tips: Quantization, GPU Layers, and Context Window Tuning

Ollama's default Q4_K_M quantization is the right choice for most users, reducing VRAM usage by 55–60% versus FP16 with minimal quality degradation. But beyond quantization format, there are several settings worth tuning to maximize performance on your specific hardware. The most impactful variable is GPU layer offloading (`num_gpu`) — Ollama automatically offloads as many layers as fit in VRAM, but you can override this with an `Modelfile`. Context window size (`num_ctx`) also directly affects VRAM usage: Gemma 4 31B supports 256K tokens, but setting a 4K or 8K context for coding tasks frees significant memory for additional parallel requests.

**Create a custom Modelfile for tuned inference:**
```
FROM gemma4:31b

# Set context window (default: 2048, max: 256K)
PARAMETER num_ctx 8192

# Force all layers to GPU (override auto-detect)
PARAMETER num_gpu 99

# Temperature for deterministic coding output
PARAMETER temperature 0.1
```

**Build and run the custom model:**
```bash
ollama create gemma4-coding -f Modelfile
ollama run gemma4-coding
```

**Quantization options and trade-offs:**
| Format | VRAM (31B) | Quality | Speed |
|--------|-----------|---------|-------|
| FP16 | ~62 GB | Best | Fastest per token |
| Q8_0 | ~33 GB | Near-lossless | Fast |
| Q4_K_M | ~18–24 GB | Good (default) | Good |
| Q4_0 | ~17 GB | Slightly lower | Slightly faster |
| Q3_K_M | ~14 GB | Acceptable | Fast on low VRAM |

### Monitoring GPU Utilization

```bash
# NVIDIA
watch -n 1 nvidia-smi

# Mac (using powermetrics or mactop)
mactop

# Check Ollama model status
ollama ps
```

## Common Errors and Fixes When Running Gemma 4 31B Locally

Most failures when running Gemma 4 31B locally fall into three categories: insufficient VRAM causing OOM errors, Ollama version mismatches that predate Gemma 4 support, and port conflicts preventing the API from starting. These are all straightforward to diagnose and fix — Ollama's error messages are specific enough to point directly to the root cause in most cases. The most common mistake is attempting to run the 31B model on a GPU with less than 20GB VRAM without adjusting quantization. The second most common is running Ollama 0.4.x, which predates the `gemma4` model tag and returns a "model not found" error regardless of what you pull.

**Error: `CUDA out of memory` or `error: model requires more system memory`**
```bash
# Check available VRAM
nvidia-smi --query-gpu=memory.free,memory.total --format=csv

# Solution: Force a lower quantization by pulling a specific GGUF tag
ollama pull gemma4:31b-q3_k_m  # ~14GB VRAM

# Or switch to the 26B model
ollama pull gemma4:26b
```

**Error: `model "gemma4:31b" not found`**
```bash
# Check Ollama version (needs 0.5+)
ollama --version

# Update Ollama
curl -fsSL https://ollama.com/install.sh | sh  # Linux
brew upgrade ollama  # Mac
```

**Error: `listen tcp :11434: bind: address already in use`**
```bash
# Another process is using port 11434
lsof -i :11434
kill -9 <PID>
ollama serve
```

**Slow generation speed (< 5 tok/s on RTX 4090)**
```bash
# Verify GPU is being used, not CPU
ollama ps  # shows active model and runner type

# If showing "cpu" runner, CUDA drivers may not be detected
# Reinstall with CUDA drivers:
OLLAMA_SKIP_GPU=false ollama serve
```

**Model loads but produces garbage output**
```bash
# Corrupted model file — re-pull
ollama rm gemma4:31b
ollama pull gemma4:31b
```

---

## FAQ

The following questions address the most common issues and misconceptions when setting up Gemma 4 31B locally with Ollama. Hardware compatibility is the most frequent stumbling block — specifically the gap between a model's FP16 memory footprint and its quantized footprint. Gemma 4 31B at Q4_K_M requires roughly 18–24GB VRAM, not the 62GB you would need for FP16, which changes the hardware requirements dramatically. Other common points of confusion include the model variant naming (no "27B" variant exists in Gemma 4), offline operation capabilities (the model runs entirely air-gapped after the initial download completes), CPU fallback behavior when no compatible GPU is present, and licensing terms for commercial deployments. The Apache 2.0 license makes Gemma 4 31B fully usable in production environments without royalties or usage restrictions, which distinguishes it from some other open-weight models with more restrictive non-commercial terms.

### Does Gemma 4 31B require an internet connection after download?

No. Once `ollama pull gemma4:31b` completes, the model runs entirely offline. Ollama stores the weights in `~/.ollama/models/` and inference happens locally with no network calls. You can disconnect your machine from the internet and the model continues to work normally.

### Can I run Gemma 4 31B on a CPU without a GPU?

Yes, but it will be very slow. Ollama falls back to CPU inference automatically if no compatible GPU is detected. Expect 1–3 tokens per second on a modern desktop CPU versus 30–60+ tokens per second on an RTX 4090. For practical use, a GPU with at least 20GB VRAM is strongly recommended for the 31B variant.

### What is the difference between Gemma 4 31B and Gemma 4 27B?

There is no official "27B" variant in the Gemma 4 family. The lineup is E2B, E4B, 12B, 26B, and 31B. Some confusion arises because earlier Gemma 2 had a 27B model. Gemma 4 31B is the top-tier dense model in the current release.

### How do I update Gemma 4 to a newer version when Google releases one?

Run `ollama pull gemma4:31b` again. Ollama checks the registry for a newer manifest and downloads only the changed layers if an update is available. You can also use `ollama pull gemma4:latest` to always fetch the most recent Gemma 4 variant automatically.

### Is Gemma 4 31B safe to use in production with real user data?

Gemma 4 31B is Apache 2.0 licensed, so commercial use is permitted without restriction. For production deployments handling sensitive user data, running it locally with Ollama is actually the privacy-correct approach — no data is sent to third-party servers. However, like all language models, it can produce hallucinations and should not be used for safety-critical decisions without human review and output validation.
