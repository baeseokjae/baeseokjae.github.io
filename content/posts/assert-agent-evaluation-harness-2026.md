---
title: "ASSERT Agent Evaluation Harness 2026 Review: Requirement-Driven Testing for AI Agents"
date: 2026-07-17T13:06:50+00:00
tags:
  - AI Agent Evaluation
  - ASSERT Framework
  - Microsoft Open Trust Stack
  - Agent Testing
  - LLM Evaluation
  - AI Governance
description: "ASSERT is Microsoft's open-source, requirement-driven evaluation harness that turns agent policies into executable tests across any framework."
draft: false
cover:
  image: "/images/assert-agent-evaluation-harness-2026.png"
  alt: "ASSERT Agent Evaluation Harness 2026 Review: Requirement-Driven Testing for AI Agents"
  relative: false
schema: "schema-assert-agent-evaluation-harness-2026"
---

ASSERT (Adaptive Spec-driven Scoring for Evaluation and Regression Testing) is an open-source, requirement-driven evaluation harness for AI agents and LLM applications, announced at Microsoft Build 2026. Built by Microsoft's Responsible AI organization and released under the MIT license, ASSERT transforms natural-language agent policies into executable test suites through a four-stage pipeline — systematize, test set, inference, and judge — making it the first framework to bridge the gap between product requirements and automated test coverage for AI agents.

## What Is ASSERT? — Adaptive Spec-driven Scoring for Evaluation and Regression Testing

ASSERT is a Python-based evaluation framework (compatible with Python 3.11 through 3.13) that lets development teams define what their AI agents should and should not do in natural language, then automatically generates test scenarios and scores agent behavior against those requirements. Unlike traditional LLM benchmarks such as MMLU or HumanEval that test general knowledge, ASSERT evaluates agents against your specific policies — the rules, constraints, and behavioral expectations that define acceptable agent behavior in your particular use case.

The project was created on April 30, 2026, and as of July 17, 2026, has accumulated 196 stars and 27 forks on GitHub. It is built on the research methodology described in Agarwal et al. (2026) "AI-Assisted Systematization for Evaluating GenAI Systems," published by Microsoft Research. The framework is framework-agnostic, supporting major agent orchestration tools including LangChain, CrewAI, OpenAI Agents SDK, DSPy, LlamaIndex, and AutoGen, and connects to over 100 model endpoints through its LiteLLM integration.

## The Open Trust Stack: ASSERT, ACS, and OpenInference

ASSERT does not exist in isolation. It is one component of Microsoft's broader **Open Trust Stack**, a coordinated set of open-source tools announced at Build 2026 that together provide end-to-end governance for AI agents. The stack consists of three complementary layers:

| Component | Role | Stage |
|-----------|------|-------|
| **ASSERT** | Pre-deployment evaluation | Before release |
| **ACS (Agent Control Specification)** | Runtime safety enforcement | During execution |
| **OpenInference** | Observability and trace capture | Throughout lifecycle |

ASSERT evaluates whether an agent meets policy requirements before it reaches production. ACS, the Agent Control Specification, defines eight control points in the agent lifecycle — from tool invocation to memory access — where runtime policies can be enforced deterministically. OpenInference, built on the OpenTelemetry standard, provides the observability layer that both ASSERT and ACS rely on for trace-grounded decision-making. Together, they form a complete governance loop: evaluate with ASSERT, deploy with ACS controls, monitor with OpenInference, and re-evaluate when policies change.

## How ASSERT Works: The 4-Stage Pipeline

ASSERT's architecture is organized around four distinct pipeline stages, each producing artifacts that can be cached and reused independently. This design makes the framework practical for CI/CD integration, where changing only the inference target (e.g., testing a new model version) reuses the systematization and test set stages without recomputation.

### Stage 1 — Systematize: From Policy to Taxonomy

The systematize stage takes natural-language policy documents — your agent's behavioral requirements, safety rules, and domain constraints — and produces a structured taxonomy of evaluation dimensions. This is where the "AI-assisted systematization" research methodology comes into play: instead of manually enumerating every possible test scenario, ASSERT uses an LLM to help decompose high-level policies into granular, testable dimensions. The output is a JSON taxonomy file that defines what aspects of agent behavior need to be measured.

### Stage 2 — Test Set: Generating Scenarios

Using the taxonomy from Stage 1, the test set stage generates concrete test scenarios. Each scenario is a structured prompt or instruction that exercises a specific policy dimension. For example, if your policy states "the agent must not execute financial transactions without explicit user confirmation," the test set stage generates scenarios where the agent is asked to perform financial actions under varying levels of user consent. These scenarios are stored as JSONL artifacts, making them inspectable, version-controllable, and reusable across evaluation runs.

### Stage 3 — Inference: Running the Agent

