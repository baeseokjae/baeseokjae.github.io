---
title: "Simmis Review: A Self-Hosted Shared Memory Workspace for People and AI Agents"
date: 2026-08-23T13:01:39+00:00
tags:
  - AI Agents
  - Self-Hosted
  - Memory
  - Local-First
  - Clojure
  - Datalog
description: "Simmis is a self-hosted workspace where people and AI agents share one versioned, queryable memory — chat, wiki, ledger, and repo on a single substrate."
draft: false
cover:
  image: "/images/simmis-shared-memory-workspace.png"
  alt: "Simmis: Self-Hosted Shared Memory Workspace for People and AI Agents"
  relative: false
schema: "schema-simmis-shared-memory-workspace"
---

Simmis is a self-hosted workspace where people and AI agents share a single, versioned, queryable memory — chat rooms, wiki pages, knowledge bases, a double-entry ledger, and a code repository all live on one substrate instead of being scattered across siloed tools. Built in Clojure on the replikativ stack, it treats humans and agents as the same kind of participant, so @mentions, governance, and history work identically across both. It is an early, MIT-licensed "release early" project that is used daily but still has rough edges.

## What is Simmis? A self-hosted shared-memory workspace for people and AI agents

Simmis is a reference application for the replikativ stack, a set of Clojure libraries for building distributed, versioned, local-first systems. The project's own description is precise: it is a self-hosted workspace where people and AI agents share one memory. That memory is not a single chat log or a single database table — it is a durable, versioned substrate that holds chat rooms, wiki pages, knowledge bases, an accounting book, and a code repository, all queryable as one coherent store.

The project was created on 2026-08-20 and is explicitly an early "release early" first public cut. At research time it had roughly 5 stars and 2 forks on GitHub, which tells you this is not a mature, widely adopted product. It is a serious, opinionated prototype that its author uses daily, with a clear architectural vision and an unusually honest list of known gaps.

## The core idea — one versioned, queryable substrate instead of siloed tools

Most teams today run their collaboration across a patchwork of tools: Slack or Discord for chat, Notion or Confluence for wiki, a spreadsheet or accounting package for money, and Git for code. Each tool has its own data model, its own history, and its own access controls. When you add AI agents to the mix, the fragmentation gets worse — each agent needs its own memory layer, its own context, and its own way of writing back.

Simmis collapses this into a single substrate. Chat, wiki, knowledge bases, the ledger, and the repository all live in the same versioned store. Because everything is on one substrate, a query can cross boundaries that would be impossible in a siloed setup: you can ask "what did we decide about pricing, and what did the agent write into the ledger to reflect it?" and get a single, coherent, time-traveling answer.

This is the fundamental differentiator. Memory-layer tools like mem0, Letta, Cognee, and Zep give agents a memory store, but they do not give you a shared workspace where humans and agents collaborate on the same artifacts with the same governance. Simmis is not a memory layer bolted onto your existing tools — it is a workspace built around shared memory as the organizing principle.

## Key features: Rooms, Knowledge bases, Proposals, Time travel, The book, Agents, Intake

### Rooms — conversation with durable memory

Rooms are Simmis's chat primitive, but they are more than chat. A room is a conversation with durable memory, and humans and agents are the same kind of participant — a "party." That means @mention works across both humans and agents, and a room can mirror to Telegram so you can interact with your workspace from a messaging app you already use.

### Knowledge bases — a real Datalog database

Each knowledge base is its own Datahike database holding wiki pages, blocks, links, and typed entities. The key insight is that `[[Title]]` links are stored as datoms, so backlinks and neighborhood queries are ordinary database queries rather than string matching. This is a genuinely different architecture from a typical wiki, where links are just text.

### Proposals — governed agent writes

Every governed agent write lands on a fork (a yggdrasil branch), shows a semantic diff, and merges only with `:merge` authority. This is the trust mechanism that lets you be generous with what agents may write: an agent can propose anything, but nothing takes effect until a human (or authorized party) reviews and merges it.

### Time travel — history-preserving memory

Stores keep their history, and any knowledge base can be read as-of a point in time. This means agents and humans can audit exactly how a page or a ledger entry got to where it is. If an agent proposes a change that turns out to be wrong, you can see precisely what changed and when.

### The book — a governed double-entry ledger

The book is a governed double-entry ledger built on kontor. Unbalanced entries are rejected in the writer, so an agent cannot corrupt the ledger by posting a one-sided transaction. This is a strong example of domain-level integrity enforced at the write boundary.

