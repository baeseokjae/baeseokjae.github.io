---
title: "IBM Bob V2 AI Coding Agent Review 2026: Plan, Agent, Ask Modes and Agentic Architecture"
date: 2026-06-30T00:55:28+00:00
tags: ["IBM Bob", "AI coding agent", "agentic architecture", "AI code review", "enterprise AI"]
description: "Hands-on review of IBM Bob V2 AI coding agent: three-tier architecture, Plan/Agent/Ask modes, pricing, and how it compares to Claude Code and Cursor."
draft: false
cover:
  image: "/images/ibm-bob-v2-review-2026.png"
  alt: "IBM Bob V2 AI Coding Agent Review 2026"
  relative: false
schema: "schema-ibm-bob-v2-review-2026"
---

IBM Bob V2 is an enterprise AI coding agent that reached general availability on June 24, 2026, redefining how development teams approach the full software delivery lifecycle. Built on a three-tier architecture that separates reasoning, infrastructure, and interfaces, Bob V2 consolidates its workflow into three modes — Agent, Plan, and Ask — while introducing background task execution, per-task rollback, and subagent support. With 80,000+ IBM internal developers reporting 45% average productivity gains and pricing starting at $20/user/month, this review breaks down whether Bob V2 delivers on its promise of enterprise-grade agentic development.

## What Is IBM Bob V2?

IBM Bob V2 is an enterprise AI coding agent platform that covers the end-to-end software development lifecycle — from planning and coding through security scanning, testing, and deployment. Launched as a SaaS product in April 2026 and reaching V2 general availability on June 24, 2026, Bob evolved from an internal IBM tool used by 100 developers in June 2025 to a platform serving over 80,000 IBM developers today. Unlike standalone AI coding assistants that focus primarily on code completion, Bob operates as an agentic platform: it plans multi-step workflows, executes tasks in the background, invokes subagents with isolated context, and integrates with existing CI/CD pipelines through BobShell, a CLI that provides full audit trails. The platform uses multi-model orchestration — routing tasks across Claude, Mistral, IBM Granite, and proprietary fine-tuned models based on complexity and cost — rather than relying on a single LLM. Gartner projects 40% of enterprise applications will embed agentic coding tools by end of 2026, and Bob V2's architecture positions it as a contender for that embedded agent role. The takeaway: Bob V2 is not an autocomplete tool — it is an agentic development platform designed for teams that need governance, legacy modernization, and multi-step autonomous workflows.

## What Is the Three-Tier Agentic Architecture of IBM Bob V2?

IBM Bob V2 introduced a fundamental re-architecture splitting the platform into three distinct layers: Agent (reasoning), Harness (infrastructure), and Clients (interfaces). This separation of concerns — announced at V2 GA on June 24, 2026 — is the most significant architectural shift from V1, which bundled reasoning and execution into a monolithic agent. In the V2 model, the Agent layer handles all LLM reasoning, planning, and tool selection but has no direct access to files, networks, or external systems. The Harness layer provides the sandboxed runtime environment: executing tool calls, managing file state, enforcing security policies, and maintaining the audit trail. The Client layer encompasses all user-facing interfaces: VS Code extension, JetBrains plugin, BobShell CLI, and the embeddable API that allows third-party tools to invoke Bob as a sub-agent. This three-tier design means the same Agent reasoning engine can be accessed from any Client without modification, and security policies are enforced at the Harness level regardless of which Client initiated the request. For enterprise teams, this architecture means compliance teams can audit Harness logs without touching Agent prompts, and developers can switch interfaces without losing workflow continuity.

### How Does the Agent Layer Work?

The Agent layer is the reasoning engine responsible for interpreting user intent, decomposing complex requests into actionable plans, selecting the appropriate tools, and generating code or responses. It operates purely at the semantic level — it never directly reads files or executes commands. Instead, it issues abstract tool requests to the Harness, which executes them in a sandboxed environment. The Agent orchestrates multi-model calls, routing simple documentation lookups to lighter models (Granite, Mistral) while routing complex refactoring or legacy transformation tasks to frontier models (Claude). In V2, the Agent also manages subagent spawning: when a task requires parallel exploration, the Agent can request the Harness to launch independent subagents, each with its own isolated context window of up to 270K tokens.

### What Does the Harness Layer Handle?

