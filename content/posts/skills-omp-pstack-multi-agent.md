---
title: "Best-of-N Coding Agents With LLM-as-a-Verifier in Oh My Pi"
date: 2026-10-01T06:53:02+00:00
tags:
  - best-of-n coding agents
  - llm-as-a-verifier
  - oh my pi best of n
  - omp-best-of plugin
  - verifier-selected patch
  - test-time scaling coding agent
  - best-of-n vs pass@1
  - probabilistic pivot tournament
  - sampled pairwise verifier
  - logprob verifier deepseek v4 flash
  - oracle@N ceiling
  - verifier-guided repair
  - best-of-n cost per task
  - git worktree isolation coding agent
  - how to pick the best agent patch
  - llm verifier vllm sglang logprobs
description: "Best-of-N coding agents run N candidates and let an LLM verifier pick the winner. How omp-best-of works, what it costs, and where it fails."
draft: false
cover:
  image: "/images/skills-omp-pstack-multi-agent.png"
  alt: "Best-of-N Coding Agents With LLM-as-a-Verifier in Oh My Pi"
schema: "schema-skills-omp-pstack-multi-agent"
---

Best-of-N coding agents run the same task N times in isolated workspaces, then use an LLM-as-a-verifier to score every full trajectory and select the winning patch. In Oh My Pi, the `omp-best-of` plugin does this with `/best-of --n 5 --apply "Fix the failing authentication test"`, defaulting to 3 candidates and selection-only mode.

That is the short answer. The rest of this guide is the part that decides whether the technique saves you money or burns it: what selection can and cannot fix, why the maintainers' own benchmark numbers are much smaller than the headline claims circulating about them, and how to choose N without paying for a fourth opinion nobody needed.

## What Does Best-of-N Actually Solve — and What Can't It?

The case for sampling is arithmetic, not intuition. If a single attempt succeeds with probability `p`, then the chance that at least one of `k` independent attempts succeeds is:

```
coverage = 1 - (1 - p)^k
```

At `p = 50%`, three attempts cover 87.5% of the outcomes and five attempts cover 96.9%. At `p = 25%`, three attempts only reach 57.8%. At `p = 10%`, you need twenty attempts to crawl to 87.8%. The math is unforgiving in exactly one direction: samples rescue tasks that are already roughly half-solvable, and do almost nothing for tasks the model cannot approach at all.

The strongest empirical demonstration remains the Large Language Monkeys result, which took a mid-tier open model from 15.9% on SWE-bench Lite with a single attempt to 56% with 250 attempts — above the 43% single-attempt state of the art at the time. That is horizontal scaling beating vertical scaling: more samples from a cheap model outrunning a bigger model used once.

But notice what that result does *not* say. It measures **oracle@N** — the fraction of tasks where *some* candidate in the pool was correct. It assumes a perfect selector that always picks the right one. Real deployments do not have that. Coverage is what N buys you; selection is a separate problem, and it is the harder one.

This distinction is where most best-of-N write-ups quietly cheat. A pool with 87.5% oracle@3 and a 50% accurate verifier does not deliver 87.5% of anything. This is why best-of-N with LLM-as-a-verifier is best understood as an architecture decision rather than a benchmark trick: you are not making the model smarter, you are buying a larger pool and then paying a second model to referee it. If the referee is bad, you have added cost and latency to random selection.

There is also a sharp edge on the other end. Best-of-N pays off in the **middle band**, where single-shot success is neither near zero nor near one. If your agent already solves a task 95% of the time, you are paying four extra attempts to be told what you already knew. If it solves it 5% of the time, you are buying lottery tickets. The regime that matters is the 30–70% band, and knowing which band you are in is a prerequisite, not an afterthought.

## How Does LLM-as-a-Verifier Score a Trajectory?

The upstream framework here is `llm-verifier` (Kwok et al., arXiv 2607.05391, MIT licensed, roughly 3.2k stars on GitHub), installable with `pip install llm-verifier` and exposing `select()`, `compare()` and token accounting.

What separates it from an ordinary LLM judge is granularity and how the score is read. A conventional judge asks a model for a rating and takes the argmax token. LLM-as-a-Verifier instead expects a model to produce a *distribution* over score tokens and computes the expectation over that full distribution. That single change is what converts a noisy ordinal judgment into a continuous score, which in turn makes paired comparisons stable enough to rank.

