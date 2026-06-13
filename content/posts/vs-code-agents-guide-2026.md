---
title: "VS Code Agents Guide 2026: The Agent-Native Companion App"
date: 2026-06-13T16:04:34+00:00
tags: ["VS Code", "AI agents", "developer tools"]
description: "A practical VS Code agents guide for using Agent Sessions, worktrees, MCP, custom agents, and review gates in 2026."
draft: false
cover:
  image: "/images/vs-code-agents-guide-2026.png"
  alt: "VS Code Agents Guide 2026: The Agent-Native Companion App"
  relative: false
schema: "schema-vs-code-agents-guide-2026"
---

VS Code agents are turning the editor into a control plane for delegated software work: plan a task, run it in an isolated session, review diffs, give feedback, and decide what merges. This VS Code agents guide explains the 2026 workflow without treating agents as magic or replacing engineering judgment.

## What Are VS Code Agents in 2026?

VS Code agents are AI coding systems embedded in, or coordinated around, Visual Studio Code that can inspect a codebase, plan multi-step changes, edit files, run commands, and revise their work from feedback. In VS Code 1.115, Microsoft introduced the Visual Studio Code Agents preview companion app for Insiders, with parallel sessions, isolated worktrees, inline diffs, feedback, PR creation, and inherited VS Code customizations. That matters because agent work is no longer just a chat response pasted into an editor. A developer can delegate a scoped issue, monitor progress, review exact file changes, and keep merge authority. Stack Overflow's 2025 survey reported that 84% of respondents use or plan to use AI tools in development, but useful agent adoption depends on controlled workflows, not novelty. The takeaway: VS Code agents are best understood as reviewable work sessions, not autocomplete with a bigger context window.

In practice, the useful mental model is a junior-to-mid engineer with tools, memory, and a terminal, operating under your constraints. You provide the goal, repository context, acceptance criteria, and boundaries. The agent proposes or executes a path. You inspect the diff, tests, logs, and assumptions before the work lands.

### What Makes an Agent Different From Chat?

An agent differs from chat because it can carry a task through actions instead of only generating text. A chat panel can explain a failing test; an agent can inspect the test, edit the implementation, run the test again, and summarize the remaining risk. The distinction is not intelligence level. The distinction is permissioned action against a real workspace.

### What Should Developers Still Own?

Developers still own intent, scope, architecture, review, and production accountability. I do not let an agent decide whether to change a public API, weaken a security boundary, or merge a large refactor without review. The agent can produce the patch; the engineer must decide whether the patch fits the system.

## Why Does the VS Code Agents Companion App Change the Workflow?

The VS Code Agents companion app changes the workflow by separating agent execution from the main editor while preserving the developer's existing VS Code environment. The 1.115 preview describes a companion app that can run multiple tasks across repositories, use isolated worktrees, show inline diffs, accept feedback, create pull requests, and carry over customizations such as instructions, prompt files, custom agents, MCP servers, hooks, and plugins. That is a different product shape from a sidebar because multiple agents can work while the developer continues reviewing, coding, or triaging. The companion app also reduces context switching: the work still speaks VS Code, Git, terminal output, and PRs instead of living in a separate AI dashboard. For teams, the key benefit is operational discipline. Agent work becomes observable, interruptible, and comparable. The takeaway: the companion app matters because parallel agent work needs a queue, not another text box.

The small detail that changes daily practice is isolation. If an agent works in the active checkout, it can dirty your branch, collide with manual edits, or make it hard to separate experiments. If each session gets a worktree, you can run two feature attempts, one bug fix, and one test-generation task without mixing diffs.

### Why Are Worktrees So Important?

Worktrees are important because they give each agent a separate filesystem view backed by the same repository history. That keeps the main workspace stable while agent sessions create branches, edit files, and run commands. When the result is bad, you can abandon the worktree. When it is good, you can review and merge the branch like any other contribution.

### Where Does the Developer Spend Time Now?

The developer spends less time typing boilerplate edits and more time writing precise task briefs, watching failure signals, and reviewing diffs. That shift is not passive. A vague task still produces vague work. The highest leverage is writing acceptance criteria that an agent can test against.

