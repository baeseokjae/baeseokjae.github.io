---
cover:
  alt: 'Claude 300K Output Tokens Guide: Batch API for Large Code Generation 2026'
  image: /images/claude-300k-output-tokens-guide-2026.png
  relative: false
date: 2026-06-09 22:01:56+00:00
description: How to use Claude's 300K output token extended mode via the Message Batches
  API — models, pricing, limits, and code generation workflows.
draft: false
schema: schema-claude-300k-output-tokens-guide-2026
tags:
- claude
- anthropic
- batch-api
- code-generation
- llm-api
title: 'Claude 300K Output Tokens Guide: Batch API for Large Code Generation 2026'
---

Claude's Extended Output beta raises the `max_tokens` ceiling from 128K to **300,000 tokens** — but only for requests sent through the Message Batches API. If you're generating full codebases, book-length documentation, or exhaustive structured extractions in a single turn, this guide covers everything you need to get it working.

## What Is Extended Output and How Does It Work?

Extended Output is a Claude API beta feature, activated via the `anthropic-beta: output-300k-2026-03-24` header, that increases the maximum `max_tokens` limit per request from 128,000 to 300,000 tokens. As of June 2026, it is **only available on the Message Batches API** — the synchronous Messages API remains capped at 64K–128K depending on the model. The models that support extended output are Claude Opus 4.8, Opus 4.7, Opus 4.6, and Sonnet 4.6, all of which carry 1M-token context windows. Claude Fable 5 and Mythos 5 are explicitly excluded and remain at 128K output. A single 300K-token generation can take **over an hour** to complete, which is why the asynchronous batch architecture is a prerequisite. This is not a setting you flip on a chat endpoint — it's a deliberate architectural tradeoff: accept latency, gain volume. The practical upside is book-length code scaffolds, full API documentation sets, and exhaustive data extraction jobs that previously required chaining multiple requests with fragile state management between them.

### Why the Batch API Requirement?

The Message Batches API processes requests asynchronously in the background, returning results when complete rather than streaming in real time. Because a 300K-token generation can exceed an hour of compute time, synchronous API timeouts make extended output structurally impossible on that path. The batch API was designed for exactly this tradeoff — you submit work, poll for results, and retrieve them when ready.

## Which Models and Platforms Support Extended Output?

Not all Claude models or deployment platforms support the 300K extended output feature. This table shows the current state as of June 2026.

| Model | Max Output (Standard) | Max Output (Extended) | Platforms |
|---|---|---|---|
| Claude Opus 4.8 | 128K | **300K** | Claude API, Claude Platform on AWS |
| Claude Opus 4.7 | 128K | **300K** | Claude API, Claude Platform on AWS |
| Claude Opus 4.6 | 128K | **300K** | Claude API, Claude Platform on AWS |
| Claude Sonnet 4.6 | 64K | **300K** | Claude API, Claude Platform on AWS |
| Claude Fable 5 | 128K | ❌ Not supported | All |
| Claude Mythos 5 | 128K | ❌ Not supported | All |

**Platform availability is a hard constraint.** Extended output works on `api.anthropic.com` and Claude Platform on AWS. It is **not available** on Amazon Bedrock, Google Vertex AI, or Microsoft Foundry. If your infrastructure routes Claude calls through Bedrock or Vertex, you cannot use 300K output without redirecting those requests to the direct Claude API.

### Model Selection Tradeoffs

Claude Opus 4.8 is the most capable model for complex code generation but costs $2.50/MTok input and $12.50/MTok output at batch pricing (50% off standard). Sonnet 4.6 is significantly cheaper at roughly half the Opus 4.8 rate while supporting the same 300K output limit. For boilerplate-heavy tasks like generating CRUD endpoints, migration files, or config scaffolds, Sonnet 4.6 at batch pricing is often the economically correct choice. Reserve Opus 4.8 for tasks where architectural reasoning matters — generating a plugin system, designing a state machine, or producing documentation that requires deep understanding of the codebase.

