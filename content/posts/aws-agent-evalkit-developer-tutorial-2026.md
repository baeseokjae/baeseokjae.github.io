---
cover:
  alt: AWS Agent-EvalKit Developer Tutorial 2026
  image: /images/aws-agent-evalkit-developer-tutorial-2026.png
  relative: false
date: 2026-06-20 12:00:00+00:00
description: 'A hands-on tutorial for AWS Agent-EvalKit (released June 11, 2026):
  install, run the 6-phase eval workflow, combine code-based and LLM-judge scoring,
  an...'
draft: false
schema: schema-aws-agent-evalkit-developer-tutorial-2026
tags:
- agent-evaluation
- aws
- evalkit
- claude-code
- bedrock
- llm-testing
- agent-testing
title: 'AWS Agent-EvalKit: Open-Source AI Agent Evaluation for Developers — Tutorial
  & Deep Dive'
---

AWS Agent-EvalKit is an open-source toolkit (Apache 2.0, released June 11, 2026) that runs AI agent evaluation directly inside your coding assistant via slash commands. Instead of treating agent evaluation as a post-deployment activity, it brings a six-phase workflow — Plan, Data, Trace, Run Agent, Eval, Report — into Claude Code, Kiro CLI, or Kilo Code, combining code-based evaluators with LLM-as-judge scoring through Amazon Bedrock. I've been running evaluations against AI agents for the last two years, and the pattern I kept seeing was: teams either buy a managed eval platform or cobble together Python scripts and a prompt template. Agent-EvalKit splits the difference — it's a CLI that reads your agent source code, generates test cases, instruments tracing, runs the trials, and recommends fixes with file-level accuracy. In this tutorial, I'll walk through installing it, running your first evaluation, and the real-world case study where it caught a hallucination problem that output-level testing missed entirely.

## What Agent-EvalKit Actually Does

Agent-EvalKit is not another eval framework you import as a library. It's an AI assistant that operates through your existing coding assistant. You install it once with `uv tool install`, initialize a project, then issue slash commands like `/evalkit.plan` and `/evalkit.eval` in your Claude Code or Kiro CLI session. The assistant reads your agent's source code from disk, designs an evaluation strategy, generates test cases, adds OpenTelemetry tracing to instrument your agent, runs it against the test cases, scores the traces, and writes a report with specific code-level fix recommendations.

The key architectural decision is that the evaluation pipeline lives in your dev environment, not in a separate platform. This means it reads your actual agent code, runs against real tool endpoints (with the safety caveat that you should use staging credentials), and produces recommendations that reference specific lines in your codebase. The trade-off vs. a managed platform like AgentCore Evaluations: you get deeper code awareness and lower setup friction, but you don't get the managed dataset versioning, cross-team dashboards, or release gating that a platform provides.

## Installation

Agent-EvalKit requires Python 3.11+, `uv`, Git, and a supported AI coding assistant. I'm using Claude Code 0.3.14 and it works cleanly.

```bash
uv tool install evalkit --from git+https://github.com/awslabs/Agent-EvalKit.git

# Verify
evalkit check
```

This installs the `evalkit` CLI globally. The actual eval workflow runs through your coding assistant's slash commands, but `evalkit init` scaffolds the project structure.

```bash
evalkit init my-search-agent-eval
cd my-search-agent-eval

# Copy your agent source into the eval project
cp -r /path/to/your/search-agent .
```

The project structure created by `evalkit init` includes a `commands/` directory where the slash-command handlers live, a `templates/` directory for evaluation test case templates, and a `tracing/` directory with OpenTelemetry instrumentation helpers.

## The Six-Phase Workflow

Once the project is initialized, you open the `my-search-agent-eval` directory with your coding assistant and start the workflow.

### Phase 1: Plan (`/evalkit.plan`)

This is the only phase that requires user input. You tell the assistant what kind of agent you're evaluating and what you care about.

```
/evalkit.plan Evaluate my search agent at ./search-agent for faithfulness and tool accuracy
```

The assistant reads every Python file in `./search-agent`, identifies the tool-calling patterns, the LLM provider configuration, and the response formatting logic. It returns an evaluation strategy document that specifies:

- Which metrics to compute (faithfulness, tool-selection accuracy, response quality)
- What evaluator style to use for each (LLM-as-judge for faithfulness, code-based for tool accuracy)
- How many test cases to generate and what categories they should cover

