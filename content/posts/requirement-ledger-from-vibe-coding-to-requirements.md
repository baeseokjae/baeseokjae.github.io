---
title: 'Requirement Ledger for Vibe Coding: Recover the Requirements Your AI Session Already Wrote'
date: 2026-10-01T10:29:09+00:00
tags:
  - requirement ledger vibe coding
  - requirement ledger
  - vibe coding requirements document
  - requirements traceability AI coding agents
  - spec driven development with claude code
  - regeneration test specification quality
  - AI code rework rate
  - coding agents
description: "A requirement ledger recovers the requirements your AI coding session already produced — read from the transcript, not invented at the start."
draft: false
cover:
  image: "/images/requirement-ledger-from-vibe-coding-to-requirements.png"
  alt: "Requirement Ledger for Vibe Coding: Recover the Requirements Your AI Session Already Wrote"
  relative: false
schema: "schema-requirement-ledger-from-vibe-coding-to-requirements"
---

A requirement ledger is a retrospective requirements record: instead of writing a specification before you prompt an AI agent, you mine the conversation you already had and reconstruct what you actually required. Its evidence trail is the transcript, a test log, and a read-only Git snapshot — and your last correction beats your first prompt.

## Why do vibe-coded projects lose their requirements?

They lose them because the intent was never written down in the first place — it lived in the chat window, and the chat window closes. A prompt is not a requirement document. It is a compressed instruction to a system that fills in every gap with a plausible guess, and the guesses are what you end up shipping.

The scale of the gap is now measurable rather than rhetorical. JetBrains surveyed 15,509 developers between May and July 2026 and found agents fully write an average of 47% of developers' code, with 90% of professional developers using a coding agent at least weekly and 68% using one daily. A separate cohort breakdown in the same survey is more telling for anyone reviewing the output: the 31% of developers classified as "agentic coders" have 84% of their code written by agents, while the 23% classified as manual still hand-write 75% of theirs.

New Relic's 2026 State of AI Coding report, run with Hanover Research, describes the resulting review paradox in hard numbers. 94% of technology leaders rate AI-generated code as higher quality than human-authored code at the time of review, but 78% report more incidents after it ships, 86% report more senior-staff time spent fixing it, and 74% say at least a quarter of their AI code needs significant rework. 82% experienced at least one production failure tied to AI-generated code in the past six months.

### Why is the transcript the only surviving record of intent?

Because the artifacts that normally carry intent do not exist in a vibe-coding session. In a conventional project, three things encode intent: the ticket, the commit message, and the pull-request discussion. Vibe coding shortens all three. The ticket is a one-line prompt, the commit message is often generated from the diff (describing *what changed*, never *what was wanted*), and the PR discussion is thin because review itself is under pressure — Faros AI's 2026 report, covering 22,000 developers across 4,000+ teams, found median time in PR review up 441.5%, time to first review up 156.6%, incidents per pull request up 242.7%, and PRs merging unreviewed up 31.3%.

So the intent evaporates on a schedule of hours. By the time drift is visible in production, the conversation that justified the code is gone, and the person who could have explained it has moved to the next task. The research paper AfterVibe (arXiv 2607.09900), from authors affiliated with Meta, states the problem precisely: the mapping between the intent expressed in a chat trajectory and the code that resulted is "implicit at best", which undermines the core assumption of code review — that someone can read the code and vouch for it.

### What does a course correction tell you that a prompt cannot?

Everything that matters. The first message states what you asked for. The last correction states what you actually needed. Every pushback is a place where the delivered artifact and the wanted artifact diverged, and that divergence is the requirement, written in the user's own words at the exact moment they noticed the gap.

SWE-chat, a study of real coding-agent sessions cited in arXiv 2609.04681, quantifies how common that divergence is: users pushed back in 44% of turns, and only 44% of agent-produced code survived into commits. A requirement ledger built from the opening prompt is a ledger of the wrong thing. It documents the hypothesis, not the conclusion.

## What is a requirement ledger — and what is it not?

