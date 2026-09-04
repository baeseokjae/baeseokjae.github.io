---
title: "dsh trace compare 2026: Visualizing Agent Exploration Paths in DeepSeek Harness"
date: 2026-09-04T13:01:40+00:00
tags:
  - deepseek harness
  - trace compare
  - agent observability
  - dsh trajectory
  - visualization
description: "Learn how to use dsh trace compare in DeepSeek Harness to visualize and compare agent exploration paths, read session events, and debug divergent runs."
draft: false
cover:
  image: "/images/dsh-trace-compare-agent-exploration-2026.png"
  alt: "dsh trace compare: Visualizing Agent Exploration Paths in DeepSeek Harness"
  relative: false
schema: "schema-dsh-trace-compare-agent-exploration-2026"
---

DeepSeek Harness (dsh) records every agent run as a durable series of session events — reasoning deltas, tool calls, tool results, step starts and ends, and turn boundaries — and `dsh trace compare` is the workflow for visualizing and contrasting those exploration paths side by side. Instead of staring at linear chat logs, you render agent execution as a graph (a DAG) where parallel tool calls fan out from a single reasoning step and results fan back in, letting you pinpoint exactly where two runs diverge, stall, retry, or branch. This guide walks you through the session-event format, the native trajectory view, community comparison tools, and the pitfalls to avoid.

## What Is a DeepSeek Harness Trace (and Why Compare Them)?

A dsh trace is the complete, replayable record of everything an agent did during one run, captured as durable session events rather than a flat text transcript. DeepSeek Harness defines the trajectory as its flagship feature: reasoning deltas, text deltas, tool calls, tool results, step start/end, and turn start/end are all persisted as first-class events. This is what makes trace comparison meaningful — because the events are structured, you can align two (or a hundred) runs on the same timeline and ask concrete questions: did both agents pick the same first tool? Did one take a different branch after the third reasoning step? Where did one stall and retry while the other moved on?

Why compare at all? Agent runs are non-deterministic and often parallel; a single successful run tells you almost nothing about whether that path was lucky or repeatable. Comparing exploration paths across runs is how you find divergence, stalls, retries, and branches — the places where behavior degrades or improves. For anyone debugging prompt changes, model swaps, or tool-config edits, trace comparison is the difference between guessing and observing.

## Understanding the DSH Session Event Format (durable trace source of truth)

Every dsh run writes a `session.jsonl` file — one JSON object per line, in chronological order. This file is the single durable source of truth for comparison, because every surface (the Web UI, headless mode, the ACP/SDK, custom UIs, and Hooks) consumes the same event stream. The core event types are documented in the official DeepSeek Harness docs and reused by every community plugin:

| Event type | What it records |
|---|---|
| `reasoning-delta` | Incremental tokens of the model's chain-of-thought |
| `text-delta` | Incremental user-visible text tokens |
| `tool/call` | An outgoing tool invocation with its arguments |
| `tool/result` | The result returned for a tool call |
| `step/start` / `step/end` | Beginning and end of a discrete agent step |
| `turn/start` / `turn/end` | Beginning and end of a full user↔agent turn |

Because these events are timestamped and ordered, two `session.jsonl` files can be diffed structurally. In a comparison workflow you typically export each run's JSONL, align on event type and order, then render differences as an overlay or side-by-side graph. If a tool call fanned out into five parallel calls in run A but only two in run B, that difference shows up immediately as a structural diff in the trace.

## Reading an Agent Exploration Path — Node Types and Flow

To compare paths, you first need to read a single path correctly. Community viewers (notably the DAG-style `dsh-agent-trace` plugin) model agent execution as a graph rather than a line. The core thesis is that "agent execution is a graph, not a line" — parallel tool calls fan out, and their results fan back in. The common node types you will encounter are:

- **Turn** — a full user-to-agent exchange; the outer container.
- **Step** — a discrete reasoning-or-action unit inside a turn.
- **Reasoning** — the model's chain-of-thought for a step.
- **Tool Call** — an outgoing invocation (which may be one of N parallel calls).
- **Result** — the returned tool output that feeds back into the next reasoning step.
- **Response** — the final user-facing output of a turn.

The flow is a DAG: a Reasoning node can spawn multiple parallel Tool Call nodes; each Tool Call produces a Result; Results converge back into the next Reasoning node. When you compare two paths, you are really comparing two DAGs. Look first for structural differences — different out-degree on a Reasoning node (fan-out), different branch after a Result, or an extra Retry cycle that one run suffered. Tools like MiniMap and click-to-expand in the DAG viewer help you zoom in on exactly the divergence region without drowning in a wide trace.

