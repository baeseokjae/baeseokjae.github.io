---
title: "Claude Code Effort Levels A/B Test: What Reduced Effort Means for Coding Agents"
date: 2026-08-25T22:01:56+00:00
tags:
  - claude code
  - claude code effort levels
  - ai coding agents
  - claude code /effort command
  - token usage
draft: false
description: "Claude Code's reduced-effort A/B test makes coding agents less proactive, not less smart. Learn what effort levels control, when low effort helps or hurts, and how to override."
cover:
    image: "/images/claude-code-effort-ab-test.png"
    alt: "Claude Code Effort Levels A/B Test"
    relative: false
schema: "schema-claude-code-effort-ab-test"
---

Anthropic is quietly A/B testing reduced default effort levels in Claude Code, and the change does not make the coding agent dumber — it makes it less proactive. Effort controls how much autonomous work Claude performs per turn (reading files, running tests, double-checking its own output) before responding or asking for context. When the default drops, you get faster, cheaper turns that skip deep investigation, which is fine for scoped tasks but can silently degrade complex multi-file refactors.

## What Are Claude Code Effort Levels?

Effort is the single most misunderstood knob in Claude Code because people confuse it with model quality. The clearest mental model comes straight from Anthropic's own documentation: **model = how capable, effort = how thorough**. Switching from a high-effort setting to a low-effort setting does not swap in a weaker model; it changes how much work Claude decides to do on each turn before it answers.

At higher effort, Claude takes more actions before responding. It reads files, runs tests, re-checks its reasoning, and double-checks edge cases. At lower effort, it prefers to ask you for more context rather than spend tokens investigating on its own. The official Claude Code blog frames it as a trade-off between autonomy and token spend: "at lower effort, it asks for more context rather than spending tokens."

This distinction matters because it changes how you diagnose problems. If Claude skips a file you expected it to read, or skips running tests, that is usually an effort problem, not a capability problem. The model understands the task; it is just choosing not to be thorough about it.

## The A/B Test: What "Reduced Effort" Actually Changes

Anthropic has been running A/B tests on reduced — meaning lower — default effort levels inside Claude Code. A 215-point Hacker News story documented exactly this: "Anthropic appears to be A/B testing reduced effort levels in Claude Code." What this means in practice is that some users, some sessions, or some model versions get a lower default than the traditional "high," and many of them never notice until output quality changes.

The concrete behavioral change is straightforward. Under reduced effort, Claude does **less autonomous work per turn**:

- Fewer file reads before proposing a change
- Fewer test runs before declaring a change complete
- Fewer double-checks of its own output
- A stronger tendency to ask you clarifying questions instead of figuring things out

The A/B test is experimental, which is why you may see inconsistent behavior across sessions on the same project. One session might default to high and thoroughly inspect everything; the next defaults lower and "bails" early. This inconsistency is the tell-tale sign you have been put into the reduced-effort bucket.

## Effort Levels by Model and How Fallback Works

Effort is not a single scale — supported levels depend on which model you are running. According to the official model configuration documentation, the supported sets are:

| Model | Supported effort levels | Default |
|-------|------------------------|---------|
| Fable 5 / Opus 5 / Sonnet 5 | low, medium, high, xhigh, max | high |
| Opus 4.7 | low, medium, high, xhigh, max | **xhigh** |
| Opus 4.6 / Sonnet 4.6 | low, medium, high, max | high |

A few things stand out. Opus 4.7 is the only model that defaults to xhigh rather than high. And the fallback behavior is important: if you set an effort level your current model does not support, Claude Code falls back to the **highest supported level at or below** what you asked for. So if you request "max" on a model that only goes up to "high," you get high — not an error.

This fallback is a common source of confusion in A/B-style workflows. Users report setting xhigh or max and assuming they got it, when the model silently downgraded the request. Always confirm the level your model actually supports before relying on the setting.

## How Effort Affects Tokens, Cost, and Latency

