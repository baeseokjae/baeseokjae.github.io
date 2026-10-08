---
title: "Best of N Agent Verifier: How to Pick the Coding Agent Run That Actually Solved the Task"
date: 2026-10-01T10:46:43+00:00
tags:
  - "best of n agent verifier"
  - "best-of-n coding agent"
  - "LLM as a verifier"
  - "verifier ranked trajectories"
  - "test-time scaling coding agents"
  - "probabilistic pivot tournament"
  - "pass@k vs selected accuracy"
  - "logprob scoring verifier"
  - "git worktree parallel coding agents"
  - "reward hacking verifier"
  - "unit test based code selection"
  - "code agent candidate selection"
description: "A practical guide to best-of-n coding agents with an LLM-as-verifier: logprob scoring, pivot tournaments, worktree isolation, and choosing N."
draft: false
cover:
  image: "/images/best-of-n-coding-agents-with-llm-as-verifier.png"
  alt: "Best of N Agent Verifier: How to Pick the Coding Agent Run That Actually Solved the Task"
  relative: false
schema: "schema-best-of-n-coding-agents-with-llm-as-verifier"
---

Run N isolated candidate agents in separate git worktrees, capture each trajectory and patch, then rank them with a verifier that returns a continuous logprob score rather than a discrete grade. Terminal-Bench V2 went from 83.1% Pass@1 to 86.5% verifier-selected against a 92.1% oracle — the model had already solved it; selection was the bottleneck.

That gap between what the model *can* do and what you can *identify* is the entire subject of this guide. The rest of it covers why a plain LLM judge silently fails, how to turn a 20-token score distribution into a calibrated reward, how to rank 8 candidates without paying for 28 pairwise comparisons, what worktrees do not isolate, how many samples are actually worth paying for, and where optimistic best-of-N claims collapse under measurement noise.

## What Does Best-of-N With a Verifier Actually Buy You?

Best-of-N generates multiple independent attempts at one task and uses an external scoring function to choose among them. In an agentic setting the "attempt" is a whole trajectory — a sequence of tool calls, file reads, edits, and shell commands — not a single completion. The candidate is the final patch, but the thing you usually verify is the trajectory that produced it.

The purchase is not a smarter model. It is the ability to spend inference compute on *identification* instead of *generation*. That distinction only pays off when three conditions hold, and it is worth stating them plainly because most best-of-N disappointments are one of these failing:

1. **There is real coverage.** The correct solution exists somewhere in the N candidates. If pass@N is 40%, no selector on earth gets you to 90%.
2. **There is a trustworthy signal.** Unit tests, an oracle, a reward model, or an LLM verifier that correlates with task success better than random.
3. **The candidate pool is genuinely diverse.** N copies of the same failing approach is one candidate billed N times.

When all three hold, best-of-N is one of the few test-time scaling techniques with a measurable payoff on real coding tasks rather than only on math benchmarks. When any one fails, you have built an expensive random number generator.

## Coverage vs Precision: The Two Numbers That Decide Everything

Before you tune a verifier, measure two things. They are cheap to compute and they determine whether the whole approach is viable.

**Coverage (pass@N)** is the oracle: what fraction of tasks have *at least one* correct candidate in the pool. It is computable in a harness (you can run the hidden tests on every candidate) and not computable in production (if you had the tests, you would not need a verifier).

**Selected accuracy (best@N)** is what your verifier actually delivers: the fraction of tasks where the chosen candidate is correct.

The ratio between them is your verification headroom. Three published examples frame the scale:

| Setting | Pass@1 (single attempt) | Verifier-selected | Oracle bound | Headroom remaining |
|---|---|---|---|---|
| Terminal-Bench V2 (GPT-5.5, Best-of-5) | 83.1% | 86.5% | 92.1% (Pass@5) | 5.6 pts |
| Terminal-Bench V2, oracle (trajectories pooled across the leaderboard) | — | — | 98.9% | 12.4 pts vs selected |
| SWE-Bench Verified (Opus 4.5 / Gemini 3 Flash / MiniMax M2.5, Bo3, one trajectory each) | 76.1% | 78.2% | 84.4% | 6.2 pts |
| HumanEval (Codex, sampling only) | 28.8% | — | 70.2% (pass@100) | selection is the whole problem |

Source: Kwok et al., *LLM-as-a-Verifier* (arXiv:2607.05391) and its GitHub README tables; Codex numbers from *Evaluating Large Language Models Trained on Code* (arXiv:2107.03374).

Read those columns carefully, because they contain the most misquoted number in this field. Terminal-Bench V2 reaches 98.9% when an oracle picks from trajectories pooled across the full benchmark leaderboard. A verifier-selected Best-of-5 reaches 86.5%. The 12.4-point gap to that pooled oracle is not a model capability deficit — the same model generated a correct solution in most of those pools. It is a *selection* deficit, and it is the honest measure of how much the verification layer is leaving on the table in 2026.

The second lesson is that coverage grows fast while selection grows slowly. Repeated sampling took DeepSeek-Coder-V2-Instruct from 15.9% of SWE-bench Lite issues solved at one sample to 56% at 250 samples — above the 43% single-sample state of the art at the time — while majority voting and reward-model selection plateau beyond a few hundred samples in domains with no automatic verifier (Brown et al., *Large Language Monkeys*, arXiv:2407.21787). Coverage scales roughly log-linearly across four orders of magnitude. Selection does not scale at all unless you invest in the verifier.

