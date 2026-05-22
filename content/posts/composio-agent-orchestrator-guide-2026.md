---
title: "Composio Agent Orchestrator: Parallel Coding Agents for CI and PR Reviews"
date: 2026-05-22T03:02:46+00:00
tags: ["composio", "agent-orchestrator", "parallel-agents", "CI-automation", "PR-review"]
description: "Composio Agent Orchestrator runs 5+ parallel coding agents that autonomously fix CI failures and merge PRs — a practical guide and comparison with OpenAI Symphony."
draft: false
cover:
  image: "/images/composio-agent-orchestrator-guide-2026.png"
  alt: "Composio Agent Orchestrator: Parallel Coding Agents for CI and PR Reviews"
  relative: false
schema: "schema-composio-agent-orchestrator-guide-2026"
---

Composio Agent Orchestrator (AO) is an open-source framework that runs multiple coding agents in parallel across your Git worktrees, automatically routes CI failures back to the responsible agent, and handles the full PR lifecycle from task assignment to merged code — without a human in the loop.

## What Is Composio Agent Orchestrator?

Composio Agent Orchestrator is an open-source TypeScript framework, released by Composio in February 2026, that coordinates multiple AI coding agents working simultaneously on separate Git worktrees. Unlike single-agent tools that queue tasks sequentially, AO spawns up to 30+ parallel agents (default: 5 per project) and assigns each agent an isolated branch. When a CI pipeline fails, AO detects the failure within ~30 seconds via lifecycle polling and routes the error context back to the specific agent session that introduced the regression. The system comprises 40,000 lines of TypeScript, 17 plugins, and 3,288 tests — and was mostly built by the agents it now orchestrates. Since open-sourcing, it has accumulated 4.9k GitHub stars. The core value proposition: development teams can offload the full feedback loop of "write code → CI fails → fix → re-review → merge" to AI, reducing the time humans spend on routine CI triage and PR shepherding.

## How It Works: The Dual-Layer Planner/Executor Architecture

Composio Agent Orchestrator replaces the traditional ReAct loop — where a single agent reasons, acts, observes, and repeats in a sequential chain — with a stateful dual-layer architecture that separates strategic planning from code execution. The **Planner layer** ingests tickets from a tracker (GitHub Issues, Linear, Jira) and decomposes them into bounded tasks, each with a clear success criterion and estimated blast radius. The **Executor layer** picks up these tasks, each in an isolated Git worktree, and drives a coding agent (Claude Code, OpenAI Codex, Aider, or a custom adapter) to completion. The Planner retains global state — which branches are active, which CI runs are pending, which PRs are blocked on review — so it can rebalance work dynamically without any task dropping through the cracks.

### Why This Beats ReAct Loops in Production

ReAct loops accumulate tool noise as context grows. A single agent working on a ten-file refactor will have hundreds of tool calls in its context by the time it opens the fifth file, degrading output quality and inflating token costs. AO's Just-in-Time context management routes only the tool definitions relevant to the current execution step to each agent session. An agent writing a database migration never sees the GitHub PR review tools; an agent fixing a failing Cypress test never receives the Linear ticket-creation schema. This selective routing keeps each agent session lean and focused — typically under 200k tokens even on large codebases — and eliminates the "confused by irrelevant tools" failure mode that plagues general-purpose agents handling 100+ API integrations.

### The 8 Plugin Slots

AO's plugin architecture exposes eight standardized slots that control every layer of the orchestration: **runtime** (tmux, Docker, bare Node), **agent** (Claude Code, Codex, Aider), **workspace** (local Git, remote volume), **tracker** (GitHub, Linear), **SCM** (GitHub, GitLab), **notifier** (Slack, email), **terminal** (xterm, headless), and **lifecycle** (CI polling adapters for GitHub Actions, CircleCI, Jenkins). Each slot accepts a single plugin; swapping the tracker from GitHub Issues to Linear requires changing one config key and restarting — no code changes needed.

## Key Features: Autonomous CI Fixes, PR Reviews, and Merge Handling

