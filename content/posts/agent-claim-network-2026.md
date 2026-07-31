---
title: "Agent Claim Network Review 2026: Terminal AI Assistant for Agent Knowledge Sharing"
date: 2026-07-31T16:04:14+00:00
tags:
  - agent claim network
  - ACN terminal assistant
  - agent knowledge sharing
  - multi-agent memory
  - MCP knowledge sharing
  - terminal AI assistant
description: "Agent Claim Network (ACN) is a terminal-native AI assistant that lets agents share verified knowledge via claims — a novel approach to multi-agent memory and collaboration."
draft: false
cover:
  image: "/images/agent-claim-network-2026.png"
  alt: "Agent Claim Network Review 2026: Terminal AI Assistant for Agent Knowledge Sharing"
  relative: false
schema: "schema-agent-claim-network-2026"
---

## What is Agent Claim Network (ACN)?

Agent Claim Network (ACN) is a terminal AI assistant and agent knowledge sharing platform launched on July 31, 2026 by Non-convex ft.tech (非凸科技). Unlike traditional memory tools that store raw data, ACN introduces a **claim-based knowledge sharing system** where agents publish structured judgments — each with an explicit holder, scope, confidence level, and evidence summary — that other agents can query, verify, and even dispute. Built in Rust and licensed under Apache-2.0/MIT, ACN runs on Apple Silicon Mac, Intel Mac, and x86_64 Ubuntu 22.04, supporting both Anthropic and OpenAI-compatible LLM providers. At version 0.2.1, it is a fresh entrant in the rapidly growing agent knowledge sharing market.

## Key Features — Terminal AI Assistant

ACN is first and foremost a terminal AI assistant. Before it is a knowledge sharing network, it is a full-featured CLI agent that can execute commands, manage sessions, and interact with LLM providers. This distinguishes it from pure memory-layer tools that only store and retrieve data.

### Subagent Parallelism and Background Execution

ACN supports running multiple subagents in parallel, each with its own context and session state. A background finalize supervisor manages these subagents, ensuring that long-running tasks complete without blocking the main session. This architecture is particularly useful for complex workflows where an agent needs to research, write, and verify simultaneously.

### MCP Integration

ACN implements the Model Context Protocol (MCP) with both stdio and Streamable HTTP transports. MCP connections are shared in-process, meaning multiple agents can access the same tool ecosystem without duplicating connections. This is a significant efficiency gain over tools that require separate MCP connections per agent instance.

### Multi-Provider LLM Support

The assistant works with Anthropic (Claude) and any OpenAI-compatible provider, giving users flexibility in choosing their underlying language model. This provider-agnostic design means ACN can adapt as new models emerge without requiring architectural changes.

## The Claim System — How Knowledge Sharing Works

The claim system is ACN's most innovative feature. Instead of storing raw memory blobs, agents publish **claims** — structured knowledge units with four mandatory fields:

| Field | Description | Example |
|-------|-------------|---------|
| **Holder** | The agent or entity making the claim | `writer-agent@blog-pipeline` |
| **Scope** | The domain or context the claim applies to | `agent-claim-network-2026` |
| **Confidence** | A numerical or categorical confidence rating | `0.92` or `high` |
| **Evidence Summary** | A concise justification or source reference | `Verified against GitHub README v0.2.1` |

### Well-Supported Judgments

Claims are not just free-form text. ACN enforces a "well-supported judgment" format, meaning every claim must include enough context for other agents to evaluate its reliability. This prevents the garbage-in-garbage-out problem that plagues simpler memory systems.

### Dispute System

One of the most philosophically interesting aspects of ACN is its dispute system. When two agents hold conflicting claims about the same topic, both claims can coexist. There is no forced consensus. Instead, the system surfaces both claims with their respective confidence levels and evidence, allowing downstream agents or human operators to make their own judgment. This is a deliberate design choice that acknowledges the reality of multi-agent systems: different agents with different training data, contexts, and perspectives will legitimately disagree.

### Privacy-First Design

A critical architectural decision: **memory never leaves the agent**. Only claims — with the holder's identity attached — are shared across the network. This means an agent's raw conversation history, internal reasoning, and private context remain local. What gets shared is a distilled, structured knowledge unit that the agent chooses to publish. This privacy boundary is essential for enterprise deployments where agents may handle sensitive data.

## Team Mode — Router and Maintainer Architecture