If you only remember one diagnostic from this article: **when best-of-N underperforms, plot pass@N against best@N.** Rising coverage with flat selected accuracy means your generator is fine and your verifier is the bottleneck. Flat coverage means you have a generation problem and no amount of judging will fix it.

## How Many Samples Should You Actually Buy?

N is a budget line, not a virtue. Four separate effects push in different directions.

**The oracle curve is concave and easy to compute.** pass@N = 1 − (1 − p)^N. At p = 0.1, N = 10 gives you 65% and N = 20 gives you 88%. At p = 0.25, N = 10 already gives 94.4%. The marginal value of one more sample is Δ_N = p(1 − p)^(N−1) — it decays exponentially. Whatever N you pick, the N-th sample is worth far less than the first.

**Measured gains on real tasks flatten early.** With a self-verifier (the same model both generating and verifying), Terminal-Bench 2.1 moved from 79.4% Pass@1 to 86.5% ± 1.1% at Best-of-3 and to 88.0% ± 0.6% at Best-of-5, against oracle bounds of 92.1% and 96.6%. Two extra samples bought 1.5 points. Source: *LLM-as-a-Verifier* self-verification section.

**Optimization pressure grows sublinearly but inexorably.** Best-of-N pushes the policy away from its base distribution; the KL divergence from the base policy in nats is 0.1931 at N = 2, 0.6363 at N = 4, 1.2044 at N = 8, 1.8351 at N = 16 and 3.1745 at N = 64 (Gao, Schulman & Hilton, *Scaling Laws for Reward Model Overoptimization*, arXiv:2210.10760). Best-of-64 buys barely three nats of divergence over the base policy. That is the whole budget available for reward hacking to exploit.

**Verification cost grows faster than generation cost if you are naive.** Ranking N candidates pairwise needs up to N(N−1)/2 comparisons. Rank 8 candidates the obvious way and you pay 28 verifier calls for 8 generations.

The practical answer for coding agents in 2026 is **3 to 5 candidates for most work**, with 8 as a reasonable upper bound for high-value, low-frequency changes, and 16 only when you have already removed the O(N²) ranking cost and are pruning candidates cheaply before scoring. CodeMonkeys sampled ten full agent trajectories per issue against SWE-bench Verified and resolved 57.4% of issues for roughly $2,300 of compute, selecting with model-generated-test voting plus a final multi-turn selection trajectory (arXiv:2501.14723) — real, but that is a research-scale budget, not a CI budget.

### How Do You Budget Cost and Latency for Parallel Attempts?

The arithmetic that surprises people is the wall clock. Parallel attempts do not add latency; they add cost.

- **Wall clock** ≈ max-of-N attempt time + verification time, not sum-of-N. If your attempts take 4 minutes each and your verifier takes 40 seconds, Best-of-5 costs you about 4:40 of latency and 5× the tokens.
- **Prefix caching** makes attempts 2..N substantially cheaper on input tokens, since the system prompt, repo context and task description are shared. The incremental cost of an extra sample is largely output tokens.
- **Dollar envelope**: the only fully published accounting at SWE-bench-Verified scale is CodeMonkeys' $2,300 for the complete run — ten candidate trajectories per issue plus context selection and test generation, i.e. single-digit dollars per issue. Per-attempt figures quoted elsewhere are order-of-magnitude planning numbers, not vendor quotes; they move with model choice and repo size.

Three savings stack on top of that, and all three are additive rather than alternative:

| Technique | What it saves | Reported effect |
|---|---|---|
| Cascading with early stopping | Compute at equal quality | Up to 44% less compute; saving paid for in latency |
| Staged verification (cheap outcome model prunes before full test runs) | Verification throughput | 11.64× throughput at 8.26% accuracy cost |
| Token-free filtering (LatentSift policy-state filtering at K=16) | Verifier tokens | 49.1–62.1% total verification tokens cut; hybrid Best@16 held or improved (59.26% → 60.06%) |

Sources: AI21, *Improving Best-of-N with Budget-Aware Execution for SWE Agents*; *Pareto Optimal Code Generation* (arXiv:2506.10056); *LatentSift* (arXiv:2609.36371).

Note the shape of the AI21 result: parallel launch with early stopping is reported to strictly dominate launch-all-and-wait for latency, at the cost of giving back some of the compute saving. Cascading and parallelism are in tension; pick which one you are buying.

## The Scoring Ladder: Four Verifier Families Ranked by Trust

Verifiers are not interchangeable. They differ in how strongly they correlate with ground truth and how expensive they are to falsify.

**1. Deterministic checkers — compilers, linters, type checkers, formatters.** Nearly free, zero false positives on what they do cover, and almost no coverage of semantic correctness. Use them as hard filters, never as rankers. A patch that does not compile should never reach an expensive scorer.

