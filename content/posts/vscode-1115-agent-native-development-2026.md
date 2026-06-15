---
title: "VS Code 1.115 Agents: What Changed for Agent-Native Development"
date: 2026-06-15T04:04:25+00:00
tags: ["VS Code", "AI agents", "developer tools"]
description: "A practical guide to VS Code 1.115 agents, the new Agents app, worktrees, browser tools, terminals, and team governance."
draft: false
cover:
  image: "/images/vscode-1115-agent-native-development-2026.png"
  alt: "VS Code 1.115 Agents: What Changed for Agent-Native Development"
  relative: false
schema: "schema-vscode-1115-agent-native-development-2026"
---

VS Code 1.115 agents matter because Microsoft moved beyond chat assistance and added execution infrastructure: an Agents preview app, isolated worktrees, parallel sessions, review surfaces, browser transparency, and stronger terminal tooling. The practical takeaway is simple: VS Code is becoming a host for delegated coding work, not just an editor with AI features.

## What Changed in VS Code 1.115?

VS Code 1.115 is the April 8, 2026 Visual Studio Code release that introduced the VS Code Agents preview app alongside agent-focused browser and terminal improvements. The headline is not a new autocomplete model; it is a workflow layer for running multiple coding agents, watching their progress, reviewing diffs, giving feedback, and opening pull requests. That matters because Stack Overflow's 2025 Developer Survey found 84% of developers were using or planning to use AI tools, while 66% were frustrated by AI answers that were almost right but not quite. VS Code 1.115 targets that gap by giving agent work more isolation, visibility, and review pressure. The release also improved integrated browser tool calls, long-running Playwright scripts, background terminal interaction, and notifications. The takeaway: VS Code 1.115 treats agents as operational workers that need supervision, not magic assistants that can be trusted blindly.

### What did Microsoft ship first?

Microsoft shipped the VS Code Agents preview through VS Code Insiders, so it is intentionally early-access infrastructure. In practice, that means teams should evaluate it with real tasks but avoid making it the only path for production development. I would start with low-risk maintenance work: dependency updates, test generation, migration rehearsals, and documentation-driven refactors.

### What changed beyond the Agents app?

The surrounding tools changed in ways that matter to agents. Browser tool calls now have clearer labels and better links to target tabs. Long-running Playwright scripts can return deferred results instead of blocking awkwardly. Terminals gained a `send_to_terminal` tool for background sessions and experimental background notifications, which reduces the chance that an agent silently stalls waiting for a process.

## How Does the New VS Code Agents App Work?

The VS Code Agents app is a preview companion application that ships with VS Code Insiders and manages autonomous coding sessions across repositories. A session can run in its own worktree, keep progress visible, expose inline diffs, accept feedback, and create a pull request when the result is ready. That is a different product shape from editor chat because the app is built around session management rather than prompt response. GitHub's Octoverse 2025 reported more than 1.1 million public repositories using an LLM SDK, which shows how quickly AI development patterns are spreading across real codebases. The Agents app is Microsoft's answer to the coordination problem that appears after teams stop asking single questions and start delegating whole tasks. The takeaway: the app makes agent work trackable enough for normal engineering review habits.

### How is this different from Copilot chat?

Copilot chat is usually interactive and local to the developer's current context. The Agents app is built for delegated sessions that may run longer, touch separate branches, and produce reviewable output. I still expect chat to be useful for quick explanation and small edits, but the app fits tasks where you want an agent to attempt a defined outcome while you do something else.

### What carries over from VS Code?

Existing VS Code customization carries over, including custom instructions, prompt files, custom agents, MCP servers, hooks, plugins, themes, and related configuration. That is important for teams that have already invested in repository instructions or model context plumbing. Agent-native development gets much more predictable when the same rules apply across chat, local tools, and delegated sessions.

## Why Do Isolated Worktrees and Parallel Sessions Matter?

