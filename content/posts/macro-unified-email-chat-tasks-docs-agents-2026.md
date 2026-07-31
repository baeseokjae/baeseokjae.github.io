---
title: "Macro Review 2026: The Unified Open-Source System for Email, Chat, Tasks, Docs, and AI Agents"
date: 2026-07-31T04:03:13+00:00
tags:
  - macro
  - open source
  - unified workspace
  - AI agents
  - productivity
  - review
description: "Macro is an open-source all-in-one workspace combining email, chat, tasks, docs, CRM, and AI agents under AGPLv3. Here is our full 2026 review."
draft: false
cover:
  image: "/images/macro-unified-email-chat-tasks-docs-agents-2026.png"
  alt: "Macro Review 2026: The Unified Open-Source System for Email, Chat, Tasks, Docs, and AI Agents"
  relative: false
schema: "schema-macro-unified-email-chat-tasks-docs-agents-2026"
---

Macro is an open-source (AGPLv3) all-in-one workspace that replaces email, team chat, task management, documents, CRM, calls, pull requests, file storage, and AI agents with a single unified system. Built in Rust and TypeScript and backed by $30M from a16z, Macro aims to be the command center for modern companies — eliminating the need to juggle five or more separate SaaS tools.

## What is Macro? — Overview of the All-in-One Open-Source Workspace

Macro, founded by a team that previously relied on Superhuman, Slack, Notion, HubSpot, and Linear simultaneously, was born from a simple frustration: too many tools, too much context-switching, and no unified view of the business. The founders set out to build what they describe as an "operating system for a company" — a single workspace where every business function lives under one roof.

Launched on Hacker News in June 2026, Macro has already attracted 689 GitHub stars and 134 forks. The project is fully open source under the AGPLv3 license, distinguishing it from "open core" competitors that gatekeep premium features behind proprietary licenses. With $30M in Series A funding led by a16z with participation from BoxGroup and 3kVC, Macro has the financial runway to execute on an ambitious product roadmap.

The core thesis is straightforward: instead of paying for and managing separate tools for email (Superhuman), chat (Slack), tasks (Linear), docs (Notion), CRM (HubSpot), and file storage (Google Drive), companies can run a single self-hosted or cloud-hosted system that handles all of these functions natively. The key differentiator is that these modules are not bolted together via integrations — they share a common data model, a unified search index, and a single permission system.

## Key Features Deep Dive

### Email — Keyboard-First Multi-Account Email Client

Macro's email module is designed as a direct replacement for Superhuman, offering the same keyboard shortcuts and split-second navigation that power users expect. Unlike Superhuman, Macro supports multiple email accounts natively — a feature Superhuman charges extra for. The email client integrates directly with the workspace's unified search, so finding an email related to a task or a contact is instantaneous.

The email module also auto-links to CRM records: every email sender becomes a contact in the built-in CRM, and email threads can be linked to tasks, docs, and messages via Macro's bidirectional @linking system.

### Messages — Focused Team Chat with Channel-Based Permissions

Macro's messaging system is designed for quieter, more focused technical conversations. Unlike Slack's firehose of notifications, Macro channels support inline replies (threads that stay in the main view), channel-based permissions, and direct integration with tasks and docs. Messages can be @-linked to any other block type in the system — a message about a bug fix can link directly to the task and the pull request.

The channel structure is permissioned at a granular level, making it suitable for organizations that need to separate internal communications from client-facing discussions. The keyboard-first design means power users can navigate channels, search messages, and compose replies without touching a mouse.

### Tasks — Keyboard-First Task Management Linked to Chat and Docs

Macro's task module competes directly with Linear and Todoist. Tasks support markdown descriptions, assignees, due dates, labels, and status workflows. The killer feature is deep linking: a task can be created directly from a message or email, and any update to the task is reflected everywhere it is @-linked. This eliminates the common workflow of copying information between a chat message and a task manager.

