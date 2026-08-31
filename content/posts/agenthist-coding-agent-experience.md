---
title: "Coding Agent Experience Management: Manage, Migrate, and Extract Value from Local Sessions"
date: 2026-08-31T10:05:07+00:00
tags:
  - coding agents
  - agent memory
  - agent session management
  - local-first
  - AgentHist
description: "Coding agent experience management means turning scattered local sessions into a searchable, migratable, reusable library. AgentHist handles browse, search, export, import, cross-agent conversion, and evidence-backed experience extraction."
draft: false
cover:
  image: "/images/agenthist-coding-agent-experience.png"
  alt: "Coding Agent Experience Management: Manage, Migrate, and Extract Value from Local Sessions"
  relative: false
schema: "schema-agenthist-coding-agent-experience"
---

Coding agent experience management is the practice of turning the session history your local coding agents generate into a searchable, migratable, and reusable asset instead of leaving it as scattered log files. Open-source tools such as AgentHist bring sessions from Codex, Claude Code, OpenCode, and Pi into one library for browsing, searching, exporting, and selective importing — including cross-machine migration and cross-agent conversion. AgentHist is a TypeScript CLI, MIT-licensed, supporting Linux, macOS, and Windows, created August 2026 (source: GitHub API).

## Why your coding agent's history is your most underused asset

Every coding agent session captures decisions, requirements, and working methods that your team paid tokens to produce. Yet in most setups, that history is treated as ephemeral. When a session ends, the transcript sinks into a verbose log file that nothing indexes, nothing searches, and nothing reuses. The next session on the same codebase starts from zero, re-reading the same files and re-deriving the same conclusions.

This is a real economic problem, not an aesthetic one. Consider what the research brief for this guide uncovered: the community has responded with at least three separate open-source tools — AgentHist, coding_agent_session_search (cass), and ctx — all built around the same insight that coding agents have git history for code but effectively no usable memory for the reasoning behind it. The core value proposition stated in the ctx project README is that coding agents already have git history but their session transcripts live in verbose log files the developer cannot query.

The return on experience management shows up in four measurable places: less repeated agent work, lower token spend, better task outcomes, and the ability to recover failed approaches and decisions from prior sessions. When a session disappears, a hard-won bug hunt, a rejected architecture, or a carefully tested workaround is gone with it. Managing that history turns a one-time cost into a compounding asset.

## What AgentHist does — one library for all your agent sessions

AgentHist (lohoz/agenthist) is designed around a simple premise: your coding agents already produce rich session records, and you should own them in one place. It supports four agents today — Codex, Claude Code, OpenCode, and Pi — and brings their sessions into a unified store that you can browse, search, export, and selectively import.

| Capability | What it does | Agents supported |
|-----------|--------------|------------------|
| Browse & history | List and inspect past sessions in one timeline | Codex, Claude Code, OpenCode, Pi |
| Resume | Pick up a prior session where it left off | Same as above |
| Search | Run unified search across all sessions | Same as above |
| Export | Package sessions for backup or migration | Same as above |
| Selective import | Pull specific sessions back in with conflict detection | Same as above |
| Cross-agent conversion | Convert Codex sessions to Claude Code and back | Across supported agents |
| Experience extraction | Extract recurring requirements, preferences, and methods | Cross-session |

The differentiator versus earlier tools is the selective import and cross-agent conversion workflow. AgentHist treats your session history as something you can move and reshape, not just view. Before writing anything, it reports conflicts and lets you inspect what a migration would do, which fits a safe-by-design framing discussed below.

## Setting up AgentHist — install, doctor, and first scan

AgentHist runs on the JavaScript runtime and requires Node.js 24 (source: README). Installation is a standard package-manager step. Once installed, the workflow starts with a `doctor` command that validates your environment, then a `scan` that discovers sessions from each supported agent and ingests them incrementally into the local store.

```bash
npm install -g agenthist
# or, without a global install
npx agenthist --help
```

The command set is documented in the README and includes: `doctor`, `scan`, `history`, `resume`, `export`, `inspect`, `import`, `experience`, `skill`, `codex provider`, and `transaction`. Two early commands matter most on first setup:

- `doctor` — checks that the environment and any agent providers are healthy before you scan.
- `scan` — discovers and ingests sessions. Because processing is incremental, a second scan only handles sessions that changed since the last run, keeping repeat analysis cheap.

If you hit a problem, `doctor` is the first place to look. It surfaces environment or provider issues before you waste time on an ingestion that cannot succeed.

## Browse, search, and resume sessions from any agent

Once sessions are scanned, the `history` command gives you a unified view across every supported agent. Rather than opening each agent's own log directory, you see one timeline. From there you can inspect a single session in detail and `resume` it when you need to continue the work.

