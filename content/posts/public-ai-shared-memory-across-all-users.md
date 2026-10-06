---
title: "Shared AI Agent Memory Across All Users: The Real Implications of a Public AI Memory Pool"
date: 2026-10-01T06:04:54+00:00
tags:
  - shared AI agent memory
  - public AI shared memory
  - cross-user memory sharing
  - AI agent memory privacy
  - unintentional cross-user contamination
  - shared memory bank architecture
  - memory poisoning OWASP ASI06
  - multi-tenant agent memory
  - per-user vs shared memory isolation
  - attributed vs de-attributed memory
  - agent memory provenance audit
  - GDPR erasure AI memory embeddings
  - memory leakage benchmark
  - AI memory governance framework
  - shared context privacy floor
  - cross-user preference interference
description: "Raw shared AI agent memory contaminates 57-71% of cross-user answers with no attacker present. The architecture, security and erasure rules that survive."
draft: false
cover:
  image: "/images/public-ai-shared-memory-across-all-users.png"
  alt: "Shared AI Agent Memory Across All Users: The Real Implications of a Public AI Memory Pool"
  relative: false
schema: "schema-public-ai-shared-memory-across-all-users"
---

Sharing memory across every user of a public AI is three different architectures wearing one name: a private per-user layer, an attributed shared layer, and a de-attributed wisdom layer. Raw pooling without those boundaries produces 57-71% cross-user contamination from benign interactions alone, and 80-99% memory-poisoning success under attack.

That is the short answer, and it is deliberately unflattering to the idea. The longer answer is more useful: cross-user sharing genuinely works where local experience is scarce, the failure mode nobody budgets for is not forgetting but confidently remembering somebody else's local convention, and the security model changes so completely that standard prompt-injection controls do not catch it. This guide walks through what the 2026 research actually measured, what it costs, and the design rules that hold up when one memory pool serves an entire user base.

## What Does "Shared Memory Across All Users" Actually Mean?

The phrase hides three architectures that behave nothing alike under load.

The first is the **private per-user layer** — facts bound to one account and unreachable by anyone else. Every system has this; it is the baseline. The second is **attributed shared memory**, where a fact is shared *and* carries its origin: you can see that the convention came from another user, another team, or another agent. The third is **de-attributed generalisation**, sometimes called the "wisdom" layer — aggregate patterns with the identity stripped out, so the system improves for everyone without exposing anyone.

