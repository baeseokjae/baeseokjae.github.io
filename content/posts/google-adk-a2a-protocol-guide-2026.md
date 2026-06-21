---
cover:
  alt: Google ADK A2A Protocol Guide for Cross-Framework Agent Interoperability
  image: /images/google-adk-a2a-protocol-guide-2026.png
  relative: false
date: 2026-06-12 07:51:58+00:00
description: A practical Google ADK A2A protocol guide for building interoperable
  agents across frameworks, clouds, and teams.
draft: false
schema: schema-google-adk-a2a-protocol-guide-2026
tags:
- Google ADK
- A2A Protocol
- AI Agents
title: Google ADK A2A Protocol Guide for Cross-Framework Agent Interoperability
---

The google adk a2a protocol pairing gives developers a practical way to build agents in Google ADK while exposing them through the open Agent2Agent protocol. Use ADK for agent logic, workflows, tools, and state; use A2A when those agents need to collaborate across frameworks, clouds, services, or organizational boundaries.

## What Do Google ADK and A2A Solve Together?

Google ADK and A2A solve different parts of the same multi-agent system: ADK builds and runs the agent, while A2A lets that agent communicate with other agents through a shared protocol. Google announced ADK Python v1.0.0 as production-ready at Google I/O 2025, and ADK Python v2.2.0 was the latest release in the research brief dated June 12, 2026. A2A moved from a Google-led protocol into an open standard hosted by the Linux Foundation, with more than 150 supporting organizations announced on April 9, 2026. The practical result is a cleaner boundary: teams can use ADK for prompts, tools, graph workflows, memory, and orchestration, then publish selected capabilities through A2A Agent Cards, tasks, messages, and artifacts. The takeaway is simple: ADK is your implementation framework, and A2A is your interoperability contract.

I use this split when an agent needs to leave the comfort of one codebase. A customer-support triage agent can stay as an internal ADK sub-agent if every collaborator lives in the same application. The moment it needs a contract-analysis agent maintained by legal, a refund agent owned by finance, or a third-party research agent hosted on another cloud, A2A becomes valuable.

The decision is less about vendor preference and more about coupling. ADK gives you a productive local runtime. A2A keeps the network boundary explicit enough that another team can replace its implementation without breaking your caller.

## What Is the 2026 Agent Stack: MCP for Tools, ADK for Agent Logic, and A2A for Interoperability?

The 2026 agent stack is a three-layer architecture where MCP connects agents to tools and context, Google ADK defines agent behavior and workflows, and A2A coordinates communication between autonomous agents. The official A2A documentation frames this stack directly: build agents with ADK or another framework, equip them with MCP or another tool layer, then communicate with A2A across remote agents, local agents, and humans. This distinction matters because teams often confuse tool calling with agent interoperability. MCP answers, "How does this agent call a database, file system, or SaaS API?" ADK answers, "How does this agent reason, route, retry, and maintain state?" A2A answers, "How does this agent discover and collaborate with another agent it does not own?" The takeaway is that MCP, ADK, and A2A are complementary layers, not competing standards.

Here is the mental model I recommend in architecture reviews:

| Layer | Primary job | Typical owner | Example |
|---|---|---|---|
| MCP | Tool and context access | Platform or app team | A code agent reads a repository, calls GitHub, or queries a vector index |
| ADK | Agent logic and workflow | Agent team | A planner routes requests through graph nodes, retries failed steps, and stores state |
| A2A | Agent-to-agent collaboration | Cross-team platform | A finance agent delegates invoice validation to a vendor-risk agent |

This separation also makes failures easier to debug. If the agent cannot read a file, look at MCP or the tool adapter. If the agent chooses the wrong branch, look at ADK workflow logic. If a remote collaborator cannot be discovered, authenticated, or resumed, look at the A2A boundary.

## Which A2A Core Concepts Do Developers Need: Agent Cards, Skills, Tasks, Messages, Artifacts, and Streaming?

A2A core concepts define how agents advertise capabilities, accept work, exchange state, and return results over a protocol that other frameworks can understand. Agent Cards describe an agent's public identity, endpoint, authentication requirements, and skills; the well-known discovery pattern commonly uses metadata such as `/.well-known/agent.json`. Skills describe what the agent can do. Tasks represent units of delegated work with lifecycle state. Messages carry user, agent, or system communication. Artifacts carry durable outputs such as files, reports, JSON payloads, or generated documents. Streaming, often implemented over Server-Sent Events in A2A examples, lets long-running agents report progress without forcing clients to poll blindly. A2A also uses familiar web mechanics such as HTTP/HTTPS and JSON-RPC 2.0 in common implementations. The takeaway is that A2A is not just remote prompt calling; it is a task and capability contract.