## How Do VS Code Agents Compare With Copilot Chat, Agent Mode, Cursor, and Windsurf?

VS Code agents compare with Copilot Chat, agent mode, Cursor, and Windsurf by moving along a spectrum from conversational assistance to autonomous, multi-step task execution. Copilot Chat is best for questions, explanations, small edits, and quick code navigation. Agent mode adds task execution inside the editor. The VS Code Agents companion app extends that model into parallel, reviewable sessions with worktrees and PR handoff. Cursor and Windsurf are VS Code-derived environments that make agent-first workflows central to the IDE experience, while stock VS Code emphasizes extension compatibility and existing team setup. The Pragmatic Engineer's 2026 AI tooling survey analysis reported Claude Code as the most-loved tool at 46%, Cursor at 19%, and GitHub Copilot at 9%, while large enterprises often default to Copilot. The takeaway: choose based on workflow control, not leaderboard sentiment.

| Option | Best fit | Main tradeoff |
|---|---|---|
| Copilot Chat | Quick explanations, small edits, code lookup | Limited autonomy for full issue delivery |
| VS Code agent mode | Interactive task execution in the current editor | Can still compete with active local work |
| VS Code Agents companion app | Parallel delegated tasks, worktrees, PR review | Preview status and evolving UX |
| Cursor | Agent-first IDE habits and fast iteration | Forked editor workflow for teams standardized on VS Code |
| Windsurf | Integrated AI coding environment | Similar adoption and governance questions as other forks |
| Claude Code or Codex in terminal | Scriptable repository-level task work | Less native visual integration unless bridged back to VS Code |

### When Should You Stay in Stock VS Code?

You should stay in stock VS Code when your team depends on existing extensions, devcontainers, settings sync, security approvals, and enterprise identity controls. The switching cost of a forked editor is real in regulated or large organizations. If agent capability is available through VS Code, GitHub, or approved CLI tools, standardizing there may reduce operational friction.

### When Is an Agent-First IDE Worth It?

An agent-first IDE is worth it when the team values rapid autonomous iteration more than strict compatibility with a standardized editor setup. Small teams building greenfield products may accept a forked environment if the agent workflow is materially faster. The test is whether it improves reviewed, merged work, not whether demos feel impressive.

## What Is the Core Architecture Behind Agent Sessions, Worktrees, MCP, Tools, and Instructions?

The core architecture behind VS Code agents is a session model that combines repository context, model reasoning, tool permissions, workspace isolation, and persistent instructions. Agent Sessions act as the visible unit of delegated work: a task has context, logs, diffs, feedback, and a final disposition. Worktrees isolate filesystem changes. MCP, the Model Context Protocol, connects agents to external tools such as issue trackers, databases, docs, or internal services. Custom instructions, prompt files, hooks, and plugins shape behavior so the agent follows team conventions. GitHub's Octoverse 2025 reported more than 1.1 million public repositories using an LLM SDK, including 693,867 created in the prior 12 months, which shows how quickly AI-connected development is becoming normal infrastructure. The takeaway: successful VS Code agent setups are engineered systems, not a single model toggle.

The architecture should be documented like any other development environment. I want a repository to say which agent surfaces are approved, which commands require confirmation, how secrets are protected, what tests are expected before handoff, and which instructions define local coding style.

### What Should Go Into Repository Instructions?

Repository instructions should include build commands, test commands, code style, architectural boundaries, security rules, and examples of good changes. Avoid vague personality guidance. An agent benefits more from "run `npm test -- --runInBand` before handoff" than from "be careful." Concrete instructions reduce review noise.

### How Should MCP Be Used?

MCP should be used to give agents narrow, auditable access to real systems. A docs MCP server is low risk and high value. A production database tool is high risk and should require strong permissions, read-only defaults, and logging. Treat every MCP server like a new internal integration.

## How Do You Set Up an Agent-Native VS Code Workflow?

