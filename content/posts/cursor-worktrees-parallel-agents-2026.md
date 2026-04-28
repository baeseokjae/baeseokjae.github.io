---
title: "Cursor Worktrees Guide 2026: Parallel Agents Without File Conflicts"
date: 2026-04-28T09:02:41+00:00
tags: ["cursor", "ai-coding", "git-worktrees", "parallel-agents"]
description: "Learn how to run multiple Cursor AI agents in parallel using Git worktrees — no file conflicts, faster feature delivery, and smarter model comparison."
draft: false
cover:
  image: "/images/cursor-worktrees-parallel-agents-2026.png"
  alt: "Cursor Worktrees Guide 2026: Parallel Agents Without File Conflicts"
  relative: false
schema: "schema-cursor-worktrees-parallel-agents-2026"
---

Cursor worktrees let you run multiple AI agents simultaneously — each in its own isolated Git checkout — so they never overwrite each other's files. You type `/worktree` in Cursor's chat, the agent spawns a separate branch and directory, and you review or discard the result independently from your main codebase.

## What Are Git Worktrees and Why Do They Matter for AI Agents?

Git worktrees are a native Git feature that allows a single repository to have multiple working directories checked out simultaneously, each on its own branch. Instead of cloning the repo three times to run three separate experiments, you add three worktrees to the same `.git` database — they share history and objects, but each has independent file state. In the context of AI coding agents, this capability transforms single-threaded tool use into genuine parallel execution. Cursor 3 (released April 2, 2026 under the codename "Glass") integrated worktrees directly into its Agents Window, giving developers a first-class UI for managing several agents at once. Before this, running two Cursor agents on the same project meant accepting file conflicts or constantly switching chat contexts. With worktrees, an authentication agent and a notifications agent can each modify their respective files at the same time, with zero risk of clobbering each other's work. The takeaway: worktrees are the infrastructure layer that makes multi-agent AI development safe and practical at scale.

### How Git Worktrees Differ from Branches

A regular branch switch (`git checkout feature-x`) replaces your entire working directory. A worktree addition (`git worktree add ../project-feature-x feature-x`) creates a *second* directory alongside your main one. Both are live checkouts; both track their own staged/unstaged changes. You can have your main checkout on `main` and a worktree on `feature/auth` simultaneously — open in separate editor windows, edited by separate agents, without any merge conflict until you deliberately apply changes.

## How Cursor Implements Worktrees: The Core Commands

Cursor's worktree implementation wraps Git's native worktree mechanics behind three slash commands designed specifically for AI agent workflows. The commands are `/worktree`, `/best-of-n`, `/apply-worktree`, and `/delete-worktree`. The `/worktree` command spawns one isolated run: it creates a new branch, copies your working directory state into a dedicated worktree path (stored under `~/.cursor/worktrees` when using the Cursor CLI with the global `--worktree` flag), then runs the agent's task entirely within that sandbox. Your main checkout is untouched. If the agent installs packages, rewrites a service, or breaks the test suite — none of that bleeds back until you choose to apply. This single-command isolation is the fastest path to "let the agent try something risky without me having to undo it manually." Cursor's documentation explicitly describes this as the right pattern for experimental edits, large refactors, and anything that touches build or install scripts.

### `/best-of-n` — Model Comparison in Parallel Worktrees

The `/best-of-n` command extends the single-worktree pattern into multi-model comparison. You send the same prompt to N different models (e.g., Claude Sonnet 4.6, GPT-4o, Gemini 1.5 Pro) simultaneously; Cursor spins up one worktree per model and runs each agent in isolation. When all agents finish, you review the diffs side by side and pick the strongest result. This command converts what used to be a manual, time-consuming A/B test — run agent A, note output, reset, run agent B — into a parallel operation that completes in roughly the same wall-clock time as a single agent run. For critical rewrites or algorithmic problems where the correct solution is non-obvious, `/best-of-n` provides empirical evidence rather than model reputation heuristics.

### `/apply-worktree` and `/delete-worktree`

Once you select a result, `/apply-worktree` merges the chosen worktree's changes back into your main checkout. Cursor handles the diff application so you don't need to manually cherry-pick commits. If you decide none of the results are worth keeping — or if the agent failed partway through — `/delete-worktree` cleans up the directory and branch. This cleanup path is what makes worktree-based experimentation low-risk: the cost of a failed agent run is a single command, not manual `git stash` archaeology.

## The Agents Window: Cursor 3's Multi-Agent Interface

