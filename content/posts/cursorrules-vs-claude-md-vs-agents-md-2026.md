---
cover:
  alt: .cursorrules vs CLAUDE.md vs AGENTS.md 2026
  image: /images/cursorrules-vs-claude-md-vs-agents-md-2026.png
  relative: false
date: 2026-04-17 21:00:16+00:00
description: 'Compare AI coding config formats: .cursorrules, CLAUDE.md, AGENTS.md,
  .cursor/rules. Which format best fits your team in 2026?'
draft: false
schema: schema-cursorrules-vs-claude-md-vs-agents-md-2026
tags:
- cursorrules vs claude.md vs agents.md
- AI coding config
- CLAUDE.md
- AGENTS.md
- cursor rules
title: '.cursorrules vs CLAUDE.md vs AGENTS.md 2026: Which AI Config File Should You
  Use?'
---

If your AI coding agent keeps making the same mistakes — using the wrong import style, ignoring your test conventions, or not knowing which files to avoid — the fix is a config file, not a better prompt. In 2026, three formats dominate: `.cursorrules` for Cursor-only teams, `CLAUDE.md` for Claude Code users who want the most features, and `AGENTS.md` for teams using multiple AI tools. Here is how to choose.

## The AI Coding Config Landscape in 2026

The AI coding configuration landscape in 2026 has fragmented into nine distinct formats across six major tools — a direct result of every AI coding product independently solving the same problem of how to give the AI persistent, project-specific context. The formats are: `.cursorrules` (Cursor, deprecated but still supported), `.cursor/rules/*.mdc` (Cursor's current format with four activation modes), `CLAUDE.md` (Claude Code with five-layer hierarchy), `AGENTS.md` (multi-tool universal standard, Linux Foundation stewardship), `copilot-instructions.md` (GitHub Copilot), `.windsurfrules` (Windsurf), `GEMINI.md` (Google Gemini CLI), `.github/instructions/*.instructions.md` (GitHub Copilot organization-level, GA April 2026), and `AGENTS.override.md` (Codex CLI local overrides). All converge on the same core concept — Markdown files in your repository that give the AI instructions it reads before every session — but they differ significantly in hierarchy depth, cross-file imports, activation modes, tooling ecosystem, and maintenance trajectory. If you use one AI tool, pick its native format. If you use three or more, AGENTS.md is the closest thing to a universal standard, adopted by 60,000+ open-source projects and backed by the Linux Foundation's Agentic AI Foundation.

## .cursorrules — The Original: Simple, Popular, but Cursor-Only

`.cursorrules` is the format that popularized the concept of AI coding configuration files, and it still has the largest community ecosystem in 2026 with over 2,000 community-contributed rule files in the awesome-cursorrules collection. The format is a single flat Markdown file placed in your project root that Cursor reads at the start of every session. It has no hierarchy, no cross-file imports, no global configuration, and no formal specification — just plain Markdown prose that the AI reads as context. The simplicity that made it popular is also its structural limitation: if you work on five projects, you maintain five separate `.cursorrules` files with no shared base, and if you switch to a different AI tool, none of your rules transfer. More significantly, Cursor itself deprecated `.cursorrules` in favor of `.cursor/rules/*.mdc` files with four activation modes — the old format still works but is no longer the recommended approach. Despite these limitations, `.cursorrules` remains a valid choice for solo developers who use only Cursor and want to get started in minutes without learning hierarchy systems. For teams or multi-tool users, it is the wrong foundation to build on in 2026.

### .cursor/rules/*.mdc — The Cursor Evolution

Cursor's current format replaces the single `.cursorrules` file with multiple `.mdc` files inside a `.cursor/rules/` directory, each with a YAML frontmatter block that specifies its activation mode. The four modes are: **Always On** (loaded every session regardless of context), **Auto Attached** (loaded when files matching a glob pattern are in context), **Model Decision** (the AI decides whether to load the rule based on the current task), and **Manual** (loaded only when explicitly referenced with `@ruleName`). This activation system solves the context window problem: instead of loading your entire rule library on every task, you load only the rules relevant to the current work. A backend developer editing Django models loads the Django rules; a frontend developer editing React components loads the React rules. The practical downside is fragmentation — `.cursor/rules/*.mdc` files are Cursor-proprietary, so switching to Claude Code or Windsurf means starting your config from scratch.

## CLAUDE.md — The Deepest Feature Set

CLAUDE.md is Claude Code's native configuration format and has the most sophisticated feature set of any AI coding config format in 2026. It supports a five-layer hierarchy that merges configuration from multiple locations: `~/.claude/CLAUDE.md` (global, applies to all projects), `./CLAUDE.md` (project root), `subdirectory/CLAUDE.md` files (apply only when that directory is in context), explicit `@import` statements that pull in additional files, and user-specific local overrides. This hierarchy means you can define organization-wide conventions once in your global CLAUDE.md, project-specific patterns in the repo root, and component-specific rules in subdirectory files — all automatically merged without duplication. Claude Code reads the merged result before every session and loads it into its context window. The feature that distinguishes CLAUDE.md most from competitors is its integration with Claude Code's hooks system: while CLAUDE.md handles advisory instructions (what the AI should do), `.claude/settings.json` hooks handle deterministic enforcement (what the system will do regardless of AI decisions, such as running a linter before every commit or refusing git push without passing tests). Major projects using CLAUDE.md include Next.js (138K GitHub stars), LangChain (128K), Excalidraw (118K), and Deno (106K).

### The @import System for Large Projects

CLAUDE.md's `@import` syntax allows you to split your configuration across multiple files and import them into a master CLAUDE.md, which is critical for large projects where a single monolithic config file becomes unwieldy. A common pattern is to maintain a base `AGENTS.md` with tool-agnostic universal conventions, then have your `CLAUDE.md` import it and add Claude-specific enhancements:

```markdown
# CLAUDE.md

@import AGENTS.md

### Claude Code-Specific Instructions

When using bash tools, prefer the Bash tool over running shell commands inline.
Always use TodoWrite to track multi-step tasks.
```

This approach means your universal rules live in one place (`AGENTS.md`), your Claude-specific rules augment them in `CLAUDE.md`, and you avoid duplicating content across two files. HumanLayer uses this pattern and keeps their entire CLAUDE.md under 60 lines by importing shared conventions rather than repeating them.

## AGENTS.md — The Universal Standard

AGENTS.md is the closest thing to a universal AI coding configuration standard in 2026. It is stewarded by the Linux Foundation under the Agentic AI Foundation, supported by 60+ tools including Codex CLI, Cursor, Claude Code, GitHub Copilot, Windsurf, Aider, Gemini CLI, Zed, Warp, Devin, and JetBrains Junie, and adopted by 60,000+ open-source projects. The format is intentionally simple: a Markdown file placed in your project root (or in subdirectories for scoped rules) that every supporting tool reads before starting work. Major projects that chose AGENTS.md over CLAUDE.md include n8n (178K GitHub stars), awesome-go (167K stars), LangFlow (145K stars), llama.cpp (97K stars), and Bun (82K stars) — notably these are projects with large contributor bases that need instructions to work regardless of which AI tool each contributor uses. The AGENTS.md community has 300+ example configurations available. OpenAI's own Codex repository uses 88 separate AGENTS.md files distributed across its directory structure, demonstrating that the format scales to complex monorepos. The tradeoff versus CLAUDE.md is features: AGENTS.md has no `@import` syntax, no hooks integration, and no global configuration outside the repository. What it has is universality.

### AGENTS.md Discovery and Hierarchy

AGENTS.md supports a simple directory hierarchy: the AI tool walks from the repository root down to the current working directory, loading any AGENTS.md files it finds along the way and merging them in order. More specific (deeper) rules take precedence over more general (root-level) rules. Codex CLI extends this with `AGENTS.override.md` for local per-developer overrides that are not committed to the repository, and it enforces a 32 KiB (32,768 byte) per-file limit to prevent context window abuse. The discovery algorithm — walk the tree, load and merge — is simple enough that tool authors implement it consistently across 60+ tools, which is the key to its cross-tool reliability.

## Head-to-Head Comparison

Choosing between these formats is fundamentally a question of coverage versus features. AGENTS.md wins on coverage — 60+ tools, 60,000+ open-source project adoptions, and Linux Foundation stewardship make it the safest long-term bet for any team that might add a second AI tool. CLAUDE.md wins on features — five-layer hierarchy, `@import`, hooks integration, and global configuration make it the most capable format for Claude Code teams who want maximum control over AI behavior. `.cursorrules` wins on nothing in 2026: its community ecosystem is large but it is deprecated in favor of `.cursor/rules/*.mdc`, and Cursor's new format with four activation modes is strictly superior for Cursor users.

| Feature | .cursorrules | CLAUDE.md | AGENTS.md | .cursor/rules |
|---------|-------------|-----------|-----------|---------------|
| Tool support | Cursor only (deprecated) | Claude Code native | 60+ tools | Cursor only |
| Hierarchy | None | 5 layers + @import | Directory tree | Per-file activation |
| Global config | No | Yes (~/.claude/) | No | No |
| Community examples | 2,000+ | 500+ | 300+ | Growing |
| Linux Foundation backing | No | No | Yes | No |
| Hooks/enforcement | No | Yes (.claude/settings.json) | No | No |
| Formal spec | No | Partial | Yes | Partial |
| Status | Deprecated | Active, recommended | Active, recommended | Active, recommended |
| Best for | Cursor solo devs | Claude Code teams | Multi-tool teams | Cursor teams |

## The Instruction Budget Problem

The most underappreciated constraint in AI coding configuration is the instruction budget. Frontier LLMs can reliably follow approximately 150–200 distinct instructions before adherence degrades — additional instructions compete with each other for attention and the probability of any single rule being followed reliably decreases. Claude Code's own system prompt consumes roughly 50 of those slots before your CLAUDE.md is even read. This means a 600-line CLAUDE.md does not give you 600 instructions — it gives you perhaps 100–150 reliable ones, with the remaining lines reducing the reliability of everything else. The practical implication: ruthless prioritization is more important than comprehensive coverage. A CLAUDE.md with 40 high-priority, non-obvious rules will produce better AI behavior than one with 200 rules covering everything. HumanLayer's approach of keeping CLAUDE.md under 60 lines is not minimalism for its own sake — it is calibration to the instruction budget. The recommended ceiling for most projects is 200–300 lines, with larger projects using `@import` to modularize rather than cramming everything into one file.

### Token Visibility and Context Costs

Beyond the instruction budget, config files consume token context on every session — and context is not free. A 500-line CLAUDE.md costs approximately 2,000–3,000 input tokens on every Claude Code session, which adds up to meaningful API cost at team scale. The token cost consideration pushes toward the same conclusion as the instruction budget: shorter is better. tokencentric.app's benchmark of 100–200 lines per config file reflects both constraints simultaneously.

## Real-World Adoption: How Major Projects Choose

The split between CLAUDE.md and AGENTS.md adoption in major open-source projects reveals a clear pattern: projects with a single dominant contributor base using specific tools tend toward CLAUDE.md; projects with large, diverse contributor bases needing tool-agnostic instructions tend toward AGENTS.md. Next.js (138K stars, primarily Vercel team contributors using Claude Code) chose CLAUDE.md. n8n (178K stars, 700+ contributors using diverse AI tools) chose AGENTS.md. Deno (106K stars, small core team with Claude Code preference) chose CLAUDE.md. llama.cpp (97K stars, community-driven with contributors across all editors and tools) chose AGENTS.md. The decision logic: if your team is small and aligned on one AI tool, pick that tool's native format for maximum features. If your project has diverse contributors who use different tools, AGENTS.md ensures everyone's AI tool reads the same base conventions.

## Hooks vs Instructions: Deterministic vs Advisory

One of the most important conceptual distinctions in AI coding configuration is the difference between hooks (deterministic enforcement) and instructions (advisory guidance). CLAUDE.md instructions tell the AI what to do — but the AI can choose to deviate, especially under ambiguous conditions or when the instruction conflicts with another instruction. Hooks in `.claude/settings.json` are executed by the system, not the AI — they run regardless of AI decisions and cannot be overridden by the AI's judgment. The rule: use instructions for stylistic preferences and workflow conventions; use hooks for anything that must be enforced without exception. Examples: "prefer functional components over class components" belongs in CLAUDE.md as an instruction. "Run ESLint before every commit" belongs in `.claude/settings.json` as a hook. "Never push to main" belongs as a hook. "Write tests for new functions" is advisory enough to be an instruction.

## The Linter Principle: What NOT to Put in Your Config File

A principle that experienced AI coding practitioners converge on independently: never use AI config files to enforce what a linter or formatter can enforce deterministically. If your project uses Prettier for code formatting and ESLint for code style, those tools enforce their rules on every file save and every CI run with 100% reliability. Adding the same rules to your CLAUDE.md gives you maybe 80% reliability (AI adherence) instead of 100%, while consuming instruction budget slots that could be used for non-automatable conventions. The test for whether a rule belongs in your config file: "Can a tool enforce this automatically?" If yes, use the tool. If no (architectural constraints, domain-specific conventions, non-obvious gotchas, workflow patterns), put it in your config file. This principle dramatically reduces config file size and increases the reliability of the rules that remain.

## Migration Paths: .cursorrules → CLAUDE.md → AGENTS.md

For teams evolving their AI toolchain, here are the practical migration steps.

**From .cursorrules to CLAUDE.md:**
1. Copy `.cursorrules` content to `CLAUDE.md` in project root
2. Add `## Bash Commands` section with project-specific shell commands
3. Add `## Code Style` section for conventions not covered by your linter
4. Remove any rules that Prettier/ESLint already enforces
5. Create `~/.claude/CLAUDE.md` for cross-project personal conventions
6. Keep `CLAUDE.md` under 200 lines; use `@import` for larger projects

**From CLAUDE.md to AGENTS.md (adding multi-tool support):**
1. Extract tool-agnostic rules from `CLAUDE.md` into a new `AGENTS.md`
2. Update `CLAUDE.md` to `@import AGENTS.md` at the top
3. Move Claude Code-specific instructions (hooks references, tool names) back to `CLAUDE.md`
4. Test that both files load correctly in Claude Code
5. Verify AGENTS.md is read by your secondary AI tool (Cursor, Copilot, etc.)

**From .cursorrules to AGENTS.md directly:**
1. Rename `.cursorrules` to `AGENTS.md`
2. Remove Cursor-specific syntax if any
3. Add your secondary AI tool's specific instructions to its native config file (`CLAUDE.md`, `.windsurfrules`, etc.)
4. Each tool-specific file should `@import AGENTS.md` (where supported) or duplicate the universal rules

## Multi-Tool Strategy: Avoiding the 15-Config-File Problem

A developer using three AI tools (Cursor, Claude Code, GitHub Copilot) across five projects faces a potential 15-config-file maintenance burden — nine if you are disciplined, fifteen if you are not — when each project requires separate configuration for each tool. According to tokencentric.app's analysis of multi-tool developer workflows, config file fragmentation is the top complaint among developers who use three or more AI coding tools in parallel, with the average developer spending 45 minutes per week synchronizing instructions across tool-specific config files. The solution is a canonical source-of-truth architecture that prevents this explosion while preserving tool-specific capabilities.

A developer using three AI tools (Cursor, Claude Code, GitHub Copilot) across five projects faces a potential 15-config-file maintenance burden if each project has separate configs for each tool. The solution is a single canonical source of truth (AGENTS.md) plus thin tool-specific adapters. The canonical AGENTS.md contains universal rules: project architecture, key commands, test patterns, workflow conventions. Each tool-specific file contains only what cannot be in AGENTS.md: tool-specific syntax, tool-specific features, and tool-specific performance tuning. Any rule change that applies universally is made in AGENTS.md once; changes that are truly tool-specific go in the adapter. This reduces the 15-file maintenance burden to 5 canonical files plus lightweight adapters that rarely change.

## FAQ

Choosing between `.cursorrules`, `CLAUDE.md`, and `AGENTS.md` is a genuine architectural decision that affects every developer on your team and every AI tool in your workflow. The questions below address the most common decision points, based on the adoption data and feature comparisons from the research underlying this guide. The format landscape is still evolving rapidly — Cursor's deprecation of `.cursorrules` in favor of `.mdc` files, GitHub Copilot's organization-level instructions going generally available in April 2026, and the Linux Foundation's stewardship of AGENTS.md all happened within the last six months. The right answer in 2026 may look different in 2027 as the category converges, but the core decision framework — tool coverage, hierarchy needs, team size, and enforcement requirements — will remain stable regardless of which specific format wins. When in doubt, start with AGENTS.md as your base and layer tool-specific files on top.

### Is .cursorrules still worth using in 2026?

Not for new projects. Cursor deprecated `.cursorrules` in favor of `.cursor/rules/*.mdc` files with four activation modes, which gives you more control over when rules apply. Existing `.cursorrules` files still work, but you should migrate to `.mdc` format to access activation modes and stay on the supported path. If you use only Cursor, `.cursor/rules/*.mdc` is the right choice. If you use multiple tools, AGENTS.md should be your base.

### Should I maintain both CLAUDE.md and AGENTS.md?

Yes, if you use Claude Code alongside other AI tools. The recommended pattern: `AGENTS.md` contains universal, tool-agnostic rules; `CLAUDE.md` imports `AGENTS.md` with `@import AGENTS.md` and adds Claude-specific instructions (hooks references, Claude Code-specific workflow steps). This way universal rules are maintained once and Claude Code gets its full feature set without duplication.

### How long should my AI config file be?

Target 200 lines or fewer for the effective range. Frontier LLMs reliably follow 150–200 instructions; Claude Code's system prompt uses ~50 slots before your file is loaded, leaving roughly 100–150 reliable instruction slots. HumanLayer keeps theirs under 60 lines. The ceiling for most projects is 300 lines. Use `@import` to modularize larger projects rather than exceeding this limit.

### What should I never put in my AI config file?

Anything a linter or formatter enforces automatically. If ESLint catches it, Prettier formats it, or your CI pipeline rejects it, do not duplicate that rule in your AI config file — you get lower reliability (AI adherence vs tool enforcement) while wasting instruction budget. Config files should contain non-automatable knowledge: project-specific architectural decisions, non-obvious conventions, domain context, workflow patterns, and gotchas that aren't visible from the code itself.

### Which format will win long-term?

AGENTS.md has the strongest structural position: Linux Foundation stewardship, 60+ tool support, and adoption by 60,000+ open-source projects give it the network effects of an emerging standard. The analogy is `.editorconfig` — once enough tools supported it, the question shifted from "will editors adopt it?" to "which version of the spec are we on?" CLAUDE.md will remain the superior choice for Claude Code teams who need its advanced features (hooks, `@import`, five-layer hierarchy). The most likely outcome is both coexist: AGENTS.md as the universal base, CLAUDE.md and `.cursor/rules/*.mdc` as feature-rich tool-specific layers above it.