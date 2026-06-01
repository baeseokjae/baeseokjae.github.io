---
title: "Codeium to Windsurf: The Full History and What Changed"
date: 2026-05-31T12:08:14+00:00
tags: ["windsurf", "codeium", "ai-ide", "history", "developer-tools"]
description: "From a GPU startup to a $3B AI IDE: the complete story of how Codeium became Windsurf and what it means for developers in 2026."
draft: false
cover:
  image: "/images/codeium-windsurf-history-2026.png"
  alt: "Codeium to Windsurf: The Full History and What Changed"
  relative: false
schema: "schema-codeium-windsurf-history-2026"
---

Codeium became Windsurf because the product outgrew its original identity: what started as an autocomplete plugin for VS Code transformed into a full AI-native IDE with an agentic reasoning engine, and the old brand no longer fit. The rebrand in April 2025 was a formality — the real identity shift happened in November 2024 when the Windsurf Editor launched and attracted one million developers in four months.

## Origins: How a GPU Startup Became an AI Code Editor (2021–2022)

Windsurf's origin story is one of the more unusual pivots in recent startup history. The company that would become Windsurf was founded in 2021 as **Exafunction** — not a developer tools company at all, but a GPU optimization startup. MIT graduates Varun Mohan and Douglas Chen built Exafunction to help companies run machine learning inference workloads more efficiently, a profitable infrastructure business backed early by Kleiner Perkins, Greenoaks Capital, and General Catalyst with combined early funding exceeding $200 million. By conventional startup logic, there was no reason to pivot.

But Mohan and Chen were watching something shift in late 2021: GitHub Copilot launched technical preview in June 2021, and within months it was clear that AI-assisted coding was going to be a category-defining product. The core technology Exafunction had built — fast, efficient model serving for transformer-based models — was exactly what a code AI product needed. Rather than license that infrastructure capability, the founders decided to use it directly. In October 2022, they launched a beta of their own AI coding product and renamed the company **Codeium**. The GPU optimization business was wound down. The bet was that being close to the developer would matter more than selling infrastructure to others who were building developer tools.

The product that launched was a multi-IDE plugin: autocomplete-first, supporting VS Code, JetBrains, Neovim, Emacs, and eventually 40+ environments. The pricing decision — free for individual developers — was deliberate. GitHub Copilot cost $10/month. Codeium would be free, funded by enterprise contracts. It was a classic bottom-up distribution play, and it worked.

## Codeium's Rise: Building a Developer-First Plugin Empire (2023–2024)

Codeium's growth from late 2022 through 2024 was driven by a combination of product quality and aggressive free-tier availability that competitors couldn't match. The company grew from under **1,000 users in early 2023 to over 1 million downloads by February 2024** — roughly 14 months of growth without paid acquisition. That's fast by any measure, and it happened primarily through word of mouth and developer community adoption.

The product during this period was squarely a plugin story. Codeium lived *inside* your existing IDE — VS Code, JetBrains, Vim, whatever you preferred. It enhanced your workflow rather than replacing it. The core features were multi-line autocomplete, an inline chat assistant for asking questions about selected code, and a search tool for navigating large codebases. Compared to Copilot, the autocomplete quality was competitive, and the free tier made it an easy recommendation for individual developers and open source projects.

By 2024, the team had grown to around 100 engineers, the enterprise customer base was expanding, and ARR reached approximately $12M by Q4 2024. Those are good numbers for a developer tools startup, but the competitive landscape was shifting fast. Cursor had launched in 2023 and was building something different: not a plugin, but a VS Code fork where the AI was a first-class citizen of the IDE itself. Cursor's agent features — the ability to let the AI write code across multiple files autonomously — were resonating with developers in a way that plugin-based autocomplete wasn't going to match. Codeium needed to build the IDE, not just the plugin.

## The Windsurf Editor Launch: From Plugin to Full Agentic IDE (November 2024)

