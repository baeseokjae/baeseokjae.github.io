---
cover:
  alt: 'OWASP Agentic Applications: 2026 Developer Security Checklist'
  image: /images/owasp-top-10-agentic-applications-2026.png
  relative: false
date: 2026-06-14 09:04:37+00:00
description: A developer checklist for the OWASP Top 10 for Agentic Applications 2026,
  covering identity, tools, memory, and runtime controls.
draft: false
schema: schema-owasp-top-10-agentic-applications-2026
tags:
- agentic-ai
- security
- owasp
title: 'OWASP Agentic Applications: 2026 Developer Security Checklist'
---

OWASP agentic applications security is the practice of limiting what AI agents can decide, access, remember, execute, and delegate. The 2026 OWASP Agentic Top 10 gives developers a checklist for shipping agents that call tools, persist state, and act across real systems without turning autonomy into uncontrolled production risk.

## What Is the OWASP Top 10 for Agentic Applications 2026?

The OWASP Top 10 for Agentic Applications 2026 is a security framework for AI systems that plan, choose actions, call tools, use memory, and coordinate with other agents. OWASP released it on December 9, 2025, after work from more than 100 industry experts, researchers, and practitioners. The list is different from the OWASP LLM Top 10 because it focuses on agent behavior, not only model input and output. A chatbot can give a bad answer; an agent can approve a refund, run a shell command, update a CRM record, leak a token through a tool call, or ask another agent to continue the mistake. For developers, the useful shift is to treat each agent as a production actor with identity, permissions, state, budget, and failure modes. The takeaway: secure agentic applications by controlling autonomy, not just prompts.

The ten risks are named ASI01 through ASI10. They cover goal hijacking, tool misuse, identity abuse, supply chain weaknesses, unexpected code execution, memory poisoning, insecure inter-agent communication, cascading failures, human trust exploitation, and rogue agents.

## Why Do Agentic Applications Need a Different Security Checklist?

Agentic applications need a different security checklist because they convert model output into real actions across APIs, databases, files, queues, browsers, and other agents. Deloitte's 2026 State of AI in the Enterprise survey of 3,235 IT and business leaders found only 21% have a mature governance model for agentic AI, while 74% expect at least moderate AI agent use by 2027. That gap matters at code level. A prompt-injection bug in a retrieval app may produce bad text; the same bug in an agent with billing, ticketing, or deployment tools can modify live state. Traditional controls like output filtering, prompt hardening, and model evaluation still help, but they do not define who the agent is, which tool parameters are legal, how memory is written, or when execution must stop. The takeaway: agent security starts where LLM security ends, at action boundaries.

The practical model I use is "least agency." Least privilege asks what a principal may access. Least agency asks how freely that principal may pursue a goal. An internal support agent may read account status, draft replies, and suggest refunds, but it should not issue refunds without a separate approval path, even if the same service account technically can.

| Control question | Traditional LLM app | Agentic application |
|---|---:|---:|
| Can it call external tools? | Usually no or limited | Yes, often many |
| Does it persist memory? | Optional | Common |
| Can it change production state? | Rare | Core capability |
| Does it need an identity? | Sometimes | Always |
| Can failures cascade? | Usually low | High when agents delegate |

## What Are the 10 OWASP Agentic Application Risks at a Glance?

The OWASP Agentic Top 10 risks are a taxonomy for the main ways autonomous AI systems fail when goals, tools, identity, memory, code execution, communication, and human trust are not constrained. Promptfoo's OWASP agentic AI testing guide lists the 2026 risks as ASI01 Agent Goal Hijack, ASI02 Tool Misuse and Exploitation, ASI03 Identity and Privilege Abuse, ASI04 Agentic Supply Chain Vulnerabilities, ASI05 Unexpected Code Execution, ASI06 Memory and Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation, and ASI10 Rogue Agents. The list is useful in code review because each item maps to a concrete engineering question: what can change the goal, what can invoke a tool, what credentials are used, what state is trusted, and what stops runaway behavior. The takeaway: treat the Top 10 as review prompts, not as a poster.

