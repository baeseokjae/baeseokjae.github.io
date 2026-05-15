---
title: "Z.ai API Developer Guide 2026: GLM Models, Pricing, and Setup"
date: 2026-05-15T06:05:13+00:00
tags: ["Z.ai", "Zhipu AI", "GLM", "API", "Claude Code", "developer guide"]
description: "Complete Z.ai API guide: GLM model lineup, Coding Plan pricing, OpenAI/Anthropic-compatible endpoints, and step-by-step Claude Code setup."
draft: false
cover:
  image: "/images/z-ai-api-developer-guide-2026.png"
  alt: "Z.ai API Developer Guide 2026"
  relative: false
schema: "schema-z-ai-api-developer-guide-2026"
---

Z.ai is Zhipu AI's international developer platform, offering access to the GLM model family — including GLM-5.1, the first open-weight model to top the SWE-bench Pro leaderboard — via OpenAI-compatible and Anthropic-compatible APIs. Coding Plan subscriptions start at $10/month, making it the cheapest frontier-adjacent coding setup available in 2026.

## What Is Z.ai? Zhipu AI's International Developer Platform Explained

Z.ai is the international-facing developer API platform operated by Zhipu AI, a Beijing-based AI lab founded in 2019 as a spinout from Tsinghua University. The platform exposes Zhipu's GLM (General Language Model) series to developers worldwide through two API compatibility layers: an OpenAI-compatible endpoint at `https://api.z.ai/api/openai/v1` and an Anthropic-compatible endpoint at `https://api.z.ai/api/anthropic` — making Z.ai the only provider besides Anthropic itself that offers a true Anthropic API drop-in replacement. Zhipu AI trained the GLM models without Nvidia hardware, a geopolitical differentiator as export restrictions tighten in 2026. The platform offers free models (GLM-4.7-Flash, GLM-4.5-Flash) for prototyping, quota-based Coding Plan subscriptions for Claude Code users, and direct per-token billing for production workloads. As of May 2026, GLM-5.1 scores 58.4% on SWE-bench Pro, edging out GPT-5.4 (57.7%) and Claude Opus 4.6 (57.3%). For developers who need frontier-adjacent coding performance without the $200/month Claude Max bill, Z.ai is the most cost-effective path.

### Why Developers Are Choosing Z.ai

The practical draw is simple: a $30/quarter Coding Plan ($10/month equivalent) lets you run Claude Code against GLM-5.1 using a quota system, replacing Anthropic's direct subscription at a fraction of the cost. The Anthropic-compatible endpoint means zero code changes — the same environment variables that point Claude Code at Anthropic's API can be redirected to Z.ai with a base URL swap.

## GLM Model Family Overview: GLM-5.1, GLM-5-Turbo, GLM-4.7, and Free Flash Models

The Z.ai GLM model family spans six tiers in 2026, ranging from zero-cost flash models suitable for prototyping to the full GLM-5.1 flagship designed for long-horizon agentic tasks. GLM-5.1 is the headline model: 745 billion parameters, 200K token context window, and a demonstrated ability to run autonomous execution sessions up to 8 hours — in one published benchmark, it completed 655 iterations with 6,000+ tool calls to build a functional vector database at 21,500 QPS. GLM-5-Turbo is the speed-optimized variant for latency-sensitive applications. GLM-4.7 targets balanced cost-performance, priced at $0.60/M input and $2.20/M output tokens. GLM-4.7-Flash and GLM-4.5-Flash are fully free for all registered Z.ai accounts, with GLM-4.7-Flash offering a 203K context window — the largest free context window available from any major API provider. GLM-4-Air rounds out the family as an ultra-low-cost option for high-volume, simple tasks. The key architectural differentiator: all GLM models were trained on custom hardware without Nvidia GPUs, making Zhipu AI independent from Western export-controlled supply chains.

