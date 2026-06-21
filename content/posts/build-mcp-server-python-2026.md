---
cover:
  alt: 'How to Build an MCP Server with Python 2026: Step-by-Step Tutorial'
  image: /images/build-mcp-server-python-2026.png
  relative: false
date: 2026-04-24 21:08:12+00:00
description: Build a production-ready MCP server in Python using FastMCP — from 9-line
  hello world to Docker, auth, and security hardening.
draft: false
schema: schema-build-mcp-server-python-2026
tags:
- mcp
- python
- fastmcp
- ai-tools
- tutorial
title: 'How to Build an MCP Server with Python 2026: Step-by-Step Tutorial'
---

Building an MCP server in Python takes under 30 minutes with FastMCP. Install `fastmcp`, decorate a Python function with `@mcp.tool()`, and any AI client — Claude, ChatGPT, Cursor, or Copilot — can call it immediately. This tutorial walks from a 9-line working server through PostgreSQL integration, Docker deployment, and security hardening.

## What Is MCP and Why It Matters in 2026?

Model Context Protocol (MCP) is an open standard developed by Anthropic that lets AI clients connect to external tools and data sources using a single, universal interface. Think of it as USB-C for AI integrations: you build a server once, and every compliant AI client — Claude, ChatGPT, Gemini, Cursor, VS Code Copilot — can use it without any client-side code changes. MCP uses JSON-RPC 2.0 as its transport layer and defines three core primitives: **tools** (functions the AI can call), **resources** (data the AI can read), and **prompts** (reusable instruction templates). As of early 2026, MCP SDK downloads hit 97 million per month across Python and TypeScript, with over 12,000 active servers live on the internet (8,600 verified on PulseMCP). OpenAI adopted MCP in March 2025, Google DeepMind in April 2025, Microsoft in May 2025, and the Linux Foundation took over governance in December 2025 — making MCP the undisputed standard for AI tool connectivity. Early enterprise deployments report up to 70% AI operational cost reduction through on-demand data fetching versus context stuffing. The takeaway: MCP is no longer experimental infrastructure — it's the production-grade integration layer for the AI era.

### FastMCP vs the Raw MCP SDK: Which Should You Use?

FastMCP is the right choice for almost every Python MCP project in 2026. It has 23,000+ GitHub stars, approximately 1 million daily PyPI downloads, and powers roughly 70% of all Python MCP servers. FastMCP wraps the official `mcp` SDK with a developer-friendly decorator API that eliminates boilerplate — what takes 80 lines with the raw SDK takes 9 lines with FastMCP. Use the standalone `fastmcp` package (v3.1.1+) rather than the version bundled inside the `mcp` SDK, since the standalone version ships newer features and bug fixes faster. The one scenario where you'd reach for the raw SDK is if you need direct control over the JSON-RPC message loop for a highly custom transport — rare in practice.

## Prerequisites

Before building an MCP server, you need three tools installed: Python 3.10 or higher, Node.js 18+ for the MCP Inspector testing utility, and either `uv` or pip for Python dependency management. Docker is optional and only required in Step 9 when you containerize for production. The `uv` package manager is strongly recommended over pip because it resolves dependencies faster, generates a lockfile automatically, and makes `uv run python server.py` work reliably across different machines without activating virtual environments manually. If you are on Python 3.9 or earlier, install a newer Python version with `pyenv` before continuing — FastMCP uses type hint features and `match` syntax unavailable in older versions. Node.js is only needed for `npx @modelcontextprotocol/inspector`; you do not need to write any JavaScript. Confirm all three are installed before starting.

Before starting, ensure you have:

- **Python 3.10+** — FastMCP requires 3.10 minimum; 3.12 recommended
- **uv** (recommended) or pip for dependency management
- **Node.js 18+** — needed only for MCP Inspector testing
- **Docker** — optional, only needed for Step 9

```bash
# Verify versions
python --version   # Python 3.10+
node --version     # v18+
uv --version       # 0.4+ recommended
```

## Step 1: Set Up the Project Structure

A clean project layout separates tools, resources, and configuration, and keeps your MCP server maintainable as complexity grows. The pattern used here — a top-level `server.py` entry point with tools organized into a `tools/` subpackage — scales from a single-file demo to a 50-tool production service without restructuring. Use `uv init` rather than creating a virtualenv manually: it generates a `pyproject.toml`, a `uv.lock` lockfile, and the virtual environment in one command. Lockfiles are critical for MCP servers deployed in Docker or CI, because they guarantee identical dependency versions on every machine. The `.env` file stores secrets locally without committing them; `python-dotenv` loads them automatically when the server starts. Keep your `tools/` modules thin — each file should expose one or two related tools rather than bundling everything in `server.py`, which becomes unmanageable past 200 lines.