Tasks live alongside other workspace objects in the unified search index, so searching for a project name returns relevant tasks, emails, docs, and messages in a single result set — delivered in under 50ms.

### Docs — Collaborative Markdown-Native Documents with CRDTs

Macro's document editor is markdown-native and uses CRDTs (Conflict-Free Replicated Data Types) for real-time collaborative editing. This is the same technology used by tools like Linear and Apple Notes, ensuring that concurrent edits from multiple team members never conflict or lose data.

Documents support @-linking to any other block in the workspace — tasks, emails, messages, contacts, and agents. A product requirements document can embed live links to the relevant tasks, the Slack thread where the feature was discussed, and the email from the customer who requested it. Documents are versioned and searchable through the unified index.

### AI Agents — Unified Team Memory and MCP Integration

Macro's AI agent system is arguably its most innovative feature. Agents live inside the workspace with full read and write access to email, messages, tasks, docs, calls, and channels. They maintain both personal and team-level memory — refreshed nightly — so they understand what the entire team is doing, not just individual chat history.

Agents can take real actions: send emails, create tasks, update documents, search content, and answer questions about any workspace data. The unified memory means an agent can answer "What did the team decide about the Q3 pricing strategy?" by searching across emails, meeting notes, and task descriptions.

Macro supports the Model Context Protocol (MCP), allowing external AI clients like Claude Code and Codex to connect to the workspace and interact with its data. This positions Macro as an "operating system for AI agents" — a central hub where agents can read and write across all business data.

### CRM — Auto-Built Contact Records from Email

The CRM module is lightweight but practical. Contact records are built automatically from email interactions, and each contact's profile shows their email history, linked tasks, and related messages. For startups and small teams that don't need the complexity of Salesforce or HubSpot, Macro's built-in CRM is sufficient for managing relationships without a separate tool.

### Canvas, Calls, Pull Requests, and File Storage

Macro includes additional modules that round out the workspace: a Canvas for visual brainstorming and diagramming, native voice and video calls, pull request management (linking to GitHub), and file storage. These modules share the same permission system, search index, and @-linking as the rest of the workspace, creating a genuinely unified experience.

## The Unified Memory Advantage — How AI Agents Get Full Workspace Context

The most significant architectural advantage of Macro over integrated tool stacks is unified memory. In a typical setup where a company uses Slack, Gmail, Notion, and Linear separately, an AI agent has no way to connect information across these tools. Each tool has its own data silo, its own search, and its own context.

Macro solves this by design. Because email, messages, tasks, docs, and CRM all share a single data model, the AI agent has complete context. When you ask "What's the status of the Acme Corp deal?" the agent can search across email threads with the client, task assignments, meeting notes in docs, and CRM records — all in one query.

The memory system is refreshed nightly and is accessible via @mentions and natural language queries. Critically, Macro maintains zero data retention with model providers — no customer data is used for training, and all AI processing happens with privacy guarantees backed by SOC 2 Type II and ISO 27001 compliance.

## Architecture and Tech Stack — Rust + TypeScript, CRDTs, MCP Protocol

Macro's backend is built in Rust, chosen for performance, memory safety, and concurrency. The frontend is TypeScript with a React-based UI. The use of CRDTs for collaborative editing ensures that real-time document collaboration works reliably even in offline or low-connectivity scenarios.

The unified search index returns results across all data types in under 50ms, a performance benchmark that is critical for a tool that aims to replace multiple search experiences. The MCP (Model Context Protocol) server is a first-class component, not an afterthought — it exposes the full workspace data model to external AI clients.

The system is designed to be self-hosted on a single server for small teams, with the hosted version running on AWS for larger organizations. The AGPLv3 license ensures that any modifications to the source code must be shared back with the community.

## Open Source and Licensing — AGPLv3, Self-Hosting, and Commercial Model

Macro is licensed under AGPLv3, which is a strong copyleft license. This means the software is fully open source — not "open core" with proprietary extensions. Any company that modifies and distributes Macro must release those modifications under the same license.

