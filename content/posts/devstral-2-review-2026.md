---
cover:
  alt: 'Devstral 2 Review 2026: Mistral''s Open-Source Coding Agent Hits 72.2% SWE-bench'
  image: /images/devstral-2-review-2026.png
  relative: false
date: 2026-04-29 18:14:43+00:00
description: Devstral 2 achieves 72.2% on SWE-bench Verified at $0.40/M tokens — the
  most capable open-weight coding model in 2026. Full review with benchmarks.
draft: false
schema: schema-devstral-2-review-2026
tags:
- devstral-2
- mistral
- open-source-ai
- coding-agents
- swe-bench
title: 'Devstral 2 Review 2026: Mistral''s Open-Source Coding Agent Hits 72.2% SWE-bench'
---

Devstral 2 is Mistral AI's most capable open-weight coding model, achieving 72.2% on SWE-bench Verified — the highest score ever recorded by an open-source model at its parameter count. Released in late 2025 alongside the Mistral Vibe CLI, it costs $0.40 per million input tokens, making it up to 7x cheaper than Claude Sonnet for typical coding workloads.

## What Is Devstral 2? Overview of Mistral's Latest Open-Source Coding Agent

Devstral 2 is a 123-billion parameter open-weight large language model purpose-built for agentic software engineering tasks — it can autonomously navigate codebases, edit multiple files, run tools, and resolve GitHub issues end-to-end. Released by Mistral AI in December 2025, it achieves 72.2% on SWE-bench Verified (the industry-standard benchmark for autonomous bug-fixing), placing it at the frontier of all open-weight models and ahead of significantly larger competitors including DeepSeek V3.2 (672B) and Kimi K2 (1T). Unlike most frontier coding models, Devstral 2 is released under the Apache 2.0 license, meaning developers can download, self-host, fine-tune, and deploy it commercially without restriction. In human evaluations against DeepSeek V3.2, Devstral 2 wins 42.8% of coding tasks versus a 28.6% loss rate — a meaningful real-world advantage that SWE-bench alone doesn't fully capture. The model supports a 256K-token context window, enabling comprehension of entire repositories in a single pass. For teams that need frontier-grade coding intelligence without proprietary lock-in, Devstral 2 is the clearest option available in 2026.

### Released Alongside the Mistral Vibe CLI

Devstral 2 launched simultaneously with Mistral Vibe CLI, an open-source command-line coding assistant comparable to Claude Code or Aider. The CLI is designed to use Devstral 2 as its native model, providing an out-of-the-box agentic coding workflow without needing an IDE plugin or third-party orchestration layer. The Agent Communication Protocol (ACP) integration means Devstral 2 can participate in multi-agent pipelines alongside models from other providers.

## Devstral 2 vs Devstral Small 2: Which Model Should You Use?

Devstral 2 and Devstral Small 2 are complementary models targeting different deployment contexts — one prioritizes maximum capability, the other optimizes for local hardware constraints. Devstral 2 (123B parameters) achieves 72.2% on SWE-bench Verified and is recommended for cloud API usage, CI/CD pipelines, and complex multi-file architectural tasks. Devstral Small 2 (24B parameters) achieves 68.0% on SWE-bench Verified — a 4.2-point gap that closes significantly in everyday coding tasks — and runs comfortably on a 32GB MacBook Pro or a single RTX 4090 GPU. Both models use a dense transformer architecture rather than mixture-of-experts (MoE), which matters for latency and memory footprint at inference time. Devstral Small 2 costs $0.10/$0.30 per million tokens (input/output), making it dramatically cheaper than any proprietary alternative for teams willing to trade a modest capability ceiling for local control and zero data egress.

| Model | Parameters | SWE-bench | Input Price | Output Price | Context |
|---|---|---|---|---|---|
| Devstral 2 | 123B | 72.2% | $0.40/M | $2.00/M | 256K |
| Devstral Small 2 | 24B | 68.0% | $0.10/M | $0.30/M | 256K |

**When to choose Devstral 2:** Complex refactors, cross-file reasoning, production CI/CD, multi-agent pipelines requiring maximum accuracy.

**When to choose Devstral Small 2:** Local development, privacy-sensitive codebases, cost-constrained projects, and open-source teams where Apache 2.0 self-hosting is the primary concern.

## SWE-bench 72.2%: How Devstral 2 Ranks Against Other Coding Models in 2026