Composio Agent Orchestrator's headline capability is end-to-end PR autonomy: the framework handles every stage between "task assigned" and "PR merged" without requiring human action at any intermediate step. Here is how each stage works in practice. When a tracker plugin surfaces a new ticket, the Planner layer creates a task record with acceptance criteria parsed from the ticket body. An Executor agent claims the task, creates a branch (`ao/task-<id>`), and begins implementing. When the agent pushes a commit, the lifecycle plugin polls the CI system every 15 seconds. If a run fails within 30 seconds of detection, AO injects the structured CI log — only the failing step's output, not the full 10,000-line log — back into the agent's session as a tool result. The agent corrects the issue and pushes again. Once CI passes, the SCM plugin opens a PR (or marks a draft PR ready for review), optionally assigns reviewers based on CODEOWNERS, and monitors the review thread. If a reviewer requests changes, AO surfaces the diff comments to the agent as structured input. Approvals trigger an auto-merge if branch protection rules allow it.

### CI Failure Routing: The Key Differentiator

Most CI failure workflows today rely on a human reading the failure log and deciding which engineer (or which agent session) should fix it. AO eliminates this coordination cost entirely. Its lifecycle plugin maintains a map of `commit SHA → agent session ID`, so when a CI run fails on commit `abc123`, AO knows exactly which tmux pane (or Docker container) owns that work and injects the failure context there. Teams running 10 parallel agents report that this routing resolves 70–80% of CI failures without any human involvement, because most failures are deterministic (missing import, type error, wrong env var) and the same agent that introduced the bug has full context to fix it in under two minutes.

### Automatic PR Review Handling

PR review automation in AO works through the SCM plugin, which subscribes to the repository's webhook events. When a reviewer posts an inline comment, the plugin extracts the comment, the file path, and the surrounding diff context, and queues it as a structured input event for the responsible agent. The agent processes each review comment as an individual task: read the comment, locate the code, apply the fix, push a commit. The reviewer sees a resolved conversation and a new commit within minutes. This loop continues until all review threads are resolved and approvals are received, at which point the SCM plugin triggers the merge.

## Getting Started: Installation and Setup in Under 10 Minutes

Composio Agent Orchestrator installs as a single global pnpm package and requires four system-level prerequisites: Node.js 20+, pnpm, tmux, and Git 2.25+. Git 2.25 introduced the `git worktree add` subcommand that AO depends on to isolate each agent in its own working tree — older Git versions will fail silently during task startup. Beyond those prerequisites, you need an API key for your chosen coding agent (Anthropic for Claude Code, OpenAI for Codex) and a GitHub or Linear personal access token with `repo` and `issues` scopes. The entire setup — from `pnpm add -g` to a running orchestrator watching your repository — takes under 10 minutes on a fresh machine. There are no databases to provision, no persistent services beyond the tmux session itself, and no cloud accounts to create beyond what you already use for CI. This low operational footprint is one of AO's strongest advantages over Symphony, which requires a running PostgreSQL instance and an Elixir release before it can process a single ticket.

### Prerequisites

```bash
# Verify prerequisites
node --version   # must be ≥ 20
pnpm --version   # any recent version
tmux -V          # must be installed
git --version    # must be ≥ 2.25
```

### Installation

```bash
# Install the CLI globally
pnpm add -g @composio/agent-orchestrator

# Verify
ao --version
```

### Initialize a Project

```bash
cd your-repo
ao init
```

`ao init` generates an `ao.config.ts` in the project root. The default config uses tmux as the runtime, Claude Code as the agent, GitHub as both the tracker and SCM, and GitHub Actions as the CI lifecycle adapter. Edit the config to swap any slot:

```typescript
// ao.config.ts
import { defineConfig } from '@composio/agent-orchestrator';

export default defineConfig({
  agent: 'claude-code',          // or 'codex', 'aider'
  runtime: 'tmux',               // or 'docker'
  tracker: 'github',             // or 'linear', 'jira'
  scm: 'github',                 // or 'gitlab'
  lifecycle: 'github-actions',   // or 'circleci', 'jenkins'
  concurrency: 5,                // parallel agent sessions
  autoMerge: true,               // merge when CI passes + approved
});
```

### Start the Orchestrator

```bash
ao start
```

AO opens a tmux session with a dashboard pane showing active tasks, agent status, and CI states. New tasks are picked up automatically from the configured tracker.

## Running Parallel Agents: A Step-by-Step Walkthrough

