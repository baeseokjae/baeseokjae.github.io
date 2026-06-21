---
cover:
  alt: 'Amazon Bedrock AgentCore Guide: Deploy Production AI Agents on AWS'
  image: /images/amazon-bedrock-agentcore-guide-2026.png
  relative: false
date: 2026-06-12 09:04:45+00:00
description: Practical Amazon Bedrock AgentCore guide for deploying secure, observable
  production AI agents on AWS.
draft: false
schema: schema-amazon-bedrock-agentcore-guide-2026
tags:
- AWS
- AI agents
- Amazon Bedrock
title: 'Amazon Bedrock AgentCore Guide: Deploy Production AI Agents on AWS'
---

Amazon Bedrock AgentCore is AWS's production platform for deploying, securing, observing, and governing AI agents built with frameworks such as LangGraph, CrewAI, LlamaIndex, and Strands Agents. Use it when your agent needs managed runtime isolation, enterprise identity, tool governance, memory, evaluation, and AWS-native operations instead of another prototype server.

## What Is Amazon Bedrock AgentCore?

Amazon Bedrock AgentCore is a managed AWS platform for taking code-first AI agents from local development to production operations with runtime hosting, memory, identity, tool access, observability, policy, browser automation, and code execution. AWS made AgentCore generally available on October 13, 2025, and GA added VPC, AWS PrivateLink, AWS CloudFormation, and resource tagging across its services. The important detail is that AgentCore is not a new prompt format or a single agent framework. It is the production control plane around agents you already build with frameworks such as LangGraph, CrewAI, LlamaIndex, and Strands Agents, and it can work with different foundation models. The platform matters because production agents fail in places demos ignore: credentials, network boundaries, tool authorization, memory drift, tracing, replay, cost, and incident response. The takeaway: Amazon Bedrock AgentCore is the AWS operations layer for serious agent deployments.

The mental model I use is simple: keep business reasoning in your agent code, then move infrastructure concerns into AgentCore services. Runtime runs the agent. Gateway brokers tools. Identity handles access. Memory persists state. Observability and Evaluations tell you whether the agent is behaving. Policy adds guardrails outside the application code.

## AgentCore vs Bedrock Agents: Which Should You Use?

AgentCore vs Bedrock Agents is a choice between code-first production infrastructure and faster Bedrock-native agent assembly. Bedrock Agents is usually the shorter path when your workflow fits AWS's managed agent model, knowledge bases, action groups, and foundation-model orchestration. Amazon Bedrock AgentCore is the better fit when you already have a LangGraph, CrewAI, LlamaIndex, or Strands Agents application and need runtime isolation, custom orchestration, Gateway-managed tools, Identity, Memory, Evaluations, Policy, and CloudWatch-backed operations. The difference became sharper after AgentCore reached GA on October 13, 2025, because it added the deployment and governance pieces enterprises expect around custom agents. Bedrock Agents can still be the right default for a small internal assistant. AgentCore becomes more compelling when the agent owns multi-step workflows, talks to sensitive systems, or needs framework portability. The takeaway: use Bedrock Agents for simple Bedrock-native builds and AgentCore for custom production agents.

| Decision point | Bedrock Agents | Amazon Bedrock AgentCore |
|---|---|---|
| Build style | Managed Bedrock configuration | Code-first agent application |
| Framework support | Bedrock-native | LangGraph, CrewAI, LlamaIndex, Strands Agents, and custom code |
| Best use case | Standard assistants and action workflows | Production agents with custom orchestration |
| Operations model | Simpler managed path | Runtime, Gateway, Identity, Memory, Policy, Evaluations, Observability |
| Portability | Lower | Higher at the framework layer, lower at AWS operations layer |

### What is the practical selection rule?

The practical selection rule is to start with the smallest platform that can meet your production requirements. If the agent needs only a few Bedrock action groups and a knowledge base, Bedrock Agents reduces code and deployment work. If you need explicit graph control, nonstandard tools, agent-specific memory, policy review, custom traces, or canary rollout discipline, AgentCore gives you the missing production surface.

