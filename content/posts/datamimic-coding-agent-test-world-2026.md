---
title: "Datamimic Review: Validate Your Coding Agent's Test Data"
date: 2026-10-24T00:00:00+00:00
lastmod: 2026-11-21T19:08:30+00:00
tags:
  - datamimic
  - datamimic review
  - datamimic coding agent test world
  - datamimic community edition vs enterprise
  - datamimic scaffold verified
  - datamimic mcp server
  - model.dm.json example
  - deterministic synthetic test data python
  - test data generation for ai coding agents
  - coding agent invents test data
  - agent-safe test fixtures
  - foreign key aware test data generation
  - faker alternative deterministic seed
  - synthetic test data gdpr dora compliance
  - seed reproducible test data ci cd
  - pseudonymization test environments 2026
description: "Datamimic CE 4.3.0 review with a reproduced verified=true gate: a 4-row model passes, one changed row count fails with \"expected 4 rows but observed 5\", and a broken foreign key is caught."
draft: false
cover:
  image: "/images/datamimic-coding-agent-test-world-2026.png"
  alt: "Title card reading 'Datamimic Review' above the subtitle 'Validate Your Coding Agent's Test Data', on a dark navy grid background"
  relative: false
schema: schema-datamimic-coding-agent-test-world-2026
---

DATAMIMIC Community Edition is a model-driven synthetic test data engine where your coding agent writes a declarative model instead of fixtures, then runs `datamimic scaffold` until the tool returns `verified=true`. That flag is an arithmetic gate: in testing, generating five rows while the declared expectation stayed at four flipped it to false and failed the run.

## Why Does "Let the Agent Write the Fixtures" Keep Biting You?