The Harness is the infrastructure layer that provides the secure execution environment for all tool calls issued by the Agent. It manages file system access, network requests, command execution, and state persistence. The Harness enforces all security policies — role-based access controls, allowed command lists, network restrictions, and human-in-the-loop approval gates. It maintains the full audit trail of every tool call, every file change, and every rollback operation. When a developer invokes rollback, the Harness reconstructs file state from its per-tool-call snapshot history, not from git. The Harness also handles background task lifecycle — it can keep agent sessions alive after a developer closes their editor, sending notifications when tasks complete.

### What Is the Client Layer in IBM Bob V2?

The Client layer contains all user-facing interfaces through which developers interact with Bob. This includes the VS Code extension, JetBrains plugin, BobShell CLI, and the embeddable HTTP API. The guiding philosophy, stated by IBM's Bob team, is that the "best interface is no interface" — Bob V2 is designed to be embedded into existing developer workflows rather than requiring developers to switch to a dedicated chat panel. The API allows third-party tools, CI/CD pipelines, and custom internal platforms to invoke Bob agents programmatically. Because the Client layer is decoupled from the Agent and Harness layers, each interface can be optimized independently — the CLI provides raw agent access for power users, while the IDE extensions offer context-aware inline suggestions and diff views.

## What Are the Three Modes in IBM Bob V2: Plan, Agent, and Ask?

IBM Bob V2 consolidated its workflow modes from five in V1 to three in V2 — Plan, Agent, and Ask — removing the Advanced and Orchestrator modes and folding their capabilities into the core Agent mode. This simplification reflects real usage patterns observed across 80,000 IBM developers: most tasks fell into one of three categories — structured planning before execution, fully autonomous action, or read-only exploration. Each mode changes how the Agent layer interprets user input and what level of autonomy it exhibits, while the same Harness and Client layers operate underneath. The three-mode design makes it clearer for developers to choose the right interaction model without guessing whether they need Advanced or Orchestrator mode. Below is a comparison of the three modes.

| Feature | Plan Mode | Agent Mode | Ask Mode |
|---|---|---|---|
| Autonomy level | Proposes plan, waits for approval | Full autonomous execution | Read-only queries |
| Code modification | After plan approval | Direct file editing | None |
| Tool access | All tools (deferred) | All tools (immediate) | Read tools only |
| Best for | Complex multi-step features | Routine implementations | Codebase exploration |
| Review step | Required before execution | Optional (configurable) | N/A |

### How Does Plan Mode Work?

Plan Mode engages the Agent to produce a structured, step-by-step plan before any code is written. The agent analyzes the request, explores the codebase, identifies affected files, and presents the plan with estimated tool calls and file changes. The developer reviews and approves the plan — or requests modifications — before the Agent proceeds to execute. This mode is designed for complex, high-risk changes like database migrations, cross-service refactoring, or legacy codebase modifications where blind execution could introduce subtle issues. Plan Mode reduces the cognitive load of reviewing a diff after changes are made, because the developer validates intent and approach upfront.

### What Does Agent Mode Do in IBM Bob V2?

Agent Mode gives the Agent full autonomy to plan, execute, and iterate on tasks without pausing for approval at each step. The agent analyzes the request, explores the codebase, makes file edits, runs commands, and loops until the task is complete or it encounters an unresolvable error. This is the default mode for experienced developers working on well-understood tasks: implementing new features from specifications, fixing known bugs with clear reproduction steps, or running automated test creation across multiple files. Agent Mode can still trigger human-in-the-loop gates for high-risk operations based on Harness-level policy configuration.

### When Should You Use Ask Mode?

Ask Mode is a read-only interaction mode where the Agent can explore the codebase and answer questions but cannot modify files or execute commands. It uses the same reasoning engine and multi-model orchestration as the other modes, but the Harness restricts all tool calls to read-only operations: file reads, grep searches, git log queries. Ask Mode is ideal for codebase exploration, understanding unfamiliar code, reviewing diffs from pull requests, or getting architectural explanations. It also serves as a documentation lookup tool — developers can ask "How does our authentication middleware work?" and receive a synthesized answer across multiple files without risking accidental modifications.

## What Are the Key New Features in IBM Bob V2?