The headline number in Anthropic's documentation is stark: the high-effort path generates **roughly 7x more tokens** than low effort to reach a higher-confidence answer. That 7x multiplier is why effort tuning is so tempting as a cost lever — and why the naive "always lower the effort" approach can backfire.

Independent benchmarking backs this up. A 200-run headless Claude Code benchmark (5 prompt variants x 2 effort anchors x 2 model sides x 10 prompts, comparing Opus 4.6 vs 4.7) found that **cost was the clearest signal — and the cheapest path was not "always lower effort."** High effort with fewer or no tool calls often cost less than medium effort with aggressive tool use.

Why? Two mechanisms dominate cost:

1. **Cache writes.** Reading files and processing tool results balloons the prompt cache on every turn. Each tool result gets re-sent, and cache writes are expensive.
2. **Tool use frequency.** Sessions that call tools constantly accumulate mid-session context that has to be re-processed.

The benchmark's most counterintuitive finding was that a "concise" prompt *increased* tool calls at medium effort, while a "no-tools" prompt eliminated mid-session context accumulation. Output tokens did not explain cost either — cheaper runs did not always produce shorter answers.

| Strategy | Observed cost impact |
|----------|---------------------|
| Always lowest effort | Not reliably cheapest; tool use can dominate |
| High effort + few tool calls | Often cheaper than medium + heavy tool use |
| Prompt suppression (no-tools) | Eliminated mid-session context growth |
| ultrathink | Slow everywhere, did not reduce cost |

The practical takeaway: effort is one input to cost, but **tool-use behavior and prompt cache are often the real levers**. If you want to cut spend, first reduce unnecessary tool calls before you hammer effort down.

## When Reduced Effort Is Fine vs When It Breaks

Reduced effort is not uniformly good or bad — it is a trade-off that depends on the task shape. The important insight is that quality degrades predictably in some situations and stays fine in others.

**Reduced effort is usually fine for:**

- Single-file edits with clear scope
- Simple Q&A about your codebase
- Boilerplate generation
- Repetitive, well-specified transformations

**Reduced effort tends to break for:**

- Multi-file refactors where the agent must trace dependencies
- Test-heavy workflows where skipping tests hides regressions
- Tasks with implicit requirements the agent must discover by reading
- Anything where "bailing" early produces a plausible-but-wrong answer

The 200-run benchmark found both high-effort Opus models passed every testable prompt (0 failures across high-effort runs), while medium-effort runs had instruction-following (IFEval) constraint failures. That is a clean signal: lower effort increases the chance of subtle, spec-violating output that looks correct at a glance.

## How to Detect Your Session Is on Reduced Effort

Because the A/B test is experimental, you cannot always trust that your session is on the default you expect. Here are the concrete behavioral signals that your session is running reduced effort:

- Claude proposes changes **without reading** the relevant files first
- Claude declares a change complete **without running tests**
- Claude asks you clarifying questions that it should be able to answer from the repo
- The same prompt that previously produced a thorough multi-step plan now returns a single, shallow answer
- Behavior is inconsistent session-to-session on the same project

If you see a pattern of skipped files or skipped tests, that is the reduced-effort fingerprint. It is the exact scenario Anthropic's guidance warns about: "if Claude skipped a file or tests, raise effort."

## How to Override Effort

You are not stuck with whatever default the A/B test assigned you. Effort can be controlled three ways, per the official documentation:

1. **`/effort`** — the interactive slash command inside Claude Code
2. **`--effort`** — the CLI flag when launching a session
3. **`effortLevel`** — the setting in `settings.json` for persistent configuration

Organizations can also **cap available levels** via Organization effort limits. If you work under an org policy, the cap shows up in the supported set for your session, and requests above the cap silently fall back to the highest allowed level.

If you are in an A/B bucket with a reduced default and want the thorough behavior back, set `effortLevel: "high"` (or xhigh/max on models that support them) explicitly rather than relying on the default. Because effort is a per-request value sent to the model alongside the prompt, overriding it re-establishes the behavior you want for that session.

