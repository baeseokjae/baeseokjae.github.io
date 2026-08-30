---
title: "Open-Source Memory for Coding Agents, Synced Over SSH: The Complete Guide"
date: 2026-08-24T10:01:16+00:00
tags:
  - agent memory
  - coding agents
  - SSH
  - Claude Code
  - AGENTS.md
  - git sync
  - MCP
draft: false
cover:
  image: "/images/open-source-memory-for-coding-agents-synced-over-ssh.png"
  alt: "Open-Source Memory for Coding Agents, Synced Over SSH"
  relative: false
description: "Sync coding-agent memory across machines over SSH using open-source tools: symlink CLAUDE.md/AGENTS.md, git-based auto-sync, or MCP markdown stores."
schema: "schema-open-source-memory-for-coding-agents-synced-over-ssh"
---

Open-source memory for coding agents synced over SSH lets you carry your AI assistant's context, preferences, and project knowledge across every machine you work on — without a cloud service. The most portable approach is a git-backed markdown store: symlink your agent's memory files, push and pull over SSH, and let auto-sync hooks handle the rest. This guide walks through the three proven methods and how to pick the right one.

## Why Coding-Agent Memory Drifts Across Machines

Modern coding agents each read their own memory file. Claude Code reads `.claude/CLAUDE.md`, while Cursor and Codex CLI read `AGENTS.md` in the project root. When you work on a laptop, a desktop, and a remote server over SSH, each machine holds a slightly different copy of that context — and the drift compounds.

The core problem is that copying instructions between `CLAUDE.md` and `AGENTS.md` causes drift: the same intent gets reworded differently, and you forget to update one file when you change the other. Over weeks, the memory on your remote box no longer matches your local setup, so the agent on each machine behaves differently. This is a real, recurring pain point for anyone running multiple agents or multiple machines.

The demand for a fix is enormous. The cross-agent memory tool claude-mem has passed 91,000 GitHub stars, and claude-reflect, which writes session feedback back into `CLAUDE.md` and `AGENTS.md`, has over 1,400 stars. Developers clearly want their agent memory to follow them.

## The Two Camps of Open-Source Agent Memory (File-Based vs Semantic)

Open-source memory tools fall into two broad camps, and the distinction matters a lot for SSH sync.

**File-based memory** stores everything as plain markdown plus git. Examples include memex (a Zettelkasten-style system) and claude-brain. Because the data is just text files in a git repo, it is trivially portable: you clone, pull, and push over SSH with zero special infrastructure. No vector database, no external service.

**Semantic or vector-based memory** compresses and indexes context using embeddings and knowledge graphs, typically exposed through an MCP server. These are more powerful for retrieval — one Claude Code setup using Obsidian and Graphify claims up to 71.5x fewer tokens per session — but they add moving parts that complicate remote sync.

For SSH-based synchronization, file-based memory is the clear winner. It is simpler, more robust, and works with any git remote you already have.

## Prerequisites — SSH Access and a Git Remote for Your Memory Store

Before you start, you need two things:

1. **SSH access** between the machines you want to sync. If you can `ssh user@host` from one box to another, you are ready. For a bare remote, a simple `git remote add origin user@host:/path/to/memory.git` works.
2. **A git remote** for the memory store. This can be a bare repo on your server, a private GitHub/GitLab repo, or even a local path. The key requirement is that every machine can reach it.

You also need the agent's memory directory initialized. For Claude Code that is `.claude/`, and for Cursor/Codex it is the project root's `AGENTS.md`. Decide which file is your canonical source of truth before you set up sync.

## Method 1 — Symlink CLAUDE.md and AGENTS.md (Zero-Dependency)

The simplest fix for multi-agent drift requires no new tool at all. Because Claude Code reads `.claude/CLAUDE.md` and Cursor/Codex read `AGENTS.md`, you can point both at the same file with a Unix symlink:

```bash
ln -s .claude/CLAUDE.md AGENTS.md
```

Now both tools read the same memory file, so there is only one source of truth to edit. This is the zero-dependency approach recommended by the coding-with-ai.dev guide on syncing Claude Code, Codex, and Cursor memory.

The trade-off is that a symlink only works on a single machine. To carry it across machines, you still need to sync the underlying file — which is where git comes in. But as a first step, symlinking eliminates the most common source of drift: two files that say the same thing in different words.

## Method 2 — Git-Based Memory Sync with Auto-Sync Hooks (claude-brain)