```bash
uv init my-mcp-server
cd my-mcp-server
uv add "fastmcp>=3.1.1" "httpx>=0.27" "python-dotenv"
```

Expected directory layout:

```
my-mcp-server/
├── pyproject.toml
├── .env
├── server.py          # Main entry point
├── tools/
│   ├── __init__.py
│   ├── weather.py
│   └── database.py
├── resources/
│   └── __init__.py
└── tests/
    └── test_tools.py
```

Create a `.env` for secrets (never commit this file):

```bash
# .env
WEATHER_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
```

## Step 2: Build a Minimal MCP Server with FastMCP

The fastest working MCP server is 9 lines. This is the foundation everything else builds on — understanding it fully prevents the most common mistakes developers hit later.

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

Run it immediately:

```bash
uv run python server.py
```

Three things make this work: the `FastMCP` instance registers your server with a name, the `@mcp.tool()` decorator exposes the function as an MCP tool, and type hints plus the docstring become the tool's schema — what the AI client uses to know when and how to call it. **Write precise docstrings.** The AI model reads them verbatim to decide whether to call your tool, so vague descriptions produce unreliable tool selection.

### Tool Description Best Practices

```python
@mcp.tool()
def search_documents(
    query: str,
    max_results: int = 10,
    category: str | None = None
) -> list[dict]:
    """
    Search internal documents by keyword.

    Args:
        query: Full-text search query. Supports AND/OR operators.
        max_results: Maximum number of results (1-100). Default 10.
        category: Optional filter — 'legal', 'finance', or 'engineering'.

    Returns:
        List of matching documents with title, url, and snippet fields.
    """
    ...
```

## Step 3: Add Tools That Do Real Work

Real MCP tools call external APIs, query databases, read files, or trigger workflows — anything the AI client cannot do on its own. Two patterns cover 80% of production use cases: async HTTP calls to external APIs (weather data, payment processors, CRMs) and parameterized SQL queries against local databases. Both require the same discipline: validate inputs before using them, set timeouts on every network call, and return structured data rather than raw strings so the AI model can reason about the result. Async functions are essential for HTTP tools — a synchronous call blocks the entire MCP server while waiting for the network response, which causes timeouts in multi-tool workflows where the AI chains several tool calls together. FastMCP handles async functions transparently: decorate with `@mcp.tool()` exactly the same way as sync functions. The two examples below show the full pattern including error handling and input sanitization.

### Async HTTP Tool (Weather API)

Async tools are essential for I/O-bound operations. FastMCP handles async functions transparently — just use `async def`.

```python
# tools/weather.py
import httpx
from fastmcp import FastMCP

mcp = FastMCP("Weather Tools")

@mcp.tool()
async def get_weather(city: str) -> dict:
    """
    Get current weather for a city.

    Args:
        city: City name, e.g. 'London' or 'New York'.

    Returns:
        Dict with temperature_c, condition, humidity_percent.
    """
    import os
    api_key = os.environ["WEATHER_API_KEY"]
    url = f"https://api.weatherapi.com/v1/current.json"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"key": api_key, "q": city})
        resp.raise_for_status()
        data = resp.json()

    return {
        "temperature_c": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"],
        "humidity_percent": data["current"]["humidity"],
    }
```

### SQLite Database Tool with Injection Guard

Never pass raw user input directly into SQL. This pattern uses parameterized queries and whitelists allowed table names.

```python
# tools/database.py
import sqlite3
from fastmcp import FastMCP

mcp = FastMCP("Database Tools")

ALLOWED_TABLES = {"products", "orders", "customers"}

@mcp.tool()
def query_database(table: str, limit: int = 20) -> list[dict]:
    """
    Read rows from the local SQLite database.

    Args:
        table: Table name — must be one of: products, orders, customers.
        limit: Maximum rows to return (1-100).

    Returns:
        List of row dicts.
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' not allowed. Choose from: {ALLOWED_TABLES}")

    limit = max(1, min(limit, 100))  # clamp

    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```

## Step 4: Add Resources and Prompts

