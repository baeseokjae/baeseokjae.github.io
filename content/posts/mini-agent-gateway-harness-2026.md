---
title: "Mini Agent Gateway: Building Code That Constrains the LLM — An Agent Gateway Harness Architecture Guide"
date: "2026-08-25T10:03:46+00:00"
tags:
  - agent gateway harness architecture
  - LLM agent harness
  - mini agent harness
  - constrain LLM output
  - tool call validation
  - LLM gateway routing
  - agent safety guardrails
  - ReAct agent loop
  - schema-based LLM argument validation
  - agent cost optimization model routing
  - self-hosted LLM gateway
description: "A mini agent gateway constrains the LLM with schema validation, tool allow-lists, guardrails, and model routing. Here's how to build one with a ReAct loop and a dynamic tool registry."
draft: false
cover:
  image: "/images/mini-agent-gateway-harness-2026.png"
  alt: "Mini Agent Gateway: Building Code That Constrains the LLM — An Agent Gateway Harness Architecture Guide"
  relative: false
schema: "schema-mini-agent-gateway-harness-2026"
---

A mini agent gateway is the code layer you place between your LLM and its tools that constrains what the model can say, call, and spend. Instead of trusting a raw model endpoint, you add schema-based argument validation, a tool allow-list, pre-execution guardrails, and model routing so every model call is checked before it touches a real system. The result is an LLM you can actually run in production: cheaper, safer, and deterministic.

## What Is a Mini Agent Gateway (Agent Harness) and Why Build Your Own?

