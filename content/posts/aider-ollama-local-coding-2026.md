---
cover:
  alt: 'Aider + Ollama Local Coding Setup 2026: Free AI Pair Programming Offline'
  image: /images/aider-ollama-local-coding-2026.png
  relative: false
date: 2026-04-23 01:15:20+00:00
description: Complete setup guide for Aider + Ollama local AI pair programming — zero
  API costs, full privacy, works offline in 2026.
draft: false
schema: schema-aider-ollama-local-coding-2026
tags:
- aider
- ollama
- local-llm
- ai-coding
- open-source
title: 'Aider + Ollama Local Coding Setup 2026: Free AI Pair Programming Offline'
---

Aider + Ollama gives you a fully local AI pair programmer that costs nothing to run, sends zero code to any cloud, and works completely offline — set it up once and you have a private coding assistant running on your own hardware.

## Why Local AI Coding Matters in 2026

Local AI coding matters in 2026 because the economics and privacy calculus have fundamentally shifted. Stack Overflow's 2025 developer survey found that 84% of developers use or plan to use AI coding tools, with 51% using them daily — but cloud AI subscriptions add up fast. GitHub Copilot runs $10–19/month per seat; Claude API costs $15–75 per million tokens at the high end. For teams or solo developers processing large codebases, those costs compound quickly. Meanwhile, 91% AI adoption across 135,000+ developers in active repos (DX Q4 2025) means organizations are scrutinizing what code actually leaves their networks. Financial services, healthcare, and defense contractors operate under strict data residency rules that make cloud AI assistants a compliance liability. Local models eliminate both problems simultaneously: the API bill drops to zero, and proprietary code never touches an external server. The AI code assistant market hit $3–3.5 billion in 2025 (Gartner), which means the tooling to run serious models locally has matured — Ollama now supports 100+ models, and quantized 7B parameter models run comfortably on a 16GB RAM MacBook M-series chip.

## What Is Aider? The Open-Source AI Pair Programmer

Aider is an open-source AI coding CLI with 39,000+ GitHub stars, 4.1 million installs, and 15 billion tokens processed per week — making it the most widely used open-source AI coding tool in the category. Unlike AI chat interfaces where you paste code, ask a question, and manually apply the response, Aider integrates directly with your Git repository. It reads your files, makes targeted edits, commits changes with descriptive messages, and lets you undo anything with a single command. The key architectural distinction is that Aider treats your codebase as a workspace, not a conversation. You add files to its context with `/add`, describe what you want changed, and it writes and commits the diff. This Git-aware workflow means you always have a clean audit trail, and rollbacks are trivial. Aider works with any LLM that exposes an OpenAI-compatible API — which is exactly what Ollama provides. That compatibility is the bridge that makes the entire local stack possible without any special plugins or forks.

## What Is Ollama? Your Local AI Model Runtime

Ollama is a local inference runtime that lets you download, manage, and serve large language models on your own hardware via an OpenAI-compatible REST API. It runs on macOS (Apple Silicon and Intel), Linux, and Windows, and handles the complexity of model quantization, GPU offloading, and memory management behind a simple CLI. When you run `ollama pull deepseek-coder:6.7b`, Ollama downloads a quantized version of the model, manages VRAM allocation automatically, and starts serving it at `http://127.0.0.1:11434` with an API that looks identical to OpenAI's `/v1/chat/completions` endpoint. This OpenAI compatibility layer is what makes Ollama the ideal backend for Aider — no custom integration needed. Ollama currently supports 100+ models, including all major coding-focused models: DeepSeek Coder, Qwen 2.5 Coder, CodeLlama, Mistral, and more. For coding tasks specifically, quantized 6.7B–7B models run on 16GB unified memory at 10–30 tokens/second on Apple M-series hardware, which is genuinely fast enough for an interactive pair programming workflow.

## Hardware Requirements: What You Need to Run Local Coding AI

Running local AI coding requires at minimum 16GB RAM for 7B parameter models, though 32GB opens up 13B+ models that produce meaningfully better code. A dedicated GPU dramatically improves token generation speed — NVIDIA GPUs with 8GB+ VRAM (RTX 3070, 4070, etc.) or Apple Silicon M-series chips with unified memory are the sweet spots for consumer hardware in 2026. Without GPU acceleration, inference falls back to CPU, which is usable for small models but slow (3–8 tokens/second on a modern laptop CPU versus 15–40+ tokens/second with GPU offloading). Storage is also a factor: a 4-bit quantized 7B model takes roughly 4–5GB on disk, a 13B model takes 8–10GB, and a 34B model needs 20GB+. For most developers starting out, a machine with 16GB RAM and any Apple M-series chip or NVIDIA GPU with 8GB+ VRAM is the practical entry point. Intel Arc and AMD Radeon GPUs work with Ollama but with more configuration friction.

