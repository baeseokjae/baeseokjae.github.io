---
cover:
  alt: 'MCP Server Tutorial 2026: Build Your First Model Context Protocol Server'
  image: /images/mcp-server-tutorial-2026.png
  relative: false
date: 2026-04-16 04:08:44+00:00
description: 'Step-by-step MCP server tutorial: build, test, and deploy your first
  Model Context Protocol server using Python FastMCP or TypeScript in 2026.'
draft: false
schema: schema-mcp-server-tutorial-2026
tags:
- MCP
- Model Context Protocol
- AI development
- Python
- TypeScript
- tutorial
title: 'MCP Server Tutorial 2026: Build Your First Model Context Protocol Server'
---

You can build a working MCP server with 2–3 tools in under 30 minutes using Python FastMCP. This tutorial walks through every step — from installing the SDK to testing with MCP Inspector and deploying locally or to a remote server.

## What Is MCP and Why Does It Matter in 2026?

MCP (Model Context Protocol) is an open standard created by Anthropic in November 2024 that defines how AI models connect to external tools, data sources, and services. Before MCP, every AI integration was a bespoke REST API wrapper — each model provider invented its own function-calling format, and every tool had to be re-implemented per-client. MCP standardizes this: you build a server once, and any MCP-compatible client (Claude, Cursor, VS Code Copilot, custom agents) can discover and call your tools automatically. By early 2026, over 5,000 MCP servers are publicly available, and Anthropic, OpenAI, and Google have all committed to the protocol. The shift parallels what LSP (Language Server Protocol) did for editor tooling — one interface, many clients. If you're building AI tooling in 2026, MCP is the integration layer you ship to.

## Why Build an MCP Server? Key Benefits and Use Cases

Building an MCP server exposes your capabilities to AI agents in a way that REST APIs alone cannot. An MCP server speaks the language AI clients expect — structured tool definitions with typed schemas, resource listings, and reusable prompt templates — so clients can discover what you offer without reading documentation. By April 2026, over 1,800 MCP servers are listed in public directories, covering everything from database access to payment processing. The core use cases are: (1) **wrapping internal APIs** so Claude or Cursor can query your services directly, (2) **exposing database read/write tools** to agents running automated workflows, (3) **building specialized agents** that combine multiple data sources under one server, and (4) **integrating dev tools** (GitHub, Jira, Slack) into coding assistants. The decisive advantage over REST: AI clients can introspect your tool schemas at runtime, so there's no separate documentation step — the model learns what your server can do by asking.

## MCP Architecture Deep Dive: Tools, Resources, Prompts

An MCP server exposes three primitive types: Tools, Resources, and Prompts. Understanding these before writing code saves significant refactoring later.

**Tools** are the most common primitive — functions the model can call with structured arguments. Each tool has a name, description (shown to the model), and a JSON Schema for its input parameters. The model decides when to call a tool based on your description, so tool descriptions are part of your API surface. A weather lookup tool might be: `get_weather(city: str) -> dict`. Tools are the right primitive for anything that performs an action or returns computed results.

**Resources** are read-only data sources the client can query. A PostgreSQL database, a file system, or a documentation corpus are natural resources. Resources use URI templates (`postgres://mydb/users/{id}`) and return structured or unstructured content. They're closer to GET endpoints than function calls — no side effects expected.

**Prompts** are reusable prompt templates with arguments. A `summarize_pr` prompt might take a PR number and return a structured system+user message pair. This primitive is underused in 2026 but powerful for building consistent agent behaviors across clients.

The transport layer connects clients to your server. **STDIO** transport (local subprocess communication) has ~1ms latency and is the default for local tools embedded in editors. **Streamable HTTP** (formerly SSE) targets remote deployments and adds 10–100ms overhead but works across network boundaries. Choose STDIO for local dev tools; choose HTTP for multi-tenant SaaS or cloud agents.

### The JSON-RPC Layer Under the Hood

MCP uses JSON-RPC 2.0 as its wire format. Every tool call is a `tools/call` request; tool discovery is `tools/list`. You rarely interact with this directly — the SDKs handle it — but understanding it helps when debugging connection issues. The MCP Inspector (covered later) exposes raw JSON-RPC messages, which is invaluable when something goes wrong.

## Choosing Your SDK: Python FastMCP vs TypeScript vs Go