SWE-bench Verified is the standard benchmark for autonomous coding agents — it measures a model's ability to resolve real GitHub issues from popular Python repositories without human guidance. A score of 72.2% means Devstral 2 successfully fixes 72 out of every 100 real bug reports it encounters, placing it at the frontier of all open-weight models. As of April 2026, only a handful of proprietary models outperform it: Grok 4 leads at 75%, followed by GPT-5.4 at 74.9%, and Claude Opus 4.6 at 74%+. The critical context is parameter efficiency — Devstral 2 achieves this with 123B all-active parameters, while DeepSeek V3.2 (671B) and Kimi K2 (1T sparse) require 5x and 8x more compute respectively to reach comparable numbers. For teams self-hosting open-weight models, Devstral 2's combination of score and hardware footprint is unmatched in 2026.

| Model | SWE-bench | Type | Approx. Parameters |
|---|---|---|---|
| Grok 4 | 75.0% | Proprietary | Unknown |
| GPT-5.4 | 74.9% | Proprietary | Unknown |
| Claude Opus 4.6 | 74%+ | Proprietary | Unknown |
| **Devstral 2** | **72.2%** | **Open-weight** | **123B dense** |
| Devstral Small 2 | 68.0% | Open-weight | 24B dense |
| DeepSeek V3.2 | ~68% | Open-weight | 671B MoE |
| Kimi K2 | ~67% | Open-weight | 1T MoE |

The benchmark gap between Devstral 2 and the top proprietary models is roughly 2-3 points — within the margin where engineering workflow choices (prompt quality, retry logic, context management) can compensate.

## Architecture Deep Dive: Why 123B Dense Beats Larger MoE Models for Coding

Devstral 2 uses a dense transformer architecture where all 123 billion parameters are active on every forward pass — contrasted with mixture-of-experts (MoE) architectures like DeepSeek V3.2 (671B total, ~37B active) and Kimi K2 (1T total, ~32B active), which route each token through only a small subset of parameters. For coding tasks specifically, this matters in three ways: dense models exhibit stronger cross-token coherence across long contexts, reducing errors in multi-file edits where understanding requires integrating signals from thousands of lines simultaneously; dense models run faster per meaningful compute unit (Devstral 2 delivers 71 tokens/second versus a 63 tok/s average for comparable models); and dense models have a smaller hardware footprint for their effective capability, making 2×80GB A100 self-hosting feasible where the apparent size of MoE competitors would suggest far larger requirements. Mistral's Artificial Analysis Intelligence Index score for Devstral 2 is 22, well above the 13 average for models in its tier — a composite metric that factors in code, reasoning, and instruction-following quality simultaneously.

### Why Larger MoE Isn't Always Better for Repo Tasks

MoE models scale parameter counts cheaply but can underperform on tasks requiring tight long-range dependency tracking across a repository. A 1T MoE model activating 32B parameters per token is effectively competing against Devstral 2's 123B dense activations — and at actual coding tasks, Devstral 2's human-eval win rate of 42.8% vs 28.6% loss against DeepSeek V3.2 demonstrates this gap concretely. For local deployment, the practical memory requirement of Devstral Small 2 (24B dense, approximately 48GB quantized to 4-bit) fits a single high-end consumer GPU where an equivalent MoE model at nominally similar active parameters would require more VRAM due to sparse activation overhead.

## Mistral Vibe CLI: Getting Started with Devstral 2's Native Coding Agent

Mistral Vibe CLI is an open-source, terminal-based coding assistant — the Mistral-native equivalent of Claude Code or Aider — that ships with Devstral 2 as its default model and provides an autonomous agentic loop for software development tasks. Rated 7.5/10 by AwesomeAgents in independent testing, it performs excellently on well-defined tasks: adding unit tests, refactoring functions, fixing linter errors, and implementing specified features. Installation takes under two minutes: `pip install mistral-vibe-cli` and `export MISTRAL_API_KEY=your_key`, then `vibe init` in any project directory. The CLI uses Devstral 2's 256K context window to load entire repository structures before making edits, providing coherent multi-file changes rather than isolated hunks. For teams currently paying for Claude Code ($20+/month per developer plus token costs), Vibe CLI's API pricing ($0.40/$2.00 per million tokens) can reduce per-developer costs by 60–80% on typical workloads.

### Installation and First Use

```bash
pip install mistral-vibe-cli
export MISTRAL_API_KEY=your_key_here
cd your-project
vibe init
vibe "Add integration tests for the payment service"
```

The CLI supports slash commands for common workflows (`/fix`, `/test`, `/refactor`), integrates with git for automatic branch creation, and includes a `--model devstral-small-2` flag for switching to the lighter model mid-session.

## Devstral 2 Pricing & API: Cost Breakdown vs Claude, GPT, and DeepSeek

