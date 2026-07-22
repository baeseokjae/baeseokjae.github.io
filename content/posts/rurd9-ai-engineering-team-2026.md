---
title: "RUDR9 Review: One Command AI Engineering Team with Kanban Coordination"
date: 2026-07-22T01:02:15+00:00
tags:
  - RUDR9
  - AI Engineering Team
  - Kanban Coordination
  - Multi-Agent Systems
  - Hermes Agent
  - AI Development
  - Software Engineering
description: "RUDR9 transforms Hermes Agent into a 9-role AI engineering organization with one command. This review covers architecture, bugs, performance, and whether it's production-ready."
draft: false
cover:
  image: "/images/rurd9-ai-engineering-team-2026.png"
  alt: "RUDR9 Review: One Command AI Engineering Team with Kanban Coordination"
  relative: false
schema: "schema-rurd9-ai-engineering-team-2026"
---

RUDR9 is an open-source project that transforms Hermes Agent into a 9-role AI engineering organization with a single command. It creates distinct AI agents — CTO, Planner, Architect, VCM, Builder, Security, Performance, and Reviewer — each with isolated profiles, tool permissions, and kanban-coordinated workflows. The project is MIT-licensed, written in Shell script, and has accumulated 40 GitHub stars and 8 forks within its first week of existence as of July 2026.

## What Is RUDR9? — One Command to an AI Engineering Team

RUDR9 is a bold experiment in multi-agent orchestration built on top of Hermes Agent. The core idea is simple: run one installer command, and you get a full AI software engineering organization with nine specialized roles, each operating in its own Hermes profile with isolated configuration, memory, sessions, and skills.

The project was created on July 15, 2026, making it less than one week old at the time of this review. Despite its youth, RUDR9 has already generated substantial self-critique documentation including an Architecture Review, a Claude Code Review, and a Performance Audit — a sign of strong engineering discipline from its creators.