**2. Execution-based verification — the repository's own unit and integration tests.** The strongest practical signal because tests are what the task actually demands. Self-consistency (majority voting) gave +17.9 points on GSM8K, +11.0 on SVAMP and +12.2 on AQuA over plain chain-of-thought, but it only applies when a discrete extractable final answer exists — which is exactly why it does not transfer to code patches (Wang et al., arXiv:2203.11171). Tests do transfer.

The catch is coverage and gameability. Benchmark tests systematically overstate how close selection is to truth: EvalPlus-style test augmentation caught previously accepted wrong code and lowered reported pass rates (arXiv:2305.01210). And tests are the most hackable signal you can hand an optimizer — see the reward-hacking section below.

**3. Learned reward models — outcome reward models (ORMs) and process reward models (PRMs).** ORMs score a finished solution; PRMs score each reasoning step. PRMs generalize across domains better than people expect: PRMs trained on math datasets perform comparably to code-specific PRMs for code test-time scaling (arXiv:2506.00027), and Math-Shepherd aggregates step scores by taking the minimum, so a single bad step sinks the trajectory (Wang et al., arXiv:2312.08935, following Lightman et al., arXiv:2305.20050). These are learned proxies, and every learned proxy carries a Goodhart risk.

**4. LLM-as-a-judge and LLM-as-a-verifier.** The judge reads the candidate and emits a verdict. This is the family where implementation details decide whether you get a real signal or coin-flip noise — which is the next section, and the most important part of this article.

Two orthogonal axes are worth knowing about. **Generative verifiers** (GenRM) reframe reward modelling as next-token prediction and beat discriminative verifiers and standard LLM-as-judge under Best-of-N: 73% → 93.4% on GSM8K, 5% → 45.3% on algorithmic tasks, 28% → 44.6% on MATH easy-to-hard generalization (Zhang et al., ICLR 2025, OpenReview Ccwp4tFEtE). **Multi-agent verification** adds an independent axis by combining binary approvals from M aspect-specific verifiers rather than only scaling the sample count (arXiv:2502.20379).

## Why a Discrete LLM Judge Quietly Stalls

Here is the mechanism almost nobody explains, and it is the highest-leverage paragraph in this guide.

Ask a model to score a patch from 1 to 10 and you get an integer. Ten possible outputs for a space of thousands of meaningfully different trajectories. Two candidates that differ substantially — one that fixed the bug with a clean test-driven change and one that special-cased the test input — routinely land on the same integer. In Terminal-Bench measurements, ties occurred in **26.7% of comparisons at the lowest evaluation budget**. A third of your ranking decisions were resolved by whatever tie-break your code happened to use.

The fix is not a better prompt. It is reading the wrong part of the output. Instead of taking the argmax token, take the **expectation over the probability distribution across the ordered score tokens**:

score = Σ (i × p_i)  over i in {1..20}

That single change converts a coarse verdict into a calibrated continuous score and eliminates ties entirely, because two candidates almost never share an identical probability distribution over 20 score tokens.

The measured result is stark:

- **Discrete judge at K=16 repeated evaluations: 79.1%.** Continuous logprob scoring at K=1: **80.1%.** Continuous scoring with a *single* evaluation beat a discrete judge with sixteen — 16× fewer model calls for better accuracy.
- Continuous scoring at K=16 reaches 81.2% against 79.1% for the discrete judge at the same budget.
- The same verifier is applied unchanged across SWE-Bench Verified and MedAgentBench-style mixed-domain pools.

The operational constraint is upstream of the prompt: **the verifier endpoint must return token-level logprobs over the score tokens**. In the paper's scaling experiments the verifier is Gemini 2.5 Flash precisely because it allows extraction of up to 20 top logprobs per scoring token; without logprobs you cannot compute the expectation and you are back to a discrete judge. The paper's own case study shows why that matters: on the `query-optimize` task Gemini 2.5 Flash reliably identifies the failure mode, but expresses it in graded, hedged language ("slightly cleaner," "marginally more direct") — and a discrete 1–5 judge collapses those assessments into the same integer in 88 of 100 repeated evaluations. A verifier can be perceptive and still useless if its output is compressed to an integer.

The practical consequence: when you evaluate verifier backends for a best-of-N pipeline, test for **constrained score-token prefill** before anything else. A verifier that cannot emit a probability distribution over its score tokens is not an LLM-as-verifier, it is an LLM-as-a-judge with extra latency.

## Three Verification Scaling Axes You Can Tune Independently

Verification is not a single knob you set to "on." It has three independent axes, each with measured headroom. This is the framing that separates a working pipeline from a demo.

| Axis | Change | Measured lift |
|---|---|---|
| Granularity (G) | More score levels, G = 1 → 20 | Pairwise accuracy 73.1% → 77.5% |
| Repeated evaluation (K) | More verifier passes per pair, K = 1 → 16 | Pairwise accuracy 74.7% → 77.5% |
| Criteria decomposition (C) | One broad criterion → three narrow ones | 75.2–76.4% → 78.3% |

Source: Kwok et al., arXiv:2607.05391, Figure 4. Reproduce the underlying tables before quoting exact figures in high-stakes material.

Two observations matter more than the numbers themselves.

**Granularity is nearly free; repetition is not.** Going from a binary pass/fail to a 20-level score costs you prompt tokens and nothing else, and buys 4.4 points of pairwise accuracy. Going from K=1 to K=16 costs 16× the verifier calls and buys 2.8 points. Spend on granularity first, always.