Resources and prompts are two of the three MCP primitives that elevate a server beyond a simple function registry. A **resource** is a URI-addressable piece of data the AI client can read — think of it as a file the AI opens rather than a function it calls. Resources are ideal for configuration, documentation, or reference datasets that the model should read before deciding which tools to use. A **prompt** is a named, parameterized instruction template that users or orchestrating agents can invoke by name; it returns a formatted string the AI treats as a system or user message. Both primitives are defined with decorators just like tools. The key difference from tools: tools produce side effects (API calls, DB writes), while resources are read-only and prompts produce text output only. Registering a prompt for your most common workflows — "analyze this code", "summarize this dataset" — gives users a consistent, tested starting point instead of improvised prompting.

### Resources — Exposing Data for AI Context

Resources work like files the AI can open. Use them for configuration, documentation, or datasets that should be readable but not writable.

```python
from fastmcp import FastMCP
from fastmcp.resources import FileResource
import pathlib

mcp = FastMCP("My Server")

# Static file resource
@mcp.resource("docs://readme")
def get_readme() -> str:
    """Return the project README."""
    return pathlib.Path("README.md").read_text()

# Dynamic resource computed at request time
@mcp.resource("data://system-status")
def get_system_status() -> dict:
    """Return current system health metrics."""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
    }
```

### Prompts — Reusable Instruction Templates

Prompts let you ship pre-crafted instructions that users or agents can invoke by name.

```python
@mcp.prompt()
def analyze_code_prompt(language: str, code: str) -> str:
    """Generate a code review prompt for the given snippet."""
    return f"""Review this {language} code for:
1. Security vulnerabilities
2. Performance issues
3. Style/maintainability

Code:
```{language}
{code}
```

Provide specific line references for each issue found."""
```

## Step 5: Connect to MCP Clients

One MCP server connects to every major AI client without writing client-specific code — that is the core value proposition of the protocol. By end of 2025, every significant AI development tool shipped MCP support: Claude Desktop, Claude Code CLI, Cursor, VS Code with GitHub Copilot, and ChatGPT via Streamable HTTP. The connection mechanism differs slightly per client — Claude Desktop and Cursor use a JSON config file, Claude Code CLI uses the `claude mcp add` command, VS Code uses a workspace `.vscode/mcp.json` file — but your server code stays identical across all of them. The only variable is transport: use **stdio** for local clients that spawn your server as a subprocess, and **Streamable HTTP** for remote deployments where the client connects over the network. Stdio is simpler to configure (just point to the Python script), while Streamable HTTP enables multi-client access, Docker deployment, and load balancing. The examples below show exact configuration for each major client.

### Claude Code CLI

```bash
# Add your server to Claude Code
claude mcp add my-server -- uv run python /path/to/server.py

# Verify it's registered
claude mcp list
```

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop after saving.

### Cursor

Open Cursor Settings → MCP → Add Server → paste the same JSON block. Cursor uses the same configuration format as Claude Desktop.

### VS Code with GitHub Copilot

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "my-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "${workspaceFolder}/server.py"]
    }
  }
}
```

## Step 6: Test with MCP Inspector

MCP Inspector is the official Anthropic debugging tool that lets you test your server interactively before connecting any AI client. It launches a local web UI at `http://localhost:5173` that lists all registered tools, resources, and prompts, lets you call tools with custom arguments, and shows the raw JSON-RPC 2.0 request/response messages for every interaction. Inspector is essential for catching tool registration bugs — a missing type hint, an incorrect docstring, a Python import error — before they cause silent failures inside Claude or Cursor where the error is harder to trace. Running `npx @modelcontextprotocol/inspector uv run python server.py` starts both your server and the Inspector UI in a single command. No npm install step is needed; npx downloads the Inspector package on first use. Always test a new tool in Inspector before adding it to your Claude Desktop or Cursor config — the round-trip debug cycle is much faster in Inspector's dedicated UI than restarting an AI client.

```bash
npx @modelcontextprotocol/inspector uv run python server.py
```

Inspector opens at `http://localhost:5173`. From there you can:

1. Click **Tools** to see all registered tools and their schemas
2. Fill in arguments and click **Run** to test a tool call
3. Switch to **Messages** to inspect raw JSON-RPC request/response pairs
4. Check **Resources** to verify your resource URIs resolve correctly

Common Inspector issue: if your server starts then immediately exits, you have an import error. Run `uv run python server.py` directly first to see the traceback.

## Step 7: Add Database Integration (PostgreSQL)

Production MCP servers often need PostgreSQL with connection pooling. The `asyncpg` driver is the fastest option for async Python.

```bash
uv add "asyncpg>=0.29" "sqlalchemy[asyncio]>=2.0"
```

