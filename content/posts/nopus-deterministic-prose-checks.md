---
title: "Nopus Coding Agent Review: Deterministic Prose Checks for Clearer Responses"
date: 2026-10-01T00:26:26+00:00
tags:
  - nopus coding agent
  - deterministic prose checks
  - coding agent response clarity
  - nopus claude code plugin
  - ai slop detector for coding agents
description: "Nopus is a deterministic prose checker for coding agents: it measures a finished response offline and asks for one clearer rewrite. No LLM judge."
draft: false
cover:
  image: "/images/nopus-deterministic-prose-checks.png"
  alt: "Nopus Coding Agent Review: Deterministic Prose Checks for Clearer Responses"
  relative: false
schema: "schema-nopus-deterministic-prose-checks"
---

Nopus is a deterministic prose checker for coding agents: it measures a finished response with packaged English word data, and if several signals cross their thresholds it asks the same agent for exactly one clearer rewrite. There is no LLM judge, no network call, and no retry loop.

That is the whole product. `nopus` (npm `@syzom/nopus`, MIT, by GitHub user Vistyy) shipped on 2026-08-15 and reached its current feature set in five days across 14 commits. It supports exactly three hosts — Pi, Claude Code and Codex — and it does one thing: after an assistant finishes answering, it looks at the prose and decides, reproducibly, whether that prose was too hard to read. If so, the agent is told once to say it more plainly.

This review is about whether that narrow idea is worth installing in 2026, what its numbers actually mean, and where the many third-party write-ups about it have already started inventing features that do not exist.

## What Is Nopus, and What Does It Do to a Coding Agent?

Nopus is a response-quality hook, not a code-quality tool. It does not lint the code your agent wrote, it does not check imports, and it does not review your diff. It reads the *prose around* the code — the explanation, the plan, the summary — and intervenes only when that prose is measurably complex.

Mechanically it is three phases. First, prose extraction: the response is stripped of code blocks, inline code, URLs, file paths and table rows, so identifiers and snippets never enter the measurement. Second, multi-metric analysis: the remaining words are scored against packaged lexical tables. Third, conditional rewrite injection: if the policy fires, a single rewrite instruction is injected into the same agent's conversation.

The repository describes the target as answers that "disappear into abstract LLM babble" — the specific complaint being long load-bearing paragraphs, abstract vocabulary and overloaded phrases from recent models. The design constraint is that the decision must be reproducible and offline, which is the opposite of asking a second model to grade your prose.

## What Does "Deterministic Prose Check" Actually Mean?

It means the accept/rewrite decision is an arithmetic comparison over lookup tables, not a model judgment. Nothing is sampled, nothing is temperature-dependent, and no tokens are spent deciding whether to rewrite. The same prose at the same sensitivity always produces the same verdict — you can verify that by running the policy twice, which you cannot do with an LLM critic.

The linguistic data is real and pinned. Word rarity comes from SUBTLEX-US conversational frequencies (Brysbaert & New, DOI 10.3758/BRM.41.4.977, ISC licensed) and Norvig's Google Web Trillion Word Corpus counts. Abstractness comes from Brysbaert, Warriner and Kuperman concreteness ratings (DOI 10.3758/s13428-013-0403-5), where "database" scores high concreteness and "paradigm" scores low. Technical terms are down-weighted using The Carpentries Glosario (CC-BY-4.0). The style-cue list is checksum-pinned to claudisms.ai (SHA-256 `f4a09fa8...`).

The data is the heavyweight part of the package. `data/broad-web-word-counts.json` alone is 20.9 MB, conversational frequencies are 4.4 MB, concreteness ratings are 2.5 MB — roughly 28 MB of tables shipped inside an 11.9 MB plugin chunk, against only about 1,087 lines of source across 13 files plus ~1,005 lines of tests. You are installing a lexicon with a small engine attached.

## The Seven Measurements and Six Rewrite Signals

Nopus publishes its decision logic rather than hiding it. Seven quantities are measured:

| Measurement | What it captures |
| --- | --- |
| Uncommon wording | Share of words rare in conversational English |
| Very uncommon wording | Share of words rare even against broad web counts |
| Abstract vocabulary | Share of words rated low on human concreteness norms |
| Abstract sentences | Sentences whose abstract-word ratio is high |
| Noun/modifier stacks | Compressed strings of 3+ nouns and modifiers |
| Phrase load | Complex phrases per 100 words |
| Formulaic style cues | Distinct entries from the packaged claudism list |

Those feed six independent signal paths in `src/policy/decide-rewrite.ts`: sustained-abstractness, combined-complexity, stacked-phrasing, concentrated-complexity, pervasive-complexity, and style-cues. A rewrite fires when **any one** path is true.

The thresholds are public and numeric. At medium sensitivity, stacked-phrasing fires when the abstract ratio is at least 0.50, there are 3 or more noun stacks, and phrase load is at least 2.5 per 100 words. At high sensitivity the same path loosens to 0.48 / 3 / 2.0. That is unusually auditable for a tool this small: you can read exactly when your agent will be interrupted instead of trusting a black box.

Anti-over-triggering is built into the same file. Most paths require several measurements to cross together, a single rare word or dense phrase does not normally fire, and style cues need either two distinct cues or one cue supported by enough uncommon wording. The README is explicit that technical terms survive end to end: "InteractiveSessionHost stays InteractiveSessionHost".

## How Sensitive Is Nopus? The 5.3% / 9.9% / 18.6% Numbers

Three sensitivity profiles are published with observed rewrite rates measured on the author's own corpus:

| Sensitivity | Rewrites observed | Rate | Corpus |
| --- | --- | --- | --- |
| Low | 284 | 5.3% | 5,337 completed Pi responses |
| Medium (default) | 531 | 9.9% | 5,337 completed Pi responses |
| High | 995 | 18.6% | 5,337 completed Pi responses |

The corpus is 5,337 unique completed Pi assistant responses drawn from 515 session files, extracted 2026-08-14. The author labels these rates "a rough comparison because results vary by agent and task", and that caveat matters: the corpus is deliberately private. Files are mode 0700, artefacts 0600, and nothing is committed. The repo ships only a public regression fixture of frozen scalar measurements exercising "more than 5,000 policy inputs" — no response text, so no peer reproduction of the headline rates is possible from the repository alone.

Read those numbers as a design calibration, not as a benchmark you can check. What they do tell you honestly is the shape of the trade-off: one response in ten gets rewritten at the default setting, and roughly one in five at high.

## What Does the Agent Actually Receive?

When the policy fires, the agent does not get a vague "be clearer" nudge. `constructRewriteRequest` injects the specific evidence into conversation history — the measurements that crossed, with examples drawn from the agent's own response — plus an instruction to rewrite it more plainly.

Two optional behaviours change the feel of that interaction. **Extra-simple mode** (`extraSimple`, or `/nopus extra-simple on`) pushes the rewrite further toward short sentences. **Hide original response** is on by default in Pi (`pi.hideOriginalResponse=true`), and it removes the rejected response from the terminal transcript while leaving it in the session and model history.

That second setting is the one to think about. nopus does not undo the answer; it hides the first draft from the human reading the terminal. The agent's reasoning about your task is unchanged — you are buying readability, not correctness, and you are creating a small deliberate divergence between what you see and what the model still carries.

The rewrite-model evaluation (2026-08-16, `openai-codex/gpt-5.6-luna`, medium thinking) is the most concrete evidence that the intervention works: of 12 historical branches tried, 4 originals were selected by the medium policy. The normal rewrite passed the medium policy in 2 cases, the extra-simple rewrite in 3. Extra-simple compressed three substantial examples from 279 words to 45, 287 to 106, and 435 to 156. The author still notes that human review of what the rewrite omitted remains required — which is exactly the right caveat for a tool that shortens answers.

## How Do You Install Nopus on Pi, Claude Code, and Codex?

Three hosts, three install paths, one Node requirement. Everything needs Node.js 22+ and `node` on PATH.