## A Practical A/B Test Playbook for Your Own Coding Workflows

Instead of fighting the global A/B test, run your own. Treat effort as a manual override and measure the actual effect on your real workload:

1. **Start at the default.** Do not touch effort on routine, well-scoped tasks.
2. **Raise effort when Claude "bails."** If it skips files or tests, bump to high/xhigh before you correct it manually.
3. **Measure cost, not just effort.** Log token usage per session. The cheapest configuration is often high effort with disciplined tool use, not the lowest effort.
4. **Use prompt suppression for no-tool tasks.** When a task does not need tool calls, suppress them rather than dropping effort — this removes the biggest cost driver.
5. **Compare apples to apples.** Run the same prompt at low and high effort on a fixed task, and grade both the output quality and the token bill, not just the wall-clock latency.

This playbook mirrors what the independent benchmark found: effort tuning is only effective when you control tool use and cache behavior in the same experiment. Isolate the variable before you draw conclusions.

## Common Pitfalls and Community Findings

The community has surfaced several gotchas worth knowing before you tune:

- **`/effort` is global, not per-session.** A GitHub issue documented that `/effort` applies across concurrent sessions instead of being scoped to one session. This breaks A/B-style parallel workflows where you want different effort levels on different tasks at once. Be aware that setting effort in one terminal can leak into another.
- **"Concise" prompts can backfire.** In the benchmark, a "concise" instruction increased tool calls at medium effort, the opposite of the intended effect.
- **ultrathink is not a cost reducer.** It was slow everywhere and did not help cost, so do not reach for it as a savings lever.
- **Effort fallback is silent.** Unsupported levels downgrade without error; verify your model's supported set.
- **Reduced effort and quality.** The HN discussion centered on whether lower defaults degrade real coding output. The benchmark evidence says yes for constraint-heavy tasks, so treat reduced defaults with skepticism on complex work.

There is even emerging tooling — an "Effort Router" that selects effort per Claude turn — a sign that developers want finer-grained control than a single global setting.

## Conclusion — Tune Effort Like a Manual Override, Not a Global Switch

Anthropic's reduced-effort A/B test is a reminder that effort is a behavioral dial, not a quality dial. Reduced effort does not make Claude less capable; it makes it less proactive — fewer file reads, fewer test runs, more questions back at you. That is ideal for scoped, routine tasks and quietly dangerous for complex refactors and test-heavy work.

The most reliable strategy is to stop relying on the default entirely. Start at whatever effort the session gives you, watch for the "bail" signals, and raise effort explicitly when Claude skips files or tests. Manage cost through tool-use discipline and prompt cache behavior rather than reflexively dropping effort. Model decides how capable the answer can be; effort decides how hard the agent works to get it right. Tune the override with that distinction in mind, and you get the thoroughness you need only when you actually need it.

## FAQ

**What do Claude Code effort levels actually control?**
Effort controls how much autonomous work Claude does per turn before responding — reading files, running tests, and double-checking its output. Model decides capability; effort decides thoroughness.

**What is the Claude Code effort A/B test?**
Anthropic has been A/B testing reduced (lower) default effort levels in Claude Code. Some sessions default to a lower level than traditional "high," making Claude less proactive without changing the underlying model.

**Which effort levels does each Claude model support?**
Fable 5, Opus 5, and Sonnet 5 support low, medium, high, xhigh, and max. Opus 4.7 also supports all five and defaults to xhigh. Opus 4.6 and Sonnet 4.6 support low, medium, high, and max, defaulting to high.

**How much more expensive is high effort?**
Anthropic reports the high-effort path generates roughly 7x more tokens than low effort. However, independent benchmarks found cost is dominated by tool use and prompt cache behavior, so "always low effort" is not reliably the cheapest path.

**How do I change the effort level in Claude Code?**
Use the `/effort` slash command, the `--effort` CLI flag, or the `effortLevel` setting in `settings.json`. Organizations can cap available levels, and unsupported levels silently fall back to the highest supported level at or below your request.