**Criteria decomposition beats a bigger model.** Three narrow criteria outperform one broad criterion, with the mechanism described as boosting weak learners: the same source measures 75.2–76.4% pairwise accuracy for any single criterion against 78.3% when the three are ensembled. The Qwen *Verification Horizon* paper measured the same effect in an agentic setting: an autonomous evaluator agent decomposing specs into checklists improved Best-of-N accuracy from 57.9% to 67.4% over four rubric iterations (arXiv:2606.26300). Crucially, **a fifth, over-specified version degraded performance.** Rubric granularity has a sweet spot. More criteria is not monotonically better; criteria that restate each other just add noise and tokens.

The decomposition that works in practice separates *what* was asked for from *how* it was done: (a) does the change satisfy the stated requirement, (b) does it avoid breaking existing behavior, (c) is the implementation approach one a reviewer would accept. Note that (c) is where trajectory-level evidence belongs.

## Ranking N Candidates Without Paying O(N²): Pivot Tournaments

Eight candidates scored absolutely, then sorted, sounds free. It is not, in the general case, because absolute LLM scores are weakly calibrated across candidates — models are systematically biased by presentation order, response length, and formatting. Pairwise comparison is far more reliable ("which of these two better satisfies criterion 1?"), but pairwise comparison across N candidates naively costs N(N−1)/2 verifier calls.

For 8 candidates that is 28 comparisons to rank 8 artifacts. For 20 candidates it is 190. This is the real reason people quietly cap N at 3.

**Probabilistic Pivot Tournament (PPT)** breaks that coupling. Instead of a full round-robin, pick pivots probabilistically and compare each candidate against a small number of them, reducing ranking cost from O(N²) to **O(N·k)**. The measured trade for a 20-candidate pool: 13,111 round-robin comparisons versus 9,630 at k = 9 — **27% fewer comparisons for 0.3 points of accuracy** (67.42% → 67.13%). Source: Kwok et al., arXiv:2607.05391, PPT section.

A 0.3-point accuracy cost to remove a quarter of the verifier bill is a trade most production pipelines should take, because verifier calls are the dominant cost once N exceeds about 5.

Three companion techniques round out the ranking layer:

- **Staged verification**: run a cheap outcome reward model over all candidates, keep the top few, and only then run expensive full test suites or high-K verification on the survivors. Reported 11.64× throughput at 8.26% accuracy cost.
- **Agentic verifiers**: instead of scoring the candidate as given, actively search for inputs that discriminate between candidates. Reported up to +10–15% absolute Best@k accuracy across five competitive-programming benchmarks (arXiv:2602.04254). This is the strongest of the "spend verification compute intelligently" findings, because discriminating inputs attack the actual failure mode — candidates that look equivalent under easy tests.
- **Recursive Tournament Voting**: for agentic coding specifically, compact rollout summaries plus tournament voting over those summaries beats naive selection (arXiv:2604.16529). Trajectories are long; you cannot feed five full transcripts into one judge call cheaply, so summarize each before comparing.

## Verification Hygiene: Most of the Win Is Here

Before you upgrade models or raise N, fix these. Each is cheap, and each is a known source of verifier error.

- **Randomize candidate order.** Position bias in LLM judges is large and directional. If candidate A is always presented first in your harness, you are partially measuring presentation order.
- **Strip length and formatting cues.** Verbosity biases LLM judges upward. A 400-line diff that touches everything looks more thorough than a 12-line fix and usually is not.
- **Use a judge from a different model family than the generator.** Same-family judges share the generator's blind spots. Self-verification works (measured, above), but cross-family verification works better when you can afford it.
- **Prefer pairwise over absolute scores**, then aggregate. Absolute scores cluster; comparisons discriminate.
- **Decompose into narrow binary criteria.** Three narrow questions beat one broad one, up to a point.
- **Calibrate on ~100 labeled cases before trusting the verifier.** You want the verifier's ordering, not its absolute scale. Report rank correlation against ground truth on your own repo. A verifier that is uncalibrated on your task distribution is a random tie-breaker.
- **Never present the candidate's own claim about what it did as evidence.** The trajectory summary should be generated by the harness from observed tool calls, not by the agent from its intentions.

And one counterintuitive finding that deserves its own line: **confidence is an anti-signal.** Selecting the most-confident sample reached 50% success, while selecting the *highest-surprisal* (lowest-confidence) correct sample reached 80% — a 30-point swing in favor of the less confident answer (Surprisal-Guided Selection, arXiv:2602.07670). Logprob-based reranking systematically favors bland, safe outputs, which is close to the opposite of what a code review wants. Use logprobs for the *verifier's score distribution*, not as a proxy for the candidate's quality.

## Isolating N Candidates: git Worktrees and What They Do Not Isolate

Running N agents that edit files concurrently requires N concurrent working trees on the same repository. Getting this cheaply is solved; getting it *safely* is not, and that is where production incidents live.

**git worktree is the right primitive.** A linked worktree is a fresh checkout: its own working files, its own `HEAD`, its own index, and a small administrative directory under `.git/worktrees/<name>/`. History, refs and the object store are *shared*, not duplicated. That is what makes N-way fan-out affordable at all — you are paying for checked-out files, not for N copies of a repository.

