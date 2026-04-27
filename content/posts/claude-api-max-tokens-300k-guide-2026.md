---
title: "Claude API 300K Output Tokens: Complete Guide to Long-Form Generation (2026)"
date: 2026-04-27T01:04:22+00:00
tags: ["Claude API", "Anthropic", "LLM", "batch processing", "long-form generation"]
description: "How to unlock Claude API 300K output tokens via the Message Batches API with the output-300k-2026-03-24 beta header — with Python code examples."
draft: false
cover:
  image: "/images/claude-api-max-tokens-300k-guide-2026.png"
  alt: "Claude API 300K Output Tokens: Complete Guide to Long-Form Generation (2026)"
  relative: false
schema: "schema-claude-api-max-tokens-300k-guide-2026"
---

The Claude API now supports up to 300,000 output tokens per request — roughly 460 pages of text in a single API call — but only through the Message Batches API with a specific beta header. The synchronous API remains capped at 64K tokens. This guide explains exactly how to enable 300K output, which models support it, when to use it, and what it costs.

## What Are Claude API 300K Output Tokens?

Claude API 300K output tokens refers to Anthropic's maximum per-request generation limit, available on Claude Sonnet 4.6, Opus 4.6, and Opus 4.7 via the asynchronous Message Batches API. At approximately 650 words per 1,000 tokens, 300,000 tokens translates to roughly 195,000 words — the equivalent of a 460-page technical document or a full software codebase migration in a single API call. This capability is unlocked by passing the `output-300k-2026-03-24` beta header with your batch request; without it, even Sonnet 4.6 caps at 64K tokens on synchronous calls. The 300K limit represents a 4.7× increase over the previous 64K ceiling and is the highest output token limit of any major LLM API in 2026 — GPT-4o Long Output tops out at 64K, and Gemini 1.5 Pro at 8K. For enterprises running document generation, codebase analysis, or legal drafting pipelines, this change fundamentally alters the economics of LLM-based automation.

## Which Models Support 300K Output Tokens?

The 300K output token limit is available on specific Claude models only, and the standard 8K or 64K limits still apply everywhere else. Knowing which model to use prevents silent truncation and wasted API spend.

| Model | Standard Output Limit | 300K Batch Output | Batch Pricing (Output/MTok) |
|---|---|---|---|
| Claude Opus 4.7 | 32K | Yes | $12.50 |
| Claude Opus 4.6 | 32K | Yes | $12.50 |
| Claude Sonnet 4.6 | 64K | Yes | $7.50 |
| Claude Haiku 4.5 | 8K | No | $1.25 |
| Claude Sonnet 3.7 | 64K | No | — |

**Key rule:** Only models in the Claude 4.x family with the `output-300k-2026-03-24` beta header on a Message Batches API request get 300K output. Haiku 4.5 and all 3.x-series models are excluded. When in doubt, use Sonnet 4.6 for cost-efficiency (batch output at $7.50/MTok) or Opus 4.7 for maximum instruction-following fidelity on deeply structured documents.

## How to Enable 300K Output: The output-300k-2026-03-24 Beta Header

Enabling the 300K output limit requires adding a single `anthropic-beta` header to your Message Batches API request. This is the only mechanism Anthropic has exposed for 300K output as of April 2026 — there is no console toggle, no SDK flag, and no way to enable it on synchronous `/v1/messages` calls.

The specific header value is `output-300k-2026-03-24`. The date suffix is part of the official header name and must be included exactly. Setting `max_tokens: 300000` in your request body alone will not unlock 300K output without this header — the API will silently clamp your response to the model's default maximum.

To add the header in the Python SDK:

```python
import anthropic

client = anthropic.Anthropic()

# For direct HTTP — add to headers dict:
# "anthropic-beta": "output-300k-2026-03-24"

# For SDK-level batch creation, pass it as:
batch = client.beta.messages.batches.create(
    requests=[...],
    betas=["output-300k-2026-03-24"],  # SDK convenience param
)
```

The `betas` parameter on the SDK's batch create method maps directly to the `anthropic-beta` HTTP header. You can pass multiple beta features as a list (e.g., `["output-300k-2026-03-24", "interleaved-thinking-2025-05-14"]`). This approach is compatible with prompt caching — add `cache_control` to your system or user blocks as normal.

## Step-by-Step: Using the Message Batches API for 300K Output (Python Code Examples)

