---
title: "Arize Phoenix Guide: Open-Source LLM Observability for Developers (2026)"
date: 2026-05-17T15:03:42+00:00
tags: ["arize phoenix", "llm observability", "opentelemetry", "rag evaluation", "ai monitoring"]
description: "Step-by-step guide to Arize Phoenix: install, instrument LLM apps, trace RAG pipelines, and run evals — all open-source, zero vendor lock-in."
draft: false
cover:
  image: "/images/arize-phoenix-observability-guide-2026.png"
  alt: "Arize Phoenix Guide: Open-Source LLM Observability for Developers"
  relative: false
schema: "schema-arize-phoenix-observability-guide-2026"
---

Arize Phoenix is a free, open-source LLM observability platform that gives developers full-stack visibility into LLM applications — tracing requests, evaluating outputs, and debugging RAG pipelines — without requiring a cloud subscription or vendor account. It runs locally in a Python process or scales to Docker and Kubernetes for production deployments.

## What Is Arize Phoenix and Why It Matters in 2026

Arize Phoenix is an open-source observability platform built specifically for LLM applications, agents, and retrieval-augmented generation (RAG) pipelines. Unlike generic APM tools, Phoenix understands LLM-native concepts — spans, traces, embeddings, prompts, retrieved contexts, and model outputs — and surfaces them in a UI designed for AI engineers. As of 2026, Phoenix has surpassed 9,000 GitHub stars, making it one of the most-adopted open-source observability tools in the AI ecosystem. The platform is backed by Arize AI but released under a permissive open-source license, meaning you can run it entirely on your own infrastructure with no usage caps or feature gating.

The urgency behind Phoenix adoption is clear: the LLM observability market is growing from $1.97B in 2025 to $2.69B in 2026 at a 36.3% CAGR, and Gartner predicts that by 2028, observability will be embedded in 50% of GenAI deployments — up from just 15% today. Yet 57% of organizations already running AI agents in production rate observability as the lowest-quality part of their AI stack. Phoenix exists to close that gap for teams who can't afford to ship LLM apps blind, and who want to own their trace data rather than send it to a SaaS vendor.

## What Core Features Does Phoenix Offer?

Arize Phoenix ships four interconnected capabilities that cover the full LLM development lifecycle: tracing, evaluation, dataset management, and a prompt playground. Together they form a workflow loop: trace what your app is doing, evaluate whether outputs meet quality thresholds, curate failure cases into datasets, and iterate on prompts in the playground before deploying changes. This feedback loop is the key reason teams migrate from generic logging to Phoenix — instead of reading raw JSON logs, engineers see structured span trees, latency breakdowns per retrieval step, and LLM judge scores alongside the actual model outputs.

**Tracing** captures every span in an LLM workflow as an OpenTelemetry trace. A single user request to a RAG pipeline generates spans for the embedding call, vector DB retrieval, context concatenation, and final LLM generation — each with token counts, latency, and input/output payloads.

**Evaluation** runs 50+ research-backed metrics including hallucination detection, relevance, Q&A correctness, toxicity, and faithfulness. These can run in the Phoenix UI as one-off evals or in CI via the `phoenix.evals` Python API.

**Dataset management** lets you export traces — especially failure cases — into labeled datasets for fine-tuning or regression testing.

**Prompt playground** connects to your LLM provider APIs and lets you replay any captured trace against modified prompts to A/B test prompt changes against real historical inputs.

## How Do You Install Phoenix in 5 Minutes?

Phoenix installs via pip and launches as a local web server that requires no external dependencies for basic usage. The minimum viable setup takes under five minutes and works in any Python 3.9+ environment, including notebooks, Docker containers, and CI runners.

```bash
pip install arize-phoenix arize-phoenix-otel openinference-instrumentation-openai
```

Then start the Phoenix server and point your app at it:

```python
import phoenix as px

# Start Phoenix server (opens UI at http://localhost:6006)
session = px.launch_app()

# Configure OpenTelemetry to send traces to Phoenix
from phoenix.otel import register
tracer_provider = register(
    project_name="my-llm-app",
    endpoint="http://localhost:6006/v1/traces",
)
```

For Docker, a single command pulls and starts the full server:

```bash
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
```

Port `6006` serves the web UI. Port `4317` is the OpenTelemetry OTLP gRPC ingest endpoint. You can persist traces across restarts by mounting a volume to `/mnt/data`.

### Notebook Usage

In Jupyter or Colab environments, `px.launch_app()` renders an embedded iframe directly in the notebook cell output. No separate terminal or process management required — Phoenix starts as a background thread within the kernel, making it ideal for exploratory data analysis on LLM outputs.