The inference stage executes the agent against each test scenario from Stage 2. ASSERT is framework-agnostic at this stage — it provides a standardized interface that wraps any supported agent framework. The agent's responses, tool calls, reasoning traces, and intermediate steps are all captured. Crucially, ASSERT integrates with OpenInference to capture OpenTelemetry traces during execution, providing a complete record of the agent's decision-making process for later judgment.

### Stage 4 — Judge: Scoring with LLM Verdicts

The judge stage evaluates the agent's performance against the original policy requirements. Unlike simple pass/fail checks, ASSERT uses LLM-based judges that examine the full trace — including intermediate reasoning, tool calls, and final outputs — to determine whether the agent complied with each policy dimension. The judgment is grounded in the actual execution trace captured via OpenTelemetry, which distinguishes ASSERT from black-box evaluation tools that only see final outputs. Results are scored and stored as local JSON artifacts, and the bundled local viewer enables side-by-side comparison of different runs.

## Key Features and Differentiators

### Spec-Driven Coverage vs Generic Benchmarks

The most significant differentiator of ASSERT is its requirement-driven approach. Traditional LLM benchmarks measure general capabilities — how well does the model answer factual questions, solve coding problems, or reason about common-sense scenarios. ASSERT measures compliance with your specific policies. This shift from generic capability testing to requirement-driven evaluation is critical for production AI agents, where the question is not "is this agent smart?" but "does this agent behave correctly in my specific domain?"

### Framework-Agnostic Architecture

ASSERT does not lock you into a specific agent framework or cloud provider. It supports LangChain, CrewAI, OpenAI Agents SDK, DSPy, LlamaIndex, and AutoGen out of the box, and its modular architecture makes it straightforward to add support for additional frameworks. This framework-agnostic design is a deliberate choice — Microsoft has positioned ASSERT as an industry-wide tool, not a vendor lock-in play. As confirmed by community analysis, ASSERT is not tied to Azure or Microsoft Foundry.

### Trace-Grounded Judgment via OpenTelemetry

ASSERT's integration with OpenInference and OpenTelemetry enables trace-grounded judgment. Instead of evaluating only the final output of an agent, ASSERT examines the full execution trace — every tool call, every reasoning step, every intermediate decision. This is particularly important for multi-step agent tasks where the final answer may be correct but the path taken to reach it violates policy. OpenInference auto-instruments over 33 agent frameworks in just two lines of code, making trace capture nearly effortless.

### Local-First Artifacts and Viewer

All ASSERT artifacts — taxonomies, test scenarios, inference outputs, and judgment scores — are stored as local JSON and JSONL files. This local-first approach means teams can version-control their evaluation artifacts, reproduce results, and audit the evaluation process without depending on external services. The bundled local viewer provides a web-based interface for comparing runs side by side, making it easy to track regressions across agent versions.

## ASSERT vs Alternatives: Vally, MSBench, Bloom, Petri

The AI agent evaluation landscape includes several other tools, each with different strengths. Here is how ASSERT compares:

| Tool | Approach | Best For | Key Limitation |
|------|----------|----------|----------------|
| **ASSERT** | Requirement-driven, 4-stage pipeline | Policy compliance testing, CI integration | Newer ecosystem, smaller community |
| **Vally** | Local-first, deterministic graders | Fast iteration, reproducible scoring | Less suited for complex multi-step scenarios |
| **MSBench** | At-scale regression testing | Large-scale model regression suites | Requires Microsoft infrastructure |
| **Bloom** | Behavioral simulation | Testing edge cases and adversarial inputs | Less structured policy mapping |
| **Petri** | Petri-net based workflow testing | Complex multi-agent orchestration | Steeper learning curve |

ASSERT fills a unique niche: it is the only framework that starts from natural-language policies and automatically generates a structured test suite. Vally excels at fast, deterministic scoring but lacks ASSERT's scenario generation capability. MSBench is designed for large-scale regression but is more tightly coupled to Microsoft's ecosystem. For teams that need to translate product requirements into test coverage without writing hundreds of manual test cases, ASSERT offers the most direct path.

## Ecosystem and Partner Integrations

ASSERT launched with a broad set of ecosystem partners, reflecting Microsoft's strategy of building an open industry standard rather than a proprietary tool. Launch partners include:

- **CrewAI** — Multi-agent orchestration framework
- **Arize AI** — ML observability and monitoring
- **LiteLLM** — Unified model endpoint interface (100+ models)
- **Pipecat** — Voice agent framework
- **Pydantic** — Data validation and schema management
- **HoneyHive** — LLM evaluation and tracing

The integration with LiteLLM is particularly important — it means ASSERT can evaluate agents running on any of 100+ model endpoints without custom adapter code. The OpenInference integration, which auto-instruments 33+ agent frameworks, ensures that trace capture works across the entire agent ecosystem with minimal configuration.

