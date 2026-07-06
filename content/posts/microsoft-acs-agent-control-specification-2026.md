---
cover:
  alt: Agent Control Specification ACS AI Agent Governance Guide
  image: /images/microsoft-acs-agent-control-specification-2026.png
  relative: false
date: 2026-06-13 10:05:06+00:00
description: A developer guide to Agent Control Specification ACS AI agent governance,
  runtime policy checks, and enterprise adoption.
draft: false
schema: schema-microsoft-acs-agent-control-specification-2026
tags:
- AI agents
- AI governance
- Microsoft ACS
title: Agent Control Specification ACS AI Agent Governance Guide
---

Agent Control Specification ACS AI agent governance is a portable way to apply policy checks while an agent runs, not just before it starts. ACS defines standard intervention points, policy manifests, evidence inputs, and auditable verdicts so teams can govern tool use, approvals, data handling, and shutdown behavior across agent frameworks.

## What Is the Agent Control Specification (ACS)?

Agent Control Specification is an open, vendor-neutral runtime governance standard for AI agents that defines where policy decisions happen and what evidence those decisions receive. Microsoft describes ACS as framework-independent, and its published model names eight intervention points, including `pre_model_call`, `pre_tool_call`, `post_tool_call`, and `output`. The practical idea is simple: instead of hiding safety rules inside prompts, SDK callbacks, or one-off middleware, ACS makes agent governance a portable contract. A host runtime supplies a snapshot of the agent state, tool metadata, annotations from evidence providers, and the policy target. A policy engine returns a verdict such as allow, warn, deny, or escalate. For developers, ACS is closest to policy-as-code for autonomous systems. The takeaway: ACS standardizes runtime control so security teams can review one governance model across many agent implementations.

### How is ACS different from ordinary guardrails?

ACS is different from ordinary guardrails because it governs the agent while work is happening, not only when a prompt enters or an answer leaves the model. A prompt guardrail might say "do not send secrets," but ACS can check the exact tool call, destination, data classification, user identity, and approval state before the tool executes. That makes it better suited to agents that browse repositories, query databases, call payment APIs, or send email.

## Why Do AI Agents Need Runtime Governance Now?

AI agents need runtime governance now because deployment is outrunning control systems in real enterprises. IBM's June 2026 study says technology leaders expect a 38% increase in deployed AI agents by 2027, while only 11% feel completely prepared and 77% say AI adoption is moving faster than governance. That matches what I see in engineering reviews: the first agent pilot often has a narrow prompt and a demo-safe tool, but the second version gets write access, credentials, retrieval, schedulers, or customer data. Gartner has also warned that governance gaps will lead many enterprises to demote or decommission autonomous agents by 2027. Static reviews cannot keep up with agents that branch, retry, call tools, and recover from failures. The takeaway: runtime governance is necessary because agent behavior is dynamic, stateful, and operationally risky.

### Where do agent failures usually start?

Agent failures usually start at the boundary between reasoning and action. The model may summarize a request correctly, then choose the wrong account, overbroad query, unsafe API, or unapproved recipient. Traditional application controls help, but agents add ambiguity: intent is inferred, plans are generated, and tool arguments are composed at runtime. ACS targets that boundary by giving policy engines a standard place to inspect state before and after each sensitive step.

## How Does ACS Work With Policy Manifests, Snapshots, Evidence, and Verdicts?

ACS works by combining a policy manifest with runtime snapshots, evidence annotations, and policy verdicts at standardized checkpoints. In Microsoft's Agent Governance Toolkit documentation, the manifest shape includes version metadata, inheritance through `extends`, named policies, intervention points, tool metadata, annotators, and approval configuration. The agent host calls the policy engine at a defined checkpoint and passes a structured input: intervention point, policy target, runtime snapshot, available annotations, and tool context. Evidence providers can attach classifications such as sensitive data, destination risk, user role, or provenance labels. The policy engine evaluates those inputs and returns a decision the host must enforce. This is intentionally stateless from the policy engine's point of view: the host owns the live runtime context and provides it on each check. The takeaway: ACS separates policy decision logic from agent framework code without ignoring runtime context.

