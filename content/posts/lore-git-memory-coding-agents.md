---
title: "Lore Git Memory Coding Agent: Searchable Session Archive for Claude Code and Codex"
date: "2026-09-13T10:01:40+00:00"
tags: ["ai coding", "claude code", "codex", "agent memory", "git"]
description: "Lore is a local, read-only desktop app that turns Claude Code and Codex session history into a searchable, git-connected archive — no cloud, no LLM calls, no vendor lock."
draft: false
cover:
    image: "/images/lore-git-memory-coding-agents.png"
    alt: "Lore Git Memory Coding Agent: Searchable Session Archive for Claude Code and Codex"
    relative: false
schema: "schema-lore-git-memory-coding-agents"
---

Coding agents like Claude Code and Codex remember nothing once a session ends, which is why you keep re-asking the same questions and re-discovering the same fixes. Lore is a local-first desktop app that reads the session files these agents already save, connects them to your repositories and Git history, and puts everything into a single searchable SQLite archive — with no accounts, no telemetry, no cloud database, and no LLM calls. Because it only reads what Claude Code and Codex already write on disk, Lore adds searchable long-term memory to your coding agents without changing how they behave or locking you into another vendor.

## What is Lore and why does git-based agent memory matter?

Lore (github.com/hsusul/lore) is a desktop application built with Tauri 2 and a Rust core on a React UI. Its entire job is to make your coding-agent history discoverable: if a Claude Code or Codex session left a trace on your machine, Lore indexes it, links it to the relevant repository and to the Git history around the moment it happened, and lets you search it months later.

Git-based agent memory matters because software development history is inherently about *change over time*. A coding agent does not produce one fixed document; it produces a sequence of edits, commits, and decisions. Storing that as plaintext tracked by Git preserves the temporal dimension — you can see what the agent decided, when, and what the repo actually looked like at that moment. That contrasts with vector-database "memory" tools, which summarize and flatten history into embeddings and lose the exact, auditable record.

The pattern is not niche. A wave of 2025–2026 Show HN projects attacks agent memory with Git and plaintext instead of vector databases — DiffMem ("I replaced vector databases with Git"), Darc, FAVA Trails, LedgerMind, and Fur ("Git-like CLI for branching chats"). Lore sits inside that movement with a polished desktop UX aimed at developers who want their agent history browsable like a code archive.

## How does Lore work — read-only adapters, SQLite archive, and Git evidence?

Architecturally, Lore is deliberately non-invasive. It does not wrap Claude Code or Codex, does not alter their files, and is read-only against your agent data. It runs three main jobs:

1. **Ingestion.** Lore reads the session files that Claude Code and Codex already save locally (JSON logs and transcript files in their respective history directories).
2. **Linking.** It connects each session to the repository it was working on and to the Git history — commits, diffs, and branch states — that surrounded the session.
3. **Storage and search.** It stores the evidence in a local SQLite index, queried through a search interface so you can retrieve past decisions, bug fixes, and context on demand.

The Rust core is split into crates: `lore-core` (ingestion, storage, Git, search, and safety), `lore-ipc` (IPC types with TypeScript bindings), `src-tauri` (the Tauri layer), and `src` (the React UI).

### Why does Lore separate commits from repo state?

Lore keeps different evidence kinds separate — a commit that was recorded *during* a session is treated as a distinct evidence type from the repository state that was *observed* during ingestion. This prevents source confusion: if your repo changed after the session ended, Lore does not retroactively attribute later commits to that session. Keeping current-state surface (files) separate from depth (Git history) is the same trick DiffMem uses to keep context windows lean, and it makes the archive auditable.

## Installing Lore on macOS

Lore requires you to build from source because it pins a specific Rust toolchain in `rust-toolchain.toml`. The prerequisites are a Rust toolchain, the Tauri 2 system dependencies, and Node for the React frontend.

| Requirement | What you need |
|-------------|---------------|
| Rust toolchain | Installed via `rustup`, pinned by `rust-toolchain.toml` |
| Tauri 2 prerequisites | macOS system libraries and Xcode command-line tools |
| Node.js | For the React UI and npm install/build |
| Claude Code and/or Codex | Their session files must exist locally to ingest |

A typical build, after cloning the repository, is:

```bash
# Install the pinned Rust toolchain
rustup toolchain install stable   # or the version locked in rust-toolchain.toml
rustup override set stable

# Build and run the Tauri desktop app
cd lore
npm install
npm run tauri dev       # development
npm run tauri build     # production bundle
```

Because the toolchain is pinned, use the exact version in `rust-toolchain.toml` rather than the latest stable if a mismatch appears. On first launch, Lore will prompt you to point it at your Claude Code and Codex history directories, then begin ingestion.

## How do you connect Claude Code and Codex session logs?

Lore reads history that Claude Code and Codex already persist on disk. You connect these in the app's settings:

- **Claude Code** stores session history in your home directory under `.claude` (project-scoped files and global transcript logs).
- **Codex** similarly keeps a local history of sessions, which Lore's adapter reads.

The important property is read-only: Lore does not install wrappers, intercept commands, or modify agent behavior. It takes what the agents already wrote and indexes it. That means there is no vendor lock-in — if you stop using Lore, your agent history is untouched, and if you stop using one agent, Lore still reads the other. It is also why onboarding is just a path selection rather than an invasive setup.

