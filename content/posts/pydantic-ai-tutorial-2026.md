---
cover:
  alt: 'Pydantic AI Tutorial 2026: Type-Safe Python Agents With Automatic Validation
    and Self-Correction'
  image: /images/pydantic-ai-tutorial-2026.png
  relative: false
date: 2026-04-22 01:13:32+00:00
description: Build production-ready AI agents with Pydantic AI — type-safe structured
  outputs, tool calling, dependency injection, and automatic validation retries.
draft: false
schema: schema-pydantic-ai-tutorial-2026
tags:
- pydantic-ai
- python
- ai-agents
- llm
- type-safety
- tutorial
title: 'Pydantic AI Tutorial 2026: Type-Safe Python Agents With Automatic Validation
  and Self-Correction'
---

Pydantic AI is a Python agent framework built by the Pydantic team that brings type-safe, validated LLM interactions to production. Install it with `pip install pydantic-ai`, define your agent with a Pydantic `BaseModel` as the result type, and the framework automatically validates LLM output — retrying if validation fails — without any manual JSON parsing or schema wrestling.

## What Is Pydantic AI?

Pydantic AI is an open-source Python agent framework, released in November 2024, that applies Pydantic's battle-tested validation engine directly to LLM interactions. With 16,500+ GitHub stars and 2,000+ forks as of April 2026, it has become one of the fastest-adopted agent frameworks in the Python ecosystem. Pydantic already powers the validation layer for OpenAI SDK, Google ADK, Anthropic SDK, LangChain, LlamaIndex, and CrewAI — Pydantic AI extends this same validation philosophy to the agent orchestration layer itself. Unlike LangChain, which relies on prompt engineering and string parsing to coerce LLM outputs into structure, Pydantic AI uses native Python type annotations and `BaseModel` schemas so your IDE catches type errors at write time, not at runtime. The design goal — as stated in the official docs — is to bring the FastAPI ergonomics of type-safe, auto-documented APIs to GenAI agent development: define the schema, wire up the model, and let the framework handle validation, retries, and error recovery automatically.

### How Pydantic AI Compares to LangChain and CrewAI

Pydantic AI focuses on type safety as a first-class feature. Where LangChain provides broad abstractions over dozens of integrations, Pydantic AI trades breadth for correctness: every structured output is validated against a `BaseModel` schema at runtime, with automatic retries when the LLM returns invalid data. CrewAI provides higher-level orchestration for role-based multi-agent teams, while Pydantic AI operates at a lower level — think of it as the foundation you'd build a CrewAI-style system on top of, with stronger type guarantees throughout.

### The FastAPI-of-AI Promise

The FastAPI analogy runs deep. FastAPI replaced boilerplate Flask route handlers with type-annotated functions that auto-generate OpenAPI docs and validate request/response payloads. Pydantic AI does the same for LLM agents: instead of writing prompt templates, manually parsing JSON, and hoping the model follows your schema, you declare a typed result model and the framework handles the rest. This means static analysis tools like mypy and pyright work end-to-end across your agent code.

## Setting Up Your First Pydantic AI Project

