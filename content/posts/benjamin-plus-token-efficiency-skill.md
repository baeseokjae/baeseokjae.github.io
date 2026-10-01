---
title: "Benjamin Plus Skill Review: The Measured Token-Efficiency Skill for Coding Agents"
date: 2026-10-01T00:43:43+00:00
tags:
  - benjamin plus skill
  - benjamin-plus token efficiency
  - JetBrains benjamin-plus
  - token efficiency skill for coding agents
  - reduce claude code token cost
  - agent token efficiency benchmark SkillsBench
  - inject skill vs install skill agent
  - agent polling token waste
  - keyhole reads agent context
description: "Benjamin Plus is JetBrains' MIT token-efficiency ruleset for coding agents: injected, it measured -17.9% median cost (p=0.005), quality unchanged."
draft: false
cover:
    image: "/images/benjamin-plus-token-efficiency-skill.png"
    alt: "Benjamin Plus Skill Review: The Measured Token-Efficiency Skill for Coding Agents"
    relative: false
schema: "schema-benjamin-plus-token-efficiency-skill"
---

The Benjamin Plus skill is a ~745-token ruleset that JetBrains publishes under MIT to cut coding-agent cost by changing how an agent looks things up and waits. On 80 paired SkillsBench tasks it measured −17.9% median cost (p=0.005) with no detectable quality loss — but only when injected into the prompt, not installed as a discoverable skill.

---

## What Is the benjamin-plus Skill, and What Does It Refuse to Be?

Benjamin-Plus is a five-rule instruction payload for coding agents, published by JetBrains on 2026-08-17 and licensed MIT. It changes how your agent performs lookups and waits; it never changes what the agent builds. The repository states the thesis in one sentence: "An agent pays twice for every clumsy lookup: once for the step itself, and again every time the growing conversation gets re-read."

That distinction matters because most "token saver" add-ons are prompt personality — instructions to talk in a clipped voice and hope the bill follows. Benjamin-Plus refuses that genre in three specific ways:

- **It never touches your output style.** It does not ask the agent to write telegraphically, skip explanation, or compress diffs. Every rule governs tool use and scheduling, not prose.
- **It ships paired A/B receipts with p-values.** The repository publishes a results document with medians, totals, per-metric significance, adoption verification, and the dollar cost of the evaluation program.
- **It argues against its own headline.** The results document includes the earlier run in which the same skill measured only −10.0% median cost at p=0.169 — not significant — and explains why.

The artifact itself is deliberately small. RULESET.md is 3,656 bytes and injected-instruction.md is 3,165 bytes; the README quotes ~745 tokens injected for v6, which matches a chars/4 heuristic on the payload (749). Integration cost is about 3 KB, and distribution is injection only — the README says so plainly and the metadata supports it: a `npx skills add` lookup against the repository fails to find a valid skill, because the project does not want to be discovered. That is not an oversight. It is the thesis.

Scale is worth stating honestly before anyone cites popularity. As of October 2026 the repository sits at 330 stars, 14 forks, 2 open issues, 1 contributor, 5 commits, no releases and no CI. Third-party directories captured earlier snapshots — 272, 283, 298, 311 — so the numbers drift, and none of them are an argument for adoption. This is a well-written document from one contributor, and the headline is trust in that document rather than a rerunnable harness (more on that below).

## The Five Habits, Each Mapped to a Measurable Waste Pool

The rules are mechanical on purpose. Each one targets a specific way an agent burns steps, and the benchmark tracks whether the rule actually fired.

| Rule | What it says | Waste pool it targets | Adoption evidence |
|---|---|---|---|
| 1. Recon in one pass | Chain probes with `;` and label the sections; sample two examples before copying a convention | Serial exploratory round-trips | Labelled probe chains rose 10 → 102 commands |
| 2. Look through a keyhole | `\| head -50`, or offset+limit, for inspection only | Context residue that gets re-paid every turn | Read calls fell 144 → 57; Read with offset/limit rose 20% → 28% |
| 3. Probe the environment once | Check every dependency in one command; install missing packages in one go | Repeated discovery of the same environment fact | Batched dependency probes rose 7/80 → 22/80 trials |
| 4. Green means the task's own check | The task-named verification command defines done; an "environmental" failure is still yours | Verification loops and false-green stops | Guardrail: same check failing twice means the approach is wrong; when it passes, stop |
| 5. Polling is a step | Wait in ≥30-second slices; never re-poll at 1s | Scheduling waste, not prompt wording | Added in v6 after 45.8% of treated-arm steps were polls |

