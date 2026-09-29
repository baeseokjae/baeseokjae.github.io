---
title: "Ordewell Coding Agent Task Planning: Turn One Goal Into an Ordered Plan (2026)"
date: 2026-09-29T07:11:09+00:00
tags:
  - ordewell coding agent task planning
  - ordewell
  - ordewell tutorial
  - ordewell vs task master
  - ordewell vs beads
  - ordewell vs taskplane
  - how to plan coding agent tasks
  - coding agent task planner
  - coding agent orchestration plan first
  - plan first orchestration vs parallel worktree sessions
  - editable plan coding agent
  - per task model selection coding agent
  - completion marker verification coding agent
  - coding agent dependency graph
  - claude code codex opencode orchestration
  - multi-agent coding worktree isolation
  - stop coding agents from losing the thread
  - coding agent self-grading problem
  - agentic task decomposition guide
  - ordewell npm install guide
  - ordewell handoff review merge
  - ordewell adr planner exploration envelope
description: "Ordewell turns one goal into an ordered plan of coding-agent tasks, then verifies each task by a completion marker. Setup, model picks, and limits."
draft: false
cover:
    image: "/images/ordewell-coding-agent-task-planner-2026.png"
    alt: "Ordewell Coding Agent Task Planning: Turn One Goal Into an Ordered Plan (2026)"
    relative: false
schema: "schema-ordewell-coding-agent-task-planner-2026"
---

Ordewell coding agent task planning works in five stages: a read-only planner explores your repository and asks about anything vague, emits an ordered task list with dependencies, each task runs in its own git worktree on a runner and model you assign, a task passes only when its completion marker appears in the output, and nothing reaches your branch until you approve the handoff.

That is the whole product in one sentence. The interesting parts are the two decisions inside it — the plan is a file you edit rather than a prompt you typed, and the pass/fail verdict comes from evidence rather than from the model's opinion of its own work.

## What does Ordewell actually do (and what does it refuse to do)?

Ordewell is an open-source task orchestrator for coding agents, Apache-2.0 licensed, written primarily in TypeScript, and published on npm as `ordewell` (also scoped as `@ordewell/cli`). It sits above Claude Code, Codex and OpenCode rather than replacing any of them — you can mix all three inside a single plan.

Four surfaces share one core: a terminal UI with the conversation on the left and the plan on the right, a CLI for scripting, a VS Code extension that bundles its own core, and a local HTTP plus WebSocket API. Every slash command has a CLI subcommand of the same name, and the project holds that parity with a test.

