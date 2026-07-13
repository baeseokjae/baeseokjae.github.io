---
title: "T3 Code Review 2026: Open-Source Control Plane for Claude Code, Codex, and OpenCode"
date: 2026-07-13T12:00:00+00:00
tags: ["t3 code", "coding agents", "claude code", "codex cli", "opencode"]
description: "A practical 2026 review of T3 Code, the open-source control plane for orchestrating Claude Code, Codex CLI, Cursor, and OpenCode from one browser UI."
draft: false
cover:
  image: "/images/t3-code.png"
  alt: "T3 Code Review 2026"
  relative: false
schema: "schema-t3-code"
---

T3 Code is not a coding agent. It is an open-source control plane that wraps Claude Code, Codex CLI, Cursor, and OpenCode under one browser UI — and that distinction matters more than any feature comparison. If you already use multiple coding agents and are tired of context-switching between terminals, the project is worth a serious look. If you expect it to replace your agent or give you free inference, you will be disappointed.

## What T3 Code Is, and What It Is Not

The most common mistake I see in reviews is treating T3 Code as a Claude Code or Codex competitor. It is not. The [T3 Code architecture docs](https://github.com/pingdotgg/t3code) describe a Node.js WebSocket server that wraps `codex app-server` over JSON-RPC stdio, serves a React/Vite web app, and translates provider runtime events into an orchestration model. In plain English: it is a desktop GUI that drives the same CLI agents you already have installed.

The taxonomy matters because it changes how you evaluate the tool. You do not compare T3 Code against Claude Code on model quality or code generation accuracy — those are inherited from whichever provider you plug in. You compare it against the experience of running those agents directly in your terminal, or against the official Codex desktop app, or against OpenCode Desktop.

T3 Code is a workflow surface. It manages projects, threads, git worktrees, diff review, integrated terminals, and PR creation. The underlying agent does the actual coding work.

## Quick Verdict for 2026

| Criteria | Verdict |
|---|---|
| Best for | Developers using 2+ coding agents who want a unified UI |
| Not for | Teams wanting a single agent replacement or free inference |
| Maturity | Early stage — v0.0.28 stable, nightly releases, 676 open issues |
| GitHub | 13,467 stars, MIT licensed, active since Feb 2026 |
| Cost | Free software, bring-your-own provider subscriptions |
| Linux support | First-class, unlike official Codex app |

I would pilot T3 Code on a side project or low-risk repo before standardizing on it. The concept is solid, the velocity is impressive, but the project is young and the provider dependencies are real.

## How T3 Code Works Under the Hood

The architecture is worth understanding because it explains both the strengths and the current limitations.

T3 Code runs a local Node.js WebSocket server that communicates with each provider's CLI over stdio. The web UI communicates with this server, which translates provider events (file changes, terminal output, agent thinking) into a unified orchestration model. The React/Vite frontend renders projects, threads, diffs, and terminals.

The key architectural detail: T3 Code is currently Codex-app-server-centric. The WebSocket server pattern mirrors how the official Codex app works, and the Claude and OpenCode providers are adapted into that same model. That means provider support quality depends on how well each CLI's event stream maps onto the Codex app-server protocol.

When you run a task in T3 Code, the flow looks like this:

```
Browser UI → Node WebSocket Server → Provider CLI (codex/claude/opencode) → stdio JSON-RPC → Events translated back to UI
```

This is more than a skin. The orchestration layer handles project isolation, thread history, checkpoint management, and multi-account switching. But it also introduces latency — every event passes through the translation layer before reaching your screen.

## Supported Providers: Codex, Claude Code, Cursor, and OpenCode

As of v0.0.28, T3 Code supports four providers:

- **Codex** — via `codex login`. Supports multiple Codex accounts using a shared `CODEX_HOME` plus optional shadow home directories for work/personal separation.
- **Claude Code** — via `claude auth login`. Supports separate Claude homes for work and personal accounts. Switching accounts inside an existing thread is not supported because different Claude homes are treated as separate environments.
- **Cursor** — via `cursor-agent login`. The newest addition to the provider list.
- **OpenCode** — via `opencode auth login`. Terminal-first users may prefer OpenCode Desktop, which drives OpenCode CLI directly rather than through the T3 Code translation layer.

The critical constraint: T3 Code inherits every backend's auth model, rate limits, subscription rules, CLI behavior, and outages. A clean UI does not remove operational complexity. If Claude Code is down, T3 Code cannot run Claude tasks. If Codex CLI has a breaking update, T3 Code may need a provider adapter update to stay compatible.

## Setup and Installation: npx, Desktop, and Provider Auth

Getting started is straightforward:

```bash
npx t3@latest
```

That is the quick-start path. The npm package `t3` (v0.0.28, published 2026-06-29) had about 22,068 downloads in the last month as of July 8, 2026. Desktop installs are also available through GitHub Releases, winget, Homebrew cask, and Arch AUR.

After installing, you need at least one provider authenticated:

```bash
codex login
# or
claude auth login
# or
cursor-agent login
# or
opencode auth login
```

Without at least one of these, T3 Code is an empty shell. This is the most common setup friction I have seen reported — new users expect the tool to work immediately after `npx t3`, not realizing they need separate provider accounts and CLI installations.

## Core Workflow: Projects, Threads, Worktrees, Diffs, Terminal, and PRs

The workflow features are where T3 Code differentiates itself from running agents directly in a terminal:

**Projects and threads.** Each project gets its own workspace with isolated thread history. This is a meaningful improvement over the terminal, where switching between tasks means scrolling through a single session log or starting a new terminal tab.

**Git worktrees.** This is the feature I find most compelling. T3 Code can create isolated git worktrees for each agent task, so the agent works on a separate copy of the codebase without touching your working tree. If the agent breaks something, your main branch is untouched. This is a real safety improvement over running agents directly in your working directory.

**Diff review.** Before applying changes, T3 Code shows a diff view. You can review what the agent changed, accept or reject individual files, and commit selectively. This is the review workflow that terminal agents lack by default — with Claude Code or Codex CLI, you either trust the agent or read the diff in a separate tool.

**Integrated terminal.** You can run commands alongside the agent without leaving the UI. Useful for running tests, checking build output, or inspecting files while the agent works.

**PR creation.** T3 Code can create pull requests from completed worktree changes. The flow is: agent finishes → review diff → commit → push → create PR. All from the same UI.

## Provider and Account Management: Codex Shadow Homes vs Claude Homes

If you manage multiple accounts — work and personal, or client projects — T3 Code's account management is worth understanding.

For Codex, T3 Code supports a shared `CODEX_HOME` plus optional shadow home directories. This lets you switch between work and personal Codex accounts while preserving shared session history when compatible. The shadow home approach means each account gets its own configuration and auth state, but they can share a common session cache.

For Claude Code, the approach is different. Each Claude home is treated as a completely separate environment. You can configure multiple Claude homes for different accounts, but switching accounts inside an existing thread is not supported. If you start a thread with your work Claude account, you cannot switch to your personal account mid-thread.

In practice, this means you should plan your account strategy before starting a project. Create separate projects for work and personal work, each configured with the appropriate provider account.

## T3 Code vs Codex App

The official Codex app is the most direct comparison. Both provide a desktop GUI for Codex CLI. The differences:

| Feature | T3 Code | Official Codex App |
|---|---|---|
| Open source | Yes (MIT) | No |
| Linux support | First-class | Limited |
| Multi-provider | Codex, Claude, Cursor, OpenCode | Codex only |
| Worktrees | Yes | No |
| Diff review | Yes | Yes |
| PR flow | Yes | Limited |
| Provider auth | BYO credentials | Integrated |
| Maturity | Early stage (v0.0.28) | Production |

If you only use Codex and are happy with the official app, there is little reason to switch. If you use multiple agents or need Linux support, T3 Code becomes more attractive.

## T3 Code vs Claude Code

This comparison is trickier because Claude Code is a terminal-first agent, not a GUI. T3 Code wraps Claude Code in a browser UI, adding project management, worktrees, and diff review that Claude Code lacks natively.

But there is a trade-off. Running Claude Code through T3 Code means you lose some of the terminal-native experience: direct pipe support, shell integration, and the ability to script Claude Code into CI/CD pipelines. If your workflow depends on piping Claude Code output into other tools, the T3 Code wrapper adds friction.

For teams that want Claude Code with better review and isolation, T3 Code is worth trying. For power users who live in the terminal, Claude Code directly is probably still the better choice.

## T3 Code vs OpenCode Desktop

[OpenCode Desktop](https://www.answeroverflow.com/m/1479853819549581493) is the closest architectural cousin to T3 Code. Both provide a GUI over a CLI agent. The difference: T3 Code drives Claude Code or Codex CLI under the hood, while OpenCode Desktop drives OpenCode CLI under the hood.

If you are already using OpenCode as your primary agent, OpenCode Desktop is the natural fit. If you use multiple agents and want one UI, T3 Code makes more sense.

## Strengths: Open Source, Linux-Friendly, Unified UI, and Forkability

T3 Code's strengths are real:

**Open source (MIT).** You can inspect the code, fork it, and customize it. For teams with compliance requirements, this is a significant advantage over proprietary tools.

**Linux support.** Unlike the official Codex app, T3 Code works on Linux out of the box. For Linux-first teams, this alone can be the deciding factor.

**Unified UI.** If you use Claude Code for refactoring, Codex for test generation, and Cursor for frontend work, T3 Code gives you one interface instead of three. The project/thread model keeps work organized across agent switches.

**Forkability.** Because T3 Code is open source and the architecture is documented, teams can fork it and add custom providers, internal tool integrations, or compliance controls.

## Weaknesses and Risks: Early Stage, Provider Dependencies, Performance Reports, and Open Issues

The weaknesses are equally real:

**Early stage.** T3 Code is at v0.0.28. The GitHub repository shows 676 open issues as of July 10, 2026. That is a lot of open issues for a project with 13,467 stars. Some are feature requests, but many are bugs.

**Provider dependencies.** T3 Code is only as reliable as its provider adapters. If Codex CLI changes its stdio protocol, T3 Code breaks until the adapter is updated. If Claude Code adds a new feature, T3 Code may not surface it immediately.

**Performance reports.** [GitHub issue #695](https://github.com/pingdotgg/t3code/issues/695) reports a concerning latency gap: the same repository-investigation task completed in Codex in about 4 minutes 35 seconds but took more than 15 minutes in T3 Code under the same model configuration. That is a 3x+ overhead. The issue is still open, and the root cause is not fully understood. If you are running long agent tasks, this is worth testing before committing to T3 Code.

**Changing provider landscape.** The provider support list has already changed since the project started. Cursor was added recently. Future providers may be added or existing ones may break. The project's velocity is high, but that also means instability.

## Pricing and Cost Reality: Free Software, Bring-Your-Own Inference

T3 Code is free. The software costs nothing. But the inference costs are whatever your provider charges.

If you use Claude Code, you pay Anthropic's rates. If you use Codex, you pay OpenAI's rates. If you use Cursor, you pay Cursor's subscription. T3 Code does not add its own inference markup, but it also does not reduce your provider costs.

The one cost consideration: if T3 Code's reported performance overhead (issue #695) is real and general, you may pay more in provider tokens for the same work because tasks take longer and may require more retries or re-reading context.

## Who Should Use T3 Code

- **Multi-agent users.** If you regularly switch between Claude Code, Codex, and Cursor, T3 Code's unified UI saves real context-switching overhead.
- **Linux developers.** If you are on Linux and want a GUI for coding agents, T3 Code is currently the best option.
- **Teams that want review workflows.** The diff review and worktree isolation are genuine improvements over running agents directly.
- **Open-source enthusiasts.** If you want to customize your coding agent UI or contribute to the ecosystem, T3 Code's MIT license and documented architecture make that possible.

## Who Should Skip It for Now

- **Single-agent users.** If you only use one coding agent, the official app or terminal is probably a better experience.
- **Performance-sensitive teams.** If every minute of agent runtime matters, the reported latency overhead is a real concern. Test your specific workload before committing.
- **Teams needing production stability.** With 676 open issues and nightly releases, T3 Code is not yet a tool I would standardize across a large engineering organization.
- **Terminal power users.** If your workflow depends on pipes, shell scripts, and CI/CD integration with your coding agent, the T3 Code wrapper adds friction rather than value.

## Hands-On Evaluation Checklist

If you want to evaluate T3 Code for your team, here is the checklist I would follow:

1. Install one provider (`codex login` or `claude auth login`)
2. Run a read-only audit task (e.g., "list all unused dependencies")
3. Run a worktree-backed edit task (e.g., "refactor this function")
4. Inspect the diff and accept/reject individual changes
5. Run tests in the integrated terminal
6. Create a PR from the completed worktree
7. Compare latency against the same task in the underlying CLI directly
8. Test provider switching (e.g., start a task with Codex, switch to Claude)
9. Test account switching (work vs personal, if applicable)

## Final Verdict: Is T3 Code the Right Control Plane for Your Coding Agents?

T3 Code solves a real problem: the fragmentation of coding agent UIs. If you use multiple agents, the project/thread model, worktree isolation, and diff review are genuine workflow improvements over running agents in separate terminals.

But the project is early. The reported performance gap, the high open-issue count, and the dependency on provider CLI stability mean this is not yet a tool I would bet a production team on. I would pilot it on a side project, contribute bug reports, and watch the velocity. If the project maintains its current pace through the end of 2026, it could become the default control plane for multi-agent development.

For now, T3 Code is the most promising open-source control plane for coding agents — with the emphasis on "promising." The foundation is solid, but the house is still being built.

For more on coding agent tooling, see my reviews of [OmniRoute's 231-provider gateway](/posts/omniroute-231-provider-gateway/) for AI gateway infrastructure, the [Claude Code dev team stack](/posts/claude-code-dev-team-stack-skills-mcp-2026/) for practical agent workflows, and [Grok Build](/posts/grok-build-coding-agent/) for another take on the terminal coding agent landscape.

## FAQ

### Is T3 Code free?

Yes, T3 Code is free and open source under the MIT license. You pay only for the provider subscriptions (Claude Code, Codex, Cursor, or OpenCode) that you use through it.

### Does T3 Code work on Linux?

Yes, T3 Code has first-class Linux support, unlike the official Codex app. It also works on macOS and Windows through Homebrew cask, winget, and GitHub Releases.

### Can T3 Code replace Claude Code or Codex?

No. T3 Code is a UI wrapper that drives Claude Code, Codex, Cursor, or OpenCode under the hood. You still need those tools installed and authenticated. T3 Code does not generate code or run inference itself.

### Is T3 Code slower than running agents directly?

There are reports of performance overhead. [GitHub issue #695](https://github.com/pingdotgg/t3code/issues/695) documents a case where the same task took 15+ minutes in T3 Code versus 4m35s in Codex directly. The root cause is not fully understood, and the issue remains open. Test your specific workload.

### How do I install T3 Code?

Run `npx t3@latest` for the quick start, or install through GitHub Releases, winget, Homebrew cask, or Arch AUR. You will also need at least one provider authenticated (`codex login`, `claude auth login`, `cursor-agent login`, or `opencode auth login`).
