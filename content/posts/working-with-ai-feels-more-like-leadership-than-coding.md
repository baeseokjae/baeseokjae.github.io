---
title: 'Working With AI Feels More Like Leadership Than Coding: A Guide to Managing AI Coding Agents'
date: 2026-10-01T07:42:21+00:00
tags:
  - managing AI coding agents
  - AI coding agent leadership
  - agent orchestration
  - delegation gap
  - code review bottleneck
  - AGENTS.md
  - AI for developers
description: "Managing AI coding agents is real leadership: agent-wrangling skill correlates 0.81 with managing humans. Here is the delegation and review model."
draft: false
cover:
  image: "/images/working-with-ai-feels-more-like-leadership-than-coding.png"
  alt: "Working With AI Feels More Like Leadership Than Coding: A Guide to Managing AI Coding Agents"
  relative: false
schema: "schema-working-with-ai-feels-more-like-leadership-than-coding"
---

Working with AI coding agents feels like leadership because it is. The unit of work changed from writing code to decomposing it, delegating it, and verifying the result. That shift is measurable: a 2026 NBER working paper found that a leader's performance managing AI agents correlates at rho = 0.81 with their performance managing human teams — and still 0.69 after controlling for hard technical skills.

That single finding reframes everything else in this guide. If managing AI coding agents were a disguised coding skill, the correlation with human-team leadership would collapse once you controlled for task-specific ability. It does not. What the AI task is actually measuring is the soft, transferable part of leadership: how you set expectations, calibrate trust, and run a review loop.

So this is not a metaphor you reach for when the tooling gets confusing. It is an empirical description of the job — and, more usefully, a diagnosis with a treatment. The management canon you may have never read maps onto agents with almost no translation, and the failure modes you are about to hit have already been documented.

## You got promoted and nobody told you

Most developers never applied for a management job. They applied to write software. Then between 2025 and 2026, the shape of the daily routine changed underneath them.

Anthropic's 2026 Agentic Coding Trends Report — which has been widely reported but whose primary PDF is not publicly hosted, so treat these figures as vendor-reported — describes the transition with session telemetry. Average Claude Code session length went from about 4 minutes in Q1 2025 to roughly 23 minutes in Q1 2026. The share of sessions involving multi-file edits rose from 34% to 78%. The average session now makes around 47 tool calls.

Read that as a job description rather than a product metric. You are no longer typing the lines. You are scoping a change, handing it to something that will touch a dozen files, and then deciding whether to accept what came back. That is a stand-up, a ticket hand-off, and a code review, compressed into one loop. It is management work with the meeting overhead stripped out.

The inversion shows up in how practitioners describe their own fleets. Boris Cherny runs five local and five to ten browser-based Claude Code sessions in parallel, a workflow Addy Osmani uses to make the point that AI coding at scale stops being a prompting problem and becomes a management problem. Among intensive OpenAI Codex users, 28.6% peaked at five or more concurrent agents, with p99 usage around 71 agent-hours per day — a number that only makes sense if a human is coordinating rather than executing.

If your day now consists of writing specifications, dispatching work, reading diffs, and deciding what to escalate, you are not "using AI." You are running a team.

## The evidence that this really is leadership, not a metaphor

The strongest study here is NBER Working Paper 33662 by Ben Weidmann, Yixian Xu and David Deming, summarized in the NBER Research Digest. The design is what makes it convincing. Participants led both a team of human collaborators and a set of AI agents through structured work, and the researchers compared the two performance measures.

| Finding | Result | What it means for you |
|---|---|---|
| Correlation, agent leadership vs human-team leadership | rho = 0.81 | The two tasks share most of their skill content |
| Correlation after controlling for hard skills | rho = 0.69 | The overlap is leadership-specific, not technical ability |
| Effect of leader quality on team outcome | +1 SD leader ≈ +0.65 SD team performance | Who leads matters more than which model you run |
| Behavioural markers of strong leaders | More questions, more turn-taking, more "we"/"us" language | The winning behaviours are conversational, not technical |
| Demographic predictors | None significant | Seniority and titles did not predict who led well |
| Cost per assessment | $23 (AI) vs $114 (human) | Agent work makes leadership measurable at scale |

Two details deserve emphasis. First, the correlation survived controls for task-specific ability and fluid intelligence, which means the AI setting is capturing something real about how a person directs other workers. Second, in both settings the leader explained more than half the variation in team performance. The model was not the variable. The person directing the model was.

What does *not* transfer matters too. Agents do not negotiate roles, self-organize, or give each other psychological safety. All coordination remains centralized on you. Fortune's coverage of the same research quotes the analogy directly: with AI teams the human is closer to an orchestral conductor than a jazz-ensemble leader — every cue originates from one baton. You get the authority of a manager without the delegation of authority that a real team provides.