The most important design habit is to make the Agent Card boring and precise. Do not advertise "does analytics" when the skill is actually "summarizes daily revenue variance from a warehouse-backed report." Remote orchestrators use this metadata to choose a collaborator, and vague skills create expensive runtime mistakes.

For artifacts, prefer structured outputs over prose when another agent will consume the result. A fraud-screening agent should return a risk score, reasons, evidence references, and confidence, not a paragraph that another model must parse again.

## How Do You Expose a Google ADK Agent as an A2A Server?

Exposing a Google ADK agent as an A2A server means wrapping the ADK runner behind an A2A-compatible application that publishes an Agent Card, accepts A2A tasks, invokes the ADK agent, and returns messages or artifacts through the task lifecycle. Google's own conversion guidance uses an AgentSkill and AgentCard as the public discovery identity, then bridges inbound A2A requests into ADK execution through an AgentTaskManager or AgentExecutor-style adapter. Community examples also call out ADK's `to_a2a()` helper as a fast path for turning an ADK agent into an A2A app. A practical deployment often runs the service on Cloud Run, exposes the metadata endpoint, protects the task endpoint with OAuth or service identity, and tests it with an A2A client. The takeaway is that the wrapper should translate protocols, not bury business logic.

A minimal conversion plan looks like this:

1. Start with a working ADK agent and a narrow responsibility.
2. Define one or more A2A skills that match real capabilities.
3. Publish an Agent Card with endpoint, auth scheme, version, and skill metadata.
4. Implement the A2A task handler as a thin adapter around ADK execution.
5. Return structured artifacts for machine consumers and readable messages for humans.
6. Add contract tests that call the A2A endpoint without importing ADK internals.

The adapter layer should be intentionally small. If it starts containing business rules, routing policy, or custom memory handling, you are building a second framework beside ADK. Keep the A2A server focused on discovery, authentication, task translation, streaming updates, and result packaging.

## How Do You Build a Cross-Framework Orchestrator with ADK and A2A?

A cross-framework orchestrator with ADK and A2A is an ADK agent that discovers remote A2A Agent Cards, evaluates their skills, delegates tasks to selected agents, and combines their artifacts into a final result. This pattern is useful when teams want Google ADK for orchestration but need to collaborate with agents built in Microsoft Agent Framework, LangGraph, BeeAI, custom Python services, or vendor-hosted platforms. A concrete example is an enterprise procurement workflow: an ADK orchestrator receives a supplier onboarding request, calls a risk agent maintained by compliance, calls a contract agent maintained by legal, and calls an ERP agent maintained by finance. Each remote agent keeps its own framework and deployment model, but exposes a shared A2A surface. The takeaway is that the orchestrator should reason over capabilities and results, not remote implementation details.

In practice, I keep an internal registry of trusted Agent Cards rather than letting production orchestrators crawl arbitrary endpoints. Discovery still uses the A2A contract, but platform governance decides which cards are trusted, what scopes they receive, and which versions are allowed.

The orchestrator prompt should not say, "Call the legal agent whenever legal is relevant." Encode that routing as workflow policy where possible. ADK 2.0 graph workflows are useful here because fan-out, fan-in, loops, retries, dynamic nodes, human-in-the-loop steps, and nested workflows can be represented explicitly instead of hidden inside one large prompt.

## What Production Architecture Issues Matter for Authentication, Identity, Observability, Retries, and Deployment?

Production A2A architecture depends on treating remote agents like critical services: authenticate callers, verify agent identity, trace every task, retry safely, and deploy behind controlled endpoints. A2A v0.2 introduced standardized authentication schemes based on an OpenAPI-like authentication schema, which matters because real deployments cannot rely on unsigned Agent Cards or shared demo tokens. In a production design, each agent should have a stable service identity, scoped authorization, versioned Agent Cards, task IDs that flow through logs and traces, and timeout rules that match the business process. Long-running tasks need streaming progress or resumable state, while non-idempotent tasks need idempotency keys before retries are enabled. Cloud Run, Kubernetes, or managed agent platforms can all work if the protocol boundary stays stable. The takeaway is that interoperability is only useful when the operating model is as explicit as the API.