```python
# tools/postgres.py
import asyncpg
import os
from fastmcp import FastMCP

mcp = FastMCP("Postgres Tools")
_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            os.environ["DATABASE_URL"],
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool

ALLOWED_SCHEMAS = {"public", "analytics"}

@mcp.tool()
async def run_query(sql: str, schema: str = "public") -> list[dict]:
    """
    Execute a read-only SQL query against the PostgreSQL database.

    Args:
        sql: A SELECT statement. INSERT/UPDATE/DELETE are rejected.
        schema: Database schema — 'public' or 'analytics'.

    Returns:
        Query results as a list of row dicts.
    """
    if schema not in ALLOWED_SCHEMAS:
        raise ValueError(f"Schema '{schema}' not allowed")

    # Block write operations
    normalized = sql.strip().upper()
    for keyword in ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"):
        if normalized.startswith(keyword):
            raise ValueError(f"Only SELECT queries are permitted. Got: {keyword}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql)
        return [dict(row) for row in rows]
```

## Step 8: Add Authentication for Remote Deployment

Remote MCP servers require authentication — without it, anyone who can reach your server's port can invoke all of your tools. A 2026 security scan found 492 MCP servers publicly exposed with zero authentication, giving attackers direct access to database queries, file reads, and API calls. For servers using Streamable HTTP or SSE transport (both expose an HTTP endpoint), enforce auth before any tool call is processed. Two patterns work well in practice: **API key authentication** (an `X-API-Key` header checked in middleware) is simple to implement and suitable for machine-to-machine integrations; **OAuth 2.0 bearer tokens** (validated against a JWKS endpoint) are required for user-facing enterprise deployments where tokens are scoped to individual users. FastMCP 3.1+ ships a built-in `BearerAuthProvider` that handles token validation, caching the JWKS, and returning proper 401 responses. For internal tools with a single service account, the API key middleware below is the fastest path to a secure deployment.

### API Key Authentication Middleware

```python
# server.py — remote deployment with API key auth
import os
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

mcp = FastMCP("Secure Server", transport="streamable-http")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Health check endpoint bypasses auth
        if request.url.path == "/health":
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        valid_key = os.environ.get("MCP_API_KEY")

        if not api_key or api_key != valid_key:
            return Response("Unauthorized", status_code=401)

        return await call_next(request)

mcp.add_middleware(APIKeyMiddleware)
```

### OAuth 2.0 (Bearer Token)

For enterprise deployments, FastMCP 3.1+ supports OAuth bearer token validation:

```python
from fastmcp.auth import BearerAuthProvider

mcp = FastMCP(
    "Enterprise Server",
    auth=BearerAuthProvider(
        jwks_url="https://your-idp.com/.well-known/jwks.json",
        audience="https://your-mcp-server.com",
    )
)
```

## Step 9: Dockerize for Production