The framework's published self-verification table on Terminal-Bench 2.1, using DeepSeek V4 Flash for both generation and verification, is the cleanest illustration of the gap between coverage and selection:

| Configuration | Random selection | Verifier-selected | Oracle |
|---|---|---|---|
| Best-of-3 | 79.4% | 86.5% | 92.1% |
| Best-of-5 | 78.7% | 88.0% | 96.6% |

Read the columns in order. Verifier selection recovers a real chunk of the distance between random and oracle — about 7 points at N=3 — but it does not close it. At N=5 the oracle ceiling is 96.6% and the verifier delivers 88.0%. That 8.6-point gap is the price of an imperfect judge, and it is the number that should anchor your expectations rather than the oracle figure.

Three scaling levers follow from that design: finer scoring granularity, scaling the number of repeated evaluations, and decomposing one holistic verdict into several narrow criteria. The upstream project reports cross-benchmark results of 86.5% on Terminal-Bench V2 (GPT-5.5, best-of-5), 78.2% on SWE-Bench Verified (best-of-3), 87.4% on RoboRewardBench and 73.3% on MedAgentBench (best-of-5).

The framework also requires a backend that returns token logprobs — DeepSeek, vLLM or SGLang, or any OpenAI-compatible server that honors the constraint. That requirement is not incidental; it is the whole reason the `logprob` backend in `omp-best-of` has installation prerequisites that the `sampled` backend does not.

Version 0.2.0 added a prefix-cache optimization that cuts uncached input tokens by roughly 3.4x on trajectory-heavy benchmarks. That is the fix aimed squarely at the cost problem described later, because verifying a long agent trajectory means re-reading the entire thing.

## How Do You Install omp-best-of in Oh My Pi?

`omp-best-of` (wolfiesch/omp-best-of) is an MIT-licensed Oh My Pi plugin — around 70 stars, 53 commits, last pushed 2026-09-02. It runs N headless OMP candidate sessions in isolated copy-on-write workspaces and ranks full trajectories rather than just final diffs.

Requirements are specific and worth reading before you install:

- **Oh My Pi 17+** (can1357/oh-my-pi, roughly 33.9k stars, shipping daily)
- **Bun 1.3+**
- **Git** — the isolation mechanism depends on it
- **`uv`** — only for the `logprob` backend, which runs a pinned `llm-verifier==0.2.0` sidecar
- A **verifier route configured in omp** — the plugin does not invent one for you

One operational constraint deserves emphasis because it is a hard gate rather than a warning: **a clean working tree is enforced before any candidate starts.** Uncommitted changes stop the run. That is the correct design — the plugin cannot reason about patches against a dirty baseline — but it means the tool is not something you reach for in the middle of a debugging session with three half-edited files open.

## What Does Your First Run Look Like, from /best-of to an Applied Patch?

The command surface is deliberately small, which is a virtue worth crediting. In-session:

```bash
/best-of --n 5 --apply Fix the failing authentication test
```

Standalone, writing a JSON summary to stdout:

```bash
omp-best-of --n 3 --apply -- "Fix the failing authentication test"
```

Defaults matter more than the flags here. `--n` defaults to **3**. The default verifier is **deepseek/deepseek-v4-flash**. And `--apply` is **off** by default, which means the tool selects a winner and tells you about it without touching your branch. That default is the right one: you want to read the verifier's reasoning on a few real tasks before you let it mutate a working tree.

Two behaviours are worth knowing before the first run:

1. A candidate that **exits non-zero**, or whose patch **cannot be captured**, is excluded before ranking. It never competes.
2. Both backends score candidates against the same three criteria: **Requirements**, **Correctness**, and **Verification**. Holding the rubric constant across backends is what makes the two comparable at all — a detail competitors often blur.

Practically, run selection-only for a week. Compare the verifier's pick against the pick you would have made. If they agree most of the time, `--apply` is safe. If they don't, you have learned something valuable at zero risk.

## Which Verifier Backend Should You Pick: logprob or sampled?

This is the decision that determines your infrastructure bill, and the distinction is architectural rather than cosmetic.

| | `logprob` backend | `sampled` backend |
|---|---|---|
| Mechanism | Continuous-score pivot tournament | 2 sandboxed candidate audits + seeded all-pairs judge |
| Requires | Endpoint returning score-token distributions; honors constrained prefill | A subscription model route, e.g. `openai-codex/gpt-5.6-luna` |
| Infra | `uv` + pinned `llm-verifier==0.2.0` sidecar; vLLM/SGLang eligible | No API credits or local GPU required |
| Fidelity to the paper | Upstream continuous-score method | Conventional pairwise judge — **not** the paper's method |