The failure mode I see most often is optimistic delegation. A caller sends a task to a remote agent and assumes the result will arrive quickly, in the expected shape, with no partial failures. That assumption fails the first time a human approval is needed, a model provider throttles, or a downstream SaaS API times out.

Build the control plane before broad rollout. You need dashboards for task volume, latency, failure reason, artifact size, auth denials, protocol versions, and remote-agent health. If you cannot answer "Which remote agent produced this artifact and under which policy?" you are not ready for regulated workflows.

## How Do ADK, A2A, and MCP Compare, and When Should You Use Each Layer?

ADK, A2A, and MCP compare best by boundary: ADK is for building and orchestrating agent behavior, MCP is for connecting an agent to tools and context, and A2A is for connecting agents to other agents. Google ADK Python 2.0 adds graph-based workflows for routing, fan-out/fan-in, loops, retry, state management, dynamic nodes, human-in-the-loop, and nested workflows, which makes it a strong fit for internal agent execution. MCP is a better fit when the same agent needs controlled access to GitHub, a database, a browser, or an enterprise API. A2A is the right layer when the collaborator is itself an autonomous agent with its own skills, identity, lifecycle, and artifacts. The takeaway is to choose the layer based on the boundary you are crossing.

| Question | Use ADK | Use MCP | Use A2A |
|---|---:|---:|---:|
| Are you defining agent reasoning, state, and workflow? | Yes | No | No |
| Are you connecting one agent to tools or data sources? | Sometimes | Yes | No |
| Are you delegating work to another autonomous agent? | Sometimes | No | Yes |
| Do you need cross-framework collaboration? | No by itself | No | Yes |
| Do you need task lifecycle and artifacts from a remote agent? | No by itself | No | Yes |

Do not expose every ADK sub-agent as an A2A service. Internal delegation inside one ADK application is cheaper, faster, and easier to refactor. Use A2A when the collaboration boundary is real: another team owns the agent, another framework runs it, another cloud hosts it, or another organization governs it.

## What Is the Current Ecosystem Status for Linux Foundation Governance, Cloud Support, and SDK Maturity?

The A2A ecosystem in 2026 has moved beyond a Google-only proposal into a Linux Foundation-hosted open standard with broad vendor participation, but teams should still validate maturity through proof-of-concept work. A2A launched in April 2025 with support from more than 50 technology partners and service providers, including Atlassian, Box, Cohere, Intuit, LangChain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, Workday, Accenture, Deloitte, McKinsey, PwC, TCS, and Wipro. On April 9, 2026, the Linux Foundation announced A2A had surpassed 150 supporting organizations, with integrations across Google, Microsoft, and AWS platforms and production deployments across multiple industries. The research brief also recorded A2A v1.0.1 as the latest GitHub release on May 28, 2026. The takeaway is that A2A has real momentum, but production confidence still comes from testing your own workflow.

ADK is also moving quickly. The brief recorded Google ADK Python v2.2.0 as the latest release on June 4, 2026, and noted that ADK documentation shows language tabs for Python, JavaScript, Go, Java, and Kotlin. That breadth helps teams standardize patterns without forcing every service into one runtime.

My read is pragmatic: the governance story is strong enough to justify architecture experiments, and the SDK story is strong enough to build pilots. For critical workflows, I would still pin protocol and SDK versions, keep compatibility tests in CI, and avoid relying on undocumented behavior from any one implementation.

## What Implementation Pitfalls Should Teams Avoid?

Common A2A and ADK implementation pitfalls come from exposing too much too early, trusting metadata too blindly, and treating remote agents like local function calls. The A2A GitHub repository had 24,247 stars and 2,459 forks when checked on June 12, 2026, which signals developer interest, but popularity does not remove distributed-systems risk. The first pitfall is a vague Agent Card that makes orchestration decisions unreliable. The second is missing authentication or unsigned metadata that lets callers confuse identity with availability. The third is returning prose where downstream agents need structured artifacts. The fourth is skipping task lifecycle observability, which makes long-running workflows impossible to debug. The fifth is wrapping tiny internal ADK sub-agents as network services before there is a real ownership boundary. The takeaway is that A2A should make agent collaboration explicit, not turn every helper into infrastructure.

