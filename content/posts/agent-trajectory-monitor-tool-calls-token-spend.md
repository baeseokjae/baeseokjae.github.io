---
title: "Agent Trajectory Monitor: Watching Tool Calls and Token Spend in Real Time"
date: 2026-08-20T13:01:35+00:00
tags:
  - ai-agents
  - observability
  - llm-monitoring
  - token-usage
  - tool-calls
  - mlops
  - cost-optimization
description: "An agent trajectory monitor logs every tool call and token spend in real time to expose retry loops, context exhaustion, and budget overruns before they cost you."
draft: false
cover:
    image: "/images/agent-trajectory-monitor-tool-calls-token-spend.png"
    alt: "Agent Trajectory Monitor: Watching Tool Calls and Token Spend in Real Time"
    relative: false
schema: "schema-agent-trajectory-monitor-tool-calls-token-spend"
---

An agent trajectory monitor watches the full sequence of steps, tool calls, decisions, and token spend an AI agent makes in real time — not just the final answer. Because AI agents consume 5-30x more tokens per task than standard chatbots, real-time trajectory monitoring has moved from a nice-to-have to a budget requirement. It lets you see whether your agent is doing the right work or just getting the right answer by chance.

## What Is an Agent Trajectory Monitor and Why You Need One

A trajectory is the ordered action log of everything an agent does between receiving a prompt and producing an output: the reasoning steps, the tool calls it makes (which tool, with which arguments), the observations that come back, and the tokens consumed along the way. A trajectory monitor captures and displays this log as it happens, letting you replay any run like a flight recorder.

The core problem it solves is that output-only evaluation cannot tell a reliable agent from one that reaches the right answer by chance. An agent can produce a perfect final answer while taking a terrible path to get there — calling the right tool with wrong arguments, retrying the same failing call in a loop, or following a slow, expensive route. A trajectory monitor exposes that hidden behavior.

This matters more in 2026 than ever. Teams are now deploying autonomous agents that act directly on infrastructure with read/write production access through secure toolchains, as described in RajivOnAI's analysis of autonomous SRE agents. When an agent can spin up read replicas, terminate blocking queries, or modify autoscaling, monitoring the trajectory is not optional — it is the difference between a helpful assistant and an autonomous denial-of-service engine.

## The Real-Time Signals That Matter: Tool Calls, Token Spend, and Loops

Monitoring an agent is fundamentally different from monitoring an application. Application code execution is deterministic; agent behavior is not. A single agent request can trigger many model calls and many tool calls, each adding latency and cost. Three signals matter most in real time:

- **Tool calls** — which tool is invoked and with what arguments. This is the highest-leverage signal because it shows whether the agent is acting correctly before the action has side effects.
- **Token spend** — how many input and output tokens each step consumes. Because agents use 5-30x more tokens than chatbots, this is the budget-critical metric.
- **Loops and stalls** — recursive retry loops, duplicated context, and context window exhaustion. These are the silent killers that burn budget without making progress.

The groundcover research on AI agent observability notes that an agent run can look successful while doing the wrong work — calling the right tool with wrong arguments, entering a loop, or following a slow path. Real-time signals catch these patterns in flight rather than after the fact.

## How to Capture the Data: stream_options Usage, Provider APIs, and Telemetry

You cannot monitor what you do not capture. There are three primary ways to get trajectory data, and mature setups use all of them.

**Provider usage in streamed responses.** OpenAI Chat Completions requires passing `stream_options: {"include_usage": true}` to return aggregate token usage in the final stream chunk. Without this flag, streamed responses hide token counts entirely. Other providers have equivalent options, so check your model provider's documentation.

**Provider usage APIs.** Most providers expose usage endpoints that report token consumption per request, per model, and per API key. These are the authoritative source for billing-accurate numbers, and they are the foundation of any cost dashboard.

**Application telemetry and tracing.** Instrument your application layer to log each tool call, its arguments, latency, and the token counts associated with each step. This is where the trajectory itself lives — the ordered sequence of what happened, which provider APIs cannot give you.

