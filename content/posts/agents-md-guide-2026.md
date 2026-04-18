---
title: "AGENTS.md Guide 2026: How to Write AI Agent Instructions for Every Tool"
date: 2026-04-18T06:11:17+00:00
tags: ["AGENTS.md", "AI coding", "developer tools", "Claude Code", "Cursor", "Codex"]
description: "AGENTS.md is the open standard for AI agent instructions that cuts agent runtime 28.6% and works across Cursor, Claude Code, Windsurf, and 20+ tools."
draft: false
cover:
  image: "/images/agents-md-guide-2026.png"
  alt: "AGENTS.md Guide 2026: How to Write AI Agent Instructions for Every Tool"
  relative: false
schema: "schema-agents-md-guide-2026"
---

AGENTS.md is a markdown file placed at your repository root that gives AI coding agents the project-specific instructions they need to work effectively — build commands, code style rules, testing conventions, and git workflow — without reading your entire codebase first.

## What Is AGENTS.md? The Open Standard Explained

AGENTS.md is an open standard for AI agent instructions, stewarded by the Agentic AI Foundation (AAIF) under the Linux Foundation alongside MCP (Anthropic) and Goose (Block). It is a plain markdown file placed at the root of a code repository that tells AI coding agents how your project works — how to build it, test it, what style conventions to follow, and where the important parts live. Unlike README.md, which explains a project to humans, AGENTS.md speaks directly to AI tools. As of 2026, over 60,000 open-source repositories contain the file, and 20+ AI coding agents — including OpenAI Codex, Cursor, Claude Code, Windsurf, Devin, Gemini CLI, and Aider — read it natively. The Agentic AI market is projected to reach $10.86 billion in 2026, with 57% of developers already reporting AI agents in production. AGENTS.md has become the connective tissue between human intent and machine execution. The key takeaway: it is a living operational manual for AI, not documentation for humans.

### How AI Agents Read AGENTS.md

When an AI coding agent starts a task, it looks for AGENTS.md in the current directory and walks up the directory tree. If multiple AGENTS.md files exist — as in a monorepo — the agent reads all of them, with the nearest file taking precedence for conflicting instructions. Codex CLI enforces a 32 KiB default size cap. Claude Code reads AGENTS.md as a fallback when no CLAUDE.md exists, which means a single AGENTS.md file can serve all tools without duplication. The agent injects the file's contents into its system prompt alongside its own instructions, which is why length and specificity matter — vague or bloated instructions dilute the signal.

## AGENTS.md vs CLAUDE.md vs .cursorrules vs copilot-instructions.md

AGENTS.md is not the only AI instruction file format in 2026, but it is the closest thing to a universal standard. Claude Code uses CLAUDE.md (and falls back to AGENTS.md). Cursor uses `.cursor/rules/` directory with individual `.mdc` files (previously `.cursorrules`). GitHub Copilot uses `.github/copilot-instructions.md` for repo-wide context plus scoped `.github/instructions/*.instructions.md` files with glob-pattern frontmatter (added July 2025). Windsurf uses `.windsurf/rules/` with a 6,000 character per-file limit and 12,000 character total cap. Maintaining all four formats separately means four times the maintenance burden and four times the drift risk — each file goes stale on a different timeline.

| File | Tool | Scope | Size Limit |
|------|------|-------|-----------|
| `AGENTS.md` | Codex, Cursor, Windsurf, Claude Code, 20+ | Universal | 32 KiB (Codex default) |
| `CLAUDE.md` | Claude Code only | Claude-specific features | None specified |
| `.cursor/rules/` | Cursor only | Per-file glob patterns | None specified |
| `copilot-instructions.md` | GitHub Copilot only | Repo-wide | None specified |
| `.windsurf/rules/` | Windsurf only | Directory-scoped | 6K chars/file, 12K total |

The recommended approach from DeployHQ and the AAIF: start with AGENTS.md as the single source of truth, then add tool-specific files only for features unique to that tool (for example, Claude Code's `/commands` or Cursor's semantic indexing triggers).