### What does a policy manifest usually contain?

A policy manifest usually contains metadata, policy names, enforcement points, tool descriptions, evidence providers, and approval rules. In practice, I would expect a security team to own the shared baseline manifest while product teams extend it for local tools. For example, a finance agent might inherit the company DLP policy, then add a stricter `pre_tool_call` rule for wire-transfer APIs and customer export tools.

## What Are the Eight ACS Intervention Points?

The eight ACS intervention points are the lifecycle checkpoints where an agent host can ask a policy engine for a governance decision: `agent_startup`, `input`, `pre_model_call`, `post_model_call`, `pre_tool_call`, `post_tool_call`, `output`, and `agent_shutdown`. The most important number here is eight because it makes ACS more precise than a generic "before and after" guardrail. `agent_startup` can verify identity, configuration, and policy version before work begins. `input` can classify the user's request. `pre_model_call` and `post_model_call` can control model routing and inspect generated plans. `pre_tool_call` is the critical gate before real-world side effects. `post_tool_call` can inspect tool results and update evidence. `output` governs what leaves the system, and `agent_shutdown` records final state. The takeaway: ACS maps governance to the actual lifecycle of an autonomous task.

| Intervention point | What it controls | Example policy |
|---|---|---|
| `agent_startup` | Agent identity, configuration, policy version | Deny startup if policy bundle is missing |
| `input` | User request and task scope | Warn on regulated-data requests |
| `pre_model_call` | Model selection and prompt context | Deny sending secrets to external models |
| `post_model_call` | Plans and generated arguments | Escalate if the plan includes deletion |
| `pre_tool_call` | Tool execution before side effects | Require approval for payment API calls |
| `post_tool_call` | Tool results and returned data | Redact sensitive fields from retrieved rows |
| `output` | Final user-visible response | Block customer data leakage |
| `agent_shutdown` | Final audit and cleanup | Persist decision trace without raw content |

### Which intervention point matters most?

`pre_tool_call` matters most for production risk because it is the last reliable checkpoint before an agent changes an external system. I treat it like an authorization hook with richer context: who asked, what tool is being called, what arguments were generated, what data was used, and whether approval exists. `post_tool_call` is the second checkpoint I would prioritize because it catches sensitive results before they propagate.

## What Can ACS Policies Decide?

ACS policies can decide whether an agent action should be allowed, warned, denied, escalated, or transformed depending on host and policy-engine support. Microsoft describes core verdicts such as allow, warn, deny, and escalate, while practical governance systems often add transformations like redaction, argument rewriting, or destination narrowing. The value is not the vocabulary itself; it is the consistent enforcement contract. A `pre_tool_call` rule might allow a read-only CRM lookup, warn on a broad export, deny a request that includes social security numbers, and escalate a refund over $500 to a human approver. A `post_tool_call` rule might allow a database result but transform it by redacting fields before the model sees them. The takeaway: ACS turns governance from advice into enforceable runtime decisions tied to specific agent actions.

### Should policies fail open or fail closed?

Policies should fail closed for high-impact actions and explicitly declare any fail-open exceptions for low-risk reads. If an approval service, annotator, or policy engine is unavailable, a payment, deletion, email, or production deployment should stop. For a low-risk documentation lookup, warning and telemetry may be acceptable. The decision should be encoded in the manifest, not left to whatever behavior the SDK adapter happens to implement.

## How Does ACS Compare With Prompt Guardrails, Framework Callbacks, MCP, and Observability?

