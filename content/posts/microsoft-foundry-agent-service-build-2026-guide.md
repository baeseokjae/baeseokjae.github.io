---
title: "Microsoft Foundry Agent Service Build 2026 Guide: Hosted Agents, Memory, Toolboxes, Evaluations, and Governance"
date: 2026-06-13T07:04:28+00:00
tags: ["Microsoft Foundry", "AI agents", "Azure"]
description: "A developer guide to Microsoft Foundry Agent Service Build 2026 hosted agents, memory, tools, evaluation, and governance."
draft: false
cover:
  image: "/images/microsoft-foundry-agent-service-build-2026-guide.png"
  alt: "Microsoft Foundry Agent Service Build 2026 Guide"
  relative: false
schema: "schema-microsoft-foundry-agent-service-build-2026-guide"
---

Microsoft Foundry Agent Service Build 2026 is Microsoft's production platform for running AI agents with managed hosting, memory, tool access, evaluations, and governance. The practical shift is that teams can keep their preferred agent framework while moving runtime, identity, observability, and policy controls into a managed Azure control plane.

## What Did Microsoft Announce for Foundry Agent Service at Build 2026?

Microsoft Foundry Agent Service Build 2026 is a set of production agent capabilities around hosted runtimes, Toolboxes, managed Memory, Foundry IQ, evaluations, and governance controls. Microsoft positioned the service as the operating layer for enterprise agents, while Gartner predicts 40% of enterprise applications will include task-specific AI agents by the end of 2026, up from less than 5% in 2025. The important developer news is not a single model endpoint. It is the packaging of agent execution, identity, lifecycle management, tool calling, long-term context, tracing, evaluation, and compliance into one managed service. Hosted agents let teams bring code from Microsoft Agent Framework, LangGraph, OpenAI Agents SDK, Anthropic Agent SDK, GitHub Copilot SDK, or custom runtimes. Toolboxes and Memory move common platform concerns out of each application. The takeaway: Build 2026 made Foundry Agent Service look less like a demo builder and more like infrastructure for operating agents repeatedly.

Microsoft also put clear preview boundaries around the stack. Foundry IQ knowledge bases are positioned as generally available in the research brief, while hosted agents, Memory, Routines, Toolboxes, ASSERT, and Agent Control Specification are preview or emerging capabilities. That matters because architecture decisions should separate what can anchor a production system today from what needs feature flags, fallback paths, or limited rollout.

## Why Is Foundry Becoming an Agent Control Plane?

Foundry Agent Service is becoming an agent control plane because it manages the shared operational layers around agents rather than forcing developers into one framework. Microsoft says hosted agents can use Microsoft Agent Framework, LangGraph, OpenAI Agents SDK, Anthropic Agent SDK, GitHub Copilot SDK, or custom code, which is a strong signal that the runtime boundary is more important than the authoring library. In practice, an agent control plane owns endpoint exposure, Microsoft Entra identity, scaling, session persistence, observability, lifecycle operations, tool access, memory, and evaluation workflows. That is where enterprise agent projects usually fail after the first impressive prototype: duplicated authentication code, inconsistent audit logs, untracked prompts, and tool calls that nobody can explain during an incident. Foundry's bet is that developers will keep experimenting in code, but platform teams will centralize the surrounding runtime and governance. The takeaway: treat Foundry as the operational shell around agent systems, not merely as another SDK.

This framing also helps with internal platform conversations. If every team deploys a separate agent stack on its own Kubernetes namespace, you get freedom but also fragmented secrets, telemetry, and policy enforcement. Foundry tries to make the agent runtime a repeatable platform concern, similar to how API gateways standardized service exposure.

## Should You Use Prompt Agents or Hosted Agents?

Prompt agents are Foundry-managed agents where configuration, instructions, tools, and model settings live inside the service, while hosted agents are containerized applications that bring custom code and run behind a managed Foundry endpoint. Microsoft documents both operating models, and hosted agents are the Build 2026 feature most relevant to engineering teams with existing LangGraph, OpenAI Agents SDK, Anthropic Agent SDK, GitHub Copilot SDK, or custom orchestration code. Choose prompt agents when the workflow is mostly instruction-driven, the tool surface is narrow, and you want the fastest path to a managed agent. Choose hosted agents when you need custom routing, state machines, framework-specific behavior, proprietary middleware, or deeper integration with your existing platform code. The decision is less about sophistication and more about ownership boundaries: prompt agents optimize for managed simplicity, while hosted agents preserve application control. The takeaway: use prompt agents for straightforward managed workflows and hosted agents when code ownership is part of the product.

