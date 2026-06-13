---
title: "Microsoft Open Trust Stack AI agent governance: ASSERT, ACS, and OpenInference for production"
date: 2026-06-13T09:03:45+00:00
tags: ["ai agents", "governance", "microsoft foundry"]
description: "A production guide to Microsoft Open Trust Stack AI agent governance with ASSERT, ACS, OpenInference, and Foundry."
draft: false
cover:
  image: "/images/microsoft-foundry-open-trust-stack-guide-2026.png"
  alt: "Microsoft Open Trust Stack AI agent governance: ASSERT, ACS, and OpenInference for production"
  relative: false
schema: "schema-microsoft-foundry-open-trust-stack-guide-2026"
---

Microsoft Open Trust Stack AI agent governance is Microsoft's 2026 pattern for making agents testable, enforceable, and observable. The practical model is simple: use ASSERT before release, ACS during runtime, and OpenInference traces across both so engineering, security, and SRE teams can inspect the same evidence.

## What does Microsoft mean by the Open Trust Stack?

Microsoft Open Trust Stack AI agent governance is a production governance approach announced at Build 2026 that combines two open-source projects, ASSERT and Agent Control Specification, with OpenInference telemetry. ASSERT means Adaptive Spec-driven Scoring for Evaluation and Regression Testing, while ACS defines portable runtime controls for agent behavior. Microsoft frames the audience as the 6 to 13 million generative AI developers building agents across frameworks such as LangChain, CrewAI, LiteLLM, and OpenAI. The stack is not a single hosted product or a replacement for secure application design. It is a lifecycle: evaluate agent behavior before release, enforce policies while the agent acts, and preserve trace evidence for debugging, audits, and regression analysis. The important takeaway is that governance becomes an engineering system, not a policy document.

### Why is the stack useful for production teams?

The stack is useful because it separates three jobs that teams often blur together: evaluation, control, and observability. ASSERT scores whether an agent should ship. ACS decides whether a live action should proceed. OpenInference records what happened in a format that tools can read later. That split makes failures easier to diagnose.

### What is the core workflow?

The core workflow is evaluate, enforce, trace, and repeat. A team instruments agent runs with OpenInference, runs ASSERT against risky workflows, applies ACS controls at runtime, then uses production traces to update tests and policies. That feedback loop is what turns isolated guardrails into a governance program.

## Why does agent autonomy outrun prompt-level safety?

Agent autonomy outruns prompt-level safety because agents do not only generate text; they read state, call tools, use credentials, modify systems, and chain decisions over multiple steps. Microsoft updated its agentic AI failure taxonomy in June 2026 after 12 months of red team engagements against deployed agentic systems, adding seven new failure mode categories. The same update cited 99 CVEs in MCP-related software during 2025 and noted that tool poisoning had moved from theory into live attack surface. A prompt instruction like "never delete production data" is advisory when the model is one component inside a tool-using runtime. Production safety needs deterministic checks around the model, especially before external tool calls, state changes, and irreversible actions. The takeaway is that prompt safety can help, but it cannot be the enforcement boundary.

### Where do prompt-only controls fail?

Prompt-only controls fail when the dangerous decision is outside the final answer. For example, an agent may summarize a request safely while still passing tainted arguments into a ticketing, email, database, or deployment tool. The output looks benign, but the side effect is already committed.

### What changes when agents get tools?

Tools turn model mistakes into system actions. A wrong classification can become a refund, a leaked record, or a merged pull request. That is why agent governance should inspect tool name, arguments, identity, environment, approval state, and resulting trace, not just the model's natural language response.

## How does ASSERT handle policy-driven evaluation before release?

ASSERT is Microsoft's policy-driven evaluation framework for testing agent behavior before release and catching regressions after changes. Microsoft describes ASSERT as framework-compatible across LangChain, CrewAI, LiteLLM, OpenAI, and other agent stacks, which matters because most enterprises already have mixed experimentation environments. In practice, ASSERT should be treated like a test harness for governance requirements: define expected behavior, score traces and outcomes, compare versions, and block releases when a policy regression appears. A useful ASSERT suite does not only ask whether the final answer was accurate. It checks whether the agent refused unsafe instructions, preserved tenant boundaries, used the right tool, requested human approval, and left enough trace data for investigation. The takeaway is that ASSERT moves safety review into CI/CD instead of leaving it as a manual launch checklist.

### What should teams evaluate with ASSERT?

Teams should evaluate the workflows where autonomy creates business or security risk. Start with account changes, payment actions, production operations, privileged data access, external messages, and code execution. For each workflow, define acceptable tool usage, refusal behavior, approval requirements, and expected trace fields.