## Core AgentCore Services Explained

Amazon Bedrock AgentCore services are modular production capabilities that wrap an AI agent with hosting, state, security, tools, execution environments, evaluation, and governance. The AWS documentation lists core services including Runtime, Memory, Identity, Gateway, Observability, Browser, Code Interpreter, Evaluations, Policy, Registry, Optimization, and Payments, with several newer capabilities arriving after the 2025 GA launch. Runtime hosts the agent application. Gateway exposes tools and APIs in a controlled way. Identity gives agents access to protected resources without hardcoding secrets. Memory stores session and long-term context. Browser and Code Interpreter let agents perform web and code tasks in isolated environments. Evaluations measures behavior, while Policy enforces rules outside the agent's prompt. This service split is useful because agent failures are rarely isolated to model quality. They usually involve permissions, tool misuse, missing traces, stale memory, and unsafe autonomy. The takeaway: AgentCore is valuable because each production risk has a named AWS service boundary.

| Service | What it does | Production question it answers |
|---|---|---|
| Runtime | Runs agent workloads | Where does the agent execute reliably? |
| Gateway | Connects tools and APIs | Which tools can the agent call, and how are calls audited? |
| Identity | Manages access | How does the agent authenticate without embedded secrets? |
| Memory | Stores short-term and long-term context | What should the agent remember across turns or sessions? |
| Observability | Emits traces, metrics, and logs | How do operators debug decisions and failures? |
| Evaluations | Scores agent behavior | How do we block regressions before and after release? |
| Policy | Applies external controls | Which actions are disallowed even if the model tries them? |

### Why does modularity matter?

Modularity matters because agent platforms age quickly when every concern is buried in application code. I have seen teams ship a capable local agent, then spend weeks extracting credentials, adding tracing, rewriting retry behavior, and explaining tool calls to security reviewers. AgentCore's model encourages you to isolate those responsibilities from day one, which makes audits and later service swaps less painful.

## What Does a Production AWS Agent Architecture Look Like?

A production AWS agent architecture on AgentCore usually starts with a framework agent in Runtime, routes external capabilities through Gateway and Identity, stores useful context in Memory, and feeds logs, traces, metrics, evaluations, and policy decisions into an operations loop. A real deployment should also include VPC access, AWS PrivateLink where needed, IAM least privilege, CloudWatch dashboards, alarms, release gates, and rollback procedures. Those requirements became easier to standardize when AgentCore GA added VPC, PrivateLink, CloudFormation, and resource tagging across services. In practice, I design the agent path as a controlled transaction: user request enters through an application API, the agent plans, tool requests pass through Gateway, credentials come from Identity, state reads and writes pass through Memory, and every meaningful step is traceable. The model call is only one component in that path. The takeaway: production architecture is about controlling the agent's environment, not just improving prompts.

A common architecture is an API front end, an AgentCore Runtime-hosted worker, a Gateway layer for internal APIs, Memory for customer or workflow continuity, and Observability wired into CloudWatch. For regulated workflows, Policy should sit near tool execution rather than inside the prompt. That prevents the weakest control from being a sentence the model can ignore.

### What should you keep outside the agent?

You should keep authorization, network boundaries, irreversible action rules, billing limits, and release gates outside the agent. The agent can propose actions, but infrastructure should decide what it is allowed to do. For example, a procurement agent can draft a vendor order, but Gateway and Policy should block purchases over a threshold unless an approval token is present.

## How Do You Deploy an Agent to AgentCore Runtime?

Deploying an agent to AgentCore Runtime means packaging your existing agent application as a managed workload, configuring its execution environment, connecting required AWS permissions, and exposing a controlled invocation path. Runtime, Browser, and Code Interpreter are priced with active-consumption billing at $0.0895 per vCPU-hour and $0.00945 per GB-hour, so deployment choices affect both reliability and cost. The workflow is similar to moving any service from a laptop into production: define dependencies, environment variables, IAM roles, network access, health behavior, logging, and release strategy. The difference is that an agent also needs deterministic tool contracts, timeout boundaries, and trace-friendly step names. I recommend deploying the thinnest useful agent first: one model, one or two tools, one memory strategy, and one measurable task. Once that path is observable, add autonomy. The takeaway: treat Runtime deployment like a production service release, not a prompt upload.