The anchor implementation is `adand-91/requirement-ledger`, a MIT-licensed Python project that describes itself as "a local, privacy-first evidence loop for improving any Git project with Codex or another coding agent." Its positioning is unusually modest because the modesty is the design. Version 0.1 does not autonomously edit your project. It gathers and structures evidence; your agent remains the developer; every real modification stays visible and reviewable.

That constraint is the whole point. A tool that silently rewrites your repository based on an inferred requirement is worse than no tool, because a wrong inference becomes a permanent change with a justification nobody can audit. The ledger produces a DRAFT repair plan stamped "DRAFT — NOT SENT, not-applied" and hands it to the agent you already trust to make edits.

| What a requirement ledger is | What it is not |
|---|---|
| A local, retro-spective evidence loop over an existing Git project | A prospective spec you write before prompting |
| Private evidence separate from quote-free reports | A transcript pasted into a hosted model |
| Conservative attribution with `unknown` as the default | A confident claim about who asked for what |
| A DRAFT repair plan handed to the host agent | An autonomous editor of your repository |
| Numbers emitted by a script, never by a model | A summary with estimated counts |
| A record reviewed before the code diff | A replacement for code review |

The versioned record types make the shape concrete: `SourceRef`, `EvidenceItem`, `IssueRecord`, `FixProposal`, `ValidationResult`. Each of those is a data structure, not a paragraph of prose, which is what makes the ledger queryable and diffable later.

## How does the requirement ledger evidence chain work, step by step?

The pipeline has six stages, and the ordering is not arbitrary — each stage exists to prevent a specific failure in the one after it.

| Stage | Input | Output | Failure it prevents |
|---|---|---|---|
| 1. Capture | Explicit agent transcript (Codex, Claude, or plain text), test log, read-only Git snapshot | A bounded evidence set | Inference from memory or vibes |
| 2. Isolate | The evidence set | Private evidence directory with restrictive modes | Leaking client code into a report |
| 3. Attribute | Private evidence | Upstream / project-local / personal / unknown labels | Blaming the wrong owner |
| 4. Report | Attributed evidence | Quote-free report plus a DRAFT repair plan | Copying verbatim user text into a shared artifact |
| 5. Patch | The DRAFT plan | A host-owned agent patch you review | Unreviewed autonomous edits |
| 6. Validate | Before/after test result bound to a digest | A `ValidationResult` | Claiming a fix that never ran |

The Git snapshot is read-only by design, and the tool never reads or emits remote URLs, which is what closes the "exfiltration by URL templating" hole that most transcript-analysis tools leave open.

## Why is 'unknown' the honest default attribution bucket?

Every recovered requirement gets one of four labels: `upstream` (a convention or dependency imposes it), `project-local` (this codebase's own decision), `personal` (one contributor's preference that was never agreed), or `unknown`.

The value is entirely in the last one. In most retrospective tooling, an inference engine forced to choose will pick the bucket with the best-looking evidence and sound confident. The ledger's insistence that `unknown` is a legitimate and expected terminal state converts a guessing machine into an evidence machine, and it changes the downstream conversation: an `unknown` requirement is a question for the team, while a mislabeled `personal` requirement is a rule nobody agreed to that everyone now follows.

That distinction generalises well beyond this tool. Any time an AI system reconstructs human intent after the fact, the honest output distribution includes a residual "we cannot tell" class, and a system that never produces one is lying by structure rather than by content.

## Two in three professional developers use a coding agent daily — and the requirements still go unwritten

The why-now argument is not about code volume. It is about code that nobody can justify after the fact. Security Boulevard's "The Acceptance Gap" analysis cites a 2026 empirical study of AI-authored commits finding that more than 15% of commits from every AI coding assistant studied introduced at least one issue, and that 22.7% of tracked AI-introduced issues survived to the latest repository revision.

