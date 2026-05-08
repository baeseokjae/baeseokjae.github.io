---
title: "xAI Grok API Pricing 2026: Every Model, Context Window, and Cost Compared"
date: 2026-05-07T12:00:00+00:00
tags: ["grok", "xai", "api-pricing", "llm-pricing", "cost-comparison"]
description: "Full xAI Grok API pricing breakdown for 2026: Grok 4.1 Fast, Grok 4.20, Grok Code Fast 1 — with context windows, cost tables, and competitor comparisons."
draft: false
cover:
  image: "/images/xai-grok-api-pricing-2026.png"
  alt: "xAI Grok API Pricing 2026: Every Model, Context Window, and Cost Compared"
  relative: false
schema: "schema-xai-grok-api-pricing-2026"
---

xAI's Grok API in 2026 offers three distinct models priced from $0.20 to $6.00 per million tokens, with a 2M-token context window on the flagship tiers — undercutting Anthropic's Claude Opus 4.7 by 92% on input costs and GPT-5.5 by 60% on output costs at comparable capability levels. The API is fully OpenAI-compatible, ships with built-in real-time web search, and supports prompt caching to further reduce repeated-context costs. This guide covers every model, every price point, and how to calculate what you will actually spend in production.

## xAI Grok API Pricing Overview: Three Models for Different Use Cases

xAI's Grok API lineup in 2026 is structured as a three-tier stack: a fast/cheap general-purpose model (Grok 4.1 Fast at $0.20/$0.50 per million tokens), a flagship reasoning model (Grok 4.20 at $2.00/$6.00 per million tokens), and a coding-optimized variant (Grok Code Fast 1 at $0.20/$1.50 per million tokens). All three use the same OpenAI-compatible REST API at `https://api.x.ai/v1`, meaning any codebase already integrated with the OpenAI Python SDK or TypeScript SDK can switch to Grok by changing the `base_url` parameter and swapping API keys — zero refactoring required. Grok 4.1 Fast and Grok 4.20 both carry a 2M-token context window, which is 10× larger than Anthropic's 200K limit and twice the size of GPT-5.5's 1M. Grok Code Fast 1 comes with a 256K context window, sized specifically for the large repository indexes that coding assistants need to maintain. Built-in real-time web search is available across all three models — a capability that competitors like GPT-5.5 and Claude charge extra for or require additional tooling to achieve. Prompt caching is supported on Grok 4.1 Fast and Grok 4.20, enabling significant cost reductions for applications that repeatedly send the same system prompt or document context across requests.

| Model | Input ($/M tokens) | Output ($/M tokens) | Context Window |
|---|---|---|---|
| Grok 4.1 Fast | $0.20 | $0.50 | 2M tokens |
| Grok 4.20 | $2.00 | $6.00 | 2M tokens |
| Grok Code Fast 1 | $0.20 | $1.50 | 256K tokens |

## Grok 4.1 Fast: High-Volume Applications at $0.20 Per Million Tokens

Grok 4.1 Fast is xAI's lowest-cost production model, priced at $0.20 per million input tokens and $0.50 per million output tokens — making it the go-to choice for applications where volume is high, latency matters, and per-request cost must stay under control. At those numbers, processing one billion tokens costs $200 on input and $500 on output, which is roughly what you spend on a single day of a mid-scale customer-support pipeline. The 2M-token context window — the same ceiling as the more expensive Grok 4.20 — means high-volume applications do not need to compromise on context depth to hit their cost targets. Grok 4.1 Fast is designed for background processing, batch classification, document summarization queues, and any workload where requests run in parallel at scale. Prompt caching is available on this tier: if your application repeatedly sends the same system prompt (say, a 10K-token instruction block), the cached portion is priced at a fraction of standard input cost, pushing effective input costs below $0.10 per million tokens for cache-heavy workloads. For developers running tens of millions of API calls per month, the difference between $0.20 and $2.00 per million input tokens is the difference between a manageable variable cost and a budget-busting line item.

**Grok 4.1 Fast: Cost calculation examples**

| Volume (tokens/month) | Input Cost | Output Cost | Total |
|---|---|---|---|
| 10M input / 5M output | $2.00 | $2.50 | $4.50 |
| 100M input / 50M output | $20.00 | $25.00 | $45.00 |
| 1B input / 500M output | $200.00 | $250.00 | $450.00 |