The refusal is the first thing worth understanding. The planner reads your repository but cannot write to it: exploration is read-only, and commands that would mutate the workspace are rejected at the boundary. The maintainer is explicit that this is a denylist classifier over a real shell rather than an OS-level sandbox, and tracks the gap in [ADR-0011](https://github.com/ordewell/ordewell/tree/main/docs/adr). Treat that as a disciplined guardrail, not a security boundary.

Live project state, verified on 2026-09-29 through the GitHub and npm APIs:

| Signal | Value (2026-09-29) |
| --- | --- |
| GitHub stars / forks / open issues | 179 / 14 / 33 |
| Repository created | 2026-07-31 |
| Last push | 2026-09-29 |
| npm versions published | 29 (first publish 2026-08-01) |
| npm latest | 0.5.5, released 2026-09-28 |
| npm downloads, last 30 days | 2,145 (`ordewell`) + 2,286 (`@ordewell/cli`) = 4,431 |
| Show HN launch | 2026-09-15, 56 points, 35 comments |
| Licence | Apache-2.0 (name and logos excluded via NOTICE) |

Requirements are modest: Node.js 20 or newer, at least one of the three supported agents, git for task isolation, and tmux for the terminal UI (Windows runs it under WSL). You do not need an API key to start — an agent you already subscribe to can act as the planner. If you prefer key-based planning, 25 providers are recognised, including OpenRouter, Anthropic, OpenAI, Gemini, Groq, DeepSeek, Mistral, Together, Fireworks, Cerebras and Kimi, plus any OpenAI-compatible base URL such as a local model server. The default planner model is deliberately a budget one, on the reasoning that planning does not need the strongest model in the fleet.

## Why do coding agents lose the thread in the first place?

The tool is aimed at a specific failure. Run four agents in four worktrees and the decomposition of the work exists only in the prompt you typed and in each agent's private context. When you learn at step four that step one was misread, there is nothing to edit — only something to undo.

The numbers say that failure mode is now the mainstream cost of agent work. JetBrains Research's 2026 Developer Ecosystem Survey, covering more than 15,000 professional developers, found 90% using AI coding agents at work at least weekly and 68% daily. Claude Code reached roughly 39% adoption among professional developers (47% in the US), up from 18% in January 2026, while Codex grew about fivefold from 3% to 16% and GitHub Copilot fell from 29% to 21%.

Adoption is not the same as confidence. The [Stack Overflow 2025 Developer Survey](https://survey.stackoverflow.co/2025/ai) found 84% of developers using or planning to use AI tools, but more actively distrusting AI output accuracy (46%) than trusting it (33%) — and among professional developers trust fell to 29%, down from 40% in 2024. The resistance concentrates exactly where Ordewell wants to play: 69% of developers do not plan to use AI for project planning, and 76% do not plan to use it for deployment and monitoring.

Then there is the measurement problem. [LinearB's 2026 Software Engineering Benchmarks Report](https://linearb.io/library/ai-in-software-development), drawing on 8.1 million pull requests from 4,800 teams, found AI-agent pull requests wait 17.6 hours for review against 3.4 hours for unassisted work — a 5.25x gap — and merge within 30 days only 32.7% of the time versus 84.4% for unassisted work. 88.3% of organisations now use AI-assisted tooling daily or several times a week, up from 71.6% in early 2024, yet 44.7% do not formally measure its impact and 76.1% of leaders report productivity gains from adoption signals rather than delivery data.

And the seam is where projects die. AgentMarketCap's April 2026 review of multi-agent coordination put 40% of enterprise agentic AI projects cancelled or paused — not because models failed on benchmarks, but because agents failed at the handoffs and context transfers between them. Only 24.4% of organisations have full visibility into which agents are talking to each other in production.

Ordewell's bet is that a plan is cheaper to audit than a diff, and that a marker is harder to argue with than a model's self-assessment. Whether that bet pays off is a separate question, addressed further down.

## Step 1: How do you install Ordewell and plan your first goal?

Install globally, then plan. The interactive path is the intended one.

```bash
npm install -g ordewell
```

Run `ordewell` inside your project to open the terminal UI and type a goal. On the first run you pick a planner and your runners with `/planner` and `/runners`. For anyone who wants a goal out of a script rather than a chat, the same pipeline is exposed on the CLI:

```bash
export AI_PROVIDER=claude-code      # plan with Claude Code, Codex or OpenCode

ordewell plan --goal "Add rate limiting to the public API"
ordewell run
ordewell handoff review             # read the diff
ordewell handoff merge              # bring it onto your branch
```

The planner's job between those two commands is to ask the questions you skipped. The `/grilling` skill is the aggressive version of that: it interrogates a vague goal with at least three probing questions before it outlines anything. If your goal is genuinely well specified, `/to-spec` moves in the other direction and turns the conversation so far into a product spec saved into the project.

One operational detail that catches people: uncommitted changes hold a run back until you stash them (`--stash`) or explicitly disable isolation (`--without-isolation`). That is deliberate — the isolation model assumes a clean base to branch from.

## Step 2: How do you read a plan before a token is spent?

The plan is a typed JSON artifact per session, stored under `.ordewell/sessions/`, with the conversation persisted separately. It is not an agent's internal state and not a message in a log. That distinction is what makes the next sentence possible: you can rewrite any part of the plan without another round trip to the model, and without losing work that has already completed.

Each task carries five editable properties:

| Field | What it decides | Why you would change it |
| --- | --- | --- |
| Runner | Claude Code, Codex, OpenCode, or a plugin runner | Route work by strength, cost or policy — a security refactor on one agent, a docs pass on another |
| Model | Chosen from that runner's catalogue | Stop paying frontier prices for a changelog edit |
| Thinking effort | Reasoning budget for the task | Turn it down for mechanical work, up for a migration |
| Mode | Execution mode for the task | Encode TDD or verification intent per task |
| Dependencies | Which tasks must land first | Keep a cycle impossible to express |

There is an enforced edit order: runner, then model, then thinking effort, then mode. Each choice constrains the next, and the remaining three are recomputed from the new runner's catalogue — so an unstartable combination is never saved in the first place. That is a small design decision with outsized consequences: it removes an entire class of "the plan looked fine and then failed at launch" errors.

Dependencies also point backwards in display order, which means a cycle cannot be created at the edit site. No surface lets you reorder tasks, because display order never was the schedule — the orchestrator fans out every task whose dependencies are satisfied.

The dependency edits are plain commands:

```bash
ordewell task-runner 2 opencode     # move a task to another agent
ordewell task-model 3 sonnet        # or just change its model
ordewell task-deps 3 1,2            # make it wait for tasks 1 and 2
```

## Step 3: How do you assign the right model to each task?

This is the step where Ordewell is most visibly not an orchestration product and most visibly an accounting decision. Per-task model assignment is a portfolio decision made visible before any spend: a security refactor, a README update and a test backfill should not cost the same amount of tokens or money, and the plan shows every assignment on one screen.

A worked allocation for a mid-sized feature looks like this:

| Task | Runner | Model class | Effort | Mode | Deps |
| --- | --- | --- | --- | --- | --- |
| 1. Extract the token-bucket limiter into its own module | Claude Code | strong | high | isolation-heavy | — |
| 2. Wire the limiter into the public API routes | Codex | mid | medium | standard | 1 |
| 3. Add integration tests for burst and refill behaviour | Claude Code | mid | medium | TDD | 2 |
| 4. Backfill unit tests for the legacy middleware path | OpenCode | cheap | low | TDD | 1 |
| 5. Update the API docs and changelog | OpenCode | cheap | low | standard | 2 |
| 6. Verify: run the full suite, fill in missing spec checks | Claude Code | mid | medium | verify | 3,4,5 |

The default planner model is a budget model for the same reason. Planning is decomposition and question-asking; it does not need the strongest reasoning engine, and Ordewell assumes you would rather spend the strong model on task 1 than on writing the list.

## Step 4: How does the run actually execute?

Each task starts a fresh coding-agent session in its own git worktree on its own branch. `node_modules`, `.env` and agent config are linked from the checkout rather than copied, and a `worktreeSetupCommand` handles project-specific preparation. Independent tasks run concurrently, three at a time by default:

```bash
ordewell parallel 6
```

Tasks receive the results of the tasks they depend on. A passing task is committed and merged into one per-run integration branch, lowest plan number first, and dependents start only once their predecessor is on that branch.

Two isolation behaviours matter in practice. First, a folder containing several repositories is treated as one workspace: every task gets a worktree of every repository and lands in all of them or none, which closes the "the change is only in the frontend repo" failure. Second, conflicts get a bounded repair attempt in the kept worktree — `conflictRepairAttempts` defaults to 2, and 0 disables it. The repair counts only if the branch really contains the work and no conflict markers remain; otherwise the task waits for you with the conflicting files named. A failed repair never halts the run and never overturns the task's own pass.

## Step 5: How is the verdict decided?

A task passes when its unique completion marker appears in the runner's output. The exit code is kept as supporting evidence. The model is never asked to grade its own work — that is the design rule, and it targets the single most-cited weakness in agent pipelines.

Two escape hatches exist for reality: `/complete` advances a task manually, and `/uncomplete` reverses it. The verify mode appends a final task that runs the full suite and fills in missing spec checks — still judged by exit code, so the extra task does not get to reinterpret its own result.

If you only take one idea from Ordewell, take this one. A verification primitive that does not consult the model is the part most worth copying into whatever orchestration you already run.

## Step 6: How do you review and hand off?

Nothing reaches your checked-out branch until you ask. The handoff verb is explicit about which of the four things you mean:

| Command | Effect |
| --- | --- |
| `ordewell handoff review` | Read the accumulated diff on the integration branch |
| `ordewell handoff merge` | Bring the integration branch onto your branch |
| `ordewell handoff discard` | Throw the run's work away |
| `ordewell handoff cleanup` | Remove the run's worktrees |

That is the moment Ordewell's own comparison page argues about: parallel-worktree tools also ask you to review diffs before merging, so the difference is not whether review happens but which moment the correction is cheap.

## Which skills and conversation controls matter?

Skills shape the plan before it exists; conversation controls keep the session usable while it does.

| Control | What it does |
| --- | --- |
| `/grilling` | Interrogates a vague goal with at least three probing questions before outlining |
| `/to-spec` | Turns the conversation so far into a product spec saved to the project |
| `/improve-codebase-architecture` | Scans for refactors worth doing, ranks them, splits the chosen ones into ordered tasks |
| TDD mode | Adds red/green/refactor instructions to every task |
| Verify mode | Appends a final suite-running task, still judged by exit code |
| `/rewind`, `/fork`, `/compact`, `/sessions`, `/new`, `/save`, `/load` | Conversation-level control: step back, branch, compress, list, start, save, restore |

The architecture skill is the one with a non-obvious use: run it with no goal at all and it proposes a ranked refactor plan, which is a reasonable way to test whether the planner's judgement is worth your trust before you give it a real feature.

## How does Ordewell compare with the alternatives?

The category has split into recognisable shapes, and Ordewell occupies exactly one of them. Note that the plan-first-versus-fan-out framing below originates on [ordewell.ai/plan-first.html](https://ordewell.ai/plan-first.html), a page published by the maintainer with a disclosure line, so treat that axis as vendor framing rather than neutral analysis. The storage, scale and verification columns are from live sources verified on 2026-09-29.

| Tool | Shape | Unit of work | Verification model | Scale (2026-09-29) |
| --- | --- | --- | --- | --- |
| Ordewell | Editable plan-first | Typed plan JSON per session | Completion marker in runner output; exit code as evidence | 179 stars |
| Task Master | PRD-first | Task list derived from a PRD | Manual / agent-judged | ~28,100 stars |
| beads | Shared-queue state layer | Dolt SQL rows with atomic claims | Claim-based ownership | ~27,500 stars, 1,270 open issues |
| Backlog.md | Markdown task files | Markdown per task | Review of agent-written files | ~6,900 stars |
| GitHub Spec Kit | Spec-driven development | Spec carried through implement and converge | Review of the implementation against the spec | 139,316 stars |
| Taskplane | Multi-agent pipeline | `prompt.md` / `status.md` task files | Separate reviewer and merger agents | 217 stars |
| Fusion | Software factory | `PROMPT.md` plan with acceptance criteria | Build, review and ship stages; kanban board | 1,249 stars |

Two rows deserve a note. beads is not really a competitor: it is a state layer with atomic claims, and Ordewell is the planning layer above that shape, so they compose more than they compete. Taskplane is the closest analogue by workflow philosophy — idea, spec, tasks, orchestrate, evaluate — but it runs one supervisor, a worker, a reviewer and a merger with a file-based mail system, rather than a single editable plan with per-task runner and model assignment.

The structural difference across the whole table is storage. Markdown task files diff cleanly but race under concurrency; SQL with atomic claims survives competing agents; Ordewell stores typed plan JSON per session and keeps the conversation separate. Ordewell is also the only column that gates on reviewing the plan itself rather than only the agent's output — Backlog.md gates on reviewing agent-written files, and the fan-out tools gate on diffs.

## Where does Ordewell not pay off?

Plan-first orchestration has real overhead, and it does not shrink to fit small work. A single-file fix, a dependency bump, a typo sweep: the time spent reading and editing a plan exceeds the time spent just doing the task, and if the work is genuinely independent, a parallel worktree tool is the simpler answer.

The harder caution is maturity. The project is roughly two months old by its own timestamps, has shipped 29 npm versions, and put out five releases in two days on the v0.5.x line. An independent review at [tomrochette.com](https://tomrochette.com/agents/task-management/ordewell) records that ADR-0002 documents saved sessions being wiped without migration during that rewrite. For a tool whose sessions are effectively the memory of your runs, session durability is the concrete adoption risk — not the architecture, and not the star count.

## What are the honest limits?

Four, in descending order of how much they should affect your decision.

The read-only planner is a denylist classifier over a real shell, not a sandbox, and the maintainer documents that limitation himself. If your threat model requires the planner to be unable to write, this does not satisfy it by itself.

No coordination benchmarks have been published. Asked to quantify performance in the launch thread, the maintainer said the tool targets large undefined tasks that are hard to quantify and that a statistically significant dataset would cost a lot of money. That is a defensible answer and also not evidence.

The launch thread's defining exchange was about authorship, not architecture: a commenter observed that everything around the project, including the maintainer's replies, reads as AI-written, and the maintainer confirmed heavy AI use for docs and code. For a product whose job is surfacing whether work is actually done, provenance is a fair thing to be judged on. The strongest technical pushback in that thread is also worth repeating — too rigid a plan and agents thrash on work they manufacture for themselves; too little and they get lost, and the details matter a lot.

Finally, absorbability. The standing objection is that any orchestration advance gets absorbed into Claude Code and Codex within months, and planner-plus-runners is exactly the surface absorption targets. The maintainer's counter is provider freedom: wanting to run Opus, DeepSeek and the next GPT at the same time. The fair version of that argument is that an artifact format plus an evidence rule outlives one vendor's roadmap in a way that a UI feature does not — which is also the honest reason to adopt this shape rather than this binary.

## Who should use it, and what is the first plan worth trying?

It fits engineers running mixed-model agent fleets who want per-task model assignment, evidence-based completion, and who are comfortable with a two-month-old project. It does not fit teams needing shared multi-agent queues, or anyone whose work is mostly small single-file changes.

If that describes you, the first plan to try is deliberately unglamorous: point `ordewell` at a repository you know well, run `/improve-codebase-architecture`, and read the ranked refactor plan without running it. You are testing the planner's judgement on ground where you already know the right answer. If the plan is good, set a budget, assign cheap models to the mechanical tasks, and let it run three at a time.

## FAQ

**Does Ordewell need an API key?**
No. A coding agent you already subscribe to — Claude Code, Codex or OpenCode — can act as the planner. If you prefer key-based planning, 25 providers are recognised, plus any OpenAI-compatible base URL including a local model server.

**Can Ordewell's planner change my repository?**
It reads, asks and plans; commands that would mutate the workspace are refused at the boundary. Be precise about what that means: it is a denylist classifier over a real shell, not an OS sandbox, and ADR-0011 tracks that gap.

**How does Ordewell decide a task is done?**
A task passes when its unique completion marker appears in the runner's output, with the exit code retained as supporting evidence. The model is never asked to judge its own work; `/complete` and `/uncomplete` are the manual overrides.

**Can I mix Claude Code, Codex and OpenCode in one plan?**
Yes — mixing is the point. Each task names its own runner, model, thinking effort and mode, and the plan shows every assignment before a token is spent.

**Is Ordewell free, and is it open source?**
The CLI is on npm and licensed Apache-2.0, with the name and logos excluded via NOTICE. There is no paid tier described; the cost is your existing agent subscriptions and the tokens the tasks consume.
