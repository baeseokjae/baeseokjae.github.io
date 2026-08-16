---
title: "Langfuse for DeepSeek Harness: OpenTelemetry-Based Agent Observability"
date: 2026-08-16T16:01:16+00:00
tags: ["Langfuse", "DeepSeek", "OpenTelemetry", "LLM Observability", "Agent Tracing"]
description: "Learn how to add OpenTelemetry-based observability to a DeepSeek harness with Langfuse, covering OTLP export, the OpenAI SDK integration, and self-hosting."
draft: false
cover:
    image: "/images/langfuse-for-deepseek-harness-opentelemetry-based-agent-observability.png"
    alt: "Langfuse for DeepSeek Harness: OpenTelemetry-Based Agent Observability"
    relative: false
schema: "schema-langfuse-for-deepseek-harness-opentelemetry-based-agent-observability"
---

DeepSeek harnesses — the scripts, agents, and pipelines that call DeepSeek models — become production systems the moment they leave your laptop, and production systems need observability. The fastest way to get it is to instrument your harness with OpenTelemetry and export the traces to Langfuse, an open-source AI engineering platform that turns raw OTLP spans into searchable, debuggable agent traces. This guide walks you through the exact setup, from the OTLP endpoint and authentication to the OpenAI SDK integration and self-hosting, so you can trace every DeepSeek call end to end.

## Why DeepSeek Harnesses Need Observability

A DeepSeek harness is rarely a single API call. In practice it is a chain: a prompt template, a retrieval step, a model call, a tool invocation, a second model call to parse the result, and a final formatting pass. When that chain returns a wrong answer, you need to know which step failed and why. Without tracing, you are debugging blind — guessing whether the problem was a bad prompt, a malformed tool response, or a model that simply drifted.

Observability answers three questions that every harness operator asks daily: What did the model actually receive as input? What did it return? And how long did each step take, and at what cost? Langfuse captures all of this as structured traces, so a single failed run becomes a clickable timeline instead of a wall of log lines. For teams running DeepSeek in production, this is the difference between a five-minute fix and a five-hour investigation.

The stakes are measurable. Langfuse is a YC W23-backed open-source project with roughly 33,186 GitHub stars and about 3,574 forks, and it has become the de facto trace backend for LLM applications precisely because it makes this debugging workflow concrete. When you instrument a DeepSeek harness, you are not adding a nice-to-have — you are adding the tool that tells you whether your agent is actually working.

## What Is OpenTelemetry and How It Fits LLM Tracing

OpenTelemetry (OTel) is a CNCF project that provides a standard, vendor-neutral way to collect distributed traces, metrics, and logs from applications. Instead of baking a proprietary SDK into your code, you emit spans and traces using a common specification, then export them to any backend that speaks the OpenTelemetry Protocol (OTLP). This is the key architectural decision: your instrumentation is portable, and your trace backend is swappable.

For LLM workloads, OTel defines semantic conventions for spans that represent model calls, retrievals, and tool executions. A single agent run becomes a trace — a tree of spans — where the root span is the overall request and child spans represent each model call, embedding, or tool use. Each span carries attributes like the model name, input tokens, output tokens, latency, and cost, which is exactly the data you need to monitor a DeepSeek harness.

The practical benefit is that you can instrument once with OTel and export to Langfuse, Grafana, Jaeger, or any other OTLP-compatible backend. If you later decide Langfuse is not the right fit, your instrumentation does not change. This vendor neutrality is the strongest argument for the OTel route over a proprietary SDK, and it is why Langfuse explicitly supports receiving OTLP traces on its `/api/public/otel` endpoint.

## Langfuse as the OTel Trace Backend

Langfuse receives OpenTelemetry traces on the `/api/public/otel` endpoint, which is the OTLP ingestion path. You point your exporter at this endpoint, authenticate with your Langfuse keys, and spans start flowing. Langfuse offers cloud regions in the EU, US, and Japan, plus a HIPAA-compliant option, so you can choose where your DeepSeek trace data lives.

The endpoint and authentication details are straightforward:

- **OTLP endpoint:** For Langfuse Cloud, use the region-specific URL (for example, `https://cloud.langfuse.com/api/public/otel`). For self-hosted Langfuse version 3.22.0 or later, use `http://localhost:3000/api/public/otel`.
- **Authentication:** Use Basic Auth with a base64-encoded `pk-lf-...:sk-lf-...` pair. The public key identifies your project; the secret key authorizes writes.
- **Ingestion version:** For Langfuse v4, include the `x-langfuse-ingestion-version: 4` header to enable real-time ingestion.

