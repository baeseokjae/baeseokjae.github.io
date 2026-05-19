---
title: "Archon AI Benchmark: Open-Source Harness Builder for Reproducible AI Coding"
date: 2026-05-19T18:04:15+00:00
tags: ["archon AI benchmark", "AI coding tools", "open source", "harness engineering", "LLM reproducibility"]
description: "Archon is the open-source YAML workflow harness that lifts AI coding PR acceptance from 6.7% to 70% — a 10x improvement with the same LLM."
draft: false
cover:
  image: "/images/archon-ai-benchmark-tool-2026.png"
  alt: "Archon AI Benchmark: Open-Source Harness Builder for Reproducible AI Coding"
  relative: false
schema: "schema-archon-ai-benchmark-tool-2026"
---

Archon is an open-source AI coding harness builder that wraps LLMs like Claude Code and OpenAI Codex inside deterministic YAML workflows, lifting the PR acceptance rate from a raw 6.7% to nearly 70% — without changing the underlying model. If you've ever wondered why AI-generated code works brilliantly one day and catastrophically fails the next, the answer is the absence of structure. Archon provides that structure.

## What Is Archon? The First Open-Source AI Coding Harness Builder

Archon is an open-source framework that converts ad-hoc AI coding sessions into reproducible, version-controlled workflows by wrapping LLM calls in a directed acyclic graph (DAG) of YAML-defined steps. Released by Cole Medin in early 2026 and rewritten entirely in TypeScript in April 2026, Archon reached 21,600+ GitHub stars — briefly trending #1 on GitHub — because it addresses a problem every developer using AI coding tools encounters immediately: the same prompt produces wildly different results across runs. Instead of accepting that variance as inevitable, Archon treats the workflow itself as a first-class engineering artifact. A `.archon/workflows/` directory in your repository holds YAML files that define exactly how the AI plans, implements, tests, reviews, and submits a change. These workflow files are reviewed in pull requests alongside the code they generate. The analogy to Dockerfiles for infrastructure is deliberate: Archon is what Dockerfiles did for reproducible environments, applied to AI-generated code.

## The Reproducibility Crisis That Archon Was Built to Solve

The reproducibility crisis in AI-generated code is measurably severe, documented in a peer-reviewed arXiv study (2512.22387, March 2026) covering 300 LLM-generated projects across multiple languages. That study found 31.7% of AI-generated code projects fail to execute out of the box due to dependency gaps alone. Python fares best at 89.2% reproducibility success, while Java collapses to just 44.0%. The root cause is not model capability — it is structural: LLMs declare dependencies in code but the actual runtime dependency graph expands by an average of 13.5x from declared to actual. One `import requests` in a requirements file can silently require 14 transitive packages that differ between developer laptops, CI runners, and production. Without a harness that enforces environment setup, dependency pinning, test execution, and review gates, even a correct implementation fails on the second run on a different machine. The research makes the problem concrete: AI-generated code is not inherently unreliable, but AI coding *workflows* — or the absence of them — are. Archon's core thesis is that you cannot benchmark or rely on AI coding output until you first standardize how the output is produced.

## How Archon Works: YAML Workflows as Deterministic AI Pipelines

An Archon workflow is a YAML file that defines a DAG of nodes, each corresponding to a step in the AI coding process. A minimal workflow file looks like this:

```yaml
name: feature-implementation
version: 1
nodes:
  plan:
    type: plan
    prompt: "Analyze the issue and write a step-by-step implementation plan"
    model: claude-sonnet-4-6
  implement:
    type: implement
    depends_on: [plan]
    prompt: "Implement the plan from the previous step"
  test:
    type: test
    depends_on: [implement]
    runner: bun test
  review:
    type: review
    depends_on: [test]
    prompt: "Check the implementation against the original requirements"
  pr:
    type: pull-request
    depends_on: [review]
    title_template: "feat: {{issue.title}}"
```

