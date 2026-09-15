---
title: "Deja Vu Coding Agent Memory: Index Your Session History for Instant Recall"
date: 2026-09-15T16:09:01+00:00
tags: ["coding agent memory", "deja vu memory", "AI coding agent session history", "persistent memory for coding agents", "Claude Code memory", "Codex memory", "MCP memory recall", "LongMemEval benchmark", "LoCoMo benchmark", "LLM context compaction memory"]
description: "Deja Vu indexes the session history your coding agents already wrote to disk and makes it searchable in under a millisecond, with no LLM, no embeddings, and no API key."
draft: false
cover:
    image: "/images/deja-vu-memory-coding-agents-indexes-sessions.png"
    alt: "Deja Vu: Memory for Coding Agents That Indexes Sessions"
    relative: false
schema: "schema-deja-vu-memory-coding-agents-indexes-sessions"
---

Deja Vu is a memory layer for coding agents that indexes the session history your AI agents already wrote to disk, then makes it searchable by the agent itself through an MCP recall server. It starts full, not empty: instead of recording facts forward like most memory tools, it builds a searchable index over months of existing Claude Code, Codex, Cursor, and opencode transcripts, then answers recall queries in under a millisecond with a single zero-dependency local Go binary — no LLM, no embeddings, and no API key required.

## What Deja Vu Does: One Memory Layer for Every Coding Agent

Deja Vu (the open-source project at `vshulcz/deja-vu`, distinct from the unrelated `focaxisdev/deja-vu` repo-local Markdown tool) is a compact local Go binary that turns a coding agent's session history into a retrievable memory. It works with 20+ coding agents that record their conversations to local files — including Claude Code, Codex, Cursor, opencode, Copilot CLI, and Hermes.

The architecture is deliberately minimal. A `deja` daemon watches the directories where your agents write session transcripts, indexes them into a small on-disk structure, and exposes an MCP server that any agent can call to search that history. Because it reads plain session logs rather than requiring agents to log structured events, it picks up months of history from before you ever installed it.

## Why Agent Memory Is the Missing Piece (and the Context-Dump Fallacy)

Coding agents are stateless across sessions. Every new conversation starts from scratch unless you manually paste context, maintain an `AGENTS.md` file, or dump a session transcript into the prompt. That context-dump approach fails in predictable ways.

Full-context injection has severe accuracy limits. On the LongMemEval benchmark, injecting the entire conversation history scores 46.20%, while a no-memory baseline falls to just 22.8%. The fundamental problem is token budget and position: a long transcript far exceeds what fits in a context window, and even when a truncated slice fits, the agent must re-read and re-reason over tens of thousands of tokens to find the single decision it needs. Naive RAG over transcripts often does worse on temporal and multi-hop tasks than a simple baseline.

Memory is the missing architectural component. Agent memory reports from 2026 now treat persistent recall as a first-class component rather than context dumping, with standardized benchmarks (LongMemEval, LoCoMo, and BEAM) measuring how well memory systems retrieve the right information at the right time.

## How deja Indexes Sessions Instead of Recording Forward

The core differentiator is direction. Most memory tools — agentmemory, Mem0, the AGENTS.md pattern — start empty and record forward, meaning they only know what they learned after they were installed and only if the agent explicitly saved it. Deja Vu starts full by indexing the session transcripts your agents have already been writing to disk, including months of history that predate the install.

The indexing flow works like this:

1. **Discover** the session-log directories your agents write to (Claude Code JSONL transcripts, Codex, Cursor, and others).
2. **Build** an index over that history on first install — this can take a few minutes for several gigabytes of transcripts.
3. **Query** via an MCP recall server, which the agent invokes the way it would call any other tool.

Because index lookups return the relevant transcript slices rather than raw dumps, the agent receives only what it asked for. Deja Vu reports a median lookup time of roughly 1.5 milliseconds over 3.5 GB of history at v0.17, with the project citing sub-millisecond searches across about 5 GB of accumulated sessions.

## Key Features: Cross-Agent Recall, Compaction Survival, Secret Redaction

### Cross-agent recall

Because all supported agents write transcripts to the same shared memory layer, a decision made in one tool is recallable in another. Solve a problem in Codex or Cursor, then recall it in a fresh Claude Code session — the indexed history is the same. This solves the practical problem where switching tools for a task loses the context you built in your usual one.

