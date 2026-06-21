---
cover:
  alt: CLAUDE.md Setup Guide 2026
  image: /images/claude-md-setup-guide-2026.png
  relative: false
date: 2026-04-23 01:10:34+00:00
description: 'Complete CLAUDE.md setup guide for 2026: structure, examples, hierarchy,
  hooks, and best practices to maximize Claude Code in any project.'
draft: false
schema: schema-claude-md-setup-guide-2026
tags:
- claude-code
- ai-coding
- developer-tools
- configuration
- productivity
title: 'CLAUDE.md Setup Guide 2026: The Config File That Makes Claude Code Actually
  Useful'
---

CLAUDE.md is the project instructions file that Claude Code reads before every session — it's the single most impactful configuration you can make. Drop it in your repo root, add your coding conventions and architecture notes, and Claude stops asking the same questions every session.

---

## What Is CLAUDE.md? The System Prompt for Your Codebase

CLAUDE.md is a Markdown file that acts as a persistent system prompt scoped to your project. Unlike conversation-level instructions that disappear after compaction, CLAUDE.md is re-read from disk at the start of every session and after every context compaction event. Introduced by Anthropic in August 2025, the format caught on fast enough that competitors shipped their own versions — GEMINI.md, .cursorrules, AGENTS.md — within months. By early 2026, 71% of developers who regularly use AI agents were using Claude Code (Pragmatic Engineer Survey, 15,000 developers), and the CLAUDE.md pattern had become the de facto standard for project-level AI configuration.

The core purpose is simple: tell Claude what it needs to know about *your specific project* that it cannot infer from reading the source files. This includes architectural decisions, conventions that deviate from common defaults, commands to run, things Claude should never do, and project-specific context. You write CLAUDE.md; Claude reads it. The relationship between CLAUDE.md and Claude's auto memory (MEMORY.md) is complementary — you own CLAUDE.md, Claude owns auto memory, and both persist across sessions through different mechanisms.

The practical payoff is immediate. With a well-structured CLAUDE.md, Claude stops generating code that violates your conventions, stops asking what test runner you use, and stops proposing architectures you've already decided against. That improvement compounds across hundreds of sessions.

---

## How Claude Code Discovers and Loads CLAUDE.md Files

Claude Code uses a layered discovery system that loads multiple CLAUDE.md files simultaneously, merging their instructions in priority order. Understanding this discovery order is essential for monorepos and large projects where different directories need different rules.

The load order from highest to lowest priority:

1. **Managed policy** — Enterprise-level policy set by your org admin (cannot be overridden)
2. **User global** — `~/.claude/CLAUDE.md` — applies to every project on your machine
3. **Project root** — `./CLAUDE.md` — the standard project-level file
4. **Local project** — `./.claude/CLAUDE.md` — gitignore-friendly variant for personal overrides
5. **Parent directories** — Any CLAUDE.md files in directories above your working directory
6. **Subdirectory files** — `./src/CLAUDE.md`, `./packages/api/CLAUDE.md`, etc.

The critical distinction for monorepos: **parent-directory CLAUDE.md files load at launch**, while **subdirectory files load on demand** when Claude accesses that directory. This means your root CLAUDE.md is always in context, but a `packages/api/CLAUDE.md` only gets loaded when Claude is actually working in that package. This keeps the context window lean when you have many packages.

Claude Code also reads `.claude/rules/` files on demand based on path matching, and respects an `@import` syntax for inline file inclusion.

---

## The CLAUDE.md Hierarchy: Global, Project, Local, and Subdirectory Files

Managing multiple CLAUDE.md files lets you separate concerns cleanly across teams, machines, and project components. The hierarchy is designed so that personal preferences don't pollute shared project config, and project-wide rules don't need to be repeated in every subdirectory.

**User global (`~/.claude/CLAUDE.md`)** — Personal preferences that apply everywhere: your preferred diff format, how you like code explained, your timezone for date calculations. Keep this short — under 30 lines. It applies to every project, so anything project-specific here is noise.

