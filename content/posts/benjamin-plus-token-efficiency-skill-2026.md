---
title: "Benjamin-Plus Review 2026: A Measured Token-Efficiency Skill for Coding Agents"
date: 2026-09-21T07:01:43+00:00
tags:
  - coding agents
  - token efficiency
  - AI cost optimization
  - agent skills
  - Claude Code
  - Codex
  - AI engineering
  - benchmark-driven skill engineering
description: "Benjamin-Plus is a JetBrains token-efficiency skill for coding agents, measured at up to -18% cost with unchanged quality. This 2026 review explains whether it is worth injecting."
draft: false
cover:
    image: "/images/benjamin-plus-token-efficiency-skill-2026.png"
    alt: "Benjamin-Plus Review 2026: A Measured Token-Efficiency Skill for Coding Agents"
    relative: false
schema: "schema-benjamin-plus-token-efficiency-skill-2026"
---

Benjamin-Plus is a JetBrains-published, MIT-licensed token-efficiency skill for coding agents that measurably cuts cost per task by up to 18% and total tokens by up to 22% without detectable quality loss. In this 2026 review we walk through the independent paired A/B results, the five habits it teaches, the decisive finding that you must inject it rather than install it, and a practical adoption checklist for Claude Code, Codex, and Cursor.

## What Is Benjamin-Plus and Where It Came From

Benjamin-Plus is an open-source "instruction-set skill" released by JetBrains on August 17, 2026. It does not change what your coding agent builds; it changes how the agent looks things up and waits. The core claim, stated directly in the repository, is that the skill "changes how the agent looks things up and waits, never what it builds" — and every saving is measured against a paired-A/B baseline rather than asserted.

The project sits inside a wider JetBrains effort to get AI spend under control. JetBrains has been benchmarking public "token saver" add-ons with the same paired-A/B method: Part 1 tested caveman (advertised as −65% cost, measured at −8.5%), and Part 2 tested rtk (advertised as −60–90%, measured at +7.6%). Benjamin-Plus applies the same discipline to its own skill — publish the methodology, publish the honest caveats, and let the numbers speak.

The repository gained traction quickly: by September 2026 it had roughly 311 stars and 13 forks per gitstars, with Cult of Claude listing it at 272 stars as of August 27, 2026 under Development. It is a genuinely useful case study in how agent skills are shifting from collections of convenience prompts into engineered, benchmark-validated assets.

## The Core Thesis — Agents Pay Twice for Every Clumsy Lookup

The economic argument behind Benjamin-Plus is subtle and worth understanding. Every clumsy agent action is paid twice: once for the step itself, and again for every re-read of the growing conversation context in later turns. When an agent spams a broad search or dumps thousands of lines into context, that noise is not erased — it accumulates and gets re-read every subsequent turn, compounding the cost.

This is why the skill's five habits attack structure, not intelligence. The thesis is that "small waste" in long agent traces accumulates in conversation context and gets re-read every turn. Batch the reconnaissance, narrow the reads, probe once, stop at green — each of these trims both the immediate cost and the compounding context that follows.

## The Five Habits Benjamin-Plus Teaches (with Rationale)

Benjamin-Plus codifies five operating habits. Each one maps to a measurable waste class:

1. **Recon in one pass.** Batch repository reconnaissance into a single pass instead of many fragmented lookups. Each lookup you avoid is a step not spent and context not added.

2. **Keyhole reads.** Read about 50 lines instead of a whole file, unless full data is needed. Critically, the skill ensures transformed data is never truncated — so narrowing a read does not silently break correctness.

3. **Probe the environment once.** Instead of probing dependencies or the environment repeatedly, consolidate probe commands into one pass. Redundant probing is pure overhead.

4. **Green means done.** Treat the task's own verification command as the definition of done and stop when it passes. Many agents keep "polishing" past the first green build, spending tokens for no measurable gain.

5. **Polling is a step.** Check unfinished builds every 30 seconds rather than every second. This habit was added after Java SWE-bench traces showed that 45.8% of the treated arm's agent steps were polls, with 3,982 of them yielding at sub-5-second intervals — a near-total waste.

These habits sound obvious in retrospect, which is exactly the point. The skill's contribution is making them a default discipline rather than leaving them to the agent's discretion.

## The Numbers — What Paired A/B Actually Measured

