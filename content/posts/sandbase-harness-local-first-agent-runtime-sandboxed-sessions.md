---
title: "SandBase Agent Runtime: A Local-First Runtime with Sandboxed Sessions"
date: 2026-09-17T13:01:44+00:00
tags:
  - sandbase agent runtime
  - local-first agent runtime
  - self-hosted agent runtime
  - sandboxed AI agent sessions
  - agent runtime security
  - MCP agent runtime
  - AI agent infrastructure
description: "SandBase Harness is an open-source, local-first agent runtime with Docker/K8s sandboxed sessions, SQLite storage, credential vaults, audit trails, and MCP support. Learn how self-hosted, sandboxed AI agent sessions keep data on your own infrastructure."
draft: false
cover:
  image: "/images/sandbase-harness-local-first-agent-runtime-sandboxed-sessions.png"
  alt: "SandBase agent runtime: local-first agent runtime with sandboxed sessions"
  relative: false
schema: "schema-sandbase-harness-local-first-agent-runtime-sandboxed-sessions"
---

SandBase Harness is an open-source (Apache-2.0), local-first agent runtime that runs sessions, sandboxed tools, memory, credentials, and audit trails entirely on your own machine or infrastructure. It runs any model — OpenAI, Anthropic, DeepSeek V4, or any OpenAI-compatible endpoint — integrates MCP toolsets, and supports local process, Docker, Kubernetes, and self-hosted worker sandbox backends. In short, it turns a capable model into a production-grade, sandboxed, auditable agent without your data ever leaving your perimeter.

## What Is SandBase Agent Runtime?

SandBase agent runtime is the execution core of SandBase Harness, a self-hosted framework that gives autonomous agents a place to live and work. Instead of running each prompting loop in a stateless cloud call, SandBase persists sessions, environments, credential vaults, memory, and files in SQLite and executes tasks inside configurable sandboxes. Created in July 2026, the project has already accumulated 110-plus commits and is actively developed by liyangbing, with roughly 580-650 GitHub stars and 55-69 forks as of the September 2026 research date.

The term "harness" is deliberate. Like a test harness that isolates code under test, SandBase wraps an agent in a controlled shell where every tool call, file write, and network request is recorded against a recoverable session. It ships as a DeepSeek Harness (DSH) plugin bundle over the stdio MCP protocol, which means it plugs directly into MCP-aware clients rather than requiring a proprietary SDK.

What separates it from a typical Agent SDK is the persistence and isolation stack: resumable Server-Sent Events (SSE) for session replay, per-session containers, a credential vault, and permission policies with approval gates. These are the primitives production agents need but that a pure model API never provides.

## Why Production Agents Need More Than a Model Loop

A model loop — prompt, call the model, parse the tool result, repeat — is the starting point, not the finish line. In real production use, agents fail, get interrupted, leak a credential, or touch a file they should not have. The market data underlines how expensive those failures are. Gartner forecasts that 40 percent of enterprise applications will embed task-specific AI agents by the end of 2026, up from under 5 percent in 2025. Yet the same firm warns that more than 40 percent of agentic AI projects risk cancellation by 2027 without governance, observability, and ROI clarity.

That governance gap is exactly the product gap Agent SDKs leave open. The AI agents market was roughly USD 7.84 billion in 2025 and is projected to reach USD 52.62 billion by 2030; the broader agentic AI market sits near USD 7.06 billion in 2025 and is expected to reach USD 93.2 billion by 2032, a 44.6 percent CAGR, per MarketsandMarkets. Teams are spending on agents, but they are also getting burned by non-deterministic, unrecoverable, unobservable runs.

SandBase closes three gaps a bare model loop cannot:

1. **Persistence.** Sessions survive restarts. A sandbox crash does not destroy the conversation history.
2. **Replay and audit.** Resumable SSE means an interrupted run can be replayed from where it stopped, and every action is logged.
3. **Isolation and permissioning.** Tools run inside a sandbox with a permission policy, so a misbehaving agent cannot roam the host filesystem.

With Gartner attributing a large share of project cancellations to missing observability and governance, audit trails and replay are not developer niceties — they are the risk-management reason to buy a runtime at all. By 2028, Gartner projects 33 percent of enterprise software applications will include agentic AI (up from under 1 percent in 2024), and at least 15 percent of day-to-day work decisions will be made autonomously by agents. At that scale, an unauditable agent is a liability.

## The Four Sandbox Backends and How to Choose Between Them

SandBase agent runtime offers four sandbox backends, each mapping to a different trust level of the workload:

| Backend | Isolation model | Best for | Downsides |
|---------|-----------------|----------|-----------|
| Local process | Same host, process-level | Fast iteration, simple tool calls, low-risk writes | No filesystem isolation; host-level risk |
| Docker (per-session containers) | Container per session | Untrusted code, package installs, parallel workloads | Needs Docker daemon; image cold-start |
| Kubernetes (kubectl exec/cp) | Pod per workload | Scalable, multi-node, enterprise clusters | Cluster operational overhead; kubectl permissions |
| Self-hosted worker queue | Distributed workers | Offloaded batch jobs, remote runners | Extra orchestration to operate |

