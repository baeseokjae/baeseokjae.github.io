---
title: "Succubus: Cross-Agent Coordination Daemon for AI Coding Agents — Full Review"
date: 2026-07-30T16:03:18+00:00
tags:
  - AI Coding Agents
  - Multi-Agent Coordination
  - Succubus
  - MCP
  - Developer Tools
  - Open Source
description: "Succubus is a Go daemon that coordinates multiple AI coding agents via file claims, shared task boards, and lifecycle hooks — preventing conflicts in shared repositories."
draft: false
cover:
  image: "/images/succubus-cross-agent-coordination-2026.png"
  alt: "Succubus: Cross-Agent Coordination Daemon for AI Coding Agents — Full Review"
  relative: false
schema: "schema-succubus-cross-agent-coordination-2026"
---

## What is Succubus?

Succubus is an open-source, single-binary daemon written in Go that coordinates multiple AI coding agents working on the same repository. It prevents the "blind multi-agent" problem — where two or more AI agents edit the same files without knowing about each other — by providing file claims with lease-based locking, a shared task board, inter-agent communication, and a real-time dashboard. Created by enowx labs and released on July 28, 2026, Succubus supports eight different AI coding tools including Claude Code, Codex CLI, Gemini CLI, Cursor CLI, and Aider, and integrates via both MCP server and mandatory lifecycle hooks.

## The Problem — Why Do AI Coding Agents Need Coordination?

AI coding agents are becoming indispensable for software development. Developers routinely run multiple agents in parallel — one refactoring a backend module while another updates tests and a third writes documentation. The problem is that these agents operate in isolation. Each agent sees the repository as it was when it started, not as it is right now. When Agent A modifies `auth.go` and Agent B simultaneously rewrites the same function, the result is merge conflicts, lost work, and corrupted state.

This is the "blind multi-agent" problem. Without a coordination layer, each agent is a solo performer in what should be an ensemble production. The industry has tried various solutions — git hooks, manual task assignment, sequential agent runs — but none provide real-time awareness of what other agents are doing. Succubus addresses this gap by acting as a shared state server that every agent must register with before touching any file.

## Architecture Overview — How Does Succubus Work?

Succubus is a daemon process that runs on the developer's machine and exposes two integration surfaces: an MCP server for opt-in tool access, and lifecycle hooks for mandatory registration. The daemon uses an embedded SQLite database (via `modernc.org/sqlite`, its only non-stdlib dependency) to store agent identities, file claims, task board items, and agent room messages.

### One Binary, Four Modes

Succubus ships as a single Go 1.26 binary with four operating modes:

- **Daemon mode** — runs the background server that manages all coordination state
- **Dashboard mode** — serves a real-time web UI built with React 19 and Vite
- **CLI mode** — command-line interface for manual queries and management
- **MCP server mode** — exposes coordination primitives as MCP tools for agent consumption

The binary is cross-platform, supporting macOS, Linux, and Windows on both amd64 and arm64 architectures. There are no runtime dependencies — no Node.js, no Python, no database server. Just a single executable.

### Storage and Project Identity

Succubus stores all state in an embedded SQLite database. Project identity is derived from the git remote URL: the remote is normalized and hashed with SHA-256, and the first 12 hex characters become the project ID. This means a single Succubus daemon can serve multiple projects on the same machine, with each project's state fully isolated by its project ID.

Agent identity is cached locally at `.succubus/agent-<session>.json`, which survives context compaction — a critical detail for agents like Claude Code that may lose context between sessions. When an agent resumes work, it reads its cached identity rather than registering as a new agent.

## Key Features — What Can Succubus Do?

### Agent Identity and Registration

Every agent that connects to Succubus receives a curated identity from a pool of 32 names — ORION, VESPER, KESTREL, NEXUS, and others. These identities persist across sessions via the local cache file, enabling the daemon to track agent history, heartbeat status, and claim ownership over time.

The heartbeat system uses three thresholds: agents ping every 30 seconds, are marked idle after 90 seconds of silence, and are declared dead after 300 seconds. This allows the daemon to detect crashed or disconnected agents and release their file claims automatically.

### File Claims with Intelligent Leases

The file claim system is Succubus's core feature. When an agent wants to edit a file, it must first claim it. The claim is a conditional UPSERT operation with a default TTL of 900 seconds (15 minutes). Claims can be released under four conditions:

1. **Freed** — the agent voluntarily releases the claim after finishing edits
2. **Expired** — the TTL elapses without renewal
3. **Renewal** — the agent extends its claim (normal operation for long edits)
4. **Dead holder** — the agent's heartbeat stops and it's declared dead

This design elegantly handles edge cases. If an agent crashes mid-edit, its claims expire automatically. If an agent is slow but still alive, it renews its lease. If two agents want the same file, the second one is told who holds the claim and can either wait or negotiate via the agent room.

### Shared Plan and Task Board

Succubus includes a Kanban-style task board with dependency tracking and cycle detection. Agents can create tasks, assign them to specific agents (or leave them unassigned), mark dependencies between tasks, and update status. The board supports the full Kanban workflow: backlog, in progress, in review, and done.