IBM Bob V2 introduced four major feature categories that fundamentally change how developers interact with the platform: background task execution with multitasking, per-task per-turn rollback replacing git-based checkpoints, subagents with clean context isolation, and an actor-critic workflow for security-audited code generation. These features are built on the three-tier architecture and are available across all three modes where applicable. For enterprise teams evaluating AI coding tools, these four capabilities represent the most significant functional delta between Bob V2 and competing tools like Claude Code or Cursor — neither of which offer background execution, granular rollback, or subagent isolation at the same level. According to IBM's V2 release announcement, these features were the top-requested capabilities from enterprise customers during the V1 beta, and they directly address the limitations that prevented teams from adopting AI coding agents in compliance-constrained environments. Taken together, they transform Bob from a single-session pair programmer into a persistent, auditable, parallel-processing development platform that teams can integrate into daily workflows without sacrificing security or control.

### How Does Background Task Execution Work?

Background task execution allows Bob to continue processing after the developer closes their editor or starts a new task. When a developer submits a long-running operation — a legacy COBOL-to-Java conversion, a large-scale refactoring, or a comprehensive test suite generation — Bob's Agent layer continues reasoning while the Harness manages the task lifecycle independently. The developer receives a notification when the task completes and can review the diff at their convenience. This is distinct from the "run in background" feature in Cursor or Claude Code, which typically pauses agent activity when the terminal or editor loses focus. Bob V2 can run multiple background tasks concurrently, each managed as an independent agent session, enabling genuine multitasking.

### What Is Rollback and How Is It Different from Git?

Rollback in IBM Bob V2 replaces V1's git-based checkpoint system with direct file-state tracking at the per-tool-call granularity. After every tool call — whether a file edit, command execution, or API request — the Harness snapshots the affected file state before and after the operation. This means rollback can revert a single file edit from three steps ago without affecting intervening changes, something git's commit-based model cannot do cleanly. A developer testing five approaches to a bug fix can roll back any individual attempt without stashing or resetting. Rollback operates independently of git: it does not create commits, does not require commit messages, and does not interfere with the project's version control history. The Harness stores these snapshots in an append-only log that also serves as the audit trail for compliance purposes.

### How Do Subagents Work with Context Isolation?

Subagents in IBM Bob V2 are independent agent instances spawned by the primary Agent to handle parallel or delegated work. Each subagent receives its own isolated context with a dedicated 270K-token window, its own tool-call sandbox, and its own rollback history. The primary agent can delegate subtasks — "Check the database schema in module A while I refactor module B" — and both execute concurrently without context bleed or token limit contention. Subagents complete their work and return results to the primary agent, which integrates the outputs. This architecture enables patterns like parallel code review with three subagents reviewing three modules simultaneously, or multi-file refactoring where each subagent handles one file's transformation independently.

### What Is the Actor-Critic Workflow in IBM Bob V2?

The actor-critic workflow is a built-in security mechanism where Bob V2 generates code through two distinct agent roles. The "actor" agent writes the implementation while a separate "critic" agent reviews the output for security vulnerabilities, logic errors, and compliance violations before the changes are applied. This double-check pattern runs within a single agent session — the critic is spawned as a subagent with access to the actor's proposed diffs and a security rule set. In practice, a developer asking Bob to rewrite a COBOL module to Java gets the generated code automatically scanned for SQL injection risks, buffer overflows, and IBM-specific security standards before the file is modified. This makes Bob V2 the only major AI coding tool with built-in, pre-commit security auditing rather than relying on post-hoc scanning.

## What Enterprise Governance Does IBM Bob V2 Offer?

Enterprise governance is IBM Bob V2's strongest differentiator in the AI coding agent market. Every tool call, file change, and rollback operation is recorded in an append-only audit log maintained by the Harness layer. BobShell CLI provides raw access to these logs for integration with SIEM systems, compliance dashboards, and security information management tools. Role-based access controls let organizations restrict which developers can invoke Agent mode vs. Ask mode, which file paths are writable, and which commands are allowed. Human-in-the-loop approval gates can be configured at the organization level to require manager sign-off before Bob modifies production code, security-sensitive files, or infrastructure configurations. For regulated industries — finance, healthcare, government — Bob V2's audit trail meets the evidentiary requirements that tools like Cursor and Claude Code cannot provide. The actor-critic security workflow adds another governance layer: code generated by Bob is automatically audited for vulnerabilities before it touches the filesystem, closing the window between code generation and security review.

## What Is IBM Bob V2 Pricing?

