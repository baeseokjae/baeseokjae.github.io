---
title: "I Still Don't Understand Why AI Agents Need Skills — Here's the Real Answer"
date: 2026-08-04T15:42:44+00:00
tags:
  - ai agent skills
  - claude code skills
  - codex cli skills
  - agent skills framework
  - progressive disclosure ai agents
  - context window management agents
  - agent skill security
  - openclaw skills marketplace
  - ai agent instructions
  - AGENTS.md vs skills
description: "AI agents need skills because dumping all instructions into one file pollutes the context window. Skills use progressive disclosure to load only relevant knowledge, improving performance and security."
draft: false
cover:
  image: "/images/ai-agents-need-skills-ask-hn-2026.png"
  alt: "I Still Don't Understand Why AI Agents Need Skills — Here's the Real Answer"
  relative: false
schema: "schema-ai-agents-need-skills-ask-hn-2026"
---

AI agents need skills because a single monolithic instruction file like `AGENTS.md` forces the entire knowledge base into the agent's context window on every interaction, degrading performance, increasing cost, and reducing accuracy. Skills solve this by using **progressive disclosure** — the agent sees only a skill's name and description upfront, and loads the full instructions only when it decides the skill is relevant. This architectural pattern, borrowed from how human experts organize knowledge, is the difference between handing someone a 500-page manual and letting them ask for the chapter they need.

## The Question That Started It All

In mid-2026, a Hacker News user posting as `skeptic_ai` asked a question that resonated with hundreds of developers: *"I still don't understand why AI agents need skills. Couldn't I just have an AGENTS.md that points to folders of .md files?"*

The post earned 17 points and 25+ comments — significant engagement for a technical question on HN. The skepticism was genuine and well-reasoned. If an AI agent can already read files, why add a whole skill abstraction layer? Why not just organize your Markdown files in folders and let the agent browse them?

It's a fair question, and it deserves a real answer — not marketing fluff. Let's break down exactly what skills are, why they exist, and whether the skeptic was right.

## What Are Skills, Really?

At their core, AI agent skills are **lazy-loaded, progressively-disclosed Markdown documents with structured metadata**. The most widely adopted format — pioneered by Anthropic's Claude Code — uses YAML front-matter (name, description, optional allowed-tools) followed by a Markdown body containing the actual instructions.

Here's what a typical skill looks like:

```yaml
---
name: react-testing
description: Expert guidance for testing React components with Jest and React Testing Library
---

When writing React component tests, follow these patterns:
- Use `render()` from @testing-library/react
- Prefer `screen.getByRole()` over `getByTestId()`
- Test behavior, not implementation
...
```

The key architectural insight is **what the agent sees and when**. When an agent starts a task, it loads only the **name** and **description** of every available skill — a lightweight index that fits in a few hundred tokens. The agent then decides which skills are relevant to the current task and requests the full body only for those. This is called progressive disclosure, and it's the entire point of the abstraction.

### Skills vs. AGENTS.md: A Comparison

| Feature | AGENTS.md (Monolithic) | Skills (Progressive Disclosure) |
|---|---|---|
| Initial context cost | Full file loaded every time | Names + descriptions only (~200 tokens) |
| Relevance filtering | Manual — you read the whole thing | Automatic — agent selects what it needs |
| Composability | One file, one purpose | Multiple skills, mix and match |
| Versioning | Git history on one file | Per-skill versioning possible |
| Security boundaries | None — all instructions visible | Front-matter can restrict tools |
| Community sharing | Copy-paste | Registry-ready format |
| Maintenance | Single file grows unbounded | Modular, independently updatable |

## Why Not Just AGENTS.md?

The skeptic's proposal — a single `AGENTS.md` that points to folders of `.md` files — sounds reasonable until you understand how LLM context windows actually work.

### The Context Pollution Problem

Every token in the context window consumes attention budget. When you dump a 10,000-token instruction file into an agent's context, you're not just paying for the tokens — you're actively degrading the agent's ability to focus on the actual task. This is called **context pollution**, and it's measurable.

As HN user `thiago_fm` put it in the discussion: *"Loading all instructions into context degrades LLM performance. The key architectural reason for skills is context window management."*

Research bears this out. LLM performance on focused tasks drops measurably when irrelevant context is present. A 2024 study on in-context learning showed that adding irrelevant but plausible information reduced accuracy by 15-30% across multiple model families. Skills prevent this by keeping the context lean.

### The Scaling Problem

A single `AGENTS.md` works for a small project with 3-5 instructions. But real-world agent deployments accumulate knowledge rapidly:

- Project conventions
- Testing patterns
- Deployment workflows
- API documentation
- Security policies
- Code review guidelines
- Database schemas
- Environment-specific instructions

A production agent at a mid-size company might need 50+ distinct instruction sets. Loading all of them simultaneously would consume 30,000-50,000 tokens before the agent even starts working. Skills keep the active context at a fraction of that.