### How should ASSERT fit into CI/CD?

ASSERT should run as a release gate for high-risk agent changes and as a scheduled regression suite for production prompts, tools, and policies. A failing score should identify the scenario, policy, trace, and version that changed. Treat the result like a test failure, not an opinion from a separate review board.

## How does ACS enforce runtime controls at the five agent checkpoints?

Agent Control Specification, or ACS, is a portable runtime control standard for enforcing policies while an agent is operating. Microsoft defines five validation checkpoints in the agent lifecycle: input, LLM, state, tool execution, and output. That placement is the important engineering detail. ACS is not another instruction added to the system prompt; it is an external control layer that can inspect and block behavior before the model sees sensitive input, before state is updated, before a tool runs, or before output leaves the system. In production, I would use ACS-style controls for actions that need deterministic approval: deleting records, sending customer communications, reading regulated data, changing infrastructure, or invoking expensive workflows. The takeaway is that ACS gives teams a runtime enforcement plane around agent autonomy.

### Which checkpoint matters most?

Tool execution is usually the most important checkpoint because it is where intent becomes side effect. Input and output controls reduce exposure, but tool controls prevent expensive or irreversible actions. For privileged tools, validate identity, scope, arguments, environment, approval state, and rate limits before execution.

### What should ACS policies look like?

ACS policies should be small, explicit, and easy to audit. A good policy says which action is controlled, which condition triggers a deny or approval, which identity can approve it, and which trace fields must be emitted. YAML policy files from Microsoft's Agent Governance Toolkit are a practical starting pattern.

## Why is OpenInference the trace contract connecting evals, controls, and observability?

OpenInference is the telemetry contract that lets ASSERT, ACS, and production observability tools speak about the same agent run. The OpenInference specification defines an attribute schema and span-kind taxonomy on top of OpenTelemetry, and every OpenInference trace is a valid OTLP trace. That means a single trace can describe user input, model calls, retrieved context, tool invocations, control decisions, outputs, token usage, and errors without locking the team into one vendor dashboard. This is the part of the stack I would implement first, because you cannot evaluate or enforce what you cannot see. When ASSERT consumes trace spans, ACS emits policy-decision spans, and Phoenix or Arize AX reads the same traces, governance evidence becomes portable. The takeaway is that OpenInference turns agent behavior into inspectable operational data.

### What should an agent trace include?

An agent trace should include the request, model call, selected tools, tool arguments, control decisions, retrieved context, state changes, final output, latency, token use, errors, and version metadata. Sensitive values should be redacted or hashed, but the structure must remain useful for debugging.

### Why not use normal application logs?

Normal logs are useful, but they rarely capture agent semantics consistently. Agent governance needs spans that distinguish LLM calls from retriever calls, tool calls, approvals, policy denials, and output filtering. OpenInference gives those events a shared shape while still riding on OpenTelemetry infrastructure.

## How does this fit with Microsoft Foundry Agent Service?

Microsoft Foundry Agent Service is Microsoft's managed platform for building, deploying, scaling, evaluating, and monitoring agents, and it provides a practical hosting layer for Open Trust Stack patterns. The service includes end-to-end tracing, metrics, Application Insights integration, Microsoft Entra identity, RBAC, content filters, virtual network isolation, built-in tools, MCP support, and publishing paths. Those platform controls do not remove the need for ASSERT, ACS, or OpenInference; they give enterprise teams a place to attach them. In a Microsoft-heavy environment, Foundry can handle identity, deployment, network boundaries, and operational telemetry while the open stack handles portable evaluation, runtime policies, and trace semantics across services. The takeaway is that Foundry is the managed runtime option, while the Open Trust Stack is the governance architecture.

### When should teams use Foundry Agent Service?

Teams should use Foundry Agent Service when they need enterprise identity, deployment management, Azure observability, private networking, and governed access to built-in tools. It is especially useful when agents must integrate with Microsoft Entra, Azure AI, Application Insights, and existing security operations.

### When should teams stay framework-neutral?

Teams should stay framework-neutral when they have agents spread across Python services, LangChain, CrewAI, internal orchestration, multiple clouds, or third-party platforms. In that case, OpenInference and portable ACS-style policy enforcement prevent governance from becoming tied to one runtime.

## What is a reference architecture for production agent governance?

