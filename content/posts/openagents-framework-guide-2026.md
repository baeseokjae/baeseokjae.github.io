---
title: "OpenAgents Framework Guide: Build Persistent AI Agent Networks with MCP and A2A Support"
date: 2026-04-23T01:25:01+00:00
tags: ["openagents", "ai-agents", "mcp", "a2a", "multi-agent", "python"]
description: "Complete guide to OpenAgents framework — build persistent AI agent networks with native MCP and A2A protocol support in 2026."
draft: false
cover:
  image: "/images/openagents-framework-guide-2026.png"
  alt: "OpenAgents Framework Guide: Build Persistent AI Agent Networks with MCP and A2A Support"
  relative: false
schema: "schema-openagents-framework-guide-2026"
---

OpenAgents is an open-source framework for building persistent AI agent networks — systems where agents continue to exist, learn, and collaborate long after an initial task completes. Unlike LangGraph or CrewAI, which treat agents as stateless task runners, OpenAgents gives every agent a durable identity, a shared workspace with a persistent URL, and native support for both MCP (Model Context Protocol) and A2A (Agent-to-Agent) protocols from day one.

## What Is the OpenAgents Framework?

OpenAgents is an open-source Python framework designed specifically for building persistent, interoperable AI agent networks. Launched in early 2026, it addresses the fundamental limitation of most agent frameworks: agents disappear once a task finishes, losing all learned context. OpenAgents agents maintain a durable workspace accessible at a stable URL (e.g., `workspace.openagents.org/abc123`), enabling teams to bookmark a network and return to an evolved, context-rich system days or weeks later. The framework ships with three core components — Workspace, Launcher, and Network SDK — and natively implements both the MCP and A2A protocols, which means agents built with different underlying frameworks can collaborate without custom glue code. In 2026, as 85% of developers regularly use AI tooling, the demand for long-running, team-aware agent infrastructure has grown sharply, and OpenAgents is purpose-built to fill that gap. The key distinction from alternatives is its architectural commitment: persistence and interoperability are first-class features, not afterthoughts bolted on via plugins.

## OpenAgents vs LangGraph vs CrewAI vs AutoGen

OpenAgents occupies a distinct position among AI agent frameworks because it prioritizes network persistence and protocol interoperability over workflow orchestration or role-based task assignment. LangGraph excels at stateful, graph-based workflows where you need fine-grained control over execution paths — it's the right choice when your problem maps cleanly to a DAG. CrewAI is optimized for role-based crews where each agent has a defined persona and job, making it popular for content pipelines and structured research tasks. AutoGen (now AG2) focuses on conversation-driven multi-agent patterns with strong support for human-in-the-loop interactions. OpenAgents wins when the requirement is a long-running agent network that must persist state between sessions, support agent discovery across framework boundaries, and integrate natively with MCP tool servers or A2A-compliant agents from other organizations. A practical rule of thumb: if your agents need to be alive tomorrow and collaborate with agents you didn't build, use OpenAgents. If you're orchestrating a one-shot pipeline, LangGraph or CrewAI may be simpler.

| Framework | Persistence | MCP Support | A2A Support | Best For |
|---|---|---|---|---|
| OpenAgents | Native | Native | Native | Long-running networks |
| LangGraph | Manual checkpoints | Plugin | No | Workflow orchestration |
| CrewAI | Task-scoped | Plugin | No | Role-based crews |
| AutoGen (AG2) | Conversation history | Plugin | Experimental | Conversational agents |

## Core Concepts: Workspace, Launcher, and Network SDK

OpenAgents is built around three components that together form its persistent network model. The **Workspace** is a shared environment that persists at a stable URL — every agent in a network shares access to a common state store, message history, and tool registry. This is what makes "return to yesterday's agent network" possible. The **Launcher** is the entry point for starting and resuming agent sessions; it handles authentication, context restoration, and agent discovery, so picking up a paused network feels like reopening a browser tab rather than re-running a script. The **Network SDK** is the Python library that lets you define agent behavior, register tools via MCP, expose capabilities to other A2A-compliant agents, and subscribe to real-time events from peers. Together these components solve the three hard problems in production multi-agent systems: where does shared state live, how do new agents find existing ones, and how do you add human oversight without breaking automation. The Workspace URL is the anchor; the Launcher is the runtime entry point; the Network SDK is the developer surface.