## How Does OpenTelemetry Auto-Instrumentation Work with Phoenix?

Phoenix uses OpenTelemetry (OTel) as its trace collection standard, which means it benefits from a growing ecosystem of vendor-neutral instrumentation libraries. Auto-instrumentation patches popular LLM SDKs at import time — you add two lines of code and Phoenix captures every API call automatically, with no manual span creation required.

OpenTelemetry instrumentation in Phoenix works through the `openinference` family of packages. These are OTel-compatible semantic conventions for LLM-specific data: input messages, output messages, token usage, model name, embedding vectors, retrieved documents, and tool calls. When you call `OpenAIInstrumentor().instrument()`, the instrumentor monkey-patches the OpenAI Python client so every `client.chat.completions.create()` call emits a span with the full request/response payload automatically attached.

```python
from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Now every OpenAI call is automatically traced
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain observability in one sentence."}]
)
# Trace appears in Phoenix UI automatically
```

Supported auto-instrumentation packages as of 2026:

| Package | Instruments |
|---|---|
| `openinference-instrumentation-openai` | OpenAI Chat, Embeddings, Responses API |
| `openinference-instrumentation-anthropic` | Claude Messages API |
| `openinference-instrumentation-langchain` | LangChain chains, agents, tools |
| `openinference-instrumentation-llama-index` | LlamaIndex query engines, retrievers |
| `openinference-instrumentation-crewai` | CrewAI agent crews and tasks |
| `openinference-instrumentation-litellm` | LiteLLM proxy (any provider) |

### Custom Spans

For business logic that sits between LLM calls — pre-processing, validation, post-processing — you can add manual spans using the standard OTel tracer API:

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("validate-user-query") as span:
    span.set_attribute("query.length", len(user_query))
    cleaned = preprocess(user_query)
```

These custom spans appear nested within the auto-instrumented LLM spans in the Phoenix UI, giving full end-to-end visibility including your non-LLM application code.

## How Do You Trace RAG Pipelines with LlamaIndex and LangChain?

RAG pipeline tracing is Phoenix's strongest differentiator versus general-purpose observability tools. A RAG pipeline involves at least four distinct operations — query embedding, vector retrieval, context stuffing, and generation — and failures at any step produce subtly wrong outputs that are invisible without span-level visibility. Phoenix captures each step as a separate span and links them into a single trace tree, making it immediately obvious whether a bad answer came from poor retrieval or poor generation. In a typical LlamaIndex or LangChain RAG setup, a user question that returns a hallucinated answer could have failed at any of three points: the wrong documents were retrieved (retrieval failure), the correct documents were retrieved but the LLM ignored them (faithfulness failure), or the question was ambiguous and the embedding model found semantically unrelated chunks (embedding failure). Without Phoenix traces, distinguishing these failure modes requires manual logging and extensive print-statement debugging. With Phoenix, you see each span's latency, input, and output in a hierarchical tree within seconds of the query completing.

### LlamaIndex RAG Tracing

```python
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load and index documents
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# This query generates a full trace: embed → retrieve → generate
response = query_engine.query("What are the main risks of LLM hallucination?")
```

In Phoenix, this single query appears as a trace with child spans for:
- `embedding` — the query vector computation (model, latency, token count)
- `retrieval` — the top-k documents returned (document IDs, similarity scores)
- `llm` — the generation call (prompt, completion, token usage, cost)

### LangChain RAG Tracing

```python
from openinference.instrumentation.langchain import LangChainInstrumentor

LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(documents, embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o"),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
)

result = qa_chain.invoke({"query": "What is LLM observability?"})
```

Phoenix captures the full LangChain chain execution including each tool call, retriever invocation, and LLM generation as nested spans.

## How Do You Run LLM Evaluations in Phoenix?

Phoenix evaluations use LLM-as-a-judge to score traces against quality metrics — automatically and at scale. The `phoenix.evals` module provides pre-built eval templates backed by published research, so you don't need to write your own judge prompts for common tasks like hallucination detection, relevance scoring, or Q&A correctness.

Running evals takes three steps: export traces from Phoenix, run the eval function, and ship scores back to Phoenix for visualization alongside the original traces.

```python
import phoenix as px
from phoenix.evals import (
    HallucinationEvaluator,
    QAEvaluator,
    RelevanceEvaluator,
    run_evals,
)
from phoenix.evals import OpenAIModel

# Connect to running Phoenix instance
client = px.Client()

# Export traces from a project
traces_df = client.get_spans_dataframe(project_name="my-rag-app")

