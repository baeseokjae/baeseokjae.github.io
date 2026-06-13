---
title: "Microsoft ASSERT Agent Evaluation Framework: Turn Agent Policies Into Executable Evals"
date: 2026-06-13T12:04:09+00:00
tags: ["AI agents", "AI evaluation", "Microsoft ASSERT"]
description: "A practical guide to using Microsoft ASSERT to convert AI agent policies into executable evaluations and regression tests."
draft: false
cover:
  image: "/images/microsoft-assert-agent-policy-evaluation-2026.png"
  alt: "Microsoft ASSERT Agent Evaluation Framework: Turn Agent Policies Into Executable Evals"
  relative: false
schema: "schema-microsoft-assert-agent-policy-evaluation-2026"
---

Microsoft ASSERT is an open-source agent evaluation framework that turns written AI policies, product requirements, and safety rules into executable tests. For developers, the value is practical: instead of debating whether an agent "mostly follows policy," ASSERT gives you repeatable scenarios, metrics, traces, and scorecards you can run before release.

## What Is the Microsoft ASSERT Agent Evaluation Framework?

Microsoft ASSERT is a requirement-driven evaluation harness for AI agents and LLM applications that converts natural-language specifications into executable evaluations. ASSERT stands for Adaptive Spec-driven Scoring for Evaluation and Regression Testing, and Microsoft describes it as open source and framework-agnostic for the estimated 6 million to 13 million generative AI developers working across today's agent ecosystem. The framework starts with written intent, such as a product requirement, policy document, system prompt, or launch checklist, then helps generate scenarios, datasets, metrics, and scorecards that can be run against hosted models, Python callables, or traced agent systems. The key idea is simple: agent behavior should be tested against your own requirements, not only against generic benchmarks. ASSERT is best understood as policy-as-evaluation for teams that need repeatable evidence before deploying autonomous workflows.

ASSERT is not just another leaderboard wrapper. In a real agent project, the risky behavior is usually local to the product: refund rules, data-access boundaries, escalation policies, regulated terms, or tool-use limits. Those requirements rarely appear in public benchmarks. ASSERT gives developers a way to express that local intent and keep testing it as prompts, models, tools, and orchestration code change.

## Why Do Agent Policy Evaluations Need More Than Generic Benchmarks?

Agent policy evaluation needs more than generic benchmarks because production agents fail in workflow-specific ways that broad model tests rarely capture. Databricks reported that multi-agent architectures grew by 327% in less than four months in its 2026 State of AI Agents research, while companies using evaluation tools got nearly 6x more AI projects into production. A benchmark can tell you whether a model answers math questions or follows simple instructions; it will not tell you whether your support agent respects a 30-day refund window, avoids exposing another customer's account data, logs the right escalation reason, and stops when a payment tool returns an ambiguous error. Agent evaluation has to inspect decisions, tool calls, intermediate state, and policy boundaries across multi-step execution. The takeaway: generic benchmarks are useful model signals, but requirement-driven evals are the production safety rail.

For developers, this changes what "done" means. A prompt that works in five demos is not production-ready. A workflow is closer to ready when its important policies have positive cases, negative cases, edge cases, failure thresholds, and trace evidence. That is the gap ASSERT tries to close.

### How Are Benchmarks Different From Requirement-Driven Evals?

Benchmarks are broad tests designed to compare models across shared tasks. Requirement-driven evals are local tests designed to verify a specific application promise. A benchmark might say Model A is better at instruction following; an ASSERT suite might show your deployed agent still violates the enterprise data-retention policy when a user asks for a CSV export after account closure.

| Evaluation type | Best for | Weak spot |
|---|---|---|
| Generic LLM benchmark | Model selection and broad capability checks | Misses product-specific policy behavior |
| Manual QA script | Early smoke testing | Hard to scale and easy to forget |
| Requirement-driven ASSERT suite | Repeatable agent policy and workflow testing | Depends on clear specs and reviewed test generation |
| Production observability | Finding live incidents and drift | Detects after traffic unless paired with pre-release evals |

## How Does ASSERT Turn Written Requirements Into Executable Evals?