ACS refers to runtime policy governance, while prompt guardrails, framework callbacks, MCP, and observability each solve adjacent but different problems. Prompt guardrails shape model behavior but are weak against tool misuse and jailbreak pressure. Framework callbacks in LangChain, AutoGen, CrewAI, Semantic Kernel, or custom orchestration code can enforce controls, but they are usually framework-specific. MCP standardizes tool access, not enterprise policy decisions across every agent lifecycle checkpoint. Observability tools record traces, spans, state transitions, approvals, and failures, but recording an unsafe action is not the same as stopping it. ACS sits between these layers as the decision contract: it tells the host where to ask, what evidence to provide, and what verdict to enforce. The takeaway: ACS complements existing agent infrastructure rather than replacing prompts, tool protocols, or telemetry.

| Layer | Primary job | ACS relationship |
|---|---|---|
| Prompt guardrails | Influence model behavior | Useful signal, not enough enforcement |
| Framework callbacks | Hook into one runtime | Possible ACS adapter surface |
| MCP | Standardize tool connections | Tool metadata can feed ACS policies |
| Observability | Trace what happened | ACS decisions should be logged there |
| ACS | Decide and enforce policy | Governance contract across runtimes |

### Why not just use framework callbacks?

Framework callbacks are useful when one team owns one stack, but they do not scale cleanly across mixed agent environments. A company may have LangChain prototypes, OpenAI Agents SDK services, Semantic Kernel workflows, and vendor agents running at the same time. Without a shared contract, each team invents slightly different policy hooks, logs, and approval behavior. ACS gives security and platform teams a common target even when application teams choose different frameworks.

## Where Does ACS Fit in Microsoft's Agent Governance Toolkit and Foundry Stack?

ACS fits into Microsoft's broader agent governance stack as the runtime control layer, alongside evaluation and validation tools such as ASSERT and platform services in Microsoft Foundry. Microsoft Foundry's 2026 framing describes a loop: use ASSERT to identify policy failures, apply ACS controls at runtime checkpoints, then rerun evaluation to validate that the agent behaves better. That loop matters because governance is not a single review before launch. A team can test a procurement agent, find that it attempts unapproved supplier changes, add a `pre_tool_call` escalation policy, and rerun the evaluation suite. The Agent Governance Toolkit positions ACS as the decision-runtime core behind policy evaluation, with SDK surfaces documented for Python, Node.js, .NET, and Rust. The takeaway: ACS is most useful when paired with repeatable evaluation and production telemetry.

### What role does telemetry play?

Telemetry turns ACS from a blocking mechanism into an audit system. The useful records are not raw prompts or private outputs; they are policy IDs, reason codes, verdicts, intervention points, annotator results, durations, approval identifiers, and error classes. Microsoft's ACS documentation emphasizes content-redacted telemetry by default. That is the right default because security teams need evidence of control without creating a new sensitive-data warehouse in the observability backend.

## Which Framework and SDK Support Should Developers Watch?

Developers should watch ACS support across agent frameworks, SDKs, tool protocols, policy engines, and observability vendors because the specification only becomes valuable when hosts enforce it consistently. TechCrunch reported SDK or plugin support around the ACS launch for LangChain, OpenAI Agents SDK, Anthropic Agents SDK, AutoGen, CrewAI, Semantic Kernel, Microsoft.Extensions.AI, MCP tools, and related ecosystems. Microsoft also named partners across governance, security, observability, and frameworks, including Arize AI, IBM, CrewAI, KPMG, and Zscaler. The specific vendor list will change, but the evaluation criteria should not. Ask which intervention points are implemented, whether tool metadata is complete, whether policy failures are fail-closed, and whether decision telemetry is exported in a usable format. The takeaway: ACS compatibility is only meaningful when enforcement depth is documented.

### What should an SDK adapter prove?

An SDK adapter should prove that it calls the policy engine at the promised intervention points and enforces the returned verdict. For `pre_tool_call`, that means the tool does not run after a deny verdict. For escalation, it means the agent blocks until the approval workflow returns a valid decision. For telemetry, it means every decision has a durable trace with a policy ID and reason code.

## What Enterprise Use Cases Benefit Most From ACS?

