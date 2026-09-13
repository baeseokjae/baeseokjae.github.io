---
title: "Super Simple Software Factory: How to Build Repeatable Agent Workflows as a Skill"
date: 2026-09-13T16:01:28+00:00
tags: [software factory, agentic software factory, AI software factory, repeatable agent workflows, agent skills, Claude skills, AI developer workflow, deterministic AI agents, software factory skill]
description: Turn one-off AI coding runs into repeatable results by packaging a deterministic Python control plane and bounded agents into a single repo-stamped skill.
draft: false
cover:
  image: "/images/super-simple-software-factory.png"
  alt: "Super Simple Software Factory: Repeatable Agent Workflows as a Skill"
  relative: false
schema: "schema-super-simple-software-factory"
---

Every team can get an AI coding agent to write code once; almost nobody gets the same result twice. A software factory agent skill fixes exactly that: it packages a repeatable agents-plus-code workflow into one Claude skill you stamp into any repository, with the control plane living in deterministic Python rather than in a prompt. By the end of this guide you will know how to build your own repeatable workflow, where the human still makes decisions, and the real statistics behind the skills movement.

## What Is a Software Factory (and Why Generative Agents Changed It)

"Software factory" is not a new idea. Ben Bemer proposed a software "factory" concept as far back as 1968, the Software Design Corporation described one in 1975, and Microsoft published its influential "Software Factories" book in 2004. The recurring idea is simple: take the messy, heroic, one-off act of building software and turn it into a structured, repeatable pipeline that converts raw inputs — requirements, code, tests — into quality output using shared tooling, standards, and patterns.

What changed in 2026 is that the pipeline itself has become agent-native. Autonomous AI systems now carry out planning, implementation, testing, and review steps that a factory once delegated to humans or rigid tooling. As TrueFoundry explains in its enterprise guide, this agent-native reinterpretation is broader than a coding assistant (which only writes code) and broader than CI/CD (which only validates it): it spans the full production system, with agents doing more of the planning and review work under human governance.

The practical consequences are staggering in scale. A 2026 JetBrains State of Developer Ecosystem survey found that 90% of professional developers used AI coding agents at work at least weekly by mid-2026, up sharply from early in the year. Uber now attributes more than 70% of its pull requests to agents and has shipped 3,600+ employee-built agent skills across the software development lifecycle. Gartner reports that 93% of IT leaders plan to deploy autonomous agents within two years, and forecasts that a third of enterprise software will carry built-in agentic capabilities by 2028.

| Era | Control mechanism | Who plans? | Reusability |
|-----|------------------|-----------|-------------|
| Pre-AI factory (1968–2004) | Manual standards, toolchains | Humans | Low, documented as best practice |
| CI/CD pipelines | Declarative config, tests | Humans | Medium, code-based |
| Free-form agent use (2024–2025) | Prompting, context windows | Agent, inconsistently | Low, non-deterministic |
| Agent-native factory (2026) | Deterministic code owns the graph | Human intent + bounded agent | High, packaged as skills |

## The Repeatability Problem: Why One-Off Agent Runs Don't Scale

The reason most teams stall at the "write code once" stage is a simple gap between aspiration and reality. Stack Overflow's 2025 Developer Survey found that while 84% of developers use or plan to use AI tools (up from 76% in 2024), only 29% trust AI outputs to be accurate — a drop from 40%. Fully 46% of developers actively distrust AI accuracy, and 66% list "almost right but not quite" as their top frustration.

That trust collapse is the real driver behind the shift to deterministic workflows. When you hand an agent a prompt and it produces a slightly different plan, different file layout, and different quality bar every time, you cannot build on top of it. Every run is a gamble. The moat in this space is not which foundation model you call — it is determinism: the ability to run the same workflow on the same input and get the same shape of result, with failure and acceptance rules that hold.

## The Core Model: Deterministic Code Owns the Graph, Agents Are Bounded Nodes

The design pattern at the heart of a super simple software factory is best captured in one motto drawn from the reference open-source project: "Agent proposes, code disposes." The control plane lives in code, not in the prompt. This is the single most important architectural choice you can make.

Concretely, a deterministic Python module — in the ADW (AI Developer Workflow) pattern — owns sequencing, retries, and acceptance criteria. Agents are not free-wheeling thinkers; they are bounded nodes inside that Python graph. The Python decides what step runs next, whether a step passed its acceptance check, and how many retries a failing step gets before the graph marks it failed. The agent contributes content within a defined corridor; code decides whether that content is good enough to proceed.

