---
cover:
  alt: 'OpenAI Agents SDK v2 Guide 2026: Configurable Memory, Sandbox Orchestration,
    Filesystem Tools'
  image: /images/openai-agents-sdk-v2-guide-2026.png
  relative: false
date: 2026-05-01 09:04:53+00:00
description: 'Complete guide to OpenAI Agents SDK v2 (April 2026): configurable memory,
  apply_patch filesystem tools, 7 sandbox providers, and AGENTS.md workspace con...'
draft: false
schema: schema-openai-agents-sdk-v2-guide-2026
tags:
- openai
- agents
- sdk
- python
- sandbox
- ai-agents
title: 'OpenAI Agents SDK v2 Guide 2026: Configurable Memory, Sandbox Orchestration,
  Filesystem Tools'
---

OpenAI Agents SDK v2, released April 15, 2026, transforms the framework from a pure orchestrator into a full execution environment with configurable memory, sandboxed code execution, `apply_patch` filesystem tools, and support for 100+ LLMs — the most significant overhaul since the SDK replaced the experimental Swarm library in March 2025.

## What Is OpenAI Agents SDK v2?

OpenAI Agents SDK v2 is the April 15, 2026 update to OpenAI's open-source Python framework for building production-grade AI agents. The update — the largest since the SDK's March 2025 launch — introduces a model-native harness that wraps the entire lifecycle of agent execution: memory management, tool access, sandbox orchestration, and filesystem operations. Unlike the v1 pure orchestrator design that left developers to wire up their own context, storage, and execution layers, v2 ships a turnkey harness that handles these concerns while remaining fully configurable. The SDK now supports over 100 non-OpenAI LLMs via the Chat Completions API, removing what had been the framework's biggest criticism: vendor lock-in. With more than 4 million weekly users of OpenAI Codex as of 2026, the developer appetite for agentic tooling at this level is validated. The v2 harness covers five domains: configurable memory, filesystem tools (`apply_patch` and shell), sandbox execution across 7 providers, workspace manifests via AGENTS.md, and skills for progressive feature disclosure.

## From Pure Orchestrator to Full Execution Environment: Why the Philosophy Shifted

The original Agents SDK v1 was deliberately minimal — a thin coordination layer that handled handoffs, guardrails, and tool-calling but left memory, compute isolation, and file access entirely to the developer. That design was principled but incomplete. Teams building real coding agents discovered that managing agent context across turns, securely running LLM-generated code, and editing files without blowing up repos required thousands of lines of custom infrastructure. The v2 harness answers each of those gaps explicitly. Memory is now an intentional first-class concern rather than accidental chat history accumulation. Code execution happens in isolated sandbox environments rather than directly on the host machine. File edits happen through a structured `apply_patch` interface with diff semantics rather than raw `open().write()` calls. The philosophy shift is from "bring your own plumbing" to "opinionated plumbing you can swap out." Developers can replace any harness component — use their own memory store, their own sandbox provider, their own manifest format — but they get sane defaults from day one. This matters especially for enterprises, where standing up a reliable agent pipeline previously required significant platform engineering investment before a single business-logic line was written.

### Why v1's Pure Orchestrator Design Broke Down

The v1 approach delegated too much. Developers using Agents SDK v1 for coding workflows had to independently solve: rolling context windows (agents would either forget or hit token limits), safe execution of shell commands the agent generated, editing code files without corrupting them, and mounting the right filesystem state before each turn. Each team solved these problems differently, making agents non-portable and difficult to deploy consistently. v2 standardizes all of it without removing developer control.

## Configurable Memory: How the v2 Harness Manages Agent Context

Configurable memory in OpenAI Agents SDK v2 refers to the explicit, developer-controllable layer that governs what context an agent retains across turns, sessions, and tasks. In v1, memory was whatever remained in the chat history array — agents would accumulate unstructured conversation turns until hitting a token limit, causing unpredictable behavior on long tasks. v2 replaces this with a structured memory system where developers define retention policies: what to keep verbatim, what to summarize, what to discard, and what to persist to external storage. The harness supports short-term working memory (in-context), medium-term episodic memory (summarized and stored), and long-term semantic memory (retrieved via vector search). For enterprise use cases — expense auditing, code review pipelines, multi-session research tasks — this distinction is critical. An agent auditing 500 financial documents does not need to retain the full text of each document in its context; it needs a structured summary and the ability to retrieve specific facts on demand. Configurable memory makes that architecture first-class in the SDK rather than something each team builds from scratch. The harness integrates with the Manifest abstraction, allowing memory backends to be declared alongside compute and storage configuration.

