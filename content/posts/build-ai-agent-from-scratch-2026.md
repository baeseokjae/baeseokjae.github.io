---
cover:
  alt: 'How to Build an AI Agent from Scratch 2026: Python + LangChain + Tools'
  image: /images/build-ai-agent-from-scratch-2026.png
  relative: false
date: 2026-04-24 04:10:20+00:00
description: Build a production-ready AI agent from scratch using Python, LangGraph,
  and custom tools — with memory, error handling, and deployment included.
draft: false
schema: schema-build-ai-agent-from-scratch-2026
tags:
- ai-agents
- python
- langchain
- langgraph
- tutorial
title: 'How to Build an AI Agent from Scratch 2026: Python + LangChain + Tools'
---

Building an AI agent from scratch in 2026 means choosing LangGraph or LangChain, wiring in custom tools, and adding persistent memory — all in under 200 lines of Python. This guide walks every step from environment setup through production deployment, with runnable code and cost estimates under $2.00 in API calls.

## Why 2026 Is the Year to Build AI Agents

The AI agents market reached $7.63 billion in 2025 and is projected to hit $182.97 billion by 2033 at a 49.6% CAGR, according to Grand View Research. More practically: Gartner projects 40% of enterprise applications will integrate task-specific AI agents by end of 2026, up from less than 5% today. McKinsey's 2025 State of AI Survey found 62% of organizations are at least experimenting with AI agents — 23% actively scaling. The gap between experimenters and producers is closing fast, and the Python tooling in 2026 is mature enough to bridge it. LangGraph crossed 126,000 GitHub stars in April 2026, making it the dominant orchestration framework. The window for competitive advantage belongs to developers who can ship working agents now, not teams still debating which framework to pick.

The catch: only 6% of organizations qualify as true AI high performers where more than 5% of EBIT is attributable to AI. The difference is rarely model quality — it's agent architecture. Agents that work in demos fail in production because they lack persistent state, error recovery, and observability. This guide addresses all three.

## Understanding AI Agent Architecture

An AI agent is software that perceives its environment, reasons about a goal, and takes autonomous action to achieve it without waiting for step-by-step human instructions. Unlike a chatbot that responds once per prompt, an agent runs a loop: it receives input, decides whether to use a tool or respond directly, executes the tool, observes the result, and repeats until the goal is satisfied. This perception → reasoning → action cycle runs continuously, with the agent adapting when results deviate from expectations.

The three core components of any LLM-based agent in 2026:

1. **Brain (LLM)**: The model (Claude, GPT-4o, Gemini) that reasons about goals and decides which tools to call.
2. **Tools**: Functions the agent can invoke — web search, database queries, API calls, code execution.
3. **Memory**: Short-term context (conversation history) plus long-term persistence (checkpointed state in SQLite or PostgreSQL).

The ReAct pattern (Reason + Act) is the standard execution loop: the LLM reasons about the next step, calls a tool, observes the output, reasons again. LangGraph extends this with graph-based state machines that support cycles, branching, and conditional logic — essential for production workflows where a linear chain breaks.

## Choosing Your Framework: LangGraph vs LangChain vs CrewAI vs AutoGen

The right framework depends on whether you need graph-based state control, role-based crews, or conversation-driven coordination. Here is the 2026 comparison:

| Framework | Architecture | Learning Curve | Checkpointing | Best For |
|-----------|-------------|----------------|---------------|----------|
| LangGraph | Directed graph with nodes/edges | Moderate | Built-in (SQLite/PostgreSQL) | Complex stateful workflows |
| LangChain | AgentExecutor with ReAct | Low | Via memory modules | Simple tool-calling agents |
| CrewAI | Role-based agent crews | Low | Limited | Multi-agent collaboration |
| AutoGen | Conversation-based | Low | Limited | Research, multi-agent chat |

**LangGraph** wins for production workloads requiring branching logic, human-in-the-loop approval, and persistent checkpointing across sessions. It dropped Python 3.9 support in 1.1.x and added Python 3.14 compatibility. Use it for anything that needs to resume after failure or pause for human review.

