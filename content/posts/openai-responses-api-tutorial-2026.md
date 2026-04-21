---
title: "OpenAI Responses API Tutorial 2026: Build Stateful AI Apps in Python"
date: 2026-04-21T00:11:38+00:00
tags: ["openai", "api", "python", "ai-agents", "tutorial"]
description: "Complete OpenAI Responses API tutorial 2026: stateful conversations, built-in tools, function calling, and migration from Chat Completions."
draft: false
cover:
  image: "/images/openai-responses-api-tutorial-2026.png"
  alt: "OpenAI Responses API Tutorial 2026: Build Stateful AI Apps in Python"
  relative: false
schema: "schema-openai-responses-api-tutorial-2026"
---

The OpenAI Responses API is the new primary interface for building stateful, agentic AI applications — replacing the Assistants API (being sunset H1 2026) and extending beyond what Chat Completions can do. This tutorial walks through everything from your first API call to building multi-step agents with built-in tools like web search and file retrieval.

## What Is the OpenAI Responses API?

The OpenAI Responses API is a stateful, tool-native interface for building AI agents and multi-turn applications — launched in March 2025 as OpenAI's replacement for the Assistants API and a significant evolution beyond Chat Completions. Unlike Chat Completions, which is stateless (every request requires you to resend the full conversation history), Responses API maintains conversation state server-side using `previous_response_id`. A 10-turn conversation with Chat Completions resends your entire history on turn 10, making it up to 5x more expensive for long dialogues. Responses API sends only the new message each turn — the server already holds context. Built-in tools (web search at $25–50/1K queries, file search at $2.50/1K queries) are first-class citizens rather than custom function definitions, and reasoning tokens from o3 and o4-mini are preserved between turns instead of being discarded. OpenAI has moved all example code in the openai-python repository to Responses API patterns — it is where the platform is going.

### Key Architecture Concepts

The Responses API is built around three core primitives that differ from Chat Completions:

- **Response objects** — Each API call returns a Response object with an `id` field. Pass this as `previous_response_id` in the next call to chain turns without resending history.
- **Built-in tools** — `web_search_preview`, `file_search`, and `computer_use_preview` are activated by including them in the `tools` array. No custom server infrastructure required.
- **Semantic streaming events** — Instead of raw token deltas, streaming emits structured events like `response.output_item.added`, `response.content_part.added`, and `response.done`.

## Chat Completions vs Responses API vs Assistants API

The Responses API occupies a distinct position: it is more capable than Chat Completions for stateful and agentic workflows, while being simpler and cheaper than the Assistants API that it is replacing. Understanding which to use requires knowing what each one manages for you versus what you manage yourself. Chat Completions gives you maximum control (you own all state, all persistence, all tool execution loops) at the cost of client-side complexity. Responses API moves state management and tool orchestration server-side while keeping the request/response model familiar. Assistants API managed Threads, Runs, and Files as persistent objects — a full lifecycle that developers found overly complex for most use cases. OpenAI is converging on Responses API as the primary stateful API.

| Feature | Chat Completions | Responses API | Assistants API |
|---|---|---|---|
| State management | Client-side | Server-side | Server-side (Threads) |
| Built-in tools | No | Yes | Yes (Code Interpreter, etc.) |
| Reasoning token preservation | No | Yes | No |
| Pricing overhead | Lowest | Medium | Highest |
| Streaming events | Raw token deltas | Semantic events | SSE stream |
| Status | Active | Active (primary) | Sunset H1 2026 |
| Multi-provider support | Wide | Open Responses spec | OpenAI only |

The migration path from Assistants to Responses is the most urgent — H1 2026 sunset means any Threads/Runs code needs to be ported now.

## Getting Started: Your First Responses API Call

