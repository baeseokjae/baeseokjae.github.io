---
title: "OpsGraph: Evidence-First Agentic PostgreSQL Investigations"
date: 2026-08-22T13:04:07+00:00
tags:
  - ai-agents
  - incident-response
  - langgraph
  - observability
  - postgresql
  - read-only
  - self-hosted
description: "An evidence-first agentic PostgreSQL investigation tool that enforces read-only roles, AST-validated queries, and a tamper-evident audit chain so AI conclusions stay auditable."
draft: false
cover:
  image: "/images/opsgraph-agentic-postgresql.png"
  alt: "OpsGraph: Evidence-First Agentic PostgreSQL Investigations"
  relative: false
schema: "schema-opsgraph-agentic-postgresql"
---

An agentic PostgreSQL investigation is an AI-driven workflow that explores a database to answer operational questions, and OpsGraph makes it evidence-first: it discovers an approved read-only schema, validates every SELECT against the PostgreSQL AST and policy bounds, and records a tamper-evident audit chain so no conclusion can be asserted without opening its exact evidence. Instead of giving a model direct credentials and "asking it anything," OpsGraph constrains the investigation to bounded, read-only, auditable queries that fail closed on unsafe SQL.

## Why Agentic Database Tools Need an Evidence-First Design

The promise of agentic database tooling is seductive: point an LLM at your operational database and let it answer questions, find root causes, and surface anomalies without a human writing every query. But the moment a model holds real credentials to a production database, the risk profile changes dramatically. A single hallucinated `UPDATE`, a missing `WHERE` clause, or a query that scans a billion-row table can turn a helpful assistant into an incident amplifier.

Evidence-first design is the answer to that risk. Instead of trusting the model, the tooling trusts the evidence: every claim must be traceable to a query that actually ran, against a schema the operator approved, within bounds the operator set. This is the core philosophy behind OpsGraph, a self-hosted, read-only PostgreSQL investigation workspace released as a public validation alpha on 2026-08-16 under the Apache-2.0 license.

The distinction matters because operational data is not a sandbox. When an AI investigates a production incident, the cost of a wrong answer is not a failed unit test — it is a wrong diagnosis, a missed root cause, or worse, an accidental write. Evidence-first design treats the database as a read-only crime scene, not a playground.

## What Is OpsGraph? A Self-Hosted, Read-Only PostgreSQL Investigation Workspace

OpsGraph is a Python-based, self-hosted tool that lets an AI agent investigate a PostgreSQL database without ever granting the model direct database credentials or arbitrary SQL execution. It is built around a simple but powerful idea: the agent works inside a constrained workspace where every action is validated, bounded, and recorded.

The tool's own product charter defines its alpha success criteria in concrete, measurable terms:

- A sample investigation completes in under five minutes.
- A PostgreSQL schema can be reviewed within fifteen minutes.
- Every factual claim opens its exact evidence.
- Unsafe SQL and data-bearing dumps fail closed.

These are not vague aspirations. They are testable acceptance criteria that define what "good" looks like for an evidence-first investigation. The five-minute target matters because investigation tools that are slow get abandoned; the fail-closed requirement matters because it is the difference between a safe tool and a dangerous one.

OpsGraph is written in Python and built on LangGraph, which gives it a structured, stateful agent loop. It is self-hosted, meaning the operator controls where it runs, what it can reach, and what data leaves the host.

## The Trust Problem: Why "Ask the Model Anything" Fails for Operational Data

The naive approach to agentic database tooling is to give the model a connection string and a prompt: "investigate this." This fails for three structural reasons.

First, **prompt injection is not a hypothetical**. OpsGraph's threat model explicitly treats prompts, database values, identifiers, comments, logs, uploaded SQL, and playbook text as untrusted. In a real database, a row of data can contain text that looks like an instruction. If the model reads that text and acts on it, stored prompt injection has succeeded. The threat model's requirement is blunt: stored prompt injection must remain inert data — it must never become an action.

Second, **models self-assert evidence**. When you ask a model "is the evidence sufficient?", it will almost always say yes. It has no independent way to know whether it has actually covered the relevant tables, rows, and time ranges. Its confidence is not evidence.