Enterprise ACS use cases benefit most when agents have tools, data access, side effects, or regulatory obligations. PwC's 2025 survey found 79% of senior executives said AI agents were already being adopted in their companies, and 88% planned to increase AI-related budgets because of agentic AI. Those agents are moving into workflows where "just trust the prompt" is not a serious control. Tool permissions are the first use case: restrict which APIs an agent can call for a user, tenant, or task. Data loss prevention is second: classify inputs, retrieved documents, and outputs before information leaves a boundary. Human approval is third: route high-risk actions to named approvers. Audit trails are fourth: preserve redacted decision evidence for compliance reviews. The takeaway: ACS is strongest where autonomous action meets enterprise accountability.

### What would this look like in a finance workflow?

In a finance workflow, ACS could allow an agent to read invoices, warn when a supplier record is incomplete, require human approval for a payment above $500, and deny any transfer to an unverified bank account. The manifest would define the tool sinks, approval rules, and evidence required for each decision. The audit log would show the policy version, approver, verdict, and reason code without storing the full invoice text.

### What would this look like in a developer workflow?

In a developer workflow, ACS could let an agent read repository files, require approval before opening a pull request, deny production secret access, and block destructive database commands. A `post_tool_call` rule could redact credentials returned by a shell tool before the model sees them. This is especially relevant for coding agents because their power comes from tool access, not from chat alone.

## What Are the Limitations and Implementation Risks?

ACS has limitations because a specification does not enforce itself; the host runtime, SDK adapter, approval service, evidence providers, telemetry pipeline, and surrounding infrastructure must all behave correctly. Rubrik's 2026 survey found that 86% of IT and security leaders expect AI agents to outpace their organization's security guardrails within a year, and only 23% report full visibility into agents operating in their environments. ACS can reduce that gap, but it cannot fix invisible agents, missing identity, weak tool authorization, or network paths that bypass the governed host. A compromised runtime could fail to call the policy engine. An incomplete adapter could skip `post_tool_call`. A noisy annotator could create false confidence. The takeaway: ACS is a governance contract, not a substitute for defense in depth.

### Why might network enforcement still matter?

Network enforcement still matters because an agent runtime may not be the only control point between generated intent and external systems. Aviatrix argues that ACS-style policy can be compiled into multicloud network controls across AWS, Azure, Google Cloud, and Kubernetes. I would not treat network controls as a replacement for ACS, but they are valuable backstops for destination controls, protocol restrictions, and blast-radius reduction when runtime enforcement fails.

## How Should Teams Evaluate an ACS-Compatible Vendor or Agent Platform?

Teams should evaluate an ACS-compatible vendor by testing enforcement behavior, not by accepting a badge or launch announcement. Grant Thornton's 2026 AI Impact Survey found 78% of C-suite and senior business leaders lack strong confidence they could pass an independent AI governance audit within 90 days, which means evidence quality matters as much as feature claims. Start with a matrix of the eight intervention points and ask the vendor to show which are supported today. Then test fail-closed behavior, approval workflows, redacted telemetry, policy versioning, reason codes, annotator quality, and integration with your identity provider. Run adversarial cases: overbroad exports, unapproved recipients, sensitive tool arguments, malformed tool metadata, and unavailable policy services. The takeaway: ACS procurement should be based on observable enforcement and audit evidence.

| Evaluation question | Strong answer | Weak answer |
|---|---|---|
| Which intervention points are enforced? | Documented per SDK and tested | "We support guardrails" |
| What happens on policy engine failure? | Fail-closed for high-risk actions | Runtime-specific default |
| Is telemetry content-redacted? | Decision metadata without raw content | Full prompts in logs |
| How are approvals recorded? | Named approver, reason, timestamp | Chat message or manual note |
| Can policies be versioned? | Immutable versions in traces | Mutable config only |

### What is the fastest proof-of-control test?

The fastest proof-of-control test is to create a policy that denies one harmless but observable tool call, then verify that the tool does not execute, the agent receives a clear denial, and telemetry records the intervention point, policy ID, reason code, and verdict. Repeat the same test for an approval path and a policy-engine outage. This catches shallow integrations quickly.

