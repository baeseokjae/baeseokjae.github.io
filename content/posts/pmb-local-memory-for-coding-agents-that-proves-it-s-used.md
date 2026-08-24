---
title: "Local Coding Agent Memory That Proves It's Used: PMB Review"
date: 2026-08-24T19:02:12+00:00
tags:
  - local coding agent memory
  - pmb agent memory
  - coding agent memory review
  - claude code memory
  - codex memory
  - cursor memory
  - local-first agent memory
  - MCP memory server
  - open source agent memory
description: "PMB is a local-first, MCP-native memory layer for coding agents that measures whether memory actually changes outcomes — not just claims it."
draft: false
cover:
  image: "/images/pmb-local-memory-for-coding-agents-that-proves-it-s-used.png"
  alt: "PMB: Local Memory for Coding Agents That Proves It's Used"
  relative: false
schema: "schema-pmb-local-memory-for-coding-agents-that-proves-it-s-used"
---

PMB is a local-first, MCP-native memory layer for AI coding agents that stores everything in one SQLite file on your disk and — unusually — measures whether that memory actually changes outcomes. Instead of claiming "+X% faster," it scores each surfaced lesson against the turn's real result, so you can see when memory is genuinely helping.

## Why Coding Agents Forget — and Why "Memory" Is the Hard Part

Every coding agent you've used — Claude Code, Cursor, Codex, Windsurf, Zed, VS Code, gemini, opencode, continue — starts each session with a clean slate. The model has no persistent recollection of the architecture decisions you made last week, the test suite you just fixed, or the deployment gotcha that cost you an afternoon. This is the "forgetting problem," and it is the single biggest reason long-running projects feel like they restart from zero every time you open a new session.

The hard part of agent memory is not storage. Storing text is trivial. The hard part is **getting the agent to actually use the memory at the right moment** — and doing so without flooding the context window with irrelevant facts. A memory system that requires the model to "remember to call a tool" fails in practice, because the model is exactly the thing that forgets. That is why the category has exploded: hundreds of projects now try to give coding agents durable memory, from heavyweight tools like Beads to lightweight retroactive indexers like deja-vu.

## What Makes PMB Different: Memory That Proves It's Used

PMB (oleksiijko/pmb) enters this crowded field with a deliberately contrarian pitch: it does not ask you to trust that memory helps. It measures it. The project's core differentiator is **Earned Memory** — a scoring system that joins each surfaced lesson to the outcome of the turn in which it was used, then reports whether that lesson was actually useful, harmful, or unverified. No LLM is involved in the scoring; it reads real signals like tests passing, a red-to-green fix, a successful build, or a completed deploy.

This matters because most agent-memory tools market themselves with vague productivity claims. PMB's philosophy, stated plainly in its docs, is that "a memory system you can't measure is one you can't trust." It would rather show you "insufficient" than let a flattering-but-wrong number quietly re-weight your memory. That honesty is the review's core hook, and it is genuinely rare in this space.

## How PMB Works — SQLite Source of Truth, Hybrid Recall, Async Writes

Under the hood, PMB is refreshingly simple. One SQLite file is the source of truth for all memory. Beside it, LanceDB holds rebuildable vector indexes — meaning the vectors can be regenerated from the SQLite data at any time, so nothing is ever lost if an index corrupts.

Recall is **hybrid**: it fuses BM25 keyword search, dense vector embeddings, an entity graph, and an optional cross-encoder rerank, combined via Reciprocal-Rank-Fusion. This gives you the best of both worlds — exact keyword matches and semantic similarity — without relying on any single retrieval method.

Writes are asynchronous and fast. The project reports `record_batch_async` writes returning in under 1ms, `prepare()` in 4–16ms, and warm recall at roughly 35ms (p50) with 110ms at p95. MCP cold boot takes about 3.7 seconds. These numbers matter because a memory layer that adds latency to every turn will get disabled; PMB is designed to stay out of the way.

## Hooks That Don't Wait to Be Asked: Auto-Recall, Ambient Memory, Session-Restore

The most important design decision in PMB is that it works at the **protocol level**, not the tool level. It wires hooks into the agent's own lifecycle so the model never has to remember to call a memory tool:

- **UserPromptSubmit auto-recall** — before the model thinks, PMB injects relevant memory automatically.
- **PostToolUse ambient observe** — after a tool runs, PMB journals what happened.
- **SessionStart session-restore** — when a session opens, prior context is restored.
- **Stop follow-through + ambient auto-write** — when a turn ends, PMB records the outcome and writes lessons.