An agent-native VS Code workflow starts by standardizing the path from issue to isolated session to reviewed pull request. A practical setup in 2026 uses VS Code Insiders for the Agents preview where required, GitHub Copilot or approved agent providers for model access, repository instructions for local conventions, worktrees for isolation, and CI as the non-negotiable verification layer. Microsoft's Build 2026 recap said the GitHub Copilot app technical preview lets Copilot Pro, Pro+, Business, and Enterprise users direct multiple agents in parallel from a single My Work view, which matches the broader shift from single prompts to managed queues. The setup should also include prompt files for common tasks, custom agents for repeatable roles, and terminal approval rules. The takeaway: build the workflow around review checkpoints before increasing autonomy.

A starter setup I would use for a professional team looks like this:

| Layer | Recommended default | Why it matters |
|---|---|---|
| Editor | Stock VS Code plus Insiders for preview testing | Keeps production work stable while evaluating agents |
| Isolation | One worktree per agent task | Prevents mixed diffs and branch collisions |
| Instructions | Repo-level coding, testing, and security rules | Makes agent output more consistent |
| Tools | Minimal MCP servers and approved terminal commands | Reduces accidental access and confusing failures |
| Review | Inline diff review plus CI before merge | Keeps humans accountable for shipped code |

### What Is the First Task to Delegate?

The first task to delegate should be low ambiguity, covered by tests, and easy to review. Good examples are fixing a small bug with a reproduction, adding a narrow validation rule, updating a migration test, or writing missing unit coverage. Do not start with a cross-service architecture change.

### What Should Be in the Task Brief?

The task brief should include the user-visible problem, files or areas likely involved, acceptance criteria, commands to run, and constraints. A strong brief says, "Fix the null customer name crash in checkout summary; preserve API shape; add a regression test; run the checkout test suite." That is enough for a useful agent session.

## How Should You Choose Local, Background, Cloud, and Subagent Sessions?

Choosing local, background, cloud, and subagent sessions depends on latency, risk, repository size, credentials, and how much human supervision the task needs. Local interactive sessions are best when you need fast steering or the task touches sensitive local setup. Background sessions fit medium tasks such as test fixes, dependency cleanup, or small feature branches. Cloud agents fit longer work that can run away from the laptop, especially when they operate in managed environments with reproducible setup. Subagents are useful when a task naturally splits into roles such as planner, implementer, reviewer, and security checker. The Verge reported in 2026 that GitHub Agent HQ adds Claude and OpenAI Codex agents to GitHub, GitHub Mobile, and VS Code for Copilot Pro Plus and Enterprise users, showing that multi-agent routing is becoming a mainstream interface. The takeaway: match autonomy to blast radius.

I use a simple rule: the more dangerous the change, the closer the session stays to my eyes. Local interactive mode is right for authentication, billing, migrations, production data paths, and incident fixes. Background or cloud mode is fine for repetitive work with strong tests and a clean rollback path.

### When Do Subagents Help?

Subagents help when different review lenses catch different classes of defects. A planner can decompose a task, an implementer can write the patch, a reviewer can inspect edge cases, and a security agent can look for unsafe data handling. This only helps if each role has a specific checklist and authority boundary.

### When Do Subagents Waste Time?

Subagents waste time when the task is tiny, the repository setup is slow, or the roles are poorly defined. Four agents debating a two-line CSS fix is process overhead. Use multiple agents when parallelism or independent review reduces real risk.

## How Do You Create Custom Agents for Planning, Implementation, Review, and Security?

Custom agents are reusable role definitions that tell VS Code-compatible agent workflows how to behave for a specific responsibility, such as planning, implementation, review, test writing, or security analysis. In the VS Code ecosystem, research brief sources point to custom agents, prompt files, inherited instructions, hooks, plugins, and MCP servers as portable developer-tool configuration. The useful pattern is to encode a role's inputs, allowed actions, expected outputs, and stopping conditions. A reviewer agent should not rewrite half the codebase unless explicitly asked. A security agent should check authentication, authorization, secrets, injection risks, dependency changes, and logging of sensitive data. Sonar's 2026 State of Code coverage reported that 96% of developers do not fully trust AI-generated code, which makes specialized review roles practical rather than decorative. The takeaway: custom agents should constrain behavior as much as they enable it.