**LangChain's AgentExecutor** with `create_react_agent` is the faster path for simple tool-calling agents. It uses the same LCEL (LangChain Expression Language) interface and integrates with LangSmith for tracing. Choose it when you need something running in an afternoon and the workflow is linear.

**CrewAI** shines for multi-agent systems where agents have defined roles (researcher, writer, reviewer). The abstraction is higher-level, which makes it faster to prototype but harder to customize execution flow.

For this guide, we build with LangGraph for the production path and show the LangChain equivalent for simpler use cases.

## Prerequisites and Environment Setup

Before writing a single line of agent code, your environment needs three things in place: the right Python version, valid API keys, and a virtual environment that isolates your dependencies. Python 3.12 is the recommended version for 2026 — LangGraph 1.1.x dropped Python 3.9 support and 3.12 delivers significantly better async performance than 3.10 or 3.11. The entire tutorial runs for under $2.00 in API costs using cloud-hosted models. Local model support via Ollama is available but requires substantially more hardware. Hardware: 4GB RAM is sufficient for cloud API mode with OpenAI or Anthropic. Local Ollama models require 16GB RAM and 8GB VRAM GPU minimum. Most developers on MacBook M-series chips or any cloud VM with 4+ vCPUs can run the full tutorial without GPU requirements.

**Python version**: 3.12+ (LangGraph 1.1.x dropped 3.9, added 3.14 support)

**API keys needed**:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for the LLM
- `TAVILY_API_KEY` for web search (free tier: 1,000 searches/month)
- `LANGCHAIN_API_KEY` for LangSmith tracing (optional but recommended)

```bash
python -m venv .venv
source .venv/bin/activate

pip install langgraph langchain langchain-openai langchain-anthropic \
            tavily-python python-dotenv fastapi uvicorn
```

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=my-agent
```

Total API cost for all steps in this tutorial: under $2.00.

## Step 1: Project Structure and Dependency Installation

A clean project layout is not bureaucracy — it is the difference between an agent you can debug in 5 minutes and one that requires reading 600 lines to understand. The structure below separates the state schema, tool definitions, graph nodes, and graph assembly into discrete files. Each file can be imported and tested independently. When a tool starts returning bad results, you open `tools.py`. When the agent routing logic breaks, you open `nodes.py`. When you need to add a new node, you touch `graph.py` without risking side effects in the tool layer. This layout scales from a single-developer prototype to a multi-team production system with minimal refactoring. Start with it, not after your first refactor. The `tests/` directory is not optional for production agents — at minimum, test the circuit breaker logic and each custom tool in isolation before deploying.

```
my-agent/
├── agent/
│   ├── __init__.py
│   ├── state.py        # TypedDict state schema
│   ├── tools.py        # Custom tool definitions
│   ├── nodes.py        # Graph node functions
│   └── graph.py        # Graph assembly and compilation
├── tests/
│   └── test_agent.py
├── main.py             # FastAPI entrypoint
├── .env
└── requirements.txt
```

Keep `state.py`, `tools.py`, `nodes.py`, and `graph.py` separate. This structure lets you test nodes in isolation and swap tools without touching graph logic.

## Step 2: Define the Agent State Schema

The state schema is the foundation of a LangGraph agent. It defines what data flows between nodes, how messages accumulate, and what gets checkpointed. A poorly designed state schema causes most of the debugging pain in production agents.

```python
# agent/state.py
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    tool_calls_count: int
    requires_human_approval: bool
```

The `Annotated[list[BaseMessage], add_messages]` pattern is the key: `add_messages` is a reducer that appends new messages rather than replacing the list. Without this, each node invocation overwrites the conversation history. The `tool_calls_count` field enables rate limiting and loop detection. The `requires_human_approval` flag drives the human-in-the-loop conditional edge.

For complex agents, add domain-specific fields to the state: `current_task`, `retrieved_context`, `error_count`. Every field you add is automatically persisted by the checkpointer.

## Step 3: Create and Register Tools

Tools are the capabilities your agent can invoke. In LangGraph and LangChain, the `@tool` decorator converts a Python function into a tool the LLM can call by name, with automatic schema generation from type hints and docstrings.

```python
# agent/tools.py
from langchain_core.tools import tool
from tavily import TavilyClient
import sqlite3

