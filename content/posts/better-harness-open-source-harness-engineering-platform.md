---
title: "Better-Harness: An Open-Source Harness Engineering Platform for Better Harness Coding Agents"
date: 2026-09-17T07:01:48+00:00
tags:
  - harness engineering
  - coding agents
  - open source
  - agent eval
  - AI engineering
description: "Better-Harness gives better harness coding agents an open-source, host-agnostic loop: feedforward guides, feedback sensors, and evidence-bounded reports across five work dimensions."
draft: false
cover:
    image: "/images/better-harness-open-source-harness-engineering-platform.png"
    alt: "Better-Harness: An Open-Source Harness Engineering Platform"
    relative: false
schema: "schema-better-harness-open-source-harness-engineering-platform"
---

If you want better harness coding agents, the fastest lever is rarely a newer model — it is the harness that surrounds the model. Better-Harness is an MIT-licensed, open-source harness engineering platform from QoderAI that runs inside your existing coding agents (Claude Code, Codex, Cursor, and more) rather than replacing them. It combines feedforward guides with feedback sensors, then evaluates your agent across five work-dimension scores that keep missing evidence explicit instead of fabricating plausible numbers.

## What Is the Agent Harness, Anyway?

The phrase "Agent = Model + Harness" is not marketing spin; it is a structural claim about where reliability actually comes from. Martin Fowler defines the harness as everything around the model — the outer user harness that shapes how an agent behaves before, during, and after a coding task. That outer harness serves two goals: raise the odds of first-try success, and build a self-correction loop that works before a human ever reviews the result.

Feedforward mechanisms push guidance in ahead of action: AGENTS.md files, task specs, acceptance criteria, and reusable skills. Feedback sensors pull signals back after action: linters, tests, CI gateways, review agents, and evaluation agents. The engineering skill is not adding more of either — it is pairing the right guide with the right sensor so the loop closes quickly.

The same principle appears across the industry. OpenAI documented shipping a product built with roughly 1 million lines of code across about 1,500 pull requests with zero manually written code, running at about 3.5 PRs per engineer per day. Their sharpest lesson was not "try harder"; it was that early progress stayed slow because the environment was underspecified, and the fix was better legibility — observability and CDP-based introspection — not a stronger prompt.

A widely-cited teardown of Claude Code went further, finding that roughly 98 percent of the tool is the harness, not the model. That number is a useful heuristic even if you discount it: when your agent misbehaves, the surrounding system of guides, sensors, and gates is where most of the fix lives.

## What Better-Harness Actually Is

Better-Harness is an open-source harness engineering platform written in JavaScript, released under the MIT license, and added to GitHub in late July 2026. It sits at roughly 2,261 stars and about 180 forks, with three npm versions and ten dependents. It does not wrap your coding agent in a new client; instead, it runs through whichever agent you already use.

Supported hosts include Claude Code, Codex Desktop and CLI, Qoder, Cursor, qwen-code, GitHub Copilot CLI, Kimi Code, Pi, WorkBuddy, and Grok. That host-agnostic design matters because it means your existing provider, workflow, and prompts survive; Better-Harness layers the evaluation loop on top of them.

Conceptually, the platform formalizes the same feedforward-and-feedback architecture that Fowler and Augment both describe. Guides steer the agent before it acts; sensors — linters, tests, hooks, and evaluation agents — trigger self-correction when output drifts. The whole system is meant to be iterated on: when a failure recurs, you adjust the harness, not the model.

## The Five Dimensions of the Agent Work Loop

Better-Harness evaluates your agent on five Agent Work Loop dimensions rather than a single headline number. That split matters because a coding agent can be excellent at one stage and weak at another, and a total score hides the failure.

- Task understanding — did the agent correctly interpret the request and the acceptance criteria before acting?
- Controlled execution — did it act within the guardrails and scope you set, or did it wander?
- Change validation — did linters, tests, and hooks actually run, and did the change pass them?
- Reliable delivery — did the agent deliver a mergeable, working result on the first real attempt?
- Learning capture — did the loop record what went wrong so the next run avoids the same pitfall?

These five dimensions line up with wider measurement thinking. Augment Code recommends tracking task resolution rate, code churn, verification tax, defect escape rate, and pass@1. Better-Harness's dimensions are effectively a practical mapping of those ideas onto a single runnable loop, evaluated in your own repository rather than on a benchmark you never ship.

## Why Evidence-Bounded Findings Matter

One of the more refreshing properties of Better-Harness is what it refuses to do: it will not fabricate a score. When evidence for a dimension is missing, the report says so explicitly instead of assigning a plausible-looking number. That "missing evidence stays explicit" stance is genuinely different from opaque evaluation suites that return confident grades with no trail to reproduce them.

The contrast matters because the industry is full of inflated-looking numbers. Top coding agents post 65% to 76.8% resolution rates on SWE-bench-verified Python tasks, yet METR has warned that many benchmark-passing PRs would never actually merge in a real codebase. A DORA study found that 30% of developers reported little to no trust in AI-generated code. When every vendor quotes a benchmark, the only trustworthy signal is one you can reproduce against your own repository — and that is exactly what a harness with explicit "evidence missing" markers forces you to look at.

Reproducibility is the point: if your report cannot tell you which dimension was never measured, you cannot know whether your harness improved or your benchmark got easier.

## Where Better-Harness Sits vs. Prompt and Context Engineering