| Hardware | Viable Models | Speed Estimate | Use Case |
|----------|--------------|----------------|----------|
| 16GB RAM, Apple M1/M2/M3 | 7B–13B (Q4) | 15–30 tok/s | Daily pair programming |
| 32GB RAM, Apple M2 Pro/Max | 13B–34B (Q4) | 20–40 tok/s | Complex refactoring |
| 16GB RAM + NVIDIA RTX 3070 8GB | 7B–13B (Q4) | 20–50 tok/s | Fast iteration |
| 32GB RAM + RTX 4090 24GB | 34B–70B (Q4) | 30–70 tok/s | Near-cloud quality |
| 16GB RAM, CPU only | 3B–7B (Q4) | 3–8 tok/s | Light edits only |

## Step 1: Installing Ollama

Installing Ollama is the fastest part of the entire setup — the process takes under two minutes on any supported platform, and the installer handles GPU driver detection automatically. Ollama runs as a background server that listens on port 11434 and exposes an OpenAI-compatible REST API. Once running, you interact with it via the `ollama` CLI to pull and manage models, or via HTTP requests from any tool (like Aider) that supports the OpenAI API format. Ollama supports macOS (Apple Silicon and Intel x86), Linux (Ubuntu, Debian, Fedora, Arch, and most others), and Windows 10/11. On Linux, the install script auto-detects NVIDIA CUDA and AMD ROCm drivers and links the appropriate GPU backend — you don't need to configure GPU acceleration manually. On macOS with Apple Silicon, GPU inference via Metal is enabled by default with no extra steps. The server starts automatically on install and can be verified with `curl http://localhost:11434` — you should see `"Ollama is running"` in the response.

### macOS Installation

