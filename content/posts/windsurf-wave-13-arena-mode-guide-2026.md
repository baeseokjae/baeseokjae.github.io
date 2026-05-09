---
title: "Windsurf Wave 13 Guide: Arena Mode, Plan Mode and SWE-1.5 (2026)"
date: 2026-05-09T03:05:17+00:00
tags: ["windsurf", "ai-ide", "wave-13", "wave-14", "swe-1.5", "arena-mode", "plan-mode", "parallel-agents"]
description: "Complete guide to Windsurf Wave 13 and Wave 14 features: SWE-1.5 free model, parallel Git worktree agents, Arena Mode, and Plan Mode."
draft: false
cover:
  image: "/images/windsurf-wave-13-arena-mode-guide-2026.png"
  alt: "Windsurf Wave 13 Guide: Arena Mode, Plan Mode and SWE-1.5"
  relative: false
schema: "schema-windsurf-wave-13-arena-mode-guide-2026"
---

Windsurf Wave 13 (the "Shipmas Edition," released December 24, 2025) introduced three production-ready capabilities that reshaped the AI IDE landscape: the SWE-1.5 model free for all users, true parallel agents running in isolated Git worktrees, and a dedicated Cascade terminal with interactive zsh support. Wave 14 followed with Arena Mode for blind model comparison and Plan Mode for structured task planning. Together, these two releases represent the largest capability jump Windsurf has shipped to date.

## What Is Windsurf Wave 13? (Shipmas Edition Overview)

Windsurf Wave 13 is a major update to the Windsurf AI IDE released on December 24, 2025, under the name "Shipmas Edition." It delivered four headline features simultaneously: SWE-1.5 as the free default model, true parallel Cascade agents backed by Git worktrees (up to 5 simultaneous sessions), a dedicated Cascade terminal with interactive zsh support on macOS, and a real-time context window indicator with prompt cache timer. Before Wave 13, running multiple Cascade agents meant working in the same directory, creating file conflicts and unpredictable merge states. Wave 13 eliminated that problem entirely by giving each agent its own isolated working directory backed by a separate Git branch. The release positioned Windsurf as the strongest alternative to Cursor in early 2026, particularly for developers who need to parallelize long-running agentic tasks. Wave 14, released in April/May 2026, built on this foundation by adding Arena Mode (blind model head-to-head comparison) and Plan Mode (structured planning before code execution).

## SWE-1.5: Windsurf's Free Frontier Coding Model

SWE-1.5 is Windsurf's proprietary coding model, achieving 40.08% accuracy on SWE-Bench-Pro — a real-world benchmark of GitHub issue resolution — matching Claude Sonnet 3.5-level performance on actual software engineering tasks. It runs at approximately 950 tokens per second, which is 13–14x faster than Claude Sonnet 4.5 at comparable capability levels. For the three months following Wave 13's release (through March 2026), SWE-1.5 was free for all Windsurf users and set as the default Cascade model. This eliminated the credit-drain concern that had previously made power users hesitant to use frontier models on exploratory tasks. SWE-1.5 is optimized specifically for code generation, bug fixing, and agentic tool-use workflows — not general reasoning. For tasks requiring broad contextual understanding or non-coding domains, Claude Opus 4.6 or GPT-5.4 remain stronger choices. On the Fast Arena leaderboard (May 2026), SWE-1.5 ranks first among speed-optimized models, above Haiku 4.5 and Gemini 3 Flash Low.

### Why SWE-1.5 Speed Matters for Parallel Agents

When running 5 parallel Cascade agents, model latency compounds. At 950 tokens/second, SWE-1.5 completes typical coding subtasks in seconds rather than tens of seconds — making the parallel agent workflow feel genuinely snappy rather than a monitoring exercise.

### How to Select SWE-1.5 in Cascade

Open a Cascade chat, click the model selector in the top-right corner, and choose `SWE-1.5`. If you're on a plan with quota limits, monitor usage via the new context window indicator. SWE-1.5 consumes fewer credits than frontier models, so it's a cost-effective default for most coding tasks.

## True Parallel Agents with Git Worktrees

Wave 13's parallel agent feature is the most structurally significant capability Windsurf has shipped. It allows developers to run up to 5 Cascade agents simultaneously, each operating in its own isolated Git worktree — a separate directory that shares the same repository history but maintains an independent working tree and branch. Before this feature existed, running two agents on the same codebase risked file conflicts when both attempted to modify overlapping files. With Git worktrees, each agent works on its own branch (e.g., `feature/auth-refactor`, `feature/api-v2-migration`) and conflicts only surface at intentional merge time. This matches how senior engineering teams actually structure parallel work: independent branches, deliberate integration. The multi-pane Cascade interface lets you monitor all 5 agents in a single view, with each panel showing the agent's current task, tool calls in progress, and branch status. This is the first commercial IDE feature that genuinely enables autonomous multi-task parallel coding at a production-useful scale.

