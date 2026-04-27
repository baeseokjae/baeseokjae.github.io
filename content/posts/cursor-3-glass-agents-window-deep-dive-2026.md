---
title: "Cursor 3 Agents Window Guide: Glass Interface, Design Mode, and Worktrees Explained"
date: 2026-04-27T09:03:54+00:00
tags: ["Cursor", "AI IDE", "Agents Window", "Cursor 3", "developer tools"]
description: "A complete guide to Cursor 3 Glass — covering the Agents Window, Design Mode, and Worktrees for parallel agent-first development in 2026."
draft: false
cover:
  image: "/images/cursor-3-glass-agents-window-deep-dive-2026.png"
  alt: "Cursor 3 Agents Window Guide: Glass Interface, Design Mode, and Worktrees Explained"
  relative: false
schema: "schema-cursor-3-glass-agents-window-deep-dive-2026"
---

Cursor 3 Glass is a full rebuild of the Cursor IDE interface around agent orchestration — not just code editing. Released April 2, 2026, it lets you run dozens of parallel agents across multiple repos and branches, annotate UI elements directly in a browser with Design Mode, and isolate background tasks in Worktrees, all from a single unified window.

## What Is Cursor 3 Glass? The Agent-First Interface Explained

Cursor 3 Glass is the fourth-generation interface of the Cursor AI IDE, developed under the internal codename "Glass" and released on April 2, 2026. It represents a fundamental architectural shift: rather than treating AI assistance as a side panel to your editor, Glass positions the developer as an agent orchestrator — a conductor who dispatches, monitors, and steers multiple AI agents working in parallel. By February 2026, Cursor had already crossed $2B ARR and over 1 million daily active users, with roughly 2 in 3 Fortune 500 companies on the platform. Glass is Anysphere's answer to that scale: enterprise teams need to parallelize engineering work, not just autocomplete individual lines. The central bet is that developers in 2026 spend more time orchestrating agents than editing code. Glass makes that orchestration first-class — with a dedicated Agents Window, a visual Design Mode, and deep Git Worktrees integration — rather than an afterthought bolted onto a text editor. If you've used Cursor 2.x and found yourself manually juggling multiple Composer sessions, Glass is the upgrade that consolidates that workflow into a coherent, observable interface.

## The Agents Window: Running Parallel Agents Across Repos and Environments

The Agents Window is Cursor 3 Glass's primary interface for managing concurrent AI agents — a mission-control panel where you can launch, monitor, pause, and cancel any number of agents operating simultaneously across different repositories, branches, and environments. Unlike the older Composer approach (one active session at a time), the Agents Window treats each task as an independent agent with its own context, toolset, and lifecycle. You can assign one agent to write a new API endpoint while another runs a test suite on a different branch and a third handles a database migration in a staging environment — all visible in a single scrollable panel. Each agent card shows its current status (running, waiting, blocked, done), the files it has modified, and a token-level cost estimate. Clicking into any card opens a full conversation thread so you can inspect reasoning, override decisions, or inject new instructions mid-run. As of the April 24, 2026 update, the Agents Window also supports multi-root workspaces, so a single pane can span agents working across completely separate repositories in one orchestration view.

## How to Set Up and Launch the Agents Window (Step-by-Step)

Setting up the Agents Window in Cursor 3 Glass takes under two minutes for most projects and requires no additional configuration beyond installing Cursor 3 (version 0.47 or later). The Agents Window is enabled by default on all plans — Free, Pro, and Business — with the main difference being the number of simultaneous agents allowed: Free supports 2 concurrent agents, Pro supports 10, and Business supports unlimited. Once open, the panel persists across editor sessions; agents you launched yesterday appear in their last state (done, archived, or still running as a cloud agent) the next time you open Cursor. The Agents Window also syncs across machines for Pro and Business users — dispatch an agent from your desktop, check its progress from your laptop. For teams, agents launched by any team member appear in a shared view accessible from the same keyboard shortcut, making it the central coordination surface for async engineering work.

### Opening the Agents Window

