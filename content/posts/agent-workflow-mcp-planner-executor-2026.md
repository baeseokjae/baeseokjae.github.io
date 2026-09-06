---
title: "Agent Workflow MCP Orchestrator: Building a Planner-Executor Multi-Agent System"
date: 2026-09-06T22:01:18+00:00
tags:
  - MCP
  - Multi-Agent Systems
  - Agent Orchestration
  - Planner-Executor
  - AI Agents
description: "Learn how to build a planner-executor agent workflow MCP orchestrator: split strategy from tool execution, connect agents via MCP tool servers, and scale."
draft: false
cover:
  image: "/images/agent-workflow-mcp-planner-executor-2026.png"
  alt: "Agent Workflow MCP Orchestrator: Planner-Executor Multi-Agent System"
  relative: false
schema: "schema-agent-workflow-mcp-planner-executor-2026"
---

A planner-executor agent workflow MCP orchestrator splits a hard task into two roles: a planner that decomposes the goal into a step-by-step plan, and one or more executors that carry out each step with tool access, all connected through Model Context Protocol (MCP) tool servers. This pattern handles open-ended, path-dependent work that a linear pipeline cannot, because the planner can re-plan mid-run based on what executors return. It is the canonical multi-agent orchestration architecture for tasks where the full sequence of steps is not known in advance.

## What Is the Planner-Executor Pattern?

The planner-executor pattern is a core multi-agent orchestration architecture in which a single "planner" agent owns strategy and a separate "executor" agent (or a pool of executors) owns tool execution. The planner receives the high-level goal, decomposes it into discrete steps, and hands each step to an executor. The executor performs the work — often calling tools, searching, or running code — and returns a condensed result. The planner then decides whether to proceed, adjust, or re-plan.

LangGraph documents planner-executor as a core agent architecture pattern: the planner decomposes a task into a plan, the executor carries out each step with tool access, and the planner can re-plan based on executor results, enabling dynamic, adaptive execution. It is well-suited for tasks where the full sequence of steps is not known in advance.

Anthropic's "Building Effective Agents" taxonomy places planner-executor as a specialization of the orchestrator-workers pattern. In that taxonomy, the orchestrator decomposes a task, delegates subtasks to worker agents, and synthesizes their results. The planner-executor variant makes the planning loop explicit: the planner is the orchestrator, and the executors are the workers, with a feedback loop that allows re-planning.

The key distinction from a simple prompt chain is the feedback loop. In a chain, each step feeds the next in a fixed order. In planner-executor, the planner observes executor output and can change the plan entirely — adding steps, removing dead ends, or spawning parallel executors.

## Why MCP Is the Glue for Multi-Agent Orchestration

Model Context Protocol (MCP) is an open standard created by David Soria Parra and Justin Spahr-Summers, released under the MIT license, with the schema defined in TypeScript and published as JSON Schema. MCP provides a standardized way for LLM applications to connect to external tools, data sources, and context.

For multi-agent orchestration, MCP solves a portability problem. Without a standard, each agent framework invents its own tool interface, so a planner built in one framework cannot reuse tools written for another. MCP makes the tool layer portable: an MCP tool server exposes capabilities over a standard protocol, and any MCP-compatible agent — planner or executor — can call it.

This is the philosophy behind mcp-agent (lastmile-ai), a composable framework that implements every pattern from Anthropic's Building Effective Agents, including planner-executor and orchestrator-workers, in a composable way. Its stated philosophy: "MCP is all you need to build agents, and simple patterns are more robust than complex architectures." mcp-agent manages the full lifecycle of MCP server connections and scales to sophisticated workflows built on Temporal for pause, resume, and recovery.

The practical benefit: you build your tool servers once as MCP servers, then both the planner and the executors consume them through the same protocol. Adding a new capability (a database, a search API, a code runner) means adding one MCP server, not rewriting agent glue.

## Architecture: Planner, Executor, and MCP Tool Servers

A reference implementation of a multi-agent workflow orchestrator with MCP tool servers uses dedicated planner and executor agents connected through MCP. The architecture has three layers:

**Planner agent.** Owns the goal, the plan, and the decision loop. It does not execute tools directly; it decomposes the task, dispatches steps, and synthesizes results. Its context window stays clean because it only receives condensed executor outputs.

**Executor agents.** Own tool execution. Each executor runs in its own context window, explores freely, calls MCP tools, and returns a compressed summary to the planner. This is the compression mechanism Anthropic describes: subagents explore in isolated context windows and condense the most important tokens back to the lead agent.

**MCP tool servers.** The shared capability layer. Both planner and executors connect to these servers over the MCP protocol. A tool server might wrap a search API, a database, a file system, or a code interpreter.

The separation of concerns is the point. The planner owns strategy; the executors own tool execution. This gives each role distinct tools, prompts, and exploration trajectories, which reduces path dependency — a failure in one executor's exploration does not corrupt the planner's plan or another executor's work.

| Layer | Responsibility | Context window | Example tools |
|-------|---------------|----------------|---------------|
| Planner | Decompose, dispatch, re-plan, synthesize | Clean, receives summaries only | Planning, routing, evaluation |
| Executor | Execute steps, call tools, explore | Isolated per executor | Search, code, DB, file I/O |
| MCP tool server | Expose capabilities over standard protocol | N/A (stateless) | Search API, database, runner |

## Step-by-Step: Building a Planner-Executor with MCP

Here is a concrete path to build a planner-executor agent workflow MCP orchestrator.

**Step 1: Define the MCP tool servers.** Identify the capabilities your executors need and wrap each as an MCP server. Start with the smallest set — a search tool and a code runner are enough for most research and automation tasks. Register each server so both planner and executors can discover it.