The decision framework is about workload trust and blast radius. A local process sandbox is fine when an agent only writes into a designated project directory and makes no network calls — think an internal code-refactoring helper. The moment an agent installs packages, spawns subprocesses, or touches files outside the project, you want a Docker per-session container so the blast radius of a bad command is a scrap container, not your host.

For regulated or large fleets, Kubernetes exec/cp gives you central policy, logging, and horizontal scaling across nodes. The self-hosted worker queue decouples heavy batch work from interactive sessions so a long job does not block a chat. The general rule: choose the weakest sandbox that still contains the specific risk, because stronger sandboxes cost more operational overhead and slower startup.

## Local-First by Design: SQLite Storage, Credentials, and Audit Trails

Local-first is not just a deployment preference; it is an architectural choice encoded in how state is stored. SandBase keeps agents, sessions, environments, memory, files, and credential vaults in SQLite, all on your own infrastructure. Nothing is shuttled to a vendor cloud to persist state.

This matters most for data ownership. With a persistent cloud sandbox VM — the model behind several hosted agent products — source code and data effectively leave the building on every session. SandBase inverts that: the only thing that touches a remote service is the model API call itself. For finance, healthcare, and defense workloads, where data-residency mandates are non-negotiable, that is often the deciding factor. 67 percent of enterprises express concern about AI data privacy, and 42 percent of EU companies plan on-premise AI deployment by 2027; the average data breach now costs USD 4.44 million, per IBM 2023 data. Keeping session state, credentials, and audit logs in your own SQLite store is the compliance-safe default.

The audit trail deserves emphasis because it is the governance control Gartner says projects are missing. Every tool call, result, and state transition can be replayed via resumable Server-Sent Events. If an agent makes an unwanted change, you have a precise record of what it did and in what order — the difference between an explainable incident and a mystery. Permission policies with approval gates add a human-in-the-loop brake for high-stakes actions like file deletion or external payments.

Credentials are another local-first win. Instead of scattering API tokens in environment variables, SandBase stores them in a vault tied to environments, so the agent only sees the credentials appropriate to its session. This is a meaningful step up from pasting secrets into prompts.

## Model-Agnostic and MCP-Native: Avoiding Lock-In

A common objection to agent platforms is model and tool lock-in. SandBase agent runtime addresses it on both axes. It runs OpenAI, Anthropic, any OpenAI-compatible endpoint including DeepSeek V4, and integrates existing MCP toolsets. You bring your own model and your own tools, and the harness standardizes sessions, sandboxing, and audit around them.

MCP (Model Context Protocol) compatibility is especially relevant because it means SandBase is not asking you to throw away the tools you already use. Any MCP server you have — file access, web search, databases, internal APIs — can be wired into a sandboxed session. And because the whole thing ships as a DeepSeek Harness (DSH) plugin bundle over stdio MCP, clients that speak MCP can adopt it without a rewrite.

Anti-lock-in also extends to the sandbox backends themselves. Because local process, Docker, Kubernetes, and worker queue are pluggable, you are not frozen into a single execution model. Switch from local iteration to Docker in production without switching runtimes. This "bring your own everything, harness standardizes the shell" posture is what makes the runtime attractive to teams that have already invested in models, toolsets, and infrastructure.

## SandBase Harness vs. Suna, Maka, and Cloud-Centric Runtimes

SandBase does not exist in a vacuum, and the comparison against peers clarifies what is distinctive. Suna is a local-first terminal agent runtime with isolated subtasks and an intent-aware Guard, but it is PolyForm Noncommercial licensed, has roughly 18 stars, does not offer a full OS sandbox, and has limited MCP and vector memory support. Maka-agent is an Apache-2.0 local-first desktop assistant built on a "log is the runtime" model with durable TaskRuns, but it targets desktop/CLI surfaces rather than a deployment-oriented runtime. OpenClaw uses a two-tier model that restricts host sessions to paired contacts and runs group sessions in Docker — a useful lesson in sandbox boundaries, though its design centers on channels rather than as a general runtime.

| Capability | SandBase Harness | Suna | Maka-agent | Cloud VM runtime (e.g., Devin-style) |
|-----------|------------------|------|------------|---------------------------------------|
| License | Apache-2.0 | PolyForm Noncommercial | Apache-2.0 | Proprietary |
| Data location | Your infra | Your infra | Your infra | Vendor cloud |
| OS-level sandbox | Docker/K8s/process/worker | Partial; no full OS sandbox | Not full | Cloud VM |
| MCP support | Yes | Limited | Via gateway | Varies |
| Audit/replay | Resumable SSE | Limited | Event-log replay | Vendor logs |
| Deployment targets | Server/self-host | Terminal/IDE | Desktop/CLI | Cloud |

The cloud-vs-local-first comparison is the sharpest. As Daniel Vaughan's Codex CLI analysis notes, the architectural choice between a cloud sandbox and local-first execution matters more than benchmark scores for enterprise teams. Local-first yields sub-second feedback-loop latency, keeps source and data inside the perimeter, eliminates per-task cloud billing, and satisfies data residency. Cloud VMs offer convenience and zero internal operations, at the cost of sending code and data to a vendor and accumulating metered spend.