Third, **unbounded queries are dangerous**. A model that can run any SQL can accidentally (or adversarially) run a query that locks a table, exhausts memory, or dumps sensitive data. Without bounds, the investigation tool becomes a liability.

OpsGraph addresses all three by refusing to "ask the model anything." It asks the model to work within a validated, bounded, read-only workspace — and it verifies the model's work against the actual schema and policy, not against the model's own claims.

## Read-Only by Design: Roles, AST Validation, and Bounded Queries

The heart of OpsGraph's safety model is a layered set of controls that make it structurally impossible for the agent to write to the database or run unsafe queries.

**A dedicated read-only role.** OpsGraph discovers an approved PostgreSQL schema through a dedicated read-only role. The model never receives direct database credentials. Instead, it operates through a role that can only read — and only within the schema the operator has explicitly approved. This is the first and most important boundary: no write access, ever.

**AST validation.** Before any query executes, OpsGraph validates the SELECT against the PostgreSQL AST. This is not a string check or a regex. It parses the query into an abstract syntax tree and verifies that it is a well-formed, read-only SELECT. This catches the cases where a model tries to smuggle a write into what looks like a read, or constructs malformed SQL that would behave unpredictably.

**Table scope, row bounds, and time bounds.** The validation layer checks that the query only touches tables within the approved scope, and that it respects row and time bounds the operator has configured. A query that would scan the entire history of a table, or return an unbounded result set, is rejected before it runs.

**A hard query budget.** OpsGraph enforces at most three SELECT queries per investigation. This is a deliberate constraint. It forces the model to be economical and focused, and it caps the blast radius of any single investigation. Three well-chosen queries are almost always more useful than thirty scattered ones.

**A read-only transaction.** Queries execute inside a read-only transaction, adding a final database-level guarantee that nothing can be written, even if a validation layer were somehow bypassed.

The result is a fail-closed system: if anything is ambiguous, unsafe, or out of bounds, the query does not run. The default is denial, not permission.

## Evidence Coverage from Source-Owned Table Bindings, Not Model Self-Assertion

This is the key differentiator that separates OpsGraph from most agentic database tools. When a model claims "I have sufficient evidence to conclude X," how do you know it is telling the truth?

Most tools take the model's word for it. OpsGraph does not. It derives evidence coverage from **source-owned table bindings** — a mapping that the operator (or the schema) defines, which states which tables are the authoritative sources for which facts. The model cannot self-assert that its evidence is sufficient, because sufficiency is determined by whether the queries it ran actually touched the tables that own the relevant evidence.

Concretely, this means the investigation's conclusion is only as strong as the coverage of its evidence. If the model concludes "the slowdown correlates with table X" but never queried table X, the system knows the evidence is incomplete — regardless of how confident the model sounds. This closes the hallucination gap at the point where it matters most: the moment a conclusion is drawn.

This design choice is what makes the tool genuinely evidence-first rather than merely "AI-assisted." The evidence is not whatever the model says it gathered; it is what the audit trail proves it gathered, measured against a source-of-truth mapping the operator controls.

## The Tamper-Evident Audit Chain: Making Conclusions Reproducible

An investigation is only as trustworthy as its record. OpsGraph records evidence hashes and maintains a local, tamper-evident audit chain — an append-only, hash-chained log of audit events.

The mechanics are straightforward: each evidence item is hashed, and each audit event is chained to the previous one via its hash. This means that if anyone modifies an earlier record, every subsequent hash in the chain breaks. Tampering becomes immediately detectable. The chain is append-only, so nothing can be silently rewritten.

For an operator, this delivers two things. First, **reproducibility**: any conclusion can be traced back to the exact evidence that produced it, and that evidence can be re-opened and re-verified. Second, **accountability**: if a conclusion later turns out to be wrong, you can audit exactly what the agent saw, when, and how it reached its conclusion. This is the difference between "the AI said so" and "here is the evidence chain that proves what the AI saw."

In incident response, where post-mortems and regulatory scrutiny are common, this audit trail is not a nice-to-have. It is the difference between a tool you can defend and a tool you cannot.

## Local-First and Egress Opt-In: Keeping Sensitive Data on the Host

Operational databases contain sensitive data — customer records, financial information, internal identifiers. Sending that data to a third-party API is often a non-starter for security and compliance reasons.

