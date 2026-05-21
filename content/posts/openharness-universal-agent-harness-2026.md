---
title: "OpenHarness: Universal Agent Harness for Any LLM (2026 Review)"
date: 2026-05-20T00:04:29+00:00
tags: ["openharness", "agent harness", "LLM", "open-source", "AI agents", "CLI"]
description: "OpenHarness is an open-source universal agent harness supporting Claude, GPT, Gemini, Ollama and any LLM under a single CLI runtime."
draft: false
cover:
  image: "/images/openharness-universal-agent-harness-2026.png"
  alt: "OpenHarness: Universal Agent Harness for Any LLM"
  relative: false
schema: "schema-openharness-universal-agent-harness-2026"
---

OpenHarness is an open-source, CLI-first agent runtime that lets you run autonomous AI agents against any LLM — Claude, GPT-5, Gemini, Ollama, or any OpenAI-compatible endpoint — without rewriting your harness each time you switch providers. As of April 2026, the HKUDS/OpenHarness project has 9,100 GitHub stars and ships 43+ built-in tools out of the box.

## What Is OpenHarness? (The Name Collision Problem Explained)

OpenHarness refers to at least three distinct open-source projects that share the same name but solve the same fundamental problem: building a reusable execution layer that wraps an LLM and gives it tools, memory, permissions, and a structured agentic loop. The most prominent is HKUDS/OpenHarness (Hong Kong University of Data Science), a CLI-first runtime with 9,100 GitHub stars as of April 2026 and 43 built-in tools. A second project, AgentBoardTT/openharness, focuses on multi-provider SDK integration with explicit support for Claude, GPT, Gemini, and Ollama under a unified auth model. A third lives at OpenHarness.ai and emphasizes harness interoperability. Despite the naming confusion, all three projects share the same philosophical root: **Agent = Model + Harness**. The model provides intelligence; the harness provides everything else — tools, memory, lifecycle hooks, permissions, and observability. In a market projected to grow from $8.29 billion in 2025 to $12.06 billion in 2026 at a CAGR of 45.5%, building vendor-agnostic harnesses is becoming the defining engineering challenge of the AI era. Understanding which "OpenHarness" you're working with is the first step.

### Why the Name Collision Matters for Developers

When you search for "openharness agent harness" on GitHub or npm you'll surface multiple repositories. Before committing to any of them, check the GitHub org: `HKUDS` for the CLI runtime, `AgentBoardTT` for the SDK-first multi-provider variant. This guide focuses primarily on HKUDS/OpenHarness because it has the most documented production usage, but draws comparisons from AgentBoardTT where the multi-provider support is more thoroughly tested.

## HKUDS OpenHarness: The Open-Source CLI Agent Runtime

HKUDS/OpenHarness is a production-grade open-source agent harness built to make the internals of AI agent systems fully inspectable and hackable. Unlike Claude Code (which ships as a closed binary with a public SDK) or the OpenAI Agents SDK (which is vendor-locked by design), HKUDS/OpenHarness is fully open: every subsystem from the agent loop to the permission evaluator is readable and forkable. The project launched in late 2024 and reached 9,100 stars by April 2026, driven by developers frustrated with vendor lock-in. Its headline features are a 10-subsystem architecture, MCP HTTP transport support, multimodal gateway integration, a built-in personal agent called Ohmo, and a CLI that feels closer to a Unix tool than a chatbot. The philosophy is explicitly "inspector-friendly" — you can run `openharness --debug` and see every tool call, permission check, and LLM exchange in real time. For teams building AI products that need to audit agent behavior, this transparency is a core differentiator that neither LangChain nor any vendor-hosted harness offers at the same depth.

### Installing OpenHarness in Under 5 Minutes

```bash
pip install openharness
# or from source
git clone https://github.com/HKUDS/OpenHarness && cd OpenHarness
pip install -e .
openharness --version
```

Once installed, configure your provider:

```bash
openharness config set provider anthropic
openharness config set api_key $ANTHROPIC_API_KEY
openharness run "List all Python files in this repo and summarize what each one does"
```

Switching to Ollama for local inference requires only two lines:

```bash
openharness config set provider ollama
openharness config set model llama3.3:70b
```

No code changes. The harness abstracts the provider entirely.

## Core Architecture: The 10-Subsystem Agent Harness Pattern