Setting up Pydantic AI takes under five minutes for any developer with Python 3.10+ and a model API key. The core package installs cleanly: `pip install pydantic-ai` pulls in the framework and its model adapters. For provider-specific extras you can use `pip install pydantic-ai[openai]`, `pydantic-ai[anthropic]`, or `pydantic-ai[gemini]`. As of April 2026, Pydantic AI supports 20+ model providers including OpenAI, Anthropic, Gemini, DeepSeek, Groq, Ollama (local), Azure AI Foundry, and Amazon Bedrock — switching providers requires only changing one string in your Agent constructor. The recommended project structure mirrors FastAPI conventions: an `agents/` directory for agent definitions, a `models/` directory for Pydantic schemas, and `tools/` for callable functions. Environment variables follow provider conventions (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`), and the framework reads them automatically without any extra configuration code.

```bash
pip install pydantic-ai
export OPENAI_API_KEY="sk-..."
```

```python
from pydantic_ai import Agent

agent = Agent("openai:gpt-4o")
result = agent.run_sync("What is the capital of France?")
print(result.data)  # "Paris"
```

### Configuring Model Providers

Switching models requires only a string change in your Agent constructor — no additional configuration or adapter code needed:

```python
# OpenAI
agent = Agent("openai:gpt-4o")

# Anthropic
agent = Agent("anthropic:claude-sonnet-4-6")

# Local via Ollama (no API key required)
agent = Agent("ollama:llama3.2")

# Google Gemini
agent = Agent("google-gla:gemini-2.0-flash")
```

## Building Your First AI Agent

A Pydantic AI agent is a Python object that wraps a model, a system prompt, optional tools, and a typed result schema. The minimal example — `Agent("openai:gpt-4o")` — creates a string-output agent using OpenAI's GPT-4o. For synchronous code, `agent.run_sync(prompt)` blocks until the model responds; for async applications, `await agent.run(prompt)` integrates directly with asyncio and FastAPI route handlers. Streaming responses work with `agent.run_stream(prompt)` as an async context manager, yielding text chunks as they arrive from the model. The returned `RunResult` object carries `.data` (the validated output), `.usage()` (token counts and cost tracking), and `.all_messages()` (the full conversation history for multi-turn use cases). System prompts can be static strings passed to the constructor or dynamic functions decorated with `@agent.system_prompt` that receive the dependency context and generate prompts at runtime based on user data or configuration. The entire API surface is intentionally minimal — if you know FastAPI, you already know most of Pydantic AI's patterns.

```python
from pydantic_ai import Agent

agent = Agent(
    "openai:gpt-4o",
    system_prompt="You are a helpful assistant. Be concise."
)

result = agent.run_sync("Explain async/await in Python in one sentence.")
print(result.data)
print(result.usage())  # Usage(requests=1, tokens=...)
```

### Streaming Responses

```python
import asyncio
from pydantic_ai import Agent

agent = Agent("anthropic:claude-sonnet-4-6")

async def stream_response():
    async with agent.run_stream("Write a haiku about Python.") as stream:
        async for chunk in stream.stream_text(delta=True):
            print(chunk, end="", flush=True)

asyncio.run(stream_response())
```

## Structured Outputs With Pydantic Models

Structured outputs are the defining feature of Pydantic AI: define a `BaseModel` subclass as your agent's `result_type` and the framework guarantees that every response conforms to your schema — or automatically retries the query until it does. This eliminates the most common failure mode in LLM applications: brittle JSON parsing that breaks when the model adds an unexpected field, nests objects differently, or returns prose instead of valid JSON. In a production e-commerce scenario, for example, you might define `ProductExtraction(BaseModel)` with fields for `name: str`, `price: float`, `currency: str`, `availability: bool`, and `attributes: dict[str, str]`. Pass unstructured product description text to the agent and get back a fully-validated Python object that your IDE understands, your type checker approves, and your database ORM can insert directly. The validation retry mechanism uses the Pydantic validation error message as additional context for the LLM on the next attempt — so the model learns from its mistake within the same request, dramatically improving success rates on complex schemas compared to single-shot prompting. This self-correction capability is what makes Pydantic AI particularly reliable for production workloads.

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class MovieReview(BaseModel):
    title: str
    year: int
    sentiment: str  # "positive", "negative", "neutral"
    score: float    # 0.0 to 10.0
    summary: str

agent = Agent(
    "openai:gpt-4o",
    result_type=MovieReview,
    system_prompt="Extract structured movie review data from user input."
)

result = agent.run_sync(
    "Inception (2010) was mind-blowing, a perfect 10/10 thriller."
)
review = result.data
print(review.title)      # "Inception"
print(review.year)       # 2010
print(review.score)      # 10.0
print(review.sentiment)  # "positive"
```

### Complex Nested Models

```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str

class CompanyProfile(BaseModel):
    name: str
    founded: int
    headquarters: Address
    products: List[str]
    revenue_usd_millions: Optional[float] = None

agent = Agent("openai:gpt-4o", result_type=CompanyProfile)
result = agent.run_sync("Tell me about Stripe the payments company.")
profile = result.data
print(profile.headquarters.city)  # "San Francisco"
```

## Tool Calling and Function Integration

Tool calling in Pydantic AI uses the `@agent.tool` decorator to register Python functions that the LLM can invoke autonomously during a conversation. The LLM reads the function's docstring to understand what the tool does, reads the type annotations to understand input and output types, and decides when to call it based on the user's query — no separate schema definition, no JSON Schema boilerplate, no manual tool routing. This approach, used in the official Pydantic AI examples repository (16,500+ GitHub stars), covers real-world cases from weather APIs to SQL query execution to bank account lookups. Tools receive a `RunContext[DepsType]` as their first argument, giving them access to the dependency injection context — databases, API clients, configuration — in a fully type-safe way. The LLM can call multiple tools in sequence, use one tool's output as input to another, and combine tool results with its own reasoning before returning a final structured answer. Pydantic AI validates all tool inputs against their type annotations before executing the function, so type errors surface immediately rather than propagating silently through your agent pipeline. Well-written docstrings are critical: the LLM uses them to decide which tool to call and how to populate its arguments.

```python
import httpx
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class WeatherReport(BaseModel):
    location: str
    temperature_celsius: float
    conditions: str
    humidity_percent: int

agent = Agent(
    "openai:gpt-4o",
    result_type=WeatherReport,
    system_prompt="Use the weather tool to fetch current conditions for the requested city."
)

@agent.tool
async def get_weather(ctx: RunContext[None], city: str) -> dict:
    """Fetch current weather data for a given city name. Returns temperature, conditions, and humidity."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://wttr.in/{city}?format=j1")
        data = resp.json()
        current = data["current_condition"][0]
        return {
            "temp_c": float(current["temp_C"]),
            "desc": current["weatherDesc"][0]["value"],
            "humidity": int(current["humidity"])
        }

result = agent.run_sync("What's the weather like in Tokyo right now?")
print(result.data.temperature_celsius)
```

### How LLMs Choose Which Tool to Call

Write docstrings that describe *what* the tool does, *when* to use it, and *what* its parameters represent. A well-documented tool is called correctly; a vague docstring leads to incorrect tool selection or missing arguments. For agents with many tools, use `@agent.tool_plain` for tools that don't need the `RunContext` — this signals to the LLM that the tool has no side effects on agent state.

## Dependency Injection for Type-Safe Context

Dependency injection in Pydantic AI solves the global state problem that plagues most LLM agent frameworks: instead of using module-level variables or environment lookups inside tool functions, you declare a typed dependency container and inject it at runtime via the `deps_type` parameter on the Agent constructor. This pattern — familiar to FastAPI developers — makes agents fully testable because tests can inject mock dependencies without patching globals or monkeypatching module state. A typical production agent might depend on a database connection pool, an HTTP client, a user authentication context, and a configuration object. Define these as a `dataclass` or `BaseModel`, annotate your tools with `RunContext[MyDeps]`, and Pydantic AI ensures your tools receive exactly the right types with full IDE autocomplete and static analysis support. The dependency container is constructed outside the agent and passed at call time: `agent.run_sync(prompt, deps=MyDeps(db=pool, client=http_client))`. This makes agents composable — the same agent definition works with different dependency configurations in different environments, supporting local development, testing, staging, and production without any code changes to the agent itself.

```python
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
import asyncpg

@dataclass
class Deps:
    db_pool: asyncpg.Pool
    user_id: int

class OrderSummary(BaseModel):
    total_orders: int
    total_spent_usd: float
    most_recent_order: str

agent = Agent(
    "anthropic:claude-sonnet-4-6",
    deps_type=Deps,
    result_type=OrderSummary,
    system_prompt="Summarize the user's order history from the database."
)

@agent.tool
async def get_orders(ctx: RunContext[Deps]) -> list[dict]:
    """Fetch all orders for the current user from the database."""
    rows = await ctx.deps.db_pool.fetch(
        "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
        ctx.deps.user_id
    )
    return [dict(row) for row in rows]
```

## Multi-Agent Patterns and Orchestration

Multi-agent orchestration with Pydantic AI enables complex workflows where specialized agents hand off tasks to each other with full type safety preserved across agent boundaries. Pydantic AI supports this through agent delegation: one agent can call another agent's `run()` method inside a tool function, passing structured Pydantic models between agents at each handoff point. This eliminates a common failure mode in multi-agent systems where unstructured string passing between agents allows errors to propagate silently through a pipeline — in Pydantic AI, every agent boundary is an explicit type contract. A research-and-summarization pipeline might use a `ResearchAgent` that returns a `ResearchFindings(BaseModel)` with source URLs, key facts, and confidence scores, then pass that validated output to a `WriterAgent` that produces a `BlogPost(BaseModel)` with title, sections, and metadata. The Pydantic AI repository includes working examples of multi-agent patterns including a coding agent skill that uses sub-agents for code generation, review, and test execution. Each agent's typed output becomes the next agent's validated input, making the system debuggable, testable, and maintainable as the number of agents and the complexity of workflows grows.

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class ResearchFindings(BaseModel):
    topic: str
    key_facts: list[str]
    sources: list[str]
    confidence: float

class BlogPost(BaseModel):
    title: str
    introduction: str
    sections: list[str]
    conclusion: str

researcher = Agent(
    "openai:gpt-4o",
    result_type=ResearchFindings,
    system_prompt="Research topics thoroughly and cite your sources."
)

writer = Agent(
    "anthropic:claude-sonnet-4-6",
    result_type=BlogPost,
    system_prompt="Write engaging blog posts from research findings."
)

@writer.tool
async def research_topic(ctx, topic: str) -> dict:
    """Research a topic using the research agent and return structured findings."""
    result = await researcher.run(topic)
    return result.data.model_dump()
```

## Testing and Evaluating Your Agents

Testing AI agents with Pydantic AI is fundamentally more tractable than with other frameworks because every agent interaction has an explicit typed contract. Pydantic AI provides `TestModel` — a deterministic mock that returns schema-conformant responses without making real API calls, essential for CI/CD pipelines where LLM API costs and latency make live testing impractical. The built-in eval framework extends this to production monitoring: define test cases with expected structured outputs, run them against your agent, and track pass rates over time as you change models or prompts. This is the kind of production observability tooling that most agent frameworks leave entirely to the developer to build from scratch. For unit testing individual tools, the dependency injection pattern makes mocking trivial: inject a mock database or HTTP client via `deps`, call the tool function directly, and assert on its output without any LLM involvement. `pytest` integration is straightforward — use `agent.override(model=TestModel())` as a context manager to swap the real model for the test mock within a test function. For regression testing, record real LLM interactions with pytest-recording or VCR cassettes and replay them in CI.

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic import BaseModel

class Sentiment(BaseModel):
    label: str
    confidence: float

agent = Agent("openai:gpt-4o", result_type=Sentiment)

def test_sentiment_analysis():
    with agent.override(model=TestModel()):
        result = agent.run_sync("I love this product!")
        # TestModel returns schema-valid mock data without API calls
        assert isinstance(result.data, Sentiment)
        assert result.data.label in ["positive", "negative", "neutral"]
        assert 0.0 <= result.data.confidence <= 1.0
```

## Observability: Debugging With Pydantic Logfire

Pydantic Logfire is the native observability backend for Pydantic AI, built on OpenTelemetry so traces, spans, and metrics export to any compatible backend — Grafana, Datadog, Honeycomb, or the Logfire SaaS platform. Integrating Logfire takes three lines of code: `pip install logfire`, `import logfire`, `logfire.configure()` — after which every agent run, tool call, model request, and validation event is automatically traced with full context. Each span captures the model name, prompt tokens, completion tokens, cost estimate, tool inputs and outputs, and validation results, giving you a complete audit trail for debugging agent failures in production. The cost tracking feature aggregates token usage across nested agent calls, making it straightforward to identify expensive prompts or tools that are invoked more than expected. For teams already using OpenTelemetry with a different backend, Logfire respects the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable — there's no Pydantic-specific lock-in. The Logfire integration also instruments the automatic retry mechanism, recording each failed validation attempt and the corrected LLM response, which is invaluable for diagnosing structured output failures and understanding whether your schemas or your prompts need adjustment.

```python
import logfire
from pydantic_ai import Agent

logfire.configure()  # reads LOGFIRE_TOKEN from env
logfire.instrument_pydantic_ai()

agent = Agent("openai:gpt-4o", system_prompt="You are a helpful assistant.")
result = agent.run_sync("Summarize the benefits of type safety in Python.")
# Full trace — model, tokens, cost, tool calls — now visible in Logfire
```

## Production Best Practices

Running Pydantic AI agents in production requires attention to error handling, concurrency, cost management, and deployment patterns that differ meaningfully from development usage. The framework's model gateway feature (available in `pydantic-ai[gateway]`) provides a unified proxy layer for routing requests across multiple providers — try GPT-4o, fall back to Claude Sonnet if rate-limited — and centralizing API key management across your infrastructure. Error handling best practice is to catch `ModelRetry` exceptions (raised after all automatic validation retries are exhausted) at the application layer and implement graceful degradation rather than letting them propagate as 500 errors. Rate limiting is most effectively implemented with `asyncio.Semaphore` around concurrent agent runs, or with a task queue like ARQ or Celery for high-throughput batch workloads. Pydantic AI's async-native design means a single event loop can handle dozens of concurrent agent calls efficiently, but each call holds an open HTTP connection to the model API — connection pooling via a shared `httpx.AsyncClient` configured as a dependency significantly reduces per-call overhead. For FastAPI integration, mount agents as async route handlers that construct the dependency context from the request state and stream responses back using `StreamingResponse` with `run_stream()`, giving users real-time feedback while the agent works.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic_ai import Agent

app = FastAPI()
agent = Agent("openai:gpt-4o")

@app.post("/chat")
async def chat(request: dict):
    async def generate():
        async with agent.run_stream(request["message"]) as stream:
            async for chunk in stream.stream_text(delta=True):
                yield chunk
    return StreamingResponse(generate(), media_type="text/plain")
```

## Complete Project: A Production-Ready Research Agent

This end-to-end example combines structured outputs, tool calling, dependency injection, and observability into a single production-ready agent that researches a topic and returns a structured report. Notice how every boundary — the dependency container, the tool return types, the final result — is explicitly typed, making the entire agent system statically analyzable with mypy or pyright and fully testable with `TestModel`.

```python
import logfire
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
import httpx

logfire.configure()
logfire.instrument_pydantic_ai()

@dataclass
class ResearchDeps:
    http_client: httpx.AsyncClient
    max_sources: int = 5

class Source(BaseModel):
    url: str
    title: str
    relevance_score: float

class ResearchReport(BaseModel):
    topic: str
    summary: str
    key_findings: list[str]
    sources: list[Source]
    confidence: float
    follow_up_questions: list[str]

research_agent = Agent(
    "openai:gpt-4o",
    deps_type=ResearchDeps,
    result_type=ResearchReport,
    retries=2,
    system_prompt=(
        "You are an expert research assistant. Use the available tools to "
        "gather information, evaluate sources critically, and produce "
        "structured research reports with confidence scores."
    )
)

@research_agent.tool
async def web_search(ctx: RunContext[ResearchDeps], query: str) -> list[dict]:
    """Search the web for information. Returns a list of results with titles and URLs."""
    resp = await ctx.deps.http_client.get(
        "https://api.search.example.com/search",
        params={"q": query, "limit": ctx.deps.max_sources}
    )
    return resp.json()["results"]

@research_agent.tool
async def fetch_page_content(ctx: RunContext[ResearchDeps], url: str) -> str:
    """Fetch and return the main text content of a web page. Use to read full articles."""
    resp = await ctx.deps.http_client.get(url, follow_redirects=True)
    return resp.text[:5000]

async def run_research(topic: str) -> ResearchReport:
    async with httpx.AsyncClient(timeout=30.0) as client:
        deps = ResearchDeps(http_client=client, max_sources=5)
        result = await research_agent.run(
            f"Research the following topic thoroughly: {topic}",
            deps=deps
        )
        return result.data
```

## FAQ

**Does Pydantic AI work with local models like Ollama?**

Yes. Pydantic AI supports Ollama out of the box with `Agent("ollama:llama3.2")`. For structured outputs, the model must support function calling or JSON mode — most modern Ollama models (Llama 3.2+, Mistral, Qwen 2.5) support this. Performance of automatic validation retries depends on the model's instruction-following capability; GPT-4o and Claude Sonnet achieve near-100% first-attempt success on well-designed schemas, while smaller local models may require more retries or simpler schemas.

**How many validation retries does Pydantic AI attempt before failing?**

By default, Pydantic AI retries up to 1 time when structured output validation fails. Configure this with `retries` on the Agent constructor: `Agent("openai:gpt-4o", result_type=MyModel, retries=3)`. Each retry includes the Pydantic validation error message as additional context, giving the model the information it needs to correct its output. Set `retries=0` to disable automatic retries if you want to handle validation failures manually at the application layer.

**Can I use Pydantic AI alongside existing LangChain code?**

Pydantic AI operates independently of LangChain and doesn't integrate with LangChain chain abstractions. You can call Pydantic AI agents from within LangChain pipelines as ordinary Python function calls, passing strings or serialized Pydantic model outputs between them. For new agent development, Pydantic AI's type-safe approach is generally preferable; for existing LangChain projects, incremental adoption — replacing individual chains with Pydantic AI agents — is a practical migration strategy that avoids a full rewrite.

**How does Pydantic AI handle streaming with structured outputs?**

Streaming and structured outputs are mutually exclusive in a single agent run: `run_stream()` yields text tokens in real time but cannot validate the final output against a `BaseModel` until the stream completes. For use cases requiring both streaming UX and structured data, the recommended pattern is to stream the model's text response to the UI for display, then run a second non-streaming call with `result_type` to get a validated structured object for backend processing. The framework does not double-bill for this pattern when using response caching.

**Is Pydantic AI production-ready for high-throughput applications?**

Yes, with appropriate architecture. Pydantic AI's async-native design supports hundreds of concurrent agent calls on a single event loop. For high throughput, use `asyncio.gather()` for parallel independent calls, a task queue (ARQ, Celery) for background processing, and the model gateway feature for automatic failover across providers. Multiple teams are running thousands of daily agent interactions in production with Pydantic AI, and the framework's explicit type contracts make debugging production incidents significantly faster than with loosely-typed alternatives like vanilla LangChain.