This is the answer to the "remember to call a tool" failure mode. The hooks fire whether or not the model cooperates. On the write side, **ambient memory** journals the agent's work even when it forgets to call `record_batch`, tagging entries as `source=autowrite` and scoring them by outcome (tests passed, failure fixed, deploy ran). If you don't like it, `pmb forget-auto` reverses it.

## Earned Memory — Measuring Whether Memory Actually Helps

Earned Memory is the heart of PMB's "proves it's used" claim, and it reports at three levels of rigor:

1. **Associational lift** (weakest) — compares outcomes on turns where a lesson surfaced versus turns where it didn't. This is confounded: lessons tend to surface on harder turns, so a genuinely helpful lesson can show *negative* lift. PMB flags this as a review signal, never as ground truth.
2. **Statistical honesty** — uses a 95% Wilson confidence interval and only labels a lesson useful or harmful when the CI clears baseline **and** the sample size meets a minimum. Otherwise it reports "unverified" or "insufficient."
3. **Within-lesson causal read** (strongest) — holds the surfacing trigger fixed and compares the same lesson followed versus ignored.

The key guarantee: an n=1 fluke can never read as a real effect. And critically, Earned Memory is **measurement-only** — it does not feed ranking or decay until the outcome signal is dense enough to trust. PMB would rather under-claim than let a wrong number re-weight your memory.

## The Context-Bloat Problem and How PMB Handles It

The top user concern about agent memory — raised repeatedly in the Show HN thread — is context bloat: "My main concern is that it can overwhelm the context window with useless facts." Because PMB auto-injects memory before the model thinks, this risk is real and central.

PMB's answer is a **follow-rate scoring** system. Every surfaced lesson carries a `surface_id`, and follow-through is recorded both by agent confirmation (`mark_lesson_followed`) and by Stop-hook inference. The dashboard's Lessons tab then classifies each lesson:

- **USEFUL** — followed at least twice
- **UNVERIFIED** — not enough signal yet
- **DEAD** — ignored at least twice

Dead lessons are flagged for removal, and trivial-message filtering keeps noise out. This is the mechanism that turns "memory that proves it's used" from a slogan into an operational loop: lessons that don't get followed get pruned, and lessons that do get followed get promoted.

## Hands-On: Quickstart, Connecting Agents, and the Dashboard

Getting started is genuinely quick. The quickstart is seven commands:

```
pip install pmb-ai
pmb setup
pmb warmup
pmb stats
pmb recall
pmb doctor
```

`pmb connect` wires one or more agents to one workspace. All connections are stdio — the server runs as a child of the agent, so there is no network port and no token to manage. Two agents can share one memory by pointing at the same workspace; SQLite WAL plus a 10-second busy-timeout handles concurrent writes. For teams, an optional HTTP mode with bearer-token auth enables multi-machine sharing.

The dashboard binds to `127.0.0.1:8765` and is where PMB's transparency shines. It includes a **Map** (live entity graph), a **Timeline** (git-graph journal), and nine tabs including Lessons, Duplicates, Performance, and Recall. You can inspect exactly what memory exists, why a lesson is classified the way it is, and manually review borderline dedup cases.

## Privacy, Security, and Local-First Trust

PMB is 100% offline by default with zero telemetry. Your workspace lives under `~/.pmb/<name>/` and is fully copyable and exportable (`pmb export` dumps to Markdown or JSON). There are no API keys, no cloud dependency, and no LLM call on the read path.

Security is handled at write time: PMB auto-redacts secrets — OpenAI, Anthropic, AWS, Stripe, and GitHub keys — before they hit disk, and the redaction list is configurable. Dedup uses four layers (exact text match → cosine ≥0.92 auto-merge → 0.80–0.92 borderline for later LLM verification → manual review in the dashboard), and old values are archived, never deleted, with `keyed_fact_as_of(t)` for time-travel. The license is Apache 2.0.

## Benchmarks and Real-World Numbers

PMB publishes concrete numbers rather than vague claims:

| Metric | Value |
|--------|-------|
| Warm recall (p50) | ~35ms |
| Warm recall (p95) | ~110ms |
| `prepare()` | 4–16ms |
| `record_batch_async` write | <1ms |
| MCP cold boot | 3.7s |
| LoCoMo recall@10 | 94.5% (n=10) |
| Multilingual top-10 | 99.2% (900-query mega-stress) |
| Default embedder languages | 50+ |