A reference architecture for production agent governance has four layers: an instrumented agent runtime, a policy enforcement plane, an evaluation pipeline, and an observability and incident response layer. In a Microsoft-oriented stack, the runtime might be Foundry Agent Service with Entra identity, RBAC, content filters, and network isolation. The policy plane applies ACS controls at input, LLM, state, tool execution, and output checkpoints. The evaluation pipeline runs ASSERT suites against OpenInference traces before release and during regression testing. The observability layer exports OpenInference-compatible spans into Application Insights, Phoenix, Arize AX, or another OpenTelemetry backend. This architecture works because every layer has a clear job and shared evidence. The takeaway is that production governance should look like normal platform engineering, with policies and traces as first-class artifacts.

| Layer | Primary job | Example controls |
|---|---|---|
| Runtime | Execute the agent safely | Identity, RBAC, sandboxing, network isolation |
| ACS policy plane | Enforce live decisions | Deny, approve, redact, rate limit |
| ASSERT pipeline | Test behavior before release | Regression suites, policy scores, red-team scenarios |
| Observability | Investigate and improve | OpenInference spans, metrics, incident timelines |

### Where should human approval sit?

Human approval should sit inside the runtime control path, not in a separate chat thread. For high-risk tool calls, the agent should pause with structured context: action, arguments, identity, policy reason, trace link, and expected impact. The approval or denial should be recorded as a trace event.

### How should teams handle identity?

Teams should give agents scoped identities with least privilege, not shared service accounts with broad access. The runtime should know which user, agent, tool, tenant, and environment are involved. ACS policies can then make decisions based on identity and context instead of static allowlists.

## How should teams implement the stack in phases?

Teams should implement Microsoft Open Trust Stack AI agent governance in phases: instrument first, evaluate second, enforce third, and monitor continuously. A common mistake is starting with a large policy catalog before the team has traces that show how agents actually behave. Start by emitting OpenInference spans for representative workflows and use those traces to identify risky tools, missing metadata, and ambiguous state changes. Next, build ASSERT suites for workflows that touch money, credentials, customer data, production systems, or external communication. Then add ACS policies around irreversible actions and approval-required operations. Finally, feed production incidents, denials, and near misses back into the ASSERT regression suite. The takeaway is that incremental rollout produces better controls than a one-time governance rewrite.

| Phase | Goal | Exit criteria |
|---|---|---|
| 1. Instrument | See agent behavior | OpenInference traces cover model and tool spans |
| 2. Evaluate | Catch risky regressions | ASSERT blocks known unsafe workflows |
| 3. Enforce | Stop unsafe live actions | ACS policies protect high-risk checkpoints |
| 4. Monitor | Improve from evidence | Incidents generate new tests and policies |

### What should the first sprint deliver?

The first sprint should deliver trace coverage for one production-like workflow and one risky tool. Capture model spans, tool spans, arguments, policy placeholders, errors, and version metadata. Do not try to govern every agent. Prove that a real run can be inspected end to end.

### What should wait until later?

Broad policy catalogs, automated remediation, and organization-wide dashboards should wait until teams understand their trace quality and failure modes. Early governance work should focus on evidence and enforcement for a few important actions. Scale the pattern after engineers trust the signal.

## Which policies and metrics should engineering teams track?

Engineering teams should track policies and metrics that reveal whether agents are safe to operate, not just whether they answer correctly. The Microsoft Agent Governance Toolkit public preview targets Python 3.10+ and shows YAML policy patterns for controlling tool calls, which is a useful model for readable enforcement. Start with policies for irreversible tools, privileged data access, external communication, production infrastructure, tenant boundaries, and human approval. Then measure policy denials, approval latency, unsafe regression rate, trace completeness, tool error rate, retry loops, token cost, and incident recurrence. A dashboard with 30 charts is less useful than five metrics tied to release gates and on-call action. The takeaway is that governance metrics should connect directly to blocked risk and operational response.

| Control area | Example policy | Metric to watch |
|---|---|---|
| Tool execution | Require approval for delete, refund, deploy | Approval rate and denial reason |
| Data access | Block cross-tenant retrieval | Tenant-boundary violations |
| Output | Redact secrets and regulated identifiers | Redaction count and leak reports |
| State | Prevent unsafe memory writes | State mutation failures |
| Cost | Cap loops and expensive tools | Tokens, retries, timeout rate |

### What does a good deny policy do?

A good deny policy blocks a specific unsafe action and records enough context to fix the cause. For example, deny production database writes from a non-production agent identity, include the agent version and requested SQL operation, and emit a trace event that SRE can query.

### What does a good approval policy do?

A good approval policy pauses only when judgment is needed. It should avoid asking humans to rubber-stamp every action. Require approval for high-impact operations, provide structured context, set an expiration, record the approver, and feed approval outcomes back into evaluation data.