Isolated worktrees are separate working copies tied to the same repository, and VS Code 1.115 uses them so multiple agent sessions can run without trampling the developer's active branch. The concrete value is conflict control: one agent can attempt a React migration, another can generate tests, and a third can update documentation without all three editing the same checkout. GitHub's Octoverse 2025 reported 518.7 million merged pull requests, up 29% year over year, which makes reviewable branch-level output the right unit for AI coding work. In my experience, the worst agent failures happen when generated edits are mixed into an already-dirty tree and nobody can reconstruct intent. Worktree isolation turns each delegated task into a contained review artifact. The takeaway: parallel agents only scale when their file changes and failure modes are separated.

### What does this change for daily development?

The developer can keep a stable main workspace open while agents work elsewhere. That reduces context switching because you are not constantly stashing half-finished work before trying an AI task. It also makes cancellation cheaper. If an agent goes down the wrong path, you can discard that worktree or close the session without cleaning up unrelated local edits.

### Where do worktrees still hurt?

Worktrees do not remove merge conflicts, flaky tests, or bad task definitions. They just make those problems easier to observe and contain. Shared generated files, lockfiles, schema migrations, and broad formatting changes can still collide. For agent-heavy teams, I would set clear rules around lockfile ownership, migration sequencing, and when agents are allowed to run formatters.

## How Did Browser Tooling Improve for Agent Workflows?

Browser tooling in VS Code 1.115 improved by making agent-driven browser actions more visible, less duplicative, and better suited to long-running Playwright work. The release added clearer browser tool-call labels, links to target tabs, deferred results for long-running Playwright scripts, fewer duplicate tabs, and macOS pinch-to-zoom support. Those details sound small until you debug a failing UI test that an agent ran through a hidden or duplicated browser tab. In front-end work, visibility is part of correctness: a selector may pass while the wrong modal is open, or a script may hang while the agent reports vague progress. Better labels and target links give the reviewer a way to inspect what actually happened. The takeaway: browser transparency turns agent UI work from guesswork into evidence you can review.

### Why do deferred Playwright results matter?

Deferred Playwright results matter because UI automation often takes longer than a chat-style tool call expects. A build may start a dev server, wait for hydration, run several interactions, and collect screenshots. If the tool must block until everything finishes, the agent becomes brittle. Deferred results make long-running browser checks fit the agent loop more naturally.

### What should front-end teams test with it?

Front-end teams should test agent workflows that already have observable browser outcomes. Good examples include fixing a failing Playwright spec, reproducing a visual regression, validating a form flow, or checking a responsive layout after a component refactor. Avoid starting with open-ended "improve the UI" prompts; the browser tooling is strongest when success is visible and testable.

## What Changed in Terminal Tools?

VS Code 1.115 terminal tooling changed by adding a `send_to_terminal` tool for background terminals and experimental notifications for background terminal activity. This matters because many coding agents fail in boring places: a test watcher asks for input, a dev server logs an error, a package manager waits on a prompt, or a migration command keeps running after the agent's attention moved elsewhere. Stack Overflow's 2025 survey found 45.2% of developers cited time-consuming debugging of AI-generated code, and terminal opacity is one source of that cost. A stronger terminal contract lets agents send commands to the right background process and lets developers notice when a task needs attention. This is less glamorous than model reasoning, but it directly affects reliability. The takeaway: agent-native IDEs need terminal state to be observable, addressable, and interruptible.

### How should teams use `send_to_terminal`?

Teams should treat `send_to_terminal` as a way to keep long-running processes stable while agents continue working. For example, an agent can start a dev server, send follow-up commands to the same terminal, and inspect results without repeatedly creating duplicate sessions. The practical rule is to name tasks clearly and keep terminal output tied to the session that produced it.

### Why are background notifications useful?

