---
title: "CrewAI A2A Protocol Tutorial: Build Interoperable Agents with Agent2Agent Support"
date: 2026-04-23T01:23:58+00:00
tags: ["crewai", "a2a-protocol", "multi-agent", "agent-interoperability", "langraph"]
description: "Step-by-step tutorial on using the A2A protocol with CrewAI to build cross-framework multi-agent systems in 2026."
draft: false
cover:
  image: "/images/crewai-a2a-protocol-tutorial-2026.png"
  alt: "CrewAI A2A Protocol Tutorial: Build Interoperable Agents with Agent2Agent Support"
  relative: false
schema: "schema-crewai-a2a-protocol-tutorial-2026"
---

The A2A (Agent2Agent) protocol lets you connect a CrewAI agent to a LangGraph agent — or any other compliant framework — over a standard HTTP interface, with no custom glue code. Setup takes about 15 minutes once your CrewAI environment is running.

## What Is the A2A Protocol?

The A2A (Agent2Agent) protocol is an open HTTP-based standard that defines how AI agents from different frameworks discover each other, exchange tasks, and stream results — without requiring framework-specific integration code. Originally developed by Google and donated to the Linux Foundation in early 2026, A2A is now a vendor-neutral specification backed by Anthropic, Microsoft, Salesforce, and over 50 other organizations. Think of it as the HTTP of multi-agent systems: just as HTTP lets any browser talk to any web server regardless of their underlying technology, A2A lets any compliant agent talk to any other. The protocol uses JSON-RPC 2.0 over HTTPS, supports server-sent events for streaming, and mandates an `/.well-known/agent.json` discovery endpoint so agents can advertise their capabilities. CrewAI adopted A2A as a first-class feature in version 0.80, making it possible to delegate tasks from a CrewAI crew to a LangGraph graph, a Semantic Kernel agent, or a custom Python service — all with a single configuration block. For teams building composite AI systems in 2026, A2A removes the biggest integration pain point: the need to write and maintain bespoke adapter layers every time you add a new agent framework.

## Why CrewAI Adopted A2A as a First-Class Primitive

CrewAI treats A2A as a delegation primitive, not an afterthought bolt-on. Rather than wrapping A2A in a special tool class or plugin, CrewAI exposes it directly as a configuration option on the `Agent` class — the same place you define an agent's role, backstory, and LLM. This design decision reflects a key insight: 85% of developers in 2026 regularly use AI tools across multiple frameworks, which means cross-framework agent communication is a mainstream problem, not an edge case. Before A2A, connecting a CrewAI research agent to a LangGraph execution agent meant writing custom REST adapters, managing serialization formats, and handling auth manually for each pair of frameworks. With A2A, CrewAI agents can delegate tasks to any compliant server agent by specifying a URL and auth config — the protocol handles capability negotiation, task lifecycle, and streaming. CrewAI also acts as an A2A server itself: you can expose any CrewAI crew as an A2A-compliant endpoint, making it accessible to agents built in other frameworks. This bidirectional support is what makes A2A genuinely useful in production: you can participate in a multi-framework ecosystem as both a consumer and a provider without rewriting your core crew logic.

## A2A vs Direct API Integration: Key Differences

A2A protocol and direct API calls solve different problems, and picking the wrong one creates unnecessary complexity. A direct API call works best when you control both ends of the integration, both agents use the same framework version, and you only need request-response (no streaming). A2A is better when agents are built on different frameworks, owned by different teams, or need to stream results back incrementally.

| Dimension | Direct API Call | A2A Protocol |
|---|---|---|
| Discovery | Manual, hardcoded | Automatic via `/.well-known/agent.json` |
| Auth | Custom per integration | Standardized: Bearer, OAuth2, API keys |
| Streaming | Manual SSE/WebSocket | Built into the spec |
| Framework coupling | Tight | None |
| Schema validation | Ad hoc | JSON-RPC 2.0 enforced |
| Task lifecycle | Custom | Standardized (`submitted`, `working`, `completed`) |
| Interoperability | Framework-specific | Any A2A-compliant agent |

A direct API call has less overhead and fewer moving parts when you control both sides. But A2A wins in any scenario where you're connecting agents from different teams or frameworks — the standardization eliminates the negotiation cost of "how do we send data between these two things?" every time you add a new agent to the system.