The cycle detection is particularly important for multi-agent workflows. If Agent A depends on Agent B, and Agent B depends on Agent A, the system flags the circular dependency before work begins — preventing the kind of deadlock that can stall an entire multi-agent pipeline.

### Agent Room for Inter-Agent Communication

One of Succubus's most innovative features is the agent room — a shared Q&A space where agents can ask each other questions, mention specific agents with @mentions, and track resolution status. This enables patterns like:

- Agent A: "I need to refactor `auth.go` — does anyone hold a claim on it?"
- Agent B: "I do, but I'm almost done. Wait 2 minutes."
- Agent A: "Confirmed. I'll claim it after your release."

Without the agent room, this kind of coordination would require human intervention. With it, agents can self-coordinate, reducing the human's role to oversight rather than traffic control.

### Real-Time Dashboard

The dashboard is embedded directly in the Succubus binary — no separate build step, no deployment. It's built with React 19 and Vite, uses lucide-react for icons, and deliberately avoids Tailwind and component libraries. The dashboard shows:

- Active agents and their heartbeat status
- Current file claims with remaining TTL
- Task board with dependency graph
- Agent room messages and resolution status
- System health and configuration

This gives human developers real-time visibility into what their AI agents are doing — essential for trust and oversight in multi-agent workflows.

## Tool Support and Integration — Which Agents Can Use Succubus?

Succubus supports eight AI coding tools out of the box:

| Tool | Integration Type | Notes |
|------|-----------------|-------|
| Claude Code | Hooks + MCP | Full support with lifecycle hooks |
| Factory Droid | Hooks + MCP | Full support |
| Codex CLI | Hooks + MCP | Full support |
| Gemini CLI | Hooks + MCP | Full support |
| OpenCode | Hooks + MCP | Full support |
| Cursor CLI | Hooks + MCP | Full support |
| Copilot CLI | Hooks + MCP | Full support |
| Aider | Hooks + MCP | Full support |

### MCP Server

The MCP (Model Context Protocol) server exposes Succubus's coordination primitives as tools that agents can call. This is the opt-in integration path — agents that support MCP can discover and use Succubus's features without any custom configuration. The MCP server provides tools for claiming files, querying the task board, sending agent room messages, and checking agent status.

### Lifecycle Hooks

Lifecycle hooks are the mandatory integration path — and this is Succubus's key design insight. Hooks are shell scripts that run before and after every agent operation (file read, file write, command execution). They register the agent with the daemon, claim files before edits, and release claims after edits. Because hooks are mandatory (they run as part of the agent's execution environment), agents cannot opt out of coordination.

The hooks are designed with a "degrade to nothing" philosophy: if the Succubus daemon is not running, the hooks exit silently and let the agent proceed normally. This means Succubus never blocks development — it only adds coordination when the daemon is available.

### AGENTS.md and Agent Skills

Succubus also generates an `AGENTS.md` file in the project root that describes the coordination rules and agent identities. This file serves as a shared context document that every agent reads at startup, ensuring consistent behavior across different agent types. Combined with agent skills (reusable instruction sets), this creates a comprehensive coordination framework that goes beyond simple file locking.

## Enforcement Tiers — How Strict Is the Coordination?

Succubus offers three enforcement tiers that let teams choose their comfort level:

| Tier | Behavior | Use Case |
|------|----------|----------|
| **Off** | Hooks register agents but do not enforce claims | Exploration and evaluation |
| **Nag** (default) | Hooks warn when agents violate claims but do not block | Teams building trust in the system |
| **Block** | Hooks prevent agents from editing claimed files | Production multi-agent workflows |

The default is "nag" — a gentle reminder that another agent holds the claim. This lets teams adopt Succubus gradually, starting with awareness and moving to enforcement as they gain confidence.

## How File Claims Work — Technical Deep Dive

The file claim system uses a conditional UPSERT pattern in SQLite. When an agent requests a claim on `src/auth.go`, the daemon executes:

1. Check if a claim exists for `src/auth.go` with an active (non-expired) lease
2. If no claim exists, insert a new claim with the requesting agent's identity and a 900-second TTL
3. If a claim exists and is held by the same agent, renew the TTL
4. If a claim exists and is held by a different agent, return the current holder's identity

The TTL is refreshed on every heartbeat, so as long as the agent is alive and working, its claims remain valid. If the agent crashes, the heartbeat stops, the agent is declared dead after 300 seconds, and all its claims are released.

This design is remarkably robust. It handles:
- **Graceful shutdown**: agent releases all claims before exiting
- **Crash recovery**: claims expire via TTL
- **Network partition**: agent reconnects and renews claims
- **Long-running edits**: agent periodically renews its lease
- **Dead agent detection**: heartbeat timeout triggers claim release

## Comparison with Alternatives

Succubus is not the only tool attempting to solve multi-agent coordination. Here is how it compares with the alternatives:

| Feature | Succubus | Bazinga | Batty | Forge Orchestrator | Agent Hub MCP |
|---------|----------|---------|-------|-------------------|---------------|
| Language | Go 1.26 | N/A | N/A | Rust | N/A |
| Binary size | ~10MB | N/A | N/A | ~3MB | N/A |
| File claims | Yes (TTL leases) | No | No | No | No |
| Task board | Yes (Kanban + deps) | No | No | No | No |
| Agent room | Yes | No | No | No | No |
| Dashboard | Yes (React 19) | No | No | No | No |
| MCP server | Yes (opt-in) | No | No | Yes (only) | Yes (only) |
| Lifecycle hooks | Yes (mandatory) | No | No | No | No |
| Enforcement tiers | 3 tiers | No | No | No | No |
| Tool support | 8 agents | 1 agent | 1 agent | Limited | Limited |
| Dependencies | 1 (SQLite) | N/A | N/A | Minimal | N/A |
| License | MIT | MIT | MIT | MIT | MIT |

**Bazinga** focuses on enforced engineering practices and code quality gates rather than cross-agent coordination. It is a useful tool for ensuring agents follow coding standards, but it does not solve the file conflict problem.

**Batty** runs teams of AI coding agents in tmux sessions with test gating. Its approach is more about parallel execution orchestration than shared awareness — agents run in isolated terminals without knowing about each other.

**Forge Orchestrator** is the closest alternative in terms of design philosophy. It is a 3MB Rust binary that coordinates multi-AI agents via MCP. However, it relies exclusively on MCP (no hook system), meaning agents must opt in to coordination. Succubus's hook-based approach ensures every agent participates, whether they support MCP or not.

**Agent Hub MCP** provides universal coordination via MCP but lacks the hook-based enforcement that makes Succubus's coordination mandatory. It is a lighter-weight solution for teams that already use MCP-compatible agents exclusively.

**OpenRig** takes a different approach entirely — it is a control plane for multi-agent coding topologies, more focused on infrastructure management than per-file coordination.

## Getting Started with Succubus

Getting started with Succubus is straightforward:

1. **Download the binary** from the GitHub releases page for your platform
2. **Start the daemon**: `succubus daemon`
3. **Install hooks** in your project: `succubus install-hooks`
4. **Configure enforcement tier** in `.succubus/config.yaml` (default: nag)
5. **Run your AI coding agents** as normal — hooks handle registration automatically
6. **Open the dashboard** at `http://localhost:8080` to see real-time activity

The daemon runs in the background and consumes minimal resources — the embedded SQLite database and Go runtime keep memory usage under 50MB in typical use.

## FAQ

### What problem does Succubus solve?

Succubus solves the "blind multi-agent" problem where multiple AI coding agents edit the same repository without awareness of each other, causing file conflicts, lost work, and merge issues. It provides real-time coordination through file claims, shared task boards, and inter-agent communication.

### Does Succubus work with all AI coding agents?

Succubus supports eight AI coding tools out of the box: Claude Code, Factory Droid, Codex CLI, Gemini CLI, OpenCode, Cursor CLI, Copilot CLI, and Aider. It integrates via both MCP server (opt-in) and lifecycle hooks (mandatory), so any agent that supports shell hooks can be integrated.

### Will Succubus block my work if the daemon crashes?

No. Succubus follows a "degrade to nothing" philosophy — if the daemon is not running, the lifecycle hooks exit silently and agents proceed normally. The daemon never blocks development; it only adds coordination when available.

### How does Succubus handle crashed agents?

Succubus uses a heartbeat system where agents ping every 30 seconds. If an agent misses heartbeats for 90 seconds it is marked idle, and after 300 seconds it is declared dead. All file claims held by a dead agent are automatically released, preventing permanent locks.

### Is Succubus free and open source?

Yes. Succubus is released under the MIT license and is available on GitHub at github.com/enowdev/succubus. It is written entirely in Go 1.26 with exactly one non-stdlib dependency (modernc.org/sqlite), making it easy to build from source or use the pre-built binaries.

## Conclusion — Is Succubus Ready for Production?

Succubus is remarkably polished for a project that is less than a week old. The architecture is clean, the design decisions are well-considered, and the implementation is minimal and focused. The hook-based registration system is the right approach for solving the blind multi-agent problem — it ensures participation without requiring agent modifications.

The file claim system with conditional UPSERT and TTL-based leases handles edge cases that more naive implementations would miss. The agent room enables a level of self-coordination that reduces human overhead. The dashboard provides the visibility that teams need to trust autonomous agents.

The main risk is maturity. With 13 GitHub stars and 2 forks as of July 2026, Succubus has not been battle-tested at scale. The single-developer (enowx labs) backing means bus-factor is a concern. However, the MIT license means the project can be forked and maintained independently if needed.

For teams running multiple AI coding agents on the same repository, Succubus is worth evaluating today. The "nag" enforcement tier provides a low-risk way to test the system, and the "degrade to nothing" design means there is no downside to installing the hooks. As multi-agent workflows become the norm in software development, tools like Succubus will transition from nice-to-have to essential infrastructure.