| Model | Context | Input Price | Output Price | Notes |
|---|---|---|---|---|
| GLM-5.1 | 200K | $1.00/M | $3.20/M | SWE-bench Pro #1 |
| GLM-5-Turbo | 128K | $0.80/M | $2.80/M | Speed-optimized |
| GLM-4.7 | 128K | $0.60/M | $2.20/M | Best cost/performance |
| GLM-4.7-Flash | 203K | Free | Free | Largest free context |
| GLM-4.5-Flash | 128K | Free | Free | Prototyping |
| GLM-4-Air | 128K | $0.10/M | $0.30/M | Ultra-low cost |

### Which Model Should You Default To?

For Claude Code integration, GLM-5.1 is the default recommendation — it's what Coding Plan quota is designed for, and the performance gap vs Claude Opus 4.6 is under 4% on SWE-bench Verified (77.8% vs 80.8%). For direct API workloads where cost matters more than peak coding performance, GLM-4.7 at $0.60/$2.20 per million tokens is the practical sweet spot.

## Z.ai Pricing: Coding Plans vs Direct Per-Token API Access

Z.ai pricing splits into two distinct models. Zhipu AI removed the $3/month promotional pricing on February 11, 2026; current Coding Plans use a quota-based system with three tiers. The Lite plan is $30/quarter (~$10/month) and provides enough quota for individual developers doing moderate coding assistance. The Pro plan is $90/quarter (~$30/month), targeting power users running multi-file refactors and agentic tasks daily. The Max plan is $240/quarter (~$80/month), designed for teams or developers running Claude Code as their primary coding environment throughout the workday. All Coding Plan quotas reset quarterly and are consumed by API calls routed through the Anthropic-compatible endpoint — there is no separate charge per token when using Coding Plan quota. Direct per-token API access is available for production workloads that need predictable billing without quota caps. For most Claude Code users, the Lite plan ($10/month) offers compelling value: it replaces a $20/month Claude Pro subscription for coding use cases while using a model that scores within 3 points of Claude Sonnet on SWE-bench Verified.

| Plan | Quarterly Price | Monthly Equivalent | Best For |
|---|---|---|---|
| Free | $0 | $0 | Prototyping with Flash models |
| Lite | $30/quarter | ~$10/month | Individual developers |
| Pro | $90/quarter | ~$30/month | Daily power users |
| Max | $240/quarter | ~$80/month | Full-time Claude Code users |

### Direct API vs Coding Plan: Cost Math

If you send 50M input tokens and 20M output tokens per month using GLM-5.1: direct API billing = ($1.00 × 50) + ($3.20 × 20) = $50 + $64 = $114/month. The Max Coding Plan at $80/month is capped but limited by quota. For light usage under the Lite plan's quota, you save 80-90% vs Anthropic direct.

## Quick Start: OpenAI-Compatible API Setup in Python

Z.ai's OpenAI-compatible endpoint is the fastest path from zero to working API calls. Register at z.ai, generate an API key from the dashboard, and you can reuse any OpenAI SDK code by changing two values: the base URL and the API key. The endpoint is `https://api.z.ai/api/openai/v1`, and model names follow the pattern `glm-5.1`, `glm-4.7`, `glm-4.7-flash`. No other configuration changes are required — chat completions, function calling, streaming, and embeddings all work identically to the OpenAI API contract. For teams already running OpenAI SDK in production, migrating to Z.ai for cost reduction requires only environment variable changes, not code refactoring. The recommended starting model is `glm-4.7-flash` for free exploration, then `glm-5.1` once you have a Coding Plan or direct billing configured.

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-z-ai-api-key",
    base_url="https://api.z.ai/api/openai/v1"
)

response = client.chat.completions.create(
    model="glm-5.1",
    messages=[
        {"role": "user", "content": "Write a Python function to parse JWT tokens without a library."}
    ]
)