Pick by what your credentials can actually prove. If you have a DeepSeek key or your own vLLM or SGLang endpoint, `logprob` gives you the method the paper describes. If you are on a subscription coding plan with no API credits, `sampled` is the only door open to you — and that is fine, as long as you do not call it something it isn't.

The maintainers make this explicit, and their wording is worth quoting verbatim because a lot of secondary coverage drops it: *"the sampled backend is a separate conventional pairwise judge, not the paper's continuous-score method"*, and *"this plugin has not established equivalent reliability"*. Anyone presenting `sampled` results as a reproduction of the published method is misreading the README.

## What Do the Maintainers' Own Benchmarks Really Show?

This is the section most guides omit, and it is the most useful one.

The plugin's own `bench/RESULTS.md` and README report two results that still stand, against baseline comparisons the maintainers constructed themselves:

- **`logprob 1` evaluation: 5/10 (50.0%) selections correct** against a *62.5% random pass@1 baseline*. The verifier underperformed random selection on two reused tasks.
- **`sampled` Luna, 1 round: 13/15 (86.7%)** against a 32.0% random baseline across five reused discriminating pools (ancestor commit `06eefab`).

A 50% selection accuracy on the first configuration is not a rounding error. It is the honest, unflattering number, and the maintainers published it.

Two earlier headlines — **83.3% and 72.2%** — were **withdrawn** because two pools (content-type, http-range) had defective oracles and, once the oracles were corrected, no candidate passed. The apparent successes had been measuring a broken test.

Three findings from the same file matter more than either headline:

**Score separation collapses on saturated pools.** Where the task was easy enough that candidates were mostly equivalent, the verifier's score spread fell to **0.000–0.006**. Nearly every comparison was a tie, which means the reported winner was effectively decided by a tie-break rule, not by verification. Re-ranking one pool three times with identical settings and the same seed produced picks #2, #4, #2 — that is not a stable selector, that is a coin with extra steps.

**Repeated evaluation is not free accuracy.** On the single pool with genuine separation (0.061), the verifier ranked a *failing* candidate first at both 1 and 3 evaluations per criterion. Tripling the evaluation count tripled the cost and changed nothing.

**Saturation and discrimination pull in opposite directions.** To measure selection accuracy you need pools with headroom *and* trajectories containing validation evidence. Visible tests supply the second and destroy the first. The maintainers' conclusion — harden the hidden contract instead of deleting the visible tests — is the right lesson for anyone building a benchmark, and it applies well beyond this plugin.

The generalizable principle: **before you trust any selector, measure the spread on your own pool.** If your candidates are scoring 0.000–0.006 apart, your verifier is not selecting, it is guessing.

## What Does Best-of-N Cost, and How Do You Choose N?

Verification is not a rounding error in the bill. In the plugin's early live runs, verification accounted for **25–51% of total cost**, because the verifier reads long trajectories and its output and reasoning tokens dominate. In one measured run (`run C retry-transient`), **147,533 of 153,547 output tokens were reasoning**. You are paying for a model to think carefully about work it did not do.

The sampled backend's invocation count is a closed-form cost model:

```
invocations = 2N + E * N(N-1)/2
```

for N candidates and E evaluations per criterion. Four candidates at one evaluation is 14 invocations; eight candidates is 44. The quadratic term is why raising N is not a linear purchase.

Measured wall-clock and money on small fixtures: roughly **$0.0084–$0.0119 per candidate run**, i.e. **$0.04–$0.05 for a four-candidate pool** and **$0.05–$0.08 including verification**. One four-candidate task took **95s to 693s** end to end.

For comparison at production scale, coding agents on SWE-bench Verified cost roughly **$0.35–$0.75 per instance per attempt**, making best-of-5 **$1.75–$3.75** and best-of-10 **$3.50–$7.50**. Against a loaded developer hour around $150, that is still cheap — but only if the selection is better than choosing at random.

**Latency, not money, is the real wall.** Candidates run concurrently within a task, but tasks run sequentially, so wall clock is dominated by the slowest candidate plus the judge pass rather than the sum of all candidates. Latency is max-of-N, not sum-of-N, and shared prompt prefixes are usually billed once, so the marginal attempt costs less than it looks. The 95s–693s range per four-candidate task is the number that decides whether best-of-N belongs in CI or in a nightly job. Task-level parallelism is the obvious missing optimization.

