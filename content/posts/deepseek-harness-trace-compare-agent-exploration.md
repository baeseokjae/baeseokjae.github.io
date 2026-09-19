---
title: "dsh Trace Compare: Visualizing DeepSeek Harness Agent Exploration with dsh-maze"
date: 2026-09-19T16:01:28+00:00
tags: ["DeepSeek Harness", "agent observability", "trace visualization", "dsh-maze", "agent debugging"]
description: "Visualize DeepSeek Harness agent exploration with dsh-maze: see main path, detours, and backtracks on one timeline, compare 2-5 model runs, and debug recovery chains with LLM-free evidence."
draft: false
cover:
    image: "/images/deepseek-harness-trace-compare-agent-exploration.png"
    alt: "dsh Trace Compare: Visualizing DeepSeek Harness Agent Exploration"
    relative: false
schema: "schema-deepseek-harness-trace-compare-agent-exploration"
---

The **dsh trace compare agent exploration** use case is the fastest way to see why a DeepSeek Harness agent does what it does: install the dsh-maze plugin (formerly dsh-trace-compare), load a session log or follow a live run, and you get the agent's full exploration maze — main path, failed detours, and backtracking points — rendered on a single timeline with deterministic, LLM-free analysis you can drill back to the raw commands and outputs. It turns an invisible black-box trajectory into something you can actually read, compare across models, and fix.

## Why visualize an agent's exploration instead of just its answer

Most agent teams can inspect the final output but cannot reliably replay the trajectory behind it. As Arize's guidance on building better agents points out, teams "can inspect the final answer but can't reliably replay the agent's trajectory — that's the gap trace visualization fills." When an agent wanders, takes five detours, or re-tries the same failing tool call three times, none of that shows up in the finished answer. The waste is invisible.

Visualizing exploration solves a different problem than reading output. The final answer tells you *what* the agent produced; the trace tells you *how* it got there — which tool it reached for, what errored, where it backtracked, and how many wasted round-trips it burned before succeeding. For anyone studying how tool surface, context, profiles, or the agent loop affect results, the trajectory is the actual object of study.

The repeatable loop is straightforward: trace the run, create targeted evals, inspect failed spans, decide whether the agent or the evaluator is wrong, then improve the prompt, tools, context, rubric, or evaluator — and run again. None of that works without a trace you can actually read.

## What dsh-trace-compare / dsh-maze is and where it comes from

- **dsh-trace-compare** was the original plugin name. On the Plugin Hub it resolves to version 0.7.0, with 0.6.x and 0.5.x in its history. It visualizes the agent's exploration maze — main path, detours, and backtracks — on one timeline.
- **dsh-maze** is the newer name (from v1.0.0) for the same project, maintained under `lamost423/dsh-maze`. It adds the multi-session comparison, replay, and the honest-verdict engine.

Both belong to the DeepSeek Harness ecosystem. DeepSeek Harness (dsh) is an open-source agent harness built on the Cordis plugin system — "everything is a plugin." Models, tools, skills, sessions, storage, loops, scheduling, and even the UI are all plugins that can be swapped or recomposed. In that philosophy, trace tooling composes *into* the harness as a plugin rather than living only as an external tool.

The project sits at the intersection of two documented truths:

1. **Every run is traceable.** DeepSeek Harness records every run in an append-only session log — system prompts, reasoning, tool calls and results, subagent scheduling, and every context injection. The Trajectory view inspects records by source, and resume, fork, search, and replay all operate on the same event stream.
2. **Trace visibility is a differentiator.** DeepSeek's own material positions trace visibility as a reason harness researchers pick the harness over ready-made coding agents like Codex or Claude Code, which are engineering tools first and study subjects second.

## Installing Trace Compare into DeepSeek Harness (host-compatibility caveat)

The install command is a single `npx` line. From the Plugin Hub listing:

```bash
npx -y @deepseek-ai/dsh plugin --profile web add dsh-trace-compare@0.7.0
```

Or, for newer hosts on the 0.1.2 host line (DSH Desktop 2.x), the maintained name is dsh-maze:

```bash
npx -y @deepseek-ai/dsh plugin --profile web add dsh-maze@2.0.0
```

### The host-compatibility gotcha

The plugin version you choose depends on the host, not just "latest." The compatibility split is explicit:

| Host line | Example | Plugin version required |
|---|---|---|
| host 0.1.2 line | DSH Desktop 2.x | dsh-maze 2.x |
| Older hosts | earlier DSH versions | dsh-maze 1.1.0 (pinned) |