**Project root (`./CLAUDE.md`)** — The main file checked into version control. Contains architecture decisions, tech stack, shared commands, coding conventions, and constraints the whole team agrees on. This is the file most developers mean when they say "CLAUDE.md."

**Local project (`./.claude/CLAUDE.md`)** — Typically gitignored. Good for personal overrides: machine-specific paths, draft notes about what you're currently working on, or instructions you want for your sessions but don't want to enforce on the whole team.

**Subdirectory files** — Load on demand. Ideal for monorepos where `packages/payments/` has different conventions than `packages/dashboard/`. The subdirectory file adds to (not replaces) the root file.

For most solo projects, you only need the project root file. For teams, add global for personal preferences and consider `.claude/rules/` for path-scoped automation.

---

## The .claude/rules/ Directory: Path-Scoped Rules for Large Projects

The `.claude/rules/` directory is a folder-based extension to CLAUDE.md that lets you create rule files activating only when Claude is working with specific file paths. Each file in `.claude/rules/` uses YAML frontmatter with a `paths` key — a list of glob patterns — to declare its scope. When Claude opens or edits a file that matches any listed pattern, it loads that rules file automatically. This is more surgical than subdirectory CLAUDE.md files: you can apply different rules to `*.test.ts` files versus `src/api/**` versus `infrastructure/**` without restructuring your directory tree or creating nested CLAUDE.md files. In a large codebase where the backend, frontend, infrastructure, and test suites have genuinely different conventions, `.claude/rules/` prevents the root CLAUDE.md from growing into an unmaintainable wall of conditional statements. Rules files load on demand at pattern-match time, not at startup, so they don't inflate the initial context load. The practical limit is the same as CLAUDE.md — keep each rules file focused, under 100 lines, targeting conventions specific to that path pattern.

Rules files use YAML frontmatter to declare when they apply:

```markdown
---
paths:
  - "src/api/**"
  - "packages/server/**"
description: "Server-side rules: no browser APIs, always use structured logging"
---

## Server Rules

- Never use `window`, `document`, or `localStorage` — server-side code only
- Use `logger.info()` not `console.log()` — structured logging required
- All async functions must have explicit error handling with typed catch blocks
- Database calls go through the repository layer in `src/db/repositories/`, never raw queries in route handlers
```

Rules files load on demand, not at startup. Claude checks path matches when it opens or edits a file and pulls in the matching rules. This keeps startup context lean while ensuring rules are present when relevant.

Key difference from `.claude/CLAUDE.md`: rules files target specific file patterns and are better for language- or layer-specific conventions. Use CLAUDE.md for project-wide context; use rules files for "only when working in X."

---

## The @import Syntax: Referencing External Files in CLAUDE.md

The `@import` syntax is a CLAUDE.md directive that expands an external file inline — Claude reads the referenced file's contents as if they were written directly at that point in CLAUDE.md. This lets you keep the CLAUDE.md itself short and navigable while pulling in detailed reference material that would otherwise inflate the file beyond the 200-line limit. The most common use cases are database schemas (too long to write out, but Claude needs to know the column names), API style guides (often 50–100 lines of endpoint conventions), and architecture decision records that explain why certain patterns are mandated. When Claude reads a CLAUDE.md containing `@import` directives, it fetches and expands each one before processing the full instruction set — the imported content is fully visible and subject to the same instruction budget as anything else in the file. The import chain supports up to 5 hops of recursion: an imported file can import another, that file can import a third, and so on up to 5 levels deep. Beyond that depth, imports are ignored. Practical constraint: files imported via `@import` must live on the local filesystem. There is no support for URLs or remote resources. For frequently-updated reference material, `@import` is better than copy-pasting because you update the source file and CLAUDE.md automatically reflects the change.

Here's how to structure a CLAUDE.md that uses imports:

```markdown
# Project Overview

This is a Next.js e-commerce platform for B2B customers.

## Architecture

@import docs/architecture/overview.md

## API Conventions

@import docs/conventions/api-style-guide.md

## Database Schema

@import docs/schema/current-schema.sql
```

When Claude reads the CLAUDE.md, it expands each `@import` inline, as if the content were written directly in the file. This is useful for keeping CLAUDE.md itself under the recommended length while still giving Claude access to detailed reference material.

Constraints to know:
- Maximum 5-hop recursion depth (imported files can import others, up to 5 levels deep)
- Each imported file counts toward the total instruction budget
- The 200K token context window (1M in beta) is generous, but deep import chains in large docs can add up

Practical use: `@import` is ideal for database schemas, API contracts, and detailed architecture docs that are too long for CLAUDE.md but too important to leave out. Avoid importing files that change frequently without pruning old versions — stale imported content causes stale behavior.

---

## 7 Essential Sections of an Effective CLAUDE.md

A well-structured CLAUDE.md covers seven areas that address the most common sources of friction between developers and AI coding assistants. Not every project needs all seven — a solo weekend project might need only three — but most production codebases with more than one developer benefit from each section. The order below is intentional: Claude reads CLAUDE.md top to bottom, and earlier context shapes how it interprets later sections. A project overview at the top tells Claude what domain it's working in before it sees any conventions; that framing makes the conventions more parseable. Stack information before commands prevents Claude from suggesting commands that don't match your actual setup. Negative instructions work best at the end, where they override any positive patterns Claude might have developed from reading the earlier sections. The most common CLAUDE.md mistake is omitting the "What NOT to Do" section — it's the highest-value section in most production files because it directly encodes lessons from real mistakes. Start with the first four sections for immediate improvement; add the remaining three as you discover where Claude consistently goes wrong in your codebase.

### 1. Project Overview (5–10 lines)

What the project does, who uses it, and its current stage. Include the production URL if there is one. This orients Claude before it reads a single line of code.

```markdown
## Project Overview

InventoryOS is a B2B inventory management SaaS for mid-market retailers.
Live at app.inventoryos.io, 400+ paying customers.
Next.js 15 frontend, FastAPI backend, PostgreSQL + Redis.
Currently: migrating from REST to tRPC for the internal API layer.
```

### 2. Technical Stack and Versions

Exact versions matter. Claude behaves differently for React 18 vs React 19, Python 3.11 vs 3.12. Don't assume it will infer from package.json.

```markdown
## Stack

- Frontend: Next.js 15.2, React 19, TypeScript 5.4, Tailwind 4.0
- Backend: Python 3.12, FastAPI 0.115, SQLAlchemy 2.0 (async)
- DB: PostgreSQL 16 (primary), Redis 7 (sessions + cache)
- Testing: pytest + httpx (backend), Vitest + Testing Library (frontend)
- Infra: AWS ECS Fargate, RDS, ElastiCache
```

### 3. Common Commands

The commands Claude should run — and the ones it should never run. This section alone saves enormous back-and-forth.

```markdown
## Commands

Development:
- `pnpm dev` — start frontend (port 3000)
- `uvicorn app.main:app --reload` — start backend (port 8000)
- `docker compose up db redis` — start DB + cache

Testing:
- `pytest -x` — run backend tests (stop on first failure)
- `pnpm test` — run frontend tests
- `pnpm test:e2e` — Playwright E2E tests (requires dev server running)

NEVER run:
- `DROP TABLE` or `DELETE FROM` without explicit user confirmation
- `git push --force` under any circumstances
- `pnpm build` in development — it overwrites dev configs
```

### 4. Code Style and Conventions

Project-specific patterns that deviate from defaults. Don't list things Claude already knows — focus on your choices.

### 5. Architecture and File Organization

Where things live and why. Especially important for monorepos or projects with non-obvious structure.

### 6. What NOT to Do

This is the most underused and highest-value section. Negative instructions are often more effective than positive ones because they prevent the specific mistakes that have already cost your team time.

### 7. Testing Expectations

