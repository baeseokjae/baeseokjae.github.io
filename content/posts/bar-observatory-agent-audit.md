---
title: "Bar Observatory: Deterministic Local Audit Reports for Claude Code"
date: 2026-08-21T01:04:01+00:00
lastmod: 2026-10-19T00:22:12+00:00
tags: ["claude-code", "observability", "audit-trail", "ai-agents", "local-first", "devtools"]
description: "Bar Observatory records Claude Code sessions into a local SQLite store and renders audit reports its author says are byte-identical. What it captures, what its own verification does and does not prove, and where it fits beside tracing dashboards."
draft: false
schema: schema-bar-observatory-agent-audit
cover:
  image: "/images/bar-observatory-agent-audit.png"
  alt: "Bar Observatory: deterministic local audit reports for Claude Code"
  relative: false
---

Bar Observatory is an MIT-licensed Rust tool that records Claude Code sessions into a local SQLite file and renders that file into JSON, HTML and Markdown audit reports. The selling point is narrow and specific: the render path contains no model, so an unchanged store produces the same document every time, and the same store can be handed to a reviewer who renders it again. If your question is "what did the agent actually do, and can someone else re-derive that answer?", this is the category of tool worth evaluating. If your question is "how many tokens did this cost?", it is the wrong tool.

The honest caveats belong up front. The project is small — 24 GitHub stars, 0 forks and 158 crates.io downloads when checked on 2026-10-19 — and maintained as a single public front door around a private source tree. Its headline determinism result comes from the author's own black-box script run against the author's own shipped example, not from a third-party audit. And the evidence covers Claude Code only: the plugin, the transcripts it parses and the lifecycle hooks it installs are all Claude Code surfaces. Treat everything below as a review of a plausible, narrowly scoped tool, not as a recommendation for regulated workloads.

## The reader problem: an agent's summary is not a receipt

An unattended coding agent reports on itself. When it finishes, you get prose describing what it meant to do, written by the same model that did the work. That summary is useful for steering and useless as evidence: it can omit failed commands, misdescribe a test run, or claim a validation it never performed. The question a reviewer actually asks is narrower than "is the agent trustworthy" — it is "what tool calls, errors and test results occurred in this run, and did they stay inside the permissions we granted?"

There is a security argument for wanting that record too. In April 2026, audited.xyz published a confirmed finding in Claude Code's structured I/O layer: `update_environment_variables` transport messages were applied to `process.env` without an allowlist, and a proof of concept injected `NODE_OPTIONS` to achieve remote code execution, tested against Claude Code 2.1.92. The report rates severity Low and states the attack surface is limited to remote-worker deployments, since the common local CLI case uses a Unix pipe to a trusted parent. The lesson for audit design is not that Claude Code is unsafe; it is that when the runtime environment can be influenced, a local record of what the process actually executed is the artifact you reconstruct events from afterwards.

## What Bar Observatory actually is

The public repository describes a 16-crate Rust engine with 16 of 17 crates published, 21 lifecycle hook events and 12 read-only MCP tools. The user-facing surface is a Claude Code marketplace plugin that adds five slash commands: `/bar-init`, `/bar-report`, `/bar-interpret`, `/bar-doctor` and `/bar-query`.

Recording is automatic once installed: session transcripts and hook events are appended to a local file, one per run. Reporting is on demand. Interpretation is separate and optional — `/bar-interpret` writes a plain-English summary using your own Claude Code session, and the project is explicit that the label matters: the summary is commentary, and the deterministic evidence does not depend on it existing.

Two helper binaries, `bar-hook` and `bar-mcp`, must be on `PATH`. The plugin resolves them by name rather than bundling them, which the README discloses as a gap and not an oversight. In practice that means one manual `cargo install` step before the plugin works, and it means the binaries a session uses are whichever ones the invoking environment's `PATH` resolves — worth pinning explicitly if you care which build recorded your evidence.

## Record, store, report, reuse

The pipeline has four stages, and the design claim is that determinism is preserved at each one.

1. **Record** — the session transcript is the primary capture path and requires no API calls; 21 lifecycle hook events are added once the plugin is set up. Optional proxy or OTLP capture is opt-in for teams that already run that infrastructure.
2. **Store** — everything lands in a local SQLite file on your machine. There is no account, no API key and no telemetry on the evidence path.
3. **Report** — the engine renders the store into JSON, HTML and Markdown. The same unchanged file renders identical bytes, which is the property that makes two parties able to compare outputs.
4. **Reuse** — 12 read-only MCP tools expose run history, reports, findings and cross-run context so a later agent can query what happened instead of guessing.

Stage 3 is where the audit value lives, and it is also where the claim needs to be stated precisely. Determinism here means reproducibility from the store: a pure function of captured rows, with no clock, network or model input in the render path. It does not mean authenticity. If someone edits the SQLite file, a re-render faithfully reproduces the edit — the project makes no tamper-evidence claim, and a reviewer who needs proof that a record was not altered is asking for a different control, such as signing or an append-only external log.