The project lives at [github.com/ardhaecosystem/RUDR9](https://github.com/ardhaecosystem/RUDR9) and is written entirely in Shell script. Its one-command installer promises to turn any Hermes Agent installation into a multi-agent development powerhouse with kanban coordination, DAG dependency tracking, and scope-adaptive ceremony levels.

## The 9-Role Architecture — How It Works

RUDR9 defines nine distinct AI agent roles, each with its own Hermes profile, tool permissions, and responsibilities:

| Role | Tool Access | Primary Responsibility |
|------|-------------|----------------------|
| CTO/Orchestrator | Full access | Decomposes tasks, assigns work, manages kanban board |
| Planner | Read-only | Creates implementation plans with BDD acceptance criteria |
| Architect | Read + write code | Designs system architecture and data flow |
| VCM (Version Control Manager) | Git + write | Manages branches, commits, and pull requests |
| Builder | Write code + terminal | Implements features and fixes bugs |
| Security | Read-only + security tools | Audits code for vulnerabilities |
| Performance | Read-only + profiling tools | Identifies performance bottlenecks |
| Reviewer | Read-only | Reviews pull requests and code quality |

The per-profile tool permission system is the architectural centerpiece. Each role gets exactly the tools it needs and nothing more. A Planner cannot write code. A Security agent cannot push commits. This authority matrix is enforced through Hermes Agent's profile system, where each profile has its own `config.yaml` with toolset restrictions.

### Kanban Coordination via Hermes Dispatcher

RUDR9 leverages Hermes Agent's built-in kanban orchestrator for task management. The configuration uses:

- `auto_decompose=false` — tasks are manually decomposed by the CTO role
- `max_in_progress=3` — limits concurrent work to prevent context overload
- `max_in_progress_per_profile=1` — ensures no single role works on multiple tasks simultaneously

Task linking via `kanban_link` provides DAG dependency graphs and join barriers. This means a Builder task can depend on an Architect task completing first, and the system enforces that ordering automatically.

### Scope-Adaptive Ceremony Levels

One of RUDR9's more pragmatic features is its three-tier ceremony system:

1. **Quick-fix (3 stages):** For small changes — plan, implement, review. Single file, minimal overhead.
2. **Standard (6 stages):** For typical feature work — plan, design, implement, test, review, merge. 2-5 tasks.
3. **Complex (9 stages):** For major features — full 9-role workflow with parallel security and performance audits. 6+ tasks.

This adaptive approach attempts to solve the over-engineering problem that plagues many multi-agent systems. A typo fix should not require a CTO meeting and an architecture review.

## Installation Experience — One-Liner Promise vs Reality

RUDR9 advertises a one-command install, but the reality is more complicated. The `curl | bash` one-liner is currently broken because the assets directory is missing in the piped install path. Users who clone the repository and run the installer locally have better success, but the experience is far from seamless.

The full install process takes approximately 8.5 minutes in its current form. This is dominated by two bottlenecks:

- **Skill scanning (4 minutes):** The ponytail skill is scanned 8 times — once per profile — instead of being seeded once and cloned.
- **MCP probing (4.5 minutes):** The installer probes MCP servers at install time instead of writing configuration directly to `config.yaml`.

The recommended fix, documented in the project's own Performance Audit, is to rewrite the installer's main flow as: `seed_default → create_profiles → reconcile → install_souls → configure_toolsets → install_mcps`. This would reduce install time to under 2 minutes.

## The Good — What RUDR9 Gets Right

Despite its rough edges, RUDR9 has several genuinely good ideas:

**Per-profile tool isolation is the right architectural insight.** Most multi-agent systems give every agent the same capabilities and rely on prompt-level instructions to enforce role boundaries. RUDR9's approach of encoding authority in the profile configuration — where it cannot be bypassed by a clever prompt — is architecturally sound.

**The scope-adaptive ceremony is practical.** Many multi-agent frameworks force the same heavyweight process on every task. RUDR9's three-tier system lets users match ceremony to task complexity, which is essential for real-world adoption.

**Self-critique documentation shows engineering maturity.** The project includes an Architecture Review that is brutally honest about its own shortcomings, a Claude Code Review that found 15 bugs, and a Performance Audit with concrete optimization recommendations. This level of transparency is rare in open-source AI projects.

**Kanban with DAG dependencies is a solid coordination primitive.** The use of Hermes Agent's built-in kanban dispatcher with dependency linking provides a real coordination mechanism, not just a chat-based handoff between agents.

## The Critical Issues — Architecture Review Findings

The project's own Architecture Review identifies several fundamental problems:

### 9 Roles Is "Org-Chart Cosplay"

The review's most damning critique is that nine roles optimize for the wrong scarce resource. In AI agent systems, the scarce resource is context window and reasoning budget — not human availability. Creating nine agents means fragmenting context across nine separate sessions, each with incomplete information about the project.

The review recommends 3-4 roles for a v1 product, which would reduce context fragmentation while still providing meaningful specialization.

### Authority Matrix Is "Prompt-Level Wishful Thinking"

While the per-profile tool enforcement is architecturally sound in theory, the review identifies a critical gap: the guard plugin's profile detection may be broken. The `_get_profile()` function uses `HERMES_HOME` basename to determine which profile an agent is running under, which likely resolves every worker to the "default" profile. If this is true, every role gets the default profile's full tool access, and the entire authority matrix collapses.

### PAUL Mapping Is a "Forced Fit"

RUDR9 claims to follow PAUL (Plan, Act, Update, Learn) workflow principles. However, PAUL's core principle is keeping context in-session — reasoning about a task, acting on it, updating understanding, and learning from the result, all within a single session. RUDR9 fragments this across nine separate agents, each with its own session. The Architecture Review calls this mapping a "forced fit" that contradicts PAUL's design philosophy.

### No Real Orchestration Layer

The review identifies that RUDR9 lacks a proper orchestration layer. The coordination primitive, state store, and failure model are all unspecified. While the kanban dispatcher provides task routing, there is no centralized orchestrator that manages cross-agent state, handles failures gracefully, or makes dependency decisions.

### Role Overlap

Four roles — Checker, Security, Performance, and Reviewer — all review the same pull request from different angles. This creates overlapping effort without clear ownership boundaries. Additionally, there are gaps: no explicit owner for test authorship, no documentation role, and no dependency decision owner.

## The Bugs — Claude Code Review's Top 5 Fixes

The Claude Code Review performed static analysis on the RUDR9 codebase and found 15 bugs ranked by severity. The top five fixes are:

1. **Critical — Guard profile detection bug:** The guard plugin's `_get_profile()` function uses `HERMES_HOME` basename for profile detection, which likely resolves every worker to the "default" profile. This breaks the entire authority enforcement system.

2. **Uninstall never re-enables tools:** The uninstall script does not restore file and terminal access on the default profile, leaving the user's base Hermes installation crippled after removal.

3. **Install overwrites default SOUL.md with no backup:** The installer replaces the default profile's SOUL.md without creating a backup, making it impossible to restore the original configuration.

4. **GitHub MCP uses deprecated server package:** The GitHub MCP integration references a deprecated server package and provides no authentication token, making it non-functional out of the box.

5. **Security and Performance auditors have no diff tool:** The Security and Performance roles have no tool to produce a diff of their findings, making their core workflow unreachable.

## Performance — Why Install Takes 8 Minutes and How to Fix It

The Performance Audit breaks down the 8.5-minute install time into specific bottlenecks:

| Bottleneck | Time | Root Cause | Fix |
|-----------|------|-----------|-----|
| Skill scanning | 4 min | Ponytail scanned 8 times (once per profile) | Seed ponytail into default once, then clone |
| MCP probing | 4.5 min | MCP servers probed at install time | Write MCP config directly to config.yaml |
| Toolset configuration | 15-25s | 13 separate CLI calls | Write toolset restrictions to config.yaml in one pass |

The recommended fix is a rewritten `main()` function that follows a linear pipeline: seed the default profile first, create role profiles from it, reconcile configurations, install SOUL.md files, configure toolsets in bulk, and install MCPs from static configuration. This would reduce total install time to under 2 minutes.

## Who Is RUDR9 For? — Solo Devs, Teams, or Experimenters?

RUDR9 sits in an awkward position between use cases:

**Solo developers** will likely find the 9-role system over-engineered for their needs. A single developer working on a side project does not need a CTO, Architect, and Planner to fix a bug. The scope-adaptive ceremony helps, but the overhead of managing nine profiles for a one-person project is hard to justify.

**Small teams** are the most natural audience. A team of 2-3 developers could benefit from specialized AI agents handling different aspects of the development pipeline — one agent plans, another builds, a third reviews. The kanban coordination provides visibility into what each agent is doing.

**Experimenters and researchers** will find RUDR9 fascinating. It is a genuine attempt to implement organizational theory in AI agent systems, and the self-critique documentation makes it a valuable case study in multi-agent architecture design.

**Production users** should wait. The known bugs — especially the guard profile detection issue that may render the entire authority matrix ineffective — make RUDR9 unsuitable for production use in its current state.

## Verdict — Promising but Not Production-Ready

RUDR9 is a fascinating project that demonstrates both the potential and the pitfalls of multi-agent AI development teams. Its core architectural insight — per-profile tool enforcement — is sound, and the scope-adaptive ceremony is a practical solution to the over-engineering problem.

However, the project is clearly in an early, experimental phase. The critical guard profile detection bug, the broken one-liner installer, the 8.5-minute install time, and the architectural concerns raised in the project's own reviews all point to a system that is not yet production-ready.

The most encouraging sign is the project's culture of self-critique. The Architecture Review, Claude Code Review, and Performance Audit are unusually honest assessments that identify real problems with concrete solutions. If the project's creators address the top five bugs, reduce the role count to 3-4, and implement the performance optimizations, RUDR9 could become a genuinely useful tool for AI-assisted software development.

For now, RUDR9 is best viewed as an ambitious prototype and a valuable learning resource for anyone interested in multi-agent orchestration. Watch this project — it may mature quickly.

## Frequently Asked Questions

### What is RUDR9 and how does it work?

RUDR9 is an open-source Shell script project that transforms Hermes Agent into a 9-role AI engineering organization with a single command. It creates specialized AI agents — CTO, Planner, Architect, VCM, Builder, Security, Performance, and Reviewer — each with isolated Hermes profiles, tool permissions, and kanban-coordinated workflows using DAG dependency tracking.

### Is RUDR9 production-ready?

No. RUDR9 has several critical bugs including a guard profile detection issue that may break the entire authority enforcement system, a broken one-liner installer, and an 8.5-minute install time. The project's own Architecture Review recommends reducing from 9 roles to 3-4 for a v1 product.

### How long does RUDR9 take to install?

The current install process takes approximately 8.5 minutes. This is dominated by skill scanning (4 minutes, ponytail scanned 8 times) and MCP probing (4.5 minutes). The project's Performance Audit recommends optimizations that would reduce this to under 2 minutes.

### What are the main bugs in RUDR9?

The Claude Code Review found 15 bugs. The top five are: critical guard profile detection bug that likely resolves every worker to the "default" profile, uninstall that never re-enables tools on the default profile, install that overwrites SOUL.md without backup, non-functional GitHub MCP integration, and Security/Performance roles with no tool to produce diffs.

### Who should use RUDR9?

Small teams of 2-3 developers are the most natural audience. Solo developers will likely find 9 roles over-engineered. Researchers and experimenters will find it valuable as a case study in multi-agent architecture. Production users should wait until the critical bugs are fixed and the architecture matures.