The deployment path I prefer is local test, container or package validation, Runtime deployment, synthetic invocation, trace review, evaluation gate, then limited traffic. Do not start by moving every prototype feature into the first Runtime release. The first production milestone should prove that the deployment path, permissions, logging, and rollback process work under controlled traffic.

### What should the first deployment include?

The first deployment should include one happy-path workflow, one failure-path workflow, explicit timeouts, structured errors, and enough trace metadata to identify the user request, agent version, tool name, model, latency, and outcome. That sounds basic, but those fields are what you need when an agent starts retrying a tool or returning plausible but wrong answers.

## How Do Gateway and Identity Connect Agent Tools Safely?

AgentCore Gateway and Identity connect agent tools safely by separating what the agent wants to do from how production systems authorize and execute that action. Gateway pricing is published at $0.005 per 1,000 API invocations, $0.025 per 1,000 Search API invocations, and $0.02 per 100 tools indexed per month, which makes tool governance a visible platform cost rather than hidden glue code. Gateway gives you a place to define, expose, search, and audit tools. Identity gives the agent a controlled way to access AWS services and enterprise resources without embedding secrets in prompts, configuration files, or framework callbacks. This split matters because tool access is where agents move from text generation into real operational impact. A bad answer is annoying; a bad tool call can change data, leak information, or trigger a customer-facing process. The takeaway: Gateway and Identity turn tool use into an auditable production interface.

For example, a support agent might need customer lookup, refund eligibility, ticket update, and email-draft tools. Do not give that agent broad database credentials. Put those capabilities behind Gateway, bind them to clear schemas, authorize through Identity, and log each request with the agent version and user context.

### How should tool schemas be designed?

Tool schemas should be narrow, typed, and aligned with business actions instead of raw infrastructure access. Prefer `create_refund_case` over `run_sql_query`, and prefer `get_order_status` over a generic internal API proxy. Narrow tools make policy easier, reduce prompt injection blast radius, and give evaluations a clearer target for expected behavior.

## How Do Memory, Browser, and Code Interpreter Capabilities Change an Agent?

AgentCore Memory, Browser, and Code Interpreter change an agent by giving it persistent context, web interaction, and isolated code execution beyond ordinary model responses. AgentCore Memory pricing includes $0.25 per 1,000 short-term memory events, $0.75 per 1,000 long-term memory records stored per month with built-in strategies, and $0.50 per 1,000 memory retrievals. Those numbers force a useful design question: what is worth remembering? Memory should capture durable user preferences, workflow state, and prior decisions, not every token the model saw. Browser is useful when an agent must interact with web interfaces that lack clean APIs. Code Interpreter is useful for data transformation, file inspection, calculations, and generated scripts. Each capability also expands risk: stale memory can mislead decisions, browser automation can hit brittle pages, and code execution needs isolation. The takeaway: add these capabilities only when the workflow earns the extra operational surface.

In production, I treat Memory as a product feature with retention rules, not a cache. I treat Browser as a fallback when APIs are missing, not the first integration path. I treat Code Interpreter as a sandbox for bounded computation, not a general-purpose server. Those boundaries keep the agent easier to test and easier to explain during review.

### What should agents remember?

Agents should remember facts that improve future task completion and remain valid long enough to justify storage. Good examples include a customer's preferred region, a project-specific approval rule, or the last completed step in a long workflow. Bad examples include temporary reasoning traces, sensitive secrets, raw documents without retention review, and model guesses that were never verified.

## How Should Observability, Evaluations, and Policy Controls Work?