Self-hosting is possible under AGPLv3, though as of July 2026 it is not yet a turnkey experience. The documentation acknowledges this gap, and the community is expected to improve the self-hosting experience over time. For teams that prefer a managed solution, Macro offers a hosted SaaS subscription on AWS.

The business model combines hosted SaaS subscriptions with commercial licenses for organizations that need AGPL exceptions. This is a proven model used by companies like GitLab and MongoDB in their early days.

## Macro vs The Competition

| Feature | Macro | Notion | Slack | Linear | Superhuman | HubSpot |
|---------|-------|--------|-------|--------|------------|---------|
| Email | Native | ❌ | ❌ | ❌ | ✅ | ❌ |
| Team Chat | Native | ✅ | ✅ | ❌ | ❌ | ❌ |
| Task Management | Native | ✅ | ❌ | ✅ | ❌ | ❌ |
| Docs | Native | ✅ | ❌ | ❌ | ❌ | ❌ |
| CRM | Native | ❌ | ❌ | ❌ | ❌ | ✅ |
| AI Agents | Native | ❌ | ❌ | ❌ | ❌ | ❌ |
| Open Source | ✅ (AGPLv3) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Self-Hosted | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Unified Search | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| MCP Support | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Macro vs Notion — Purpose-Built Modules vs Generic Databases

Notion is a powerful tool, but its flexibility is also its weakness. Notion's databases are generic — you can build a task tracker, a CRM, or a wiki, but none of them are purpose-built for their function. Macro offers dedicated modules for email, tasks, CRM, and chat that are optimized for each use case. If you need a true email client or a real-time chat system, Notion cannot replace those tools. Macro can.

### Macro vs Superhuman — Email Client Comparison

Superhuman is the gold standard for keyboard-first email, but it is expensive ($30/month), supports only one account at the base tier, and integrates with nothing outside of email. Macro matches Superhuman's keyboard shortcuts and speed while adding multi-account support, deep workspace integration, and a fraction of the per-seat cost when self-hosted.

### Macro vs Slack — Quiet, Focused Channels vs Noisy Chat

Slack's strength is its ecosystem of integrations, but its core chat experience is noisy. Channels accumulate thousands of messages, and finding relevant information requires scrolling or searching across a separate tool. Macro's channels are designed for quieter, more focused conversations with inline replies and direct linking to tasks and docs. For technical teams that value context over volume, Macro's approach is more productive.

### Macro vs Linear — Task Management Comparison

Linear is the current favorite for software teams, and Macro's task module borrows heavily from its design philosophy: keyboard-first, markdown-native, and fast. The difference is that Macro's tasks are natively linked to emails, messages, and docs. A Linear task exists in isolation; a Macro task exists in the full context of the business.

### Macro vs HubSpot — CRM Capabilities

Macro's CRM is not a replacement for HubSpot's marketing automation, sales pipeline management, or analytics. However, for startups and small teams that primarily need contact management linked to email and tasks, Macro's built-in CRM eliminates the need for a separate tool. As the company grows, Macro's open-source nature means the CRM can be extended or integrated with external systems.

## Security and Compliance — SOC 2, ISO 27001, Zero Data Retention

Macro has achieved SOC 2 Type II certification and ISO 27001 compliance, making it suitable for organizations with regulatory requirements. The zero data retention policy with AI model providers means that customer data is never used for training or stored by third parties.

For self-hosted deployments, all data remains on the organization's infrastructure, giving full control over data residency and access. The AGPLv3 license ensures transparency — the code is auditable by any security team.

## Pricing and Business Model — Hosted SaaS + Commercial Licenses

Macro's pricing is not yet publicly detailed, but the business model is clear: hosted SaaS subscriptions for teams that want a managed solution, and commercial licenses for organizations that need AGPL exceptions. Self-hosting under AGPLv3 is free, though organizations must factor in the cost of infrastructure and maintenance.

