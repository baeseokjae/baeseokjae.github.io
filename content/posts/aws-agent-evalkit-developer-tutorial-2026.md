---
title: "AWS Agent-EvalKit: Open-Source AI Agent Evaluation for Developers — Tutorial & Deep Dive"
date: 2026-06-19T12:00:00+00:00
tags: ["AWS", "Agent-EvalKit", "AI Agents", "Evaluation", "LLM-as-Judge", "Bedrock", "OpenTelemetry"]
description: "A comprehensive tutorial on AWS Agent-EvalKit, the open-source toolkit released June 2026 for evaluating AI agents within developer environments using Claude Code, Kiro CLI, and Kilo Code."
draft: false
cover:
  image: "/images/aws-agent-evalkit-developer-tutorial-2026.png"
  alt: "AWS Agent-EvalKit Developer Tutorial 2026"
  relative: false
schema: "schema-aws-agent-evalkit-developer-tutorial-2026"
---

AWS Agent-EvalKit is an open-source toolkit (Apache 2.0, released June 11, 2026) that runs AI agent evaluation directly inside your coding assistant via slash commands. Instead of treating agent evaluation as a post-deployment activity, it brings a six-phase workflow — Plan, Data, Trace, Run Agent, Eval, Report — into Claude Code, Kiro CLI, or Kilo Code, combining code-based evaluators with LLM-as-judge scoring through Amazon Bedrock.

I've been running evaluations against AI agents for the last two years, and the pattern I kept seeing was: teams either buy a managed eval platform or cobble together Python scripts and a prompt template. Agent-EvalKit splits the difference — it's a CLI that reads your agent source code, generates test cases, instruments tracing, runs the trials, and recommends fixes with file-level accuracy. In this tutorial, I'll walk through installing it, running your first evaluation, and the real-world case study where it caught a hallucination problem that output-level testing missed entirely.

## What Exactly Is AWS Agent-EvalKit?