A2A also defines a formal task lifecycle (`submitted` → `working` → `completed` / `failed`) that makes it easy to poll for status or stream progress without reinventing that machinery for each integration. This is particularly valuable for long-running tasks like research synthesis or code generation, where you want intermediate updates rather than a single blocking response.

## Setting Up CrewAI with A2A Support

Installing A2A support in CrewAI requires the `crewai[a2a]` extra, which pulls in the `a2a-sdk` package alongside the base framework. Here is the full setup sequence:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install CrewAI with A2A support
pip install "crewai[a2a]>=0.80.0"

# Verify the installation
python -c "import crewai; print(crewai.__version__)"
```

You also need an LLM API key. CrewAI defaults to OpenAI but works with any LiteLLM-compatible provider:

```bash
export OPENAI_API_KEY="sk-..."
# Or use a different provider
export ANTHROPIC_API_KEY="sk-ant-..."
```

If you are connecting to an existing A2A server agent (a LangGraph endpoint, for example), you need the server's base URL and its auth credentials. Collect these before writing any code — you will pass them in the `A2AClientConfig` object shown in the next section.

Your project structure for a minimal A2A-enabled crew looks like this:

```
my_a2a_crew/
├── agents.py
├── tasks.py
├── crew.py
└── .env
```

Keep credentials in `.env` and load them with `python-dotenv`. Never hardcode tokens directly in agent configuration files.

## Building Your First A2A Agent in CrewAI

A2A agents in CrewAI work by wrapping a remote A2A server in an `A2AClientConfig` and attaching it to a standard `Agent` definition. The local agent delegates tasks to the remote server automatically when assigned tasks that require it. Here is a complete working example:

```python
from crewai import Agent, Task, Crew
from crewai.a2a import A2AClientConfig, A2AAuthConfig

# Configure the A2A client — points to a remote compliant agent
a2a_config = A2AClientConfig(
    server_url="https://my-langgraph-agent.example.com",
    auth=A2AAuthConfig(
        type="bearer",
        token="your-bearer-token-here"
    )
)

# Define a CrewAI agent that delegates to the A2A server
researcher = Agent(
    role="Research Specialist",
    goal="Gather and summarize technical information on any topic",
    backstory=(
        "You are a senior researcher with access to specialized "
        "analysis tools hosted on external agent servers."
    ),
    a2a_client=a2a_config,
    verbose=True
)

# Task will be delegated through A2A to the remote agent
research_task = Task(
    description="Research the latest advances in transformer architecture pruning",
    expected_output="A 500-word technical summary with three key findings",
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[research_task])
result = crew.kickoff()
print(result)
```

When `crew.kickoff()` runs, CrewAI sends the task payload to the remote A2A server via JSON-RPC, polls for status updates, and streams back the result. From the LLM's perspective, it simply receives the completed output — the A2A transport layer is invisible.

The `A2AClientConfig` supports four auth types out of the box: `bearer` (token in Authorization header), `oauth2` (client credentials flow), `api_key` (custom header), and `http_basic`. Match the type to what the server agent expects.

## Cross-Framework Communication: CrewAI + LangGraph

The most practical A2A use case in 2026 is connecting a CrewAI crew to a LangGraph workflow — the two most popular agent frameworks with overlapping but non-identical strengths. CrewAI excels at role-based multi-agent orchestration; LangGraph excels at complex stateful workflows with explicit graph logic. Combining them via A2A lets you use each where it fits best. Google's purchasing concierge Codelab demonstrates exactly this pattern: a CrewAI "Burger agent" and a LangGraph "Pizza agent" work together via A2A to fulfill a composite food order, with each framework handling the domain it knows best.

First, expose your LangGraph graph as an A2A server:

```python
# langgraph_server.py
from langgraph.a2a import A2AServer
from my_graph import compiled_graph

app = A2AServer(
    graph=compiled_graph,
    agent_card={
        "name": "LangGraph Execution Agent",
        "description": "Executes structured workflows with state management",
        "version": "1.0.0",
        "capabilities": ["streaming", "stateful-execution"]
    }
)

# Run with: uvicorn langgraph_server:app --port 8001
```

Then point your CrewAI agent at that server:

```python
from crewai.a2a import A2AClientConfig, A2AAuthConfig