| Runtime choice | Best fit | Main tradeoff |
|---|---|---|
| Prompt agent | Simple internal assistants, retrieval workflows, constrained tool use | Less control over custom orchestration code |
| Hosted agent | Framework-based agents, multi-step business workflows, custom middleware | More packaging, testing, and container cost responsibility |
| Custom Kubernetes | Teams needing full infrastructure control or unsupported runtime patterns | You own identity, scaling, logs, governance, and lifecycle glue |

### When Are Prompt Agents Enough?

Prompt agents are enough when the agent's behavior can be expressed through instructions, model configuration, built-in tools, and well-scoped enterprise grounding. A support triage assistant that searches a knowledge base, summarizes a case, and drafts a response is a good fit. You still need evaluations and access controls, but you probably do not need a custom container.

### When Do Hosted Agents Become Necessary?

Hosted agents become necessary when the agent is real application code. If your workflow has custom retries, graph transitions, approval gates, domain libraries, or framework-specific callbacks, keep that code and package it. The cost is operational discipline: versioned images, dependency scanning, rollback strategy, and trace review.

## How Do Hosted Agents Work in Foundry Agent Service?

Hosted agents work by running your agent as a containerized application that Foundry exposes and manages as an agent endpoint. Microsoft documentation describes the flow: teams push an image to Azure Container Registry, then Foundry provisions compute, assigns a dedicated Microsoft Entra ID, exposes an endpoint, and handles scaling, session persistence, observability, and lifecycle management. That model is familiar to developers who already ship services, but the managed endpoint is agent-aware rather than just a generic container deployment. The container keeps your orchestration code, dependencies, and framework runtime. Foundry supplies the surrounding platform concerns: identity, hosted execution, observability hooks, session continuity, and lifecycle operations. This is useful when a prototype already works locally or in a bespoke service, but production requires central governance and repeatable deployment. The takeaway: hosted agents let you bring code while moving operational control into Foundry.

The clean implementation pattern is to treat the hosted agent image like any other production service artifact. Pin dependencies, keep environment configuration outside the image, scan the container, and test the endpoint contract separately from the internal agent graph. Foundry reduces the hosting burden, but it does not remove basic release engineering.

## What Are Toolboxes in Microsoft Foundry?

Toolboxes in Microsoft Foundry are reusable collections of tools that agents can call through centrally managed definitions, authentication, and policy controls. At Build 2026, Toolboxes matter because most useful enterprise agents need actions: reading tickets, creating pull requests, querying databases, sending messages, or calling Model Context Protocol endpoints. Without a shared tool layer, every agent team ends up rebuilding connector code, secret handling, retries, and audit behavior. A Toolbox gives the platform team a place to expose approved capabilities once and let multiple agents consume them consistently. For example, a service-management Toolbox might include Jira search, incident creation, PagerDuty escalation, and a read-only CMDB lookup, each with its own permission boundary. The design goal is not just developer convenience; it is reducing hidden tool access and making action surfaces reviewable. The takeaway: Toolboxes turn agent actions into managed platform assets.

For developers, the main discipline is designing tools with narrow contracts. Do not expose a broad "run SQL" function when the agent only needs "find open invoices for account ID." Smaller tools are easier to authorize, evaluate, log, and revoke. Tool design becomes API design with a probabilistic caller in the loop.

## How Does Memory Work in Agent Service?

Memory in Foundry Agent Service is a managed long-term memory layer that extracts, stores, consolidates, retrieves, edits, and deletes useful user or task context across agent interactions. Microsoft describes Memory as supporting extraction, consolidation, retrieval, item-level CRUD, store-level retention defaults, and direct remember or forget commands. That is different from simply passing the last chat messages into a model. Long-term memory can preserve preferences, project facts, constraints, and previous decisions so an agent does not repeatedly ask the same questions. It also introduces a serious data-governance surface. A bad memory item can steer future work incorrectly, and sensitive information can persist longer than intended if retention and deletion rules are weak. The engineering work is to define what should be remembered, who can inspect it, when it expires, and how users can correct it. The takeaway: Memory improves continuity, but only if retention, review, and deletion are designed from day one.

I would start with explicit memory categories rather than letting everything become persistent context. For example, allow project preferences, approved terminology, and stable account metadata; reject temporary secrets, raw documents, and speculative conclusions. Add tests that confirm the agent forgets what policy says it must forget.

## How Are Foundry IQ, Work IQ, and Memory Different?

