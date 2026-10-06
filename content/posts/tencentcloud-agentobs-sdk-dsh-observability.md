---
title: "TencentCloud AgentObs SDK for DeepSeek Harness Review: DSH Agent Observability in 2026"
date: 2026-10-01T05:41:05+00:00
tags:
  - dsh agent observability
  - tencentcloud agentobs sdk dsh review
  - cls agent observability
  - deepseek harness trace cls
  - tencent cloud agent observability dsh
  - agentobs sdk vs loongsuite dsh-plugin
  - dsh plugin cls vs opentelemetry
  - tencentcloud-agentobs-sdk-dsh install
  - cls genai trace pricing
  - capturecontent privacy deepseek harness
  - dsh session telemetry seam one backend
  - 5-layer span model entry agent step chat tool
  - deepseek harness observability review 2026
  - tencent cloud log service trace ingestion cost
description: "Six weeks of evidence on the TencentCloud AgentObs DSH plugin: privacy defaults, real CLS cost math, adoption numbers, and when OTLP wins instead."
draft: false
cover:
  image: "/images/tencentcloud-agentobs-sdk-dsh-observability.png"
  alt: "TencentCloud AgentObs SDK for DeepSeek Harness Review: DSH Agent Observability in 2026"
  relative: false
schema: "schema-tencentcloud-agentobs-sdk-dsh-observability"
---

For most teams evaluating dsh agent observability, the TencentCloud AgentObs SDK for DeepSeek Harness is worth adopting only if you already run Tencent Cloud Log Service. Six weeks after its first release, the evidence is mixed: solid engineering, thin adoption (14 stars, 519 npm downloads in 30 days), a privacy default that ships content capture ON, and a zero-collector architecture that replaces infrastructure you operate with metered consumption you must now watch. If you are not already a CLS customer, the community OpenTelemetry plugin is the safer default.

That is the short answer. This review is the third act in a series: we covered the [OpenTelemetry tracing route for DeepSeek Harness](/posts/opentelemetry-tracing-for-deepseek-harness) in August 2026, and we published the [installation walkthrough for this specific plugin](/posts/tencentcloud-agentobs-dsh-genai-traces) on 20 August 2026. This post does not repeat either. It is a source-backed judgement written after six weeks of releases, download telemetry and price sheets, and it is aimed at the decision rather than the setup.

## Review Scope: What Six Weeks of Evidence Changed About This Plugin

When a first-party SDK appears, the honest question is not "does it work" but "has it been adopted, and is the vendor still behind it." Three data points answer that.

| Signal | TencentCloud AgentObs DSH | @loongsuite/dsh-plugin |
|---|---|---|
| GitHub stars | 14 | 26 |
| Forks | 3 | 4 |
| Open issues | 0 | 5 |
| Latest release | v0.0.1 (18 Aug 2026) | v0.1.2 (25 Aug 2026) |
| Last push | 26 Aug 2026 | active |
| npm downloads, 30 days | 519 | 1,978 |
| npm downloads, 7 days | 121 | 789 |
| License | Apache-2.0 | Apache-2.0 |

The OpenTelemetry competitor draws roughly **3.8x the monthly downloads and 6.5x the weekly downloads** of the Tencent plugin. Weekly-to-monthly ratio matters here: 789 of 1,978 (40%) downloads landed in the last week for the OTel plugin, versus 121 of 519 (23%) for Tencent's. The community plugin is accelerating; the first-party one is flattening.

None of that is a verdict on code quality. The Tencent plugin is at 0.1.0, six weeks old, with zero open issues — which in a low-adoption repository often means nobody has filed one rather than that nothing is wrong. Read the numbers as maturity evidence, not as a scoreboard.

There is also a version-hygiene detail worth noting: the GitHub release tag is **v0.0.1** while the npm package's latest version is **0.1.0**. Both were first published on 18 August 2026; the npm package was last modified 26 August 2026. If your upgrade tooling reads npm and your changelog reads GitHub releases, those two streams are telling you different stories.

## What the AgentObs DSH Plugin Does (Short Recap)