Making your first Responses API call requires the `openai` Python package (version ≥ 1.66.0 for full Responses support) and an API key. The shape of the request is close to Chat Completions but uses a different method and a different response schema. The critical difference from Chat Completions is the `input` parameter instead of `messages`, and the `model` field supporting all GPT-4o, o3, and o4-mini identifiers. The response is a `Response` object with an `id` field that enables state chaining, `output` containing the model's reply, and usage statistics. You do not need to configure threads, assistants, or vector stores before making your first call — just the model and the input.

**Install and authenticate:**

```bash
pip install openai>=1.66.0
export OPENAI_API_KEY="sk-..."
```

**Your first call (Python):**

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o",
    input="Explain the difference between Responses API and Chat Completions in one paragraph."
)

print(response.output[0].content[0].text)
print(f"Response ID: {response.id}")  # Save this for multi-turn
```

**JavaScript/TypeScript equivalent:**

```javascript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o",
  input: "Explain the difference between Responses API and Chat Completions."
});

console.log(response.output[0].content[0].text);
console.log(`Response ID: ${response.id}`);
```

The response object structure is different from `ChatCompletion` — `output` is a list of items, each with a `content` list. Text is at `response.output[0].content[0].text`.

## Server-Side State Management with previous_response_id

Server-side state management via `previous_response_id` is the most significant capability that Responses API adds over Chat Completions. When you pass a `previous_response_id` to a new request, the OpenAI server reconstructs the conversation context internally — you only send the new user message, not the full history. This eliminates the most expensive part of long conversations: re-tokenizing and re-encoding historical messages on every turn. For a 10-turn conversation with 500 tokens per turn, Chat Completions sends approximately 5,000 tokens on turn 10 (full history) while Responses API sends roughly 500 tokens (just the new input). At scale across thousands of daily active users, this is not a marginal difference. Reasoning tokens from o3 and o4-mini are also preserved — the model's internal chain-of-thought from turn 3 informs turn 7, producing more coherent agentic behavior than Chat Completions where that reasoning context is lost.

**Multi-turn conversation example:**

```python
from openai import OpenAI

client = OpenAI()

# Turn 1
response_1 = client.responses.create(
    model="gpt-4o",
    input="I'm building a Python web scraper. Where should I start?"
)
print("Assistant:", response_1.output[0].content[0].text)

# Turn 2 — only send new message, server holds context
response_2 = client.responses.create(
    model="gpt-4o",
    previous_response_id=response_1.id,
    input="Which HTTP library would you recommend for async scraping?"
)
print("Assistant:", response_2.output[0].content[0].text)

# Turn 3 — chain continues
response_3 = client.responses.create(
    model="gpt-4o",
    previous_response_id=response_2.id,
    input="Show me a basic example using that library."
)
print("Assistant:", response_3.output[0].content[0].text)
```

Store `response.id` in your database alongside the user session. When the user returns, load their latest `response_id` and pass it as `previous_response_id` — the conversation resumes with full context.

### Managing State in Production

For production applications, treat `previous_response_id` like a foreign key in your session table:

```python
import sqlite3
from openai import OpenAI

client = OpenAI()
db = sqlite3.connect("sessions.db")
db.execute("CREATE TABLE IF NOT EXISTS sessions (user_id TEXT, last_response_id TEXT)")

def chat(user_id: str, message: str) -> str:
    row = db.execute("SELECT last_response_id FROM sessions WHERE user_id=?", (user_id,)).fetchone()
    prev_id = row[0] if row else None

    response = client.responses.create(
        model="gpt-4o",
        input=message,
        previous_response_id=prev_id
    )

    new_id = response.id
    db.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?)", (user_id, new_id))
    db.commit()
    return response.output[0].content[0].text
```

## Built-in Tools: Web Search, File Search, and Computer Use

Built-in tools in the Responses API replace custom infrastructure that developers previously had to build and maintain themselves. Web search (`web_search_preview`) lets the model query the live web and return cited results without you managing a search API key or result parsing logic. File search (`file_search`) enables semantic retrieval over uploaded documents using OpenAI-hosted vector stores — at $2.50 per 1,000 queries with the first gigabyte of storage free and $0.10/GB/day after that. Computer use (`computer_use_preview`) allows the model to control a browser or desktop environment, opening the door to automation workflows that were previously limited to specialized tools. These tools are activated by listing them in the `tools` array of your request — no separate SDK, no custom endpoints. The model decides when to invoke them based on the user's input, executes them server-side, and returns the enriched response in a single API call.

**Web search tool:**

```python
response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search_preview"}],
    input="What are the latest OpenAI API pricing changes in 2026?"
)

