---
cover:
  alt: 'Zep AI Review 2026: Temporal Knowledge Graphs for Agent Memory'
  image: /images/zep-ai-agent-memory-review-2026.png
  relative: false
date: 2026-05-07 18:04:24+00:00
description: 'A source-based review of Zep and Graphiti: temporal memory, correctly scoped benchmark evidence,
  current pricing, and production evaluation questions.'
draft: false
schema: schema-zep-ai-agent-memory-review-2026
tags:
- agent memory
- knowledge graph
- AI agents
- Zep AI
- Graphiti
title: 'Zep AI Review 2026: Temporal Knowledge Graphs for Agent Memory'
lastmod: 2026-10-07 00:00:00+00:00
---

Zep provides a managed context layer for AI applications, using temporal graph artifacts derived with Graphiti. Graphiti is its open-source temporal knowledge graph framework. This review explains the architecture and its evaluation limits; it does not report an independently reproduced product benchmark. [Source: Zep documentation](https://help.getzep.com/graphiti/getting-started/overview).

> **Correction — October 7, 2026:** The previous version described unrelated benchmark values as an independent Zep-versus-Mem0 comparison and called an arXiv paper peer-reviewed without evidence for that status. Those claims, unverified latency promises and unsupported integration examples have been withdrawn.

## What Temporal Memory Adds

A temporal graph represents entities, relationships and the times associated with facts. Graphiti supports ingestion of structured and unstructured information and retrieval that combines semantic, text and graph approaches. Its temporal model can represent changes while preserving historical context. [Source: Graphiti overview](https://help.getzep.com/graphiti/getting-started/overview).

Consider an assistant that first learns that Alice works for one employer and later receives an update naming a different employer. A useful memory system must preserve the evidence, resolve the update and answer both “where does Alice work now?” and “where did Alice work last year?” appropriately.

Temporal metadata helps express that problem. It does not guarantee correct extraction, entity resolution or answers. A missing invalidation timestamp is not proof that a claim is true: the system may not have seen an update, or extraction may have failed. Validate the returned evidence before taking consequential action.

## Graph Memory, Vector Retrieval and Full Context

These are implementation choices that can be combined. Vector retrieval can include timestamps, metadata filters, reranking and application-level update rules. It is inaccurate to say that it inherently cannot handle current facts or multi-step retrieval. A graph can make relationships explicit while still relying on embeddings and an LLM.

| Approach | What to evaluate | Common implementation questions |
|---|---|---|
| Temporal graph | Relationship extraction and time-aware retrieval | Wrong merges, missed updates, provenance and deletion |
| Vector-based retrieval | Relevant evidence under filters and ranking rules | Duplicate chunks, stale results, chunking and metadata quality |
| Full conversation context | Answer quality using retained source material | Input size, latency, cost and irrelevant history |

This table describes evaluation concerns, not measured product rankings. Compare systems using the same data, question set, answer model and resource limits before choosing one.

## What the Zep Paper Actually Measures

The authors' [January 2025 Zep paper](https://arxiv.org/html/2501.13956v1) reports the following LongMemEval_s results in Table 2:

| Memory method | Answer model | Reported score |
|---|---|---|
| Full context | GPT-4o-mini | 55.4% |
| Zep | GPT-4o-mini | 63.8% |
| Full context | GPT-4o | 60.2% |
| Zep | GPT-4o | 71.2% |

The same table does **not** contain a Mem0 row. The former “63.8% versus 49.0%, a 15-point advantage” statement therefore does not follow from this experiment. The paper's authors are associated with Zep; this is author-reported research, not an independent reproduction by this blog. An arXiv posting alone does not establish peer review.

Benchmark results apply to the documented setup and release, not automatically to the current managed service or a self-hosted installation. Model choice, ingestion, retrieval budget, prompts and grading can change the outcome. This article does not assert a current cross-product winner or a universal p99 latency guarantee.

### A Fair Memory Evaluation

Use a fixed dataset and question set, including updates, contradictions, deletions and out-of-scope questions. Keep the answer model and scoring procedure the same. Record default settings separately from tuned configurations, and retain the retrieved evidence for each answer.

Measure ingestion cost and latency as well as retrieval and answer generation. Include failure recovery and document what happens when a write succeeds but extraction is delayed or fails. For multi-tenant applications, test whether one user's data can be retrieved by another. A benchmark accuracy score does not establish that access controls work.

## Zep Cloud and Graphiti Are Different Deployment Choices

The [current documentation](https://help.getzep.com/graphiti/getting-started/overview) distinguishes the Graphiti framework from Zep's managed context service. Self-hosting the framework requires operating the selected graph storage and model/embedding dependencies. It is not a turnkey duplicate of every managed-service capability.

For current installation and supported configurations, use the [Graphiti repository](https://github.com/getzep/graphiti). Pin the version, review its license and follow the corresponding examples. A self-hosted graph can still use a hosted LLM or embedding service, so document the complete data path when local operation matters.

### Integration Example Boundaries

The earlier article included guessed wrapper classes and an unsupported `memory_type="perpetual"` configuration. Those snippets have been removed. Graphiti's current public API uses methods such as `add_episode` and `search`, with explicit episode metadata and asynchronous calls; use the maintained [Neo4j quickstart](https://github.com/getzep/graphiti/blob/main/examples/quickstart/quickstart_neo4j.py) for runnable setup instructions.

If integrating with an agent framework, separate storing context from checkpointing execution state. Decide what is written, which namespace is searched, how errors are handled and what the agent is allowed to reveal. Similar names in an older integration package do not guarantee compatibility with a current SDK.

## Pricing: Checked October 7, 2026

Zep's [pricing page](https://www.getzep.com/pricing/) currently lists the following monthly self-serve plans:

| Plan | Monthly price | Included credits | Additional credits |
|---|---|---|---|
| Flex | $125 | 50,000 | $25 per 10,000 |
| Flex Plus | $375 | 200,000 | $75 per 40,000 |
| Enterprise | Negotiated | Negotiated | Negotiated |

The page offers 10,000 monthly credits for prototyping, subject to limits. It meters episode ingestion by size: one credit for up to 350 bytes, with another credit for each additional 350 bytes or part. Other operations can have different treatment. Check the current limits, billing mode and top-up behavior before budgeting; the earlier 1,000-credit free-tier description was out of date.

For example, a 700-byte episode is two ingestion credits under that rule. This is arithmetic based on the published unit, not a measured workload bill. Determine actual encoded episode sizes and operation counts before projecting spend. See the [pricing page's credit definitions](https://www.getzep.com/pricing/).

## Production Questions Before Adoption

Test whether the system answers your domain's update and relationship questions better than your existing baseline, then examine the operational tradeoffs. Important questions include:

- Can a user inspect and correct a stored fact and its provenance?
- What is deleted when an episode, user or graph is removed, and when does deletion take effect?
- How are namespaces and permissions enforced during retrieval?
- How are delayed ingestion, retries and inconsistent updates surfaced?
- What data reaches model providers, and what contractual deployment terms apply?

For regulated workloads, verify the applicable contract, plan and deployment configuration. A vendor's listed security offering is not blanket approval for every healthcare or financial use. Avoid treating a framework selection as a substitute for those checks.

## Alternatives and Selection Criteria

Evaluate alternatives such as Mem0, LangMem, Letta or another retrieval stack against the same requirements rather than carrying forward this article's previous unsupported scores or fixed price comparisons. Determine whether the real need is durable user facts, document retrieval, execution checkpoints or a combination.

Choose a small representative scenario and compare correctness, evidence quality, integration work, operational cost and failure handling. A more elaborate graph is not automatically better for a small history; a simple baseline that meets the requirements can be the right result of an evaluation.

## FAQ

### Has this review established that Zep beats Mem0 by 15 points?

No. The cited paper compares Zep with full-context baselines using specified answer models. It does not support the earlier direct Mem0 comparison.

### Is the architecture guaranteed to return the current truth?

No. Temporal records can represent updates, but extraction errors, missing evidence and delayed ingestion still require testing and correction.

### Is Graphiti the same product as Zep Cloud?

No. The framework and the managed service have different operational responsibilities and capabilities. Check the current documentation for the deployment you intend to use.

### Is this a hands-on review with a tested rating?

No. It is a documentation and research review. The earlier numeric rating has been removed because no reproducible scoring rubric or first-party product evaluation supported it.