Foundry IQ, Work IQ, and Memory refer to different context systems: Foundry IQ grounds agents in curated enterprise knowledge, Work IQ connects Microsoft 365 work context, and Memory stores durable agent-specific or user-specific context. The Build 2026 confusion is understandable because all three make agents "know more," but they solve separate problems. Foundry IQ knowledge bases are useful when the agent needs authoritative documents, policies, product information, or domain content. Work IQ is useful when the relevant context lives in Microsoft 365 signals such as meetings, files, messages, or organizational work patterns. Memory is useful when the agent must preserve preferences or facts learned through prior interactions. Mixing them carelessly creates stale answers and compliance risk. A policy document belongs in grounded knowledge, not personal memory. A user's preferred report format may belong in memory. The takeaway: use grounding for authoritative knowledge and memory for durable interaction context.

| Context layer | Stores | Typical question |
|---|---|---|
| Foundry IQ | Curated enterprise knowledge bases | "What does the current support policy say?" |
| Work IQ | Microsoft 365 work context | "What did this team decide in recent project meetings?" |
| Memory | Durable user or agent context | "What format does this user prefer for weekly summaries?" |

The separation also improves evaluation. Retrieval failures, memory corruption, and work-context permission mistakes have different causes and fixes. If the context source is clear in traces, the platform team can debug the system instead of arguing about whether "the model made it up."

## When Should Agents Use Routines and Scheduled Execution?

Routines and scheduled execution are Foundry capabilities for running agent workflows without waiting for a user to start a chat session. They matter because many useful agents are operational: checking aging support tickets every morning, reviewing new pull requests hourly, summarizing overnight incidents, or escalating compliance exceptions before a deadline. A chat prompt is a poor trigger for these workflows because the business value depends on time, events, or recurring checks. With scheduled execution, an agent can run against approved tools, produce an auditable result, and route output to the right destination. The risk is that unattended agents can create noise or take repeated actions if guardrails are loose. A scheduled agent needs stricter limits than an interactive assistant: idempotency, rate limits, dry-run modes, human approval for destructive actions, and clear ownership. The takeaway: use Routines for recurring operational work, but design them like production jobs with agent behavior inside.

A good first Routine is read-only. Let the agent collect facts, identify exceptions, and draft recommendations. After traces and evaluations prove the workflow is stable, add controlled write actions such as creating tickets or sending notifications. This staged rollout catches prompt drift before it becomes operational damage.

## How Do Evaluations and Tracing Catch Agent Regressions?

Evaluations and tracing catch agent regressions by recording how an agent reasoned through a task, which tools it called, what context it retrieved, and whether the final output met quality and safety expectations. Microsoft says the agent development lifecycle includes tracing, repeatable quality and safety evaluations, hosted-agent optimization, publishing, monitoring, and iteration. That lifecycle is the difference between a demo and a service you can change safely. Agent behavior can regress when a model changes, a prompt is edited, a tool schema evolves, a knowledge base is refreshed, or a memory item is added. Without traces, developers only see the final wrong answer. With traces, they can inspect retrieval, tool inputs, latency, errors, and policy decisions. With evaluations, they can run repeatable scenarios before release. The takeaway: evaluations are the CI suite for agent behavior, and tracing is the debugger you need when the suite fails.

For a production Foundry agent, keep evaluation sets small but representative at first. Include happy-path tasks, permission-denied cases, stale data cases, prompt-injection attempts, and tool-failure scenarios. The goal is not academic scoring. The goal is knowing whether the next deployment made the agent worse.

## What Governance Did Microsoft Highlight at Build 2026?

Microsoft highlighted governance through ASSERT, Agent Control Specification, RBAC, identity boundaries, observability, and policy-driven evaluation for agents. The Build 2026 research brief notes that ASSERT is an open-source policy-driven evaluation framework and Agent Control Specification is a portable runtime control standard. This focus is timely: IBM's 2026 survey of 2,000 CIOs and CTOs found that 77% say current governance frameworks are inadequate and only 11% feel fully prepared for large-scale AI deployment. Agent governance is harder than chatbot governance because agents can call tools, remember context, act on schedules, and interact with other systems. The minimum governance baseline is least-privilege identity, explicit tool permissions, trace retention, memory deletion, evaluation gates, human approval for risky actions, and clear compliance boundaries for third-party models or services. The takeaway: agent governance must control actions and state, not just model prompts.

Microsoft documentation also warns that when hosted agents interact with third-party models, servers, or agents, customers remain responsible for understanding data retention, location, and compliance boundary implications. That warning should appear in your architecture review. A managed runtime does not automatically make every downstream processor compliant.

