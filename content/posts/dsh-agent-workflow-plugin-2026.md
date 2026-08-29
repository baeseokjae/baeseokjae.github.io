---
title: "DeepSeek Harness Agent Workflow Plugin: Orchestrate Multi-Step Agent Runs"
date: 2026-08-29T16:01:16+00:00
tags:
  - deepseek harness
  - deepseek harness plugin
  - agent workflow
  - dsh plugin
  - agent orchestration
  - workflow visualization
description: "The DeepSeek Harness Agent Workflow plugin visualizes multi-step agent runs as an execution chain, with token and cache stats for context-reuse analysis."
draft: false
cover:
  image: "/images/dsh-agent-workflow-plugin-2026.png"
  alt: "DeepSeek Harness Agent Workflow Plugin: Orchestrate Multi-Step Agent Runs"
  relative: false
schema: "schema-dsh-agent-workflow-plugin-2026"
---

The DeepSeek Harness Agent Workflow plugin (dsh-plugin-agent-workflow) is a standalone, installable Web UI plugin that adds a dedicated "Workflow" tab to DeepSeek Harness, letting you orchestrate and inspect multi-step agent runs as a clear execution chain. It renders your real recorded Session events — model requests, model responses, and tool calls — in chronological order, split by user conversation turn, with token and cache statistics that reveal exactly how context is reused across steps. Because it is read-only and non-invasive, it never adds messages, prompts, or tools to your requests, making it a trustworthy observability layer for anyone running complex, multi-step agent workflows on DeepSeek Harness.

## What is DeepSeek Harness and the "Everything is a Plugin" philosophy?

DeepSeek Harness (dsh) is DeepSeek's open-source agent harness, currently in developer preview at version 0.1.0-rc.x. The project has roughly 203,000 GitHub stars, and its defining architectural idea is that "everything is a plugin." Every capability — models, tools, skills, sessions, sandboxes, storage, loops, scheduling, and even the UI itself — is a swappable, recomposable plugin built on the Cordis kernel, which manages plugin mounting, unmounting, and dependencies.

The conceptual shift is significant compared to other harnesses. There is no separate manifest format per capability type; one plugin mechanism covers everything. A plugin is simply a JavaScript or TypeScript module that exports `apply(ctx, config)`. What that plugin registers determines what it becomes:

- `ctx.tools.register()` makes it a tool
- `ctx.commands` makes it a slash command
- A prompt section plus a tool makes it a skill
- One plugin per MCP server connects an MCP server
- A listener on `agent/pre-step` or `tools/pre-execute` makes it a lifecycle hook
- `ctx.llm.registerAdapter()` adds a new LLM provider
- `ctx.jobs` adds a background or cron job

This means skills, commands, and MCP connections are all just code that calls `ctx`. The Agent Workflow plugin fits squarely into this philosophy: it is a UI plugin that registers a new tab and reads the session event stream to give you a visual, chronological view of your agent runs.

## Introducing the Agent Workflow plugin (dsh-plugin-agent-workflow)

The dsh-plugin-agent-workflow plugin, developed by xuanyuanzhifeng, is a standalone installable DeepSeek Harness Web UI plugin that adds a "Workflow" tab alongside the built-in "Conversation" and "Trajectory" tabs. It has roughly 126 GitHub stars, is written in TypeScript, and is MIT-licensed.

Its core purpose is to make multi-step agent runs legible. Instead of forcing you to read raw logs or reconstruct what happened from a flat conversation, the plugin uses your user conversation turns as the entry point and renders model requests, model responses, and tool calls as a clear execution chain. The left panel organizes tasks by user conversation turn; the right panel shows model and tool calls chronologically; and the top summarizes counts and total time for the whole run.

The plugin is deliberately read-only and non-invasive. It visualizes real recorded Session events and never re-infers behavior from Harness source code. It adds no messages, prompts, or tools to your requests, which makes it a trust and observability layer rather than an active orchestrator. If you want to understand what your agent actually did across a long, multi-step run, this plugin gives you the ground truth.

