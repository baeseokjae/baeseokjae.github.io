---
title: "Agent Memory Layer Comparison 2026: Déjà Vu vs Mem0 vs Zep vs Agent Memory MCP"
date: 2026-07-16T21:02:16+00:00
tags:
  - agent memory layer
  - AI agent memory comparison
  - Mem0 vs Zep vs Déjà Vu
  - agent memory MCP
  - temporal knowledge graph agent memory
  - local-first agent memory
  - agent memory benchmark LoCoMo
  - LongMemEval agent memory
  - serverless memory for AI agents
  - agent memory architecture 2026
  - persistent memory AI agents
  - agent session log indexing
  - Graphiti knowledge graph
  - MCP memory server
  - agent memory privacy
description: "Compare Déjà Vu, Mem0, Zep, and Agent Memory MCP — the top agent memory layer solutions in 2026 across performance, privacy, pricing, and architecture."
draft: false
cover:
  image: "/images/agent-memory-comparison-2026.png"
  alt: "Agent Memory Layer Comparison 2026: Déjà Vu vs Mem0 vs Zep vs Agent Memory MCP"
  relative: false
schema: "schema-agent-memory-comparison-2026"
---

## Introduction — Why Agent Memory Matters in 2026

Agent memory is the single most important infrastructure decision for production AI agents in 2026. Without a persistent memory layer, every agent conversation starts from scratch — no user preferences, no session history, no learned behaviors. The four leading solutions — Déjà Vu, Mem0, Zep, and Agent Memory MCP — take fundamentally different approaches to solving this problem, and choosing the wrong one can cost you in latency, privacy, vendor lock-in, or benchmark credibility. This comparison breaks down each solution's architecture, performance, pricing, and ideal use case so you can make an informed decision for your agent stack.

## The Four Contenders at a Glance

The agent memory layer market in 2026 has fragmented into four distinct categories, each with a different philosophy about how agents should remember.

### Déjà Vu — Retroactive Session Log Indexing

Déjà Vu is a zero-dependency Go binary that takes a radically different approach from every other memory solution: it does not capture anything. Instead, it indexes agent session logs that already exist on disk. Built by vshulcz, it supports over eight agent harnesses including Claude Code, Codex, opencode, aider, Gemini CLI, Cursor, Antigravity, and Grok Build. Its warm search latency is an astonishing 7-9ms typical, with a worst-case of ~40ms over gigabytes of logs. The index compresses to roughly 2.4% of the original corpus size — a 1GB log directory becomes a 24MB index. Déjà Vu is privacy-first by design: there is no network path in its indexing or search code, and credentials are redacted at index time. It also ships an MCP recall tool for agent self-querying and auto-recall via SessionStart hooks.

### Mem0 — Cloud-Native Semantic Memory Platform

Mem0 is a Y Combinator-backed cloud memory layer that uses a semantic graph to link user profiles with preference nodes. It performs autonomous semantic extraction from conversational streams, building a structured knowledge graph of user preferences, facts, and relationships over time. Mem0 integrates with LangChain, CrewAI, and other popular agent frameworks. However, it is cloud-only — requiring an API key and costing $40-50+ per month. Mem0 published benchmark results claiming state-of-the-art performance on the LoCoMo benchmark, though those claims have been contested by Zep with evidence of implementation errors in Zep's evaluation.

### Zep — Temporal Knowledge Graph Memory

Zep offers both an open-source Community Edition and a commercial Cloud tier. Its core innovation is Graphiti, a temporal knowledge graph that tracks fact validity over time using `valid_at` and `invalid_at` metadata on graph edges. This temporal awareness is critical for agents that need to know not just what a user said, but whether that information is still current. Zep asynchronously precomputes graph and related facts for low-latency deterministic retrieval, supports a full CRUD API for fine-grained data control, and recently added Attribute-Based Access Control (ABAC) for enterprise security compliance. The Community Edition was open-sourced in September 2024 and has seen rapid adoption.

### Agent Memory MCP — The Protocol Standard