langgraph_config = A2AClientConfig(
    server_url="http://localhost:8001",
    auth=A2AAuthConfig(type="bearer", token="dev-token")
)

executor_agent = Agent(
    role="Workflow Executor",
    goal="Execute structured multi-step workflows via LangGraph",
    backstory="Specialist in stateful task execution with rollback support",
    a2a_client=langgraph_config
)
```

The two agents now communicate over A2A: CrewAI sends tasks as JSON-RPC messages, LangGraph processes them through its state graph, and results stream back to the CrewAI crew. Neither framework needs to know anything about the other's internals.

## Authentication and Security for A2A Agents

A2A's authentication model mirrors enterprise API security patterns, which makes it straightforward to integrate with existing identity infrastructure. CrewAI's `A2AAuthConfig` supports four auth strategies, each suited to different deployment scenarios. The bearer token approach is simplest and works for internal services; OAuth2 client credentials is the right choice for production B2B agent communication where you need short-lived, auditable tokens.

```python
from crewai.a2a import A2AAuthConfig

# Bearer token (simple, good for internal/dev)
bearer_auth = A2AAuthConfig(
    type="bearer",
    token="eyJhbGciOiJSUzI1NiJ9..."
)

# OAuth2 client credentials (production cross-org communication)
oauth2_auth = A2AAuthConfig(
    type="oauth2",
    client_id="crewai-crew-prod",
    client_secret="your-secret",
    token_url="https://auth.example.com/oauth/token",
    scopes=["agent:read", "agent:execute"]
)

# API key via custom header (common for SaaS agent platforms)
api_key_auth = A2AAuthConfig(
    type="api_key",
    header_name="X-Agent-API-Key",
    api_key="ak_live_..."
)

# HTTP Basic (legacy systems or internal proxies)
basic_auth = A2AAuthConfig(
    type="http_basic",
    username="crew-service",
    password="internal-password"
)
```

Beyond auth, enforce these security practices for production A2A deployments:

- **TLS everywhere**: Only connect to `https://` endpoints in production. A2A over plain HTTP leaks task payloads.
- **Rotate bearer tokens**: Set a short TTL (1–24 hours) and automate rotation via your secrets manager.
- **Scope OAuth2 tokens tightly**: Request only the scopes an agent needs (`agent:execute` not `agent:admin`).
- **Validate the agent card**: Before delegating tasks to a discovered agent, verify its `/.well-known/agent.json` matches your expected capabilities and version.
- **Rate-limit outbound requests**: Wrap your `A2AClientConfig` in a circuit breaker to prevent a misbehaving remote agent from cascading failures into your crew.

## Debugging with A2A Inspector

The A2A Inspector is a browser-based tool for observing the JSON-RPC messages that flow between A2A agents in real time. It works by proxying traffic between your client and server, displaying each request and response in a structured UI. This is the fastest way to diagnose why a delegation is failing or why results are arriving malformed.

To use it during local development:

```bash
# Install the inspector CLI
pip install a2a-inspector

# Start the inspector proxy (listens on 8080, forwards to your server on 8001)
a2a-inspector proxy --target http://localhost:8001 --port 8080
```

Then point your `A2AClientConfig` at the inspector proxy instead of directly at the server:

```python
a2a_config = A2AClientConfig(
    server_url="http://localhost:8080",  # Inspector proxy
    auth=A2AAuthConfig(type="bearer", token="dev-token")
)
```

Open `http://localhost:8080/inspector` in your browser. You will see each JSON-RPC call as it happens, including the task payload sent to the server, status update messages streamed back, and the final result envelope.

Common issues the Inspector surfaces immediately:

| Symptom | Root cause | Fix |
|---|---|---|
| 401 on every request | Wrong auth type or expired token | Check `A2AAuthConfig.type` matches server expectation |
| Task stuck in `working` | Remote agent timeout or exception | Check server logs; add timeout to `A2AClientConfig` |
| Empty result payload | Schema mismatch in response | Inspect raw JSON; check `expected_output` format |
| 404 on agent card | Wrong `server_url` or server not started | Curl `{server_url}/.well-known/agent.json` manually |

The Inspector also records a session log you can export as JSON — useful for sharing a debugging trace with a teammate or filing a bug report against a third-party agent service.

## Deploying A2A Agents to Production