I also avoid building a universal "agent broker" too early. It sounds attractive, but most teams learn more from two or three well-instrumented agent-to-agent integrations than from a generic router with weak policy. Start with known collaborators, explicit contracts, and boring operational metrics.

Versioning deserves special care. Agent Cards should expose enough version information for clients to make safe choices, and clients should tolerate additive changes. If a remote agent changes artifact structure without a compatibility window, your orchestrator will fail in a place that looks like a reasoning problem but is really a contract problem.

## What Starter Blueprint Should You Use for a 2026 Interoperable Agent System?

A good 2026 starter blueprint is a small ADK-orchestrated system with two or three well-scoped remote A2A agents, one shared identity model, contract tests, and structured artifacts from day one. For example, a developer-platform team could build an ADK orchestrator that receives a release-readiness request, delegates dependency scanning to a security agent, changelog drafting to a documentation agent, and deployment-risk analysis to an operations agent. Each agent exposes an Agent Card and one or two skills, runs behind authenticated HTTPS, and returns JSON artifacts plus human-readable summaries. ADK graph workflows handle routing, fan-out/fan-in, retries, and human approval. MCP can still connect individual agents to GitHub, ticketing systems, or internal databases. The takeaway is to begin with a narrow production-shaped slice rather than a broad demo mesh.

My default checklist for the first pilot is short:

| Area | Starter decision |
|---|---|
| Agent scope | One business capability per remote agent |
| Discovery | Trusted registry of Agent Cards |
| Authentication | Service identity plus scoped authorization |
| Results | JSON artifacts with schema tests |
| Workflow | ADK graph with explicit retry and approval nodes |
| Operations | Trace IDs across every task, message, and artifact |

Once that works, expand horizontally. Add another remote agent, another artifact type, or another framework. Do not expand by making the orchestrator smarter in vague ways. The value of the google adk a2a protocol approach is that each boundary stays visible enough to test, secure, and replace.

## What Questions Do Developers Ask About Google ADK and A2A?

Google ADK and A2A questions usually center on whether the technologies overlap, how they relate to MCP, and when a team should introduce a network protocol between agents. The most practical answer is that ADK is a framework for building agents, A2A is a protocol for agent interoperability, and MCP is a tool/context access layer. As of the June 12, 2026 research brief, ADK Python was at v2.2.0, A2A's latest GitHub release was v1.0.1, and A2A was hosted by the Linux Foundation. Those facts make the stack credible enough for pilots and carefully scoped production work, but not a reason to skip design discipline. The right adoption path is a narrow workflow with clear ownership boundaries, authenticated endpoints, structured artifacts, and contract tests. The takeaway is that ADK plus A2A is powerful when the collaboration boundary is real.

### Is Google ADK the same thing as the A2A protocol?

Google ADK is not the same thing as the A2A protocol; ADK is an agent development framework, while A2A is an interoperability protocol. Use ADK to define agent behavior, tools, state, workflows, and orchestration. Use A2A when that agent needs to advertise skills, accept remote tasks, stream progress, or return artifacts to another agent or orchestrator.

### Do I need MCP if I already use A2A?

MCP is still useful with A2A because the two layers solve different problems. MCP connects an agent to tools, services, files, APIs, and context sources. A2A connects one autonomous agent to another autonomous agent. A common pattern is an ADK agent that uses MCP to read GitHub and uses A2A to delegate security review to a remote agent.

### When should I not expose an ADK sub-agent through A2A?

You should not expose an ADK sub-agent through A2A when it is only an internal helper inside one application and has no independent ownership, deployment, or framework boundary. Local ADK composition is simpler and faster. Add A2A when another team, service, cloud, framework, or organization needs to call that capability through a stable contract.

### What should an Agent Card include in a production system?

An Agent Card should include the agent's identity, endpoint, supported protocol version, authentication requirements, skill descriptions, input expectations, output or artifact formats, and operational ownership. In production, treat the card like an API contract. Keep skills narrow, version changes clearly, and store trusted cards in a governed registry instead of accepting arbitrary metadata.

### Can A2A work across non-Google frameworks?

A2A can work across non-Google frameworks because its purpose is cross-framework agent interoperability. An ADK orchestrator can call agents implemented in Microsoft Agent Framework, LangGraph, BeeAI, custom services, or vendor platforms if those agents expose compatible A2A endpoints and trusted Agent Cards. The hard parts are authentication, versioning, observability, and artifact contracts, not the framework names.