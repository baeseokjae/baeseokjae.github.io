---
title: "MarkMem: A Git-Native Plain-Markdown Memory Layer for Chatbots"
date: 2026-09-07T10:01:48+00:00
tags:
  - markmem
  - chatbot memory
  - AI agents
  - markdown
  - git
  - LLM memory
  - GDPR compliance
description: "MarkMem stores chatbot memory as plain markdown in a git repo, with bi-temporal facts, a Presidio PII gate, and git as the compliance surface."
draft: false
cover:
  image: "/images/markmem-git-markdown-chatbot-memory-2026.png"
  alt: "MarkMem: A Git-Native Plain-Markdown Memory Layer for Chatbots"
  relative: false
schema: "schema-markmem-git-markdown-chatbot-memory-2026"
---

MarkMem is a git-native, plain-markdown memory layer for chatbots that stores every fact as an inspectable Markdown file in a git repository, backed by a rebuildable SQLite cache. It combines bi-temporal facts in YAML, a Presidio PII write gate, and git as the compliance surface, so you can `cat`, `grep`, and `git-diff` your chatbot's memory instead of trusting an opaque vector database.

## What is MarkMem and why do chatbots forget?

Every chatbot that carries context across sessions faces the same problem: the model's context window is finite, and once a conversation scrolls past it, the details are gone. Traditional memory layers solve this by embedding facts into a vector database and retrieving the most similar chunks at query time. That works, but it turns your chatbot's memory into a black box — you cannot read it, audit it, or prove what it contains.

MarkMem takes the opposite approach. It stores memory as plain Markdown files inside a git repository. Each fact is a human-readable document that you can open in any editor, search with `grep`, and version with `git`. The SQLite index that powers fast retrieval is treated as a rebuildable cache: delete it and run `markmem reindex` to restore everything from the Markdown source of truth.

This design is the core of the "inspectable memory" argument. Vector databases trade away the ability to `cat`, `grep`, or `git-diff` your own memory. MarkMem restores it, giving you a memory layer that is both fast enough for production and fully transparent.

## The ecosystem gap — why vector databases fall short

The incumbent memory layers are dominated by vector and graph approaches. Mem0, the most popular option, has 64.8K GitHub stars and provides a drop-in vector/graph-based memory infrastructure built for production scale. Khoj (37.1K stars) is a broader self-hostable AI second brain. Graphiti (30.6K stars) builds real-time knowledge graphs with strong relationship tracking. Letta (24.6K stars) descends from MemGPT and focuses on stateful agents that learn and self-improve.

| Tool | Stars | Storage model | Focus |
|------|-------|---------------|-------|
| mem0 | 64.8K | Vector/graph | Production-scale memory infrastructure |
| Khoj | 37.1K | Vector + docs | Self-hostable AI second brain |
| Graphiti | 30.6K | Knowledge graph | Temporal relationship memory |
| Letta | 24.6K | Stateful agent | Agent statefulness and self-improvement |
| basic-memory | 3.8K | Markdown | Plain-markdown memory niche |
| memweave | 54 | Markdown | Async-first markdown memory |
| MarkMem | new | Markdown + git | Git-native, compliance-first memory |

The gap is clear: the big players optimize for scale and statefulness, but none of them make memory inspectable as plain text with git as the compliance surface. basic-memory and memweave occupy the markdown niche but lack the hybrid search, bi-temporal facts, and compliance tooling that MarkMem bundles together. MarkMem is the only tool combining markdown, hybrid search, git compliance, and bi-temporal facts in one package.

## The three pillars: bi-temporal facts, Presidio write gate, git compliance

MarkMem is built on three unique pillars that together address the weaknesses of both vector databases and naive markdown stores.

**Bi-temporal facts in YAML.** Facts carry both a valid time (when the fact is true) and a transaction time (when it was recorded). When a fact is superseded, the old one is closed with a `valid_until` timestamp rather than silently overwritten. This enables `as_of` temporal reasoning — you can ask what the chatbot knew at any point in the past, and you never lose the history of a correction.

**Presidio as a PII write gate.** Before any fact reaches disk, it passes through Microsoft's Presidio, which detects and blocks or masks sensitive entities such as Social Security numbers, email addresses, and credit card numbers. This is a write-time gate, not a post-hoc scan, so PII never lands in your memory store in the first place.

**Git as the compliance surface.** Every write becomes a git commit, giving you a full audit trail via `git log`. GDPR erasure is provable and path-scoped: you can scrub a specific user's facts, rewrite them, or crypto-shred them against backups, and the git history documents exactly what was removed and when.

## How MarkMem works under the hood

The write path is a pipeline: **add → PII gate → compile → git commit**. When a fact is added, it is first checked by the Presidio gate. If it passes, it is compiled into a Markdown document and committed to the git repository. The SQLite index is updated as a cache.

On the read side, MarkMem uses a tiered search strategy. **L0** is a fast in-memory cache for the hottest facts. **L1** uses BM25 keyword search over the Markdown content. **L2** adds vector retrieval when a vector extra is installed. The tiers are fused with Reciprocal Rank Fusion (RRF), so you get the precision of keyword search and the semantic reach of vectors without requiring a vector database as a hard dependency.

This zero-hard-dependency design is deliberate. With no vector extra installed, MarkMem runs on BM25 alone. With no LLM API key, it falls back to a heuristic extractor. The core library never imports torch, so it stays lightweight and easy to deploy.

