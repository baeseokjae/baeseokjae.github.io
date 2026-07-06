---
cover:
  alt: Cursor Background Agents Guide 2026
  image: /images/cursor-background-agents-2026.png
  relative: false
date: 2026-04-21 13:05:10+00:00
description: 'Complete guide to Cursor background agents in 2026: setup, pricing,
  Computer Use, best practices, and when to use them vs Claude Code or Codex.'
draft: false
schema: schema-cursor-background-agents-2026
tags:
- cursor
- ai-agents
- autonomous-coding
- developer-tools
- agentic-ai
title: 'Cursor Background Agents Guide 2026: Run Autonomous Coding Tasks in the Background'
---

Cursor background agents let you fire off a coding task — a bug fix, test suite, refactor, or feature — and walk away while a cloud VM handles it asynchronously, returning a pull request when it's done. Unlike in-editor Agent Mode that runs interactively beside you, background agents run in parallel on isolated remote machines, freeing you to work on something else entirely.

## What Are Cursor Background Agents?

Cursor background agents are cloud-hosted autonomous coding workers that run on dedicated virtual machines outside your local editor. Each agent receives a task description, checks out your repository, executes file edits using its own model and toolchain, and opens a pull request with the results — entirely without you watching. This is the architectural break from traditional AI coding assistants: instead of a synchronous conversation where you approve every step, you submit a task once and the agent works asynchronously in a remote sandbox. As of early 2026, Cursor reports that 35% of their internal merged PRs are created by background agents — a figure that signals how much trust the company itself places in the workflow. The agents support custom Dockerfiles, multi-platform access (desktop, web, mobile, Slack, GitHub), and, since February 24, 2026, full Computer Use capabilities including browser access, video recording, and remote desktop screenshots. The key architectural components are: contextual codebase awareness (the agent reads your repo before starting), task planning (it reasons about scope before editing), and conflict avoidance (it isolates to a git worktree so parallel agents never collide).

### Background Agents vs Agent Mode: The Core Difference

Background agents run remotely on cloud VMs, work asynchronously without user supervision, and deliver output as a PR. Agent Mode runs locally inside your editor session, operates interactively with you in the loop, and applies edits directly to your workspace. Choose background agents when the task is well-defined and parallelizable. Choose Agent Mode when you need exploratory back-and-forth, complex debugging, or tasks that require your architectural judgment at each step.

## How to Set Up and Use Cursor Background Agents

Setting up Cursor background agents takes under five minutes from the Cursor editor and requires a Pro plan or higher. Navigate to **cursor.com/agents** or open the Background Agents panel in the editor (the cloud icon in the sidebar). Connect your GitHub or GitLab account, disable Privacy Mode for the target repository, select the repo, write a task description, choose your model, and click Submit. The agent clones your repo into an isolated cloud VM, plans its approach using codebase-aware search tools, executes file changes, runs tests if you specified a test command in the acceptance criteria, and opens a PR for your review. You can monitor progress in real time from the Agents dashboard — each agent shows its current step, active tool calls, token usage, and any errors encountered. If a task goes in the wrong direction, you can cancel mid-run from the dashboard. Tasks can also be triggered from the Cursor mobile app or the Slack integration, which is useful for delegating work during code review sessions, standups, or when you're away from your desk. Multiple agents can run simultaneously, each in its own isolated git worktree.

### Writing an Effective Task Description

The quality of your task description determines 80% of the output quality. Background agents cannot ask clarifying questions mid-task the way interactive Agent Mode can. A strong prompt includes: the specific goal ("Add unit tests for the `UserAuthService` class covering all public methods"), the acceptance criteria ("All tests must pass with `npm test`"), any constraints ("Do not modify the existing method signatures"), and context pointers ("See `src/auth/UserAuthService.ts` and `src/__tests__/` for existing patterns"). Vague prompts like "improve the tests" lead to premature completion — the agent decides it's done when it isn't. Specific, verifiable goals with explicit acceptance criteria get dramatically better results.

### Enabling Privacy Mode Considerations

Background agents require disabling Cursor's Privacy Mode because the agent needs to send your code to remote infrastructure. For regulated industries (healthcare, finance, government), verify with your compliance team before enabling cloud agents. Privacy Mode disabling is a per-workspace setting; you can leave it enabled for sensitive repos and disabled for open-source or internal tooling work.

## Cloud Agents with Computer Use: The February 2026 Upgrade

