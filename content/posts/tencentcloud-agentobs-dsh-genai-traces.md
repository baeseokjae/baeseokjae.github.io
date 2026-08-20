---
title: "TencentCloud AgentObs SDK for DeepSeek Harness: Zero-Collector GenAI Trace Observability"
date: 2026-08-20T07:02:10+00:00
tags:
  - DeepSeek Harness
  - Observability
  - Tencent Cloud
  - GenAI Tracing
  - AI Agents
description: "Add deepseek harness observability without an OTLP collector: the TencentCloud AgentObs DSH plugin pushes GenAI traces straight to CLS."
draft: false
cover:
  image: "/images/tencentcloud-agentobs-dsh-genai-traces.png"
  alt: "TencentCloud AgentObs SDK for DeepSeek Harness"
  relative: false
schema: "schema-tencentcloud-agentobs-dsh-genai-traces"
---

DeepSeek Harness observability usually means standing up an OpenTelemetry collector, a tracing backend, and code instrumentation. The TencentCloud AgentObs SDK for DSH eliminates all of that: it is a DeepSeek Harness plugin that observes the harness's native session, agent-loop, LLM-stream, and tool lifecycles and uploads GenAI trace spans directly to Tencent Cloud Log Service (CLS) using Protobuf. There is no OTLP collector, no sidecar, and no extra service to deploy. If you already run agents on Tencent Cloud, this is the fastest path from "where did my agent spend its tokens?" to a dashboards-and-alerts answer.

## What is the TencentCloud AgentObs SDK for DeepSeek Harness?

The TencentCloud AgentObs SDK for DSH (`tencentcloud-agentobs-sdk-dsh`) is a first-party observability plugin for DeepSeek Harness. Rather than treating DSH as a black box that you instrument from the outside, it hooks directly into the harness's own lifecycle events. Those events — a session starting, an agent being invoked, each ReAct round, an LLM stream, and every tool execution — are converted into spans that follow Tencent Cloud's AI Agent observability specification, then shipped to CLS through the official `tencentcloud-cls-sdk-js` transport.

The key architectural decision is that the plugin is transport-native to a cloud vendor's log service. Where most DSH observability plugins speak OpenTelemetry and require an OTLP endpoint, this one talks Protobuf directly to Tencent Cloud Log Service. For teams already paying for CLS, that removes an entire class of operational burden.

## How does DSH GenAI trace observability work without a collector?

The zero-collector architecture is the plugin's defining feature. The data path is short and self-contained:

1. DeepSeek Harness fires native lifecycle events during a session.
2. The AgentObs plugin's CLS Trace Coordinator receives those events.
3. Each event is normalized into Tencent Cloud's 5-layer span model.
4. Spans are batched and serialized with `tencentcloud-cls-sdk-js` (Protobuf).
5. Batches are uploaded directly to a CLS topic over HTTPS.

There is no OpenTelemetry Collector to run, no Jaeger or SigNoz backend to maintain, and no sidecar container to schedule. Contrast that with the standard OpenTelemetry DeepSeek approach, which requires you to deploy an OTLP receiver and run `opentelemetry-distro` instrumentation on top of an OpenAI-compatible SDK. That approach is portable and vendor-neutral, but it is also infrastructure you must operate. The Tencent plugin trades portability for a dramatically simpler deploy.

## What is the 5-layer span model for AI agent observability?

Tencent Cloud's AI Agent observability spec organizes traces into a five-layer span hierarchy: entry, agent, step, chat, and tool. The plugin maps DSH's native lifecycle onto that model, so a single DSH turn produces a nested trace:

```
ENTRY
└── AGENT (invoke_agent)
    └── STEP (react round_N)
        ├── CHAT (chat model_name)
        └── TOOL (execute_tool tool_name)
```

This nesting is what makes the trace useful. Instead of a flat list of spans, you see the whole shape of an agent turn: which round of ReAct a tool call happened in, which model answered which prompt, and where the time and tokens actually went. When you open a trace in CLS, you can drill from the top-level entry down to a single tool invocation in a specific reasoning step.

## What span semantics are recorded under the hood?

The plugin does not invent a proprietary trace format; it aligns with OpenTelemetry conventions. Each span carries the standard identifiers and metadata you would expect from a well-behaved tracer:

- `traceID` as a 32-hex-character string
- `spanID` and `parentSpanID` as 16-hex-character strings
- OpenTelemetry span kinds (`INTERNAL`, `CLIENT`, `SERVER`)
- Status codes (`OK`, `ERROR`, `UNSET`)
- Nanosecond-precision start, end, and duration fields
- Token usage and model identifiers on chat spans

This OTel alignment matters for two reasons. First, it keeps the data recognizable to engineers already comfortable with distributed tracing. Second, it makes correlation possible inside Tencent Cloud: because spans live in CLS, you can join GenAI traces against logs, metrics, and cost analytics in the same log platform, enabling session-to-token-cost analysis without a separate tracing database.