Running your first set of parallel agents requires three steps after initial setup: labeling issues for AO to pick up, watching the dashboard, and optionally intervening at review gates. AO's default concurrency is 5 parallel agents, configurable up to 30+ via the `concurrency` key in `ao.config.ts`. Each agent runs in its own tmux pane with an isolated Git worktree, meaning five agents can simultaneously edit five different parts of your codebase without any shared file state or merge conflicts during the coding phase. In practice, teams starting with AO for the first time should label 5–10 issues from their backlog — picking bounded, well-scoped tasks with clear acceptance criteria in the ticket body — and observe one full cycle before increasing concurrency. This first run surfaces any misconfigured plugin settings (wrong API token scopes, incorrect CI adapter URLs) in a controlled way, while giving you a realistic picture of per-agent token costs before you scale to 20 or 30 parallel sessions. This walkthrough shows what happens for a batch of five issues processed simultaneously by five parallel agents.

### Step 1: Label Issues for Pickup

AO monitors the configured tracker for issues with the label `ao:ready` (configurable). Apply this label to five open issues:

```bash
# Using GitHub CLI
gh issue edit 101 --add-label "ao:ready"
gh issue edit 102 --add-label "ao:ready"
gh issue edit 103 --add-label "ao:ready"
gh issue edit 104 --add-label "ao:ready"
gh issue edit 105 --add-label "ao:ready"
```

### Step 2: Watch the Dashboard

Within seconds of labeling, AO's Planner layer ingests all five issues and distributes them across five Executor agents. Each agent gets its own tmux pane, its own Git worktree (`ao/task-101` through `ao/task-105`), and its own CI run. The dashboard shows:

```
AGENT ORCHESTRATOR — 5 active / 0 queued / 0 blocked

  Task 101 [agent-1]  ██████░░░░  63%  ci:running   branch:ao/task-101
  Task 102 [agent-2]  ████████░░  82%  ci:passed    branch:ao/task-102  ← PR open
  Task 103 [agent-3]  ██░░░░░░░░  24%  coding       branch:ao/task-103
  Task 104 [agent-4]  ██████████ 100%  review:2     branch:ao/task-104  ← awaiting approval
  Task 105 [agent-5]  ████░░░░░░  41%  ci:failed    branch:ao/task-105  ← routing fix
```

### Step 3: Review Gates (Optional)

If `autoMerge: false`, AO pauses at the "PR approved" state and waits for a human merge click. With `autoMerge: true`, the SCM plugin merges automatically once CI is green and required approvals are received. Teams typically enable auto-merge for low-risk tasks (dependency bumps, doc updates, minor refactors) and disable it for tasks touching authentication, payments, or data migrations.

### Handling CI Failures Automatically

Task 105 in the example above shows `ci:failed` with "routing fix" in progress. AO has already injected the failure context back to agent-5. Within 60–90 seconds, agent-5 will push a fix commit, CI will re-run, and the dashboard will update to `ci:running`. No human action required unless the fix fails twice in a row, at which point AO marks the task `blocked` and sends a Slack notification (via the notifier plugin) with the CI log summary.

## Composio AO vs OpenAI Symphony vs T3 Code: Which Should You Use?

The parallel coding agent space has three serious contenders as of mid-2026: Composio Agent Orchestrator, OpenAI Symphony, and T3 Code. Each makes different trade-offs on autonomy, setup complexity, and ecosystem lock-in. AO is the most production-ready option for teams that want full PR lifecycle automation without committing to a specific AI provider or infrastructure stack. Symphony offers superior fault tolerance (Erlang/OTP supervision trees) but requires Elixir, PostgreSQL, and a Linear workspace — a significant operational bet. T3 Code is the best fit for teams that want interactive, per-edit review rather than autonomous batch processing.

| Feature | Composio AO | OpenAI Symphony | T3 Code |
|---|---|---|---|
| **Language** | TypeScript | Elixir | TypeScript |
| **Default concurrency** | 5 (up to 30+) | 10 | 1 (interactive) |
| **Agent support** | Claude, Codex, Aider | Codex (primary) | Claude, Codex |
| **CI auto-fix** | Yes (30s detection) | Partial | No |
| **PR auto-merge** | Yes | Yes | No |
| **Tracker integration** | GitHub, Linear, Jira | Linear (required) | GitHub |
| **Setup complexity** | Low (Node + pnpm + tmux) | High (Elixir + PostgreSQL) | Low |
| **Production status** | Production-ready | Engineering preview | Beta |
| **Open source** | Yes (MIT) | Yes (Apache 2.0) | Yes (MIT) |
| **Self-hosted** | Yes | Yes | Yes |

### When to Choose Composio AO

Choose AO if you want autonomous PR lifecycle management without infrastructure overhead, if your team uses Claude Code as its primary coding agent, or if you need agent-agnosticism to hedge against provider lock-in. AO's plugin system makes it the most adaptable option: you can wire it to an on-premise GitLab instance, a self-hosted Jenkins server, and a custom Linear workspace in under an hour.