## How the Message Batches API Works

The Message Batches API is an asynchronous job queue built into the Claude API. You submit a batch containing up to 100,000 individual Message requests (or 256 MB total, whichever limit is hit first), and the API processes them in the background. Results are typically available within **one hour**, though complex 300K-token generations can push past that. Batches expire if processing doesn't complete within 24 hours. Results stay retrievable for **29 days** after creation.

The request format wraps each individual Message in a `custom_id` envelope:

```python
import anthropic

client = anthropic.Anthropic()

batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "scaffold-user-auth",
            "params": {
                "model": "claude-opus-4-8-20260101",
                "max_tokens": 300000,
                "messages": [
                    {
                        "role": "user",
                        "content": "Generate a complete user authentication module..."
                    }
                ]
            }
        }
    ],
    betas=["output-300k-2026-03-24"]
)

print(batch.id)  # batch_01...
```

Polling for results:

```python
import time

while True:
    batch_status = client.messages.batches.retrieve(batch.id)
    if batch_status.processing_status == "ended":
        break
    time.sleep(60)

# Stream results
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(result.custom_id, result.result.message.content[0].text[:200])
```

### Batch Limitations Summary

| Constraint | Limit |
|---|---|
| Max requests per batch | 100,000 |
| Max batch size | 256 MB |
| Typical processing time | ~1 hour |
| Max processing time before expiry | 24 hours |
| Results retention | 29 days |
| Concurrent batches | No published limit |

## Extended Output Use Cases for Code Generation

Extended Output at 300K tokens unlocks generation tasks that are genuinely impossible at the 128K ceiling. A 300K-token output is approximately 225,000 words — enough for a 700-page technical manual, a fully scaffolded microservice with tests and documentation, or the complete migration of a mid-size codebase from one framework to another.

**High-value use cases developers are already running in production:**

- **Full microservice scaffolding**: Generate a complete service with routes, middleware, data models, database migrations, unit tests, integration tests, Dockerfile, and deployment config in a single batch request. At 128K you're forced to split this across multiple turns, losing coherence between layers.
- **Exhaustive API documentation**: Feed the full OpenAPI spec and generate developer docs, code examples in 5 languages, error handling guides, and a getting-started tutorial without truncation.
- **Large-scale structured data extraction**: Transform raw unstructured datasets (support tickets, legal documents, medical records) into typed JSON schemas at scale — 300K tokens of output maps to thousands of structured records per request.
- **Codebase migration**: Provide an entire legacy module as input and generate a fully refactored version in the target language or framework, with inline comments explaining each transformation decision.
- **Long reasoning chains**: For math-heavy or logic-intensive problems, 300K output allows Claude to show all intermediate steps without hitting a ceiling mid-derivation.

## Pricing Economics: The 50% Batch Discount

The Message Batches API applies a **50% discount** to both input and output tokens across all supported models. This makes extended output economically viable even for large-scale generation tasks that would otherwise be prohibitively expensive at synchronous API rates.

| Model | Standard Input | Batch Input | Standard Output | Batch Output |
|---|---|---|---|---|
| Claude Opus 4.8 | $5.00/MTok | **$2.50/MTok** | $25.00/MTok | **$12.50/MTok** |
| Claude Opus 4.7 | $3.00/MTok | **$1.50/MTok** | $15.00/MTok | **$7.50/MTok** |
| Claude Sonnet 4.6 | $1.50/MTok | **$0.75/MTok** | $7.50/MTok | **$3.75/MTok** |