## Why AGENTS.md Is Becoming the Universal Standard

AGENTS.md has reached critical mass as the default AI coding instruction format because it solves the multi-tool maintenance problem that most development teams hit by Q2 2026. When a team uses Claude Code for exploratory tasks, Codex for CI-integrated generation, and Cursor for IDE-based editing, maintaining three separate instruction files means three separate files to keep accurate, three divergence points where one tool's file contradicts another, and three times the cognitive overhead during onboarding. AGENTS.md's Linux Foundation governance gives it credibility similar to how package.json became the universal dependency manifest regardless of which package manager you use. The 28.6% runtime reduction and 16.6% token reduction reported in Princeton research (98.6s → 70.3s, 2,925 → 2,440 tokens) come from any compliant tool reading the same file. That cost reduction compounds across every agent invocation in your CI/CD pipeline.

### Claude Code and AGENTS.md

Claude Code has native AGENTS.md support and reads it as a fallback when no CLAUDE.md file exists. In practice, a team can write one AGENTS.md and get compatible behavior across Claude Code, Codex, and Cursor without any duplication. Claude Code's system prompt uses approximately 50 of the ~150-200 instructions frontier LLMs can reliably follow, which leaves 100-150 instruction slots for your AGENTS.md content — well within the recommended 300-line limit.

## How to Write an Effective AGENTS.md: The 6 Essential Sections

An effective AGENTS.md file consists of six categories of information that AI agents actually need: build and test commands, code style rules, project structure overview, testing instructions, git workflow requirements, and operational boundaries (what the agent must never do). Research from ETH Zurich (February 2026) tested four agents on 138 real-world Python tasks and found that human-written AGENTS.md files improved task success rates by 4% on average. The same study found LLM-generated AGENTS.md files reduced success by 3% and increased costs by 20%+. The difference is specificity — human-written files include exact commands, actual file paths, and non-obvious constraints that an LLM generating a template would guess wrong. The sections below follow the priority order from DeployHQ's 2026 survey of professional engineering teams.

### Section 1: Build and Test Commands

The most critical section. Write the exact commands an agent needs to build, test, lint, and start the project — not descriptions of what they do. An agent that guesses wrong here wastes the most expensive part of its context: the action phase.

```
# Commands
- Build: `npm run build`
- Test: `npm test -- --runInBand` (always run in band, parallel tests cause race conditions in this repo)
- Lint: `npm run lint:fix` (auto-fixes; never run `lint` without `:fix`)
- Type check: `npx tsc --noEmit`
- Dev server: `npm run dev` (port 3000; hot reload enabled)
```

### Section 2: Code Style Rules

List conventions that aren't enforced by your linter. Things like naming patterns, file organization within modules, import ordering philosophy, and patterns the team has explicitly rejected.

```
# Code Style
- TypeScript strict mode; no `any` unless explicitly commented with reason
- Named exports only; no default exports except for Next.js page components
- Prefer `const` over `let`; never `var`
- Test files co-located next to source files, not in separate `__tests__/` directories
- Error messages must include the function name: `throw new Error('fetchUser: userId is required')`
```

### Section 3: Project Structure

Not a full file tree — just the non-obvious organizational decisions an agent wouldn't infer from reading the directory listing.

```
# Project Structure
- `src/lib/` — shared utilities; no business logic
- `src/features/` — feature modules; each contains its own components, hooks, and tests
- `src/app/` — Next.js App Router pages; thin wrappers only
- `prisma/migrations/` — never edit manually; always use `prisma migrate dev`
- `public/generated/` — build artifacts; never commit
```

### Section 4: Testing Instructions

Specify test runner behavior, required coverage thresholds, what to mock, and what must never be mocked.

### Section 5: Git Workflow

Commit message format, branch naming convention, and PR requirements.

### Section 6: Operational Boundaries

What the agent must never do. This section is the safety net that prevents the most expensive mistakes.

```
# Boundaries
- Never modify `prisma/schema.prisma` without explicit human approval
- Never run `git push` — only stage and commit; a human reviews before pushing
- Never delete files; use `git rm` only with human confirmation
- Never edit `.env` or `.env.local` files
```