The headline results come from the v6 FINAL run on EXPECTED-RESULTS.md: 80 paired SkillsBench tasks on Sonnet 5 at low effort under Claude Code 2.1.201. The results were statistically solid:

| Metric | Measured change | Significance |
|---|---|---|
| Median cost (paired) | −17.9% | p=0.005 |
| Total cost | −16.7% | — |
| Turns | −20.0% | p=0.001 |
| Total tokens | −21.9% | p=0.001 |
| Cache reads | −23.9% | — |
| Output tokens | −21.2% | — |
| Code written | −13.3% | — |
| Wall-clock time | −15.6% | — |

Quality was unchanged: 7 tasks better, 5 worse, and 68 ties (sign test p=0.77), with the Verifier mean reward moving from 0.362 to 0.392. The authors are explicit that the study was not powered as an equivalence test — they cannot prove quality is identical, only that no difference was detected.

The benchmark program itself was modestly expensive: roughly $153 in spend across 254 billed trials to develop and validate the skill through iterative paired A/B. For a cost-reduction tool, that is a striking and honest line item.

## The Decisive Finding — Inject It, Don't Install It

The single most actionable finding is about distribution. Injected saves cost, and a discoverable skill folder saves nothing. When the skill was injected directly into agent instructions, it delivered −17.9% median cost. When installed as a discoverable skill folder that the agent had to go find, it saved essentially nothing (−0.5%, not significant) — because agents burned roughly 3 steps with a 73% path-miss rate simply locating the SKILL.md file.

This means the install guidance on repositories (copy the folder into ~/.claude/skills/) is actually the wrong path for Benjamin-Plus. The intended and measured-effective distribution is injection: append the injected-instruction file to session prompts, system prompts, Claude Code hooks, a Codex AGENTS.md, or a project CLAUDE.md. The injected payload is small — roughly 745 tokens in total, with the full injected-instruction.md at about 3KB.

## Cross-Platform Replication on Java SWE-bench

The result is not confined to Claude Code. An independent install-method study on Java SWE-bench using Codex CLI (gpt-5.6-luna) across 675 paired replicas found that hook-injected Benjamin-Plus delivered −4.4% cost with a 95% confidence interval of [−7.5, −1.5] (p=0.003), left the solve rate unchanged (p=0.22), and cut tool calls by 20%.

The effect size is smaller than the Claude Code run, which makes sense: the replication used a leaner baseline, so there was less waste to remove. The direction is consistent, however, and the solve rate was untouched — the same "free lunch" pattern.

The Java study also produced the data that motivated the "polling is a step" rule: 45.8% of the treated arm's agent steps were polls, with 3,982 yielding under 5 seconds.

## Benjamin-Plus vs Other Token-Saver Skills

The wider ecosystem of token-saver skills has a poor track record, which makes Benjamin-Plus look good by contrast. JetBrains' own measurements:

| Skill | Advertised saving | Measured saving |
|---|---|---|
| caveman | −65% | −8.5% |
| rtk | −60–90% | +7.6% (cost increased) |
| Ponytail | −54% | measured in detail, below claims |
| Benjamin-Plus | "up to −18%" | −17.9% median (Claude Code), −4.4% (Codex/Java) |

The distinction is method, not marketing. Benjamin-Plus under-claims and over-delivers against its measured ceiling, and it publishes the full methodology and honest caveats rather than hand-picked screenshots. That alone justifies treating it differently from its peers.

## Honest Caveats — Effect Size, Baselines, and Quality-Testing Limits

It would be easy to overstate Benjamin-Plus. The honest reading is that it works as a session-cost variance clamp rather than a universal discount. Consider the evidence:

- The v5 same-day run measured −10.0% median cost but with p=0.169, which is not statistically significant. The control baseline drifted by +10.5% between days while the treated arm stayed flat (−3.0%).
- The practical floor is around −10% on an already-lean baseline day, rising to roughly −18% against a bloated baseline. If your sessions are already disciplined, expect the lower end of the range.
- The quality result (7 better / 5 worse / 68 ties) shows no detectable loss but is explicitly not powered as an equivalence test. You cannot claim identical quality with statistical certainty.

The right mental model is that Benjamin-Plus clamps variance: it does the most good when baseline sessions are bloated with wasteful lookups and polls, and modest good when they are already tight.