Here is a compact role breakdown that works in real repositories:

| Custom agent | Primary job | Required output |
|---|---|---|
| Planner | Turn an issue into a scoped implementation plan | Files, risks, test strategy, open questions |
| Implementer | Make the smallest correct patch | Diff, commands run, assumptions |
| Test writer | Add regression or integration coverage | Tests tied to acceptance criteria |
| Reviewer | Find bugs and maintainability risks | Findings with file and line references |
| Security checker | Inspect trust boundaries and data handling | Risk list and required fixes |

### How Specific Should Agent Instructions Be?

Agent instructions should be specific enough that two sessions produce similar work. Include preferred libraries, naming conventions, test commands, forbidden shortcuts, and escalation rules. Do not overload instructions with essays. The agent needs operational rules it can apply while editing, not a company handbook.

### What Should a Reviewer Agent Never Do?

A reviewer agent should never silently rewrite the implementation it is reviewing. Keep review and implementation separate unless you intentionally ask for a fix. This preserves the value of independent critique and avoids a common failure where the reviewer masks the original defect with a larger unreviewed change.

## What Is a Practical Issue-to-PR Workflow Without Losing Control?

A practical issue-to-PR workflow uses agents to accelerate implementation while keeping humans in charge of scope, review, and merge decisions. Start with an issue that has acceptance criteria. Launch an isolated agent session with repository instructions and a branch or worktree. Let the agent inspect, edit, and run approved commands. Review the inline diff before asking for revisions. Require tests or a documented reason tests were not run. Create a pull request only when the patch is coherent, then use CI and human review as the final gate. GitHub Octoverse reported 518.7 million merged pull requests in 2025, up 29% year over year, so the PR remains the durable coordination object even as agents produce more code. The takeaway: the best agent workflow still ends in ordinary engineering review.

My preferred loop is short: delegate, inspect, correct, verify, PR. If the first diff is directionally wrong, I stop the session and rewrite the brief. Trying to rescue a badly scoped task through ten follow-up prompts usually costs more than restarting with sharper constraints.

### What Does a Good Agent Handoff Include?

A good agent handoff includes a concise summary, changed files, tests run, tests not run, known risks, and any decisions that need human confirmation. I care less about confident prose and more about evidence. A handoff that says "I could not run integration tests because Docker was unavailable" is more useful than one that hides the gap.

### How Do You Review Agent Diffs Efficiently?

Review agent diffs by starting at public interfaces, security-sensitive paths, generated files, tests, and dependency changes. Then inspect the implementation. Agents often produce plausible local code that fails broader architecture expectations. Diff review should ask whether the change belongs in the system, not only whether the syntax works.

## What Governance, Security, and Review Checkpoints Should Teams Add?

Governance for VS Code agents refers to the policies, permissions, logs, and review gates that control how autonomous coding tools interact with source code, secrets, terminals, dependencies, and production-adjacent systems. The need is concrete: Sonar's 2026 survey coverage reported that 42% of developers' code is AI-generated, expected to reach 65% by 2027, while only 48% always check AI-generated code before committing. Those numbers make "just review it" an insufficient policy unless review is built into the workflow. Teams should define approved models, allowed repositories, terminal command policies, MCP access, secret handling, attribution rules, dependency approval, and CI requirements. The point is not to slow every task. The point is to prevent silent privilege expansion as agents become more capable. The takeaway: agent governance should be lightweight, explicit, and enforced at review boundaries.

Minimum controls I would add before broad rollout:

| Control | Practical rule |
|---|---|
| Secrets | Agents cannot read `.env` files or secret stores unless explicitly approved |
| Terminal | Destructive commands require confirmation |
| Dependencies | New packages require human review |
| Data | Production data access is read-only by default, preferably unavailable |
| CI | No merge without automated checks or named exception |
| Attribution | PRs disclose material AI assistance when policy requires it |

### What Approval Rules Matter Most?