How to choose N, practically:

1. **Estimate `p` first.** Run the task once, ten times, and count. If `p` is above 0.8, best-of-N is waste. If it is below 0.2, samples will not save you.
2. **Start at N=3**, the default. It captures most of the coverage jump from a 50% base (87.5%) at a quarter of the verification bill of N=5.
3. **Go to N=5 only when you have measured that the spread is real** — that candidates land in distinguishable score bands.
4. **Stop at N=5 unless the task is high-value.** Returns diminish sharply past N=10 while the quadratic judge term keeps growing.
5. **Use adaptive N by estimated difficulty**, and **early-exit the moment a candidate passes your tests.** OpenHands measured early stopping averaging only **1.35 attempts** while adding **+17.7 points over random** — the single best cost-control pattern available.

## Where Does Best-of-N Fail, and When Should You Not Use It?

Four failure modes are documented well enough to plan around.

**The verifier saturates on convincing-but-wrong self-reports.** The named example is a failing run that claimed *"4102 entries, zero mismatches"* when the correct answer was 698. A model writing a confident summary of its own success is not evidence, and a verifier reading that summary can be fooled. **Pure code diffs are the clean signal; terminal self-reports are not.** Treat any verifier that reads self-reported success as structurally compromised.

**Plausible code can outrank correct code.** A patch that looks idiomatic and passes the visible tests can beat a correct patch that missed an unobserved contract edge case. This is the flip side of the saturation problem: visible validation evidence makes a candidate *look* verified to the judge.

**Benchmark-trained critics do not transfer.** OpenHands measured critics trained only on benchmark traces at **AUC 0.45–0.48 on production outcomes — worse than random** — versus **0.69** when trained with code-survival supervision. A verifier that looked fine in evaluation can be actively harmful in production. The same source shows a well-trained critic moving Best@8 to **73.8% vs 57.9% random@8**, so the ceiling is high but the floor is below chance.

**Planning-first best-of-N is a measured dead end.** Drafting N plans, selecting one, then executing once changed **0 of 5 outcomes** on Terminal-Bench at **3–10x the cost**. Whatever problem best-of-N solves, it is not plan quality.

On safety, the framing that matters most is that **isolation is not a sandbox**. The copy-on-write workspaces prevent patch *collisions* — two candidates cannot stomp each other's changes. They do not constrain what a candidate can do. Candidates run headless in yolo approval mode with host filesystem and network access. Treat them exactly as you would any unsandboxed subprocess: no production credentials in the environment, no write access to anything that matters, and a container boundary if you can arrange one.

Do not use best-of-N when:

- The task is already reliably solved (you are buying tie-breaks).
- The task is effectively unsolvable by the model (no amount of sampling helps at low `p`).
- The bottleneck is **planning**, not execution.
- Your verification budget is capped below a full trajectory read — a truncated verifier is a worse selector than a coin.

## How Do You Get Past the oracle@N Ceiling? Repair and Alternatives

The sharpest framing in this whole space is that **selection can never beat oracle@N**. Best-of-N selects from a pool; it cannot invent a candidate the pool never contained. This means the marginal value of another point of selection accuracy is bounded by the pool, while the marginal value of *improving the winning candidate* is not.

`agent-ultramode` (maverick-tr/agent-ultramode) is the competing implementation that acts on this. It runs the task N times in isolated git worktrees for opencode, Claude Code and Grok, and uses the **same model** as the verifier — no cross-model dependency. Its v2 adds **verifier-guided repair on the winner**, kept only if it verifies better, reaching **91.7% on a 24-task SWE-bench Lite slice against its own 87.5% oracle@5 ceiling** by rescuing two tasks no attempt had solved. That is the ceiling being broken rather than approached.

The same project reports **90.4% on the Terminal-Bench 2.1 coding subset (77 tasks)** with a small non-vision flash model at best-of-5, against 89.5% / 89.1% / 88.4% pass@1 for GPT-5.6 Sol / Claude Opus 5 / Grok 4.6 — and frames it honestly as reaching that tier at a fraction of the cost, not as a like-for-like win. Its blended figure is 78.7% base to 87.6%, a **+8.9 point lift**.