tavily = TavilyClient()

@tool
def web_search(query: str) -> str:
    """Search the web for current information. Use for news, prices, recent events."""
    results = tavily.search(query=query, max_results=3)
    return "\n\n".join([r["content"] for r in results["results"]])

@tool
def query_database(sql: str) -> str:
    """Run a read-only SQL query against the products database."""
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: only SELECT queries are permitted"
    conn = sqlite3.connect("products.db")
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return str([dict(zip(cols, row)) for row in rows[:20]])
    except Exception as e:
        return f"Query error: {e}"
    finally:
        conn.close()

@tool
def calculate_metrics(values: list[float], metric: str) -> str:
    """Calculate statistical metrics (mean, median, std, sum) for a list of numbers."""
    import statistics
    ops = {"mean": statistics.mean, "median": statistics.median,
           "std": statistics.stdev, "sum": sum}
    if metric not in ops:
        return f"Unknown metric. Choose from: {list(ops.keys())}"
    return str(ops[metric](values))

tools = [web_search, query_database, calculate_metrics]
```

Security note: the `query_database` tool enforces SELECT-only at the tool level. Never pass raw user input directly to SQL. Always validate at the tool boundary, not just the application layer.

## Step 4: Build Graph Nodes and Wire Conditional Edges

Nodes are pure functions that take the current state and return a state update. The graph wires them together with edges that can be conditional — branching based on state values to route between nodes. This is where LangGraph's power over simple chains becomes visible.

```python
# agent/nodes.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from .state import AgentState
from .tools import tools

llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

def call_model(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],
        "tool_calls_count": state["tool_calls_count"] + (
            1 if response.tool_calls else 0
        )
    }

def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return "end"
    if state["tool_calls_count"] > 10:
        return "end"  # circuit breaker: prevent infinite loops
    if state.get("requires_human_approval"):
        return "human_review"
    return "tools"
```

```python
# agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import AgentState
from .nodes import call_model, should_continue
from .tools import tools

def build_graph(db_path: str = "checkpoints.db"):
    graph = StateGraph(AgentState)
    
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))
    
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END, "human_review": END}
    )
    graph.add_edge("tools", "agent")
    
    checkpointer = SqliteSaver.from_conn_string(db_path)
    return graph.compile(checkpointer=checkpointer)
```

The `ToolNode` prebuilt node handles tool execution, error catching, and formatting tool results back as `ToolMessage` objects. The circuit breaker at 10 tool calls prevents runaway agents — critical for production use where a poorly-worded prompt can trigger an expensive loop.

## Step 5: Add Persistent Memory with Checkpointing

Persistent memory separates toy agents from production agents. A checkpointer serializes the full agent state after each step, storing it by `thread_id`. If the process crashes, the agent resumes exactly where it stopped. Users can continue conversations across days without losing context.

LangGraph's `SqliteSaver` works for development and low-traffic production. For high-concurrency production, switch to `AsyncPostgresSaver`:

```python
# Development (SQLite)
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# Production (PostgreSQL)
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import asyncpg

async def get_checkpointer():
    pool = await asyncpg.create_pool(dsn=os.environ["DATABASE_URL"])
    return AsyncPostgresSaver(pool)
```

Running the agent with thread-based memory:

```python
app = build_graph()

config = {"configurable": {"thread_id": "user-123-session-1"}}

result = app.invoke(
    {
        "messages": [{"role": "user", "content": "What are the top 3 products by revenue?"}],
        "user_id": "user-123",
        "tool_calls_count": 0,
        "requires_human_approval": False,
    },
    config=config
)