The Windsurf Editor launched in **November 2024** and changed everything about how the company operated. Unlike the Codeium plugin, which sat inside an existing IDE, the Windsurf Editor *was* the IDE — a fork of VS Code that could import your existing settings, extensions, themes, and keyboard shortcuts, but with AI woven into the fabric of the environment rather than bolted on as a sidebar. The central feature was **Cascade**, an agentic AI system with two modes: Write mode, where the AI makes direct code changes across multiple files autonomously, and Chat mode, for context-aware conversation about your entire codebase.

Cascade wasn't just smarter autocomplete — it could understand a high-level task ("refactor this authentication module to use JWT"), plan a sequence of file edits, execute them, run tests, and iterate based on results. Other features at launch included live preview of webpage changes before applying them, MCP integration pulling context from GitHub PRs, Slack, Jira, and Notion, and Codemaps — AI-annotated visual maps of code structure showing grouped sections, trace guides, and precise line-level linking. No competitor has since shipped an equivalent to Codemaps.

The adoption numbers were striking: **10,000+ users in the first two days**, hundreds of thousands within weeks, and **1 million developers within four months** of launch. By March 2025, ARR had jumped to **$40 million** — more than tripling from the Q4 2024 baseline of $12M. The IDE bet was working, and it was working faster than anyone had anticipated. Those growth numbers set the stage for both the brand decision in April 2025 and the acquisition chaos that followed in May.

## The Official Rebrand: Why 'Codeium' Became 'Windsurf' (April 2025)

The formal company rebrand from Codeium to Windsurf happened in **April 2025**, roughly five months after the IDE launched. By that point, the new IDE had already become the product that defined the company — the old plugin brand was creating confusion rather than continuity. Developers who found Windsurf through the IDE were discovering a "Codeium" brand they'd never heard of. Developers who knew Codeium from the plugin era were unsure whether Windsurf was the same company or a competitor.

The rename resolved the ambiguity cleanly: the company was now Windsurf, the IDE was Windsurf, and the old Codeium plugin was relaunched as the **Windsurf plugin** — the same multi-IDE extension experience, under the new brand. The underlying product for plugin users didn't change significantly; the Windsurf plugin still supported JetBrains, Neovim, and other environments where a full IDE fork wasn't practical. But the brand change signaled a philosophical shift: Codeium's identity had been "AI assistant inside your editor." Windsurf's identity was "IDE where AI and developer are equal partners."

At the time of the rebrand, ARR had reached **$100 million** — an 8x jump from $12M just six months earlier. The company had approximately 200 employees and 350+ enterprise customers. This growth trajectory — $0 to $100M ARR in under three years without big-tech backing — made Windsurf one of the fastest-growing independent developer tool companies ever, and it triggered the acquisition frenzy that would define the rest of 2025.

## What Actually Changed for Developers — Then vs. Now

The practical differences between the old Codeium plugin experience and the current Windsurf IDE are significant enough to warrant a direct comparison. Understanding what changed — and what stayed the same — is the core question for any developer who used Codeium and is now evaluating whether to migrate.

The Codeium plugin era featured single-file context awareness: the AI could see the file you were working in, plus some imports, but struggled with large multi-file reasoning tasks. Autocomplete was fast and high-quality. The chat assistant was useful for explaining code or generating snippets, but couldn't execute multi-step changes autonomously. Installation was simple — add an extension to your existing IDE and sign in. Free tier was unlimited with no credit cap.

The Windsurf IDE era is architecturally different. Cascade maintains context across your entire repository. It can read test output, observe build failures, and make corrective changes without prompting. The Codemaps feature provides a structural view of your codebase that no competitor has matched. MCP integration means the IDE has context from outside the codebase: your PRs, your issue tracker, your team communication. The trade-off is that Windsurf IDE is a separate application — you're running a VS Code fork, which means occasional plugin compatibility gaps and a free tier now capped at 25 credits/month.