## How Should You Think About Pricing and Hosted Agent Cost?

Hosted agent cost in Foundry Agent Service includes more than model tokens because hosted agents also consume container compute, grounding resources, tool execution, evaluation runs, observability storage, and operational support. Microsoft pricing details say hosted agents are billed based on underlying container compute consumed per hour. That means an inefficient hosted agent can cost money while idle or waiting, even before counting token usage. Add Code Interpreter sessions, data retrieval, vector storage, logs, traces, evaluation workloads, and network calls, and the bill starts looking like a service bill rather than a chatbot bill. This matters during architecture review because teams often estimate only prompt and completion tokens. For agents, latency, retry behavior, long-running workflows, scheduled jobs, and tool fan-out can dominate cost. The takeaway: model spend is one line item; production agent cost is a runtime, data, evaluation, and operations model.

Build a cost model before rollout. Estimate daily invocations, average runtime duration, tool calls per task, grounding queries, trace volume, evaluation frequency, and expected retries. Then add a failure budget: agents that hit tool errors repeatedly can burn compute and tokens while producing no user value.

## What Reference Architecture Works for a Production Foundry Agent?

A production Foundry agent architecture is a containerized hosted agent behind Foundry Agent Service, connected to approved Toolboxes, grounded through Foundry IQ, supported by managed Memory, evaluated through repeatable test suites, and governed with Entra identity plus policy controls. A concrete example is an enterprise support agent that triages cases, reads product policy from Foundry IQ, remembers each customer's support preferences, calls a service-management Toolbox, and creates escalation drafts for human approval. The hosted agent contains the orchestration code, such as a LangGraph workflow or Microsoft Agent Framework implementation. Foundry supplies endpoint management, identity, scaling, session persistence, observability, and lifecycle controls. Evaluations test the agent against known cases before deployment, and traces capture production behavior for review. This architecture keeps business logic in code while standardizing the runtime and control layers. The takeaway: separate orchestration, tools, knowledge, memory, evaluation, and governance into explicit layers.

| Layer | Recommended responsibility |
|---|---|
| Hosted agent container | Orchestration, framework code, domain workflow |
| Toolboxes | Approved actions and reusable connectors |
| Foundry IQ | Authoritative knowledge grounding |
| Memory | Durable user or task context |
| Evaluations | Repeatable behavioral and safety checks |
| Governance | Identity, RBAC, policy, audit, compliance review |

This layered design makes incidents easier to debug. If the agent created the wrong ticket, you can inspect whether the issue came from orchestration, a tool schema, retrieved knowledge, memory, or a policy miss.

## What Migration and Preview Caveats Should Teams Know?

Migration to Foundry Agent Service should start by identifying which parts of an existing agent belong in the hosted container and which parts should move into managed Foundry services such as Toolboxes, Memory, Foundry IQ, evaluations, and governance. The biggest Build 2026 caveat is preview status: hosted agents, Toolboxes, Memory, Routines, ASSERT, and Agent Control Specification should be adopted with rollout controls until their contracts stabilize. Do not migrate by lifting every local helper into the container and calling the job done. That preserves old platform debt inside a new runtime. Instead, move secrets and reusable action logic into Toolboxes, move authoritative documents into Foundry IQ, move durable preferences into Memory, and move regression checks into evaluations. Keep feature flags around preview capabilities and document fallback behavior. The takeaway: migration is a platform cleanup opportunity, not just a hosting change.

For existing hosted-agent experiments, review data boundaries before adding third-party models or external MCP servers. Foundry can manage the agent endpoint, but it cannot make an external service's retention policy disappear. Security review should follow the actual path of data and tool calls, not the marketing diagram.

## How Does Foundry Compare with LangGraph, Copilot Studio, and Custom Kubernetes?

Foundry Agent Service differs from LangGraph, Copilot Studio, and custom Kubernetes because it is primarily a managed agent platform, not only an orchestration library, low-code builder, or generic infrastructure layer. LangGraph is excellent when developers need explicit graph-based control over agent state and transitions. Copilot Studio is strong for business-facing conversational agents and Microsoft ecosystem workflows. Custom Kubernetes gives platform teams maximum control over runtime, networking, and deployment patterns. Foundry Agent Service sits across these choices by allowing hosted agents built with several frameworks while supplying managed identity, endpoint exposure, scaling, sessions, observability, memory, tools, evaluations, and governance. The strategic choice is whether your scarce resource is application flexibility, business-user authoring, or platform operations. The takeaway: Foundry is most compelling when teams want code-level agent development with managed enterprise controls around it.