## Native Trajectory View in DSH Web UI (default 127.0.0.1:3080)

DeepSeek Harness ships a Web UI that includes a native trajectory renderer. Install and launch it with:

```bash
npx @deepseek-ai/dsh web
```

The default Web UI is served at `http://127.0.0.1:3080`. Inside it, the trajectory view renders the same session events as a browsable path. You can step through reasoning deltas, expand or collapse tool calls, and see the parallel fan-out of multi-tool steps. The native view is the fastest way to eyeball a single run: it requires no additional plugins, uses the exact official `@deepseek-ai/dsh-session` data model, and respects the same interpretation rules as every other dsh surface.

For comparison specifically, the native view is best as a starting point — it is excellent for single-run inspection but does not itself lay two runs on top of each other. To compare, you export the underlying `session.jsonl` (or use Headless/CLI, covered below) and feed it into a comparison-aware tool. If you are only ever debugging one run, the native view may be all you need.

## Comparing Two Runs Side by Side — Manual and Plugin Workflows

There are two broad ways to compare dsh traces: manual (diff the JSONL / run the same task twice) and plugin-assisted (use a viewer that renders both).

**Manual workflow:** Run the same task twice against the model or config you want to compare. Export both `session.jsonl` files. Diff them line-by-line or, better, normalize each event to a compact structural tuple (`eventType + tool + step index`) and compare the sequences. The places where the sequences diverge are your exploration-path differences. Manual comparison is transparent and dependency-free, but tedious at scale and hard to do visually.

**Plugin workflow:** Use a comparison-aware tool that renders both traces as graphs and lets you align them. The DAG-style viewer and the plain-language `/visual-trace` command are the common choices (details in the next section). These convert the raw event stream into a readable path or graph, highlight pending-review markers, and let you spot divergence visually instead of by eye-diffing JSON.

Whichever you choose, keep the comparison fair: identical model, identical temperature where relevant, identical tools and ordering, and identical task input. The only variable you want to change is the one you are actually testing.

## Community Plugins for Trace Visualization and Comparison

Several community plugins extend dsh trace work beyond the native view. Each takes a slightly different stance on visualization, comparison, and sharing.

**dsh-agent-trace** (goldgish) — the graph-centric DAG viewer. Built on react-flow with dagre auto-layout, it subscribes to durable session events and renders an interactive DAG inside the chat stream, with parallel tool-call fan-out and fan-in. Features include click-to-expand steps, a MiniMap, streaming nodes, and JSON export. Best when you want to think of exploration as a graph.

**dsh-visual-trace** (wikiiizhao) — a cross-surface plain-language trajectory reviewer. It applies the same trace-interpretation rules across Web, headless, ACP/SDK, custom UI, and Hooks. Commands include `/visual-trace`, `/visual-trace markdown`, and `/visual-trace json`, with emoji node types (user/model/tool/system) and pending-review markers. Requires DeepSeek Harness 0.1.0-rc.6 and Node.js `^22.19.0 || >=24.0.0`. Best for turning traces into readable, reviewable summaries.

**dsh-trace-viewer** (li-zhixin) — an offline browser viewer for `session.jsonl`. You drop a file in and nothing is uploaded; it is a static client-only app deployed on Cloudflare Pages, built on `@deepseek-ai/dsh-session`, with a live demo at dsh-trace.lizhixin.top. Best for private, local trace inspection.

**dsh-trace-narrator** (xiangyun0519) — turns trajectory logs into structured reports (summary, postmortem, tutorial, debug, executive) with five built-in schemas, trilingual output (CN/EN/JP), and redaction on by default. Positioned as the "shareable, reusable, teachable" layer on top of dsh trajectories. Best when you need to hand a run to someone else as a report.

## Tool-by-Tool Comparison Table

| Capability | Native DSH Web UI | dsh-agent-trace | dsh-visual-trace | dsh-trace-viewer | dsh-trace-narrator |
|---|---|---|---|---|---|
| Primary view | Trajectory path | Interactive DAG | Plain-language path | Offline browser viewer | Structured report |
| Parallel tool fan-out | Yes | Yes (core thesis) | Yes | Yes | Summarized |
| Side-by-side run compare | Manual | Manual + visual | Command-based | Manual | Report-level |
| Rendering model | Web renderer | react-flow + dagre | Text/emoji | Static client app | Documents |
| Data leaves your machine | No | No | No | No (client-only) | No (redaction on) |
| Best for | Single-run inspection | Graph thinking | Reviewable summaries | Offline privacy | Shareable reports |