| Feature | Codeium Plugin (2023) | Windsurf IDE (2026) |
|---|---|---|
| Context scope | Single file / imports | Full repository + external tools |
| Agentic execution | No | Yes (Cascade Write mode) |
| Multi-file edits | No | Yes |
| MCP integration | No | Yes (GitHub, Slack, Jira, Notion) |
| Codemaps | No | Yes (unique feature, no competitor match) |
| IDE requirement | Existing VS Code / JetBrains | Windsurf IDE (VS Code fork) |
| JetBrains support | Yes (native plugin) | Plugin only |
| Free tier | Unlimited | 25 credits/month |
| Model powering AI | Third-party LLMs | SWE-1.5 (Cognition, 950 tok/sec) |
| Pricing (paid) | Enterprise only | $15/mo Pro, $30/user/mo Teams |

## The $5 Billion Drama: OpenAI, Google, and Cognition's Three-Way Split (2025)

The summer of 2025 produced one of the more unusual acquisition sequences in tech history: three separate deals, three different buyers, all overlapping within a two-month window — and the original bidder never actually closed.

**OpenAI's offer** came first. In May 2025, OpenAI offered approximately **$3 billion** to acquire Windsurf outright. The deal made strategic sense: OpenAI needed a high-quality IDE distribution channel, and Windsurf's IDE plus Cascade system would give them a direct distribution channel for their models. The acquisition **collapsed over Microsoft IP disputes** — Microsoft, which has a strategic partnership with OpenAI, had concerns about Windsurf IP crossing into territory overlapping with GitHub Copilot and the VS Code ecosystem. The deal died without closing.

**Google's acquihire** moved in parallel and closed on **July 11, 2025**. Google agreed to pay **$2.4 billion** to hire CEO Varun Mohan, CTO Douglas Chen, and approximately 40 core engineers — a talent acquisition plus a technology license, not a company acquisition. The founders and key technical staff transitioned to Google. This is structurally similar to Google's 2023 Inflection AI deal, where they hired most of the founding team without technically buying the company.

**Cognition AI's acquisition** closed three days later, on **July 14, 2025**. Cognition — makers of Devin, the autonomous software engineering agent — acquired the remaining Windsurf business for approximately **$250 million**. At closing, Windsurf had **$82M ARR, 350+ enterprise customers, and 210 employees**. The three-way outcome was unusual but internally coherent: the founders went to Google, the product and engineering team went to Cognition, and the company was absorbed. By September 2025, Cognition's valuation had reached **$10.2 billion**, two months after the acquisition closed.

## Windsurf Under Cognition: SWE-1.5, Codemaps, and Devin Integration (2026)

The Windsurf that developers use in 2026 is substantively different from the product that launched in November 2024, in ways that reflect Cognition's priorities rather than the original Codeium team's. Cognition has invested heavily in three areas: a proprietary model, a new visualization feature, and integration with their flagship Devin agent — creating a product that no longer relies on third-party LLMs and pairs interactive development with fully autonomous execution.

The most significant change is the model. Windsurf now runs on **SWE-1.5**, Cognition's proprietary software engineering model, rather than third-party LLMs like Claude or GPT. SWE-1.5 runs at **950 tokens per second** — Cognition reports this as 13x faster than Claude Sonnet 4.5 at comparable task quality. For agentic coding tasks, inference speed matters: when Cascade is autonomously editing, running tests, and iterating, latency accumulates across dozens of model calls. A 13x speed advantage translates to meaningfully faster task completion, not just a benchmark improvement.

**Codemaps**, which launched with the original Windsurf Editor, has matured into the IDE's most visually distinctive feature: AI-annotated maps showing grouped sections, trace guides, and precise line-level linking across files. The feature is particularly useful for onboarding to large unfamiliar codebases. **Devin integration** is the longer-term strategic bet — Cognition's autonomous agent can now be dispatched directly from the Windsurf IDE for long-running tasks that exceed an interactive Cascade session: overnight refactors, bulk test generation, dependency migration. As of 2026, Windsurf has **1M+ active users** and **4,000+ enterprise customers**, with support for 40+ IDEs that rival Cursor (VS Code-only, no JetBrains) doesn't match.

