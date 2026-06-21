---
cover:
  alt: 'Devstral Small 2 Local Setup Guide 2026: Run Mistral Coding Agent on Your
    Laptop'
  image: /images/devstral-small-2-local-setup-guide-2026.png
  relative: false
date: 2026-04-30 06:04:25+00:00
description: Step-by-step guide to running Devstral Small 2 (24B, 68% SWE-bench) locally
  via Ollama, vLLM, or llama.cpp — zero API fees, full privacy.
draft: false
schema: schema-devstral-small-2-local-setup-guide-2026
tags:
- devstral small 2
- local AI
- mistral
- coding agent
- ollama
- vllm
- llama.cpp
title: 'Devstral Small 2 Local Setup Guide 2026: Run Mistral Coding Agent on Your
  Laptop'
---

Devstral Small 2 is a 24B-parameter coding model from Mistral AI that scores 68% on SWE-bench Verified and runs on a single 24GB GPU or a Mac M-series with 32GB unified memory — making it the first cloud-grade coding agent most developers can realistically self-host. This guide covers three setup paths: Ollama for beginners, vLLM for production teams, and llama.cpp for CPU-only or low-VRAM machines.

## What Is Devstral Small 2?

Devstral Small 2 is Mistral AI's open-weight coding specialist, released December 10, 2025 under the Apache 2.0 license. With 24 billion parameters and a 256K-token context window, it achieves 68.0% on SWE-bench Verified — a real-world benchmark measuring a model's ability to resolve open GitHub issues autonomously. That puts it on par with models up to five times its parameter count, including closed-source proprietary systems. Because it ships under Apache 2.0, you can run it locally with no API fees, no data leaving your machine, and no usage restrictions — even in commercial projects. The model is fine-tuned specifically on agentic coding workflows: reading multi-file codebases, writing patches, running tool calls, and self-correcting from test failures. Devstral Small 2 outperforms Qwen 3 Coder Flash (30B) despite being a smaller model, and its larger sibling Devstral 2 (123B) hits 72.2%, compared to Claude Sonnet 4.5's 77.2% — at up to 7x lower cost per coding task. For teams or individuals who need a capable coding agent without cloud dependency, Devstral Small 2 is the most practical choice available today.

### How Does It Compare to GitHub Copilot?

GitHub Copilot is a cloud-only SaaS product that sends your code to Microsoft/OpenAI servers for every completion. Devstral Small 2 runs entirely on your hardware — no telemetry, no subscription, no code leaving your machine. For developers working with proprietary codebases, HIPAA-sensitive data, or airgapped environments, this distinction is not a preference but a requirement. In terms of raw capability, Devstral Small 2 handles multi-file edits, shell tool use, and autonomous bug-fix loops that Copilot's autocomplete model is not designed for.

## Hardware Requirements — Can Your Laptop Run It?

Devstral Small 2 requires a minimum of 24GB VRAM to run at full precision (FP16) on a discrete GPU, or 32GB unified memory on Apple Silicon Macs. With Q4_K_M quantization — which preserves 95%+ of model quality at 40% reduced memory — you can run it on a single RTX 3090, RTX 4090, or any GPU with 16GB+ VRAM, though performance is faster with 24GB. Apple M1, M2, M3, and M4 chips with 32GB unified memory can run the model without any discrete GPU because macOS treats CPU and GPU memory as a shared pool. Windows and Linux users with 16GB VRAM GPUs should use GGUF quantization via llama.cpp for the best performance-to-memory tradeoff. CPU-only inference is possible but slow — expect 1–3 tokens per second on a modern AMD or Intel machine with 64GB RAM, which is usable for testing but not for interactive coding sessions. The model's 256K context window is memory-hungry: fitting a 128K context requires approximately 20GB VRAM even at Q4. For most local setups, keep context under 32K unless you have 24GB+ VRAM available.

