---
title: "Perplexity Sonar API Guide 2026: Add Real-Time Search to Your App"
date: 2026-05-07T00:04:02+00:00
tags: ["Perplexity", "API", "real-time search", "AI development", "Python"]
description: "Step-by-step guide to integrating the Perplexity Sonar API for web-grounded AI responses with citations, streaming, and domain filtering."
draft: false
cover:
  image: "/images/perplexity-sonar-api-guide-2026.png"
  alt: "Perplexity Sonar API Guide 2026: Add Real-Time Search to Your App"
  relative: false
schema: "schema-perplexity-sonar-api-guide-2026"
---

The Perplexity Sonar API lets you add live web search and inline citations to any app using a single OpenAI-compatible endpoint. You get grounded, up-to-date answers with source links — no separate search API, no custom scraping pipeline — starting at $1 per million tokens.

## What Is the Perplexity Sonar API?

The Perplexity Sonar API is a search-first AI inference service that automatically retrieves live web results before generating each response, embedding citations directly into the output. Unlike OpenAI or Anthropic models that ground answers in training data, Sonar queries the live web on every request — making it purpose-built for applications that need current information, not just general reasoning. Pricing starts at $1 per million tokens (input and output combined) for the standard Sonar model, with no extra per-query search fee bundled on top. In a 2026 production benchmark, Sonar delivered inline citations on 94% of test queries with latency consistently under 2 seconds. The API endpoint is fully OpenAI-compatible, meaning any application already calling GPT-4 or Claude can switch to Sonar by changing the base URL and model name — no SDK migration required. This drop-in compatibility, combined with a search-first architecture, is what separates Sonar from general-purpose models with optional grounding add-ons.

### How Does Search-First Architecture Differ from Model-First Grounding?

Search-first architecture retrieves web content before the model generates a token. Model-first grounding (like OpenAI's web search tool or Google Gemini's grounding feature) calls a search tool as an optional step during generation, which can be slower and less tightly coupled to the final answer. Sonar bakes retrieval into every call by default — you don't enable or configure a grounding plugin; it's simply how the model works. This distinction matters for latency, citation density, and cost predictability.

## Sonar vs Sonar Pro vs Sonar Reasoning: Choosing the Right Model

Sonar, Sonar Pro, and Sonar Reasoning are three distinct tiers of the Perplexity API, each targeting a different balance of cost, context window, and reasoning depth. The standard Sonar model handles most production workloads: conversational search, Q&A, summarization, and real-time fact lookup at $1/million tokens with no citation-token billing (citation tokens were removed from billing in 2026 for Sonar and Sonar Pro). Sonar Pro steps up to a 200K context window, 2–3x more source citations per response, and $3/million input tokens + $15/million output tokens — worth it for document-length research tasks or complex multi-turn queries where source density matters. Sonar-Reasoning-Pro adds multi-step chain-of-thought reasoning on top of live search, scoring 1,136 on the Search Arena evaluation (statistically tied with Gemini-2.5-Pro-Grounding at 1,142), which is the highest position for any developer API at the time of writing. Sonar Pro Search (agentic mode) adds $14–$22 per 1,000 requests for autonomous multi-step search orchestration — useful for research agents but overkill for standard chat interfaces.

| Model | Context | Price (Input/Output) | Best For |
|---|---|---|---|
| sonar | 32K | $1M / $1M | Chat, Q&A, real-time lookup |
| sonar-pro | 200K | $3M / $15M | Long docs, dense citations |
| sonar-reasoning | 32K | $1M / $5M | Multi-step reasoning + search |
| sonar-reasoning-pro | 200K | $2M / $8M | Complex research tasks |

## Getting Started: Generate Your API Key and Install the SDK

Setting up the Perplexity Sonar API takes under five minutes. Go to `https://www.perplexity.ai/settings/api`, create an account or sign in, and generate an API key from the API Keys panel. Perplexity provides $5 in free credits to new accounts, enough to run several thousand Sonar calls. The API is OpenAI-compatible, so you can use the official `openai` Python or JavaScript package by pointing it at Perplexity's base URL — no separate SDK installation is required. For Python, install via `pip install openai`. For JavaScript, use `npm install openai`. Alternatively, any HTTP client works because the endpoint is a standard REST API. Store your key as an environment variable (`PERPLEXITY_API_KEY`) rather than hardcoding it. Your application's environment configuration handles the rest — you only need to set `base_url="https://api.perplexity.ai"` and `api_key=os.environ["PERPLEXITY_API_KEY"]` when instantiating the client.

