---
cover:
  alt: 'Superpowers Framework: TDD Methodology for AI Coding Agents 2026'
  image: /images/superpowers-framework-ai-coding-2026.png
  relative: false
date: 2026-04-24 04:12:05+00:00
description: Superpowers is the open-source framework that enforces TDD discipline
  on AI coding agents—here's how to install it and why it works.
draft: false
schema: schema-superpowers-framework-ai-coding-2026
tags:
- ai-agents
- developer-tools
- tutorial
- tdd
- claude-code
title: 'Superpowers Framework: TDD Methodology for AI Coding Agents 2026'
---

The Superpowers framework is the fastest way to stop your AI coding agent from shipping broken code. Instead of hoping the model follows best practices, Superpowers installs a structured set of skills that *enforce* a clarify → design → plan → code → verify discipline on every task—red tests before green, always.

## What Is the Superpowers Framework? (The Problem It Solves)

Superpowers is an open-source agent skills framework created by Jesse Vincent (obra) that encodes professional software engineering discipline—particularly test-driven development—into reusable skill files that AI coding agents auto-trigger by context. Released in October 2025, it gained 1,528 GitHub stars in its first 24 hours and reached 129,443 stars by April 2026, making it one of the most starred coding-agent repositories ever. The framework emerged from a concrete frustration: AI agents like Claude Code are capable of writing correct code, but when left unguided they skip tests, cut corners on design, and produce implementations that pass their own ad-hoc checks rather than actual requirements. Superpowers solves this by shipping 14 composable skills—from brainstorming to subagent code review—that transform an unconstrained coding agent into a disciplined engineering collaborator. Rather than patching behavior with a long CLAUDE.md paragraph, each skill is a focused SKILL.md file that triggers at the right moment and dispatches fresh subagents to handle isolated subtasks like writing failing tests or running a two-stage review.

The core insight: you can't reliably instruct an AI agent to "follow TDD" in a system prompt. Under time pressure, the agent will write implementation first and retrofit tests. Superpowers removes the choice—the skill pipeline makes it structurally impossible to skip the red phase.

## Why TDD Is Non-Negotiable for AI Coding Agents

TDD is non-negotiable for AI coding agents because without it, agents produce tests that are guaranteed to pass—not because the code is correct, but because the tests were written to match whatever the implementation already does. This is the "tests-that-pass-by-construction" failure mode: the agent writes a function, then generates a test that calls that function and asserts its actual output equals the expected output. The test suite is green from line one. It passes in CI. It ships to production. And it verifies nothing except that the code is internally consistent with itself—not that it satisfies the original requirement. Research from codemanship.wordpress.com in January 2026 confirmed this is the default behavior for AI agents operating without TDD constraints. Developers using Superpowers report 85–95% test coverage, compared to 30–50% with standard Claude Code prompting. The reason is structural: Superpowers forces the agent to write a failing test (red) before any implementation exists, proving the test is actually capable of catching a bug. Only then does the agent write the minimum implementation to make it pass (green), and finally refactor. This is classical Red-Green-Refactor, enforced mechanically rather than left to the agent's judgment.

Separately, spec-driven development—writing detailed specifications before prompting the agent—reduces rollback rates by 60%+ compared to vague prompts. Superpowers operationalizes this through its clarify and design phases, which happen before a single line of code is written.

### The Tests-That-Pass-By-Construction Problem

When an agent writes `assert add(2, 3) == add(2, 3)` instead of `assert add(2, 3) == 5`, the test is technically passing but meaningless. AI agents do this implicitly—they observe what the function returns and assert that value, rather than deriving the expected value from the specification. A red-first TDD workflow prevents this because the test is written before the function exists, forcing the developer (or agent) to derive the expected value from the requirement, not from the implementation.

## How Superpowers Enforces Red-Green-Refactor (Step by Step)

