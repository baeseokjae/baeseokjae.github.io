---
title: "Linux Foundation Agentic AI Foundation (AAIF): MCP + A2A Governance Explained"
date: 2026-05-22T13:03:54+00:00
tags: ["agentic-ai", "mcp", "linux-foundation", "a2a", "enterprise-ai", "open-source"]
description: "The Linux Foundation's Agentic AI Foundation (AAIF) brings MCP, goose, and AGENTS.md under neutral governance. Here's what it means for developers."
draft: false
cover:
  image: "/images/linux-foundation-agentic-ai-foundation-2026.png"
  alt: "Linux Foundation Agentic AI Foundation (AAIF): MCP + A2A Governance Explained"
  relative: false
schema: "schema-linux-foundation-agentic-ai-foundation-2026"
---

The Linux Foundation launched the Agentic AI Foundation (AAIF) in December 2025 to provide neutral governance for the infrastructure powering AI agents in production. It now governs MCP, goose, and AGENTS.md — protocols and tools used across OpenAI, Anthropic, Google, and Block's agent stacks.

## What Is the Agentic AI Foundation (AAIF)?

The Agentic AI Foundation (AAIF) is an independent, vendor-neutral foundation under the Linux Foundation umbrella, established in December 2025 to govern open infrastructure for AI agent systems. AAIF launched with 150+ member organizations — making it the fastest-growing foundation in Linux Foundation history — and three anchor projects: the Model Context Protocol (MCP), goose (an open-source AI agent framework by Block), and AGENTS.md, a standardization spec for defining agent behavior. Co-founded by Anthropic, OpenAI, and Block, with backing from Google, Microsoft, AWS, Bloomberg, and Cloudflare, AAIF occupies the same structural role in the AI agent ecosystem that the Linux Foundation occupies for open-source operating systems: it removes any single company's control over infrastructure that the entire industry depends on. The agentic AI market is projected to reach $42 billion by 2027 at a 47% CAGR, and AAIF's founding reflects the industry's recognition that production-grade AI agents need shared governance, not competing proprietary protocols.

### Why does neutral governance matter for AI agents?

AI agents connect to external tools, APIs, and data stores. When the protocols that enable those connections are owned by a single vendor, every downstream developer is exposed to unilateral changes in pricing, compatibility, and deprecation. AAIF applies the Linux Foundation model — neutral stewardship, open governance documents, Technical Steering Committee (TSC) oversight — to ensure that MCP, goose, and AGENTS.md evolve based on community consensus rather than any one company's roadmap.

## Why Did Anthropic Donate MCP to the Linux Foundation?

Anthropic donated the Model Context Protocol to the Linux Foundation and co-founded AAIF because MCP had outgrown single-vendor governance. By early 2026, MCP had 10,000+ servers and 97 million downloads — an adoption curve Anthropic neither anticipated nor could manage alone at neutral scale. Donating MCP to AAIF signals to enterprise buyers that the protocol is infrastructure, not product: governed by a TSC with multi-company representation, subject to RFC-style change processes, and immune to the kind of sudden pivots that have burned enterprise adopters of proprietary protocols before. The move closely mirrors Kubernetes' 2016 donation to the CNCF, which accelerated enterprise container adoption by eliminating Google's perceived lock-in. Anthropic retains a founding seat on the TSC but no veto power — the same arrangement that let Linux become the default server OS while no single vendor controls it. For developers already running MCP-connected agents, this donation means protocol stability and a clear governance process for submitting RFCs.

### What changes for developers using MCP after the AAIF donation?

The MCP specification itself does not change at the donation boundary. What changes is the process for changing it. Before, a breaking API change could ship with Anthropic's Claude update cycle. After, any change to the MCP specification requires an RFC, TSC review, and comment period — the same process governing OpenAPI, GraphQL, and other Linux Foundation specs. Existing 10,000+ MCP servers remain compatible. The practical benefit: enterprise IT teams can now include MCP in their long-term architectural plans without worrying that the protocol disappears when Anthropic's strategy shifts.

## What Are the Three Core AAIF Projects?

AAIF's three founding projects — MCP, goose, and AGENTS.md — cover the full stack required to build, run, and govern AI agents in production environments. MCP is the tool-connectivity layer (how an agent calls external APIs and reads data sources). Goose, contributed by Block, is the agent execution runtime (how you run, compose, and extend agents). AGENTS.md is the behavioral specification layer (how you document what an agent is allowed to do and how it should behave). Together they form a reference architecture for production agents: connect with MCP, execute with goose, govern behavior with AGENTS.md. Before AAIF, developers had to assemble these layers from vendor-specific SDKs (Claude's tool-use format, OpenAI's function calling, LangChain's agent executor). Under AAIF, all three layers have vendor-neutral specs that any model provider can implement.

