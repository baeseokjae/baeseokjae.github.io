---
title: "Swarm: Local-First Control Plane Agent Watching Every Claude Code Session Live"
date: 2026-09-05T13:01:48+00:00
tags:
  - claude-code
  - multi-agent-orchestration
  - local-first
  - observability
  - agent-control-plane
  - git-worktree
  - ai-agent-swarm
description: "Swarm is a local-first control plane agent that watches every Claude Code session live, stops collisions, and enforces CLAUDE.md rules offline."
draft: false
cover:
    image: "/images/swarm-local-control-plane-claude-code-2026.png"
    alt: "Swarm: Local-First Control Plane Agent Watching Every Claude Code Session Live"
    relative: false
schema: "schema-swarm-local-control-plane-claude-code-2026"
---

A local-first control plane agent like Swarm watches every Claude Code session on your machine live so you can see each agent's tool calls, reasoning, token spend, and cost from one dashboard instead of cycling through terminal tabs. It keeps a ledger of who holds which task and worktree, turns CLAUDE.md "never do X" prose into real permission decisions, and runs entirely offline with no account and no telemetry.

## What Is a Local-First Control Plane for Coding Agents?

A control plane is the management layer that decides how the agents underneath it behave. In IT operations, the control plane and the data plane are separated: the data plane does the work, while the control plane watches, meters, and governs. [ra3orblade/swarm](https://github.com/ra3orblade/swarm) applies that same separation to AI coding agents, with one crucial twist: the entire control plane runs on your own machine.

Swarm is a TypeScript/Bun project, Apache-2.0 licensed, that installs with a single command — `bunx @ra3orblade/swarm setup`. Once running, one daemon watches every Claude Code session live, along with Codex CLI, Gemini, Grok, Aider, and opencode sessions. For each one it captures the live reasoning stream, tool calls, token spend, and running cost. It does not add anything to your repositories, requires no account, no telemetry, and works fully offline.

The word "swarm" here means the control plane manages a *group* of agents, not a single session. The tagline says it best: "See every agent. Stop the collisions."

## The Problem: Losing the Thread Across Multiple Agent Sessions

Anyone who runs more than one or two coding agents in parallel has felt this specific frustration. You have three terminal tabs open, each running a different Claude Code or Codex session. To know what any of them is doing you have to switch tabs, scroll through logs, and piece together what the agent thinks it is doing versus what it is actually doing. When two agents touch the same file or the same port, the results are silent merge conflicts and a mystery about who killed your dev server.

The problem compounds as teams grow. Anthropic made agent *teams* a first-class Claude Code feature in early 2026 — a lead agent that delegates to parallel teammates that research, debug, and build while coordinating ([Addy Osmani, Feb 2026](https://addyosmani.com/blog/claude-code-agent-teams/)). Community tooling had already been calling these workflows "swarms" — coordinated teams of specialist agents. But a team of agents running against the same repository without a shared view of state is a recipe for collisions.

## Swarm's Core Screens: Fleet, Session, Board

Swarm organizes its observability around four main screens, each answering a different operational question.

**Fleet** is the at-a-glance view of every agent running on your machine. You see the full list of sessions, which CLI each one is using, and its live status. This is the replacement for the terminal-tab shuffle — instead of guessing which terminal holds which agent, you get one pane that answers "what is running right now?"

**Session** is the deep-dive view for a single agent. It shows the live reasoning stream, every tool call, and the running token and cost counters. Because Swarm is local-first, it records the full transcript to disk, which enables session replay — you can rewatch what an agent did even after it finished — and a "resume-where-it-died" flow that lets you restart an interrupted session from its exact state.

**Board** is the coordination surface: which task each agent holds, which worktree, and which runtime resources. This is where Swarm's collision-prevention story lives. A collision graph shows conflicts explicitly rather than letting them surface as surprise merge conflicts later.

Together these three screens form what the project calls the missing "observability layer" for the multi-agent age — one daemon watching every session instead of cycling through terminal tabs.

## Turning CLAUDE.md Guardrails into Real Permission Decisions

The cleverest idea in Swarm is that it converts documentation into enforcement. A CLAUDE.md file often says things like "never run `git push --force`" or "don't kill random processes" — but that is prose. Claude Code reads it as a style hint. Nothing structurally stops a session from running a destructive command.

Swarm adds a `Rules` set that turns those instructions into real permission decisions. The rules target Bash commands a Claude Code session runs: `shared_tree`, `destructive_git`, `pattern_kill`, `protected_ports`, `no_foreign_worktree`, and the opt-in `claim_required_to_write`. Each rule is set to `ask`, `deny`, or `off` per repo in a `.swarm.toml`. When a rule fires, Swarm returns an actual permission denial to Claude Code rather than leaving the decision to chance.

This is explicitly not a sandbox. Swarm is guardrails against accidents, not a security boundary. A determined agent could still work around it. But for the common failure mode — an agent running `git clean -fdx` in the wrong directory, or binding a port that your dev server already owns — a `deny` rule stops the accident before it starts.

## Coordination Through Git Worktrees and Runtime Resources

Collisions are the core coordination story, and Swarm attacks them from two directions at once: task claims in isolated git worktrees, and runtime resources.

Git worktrees are Swarm's default isolation mechanism. Each agent gets its own worktree, so parallel sessions are less likely to write over each other's files. The `claim_required_to_write` rule (opt-in) reinforces this: an agent must hold an explicit claim on a task and its worktree before it may write. This is a concrete answer to the classic multi-agent problem of two agents editing the same file.

Runtime resources are the second half. Ports, dev servers, and databases become named singletons. Because Swarm is watching every session, it knows which agent holds which resource. When a second agent tries to start on a port that is already claimed, the collision graph flags it instead of letting both agents silently fight over the same socket. For anyone who has lost a dev server to a rampaging agent this is the feature that pays for itself.

## Run & Dispatch, Handoffs, and the Built-in Reviewer

Beyond observation, Swarm ships orchestration features that make it a genuine control plane rather than just a telescope.

**Run & Dispatch** covers the spawning side. `swarm run` and `swarm dispatch` let you start agent tasks from the control plane, including headless agents running in git worktrees. Declarative workflows let you define multi-step processes the agents follow.

**Handoffs** and **agent-to-agent messaging** let one agent pass a task to another cleanly. This mirrors the delegation patterns that make agent teams productive: a lead agent plans, delegates, and synthesizes rather than writing everything itself, which keeps its context clean and reduces token usage.

**Verification gates** come with a built-in reviewer. When an agent finishes work, the control plane can require a review pass before the task is accepted. This connects directly to Cursor's finding that stacked review is high-return because review is cheaper than the work it audits — the reviewer agent is a cheap insurance policy against low-quality output.

## Local-First by Design: No Account, No Telemetry, Works Offline

The privacy architecture is central to Swarm's identity. Everything runs entirely on your machine: no account, no telemetry, works offline, and nothing is added to your repositories. For a tool whose entire job is to record complete agent conversation histories, that local-first stance is not a footnote — it is the point.

The contrast with built-in tooling is stark. Claude Code's "Swarms" feature (which leaked via [Hacker News in Jan 2026](https://news.ycombinator.com/item?id=46743908), 521 points and 335 comments) ships behind a feature flag that *phones home to the backend.* The controversy centered on privacy: the telemetry captures "Claude session JSONL files (when accessible)" — complete conversation histories. With Swarm, those same transcripts never leave your machine.

If your agents work on proprietary codebase, or if you are under a compliance regime that forbids sending source context to a third party, a local-first control plane is the difference between being able to run swarms at all and being blocked.

## The Economics of Agent Swarms: Cost, Tokens, and Review

Swarm's live token spend, cost-per-turn, cache hit rate, and budgets directly address the economics of running many agents. [Cursor's agent-swarm economics post](https://cursor.com/blog/agent-swarm-model-economics) (2026-07-20) is the anchor here: an earlier-2026 browser swarm peaked at roughly 1,000 commits per hour on Git, while the new system peaks at around 1,000 commits per *second*. Better coordination delivers similar quality at a fraction of the cost.

Delegation is the mechanism that makes swarms cheaper. When a team lead delegates, subagents get fresh, focused contexts, which leads to less token usage and better reasoning. Swarm's observability lets you watch that cost in real time rather than discovering it in a monthly invoice.

The economics argument is not uncontested. An [Hacker News thread from Jul 2026](https://news.ycombinator.com/item?id=48982535) pushed back: only models trusted to work autonomously still cost more than a human employee, and there is real concern about reviewing copious generated code. The mitigation is automated reviewer agents and verification gates — which is exactly the stack Swarm ships.

## Swarm vs. Claude Code's Built-in Swarms and Other Control Planes

Swarm is not the only local-first control plane on the market, and it sits alongside — not against — Anthropic's built-in Swarms. Here is how they compare.

| Capability | Swarm (ra3orblade) | Swarmery | Claude Code built-in Swarms |
|---|---|---|---|
| Locality | Local-first, offline, no account | Local-first, 100% local data | Phones home, feature-flagged |
| Runtime | TypeScript/Bun | Go 1.25 binary + React 19 UI | Native Claude Code feature |
| Session observation | Tool calls, reasoning, tokens, cost | Tool calls, diffs, cost, sub-agents | Within the harness |
| Permission enforcement | CLAUDE.md → ask/deny rules | Approve/deny queue, auto-approve | Built-in prompt approvals |
| Isolation | Git worktrees + runtime claims | Git worktrees, cards | Delegation mode |
| License | Apache-2.0 | Control plane PolyForm NC, framework Apache-2.0 | Proprietary |
| Cost tracking | Live spend, budgets, cache rate | Cost per session | Via usage metrics |

Swarmery is the closest direct competitor — a Go/React local-first control plane that listens on `:7777`, backfills from `~/.claude/projects` JSONL transcripts with zero instrumentation, and gives you a permission-approval queue. The [HN debate](https://news.ycombinator.com/item?id=46743908) about built-in Swarms vs third-party wrappers (Conductor, Gas Town, claude-flow, GSD, and others) framed the deciding factor as tight integration into the harness plus delegation mode and a mailbox system. Swarm's bet is that a neutral, CLI-agnostic control plane that watches *six* different CLIs is more valuable than being locked into one harness.

## Privacy and the Sovereignty Argument

Sovereignty is the deepest reason to prefer a local-first control plane. When your agent transcripts and source context stay on your machine, you retain full control over who can access them, how long they are retained, and what happens to them when you stop using the tool. You are not at the mercy of a vendor's retention policy or a backend outage.

This matters more as agents become more capable and are trusted with more sensitive work. If an agent is going to read your private schema, customer data references, or proprietary algorithms, the tool that records that work should not silently upload it. Swarm's design — no account, no telemetry, fully offline — is engineered to make that guarantee structural rather than aspirational.

## Who It's For, Limitations, and Getting Started

Swarm is early but real. As of its launch window it had eleven releases in roughly two weeks, is dogfooded daily (the project notes "Swarm dispatches its own tasks"), and covers observability across six agent CLIs. It is a rapidly moving, shipping-fast tool — but it is also young, with a small star count and a single-digit release history.

It is for developers and teams who run multiple coding agents in parallel and have felt the collision problem: parallel worktrees fighting over files, agents stealing ports, and a nagging inability to see the whole fleet at once. It is especially attractive if you need offline operation or cannot send code to a third party.

Its limitations are honest ones. With a small community and young codebase, you should expect rough edges and rapid change rather than a mature product. Its rules are guardrails, not a security sandbox. And the ecosystem is young enough that you will likely need to configure and shape it to your workflow.

Getting started is a one-liner: `bunx @ra3orblade/swarm setup`. From there you point it at your repositories, define your `.swarm.toml` rules, and start watching your sessions from the Fleet. There is no account to create and nothing to host.

## Verdict: Is Swarm Worth Running Today?

If you run only a single agent occasionally, a full control plane is probably overkill. But if you already run multiple agents in parallel — or you are planning a real agent team — Swarm is worth serious consideration today. It solves a problem built-in tooling leaves open, it does it locally and offline, and it is moving fast enough that its early rough edges are likely to harden quickly.

The honest caveats remain: it is early, the community is small, and the enforcement rules are guardrails rather than a sandbox. But the core value proposition — see every agent, stop the collisions, keep it all on your machine — is exactly the missing observability layer for the multi-agent age. For teams ready to run code agents like a fleet rather than a pile of terminal tabs, Swarm is today's most credible local-first answer.

## FAQ

**What exactly does a local control plane agent like Swarm do?**
It runs a daemon on your machine that watches every Claude Code (and Codex, Gemini, Grok, Aider, opencode) session live, capturing reasoning, tool calls, token spend, and cost, and surfaces them all in one Fleet dashboard. It also coordinates tasks so parallel agents don't collide.

**Is Swarm safe to use with proprietary code?**
Yes. Swarm is local-first by design — no account, no telemetry, works offline, and adds nothing to your repositories. Your agent transcripts and source context never leave your machine, which is a structural contrast to built-in features that phone home.

**How does Swarm stop multiple agents from colliding?**
It issues task claims in isolated git worktrees and manages runtime resources (ports, dev servers, databases) as named singletons. A collision graph flags conflicts explicitly, and the opt-in `claim_required_to_write` rule forces an agent to hold a claim before writing.

**Can Swarm enforce my CLAUDE.md rules?**
Yes. Swarm converts CLAUDE.md "never do X" prose into real permission decisions via rules like `destructive_git`, `pattern_kill`, and `protected_ports`, each set to ask, deny, or off per repo in `.swarm.toml`. It returns actual permission denials rather than leaving behavior to chance.

**Which agent CLIs does Swarm observe?**
Swarm watches every Claude Code session plus Codex CLI, Gemini, Grok, Aider, and opencode — six CLI types in total. It is CLI-agnostic, which distinguishes it from control planes locked into a single harness.