You set the exporter endpoint and credentials as environment variables, most commonly `OTEL_EXPORTER_OTLP_ENDPOINT`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY`. Once configured, any OTel-compatible exporter in your DeepSeek harness can ship traces to Langfuse without custom code.

## Option A — Instrument a DeepSeek Harness with the Langfuse OpenAI SDK

DeepSeek's API is OpenAI-compatible, which means you can use the OpenAI SDK to call DeepSeek models. This is the single most important fact for observability, because it lets you reuse the entire OpenAI SDK integration ecosystem — including Langfuse's drop-in tracing wrapper.

The Langfuse Python SDK provides a `Langfuse` client that wraps the OpenAI SDK. Instead of calling `OpenAI()` directly, you create a `Langfuse` client and use its `.openai` attribute to get a traced client. Every request you make through that client is automatically wrapped in a span, capturing the model, prompt, completion, token counts, latency, and cost.

Here is the minimal setup for a DeepSeek harness:

```python
import os
from langfuse.openai import OpenAI

# Set these in your environment
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_BASE_URL"] = "https://cloud.langfuse.com"

client = OpenAI(
    base_url="https://api.deepseek.com",  # DeepSeek's OpenAI-compatible endpoint
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Explain observability in one sentence."}],
)
print(response.choices[0].message.content)
```

Because the client is the Langfuse-wrapped OpenAI client, that single `create` call produces a full trace in Langfuse with zero manual span management. For a harness that makes many calls — a retrieval step, a reasoning step, a tool call — each one becomes a child span under the parent trace, giving you a complete timeline of the agent run.

Langfuse also integrates natively with LangChain, LlamaIndex, and LiteLLM, so if your DeepSeek harness is built on one of those frameworks, you get tracing with a one-line callback or wrapper rather than manual instrumentation. This is the lowest-friction path and the right choice for most teams.

## Option B — Raw OpenTelemetry Export to Langfuse for Custom Harnesses

If your DeepSeek harness is written in a language without a Langfuse SDK, or you want to keep your instrumentation fully vendor-neutral, you can use the native OpenTelemetry API and export spans directly to Langfuse. This is the "raw OTel" path, and it is the right choice when you need maximum control or are standardizing on OTel across multiple backends.

The pattern is to create a tracer, start spans around each logical step, and let the OTLP exporter ship them to Langfuse. Here is a Python example using the `opentelemetry-sdk` and `opentelemetry-exporter-otlp-proto-http` packages:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint="http://localhost:3000/api/public/otel",
            headers={"Authorization": "Basic <base64(pk:sk)>"},
        )
    )
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("deepseek-harness")

with tracer.start_as_current_span("agent.run") as root:
    with tracer.start_as_current_span("deepseek.call") as span:
        span.set_attribute("gen_ai.request.model", "deepseek-chat")
        # ... call DeepSeek here ...
        span.set_attribute("gen_ai.usage.input_tokens", 120)
        span.set_attribute("gen_ai.usage.output_tokens", 45)
```

The trade-off is clear: raw OTel gives you portability and control, but you must manually set the semantic-convention attributes that Langfuse uses to render cost, tokens, and model names. The Langfuse SDK does this for you automatically. For a custom harness, weigh whether the extra control is worth the manual attribute management.

## Self-Hosting Langfuse for Private DeepSeek Trace Data

If your DeepSeek harness processes sensitive data, you may not want traces leaving your infrastructure. Langfuse is fully self-hostable, and self-hosting gives you complete control over where trace data lives. The self-hosted instance exposes the same OTLP endpoint on `localhost:3000` (for version 3.22.0 and later), so the exporter configuration is identical to the cloud path — you just change the endpoint.

Self-hosting is a good fit when you need data residency guarantees, want to avoid per-token or per-trace cloud costs at high volume, or need to keep DeepSeek prompts and completions inside your own network. The setup is a standard Docker deployment, and because Langfuse is open source, you can inspect and extend it.

The main cost is operational: you are now responsible for running, upgrading, and backing up the Langfuse instance. For a small team this is a reasonable trade for data privacy; for a large one, the cloud regions (EU, US, Japan, HIPAA) may already satisfy your residency requirements without the operational burden.

## Enabling Real-Time Ingestion in Langfuse v4

One of the biggest changes in Langfuse v4 is real-time ingestion. Langfuse claims up to 165x faster real-time ingestion compared to prior versions, which matters for live agent debugging. In older versions, traces could be batched and delayed; in v4, you can see spans appear as they happen, which is essential when you are watching a DeepSeek agent run in production and need to catch a failure the moment it occurs.

To opt into real-time ingestion, include the `x-langfuse-ingestion-version: 4` header on your OTLP export requests. If you are using the Langfuse SDK, this is handled for you. If you are using raw OTel, add the header to your exporter's headers dictionary alongside the Basic Auth credentials.

Real-time ingestion changes your debugging workflow. Instead of running a batch, waiting, and then inspecting traces, you can watch a live agent run unfold in the Langfuse UI, spot a bad tool call mid-run, and intervene. For a DeepSeek harness that makes many sequential calls, this live view is the difference between catching a problem in seconds and discovering it after the fact.