An agent gateway — often called an agent harness — is the structured execution environment that surrounds an LLM and does most of the actual engineering work. MongoDB makes the point bluntly in its post "The LLM Is the Smallest Part": production agent systems are dominated by the harness that owns state, memory, tooling, routing, and guardrails, not by the model itself ([source](https://www.mongodb.com/company/blog/technical/agent-harness-the-llm-is-the-smallest-part)). A *mini* version is the same idea scaled down: a lightweight, self-hosted gateway you can build in a few hundred lines of Python rather than buying an enterprise platform.

Why build your own when managed gateways exist? Three reasons dominate:

- **You control the constraints.** Schema validation, tool allow-lists, and guardrails are not abstractions you configure in a dashboard — they are code you own and can audit.
- **You control cost and routing.** You decide which calls go to a cheap on-device model and which deserve an expensive frontier model, instead of paying the vendor's default.
- **You avoid lock-in.** A gateway speaks the OpenAI-compatible API, so you can swap vLLM, Ollama, or FastAPI backends without rewriting your agent logic.

The core shift in thinking is this: the LLM is a pluggable component, not the system. The gateway is the system. Everything that makes an agent trustworthy — validation, safety, routing, tracing — lives in the harness, not in the model weights.

## How Does Code Actually Constrain an LLM? (Schema Validation, Tool Allow-Lists, and Guardrails)

An LLM is non-deterministic by nature, but a harness turns it into a *bounded* component. Constraint is not done by hoping the model behaves; it is done by hard engineering gates that run *before* and *after* every model call.

### Schema-based argument validation

The most important single constraint is that the LLM cannot call a tool with arbitrary arguments. You define a JSON Schema for every tool, and the harness validates the model's proposed arguments before execution. This mirrors the approach in the [Anicanic mini-agent-harness](https://github.com/Anicanic/mini-agent-harness), where a `schemas.py` layer plus a tool normalization layer constrain exactly what the LLM can call. If the model emits arguments that fail validation, the harness rejects the call and feeds the error back into the next ReAct step — teaching the model to correct itself instead of silently executing bad input.

### Tool allow-lists

Instead of exposing every function on your machine to the model, you present a curated registry of tools. The gateway decides *what the model can even see*. If the LLM cannot see a tool, it cannot call it. A single `tools.json` file drives the tool descriptions, the validation schemas, and runtime registration simultaneously — one source of truth that guarantees the model's view of the toolset matches the harness's enforcement.

### Pre-execution guardrails

Guardrails run checks on both input and output: content sanitization, PII filtering, safety-policy verification, and command allow-lists. The [glenshadow agent-harness-llm-gateway-platform](https://github.com/glenshadow/agent-harness-llm-gateway-platform) implements these as a first-class layer between the model and your tools, applying policy checks *before* the tool executes so a malicious or hallucinated tool call never reaches a real system.

### Why constraint matters more than ever

Community demand for exactly this kind of tooling is visible and growing. Claw Patrol, an agent security firewall that sits between the LLM and its tools and enforces policy, drew roughly 112 points on Hacker News in 2026 — a strong signal that developers actively want to constrain agent tool calls ([source](https://hn.algolia.com/api/v1/search?query=agent%20gateway%20LLM)). The lesson is that "just prompt it to be safe" does not scale; code-level gates do.

## Core Architecture: The ReAct Loop and a Dynamic Tool Registry

At the heart of most mini gateways is a ReAct (Reason + Act) loop. The pattern is simple and powerful: the model reasons about a task, decides on a tool call, the harness validates and executes it, and the result is fed back into the model for the next round of reasoning. This repeats until the task is solved or a stop condition fires.

A clean, reference architecture — drawn from the [Anicanic mini-agent-harness](https://github.com/Anicanic/mini-agent-harness) — looks like this:

```
User Input -> Web UI/CLI -> agent.py -> prompts.py -> dispatcher.py
    -> schemas.py -> tools.json -> tools.py -> Tool Result -> ReAct loop
```

Breaking it down:

- **`agent.py`** — the entry point that owns the loop and the conversation state.
- **`prompts.py`** — the system prompt that tells the model how to reason and which tools exist.
- **`dispatcher.py`** — decides which tool to invoke based on the model's structured output.
- **`schemas.py`** — the JSON Schema definitions that validate every tool call.
- **`tools.json`** — the single source of truth for tool descriptions, schemas, and registration.
- **`tools.py`** — the actual executable functions the model is allowed to reach.

The dynamic tool registry is what keeps the loop extensible. Because `tools.json` drives descriptions, validation, and registration simultaneously, adding a new tool is a one-line change: write the function in `tools.py`, add its schema, and the gateway automatically exposes it to the model with validation built in. No hand-written glue between the model's JSON output and your Python functions.

## Building the Gateway Step by Step: Prompts, Schemas, Dispatcher, and Tools

Here is the build-up path you can follow, starting small and layering in constraint as you go.

**Step 1 — Start with a bare ReAct loop.** Stand up a minimal loop that calls an OpenAI-compatible endpoint (vLLM, Ollama, or FastAPI all work) and returns text. Get the conversation flowing before you add any safety.

**Step 2 — Add a dynamic tool registry.** Create `tools.json` listing one simple tool (say, a calculator or a date fetcher). Register it at runtime so the model can see it. The key win: the model now emits structured tool calls instead of free text.

**Step 3 — Add schema validation.** Define the JSON Schema for each tool's arguments in `schemas.py`. Validate every proposed call before executing. This is the first real constraint — the moment the LLM stops being able to pass arbitrary arguments to your code.

**Step 4 — Build the dispatcher.** `dispatcher.py` parses the model's validated tool call, invokes the matching function in `tools.py`, and returns the result to the loop. Add error handling so a failed validation loops back to the model as a correction signal.

**Step 5 — Add tracing.** Log every step: the prompt, the model's choice, the validated call, the tool result, and the cost. Tracing is what turns a black-box loop into a debuggable, auditable system.

**Step 6 — Layer in guardrails.** Add input sanitization and PII filtering before execution, plus a policy check that a tool call is actually allowed. This is the step that makes the gateway safe enough for real systems.

Start with step 1 and stop at whatever layer your risk tolerance requires. A personal assistant script might only need steps 1–3; a production-facing agent needs all six.

## How to Route Models to Cut Cost Without Sacrificing Quality

One of the strongest economic arguments for a gateway is model routing: sending the right call to the right model. A gateway is uniquely positioned to do this because it sees every request in one place.

The [glenshadow](https://github.com/glenshadow/agent-harness-llm-gateway-platform) reference implements dynamic routing across Gemini 2.5 Flash/Pro, Claude 3.5 Sonnet, and GPT-4o based on latency, cost, or capability. Arch GW goes further and markets a distributed gateway "engineered with small LLMs," reflecting a clear industry trend toward routing agent traffic through cheaper or on-device models ([source](https://docs.archgw.com/)). Rayline is a working example of the same idea in the wild: it routes Claude Code subagents to on-device and cheaper models, optimizing cost and latency by sending each call to the cheapest model that can handle it ([source](https://rayline.ai/)).

Practical routing rules you can implement today:

- **Classify by task type.** Simple extraction and summarization go to a small on-device model; complex multi-step reasoning goes to a frontier model.
- **Classify by risk.** Any call that touches a destructive tool gets routed to a stronger model and passes through stricter guardrails.
- **Classify by token budget.** High-volume, low-stakes calls get the cheap model; low-volume, high-stakes calls get the best model.

A simple `route()` function at the top of your dispatcher can decide the model based on intent, tool, or user tier. Even a coarse two-tier split — cheap model for routine steps, premium model for the final synthesis — typically cuts spend significantly while keeping output quality within acceptable bounds.

## Security Patterns: Proxy Isolation, PII Filtering, and Pre-Execution Guardrails

Production gateways treat security as a first-class concern, not an afterthought. Three patterns matter most.

**Zero-secret-exposure proxy.** The gateway runs as a full-stack proxy so API keys stay isolated on the backend and never reach the client. This is the pattern the [glenshadow](https://github.com/glenshadow/agent-harness-llm-gateway-platform) design calls out explicitly: users interact through the gateway, and their credentials never touch browser or CLI sessions. It is the difference between an agent that is safe to deploy and one that leaks keys the moment a prompt injection slips through.

**PII filtering and content sanitization.** Before any tool executes, the harness scrubs input for personally identifiable information and sanitizes content against injection attempts. If an attacker tricks the model into emitting a destructive tool call, the sanitizer is a second line of defense that does not rely on the model behaving.

**Pre-execution guardrails.** Policy verification runs *before* the tool call, not after. The gateway checks whether the proposed action is permitted — is this file in the allow-list? Is this command allowed? Is this network endpoint trusted? — and refuses if it is not. This is the exact posture of Claw Patrol, which positions itself as a security firewall between the LLM and its tools, proving the gateway pattern as a safety mechanism rather than just an optimization ([source](https://github.com/denoland/clawpatrol)).

## Comparing Direct API Calls vs a Gateway vs a Full Harness

The decision of how much infrastructure to build depends on what you are protecting. Here is a practical comparison:

| Capability | Direct API Call | Mini Agent Gateway | Full Agent Harness |
|------------|----------------|--------------------|--------------------|
| Tool-call validation | None — you parse output yourself | Schema-based, enforced in code | Schema-based, enforced in code |
| Tool allow-list | Manual | Yes, via a single registry | Yes, plus role-based access |
| Model routing | None | Yes, per-request | Yes, per-request + per-tool |
| API-key isolation | Keys exposed to clients | Zero-secret proxy | Zero-secret proxy |
| Pre-execution guardrails | None | PII filter + policy check | Full safety verification suite |
| Memory / state | Manual | In-loop only | Durable, DB-backed |
| Tracing | None | Basic step logging | Full observability |
| Build effort | Minutes | A few hundred lines | Weeks + a data platform |
| Best for | Prototypes, scripts | Personal agents, small teams | Production, enterprise, regulated |

The takeaway is a spectrum rather than a binary choice. Direct API calls are fine for a prototype where a bad call has no real consequence. A mini gateway is the sweet spot for most working agents: it delivers the constraint, routing, and guardrails that make an LLM trustworthy without the operational cost of a full platform. A full harness — what MongoDB calls the production-grade agent system — becomes necessary when you need durable state, multi-agent coordination, and enterprise governance ([source](https://www.mongodb.com/company/blog/technical/agent-harness-the-llm-is-the-smallest-part)).

## FAQ

**What is a mini agent gateway?**
A mini agent gateway (or agent harness) is a lightweight, self-hosted code layer between an LLM and its tools that constrains what the model can call and spend. It adds schema validation, tool allow-lists, guardrails, and model routing around a model endpoint you already use.

**How does code constrain what an LLM can do?**
By refusing to execute anything that does not pass a gate. Schema validation rejects malformed tool arguments, a tool allow-list hides tools the model is not allowed to use, and pre-execution guardrails sanitize input and verify policies before any tool runs. The LLM proposes; the harness disposes.

**Why route agent traffic through cheaper models?**
Because most calls do not need a frontier model. Routing routine or low-risk steps to small on-device models cuts token cost and latency, while reserving expensive frontier models for complex reasoning. This is the pattern used by tools like Rayline and Arch GW.

**Is a gateway only for security?**
No — it is a dual win. The same layer that enforces safety also enables cost optimization through routing, and it centralizes tracing and observability. Security and efficiency come from the same architectural decision: putting code in charge of every model call.

**Do I need a full agent harness instead?**
Only if you need durable state, multi-agent coordination, or enterprise governance. For a personal assistant or a small team's agent, a mini gateway delivers most of the safety and cost benefits in a few hundred lines of code. Move to a full harness when your agent outgrows in-loop memory and single-process execution.