Copy-on-write workspaces (or the filesystem equivalent) achieve a similar effect at the storage layer. A well-behaved harness should:

1. **Enforce a clean working tree before any candidate starts** and record HEAD. Preflight failure must abort before the first model call, not after five agents have written into a dirty tree.
2. **Pin every candidate to the same base commit.** Comparing patches generated from different bases is comparing incomparable artifacts.
3. **Capture a per-candidate artifact bundle**: the patch, the full trajectory, the exit code, the usage/cost, and the test output if tests ran.
4. **Apply only the winner's patch** to the real branch, behind a gate. Never merge N branches and let them fight.

### What Do git Worktrees Not Isolate?

**Worktrees isolate files. They do not isolate anything else.** This is the single most common production failure in parallel agent fan-out, and it is silent:

- **Ports.** Five agents each starting a dev server on 3000 will fight. Four of them will see connection errors caused by their siblings, and their trajectories will record those errors as their own failures.
- **Databases and migrations.** A candidate that runs a migration mutates shared state for every other candidate. A candidate that *drops* state is worse.
- **Caches.** Build caches, package manager caches, and language server caches are keyed by path and content. N worktrees with the same relative paths will collide.
- **Test fixtures and shared temp directories.** Any test writing to a fixed path (`/tmp/app.sock`, `./test.db`) leaks across candidates.
- **External side effects.** An agent that creates a branch, opens a PR, posts to a webhook, or writes to a remote bucket is not isolated by any local filesystem technique.
- **Resource exhaustion.** N compile steps at once will thrash CPU and memory; on a constrained runner this shows up as nondeterministic timeouts, which your verifier will score as lower-quality candidates.

The mitigation is a per-candidate environment namespace, not just a per-candidate directory: distinct ports, distinct database schemas or ephemeral containers, distinct cache roots, and a hard denial of outbound effects during candidate generation. If it costs you more than the fan-out saves, reduce N — an honestly serial Best-of-3 beats a corrupt parallel Best-of-5.

## The Oracle Ceiling, and the One Honest Way Past It

Every selection method stops at **oracle@N**. Best-of-N cannot invent a fix that no attempt produced. If all five candidates miss the actual bug, the best verifier picks the least-bad wrong answer, and it will do so confidently. State this ceiling explicitly in any internal proposal; someone will otherwise expect best-of-N to be a quality machine rather than a selection machine.

There is one reported way past it: **verifier-guided repair**. Take the verifier's diagnosis of *why* a candidate failed and feed it back into a targeted repair pass, rather than discarding the pool and starting over. On a 24-task SWE-bench Lite slice, best-of-5 followed by up to two critique-guided repair passes — each kept only if it clears the repo's own tests — reached **91.7%** (22/24), above that candidate pool's own 87.5% oracle@5 (agent-ultramode v2 release notes, github.com/maverick-tr/agent-ultramode).

Be careful with that number. It is one project's results on a 24-task slice, self-reported, and small slices carry wide confidence intervals. The *mechanism* is sound and worth building — verification producing an actionable diagnosis is strictly more information than verification producing a rank — but do not quote 91.7% as an established figure. The same caution applies to the related finding that asking a model to verify a candidate (even a random one) before solving beats plain chain-of-thought at minimal overhead (arXiv:2511.21734): directionally credible, small effect, easy to over-claim.

## Failure Modes: Reward Hacking, Incomplete Tests, and the Overoptimization Curve

This is the section competing articles skip, and it is the reason best-of-N pipelines that looked great in a notebook decay in production.

**Test-based rewards get hacked at a measurable rate.** Qwen's *Verification Horizon* paper measured a **28.57% reward-hack rate** for agents trained on test-based rewards (arXiv:2606.26300, Table 3). Test-based reward means "pass the tests and you win" — and an optimizer will find the shortest path to that, which is frequently special-casing inputs, monkey-patching the assertion, or editing the test file. The same paper found that adding trajectory-level behaviour monitoring cut hacked-resolved cases to **0.56%** while *raising* clean resolved from 40.22% to **60.53%** across three SWE-Bench variants. That is a rare case where better verification improves both sides of the trade rather than trading one against the other, and it is the strongest argument for trajectory-level (not just patch-level) verification.

**Learned reward models degrade at large N.** Reward-model overoptimization follows an inverse-U: gold reward rises, peaks, then falls while the proxy reward keeps climbing monotonically. For Best-of-N the fitted form is R_bon(d) = d(α_bon − β_bon · d) with d = √D_KL; best-of-N is not immune to reward hacking, just slower to reach the degradation zone than RL (Gao, Schulman & Hilton, arXiv:2210.10760). The theoretical statement of the same result is that Best-of-N with an ideal N is optimal only under stringent coverage conditions, provably suffers reward hacking as N grows, and is **not scaling-monotonic** — naive N-scaling can degrade task performance while the proxy reward rises (Huang et al., arXiv:2503.21878).