## How do I install the DSH plugin?

Installation uses DeepSeek Harness's native plugin mechanism. You add the plugin to whichever profile you are running, then restart the harness for it to take effect:

```bash
dsh plugin --profile web add tencentcloud-agentobs-sdk-dsh
# or
dsh plugin --profile headless add tencentcloud-agentobs-sdk-dsh
# or
dsh plugin --profile harness add tencentcloud-agentobs-sdk-dsh
```

Because the profile flag selects where the plugin applies, you can enable tracing only on the headless automation profile and leave interactive sessions untouched — or vice versa. The restart requirement is worth remembering: adding the plugin is not enough, DeepSeek Harness must be restarted before the observer attaches.

One installation pitfall applies to pnpm v9 or later. The plugin depends on `protobufjs`, which has a build script. Modern pnpm blocks build scripts by default, so you must approve them or the Protobuf serialization layer will not build:

```bash
pnpm approve-builds
```

## How do I configure the plugin?

Configuration is handled either through environment variables or through a `cordis.patch.yml` file in the profile directory. The environment variable path is the quickest for a single deployment:

| Setting | Environment variable | Default |
| --- | --- | --- |
| CLS endpoint | `CLS_ENDPOINT` | — |
| CLS topic ID | `CLS_TOPIC_ID` | — |
| Secret ID | `CLS_SECRET_ID` | — |
| Secret key | `CLS_SECRET_KEY` | — |
| Service name | `CLS_SERVICE_NAME` | — |
| Content capture | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | `true` |

The four credentials — endpoint, topic, secret ID, and secret key — are mandatory; without them the plugin has nowhere to write spans. The service name is how you identify this deployment inside CLS, so give it a value that distinguishes environments, for example `dsh-prod-web`.

For teams that prefer declarative config checked into the repo, `cordis.patch.yml` under the profile is the alternative. It carries the same options in YAML form and keeps secrets out of shell history — though you should still externalize the actual secret values through your secret manager rather than committing them.

## Should I capture prompts, responses, and tool content?

Content capture is on by default, and this is the feature that demands the most attention. With capture enabled, the plugin attaches prompts, LLM responses, and tool arguments and results to their spans. That gives you searchable, debuggable traces — but it also means credentials, source code, and personally identifiable information can be shipped to CLS as part of a trace.

The trade-off is real, and the brief is unambiguous: content capture can leak sensitive data into a cloud log service. You control the blast radius with two levers:

- `captureContent: false` (or `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`) disables content attachment entirely, leaving only span structure, timing, and metadata.
- `contentMaxChars`, defaulting to 128000, caps how much content a single span carries so a pathological tool result does not bloat a topic.

For anything that touches production data, plan a content policy before you enable the plugin. Trace structure and timing usually survive with capture off; if you need content, apply the same redaction rules you use for your application logs.

## How do batching, buffering, and retries behave?

The plugin buffers spans in memory and flushes them in batches to avoid hammering CLS with a request per span. Four knobs control that behavior:

| Option | Default | Purpose |
| --- | --- | --- |
| `batchMaxSize` | 32 | Maximum spans per upload |
| `maxQueueSize` | 2048 | In-memory queue cap; oldest span is dropped when full |
| `flushIntervalMs` | 5000 | How often buffered spans are flushed |
| `retryTimes` | 3 | Retries per failed upload |

The most important implication is the drop policy. When the in-memory queue hits `maxQueueSize`, the plugin drops the oldest span rather than blocking the agent. That is a deliberate availability choice: observability must never stall the harness. Under normal load 2048 buffered spans is generous, but a burst of heavy tool calls can fill it, so treat dropped spans as a signal that batching needs tuning or the flush interval needs lowering.

## What are the compatibility requirements?

The plugin targets a specific window of DeepSeek Harness releases and a recent Node.js runtime:

| Component | Requirement |
| --- | --- |
| DeepSeek Harness | `>=0.1.0-rc.6` and `<0.2.0` |
| Node.js | `>=18.0.0` |
| Language | TypeScript |
| License | Apache-2.0 |
| Package manager note | pnpm v9+ needs `approve-builds` |

The version pin matters. Because the plugin hooks DSH's internal lifecycle events, it depends on the event shapes of a particular harness generation. If you are on a Harness older than `0.1.0-rc.6` or have already moved to `0.2.0` and beyond, verify plugin compatibility before assuming your traces will appear.

## How does the Tencent plugin compare to other DSH observability options?

DeepSeek Harness already has an observability ecosystem, and the Tencent plugin is not the only choice. The realistic decision is less "which tracer" and more "which architecture":