## Installation and quick start

MarkMem is Apache-2.0, written in Python, and published on PyPI as `markmem`. It was created on 2026-08-18. Installation is a single command:

```bash
pip install markmem
```

The primary interface is the `Memory` API. You add facts, search them, and retrieve context for your chatbot:

```python
from markmem import Memory

memory = Memory(repo_path="./memory")
memory.add("The user prefers concise responses in Korean.")
results = memory.search("how should I respond?", format="context")
```

The `format="context"` option packs the retrieved facts into a ready-to-inject context block for your LLM prompt. The package also ships 19 CLI commands for managing the memory store, reindexing, exporting, and inspecting the git history.

## Using any LLM with LiteLLM and the MCP/REST/CLI integrations

MarkMem supports 100+ LLMs through LiteLLM, so you are not locked into a single provider. You can plug in OpenAI, Anthropic, local models, or any LiteLLM-compatible endpoint.

Beyond the Python API, MarkMem exposes an MCP server, a REST API, and the CLI. The MCP server is especially useful for agent frameworks that speak the Model Context Protocol — your chatbot can call memory tools directly through MCP without custom glue code. The REST API lets you integrate MarkMem into any language or service, and the CLI covers scripting and manual inspection.

## Compliance and erasure modes

Compliance is where MarkMem differentiates itself most sharply. Because memory lives in git, erasure is not a destructive delete that leaves no trace — it is a documented, auditable operation.

- **Scrub mode** removes a user's facts from the current state.
- **Rewrite mode** replaces sensitive content with sanitized values.
- **Crypto-shred mode** encrypts facts and destroys the key, making the data unrecoverable even from backups.

In MarkMemBench, GDPR erasure via crypto-shred plus tombstone completed in 230.5ms. The git history provides a provable, path-scoped audit trail of exactly what was removed, which is a significant advantage for organizations that must demonstrate compliance to regulators.

## Portability and migration

MarkMem is designed to avoid lock-in. You can export the entire memory store losslessly to JSONL, migrate to or from mem0, and export to the Claude Code memory-md format. This means you can start with MarkMem, and if your needs change, your memory is not trapped in a proprietary format — it is plain Markdown you can take anywhere.

## Benchmarks and security edge cases

MarkMemBench reports strong results across recall, latency, and isolation:

| Metric | MarkMem | Mem0 | Letta/MemGPT | Khoj |
|--------|---------|------|--------------|------|
| LoCoMo R@5 evidence recall | 83.3% | 92.5% | 68.5% | 83.2% |
| Search latency p50 | 1.5ms | 880ms | — | — |
| Context packing latency p50 | 2.0ms | — | — | — |

MarkMem trails Mem0 on raw evidence recall (83.3% vs 92.5%) but is dramatically faster on search latency — 1.5ms p50 versus 880ms for Mem0. It also reports 100% multi-user isolation with zero leaks, 100% temporal reasoning supersession accuracy, and the 230.5ms GDPR erasure path mentioned above.

## Limitations and when to choose an alternative

MarkMem is not a universal replacement for every memory layer. Its main limitation is scale: it is designed for roughly 50–100K pages per repository. Many small files are the worst case for both git and NTFS, so extremely large memory stores will hit performance and filesystem limits. The FTS5 stemming is also English-biased, which matters if your content is heavily non-English.

If you need to store millions of facts, require heavy graph-based relationship reasoning, or need the scale that mem0 and Graphiti target, a vector or graph store may be a better fit. MarkMem is the right choice when inspectability, compliance, and portability matter more than raw scale.

## Conclusion — is MarkMem right for your chatbot?

MarkMem fills a real gap in the chatbot memory ecosystem. If you want memory you can read, audit, and prove compliance for — and you are comfortable with a plain-markdown, git-native workflow — it is a compelling choice. It is fast, portable, PII-safe at the write gate, and gives you a full audit trail out of the box. For teams that value transparency and compliance over raw scale, MarkMem is worth serious consideration.

## FAQ

**What is MarkMem?**
MarkMem is a git-native, plain-markdown memory layer for chatbots. It stores every fact as an inspectable Markdown file in a git repository, with a rebuildable SQLite cache for fast retrieval.

**How is MarkMem different from mem0?**
Mem0 is a vector/graph-based memory infrastructure built for production scale. MarkMem stores memory as plain Markdown in git, making it inspectable and auditable. MarkMem is also dramatically faster on search latency (1.5ms vs 880ms p50) but trails mem0 on raw evidence recall.

**Does MarkMem require a vector database?**
No. Vector retrieval is optional. Without a vector extra, MarkMem runs on BM25 keyword search alone, and it fuses BM25 and vector results with Reciprocal Rank Fusion when vectors are available.

**How does MarkMem handle GDPR erasure?**
MarkMem uses git as the compliance surface. Erasure is a documented, auditable operation with scrub, rewrite, and crypto-shred modes. Crypto-shred plus tombstone completes in about 230ms and provides a provable, path-scoped audit trail.

**What are MarkMem's limitations?**
MarkMem is designed for roughly 50–100K pages per repository, since many small files are the worst case for git and NTFS. Its FTS5 stemming is English-biased, and it is not the best choice for very large or graph-heavy memory workloads.