# Response includes citations
for item in response.output:
    if item.type == "message":
        print(item.content[0].text)
    elif item.type == "web_search_call":
        print(f"Searched: {item.query}")
```

**File search with vector store:**

```python
# Upload files first
with open("docs/api_reference.pdf", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

# Create vector store
vs = client.vector_stores.create(name="API Docs")
client.vector_stores.files.create(vector_store_id=vs.id, file_id=file.id)

# Query with file search
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "file_search",
        "vector_store_ids": [vs.id]
    }],
    input="What are the rate limits for the Responses API?"
)
print(response.output[0].content[0].text)
```

**Tool pricing summary:**

| Tool | Cost |
|---|---|
| `web_search_preview` | $25–50 per 1,000 queries |
| `file_search` | $2.50 per 1,000 queries + $0.10/GB/day storage (first GB free) |
| `computer_use_preview` | Billed at model token rates + compute |

## Function Calling with the Responses API

Function calling in the Responses API follows the same five-step loop as Chat Completions, but integrates cleanly with server-side state so you do not need to manually reconstruct conversation history after each tool execution. The loop is: define tools → send request → model returns `function_call` items in `output` → execute functions locally → send results back with `previous_response_id` → model generates final response. Strict mode (`strict: true`) uses constrained decoding at token generation time to guarantee 100% schema compliance — critical for production agents where a malformed JSON response would break your execution logic. Parallel tool calls allow the model to request multiple function executions in a single response; you run all of them simultaneously and return all results in one follow-up request.

**Five-step function calling loop:**

```python
import json
from openai import OpenAI

client = OpenAI()

# Step 1: Define tools
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city", "units"],
            "additionalProperties": False
        },
        "strict": True  # Step 1b: Enable strict mode
    }
]

# Step 2: Send request
response = client.responses.create(
    model="gpt-4o",
    tools=tools,
    input="What's the weather in Tokyo and Berlin?"
)

# Step 3: Check for tool calls
tool_calls = [item for item in response.output if item.type == "function_call"]

# Step 4: Execute functions
results = []
for tc in tool_calls:
    args = json.loads(tc.arguments)
    # Your actual implementation
    weather_data = {"temperature": 18, "condition": "partly cloudy"}
    results.append({
        "type": "function_call_output",
        "call_id": tc.call_id,
        "output": json.dumps(weather_data)
    })

# Step 5: Send results, get final response
final = client.responses.create(
    model="gpt-4o",
    previous_response_id=response.id,
    input=results
)
print(final.output[0].content[0].text)
```

### Parallel Tool Calls

When the model needs multiple data points, it can request them all at once. Execute in parallel and return all results together:

```python
import asyncio

async def execute_tool(tc):
    args = json.loads(tc.arguments)
    # Async execution of each tool call
    result = await fetch_data(args)
    return {
        "type": "function_call_output",
        "call_id": tc.call_id,
        "output": json.dumps(result)
    }