Archon ships with 17 default workflows covering the full lifecycle: planning, implementation, testing, review, and PR creation. Each node type has documented retry logic and fallback behavior. When a `test` node fails, Archon can re-enter the `implement` node with the error output as additional context rather than surfacing a raw failure to the user. The workflow engine runs in a TypeScript/Bun runtime, executes nodes in parallel where the DAG allows, and reports status through a real-time dashboard. The YAML syntax is explicit about which model runs at each step — you can use Claude for planning, GPT-4 for implementation, and a local Ollama model for review, mixing providers per node.

## Key Features: DAG Architecture, Multi-Model Support, and Error Recovery

Archon's architecture centers on four capabilities that distinguish it from running LLMs directly. First, the DAG execution engine ensures steps run in dependency order and parallelizes independent nodes automatically — a `test` and a `docs` node that both depend on `implement` will run concurrently without any configuration. Second, multi-model support lets teams assign the cheapest adequate model to each step: a weak model for boilerplate test scaffolding, a powerful model for architecture planning. Supported providers include Anthropic Claude (all tiers), OpenAI GPT-4 and Codex, and any model served via Ollama locally. Third, structured error recovery replaces "it failed, retry from scratch" with targeted re-entry: when a node fails, Archon passes the failure details back to the relevant upstream node as context, enabling the LLM to self-correct within the same workflow run. Fourth, the `.archon/workflows/` directory makes workflows version-controlled artifacts. Teams can review changes to a workflow definition in a pull request, roll back a workflow to a previous version, and audit exactly which workflow version produced a given merged PR.

### Model Flexibility in Practice

The multi-model routing in Archon is more nuanced than a single model selection at setup. Each node in a workflow YAML specifies a `model` field, and that field accepts any model string Archon understands. A team running cost-sensitive CI pipelines might assign `haiku-4-5` to the `test` node (where the prompt is formulaic) and `claude-opus-4-7` only to the `review` node (where reasoning quality matters most). Because the model choice is in the YAML file, changing the model for one step of one workflow is a one-line diff — it shows up in code review, gets recorded in git history, and can be reverted if the cheaper model introduces regressions.

## Real-World Results — From 6.7% to 70% PR Acceptance Rate

The most striking data point in Archon's launch story is not a benchmark score — it is a production outcome: the same LLM, given the same coding task, achieves a 6.7% PR acceptance rate without a structured harness and nearly 70% PR acceptance with Archon wrapping the workflow. That is roughly a 10x improvement from workflow structure alone, with no change to the underlying model or prompts. The explanation is not that Archon makes the LLM smarter. It is that the harness eliminates the modes of failure that account for the gap: generated code that was never tested, code that passed tests locally but failed in CI due to missing dependencies, code that addressed the wrong interpretation of a requirement because no planning step forced clarification, and code submitted as a PR without a review step catching obvious regressions. Stripe provides the enterprise-scale reference: their internal harness architecture, called Minions, merges over 1,300 pull requests per week that contain zero human-written code. Archon is positioned as the open-source path to the same outcome — a repeatable, auditable AI coding pipeline that teams without Stripe's engineering resources can adopt today.

## Archon vs. Traditional Benchmarks: Why a Harness Is Different

Traditional AI coding benchmarks like SWE-bench, HumanEval, and LiveCodeBench measure model capability by presenting a model with a task and scoring the output against a reference solution. They are model-centric: the question is "which model is best?" Archon is workflow-centric: the question is "given a fixed model, how do we maximize the reliability of real-world code delivery?" This is a categorical distinction. SWE-bench tells you that Model A solves 42% of GitHub issues in its test set. Archon tells you that your team's chosen model, wrapped in a structured plan-implement-test-review-PR pipeline, will deliver merge-ready code at a predictable rate. SWE-bench is useful for model selection; Archon is useful for production engineering. They answer different questions. The framing of Archon as a "benchmark tool" in early coverage is slightly misleading — it is better understood as a harness builder that makes AI coding results reproducible and measurable. The measurability is a side effect of the structure, not the primary goal. Because every Archon run executes the same workflow definition and logs the same structured output, you can compare workflow versions, model assignments, and task types in a way that raw LLM usage never permits.