### Agents — sandboxed with a curated vocabulary

Agents run in an SCI sandbox with a curated vocabulary: `wiki/`, `kb/`, `kontor/`, `proposal/`, `workflow/`, the muschel shell, and `datahike.api`. They can schedule recurring workflows. The sandbox is a soft boundary, not a VM — a point the project itself is honest about.

### Intake — everything lands in the same substrate

A web-clipper browser extension, mail accounts, screen capture, and voice notes all land in the same substrate. This means your external inputs become part of the same versioned, queryable memory as your internal collaboration.

## How governance works — fork-and-review proposals and the :merge authority

The governance model is the heart of what makes Simmis safe to give agents write access. When an agent wants to write, it does not write directly to the shared state. Instead, the write lands on a fork — a yggdrasil branch — and is presented as a semantic diff. A party with `:merge` authority reviews the diff and decides whether to merge it.

This is a fork-and-review model borrowed from how code review works in Git, applied to every kind of write an agent can make. The practical effect is that you can be generous with what agents may attempt, because nothing is destructive by default. An agent can propose a wiki edit, a ledger entry, or a knowledge-base change, and a human reviews it before it becomes part of the shared memory.

The ledger adds a second layer of integrity: unbalanced double-entry transactions are rejected in the writer itself, so even a buggy or malicious agent cannot post a transaction that breaks the accounting invariant. This is domain-level enforcement on top of the process-level governance.

## The architecture — local-first Datahike replica, server as authorization boundary

Simmis's architecture is deliberately local-first. The client runs a real Datahike replica in the browser, backed by IndexedDB, and keeps it in sync with the server via konserve-sync. Queries run locally against your replica, and the server is the authorization boundary — not a query API.

This has two important consequences. First, it is privacy-friendly and offline-friendly: your data lives in your browser, and reads do not require a round-trip to a server. Second, it changes the security model: the server does not need to be a general-purpose query endpoint, because the client already has the data it needs locally. The server's job is to authorize writes and keep replicas in sync, not to serve arbitrary queries.

The trade-off is that this is a more complex architecture than a simple client-server app, and it is single-node only at this stage. There is no clustering, no multi-node replication across servers, and no migration tooling yet.

## The replikativ stack under the hood

Simmis is the reference application for the replikativ stack, and understanding the stack helps you understand the architecture. The main components are:

- **Datahike** — a durable Datalog database that provides the queryable, versioned store. Datahike itself drew 146 points on Hacker News, indicating real interest in the underlying technology.
- **konserve** — the storage abstraction layer, with konserve-sync handling browser/server sync.
- **yggdrasil** — the CRDT-based replication and branching layer that powers forks and merges.
- **kabel** — the messaging/transport layer.
- **kontor** — the governed double-entry ledger.
- **spindel** and **dvergr** — additional components for the distributed system.

This is a coherent, opinionated alternative to mainstream agent stacks. Where most agent frameworks are built around Python, REST APIs, and vector databases, Simmis is built around Clojure, Datalog, and CRDTs. That is a real philosophical difference, not just a language preference: Datalog gives you declarative, time-traveling queries, and CRDTs give you conflict-free replication.

## Getting started — prerequisites, quick start, LLM providers

Getting Simmis running requires a JDK 21+ and Node 18+. The quick start is:

```bash
npm install
clj -M:dev
```

The UI runs at `localhost:8080` and the WebSocket endpoint at port 47295. LLM providers are configured via environment keys for Fireworks, OpenAI, Anthropic, and Groq, with a fallback model of `accounts/fireworks/models/glm-5p2`. Model settings can be configured per room.

For production use, you must set `SIMMIS_JWT_SECRET`. The project is clear that this is not a set-and-forget install — it is a developer-oriented tool for people comfortable with the Clojure toolchain.

## Known gaps and honest limitations

Simmis's documentation includes a refreshingly honest list of known gaps, which is a strong trust signal for an early-stage tool — but also a caution for production use:

- **No integration-level auth test** — the auth path is not yet covered by integration tests.
- **Blob reads are authenticated but not authorized** — a security gap that matters if you store sensitive blobs.
- **The agent sandbox is a soft boundary, not a VM** — a determined or buggy agent could potentially escape the SCI sandbox.
- **No migration tooling** — upgrading the data model is not yet automated.
- **`SIMMIS_JWT_SECRET` must be set in production** — easy to miss.
- **Room apps are private** — no public/shared room apps yet.
- **Single-node only** — no clustering or multi-node replication.

