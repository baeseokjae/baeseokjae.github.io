---
title: "AI Agent Observability with OpenTelemetry: From Dev to Production in 2026"
date: 2026-05-19T09:04:46+00:00
tags: ["opentelemetry", "ai-agents", "observability", "llm-tracing", "production"]
description: "Complete guide to instrumenting AI agents with OpenTelemetry GenAI semantic conventions — from local Jaeger to production Grafana Cloud in 2026."
draft: false
cover:
  image: "/images/ai-agent-observability-opentelemetry-2026.png"
  alt: "AI Agent Observability with OpenTelemetry: From Dev to Production in 2026"
  relative: false
schema: "schema-ai-agent-observability-opentelemetry-2026"
---

OpenTelemetry is the standard way to add structured tracing, metrics, and logs to AI agents in 2026 — covering token usage, tool call latency, and multi-agent context propagation with a single SDK and vendor-neutral backends.

## Why Traditional Observability Fails for AI Agents

Traditional APM tools like Datadog APM or New Relic were designed for deterministic request/response cycles: a user hits an endpoint, a function runs, a database query fires, a response returns. The execution path is fixed, latency is bounded, and errors are binary. AI agents break every one of these assumptions. An agent reasoning chain is non-deterministic — the same input prompt can trigger three tool calls in one run and seven in the next. Execution duration ranges from 500ms for a fast LLM call to 3+ minutes for a multi-step agent that searches the web, queries a database, and synthesizes results. Without agent-native spans, you cannot tell which tool call caused a timeout or why a particular run cost $0.40 while a similar one cost $0.03. Traditional APM measures function latency in microseconds and ignores tokens entirely. The LLM observability platform market recognized this gap — growing to an estimated $2.69 billion in 2026 and projected to reach $9.26 billion by 2030 at a 36.2% CAGR. OpenTelemetry's GenAI Semantic Conventions fill that gap with a purpose-built span model for LLM operations, agent reasoning loops, and tool executions that traditional APM never anticipated.

### What Makes AI Agent Telemetry Different?

AI agents require three observability primitives that traditional APM lacks. First, **token-based cost attribution** — you need to know how many input and output tokens each LLM call consumed, mapped to a session, user, or feature. Second, **reasoning chain tracing** — a parent span for the agent loop with child spans for each tool call, LLM request, and decision step, linked by trace context so you can reconstruct the full execution tree. Third, **non-deterministic failure modes** — an agent might hallucinate a tool name, exceed its context window mid-run, or loop indefinitely; catching these requires span attributes that conventional HTTP APM never defines. GenAI conventions add `gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`, and `gen_ai.usage.input_tokens` to fill exactly these gaps.

### The Token Economy Problem

A single user session might trigger dozens of LLM calls across multiple agents. Without per-call token tracking, your billing dashboard shows a lump sum while your engineers have no idea which feature, agent, or user is driving costs. OpenTelemetry's `gen_ai.client.token.usage` metric and corresponding span attributes let you aggregate token spend by `gen_ai.agent.name`, session ID, or custom attribute — giving you cost observability with the same instrumentation that drives latency dashboards.

## OpenTelemetry GenAI Semantic Conventions: The 2026 Standard

OpenTelemetry GenAI Semantic Conventions are the standardized attribute names, span structure, and metric definitions that give AI telemetry a common language across every vendor and framework. In early 2026, GenAI client spans and the `gen_ai.client.token.usage` / `gen_ai.client.operation.duration` metrics exited experimental status and became stable — meaning you can rely on them in production without fear of breaking changes. Agent-specific spans (`gen_ai.agent.name`, `gen_ai.tool.name`) and framework-level instrumentation remain experimental but are production-stable at most major observability vendors. The conventions define how to capture prompt and completion content safely (in span events, not span attributes, to enable opt-in content capture without leaking PII into your metrics store). Gartner predicts that by 2028, LLM observability investments will account for 50% of GenAI deployments, up from 15% in early 2026 — and OpenTelemetry's vendor-neutral standard is what makes that investment transferable across backends.

### Core GenAI Span Attributes

The stable attributes every AI agent span should carry:

| Attribute | Type | Example | Purpose |
|---|---|---|---|
| `gen_ai.system` | string | `openai`, `anthropic` | Identifies the LLM provider |
| `gen_ai.operation.name` | string | `chat`, `execute_tool` | Type of GenAI operation |
| `gen_ai.request.model` | string | `gpt-5`, `claude-opus-4` | Requested model name |
| `gen_ai.response.model` | string | `gpt-5-2026-05` | Actual model version used |
| `gen_ai.usage.input_tokens` | int | `1248` | Prompt tokens consumed |
| `gen_ai.usage.output_tokens` | int | `342` | Completion tokens generated |
| `gen_ai.agent.name` | string | `research_agent` | Identifies the agent (experimental) |
| `gen_ai.tool.name` | string | `web_search` | Tool called by the agent (experimental) |

### Span Events vs Span Attributes for Content

The conventions deliberately separate prompt and completion content from the main span attribute set. Content goes into **span events** — specifically `gen_ai.content.prompt` and `gen_ai.content.completion` events — rather than span attributes. This design means that a) content capture is opt-in (disabled by default), b) you can strip content at the collector level without losing metrics, and c) you avoid accidentally indexing PII into your tracing backend. For GDPR compliance, this is critical: you can run full token usage and latency observability without ever storing a single user message.

## Setting Up OpenTelemetry for AI Agents in Python (Step-by-Step)

Getting OpenTelemetry running for an AI agent takes about 20 minutes from zero to local Jaeger traces. The setup uses `opentelemetry-sdk`, a GenAI instrumentation library (`openlit`, `openinference`, or `opentelemetry-instrumentation-openai` depending on your framework), and a local Jaeger instance for development. In production, you swap the exporter endpoint to Grafana Cloud, Honeycomb, or any OTLP-compatible backend — the instrumentation code stays identical. 85% of organizations with GenAI deployments planned for LLM observability as key infrastructure in 2026, and OpenTelemetry's backend-agnostic design is why they can avoid vendor lock-in at the SDK layer. The key insight is that auto-instrumentation handles the heavy lifting for LLM API calls, while manual spans wrap the agent loop itself. This two-layer approach — auto-instrumented LLM calls nested inside manually-traced agent runs — gives you complete visibility into both LLM-level metrics (tokens, latency per call) and agent-level behavior (iterations, tool success rates, end-to-end duration) without duplicating code across every model integration your agent might use. The five steps below take you from a fresh Python environment to a trace visible in Jaeger, then show the one-line change needed to point that same setup at a production backend.

### Step 1: Install Dependencies

```bash
pip install opentelemetry-sdk \
            opentelemetry-exporter-otlp \
            openlit \
            openai  # or anthropic, langchain, etc.
```

`openlit` is the simplest auto-instrumentation library for 2026 — one `openlit.init()` call instruments OpenAI, Anthropic, LangChain, and LlamaIndex clients automatically.

### Step 2: Configure the Tracer Provider

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import openlit

# Point to local Jaeger in dev, Grafana Cloud / Honeycomb in prod
otlp_endpoint = "http://localhost:4317"

provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
)
trace.set_tracer_provider(provider)

# Auto-instrument all supported LLM clients
openlit.init(
    otlp_endpoint=otlp_endpoint,
    capture_message_content=False,  # Opt-in; set True only in dev
)
```

### Step 3: Instrument Your Agent Loop

Auto-instrumentation covers LLM API calls. For the agent loop itself, add manual spans:

```python
tracer = trace.get_tracer("my_agent", "1.0.0")

def run_agent(task: str, session_id: str) -> str:
    with tracer.start_as_current_span(
        "agent.run",
        attributes={
            "gen_ai.agent.name": "research_agent",
            "session.id": session_id,
            "agent.task": task[:100],  # Truncate for index efficiency
        }
    ) as span:
        for iteration in range(MAX_ITERATIONS):
            span.set_attribute("agent.iterations", iteration + 1)
            
            # LLM call — auto-instrumented by openlit
            response = client.chat.completions.create(
                model="gpt-5",
                messages=messages
            )
            
            tool_calls = extract_tool_calls(response)
            if not tool_calls:
                break
                
            for tool_call in tool_calls:
                with tracer.start_as_current_span(
                    "agent.tool_call",
                    attributes={
                        "gen_ai.tool.name": tool_call.name,
                        "gen_ai.tool.call.id": tool_call.id,
                    }
                ) as tool_span:
                    result = execute_tool(tool_call)
                    tool_span.set_attribute("tool.success", result.ok)
        
        return extract_final_answer(response)
