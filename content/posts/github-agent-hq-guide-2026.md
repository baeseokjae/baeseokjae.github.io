---
title: "GitHub Agent HQ Guide 2026: Run Claude, Copilot, and Codex from One Interface"
date: 2026-05-22T03:00:29+00:00
tags: ["github", "ai-agents", "github-copilot", "claude", "codex", "developer-tools"]
description: "Complete guide to GitHub Agent HQ: assign issues to Claude, Copilot, and Codex from a single interface, compare PRs, and optimize agent selection for every task type."
draft: false
cover:
  image: "/images/github-agent-hq-guide-2026.png"
  alt: "GitHub Agent HQ Guide 2026: Run Claude, Copilot, and Codex from One Interface"
  relative: false
schema: "schema-github-agent-hq-guide-2026"
---

GitHub Agent HQ is GitHub's unified Mission Control interface that lets you assign issues to Claude, Copilot, and Codex agents side-by-side, compare their pull requests, and manage all AI coding sessions from one dashboard — no external subscriptions beyond your existing Copilot plan required.

## What Is GitHub Agent HQ? The Unified Mission Control for AI Coding Agents

GitHub Agent HQ is a centralized orchestration layer within GitHub that allows development teams to deploy, monitor, and compare multiple AI coding agents — including GitHub Copilot (workspace agent), Anthropic Claude, and OpenAI Codex — from a single unified interface. Launched in late 2025 and expanded significantly in early 2026, Agent HQ represents GitHub's shift from a single-agent assistant model to a vendor-neutral, multi-agent development platform. As of April 2026, available Claude models include Claude Sonnet 4.6, Claude Opus 4.6, Claude Sonnet 4.5, and Claude Opus 4.5; Codex options span GPT-5.2-Codex through GPT-5.4. Agent HQ is included with all GitHub Copilot plans — no separate marketplace purchases required. The platform supports github.com, VS Code, and GitHub Mobile, giving every developer on your team access to the same agent orchestration tools regardless of their preferred environment. The key value proposition: instead of context-switching between different AI tools with incompatible workflows, Agent HQ standardizes the entire agentic development cycle under GitHub's existing issue and PR model.

### Why Agent HQ Changes Multi-Agent Development

Before Agent HQ, using Claude alongside Copilot meant juggling separate tabs, separate contexts, and separate billing dashboards. Agent HQ collapses this into a single Assignees dropdown on any GitHub issue, turning agent selection into a one-click operation. GitHub Copilot reached 4.7 million paid subscribers by January 2026 — up ~75% year-over-year — and is deployed at ~90% of Fortune 100 companies. Agent HQ leverages this installed base to make multi-agent development a first-class workflow rather than a power-user workaround.

## Which Agents Are Available — Copilot, Claude, and Codex Explained

GitHub Agent HQ currently supports three distinct AI coding agents: GitHub Copilot (the workspace agent), Anthropic Claude, and OpenAI Codex. Each agent has a different architecture, strength profile, and optimal task domain. GitHub Copilot's workspace agent excels at repository-aware tasks — it has deep context of your codebase structure, existing conventions, and linked issues. Claude (Sonnet 4.6 and Opus 4.6) is optimized for multi-file refactors, complex architectural changes, and tasks requiring detailed explanatory comments or documentation alongside code changes. Codex (GPT-5.2-Codex through GPT-5.4) dominates algorithmic and data-structure-heavy tasks — sorting implementations, parsing logic, and performance-critical routines where terse, high-precision code is the goal. All three agents work through the same GitHub PR workflow: each agent creates a branch, commits code, and opens a draft PR that you can review, request changes on, or merge. The multi-agent comparison workflow lets you assign the same issue to all three simultaneously and select the best PR from three competing implementations.

| Agent | Strength | Best For | Model Options |
|-------|----------|----------|---------------|
| Copilot (workspace) | Repository context | Inline completions, repo-aware fixes | Built-in (Copilot model) |
| Claude | Multi-file reasoning | Refactors, architecture, docs | Sonnet 4.6, Opus 4.6, Sonnet 4.5, Opus 4.5 |
| Codex | Algorithmic precision | Data structures, parsing, performance | GPT-5.2-Codex, GPT-5.3-Codex, GPT-5.4 |

## Prerequisites: Subscription Tiers and Enabling Agents in Your Repository

