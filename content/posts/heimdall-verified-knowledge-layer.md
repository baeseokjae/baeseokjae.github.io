---
title: "Heimdall: A Verified, Self-Healing Knowledge Layer for AI Coding Agents"
date: 2026-08-24T01:02:43+00:00
tags:
  - AI coding agents
  - agent memory
  - knowledge graph
  - semantic search
  - Claude Code
  - Codex
  - MCP
description: "Heimdall is a CPU-only, zero-token knowledge layer that gives AI coding agents trust-verified, self-healing memory across every repo."
draft: false
cover:
  image: "/images/heimdall-verified-knowledge-layer.png"
  alt: "Heimdall: A Verified, Self-Healing Knowledge Layer for AI Coding Agents"
  relative: false
schema: "schema-heimdall-verified-knowledge-layer"
---

Heimdall is an open-source, CPU-only knowledge layer that gives AI coding agents a verified, self-healing memory across every repository you work in. Instead of returning plausible-but-unverified matches, every search result carries a trust verdict — STRONG, WEAK, REBUILT, or STALE — re-checked against your live filesystem at query time. It indexes with tree-sitter and local embeddings, spends zero tokens on memory maintenance, and re-anchors moved files automatically.

## What is Heimdall and why does it exist?

Heimdall is a trust-verified knowledge layer built specifically for AI coding agents. It was released on Hacker News on August 22, 2026, and is published on npm as `@ariantdeva/heimdall` at version 0.2.1. The project's core claim is simple: most agent memory tools return results that *look* right but have not been checked against the actual state of your codebase. Heimdall exists to close that gap.

The tool maintains persistent memory across every repo and project you touch. A single `kb_search` call replaces the familiar grep/find/ls orientation loop that agents run at the start of every task. Because the knowledge graph is cross-repository, knowledge follows the developer across projects, languages, and months of work — rather than being trapped in whichever directory the agent happens to be standing in.

## The problem: memory that doesn't live in one repo, and the orientation tax

Coding agents face two compounding problems that most memory tools ignore.

First, **knowledge is fragmented across repositories.** A developer working on a monorepo, a shared library, and a documentation site has context scattered across three different directory trees. An agent that only sees the current working directory is blind to the other 80% of the relevant context. Per-project memory tools make this worse by design — they scope their index to a single directory and never look beyond it.

Second, **agents pay a heavy orientation tax.** Before an agent can do useful work, it must figure out where things live: which file defines a symbol, which module imports it, where the config lives. This is the grep/find/ls loop, and it burns tokens and latency on every single task. Heimdall's pitch is that a verified knowledge layer turns this repeated discovery work into a single indexed lookup.

The deeper problem is that even when an agent finds a match, it has no way to know whether that match is still true. Files move, get deleted, or get rewritten. A memory entry that was accurate last week can be a confident lie today. This is the "rotten anchors" problem, and it is the specific failure mode Heimdall was designed to solve.

## Trust verdicts: STRONG, WEAK, REBUILT, and STALE explained

The differentiator that sets Heimdall apart is its trust-verdict system. Every search result is labeled with one of four verdicts, and crucially, these verdicts are **re-verified against the live filesystem at query time** — not stored as stale metadata.

| Verdict | Meaning | When it appears |
|---------|---------|-----------------|
| **STRONG** | The result is verified against the current filesystem and is accurate | The file exists, the symbol is present, nothing has changed |
| **WEAK** | The result is plausible but could not be fully verified | A fuzzy semantic match, or a path that exists but whose contents are uncertain |
| **REBUILT** | The result was re-anchored after the file moved | A moved file was automatically re-linked to its new location |
| **STALE** | The result no longer matches the filesystem | The file was deleted or rewritten; the node is being retracted |

This matters because most memory tools return matches that are *plausible but unverified*. An LLM-based memory layer might recall that "the auth module lives in `src/auth.ts`" — but if that file was renamed to `src/authentication/index.ts` last week, the memory is confidently wrong. Heimdall's verdicts make the reliability of each result explicit, so an agent can decide whether to act on it or re-orient.

## Self-healing knowledge graph: how moved files get re-anchored

