---
title: "Autoprompt Skill Review: The Coding Agent Prompt Skill That Cuts Failures 45%"
date: 2026-09-28T12:55:34+00:00
tags: ["coding agent prompt skill", "autoprompt skill review", "agent skills benchmark 2026", "terminal-bench 2.1", "coding agent orchestration", "agent skill token overhead", "claude code verification skill"]
description: "Autoprompt claims 45% fewer coding-agent failures. We trace the number to its run, verify the repo state on 2026-09-28, and price the token cost."
draft: false
cover:
    image: "/images/autoprompt-skill-coding-agent-failures.png"
    alt: "Autoprompt Skill Review: The Coding Agent Prompt Skill That Cuts Failures 45%"
    relative: false
schema: "schema-autoprompt-skill-coding-agent-failures"
---

Autoprompt is a coding agent prompt skill that injects an orchestration procedure — plan, delegate, implement, verify — into 11 host agents, including Claude Code, Codex, and OpenCode. Its headline claim of 45% fewer failures comes from a single 89-task Terminal-Bench 2.1 run where failures fell from 29 to 16. That result is real arithmetic but version 1 evidence, and it costs roughly 3x wall-clock time and 2x tokens.

## What the 45% Figure Actually Measures

The number everyone quotes is not a percentage of tasks solved and it is not a percentage reduction in tokens. It is a reduction in failures on one benchmark, measured once.

The run is documented as Terminal-Bench 2.1 with 89 tasks, OpenCode 1.18.7 as the harness, and DeepSeek V4 Flash as the model. Baseline solves were 60 of 89. With Autoprompt active, solves rose to 73 of 89. Failures went from 29 to 16, which is a 44.8% reduction — rounded to 45% in every headline since.

| Metric | Baseline | With Autoprompt | Delta |
|---|---|---|---|
| Tasks solved | 60 / 89 | 73 / 89 | +13 tasks |
| Solve rate | 67.42% | 82.02% | +14.61 pp |
| Failures | 29 | 16 | -13 (-44.8%) |
| Wall-clock time | 1x | ~3x (estimated) | not measured |
| Token usage | 1x | ~2x (estimated) | not measured |

Two things make that table worth reading slowly. First, the denominator: 13 tasks out of 89 is a meaningful but bounded result, and 44.8% is a property of the failure slice (13 of 29), not of the workload. The same result is also described in the project's own README as "about 2x fewer mistakes," which is the identical measurement expressed against the smaller surviving set. Neither framing is dishonest; the choice of denominator is what makes a 13-task improvement look like a near-halving.

Second, and more important: cost was not instrumented. The project discloses the ~3x time and ~2x token trade-off as "planning estimates based on user experience reports, not measured benchmark results," and explains that timing and token logs were not retained. So the accuracy half of the claim is a measured benchmark; the cost half is not a measurement at all. If you are budgeting an unattended run, treat 3x as a floor and verify it on your own task distribution before trusting it in a CI budget.

## Autoprompt v2: What Changed Since the Original Review

The repository has moved past the benchmark. Autoprompt shipped v2.0.0 on 2026-09-09, and the README now labels the 45% result as "version 1 benchmarks," with a note that version 2 benchmarks will follow. No v2 efficacy number exists as of 2026-09-28. That matters for anyone citing the headline today: the marketing line is unchanged, but the artifact it refers to is two releases old.

What v2 actually changed is scope and control, not the accuracy thesis:

| Area | v1 | v2.0.0 |
|---|---|---|
| Interface | Slash-command modes | CLI: `autoprompt activate PROVIDER --target /abs/project -- '<goal>'` |
| Providers | Codex, OpenCode, Prime Agent | 11, adding Hermes Agent and Grok Build |
| Controls | Mode presets | Path selection plus model, effort, and concurrency flags |
| Subagent bounds | Not configurable | `--concurrency tokensaver\|wide\|custom --max-subs N` |
| Installer lifecycle | Manual | Managed install/update lifecycle |

The v2 workflow is more explicit about where control sits. Instead of a mode switch, you select a work path — `path=auto|direct|light|roadmap` — and a concurrency profile. The default is `tokensaver`, which caps fan-out at six subagents. The documentation is clear that choosing a path does not waive authorization, capability, budget, or verification requirements, and that invalid combinations error out rather than silently falling back to a different route.