## Security and Governance in Regulated Industries

For finance, healthcare, and defense, the compliance case for a self-hosted agent runtime is straightforward: data residency mandates simply do not allow session state or audit logs to live in a third-party cloud. By running entirely on-prem or in your own VPC, SandBase agent runtime satisfies those requirements by construction. With 67 percent of enterprises already worried about AI data privacy, and data breaches averaging USD 4.44 million, the cost of a leak can exceed the entire budget of many agent projects.

The security architecture holds up under scrutiny because it layers controls rather than relying on a single mechanism:

- **Sandbox isolation** contains tool execution to a controlled environment.
- **Credential vault** prevents token leak-by-prompt and scopes secrets per environment.
- **Permission policies + approval gates** block or require human sign-off on high-risk actions.
- **Audit trails + SSE replay** provide deterministic reconstruction of any incident.

The audit trail doubles as the governance evidence Gartner says agentic projects are missing. With more than 40 percent of agentic AI projects at risk of cancellation by 2027, an operator that can demonstrate control — "here is exactly what the agent did, and here is the approval it required" — is far less likely to be cancelled on governance grounds. This is a risk-management purchase, not merely a developer convenience.

One caution for regulated rollouts: the audit trail is only as strong as its retention policy. Configure log rotation and off-site backup of the SQLite audit store, and restrict who can mutate it, otherwise the evidence chain weakens.

## Getting Started with SandBase Harness (Install + First Session)

To use the sandbase agent runtime, clone the open-source repository and run it as a DeepSeek Harness plugin bundle over stdio MCP, then launch a sandboxed session with a chosen model and backend. The flow is: configure a model provider (OpenAI, Anthropic, or an OpenAI-compatible endpoint such as DeepSeek V4), define a sandbox backend (local process for a first test), store any credentials you need in the vault, and start a session. Resumable SSE means you can disconnect and reconnect without losing history.

For a first session, the local process backend is the fastest path. Create a small task — for example, "summarize these three files into a markdown report" — and watch the tool calls and audit events stream back. Once that works, promote the same session to a Docker per-session container to confirm your code runs behind real filesystem isolation before you trust it with anything sensitive. Because the harness speaks MCP, point it at an existing MCP server to exercise tool integration.

The key habit to adopt early is the approval policy. Start strict: require approval for write operations outside a scratch directory. Tighten or relax as you observe what the agent legitimately needs. This gives you visibility into the agent's behavior before you grant it broad rights, and it builds the audit trail you will rely on later.

## When to Choose a Self-Hosted Agent Runtime (and When Not To)

A self-hosted agent runtime is the right call when any of these apply: your data must stay in-house for residency or policy reasons; you need sub-second latency on internal workloads; you want to avoid per-task cloud billing scaling with agent volume; or you must produce deterministic audit evidence. Regulated finance, healthcare, and defense are the clearest fits — they get compliance and governance in one purchase.

Defer a self-hosted runtime when you do not yet have the operational capacity to run container or Kubernetes sandboxes, when your agent usage is exploratory and a hosted provider's convenience outweighs cost, or when you are unwilling to own backup, patching, and retention of the runtime. And note the honest trade-off: local-first keeps data inside but pushes infrastructure and security ops onto you. Sub-second feedback latency and no per-task cloud billing come with the cost of operating the environment yourself.

The market's direction is clear: Gartner expects 40 percent of enterprise applications to embed task-specific AI agents by end of 2026, and 33 percent of enterprise software to include agentic AI by 2028. As agents move from demos to production, the runtimes that succeed will be the ones that give operators persistence, isolation, and audit — exactly what SandBase agent runtime is built to provide.

## FAQ

### Is SandBase agent runtime free to use?
Yes. SandBase Harness is open-source under the Apache-2.0 license, so you can use, modify, and self-host it without licensing fees. You still pay for any model API usage and the infrastructure you choose to run it on.

### What is the difference between a sandbox backend and a sandboxed session?
A sandbox backend is the isolation layer — local process, Docker, Kubernetes, or a self-hosted worker queue. A sandboxed session is a single agent run executed inside that isolation layer. Choosing a backend determines how much isolation every session gets.

### Can SandBase agent runtime work with DeepSeek V4?
Yes. Because it is model-agnostic and accepts any OpenAI-compatible endpoint, it runs DeepSeek V4 alongside OpenAI, Anthropic, and other compatible models. It also ships as a DeepSeek Harness (DSH) plugin bundle over stdio MCP.

### How does SandBase agent runtime protect credentials?
It stores credentials in an encrypted vault tied to environments, so an agent only sees the secrets its current session is permitted to use. This avoids scattering API tokens and limits the blast radius if a session is compromised.

### Is SandBase agent runtime suitable for regulated industries?
Yes, and it is one of its strongest use cases. Because sessions, credential vaults, memory, and audit trails all live in your own infrastructure, finance, healthcare, and defense teams satisfy data-residency mandates by construction rather than by relying on a vendor to keep data in-jurisdiction.