| Risk | Developer control to add first |
|---|---|
| ASI01 Agent Goal Hijack | Immutable task envelope and instruction hierarchy |
| ASI02 Tool Misuse and Exploitation | Typed tool schemas, allowlists, and parameter validation |
| ASI03 Identity and Privilege Abuse | Agent-specific identity with short-lived scoped tokens |
| ASI04 Agentic Supply Chain Vulnerabilities | Signed tools, pinned MCP servers, reviewed prompts and datasets |
| ASI05 Unexpected Code Execution | Sandboxes, syscall limits, egress policy, artifact scanning |
| ASI06 Memory and Context Poisoning | Separate trusted memory, quarantine writes, provenance metadata |
| ASI07 Insecure Inter-Agent Communication | Mutual authentication and signed message envelopes |
| ASI08 Cascading Failures | Budgets, circuit breakers, retry caps, rollback plans |
| ASI09 Human-Agent Trust Exploitation | Approval UI with diffs, risk labels, and independent verification |
| ASI10 Rogue Agents | Runtime detection, drift checks, revocation, and kill switches |

## How Should Developers Prevent Agent Goal Hijack and Tool Misuse?

Agent goal hijack is an attack where external content, user input, retrieved documents, or tool results redirect the agent away from its approved objective; tool misuse is the follow-on risk where that redirected agent invokes capabilities in unsafe ways. IBM's June 2026 AI agent study reported an average of 54 AI agent incidents per surveyed organization in the prior year, with 17% classified as high severity. In practice, these incidents often start with ordinary ambiguity: a support ticket includes instructions to ignore policy, a web page tells the browser agent to export cookies, or a retrieved document asks the agent to email confidential data. Developers should protect the objective as a signed task envelope, validate each tool call against policy, and require approval when a call changes money, permissions, production data, or external communication. The takeaway: never let retrieved text become operational authority.

### What does a secure task envelope include?

A secure task envelope is a server-side object that states the agent's goal, allowed tools, allowed resources, maximum budget, approval requirements, and expiry time. The model can reason inside that envelope, but it cannot rewrite the envelope. Store the envelope outside the prompt, pass only the minimum necessary fields into context, and log every policy decision against the envelope ID.

### How should tool calls be constrained?

Tool calls should be constrained with typed schemas, parameter allowlists, server-side authorization, and deterministic validators before execution. Do not rely on "the model should only call this for safe cases." Validate account IDs against the task scope, block arbitrary URLs unless explicitly allowed, cap batch sizes, and require human approval for irreversible writes. Treat tools as public APIs exposed to a confused deputy.

## How Should Developers Handle Agent Identity and Privilege Abuse?

Agent identity and privilege abuse happens when an AI agent borrows a human account, over-scoped service account, long-lived API key, or shared token to perform actions beyond the task's real authority. Cloud Security Alliance 2026 research on non-human identity and agentic AI found that 78% of organizations have no documented policy for creating or removing AI identities, and only 8% have high confidence that legacy IAM can manage AI and non-human identity risks. That is a direct warning for developers: if the agent uses a generic backend credential, logs cannot answer which agent acted, who owned it, why it acted, or how to revoke only that capability. Each production agent needs its own principal, owner, scopes, token lifetime, audit trail, and deprovisioning path. The takeaway: an agent without identity boundaries is an unaccountable production user.

Build identity boundaries before adding more tools. A coding agent that can read repositories may need separate scopes for issue comments, pull requests, package publishing, secrets access, and CI reruns. A finance agent may read invoices by default but require a step-up approval token to submit payment. The token minted for a task should expire quickly, carry the task ID, and be useless outside that task's resources.

| Bad pattern | Better pattern |
|---|---|
| Agent uses the operator's OAuth session | Agent gets a task-bound delegated token |
| One service account for all agents | One principal per agent type and environment |
| Static API key in prompt context | Short-lived credential retrieved at call time |
| Broad `write:*` scope | Narrow tool-specific scopes with approval gates |
| Manual cleanup | Lifecycle policy tied to deployment and owner records |

## How Should Developers Secure the Agentic Supply Chain and Code Execution?