## The Evidence Boundary Moved, and It Got Thinner

The single most important fact for a 2026 buyer is not in the README: the benchmark evidence is no longer fully checkable.

The per-task verdict file that the benchmark documentation points to for all 89 retained verdicts now returns HTTP 404. The `benchmark/` directory that once held the raw artifacts is absent from the main branch — verified by walking the recursive git tree listing of 1,381 paths, not inferred from a link. The methodology summary survives in `docs/benchmarks/terminal-bench-2.1.md`, but the per-task data a skeptical reader would use to audit the run does not.

That is a reproducibility regression, and it is the correct thing to hold against this project, because prompt-skill vendors have an obvious incentive to publish the summary and not the ledger. A benchmark you cannot audit is a marketing claim with a methodology section. Independent verification does not become impossible — you can rerun Terminal-Bench yourself — but the cheapest possible audit path (read the verdicts) is closed, and that cost falls on the buyer.

The v2.0.0 release notes show a similar honesty pattern in miniature. They concede that "full live acceptance of the final Codex artifact is not established," and that Windows and macOS builds are installer kits with native runtime verification remaining Linux-only. That is unusually candid disclosure for a release announcement, and it is the reason this review reads the project as careful rather than reckless: it publishes caveats that hurt it. It simply has not published version 2 evidence yet.

## Eleven Providers, One Verified Platform

Provider count is the feature most third-party articles get stale. Autoprompt now claims 11 supported hosts. The v2.0.0 work extended the Codex workflow across all of them and added Hermes Agent and Grok Build to a list that previously stopped at Codex, OpenCode, and Prime Agent.

The platform support story is narrower than the provider story. All three open items on the repository concern Windows:

- Issue #27 — activation is refused on Windows with `PROVIDER_UNSUPPORTED` because all 10 reviewed local records are `linux/x64` and `trusted-public-keys.json` lists no Windows keys.
- Issue #28 — OpenCode activation fails on the npm `cmd` shim.
- PR #29 — an in-flight fix for Windows npm shims for native package bins.

Read together with the release notes' Linux-only verification line, the practical rule is simple: the 11-provider claim is a code-path claim, and the verified execution surface is Linux. If your team codes on Windows, this is not yet a drop-in tool, and the open issues say so more precisely than any review can.

## Paths and Run Controls: Where v2 Spends Your Tokens

Cost in this category is not a fixed multiplier; it is a budget you set. The mechanism is straightforward and is the same one the independent literature describes: every phase is another model call over the same code, the judge is a separate model call with its own context, and parallel lanes re-read the same files. Fan-out is therefore the dominant cost lever, more than the model choice per phase.

The v2 controls map to that reality directly:

- `--concurrency tokensaver` — at most six subagents, the default. Sensible for a laptop or a metered API key.
- `--concurrency wide` — maximum parallel lanes. Fast, and the most expensive way to run it.
- `--concurrency custom --max-subs N` — the setting most teams should actually use, because it lets you align fan-out with the size of the change rather than the optimism of the moment.
- `path=direct` — minimal routing for a small, well-specified change.
- `path=light` / `roadmap` — progressive planning depth for larger or ambiguity-heavy work.

One operational caution worth repeating from independent walkthroughs: six lanes can touch deployment credentials, so run unattended sessions in a disposable VM or a container with scoped keys rather than on your working machine. And there is a real quality floor below which orchestration is pure overhead — if the task has nothing to execute or test, the verification phase produces one more opinion at full token price.

The default `tokensaver` profile is a reasonable acknowledgment of that floor. It is also the setting to keep when you are running agents on a VPS budget, where a wide fan-out can turn a ten-minute change into a twenty-dollar one.

## What Independent Skill Benchmarks Say About This Category

Autoprompt is one instance of a category that has been measured independently, and the category averages are not kind. Any review that quotes 45% without quoting the surrounding literature is selling, not informing.

The closest comparable study, SWE-Skills-Bench, ran 565 task instances across 49 public SWE skills with GitHub repositories pinned at fixed commits and execution-based verification. Thirty-nine of the 49 skills produced zero pass-rate improvement. The average gain was +1.2%. Token overhead ranged from -78% to +451% while pass rates stayed flat. Seven specialized skills gained up to +30%, and three actively degraded performance by up to -10% through version-mismatched guidance.