| Approach | Transport | Collector needed? | Best for |
| --- | --- | --- | --- |
| TencentCloud AgentObs DSH | Protobuf → CLS | No | Teams already on Tencent Cloud wanting CLS-native dashboards |
| dsh-plugin-langfuse | OpenTelemetry → Langfuse | Langfuse self-host or cloud | Teams standardizing on Langfuse as the LLM observability platform |
| dsh-Agentlink | OTel bridge to Codex | OTLP endpoint | Cross-framework observability bridging |
| dsh-plugin-opentelemetry-tracing | OTel → generic OTLP | OTLP backend (e.g., SigNoz, Jaeger) | Vendor-neutral, self-hosted stacks |

The structural difference is collector versus no collector. `dsh-plugin-langfuse` and the generic OpenTelemetry plugin both lean on OTLP and expect an endpoint you run or subscribe to. Langfuse, the incumbent open-source LLM observability platform, also auto-traces OpenAI-compatible DeepSeek API calls through `langfuse.openai`, but it still requires running Langfuse as a backend. The Tencent plugin is the first DSH plugin that targets a specific cloud vendor's native log service, so it carries no collector and no extra backend — you only need the CLS topic you already pay for.

## Who should use it, and who should skip it?

This plugin is a strong fit for teams that are already invested in Tencent Cloud. If your infrastructure, log pipeline, and alerting all live in CLS, pushing GenAI traces into the same platform gives you unified dashboards, cost correlation, and retention policy management without introducing a second observability silo. The zero-collector setup is genuinely attractive for a small agent fleet where running an OTLP stack is disproportionate overhead.

It is a less obvious fit when you are not on Tencent Cloud. The plugin locks your trace data to a single vendor's log service, and if your organization standardizes on OpenTelemetry or a self-hosted stack, `dsh-plugin-langfuse` or the generic OTel plugin keeps you portable. If your DeepSeek Harness version has drifted outside the supported window, portability also wins. In short: Tencent Cloud users get the cleanest setup; everyone else should weigh vendor lock-in against the convenience.

## Hands-on: from install to your first CLS trace

A minimal end-to-end run looks like this. First, add the plugin to the profile you run:

```bash
dsh plugin --profile harness add tencentcloud-agentobs-sdk-dsh
pnpm approve-builds   # required on pnpm v9+
```

Second, set the CLS credentials. With environment variables:

```bash
export CLS_ENDPOINT="ap-guangzhou.cls.tencentcs.com"
export CLS_TOPIC_ID="your-topic-id"
export CLS_SECRET_ID="your-secret-id"
export CLS_SECRET_KEY="your-secret-key"
export CLS_SERVICE_NAME="dsh-prod"
```

Third, restart DeepSeek Harness so the observer attaches. Fourth, run a session that invokes the agent and at least one tool. Within the flush interval, spans will appear in your CLS topic, nested as entry → agent → step → chat → tool. From there, build a dashboard for token usage and per-tool latency, and add an alert on ERROR-status spans — you now have deepseek harness observability without a single extra service to run.

## What pitfalls should I watch for?

The practical gotchas cluster around configuration, privacy, and environment:

- **Content leakage.** Capture is on by default; disable it or set `contentMaxChars` before tracing anything sensitive.
- **pnpm build scripts.** On pnpm v9+, forgetting `pnpm approve-builds` breaks the Protobuf layer silently at build time.
- **Restart required.** Adding the plugin does not attach it; you must restart DeepSeek Harness.
- **Queue overflow drops.** At `maxQueueSize` the oldest span is dropped to keep the harness responsive — not a sign of a network failure.
- **Version drift.** Outside `>=0.1.0-rc.6 <0.2.0` the lifecycle hooks may not fire, so traces can silently not appear.
- **Secrets in config.** Prefer a secret manager for `CLS_SECRET_ID` / `CLS_SECRET_KEY` over committing them to `cordis.patch.yml`.

## FAQ

### What does deepseek harness observability mean in practice?

It means capturing the full lifecycle of a DeepSeek Harness run — session, agent invocation, each ReAct step, LLM calls, and tool executions — as structured trace spans so you can inspect latency, token usage, and errors per agent turn.

### Does the TencentCloud AgentObs SDK require an OTLP collector?

No. It uploads GenAI trace spans directly to Tencent Cloud Log Service via Protobuf using `tencentcloud-cls-sdk-js`. There is no OTLP collector, sidecar, or extra backend to deploy.

### What span hierarchy does the plugin produce for a single DSH turn?

Each turn produces an ENTRY span containing an AGENT span, which contains STEP spans per ReAct round. Each STEP in turn has CHAT (model) and TOOL (tool execution) children, following Tencent Cloud's 5-layer entry → agent → step → chat → tool model.

### Is prompt and tool content captured by default?

Yes, content capture is enabled by default, attaching prompts, responses, and tool arguments to spans. Disable it with `captureContent: false` or the `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false` environment variable.

### Which DeepSeek Harness versions does the plugin support?

It supports DeepSeek Harness `>=0.1.0-rc.6` and `<0.2.0`, with Node.js `>=18.0.0`. It is Apache-2.0 licensed and written in TypeScript.
