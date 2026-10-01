---
title: "Autoprompt Skill Review: Cutting Agentic Failures by 45%, Measured"
date: 2026-10-01T00:51:12+00:00
tags: ["autoprompt skill", "autoprompt skill review", "autoprompt coding agent skill", "agentic coding failure rate", "terminal-bench 2.1", "agent skill token overhead", "coding agent self-verification loop"]
description: "Autoprompt's 45% claim recomputed: +14.61pp gain, 95% CI +2.02pp to +27.20pp, and roughly 1.5 pass-rate points per extra 10% of tokens."
draft: false
cover:
    image: "/images/autoprompt-coding-agent-skill.png"
    alt: "Autoprompt Skill Review: Cutting Agentic Failures by 45%, Measured"
    relative: false
schema: "schema-autoprompt-coding-agent-skill"
---

Autoprompt is an open-source agent skill that wraps a coding agent in a plan, build, check, verify and finish loop. Its headline result — 45% fewer failures — is 29 down to 16 failures on 89 Terminal-Bench 2.1 tasks, a +14.61 percentage-point pass-rate gain whose 95% confidence interval is +2.02pp to +27.20pp. The direction is real; the precision is not.

This review is deliberately narrow. We recap the product in one paragraph and then spend the rest of the article on the three things no catalog page does: compute the error bar, price the trade-off, and test the claim against category-level evidence. If you want the feature tour, see our [earlier Autoprompt walkthrough](https://baeseokjae.github.io/posts/autoprompt-skill-coding-agent-2026/).

## What Is the Autoprompt Skill in One Paragraph?

Autoprompt is a coordination layer, not another coding agent. It installs into a host tool — Claude Code, Codex, OpenCode and eight others — and, when explicitly invoked, runs a fixed loop: choose a route, plan, build, check, independently verify, then finish. Roles are split across levels L0 to L4 so that no single agent plans a change, approves it and certifies its own verification. It requires Node.js 20+, Python 3.11+ with PyYAML and Bash 4.3+, and v2.0.0 ships a single CLI that activates the skill per provider. That is the whole product; everything below is about whether its number survives scrutiny.

## What Does "45% Fewer Failures" Actually Measure?

It measures one metric on one benchmark, once. Baseline OpenCode 1.18.7 solved 60 of 89 Terminal-Bench 2.1 tasks. With Autoprompt active, the same harness on the same model solved 73 of 89. Failures fell from 29 to 16.

That is a defensible statement, and it is also the limit of what the published evidence supports. The figure is a reduction in the failure **rate** on a single 89-task run, not a reduction in defects you will see in your repository, and not a comparison against any other tool.

| Read the same result a different way | Baseline | With Autoprompt | Change |
|---|---|---|---|
| Tasks solved | 60 / 89 | 73 / 89 | +13 tasks |
| Pass rate | 67.42% | 82.02% | +14.61 pp |
| Failure rate | 32.58% | 17.98% | −14.61 pp |
| Failures (count) | 29 | 16 | −44.8% (~45%) |
| Relative pass-rate gain | — | — | +21.67% |
| Failures per solved task | 0.483 | 0.219 | −54.7% |

Every row is the same data. The "45%" headline is the most flattering row that is still arithmetically true, which is exactly why it propagated and the rest did not.

## Why Is a 45% Reduction Really a 1.81x Claim?

Because a percentage reduction in failures is not a percentage improvement in capability, and the difference is large enough to change how you budget for it.

Two useful translations exist. In odds terms, 29 failures becoming 16 is **1.81x fewer failures** — the treatment arm fails about 55% as often. In rate terms, 32.58% becoming 17.98% is a **44.8% reduction in the failure rate**, rounded to 45%. Both are honest. "45% better agent" is not, and it is the phrase most readers hear.

For a working developer the odds reading is the operative one: on a hard task where the plain agent has a 33% chance of failing, the wrapped agent has roughly an 18% chance, so you still expect to repair one task in six. That is a meaningful improvement and it is not a transformation.

## What Is the Confidence Interval on the 45% Claim?

The error bar nobody publishes is +2.02pp to +27.20pp at 95% confidence. That is the single most useful number in this review.

| Statistic (60/89 vs 73/89, n = 89 per arm) | Value |
|---|---|
| Absolute difference in pass rate | +14.61 pp |
| 95% CI, two-proportion interval | **+2.02 pp to +27.20 pp** |
| Two-proportion z | 2.24 |
| Two-sided p (normal) | 0.025 |
| Fisher exact, one-sided p | 0.019 |
| Fisher exact, two-sided p | 0.038 |
| Statistical power to detect this effect at n=89 | ≈61% |
| n per arm to detect +5pp at 80% power | ≈1,319 |
| n per arm to detect +3pp at 80% power | ≈3,735 |

Read the interval, not the point estimate. The result is statistically significant — the lower bound clears zero — but the CI spans from "a marginal benefit you might not notice" to "a near doubling of the failure reduction you were promised." A 14.61-point change on 89 tasks cannot distinguish those two worlds, and it cannot rule out an effect as small as two points.

The lower bound is worth translating. At +2.02pp, the wrapped agent would pass 69.44% instead of 67.42% — about 61.8 solves instead of 60, meaning roughly one extra task solved out of 89 for the same ~2x token spend. That is the pessimistic-but-consistent version of the claim. Nobody selling this skill prints it.

The power figure matters too. With n=89, a study has only about a 61% chance of detecting an effect the size of the one actually observed. This is a single run reporting a positive result, not a replicate — and single runs in this size class routinely produce point estimates that shrink on retest.

## Is the Evidence Asymmetric — Did the Treatment Arm Keep Its Receipts?

No. The baseline retained all 89 per-task verdicts; the Autoprompt arm did not, and that asymmetry is more serious than a dead link.

The benchmark document links to a per-task verdict file that returns HTTP 404, and the top-level `benchmark/` directory it lived in is absent from the repository's main branch — verified by walking the full git tree on 2026-10-01, not inferred from the broken link. The document itself concedes that the Autoprompt arm "cannot be rebuilt task by task" because "its original per-task map was not retained." The baseline's ledger exists; the treatment arm's does not.

This inverts the usual storage pattern. When a benchmark claims an improvement, the arm whose result is surprising is the arm whose raw output you most need to inspect — to check for task contamination, harness leakage, retries, or selective reporting. Here the ordinary arm is fully auditable and the extraordinary one is a summary table.

None of that is proof of error, and it should not be read as an accusation. It is a statement about what a reader can verify: the published counts can be re-analysed (the interval above is that analysis), but the underlying per-task result cannot be reproduced or falsified without rerunning the whole benchmark at your own expense. A result you cannot rebuild is a result you must trust, and trust is the one input a benchmark is supposed to remove.

## Does the v2 Release Invalidate the Benchmark?

For the claim as currently marketed, yes — the 45% is version 1 evidence attached to a version 2 product.

v2.0.0 shipped on 2026-09-09 with a new CLI activation path, eleven provider adapters, `path=` controls (auto, direct, light, roadmap) and new concurrency controls. The benchmark was run with OpenCode 1.18.7 in the v1 line; the current repository lists OpenCode 1.18.29 among its tested hosts. As of 2026-10-01 the `docs/benchmarks/` directory contains only the Terminal-Bench 2.1 file, a Codex canary note and a low-compute mechanism note — **there is no v2 benchmark**.

That distinction is not pedantry. A new activation path, new routing controls and eleven adapter changes alter the very execution path the benchmark measured. Every article published after 2026-09-09 that presents 45% as the current, measured performance of the software you are about to install is citing a superseded artifact. The honest framing is: "v1 measured +14.61pp on one run; v2 is unmeasured."

## How Does Autoprompt Compare to Other Agent Skills?

Autoprompt sits in a small minority that works at all, and about in the middle of the curated-skill field — and the second half of that sentence is the part nobody likes.

Two independent benchmarks bracket this category. SWE-Skills-Bench evaluated 49 skills across roughly 565 task instances with deterministic pytest verification and found that **39 of 49 skills produced zero pass-rate improvement**, with an average gain of just +1.2%. Token overhead ranged from −78% to +451% while pass rates stayed flat, and three skills actively degraded performance by up to −10%. Anyone assuming a popular skill helps has roughly an 80% chance of being wrong about a random one.

SkillsBench is the kinder baseline: 87 tasks across 8 domains and 18 model-harness configurations, with matched no-skill and with-skill conditions. Curated skills lifted average pass rate from 33.9% to 50.5% — **+16.6pp**, a 25.5% normalised gain, with per-configuration gains from +4.1pp to +25.7pp.

Set Autoprompt's +14.61pp against those numbers:

| Evidence set | Scope | Effect on pass rate |
|---|---|---|
| SWE-Skills-Bench average | 49 skills, ~565 instances | +1.2 pp |
| SWE-Skills-Bench null result | 39 of 49 skills | 0 pp |
| SkillsBench fleet average | 87 tasks, 18 configs | +16.6 pp |
| **Autoprompt, Terminal-Bench 2.1** | **1 run, 89 tasks** | **+14.61 pp** |

The headline that looks enormous in isolation is slightly below the fleet average of curated skills in context. Both statements are true, and together they give the honest verdict: Autoprompt is in the minority of skills that measurably help, and it is not an outlier among them. If your baseline assumption was "agent skills do nothing" (a 1.2% expectation), this is a large win. If your baseline was "curated skills give about 16 points," this is ordinary.

## What Is the Trap Next Door for Self-Generated Skills?

The same SkillsBench work contains the finding most relevant to anyone tempted to copy the pattern: when agents were asked to author their own skills before starting a task, they performed **worse than baseline, dropping 8.1 to 11.5 percentage points**.

That is a direct warning for teams that read Autoprompt's architecture and conclude they can have their orchestrator auto-generate a project-specific checklist each run. The evidence says the opposite. Curated skills help; self-generated skills hurt, plausibly because an agent writing its own procedure optimises for plausibility rather than for the verification steps it is least likely to perform unaided. Autoprompt's own design leans the right way here — it is explicit, invoked by name (`/autoprompt`, `$autoprompt`, `/skill:autoprompt`) rather than authored on the fly — but the temptation to bolt on auto-generation is real, and the literature is not neutral about it.

## What Does the 45% Cost in Tokens and Time?

It costs roughly 3x wall-clock time and 2x tokens, and nobody has published the exchange rate between the two. We can compute an approximate one.

| Cost component | Published value | Evidence quality |
|---|---|---|
| Wall-clock time | ~3x | Project states it is a planning estimate from user reports |
| Tokens | ~2x | Same — timing and token logs were not retained |
| Pass-rate gain | +14.61 pp (CI +2.02 to +27.20) | Measured once, n=89 |
| Implied efficiency | ≈1.5–1.6 pp of pass rate per extra 10% of tokens | Derived by this review |

The project's own README labels the 3x/2x figures "planning estimates based on user experience reports, not measured benchmark results," which is unusually candid — most projects would print them as fact. But it also means the one number a buyer needs does not exist. At an assumed 1.9x token multiplier, the +14.61pp gain comes at roughly 90% more tokens than baseline; spread across the 13 extra solves, that is about **7% of a full baseline run's token budget per additional task solved**. Or, in the form that survives a business case: you are buying roughly 1.5 percentage points of pass rate for every extra 10% of tokens you spend.

Whether that is worth it depends entirely on the alternative use of the same tokens — a second opinion from a stronger model, a broader test suite, or simply a retry with a different seed. Autoprompt's honest framing is a price, not a percentage, and the price is currently an estimate of an estimate.

## Why Do Failure-Reduction Tools Exist at All?

Because long-horizon reliability, not raw capability, is the binding constraint — and the arithmetic of chained steps explains why a verification layer can help at all.

METR's time-horizon research found that frontier agents succeed on nearly 100% of tasks a human would finish in under about four minutes, but on under 10% of tasks taking a human over roughly four hours, with the 50%-reliability horizon doubling approximately every seven months since 2019. Capability is not the problem at long horizons; the ability to keep 20 or 50 steps correct is.

Compounding makes that concrete. At 95% per-step reliability, a 20-step task succeeds about 36% of the time and a 50-step task about 8%.

| Per-step reliability | 20-step task success | 50-step task success |
|---|---|---|
| 90% | 12.2% | 0.5% |
| 95% | 35.9% | 7.7% |
| 97% | 54.4% | 21.8% |
| 99% | 81.8% | 60.5% |

This is why a loop that adds independent verification is a plausible intervention rather than a gimmick: it targets step-level error, which is where the compounding lives. It is also why the *size* of Autoprompt's measured gain is plausible — moving an agent from roughly 67% to roughly 82% on a hard terminal benchmark is exactly the scale of improvement you would expect from catching a fraction of mid-trajectory mistakes, not from making the model smarter. And it is why the measurement is hard: the same compounding that makes the intervention valuable makes single-run estimates volatile.

## Is 82.02% Actually a Good Score?

It is a mid-table score. Public Terminal-Bench 2.1 leaderboards put top model-harness combinations at roughly 87–91% on the same 89 tasks, so Autoprompt's 82.02% — with an 89-task, OpenCode 1.18.7, DeepSeek V4 Flash harness — sits below the frontier, not at it.

The comparability warning matters as much as the number. Terminal-Bench scores are not interchangeable across boards: the official board measures agent-plus-model combinations, Artificial Analysis tests models directly with labelled effort tiers, and vals.ai retests everything under a unified Terminus 2 harness. Citing "82.02%" without naming the harness and model invites a wrong read, in either direction — as a disappointing score when the harness was never frontier, or as a frontier score when the board is measuring something else. The safe sentence is the specific one: OpenCode 1.18.7 with DeepSeek V4 Flash and Autoprompt scored 82.02% on Terminal-Bench 2.1.

## Why Do the Stars and npm Downloads Point the Other Way?

Adoption is decelerating while the headline number compounds, and the open-issue queue tells you where maintainer attention is going.

| Signal (as of 2026-10-01) | Value |
|---|---|
| GitHub stars | 1,298 |
| Forks | 88 |
| Open issues | 3 — all Windows activation blockers |
| Created / last push | 2026-08-17 / 2026-09-28 |
| Licence | MIT |
| Stars/day, first 3 days | ≈146/day |
| Stars/day, following ~38 days | ≈23/day |
| npm `latest` | 1.0.4 (published 2026-08-21) |
| npm downloads, week to 2026-09-29 | 32 |
| npm downloads, month to 2026-09-29 | 144 |

The star curve is a launch burst into a slow tail, not compounding growth: roughly 146 stars a day for three days, then about 23 a day for the next five weeks. npm tells the same story more sharply — the published package is still 1.0.4, two minor lines behind GitHub's v2.0.0, and therefore still carries nine providers and the old `mode=`/`max_subs=` interface. Weekly downloads are in the tens.

Meanwhile the three open issues are all Windows activation failures (#27 native Windows refused, #28 OpenCode `cmd-shim` EINVAL, #29 npm shims for native package bins), and the README's own requirement line says "these versions passed Linux runs." The practical reading: the eleven-provider claim is a **code-path** claim, the **verified execution surface is Linux**, and if you are on Windows you are currently the maintainer's queue. If you want the tool to keep working, file issues rather than stars.

## How Portable Is Autoprompt Across Its 11 Host Agents?

The adapters are real, and portability is the dimension no agent-skill framework has fully solved.

The tested-version table lists Claude Code 2.1.263, Codex 0.148.0, OpenCode 1.18.29, Kilo Code 7.5.15, VS Code 1.136.1, Prime Agent 0.7.2, Oh My Pi 18.1.14, DeepSeek Harness 0.1.2-rc.1, Reasonix 1.30.0, Hermes Agent 0.21.1 and Grok Build 1.0.13 — eleven hosts, each pinned to a version that passed on Linux. The v2 CLI unifies activation across them, which is genuine progress over the v1 invocation-per-host mess.

Two gaps remain. First, one independent review rates the project's portability "portable with changes" rather than portable, because the v2 CLI activation path is provider-specific — the unification is at the command surface, not at the execution semantics. Second, custom model routing does not exist on all hosts, so a team that needs to pin a specific model per role will find the coverage uneven. Independent taxonomy work reaches the same conclusion at the framework level: no agent-skill system currently covers specification, context, roles, execution, validation and portability simultaneously. Budget for a portability tax on any host other than Linux plus a mainstream agent.

## Who Should Use Autoprompt in 2026, and Who Should Not?

Buy it for hard, ambiguous tasks on a Linux workstation with an established host agent — and skip it everywhere else.

**A good fit if you:**
- Run Claude Code, Codex or OpenCode on Linux or macOS and already have a working test suite.
- Spend your time on multi-step, underspecified tasks where the agent "gets stuck mid-task" rather than failing instantly.
- Value the verification structure more than the speed — the independent-check discipline is the durable part of the design, and it is transferable even if you later drop the tool.
- Need evidence you can point at: the +14.61pp gain is statistically significant, and you now know its interval.

**A poor fit if you:**
- Do very small tasks. A 2x token multiplier on a one-file change is pure loss, and the project itself notes gains may vary significantly between small and large tasks.
- Work primarily on Windows today. All three open issues are Windows activation failures.
- Need custom model routing on every host.
- Have no local terminal runtime for the agent to execute in — without that, there is nothing for the verification loop to verify.
- Are choosing between Autoprompt and simply spending the same 2x tokens on a stronger model or a larger test suite. That comparison has never been published, and it is the one that decides most budgets.

Read against the third-party score available — FollowAgents rates the project 69/100, "use with care," with praise focused specifically on disclosure quality and a caveat that the review is stale on provider count and version — the fair summary is that the engineering and the honesty are both above average while the evidence remains one run.

## How Do You Reproduce or Reject the Claim Yourself?

The claim is falsifiable, and the cheapest path is a paired test on your own backlog.

1. **Fix the harness.** Pin one host agent and one model. Mixed hosts invalidate every comparison, as the three-board divergence on Terminal-Bench 2.1 shows.
2. **Select tasks with headroom.** Pick 30–50 tasks you already fail. Testing on tasks you pass measures nothing.
3. **Run both arms on the same tasks.** Baseline run, then an Autoprompt run, same commit, same environment, ideally same day to reduce drift.
4. **Score deterministically.** Use your test suite or an external grader, not agent self-assessment. This is the step most teams skip, and it is the step that matters — an agent judging its own work is precisely the failure mode the skill exists to prevent.
5. **Compute the interval, not just the difference.** At 30 paired tasks you have almost no power; a 15-point difference on 30 tasks will not be distinguishable from noise. If your observed difference is small, treat the result as inconclusive rather than negative.
6. **Log tokens and wall clock.** The project could not, and that is why its cost figure is an estimate. Your run should not repeat that mistake.
7. **Run `autoprompt doctor --strict`** before measuring, so a partial install is not scored as a skill failure.

Expect a real but unglamorous outcome. The published effect is +14.61pp with a lower bound of +2.02pp; on a 40-task set, a plausible result is three to six extra solves at roughly double the tokens.

## What Is the Verdict on the Autoprompt Skill?

It works, the number is real, and the number is smaller and less certain than the headline implies.

The defensible statement of the evidence is this: on a single 89-task Terminal-Bench 2.1 run, wrapping OpenCode 1.18.7 with Autoprompt raised pass rate from 67.42% to 82.02%, a +14.61pp gain (95% CI +2.02pp to +27.20pp, p=0.025) that reduces the failure rate 44.8% — 1.81x fewer failures — at an estimated 3x time and 2x tokens, with no v2 benchmark yet published.

Everything past the comma is why this article exists. Most surfaces that rank for "autoprompt skill" have already lost it: catalog pages still publish nine providers, v1.0.4 and 940 stars while the repository says eleven providers, v2.0.0 and 1,298 stars. The 45% survived intact while every verifiable detail around it decayed — which is the normal behaviour of a good headline and the reason it deserves an error bar. Use the skill for hard tasks, budget the tokens honestly, and quote the interval.

## FAQ

**Does the Autoprompt skill actually work?**
The evidence says yes, within limits. Autoprompt's own Terminal-Bench 2.1 run moved OpenCode 1.18.7 from 60/89 to 73/89 solves (+14.61pp, p=0.025), and independent category benchmarks show most agent skills produce no measurable gain at all, so a skill that clears the bar is a minority case. However, the result is a single 89-task run, the treatment arm's per-task ledger was not retained, and the 95% confidence interval spans +2.02pp to +27.20pp. Treat it as a real but imprecisely measured improvement, not a guarantee.

**Where does the 45% figure come from and is it accurate?**
It comes from failures falling from 29 to 16 on 89 Terminal-Bench 2.1 tasks. That is a 44.8% reduction in the failure rate, so 45% is accurate as a description of that specific metric. It is not a 45% improvement in capability: the pass rate rose 14.61 points (67.42% to 82.02%), the relative pass-rate gain is 21.67%, and in odds terms the wrapped agent fails 1.81x less often. Any source describing it as "45% better" has changed the meaning of the number.

**What is the confidence interval on the Autoprompt benchmark, and why does it matter?**
The +14.61pp difference corresponds to a 95% confidence interval of roughly +2.02pp to +27.20pp at n=89 per arm (two-proportion z=2.24; Fisher exact two-sided p=0.038). No competitor publishes this. It matters because the interval is wide: the same data is consistent with a benefit as large as 27 points and as small as 2 points, and at 2 points the tool would win about one extra task out of 89. With n=89, statistical power to detect the observed effect is only about 61%, so this should be read as a positive single run, not a settled effect size.

**Does Autoprompt work on Windows, and is the npm package current?**
Windows is currently the hard gate: all three open issues on the repository as of 2026-10-01 are Windows activation failures (#27 native Windows refused, #28 OpenCode cmd-shim EINVAL, #29 npm shims for native package bins), and the project states that its tested versions "passed Linux runs." Separately, npm's `latest` tag is still 1.0.4 (published 2026-08-21), two minor lines behind the GitHub v2.0.0 release of 2026-09-09, so the npm package still ships nine providers and the old `mode=`/`max_subs=` interface. Install from the v2.0.0 release if you need the CLI and the eleven adapters.

**How much does Autoprompt cost in tokens and time, and is it worth it?**
The project estimates roughly 3x wall-clock time and 2x tokens, and explicitly labels both as planning estimates from user experience reports because timing and token logs were not retained. Pair that with the +14.61pp gain and you get approximately 1.5 to 1.6 percentage points of pass rate per extra 10% of tokens — a real but modest exchange rate. It is worth it on hard, multi-step tasks where your agent tends to get stuck and you have a deterministic test suite to verify against. It is a clear loss on small single-file changes, where the multiplier buys nothing.