## How to Adopt Benjamin-Plus in Claude Code, Codex, and Other Agents

The adoption checklist follows directly from the measurement:

1. **Inject, don't install a skill folder.** Append the injected-instruction.md content to your system prompt, a project CLAUDE.md, a Codex AGENTS.md, or drive it through Claude Code hooks. Do not rely on the agent discovering a skill folder on its own.

2. **Verify the injection landed.** In Claude Code, confirm the payload is live via `/hooks` or by checking that the injected ruleset appears in the session context. A payload that silently failed to load buys you nothing.

3. **Baseline before you adopt.** Run a few representative tasks without the skill and with it, so you can compute your own paired delta rather than trusting a headline number. Your baseline may already be lean.

4. **Watch the right signals in traces.** After adopting, look at tool-call counts, polling steps, and cache-read volume. A drop in poll count is one of the clearest early signs the habit is being followed.

5. **Calibrate expectations.** Expect roughly −10% to −18% depending on how bloated your baseline is, and treat any large claimed number with the skepticism the wider JetBrains benchmark series demands.

## The Bigger Trend — Benchmark-Driven Skill Engineering

Benjamin-Plus matters beyond its own numbers because it points at a structural shift. Competition in AI coding is moving from which model you pick to how you design and validate the skills and habits around the model. "Skill evaluation" is emerging as an independent layer beside Model, Harness, and Memory — the idea that a skill's worth should be proven by paired A/B measurement, not by its claims.

A related trend analysis in the developer community frames Benjamin-Plus as a "hidden gem" that measures agent waste, contrasting it with tools like Autoprompt that may trade higher pass rates for doubled tokens and tripled time. The thesis is that agent skills are evolving from convenient prompt collections into engineering assets measured and improved with evidence. For teams running coding agents at scale, this is the more durable lesson: the tool that survives is the one whose effect you can measure.

## Verdict — Is Benjamin-Plus Worth Injecting in 2026?

For most teams, yes, with a clear caveat. Benjamin-Plus is a well-engineered, honestly measured token-efficiency skill that appears to deliver a genuine free lunch: meaningful cost and token reductions with no detectable quality loss, and a methodology transparent enough to verify yourself. The key is to take the installation advice literally — inject the payload rather than dropping a skill folder — and to calibrate expectations to roughly −10% to −18% depending on baseline bloat.

The cost of trying it is low. The payload is about 745 tokens, it does not change what your agent builds, and the benchmark program cost JetBrains only ~$153 to produce. Against a landscape of token-saver skills whose claims routinely do not survive A/B testing, Benjamin-Plus stands out precisely because its measured numbers hold up. Inject it, benchmark it against your own baseline, and watch the poll counts and cache reads fall.

## FAQ

**What is the Benjamin-Plus token efficiency skill?**
Benjamin-Plus is a JetBrains-published, MIT-licensed instruction-set skill for coding agents that teaches five operating habits — batch reconnaissance, keyhole reads, single-pass environment probing, treating the verification command as done, and polling at longer intervals — to reduce token and tool-call usage without changing what the agent builds.

**How much does Benjamin-Plus actually save?**
In the v6 FINAL paired A/B on 80 SkillsBench tasks it measured median cost −17.9% (p=0.005), total tokens −21.9%, and wall-clock −15.6%. A Codex CLI replication on Java SWE-bench measured −4.4% cost. The practical range is roughly −10% to −18% depending on how bloated your baseline is.

**Does Benjamin-Plus reduce code quality?**
No detectable quality loss was found: 7 tasks better, 5 worse, and 68 ties (sign test p=0.77), with mean reward moving from 0.362 to 0.392. The authors note the study was not powered as an equivalence test, so identical quality is not proven with statistical certainty.

**Should I install Benjamin-Plus as a skill folder or inject it?**
You should inject it, not install it as a discoverable skill folder. Injected, it delivered −17.9% median cost; as a skill folder it saved essentially nothing (−0.5%) because agents burned roughly 3 steps with a 73% path-miss rate locating SKILL.md. Append the injected-instruction to a system prompt, CLAUDE.md, AGENTS.md, or Claude Code hooks.

**Is Benjamin-Plus free and open source?**
Yes. It is released by JetBrains under the MIT license, and the injected payload is small (roughly 745 tokens total). The benchmark program cost about $153 across 254 billed trials to develop.