IBM Bob V2 uses a token-based pricing system called Bobcoins. Each Bobcoin is worth $0.50 USD, and different tasks consume different amounts of Bobcoins based on model usage, context size, and execution time. The base subscription determines how many Bobcoins are included each month, with overage billed at the same rate.

| Plan | Monthly Price | Included Bobcoins | Best For |
|---|---|---|---|
| Free Trial | $0 | 40 Bobcoins ($20 value) | Evaluation and experimentation |
| Pro | $20 | 40 Bobcoins ($20 value) | Individual developers |
| Pro+ | $80 | 160 Bobcoins ($80 value) | Professional teams |
| Ultra | $200 | 500 Bobcoins ($250 value) | Enterprise organizations |

Pricing is competitive with Claude Code Pro ($20/month for individual, usage-based overage) and Cursor Pro ($20/month). The Ultra plan includes priority support and custom model routing policies. Bobcoins expire monthly and do not roll over. For enterprise deployments, Bob also offers custom pricing with dedicated model instances, SSO/SAML integration, and on-premises Harness deployment options.

## IBM Bob V2 vs. Claude Code vs. Cursor vs. GitHub Copilot

Each major AI coding tool targets a different point in the developer productivity space. Below is a direct feature comparison across the four platforms most frequently evaluated together.

| Feature | IBM Bob V2 | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|---|
| Agentic architecture | Three-tier (Agent/Harness/Client) | Single agent model | Agent mode (beta) | Copilot Workspace |
| Work modes | Plan, Agent, Ask | Chat + CLI commands | Chat + Agent + Edit | Chat + Completions |
| Multi-model routing | Claude, Mistral, Granite, proprietary | Claude only | GPT-4o, Claude | GPT-4o, Gemini |
| Legacy modernization | COBOL, JCL, CICS, IMS, RPG, DB2 | Not supported | Not supported | Not supported |
| Background tasks | Yes, multi-task | No | Limited | No |
| Rollback granularity | Per-tool-call | Per-message | Git-based | Git-based |
| Subagents | Yes, isolated context | No | No | No |
| Audit trail | Append-only, SIEM-ready | Terminal history | Not available | Not available |
| Security scanning | Built-in actor-critic | Not built-in | Not built-in | Not built-in |
| Pricing (individual) | $20/mo + usage | $20/mo + overage | $20/mo | $10-39/mo |
| Enterprise pricing | $200/mo (Ultra) + custom | Custom (Team/Enterprise) | Business $40/user/mo | Enterprise $39/user/mo |

### Bob vs. Claude Code

Claude Code is a terminal-native agent from Anthropic, designed for developers who live in the command line. It excels at monorepo work, multi-file edits, and complex refactoring in a single session. Bob V2 differentiates with background execution, subagent parallelism, and enterprise governance. Claude Code has no equivalent of Bob's Plan Mode — it executes immediately unless the user explicitly reviews diffs. For individual developers who prefer terminal workflows and don't need compliance-grade audit trails, Claude Code remains a strong choice. For teams that need auditable AI-assisted development, Bob V2 has the clear advantage.

### Bob vs. Cursor

Cursor is the most polished IDE-focused AI coding assistant, offering inline completions, agent mode, and chat within a VS Code fork. Its agent mode handles multi-file edits well but lacks Bob's three-tier architecture, background task execution, and subagent support. Cursor's primary advantage is its seamless inline completion experience — suggesting code as you type, which Bob does not emphasize. For individual developers and small teams building new projects, Cursor offers a more polished day-to-day experience. For enterprises with legacy codebases, compliance requirements, and multi-step workflow needs, Bob V2 is the more complete platform.

### Bob vs. GitHub Copilot

GitHub Copilot is the most widely adopted AI coding assistant, with over 1.8 million paid subscribers as of early 2026. Its strength is ubiquity — it works across every major editor and platform. Copilot Workspace introduces agentic capabilities, but remains limited compared to Bob's full agentic architecture. Copilot cannot run background tasks, spawn subagents, or provide per-tool-call rollback. For individual developers who want autocomplete everywhere, Copilot is the default choice. For organizations that need a single agentic platform covering planning, coding, testing, security, and deployment with enterprise governance, Bob V2 is positioned as a Copilot alternative rather than a complement.

## Who Should Use IBM Bob V2?