### MCP: The Tool-Connectivity Protocol

MCP (Model Context Protocol) is a JSON-RPC-based protocol that defines how AI agents discover and call external tools, read resources (files, databases, APIs), and receive structured results. An MCP server exposes capabilities — a filesystem MCP server exposes read/write tool calls; a Postgres MCP server exposes SQL query tools. MCP clients (Claude, Cursor, Windsurf, any LLM runtime) connect to these servers using a standard handshake. With 10,000+ servers in the public registry as of 2026, MCP has become the de facto standard for agent tool integration in the same way REST became the standard for web APIs. Under AAIF, the protocol evolves through an RFC process with a TSC that includes seats from Anthropic, OpenAI, Google, and community representatives.

### goose: The Open-Source Agent Runtime

Goose is Block's open-source AI agent framework, donated to AAIF as part of the foundation launch. It provides a local agent execution environment — you give goose a task, it plans steps, selects MCP-connected tools, calls them, and iterates until the task completes. Goose is model-agnostic: it runs on Claude, GPT-4o, Gemini, or any LLM that supports tool-use. Under AAIF, goose becomes the reference implementation for the AGENTS.md behavioral spec, meaning any agent platform claiming AGENTS.md compliance can validate against goose's test suite.

### AGENTS.md: The Behavioral Specification Standard

AGENTS.md is a standardization format for defining agent behavior in a human-readable, version-controlled document. Analogous to how OpenAPI documents REST endpoints, an AGENTS.md file specifies what tools an agent can access, under what conditions, with what constraints. Enterprise IT teams can use AGENTS.md to enforce agent governance policies without modifying agent code: an agent that violates its AGENTS.md spec can be blocked at the runtime layer. As of 2026, AAIF's TSC is developing validation tooling that checks deployed agent behavior against their AGENTS.md declarations.

## How Does A2A (Agent-to-Agent) Governance Work?

A2A (Agent-to-Agent) governance refers to the set of standards and oversight mechanisms that control how AI agents interact with each other in multi-agent systems — not just with tools (MCP) but with other autonomous agents. Under AAIF, A2A governance is emerging as a distinct workstream from MCP: while MCP governs the tool layer, A2A governance addresses the trust, authorization, and audit requirements when one agent delegates a subtask to another. In a practical enterprise scenario: an orchestrator agent calls a data analyst agent to query a warehouse, which calls a reporting agent to format results. Each hop needs authorization scope, identity attestation, and audit logging that MCP alone doesn't provide. AAIF's A2A working group is developing specifications for inter-agent trust chains, capability declarations, and rate limiting — the same governance primitives that OAuth solved for user-to-service authentication, now applied to agent-to-agent delegation.

### TSC and Membership Council Structure

AAIF governance operates through two bodies: the Technical Steering Committee (TSC) and the Governing Board. The TSC has technical seats held by engineers from founding member companies (Anthropic, OpenAI, Block) plus community-elected seats — a model borrowed directly from Kubernetes' governance structure. The Governing Board handles foundation budget, membership tiers, and strategic direction. Founding member companies (Anthropic, OpenAI, Block) have permanent TSC seats for the first two years; after that, all seats are elected. Premier members (Google, Microsoft, AWS, Cloudflare, Bloomberg) have Governing Board representation proportional to their membership tier. General members can participate in working groups and RFC processes. This structure ensures that no single company can block a protocol change or force an incompatible fork.

## What Does AAIF Mean for Enterprise AI Deployment?

For enterprise IT and engineering teams, AAIF's formation is the signal that was missing before: agentic AI infrastructure is now governed by the same institutional model as Linux, Kubernetes, and Node.js — stable enough to build on, with a documented change process and multi-vendor support. Before AAIF, the risk of building production agents on MCP was that Anthropic could deprecate or incompatibly change it with a Claude API update. That risk is now bounded by TSC process. The immediate practical effect is that enterprise procurement and security review teams have a governance entity to audit — they can review AAIF's RFC history, TSC meeting notes, and security policy the same way they review Linux Foundation project governance before deploying Kubernetes. Solo.io's contribution of agentgateway — a secure MCP proxy for enterprise environments — illustrates the direction: the foundation is building security primitives (TLS, auth, audit logging) directly into the reference architecture, addressing the compliance requirements that blocked enterprise adoption in 2025.