```bash
pip install openai
export PERPLEXITY_API_KEY="your-key-here"
```

## Your First Sonar API Call in Python and JavaScript

Making your first Perplexity Sonar API call requires fewer than 20 lines of code, and the response includes both the generated answer and an array of citation URLs in the same JSON object. The API follows the OpenAI chat completions format exactly: you send a `messages` array with `role` and `content` fields, specify a Sonar model, and receive a `choices` array back. The key difference from standard OpenAI responses is the `citations` field at the top level of the response object — an ordered list of URLs that the model referenced when generating the answer. Below are complete working examples for Python and JavaScript that you can run against your live key immediately.

**Python:**

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["PERPLEXITY_API_KEY"],
    base_url="https://api.perplexity.ai",
)

response = client.chat.completions.create(
    model="sonar",
    messages=[
        {"role": "system", "content": "Be precise and cite sources."},
        {"role": "user", "content": "What are the latest AI agent frameworks in 2026?"},
    ],
)

print(response.choices[0].message.content)
print("\nCitations:")
for url in response.citations:
    print(f"  - {url}")
```

**JavaScript (fetch):**

```javascript
const response = await fetch("https://api.perplexity.ai/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.PERPLEXITY_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "sonar",
    messages: [
      { role: "system", content: "Be precise and cite sources." },
      { role: "user", content: "What are the latest AI agent frameworks in 2026?" },
    ],
  }),
});

const data = await response.json();
console.log(data.choices[0].message.content);
console.log("Citations:", data.citations);
```

The response arrives in under 2 seconds for most queries. Citations are returned as a flat array of URLs, numbered to match `[1]`, `[2]` markers in the generated text.

## Streaming Responses for Real-Time User Experience

Sonar supports server-sent event (SSE) streaming, allowing you to render answers token-by-token as they arrive — critical for chat interfaces where users expect instant visual feedback. Streaming a Sonar response requires setting `stream=True` (Python) or `stream: true` (JavaScript) in the request. The response then emits a series of `data:` events, each containing a JSON delta. Citations arrive in the final chunk's `citations` field rather than with each token, so you need to accumulate the stream and extract citations at the end. The pattern is identical to OpenAI's streaming API — any existing streaming implementation transfers without modification.

```python
stream = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "Latest React 20 features?"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)

# Citations are on the last chunk
print("\nCitations:", chunk.citations if hasattr(chunk, "citations") else [])
```

For production UIs, render citation links below the streamed answer once the stream closes. Avoid injecting citation markup mid-stream — it produces broken UI states before the citation list is complete.

## Working with Citations: Displaying Trusted Sources in Your App

Sonar's citation system returns an ordered list of source URLs that map to numeric markers (`[1]`, `[2]`, etc.) embedded in the generated text. Processing citations correctly is what separates a trustworthy AI-powered feature from one that users rightfully distrust. In 2026, citation tokens are no longer billed separately for Sonar and Sonar Pro — only Deep Research incurs citation token costs — so richer citation handling is now essentially free. The standard approach is to parse the response text for bracketed numbers, look up the corresponding URL in the `citations` array, and render each as a hyperlink or footnote. Sonar Pro returns 2–3x more citations per response than equivalent Gemini models, which matters for research tools where source density directly correlates with user trust. Production testing shows Sonar models deliver inline citations on 94% of queries, making the citation array reliable enough to surface in the UI without a fallback check.

```python
import re

def format_with_citations(text: str, citations: list[str]) -> str:
    def replace_citation(match):
        idx = int(match.group(1)) - 1
        if idx < len(citations):
            return f"[{match.group(1)}]({citations[idx]})"
        return match.group(0)
    return re.sub(r'\[(\d+)\]', replace_citation, text)

