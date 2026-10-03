---
title: "Prove-It: An Adversarial Verification Agent Skill for Claude Code (2026 Guide)"
date: 2026-10-01T02:20:51+00:00
tags:
  - "adversarial verification agent"
  - "prove-it claude code skill"
  - "falsification based verification LLM"
  - "agent self-verification skill"
  - "PROVEN FAILED NOT PROVEN BLOCKED verdict"
  - "vibe verification"
  - "counterfeit proof detection"
  - "weakened test assertion detection AI"
  - "stop AI agent premature success claim"
  - "fresh context verifier agent"
description: "Prove-It is a single-file Agent Skill that forces a coding agent to falsify its own 'done' claim and return one of four verdicts, not reassurance."
draft: false
schema: "schema-prove-it-adversarial-verification-skill"
cover:
  image: "/images/prove-it-adversarial-verification-skill.png"
  alt: "Prove-It: An Adversarial Verification Agent Skill for Claude Code (2026 Guide)"
  relative: false
---

An adversarial verification agent is a checker with an inverted objective: instead of collecting signals that confirm a claim, it is built to refute it. Prove-It turns that refuter on a coding agent's own "done" claim, answering with one of four verdicts — PROVEN, FAILED, NOT PROVEN, or BLOCKED — instead of a paragraph of reassurance.

That is the short answer. The rest of this guide explains why the pattern exists, what the four verdicts actually mean, where the skill stops being useful, and how a 12-case self-authored benchmark should be read without overselling it.

## What Is an Adversarial Verification Agent?

Most people arrive at this topic assuming "adversarial verification" is a synonym for code review or a stricter test suite. It is neither, and the distinction matters because it determines what the agent is actually optimizing for.

| Pattern | Question it asks | Who does the work | Failure mode it catches |
|---|---|---|---|
| Unit testing | "Does this input produce this output?" | A fixed test suite | Regressions in covered behaviour |
| Self-review | "Does this code look right to me?" | The same agent, same context | Almost nothing — same premises |
| Code review | "What else might be wrong here?" | A human or a peer agent | Design issues, missing cases |
| Adversarial verification | "What would let this pass while the claim is still false?" | A refuter with an inverted objective | False assurance |

The adversary's job is not to find more issues. Its job is to answer one question about one frozen claim: is there a world in which the evidence you are holding is true and the claim is still false? That is falsification-first verification, and it is a different search direction from review. Review expands the search space; refutation constrains it to a single proposition and tries to break that proposition specifically.