## How the Workflow tab visualizes multi-step agent runs

The Workflow tab is organized around a two-panel layout that mirrors how you actually think about a run. On the left, tasks are grouped by user conversation turn — each turn is a distinct unit of work. On the right, the model and tool calls for the selected turn appear in chronological order. At the top of the view, a summary bar shows counts and total time, giving you an at-a-glance sense of how long the run took and how many steps it involved.

This structure is especially valuable for multi-step agent runs, where a single user request can trigger a long chain of reasoning, tool calls, subagent scheduling, and context injections. By grouping work by turn and then by call, the plugin lets you trace exactly which model call produced which tool call, and in what order. Independent scrolling for the turn list and the model-call list means you can keep a long chain in view while inspecting a specific step, and virtualized rendering keeps the interface responsive even for very long chains.

Because the data comes from real recorded Session events, the view is always accurate. DeepSeek Harness records everything the model sees in an append-only session log — system prompts, reasoning, tool calls and results, subagent scheduling, and context injections — and the Workflow tab reads that same event stream. You are never looking at a reconstruction; you are looking at the actual execution trace.

## Inspecting model requests, responses, and tool execution in detail

Beyond the high-level chain, the plugin lets you drill into each individual step. Request details expose the real recorded system prompt, the provider-agnostic `messages[]` body, and the tool definitions as collapsible JSON trees with copy and zoom controls. This is useful when you need to verify exactly what context was sent to the model at a given step, or when you are debugging why a tool call was malformed.

Response inspection shows the reasoning, content, tool calls, and raw records for each model response. Tool execution states distinguish running, completed, and failed steps, and each tool call shows its parameters, results, duration, and an error summary when something went wrong. This makes it straightforward to spot a slow tool, a failed call, or a step where the model's reasoning diverged from what you expected.

For a multi-step agent run, this level of detail is the difference between guessing and knowing. When a run fails or produces an unexpected result, you can open the Workflow tab, find the exact step where things went sideways, and inspect the request, the response, and the tool execution state in one place.

## Token and cache statistics for context-reuse analysis

One of the most practical features of the Agent Workflow plugin is its token and cache statistics. For each step, the plugin splits token usage into input, uncached input, cache-read, cache-write, and output tokens. This breakdown is essential for context-reuse and cost analysis.

DeepSeek's pricing model rewards context reuse: tokens read from cache are dramatically cheaper than uncached input tokens. By seeing how many tokens were cache-read versus uncached input, you can tell whether your workflow is actually reusing context effectively across steps. A high cache-read ratio means your agent is building on prior context efficiently; a high uncached-input ratio suggests you are re-sending context that could be cached or trimmed.

This is particularly relevant for multi-step agent runs, where context accumulates across turns. The plugin's per-step breakdown lets you identify which steps are the most expensive, whether context is being reused as intended, and where you might restructure your workflow to improve cache hits and reduce cost.

## Installing the plugin (local .tgz and GitHub install paths)

Installing the Agent Workflow plugin follows the standard DeepSeek Harness plugin workflow. The plugin is compatible only with dsh@0.1.0-rc.8 (0.1.x), so you must be on that version. You can install from a local `.tgz` package or directly from GitHub:

```bash
npx @deepseek-ai/dsh@0.1.0-rc.8 plugin --profile web add <path-to.tgz> --workspace-root
```

or, for a GitHub install pinned to a release tag:

```bash
npx @deepseek-ai/dsh@0.1.0-rc.8 plugin --profile web add github:<owner>/<repo>#v0.1.1 --workspace-root
```

To remove the plugin, use `plugin remove`. The broader ecosystem uses a similar pattern — for example, the independent DSH Plugin Registry (dshplugin.app) documents installs as `dsh plugin --profile web add github:<owner>/<repo>`. Because DSH is pre-release, always pin your plugin version to the matching RC version of the harness.