When you need memory to follow you across machines, git-based sync with auto-sync hooks is the most robust open-source option. claude-brain is built specifically for this: it syncs your Claude Code brain — memory, skills, agents, rules, and settings — across machines with intelligent semantic merge.

The workflow is straightforward:

1. Initialize a git repo in your memory directory (`.claude/` or the project root).
2. Add a remote reachable over SSH.
3. Install auto-sync hooks that commit and push on change, and pull on startup.

The standout feature is semantic merge. Instead of throwing raw git merge conflicts at you when two machines edit the same memory file, claude-brain merges the changes intelligently, so you rarely have to resolve conflicts by hand. That solves the "forgot to push" and "merge conflict" pain points that kill most naive sync setups.

## Method 3 — Markdown + Git Memory via MCP (memex)

If you want a memory layer that works across many different agents — Claude Code, Cursor, VS Code Copilot, Codex, Windsurf, and any MCP client — memex is a strong choice. It is Zettelkasten-based, stores everything as markdown plus git, and exposes itself through an MCP server.

Because there is no vector database, memex is naturally portable and SSH/git-sync friendly. You keep your memory in a git repo, and any agent that supports MCP can read and write to it. This makes it the most flexible option if you switch tools frequently or run several agents side by side.

The setup cost is slightly higher than a symlink because you run an MCP server, but the payoff is a single memory store that every agent on every machine can share.

## Syncing Over SSH — Push/Pull Workflow and Conflict Handling

Whichever method you choose, the sync mechanics over SSH follow the same pattern. On each machine, you pull the latest memory before you start working and push after you finish:

```bash
# On each machine, before starting work
git -C ~/.claude pull --rebase

# After a session, commit and push
git -C ~/.claude add -A
git -C ~/.claude commit -m "Update agent memory"
git -C ~/.claude push
```

Auto-sync hooks automate this so you never forget. The remaining risk is conflicts when two machines edit the same file. Tools like claude-brain handle this with semantic merge; if you are doing it manually, `git pull --rebase` plus a quick review of any conflict markers is usually enough for small memory files.

## Security Considerations for Remote Memory Sync

One of the strongest arguments for open-source, SSH-based memory is privacy. Local memory files synced over SSH avoid sending your context to third-party cloud memory services. Your prompts, code snippets, and project notes stay on machines you control.

That said, take basic precautions:

- Use SSH keys rather than passwords, and protect the private key.
- If your memory repo contains secrets, keep it private and never push to a public remote.
- Consider encrypting the memory directory if it holds sensitive project context.
- Remember that anything in your agent memory can be read by the agent — treat it like source code.

## Choosing the Right Approach for Your Setup

| Approach | Best for | Sync over SSH | Setup effort | Multi-agent |
|----------|----------|---------------|--------------|-------------|
| Symlink CLAUDE.md/AGENTS.md | Single machine, quick fix | Manual (git) | Minimal | Yes (2 tools) |
| claude-brain (git + semantic merge) | Cross-machine Claude Code | Auto via hooks | Medium | Claude Code focus |
| memex (markdown + git via MCP) | Many agents, portable store | Git-native | Medium-high | Yes (any MCP client) |

If you just need two tools on one machine to stop drifting, start with the symlink. If you live in Claude Code across a laptop and a server, claude-brain's auto-sync and semantic merge will save you the most time. If you run many different agents and want one portable memory store, memex is the most future-proof.

## FAQ

**What is agent memory sync over SSH?**
It is the practice of keeping a coding agent's memory files — like `CLAUDE.md` and `AGENTS.md` — synchronized across multiple machines using SSH and git, so every machine has the same context without a cloud service.

**How do I sync CLAUDE.md across machines?**
Put your memory directory in a git repo, add a remote reachable over SSH, and pull before work and push after. Tools like claude-brain automate this with auto-sync hooks and semantic merge.

**What is the difference between CLAUDE.md and AGENTS.md?**
Claude Code reads `.claude/CLAUDE.md`, while Cursor and Codex CLI read `AGENTS.md` in the project root. A symlink (`ln -s .claude/CLAUDE.md AGENTS.md`) makes both tools read the same file.

**Is open-source agent memory better than cloud memory services?**
For privacy, yes — local markdown synced over SSH keeps your context on machines you control and avoids sending it to third-party services. The trade-off is that you manage the sync yourself.

**Which open-source memory tool should I use?**
For a quick multi-agent fix, symlink your memory files. For cross-machine Claude Code, use claude-brain. For a portable store that works with any MCP client, use memex.