The 10-subsystem architecture of OpenHarness represents the most detailed public taxonomy of what a production agent harness actually does. The ten subsystems are: (1) **Agent Loop** — the perceive-reason-act cycle that drives execution; (2) **Tool Registry** — 43 built-in tools covering filesystem, web, code execution, and external APIs; (3) **Knowledge & Skills** — persistent fact storage and reusable task templates; (4) **Plugin System** — first-class extension points for custom tools and providers; (5) **Permission Engine** — multi-level access control from read-only to full-auto; (6) **Lifecycle Hooks** — pre/post hooks for every tool call and agent turn; (7) **MCP Transport** — Model Context Protocol support over HTTP for remote tool servers; (8) **Memory Subsystem** — MEMORY.md persistence plus vector-backed retrieval; (9) **Multi-Agent Coordination** — spawning and orchestrating sub-agents; (10) **Observability** — structured logging, token counting, and debug traces. This taxonomy matters because most competing harnesses implement only 4–6 of these subsystems. LangChain covers tools and memory well but has no native permission engine or lifecycle hooks. Claude Code SDK covers all ten but only for Anthropic models. OpenHarness is the only open-source harness that attempts all ten subsystems across any LLM.

### The Agent Loop in Detail

The agent loop follows a strict perceive → plan → tool-call → observe → repeat cycle. Each turn, the model receives the current context window (system prompt + conversation history + tool results), generates either a response or a tool call, and the harness executes the tool and appends the result. OpenHarness adds two non-standard extensions: **streaming tool-call cycles** (the model can emit partial tool arguments and the harness streams the execution) and **background task management** (long-running tools run in a separate process with progress callbacks to the main loop). Both features address a gap in simpler harnesses where a single slow tool call (a 30-second web scrape, a database migration) would block the entire agent.

### Permission Engine: Multi-Level Access Control

OpenHarness ships three permission modes: `read-only` (file reads and web fetches only), `confirm` (all writes prompt the user), and `auto` (full autonomous execution). This mirrors Claude Code's permission model but extends it to any LLM provider — you can run a local Llama model in `confirm` mode with the same safety guarantees you'd expect from a closed-source harness. A fourth mode, `allowlist`, lets you define per-tool permissions at the granularity of individual filesystem paths or API endpoints.

## Universal LLM Support — Every Provider, One Harness

Universal LLM support is OpenHarness's most commercially important feature: a single harness configuration works across Anthropic Claude (all versions), OpenAI GPT-4o and GPT-5, Google Gemini 2.0 and 2.5, Mistral, Kimi, GLM-4, and any server that speaks the OpenAI-compatible chat completion API — including self-hosted Ollama, LM Studio, vLLM, and Together AI. In 2026, 65% of global organisations use generative AI tools, and most enterprises run more than one LLM provider for cost, compliance, or capability reasons. A harness that forces you to pick one provider creates a hidden long-term cost: every time the model landscape shifts (GPT-5 arrives, a new Gemini model drops), you rewrite your harness. OpenHarness avoids this by normalizing all providers behind a single `ProviderAdapter` interface. Tool calls, streaming, token counting, and error handling are handled by the adapter; your agent code never sees the difference. The AgentBoardTT variant takes this further with explicit benchmarks showing sub-100ms provider switching latency in tests across Claude, GPT, and Gemini.

### Supported Providers and Configuration

| Provider | Auth Method | Streaming | Tool Calls | Notes |
|---|---|---|---|---|
| Anthropic Claude | API key | Yes | Yes | claude-opus-4-7, sonnet-4-6, haiku-4-5 |
| OpenAI GPT | API key | Yes | Yes | gpt-4o, gpt-5, o3 |
| Google Gemini | Service account / key | Yes | Yes | gemini-2.0-flash, gemini-2.5-pro |
| Ollama (local) | None | Yes | Yes | Any Ollama-compatible model |
| vLLM / LM Studio | API key optional | Yes | Partial | OpenAI-compatible endpoints |
| Kimi / GLM-4 | API key | Yes | Yes | Chinese model providers |
| Together AI | API key | Yes | Yes | Hosted open-source models |

Switching providers requires only editing `~/.openharness/config.yaml` or passing `--provider` and `--model` flags at the CLI. No code changes in your agent logic.

## Built-in Tools, Skills, and the Ohmo Personal Agent

OpenHarness ships 43 built-in tools across six categories, making it immediately useful without writing any tool integrations. The six categories are: **Filesystem** (read, write, glob, grep, tree — 8 tools), **Web** (fetch, search, screenshot, crawl — 7 tools), **Code** (execute Python/JS/Bash, lint, test runner — 9 tools), **External APIs** (GitHub, Slack, Linear, calendar — 10 tools), **Memory** (save fact, recall, summarize conversation — 5 tools), and **System** (process management, environment, cron — 4 tools). The 43-tool count matches what Claude Code ships, but unlike Claude Code's tools (which are tightly coupled to the Anthropic SDK), OpenHarness tools are provider-agnostic — they work identically whether the underlying model is Claude or Llama. Beyond the built-in tools, OpenHarness ships a **Skills** system: reusable task templates that combine multiple tools into named workflows. A `skills/deploy.yaml` file, for example, can encode your entire deploy pipeline as a skill that the agent can invoke by name. This is the harness equivalent of shell aliases, but semantically grounded — the agent understands what a skill does, not just how to call it.

