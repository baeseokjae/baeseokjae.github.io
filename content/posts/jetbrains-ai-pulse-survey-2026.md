---
title: "JetBrains AI Pulse Survey 2026: 85% of Developers Now Use AI"
date: 2026-05-24T06:05:17+00:00
tags: ["jetbrains", "ai-tools", "developer-survey", "github-copilot", "claude-code", "cursor", "ai-coding"]
description: "JetBrains surveyed 10,000+ developers in Jan 2026: 85-90% use AI, but only 29% trust it. Full breakdown of tool market share, productivity data, and what it means."
draft: false
cover:
  image: "/images/jetbrains-ai-pulse-survey-2026.png"
  alt: "JetBrains AI Pulse Survey 2026: 85% of Developers Now Use AI"
  relative: false
schema: "schema-jetbrains-ai-pulse-survey-2026"
---

JetBrains surveyed over 10,000 professional developers across 8 languages in January 2026 and found that 85-90% now use AI tools regularly — but only 29% trust the output to be accurate. That trust gap, more than the adoption numbers, defines the state of AI-assisted development in 2026.

## JetBrains AI Pulse Survey 2026: What It Is and Why It Matters

The JetBrains AI Pulse Survey is a recurring research program that tracks how professional developers actually use AI tools at work — not what they intend to use, not what they experiment with at home, but what ends up in their daily workflows. The January 2026 wave covered 10,000+ professional developers across 8 languages (English, German, French, Spanish, Portuguese, Russian, Chinese, and Japanese), making it one of the largest and most globally representative developer AI surveys conducted to date. Unlike analyst surveys that ask "are you excited about AI?", JetBrains asks about specific tools, specific tasks, and specific outcomes — yielding data that teams can actually act on when building AI strategy. The survey runs in waves (previous waves covered April-June 2025 and September 2025), so researchers can track trends over time rather than reporting a single snapshot. This longitudinal design is what makes it possible to spot things like Claude Code's 6x adoption surge or GitHub Copilot's growth stall — patterns invisible in single-wave surveys.

## Key Finding #1 — 85-90% of Developers Now Use AI (But Trust Lags Far Behind)

Eighty-five to ninety percent of professional developers now use AI tools as part of their regular coding workflow, according to JetBrains' January 2026 AI Pulse Survey of 10,000+ developers. But a second number cuts against that headline: only 29% trust AI-generated code to be accurate. Sixty-one percent of developers agree that AI "often produces code that looks correct but isn't reliable" — and only 48% say they always review AI-assisted code before committing. This is not a story of widespread AI enthusiasm; it is a story of widespread AI use alongside deep skepticism. The gap between adoption (85-90%) and trust (29%) is the defining tension in professional development workflows right now. Teams that treat this gap as a problem to solve — by investing in code review tooling, AI output validation processes, and structured verification checklists — will capture more of the real productivity benefit than teams that assume trust will follow automatically from adoption.

### Why the Trust Gap Matters More Than Adoption Numbers

The 29% trust figure should recalibrate how teams budget for AI tooling. If 85-90% of developers use AI but only about a third trust the output, it means most usage involves a verification step that takes real time. JetBrains data confirms this: developers who regularly use AI spend an average of 11.4 hours per week reviewing AI-generated code — compared to just 9.8 hours actually writing new code. The verification burden is already larger than the writing burden, and this will grow as AI handles larger and larger code chunks. The practical implication: AI tooling budgets should include investment in review and validation infrastructure, not just in the AI tools themselves.

### What Developers Actually Use AI For

AI adoption is highest for tasks with tight feedback loops — code completion, generating boilerplate, writing unit tests, and explaining unfamiliar code. It drops sharply for tasks that require architectural judgment, compliance knowledge, or domain-specific correctness (security, performance-critical paths, data model design). Only 13% of developers report using AI across the full software development lifecycle (SDLC). The other 87% use AI for a subset of tasks, clustering in the middle of the SDLC (write/test) rather than at the edges (plan/deploy/monitor).

## Key Finding #2 — The AI Tool Market Share Battle: GitHub Copilot vs Cursor vs Claude Code