Rule 5 is the newest and the most interesting, because it was not designed — it was discovered. Java SWE-bench traces showed that 45.8% of the treated arm's agent steps were polls, with 3,982 of them resolving in under five seconds. An agent waiting on a build was spending a step to learn nothing. Reframing that as a scheduling problem rather than a verbosity problem is the single most transferable idea in the payload.

Rules 2 and 3 also come with explicit misfire conditions, which is rarer than it should be. Community issue #9 documents that the keyhole rule can *add* a step with zero context savings on a small file: reviewing the 65-line RULESET.md takes one direct `cat`, not a measure-then-slice sequence. The rules are conditional heuristics with stated boundaries, not laws.

## Why Any of This Works: Stateless APIs and Transcript Residue

The mechanism is not mysterious, and understanding it is what separates a real evaluation from a plausible story. Chat completions APIs are stateless: every turn resends the whole conversation. Cost is therefore roughly transcript size multiplied by turns. A file read on turn 3 of a 40-turn run is paid for again on each of the following 37 turns.

An independent model-free wire-cost harness makes the arithmetic concrete. With 36 scripted tool calls across 37 turns, the baseline run moved 4,157,949 bytes — about 1,039,487 tokens — which works out to 112,377 bytes per turn. A tuning pass halved it to roughly 517,000 tokens. The harness also caught an "optimization" that made the run 10% *worse* until measurement exposed it, which is the best available argument for measuring token work instead of intuiting it.

This is exactly why "keyhole reads" and batching pay. The expensive thing is not the lookup; it is the residue the lookup leaves in the transcript for every subsequent turn. It is also why tool schemas matter: trimming a tool block from 5,193 to 4,556 bytes saved roughly 160 tokens per turn, and a build-time byte budget now fails the build if the block grows back. Any percentage saving from a skill is competing against these structural costs.

## How Was the Benjamin Plus Skill Measured? Paired A/B, Not Vibes

This is the part most reviews skip, and it is the reason the number is worth quoting. The v6 evaluation ran on 80 paired SkillsBench tasks with Claude Code 2.1.201 in Docker, Sonnet 5 at low reasoning effort, job label `bp6-final`, on 2026-08-16. Analysis is Wilcoxon signed-rank on paired deltas — the treated and control arms run the same task, and the comparison is per-pair, not between two unrelated averages.

| Metric | Change | p-value |
|---|---|---|
| Cost, median paired | −17.9% | 0.005 |
| Cost, totals | −16.7% | — |
| Turns | −20.0% | 0.001 |
| Total tokens | −21.9% | 0.001 |
| Cache reads | −23.9% | 0.001 |
| Output tokens | −21.2% | 0.007 |
| Code written | −13.3% | 0.006 |
| Wall-clock | −15.6% | 0.018 |
| Fresh input tokens | −7.8% | 0.125 (n.s.) |
| Quality (verifier reward) | 0.362 → 0.392 | 0.77 (sign test) |

Two rows deserve special attention. First, fresh input tokens were *not* significantly reduced. The skill saves by not re-reading, not by writing a shorter prompt — which is consistent with the mechanism above and inconsistent with the idea that a clever phrase makes models thrifty. Second, quality moved from 0.362 to 0.392 mean verifier reward with 7 better / 5 worse / 68 tie outcomes. That is not evidence of improvement; it is evidence of no large harm. The document says so itself: it is "not powered as an equivalence test — large effects ruled out, small ones not."

Adoption was verified mechanically rather than assumed. The payload reached the model in 80 of 80 treated runs and 0 of 80 controls, and the behavioural traces above confirm the rules changed tool use rather than merely being present. Disclosure is also unusually complete: the whole evaluation ladder cost roughly $153 across 254 billed trials.

## The Honesty Notes: Where −17.9% Does Not Apply

The most credible thing in this repository is the section that weakens its own claim. Read these four caveats before quoting any number.

**The earlier run was not significant.** A same-day v5 comparison on 2026-08-15 (job `bp-final`) measured only −10.0% median cost at p=0.169, not significant at 80 pairs. The v5 wins that *were* solid were code written (−11.5%, p=0.012) and wall-clock (−13.9%, p=0.039).