The Message Batches API is an asynchronous endpoint that accepts up to 10,000 requests per batch, processes them within 24 hours, and returns results as a JSONL stream. Using it for 300K output requires three steps: submit the batch, poll for completion, and stream results.

**Step 1 — Submit the batch:**

```python
import anthropic

client = anthropic.Anthropic()

batch = client.beta.messages.batches.create(
    requests=[
        {
            "custom_id": "doc-generation-001",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 300000,
                "system": (
                    "You are a senior technical writer. Generate complete, "
                    "exhaustive documentation with no truncation."
                ),
                "messages": [
                    {
                        "role": "user",
                        "content": "Write a complete 200-page API reference guide for...",
                    }
                ],
            },
        }
    ],
    betas=["output-300k-2026-03-24"],
)

print(f"Batch ID: {batch.id}")
print(f"Status: {batch.processing_status}")
```

**Step 2 — Poll for completion:**

```python
import time

def wait_for_batch(client, batch_id, poll_interval=60):
    while True:
        batch = client.beta.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            return batch
        print(f"Status: {batch.processing_status} — waiting {poll_interval}s")
        time.sleep(poll_interval)

completed = wait_for_batch(client, batch.id)
print(f"Request counts: {completed.request_counts}")
```

**Step 3 — Stream results:**

```python
for result in client.beta.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        content = result.result.message.content[0].text
        token_count = result.result.message.usage.output_tokens
        print(f"ID: {result.custom_id} | Tokens: {token_count}")
        # Write content to file or database
        with open(f"{result.custom_id}.txt", "w") as f:
            f.write(content)
    elif result.result.type == "errored":
        print(f"Error on {result.custom_id}: {result.result.error}")
```

Batch requests do not count against your synchronous rate limits, which means you can submit large batches without affecting production API throughput.

## Synchronous vs Asynchronous: When to Use 64K vs 300K Output

Choosing between the synchronous API (64K max) and the Batches API (300K max) depends on your latency tolerance, UX requirements, and batch size. Both have valid use cases, and the wrong choice for your workload can cost 2× more or introduce unacceptable delays.

| Criterion | Synchronous API (64K) | Batches API (300K) |
|---|---|---|
| Latency | Seconds to minutes | Up to 24 hours |
| Output limit | 64K tokens | 300K tokens |
| Cost | Standard rates | 50% discount |
| Use case | Real-time chatbots, streaming | Offline pipelines, bulk generation |
| Rate limits | Shared with other sync calls | Separate batch limits |
| Result delivery | Streaming or immediate JSON | JSONL result stream after completion |

**Use synchronous (64K) when:** your application needs real-time responses, you're building a user-facing chatbot or coding assistant, the output fits within 64K tokens, or you require streaming. The synchronous API also supports prompt caching with identical cache TTLs.

**Use batch (300K) when:** you're running nightly document generation jobs, processing large queues of independent requests, generating codebases or technical books, or doing cost-sensitive bulk work where 50% cost savings justify async delivery.

The inflection point is roughly this: if you need more than 64K output tokens OR you have more than 100 independent requests to process, the Batches API is almost always the right choice.

## Real-World Use Cases for 300K Output Tokens

The 300K output token limit unlocks document and code generation tasks that were previously impossible in a single API call. At 195,000 words per request, the realistic use cases span legal, engineering, and content production workflows.

**Full codebase migration:** A 100,000-line Python 2 → Python 3 migration can be completed in a single batch call using Opus 4.7. Feed the entire codebase as input context (leveraging the 1M-token context window on Sonnet 4.6), instruct Claude to output the migrated code, and receive the complete refactored codebase in one response — no chunking, no stitching, no context loss between chunks.

**Legal document drafting:** A 200-page commercial contract, complete with exhibits and schedules, runs approximately 130,000 tokens. A batch call with `max_tokens: 200000` generates the entire document with consistent clause numbering, cross-references, and defined terms — something that breaks down badly when chunked across multiple calls.

**Technical book generation:** A 60-chapter technical manual at 2,500 words per chapter totals ~150,000 tokens. With 300K headroom, Claude can generate the complete book plus appendices and index in a single request, maintaining consistent terminology and style throughout.

**Codebase documentation:** Generating JSDoc or docstring coverage for a large TypeScript monorepo (50K+ LOC) at 300K output means the entire documentation pass completes in one batch job rather than hundreds of chunked API calls.