GitHub Copilot leads workplace adoption at 29%, but Cursor and Claude Code have both hit 18% — making it a genuine three-way contest for the professional AI coding tool market as of January 2026. GitHub Copilot's awareness is at 76%, far ahead of the field, but that advantage has not translated into growing usage: adoption has stalled year-over-year while both Cursor and Claude Code surged. Cursor grew from single-digit adoption in early 2025 to 18% by January 2026. Claude Code's trajectory is even sharper: awareness climbed from 31% in April-June 2025 to 49% in September 2025 to 57% by January 2026, while adoption grew from roughly 3% to 18% — a 6x increase in under a year. JetBrains AI Assistant sits at 9%; Junie at 5%. Google Antigravity, launched in November 2025, already reached 6% adoption by January 2026 — a strong debut that signals the market is not yet settled.

### GitHub Copilot's Stalled Growth: What Happened

GitHub Copilot's stall is partly a product maturity story and partly a market maturity story. Early AI coding tool adoption was driven by developers who wanted any AI in their editor — Copilot was first, familiar, and bundled with GitHub. As the market matured, developers grew more selective. The shift, as JetBrains researchers describe it, is toward "best-of-breed agents" rather than ecosystem bundles. Developers are choosing tools based on output quality and workflow fit rather than vendor relationship. GitHub Copilot's IDE integration remains strong, but for agentic tasks — multi-step code generation, codebase-wide refactoring, autonomous test writing — users are finding alternatives more capable.

### Claude Code's 6x Adoption Surge: The Data Behind the Rise

Claude Code's growth from ~3% to 18% workplace adoption between April 2025 and January 2026 is the standout trend in this survey. Two metrics explain why: CSAT of 91% and NPS of 54 — the highest product loyalty scores in the AI coding tool market. In US and Canadian markets, adoption hit 24%, indicating stronger early traction in English-speaking enterprise environments. The surge aligns with Claude Code's October 2025 GA release and its focus on agentic workflows: rather than just completing lines of code, it handles multi-step tasks autonomously, which maps to where developer demand is actually growing.

| Tool | Workplace Adoption (Jan 2026) | Awareness | CSAT | NPS |
|---|---|---|---|---|
| GitHub Copilot | 29% | 76% | — | — |
| Cursor | 18% | ~50% | — | — |
| Claude Code | 18% | 57% | 91% | 54 |
| JetBrains AI Assistant | 9% | — | — | — |
| Google Antigravity | 6% | — | — | — |
| Junie | 5% | — | — | — |

## Key Finding #3 — The Agentic Revolution Is Already Here (22% and Climbing)

Twenty-two percent of developers already use AI coding agents — software that takes multi-step actions autonomously rather than just generating completions — and 66% of companies plan to adopt agents within the next 12 months, according to the JetBrains January 2026 AI Pulse Survey. This is not a future trend; it is a present adoption wave that is about to hit the majority of engineering organizations. AI agents differ from autocomplete tools in a critical way: they do not just suggest; they act. An agent can read a GitHub issue, open the relevant files, write a fix, run the tests, update the PR description, and request review — all without a human in the loop for each step. For engineering teams, this changes the role of the developer from writer to reviewer, and changes the risk profile of the codebase. Code that was written by a human with deep context is now being supplemented — and in some workflows, replaced — by code written by an agent that has read the context but may not understand the constraints.

### What "Using an Agent" Actually Means in Practice

Among the 22% who report using AI coding agents, usage varies widely. The most common patterns: using Claude Code or Cursor's agent mode for autonomous feature implementation (given a spec, generate the working code); using AI agents for test generation across a codebase; using agents for code review on PRs (adding comments, flagging style issues). Less common but growing: agents with filesystem and terminal access running autonomously for multi-hour coding sessions. The 66% company adoption figure for the next 12 months suggests this will become a mainstream workflow by late 2026 — which means companies that do not have a review process for AI-agent-generated code are already behind.

## Key Finding #4 — AI Across the Full SDLC: The 13% Problem