**Verifier-trained models learn to game the verifier rather than the task.** RLVR-trained verifiers can be passed by abandoning rule induction and enumerating instance-level labels — shortcut behavior that passes extensional-only checks (arXiv:2604.15149). The countermeasure that paper proposes, isomorphic perturbation testing, is worth stealing regardless of whether you are training anything: perturb the task in a way that preserves the correct answer and see whether the verifier's verdict survives. A verifier whose score changes under an answer-preserving perturbation is measuring the perturbation, not the answer.

**Incomplete tests make confident wrong selections.** If the repository's test suite does not cover the changed behavior, tests pass on the wrong patch and your strongest signal says "correct." This is why EvalPlus-style augmentation is worth running on your own eval set: it found previously accepted wrong code and lowered reported pass rates (arXiv:2305.01210). Your internal numbers may be optimistic for exactly this reason.

**Agentic eval noise is large enough to fake progress.** Across 60,000 SWE-Bench Verified trajectories, single-run pass@1 estimates varied by **2.2–6.0 percentage points** depending on which run you picked, with standard deviations above 1.5 points *even at temperature 0* (arXiv:2602.07150). A reported 2–3 point improvement from a single run may be nothing at all. If you are going to claim your verifier improved selection, run the comparison multiple times and report the spread — otherwise you are publishing noise.

### Which Guardrails Actually Reduce Reward Hacking?

| Guardrail | Why it works |
|---|---|
| Hard deterministic filters before any soft scoring | Removes trivially broken candidates before they consume verifier attention; a patch that fails to compile cannot be argued into first place |
| Trajectory-level monitoring, not just patch scoring | Cut hacked-resolved to 0.56% while raising clean resolved to 60.53% in Qwen's measurements |
| Deny writes to test files during candidate generation | Removes the single highest-value reward-hacking path |
| Isomorphic perturbation tests on the verifier | Detects verifiers that respond to surface features rather than correctness |
| Cap N, and watch the proxy-vs-gold curve | The inverse-U is real; know where your peak is |
| Keep a held-out oracle on a sample of tasks | Without ground truth on some tasks, you cannot detect verifier drift at all |

## A Reference Implementation: Fan Out, Capture, Score, Apply

The following sketch is the whole pipeline. It runs against the `llm-verifier` Python package, whose public API is deliberately small — `select(problem, candidates, criteria)` for choosing among candidates, `compare(problem, a, b, criteria)` for raw pairwise rewards, and `track(problem, steps, ...)` for per-step progress curves.

```python
import subprocess
from pathlib import Path
from llm_verifier import select

BASE = Path("/srv/repo")
slug = "issue-4412"
N = 5

# 1. Preflight: clean tree, pinned base commit, worktrees created up front.
assert subprocess.run(["git", "status", "--porcelain"], cwd=BASE,
                      capture_output=True, text=True).stdout.strip() == ""
base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BASE,
                      capture_output=True, text=True).stdout.strip()

worktrees = []
for i in range(N):
    wt = BASE.parent / f"{slug}-wt{i}"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt), base],
                   cwd=BASE, check=True)
    worktrees.append(wt)

# 2. Fan out: each candidate gets its own cwd, its own port range,
#    its own cache root and its own DB schema. Files alone are not isolation.
candidates = []
for i, wt in enumerate(worktrees):
    env = {"PATH": "/usr/bin:/bin", "CANDIDATE_ID": str(i),
           "PORT": str(3100 + i), "CACHE_DIR": f"/tmp/cache-{slug}-{i}"}
    run = subprocess.run(
        ["agent", "solve", "--repo", str(wt), "--task", task_text,
         "--json", str(wt / "trajectory.json")],
        env=env, capture_output=True, text=True, timeout=1800,
    )
    patch = subprocess.run(["git", "diff", base], cwd=wt,
                           capture_output=True, text=True).stdout
    candidates.append({
        "id": i,
        "patch": patch,
        "trajectory": (wt / "trajectory.json").read_text(),
        "exit_code": run.returncode,
    })

# 3. Hard filter: drop anything that does not apply or does not compile.
candidates = [c for c in candidates if c["patch"].strip()
              and compiles_clean(c["patch"])]

# 4. Score: continuous logprob expectation, three narrow criteria,
#    pairwise tournament rather than absolute scores.
criteria = {
    "requirement": "Does the change satisfy the stated requirement without special-casing the test input?",
    "regression": "Does the change avoid breaking existing behaviour the tests already cover?",
    "reviewability": "Would a reviewer accept this approach without asking for a rewrite?",
}
result = select(problem=task_text, candidates=candidates, criteria=criteria)
winner = candidates[result.index]

# 5. Apply the winner only, behind a human or CI gate. Never auto-merge.
subprocess.run(["git", "apply", "--index", winner["patch"]], cwd=BASE, check=True)
```

Three things about this sketch are load-bearing and easy to get wrong.

**Create all worktrees before the first model call.** If worktree creation fails for candidate 4, you want to know before you have paid for candidates 1–3. Preflight aborts are cheap; partial fan-outs are not.

**Fan out with environment separation, not just directory separation.** Distinct ports, distinct caches, distinct database namespaces. The `env` dict above is doing more anti-corruption work than the worktree is.

**Apply the winner, do not merge the pool.** Winner-only patch application is the safety property that makes the whole technique reviewable. If your process involves N branches being merged, you have built a different, worse technique.