**Savings scale with baseline bloat, not with task.** Between the two evaluation days the control arm drifted +10.5% median (+20.5% on totals) while the treated arm stayed flat at about −3.0%. That means the skill behaves less like a fixed discount and more like a session-cost variance clamp: it removes the expensive way of doing things, so it saves the most precisely when a session was running badly. Against a lean baseline it saves little; against a bloated one it saves more. The honest range in the README is −10% to −18% cost.

**Medians and totals disagree.** In v5 the skill was cheaper on the median task but flat in aggregate: arm totals came in at +0.6% cost. The reason given is that the skill "wins the middle of the distribution and gives some of it back on trap-task tails." If you are budgeting a monthly bill, read totals; if you are judging whether the skill generally helps, read medians. They are different questions.

**Quality was not proven equivalent.** 80 pairs can rule out large quality effects. It cannot rule out small ones, and nobody should present it as if it can.

There is also a rule-level caveat still open on the board. Issue #17 reports that the dependency-probe rule is not robust for dotted module names (`find_spec` raises on dotted names), so the "probe the environment once" habit can misreport a present dependency as missing on some Python projects.

## Inject, Don't Install: The Load-Bearing Evidence

If you take one thing from this review, take this. The delivery method was tested head-to-head, and the result is decisive.

The external validation ran on Java SWE-bench with Codex CLI and gpt-5.6-luna: 225 instances × 3 replicas, or 675 paired replicas.

| Delivery method | Cost change | Significance | Other effects |
|---|---|---|---|
| Hook-injected (SessionStart) | −4.4% [−7.5, −1.5] | p=0.003 | Solve rate unchanged (p=0.22); tool calls −20% |
| Skill-folder install | −0.5% | not significant | Median 3 steps burned locating SKILL.md; 73% path misses |

The skill-folder arm saved nothing net, and the reason is mundane: the agent had to find the skill first. A median of 3 wasted steps with 73% path misses is enough to erase the entire benefit of a 745-token payload. Third-party directories make the problem worse — they list the repository without the path inside it, which is precisely the friction the injection-only stance is designed to avoid.

This generalizes well beyond this repository. It is the sharpest counter-argument in circulation to "move everything into skills," and it is measurable in your own setup. The skill-index tax is not hypothetical: one measured registry of 78 skills cost 8,260 tokens of context before the user typed anything, and Anthropic documents roughly 100 tokens per skill's name and description. A separate measured Claude Code setup paid 7,778 prompt tokens simply for knowing which skills existed, versus 26,835 with slash commands disabled across 84 headless runs. Discovery looks cheap and bills per turn; injection is resident but tiny and fixed.

A study of 55,315 public skills reinforces the same conclusion from the supply side: 26.4% lack routing descriptions entirely, over 60% of body content is non-actionable, and compressing descriptions by 48% and bodies by 39% slightly *improved* functional quality (2.8%). If your agent must search that corpus to find the right skill, discovery is a cost center, not a feature.

## Cross-Platform Reality Check: Codex, Java, and Other Harnesses

Do not promise a Codex team the SkillsBench figure. The effect shrank to −4.4% on Java SWE-bench, which is still statistically significant and still came with a 20% reduction in tool calls — but it is a quarter of the headline. The likely explanation is the workload, not the skill: Java repository work has more compile-test loops and longer mechanical stretches where the five rules have less discretionary waste to remove. SkillsBench tasks reward reconnaissance and keyhole reading; a Maven build does not.

There is a second, more structural limit worth knowing. In the rtk evaluation, the same lab measured that a Bash hook only ever sees about 33% of Bash calls, roughly 20% of tool-result characters, because Claude Code's built-in Read and Grep bypass the hook entirely — and cached re-reads bill at about a tenth of the price. That bounds what any interception-layer product can claim, and it is a reason to prefer instruction-level payloads over proxy-level ones: the payload governs the tool call the agent *chooses*, while a hook only sees what passes through it.

## Which Token Efficiency Skill Should You Actually Use?

"Token efficiency skill" is now a category with genuinely different bets inside it. Benjamin-Plus is not the whole market, and picking between them is a question about where your waste actually lives.