Agent Memory MCP is not a memory platform itself but a protocol — the Model Context Protocol — that has become the universal connector for agent memory tools. MCP defines a standard interface for agents to read from and write to memory servers, enabling a plug-and-play ecosystem where any MCP-compatible memory backend can be swapped in without changing agent code. Déjà Vu ships an MCP recall tool, Zep offers MCP integration, and the protocol is rapidly becoming the lingua franca of agent memory. For teams building multi-agent systems, MCP compatibility is increasingly a non-negotiable requirement.

## Head-to-Head Comparison

### Architecture & Storage Model

| Feature | Déjà Vu | Mem0 | Zep | Agent Memory MCP |
|---|---|---|---|---|
| **Core approach** | Retroactive log indexing | Semantic graph extraction | Temporal knowledge graph | Protocol standard |
| **Storage** | On-disk index (~2.4% of corpus) | Cloud-hosted graph DB | Local or cloud graph DB | Depends on backend |
| **Data model** | Flat search index | User-preference graph | Temporal graph with edge timestamps | Abstracted by protocol |
| **Capture mechanism** | None (reads existing logs) | Autonomous extraction from streams | Async graph precomputation | Via MCP server |
| **LLM in CRUD path** | No | Yes | No (precomputed) | Depends on server |
| **Temporal awareness** | No (static index) | Limited | Full (valid_at/invalid_at) | Depends on server |

Déjà Vu's architecture is the simplest: it indexes what agents already wrote to disk. There is no capture step, no running service, and no cloud dependency. This makes it ideal for developers who want zero infrastructure overhead. The trade-off is that it has no temporal awareness — it cannot distinguish between a preference stated yesterday and one stated six months ago.

Mem0 builds a semantic graph by extracting entities and relationships from conversation text using an LLM. This means every memory write incurs an LLM call, adding latency and cost. The graph structure enables rich relationship queries — "what does this user prefer in Italian restaurants?" — but the cloud dependency means your agent's memory stops working if the API is unreachable.

Zep's temporal knowledge graph is the most sophisticated storage model. Every fact is stored with `valid_at` and `invalid_at` timestamps, enabling the agent to answer time-sensitive questions like "what was the user's shipping address last month?" The graph is precomputed asynchronously, so reads are deterministic and low-latency without requiring an LLM in the critical path.

Agent Memory MCP abstracts the storage model entirely. Your agent talks to an MCP server, and the server handles whatever backend it uses. This is the most flexible option but adds a protocol layer that may introduce latency.

### Latency & Performance Benchmarks

| Metric | Déjà Vu | Mem0 | Zep | Notes |
|---|---|---|---|---|
| **Read latency (typical)** | 7-9ms | ~200-500ms (LLM-dependent) | ~50-100ms | Déjà Vu is 10-50x faster |
| **Read latency (p95)** | ~40ms | Not published | 0.632s (concurrent) | Zep's published figure |
| **Index/build time** | Fast (Go binary) | N/A (real-time) | Async precomputation | Déjà Vu indexes offline |
| **Memory overhead** | ~2.4% of corpus | Cloud-hosted | Cloud or local | Déjà Vu is most efficient |
| **Concurrent search** | Single-threaded | Cloud-scaled | 0.632s p95 | Zep published concurrent data |

Déjà Vu's performance numbers are remarkable: 7-9ms typical warm search and ~40ms worst-case over a 3.3GB corpus of 1,250+ sessions. This is possible because it is a pure Go binary with no network calls and no LLM involvement. The index is a flat, optimized structure designed for fast keyword and semantic search.

Zep's published p95 search latency is 0.632s for concurrent searches, compared to Mem0 Graph's 0.657s — a statistical tie. However, Zep argues that its temporal knowledge graph provides richer, more accurate results that justify the comparable latency.

Mem0's latency is harder to benchmark because every memory operation may involve an LLM call for entity extraction. In practice, users report 200-500ms per operation, with significant variance depending on the LLM provider and network conditions.