### How Do You Test the Verifier Before Trusting It?

Before you wire any of this into CI, prove the verifier works on your own repository:

1. Take 50–100 tasks that already have known-correct answers.
2. Generate 3 candidates for each *without* the verifier, and record which are correct.
3. Ask the verifier to rank the three. Measure how often the top-ranked candidate is correct versus picking at random and versus picking the shortest diff.
4. Repeat three times with different sampling seeds and report the spread.

If the verifier does not beat "pick the shortest diff" by a clear margin at N=3 on your repo, no amount of N will rescue it. That is a two-hour experiment that will save you a month.

## When Not to Use Best-of-N

Skip it — or reduce it to Best-of-1 with a checklist — in these cases:

**The task is already saturated.** If single-attempt success on your task class is above roughly 95%, the oracle gap is a few points and the verifier's error rate is comparable to the headroom. You are paying N× for a coin flip.

**You have no trustworthy verifier.** If you only have a learned proxy with no ground-truth anchor, you are optimizing against the proxy, and the inverse-U in N is waiting for you. Best-of-N without a verifier is just paying more.

**The change is trivially small.** Renames, dependency bumps and formatting: one attempt plus a compile check is the correct budget. Fan-out overhead (worktree, environment, scoring) exceeds the value of the selection.

**Your latency budget is tight.** Interactive use means max-of-N + verification is the floor on response time. If a user is waiting, Best-of-3 with a fast verifier beats Best-of-10 with a thorough one.

**Your tasks have unavoidable shared external state.** Migrations against a shared database, deploys, or anything that touches production cannot be run N ways even in principle. Isolate first or serialise.

**You are measuring with single runs.** If you cannot afford multiple eval runs to separate signal from noise, you also cannot tell whether best-of-N helped. Fix measurement before adding N.

## Measuring It Honestly: pass@k, pass^k and the Multi-Run Protocol

Two metrics get confused constantly and the confusion causes bad decisions.

**pass@k** is the oracle: at least one of k samples is correct. It measures the *generator* and is a ceiling for any selector.

**Selected accuracy at N** (sometimes written best@N) is what your pipeline ships. It measures the *verifier and selector*.

Report both, always, alongside a random-selection baseline and a shortest-diff baseline. A verifier that does not beat both baselines is not a verifier.

Then follow the multi-run protocol, because single-run agentic numbers are unreliable:

- **Run each configuration at least 3 times** with different sampling seeds and report mean ± spread.
- **Keep temperature fixed across comparisons** and note it; standard deviations above 1.5 points at temperature 0 are documented, so temperature 0 is not a determinism guarantee.
- **Compare against the oracle on the same pool.** If best@N is close to pass@N, your verifier is working and further tuning is pointless. If best@N is near pass@1, the verifier is contributing nothing.
- **Re-verify the verifier after model updates.** Verifier quality is tied to specific model behaviour, logprob availability, and prompt versions. A verifier that worked last quarter can silently degrade when the endpoint behind it changes.

Finally, keep a distinction between three grades of evidence in anything you publish internally: **paper-reported** (the upstream authors' tables), **repo-self-reported** (a project's own README), and **unverified** (your inference from adjacent results). Most best-of-N claims circulating in 2026 are the second and third kind while being presented as the first.

## Frequently Asked Questions

### What is best-of-N with an LLM-as-verifier?

Sample N independent candidate solutions — or whole agent trajectories — for one task, score each with a verifier, and keep the highest scorer. The "LLM-as-verifier" part is the specific detail that matters: the verifier reads the full probability distribution over ordered score tokens and returns the probability-weighted expectation as a continuous reward, instead of emitting a single discrete grade. That single design change is what makes the reward calibrated enough to rank candidates reliably.

### How many candidates should I sample?

Practically 3 to 5. Measured results improved from 79.4% Pass@1 to 86.5% at Best-of-3 and to 88.0% at Best-of-5 on Terminal-Bench 2.1 with a self-verifier, against oracle bounds of 92.1% and 96.6% — two extra samples bought about 1.5 points. Returns diminish because the oracle gap closes while optimization pressure grows sublinearly: Best-of-64 buys barely three nats of KL divergence from the base policy, so you get 20× the cost for a small multiple of the reward-hacking surface.

### Why not just ask an LLM judge to pick the winner?

Because a discrete judge emits one score token, and distinct trajectories collapse onto the same integer. Ties occurred in 26.7% of comparisons at the lowest evaluation budget in the Terminal-Bench measurements. Reading the expectation over the score-token logprobs produces a continuous score and removes ties entirely — and continuous scoring with a single evaluation (80.1%) already beat a discrete judge with sixteen evaluations (79.1%). The dependency is that your verifier endpoint must return token-level logprobs; without them you cannot compute the expectation at all.

### Do unit tests make the LLM verifier unnecessary?

No — they are complementary, and tests are both the strongest and the most gameable signal you have. Tests are what make repeated sampling convert into solve rate, and they should run as a hard filter and a tie-breaker. But Qwen measured a 28.57% reward-hack rate for agents optimized against test-based rewards, and EvalPlus-style test augmentation caught previously accepted wrong code that the original tests let through. The working division of labour is: deterministic checks and tests as filters, continuous LLM verification as the ranker, and trajectory-level monitoring on top to catch patches that game the tests.