What level of test coverage you expect, what testing patterns you use, and what Claude should or shouldn't generate when writing tests.

---

## Real-World CLAUDE.md Examples

Real CLAUDE.md files from production projects follow a clear pattern: they are shorter than you'd expect, they are blunt, and they spend more words on what not to do than on abstract principles. The examples below cover the four most common project archetypes — minimal solo project, monorepo, Python ML pipeline, and Next.js app. Each one is opinionated by design: the goal is to show how specificity outperforms generality. A CLAUDE.md that says "follow TypeScript best practices" does nothing; one that says "never use `any`, never write class components, always use Server Components by default" gives Claude actionable constraints. Open-source projects provide the best real-world reference points: the Next.js repository (138K GitHub stars), LangChain (128K stars), Excalidraw (118K stars), and Deno (106K stars) all maintain CLAUDE.md files. Their files average 80–150 lines, weight heavily toward commands and constraints, and include specific negative instructions drawn from real contributor mistakes. These examples are simplified but reflect that structure. Adapt the one closest to your project type as a starting template, then prune any line that doesn't reflect an actual decision your team has made.

### Minimal Project (Solo Dev)

```markdown
# CLAUDE.md

## Project
Personal finance tracker. Next.js 15 + Prisma + PostgreSQL. Solo project, no need for PR process.

## Commands
- `pnpm dev` — dev server (port 3000)
- `pnpm db:push` — push schema changes (dev only)
- `pnpm test` — vitest

## Conventions
- Functional components only, no class components
- Server Components by default; use 'use client' only when state/effects needed
- Prisma for all DB access — no raw SQL
- tailwind-merge for className joins

## Never
- Add comments to obvious code
- Use `any` in TypeScript
- Create new API routes — we use Server Actions
```

### Monorepo Setup

```markdown
# CLAUDE.md — Root (applies to all packages)

## Repo Structure
Turborepo monorepo. Packages: `apps/web` (Next.js), `apps/api` (FastAPI), `packages/shared` (TS types).
See per-package CLAUDE.md for package-specific rules.

## Shared Commands
- `turbo dev` — start all services
- `turbo test` — run all tests
- `turbo build` — build all packages

## Shared Conventions
- All public APIs must be typed in `packages/shared/types/`
- Breaking changes to shared types require updating all consumers before merge
- Use pnpm workspaces — never install to root package.json

## Never
- Import from `apps/` in `packages/` — packages must not depend on apps
- Commit .env files — use .env.example with documented keys only
```

### Python ML Project

```markdown
# CLAUDE.md

## Project
ML pipeline for churn prediction. Trains weekly on Databricks, serves via FastAPI.
Python 3.12. Data in S3, models in MLflow.

## Commands
- `make train` — local training run with sample data (50K rows, not full dataset)
- `make serve` — start inference API
- `pytest tests/ -v` — run tests

## Data Conventions
- Never load full dataset locally — use `data/sample/` for dev/test
- All features go through `src/features/` pipeline — no ad-hoc transformations in notebooks
- Model artifacts saved to `models/` locally, `s3://ml-models/churn/` in production