### Ohmo: The Built-in Personal Agent

Ohmo is OpenHarness's built-in personal agent, designed to be the "always-on" companion that manages your development environment. Unlike running `openharness run "..."` for one-off tasks, Ohmo maintains persistent context across sessions, remembers your project structure, tracks in-progress tasks, and proactively surfaces reminders. Under the hood, Ohmo uses the Memory subsystem (MEMORY.md persistence + optional vector retrieval) and runs on a configurable heartbeat — by default checking in every 30 minutes to look for new tasks, expiring reminders, or stalled background jobs. Ohmo is provider-agnostic: you can back it with Claude for complex reasoning and fall back to a local Ollama model when offline.

```bash
# Start Ohmo as a background daemon
openharness ohmo start --provider anthropic --model claude-sonnet-4-6
# Ask Ohmo something
openharness ohmo ask "What tasks are in progress in this repo?"
# Stop the daemon
openharness ohmo stop
```

## OpenHarness vs Other Harnesses: Head-to-Head Comparison

The right agent harness depends on whether you prioritize vendor flexibility, developer experience, production reliability, or research transparency. In 2026, the main contenders are OpenHarness (HKUDS), Claude Code SDK (Anthropic), LangChain/LangGraph, and the OpenAI Agents SDK. OpenHarness is the only fully open-source option that supports all major LLM providers under a single runtime, making it the strongest choice for teams that cannot commit to a single vendor. Claude Code SDK delivers the best developer experience for Anthropic-only stacks — it's tightly integrated, well-documented, and production-hardened. LangChain covers the widest range of integrations (databases, vector stores, document loaders) but its abstractions have historically leaked at scale. The OpenAI Agents SDK is the fastest path to production if your stack is 100% OpenAI, but offers no path to provider migration. Gartner projects 40% of enterprise applications will include task-specific AI agents by end of 2026 — which means the harness decision you make today will affect your architecture for years.

### Feature Comparison Table

| Feature | OpenHarness (HKUDS) | Claude Code SDK | LangChain | OpenAI Agents SDK |
|---|---|---|---|---|
| Multi-provider LLM | Yes (7+ providers) | No (Anthropic only) | Yes (via adapters) | No (OpenAI only) |
| CLI-first | Yes | Yes | No | No |
| Open-source | Yes (MIT) | Partial (SDK open, runtime closed) | Yes (MIT) | No |
| Built-in tools | 43 | 43 | 100+ (via integrations) | ~10 |
| Permission engine | Yes (4 modes) | Yes (3 modes) | No | Partial |
| MCP support | Yes (HTTP) | Yes (stdio + HTTP) | No | No |
| Memory persistence | Yes (MEMORY.md + vector) | Yes (MEMORY.md) | Yes (vector stores) | Partial |
| Multi-agent | Yes | Yes | Yes (LangGraph) | Yes |
| Streaming tool calls | Yes | Yes | Partial | Yes |
| Production-grade | Growing (2025-2026) | Yes (mature) | Yes (mature) | Yes (mature) |

### When to Choose OpenHarness Over Claude Code

If your team uses more than one LLM provider — either today or plausibly in the next 12 months — OpenHarness is the correct harness choice. The switching cost from Claude Code to OpenHarness is high once you've built against the Anthropic SDK's agent primitives. The switching cost from OpenHarness to a different provider is nearly zero. The key question to ask: "If Anthropic prices doubled tomorrow, could we switch models without rewriting our agent?"

## Who Should Use OpenHarness in 2026?

OpenHarness is the right tool for four categories of developer in 2026. First, **multi-cloud enterprise teams** building agents that need to run on different models in different regions or compliance environments — OpenHarness's unified auth model and provider-agnostic tool layer handles this cleanly. Second, **research teams** who need full transparency into agent internals — every subsystem is inspectable, every tool call is logged, and the debug output is structured for analysis. Third, **developers building agent-powered developer tools** who want a production harness without vendor lock-in and with a CLI interface that fits naturally into existing shell workflows. Fourth, **cost-sensitive startups** who want to run agents on Ollama or open-weight models locally during development and switch to Claude or GPT in production — OpenHarness makes this a config change. OpenHarness is probably not the right choice for teams that are already heavily invested in the Claude Code SDK and have no multi-provider requirements, or for teams using LangChain's extensive document-loader and vector-store ecosystem extensively. The LLM market is projected to grow from $4.5 billion in 2023 to $82.1 billion by 2033 — the teams that invest in provider-agnostic infrastructure today will have far more flexibility as that market matures.