Cursor 3 (Glass) shipped April 2, 2026, and its headline feature is the Agents Window — a dedicated sidebar for managing multiple AI agents simultaneously. Before Glass, Cursor's chat was fundamentally single-threaded: one conversation, one agent, sequential progress. The Agents Window surfaces all running worktree agents in one place, showing their status (planning, executing, waiting for review), the branch they're working on, and a quick-diff preview. Developers can launch a new parallel agent without interrupting agents already in flight. This represents a structural shift: Cursor is evolving from a smart editor into an orchestration layer, where the editor itself becomes secondary to managing a fleet of AI workers. Industry observers from The New Stack noted this trajectory in April 2026, describing the emerging stack as "Cursor for orchestration, Claude Code or Codex for execution." The Agents Window is the first concrete UI artifact of that vision — a control plane for AI agent deployment running locally.

### What the Agents Window Shows

Each agent card in the Agents Window displays:

| Field | Description |
|---|---|
| Branch | The worktree branch the agent is operating on |
| Status | Planning / Executing / Awaiting review / Done |
| Task summary | The original prompt truncated to ~80 chars |
| Changed files | Count of files modified so far |
| Quick actions | Apply, Delete, Open in editor |

The "Awaiting review" status is particularly useful for human-in-the-loop workflows: the agent pauses after generating a plan (Plan Mode) and waits for your approval before executing destructive changes.

## The Plan Mode + Agent Mode + Worktrees Pattern

The most reliable parallel agent workflow combines three Cursor features: Plan Mode, Agent Mode, and worktrees. The sequence looks like this: you describe the task in Cursor's chat and invoke `/worktree`; the agent enters Plan Mode first, generating a step-by-step proposal without writing any code; you review the plan and approve or redirect; the agent then enters Agent Mode within the worktree and executes the approved plan. This three-stage gate — isolate, plan, execute — prevents the most common failure modes of autonomous agents: irreversible file changes made before you understood the approach, and conflicts caused by two agents simultaneously modifying shared utilities. Engincan Veske documented this pattern with a concrete example: an authentication agent and a notifications agent each receive their feature brief, each generates a plan in their own worktree, and each waits for independent approval before writing a single line of code. The result is two completed feature branches ready for review in roughly the same time a sequential workflow would deliver one.

### When to Use Plan Mode vs. Letting the Agent Run

Not every task warrants the Plan Mode overhead. A quick fix — renaming a variable, updating a dependency version, adding a docstring — benefits more from direct Agent Mode execution without the planning step. Plan Mode pays off when:

- The task involves more than 5 files
- The agent will run install scripts or migrations
- Two or more parallel agents share adjacent code (services that import the same module)
- The change is difficult to reverse (schema changes, API contract modifications)

For simple fixes, skip Plan Mode and let the agent run directly in a worktree. The worktree still gives you the safety net; Plan Mode adds review latency that isn't worth it for low-risk tasks.

## Practical Workflow: Running Authentication and Notifications Agents in Parallel

Here is a concrete end-to-end walkthrough using the authentication + notifications example from Cursor's community documentation. Start with a clean `main` branch. Open two Cursor chat panels (or use the Agents Window). In the first panel, type:

```
/worktree feature/auth
Implement JWT authentication middleware in src/auth/. Use express-jwt, validate tokens on all /api/* routes, store user context in req.user. Plan first.
```

In the second panel:

```
/worktree feature/notifications
Implement email notification service in src/notifications/. Use Nodemailer, queue outbound emails via Bull, expose sendWelcomeEmail() and sendPasswordReset() functions. Plan first.
```

Cursor creates two worktrees: `~/.cursor/worktrees/feature-auth` and `~/.cursor/worktrees/feature-notifications`. Both agents enter Plan Mode. You review `feature/auth`'s plan (confirm the middleware signature, approve), then review `feature/notifications`'s plan (confirm the queue configuration, approve). Both agents execute in parallel. Fifteen minutes later, you have two independent feature branches, each with passing tests, ready for your review. You run `/apply-worktree feature/auth`, review the diff, merge. Then `/apply-worktree feature/notifications`, review, merge. Total wall-clock time: roughly the duration of the longer agent run, not the sum of both.

## Using `/best-of-n` for Model Comparison

The `/best-of-n` command is most valuable when you face a decision point where the implementation strategy matters: algorithm selection, API design, query optimization. Example usage for a performance-critical route:

```
/best-of-n 3
Refactor the /api/search route in src/routes/search.ts to handle 10,000 req/s. Currently uses sequential DB queries. Optimize aggressively.
```