**Step 2: Build the executor.** The executor is the simpler agent: it receives a single step, calls the relevant MCP tools, and returns a condensed result. Keep its prompt focused on execution, not strategy. Give it a hard output contract — a short summary, a list of findings, or a status — so the planner can parse it reliably.

**Step 3: Build the planner.** The planner receives the goal, produces an initial plan, and enters a loop: dispatch a step to an executor, read the result, decide whether to proceed, adjust, or re-plan. The planner should be able to spawn multiple executors in parallel for independent steps, mirroring Anthropic's research system where a lead agent spawns parallel subagents to search simultaneously.

**Step 4: Wire the loop.** Connect planner and executors through MCP. The planner calls an executor as if it were a tool, and the executor calls MCP tool servers as its own tools. This keeps the interface uniform: everything is a tool call over MCP.

**Step 5: Add re-planning.** The critical differentiator. When an executor returns a result that invalidates part of the plan, the planner must be able to revise it. Implement a re-plan trigger: after each executor result, the planner evaluates whether the plan still holds and, if not, regenerates the remaining steps.

**Step 6: Test with a real task.** Run the system on an open-ended task — a research question, a multi-step build, a data-analysis job — and observe where it stalls. Most failures come from ambiguous executor output contracts or a planner that re-plans too aggressively.

## Best Practices and Common Pitfalls

**Start simple.** Anthropic's Building Effective Agents explicitly advises starting with the simplest pattern and adding complexity only when needed. Do not build a five-agent system when a single agent with tools suffices. The planner-executor pattern earns its complexity only on open-ended, path-dependent tasks.

**Give executors a strict output contract.** The most common failure is an executor returning unstructured prose the planner cannot act on. Define a schema: findings, status, confidence, next-step suggestions. This makes the planner's decision loop reliable.

**Keep the planner's context clean.** The whole point of executors is compression. If the planner accumulates raw executor output, you lose the benefit. Enforce that executors return condensed summaries, not full transcripts.

**Isolate executor context windows.** Each executor should explore in its own context window. This is what gives you separation of concerns and reduces path dependency. A failure in one executor should not poison another.

**Bound the re-plan loop.** A planner that re-plans on every result can thrash. Add a budget: a maximum number of re-plans, or a confidence threshold below which re-planning is allowed. Otherwise you trade a linear pipeline for an infinite loop.

**Manage MCP server lifecycle.** If you use a framework like mcp-agent, it manages MCP server connections for you. If you build from scratch, handle connection, reconnection, and timeouts explicitly — a dropped tool server is a common silent failure in multi-agent systems.

**Watch for coordination overhead.** Multi-agent systems introduce new challenges in coordination, evaluation, and reliability, as Anthropic notes. Every agent boundary is a place where information is lost or corrupted. Measure whether the added complexity is paying for itself.

## When to Use Planner-Executor vs. Other Agent Patterns

Anthropic's taxonomy gives you a decision ladder. Use the simplest pattern that solves the problem:

| Pattern | Best for | When to reach for planner-executor instead |
|---------|----------|---------------------------------------------|
| Prompt chaining | Fixed, known sequence of steps | When steps depend on intermediate results you cannot predict |
| Routing | Classify input, pick one path | When the task needs multiple cooperating paths, not one |
| Parallelization | Independent subtasks, same input | When subtasks are interdependent and need a coordinator |
| Orchestrator-workers | Decompose into independent subtasks | When the decomposition itself is dynamic and needs re-planning |
| Evaluator-optimizer | Iterate on one output against a judge | When the work is multi-step tool execution, not single-output refinement |
| Planner-executor | Open-ended, path-dependent, tool-heavy tasks | This is the pattern |

Use planner-executor when the full sequence of steps is not known in advance and the work is tool-heavy. Use a simple orchestrator-workers when the decomposition is static. Use a single agent when the task is small enough that orchestration overhead exceeds the benefit.

The rule of thumb from Anthropic and mcp-agent is the same: simple patterns are more robust than complex architectures. Start with the simplest pattern that works, and only graduate to planner-executor when a linear or single-agent approach demonstrably fails on open-ended, path-dependent work.

## FAQ

**What is a planner-executor agent workflow MCP orchestrator?**
It is a multi-agent architecture where a planner agent decomposes a goal into steps, executor agents carry out each step with tool access, and MCP tool servers provide a portable, standard capability layer connecting both roles. The planner can re-plan based on executor results.

**How does MCP help multi-agent orchestration?**
MCP standardizes how agents connect to tools, data, and context. Because both planner and executors consume the same MCP tool servers through one protocol, tool capabilities become portable and reusable across agents and frameworks instead of being locked into one vendor's interface.

**What is the difference between planner-executor and orchestrator-workers?**
Orchestrator-workers decomposes a task into independent subtasks and delegates them to workers. Planner-executor is a specialization that makes the planning loop explicit: the planner observes executor results and can re-plan dynamically, which suits tasks where the step sequence is not known in advance.

**When should I use planner-executor instead of a single agent?**
Use it for open-ended, path-dependent, tool-heavy tasks where a single agent's context window would overflow or where a linear pipeline cannot adapt. For small or fixed tasks, a single agent or a simple chain is more robust and cheaper.

**What are the main pitfalls of the planner-executor pattern?**
The main pitfalls are unstructured executor output the planner cannot parse, planner context bloat from raw results, unbounded re-planning loops, dropped MCP server connections, and coordination overhead that outweighs the benefit. Strict output contracts, isolated executor contexts, and re-plan budgets mitigate these.