| Skill | Stars | Core bet | Measured result | Delivery |
|---|---|---|---|---|
| JetBrains benjamin-plus | 330 | Steps and context residue | −17.9% median cost (p=0.005); −4.4% on Java SWE-bench | Injection only |
| Kulaxyz/token-diet | 473 | Output and artifact volume | −31% average bill, −53% output across three sessions; −54%/−81% output-heavy, −22%/−49% code+tests, −17%/−30% read-heavy | SessionStart hook or always-loaded context |
| undefdev/token-efficiency | 30 | Tool hygiene (jq/rg/git) | No paired A/B published; ships a self-declared sunset notice | Native marketplaces |
| phoenixlucky/zerotoken-skill | 17 | Process order and task modes | Seven-mode decision table with per-mode token budgets; no paired A/B published | GitHub + ClawHub |

The distinction that matters: token-diet compresses what the agent *says and produces*, while benjamin-plus compresses how the agent *looks things up and waits*. They are not substitutes. If your sessions are output-heavy — long plans, verbose summaries, huge test dumps — token-diet's bet is the one that pays. If your sessions are step-heavy — serial greps, repeated environment probes, polling loops — benjamin-plus's bet pays. undefdev's skill assumes your problem is that the agent shells out to Python when `jq` would do, and it is honest enough to predict its own obsolescence as models improve. zerotoken is a mode-selection framework rather than a rule set, closer to a process discipline than a lookup discipline.

One competing data point shows the boundary clearly. A "token-discipline" skill measured −19.0% on codebase Q&A and −19.9% on multi-file edits, but −2.1% on a one-shot code trace, +0.0% on an audit sweep, and *+5.7%* — a loss — on a big-JSON digest. Discipline only pays where indiscipline is possible. If your workload is one-shot and lean, no token skill will save you anything, and several will cost you.

## Benjamin-Plus on the Measured-Premium Ledger

The most useful context for judging this skill is the same laboratory's earlier work. JetBrains runs a public paired-A/B series against third-party token savers, publishing what it measured against what was advertised.

| Skill | Advertised | Measured | Verdict |
|---|---|---|---|
| caveman | −65% output tokens | −8.5% output tokens, ~−10% cost at absolute best (p=0.82) | Oversold; safe and honest about style |
| rtk (Rust Token Killer) | 60–90% token reduction | **+7.6% cost increase** at low effort (p=0.004), flat at high effort | Made sessions more expensive |
| ponytail | −54% code, −20% cost | −15% code, −10.3% cost (p=0.004), −11% time | First statistically solid saving in the series |
| benjamin-plus | −18% cost, −22% tokens | −17.9% median cost (p=0.005), −16.7% totals | Advertised and measured agree |

Two lessons come out of that table. First, the category norm is that vendor numbers land at a quarter to a half of the advertised figure — caveman and rtk both did — so a claim that matches its measurement is genuinely unusual and worth noting. Second, the rtk case is a warning about dashboards: rtk's own UI reported 96.2 million tokens "saved," which was 99.8% of everything it touched, in the very run where the measured bill went up. Instruments that grade their own homework are not evidence.

The vendor motivation is also on the record, which makes the artifact easier to place. JetBrains' own AI development spend rose roughly 10x in the first half of 2026; most of its developers use between three and five AI tools in a given month; and the company hit 150 Claude Code seats and moved to an API-usage-based Enterprise plan — "that's when costs really took off." Benjamin-Plus is an in-house cost-control artifact from that program, which is a plausible reason it exists and a reason to expect it to be measured rather than marketed.

## Reading the Receipts Critically: What the Repository Does Not Ship

The strongest objection to this project is not about its numbers. It is that you cannot rerun them.

The README's "Reproducing" section names four scripts and two documents — `gen_instruction.py`, `compare.py`, `adoption.py`, `mediators.py`, `LAB-NOTES.md`, and `winning-strats.md` — and none of them are in the public repository. No evaluation code ships at all. What does ship is verifiable: SHA256SUMS.txt covers 8 files, and all four text files matched the manifest byte-exactly when checked on 2026-10-01.