The default embedder, `paraphrase-multilingual-MiniLM-L12-v2`, covers 50+ languages out of the box — a Russian query can find an English fact, with top-1 scores of 1.00 for en/fr/pt/ru on a 101-query eval. There are 105 configurable settings: 25 default-tier keys that affect day-to-day quality, and 80 advanced knobs hidden behind `--pro`.

## PMB vs the Landscape: Beads, deja-vu, ctx, mem0, and the DIY Crowd

PMB is young — 296 GitHub stars, 23 forks, created 2026-05-25 — and it is honest about not being a category leader. Here is how it stacks up against the closest cousins:

| Tool | Approach | Differentiator | Stars |
|------|----------|----------------|-------|
| **Beads** (Steve Yegge) | Persists/recalls decisions across sessions | Category heavyweight by adoption | 26,551 |
| **deja-vu** | Retroactive verbatim-text search (BM25), no embeddings | P2P sync over SSH; indexes pre-install sessions | 693 |
| **PMB** | Local-first SQLite + hybrid recall + MCP hooks | Earned Memory follow-through measurement | 296 |

Beads is the reference point for the category by raw adoption. deja-vu is the closest functional cousin — it indexes sessions agents already wrote to disk, including months before install, with 85.3% hit@1 on LongMemEval-S and 69.6% on LoCoMo, but it is retroactive verbatim search with no follow-through measurement. PMB differentiates on proactive protocol-level hooks, an entity graph, and — above all — honest impact scoring. The broader landscape includes ctx, mem0, zep, Mnemos, NexusMem, Mimirs, and CodeYam, plus a DIY crowd building their own memory files.

## Honest Limitations — Young Project, Small Community, Differentiation Pressure

A fair review has to flag the downsides. PMB is a young project with a small community (296 stars, 3 open issues). The Show HN thread drew healthy skepticism: one commenter noted "35ms local ain't a brag" and asked why this is different from the "tonnes of agent memory options" already out there. Another called for a "memory arena" to objectively compare the hundreds of projects in this space. The site itself had an intermittent load failure reported.

The differentiation pressure is real. PMB's answer — honest measurement — is compelling, but it is a niche angle, not a moat. The context-bloat risk, the #1 user fear, is only partially mitigated by follow-rate scoring. And because Earned Memory is deliberately conservative, early users will see a lot of "insufficient" signals before the system has enough data to be useful. That is honest, but it is also a patience tax.

## FAQ: Is PMB Right for Your Setup?

**Is PMB free and open source?**
Yes. PMB is Apache 2.0 licensed, installable via `pip install pmb-ai`, with no API keys and no cloud dependency. The dashboard, all hooks, and Earned Memory scoring are included.

**Which coding agents does PMB support?**
PMB connects via MCP to Claude Code, Cursor, Codex, Windsurf, Zed, VS Code, gemini, opencode, and continue. `pmb connect` wires one or more agents to a single shared workspace over stdio.

**Does PMB send my code or memory to the cloud?**
No. PMB is 100% offline by default with zero telemetry. Everything lives in a local SQLite file under `~/.pmb/<name>/`, and secrets are auto-redacted at write time. Optional HTTP mode for teams uses bearer-token auth.

**How does PMB prove memory is actually used?**
Through Earned Memory, which joins each surfaced lesson to the turn's real outcome (tests pass, red-to-green, build, deploy) and reports at three rigor levels — associational lift, Wilson-CI statistical honesty, and within-lesson causal read. An n=1 fluke can never read as a real effect.

**What is the main risk, and how does PMB handle it?**
The main risk is context bloat — auto-injected memory overwhelming the context window. PMB counters with follow-rate scoring (USEFUL/UNVERIFIED/DEAD), dead-lesson detection, and trivial-message filtering, so lessons that don't get followed get pruned.

## Final Verdict — A Memory Layer That Earns Its Place

PMB is not the biggest or most established agent-memory tool, and it does not pretend to be. What it offers is something rarer: a local-first, MCP-native memory layer that refuses to overclaim and instead measures whether memory actually changes outcomes. The hybrid recall is fast, the hooks work at the protocol level so the model never has to remember, and the Earned Memory system is a genuinely novel answer to the question every agent-memory tool dodges — "does this actually help?"

If you want a memory layer you can trust because it proves it's used, PMB is worth a serious look. It is young, so expect a patience tax while the outcome signal accumulates. But for developers who value honest measurement over marketing, that is exactly the point.