### Privacy & Data Sovereignty

| Aspect | Déjà Vu | Mem0 | Zep | Agent Memory MCP |
|---|---|---|---|---|
| **Data location** | Local disk | Cloud servers | Local (CE) or Cloud | Depends on server |
| **Network required** | No | Yes | Optional | Optional |
| **Credential handling** | Redacted at index time | Server-side | Configurable | Depends on server |
| **Open source** | Yes | No | Yes (CE) | Yes (protocol) |
| **Self-hostable** | Yes | No | Yes (CE) | Yes |

Privacy is where the solutions diverge most dramatically. Déjà Vu is the clear winner for privacy-conscious teams: it has no network path in its indexing or search code, credentials are redacted at index time, and the entire system runs on local disk. Your agent's memory never leaves your machine.

Mem0 is at the opposite end of the spectrum. As a cloud-only service, all conversation data is processed and stored on Mem0's servers. For teams subject to GDPR, HIPAA, or other data residency requirements, this may be a dealbreaker.

Zep offers a middle path. The Community Edition is fully self-hostable and open-source, giving you data sovereignty. The Cloud tier adds enterprise features like ABAC and managed infrastructure. This makes Zep suitable for organizations that want control but may not want to operate their own graph database.

Agent Memory MCP is protocol-level and inherits the privacy posture of whatever server you choose. You can run a local MCP memory server for full privacy or connect to a cloud MCP server for managed infrastructure.

### Pricing & Deployment Models

| Solution | Pricing | Deployment | Best for |
|---|---|---|---|
| **Déjà Vu** | Free (open-source) | Local binary | Solo devs, privacy-first teams |
| **Mem0** | $40-50+/month | Cloud-only | Teams already in cloud ecosystem |
| **Zep CE** | Free (open-source) | Self-hosted | Teams wanting control + features |
| **Zep Cloud** | Usage-based | Managed | Enterprise teams |
| **MCP Memory** | Free (protocol) | Any | Teams wanting flexibility |

Déjà Vu and Zep Community Edition are both free and open-source, but they serve different needs. Déjà Vu is a lightweight binary you run alongside your agent — no database, no dependencies. Zep CE requires running a graph database but offers richer memory features.

Mem0's $40-50+/month pricing may seem modest, but it adds up across multiple agents and environments. For a team running five agents in production, that is $200-250/month for memory alone.

### Framework & Harness Support

Déjà Vu leads in harness support with compatibility for Claude Code, Codex, opencode, aider, Gemini CLI, Cursor, Antigravity, and Grok Build. Mem0 integrates with LangChain and CrewAI. Zep offers SDKs for Python and TypeScript with integrations for LangChain, LlamaIndex, and direct API access. Agent Memory MCP is framework-agnostic — any agent that speaks MCP can use any MCP-compatible memory server.

## The Benchmark Controversy: LoCoMo vs LongMemEval

The agent memory field is currently embroiled in a benchmark war that reveals deeper problems with how we evaluate memory systems. Zep published a detailed critique of the LoCoMo benchmark, which Mem0 had used to claim state-of-the-art performance.

Zep's analysis identified three fundamental flaws in LoCoMo. First, the benchmark conversations average only 16,000-26,000 tokens — well within the context window of modern LLMs. This means a model with a large context window could theoretically answer memory questions without any external memory system at all, making the benchmark a test of context length rather than memory quality. Second, LoCoMo does not test knowledge updates — it cannot distinguish between a system that remembers a fact correctly and one that fails to update when that fact changes. Third, Zep identified data quality issues in the benchmark dataset.

When Zep ran its own evaluation correcting for these issues, it achieved a 75.14% J score on LoCoMo compared to Mem0 Graph's approximately 68% — a roughly 10% advantage. Zep also claims that Mem0's evaluation of Zep had implementation errors including an incorrect user model, improper timestamp handling, and sequential instead of parallel searches.