Observability, Evaluations, and Policy controls should work as a closed feedback loop that records what the agent did, measures whether it behaved correctly, and blocks actions that violate external rules. AWS says AgentCore Evaluations includes 13 built-in evaluators for common quality dimensions and supports CI/CD thresholds plus production sampling. Policy for Amazon Bedrock AgentCore became generally available on March 3, 2026, in 13 AWS Regions, making governance a first-class part of the platform instead of custom middleware. Observability should capture the full request path: user input, model choice, planned steps, tool calls, memory access, policy decisions, latency, error classes, and final output. Evaluations should run before release and on sampled production traffic. Policy should enforce rules that cannot depend on model cooperation. The takeaway: production agents need measurable behavior and enforceable boundaries, not just better prompts.

I like to define four operational signals: task success, tool correctness, safety compliance, and cost per completed workflow. Task success asks whether the user got the intended outcome. Tool correctness asks whether the agent called the right tool with valid arguments. Safety compliance asks whether policy was followed. Cost per workflow keeps teams honest about runaway loops.

### Where do evaluations belong in CI/CD?

Evaluations belong both before deployment and after deployment. In CI/CD, run a fixed scenario suite against the candidate agent version and block release when success, safety, or regression thresholds fail. In production, sample real interactions, strip or protect sensitive data as required, and compare results across versions so you catch behavior drift before customers report it.

## What Does Amazon Bedrock AgentCore Pricing Mean in Practice?

Amazon Bedrock AgentCore pricing is a platform cost model layered on top of foundation-model token costs, tool backend costs, storage, and ordinary AWS infrastructure. Runtime, Browser, and Code Interpreter use active-consumption pricing at $0.0895 per vCPU-hour and $0.00945 per GB-hour, while Gateway, Memory, and Evaluations have their own usage dimensions. AWS's pricing examples estimate 10 million monthly customer-support Runtime sessions at $7,235 when sessions run 60 seconds with 70% I/O wait, because CPU billing excludes idle I/O wait time. That example is useful because many agents spend time waiting on model responses, APIs, browsers, databases, and human approvals. Still, the platform line item is not the whole bill. Model tokens, vector search, logs, traces, memory records, and downstream API calls can dominate depending on workload shape. The takeaway: model AgentCore cost per completed workflow, not per chat message.

| Cost area | What drives it | How to control it |
|---|---|---|
| Runtime | vCPU and memory during active work | Shorter workflows, bounded loops, async waits |
| Model usage | Input and output tokens | Prompt trimming, retrieval discipline, smaller models where acceptable |
| Gateway | API calls, search calls, indexed tools | Narrow tool catalog, avoid unnecessary discovery |
| Memory | Events, records, retrievals | Store durable facts only, expire stale state |
| Observability | Logs, traces, metrics volume | Structured sampling and retention tiers |
| Evaluations | Test volume and evaluator use | Run broad suites in CI, sample production intelligently |

### What is a useful cost metric?

A useful cost metric is cost per successful completed workflow. Cost per token or cost per Runtime invocation can mislead because agents vary in retries, tool calls, latency, and success rate. A cheap agent that fails 30% of tasks can cost more operationally than a more expensive one that completes work correctly with fewer escalations.

## What Security and Compliance Checklist Should Teams Use?

A security and compliance checklist for Amazon Bedrock AgentCore should cover IAM least privilege, VPC and PrivateLink network paths, secret-free tool access, policy enforcement, memory retention, trace redaction, evaluation gates, audit logs, and incident response ownership. GA support for VPC, AWS PrivateLink, CloudFormation, and resource tagging matters because these are the controls AWS teams already use to standardize production workloads. The checklist should also include agent-specific concerns: prompt injection through retrieved content, tool argument validation, approval thresholds for irreversible actions, tenant isolation, memory poisoning, browser session isolation, and code execution limits. Compliance teams usually do not object to agents because they are agents; they object because ownership, logs, access, and rollback are vague. Make those explicit before launch. The strongest pattern is to let the agent recommend actions while infrastructure enforces permission and policy decisions. The takeaway: secure AgentCore deployments by applying normal AWS controls plus agent-specific guardrails.