## The trap: you are a worse judge of your own AI workflow than you think

Here is the part of the leadership literature that stings. Management instinct is miscalibrated by default, and the calibration error is largest precisely for experts.

METR's randomized controlled trial is the reference point. Sixteen experienced open-source developers worked 246 real issues on repositories averaging 22,000+ stars and over a million lines of code. When allowed to use AI, they were **19% slower**. Their forecast beforehand was a 24% speedup. Their post-hoc belief was that AI had sped them up by 20%. Reality and perception pointed in opposite directions, roughly 39 points apart.

METR's authors were careful about scope, and so should you be: the study does not show that AI fails to speed up most developers, and it explicitly notes that unfamiliar codebases, less experienced developers, and greenfield projects plausibly behave differently. Five contributing factors were identified — over-optimism, deep familiarity with the repository, large and complex codebases, low suggestion acceptance (under 44%), and implicit repository context the model could not see.

The leadership lesson is not "AI is slow." It is that **a confident manager with no instrumentation is how you get a fleet that looks productive and is not**. METR's developers were not lazy or naive; they were experienced engineers who trusted their own feel for the work. Feel is exactly what stops being reliable when the work is distributed across agents.

The industry-level evidence rhymes. Google Cloud's DORA 2025 report (roughly 5,000 respondents) found 90% of technology professionals use AI at work and more than 80% report productivity gains — while 30% report little or no trust in AI-generated code. DORA's central framing is that AI is an amplifier: it shows a positive relationship with throughput and product performance alongside a *continuing negative relationship with delivery stability*. DORA 2024 had already estimated a 1.5% throughput reduction and a 7.2% instability increase for every 25% increase in AI adoption.

Faros AI's July 2025 telemetry (1,255 teams, 10,000+ developers) shows the same pattern in delivery terms: teams with high AI adoption completed 21% more tasks and merged 98% more pull requests, while PR review time rose 91%, average PR size rose 154%, and bugs per developer rose 9% — with no measurable organization-level DORA improvement.

Output went up. So did the cost of checking it. Both are true, and only one of them shows up in a demo.

## The delegation gap: 60% usage, 0-20% full delegation

If you want a single number that defines the job, take this one from Anthropic's 2026 report: developers use AI in roughly 60% of their work, but can "fully delegate" only 0-20% of tasks without line-by-line review.

That 40-to-60-point gap is not a model-capability problem waiting for the next release. It is a trust-calibration problem, and trust calibration is a management discipline with forty years of prior art. Andy Grove's *High Output Management* (1983) introduced task-relevant maturity: the appropriate level of supervision depends on the subordinate's demonstrated competence with *this specific task class*, not on a global judgment about their talent.

Applied to agents, that produces a rule that is both more permissive and more useful than either extreme:

- Autonomy is granted per task class, not globally. "This agent handles test scaffolding unsupervised" is a valid, earned statement. "I trust the agent" is not.
- Maturity is demonstrated by evidence, not by vibes. Track the failure rate per class. Raise autonomy only when the class has a track record.
- New classes start at high supervision regardless of how good the model is. A better model does not shorten the trust ramp for work you have never delegated.

Management 3.0's seven-level delegation spectrum — Tell, Sell, Consult, Agree, Advise, Inquire, Delegate — turns out to be literally implemented in your harness. Plan mode is Consult. Auto-accept is Advise. Full bypass is Delegate. You are not designing a new permission model; you are re-deriving a standard one, badly, from scratch, if you never read it.

## Verification is the binding constraint, so fleet size is a review decision

The instinct when you get faster at dispatching work is to dispatch more of it. That instinct runs straight into the actual bottleneck, which is not generation.

A February 2026 MIT working paper (Catalini et al., cited in analysis of management practice for agents) frames it plainly: the binding constraint on scaling agentic work is human verification bandwidth, not model intelligence. "The code got cheap this year. The supervision didn't," as one practitioner write-up puts it — the unit of work changed from accepting a completion to handing over a ticket, and the ticket comes back as an obligation to review.

Look at what the review side is doing while output climbs.

| Metric | Faros AI 2025 (1,255 teams) | Faros AI 2026 (22,000 developers) |
|---|---|---|
| Tasks completed | +21% | — |
| PRs merged | +98% | — |
| Time in PR review | +91% | +441% (median) |
| Average PR size | +154% | — |
| Bugs / incidents per PR | +9% | +242.7% per PR |
| PRs merged with no review | — | +31% more |
| PRs reviewed by an AI agent | 0% | 25% |