ASSERT works by translating written requirements into structured behavior expectations, test scenarios, executable cases, judge criteria, and result artifacts. Microsoft positions the framework around a pipeline where human-readable intent becomes machine-runnable evaluation assets: requirements become acceptable and unacceptable behaviors, those behaviors become scenarios and datasets, and execution produces metrics and scorecards. A real example is a policy paragraph that says, "The agent must not reveal customer personal data unless the authenticated user owns the account." ASSERT can turn that into positive tests for authorized requests, negative tests for cross-account requests, and edge cases involving partial identifiers or tool failures. Developers can run those tests against a hosted model, a callable wrapper, or an OpenTelemetry/OpenInference-traced agent. The takeaway: ASSERT makes policy text operational by converting it into repeatable test evidence.

The practical benefit is traceability. When a test fails, the team can inspect not only the final response but also the intermediate actions, retrieved context, tool calls, and judge reasoning captured by the evaluation flow. That matters because many agent failures are not visible in the final message. The agent may call the wrong tool, pass too much data into a tool, skip an approval step, or recover from an error by inventing state.

### What Should a Good ASSERT Specification Include?

A good ASSERT specification includes the policy, the intended behavior, disallowed behavior, context assumptions, examples, and measurable pass/fail criteria. I would start with one narrow requirement rather than a broad governance slogan. "Do not leak private data" is too vague. "The agent must only return invoice details when the authenticated user ID matches the invoice owner ID" is testable.

Useful spec fields include:

| Spec element | Example |
|---|---|
| Policy statement | Only account owners can access invoice details |
| Positive behavior | Return invoice summary after ownership verification |
| Negative behavior | Refuse cross-account invoice requests |
| Edge case | User provides an invoice ID but no authenticated identity |
| Evidence | Trace must show ownership lookup before invoice retrieval |
| Threshold | 100% pass for cross-account denial tests |

## Where Does ASSERT Fit With ACS, OpenInference, and the Open Trust Stack?

ASSERT fits into Microsoft's open trust stack as the evaluation layer that finds behavior defects before and after runtime controls are applied. Microsoft Foundry describes ASSERT alongside Agent Control Specification, or ACS, where ASSERT handles requirements-driven evaluation and ACS handles runtime policy controls. Arize's OpenInference coverage adds the telemetry angle: ASSERT can consume agent traces as evidence, while ACS control decisions can also be emitted as spans. That means evaluation, enforcement, and observability can share the same trace substrate instead of living in disconnected reports. The loop is straightforward: run ASSERT to expose failures, add or tune ACS controls, observe the agent's OpenTelemetry or OpenInference spans, then re-run ASSERT to prove the failure rate improved. The takeaway: ASSERT is most valuable when it is connected to runtime controls and trace evidence, not treated as a one-off safety report.

This architecture is close to how experienced teams already treat normal software. Unit tests catch expected behavior, runtime guards prevent invalid operations, and observability explains what happened when reality is messier than the test suite. Agents need the same layers, but the tests must account for probabilistic responses, tool choices, and context-dependent decisions.

### What Role Does OpenInference Play?

OpenInference is useful because it gives agent evaluation a common trace format for prompts, retrieved documents, tool calls, model outputs, and control decisions. Without traces, an evaluation often sees only the final answer. With traces, ASSERT-style checks can ask sharper questions: did the agent retrieve the correct record, did it pass sensitive fields to a model, did a policy control block an unsafe action, and did the agent recover correctly?

## Which Frameworks and Providers Can Use ASSERT?

ASSERT is designed to be framework-independent, so it can evaluate agents built with LangGraph, CrewAI, OpenAI Agents SDK, DSPy, LlamaIndex, AutoGen, custom Python orchestration, hosted models, and callable application wrappers. The GitHub project emphasizes that it can test AI agents and LLM applications without forcing teams to standardize on one orchestration framework. LiteLLM's Microsoft ASSERT integration is also important because LiteLLM routes traffic across 100+ LLM providers, which means teams can introduce ASSERT while keeping their existing model gateway strategy. That matters in enterprise environments where one team may use LangGraph, another may run a custom service, and a platform team may centralize model access through a gateway. The takeaway: ASSERT is meant to sit beside your agent stack rather than replace it.

The cleanest integration point depends on your system shape. If your agent is a Python callable, wrap the callable and run tests directly. If your agent is a distributed service, run tests against a stable API and capture traces. If your team already uses LiteLLM, keep provider routing there and make ASSERT focus on behavioral verification. The goal is not to rebuild the agent around the evaluator; the goal is to give the evaluator enough control and evidence to make reliable judgments.