Assuming a 2:1 input-to-output ratio typical of classification and summarization tasks.

## Grok 4.20: Flagship Reasoning at Competitive Pricing

Grok 4.20 is xAI's flagship model, priced at $2.00 per million input tokens and $6.00 per million output tokens, targeting complex reasoning, long-document analysis, and research-grade synthesis tasks that require the full capability of a frontier model. Despite sitting at the top of xAI's lineup, Grok 4.20 is priced 7.5× below Claude Opus 4.7 on input ($2.00 vs. $15.00) and 12.5× below it on output ($6.00 vs. $75.00) — a gap so large it restructures how teams think about deploying flagship-class intelligence. The 2M-token context window on Grok 4.20 enables use cases that are simply impossible on 200K-context models: ingesting an entire codebase for architecture review, loading a multi-year contract corpus for due-diligence analysis, or processing a full research dataset in a single prompt without chunking. Prompt caching is fully supported on Grok 4.20, which matters considerably at this tier — a repeated 100K-token system prompt costs $0.20 per uncached call; with caching, that same context might cost a fraction of that on subsequent requests. For reasoning-heavy pipelines that send the same long context repeatedly (legal review, compliance checking, codegen with a fixed spec), caching can cut monthly Grok 4.20 spend by 40–60%.

**Grok 4.20: Cost calculation examples**

| Scenario | Input Tokens | Output Tokens | Cost per Request | Monthly Cost (1K req/day) |
|---|---|---|---|---|
| Long-doc analysis | 50K | 2K | $0.11 + $0.012 = $0.122 | $3,660 |
| Research synthesis | 200K | 10K | $0.40 + $0.06 = $0.46 | $13,800 |
| Full-context reasoning | 1M | 20K | $2.00 + $0.12 = $2.12 | $63,600 |

For enterprise-scale reasoning workloads, compare to Claude Opus 4.7 at the same volumes: the 1M-token request above costs $15.00 + $1.50 = $16.50 with Opus 4.7 vs. $2.12 with Grok 4.20 — a 7.8× cost difference per request.

## Grok Code Fast 1: Developer-Optimized Coding Model

Grok Code Fast 1 is priced at $0.20 per million input tokens and $1.50 per million output tokens, with a 256K context window tuned specifically for software development workloads: inline completions, code review, test generation, and coding-assistant backends where low latency and low cost-per-completion define success. The $0.20 input price matches Grok 4.1 Fast, but the $1.50 output price reflects the reality that code generation produces denser, higher-value tokens than general text — completions, function bodies, and test suites are consistently longer per request than summarization or classification outputs. The 256K context window is sufficient to hold a 50–100 file repository index, a full module with all its dependencies, or several hundred lines of accumulated conversation context from a coding session. For teams building IDE plugins, CI pipeline assistants, or autonomous coding agents, the combination of $0.20 input and $1.50 output makes Grok Code Fast 1 dramatically cheaper than GPT-5.5 ($5.00/$30.00) for the same coding throughput. A coding assistant generating 100M output tokens per month — roughly the volume of a mid-sized developer tool with several thousand active users — costs $150,000 per month with Grok Code Fast 1 vs. $3,000,000 per month with GPT-5.5 at full output pricing. That 20× cost advantage can be the deciding factor for early-stage developer tools trying to reach profitability before their next funding round.

**Grok Code Fast 1: Cost calculation examples**

| Use Case | Input/Request | Output/Request | Cost/Request | Monthly (500K req) |
|---|---|---|---|---|
| Inline completion | 2K | 200 | $0.000700 | $350 |
| Function generation | 10K | 1K | $0.003500 | $1,750 |
| Code review | 20K | 3K | $0.008500 | $4,250 |

## The 2M Context Window Advantage: Real Cost Implications