| Host | Install | Mechanism |
| --- | --- | --- |
| Pi | `pi install npm:@syzom/nopus` | Extension with lifecycle hooks; hides the rejected response by default |
| Claude Code | `/plugin marketplace add Vistyy/nopus` then `/plugin install nopus@nopus` | Bounded Stop hook requesting one clearer response |
| Codex | `codex plugin marketplace add Vistyy/nopus` then `codex plugin add nopus@nopus` | Plugin; a new session is required so the plugin and skills load |

The user-facing surface is two bundled skills, `nopus-configure` and `nopus-simplify`, plus a command set: `/nopus status`, `/nopus check`, `/nopus on`, `/nopus off`, `/nopus extra-simple on|off`, and `/nopus hide-original on|off`. `nopus-simplify` exists because you do not have to wait for the hook — you can ask it to rewrite the immediately preceding response on demand.

Configuration lives in `$XDG_CONFIG_HOME/nopus/config.json` (resolved through `NOPUS_CONFIG`, then XDG, then platform defaults). Defaults are `complexitySensitivity: medium`, `includeEvidence: true`, `extraSimple: false`, `pi.hideOriginalResponse: true`. Every field has an environment override: `NOPUS_COMPLEXITY_SENSITIVITY`, `NOPUS_INCLUDE_EVIDENCE`, `NOPUS_EXTRA_SIMPLE`, `NOPUS_PI_HIDE_ORIGINAL_RESPONSE`.

One trust note specific to Pi: extensions run in-process with your full permissions, which makes any prose-checking extension an arbitrary-code dependency as well as a style tool. Pi's own documentation tells users to review package source before installing. The npm package has zero runtime dependencies and is small enough to read, which helps.

## The Evidence, Read Honestly: 5,337 Responses and 50 Labels

The most interesting thing about nopus's evaluation is that it publishes a result that does not flatter the tool.

| Evidence | Result |
| --- | --- |
| Corpus | 5,337 unique completed Pi responses, 515 session files, collected 2026-08-14 |
| Policy rewrite rates | 5.3% low / 9.9% medium / 18.6% high |
| Human labels | 50 labels on medium-sensitivity batches |
| Agreements | 41 |
| Wrong rewrites (accepted responses sent back) | 5 |
| Missed rewrites (responses marked for rewrite, not caught) | 4 |

Fifty labels is a small sample, and the author states plainly that the batches were sampled *at* the medium boundary and are "not a representative population sample". That means the directional read is roughly four in five correct on a deliberately hard batch — and, equally, that the numbers bound nothing about how the tool behaves on ordinary traffic in either direction.

Two structural limits follow. There is no published precision, recall or F1 for the policy anywhere in the repository. And the corpus being private means the headline rates cannot be audited independently. The project's honesty about this is unusual and should be rewarded, but the claim must still be sized to the evidence: one maintainer's private corpus, fifty human labels, and a rewrite model evaluated on four flagged originals.

## Four Limits You Should Know Before Installing

**English only.** SUBTLEX, Norvig's counts and Brysbaert's ratings are English datasets with no multilingual equivalents packaged. Non-English or code-switching responses produce meaningless metrics. For teams working in other languages this is a hard blocker, not a tuning problem — though a 2026 wave of small variants (a Korean `prose-lint`, a German `schreibwaechter`) shows the gap being filled from the edges.

**It cannot save you tokens.** Nopus evaluates completed responses, so the flagged babble has already been generated and billed. Any cost saving is human reading time and transcript clutter. Anyone shopping for a cost-reduction tool is looking at the wrong product.

**One rewrite, maximum.** That is the best engineering decision in the package: a bounded Stop hook that requests exactly one clearer response cannot create the infinite politeness loop a critic-model hook can. The price is that a response which is bad twice stays partly bad — nopus will never chase it further.

**Maintenance risk.** Two npm versions (1.0.0 on 2026-08-15, 1.1.0 on 2026-08-16), 14 commits, and the last commit on 2026-08-19T16:25:13Z — roughly six weeks of silence as of this writing. The only open issue is #1 "Add OpenCode plugin support" (opened 2026-09-01, zero comments), and the most requested integration remains unbuilt. Star counts continue to drift up (repo at 296 stars on 2026-10-01; third-party snapshots in the same period read 264/276/287), but an unmaintained extension that runs in-process with full permissions is a dependency to pin and read, not infrastructure.