### Workspace Persistence Model

A Workspace is more than a key-value store — it maintains versioned agent state, a shared tool registry, a message bus, and an audit log. Each Workspace gets a globally unique identifier, and all agents in a network read from and write to the same Workspace. When an agent restarts or a new agent joins, it calls `workspace.restore()` to hydrate its local state from the Workspace snapshot, ensuring continuity even after crashes or planned shutdowns.

### Network SDK Fundamentals

The Network SDK exposes a `@agent` decorator pattern similar to FastAPI routes. You define agent capabilities as async functions, annotate them with `@agent.tool` for MCP exposure or `@agent.skill` for A2A advertisement, and the SDK handles serialization, routing, and protocol negotiation. This keeps agent code readable and framework-agnostic — the same skill can be called by a Claude-powered agent, a GPT-based peer, or a human via the Workspace UI.

## Why Persistence Matters for AI Agents

Persistence is the feature that separates toy multi-agent demos from production agent infrastructure. In a non-persistent system, every task run starts from zero: the agent reloads its tools, re-fetches context, and has no memory of what it learned or decided in previous sessions. For one-off automations, this is fine. For knowledge-intensive workflows — ongoing research, continuous monitoring, evolving codebases — it compounds costs and errors rapidly. OpenAgents addresses this by treating the Workspace as a first-class persistence layer: agents write intermediate results, learned preferences, and accumulated tool knowledge back to the Workspace after every significant action. When the same agent (or a successor) wakes up tomorrow, it picks up exactly where it left off. The practical impact: a research agent that spent three sessions mapping a competitive landscape doesn't re-crawl the same sources on session four. A coding agent that learned your team's naming conventions applies them immediately without re-prompting. In 2026, as the global AI agents market matures and teams run agents continuously rather than on-demand, persistence transitions from a nice-to-have to a hard architectural requirement.

### Memory vs. State vs. Context

These three terms are often conflated but OpenAgents treats them distinctly. **State** is structured data written to the Workspace store (tool results, decisions, flags). **Memory** is the agent's compressed semantic history, managed by the Network SDK's built-in summarization pipeline. **Context** is the window assembled at inference time from state and memory. Keeping these separate allows OpenAgents to scale agent history indefinitely without hitting LLM context limits.

## Installing and Setting Up OpenAgents

Setting up OpenAgents takes under ten minutes on a standard Python 3.11+ environment. Install the core package via pip, authenticate against the OpenAgents cloud (or point at a self-hosted Workspace server), and you're ready to define your first agent network.

```bash
pip install openagents
openagents login          # OAuth flow, stores token in ~/.openagents/config.json
openagents workspace new my-research-network
```

The `workspace new` command returns a persistent URL and a workspace ID you'll use in all subsequent SDK calls. For self-hosted deployments, set `OPENAGENTS_WORKSPACE_URL` to your server address before running `openagents login`.

```python
from openagents import Agent, Workspace

ws = Workspace.connect("my-research-network")

@ws.agent(name="researcher")
class ResearchAgent(Agent):
    async def on_start(self):
        await self.restore()   # hydrate from Workspace snapshot

    @Agent.tool(description="Search the web for a query")
    async def web_search(self, query: str) -> str:
        ...
```

For teams, pin the OpenAgents version in `pyproject.toml` and commit the workspace ID (not the token) to version control so every developer connects to the same persistent network.

## Building Your First Persistent Agent Network

A minimal but realistic OpenAgents network consists of at least two agents with complementary roles — a planner that breaks tasks into subtasks and a worker that executes them — connected via the Workspace message bus. The key architectural decision is defining which state lives in the Workspace (shared, durable) versus which is local to an agent instance (ephemeral).

```python
from openagents import Agent, Workspace, Message

ws = Workspace.connect("my-first-network")

@ws.agent(name="planner")
class PlannerAgent(Agent):
    async def handle(self, msg: Message):
        subtasks = await self.llm.plan(msg.content)
        for task in subtasks:
            await self.send("worker", task)
            await ws.state.append("task_log", task)

@ws.agent(name="worker")
class WorkerAgent(Agent):
    async def handle(self, msg: Message):
        result = await self.execute(msg.content)
        await ws.state.set(f"result:{msg.id}", result)
        await self.send("planner", f"Done: {result}")

ws.launch(agents=[PlannerAgent, WorkerAgent])
```