The plugin observes DeepSeek Harness's native session, agent-loop, LLM-stream and tool-lifecycle events and converts them into Tencent Cloud's five-layer span model — entry, agent, step, chat, tool. It ships spans as Protobuf directly to Tencent Cloud Log Service through `tencentcloud-cls-sdk-js`, with no OTLP collector and no sidecar.

If you need the install steps, the profile-add command, the `pnpm approve-builds` workaround, the full configuration table or the span-nesting diagram, they are all in the [original setup guide](/posts/tencentcloud-agentobs-dsh-genai-traces). What follows assumes you have read that and are deciding whether to keep it.

## Adoption Check: Stars, npm Downloads and Release Cadence Against the Competition

Two details in the table above deserve separating from the raw counts.

First, **0 open issues is not the same as 0 defects**. The loongsuite plugin's five open issues are a sign of an active user base stress-testing edge cases — retries, aborts, content-capture boundaries. A repository with 519 monthly downloads and no issue tracker activity has not yet been pushed hard. Treat the Tencent plugin's bug surface as *unknown* rather than *clean*.

Second, **download counts measure installs, not retention**. 519 downloads in 30 days for a zero-collector plugin whose headline promise is "skip the collector" is modest. If that promise were the decisive advantage it sounds like, you would expect the ease-of-adoption curve to favour Tencent's plugin, not the community one — especially given Tencent's plugin supports Node.js >=18.0.0 while the loongsuite plugin requires Node.js >=22.19.0. The plugin that runs on more machines is being installed on fewer. That gap is the most interesting number in this review, and it points at the harness-ecosystem question rather than at Tencent's engineering.

The most likely explanation is stack gravity: DeepSeek Harness users are largely picking their observability backend first (Jaeger, Tempo, SigNoz, Langfuse) and their ingestion plugin second. A backend-native plugin only wins when the backend is already decided.

## Privacy Defaults Compared: captureContent True vs Off

This is the section to read before anything else, because it is the only difference in this comparison that can cause an incident rather than an inconvenience.

| Behaviour | TencentCloud AgentObs DSH | @loongsuite/dsh-plugin |
|---|---|---|
| Content capture default | **ON** (`captureContent: true`) | **OFF** |
| Content cap | `contentMaxChars` 128,000 | applies when enabled |
| What gets attached | prompts, responses, tool arguments, tool results | same fields, when enabled |
| Destination | your CLS topic | your OTLP backend |

A DeepSeek Harness coding session is not a chat session. It reads source trees, `.env` files, CI configuration, infrastructure manifests, database dumps and arbitrary tool output. With content capture on by default and a 128,000-character per-item cap, a single traced turn can carry a substantial slice of a private repository into a hosted log service — at 128K characters, that is on the order of 30,000 tokens of payload per captured item, and tool results can be several such items per step.

The defence is one configuration line. The problem is that defaults are what actually ship. In a plugin shipped by a cloud vendor to that vendor's own log service, default-on capture is a defensible product decision — the vendor's console demo depends on having content to display. But it means the *installation* is the compliance decision, not a later checkbox. If you roll this out to a fleet by profile, every developer inherits a capture-on posture unless the profile explicitly says otherwise.

Two mitigations, in order of preference:

1. Set `captureContent: false` in the profile before rollout, and enable it per-developer only when debugging. This also cuts payload volume by roughly an order of magnitude — see the cost section for what that is worth.
2. If you need content, lower `contentMaxChars` aggressively (a few thousand characters, not 128,000), scope the CLS topic's retention, and treat the topic as you would a secrets-adjacent data store.

The OTel competitor's off-by-default posture is the correct default for a coding agent, and it is the single strongest argument in this review for choosing it.

## What It Actually Costs: CLS Ingestion Math for a Realistic DSH Workload

"Zero collector" removes infrastructure, not cost. It moves the spend from a server you run to consumption you meter, and in CLS the meter has several line items that behave differently.