### How Memory Backends Work in Practice

The memory harness exposes three interfaces: `MemoryStore` for reads/writes, `MemoryPolicy` for retention rules, and `MemoryRetriever` for semantic search. You swap implementations without changing agent logic. The default in-memory backend is suitable for single-session agents; for persistence across sessions, swap in a Redis or PostgreSQL backend. OpenAI ships reference implementations for both; community backends for Pinecone, Weaviate, and Supabase are already available on PyPI.

```python
from agents import Agent, Runner
from agents.memory import RedisMemoryStore, SummarizationPolicy

agent = Agent(
    name="code-reviewer",
    memory_store=RedisMemoryStore(url="redis://localhost:6379"),
    memory_policy=SummarizationPolicy(keep_last_n=5, summarize_older=True),
)
```

This configuration keeps the last 5 turns verbatim and summarizes older turns automatically, preventing context blowout on long-running review sessions.

## Filesystem Tools Deep Dive: apply_patch and Shell Tool

The filesystem tools in OpenAI Agents SDK v2 consist of two primitives: `apply_patch`, which edits files via a structured diff format, and `shell`, which runs arbitrary commands in a controlled execution environment. These tools are derived directly from the Codex pipeline, bringing the same file manipulation capabilities that power OpenAI's coding product directly into the SDK for any developer to use. `apply_patch` accepts a unified diff as input and applies it to the target file atomically, meaning partial writes that corrupt a file are impossible — either the entire patch applies cleanly or the operation fails and the original file is untouched. This is a significant safety improvement over agents that use `write_file` to overwrite complete files: large files don't need to be fully regenerated for small changes, and reviewers can see exactly what changed in a structured format. The `shell` tool wraps command execution with configurable timeouts, environment variable injection, and output capture. When combined with sandbox providers (covered in the next section), the shell tool runs commands inside an isolated container rather than the host machine, eliminating the class of security issues where agents execute malicious or buggy code in production environments. Both tools are available as first-class SDK primitives, not external MCP integrations — they appear in the agent's tool list automatically when code mode is enabled.

### Using apply_patch in Code Mode

Enable code mode to unlock both filesystem tools automatically:

```python
from agents import Agent, Runner, CodeMode

agent = Agent(
    name="refactoring-agent",
    model="gpt-4.1",
    mode=CodeMode.SANDBOX,  # enables apply_patch + shell
    sandbox_provider="e2b",
)

result = await Runner.run(
    agent,
    "Refactor auth.py to use the repository pattern. Tests are in tests/test_auth.py."
)
```

The agent receives `apply_patch` and `shell` in its tool list and can edit files, run tests, and iterate on failures within the sandbox environment.

## Sandbox Orchestration: Running Agents in Controlled Environments

Sandbox orchestration in OpenAI Agents SDK v2 is the native execution isolation layer that runs agent-generated code and shell commands inside controlled containers, separate from the orchestration process. Before v2, developers who wanted to safely execute LLM-generated code had to build their own sandboxing layer — typically wrapping Docker containers manually, managing their lifecycle, and handling I/O bridging by hand. v2 makes sandboxing a first-class SDK concept. The harness manages container lifecycle (spin up, teardown, timeout enforcement), workspace mounting (local files, S3, GCS, Azure Blob, Cloudflare R2), and environment variable injection. Code the agent writes runs inside the sandbox, not on the orchestration host. If the agent's code crashes, hangs, or produces a security incident, it stays contained. The sandbox model is particularly important for enterprise deployments where autonomous agents touch real codebases or production data. Seven providers are natively supported: Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, and Vercel. Switching providers is a one-line config change — the SDK abstracts away provider-specific APIs. Subagents, a feature coming to the SDK later in 2026, will extend sandbox orchestration to hierarchical agent trees where parent agents spawn child agents in their own isolated contexts.

### How the Sandbox-Orchestration Split Works

The harness maintains a strict separation: the orchestration process (LLM calls, tool routing, memory management) runs on your infrastructure, while execution (shell commands, file edits) runs in the provider sandbox. The two communicate via the SDK's internal messaging layer. This split means orchestration cost and compute cost are independently scalable — you can run orchestration on a small VM and scale execution to beefy GPU sandboxes for compilation-heavy workloads.

## Choosing Your Sandbox Provider: E2B vs Modal vs Daytona vs Others