### Teams That Should Stick with Claude Code SDK

Teams building exclusively on Anthropic models with complex extended thinking workflows, tight MCP integrations using stdio transport, or deep reliance on Claude-specific features (citations, computer use, vision-heavy workflows) will find Claude Code SDK more production-ready today. OpenHarness's Claude adapter is solid but not as deeply tested as the native SDK.

## Getting Started with OpenHarness (Quick Setup Guide)

Getting a working OpenHarness agent running takes under 10 minutes from a fresh machine. The harness requires Python 3.11+ and installs via pip. After installation, the `openharness init` command scaffolds a project directory with a config file, a MEMORY.md file for persistence, and a `skills/` directory for reusable task templates. The first time you run an agent, OpenHarness will prompt you for your LLM provider credentials and store them in `~/.openharness/config.yaml`. From there, you can run one-shot tasks via `openharness run "..."`, start a persistent Ohmo session via `openharness ohmo start`, or build a custom agent by importing the SDK: `from openharness import Agent, ToolRegistry`. The SDK path is useful when you need to embed OpenHarness inside a larger application — a FastAPI service, a CI/CD pipeline, or a Slack bot — without exposing the CLI interface. OpenHarness's `Agent` class takes a `provider`, a `model`, a `tool_registry`, and a `permission_mode`, and exposes a simple `agent.run(prompt)` method that handles the full agentic loop internally.

### Step-by-Step Setup

```bash
# 1. Install
pip install openharness

# 2. Initialize a project
mkdir my-agent && cd my-agent
openharness init

# 3. Configure your provider (interactive)
openharness config setup
# Prompts: provider, api_key, model, permission_mode

# 4. Run your first agent task
openharness run "Find all TODO comments in this directory and create a summary report"

# 5. Switch to a different provider
openharness config set provider ollama && openharness config set model qwen3:32b
openharness run "Same task, different model — no code changes required"
```

### Using the Python SDK

```python
from openharness import Agent, ToolRegistry
from openharness.providers import AnthropicProvider

registry = ToolRegistry.defaults()  # loads all 43 built-in tools
provider = AnthropicProvider(model="claude-sonnet-4-6")

agent = Agent(
    provider=provider,
    tool_registry=registry,
    permission_mode="confirm",
    memory_path="./MEMORY.md"
)

result = agent.run("Analyze this codebase and identify the three riskiest files")
print(result.response)
```

Swapping `AnthropicProvider` for `OllamaProvider(model="llama3.3:70b")` requires no other changes.

## FAQ

**Q: Is OpenHarness the same as Claude Code?**
No. OpenHarness (HKUDS) is an independent open-source project that supports any LLM provider, including Claude. Claude Code is Anthropic's own CLI and SDK, which only works with Anthropic models. OpenHarness is architecturally similar to Claude Code — both have a CLI, a permission engine, and a 10-subsystem harness model — but OpenHarness is vendor-agnostic and fully open-source.

**Q: Can I use OpenHarness with a local model via Ollama?**
Yes. OpenHarness has first-class Ollama support. Set `provider: ollama` and `model: llama3.3:70b` (or any Ollama-compatible model) in your config, and the harness will route all LLM calls to your local Ollama server. All 43 built-in tools, the permission engine, and the memory subsystem work identically with local models.

**Q: How does OpenHarness handle tool calls for models that don't support native function calling?**
OpenHarness includes a fallback tool-call parser that works with models that produce structured JSON in their response text rather than native function-call tokens. This is used automatically for models that don't support the OpenAI tool-call format, enabling tool-use with older or smaller models that lack native support.

**Q: What is the difference between HKUDS/OpenHarness and AgentBoardTT/openharness?**
HKUDS/OpenHarness is the more mature project with 9,100 stars, a full CLI, 43 built-in tools, and the Ohmo personal agent. AgentBoardTT/openharness is a lighter-weight SDK-first project focused on multi-provider benchmarking with explicit latency measurements across providers. If you want a full production runtime, use HKUDS. If you want a thin multi-provider abstraction layer for your own agent framework, AgentBoardTT may be a better fit.

**Q: Is OpenHarness production-ready in 2026?**
HKUDS/OpenHarness is production-ready for teams that accept it's a 2-year-old project with a smaller support ecosystem than LangChain or Claude Code SDK. It runs reliably in CI/CD pipelines, has a stable CLI interface, and its core subsystems (agent loop, tools, permissions) are well-tested. The MCP transport and multi-agent coordination features are newer and carry more risk. For high-stakes production deployments, plan for more testing than you'd budget for Claude Code SDK.