### The Composability Problem

Monolithic files don't compose. If you have a React testing skill and a Python backend skill, an `AGENTS.md` approach forces you to either:

1. Put everything in one file (context pollution)
2. Have the agent read multiple files on every task (slow, wasteful)
3. Maintain separate agents for separate domains (operational overhead)

Skills solve this cleanly: the agent loads the React testing skill when it's writing frontend tests, and the Python backend skill when it's working on API routes. Both can coexist in the same agent without conflict.

## The Open Standard: How Claude Code's Skill Format Became Cross-Platform

What started as a Claude Code feature has become a de facto open standard. The Claude Code skills format — YAML front-matter plus Markdown body — is now adopted by Codex CLI, Cursor, and a growing ecosystem of AI coding tools.

Robert Glaser documented this transition in his analysis of Claude Skills in Codex CLI: *"Non-Claude agents like Codex CLI can adopt the same format with a small enumerator script. The skills directory structure — SKILL.md with front-matter, body loaded only when relevant — works across platforms."*

This cross-platform adoption matters because it creates a **portable skill ecosystem**. A skill written for Claude Code can be used by Codex CLI, and vice versa. The format is simple enough that any agent framework can implement it with minimal engineering effort.

### The Skill Directory Structure

The standard layout is straightforward:

```
~/.hermes/skills/
├── react-testing/
│   └── SKILL.md
├── python-packaging/
│   └── SKILL.md
├── docker-compose/
│   └── SKILL.md
└── security-review/
    └── SKILL.md
```

Each skill is a directory containing a `SKILL.md` file with YAML front-matter. Some implementations also support supporting files — scripts, templates, reference documents — bundled alongside the skill.

## Beyond Markdown: Skills That Bundle Executable Behavior

One of the most compelling arguments for skills over plain Markdown is that skills can bundle **deterministic scripts and artifacts**, not just text instructions.

As HN user `alexhans` noted: *"Skills can bundle deterministic scripts and artifacts (not just markdown), enabling executable behavior beyond prompting."*

This means a skill can include:

- **Validation scripts** that run automatically when the skill is activated
- **Code generators** that scaffold project structures
- **Linting configurations** that enforce project conventions
- **Test fixtures** and mock data
- **API client wrappers** with authentication baked in

A deployment skill, for example, might include a Python script that validates the deployment target, runs pre-deployment checks, and rolls back on failure — all triggered automatically when the agent decides to deploy. A plain Markdown file can describe these steps, but it can't execute them.

### The Hermes Agent Example

Hermes Agent by Nous Research demonstrates this pattern in practice. Its skills system supports:

- **SKILL.md** with YAML front-matter for metadata
- **Linked files** — references, templates, scripts — stored alongside the skill
- **Cron job integration** — skills can be loaded by scheduled tasks
- **Cross-profile isolation** — each Hermes profile has its own skills directory

This is the direction the ecosystem is moving: skills as **self-contained packages of agent capability**, not just documentation.

## The Security Reality Check

If skills are just Markdown files, what's the security risk? The answer is: **the same risk as any executable content delivery system**.

The OpenClaw skills marketplace — the largest public registry of AI agent skills — was audited by RankClaw, which examined all 14,706 skills in the marketplace. The findings were alarming:

- **1,103 skills (7.5%) were malicious**
- The **#1 most downloaded skill** on the marketplace was malware
- Static analysis and AI-based auditing were insufficient to catch all runtime threats

This is the "npm for AI skills" nightmare. When you create a marketplace where anyone can publish skills, you inherit all the security problems of package registries — supply chain attacks, typosquatting, malicious updates, and dependency confusion.

### The Security Landscape

| Threat | Description | Real-World Example |
|---|---|---|
| Malicious skills | Skills designed to exfiltrate data or compromise the agent | 7.5% of OpenClaw skills |
| Supply chain attacks | Compromised skill dependencies | #1 download was malware |
| Typosquatting | Skills named to mimic popular ones | Common in npm ecosystem |
| Privilege escalation | Skills that request more tools than needed | Front-matter tool restrictions |
| Data exfiltration | Skills that read and transmit sensitive data | Runtime detection challenges |

The lesson is clear: **skills need security scanning, sandboxing, and trust verification** — the same infrastructure that package registries like npm, PyPI, and RubyGems have built over decades. The agent skill ecosystem is learning these lessons from scratch, and the early results are sobering.

## The npm-for-Skills Vision

Despite the security challenges, the vision of a community-driven skill registry is compelling. The parallels to npm are intentional:

- **npm** made JavaScript package sharing trivial → **Skill registries** make agent capability sharing trivial
- **npm** created a massive ecosystem of reusable code → **Skill registries** create reusable agent behaviors
- **npm** struggled with security for years → **Skill registries** are learning those lessons now