I found the plan output thorough but verbose — it runs the full agent code through the assistant's context window, which costs 8,000–15,000 tokens per `plan` invocation depending on agent size. You can constrain it with a focused description if your agent is large.

### Phase 2: Data (`/evalkit.data`)

```
/evalkit.data Focus on edge cases: empty search results, malformed queries, timeout scenarios
```

The assistant generates test cases with ground-truth annotations and writes them to `eval/test_cases.json`. Each test case includes:

```json
{
  "id": "tc_003",
  "input": "search for non-existent product 'XYZ-999'",
  "ground_truth": {
    "expected_tool": "search_products",
    "expected_params": {"query": "XYZ-999"},
    "expected_response_contains": ["no results found", "try different search terms"],
    "faithfulness_check": "response must not fabricate product details"
  },
  "category": "empty_results"
}
```

The ground truth structure matters because it enables both code-based checks (did the agent call the right tool with the right params?) and LLM-judge checks (is the response faithful to the tool output?).

### Phase 3: Trace (`/evalkit.trace`)

```
/evalkit.trace
```

This phase instruments your agent with OpenTelemetry tracing. The assistant reads your agent code and inserts tracer spans around each tool call. For a Python agent using the Strands Agents SDK, the instrumentation wraps the `agent.run()` call with span context that captures:

- Tool name and input parameters
- Timestamps and duration
- Tool output (truncated to configurable max chars)
- Error states and retry attempts

The tracing is optional — you can run the eval against raw agent outputs if you already have logging in place. But without traces, you can only score the final response, not the tool-call path, which is where Agent-EvalKit's best value lives.

### Phase 4: Run Agent (`/evalkit.run_agent`)

```
/evalkit.run_agent
```

The assistant executes your agent against each test case, collects the traces, and writes the results to `eval/traces/`. Each trace file captures the full execution path:

```json
{
  "test_case_id": "tc_003",
  "agent_response": "I couldn't find any products matching 'XYZ-999'. Please try different search terms or check the product catalog.",
  "tools_called": [
    {
      "tool": "search_products",
      "params": {"query": "XYZ-999"},
      "result": {"products": [], "total_count": 0, "suggestions": []}
    }
  ],
  "latency_ms": 2340,
  "token_usage": {"input": 1450, "output": 320}
}
```

### Phase 5: Eval (`/evalkit.eval`)

```
/evalkit.eval
```

This is where the actual scoring happens. The assistant writes evaluation code that reads the traces and computes metrics. For the travel agent case study AWS published, the eval pipeline used two evaluators in parallel:

**Code-based evaluator** — checks tool-selection correctness deterministically. Did the agent call the expected tool? Were the parameters correct? This runs fast (milliseconds per trace) and produces binary pass/fail scores.

**LLM-as-judge evaluator** — scores response faithfulness on a 0–100 scale. The LLM judge (Amazon Nova Pro through Bedrock in the published case study) receives the tool trace alongside the agent's response and answers: "Does the response faithfully reflect what the tools returned, without adding information not present in the tool output?"

The assistant writes the evaluation code at `eval/evaluator.py` so you can review and customize it. I found the generated evaluator templates reasonable but simplistic — the faithfulness judge prompt needed tuning for my domain-specific vocabulary.

### Phase 6: Report (`/evalkit.report`)

```
/evalkit.report
```

The final output is a markdown report covering:

- Aggregate scores per metric
- Per-test-case breakdown with pass/fail details
- A ranked list of improvement recommendations referencing specific code locations
- Expected impact estimate for each recommendation

## The Travel Agent Case Study: Why Output-Level Testing Lies to You

The AWS Machine Learning Blog published Agent-EvalKit using a travel research agent built with Strands Agents SDK and Amazon Bedrock. The agent's job: given a destination and preferences, research flights, hotels, and attractions, then write a travel brief.

The standard eval — ask the agent 20 questions, have a human rate the answers — gave it a response quality score of 83.9%. That looks solid. But Agent-EvalKit's trace-level evaluation told a different story. The faithfulness score was 32.3%.