### How Should Teams Choose the First Integration Point?

Teams should choose the first integration point where they can run stable, repeatable tests with useful evidence. For a small prototype, that may be a direct Python function. For a production assistant, it is usually the same API path users hit, with test identities and controlled fixtures. Avoid starting at the deepest internal function if the real risk lives in orchestration, retrieval, or tool authorization.

## How Would You Convert a Refund or Data-Access Policy Into ASSERT Tests?

Converting a refund or data-access policy into ASSERT tests means breaking a written rule into expected behaviors, prohibited behaviors, edge cases, and evidence requirements. Take a refund policy: "The agent may issue refunds under $100 within 30 days for verified purchases, but must escalate higher-value refunds or fraud-risk cases." In ASSERT terms, that becomes positive scenarios for a $49 verified purchase on day 12, negative scenarios for a $250 refund attempt, edge cases for day 31, and trace checks that verify purchase lookup happened before the refund tool was called. For data access, the same pattern applies: authorized user, unauthorized user, ambiguous identity, stale session, and tool-call evidence. The takeaway: good agent evals turn each policy verb into an observable behavior or refusal.

Here is how I would draft the first slice before handing it to an evaluation framework:

| Policy rule | Positive test | Negative test | Trace evidence |
|---|---|---|---|
| Refunds under $100 are allowed within 30 days | Verified $49 order from 12 days ago is refunded | $49 order from 45 days ago is refused or escalated | Order lookup before refund call |
| Refunds over $100 require escalation | $250 refund creates escalation ticket | $250 refund is not directly issued | No direct refund tool call |
| Fraud-risk cases require human review | Risk flag creates review task | Agent does not reassure user refund is complete | Risk signal appears before response |
| User data requires ownership match | Owner gets invoice summary | Different user gets refusal | Ownership check before invoice retrieval |

### What Makes These Tests Better Than Prompt Spot Checks?

These tests are better than prompt spot checks because they define the expected system behavior and the evidence needed to prove it. A spot check might only ask, "Can I get a refund?" A useful eval asserts the purchase age, amount, risk flag, authenticated identity, allowed tool path, forbidden tool path, and final response. That gives you a regression test instead of a memory of a good demo.

## How Should ASSERT Run in CI and Regression Testing?

ASSERT should run in CI as a focused regression suite for high-risk agent policies, with slower or broader suites scheduled before release. In practice, I would not run every generated scenario on every commit; I would keep a small blocking suite for critical invariants, such as data isolation, payment authorization, legal disclaimers, and irreversible tool actions. The broader suite can run nightly, before model upgrades, before prompt changes, and before switching providers through a gateway such as LiteLLM. Databricks reported that companies using AI governance tools got over 12x more AI projects into production, which matches the engineering pattern: teams ship faster when the release gate is explicit. The takeaway: put ASSERT where regressions happen, especially around prompts, models, retrieval, tools, and policy controls.

A practical CI setup has three tiers. First, smoke tests run on pull requests and block merges when a critical policy fails. Second, full policy suites run on scheduled jobs and before releases. Third, exploratory generated tests run outside the blocking path, then promoted into the regression suite after review. That prevents the evaluator from becoming a noisy gate while still capturing new failure modes.

### What Should Fail the Build?

The build should fail on deterministic, high-impact policy violations: cross-tenant data exposure, unauthorized payment actions, missing human escalation, unsafe medical or legal claims, and tool calls that bypass required approval. Softer quality signals can warn without blocking at first. Once a warning has a clear threshold and stable judge behavior, promote it to a blocking check.

## What Should Developers Inspect in Traces, Tool Calls, and Failure Reports?

Developers should inspect traces, tool calls, retrieved context, policy-control decisions, judge explanations, and scorecard deltas when an ASSERT evaluation fails. The final answer is only one artifact; an agent can produce a compliant-looking response after making a dangerous intermediate call. Microsoft and ecosystem coverage both emphasize traceability because ASSERT can evaluate agents through recorded intermediate steps, especially when OpenTelemetry or OpenInference spans are available. In a data-access test, I want to see whether the identity check happened before retrieval, whether the retrieval query was scoped by tenant, whether the model saw sensitive fields, and whether a policy control blocked or allowed a tool call. Scorecards help show whether a fix improved the suite instead of only one case. The takeaway: evaluate the whole execution path, not just the text returned to the user.