Open the Agents Window via `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux), then type **Agents Window** and press Enter. Alternatively, click the grid icon in the top-right corner of the Cursor toolbar — it's new in Glass and sits next to the standard file explorer toggle.

### Launching Your First Agent

With the Agents Window open, click **+ New Agent**. A prompt field appears. Describe the task in natural language: *"Add rate limiting middleware to the Express API in `/server/api`"*. Cursor automatically scopes the agent to the current workspace root. You can override the repo, branch, or environment by expanding the **Agent Settings** dropdown before submitting.

### Using /worktree and /best-of-n Commands

Two slash commands unlock advanced orchestration:

- `/worktree` — forks the current branch into an isolated Git worktree so the agent edits files without touching your working tree. Essential for tasks you're not ready to merge.
- `/best-of-n` — spins up *n* parallel agents with identical instructions and presents their outputs side-by-side for you to cherry-pick the best solution. Cursor 3 supports up to `/best-of-5` on Pro and Business plans.

### Monitoring and Steering Agents

Each agent card in the panel updates in real time. A yellow spinner means the agent is actively executing; orange means it's blocked (usually waiting on a terminal command approval); green means done. Click **Review** on a done card to see a file diff and either accept, reject, or continue the agent with follow-up instructions.

## Design Mode: Visual UI Annotation for Faster Frontend Development

Design Mode is Cursor 3 Glass's browser-embedded annotation layer that lets you click directly on rendered UI elements and describe changes in natural language, eliminating the need to hunt for component file paths, class names, or CSS selectors. In a standardized March 2026 benchmark, Cursor built a responsive data table component in 2 rounds of prompting compared to Windsurf's 3 and GitHub Copilot's 5 — Design Mode is a significant contributor to that gap for frontend tasks. The workflow is: open your app's dev server preview inside Cursor (it embeds a Chromium viewport), click the Design Mode toggle (or press `Cmd+D`), then click any element on screen. Cursor highlights the element, identifies its source file and line, and opens a prompt attached to that component's exact context. You describe the change — *"make this button pill-shaped and change the hover state to #3B82F6"* — and the agent edits the component file directly. No more grep-ing for class names or manually tracing React component trees. Design Mode also supports multi-element selection (hold Shift and click) for batch instructions like *"change all these cards to use the new `CardV2` component"*.

### Design Mode vs Text-Based Frontend Prompting

Traditional text prompts for frontend work suffer from a context problem: you describe an element in words, the agent guesses the correct file and selector, and mismatches cause slow iteration loops. Design Mode eliminates that ambiguity by grounding every instruction in the actual rendered DOM. The tradeoff is that Design Mode requires your dev server to be running and accessible in Cursor's embedded browser — it doesn't work on screenshots or static HTML files. For projects with complex authentication (OAuth flows, multi-tenant apps), you'll need to log in inside the embedded browser once per session. Teams using Design Mode report the biggest gains on component-heavy React and Vue codebases where element-to-file mapping is non-obvious.

## Worktrees in Cursor 3: Isolated Background Task Execution

Cursor 3 Worktrees integrate Git's `git worktree` mechanism directly into the IDE, allowing agents to work on isolated branches without interfering with your current development environment. A worktree is a checked-out copy of a repository at a specific commit or branch, stored in a separate directory but sharing the same `.git` object database. In practical terms: your main branch stays clean and interactive while a background agent runs a risky refactor on `refactor/auth-middleware` in its own worktree — if the refactor goes wrong, you discard the worktree without touching your work. The April 24, 2026 Cursor update improved worktree UX significantly, adding one-click branch switching from the Agents Window card (previously you had to use the terminal), and multi-root workspace support so agents in different worktrees appear as peers in the same Agents Window panel.

### Creating and Managing Worktrees

From the Agents Window, launch an agent and prefix the prompt with `/worktree branch-name` to automatically create a new worktree for `branch-name`. Cursor handles the `git worktree add` call, sets the working directory for the agent, and registers the worktree in the Agents Window sidebar. When the agent is done and you've reviewed the diff, click **Merge & Cleanup** to merge the branch and run `git worktree remove` automatically. You can also open any existing worktree in a new Cursor window via `File > Open Worktree` — useful when you want to manually inspect agent work in a separate editor context before merging.

### When to Use Worktrees vs Standard Agents

Use worktrees when the task requires branch isolation — database migrations, large refactors, dependency upgrades, or anything that modifies lock files. Standard agents (without `/worktree`) are fine for additive tasks (new files, new functions) where a conflict is unlikely. The rule of thumb: if you'd normally create a branch for the task manually, use `/worktree`.

## Cloud Agents and Remote SSH: Taking Cursor Beyond Local Development

Cloud Agents in Cursor 3 Glass run on Anysphere's infrastructure rather than your local machine, enabling long-running tasks (multi-hour refactors, large test suite runs, data pipeline jobs) to continue even when you close your laptop. Cursor 3 was built around the observation that enterprise workflows can't be bounded by a developer's battery life or VPN session. Cloud Agents connect to your codebase via a secure tunnel — either through GitHub/GitLab OAuth for cloud repos, or via a persistent Remote SSH connection for on-prem environments. Once connected, you dispatch agents from the Agents Window exactly as you would local agents; the only difference is an icon indicating the agent is executing remotely. Cloud Agents support the same `/worktree` and `/best-of-n` commands, and their logs stream back to your Agents Window in real time. For enterprise teams running Cursor Business, Cloud Agents can be scoped to specific infrastructure environments (staging, QA, sandbox) so agents never accidentally touch production systems.

### Setting Up Remote SSH Agents

Go to `Settings > Agents > Remote Environments`, add a new SSH host (hostname, port, SSH key path), and click **Test Connection**. Once the connection is verified, the remote environment appears in the **Agent Settings** dropdown when launching any agent from the Agents Window. Cursor installs a lightweight agent runner on the remote host on first connection; subsequent launches reuse the installed runner. Supported on Linux x86_64 and ARM64 hosts.

## Cursor 3 vs Competitors: How Glass Stacks Up in 2026

Cursor 3 Glass competes primarily against Windsurf 3, GitHub Copilot (VS Code + CLI), and Claude Code in the agent-first IDE category. The competitive landscape as of April 2026 breaks down as follows:

| Feature | Cursor 3 Glass | Windsurf 3 | GitHub Copilot | Claude Code |
|---|---|---|---|---|
| Parallel agents | Yes (Agents Window) | Limited (2 concurrent) | No (sequential only) | Yes (via worktrees) |
| Visual UI annotation | Yes (Design Mode) | No | No | No |
| Git Worktrees integration | Native (1-click) | Manual only | Manual only | Native |
| Cloud agents | Yes (Anysphere infra) | Yes (Codeium infra) | No | No |
| Multi-repo workspace | Yes (April 2026 update) | Partial | No | No |
| Best-of-N sampling | Yes (/best-of-5) | No | No | No |
| IDE base | VS Code fork | VS Code fork | VS Code extension | Terminal/CLI |
| Monthly cost (Pro) | $20 | $15 | $10 | $20 |

Cursor's differentiation in 2026 is depth of agent orchestration and the Design Mode feature — no competitor offers visual UI annotation natively. Windsurf is cheaper for solo developers doing primarily backend work. GitHub Copilot remains the easiest integration for teams locked into the GitHub ecosystem. Claude Code is the strongest choice for pure terminal workflows and long-horizon autonomous tasks, but lacks a GUI for multi-agent monitoring.

### Where Cursor 3 Falls Short

Cursor 3 Glass's cloud agent infrastructure is US-hosted with EU data residency available only on Enterprise plans — a friction point for GDPR-sensitive teams. The embedded Chromium browser for Design Mode adds ~300MB to the installed app size. And despite the multi-repo support added in April 2026, cross-repo agents still require both repos to be in the same organization on GitHub/GitLab — cross-org workflows need manual SSH configuration.

## Tips and Best Practices for Multi-Agent Orchestration in Cursor 3

Effective multi-agent orchestration in Cursor 3 Glass requires a different mental model than single-agent IDE use. These are the patterns that produce the best results after daily use of Glass since its April 2, 2026 release.

**Scope agents narrowly.** Agents with focused tasks (one endpoint, one component, one test file) outperform broad instructions ("refactor all the auth code"). The Agents Window makes it cheap to run five narrow agents versus one bloated one — use that.

**Pair /worktree with /best-of-n for risky changes.** When you're unsure which implementation approach is correct, run `/worktree feature/option-a` and `/worktree feature/option-b` with different instructions, then use `/best-of-2` to compare diffs side-by-side before merging either branch. This is the Glass-native replacement for the old "duplicate Composer session" hack.

**Set approval gates on terminal commands.** In `Settings > Agents > Permissions`, configure agents to require your approval before running any shell command. This prevents agents from installing unexpected packages or overwriting files outside their task scope. The approval prompt appears inline in the Agents Window card — one click, no context switch.

**Use agent labels.** Each agent card supports custom labels (click the tag icon). Label agents by feature, sprint, or epic. The Agents Window search bar filters by label, so you can quickly find all agents related to `auth-refactor` across sessions.

**Archive, don't delete.** When an agent finishes, archive its card rather than deleting it. Archived agents retain their full conversation thread and file diff — useful for auditing decisions or restarting a similar task later with one-click clone.

**Monitor token spend in real time.** The Agents Window shows a running token cost per agent and a session total in the top-right. Set a session budget in Settings; Cursor will pause all agents and notify you when you approach the limit rather than silently running up your bill.

## FAQ

**How do I open the Agents Window in Cursor 3?**
Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux) and type "Agents Window," then press Enter. Alternatively, click the grid icon in the Cursor toolbar at the top right of the window.

**Can I run Cursor 3 Agents on a remote server?**
Yes. Go to `Settings > Agents > Remote Environments`, add an SSH host, and once the connection is verified it appears in the Agent Settings dropdown. Cloud Agents run on Anysphere's infrastructure for fully managed remote execution without SSH configuration.

**What is Design Mode in Cursor 3 and how do I enable it?**
Design Mode is a browser-embedded UI annotation layer that lets you click rendered elements and describe changes in natural language. Enable it with `Cmd+D` or the toggle in Cursor's embedded Chromium browser while your dev server is running. It works with any web framework.

**What's the difference between /worktree and a standard Cursor agent?**
A standard agent edits files in your current working tree. `/worktree branch-name` creates an isolated Git worktree on a new branch so the agent works without affecting your main workspace. Use worktrees for risky changes — refactors, migrations, dependency upgrades.

**Is Cursor 3 Glass worth the $20/month Pro plan?**
For developers running multiple concurrent agents or using Design Mode for frontend work, yes — the Agents Window and parallel execution alone justify the cost for most professional workflows. Solo developers doing primarily backend work with minimal parallelism may find Windsurf 3 at $15/month a better value-to-cost ratio.