The most important approval rules cover terminal commands, dependency changes, network access, credential access, and pull request creation. These are the places where an agent can cause damage beyond a bad local edit. Keep approvals rare enough that developers do not rubber-stamp them, but strict enough to catch real risk.

### How Should Teams Handle AI Code Attribution?

Teams should handle AI code attribution according to legal, customer, and platform requirements, then automate the boring part. A PR template field is often enough: "AI assistance used: yes/no; tool: Copilot/Codex/Claude; reviewer checked generated code." The goal is traceability without turning every commit into paperwork.

## What Are Common Failure Modes in VS Code Agent Sessions?

Common VS Code agent failure modes include vague task interpretation, overbroad edits, broken environment setup, missing tests, hallucinated APIs, hidden dependency changes, command loops, and superficially correct fixes that violate local architecture. These failures are predictable because agents optimize from available context, and repository context is often incomplete or contradictory. Official VS Code positioning emphasizes trust, control, session configuration, and tailoring agents to a codebase; those are not optional polish features. They are the difference between useful delegation and cleanup work. The fastest debugging move is to inspect the session transcript, command output, changed files, and first incorrect assumption. Do not keep prompting around a bad premise. Re-scope the task, add missing instructions, or split the work. The takeaway: debug agent sessions like distributed builds, with logs, inputs, outputs, and reproducible failure points.

Here is the failure table I keep in mind:

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent edits too many files | Scope too broad or no boundary | Restart with explicit file and behavior limits |
| Tests are skipped | Environment command missing or failing | Add setup instructions and required test command |
| API does not exist | Model inferred from similar libraries | Require docs lookup or compile/test verification |
| Same fix repeats | Agent is stuck on a false assumption | Stop session and provide the failing evidence |
| Diff is hard to review | Task combined refactor and behavior change | Split refactor from feature work |

### When Should You Stop an Agent Session?

You should stop an agent session when it repeatedly makes the same false assumption, expands scope without justification, cannot run required verification, or produces a diff you cannot review confidently. Stopping is not failure. It is cheaper than layering prompts on top of a corrupted working path.

### What Logs Should You Keep?

Keep the task brief, session transcript, terminal output, test results, final diff, and PR discussion. These artifacts help improve repository instructions and diagnose recurring problems. If three sessions fail on setup, the agent is not the only issue; your development environment is under-documented.

## What VS Code Agent Stack Should Different Teams Use?

The recommended VS Code agent stack depends on team size, compliance needs, repository maturity, and appetite for preview tooling. Solo developers can move faster with VS Code Insiders, the Agents preview, Copilot, Codex or Claude integrations, and lightweight prompt files. Startups can add worktree conventions, PR templates, CI gates, and custom reviewer agents. Enterprises should standardize approved providers, identity controls, audit logging, MCP allowlists, dependency policies, and rollout training. The research brief's competitive angle is important: the practical buyer question is not simply "Copilot or Cursor?" It is whether the team wants stock VS Code extension workflows, the VS Code Agents companion app, the GitHub Copilot app, terminal agents, or a VS Code fork. The takeaway: pick the narrowest stack that produces reviewed, merged, maintainable code.

| Team type | Recommended stack | Avoid |
|---|---|---|
| Solo developer | VS Code Insiders, agent mode, terminal agent, local worktrees | Heavy governance before habits are stable |
| Startup team | Shared instructions, CI, PR templates, custom reviewer agent | Untracked agent experiments on main branches |
| Enterprise | Approved providers, audit logs, MCP allowlists, policy-backed review | Tool sprawl across unapproved IDE forks |
| Open source maintainer | Agent-assisted triage, tests, documentation patches | Auto-merging untrusted generated code |

### What Is the Minimum Viable Stack?

The minimum viable stack is one approved agent surface, repository instructions, a known test command, worktree isolation, and a PR review rule. That is enough to learn from real work without building a platform program first. Add custom agents and MCP only after basic delegation works.

### What Should Enterprises Pilot First?

Enterprises should pilot narrow workflows with strong auditability: test generation, documentation updates, small bug fixes, migration preparation, and code review assistance. Avoid starting with production incident response or broad autonomous feature delivery. A pilot should measure merged quality, review time, rollback rate, and developer satisfaction.