Prompt engineering, context engineering, and harness engineering are often conflated, but they operate at different temporal scopes. Augment Code offers a clean way to slice them: prompt engineering shapes a single turn, context engineering shapes a single context, and harness engineering shapes the full task lifetime. A prompt is a snapshot of intent; a harness is a system that runs before, during, and after the model acts.

In that framing, Better-Harness is unambiguously a harness-engineering tool. It does not improve your one-shot prompt, and it does not curate your working context. It builds the loop around the lifetime of the task: guides in ahead, sensors out after, and a steering loop for you to tighten each time a failure recurs. Monolithic instruction files tend to fail, as OpenAI observed — skills-as-map beats encyclopedia context. Better-Harness operationalizes the map rather than the encyclopedia.

## The Open-Source Advantage: Harness as Code

Because Better-Harness is MIT-licensed and written in JavaScript with npm packaging, your harness configuration becomes version-controlled infrastructure rather than a private configuration blob. Teams can treat guides, sensors, and quality gates as code: reviewed, diffed, and reverted like any other change. That is the natural fit for the "harness as code" idea — your reliability system belongs in the same repo discipline as your application.

The open license also means you are not locked into a closed evaluation platform. If the built-in gates do not cover your compliance checks, your linters, or your own review agents, you extend the platform instead of filing a feature request. The ~180 forks and 10 npm dependents are early evidence that the community is already bending it to fit real workflows rather than adopting a one-size-fits-all score.

This matters for teams that treat coding agents as an ongoing system to improve, not an event to benchmark once. Longitudinal validation — running the loop repeatedly to show the loop itself got better — is only practical when the harness is cheap, local, and yours to modify.

## Caveats and Honest Limits

Before you adopt Better-Harness, keep three limits in mind.

First, evidence is not causal proof. A high score across the five dimensions shows your agent and harness behave well under your conditions; it does not prove the loop caused the improvement. You still need controlled before-and-after runs to attribute gains.

Second, harnessability is not uniform. Martin Fowler's point holds here: not every codebase is equally amenable to harness controls. A greenfield service with fast tests and clean interfaces is far more harnessable than a legacy monolith with flaky suites and tangled dependencies. If your feedback sensors are unreliable, the loop will tell you that loudly — but it cannot repair poor test infrastructure for you.

Third, Better-Harness optimizes what you can measure. It is designed to keep missing evidence explicit, but it cannot force you to define the right dimensions in the first place. Teams that skip the guide-and-sensor design will get an honest report of an underbuilt harness, which is useful information but not a solution.

## Verdict: Who Should Adopt Better-Harness

Adopt Better-Harness if you already run one or more of the supported coding agents and you want a reproducible, host-agnostic way to measure and tighten the loop around them. It is especially well-suited to teams that value explicit, evidence-bounded reports over benchmark-friendly but unverifiable scores, and to engineering organizations that want their quality gates version-controlled as open, extendable code.

Skip it if you are looking for a benchmark to quote, or if your codebase lacks the feedback infrastructure (tests, linters, hooks) that any harness loop depends on — the platform will expose that gap, not close it for you.

For most teams running Claude Code, Codex, or Cursor in earnest, the practical verdict is positive: at zero license cost, with a mental model that matches how reliability actually improves — via the harness, not the model — Better-Harness is one of the most honest tools available for better harness coding agents.

## How to Get Started with Better-Harness

Starting takes minutes and follows the same shape on every supported host.

First, install the platform through your existing agent workflow (npm-based, per the repository). Because it is host-agnostic, the installation pattern for Claude Code differs only trivially from Codex CLI or Cursor.

Second, run a baseline pass on a representative task without changing anything about how you normally work. Capture the initial score across the five dimensions — this baseline is your point of comparison, and it will already tell you which dimensions were never actually measured.

Third, read the report for "evidence missing" markers. Those gaps are your highest-value work because they point at the sensors you lack, not the guides you should write more of.

Fourth, tighten one loop: add a guide where the agent misread intent (task understanding), add a pre-push linter or hook where it shipped sloppy changes (change validation), or add an eval agent where it delivered the wrong shape repeatedly (reliable delivery). Re-run the baseline.

Fifth, repeat and compare longitudinally. The goal is not a one-time score but a rising floor: each run should show the loop measurably improving, with every score traceable to evidence in your repository.

## FAQ

**What is Better-Harness?**
Better-Harness is an MIT-licensed, open-source harness engineering platform from QoderAI that runs inside existing coding agents — Claude Code, Codex, Cursor, and others — combining feedforward guides with feedback sensors and reporting evidence-bounded scores across five work-dimensions.

**What does "Agent = Model + Harness" mean?**
It means the reliability of a coding agent depends on the system around the model — guides in ahead of action and sensors after it — more than on the model itself. A popular teardown attributed roughly 98% of Claude Code to the harness, not the model.

**Is Better-Harness free to use?**
Yes. It is released under the MIT license with npm packaging, so there is no license cost, and teams can extend its quality gates for their own compliance checks instead of buying a closed evaluation platform.

**Which coding agents does Better-Harness support?**
It is host-agnostic and runs through Claude Code, Codex Desktop and CLI, Qoder, Cursor, qwen-code, GitHub Copilot CLI, Kimi Code, Pi, WorkBuddy, and Grok — it layers the evaluation loop on top without replacing your client or workflow.

**How does Better-Harness keep scores honest?**
It refuses to fabricate numbers: when evidence for a dimension is missing, the report says so explicitly instead of assigning a plausible score. That "missing evidence stays explicit" stance keeps every claim reproducible in your own repository.