GitHub Agent HQ requires an active GitHub Copilot subscription and repository-level feature enablement. As of 2026, Copilot pricing tiers are: Copilot Pro at $10/month (individual), Copilot Business at $19/user/month (team), and Copilot Pro+ and Enterprise at $39/user/month (advanced features including Agent HQ multi-agent access). Claude and Codex access within Agent HQ is included with Copilot Business and above — no separate Anthropic or OpenAI billing during the public preview. Starting June 1, 2026, GitHub transitions to usage-based billing: 1 AI credit = $0.01 USD, with each agent session consuming one premium request. To enable Agent HQ, navigate to your repository Settings → Copilot → Agents, then toggle on "Enable GitHub Copilot Agent Access" and check "Allow third-party agents (Claude, Codex)." Organization admins can enforce agent policies via the Agent Control Plane under Organization Settings → Copilot → Agent Governance. Without this step, the Assignees dropdown in issues will only show the built-in Copilot workspace agent.

### Required Permissions

- Repository write access (to assign issues)
- Copilot Business or higher subscription (for Claude/Codex access)
- Branch protection rules configured (agents cannot push directly to `main` by default)

## Step-by-Step: Assigning Issues to AI Agents on GitHub

Assigning an issue to an AI agent in GitHub Agent HQ takes under 30 seconds once setup is complete. The entire workflow mirrors how you'd assign an issue to a human teammate — with the addition of agent-specific options in the Assignees dropdown. Navigate to the target GitHub issue, click the Assignees gear icon on the right sidebar, and you will see AI agents listed below human collaborators: "Copilot (workspace)," "Claude (Anthropic)," and "Codex (OpenAI)." Selecting an agent triggers the agentic session immediately — the agent reads the issue body, analyzes linked code, and begins working autonomously. Within minutes (typically 3–12 minutes depending on scope), the agent opens a draft PR against the default branch with its implementation. You will receive a GitHub notification when the PR is ready. The draft PR includes the agent's commit history, a summary of changes made, and a self-generated test plan. From here, you review the diff exactly as you would any PR: add comments, request changes, or approve and merge. If the agent's first attempt misses the mark, comment on the PR with clarifying instructions — the agent picks up the thread and pushes additional commits automatically.

### Common Setup Issues

- **Agent not appearing in Assignees**: Confirm third-party agents are enabled in repo settings and your Copilot tier includes Agent HQ access.
- **Agent session times out**: Large codebases may exceed the default 15-minute session window; increase via Copilot → Agent Timeout settings.
- **PR opens against wrong branch**: Set `base_branch` in `.github/copilot-config.yml` to control which branch agents target.

## Running Multiple Agents in Parallel — The Three-PR Comparison Workflow

One of Agent HQ's most powerful features is the ability to assign the same issue to multiple agents simultaneously and receive competing PR implementations. This multi-agent parallel workflow works by assigning an issue to Claude, Codex, and Copilot at the same time — each agent spins up an independent session, creates a separate branch (e.g., `agent/claude/issue-123`, `agent/codex/issue-123`, `agent/copilot/issue-123`), and opens a draft PR. The Mission Control dashboard (accessible at github.com/[org]/[repo]/agent-hq or via the "Agents" tab in the repository navbar) shows all three sessions running in real time — their status, estimated completion, and token consumption. Once all three PRs are open, use the side-by-side diff view in Agent HQ to compare implementations across the same changed files. In practice, this workflow takes 10–20 minutes for a medium-complexity issue and saves significant back-and-forth iteration: you select the best implementation, merge it, and close the other two branches. Teams at enterprise scale report using this approach for refactoring milestones where architectural trade-offs benefit from multiple independent interpretations.

## Choosing the Right Agent for the Right Task (Decision Matrix)

Not all coding tasks benefit equally from all three agents. Experienced Agent HQ users develop a task-routing intuition based on issue type, codebase size, and output requirements. Claude performs best on tasks where reasoning transparency matters: it produces detailed commit messages, explains why it made each structural decision, and often includes inline documentation. Codex optimizes for correctness and conciseness in algorithmic problems — its outputs tend to be shorter and more performant for computational tasks, with fewer explanatory comments. Copilot's workspace agent wins on repository-specific muscle memory: it understands your existing naming conventions, import patterns, and testing frameworks without being told. According to developer productivity studies, AI coding tools generate 46% of code written in 2026, saving an average of 3.6 hours per week per developer — and agent routing multiplies this leverage by ensuring the right model handles each task class.