On February 24, 2026, Cursor launched Cloud Agents with Computer Use, extending background agents with a full browser environment, video recording of every session, and remote desktop access for visual verification tasks. This upgrade means agents can now run end-to-end tests that require a real browser — loading your app, clicking buttons, taking screenshots of UI states, and verifying visual regressions. Each Computer Use session produces a video recording that you can review after the agent completes, giving you proof of what the agent actually did rather than just what it claimed to do. This capability closes a major gap compared to purely code-only agents: a background agent can now write a Playwright test, run it in a headless browser, capture a screenshot of the result, and include that screenshot in the PR description. The practical result is that agents can handle full-stack UI validation tasks that previously required developer attention.

### What Computer Use Enables That Code-Only Agents Cannot

Computer Use unlocks tasks requiring visual confirmation: screenshot regression testing, UI component validation, form submission flows, OAuth redirect sequences, and any workflow that depends on a real browser rendering engine. Before February 2026, background agents could only validate through CLI tools and test runners. With Computer Use, agents can verify that a CSS change doesn't break the mobile layout, that a login form redirects correctly, or that a new dashboard component renders without console errors — then attach screenshot evidence to the PR.

## Pricing and Real Costs: Plans, MAX Mode, and Budget Planning

Cursor background agents always run in MAX mode, which applies a 20% surcharge on top of the underlying model credit cost. That surcharge adds up quickly: daily background agent users typically spend $60–$100/month in total Cursor costs according to Morph's 2026 analysis. Understanding the tier structure is essential before scaling usage. The **Hobby** plan has no background agent access. **Pro** at $20/month includes agents but overages are common once you exceed the included credits. **Pro+** at $60/month is a better fit for solo developers who run multiple agents per day. **Ultra** at $200/month is described as "best value" for heavy users, offering the highest credit allocation before per-credit overages kick in. **Teams** at $40/user/month works for organizations with shared credit pools. A practical budget rule: if you're running 3–5 background agent tasks per day, start with Pro+ and monitor credit consumption for the first week before committing to a tier.

### The MAX Mode Surcharge Explained

MAX mode ensures agents use the most capable model available for the task rather than defaulting to a cheaper model to save credits. While this produces better results, the 20% surcharge is applied before you see credit consumption in the dashboard. To control costs, write tightly scoped tasks that complete in fewer agent steps — a 1,000-step agent run costs more than two 400-step runs for equivalent work. Set task scope carefully: background agents don't stop when they "feel" done if there's more code to touch, so overly broad prompts can spiral into large credit charges.

## When Background Agents Shine — and When They Don't

Cursor background agents excel at tasks that are parallelizable, well-defined, have verifiable completion criteria, and don't require real-time architectural input. The best use cases from the 2026 developer workflow evidence are: (1) **Test generation** — write all missing unit tests for a module, following existing patterns; (2) **Bug fixes with clear reproduction steps** — "this function throws TypeError when input is null, fix it and add a test"; (3) **Code migrations** — "update all API calls from v2 to v3 schema across the codebase"; (4) **Documentation** — "write JSDoc for all exported functions in `src/utils/`"; (5) **Pattern-following features** — "add a new endpoint `/api/v1/orders` that follows the same pattern as `/api/v1/users`". Background agents underperform on exploratory debugging without a reproduction case, architectural decisions that require codebase-wide judgment, tasks with ambiguous success criteria, and anything where the agent needs to ask you a question mid-task.

### Decision Framework: Background vs Interactive

Use this quick decision filter: Is the task fully specifiable in writing? → If yes, background agent is viable. Does completion have an objective pass/fail test? → If yes, background agent is preferred. Does the task require real-time architectural feedback? → If yes, use Agent Mode. Is the task exploratory ("figure out why X is slow")? → Use Agent Mode. Is speed critical (need results in 2 minutes)? → Use Agent Mode for small tasks since background agents have startup overhead.

## Cursor Background Agents vs Claude Code

Cursor background agents and Claude Code represent two different philosophies in AI-assisted development. Cursor background agents run on remote cloud VMs, work asynchronously, operate with 70K–120K usable context tokens, and deliver output as pull requests. Claude Code runs locally in your terminal, operates as an interactive conversation, offers up to 200K token context, and modifies your local files directly. The usable context gap matters for large monorepos: Claude Code can hold more of your codebase in context at once, which helps on tasks that span many files or require understanding deeply interconnected systems. Cursor background agents compensate with parallelism — you can run five agents at once across five separate tasks, something Claude Code's interactive model doesn't support natively. Claude Code also excels at exploratory work: "figure out why this test flakes" is a conversation, not a specification. Cursor background agents excel at specification-first work where you can write down exactly what done looks like before starting.

