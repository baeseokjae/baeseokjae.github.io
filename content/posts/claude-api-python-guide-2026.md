---
cover:
  alt: 'How to Use Claude API in Python 2026: Complete Developer Guide'
  image: /images/claude-api-python-guide-2026.png
  relative: false
date: 2026-04-18 08:46:52+00:00
description: 'Step-by-step Claude API Python tutorial: install the SDK, send messages,
  use streaming, tool use, and prompt caching with real code examples.'
draft: false
schema: schema-claude-api-python-guide-2026
tags:
- Claude API
- Python
- Anthropic SDK
- AI development
- LLM
title: 'How to Use Claude API in Python 2026: Complete Developer Guide'
---

The Claude API lets you integrate Anthropic's Claude models into any Python application in under 10 lines of code. Install the `anthropic` package, set your API key, and call `client.messages.create()` — that's the entire setup. This guide covers everything from basic text generation to advanced features like streaming, tool use, vision, and prompt caching that can cut your costs by up to 90%.

## What Is the Claude API and Why Use It in 2026?

The Claude API is Anthropic's REST interface for accessing Claude models — including Claude Opus 4.7, Claude Sonnet 4.6, and Claude Haiku 4.5 — programmatically. Unlike ChatGPT's API, Claude's API is built with safety-first architecture, a 200K-token context window (one of the largest available), and native tool-use support that lets agents take real actions. As of 2026, the Claude API powers production workloads at companies like Salesforce, Notion, and Slack, processing billions of tokens daily. The Python SDK (`anthropic`) wraps the REST API with type-safe client objects, automatic retries, and streaming support. Developers choose Claude over alternatives for three reasons: superior instruction following on long documents, better refusal calibration (fewer false positives), and prompt caching that makes repeated context tokens 90% cheaper. The API follows the Messages format — a list of role/content pairs — which maps cleanly to Python dicts and requires no special framework.

## How to Install the Anthropic Python SDK

Installing the Anthropic Python SDK takes one command and works with Python 3.8 and above. Run `pip install anthropic` to get the latest stable release. As of April 2026, the current SDK version is 0.51.x, which includes native support for Claude Opus 4.7, Claude Sonnet 4.6, and Claude Haiku 4.5 — Anthropic's full 2026 model lineup. The SDK ships with built-in prompt caching helpers, async streaming via `AsyncAnthropic`, and typed response objects that eliminate guessing about response structure. For production projects, always pin the version in your `requirements.txt` — breaking changes between major versions are documented in the official changelog, and unpinned installs have caused production outages when Anthropic ships major SDK updates. The SDK has zero mandatory runtime dependencies beyond `httpx` and `pydantic`, keeping your container images lean. Virtual environments (via `venv` or `conda`) are strongly recommended to avoid conflicts with other packages. If you need async support — which most production apps do for FastAPI, Starlette, or asyncio-based services — `AsyncAnthropic` is included out of the box with no extra install step.

```bash
pip install anthropic

# For async support (already included, no extras needed)
pip install anthropic

# Pin for production
echo "anthropic==0.51.0" >> requirements.txt
```

### Setting Up Your API Key

Get your API key from [console.anthropic.com](https://console.anthropic.com) and store it as an environment variable — never hardcode it in source files.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

The SDK automatically reads `ANTHROPIC_API_KEY` from the environment. You can also pass it explicitly: `Anthropic(api_key="sk-ant-...")`.

## How to Send Your First Message to Claude

Sending your first message to Claude requires three objects: an `Anthropic` client, a model name, and a messages list. The response comes back as a `Message` object with a `content` list — each item is a `TextBlock` with a `.text` attribute. The pattern mirrors OpenAI's Chat Completions API but adds Anthropic-specific fields like `stop_reason` and `usage.cache_read_input_tokens`. In 2026, Claude Sonnet 4.6 (`claude-sonnet-4-6`) is the recommended default for most production workloads: it's approximately 3x faster than Opus at one-fifth the cost, while matching Opus on the majority of coding and instruction-following tasks. Use Haiku 4.5 for latency-sensitive tasks like autocomplete or real-time suggestions (under 300ms p95), and Opus 4.7 for complex, multi-step reasoning tasks like autonomous agents or long-document analysis. The `max_tokens` parameter sets the upper bound on output length — Claude will stop sooner if it naturally finishes. Always set it to a reasonable value; leaving it too high doesn't cost extra but can cause issues if downstream code assumes a short response.

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain dependency injection in Python with a concrete example."}
    ]
)