Maintainability metrics point the same direction. GitClear's 2026 Maintainability Gap report, covering 623 million code changes, measured within-commit copy/paste up 41%, code block duplication up 81%, and error-masking constructs up 47%. Meanwhile the productivity gain is real but narrower than the headline: Demirer, Musolff and Yang, studying more than 500,000 GitHub developers with AI-usage telemetry, found cumulative coding activity up 30% for autocomplete, 180% once interactive agents are added, and 240% with autonomous agents — but only 80% at the project level and 30% at actual releases.

The bottleneck moved. Developers now report spending 11.4 hours per week reviewing AI-generated code versus 9.8 hours per week writing new code, a reversal of the 2024 pattern, according to the Agentic Engineering Trends Report 2026. A requirement ledger is a review-capacity tool before it is a documentation tool, because it tells a reviewer which diff is worth reading.

## How do you set up requirement-ledger with Claude Code or Codex?

Installation is deliberately unfashionable, and knowing that in advance saves a wasted afternoon: the project is **not on PyPI**, so `pip install requirement-ledger` will fail. It ships as a skill you clone into your agent's skill directory. It requires Python 3.10 through 3.13 and has zero runtime dependencies.

Three practical notes from the repository itself shape how you run it:

- Sessions reach 250 MB, with single lines running up to 1.5 million characters of base64. Transcripts are streamed line by line, never loaded whole, because the naive whole-file approach fails on inputs of that shape. Pasting a log into a model is not merely expensive; it is the wrong shape of operation.
- There is a deterministic synthetic demo, documented as a sixty-second first run, which is the correct first run. Do not start with your 250 MB production session.
- `scan_transcript.py` is the facts-first entry point. It emits counts and references before any interpretation, and everything downstream consumes those counts.

Read the repository's own numbering rule before you run anything: **every number comes from the script; the model never estimates one.** Counting messages by eye is described in the tooling as "a failed retrospective."

### Why is an invented count worse than no count?

Because a retrospective number gets quoted later as fact. If your report says "the agent rewrote this module eleven times", someone will put eleven in a post-mortem, a planning doc, or a performance review, and eleven will be wrong. A missing count invites someone to go measure it; a fabricated count terminates the enquiry. This is the single most transferable discipline in the project, and it applies to any AI-produced analysis of your work, not just this tool.

There is a matching human-factors reason to care. Shaw and Nave at Wharton, cited in the same Security Boulevard analysis, found that people follow AI advice roughly 80% of the time even when it is wrong. An AI-authored retrospective with an invented number is not a neutral document; it is a document with an 80% chance of being believed.

## What is the authority chain, and why mirror requirement tests?

The engineering half of this idea comes from Justin Chase's field report on the Real Polite Protocol, and it supplies the mechanism the ledger's evidence loop leaves implicit. The protocol writes down a strict authority order that every change must respect:

**RFC / spec → requirement documents → requirement tests → scenarios → implementation code**

A lower-authority artifact must never contradict a higher-authority one. The rule that makes this real is absolute and non-negotiable: when a test fails, the implementation is fixed — the test is never weakened. Changing behaviour means changing the requirement deliberately and explicitly first, in the higher-authority document, and only then changing the test and the code.

Two consequences follow, and both are why this survives contact with a deadline. First, requirement documents become the smallest reviewable unit of intent, which yields a cheap heuristic: if the code diff is large and the requirement diff is empty, something is wrong. Second, requirement tests mirror requirement paths exactly, so coverage analysis becomes a script rather than an exercise in reading — a tool can report a requirement with no test, or a test with no requirement, without parsing either file's contents.

The durable-context effect is what makes the ledger compound. Requirement files accumulate a structured record of every behaviour the system has committed to, so an agent reasons against decided behaviour instead of against whatever the code happens to say today.

## How is a requirement ledger different from spec-driven development?

This is the objection the term has to survive, and the answer is that the two sit on different axes. Birgitta Böckeler's taxonomy on martinfowler.com defines spec-driven development as writing a spec before code, with three maturity levels: **spec-first** (written first, used for the task at hand), **spec-anchored** (kept afterwards to drive evolution and maintenance), and **spec-as-source** (the spec is the primary source file and humans edit only the spec).

