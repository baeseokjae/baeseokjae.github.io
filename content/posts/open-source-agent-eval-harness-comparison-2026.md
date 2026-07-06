---
cover:
  alt: Open Source Agent Eval Harness Comparison 2026
  image: /images/open-source-agent-eval-harness-comparison-2026.png
  relative: false
date: 2026-06-19 12:00:00+00:00
description: 'A 2026 comparison of 11 open-source agent evaluation harnesses: MASEval,
  ClawBench, reaatech, ProofAgent, OpenAgentBench, Kensa, PawBench, CUBE, evalh, ...'
draft: false
schema: schema-open-source-agent-eval-harness-comparison-2026
tags:
- agent-evaluation
- eval-harness
- llm-testing
- open-source
- maseval
- clawbench
- kensa
- evalh
title: Open Source Agent Eval Harness Comparison 2026
---

The 2026 open-source agent eval harness market is undergoing a Cambrian explosion. Unlike 2024–2025 where the dominant tools focused on scoring LLM outputs — comparing a generated answer to a ground-truth label — this year's crop evaluates the entire agent system: harness configuration, tool-use trajectory, orchestration topology, and failure recovery as a unified stack. I spent the last month digging into 11 open-source eval frameworks that emerged in the past 12 months. The key finding: framework choice matters as much as model choice. PawBench demonstrates this directly — identical models across different harnesses produce up to an 11.5-point spread on the same task set. If you're still treating eval as "run a model, check the answer," the tools below will change how you think about agent quality.

## The 2026 Landscape Shift

Three things have changed since the early eval days of DeepEval, Ragas, and PromptFoo. First, trace-based scoring replaced final-answer checking as the architectural standard — tools score the *process* (tool selection order, recovery from errors, state management) not just the output. Second, reproducibility is recognized as the #1 unsolved problem: ClawBench found that 47% of benchmark variance is seed noise, which means a model that looks 10 points better might just be luckier with random seeds. Third, the market is fragmenting into focused niches — adversarial security harnesses (ProofAgent), coding-agent-specific evaluators (Kensa), TypeScript-native pipelines (reaatech), and YAML-driven regression gates (evalh). No single framework dominates; the right choice depends entirely on your architecture.

Below I cover the 11 tools grouped by what they do best.

## Multi-Agent System Evaluation: MASEval

MASEval (MIT, PyPI, arXiv 2603.08835) is the strongest option for evaluating full multi-agent systems. Unlike tools that treat agents as independent LLM calls, MASEval treats the entire orchestration topology as the unit of analysis — agent-to-agent communication patterns, error propagation across agents, and delegation decisions.

```python
from maseval import SystemEvaluator, AgentTrace
from maseval.metrics import (
    TopologyCoherence, DelegationOptimality, RecoveryEfficiency
)

evaluator = SystemEvaluator(
    adapters=["autogen", "langchain", "custom"],
    metrics=[TopologyCoherence(), DelegationOptimality(), RecoveryEfficiency()]
)

# Evaluate a recorded multi-agent session from its trace
trace = AgentTrace.load("session_001.jsonl")
result = evaluator.evaluate(trace)
print(result.report())
```

MASEval ships with adapters for AutoGen, LangChain, and custom frameworks, making it agent-agnostic. If you're running [multi-agent systems with LangGraph or CrewAI](/posts/ai-harness-engineering-guide-2026/), MASEval is the only harness that can score how well your agents coordinate rather than how well each individual LLM answers. The trade-off: no CI integration out of the box. You get detailed system-level reports, but you need to wire them into a pipeline yourself.

## Reproducibility-First Benchmarking: ClawBench

ClawBench (MIT, 180+ stars) approaches evaluation from the opposite direction of most tools. Rather than adding more metrics, it subtracts noise. Core v1 ships with 19 signal-curated tasks from a 40-task pool — dropping 21 that produce unreliable scores. Every run executes 3 mandatory trials with statistical significance tests, and the framework quantifies exactly how much of your score variance comes from seed noise versus actual model capability.

```bash
clawbench run --model claude-opus-4.7 \
  --harness openclaw \
  --trials 3 \
  --variance-report full
```

The variance decomposition is ClawBench's killer feature. I ran a regression suite where GPT-5.5 appeared 5 points ahead of DeepSeek V4 on a single run, but ClawBench's bootstrap confidence intervals showed the difference was within noise — saving me from a false-positive model swap. For teams running leaderboard-style evaluations where a wrong read could derail model selection, ClawBench's statistical rigor is worth the narrower task scope. It's not for CI regression gates; it's for high-stakes model and harness decisions.