The unified view matters because most developers run more than one coding agent. You might prototype in Codex, then switch to Claude Code for a long task, then use OpenCode for a small edit. Without a unified store, that workflow fragments your memory across three incompatible formats. AgentHist collapses them into one browsable source of truth.

The resume flow is also a form of continuity insurance. When you come back to a task days later, you do not have to reconstruct the context from a stale chat window. You recall the session by name or description, inspect its transcript, and resume exactly where the work left off.

## Migrating between machines — export, inspect, and selective import

Experience management is not just about time; it is about machines. When you switch from a workstation to a laptop, or onto a new machine entirely, your coding agent history should come with you. AgentHist's migration path is export, inspect, then selective import, and it is deliberately granular so you never migrate more than you intend.

The workflow uses session references such as `ahsr1_codex_ck1_7d4c...` — a unique identifier for a source session. These refs let you target exactly which sessions you export or import rather than committing to a bulk copy of everything.

| Migration step | Command / action | What it protects |
|----------------|-----------------|------------------|
| 1. Export | Package the sessions you want | Selectivity — export only what you need |
| 2. Inspect | Review the export and its refs before importing | Safety — confirm exactly what will be written |
| 3. Import | Pull sessions into the target machine | Path mapping across OSes |
| 4. Verify | Confirm conflicts were handled | No silent duplicate or partial writes |

AgentHist also handles path mapping across operating systems, so a session recorded on a macOS machine with `/Users/me/project` can be imported sensibly onto a Linux machine that references `/home/me/project`. This path mapping is what makes cross-machine and cross-OS migration practical rather than theoretical.

## Converting sessions between agents (Codex → Claude Code) with --dry-run and --apply

Perhaps the most distinctive feature of AgentHist is cross-agent conversion: turning a session from one agent into the format of another. The flagship example is converting a Codex session into a Claude Code session, but the tool supports conversion in either direction among the supported agents.

This feature is a direct answer to vendor lock-in. Your accumulated session history in one agent is a sunk investment; the ability to convert it to another agent's format means you can switch tools without abandoning the context you have built up. The project frames this as "cross-Agent conversion (Codex -> Claude, etc.)" and positions it as a core reason to manage history rather than let each agent own its fragments in isolation.

Two flags govern the write path and they are the safety rail for the whole feature:

- `--dry-run` — preview exactly which sessions would convert and how, without changing anything on disk.
- `--apply` — actually perform the conversion after you have reviewed the dry run.

This preview-then-apply pattern is what separates conversion from destructive migration. You see the plan, confirm it matches your intent, and only then commit the write. It is the same conservative behavior applied to imports and experience writes.

## Extracting cross-session experience — the fast/deep model two-tier workflow

Browsing, migrating, and converting organize your history, but the reason most tools in this space exist is reuse — turning the raw transcript pile into something you can act on. AgentHist addresses this with an `experience` command that extracts recurring requirements, preferences, and working methods across sessions, then surfaces them as evidence-backed candidates for review, merging, and refinement.

The extraction pipeline uses a two-tier model strategy that is explicitly designed to control cost. A fast model first extracts evidence from each session. An optional deep model then organizes that evidence into structured candidates across sessions. This tiers the expensive reasoning to the top of the funnel only, never re-analyzing unchanged sessions.

| Workflow stage | Model tier | What it produces |
|----------------|-----------|------------------|
| 1. Extract | Fast model | Discrete evidence per session |
| 2. Organize | Deep model (optional) | Cross-session candidates |
| 3. Filter | Reviewer | Merged, refined, human-validated preferences |
| 4. Re-run | Cached | No repeat analysis of unchanged sessions |

The cost control is deliberate. The README identifies incremental processing and cached model results for unchanged sessions as the mechanism that keeps repeated analysis cheap. This matters because experience extraction is not a one-time event — it is something you re-run as new sessions accumulate. If every run re-analyzed everything, the expense would grow unbounded. Because unchanged sessions are skipped, the marginal cost of a daily or weekly extraction stays low.

The output is explicitly framed as candidates, not final answers. Recurring patterns are surfaced for a human to review, merge, and refine before they become durable preferences or working methods. This keeps extracted knowledge grounded in evidence rather than in a model's confident guess.

## Safety first — transactions, duplicate detection, and what AgentHist does NOT touch

A history tool is only trustworthy if it cannot damage the very thing it presides over. AgentHist is built around transactional safety: deduplicate sessions, report conflicts before writing, and recover or roll back changes when something goes wrong.

The `transaction` command is the mechanism behind this guarantee. Writes to the session store — whether imports, conversions, or experience outputs — are treated as transactions with defined success and rollback paths. If a write fails midway, you can recover rather than being left with a half-updated store.

Duplicate detection is a specific concern in migration. When you import a session that is already present, AgentHist deduplicates by session reference rather than creating a second copy. This prevents the store from ballooning with repeated imports across machine moves.