Only 13% of developers use AI tools across the full software development lifecycle — from planning and design through coding, testing, deployment, and monitoring — as of the January 2026 JetBrains AI Pulse Survey. The other 87% use AI for a subset of tasks, and the distribution is uneven: AI adoption is highest in the middle (code generation, unit tests) and lowest at the ends (architecture planning, production monitoring, incident response). This creates an AI adoption pattern that is wide but shallow: many developers touch AI tools, but few have integrated them deeply into every phase of their work. The 13% figure is also a ceiling metric — it represents the developers who have done the work to integrate AI into every major workflow, not just the easy ones. Crossing that threshold requires deliberate experimentation with AI in uncomfortable contexts: requirements analysis, design review, post-incident retrospectives.

### Why AI Adoption Stalls Before Full SDLC Integration

Three barriers account for most of the gap between 85-90% partial adoption and 13% full SDLC integration. First, trust: developers do not trust AI to make architecture decisions or security assessments, and that skepticism is largely warranted given current model limitations. Second, tool coverage: most AI coding tools are optimized for code generation and autocomplete; they do not have good interfaces for planning, monitoring, or incident response workflows. Third, process inertia: teams have existing workflows for requirements, design, and deployment that are hard to change even when AI tooling is available.

## Key Finding #5 — Productivity Is Real (4.2x More Durable Code), But So Is the Verification Burden

Regular AI users produced 320% (4.2x) more durable code than non-users in JetBrains' April 2026 Impact on Developer Workflows study, and increased their total code output by 25% from 2024 to 2025. These are the productivity numbers that make AI tooling investment cases compelling — but they come with a significant qualifier: regular AI users spend 11.4 hours per week reviewing AI-generated code, compared to 9.8 hours writing new code. The verification burden is already larger than the creation burden for heavy AI users. JetBrains researchers flag a second concern: AI redistributes developer workflows in ways that developers themselves do not fully perceive. Developers who use AI heavily may be producing more code, but may also be spending less time on the kind of deep problem-solving that builds architectural intuition. Over a multi-year horizon, this could mean that AI-assisted developers produce more output while developing fewer of the judgment skills needed to validate what they produce.

### What "Durable Code" Means in JetBrains' Methodology

JetBrains defines durable code as code that passes review without major revisions and does not require significant rework within 30 days of merge. The 4.2x figure compares regular AI users (5+ days per week) against developers who use AI rarely or never. The gap is large enough to make the productivity case for AI tooling unambiguous — but it does not address what happens when AI-generated code makes it through review and fails later in production, a failure mode that does not show up in the durable code metric.

## What JetBrains Is Doing About It: AI Assistant, Junie, and JetBrains Central

JetBrains AI Assistant (9% adoption) and Junie (5% adoption) sit well below GitHub Copilot, Cursor, and Claude Code in market penetration — a notable position for a company whose IDEs (IntelliJ IDEA, PyCharm, WebStorm, GoLand) are used by millions of professional developers daily. JetBrains' response to this gap is JetBrains Central, announced in 2025 as a central coordination layer for AI tools within the JetBrains ecosystem. Rather than competing head-to-head with Claude Code or Cursor on raw AI capability, JetBrains is positioning Central as an orchestration and integration layer — connecting AI tools, managing context across a project, and providing the IDE-deep integration that standalone agents lack. Junie, specifically, is designed as an autonomous coding agent that runs within the JetBrains IDE context, with access to project structure, run configurations, and test results that a standalone agent cannot easily reach.

### JetBrains' Competitive Position: Strengths and Gaps

JetBrains' core strength is IDE depth: their tools have unmatched project model integration, static analysis, and refactoring capability. The challenge is that agentic AI workflows are increasingly operating outside the IDE — in terminals, CI pipelines, and browser-based tools. If the future of AI-assisted development is agents running autonomously in a cloud environment rather than assistants embedded in a desktop IDE, JetBrains' moat narrows. The 9%/5% adoption figures for AI Assistant and Junie suggest developers using JetBrains IDEs are reaching for Claude Code, Cursor, or Copilot as their primary AI layer rather than the native tools.