# Continue same session — full history is preserved
result2 = app.invoke(
    {"messages": [{"role": "user", "content": "Now compare them to last quarter"}]},
    config=config
)
```

The same `thread_id` retrieves the checkpointed state automatically. Each invocation appends to the existing message history. Change the `thread_id` to start a fresh session.

## Step 6: Implement Human-in-the-Loop Approval

Human-in-the-loop (HITL) is a safety mechanism that pauses the agent before high-stakes tool calls and waits for human approval. In LangGraph, this is a first-class feature using `interrupt_before` at compile time.

```python
# Compile with interrupt point
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]  # pause before every tool execution
)

config = {"configurable": {"thread_id": "approval-flow-1"}}

# Step 1: Run until interrupt
result = app.invoke(initial_state, config=config)
# Agent has reasoned and selected a tool — now paused

# Step 2: Inspect the pending tool call
pending_state = app.get_state(config)
tool_call = pending_state.values["messages"][-1].tool_calls[0]
print(f"Agent wants to call: {tool_call['name']} with {tool_call['args']}")

# Step 3: Approve or reject
if human_approves(tool_call):
    result = app.invoke(None, config=config)  # resume
else:
    app.update_state(config, {"messages": [{"role": "tool", 
        "content": "Action rejected by human reviewer", 
        "tool_call_id": tool_call["id"]}]})
    result = app.invoke(None, config=config)
```

For production, wire this into a Slack bot or web UI: the agent posts a message with approve/reject buttons, the human clicks, and the webhook resumes the agent. The state is checkpointed at the interrupt point, so the approval workflow survives server restarts.

## Step 7: Testing, Error Recovery, and Retry Logic

Reliable agents require testing at three levels: individual tools, individual nodes, and full graph execution. LangGraph's node isolation makes unit testing straightforward — each node is a pure function.

```python
# tests/test_agent.py
import pytest
from agent.nodes import call_model, should_continue
from agent.state import AgentState
from langchain_core.messages import HumanMessage, AIMessage

def make_state(**kwargs) -> AgentState:
    defaults = {"messages": [], "user_id": "test", 
                "tool_calls_count": 0, "requires_human_approval": False}
    return {**defaults, **kwargs}

def test_circuit_breaker():
    """Agent should stop after 10 tool calls to prevent infinite loops."""
    state = make_state(
        messages=[AIMessage(content="", tool_calls=[{"name": "web_search", 
                  "args": {"query": "test"}, "id": "1"}])],
        tool_calls_count=11
    )
    assert should_continue(state) == "end"

def test_end_without_tool_calls():
    state = make_state(messages=[AIMessage(content="Here is the answer")])
    assert should_continue(state) == "end"
```

For error recovery, add retry logic at the node level using `tenacity`:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def call_model_with_retry(state: AgentState) -> dict:
    return call_model(state)
```

The `handle_parsing_errors=True` equivalent in LangGraph is catching `OutputParserException` in the node and returning an error message to the state instead of raising. Always set a max retry count — uncapped retries turn network blips into runaway API bills.

## Step 8: Multi-Agent Collaboration Patterns

Multi-agent systems split complex tasks across specialized agents: a researcher, an analyst, and a writer each handle their domain, with a supervisor routing between them. LangGraph supports this natively through subgraphs and the `Command` primitive.

```python
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str

def supervisor_node(state: SupervisorState) -> Command:
    """Route to the appropriate specialist agent."""
    last_message = state["messages"][-1].content
    
    # Supervisor LLM decides which agent goes next
    decision = supervisor_llm.invoke(state["messages"])
    
    return Command(goto=decision.next_agent, 
                   update={"next_agent": decision.next_agent})

# Subgraph pattern: each agent is its own compiled graph
researcher_graph = build_researcher_graph()
analyst_graph = build_analyst_graph()

supervisor = StateGraph(SupervisorState)
supervisor.add_node("supervisor", supervisor_node)
supervisor.add_node("researcher", researcher_graph)
supervisor.add_node("analyst", analyst_graph)
```

The `Command` primitive is new in LangGraph 1.1 — it replaces the older pattern of updating state flags to control routing. Commands make multi-agent flow explicit and easier to debug in LangSmith traces.