## Should You Switch from the Codeium Plugin to Windsurf IDE?

The answer depends on your workflow, IDE preference, and what kind of AI assistance you actually use day to day. The decision isn't binary — the Windsurf plugin still exists and is the right choice for some workflows.

**Switch to Windsurf IDE if** you're doing complex, multi-file feature work where autonomous execution would save time. Cascade's Write mode — editing across files, running tests, iterating on failures — is genuinely better for these tasks than any plugin experience. If you use VS Code as your primary environment and don't have deep JetBrains dependencies, migration is low-friction: Windsurf imports your settings, extensions, and keybindings. The Codemaps feature alone is worth evaluating if you regularly onboard to large codebases.

**Stay with the Windsurf plugin if** you're in JetBrains (IntelliJ, PyCharm, WebStorm, Rider) or another non-VS Code environment. The Windsurf plugin supports 40+ IDEs natively; the Windsurf IDE is a VS Code fork. If switching IDEs is disruptive to your team or toolchain, the plugin gives you autocomplete and chat without changing your environment. The plugin also remains the right choice if you need full JetBrains feature parity — agentic capabilities on JetBrains are plugin-mode only, not IDE-mode.

**Consider the credit model** before committing. Free Codeium was genuinely unlimited — it was a core part of the go-to-market. Windsurf's free tier now includes 25 credits per month. For light users, that's fine. For developers who want Cascade's agentic features heavily, the $15/month Pro plan is the realistic baseline. The migration path from old Codeium is intentionally smooth: your account transfers, settings import, and enterprise contracts generally converted automatically. The product changed profoundly; the onboarding didn't need to.

---

## FAQ

**What happened to Codeium?**
Codeium was rebranded to Windsurf in April 2025, after the Windsurf Editor IDE (launched November 2024) became the company's primary product. The old Codeium plugin continues as the "Windsurf plugin," available for VS Code, JetBrains, and 40+ other IDEs. The company was subsequently acquired by Cognition AI in July 2025 for approximately $250M.

**Is Windsurf the same as Codeium?**
Windsurf is the same company and successor product to Codeium, but the product architecture is fundamentally different. Codeium was an IDE plugin that enhanced VS Code or JetBrains from inside. Windsurf is a full IDE (a VS Code fork) with an agentic AI system called Cascade that can autonomously edit files, run tests, and iterate. The Windsurf plugin is the closest equivalent to the original Codeium experience for non-VS Code users.

**Who owns Windsurf in 2026?**
Windsurf is owned by Cognition AI, which acquired the company on July 14, 2025 for approximately $250 million. The original founders — CEO Varun Mohan and CTO Douglas Chen — moved to Google via a separate $2.4 billion acquihire completed July 11, 2025. OpenAI had previously offered $3B to acquire Windsurf in May 2025, but that deal collapsed over Microsoft IP disputes.

**What is Cascade in Windsurf?**
Cascade is Windsurf's agentic AI system, introduced with the Windsurf Editor in November 2024. It operates in two modes: Chat mode for context-aware Q&A about your codebase, and Write mode for autonomous multi-file code editing. In Write mode, Cascade plans a sequence of changes, executes them across files, runs tests, and adapts based on results — without step-by-step human direction for each change. In 2026, Cascade runs on Cognition's SWE-1.5 model at 950 tokens/second.

**How does Windsurf compare to Cursor in 2026?**
The main differences are IDE support and model strategy. Windsurf supports 40+ IDEs via its plugin including JetBrains; Cursor is VS Code-only. Windsurf runs on Cognition's proprietary SWE-1.5 model at 950 tokens/second; Cursor uses third-party LLMs. Windsurf's Codemaps feature has no direct Cursor equivalent. Pricing: Cursor Pro is $20/month; Windsurf Pro is $15/month. Both offer agentic coding with autonomous multi-file editing, but only Windsurf integrates with Devin for fully autonomous async tasks.