Here's what happened. When the agent's `search_hotels` tool returned empty results (no vacancies matching the criteria), the agent didn't say "no hotels found." It fabricated hotel names, prices, and descriptions that sounded plausible but came entirely from the model's training data. The final response was well-structured and actionable — every human rater gave it high marks because the hallucinations matched the destination's real hotel landscape. The agent looked competent while being completely wrong.

The trace caught it because the eval compared the tool output (empty list) against the agent response (hallucinated hotel names). An output-only eval never sees the tool output.

After applying Agent-EvalKit's report recommendations — adding an explicit "disclose empty results" instruction to the system prompt and a post-processing check that flags responses containing information not present in tool outputs — the faithfulness score went from 32.3% to 78.1% in one iteration.

This pattern is why I now run trace-level evaluation on every agent I ship. If you only check final outputs, you're measuring presentation quality, not factual reliability.

## CI/CD Integration

Agent-EvalKit generates standalone evaluation code at `eval/` that you can run outside the coding assistant. After the initial `evalkit init` and a full workflow run to set up the pipeline, subsequent runs work as a shell command:

```bash
# Run the evaluation pipeline without the slash-command assistant
python eval/run_pipeline.py --config eval/config.yaml --output eval/report.json

# Check against threshold
python -c "
import json
r = json.load(open('eval/report.json'))
assert r['faithfulness'] > 0.70, f'Faithfulness {r[\"faithfulness\"]} below threshold'
assert r['tool_accuracy'] > 0.85, f'Tool accuracy {r[\"tool_accuracy\"]} below threshold'
"
```

This runs in any CI runner that has Python and network access to Bedrock. For a full CI/CD setup with gating, cost controls, and shadow deployment, see the [Agent CI/CD Eval Pipeline Integration Guide](/posts/agent-ci-cd-eval-pipeline-integration-guide-2026/). The interaction between Agent-EvalKit's trace-level scoring and broader CI gates (regression detection, cost budgets, canary rollouts) is where it gets production-relevant.

## Honest Trade-offs

After running Agent-EvalKit against three different agents over the past week, here are the limitations you'll hit:

**No cross-run versioning.** Each `evalkit init` creates a fresh project. There's no built-in way to compare scores across agent versions or track regression over time. You have to build that yourself by archiving `eval/report.json` files and comparing them externally. The [Open Source Agent Eval Harness Comparison](/posts/open-source-agent-eval-harness-comparison-2026/) covers tools that handle versioning natively if that's a priority.

**LLM-judge cost adds up.** Each eval run pays for both the agent under test (API calls to its tools + LLM) and the judge LLM (Amazon Bedrock inference for faithfulness scoring). On the travel agent eval with 50 test cases, the judge cost was roughly $0.80 per run. At 20 CI runs per day, that's $16/day just for the judge — before the agent's own inference cost.

**Narrow framework support for tracing.** The auto-instrumentation currently generates OpenTelemetry traces for Strands Agents SDK, LangGraph, and CrewAI. If your agent uses a custom framework (many production agents do), you need to write the OTel instrumentation yourself. The generated trace templates at `tracing/` are a decent starting point but not plug-and-play.

**Single-project scope.** Agent-EvalKit is designed for evaluating one agent at a time in one project directory. It doesn't help with cross-agent comparison, A/B testing of prompt variants, or multi-agent system evaluation. For those use cases, tools like MASEval (covered in the eval harness comparison) are a better fit.

## When to Use Agent-EvalKit vs. When to Skip

Use Agent-EvalKit when: you're actively developing an agent and want to catch trace-level failures before they hit production; you need code-level fix recommendations, not just pass/fail scores; you're already in a Claude Code, Kiro CLI, or Kilo Code workflow and want evaluation to feel like an extension of your coding session.

Skip it when: your agent does no tool calling (pure chat — a manual checklist is sufficient); you need managed dataset versioning and regression dashboards across a team; you're evaluating multi-agent systems where coordination topology matters more than individual agent traces.

The toolkit is fresh (v0.1.2 at time of writing) and the community is small — 25 GitHub stars, 5 forks. The Apache 2.0 license and AWS backing suggest it will grow, but today you should expect to customize the generated eval code and trace instrumentation rather than use everything out of the box. For most teams building production agents in 2026, that's still a net positive: the 80% of scaffolding that Agent-EvalKit generates is the boring, error-prone part of setting up trace-level evaluation, and the 20% you customize is the part that makes your agent's specific failure modes visible.