### Setting Up Git Worktrees in Windsurf

Git worktrees are created automatically when you launch a parallel Cascade agent. You don't need to run `git worktree add` manually. In the Cascade panel, click the **+ New Agent** button (or the parallel agent icon in the top-right), assign a task description, and Windsurf creates the worktree and branch in the background. Each agent panel shows the active branch name so you always know where changes are landing.

### When to Use Parallel Agents vs a Single Agent

Use parallel agents when tasks are genuinely independent: separate features, independent bug fixes across different modules, or test suite generation for isolated components. Avoid parallel agents for tasks with shared state — two agents modifying the same config file or database migration sequence will create conflicts at merge time regardless of worktree isolation.

## Wave 14 Continuation: Arena Mode and Plan Mode

Wave 14, released in April/May 2026, extended the Wave 13 foundation with two new Cascade modes: Arena Mode and Plan Mode. Arena Mode enables blind head-to-head comparison of AI models using an Elo rating system — developers submit a prompt and two models respond in parallel, with identities hidden until the user votes on the better response. Plan Mode introduces a structured planning phase before code execution, letting developers review and edit a task plan before Cascade begins making file changes. Together, these additions address two persistent frustrations in AI-assisted coding: uncertainty about which model to use for a given task, and the loss of control when an agent immediately starts modifying files without showing its reasoning first. Wave 14 features were initially free for one week after launch and then became part of the standard Pro and advanced tier quotas.

## Arena Mode — Blind Head-to-Head Model Comparison

Arena Mode is a Windsurf Cascade feature that runs two AI models simultaneously on the same prompt, hides their identities during response generation, and asks the developer to vote on which response is better. Votes feed into a personal Elo leaderboard and a global Windsurf Elo ranking — structurally similar to the chess rating system used by FIDE. According to the May 2026 Windsurf Arena leaderboard, the Frontier Arena top models are Opus 4.6, Opus 4.5, and Sonnet 4.5; the Fast Arena leaders are SWE-1.5, Haiku 4.5, and Gemini 3 Flash Low. Arena Mode supports up to 5 models for expanded comparison sets. Credits are consumed based on the models selected, not the number of rounds. Arena Mode is particularly useful for establishing personal calibration: most developers find their intuitions about "which model is best" are significantly revised after 20–30 real Arena votes on their own actual tasks.

### Arena Battle Groups Explained

Windsurf organizes Arena Mode into three battle groups:

- **Frontier Arena**: Highest-capability models (Opus 4.6, GPT-5.4, Gemini 2 Ultra). Best for complex reasoning, architecture decisions, and multi-file refactors.
- **Fast Arena**: Speed-optimized models (SWE-1.5, Haiku 4.5, Gemini 3 Flash Low). Best for autocomplete, small bug fixes, and test generation where latency matters.
- **Hybrid Arena**: Mixed-tier comparisons for developers calibrating cost vs. capability tradeoffs.

### How to Enable Arena Mode

In Cascade, click the **Arena** icon in the model selector dropdown. Select your battle group, choose up to 5 models to include in the rotation, and submit a prompt. Two models respond in parallel. Review both responses — model identities are hidden behind Model A/B labels — then click **Vote** on the better response. After voting, identities are revealed and your vote updates both your personal leaderboard and the global ranking.

## Plan Mode — Think Before You Code

Plan Mode is a Windsurf Cascade feature that inserts a structured planning phase between task input and code execution. When Plan Mode is active, Cascade generates a step-by-step implementation plan — including which files it will modify, what logic changes it will make, and the expected sequence of actions — before writing a single line of code. The developer reviews this plan, can edit it directly, and only then triggers execution. This addresses the most common complaint about agentic coding: agents immediately start making changes without showing their work, making it difficult to course-correct before damage is done. Plan Mode adds a friction-by-design checkpoint that mirrors how senior engineers actually work — think first, code second. For extra-thorough planning on complex tasks, Windsurf added a **megaplan** shortcut (accessible via `/megaplan` in the Cascade input) that generates more detailed sub-task breakdowns before execution.

### When Plan Mode Saves You Time

Plan Mode is most valuable for: large refactors across multiple files, database schema migrations, API breaking changes, or any task where a wrong first step cascades into significant rework. For small bug fixes or autocomplete-style tasks, Plan Mode adds unnecessary latency — disable it and use standard Cascade for quick edits.

### Enabling and Disabling Plan Mode

Toggle Plan Mode in the Cascade toolbar using the **Plan** button (or via `Cmd+Shift+P` on macOS). When enabled, Cascade displays a plan card before execution. You can approve the plan as-is, edit individual steps, or reject it and re-describe the task to generate a different plan. The plan card is not read-only: click any step to modify the approach before committing to execution.

## Windsurf vs Cursor in 2026: How Wave 13/14 Changes the Race