All three are prospective. A requirement ledger is retrospective. It does not compete with SDD; it operates on the sessions where SDD never happened, which is most sessions.

| Dimension | Spec-driven development | Requirement ledger |
|---|---|---|
| Direction | Prospective — spec precedes code | Retrospective — spec follows the conversation |
| Trigger | New feature, deliberate ceremony | Existing project, accumulated drift |
| Source of truth | The written specification | The transcript, tests, and Git history |
| Cost profile | Upfront document authoring | Post-hoc evidence extraction |
| Works on legacy vibe code | Rarely | Yes |
| Fails when | Nobody writes the spec | The transcript is already deleted |

The strongest published objection to the prospective approach is concrete rather than philosophical. François Zaninotto at Marmelab describes SDD as reviving "the old idea of heavy documentation before coding — an echo of the Waterfall era", and backs it with an example: a spec-kit run for one small feature (display the current date in a time-tracking app) produced 8 files and 1,300 lines of text. A Kiro run for adding a single "referred by" field to a small CRM generated Requirements.md, Design.md and Tasks.md. Against 1,300 lines for a clock widget, a ledger that reads what you already said and produces a reviewable artifact is the pragmatic option, not the ceremonial one.

The waterfall charge deserves a direct answer too. Chase's response is structural: the spec governs **what** the system does, not **how**; the how lives in a separate, orthogonal instructions layer. If your requirement document specifies Redis over Postgres, you have written a design document wearing a requirement's name, and the objection is correct.

## How do you prove a recovered requirement set is correct?

A recovered requirement set is a hypothesis until something tests it, and AfterVibe (arXiv 2607.09900) supplies the test. A second, blind AI agent rebuilds the artifact from the recovered spec alone — no transcript, no original code — and a three-tier verifier judges equivalence: flexible test execution, verification conditions extracted from the trajectory, and ground-truth alignment via structured LLM reasoning.

The result operationalises "good spec" as "an agent can regenerate passing code from it", rather than as a feeling a human reviewer has. Across 72 real-world vibe-coded tasks from an industrial monorepo, recovered specs scored a mean of 5.06 out of 6.0 across multiple independent regenerations, rising to 5.74 out of 6.0 after iterative strengthening — while the regenerations stayed diverse in their implementation details, which is the evidence that the spec captured behaviour rather than dictating code.

AfterVibe's environmental grounding hypothesis explains why that is achievable. A spec only needs to be concrete about undiscoverable facts — decisions, thresholds, domain constraints — because the agent can navigate the repository for build configuration, naming conventions, module structure and API contracts. You are not documenting your codebase. You are documenting the four things you decided that the codebase cannot tell anyone.

## Why is privacy the feature that decides adoption?

The unglamorous feature is the one that decides whether this works inside a company. Three mechanics matter:

- **Stream everything.** Sessions reach 250 MB with single lines up to 1.5 million characters of base64. A tool that loads the whole thing dies or bills you for it.
- **Separate private evidence from quote-free reports.** The report is a shareable artifact; the evidence is not. Mixing them means every report needs a legal review before it leaves the team.
- **Fail closed.** If the privacy gate cannot verify the output is quote-free, it emits nothing. No hidden patch, commit, push, issue, PR, release, upload or telemetry.

That last list is the security argument, not a feature list. A retrospective tool that can write to GitHub has the blast radius of a compromised CI token, because it reads untrusted text and produces actions. The ledger's design refuses that capability on purpose.

## How mature is requirement-ledger in 2026?

Honesty about the maturity of this space is part of the value, because the naming trend is real while the tooling is young.