The Generalized approach — skills as versioned, evaluated, and trust-scored packages — represents the mature vision. Tessl's proposed framework for evaluating skills focuses on:

1. **Structured metadata** — version, author, dependencies, tool requirements
2. **Performance evaluation** — how well does the skill actually work?
3. **Security scoring** — automated and manual review processes
4. **Versioning** — semantic versioning for skills, with changelogs and migration guides

This is where the ecosystem is heading, but we're in the early days. The current state is closer to "wild west" than "curated registry."

## What the Skeptic Was Right About

Let's give credit where it's due. The skeptic who asked "why not just AGENTS.md?" was right about several things:

1. **Skills are fundamentally just organized Markdown.** The core content of a skill is text instructions. There's no magic — no special AI sauce that makes skills work differently than reading a file.

2. **The abstraction adds complexity.** Skills introduce a new concept — the skill directory, the enumerator, the loading mechanism — that a simple file structure doesn't need.

3. **For small projects, AGENTS.md works fine.** If you have 3-5 instructions and a single domain, a monolithic file is simpler and equally effective.

4. **The skill ecosystem is immature.** Security is poor, standards are still forming, and the tooling is rough around the edges.

The skeptic's core insight — that skills are "just organized docs with a loading mechanism" — is essentially correct. The question is whether that loading mechanism matters enough to justify the abstraction.

## What the Skeptic Was Missing

Here's what the skeptic's framing misses:

### 1. Scale Changes Everything

A single `AGENTS.md` works for a personal project. It doesn't work for a team of 20 developers maintaining 50+ instruction sets across multiple domains. Skills are an **organizational pattern** that scales, not a technical trick.

### 2. Progressive Disclosure Is Not Just "Lazy Loading"

Calling skills "lazy-loaded Markdown" is technically accurate but misses the architectural significance. Progressive disclosure changes how the agent reasons:

- **Without skills:** The agent has all instructions in context and must decide which to follow. This is like giving a chef every recipe in the cookbook and asking them to cook one dish.
- **With skills:** The agent sees a menu of capabilities and requests only what it needs. This is like the chef picking a recipe card from the box.

The difference isn't in the content — it's in the **decision architecture**.

### 3. Composability Enables Emergent Behavior

When skills are modular and composable, agents can combine them in ways the author didn't anticipate. A testing skill + a deployment skill + a monitoring skill can produce a CI/CD pipeline that none of the individual skills described. This emergent composition is where the real value lives.

### 4. Security Boundaries Are Architectural

The front-matter in a skill can declare what tools it needs. This enables sandboxing — a skill that only needs file-reading tools shouldn't have network access. A monolithic `AGENTS.md` can't enforce these boundaries because everything is in one blob.

## The Bottom Line

Skills are a **packaging convention**, not magic. They take the same Markdown instructions you'd put in an `AGENTS.md` and add:

1. **Progressive disclosure** — load only what's relevant, when it's relevant
2. **Composability** — mix and match skills from different sources
3. **Versioning** — track and update skills independently
4. **Security boundaries** — declare and enforce tool requirements
5. **Portability** — share skills across agent platforms

The skeptic was right that skills are "just organized docs with a loading mechanism." But that loading mechanism — progressive disclosure — is the difference between a library where every book is open on the table and a library where you browse the catalog and pull only the books you need.

For small projects, `AGENTS.md` is fine. For anything that scales — multiple domains, multiple developers, multiple agent platforms — skills are the difference between chaos and structure. And in a world where 7.5% of published skills are malicious, that structure might also be the difference between a secure agent and a compromised one.

## Frequently Asked Questions

### Do I need skills for a simple personal project?

No. If you're the only developer and your agent handles 3-5 tasks, a single `AGENTS.md` or `CLAUDE.md` file is simpler and equally effective. Skills become valuable when you have multiple domains, multiple developers, or complex workflows.

### Can I use Claude Code skills with non-Anthropic agents?

Yes. The Claude Code skills format (YAML front-matter + Markdown body) has become a de facto open standard. Codex CLI, Cursor, and Hermes Agent all support the same format with minimal adaptation.

### How do skills affect token usage and cost?

Skills reduce token usage by keeping only relevant instructions in context. Instead of loading a 10,000-token instruction file on every interaction, the agent loads a 200-token index and fetches only the skills it needs. This can reduce context costs by 80-95% for complex projects.

### What's the biggest risk of using community skills?

Security. The OpenClaw marketplace audit found 7.5% of skills were malicious, and the #1 most downloaded skill was malware. Always audit community skills before using them, and prefer skills from trusted sources.

### Can skills include executable code, or are they just text?

Modern skill systems support both. While the core format is Markdown, many implementations allow skills to bundle scripts, templates, and artifacts. Hermes Agent, for example, supports linked files including Python scripts that run when the skill is activated.