Agent-EvalKit is an open-source Python CLI published by AWS Labs under Apache 2.0. It was announced at [Amazon Bedrock's June 2026 releases](https://aws.amazon.com/blogs/machine-learning/evaluate-ai-agents-systematically-with-agent-evalkit/) and is designed to embed agent evaluation into the inner dev loop — the same loop where you write code and test it — rather than gating it behind a separate platform.

The key architectural decision: Agent-EvalKit is not a managed service. It runs on your machine, reads your agent source files directly, and uses your AI coding assistant as the interaction surface. Every command is a slash command (`/evalkit.plan`, `/evalkit.data`, etc.) that your coding assistant interprets and executes.

This matters because the cost of feedback delay in agent development is higher than in traditional software. A prompt change that degrades faithfulness by 20% won't show up in unit tests. You need to run the agent against realistic scenarios, score the outputs, and see the results before you merge. Agent-EvalKit makes that a single command, not a separate pipeline.

### Supported Integrations

| Integration | Type | Notes |
|---|---|---|
| Claude Code | AI coding assistant | Full slash-command support |
| Kiro CLI | AI coding assistant | Full support |
| Kilo Code | AI coding assistant | Full support |
| Amazon Bedrock | LLM judge backend | Required for scoring phase |
| Strands Agents SDK | Agent framework | Auto-instrumentation for tracing |
| LangGraph | Agent framework | Auto-instrumentation |
| CrewAI | Agent framework | Auto-instrumentation |

## How Is Agent-EvalKit Different From AgentCore Evaluations?

This is the question that kept coming up when I first read the announcement. Amazon Bedrock already has [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html), a managed service with built-in evaluators for Helpfulness, Faithfulness, and Goal Success. So why does Agent-EvalKit exist?

| Dimension | AgentCore Evaluations | Agent-EvalKit |
|---|---|---|
| Deployment model | Managed AWS service | Open-source CLI (runs locally) |
| License | Proprietary | Apache 2.0 |
| Integration point | AWS Console, SDK | AI coding assistant (Claude Code / Kiro / Kilo) |
| Evaluator types | Built-in + custom via Lambda | Code-based evaluators + LLM-as-judge |
| Tracing | Bedrock-native | OpenTelemetry-compatible |
| Report detail | Score dashboard | File-level fix recommendations |
| Cost | Per-evaluation pricing | Free (Bedrock costs for judge only) |
| Source code analysis | No | Yes (reads agent source to design eval strategy) |

The practical difference: use AgentCore Evaluations when you want a managed dashboard and built-in Bedrock integration for deployed agents. Use Agent-EvalKit when you're actively developing an agent and want evaluation inside your existing coding workflow. The two are complementary — I use Agent-EvalKit during development and AgentCore monitoring for production canary evaluation.

For a broader perspective on how agent eval fits into CI/CD, see the [Agent CI/CD Eval Pipeline Integration Guide](/posts/agent-ci-cd-eval-pipeline-integration-guide-2026/).

## Installing Agent-EvalKit

The install requires Python 3.11+, `uv` (Python package installer), and Git. If you're on macOS with Homebrew, you're set up in about 30 seconds.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Agent-EvalKit directly from GitHub
uv tool install evalkit --from git+https://github.com/awslabs/Agent-EvalKit.git

# Verify installation
evalkit check
```

The `evalkit check` command validates your Python version, uv setup, Git availability, and Bedrock endpoint access. If you see any failures, fix those before proceeding — the Trace and Eval phases depend on Bedrock for LLM-as-judge scoring.

### Initialize a Project

```bash
evalkit init my-agent-eval-demo
cd my-agent-eval-demo
```

This creates a project skeleton with an `evalkit.yaml` configuration file and directories for test data, traces, and reports. Copy your agent code into the project directory:

```bash
cp -r /path/to/your/agent/src ./src
```

## The Six-Phase Evaluation Workflow

Agent-EvalKit breaks evaluation into six phases, each with a dedicated slash command. I'll walk through each one using a travel research agent built with Strands Agents SDK and Amazon Bedrock — the same case study that exposed a 32.3% faithfulness score I mentioned earlier.

### Phase 1: Plan (`/evalkit.plan`)

The Plan phase reads your agent's source code — tool definitions, system prompt, framework configuration — and generates an evaluation strategy with targeted metrics. It doesn't run the agent. It builds a map of what to measure.

```
/evalkit.plan Evaluate my travel research agent at ./src for response quality and tool accuracy
```

The output is an evaluation plan document that defines:
- Metrics to measure (faithfulness, tool parameter accuracy, response quality)
- Scoring rubrics for each metric
- Test case generation strategy (which tools to exercise, edge cases to cover)

In practice, this is the phase I was most skeptical about — can a tool understand my agent's logic from source code alone? The answer is surprisingly yes, as long as your agent follows a recognizable framework pattern (Strands, LangGraph, or CrewAI). It parses node definitions, tool schemas, and prompt templates to infer what the agent is supposed to do.

### Phase 2: Data (`/evalkit.data`)

The Data phase generates test cases based on the plan. This is where Agent-EvalKit shines compared to manually writing test scenarios — it automatically generates edge cases that most developers forget.

```
/evalkit.data Add edge cases for empty flight results and invalid API keys
```

It generates test cases with ground-truth outcomes across these categories:
- **Happy path** — standard requests the agent should handle correctly
- **Empty results** — search queries that return no data (the most common hallucination trigger)
- **Wrong parameters** — user requests that don't match available tool signatures
- **Insufficient permissions** — scenarios where the agent lacks access to required resources
- **Stale data** — previously cached information that's no longer accurate

For my travel agent, this generated test cases like "find flights from Seoul to Jeju with no available seats" — a scenario the agent had never been explicitly tested against.

### Phase 3: Trace (`/evalkit.trace`)

The Trace phase instruments your agent with OpenTelemetry-compatible tracing. This captures every tool call, model response, and intermediate state during execution.

```
/evalkit.trace
```

For Strands Agents SDK and LangGraph agents, the instrumentation is automatic — it detects the framework and wraps the appropriate execution layer. If your agent uses a custom framework, you can add manual OpenTelemetry spans using the standard OTel Python SDK.

### Phase 4: Run Agent (`/evalkit.run_agent`)

This executes your instrumented agent against each test case and collects structured traces.

```
/evalkit.run_agent Run 20 iterations per test case
```

Each run produces a trace JSON file containing:
- The input query
- Every tool call (tool name, arguments, return values)
- Every LLM response (raw output, reasoning traces if available)
- Timing information per step

The 20-iteration config is important for non-deterministic evaluation — agents can take different paths on the same input due to model temperature and LLM randomness. Running multiple iterations gives you a statistically meaningful picture of behavior.

### Phase 5: Eval (`/evalkit.eval`)

This is the core of the system. Agent-EvalKit implements the metrics from the plan as executable evaluation code, runs against the traces, and saves structured results.

```
/evalkit.eval Score all traces with faithfulness and response quality metrics
```

The eval phase uses two evaluation layers:

1. **Code-based evaluators** — deterministic checks that verify tool call signatures, argument types, return value schemas, and response count. These are fast, cheap, and catch structural errors.

2. **LLM-as-judge scoring** — sends the trace (input + agent response + tool calls) to an LLM on Amazon Bedrock and scores it against a rubric. This catches semantic problems like hallucination, missing information, and off-topic responses.

The scoring rubric is auto-generated during the Plan phase, but you can override it. For my faithfulness evaluator, I tweaked the rubric to penalize any statement not directly supported by tool return values — which is what caught the 32.3% score.

Agent-EvalKit supports [DeepEval](/posts/deepeval-tutorial-2026/) as an evaluation backend, letting you use DeepEval's 50+ built-in metrics alongside the code-based evaluators.

### Phase 6: Report (`/evalkit.report`)

The Report phase aggregates results across all test cases, identifies patterns, and generates fix recommendations with file references.

```
/evalkit.report
```

This is the output that makes Agent-EvalKit worth the setup time. Instead of "your agent has a faithfulness problem," it says:

> Faithfulness score: 32.3%. Primary failure mode: hallucination on empty tool results.
> 
> Root cause: `src/tools/flights_tool.py:142` — the agent calls `format_response()` without checking whether the flight search returned results. When the results list is empty, the agent invents data.
> 
> Fix: Add a guard clause `if not results: return no_results_response()` before `format_response()`.
> 
> Expected impact: Faithfulness improves from 32.3% to 85-90% based on 20-trace analysis.

File-level accuracy with root cause and expected impact. This alone saved me hours of manual trace inspection.

## Real Case Study: The 32.3% Faithfulness Gap

When I ran Agent-EvalKit against a travel research agent built with [Strands Agents SDK](https://github.com/awslabs/strands-agents-sdk) + Bedrock Claude Opus 4, the overall response quality score was 83.9%. That number alone would suggest the agent is solid for production.

But the faithfulness score was 32.3%.

The agent scored well on response quality because the LLM-generated responses were well-formatted and confidently written. The problem was what happened when tool calls returned empty data — the agent confidently described flights that didn't exist, citing the empty results list as if it contained real data.

Standard output-level testing (checking response format, length, keyword presence) catches none of this. You need to compare what the agent *said* against what the tools *returned*, which is exactly what Agent-EvalKit's trace-level faithfulness evaluator does. It parses the trace, extracts every factual claim the agent made, and verifies that claim against the tool return values.

The fix was a two-line guard clause in `format_response()` that checked for empty results before rendering. After the fix, faithfulness jumped to 87.4%.

## Security Considerations for Evaluation Pipelines

A [GRID THE GREY analysis from June 16, 2026](https://gridthegrey.com/posts/first-look-agent-evalkit-embeds-llm-judges-into-dev-pipelines-expanding-test/) flagged several security vectors for Agent-EvalKit that are worth taking seriously:

| Risk | Impact | Mitigation |
|---|---|---|
| Eval pipeline manipulation | Corrupted quality signals — bad agents pass eval | Apply write-access controls and integrity verification to evaluation dataset files |
| Source code exfiltration | Agent source leaked via eval context window | Restrict AI coding assistant network access during evaluation runs |
| Prompt injection via eval data | LLM judge compromised by adversarial test cases | Sanitize tool return values before passing to LLM judge prompts |
| Supply chain poisoning | Malicious dependency in eval pipeline | Pin Agent-EvalKit and dependency tree in CI/CD |

The mapped OWASP risks are primarily LLM01 (Prompt Injection) and LLM05 (Supply Chain Vulnerabilities). If you're running Agent-EvalKit in a CI/CD pipeline, treat the evaluation dataset as a trusted input with integrity controls — the same way you'd treat your test database.

For a deeper look at agent security in production, see [AI Agent Security Best Practices](/posts/ai-agent-security-best-practices-2026/).

## Agent-EvalKit vs Other Evaluation Tools

The eval landscape in 2026 is crowded. Here's how Agent-EvalKit positions against the main alternatives:

| Tool | License | Agent-Specific? | Dev-Env Integration | Cost |
|---|---|---|---|---|
| Agent-EvalKit | Apache 2.0 | Yes (full agent workflow) | Claude Code / Kiro / Kilo | Free (Bedrock costs) |
| DeepEval | Apache 2.0 | No (general LLM eval) | pytest-native | Free |
| Promptfoo | MIT | Partial (prompt-focused) | CLI | Free |
| Braintrust | Proprietary | Partial | Web + CLI | Paid |
| LangFuse | MIT (EE) | No (observability) | SDK | Free tier |

The key differentiator for Agent-EvalKit is the agent-specific workflow. DeepEval gives you a general-purpose LLM evaluation framework with 50+ metrics, but it doesn't read your agent's source code, generate test cases from tool definitions, or produce file-level fix recommendations. Both tools are open-source — DeepEval runs as a backend for Agent-EvalKit's eval phase, which means you can use both together.

For a head-to-head comparison of open-source eval harnesses, see the [Open-Source Agent Eval Harness Comparison](/posts/open-source-agent-eval-harness-comparison-2026/).

## When Should You NOT Use Agent-EvalKit?

Honest trade-offs:

- **Your agent isn't on a supported framework.** If you're using a custom agent architecture that doesn't follow Strands, LangGraph, or CrewAI patterns, Agent-EvalKit's source code analysis in the Plan phase won't understand your agent. You can still use it with manual evaluation configuration, but you lose the main advantage.

- **You need a managed dashboard.** Agent-EvalKit produces markdown reports. If your org requires a dashboard, SLAs, role-based access, and audit trails, you want AgentCore Evaluations or Braintrust.

- **You don't want an AWS dependency.** The LLM-as-judge scoring requires Amazon Bedrock. If your eval pipeline runs on OpenAI or local models, you can use DeepEval with Ollama for evaluation — but you lose the integrated six-phase workflow.

- **Your agent is in production, not development.** Agent-EvalKit is designed for the inner dev loop. For production monitoring, you need online evaluation with trace sampling and error budgets — that's AgentCore Evaluations or a dedicated observability platform.

## FAQ

### What AI coding assistants does Agent-EvalKit integrate with?

Claude Code, Kiro CLI, and Kilo Code. The integration uses slash commands (`/evalkit.plan`, `/evalkit.data`, etc.) that the assistant interprets as evalkit CLI invocations. If you use a different coding assistant, you can run the evalkit CLI commands directly — you just lose the guided workflow.

### Does Agent-EvalKit require Amazon Bedrock?

For the LLM-as-judge scoring phase (Eval), yes — it uses Bedrock to run the evaluation model. The Plan, Data, Trace, and Run Agent phases run locally. If you need a completely offline eval pipeline, you can use DeepEval as a backend with local models, but you lose the automated six-phase orchestration.

### Can I use Agent-EvalKit in CI/CD?

Yes, but it's not the primary use case. Agent-EvalKit's commands are designed for interactive use with a coding assistant. For CI/CD, you'd script the CLI commands directly: `evalkit plan`, `evalkit data`, `evalkit run_agent`, `evalkit eval`, `evalkit report`. The [Agent CI/CD Eval Pipeline Integration Guide](/posts/agent-ci-cd-eval-pipeline-integration-guide-2026/) covers this in more detail.

### How many test cases should I generate?

Start with 20-30 covering the most common agent flows and known edge cases (empty results, permission errors, ambiguous queries). Each test case run with 5-10 iterations gives you ~200-300 total agent executions, which costs about $2-5 in Bedrock judge fees. Scale up as you add more agent capabilities, not before.

### How does Agent-EvalKit compare to AgentCore Evaluations?

AgentCore is a managed AWS service for evaluating deployed Bedrock agents with built-in metrics and a console dashboard. Agent-EvalKit is an open-source CLI for evaluating any agent framework during development. Use both — Agent-EvalKit during development, AgentCore for production monitoring.