Selecting the right sandbox provider for OpenAI Agents SDK v2 depends on your workload type, latency requirements, and budget. All seven supported providers (Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, Vercel) are interchangeable from the SDK's perspective — the `sandbox_provider` config field is the only change required to switch. E2B is the recommended starting point for development and testing: it offers a $100 free credit, cold starts under 500ms, and a free tier suitable for low-volume workloads. For production Python-heavy workloads (data analysis, ML pipelines, package-dependent agents), Modal is the preferred choice — it supports GPU instances, has sub-second cold starts for pre-warmed images, and its pricing at $0.000529/GB-s for CPU is competitive for sustained workloads. Daytona specializes in full development environment sandboxes with persistent workspace state, making it ideal for agents that need to maintain a git working tree across sessions. Cloudflare Workers Sandbox is the right choice for latency-sensitive agents deployed at the edge — sub-100ms cold starts globally but limited to CPU-only workloads and 128MB memory. Vercel Sandbox integrates natively with Next.js deployments for frontend-adjacent agents. For air-gapped enterprise deployments, Runloop offers on-premises sandbox infrastructure.

| Provider | Cold Start | GPU Support | Free Tier | Best For |
|----------|-----------|-------------|-----------|----------|
| E2B | <500ms | No | $100 credit | Dev/testing |
| Modal | <1s (warm) | Yes | $30/mo | Python/ML production |
| Daytona | ~2s | No | Yes | Persistent dev environments |
| Cloudflare | <100ms | No | Generous | Edge/latency-sensitive |
| Vercel | <500ms | No | Hobby plan | Next.js-integrated agents |
| Runloop | Variable | Yes | No | On-premises enterprise |
| Blaxel | <1s | No | Yes | General purpose |

## AGENTS.md and the Manifest Abstraction: Configuring Agent Workspaces

AGENTS.md is a configuration file placed in an agent's workspace that defines its custom instructions, available skills, MCP tool connections, and behavioral rules in a portable, human-readable format. It extends the concept of `.cursorrules` or `CLAUDE.md` files to the Agents SDK — a software contract that specifies how an agent should behave when it wakes up in a given project context. An AGENTS.md file can specify which tools are available, what coding conventions to follow, which files to treat as read-only, and what escalation rules apply when the agent encounters unexpected states. This portability is what allows the same agent definition to behave consistently whether running locally, in CI, or in a production sandbox. The Manifest abstraction complements AGENTS.md at the infrastructure level: while AGENTS.md covers behavior and instructions, the Manifest covers compute (Docker image, resource limits), storage (workspace mount points, cloud storage backends), and environment (secrets, env vars). Together, AGENTS.md and Manifest form a complete, reproducible agent workspace spec. The Manifest supports mounting workspaces from local disk, AWS S3, Google Cloud Storage, Azure Blob Storage, or Cloudflare R2 — meaning agents can operate on existing codebases or datasets stored in your cloud infrastructure without copying files to the orchestration host.

### What Goes in AGENTS.md

A minimal AGENTS.md for a code-review agent might look like:

```markdown
# Code Review Agent

### Instructions
- Review for security vulnerabilities first, performance second
- Never modify test files
- Post findings as inline comments using the comment tool

### Tools
- github_comment: post review findings
- web_search: look up CVE references

### Constraints
- Read-only access to /src, /tests
- Write access to /review-output only
```

The SDK reads this file automatically when the agent initializes in the workspace, with no additional configuration required.

## Step-by-Step Setup Guide: Installing and Running Your First v2 Agent

Getting started with OpenAI Agents SDK v2 requires Python 3.11+ and roughly five minutes for a basic agent. The SDK ships as `openai-agents` on PyPI; the v2 harness features are available from version 0.4.0 onward. Install with `pip install openai-agents>=0.4.0`. Set your `OPENAI_API_KEY` environment variable, or configure an alternative LLM provider — the SDK accepts any Chat Completions-compatible endpoint, covering the 100+ supported models. For sandbox execution, install the provider-specific extra: `pip install openai-agents[e2b]` for E2B, `pip install openai-agents[modal]` for Modal, and so on. A complete working agent with configurable memory, sandbox execution, and the filesystem tools can be running in under 30 lines of Python. The `Runner.run()` API is unchanged from v1 for basic cases — existing agents that only use the orchestration layer will continue to work without modification. The harness features opt-in: you enable memory, sandbox, and filesystem tools explicitly through agent configuration, so existing codebases are not broken by the upgrade.