Background notifications are useful because agents often wait on commands that humans would notice instantly. A failing test, blocked install, or server restart can be easy to miss when it happens outside the active editor pane. Notifications give both the agent and the supervising developer a better chance to respond before the task drifts into stale output.

## What Does This Mean for Agent-Native Development?

Agent-native development refers to building software workflows around autonomous agents that can plan, run tools, edit files, test results, and hand work back for human review. VS Code 1.115 matters because it adds infrastructure around that workflow: isolated sessions, inline diffs, browser evidence, terminal control, and pull request handoff. GitHub reported that nearly 80% of new developers on GitHub use Copilot within their first week, so the next bottleneck is not awareness of AI coding tools; it is making AI work safe enough for repeated use. Agent-native development shifts the developer's role from typing every line to defining tasks, reviewing patches, debugging failures, and deciding what ships. The best teams will not remove review; they will make review faster and more grounded. The takeaway: agent-native development is delegation with engineering controls.

### What tasks fit this model?

The best tasks have clear acceptance criteria and a reviewable diff. Examples include adding missing tests around a bug, upgrading a small dependency, migrating a repeated API usage, writing typed wrappers, improving error handling, or preparing a draft PR for a narrow feature. Agents struggle more with ambiguous product calls, cross-team architecture decisions, and work that depends on undocumented tribal knowledge.

### What changes for senior developers?

Senior developers spend more time shaping tasks and less time babysitting keystrokes. That is not a demotion of craft; it is a different bottleneck. You need to know which files are risky, which tests prove behavior, which shortcuts will hurt later, and where generated code is likely to look plausible while being wrong.

## Who Should Try the VS Code Agents Preview Now?

The VS Code Agents preview is best for developers and teams already comfortable with VS Code Insiders, AI coding tools, Git worktrees, and pull request review discipline. Because the app is preview-only in VS Code Insiders, production teams should evaluate it in parallel with stable VS Code rather than forcing it onto every developer immediately. The most useful pilot group is usually two to five engineers working on maintenance-heavy repositories with good tests and clear ownership boundaries. Stack Overflow's 2025 survey showed 51% of professional developers use AI tools daily, so many teams already have enough adoption to run a serious pilot. The missing ingredient is not enthusiasm; it is a controlled workflow that produces measurable review outcomes. The takeaway: try VS Code Agents now if you can test it against real tasks without betting your delivery process on preview software.

### What is a good first pilot?

A good first pilot is a two-week trial on one repository with repeatable tasks. Pick issues that can be reviewed in under 30 minutes and validated by automated tests. Track simple metrics: task completion rate, review time, number of agent attempts discarded, test failures caught before review, and human follow-up required after merge.

### Who should wait?

Teams should wait if their repository has weak tests, unclear ownership, fragile local setup, or strict compliance rules that are not yet mapped to agent behavior. Agents amplify existing process quality. If builds are undocumented and reviewers already struggle to understand changes, adding parallel autonomous sessions will create more noise than leverage.

## What Risks and Governance Limits Should Teams Consider?

The main risk with VS Code 1.115 agents is not that an agent writes bad code; it is that bad code can look organized, tested, and review-ready before anyone checks the assumptions. The 2025 Stack Overflow survey found 66% of developers frustrated by AI solutions that are almost right, which is exactly the failure class that governance must catch. VS Code 1.115 helps by exposing diffs, progress, feedback loops, browser actions, and terminal state, but those controls do not replace engineering judgment. Teams still need rules for secrets, dependency changes, generated tests, production migrations, model access, and approval thresholds. I would also require explicit human approval for changes touching authentication, billing, data deletion, infrastructure, or security policy. The takeaway: agent governance should define where agents may act, what evidence they must produce, and who approves the result.

### What policies should be written down?

Write down which repositories agents may touch, which commands they may run, which files require human ownership, and when auto-approval is forbidden. Include rules for MCP servers, API keys, package installs, generated migrations, and external network calls. The point is not bureaucracy; the point is making agent behavior predictable enough that reviewers can trust the workflow.