## Never
- Hard-code thresholds — use config in `conf/model.yaml`
- Commit model artifacts or datasets to git
- Run experiments in production MLflow tracking server — use staging
```

---

## The 200-Line Rule: Why Shorter CLAUDE.md Files Outperform Longer Ones

The 200-line limit for CLAUDE.md is not about token budgets — it's about instruction budgets. Frontier LLMs like Claude reliably follow approximately 150–200 distinct instructions in a given context. Claude Code's own system prompt uses roughly 50 of those slots, leaving around 100–150 instructions for your CLAUDE.md. A 500-line CLAUDE.md likely contains far more than 150 instructions, and the excess dilutes the ones that matter.

The math is straightforward: 100 lines of CLAUDE.md use roughly 500–1000 tokens, a trivial fraction of Claude's 200K token context window. The bottleneck is not tokens — it's attention. Instructions compete for Claude's attention, and in a crowded prompt, low-priority instructions get deprioritized or ignored. A focused 80-line CLAUDE.md where every line earns its place will consistently outperform a sprawling 400-line file full of things Claude already knows.

Pruning strategy: remove anything Claude can infer from the codebase (it reads your files), anything generic that applies to any project (follow REST conventions, write clean code), and anything that hasn't influenced a real interaction in the past month. What remains should be specific, non-obvious, and project-critical. If you're unsure whether a line belongs, delete it and see if Claude's behavior degrades. If it doesn't, the line wasn't doing work.

The 200-line recommendation also applies to auto memory files. The MEMORY.md index is always loaded, but only the first 200 lines are guaranteed to be visible — another reason to keep your index tight.

---

## Advisory vs Deterministic: CLAUDE.md Instructions vs Hooks

CLAUDE.md instructions are advisory — Claude reads them and tries to follow them, but there is no enforcement mechanism. For conventions like naming patterns, architecture preferences, or explanation style, advisory is fine. For compliance requirements, security rules, or anything that must never be violated, you need hooks.

Hooks are shell commands configured in `.claude/settings.json` that execute deterministically in response to Claude's actions. They run outside of Claude's context — they cannot be talked out of running, overridden by conversation, or forgotten after compaction.

Common hook patterns:

**PostToolUse — run linter after every file edit:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "cd $CLAUDE_PROJECT_ROOT && pnpm lint --fix $CLAUDE_TOOL_INPUT_FILE_PATH" }
        ]
      }
    ]
  }
}
```