print(message.content[0].text)
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
```

### Understanding the Response Object

The `Message` object contains everything you need to build robust applications:

```python
# Full response structure
message.id          # "msg_01XFDUDYJgAACzvnptvVoYEL"
message.type        # "message"
message.role        # "assistant"
message.content     # [TextBlock(text="...", type="text")]
message.model       # "claude-sonnet-4-6"
message.stop_reason # "end_turn" | "max_tokens" | "tool_use" | "stop_sequence"
message.usage.input_tokens   # 25
message.usage.output_tokens  # 315
```

## How to Use Streaming with the Claude API

Streaming is how you build responsive Claude-powered UIs — instead of waiting seconds for the full response, tokens arrive as they're generated. The Python SDK provides two streaming interfaces: `client.messages.stream()` for high-level event handling, and `client.messages.create(stream=True)` for raw SSE access. In 2026, streaming is the default approach for any user-facing application because it drops perceived latency by 80% — users see text appearing in under 200ms instead of waiting 3-5 seconds for a complete response. The streaming context manager handles connection cleanup automatically, so you don't need try/finally blocks.

```python
import anthropic

client = anthropic.Anthropic()

# High-level streaming (recommended)
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a Python function to parse JSON safely."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Get the final message after streaming completes
final_message = stream.get_final_message()
print(f"\nTotal tokens: {final_message.usage.output_tokens}")
```

### Async Streaming for FastAPI and Async Frameworks

For FastAPI, asyncio, or any async Python application, use `AsyncAnthropic`:

```python
import asyncio
import anthropic

async def stream_response(prompt: str):
    client = anthropic.AsyncAnthropic()
    
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        async for text in stream.text_stream:
            yield text

# FastAPI example
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
async def chat(prompt: str):
    return StreamingResponse(
        stream_response(prompt),
        media_type="text/plain"
    )
```

## How to Use System Prompts and Multi-Turn Conversations

System prompts define Claude's role, constraints, and behavior for your entire session. They sit outside the `messages` array at the top level of the API call, and Claude treats them as authoritative instructions that override user requests when they conflict. A well-crafted system prompt is the single highest-leverage tool for steering model behavior — it's where you define persona, output format, safety constraints, and domain knowledge. Multi-turn conversations work by appending each user message and assistant response to the messages list, giving Claude full conversation history. In 2026, most production apps store conversation history in Redis or a database and reconstruct the messages array on each request rather than keeping it in memory.

```python
import anthropic

client = anthropic.Anthropic()

def chat_with_memory():
    conversation_history = []
    
    system_prompt = """You are a senior Python engineer with 10 years of experience.
    You give concise, production-ready code examples.
    Always mention edge cases and potential issues."""
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        print(f"Claude: {assistant_message}\n")

chat_with_memory()
```

## How to Use Tool Use (Function Calling) with Claude API

Tool use — also called function calling — lets Claude invoke external functions, APIs, and databases to answer questions it couldn't handle from training data alone. You define tools as JSON schemas describing their name, description, and input parameters. Claude decides when to call a tool, extracts the arguments, and returns a `tool_use` block. Your code executes the function and returns the result back to Claude, which then generates a final response. This tool-use loop is the foundation of every AI agent built on Claude in 2026. The key insight: Claude's tool selection is driven by the description field — write descriptions like you're writing a docstring for a human engineer who needs to decide which function to call.

```python
import anthropic
import json