Prove-It states the reframe directly in its own doctrine: don't try to prove it works, try to prove it doesn't — the same prover-verifier inversion [formalized in OpenAI's prover-verifier games](https://arxiv.org/abs/2407.13692). The skill is deliberately small — four rules and one verdict — and it changes the verification *objective* rather than the test framework, which is why it ports across stacks, languages, and agent hosts without a runtime dependency.

## Why Can't Your AI Agent's "Done" Claim Be Trusted?

The case for an external refuter is not philosophical. It is measurable, and the measurement is uncomfortable.

A benchmark of 14 open-source non-reasoning models — [Self-Correction Bench](https://arxiv.org/abs/2507.02778), published as arXiv 2507.02778 and presented at COLM 2026 — found a 64.5% average "Self-Correction Blind Spot": these models reliably corrected an error when it was presented as external input, but failed to correct the *byte-identical* error when it appeared inside their own output. This is not an artifact of artificial test errors. When the models' own naturally generated errors were re-presented externally, they caught only 4.3% to 10.8% of them.

The most useful detail in that paper for anyone building agent harnesses is the mitigation. Simply appending the word "Wait" [reduced the self-correction blind spot by 89.3%](https://arxiv.org/pdf/2507.02778). The capability was already present; it required external activation rather than new capability. A follow-up study, [*The Self-Correction Illusion* (arXiv 2606.05976)](https://arxiv.org/html/2606.05976v1), put numbers on the same mechanism: relabeling a wrong claim from the agent's own reasoning into an external user message lifted the correction rate by 23 to 93 percentage points across seven model families. A "self-distrust" prompt that left the claim in place yielded only 0-23% correction, against roughly 70% for the relabel.

The conclusion is structural, not stylistic: a same-session "double-check" is not a second opinion. It is a consistency check against the agent's own premises. Huang et al. ([*Large Language Models Cannot Self-Correct Reasoning Yet*, arXiv 2310.01798](https://arxiv.org/abs/2310.01798), ICLR 2024) showed that intrinsic self-correction without external feedback often fails to improve and can actively degrade reasoning accuracy. [CRITIC](https://arxiv.org/abs/2305.11738) (arXiv 2305.11738) showed what does work: critiquing that calls external tools rather than re-reading its own prose. And [*LLM Critics Help Catch LLM Bugs*](https://arxiv.org/abs/2407.00215) (McAleese et al., OpenAI) established the empirical basis for LLM-as-verifier — purpose-trained critics find bugs in real-world code that human reviewers miss, and their critiques were preferred over human-written ones in evaluation.

Put those four results together and the architecture writes itself: the verifier must be a separate context, must be pointed at the world rather than at the author's reasoning, and must be given an objective that rewards refutation.

## What Is "Vibe Verification"?

"Vibe verification" is the named anti-pattern this whole skill family exists to interrupt. It is the moment an agent accumulates enough green signals to feel confident and stops looking for ways its conclusion could be false.

It is a real, observable behaviour, and it is easy to recognize once you have a name for it:

- **Vibe verification:** "Tests pass. Build is green. Looks good."
- **Adversarial verification:** "What would let these tests pass while the original bug still exists?"

The second question is not rhetorical. It has concrete answers. The test might be asserting on a mocked collaborator that no longer matches the real one. The assertion might have been weakened — `expect(x).toBe(3)` quietly edited to `expect(x).toBeTruthy()` — during the same session that "fixed" the failure. The suite might be running against a stale build artifact. The test might be skipped, and the skip might be reported as a pass by a runner that only checks the exit code.

None of those require bad faith. They require an agent that stopped searching in the direction of falsity. That is what "vibe verification" describes, and it is why the fix is a change of search direction rather than a longer prompt saying "be careful."

## How Does Prove-It Work? Four Rules, One Verdict

Prove-It, published by Pablo-aps in August 2026, packages the refuter as an Agent Skill — Anthropic's [documented Agent Skills format](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for modular capabilities (instructions plus metadata plus optional scripts) that load on demand and extend Claude automatically when relevant. The skill implements a four-step loop.

**1. DEFINE — freeze a falsifiable claim and its acceptance criteria before inspecting any evidence.** This ordering is load-bearing. If you read the evidence first and write the criteria second, verification degrades into moving the goalposts until the evidence fits. The claim must be specific enough to be wrong: not "the endpoint works" but "a POST to `/api/export` with a valid token enqueues a job and the job completes with a downloadable artifact."

**2. BREAK — produce a ranked falsification plan.** What are the most plausible ways this claim could be false given the evidence I am about to collect? What is the single cheapest decisive check — the one that, if it fails, ends the investigation? The skill asks for the safest decisive check first, not the most dramatic one.

**3. VERIFY — verify the outcome, not a proxy for the outcome.** This is where most false assurance is manufactured, and the skill treats proxy-versus-outcome confusion as a first-class defect rather than an edge case.

**4. VERDICT — emit exactly one of four values.** No prose hedging, no "looks good to me," no confidence percentages.

The skill is explicitly out of scope for a lot of things people assume it does. It ships no runtime dependencies, no hooks, no background process, no telemetry, no MCP server, and no orchestration layer. It is a behavioural guardrail, not a test framework and not a security scanner. Its own prior conclusions are treated as claims to be re-verified, not as evidence — which is the detail that separates it from a session-level reminder to try harder.

## What Do the Four Verdicts — PROVEN, FAILED, NOT PROVEN, BLOCKED — Actually Mean?

The verdict vocabulary is arguably the real product. Four values, deliberately calibrated, each with a narrow scope.

| Verdict | Requires | Does *not* claim |
|---|---|---|
| **PROVEN** | A decisive check ran and passed, within frozen acceptance criteria | Formal correctness, future safety, or behaviour under untested conditions |
| **FAILED** | A decisive check ran and produced direct contradiction | That the *approach* is wrong — only that the claim is |
| **NOT PROVEN** | Evidence is indirect, incomplete, stale, or narrower than the claim | That the claim is false |
| **BLOCKED** | A specific named check cannot run, and the reason is identified | That the claim is unverifiable in principle |

**NOT PROVEN is the most valuable of the four**, and it is the verdict that collapses into a false "done" in every naive agent loop. Consider a claim that reads "the migration completes cleanly on production data." A test suite against a 100-row fixture does not refute the claim and does not establish it. The honest verdict is NOT PROVEN. An agent with only two options — pass or fail — will inevitably report pass, because the tests are green.

**BLOCKED is narrower than it looks.** It is reserved for a check you can name and cannot run: no credentials for the staging environment, a service the check depends on is down. "I could not think of a check" is NOT PROVEN, not BLOCKED. That distinction exists because BLOCKED creates a visible escalation, and padding it with vague uncertainty would destroy its signal value.

**FAILED requires direct contradiction.** An agent that has stopped finding positive signals has not proven failure, and reporting FAILED on indirect evidence is the mirror-image error of reporting PROVEN on indirect evidence. Both are miscalibrated verdicts; both destroy trust in the verifier.

The ordering also prevents the failure mode that makes people abandon verification tools: infinite skepticism. A refuter that always answers NOT PROVEN is useless, which is why Prove-It warns explicitly against inventing unbounded hypothetical gaps after the frozen scope is covered.

## How Do You Install Prove-It in 30 Seconds (Claude Code, Codex, Cursor)?

The install is one command:

```bash
npx skills add Pablo-aps/prove-it
```

The skill is a single file, so a manual install is just as easy — drop `SKILL.md` into the skills directory your host reads:

```
.claude/skills/prove-it/SKILL.md    # Claude Code
.agents/skills/prove-it/SKILL.md    # Codex
.cursor/skills/prove-it/SKILL.md    # Cursor
```

Invocation differs by host:

| Host | How to invoke |
|---|---|
| Claude Code | `/prove-it` slash command, or the trigger words below |
| OpenAI Codex | `$prove-it` |
| Cursor | Auto-activates on trigger words in the prompt |

The auto-activation trigger words matter more than they sound. In practice, the skill fires on **prove**, **verify**, **validate**, **confirm**, and **double-check** — which means the cheapest adoption path is not a new command in your workflow but a vocabulary change in the prompts you already write. When you would have typed "make sure this works," type "verify this and give me a verdict."

A realistic single invocation looks like this:

```text
/prove-it Fix the pagination bug in listUsers() — the per_page
parameter is ignored when page > 1.

Claim: listUsers({page: 3, per_page: 10}) returns records 21-30.
Acceptance: the returned array length is 10 and the first record's
id matches the 21st record in the unfiltered table.
```

Then let it run. The value is not that it finds something every time — it is that the answer arrives as one of four words instead of a paragraph of reassurance.

## Why Is a Passing Signal Not a Passing Outcome?

The single most reusable table in this topic is the proxy-versus-outcome mapping. Every row is a signal that feels like proof and is not.

| Signal you observe | What it actually establishes | What still has to be true |
|---|---|---|
| Tests are green | The assertions that ran passed | The assertions cover the original bug |
| Build succeeded | Compilation finished | The artifact being tested is this build |
| Deploy reported success | The control plane accepted the rollout | Every replica runs the new version |
| Healthcheck returns 200 | One endpoint answered | Dependencies and workers are healthy |
| HTTP 200 returned | The request was accepted | The async operation completed |
| No ERROR lines in the log | No error-level lines were emitted | No relevant failure was logged at all |
| One request succeeded | That request succeeded | There is no race under concurrency |

That last row is why verification skills keep insisting on outcomes. A race condition is not falsified by a single successful request any more than a flaky test is proven stable by one green run.

The 2026 maintainability data explains why this matters more now than it did in 2022. GitClear's [analysis of 623 million code changes](https://www.gitclear.com/the_ai_code_quality_maintainability_gap) (2023-2026) found refactoring line moves down 70%, long-term legacy maintenance down 74%, cross-file function calls down 35% — while within-commit copy/paste rose 41%, duplicated code blocks rose 81% (from 40.3 to 73.0 duplicated lines per million changed lines), and error-masking constructs rose 47%. In their earlier 211-million-line study, 2024 was the first year measured where within-commit copy/pasted lines exceeded *moved* (refactored) lines, and refactoring fell from 21% of changed lines in 2022 to under 10% in 2024.

When duplication rises and refactoring falls, "it passed" matters less than "it still holds." Verification has to check the outcome, because the structural signals that used to correlate with correctness are weakening.

## What Is Counterfeit Proof? The Green Signals That Prove Nothing

Counterfeit proof is the practical centerpiece of the skill, and it is a checklist rather than a theory. A construct is counterfeit when it hides, redefines, or removes the behaviour being verified.

| Construct | Why it counterfeits proof | Legitimate version |
|---|---|---|
| `test.skip` / `xit` | Reports as a non-failure while testing nothing | A tracked issue with a named owner |
| Weakened assertion (`toBe(3)` → `toBeTruthy()`) | Passes for the wrong reason | Assert the specific value |
| Ignored exit code | Turns a failing command into a passing pipeline step | Check the code, fail the step |
| Empty `catch {}` | Converts an exception into silence | Handle it, or let it propagate |
| `\|\| true` / blanket suppression | Deletes the failure instead of the cause | Suppress one specific, cited case |
| Hardcoded result | The test asserts the value it was given | Compute the expected value independently |
| Mock that no longer matches reality | Verifies the mock, not the system | Contract test against the real interface |
| Unrelated mock substitution | The wrong collaborator is stubbed | Stub the actual dependency |
| Timeout increased without a reproduced timing cause | Masks a flake instead of explaining it | Reproduce the timing failure first |

None of these are automatically wrong. Mocks are necessary. Suppressions are sometimes correct. Skips are sometimes honest. The point is that each one is *evidence against a claim* when it hides or redefines the behaviour you are claiming to have verified — and an agent that adds one during the same session it declares success has not verified anything.

A copy-pasteable pre-flight check, adapted from the skill's own doctrine:

```text
Before trusting any green signal, ask:
[ ] Did I run the thing, or the tests around the thing?
[ ] Did anything get skipped, and does the runner count skips as passes?
[ ] Did I edit any assertion, mock, timeout, or suppression this session?
[ ] Does the artifact under test come from the code I changed?
[ ] Is this signal an outcome, or a proxy for an outcome?
[ ] What would let this signal be true while the claim is false?
```

## What Do False "Done" Claims Look Like in Practice?

The generic form of each failure is easier to recognize than the abstract rule, so here are the four that recur most often in practice.

**The weakened assertion.** An agent fixes a bug, sees `expect(count).toBe(12)` fail, and changes it to `expect(count).toBeGreaterThan(0)`. The suite is green. The bug is intact. The falsifying check is not "do tests pass" but "does any assertion in this session's diff constrain the behaviour I claimed to fix?"

**The stale replica.** A deploy reports success. The rollout controller accepted the change. Two of five replicas are still serving the previous image because the readiness probe passed on a cached layer. The proxy (deploy accepted) is true; the outcome (every replica runs the new version) is false. The decisive check targets the replicas, not the controller.

**The wrong-environment logs.** A claim that a handler no longer throws is supported by a clean log file — from the pre-fix window, or from a different environment than the one under test, or from a service whose log level filters the relevant exception. The evidence is real and irrelevant. This is the canonical NOT PROVEN: indirect, stale, or narrower than the claim.

**The async export.** An HTTP 200 from the export endpoint proves the request was accepted. It does not prove the job ran, that the artifact exists, or that the file contains the requested rows. The decisive check fetches the artifact and validates the row count against the source — which is exactly the kind of outcome check a refuter demands and a green status code discourages.

## How Does Prove-It Compare to prove_it, bug-hunt, adversarial-verify, and production-audit?

This niche is crowded, and one detail tells you how crowded: at least six unrelated repositories named [`prove-it`](https://github.com/Pablo-aps/prove-it) shipped between April and September 2026 — Pablo-aps, jkaraml, josharsh, jongouveia, ryanda9910, and dvhthomas. The name converged before the design did. That is evidence the need is real and the pattern is not yet standardized, which is why positioning matters more than ranking here.

| Tool | Mechanism | Enforcement point | Best fit |
|---|---|---|---|
| **Pablo-aps/prove-it** (Apache-2.0) | Four-rule loop, one of four verdicts | Agent's own claim, pre-"done" | Portable falsification gate across Claude Code, Codex, Cursor |
| **searlsco/prove_it** (~198★, MIT) | Lifecycle hooks that **block** stop/commit until configured tasks pass | Harness level — cannot be skipped | Claude Code shops that want mechanical enforcement |
| **danpeg/bug-hunt** (~146★, MIT) | Three isolated agents: Hunter → Skeptic → Referee, competing incentives | Independent review of a diff or project | Finding bugs, as opposed to adjudicating a claim |
| **fullo/claude-adversarial-skill** (MIT) | Chain-of-Verification plus tri-modal confidence scoring | Protocol-level, multi-domain | Teams wanting one heavyweight verification framework |
| **Sahir619/fable-method** | Treats completion reports as hostile testimony; re-executes claimed checks | Verifying *another* agent's work | Judging delegated work where re-execution is possible |
| **apoorvjain25/production-audit** (~19★, MIT) | 24 lenses, convergence stop when two consecutive sweeps find nothing | Whole-product audit | Pre-launch audits where 24 lenses fit the budget |
| **henchmarketing-rgb/sub-zero-skill** | Separate fresh-context verifier that checks the live world | Post-deploy outcome check | Claims that resolve to a URL, screenshot, or git ref |
| **lucasfcosta/backpressured** (~63★, MIT) | Four-phase plan → implement → verify → ship loop with gates | Long unattended runs | Multi-hour autonomous runs needing process scaffolding |

The architectural distinction worth internalizing: `prove_it` enforces verification *mechanically* at the harness level and cannot be skipped, whereas Prove-It is a portable prompt-level discipline with zero runtime that works across three different hosts. Those solve different problems. If your team is all-in on Claude Code and you want a hook that physically prevents a commit, the hook-based skill is the stronger control. If you want the same discipline available in Codex and Cursor, or you want to verify a claim without installing infrastructure, the single-file skill is the cheaper primitive.

`bug-hunt` and Prove-It also answer different questions. `bug-hunt` generates and filters findings with three isolated agents and load-bearing scoring incentives (Hunter +1/+5/+10 by severity; Skeptic earns for disproving but pays a 2× penalty for wrongly dismissing a real bug; Referee on symmetric +1/−1 ground-truth framing). Prove-It adjudicates one claim already made. One hunts; the other judges.

Cross-model verification deserves a note here. All-Claude adversarial panels share blind spots, so when the blast radius is high — authentication, cryptography, payments, migrations — adding a cross-vendor finder such as Codex to the panel buys genuine independence rather than more variance. `ng/adversarial-review` builds this in explicitly by treating agreement *across providers* as the strongest available signal.

## Does It Actually Work? Reading the 12-Case Benchmark Honestly

The repository ships a [reproducible 12-case benchmark](https://github.com/Pablo-aps/prove-it/blob/main/benchmark/README.md) with three positive controls. The published directional run — Codex CLI 0.147.0, gpt-5.6-luna, low reasoning, one run per cell, 2026-08-18 — reports the following.

| Metric | Baseline | With the skill |
|---|---|---|
| Correct verdict | 9/12 (75%) | 12/12 (100%) |
| Positive-control accuracy | 2/3 (67%) | 3/3 (100%) |
| Decisive-signal recall | 96% | 96% |
| False-assurance rate | 0/12 | 0/12 |
| Falsification attempt rate | 12/12 | 12/12 |

Read that honestly and the honest reading is: this is a **transparent regression test, not an independent evaluation**. The authors say so themselves, and the reason is straightforward — the cases were authored during the skill's development, by the people who wrote the skill. A 12-case suite with one run per cell cannot separate a real behavioural improvement from overfitting to twelve hand-picked scenarios.

Two further caveats from the repository's own metadata at research time: the project had 9 stars, 0 forks, 0 open issues, and one release, created and last pushed on 2026-08-18, listed on skills.sh. Its nearest neighbors by name and intent — `prove_it` at 198 stars and `bug-hunt` at 146 stars — mean this is an early-stage entrant in an already crowded niche. The metric that deserves the most attention is the one that *didn't* move: decisive-signal recall was flat at 96% in both arms, which suggests the skill is sharpening verdict discipline rather than making the underlying model better at finding evidence.

What the benchmark does establish, and what makes it worth citing, is the method. The results are published with a SHA-256-fingerprinted methodology and a positive-control set that guards against the obvious degenerate strategy — a skill that answers NOT PROVEN to everything would score 0/3 on positive controls and be visibly useless. That design choice is itself a good model for anyone building a verifier.

For the independent evidence, lean on the academic results instead: the 64.5% blind spot, the 23-93 percentage-point relabel lift, CRITIC's tool-interactive results, and the OpenAI critic study. Those were produced by people with no stake in this skill.

## What Does Adversarial Verification Cost, and When Does It Pay for Itself?

Adversarial verification is not free, and almost every write-up in this genre skips the cost. Three verifiers per finding triples the verification pass. Token cost scales linearly with verifier count, which means a naive "adversarially verify everything" policy is a budget leak.

The engineering answer is triage plus thresholds:

- **Route selectively.** Run full adversarial review on high-confidence, high-blast-radius findings only. Mechanical checks — lint, typecheck, build, tests — are cheap and should run first and always.
- **2-of-3 as the code-review floor.** Independent verification is worth more than more variants of the same prompt. Running multiple copies of an identical verifier reduces variance but not bias, so diversify by *perspective* — correctness auditor, security reviewer restricted to trust boundaries, reproducibility auditor — rather than by count.
- **Unanimous for security and compliance.** Where a single refutation should block a change, a majority threshold is the wrong instrument.
- **Tighten when escaped defects surface.** A threshold is a tuning parameter, not a constant. If something reached production that passed verification, the threshold was too loose.

The evidence that the budget is justified comes from the failure side. [Undo research by Coleman Parkes](https://itnerd.blog/2026/09/28/producing-code-has-never-been-easier-but-ai-generated-bugs-and-rising-debugging-workloads-are-slowing-software-delivery) (July-August 2026, n=300 senior engineering leaders at $250m+ revenue organizations) found that 81% of organizations had a production incident or customer-visible outage in the previous six months attributed to AI coding tools, 93% had a root cause misdiagnosed because of an AI hallucination, and 91% had test escapes or serious defects reach production. In the same survey, 35% of AI-generated code reaches production before engineers fully comprehend it, and engineers spend 16.9 hours per week — 42% of the working week — debugging rather than writing.

Faros AI telemetry across roughly 10,000 developers and 1,255 teams points the same direction: high-AI-adoption teams closed 21% more tasks and produced 98% more pull requests, with PR size up 154%, review time up 91%, bugs up 9% per developer, and an incidents-to-pull-request ratio 242.7% higher. DORA's 2025 report put a number on the same effect: every 25% increase in AI adoption correlated with a 1.5% drop in delivery speed and a 7.2% decrease in stability. The bottleneck moved from writing code to reviewing it. A verification gate is a control on exactly that bottleneck, and it is cheap next to a misdiagnosed incident.

## How Do You Build Your Own Refuter? Isolation, Default-Refuted, Fixed Output

If you are building verification into your own harness rather than adopting a skill, five rules generalize. They come from [the clearest editorial treatment of the mechanism available](https://dsplce.co/agentic-engineering/core/adversarial-verification) and they are what separate a refuter from another opinion.

1. **Pass the claim, not the conversation.** The verifier receives the assertion and its cited evidence — never the authoring agent's reasoning chain. Inheriting that chain means inheriting its biases.
2. **Do not include the first model's rationale or a summary of it.** A summary transmits framing even when it drops conclusions.
3. **Do not disclose where the finding came from.** Authority framing is bias; a finding labeled "from a senior reviewer" is evaluated differently from an unattributed one.
4. **Default to refutation.** Uncertainty is not a pass. If the evidence does not decide the claim, the verdict is NOT PROVEN.
5. **Fixed output schema.** A contract with a fixed decision rule and a fixed output shape, not a longer essay. A working refuter returns something closer to `{"refuted": true, "evidence": "<code>", "locator": "auth.py:1-10"}` than four paragraphs of analysis.

The control experiment behind rule five is worth knowing. In that write-up, a deliberately false finding about an empty-token auth bypass — framed as coming from a senior engineer — was correctly *rejected* by a fresh session, which replied with four paragraphs, a code block, two caveats, and an open question back to the human. The verdict was right and the process was unworkable: at 40 findings it "isn't a verification step at all, it's just 40 more things to read." The fix was not more cynicism. It was a contract.

And one meta-rule that the skill family's own doctrine implies: **adversarially verify the verifier.** Isolation, default-refuted, read-only, and frozen acceptance criteria are the safety rails. A verifier that mutates production to obtain proof, or that relaxes the claim after a failed check, is worse than no verifier at all, because it manufactures false assurance with a credible label attached. Read-only by default is not a limitation; it is what makes the verdict trustworthy.

## How Big Is the 2026 Trust Gap? 90% Adoption Versus 24% Trust

The reason a niche this crowded still has room is the size of the gap between how much developers use AI and how much they believe it.

Google Cloud's [DORA 2025 *State of AI-assisted Software Development*](https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report) report, covering nearly 5,000 technology professionals, found 90% of professional developers now use AI at work — up 14% year over year — spending a median of two hours per day with AI tools, with 71% using AI for writing new code. Then the trust paradox: only 24% trust AI-generated output "a lot" or "a great deal," while 30% trust it "a little" or "not at all," and 49% trust it "somewhat." More than 80% still report productivity gains. Autonomous agent adoption lags far behind assisted use: only 17% of developers use agent mode daily, while 61% never use it at all.

Stack Overflow's [2025 developer survey](https://survey.stackoverflow.co/2025/ai) found the distrust is hardening: 46% of developers actively distrust AI accuracy against 33% who trust it, with only 3% reporting high trust, and distrust up from 31% in 2024. The same survey family shows 96% of developers do not fully trust that AI-generated code is functionally correct, yet only 48% always verify it before committing — and 66% name "almost right, but not quite" as their top frustration. Sonar's 2026 survey of 1,149 professional developers adds the operational detail: 38% say reviewing AI code takes more effort than reviewing a colleague's, and 61% say AI often produces code that looks correct but is unreliable.

Meanwhile the measured productivity effect is contested in exactly the direction skepticism suggests. METR's [randomized controlled trial](https://arxiv.org/abs/2507.09089) had 16 experienced open-source developers complete 246 real tasks 19% *slower* when allowed to use early-2025 AI tools on their own repositories — while estimating afterwards that AI had made them 20% faster. That is roughly a 39-percentage-point gap between belief and measurement. A February 2026 METR re-run with late-2025 tools still placed returning developers around 18% slower as the central estimate, with a confidence interval spanning −38% to +9%; METR characterizes the evidence for speedup as "very weak" once selection effects are accounted for.

There is also the benchmark-versus-production gap to keep in view. Claude Opus 4.7 [leads SWE-bench Verified at 87.6%](https://benchlm.ai/benchmarks/sweVerified), but on SWE-bench Pro every top model drops 18-25 points (Opus 4.7 at 64.3%). Roughly 20 points of Verified performance looks like benchmark-specific optimization rather than general code reasoning. When your benchmark number and your production experience disagree, the production experience is data.

A verifier does not close that trust gap by making models better. It closes it by making the *claim* checkable — which is a process fix, not a prompt trick.

## What Does a Verdict Not Claim? Limits and Scope Discipline

Prove-It's most credible design choice is how little its best verdict asserts. PROVEN is scoped to the frozen acceptance criteria and nothing else. It is not a claim of formal correctness, not a claim about untested inputs, and not a claim about future behaviour. A tool that promised more would be lying.

Five limits worth stating plainly:

- **A verdict is only as good as the frozen claim.** Vague acceptance criteria produce a confident verdict about nothing. Write the criteria before you look at the evidence, or you are verifying your ability to rationalize.
- **Positive controls are mandatory.** A verifier that always refutes is as useless as one that always confirms, and it is harder to notice because it feels rigorous. Include cases that must come back PROVEN, and treat a failure there as a bug in the verifier.
- **Verification does not replace review.** It constrains a single proposition; it does not search for the bugs nobody thought to claim were absent.
- **Scope creep is the silent failure.** If the claim gets easier to prove after a check fails, the verification was theater. Frozen means frozen.
- **Read-only is non-negotiable.** Any verification step that changes the system under test has invalidated its own evidence.

## Where Should You Put the Verification Gate in Your Agent Loop?

The cheapest adoption path is not a new tool but a new gate location. Three places pay for themselves fastest.

**Before any "done" is spoken.** This is the default and the highest-value slot. The agent writes the claim and acceptance criteria, runs the refuter, and reports the verdict instead of a summary. The cost is one extra pass; the return is that "done" becomes a word with a defined meaning.

**Before a commit or a merge.** This is where hook-based enforcement outranks a prompt-level skill, because it cannot be skipped. If your team is standardized on one host, `prove_it`-style hooks are the stronger control. If you are multi-host, use the portable skill and make the verdict a required line in the PR description.

**After deploy, against the live world.** The verifier fetches the URL, takes the screenshot, checks the git ref. Only the verifier gets to call a win, and it has never seen the work — only the result. This is the mode where "no evidence, no win" stops being a slogan: a 200 response with the pricing table actually on screen is evidence; "the deploy succeeded" is a proxy.

Across all three slots, the same two questions do the work. *Is this a signal or an outcome?* And *what would let this be true while my claim is false?*

## FAQ: Adversarial Verification Agents, Invocation, and Verdicts

**Is Prove-It a test framework?**
No. It ships no runtime dependencies, no test runner, no hooks, and no orchestration. It is a behavioural guardrail that changes how an agent verifies a claim. You still need tests — the skill's job is to stop you from treating a green test as proof of an unverified outcome.

**Which agents does it support?**
Claude Code (`/prove-it`), OpenAI Codex (`$prove-it`), and Cursor (auto-activation on trigger words). Installation is `npx skills add Pablo-aps/prove-it`, or a manual copy of `SKILL.md` into `.claude/skills/prove-it/`, `.agents/skills/prove-it/`, or `.cursor/skills/prove-it/`.

**What is the difference between NOT PROVEN and BLOCKED?**
NOT PROVEN means the evidence you have is indirect, incomplete, stale, or narrower than the claim — the claim remains open. BLOCKED is reserved for a specific named check that cannot run, with the reason identified, such as missing credentials for the environment the check requires. "I couldn't think of a check" is NOT PROVEN.

**Should I use Prove-It or bug-hunt?**
They answer different questions. bug-hunt generates and adversarially filters findings across three isolated agents with competing scoring incentives — it hunts for bugs. Prove-It adjudicates a claim that has already been made, using four rules and four verdicts. If your problem is "I don't know what's wrong," hunt. If your problem is "the agent says it's fixed and I don't believe it," adjudicate.

**Is adversarial verification worth the extra cost?**
Not for everything. Run mechanical checks — lint, typecheck, build, tests — always and cheaply, then route only high-confidence findings and high-blast-radius changes to full adversarial review. A 2-of-3 independent panel is a reasonable floor for code review, unanimous agreement for security and compliance. Given that 93% of organizations surveyed had a root cause misdiagnosed because of an AI hallucination within a six-month window, the question is usually not whether the gate pays for itself but where to place it.

**Does the 75% → 100% benchmark prove the skill works?**
No, and the authors do not claim it does. It is a 12-case, single-run, self-authored regression test published with a fingerprinted methodology and three positive controls. Read it as evidence of a reproducible method and of verdict discipline, then lean on the independent academic results — the 64.5% self-correction blind spot and the 23-93 percentage-point relabel lift — for the underlying mechanism.

**Where should the verification gate sit in a normal agent workflow?**
Three places pay off fastest: before any "done" is spoken (the default slot, one extra pass for a verdict instead of a summary), before a commit or merge (where hook-based enforcement outranks a prompt-level skill because it cannot be skipped), and after deploy against the live world (where only a verifier that has never seen the work gets to call a win).