### When to Choose OpenAI Symphony

Symphony is worth considering if your team already runs Elixir infrastructure, relies on Linear as its primary tracker, and needs battle-tested process supervision for extremely long-running agent sessions. Symphony's Erlang/OTP foundation means an agent process crash doesn't lose task state — the supervisor tree restarts it and resumes from the last checkpoint. This is a genuine advantage for multi-day tasks. The trade-off: Symphony is still an engineering preview as of May 2026, and its dependency on Linear means tracker portability is limited.

### When to Choose T3 Code

T3 Code targets a different workflow: interactive, human-in-the-loop editing where a developer reviews each suggested change via a JSON-RPC protocol before it is applied. This is not autonomous batch processing — it is more like an advanced pair-programming tool. Choose T3 Code if your team values granular control over every line change and is skeptical of autonomous merges.

## Plugin Ecosystem and Extensibility

Composio Agent Orchestrator's plugin system is what makes it practical for real-world engineering teams, whose CI stacks, trackers, and SCM platforms rarely match the defaults of any open-source tool. AO exposes 8 standardized plugin slots — runtime, agent, workspace, tracker, SCM, notifier, terminal, and lifecycle — each backed by a TypeScript interface with 3–5 methods. The community registry at `registry.composio.dev/plugins` already lists 23 plugins as of May 2026, covering CircleCI, Jenkins, GitLab, Jira, Bitbucket, Azure DevOps, and Buildkite. Writing a new plugin requires implementing a single interface, typically in 50–150 lines of TypeScript, with no changes to AO's core. This design was a deliberate architectural choice: Composio's own team swapped the tracker plugin from GitHub Issues to Linear mid-project during AO's self-bootstrapping build phase, and the ability to do so without touching orchestration logic validated the plugin boundary design. For enterprise teams running on-premise SCM or proprietary CI systems, the plugin model means AO can integrate without requiring access to Composio's hosted services — the entire stack runs inside your own infrastructure.

### Writing a Custom Lifecycle Plugin

The lifecycle plugin interface has three methods: `subscribe(commitSHA: string): void` to register a CI run for monitoring, `poll(): CIStatus[]` to return the current state of all tracked runs, and `unsubscribe(commitSHA: string): void` to stop monitoring a run. A minimal CircleCI adapter:

```typescript
import { LifecyclePlugin, CIStatus } from '@composio/agent-orchestrator';
import { CircleCI } from 'circleci-client';

export class CircleCIPlugin implements LifecyclePlugin {
  private client = new CircleCI({ token: process.env.CIRCLECI_TOKEN });
  private tracked = new Map<string, string>(); // sha → workflow_id

  async subscribe(sha: string) {
    const run = await this.client.getWorkflowBySHA(sha);
    this.tracked.set(sha, run.id);
  }

  async poll(): Promise<CIStatus[]> {
    return Promise.all([...this.tracked.entries()].map(async ([sha, id]) => {
      const status = await this.client.getWorkflow(id);
      return { sha, status: status.state, log: status.failedStepOutput ?? null };
    }));
  }

  async unsubscribe(sha: string) {
    this.tracked.delete(sha);
  }
}
```

Register it in `ao.config.ts`:

```typescript
import { CircleCIPlugin } from './plugins/circleci';

export default defineConfig({
  lifecycle: new CircleCIPlugin(),
  // ... other config
});
```

### Community Plugin Registry

The Composio team maintains a plugin registry at `registry.composio.dev/plugins`. As of May 2026, the registry includes 23 community-maintained plugins covering Bitbucket, Azure DevOps, Buildkite, PagerDuty (as a notifier), and a Docker-based runtime plugin for teams that prefer container isolation over tmux sessions.

## Limitations and When Not to Use Agent Orchestrator

Composio Agent Orchestrator is a strong tool for autonomous PR automation, but it is not a universal solution — and teams that deploy it outside its design envelope will be frustrated within a week. The primary limitation is task granularity: AO works best on bounded, self-contained tasks that can be fully described in a ticket with clear acceptance criteria and a verifiable success condition (tests pass, specific UI behavior, linter clean). Open-ended tasks like "improve the performance of the search API" or "refactor the authentication module" routinely produce unsatisfying results because the agent lacks the product judgment to decide when "done" is good enough. A second structural limitation is test coverage: AO's auto-merge path assumes that a green CI run equals correctness. In codebases where test coverage is below 50%, this assumption breaks down badly — agents can make API-breaking changes, introduce silent data regressions, or delete features entirely if no test catches the deviation. The framework does not compensate for weak test suites; it amplifies the consequences of having one. Teams should audit their test coverage and enforce minimum thresholds before enabling `autoMerge: true` on anything beyond trivial tasks.