Distribution context is worth stating plainly, because it explains the adoption picture. Host tools are enormous — `@openai/codex` runs 25,653,416 weekly npm downloads, `@anthropic-ai/claude-code` 14,495,496, and `@earendil-works/pi-coding-agent` 4,316,299 in the same window — while `@syzom/nopus` itself had 34 downloads in its last week and 204 in the last month (window 2026-08-31 to 2026-09-29). Discoverability came from agent-package catalogs (agentmods, pi.dev, claudepluginhub) rather than developer-tool press: Hacker News has no nopus story at all, with an Algolia URL-restricted query returning zero hits.

## Nopus vs write-good, alex, Vale, and avoid-ai-writing

The prose-linting family is old and much larger, but none of it was built to interrupt an agent.

| Tool | Stars | npm downloads/month | Output | Where it runs |
| --- | --- | --- | --- | --- |
| write-good | 5,092 | 266,386 | Suggestions list | Human documents, CI gate |
| alex | 5,102 | 184,122 | Warnings list | Human documents, CI gate |
| Vale | 6,175 | — (standalone) | House-style violations | Human documents, CI gate |
| proselint | 4,579 | 314 | Warnings list | Effectively dormant |
| avoid-ai-writing | 4,803 | 2,092 (detector pkg) | AI-tell detection | Content, not agent responses |
| **nopus** | 296 | 204 | **One rewrite instruction** | **Agent Stop hook / response** |

The distinction is the output type. Existing linters measure prose and return a report you read; nopus measures prose and returns an instruction the *agent* acts on. That is a new wiring of an old idea, and it is the only reason the project is interesting despite being three orders of magnitude smaller than write-good in usage.

The closer modern rival is `avoid-ai-writing` (4,803 stars, detector package published 2026-08-02, last modified 2026-09-23), which targets AI-writing tells in published content and explicitly defers house style to Vale. It answers "does this read like AI wrote it?" Nopus answers "was this response too hard to read — rewrite it". Different job, different failure modes.

For the general linter lineage and its CI wiring, see the [agent skills supply chain security guide](/posts/agent-skills-supply-chain-security-guide-2026/), which covers how these extension packages get discovered and trusted. If you are building the hooks yourself rather than installing one, the [Claude Code hooks guide](/posts/claude-code-hooks-guide-2026/) documents the lifecycle events nopus runs on, and the [Codex plugins guide](/posts/codex-plugins-integrations-guide-2026/) covers that host's plugin loading.

## Do Third-Party "Nopus Reviews" Get the Facts Right?

Mostly no, and this is worth documenting because it is now typical of agent-tooling search results.

One aggregator page claims nopus implements a paper "Reducing Hallucinations in Coding Agents via Prose Constraints" (2026, arXiv:2607.89123). That arXiv ID returns "Article not found" (404), and no such paper is referenced anywhere in the repo. The same page invents a browser runtime, a CDN bundle, a CLI wrapper, an `@vistyy/nopus` package name, "12+ prose/coding rules" that block "I think"/"maybe", code-block fencing validation, 98% coding-agent specificity, 67% hallucination reduction, and three community adapters including a Slack bot. None of it exists: there are 7 measurements and 6 signals, three host integrations, no browser target, and no hallucination-rate claim anywhere in the source.

Other write-ups are merely stale — one shows 154 stars against an actual 296 — and at least one openly labels its own metrics "heuristic approximations ... not authoritative measurements".

The lesson generalizes beyond nopus: for agent tooling, go to the repository and the registry. Both are cheap to read here, and the README is unusually specific about thresholds, defaults and provenance.

## Does the Concept Have Real Academic Support?

The idea behind nopus — that verbosity is a measurable defect rather than a style preference — does, even though nopus itself has no published paper.

