---
cover:
  alt: 'Multi-Agent System Design: Boundaries, State, and Failure Recovery'
  image: /images/multi-agent-system-design-guide-2026.png
  relative: false
date: 2026-05-18 21:03:56+00:00
description: Choose an agent architecture from task dependencies, define handoff contracts, and plan recovery tests without unsupported performance promises.
draft: false
schema: schema-multi-agent-system-design-guide-2026
tags:
- multi-agent systems
- AI architecture
- LangGraph
- production AI
- agent design patterns
title: 'Multi-Agent System Design: Boundaries, State, and Failure Recovery'
lastmod: '2026-10-20T07:02:10.628622+00:00'
---

A multi-agent design is useful when work can be separated into tasks with clear inputs and reviewable outputs. It becomes harder to justify when every participant needs the same changing context or can modify the same resource.

Start with the smallest workflow that can complete the task reliably. Add an agent when it has a distinct responsibility, information boundary, or permission set. The design below uses a support-answer drafting workflow to make those boundaries concrete.

## Choose a structure from the dependency graph

Anthropic's [agent design guide](https://www.anthropic.com/engineering/building-effective-agents) distinguishes predictable workflows from agents that choose their next steps. Its [multi-agent research account](https://www.anthropic.com/engineering/multi-agent-research-system) describes parallel research workers, along with coordination and token-cost challenges. Those are useful design observations, not a benchmark for your application.

## A decision table for the first implementation

| Task characteristic | Starting design | Main failure to plan for |
|---|---|---|
| Known sequence with stable intermediate artifacts | Explicit pipeline | An early error contaminates later steps |
| Independent research questions | Coordinator with bounded workers | Duplicate work, inconsistent evidence, runaway cost |
| Different specialist permissions | Router to a narrowly authorized worker | Incorrect routing or leaked context |
| One output needs independent review | Draft-and-review loop | Endless revision or a reviewer repeating the same error |
| Participants must edit shared state | Central state owner with serialized writes | Conflicts, duplicate effects, stale approvals |

Do not choose a peer-to-peer topology solely because a diagram looks decentralized. First specify who owns state and who can commit a side effect.

For ten fully connected peers, there are `10 × 9 / 2 = 45` possible undirected pairwise relationships. Ten workers connected only to one coordinator have ten coordinator-worker relationships and eleven total participants. This counts potential communication relationships; it does not predict message volume, latency, or API cost.

## A concrete support-answer workflow

Suppose a team wants draft answers to product-support questions. Use a coordinator to classify the request, a retrieval worker to collect permitted documentation, a drafting worker to write a proposal, and a reviewer to check that each material claim has support. A person or separately authorized service decides whether to send the answer.

Pass a compact artifact between steps:

```json
{
  "task_id": "example-001",
  "request_revision": 3,
  "status": "draft",
  "source_ids": ["doc-a", "doc-b"],
  "unresolved_questions": ["Does the requested plan include this feature?"],
  "proposed_action": "return_draft",
  "external_write_authorized": false
}
```

These field names are an illustrative application contract, not a framework API. Keep source documents in a store with their access rules; do not pass private material to a worker that lacks access. A model-generated `external_write_authorized` value must never substitute for the application's permission check.

The reviewer should be able to reject a claim without inventing a replacement. An unresolved question is an acceptable output when the evidence is missing. Distinguish “retrieval completed” from “answer approved.”

## Make recovery an explicit design requirement

Persist task identity, input revision, state transition, and result references. On resume, check whether the input changed and whether an external operation already happened. A saved checkpoint alone cannot undo an email, payment, or third-party API call.

Use the [failure-injection worksheet](/research/content-quality-2026-10/framework-recovery.csv) to plan interruptions before an operation, after the operation but before the checkpoint, and after the checkpoint. Record the final business state as well as the workflow status. Duplicate submissions should not create duplicate effects.

For the support example, the retrieval and drafting steps can be repeated. Sending the answer needs a durable operation identifier and a check of the approved draft revision. If the content changes after approval, that approval no longer describes the same action.

## Budget the complete run

Assume three workers each consume a budget of four tool calls, while the coordinator may use two calls. The initial maximum is `3 × 4 + 2 = 14` calls. If each worker can retry its entire budget once, the worker allowance doubles and the maximum becomes twenty-six. Model calls, tool fees, and elapsed time still need their own limits.

Set a task-level ceiling that every worker draws from. Stop spawning new work when that ceiling is exhausted. Track useful accepted outputs, not only completed agent turns, when calculating cost.

## Select a framework after writing the contract

Use the [LangGraph, CrewAI, and Dapr comparison](/posts/langgraph-crewai-dapr-comparison-2026/) to map the design to state persistence and operational requirements. Keep the acceptance criteria independent of the framework: correct access boundaries, recoverable work, bounded retries, reviewable evidence, and observable final effects.

Evaluate a single-worker baseline with the same tasks before adding parallel workers. If the system becomes more complex without improving accepted outcomes, retain the simpler design.

## Revision note

**Updated October 20, 2026.** Removed unsupported adoption, recovery, savings, and regulatory generalizations. Added an original handoff contract, topology arithmetic with consistent node counts, and an explicit recovery worksheet.

## Primary sources

Checked October 20, 2026: [anthropic patterns](https://www.anthropic.com/engineering/building-effective-agents); [anthropic multiagent](https://www.anthropic.com/engineering/multi-agent-research-system).