# Initialize evaluators
eval_model = OpenAIModel(model="gpt-4o")
evaluators = [
    HallucinationEvaluator(eval_model),
    QAEvaluator(eval_model),
    RelevanceEvaluator(eval_model),
]

# Run evals (parallelized automatically)
eval_results = run_evals(
    dataframe=traces_df,
    evaluators=evaluators,
    provide_explanation=True,
)

# Ship scores back to Phoenix
px.log_evaluations(*eval_results, project_name="my-rag-app")
```

After running, each trace in the Phoenix UI shows inline eval scores: `hallucination: 0.12`, `relevance: 0.94`, `qa_correctness: 1.0`. You can filter and sort by any eval metric to find the worst-performing traces for debugging.

### Available Evaluation Metrics

Phoenix ships 50+ evaluation metrics across five categories:

| Category | Metrics |
|---|---|
| **Retrieval quality** | Relevance, NDCG, Precision@k, Recall@k |
| **Generation quality** | Hallucination, Faithfulness, Q&A Correctness |
| **Safety** | Toxicity, PII detection, Prompt injection |
| **Code** | Code correctness, Execution success rate |
| **Custom** | Template-based LLM judge for any criteria |

## How Do You Self-Host Phoenix with Docker and Kubernetes?

Self-hosting Phoenix gives teams complete data sovereignty — traces never leave your infrastructure, which matters for regulated industries or any team with sensitive data flowing through their LLM apps. Phoenix supports three self-hosting paths: Docker Compose for small teams, standalone Docker for development, and Kubernetes Helm chart for production-scale deployments.

The Docker Compose setup is the recommended starting point for teams moving from local development to a shared instance:

```yaml
# docker-compose.yml
services:
  phoenix:
    image: arizephoenix/phoenix:latest
    ports:
      - "6006:6006"   # Web UI
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
    volumes:
      - phoenix-data:/mnt/data
    environment:
      - PHOENIX_WORKING_DIR=/mnt/data
      - PHOENIX_SECRET=your-secret-key
      
volumes:
  phoenix-data:
```

```bash
docker compose up -d
```

For Kubernetes, Arize provides an official Helm chart:

```bash
helm repo add arize-phoenix https://arize-ai.github.io/phoenix
helm install phoenix arize-phoenix/phoenix \
  --set persistence.enabled=true \
  --set persistence.size=50Gi \
  --set ingress.enabled=true \
  --set ingress.host=phoenix.yourdomain.com