A 2M-token context window is not just a benchmark number — it eliminates entire categories of infrastructure complexity that teams currently pay for in engineering time, vector database costs, and chunking pipeline maintenance. At 2M tokens, Grok 4.1 Fast and Grok 4.20 can ingest approximately 1,500 pages of text, a 200K-line codebase, or a year's worth of customer support transcripts in a single API call, removing the need for retrieval-augmented generation (RAG) pipelines on most document-scale workloads. The direct cost implication: RAG pipelines require embedding models, vector stores, and retrieval logic that add $0.005–0.02 per query on top of LLM costs. For a pipeline running 1 million queries per month, eliminating RAG saves $5,000–$20,000 per month in infrastructure — partially or fully offsetting the LLM spend itself. Compare the 2M context ceiling to Anthropic's 200K and OpenAI's 1M (for GPT-5.5): a task that requires 800K tokens of context simply cannot run on Claude Opus 4.7 or Claude Sonnet 4.6 without chunking and multiple calls, which multiplies cost and introduces retrieval errors. Gemini 3.1 Pro matches Grok at 2M context but costs $3.50/$10.50 per million tokens — 75% more expensive on input and 75% more expensive on output than Grok 4.20. For teams whose bottleneck is context length rather than reasoning capability, Grok at the 2M tier is currently the most cost-efficient path to native long-context inference at scale.

**Context window comparison across providers**

| Model | Context Window | Input ($/M) | Output ($/M) | Cost for 1M-token input |
|---|---|---|---|---|
| Grok 4.1 Fast | 2M | $0.20 | $0.50 | $0.20 |
| Grok 4.20 | 2M | $2.00 | $6.00 | $2.00 |
| Gemini 3.1 Pro | 2M | $3.50 | $10.50 | $3.50 |
| GPT-5.5 | 1M | $5.00 | $30.00 | $5.00 |
| Claude Sonnet 4.6 | 200K | $3.00 | $15.00 | N/A (exceeds limit) |
| Claude Opus 4.7 | 200K | $15.00 | $75.00 | N/A (exceeds limit) |

## Competitor Pricing Comparison: Grok vs Claude vs GPT-5.5 vs Gemini

The 2026 LLM API market has fractured into two pricing tiers: sub-$1 fast models and $2–15 flagship models — and Grok occupies an unusually strong position in both camps simultaneously. Grok 4.20, despite being xAI's top-tier flagship model, is priced at $2.00/$6.00 per million tokens, landing it squarely in what other vendors price as mid-tier: Claude Sonnet 4.6 ($3.00/$15.00), Gemini 3.1 Pro ($3.50/$10.50), and GPT-5.5 ($5.00/$30.00) all cost more while offering smaller context windows. Claude Opus 4.7 at $15.00/$75.00 is in a different pricing bracket entirely — 7.5× more expensive on input and 12.5× more expensive on output than Grok 4.20. Whether Opus 4.7's quality premium justifies that gap depends entirely on your task: for open-ended creative reasoning, instruction-following in complex multi-step pipelines, and tasks where subtle nuance matters, Opus 4.7 may produce measurably better outcomes. For bulk document analysis, long-context summarization, and structured data extraction, Grok 4.20 at 2M context will frequently match or exceed Opus 4.7 at 200K — at one-seventh the cost. Built-in real-time web search is a genuine differentiator for Grok: GPT-5.5 and Claude require separate tool-calling setups or subscriptions to access live web data, while Grok exposes it natively via the API with no additional per-search fee.

**Full competitor pricing comparison**

| Model | Input ($/M) | Output ($/M) | Context | Web Search | Caching |
|---|---|---|---|---|---|
| Grok 4.1 Fast | $0.20 | $0.50 | 2M | Built-in | Yes |
| Grok 4.20 | $2.00 | $6.00 | 2M | Built-in | Yes |
| Grok Code Fast 1 | $0.20 | $1.50 | 256K | Built-in | No |
| Claude Sonnet 4.6 | $3.00 | $15.00 | 200K | Via tool | Yes |
| Claude Opus 4.7 | $15.00 | $75.00 | 200K | Via tool | Yes |
| GPT-5.5 | $5.00 | $30.00 | 1M | Via tool | Yes |
| Gemini 3.1 Pro | $3.50 | $10.50 | 2M | Via tool | Yes |

**Cost to process 100M input + 50M output tokens:**

| Model | Input Cost | Output Cost | Total |
|---|---|---|---|
| Grok 4.1 Fast | $20 | $25 | **$45** |
| Grok 4.20 | $200 | $300 | **$500** |
| Gemini 3.1 Pro | $350 | $525 | **$875** |
| Claude Sonnet 4.6 | $300 | $750 | **$1,050** |
| GPT-5.5 | $500 | $1,500 | **$2,000** |
| Claude Opus 4.7 | $1,500 | $3,750 | **$5,250** |