Production A2A deployments require three infrastructure decisions: where to host your A2A server agents, how to handle discovery, and how to manage agent card versioning. Google Cloud Run is the most common choice for A2A server agents in 2026 because it scales to zero between requests, supports streaming (required for A2A SSE), and has native integration with Google's Agent Engine for multi-agent orchestration at scale.

Here is a minimal `Dockerfile` for a CrewAI A2A server agent:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Deploy to Cloud Run:

```bash
gcloud run deploy crewai-a2a-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

For the discovery endpoint, host your `agent.json` at the service URL's `/.well-known/agent.json` path. Cloud Run handles HTTPS automatically, satisfying A2A's TLS requirement.

For multi-region deployments, put a load balancer in front of your Cloud Run services and ensure the agent card's `url` field points to the load balancer endpoint, not individual regional endpoints. This keeps the A2A discovery address stable across deployments.

Agent card versioning matters when you update an agent's capabilities. Increment the `version` field in your agent card and maintain backward compatibility for at least one version cycle — client agents may cache the card and not pick up new capabilities immediately.

## Real-World Use Cases for Interoperable Agents

A2A interoperability unlocks composite AI architectures that weren't practical before a common standard existed. The most valuable real-world patterns in 2026 fall into three categories: cross-team agent composition, cross-vendor delegation, and capability specialization. In enterprise settings, different teams often own different AI systems — the data team has LangGraph pipelines, the product team has CrewAI crews, and a vendor provides a specialized analysis agent. A2A lets all three participate in a single workflow without requiring any team to rewrite their agent stack. A cross-team research pipeline, for example, might have a CrewAI orchestrator crew dispatching subtasks to a LangGraph data retrieval graph and a third-party A2A-compliant summarization service, then assembling the results into a final report. Each component is independently deployed, versioned, and scaled. Cross-vendor delegation covers scenarios like routing complex financial analysis to a specialized vendor agent while keeping sensitive data processing on your own infrastructure — A2A's standardized auth makes this auditable and controllable. Capability specialization is the most granular pattern: one agent per specialized skill (web search, code execution, database query), all exposed as A2A servers, composed by a lightweight orchestrator that routes tasks to the right specialist. This "skill bus" architecture scales well because you add new capabilities by deploying a new A2A server — no changes to the orchestrator.

Concrete examples already running in production:

- **E-commerce fulfillment**: CrewAI order management crew + LangGraph inventory agent + vendor shipping A2A service
- **Legal document review**: CrewAI case coordinator + specialized contract parsing A2A agent + compliance checker
- **Software delivery**: CrewAI project manager + GitHub Copilot Workspace A2A endpoint + test runner agent

## FAQ

**What Python version does CrewAI A2A support?**
CrewAI with A2A support requires Python 3.10 or higher. Python 3.12 is recommended for production deployments because it includes performance improvements that reduce latency for SSE streaming in high-throughput agent pipelines.

**Can I use CrewAI as an A2A server, not just a client?**
Yes. CrewAI 0.80+ includes an `A2AServer` class that wraps your crew and exposes it as an A2A-compliant HTTP endpoint, including the `/.well-known/agent.json` discovery file. Any A2A-compliant client — LangGraph, Semantic Kernel, or a custom agent — can then delegate tasks to your crew.

**Is A2A the same as MCP (Model Context Protocol)?**
No. MCP (developed by Anthropic) standardizes how agents access tools and resources. A2A standardizes how agents communicate with other agents. They are complementary: an agent might use MCP to access a database tool and A2A to delegate a subtask to another agent. Many frameworks, including CrewAI, support both.

**How does A2A handle long-running tasks that take minutes to complete?**
A2A defines a task lifecycle (`submitted` → `working` → `completed`) with optional server-sent events for streaming intermediate updates. For tasks that take more than a few seconds, configure your `A2AClientConfig` with a `streaming=True` flag and handle the event stream in your crew's task callback. This prevents HTTP timeouts and gives users incremental progress feedback.

**What happens when an A2A server agent is unavailable?**
CrewAI surfaces an `A2AConnectionError` or `A2ATaskError` depending on whether the failure is at the connection or task execution layer. Wrap your crew's `kickoff()` in a try/except block and implement retry logic with exponential backoff. For production systems, add a circuit breaker — if the remote agent fails more than N times in a window, stop sending requests and alert the on-call engineer.