| Dimension | Cursor Background Agents | Claude Code |
|---|---|---|
| Execution location | Remote cloud VM | Local terminal |
| Interaction model | Async, fire-and-forget | Interactive conversation |
| Output format | Pull request | Local file edits |
| Context window | 70K–120K tokens | Up to 200K tokens |
| Parallelism | Native (multiple agents) | Requires worktrees |
| Best for | Well-defined, parallelizable tasks | Exploratory, context-heavy work |
| Privacy | Requires Privacy Mode off | Fully local |
| Internet access | Yes (Computer Use) | No by default |

## Cursor Background Agents vs OpenAI Codex

Cursor background agents and OpenAI Codex CLI (the agentic version launched in 2025) both target async autonomous coding but differ significantly in architecture and capability. Cursor background agents support multiple model backends, include Computer Use with browser access, allow custom Dockerfiles, and integrate natively with the Cursor editor ecosystem. OpenAI Codex agents use the `codex-1` model exclusively, do not have internet access by default (network is disabled in sandboxes), and focus purely on code-level changes without visual verification. Cursor background agents also have a programmatic-free limitation (no public API for triggering agents from CI/CD pipelines), while Codex can be invoked via the OpenAI API. For teams with existing OpenAI API integrations, Codex offers better pipeline automation. For teams already using Cursor as their primary editor, background agents offer a superior end-to-end experience with Computer Use and multi-model support.

| Feature | Cursor Background Agents | OpenAI Codex Agents |
|---|---|---|
| Internet access | Yes (Computer Use) | No (disabled by default) |
| Model options | Multiple (GPT-4o, Claude, etc.) | codex-1 only |
| Browser testing | Yes (video + screenshots) | No |
| Custom environment | Dockerfile support | Sandbox configuration |
| Programmatic API | No public API | Via OpenAI API |
| Editor integration | Native Cursor | CLI / API-first |
| Cost model | Credits + 20% MAX surcharge | Per-token API pricing |

## Best Practices for Background Agent Prompts

Writing effective background agent prompts requires a different mindset than writing interactive Agent Mode prompts. The agent cannot interrupt you to ask questions, so every ambiguity in your prompt becomes a judgment call the agent makes on its own — often incorrectly. Follow this structure for reliable results: **Goal** (one sentence, specific outcome), **Files/Scope** (exact paths or patterns to touch), **Constraints** (what not to change), **Acceptance Criteria** (how to verify done), **Reference Patterns** (link to similar existing code). For example: "Goal: Add rate limiting to the `/api/v1/auth/login` endpoint. Files: `src/api/auth/login.ts`, `src/middleware/`. Constraint: Do not change the request/response schema. Acceptance: `npm test` passes and `curl` to the endpoint returns 429 after 5 requests/minute. Reference: See `src/middleware/rateLimiter.ts` for existing pattern." This structure eliminates the top three failure modes: scope creep, schema changes, and untested implementations.

### Using Plan Mode Before Background Agent Submission

Before submitting a task to a background agent, use Cursor's Plan Mode (Shift+Tab in Agent Mode) to let the agent research your codebase and outline its approach. Review the plan, correct misunderstandings, and then use that plan as the task description for the background agent. This two-step workflow catches the most expensive failure mode: an agent that confidently executes the wrong approach for 200 steps. Saving plans to `.cursor/plans/` also creates team documentation of intent that survives the agent session.

## Customizing Agent Environments with Dockerfiles

Cursor background agents support custom Dockerfiles for configuring the VM environment before the agent starts work. This is critical for projects with native dependencies, specific Node.js/Python versions, database services, or build tools not in the default image. Place a `Dockerfile` in your repository root or specify a path in the agent configuration. The agent builds the image, starts the container, and runs your setup scripts before executing the task. A practical example for a TypeScript/Postgres project:

```dockerfile
FROM node:20-slim
RUN apt-get update && apt-get install -y postgresql-client
WORKDIR /workspace
COPY package*.json ./
RUN npm ci
```

For monorepos with multiple services, create service-specific Dockerfiles and point the agent at the relevant one per task. Custom environments dramatically reduce "works in agent, fails in CI" scenarios by ensuring the agent runs in the same environment as your tests.