Heimdall's knowledge graph is self-healing. When a file is moved, the graph does not leave a dead pointer behind — it **re-anchors** the node to the file's new location and marks the result as REBUILT. When a file is deleted, the graph **retracts its own nodes**, pruning dead paths automatically.

This directly solves the "rotten anchors" problem that other tools ignore. In a typical memory system, a moved file leaves behind a stale entry that keeps surfacing in search results, wasting the agent's time and eroding trust in the tool. Heimdall's reconciler notices that a path "might have changed" and re-verifies it, so the graph stays honest about what is actually on disk.

The self-healing behavior is not a gimmick — it is the property that makes the trust verdicts trustworthy. A verdict is only meaningful if the graph actively repairs itself when the underlying filesystem changes. Heimdall couples the two: because the graph heals, the verdicts stay accurate; because the verdicts are re-checked live, the graph's self-repair is verifiable.

## Zero token spend: CPU-only indexing with tree-sitter and local embeddings

One of Heimdall's most distinctive engineering choices is that it **never spends a token on memory maintenance**. Indexing and search run entirely on CPU using:

- **tree-sitter** for AST parsing, which extracts structural knowledge about your code without an LLM
- **local bge-m3 embeddings** for semantic understanding, computed on your own machine
- **sqlite** for storage
- **hybrid ranked search** that combines lexical, semantic, and graph-walk signals

This is a deliberate contrast with LLM-based memory tools like mem0 and Letta, which use language models to extract and manage memory — and therefore incur token cost on every write and every consolidation pass. Heimdall's approach means memory maintenance is effectively free, and it works on machines without a GPU.

The trade-off is real: LLM-based extraction can capture higher-level intent that tree-sitter parsing misses. But for the specific job of *knowing where things live in a codebase*, structural parsing plus local embeddings is often sufficient — and it is dramatically cheaper to run continuously.

## Architecture: the single-writer reconciler and why it matters

Heimdall's architecture contains a design lesson worth studying. The project's v0.2.0 release introduced a **single-writer, level-triggered reconciler**. The key insight is that nothing tells the graph *what* changed — only that a path *might* have changed.

The author's earlier approach tried to infer graph mutations from bash hooks, and it collapsed. Hooks are unreliable: they fire inconsistently, they miss changes made by other tools, and they create a many-writer problem where concurrent mutations corrupt the graph. The fix was to abandon fine-grained change detection entirely and instead use a level-triggered reconciler: a single writer periodically checks whether paths might have changed and re-verifies them.

This is a clean architectural decision. By making reconciliation idempotent and level-triggered rather than edge-triggered, Heimdall avoids the classic distributed-systems failure mode where a missed event leaves the system permanently out of sync. The single-writer constraint guarantees that the graph is never mutated concurrently, which is what makes the self-healing behavior safe.

## Heimdall vs mem0, Letta, Claude Memory, and grep

To understand where Heimdall fits, it helps to compare it directly against the alternatives.

| Tool | Scope | Trust verdicts | Self-healing | Indexing cost | Stars |
|------|-------|---------------|--------------|---------------|-------|
| **Heimdall** | Cross-repo | Yes (STRONG/WEAK/REBUILT/STALE) | Yes (re-anchors moved files) | CPU-only, zero tokens | 34 |
| **mem0** | Per-app/per-user | No | No | LLM-based (token cost) | 63,893 |
| **Letta (MemGPT)** | Per-agent | No | No | LLM-based (token cost) | 24,375 |
| **Engram** | Cross-tool (MCP) | No | Partial (consolidation) | LLM-based | ~2.5K installs |
| **grep / cAST** | Current repo | No | No | Free | — |

The comparison makes Heimdall's positioning clear. It is the only tool in this group that combines **trust verdicts, self-healing re-anchoring, cross-repo scope, and CPU-only indexing**. mem0 and Letta are far more mature and widely adopted, but they rely on LLM-based extraction (token cost) and do not verify their results against the live filesystem. Engram offers persistent memory via MCP and reports 80% accuracy on the LOCOMO benchmark, but it does not provide trust verdicts or re-anchor moved files.