Agentic supply chain security is the process of verifying every component that can influence an agent's plan or actions, including prompts, tool definitions, MCP servers, browser extensions, orchestration code, model dependencies, RAG datasets, memory stores, and generated code runners. Palo Alto Networks' agentic AI security guidance emphasizes inventory, behavior, permissions, memory use, and data access because a vulnerable tool or poisoned dataset can become an execution path. ASI04 and ASI05 belong together in developer workflows: the same agent that installs a package, loads an MCP server, or writes a script may later execute code based on untrusted instructions. Pin versions, sign tool manifests, review prompt changes, sandbox execution, block ambient credentials, and scan artifacts before promotion. The takeaway: secure agents by treating their tools and context as executable supply chain inputs.

### What should go into an agent asset inventory?

An agent asset inventory should record the agent owner, model, system prompt version, tool list, scopes, memory stores, datasets, MCP servers, deployment environment, outbound network permissions, and approval gates. Keep it generated from deployment metadata where possible. A spreadsheet that drifts from production is worse than no inventory because it creates false confidence during incident response.

### How should generated code be run?

Generated code should run in a locked sandbox with no default secrets, limited CPU and wall-clock time, read-only mounts unless needed, explicit network egress, and disposable storage. Capture stdout, stderr, file diffs, package installs, and external calls. If the generated code needs production data, move the approval to the data access boundary rather than trusting the model's explanation.

## How Should Developers Prevent Memory and Context Poisoning?

Memory and context poisoning refers to attacks where untrusted content is stored, retrieved, or ranked in a way that later changes an agent's decisions. McKinsey's 2026 AI trust research reports that 74% of respondents identify inaccuracy and 72% cite cybersecurity as highly relevant AI risks as adoption expands; memory poisoning sits at the intersection of both. A poisoned customer note, support transcript, vector record, browser cache, or inter-agent summary can quietly persist after the original session ends. Developers should separate trusted policy memory from user-derived memory, attach provenance to every stored item, quarantine writes from external content, and require review before memories affect privileged actions. Retrieval should prefer signed, source-ranked records over opaque similarity alone. The takeaway: persistent memory must be governed like a database, not treated like a larger prompt.

For implementation, create distinct stores for policy, user preferences, session summaries, operational facts, and untrusted observations. Label records with source, author, timestamp, task ID, tenant, sensitivity, and review state. When the agent proposes a memory write, pass it through a classifier and a deterministic policy check. For high-risk domains, require a human or another trusted service to approve facts that will be reused across sessions.

The retrieval side matters just as much. Show the model the provenance and confidence of retrieved facts. Down-rank old records. Refuse instructions embedded inside documents that are supposed to be data. If a retrieved record asks the agent to change its goal, reveal secrets, disable tools, or contact an external endpoint, classify that as hostile content, not guidance.

## How Should Developers Secure Inter-Agent Communication and Prevent Cascading Failures?

Insecure inter-agent communication occurs when agents exchange tasks, summaries, tool outputs, credentials, or decisions without authentication, authorization, message integrity, and clear responsibility boundaries; cascading failure occurs when one bad action multiplies through retries, delegation, queues, or dependent agents. IBM's 2026 study found that among high-severity AI agent incidents, 37% resulted in data exposure or security breaches, 33% caused cascading system failures, and 17% triggered compliance issues. Multi-agent systems increase blast radius because each agent may treat another agent's output as trusted context. Developers should sign message envelopes, authenticate sender and receiver identities, include task scope in each message, cap delegation depth, enforce budgets, and add circuit breakers that stop repeated failures. The takeaway: agent-to-agent messages need the same rigor as service-to-service API calls.

The clean pattern is boring distributed-systems engineering. Use a message schema with sender, receiver, task ID, parent task ID, allowed action, expiry, trace ID, and signature. Do not pass raw credentials between agents. Do not allow an agent to invent new agents or new queues without a control-plane approval. If a planner delegates to a worker, the worker should receive a narrower task, not the planner's full authority.

For cascading failure, set hard limits: maximum tool calls per task, maximum retries per tool, maximum spend, maximum changed records, maximum emails sent, maximum child tasks, and maximum wall time. Add rollback where state changes are possible. On repeated policy denials or validation failures, stop execution and mark the task for review instead of asking the model to "try another way."