```

### Step 4: Run Local Jaeger for Development

```bash
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

Open `http://localhost:16686` to see traces. Each agent run appears as a root span with nested LLM call spans and tool call spans — you can drill into any span to see token counts, model versions, and timing.

### Step 5: Switch to Production Backend

Replace the OTLP endpoint with your production backend:

```python
# Grafana Cloud
otlp_endpoint = "https://otlp-gateway-prod-us-east-0.grafana.net/otlp"

# Add authentication header
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    headers={"Authorization": f"Bearer {GRAFANA_API_KEY}"}
)
```

The instrumentation code does not change — only the exporter endpoint and auth header.

## The 6 Essential Metrics Every Production AI Agent Needs

Production AI agent observability requires six distinct metrics that cover cost, reliability, performance, and capacity. These map directly to OpenTelemetry GenAI metric definitions and can be derived from spans if you do not emit them explicitly. Agent execution durations range from 500ms to 3+ minutes; without these metrics, identifying which tool call caused a timeout is nearly impossible. The six metrics form a complete diagnostic surface: token usage ties to cost, tool call success rate ties to reliability, LLM latency ties to user experience, loop iterations catch infinite loops, context window utilization prevents silent truncation, and end-to-end latency covers the full user-facing impact. Two of these — `gen_ai.client.token.usage` and `gen_ai.client.operation.duration` — are stable OTel metrics in 2026, meaning vendor-provided dashboards and alerting templates are available out of the box. The remaining four are derived from span attributes on your agent spans. Tracking all six from day one of production deployment means you have a complete baseline when something goes wrong, rather than scrambling to add instrumentation after an incident. Each metric below includes the exact OTel attribute or metric name and a concrete alert threshold that distinguishes healthy agent behavior from a problem worth waking someone up for.

### 1. Token Usage per Run

**Metric:** `gen_ai.client.token.usage` (histogram, stable in OTel 2026)

Emit this metric with `gen_ai.token.type` (`input` / `output`), `gen_ai.system`, `gen_ai.request.model`, and a custom `agent.name` attribute. This lets you build dashboards showing cost per agent, per session, and per feature. For a production agent handling 10,000 sessions/day, a 10% reduction in input tokens can cut monthly spend by thousands of dollars — but you cannot optimize what you do not measure.

### 2. Tool Call Success Rate

Track `tool.success` as a boolean span attribute on each tool call span. Aggregate to a success rate metric by `gen_ai.tool.name`. A web search tool with a 95% success rate looks fine until you check that the 5% failures all cluster around a specific query pattern — only per-tool tracing surfaces that.

### 3. LLM Latency Distribution (p50/p95/p99)

**Metric:** `gen_ai.client.operation.duration` (histogram, stable in OTel 2026)

Track latency distribution by model and operation type. p99 latency matters for user-facing agents — if your p99 is 12 seconds, some users experience 12-second waits even if your median is 800ms. Percentile tracking requires a histogram metric, not an average.

### 4. Agent Loop Iterations

Set `agent.iterations` on the root agent span at completion. A healthy agent typically resolves in 1-5 iterations. Runs exceeding 10 iterations usually indicate prompt issues or tool failures causing the agent to retry. An alert on `agent.iterations > 8` catches runaway loops before they exhaust token budgets.

### 5. Context Window Utilization

Calculate `(input_tokens / model_context_window) * 100` per LLM call. When utilization exceeds 85%, you risk silent context truncation where the model loses early conversation history. Track this as a gauge metric by model — it informs when to implement context compression strategies.

### 6. End-to-End Latency

The duration of the root `agent.run` span, not individual LLM calls. This is the user-facing latency that maps to actual experience. An agent might have fast LLM calls but slow tool executions; only end-to-end latency catches that. SLA alerts should be set on this metric.

## Distributed Tracing for Multi-Agent and Tool-Calling Workflows

