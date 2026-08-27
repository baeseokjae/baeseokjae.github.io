---
title: "Project Orrery: A Portable Codex Project Documentation Skill for Traceable Docs"
date: 2026-08-27T22:01:25+00:00
tags:
  - codex project documentation skill
  - codex skills
  - agent skills standard
  - SKILL.md
  - project documentation for AI agents
  - traceable project docs
  - AGENTS.md
  - documentation as code
  - AI agent orchestration
  - codex CLI skills
  - portable agent skill
  - project planning agent
description: "Project Orrery is a portable Codex skill that turns goals into traceable YAML plans and archived execution reports, so agent work stays auditable."
draft: false
cover:
  image: "/images/project-orrery-codex-skill-2026.png"
  alt: "Project Orrery: A Portable Codex Skill for Traceable Project Docs"
  relative: false
schema: "schema-project-orrery-codex-skill-2026"
---

A codex project documentation skill is a portable, SKILL.md-based capability that lets an AI coding agent plan work as traceable YAML contracts and record every execution step, so the reasoning behind a project survives as an auditable archive instead of vanishing into a chat log. Project Orrery implements exactly this: it turns high-level goals into executable, engineered workflows whose state lives in a `.agent-work/` directory with `plans/`, `reports/`, and `completed/` subdirectories. Because the skill is built on the open agent skills standard, the same skill works in Codex CLI, Claude Code, Cursor, and Gemini CLI.

## What Is Project Orrery and Why Traceability Matters

Project Orrery is a workflow planning and orchestration CLI for AI agents. Where a typical agent session is a black box — you see the final diff but not the reasoning, the rejected alternatives, or the acceptance criteria that shaped each step — Orrery makes the process itself a first-class artifact. It converts a high-level goal into a structured plan, executes that plan through one or more agents, and archives the entire lifecycle for later review.

Traceability matters because AI agents increasingly run autonomously. When a human is not watching every keystroke, you need a durable record of *what* was done, *why* it was done that way, and *whether* it met the stated criteria. Orrery's `.agent-work/` archive turns every plan and every execution report into an auditable record. That is the difference between trusting an agent and verifying an agent.

The project is built around modular "Skills" — Discovery, Refine-Plan, and Simulate-Plan — that install into global agent config directories such as `~/.claude/skills`. The orchestrator, `orrery exec`, loads a plan, resolves its dependencies, invokes the appropriate agents, and manages the lifecycle with reporting and archiving. Advanced workflows include plan refinement, devcontainer isolation, a review loop, parallel execution, background mode, and completion hooks.

## The Open Agent Skills Standard: Why SKILL.md Is Portable

The reason a codex project documentation skill can be portable is the open agent skills standard. Agent Skills is a lightweight, open format for extending AI agent capabilities: a skill is simply a folder containing a `SKILL.md` file with name and description metadata, plus optional `scripts/`, `references/`, `assets/`, and `agents/` subdirectories. Because the format is open and markdown-based, any agent that can load markdown skills can consume it.

This portability is the core of the "portable" claim. A skill written once for Codex CLI also works in Claude Code, Cursor, GitHub Copilot, OpenCode, Gemini CLI, and Pi. The ecosystem has embraced the convention: the `agent-skills` collection by addyosi, a set of production-grade engineering skills for AI coding agents, has roughly 90,000 GitHub stars, and OpenAI Codex CLI itself has about 119,000 stars, making it one of the most popular terminal coding agents.

The standard also defines how skills are discovered. In Codex, the initial skills list uses at most 2% of the model's context window, or 8,000 characters when the context window is unknown. This keeps the skill menu cheap to load while still allowing the full `SKILL.md` to be pulled in when a skill is actually selected — a mechanism called progressive disclosure.

## How Orrery Turns Goals into Traceable Plans

Orrery's central abstraction is the plan. A plan is a YAML file that defines the "contract" for a piece of work: its dependencies, its acceptance criteria, and the context needed per step. This contract mindset is what makes agent work reviewable *before* it runs autonomously.

A typical plan encodes:

- **Dependencies** — which steps must complete before others begin, enabling parallel execution where safe.
- **Acceptance criteria** — explicit, testable conditions that define when a step is genuinely done, not merely attempted.
- **Context per step** — the information each agent needs, so a step is self-contained and reproducible.

Once a plan is written, `orrery exec` loads it, resolves the dependency graph, and dispatches work to agents. Execution state is stored in `.agent-work/` with `plans/`, `reports/`, and `completed/` subdirectories. When a plan finishes, its report and plan move into the `completed/` archive, giving you a full, chronological record of every workflow the project has run.

## Step-by-Step: Building a Portable Codex Skill for Project Docs

Here is how to build your own portable codex project documentation skill, modeled on Orrery's approach.

**Step 1: Create the skill directory.** A skill is a folder. Create `~/.codex/skills/project-docs/` (or the equivalent global config directory for your agent) and add a `SKILL.md` file.

**Step 2: Write the frontmatter.** The `SKILL.md` opens with YAML frontmatter containing a `name` and `description`. The description is what the agent reads to decide whether to load the skill, so make it specific: "Plan project work as traceable YAML contracts and archive execution reports."

**Step 3: Define the plan schema.** Decide what a plan looks like. At minimum, include `goal`, `steps`, `dependencies`, and `acceptance_criteria`. Keep it YAML so it is human-readable and diffable.

**Step 4: Add a plan template.** Include a `templates/plan.yaml` that the agent can copy. A good template makes the skill usable without the agent inventing structure on the fly.

**Step 5: Specify the archive layout.** Tell the skill to write plans and reports into a `.agent-work/` directory with `plans/`, `reports/`, and `completed/` subdirectories, mirroring Orrery's traceability model.

**Step 6: Add a verification step.** Instruct the agent to check acceptance criteria before marking a step done, and to write a short report per step. This is what turns a chat session into an auditable record.

**Step 7: Test portability.** Copy the same skill folder into `~/.claude/skills/` and `~/.cursor/skills/` and confirm the agent loads it. If it works in all three, your skill is genuinely portable.

## Progressive Disclosure: Keeping Your Skill Light on Context

One of the smartest design decisions in the agent skills standard is progressive disclosure. The agent does not load your entire skill into context at startup. Instead, it reads only the name and description — a tiny footprint that costs at most 2% of the context window, or 8,000 characters. Only when the agent decides the skill is relevant does it load the full `SKILL.md` and any referenced files.

This matters for a project documentation skill because the full instructions can be long. By keeping the description crisp and pushing the detailed plan schema, templates, and examples into referenced files, you keep the skill discoverable without bloating every session. Large skill sets may even omit skills with a warning if the combined list exceeds the budget, so a tight description is not just nice-to-have — it is what keeps your skill from being dropped entirely.

## Making Documentation a Byproduct, Not Extra Work

The most common reason project documentation fails is that it is treated as a separate, after-the-fact task. By the time the code is written, the reasoning is gone. Orrery and related skills invert this: they capture reasoning *during* the conversation, as a byproduct of working with the agent, rather than writing docs afterward.

This is the philosophy behind "Keep the Why," a repo-native convention and agent skill that preserves the reasoning behind a codebase as a byproduct of working with your agent. It offers four modes — continuous capture, retrospective recovery, knowledge-transfer interview, and maintenance — and ships `context/` updates in the same commit as the code change, so they are versioned and reviewed the same way. Its tagline captures the distinction: "Keep a Changelog records what changed. Keep the Why preserves why it changed."

For a codex project documentation skill, the practical takeaway is to make documentation part of the plan contract. Each step's report *is* the documentation. You are not adding a documentation phase; you are making the execution phase produce documentation automatically.

## Running Autonomously Without Losing Control

Autonomy is only safe when you can bound its blast radius. Orrery supports devcontainer isolation and isolated branches so agents can run unattended without risking the main branch. A review loop lets a human or a second agent check work before it merges, and completion hooks fire when a workflow finishes.