## TypeScript-Native Production Eval: reaatech/agent-eval-harness

Every other harness in this comparison is Python. reaatech/agent-eval-harness (TypeScript, pnpm monorepo) is the first serious TypeScript-native eval framework. It ships 12 composable packages covering trajectory analysis, tool-use correctness, cost-per-task, latency budgets, golden trajectory curation, and an MCP server for LLM client integration.

```typescript
import { Suite, TrajectoryMetric, CostMetric, Gate } from '@agent-eval/harness';

const suite = new Suite({
  metrics: [new TrajectoryMetric(), new CostMetric()],
  gate: new Gate({ maxCostPerTask: 0.05, maxLatencyMs: 15000 })
});

const report = await suite.run(trajectories);
console.log(report.toJUnit());
```

The JUnit/XML output and GitHub Annotations support mean it integrates into CI the same way Playwright or Vitest does — failing a PR when an agent's trajectory deviates from the golden path or when cost-per-task exceeds budget. If your stack is TypeScript end-to-end (agents, API layer, CI), this harness avoids the Python impedance mismatch. If you're in Python, skip it — the ecosystem is still young with less community adoption than the Python tools.

## Adversarial Security Eval: ProofAgent

ProofAgent is positioned as "pytest for AI agents" and lives up to that claim. It ships 183 bundled adversarial traps across 11 families — GDPR, HIPAA, PCI, SOX, prompt injection, jailbreak, PII leakage, and malware-gen solicitation. The scoring uses a 3-Harness-Juror Delphi consensus: three independent evaluators score the agent's response, and if they disagree, the system re-votes until consensus is reached.

```python
from proofagent import Harness, JurorPool

harness = Harness(
    traps=["prompt_injection", "pii_leakage", "hipaa_boundary"],
    jurors=JurorPool(size=3, consensus="delphi")
)

results = harness.run_against(my_agent_endpoint)
assert results.overall_pass_rate > 0.95
```

The assertion-style output makes it natural to gate deployments on security eval scores. If you're shipping an agent that handles user data, running ProofAgent as a pre-deploy gate should be table stakes. If your agent is purely internal tooling with no user-facing prompts, the trap coverage is overkill — use a simpler approach.

## Stateful Control System Verification: OpenAgentBench

OpenAgentBench evaluates agents as stateful control systems, not transcript generators. It scores tool-choice optimality (did the agent pick the right tool or brute-force with the wrong one?), privilege safety (did it try to escalate permissions?), memory hygiene (did it leak context across sessions?), and recovery behavior (how did it handle tool failures?).

```python
from openagentbench import AgentTester
from openagentbench.checks import (
    ToolOptimality, PrivilegeSafety, RecoveryGrace
)

tester = AgentTester(checks=[ToolOptimality(), PrivilegeSafety()])
report = tester.run("my_agent.py", scenarios=["billing_flow"])
```

The Agent Chaos Lab injects failures mid-session — revoking a tool mid-call, dropping a network request, corrupting a memory cell — and measures whether the agent recovers gracefully. This is the closest thing to chaos engineering for agents. For production-critical agents that handle money, credentials, or user data, OpenAgentBench's state verification catches failure modes that no output-scoring metric ever would.

## Coding Agent Eval: Kensa

Kensa (MIT, free) is purpose-built for evaluating coding agents — Claude Code, OpenAI Codex, Cursor, OpenCode, Gemini CLI. Its workflow is capture-then-generate-then-eval: you record real agent sessions via auto-instrumentation (zero code changes, OTel), the tool synthesizes new test scenarios from those captures using an LLM, then you run the eval.

```bash
kensa capture --agent claude-code --output my_traces.jsonl
kensa generate scenarios --from my_traces.jsonl --output scenarios.jsonl
kensa eval --scenarios scenarios.jsonl --models claude-opus-4.7,gpt-5.5
```

The auto-instrumentation uses OpenTelemetry and requires no changes to the agent — it hooks into the process environment. Kensa's 5 built-in skills (audit, generate scenarios, generate judges, validate judge, diagnose errors) make it useful for teams building custom eval pipelines for coding agents. It's the most practical tool I've found for running a regression suite against new coding agent versions. For evaluating general-purpose non-coding agents, look elsewhere — Kensa's scenario generation is heavily optimized for code-editing tasks.