client = anthropic.Anthropic()

# Define tools as JSON schemas
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city. Returns temperature in Celsius, conditions, and humidity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (e.g., 'San Francisco', 'Tokyo')"
                },
                "country_code": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'JP')"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "search_database",
        "description": "Search a product database by keyword. Returns list of matching products with prices.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_weather":
        # In production, call a real weather API
        return json.dumps({
            "city": tool_input["city"],
            "temperature": 22,
            "conditions": "Partly cloudy",
            "humidity": 65
        })
    elif tool_name == "search_database":
        return json.dumps([
            {"name": "Product A", "price": 29.99},
            {"name": "Product B", "price": 49.99}
        ])
    return json.dumps({"error": "Unknown tool"})

def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            # No tool call — return final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
        
        if response.stop_reason == "tool_use":
            # Add assistant's response with tool_use blocks
            messages.append({"role": "assistant", "content": response.content})
            
            # Execute all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Return tool results to Claude
            messages.append({"role": "user", "content": tool_results})

result = run_agent("What's the weather like in Tokyo?")
print(result)
```

## How to Use Vision (Image Analysis) with Claude API

Claude's vision capability lets you send images alongside text and get detailed analysis, code extraction, chart interpretation, or OCR results. You can pass images as base64-encoded data or as URLs. In production, base64 encoding is more reliable — URLs require Claude's servers to fetch the image, which adds latency and can fail on private resources. Claude supports JPEG, PNG, GIF, and WebP. The vision capability is particularly powerful for developer use cases: extract code from screenshots, analyze error logs from terminal screenshots, or process UI mockups for spec generation. Claude Sonnet 4.6 processes images in under 2 seconds for most use cases, making it practical for interactive applications.

```python
import anthropic
import base64
from pathlib import Path

client = anthropic.Anthropic()

def analyze_image_file(image_path: str, question: str) -> str:
    image_data = Path(image_path).read_bytes()
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")
    
    # Detect media type from extension
    ext = Path(image_path).suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp"
    }
    media_type = media_type_map.get(ext, "image/jpeg")
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image,
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    )
    
    return message.content[0].text

# Example: analyze a screenshot
result = analyze_image_file(
    "error_screenshot.png",
    "What Python error is shown in this screenshot? How do I fix it?"
)
print(result)
```

## How to Implement Prompt Caching for Cost Reduction

Prompt caching is the single biggest cost-reduction lever for Claude API users in 2026. When you mark content blocks with `"cache_control": {"type": "ephemeral"}`, Anthropic caches those tokens on their servers for 5 minutes. Subsequent requests that hit the cache pay 90% less for those tokens — from $3/MTok to $0.30/MTok for Sonnet. The pattern works best for system prompts, large document corpora, and conversation histories that stay stable across requests. A typical RAG application that injects 50K tokens of context into every request saves ~$270 per million requests with caching enabled. The `usage.cache_read_input_tokens` field tells you exactly how many tokens were served from cache vs. recomputed.

```python
import anthropic

client = anthropic.Anthropic()

# Large system prompt that stays constant across requests
SYSTEM_PROMPT = """You are an expert Python code reviewer with deep knowledge of:
- PEP 8 style guidelines and modern Python idioms
- Security vulnerabilities (OWASP Top 10, injection attacks, secrets exposure)
- Performance optimization (profiling, algorithmic complexity, memory usage)
- Testing best practices (pytest, fixtures, mocking, coverage)

[... 10,000 more words of domain knowledge ...]"""

def review_code_with_caching(code: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}  # Cache this large prompt
            }
        ],
        messages=[
            {"role": "user", "content": f"Review this code:\n\n```python\n{code}\n```"}
        ]
    )
    
    # Log cache performance
    usage = response.usage
    cached = getattr(usage, 'cache_read_input_tokens', 0)
    created = getattr(usage, 'cache_creation_input_tokens', 0)
    print(f"Cache hit: {cached} tokens | Cache miss: {created} tokens")
    
    return response.content[0].text