Zep advocates for LongMemEval as a superior alternative. LongMemEval features significantly longer conversations averaging 115,000 tokens, which better stress-test real memory systems. It also includes temporal reasoning tasks that require the system to track how facts change over time — something LoCoMo does not test.

The takeaway for practitioners: do not make purchasing decisions based on LoCoMo scores alone. The benchmark is widely considered insufficient for evaluating production memory systems. If you are evaluating memory layers, design your own evaluation that reflects your actual use case — conversation lengths, update patterns, and query types that match your deployment.

## The Emerging Three-Tier Architecture

A consensus is forming among production agent teams that a single memory layer is insufficient. The emerging best practice is a three-tier architecture:

**Tier 1: Session Log Memory (Zep or custom).** This is the raw message database with auto-summarization and message-indexing pipelines. It captures the full conversation history and provides search over past interactions. Zep is the leading solution for this tier, but a custom implementation using a vector database is also common.

**Tier 2: Personalization Memory (Mem0 or equivalent).** This is a semantic graph linking user profiles with preference nodes. It extracts and stores user preferences, habits, and personal facts. Mem0 dominates this tier, but Zep's temporal graph can also serve this role.

**Tier 3: Governance Memory (ContextNest or custom).** This is a deterministic, version-controlled memory layer that uses SHA-256 hash chains and steward approval for compliance-critical applications. Unlike the probabilistic approaches of Zep and Mem0, governance memory provides auditable, tamper-proof records of what the agent knew and when.

The PromptOwl framework explicitly recommends deploying all three layers together. In this architecture, Zep manages session logs, Mem0 handles personalization, and ContextNest provides governance. Each layer handles the type of memory it is best suited for, and together they form a complete memory stack.

## The Local-First Movement in Agent Memory

A significant trend in 2026 is the shift toward local-first agent memory, driven by three factors: privacy concerns, cost optimization, and latency requirements.

Déjà Vu is the purest expression of this movement. By indexing existing session logs with no capture step, it eliminates the need for any cloud service or running daemon. Its privacy-first design — no network path, credential redaction at index time — makes it the go-to choice for developers who cannot or will not send agent conversation data to third parties.

Zep Community Edition supports this trend by offering a self-hosted alternative to cloud-only solutions. Teams can run Zep on their own infrastructure, keeping all data in-house while benefiting from the temporal knowledge graph.

Mem0's cloud-only model is increasingly at odds with this trend. While its semantic graph capabilities are compelling, the requirement to send all conversation data to Mem0's servers is a hard block for many enterprise deployments. The market is voting with its feet: open-source, self-hostable solutions are gaining adoption faster than cloud-only alternatives.

## MCP as the Universal Memory Connector

The Model Context Protocol (MCP) is rapidly becoming the universal connector for agent memory tools. Originally developed by Anthropic, MCP defines a standard interface for agents to interact with external tools and data sources, including memory.

Déjà Vu ships an MCP recall tool that enables agents to query their session history through the MCP protocol. Zep offers MCP integration for its temporal knowledge graph. The protocol enables a plug-and-play ecosystem where any MCP-compatible memory backend can be swapped in without changing agent code.

For teams building multi-agent systems, MCP compatibility is increasingly a non-negotiable requirement. It allows different agents — potentially using different frameworks — to share a common memory interface. An agent built with LangChain and an agent built with Claude Code can both access the same MCP memory server, sharing context and learned preferences.

The MCP ecosystem is also enabling new memory paradigms. Serverless memory solutions like Mnemora, which achieves sub-10ms state reads with four memory types (state, semantic, episodic, procedural) and requires no LLM for CRUD operations, are emerging as MCP-compatible backends. This gives teams the flexibility to start with a simple MCP memory server and upgrade to a more sophisticated backend as their needs grow.

## How to Choose the Right Memory Layer

The right memory layer depends on your specific requirements. Here is a decision framework:

**Choose Déjà Vu if:** You need zero infrastructure overhead, your agents already write session logs to disk, privacy is a hard requirement, and you do not need temporal awareness or real-time memory capture. Déjà Vu is ideal for solo developers, research projects, and teams that want to add memory to existing agent workflows without changing their architecture.