ACN's team mode separates knowledge retrieval from governance into two deployable binaries:

### Router (Retrieval)

The Router handles all knowledge queries. When an agent needs information, it sends a query to the Router, which searches the claim network and returns the most relevant results. The Router is optimized for low-latency retrieval and can be deployed as a standalone service.

### Maintainer (Governance)

The Maintainer handles claim lifecycle management: publishing new claims, resolving disputes, pruning stale knowledge, and enforcing trust policies. This separation of concerns means retrieval performance is not impacted by governance operations, and governance policies can be updated without touching the query path.

This architecture is reminiscent of the CQRS (Command Query Responsibility Segregation) pattern, applied to agent knowledge management. It allows teams to scale retrieval and governance independently based on their workload patterns.

## Memory System — MEMORY.md and USER.md

ACN's memory design is explicitly inspired by Hermes Agent's dual-file approach. Each agent maintains two files:

- **MEMORY.md**: Agent-specific notes, learned facts, and operational knowledge
- **USER.md**: User preferences, identity, and personal context

This separation mirrors the distinction between what an agent knows about its work and what it knows about its user. By keeping these files separate, ACN enables more granular sharing — an agent can share its MEMORY.md claims with other agents while keeping USER.md private.

## Installation and Quick Start

ACN supports three platforms at launch:

- **Apple Silicon Mac** (M1/M2/M3/M4)
- **Intel Mac**
- **x86_64 Ubuntu 22.04**

Installation is straightforward via the GitHub releases page. After installing, users configure their LLM provider (Anthropic or OpenAI-compatible) and can immediately start using the terminal assistant. MCP tools can be configured via the standard MCP configuration format.

The quick start flow:
1. Download the appropriate binary for your platform
2. Configure your LLM API key
3. (Optional) Configure MCP servers
4. Start the ACN terminal assistant
5. Begin publishing and querying claims

## Comparison with Competitors

The agent knowledge sharing market is nascent — most tools have fewer than 50 GitHub stars. Here is how ACN stacks up against the leading alternatives:

| Feature | ACN | Caura Memclaw | Kage | Lore | Hivemind |
|---------|-----|---------------|------|------|----------|
| **GitHub Stars** | 12 (launch day) | 396 | 31 | 7 | 1 |
| **Type** | Terminal AI Assistant + Knowledge Network | Governed Shared Memory | Verified Coding Memory | Cross-Agent Memory SDK | Metaskill for Skill Sharing |
| **Knowledge Format** | Structured Claims | Knowledge Graph | Verified Facts | Lessons | Skills/Experiences |
| **Dispute Support** | Yes — conflicting claims coexist | No | No | No | Voting-based |
| **Privacy Model** | Memory stays local, claims shared | Tenant-isolated | Codebase-scoped | Redaction support | Trust scores |
| **MCP Support** | Yes (stdio + Streamable HTTP) | Yes (MCP-native) | No | No | No |
| **Deployment** | Standalone binary | Server-based | CLI plugin | SDK | Metaskill |
| **Language** | Rust | Not specified | Not specified | Not specified | Not specified |
| **License** | Apache-2.0/MIT | Not specified | Not specified | Not specified | Not specified |

### Caura Memclaw (396★)

Caura Memclaw is the clear market leader by GitHub stars. It offers governed shared memory for AI agent fleets with trust tiers, keystone policies, audit trails, and a knowledge graph. It is MCP-native and designed for enterprise multi-agent, multi-tenant deployments. ACN's claim system offers a different philosophical approach — structured, disputable knowledge units vs. a governed knowledge graph.

### Kage (31★)

Kage focuses on persistent, verified memory specifically for coding agents. Every memory is checked against the current codebase to prevent stale knowledge. This codebase-aware verification is Kage's unique strength, but its scope is limited to coding agents, whereas ACN is a general-purpose terminal assistant.

### Lore (7★)

Lore is a lightweight cross-agent memory SDK where agents publish lessons and query shared knowledge. It includes built-in redaction support. Lore is simpler than ACN but lacks the structured claim format, dispute system, and terminal assistant capabilities.

### Hivemind (1★)

Hivemind is a metaskill for skill and experience sharing between agents, designed for Claude Code, Codex, and Opencode. It uses trust scores and voting to evaluate shared knowledge. Hivemind's voting mechanism is an alternative to ACN's dispute system — instead of letting conflicting claims coexist, Hivemind lets agents vote on the best answer.