print(response.choices[0].message.content)
```

### Streaming Responses

```python
stream = client.chat.completions.create(
    model="glm-4.7",
    messages=[{"role": "user", "content": "Explain the actor model in distributed systems."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Function Calling

Z.ai's OpenAI-compatible endpoint supports the same `tools` parameter as OpenAI. Define tools using the standard JSON schema format:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="glm-5.1",
    messages=[{"role": "user", "content": "What's the weather in Beijing?"}],
    tools=tools
)
```

## Claude Code + Z.ai: Drop-In Replacement via Anthropic-Compatible Endpoint

Z.ai is the only provider besides Anthropic that offers a true Anthropic-compatible API endpoint, located at `https://api.z.ai/api/anthropic`. This makes it a genuine drop-in replacement for Claude Code: you redirect Claude Code's API calls to Z.ai using two environment variables, and Claude Code operates normally using GLM-5.1 instead of Claude Opus or Sonnet. This setup works because GLM-5.1 supports the Anthropic messages API contract, including extended thinking format and tool use. The practical result: a $10/month Coding Plan Lite subscription replaces a $20/month Claude Pro subscription for coding-focused workflows, with GLM-5.1 achieving 94.6% of Claude Opus 4.6's coding performance on standard benchmarks. Z.ai also provides `npx @z_ai/coding-helper` as an auto-configuration tool that sets the environment variables and verifies connectivity in one command.

### Manual Setup (Two Environment Variables)

```bash
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-ai-api-key"

# Optional: increase timeout for long-running agentic tasks
export API_TIMEOUT_MS=300000

# Launch Claude Code
claude
```

### Auto-Configuration Tool

```bash
npx @z_ai/coding-helper
```

This interactive tool prompts for your Z.ai API key, sets environment variables, and runs a connectivity test. It also configures the default model to `glm-5.1` for Coding Plan accounts.

### Switching Models Inside Claude Code

Once connected, use the `/model` command inside Claude Code to switch between GLM models:

```
/model glm-5.1          # Full flagship — SWE-bench Pro leader
/model glm-5-turbo      # Faster responses, lower quota consumption
/model glm-4.7          # Best cost/performance for file-heavy tasks
```

### Verifying the Setup

After launching Claude Code with Z.ai environment variables, check the session header — it should show the model name (e.g., `glm-5.1`) and confirm the base URL. A quick test:

```bash
claude -p "Write a one-line Python HTTP server"
```

If you receive a response, the routing is working correctly. If you see an authentication error, verify that `ANTHROPIC_AUTH_TOKEN` is set to your Z.ai API key (not an Anthropic key).

## GLM-5.1 Benchmarks: How It Compares to GPT-5 and Claude Opus 4.6

GLM-5.1 is the first open-weight model to top the SWE-bench Pro leaderboard, scoring 58.4% versus GPT-5.4's 57.7% and Claude Opus 4.6's 57.3% — a margin of 0.7 points over the previous leader. On SWE-bench Verified, which tests real-world GitHub issue resolution, GLM-5.1 scores 77.8% against Claude Opus 4.6's 80.8%, a gap of 3 percentage points. In practical terms, GLM-5.1 resolves approximately 94.6% as many coding tasks as Claude Opus 4.6 while costing $1.00/M input vs Claude Opus 4.6's $15.00/M input — a 15x price difference for a 5.4% performance gap. The 8-hour sustained autonomous execution benchmark is the most differentiating result: in a published test, GLM-5.1 ran 655 consecutive iterations with more than 6,000 tool calls to build a working vector database serving 21,500 QPS. No other open-weight model has demonstrated equivalent long-horizon agentic performance.

| Benchmark | GLM-5.1 | GPT-5.4 | Claude Opus 4.6 |
|---|---|---|---|
| SWE-bench Pro | **58.4%** | 57.7% | 57.3% |
| SWE-bench Verified | 77.8% | 76.9% | **80.8%** |
| Input Price | $1.00/M | $15.00/M | $15.00/M |
| Output Price | $3.20/M | $60.00/M | $75.00/M |
| Context Window | 200K | 128K | 200K |
| Open Weight | Yes | No | No |

### Training Without Nvidia Hardware

Zhipu AI trained the GLM-5 series entirely without Nvidia GPUs, using alternative accelerator hardware. This is strategically significant: as US export controls on H100 and future Nvidia GPUs tighten, Zhipu AI's supply chain is not affected. For enterprise buyers concerned about geopolitical risk in their AI vendor stack, this is a material differentiator from models trained exclusively on Nvidia infrastructure.

## GLM Coding Plan vs Direct API: Which Should You Use?

The Coding Plan and direct per-token API access are optimized for different use cases, and choosing the wrong one wastes money. The Coding Plan uses quota — a fixed allocation of compute per billing period — designed specifically for interactive Claude Code sessions where request patterns are bursty and unpredictable. You pay a flat quarterly fee and consume quota as you code, without tracking individual token counts. Direct per-token API access is billed by actual consumption, making it predictable and auditable for production systems that process user requests at defined volumes. For Claude Code users who code 4-8 hours per day, the Coding Plan is almost always cheaper: the $80/month Max plan provides sustained access that would cost hundreds per month under direct per-token billing at GLM-5.1 rates. For batch processing pipelines, document analysis, or any workload where you can estimate monthly token volumes, direct per-token pricing lets you model costs precisely and avoid paying for unused quota.

| Scenario | Recommended Plan | Reason |
|---|---|---|
| Claude Code daily coding (<2h/day) | Lite ($10/mo) | Quota sufficient, flat cost |
| Claude Code power user (4h+/day) | Max ($80/mo) | Quota covers sustained usage |
| Production API — predictable volume | Direct per-token | Precise billing, no waste |
| Prototyping / testing | Free Flash models | Zero cost, 203K context |
| CI/CD pipeline, batch tasks | Direct per-token (GLM-4-Air) | Lowest per-token rate |

### Quota Reset and Rollover

Coding Plan quotas reset quarterly and do not roll over. If you consistently under-consume the Lite plan quota, downgrading to free Flash models for off-peak work and supplementing with direct billing during crunch periods is a legitimate optimization. Z.ai does not currently offer monthly billing — all Coding Plans require quarterly payment upfront.

## Frequently Asked Questions

**Q: Does Z.ai work as a Claude Code backend outside China?**
Yes. Z.ai is Zhipu AI's international platform, accessible globally. The Anthropic-compatible endpoint (`https://api.z.ai/api/anthropic`) and OpenAI-compatible endpoint (`https://api.z.ai/api/openai/v1`) are both served from infrastructure reachable from the US, EU, and other regions without VPN. Account registration requires a valid email address — no China phone number required.

**Q: Is GLM-5.1 actually open-weight, and can I run it locally?**
GLM-5.1 weights are released under an MIT license, making it fully open-weight. However, at 745 billion parameters, local inference requires significant hardware: at minimum 6-8 high-end GPUs (A100 or H100 class). Most developers access GLM-5.1 through the Z.ai API rather than local deployment. Smaller distilled variants are available for local use.

**Q: How does the Anthropic-compatible endpoint handle Claude-specific features like extended thinking?**
Z.ai's Anthropic-compatible endpoint supports the core Anthropic messages API contract including tool use and streaming. Claude-specific prompt formats (e.g., Claude system prompts with `<thinking>` blocks) pass through to GLM-5.1, which handles them in its own reasoning pipeline. Some Claude-specific behaviors may differ — in practice, most Claude Code workflows are unaffected because Claude Code communicates via standard API calls, not Claude-proprietary protocol extensions.

**Q: What happened to the $3/month Z.ai promotion?**
Zhipu AI ended the $3/month promotional pricing on February 11, 2026. The promotion was a limited-time offer for early adopters during the Coding Plan launch. Current pricing starts at $30/quarter (~$10/month) for the Lite plan. Existing subscribers who locked in promotional pricing during the promotion window retained it until their current quarter expired.

**Q: Can I use Z.ai for image generation or multimodal inputs?**
Yes. GLM-4V variants on Z.ai support image inputs for vision tasks, using the same OpenAI-compatible message format with `image_url` content blocks. The GLM-5v-Turbo model handles image analysis, document OCR, and visual question answering. Image generation is available through a separate CogView endpoint on the same API key — check Z.ai's documentation for model names and supported resolution formats.
