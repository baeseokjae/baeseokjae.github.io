---
title: "Cross Repository Context for Coding Agents: WCTX via Local MCP"
date: 2026-08-30T19:02:48+00:00
tags:
  - MCP
  - coding agents
  - agent memory
  - cross-repo context
  - local-first
  - WCTX
description: "WCTX is a local-first MCP server that gives coding agents cross-repository context by importing finished sessions into SQLite + FTS5, with git-based freshness."
draft: false
cover:
  image: "/images/wctx-cross-repo-context-mcp.png"
  alt: "WCTX: Cross-Repository Context for Coding Agents via Local MCP"
  relative: false
schema: "schema-wctx-cross-repo-context-mcp"
---

Coding agents lose context across repositories because a session is scoped to one repo while the system under investigation spans many. WCTX is a local-first MCP server that solves this by importing finished coding-agent sessions into a SQLite + FTS5 store, linking repositories with typed relations, and exposing seven tools that let a fresh session search prior evidence with git-based freshness verdicts. No cloud account, no embeddings, no transcript upload.

## Why coding agents lose context across repositories

The core problem is a mismatch between the scope of a session and the scope of the system. When you run a coding agent inside repository A, its entire working memory — the files it read, the bugs it found, the decisions it made — lives in that session's context window. But the system you are actually building or debugging rarely lives in a single repository. A monorepo, a set of microservices, a frontend plus a backend, a library plus the applications that consume it: all of these are multi-repository systems.

Consider a concrete scenario. A session in repo A discovers that a bug in repo B is caused by a specific function in repo C. That is a valuable, hard-won finding. A week later, a fresh session starts in repo B to fix the bug. That session has no memory of the earlier investigation. It re-reads the same files, re-traces the same call path, and re-discovers what the first session already knew. The knowledge was never lost from the system — it was lost from the agent's context.

This is not a niche annoyance. As agentic coding becomes a daily workflow, the cost of re-deriving context grows linearly with the number of repositories and the number of sessions. The research brief for WCTX frames it precisely: "coding-agent sessions are scoped to a repository, but the system under investigation is not." The fix is not to make agents remember more inside a session; it is to persist what a session learned so that future sessions in related repositories can retrieve it.

## What is WCTX and how it works

WCTX is a local-first MCP server that turns completed coding-agent sessions into structured, evidence-backed engineering context. It is written in TypeScript, requires Node 22+ and git, and is MIT licensed. Its design centers on six core concepts:

- **Workspace** — a logical product that sits above individual repositories. A workspace groups the repositories that together form one system.
- **Repository** — a git repository that belongs to a workspace.
- **Relation** — a directional, typed edge between repositories, such as `uses`, `depends_on`, `calls`, or `imports`. Relations are declared, not inferred, which keeps ranking explainable.
- **Session** — a completed coding-agent session, imported from a transcript.
- **Evidence** — a discrete, attributable finding extracted from a session, carrying its session id, repository, and commit.
- **Freshness** — a git-based staleness verdict that tells an agent whether evidence is still trustworthy.

The storage layer is deliberately simple: SQLite for structured data, FTS5 for full-text search, and git for freshness checks. There are no embeddings, no vector database, and no cloud dependency. The whole thing runs on your machine.

WCTX exposes seven MCP tools, ordered for progressive disclosure so the surface stays affordable inside a context window:

1. `workspace_overview` — a cheap, high-level map of the workspace.
2. `search_session_evidence` — the primary retrieval tool.
3. `get_evidence` — fetch a specific piece of evidence.
4. `get_session_evidence` — all evidence from one session.
5. `get_related_repositories` — repositories connected to the current one.
6. `verify_finding_freshness` — check whether evidence is stale.
7. `finalize_session` — mark a session complete and index its evidence.

The contrast with tools that expose dozens of MCP functions is intentional. The brief notes that agentmemory ships 54 MCP tools; WCTX ships 7. Fewer tools means a smaller context footprint and a lower chance the agent wastes tokens enumerating capabilities.

## Installing and setting up WCTX

WCTX requires Node 22+ and git. Installation is a standard Node project:

```bash
git clone https://github.com/Haroon-jay/wctx.git
cd wctx
pnpm install
pnpm build
```

After building, initialize the workspace and run a health check:

```bash
wctx init
wctx doctor
```

`wctx init` creates the local data directory and the SQLite store. `wctx doctor` verifies that Node, git, and the store are all in a working state before you connect an agent. If you are importing transcripts from Claude Code, note that WCTX copies the raw transcript into its own data directory at import time — this matters because Claude Code's `cleanupPeriodDays` (default 30) deletes JSONL transcripts, so an import-only capture strategy silently loses old history. WCTX avoids that trap by owning a copy of the transcript.