For governance across multiple agents, a centralized MCP Gateway plus an agent monitor collects usage from many tools in one place, giving you attribution and audit trails that ad-hoc instrumentation cannot. This also closes the shadow AI gap: agents running outside governed infrastructure consume tokens without attribution or audit trails.

## Key Metrics to Watch: Tool-Call Precision, Step Efficiency, Token-per-Step, and Latency

Once data is flowing, focus on four metrics that together describe agent health. These map directly to the trajectory evaluation framework from Atlan's research on AI agent trajectory evaluation:

| Metric | What it measures | Why it matters |
|--------|-----------------|----------------|
| Tool-call precision | Whether the agent calls the right tool with the right arguments | Distinguishes correct-by-chance from genuinely reliable agents |
| Step efficiency | Number of tool calls vs. the minimum needed; loops and retries | Exposes wasteful paths and retry storms |
| Token per step | Average input + output tokens per tool call | The raw driver of your agent bill |
| Latency | Time per tool call and total run time | Predicts UX and infrastructure load |

Tool-call precision is the most important because it reveals intent. An agent that calls a search tool to answer a question it already knows, or calls a write tool with corrupted arguments, will eventually fail — trajectory monitoring surfaces this before the side effects compound. Step efficiency catches the retry-loop pattern where the agent repeats a failing call with the same bad arguments and burns tokens each time.

## Building the Monitor: Instrumentation, Tracing, and Dashboards

A minimal trajectory monitor has three layers: instrumentation, tracing, and a dashboard.

**Instrumentation** wraps your agent loop. Before each tool call, record the tool name, the arguments, a timestamp, and the token count so far. After each tool returns, record the result size, latency, and new token count. This produces the ordered action log that is the heart of a trajectory.

**Tracing** links a single logical request across its many model and tool calls. Use trace IDs so you can view an entire run as one timeline rather than disconnected log lines. OpenTelemetry spans work well here and integrate with your existing observability stack.

**Dashboarding** turns the captured data into something watchable. At minimum, show: active runs and their current step, token spend per run and per agent, tool-call success vs. failure rates, and live alerts when thresholds breach. Real-time means you see a runaway agent while there is still time to stop it.

The four pillars framework from groundcover — telemetry, traces, metrics, and evals — is a useful checklist. Telemetry captures the events, traces connect them into runs, metrics aggregate them into trends, and evals score them against reference trajectories.

## Setting Token and Workflow Budgets with Real-Time Alerts

Cost visibility in production AI environments is a design constraint, not a byproduct, as Suhas Bhairav's cost-monitoring guide argues. A trajectory monitor feeds directly into budget enforcement.

Start by building a cost model for each tool and route. Different tools have very different costs: a file write is cheap, a high-capacity model call with a large context is expensive, and a retry loop multiplies either. Measure token consumption per agent and per tool call, then cap token spend per workflow and instrument real-time budgets tied to business KPIs.

Alert when thresholds breach. The key insight is that token counting must align with the exact model and prompt structure used in production, not just raw input length. Prompt templating, system instructions, and retrieved context all inflate token counts beyond what a naive character-to-token estimate predicts.

Enforce budget-aware routing for fallbacks. When the primary path is about to exceed budget, the monitor can route to a cheaper model or a more efficient tool rather than letting the spend continue. This turns a passive dashboard into an active cost control.

## Detecting Failure Modes: Retry Loops, Context Exhaustion, and Shadow AI

Real-time trajectory monitoring is most valuable for catching the failure modes that output-only testing misses.

**Recursive retry loops.** The agent calls a tool, the call fails, and the agent retries with the same or similar arguments, burning tokens with each iteration. A trajectory monitor flags repeated identical tool calls within a window — the clearest sign of a stuck agent.

**Context window exhaustion.** As an agent accumulates tool results, its context grows. When it approaches the context limit, either it starts truncating or the provider errors out. Monitoring context size per step lets you alert before the agent degrades or fails mid-task.

**Duplicated context.** Agents often re-inject the same retrieved document or system prompt into every step. This silently inflates token spend and is invisible without per-step token measurement.

**Shadow AI.** Agents running outside governed infrastructure consume tokens with no attribution or audit trail. A centralized MCP gateway with an agent monitor detects this by seeing usage that no governed run accounts for, letting you bring the shadow workloads under management.