## Headless and CLI Trace Workflows for Comparing Runs at Scale

When "compare two runs" becomes "compare fifty runs," the Web UI and manual diffing stop scaling. dsh exposes headless modes and ACP/SDK access that let you run tasks programmatically and collect `session.jsonl` per run without a browser. The comparison pattern at scale is:

1. Script the runs: invoke dsh headless for each configuration you want to compare, capturing one `session.jsonl` per run.
2. Normalize the events into a common comparison schema (event type, tool name, step index, timing).
3. Aggregate and diff programmatically — compute per-run metrics like step count, tool-call count, retry count, and divergence points.
4. Render only the interesting differences (via `/visual-trace json` or a custom emitter) instead of every full trace.

The CLI/`/visual-trace` command path is especially useful here because it emits structured output (`markdown` or `json`) that a script can consume. This turns trace comparison into a repeatable, automated quality gate on your prompt or tooling changes, rather than a manual eyeball exercise.

## Privacy, Redaction, and Sharing Trace Reports

Traces frequently contain sensitive material — user prompts, retrieved documents, API inputs. Before you share or compare traces across a team, decide what can leave the machine. The community has built this in: `dsh-trace-viewer` is client-only (a dropped file is never uploaded), and `dsh-trace-narrator` enables redaction by default and keeps data local while producing shareable reports. The native view and DAG viewer also run locally. The practical rule: keep raw `session.jsonl` private, and share only redacted, summarized, or narrated derivatives. When comparing runs in a review, strip tool arguments and document contents first, then compare the structural path — you can usually diagnose divergence without exposing the underlying payloads.

## Common Pitfalls When Comparing Agent Exploration Paths

- **Comparing apples to oranges.** Different models, temperatures, tool sets, or task inputs make the comparison meaningless. Change only the one variable under test.
- **Relying on a single run.** Agent behavior is stochastic; one divergent path may be noise. Run each configuration several times before concluding.
- **Treating the chat log as the source of truth.** Chat text hides parallel tool calls and reasoning deltas. Compare the structured `session.jsonl`, not the transcript.
- **Ignoring event ordering.** Reasoning, tool calls, and results interleave; a reordering that looks like a divergence in raw text is often just different interleaving of the same events.
- **Forgetting pending-review markers.** Some tools flag steps awaiting review; reading those as finalized divergence will mislead you.
- **Skipping redaction before sharing.** Leaking tool arguments or document contents in a "shareable" trace defeats the purpose of safe review.

## FAQ — dsh trace compare

**What is dsh trace compare?**
dsh trace compare is the workflow of visualizing and contrasting DeepSeek Harness agent runs using their durable session-event traces, so you can see where exploration paths diverge, stall, retry, or branch.

**How do I export a dsh trace to compare runs?**
Each run writes a `session.jsonl` file containing ordered events (reasoning-delta, tool/call, tool/result, step/start/end, turn/start/end). Export that file from each run and diff or render them side by side.

**Which tool is best for comparing dsh traces?**
It depends on your goal: dsh-agent-trace for graph/DAG thinking, dsh-visual-trace for readable reviewable paths and CLI output, dsh-trace-viewer for offline privacy, and dsh-trace-narrator for shareable structured reports. The native Web UI is best for single-run inspection.

**Does dsh trace comparison work headless or at scale?**
Yes. dsh's headless and ACP/SDK modes let you script many runs, capture one `session.jsonl` per run, normalize the events, and diff them programmatically — ideal for automated quality gates.

**Are dsh traces private?**
Raw traces generally stay on your machine. dsh-trace-viewer is client-only (nothing uploaded), and dsh-trace-narrator enables redaction by default. Share only redacted or summarized derivatives.

<｜DSML｜tool_calls>
<｜DSML｜invoke name="terminal">
<｜DSML｜parameter name="command" string="true">python3 -c "
import re
content = open('/home/ubuntu/blog/content/posts/dsh-trace-compare-agent-exploration-2026.md').read()
korean = re.findall(r'[\uAC00-\uD7A3]', content)
if korean:
    print(f'LANGUAGE ERROR: {len(korean)} Korean characters found.')
    import sys; sys.exit(1)
else:
    print('Language check passed: English only.')
"
echo "---WORD COUNT---"
wc -w /home/ubuntu/blog/content/posts/dsh-trace-compare-agent-exploration-2026.md