# First call: creates cache (pays full price)
review1 = review_code_with_caching("def add(a, b): return a + b")

# Second call within 5 minutes: reads from cache (90% cheaper)
review2 = review_code_with_caching("def multiply(a, b): return a * b")
```

## How to Handle Errors and Rate Limits in Production

Production Claude API integrations must handle four error classes: authentication errors (401), rate limit errors (429), server errors (500/529), and invalid request errors (400). The SDK raises typed exceptions for each: `AuthenticationError`, `RateLimitError`, `APIStatusError`, and `BadRequestError`. For rate limits, implement exponential backoff with jitter — the SDK's `max_retries` parameter handles this automatically, but you need custom logic for quota exhaustion (as opposed to burst rate limits). In 2026, Anthropic's rate limits are per-tier: Tier 1 starts at 50,000 tokens/minute, scaling to 4,000,000 tokens/minute at Tier 4. Monitor your `x-ratelimit-remaining-tokens` response header to implement proactive throttling before hitting limits.

```python
import anthropic
import time
import random
from typing import Optional

client = anthropic.Anthropic(
    max_retries=3,  # SDK handles transient errors automatically
    timeout=60.0
)

def robust_api_call(
    messages: list,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 1024,
    max_attempts: int = 5
) -> Optional[str]:
    for attempt in range(max_attempts):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )
            return response.content[0].text
            
        except anthropic.RateLimitError as e:
            if attempt == max_attempts - 1:
                raise
            # Exponential backoff with jitter
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Waiting {wait:.1f}s... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(wait)
            
        except anthropic.APIStatusError as e:
            if e.status_code == 529:  # Overloaded
                wait = 10 + random.uniform(0, 5)
                print(f"API overloaded. Waiting {wait:.1f}s...")
                time.sleep(wait)
            elif e.status_code >= 500:
                raise  # Server errors after SDK retries
            else:
                raise  # 4xx errors are not retriable
                
        except anthropic.AuthenticationError:
            raise  # Never retry auth errors
    
    return None
```

## How to Build a Complete RAG Pipeline with Claude API

A Retrieval-Augmented Generation (RAG) pipeline with Claude works by injecting relevant document chunks into the prompt at query time. The Claude API's 200K context window means you can inject far more context than GPT-4 alternatives — up to ~150,000 words — without chunking. A production RAG pipeline has four stages: document ingestion (chunk + embed), retrieval (vector similarity search), prompt construction (inject chunks + user query), and generation (Claude API call). In 2026, the most common stack is Claude + pgvector (PostgreSQL) for teams that already run Postgres, or Claude + Pinecone for teams that need managed vector search. The key performance metric is retrieval precision: Claude can work with 20+ retrieved chunks, so cast a wide retrieval net rather than aggressively filtering.

```python
import anthropic
from typing import List

client = anthropic.Anthropic()

def build_rag_prompt(query: str, retrieved_chunks: List[str]) -> str:
    context = "\n\n---\n\n".join(
        f"[Document {i+1}]\n{chunk}" 
        for i, chunk in enumerate(retrieved_chunks)
    )
    return f"""Answer the question based on the provided documents.
If the answer isn't in the documents, say so clearly.

DOCUMENTS:
{context}

QUESTION: {query}"""

def rag_query(query: str, vector_db_results: List[str]) -> str:
    prompt = build_rag_prompt(query, vector_db_results)
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are a precise research assistant. Cite document numbers when referencing sources.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

# Example usage
chunks = [
    "Claude Sonnet 4.6 was released in Q1 2026 with improved reasoning...",
    "The Claude API pricing is $3 per million input tokens for Sonnet...",
    "Prompt caching reduces costs by 90% for cached token reads..."
]