Compared to the combined cost of Notion ($10/user), Slack ($8/user), Linear ($8/user), Superhuman ($30/user), and HubSpot ($50/user), even Macro's hosted tier is likely to be significantly cheaper for teams that would otherwise pay for five separate tools.

## Who Should Use Macro? — Target Audience and Use Cases

Macro is best suited for:

- **Startups (5–50 people)** that want one tool instead of five, reducing both cost and context-switching overhead
- **Technical teams** that value keyboard-first workflows, markdown, and command-line-adjacent design
- **Consultancies and agencies** that need client-facing communication, task tracking, and document collaboration in one place
- **Privacy-conscious organizations** that want self-hosted compliance without sacrificing modern features
- **AI-forward teams** that want to integrate AI agents deeply into their daily workflow

Macro is less suitable for large enterprises with entrenched tool ecosystems, teams that rely on Slack's extensive third-party app directory, or organizations that need advanced marketing automation or sales analytics.

## Limitations and Gaps — Self-Hosting Maturity, Email Provider Support

As of July 2026, Macro has several limitations worth noting:

- **Self-hosting is not turnkey.** The documentation acknowledges this, and the community is still building deployment guides and Docker configurations.
- **Email provider support** may be limited to common providers (Gmail, Outlook) with less support for custom IMAP setups.
- **48 open issues on GitHub** indicate active development but also a growing backlog.
- **The ecosystem is young.** Unlike Slack or Notion, Macro does not yet have a large library of integrations or third-party apps.
- **Mobile experience** is not yet detailed in the documentation, which may be a concern for teams that need full mobile functionality.

## Conclusion — Is Macro the Future of Unified Workspaces?

Macro represents a bold bet: that companies are ready to abandon the multi-tool SaaS stack in favor of a single, open-source, AI-native workspace. The product is ambitious, the technology is sound (Rust, CRDTs, MCP), and the $30M a16z backing provides credibility and runway.

The unified memory and AI agent integration are genuinely innovative — no other open-source workspace offers agents with full context across email, chat, tasks, and docs. For startups and technical teams that value speed, keyboard-first design, and open-source transparency, Macro is already a compelling option.

The biggest open questions are around self-hosting maturity, ecosystem growth, and enterprise adoption. If Macro can deliver on its self-hosting roadmap and build a community around its open-source core, it has the potential to become the default workspace for a new generation of companies.

## FAQ

### What is Macro and how does it work?

Macro is an open-source (AGPLv3) all-in-one workspace that combines email, team chat, task management, documents, CRM, calls, pull requests, file storage, and AI agents into a single unified system. It is built in Rust and TypeScript, uses CRDTs for real-time collaboration, and supports the Model Context Protocol (MCP) for AI agent integration.

### How does Macro compare to Notion?

Unlike Notion's generic databases, Macro offers purpose-built modules for email, chat, tasks, CRM, and docs. Notion is a flexible tool that can approximate many functions, but it cannot replace a native email client or real-time chat system. Macro provides dedicated, optimized modules for each function while maintaining a unified data model and search index.

### Is Macro truly open source?

Yes, Macro is fully open source under the AGPLv3 license. This is not an "open core" model where premium features are proprietary — the entire codebase is available on GitHub. Organizations that modify and distribute Macro must share those modifications under the same license, or purchase a commercial license for AGPL exceptions.

### Can I self-host Macro?

Yes, Macro can be self-hosted under the AGPLv3 license. However, as of July 2026, the self-hosting experience is not yet turnkey. The documentation acknowledges this gap, and the community is actively working on improving deployment guides and infrastructure tooling.

### What makes Macro's AI agents different from other AI tools?

Macro's AI agents have unified memory across the entire workspace — email, messages, tasks, docs, and CRM — so they understand the full context of the business, not just individual chat history. They can take real actions like sending emails, creating tasks, and updating documents. The MCP protocol support also allows external AI clients like Claude Code to interact with workspace data.