## Searching and browsing your session archive

Once indexed, Lore gives you a searchable archive across all your sessions. You can:

- Query sessions by keyword, file path, commit message, or repository.
- Filter by agent (Claude Code vs. Codex) and by time range.
- Recover past decisions and bug fixes with exact evidence, rather than relying on a vague memory of "we fixed that somewhere."
- Browse a session in the context of the Git history around it, so you can see the code state that produced a decision.

Because search is over the raw local evidence rather than an embedding summary, recall is exact (lexical/substring), not fuzzy semantic similarity. For a developer debugging a re-occurring issue, that precision is the point: you want the exact past commit, not "something kind of like it."

## How does Lore compare with alternatives?

| Tool | Storage | Retrieval | Integration | Positioning |
|------|---------|-----------|-------------|-------------|
| **Lore** | SQLite archive of Claude Code/Codex sessions | Local search UI, Git-linked | Read-only desktop app (Tauri/Rust) | Polished desktop UX |
| **DiffMem** | Git-tracked Markdown files | Sandboxed grep/git log/blame via LLM agent | FastAPI self-hosted service | Lean, current-state vs. depth |
| **Darc** | SQLite index of prior sessions | Read API, on-demand context | Grep-like CLI, git-backed sharing | Team index sharing |
| **FAVA Trails** | Git repo, Markdown with YAML frontmatter | Lexical recall via MCP tools | MCP-based | Curated lifecycle, draft isolation |
| **LedgerMind** | Local HTTP services, persistent memory | Memory for next action | Local-first | Benchmarked against Mem0 OSS |

DiffMem (902 stars) powers Annabelle across thousands of WhatsApp/Messenger conversations and is self-hostable on a 1 vCPU box, making it a strong fit for conversational agents. Darc is the grep-like CLI with team index sharing via GitHub. FAVA Trails emphasizes a curated lifecycle — every thought and decision is a Markdown file you control, with a draft-to-promoted gate. LedgerMind positions itself as memory for the next action rather than a transcript archive.

Lore differentiates through **read-only, non-invasive indexing of agents you already use** and a desktop-first search experience. It is the lightest-touch option for Claude Code and Codex users who want an archive without adopting a whole memory framework.

## What does Lore deliberately not do — privacy and scope?

Lore's scope is explicitly limited, and that is a feature:

- **No accounts or telemetry.** Everything runs locally; there is no cloud database and no usage reporting.
- **No LLM calls.** Lore does not send your sessions to a model for summarization, so it adds no model cost and no data-exfiltration risk.
- **No agent wrapping.** It does not intercept, modify, or reroute Claude Code or Codex.
- **No cloud memory.** The archive is not an IDE, an agent runtime, or a cloud memory service.

It is Apache 2.0 licensed. For teams or individuals handling proprietary code, this local-first posture means sensitive session history never leaves the machine — a direct counterpoint to cloud agent-memory services that summarize your transcripts on third-party infrastructure.

## Building and extending Lore from source

If the stock behavior does not fit, Lore's crate layout makes extension approachable:

- **`crates/lore-core`** — the ingestion, storage, Git, search, and safety logic. Most new capabilities (a new agent adapter, richer Git linkage, improved search) live here.
- **`crates/lore-ipc`** — IPC types and TypeScript bindings; the contract between the Rust core and the React UI.
- **`src-tauri`** — the Tauri desktop layer.
- **`src`** — the React frontend.

A contributor adding, say, a new code-agent adapter would implement it in `lore-core` following the pattern of the existing Claude Code and Codex adapters, expose any new search/filter capability through `lore-ipc`, and surface it in the React UI.

## What are Lore's limitations and roadmap?

The most significant limitation is a deliberate one: Lore supports **only Claude Code and Codex**. Because adapters must parse each agent's on-disk session format, supporting more agents (e.g., other coding agents or generic transcripts) means writing new adapters in `lore-core`. A second limitation is setup friction: it is a from-source build requiring a Rust toolchain and Tauri dependencies, not a one-click installer for most users. Finally, because search is lexical rather than semantic, it is exact but does not help with "I remember the concept but not the words" queries — though that exactness is preferable for auditing.

Scope also means the maintainers have deferred building it into an IDE, adding an agent runtime, or turning it into cloud memory. The roadmap is oriented around a sharper, deeper local archive for the two dominant coding agents.

## FAQ

**Is Lore free and open source?**
Yes. Lore is licensed under Apache 2.0 and available on GitHub (github.com/hsusul/lore).

**Does Lore send my session data anywhere?**
No. It is local-first with no accounts, no telemetry, no cloud database, and no LLM calls — all indexing and search happens on your machine.

**Does Lore change how Claude Code or Codex work?**
No. Its adapters are read-only; it reads the session files the agents already save locally without wrapping or modifying them.

**Which coding agents does Lore support?**
Currently Claude Code and Codex, whose on-disk session formats Lore parses. Support for more agents requires writing new adapters in the lore-core crate.

**How do I install Lore?**
You build it from source: install a Rust toolchain (pinned via rust-toolchain.toml) and Node, then run `npm install` and `npm run tauri dev` (or `npm run tauri build` for a production bundle).