This pattern gives you persistence (all tasks and results written to `ws.state`), resumability (agents call `restore()` on startup to replay missed messages), and auditability (the Workspace logs every message and state mutation).

### Handling Agent Failures Gracefully

OpenAgents implements an at-least-once delivery guarantee on the message bus. If a worker crashes mid-task, the Workspace re-delivers the message when the agent restarts. Agents signal completion by calling `msg.ack()`; unacknowledged messages are retried after a configurable timeout (default: 60 seconds).

## MCP and A2A Protocol Integration

OpenAgents natively supports both MCP (Model Context Protocol) and A2A (Agent-to-Agent) protocols, which is its strongest differentiator from LangGraph, CrewAI, and AutoGen in 2026. MCP is the emerging standard for exposing tools to AI models in a structured, discoverable way — instead of hardcoding API wrappers, you register tools as MCP servers, and any MCP-compatible agent can discover and invoke them. A2A is the cross-framework agent communication standard championed by Google and adopted across major agent platforms; it defines how agents advertise skills, negotiate tasks, and exchange results regardless of what underlying LLM or framework they use. OpenAgents implements both protocols out of the box, meaning an OpenAgents-built researcher agent can call tools from a standalone MCP server (like a web scraper or code executor) and delegate subtasks to a CrewAI or Semantic Kernel agent that exposes an A2A endpoint — all without writing custom serialization or transport code. In practice, this makes OpenAgents the natural hub in heterogeneous enterprise environments where multiple teams use different frameworks.

```python
# Register an MCP server as a tool source
ws.register_mcp_server("https://mcp.example.com/filesystem")

# Expose an agent skill via A2A
@ws.agent(name="code-reviewer")
class CodeReviewer(Agent):
    @Agent.skill(a2a=True, description="Review Python code for bugs")
    async def review_code(self, code: str) -> dict:
        ...
```

After registration, `review_code` is discoverable by any A2A-compatible agent on the network — it appears in the Workspace skill registry with its schema and endpoint.

### MCP Tool Discovery

OpenAgents automatically polls registered MCP servers for tool updates on a configurable interval (default: 5 minutes). New tools appear in `ws.tools` without requiring an agent restart. This is valuable in dynamic environments where teams add new MCP servers (database connectors, internal APIs) regularly.

## Real-Time Human-Agent Collaboration

OpenAgents includes built-in support for human participants in agent networks — not just as prompt senders, but as first-class network members who can observe agent state, inject messages, approve decisions, and receive escalations. The Workspace UI (accessible at the persistent Workspace URL) shows a live activity feed, the current state store, and message history, so a human team member can understand what agents are doing without reading logs. For approval workflows, agents can call `await self.request_approval(action, timeout=300)`, which pauses execution and notifies the designated human via the Workspace UI or a connected webhook (Slack, email). If no approval arrives within the timeout, the agent falls back to a safe default. This human-in-the-loop pattern is more robust than asking an agent to self-decide whether to escalate, because the framework enforces the pause rather than relying on the LLM's judgment.

```python
@Agent.tool(description="Execute a database migration")
async def run_migration(self, sql: str) -> str:
    approval = await self.request_approval(
        action=f"Run SQL: {sql[:100]}...",
        approvers=["dba-team"],
        timeout=600
    )
    if not approval.granted:
        return "Migration cancelled by human reviewer"
    return await self.db.execute(sql)
```

The Workspace logs approvals and rejections as immutable audit entries, satisfying compliance requirements for human-oversight-in-AI policies.

## Scaling OpenAgents for Production

Running OpenAgents at production scale requires thinking about three dimensions: Workspace throughput, agent concurrency, and cost. For throughput, OpenAgents supports sharded Workspaces — a root Workspace federates to child Workspaces for different domains (e.g., one per team or project), with cross-Workspace message routing handled by the Launcher. This avoids a single Workspace becoming a bottleneck as message volume grows. For agent concurrency, the Network SDK supports running multiple instances of the same agent class; the Workspace message bus distributes messages across instances using consistent hashing on the message key, ensuring related messages go to the same instance (important for stateful agents). For cost, OpenAgents exposes per-agent token usage via `ws.usage`, which you can route to your observability stack. Teams at scale typically set agent-level token budgets and use the `on_budget_exceeded` hook to throttle or swap to a cheaper model for low-priority tasks.