A parallel line of work attacks the same problem by changing what gets compared. arXiv 2604.16529 observes that long-horizon coding agents "violate the premise" that outputs can be directly compared, ranked or refined, and that the real challenge is *representing prior experience* rather than generating more attempts. Converting each rollout into a structured summary that preserves hypotheses, progress and failure modes — then scaling it via Recursive Tournament Voting (parallel) or Parallel-Distill-Refine (sequential) — moved Claude-4.5-Opus from **70.9% to 77.6%** on SWE-Bench Verified and **46.9% to 59.1%** on Terminal-Bench v2.0. That compression step is what makes ranking long trajectories tractable at all.

Selector engineering, consolidated from the practitioner literature:

- **Randomize candidate order and evaluate both orders.** Position bias is real; evaluating only one order bakes it in.
- **Strip length cues.** Longer is not better, but judges consistently think it is.
- **Use a judge from a different model family** than the generator. Self-preference is measurable.
- **Prefer pairwise tournaments** (N-1 comparisons) over absolute 1–10 scores. Absolute scales drift; comparisons are local and stable.
- **Decompose the verdict into narrow aspect verifiers** rather than one holistic judgment — this is what the three-criteria rubric is doing.
- **Calibrate against a labeled gold set** before trusting the selector on anything that matters.

A useful multi-signal rubric weighting, if you are building your own: test pass rate 0.35, regression tests 0.35, diff size, linter and type checker for the remainder.

## What Is a Repeatable Best-of-N Workflow?

1. **Confirm a clean working tree.** The plugin enforces this; do not fight it.
2. **Estimate `p` on the task class** with a handful of single runs. If it is outside the 0.2–0.8 band, stop here.
3. **Run selection-only** (`--apply` off, the default) at N=3.
4. **Inspect the score spread, not just the winner.** Spread under ~0.01 means the pool is saturated and the pick is a tie-break. Fix the task's discriminative power before adding candidates.
5. **Check the pick against your own judgment.** If the verifier disagrees with you, read its reasoning before blaming it — sometimes the unobserved contract edge case is real.
6. **Promote to N=5 and `--apply`** only once selection looks better than your own coin flip.
7. **Add early exit** as soon as a candidate passes your tests. This is the largest available saving.
8. **Read diffs, not self-reports.** Never let terminal output claiming success count as verification evidence.
9. **Sandbox the candidates.** Isolated workspaces are not a security boundary.
10. **Re-measure monthly.** Both the models and the oracles drift; a selector that worked in September is not verified in December.

## FAQ

**What are best-of-N coding agents in one sentence?**
They run the same coding task N times in parallel isolated workspaces and use a verifier model to score each full trajectory and select the winning patch, trading compute for a higher success rate than a single attempt.

**Does best-of-N with LLM-as-a-verifier actually work?**
Partially, and the honest numbers are modest. Upstream reports verifier selection at 86.5% (best-of-3) and 88.0% (best-of-5) against oracles of 92.1% and 96.6% on Terminal-Bench 2.1. The `omp-best-of` plugin's own standing result on its `logprob` backend was 5/10 correct selections against a 62.5% random baseline — the maintainers published that unflattering number themselves.

**What is the difference between the logprob and sampled backends?**
`logprob` runs the upstream continuous-score pivot tournament and needs an endpoint that returns score-token logprobs (DeepSeek, vLLM, SGLang). `sampled` runs a conventional pairwise judge with 2 sandboxed audits plus a seeded all-pairs comparison, and works on subscription model routes with no API credits. The maintainers state explicitly that `sampled` is not the paper's method and has not established equivalent reliability.

**How much does best-of-N cost per task?**
On small fixtures, roughly $0.0084–$0.0119 per candidate, about $0.04–$0.05 for a four-candidate pool and $0.05–$0.08 including verification, with 95s–693s wall clock. Verification alone was 25–51% of live-run cost because the verifier reasons over long trajectories. At production scale, SWE-bench Verified instances run $0.35–$0.75 per attempt, so best-of-5 is $1.75–$3.75.

**What is the oracle@N ceiling and why does it matter?**
Oracle@N is the fraction of tasks where at least one candidate in the pool was correct — the theoretical maximum any selector could achieve. Because selection can never beat it, the useful question is not how to select better but how to improve the winner: verifier-guided repair reached 91.7% on a 24-task SWE-bench Lite slice against its own 87.5% oracle@5 ceiling.