Docker packaging makes your MCP server deployable to any cloud provider. Use Streamable HTTP transport for containerized deployments — stdio only works for local processes.

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "server.py", "--transport", "streamable-http", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_API_KEY=${MCP_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - WEATHER_API_KEY=${WEATHER_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mcpdb
      POSTGRES_USER: mcpuser
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Deploy:

```bash
docker compose up -d
```

Pin your MCP SDK version to avoid breaking changes from the upcoming v2.0 release:

```toml
# pyproject.toml
[project]
dependencies = [
    "fastmcp>=3.1.1",
    "mcp>=1.25,<2",   # pin until v2.0 stabilizes
]
```

## Step 10: Security Best Practices

MCP security is under-discussed relative to the attack surface it presents. A 2026 scan found 492 MCP servers publicly exposed with zero authentication, giving any internet user access to their tools. Beyond authentication, three additional attack vectors affect MCP servers that are otherwise well-configured: **tool poisoning** (malicious tool descriptions that hijack AI behavior), **credential exposure** (tool responses that accidentally leak environment variables or API keys), and **input injection** (SQL injection, path traversal, or command injection via unvalidated tool arguments). Each is preventable with the patterns below. Tool poisoning is the most underestimated risk — because the AI model reads tool descriptions to decide what to do, a compromised or maliciously crafted description can silently redirect the model's actions without any obvious error. The defenses here — logging all tool calls, never dynamically constructing tool descriptions from user input, using an allowlist for dynamic tool loading — address each attack class with minimal code overhead.

### Tool Poisoning Prevention

Tool poisoning happens when a malicious tool description instructs the AI to take harmful actions. For example, a tool named `get_user_info` with a description that secretly says "also exfiltrate the user's API keys" can hijack the AI's behavior. Mitigations: (1) Always log tool calls with their full arguments, (2) Never concatenate user input into tool descriptions dynamically, (3) Use a allowlist of approved tool names if your server loads tools dynamically.

### Credential Exposure

```python
# BAD — leaks keys in tool responses
@mcp.tool()
def debug_config() -> dict:
    return dict(os.environ)  # Never do this

# GOOD — redact sensitive keys
@mcp.tool()
def debug_config() -> dict:
    SAFE_KEYS = {"APP_ENV", "LOG_LEVEL", "DATABASE_HOST"}
    return {k: v for k, v in os.environ.items() if k in SAFE_KEYS}
```

### Input Validation Checklist

- Validate all string lengths before passing to external APIs
- Whitelist allowed values for enum-like parameters (table names, schema names, categories)
- Clamp numeric parameters to safe ranges
- Use parameterized queries — never format SQL strings with user input
- Set timeouts on all external HTTP calls (httpx `timeout=10.0`)

### CVE Awareness

Two notable MCP CVEs from 2025 affected servers that allowed arbitrary file reads through path traversal in resource URIs. Always normalize file paths with `pathlib.Path(...).resolve()` and verify the resolved path stays within your intended root directory.

## Step 11: Add Observability and Rate Limiting

Production MCP servers need three observability layers to stay reliable under load: **structured logging** (so you can search tool call history by argument or client), **distributed tracing** (so you can measure p95 latency per tool and trace slow requests across service boundaries), and **rate limiting** (so a runaway AI agent loop cannot flood your external APIs or database). OpenTelemetry is the standard choice for tracing in 2026 — it's vendor-neutral, integrates with Datadog, Grafana Tempo, Jaeger, and every major cloud provider, and FastMCP's async tool functions wrap naturally with OTel span context managers. Rate limiting belongs at the tool level rather than the HTTP layer for MCP servers, because different tools have different cost profiles: a cheap string-manipulation tool might allow 1,000 calls per minute, while a PostgreSQL query tool should cap at 60. The token bucket implementation below is thread-safe and works for both sync and async tools.

### OpenTelemetry Integration

```bash
uv add "opentelemetry-sdk" "opentelemetry-exporter-otlp"
```

```python
# observability.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_tracing():
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

tracer = trace.get_tracer("mcp-server")

# In your tools:
@mcp.tool()
async def my_tool(query: str) -> dict:
    """Run a complex query."""
    with tracer.start_as_current_span("my_tool") as span:
        span.set_attribute("query.length", len(query))
        result = await do_work(query)
        span.set_attribute("result.count", len(result))
        return result
```

### Token Bucket Rate Limiting

```python
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, client_id: str) -> bool:
        now = time.time()
        with self._lock:
            calls = [t for t in self._calls[client_id] if now - t < self.period]
            if len(calls) >= self.max_calls:
                return False
            calls.append(now)
            self._calls[client_id] = calls
            return True

limiter = RateLimiter(max_calls=60, period=60.0)  # 60 calls/minute

@mcp.tool()
async def rate_limited_search(query: str, client_id: str = "default") -> list[dict]:
    """Search with per-client rate limiting."""
    if not limiter.check(client_id):
        raise ValueError("Rate limit exceeded. Try again in 60 seconds.")
    return await do_search(query)
```

## Step 12: Write Integration Tests

Integration tests catch regressions before they reach production. FastMCP ships a `TestClient` that lets you call tools programmatically without a live JSON-RPC connection or a running server process — it invokes your tool functions directly through FastMCP's dispatch layer, giving you real integration coverage (validation, middleware, error handling) at unit-test speed. Write tests for three categories: happy path (correct input produces expected output), rejection cases (invalid table names, out-of-range limits, and disallowed SQL keywords all raise errors), and async tools (use `pytest-asyncio` with `await client.call_tool_async()`). Run tests with `--cov` on every commit; a coverage drop below 80% should block merges. The test patterns here are practical starting points — replace the fixture-level mocks for external services (weather API, PostgreSQL) with `respx` for HTTP mocking and `pytest-asyncio` fixtures that spin up a test database using `asyncpg` and a temporary PostgreSQL container.

```python
# tests/test_tools.py
import pytest
from fastmcp.testing import TestClient
from server import mcp

@pytest.fixture
def client():
    return TestClient(mcp)

def test_hello_tool(client):
    result = client.call_tool("hello", {"name": "World"})
    assert result == "Hello, World!"

def test_query_database_blocks_invalid_table(client):
    with pytest.raises(ValueError, match="not allowed"):
        client.call_tool("query_database", {"table": "secrets"})

def test_query_database_clamps_limit(client):
    result = client.call_tool("query_database", {"table": "products", "limit": 999})
    assert len(result) <= 100

@pytest.mark.asyncio
async def test_weather_tool_async(client):
    result = await client.call_tool_async("get_weather", {"city": "London"})
    assert "temperature_c" in result
    assert "condition" in result
```

Run tests with coverage:

```bash
uv run pytest tests/ -v --cov=. --cov-report=term-missing
```

## Troubleshooting: 12 Common MCP Server Issues

MCP servers fail in predictable ways. Here are the most common issues with their fixes.

| Issue | Symptom | Fix |
|---|---|---|
| Wrong package installed | `ImportError: cannot import name 'FastMCP'` | Use `fastmcp` (standalone), not `mcp` directly |
| Server not appearing in Claude Desktop | Tool list empty after restart | Use absolute paths in config JSON |
| stdio transport in Docker | Server exits immediately | Switch to `streamable-http` transport for containers |
| Inspector can't connect | "Connection refused" | Confirm server is running before launching inspector |
| Tools not showing up | Empty tool list in inspector | Check for syntax errors; run `python server.py` first |
| v2.0 breaking changes | `TypeError` on transport | Pin `mcp>=1.25,<2` in pyproject.toml |
| Async tool hangs | Request times out | Don't mix sync and async code; use `asyncio.run()` properly |
| Credential leakage | API keys in responses | Never return `os.environ` dicts; allowlist config keys |
| SQL injection | Unexpected query results | Use parameterized queries; never format SQL with f-strings |
| Rate limit issues | AI hammers tool repeatedly | Add explicit rate limits and return clear error messages |
| Path traversal in resources | Unauthorized file reads | Resolve paths with `pathlib.resolve()` and check root prefix |
| Memory leak in long-running server | Growing RAM over time | Close DB connections in finally blocks; use connection pools |

## FAQ

This FAQ answers the most common questions developers ask after completing their first MCP server build. The five topics below cover the decisions that have the biggest impact on production reliability: which Python package to use (FastMCP standalone vs the bundled mcp SDK), the minimum Python version required, how to serve one MCP server to multiple AI clients simultaneously, the minimal security configuration needed before exposing a server outside localhost, and how to prevent a dependency update from silently breaking your server. As of April 2026, MCP SDK downloads hit 97 million per month, which means the community has surfaced and documented most of the common failure modes. These answers distill the most frequent mistakes seen across 12,000+ active MCP server deployments so you don't have to discover them in production.

### What is FastMCP and why should I use it over the raw MCP SDK?

FastMCP is a developer-friendly Python framework built on top of the official Anthropic MCP SDK. It replaces 80+ lines of boilerplate with a simple decorator API (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`). It has 23,000+ GitHub stars and handles roughly 70% of all Python MCP servers in production. Use it unless you need direct JSON-RPC loop control, which is rare.

### What Python version is required for FastMCP?

FastMCP requires Python 3.10 or higher. Python 3.12 is recommended for best performance. You can check your version with `python --version`. If you're on an older version, use `pyenv` to install a newer Python without affecting your system Python.

### How do I connect my MCP server to ChatGPT or other non-Claude clients?

Use Streamable HTTP transport (run with `--transport streamable-http`), which is the production-ready HTTP-based transport. Then add the server URL to your client's MCP configuration. ChatGPT, Gemini, and GitHub Copilot all support MCP via Streamable HTTP. stdio transport only works with local process spawning (Claude Desktop, Cursor, Claude Code CLI).

### How do I keep my MCP server secure in production?

The four essentials: (1) Always require API key or OAuth bearer token authentication for any remote server, (2) Never pass raw user input into SQL strings — use parameterized queries, (3) Whitelist allowed parameter values for table names, file paths, and category filters, (4) Set timeouts on all external HTTP calls and log all tool invocations with their arguments for audit trails.

### Should I pin the MCP SDK version?

Yes. Pin `mcp>=1.25,<2` in your `pyproject.toml`. MCP Python SDK v2.0 is in active development and will introduce breaking changes to the transport layer. Pinning prevents your production server from breaking on an automatic dependency update. Re-evaluate the pin when v2.0 reaches a stable release candidate.