**PreToolUse — block dangerous commands:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "echo $CLAUDE_TOOL_INPUT_COMMAND | grep -q 'DROP TABLE\\|DELETE FROM' && exit 1 || exit 0" }
        ]
      }
    ]
  }
}
```

The practical rule: use CLAUDE.md for things you want Claude to consider; use hooks for things that must always happen. A linter running on every edit is a hook. "Prefer functional components" is a CLAUDE.md instruction.

---

## Auto Memory vs CLAUDE.md: Complementary Context Systems

CLAUDE.md and auto memory (the `~/.claude/projects/.../memory/` system) serve different purposes and complement each other. The distinction is ownership and scope.

**You write CLAUDE.md.** It contains project conventions, architecture decisions, commands, and constraints that the whole project depends on. It's checked into version control (usually). Team members benefit from it. It changes when the project changes.

**Claude writes auto memory.** It accumulates facts about you — your role, preferences, feedback patterns, recurring decisions — across conversations. It's personal to your Claude Code installation, not shared with teammates. It helps Claude behave consistently with your preferences without you repeating yourself each session.

Auto memory is loaded into every conversation context, but the MEMORY.md index is capped at 200 lines. Individual memory files are read on demand when relevant. CLAUDE.md is always fully loaded.

A common mistake: putting personal preferences in CLAUDE.md and project facts in auto memory. Personal preferences (how you like code explained, your timezone, your preferred diff format) belong in `~/.claude/CLAUDE.md` or auto memory. Project facts (architecture decisions, team conventions, deployment procedures) belong in the project CLAUDE.md.

---

## How CLAUDE.md Survives Context Compaction

Context compaction is Claude Code's mechanism for handling long conversations — when the context window fills up, prior messages are summarized to make room. Conversation-level instructions ("for this session, always use async/await") do not survive compaction; they get summarized or dropped.

CLAUDE.md survives compaction because it is re-read from disk, not stored in conversation history. After compaction, Claude re-reads your CLAUDE.md as part of restoring its working context. Your project conventions, architecture notes, and command references are all back, even after a long multi-hour session.

This is a meaningful advantage over in-conversation instructions. Teams that rely on repeating instructions at the start of each session or after long gaps can instead encode those instructions in CLAUDE.md once and rely on compaction recovery. The file is your persistent anchor.

The corollary: anything that must persist across sessions should be in CLAUDE.md (or auto memory), not in the conversation. Don't tell Claude your preferred error handling pattern at the start of every session — write it down.

---

## CLAUDE.md vs AGENTS.md vs .cursorrules vs GEMINI.md

All four formats serve the same basic purpose — project-level AI coding instructions — but each targets a different tool. Here's the comparison:

| Format | Tool | Discovery | Scope | Limits |
|--------|------|-----------|-------|--------|
| CLAUDE.md | Claude Code | Hierarchical, multi-file, on-demand subdirs | Project + global + subdirectory | ~200 lines effective; 200K token window |
| AGENTS.md | OpenAI Codex / GPT-4o agents | Single file at repo root | Project-wide only | Varies by model |
| .cursorrules / .mdc | Cursor IDE | Single file or `.cursor/rules/*.mdc` with globs | Project or path-scoped | 500 lines recommended |
| GEMINI.md | Gemini Code Assist | Single file at repo root | Project-wide | Varies |
| .github/copilot-instructions.md | GitHub Copilot | Single file | Repository-wide | No stated limit |

The formats are similar enough that a well-written CLAUDE.md can serve as the source of truth, with minimal adaptation needed for other tools. The main differences are discovery hierarchy (Claude's multi-file layered approach is the most flexible) and path-scoping (Claude's `.claude/rules/` and Cursor's `.cursor/rules/*.mdc` are equivalent; others lack this).

If your team uses multiple AI tools, maintain CLAUDE.md as the canonical source and keep AGENTS.md / .cursorrules as lightweight references to it, or adapt the content as needed. Don't maintain independent versions — they'll drift.

---

## Common Mistakes: What NOT to Put in CLAUDE.md

Understanding what to leave out is as important as knowing what to include. These are the most common CLAUDE.md mistakes that degrade Claude's performance.

**Duplicating what Claude already knows.** "Follow REST conventions," "write clean code," "use meaningful variable names" — Claude knows these. Restating them wastes instruction budget. Only include things specific to your project or your deviations from common practice.

**Style enforcement without hooks.** If you need ESLint to run on every save, put it in a PostToolUse hook. Putting "always run ESLint after editing" in CLAUDE.md means Claude will try to remember to run it — sometimes it will, sometimes it won't. Hooks are deterministic; instructions are not.

**Growing without pruning.** CLAUDE.md tends to accumulate. Every team member adds their favorite rule; every incident generates a new constraint. Set a calendar reminder to audit your CLAUDE.md quarterly. Remove anything that hasn't changed Claude's behavior in the past month. A shorter, more focused file is always better.

**Secrets and credentials.** Never put API keys, passwords, or environment variable values in CLAUDE.md. It's committed to version control (usually), it's in Claude's context window, and it may be logged or transmitted. Secrets go in `.env` files (gitignored) or your secrets manager.

**Conflicting instructions across files.** If your root CLAUDE.md says "use tabs" and your `packages/frontend/CLAUDE.md` says "use spaces," Claude will apply whichever it read most recently in the current context. Audit your full CLAUDE.md hierarchy periodically to catch conflicts.

**Instructions that Claude ignores.** After making changes to CLAUDE.md, test the new instructions immediately. Ask Claude to describe its understanding of the convention you added, then have it write some code and verify it follows the rule. If Claude isn't following an instruction, it's usually too vague or buried in a long file.

---

## Quick Start: Your First CLAUDE.md in 5 Minutes

The minimum viable CLAUDE.md takes under five minutes to write and produces a noticeable improvement immediately. It requires four things: one paragraph describing what the project is and who uses it, the exact commands to start the dev server and run tests, five conventions that are specific to your project (not generic advice), and three things Claude should never do in this codebase. That's it. You don't need a perfect file on day one — the goal is to stop Claude from making the same mistakes it made in your last session. Start with what you had to correct most often last week. The "Never" section deserves at least half your initial effort: it's where you encode hard-won lessons. Every time you catch Claude doing something wrong, ask yourself whether that behavior would be prevented by a well-worded negative instruction. If yes, add it. The file grows organically from real friction. The template below gives you a skeleton; filling in the brackets honestly — based on your actual project, not an idealized version — is the only requirement. A specific CLAUDE.md that's occasionally incomplete is more effective than a generic one that tries to cover everything.

Here's a starter template:

Here's a starter template:

```markdown
# CLAUDE.md

## Project

[One paragraph: what the project does, who uses it, what stage it's in, and the main URL if live]

## Stack

- [Language + version]
- [Framework + version]
- [Database + version]
- [Test runner]

## Commands

- `[dev command]` — start dev server
- `[test command]` — run tests
- `[build command]` — build for production

NEVER run: [list commands that are dangerous in this repo]

## Conventions

- [Convention 1 — something specific to your project, not generic advice]
- [Convention 2]
- [Convention 3]
- [Convention 4]
- [Convention 5]

## Never

- [Thing Claude keeps doing wrong that you don't want]
- [Architectural pattern to avoid]
- [Security or compliance constraint]
```

Fill in the brackets honestly. The "Never" section especially benefits from real examples — think about the last three times Claude did something you had to correct, and put those corrections in writing. Real constraints beat abstract rules every time.

After saving the file, start a new Claude Code session and ask Claude to describe the project and its conventions. If Claude's description matches what you wrote, the file is working. If it misses something important, that section needs to be more explicit.

---

## FAQ

These are the questions developers ask most often when setting up CLAUDE.md for the first time. They cover cross-surface compatibility, multi-file behavior, instruction verification, documentation imports, and version control strategy — the practical decisions you'll face in the first week of using CLAUDE.md seriously. If your question isn't covered here, the fastest path to an answer is to test it: create a short CLAUDE.md with a specific, testable instruction ("always add a type annotation to every function parameter"), start a fresh Claude Code session, and verify that Claude's code output reflects the instruction. That test-and-verify loop is the most reliable way to calibrate your CLAUDE.md against Claude's actual behavior, since the effective instruction budget varies by project complexity, context window usage, and how deeply Claude is reasoning about the current task. The five questions below represent the most common setup challenges and decision points.

### Does CLAUDE.md work with Claude Code in VS Code and JetBrains, or only in the terminal?

CLAUDE.md works across all Claude Code surfaces — the terminal CLI, the VS Code extension, the JetBrains extension, and the web app at claude.ai/code. All surfaces use the same discovery and loading logic. The file you create for terminal use works automatically in IDE extensions.

### What happens if I have CLAUDE.md in both my home directory and my project root?

Both files load. The global `~/.claude/CLAUDE.md` applies first, then the project root CLAUDE.md adds to it. Instructions don't conflict unless they're directly contradictory — Claude merges them. If there is a conflict, the more specific (project-level) instruction generally takes precedence. Keep the global file short (personal preferences only) and let project files handle project specifics.

### How do I know if my CLAUDE.md instructions are actually being followed?

The fastest test: start a fresh Claude Code session (to ensure no cached state), then ask Claude directly: "Describe this project's conventions and what you should never do." Compare Claude's answer to your CLAUDE.md. Then have it write a short piece of code and check whether the conventions appear. Instructions that Claude doesn't follow are usually too vague or buried in a long file.

### Can I use CLAUDE.md to give Claude access to private documentation or internal wikis?

Sort of. You can use `@import` to include file contents inline, but CLAUDE.md can only reference files on the local filesystem. You can't reference URLs directly. For internal docs, export the relevant sections to Markdown files and import them. For large reference docs, prefer path-scoped rules in `.claude/rules/` so they load only when relevant.

### Should I commit CLAUDE.md to git, or keep it private?

Commit the project root CLAUDE.md to version control — it's most useful when the whole team benefits from it. For personal overrides (your machine-specific paths, draft notes, instructions you want but your team doesn't), use `.claude/CLAUDE.md` with a gitignore entry. The split between shared project config (tracked) and personal overrides (ignored) is the recommended pattern for teams.