| Signal | Status |
|---|---|
| `adand-91/requirement-ledger` | 125 stars, 8 forks, 4 watchers, 0 open issues, 38 commits from a single contributor, MIT |
| Release cadence | 7 releases, v0.1.0 on 2026-08-28 through v1.0.0 on 2026-09-09; last push 2026-09-16 |
| Distribution | Not on PyPI; git-clone-as-skill only |
| Identity drift | Repo renamed to `adand-91/gpt-6-astra-skill`, repositioned as "Astra Skill Optimizer"; CLI keeps the old name as a compatibility entry point |
| Term coverage | 0 exact-match Hacker News hits for "requirement-ledger"; 499 for "spec-driven development" |
| Adjacent work | `Foxfire1st/agents-remember` (27 stars, MIT, last push 2026-10-06) is a branch-aware, dual-revision "epistemic ledger" and control plane for coding agents |
| Academic validation | AfterVibe, 72 tasks, 5.06/6.0 regeneration score (5.74/6.0 strengthened) |
| Incumbent | `github/spec-kit` at 140,574 stars and 12,573 forks, last push 2026-10-07 |

The rename is worth pausing on, because it is the failure mode in miniature. A repository called "requirement-ledger" now resolves to one called "gpt-6-astra-skill" and markets itself as "Astra Skill Optimizer" — the original intent is preserved only as a compatibility shim in the CLI. Nobody decided to abandon requirements; the intent drifted one commit at a time, which is exactly what the tool exists to catch.

The same pattern shows up in research tooling. Dr. Claw (arXiv 2609.00365) persists a queryable task graph of roughly 14 nodes, a timestamped execution trace of roughly 14 transitions, and a decision-log brief of roughly 10 entries per run, while the bare command-line agent persists none of it. Two independent projects converging on "persist the intent, not just the artifact" is a stronger signal than either one alone.

## What is the getting-started checklist?

1. **Write the authority chain down before you install anything.** Spec → requirements → requirement tests → scenarios → implementation. If your team cannot agree on the order in one meeting, the tooling will not fix that.
2. **Run the 60-second synthetic demo first,** then `scan_transcript.py` on a real session. Look at the counts before you look at the conclusions.
3. **Add requirement files one pull request at a time,** mirroring the test paths, so structural coverage stays scriptable.
4. **Review the requirement diff before the code diff** in every PR. Empty requirement diff plus large code diff is your alarm.
5. **Never weaken a failing test.** Change the requirement first, explicitly, in the higher-authority document.
6. **Validate with a regeneration test** before you trust a recovered spec, and treat `unknown` attribution as a real answer that needs a human, not a gap to fill with a guess.

## FAQ: requirement ledger and vibe coding questions

### What is a requirement ledger in vibe coding?

A requirement ledger is a local, retrospective record of what a project actually required, reconstructed from artifacts the vibe-coding session already produced: the agent transcript, the test log, and a read-only Git snapshot. It inverts spec-driven development's direction — instead of writing a specification before prompting, you recover the specification afterwards from the corrections the user made while the work was happening. The anchor implementation is the MIT-licensed `adand-91/requirement-ledger`, which explicitly does not edit your project: it gathers evidence and produces a DRAFT repair plan that your own agent applies under review.

### Does a requirement ledger replace spec-driven development?

No, and treating it that way wastes both. Spec-driven development as Böckeler taxonomises it — spec-first, spec-anchored, spec-as-source — is prospective: the spec exists before the code and governs it. A requirement ledger is retrospective: it recovers intent from sessions where no spec was ever written, which is the majority of AI-assisted work in most organisations. Use SDD for planned features you are deliberately designing, and use a ledger for the accumulated drift in everything you already shipped, where a prospective spec is unavailable because the conversation that produced the code is the only remaining record.

### How many words should a recovered requirement document be?

Far fewer than a spec-kit run produces. Marmelab measured a spec-kit run for one small feature generating 8 files and 1,300 lines of text, which is the failure mode to avoid. AfterVibe's environmental grounding hypothesis gives the useful bound: a specification only needs to be concrete about undiscoverable facts such as decisions, thresholds and domain constraints, because an agent can discover build configuration, naming, module structure and API contracts by reading the repository. Recover the few things that exist only in someone's head, and let everything recoverable stay discoverable.

### How do I know a recovered requirement set is actually correct?