```python
# Production Workspace config
ws = Workspace.connect(
    "production-network",
    shard_count=4,
    max_agents_per_shard=50,
    default_model="claude-sonnet-4-6",
    budget_hook=lambda agent, usage: alert_if_over_budget(agent, usage)
)
```

For infrastructure, the OpenAgents Workspace server is stateless except for its backing store — you can run it on any container orchestration platform (Kubernetes, ECS) and scale horizontally behind a load balancer. The backing store requires a Redis-compatible service for the message bus and a PostgreSQL-compatible database for durable state.

## Use Cases: Research, Coding, and Content Creation

OpenAgents' persistent network model maps well to three high-value use cases where agents need to accumulate knowledge over multiple sessions. **Research networks** are the most common production deployment: a planner agent breaks a research question into sub-queries, dispatches workers to specialized sources (web, internal docs, databases), and synthesizes results into a Workspace knowledge base that grows with each session. A research network that's been running for a month has accumulated source credibility scores, known-unreliable domains, and a map of the information landscape — context a stateless agent can never build. **Coding networks** maintain a persistent understanding of a codebase: naming conventions, architectural patterns, test coverage gaps, and the history of past decisions. A persistent coding agent doesn't re-learn your project on every PR. **Content creation networks** track brand voice, past topics, audience feedback, and competitive content gaps across sessions, enabling a content agent to produce genuinely differentiated output rather than generic drafts. In all three cases, the ROI of persistence compounds over time: the network gets better at its domain with each session, reducing the manual context-setting that makes stateless AI tools tedious at scale.

### Combining Use Cases in One Network

OpenAgents' A2A support lets you compose multi-domain networks where a research agent, a coding agent, and a content agent share a Workspace. A product team might run a network where the researcher monitors competitor releases, the coding agent tracks the internal backlog, and the content agent drafts release notes — with a planner agent coordinating across all three. Each specialist agent maintains its domain knowledge in the shared Workspace, and cross-domain queries route via A2A skill calls.

---

## FAQ

**What programming language does OpenAgents support?**
OpenAgents provides a Python SDK as its primary developer interface. Python 3.11 or later is required. The Workspace server API is REST/WebSocket-based, so agents in other languages can interact with the Workspace directly without the Python SDK, but community SDKs for TypeScript and Go are in early development as of mid-2026.

**How is OpenAgents different from LangGraph?**
LangGraph is a graph-based orchestration framework optimized for stateful, step-by-step workflows with fine control over execution branches. OpenAgents is optimized for persistent agent networks where agents have long-running identities, share a durable state store, and need to interoperate with agents from other frameworks. LangGraph fits better when you're building a defined workflow pipeline; OpenAgents fits better when you're building infrastructure that agents live in over time.

**Does OpenAgents support local LLMs?**
Yes. The Network SDK's `Agent.llm` client is configurable — you can point it at any OpenAI-compatible endpoint, including Ollama, LM Studio, or a vLLM server. Cloud models (Claude, GPT-4o, Gemini) work out of the box with API key config. This makes OpenAgents viable for air-gapped deployments with local models.

**What is the A2A protocol and why does it matter?**
A2A (Agent-to-Agent) is an open standard for cross-framework agent communication. It defines how an agent advertises its skills, how peers discover it, and how task requests and results are structured. Without A2A, agents from different frameworks (e.g., a LangGraph agent talking to a CrewAI agent) require custom integration code. With A2A, any compliant agent can call any other compliant agent using a standard schema. OpenAgents implements A2A natively, making it an interoperability hub for heterogeneous enterprise agent environments.

**Is OpenAgents suitable for production workloads in 2026?**
OpenAgents is production-ready for teams willing to self-host the Workspace server or use the managed cloud offering. The framework handles at-least-once message delivery, agent failure recovery, human approval workflows, and horizontal scaling. Early adopters in research, content, and internal tooling teams report stable multi-week agent network deployments. For mission-critical financial or healthcare workloads, additional observability and compliance tooling on top of OpenAgents is recommended.