## Compatibility, versioning, and known limitations

The most important thing to understand about the Agent Workflow plugin is that it is compatible only with dsh@0.1.0-rc.8 (0.1.x). DeepSeek Harness is pre-release, which means client interfaces can change across RC versions. A plugin built against one RC may break on the next, so you must track plugin versions against your harness version.

The plugin is also read-only by design. It does not orchestrate agent runs; it visualizes them. If you need active orchestration — assigning work, managing dependencies, or running multi-model teams — you will want a different tool (see the comparison below). And because it reads the session event stream, its fidelity depends on the harness recording those events correctly, which is a core DeepSeek Harness guarantee but still worth noting for pre-release software.

## How it compares to other DeepSeek Harness workflow plugins

The DeepSeek Harness plugin ecosystem has several workflow-oriented tools, and they serve different purposes. Here is how the main ones compare:

| Plugin | Primary purpose | Stars | Language | License |
|--------|----------------|-------|----------|---------|
| dsh-plugin-agent-workflow | Per-turn execution chain visualization, read-only | ~126 | TypeScript | MIT |
| dsh-agent-team-gui | Persistent multi-model agent teams with orchestration | ~159 | TypeScript | MIT |
| dsh-harness-one | Visual multi-agent DAG orchestrator with live execution | ~17 | JavaScript | — |

The Agent Workflow plugin is the observability choice: it shows you what happened, step by step, with token and cache stats. The dsh-agent-team-gui plugin is the orchestration choice: it lets you build persistent, reusable multi-model teams where each member gets its own model, role, fallback route, token limit, and tool policy, with dynamic workflow planning and bounded DAG execution. The dsh-harness-one plugin is a visual AI workflow orchestrator that builds multi-agent DAGs with live execution, recovery, and Feishu integration.

If your goal is to understand and optimize a single agent's multi-step run, the Agent Workflow plugin is the right fit. If your goal is to coordinate multiple specialized agents, look at dsh-agent-team-gui or dsh-harness-one. Many teams use both: an orchestrator to run the work, and the Workflow tab to inspect and optimize it.

## Local development and packaging (pnpm, typecheck, test, pack)

If you want to build or modify the plugin yourself, the development workflow is standard for a TypeScript plugin. The project requires Node ^22.19.0 or >=24.0.0 and pnpm 11. The typical loop is:

```bash
pnpm install
pnpm typecheck
pnpm test
pnpm pack
```

`pnpm pack` produces the `.tgz` file you can install with the `plugin add` command. Because the plugin is MIT-licensed and open source, you can fork it, adjust the visualization to your needs, and repackage it for your own workspace. The same "everything is a plugin" philosophy means your modifications remain a self-contained plugin rather than a fork of the harness itself.

## FAQ and troubleshooting

**Is the DeepSeek Harness Agent Workflow plugin read-only?**
Yes. It visualizes real recorded Session events and adds no messages, prompts, or tools to your model requests. It is a pure observability layer, so it cannot alter the behavior of your agent runs.

**Which version of DeepSeek Harness does the plugin require?**
The plugin is compatible only with dsh@0.1.0-rc.8 (0.1.x). Because DeepSeek Harness is pre-release, client interfaces may change across RC versions, so you must match the plugin version to your harness version.

**How is the Workflow tab different from the built-in Trajectory tab?**
The Trajectory tab inspects the session log by source, while the Workflow tab organizes the same event stream by user conversation turn and renders model requests, responses, and tool calls as a chronological execution chain with token and cache statistics.

**Can the plugin help me reduce token costs?**
Yes. It splits token usage into input, uncached input, cache-read, cache-write, and output tokens per step, so you can identify where context is not being reused and restructure your workflow to improve cache hits and lower cost.

**Does the plugin orchestrate multi-agent teams?**
No. It visualizes and inspects runs. For active orchestration of multi-model teams, use a tool like dsh-agent-team-gui or dsh-harness-one, which handle team composition, dependency planning, and DAG execution.