tool_calls = [item for item in response.output if item.type == "function_call"]
results = await asyncio.gather(*[execute_tool(tc) for tc in tool_calls])
```

For dependent operations (tool B requires tool A's output), set `parallel_tool_calls: False` or use o3/o4-mini which naturally sequences calls based on reasoning.

## Strict Mode and Schema Enforcement for Production

Strict mode in the Responses API's function calling achieves 100% schema compliance by applying constrained decoding at the token generation level — the model cannot produce a token that would violate your JSON schema. This is fundamentally different from prompt-level instructions ("always return valid JSON") which can fail under adversarial inputs or long context. For production agents processing thousands of tool call cycles, even a 0.1% JSON parse failure rate creates operational overhead: error logging, retry logic, fallback handling, user-facing error states. Strict mode eliminates this class of failure entirely at generation time. The requirement is that your schema uses only supported types (`string`, `number`, `boolean`, `object`, `array`, `null`), sets `additionalProperties: false` on all objects, and marks all properties as `required`. These constraints are strict mode's trade-off: less flexible schemas in exchange for guaranteed compliance.

```python
tool_schema = {
    "type": "function",
    "name": "create_ticket",
    "description": "Create a support ticket in the system",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "assignee_id": {"type": ["string", "null"]},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["title", "priority", "assignee_id", "tags"],
        "additionalProperties": False
    },
    "strict": True
}
```

With `strict: True`, if the model cannot fit a value into your schema, it will use `null` for nullable fields rather than hallucinating invalid values.

## Streaming with Semantic Events

Streaming in the Responses API uses structured semantic events rather than the raw `choices[0].delta.content` tokens you get from Chat Completions. This matters for building reactive UIs and agent orchestration loops: you know exactly when a tool call starts, when content is being added, and when the response is complete — without parsing partial JSON or managing your own buffer state. Semantic events include `response.output_item.added` (new output item starting), `response.content_part.added` (new content part), `response.output_text.delta` (token-by-token text), `response.tool_call.arguments.delta` (streaming tool call arguments), and `response.done` (full response complete with final object). This is a meaningful ergonomic improvement for streaming agents because tool call arguments arrive incrementally — you can start validation or UI feedback before the full JSON is assembled.

```python
with client.responses.stream(
    model="gpt-4o",
    tools=[{"type": "web_search_preview"}],
    input="Search for the latest news on OpenAI Responses API"
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "response.output_item.added":
            if event.item.type == "web_search_call":
                print(f"\n[Searching: {event.item.query}]")
        elif event.type == "response.done":
            print(f"\n\nFinal response ID: {event.response.id}")
```

## Cost Architecture: When to Use Which API

The Responses API sits between Chat Completions (lowest cost) and Assistants API (highest overhead) in terms of cost structure. For short, single-turn interactions, Chat Completions is still cheaper — there is no state storage overhead and no per-query tool pricing. For conversations longer than 3–4 turns, Responses API often wins because you stop paying to re-tokenize history: a 10-turn conversation with 500 tokens of context per turn costs roughly 5,000 input tokens on Chat Completions turn 10 vs roughly 500 tokens on Responses API. The break-even point depends on your average conversation length and token costs for your chosen model. Built-in tools add per-use costs but replace infrastructure you would otherwise build: a self-hosted web search integration requires API keys, result parsing, prompt injection into context, and maintenance. At $25–50/1K queries, `web_search_preview` is often cheaper than developer time for low-to-medium volume applications.

| Scenario | Recommended API | Reason |
|---|---|---|
| Single-turn completions, high volume | Chat Completions | No state overhead |
| Multi-turn chat (3+ turns) | Responses API | Avoids history resend cost |
| Document Q&A with file retrieval | Responses API + file_search | Built-in vector store |
| Web-augmented research agents | Responses API + web_search | No custom search infra |
| Legacy Assistants code | Migrate to Responses | Assistants sunset H1 2026 |
| Multi-provider portability | Responses API (Open Responses spec) | Works on Ollama, vLLM, etc. |

## The Open Responses Specification

The Open Responses specification is a multi-provider API standard backed by OpenAI, Nvidia, Vercel, OpenRouter, Hugging Face, LM Studio, Ollama, and vLLM — defining a shared interface for stateful AI responses that any compatible server can implement. This matters for developers building on the Responses API because it means your code is not locked to OpenAI infrastructure. Ollama added Open Responses support in v0.13.3 (non-stateful flavor for local models), and vLLM ships a fully compatible server for self-hosted deployments. Azure OpenAI also supports the Responses API through its own hosted endpoint. The specification defines the request/response schema, streaming event format, and tool calling protocol — the same `previous_response_id` chaining, same `tools` array format, same semantic streaming events. Write once, run on OpenAI, Azure, local Ollama, or any vLLM deployment.

```python
# Point to any Open Responses-compatible server
client = OpenAI(
    api_key="ollama",  # or your local API key
    base_url="http://localhost:11434/v1/responses"  # local Ollama
)

# Same code works — just the endpoint changes
response = client.responses.create(
    model="llama3.2",
    input="Explain stateful conversation management."
)
```

## Migrating from Chat Completions to Responses API

Migrating from Chat Completions to Responses API is the most straightforward upgrade path because the model IDs are identical, the tool definition format is compatible, and you can migrate incrementally — route new features to Responses API while leaving existing Chat Completions code untouched. The surface-level change is `client.chat.completions.create()` → `client.responses.create()`, `messages` → `input`, and manually managed history → `previous_response_id`. For streaming, swap `for chunk in stream` token handling for semantic event processing. The deeper change is architectural: you stop owning conversation state in your database and delegate it to OpenAI's server, keeping only the `response_id` as a foreign key.

**Before (Chat Completions):**

```python
history = []

def chat(message: str) -> str:
    history.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=history  # Full history every time
    )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply
```

**After (Responses API):**

```python
last_response_id = None

def chat(message: str) -> str:
    global last_response_id
    response = client.responses.create(
        model="gpt-4o",
        input=message,
        previous_response_id=last_response_id  # Just the ID
    )
    last_response_id = response.id
    return response.output[0].content[0].text
```

## Migrating from Assistants API Before H1 2026 Sunset

The Assistants API is being sunset in H1 2026, which means any production code using Threads, Runs, Messages, or Assistants objects needs to be ported to Responses API before that date. The migration is not a one-to-one mapping — the conceptual model is different — but the capabilities are equivalent or improved. Threads (persistent conversation containers) map to `previous_response_id` chains. Runs (execution units with polling) are replaced by single synchronous or streaming Responses API calls. Messages objects (structured conversation history) are replaced by the `output` array in each Response. Assistants (reusable agent configurations with tools and system prompts) map to per-request `instructions` and `tools` parameters, or can be encapsulated in a Python class. The main operational change: you no longer poll for Run completion — Responses API calls block until complete (or stream incrementally).

**Assistants API pattern (to replace):**

```python
# OLD: Assistants API (sunset H1 2026)
thread = client.beta.threads.create()
client.beta.threads.messages.create(thread_id=thread.id, role="user", content=message)
run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant_id)
messages = client.beta.threads.messages.list(thread_id=thread.id)
reply = messages.data[0].content[0].text.value
```

**Responses API equivalent:**

```python
# NEW: Responses API
response = client.responses.create(
    model="gpt-4o",
    instructions="You are a helpful assistant specializing in Python development.",
    tools=[{"type": "file_search", "vector_store_ids": [vs_id]}],
    input=message,
    previous_response_id=prev_response_id  # replaces Thread
)
reply = response.output[0].content[0].text
prev_response_id = response.id  # store for next turn
```

## Building a Complete Agent: End-to-End Tutorial

A complete Responses API agent combines server-side state, built-in tools, and function calling into a workflow that handles multi-step reasoning without manual orchestration loops. The following agent answers research questions by searching the web, retrieving relevant files, and synthesizing a cited response — all in a single Responses API call that handles tool execution internally when using built-in tools, or across two calls when using custom functions.

```python
import json
from openai import OpenAI

client = OpenAI()

# Agent configuration
TOOLS = [
    {"type": "web_search_preview"},
    {
        "type": "function",
        "name": "save_to_notes",
        "description": "Save a research finding to the user's notes",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["title", "content", "tags"],
            "additionalProperties": False
        },
        "strict": True
    }
]

SYSTEM_PROMPT = """You are a research assistant. When asked a question:
1. Search the web for current information
2. Synthesize findings with citations
3. If the user asks to save findings, use the save_to_notes function
Always cite your sources."""