## Connecting WCTX to your agent over MCP

Once the server is built and initialized, you register it with your agent over the Model Context Protocol. For Claude Code, the command is:

```bash
claude mcp add wctx -- wctx mcp
```

This registers the WCTX MCP server under the name `wctx`. The agent can then call the seven tools during a session. Because WCTX is a standard MCP server, the same registration pattern works with other MCP-capable agents, and you can point them at the server via a JSON MCP configuration file if your agent uses that style of config.

The key point is that WCTX is a local server on your machine. There is no remote endpoint, no API key to provision, and no transcript leaving your disk. The agent talks to it over the local MCP transport, and all retrieval happens against the local SQLite store.

## Recording what a session learned

The capture model is the heart of WCTX's philosophy: post-session processing beats in-session discipline. Agents under load skip `save_memory` calls — asking an agent to remember mid-task is unreliable. Instead, WCTX imports and audits the transcript after the session ends.

The command-line interface provides:

```bash
wctx capture --summary
wctx search
```

`wctx capture` ingests a finished session transcript and extracts evidence. It supports session adapters for Xirp, Claude Code, Codex, and generic JSONL, so it is not tied to a single agent vendor. The `--summary` flag produces a structured summary of what the session learned.

Within an MCP session, the `finalize_session` tool marks a session complete and indexes its evidence, making it available to future searches. The result is that a session's findings — root causes, decisions, and unresolved questions — become durable, searchable context rather than ephemeral context-window content.

## Searching prior sessions across related repositories

Retrieval is where the cross-repository design pays off. The `search_session_evidence` tool takes a query and returns evidence ranked by relevance, with each result carrying its session id, repository, and commit. The `get_related_repositories` tool tells the agent which repositories are connected to the current one, so a search can be scoped or expanded across the workspace topology.

The evaluation data shows why workspace topology matters. On a synthetic 15-query, 28-evidence-item corpus, the relevant prior session appeared in the top five for 15 of 15 queries and ranked first for 11 of 15. Adding workspace topology to plain FTS5 improved mean reciprocal rank (MRR) from 0.839 to 0.867, made repository attribution exact (0.93 to 1.00), and eliminated results from unrelated repositories (0.20 to 0.00 per query). In other words, the declared relations between repositories are not decoration — they measurably improve both ranking quality and precision.

## Verifying evidence freshness

Freshness is a first-class concept in WCTX, and it is what separates it from a naive transcript dump. Evidence is labelled with a git-based staleness verdict drawn from one of four states:

- **current** — the evidence still matches the repository state.
- **possibly_stale** — something changed that may affect the finding.
- **stale** — the finding no longer reflects the repository.
- **unknown** — freshness could not be determined.

The `verify_finding_freshness` tool returns this verdict, so an agent can decide whether to trust a piece of evidence or re-verify it. This matters because the whole point of cross-repository context is that a finding from a week ago may no longer be true after a refactor. A freshness verdict lets the agent treat old evidence as a lead to check rather than as ground truth.

## Making it proactive with CLAUDE.md / AGENTS.md guidance

WCTX can be made proactive by installing guidance into your agent's instruction files. The command:

```bash
wctx instructions --write
```

writes guidance into `CLAUDE.md` or `AGENTS.md` so that every future session in that repository knows to search before investigating and to record root causes, decisions, and unresolved questions. This turns a passive retrieval tool into an active workflow: the agent checks prior evidence before re-deriving it, and it leaves behind evidence for the next session. The brief calls this the difference between a memory that waits to be asked and a memory that shapes how the agent works.

## WCTX vs. alternatives

WCTX is not the only tool in this space, and the competitive landscape is worth understanding. The research brief compares it against five alternatives.

| Tool | Approach | Multi-repo topology | Local-first | Notes |
|------|----------|--------------------|-------------|-------|
| **WCTX** | Import finished sessions into SQLite + FTS5; declared typed relations | Yes, first-class | Yes | 7 MCP tools; git-based freshness |
| **engram** | Persistent agent memory; single Go binary, SQLite + FTS5 | Weak; single-project focus | Yes | ~5,991 stars; works with many agents |
| **agentmemory** | Broad automatic capture; 12 hooks, 54 MCP tools, embeddings | Global server | Localhost | ~26,961 stars; documents the cleanupPeriodDays trap |
| **context-router** | Multi-repo workspaces; observations + ADRs; auto-capture hooks | Yes | Yes | Edges inferred from code/contracts, not declared |
| **anchor** | Repo/org memory from GitHub PR history | Cross-repo impact | Needs GitHub auth | Records merged PRs, not the investigation |
| **Rewind** | Nightly "dreaming" daemon consolidates transcripts | Single-agent/store | Yes | Review-gated updates; closest in philosophy |

