---
cover:
  alt: LLM Function Calling and Tool Use Guide 2026
  image: /images/llm-function-calling-tool-use-guide-2026.png
  relative: false
date: 2026-04-27 14:36:31+00:00
description: Complete 2026 guide to LLM function calling across OpenAI, Anthropic,
  and Google Gemini—with code, security, and production patterns.
draft: false
schema: schema-llm-function-calling-tool-use-guide-2026
tags:
- llm function calling
- tool use
- OpenAI
- Anthropic
- Google Gemini
- AI agents
- production
title: 'LLM Function Calling and Tool Use Guide 2026: OpenAI, Anthropic, Google'
---

Function calling is the bridge between a language model's text output and the real world. Instead of asking a model to guess what the weather is, you hand it a `get_weather` tool definition, and it decides when to call it, what arguments to pass, and how to incorporate the result. As of 2026, every major provider—OpenAI, Anthropic, and Google—supports this pattern, but the APIs look meaningfully different. This guide walks through each one with working Python code and covers parallel calls, agent loops, security, and how to pick the right approach.

## What Is LLM Function Calling and Why Does It Matter?

LLM function calling is a structured protocol that lets a language model request execution of external functions during inference—passing typed arguments back to your application, which runs the function and returns results for the model to reason about. Unlike raw text completion, function calling gives the model a typed interface to the real world: databases, APIs, file systems, payment processors. OpenAI introduced the concept in June 2023 under the name "function calling," since renamed to the `tools` parameter. By 2026, this capability is the core primitive for every production AI agent. The LLMCompiler paper (ICML 2024) showed that parallel tool calls reduce end-to-end latency by up to 3.7x compared to sequential execution. Tool use also carries real costs: each tool definition adds 100–300 input tokens, so a system with 15 tools adds roughly 1,500–4,500 tokens to every request. Understanding format differences, security boundaries, and performance patterns is no longer optional for teams shipping AI features.

### Why All Three Providers Matter

OpenAI, Anthropic, and Google each have production deployments with billions of API calls per month. They share the same conceptual model—define tool, detect call, execute, return result—but differ enough in JSON schema and response structure that copy-paste code will break. Teams that lock into one provider today often need to migrate later. Knowing all three formats also helps you choose correctly: Anthropic's server-side tools (web search, code execution) remove entire categories of infrastructure work; Google's streaming argument support cuts latency in real-time UIs; OpenAI's `strict: true` mode guarantees schema-valid outputs at the cost of parallel call support.

## The Universal 5-Step Pattern That Works Across All Providers

Every function calling implementation follows the same five steps, regardless of which LLM you use. First, **define your tools** as structured schemas describing function names, descriptions, and parameter types. Second, **send a request** with both the user message and the tools array attached. Third, **detect a tool call** in the response—the model returns a structured object instead of plain text when it decides to invoke a function. Fourth, **execute the function** in your application code and capture the result. Fifth, **return the result** to the model in a follow-up request so it can formulate a final answer. This loop can repeat multiple times—multi-step agent patterns chain dozens of tool calls before returning to the user. The difference between providers is entirely in the JSON structure of steps 1, 3, and 5. Step 4 is always pure Python (or whatever language you use), and the result you return is just a string or structured object. Mastering the universal pattern first makes provider-specific syntax a minor detail rather than a conceptual hurdle.

### Core Vocabulary

| Term | Meaning |
|------|---------|
| Tool / Function | A callable action the model can request |
| Tool definition | JSON schema describing the function's name, description, and parameters |
| Tool call | The model's structured request to invoke a specific function |
| Tool result | Your application's response after executing the function |
| Parallel tool calls | Multiple tool calls in a single model turn |
| Agent loop | Repeated tool call / result cycles until the model produces a final answer |

## OpenAI Implementation: Tools Array, Strict Mode, and Parallel Calls