| Option | Strength | Weakness |
|---|---|---|
| Foundry Agent Service | Managed runtime, identity, tools, memory, evaluations, governance | Preview features require careful rollout |
| LangGraph | Precise developer control over agent workflows | You still need hosting and enterprise controls |
| Copilot Studio | Business-friendly authoring and Microsoft workflow integration | Less ideal for deeply custom code workflows |
| Custom Kubernetes | Full infrastructure control | Highest burden for auth, scale, traces, and governance |

The comparison is not always either-or. A team can write a LangGraph agent and deploy it as a Foundry hosted agent. That combination preserves graph control while centralizing runtime operations.

## What Implementation Checklist Should Developers and Platform Teams Use?

An implementation checklist for Microsoft Foundry Agent Service should cover runtime choice, identity, tool design, knowledge grounding, memory policy, evaluation coverage, observability, cost controls, and preview-risk management. A June 2026 Forrester report covered by ITPro says about 75% of enterprise leaders report adopting agentic AI, yet many initiatives remain stuck in pilot mode because orchestration, governance, and trust costs are hard to operationalize. The checklist is how teams avoid that trap. Start by deciding whether the workflow needs a prompt agent or hosted agent. Assign least-privilege Entra identity. Convert shared actions into Toolboxes. Put authoritative documents in Foundry IQ. Define what Memory may store and when it expires. Build regression evaluations before production. Review traces after launch. Model container compute and token cost. Track preview dependencies explicitly. The takeaway: production agents need a release checklist, not just a clever prompt.

Use this as a starting gate:

| Check | Done when |
|---|---|
| Runtime selected | Prompt agent or hosted agent decision is documented |
| Identity scoped | Entra identity has only required permissions |
| Tools reviewed | Toolboxes expose narrow, auditable actions |
| Knowledge grounded | Authoritative content lives outside prompts |
| Memory governed | Retention, edit, delete, and forbidden data rules exist |
| Evaluations built | Critical tasks and safety cases run before release |
| Traces monitored | Tool calls, retrieval, failures, and latency are visible |
| Costs modeled | Compute, tokens, evaluation, storage, and retries are estimated |

## FAQ: Microsoft Foundry Agent Service Build 2026

Microsoft Foundry Agent Service Build 2026 FAQ answers the practical questions developers ask before choosing the platform: what it is, whether hosted agents are production-ready, how Memory differs from grounding, how Toolboxes fit with MCP, and what governance work remains. The short answer is that Foundry Agent Service is best understood as Microsoft's managed control plane for enterprise agents, especially when teams want to keep code-level flexibility while centralizing runtime and oversight. Hosted agents are the key engineering feature because they let existing framework code run as managed containers, but preview labels still matter. Memory, Toolboxes, Foundry IQ, evaluations, and governance controls solve different operational problems and should not be collapsed into one generic "agent context" bucket. Teams should evaluate Foundry on runtime fit, identity model, data boundaries, trace quality, cost behavior, and migration effort. The takeaway: use Foundry when managed operations are as important as agent behavior.

### What is Microsoft Foundry Agent Service?

Microsoft Foundry Agent Service is a managed Azure platform for building, deploying, scaling, observing, and governing AI agents. It supports prompt agents and hosted agents, so teams can either configure managed agents inside Foundry or package their own code as containers.

### Are hosted agents generally available?

Hosted agents are described in the Build 2026 research brief as preview capability, so teams should verify current availability in their tenant and region before committing production dependencies. Preview does not mean unusable, but it does mean rollout controls, fallbacks, and contract-change awareness are required.

### Is Foundry Agent Service a replacement for LangGraph?

Foundry Agent Service is not a direct replacement for LangGraph. LangGraph is an orchestration framework, while Foundry provides a managed runtime and operational control plane. A practical architecture can use LangGraph inside a Foundry hosted agent.

### What is the difference between Memory and Foundry IQ?

Memory stores durable interaction context such as preferences or learned facts, while Foundry IQ grounds the agent in authoritative enterprise knowledge. Put policy documents, product docs, and reference material in grounding; put stable user-specific preferences in Memory only when retention rules allow it.

### What should teams evaluate before adopting Foundry Agent Service?

Teams should evaluate runtime fit, framework compatibility, Entra identity design, Toolbox permissions, data residency, third-party model boundaries, Memory retention, trace visibility, evaluation coverage, and total cost. The biggest mistake is treating an agent like a prompt instead of a production service.