The AIM framework ([arXiv 2609.12320](https://arxiv.org/abs/2609.12320)) makes this the central design decision: it classifies every memory item as PRIVATE or PUBLIC and enforces the boundary at the **index** level rather than the prompt level. Private memories are retrievable only by their owner. That matters because prompt-level scoping ("do not mention Jane's record") is an instruction the model can be talked out of, while index-level scoping is a retrieval path that simply does not exist for the wrong caller.

The commercial version of the same idea, documented by the shared-memory product [Sonzai](https://sonz.ai/docs/en/shared-memory), splits it two ways: **attributed facts** with visible names and identities, which are opt-in and off by default, and a default-on **wisdom layer** of de-attributed cross-user generalisation. The tiering is not decoration. The failures described later in this post almost all trace back to collapsing the attributed and de-attributed layers into one pool — sharing a preference without sharing whose preference it is.

| Tier | What it stores | Who can retrieve it | Failure when collapsed into one pool |
|---|---|---|---|
| Private per-user | Personal facts, preferences, sensitive context | Only the owning user | Cross-user leakage; erasure residue |
| Attributed shared | Shared facts with visible provenance | Authorised users, with disclosure | Preferences silently transferred as if they were the user's own |
| De-attributed generalisation | Aggregate patterns, "how to act" lessons | All users | Contamination without traceability; no way to unpick a bad entry |

ShareMem ([arXiv 2609.32511](https://arxiv.org/abs/2609.32511)) draws the cleanest technical version of this line. In its architecture, shared experiences record **how to act** and **which preferences to consult**, while the receiving user's own memory supplies their concrete **values**. The sharing never overrides the local user's preference set — a user-bound channel keeps preference retrieval separate from the shared experience pool, so a cross-user memory cannot silently become the user's preference.

That single sentence is the whole design brief. If you take nothing else from this article: share procedures, not preferences.

## Why Is a Shared Memory Pool So Attractive in the First Place?

Because for a new user, local memory is empty and shared memory is not. That is the cold-start problem, and it is where cross-user sharing earns its keep.

ShareMem was evaluated on three workloads — web navigation (Mind2Web), online personalised interaction (VitaBench 2.0) and multi-session coding (MemoryCode) — across four backbone models. It improved step success, average task success and dialogue-macro coding scores over matched user-local memory in **all four** backbones. The ablations are the interesting part: a two-stage consolidation that refines experience locally *before* accepted edits enter the shared pool wins for smaller shared pools, with lower induction-token usage and better downstream performance. And sharing helps **most when relevant local experience is scarce**.

That asymmetry defines the honest case for the feature. A public AI with a shared pool is not uniformly better or worse than a per-user one. It is better for users with thin history and worse for users with deep history, because the population's habits crowd out individual ones. ShareMem's own stated limitation is exactly this: "source quality and cross-user preference interference limit useful transfer." The same mechanism that lifts a first-week user can degrade a power user, and both effects are produced by the same pool.

Note also what ShareMem is *not*: a single undifferentiated store. Scope-first retrieval selects local and shared entries under one common entry budget, so shared content competes with local content rather than automatically outranking it. If your architecture retrieves shared memories first and hopes the local ones show up, you have built the interference problem on purpose.

## What Is Unintentional Cross-User Contamination?

This is the failure mode that a "public AI shared across all users" creates by default, and it is the most under-budgeted risk in the category. The paper is titled literally that — [*No Attacker Needed: Unintentional Cross-User Contamination in Shared-State LLM Agents*](https://arxiv.org/html/2604.01350v1) (USC / MSU / Northwestern).

The mechanism: a **locally valid artifact** — a local interpretation rule, an aggregation or formatting choice, a task-specific workflow decision — persists in shared state and is later reapplied as if it were generally valid. A user who asked for dates in DD/MM/YYYY leaves that rule behind; the next user's dates come back wrong. A user who wanted percentages rounded to whole numbers gets their convention inherited by everyone. A workflow decision made for one dataset is applied to a structurally different dataset.

Under raw shared state, benign interactions alone produced contamination rates of **57-71%**. No adversary, no prompt injection, no poisoned document — just normal use by other people.

The research names three contamination types:

| Type | Mechanism | Typical example | How it presents |
|---|---|---|---|
| Semantic (SC) | An interpretation rule is inherited as a general truth | Domain-specific wording assumed to hold elsewhere | Plausible but wrong answer |
| Transformation (TC) | An aggregation or formatting choice is reused | Rounding, date formats, unit conventions | Correct logic, wrong presentation |
| Procedural (PC) | A workflow or tool-use decision is replayed | Tool sequence tuned for one task shape | Extra or missing steps |

Two shared-state mechanisms were tested: explicit long-term memory reuse (EHRAgent with shared memory) and persistent collaborative context (MURMUR). The uncomfortable finding is that **write-time sanitization** (Sanitized Shared Interaction, SSI) is effective when shared state is conversational, but leaves substantial residual risk when shared state includes **executable artifacts** — and in that case failures surface as **silent wrong answers rather than errors**. The conclusion is blunt: shared-state agents need artifact-level defences, not just text-level sanitization.

For a public AI this reframes the whole quality conversation. A contamination bug does not page anyone. It produces a confident, well-formatted, wrong answer, and the second user has no way to know the first user caused it.

## How Does the Security Model Change? OWASP ASI06 and Shared Context as an Attack Surface

Without memory, an attacker has to win in a single prompt. With memory, they can stage an attack over time and act when "defenses are often lower and forensics are harder" — the framing from [Microsoft Security's June 2026 guidance on AI memory](https://www.microsoft.com/en-us/security/blog/2026/06/22/guarding-ai-memory/). The worked scenario there is worth reading in full: hidden instructions in a *shared document* plant a dormant directive; days later, an unrelated conversation triggers it, and the assistant writes attacker-shaped content into memory. That is delayed tool execution, not immediate prompt injection.

OWASP formalised this as **ASI06: Memory and Context Poisoning** in the 2026 Top 10 for Agentic Applications ([explainer](https://vectorize.io/articles/owasp-asi06)). ASI06 covers adversarial content written into persistent memory — RAG stores, vector databases, conversation history, and explicitly **shared context** — so the agent acts on it in future sessions. Three structural properties define it:

- **Persistence.** The payload survives sessions, restarts, and sometimes redeployments.
- **Temporal decoupling.** It is planted today and triggered weeks later.
- **Privileged-input vector.** Anything that can write memory can override instructions or exfiltrate data.

The reason ASI06 is a separate category from prompt injection (LLM01) is that LLM01's controls reset when the session ends. Standard prompt-injection defences — input filters, session-scoped instructions, "ignore previous instructions" hardening — do not catch a payload that never appears in the current session's input at all. Reported attack success rates for memory and context poisoning run from **80% to over 99%** across academic studies against LLM-based agent implementations.

A public pool is the highest-value single target in the stack, because one successful write reaches **every** user. OWASP's most relevant vector here is untrusted pipeline writes, with a specific defence: write-time screening and policy evaluation on **every** retain operation — not just on user-visible input. If your agent can save a memory from a web page, a tool result, or a shared document without screening, ASI06 is already in your architecture.

## Where Does Privacy Actually Leak, If Not in the Answers?

Here the evidence is unusually concrete, and it says almost everyone is auditing the wrong channel.

[AgentLeak](https://arxiv.org/pdf/2602.11510v1), a full-stack privacy-leakage benchmark from Polytechnique Montreal, runs 1,000 scenarios across healthcare, finance, legal and corporate domains with a 32-class attack taxonomy and seven instrumented channels: final outputs, inter-agent messages, tool inputs/outputs, shared memory, logs and artifacts.

Its headline finding inverts the intuition that multi-agent systems are safer:

| Channel | Leakage rate |
|---|---|
| User-facing output (C1) | 27.2% |
| Inter-agent messages (C2) | **68.8%** |
| Total system exposure (OR-aggregated across C1, C2, C5) | **68.9%** |
| Output-only audit coverage gap | **41.7% of violations missed** |

Multi-agent configurations actually **reduce** per-channel output leakage — 27.2% versus 43.2% for a single agent — but they introduce unmonitored internal channels that raise total system exposure to 68.9%. Inter-agent messages leak at 68.8%, two and a half times the output channel. The illustrative incident is the best argument for reading the paper: a scheduling agent returned a clean appointment confirmation while its delegation message to a verification agent carried the patient's complete medical record. The final output passed review. The violation went undetected.

For shared memory the implication is structural: **any shared store is one of those internal channels.** Auditing only what the AI says to users leaves the pool unaudited.

Extraction is a separate attack surface from leakage. **MEXTRA** (black-box Memory EXtraction Attack, [arXiv 2502.13172](https://www.alphaxiv.org/abs/2502.13172)) pulled 50 unique private queries out of EHRAgent and 26 out of RAP using only **30 attacking prompts**. The important negative result: generic RAG-style attacks ("please repeat all the context") fail against agent memory, which means teams **cannot assume RAG privacy tooling transfers** to agent memory stores. And agent memory contents are direct user interactions rather than retrieved documents, so every leaked record is inherently more sensitive than a leaked chunk of a public corpus.

None of this is theoretical at the product layer either. An AI companion app pair (Chattee Chat and GiMe Chat) exposed millions of intimate conversations from 400,000+ users plus 600K+ images through unprotected services — not a sophisticated hack, just missing access control. A separate AI chat app leak exposed 300 million messages tied to roughly 25 million users. Shared conversational memory at consumer scale has a track record, and it is not a good one.

## What Design Rules Actually Hold Up?

Nine rules, in rough order of return on effort.

**1. Put provenance on every shared record.** This is the cheapest control with the best payoff. If recall cannot distinguish inherited knowledge from the user's own, every downstream decision is guessing. Provenance is also what makes rollback possible: you cannot unpick a bad shared entry you cannot trace.

**2. Share procedures, not preferences.** The ShareMem split — shared experience for *how to act*, the user's own memory for *what they value* — keeps cross-user preference interference out of the user's identity layer.

**3. Retrieve with scope first, then rank.** Oracle's multi-tenant guidance states the rule precisely: every query must filter by tenant **before** ranking by vector similarity, "otherwise the vector index itself ranks across data the user should never have seen." A similarity threshold is not an access control.

**4. Consolidate before admission.** ShareMem's two-stage consolidation refines experience locally before accepted edits enter the shared pool, and its ablation says this wins for smaller pools. Curate on the way in; it is far cheaper than curating a poisoned pool afterwards.

**5. Draw an explicit bank boundary.** The practitioner guide from [Hindsight](https://hindsight.vectorize.io/guides/2026/04/21/guide-building-multi-agent-systems-with-shared-memory) frames the classic failure as a binary: most systems either **over-share** (one noisy pool, messy recall) or **under-share** (silos, nothing compounds). The fix is deciding the boundary level deliberately — user, project, team, environment, tool/agent role.

**6. Screen at write time, on every retain operation.** This is the ASI06 vector-1 defence, and it must cover non-user writes: tool results, scraped pages, shared documents.

**7. Cap size to force pruning.** The [one-repository, one-shared-brain](https://mkadri85.github.io/blog/shared-ai-memory) pattern is the sharpest practitioner account of memory hygiene: `.ai/STATE.md` is rewritten at the end of every session, **never appended**, capped at roughly 100 lines; ADRs are immutable once accepted and superseded rather than edited; topic files stay under 150 lines. Its warning is the line worth quoting in a design review: "Shared AI memory rarely fails by forgetting. It fails by confidently remembering something that is no longer true."

**8. Review memory changes like code.** The same guide puts memory edits on the code PR, "because a wrong memory entry is a bug that infects every future session of every developer." For a public AI, the blast radius is larger than a team.

**9. Make deletion admin-only and hard.** Sonzai's tiering gives agents the ability to tombstone but reserves hard delete for admins — so a misattributed fact is reversible. An agent that can permanently delete shared memory is a liability; an agent that can only mark it is not.

On which candidates belong in a shared pool at all, the practitioner consensus is consistent:

| Share these | Keep these private |
|---|---|
| Architecture decisions | Noisy intermediate reasoning |
| Accepted conventions | One-off drafts |
| Recurring failure modes | Sensitive personal details outside the intended boundary |
| Deployment lessons, milestones | Agent-local scratch work |
| Preferences all relevant agents must honour | Anything derivable from code or git history |

The recommended starter pattern is conservative for a reason: bank per project for team workflows, bank per **user** for assistants, and avoid team-wide sharing until it is proven necessary.

## Is Multi-Tenancy the Same Problem at a Different Scale?

Yes, and the database world already solved the shape of it — which is why agent teams should copy the solution rather than reinvent it.

[Oracle's guidance on multi-tenant agent memory schemas](https://blogs.oracle.com/developers/from-prompt-to-persistence-part-1-designing-multi-tenant-agent-memory-schemas-for-saas) is unambiguous: every durable memory record needs a tenant boundary, and isolation should be enforced **by the database** via row-level security rather than application code — "The application can't be trusted to remember to filter on its own." Four rules follow from that:

- **Row-level security, not WHERE clauses in app code.** One missed filter is one cross-tenant read.
- **Tenant filter before similarity ranking**, as above.
- **Type the memory, don't use one generic table.** Guidelines, persona memory, entity facts, conversations, summaries, workflows, toolbox settings and knowledge-base content have different access patterns and lifecycles; one table means one retention policy that is wrong for most of them.
- **Cascade deletion across every derived projection**, plus per-tenant key rotation for encryption at rest.

The classic failure is retrofitting tenancy. Retrieval queries, deletion sweeps and vector ranking all have to be rewritten, which is why tenancy belongs on every record from the first row.

Snowflake's [Cortex Agents multi-tenancy docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-multi-tenancy) add the runtime half: immutable session attributes set in the agent:run variables block, paired with row access policies on the tables. The attributes are **immutable for the session** — they cannot be modified by generated SQL, code execution or tool invocation — which is precisely what stops the agent from escaping its tenant context mid-run. Note the shared-responsibility line: the platform supplies the attributes and the policies; correctness of the boundary is yours.

| Isolation pattern | Boundary | Best for | Main risk |
|---|---|---|---|
| Per-user | One user | Personal assistants | Cold start; nothing compounds |
| Per-project | One repo/workspace | Team workflows | Duplicated effort across projects |
| Per-team | One team | Shared conventions | Cross-team leakage; stale central pool |
| Per-user-per-project | Compound key | Consultants, multi-client work | Schema complexity |
| Hybrid shared + local | Split tiers | Most production assistants | Requires provenance and scope-first retrieval |

For a public AI "shared across all users," the single shared pool *is* the all-tenants case: the blast radius of one bug is the entire tenant list.

## How Does GDPR Erasure Collide With Derived Memory?

This is the compliance landmine, and it is not solved by deleting the row.

Vector embeddings, graph nodes and consolidated memories are each **new copies** of the personal data, not references to it. Deleting the source record while leaving the derived projections in place leaves data residue — Oracle flags cascade deletion as a hard requirement, and the same gap appears independently in practitioner analyses of AI-memory governance. The practical consequence: a valid erasure request can be honoured at the database layer and still leave the user's information recoverable through the vector index, the knowledge graph, or a consolidated summary that was written before the deletion.

[MemRiskBench](https://arxiv.org/pdf/2609.14976) adds a failure mode that compliance reviews rarely test for: **revoked-memory reuse** — "a memory that was deleted for one user reappearing in another user's context." In a shared pool, this is not a bug in erasure; it is a bug in *reuse*. The revoked fact may persist in a shared entry, a cached retrieval result, or another user's consolidated summary, and reappear after the deletion was marked complete.

Three controls follow. First, treat every derived projection as in-scope for deletion, with a sweep that cascades through embeddings, graph nodes and summaries. Second, version shared entries so a revoked fact can be superseded and its dependents identified rather than silently outliving the source. Third, log disclosure and deletion as first-class audit events — if you cannot show which users retrieved a fact before it was revoked, you cannot answer the follow-up questions that arrive after an incident.

## Why Are Average Benchmark Scores Not Safety Evidence?

Because the aggregate hides exactly the failures that matter in a shared pool. MemRiskBench's five-category taxonomy for long-horizon agent memory is stale facts, conflicting updates, cross-user leakage, revoked-memory reuse and constraint decay. The number that should stop any go-live review is this: a headline score of **78% average task success** can sit alongside a **4% cross-scope leakage rate** and a **25% constraint-decay rate**.

| Risk category | What it looks like | Why averages hide it |
|---|---|---|
| Stale facts | Outdated value retrieved as current | Averages rarely weight recency correctly |
| Conflicting updates | Two contradictory memories both retrieved | Manifests as inconsistency, not failure |
| Cross-user leakage | Another user's data in this user's context | Low base rate, catastrophic impact |
| Revoked-memory reuse | Deleted memory resurfaces elsewhere | Invisible without per-user tracing |
| Constraint decay | Instructions progressively ignored over a long horizon | Only appears in long episodes |

MemRiskBench itself is a 120-episode scripted benchmark with full trace logging and deterministic checks — no LLM-as-judge on the pass/fail path. That design choice is the point: on a shared memory pool, **per-(model, risk) pass rates are the only defensible metric**, and aggregate task success is a marketing number.

AIM's results make the same argument from a different angle. It reports 96.0% **visibility classification** accuracy — knowing what is public is easy — against only **58.8% strict operation accuracy** (70.5% state-aware) across three independent runs on its MUMBench multi-user benchmark. The 37-point gap between "we know what is public" and "we act correctly on it" is the honest headline for any public shared-memory system. Classifying privacy is the part everyone ships; operating correctly under it is the part that is still hard.

## What Is a Practical Rollout Sequence for a Public Shared Memory Pool?

Ship it in stages, and make each stage observable before opening the next.

| Stage | What ships | Gate to pass before proceeding |
|---|---|---|
| 1 | Private per-user memory only | Erasure cascade verified across every derived projection |
| 2 | Attributed shared memory, opt-in, off by default | Provenance on every record; scope-first retrieval proven by test |
| 3 | De-attributed generalisation layer, disclosed in settings | Contamination rate on a held-out user pair set below your threshold |
| 4 | Tenant boundary hardening | Row-level security enforced by the database; tenant filter precedes ranking |
| 5 | Write-time screening on every retain operation | ASI06 red-team: poisoned write through a tool result is blocked |
| 6 | Admin-only hard delete + disclosure audit | Revoked-memory reuse test passes |
| 7 | Staged exposure to the wider user base | Per-risk release gates, not an average |

Two organisational facts should shape the timing. First, responsible-AI maturity is low: McKinsey's 2026 AI Trust Maturity Survey (~500 organisations, fielded Dec 2025–Jan 2026) put average maturity at **2.3 out of 5**, up from 2.0, with only about **30%** of organisations reaching level 3+ in strategy, governance and agentic AI controls. Second, appetite for unproven agentic projects is falling: Gartner has predicted that **over 40% of agentic AI projects will be cancelled by end-2027** on escalating cost, unclear business value and inadequate risk controls.

The market context argues for the staged path rather than against the feature. The average organisation in Salesforce's 2026 Agentic Enterprise Index cohort runs **13 AI agents in production**, up from 5 in February 2025 — roughly 3x in 14 months — with provisioning-to-first-agent down 53% to about two days. Agent fleets are arriving faster than memory governance is. That gap is where cross-user contamination becomes a production incident.

It is also worth noting what the largest consumer AI has *not* done. ChatGPT's memory lineage — saved memories (April 2024), Dreaming V0 chat-history synthesis (April 2025), and Dreaming V3 (June 4, 2026) — remains **per-account**; there is no cross-user memory pool. Its closest shipped analogue to a shared-context surface, group chats in ChatGPT, piloted in November 2025 and expanded on November 20, 2025, was **wound down from July 9, 2026** rather than extended. The most capable consumer deployment of AI memory chose to narrow the sharing surface, not widen it. That is not proof the architecture is wrong; it is evidence that the operational cost is real enough that the biggest player declined to pay it.

## When Is Shared Memory the Wrong Answer?

Four cases where a public pool should not be the design:

- **Sensitive personal context.** Health, legal, financial and relationship facts. AgentLeak's inter-agent channel number (68.8%) is the reason: even when the user-facing answer is clean, the shared store is an internal channel that leaks. There is no attribution tier that makes this safe — private is the only correct scope.
- **Executable-artifact state.** The contamination research is explicit that write-time sanitization leaves substantial residual risk when shared state includes executable artifacts, and the failures present as **silent wrong answers**. If your shared memory stores artefacts that get executed, text-level defences are not sufficient.
- **High-experience users.** Cross-user preference interference is a measured effect, and it degrades precisely the users with the deepest local history. For power users, a shared pool is a tax.
- **Surfaces with no audit trail.** If you cannot attribute a memory, cannot sweep its derivations and cannot show who retrieved it, you cannot operate the pool safely. Build the audit path first or do not build the pool.

The design question is never "shared or private." It is what is shared, with whom, with what attribution, and what happens when it is wrong. ShareMem's own limitation — source quality and cross-user preference interference — is the honest summary of the trade: sharing pays where local experience is scarce and charges where it is deep, and the only way to get one without the other is to keep the tiers separate, put provenance on everything, and gate the whole thing on per-risk evidence rather than an average.

## FAQ

### What is shared AI agent memory?

Shared AI agent memory is a memory store whose contents are retrievable across more than one user or agent, rather than being scoped to a single account. It is best understood as three tiers: a private per-user layer, an attributed shared layer where the origin of a fact is visible, and a de-attributed generalisation layer that carries aggregate patterns without identity. Most architectural failures come from collapsing the attributed and de-attributed tiers into a single pool.

### Is sharing memory across all users safe?

Not with a raw shared pool. Under raw shared state, benign interactions alone produce cross-user contamination rates of 57-71% ([arXiv 2604.01350](https://arxiv.org/html/2604.01350v1)) — no attacker required. It becomes defensible when it is built as separate tiers with provenance on every record, scope-first retrieval, write-time screening on every retain operation, and per-risk release gates. The evidence says sharing is safe *conditionally*; it does not say it is safe by default.

### How much does unintentional cross-user contamination actually cost?

It costs correctness rather than uptime, which is why it is under-budgeted. A locally valid rule — a date format, a rounding convention, a workflow choice — persists in shared state and gets reapplied as if it were generally valid. When shared state includes executable artifacts, write-time sanitization leaves substantial residual risk and the failure presents as a **silent wrong answer** rather than an error. Nothing pages, and the affected user has no way to know another user caused it.

### What is OWASP ASI06 and does it apply to shared memory?

ASI06 is Memory and Context Poisoning in OWASP's 2026 Top 10 for Agentic Applications, and it explicitly names shared context as an attack surface. It is separate from prompt injection (LLM01) because its properties are different: persistence across sessions and restarts, temporal decoupling (planted today, triggered weeks later), and privileged-input writes (anything that can write memory can override instructions). Reported attack success rates run from 80% to over 99%, and standard prompt-injection controls do not catch it because LLM01's controls reset when the session ends.

### How do you delete a user's data from a shared memory pool?

You cannot delete only the source row. Vector embeddings, graph nodes and consolidated summaries are each new copies of the personal data, so erasure has to cascade through every derived projection. You also have to test for revoked-memory reuse — a deleted memory reappearing in another user's context — which MemRiskBench treats as a first-class risk. The practical minimum is a cascade sweep, versioned shared entries that can be superseded, and audit logging of disclosure and deletion so you can answer who retrieved a fact before it was revoked.