The combination of isolated execution and a traceable archive is what makes unattended agent work defensible. If something goes wrong, you can inspect the plan, the reports, and the acceptance criteria to understand exactly what happened and why. That is the safety net that turns "the agent did it" from a liability into an auditable, reviewable process.

## Comparing Orrery, Keep the Why, and Living Docs

| Tool | Core idea | Format | Best for |
|------|-----------|--------|----------|
| **Project Orrery** | Goal-to-plan orchestration with archived execution | YAML plans + SKILL.md | Traceable, multi-step agent workflows |
| **Keep the Why** | Preserve reasoning as a byproduct of work | SKILL.md + `context/` | Explaining *why* code changed |
| **Living Docs** | Docs-as-code kept in sync with code | SKILL.md + Rust CLI | Governing doc structure and invariants |
| **AGENTS.md** | A README for agents | Markdown | Project context and instructions |

Each tool solves a different slice of the documentation problem. Orrery focuses on the *process* — turning goals into traceable, executable plans. Keep the Why focuses on the *reasoning* — preserving the decisions and rejected alternatives that code alone cannot explain. Living Docs focuses on the *structure* — governing how docs are organized with ADRs, BDRs, PRDs, a constitution, glossary, and living Mermaid diagrams, enforced by five governance invariants: docs-first, one home per fact, and cross-reference instead of copying. AGENTS.md, meanwhile, is the simplest layer: a dedicated, predictable place to provide context and instructions to help AI coding agents work on a project.

## Best Practices for Traceable Project Documentation

Drawing on Orrery and the wider agent-skills ecosystem, here are the practices that make project documentation genuinely traceable:

- **Make the plan the contract.** Write acceptance criteria before execution, not after. A plan you can review is a plan you can trust.
- **Archive everything.** Keep plans, reports, and completed workflows in a versioned directory so the history is inspectable.
- **Capture the why, not just the what.** Record rejected alternatives and workarounds alongside the chosen approach.
- **Ship docs with code.** Version documentation in the same commit as the change it describes, so the two cannot drift apart.
- **Keep skills portable.** Build on the open SKILL.md standard so your skill works across Codex, Claude Code, Cursor, and Gemini CLI.
- **Respect the context budget.** Keep skill descriptions tight so progressive disclosure keeps your skill discoverable.
- **Isolate autonomous runs.** Use devcontainers and isolated branches so unattended agents cannot damage the main branch.

## Conclusion

A codex project documentation skill built on the open agent skills standard gives you the best of both worlds: the autonomy of an AI coding agent and the auditability of a well-run engineering process. Project Orrery demonstrates the pattern — turn goals into YAML plan contracts, execute them through agents, and archive every plan and report in a `.agent-work/` directory for full traceability. Because the skill is portable, the same capability works in Codex CLI, Claude Code, Cursor, and Gemini CLI. The result is documentation that is a byproduct of the work rather than an afterthought, and agent autonomy that is safe because it is verifiable.

## FAQ

**What is a codex project documentation skill?**
A codex project documentation skill is a portable, SKILL.md-based capability that lets an AI coding agent plan work as traceable YAML contracts and record every execution step, producing an auditable archive of the reasoning behind a project.

**How does Project Orrery make agent work traceable?**
Orrery stores execution state in a `.agent-work/` directory with `plans/`, `reports/`, and `completed/` subdirectories, so every plan and execution report becomes an auditable record of what was done and why.

**Is a SKILL.md skill portable across different AI agents?**
Yes. SKILL.md is an open cross-agent format, so a skill written for Codex CLI also works in Claude Code, Cursor, GitHub Copilot, OpenCode, Gemini CLI, and Pi.

**What is progressive disclosure in agent skills?**
Progressive disclosure means the agent loads only a skill's name and description at startup — at most 2% of the context window or 8,000 characters — and loads the full SKILL.md only when the skill is selected.

**How is Orrery different from AGENTS.md?**
AGENTS.md is a simple markdown file that provides project context and instructions to coding agents, while Orrery is a workflow orchestration CLI that turns goals into executable, traceable YAML plans with archived execution reports.