**Real cost example:** Generating a complete authentication module at 150K output tokens using Opus 4.8 batch costs $1.875 in output tokens alone. The same request at standard synchronous pricing (if the 128K ceiling didn't exist) would cost $3.75. The economics improve significantly at scale — running 100 such requests in a single batch costs $187.50 in output versus $375 at synchronous rates.

For Sonnet 4.6, that same 150K-token generation costs $0.5625 at batch pricing — roughly 3× cheaper than Opus 4.8 batch. Teams running automated code generation pipelines at scale should benchmark their quality threshold carefully before defaulting to Opus.

## Processing Time: Planning for Multi-Hour Jobs

The single biggest operational change when adopting extended output is accepting multi-hour job latency. A 300K-token generation on Opus 4.8 can take **well over an hour**. Plan your architecture accordingly.

**Patterns that work:**

- **Offline batch jobs**: Nightly code generation pipelines, documentation refresh cycles, end-of-sprint codebase analysis. These are fire-and-forget tasks where results are expected the next morning.
- **Pre-generation**: Generate code scaffolds or documentation in advance of when they're needed. A deployment pipeline can submit batch jobs an hour before the deployment window opens.
- **Queue-backed workflows**: Use a job queue (SQS, Pub/Sub, Redis Streams) to decouple batch submission from result consumption. Workers poll or subscribe to results independently.

**Patterns that don't work:**

- Real-time interactive features (users waiting for results)
- CI/CD gates that block on a test suite completion
- Any workflow where latency under 60 seconds is required

If you need low-latency large outputs, the current ceiling is the synchronous API at 64K–128K tokens — which is still substantial for most interactive use cases.

## Combining Extended Output with Extended Thinking and Tool Use

Extended Output is compatible with extended thinking and tool use within batch requests. This combination is particularly powerful for complex code generation tasks that benefit from structured reasoning.

**Extended thinking in batch:**

```python
{
    "custom_id": "architect-payment-service",
    "params": {
        "model": "claude-opus-4-8-20260101",
        "max_tokens": 300000,
        "thinking": {
            "type": "enabled",
            "budget_tokens": 20000
        },
        "messages": [...],
        "betas": ["output-300k-2026-03-24", "interleaved-thinking-2025-05-14"]
    }
}
```

Extended thinking uses `budget_tokens` from the overall 300K token budget. A 20K thinking budget leaves 280K for final output. Use thinking sparingly in 300K generation tasks — the primary value-add of 300K output is *volume*, and burning 50K+ thinking tokens on a straightforward scaffolding task wastes both time and money.

**Tool use in batch** is fully supported including server tools (web search, web fetch, code execution, MCP connectors). This enables patterns like: generate a full module with code execution to verify syntax, web search to pull in current API docs, and MCP integration to query the existing codebase structure — all within a single 300K-token batch request.

## Prompt Caching Strategy for 300K-Token Batch Requests

Prompt caching is critical for cost efficiency when running repeated batch requests against the same codebase or context. Cache hits apply a 90% discount on input tokens for cached prefixes.

The key insight is that a 300K-output request often has a *large* input too — feeding in hundreds of files for a refactoring task can easily hit 500K–700K input tokens. Without caching, each batch request pays full input cost. With caching, only the changing portion (the specific task instructions) incurs full input cost.

```python
{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": "<codebase>...[full codebase here]...</codebase>",
            "cache_control": {"type": "ephemeral"}
        },
        {
            "type": "text",
            "text": "Generate complete unit tests for the PaymentService class."
        }
    ]
}
```

The codebase prefix gets cached after the first request; subsequent batch requests reuse the cache. Cached tokens cost $0.25/MTok for Opus 4.8 (vs $2.50/MTok standard) — a 90% reduction. For pipelines generating multiple artifacts from the same codebase, caching the full source context can dominate overall cost savings.

## Long-Running Agent Harness Pattern for Batch Code Generation

Anthropic's engineering team published a harness pattern for long-running agents that maps directly onto 300K batch generation pipelines. The core insight: a single generation session can fail partway through, so you need continuity mechanisms to resume rather than restart.

**The two-agent pattern:**

1. **Initializer agent** (first run): Analyzes the full task, creates a `task-list.md` file listing every deliverable (e.g., every file to be generated), and submits the first batch.
2. **Continuation agent** (subsequent runs): Reads `task-list.md`, checks which items are marked complete, generates only the remaining items in new batches.

This prevents the failure mode where a 300K generation succeeds for 80% of the task and then the process crashes — forcing a full restart and paying full cost again. With incremental progress tracking via `git commit` after each batch completes, you get cheap resumability.

```python
# task-list.md pattern
TASKS = [
    {"file": "src/auth/user.model.ts", "status": "done"},
    {"file": "src/auth/auth.service.ts", "status": "pending"},
    {"file": "src/auth/auth.controller.ts", "status": "pending"},
    ...
]
```

## The Hybrid Pattern: Batch for Generation, Sync for Refinement

The most practical production architecture combines both APIs: use batch extended output for the initial generation phase, then switch to synchronous API for iterative refinement.

**Phase 1 — Batch generation (overnight or pre-scheduled):**
- Submit 300K-token requests for complete module scaffolding
- Accept 1–2 hour latency
- Get full codebase skeleton: routes, models, tests, docs

**Phase 2 — Synchronous refinement (real-time, developer-in-the-loop):**
- Developer reviews the generated scaffold
- Uses standard Claude API (synchronous) to request targeted changes
- Short, focused turns: "Refactor the auth middleware to use JWT instead of sessions"

This pattern avoids paying Opus 4.8 batch prices for short conversational turns, while still using the 300K capability where it delivers maximum value — initial generation where coherence across the full output matters most.

## FAQ

The five questions below cover the most common points of confusion developers hit when adopting Claude's 300K output token capability. Extended Output is a beta feature activated via the `anthropic-beta: output-300k-2026-03-24` request header as of June 2026, and its availability, pricing model, and supported models differ meaningfully from the standard Claude API. Before shipping a production pipeline around it, review the platform exclusions and plan for asynchronous job latency — the two factors that catch teams off guard most often. The 300K limit is exclusive to the Message Batches API; the synchronous Messages endpoint remains hard-capped at 64K–128K tokens depending on the model. Extended output is not available on Amazon Bedrock or Google Vertex AI regardless of model version. All answers reflect Anthropic's published documentation and batch processing specs as of the June 2026 research date for Opus 4.8, 4.7, 4.6, and Sonnet 4.6.

### Can I use Claude 300K output tokens on Amazon Bedrock?

No. Extended Output (`output-300k-2026-03-24`) is only available on `api.anthropic.com` and Claude Platform on AWS. Amazon Bedrock, Google Vertex AI, and Microsoft Foundry are explicitly excluded as of June 2026. If you're locked into Bedrock for compliance reasons, the ceiling remains 128K output.

### How long does a 300K token generation actually take?

Anthropic's documentation states "over an hour" for a single 300K-token generation. In practice, generation time depends on the model (Opus 4.8 is slower than Sonnet 4.6), batch queue depth, and the complexity of the content. Plan for 1–3 hours for Opus 4.8 at 300K tokens. Batches expire if processing doesn't complete within 24 hours.

### Does extended output work with extended thinking?

Yes, extended thinking is compatible with extended output in batch requests. The `budget_tokens` you allocate to thinking count against the 300K total. For a 300K request with a 30K thinking budget, the visible output ceiling is 270K tokens. Use the interleaved thinking beta (`interleaved-thinking-2025-05-14`) to enable thinking between tool calls.

### What happens if my batch request fails mid-generation?

Individual requests within a batch can succeed or fail independently. The `type` field in each result is either `"succeeded"`, `"errored"`, or `"expired"`. Build your result handler to check this field per request and re-queue failed items in a new batch. The `custom_id` field lets you map results back to your original requests.

### Is 300K output available for free tier or test API keys?

No. Extended Output is a production API feature. Standard rate limits and tier requirements apply. Given the compute intensity of 300K-token generations, expect that high-volume usage will require coordinating with Anthropic on rate limits, especially when submitting batches of many 300K requests simultaneously.