## Comparing Langfuse SDK vs Raw OTel for Your Harness

The choice between the Langfuse SDK and raw OpenTelemetry is the central decision in this guide. Both end with traces in Langfuse, but they differ in effort, portability, and control.

| Consideration | Langfuse SDK | Raw OpenTelemetry |
| --- | --- | --- |
| Setup effort | Minimal — wrap the OpenAI client | Moderate — configure tracer and exporter |
| Span attributes | Automatic (tokens, cost, model) | Manual (you set semantic conventions) |
| Vendor neutrality | Tied to Langfuse | Fully portable across OTel backends |
| Language support | Python, JS, plus framework integrations | Any language with an OTel SDK |
| Real-time ingestion | Automatic in v4 | Requires the `x-langfuse-ingestion-version: 4` header |
| Best for | Most teams, especially OpenAI-SDK-based harnesses | Custom harnesses, multi-backend standardization |

For most DeepSeek harnesses, the Langfuse SDK is the right call. It is less code, produces richer traces automatically, and handles real-time ingestion for you. Choose raw OTel when you need to export to multiple backends, are working in a language without a Langfuse SDK, or want to keep your instrumentation independent of any single vendor.

## Common Pitfalls and Debugging Tips

Even with a clean setup, a few issues trip up most teams. Here are the ones to watch for.

**Wrong OTLP endpoint.** The most common mistake is pointing the exporter at the Langfuse base URL instead of the `/api/public/otel` path. The OTLP endpoint must include that suffix. If you see no traces, check that your exporter is hitting `.../api/public/otel`, not `.../api`.

**Authentication failures.** Langfuse expects Basic Auth with a base64-encoded `pk-lf-...:sk-lf-...` pair. If you pass the keys as separate headers or forget the base64 encoding, ingestion fails silently. Verify the header format before debugging anything else.

**Missing ingestion header.** On Langfuse v4, omitting `x-langfuse-ingestion-version: 4` can cause traces to be delayed or dropped. Add the header explicitly when using raw OTel.

**DeepSeek base URL confusion.** Remember that DeepSeek is OpenAI-compatible but has its own base URL (`https://api.deepseek.com`). If you point the OpenAI SDK at the default OpenAI endpoint, your DeepSeek calls fail. Set `base_url` explicitly.

**No spans for framework calls.** If you are using LangChain or LlamaIndex and see no traces, you likely forgot to register the Langfuse callback or handler. The SDK integration is not automatic — you must wire it in.

**Token and cost attributes missing.** With raw OTel, Langfuse cannot compute cost unless you set the `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens` attributes. If your traces render without cost, this is the cause.

## Conclusion and Next Steps

Adding OpenTelemetry-based observability to a DeepSeek harness with Langfuse is a high-leverage change. You get a complete, searchable timeline of every model call, tool invocation, and retrieval step, with token counts and cost — the data you need to debug failures and optimize spend. The two paths, the Langfuse OpenAI SDK and raw OTel export, both end at the same trace backend, so you can start with the SDK and migrate to raw OTel later if your needs change.

Start by instrumenting a single DeepSeek harness with the Langfuse OpenAI SDK, confirm traces appear in the Langfuse UI, then add real-time ingestion and expand to the rest of your pipeline. If data privacy is a concern, self-host Langfuse and keep every trace inside your network. The result is a DeepSeek harness you can actually see, debug, and trust in production.

## FAQ

**What is a DeepSeek harness?**
A DeepSeek harness is any script, agent, or pipeline that calls DeepSeek models — typically a chain of prompt, retrieval, model call, and tool steps. It is the code that turns the DeepSeek API into a working application.

**How do I trace DeepSeek calls with Langfuse?**
Because DeepSeek's API is OpenAI-compatible, you can use the Langfuse OpenAI SDK wrapper. Create a `Langfuse` client, use its `.openai` attribute, and set `base_url` to `https://api.deepseek.com`. Every call is traced automatically.

**Does Langfuse support OpenTelemetry?**
Yes. Langfuse receives OTLP traces on its `/api/public/otel` endpoint, so any OpenTelemetry-compatible exporter can ship spans to Langfuse. This is the vendor-neutral path for custom harnesses.

**Can I self-host Langfuse for DeepSeek trace data?**
Yes. Langfuse is open source and self-hostable. For version 3.22.0 and later, the self-hosted instance exposes the OTLP endpoint on `localhost:3000`, keeping all trace data inside your infrastructure.

**What is the `x-langfuse-ingestion-version: 4` header for?**
It opts into Langfuse v4's real-time ingestion, which Langfuse claims is up to 165x faster than prior versions. It makes traces appear live, which is essential for debugging DeepSeek agents in production.