### Full Quickstart: Sandbox-Enabled Coding Agent

```python
import asyncio
from agents import Agent, Runner, CodeMode
from agents.memory import InMemoryStore, SlidingWindowPolicy

async def main():
    agent = Agent(
        name="my-coding-agent",
        model="gpt-4.1",
        mode=CodeMode.SANDBOX,
        sandbox_provider="e2b",
        memory_store=InMemoryStore(),
        memory_policy=SlidingWindowPolicy(max_tokens=8000),
        instructions="You are a helpful coding assistant. Use apply_patch for file edits.",
    )

    result = await Runner.run(
        agent,
        "Write a Python function that validates email addresses with tests. "
        "Save the implementation to email_validator.py and tests to test_email_validator.py.",
    )
    print(result.final_output)

asyncio.run(main())
```

This agent writes files, runs tests inside the E2B sandbox, and iterates until tests pass — all without touching your local filesystem.

## Multi-Agent Patterns: Handoffs, Subagents, and Code Mode

Multi-agent orchestration in OpenAI Agents SDK v2 supports three patterns: handoffs (v1-compatible sequential delegation), subagents (upcoming hierarchical spawning), and code mode pipelines (end-to-end coding workflows within a shared sandbox). Handoffs remain the primary multi-agent primitive: one agent passes control to another with context, tools can be scoped per agent, and guardrails enforce transition rules. The v2 harness improves handoffs by making memory portable across them — the receiving agent inherits the sender's summarized context rather than starting fresh, which was a major gap in v1 for long pipelines. Subagents, announced as "coming soon" in the April 2026 release, will allow parent agents to spawn child agents in isolated sandbox contexts and collect their results asynchronously. This enables parallel workloads: a research agent spawning 10 sub-agents to scrape and summarize different sources simultaneously. Code mode introduces a specialized pipeline where an agent operates in a persistent sandbox across multiple turns, maintaining filesystem state (modified files, installed packages, test results) between each LLM call. This is how Codex works internally, and it's now available to any developer building coding workflows.

### Handoff Example with Shared Memory

```python
from agents import Agent, Runner, handoff

planner = Agent(name="planner", model="gpt-4.1")
executor = Agent(
    name="executor",
    model="gpt-4.1",
    mode=CodeMode.SANDBOX,
    sandbox_provider="modal",
)

planner_with_handoff = planner.clone(
    handoffs=[handoff(executor, context_transfer="summarized")]
)
```

The `context_transfer="summarized"` parameter passes a compressed summary of the planner's work to the executor rather than the raw message history, controlling token usage in multi-step pipelines.

## OpenAI Agents SDK v2 vs LangGraph vs CrewAI vs AutoGen: Which to Choose in 2026

Choosing between OpenAI Agents SDK v2, LangGraph, CrewAI, and AutoGen in 2026 depends on your team's primary workload, existing infrastructure, and tolerance for framework complexity. OpenAI Agents SDK v2 is the best choice for teams building coding agents, software engineering workflows, or any task requiring secure code execution — the native sandbox and filesystem tools give it a decisive advantage for these use cases. LangGraph remains the preferred choice for stateful, durable workflows where agents may pause for hours or days waiting for human approval or external events — its graph-based state machine model handles complex conditional flows that the Agents SDK's linear pipeline approach doesn't cover as cleanly. CrewAI scored 82% task success on multi-agent benchmarks with 1.8s average latency, making it competitive for role-based team simulations where agents have specialized personas (researcher, writer, critic). AutoGen is entering maintenance mode as Microsoft shifts focus to its broader Agent Framework; new projects should not be started on AutoGen unless already deeply invested. The v2 SDK's expansion to 100+ LLMs removes the strongest reason to prefer LangChain/LangGraph for multi-provider deployments.

| Framework | Best For | Weakness | LLM Support | Sandbox Built-in |
|-----------|----------|----------|-------------|-----------------|
| OpenAI Agents SDK v2 | Coding agents, software engineering | Complex stateful flows | 100+ models | Yes (7 providers) |
| LangGraph | Durable, pausable workflows | Steep learning curve | Any | No (DIY) |
| CrewAI | Role-based multi-agent teams | Limited filesystem tools | Any | No |
| AutoGen | Existing AutoGen codebases | Maintenance mode | Any | No |
| Mastra | TypeScript/Node.js agents | Python ecosystem gaps | Any | No |

## Pricing and Token Costs: What Sandbox Agents Actually Cost