Superpowers enforces Red-Green-Refactor by wiring the TDD cycle into a deterministic skill pipeline that runs inside the coding agent's session—the agent cannot skip a phase any more than a CI pipeline can skip a step. When you invoke a coding task under Superpowers, the framework routes execution through a five-phase discipline: (1) **Clarify**: the agent asks structured clarifying questions before touching code, surfacing ambiguities that would otherwise surface as bugs; (2) **Design**: the agent produces a written design document, including interface contracts and data flow, before writing implementation; (3) **Plan**: the agent generates an ordered task list with explicit test checkpoints; (4) **Code**: implementation proceeds in TDD cycles—write one failing test, write minimum passing code, repeat; (5) **Verify**: a dedicated subagent performs two-stage code review against the original spec. Each phase dispatches a fresh subagent with a narrow context window, preventing the context contamination that causes agents to rationalize skipping tests when they already have implementation code in memory.

The key architectural decision is subagent dispatch. Rather than one long agentic session where the model accumulates pressure to "just finish," each skill spawns an isolated agent with a single responsibility. The test-writing subagent has never seen the implementation. It cannot rationalize passing tests by construction because the implementation doesn't exist in its context.

### The Role of SKILL.md Files

Each Superpowers skill is a SKILL.md file in the `.superpowers/skills/` directory. Skills declare their trigger conditions—the agent detects matching context and loads the relevant skill automatically. A skill for "write failing tests" triggers when the agent is about to implement a new function; a skill for "subagent review" triggers when a coding session is about to close. This auto-triggering is what distinguishes Superpowers from a CLAUDE.md instruction file, which relies on the agent choosing to follow instructions under all conditions.

## Installing Superpowers in 2026 (Claude Code, Cursor, Codex CLI)

Installing Superpowers in 2026 takes under five minutes for Claude Code users and works across four major AI coding environments: Claude Code (via the built-in skill marketplace), Cursor, Codex CLI, and OpenCode. For Claude Code, the recommended path is the marketplace: open Claude Code, navigate to Skills, search "Superpowers", and click Install. This writes the `.superpowers/` directory and all 14 skill files into your project root and registers them as auto-triggering skills. For Cursor, Codex CLI, and OpenCode, the manual path is: clone `github.com/obra/superpowers` and copy the `.superpowers/skills/` directory into your project root, then configure your tool to read from that path. As of Superpowers 5 (released Q1 2026), the framework also ships with a visual brainstorming skill that generates HTML mockups during the design phase—particularly useful for frontend work where a visual target reduces ambiguity before coding begins.

```bash
# Manual install (Cursor, Codex CLI, OpenCode)
git clone https://github.com/obra/superpowers /tmp/superpowers
cp -r /tmp/superpowers/.superpowers ./
```

```bash
# Verify installation
ls .superpowers/skills/
# Should list 14 .md skill files
```

After installation, run a test task: ask your agent to "add a function that parses ISO 8601 dates." With Superpowers active, the agent should ask clarifying questions before touching code. If it starts writing the function immediately, check that your tool is configured to read from `.superpowers/skills/`.

### Superpowers 5 Visual Brainstorming

Superpowers 5 added an HTML mockup generation step to the design phase. When the task involves a UI component, the agent now produces a static HTML mockup and opens it in a browser tab before writing any React/Vue/template code. This gives the developer a visual contract to accept or reject before the agent invests in implementation. The mockup is committed alongside the spec document, making the design phase reviewable in version control.

## The 14 Core Skills: From Brainstorming to Subagent Code Review

The 14 Superpowers skills form a complete software development methodology, covering every phase from initial idea to production-ready code review. Each skill is a standalone SKILL.md file with a declared trigger condition, a structured prompt, and (in most cases) a subagent dispatch instruction. The skills group into five categories: **Discovery** (brainstorm, clarify, spec-write); **Design** (architecture, interface-design, mockup); **Planning** (task-breakdown, test-plan); **Implementation** (tdd-cycle, refactor, dependency-check); and **Quality** (subagent-review, coverage-check, retrospective). The brainstorm skill is deliberately first: it prevents the agent from jumping to an implementation approach before exploring alternatives. The agent generates three or more distinct approaches, evaluates trade-offs, and selects one before entering the design phase. This front-loads decision quality and prevents the sunk-cost problem where an agent has written 200 lines of code before discovering the approach was wrong. The subagent-review skill at the end dispatches two independent review agents: one checks correctness against the spec, one checks style and maintainability. Both reviews run in fresh contexts with no memory of the implementation session, producing genuinely independent assessments.