Devstral 2's API pricing is $0.40 per million input tokens and $2.00 per million output tokens — among the most competitive rates for frontier-tier coding models and up to 7x cheaper than Claude Sonnet for real-world development tasks. Devstral Small 2 pushes further to $0.10/$0.30 per million tokens, undercutting virtually every hosted alternative. At launch, both models are offered free during the introductory period via api.mistral.ai, making this an optimal time to evaluate them in production workflows. For a team running 100 CI pipeline coding jobs per day at an average of 50K tokens each (input + output combined), Devstral 2 costs approximately $40/day versus roughly $250/day for an equivalent Claude Sonnet workload — a $77,000 annual difference at scale. The Apache 2.0 self-hosted option via Ollama or vLLM eliminates per-token costs entirely for teams with existing GPU infrastructure.

| Model | Input (per M tokens) | Output (per M tokens) | vs Claude Sonnet |
|---|---|---|---|
| Claude Sonnet 4.5 | ~$3.00 | ~$15.00 | baseline |
| GPT-4.1 | ~$2.00 | ~$8.00 | ~2x cheaper |
| DeepSeek V3.2 | $0.27 | $1.10 | ~7x cheaper |
| **Devstral 2** | **$0.40** | **$2.00** | **~7x cheaper** |
| Devstral Small 2 | $0.10 | $0.30 | ~25x cheaper |

*Pricing as of April 2026. Free tier available at launch.*

## Local Deployment Guide: Running Devstral Small 2 on Your Own Hardware

Devstral Small 2 can run locally on a 32GB Apple Silicon Mac (M2 Pro/Max or later) or a single NVIDIA RTX 4090 (24GB VRAM) using 4-bit quantization via Ollama or llama.cpp — making it the most capable locally-deployable coding agent at any price point in 2026. The Apache 2.0 license means there are no usage restrictions: you can run it in air-gapped environments, fine-tune it on proprietary codebases, and embed it in commercial products without royalties or API dependency. At 4-bit quantization, Devstral Small 2 requires approximately 14GB of VRAM, comfortably fitting on consumer hardware and leaving room for parallel inference. For Devstral 2 (123B), you need 4×80GB A100s or equivalent, making it an enterprise self-hosting proposition ideal for teams with existing GPU clusters. Both models are available on HuggingFace under `mistralai/Devstral-Small-2` and `mistralai/Devstral-2`, and support the standard llama.cpp GGUF format for broad compatibility. With zero per-token costs and full data privacy, self-hosted Devstral Small 2 is the strongest argument for open-weight models in 2026.

### Ollama Quick Start

```bash
# Install Ollama (macOS)
brew install ollama

# Pull and run Devstral Small 2
ollama pull devstral-small:24b
ollama run devstral-small:24b

# Or use with Open WebUI for a browser interface
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  ghcr.io/open-webui/open-webui:main
```

For vLLM production deployments, Devstral Small 2 supports continuous batching and achieves throughput sufficient for small team concurrent usage on 2×A10G instances.

## Real-World Performance: What Devstral 2 Handles Well (and Where It Falls Short)

In real-world agentic coding workflows, Devstral 2 consistently excels at well-scoped tasks where the goal is unambiguous and the codebase context is sufficient to resolve it — and shows measurable limitations on tasks requiring high-level architectural reasoning across many files simultaneously. Based on independent testing and published reviews, Devstral 2 performs best on: adding or refactoring unit/integration tests, fixing linter errors and type annotation issues, implementing specified features with clear interface contracts, resolving GitHub issues where the root cause is identifiable within a few files, and writing boilerplate (API clients, data models, configuration parsers). The 7.5/10 rating from AwesomeAgents reflects a model that is "capable and radically cheaper" but not yet a complete replacement for Claude Code or Cursor on deeply ambiguous architectural tasks.

### Where Devstral 2 Underperforms

- **Complex multi-file architectural changes** with cascading side effects across 20+ files
- **Ambiguous requirements** where the correct interpretation requires business context not in the codebase
- **Long dependency chains** requiring orchestration of more than ~10 sequential tool calls
- **Non-Python/TypeScript ecosystems**: performance on Rust, Go, and Java codebases is less consistent

These limitations are not specific to Devstral 2 — they apply to all current coding agents — but they matter when setting expectations for teams considering replacing proprietary tools.

## Devstral 2 vs Claude Sonnet 4.5 vs DeepSeek V3.2: Which to Choose?