The competitive dynamic between Windsurf and Cursor shifted significantly with Wave 13 and 14. Cursor's core strength remains its VS Code-native integration and the Tab autocomplete model, which has no direct Windsurf equivalent. Windsurf's Wave 13/14 advantages are: broader IDE support (40+ IDE plugins vs. Cursor's VS Code-only focus), parallel agents with true Git worktree isolation (Cursor's parallel features share the same working directory), Arena Mode for data-driven model selection (no Cursor equivalent), and Plan Mode for pre-execution review (Cursor's equivalent is less structured). On pricing, Windsurf shifted from credit-based to flat quota tiers in March 2026 ($20/month basic, $40/month Pro with Claude Opus 4.6 and GPT-5.4 access, $200/month enterprise). Cursor's pricing remained credit-anchored through early 2026, making cost-per-task comparisons favor Windsurf for heavy parallel agent workflows. The strategic divide is depth vs. breadth: Cursor dominates VS Code, Windsurf runs everywhere. For solo developers on VS Code, the choice remains close. For teams using JetBrains, Neovim, or mixed editor environments, Windsurf's breadth makes it the practical default.

## How to Get Started with All Wave 13 and Wave 14 Features

Getting access to all Wave 13 and Wave 14 features requires Windsurf version 1.13 or later. Update via the in-app notification or by downloading the latest build from windsurf.com. After updating:

1. **Enable SWE-1.5**: Open Cascade → Model selector → Choose `SWE-1.5`. No additional configuration needed.
2. **Launch parallel agents**: In the Cascade panel header, click **+ Agent**. Assign a task. Windsurf creates a Git worktree automatically. Repeat for additional agents (up to 5).
3. **Monitor via multi-pane view**: Use the split-pane button in the Cascade toolbar to display all active agents side by side.
4. **Enable dedicated terminal**: In Preferences → Cascade → Terminal, toggle **Use Dedicated Cascade Terminal (Beta)**. This uses an interactive zsh session and sources your `.zshrc`, fixing environment variable issues in shell-heavy workflows.
5. **Try Arena Mode**: Click the model selector → Arena → Select battle group → Submit a prompt and vote.
6. **Enable Plan Mode**: Click the **Plan** toggle in the Cascade toolbar before submitting complex tasks.
7. **Check context window**: The indicator appears in the bottom of each Cascade panel. When usage exceeds 80%, consider starting a new conversation to avoid context degradation.

## Should You Switch to Windsurf in 2026?

Windsurf Wave 13 and Wave 14 make it the strongest AI IDE for teams running parallel agentic workflows, developers who work across multiple editor environments, and anyone who wants data-driven model selection via Arena Mode rather than relying on benchmark marketing. The SWE-1.5 model free period democratized frontier AI coding assistance in a way that meaningfully differentiated Windsurf from Cursor during Q1 2026. Plan Mode addresses a real workflow problem — agents that act before thinking — without adding prohibitive friction. The weakest argument for Windsurf is for developers who are deeply invested in VS Code's extension ecosystem and rely heavily on Tab autocomplete, where Cursor's integration remains tighter. The strongest argument for Windsurf is running 5 parallel agents on a large codebase refactor without file conflicts — a capability that has no production-equivalent in any other AI IDE as of May 2026. For most professional developers doing serious multi-task AI-assisted work, Wave 13/14 represents a genuinely persuasive upgrade path.

## FAQ

**What is Windsurf Wave 13?**
Windsurf Wave 13 (Shipmas Edition) is a major AI IDE update released December 24, 2025, introducing SWE-1.5 as a free default model, true parallel agents with Git worktree isolation (up to 5 simultaneously), a dedicated zsh Cascade terminal, and a real-time context window indicator.

**What is Arena Mode in Windsurf?**
Arena Mode is a Windsurf Cascade feature that runs two AI models simultaneously on the same prompt with hidden identities. After both respond, you vote on the better output, feeding a personal and global Elo leaderboard — enabling data-driven model selection over relying on marketing benchmarks.

**What is Plan Mode in Windsurf?**
Plan Mode is a Windsurf Cascade feature that generates a step-by-step implementation plan before executing any code changes. Developers review, edit, or reject the plan before Cascade begins modifying files — preventing premature or misdirected changes on complex tasks.

**How fast is SWE-1.5?**
SWE-1.5 runs at approximately 950 tokens per second, making it 13–14x faster than Claude Sonnet 4.5. It achieves 40.08% accuracy on SWE-Bench-Pro, positioning it at Claude Sonnet 3.5-level capability for real-world software engineering tasks.

**How does Windsurf compare to Cursor in 2026?**
Windsurf leads in multi-agent parallel workflows (Git worktree isolation, up to 5 agents), IDE breadth (40+ plugins vs. VS Code only), Arena Mode for model benchmarking, and flat quota pricing. Cursor leads in VS Code-native depth and Tab autocomplete quality. For solo VS Code developers, the choice is close. For teams or mixed-editor environments, Windsurf's breadth wins.