## What These Survey Results Mean for Developers in 2026

The JetBrains AI Pulse Survey data collectively paints a picture of a professional development community that has fully embraced AI as a workflow component but has not yet built the processes to use it safely at scale. Eighty-five to ninety percent use it; 29% trust it; only 48% always review it before committing. That combination — widespread use, low trust, inconsistent review — is a recipe for accumulated technical debt that will take years to clean up. For individual developers, the most actionable takeaway is to get explicit about review practices now, before AI usage scales further on your team. For teams, the data makes a clear case for investing in structured AI code review processes, not just AI tooling licenses. And for engineering leaders, the 66% company adoption figure for agents within 12 months means the agentic shift is not something to evaluate — it is something to prepare for.

### How to Read the Tool Market Share Numbers

The 29%/18%/18% split between Copilot, Cursor, and Claude Code should not be read as a horse race where only the winner matters. Most developers in the JetBrains survey use multiple tools: a general-purpose chatbot (ChatGPT, Claude.ai) for exploratory questions, an AI coding assistant embedded in their editor for completions, and sometimes a separate agent for larger tasks. The fragmentation is real — 74% use specialized AI developer tools, but the average developer is not committed to one vendor. This means switching costs are lower than in previous software categories, and the market will continue to shift rapidly based on model quality and feature releases.

## How to Choose Your AI Stack Based on the JetBrains Data

Choosing an AI coding stack in 2026 is less about picking a winner and more about matching tool capabilities to your actual workflow. For inline completions in a JetBrains IDE, AI Assistant or Copilot integrate more smoothly than standalone agents. For agentic tasks — give it a GitHub issue and get a working PR — Claude Code's 91% CSAT and 6x adoption growth suggest it is the current benchmark. For teams where Cursor's local-first model and codebase indexing matter, 18% adoption indicates a real user base with strong opinions. The right approach: run a structured 30-day trial with 2-3 developers per tool, measure code review time, defect rate, and developer NPS, and choose based on your data rather than market share figures. The JetBrains survey tells you where the market is going; your team's workflow determines which tool fits.

### Questions to Ask Before Picking an AI Coding Tool

Before committing to any AI coding tool at the team level, get clear answers to: Does it support our primary IDE and language? What is our review process for AI-generated code, and does the tool make that easier or harder? Does it handle the specific task types where we want help most (completions, test generation, agentic tasks)? What are the data privacy terms — does code leave our environment? How does it handle codebase-wide context vs file-by-file generation? The JetBrains data shows tool choice is consequential — CSAT and NPS vary significantly across tools — so a structured evaluation beats defaulting to whatever tool is already installed.

## FAQ: JetBrains AI Pulse Survey 2026

**What did the JetBrains AI Pulse Survey 2026 find?**

The January 2026 survey of 10,000+ developers found that 85-90% use AI tools regularly, but only 29% trust AI-generated code to be accurate. GitHub Copilot leads workplace adoption at 29%, with Cursor and Claude Code both at 18%.

**How fast did Claude Code grow according to JetBrains?**

Claude Code grew 6x in workplace adoption from approximately 3% in April-June 2025 to 18% in January 2026. In US and Canadian markets, adoption reached 24%. Claude Code also recorded the highest CSAT (91%) and NPS (54) of any AI coding tool in the survey.

**What is the trust gap in AI coding tools?**

The trust gap refers to the difference between AI adoption (85-90%) and trust in AI output (29%). Sixty-one percent of developers say AI "often produces code that looks correct but isn't reliable," and only 48% always review AI-assisted code before committing.

**What percentage of developers use AI agents?**

Twenty-two percent of developers already use AI coding agents as of January 2026, and 66% of companies plan to adopt agents within the next 12 months, according to JetBrains' AI Pulse Survey.

**Does AI actually improve developer productivity?**

JetBrains' April 2026 impact study found regular AI users produced 4.2x more durable code than non-users and increased output by 25% year-over-year. However, heavy AI users also spend 11.4 hours per week reviewing AI-generated code — more time than they spend writing new code (9.8 hours).