### Security Implications of AAIF for Production Agents

AAIF's security working group is developing three categories of tooling: (1) agentgateway — a network proxy that enforces TLS, auth, and rate limits for MCP connections; (2) AGENTS.md validation tooling — static analysis for agent behavioral compliance; and (3) A2A trust chain specifications — audit log standards for multi-agent delegation. For teams running agents in regulated industries (finance, healthcare, legal), these primitives are prerequisite: an agent that calls a payment API without audited authorization scope is a compliance violation. AAIF's governance framework makes it possible to deploy agents with the same audit trail documentation that internal risk teams require for any production system touching sensitive data.

## Who Are the AAIF Founding Members and Why Do They Matter?

| Member | Tier | Contribution |
|--------|------|-------------|
| Anthropic | Founding/Co-founder | MCP protocol, TSC seat |
| OpenAI | Founding/Co-founder | A2A workstream leadership, TSC seat |
| Block | Founding/Co-founder | goose runtime, TSC seat |
| Google | Premier | Gemini MCP integration, Governing Board |
| Microsoft | Premier | Azure AI Foundry MCP support, Governing Board |
| AWS | Premier | Bedrock agent MCP compatibility, Governing Board |
| Cloudflare | Premier | Edge MCP gateway, Governing Board |
| Bloomberg | Premier | Financial sector governance input, Governing Board |
| Solo.io | Member | agentgateway security contribution |

The founding member list matters because it represents the full competitive landscape of AI infrastructure choosing to cooperate on shared standards. OpenAI and Anthropic are direct LLM competitors, yet both co-founded AAIF — the same pattern as Google and IBM co-founding the Linux Foundation while competing in servers. This convergence on shared infrastructure standards typically accelerates the market: once the protocol layer is neutral, competition moves up the stack to model quality, developer experience, and pricing.

## What Is the AAIF Roadmap for 2026–2027?

AAIF's public roadmap through 2027 focuses on four workstreams: (1) MCP v2 specification — adding streaming support, improved auth flows, and resource pagination to handle large data sources; (2) A2A governance spec — RFC-complete inter-agent trust chain standard targeting Q3 2026; (3) AGENTS.md v1.0 — first stable behavioral specification release with goose-based validation tooling; and (4) Security certifications — an AAIF security conformance program that allows agent platforms to certify compliance with agentgateway standards. For developers, the most impactful near-term deliverable is MCP v2: the current protocol has known limitations with streaming responses and large file operations that make it awkward for data-heavy agent use cases. MCP v2's RFC is open for public comment through the AAIF GitHub organization, and the TSC has committed to backward compatibility with all existing MCP v1 servers.

## FAQ

**What is the Agentic AI Foundation (AAIF)?**
AAIF is a vendor-neutral foundation under the Linux Foundation that governs open infrastructure for AI agent systems, including the Model Context Protocol (MCP), the goose agent runtime, and the AGENTS.md behavioral specification. It launched in December 2025 with 150+ member organizations co-founded by Anthropic, OpenAI, and Block.

**Why did Anthropic donate MCP to the Linux Foundation?**
MCP grew to 10,000+ servers and 97M+ downloads faster than Anthropic could govern it as a single vendor. Donating MCP to AAIF transfers governance to a neutral TSC, giving enterprise buyers protocol stability and removing vendor lock-in risk — the same reason Google donated Kubernetes to the CNCF in 2016.

**What is A2A governance and how does it differ from MCP?**
MCP governs how agents connect to tools and data sources. A2A (Agent-to-Agent) governance addresses how agents interact with other agents — authorization scope, trust chain attestation, and audit logging for multi-agent delegation. AAIF's A2A working group is developing these specifications as a separate standard from MCP.

**What is AGENTS.md and how does it work?**
AGENTS.md is a behavioral specification format — similar to OpenAPI but for agent behavior rather than REST endpoints. It documents what tools an agent can access, under what conditions, and with what constraints. AAIF's TSC is developing validation tooling that checks deployed agent behavior against AGENTS.md declarations, enabling compliance teams to enforce agent governance without modifying agent code.

**How does AAIF affect my existing MCP server or agent implementation?**
Your existing MCP v1 servers remain compatible — AAIF's governance transition does not change the current protocol. What changes is the process for future protocol changes: any breaking change now requires a public RFC and TSC review. This makes MCP more stable for long-term production use, and gives you a channel to influence protocol evolution through the AAIF working groups.