Cursor spawns three worktrees, assigns each to a different model, and runs all three concurrently. You might get:
- **Model A**: Database connection pooling + query batching
- **Model B**: Redis caching layer in front of DB
- **Model C**: Elasticsearch migration with Redis cache

Each diff is reviewable independently. You benchmark or inspect the approaches, then run `/apply-worktree` on the winner. The cost is the same API tokens you'd spend on three sequential attempts — but the wall-clock time collapses to one attempt's worth.

### Choosing N for `/best-of-n`

| Task Complexity | Recommended N | Reason |
|---|---|---|
| Simple refactor | 2 | Low variance across models; 2 is enough signal |
| Algorithmic problem | 3–4 | Models diverge meaningfully; more samples needed |
| Architecture decision | 3 | Review overhead grows with N; 3 balances signal/cost |
| Boilerplate generation | 1 | No comparison value; just run the fast model |

## Risk Management: When Worktrees Protect You

Worktrees are not just a productivity feature — they are a risk management tool. The scenarios where they provide the clearest safety benefit:

**Large refactors**: An agent tasked with extracting a monolith service into microservices will touch dozens of files. If it goes wrong, recovery without a worktree means `git reset --hard` and lost context. With a worktree, you simply `/delete-worktree` and the main codebase is unaffected.

**Dependency upgrades**: Package upgrades often cascade — a major version bump triggers breaking changes across multiple consumers. Running the upgrade agent in a worktree lets you inspect the full blast radius before any change lands in `main`.

**Database migrations**: Any agent generating Prisma migrations or raw SQL should run in a worktree. Migrations are frequently irreversible; reviewing the generated SQL before running it is non-negotiable.

**Third-party API integrations**: Agents that generate API client code and test against real endpoints can create unintended side effects (test data in production, rate limit exhaustion). Isolating these runs in worktrees makes it easier to identify and attribute side effects.

## Team Adoption Patterns

Scaling parallel agent workflows across a development team requires light conventions to prevent chaos. The most common patterns observed in 2026 practice:

**Naming convention**: Prefix all agent worktree branches with `agent/` — e.g., `agent/feature/auth`, `agent/fix/login-bug`. This makes agent-spawned branches immediately distinguishable from human-authored ones in Git history and PR queues.

**Review gates**: Require all worktree-sourced branches to pass CI before `/apply-worktree` is allowed. Cursor's integration with GitHub Actions means you can enforce this with a branch protection rule targeting the `agent/*` prefix.

**Agent ownership**: Assign one human reviewer per running agent. In a team of four, you can safely run four parallel agents — one per person watching the Agents Window. Beyond that, review becomes the bottleneck, not agent capacity.

**Shared utilities freeze**: When multiple agents are running simultaneously, put a soft freeze on shared utilities (`src/utils/`, `src/types/`). Agents should not modify shared modules in parallel; route those changes through a single sequential agent after the parallel feature work is reviewed and merged.

## Integration with CI/CD and Code Review

Worktree-generated branches are standard Git branches that integrate seamlessly with existing CI/CD pipelines, requiring zero changes to your tooling. When an agent completes its task inside a Cursor worktree, the result lives on a real branch — push it to remote and GitHub Actions, CircleCI, or Jenkins fires exactly as it would for a human-authored branch. A 2026 best practice observed across teams using Cursor 3 is to prefix all agent branches with `agent/` (e.g., `agent/feature/auth`), then set a branch protection rule requiring CI to pass before `/apply-worktree` is permitted. This single convention turns worktrees from a local developer tool into a CI-enforced quality gate: no agent-generated code lands in `main` without passing tests and type checks. Code review tools like GitHub Pull Requests, Linear, and Reviewpad treat agent branches identically to human branches — reviewers see clean diffs, comment inline, and approve or reject without knowing or caring whether an AI or a human wrote the code. The recommended handoff pattern:

1. Agent completes in worktree
2. Cursor pushes the worktree branch to remote (`git push origin agent/feature/auth`)
3. CI runs automatically on the pushed branch (tests, linting, type-checking)
4. If CI passes, open a PR from the agent branch into `main`
5. Human reviewer approves and merges
6. Run `/delete-worktree` to clean up the local worktree

This pattern keeps the agent-authored code path identical to the human-authored code path for all downstream tooling. Code review tools, PR templates, and deployment pipelines require no modification.

## Common Pitfalls and How to Avoid Them

**Forgetting to clean up worktrees**: Each active worktree holds a full checkout of the repo. On large codebases, ten forgotten worktrees can consume several gigabytes. Run `git worktree list` periodically and use `/delete-worktree` (or `git worktree remove`) to prune stale ones.