OpenAI's function calling API uses a `tools` parameter that accepts an array of objects, each with `type: "function"` and a nested `function` object containing `name`, `description`, and `parameters` (a JSON Schema object). When the model decides to call a function, the response's `choices[0].finish_reason` is `"tool_calls"` and `choices[0].message.tool_calls` contains an array of call objects. Each call has an `id`, a `type`, and a `function` sub-object with `name` and `arguments` (a JSON string). You execute the function, then append both the assistant message and a `tool` role message to the conversation history before the next request. OpenAI's `strict: true` mode—added in late 2024—enforces exact schema compliance on arguments, eliminating the hallucinated-field class of bugs. The tradeoff: `strict` mode is incompatible with parallel tool calls, so you pick one guarantee or the other. As of 2026, the `gpt-4.1` series and `o3` models all support parallel tool calls when `strict` is disabled, enabling the 3.7x latency improvement from the LLMCompiler paper.

```python
import json
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["city"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Tokyo and Berlin?"}],
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message
if message.tool_calls:
    results = []
    for call in message.tool_calls:
        args = json.loads(call.function.arguments)
        # Execute your actual function here
        result = {"temperature": 22, "condition": "sunny"}
        results.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(result)
        })

    final = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": "What's the weather in Tokyo and Berlin?"},
            message,
            *results
        ],
        tools=tools
    )
    print(final.choices[0].message.content)
```

### OpenAI Tool Choice Control

The `tool_choice` parameter controls whether the model must use tools. `"auto"` lets it decide, `"required"` forces at least one call, `{"type": "function", "function": {"name": "get_weather"}}` forces a specific function. Setting `"none"` disables tool calling entirely, useful when you want a plain text response after results are returned.

## Anthropic Tool Use Architecture: Input Schema, Content Blocks, and Server-Side Tools

Anthropic's tool use API differs from OpenAI in three important ways: tools are defined with `input_schema` instead of `parameters`, responses use typed content blocks instead of a `tool_calls` array, and Anthropic uniquely offers server-side built-in tools that run inside the API without any execution code on your end. When Claude decides to use a tool, `stop_reason` is `"tool_use"` and the `content` array contains a block of `type: "tool_use"` alongside any text blocks. You match on `type == "tool_use"` to extract `name` and `input` (already a parsed dict, not a JSON string). Results go back as a `tool_result` content block in a new `user` turn. The most distinctive Anthropic feature is built-in server-side tools: `web_search`, `code_execution` (sandboxed Python), and `text_editor`. Declaring `{"type": "web_search_20250305", "name": "web_search"}` in the tools list gives Claude live internet access with zero infrastructure on your end—Anthropic runs the search and returns results as part of the content stream. This removes entire categories of retrieval infrastructure that OpenAI and Google customers must build themselves.

```python
import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
]

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Weather in Paris?"}]
)

if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    # Execute your function with tool_use.input (already a dict)
    result = {"temperature": 18, "condition": "cloudy"}

    final = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "Weather in Paris?"},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(result)
                    }
                ]
            }
        ]
    )
    print(final.content[0].text)
```

### Anthropic Server-Side Tools

```python
# Web search with no infrastructure required
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "Latest AI news today?"}]
)
# Claude handles search internally — no tool_use loop needed
```

## Google Gemini Function Declarations: Protocol Buffer Types and Streaming