## Running Multiple Agents in Parallel with Worktrees

Cursor background agents use native git worktrees to isolate parallel agent sessions — each agent works in its own branch and file tree, eliminating merge conflicts between concurrent tasks. You can submit five background agent tasks simultaneously and each will work independently. The practical workflow: submit Task A (add unit tests for module X), Task B (fix bug in module Y), and Task C (update documentation) all at once. Review the three PRs when they're done. This parallel execution model is background agents' strongest advantage over interactive tools. A single developer can effectively manage 10–20 background agent tasks in a day, reviewing PRs rather than directing each agent step-by-step. The bottleneck shifts from "time to write code" to "time to review code," which is a significantly more scalable constraint.

## Privacy, Security, and Enterprise Considerations

Background agents send your code to Cursor's cloud infrastructure, which means Privacy Mode must be disabled for cloud agent use. For enterprise teams, Cursor's Teams plan ($40/user/month) includes organization-wide settings, SSO, and dedicated infrastructure options. Before enabling background agents for regulated codebases, verify: (1) your data processing agreement with Cursor covers cloud agent processing; (2) secrets are not stored in plain text in the repository (use `.env` files excluded from git, not hardcoded credentials); (3) your security team has reviewed the expanded attack surface from remote VM access. The security surface area includes the VM itself, the git credentials provided to the agent, and any API keys the agent accesses during testing. Use repository-scoped credentials and rotate them after large agent sessions on sensitive codebases.

## Known Limitations in 2026

Cursor background agents have several documented limitations that affect real-world usage. **Premature completion** is the most common issue: an agent decides a task is "done" when it has made some progress, even if the full acceptance criteria aren't met. This is most frequent with vague prompts. **Cost surprises** happen when a task scope is broader than expected and the agent continues executing across hundreds of extra steps — always set a mental budget per task and check the Agents dashboard mid-run for long tasks. **No programmatic API** means you cannot trigger background agents from CI/CD pipelines, GitHub Actions, or custom scripts — they must be submitted via the Cursor UI or mobile app. **Privacy Mode requirement** blocks enterprise use cases where code must stay fully local. **Context window ceiling** at 70K–120K tokens limits performance on very large monorepos compared to local tools with full context access.

## Real-World Use Cases: What Teams Actually Delegate

The highest-value background agent use cases observed in 2026 deployment patterns are: **Test coverage fills** — agents write tests for code with low coverage following existing patterns; **API migration** — updating call sites from a deprecated API to a new one across hundreds of files; **Documentation generation** — writing or updating JSDoc/docstrings across a module; **Lint/formatting fixes** — applying a new ESLint or Prettier config to the entire codebase; **Security patches** — applying a known fix pattern (like escaping a SQL parameter) across all affected query sites. These tasks share a key property: they're tedious, rule-based, and don't require architectural judgment — exactly where background agents outperform and human developers underperform. Teams at Fortune 500 companies (Cursor claims 50%+ adoption) use background agents most heavily for the backlog of technical debt tasks that never make sprint planning.

---

## FAQ

**Can I use Cursor background agents on the Hobby plan?**
No. Background agents require at least the Pro plan ($20/month). The Hobby plan has no background agent access. For regular background agent use, Pro+ ($60/month) or Ultra ($200/month) are better fits due to higher credit allocations.

**Do Cursor background agents work on private repositories?**
Yes, background agents work with private repositories. You need to connect your GitHub/GitLab account with appropriate read/write permissions. Note that Privacy Mode must be disabled for cloud agents to access your code.

**How long does a typical background agent task take?**
Simple bug fixes or small test additions typically complete in 5–15 minutes. Larger tasks like writing a full test suite for a module or performing a multi-file migration can take 30–90 minutes. Tasks with Computer Use (browser testing) add overhead from browser startup and screenshot capture.

**Can background agents run tests automatically?**
Yes. Background agents can run your test suite as part of the task. Include the test command in your prompt's acceptance criteria ("run `npm test` and all tests must pass"). Agents with Computer Use can also run browser-based E2E tests and capture screenshots as verification.

**What's the difference between a background agent failing and succeeding poorly?**
A failing agent returns an error and stops — you're charged for the work done to that point. A poorly succeeding agent opens a PR that doesn't meet your criteria, which is harder to catch. This is why verifiable acceptance criteria in your prompt (specific test commands, exact output expectations) are critical — they give the agent a reliable definition of done rather than relying on its own judgment.