### What evidence should reviewers require?

Reviewers should require a focused diff, test output, a short explanation of intent, and any browser or terminal evidence relevant to the task. For UI changes, screenshots or Playwright traces are often more useful than prose. For backend changes, failing-before and passing-after tests are the best signal that the agent fixed the intended behavior.

## How Do VS Code Agents Compare With AI-First IDEs and CLI Agents?

VS Code Agents compare with AI-first IDEs and CLI agents by turning VS Code into an open host for multiple agent styles instead of a single closed coding assistant. The current VS Code agent positioning includes local interactive agents, cloud agents, Copilot CLI, and third-party agents from providers such as Anthropic and OpenAI. That matters because many teams already standardize on VS Code extensions, settings, dev containers, tasks, and enterprise policies. AI-first IDEs can move faster on opinionated workflows, and CLI agents can be excellent for terminal-native developers, but VS Code has the advantage of sitting where many teams already work. The 1.115 release signals that Microsoft wants agents to run inside familiar review, browser, and terminal surfaces. The takeaway: VS Code's differentiator is breadth and integration, not being the most radical agent interface.

| Option | Strength | Tradeoff | Best fit |
|---|---|---|---|
| VS Code Agents | Integrates with existing VS Code settings, worktrees, browser tools, and PR flow | Preview status and evolving UX | Teams standardized on VS Code |
| AI-first IDEs | Opinionated agent experience and fast iteration | Migration cost and possible lock-in | Developers willing to switch environments |
| CLI agents | Scriptable, terminal-native, easy to run in automation | Less visual review context | Backend, infrastructure, and automation-heavy work |
| Cloud agents | Asynchronous execution away from the local machine | Requires strong permissions and review controls | Large queues of well-scoped tasks |

### When is VS Code the better host?

VS Code is the better host when the team's existing workflow already depends on extensions, workspace settings, dev containers, integrated terminals, and pull request review. The migration cost is low because agent work appears inside familiar surfaces. That is valuable for enterprises where changing the IDE is harder than adding a new workflow to the existing one.

### When is a CLI agent still better?

A CLI agent is still better when the task is naturally terminal-driven and does not need rich editor context. Repository cleanup, scripted migrations, log analysis, dependency audits, and CI repair often fit the command line well. I would choose the CLI path when repeatability and automation matter more than inline visual review.

## What Is a Practical Setup Checklist for Teams?

A practical VS Code 1.115 agents setup starts with a controlled Insiders pilot, repository instructions, safe tool permissions, reliable tests, and a review rubric for agent-generated changes. The checklist should be small enough that developers actually follow it: choose one repository, enable the Agents preview, confirm worktree behavior, configure custom instructions, connect approved MCP servers, define command permissions, and require pull request review before merge. GitHub's Octoverse 2025 reported more than 180 million developers on GitHub, which means any agent workflow that produces unclear pull requests will collide with established collaboration norms. The setup goal is not to make agents autonomous at all costs; it is to make delegated work understandable to the next human reviewer. The takeaway: start with guardrails that improve review quality before expanding agent autonomy.

| Setup item | Why it matters | Minimum standard |
|---|---|---|
| Repository instructions | Keeps agent output aligned with local conventions | Include test commands, architecture notes, and forbidden edits |
| Worktree workflow | Prevents parallel edits from mixing | One task per session and one reviewable diff |
| Test command list | Gives agents concrete validation steps | Unit, integration, lint, and typecheck commands documented |
| Tool permissions | Limits accidental damage | Human approval for destructive commands and sensitive files |
| Review rubric | Makes acceptance consistent | Intent, diff, tests, risk, and rollback path checked |

### What should be in custom instructions?

Custom instructions should describe the repository's architecture, preferred test commands, coding conventions, dependency rules, and review expectations. Keep them specific. "Write clean code" is useless. "Run `npm test -- --runInBand` after touching payment code and never edit generated API clients manually" gives the agent a real constraint.

