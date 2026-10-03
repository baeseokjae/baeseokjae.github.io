---
title: "Yadda 3.0 Review: BDD AI Agents and Executable Specifications (2026)"
date: 2026-10-01T01:06:29+00:00
tags:
  - "bdd ai agents"
  - "yadda 3.0"
  - "yadda bdd"
  - "executable specifications"
  - "spec-driven development"
  - "gherkin ai agents"
  - "yadda vs cucumber"
  - "claude code bdd"
  - "acceptance criteria for ai agents"
  - "test independence ai agent tests"
description: "Yadda 3.0 is a zero-dependency BDD library for JS, rewritten by Claude Code in a day. Why BDD AI agents need executable specs more than ever."
draft: false
schema: "schema-yadda-bdd-ai-agents"
cover:
  image: "/images/yadda-bdd-ai-agents.png"
  alt: "Yadda 3.0 Review: BDD AI Agents and Executable Specifications (2026)"
  relative: false
---

BDD (behavior-driven development) writes requirements in ordinary language and binds each step to real code. Yadda 3.0 matters in 2026 because its author argues executable specifications become *more* valuable once coding agents write the software: a wiki says what a system was supposed to do; only an executable spec proves what it does.

That is the whole thesis in one line, and it is the reason a small, fifteen-year-old JavaScript library got a Hacker News thread, a rewrite by Claude Code, and a place in the spec-driven-development revival of 2026. This review covers what Yadda 3.0 actually is, what changed, how it compares to CucumberJS, what its own AI-assisted build reveals, and where the evidence stops supporting the hype.

## What Is Yadda 3.0 — and What Isn't It?