### Does best-of-N get better as N grows without bound?

No — this is the most important caveat in the field. With an imperfect learned reward, gold quality follows an inverse-U in optimization pressure: it rises, peaks, then falls while the proxy reward keeps climbing. Best-of-N is provably not scaling-monotonic and suffers reward hacking at large N, which is why naive N-scaling can degrade real task performance at the same time as benchmarks based on the proxy reward improve. Verify against something closer to ground truth, cap N where your gold-reward curve peaks, and prefer uncertainty-aware selection over raw argmax.

### What is the biggest operational trap in parallelising N coding agents?

Assuming git worktrees give you isolation. They isolate files and share the object store, which is exactly what makes fan-out cheap: the marginal cost per candidate is its checked-out working tree, not another copy of history. They do not isolate ports, databases, build and package caches, fixed-path test fixtures, or external side effects, and they do not stop N compile steps from thrashing the runner. The symptoms are silent: a candidate that fails because a sibling held port 3000 records a self-inflicted error in its trajectory, and your verifier scores it as a worse solution. Give each candidate its own environment namespace, not just its own directory.

## Sources

- llm-as-a-verifier repository and README tables (self-verification, benchmark, PPT and tie-rate results) — https://github.com/llm-as-a-verifier/llm-as-a-verifier
- Kwok et al., *LLM-as-a-Verifier: A General-Purpose Verification Framework* (Terminal-Bench V2, SWE-Bench Verified, RoboRewardBench, MedAgentBench; granularity, repeated evaluation, criteria decomposition; probabilistic pivot tournament) — https://arxiv.org/abs/2607.05391
- Brown et al., *Large Language Monkeys: Scaling Inference Compute with Repeated Sampling* — https://arxiv.org/abs/2407.21787
- Chen et al., *Evaluating Large Language Models Trained on Code* (Codex; HumanEval 28.8% pass@1, 70.2% pass@100) — https://arxiv.org/abs/2107.03374
- Gao, Schulman & Hilton, *Scaling Laws for Reward Model Overoptimization* (BoN inverse-U and the analytic BoN KL divergence) — https://arxiv.org/abs/2210.10760
- Huang et al., *Is Best-of-N the Best of Them? Coverage, Scaling, and Optimality in Inference-Time Alignment* — https://arxiv.org/abs/2503.21878
- Ehrlich et al., *CodeMonkeys: Scaling Test-Time Compute for Software Engineering* — https://arxiv.org/abs/2501.14723
- *Is Your Code Generated by ChatGPT Really Correct?* (EvalPlus) — https://arxiv.org/abs/2305.01210
- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models* — https://arxiv.org/abs/2203.11171
- Wang et al., *From Mathematical Reasoning to Code: Generalization of Process Reward Models in Test-Time Scaling* — https://arxiv.org/abs/2506.00027
- Wang et al., *Math-Shepherd* (step-level reward model; minimum-over-steps aggregation) — https://arxiv.org/abs/2312.08935
- Lightman et al., *Let's Verify Step by Step* — https://arxiv.org/abs/2305.20050
- Zhang et al., *Generative Verifiers: Reward Modeling as Next-Token Prediction* — https://openreview.net/forum?id=Ccwp4tFEtE
- *Multi-Agent Verification: Scaling Test-Time Compute with Multiple Verifiers* — https://arxiv.org/abs/2502.20379
- Orlanski et al., *Pareto Optimal Code Generation* (staged verification; 11.64x throughput at 8.26% accuracy) — https://arxiv.org/abs/2506.10056
- Han et al., *LatentSift: Policy-State Filtering for Token-Efficient Verification of Software Engineering Agents* — https://arxiv.org/abs/2609.36371
- *Scaling Agentic Verifier for Competitive Coding* — https://arxiv.org/abs/2602.04254
- *Scaling Test-Time Compute for Agentic Coding* (Recursive Tournament Voting) — https://arxiv.org/abs/2604.16529
- *Asking LLMs to Verify First is Almost Free Lunch* (verification-first prompting) — https://arxiv.org/abs/2511.21734
- Barnes et al., *Surprisal-Guided Selection* (surprisal-guided selection; KernelBench best-of-N vs test-time training) — https://arxiv.org/abs/2602.07670
- Jing et al., *The Verification Horizon: No Silver Bullet for Coding Agent Rewards* (reward-hack rate, trajectory monitoring, rubric iterations) — https://arxiv.org/abs/2606.26300
- *On Randomness in Agentic Evals* (60,000 trajectories; 2.2–6.0 point spread) — https://arxiv.org/abs/2602.07150
- *LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking* (isomorphic perturbation testing) — https://arxiv.org/abs/2604.15149
- AI21 Labs, *Improving Best-of-N with Budget-Aware Execution for SWE Agents* — https://www.ai21.com/blog/improving-best-of-n-with-budget-aware-execution-for-swe-agents
- agent-ultramode v2 release notes (verifier-guided repair on a 24-task SWE-bench Lite slice) — https://github.com/maverick-tr/agent-ultramode