### What metrics should managers track?

Managers should track accepted agent PRs, rejected attempts, review time, post-merge defects, test coverage changes, and cycle time for maintenance issues. Avoid measuring only raw lines of code. A high-output agent that creates review drag is not improving throughput; it is moving work from typing to cleanup.

## What Is the Bottom Line on VS Code Becoming an Agent Host?

VS Code is becoming an agent host by adding the session, isolation, browser, terminal, and review features that autonomous coding work needs to become routine. VS Code 1.115 is important because the Agents preview app reframes AI assistance as delegated development, while the browser and terminal changes address the operational problems that make agents unreliable in real projects. This is happening against a backdrop of mainstream AI adoption: Stack Overflow reported 84% of developers using or planning to use AI tools, and GitHub reported rapid growth in LLM SDK repositories. The sensible interpretation is not that agents will replace engineering process, but that engineering process must now include agents as participants. Teams that already have strong tests, clear ownership, and disciplined reviews will benefit first. The takeaway: VS Code 1.115 makes agent-native development feel less experimental and more like an emerging engineering workflow.

### What should developers do next?

Developers should install VS Code Insiders only if they are comfortable evaluating preview tooling, then try the Agents app on a narrow task with a clean acceptance test. Keep stable VS Code for daily production work until the preview proves reliable in your environment. The first goal is to learn where agents save reviewable time, not to automate everything.

### What should engineering leaders do next?

Engineering leaders should treat this release as a process design prompt. Decide which tasks agents may handle, how their work is reviewed, which evidence is required, and where human approval is mandatory. The teams that get value will be the teams that combine autonomy with clear boundaries.

## FAQ

VS Code 1.115 agents are best understood as Microsoft's first serious packaging of agent-native development inside the VS Code ecosystem. The release was published on April 8, 2026, and its most important feature is the VS Code Agents preview app for VS Code Insiders. It also includes browser and terminal improvements that help agents run UI checks, manage background processes, and produce reviewable work. The FAQ below covers practical questions developers and managers are likely to ask before trying the preview, including availability, Copilot chat overlap, worktree value, pull request safety, and current limitations. The short version is that the feature set is promising, but it should be piloted with clear task boundaries, strong tests, and normal pull request review. The takeaway: evaluate VS Code Agents as engineering workflow infrastructure, not as a shortcut around engineering responsibility.

### Is the VS Code Agents app available in stable VS Code?

The VS Code Agents app is available as a preview with VS Code Insiders, not as a stable default in regular VS Code. That means it is suitable for evaluation, pilots, and agent-heavy experimentation, but I would not require every developer on a production team to depend on it yet.

### Does VS Code 1.115 replace GitHub Copilot chat?

VS Code 1.115 does not replace Copilot chat. It adds a companion workflow for longer-running agent sessions that can operate in isolated worktrees and produce reviewable diffs. Chat remains useful for quick questions, explanations, and small edits inside the active coding context.

### Why are worktrees important for AI coding agents?

Worktrees are important because they isolate agent changes from the developer's active branch and from other agent sessions. That makes review cleaner, cancellation safer, and parallel experimentation less chaotic. The agent can fail without corrupting unrelated local work.

### Should teams let VS Code agents create pull requests automatically?

Teams can let agents create draft pull requests, but merge authority should remain human for meaningful code changes. A draft PR is a good handoff artifact because it gives reviewers a diff, discussion thread, test evidence, and CI result. Automatic merge should be limited to very low-risk, policy-approved tasks.

### What is the biggest practical limitation of VS Code Agents today?

The biggest practical limitation is preview maturity combined with the usual AI coding risk: plausible but wrong output. VS Code 1.115 improves isolation and observability, but teams still need tests, review rules, permission boundaries, and developers who understand the code well enough to reject weak changes.