Choosing the right SDK matters more for developer ergonomics than for runtime performance — all four major SDKs (Python, TypeScript, Go, Kotlin) produce spec-compliant servers. The practical choice in 2026 comes down to your existing stack and how quickly you need to ship.

| SDK | Best For | Tool Definition Style | Maturity |
|---|---|---|---|
| **Python FastMCP** | Data/ML workloads, scripting | `@mcp.tool()` decorator | Stable, most examples |
| **TypeScript** | Node.js backends, browser tooling | Explicit Zod schemas | Stable, typed end-to-end |
| **Go** | High-concurrency services | Struct-based handlers | Beta, growing |
| **Kotlin** | JVM services, Android | Coroutine-based | Beta |

**Python FastMCP** wins for speed-to-working-server. The decorator API is two lines per tool versus TypeScript's 10+ lines of schema declaration. If you're prototyping or working in a Python-heavy org, start here. **TypeScript** is the right choice if you're already running Node.js infrastructure — you get compile-time validation of your schemas and seamless integration with existing Express or Fastify apps. **Go** is the pick for high-throughput production services where you need goroutine concurrency and predictable memory, but the ecosystem is still catching up as of Q1 2026.

This tutorial uses Python FastMCP for its simplicity, with a TypeScript comparison at the end.

## Step-by-Step Tutorial: Build Your First MCP Server in Python

Building your first MCP server with Python FastMCP takes under 30 minutes if you follow this sequence exactly. FastMCP is the fastest path to a spec-compliant server because it infers tool schemas from Python type annotations and docstrings — you write normal Python functions and the framework handles JSON-RPC registration, schema generation, and transport setup automatically. This tutorial builds a server with two tools: a safe mathematical expression evaluator and an async currency exchange rate lookup that calls an external API. By the end, you'll have a server you can connect to Claude Desktop, MCP Inspector, or any MCP-compatible agent framework. The same patterns — decorated functions, typed parameters, structured return values — scale to production database servers and multi-tool agent backends. All code is self-contained and runs with Python 3.10+ and a single `pip install`.

### Prerequisites

- Python 3.10+
- `pip` or `uv`
- Node.js 18+ (for MCP Inspector)

### Step 1: Install FastMCP

```bash
pip install fastmcp
# or with uv (recommended):
uv add fastmcp
```

FastMCP is a third-party framework built on top of the official Anthropic `mcp` Python SDK. It reduces boilerplate dramatically — the official SDK requires manual schema registration; FastMCP infers schemas from Python type annotations.

### Step 2: Create the Server File

Create `server.py`:

```python
from fastmcp import FastMCP
import httpx

mcp = FastMCP("my-first-server")

@mcp.tool()
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    Examples: '2 + 2', '10 * 3.14', '(100 / 4) ** 2'
    """
    try:
        # Use eval with restricted builtins — no imports allowed
        allowed = {"__builtins__": {}}
        result = eval(expression, allowed)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
async def get_exchange_rate(base: str, target: str) -> dict:
    """
    Get the current exchange rate between two currencies.
    Args:
        base: Source currency code (e.g., 'USD')
        target: Target currency code (e.g., 'EUR')
    Returns dict with rate and timestamp.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.exchangerate-api.com/v4/latest/{base.upper()}"
        )
        data = resp.json()
        rate = data["rates"].get(target.upper())
        if rate is None:
            return {"error": f"Unknown currency: {target}"}
        return {
            "base": base.upper(),
            "target": target.upper(),
            "rate": rate,
            "date": data["date"],
        }

if __name__ == "__main__":
    mcp.run()
```

Key points: FastMCP extracts the tool name from the function name, the description from the docstring, and the input schema from the type annotations. `str`, `int`, `float`, `dict`, `list`, and `Optional[T]` all map to JSON Schema types automatically.

### Step 3: Run the Server

```bash
python server.py
```

With no arguments, FastMCP runs in STDIO mode — the server reads JSON-RPC messages from stdin and writes responses to stdout. This is exactly what MCP clients expect for subprocess-style integration.

**Critical pitfall**: Never write to stdout yourself (no `print()` statements in your tool code). Stdout is the MCP transport channel. Use `stderr` for debug output or FastMCP's built-in logging:

```python
import sys
print("debug message", file=sys.stderr)  # OK
print("debug message")  # BREAKS the transport
```

### Step 4: Add the Server to Claude Desktop (Optional)

