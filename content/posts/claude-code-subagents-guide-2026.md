---
title: "Claude Code Subagents Parallel Agents Guide 2026: Faster Development Without Context Bloat"
date: 2026-07-08T12:00:00+00:00
tags: ["Claude Code", "AI Coding", "Subagents", "Developer Tools"]
description: "A practical Claude Code subagents guide for parallel agents, worktrees, model routing, and real developer workflows in 2026."
draft: false
cover:
  image: "/images/claude-code-subagents-guide-2026.png"
  alt: "Claude Code Subagents Parallel Agents Guide 2026"
  relative: false
schema: "schema-claude-code-subagents-guide-2026"
---

Claude Code subagents are the cleanest way to delegate noisy, self-contained coding work without filling your main session with logs, search results, and half-finished reasoning. In 2026, they are also the simplest entry point to parallel AI development: Markdown files, YAML frontmatter, scoped tools, optional worktree isolation.

I use subagents when a task has a clear boundary and a noisy execution path. Running a full test suite, researching three unrelated modules, auditing a diff for security issues, or generating migration notes are good fits. Asking a subagent to co-own an ambiguous refactor with you is usually a bad fit. The difference matters because subagents do not share your full conversation by default. They start with their own prompt, their own context window, and a task summary from the main agent.

This guide focuses on the parts that actually change day-to-day Claude Code usage: how subagents are defined, how to run them in parallel, when to add `isolation: worktree`, how model routing affects cost, and when you should step up to agent teams instead. I am using the current Claude Code behavior from the official [subagents documentation](https://code.claude.com/docs/en/sub-agents), including the v2.1.198 changes where `/agents` no longer opens the old interactive wizard and subagents run in the background by default.

## What Are Claude Code Subagents?

A Claude Code subagent is a specialized worker that Claude can delegate to from your main session. Each custom subagent is a Markdown file with YAML frontmatter at the top and a system prompt in the body. Claude Code discovers these files from known scopes such as `.claude/agents/` for a project or `~/.claude/agents/` for your personal machine-wide agents.

In practice, a subagent gives you three things that a normal prompt does not:

| Capability | What it means in practice |
|---|---|
| Isolated context | Logs, search output, and exploratory reads stay inside the subagent instead of bloating the main chat |
| Specialized behavior | The subagent can have a tighter role, output format, and tool policy than your main session |
| Parallel execution | Multiple independent subagents can investigate separate paths at the same time |

The context isolation is the feature I care about most. When building a migration plan, I often want one worker to inspect schema files, another to scan API handlers, and a third to read test failures. I do not want all intermediate file reads and dead-end hypotheses in the main session. I want the final summary, affected files, risks, and recommended patch order.

Subagents are not magic concurrency. They are useful when the work can be split cleanly. If two workers need to edit the same file or make decisions based on each other's partial results, you need stronger coordination. That is where agent teams or explicit sequential phases become better choices.

## How Do Subagents Differ From Agent Teams?

Claude Code now has several parallel-work primitives: subagents, agent teams, worktrees, background agents, and plain multiple terminal sessions. The confusing part is that they overlap. The practical decision is simple: use subagents when workers only need to report back to the caller; use [agent teams](https://code.claude.com/docs/en/agent-teams) when workers need to talk to each other.

| Pattern | Best for | Communication | Cost profile | Main risk |
|---|---|---|---|---|
| Subagents | Focused research, review, test runs, summaries | Report back to main agent | Lower than agent teams | Poor task boundaries |
| Agent teams | Multi-role design, competing hypotheses, cross-layer features | Teammates can message each other | Higher, each teammate is a full Claude instance | Coordination overhead |
| Worktrees | File isolation for parallel edits | No orchestration by itself | Similar to separate sessions | Environment drift |
| Multiple terminals | Manual parallel work | You coordinate everything | Depends on usage | Human context switching |

I reach for subagents first because the overhead is low. A reviewer subagent can inspect code and return a short report. A test-runner subagent can run noisy commands and return only failing tests. A docs-writer subagent can draft release notes without mixing prose work into an implementation session.

Agent teams are different. They are experimental, disabled by default, and require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. They make sense when you want a lead session to coordinate several independent Claude Code instances through a shared task list and mailbox. In the official docs, Anthropic recommends agent teams for research and review, new modules or features, debugging with competing hypotheses, and cross-layer coordination.

The trade-off is token cost. Anthropic's cost guidance says agent teams consume significantly more tokens because each teammate maintains its own context window. For routine sub-tasks, a subagent is cheaper and easier to reason about.

## How Do You Create a Custom Subagent?

As of Claude Code v2.1.198, the `/agents` command no longer opens the old interactive creation wizard. The current path is to ask Claude to write the agent file or create the Markdown file directly. This is a good change for teams because the actual artifact is reviewable and versionable.

Create a project-scoped subagent here:

```text
.claude/
  agents/
    code-reviewer.md
    test-runner.md
    migration-planner.md
```

Create a personal subagent here:

```text
~/.claude/
  agents/
    code-reviewer.md
```

Project subagents are best when the role depends on repository conventions. For example, a Rails monolith reviewer and a Next.js edge-runtime reviewer should not share the same assumptions. Personal subagents are better for generic habits you want everywhere, such as "summarize failing tests without editing files."

Here is a subagent definition I would actually start from:

```markdown
---
name: test-runner
description: Runs test commands, captures failures, and returns concise debugging notes. Use after code changes or when tests are failing.
tools: Read, Bash, Grep, Glob
model: sonnet
permissionMode: default
maxTurns: 8
background: true
color: cyan
---

You are a test runner for this repository.

Run the smallest relevant test command first. If that fails because the target is unclear,
inspect package scripts, Makefiles, or project docs to find the right command.

Return:
1. The command you ran
2. Passing or failing status
3. The smallest useful failure excerpt
4. Likely cause
5. Next debugging step

Do not modify source files.
Do not paste full logs unless the user explicitly asks.
```

There are a few details in that file that matter.

The `description` is not a label. It is the routing rule. Claude uses the task description, the current context, and this field to decide whether to delegate. Generic descriptions like "helps with tests" are weak. Specific descriptions like "Runs test commands, captures failures, and returns concise debugging notes" trigger more reliably.

The `tools` list is deliberately narrow. If a test runner should not edit files, do not give it edit tools. If a researcher only needs `Read`, `Grep`, and `Glob`, keep it read-only. I have found that tool scoping is one of the easiest ways to make agent behavior more predictable.

The `model` field should match the task. Use `sonnet` for most implementation and review work. Use `haiku` for simple summarization, changelog drafting, and low-risk lookups. Reserve `opus` for difficult architecture or debugging tasks where a wrong answer costs more than the tokens.

## Which Frontmatter Fields Matter Most?

The official frontmatter surface is broader than most teams need on day one. Only `name` and `description` are required, but the optional fields are where subagents become production-grade.

| Field | Use it when | Example |
|---|---|---|
| `name` | You need a stable agent identifier | `security-reviewer` |
| `description` | You want automatic delegation to work | `Reviews auth changes for token, session, and input validation risks` |
| `tools` | The agent should only use selected tools | `Read, Grep, Glob` |
| `disallowedTools` | You inherit tools but want to block a few | `Edit, Write` |
| `model` | The task needs explicit model routing | `haiku`, `sonnet`, `opus`, `claude-sonnet-5` |
| `permissionMode` | You want a specific approval posture | `default`, `plan`, `acceptEdits` |
| `maxTurns` | You want to cap runaway loops | `6` |
| `background` | The task can run while you continue | `true` |
| `effort` | The model supports effort levels and this task needs tuning | `low`, `medium`, `high` |
| `isolation` | The subagent may edit files in parallel | `worktree` |
| `skills` | The subagent should start with known skill content loaded | `["review-pr"]` |
| `hooks` | You need lifecycle automation around the subagent | `SubagentStart`, `SubagentStop` |

Two fields deserve special attention in 2026: `background` and `isolation`.

As of v2.1.198, subagents run in the background by default unless Claude needs the result before continuing. Permission prompts still surface in the main session. That means background execution is not a permission bypass; it is a scheduling behavior.

The `isolation: worktree` field gives a subagent a temporary git worktree. This matters when a subagent can modify files while other work is happening. Without worktree isolation, two agents editing the same checkout can collide. With isolation, each agent gets a separate working directory and branch context.

## How Do You Run Subagents in Parallel?

You can invoke a subagent in natural language:

```text
Use the test-runner subagent to run the auth tests and summarize failures.
```

You can also ask for multiple independent subagents:

```text
Research the authentication, billing, and notification modules in parallel using separate subagents.
Return a table with each module's entry points, risky dependencies, and test coverage gaps.
```

For more control, mention specific subagents:

```text
Use the security-reviewer, test-runner, and docs-writer subagents in parallel.
security-reviewer: inspect the auth diff for session and token risks.
test-runner: run the smallest relevant auth test target and report failures only.
docs-writer: draft migration notes for the changed login behavior.
Wait for all three summaries before recommending the next patch.
```

The last sentence is not cosmetic. I often tell Claude to wait for all summaries because otherwise the main agent may start synthesizing too early. Parallel work is only useful if you collect the independent findings before deciding.

When building a real feature, I prefer a three-phase flow:

| Phase | Main agent action | Subagent action |
|---|---|---|
| Explore | Define boundaries and questions | Inspect modules, logs, docs, tests |
| Plan | Merge findings into one patch plan | Review plan for missing risks |
| Execute | Make changes in controlled order | Run tests, review diff, draft docs |

This maps well to the broader [AI-DLC framework](/posts/ai-dlc-framework-2026/) pattern: agents are strongest when you give them explicit lifecycle stages instead of one vague "build this" instruction.

## When Should You Use Worktrees With Subagents?

Use worktrees when parallel agents might edit files. Do not overthink it. If a subagent is read-only, worktrees are usually unnecessary. If it may write code while your main session or another agent is also writing code, add worktree isolation.

Claude Code supports worktree-backed sessions through `claude --worktree`, and subagents can use worktree isolation through frontmatter:

```markdown
---
name: feature-implementer
description: Implements isolated feature slices that can be reviewed and merged back by the main agent. Use when a task owns a distinct file area.
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
isolation: worktree
maxTurns: 12
---

You implement a single isolated feature slice.
Before editing, identify the files you expect to own.
Do not edit files outside that ownership boundary without stopping and reporting why.
Run the narrowest relevant verification command before returning.
```

The current [worktrees documentation](https://code.claude.com/docs/en/worktrees) has a few operational details that are easy to miss:

| Worktree behavior | Why it matters |
|---|---|
| `claude --worktree name` creates an isolated checkout under `.claude/worktrees/<name>/` by default | Parallel sessions do not touch the same files |
| `.worktreeinclude` copies gitignored files such as `.env.local` | Agents can run tests that need local config |
| `worktree.baseRef` can use `"fresh"` or `"head"` | Use `"head"` when subagents must see your unpushed changes |
| Subagent worktrees are removed automatically if they finish without changes | Read-only or no-op work does not leave clutter |
| v2.1.203 tightened behavior when a worktree directory disappears | Commands should fail rather than accidentally run in the main checkout |

The `worktree.baseRef` setting is the one I see teams get wrong. The default branches from the repository default branch. That is good for clean isolated tasks, but bad if your subagent needs the uncommitted or unpushed work in your current branch. For that case:

```json
{
  "worktree": {
    "baseRef": "head"
  }
}
```

Also add this to `.gitignore`:

```gitignore
.claude/worktrees/
```

If your tests depend on local secrets, use `.worktreeinclude` rather than asking every agent to manually copy files:

```gitignore
.env
.env.local
config/secrets.json
```

Only gitignored files matching `.worktreeinclude` patterns are copied. Tracked files are not duplicated through this mechanism.

## How Should You Route Opus, Sonnet, and Haiku?

Model routing is where subagents become economically useful. The mistake is running every worker on your strongest model. That feels safe, but it burns budget on tasks that do not need deep reasoning.

My default routing looks like this:

| Task | Model | Reason |
|---|---|---|
| Architecture review | `opus` | Higher reasoning value, fewer cheap shortcuts |
| Implementation | `sonnet` | Best default balance for code edits |
| Test failure triage | `sonnet` | Needs code understanding and command output interpretation |
| Changelog or PR summary | `haiku` | Low-risk summarization |
| File inventory or dependency list | `haiku` | Mostly extraction |
| Security review of auth or payment code | `opus` or pinned full model ID | False negatives are expensive |

Claude Code also supports `CLAUDE_CODE_SUBAGENT_MODEL`, which overrides the per-invocation model and the subagent definition's `model` field. That is useful for controlled rollouts:

```bash
export CLAUDE_CODE_SUBAGENT_MODEL=sonnet
```

For third-party deployments such as Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry, the official model configuration docs recommend pinning provider-specific model IDs instead of relying blindly on aliases. Aliases are convenient for local use, but production teams usually want controlled upgrades.

This is the same basic trade-off I covered in the [Claude Sonnet 5 review](/posts/claude-sonnet-5-review-2026/): the best model is not always the most expensive model. The best model is the cheapest one that reliably clears the quality bar for that task.

## What Real-World Subagent Patterns Work Best?

After using subagents on real repositories, I would start with five patterns. They are boring, which is a compliment. Boring agent workflows are easier to debug.

### How Do You Use a Review Swarm Without Getting Duplicate Findings?

Do not spawn five generic reviewers. Give each reviewer a different lens:

```text
Run three subagents in parallel:
1. security-reviewer: auth, secrets, injection, unsafe file access
2. performance-reviewer: N+1 queries, caching, hot paths, bundle size
3. test-reviewer: missing regression coverage and brittle tests

Each subagent should return only high-confidence findings with file paths and severity.
```

This works because the domains do not overlap too much. A generic "review this PR" prompt produces duplicate comments and shallow coverage. Separate review lenses produce fewer but better findings.

For security-sensitive agent work, read the [Mozilla 0DIN Claude Code case study](/posts/mozilla-0din-claude-code-case-study-2026/) as a reminder that clean-looking repositories can still manipulate coding agents through instructions, scripts, or environment assumptions. A subagent with fewer tools is not just cleaner; it is a smaller blast radius.

### How Do You Keep Test Runs From Polluting Context?

A test-runner subagent should be one of the first agents you create. Test output is high-volume and mostly disposable. You rarely need 2,000 lines of stack traces in your main conversation.

Use a prompt like this:

```text
Use the test-runner subagent to run the smallest relevant test target for the checkout flow.
Return the command, pass/fail status, and at most 40 lines of failure output.
Do not edit files.
```

That "at most 40 lines" constraint matters. Subagents return summaries to the main session, and detailed summaries still consume context. If you need the full log, ask for it later.

### How Do You Split A Migration Safely?

For migrations, I use subagents for exploration, not blind implementation:

```text
Use parallel subagents to inspect:
1. database schema and migrations
2. API handlers and service objects
3. frontend form and validation code
4. tests and factories

Each subagent should report affected files, coupling points, and migration risks.
Do not edit files yet.
```

Then the main agent creates one plan. This avoids the common failure mode where four workers each make locally reasonable changes that do not compose.

### How Do You Use Community Subagents Safely?

The [VoltAgent awesome-claude-code-subagents repository](https://github.com/VoltAgent/awesome-claude-code-subagents) has grown into a large catalog of community subagents, with language specialists, backend roles, frontend roles, infrastructure roles, and meta-orchestration agents. It is useful, but I would not install a large pack into a production repository without review.

Treat community subagents like shell scripts from the internet:

| Check | Why |
|---|---|
| Read the prompt body | It is executable behavior, even if it is Markdown |
| Narrow the `tools` list | Do not inherit broad tools by accident |
| Prefer project scope for team agents | Review changes through normal code review |
| Avoid secrets access by default | Most agents do not need environment files |
| Pin behavior in your repo | Do not depend on changing upstream prompts |

Community agents are strongest as starting points. Copy the useful role structure, remove assumptions that do not match your stack, and tighten the output format.

### How Do You Avoid Parallel Agent Conflicts?

Most failed subagent workflows come from weak ownership boundaries. If two agents can touch the same files, you need either worktrees or a different plan.

I use this rule:

| Situation | Use |
|---|---|
| Multiple agents reading different areas | Plain subagents |
| Multiple agents editing different packages | Subagents with `isolation: worktree` |
| Agents need to debate or coordinate | Agent teams |
| Same file needs careful edits | Main session only |
| High-risk production migration | Plan mode plus review subagents |

For same-file edits, parallelism is usually fake speed. You save five minutes of agent time and spend fifteen minutes resolving inconsistent patches.

## What Configuration Should A Team Start With?

For a real engineering team, I would check in three project subagents first:

```text
.claude/agents/
  code-reviewer.md
  test-runner.md
  migration-planner.md
```

The `code-reviewer` should be read-only unless your process explicitly allows reviewer-suggested edits. The `test-runner` can use `Bash`, but should not use edit tools. The `migration-planner` should be read-only and biased toward plans, affected files, and risk tables.

Then add team guidance to your `CLAUDE.md`:

```markdown
## Subagent usage

- Use `test-runner` after source changes that affect behavior.
- Use `code-reviewer` before final summaries for non-trivial diffs.
- Use `migration-planner` before database, API contract, or auth-flow changes.
- Use worktree isolation before running any subagent that may edit files in parallel.
- Do not spawn more than three subagents unless the task has independent ownership boundaries.
```

This gives Claude enough policy to delegate without turning every prompt into a long orchestration script.

For teams already thinking about AI coding as a lifecycle rather than a chat tool, subagents fit naturally into review, verification, and documentation stages. They are less useful as a substitute for architecture ownership. A senior developer still needs to define the boundaries, name the risks, and decide which results are trustworthy.

## What Are The Common Mistakes?

The first mistake is creating too many agents. A dozen vague roles such as `backend-helper`, `frontend-helper`, and `cleanup-helper` make delegation less predictable. Start with three high-value roles and add more only when you see repeated work.

The second mistake is giving every subagent every tool. Tool access should reflect the job. A docs agent rarely needs `Bash`. A security reviewer may not need `Edit`. A test runner may need `Bash` but not `Write`.

The third mistake is parallelizing dependent work. If the API contract is not decided, do not spawn frontend, backend, and test implementers and hope they converge. Have subagents research options, then let the main agent create the contract.

The fourth mistake is ignoring cost. Subagents are cheaper than agent teams, but they still consume tokens. Running eight subagents that each scan the whole repository is rarely better than asking three precise subagents to inspect known areas.

The fifth mistake is using community subagents without adapting them. A good public prompt can still be wrong for your repository's deployment model, security posture, or test commands.

## What Is My Recommended Claude Code Subagents Workflow?

For most developers, the best 2026 workflow is:

1. Create a small set of project subagents in `.claude/agents/`.
2. Keep descriptions specific enough for automatic delegation.
3. Restrict tools aggressively.
4. Use `sonnet` as the default implementation and review model.
5. Use `haiku` for low-risk summaries and extraction.
6. Use `opus` for high-risk architecture, security, or ambiguous debugging.
7. Add `isolation: worktree` before parallel edits.
8. Use agent teams only when workers need direct communication.

Here is the prompt I use when I want useful parallel work without chaos:

```text
Use parallel subagents for research only. Spawn:
- one subagent for API handlers
- one subagent for database schema and migrations
- one subagent for tests

Each subagent should return affected files, risks, and recommended changes.
Do not edit files.
After all three return, synthesize one implementation plan with patch order and verification commands.
```

That shape keeps exploration parallel and implementation coherent. It is not flashy, but it works.

Claude Code subagents are at their best when they act like focused senior assistants: inspect a bounded area, apply a specific lens, and return a concise judgment. They are at their worst when treated like a swarm of unsupervised junior developers editing the same checkout. The technology is useful, but the boundary-setting is still your job.

## What Do Developers Usually Ask About Claude Code Subagents?

### What is the difference between Claude Code subagents and the Agent tool?

The Agent tool is the mechanism Claude uses to delegate work. A custom subagent is a named, reusable agent definition that controls the delegated worker's prompt, tools, model, permissions, and optional isolation behavior. In normal usage, you create subagent files and ask Claude to use them; Claude handles the Agent tool call internally.

### Where should I store Claude Code subagents?

Use `.claude/agents/` for project-specific agents that should be reviewed and shared with the repository. Use `~/.claude/agents/` for personal agents you want across projects. Managed settings and CLI-defined agents can override those scopes, and plugin agents have the lowest precedence.

### Do Claude Code subagents share the main conversation context?

Normal subagents start with a fresh context window and receive a task summary from the main agent. They do not automatically see your whole conversation history. Forked subagents are different: they inherit the parent conversation, but that reduces the isolation benefit and should be used when the worker needs substantial prior context.

### Can Claude Code subagents run in parallel safely?

Yes, when the tasks are independent. Parallel research, review, and test runs work well. Parallel implementation is safe only when file ownership is clear or the subagents use `isolation: worktree`. If agents need to coordinate directly, use agent teams instead of plain subagents.

### Should I use community Claude Code subagents?

Yes, but review them first. Community subagents are useful templates, especially from curated catalogs, but they are still prompts with tool policies. Read the system prompt, narrow tools, remove assumptions that do not match your stack, and prefer checking project agents into version control.