**Agents modifying the same shared file**: Even with worktrees, if two agents both edit `src/config/constants.ts`, you will face a merge conflict when applying the second agent's changes. The solution is pre-assignment: review the agents' plans before approving execution and flag any overlap in the touched file lists.

**Missing context across worktrees**: An agent in a worktree doesn't automatically know what another agent is doing in a different worktree. If `feature/auth` and `feature/notifications` both need to register new Express routes, coordinate via the plans — have each agent's plan explicitly declare the route it will register to catch conflicts before execution.

**Using worktrees for trivial tasks**: Spawning a worktree for a one-line fix adds overhead — branch creation, directory copy, apply step — that outweighs the benefit. Reserve worktrees for tasks that take more than a few minutes or touch more than two files.

## Cursor Worktrees vs. Claude Code Multi-Agent Approaches

Both Cursor and Claude Code have moved toward multi-agent orchestration in 2026, but their models differ.

| Dimension | Cursor Worktrees | Claude Code Multi-Agent |
|---|---|---|
| Isolation unit | Git worktree (file-level) | Subagent + worktree (via Agent tool) |
| UI | Agents Window (visual, in-editor) | CLI-based, spawned via `Agent()` |
| Model choice | Multi-model via `/best-of-n` | Single model per session (configurable) |
| Human review step | Explicit via Agents Window | Delegated to parent agent or human |
| Best for | Feature-parallel development | Complex, hierarchical task decomposition |

Cursor's approach optimizes for developer visibility: you see every agent's status in a sidebar. Claude Code's approach optimizes for composability: agents can spawn sub-agents recursively, enabling deeper task decomposition. The practical choice comes down to whether you need visual oversight (Cursor) or programmatic control (Claude Code). Many teams in 2026 use both: Cursor for day-to-day feature parallelism, Claude Code for automated pipeline tasks where human oversight is less frequent.

## FAQ

The following questions address the most common points of confusion when adopting Cursor worktrees for parallel AI agent development. Each answer is self-contained and reflects Cursor 3 (Glass) behavior as of April 2026. The core principle to keep in mind: every `/worktree` invocation creates a real, independent Git branch in a separate directory — it is not a virtual sandbox or a snapshot. Changes are real, branches are real, and the Git history is real. This means all standard Git operations (push, diff, log, merge) work exactly as expected on worktree branches. Cursor's slash commands (`/apply-worktree`, `/delete-worktree`) are convenience wrappers around `git worktree add/remove` and standard merge operations — understanding the underlying Git primitives helps you debug edge cases that the UI doesn't expose. Whether you are new to worktrees or migrating a team from sequential single-agent workflows, these answers cover the setup, operation, and cleanup questions that come up most often in practice.

### What is the `/worktree` command in Cursor?

The `/worktree` command in Cursor creates an isolated Git worktree — a separate directory checkout of your repository on a new branch — and runs the AI agent's task entirely within that sandbox. Your main working directory is untouched until you run `/apply-worktree` to bring the changes back. It is the primary mechanism for running experimental or risky agent tasks without fear of permanently altering your codebase.

### Can I run multiple agents at the same time in Cursor?

Yes. With Cursor 3 (Glass), you can run multiple agents simultaneously using the Agents Window. Each agent operates in its own Git worktree — an isolated directory on a separate branch — so they cannot conflict with each other's file changes. You manage all running agents from the Agents Window sidebar and apply or discard their results independently.

### What does `/best-of-n` do in Cursor?

The `/best-of-n` command sends the same task to N different AI models simultaneously, each running in its own isolated worktree. When all agents finish, you compare the results side by side and use `/apply-worktree` to merge the best outcome into your main checkout. It is designed for scenarios where the optimal implementation approach is unclear and you want empirical comparison rather than picking a model by reputation.

### Do Cursor worktrees work with existing CI/CD pipelines?

Yes. Worktree-generated branches are standard Git branches and trigger existing CI/CD pipelines when pushed to remote. The recommended pattern is: agent finishes in worktree → push branch to remote → CI runs → if passed, open PR → human reviews → merges to main → delete worktree. No changes to your CI configuration are required.

### How do I clean up Cursor worktrees?

Run `/delete-worktree <branch-name>` inside Cursor to remove a worktree and its associated branch. Alternatively, use `git worktree remove <path>` and `git branch -d <branch>` from the terminal. Run `git worktree list` to see all active worktrees. It is good practice to clean up after each merged or rejected agent run to avoid disk accumulation on large repositories.