For CrewAI-style role assignment, define each agent with a system prompt that establishes its persona and constraints. The supervisor routes based on the task type, not on agent availability. Keep subgraphs stateless where possible — let the parent graph own the shared state.

## Step 9: Deployment with LangGraph Platform and Docker

LangGraph Platform provides managed deployment with built-in Redis for streaming, PostgreSQL for checkpoints, and an API layer compatible with the local development interface. For self-hosted deployment, Docker is the standard path.

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent.graph import build_graph

app = FastAPI()
agent = build_graph()

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    user_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": request.message}],
            "user_id": request.user_id,
            "tool_calls_count": 0,
            "requires_human_approval": False,
        },
        config=config
    )
    return {"response": result["messages"][-1].content}
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/agent
    depends_on:
      - db
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: agent
```

For LangGraph Platform deployment: push your graph code to a GitHub repo, connect it in the LangGraph Cloud dashboard, and deployments trigger on merge to main. The platform handles scaling, streaming, and the checkpoint database.

## Step 10: Monitoring with LangSmith Observability

LangSmith traces every LLM call, tool invocation, and node transition in your agent. Set `LANGCHAIN_TRACING_V2=true` and your `LANGCHAIN_API_KEY` in the environment — no code changes required. Every `app.invoke()` call automatically creates a trace.

Key metrics to monitor in LangSmith:

- **Latency per node**: identify which nodes are slow (usually tool calls, not LLM inference)
- **Token usage per trace**: catch prompts that are ballooning in size due to long conversation history
- **Tool error rate**: high errors on `query_database` usually mean the LLM is generating invalid SQL
- **Loop detection**: traces with 8+ tool calls indicate a potential infinite loop pattern

For custom metrics, use the `RunTree` API to add metadata to traces:

```python
from langsmith import RunTree

with RunTree(name="agent-run", run_type="chain", 
             extra={"user_id": user_id, "session_id": thread_id}) as run:
    result = agent.invoke(state, config=config)
    run.end(outputs={"response": result["messages"][-1].content})
```

Set up alerts in LangSmith for: average latency > 10s, tool error rate > 5%, or loop count > 5 in a single session. These thresholds catch 80% of production issues before users file bug reports.

## Common Pitfalls and Troubleshooting

The 10 most frequent issues developers hit when building LangGraph agents in 2026 cluster around four root causes: changed module paths between LangGraph versions, SQLite's single-writer limitation, token context management in long conversations, and environment variable loading order for LangSmith tracing. The fixes below are specific: if your symptom matches, apply the fix without reading the whole section. Most production agent failures are not model quality issues — they are infrastructure issues that could have been caught in local testing. The circuit breaker pattern (stopping after N tool calls), absolute file paths for SQLite, and tool functions that return descriptive strings instead of raising exceptions will prevent 70% of the issues listed here. Read the full list once before your first production deployment, then bookmark this section for when something breaks at 2am.

### Import errors after LangGraph upgrade

LangGraph 1.1.x reorganized module paths. If you see `ImportError: cannot import name 'SqliteSaver' from 'langgraph.checkpoint'`, update the import path:

```python
# Old (pre-1.1)
from langgraph.checkpoint import SqliteSaver
# New (1.1+)
from langgraph.checkpoint.sqlite import SqliteSaver
```

### Infinite loops in the agent

Symptom: agent keeps calling `web_search` or another tool without stopping. Fix: add the circuit breaker in `should_continue` (tool_calls_count > 10) and verify your system prompt instructs the model to stop when it has enough information. Also check that tool results are being correctly formatted as `ToolMessage` objects — malformed tool responses confuse the model into retrying.

### SQLite database lock errors

Symptom: `sqlite3.OperationalError: database is locked` under concurrent requests. Fix: switch to PostgreSQL for any multi-worker deployment. SQLite's WAL mode helps for single-worker multi-thread scenarios:

```python
checkpointer = SqliteSaver.from_conn_string("file:checkpoints.db?mode=rwc&journal_mode=WAL")
```

### Token limit exceeded mid-conversation

Long sessions accumulate messages until the context window fills. Fix: implement message trimming in the state update:

```python
from langchain_core.messages import trim_messages