These are two different cohorts from the same vendor, not one time series, so do not read the numbers as a single trend line. Read them as two snapshots of the same structural problem: generation scaled, review did not, and the gap is being closed partly by *not reviewing*. Nearly a third more PRs now merge with no human review at all. A quarter are reviewed by another agent.

The seniority tax is real and usually unbudgeted. JetBrains' ICSE 2026 telemetry of 800 developers (reported secondhand) found AI users performing roughly 100 delete/undo actions per month versus 7 for non-users — a 14x rework gap. That rework lands on whoever has to reason about the change afterwards, which is rarely the person who prompted it.

So the practical formula is not "how many agents can I run." It is:

**Sustainable fleet size = your review capacity ÷ the review cost of one agent's output**

If the answer comes out below your ambition, the fleet you actually have is the smaller number. Everything above it is generating obligations, not value. Practitioner ceilings cluster at three to five concurrent agents for meaningful work, and five to seven CLI agents on a laptop before rate limits and merge conflicts eat the gains. Anthropic's own harness ships a 20-concurrent default with a "fewer than 15 agents" workflow guideline — a vendor capping its own feature because customers were drowning.

## You are not inventing management: the canon already covers this

The most useful discovery available to a developer who has accidentally become a manager is that the field is not new. Mapping the canon onto agents is nearly mechanical.

| Management concept | Source | Agent equivalent |
|---|---|---|
| Task-relevant maturity | Grove, *High Output Management* (1983) | Autonomy earned per task class, tracked by failure rate |
| Delegation levels (Tell → Delegate) | Management 3.0 delegation poker | Plan mode → auto-accept → full bypass |
| Decision rights | Standard org design | `AGENTS.md` / `CLAUDE.md`: defaults plus escalation paths |
| Director model | Camille Fournier, *The Manager's Path* | Spend a third of your time on guardrails and tooling, not per-artifact oversight |
| Standing meetings and onboarding docs | Any management handbook | Reusable context assets, evaluation harnesses, review checklists |

The decision-rights mapping is the one people underuse. A `CLAUDE.md` or `AGENTS.md` is not a prompt; it is a decision-rights document for a worker with no judgment of its own. That means it should contain the defaults and, crucially, the escalation triggers: build and test commands, hard constraints, do-not-touch paths, and explicit stop-and-ask conditions — "stop before touching auth, migrations, payments, or CI." Keep it short. Bloated machine-generated context files reduce task success and raise inference cost, which is the documentation equivalent of writing a policy manual nobody reads.

Fournier's director model tells you where the leverage is. Reviewing each artifact one at a time does not scale, and never did for human teams either. Authoring the guardrail, the tooling, and the check that runs *before* you look is what compounds.

## The supervision loop: Plan, Monitor, Wait, Review, Teach, Manual Fix, Update Assets

If you want a defensible process rather than a pile of tips, there is now a framework paper. arXiv 2609.24234, "The Work Behind Delegation: A Framework for Supervising AI Coding Agents" (September 2026), derives its model from 19 experienced developers and reconfigures Sheridan's classic supervisory-control model into seven stages:

1. **Plan** — decide what the agent will do and what it must not do. This is the highest-leverage stage and the one people skip.
2. **Monitor** — watch progress without hovering. Use checkpoints, not continuous attention.
3. **Wait** — genuinely disengage while the agent works. Unproductive waiting is a cost, not diligence.
4. **Review** — inspect the output against the plan, in a context that did not write the code.
5. **Teach** — correct the agent when it goes wrong in a way that will recur.
6. **Manual Fix** — take over directly when the task is faster to finish than to explain.
7. **Update Assets** — turn recurring guidance into a reusable artifact: a rule in `AGENTS.md`, a lint check, an evaluation case, a test.

Stage seven is the compounding lever, and it is why the loop is a loop. Every correction you make should either fix the output or fix the system. Corrections that only fix the output get paid for repeatedly.

The paper also documents how experienced developers manage supervisory load: they concentrate effort in planning, delegate supervisory work to *other agents* (a verifier, a reviewer), and convert recurring guidance into reusable assets. That is a manager delegating oversight — and it is the same move a good engineering manager makes when they turn a recurring review comment into a lint rule.

## When a fleet is the wrong answer

Parallelism has a real cost curve, and the evidence against naive fleets is stronger than the marketing.

Agents collaborating achieve roughly 50% lower success than solo agents, according to CooperBench (January 2026, 652 tasks, reported secondhand). Two-agent cooperation on frontier models succeeded only about 25% of the time. The failure split was informative: roughly 26% communication, 32% commitment, and 42% expectation failures — which is to say, this is a management problem, not an intelligence problem. It is the same taxonomy as a project with no clear owner.