## How Should Developers Reduce Human-Agent Trust Exploitation and Rogue Agent Risk?

Human-agent trust exploitation happens when users approve unsafe actions because the agent sounds confident, hides important details, or frames a risky action as routine; rogue agent risk appears when an agent keeps acting outside its owner, policy, deployment, or approved goal. Grant Thornton's 2026 AI Impact Survey says 78% of business executives lack strong confidence they could pass an independent AI governance audit within 90 days, which tracks with what developers see in product reviews: approval flows are often added late and log trails are incomplete. Developers should design approval screens that show diffs, affected resources, confidence limits, policy reasons, and irreversible consequences. Runtime systems should detect drift, unusual tool use, repeated denials, new destinations, and ownerless agents. The takeaway: human review only works when the reviewer sees evidence, not persuasion.

Approval UX should be specific. "Approve action" is weak. "Send 183 customer emails using template v12 to segment enterprise-trial-expiring" is reviewable. Show the before-and-after state for writes, the exact external recipients for messages, the cost and quota impact for cloud actions, and the policy rule that requires approval. Make decline easy and non-punitive so operators do not learn to rubber-stamp prompts.

Rogue-agent detection belongs in runtime, not quarterly governance. Alert when an agent calls a tool it has never used, runs outside expected hours, contacts new domains, creates long chains of child tasks, writes unusual memory records, or operates after owner removal. The kill switch should revoke credentials, stop queues, cancel pending jobs, and preserve traces for investigation.

## What Build-Time and Runtime Controls Should Be on the Developer Checklist?

A developer checklist for OWASP agentic applications should separate build-time controls that prevent unsafe capabilities from shipping and runtime controls that detect, limit, and recover from unsafe behavior after deployment. Ivanti's 2026 research says 87% of security teams consider adopting agentic AI a priority, and 77% report at least some comfort allowing AI to act without human review. That comfort is only defensible when developers implement controls outside the prompt: policy enforcement, identity scoping, deterministic validation, observability, incident response, and revocation. Build-time review should ask whether the agent can change state, who owns it, what tools it can call, where memory lives, and how approvals work. Runtime review should ask what the agent actually did and how fast it can be stopped. The takeaway: prompts explain intent; controls enforce limits.

| Stage | Checklist item | Evidence to require |
|---|---|---|
| Build | Threat model each agent goal | Abuse cases for goal hijack, tool misuse, memory poisoning |
| Build | Define agent identity | Principal, owner, scopes, token TTL, revocation path |
| Build | Validate tools server-side | Schemas, allowlists, policy tests, negative tests |
| Build | Review supply chain inputs | Pinned tools, MCP manifests, prompt diffs, dataset provenance |
| Build | Design approval gates | Risk thresholds, UI copy, audit events |
| Runtime | Trace every action | Task ID, tool call, parameters, result, policy decision |
| Runtime | Enforce budgets | Tool-call, spend, retry, time, delegation, and write limits |
| Runtime | Monitor drift | Baselines for tools, destinations, memory writes, failure rates |
| Runtime | Provide kill switches | Credential revocation, queue stop, job cancellation |
| Runtime | Test incidents | Replay traces, rollback state, rotate credentials |

## How Do OWASP LLM Controls Map to OWASP Agentic AI Risks?

OWASP LLM controls map to OWASP agentic AI risks as a foundation, not a replacement, because agentic systems add action, persistence, identity, and coordination on top of model interaction. McKinsey reports that nearly two-thirds of respondents cite security and risk concerns as the top barrier to fully scaling agentic AI, which is consistent with the jump from "the model may say something unsafe" to "the system may do something unsafe." Prompt injection defenses help with ASI01 goal hijack, but they do not create task-bound credentials for ASI03, signed tool manifests for ASI04, sandbox policies for ASI05, or circuit breakers for ASI08. Developers should keep LLM security tests, then add agent-specific tests around every place output becomes action. The takeaway: LLM security protects the conversation; agent security protects the workflow.