If you are on an older host, do not grab the newest plugin — pin dsh-maze 1.1.0. If you are on the 0.1.2 host line, use dsh-maze 2.x. On the original trace-compare naming, resolving to 0.7.0 covers the same practical surface. The practical migration path is: identify your host line first, then choose the matching plugin, then install.

After install, the runtime surface is web. Launch the harness with `npx @deepseek-ai/dsh web` (opens the Web UI at http://127.0.0.1:3080 by default), and the plugin's tabs appear. Provenance is verified from the release source and the registry is updated.

## Reading the exploration maze: main path, detours, and backtracks on one timeline

Open either the live "realtime maze" tab (which grows as the current session runs) or the sidebar "execution maze" (which takes uploaded session logs), and you get the core visualization: the agent's actual working process drawn as a maze.

Three elements carry most of the meaning:

- **Main path** — the sequence of steps that ended up contributing to the finished result. This is the spine of the run.
- **Detours** — side branches the agent explored that did not make it into the final path. These are the wasted or exploratory moves.
- **Backtracks** — points where the agent reversed course, left a branch, and returned to an earlier position. These are the recovery points.

All three render on one timeline, so you can see at a glance whether a run was clean (short main path, few detours) or thrashy (long main path, many dead-end branches, repeated backtracks).

The value of one timeline is that it answers the question "how much did this agent explore to get here?" in seconds. A two-hour model with a clean maze beats a thirty-minute model that burned twenty failed branches — and now you can actually tell which is which before judging the answer.

## The data tracks: tool-call density, token pulses, context pressure

The exploration maze is not just a path drawing. dsh-maze overlays data tracks that explain *why* the path looks the way it does:

- **Tool-call density** — how often the agent invoked tools per unit of work. High density with detours suggests the agent was reaching for many tools; low density with a straight line suggests it resolved most steps from context or reasoning.
- **Token pulses** — bars distinguishing cached background tokens from uncached input, reasoning, and output tokens. You can literally see when the agent "thought hard" (a reasoning spike) versus when it streamed output.
- **Context pressure curve** — a running curve with 70% and 90% threshold lines plus compression markers. When the pressure crosses a threshold, the harness compresses context; compression events are flagged right on the timeline.

These tracks let you connect cost and context behavior to specific maze events. A backtrack right before a context-pressure compression, for example, tells you the agent may have hit a wall, compressed, and restarted — a distinct failure signature from a clean detour. The context-pressure feature also matters for one of the most common agent problems in 2026: silently degraded performance when long context forces mid-run compression. Seeing the compression markers on the timeline is the difference between "the agent randomly got worse" and "the agent compressed context at step 40 and never fully recovered."

## Execution analysis and failure-recovery chains (with drill-down to raw evidence)

Beyond the maze, dsh-maze performs execution analysis that classifies how the agent recovered from failures. The core concept is the **failure-recovery chain**, classified into a small set of patterns:

| Recovery type | What it looks like |
|---|---|
| Retry-as-is | Same tool, same parameters, tried again |
| Change-param | Same tool, different parameters |
| Change-tool | Switched to a different tool |
| Not recovered | The failure was never resolved before the run ended |

Two additional analysis surfaces:

- **Tool result matrix** — a grid of which tools returned success, error, or empty results, so you can spot chronically failing tools at a glance.
- **Duration P50/P95 scatter** — per-step latency distribution, revealing slow tools or slow steps that inflate run time.

The crucial honesty property: **every conclusion drills back to the original command and returned content.** Nothing is shown as an unexplained score. If the analysis says "change-param recovery," you can click through to the actual failing command and the error it returned. That evidential chain is what separates useful trace analysis from a dashboard of vibes.

## Comparing 2-5 agent runs on different models (round alignment, anchors, detour inventory)

Single-run analysis points at a problem. Multi-run comparison makes it benchmark-style: run the same task 2-5 times on different models and align them on one axis.

The comparison surface provides:

- **Round alignment** — automatic alignment of corresponding work rounds across runs, so you compare step-for-step rather than wall-clock-vs-wall-clock.
- **Manual anchors** — you can pin anchor points (e.g., "the point where the agent first fetched the docs") so that alignment lines up on the moments you care about.
- **Per-round detour inventory** — for each round, a list of the detours each model took, making wasted exploration comparable.

This is the "dsh trace compare" in practice: put Model A and Model B on the same task, and you instantly see that A plowed straight through while B took four detours and two backtracks. Add a third model and you start seeing systematic behavior — maybe every model that lacks a particular tool bounces between two workarounds, which is a tool-surface problem, not a model-quality problem.

## How session logs make every run replayable and verifiable

DeepSeek Harness records every run in an **append-only session log**. Everything the model sees is in there: system prompts, reasoning, tool calls and results, subagent scheduling, and every context injection. Nothing is cherry-picked afterwards; the record exists before you decide what to analyze.

That log foundation powers dsh-maze's inputs. It supports **plain .jsonl and .jsonl.zstd** session logs, auto-detected by content. The zstd logs decompress browser-side via the native `DecompressionStream` or the fzstd fallback — no server-side decode step needed.

Two more properties make logs genuinely verifiable rather than merely inspectable:

- **Replay up to 300x.** You can replay a run at up to 300× speed, with idle folding so silent stretches collapse instead of stretching the timeline. This makes "watch the whole session" feasible even for long runs.
- **Deterministic, LLM-free aggregation.** All numbers in the analysis are computed deterministically from the log. The analysis engine makes no LLM calls, so the verdicts cannot hallucinate; a number is either in the log or it is not.

This matters for trust. Many trace tools summarize trajectories with an LLM, which means the summary can be wrong in the same way the agent's output can be wrong. dsh-maze deliberately avoids that: the evidence is the log, and the analysis is arithmetic on the log.

## Limitations and honest-verdict rules (LLM-free determinism, missing-data fallbacks)

The honesty posture is explicit, and it is worth listing the rules because they tell you where the tool can be trusted and where it cannot:

- **Never judge by output length.** A long stream of output is not good work; the tool deliberately refuses to score quality by token volume.
- **Error features are scanned only at head/tail windows.** Rather than over-indexing on an error buried mid-run, error features are evaluated only at the head and tail windows of each step, a conservative choice that avoids false positives.
- **Three-layered single-tool judgment** — `isError` flag → failure signature → tool classification. A call is only labeled a failure if it clears successively stricter layers.
- **"Blind retry" as behavioral detection** — consecutive same-tool plus similar-parameter calls with at least one failure. This is inspired by AgentLens's deterministic detection of SWE-agent trajectory waste, and it is deliberately *not* an LLM judgment about intent.
- **Honest fallback for missing data.** When usage or token data is absent from the log, the tool falls back instead of fabricating. No invented numbers.

What this buys you is reproducibility: two people analyzing the same log get the same verdict. The LLM-free determinism is the differentiator.

## When trace visualization belongs in your harness (observability as a plugin)

The final design question is where observability should live. The Arize guidance is direct: "Make observability part of the harness; trace every step (data fetched, tool calls, LLM calls, intermediate outputs) before writing serious evals."

dsh-maze embodies the opposite philosophy to bolting on an external viewer: it is a **plugin in the harness itself**, following the everything-is-a-plugin model. The trace tool has the same standing as any other capability — installed, composable, and swappable like the models, tools, and sessions it observes.

That has a practical consequence for teams evaluating DeepSeek Harness. If your research question is about the agent loop — how tool surface, context windows, profiles, or scheduling change results — trace visualization is not a nice-to-have; it is the instrument. The harness's built-in append-only session log plus a maze-style viewer turns an agent run from a one-way black box into a repeatable experiment you can align, replay, and diff against other models.

## FAQ / common pitfalls

**How do I install dsh-trace-compare / dsh-maze?**
Run `npx -y @deepseek-ai/dsh plugin --profile web add dsh-maze@<version>` (the original name was `dsh-trace-compare@0.7.0`). Do not guess the version — check your host line first (see the compatibility table above).

**What's the difference between dsh-trace-compare and dsh-maze?**
Same project, renamed. dsh-trace-compare was the original name (resolving to 0.7.0); dsh-maze is the name from v1.0.0 onward, adding multi-run comparison, replay, and the deterministic verdict engine.

**Which plugin version do I need?**
It depends on the host. Host 0.1.2 line (DSH Desktop 2.x) uses dsh-maze 2.x; older hosts pin dsh-maze 1.1.0. Choosing the wrong one is the most common install failure.

**What session log formats does it accept?**
Plain `.jsonl` and `.jsonl.zstd`, auto-detected by content. Zstd decompresses browser-side (native DecompressionStream or fzstd).

**Are the analysis verdicts computed by an LLM?**
No. Every number is a deterministic aggregation of the log; the engine makes no LLM calls. If it says a recovery was a "change-param," the evidence is in the underlying command and result, and you can drill down to it.

**Should trace visualization replace eval suites?**
No — it complements evals. Trace first, build targeted evals from the failures you see, then debug and refine the prompt, tools, context, or evaluator. The loop keeps running.