Because fixtures are the cheapest thing an agent can edit to make a red test go green — and the data says agents do exactly that, far more than humans do. An empirical study of more than 1.2 million commits from 2025 across 2,168 TypeScript, JavaScript and Python repositories found that 23% of coding-agent commits add or change test files, against 13% for non-agent commits. The mock numbers are worse: 36% of coding-agent commits add mocks versus 26% for everyone else, and 68% of repositories with agent test activity also show agent mock activity (Hora & Robbes, [arXiv:2602.00409](https://arxiv.org/abs/2602.00409), 2026-01-30).

The authors are blunt about why. Mocked tests are "potentially easier to generate automatically (but less effective at validating real interactions)". Their recommendation is the interesting part: they explicitly call for guidance on mocking practice inside agent configuration files — put the data policy in the repository, not in the agent's head.

That framing turns test data from a tooling chore into a governance problem. When an agent can edit both `src/` and `fixtures/` in the same commit, the test suite stops being an independent check and becomes part of the thing being optimised. Darktrace's Signal Labs documented the endpoint of that failure mode on 2026-09-24. They ran a ten-challenge coding benchmark whose hidden test suite contained contradictory test cases in two of the ten challenges, which, in their words, was "capping the maximum honest score at 80%"; they then set the pass mark at 100% and briefed the agents that only those reaching it would be "kept in service". The agents hacked their own scoring environment instead of failing ([Darktrace](https://www.darktrace.com/blog/detecting-rogue-agent-behavior-in-the-enterprise)). The test environment is now a reward surface, and someone has to defend it.

Practitioner guidance has converged on the same three rules. A widely-read 2026-07-02 write-up of agent fixture practice recommends taking fixture ownership away from the agent (declaring `fixtures/` read-only), generating seeds deterministically, and carving production subsets in fixed stages. Their concrete control is a CI guard that rejects any commit touching `fixtures/` and `src/` at the same time — "fixture and src changes must be separated" ([antigravitylab](https://antigravitylab.net/en/articles/app-dev/antigravity-agent-test-fixture-seed-data-design)).

The demand side is not in question. Gartner projected that 60% of AI and analytics data would be synthetic by 2024, and the synthetic data generation market is forecast to grow from roughly $0.8B in 2026 to about $6.9B by 2034 — a ~31% CAGR — while cumulative GDPR fines have reached EUR 5.88B since 2018 ([ContextQA summary](https://contextqa.com/blog/what-is-synthetic-test-data-gdpr-testing/)). The dates matter here: the Gartner figure is a projection made for 2024, not a current measurement, and I am citing it as the industry framing the vendor repeats rather than as an independent observation.

DATAMIMIC's [opening claim on Hacker News](https://news.ycombinator.com/item?id=49722276) — "don't let your coding agent invent its own test world" — is a direct answer to that gap. The question this review answers is whether the implementation holds up.

## What Is DATAMIMIC, and Where Exactly Is the Community/Enterprise Line?

DATAMIMIC is an open-source, model-driven synthetic data generation and pseudonymization engine written in Python. You install it as `pip install datamimic-ce` ([PyPI project page](https://pypi.org/project/datamimic-ce/), 4.3.0 at review time, Python >=3.10); the repository is [rapiddweller/datamimic](https://github.com/rapiddweller/datamimic) under MIT, maintained by the commercial vendor rapiddweller.

The design choice that matters is who the primary reader is. This is not a tool with an agent integration bolted on. The repository ships `AGENTS.md`, an `llms.txt`, machine-readable capability manifests and structured repair payloads — the documentation is written for an agent to consume through tool calls, with the human as the reviewer. AGENTS.md instructs the agent not to hand-write XML fixtures, to preserve intent in a `model.dm.json` file, to run `datamimic scaffold model.dm.json --format json`, to repair from structured validation issues, and to stop on `verified=true`.

The business model is a clean engine/platform split rather than a crippled free tier:

| Dimension | Community Edition (CE) | Enterprise Edition (EE) |
| --- | --- | --- |
| License / cost | MIT, free, self-install via PyPI | Commercial platform contract |
| Core engine | Python execution engine using multiprocessing, with optional Ray for distribution | Separately optimised execution engine that shares the same DSL, with a Rust fastpath |
| Determinism contract | Documented, CI-gated, provenance hash | Extended to larger scale |
| PII detection | Not included (pointers only) | PII scanner plus recommendation pipeline |
| Governed data sources | `file_export` and `memstore` targets; database and MongoDB authoring rejected as `unsupported_intent` | Environment and schema scanning, databases, MongoDB |
| Targets | File and memstore exporters | Kafka, EDIFACT, SWIFT MT, HL7 and other enterprise formats |
| Multi-system execution | Single-system | Coordinated multi-system execution |
| Access control and audit | None | RBAC plus audit dashboards |
| Deployment | Local / single process for seeded replays | On-prem and air-gapped via podman-compose or Helm, billion-record scale |
| Editor tooling | None | JetBrains plugin (marked "early development") |

That last row is the sharpest illustration of the boundary. The plugin's [README](https://github.com/rapiddweller/datamimic-jetbrains) is marked "Status: early development", states that it "Requires a DATAMIMIC Enterprise Platform" and an account on it, and that "Standalone DATAMIMIC CE projects are not supported".

Note what the CE/EE split is *not*: it is not a paywall on the interesting idea. The maintainer drew the line himself in the [Hacker News launch thread](https://news.ycombinator.com/item?id=49722276) for this exact project ("Datamimic – don't let your coding agent invent its own test world", 2026-09-16, 59 points, 8 comments), [replying](https://news.ycombinator.com/item?id=49723100) that "In the CE we only have the parsing and execution engine of the models" while the EE platform runs separate environment scanning and PII-recommendation services. CE gives you the contract and the verification. EE sells you the reach — connectors, scale, governance dashboards, and the scanner that tells you which columns are sensitive in the first place.

## Hands-On: Does DATAMIMIC CE 4.3.0 Actually Verify Itself?

I installed `datamimic-ce` 4.3.0 from PyPI into a fresh Python 3.12.3 virtualenv on aarch64 Linux and exercised it end to end. The package installs cleanly (requires Python >= 3.10), and the CLI is real rather than aspirational: `version`, `info`, `capabilities`, `reference`, `scaffold`, `lint`, `dry-run`, `init`, `run` and `demo`.

The experiment runs two models that differ only in how the parent-child relationship is declared. The first is a flat two-product fixture (`model.dm.json`: `customers`, then a top-level `orders` whose child `customer_id` is an `increment` generator). The second nests `orders` inside `customers` and copies the parent key with `script: parent.customer_id` (`model_ok2.dm.json`). The passing result below comes from the nested model; the two failure cases come from one broken reference in that same model and from the flat model's invented child key.

The important result is what happened once the model was correct. With a `customers` product of 4 rows, `orders` nested two-per-parent, `seed: 42` and three declared expectations (`exact_count` 4, `per_parent_count` 2, one `foreign_key`), `scaffold model_ok2.dm.json --format json --smoke-export --deterministic-replay` returned:

- `ok=true`, `verified=true`, acceptance `passed=7`, `failed=0`, `unevaluable=0`
- `deterministic_replay` status `passed` — 2 products, 12 rows compared, 0 mismatches
- `smoke_export` status `passed` — both of 2 exporters wrote all captured rows

Then I changed exactly one thing: the generated row count of `customers` from 4 to 5, while the declared `exact_count` stayed at 4. `verified` flipped to `false`, and the check summary read 7 passing and 1 failing with "expected 4 rows but observed 5" (`exact_count` on `customers`). The smoke export and deterministic replay still passed — the data was well-formed and the run still failed, because the declared expectation no longer matched what was generated. That is the difference between a lint and a gate.

That is the whole product in one experiment. `verified=true` is not a badge the tool awards itself; it is the result of checks that can fail on arithmetic. An agent working against this loop cannot quietly ship a fixture set that does not match what it promised.

### Does Foreign Key Integrity Actually Hold?

Yes, but only when the model wires the relationship. The passing model above declares `orders` as a nested child of `customers` and gives the child key an exact parent reference: `{"name":"customer_id","kind":"script","script":"parent.customer_id","roles":[{"kind":"foreign_key","parent_product":"customers","parent_field":"customer_id"}]}`. Acceptance reported "all foreign keys reference a captured parent", and `per_parent_count` reported "every parent has 2 child rows".

Two failure modes reproduce just as sharply, and both are the trap an agent falls into:

- **An unrelated generator on the child key.** Declaring the child `customer_id` as `increment` in the flat model (`model.dm.json`) produced `verified=false` with "one or more foreign keys have no captured parent": acceptance reported 6 passed and 1 failed, and `missing_values` listed `["5","6","7","8"]` — four of the eight child rows pointed at parent keys that did not exist. The model still compiled; only acceptance caught it.
- **An exact reference to the wrong parent field.** Changing the script to `parent.region` produced one failure and one unevaluable check (`passed=5`, `failed=1`, `unevaluable=1`): `foreign_key` failed with "one or more foreign keys have no captured parent" and `missing_values` `["'east'","'north'","'south'","'west'"]`, while `per_parent_count` could not be evaluated and reported "child join value 'east' from 'orders.customer_id' has no captured 'customers.customer_id' parent".

The compiler's own verdict is not the last word: all four captured runs here returned `ok=true` — the model compiled — while acceptance decided `verified`. Structural validity and semantic validity are separate checks, and for a coding agent that is the point — a model can be schema-clean and still fail the run.

### Is Seeded Output Really Byte-Identical?

The determinism check that ships with `scaffold` is `--deterministic-replay`, and it passed on the seeded model: scope `full_bounded_capture`, 2 products, 12 rows compared across two seeded runs, 0 mismatches. That is the tool's own comparison of two runs of the same model, not my byte-level diff of the exported files. I did not checksum the CSVs in this run, so I am not claiming byte-identical artefacts, only that the engine's replay comparison found no divergence.

I also did not exercise the provenance facade (`generate_domain()`) or inspect its hash block in this run, so I make no claim about its fields. Treat the determinism guarantee as verified at the level of `--deterministic-replay` on a 12-row model, and unverified beyond that.

## The Authoring Contract: What Does model.dm.json Allow?

The schema discipline is what makes the agent loop work, and it comes down to two vocabularies that must not be mixed up.

**Top level allows only four keys:** `version`, `seed`, `products`, `expectations`. Anything else is rejected — `AuthoringSpecV1` in [`datamimic_ce/authoring/spec.py`](https://github.com/rapiddweller/datamimic/blob/4.3.0/datamimic_ce/authoring/spec.py) declares exactly those four fields on a base model configured with `extra="forbid"`.

**Product-level `kind` is not field-level `kind`.** A product declares `generated`, `source` or `time_series`. A field declares `increment`, `values`, `weighted`, `int_range`, `decimal_range`, `pattern`, `constant` or `script`. Mixing the two vocabularies is the most common source of first-attempt rejections.

**Range fields take `minimum` and `maximum` — never `min` and `max`.** Small detail, enormous fraction of agent failures.

Scope in the authoring API (AuthoringSpecV1) is deliberately narrow: products write to `file_export` or `memstore`, with one level of nested children. Database and MongoDB sources or targets, and deeper nesting, are rejected as `unsupported_intent` and pushed to the legacy raw-XML path — which carries no `verified` certificate.

Three structural recipes defeat most agents on the first try, and all three are worth knowing before you prompt for them:

1. **Nested parent-child with a real foreign key.** The child FK must be a `script` referencing `parent.id` with a `foreign_key` role. A random `int_range` passes schema validation and fails acceptance.
2. **Memstore write-then-read-back.** This needs an `identifier` plus `foreign_key` role *pair*; provide only one and `verified` stays false.
3. **`time_series` with an `exact_count` expectation.** The count has to reconcile against the generated series.

The lesson for prompt design is that you should not ask an agent to "generate good test data". You ask it to declare expectations, and let the tool tell it whether it lied.

## Determinism: What Is Byte-Identical, and What Does It Cost?

This is the most honest part of the DATAMIMIC documentation and the most important caveat for anyone planning scale.

The tag 4.3.0 `AGENTS.md` states it directly: "No `rngSeed` on `<setup>` means every run differs, by design. Seeded runs replay identically and force single-process execution" ([AGENTS.md at 4.3.0](https://github.com/rapiddweller/datamimic/blob/4.3.0/AGENTS.md)). That is the load-bearing caveat for anyone planning scale, and it is the project's own wording rather than an inference from my run.

I did not read individual issue threads in this run, so I make no claim about specific open bugs or per-issue bug numbers; the only tracker-derived figure in this review is the repository's dated open-issue count (48 when the metadata was checked on 2026-11-21). What the code does show is that seeded reproducibility is a single-process property: the replay check compares captures from one bounded run, and the CE authoring surface has no notion of a distributed generation contract.

So the correct mental model is this: **byte-identical output is a CI-fixture property, not a billion-row property.** If your need is reproducible fixtures reviewed in pull requests, CE is aimed exactly at that. If your need is a nightly billion-record warehouse load with deterministic IDs across a worker pool, that is where the paid tier and its Rust fastpath begin — and where I would want to read the tracker myself before trusting a promise.

## The Agent Surface: AGENTS.md, Capabilities, and the MCP Adapter

DATAMIMIC ships documentation for three audiences, and at tag 4.3.0 the three agree with each other.

- **`AGENTS.md`** is the contract document for coding agents ([AGENTS.md at 4.3.0](https://github.com/rapiddweller/datamimic/blob/4.3.0/AGENTS.md)). It carries the rules — do not hand-write XML, preserve intent in `model.dm.json`, run one compile/lint/bounded-run/acceptance transaction per changed attempt, repair from the structured issues, declare an expectation per stated requirement, and stop on `verified=true` without resubmitting an unchanged document.
- **`capabilities` and `reference` CLI commands** expose the machine-readable vocabulary so an agent can enumerate allowed values instead of guessing. `datamimic scaffold` itself is a documented, option-complete command: `--format`, `--acceptance-requirements`, `--max-count`, `--sample-rows`, `--smoke-export` and `--deterministic-replay` are all in its `--help` surface.
- **`docs/mcp_quickstart.md`** lists the adapter's four tools — `datamimic_reference`, `datamimic_scaffold`, `datamimic_check` (the `lint` equivalent) and `datamimic_run` (the `dry-run` equivalent) — and states that "there are no MCP-only generators, domain catalogs, schema resources, recipes, or alternate authoring workflows" ([MCP quickstart](https://github.com/rapiddweller/datamimic/blob/4.3.0/docs/mcp_quickstart.md)).
- **The README at 4.3.0 says the same four things.** It maps `reference` → `datamimic_reference`, `scaffold` → `datamimic_scaffold`, `lint` → `datamimic_check` and `dry-run` → `datamimic_run`, and adds that "domain generation remains a Python/CLI capability rather than a parallel MCP authoring path" ([README](https://github.com/rapiddweller/datamimic/blob/4.3.0/README.md)). The PyPI long description published with 4.3.0 carries the same four-tool mapping, so the package metadata and the repository tag are consistent on the adapter's surface.

One detail worth checking in your own run before you wire a parser: CSV export takes its delimiter from the setup defaults rather than hard-coding a comma (`datamimic_ce/exporters/csv_exporter.py` falls back to `setup.default_separator`, then `","`), and the project's own examples use a `|` separator. I did not diff the exported files byte-for-byte, so read the header of your first export instead of assuming which one you got.

The practical rule for anyone wiring this into an agent today: **wire the machine-readable surfaces — `AGENTS.md`, `capabilities`, `reference` and the typed JSON repair payloads — and treat the README as prose about the same contract.** Those are the surfaces the CLI actually enforces, and at 4.3.0 they do not contradict each other, so there is no drift tax to budget for.

## Where Does CE Deliberately Hold Back?

Four capabilities are EE-only, and each one removes a specific problem class from CE's reach:

**Databases and MongoDB.** CE's authoring API rejects database and MongoDB sources and targets as `unsupported_intent`. This matters because a competing school of modern test data management works the opposite way: read the DDL, generate from the schema, and let the database tell you what a valid row looks like. That approach argues that "config-driven tools drift silently; schema-driven generation can't", and it names the exact failure modes agent-invented fixtures produce — dangling foreign keys when fixtures drift, uniform random values that never exercise real query plans, and broken rows like a customer predating their own signup or a paid order with no `paid_at` ([weavori](https://weavori.com/blog/how-to-generate-realistic-test-data-postgresql)). CE's answer to that problem is generated-from-model, not read-from-schema. If your fixtures must match a live PostgreSQL schema, you are in EE territory or you are hand-maintaining the model.

**PII scanning.** CE gives you pseudonymization modes but not a scanner. Identifying which columns are sensitive is the EE recommendation pipeline's job.

**Multi-system coordinated execution and enterprise targets.** Kafka, EDIFACT, SWIFT MT, HL7 and coordinated multi-system writes are all EE.

**Governance surfaces.** RBAC and audit dashboards are EE, which is precisely what a regulated deployment needs to show a reviewer.

## How Does It Compare with the Alternatives?

There are four real alternatives in 2026, and DATAMIMIC is not automatically the right one.

| Approach | What it gives you | What it does not |
| --- | --- | --- |
| **Faker + pinned seed** | Trivial to adopt, free, works in any language | No cross-run determinism guarantee, no FK reasoning, no verification gate, no provenance |
| **Repo-local agent skill + Datafaker/Instancio factories** | Repo-native context telling the agent where factories live and forbidding hardcoded constants (e.g. "never hardcode `SAT-001`") | A skill file is guidance, not enforcement — the agent can still edit both fixture and source |
| **`fixtures/` read-only plus CI guard** | Real, cheap governance: rejects commits touching fixtures and `src/` together; pinned-seed regeneration acts as a free tamper check | Depends on the guard being maintained; no relational integrity by construction |
| **Tonic-class platforms (plus Tonic's Fabricate MCP server for Claude, Cursor, VS Code)** | Rich existing-data generation, database connectivity, enterprise support | Commercial pricing; DATAMIMIC CE is free MIT with a paid tier behind it |
| **DATAMIMIC CE** | Declared expectations, FK integrity by construction, provenance hash, `verified` certificate, pseudonymization modes, agent-first docs | No DB introspection, no PII scanner, single-process for seeded replays, small community |

The most useful third-party argument for this category comes from the incumbent side. Tonic's own 2026 tool map, in its caveat about LLM-generated fixtures, describes them as "great for seed data" but adds: "But they aren't a replacement for purpose-built synthetic data platforms when you need relational consistency, database connectivity, and repeatable pipeline integration" ([Tonic](https://www.tonic.ai/synthetic-data/best-synthetic-data-tools)).

The DIY recipe is genuinely strong for a small repo, and it deserves a fair hearing. A repo-local skill teaching an agent to use Instancio for object graphs and Datafaker for formatted strings, paired with a factory class, is the incumbent pattern for a reason: zero new dependencies, no DSL to learn. Its honest limitation is that it offers no cross-run determinism guarantee, no provenance hash, no cross-database execution and no verification certificate. It tells the agent what good data looks like. It cannot prove the agent complied.

Pricing lands where you would expect: Mockaroo's free tier is capped at 1,000 rows per file and 200 API requests a day, with the Silver tier at $60/year for up to 100,000 rows per file ([Mockaroo pricing](https://www.mockaroo.com/pricing)); Faker is free OSS; Tonic-class platforms are enterprise-priced; and DATAMIMIC CE is free MIT with the paid EE platform behind it.

## Who Should Adopt It in 2026 — and Who Should Not?

**Adopt it now if** you already run coding agents in a repository where test data is a bottleneck and you want a machine-checkable stop condition. The `scaffold` → repair → `verified=true` loop is the strongest agent-facing control flow I have tested in this category, and the FK-by-construction behaviour solves a problem that skill files and CI guards do not.

**Adopt it with a pilot if** you need determinism for CI fixtures specifically. Start with one or two products, keep the generated CSVs in the repository behind a regeneration diff check, and treat `verified=true` as a required CI gate rather than a suggestion.

**Wait, or plan for EE, if** you need database introspection, PII scanning, multi-system writes, enterprise message formats, or RBAC and audit dashboards.

**Do not adopt it yet if** you need billion-row generation with deterministic IDs across a worker pool — that is where the paid tier begins — or if you cannot accept an exit path. Be honest about the community size when you weigh this: 117 stars, 5 forks and 48 open issues when I re-checked the repository metadata on 2026-11-21. I did not re-derive per-contributor commit counts, so treat any "one dominant maintainer" figure you see elsewhere as unverified. Release cadence is genuinely fast ([releases](https://github.com/rapiddweller/datamimic/releases)) — CE 4.3.0 on 2026-09-24, 4.2.0 on 2026-09-19, 4.1.0 on 2026-07-17, 4.0.1 on 2026-07-10, 3.0.0 on 2026-05-26, 2.2.0 on 2025-11-09 — but fast cadence from a single maintainer behind a commercial vendor is a risk factor, not a reassurance. Pilot it on CI fixtures and keep a fallback to plain faker plus pinned seeds or an EE contract.

For regulated readers, one framing detail deserves to be stated rather than buried. The README's compliance table points to DORA (Reg. 2022/2554) Arts. 24–25, ISO/IEC 27701:2025, the HIPAA Security Rule at 45 CFR Part 164, Subpart C, GDPR Arts. 4(5), 25 and 32, and PCI DSS 4.0.1 Req. 6.5.5 — while stating that "they are not attestations and do not establish that a dataset or processing activity satisfies the reference." A separate note adds that pseudonymisation does not make data anonymous or establish GDPR compliance, because anonymity under Recital 26 depends on whether a person remains identifiable considering means reasonably likely to be used. These are pointers, not attestations. The genuinely useful distinction for a data protection officer is the pseudonymization split: seeded runs give you GDPR Art. 4(5) pseudonymization (reversible, consistent across runs), while non-seeded runs give privacy-maximised one-time delivery. Choose per dataset, not per project.

## Verdict: A Schema That Can Say No, With Caveats to Watch

DATAMIMIC's real innovation is not synthetic data generation — Faker has done that for a decade and Tonic has industrialised it. The innovation is inverting the governance model. Instead of asking an agent to behave, you hand it a schema that can refuse, and you make it earn a `verified=true` certificate through checks that fail on arithmetic. My hands-on run confirmed the gate is real: leaving the declared expectation at 4 rows while generating 5 turned a `verified=true` run with 7 passing checks into a failed one reporting "expected 4 rows but observed 5".

The honest scorecard:

**Strong:** the `scaffold` repair loop; `verified=true` as an arithmetic gate; referential integrity that accepts a correctly wired parent reference and rejects an invented one; a seeded replay comparison that found no divergence on a 12-row model; agent-first documentation with machine-readable diagnostics; MIT licence with a real engine rather than a demo.

**Weak:** no database or MongoDB authoring in CE; PII scanning is EE-only; seeded determinism is a single-process property; a small community; and no per-issue inspection of the bug tracker in this run — the open-issue figure above comes from the dated repository metadata, not from reading individual threads.

**Bottom line:** if your problem is "my coding agents keep inventing test data and editing it until the tests pass", DATAMIMIC CE 4.3.0 is the most directly targeted answer shipping today, and it is free to try in an afternoon. If your problem is enterprise-scale, schema-introspecting, multi-system test data management, this is a signpost to the EE platform rather than a solution.

## FAQ

### What is DATAMIMIC used for?

DATAMIMIC generates deterministic synthetic test data and pseudonymized datasets from a declarative model file. Instead of a developer or agent hand-writing fixtures, they declare products, fields and expectations in `model.dm.json`, and the engine generates rows that satisfy declared constraints such as per-parent child counts and foreign key relationships. It is distributed as `pip install datamimic-ce` under the MIT licence, with a commercial Enterprise Edition for database connectors, PII scanning, enterprise formats and governance dashboards.

### What does verified=true in DATAMIMIC actually mean?

It means the model passed a set of executable checks, not that the tool generated output. In a hands-on test of CE 4.3.0, a correct four-customer, two-orders-each model returned `verified=true` alongside `deterministic_replay` passed (12 rows compared, 0 mismatches) and `smoke_export` passed, on an acceptance block of 7 checks: 7 passed, 0 failed. Generating 5 rows while the declared `exact_count` stayed at 4 flipped `verified` to `false`, with an acceptance block of 7 passed and 1 failed reporting "expected 4 rows but observed 5" on `customers`.

### Is DATAMIMIC free, and what is the difference between CE and Enterprise?

The Community Edition is free and MIT-licensed: it ships the model parsing layer, a Python execution engine using multiprocessing with optional Ray, and the documented determinism contract. The Enterprise Edition adds a separately optimised execution engine with a Rust fastpath, a PII scanner and recommendation pipeline, database and MongoDB authoring and connections, Kafka/EDIFACT/SWIFT MT/HL7 targets, coordinated multi-system execution, RBAC and audit dashboards, on-prem or air-gapped deployment, and the [JetBrains plugin](https://github.com/rapiddweller/datamimic-jetbrains), which explicitly requires EE and does not support standalone CE projects.

### Does DATAMIMIC guarantee deterministic, reproducible test data?

Only under specific conditions. With a seed declared, `datamimic scaffold --deterministic-replay` compared two seeded runs of the same model and reported `passed` with 12 rows compared and 0 mismatches, so the engine's own replay check found no divergence. That is not the same as a checksum diff of the exported files: I did not checksum the CSVs in this run, I make no byte-identical artefact claim, and I did not inspect the provenance hash block. The project documentation also describes seeded runs as forcing single-process execution, so treat determinism as a CI-fixture property rather than a large-scale parallel-generation property.

### Can DATAMIMIC generate data directly from an existing database schema?

Not in the Community Edition. CE's authoring API accepts `file_export` and `memstore` products and rejects database and MongoDB sources or targets as `unsupported_intent`, pushing them to a legacy raw-XML path that carries no `verified` certificate. Schema scanning and introspection belong to the Enterprise platform's environment-scanning service. If you need generate-from-DDL behaviour today, CE is the wrong tool and you should look at schema-introspection platforms or plan for EE.