formatted = format_with_citations(
    response.choices[0].message.content,
    response.citations
)
```

## Domain Filtering: Restricting Search Results to Trusted Sources

The `search_domain_filter` parameter lets you restrict Sonar's web retrieval to specific domains or URLs, functioning as an allowlist or denylist for grounding sources. This is one of Sonar's most differentiating production features — no other major grounded API offers per-request source control at this granularity. The filter accepts up to 20 domains or URLs per request, and you can prefix entries with `-` to exclude a domain rather than require it. For enterprise applications handling regulated content (healthcare, legal, finance), domain filtering becomes a compliance tool: you can guarantee that AI answers are grounded exclusively in your vetted documentation, government sources, or internal knowledge bases — not random web pages. Copy.ai used a similar source control strategy and reported 8 hours of research saved per sales rep per week and a 20% throughput increase after integrating Sonar with constrained sourcing.

```python
response = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Current FDA drug approval guidelines?"}],
    extra_body={
        "search_domain_filter": [
            "fda.gov",
            "nih.gov",
            "-reddit.com",       # exclude social media
            "-wikipedia.org",    # exclude user-edited content
        ],
        "search_recency_filter": "month",
    },
)
```

### What Is search_recency_filter?

`search_recency_filter` limits retrieved web content to pages published within a given timeframe: `"hour"`, `"day"`, `"week"`, or `"month"`. Use it for news aggregators, market monitors, or any feature where stale results would be worse than no results. Combine with `search_domain_filter` for maximum precision — for example, restricting to financial news domains from the past 24 hours gives you a tight, trusted source pool for a trading assistant.

## Perplexity Sonar API Pricing Breakdown 2026

Perplexity Sonar API pricing in 2026 is token-based with no separate per-search fee for the standard and Pro tiers, making cost modeling straightforward compared to competitors that charge per search call. The standard Sonar model bills $1 per million tokens for both input and output — identical rates on both sides, which simplifies budget forecasting. Sonar Pro charges $3/million input tokens and $15/million output tokens, reflecting its larger context window and denser citations. A key 2026 change: citation tokens are no longer billed for Sonar or Sonar Pro (only Deep Research). In a real-world comparison, a 500-query-per-day customer support chatbot cost approximately $120/month on Sonar versus approximately $280/month on GPT-4 combined with Google Custom Search — a 57% cost reduction. OpenAI's search tool costs an estimated $20–$25 per 1,000 search-grounded requests; Perplexity Sonar runs $5–$14 for the equivalent workload.

| Model | Input | Output | Per-Request Fee |
|---|---|---|---|
| sonar | $1/M | $1/M | None |
| sonar-pro | $3/M | $15/M | None |
| sonar-reasoning-pro | $2/M | $8/M | None |
| sonar-pro-search (agentic) | $3/M | $15/M | +$14–22/1K requests |
| sonar-deep-research | $2/M | $8/M | +citation tokens |

## Real-World Use Cases and Performance Benchmarks

Sonar excels in four production patterns: customer support chatbots that need current product or policy information, research assistants that must cite primary sources, competitive intelligence tools that monitor live market data, and internal knowledge assistants scoped to company documentation via domain filtering. Sonar-Reasoning-Pro scored 1,136 in the Search Arena evaluation — statistically tied with Gemini-2.5-Pro-Grounding (1,142) at the top of the leaderboard, outperforming all other developer APIs at the time of writing. In independent production testing, Sonar models delivered inline citations on 94% of test queries with latency under 2 seconds, and using Sonar reduced hallucination rate by approximately 60% compared to non-grounded LLMs in the same application. Zoom's AI Companion 2.0 and Copy.ai are among the enterprise case studies Perplexity has published — Copy.ai specifically measured 8 hours saved per sales rep per week and a 20% increase in workflow throughput after integrating Sonar for competitive research tasks.

### Customer Support: A Practical Example

A support chatbot using Sonar can answer questions about current pricing, feature availability, and policy changes without manual knowledge-base updates. With `search_domain_filter` pointed at your docs site and `search_recency_filter` set to `"month"`, the model retrieves only your own up-to-date pages. The 60% reduction in hallucination rate translates directly to fewer escalations and less agent correction overhead.

## Sonar API vs OpenAI Search vs Google Gemini Grounding: Which Should You Use?

Perplexity Sonar, OpenAI's web search tool, and Google Gemini Grounding are the three primary options for adding real-time search to AI applications, and they differ significantly on cost, citation density, and developer control. Sonar is purpose-built for search-first applications: every call retrieves live web content by default, citations are always present, and domain filtering gives per-request source control. OpenAI's search tool is opt-in per message, costs an estimated $20–$25 per 1,000 grounded requests (vs. Sonar's $5–$14), and offers no per-request domain filtering. Google Gemini Grounding is tightly integrated with Google Search and works well within GCP-native stacks, but its per-request pricing is comparable to OpenAI's and it lacks Sonar-equivalent citation density (Sonar Pro returns 2–3x more citations per response). For greenfield applications where live search is a core feature — not an edge case — Sonar is the most cost-efficient and citation-dense option. For applications already using OpenAI or Gemini where occasional web access is needed, the respective platform tools may require less migration effort.

| Feature | Sonar | OpenAI Search | Gemini Grounding |
|---|---|---|---|
| Search on every call | Yes (default) | Optional per message | Optional per message |
| Domain filtering | Yes (up to 20) | No | Partial (allow only) |
| Citation density | High (94% coverage) | Medium | Medium |
| Cost per 1K requests | $5–$14 | $20–$25 | $18–$24 |
| OpenAI-compatible | Yes | Yes | No |
| Max context | 200K (Pro) | 128K | 1M |

## Production Best Practices: Rate Limits, Error Handling, and Caching

Deploying Sonar to production requires handling rate limits, transient errors, and response caching to avoid redundant spend. Perplexity enforces per-minute and per-day rate limits that scale with your plan tier; the free tier is restrictive, while paid plans offer substantially higher throughput. The API returns standard HTTP status codes: `429` for rate limit exceeded, `500`/`503` for transient server errors. Implement exponential backoff for `429` and `5xx` responses — a base delay of 1 second doubling up to 30 seconds covers the vast majority of transient failures. For caching, identical or semantically similar queries can hit a local cache (Redis or in-memory) before reaching the API, cutting costs significantly for high-traffic applications. Cache TTL should reflect your recency requirements: a news monitor might cache for 15 minutes, while a documentation assistant can cache for 24 hours. Because Sonar answers are web-grounded, excessively long cache TTLs risk serving stale answers — treat TTL as a business logic decision, not a technical one.

```python
import time
import openai