| Task Type | Recommended Agent | Why |
|-----------|------------------|-----|
| Bug fix with clear root cause | Copilot (workspace) | Knows repo context, fast |
| Multi-file architectural refactor | Claude Opus 4.6 | Deep reasoning, explains changes |
| Algorithm implementation | Codex GPT-5.4 | Precise, concise, high-correctness |
| Adding tests to existing code | Claude Sonnet 4.6 | Context-aware, documentation-friendly |
| Performance optimization | Codex GPT-5.3-Codex | Code-efficiency focused |
| Feature with complex UI logic | Claude Sonnet 4.6 | Handles multi-component reasoning |
| CI/CD config updates | Copilot (workspace) | Knows your pipeline conventions |

## Model Selection — Picking Specific Claude and Codex Models for Your Task

GitHub Agent HQ added per-session model selection in April 2026, allowing developers to choose specific model variants rather than using a single default. For Claude, you choose between Sonnet 4.6 (faster, lower cost), Opus 4.6 (more capable, slower), Sonnet 4.5 (previous generation), and Opus 4.5 (legacy). For Codex, the options are GPT-5.2-Codex (balanced), GPT-5.3-Codex (enhanced reasoning), and GPT-5.4 (latest, highest capability). The model selection UI appears in the Assignees dropdown as a secondary picker after you select the agent: "Claude → [Select model]." Under usage-based billing starting June 2026, Opus 4.6 consumes more AI credits per session than Sonnet 4.6 — roughly 3–4x more per token. A practical routing heuristic: use Sonnet 4.6 for issues under 200 lines of scope, switch to Opus 4.6 for large-scale refactors or tasks requiring multi-step reasoning across 5+ files. For Codex, GPT-5.4 is the default recommendation unless latency or cost is a concern, in which case GPT-5.2-Codex provides a 40% faster session time with slightly reduced output quality.

### Model Selection via API

For CI/CD pipelines that programmatically trigger agent sessions, model selection is available via the GitHub Agent HQ REST API:

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/ORG/REPO/agent-sessions \
  -d '{"issue_number": 123, "agent": "claude", "model": "claude-opus-4-6"}'
```

## Using Agent HQ Across All Platforms (VS Code, GitHub Mobile, github.com)

GitHub Agent HQ is designed as a cross-platform orchestration layer — the same agent sessions are accessible from github.com, VS Code with the GitHub Copilot extension (v2.0+), and GitHub Mobile (iOS/Android). All three surfaces share a unified session state: an agent session started from github.com can be monitored and interacted with from VS Code without re-initialization. On github.com, the primary entry point is the issue's Assignees panel and the Agents tab in the repository navigation. In VS Code, the Copilot Chat panel shows a dedicated "Agent Sessions" view listing all active and completed sessions for the current repository; you can review agent PRs, add review comments, and approve merges without leaving the editor. GitHub Mobile provides a real-time session monitor — ideal for keeping watch on long-running refactors while away from a desktop. Agent results (PRs, commits) sync immediately across all platforms via GitHub's standard infrastructure. This means a Codex session triggered from mobile during a commute produces a PR you can immediately review and merge from VS Code when you return to your desk.

### Cross-Platform Feature Availability

| Feature | github.com | VS Code | GitHub Mobile |
|---------|-----------|---------|---------------|
| Assign issue to agent | ✅ | ✅ | ✅ |
| Live session monitoring | ✅ | ✅ | ✅ |
| Model selection | ✅ | ✅ | ❌ |
| PR review and merge | ✅ | ✅ | ✅ |
| Multi-agent comparison | ✅ | ✅ | ❌ |
| Session history | ✅ | ✅ | Limited |

## Enterprise Governance, Security, and Guardrails Setup

For enterprise teams, GitHub Agent HQ includes an Agent Control Plane that provides policy management, audit logging, and security guardrails over all agent activity across an organization. The Agent Control Plane is accessible at Organization Settings → Copilot → Agent Governance. Key controls include: agent allowlist (restrict which agents — Copilot only, or include Claude/Codex), branch protection enforcement (agents cannot target protected branches by default, and this cannot be overridden at the repo level), secret detection (agent commits are scanned by GitHub's push protection before the PR opens), and session audit logs (all agent sessions are logged with actor, model, issue reference, token consumption, and PR link for compliance review). Enterprise administrators can set organization-wide policies that override individual repository settings — for example, mandating that all Claude sessions use Sonnet 4.6 rather than Opus to control costs, or restricting Codex access to specific repositories. The audit log integrates with GitHub's existing SIEM connectors (Splunk, Azure Sentinel, Datadog) via the GitHub Audit Log streaming API, enabling centralized monitoring of AI-generated code activity alongside human developer activity.

### Setting Up a Secure Agent Policy

```yaml
# .github/copilot-agent-policy.yml
agents:
  allowed:
    - copilot-workspace
    - claude
    - codex
  branch_restrictions:
    protected_branches: block
    default_branch: block
  claude:
    max_model: claude-sonnet-4-6  # cap at Sonnet to control costs
  session_timeout_minutes: 20