| What it ships | What it does not |
|---|---|
| README, RULESET.md, injected-instruction.md, hook script, 3 assets, results doc | Any script that produced the results |
| SHA256SUMS.txt covering 8 files; all 4 text files verified byte-exact | LAB-NOTES.md and winning-strats.md referenced in "Reproducing" |
| A hook script that runs cleanly: 55 lines, exit 0, executable bit set as cloned | Eval harness, CI, releases, or a second contributor |
| Full paired results tables with p-values and program spend | A rerunnable path from raw trajectories to those tables |

A fresh clone is about 2.1 MB across 11 files outside `.git`. So the honest characterization is: the headline is trust in a carefully written document by one contributor with a 5-commit history, checked against a hash manifest, not a reproduction of an experiment you can execute. That is a real limitation and it is worth stating before, not after, you adopt the rules.

## The Living Ruleset: 17 Issues, Six Fixed Bugs, One Unmerged Fix

One more caveat that no review should omit: the file you inject in October is not the file that was benchmarked in August.

The repository drew 17 community issues and pull requests in its first three weeks. Merged PR #18 (2026-08-27) fixed six shell-semantics bugs in the rule examples:

| Issue | Bug fixed in PR #18 |
|---|---|
| #7 | Unquoted `echo` in zsh |
| #12 | `command -v` reports false success across multiple tools |
| #14 | `grep -m` is not global |
| #15 | Pipe limiters do not cap stderr |
| #16 | `wc -l` lies on minified files |
| #17 | `find_spec` raises on dotted module names |

Note the direction of travel: the payload grew from roughly 788 to about 899 tokens as a result of that merge. Bug fixes made the artifact bigger, which is a small cost against the correctness it bought — and a reminder that "efficiency never outranks correctness" is a rule the project actually follows rather than a slogan.

More importantly, the rule-semantics change from issue #4 — that "named verification can produce a false-green and premature stop" — was tested separately and **not** merged in PR #18. The semantics fix is still unshipped. If rule 4 is the rule you care most about, you are running the version with the known weakness.

The laboratory's own notes explain why the shipped configuration is this small, and it is the most portable lesson in the whole project: "quality guards are not free." Earlier versions added verification rigor and check-to-file rules, and each guard generated "verification whales" — large verification efforts that erased savings elsewhere. The winning configuration deleted more rules than it added. Anyone writing a token-efficiency skill should treat that as the central design constraint.

## How to Adopt Benjamin-Plus: Claude Code, Codex CLI, and Any Agent

Adoption takes about three minutes, and the only real decision is whether you inject the payload for every session or only some. Injection is the tested path, so start there.

**Claude Code.** Install the hook. The SessionStart hook uses the matcher `startup|resume|clear|compact` and cats `~/.benjamin-plus/injected-instruction.md` into context. The script ships in the repo as a 55-line shell file that runs cleanly as cloned. Re-injecting on `compact` matters: compaction is exactly when an agent forgets how to look things up.

**Per project instead of globally.** Append the payload to the project's `CLAUDE.md` with a single `cat ... >> CLAUDE.md`. This is the right move if you want the rules only on repositories with expensive sessions, and it avoids paying ~745 tokens on trivial work.

**Codex CLI.** Append to `~/.codex/AGENTS.md`. This is the same mechanism and the same cost; there is no Codex-specific packaging because there does not need to be.

**Any other agent.** Append the payload to the system prompt. Total integration cost is about 3 KB, and nothing in the rules depends on Claude Code internals.

Then do two things that cost nothing:

1. **Measure your own baseline before and after.** The published range is −10% to −18% depending on baseline bloat. If your sessions are already lean, expect the low end or nothing. Run ten comparable tasks, record cost and turns, inject, run ten more.
2. **Verify the payload actually reached the model.** The adoption check in the upstream evaluation was mechanical: 80/80 treated runs versus 0/80 controls. A skill that never reached the prompt is indistinguishable from a skill that does not work.

If you want a deeper protocol, you can run a paired A/B in a day: pick 80 paired tasks, apply Wilcoxon signed-rank to the per-pair deltas, and check adoption directly in the trajectory rather than trusting that the file was installed. That is the same method described above, and it is the only way to know whether the number applies to you.

## Who Should Skip Benjamin-Plus?

Skip it if any of these describe you, and skip it without guilt — the project's own documentation makes most of these arguments.