answer = rag_query("How much does Claude API cost?", chunks)
print(answer)
```

## Claude API vs OpenAI API: Key Differences for Python Developers

Choosing between Claude API and OpenAI API in Python comes down to three factors: context window size, cost structure, and ecosystem maturity. Claude offers a 200K-token context window versus GPT-4o's 128K, making it the clear choice for long-document workflows, large codebase analysis, and extended conversations. On cost, Claude Sonnet 4.6 at $3/MTok input is competitive with GPT-4o at $2.50/MTok, but Claude's prompt caching (90% discount on cached tokens) means real-world costs for cache-friendly workloads are dramatically lower. OpenAI has a larger third-party ecosystem — more tutorials, more LangChain examples, more community plugins — but the Claude SDK is syntactically similar enough that migration takes hours, not days. The table below shows the exact API surface differences Python developers encounter when switching.

| Feature | Claude API | OpenAI API |
|---|---|---|
| Context window | 200K tokens | 128K tokens (GPT-4o) |
| Streaming | `client.messages.stream()` | `client.chat.completions.create(stream=True)` |
| Tool use | `tools` parameter | `tools` / `functions` parameter |
| System prompt | Top-level `system` param | First message with `role: "system"` |
| Prompt caching | Native, 90% discount | No native caching |
| Image input | `image` content block | Same pattern |
| Python SDK | `anthropic` | `openai` |
| Rate limits | Token-based per minute | Request + token-based |

The migration from OpenAI to Claude API requires three changes: swap the client class, rename `chat.completions.create` to `messages.create`, and move the system message from the messages array to the top-level `system` parameter. Most production migrations take under 2 hours for a simple application.

## FAQ

The most common questions developers have about the Claude API in Python center on cost, rate limits, and framework compatibility. Below are answers to the five questions that come up in every developer forum thread and Stack Overflow post about Claude API Python integration. These answers reflect the current state of the API as of April 2026 — check the Anthropic documentation for the latest rate limits and pricing tiers since both change as Anthropic scales. If you're migrating from another LLM provider or just getting started, these answers will save you the 2-3 hours of trial and error that most developers go through when first integrating Claude into a Python project. All code examples in the answers below work with `anthropic` SDK version 0.51.x or newer and have been tested against the production Claude API endpoints.

### How much does the Claude API cost in Python?

Claude API pricing as of 2026: Haiku 4.5 costs $0.80/MTok input and $4/MTok output. Sonnet 4.6 costs $3/MTok input and $15/MTok output. Opus 4.7 costs $15/MTok input and $75/MTok output. With prompt caching enabled, cached input tokens cost 90% less. A typical chatbot processing 1M tokens/month costs roughly $3-15 depending on model choice.

### Is there a free tier for the Claude API?

Anthropic offers new accounts $5 in free API credits to test the API. Beyond that, it's pay-as-you-go with no free tier. For prototyping on a budget, use Claude Haiku 4.5 — it's 75% cheaper than Sonnet while handling most straightforward tasks well.

### How do I handle Claude API timeouts in Python?

Set `timeout=60.0` on the `Anthropic()` client for a 60-second total timeout. For streaming requests that may run long, pass `timeout=httpx.Timeout(60.0, read=300.0)` to allow a longer read timeout while keeping the connection timeout short. The SDK raises `anthropic.APITimeoutError` on timeout, which you should catch and retry.

### Can I use the Claude API with LangChain or LlamaIndex?

Yes. Both LangChain and LlamaIndex have native Claude integrations. LangChain uses `ChatAnthropic` from `langchain_anthropic`. LlamaIndex uses `Anthropic` from `llama_index.llms.anthropic`. Both support streaming and tool use. However, using the raw `anthropic` SDK directly gives you access to features like prompt caching that framework wrappers sometimes lag in supporting.

### What is the maximum context window for Claude API in Python?

Claude's maximum context window is 200,000 tokens (~150,000 words). This covers a full codebase, a legal document, or many hours of transcript. The `max_tokens` parameter controls the *output* size — set it based on expected response length, not the input size. You pay for input tokens regardless of `max_tokens`; you only pay for output tokens that are actually generated.