## What Is the 2026 Outlook for VS Code as an Agent Control Plane?

The 2026 outlook is that VS Code is becoming an agent control plane: a familiar developer surface where multiple local, background, cloud, and third-party agents can be assigned, monitored, reviewed, and converted into pull requests. Microsoft's public direction around Agent Sessions, the VS Code Agents companion app, GitHub Copilot app previews, Agent HQ, and integrations with Claude and OpenAI Codex points toward orchestration rather than a single assistant. This matches the broader market: developers are using AI tools daily, public repositories are adopting LLM SDKs quickly, and teams are looking for ways to keep the editor they already trust. The risk is that faster code generation increases review debt if governance and testing do not improve with it. The opportunity is substantial: agents can remove repetitive implementation drag while developers focus on product judgment. The takeaway: VS Code's advantage is becoming the reviewable home for many agents.

I do not expect one agent to win every workflow. I expect teams to route work: Copilot for integrated enterprise workflows, Codex for repository-level implementation, Claude for reasoning-heavy edits, specialized agents for review and security, and normal humans for judgment. VS Code is valuable because it can become the place where those outputs are inspected and turned into ordinary software changes.

### What Should Developers Learn Next?

Developers should learn how to write agent-ready issues, maintain repository instructions, review generated diffs, use worktrees, and design verification steps. These skills compound across tools. Model names will change; the ability to delegate scoped work and review it rigorously will stay useful.

### What Should Teams Avoid Betting On?

Teams should avoid betting on unreviewed autonomy, undocumented tool access, and editor fragmentation without measurable gains. A flashy agent demo is not a delivery system. Bet on workflows that leave behind clean branches, reproducible tests, understandable diffs, and clear accountability.

## FAQ: What Do Developers Ask About VS Code Agents?

VS Code agents raise practical questions because they sit between editor feature, AI model, terminal automation, and team process. In 2026, the important questions are less about whether agents can write code and more about how developers should constrain, review, and operationalize that code. Stack Overflow's 2025 survey found 51% of professional developers use AI tools daily, so many teams are already past experimentation and into workflow design. The FAQ below answers the questions I hear when teams move from chat-based assistance to delegated agent sessions: whether the feature is stable, how it relates to Copilot, how to use worktrees, whether agents replace engineers, and how to start safely. The consistent answer is that agents are useful when they produce reviewable changes under explicit boundaries. The takeaway: treat VS Code agents as a disciplined development workflow, not a shortcut around engineering practice.

### Is the VS Code Agents companion app generally available?

The VS Code Agents companion app described in the research brief is a preview tied to VS Code Insiders through the VS Code 1.115 release notes. That means teams should evaluate it as emerging workflow infrastructure, not a guaranteed stable default for every developer. Use it in pilots before making it mandatory.

### Do VS Code agents replace GitHub Copilot Chat?

VS Code agents do not replace Copilot Chat; they cover a different level of work. Chat is still useful for explanations, navigation, and small edits. Agent sessions are better when a task requires multiple files, command execution, test iteration, and a final diff that can become a pull request.

### Are Cursor and Windsurf better than VS Code agents?

Cursor and Windsurf can be better for teams that want an agent-first IDE and accept a forked editor workflow. VS Code agents are more attractive when a team wants to preserve stock VS Code, existing extensions, enterprise controls, and familiar repository setup. The better choice depends on shipped code quality and team constraints.

### Should agents be allowed to run terminal commands?

Agents should be allowed to run approved terminal commands when the command is necessary for verification, such as tests, linters, builds, and safe code search. Destructive commands, dependency installs, migrations, network calls, and anything touching secrets should require explicit approval or run in a controlled environment.

### What is the safest way to start using VS Code agents?

The safest way to start is to delegate small, testable tasks in isolated worktrees with explicit acceptance criteria. Require a summary, diff review, and tests before merge. After the team sees consistent quality, add custom agents, MCP tools, and background or cloud sessions for broader work.