Google Gemini uses `FunctionDeclaration` objects inside a `Tool` wrapper, passed via the `tools` parameter. The type system derives from Protocol Buffers: `STRING`, `NUMBER`, `BOOLEAN`, `ARRAY`, `OBJECT` (all caps, from `google.generativeai.types`). When Gemini returns a function call, `response.candidates[0].content.parts` contains a `Part` with a `function_call` attribute holding `name` and `args` (a dict). Results go back as a `Part` with a `function_response` attribute. Gemini 2.5+ adds streaming function call arguments—arguments arrive incrementally as tokens generate, enabling your UI to show progress before execution completes. This is particularly valuable for latency-sensitive applications where users wait for agent responses. Google also supports `ANY` mode for `tool_config` (equivalent to OpenAI's `"required"`) and specific function forcing via `allowed_function_names`. Gemini's automatic function calling mode can execute Python functions directly using reflection, though production systems should handle execution explicitly for auditability.

```python
import google.generativeai as genai
import json

genai.configure(api_key="YOUR_API_KEY")

tools = genai.types.Tool(
    function_declarations=[
        genai.types.FunctionDeclaration(
            name="get_weather",
            description="Get current weather for a city",
            parameters=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                properties={
                    "city": genai.types.Schema(type=genai.types.Type.STRING),
                    "unit": genai.types.Schema(
                        type=genai.types.Type.STRING,
                        enum=["celsius", "fahrenheit"]
                    )
                },
                required=["city"]
            )
        )
    ]
)

model = genai.GenerativeModel("gemini-2.5-pro", tools=[tools])
chat = model.start_chat()
response = chat.send_message("Weather in Sydney?")

part = response.candidates[0].content.parts[0]
if hasattr(part, "function_call"):
    fc = part.function_call
    result = {"temperature": 25, "condition": "sunny"}

    from google.protobuf.struct_pb2 import Struct
    response_struct = Struct()
    response_struct.update(result)

    final = chat.send_message(
        genai.types.content_types.to_contents(
            genai.types.Part(
                function_response=genai.types.FunctionResponse(
                    name=fc.name,
                    response=response_struct
                )
            )
        )
    )
    print(final.text)
```

## Side-by-Side Provider Comparison

The three providers share conceptual structure but differ significantly in API surface, type systems, unique capabilities, and operational tradeoffs that matter in production. OpenAI's `tools` parameter uses standard JSON Schema with a `parameters` key, returns arguments as a JSON string that needs manual parsing, and uniquely offers `strict: true` mode for guaranteed schema-valid outputs. Anthropic uses `input_schema` instead of `parameters`, returns arguments as a pre-parsed Python dict (eliminating a common source of parse errors), and is the only provider offering server-side built-in tools like `web_search` and `code_execution` that require zero infrastructure. Google Gemini uses Protocol Buffer-derived types (`STRING`, `NUMBER`, `OBJECT`) rather than JSON Schema keywords, and Gemini 2.5+ uniquely supports streaming function call arguments—arguments arrive token-by-token as they generate, which cuts time-to-execution in latency-sensitive UIs. All three support parallel tool calls, though OpenAI's strict mode disables this feature.

| Feature | OpenAI | Anthropic | Google Gemini |
|---------|--------|-----------|---------------|
| Schema key | `parameters` (JSON Schema) | `input_schema` (JSON Schema) | `FunctionDeclaration` (Protobuf types) |
| Tool call detection | `finish_reason == "tool_calls"` | `stop_reason == "tool_use"` | Part has `function_call` attr |
| Arguments format | JSON string (needs parsing) | Dict (pre-parsed) | Proto Struct (dict-like) |
| Result format | `tool` role message | `tool_result` content block | `function_response` Part |
| Parallel calls | Yes (not with strict mode) | Yes | Yes |
| Strict schema mode | `strict: true` | N/A | N/A |
| Server-side tools | No | Yes (web_search, code_exec) | No |
| Streaming args | No | No | Yes (Gemini 2.5+) |
| Forced tool use | `tool_choice: "required"` | `tool_choice: {"type": "any"}` | `tool_config: ANY` |

### Token Cost Implications

Each tool definition consumes input tokens. A typical tool with a medium-complexity schema costs 100–300 tokens. A system with 20 tools adds 2,000–6,000 tokens per request—roughly $0.01–$0.06 at current pricing on GPT-4.1. For high-volume applications (millions of requests/day), tool count is a meaningful cost lever. Strategies: remove unused tools, consolidate related tools into one with an `action` enum parameter, and cache system prompts (Anthropic prompt caching reduces repeated tool definition costs by ~90%).

## Parallel Tool Calls: 3.7x Latency Improvement in Practice

Parallel tool calls are the single highest-impact performance optimization for agentic systems. The LLMCompiler paper (ICML 2024) demonstrated up to 3.7x latency reduction by executing independent tool calls concurrently rather than waiting for each to complete before starting the next. All three major providers return multiple tool call objects in a single response when the model determines calls are independent. Your application executes them concurrently using `asyncio.gather` or `ThreadPoolExecutor`, then returns all results in a single follow-up request. The model sees all results simultaneously and synthesizes a final answer. The pattern requires identifying which tool calls truly are independent—calls where output B depends on output A must remain sequential. The model usually gets this right, but you should validate in production and implement timeout handling so a slow tool doesn't block all parallel results.

```python
import asyncio
import json
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def execute_tool(call):
    args = json.loads(call.function.arguments)
    if call.function.name == "get_weather":
        await asyncio.sleep(0.1)  # Simulated API call
        return {"temperature": 22, "city": args["city"]}
    if call.function.name == "get_stock_price":
        await asyncio.sleep(0.15)
        return {"price": 150.5, "symbol": args["symbol"]}
    return {}

async def run_parallel_tools():
    response = await client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Weather in NYC and AAPL stock price?"}],
        tools=tools  # Define your tools array here
    )

    message = response.choices[0].message
    if message.tool_calls:
        results = await asyncio.gather(
            *[execute_tool(call) for call in message.tool_calls]
        )
        tool_messages = [
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            }
            for call, result in zip(message.tool_calls, results)
        ]

        final = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": "Weather in NYC and AAPL stock price?"},
                message,
                *tool_messages
            ]
        )
        return final.choices[0].message.content

asyncio.run(run_parallel_tools())
```

## Multi-Step Agent Loops: Building Production-Ready Systems

A multi-step agent loop runs the tool call / result cycle until the model produces a final answer with no pending tool calls. Every production agent needs three safeguards that most tutorials skip: a **maximum iteration limit** (prevents infinite loops from hallucinated or broken tools), **timeout handling** (prevents one slow external API from hanging the entire agent), and **loop detection** (prevents the model from calling the same tool with the same arguments repeatedly). A reasonable production ceiling is 15 iterations with a 30-second per-tool timeout and a 120-second total loop timeout. Beyond these hard limits, implement soft controls: log every tool call with arguments and results, alert on loops that exceed 8 iterations (usually indicates a confused model or broken tool), and expose a kill switch for human override.

```python
import json
import time
from openai import OpenAI

client = OpenAI()
MAX_ITERATIONS = 15
LOOP_TIMEOUT = 120

def run_agent(user_message: str, tools: list, tool_registry: dict) -> str:
    messages = [{"role": "user", "content": user_message}]
    start_time = time.time()
    seen_calls = set()

    for iteration in range(MAX_ITERATIONS):
        if time.time() - start_time > LOOP_TIMEOUT:
            return "Agent timeout: exceeded 120 seconds"

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason != "tool_calls":
            return message.content

        for call in message.tool_calls:
            call_key = f"{call.function.name}:{call.function.arguments}"
            if call_key in seen_calls:
                return "Loop detected: same tool called with same args twice"
            seen_calls.add(call_key)

            func = tool_registry.get(call.function.name)
            if not func:
                result = f"Error: unknown function {call.function.name}"
            else:
                try:
                    args = json.loads(call.function.arguments)
                    result = json.dumps(func(**args))
                except Exception as e:
                    result = f"Error: {e}"

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

    return "Agent exceeded maximum iterations"
```

## Error Handling: Malformed Arguments, Hallucinated Functions, and Recovery

Production function calling systems fail in four distinct ways, each requiring a different recovery strategy. **Malformed arguments** occur when the model generates JSON that doesn't validate against your schema—use Pydantic validation and return a structured error string (not an exception) so the model can retry with corrected arguments. **Hallucinated function names** happen when the model calls a function that doesn't exist in your registry—detect with a dictionary lookup and return `"Error: unknown function X"` to prompt self-correction. **Timeout failures** occur when external APIs are slow—implement per-call timeouts with `asyncio.wait_for` and return a timeout error string so the model can acknowledge the failure. **Unexpected results** happen when a function returns data in an unexpected format—validate outputs before returning them to the model and normalize structure. One critical rule: never raise a Python exception inside the tool execution path of an agent loop. Always catch exceptions, convert to error strings, and return them as tool results. This keeps the conversation alive and gives the model a chance to recover or escalate to the user.

```python
from pydantic import BaseModel, ValidationError
import asyncio

class WeatherArgs(BaseModel):
    city: str
    unit: str = "celsius"

async def safe_execute_tool(name: str, arguments: str, timeout: float = 10.0) -> str:
    validators = {"get_weather": WeatherArgs}

    if name not in tool_registry:
        return f"Error: unknown function '{name}'"

    try:
        args_dict = json.loads(arguments)
    except json.JSONDecodeError as e:
        return f"Error: invalid JSON arguments — {e}"

    if name in validators:
        try:
            validated = validators[name](**args_dict)
            args_dict = validated.dict()
        except ValidationError as e:
            return f"Error: argument validation failed — {e}"

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(tool_registry[name], **args_dict),
            timeout=timeout
        )
        return json.dumps(result)
    except asyncio.TimeoutError:
        return f"Error: {name} timed out after {timeout}s"
    except Exception as e:
        return f"Error: {name} raised {type(e).__name__}: {e}"
```

## Security First: Prompt Injection, OWASP LLM06, and Authorization

Function calling is OWASP LLM06 (Excessive Agency)—the primary attack vector is prompt injection via tool arguments. An attacker embeds instructions in data your tool retrieves (a web page, a database record, an email), and the model executes those instructions as if they came from the user. Defense requires three layers. First, **input sanitization**: strip HTML and markdown from tool results before returning them to the model. Second, **authorization checks**: validate that the current user has permission to call high-privilege tools before executing—never trust the model's decision alone. Third, **audit logging**: record every tool call with the user identity, arguments, and result. For destructive operations (database writes, API calls that spend money, emails), require explicit human approval rather than autonomous execution. Implement a confirmation step where the model proposes the action, your system presents it to the user, and only executes after explicit approval. OWASP also recommends a principle of least privilege: expose only the minimum tool set needed for a given session, not all available tools at once.

```python
import hashlib
import time

AUDIT_LOG = []

def authorized_tool_call(user_id: str, tool_name: str, args: dict, 
                          user_permissions: set) -> tuple[bool, str]:
    tool_permissions = {
        "get_weather": set(),           # Public
        "read_database": {"db_read"},   # Requires permission
        "write_database": {"db_write"}, # Requires elevated permission
        "send_email": {"email_send"},   # Requires explicit permission
    }
    required = tool_permissions.get(tool_name, {"admin"})
    if not required.issubset(user_permissions):
        return False, f"Unauthorized: {tool_name} requires {required}"

    # Sanitize arguments to prevent injection
    sanitized = {}
    for k, v in args.items():
        if isinstance(v, str):
            import re
            v = re.sub(r'<[^>]+>', '', v)   # Strip HTML
            v = re.sub(r'\[.*?\]\(.*?\)', '', v)  # Strip markdown links
        sanitized[k] = v

    AUDIT_LOG.append({
        "timestamp": time.time(),
        "user_id": user_id,
        "tool": tool_name,
        "args_hash": hashlib.sha256(json.dumps(sanitized).encode()).hexdigest(),
        "authorized": True
    })
    return True, json.dumps(sanitized)
```

## Production Best Practices: Validation, Logging, and Cost Tracking

Production function calling deployments need observability that most prototypes skip. Track these four metrics for every tool call in production: **latency** (time from tool call detection to result return), **error rate** (fraction of calls that return error strings), **token cost** (input tokens for tool definitions × requests per day), and **iteration depth** (how many loops agent runs require—outliers indicate confused models). Build cost tracking from the start: `tool_definition_tokens × requests × price_per_token` adds up at scale. A system with 10 tools averaging 200 tokens each running 1M requests/day at $0.015/1K tokens spends $30/day on tool definitions alone—before the actual conversation tokens. Tool description quality directly affects both accuracy and cost: precise descriptions reduce the number of retries and multi-step loops needed. Keep descriptions under 200 characters, use active voice ("Returns weather data for a city"), and include one concrete example in the `description` field when behavior isn't obvious.

## Future Trends: MCP Standardization and What's Coming in 2027

Model Context Protocol (MCP) is the emerging standard for tool definitions that work across providers without per-provider schema translation. Anthropic released MCP as an open protocol in late 2024, and by mid-2026 OpenAI and Google have both announced MCP compatibility in their roadmaps. MCP moves tool definitions out of your API request and into a standardized server that any MCP-compatible model can query at runtime. Instead of embedding 20 tool schemas in every request (paying 3,000+ tokens each time), an MCP server hosts them and the model fetches only what it needs. This will significantly reduce the per-request token cost of large tool libraries. Server-side tools (Anthropic's current built-in web_search and code_execution) will expand across providers—expect Google and OpenAI to offer managed retrieval and execution environments by 2027. Streaming argument generation (currently Gemini-exclusive) will become universal, enabling real-time UI feedback during complex multi-tool agent runs.

## Decision Framework: Function Calling vs Structured Outputs vs MCP

Choosing the right tool-integration pattern depends on three questions. **Do you need the model to decide when to call an external system?** If yes, use function calling—the model controls invocation. If you just need the output in a specific JSON format, use structured outputs instead (cheaper, simpler, no execution loop). **Do you need execution to happen inside the API without your infrastructure?** If yes, use Anthropic's server-side tools for web search and code execution. **Do you need to share tool definitions across multiple models or teams?** If yes, use MCP to define tools once and expose them to any compatible model. A common mistake is using function calling when structured outputs would suffice—if you're extracting entities from text or generating a form response, structured outputs give you the same schema guarantees at lower cost and complexity. Reserve function calling for cases where you genuinely need the model to call external systems based on dynamic reasoning.

| Use Case | Recommended Pattern |
|----------|-------------------|
| Extract structured data from text | Structured outputs |
| Query a live external API | Function calling |
| Web search without your infrastructure | Anthropic server-side tools |
| Cross-provider tool sharing | MCP |
| Real-time UI with streaming args | Google Gemini 2.5+ |
| Guaranteed schema compliance | OpenAI strict mode |
| Parallel independent queries | All providers (use asyncio) |

## FAQ

**Does function calling work with all models or just the most expensive ones?**
All major paid-tier models from OpenAI (GPT-4.1, GPT-4o mini), Anthropic (Claude Haiku, Claude Sonnet, Claude Opus), and Google (Gemini 1.5 Flash, Gemini 2.5 Pro) support function calling. Smaller/cheaper models like GPT-4o mini and Claude Haiku support it well for simple single-tool use cases. For complex multi-step agent loops with many tools, frontier models (GPT-4.1, Claude Opus 4.7, Gemini 2.5 Pro) are significantly more reliable at choosing the right tools and arguments.

**Can I use function calling with streaming responses?**
Yes, with caveats. OpenAI and Anthropic both support streaming with function calls—tool call arguments stream as tokens, letting you start processing before the argument JSON is complete. Google Gemini 2.5+ streams function call arguments natively. The practical complexity is that you must buffer the argument stream and parse the complete JSON before executing—streaming doesn't help with execution latency, only with time-to-first-token of the argument.

**How do I prevent the model from calling tools it shouldn't?**
Use `tool_choice` (OpenAI), `tool_choice` with `{"type": "none"}` (Anthropic), or remove the tool from the tools array entirely. Removing tools from the request is the most reliable approach for session-level restrictions because it's enforced by the API rather than relying on model compliance. For operation-level restrictions (allow tool X for read operations but not write), implement authorization checks in your execution layer—never trust the model to enforce permissions.

**What's the maximum number of tools I can include in a request?**
OpenAI supports up to 128 tools per request. Anthropic supports a similar number (documented limit varies by model). Google Gemini's limit is lower and varies by model generation. In practice, you should stay well below these limits for cost and reliability reasons: more than 20–30 tools significantly increases both token costs and the likelihood of the model choosing the wrong tool. If you genuinely need more, use tool routing—a classifier model or heuristic that selects a relevant subset of tools for each request.

**How do I handle functions that take a long time to execute?**
Use async execution with explicit timeouts. Set a per-tool timeout (typically 10–30 seconds) and a total agent loop timeout (60–120 seconds). When a timeout occurs, return a timeout error string as the tool result—don't let the exception propagate. The model can then decide to retry, use a different approach, or report the failure to the user. For genuinely long operations (batch jobs, file processing), return a job ID immediately and provide a separate `check_job_status` tool the model can poll in subsequent turns.