SkillsBench, testing 87 tasks across 18 model-harness configurations with matched no-skill controls, found that curated skills raise the average pass rate from 33.9% to 50.5% — a +16.6 percentage point gain — but with gains ranging from +4.1 to +25.7 points, and 13 of 87 tasks showing negative deltas. Its most useful structural finding is that skill value is a property of the specific stack, not of skills in general. Compact focused skills beat exhaustive bundles by a wide margin, and loading four or more skills together yielded only +10.1 points.

A third line of work explains the failure mode that matters most for a verification-heavy tool. The paper "Agent Skills Can Be Harmful" confirmed 307 skill-induced failures across those same benchmarks: 125 functional and 182 efficiency regressions. Efficiency damage was dominated by what the authors call Excessive Procedure at 62.6% — not prompt length — with excessive verification (67 cases) and heavy implementation pipelines (30 cases) as the largest drivers. Functional failures rarely came from irrelevant skills; seemingly relevant skills caused wrong or omitted implementation elements in 68.8% of cases. That is Autoprompt's exact design surface: it turns verification checklists into mandatory work, which is simultaneously the mechanism of its accuracy claim and the largest documented source of token regression in the literature.

Two further results bound the realistic ceiling. Under progressively realistic conditions, where the agent must retrieve skills itself instead of receiving a hand-picked one, skill benefits decay toward no-skill baselines — and query-specific refinement recovers performance, lifting Claude Opus 4.6 from 57.7% to 65.5% on Terminal-Bench 2.0. A separate 500-skill, roughly 38,000-trajectory evaluation found relevant skills lifting scores by 5.5 to 22 points, with open-weight GLM 5.1 plus a skill scoring 91.1 at about $0.89 per scenario against Opus 4.8 at 92.7 for $3.26.

That last number is the under-discussed lever. If you pair a cheaper model with a strong procedure, you can approach frontier quality at a third to a quarter of the cost — which changes the economics of Autoprompt's ~2x token multiplier far more than shaving one subagent will.

For context on why this market exists at all: Anthropic's 2026 survey of more than 500 technical leaders found about 90% of organizations use AI for coding, 86% deploy coding agents for production code, and 57% run agents on multi-stage workflows. Time savings were reported at 59% across code generation, review and testing, and research alike. Integration with existing systems (46%) is the top adoption blocker, ahead of data quality (42%) and cost (43%).

## The npm Versus GitHub Distribution Gap

If you install this tool with the command most articles still publish, you get the old version.

| Channel | Version | Published | Notes |
|---|---|---|---|
| GitHub | v2.0.0 | 2026-09-09 | 11 providers, CLI, path and concurrency controls |
| npm (`autoprompt-skill`) | 1.0.4 | 2026-08-21 | Zero runtime dependencies, two majors behind |

npm weekly downloads were 38 for the week of 2026-09-21 to 2026-09-27, against third-party trackers still publishing the older figure of 535 per week — a 14x discrepancy that mostly reflects how slowly catalog data propagates.

Repository state on the date this review was verified, 2026-09-28: 1,295 stars, 88 forks, 3 open issues, MIT license, 44 commits, created 2026-08-17, latest release v2.0.0 on 2026-09-09. Star velocity at launch was cited at 437 stars in three days, roughly 153 per day.

The version divergence explains most of the factual disagreements between reviews of this tool. Published comparisons disagree on provider count (9 versus 11) and star count (590 versus 1,300) because they were written against different points in a fast-moving repository. Some also repeat unattributed anecdotes — debugging-time reductions at an investment firm, e-commerce reliability gains — with no source at all. The 45% figure is exactly the kind of claim that survives this propagation intact while every verifiable detail around it goes stale; the version data in this review is dated deliberately so you can see how far it has drifted since.

## Where Autoprompt Earns Its Cost, and Where It Does Not

The category literature says a minority of skills genuinely help and the winners are concrete workflows, not general best-practice documents. Autoprompt is positioned in the subcategory that Anthropic reports as delivering the largest quality improvement: verification-type skills. That is the strongest structural argument in its favor, and it does not depend on the 45% at all.