## What are the limitations and preview risks?

The limitations of the Microsoft Open Trust Stack are the same limitations that show up in most young governance systems: preview maturity, uneven framework integration, policy drift, trace quality, and organizational adoption. Microsoft's Agent Governance Toolkit is described as public preview, so teams should expect API changes, missing adapters, and rough edges around local deployment. ACS also depends on runtimes actually honoring the checkpoints where controls are attached. OpenInference solves the trace schema problem, but it does not automatically guarantee complete, redacted, or accurate spans. ASSERT can catch regressions only for scenarios the team has written or generated. In regulated environments, third-party observability tools may also require data residency, retention, and access reviews. The takeaway is that the stack is promising, but it still needs disciplined platform ownership.

### When should teams use third-party observability?

Teams should use third-party observability when they need richer trace analysis, prompt and retrieval inspection, evaluation workflows, or cross-framework visibility beyond the default cloud dashboard. Phoenix and Arize AX are relevant examples because they already work around OpenInference traces and agent debugging workflows.

### What should security review before rollout?

Security should review identity boundaries, trace redaction, policy bypass paths, approval records, tool permissions, MCP server exposure, and retention settings. The review should focus on whether a compromised or confused agent can act outside its intended scope, not only whether model outputs look safe.

## What are the final recommendations for engineering and security teams?

The final recommendation is to treat Microsoft Open Trust Stack AI agent governance as a control loop for production software: trace every meaningful step, test risky behavior before release, enforce deterministic runtime policies, and use incidents to improve the next evaluation suite. For a team shipping agents in 2026, the minimum viable governance stack should include OpenInference instrumentation, ASSERT-style regression tests for high-risk workflows, ACS-style controls around tool execution, scoped identities, human approval for irreversible actions, and an observability backend that on-call engineers can query. Do not wait for a perfect standard or vendor platform before adding these pieces. Start with the workflows where a wrong action costs money, leaks data, or changes production state. The takeaway is that agent governance works when it becomes part of the delivery pipeline and runtime, not a document reviewed after launch.

### What should engineering own?

Engineering should own instrumentation, test suites, runtime integration, policy implementation, and operational dashboards. These are software delivery responsibilities. Security can define risk requirements, but engineers must make policies executable, traces reliable, and failures visible during normal development and incident response.

### What should security own?

Security should own risk classification, approval requirements, red-team scenarios, exception review, and audit expectations. The best operating model is shared: security defines what must be controlled, and engineering turns those requirements into ASSERT tests, ACS policies, and OpenInference evidence.

## What questions do teams ask about Microsoft Open Trust Stack AI agent governance?

Microsoft Open Trust Stack AI agent governance raises practical questions because it sits across application engineering, security architecture, platform operations, and AI observability. The most common confusion is whether ASSERT, ACS, and OpenInference are competing tools. They are not. ASSERT evaluates behavior before release, ACS enforces controls at runtime, and OpenInference provides the trace data that both systems and observability tools can consume. Another common question is whether this stack is only for Microsoft Foundry. It is not; Microsoft positions ASSERT and ACS as open projects and OpenInference is based on OpenTelemetry-compatible traces. The right implementation depends on risk, runtime maturity, and existing cloud commitments. The takeaway is that teams should adopt the pattern according to their agent risk profile, not by copying a reference diagram blindly.

### Is ASSERT a replacement for red teaming?

ASSERT is not a replacement for red teaming. It is where red-team findings should become repeatable regression tests. Human red teaming discovers new failure modes, while ASSERT helps ensure known failures do not return after model, prompt, tool, or policy changes.

### Is ACS the same as prompt guardrails?

ACS is not the same as prompt guardrails. Prompt guardrails influence the model, while ACS-style controls sit around the runtime and can block input, state changes, tool execution, or output. That distinction matters when an agent has credentials and can affect external systems.

### Do I need Microsoft Foundry to use the Open Trust Stack?

You do not need Microsoft Foundry to use the full pattern. Foundry can provide a managed Azure runtime with identity and observability integrations, but ASSERT, ACS concepts, and OpenInference traces are most valuable when they remain portable across frameworks and deployment environments.

### What should be governed first?

Govern irreversible or externally visible actions first. Good candidates include refunds, customer emails, production deployments, database writes, privileged data retrieval, account changes, and code execution. These workflows create clear business risk and make the value of runtime controls easy to prove.

### How do teams know governance is working?

Governance is working when risky regressions are blocked before release, unsafe runtime actions are denied or routed to approval, traces explain incidents quickly, and production findings produce new tests. If the only output is a dashboard nobody uses, the governance system is not mature.