The main differentiators for WCTX are the declared, typed relations (which drive explainable ranking and human-readable reasons) and the explicit multi-repository topology. engram is strong but single-project focused; agentmemory is broad but ships a much larger MCP surface; context-router infers edges from code rather than declaring them; anchor indexes merged PRs but not the investigation that led to them; Rewind shares WCTX's post-session philosophy but is single-agent in scope.

## Evaluation results and honest limitations

The evaluation numbers are encouraging but should be read with appropriate skepticism. The corpus is synthetic — 15 queries and 28 evidence items — so it is a controlled test of the retrieval mechanism, not a measure of real-world value across a production codebase. The headline results:

- Relevant prior session in the top five for 15 of 15 queries; ranked first for 11 of 15.
- Workspace topology improved MRR from 0.839 to 0.867 and made repository attribution exact (0.93 to 1.00).
- Median local retrieval latency is 1.57 ms with a median response payload of ~5.0 KB (~1,250 tokens for five results).
- Source attribution was complete for 100% of returned results under all three configurations.

The latency and payload figures are the most practically relevant: sub-2 ms retrieval and a ~1,250-token response for five results mean the tool is cheap enough to call without worrying about context-window bloat. The honest limitation is that the evaluation is synthetic and small; real-world value depends on how well the declared relations match your actual repository topology and how consistently your agents record evidence.

## Security and privacy considerations

Because WCTX is local-first, the privacy story is strong: no cloud account, no embeddings, no transcript upload. Your transcripts and evidence never leave your machine. The design also takes security seriously in several specific ways:

- **Redaction of secrets** — evidence is scrubbed of secrets before storage.
- **Historical untrusted data** — evidence is labelled as historical, untrusted data, so the agent treats it as a lead rather than as authoritative instructions.
- **Argument-array git calls** — git is invoked with argument arrays rather than shell interpolation, avoiding injection through repository names or paths.
- **Constructed FTS5 queries** — full-text queries are built safely to prevent query injection.

These are the details that matter when you are feeding agent-derived content back into an agent's context. The threat model is not a malicious remote attacker; it is the risk that stale or untrusted evidence gets treated as ground truth, or that a crafted repository name breaks a shell command.

## When to use WCTX and when not to

WCTX is a good fit when you work across multiple repositories that form one logical system, when you want local-first privacy, and when you want explainable, freshness-checked evidence rather than a black-box vector store. It is especially valuable in the post-session model: you do not need to trust agents to remember mid-task, because you import and audit the transcript afterward.

It is probably overkill if you work in a single repository with a short-lived set of sessions, or if you need a global memory server shared across many agents and are willing to accept a larger MCP surface. If your primary need is broad automatic capture with embeddings and session replay, agentmemory may fit better. If you want a minimal single-binary memory with no multi-repo emphasis, engram is worth a look.

The deciding question is whether your system spans repositories. If it does, and if you are tired of fresh sessions re-discovering what old sessions already knew, WCTX is a focused, local-first answer.

## FAQ

**What is cross repository context for coding agents?**
Cross repository context means giving a coding agent access to knowledge that was discovered in sessions run against other repositories in the same system. WCTX stores that knowledge locally and retrieves it over MCP, so a fresh session in one repo can use findings from sessions in related repos.

**Does WCTX require a cloud account or embeddings?**
No. WCTX is local-first: it uses SQLite + FTS5 for storage and search, and git for freshness checks. There is no cloud account, no embeddings, and no transcript upload.

**Which coding agents does WCTX work with?**
WCTX imports session transcripts from Xirp, Claude Code, Codex, and generic JSONL, and exposes a standard MCP server that any MCP-capable agent can connect to. For Claude Code, you register it with `claude mcp add wctx -- wctx mcp`.

**How does WCTX know when evidence is stale?**
WCTX labels every piece of evidence with a git-based freshness verdict: current, possibly_stale, stale, or unknown. The `verify_finding_freshness` tool returns this verdict so an agent can decide whether to trust a finding or re-verify it.

**Is WCTX better than agentmemory or engram?**
It depends on your needs. WCTX emphasizes declared multi-repository topology, explainable ranking, and a small 7-tool MCP surface. agentmemory offers broader automatic capture with 54 tools and embeddings, while engram is a minimal single-project memory. Choose based on whether your system spans repositories and how much MCP surface you can afford.