## Prompt Caching: How to Cut Grok API Costs by 50%+

Prompt caching on Grok 4.20 and Grok 4.1 Fast allows the API to reuse the KV-cache from a previous request when the prefix of a new request matches, charging a reduced rate for the cached portion instead of the full input token price. For applications with stable, long system prompts — a legal-review agent with a 50K-token jurisdiction and precedent block, a coding assistant with a 30K-token style guide, or a customer-support bot with a 20K-token product manual — caching eliminates the marginal cost of re-sending identical context on every call. The practical math: a 50K-token system prompt sent to Grok 4.20 without caching costs $0.10 per request; at 1,000 requests per day, that is $100/day or $3,000/month just for the system prompt. With caching, subsequent requests that hit the cache pay a fraction of the standard input rate — a saving that compounds quickly at scale. To trigger caching on xAI's API, structure your requests so the stable, repeated content appears at the beginning of the prompt (system prompt, then static context, then dynamic content), as the cache key is prefix-based. Caching is not beneficial for fully dynamic requests where no prefix is shared across calls — only workloads with stable, repeated context above roughly 1,024 tokens see meaningful savings. When both factors align (long context + high request volume), caching can reduce effective Grok 4.20 input costs from $2.00 per million down to sub-$0.50 per million on the cached portion, cutting total API spend by 40–60%.

**Caching savings example: Legal review agent**

| Scenario | Tokens | Requests/Day | Without Caching | With Caching (est. 70% hit rate) | Monthly Savings |
|---|---|---|---|---|---|
| System prompt (Grok 4.20) | 50K | 1,000 | $3,000/mo | ~$900/mo | $2,100 |
| Document context (Grok 4.20) | 200K | 500 | $6,000/mo | ~$1,800/mo | $4,200 |

## Getting Started: API Setup and First Request

The xAI API endpoint is `https://api.x.ai/v1` — OpenAI-compatible, which means you can authenticate and call it using the standard `openai` Python package or TypeScript SDK by overriding the `base_url` and passing your xAI API key. No separate SDK installation is required: if you already use `openai`, you are one configuration change away from running Grok in production. API keys are provisioned at `https://console.x.ai` after creating an xAI account. Billing is usage-based with no monthly minimum, and the same account covers all three Grok models. The model name strings for API calls are `grok-4-1-fast`, `grok-4-20`, and `grok-code-fast-1` — confirm the exact identifiers in the xAI console as naming conventions may evolve. Rate limits on new accounts default to conservative ceilings and can be raised by contacting xAI support with a description of your use case and projected monthly token volume. For teams moving from OpenAI or Anthropic, the most significant integration difference is that real-time web search does not require separate function-calling setup — it is available as a model capability flag in the request body rather than a tool definition. This simplifies the prompt design for search-augmented applications considerably compared to the tool-calling patterns required on GPT-5.5 or Claude.

**Python quickstart using the openai SDK:**

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-xai-api-key",
    base_url="https://api.x.ai/v1",
)

response = client.chat.completions.create(
    model="grok-4-20",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Summarize the current state of LLM API pricing."},
    ],
    max_tokens=1024,
)

print(response.choices[0].message.content)
```

**Switching models is a one-line change:**

```python
# Fast, cheap: $0.20/$0.50 per million tokens
model="grok-4-1-fast"

# Flagship reasoning: $2.00/$6.00 per million tokens
model="grok-4-20"