### Survives context compaction

Long sessions eventually hit context limits and are compacted into summaries. Those summaries are lossy. In measurements across 43 compactions, the surviving summary retained 77% of the decisions but only 0.2% of the commands — meaning 99.8% of the concrete, actionable command history was lost. Deja Vu hands that 99.8% back by indexing the pre-compaction transcripts, so the original details remain queryable even after the session rolls up.

### Secret redaction at index time

The indexer redacts secrets as it builds the index — API keys, tokens, JWTs, and private key blocks — so your credentials do not end up retrievable from memory. This matters because session transcripts routinely contain secrets from shell commands and tool calls.

### No LLM and no embeddings

The binary performs pure lexical and structural indexing. There is no model inference at index or query time, no embedding vectors, and no API key. It runs entirely offline on your machine, which is a privacy and cost advantage over embedding- and vector-based memory platforms.

## Benchmarks: LongMemEval-S and LoCoMo, Compared Honestly

Deja Vu publishes reproducible numbers on the two field-standard memory benchmarks:

- **LongMemEval-S**: 85.3% hit@1
- **LoCoMo**: 69.6%

LongMemEval is a 500-question test across six categories — single-session user recall, assistant recall, preference recall, knowledge update, temporal reasoning, and multi-session integration. LoCoMo is a 1,540-question benchmark built from multi-session dialogues. Both are public datasets, and deja ships the harnesses so you can re-run the evaluation in minutes.

| System | LongMemEval | LoCoMo |
|--------|-------------|--------|
| Deja Vu | 85.3% (S) | 69.6% |
| CortexDB v1 | 93.8% (S) | 86.9% (cat. 1–4) |
| Mem0 (2026 token-efficient) | 94.4 | 92.5 |
| Mem0 (reported vs CortexDB) | 93.4% | — |
| LangMem | — | 75.6% |
| MemGPT | — | 69.3% |
| GPT-4o long context | 56.7% | — |
| No memory baseline | 22.8% | — |

These numbers should be read carefully. Deja Vu does not top every chart, but it reaches a strong 85.3% on LongMemEval-S and 69.6% on LoCoMo while using no model inference and no embeddings — meaning its cost is effectively zero and its privacy posture is strictly local. Higher-scoring systems like Mem0 (94.4 on LongMemEval) reach those figures at a substantial token cost of roughly 6,900 tokens per query. If raw accuracy over a large corpus is the only goal, an embedding-based platform wins. If you want offline, free, sub-millisecond recall over your existing agent history, deja is the tool designed for exactly that.

## How It Compares to Memory Platforms (Mem0, agentmemory, CortexDB)

Understanding where deja fits requires separating two families of memory tools.

**Session indexers** (deja) read what already happened. They require no setup of save hooks, no prompt changes, and no per-fact writing discipline. Their strength and limitation are the same: they can recall anything an agent did, but they cannot reason about facts that were never recorded in a session log.

**Recording-forward tools** build memory by the agent explicitly saving facts. `agentmemory` extends Karpathy's LLM Wiki pattern with confidence scoring, lifecycle management, knowledge graphs, and hybrid search, writing roughly 1,900 tokens of facts per session (~$10 a year). Mem0 applies an LLM to write and consolidate facts forward, achieving top benchmark scores at a token cost per query. CortexDB runs a vector engine and reports 93.8% on LongMemEval-S. `focaxisdev/deja-vu` is a third, unrelated design: a repo-local Markdown memory system built from `AGENTS.md`, `memory/summary.md`, and `memory/impressions.jsonl`, with no database and no daemon.

There is a hybrid play: deja's session indexing can complement a recording-forward tool. Let deja recall the exact command history and decisions, and let a fact-focused memory hold durable preferences and constraints. On deja's own compaction measurement, the summary retains decisions (77%) but loses commands (0.2%) — exactly the two halves of memory that the two tool types handle well.

## Installation and Setup Guide: From Zero to Auto-Recall in Minutes

Deja Vu installs in about 10 seconds. This is the complete walkthrough.

**Step 1: Install the binary.** The project provides a single-command installer, or you can download a prebuilt binary for your platform. There is no Go toolchain or system dependency required at runtime.

```bash
curl -sSf https://sh.vshulcz.dev/deja | sh
```

**Step 2: Initialize and configure the daemon.** Point `deja` at the directories where your agents store their transcripts.