Chinese mainland pay-as-you-go list prices from [Tencent Cloud's CLS pricing page](https://www.tencentcloud.com/pricing/cls):

| Line item | Rate | Billed on |
|---|---|---|
| Log write traffic | USD 0.032 / GB / day | **compressed** volume |
| Standard index traffic | USD 0.062 / GB / day | **uncompressed** volume |
| Standard log storage | USD 0.0024 / GB / day | **compressed** volume |
| Standard index storage | USD 0.0024 / GB / day | **uncompressed** volume |
| Data processing | USD 0.026 / GB / day | compressed volume |
| Partition | USD 0.007 / partition / day | fixed |
| Service requests | USD 0.026 / million / day | count |

The asymmetry is the whole story: **index traffic costs roughly 2x write traffic and is charged on uncompressed bytes**, while write traffic and storage are charged on compressed bytes (typical log compression runs 1:4 to 1:10). Tencent's own worked billing examples show index traffic and index storage as the two largest line items. Your bill follows *how many span fields you index*, not how many traces you emit.

Working through a realistic DSH fleet, assuming 58 spans per agent task, 1:4 compression, one partition, and 35% of raw volume carrying indexed fields:

| Daily agent tasks | Raw volume | Variable cost / month | Partition / month | Total / month |
|---|---|---|---|---|
| 10 | 17 MB/day | $0.02 | $0.21 | $0.23 |
| 25 | 43 MB/day | $0.05 | $0.21 | $0.26 |
| 100 | 170 MB/day | $0.20 | $0.21 | $0.41 |
| 1,000 | 1.7 GB/day | $1.96 | $0.21 | $2.17 |
| 5,000 | 8.5 GB/day | $9.82 | $0.21 | $10.03 |
| 20,000 | 34 GB/day | $39.29 | $0.21 | $39.50 |

Two conclusions fall out of this and both are counter-intuitive.

**At small scale, the fixed partition charge dominates and the whole thing is nearly free.** A team running 10 to 100 agent tasks a day pays well under a dollar a month. Anyone running a self-hosted Jaeger or Tempo instance to avoid that is spending far more on the VM than the metered alternative costs.

**At large scale, content capture — not trace count — sets the bill.** Recomputing the 20,000-task-per-day case with span payloads of 30 KB instead of 8 KB (which is what capture-on looks like once prompts and tool results are attached):

- index 0% of volume: **$16.84/month**
- index 10%: **$23.26/month**
- index 35%: **$39.29/month**
- index 60%: **$55.32/month**
- index 100%: **$80.96/month**

That is a 4.8x spread on the same traces, driven entirely by index configuration — and the index ratio is the lever most teams never touch. Combined with the capture-on/off comparison at 1,000 tasks per day (about $1.96/month with capture on versus $0.22/month with it off), disabling content capture is simultaneously the strongest privacy control and roughly a 9x cost reduction.

Where self-hosting wins is a narrow band. A $12/month VM running Jaeger or Tempo has near-zero marginal ingestion cost, which beats CLS somewhere above 5,000 to 20,000 agent tasks per day depending on payload size. Below that, the arithmetic favours CLS unless you already own the infrastructure for other reasons. Above it, the arithmetic still favours CLS if you have turned indexing down — at 0% indexing the same 20,000-task workload is $16.84/month against $12/month plus your operational time.

Resource packs are denominated in U, where 1U = CNY 1, and can offset any billable item. A "billed on raw log volume" mode exists but is whitelist-only, so do not plan around it.

## Transport Showdown: Protobuf-to-CLS Versus Standard OTLP

The transport choice is where portability is decided, and it is decided against you.

| Dimension | AgentObs DSH | loongsuite dsh-plugin |
|---|---|---|
| Wire format | Protobuf, CLS-specific | OTLP/HTTP protobuf |
| Destination | Tencent Cloud Log Service topic | any OTLP backend |
| Backends reachable | CLS | Jaeger, Tempo, SigNoz, Langfuse, and others |
| Auth | SecretId/SecretKey (strong) or numeric UIN (weak) | backend-defined |
| Metrics | traces documented | `gen_ai.client.operation.duration`, `gen_ai.client.token.usage` |
| Vendor dependency | `tencentcloud-cls-sdk-js` | OpenTelemetry SDK stack |
| Runtime dependencies | 2 | OTel SDK stack |

Two structural facts matter more than the table.

First, **the Tencent plugin's documented surface is traces**, while the OTel plugin also exports the standard GenAI metrics (`gen_ai.client.operation.duration` and `gen_ai.client.token.usage`). Metrics are what you alert on cheaply and continuously; traces are what you open when an alert fires. A traces-only integration puts more weight on your log backend's query and dashboard features.

Second, **the auth modes are a real operational split**. Strong auth via `CLS_SECRET_ID` and `CLS_SECRET_KEY` is the right choice, but it is a long-lived credential that the plugin holds and that will one day expire or get rotated out from under a running fleet. Weak auth with a numeric UIN and no key removes the secret but weakens the trust boundary. Neither mode gives you the short-lived, workload-identity-style credentials you would want for a fleet. Plan the rotation before you plan the rollout.

The portability question reduces to: **can I replay the same trace into another backend?** The answer for this plugin is no, not without rewriting the export path. The CLS-bound field mapping and the Protobuf-to-CLS transport are what leave with your data. That is a fair trade for a CLS-native team and a poor one for everyone else.

## The One-Backend Rule: Why You Cannot Run This and the OpenTelemetry Plugin Together

This is the constraint that changes the shape of the decision, and it is frequently missed.

DeepSeek Harness ships a public telemetry seam, `@deepseek-ai/dsh-session-telemetry` (v0.0.1-rc.1, published 10 August 2026, BSD-3-Clause), described as "session-event capture, projection, redaction, and handoff to a reporting backend." The seam accepts **exactly one backend per context**. Loading a duplicate — the official OTLP-logs exporter plus a tracing plugin, or two tracing plugins at once — throws an error at load time.

The practical consequences:

- DSH tracing plugins are **mutually exclusive, not stackable**. You cannot run the Tencent plugin and the OpenTelemetry plugin side by side to compare them.
- The harness also ships its own OTLP-logs exporter implementing the same seam, so choosing a tracing plugin means **replacing** the official exporter, not adding to it.
- The choice is made **at install time, per profile**. It is not a runtime toggle.

Because of this, a side-by-side evaluation requires two profiles, not two plugins. And it means the cost of reversing the decision is a profile edit plus a lost ingestion history: trace data already written to CLS stays in CLS, and nothing backfills into a Jaeger instance you switch to later.

Practical advice: if you are unsure, evaluate on a second profile first, with a bounded time box. Since you cannot run both, the migration cost is real and asymmetric — switching *to* CLS is cheap, switching *away* from it means abandoning the collected history.

## Runtime Behaviour: Batching, Queue Drops, Retries and Silent Failures

The plugin's buffering behaviour is documented and, on balance, sensible. It is also where you should focus your alerting.

| Parameter | Default | Consequence |
|---|---|---|
| `batchMaxSize` | 32 spans | batch granularity |
| `maxBatchBytes` | 10 MB | must stay under the CLS SDK's 19 MB hard limit |
| `maxQueueSize` | 2,048 spans | oldest span dropped when full |
| `flushIntervalMs` | 5,000 ms | up to 5s of trace delay |
| `retryTimes` | 3 | failed batch retried three times |
| `contentMaxChars` | 128,000 | per captured item |

Three behaviours deserve reframing rather than fixing.

**Queue overflow silently drops the oldest span.** At 2,048 buffered spans the plugin discards from the head of the queue to keep the harness responsive. This is a backpressure design, not a bug — and crucially, **it is a signal**. Steady-state dropping means your ingestion path cannot keep up with your agent workload, which is exactly the condition you want an alert on. Monitor for it rather than treating it as noise. The subtlety is that dropping the oldest span preserves recent context at the cost of the start of a long-running task — the part you often need to explain why a long task went wrong.

**`maxBatchBytes` must stay below 19 MB.** Exceed the CLS SDK's hard limit and the entire batch is rejected locally, not by the server. With capture on and a large tool result, a single oversized batch can take its sibling spans down with it. Lower the batch byte cap before you lower the content cap.

**An expired CLS key fails quietly from the harness's point of view.** A 401 from CLS does not fail the agent run — the harness exits 0, the developer sees a normal session, and traces simply stop appearing. From the harness's perspective this is correct: observability must never break the workload. From an operations perspective it means **"no traces" and "no problems" look identical**. You need a synthetic check that asserts a known trace lands in the topic on a schedule, independent of the plugin's own success reporting.

The other two documented failure modes are installation-stage and cheap to avoid: on pnpm v9+, protobufjs build scripts are blocked by default, producing `ERR_PNPM_IGNORED_BUILDS` until you set `enable-scripts=true` and reinstall; and the plugin does not attach until the harness is restarted after installation.

## Compatibility Windows and the 0.2.0 Cliff

Both leading plugins pin the same harness window — `>=0.1.0-rc.6` and `<0.2.0` — and both warn that outside that range lifecycle hooks may simply not fire. The failure mode is the nasty kind: nothing crashes, traces just stop.

| Constraint | AgentObs DSH | loongsuite dsh-plugin |
|---|---|---|
| DSH version window | >=0.1.0-rc.6, <0.2.0 | >=0.1.0-rc.6, <0.2.0 |
| Node.js floor | **>=18.0.0** | >=22.19.0 |
| Verified on | not stated publicly | 0.1.0-rc.6 headless and Web profiles |

The **Node.js floor is the most underrated difference**. Tencent's plugin supports Node >=18, three major versions lower than the OTel plugin's >=22.19.0. For a fleet still running Node 20 on older build images, this is the difference between a same-day rollout and a toolchain upgrade project. It is a genuine adoption advantage and it is the strongest technical argument for the Tencent plugin.

The 0.2.0 cliff is shared and asymmetric in effect. Both plugins break at the same boundary, but the recovery paths differ: the OTel plugin's users can pin the harness and keep exporting to a backend they control, while CLS users are dependent on Tencent shipping a 0.2.0-compatible update. Given the release cadence observed here — one tag in six weeks, no push since 26 August — that dependency carries schedule risk. Pin your harness version and treat the DSH upgrade as a change that requires an observability regression test.

## Feature-by-Feature: AgentObs vs loongsuite vs the Langfuse Plugin

A third option is worth including, because it represents a different philosophy rather than a different vendor.

| Capability | TencentCloud AgentObs DSH | @loongsuite/dsh-plugin | dsh-plugin-langfuse |
|---|---|---|---|
| Version | 0.1.0 (npm) | v0.1.2 | v0.7.0 |
| Philosophy | backend-native | backend-neutral | LLM-product-team |
| Transport | Protobuf to CLS | OTLP/HTTP | Langfuse SDK via the telemetry seam |
| Span shape | ENTRY → AGENT → STEP → CHAT/TOOL | ENTRY → AGENT → STEP → LLM/TOOL | step → generation, tool call → tool span |
| Per-retry LLM span | not documented | yes | not documented |
| Error/abort closes spans | not documented | yes | not documented |
| Metrics exported | not documented | `gen_ai.*` standard metrics | Langfuse Scores for feedback |
| Content capture default | ON | OFF | backend-configured |
| Session grouping | via CLS topic | via OTLP resource attributes | explicit, per session |
| Subagent/fork lineage | not documented | not documented | preserved |
| Node.js floor | >=18.0.0 | >=22.19.0 | not stated |
| Backends reachable | CLS only | Jaeger, Tempo, SigNoz, Langfuse | Langfuse |

Three capability gaps stand out against the OTel plugin, all of which matter for debugging agent behaviour rather than for basic tracing.

**Per-retry LLM spans.** If a model call fails and retries within the same step, the OTel plugin emits a distinct LLM span per real attempt, so you can see that three calls happened and one succeeded. Whether the Tencent plugin does the same is not documented — which means you should not assume you will be able to distinguish "one slow model call" from "three retried calls" in CLS without testing it yourself.

**Error and abort handling.** The OTel plugin closes spans with error status rather than leaving them open. Left-open spans are the classic reason a trace view shows an agent turn as still running hours after it died.

**Correlation of tool calls to results** by DSH call ID is explicitly documented for the OTel plugin. Tool-call correlation is the single most useful feature of coding-agent tracing, because it tells you *which* tool call consumed the time.

The Langfuse plugin occupies its own niche: it groups traces by session, records canonical feedback as Langfuse Scores, and preserves fork and subagent lineage — capabilities neither of the other two advertise. For teams whose observability questions are about output quality and iteration rather than infrastructure, it is the closest fit to the question being asked.

The honest summary: the Tencent plugin competes on deployment simplicity and Node.js reach; the OTel plugin competes on trace semantics and portability; the Langfuse plugin competes on session-level product analytics.

## Who Should Use the TencentCloud AgentObs SDK in October 2026

There is no single winner, so here is the decision matrix instead of a verdict.

**Use it if:**

- You are already a Tencent Cloud customer with existing CLS topics, retention policies and alerting. Traces landing in the same console as the rest of your logs makes cost correlation and retention management free instead of another silo.
- Your fleet runs Node.js 18 or 20. The Node.js floor is the clearest technical win in this comparison.
- Your agent volume is modest — under a few thousand tasks a day — where the bill is a few dollars a month and a self-hosted stack is disproportionate overhead.
- Your organisation has already decided that DSH traces belong in CLS, which is a stack decision above the plugin.

**Skip it if:**

- You are not on Tencent Cloud. You would be buying lock-in to save one deployment step that SigNoz or Langfuse already match.
- You need content capture off by default across a fleet without managing a profile override. The OTel plugin's default is correct for a coding agent; this one's is not.
- You depend on documented per-retry spans, error-closed spans and tool-call correlation. The Tencent plugin does not publish those semantics.
- Your harness will move past 0.2.0 on a schedule you control. Both plugins break there, but only one leaves you free to pin and keep tracing to your own backend.
- You need vendor-neutral metrics, or the ability to replay one trace into two backends.

**The migration cost to weigh before deciding:** because of the one-backend rule, you cannot hedge. Switching to CLS is cheap; switching away abandons the history you have already written. If there is any chance your observability strategy moves toward a neutral backend, start there and stay there.

## FAQ

### Is the TencentCloud AgentObs SDK worth using for dsh agent observability?

Yes, if you already run Tencent Cloud Log Service and want traces with no collector to operate. No, if you are not a CLS customer, need content capture off by default, or want vendor-neutral trace semantics. It is a strong fit inside the Tencent Cloud stack and a lock-in purchase outside it.

### Does the TencentCloud AgentObs SDK capture prompts and tool output by default?

Yes. It ships with `captureContent: true` and a `contentMaxChars` cap of 128,000, which attaches prompts, responses, tool arguments and tool results to spans by default. The community OpenTelemetry plugin ships content capture off by default. For a coding agent that reads source trees and `.env` files, disable it in the profile before rolling out.

### How much does CLS Agent Observability cost for a DSH fleet?

At small scale, very little: roughly $0.20 to $0.45 per month for 10 to 100 agent tasks a day, where the fixed partition charge dominates. At 20,000 tasks a day, the variable bill runs about $39 per month at a 35% index ratio, or about $17 per month with indexing disabled. Index traffic is billed on uncompressed volume at roughly 2x the write-traffic rate, so index configuration — not trace count — drives the bill.

### Can I run the TencentCloud AgentObs SDK alongside an OpenTelemetry tracing plugin?

No. The DeepSeek Harness telemetry seam `@deepseek-ai/dsh-session-telemetry` accepts exactly one backend per context and throws at load time if you register a second. The Tencent plugin, the OTel plugins and the harness's own OTLP-logs exporter are mutually exclusive; evaluating two of them requires two separate profiles.

### What happens if my CLS credentials expire while the plugin is running?

The harness does not fail. A 401 from CLS leaves the agent run successful and the process exits 0, while traces silently stop appearing. Because observability failures are deliberately non-fatal to the workload, "no traces" and "no problems" look identical — add an independent synthetic check that asserts a known trace lands in your topic on a schedule.