## Getting Started with Archon: Installation and First Workflow

Archon runs on the TypeScript/Bun runtime. The install sequence is four commands:

```bash
# Install Bun if not already installed
curl -fsSL https://bun.sh/install | bash

# Clone and install Archon
git clone https://github.com/coleam00/Archon
cd Archon
bun install
```

Set your model provider API keys as environment variables:

```bash
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here  # optional
```

Start the Archon dashboard:

```bash
bun run dev
```

The dashboard runs at `localhost:3000` and shows active workflow runs, node execution status, and output logs in real time. To run a workflow against a task, pass the issue description and the workflow name:

```bash
bunx archon run --workflow feature-implementation --issue "Add rate limiting to the /api/upload endpoint"
```

Archon will execute the DAG, stream progress to the dashboard, and — if the workflow includes a `pull-request` node — submit a PR to the configured repository when the review step passes. The 17 default workflows in `.archon/workflows/defaults/` are a working starting point for most teams. Customizing them is a YAML edit, not a code change.

### Connecting to Your Repository

Archon integrates with GitHub via a personal access token or GitHub App. Configure the repository target in `archon.config.ts` at the project root:

```typescript
export default {
  repository: "your-org/your-repo",
  baseBranch: "main",
  github: {
    token: process.env.GITHUB_TOKEN,
  },
};
```

From that point, every workflow run that reaches the `pull-request` node will open a real PR against your repository. The PR description includes a structured summary of the plan, a list of files changed, and a link to the Archon workflow run log — giving reviewers full context on what the AI did and why.

## Who Should Use Archon (And Who Should Not)

Archon is the right tool for teams that are already using AI coding tools at scale and have hit the reliability ceiling of ad-hoc prompting. If your team is consistently seeing AI-generated PRs fail CI, require extensive human rework, or produce code that works locally but not in other environments, Archon addresses exactly those failure modes. It is also the right tool for teams building internal AI coding pipelines who want to avoid vendor lock-in to proprietary agent platforms — Archon workflows are plain YAML files in your repository, owned entirely by your team. Archon is a poor fit for teams still evaluating whether AI coding tools are useful at all. The harness adds real setup cost: you need to author or adapt workflow YAML files, configure model credentials, and integrate with your CI/CD system. That investment only pays back at scale. Similarly, Archon is overkill for one-off code generation tasks. If you need to ask Claude to write a single utility function, open the chat interface. Archon's value is in the 50th through 500th task, where workflow structure compounds into a measurably higher merge rate.

---

## FAQ

**What is Archon used for in AI coding?**
Archon is used to wrap AI coding agents like Claude Code and OpenAI Codex inside structured YAML workflow definitions, ensuring that every code generation task follows a repeatable plan-implement-test-review pipeline rather than a single unconstrained LLM call.

**How does Archon improve PR acceptance rates?**
Archon improves PR acceptance by enforcing structured workflow gates — planning, implementation, testing, and review — before a PR is submitted. The same LLM without a harness achieves 6.7% PR acceptance; wrapped in an Archon workflow, acceptance jumps to nearly 70%.

**Is Archon a benchmark tool or a workflow engine?**
Archon is primarily a workflow engine and harness builder. It is called a benchmark tool because its structured logging makes AI coding results measurable and comparable across workflow versions, but the primary purpose is making AI code generation reproducible and reliable in production.

**What models does Archon support?**
Archon supports Anthropic Claude (all tiers), OpenAI GPT-4 and Codex variants, and any model served locally via Ollama. Different nodes within a single workflow can use different models, allowing cost and capability optimization per step.

**How do I version-control Archon workflows?**
Archon workflows are YAML files stored in the `.archon/workflows/` directory of your repository. They are committed and reviewed in pull requests like any other code artifact, giving teams full git history, rollback capability, and code review for workflow changes.