**Choose Mem0 if:** You are building a user-facing application that needs rich personalization, you are already in a cloud ecosystem, and you are willing to pay $40-50+/month for managed memory infrastructure. Mem0's semantic graph excels at extracting and serving user preferences, but the cloud dependency and LLM-in-the-loop cost are significant trade-offs.

**Choose Zep if:** You need temporal awareness — the ability to track when facts were true and when they changed — or you want the flexibility of an open-source Community Edition with an enterprise Cloud upgrade path. Zep is the most balanced option, offering sophisticated memory features with deployment flexibility.

**Choose Agent Memory MCP if:** You are building a multi-agent system, you want to avoid vendor lock-in, or you need the flexibility to swap memory backends without changing agent code. MCP is not a memory solution itself but the protocol that connects agents to memory — pair it with any backend that meets your requirements.

For most production deployments in 2026, the recommended approach is a hybrid: use MCP as the protocol layer, Zep CE or Déjà Vu for local-first memory, and supplement with a cloud service for specific personalization needs. The three-tier architecture — session log, personalization, and governance — provides the most complete memory solution for serious agent deployments.

## Conclusion — The Future of Agent Memory

The agent memory layer market in 2026 is vibrant and fragmented, with no single solution dominating. Déjà Vu's retroactive indexing, Mem0's cloud semantic graph, Zep's temporal knowledge graph, and the MCP protocol each serve different needs in the agent memory stack.

Three trends will shape the future. First, the local-first movement will continue to gain momentum as privacy regulations tighten and teams seek to reduce cloud dependencies. Second, MCP will become the universal memory connector, enabling plug-and-play memory backends. Third, the three-tier architecture — session log, personalization, and governance — will become the standard for production deployments.

The benchmark controversy around LoCoMo versus LongMemEval highlights a deeper issue: the field needs better, more realistic evaluation standards. Until then, practitioners should design their own evaluations based on their specific use cases rather than relying on published benchmark scores.

The bottom line: agent memory is no longer optional for production AI systems. Choose your memory layer carefully, test it against your actual workloads, and design for the flexibility to evolve as the field matures.

## FAQ

**Q1: What is the fastest agent memory layer in 2026?**
Déjà Vu is the fastest by a wide margin, with 7-9ms typical warm search latency and ~40ms worst-case over gigabytes of session logs. This is because it is a pure Go binary with no network calls and no LLM involvement in the search path. Zep and Mem0 are both significantly slower due to their graph database and LLM dependencies.

**Q2: Is Mem0 really state-of-the-art for agent memory?**
The claim is contested. Mem0 published SOTA results on the LoCoMo benchmark, but Zep published a detailed critique showing that Mem0's evaluation of Zep had implementation errors. When Zep ran corrected evaluations, it achieved a 75.14% J score versus Mem0 Graph's ~68%. The LoCoMo benchmark itself has been criticized for insufficient conversation length and lack of temporal reasoning tests.

**Q3: Can I use agent memory without sending data to the cloud?**
Yes. Déjà Vu is fully local with no network path in its indexing or search code. Zep Community Edition is open-source and self-hostable. Agent Memory MCP can be paired with a local MCP memory server. Only Mem0 requires cloud connectivity.

**Q4: What is the three-tier memory architecture for AI agents?**
The three-tier architecture consists of session log memory (raw conversation history with search, typically Zep), personalization memory (semantic graph of user preferences, typically Mem0), and governance memory (deterministic, version-controlled records with audit trails, typically ContextNest). Production agents should deploy all three layers together for complete memory coverage.

**Q5: How does MCP change agent memory?**
MCP (Model Context Protocol) provides a standard interface for agents to read from and write to memory servers. This enables a plug-and-play ecosystem where any MCP-compatible memory backend can be swapped in without changing agent code. It is becoming the universal connector for agent memory, allowing multi-agent systems to share a common memory interface regardless of the framework each agent uses.