Test it by regeneration rather than by reading it. AfterVibe rebuilds the artifact from the recovered spec alone with a second blind agent and judges equivalence through flexible test execution, verification conditions extracted from the trajectory, and ground-truth alignment. Across 72 real-world vibe-coded tasks, recovered specs averaged 5.06 out of 6.0, rising to 5.74 out of 6.0 after iterative strengthening, while remaining diverse in implementation detail. The practical rule is that if a blind agent cannot rebuild a passing change from your recovered spec, the spec is under-specified — regardless of how complete it reads.

### Why must an AI never estimate the numbers in a retrospective?

Because a retrospective number gets quoted later as fact, and an invented count ends the enquiry that a missing count would have started. The `requirement-ledger` project makes this its central rule: every number comes from the script and the model never estimates one, with counting messages by eye described as "a failed retrospective." The human-factors literature makes the stakes concrete — Shaw and Nave at Wharton found people follow AI advice roughly 80% of the time even when it is wrong, so an authoritative-sounding wrong count is a documented hazard rather than a typo.

## Sources

- `adand-91/requirement-ledger` (repository, README, `v0.1.0`/`v0.1.1` READMEs, release notes, `scripts/scan_transcript.py`, `V0.1_CONTRACT.md`, `docs/PROJECT_GAPS.md`) — https://github.com/adand-91/requirement-ledger
- Current repository identity after the rename (`adand-91/gpt-6-astra-skill`, "Astra Skill Optimizer") — https://github.com/adand-91/gpt-6-astra-skill
- AfterVibe: What Remains When the Conversation Ends (arXiv:2607.09900) — https://arxiv.org/abs/2607.09900
- Beyond Code Generation: Reliability, Verification, and Cost Economics in the Agentic Software Development Lifecycle (arXiv:2609.04681) — https://arxiv.org/abs/2609.04681
- Dr. Claw: An AI Scientist Workspace for Vibe Research (arXiv:2609.00365) — https://arxiv.org/abs/2609.00365
- Debt Behind the AI Boom: A Large-Scale Empirical Study of AI-Generated Code in the Wild (arXiv:2603.28592) — https://arxiv.org/abs/2603.28592
- New Relic, 2026 State of AI Coding report with Hanover Research — https://newrelic.com/press-release/20260610
- JetBrains developer survey coverage (15,509 developers, May–July 2026) — https://techaiwire.com/articles/jetbrains-survey-agents-write-47-percent-of-code
- Faros AI, AI Engineering Report 2026: The Acceleration Whiplash (22,000 developers, 4,000+ teams) — https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways
- GitClear, The Maintainability Gap: 2026 AI Code Quality Research (623 million analysed changes) — https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- Mert Demirer, Leon Musolff and Liyuan Yang, Writing Code vs. Shipping Code: Productivity Effects Across Generations of AI Coding Tools (NBER Working Paper 35275, May 2026, revised September 2026; more than 500,000 GitHub developers) — https://www.nber.org/papers/w35275
- The Acceptance Gap: Why AI-Generated Code Still Fails to Become Shipped Work (Security Boulevard, 2026-09-29), carrying the Shaw and Nave citation and the Sonar 2026 developer survey figures — https://securityboulevard.com/2026/09/the-acceptance-gap-why-ai-generated-code-still-fails-to-become-shipped-work
- The Agentic Engineering Trends Report 2026 (the 11.4-versus-9.8 hours review/writing reversal) — https://saasrise.com/blog/the-agentic-engineering-trends-report-2026
- Birgitta Böckeler, Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl (spec-first / spec-anchored / spec-as-source taxonomy) — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- François Zaninotto, Spec-Driven Development: The Waterfall Strikes Back (the 8 files / 1,300 lines spec-kit example and the Kiro CRM example) — https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html
- `Foxfire1st/agents-remember` (branch-aware epistemic ledger and control plane for coding agents) — https://github.com/Foxfire1st/agents-remember
- `github/spec-kit` (the SDD incumbent: stars, forks and last-push date) — https://github.com/github/spec-kit

Repository and article counts were re-read from their primary sources during the Publisher's review pass on 2026-10-08; where a figure moved, the article shows the re-read value.