Google Research evaluated 180 agent configurations (also reported secondhand) and found multi-agent coordination yielding up to +81% on parallelizable tasks while *degrading performance by 70%* on sequential tasks. The pattern is consistent and worth internalizing:

**Do not run a fleet on the critical path.** If B depends on A, concurrency adds coordination cost and buys nothing. Fleet work is for independent, crisply specified, independently testable slices.

Beyond sequential work, avoid fleets for:

- **Shared files.** Parallel agents touching adjacent code produce boundary failures, not tooling failures. Worktree-per-agent is the standard fix; Bun's 64-agent Zig-to-Rust port saw shared-tree agents destroy each other's work within minutes before the team moved to sharded worktrees and process isolation. Cursor's from-scratch agent version-control system recorded over 70,000 merge conflicts, with one file touched by 1,173 distinct agents at 7,771 conflicts — falling below 1,000 after the harness was rebuilt.
- **Small tasks.** Below roughly 30 minutes of human work, dispatch and review overhead usually exceeds the gain.
- **Judgment work.** Product intent, API design, architecture, and "should we build this?" are not delegation targets. Osmani calls this the over-delegation trap: the failure is not that the agent does it badly, it is that you stopped thinking about it.

Also watch for agentic drift: parallel agents converging on conflicting implementations of the same concept while all tests still pass. Green tests are not coordination.

## The first 30 days as an agent lead

If you want a concrete starting sequence rather than a philosophy, this is the one the evidence supports.

**Days 1-7: instrument before you optimize.** Pick five metrics and collect a baseline. Time in review, PR size, share of PRs merged with no review, rework (undo/delete churn), and escaped bugs or incidents per PR. Faros' 2026 numbers show exactly why review-side metrics matter: outputs rose, median review time rose 441%, and 31% more PRs merged with no review. Note that "PRs merged" is a vanity metric in this regime.

**Days 8-14: write your decision-rights document.** Build and test commands, hard constraints, do-not-touch paths, escalation triggers. Keep it under a page. This is the artifact you will update most often, and updating it *is* the management work.

**Days 15-21: define your task classes.** List the five to ten things you actually delegate. For each, write down the required evidence for acceptance. Start every class at high supervision, and promote a class only after it has a clean track record.

**Days 22-30: cap the fleet by review capacity and set kill criteria.** Compute your honest review throughput, then set your concurrency to match — commonly three to five agents for meaningful work. Write down in advance the conditions under which you kill a running agent rather than letting it finish. Deciding that while the agent is mid-run is how review debt accumulates.

Then close the loop: every recurring correction goes into an asset — a rule, a check, a test — so that the supervision cost per task declines over time. That is the compounding return, and it is the same thing good managers have always done.

## FAQ: managing AI coding agents

**Why does working with AI coding agents feel like leadership instead of coding?**
Because the unit of work changed from writing code to delegating and verifying it — roughly 60% AI usage against 0-20% full delegation in Anthropic's 2026 report — and the skills involved (decomposition, expectation-setting, trust calibration, review) are the same ones that predict success managing human teams, per NBER Working Paper 33662's rho = 0.81.

**Is managing AI agents really the same skill as managing people?**
The overlap is large but not total. The raw correlation is rho = 0.81 and rho = 0.69 after controlling for hard skills. What does not transfer: agents do not negotiate roles, self-organize, or provide one another psychological safety, so coordination stays centralized on the human — closer to a conductor than a jazz-ensemble leader, as Fortune's reading of the Deming research puts it.

**How many AI coding agents should one developer manage?**
Bound it by review capacity, not model capacity. Practitioner ceilings cluster at three to five concurrent agents for meaningful work, or five to seven CLI agents on a laptop before rate limits, merge conflicts, and review debt consume the gains. Anthropic's harness ships a 20-concurrent default with a "fewer than 15 agents" guideline. If nobody is reviewing, the fleet is generating obligations rather than value.

**How do I decide which tasks to fully delegate?**
Use delegation levels rather than a binary: plan mode is Consult, auto-accept is Advise, full bypass is Delegate. Delegate mechanical, crisply specified, independently testable work. Keep ownership of product intent, architecture, shared interfaces, security-sensitive changes, and "should we build this?" decisions. Raise autonomy per task class only after that class earns it — Grove's task-relevant maturity, unchanged since 1983.

**What is the delegation gap?**
It is the distance between how much you use AI and how much you can hand over without line-by-line review. Anthropic's 2026 report puts usage around 60% of work and full delegation at 0-20% of tasks. It is a trust and verification problem, not a model-capability problem: closing it requires automated evaluation, explicit escalation rules, and acceptance evidence — not just a better model.
