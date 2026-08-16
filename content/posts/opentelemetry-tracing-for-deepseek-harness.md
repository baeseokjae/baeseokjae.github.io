---
title: "OpenTelemetry Tracing for DeepSeek Harness: A Complete Setup Guide"
date: 2026-08-16T10:01:56+00:00
tags:
  - OpenTelemetry
  - DeepSeek Harness
  - Observability
  - LLM Tracing
  - GenAI
  - OTLP
  - Langfuse
  - Jaeger
description: "Learn how to add OpenTelemetry tracing to DeepSeek Harness with community plugins, OTLP export, and GenAI semantic conventions."
draft: false
cover:
  image: "/images/opentelemetry-tracing-for-deepseek-harness.png"
  alt: "OpenTelemetry Tracing for DeepSeek Harness"
  relative: false
schema: "schema-opentelemetry-tracing-for-deepseek-harness"
---

OpenTelemetry tracing for DeepSeek Harness lets you export every agent session, LLM call, and tool invocation as a standard OTLP trace tree to backends like Jaeger, Grafana Tempo, SigNoz, or Langfuse. You add it by installing a community plugin that implements the official `@deepseek-ai/dsh-session-telemetry` seam, configure an OTLP endpoint and a privacy mode, and then read the GenAI trace tree to debug agent loops, retries, and token usage.

## What is DeepSeek Harness and why it needs tracing

DeepSeek Harness is the official open-source agent framework from DeepSeek, written in TypeScript with the tagline "Everything is a Plugin." Its official repository has roughly 123,000 GitHub stars, making it one of the most popular agent harnesses in the ecosystem. The framework orchestrates multi-step agent loops: it plans, calls LLMs, invokes tools, spawns subagents, and retries failed steps. Each of those steps is a potential failure point, and without tracing you are effectively debugging a black box.

Agent loops are non-deterministic. A single user request can trigger dozens of LLM calls, tool invocations, and retries, and the failure often lives in the interaction between them rather than in any single call. Traditional logging gives you a flat stream of text with no causal structure. OpenTelemetry tracing gives you a hierarchical span tree that shows exactly which step produced which LLM call, which tool ran under which step, and which retries happened along the way.

For DeepSeek Harness specifically, tracing matters because of its plugin architecture. Because "everything is a plugin," the harness exposes a public telemetry seam that any plugin can implement. That means you are not locked into a single vendor's exporter. You can swap the official OTLP-logs exporter for a community OTLP-traces plugin without forking the harness, and you can point the output at whichever backend your team already runs.

## Understanding the telemetry seam (@deepseek-ai/dsh-session-telemetry)

The key architectural fact is that DeepSeek Harness ships a public telemetry seam called `@deepseek-ai/dsh-session-telemetry`. This is the contract that plugins implement to receive session, agent-loop, LLM-stream, and tool-lifecycle events. The official repository also ships an OTLP-logs exporter that implements this seam.

Community plugins implement the same seam as alternative backends. Instead of exporting logs, they convert the events into OpenTelemetry GenAI traces and metrics. Because they implement the same interface, you can drop them in without modifying the harness source code.

There is one critical gotcha: the telemetry seam accepts exactly one backend per context. If you load a duplicate backend — for example, the official OTLP-logs exporter and a tracing plugin at the same time — the load throws an error. You must choose one backend per context, not stack them.

## Choosing an OpenTelemetry backend (Jaeger, Grafana Tempo, SigNoz, Langfuse)

Because the plugins export standard OTLP/HTTP protobuf, you can send traces to any compatible backend. The table below compares the most common choices.

| Backend | Best for | OTLP support | GenAI semconv | Notes |
|---------|----------|--------------|---------------|-------|
| Jaeger | Lightweight local debugging | Yes | Partial | Fast to spin up with Docker; great for single-node dev |
| Grafana Tempo | Grafana stack users | Yes | Yes | Pairs with Grafana dashboards and Loki logs |
| SigNoz | Open-source APM alternative | Yes | Yes | Full APM with metrics, traces, and logs in one |
| Langfuse | LLM product teams | Yes | Yes | Native LLM features: feedback scores, sessions, prompts |

The GenAI semantic conventions (semconv) are what make these traces portable. They standardize LLM span attributes — model name, provider, token usage, prompt and completion — so the same trace renders meaningfully in Jaeger, Tempo, SigNoz, and Langfuse alike. If you already run one of these backends, you do not need to stand up a new one.

## Installing a dsh OpenTelemetry tracing plugin

The most popular community options are `loongsuite/dsh-plugin`, `linyp/dsh-plugin-langfuse`, `CodePrometheus/dsh-observability`, and `TtTRz/dsh-langfuse`. All of them implement the telemetry seam and export OTLP traces. The table below summarizes their differences.

| Plugin | Backend target | Trace shape | Metrics | Notable config |
|--------|----------------|-------------|---------|----------------|
| loongsuite/dsh-plugin | Any OTLP backend | ENTRY -> AGENT -> STEP -> LLM/TOOL | gen_ai.client.operation.duration, gen_ai.client.token.usage | Standalone, no sidecar or vendor dependency |
| linyp/dsh-plugin-langfuse | Langfuse | One trace per turn, grouped by session | No | Reads LANGFUSE_HOST; feedback as Langfuse Scores |
| CodePrometheus/dsh-observability | Any OTLP backend | Session span tree, model step to child span | No | DSH_OBSERVABILITY_MODE and DSH_OBSERVABILITY_OTLP_URL |
| TtTRz/dsh-langfuse | Langfuse | One trace tree per session | No | Feedback scores and subagent lineage |