The strongest practical argument is role separation. A reviewer that runs the code and can disagree on evidence is a different thing from a model approving its own output, and that architectural difference is what makes the benchmark result plausible — plan, implement, and verify as distinct calls with distinct context. Autonomy here is bounded by design: the workflow stops for choices that change the result or actions that require authority. If you were sold "fully autonomous coding," that is not what this is, and the stopping behavior is a feature.

Where it does not earn its cost:

- **Small, well-specified changes.** The project's own caveat is that small tasks "may differ significantly," and the efficiency-regression literature is dominated by exactly this pattern. Use `path=direct` or skip it.
- **Tasks with nothing to verify.** No executable check means the verification phase buys an opinion, not evidence.
- **Windows development teams.** The verified surface is Linux; three open items say so.
- **Workflows needing an auditable number.** The per-task evidence is 404 and v2 has no benchmark. You are trusting a methodology document.
- **Multi-skill setups.** If you already load four or more skills, the incremental value measured by SkillsBench drops sharply, and skill metadata competes for context — Claude Code caps skill metadata at roughly 1% of the context window (~2,000 tokens, about 15-25 skills on a 200K model) before descriptions get truncated.

## Verdict: Who Should Use It in 2026

Autoprompt is a well-engineered orchestration skill with a real, single-run accuracy result, unusually candid disclosure about its own gaps, and a version 2 that has not been benchmarked. The 45% is defensible only with its denominator attached: 13 tasks out of 89, on one harness, with one model, costing an unmeasured ~3x time and ~2x tokens.

Adopt it if you run long agentic coding sessions on Linux, you already have test suites the verifier can execute, and you want structural role separation between implementation and review. Start with the default `tokensaver` concurrency, pin `--max-subs` to something honest for your change size, and measure your own token delta in week one.

Do not adopt it on the strength of the headline. Do not cite it as an established result without noting that the evidence directory is gone and v2 is untested. And if you need independent confirmation before standardizing, rerun Terminal-Bench on your own repositories — which is what the project's own disclosure effectively invites you to do.

The honest one-line summary: this is the exception the skeptical literature allows for, priced at 3x the wall clock, sold with a number that is two releases old.

## FAQ

**Does Autoprompt really reduce coding agent failures by 45%?**

On one measured run, yes: failures fell from 29 to 16 across 89 Terminal-Bench 2.1 tasks using OpenCode 1.18.7 and DeepSeek V4 Flash, a 44.8% reduction. That is a single benchmark on a single harness and model combination, and the project itself labels it a version 1 result. The same 13-task improvement is also described as "about 2x fewer mistakes."

**Is the 45% benchmark independently verifiable?**

Not from the project's own artifacts. The per-task verdict file the benchmark docs link to returns HTTP 404, and the `benchmark/` directory is absent from the main branch among 1,381 paths in the recursive tree. The methodology document remains, so you can read how the run was done, but the raw verdicts needed to audit it are no longer published. Independent verification means rerunning the benchmark yourself.

**How much more expensive is Autoprompt than a plain coding agent?**

The disclosed figure is roughly 3x wall-clock time and 2x tokens — and the project states plainly that these are planning estimates from user experience reports, not measured benchmark results, because timing and token logs were not retained. Actual overhead depends mostly on fan-out, which you control via the `tokensaver` (six subagents maximum), `wide`, or `custom --max-subs N` concurrency profiles.

**Which coding agents does Autoprompt support, and on which platforms?**

v2.0.0 claims 11 providers, extending the original Codex, OpenCode, and Prime Agent list and adding Hermes Agent and Grok Build. Platform verification is narrower: the release notes concede native runtime verification remains Linux-only, and the three open repository items all concern Windows — `PROVIDER_UNSUPPORTED` activation failures caused by linux-only trusted keys, an OpenCode activation failure on the npm `cmd` shim, and an in-flight PR fixing Windows npm shims.

**Should I install Autoprompt from npm or GitHub?**

GitHub. npm still ships 1.0.4, published 2026-08-21, while the repository is at v2.0.0 from 2026-09-09 — a two-major-version gap that means the npm package lacks the CLI, the path controls, and the expanded provider support. npm weekly downloads were 38 for the week ending 2026-09-27, so the stale channel is also the less-used one.