Use a release checklist that names owners. Security owns IAM review and data classification. Platform owns Runtime, network, logging, and alarms. Product owns allowed actions and human approval thresholds. Engineering owns tool schemas, tests, and rollback. Compliance owns retention and audit requirements. Without owners, the checklist becomes a document nobody trusts during an incident.

### Which controls should be mandatory before launch?

Mandatory launch controls should include least-privilege IAM roles, no secrets in prompts or source-controlled config, Gateway-mediated tool access, policy rules for high-risk actions, trace redaction for sensitive data, memory retention limits, automated evaluations, on-call runbooks, and rollback. For customer-facing agents, add tenant isolation tests and abuse-case testing before any broad rollout.

## What Failure Modes and Runbooks Matter Most?

The most important AgentCore failure modes are tool misuse, runaway loops, stale or poisoned memory, prompt injection, partial workflow completion, hidden cost spikes, weak observability, and unsafe fallback behavior. Fortune Business Insights cites Capgemini data that 14% of organizations have deployed AI agents, 23% have pilots, and 61% are exploring or preparing for deployment, which means many teams are about to discover that agent incidents look different from ordinary API failures. A model can return a valid sentence while the workflow is wrong. A tool can succeed while the business action is inappropriate. A memory record can be syntactically correct while semantically stale. Your runbooks must therefore start from symptoms operators can see: repeated tool calls, policy denials, latency spikes, evaluation failures, unusual memory retrievals, or customer escalations. The takeaway: write runbooks for behavior failure, not only infrastructure failure.

| Failure mode | Signal | First response |
|---|---|---|
| Runaway loop | High repeated tool calls or long Runtime sessions | Stop workflow, cap retries, inspect trace |
| Tool misuse | Valid API call with wrong business intent | Disable tool route, review schema and policy |
| Memory poisoning | Bad facts repeatedly retrieved | quarantine records, add write validation |
| Prompt injection | Tool calls triggered by untrusted content | tighten content boundaries and policy rules |
| Cost spike | Higher cost per completed workflow | sample traces, inspect retries and model selection |

### What should a runbook contain?

A runbook should contain detection signals, severity rules, immediate containment actions, rollback steps, owners, dashboards, and a short decision tree. For agents, add examples of bad traces and expected policy denials. During an incident, nobody wants to debate whether a tool call was "agentic"; they need a concrete way to stop damage and restore service.

## When Is AgentCore the Right Choice and When Is It Overkill?

AgentCore is the right choice when an AI agent is important enough to need managed runtime isolation, AWS-native security, controlled tool access, memory, observability, evaluations, policy, and operational ownership. The global agentic AI market was valued at $7.29 billion in 2025 and is projected to grow from $9.14 billion in 2026 to $139.19 billion by 2034 at a 40.50% CAGR, which explains why platforms are racing to own production agent infrastructure. That growth does not mean every chatbot needs AgentCore. For a demo, an internal prototype, or a simple retrieval assistant, a lighter Bedrock Agents setup or a small service may be enough. AgentCore makes more sense when failure has business impact, when tools touch private systems, when multiple teams need auditability, or when custom frameworks are already part of your stack. The takeaway: choose AgentCore for operational leverage, not because every agent needs a platform.

The lock-in tradeoff is real. Your framework code may remain portable, but Gateway, Identity, Memory, Policy, and Observability decisions will align you with AWS. For AWS-heavy teams, that is often a benefit because it fits existing IAM, networking, CloudWatch, and deployment workflows. For cloud-neutral teams, it may be too much platform commitment.

### What is the smallest sensible starting point?

The smallest sensible starting point is one production-grade workflow with Runtime, Gateway for one or two tools, Identity, Observability, and a small evaluation suite. Add Memory only when repeated interactions require it. Add Browser only when APIs are unavailable. Add Policy early if the agent can affect money, access, customer records, or external communications.

## What Is the Final Production Deployment Checklist?