Before installing, verify your environment meets the requirements. The telemetry plugins require Node.js version 22.19.0 or higher and a DeepSeek Harness version of at least 0.1.0-rc.6 and below 0.2.0. If your harness is older or newer than that range, the plugin may not load.

Installation is typically done as a profile bundle. For example, the Langfuse plugin installs via a `cordis.patch.yml` profile bundle, and it reads the `LANGFUSE_HOST` environment variable rather than `LANGFUSE_BASE_URL`. Check each plugin's README for the exact install command, because the bundle mechanism differs slightly between plugins.

## Configuring OTLP export and privacy modes (FULL / FEEDBACK_ONLY / DISABLED)

Privacy is a first-class concern in these plugins. The design principle is that sharing stays off until a mode explicitly says otherwise, and configuring an endpoint is not consent to upload session content. You must opt in to each level of data sharing.

The `CodePrometheus/dsh-observability` plugin exposes three modes through the `DSH_OBSERVABILITY_MODE` environment variable:

- **FULL** — exports the complete session content, including prompts, completions, and tool payloads. Use this only for backends you trust and for data you are allowed to share.
- **FEEDBACK_ONLY** — exports only feedback and scoring data, without the underlying session content. This is a middle ground for teams that want evaluation signals without shipping raw prompts.
- **DISABLED** — turns off sharing entirely. This is the safe default.

You also configure the OTLP endpoint, typically through a variable such as `DSH_OBSERVABILITY_OTLP_URL` or the plugin's own endpoint setting. The endpoint points at your chosen backend's OTLP/HTTP receiver. Remember that setting the endpoint alone does not enable content sharing; the mode controls that.

## Reading the GenAI trace tree (ENTRY -> AGENT -> STEP -> LLM/TOOL)

The trace shape is the most valuable part of the setup. The `loongsuite/dsh-plugin` exports a hierarchy of `ENTRY -> AGENT -> STEP -> LLM/TOOL`. Here is what each level means:

- **ENTRY** — the root span for a session or a top-level request.
- **AGENT** — the agent loop that orchestrates the work.
- **STEP** — a single planning or execution step within the loop.
- **LLM/TOOL** — the individual LLM call or tool invocation that ran under that step.

The critical design detail is that each real LLM attempt gets its own LLM span. If the harness retries a failed LLM call, each retry appears as a separate span under the same step. This keeps retries and tool fallbacks visible under the same step, which is exactly what you need when debugging flaky agent loops. Instead of seeing one opaque "LLM call failed" message, you see the full sequence of attempts and their individual latencies and token usage.

Subagent sessions create their own trace and carry DeepSeek Harness parent-session and delegation attributes. This preserves fork and subagent lineage, so you can follow a request from the parent session down into each delegated subagent and back.

The plugins also export GenAI metrics. The `loongsuite/dsh-plugin` exports `gen_ai.client.operation.duration` and `gen_ai.client.token.usage`, giving you latency and token-cost telemetry alongside the traces.

## Troubleshooting common issues (duplicate backend, version compatibility, restart required)

The most common problems fall into three buckets.

**Duplicate backend error.** Because the telemetry seam accepts exactly one backend per context, loading the official OTLP-logs exporter and a tracing plugin together throws an error. Remove or disable the official exporter before loading a tracing plugin. If you need both logs and traces, choose one backend that handles both, or run them in separate contexts.

**Version incompatibility.** The plugins require Node.js 22.19.0+ and DSH between 0.1.0-rc.6 and 0.2.0. If the plugin fails to load, check your Node and harness versions first. A harness outside the supported range will reject the plugin.

**Restart required.** Telemetry backends are typically loaded at startup. After installing a plugin or changing a mode or endpoint variable, restart the harness so the new backend is picked up. A running session will not hot-reload the telemetry seam.

**No traces appearing.** If your backend shows no traces, verify the OTLP endpoint is reachable, confirm the mode is not `DISABLED`, and check that the plugin actually loaded without a duplicate-backend error. Also confirm the backend's OTLP/HTTP receiver is enabled, since some backends disable it by default.

## FAQ

**What is OpenTelemetry tracing for DeepSeek Harness?**
It is a way to export DeepSeek Harness agent sessions, LLM calls, and tool invocations as standard OTLP trace trees to backends like Jaeger, Grafana Tempo, SigNoz, or Langfuse, using community plugins that implement the official telemetry seam.

**Which DeepSeek Harness versions support OpenTelemetry tracing plugins?**
The telemetry plugins require Node.js 22.19.0 or higher and a DeepSeek Harness version of at least 0.1.0-rc.6 and below 0.2.0.

**Can I use OpenTelemetry tracing with Langfuse?**
Yes. Plugins like `linyp/dsh-plugin-langfuse` and `TtTRz/dsh-langfuse` export each session or turn as an OpenTelemetry trace to Langfuse's OTLP endpoint, including feedback scores and subagent lineage.

**Why do I get a duplicate backend error when installing a tracing plugin?**
The `@deepseek-ai/dsh-session-telemetry` seam accepts exactly one backend per context. If you load the official OTLP-logs exporter and a tracing plugin together, the load throws an error. Remove the official exporter before loading a tracing plugin.

**How do privacy modes work in DeepSeek Harness tracing plugins?**
Plugins like `CodePrometheus/dsh-observability` use modes such as FULL, FEEDBACK_ONLY, and DISABLED. Sharing stays off until a mode explicitly enables it, and configuring an endpoint is not consent to upload session content.