## How Can Developers and Security Teams Adopt ACS Practically?

Developers and security teams can adopt ACS practically by starting with high-risk tool calls, not by trying to model every possible agent behavior on day one. McKinsey's 2026 AI trust research reports that 74% of respondents identify inaccuracy and 72% cite cybersecurity as highly relevant AI risks, while active mitigation still trails awareness. A realistic first rollout should cover `pre_tool_call` and `output` for one production agent. Define tool metadata, classify data boundaries, choose fail-closed actions, and log redacted decision metadata. Add human approval for irreversible operations. Then expand to `input`, `post_tool_call`, and model-routing policies. Pair ACS policies with evaluation suites, incident reviews, and regular policy version audits. The takeaway: ACS adoption works best as an incremental control program tied to real agent risk.

1. Inventory production and pilot agents with tool access.
2. Classify tools by read-only, write, financial, destructive, external communication, and regulated-data impact.
3. Add `pre_tool_call` policies for the highest-risk tools first.
4. Add `output` controls for sensitive data leaving the system.
5. Configure fail-closed behavior for irreversible actions.
6. Route escalations to named human approval systems.
7. Export redacted decision telemetry to the existing observability stack.
8. Rerun agent evaluations after every material policy change.

### What should the first ACS policy cover?

The first ACS policy should cover a tool whose misuse would be obvious and costly but easy to test safely. Good candidates are outbound email, customer export, payment initiation, production deployment, and database mutation tools. Define who can call it, under what task scope, with which argument constraints, and when approval is required. Avoid starting with vague behavior rules; start with concrete tool boundaries.

## FAQ: Agent Control Specification and AI Agent Governance

Agent Control Specification FAQ answers should focus on what ACS does at runtime, how it relates to existing agent stacks, and what teams should verify before trusting it in production. The most important practical fact is that ACS defines eight governance checkpoints and structured policy verdicts, but each implementation still depends on host enforcement. That distinction answers most buyer and developer questions. ACS is not a new model, not a replacement for MCP, and not a complete compliance program by itself. It is a portable decision contract that can make policies reusable across frameworks, approvals auditable, and tool actions controllable. Teams adopting ACS should start by testing whether deny and escalation decisions actually stop risky behavior in their agent runtime. The takeaway: ACS is useful when it produces enforceable decisions and durable evidence.

### Is ACS only for Microsoft agent platforms?

ACS is not only for Microsoft agent platforms. Microsoft introduced and documents much of the current ecosystem, but the specification is framed as open and vendor-neutral. Its value depends on support from non-Microsoft frameworks, SDKs, observability systems, policy engines, and security vendors. A team should still verify whether a given integration supports the intervention points it needs.

### Does ACS replace MCP?

ACS does not replace MCP. MCP standardizes how agents connect to tools and external resources, while ACS standardizes how runtime policy decisions can be made around agent behavior. In a mature architecture, MCP tool metadata can become evidence for ACS decisions, and ACS can decide whether a specific MCP tool call should proceed.

### Can ACS stop prompt injection?

ACS can reduce the blast radius of prompt injection, but it cannot eliminate prompt injection by itself. If a malicious document convinces an agent to send data to an external endpoint, a `pre_tool_call` or `output` policy can deny the action. The prompt injection still occurred; ACS helps stop or contain the harmful side effect.

### What teams should own ACS policies?

ACS policies should be jointly owned by platform engineering, security, compliance, and the application team that understands the workflow. Security can define baseline controls, but application owners know which tools are normal for the task. The best operating model is shared policy-as-code review with versioned manifests and production telemetry.

### Is ACS ready for regulated industries?

ACS is relevant to regulated industries, but readiness depends on the implementation. Finance, healthcare, HR, legal, and public-sector teams need identity integration, approval records, policy versioning, evidence retention, redacted telemetry, and independent auditability. ACS can help structure those controls, but auditors will evaluate the full system, not the specification alone.