Equally important is what AgentHist will not do. The README is explicit: it handles history records only and does NOT migrate Base URLs, API keys, tokens, OAuth data, or connection settings. Your credentials and provider configuration stay exactly where they are. This is a meaningful safety boundary — migration tools that copy credentials are a credential-leak risk; AgentHist deliberately avoids that category of data entirely.

## AgentHist vs the alternatives (cass, ctx, AgentHistory) — what to choose

AgentHist is not the only tool trying to organize coding-agent history. The field has at least four serious options, and each has a different center of gravity. Choosing among them is a matter of what you value most.

| Tool | Approach | Standout strength | License / status |
|------|---------|-------------------|------------------|
| **AgentHist** (lohoz/agenthist) | TypeScript CLI; browse, search, export, import, cross-agent convert, experience extraction | Migration + cross-agent conversion + experience reuse | MIT; ~71 GitHub stars |
| **cass** (Dicklesworthstone) | Rust TUI/CLI; unified search/index of ~20+ agents | Breadth of agents indexed into one timeline | MIT + AI licenses; ~1,097 stars |
| **ctx** (ctxrs/ctx) | CLI for fast local search across sessions; paid `ctx pro` for transcript provenance | "Git blame for agent sessions" | ~1,052 stars, paid add-on |
| **AgentHistory** (LinnkLabs) | Local-first task board + searchable librarian for Claude Code / Codex | Live status board + one-click resume | VS Code / npx |

The pattern is clear: the mainstream tools are converging on local-first search as the baseline. What separates AgentHist is the active data plane — migration, selective import, and cross-agent conversion — plus experience extraction. cass excels if your priority is indexing sessions from every agent you have ever installed, including ChatGPT, Copilot, and Hermes, into one searchable timeline. ctx wins if your main pain is provenance — knowing exactly which session produced a given line or commit. AgentHistory wins if you want a live board of what is happening now with click-to-jump resume.

For most developers, the decision comes down to intent. If you want to search history, cass and ctx are strong. If you want to own, move, convert, and mine that history as a durable asset, AgentHist is the more complete fit. Several of these tools are young — AgentHist's star count (~71) is far lower than cass (~1,097) or ctx (~1,052) as of the research date, which reflects its newness, not a lack of capability.

## Privacy and security notes on handling .agenthist files

AgentHist stores session content in `.agenthist` files, and the project is explicit about what those files contain: chat content, including the prompts and responses from your conversations with coding agents. That is not neutral data. A session transcript can include source code, internal design reasoning, customer references, or other material you would not want to leave unguarded.

The README's guidance is blunt: handle `.agenthist` files as carefully as you would the original conversations. Several practical rules follow from that:

- Encrypt or restrict access to the directories where AgentHist stores its data, especially on shared or cloud-synced machines.
- Do not commit `.agenthist` files to a repository unless the repository is private and the content is cleared for that exposure.
- Be deliberate about what you export and where you import it. A cross-machine migration is a data transfer; treat `.agenthist` exports the way you would treat exporting chat logs with confidential content.
- Remember that experience extraction sends session content through model calls. Because AgentHist supports local models and a tiered call strategy, you can choose the model tier and provider that match your confidentiality needs.
- Revisit your store before migrating machines or sharing your terminal environment — a stale transcript is still a sensitive transcript.

The privacy boundary matters precisely because the rest of the tool is so capable. If migration, search, and extraction work well, they become the default way your history moves around. The security note is the reminder that every one of those flows is moving chat content that deserves the same care as the original conversation.

## FAQ

**What is coding agent experience management?**
Coding agent experience management is the practice of organizing your local coding-agent session history into a searchable, migratable, and reusable asset. It goes beyond searching transcripts to include backing up sessions, migrating them between machines and agents, and extracting recurring requirements and preferences so future sessions do not redo past work.

**Which coding agents does AgentHist support?**
As of the research date, AgentHist supports Codex, Claude Code, OpenCode, and Pi. It provides a unified store for browsing, searching, and resuming sessions across all four, and supports cross-agent conversion between them (for example, Codex sessions converted to Claude Code).

**Does AgentHist migrate my API keys and connection settings?**
No. AgentHist explicitly handles history records only. It does not migrate Base URLs, API keys, tokens, OAuth data, or connection settings. Your credentials and provider configuration remain untouched, which removes a major credential-leak risk from migration.

**How does AgentHist keep migration and import safe?**
It uses transactional writes, duplicate detection, and conflict reporting. Sessions are deduplicated by reference, conflicts are reported before any write, and the transaction command lets you recover or roll back failed writes. Cross-agent conversion additionally uses a `--dry-run` preview before `--apply`.

**Is AgentHist experience extraction expensive to run?**
The two-tier strategy keeps it cheap. A fast model extracts evidence per session, and an optional deep model organizes candidates across sessions. Incremental processing skips unchanged sessions and caches model results, so repeated extraction runs do not re-analyze everything and the marginal cost stays low.