## Tools and Platforms: OpenTelemetry, MCP Gateways, and Managed Observability

You do not have to build everything from scratch. The 2026 observability landscape offers three tiers.

**OpenTelemetry.** The open standard for telemetry and traces. Instrument your agent loop with OTLP spans and push them to any backend. It is vendor-neutral and the most portable option, and it integrates with the dashboards you already run.

**MCP Gateways.** If you route tool calls through a Model Context Protocol gateway, you get a natural interception point for recording every tool call, its arguments, and token usage. MintMCP's research highlights this as the governance-friendly path, since all tool traffic flows through one auditable choke point.

**Managed observability.** CloudWatch and Datadog have evolved built-in generative AI observability, according to RajivOnAI. These platforms now ingest LLM and agent telemetry natively, giving you prebuilt dashboards for token spend, latency, and errors without custom instrumentation. They are the fastest path when you already run their broader stack.

## Best Practices for Multi-Agent Systems and Production

Trajectory monitoring applies to both single and multi-agent systems, and the groundcover research emphasizes this. A few practices keep it effective at scale:

- **Trace across agents.** When one orchestrator agent delegates to worker agents, use a shared trace ID so the entire delegation tree is one replayable run.
- **Sample strategically.** At high volume, trace every run is expensive. Sample full trajectories for a percentage of traffic while keeping counters on 100%.
- **Score against reference trajectories.** Build grounded reference trajectories from real business logic, as Atlan recommends, and score each run against them to distinguish reliable from lucky agents.
- **Correlate cost with KPIs.** Do not just watch token numbers; tie them to business outcomes so budget alerts mean something operationally.
- **Retain replays.** Keep recent trajectory logs to replay and debug incidents after the fact, like a flight recorder you can pull out of the drawer.

## Getting Started This Week: A Minimal Real-Time Trajectory Monitor

You do not need a full observability platform to start. A minimal real-time trajectory monitor is achievable in a single afternoon.

1. **Enable provider usage.** Add `stream_options: {"include_usage": true}` to your streaming calls so you actually receive token counts.
2. **Wrap your tool loop.** Add three lines of logging around each tool call: tool name, timestamp, and token count before and after.
3. **Add a trace ID.** Generate one ID per run and stamp every log line and tool call with it.
4. **Stream to a dashboard.** Pipe the logs into a simple dashboard or your existing monitoring tool, filtered by trace ID.
5. **Set one alert.** Start with a retry-loop detector: alert when the same tool call repeats more than N times within a window.

That gives you visibility into tool calls and token spend in real time — enough to catch the runaway agent, the retry storm, and the budget overrun before they cost you. From there, add the cost models, reference trajectories, and MCP gateway governance as the stakes grow.

## FAQ

**What is an agent trajectory monitor?**
An agent trajectory monitor captures and displays the ordered sequence of steps, tool calls, decisions, and token spend an AI agent makes during a run, in real time. It is the flight recorder for your agent, letting you replay and inspect exactly how a result was produced rather than just seeing the final answer.

**Why do AI agents need token monitoring more than chatbots?**
AI agents consume 5-30x more tokens per task than standard chatbots because a single request triggers many model calls and tool calls. Even as per-token costs fall, overall inference costs keep rising for agentic workloads, so real-time token monitoring is a budget requirement rather than a nice-to-have.

**How do I get token usage data from OpenAI streaming responses?**
You must pass `stream_options: {"include_usage": true}` in your streaming request. Without this flag, streamed responses omit aggregate token usage. Provider usage APIs remain the authoritative billing source, and application telemetry captures the per-step trajectory the provider cannot see.

**What is tool-call precision and why does it matter?**
Tool-call precision is whether the agent invokes the right tool with the right arguments. It is the key metric that distinguishes a genuinely reliable agent from one that reaches the right answer by chance, because output-only scoring cannot see whether the path to the answer was correct.

**How can a trajectory monitor detect a retry loop?**
A retry loop shows up as repeated identical tool calls within a short window, each burning tokens without progress. A trajectory monitor flags this pattern in real time so you can stop the agent and fix the underlying bad arguments or failing tool before the budget drains.