```bash
deja init
deja install # registers the session-start hook
```

**Step 3: Index your existing history.** The first-run build reads all accumulated session logs. For several gigabytes of transcripts this takes a few minutes; after that the daemon increments as new sessions close.

```bash
deja index --all
```

**Step 4: Enable auto-recall.** Add the recall hook so each new agent session starts by querying memory for relevant prior work, rather than waiting for an explicit command.

```bash
deja install --auto
```

**Step 5: Point your agent at the MCP server.** Connect the agent's MCP config to the `deja` recall server. From then on, the agent can call the recall tool directly in the flow of a task instead of making you search manually.

```bash
deja mcp  # prints the MCP server settings for Claude Code, Codex, and others
```

You are now running with a memory layer that remembers months of past sessions and is queryable by your agent in under a millisecond.

## Sync, Handoff, and Living on More Than One Machine

Deja Vu also solves the multi-machine problem without a cloud dependency. The session index can be synced across machines over SSH as an append-only store. Because the design is append-only, sync never conflicts: each machine adds its own sessions and merges in the other's without rewriting existing records, and no data ever leaves your machines to a third-party service.

This works for team and machine handoffs too. A colleague (or a second workstation) inherits the same memory layer, so a decision made on your laptop is recallable on the shared machine, and vice versa — without setting up any hosted service or managing an API key.

## Limitations and When a Memory Platform Still Makes Sense

Deja Vu is not the universal answer to agent memory, and its own README is candid about the tradeoffs.

- **It only knows what was recorded.** Facts that were never written to a session log — outside knowledge, project conventions nobody typed into a session, or decisions made mentally — are invisible to it. A recording-forward tool that writes facts is better for durable structured knowledge.
- **Lexical indexing, not semantic reasoning.** Without embeddings, it matches on structure and text rather than meaning. Recall quality depends on how the query text overlaps with what was recorded, and it does not synthesize across facts the way a semantic store can.
- **Corpus size and recall ceiling.** At roughly 85% hit@1 on LongMemEval-S, it is strong but not best-in-class. Applications that need the top few percent of retrieval accuracy on very large knowledge bases are better served by a vector/indexed platform such as CortexDB or Mem0, at the cost of tokens and inference.
- **No reasoning over memory.** A pure index returns what matches. It does not consolidate, deduplicate, or re-derive facts. For tasks that need inference over stored memory (not just retrieval), a reasoning-augmented memory engine is the better fit.

The pragmatic guidance: if your problem is "my agent keeps forgetting commands and decisions from long sessions and I want them back instantly and for free," Deja Vu is purpose-built for that. If your problem is "I want a durable, structured knowledge base my agents write and reason over," a recording-forward platform earns its token and inference cost.

## Frequently Asked Questions

**What exactly does "deja vu" mean for coding agent memory?**
It means a memory layer that indexes the session history your coding agents already wrote to disk, so it "starts full" instead of empty. An agent calling the recall server can search months of past transcripts and get the relevant slice back in under a millisecond, surviving its own context compaction.

**Does Deja Vu need an LLM, embeddings, or an API key?**
No. It is a single zero-dependency local Go binary that performs lexical indexing with no model inference, no embedding vectors, and no API key. All processing happens offline on your machine.

**Which coding agents does Deja Vu support?**
It supports 20+ agents that record their conversations to local files, including Claude Code, Codex, Cursor, opencode, and Copilot CLI. Because the memory layer is shared, a decision made in one agent is recallable in another.

**How does it survive context compaction?**
When a session rolls up into a summary, most detail is lost — in tests across 43 compactions the surviving summary kept 77% of decisions but only 0.2% of commands. Deja Vu indexes the pre-compaction transcripts, so the original details remain queryable after the session summaries.

**Is it open source and free?**
Yes. The `vshulcz/deja-vu` project is MIT-licensed and runs entirely locally with no cloud service and no per-query cost, which distinguishes it from token-based memory platforms that charge for semantic recall.

---

*Note: "Deja Vu" is used by two independent projects. This article covers the session-indexing memory layer at `vshulcz/deja-vu` — a local Go binary that indexes coding-agent session history — not the repo-local Markdown system at `focaxisdev/deja-vu` or the `agentmemory` platform. Always verify which project a documentation link refers to before you install.*