def call_model(state: AgentState) -> dict:
    trimmed = trim_messages(state["messages"], max_tokens=4000, 
                            token_counter=llm, strategy="last")
    response = llm.invoke(trimmed)
    return {"messages": [response]}
```

### Tools returning empty results

Always add fallback handling in tool functions. If `web_search` returns no results, return a descriptive string like "No results found for query: {query}" rather than an empty string or raising an exception. Empty tool results cause the model to retry indefinitely.

### Streaming not working with FastAPI

Use `StreamingResponse` and `app.astream_events()` instead of `app.invoke()`:

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for event in agent.astream_events(state, config=config, version="v2"):
            if event["event"] == "on_chat_model_stream":
                yield event["data"]["chunk"].content
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Checkpointer not persisting across restarts

If agent state resets on restart, verify the SQLite file path is absolute, not relative. Relative paths resolve differently based on the working directory at startup:

```python
import os
db_path = os.path.join(os.path.dirname(__file__), "..", "checkpoints.db")
checkpointer = SqliteSaver.from_conn_string(os.path.abspath(db_path))
```

### Human approval never resuming

If `app.invoke(None, config=config)` after human approval raises a `GraphInterrupted` error or returns immediately without continuing: check that you're passing `None` as the input (not an empty dict), and that the `thread_id` in config exactly matches the interrupted session.

### LangSmith traces missing tool calls

Ensure `LANGCHAIN_TRACING_V2=true` is set before importing LangChain — setting it after import does nothing. Use `python-dotenv`'s `load_dotenv()` at the very top of `main.py`, before any LangChain imports.

### Memory growing unbounded in multi-session deployments

Each `thread_id` in SQLite is a row of serialized state. After 30 days, run:

```sql
DELETE FROM checkpoints WHERE thread_id IN (
  SELECT thread_id FROM checkpoints 
  WHERE created_at < datetime('now', '-30 days')
);
```

Add this as a scheduled task in your deployment.

## FAQ

**What is the difference between LangChain and LangGraph for building AI agents?**

LangChain provides the AgentExecutor loop with ReAct prompting — simple, low learning curve, good for linear tool-calling workflows. LangGraph is a graph-based state machine built on top of LangChain that supports cycles, branching, checkpointing, and human-in-the-loop. For production agents with complex workflows, use LangGraph. For a quick tool-calling agent that needs to be running today, LangChain AgentExecutor is fine.

**How much does it cost to run an AI agent with GPT-4o?**

A complete tutorial run with GPT-4o including 10 web searches and 5 database queries costs under $2.00 at current API rates. Production cost depends heavily on conversation length and tool call frequency. A single agent session averaging 20 messages costs roughly $0.10–0.30 with GPT-4o. Use GPT-4o-mini for high-volume, lower-stakes tasks to reduce costs by 15x.

**Do I need LangGraph Platform or can I self-host?**

Self-hosting with Docker + PostgreSQL + FastAPI is fully supported and costs less at scale. LangGraph Platform adds managed scaling, built-in streaming infrastructure, and a deployment UI. For teams without DevOps capacity or for rapid prototyping, Platform pays for itself. For organizations with existing Kubernetes infrastructure, self-hosting gives more control over data residency and cost.

**How do I prevent my AI agent from running in infinite loops?**

Two mechanisms: a circuit breaker in `should_continue` that returns `"end"` when `tool_calls_count > N`, and a clear system prompt that instructs the model to stop once it has sufficient information. Set the circuit breaker threshold at 10 for most agents. Also validate that tool functions return descriptive strings rather than empty results or exceptions, which cause the model to retry.

**What Python version should I use for AI agent development in 2026?**

Python 3.12 is the recommended version. LangGraph 1.1.x dropped Python 3.9 support and 3.12 has significantly better performance than 3.10/3.11 for async workloads. Python 3.14 compatibility was added in LangGraph 1.1.x but 3.14 is still in pre-release as of April 2026 — stick with 3.12 for production deployments.