audit:
  enabled: true
  log_retention_days: 90
```

## Pricing and the New Usage-Based Billing Model (June 2026)

Starting June 1, 2026, GitHub transitions all Copilot users from flat-rate seat billing to a hybrid model: the seat fee covers the baseline Copilot inline completion features, while agentic sessions (Agent HQ sessions with Claude, Codex, or the workspace agent) are billed per AI credit at $0.01 per credit. A typical Claude Sonnet 4.6 session on a medium-complexity issue consumes approximately 80–150 credits ($0.80–$1.50). Claude Opus 4.6 sessions run 3–4x higher: expect 250–500 credits ($2.50–$5.00) for comparable tasks. Codex GPT-5.4 falls between the two: roughly 100–200 credits ($1.00–$2.00) per session. Before this transition, each agent session consumed one "premium request" — a simpler model that made cost estimation difficult. The new credit model enables granular budget controls: organization admins can set monthly credit ceilings per user, per repository, or per agent type via the Billing dashboard. GitHub also provides a Credit Estimator tool (github.com/settings/copilot/agent-credits) that projects monthly spend based on historical issue assignment patterns. For most Copilot Business teams using Agent HQ 2–5 times per developer per week, the total incremental cost per developer runs $15–$40/month above the base seat fee.

| Plan | Base Seat Fee | Includes | Agent HQ Credit Budget |
|------|--------------|----------|----------------------|
| Copilot Pro | $10/mo | Completions + 1 agent | 50 credits/mo included |
| Copilot Business | $19/user/mo | All agents | 150 credits/user/mo |
| Copilot Pro+ | $39/user/mo | All agents + priority | 500 credits/user/mo |
| Copilot Enterprise | $39/user/mo | All agents + governance | Custom credit pools |

Additional credits beyond the included allotment are billed at $0.01/credit, charged monthly alongside the seat fee.

---

## Frequently Asked Questions

**Do I need separate Anthropic or OpenAI subscriptions to use Claude and Codex in Agent HQ?**

No. During the public preview, Claude and Codex access are included with GitHub Copilot Business, Pro+, and Enterprise plans. Starting June 2026, usage is billed via GitHub's AI credit system at $0.01/credit — there is no separate Anthropic or OpenAI invoice.

**Can I use GitHub Agent HQ on a free GitHub account?**

Agent HQ requires an active Copilot subscription. GitHub Free users do not have access. Copilot Individual (now called Copilot Pro at $10/month) gives access to the Copilot workspace agent only; Claude and Codex require Copilot Business or higher.

**How do I know which agent is working on my issue?**

The issue's Assignees sidebar shows the assigned agent with an AI icon indicator. The PR opened by the agent includes the agent name and model in the PR description header (e.g., "Created by Claude Sonnet 4.6 via GitHub Agent HQ"). The Agents tab in repository navigation shows all active and completed sessions with timestamps and linked PRs.

**Can agents push code directly to the main branch?**

No. By design, agents always create a feature branch and open a pull request — they cannot bypass branch protection rules or push directly to protected branches. Organization admins can enforce this policy globally via the Agent Control Plane, and it cannot be overridden at the repository level.

**What happens if an agent session fails or produces bad code?**

Agent sessions that fail (e.g., due to ambiguous requirements or exceeding the session timeout) show a "Failed" status in Mission Control with an error summary. Failed sessions do not consume AI credits. If an agent produces a PR with incorrect code, simply comment on the PR with corrections — the agent resumes the session, addresses your feedback, and pushes additional commits. You can also close the PR and re-assign the issue to a different agent to start fresh.