| Existing LLM control | Agentic extension |
|---|---|
| Prompt-injection tests | Goal hijack tests with tool-call assertions |
| Output moderation | Action policy enforcement before tool execution |
| RAG source filtering | Memory write approval and provenance-aware retrieval |
| Data loss prevention | Scoped credentials and egress controls |
| Model evaluation | End-to-end task simulations with rollback checks |
| Logging prompts and outputs | Logging plans, tool calls, approvals, memory writes, and delegation |

For code review, ask one extra question after every LLM control: "What happens if the model is wrong but persuasive?" If the answer is "it can still execute," move the control outside the model. The policy engine, identity provider, sandbox, queue, and database must be able to say no even when the model says yes.

## What Is a Practical 30-Day Plan for Securing Agentic Applications?

A practical 30-day plan for securing agentic applications starts by inventorying agents and ends with enforced runtime controls on the highest-risk workflows. IBM reports that organizations embedding controls directly into AI systems experience 25% fewer incidents, while manual governance increases incident risk as adoption scales. That finding matches the engineering reality: review documents do not stop an over-scoped token, poisoned memory write, or runaway retry loop. In week one, list every agent, owner, tool, credential, memory store, and production write path. In week two, add task envelopes, scoped identities, and tool validators. In week three, add approval gates, sandboxing, and trace logs. In week four, run red-team scenarios against OWASP ASI01 through ASI10 and fix the failures. The takeaway: secure the paths where agent autonomy becomes production change first.

Start with the agents that can send external messages, move money, change permissions, execute code, access secrets, or write shared memory. Those are your high-blast-radius systems. Internal read-only copilots can wait if they truly cannot act, persist cross-session state, or call privileged APIs.

At the end of 30 days, you should have three artifacts: an agent inventory, a risk register mapped to ASI01 through ASI10, and a small set of enforced controls in production. The goal is not perfect governance. The goal is to remove silent authority, invisible state, and unstoppable execution from the first production agents your organization depends on.

## FAQ

OWASP agentic applications FAQ sections should answer the operational questions developers ask when they move from LLM prototypes to production agents. The most common confusion is whether the OWASP Agentic Top 10 replaces the OWASP LLM Top 10; it does not. The agentic list extends the security model to systems that act through tools, memory, identity, and delegation. Developers also ask whether guardrails are enough, whether every agent needs its own identity, and how much runtime monitoring is necessary. The short answer is that prompts and guardrails are useful but insufficient once an agent can mutate state. Production teams need deterministic controls, scoped credentials, observability, and revocation, especially when a single workflow can touch tickets, code, customer data, and external APIs. The takeaway: use the FAQ below as a fast design review before letting an agent act autonomously.

### Is the OWASP Top 10 for Agentic Applications only for enterprise teams?

The OWASP Top 10 for Agentic Applications is useful for any developer building agents with tools, memory, or production access. A solo developer shipping a GitHub automation bot still needs scoped credentials, tool validation, and logs. Enterprise teams need more governance, but the core risks appear as soon as model output can trigger action.

### Does the OWASP Agentic Top 10 replace the OWASP LLM Top 10?

The OWASP Agentic Top 10 does not replace the OWASP LLM Top 10. Use the LLM list for prompt injection, data leakage, model behavior, and RAG risks, then use the agentic list for autonomy, tools, identity, memory persistence, inter-agent communication, cascading failures, and rogue behavior.

### Are prompt guardrails enough for AI agent security?

Prompt guardrails are not enough for AI agent security because the model is not the enforcement boundary. A production agent needs server-side policy checks, scoped credentials, validated tool calls, sandboxed execution, memory governance, trace logging, budgets, approval gates, and kill switches that work even when the model chooses the wrong plan.

### What is the first control to add to an existing production agent?

The first control to add is usually traceable, scoped identity. Once each agent action has a principal, owner, task ID, token scope, and audit event, you can investigate behavior and revoke access without shutting down unrelated systems. After identity, add tool validators and budget limits.

### How often should teams red-team agentic applications?

Teams should red-team agentic applications before production, after major tool or prompt changes, and on a recurring schedule for high-risk agents. Test indirect prompt injection, over-scoped tools, poisoned memory, unsafe code execution, delegation loops, approval bypasses, and kill-switch behavior against the OWASP ASI01 through ASI10 categories.