Distributed tracing across agent boundaries is the hardest part of multi-agent observability — and the part where getting it wrong makes all other telemetry useless. When a coordinator agent calls a subagent via an HTTP API or a message queue, the trace context must propagate so that the subagent's spans appear as children of the coordinator's span in the same trace. Without propagation, you get disconnected traces: one for the coordinator, one for the subagent, with no way to link them. OpenTelemetry's W3C Trace Context standard (`traceparent` and `tracestate` HTTP headers) handles this automatically for HTTP-based agent communication. For async message passing, you inject the trace context into message headers and extract it on the consumer side. In a real multi-agent system — for example, a coordinator that fans out to a research subagent, a writing subagent, and a fact-checking subagent — proper context propagation means a single trace ID covers the entire execution tree. You can see in one Jaeger view that the coordinator took 45 seconds total, the research subagent took 32 of those seconds (mostly waiting on a web search tool), and the writing subagent ran in 8 seconds. Without propagation, you would have three separate 3-node traces with no causal relationship visible between them. The code examples below show propagation for both HTTP and message queue communication patterns.

### HTTP-Based Agent Communication

```python
from opentelemetry.propagate import inject, extract
from opentelemetry import trace
import httpx

tracer = trace.get_tracer("coordinator_agent")

def call_subagent(task: str, subagent_url: str) -> dict:
    with tracer.start_as_current_span("coordinator.call_subagent") as span:
        headers = {}
        inject(headers)  # Injects traceparent and tracestate headers
        
        span.set_attribute("subagent.url", subagent_url)
        span.set_attribute("gen_ai.agent.name", "coordinator")
        
        response = httpx.post(
            subagent_url,
            json={"task": task},
            headers=headers
        )
        return response.json()
```

On the subagent side:

```python
from opentelemetry.propagate import extract
from opentelemetry import trace
from flask import Flask, request

app = Flask(__name__)
tracer = trace.get_tracer("subagent")

@app.post("/run")
def run_subagent():
    # Extract trace context from incoming request headers
    ctx = extract(request.headers)
    
    with tracer.start_as_current_span(
        "subagent.run",
        context=ctx,  # Links this span to coordinator's trace
        attributes={"gen_ai.agent.name": "research_subagent"}
    ) as span:
        result = execute_research_task(request.json["task"])
        return {"result": result}
```

The result: coordinator call + subagent execution + all LLM calls inside both appear in a single trace in Jaeger or Grafana.

### Message Queue Propagation (Kafka/Redis Streams)

```python
# Producer (coordinator)
from opentelemetry.propagate import inject

def enqueue_task(task: dict, producer):
    headers = {}
    inject(headers)
    producer.send("agent_tasks", value=task, headers=list(headers.items()))

# Consumer (subagent worker)
from opentelemetry.propagate import extract

def process_task(message):
    headers = dict(message.headers)
    ctx = extract(headers)
    with tracer.start_as_current_span("subagent.process", context=ctx):
        execute_task(message.value)
```

### Baggage for Session-Level Context

Use OpenTelemetry Baggage to propagate session IDs, user IDs, and feature flags across agent boundaries without adding them to every span manually:

```python
from opentelemetry.baggage import set_baggage, get_baggage
from opentelemetry import context

# Set at entry point
ctx = set_baggage("session.id", session_id)
ctx = set_baggage("user.tier", "premium", context=ctx)

# Automatically available in all descendant spans
# Retrieve in subagent
session_id = get_baggage("session.id")
```

## Choosing Your Observability Backend (Self-Hosted vs Managed)

The choice between self-hosted and managed observability backends for AI agents comes down to three factors: data residency requirements, engineering capacity for ops, and cost at scale. OTel in production nearly doubled year-over-year from 6% to 11% among enterprises in 2026, with 89% rating vendor compliance with GenAI conventions as critical. The good news: any backend that accepts OTLP works — you are not locked to any vendor at the SDK layer. The trade-off is operational overhead vs monthly SaaS spend. A managed backend like Grafana Cloud or Honeycomb costs roughly $20–$200/month for a medium-traffic AI agent deployment and requires zero ops work. A self-hosted Jaeger + VictoriaMetrics stack requires maintaining the infrastructure but gives you full control over data retention, no per-event pricing, and no data leaving your environment — critical for healthcare or financial services applications subject to HIPAA or SOC 2 requirements. Langfuse occupies a middle ground: open source and self-hostable, but with a managed cloud tier if you want LLM-native features without the ops overhead. The comparison table below shows GenAI-specific feature support across the major options so you can match backend capabilities to your observability requirements.