OpsGraph is local-first by default. It runs investigations with a deterministic replay provider by default, and supports Ollama or vLLM through an OpenAI-compatible adapter for fully local inference. This means the schema, the query data, and the evidence can all stay on the host. Nothing leaves the machine unless the operator explicitly opts in.

Anthropic is supported only after an explicit egress opt-in. This is a deliberate design choice: the operator must consciously decide to allow data to leave the host, rather than having it happen silently by default. For teams that run sensitive workloads, this local-first posture is often the single most important feature — it makes the tool usable in environments where cloud-based AI agents would be rejected outright.

## Skills and Tools: Versioned Declarative Skills That Tighten, Never Weaken, Policy

OpsGraph extends its safety model with customizable declarative skills. A skill is a versioned definition that bundles a set of tools with per-tool bounds. The critical property is that skills can **tighten, never weaken**, server policy.

This is an important guarantee. An operator can define a skill that restricts the agent to a specific investigation playbook — say, "investigate connection pool exhaustion" — with tight bounds on which tables it may touch and how many queries it may run. What a skill cannot do is grant the agent more access than the server policy allows. The server policy is the ceiling; skills can only lower it.

This makes OpsGraph safe to extend. Teams can encode their own investigation playbooks as versioned skills, share them, and iterate on them, all without creating a path for a skill to escalate privileges. Versioning means changes are tracked and reversible, so a bad skill definition can be identified and rolled back.

## The Alpha Boundary and Threat Model: What OpsGraph Deliberately Does Not Do

Discipline about scope is a feature, not a limitation. OpsGraph is a public validation alpha, and its threat model is explicit about what it does not do:

- **No remediation.** OpsGraph investigates; it does not fix. It will not apply schema changes, restart services, or modify data.
- **No writes.** The read-only design means it cannot alter the database, period.
- **No dump restore.** It will not restore backups or load data dumps.
- **No executable plug-ins.** Skills are declarative and bounded; they cannot run arbitrary code.

This scope discipline is what makes the tool safe enough to validate in the first place. By refusing to do the dangerous things, OpsGraph keeps its attack surface small and its guarantees strong. The threat model treats all input as untrusted and requires stored prompt injection to remain inert data — a high bar that the read-only, AST-validated, bounded design is built to meet.

It is also worth being explicit about the boundary: OpsGraph is a validation alpha, not approved for production or customer data. Teams should treat it as a tool to evaluate the evidence-first approach, not as a drop-in production system.

## OpsGraph vs the Agentic PostgreSQL Landscape (pg_sage, PlayBooks, Agentic Coding)

OpsGraph is not the only agentic PostgreSQL tool, but it occupies a distinct niche. The table below compares it against the main alternatives.

| Tool | Primary Focus | Access Model | Best For |
|------|--------------|--------------|----------|
| **OpsGraph** | Evidence-first incident investigation | Read-only, AST-validated, bounded, audited | Root-cause analysis with reproducible, auditable conclusions |
| **pg_sage** | Agentic PostgreSQL DBA | Action-oriented (monitor, optimize) | Performance tuning, monitoring, SRE workflows |
| **Doctor Droid PlayBooks** | General observability investigation | Connects to 15+ tools, runs commands | Broad multi-tool incident investigation |
| **Pg-Aiguide / agentic coding** | Agentic SQL and schema code generation | Generates and manages code | Writing and managing PostgreSQL code |

**pg_sage** is an Agentic PostgreSQL DBA written in Go that monitors, analyzes, and optimizes PostgreSQL 14-18 databases with LLM-powered actions. It supports AlloyDB, Aurora, Cloud SQL, RDS, and self-hosted deployments, and integrates with Prometheus for observability. Its focus is action: optimize, monitor, fix. OpsGraph's focus is investigation: understand, with evidence, without touching anything.

**Doctor Droid PlayBooks** are Jupyter-Notebook-style on-call investigation documents that automate production issue investigation. The Doctor Droid bot connects to 15+ observability tools and servers, running commands and fetching data on alert. PlayBooks is a general observability investigation framework spanning logs, metrics, database queries, remote commands, container data, and custom API calls. OpsGraph is narrowly scoped to read-only PostgreSQL with a tamper-evident audit chain.