"Verbosity Bias in Preference Labeling by Large Language Models" (arXiv:2310.10076, 2023) shows LLM judges prefer more verbose answers of similar quality, which is the reason a *deterministic* check is a legitimate design choice rather than an odd one. "Verbosity != Veracity" (arXiv:2411.07858, 2024) documents verbosity compensation as a learned behaviour. Most directly, "Verbosity-Aware Rationale Reduction" (arXiv:2412.21006, ACL 2025 Findings) removed redundant reasoning sentences for an average +7.71% task performance while cutting token generation by 19.87% — trimming verbosity can improve accuracy, not just readability.

The developer-demand side is equally well measured. Stack Overflow's 2025 survey found 46% of developers distrust AI accuracy against 33% who trust it, with 66% naming "almost right, but not quite" as their top frustration. Sonar's 2026 State of Code survey (1,100+ respondents) found 96% do not fully trust that AI-generated code is functionally correct, and only 48% always check AI code before committing. Agent adoption roughly doubled to 59% while trust fell to 29%. Deterministic, auditable output guards are exactly the category that trust gap creates demand for.

## Verdict: Who Should Install Nopus Today?

Install it if you use Pi, Claude Code or Codex, you are genuinely annoyed by lecture-hall framing and abstract "capability / governance" prose in agent answers, and you are comfortable reading ~2,000 lines of TypeScript before running it in-process. Keep the default medium sensitivity for a week, watch the rewrite rate, and pin the version — the project has been quiet since 2026-08-19 and you do not want a silent upgrade changing how often your agent interrupts itself.

Wait if any of these describe you: you work in a language other than English; you want token or cost savings; you need published precision and recall before adopting a policy that edits your agent's output; or you run transcript-based audit trails, in which case Pi's hidden-original default needs an explicit decision rather than a default.

Skip it entirely if what you actually want is house style enforcement — that is Vale, and Vale has been maintained since 2016 with a fraction of the uncertainty. Nopus is a well-scoped, unusually honest, single-maintainer experiment: the first prose linter wired to rewrite an agent's own answer, with a real corpus, a small human-label set, and a public threshold table you can audit. That is worth 34 weekly downloads and a careful look, not a site-wide rollout.

## FAQ

**Is nopus an LLM or does it call one?**
No. It is a deterministic checker over packaged lexical tables — no model is invoked to decide whether to rewrite, and no network call is needed for the decision. That is why the same response and sensitivity always produce the same verdict, and why the tool cannot drift the way a prompt-tuned critic can. The only model involved is your agent itself, which performs the rewrite.

**Does nopus work outside Pi, Claude Code and Codex?**
Only those three are supported. Pi installs through `pi install npm:@syzom/nopus`, Claude Code through its plugin marketplace, and Codex through `codex plugin marketplace add`. OpenCode support is issue #1 and is still unbuilt. Porting it means re-implementing the Stop-hook or extension lifecycle against another harness, plus supplying your own host integration for the one rewrite request.

**Does it change the answer or only the wording?**
Only the wording of the response, and only the visible response. The rewritten answer replaces the reply you read, but the rejected version stays in the session and model history — and in Pi it is merely hidden from the terminal transcript by default, not deleted. The agent's understanding of your task is unchanged, so nopus buys readability, not correctness.

**Does nopus save tokens or reduce cost?**
No, and this is the most common misconception about it. Nopus evaluates responses that have already been generated and billed, so the flagged verbosity has already been paid for. The savings are human reading time and a cleaner transcript. There is a second-order effect — fewer tokens in future context if you keep shorter responses in history — but that is not what the tool measures or promises.

**Can nopus get stuck rewriting forever, or fire on technical terms?**
It cannot loop: the design requests exactly one automatic rewrite, so a response that fails the policy twice is simply left as it is. On false positives, the defence is explicit — code blocks, inline code, URLs, file paths and table rows are stripped before measurement, established computing terms are down-weighted, and most decision paths require several measurements to cross together. The realistic failure mode is not identifiers but legitimately abstract discussion (authorization models, governance, capability boundaries) being asked to simplify.