## Getting Started with ASSERT

To start using ASSERT, install the package via pip:

```bash
pip install assert-ai
```

The package requires Python 3.11 or later. The basic workflow involves:

1. **Define your policies** — Write natural-language policy documents describing what your agent should and should not do.
2. **Run the systematize stage** — `assert systematize --policies policies.md` to generate a taxonomy.
3. **Generate test scenarios** — `assert test-set --taxonomy taxonomy.json` to produce test cases.
4. **Run inference** — `assert infer --test-set scenarios.jsonl --agent your-agent-config.yaml` to execute tests.
5. **Judge results** — `assert judge --inference-results results.jsonl --taxonomy taxonomy.json` to score performance.
6. **View results** — Launch the local viewer with `assert view` to compare runs.

The artifact caching system means that if you only change the agent configuration (e.g., switching from GPT-4 to Claude 4), stages 1 and 2 are skipped automatically, and only inference and judgment are re-executed.

## Limitations and Considerations

While ASSERT represents a significant advance in agent evaluation, it has several limitations worth considering:

**New and rapidly evolving.** The project was created in April 2026 and is still in its early stages. With 196 stars and 27 forks, the community is small compared to established tools. Teams adopting ASSERT should expect API changes and should pin their version.

**LLM-dependent systematization.** The AI-assisted systematization stage relies on an LLM to decompose policies into taxonomies. This introduces a meta-evaluation question: how do you verify that the systematization itself is correct? The quality of your test suite depends on the quality of the LLM used in Stage 1.

**No built-in runtime enforcement.** ASSERT is an evaluation tool, not a runtime guard. It tells you whether your agent passes policy checks, but it cannot prevent policy violations during live operation. This is where ACS (Agent Control Specification) fills the gap — but ACS is a separate tool that requires its own integration.

**Trace dependency.** The trace-grounded judgment feature depends on OpenInference and OpenTelemetry instrumentation. If your agent framework is not among the 33+ auto-instrumented frameworks, or if you disable tracing for performance reasons, the judge stage loses visibility into intermediate steps.

## Conclusion: Is ASSERT Ready for Production?

ASSERT is ready for teams that are building production AI agents and need a structured, repeatable way to verify policy compliance. The framework's requirement-driven approach addresses a genuine gap in the AI agent development lifecycle — the disconnect between product requirements and test coverage. The 4-stage pipeline with artifact caching is well-designed for CI/CD integration, and the framework-agnostic architecture means it can be adopted incrementally alongside existing tools.

For teams already using LangChain, CrewAI, or OpenAI Agents SDK, ASSERT provides immediate value as a policy compliance layer. The combination of ASSERT for pre-deployment evaluation and ACS for runtime enforcement creates a governance loop that is currently unmatched in the open-source ecosystem. However, teams should be prepared for the framework's early-stage maturity — expect API changes, contribute feedback, and pin versions in production pipelines.

ASSERT is not a replacement for general capability benchmarks or for runtime monitoring tools. But as a requirement-driven evaluation harness that turns natural-language policies into executable tests, it fills a critical role that no other open-source tool currently addresses. For AI engineering teams that take agent governance seriously, ASSERT deserves a place in the evaluation stack.

## Frequently Asked Questions

**What is ASSERT in the context of AI agent evaluation?**
ASSERT (Adaptive Spec-driven Scoring for Evaluation and Regression Testing) is an open-source framework by Microsoft that converts natural-language agent policies into executable test suites through a four-stage pipeline: systematize, test set, inference, and judge.

**How does ASSERT differ from traditional LLM benchmarks like MMLU?**
Traditional benchmarks measure general knowledge and reasoning capabilities, while ASSERT evaluates agents against your specific policies and requirements. It tests whether an agent behaves correctly in your domain, not whether it answers general knowledge questions correctly.

**Is ASSERT tied to Microsoft Azure or Microsoft Foundry?**
No. ASSERT is framework-agnostic and not tied to any cloud provider. It supports multiple agent frameworks including LangChain, CrewAI, OpenAI Agents SDK, DSPy, LlamaIndex, and AutoGen, and works with over 100 model endpoints through LiteLLM.

**What is the relationship between ASSERT and ACS?**
ASSERT handles pre-deployment evaluation — checking whether an agent meets policy requirements before release. ACS (Agent Control Specification) handles runtime enforcement — preventing policy violations during live operation. Together they form a complete governance loop.

**How do I get started with ASSERT?**
Install the package with `pip install assert-ai` (requires Python 3.11+), define your policies in natural language, then run the four pipeline stages: systematize, test-set, infer, and judge. Results are stored as local JSON artifacts viewable with the bundled local viewer.