```

### Environment Variables for Production

| Variable | Purpose |
|---|---|
| `PHOENIX_SECRET` | Enables authentication (required for production) |
| `PHOENIX_WORKING_DIR` | Persistent storage path for SQLite database |
| `PHOENIX_ENABLE_AUTH` | Toggle basic auth (default: disabled) |
| `PHOENIX_SMTP_*` | Email configuration for alerts |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Override for custom OTLP collectors |

Phoenix stores traces in SQLite by default, which handles millions of spans without external database dependencies. For high-throughput production workloads (10M+ spans/day), you can configure PostgreSQL as the backend database.

## Arize Phoenix vs Langfuse vs LangSmith: Which Should You Choose?

Choosing between Phoenix, Langfuse, and LangSmith depends primarily on your stack, data sovereignty requirements, and evaluation depth needs. All three are viable for 2026 production deployments — the differences are in philosophy and depth rather than basic feature gaps.

Arize Phoenix wins when you need the deepest RAG evaluation capabilities, are running a mixed ML+LLM stack (since Phoenix integrates with traditional Arize model monitoring), or want 50+ pre-built eval metrics without writing judge prompts from scratch. Its OpenTelemetry-first design also makes it future-proof — your traces are portable to any OTel-compatible backend.

Langfuse wins for teams with strict data sovereignty requirements who want the simplest self-hosted setup under MIT license. Its pricing model is the most predictable at scale, and its API-first design integrates cleanly into non-Python stacks.

LangSmith wins exclusively for teams deeply invested in the LangChain/LangGraph ecosystem. Its tight integration with LangGraph agent debugging is unmatched, but it's a proprietary platform with limited self-hosting options and pricing that scales poorly past moderate usage.

| Feature | Arize Phoenix | Langfuse | LangSmith |
|---|---|---|---|
| License | Apache 2.0 | MIT | Proprietary |
| Self-hostable | Yes | Yes | Limited |
| Built-in eval metrics | 50+ | Custom only | ~10 built-in |
| RAG evaluation depth | Best-in-class | Basic | Good |
| OpenTelemetry native | Yes | Yes | No |
| LangChain integration | Good | Good | Native |
| LlamaIndex integration | Native | Good | Basic |
| Agent tracing | Yes | Yes | Best (LangGraph) |
| Playground | Yes | Yes | Yes |
| ML model monitoring | Via Arize AX | No | No |
| GitHub stars (2026) | 9,000+ | 8,000+ | 6,000+ |

### When to Choose Each

**Choose Phoenix if:**
- Your app uses LlamaIndex or a custom RAG pipeline
- You need hallucination/faithfulness eval out of the box
- You run both traditional ML models and LLMs and want unified monitoring
- You may scale to Arize AX's enterprise features later

**Choose Langfuse if:**
- Data sovereignty is a hard requirement and you need the simplest self-hosted setup
- Your team uses multiple languages (Ruby, Go, Java) — Langfuse has broader SDK coverage
- You want predictable open-source pricing with no enterprise upsell pressure

**Choose LangSmith if:**
- Your entire stack is LangChain/LangGraph
- You need the tightest possible agent step-debugging experience
- You're comfortable with proprietary tooling and SaaS pricing

## When Does the Arize AX Enterprise Upgrade Make Sense?

Arize AX is the commercial enterprise platform that sits above Phoenix, sharing the same tracing foundation but adding features that matter at organizational scale. Phoenix to AX is an upgrade path, not a migration — your existing OpenTelemetry instrumentation works unchanged, and Phoenix traces can be forwarded to AX without re-instrumenting your codebase.

AX adds capabilities that Phoenix does not ship: role-based access control (RBAC) for multi-team environments, SSO integration (SAML, OIDC), advanced anomaly detection with alerting, production monitoring dashboards with SLA-grade uptime guarantees, dedicated support SLAs, and compliance reporting for SOC 2 and HIPAA-regulated deployments.

The upgrade makes economic sense when: your team has grown past 10-15 engineers sharing a single Phoenix instance and RBAC becomes a pain point; your legal team requires audit trails and SOC 2 compliance evidence; you need PagerDuty/OpsGenie integration for production LLM quality alerts; or your data volume exceeds what a self-managed PostgreSQL backend can handle without dedicated infrastructure investment.

For most startups and small engineering teams, Phoenix's open-source version handles millions of daily spans without operational overhead. AX is targeted at enterprises with dedicated ML platform teams and organizational compliance requirements.

## FAQ

**Q: Is Arize Phoenix completely free?**

Yes. Arize Phoenix is released under the Apache 2.0 license with no feature gating. You can run it locally, on your own servers, or in your own cloud account with no usage limits, no required API keys, and no phone-home telemetry. The commercial upgrade is Arize AX, a separate product with enterprise features — Phoenix itself remains fully open source.

**Q: Does Phoenix work with non-OpenAI models like Claude, Gemini, or open-source LLMs?**

Yes. Phoenix supports any model through OpenTelemetry instrumentation. For Anthropic Claude, use `openinference-instrumentation-anthropic`. For local models via Ollama or vLLM, use `openinference-instrumentation-litellm` with LiteLLM as a proxy. For Google Gemini, use the LiteLLM integration or manual spans. The `openinference` semantic conventions are model-provider agnostic.

**Q: How does Phoenix handle trace data storage and retention?**

By default, Phoenix stores all traces in a local SQLite database at `~/.phoenix/` (or the `PHOENIX_WORKING_DIR` path in Docker). There are no built-in retention limits — traces accumulate until you delete them. In production Docker deployments, mount a persistent volume to `/mnt/data`. For large-scale production, configure PostgreSQL as the backend to handle higher write throughput and enable standard database backup/retention policies.

**Q: Can Phoenix run in CI/CD pipelines for automated LLM quality gates?**

Yes, and this is one of Phoenix's strongest use cases. The `phoenix.evals` Python API runs independently of the Phoenix UI server — you can run evaluations in a CI job using `run_evals()`, check scores programmatically, and fail the pipeline if quality drops below threshold. Many teams run Phoenix evals as a pytest fixture or a standalone script that gates deployments when hallucination rate exceeds a threshold.

**Q: What is the difference between Phoenix traces and traditional APM traces?**

Traditional APM traces (Datadog, Jaeger, Zipkin) capture latency, error rates, and resource usage but have no understanding of LLM-specific semantics — they see an HTTP call to `api.openai.com` but can't tell you what prompt was sent or whether the response was faithful to the retrieved context. Phoenix traces use OpenInference semantic conventions that embed LLM-specific data — input messages, output messages, retrieved documents, embedding vectors, token counts — directly into span attributes, making them queryable and evaluatable in LLM-specific ways.