## The 300-Line Rule: Understanding LLM Instruction Limits

The 300-line limit for AGENTS.md comes from understanding how frontier LLMs process instructions under real-world conditions. Frontier models like Claude and GPT-5 can reliably follow approximately 150-200 discrete instructions when those instructions are present in the system prompt alongside the model's own built-in instructions. Claude Code's system prompt already occupies approximately 50 of those slots, leaving roughly 100-150 slots for AGENTS.md content. At an average of 8-10 words per instruction line, 300 lines maps to roughly 2,400-3,000 words — which fills the remaining instruction budget without overflow. Beyond that threshold, agents begin selectively ignoring instructions, with later-listed rules more likely to be dropped. DeployHQ's 2026 study found files over 500 lines consistently underperformed 200-line files on instruction-following accuracy, particularly for rules listed after line 300. The practical rule: if you cannot fit your AGENTS.md in 300 lines, you have too many rules, not a file length problem.

### What to Leave Out

Exclude anything a competent linter already enforces (semicolons, indentation, import sorting). Exclude anything documented in your README that an agent could read if needed. Exclude aspirational guidelines — only include rules you want agents to follow on every action. Exclude obvious language idioms that any senior developer knows.

## Monorepo Strategy: Nested AGENTS.md Files and the 88-File Example

OpenAI's Codex repository uses 88 AGENTS.md files across its monorepo structure — one at the root for global rules and one in each package directory for package-specific overrides. This is not unusually complex; it's the correct architecture for monorepos. The way nested AGENTS.md files work: agents read all relevant files from the current working directory up to the repository root. Rules in the nearest file take precedence when there is a conflict. This means a `packages/api/AGENTS.md` can override the root's testing command without affecting the frontend package's behavior. For a monorepo with 10 packages, this means 10 focused 50-line AGENTS.md files rather than one 500-line root file that violates the 300-line rule and contains irrelevant rules for every sub-agent invocation. The practical architecture for a typical Node.js monorepo looks like this: root AGENTS.md covers commit format, global linting, and security boundaries; each package's AGENTS.md covers its own build command, test command, and local file conventions.

```
/AGENTS.md          ← global: commit format, security boundaries, CI commands
/packages/api/AGENTS.md    ← api: build commands, database migration rules
/packages/web/AGENTS.md    ← web: component conventions, test requirements
/packages/shared/AGENTS.md ← shared: export rules, no side effects policy
```

## What the Research Says: ETH Zurich Study on Human vs LLM-Written Context Files

The ETH Zurich study (February 2026, arxiv 2602.11988) is the most rigorous published research on AGENTS.md effectiveness to date. The researchers tested four agents — Claude 3.5 Sonnet, Codex GPT-5.2, GPT-5.1 mini, and Qwen Code — on 138 real-world Python tasks from niche repositories (deliberately excluding SWE-bench repos to avoid benchmark contamination). The findings split sharply along authorship lines. LLM-generated AGENTS.md files reduced task success rates by 3% and increased inference costs by 20% or more — agents followed the instructions but ran more tests, searched more files, and executed more grep commands than without the file. Human-written AGENTS.md files improved success rates by 4% on average but raised costs by up to 19% due to the same thoroughness effect. The researchers concluded: omit LLM-generated context files entirely; limit human-written files to non-inferable details only (specific tooling, custom build commands, non-obvious constraints). Developer community response was skeptical: critics noted that a 4% gain on niche public repos likely understates gains on private enterprise codebases with higher-quality AGENTS.md files.

### Princeton Research vs ETH Zurich: Why the Numbers Differ

Princeton research cited by morphllm.com shows 28.6% runtime reductions with human-written AGENTS.md (98.6s → 70.3s runtime, 2,925 → 2,440 tokens). ETH Zurich shows 4% success improvement but higher costs. The difference: Princeton measured time-to-completion and token consumption; ETH Zurich measured task success rate. An agent that finishes faster but is equally likely to succeed shows Princeton's numbers. An agent that is slightly more likely to succeed but takes more actions shows ETH Zurich's numbers. Both can be true simultaneously for different task types.