Devstral 2 occupies a distinct position in the 2026 coding model landscape: it is the only model that simultaneously delivers frontier-tier benchmark performance (72.2% SWE-bench), open-weight licensing (Apache 2.0), aggressive pricing ($0.40/M input), and a compact 123B dense parameter footprint suitable for self-hosting. Claude Sonnet 4.5 remains the safer default for teams prioritizing reliability on ambiguous, complex tasks and who don't have cost as a primary concern — it trades 2-3 SWE-bench points for superior instruction-following consistency and a more mature tooling ecosystem. DeepSeek V3.2 offers comparable benchmark scores to Devstral Small 2 at very low API pricing, but its 671B MoE architecture makes self-hosting impractical for most teams, and its China-origin data handling raises compliance questions for some enterprise contexts.

| Criterion | Devstral 2 | Claude Sonnet 4.5 | DeepSeek V3.2 |
|---|---|---|---|
| SWE-bench | 72.2% | ~74% | ~68% |
| Open-weight | Yes (Apache 2.0) | No | Yes (MIT) |
| Input price | $0.40/M | ~$3.00/M | $0.27/M |
| Self-hostable | Yes (2×A100s) | No | Difficult (671B) |
| Vision support | Yes | Yes | Limited |
| Context window | 256K | 200K | 128K |
| Best for | Cost-conscious teams, self-hosters | Complex ambiguous tasks | API-only budget use |

**Choose Devstral 2 if:** You need open-weight licensing, self-hosting control, or significant API cost reduction without a substantial capability tradeoff.

**Choose Claude Sonnet 4.5 if:** You're handling highly ambiguous tasks, need maximum reliability, or your workflows depend on Anthropic's tooling ecosystem.

**Choose DeepSeek V3.2 if:** You're purely API-based, don't need self-hosting, and want the lowest possible price point.

## Verdict: Is Devstral 2 the Best Open-Source Coding Agent in 2026?

Devstral 2 is definitively the best open-weight coding model available in April 2026 — it achieves a 72.2% SWE-bench score in a 123B dense package that can be self-hosted, fine-tuned, and deployed commercially under Apache 2.0, at a price point ($0.40/M input) that makes it 7x cheaper than comparable proprietary alternatives. For the specific use case of open-weight model deployment, there is no credible competitor: DeepSeek V3.2 requires 5x more parameters for similar results, and Kimi K2 requires 8x more. The honest caveat is that frontier proprietary models — Grok 4, GPT-5.4, Claude Opus 4.6 — still lead by 2-3 SWE-bench points, and that gap is real for complex multi-file architectural tasks. Teams building AI-assisted development workflows have three viable strategies in 2026: pay for proprietary frontier models (Claude, GPT) for maximum capability; run Devstral 2 via API for a 7x cost reduction with minimal capability loss on well-defined tasks; or self-host Devstral Small 2 locally for zero ongoing cost with 68% SWE-bench performance.

---

## FAQ

**What is Devstral 2's SWE-bench score?**
Devstral 2 achieves 72.2% on SWE-bench Verified, the highest score ever recorded by an open-weight model at its parameter count. Devstral Small 2 (24B) scores 68.0%. Both models were released by Mistral AI in December 2025.

**Can I run Devstral 2 locally?**
Devstral Small 2 (24B) runs locally on a 32GB MacBook Pro (M2 Max or later) or a single RTX 4090 using Ollama with 4-bit quantization. The full Devstral 2 (123B) requires approximately 4×80GB A100s for inference. Both are available on HuggingFace under Apache 2.0.

**How does Devstral 2 compare to Claude Sonnet in cost?**
Devstral 2 is priced at $0.40 per million input tokens and $2.00 per million output tokens — roughly 7x cheaper than Claude Sonnet 4.5 for typical coding workloads. At 100 CI pipeline jobs per day at 50K tokens each, this translates to approximately $40/day versus $250/day.

**What is Mistral Vibe CLI?**
Mistral Vibe CLI is an open-source command-line coding assistant shipped alongside Devstral 2, comparable to Claude Code or Aider. It uses Devstral 2 as its default model and supports autonomous multi-file editing, git integration, and a 256K context window for whole-repository tasks. Install with `pip install mistral-vibe-cli`.

**Is Devstral 2 better than DeepSeek V3.2 for coding?**
Yes, across most metrics. Devstral 2 scores 4+ points higher on SWE-bench (72.2% vs ~68%), uses 5x fewer parameters (123B vs 671B), generates tokens faster (71 vs ~60 tok/s), and wins 42.8% of head-to-head human evaluations against DeepSeek V3.2 (vs 28.6% loss rate). DeepSeek V3.2 has a slight edge on input pricing ($0.27 vs $0.40 per million tokens).