| Hardware | VRAM / RAM | Recommended Method | Speed (est.) |
|---|---|---|---|
| RTX 4090 | 24GB VRAM | Ollama / vLLM | 25–40 tok/s |
| RTX 3090 | 24GB VRAM | Ollama (Q4_K_M) | 15–25 tok/s |
| RTX 4080 | 16GB VRAM | llama.cpp Q4_K_M | 10–18 tok/s |
| Mac M3 Max 96GB | 96GB unified | Ollama (Metal) | 20–35 tok/s |
| Mac M2 Pro 32GB | 32GB unified | Ollama (Metal) | 8–15 tok/s |
| CPU only (64GB RAM) | 64GB RAM | llama.cpp Q4_K_M | 1–3 tok/s |

## Method 1: Ollama Setup (Easiest — 3 Commands)

Ollama is the fastest path to running Devstral Small 2 locally — it handles model download, quantization selection, and an OpenAI-compatible API server in three commands. Install Ollama from the official site for your OS (macOS, Linux, or Windows WSL2), then pull and run the model. No manual CUDA configuration is required; Ollama detects your GPU automatically and selects the appropriate backend. The Q4_K_M quantization variant is used by default for Devstral Small 2 on Ollama, delivering the best balance of speed and quality for consumer hardware. Once the model is running, Ollama exposes a local HTTP server at `localhost:11434` with an OpenAI-compatible `/v1/chat/completions` endpoint, which means any tool that works with OpenAI models — LangChain, LlamaIndex, Continue.dev, OpenHands — can be pointed at your local Devstral instance with a single URL change. The model download is approximately 14GB for the Q4_K_M variant.

```bash
# Step 1: Install Ollama (macOS example)
brew install ollama

# Step 2: Start the Ollama service
ollama serve

# Step 3: Pull and run Devstral Small 2
ollama run devstral-small-2
```

For Linux, replace the brew command with:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Once running, test the API directly:

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "devstral-small-2",
    "messages": [{"role": "user", "content": "Write a Python function to parse a CSV file"}]
  }'
```

### Configure Ollama for Longer Context

By default Ollama caps context at 2048 tokens for memory safety. To unlock the full 256K window (or a practical 32K for most tasks), create a custom Modelfile:

```bash
cat > Modelfile << 'EOF'
FROM devstral-small-2
PARAMETER num_ctx 32768
EOF

ollama create devstral-32k -f Modelfile
ollama run devstral-32k
```

## Method 2: vLLM Server Setup (Production-Grade)

vLLM is the preferred deployment method for teams running Devstral Small 2 as a shared inference server — it offers higher throughput, continuous batching, and PagedAttention memory management that Ollama does not implement. vLLM requires a CUDA-compatible GPU on Linux (Windows is not supported), and Python 3.9+. The setup installs via pip and takes under five minutes once CUDA drivers are configured. vLLM exposes an OpenAI-compatible REST API on port 8000 by default, making it a drop-in replacement for the OpenAI endpoint in any application. For production deployments, vLLM's continuous batching can serve multiple concurrent coding sessions without the memory overhead of spawning separate model instances per request. At 24B parameters with A100-80GB hardware, expect 60–80 tokens per second with batched inference. On a single RTX 4090, expect 25–35 tok/s single-user throughput. vLLM also supports tensor parallelism across multiple GPUs — useful if you have two 16GB cards and want to treat them as 32GB combined.

```bash
# Install vLLM
pip install vllm

# Launch the server (single GPU)
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Devstral-Small-2 \
  --served-model-name devstral-small-2 \
  --port 8000 \
  --max-model-len 32768

# For tensor parallelism across 2 GPUs:
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Devstral-Small-2 \
  --tensor-parallel-size 2 \
  --max-model-len 65536
```

Test the vLLM server:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "devstral-small-2",
    "messages": [{"role": "user", "content": "Review this Python function for bugs"}]
  }'
```

### Quantization with vLLM

For 16GB VRAM GPUs, add `--dtype float16` and `--gpu-memory-utilization 0.90`:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Devstral-Small-2 \
  --dtype float16 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 16384