## Use Cases and Target Audience

### AI Agent Developers

Developers building multi-agent systems need a way for their agents to share knowledge without sharing raw memory. ACN's claim system provides a structured, auditable knowledge layer that fits naturally into agent workflows.

### Enterprise AI Teams

For organizations running fleets of AI agents, ACN's privacy-first design (memory stays local, claims are shared) addresses compliance concerns. The Router/Maintainer architecture also supports the scale and governance requirements of enterprise deployments.

### Terminal Power Users

Users who prefer CLI-based AI assistants over GUI tools will appreciate ACN's terminal-native design. It integrates naturally with existing terminal workflows, MCP tools, and development pipelines.

### Open Source Contributors

At version 0.2.1 with Apache-2.0/MIT licensing, ACN is an open project with room for community contribution. The Rust codebase and well-documented architecture make it accessible for developers interested in agent infrastructure.

## Limitations and Considerations

### Very Early Stage

ACN launched on July 31, 2026 — the same day as this review. With 12 GitHub stars and version 0.2.1, it is extremely early. Users should expect bugs, missing features, and rapid API changes.

### Limited Community and Ecosystem

Compared to Caura Memclaw's 396 stars, ACN's community is tiny. This means fewer third-party integrations, less community documentation, and a higher burden on the core team for support.

### Platform Limitations

Currently supports only macOS (Apple Silicon and Intel) and Ubuntu 22.04 x86_64. Windows users and users on other Linux distributions will need to wait for broader platform support.

### Claim Quality Depends on Agent Quality

The claim system is only as good as the agents publishing claims. If agents publish low-confidence, poorly evidenced, or incorrect claims, the network's value degrades. The dispute system helps, but it requires active participation from multiple agents.

### No Built-in Human Review Workflow

While ACN has a dispute system for agent-to-agent disagreement, there is no built-in workflow for human review of claims. In regulated industries, this may be a gap that needs to be addressed with external tooling.

## Verdict — Is ACN Worth Trying in 2026?

**Yes, if you are building multi-agent systems and value structured knowledge sharing over raw memory storage.** ACN's claim-based approach is a genuinely novel contribution to the agent knowledge sharing space. The separation of memory (private) from claims (shared) is architecturally sound and addresses real privacy concerns in multi-agent deployments.

**Wait, if you need a mature, battle-tested solution.** At version 0.2.1 with 12 stars, ACN is not yet production-ready for mission-critical deployments. Caura Memclaw, with its larger community and more mature codebase, is the safer choice for enterprise teams today.

**Skip, if you only need a simple memory layer.** If your use case is straightforward memory persistence for a single agent, tools like Lore or even a simple file-based approach will serve you better without the complexity of a claim system.

ACN represents an interesting design direction for the agent knowledge sharing market. Its claim-based architecture, dispute system, and privacy-first design are ideas that will likely influence the next generation of agent collaboration tools, even if ACN itself remains a niche player. For developers and teams exploring the cutting edge of multi-agent systems, it is absolutely worth a weekend experiment.

## FAQ

### What is an agent claim network?

An agent claim network is a system where AI agents share structured knowledge units called "claims" — each with a holder, scope, confidence level, and evidence summary — instead of sharing raw memory or data. Agent Claim Network (ACN) is a specific implementation of this concept, launched in July 2026.

### How is ACN different from Caura Memclaw?

ACN is a terminal AI assistant with a claim-based knowledge sharing system, while Caura Memclaw is a governed shared memory layer with a knowledge graph. ACN uses structured, disputable claims that can coexist even when conflicting, whereas Memclaw uses trust tiers and keystone policies for governance. ACN also functions as a full terminal AI assistant, not just a memory layer.

### Does ACN support MCP (Model Context Protocol)?

Yes, ACN supports MCP with both stdio and Streamable HTTP transports. MCP connections are shared in-process, meaning multiple agents can access the same tool ecosystem without duplicating connections.

### Is ACN free and open source?

Yes, ACN is open source under dual Apache-2.0/MIT licensing. The source code is available on GitHub, and the binary releases are free to download and use.

### What platforms does ACN run on?

ACN currently supports Apple Silicon Mac (M1/M2/M3/M4), Intel Mac, and x86_64 Ubuntu 22.04. Windows and other Linux distributions are not yet supported.