**Test suite generation:** Generating comprehensive test suites for a backend API — unit tests, integration tests, fixture data — can easily hit 100K+ tokens when complete. One batch call produces the full test coverage.

## Cost Analysis: 300K Batch vs Multi-Call Chunking Approach

The economic case for the Batches API is compelling for large-scale generation. The 50% cost discount on batch calls, combined with eliminating chunking overhead, often reduces total cost by 60–75% for workloads that previously required multi-call approaches.

**Example: Generate a 200-page technical document (~150K output tokens)**

*Multi-call chunking approach (synchronous):*
- 3 calls × 50K output tokens each = 150K total output tokens
- Cost at Sonnet 4.6 standard rates ($15.00/MTok output): $2.25
- Plus: 3× input tokens re-sent per call (repeated context) ≈ 2× input overhead
- Total input overhead: ~300K extra input tokens × $3.00/MTok = $0.90 additional
- **Total: ~$3.15**

*Single batch call (300K output):*
- 1 batch call × 150K output tokens
- Cost at Sonnet 4.6 batch rates ($7.50/MTok output): $1.125
- Input once at batch rates ($1.50/MTok): input cost ~60% lower
- **Total: ~$1.35**

The batch approach saves approximately **57%** in this scenario — and the savings grow with output volume because you eliminate redundant context re-submission entirely. For pipelines generating millions of tokens per day, this difference is significant: at 100M output tokens/month, you save ~$750,000/year switching from chunked sync calls to single batch calls.

The trade-off is latency: batch results arrive within 24 hours, not seconds. For offline pipelines and nightly jobs, this is irrelevant.

## Claude 300K Output vs Competitors (GPT-4o, Gemini)

Claude's 300K batch output limit is the highest of any major LLM API as of April 2026. Understanding how this compares to OpenAI and Google's offerings helps justify the architectural choice.

| Model | Max Output Tokens | Batch Discount | Context Window |
|---|---|---|---|
| Claude Sonnet 4.6 (batch) | 300,000 | 50% | 1,000,000 |
| Claude Opus 4.7 (batch) | 300,000 | 50% | 200,000 |
| GPT-4o Long Output | 64,000 | ~50% (Batch API) | 128,000 |
| GPT-4.1 | 32,768 | ~50% (Batch API) | 1,000,000 |
| Gemini 1.5 Pro | 8,192 | No batch API | 1,000,000 |
| Gemini 2.0 Flash | 8,192 | No batch API | 1,000,000 |

Claude holds two structural advantages: a 4.7× higher output ceiling than GPT-4o's best offering, and a 1M-token context window on Sonnet 4.6 that means you can feed massive input documents and get massive outputs in the same call. GPT-4o's Long Output variant is capped at 64K tokens and requires the same type of beta access — but never exceeds that ceiling.

Beyond raw limits, Claude maintains instruction-following quality at 150K+ output tokens in ways GPT-4o does not. In benchmarks comparing 150K+ token outputs, Claude Sonnet 4.6 maintains consistent formatting, numbering, and terminology through the full response; GPT-4o shows measurable degradation past ~100K tokens including repetition, dropped sections, and inconsistent formatting.

For Gemini users: Google has not released a batch API with output discounts as of April 2026, and Gemini's 8K output ceiling makes it unsuitable for any long-form generation use case regardless of context window size.

## Best Practices for Long-Form Generation with Claude API

Reliably filling 300K output tokens with high-quality content requires prompt engineering strategies different from short-form generation. Claude can generate 300K tokens, but naive prompts produce verbose padding rather than substantive content.

**Be explicit about expected length and structure.** Instruct Claude upfront: "Generate a complete 180,000-word technical manual. Do not summarize or truncate. Every chapter must contain at least 15,000 words." Without explicit length targets, Claude optimizes for completeness-per-token rather than absolute token count.

**Use structured output templates.** Provide a skeleton outline in your prompt with placeholders. Claude fills placeholders more reliably than generating structure and content simultaneously for very long outputs. For a 200-chapter book, include chapter headers and minimum section requirements in the prompt.

**Split into sections with explicit continuation markers.** For documents with natural divisions (chapters, modules, sections), instruct Claude to mark section boundaries explicitly: `[SECTION: Chapter 5 — Authentication]`. This makes downstream parsing trivial and ensures section-level completeness.

**Use prompt caching for repeated system prompts.** If you're running multiple batch requests with the same style guide or system instructions, add `"cache_control": {"type": "ephemeral"}` to those blocks. Cached tokens cost 10% of standard input rates on read, reducing input costs by 90% for the repeated portions.