Installing Ollama on macOS takes under two minutes. Download the installer from [ollama.com](https://ollama.com), open the `.dmg`, and drag it to Applications. Ollama runs as a menu bar app and starts the server automatically. Alternatively, install via Homebrew: `brew install ollama`. Once installed, the server is accessible at `http://127.0.0.1:11434` immediately.

### Linux Installation

On Linux, a single curl command handles everything:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This script detects your GPU driver (CUDA for NVIDIA, ROCm for AMD), installs the appropriate runtime, and registers Ollama as a systemd service. Start it manually with `ollama serve` or let systemd manage it. Verify the server is running: `curl http://localhost:11434` should return `"Ollama is running"`.

### Windows Installation

Download the Windows installer from [ollama.com](https://ollama.com) and run the `.exe`. Ollama adds itself to the system tray and starts automatically. For WSL2 users, install Ollama natively in Windows (not inside WSL) to get GPU access, then point Aider at `http://host.docker.internal:11434` from inside WSL.

## Step 2: Choosing and Pulling Your First Coding Model

Choosing the right local coding model is the single decision that most affects your experience with Aider + Ollama, because model quality and hardware requirements are tightly coupled. In 2026, the landscape has consolidated around three serious contenders: Qwen 2.5 Coder (Alibaba Cloud), DeepSeek Coder (DeepSeek AI), and CodeLlama (Meta). For most developers starting out on 16GB RAM machines, `qwen2.5-coder:7b` is the best all-around choice — it scores 79.7% on HumanEval, outperforms DeepSeek Coder 6.7B on most coding benchmarks, and handles Python, JavaScript, TypeScript, Go, and Rust with equal competence. The `q4_K_M` quantization format (4-bit quantization, K-means optimized) offers the best quality-to-size tradeoff: it reduces a model from 13–16GB (full precision) to 4–5GB while retaining 95%+ of benchmark performance. Pulling a model downloads it to `~/.ollama/models/` and Ollama serves it automatically on next request. You can have multiple models downloaded and switch between them without restarting Ollama — just change the model name in your Aider command.

```bash
ollama pull qwen2.5-coder:7b
```

For a full comparison to help you decide:

## Model Comparison: DeepSeek Coder vs Qwen 2.5 Coder vs CodeLlama

Choosing between local coding models in 2026 comes down to three serious contenders: Qwen 2.5 Coder, DeepSeek Coder, and CodeLlama — each with distinct strengths. Qwen 2.5 Coder 7B, released by Alibaba Cloud, scores 79.7 on HumanEval and excels at multi-language completion and instruction following, making it the best general-purpose option for Aider workflows. DeepSeek Coder 6.7B (the `6.7b-instruct-q4_K_M` variant) has been the community favorite for Aider + Ollama setups since 2024 — it's well-tested with Aider's prompting style and produces clean, editable diffs. CodeLlama 7B (Meta) is the most widely supported but has fallen behind on benchmarks; it's still useful as a fallback for specific tasks or when you need the widest community documentation. For 13B+ models, Qwen 2.5 Coder 14B and DeepSeek Coder 33B are genuinely impressive if your hardware supports them.

| Model | Size (disk) | RAM Required | HumanEval | Best For |
|-------|-------------|--------------|-----------|----------|
| `qwen2.5-coder:7b` | ~4.7GB | 8GB VRAM / 16GB RAM | 79.7% | General coding, multi-language |
| `qwen2.5-coder:14b` | ~9GB | 16GB VRAM / 32GB RAM | 86.1% | Complex refactoring |
| `deepseek-coder:6.7b-instruct-q4_K_M` | ~4.1GB | 8GB VRAM / 16GB RAM | 72.6% | Aider-tested, stable diffs |
| `codellama:7b` | ~3.8GB | 8GB VRAM / 16GB RAM | 53.7% | Legacy support, wide docs |
| `deepseek-coder:33b-instruct-q4_K_M` | ~20GB | 24GB VRAM / 48GB RAM | 81.1% | Near-cloud quality |

Pull the model that matches your hardware:

```bash
# Recommended for most users
ollama pull qwen2.5-coder:7b

# Battle-tested Aider community favorite
ollama pull deepseek-coder:6.7b-instruct-q4_K_M

# High-end machines
ollama pull qwen2.5-coder:14b
```

## Step 3: Installing Aider

Aider installs via pip as the `aider-chat` package, but there is one critical prerequisite: Python version. Aider has documented compatibility issues with Python 3.13 as of early 2026 due to breaking changes in several upstream dependencies. Before installing, verify you're running Python 3.12 with `python3 --version`. If you're on 3.13, the fastest fix is pyenv — install Python 3.12, create a virtual environment, and install Aider inside it. This isolation also prevents Aider's dependencies from conflicting with other Python projects on your machine. The `aider-chat` package includes everything needed: the CLI tool, the OpenAI-compatible API client, Git integration libraries, and the syntax highlighting and diff display tools that make Aider's terminal output readable. On macOS, Homebrew's `brew install aider` formula is an alternative that handles the Python dependency automatically. On Linux, the pip path inside a virtual environment is more reliable. Post-install, run `aider --version` to confirm the install succeeded and check `aider --help` to see all available flags — particularly `--model`, `--no-show-model-warnings`, and `--yes`, which you'll use in every Ollama session.

```bash
# Check Python version
python3 --version  # Should be 3.12.x

# Install Aider
pip install aider-chat

# Verify installation
aider --version
```

For users on macOS with Homebrew, `brew install aider` is an alternative that manages the Python dependency for you. On Linux, a virtual environment is recommended to keep Aider's dependencies isolated:

```bash
python3.12 -m venv ~/.venv/aider
source ~/.venv/aider/bin/activate
pip install aider-chat
```

## Step 4: Connecting Aider to Ollama

Connecting Aider to Ollama requires setting one environment variable and specifying the model in your launch command. Ollama's API is OpenAI-compatible, so Aider uses its OpenAI provider with a custom base URL pointing to your local server.

```bash
# Set the API base URL (add to ~/.bashrc or ~/.zshrc for persistence)
export OLLAMA_API_BASE=http://127.0.0.1:11434

# Launch Aider with Qwen 2.5 Coder
aider --model ollama_chat/qwen2.5-coder:7b --no-show-model-warnings

# Or with DeepSeek Coder
aider --model ollama_chat/deepseek-coder:6.7b-instruct-q4_K_M --no-show-model-warnings
```

The `ollama_chat/` prefix tells Aider to use the chat completions endpoint rather than the completion endpoint — this is important for instruction-following models. The `--no-show-model-warnings` flag suppresses warnings about Ollama models not being in Aider's default model list, which is expected and harmless. Add `--yes` to auto-confirm all file edits during initial testing.

For a persistent setup, create an `.aider.conf.yml` in your home directory or project root:

```yaml
# ~/.aider.conf.yml
model: ollama_chat/qwen2.5-coder:7b
no-show-model-warnings: true
```

## Step 5: Your First Local AI Pair Programming Session

Starting your first local AI pair programming session with Aider + Ollama takes about 30 seconds once both are installed. Navigate to your project directory, start Aider, add the files you want to work on, and describe the change you want — Aider handles the rest, including writing, applying, and committing the diff.

```bash
# Navigate to your project
cd ~/my-project

# Start Aider
aider --model ollama_chat/qwen2.5-coder:7b --no-show-model-warnings

# Inside the Aider session:
# Add files to context
> /add src/main.py src/utils.py

# Describe what you want
> Refactor the parse_config function to use dataclasses instead of dicts

# Aider reads the files, generates a diff, shows it to you, asks to apply
# Type 'y' to apply and auto-commit
```

The workflow feels different from AI chat because you're never copying and pasting code. Aider writes directly to your files and creates a Git commit automatically. If the result isn't right, `/undo` reverts the commit and you can try again with a clearer prompt.

## Essential Aider Commands and Workflow Tips

Aider's most useful commands for day-to-day local pair programming cover context management, code inspection, and session control. Mastering these commands is what separates developers who get 20% productivity gains from those who get 55%+ (the figure GitHub Research found with heavy AI tool users). The commands below cover the full workflow cycle from adding files through reviewing changes.

| Command | What It Does |
|---------|-------------|
| `/add <file>` | Add file(s) to Aider's context |
| `/drop <file>` | Remove file from context (save tokens) |
| `/diff` | Show the last diff Aider made |
| `/undo` | Revert the last commit Aider made |
| `/run <cmd>` | Run a shell command and show output to Aider |
| `/clear` | Clear conversation history (keeps files in context) |
| `/help` | Show all available commands |
| `/ls` | List files currently in context |
| `/git <args>` | Run git commands from within Aider |
| `/ask <question>` | Ask a question without making any changes |

**Workflow tip:** Keep context tight. Local models have smaller effective context windows than cloud models, so add only the files directly relevant to the current task. Start a new Aider session for each discrete task rather than letting context accumulate across unrelated changes.

## Performance Tuning: Ollama Environment Variables for Speed

Ollama's performance on consumer hardware depends heavily on a handful of environment variables that control parallelism, memory, and GPU utilization. Setting these correctly can double effective throughput for single-user interactive coding sessions.

```bash
# For single-user interactive use (reduces overhead)
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1

# GPU layers (higher = more GPU, less CPU)
# Set to a high number to push as much as possible to GPU
export OLLAMA_NUM_GPU=99  # Ollama caps at available GPU layers

# For NVIDIA: check if GPU is being used
nvidia-smi  # Should show ollama process with VRAM usage

# For Apple Silicon: GPU is used by default via Metal
# Check with: ollama ps
```

Setting `OLLAMA_NUM_PARALLEL=1` is counterintuitive but correct for interactive use — it tells Ollama to handle one request at a time, which reduces memory fragmentation and improves latency for the single user. `OLLAMA_MAX_LOADED_MODELS=1` ensures only one model is loaded in memory, freeing VRAM for the active model. If you have 24GB+ VRAM and want to experiment with larger models, bump `OLLAMA_MAX_LOADED_MODELS=2` to allow hot-swapping.

Add these to your shell profile (`~/.bashrc` or `~/.zshrc`) for persistence:

```bash
echo 'export OLLAMA_NUM_PARALLEL=1' >> ~/.zshrc
echo 'export OLLAMA_MAX_LOADED_MODELS=1' >> ~/.zshrc
echo 'export OLLAMA_API_BASE=http://127.0.0.1:11434' >> ~/.zshrc
source ~/.zshrc
```

## Troubleshooting Common Setup Issues

The three most common Aider + Ollama setup failures are Python version conflicts, out-of-memory crashes, and GPU detection misses — each with a straightforward fix. Python 3.13 breaks several of Aider's dependencies as of Q1 2026; the fix is to install Python 3.12 via pyenv and create a dedicated virtual environment. If Ollama crashes mid-generation with `killed` or `signal: killed`, your model is too large for available RAM or VRAM — switch to a smaller quantization (`q4_K_M` instead of `f16`) or a smaller parameter count. If you're on NVIDIA and Ollama is only using CPU, verify your CUDA drivers are installed: `nvidia-smi` should show your GPU, and `ollama ps` should show GPU layers > 0 when a model is loaded.

**Python 3.13 fix:**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.9
pyenv global 3.12.9

# Reinstall Aider
pip install aider-chat
```

**Out-of-memory fix:**
```bash
# Pull a smaller quantization
ollama pull deepseek-coder:6.7b-instruct-q4_K_M  # ~4.1GB
# Instead of
ollama pull deepseek-coder:6.7b-instruct  # ~13GB fp16
```

**GPU not detected (NVIDIA):**
```bash
# Verify CUDA
nvidia-smi
nvcc --version

# Reinstall Ollama after verifying CUDA
curl -fsSL https://ollama.com/install.sh | sh

# Check model is using GPU
ollama ps  # Should show non-zero GPU% after loading a model
```

**Aider model not found error:**
```bash
# Use the correct prefix for Ollama models
# Wrong:
aider --model deepseek-coder:6.7b-instruct-q4_K_M

# Correct:
aider --model ollama_chat/deepseek-coder:6.7b-instruct-q4_K_M
```

## When Local Beats Cloud: Use Cases for Offline AI Coding

Local AI coding genuinely outperforms cloud alternatives in four specific scenarios: regulated environments, proprietary codebases, high-volume automation, and offline or air-gapped development. In regulated industries — finance, healthcare, government — sending source code to a third-party API creates data governance problems that legal teams often can't approve. A local Aider + Ollama stack keeps all code on-premises with zero egress. For high-volume use cases like CI/CD code review automation or batch refactoring across thousands of files, cloud API costs scale linearly with tokens; local inference scales with hardware you already own. Offline development — on aircraft, in disconnected environments, or in air-gapped security networks — is simply impossible with cloud-only tools. Finally, for developers who've crossed the $50–100/month threshold on cloud AI APIs, even mid-tier hardware (a used RTX 3090 for ~$400) pays for itself in under six months at current cloud pricing. The tradeoff is real though: today's best local 7B model produces code roughly equivalent to GPT-3.5, not GPT-4o. For complex architectural decisions and cross-file refactoring at scale, cloud models still lead. The practical answer for most teams is hybrid: local for routine edits and high-volume tasks, cloud for hard problems.

---

## FAQ

**Does Aider + Ollama work completely offline?**
Yes. Once you've pulled a model with `ollama pull`, Ollama serves it locally with no internet connection required. Aider connects to `http://127.0.0.1:11434` — your own machine. The entire stack runs air-gapped after the initial download.

**Which Ollama model is best for Aider in 2026?**
`qwen2.5-coder:7b` is the best general-purpose choice for 16GB RAM machines in 2026, scoring 79.7% on HumanEval. For machines with 32GB RAM or 16GB VRAM, `qwen2.5-coder:14b` is noticeably better. The `deepseek-coder:6.7b-instruct-q4_K_M` model remains the most battle-tested specifically with Aider's prompting style.

**How does Aider + Ollama compare to GitHub Copilot or Claude Code?**
Cloud tools like Claude Code and Copilot use GPT-4o/Claude-class models that are significantly stronger at complex reasoning and cross-file refactoring. Local setups win on cost (zero ongoing API fees), privacy (no code leaves your machine), and offline availability. For routine edits, autocomplete, and simple refactoring, local 7B models are genuinely productive. For hard architectural problems, cloud models still lead.

**What Python version should I use for Aider?**
Use Python 3.12. Aider has documented compatibility issues with Python 3.13 as of early 2026 due to dependency conflicts. Install Python 3.12 via pyenv (`pyenv install 3.12.9`) and create a dedicated virtual environment to isolate Aider's dependencies.

**Can I use Aider + Ollama on Windows?**
Yes. Install Ollama via the Windows installer from ollama.com, then install Aider via pip in a Python 3.12 environment. WSL2 users should install Ollama natively in Windows (not in WSL) to get GPU access, and connect to it from WSL using `http://host.docker.internal:11434` as the API base instead of `127.0.0.1`.