Running production agents with OpenAI Agents SDK v2 involves three cost dimensions: LLM inference, sandbox compute, and storage I/O. LLM inference with gpt-4.1 at $2/$8 per million tokens (input/output) is the dominant cost for short tasks; for long-running coding agents that generate thousands of tool calls, sandbox compute can exceed inference costs. E2B charges $0.10/hour for CPU sandboxes; a coding agent that runs 30 minutes per task costs $0.05 in sandbox time. Modal's pricing at $0.000529/GB-s translates to roughly $0.19/hour for a 100GB-s workload — competitive for compute-heavy tasks. Daytona persistent workspace storage adds $0.023/GB/month, relevant for agents maintaining large codebases. Storage I/O to S3 or GCS for workspace mounting adds pennies per GB. For budgeting purposes: a coding agent that runs 10-minute tasks, generates ~50K tokens, and uses E2B sandbox costs approximately $0.40-0.60 per run with gpt-4.1. Volume discounts through OpenAI's enterprise tier and provider credits (E2B's $100 free credit, Modal's $30/month free tier) make development and moderate production workloads accessible without significant upfront commitment.

## Common Pitfalls and Best Practices for Production Deployments

Deploying OpenAI Agents SDK v2 agents to production requires attention to several failure modes that are unique to the new harness architecture. The most common pitfall is sandbox cold start latency: E2B sandboxes start in under 500ms for pre-built images but can take 5-10 seconds for custom Docker images with large dependency trees. Pre-warm sandboxes for latency-sensitive workflows using the provider's warmpool APIs. Memory policy misconfiguration is the second-most-common issue: a `SlidingWindowPolicy` that's too aggressive drops important context mid-task, while one that's too permissive allows token costs to spiral on long sessions. Tune retention policies against your specific task length distribution before going to production. For filesystem tools, always verify that `apply_patch` diffs are reviewed before applying in production codebases — agent-generated patches that look correct can introduce subtle bugs. Implement a human-in-the-loop approval step for patches touching critical files. Finally, secrets management: never pass API keys or database credentials through AGENTS.md or Manifest environment variables in plaintext. Use your provider's secrets management integration (E2B secrets, Modal secrets) or inject at runtime through the SDK's encrypted env var API.

### Production Checklist

- Pre-warm sandboxes using provider warmpool APIs
- Tune `MemoryPolicy` against task length distribution before launch
- Add human-in-the-loop approval for `apply_patch` on critical files
- Use provider secrets management — never plaintext credentials in AGENTS.md
- Set sandbox timeouts to 2x your 95th-percentile task duration
- Enable tracing with `Runner.run(..., trace=True)` for all production agents
- Test handoff memory compression with your actual context size before relying on it

---

## Frequently Asked Questions

**Q: Is OpenAI Agents SDK v2 backwards compatible with v1 agents?**

Yes. Agents built with v1 that only use the orchestration layer (handoffs, tools, guardrails) run unchanged on v2. The harness features — configurable memory, sandbox execution, filesystem tools — are opt-in. You enable them through explicit configuration, so upgrading does not break existing agents.

**Q: Does OpenAI Agents SDK v2 require using OpenAI models?**

No. The April 2026 update added support for 100+ non-OpenAI LLMs via any Chat Completions-compatible API. You can use Anthropic Claude, Google Gemini, Mistral, or any locally hosted model by pointing the SDK at a compatible endpoint. This was the most-requested change from the developer community.

**Q: Which sandbox provider should I use for a coding agent in production?**

For most production use cases, Modal is the recommended choice: GPU support, sub-second warm starts, competitive pricing, and a mature API. Start with E2B during development (free $100 credit, fast iteration), then migrate to Modal for production using the one-line provider switch in your agent config.

**Q: How does AGENTS.md differ from a system prompt?**

A system prompt is injected once at conversation start and applies globally. AGENTS.md is a workspace-level contract that the agent reads when it initializes in a given directory — it covers tools, constraints, and conventions specific to that project, not just behavioral instructions. Multiple agents can share an AGENTS.md, and it's version-controlled alongside the codebase it governs.

**Q: When will TypeScript support be available for the v2 harness features?**

OpenAI launched v2 as Python-first. TypeScript support for the configurable memory, sandbox, and filesystem tool features is planned but no official release date has been announced as of May 2026. The v1 TypeScript SDK continues to receive updates for the orchestration layer. Teams using TypeScript should follow the OpenAI developer blog for the TypeScript harness announcement.