def sonar_with_retry(client, messages, model="sonar", max_retries=3):
    delay = 1
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(model=model, messages=messages)
        except openai.RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 30)
        except openai.APIStatusError as e:
            if e.status_code >= 500 and attempt < max_retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 30)
            else:
                raise
```

### What Rate Limits Should You Plan For?

Perplexity does not publish exact rate limit numbers publicly — they vary by plan and usage history. In practice, plan for 60 requests/minute on paid tiers as a conservative starting point and implement the retry pattern above regardless. If your application needs higher throughput, contact Perplexity's API team for an enterprise rate limit increase. Monitor your `X-RateLimit-Remaining` response headers to track headroom in real time.

---

## FAQ

**Q: Is the Perplexity Sonar API compatible with the OpenAI SDK?**

Yes. The Sonar API uses the same chat completions format as OpenAI. Set `base_url="https://api.perplexity.ai"` and your Perplexity API key when instantiating the OpenAI client, then use any Sonar model name. The only addition is the `citations` field in the response, which you can optionally handle.

**Q: How much does it cost to run a customer support bot on Sonar?**

A 500-query-per-day chatbot on the standard Sonar model costs approximately $120/month — compared to $280/month for the equivalent GPT-4 plus Google Custom Search setup. Exact costs depend on average message length. Use Sonar's $1/million token rate as your baseline and calculate from your average input+output token count per conversation turn.

**Q: Can I restrict Sonar to only search my own website?**

Yes. Use `search_domain_filter` with your domain (e.g., `["docs.yourcompany.com"]`) to restrict retrieval to your own pages. Combine with `search_recency_filter` to limit results to recently updated content. This turns Sonar into a grounded documentation assistant without manual RAG pipeline setup.

**Q: What is the difference between Sonar Pro and Sonar Reasoning Pro?**

Sonar Pro increases citation density (2–3x more sources) and context window (200K tokens) at $3/M input + $15/M output. Sonar Reasoning Pro adds multi-step chain-of-thought reasoning on top of the Pro search capability — useful for complex research tasks that require synthesizing multiple sources before reaching a conclusion. Use Reasoning Pro when intermediate reasoning steps, not just final answers, matter for your application.

**Q: Does streaming work with citation extraction?**

Yes, but citations arrive in the final chunk, not with individual tokens. Accumulate the stream as normal, then extract `citations` from the last chunk after the stream closes. Render the answer as it streams, then inject citation links into the UI once the stream is complete.