**Verify output completeness with token counts.** Check `usage.output_tokens` in your batch results. If a 300K-token request returns 85K tokens, the model may have interpreted the task as complete before filling the budget. Adjust prompts to signal that incomplete output is an error.

**Handle batch errors gracefully.** Batch results include per-request success/error status. Implement retry logic for `errored` results, and log `overloaded_error` vs `invalid_request_error` separately — the former is transient (retry), the latter requires prompt correction.

## Rate Limits, Polling, and Handling Batch Results

The Message Batches API has its own rate limit tier separate from the synchronous API. Understanding these limits prevents batch submission failures and ensures efficient polling patterns.

**Batch submission limits:** Each batch can contain up to 10,000 requests. The total token volume per batch is limited to your organization's token quota. For very large workloads, split across multiple batches and submit sequentially or in parallel depending on your quota headroom.

**Polling best practices:** Poll batch status no more frequently than every 60 seconds. The Anthropic SDK does not include built-in polling — implement exponential backoff starting at 60 seconds for long-running batches:

```python
import time
import anthropic

def poll_with_backoff(client, batch_id):
    interval = 60
    max_interval = 600  # 10 minutes max
    
    while True:
        batch = client.beta.messages.batches.retrieve(batch_id)
        
        if batch.processing_status == "ended":
            return batch
        
        counts = batch.request_counts
        print(
            f"Processing: {counts.processing} | "
            f"Succeeded: {counts.succeeded} | "
            f"Errored: {counts.errored}"
        )
        
        time.sleep(interval)
        interval = min(interval * 1.5, max_interval)
```

**Streaming batch results:** Use `.results()` to stream the JSONL output file rather than loading all results into memory at once. This is critical for large batches — a 10,000-request batch result file can be several GB:

```python
for result in client.beta.messages.batches.results(batch_id):
    if result.result.type == "succeeded":
        process_result(result)
    elif result.result.type == "errored":
        log_error(result.custom_id, result.result.error)
```

**Result retention:** Anthropic retains batch results for 29 days. Download and store results in your own infrastructure before the 29-day window expires — after that, the results are permanently deleted.

**Cancellation:** Batches can be cancelled while in `processing` status. Requests that completed before cancellation are billed normally; unprocessed requests are not charged.

```python
# Cancel a batch if needed
client.beta.messages.batches.cancel(batch_id)
```

## FAQ: Common Questions About Claude API 300K Output

**Q: Can I get 300K output on the synchronous `/v1/messages` API?**

No. The 300K output limit is exclusively available through the Message Batches API (`/v1/messages/batches`) with the `output-300k-2026-03-24` beta header. The synchronous API is hard-capped at 64K tokens on Sonnet 4.6 and 32K on Opus 4.6/4.7 regardless of what you pass as `max_tokens`. This architectural separation exists because generating 300K tokens takes significantly longer than synchronous request timeouts allow.

**Q: Does the output-300k-2026-03-24 header expire?**

Beta headers in Anthropic's API are dated to indicate when the feature was introduced, not when it expires. The `output-300k-2026-03-24` header is the current stable way to enable 300K output as of April 2026. Anthropic will provide migration guidance if the header format changes. Monitor the official [model documentation](https://platform.claude.com/docs/en/about-claude/models/overview) for updates.

**Q: Does prompt caching work with 300K batch output requests?**

Yes. You can combine `cache_control: {"type": "ephemeral"}` blocks with the `output-300k-2026-03-24` beta header. Cache reads cost 10% of standard input token rates, and writes cost 25%. This is particularly valuable for long system prompts (style guides, schemas, context documents) that repeat across many batch requests.

**Q: How long does a 300K token batch response take to generate?**

Processing time depends on current batch queue depth and the specific model. In practice, a single 300K-token request typically completes in 15–45 minutes once it begins processing, but queue wait time can extend total wall-clock time to several hours. Anthropic guarantees results within 24 hours. For time-sensitive workloads, the synchronous API with 64K output is more predictable.

**Q: What happens if my prompt isn't complex enough to fill 300K tokens?**

Claude generates the natural length for your task — it does not pad output to reach `max_tokens`. If you need a minimum output length, instruct Claude explicitly: "This document must be at least 150,000 words. Include exhaustive detail, worked examples for each section, and annotated code listings." The `max_tokens` parameter sets a ceiling, not a floor.