For a project this early, these gaps are expected. But they mean Simmis is not yet a drop-in for a production team that needs hardened security and operational tooling.

## How Simmis compares to mem0, Letta, Cognee, and Zep

The agent-memory space is crowded, and it is worth positioning Simmis against the incumbents. The table below summarizes the key differences.

| Tool | Stars (approx.) | Core model | Differentiator vs Simmis |
|------|-----------------|------------|--------------------------|
| mem0 | ~63.8k | Memory layer / API | Drop-in memory extraction and retrieval; not a full workspace |
| Cognee | ~30.1k | Knowledge-graph memory | Graph-centric memory engine; Simmis uses Datalog with time travel |
| Letta | ~24.3k | Stateful agents with self-improving memory | Agent memory and self-improvement; Simmis adds shared human+agent workspace |
| Zep | ~4.8k | Long-term memory for agents | Memory layer; Simmis adds governance and a real ledger |
| Simmis | ~5 | Full self-hosted workspace | Shared human+agent memory, fork-and-review governance, double-entry ledger |

The pattern is clear: the incumbents are memory layers or agent platforms, while Simmis is a full self-hosted workspace. If you already have a stack and just need agent memory, mem0 or Letta may be the pragmatic choice. If you want a single substrate where humans and agents collaborate on the same artifacts with real governance, Simmis is the differentiator.

## Who should use it today — and who should wait

Simmis is best suited today for developers and small teams who:

- Are comfortable with Clojure and the JVM toolchain.
- Value local-first, privacy-friendly architecture.
- Want to experiment with fork-and-review governance for agent writes.
- Need a coherent, versioned, queryable store rather than another memory API.
- Are willing to accept early-stage rough edges and a soft sandbox.

You should wait if you need hardened production security, multi-node scaling, migration tooling, or a large ecosystem of integrations. The single-node limitation, the blob authorization gap, and the soft sandbox are real blockers for production use at this stage.

## Verdict and caveats

Simmis is one of the most architecturally interesting entries in the agent-collaboration space. The core idea — one versioned, queryable substrate where people and agents share memory, with fork-and-review governance and a real double-entry ledger — is genuinely novel and well-executed for an early project. The local-first architecture and the Datalog/CRDT foundation are thoughtful choices that set it apart from the memory-layer incumbents.

There are two caveats worth calling out. First, the project is very early: ~5 stars, no migration tooling, a soft sandbox, and a blob authorization gap. Treat it as a promising prototype, not a production system. Second, there is a discoverability red flag: `replikativ.io` now resolves to a parked/spam site (a casino page) rather than the project's official site. The official web presence appears gone or compromised, which is a credibility concern for a project you might want to depend on. Verify the GitHub repository directly and be cautious about any links that route through the project's former domain.

Overall, Simmis is a compelling vision with a strong architectural foundation. If you are building a self-hosted, local-first workspace where humans and AI agents genuinely collaborate, it is worth a close look — with your eyes open about its early stage.

## FAQ

### What is Simmis?

Simmis is a self-hosted workspace where people and AI agents share a single, versioned, queryable memory. Chat rooms, wiki pages, knowledge bases, a double-entry ledger, and a code repository all live on one substrate, built in Clojure on the replikativ stack.

### How is Simmis different from mem0 or Letta?

mem0, Letta, Cognee, and Zep are memory layers or agent platforms that give agents a memory store. Simmis is a full self-hosted workspace where humans and agents collaborate on the same artifacts, with fork-and-review governance and a real double-entry ledger.

### Is Simmis safe to give AI agents write access?

Simmis uses a fork-and-review governance model: every governed agent write lands on a fork, shows a semantic diff, and merges only with `:merge` authority. The ledger also rejects unbalanced entries in the writer. However, the agent sandbox is a soft boundary, not a VM, so treat it as a trust mechanism, not a hard security boundary.

### What are Simmis's main limitations?

Known gaps include no integration-level auth test, blob reads that are authenticated but not authorized, a soft (non-VM) agent sandbox, no migration tooling, single-node-only operation, and the need to set `SIMMIS_JWT_SECRET` in production.

### Is Simmis ready for production use?

Not yet for most teams. It is an early "release early" project with ~5 stars, no migration tooling, a soft sandbox, and a blob authorization gap. It is best suited to developers comfortable with Clojure who want to experiment with a local-first, governed shared-memory workspace.