## What a report contains

A report is a structured ledger rather than a narrative. The project's shipped example covers seven captured Claude Code sessions between 2026-05-04T19:07Z and 2026-05-18T06:06Z — 7 runs and 9,132 transcript turns — and it contains 60 error results, 373 test results, 96 rework hotspots and 17 tool counts, alongside a task ledger, validation state and a coverage section.

Those numbers illustrate the shape of the output, not the prevalence of failure in agent runs. They come from a vendor-selected window of seven sessions shipped in the repository, and the 60 errors in particular are worth reading as a demonstration of the reporting gap: the README says the agent's own summary never mentioned them. One documentation inconsistency is worth naming here, because it is the kind of claim you may end up quoting: the README's marketing copy credits that figure to "one real captured session", while its own example report records those 60 error results under a scope of seven sessions — the artifact is the better evidence, and the count is the same either way.

Rework hotspots are the most operationally interesting field for anyone tuning an agent workflow, because repeated edits to the same region, retries and tool-call patterns are exactly what a human reviewer would otherwise have to reconstruct by reading a long transcript.

Coverage is the field that decides whether the report can be trusted at all. Absence is always an explicit status rather than a fabricated zero, and the shipped example shows two distinct kinds of it: channels the transcript-only capture path never wrote to — hooks, events, spans, requests, file history and provider cost — are reported as `not_recorded`, while channels nobody has inspected yet, such as plan documents and raw logs, are reported as `not_observed`. The transcript channel itself carries a third value, `partial`, with a measured gap attached: 629 dangling parent links and 136 unpaired tool-use/tool-result pairs in that window. Every observability tool implicitly claims completeness; this one makes its blind spots explicit, which is the correct default for evidence and an unusual one to see stated in a README.

## What the verification script proves, and what it does not

The project's headline result is 99 of 101 report fields matching after an install from crates.io. The mechanism matters more than the number. `tests/verify.sh` installs `bar-hook`, `bar-mcp` and `bar-observatory` with `--locked` from the public registry, ingests the example transcripts shipped in the repository, normalizes both the fresh and the shipped report with `jq -S`, deletes `integrity.source_db_hash` and `report.id`, and diffs the remainder.

So the precise reading is: after excluding the two fields the documentation describes as varying per ingest, the remaining 99 fields were identical. That is a meaningful check of the render path — if a model or a clock leaked into it, the diff would not close — but it is the project's own script, in the project's own repository, against the project's own fixture. It is repeatable by anyone with Rust, `jq` and a few minutes, and it is not an independent third-party audit.

The suite also checks the crate install, repository checksum manifest, `bar doctor` health output, config validity and the MCP tool count against a live client response. Its own documentation is candid about the limits: the 699 internal unit and integration tests live in private source and cannot be re-proved from outside, and the suite does not verify that a write attempt against the MCP server is genuinely refused rather than merely absent from the tool list.

One documentation inconsistency is worth flagging because it affects how you quote the project: the technical-details section says 699 tests at the current published snapshot, while the 0.3.0 status paragraph says 716. Neither number is checkable from outside, and this review does not rely on either.

This review did not run the tool. The writing environment has no Rust toolchain, so every capability statement above is attributed to the repository and its published artifacts rather than to a reproduction performed here. Readers who want first-hand confirmation should run `tests/verify.sh` themselves; that is the point of shipping it.

## Install and first report

Inside a Claude Code session:

```bash
/plugin marketplace add bar181/bar-observatory
/plugin install bar-observatory@bar-observatory
cargo install bar-hook bar-mcp bar-observatory
/bar-init
```

Then `/bar-report` renders whatever has accumulated into JSON, HTML and Markdown. `/bar-doctor` reports store health, and `/bar-query` answers direct questions against the record.

Without the plugin, for scripting or CI, the same pipeline is three commands against a transcript you already have:

```bash
cargo install bar-observatory
bar init --dir . && bar ingest .bar/ambient.sqlite ~/.claude/projects/<project>/<session>.jsonl
bar report .bar/ambient.sqlite --out .
```

Retroactive ingestion is the underrated path here. You do not need to have installed the recorder before the run you want to examine — any existing Claude Code transcript can be ingested and rendered afterwards, which makes a pilot cheap: point it at a session you already have, render, and see whether the ledger contains the fields your review process actually needs.

## Privacy: the store is a session artifact, not a sanitized log

The evidence path is local and zero-egress, and the optional interpretation step is the only part that touches a model — your own Claude Code session, producing clearly labeled commentary. That split is the right architecture for audit work: the deterministic document is the evidence, and the narrative layer is disposable.