# Coding workloads: $0.20/$1.50 per million tokens
model="grok-code-fast-1"
```

## Cost Optimization Strategies for Production Grok Deployments

Production Grok deployments achieve the lowest effective cost-per-task by combining model routing, prompt caching, output token discipline, and workload batching — each strategy compounding the savings from the others. The single highest-leverage decision is model routing: not every request in your pipeline needs Grok 4.20's reasoning power, and sending every call to the flagship model when 60–70% of your workload is classification, extraction, or summarization is the most common source of inflated API bills. A routing layer that classifies incoming requests by complexity and directs simple tasks to Grok 4.1 Fast ($0.20/$0.50) and only genuinely complex reasoning to Grok 4.20 ($2.00/$6.00) typically reduces per-token blended cost by 50–70% at scale. Prompt caching addresses repeated context: audit your production system prompts and identify any prefix content that is stable across requests — instructions, policies, reference data, schema definitions — and ensure that content appears at the very start of the prompt to maximize cache hit rates. Output token discipline matters more than most teams realize: unnecessarily verbose completions are expensive at $6.00 per million on Grok 4.20; explicit `max_tokens` limits and prompt instructions to be concise on structured-output tasks (JSON extraction, classification labels, short summaries) can cut output spend by 20–40% with no quality loss. For batch workloads — document processing, data enrichment, nightly analysis jobs — use the largest feasible batch size to minimize API call overhead and maximize cache utilization across similar requests. Finally, monitor your token usage at the prompt component level (system prompt vs. user message vs. retrieved context) to identify which parts of your prompt are growing over time; unbounded context accumulation in multi-turn agents is one of the fastest ways to watch your Grok 4.20 bill climb unexpectedly.

**Model routing decision framework:**

| Task Type | Recommended Model | Rationale |
|---|---|---|
| Classification, tagging | Grok 4.1 Fast | Simple pattern match; $0.20 input is optimal |
| Summarization (< 50K tokens) | Grok 4.1 Fast | Compression task; fast model sufficient |
| Long-doc analysis (> 200K tokens) | Grok 4.20 | Requires large context + quality |
| Complex reasoning, research | Grok 4.20 | Full capability needed |
| Inline code completion | Grok Code Fast 1 | Coding-optimized; $0.20 input |
| Code review, architecture | Grok Code Fast 1 or 4.20 | Depends on codebase size |
| Search-augmented Q&A | Any Grok model | Built-in web search, no extra cost |

A blended model routing strategy with 70% Grok 4.1 Fast and 30% Grok 4.20 (assuming a 2:1 input-to-output ratio) reduces effective blended input cost to $0.74/M and output cost to $2.15/M — a 63% reduction vs. using Grok 4.20 for all requests, and 85% cheaper than a GPT-5.5 equivalent deployment.

---

## Frequently Asked Questions

**1. Can I use my existing OpenAI SDK code with the Grok API without rewriting it?**

Yes. The xAI API is fully OpenAI-compatible. You only need to change two things: set `base_url="https://api.x.ai/v1"` and replace your OpenAI API key with your xAI API key. Model name strings change (`grok-4-20` instead of `gpt-4o`, for example), but all request/response structures, streaming behavior, and tool-calling conventions follow the OpenAI API spec.

**2. Is real-time web search included in the standard per-token pricing, or is it an additional charge?**

Real-time web search is a built-in model capability on all three Grok models and does not carry a separate per-search fee beyond the token cost of the search results returned in the response. When search results are included in the model's context, they count toward your output token billing at the standard rate for that model.

**3. Which Grok model should I use for a coding assistant with a large repository context?**

Grok Code Fast 1 is the designed-for-purpose choice for most coding assistant workloads, offering a 256K context window at $0.20/$1.50 per million tokens. For tasks requiring analysis of extremely large codebases (over 256K tokens) — full monorepo architecture reviews or cross-repository impact analysis — Grok 4.20's 2M context window is the correct tool, at the higher $2.00/$6.00 price point.

**4. Does prompt caching work automatically, or does it require specific API parameters?**

Prompt caching on xAI's API is prefix-based: the API automatically reuses cached KV-state when a new request's prompt begins with a prefix that matches a recently processed request. To maximize cache hits, structure your prompts with stable, repeated content (system instructions, document context, schemas) at the top and dynamic content (user messages, query variables) at the end. No special API flag is required to enable caching — it activates automatically when the cache key matches.

**5. How does Grok 4.20 compare to Claude Opus 4.7 for tasks that need both long context and strong reasoning?**

Grok 4.20 is 7.5× cheaper on input ($2.00 vs. $15.00) and 12.5× cheaper on output ($6.00 vs. $75.00), while supporting a 10× larger context window (2M vs. 200K tokens). For tasks that require both long context and reasoning — large codebase analysis, full-document contract review, multi-source research synthesis — Grok 4.20 is the only model in its price tier that can handle them without chunking. Claude Opus 4.7 remains the benchmark for subtle instruction-following and nuanced creative reasoning on shorter contexts; for long-context reasoning at scale, Grok 4.20's cost and context advantages are decisive.