**Agentic coding tools** like Pg-Aiguide focus on using AI agents to write and manage PostgreSQL code — schema changes, queries, migrations. That is a code-generation workflow, not an incident-investigation workflow.

The practical takeaway: if you need to *fix* a database, look at pg_sage. If you need to investigate across your whole stack, look at PlayBooks. If you need to *understand* a PostgreSQL incident with evidence you can defend, OpsGraph is the tool designed for exactly that.

## Getting Started: Running an Evidence-First Investigation in Under Five Minutes

OpsGraph's alpha success criteria promise that a sample investigation completes in under five minutes. Getting started follows a clear path:

1. **Deploy the self-hosted workspace** on a host that can reach the target PostgreSQL instance.
2. **Create a dedicated read-only role** in PostgreSQL and grant it access to the schema you want to investigate. This is the approved schema OpsGraph will discover.
3. **Configure the provider.** For local-first operation, use the deterministic replay provider or an Ollama/vLLM instance via the OpenAI-compatible adapter. Only opt in to egress (e.g., Anthropic) if you explicitly accept data leaving the host.
4. **Define or select a skill** that matches your investigation playbook, with per-tool bounds that tighten server policy.
5. **Run the investigation.** The agent will issue at most three AST-validated, bounded SELECT queries inside a read-only transaction, gather evidence, and produce a conclusion with an audit chain.

The five-minute target is achievable because the tool is deliberately constrained: a focused agent with a hard query budget and a clear schema can reach a defensible conclusion quickly. The fifteen-minute schema review target reflects the same discipline — a bounded, structured review beats an open-ended exploration.

## When to Trust an Evidence-First Investigation Tool (and When Not To)

An evidence-first tool earns trust by making its reasoning auditable, but it is not a substitute for judgment. Here is a practical framework.

**Trust it when:**
- You need a reproducible, auditable record of what the agent saw and concluded.
- The investigation is read-only and the blast radius is bounded.
- You can verify the evidence chain against the source-owned table bindings.
- You are running locally and sensitive data stays on the host.

**Be cautious when:**
- You need remediation, not just investigation — OpsGraph will not fix anything.
- The investigation requires write access or schema changes.
- You are handling production or customer data — this is a validation alpha, not production-approved.
- You expect the model to act on untrusted database content without validation — the threat model requires stored prompt injection to remain inert.

The bottom line: evidence-first design does not make an AI infallible. It makes the AI's work *verifiable*. That is the real value. When a conclusion can be traced to exact, bounded, read-only evidence with a tamper-evident audit chain, you can decide for yourself whether to trust it — and you can defend that decision to anyone else.

## FAQ

**What is an agentic PostgreSQL investigation?**
An agentic PostgreSQL investigation is an AI-driven workflow that explores a PostgreSQL database to answer operational questions, such as finding the root cause of an incident. OpsGraph makes it evidence-first by constraining the agent to read-only, AST-validated, bounded queries and recording a tamper-evident audit chain.

**How does OpsGraph keep an AI from writing to the database?**
OpsGraph uses a dedicated read-only PostgreSQL role, validates every SELECT against the PostgreSQL AST, enforces table scope and row/time bounds, caps each investigation at three queries, and runs queries inside a read-only transaction. Any unsafe or out-of-bounds query fails closed.

**What makes OpsGraph "evidence-first" rather than just AI-assisted?**
Evidence coverage is derived from source-owned table bindings, not from the model's own claims. A conclusion is only as strong as the evidence the audit trail proves was gathered against the authoritative tables — so the model cannot self-assert that its evidence is sufficient.

**Is OpsGraph safe to use in production?**
No. OpsGraph is a public validation alpha released under Apache-2.0 and is not approved for production or customer data. It is designed to validate the evidence-first approach and should be evaluated accordingly.

**How does OpsGraph compare to pg_sage or Doctor Droid PlayBooks?**
OpsGraph is narrowly scoped to read-only, audited PostgreSQL investigation. pg_sage is an action-oriented Agentic PostgreSQL DBA for monitoring and optimization, and Doctor Droid PlayBooks is a general observability investigation framework spanning 15+ tools. Each serves a different workflow.