IBM Bob V2 is designed for teams and organizations, not individual developers looking for tab-completion. The ideal user works in an environment where code changes need audit trails, security review gates, and compliance documentation. Enterprise developers in finance, healthcare, insurance, and government sectors are the primary audience — teams that work with legacy COBOL, mainframe systems, or heavily regulated codebases. Bob V2 is also a strong fit for organizations undergoing digital transformation, where the primary value is modernizing decades-old systems rather than writing greenfield applications. Individual developers who experiment with multiple AI coding tools will find Bob V2's Plan and Ask modes useful for complex tasks, but the full ROI materializes when the team uses BobShell audit trails, role-based access controls, and human-in-the-loop approval workflows.

## Verdict — Is IBM Bob V2 Worth It?

IBM Bob V2 is worth it if your team's AI coding needs extend beyond autocomplete. The three-tier architecture is a genuinely novel approach to agentic development infrastructure, and features like background tasks, per-tool-call rollback, and subagents are not available in any competing product at the same maturity level. The 45% productivity gain reported across 80,000 IBM internal developers is a credible benchmark, especially for modernization work where Bob's legacy language support is unmatched. The caveat: Bob V2's Pro model at $20/month for 40 Bobcoins is expensive relative to Cursor or Copilot, and the usage-based Bobcoins system requires cost management. For individual developers who primarily write greenfield TypeScript or Python, Cursor or Claude Code may deliver more value per dollar. For enterprise teams with compliance requirements, legacy codebases, or multi-step workflows, Bob V2 is the most capable AI coding agent available in 2026.

## Frequently Asked Questions

This section answers the most common questions about IBM Bob V2 based on hands-on evaluation, IBM's official documentation at bob.ibm.com, and developer community discussions across Hacker News, Reddit, and DevOps review sites. Each answer draws from the V2 feature set as of the June 24, 2026 GA release, covering pricing via the Bobcoins system, the three-tier Agent-Harness-Client architecture, and competitive comparisons against Claude Code, Cursor, and GitHub Copilot. IBM Bob V2 is a rapidly evolving platform, and the details below reflect the shipping V2 release — not roadmap items or beta features. If you are evaluating Bob V2 for your organization, these five questions cover the most common decision points that determine whether Bob fits your team's workflow, compliance requirements, and budget. The FAQ is organized to help you compare Bob V2 against alternatives based on your specific priorities, whether that is legacy modernization, enterprise governance, pricing predictability, or raw developer productivity.

### How is IBM Bob V2 different from Claude Code?

IBM Bob V2 is an enterprise agentic platform with a three-tier architecture (Agent/Harness/Client), multi-model orchestration across Claude, Mistral, and Granite, and built-in governance features including audit trails, role-based access controls, and human-in-the-loop approval gates. Claude Code is a single-agent terminal tool focused on individual developer productivity. Bob V2 supports background tasks, subagents with isolated context, and per-tool-call rollback — features Claude Code does not offer.

### Does IBM Bob V2 support legacy languages like COBOL?

Yes. IBM Bob V2 is the only major AI coding agent with first-class support for COBOL, JCL, CICS, IMS, RPG, and DB2. This legacy modernization capability is a core differentiator, making Bob V2 the go-to tool for enterprise teams migrating mainframe applications to modern architectures.

### How does the Bobcoins pricing system work?

Bobcoins are IBM Bob V2's usage-based currency, valued at $0.50 each. Each subscription tier includes a monthly allocation of Bobcoins: Free (40), Pro (40), Pro+ (160), Ultra (500). Different tasks consume Bobcoins at different rates based on model tier, context usage, and execution time. Overage is billed at $0.50 per Bobcoin.

### Can IBM Bob V2 run tasks in the background?

Yes. Bob V2 introduced background task execution in the V2 release, allowing the agent to continue working on long-running operations — such as legacy conversions, large refactorings, or test suite generation — after the developer closes their editor or starts a new task. Multiple background tasks can run concurrently, each as an independent agent session.

### What audit capabilities does IBM Bob V2 provide for compliance?

Bob V2 records every tool call, file change, and rollback operation in an append-only audit log maintained by the Harness layer. BobShell CLI provides raw access to these logs for SIEM and compliance dashboard integration. Organizations can configure role-based access controls, network restrictions, allowed command lists, and human-in-the-loop approval gates, making Bob V2 suitable for regulated industries requiring auditable AI-assisted development.