### Tasks AO Handles Poorly

- **Cross-cutting architectural changes** that touch 30+ files with deep semantic dependencies — agents frequently break interfaces they cannot see
- **Tasks requiring human judgment on product direction** — AO will implement the literal ticket description even when the right answer is to change the spec
- **Tasks in legacy codebases with poor test coverage** — CI passing does not mean correctness, and AO's auto-merge will happily ship a behavior regression if no test catches it
- **Security-sensitive changes** — automated code review cannot replace a human security audit for auth flows, cryptography, or access control

### Operational Overhead

AO requires persistent infrastructure: a tmux-capable server (or Docker host), reliable network access to your SCM and tracker, and API keys for each service. For teams running on ephemeral CI runners without persistent sessions, the tmux-based runtime is impractical. The Docker runtime plugin mitigates this, but adds container management overhead. Teams using managed CI (e.g., GitHub Actions as their primary dev environment) will find AO's operational model a poor fit.

### Cost Considerations

Five parallel Claude Code sessions running continuously generate significant API costs. A single agent session resolving a medium-complexity ticket (10–20 file changes, 2–3 CI retry loops) consumes approximately 500k–1M tokens. At five concurrent agents, a busy day of 20 resolved tickets can cost $200–$400 in API fees. Teams should profile costs carefully before enabling high-concurrency AO runs on large backlogs.

## Verdict: Is Composio Agent Orchestrator Production-Ready in 2026?

Composio Agent Orchestrator is production-ready for teams whose development workflow matches its design assumptions: well-scoped tickets, good test coverage, and a tolerance for occasional agent errors requiring human cleanup. For those teams, AO delivers on its promise: parallel coding agents that handle CI failures and PR lifecycle management autonomously, reducing engineering hours spent on routine triage by 60–80% in early adopter reports. The fact that Composio built 40,000 lines of its own codebase using AO — in 8 days — is the most compelling proof point in the product's favor. It is not a demo; it is the engineering team's primary development workflow.

For teams with open-ended tasks, weak test coverage, or security-critical codebases, AO is better used as an accelerator for low-risk work (dependency upgrades, documentation, test generation) while humans retain control over the full-stack changes that matter most.

---

## FAQ

**Q1: Does Composio Agent Orchestrator require a specific AI model?**

No. AO is model-agnostic. The agent plugin slot accepts Claude Code, OpenAI Codex, Aider, and custom adapters. You can run different agents on different tasks by configuring per-task overrides in `ao.config.ts`. Most teams default to Claude Code (claude-sonnet-4-6) for its strong code editing performance and long context window.

**Q2: How does AO handle merge conflicts between parallel agent branches?**

AO does not automatically resolve merge conflicts. When a conflict is detected at PR creation or merge time, the SCM plugin marks the task `blocked:conflict` and notifies via the configured notifier (Slack, email). A human must resolve the conflict manually or instruct the agent via a ticket comment. Future roadmap items include automatic rebase-and-retry for simple conflicts.

**Q3: Can AO run on Windows?**

The default tmux runtime requires a Unix-like environment, so bare Windows is not supported. Windows users can run AO inside WSL2 or use the Docker runtime plugin. The development team has indicated that a native Windows terminal runtime plugin is planned but not yet available.

**Q4: How do I limit AO to specific repositories or branches?**

In `ao.config.ts`, set the `allowedBranches` and `trackerFilter` options. `trackerFilter` accepts a JMESPath expression evaluated against ticket metadata, so you can restrict AO to tickets with specific labels, milestones, or assignees. The `allowedBranches` pattern (glob) controls which base branches AO will open PRs against.

**Q5: What happens if an agent session crashes mid-task?**

AO's Planner layer monitors all active Executor sessions via the runtime plugin. If a session exits unexpectedly (process crash, network timeout, API error), the Planner marks the task `interrupted`, releases the worktree, and re-queues the task for a new agent session after a configurable backoff (default: 5 minutes). The new session receives the full task context plus the last 50 lines of the interrupted session's terminal output to aid recovery.