class ResearchAgent:
    def __init__(self):
        self.notes = []
        self.last_response_id = None

    def run(self, user_message: str) -> str:
        response = client.responses.create(
            model="gpt-4o",
            instructions=SYSTEM_PROMPT,
            tools=TOOLS,
            input=user_message,
            previous_response_id=self.last_response_id
        )

        # Handle function calls (built-in tools execute automatically)
        function_calls = [i for i in response.output if i.type == "function_call"]
        if function_calls:
            results = []
            for fc in function_calls:
                args = json.loads(fc.arguments)
                if fc.name == "save_to_notes":
                    self.notes.append(args)
                    result = {"saved": True, "note_count": len(self.notes)}
                results.append({
                    "type": "function_call_output",
                    "call_id": fc.call_id,
                    "output": json.dumps(result)
                })
            # Get final response after function execution
            response = client.responses.create(
                model="gpt-4o",
                previous_response_id=response.id,
                input=results
            )

        self.last_response_id = response.id
        return response.output[0].content[0].text

# Usage
agent = ResearchAgent()
print(agent.run("What are the key features of the OpenAI Responses API launched in 2025?"))
print(agent.run("Save those findings to my notes with the tag 'openai-api'"))
print(agent.run("What questions do I still have based on what we've discussed?"))
```

---

## FAQ

The OpenAI Responses API introduces a fundamentally different programming model compared to Chat Completions and the now-sunset Assistants API. The most common questions from developers migrating existing applications center on state management, cost implications, and tool compatibility. These answers address the questions that come up most frequently when teams evaluate or implement the Responses API in production systems — covering `previous_response_id` chaining, the Assistants API sunset timeline, multi-provider portability via the Open Responses specification, cost savings on long conversations, and the interaction between custom function calling and built-in tools. Each answer is self-contained and reflects the current Responses API behavior as of April 2026. The Responses API launched in March 2025 and has since become OpenAI's primary recommended interface for stateful and agentic applications, with the openai-python library updated to use Responses API patterns throughout its examples.

### What is the difference between OpenAI Responses API and Chat Completions?

The key difference is state management. Chat Completions is stateless — you send the full conversation history on every request and manage persistence yourself. Responses API maintains conversation state server-side via `previous_response_id`, so each turn only sends the new message. Responses API also includes built-in tools (web search, file search) that Chat Completions lacks, and preserves reasoning tokens between turns for o3 and o4-mini models.

### When will the Assistants API be sunset?

OpenAI has announced the Assistants API will be sunset in H1 2026. This means any production code using Threads, Runs, Messages, or the Assistants beta endpoints needs to be migrated to the Responses API before that deadline. The migration is well-documented and the Responses API provides all equivalent capabilities — stateful conversations, file retrieval, and tool use.

### Is the OpenAI Responses API available on Azure OpenAI?

Yes. Azure OpenAI supports the Responses API through its hosted endpoint. Additionally, the Open Responses specification backed by Nvidia, Vercel, OpenRouter, and others enables the same API surface on Ollama (v0.13.3+), vLLM, and other compatible servers. The `base_url` parameter in the OpenAI Python client lets you point to any compatible server.

### How does `previous_response_id` save money on long conversations?

In a 10-turn conversation with Chat Completions, turn 10 sends the entire 9-turn history plus the new message — potentially thousands of tokens of input. With Responses API, turn 10 only sends the new message (a few hundred tokens) because the server already holds the full context. OpenAI estimates Chat Completions can be up to 5x more expensive for long conversations due to this history re-tokenization cost.

### Can I use both function calling and built-in tools in the same Responses API call?

Yes. You can include both custom function definitions and built-in tools (like `web_search_preview` or `file_search`) in the same `tools` array. The model will call whichever tools are relevant to the user's request. Built-in tools execute server-side and their results appear automatically in `response.output`, while custom function calls require your client to execute them and return results via a follow-up request with `previous_response_id`.