A final production deployment checklist for Amazon Bedrock AgentCore should prove that the agent can run, act, fail, recover, and be audited under real operating conditions. At minimum, confirm Runtime health checks, VPC or PrivateLink paths, IAM least privilege, Gateway tool schemas, Identity configuration, Memory retention rules, Observability dashboards, Evaluation thresholds, Policy enforcement, cost alarms, rollback, and human escalation paths. The reason this checklist matters is that AI agents combine application logic, model behavior, tool execution, and state, so a release can fail even when each individual component appears healthy. Before broad launch, run synthetic tasks, adversarial prompts, timeout scenarios, bad tool responses, policy-denied actions, memory updates, and canary traffic. Then review traces with the team that will operate the system. The takeaway: do not call an AgentCore deployment production-ready until operations can explain and control its behavior.

Use this checklist as the release gate:

| Area | Release question |
|---|---|
| Runtime | Can the agent start, scale, time out, and roll back cleanly? |
| Tools | Are Gateway schemas narrow, validated, and audited? |
| Identity | Are permissions least-privilege and secret-free? |
| Memory | Are retention, retrieval, update, and deletion rules defined? |
| Observability | Can operators trace a user request through model and tool steps? |
| Evaluations | Are release thresholds defined and enforced in CI/CD? |
| Policy | Are high-risk actions blocked outside prompt logic? |
| Cost | Are per-workflow cost targets and alarms configured? |
| Incident response | Does on-call know how to disable tools or roll back versions? |

## FAQ

Amazon Bedrock AgentCore FAQ answers should focus on deployment decisions, cost, governance, and how the platform differs from simpler Bedrock agent options. AgentCore became generally available on October 13, 2025, and the most relevant 2026 update for governance-focused teams is Policy GA on March 3, 2026, across 13 AWS Regions. Developers usually ask whether AgentCore replaces their existing framework, whether it requires Amazon Bedrock models, how pricing works, whether Memory is required, and when the platform is excessive. The short answer is that AgentCore wraps production infrastructure around agents; it does not eliminate the need to design workflows, tools, tests, and operations carefully. If your agent is experimental, start smaller. If it touches production systems, customer data, or regulated workflows, treat AgentCore as a serious platform candidate. The takeaway: AgentCore answers production questions that framework demos usually leave unresolved.

### Does Amazon Bedrock AgentCore replace LangGraph or CrewAI?

Amazon Bedrock AgentCore does not replace LangGraph, CrewAI, LlamaIndex, or Strands Agents. It provides production services around agents built with those frameworks. You still design the workflow, prompts, tool interfaces, and application behavior in code. AgentCore helps with runtime hosting, identity, gateway access, memory, observability, evaluations, policy, and related operations.

### Do I have to use Amazon Bedrock foundation models with AgentCore?

Amazon Bedrock AgentCore is positioned as framework and model flexible, but your exact model choices should match supported AWS documentation, compliance requirements, latency needs, and cost targets. Many teams will use Amazon Bedrock models because the integration path is natural, but the main AgentCore value is the production control plane around the agent.

### Is AgentCore Memory required for production agents?

AgentCore Memory is not required for every production agent. Use it when remembering preferences, workflow state, prior decisions, or cross-session context improves task quality. Avoid memory for secrets, unverified guesses, and data that lacks retention approval. A stateless agent with strong tool access and good retrieval can be safer and cheaper.

### How should I estimate AgentCore costs?

Estimate AgentCore costs per completed workflow. Include Runtime vCPU and GB-hours, Gateway invocations, Memory events and retrievals, Evaluations, model tokens, logs, traces, and downstream services. Also measure success rate. A workflow that needs repeated retries, long browser sessions, or large memory retrievals can cost more than expected even when individual unit prices look small.

### What is the biggest production risk with AgentCore?

The biggest production risk is assuming managed infrastructure automatically makes agent behavior safe. AgentCore gives you strong building blocks, but you still need narrow tool schemas, least-privilege permissions, policy enforcement, evaluation gates, trace review, cost alarms, and runbooks. The dangerous failures are usually wrong actions, not obvious service crashes.