```

## Method 3: llama.cpp + GGUF (CPU or Low-VRAM Machines)

llama.cpp with GGUF quantization is the right method when you have less than 16GB VRAM or want to run Devstral Small 2 entirely on CPU. GGUF is a portable model format that supports mixed-precision quantization — different layers use different bit depths — which means the model fits in less memory while preserving most of the accuracy on higher-reasoning tasks. The Q4_K_M quantization variant is the community consensus for best quality-to-size ratio: it reduces the 24B model from ~48GB (FP16) to approximately 14GB, while maintaining 95%+ task accuracy on coding benchmarks. For machines with 8GB VRAM, you can offload 20 layers to GPU and run the rest on CPU (`--n-gpu-layers 20`), which gives 3–8 tok/s — slow but functional. llama.cpp also supports Metal on macOS, making it an alternative to Ollama for Mac users who want more control over layer offloading configuration. Install from source or use a prebuilt binary from the llama.cpp releases page.

```bash
# Build llama.cpp from source (Linux/Mac)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON  # use DGGML_METAL=ON for Mac
cmake --build build --config Release -j$(nproc)

# Download the GGUF file (Q4_K_M recommended)
# From HuggingFace: mistralai/Devstral-Small-2-GGUF
wget https://huggingface.co/mistralai/Devstral-Small-2-GGUF/resolve/main/devstral-small-2-q4_k_m.gguf

# Run inference (GPU offload)
./build/bin/llama-server \
  --model devstral-small-2-q4_k_m.gguf \
  --n-gpu-layers 35 \
  --ctx-size 16384 \
  --port 8080

# CPU-only (no --n-gpu-layers flag)
./build/bin/llama-server \
  --model devstral-small-2-q4_k_m.gguf \
  --ctx-size 8192 \
  --port 8080 \
  --threads $(nproc)
```

### Choose the Right GGUF Quantization

| Variant | File Size | VRAM/RAM | Quality vs FP16 | Best For |
|---|---|---|---|---|
| Q2_K | ~9GB | 12GB | ~85% | Testing only |
| Q4_K_M | ~14GB | 16GB | ~95% | **Recommended** |
| Q5_K_M | ~17GB | 20GB | ~97% | 24GB VRAM systems |
| Q8_0 | ~25GB | 28GB | ~99% | Near-lossless quality |
| F16 | ~48GB | 50GB | 100% | Dedicated A100/H100 |

## Connect to Mistral Vibe CLI for Terminal Coding

Mistral Vibe CLI is Mistral's official terminal-native coding agent — the equivalent of Cursor or Claude Code, but designed to work with local models via any OpenAI-compatible endpoint. Once Devstral Small 2 is running via Ollama or vLLM, you point Vibe CLI at your local server and get a full agentic coding session in your terminal: multi-file edits, shell command execution, test running, and autonomous bug-fix loops — all without leaving the command line or sending code to the cloud. The CLI reads your project directory, maintains a conversation about the codebase, and can autonomously apply patches across multiple files when given a high-level task like "fix all failing tests" or "add OAuth2 to the auth module." This is the closest local equivalent to GitHub Copilot Workspace or Devin for developers who prioritize privacy.

```bash
# Install Mistral Vibe CLI
pip install mistral-vibe

# Configure for local Ollama endpoint
cat > ~/.vibe/config.toml << 'EOF'
[model]
provider = "openai-compatible"
base_url = "http://localhost:11434/v1"
model = "devstral-small-2"
api_key = "ollama"

[agent]
auto_approve = false
max_file_changes = 50
EOF

# Start a coding session
cd /your/project
vibe "Refactor the authentication module to use JWT tokens"
```

For vLLM backend, change `base_url` to `http://localhost:8000/v1`.

### Auto-Approval Mode

For trusted projects where you want fully autonomous operation:

```yaml
[agent]
auto_approve = true
allowed_tools = ["read_file", "write_file", "run_shell"]
denied_tools = ["delete_file", "network_request"]
```