## Common Anti-Patterns: Why Most AGENTS.md Files Fail

Most AGENTS.md files fail for one of four reasons: they are too long (over 500 lines), they duplicate README content, they were auto-generated by an LLM and contain guessed commands, or they contain vague instructions that aren't actionable. The "too long" failure mode is the most common in 2026. Teams add instructions every time an agent misbehaves, never pruning, until the file becomes a 600-line novel that violates the 300-line instruction budget. The result is selective instruction-following: agents reliably execute the first 100-150 lines and probabilistically ignore the rest. The "duplicate README" anti-pattern stems from confusing audiences. README explains what the project does to a new human contributor. AGENTS.md tells an AI agent what to do when editing code. Overlap should be near zero. The "LLM-generated" anti-pattern produces files that look professional but contain wrong commands, hallucinated file paths, and generic style rules that don't reflect your actual codebase.

| Anti-Pattern | Symptom | Fix |
|---|---|---|
| Too long (>500 lines) | Agents ignore late-file rules | Audit and prune; split into nested files |
| Duplicate README | Agents read irrelevant context | Remove anything also in README |
| LLM-generated | Wrong commands, hallucinated paths | Write from scratch with actual terminal output |
| Vague instructions | Agents interpret inconsistently | Replace descriptions with exact commands |
| No boundaries section | Agents take dangerous actions | Add explicit "Never do X" rules |

## Step-by-Step: Creating Your First AGENTS.md from Scratch

Creating an effective AGENTS.md from scratch takes about 30 minutes if you work through these steps in order rather than writing top-to-bottom. Start by running your actual build, test, lint, and type-check commands in a terminal and pasting the exact commands — including flags — into the Commands section. Do not describe them; copy them verbatim. Next, read your linter config and list only the rules that are NOT enforced by the linter (the linter handles the rest). Then draw the directory structure that confuses new team members — not the full tree, just the non-obvious parts. Write the testing section by answering: what do agents mock, what must never be mocked, and what's the coverage threshold? Write the git section by looking at your last 20 commit messages and distilling the pattern. Write the Boundaries section by listing the last three times an AI agent did something you had to revert — those are your boundaries.

```
# AGENTS.md

# Commands
- Install: `npm ci`
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint:fix`
- Type check: `npx tsc --noEmit`

# Tech Stack
- Next.js 15 (App Router), TypeScript 5.4, Prisma 5, PostgreSQL
- Testing: Vitest + React Testing Library

# Project Structure
- `src/app/` — App Router pages (thin wrappers)
- `src/features/` — Feature modules (co-located components, hooks, tests)
- `src/lib/` — Shared utilities (no business logic)

# Code Style
- No `any`; no default exports (except Next.js pages)
- Co-locate tests with source files

# Testing
- Unit tests for all utility functions in `src/lib/`
- Integration tests for API routes using real database (no mocks)
- Never mock Prisma client

# Git
- Commits: `type(scope): message` (conventional commits)
- Branch: `feature/ticket-description` or `fix/ticket-description`