This inversion matters because prompts and context windows are the least reliable, least versionable part of an AI system. Deterministic Python is tested, version-controlled, and deterministic by construction. By moving orchestration out of the prompt, you make the workflow behave predictably even as the underlying model changes.

## Anatomy of a Repeatable Workflow Stamped Into Any Repo

When you stamp a super simple software factory into a repository, you introduce a small, predictable layout. A typical stamped repo might contain an `adws/` directory with focused workflow modules such as:

- `adw_plan.py` — turns requirements into a structured plan
- `adw_build.py` — implements the plan with bounded agents
- `adw_test.py` — runs acceptance checks and retries
- `adw_document.py` — produces documentation from evidence
- `adw_simple_sdlc.py` — orchestrates the full lifecycle graph
- `adw_modules/` — shared building blocks across workflows

Alongside those modules you keep tracked prompts under `adw_data/prompt_engineering/` and a `sssf.config.yaml` that acts as the agent roster. A key design detail from the reference implementation: a single Cursor query serves as both the live view and the full history transport. There is no separate ingest endpoint to maintain — the state you need is already in the query response. That keeps the factory simple enough to understand, debug, and move between repos.

Two properties make this layout portable rather than repo-specific. First, it is self-contained: everything the workflow needs lives inside the repo, so stamping it into a new project requires no external infrastructure. Second, prompts are treated as versioned data, not as ephemeral instructions — which means changes to prompting are reviewable, revertible, and shareable across teams.

## Packaging the Workflow as a Reusable Skill

Skills have become the unit of reuse in this world. The most visible expression is Anthropic's Claude skills pattern, which exploded in popularity: a single CLAUDE.md-driven skills approach reached roughly 176,000 GitHub stars by mid-2026. Atlassian, building its "AI work factory," describes a skills layer of AI playbooks that sit on top of a data layer (live sources like Jira or Confluence) and an orchestration layer. Uber's engineers have authored more than 3,600 employee-built agent skills and run 30+ production workflow skills across the SDLC.

Atlassian highlights a clean portability pattern worth copying: keep a **thin SKILL.md in a standard location** that points to the full skill detail stored inside the factory. The thin pointer makes the skill discoverable and importable; the full detail lives where it can be versioned and governed. This mirrors the Gang of Four design-patterns insight — a shared vocabulary capturing proven expertise. A skill, like a design pattern, is a named, reusable answer to a recurring problem, and giving that answer a canonical name lets people talk about it and share it.

So packaging your software factory as a skill means: (1) write a thin, discoverable SKILL.md; (2) keep the deterministic Python, prompts, and config in your factory repo; (3) stamp the whole thing into any target repo when you need that workflow. One command moves the capability from "we know how to do this" to "any team with this repo can do this."

## Real-World Numbers: Uber, Atlassian, and the Skills Explosion

The numbers are not hypothetical. Uber's engineering blog reports that local and cloud agents drive more than 70% of pull requests, backed by 3,600+ employee-built agent skills. Uber is honest about the caveat: those PRs are "attributed to" agents, with human review and escalation in the loop — agents drive the work rather than shipping 70% of PRs unreviewed. That honesty is exactly the division of labour the factory model demands.

Atlassian's "AI work factory" reframes the whole company around the three-layer model of data, orchestration, and skills. Anthropic's skills pattern hit roughly 176K GitHub stars by mid-2026, and Gartner's projection that 33% of enterprise software will include built-in agentic capabilities by 2028 gives you a timeline for when this stops being a novelty and becomes default infrastructure.

The skills explosion is not about novelty chasing. It is the market converging on a small set of portable ways to package deterministic agent workflows — the same standardization that happened to CI/CD, container images, and design patterns. When a workflow is a named, stamped artifact instead of tribal knowledge, it can be audited, improved, and reused at scale.

## The Cost-Engineering Playbook (Model Routing, Caching, Lean Schemas)

A software factory only pays for itself if it is cheap enough to run per-iteration, and Uber's engineering team has published the playbook. Four levers dominate cost:

- **Benchmark-driven model routing.** Expensive, capable frontier models are reserved for steps that need them; cheaper default models handle the long tail.
- **Prompt caching tuned to idle gaps.** Cache window that matches the way agents actually idle between calls, so you never pay to re-tokenize unchanged context.
- **Lean tool schemas.** Smaller, sharper tool definitions mean fewer tokens per call and simpler reasoning.
- **Code-mode subprocess loops.** Uber reports 50–71% token savings on trivial queries, roughly 100% on wide result sets, and 90%+ on bulk workloads by streaming results through subprocess-style loops instead of large context dumps.