Auto-approval is off by default. Enable it only in isolated dev environments — it will execute shell commands without confirmation.

## Integrate Devstral Small 2 with OpenHands

OpenHands (formerly OpenDevin) is an open-source autonomous software engineering platform that wraps a coding model in a Docker-based sandbox, giving it persistent file access, shell execution, and browser automation. Integrating Devstral Small 2 with OpenHands gives you a self-hosted version of Devin-like autonomous coding — the agent can read your codebase, run tests, browse documentation, write multi-file patches, and iterate until the tests pass, all locally. OpenHands supports any OpenAI-compatible backend, making the Ollama or vLLM integration straightforward. The combination of Devstral Small 2's 68% SWE-bench score with OpenHands's tool execution scaffolding is currently one of the most capable local autonomous coding setups available. Setup requires Docker and about 5 minutes of configuration.

```bash
# Install OpenHands
pip install openhands-ai

# Or run via Docker (recommended)
docker pull ghcr.io/all-hands-ai/openhands:latest

# Launch with local Devstral endpoint
docker run -it \
  -e LLM_API_KEY=ollama \
  -e LLM_BASE_URL=http://host.docker.internal:11434/v1 \
  -e LLM_MODEL=devstral-small-2 \
  -v /your/workspace:/workspace \
  -p 3000:3000 \
  ghcr.io/all-hands-ai/openhands:latest

# Open http://localhost:3000 in your browser
```

For vLLM backend, replace `LLM_BASE_URL` with `http://host.docker.internal:8000/v1`.

### OpenHands Task Examples

Once connected, you can give OpenHands high-level tasks:

- "Add unit tests for all functions in `src/auth/`"
- "Find and fix the memory leak in the websocket handler"
- "Migrate this codebase from Python 2 to Python 3"
- "Implement the GitHub issue #47 according to the spec in SPEC.md"

## Devstral Small 2 vs. Cloud Alternatives: Is Local Worth It?

Running Devstral Small 2 locally is worth it under specific conditions, and not worth it under others — the decision depends on your usage volume, hardware, and privacy requirements. At $0.10/$0.30 per million input/output tokens via the Mistral API, the hosted version is already among the cheapest coding models available, making local deployment a breakeven proposition for casual users who run under a few million tokens per month. But for teams with high token volume, local deployment eliminates per-token costs entirely after the hardware investment. A single RTX 4090 ($1,500–1,800) breaks even against API costs at roughly 5–10 million output tokens — achievable in 2–4 weeks of heavy use. For privacy-sensitive workloads — healthcare software, financial systems, proprietary algorithms — local deployment is not a cost decision but a compliance requirement. The 256K context window also becomes a cost driver at scale: processing a 50K-token codebase context with every request at API prices adds up quickly; locally, it's free.

| Factor | Local (Devstral Small 2) | Cloud (Mistral API) | Cloud (Claude Sonnet 4.5) |
|---|---|---|---|
| SWE-bench Score | 68.0% | 68.0% | 77.2% |
| Cost per 1M output tokens | $0 (after hardware) | $0.30 | ~$15.00 |
| Privacy | 100% on-device | Mistral data policy | Anthropic data policy |
| Context window | 256K | 256K | 200K |
| Setup time | 5–30 min | Instant | Instant |
| Latency | 8–40 tok/s | 50–100 tok/s | 40–80 tok/s |
| Offline capability | Yes | No | No |

Cloud wins on latency and zero setup. Local wins on privacy, cost at scale, and offline operation.

## Troubleshooting Common Setup Issues