# Boundaries
- Never modify `prisma/schema.prisma` without human approval
- Never run `git push`
- Never edit `.env` files
```

## Tool-Specific Additions: When to Add CLAUDE.md or .cursor/rules/

Tool-specific instruction files extend AGENTS.md for features unique to a single tool — they do not replace it or duplicate it. Add a CLAUDE.md file when you need Claude Code-specific features that have no equivalent in AGENTS.md: custom `/commands`, MCP server configuration, specific memory instructions for multi-turn sessions, or Claude-specific operator-level behaviors. Add `.cursor/rules/` when you need file-type-specific rules scoped by glob pattern (apply TypeScript rules only to `.ts` files, apply Python rules only to `*.py` files) that AGENTS.md's flat structure can't express without ambiguity. Add `.windsurf/rules/` only if you have Windsurf-specific workflow needs — Windsurf's 6,000 character per-file and 12,000 character total limits mean you will need to trim aggressively anyway. Add `.github/copilot-instructions.md` or scoped `.github/instructions/*.instructions.md` files when GitHub Copilot needs repo-specific context not covered by AGENTS.md. The maintenance principle: AGENTS.md is canonical. Tool-specific files extend it, never duplicate it. If a rule belongs in AGENTS.md, it must not be copied to CLAUDE.md — update AGENTS.md and let Claude Code read it as fallback. Drift between these files is a silent failure mode: agents get contradictory instructions and pick whichever they encounter first.

## Maintaining Your AGENTS.md: Update Triggers and Living Document Strategy

An AGENTS.md file that was accurate in January becomes a liability by April if not maintained. The most effective maintenance strategy is trigger-based, not calendar-based. Update your AGENTS.md immediately when: you add or change a build command, you adopt a new testing library or change mock strategy, you change commit message format, you add a new major directory or restructure the project, or an AI agent takes an action you had to revert (that revert is evidence of a missing boundary). A useful heuristic: every time you onboard a new developer and they ask a question that isn't in the README, that answer belongs in AGENTS.md. Questions from humans about "how do I build this?" are the same questions AI agents would ask if they could. The goal is an AGENTS.md that makes a new agent as productive on day one as a developer who has been on the project for a week.

---

## FAQ

Here are the five most common questions developers ask when setting up AGENTS.md for the first time in 2026, with direct answers based on published research and production usage across 60,000+ open-source repositories. AGENTS.md is the open standard for AI coding agent instructions, stewarded by the Agentic AI Foundation under the Linux Foundation, and supported by 20+ tools including Codex, Cursor, Claude Code, Windsurf, and Gemini CLI. The research is clear: human-written files improve agent success rates by ~4% while LLM-generated files hurt performance by 3% or more. The Agentic AI market is projected at $10.86 billion in 2026, and 57% of developers already report agents in production — AGENTS.md is the fastest path to consistent agent behavior across all tools in your stack. These answers address the most common setup mistakes — length, authorship, tool compatibility, and monorepo structure — that developers get wrong on the first attempt.

### What is AGENTS.md and why do I need it?

AGENTS.md is a markdown file at your repository root that gives AI coding agents project-specific instructions: build commands, code style rules, testing requirements, and operational boundaries. You need it because AI agents without project context guess — and wrong guesses waste tokens, break tests, or create work you have to revert. A well-written AGENTS.md reduces AI agent runtime by up to 28.6% (Princeton research) and improves task success rates by approximately 4% (ETH Zurich).

### Which AI tools support AGENTS.md in 2026?

Over 20 AI coding tools support AGENTS.md natively, including OpenAI Codex, Cursor, Claude Code, Windsurf, Devin, Gemini CLI, Aider, VS Code AI extensions, and more. Claude Code reads AGENTS.md as a fallback when no CLAUDE.md exists, making it the most broadly compatible single instruction file format available.

### How long should an AGENTS.md file be?

Keep AGENTS.md under 300 lines. Frontier LLMs can reliably follow approximately 150-200 discrete instructions. Claude Code's system prompt uses ~50 slots, leaving roughly 100-150 slots for your file. Files over 500 lines cause agents to selectively ignore late-listed rules. If your instructions exceed 300 lines, split them into nested AGENTS.md files per directory rather than adding to the root file.

### Should I generate my AGENTS.md with an LLM?

No. ETH Zurich research (2026) found that LLM-generated AGENTS.md files reduced task success rates by 3% and increased costs by 20%+, while human-written files improved success rates by 4%. LLMs generate plausible-looking but often wrong commands and hallucinated file paths. Write your AGENTS.md from actual terminal output and real codebase knowledge.

### How does AGENTS.md work in a monorepo?

Place AGENTS.md files at multiple levels: a root file for global rules (commit format, security boundaries, CI commands) and per-package files for package-specific rules (build commands, local conventions). Agents read all files from the current directory up to the repo root, with the nearest file taking precedence for conflicts. OpenAI's Codex repository uses 88 AGENTS.md files across its monorepo — one per significant directory — as the reference implementation of this pattern.