The lesson is that efficiency is an architecture decision, not a rounding detail. Routing and caching choices routinely produce savings well above an order of magnitude on the widest workloads, which is what makes it viable to run thousands of agent workflow invocations per day.

## Human versus Agent: Who Owns Intent, Acceptance, and Evidence

It is tempting to conclude that "the factory is autonomous, so humans are out." The successful implementations say the opposite. Across the reference project, Atlassian, and TrueFoundry, the split is consistent: **humans own intent, acceptance criteria, governance, and evidence review; agents own planning, retrieval, synthesis, formatting, and execution.**

Engineers define the problem, set the acceptance criteria, govern access and policy, and review the evidence an agent produces. Agents execute within those constraints. This is precisely why the trust numbers matter: because only 29% of developers trust AI accuracy, the factory must produce evidence — test results, diffs, acceptance checkpoints — that a human can verify. Code owning the graph makes that possible, because each step's acceptance is defined and checkable, not a judgment call buried in prose.

As TrueFoundry frames it, engineers define intent, acceptance criteria, govern access, and review evidence — while the agent-native system does more planning, implementation, testing, and review. The factory is not replacing judgment; it is industrializing the execution side of judgment.

## Common Pitfalls and How to Avoid Them

- **Leaving control in the prompt.** The most common failure is letting the agent decide sequencing and success. Fix: move the graph into deterministic Python and treat the agent as a bounded node.
- **Untracked prompts.** If prompting changes are not versioned, you cannot reproduce a result or review a regression. Fix: keep prompts in `adw_data/prompt_engineering/` as data.
- **Over-engineering the factory.** Adding an ingest endpoint or external orchestration dependencies breaks the "stamp into any repo" property. Fix: use the query-as-state design and stay self-contained.
- **Claiming autonomy you do not have.** Presenting "attributed to agents" as unreviewed automation undercuts the trust the whole model depends on. Fix: keep human acceptance in the loop and say so.
- **Ignoring cost per iteration.** A workflow that costs too much per run gets abandoned. Fix: apply model routing, caching, and lean schemas from day one.

## Getting Started: Your First Repeatable Software-Factory Workflow

1. **Pick one boring, repeated task.** Choose a workflow your team runs constantly — plan a feature, scaffold a module, run a test suite, write docs — not the most ambitious thing you can think of.
2. **Write the Python control plane first.** Define the steps, ordering, retries, and acceptance checks before you think about prompts.
3. **Bound the agent.** Give the agent a narrow role within one step and make its output plug into a checkable acceptance gate.
4. **Stamp the layout.** Create `adws/`, `adw_data/prompt_engineering/`, and `sssf.config.yaml` in the target repo.
5. **Package the thin skill.** Write a discoverable SKILL.md that points to the full factory detail.
6. **Add cost controls.** Route models per step, cache prompts, and keep tool schemas lean.
7. **Iterate on evidence.** Run it, review the test results and diffs, tighten acceptance, and reversion the workflow.

You do not need a platform or special infrastructure to start. The super simple software factory is deliberately a single skill you can stamp into any repository today, with deterministic code doing the deciding and agents doing the proposing.

## FAQ

**What is a software factory agent skill?**
A software factory agent skill is a named, reusable package that combines deterministic Python orchestration, tracked prompts, and bounded AI agents into one repo-stamped capability. It turns a repeated software task into a workflow any team can run with predictable results.

**Why does deterministic code matter more than the AI model?**
Because consistency, not peak cleverness, is what makes workflows scalable. If each agent run produces a different plan and quality bar, you cannot build on it. Moving the control plane into versioned, testable Python guarantees repeatable sequencing, retries, and acceptance — so results hold even when the model changes.

**How many real teams are actually running these factories?**
The signals are strong: Uber attributes 70%+ of PRs to agents with 3,600+ built skills; Gartner says 93% of IT leaders plan autonomous agents within two years; and Anthropic's skills pattern reached roughly 176K GitHub stars by mid-2026.

**Do agents replace human engineers in a software factory?**
No. Humans own intent, acceptance criteria, governance, and evidence review; agents own planning, synthesis, formatting, and execution. Because only 29% of developers trust AI accuracy, human review of evidence is the load-bearing part of the model.

**Can I start a software factory without buying infrastructure?**
Yes. The super simple factory is a single skill stamped into any repository — deterministic Python modules, tracked prompts, and one config file. You need no separate orchestration platform or ingest endpoint to begin.