The privacy warning is equally explicit in the documentation and deserves repeating. A capture database can contain full conversation content, the agent's reasoning blocks, file snapshots and tool inputs and outputs. That is a richer artifact than a request log, and it should be handled like any other sensitive session artifact: scoped storage, retention limits, and a decision about who can read the store. The project points to its enterprise and air-gapped documentation for what is stored and which redaction options exist.

For teams that cannot send session data to a third party, the local-only design is the whole reason to look at this tool at all. It is also the reason a rollout needs a storage decision before the first capture, not after.

## Where it fits beside observability tooling

The agent-observability space has split into three jobs that are easy to confuse.

Tracing and evaluation platforms — the OpenTelemetry-shaped tools covered in our [agent observability tools comparison](/posts/ai-agent-observability-tools-2026/) and the [OpenTelemetry walkthrough](/posts/ai-agent-observability-opentelemetry-2026/) — answer latency, cost, token and quality questions across many runs. They are built for dashboards and aggregation, and their output is a rendering of telemetry rather than a document two parties diff.

Memory tools answer "what should the next session remember?", and most of them compress history with a model. Compression is the point; it is also why the output is an interpretation rather than evidence.

Permission and configuration checkers answer "is this agent configured with least privilege?", which is the static half of the question covered in our [least-privilege guide for AI agents](/posts/secure-ai-agents-least-privilege-2026/). They inspect intent as expressed in config, not what executed.

Bar Observatory occupies the fourth slot: a per-run, local, re-renderable record of execution that can be handed to another party. The closest conceptual neighbour in this site's archive is [trace-file lineage for agent provenance](/posts/trace-file-lineage-agent-provenance-2026/), which addresses the provenance question at the artifact level rather than the session level. The gap Bar Observatory fills is the diffable run document; its weakness is that a single local SQLite file is only as trustworthy as the machine that holds it.

## Limitations and who should not use it

The adoption signal is thin. At check time on 2026-10-19 the repository showed 24 stars, 0 forks and an MIT licence, created 2026-08-12 with its last push on 2026-08-27; crates.io showed 158 total downloads with 0.3.0 as the newest version, published 2026-08-27, while GitHub release objects stop at v0.2.1 from 2026-08-20. That release-object lag is an observation, not necessarily a defect — crates.io publishing and GitHub releases are separate steps — but anyone pinning versions should know the registry is ahead of the release page. Stars and downloads are not usage evidence either way; there is no published production case study.

Scope is Claude Code only. The capture layer is built on Claude Code transcripts and lifecycle hooks, and nothing in the evidence shows the same pipeline working for another coding agent.

The MCP surface is read-only by contract and by tool listing. The verification documentation states that genuine write refusal is not re-proved from outside, so treat "read-only" as the intended design until you have tested it in your own environment.

Determinism is reproducibility, not integrity, as described above. A team that needs third-party attestation, signed records or an append-only audit trail outside the agent's own machine will not get it here, and should not stretch this tool's guarantee to cover that requirement.

Finally, the project is a single-maintainer effort around a private source tree. The public repository is the front door and the published crates; the internal test suite is not available for inspection. That is a legitimate design choice for a commercial project, and it is also a bus-factor and review-depth risk that belongs in any adoption decision.

## Verdict

Bar Observatory is worth a bounded pilot if you run Claude Code unattended and need a run record that another person can re-render and check. The pilot is cheap and concrete: install the three crates, run `tests/verify.sh` to confirm the determinism check closes on your machine, ingest a transcript you already have, and read the resulting ledger against the review questions you actually ask. If the fields you need are there and the diff closes, you have a local evidence artifact that no model wrote.

It is not the right tool for cross-run cost and latency analytics, for cross-session memory, or for proving that a record was never altered. Those are different problems with different tools, and conflating them is how audit claims become marketing.

The project's own framing is the fairest summary of what it delivers: your agent tells you what it meant to do, and this tells you what it did. Whether the second half is true for your sessions is something you can check in a few minutes, which is more than most observability vendors offer.

## Primary sources checked

- Repository and README: https://github.com/bar181/bar-observatory
- Shipped example report (seven-session window, field counts and capture statuses): https://github.com/bar181/bar-observatory/blob/main/examples/deterministic/session.report.json
- Black-box verification script: https://github.com/bar181/bar-observatory/blob/main/tests/verify.sh
- Verification write-up, including stated limits: https://github.com/bar181/bar-observatory/blob/main/wiki/human-md/verification.md
- crates.io registry metadata: https://crates.io/api/v1/crates/bar-observatory
- GitHub repository metadata: https://api.github.com/repos/bar181/bar-observatory
- GitHub release objects: https://api.github.com/repos/bar181/bar-observatory/releases
- Claude Code environment-variable finding, April 2026: https://audited.xyz/blog/claude-code

All metadata above was read on 2026-10-19. The audit finding is scoped to Claude Code 2.1.92 remote-worker mode and is rated Low by its authors; it is cited as motivation for run evidence, not as a claim about the security of Bar Observatory.