## Model x Harness Co-Evaluation: PawBench and CUBE

PawBench (Apache 2.0, 57 stars) is unique in that it scores the model *and* the harness together. It runs 150 tasks from 6 source benchmarks across 9 models and 3 harnesses, then produces a matrix showing harness gaps even when the model is fixed. The spread is up to 11.5 points — QwenPaw averages 74.9, OpenClaw 72.9, Hermes 69.3. If you're debating which eval harness to standardize on, PawBench gives you data, not opinions.

CUBE Harness (AI Alliance) takes the opposite approach: it standardizes the evaluation *protocol* so harness choice becomes irrelevant. Based on the CUBE Standard benchmark protocol, it uses Ray for parallel episode execution and outputs RL-ready trajectories with full LLM call logging. Still alpha-stage, but if CUBE gains adoption, it could consolidate the fragmented harness landscape. Watch this space rather than adopting it today.

## Config-Driven Regression: evalh

evalh is the most boring tool in this comparison, and that's its strength. One YAML config drives everything — metrics, variants (N x M cases for A/B testing), executor backends (6 adapter families), and observability integrations (8 backends).

```yaml
suite: billing-agent-regression
variants:
  - model: claude-opus-4.7
    config: production.toml
  - model: gpt-5.5
    config: experimental.toml
metrics:
  - text_checks: [contains_invoice_total, no_pii]
  - llm_judge: { prompt: judge_billing.txt }
gate:
  drift_detection: true
  baseline: production-2026-06-01
```

I use evalh for my day-to-day CI regression suite because it takes 10 minutes to configure a new eval — no boilerplate, just YAML. The drift detection mode promotes a baseline, then flags any regression across variants. For teams that want eval coverage without a multi-week integration project, evalh is the fastest path.

## Lightweight and Auto-Improving: Siddharth-1001 and Harness Bench

Siddharth-1001/agent-eval-harness (MIT) covers 4 metric dimensions (tool success, hallucination, latency, cost) with adapters for LangGraph, CrewAI, OpenAI Agents SDK, and Anthropic. The local dashboard and HTML export for side-by-side comparison make it useful for hacking on eval configurations before investing in production infrastructure.

Harness Bench takes this one step further with "Improvers" — automated research loops that analyze eval failures and propose harness mutations, similar to how DSPy optimizes prompts. You point it at a failing eval run, and it suggests changes to the harness configuration. Novel concept, early stage — the generated mutations still require human review before deployment.

## A Staged CI Framework for 2026

No single harness covers all four eval stages. Here's what I run in practice:

| Stage | Tool | What It Checks |
|-------|------|----------------|
| Unit eval | evalh + Siddharth-1001 | Per-task correctness, tool accuracy, latency |
| Integration eval | MASEval + OpenAgentBench | Multi-agent coordination, state recovery |
| Regression gate | evalh (drift detection) | Score regression from baseline |
| Production security | ProofAgent | Adversarial resilience, compliance boundary |

[AI Harness Engineering](/posts/ai-harness-engineering-guide-2026/) covers the orchestration layer connecting these stages. For understanding the benchmarks these harnesses run against, see the [LLM Benchmarks Guide](/posts/llm-benchmarks-guide-2026/) and [SWE-bench Guide](/posts/swe-bench-coding-benchmarks-guide-2026/).

## Decision Matrix

| Your Need | Best Pick | Runner-Up |
|-----------|-----------|-----------|
| Multi-agent system eval | MASEval | OpenAgentBench |
| High-stakes model selection | ClawBench | PawBench |
| TypeScript CI pipeline | reaatech/agent-eval-harness | — |
| Security/compliance gating | ProofAgent | — |
| Coding agent regression | Kensa | evalh |
| Stateful failure injection | OpenAgentBench | MASEval |
| Quick YAML-driven regression | evalh | Siddharth-1001 |
| Harness benchmarking | PawBench | CUBE (alpha) |
| Auto-improving harnesses | Harness Bench | — |

The fragmentation in this space is real — there isn't one framework to rule them all, and I don't expect one to emerge in 2026. Pick the tool that matches your eval stage and architecture, chain them together with a CI pipeline, and treat eval infrastructure as a first-class investment alongside model selection. The teams winning at production AI agents aren't the ones with better models; they're the ones that can measure whether their agents actually work.