The most useful failure report answers four questions: what requirement failed, what scenario triggered it, what evidence proves the failure, and what code or configuration layer likely owns the fix. A prompt patch may solve a refusal wording issue, but a tool authorization bug belongs in deterministic code. A retrieval leak belongs in query scoping or access control. A missing escalation may belong in orchestration logic or ACS controls.

## How Does ASSERT Compare With Promptfoo, LangSmith, OpenAI Evals, and Observability Tools?

ASSERT differs from Promptfoo, LangSmith, OpenAI Evals, and observability tools by centering the evaluation workflow on written requirements and agent policy compliance. Promptfoo is strong for prompt and model comparison, LangSmith is strong for LangChain and LangGraph tracing plus dataset-based evals, OpenAI Evals is useful for model and task evaluation in OpenAI-centered workflows, and observability platforms are essential for production monitoring. ASSERT's distinctive angle is taking natural-language behavior specifications and turning them into test scenarios, datasets, metrics, and scorecards for agents and LLM apps across frameworks. The OWASP Top 10 for Agentic Applications 2026 was developed with more than 100 experts, which shows how many risks are agent-workflow risks rather than plain text-generation risks. The takeaway: ASSERT complements existing eval and observability tools when policy traceability is the main job.

| Tool category | Primary strength | Where ASSERT is different |
|---|---|---|
| ASSERT | Requirement-driven agent policy evaluation | Starts from written intent and produces executable eval artifacts |
| Promptfoo | Prompt and provider comparison | Less focused on policy-to-test generation |
| LangSmith | Tracing, datasets, LangChain/LangGraph workflows | Strong observability, but tied closely to that ecosystem |
| OpenAI Evals | Custom model/task evals | Useful when the OpenAI stack is central |
| Observability platforms | Production traces and incident analysis | Detect live behavior; ASSERT can pre-test requirements |

### Should ASSERT Replace Existing Eval Tools?

ASSERT should not automatically replace existing eval tools. Use it where written policy needs to become executable tests. Keep the tools that already provide model comparison, tracing, dashboarding, or production incident workflows. The better architecture is usually layered: ASSERT for policy suites, existing eval tools for model and prompt experiments, and observability for live drift.

## What Are the Limitations and Human Review Requirements?

ASSERT has limitations because generated tests, judge-model scoring, and natural-language policies can all be incomplete or wrong. An evaluation framework can accelerate coverage, but it cannot decide your risk appetite, fix vague policy language, or prove the absence of failures. The June 2026 IBM survey summarized by ITPro found that only 11% of CIOs and CTOs felt fully prepared for large-scale AI deployment, and 77% said current governance frameworks were inadequate; that gap will not disappear just because a tool can generate tests. Human review is still required for policy interpretation, scenario quality, threshold setting, and post-failure remediation. Judge models can miss nuance, over-penalize acceptable behavior, or reward polished but unsafe answers. The takeaway: ASSERT is evaluation infrastructure, not a substitute for ownership.

The biggest mistake is treating generated tests as automatically authoritative. Review the tests the way you would review security rules or migration scripts. Make sure the policy is specific, the test fixtures represent real workflows, the judge criteria are inspectable, and the pass/fail threshold matches impact. Pair ASSERT with deterministic runtime controls for actions that must never rely on model judgment, such as authorization, payments, deletion, and regulated disclosures.

## What Implementation Checklist Should Production Agent Teams Follow?

A production team implementing ASSERT should start with a small set of critical policies, build reviewed test specs, connect the agent through a stable execution path, capture traces, define blocking thresholds, and run the suite repeatedly in CI and release workflows. Microsoft says its open-source Agent Governance Toolkit addresses all 10 OWASP agentic AI risks with deterministic, sub-millisecond policy enforcement, which is a useful reminder that evaluations and controls should work together. For ASSERT specifically, begin with the risks that would cause customer harm or force a rollback: data leakage, unauthorized tool use, unsafe advice, missed escalation, and broken audit trails. Then expand coverage as failures teach you what matters. The takeaway: start narrow, make the tests reliable, and turn every serious incident into a regression case.

Use this checklist as a practical starting point:

| Step | Developer action | Output |
|---|---|---|
| 1 | Pick 3 to 5 critical policies | A scoped eval backlog |
| 2 | Rewrite each policy as testable behavior | Clear specs with positive and negative cases |
| 3 | Add fixtures and test identities | Repeatable scenarios |
| 4 | Connect the agent execution path | Callable, API, or traced agent target |
| 5 | Capture OpenTelemetry or OpenInference traces | Evidence beyond final text |
| 6 | Define pass thresholds | Blocking and warning rules |
| 7 | Run in CI and before releases | Regression protection |
| 8 | Review failures with owners | Prompt, tool, retrieval, control, or policy fixes |

### What Should Be Tested First?

Test irreversible actions and confidentiality boundaries first. That usually means payment, refund, deletion, account changes, cross-tenant data access, regulated advice, and human escalation requirements. Do not start with tone or style unless your product risk is genuinely brand language. A polite unsafe agent is still unsafe.

## What Is the Bottom Line for Microsoft ASSERT?

Microsoft ASSERT is best treated as a way to make agent policies executable, reviewable, and repeatable across the software delivery lifecycle. Its strongest use case is not proving that an AI model is generally smart; it is proving that your agent follows your organization's specific requirements under realistic scenarios. The enterprise pressure is clear: a June 2026 IBM survey summary said organizations averaged 54 AI-related incidents in the prior year, with 17% classified as severe, while Forrester research summarized by ITPro said about 75% of enterprise leaders report adopting agentic AI but many remain stuck in pilot mode because of governance, orchestration, and trust gaps. ASSERT gives developers a concrete mechanism for closing part of that gap: turn written intent into tests, inspect failures, apply controls, and re-run the suite. The takeaway: treat agent policies as software contracts, not launch-document prose.

If you are already building agents, the next step is not to write a 40-page governance plan. Pick one policy that has real user impact, express it as observable behavior, generate and review test cases, run them against the actual agent path, and save the results as a regression suite. That is how evaluation becomes engineering practice.

## FAQ: Microsoft ASSERT Agent Evaluation Framework

Microsoft ASSERT FAQs usually come down to scope, integration, reliability, and whether the framework replaces existing tools. ASSERT is an open-source framework for requirement-driven AI agent evaluation, not a universal governance platform or a magic safety switch. It is most useful when a team already has written policies or product rules that need to become executable tests. In practice, developers use ASSERT-style workflows to verify refusal boundaries, tool-use requirements, escalation paths, data-access rules, and regression behavior after prompt, model, retrieval, or orchestration changes. The framework can fit several stacks, including LangGraph, CrewAI, OpenAI Agents SDK, LlamaIndex, AutoGen, LiteLLM-backed providers, hosted models, and custom Python callables. The takeaway: use ASSERT when you need policy compliance evidence that can be run repeatedly and inspected through artifacts.

### Is Microsoft ASSERT open source?

Microsoft ASSERT is open source, with its project available through the Responsible AI GitHub organization. The repository describes it as a requirement-driven evaluation harness for AI agents and LLM applications. As with any open-source infrastructure, check the current repository license, release notes, and issue activity before standardizing on it for production workflows.

### Does ASSERT only work with Microsoft Foundry?

ASSERT does not only work with Microsoft Foundry. Microsoft describes it as framework-agnostic, and the research material highlights support patterns across LangGraph, CrewAI, OpenAI Agents SDK, DSPy, LlamaIndex, AutoGen, hosted models, Python callables, and LiteLLM-routed providers. Foundry may be a natural home for Microsoft users, but the evaluation concept is broader.

### Can ASSERT evaluate tool-calling agents?

ASSERT can evaluate tool-calling agents when the execution path exposes enough evidence, especially through wrappers or traces. For tool-calling systems, the final answer is not enough. The useful checks verify whether the agent called the right tool, avoided forbidden tools, passed scoped parameters, handled errors correctly, and respected escalation or approval requirements.

### Should ASSERT tests be generated automatically?

ASSERT can help generate tests from written requirements, but the generated tests should be reviewed before they become release gates. Human review is needed to catch vague policies, unrealistic scenarios, weak judge criteria, and missing edge cases. Treat generated evals as a draft test suite, then promote reviewed cases into CI.

### What is the fastest useful way to start with ASSERT?

The fastest useful start is one high-risk policy with clear user impact. Choose a data-access, refund, payment, deletion, or escalation rule; write positive and negative scenarios; run them against the real agent path; inspect traces; and save failures as regression cases. Avoid starting with broad governance language that cannot produce measurable pass/fail behavior.