If you have Claude Desktop installed, add your server to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "my-first-server": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop. Your tools now appear in every conversation.

### TypeScript Equivalent for Comparison

The same server in TypeScript (using the official `@modelcontextprotocol/sdk`):

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-first-server", version: "1.0.0" });

server.tool(
  "calculate",
  "Evaluate a mathematical expression safely.",
  { expression: z.string().describe("Math expression like '2 + 2'") },
  async ({ expression }) => {
    // safe eval implementation
    return { content: [{ type: "text", text: "result" }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

TypeScript requires explicit Zod schema definitions per parameter — more verbose but catches type mismatches at compile time. For teams shipping production TypeScript services, this trade-off is worth it.

## Testing with MCP Inspector: Interactive Development Workflow

MCP Inspector is the official browser-based debugging tool for MCP servers, maintained by Anthropic as part of the core SDK. It connects directly to your server and exposes a full testing UI where you can discover tools, call them with custom arguments, inspect raw JSON-RPC messages, and verify resource and prompt registrations — all without writing a single line of client code. In practice, Inspector eliminates the cycle of "start Claude Desktop, restart, test, repeat" that slows local development to a crawl. Instead: run your server through Inspector's proxy, open the browser, call your tools, iterate. A typical development session catches schema issues, missing error handling, and malformed responses in minutes rather than hours. As of April 2026, MCP Inspector supports all transport modes (STDIO and HTTP) and all three MCP primitives. It's the single most important tool in the MCP developer workflow — use it before every deployment.

Installing and running MCP Inspector takes under two minutes. Run your server via Inspector's proxy: `npx @modelcontextprotocol/inspector python server.py`. This starts a local web UI (default: `http://localhost:5173`) with three panels: server connection status, tool list (auto-populated from your `tools/list` response), and a call interface where you can set arguments and execute tools.

### What to Check in Every Testing Session

**Tool discovery**: After connecting, click "List Tools." You should see all your tools with their descriptions and parameter schemas exactly as defined. If a tool is missing or shows wrong schema, check your type annotations or decorators.

**Happy-path calls**: Call each tool with valid input. Verify response structure matches what you expect. For the calculator: input `"2 + 2"`, expect `"4"`.

**Error handling**: Test with invalid input — empty strings, wrong types, out-of-range values. Your server should return structured error messages, not crash.

**Raw JSON-RPC view**: Toggle the inspector's "Show raw messages" option to see the actual JSON-RPC request/response pairs. This is essential when debugging schema issues — you can see exactly what the client sends and what your server returns.

MCP Inspector also tests Resources and Prompts if your server exposes them. Run a full test pass before every deployment.

## Deploying Your Server: Local vs Remote Options

Choosing between local (STDIO) and remote (Streamable HTTP) deployment is one of the more consequential architectural decisions when building an MCP server, because it affects latency, multi-tenancy, authentication, and how clients discover and connect to your server.

**Local STDIO deployment** runs your server as a child process managed by the client. Latency is ~1ms. Setup is minimal: the client config points to your executable. This is the right choice for developer tools that live on a single machine — Cursor plugins, CLI helpers, local database inspectors. The downside: every user installs and runs the binary themselves; no centralized management.

**Remote Streamable HTTP deployment** exposes your server over HTTP. The client connects to a URL like `https://api.yourservice.com/mcp`. This model supports multi-tenant SaaS (one server instance, many users), cloud-hosted agents, and scenarios where the server needs access to infrastructure that users shouldn't touch (internal databases, credentials). The trade-off is complexity: you manage authentication, connection state, and deployment.

### Deploying to HTTP with FastMCP

```python
# server_http.py
from fastmcp import FastMCP

mcp = FastMCP("my-first-server")

# ... tool definitions same as before ...

if __name__ == "__main__":
    # Run as HTTP server on port 8000
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

For production, add authentication middleware. FastMCP supports standard ASGI middleware — wrap with an API key check:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        key = request.headers.get("x-api-key")
        if key != "your-secret-key":
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)

mcp.app.add_middleware(APIKeyMiddleware)
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server_http.py .
EXPOSE 8000
CMD ["python", "server_http.py"]
```

Build and run: `docker build -t my-mcp-server . && docker run -p 8000:8000 my-mcp-server`. For Kubernetes deployments, treat your MCP server like any stateless HTTP service — horizontal scaling works out of the box because MCP connections are request-scoped, not persistent.

## Advanced Patterns: Database Integration and Production Readiness

Production MCP servers serving real agent workflows need more than basic tool definitions — they need connection pooling, observability, rate limiting, and graceful error handling. This section covers the patterns that separate a weekend prototype from a production-grade server.

The most common production use case is wrapping a PostgreSQL (or any SQL) database so agents can query it directly. Here is a complete example using `asyncpg`:

```python
import asyncpg
from fastmcp import FastMCP
from typing import Optional
import os

mcp = FastMCP("postgres-server")
pool: Optional[asyncpg.Pool] = None

@mcp.on_startup()
async def startup():
    global pool
    pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        min_size=5,
        max_size=20,
    )

@mcp.on_shutdown()
async def shutdown():
    if pool:
        await pool.close()

@mcp.tool()
async def query_users(email_filter: Optional[str] = None) -> list[dict]:
    """
    Query users from the database.
    Args:
        email_filter: Optional email substring to filter by (e.g. '@acme.com')
    Returns list of user records (id, email, created_at).
    """
    async with pool.acquire() as conn:
        if email_filter:
            rows = await conn.fetch(
                "SELECT id, email, created_at FROM users WHERE email ILIKE $1 LIMIT 100",
                f"%{email_filter}%",
            )
        else:
            rows = await conn.fetch(
                "SELECT id, email, created_at FROM users LIMIT 100"
            )
        return [dict(row) for row in rows]
```

**SQL injection note**: always use parameterized queries (`$1`, `$2`) — never string-format user input into SQL. MCP tool arguments come from AI model outputs, which can be adversarially crafted via prompt injection.

### Adding OpenTelemetry Observability

Instrument your server with OpenTelemetry to track which tools are called, with what arguments, and how long they take:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer("mcp-server")

@mcp.tool()
async def query_users(email_filter: Optional[str] = None) -> list[dict]:
    with tracer.start_as_current_span("query_users") as span:
        span.set_attribute("filter", email_filter or "none")
        result = await _do_query(email_filter)
        span.set_attribute("result_count", len(result))
        return result
```

This integrates with Grafana, Jaeger, or any OTLP-compatible backend and gives you full visibility into agent behavior in production.

### Rate Limiting

Agents can call tools in tight loops. Protect expensive operations with a token bucket:

```python
import asyncio
import time

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.rate = calls_per_minute / 60
        self.tokens = calls_per_minute
        self.last_update = time.monotonic()

    async def acquire(self):
        now = time.monotonic()
        self.tokens = min(
            self.tokens + (now - self.last_update) * self.rate,
            60.0,
        )
        self.last_update = now
        if self.tokens < 1:
            await asyncio.sleep((1 - self.tokens) / self.rate)
        self.tokens -= 1

limiter = RateLimiter(calls_per_minute=30)

@mcp.tool()
async def expensive_operation(query: str) -> dict:
    """Run an expensive external API call."""
    await limiter.acquire()
    # ... do work ...
```

## Common Pitfalls and Best Practices

Building your first MCP server surfaces a predictable set of mistakes. Here is what developers commonly get wrong, and the fixes that save hours of debugging.

**Pitfall 1: Writing to stdout breaks the transport.** Every `print()` in your server code corrupts the STDIO channel. The client sees garbage JSON and disconnects. Fix: use `logging` with a `StreamHandler` pointing to `sys.stderr`, or use FastMCP's built-in `mcp.logger`.

**Pitfall 2: Vague tool descriptions hurt model performance.** The model decides when to call your tool based solely on its description. A description like "Does stuff with data" is useless. Write descriptions like a senior dev explaining the function to a new teammate: include the precondition, what it returns, and any important limits. The extra 20 words in a description can double tool call accuracy.

**Pitfall 3: Over-broad tools create ambiguity.** A single `query_database(sql: str)` tool sounds convenient but forces the model to write raw SQL, handle escaping, and guess your schema. Instead, expose narrow, purpose-built tools: `get_user_by_email`, `list_recent_orders`, `search_products`. Narrow tools mean fewer model errors.

**Pitfall 4: Missing error returns.** If your tool raises an unhandled exception, the MCP client receives a protocol-level error with no detail. Always catch exceptions and return structured error info: `return {"error": "user_not_found", "message": f"No user with id {user_id}"}`. The model can read this and decide what to do next.

**Pitfall 5: Not validating tool output size.** MCP responses are passed directly into the model's context window. A tool that returns 500KB of database rows will blow the context limit. Enforce pagination: always cap results at 100 rows, add a `cursor` parameter for pagination, and document the limits in the tool description.

**Best practice: version your tools.** Use the server version string and include it in error messages. When you change a tool's behavior, bump the version. Agent workflows that depend on your server need to know when the contract changes.

## Future of MCP: Trends and Predictions for 2027

The MCP ecosystem is accelerating fast, and the trajectory through 2026 points to three converging shifts that will shape what you build next year. First, **remote MCP registries** are emerging as the distribution layer for AI tools — think npm for MCP servers. By Q3 2026, several competing registries have launched, and Anthropic is expected to standardize a discovery protocol so clients can auto-install servers from a central index. Second, **multi-agent MCP chaining** — where one MCP server calls tools on other MCP servers — is becoming a first-class pattern. The spec now supports agent-to-agent tool calls, enabling complex workflows like "research agent calls web-search server, passes results to summarization server, posts to Slack via another server," all coordinated through MCP. Third, **authentication and authorization** are getting standardized: the MCP spec's OAuth integration (currently in draft) will let servers declare required scopes and clients handle token flows automatically, removing the bespoke auth plumbing every production server currently needs.

For developers building now: invest in clean tool schemas, good descriptions, and narrow tool surfaces. The model quality improvements coming in 2026–2027 amplify the quality of your tool interface — a well-described tool will be called correctly more often as models improve, but a vague tool description remains a liability regardless of model version.

## FAQ

These are the questions developers most commonly ask when building their first MCP server. Each answer is self-contained — you don't need to read the full article to use them. Topics cover SDK selection, primitive types, testing workflow, transport layer differences, and security. If you're new to MCP, start with the tool vs. resource vs. prompt distinction (question 2) and the STDIO vs. HTTP transport choice (question 4) — these two decisions shape everything else in your server design. For production deployments, pay close attention to the SQL injection answer (question 5): MCP tool arguments flow from AI model outputs and require the same defensive handling as user-supplied HTTP input. The MCP spec is evolving rapidly; check the official Anthropic SDK changelog for breaking changes before upgrading FastMCP or the TypeScript SDK in an active deployment.

### What language should I use to build an MCP server in 2026?

Python with FastMCP is the fastest path to a working server — you can ship 2–3 tools in under 30 minutes with minimal boilerplate. Use TypeScript if your existing backend is Node.js, since you get compile-time schema validation and seamless integration with Express or Fastify. Go is the right choice for high-concurrency production services, but the SDK ecosystem is still maturing as of Q1 2026. Start with Python unless you have a specific reason to choose otherwise.

### What is the difference between MCP tools, resources, and prompts?

**Tools** are callable functions the model can invoke with arguments — think POST endpoints. **Resources** are read-only data sources the client can query by URI, like GET endpoints with no side effects. **Prompts** are reusable message templates with parameters that produce structured system/user message pairs. Most servers only need Tools; add Resources if you're exposing queryable datasets, and Prompts if you want to standardize how the model approaches specific workflows.

### How do I test my MCP server without integrating it into Claude?

Use MCP Inspector: `npx @modelcontextprotocol/inspector python server.py`. This opens a browser UI where you can discover tools, set arguments, call them, and see raw JSON-RPC messages. It's the official testing tool from Anthropic and supports all three primitives (Tools, Resources, Prompts). Run every new tool through Inspector before adding it to a client.

### What is the difference between STDIO and HTTP transport in MCP?

STDIO transport runs your server as a local subprocess with ~1ms latency — best for developer tools on a single machine (Cursor plugins, CLI tools). HTTP transport (Streamable HTTP) exposes your server over a URL, enables multi-tenant deployments, and works across network boundaries at 10–100ms latency. Choose STDIO for local tools; choose HTTP when multiple users or cloud agents need to reach your server.

### How do I prevent SQL injection in an MCP database server?

Always use parameterized queries, never string-format user input into SQL. In `asyncpg`: use `conn.fetch("SELECT ... WHERE id = $1", user_id)`. In `psycopg2`: use `cursor.execute("SELECT ... WHERE id = %s", (user_id,))`. MCP tool arguments come from AI model outputs, which can be adversarially manipulated via prompt injection — treat them with the same distrust as user-supplied HTTP input. Add input validation (check types, enforce length limits) before passing anything to a database query.