Most Devstral Small 2 setup failures fall into four categories: CUDA version mismatch, insufficient VRAM, context length errors, and model format issues. Diagnosing these systematically saves significant time compared to trial-and-error. CUDA mismatches are the most common issue on Linux — Ollama requires CUDA 11.8+ and vLLM requires CUDA 12.1+. Check your driver version with `nvidia-smi` and ensure it supports your installed CUDA toolkit. VRAM errors appear as "CUDA out of memory" exceptions during model loading; the fix is either to reduce `--max-model-len` (for vLLM) or switch to a lower quantization variant. Context length errors during inference mean your prompt exceeds the configured `num_ctx` (Ollama) or `--max-model-len` (vLLM) — increase these parameters or reduce your prompt size. On macOS, model download stalls are often caused by Ollama's background service not starting; run `ollama serve` explicitly in a terminal and check for permission errors in `~/.ollama/logs/`.

**Issue: "CUDA out of memory" on model load**
```bash
# Check actual VRAM usage
nvidia-smi --query-gpu=memory.used,memory.free --format=csv

# vLLM: reduce model length
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Devstral-Small-2 \
  --max-model-len 8192  # reduce from default

# Ollama: use smaller quantization
ollama pull devstral-small-2:q4_0  # smaller than q4_k_m
```

**Issue: Ollama not detecting GPU on Linux**
```bash
# Verify CUDA driver
nvidia-smi
# Check Ollama GPU detection
ollama run devstral-small-2 --verbose 2>&1 | grep -i gpu
# Reinstall with GPU support
curl -fsSL https://ollama.com/install.sh | sh
```

**Issue: Slow inference on Mac (< 5 tok/s)**
```bash
# Ensure Metal is enabled (should be automatic)
# Check if running CPU fallback
ollama run devstral-small-2 --verbose 2>&1 | grep -i metal
# Increase num_ctx to use Metal more efficiently
ollama run devstral-small-2 --num-ctx 8192
```

**Issue: vLLM tokenizer error on Devstral Small 2**
```bash
# Install correct tokenizer dependencies
pip install transformers>=4.40.0 sentencepiece
# Use trust_remote_code flag
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Devstral-Small-2 \
  --trust-remote-code
```

## FAQ

**Can Devstral Small 2 run on a laptop with 16GB RAM and no dedicated GPU?**
Yes, but slowly. Using llama.cpp with Q4_K_M quantization and a context of 4096 tokens, expect 0.5–2 tokens per second on a modern CPU. This is functional for testing or occasional queries but too slow for interactive coding sessions. A Mac with 32GB unified memory is significantly better than a PC with 16GB system RAM and no discrete GPU — the Mac's memory bandwidth is purpose-built for this workload.

**Is the Apache 2.0 license really free for commercial use?**
Yes. Apache 2.0 permits use, modification, and distribution in commercial software without royalties or attribution requirements beyond including the license file. There are no "non-commercial only" restrictions. You can embed Devstral Small 2 in a product, use it internally in a company, or sell a service built on it — all without contacting Mistral.

**How does Devstral Small 2 handle multi-file edits?**
Devstral Small 2 is fine-tuned specifically for agentic tool use, including multi-file read/write operations. When connected to a tool-calling harness (Vibe CLI, OpenHands, or a custom agent), it can read multiple files into context, reason about dependencies, and output structured patches for each file. Without a tool harness, it's a standard chat model that requires you to paste file contents manually.

**What context length should I use for everyday coding tasks?**
For most coding tasks — reviewing a function, writing a new module, fixing a bug — 8K–16K tokens is sufficient. The 256K window is most valuable for large refactors where you need to hold an entire codebase in context simultaneously. Using large context windows increases memory usage and inference latency, so set `num_ctx` to the minimum needed for your actual task.

**Can I fine-tune Devstral Small 2 on my own codebase?**
Yes, under Apache 2.0 you have full rights to fine-tune the model. The recommended path is QLoRA fine-tuning via Unsloth or Axolotl — both support the Devstral Small 2 architecture and can run fine-tuning on a single 24GB GPU. A small dataset of 500–2,000 examples from your codebase is typically enough to meaningfully improve performance on domain-specific patterns. Unsloth's GGUF export pipeline lets you convert the fine-tuned model back to llama.cpp format for local deployment.