- **Your sessions are already lean.** Savings scale with baseline bloat. A disciplined team that batches commands, reads narrowly, and never polls in 1-second ticks has already captured the value; the payload adds ~745 tokens per session and near-zero savings.
- **You work in one-shot, single-lookup tasks.** A competing discipline skill measured a *+5.7% loss* on a big-JSON digest and a −2.1% gain on a one-shot trace. Rules cost tokens; where there is no waste to remove, the rules are the waste.
- **You need reproducible evidence before adopting tooling.** The eval code is not public. If your process requires rerunning a benchmark, this fails that gate, and no amount of well-formatted tables changes it.
- **You rely on rule 4's semantics as written.** The false-green fix from issue #4 is unmerged. Pin your expectations to the shipped version.
- **You need certainty about quality.** 80 pairs rule out large effects only. If your workload has expensive failure modes, measure quality yourself before trusting an unchanged-quality headline.
- **You install skills by discovery.** A skill folder for this payload measured −0.5% and not significant, because finding the file cost a median 3 steps with 73% path misses. Install it that way and you have paid for nothing.

## Verdict: Inject It, Measure It, and Do Not Believe the Category

Benjamin-Plus earns a recommendation for a specific job: making a bloated coding-agent session cheaper without changing what it builds. Three things make it unusually trustworthy for this category — the head-to-head delivery test that proved injection beats installation, the published honesty note about a non-significant earlier run, and the fact that the vendor applied its public benchmark method to its own product and reported a number matching its claim.

Three things should temper that: the evaluation code is not public, so the headline is trust in a document rather than a reproduction; quality was not proven equivalent, only shown not to move much at 80 pairs; and the ruleset is a living artifact whose semantics fix from issue #4 remains unmerged while its payload has already grown from fixes in PR #18.

The practical play is small and cheap. Inject the ~745-token payload via a SessionStart hook, append it to CLAUDE.md or AGENTS.md, confirm it actually reached the model, and measure your own before-and-after on ten comparable tasks. If you are already lean, the honest expected result is close to nothing — and knowing that in advance is the difference between adopting a measured tool and buying category hype one more time.

## Frequently Asked Questions

### Is benjamin-plus worth injecting?

Yes, if your coding-agent sessions show step waste — serial greps, repeated environment probes, or polling loops. Injected, it measured −17.9% median cost (p=0.005) on 80 paired SkillsBench tasks with quality unchanged. The catch is delivery: injected as a ~745-token payload it saves; installed as a discoverable skill folder it saved nothing (−0.5%, not significant) because agents burned a median 3 steps locating SKILL.md with 73% path misses.

### Does benjamin-plus actually reduce cost by 18%?

Not universally, and the repository says so itself. The honest range is −10% to −18% depending on how bloated your baseline sessions run; on Java SWE-bench with Codex CLI the same skill measured −4.4% (p=0.003). Savings scale with baseline bloat, so a 330-star repository's headline is a property of its baseline rather than a fixed discount you can budget.

### Can I install benjamin-plus as a normal agent skill?

You can, but it is the one delivery method that was measured not to work. The skill-folder arm came in at −0.5%, not significant, against −4.4% for hook injection on the same 675 paired Java SWE-bench replicas. The upstream stance is inject-only, and `npx skills add` against the repository fails to find a valid skill by design. Use the SessionStart hook, append to CLAUDE.md or AGENTS.md, or add it to your system prompt.

### Does benjamin-plus hurt code quality?

Nothing in the paired evaluation suggests large harm: quality outcomes were 7 better / 5 worse / 68 tie, sign test p=0.77, with mean verifier reward moving 0.362 → 0.392. But the document is explicit that 80 pairs is "not powered as an equivalence test" — it rules out large quality effects, not small ones. The payload also carries explicit guardrails, including that efficiency never outranks correctness, that keyhole reads apply to inspection and never to ingestion, and that the agent should never build a verification harness the task did not ask for.

### How does benjamin-plus compare with caveman, rtk, and ponytail?

They were benchmarked by the same laboratory with the same paired method, and the pattern is that advertised numbers land at a quarter to a half of measured ones. caveman advertised −65% output tokens and measured −8.5%; rtk advertised 60–90% token reduction and measured a +7.6% cost *increase* at low effort; ponytail advertised −54% code and −20% cost and measured −15% and −10.3%. Benjamin-Plus is the outlier where the advertised figure (−18% cost) and the measured figure (−17.9% median) agree, which is the strongest argument for taking its receipts seriously.