### Comparison Table

| Backend | Type | GenAI Support | Cost Model | Best For |
|---|---|---|---|---|
| **Grafana Cloud** | Managed | Native GenAI dashboards | Free tier + usage | Most teams starting out |
| **Honeycomb** | Managed | Full attribute querying | Per event | High-cardinality debugging |
| **Langfuse** | Managed + OSS | LLM-native, 21K+ GitHub stars | Free OSS / managed | LLM-first observability |
| **Jaeger** | Self-hosted | Standard OTel traces | Infrastructure cost | Dev/test, cost-sensitive |
| **Grafana + Tempo** | Self-hosted | Custom dashboards | Infrastructure cost | Full control, data residency |
| **VictoriaMetrics** | Self-hosted | Prometheus-compatible metrics | Infrastructure cost | Metrics-heavy workloads |

### Managed: Grafana Cloud

Grafana Cloud accepts OTLP traces, metrics, and logs from the same endpoint. Their AI/LLM dashboard templates include token usage panels, latency percentile histograms, and cost aggregation by agent. The free tier covers 50GB of logs and 10K traces/month — enough for a medium-traffic development environment.

### Self-Hosted: Langfuse

Langfuse is the most popular open-source LLM observability platform (21,000+ GitHub stars by early 2026). It provides a purpose-built UI for LLM traces with session views, prompt management, and evaluation tooling that generic APM tools lack. Deploy with Docker Compose for single-node or Kubernetes for production:

```bash
git clone https://github.com/langfuse/langfuse
cd langfuse
docker compose up -d
```

Then point openlit at the Langfuse OTLP endpoint. Langfuse also maintains a Python SDK for direct integration if you prefer to skip the OTel SDK layer.

### Self-Hosted: Jaeger + OpenTelemetry Collector

The minimal self-hosted stack for production:

```yaml
# docker-compose.yml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"  # OTLP gRPC
      - "4318:4318"  # OTLP HTTP
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
```

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"
      http:
        endpoint: "0.0.0.0:4318"

processors:
  # Redact prompt content for GDPR compliance
  redaction:
    allow_all_keys: true
    blocked_values:
      - "gen_ai.content.prompt"
      - "gen_ai.content.completion"

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [redaction]
      exporters: [jaeger]
```

## Production Deployment Checklist: Dev to Prod in One Guide

Moving AI agent observability from a local Jaeger instance to production requires addressing four concerns that do not exist in development: authentication, cardinality, sampling, and alerting. Each of these can either degrade your observability posture (too aggressive sampling) or destabilize your backend (unbounded cardinality). The following checklist is what a production AI agent deployment looks like when observability is treated as a first-class requirement from day one — not bolted on after the first incident. Authentication is the most urgent: an unauthenticated OTLP exporter will fail silently against a production backend, leaving you with zero traces and no error in application logs. Cardinality problems typically appear 2–4 weeks after launch when someone adds a user-ID-based span attribute and your metrics cardinality explodes. Sampling decisions made before you understand your traffic patterns are almost always wrong — start with 100% traces in production for the first week, then tune down using tail-based sampling once you understand what "normal" looks like. The alerting section below maps each of the six essential metrics from the previous section to a specific alert condition, giving you a working alert configuration you can paste directly into Grafana or your alerting tool of choice.

### Authentication and Transport Security

- [ ] Replace unauthenticated OTLP exporter with authenticated connection using API keys or mTLS
- [ ] Rotate API keys for observability backends on the same schedule as other service credentials
- [ ] Ensure OTLP exporter uses TLS (`InsecureSkipVerify: false` in production)
- [ ] Validate that `capture_message_content=False` is set in production (opt-in content capture only in dev/staging)

### Cardinality Management

- [ ] Never use unbounded values (user IDs, session IDs, full URLs) as span attribute keys — only as values
- [ ] Cap `agent.task` attribute to 100 characters to avoid high-cardinality string fields
- [ ] Use `gen_ai.request.model` (the standardized attribute) instead of a custom model attribute — this ensures consistent cardinality across frameworks
- [ ] Review tool name attributes — if tool names are dynamically generated, normalize them to a fixed set

### Sampling Strategy

For production AI agents, **tail-based sampling** is the right default: sample 100% of errored traces, 100% of traces exceeding your p95 latency threshold, and 5-10% of successful fast traces. Head-based sampling at 10% will randomly drop slow or errored traces, defeating the purpose.

```yaml
# otel-collector sampling config
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors-policy
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow-traces-policy
        type: latency
        latency: {threshold_ms: 5000}
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