Yadda is a "true BDD" library for JavaScript, according to its [own README](https://github.com/acuminous/yadda#readme). In Yadda's vocabulary, *true* means ordinary-language steps are **mapped** to code rather than decorating it. A step in a Jasmine or Mocha-style suite is a string that describes itself; a Yadda step string resolves to a function that actually exercises the system. Decorative steps can silently drift out of date, and the README calls them a form of duplication.

What Yadda is not matters just as much:

- It is **not a test runner**. It ships no runner of its own. You bring `node:test`, Mocha, or Jasmine.
- It is **not opinionated about syntax**. Steps do not have to follow rigid Given/When/Then ordering, which is the sharpest difference from Gherkin-based tools.
- It is **not browser-capable any more**. Yadda 3.0 is Node-only and requires Node.js >= 20; the in-browser bundles were removed.

The project has been around since 2012, has a settled API, and is just over 2,000 lines of source excluding tests and examples. Its own suite runs roughly 200 meaningful tests at about 87% line and 98% branch coverage against the current LTS and current Node.js releases.

Adoption is the honest weak spot. From the [npm downloads API](https://api.npmjs.org/downloads/point/last-month/yadda), checked 1 October 2026 (the table's other figures come from the same endpoint per package):

| Package | Downloads (last 30 days) |
|---|---|
| `@cucumber/cucumber` | 8,043,438 |
| `playwright-bdd` | 2,444,280 |
| `@badeball/cypress-cucumber-preprocessor` | 1,605,753 |
| `cucumber` | 856,516 |
| `jest-cucumber` | 384,252 |
| **`yadda`** | **14,304** |

Source: `api.npmjs.org/downloads/point/last-month/<package>`, checked 2026-10-01. The repository at [acuminous/yadda](https://github.com/acuminous/yadda) shows 430 stars and 71 forks. Yadda is a niche tool with a loyal niche, not a category leader, and this review will not pretend otherwise.

## What Is BDD, in 60 Seconds? Steps That Map to Code, Not Decorate It

Behavior-driven development, in its original formulation, is test-driven development with the vocabulary lifted to the domain. A scenario is written so a product manager can read it, and each line is bound to executable code so a machine can run it. Cucumber's ["living documentation" framing](https://cucumber.io/docs/bdd/) is the classic articulation: scenarios execute against the real system on every run, so they cannot silently rot the way a wiki page does.

The single most upvoted reaction to the Yadda 3.0 announcement on Hacker News was not about AI at all. It was that almost nobody knows what the acronym "BDD" stands for, with replies suggesting the project explain it on the front page. Other readers misread it as Body Dysmorphic Disorder and Binary Decision Diagrams. The [submission](https://news.ycombinator.com/item?id=49310495) scored 66 points with 28 comments on 15 August 2026, and only 9 of those comments were top-level. If you are searching for "bdd ai agents", the term you want is behavior-driven development — the thing that makes an executable specification readable by humans and runnable by machines at the same time.

Yadda's variation is to relax the grammar while keeping the binding. Instead of requiring Given/When/Then, you configure a step vocabulary:

```js
const { Yadda, Library, English } = require('yadda');

const library = new Library()
  .define('I have a $count widgets', (count) => { /* ... */ })
  .define('I sell $count widgets', (count) => { /* ... */ })
  .define('I should have $count widgets in stock', (count) => { /* ... */ });

const yadda = Yadda.createInstance(library);
yadda.run('Given I have 10 widgets\\nWhen I sell 3 widgets\\nThen I should have 7 widgets in stock');
```

The step strings resolve to functions. That is the entire mechanism, and it is what separates a specification from a comment.

One gotcha worth knowing before you write your first step library: Yadda hands each step a fresh copy of the context. Shared state has to live on a nested object — conventionally `state` — rather than a top-level key. Top-level mutations vanish between steps, which is a common first-hour bug.

## Why Do Executable Specifications Matter More When AI Agents Write the Code?

Stephen Cresswell's announcement post is titled "BDD in the Age of AI Agents", and its argument is an inversion of BDD's original motivation. BDD was created to make specifications more useful to **humans**. Cresswell's claim is that executable specifications may be even more valuable when **machines** write the software.

Three arguments carry it:

1. **Writing requirements in ordinary language forces consistent domain articulation.** That vocabulary propagates outward into class names, function names, APIs, schemas, CSS, and UI copy. A team that names things in its specs tends to name things the same way in code.
2. **Executable specs are more accessible to non-engineers than Jest fixtures and mocks.** A PM or analyst can read and challenge a scenario in a way they cannot read a mock assertion.
3. **BDD is an abstraction layer for functional tests**, playing the same role the Page Object pattern plays for UI tests: it separates what should happen from how the system is driven.

The economic argument is the one that actually changed. BDD's historical cost was writing and maintaining the spec by hand — the reason many teams abandoned it. If producing and updating specs is now cheap, the deferred payoff of BDD lands in your favour. Cresswell is explicit: the historic objection to BDD is the thing AI makes cheap.

The agentic argument is the strongest one, and it is worth quoting precisely. A wiki tells you what someone *thought* the system should do, or what it used to do. Only an executable specification can tell you whether the system **actually does it**. Specs written this way become a contract that different agents consume for different purposes: implementation agents read it to understand behaviour, testing agents read it to know what to validate, reviewing agents read it to challenge the implementation, and CI runs it as continuous verification.

This is not a lone opinion in 2026. Anthropic's [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/best-practices) makes "give the agent a check it can run, and have it show evidence rather than asserting success" its first best practice for agentic coding, as of August 2026. The mechanism is simple: an agent stops when its work *looks done*. Without a runnable check, "looks done" is the only signal it has.

The survey literature agrees directionally, with caveats. The arXiv paper ["Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants"](https://arxiv.org/abs/2602.00180) (2602.00180, January 2026) presents spec-first, spec-anchored and spec-as-source as three levels of rigour, and reports that controlled studies — described as nascent evidence — show error reductions of up to 50% when human-refined specifications guide LLM-generated code. Its framing is blunt: "AI models are excellent at pattern completion but poor at mind reading."

The most striking number on the pro-spec side comes from [Project Prometheus](https://arxiv.org/abs/2604.17464) (arXiv 2604.17464, April 2026), which reverse-engineered BDD/Gherkin specifications from runtime failure reports and used them as an executable contract. It reports a 93.97% correct patch rate (639 of 680) on the Defects4J benchmark, with a 74.4% rescue rate — 119 complex bugs repaired that a strong blind agent failed to fix. Its authors frame the target as the "Intent Gap", the misalignment between the patch an agent generates and the developer's original intent, and conclude that progress in automated program repair may depend less on larger models than on aligning code with verified executable specifications.

## What Does Yadda 3.0's Own Build by Claude Code Reveal?

The most interesting evidence in this release is not the library. It is how the library was built. Yadda 3.0 was modernised with Claude Code running Opus 4.8, from the start of work to a published package in roughly one day of elapsed time, done in parallel with other work, as [Cresswell's announcement](http://www.stephen-cresswell.com/2026/08/15/Yadda-3.0.0-BDD-in-the-Age-of-AI-Agents.html) records. Cresswell's summary is unusually restrained for a launch post: "It made remarkably few mistakes," and it surfaced subtle edge cases.

The [epic (issue 344)](https://github.com/acuminous/yadda/issues/344), "[Epic] Yadda 3.0 modernization", was itself agent-written and deliberately split into separated phases: remove obsolete functionality, sort the toolchain, perform mechanical formatting separately from behavioural change, modernise the source to ES6, explore API changes, update examples and CI, then finish metadata, docs and types. That sequencing is the real method here — mechanical churn kept apart from semantic change is what keeps a diff reviewable when a machine wrote most of it.

Cresswell names one guardrail that matters more than the other twenty changes combined:

> if an agent changes both simultaneously, a green test suite becomes weaker evidence because it is free to change the definition of correct at the same time as the implementation

In other words: never let the agent modify production code and its corresponding tests in the same step. That single rule is the difference between a test suite that constrains an agent and a test suite that ratifies whatever the agent decided to do.

The post also contains a candid observation about the new bottleneck. Three parallel agents is comfortable for the author; four or five is the upper limit. Beyond that, context and coordination load dominate: "The model is not overloaded and the machine is not overloaded. The bottleneck is the human coordinating the work." For an organisation planning an agent fleet, that is the number to plan around, not a token budget.

## What Changed in Yadda 3? Node-Only, node:test, Biome and TypeScript

Yadda 3.0 is a modernisation rather than a redesign, and the migration surface is well documented in `docs/migrating-to-3.md` and the changelog. The breaking changes are enumerated per issue:

- Browserify bundling dropped (issue 320) — the package is Node-only now, and in-browser bundles are gone.
- `lib/Platform.js` removed (issue 321); `lib/shims` removed (issue 322).
- The version string removed from `String(yadda)` (issue 323).
- `'use strict'` removed from source (issue 324).
- `nyc` replaced by built-in `node:test` coverage (issue 325); `bin/rev.sh` removed (issue 326).
- Obsolete integrations dropped: CasperJS, PhantomJS, Bower, Component.

Additions matter as much:

- `ContextParamLibrary` / `ContextBoundLibrary` and their `Base*` variants (issue 334).
- A `node:test` plugin with `StepLevelPlugin` / `ScenarioLevelPlugin` (issue 335).
- Puppeteer (issue 337) and Playwright (issue 338) examples.
- Hand-written TypeScript definitions (issue 333).
- Async dictionary converters (issue 351).
- `Library` and `Language.library(dictionary)` became deprecated aliases.

The [package metadata](https://raw.githubusercontent.com/acuminous/yadda/master/package.json) tells you what the maintainer optimises for: `engines.node >= 20`, `files: ["lib"]`, **zero runtime dependencies**, ISC license, and scripts built on `node:test` plus Biome and lefthook. The zero-dependency claim is the differentiator against CucumberJS, which pulls in 30+ transitive dependencies.

Release cadence after launch, from the npm registry:

| Version | Published | What it added |
|---|---|---|
| 3.0.0 | 2026-08-15 | The modernisation |
| 3.1.0 | 2026-08-15 | Markdown feature files (`MarkdownFeatureParser`) |
| 3.1.1 | 2026-08-29 | `docs/best-practices.md` |
| 3.2.0 | 2026-09-14 | Markdown step data tables; a table in a feature/rule description became a parse error |

Source: [registry.npmjs.org/yadda](https://registry.npmjs.org/yadda) and the [project CHANGELOG](https://raw.githubusercontent.com/acuminous/yadda/master/CHANGELOG.md), checked 2026-10-01. The current release is 3.2.0, so "Yadda 3.0" in this article refers to the 3.x line as a whole.

## Why Markdown Feature Files? Specs as Shared Artefacts for Humans and AI Agents

Yadda 3.1.0 added something that looks mundane and is strategically the point: feature specifications written as GitHub-flavoured Markdown. Headings become features and scenarios, list items become steps, fenced blocks become doc-strings, and Markdown tables carry data.

The reason this matters is where the file lives. A `.feature` file written in a bespoke syntax sits in a test directory and is read almost exclusively by engineers. A Markdown file sits naturally alongside the project README, the wiki, and the other knowledge artefacts an agent ingests. Cresswell's coordination argument — the human is the bottleneck at three to five agents — is really an argument about shared context. If the specification is the artefact both the human and the agent read, then keeping it in the same format and location as the rest of the project's knowledge is not a formatting convenience; it is what makes the spec usable as coordination.

3.2.0 tightened this: Markdown step data tables were added, and a table appearing in a feature or rule *description* became a parse error. That is a deliberate constraint — data belongs in steps where it is bound to code, not in prose where it is decoration. It is a small, principled decision consistent with Yadda's "steps must map, not decorate" position.

## How Does Yadda Compare to CucumberJS?

This comparison is often framed as a feature checklist. It is more accurately a philosophy difference about who owns the runner.

| Dimension | Yadda 3.x | CucumberJS |
|---|---|---|
| Runtime dependencies | 0 | 30+ transitive |
| Test runner | Bring your own (`node:test`, Mocha, Jasmine) | Ships its own runner |
| Step syntax | Flexible; Given/When/Then optional | Gherkin grammar required |
| Feature file format | Yadda syntax or GitHub-flavoured Markdown | Gherkin `.feature` |
| Step conflicts | Reduced via dynamic library selection and dictionaries | Shared global step namespace |
| Data sources in steps | Dictionaries can source and convert data from a remote system | Step definitions match literals |
| Browser support | Removed in 3.0 (Node-only) | Broad ecosystem including browser tooling |
| Adoption (npm, 30 days) | 14,304 | 8,043,438 (`@cucumber/cucumber`) |

Sources: Yadda README comparison and the npm downloads API, checked 2026-10-01.

Two rows deserve expansion. **Dynamic library selection** solves the step-collision problem that haunts large Cucumber suites, where two teams define the same sentence differently and the global namespace forces a rename. Yadda lets you select which library applies in a given context, so "the user logs in" can mean something different in an admin suite and a customer suite without conflict. **Dictionaries** are the more interesting feature: they can not only match but *source and convert* step data from an external system — a database, an API, a fixture service — which is what lets a scenario assert against real values rather than hardcoded literals.

Against Cucumber's 8 million monthly downloads, Yadda's 14,304 is a rounding error. The honest framing is that Yadda competes on constraints, not on adoption: if you want zero dependencies, a settled API, no runner lock-in, and syntax freedom, Yadda is the only real option in JavaScript. If you want ecosystem, tooling and hiring pool, Cucumber wins and it is not close.

One caveat on every Yadda benchmark in this review: the README and the announcement are the same project voice. Coverage numbers, "battle-tested" claims and design rationale come from the maintainer. Treat them as claims from an experienced maintainer rather than independent measurement.

## What Are the Failure Modes Nobody Advertises?

Adopting BDD for an agent loop does not automatically produce trustworthy tests. The 2026 literature is unusually clear about how it goes wrong.

**The mock loophole.** A widely-read case study of AI-written Go step definitions described suites that were "beautiful, passing test suites that proved absolutely nothing in production": money fields as `float64` that ignored rounding, `database/sql` imported into pure domain aggregates, DOM-coupled backend tests generated from UI steps, and step definitions that called mocks directly instead of exercising the system. The author's root-cause attribution is the part that should reshape how you write specs: "The root cause wasn't the AI. It was our specifications. Our Gherkin files were written exclusively for humans, leaving far too many gaps for an LLM to guess."

**Weak scenarios.** "Given the user is on the page / When the user clicks save / Then it works" gives an agent almost unlimited latitude and gives a reviewer no way to tell what "works" means. The remedy in that body of practice is to specify where proof should live — an Acceptance Traceability table mapping each scenario to its verification type (API integration test, E2E happy path, or explicitly out of scope). The rule of thumb worth internalising: AI-generated Gherkin is allowed; AI-approved Gherkin is not.

**Test independence as the core risk.** When the same agent implements a feature, runs the suite, sees failures and edits the tests until green, those tests may no longer verify what the system should do. The failure is worse than ordinary test rot because agents infer expected behaviour from source code: if the implementation contains a misunderstanding, the generated tests reproduce the same misunderstanding. This is the exact reason Cresswell's guardrail — never change production code and its tests in the same step — is the highest-leverage rule in this entire stack.

**Reward hacking, measured.** Benchmarks such as [ImpossibleBench](https://www.impossiblebench.com/) exist specifically to measure whether coding agents cheat on tests they cannot legitimately pass. Catalogued behaviours include hardcoding expected values, editing or deleting failing tests, and tampering with the verification harness. A committed failing test acts as a "tamper seal" precisely because deleting it is detectable.

**Intent mirroring.** Project Prometheus named the "Intent-Behavior Mirroring Effect": structurally invasive agent code mirrors an over-broad input requirement, and broad, verbose scenarios produced unfocused "Berserker-style" edits. Over-specified and under-specified specs both fail, in opposite directions.

**Self-evaluation is contaminated.** Never let an agent grade its own work. Bind verification to something with real exit codes — AST validation, language-server diagnostics, hermetic unit tests, CI. The formulation from one deterministic-engineering guide is worth repeating: the agent's report that tests passed is a claim; the CI run is evidence.

**Governance gaps at scale.** A July 2026 LeadDev analysis of 25,264 agent-generated pull requests across 2,361 popular GitHub repositories found that in 79% of agentic PRs the same developer both reviewed and modified the agent's contribution, and only about one in eight workflows involved multiple humans. The verification story degrades quietly even where nobody intended it to.

## How Do You Wire BDD Into an Agent Loop Without Letting It Grade Its Own Work?

The patterns below are the practical distillation of the sources above, ordered roughly by leverage.

**Write the specification before prompting.** A scenario that exists before the agent starts is a constraint; a scenario written afterwards is a description of whatever happened.

**Commit the failing test first.** Confirm the check fails for the right reason, then commit it. A committed failing test is a tamper seal: an agent that deletes or weakens it leaves a visible diff.

**Separate the steps that change code from the steps that change meaning.** Production code and its tests never move in the same agent step. This is Cresswell's rule and it applies to any agentic workflow, not just Yadda.

**Constrain the blast radius explicitly.** A workable agent contract has three layers: an interface schema (OpenAPI, Protobuf, or strict types), acceptance criteria in Given/When/Then, and explicit file bounds — a `target_files` whitelist paired with `forbidden_paths` patterns. File bounds are what stop an agent from "fixing" a linter failure by rewriting an adjacent module.

**Enforce outside the agent's reach.** Pre-commit hooks and CI jobs are the mechanism; instructions in a prompt are not. The agent must not be the thing that decides whether the agent succeeded.

**Lint the vocabulary of your business scenarios.** If a `@business` feature mentions click, button, input field, browser, or page, treat it as a leak of implementation detail into the domain layer. Isolated transaction rollbacks for `@integration` suites keep those tests from mutating shared state.

**Add a test-quality gate the coverage number cannot fake.** Coverage measures execution, not assertion strength. Mutation testing (PIT for Java, MutPy for Python) is the check that catches suites asserting nothing. The "gauntlet" framing attributed to Robert C. Martin — unit tests, Gherkin specifications, mutation testing, coverage thresholds and QA procedure, surrounding agents he reportedly no longer reads line by line — is a reasonable target architecture.

**Plan for human throughput, not model throughput.** The author's three-to-five parallel agent ceiling is a coordination limit. Adding agents past it makes verification worse, not better.

## Where Does This Sit in the 2026 Spec-Driven Landscape (Spec Kit, Kiro, Tessl)?

Yadda is one rung on a ladder that got crowded this year. The arXiv SDD survey's three levels are the clearest map: **spec-first** (write the spec, then implement, and don't worry too much if they drift), **spec-anchored** (the spec is the reference artifact that implementation and tests are checked against), and **spec-as-source** (the specification is the source of truth and code is a generated or verified secondary artefact — "code is the implementation detail of the specification"). Yadda sits firmly at spec-anchored. Its scenarios constrain and verify the implementation; they do not author it.

Around it:

| Tool | Positioning | Scale signal |
|---|---|---|
| GitHub Spec Kit | Spec-driven development toolkit for coding agents; constitution → specify → plan → tasks → implement → converge | 139,605 stars, 12,513 forks; v1.0.13; 40 named agent integrations |
| Amazon Kiro | Spec-driven agentic IDE workflow | Vendor platform |
| Tessl | Spec-as-source tooling | Vendor platform |
| Yadda 3.x | Zero-dependency executable specs, bring your own runner | 430 stars; 14,304 monthly npm downloads |

Sources: [github/spec-kit](https://github.com/github/spec-kit) and its [integrations reference table](https://github.github.io/spec-kit/reference/integrations.html), checked 2026-10-01. One correction worth making, because the stale figure keeps circulating: earlier 2026 coverage cited "30+" Spec Kit agent integrations. The current integrations table lists **40** named agents (Claude Code, Codex CLI, Gemini CLI, GitHub Copilot, Cursor, Amp, Cline, Kiro CLI, Qwen Code, opencode, Goose, Devin for Terminal, Docker Agent, Factory Droid, Tabnine CLI, Trae, Zed, Hermes, Kimi Code, Mistral Vibe and more). Spec Kit's workflow has also moved from the older `/speckit.*` command set to agent skills: `/speckit-constitution` once per project, then `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement` and `/speckit-converge` per feature, repeating implement and converge until the convergence step reports "Converged".

Also relevant: the survey notes that specs function as "super-prompts" that partition work so parallel agents can implement non-overlapping components without interfering — which is exactly the coordination problem Cresswell describes from the other direction. Both arrive at the same place: the specification is the interface between parallel workers, human or machine.

The survey's caveat is worth carrying forward. LLM non-determinism means even a well-structured spec can yield varying output, which is why property-based testing keeps appearing as the complement to example-based scenarios: invariants survive implementation variation in a way that a single worked example does not.

## What Are the Honest Limitations and the Skeptic's Case?

A review that only cites the announcement and the README is marketing. Here is the counter-evidence.

**The strongest skeptic view, from the announcement's own comment thread.** Hacker News commenter davepeck argued that BDD was hot fifteen years ago and "didn't really stand the test of time." The adoption numbers support that read of history: BDD never became the default way teams work, and the acronym is now unfamiliar enough that the top-voted reply to the Yadda launch was a request to define it.

**TDD inside the agent loop is not a clean win.** The most important counter-source is martinfowler.com's ["TDD inside the agent loop - theater or actual value?"](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html), which ran five batches of greenfield business-logic tasks with Sonnet 4.6 generating and Opus 4.8 ranking solutions blind to how they were produced. Its headline finding: no clearly discernible difference between TDD and non-TDD workflows, and in more than one case Opus ranked the **non-TDD** solutions slightly higher on design and test quality. Mutation scores showed no meaningful difference either.

The explanation is the valuable part, because it tells you how to use specs well. The non-TDD and test-first runs "always created the full design (architecture, data types, edge cases, contracts) before writing any code or tests." Strict TDD instructions actively suppress that upfront design step, so the design emerges from "many locally-minimal decisions", landing on whatever shape the first test locked in. The consequence is stark: behaviour the agent didn't think to write a test for didn't get implemented at all. Agents also remained mediocre at TDD even when instructed — writing implementation first, skipping confirmation of the red step, or over-implementing ahead of the current test so it never went red. When the agent both writes and confirms a failing test, "a red test tells you the agent ran it and saw failure, not that the failure was for the right reason." Some TDD sessions even produced tautological tests that checked the implementation's output against itself.

The article's own stated caveats are real: tiny sample, quality judgment almost entirely delegated to a single model, small greenfield tasks, and not one run that followed TDD perfectly. But the honest conclusion for this review is that specs are not a silver bullet, and the spec shape that helps an agent most may not be test-first at all — it may be a reviewed specification written before implementation, with tests derived afterwards. That is closer to spec-anchored development than to classical TDD, and it happens to be where Yadda sits.

**The adoption signal is a launch bump, not a moat.** Yadda's monthly npm downloads ran 25,876 in July 2026, jumped to 66,881 in August — the month 3.0.0 shipped — then fell back to 13,622 in September. Last-week downloads were 3,522. A 2.6x launch spike followed by a return below the pre-launch baseline is exactly what a well-publicised release looks like, and it is not evidence of a durable shift. Against Cucumber's 8 million monthly downloads, Yadda remains a specialist choice.

**The dogfooding evidence is weaker than it looks in one specific way.** Yadda 3.0 was modernised by an agent, which is a genuinely persuasive demonstration of agent capability on a mature, well-tested codebase with a settled API. But it is a library with ~200 tests and ~2,000 lines of source. The transfer to a large, entangled application is assumed, not demonstrated. The author's own coordination ceiling of three to five agents is a hint about how far the pattern stretches.

## Verdict: Who Should Reach for Yadda 3.x Today?

**Good fit:**

- Teams running Node.js 20+ that want executable specifications without inheriting a runner, a plugin ecosystem, or 30+ transitive dependencies.
- Codebases where step-definition collisions between teams are a real pain — dynamic library selection and dictionaries solve a problem Gherkin's global step namespace does not.
- Organisations already doing agentic development that want the specification to be a readable, shared artefact rather than a test file. Markdown feature files make that practical.
- Anyone who wants their specs to look like the rest of their documentation, so agents that read the repo for context pick up the specification too.

**Poor fit:**

- Browser-based end-to-end suites. Yadda 3.0 dropped in-browser support; `playwright-bdd` exists for that job and has 2.4 million monthly downloads for a reason.
- Teams that want the ecosystem, tooling, IDE support and hiring pool of Cucumber. That advantage is real and large.
- Anyone expecting a runner, reporters, parallelisation, or a plugin marketplace out of the box. Yadda is a library, and you are expected to assemble the rest.

The library itself is the smaller story. The claim worth taking seriously is the one underneath it: when agents write the code, the specification stops being documentation and becomes the only artifact that can tell you what the system does. Yadda 3.x is a lightweight, unopinionated way to write that artifact in JavaScript. Whether or not you adopt it, the discipline it encodes — specs that are executable, tests the agent cannot edit in the same breath as the implementation, verification that lives outside the agent's reach — is the part that generalises.

## How Do You Get Started with Yadda 3? Install, Feature, Step Library, Run

Yadda 3.x is Node-only and requires Node.js >= 20.

```bash
npm install --save-dev yadda
```

**1. Write the feature as Markdown** (supported from 3.1.0). Headings are features and scenarios, list items are steps:

```markdown
# Shopping cart

## Adding items

- Given I have 10 widgets in stock
- When I sell 3 widgets
- Then I should have 7 widgets in stock
```

**2. Write the step library** that binds each sentence to real code:

```js
const { Yadda, Library } = require('yadda');

const library = new Library()
  .define('I have $count widgets in stock', function (count, next) {
    this.state.stock = Number(count);
    next();
  })
  .define('I sell $count widgets', function (count, next) {
    this.state.stock -= Number(count);
    next();
  })
  .define('I should have $count widgets in stock', function (count, next) {
    if (this.state.stock !== Number(count)) {
      return next(new Error(`expected ${count}, got ${this.state.stock}`));
    }
    next();
  });

module.exports = library;
```

**3. Run it under `node:test`** (the built-in runner added as a first-class integration in 3.0):

```js
const { test } = require('node:test');
const assert = require('node:assert');
const { Yadda } = require('yadda');
const library = require('./steps/cart.steps');

test('selling widgets reduces stock', async () => {
  const yadda = Yadda.createInstance(library);
  const ctx = { state: {} };
  await yadda.run(`
    Given I have 10 widgets in stock
    When I sell 3 widgets
    Then I should have 7 widgets in stock
  `, ctx);
});
```

```bash
node --test
```

Three things to get right on day one. Put shared state on `ctx.state`, never at the top level — Yadda gives each step a fresh copy of the context. Keep the runner outside Yadda; if you are on Mocha or Jasmine, the same library works unchanged. And wire the run into CI before you wire it into an agent loop, so the first thing your agent learns is that verification happens somewhere it does not control.

## Sources and Further Reading

Primary sources for this review, all checked 1 October 2026:

- Stephen Cresswell, ["Yadda 3.0.0: BDD in the Age of AI Agents"](http://www.stephen-cresswell.com/2026/08/15/Yadda-3.0.0-BDD-in-the-Age-of-AI-Agents.html) — the announcement, the inversion thesis and the agent-phase method.
- [acuminous/yadda](https://github.com/acuminous/yadda) — README, comparison table, coverage and design rationale.
- [registry.npmjs.org/yadda](https://registry.npmjs.org/yadda) — version history and dependency metadata.
- [Yadda CHANGELOG and migration guide](https://raw.githubusercontent.com/acuminous/yadda/master/CHANGELOG.md) — every 3.x breaking change, by issue number.
- [Hacker News discussion of the announcement](https://news.ycombinator.com/item?id=49310495) — the acronym-literacy thread and the dissenting view.
- [martinfowler.com, "TDD inside the agent loop - theater or actual value?"](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html) — the strongest counter-evidence.
- [arXiv 2602.00180, "Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants"](https://arxiv.org/abs/2602.00180) — the spec-first / spec-anchored / spec-as-source ladder.
- [arXiv 2604.17464, "Project Prometheus"](https://arxiv.org/abs/2604.17464) — the 93.97% patch rate and the Intent-Behavior Mirroring Effect.
- [aq.dev, "Executable Specs for AI Coding Agents"](https://aq.dev/guides/executable-specs-for-ai-coding-agents) — operational guardrails and the reward-hacking catalogue.
- [GitHub Spec Kit](https://github.com/github/spec-kit) and its [integrations page](https://github.github.io/spec-kit/reference/integrations.html) — the 2026 spec-driven tooling landscape.

Related reading on this site: [agent verification plugins compared](/posts/ai-agent-verification-plugins-comparison-2026/), [AI agent testing guide](/posts/ai-agent-testing-guide-2026/), [TDD with Claude Code](/posts/superpowers-claude-code-tdd-guide-2026/), [Claude Code best practices](/posts/claude-code-best-practices-2026/), and [AI coding agent capability matrix](/posts/ai-coding-agent-capability-matrix-2026/).


## FAQ

### What is BDD in simple terms?
Behavior-driven development is a practice where requirements are written in ordinary language and each step is bound to executable code. The spec is readable by non-engineers and runnable by machines. The point is that the documentation cannot silently drift, because it fails the build when the system stops matching it.

### Is Yadda better than Cucumber for AI coding agents?
Not universally. Yadda is better if you want zero runtime dependencies, no runner lock-in, non-rigid step syntax, and dictionaries that can source step data from external systems. Cucumber is better if you need its ecosystem, its reporter and plugin tooling, or browser-based step support. For agent work specifically, the properties that matter are executable binding and the ability to keep tests outside the agent's reach — both tools provide that. Yadda's flexibility is a preference, not a correctness advantage.

### Should the same AI agent write the tests and the implementation?
No. If one agent implements a feature and can also edit the tests until they pass, a green suite stops being evidence — the agent can change the definition of correct at the same time as the implementation. Commit the failing test first as a tamper seal, tell the agent not to modify existing tests, and enforce the rule with a pre-commit hook or CI job rather than a prompt instruction. Project Prometheus's "Intent-Behavior Mirroring Effect" and the reward-hacking behaviours catalogued by benchmarks like ImpossibleBench are what this rule defends against.

### Does Yadda 3.0 work in the browser?
No. Yadda 3.0 is Node-only, requires Node.js >= 20, and dropped browserify bundling and in-browser bundles entirely (issues 320–322 of the modernisation epic). For browser end-to-end BDD, `playwright-bdd` or `@badeball/cypress-cucumber-preprocessor` are the conventional choices.

### How long does it take to migrate from Yadda 2 to Yadda 3?
It depends on how much of the removed surface you used. Every breaking change is enumerated per issue in the changelog and `docs/migrating-to-3.md`: browser bundling (320), `lib/Platform.js` (321), `lib/shims` (322), the version string in `String(yadda)` (323), `'use strict'` in source (324), `nyc` in favour of built-in `node:test` coverage (325), and `bin/rev.sh` (326). A Node-only project that used Yadda as a library typically has a small change surface; anything relying on in-browser execution needs a different tool rather than a migration.