The honest caveat is maturity. Heimdall has 34 GitHub stars and is at version 0.2.1, while mem0 has 63,893 stars and Letta has 24,375. For a production team that needs battle-tested memory, the mature options are safer. For a developer who wants verified, self-healing, zero-token memory and is willing to run early-stage software, Heimdall's feature set is currently unique.

## How to install and wire it into Claude Code, Codex, Cursor, and Windsurf

Heimdall ships as a global npm package and integrates with the major coding-agent harnesses.

```bash
npm i -g @ariantdeva/heimdall
```

The tool provides harness integrations for **pi, Claude Code, Codex, Cursor, and Windsurf**. Once installed, the agent can call `kb_search` to query the verified knowledge layer instead of running the grep/find/ls orientation loop. Because the knowledge graph is cross-repository, the same index serves the agent regardless of which harness or which repo it is currently working in.

Note that the MCP server mode is still on the roadmap, and the ranked-search backend currently depends on a graft backend. For most users, the harness integrations are the practical path today; MCP-based tooling (like Engram's approach) is not yet available for Heimdall.

## Benchmarks and maturity: LongMemEval, the test suite, and the roadmap

Heimdall's maturity story is honest about where it stands. The project reports:

- A reproduced **LongMemEval benchmark baseline S score of 0.740**, with a roadmap target of **LongMemEval-S score ≥ 0.90**
- A **166-test suite** guarding concurrency invariants
- Daily runs on the author's machine across **~12,800 live nodes**
- **34 GitHub stars, 1 fork**, MIT license, JavaScript, created 2026-08-20, updated 2026-08-24
- npm version **0.2.1**

The LongMemEval baseline of 0.740 is a meaningful starting point, but the gap to the 0.90 target is substantial. The 166-test suite focused on concurrency invariants is a good sign for a tool whose core value proposition depends on a single-writer reconciler being correct under load. The daily 12,800-node run is real-world validation, but it is one machine — not a broad user base.

## Verdict: who should use Heimdall today, and what's still missing

Heimdall is a genuinely novel tool with a feature combination that no established competitor offers: **trust verdicts, self-healing re-anchoring, cross-repo scope, and CPU-only, zero-token indexing**. For a solo developer or small team that lives across multiple repositories and wants their coding agent to stop re-orienting on every task, it is worth trying today — especially if you value the zero-token design and the verified results.

What's still missing is maturity and ecosystem. At 34 stars and v0.2.1, Heimdall is early-stage. The MCP server mode is on the roadmap but not shipped. The ranked-search backend depends on a graft backend. The LongMemEval score needs to climb from 0.740 toward the 0.90 target. And the author's own Show HN post scored only 4 points, so the project has not yet attracted broad attention.

The pragmatic recommendation: if you are evaluating agent memory and want the safest choice, mem0 or Letta are the proven options. If you want the *only* tool that verifies its results, heals its own graph, and costs zero tokens to maintain, Heimdall is the one to watch — and to try on a side project before trusting it with production context.

## FAQ

**What is a verified knowledge layer for coding agents?**
A verified knowledge layer is a memory system that checks its stored knowledge against the live filesystem before returning it. Heimdall labels every search result with a trust verdict — STRONG, WEAK, REBUILT, or STALE — so agents know whether a match is still accurate.

**How is Heimdall different from mem0 and Letta?**
Heimdall is the only one of the three that provides trust verdicts, self-healing re-anchoring of moved files, and CPU-only zero-token indexing. mem0 and Letta use LLM-based extraction (token cost) and do not verify results against the filesystem.

**Does Heimdall cost tokens to maintain memory?**
No. Heimdall indexes with tree-sitter AST parsing and local bge-m3 embeddings, all on CPU. Memory maintenance never requires an LLM call or a GPU.

**Which coding agents does Heimdall integrate with?**
Heimdall provides harness integrations for pi, Claude Code, Codex, Cursor, and Windsurf, installed globally via `npm i -g @ariantdeva/heimdall`. MCP server mode is still on the roadmap.

**Is Heimdall production-ready?**
It is early-stage: 34 GitHub stars, version 0.2.1, and a LongMemEval baseline of 0.740 (target ≥ 0.90). It is best tried on a side project before being trusted with production context.