The coverage-check skill enforces the 85–95% coverage target by running the test suite, parsing the coverage report, and refusing to close the session if coverage is below the configured threshold. The threshold is configurable per project in `.superpowers/config.yaml`.

### YAGNI and DRY Enforcement

Two skills directly enforce classic software engineering principles. The YAGNI (You Aren't Gonna Need It) check runs during the planning phase and flags any planned feature that isn't required by the current spec. The DRY check runs during the refactor phase and detects duplicated logic across the implementation, prompting the agent to extract it before closing. These aren't stylistic suggestions—skills that detect violations pause execution and require explicit sign-off to continue, making the principles operationally enforceable rather than advisory.

## Real-World Results: chardet 7.0.0 Case Study (41x Faster, 96.8% Accuracy)

The chardet 7.0.0 release is the most-cited Superpowers case study because its results are independently verifiable and dramatically better than prior versions. The chardet library—Python's automatic character encoding detector—had been maintained incrementally for years, accumulating technical debt that made the encoding detection logic slow and brittle. Jesse Vincent, Superpowers' creator, used the framework to drive a ground-up rewrite: the resulting version 7.0.0 runs 41 times faster than 6.x, achieves 96.8% detection accuracy across 99 encodings, and ships with a test suite covering 2,161 files. The 2,161-file test corpus is a direct product of the Superpowers TDD methodology: the test-plan skill generated a comprehensive encoding coverage matrix before any implementation existed, ensuring the test suite was derived from requirements rather than retrofitted to implementation. The 96.8% accuracy figure represents a significant improvement over the industry baseline, and the 41x speed improvement came directly from the architecture skill surfacing a more efficient algorithm before the agent committed to the legacy approach. Without the brainstorm-first and design-before-code phases, the agent would likely have implemented an optimized version of the existing algorithm rather than reconsidering the architectural foundation.

This case study validates the framework's core claim: the upfront investment in clarify → design → plan phases pays off in implementation quality that simple "just write it" prompting cannot match, regardless of model capability.

### How to Apply the chardet Approach to Your Project

The chardet workflow generalizes: (1) start with the brainstorm skill to generate competing architectural approaches; (2) build a test corpus from the requirement specification before writing a single implementation line; (3) use the coverage-check skill to enforce corpus coverage; (4) let the tdd-cycle skill drive implementation. The key is resisting the urge to skip directly to coding. The chardet rewrite succeeded because the test corpus was built first—the implementation had to satisfy 2,161 real-world files, not a handful of hand-crafted examples.

## Superpowers vs Standard Prompting: Quality Comparison

Superpowers consistently outperforms standard prompting across the quality metrics that matter in production: test coverage, spec adherence, and rollback rate. Standard prompting—whether via a long CLAUDE.md file, .cursorrules, or a system prompt—relies on the model choosing to follow instructions in every context and under every level of time pressure. Models do not reliably do this. As context length grows and the agent accumulates implementation momentum, adherence to prompting instructions degrades. Superpowers sidesteps this degradation by encoding behavior into skill pipelines rather than instructions: the agent cannot skip the red phase because the skill pipeline routes execution through it before the implementation skill is available. The empirical gap is significant: 85–95% test coverage with Superpowers vs. 30–50% with standard prompting. Rollback rates drop 60%+ when the clarify and design phases surface ambiguity before coding begins. These numbers are consistent with the broader finding that AI coding tools deliver a 2.5–3.5x ROI when used with structured workflows, compared to marginal gains when used as ad-hoc autocomplete.

| Metric | Standard Prompting | Superpowers Framework |
|---|---|---|
| Test Coverage | 30–50% | 85–95% |
| Spec Adherence | Variable | Enforced |
| Rollback Rate | Baseline | -60% |
| Code Review | Manual | Automated (subagent) |
| Setup Time | 5 min | 5 min |

The setup time is identical. The quality gap is not.

### When Standard Prompting Is Enough

Superpowers adds overhead. For one-off scripts, quick prototypes, or exploratory analysis code that will never enter production, the five-phase discipline is overkill. CLAUDE.md instructions or .cursorrules work fine when correctness isn't critical and you're the only consumer of the output. Superpowers earns its overhead when: (a) the code runs in production, (b) multiple developers will maintain it, (c) correctness is externally verifiable (parsing, encoding, computation), or (d) the scope is large enough that rollbacks are expensive.

## Common Mistakes and How to Avoid Them

The most common Superpowers mistake is installing the framework and then bypassing it by prompting the agent directly with implementation instructions—"write a function that does X"—rather than activating the brainstorm or clarify skill first. When you start with an implementation prompt, you skip the design and planning phases, and the skills that should have run before coding are never triggered. The fix is to always start a task with the Superpowers entry point: in Claude Code, type `/superpowers` or invoke the brainstorm skill explicitly. The second most common mistake is setting the coverage threshold too low during initial setup. The default is 80%; for production code, set it to 90% or higher in `.superpowers/config.yaml`. A low threshold lets the coverage-check skill sign off on a partially covered codebase, undermining the framework's quality guarantees. Third: not committing the `.superpowers/` directory to version control. Skill files are project artifacts, not tooling configuration—they should be reviewed, versioned, and shared across the team. A skill file that enforces an encoding standard or a testing convention is as important to commit as a linter config.

Misconfigured skill triggers are a fourth failure mode: if your tool isn't loading skills from `.superpowers/skills/`, the framework is silently inactive. Verify with a test task as described in the installation section above.

### Customizing Skills for Your Stack

Skills are Markdown files with a structured prompt—they're designed to be modified. For a TypeScript project, fork the tdd-cycle skill and add an instruction to always use `describe`/`it` blocks and mock with `vi.fn()`. For a Python project, add a pytest coverage command to the coverage-check skill. The `.superpowers/config.yaml` file controls coverage thresholds, coverage tool, and which skills are active. Customization is low-friction and the changes are version-controlled alongside the skill files.

## FAQ

**What is the Superpowers framework for AI coding agents?**
Superpowers is an open-source framework of 14 agent skills that enforce a clarify → design → plan → code → verify discipline on AI coding agents like Claude Code and Cursor. It was created by Jesse Vincent (obra) and reached 129,443 GitHub stars by April 2026. Its primary mechanism is TDD enforcement: agents must write failing tests before any implementation, preventing the "tests-that-pass-by-construction" failure mode common in unguided AI coding sessions.

**How do I install Superpowers in Claude Code?**
In Claude Code, open the Skills marketplace, search for "Superpowers", and click Install. This creates the `.superpowers/` directory with all 14 skill files in your project root. For Cursor and Codex CLI, clone `github.com/obra/superpowers` and copy the `.superpowers/skills/` directory into your project. Verify the install by asking your agent to add a function—it should ask clarifying questions before writing any code.

**What are the 14 Superpowers skills?**
The 14 skills group into five categories: Discovery (brainstorm, clarify, spec-write), Design (architecture, interface-design, mockup), Planning (task-breakdown, test-plan), Implementation (tdd-cycle, refactor, dependency-check), and Quality (subagent-review, coverage-check, retrospective). Each is a standalone SKILL.md file that auto-triggers based on context within the coding agent's session.

**Does Superpowers work with models other than Claude?**
Yes. Superpowers ships skill files for Claude Code, Cursor (GPT-4/Claude backend), Codex CLI, and OpenCode. The framework is model-agnostic in principle—skills are Markdown prompt files that any instruction-following model can execute. In practice, the subagent dispatch features work best with models that support tool use and can spawn sub-sessions, which covers all four officially supported environments.

**How does Superpowers compare to just writing a good CLAUDE.md file?**
CLAUDE.md instructions rely on the model consistently choosing to follow them—reliability degrades as context grows and the agent accumulates implementation momentum. Superpowers encodes behavior into a pipeline: skills are triggered mechanically, not by the model's judgment. The practical result is 85–95% test coverage with Superpowers vs. 30–50% with CLAUDE.md prompting, and 60%+ lower rollback rates. For production code, Superpowers is the more reliable choice; for quick scripts, a well-written CLAUDE.md is sufficient.