### Alerting Configuration

Set up these five alerts at minimum:

| Alert | Condition | Severity |
|---|---|---|
| High agent loop iterations | `agent.iterations > 8` for >1% of runs | Warning |
| Tool call failure spike | Tool success rate drops below 90% | Critical |
| Token budget exceeded | `gen_ai.usage.input_tokens` > model limit × 0.9 | Warning |
| End-to-end latency p99 | Agent run duration p99 > 30s | Critical |
| Trace loss | No traces received from agent in 5 min | Critical |

### Instrumentation Coverage Verification

```python
# Add this to your CI pipeline to verify instrumentation is active
import opentelemetry.trace as trace_api

def test_tracer_configured():
    tracer = trace_api.get_tracer("test")
    assert not isinstance(
        tracer, trace_api.ProxyTracer
    ), "TracerProvider not configured — spans will be no-ops"
```

A no-op TracerProvider is the silent failure mode: your code runs, no errors appear, and no traces arrive. This test catches that in CI before it reaches production.

### Environment Variable Configuration

```bash
# Production environment
OTEL_SERVICE_NAME=my-production-agent
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production,service.version=1.2.3
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-otlp-endpoint:4317
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer ${OTLP_API_KEY}
OTEL_TRACES_SAMPLER=parentbased_always_on  # Let collector handle tail sampling

# Dev override
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OPENLIT_CAPTURE_MESSAGE_CONTENT=true
```

Keep all observability configuration in environment variables — never hardcode endpoints in instrumentation code.

---

## FAQ

**What is OpenTelemetry GenAI semantic conventions and why does it matter?**

OpenTelemetry GenAI semantic conventions are the standardized set of attribute names, span types, and metric definitions that give AI/LLM telemetry a consistent structure across every framework and vendor. They matter because without them, a LangChain trace uses different attribute names than an OpenAI trace, making aggregation and alerting across your stack impossible. In 2026, core client spans and token usage metrics are stable, meaning you can build production dashboards on them without breaking change risk.

**How do I instrument an OpenAI or Anthropic client without changing my application code?**

Use `openlit.init()` before your first API call. It patches the OpenAI and Anthropic client libraries automatically using monkey-patching, so every `client.chat.completions.create()` call generates a span with GenAI attributes without requiring any code changes to your existing agent logic. You only need to configure the TracerProvider once at application startup.

**What is the difference between session-level and request-level observability for AI agents?**

Request-level observability covers a single LLM call: model, tokens, latency. Session-level observability covers the entire user interaction: all agent runs, all tool calls, cost totals, and outcome. Session-level requires threading a `session.id` through every span and aggregating across multiple traces. OpenTelemetry Baggage is the standard mechanism for propagating session context across agent boundaries without adding it to every span attribute manually.

**How do I avoid storing sensitive user data (PII) in my traces?**

Set `capture_message_content=False` in openlit (which is the default). GenAI conventions separate prompt/completion content into span events rather than attributes, so stripping them at the OpenTelemetry Collector level is straightforward — add a `redaction` processor that blocks `gen_ai.content.prompt` and `gen_ai.content.completion` event attributes. This gives you full token usage and latency observability without storing any message content.

**Which observability backend should I use for AI agents in 2026?**

For most teams: Grafana Cloud for its generous free tier, native OTLP support, and pre-built LLM dashboard templates. For LLM-specific features like prompt management and evaluation: Langfuse (open source, 21K+ GitHub stars). For maximum flexibility and self-hosting: Jaeger + OpenTelemetry Collector + VictoriaMetrics. All three work with the same OTel SDK instrumentation — you switch backends by changing an endpoint URL, not rewriting instrumentation code.
