---
cover:
  alt: 'LangGraph Tutorial 2026: Build Stateful AI Agents with Graphs'
  image: /images/langgraph-tutorial-2026.png
  relative: false
date: 2026-04-19 16:32:57+00:00
description: 'Step-by-step LangGraph tutorial 2026: install, define state, build graph
  nodes, add memory, deploy production agents.'
draft: false
schema: schema-langgraph-tutorial-2026
tags:
- langgraph
- ai-agents
- python
- llm
- tutorial
title: 'LangGraph Tutorial 2026: Build Stateful AI Agents with Graphs'
---

LangGraph is a Python and JavaScript framework for building stateful, graph-based AI agents. Unlike simple chain-based approaches, LangGraph lets you define agents as directed graphs where nodes are processing steps and edges determine flow — including loops, conditionals, and human approval gates. With 126,000+ GitHub stars as of April 2026, it's the most widely adopted open-source framework for production AI agents.

## What Is LangGraph and Why Use It in 2026?

LangGraph is an open-source orchestration framework built on top of LangChain that models AI agent workflows as graphs — nodes represent computation steps (calling an LLM, running a tool, parsing output) and edges represent transitions between those steps, including conditional branching. Released in 2023 under the Apache 2.0 license, LangGraph reached version 1.1.6 in April 2026 with over 126,000 GitHub stars. The core insight is that production AI agents are inherently cyclic: an agent reasons, acts, observes, then reasons again until done. Simple chain frameworks force you to unroll those loops manually; LangGraph handles them natively. State persists across the entire graph execution via checkpointers (SQLite, PostgreSQL, in-memory), making it trivial to pause mid-workflow, resume after a crash, or implement human-in-the-loop approval gates. Compared to CrewAI (role-based team abstraction) or AutoGen (conversational multi-agent), LangGraph gives you lower-level control — you explicitly wire the graph topology rather than letting the framework infer it from roles. That control pays off at production scale: parallel tool execution, fine-grained error recovery, and streaming output all come standard.

### LangGraph vs LangChain: What's the Difference?

LangGraph is a separate package (`langgraph`) that extends LangChain's ecosystem but isn't a replacement. LangChain handles the building blocks — prompt templates, LLM wrappers, tool definitions, output parsers. LangGraph handles orchestration — how those blocks connect, loop, branch, and persist state. You need both. LangChain uses `RunnableSequence` for linear chains; LangGraph uses `StateGraph` for cyclic agent workflows.

| Feature | LangChain | LangGraph |
|---|---|---|
| Architecture | Linear chain | Graph (DAG + cycles) |
| State persistence | None native | SQLite / Postgres / Redis |
| Human-in-the-loop | Manual | Built-in interrupt/resume |
| Streaming | Partial (token-level) | Full (node + token level) |
| Best for | Simple pipelines | Production agents |

## Prerequisites and Environment Setup

Before writing any LangGraph code, you need a working Python environment, an LLM API key, and a clear understanding of what you're going to spend. This tutorial uses GPT-4o from OpenAI — the complete walkthrough costs under $2 in API calls, and individual queries with 2–3 tool calls typically run $0.02–$0.05 each. If you want to avoid cloud API costs entirely, LangGraph works seamlessly with local models via Ollama — plan for at least 16GB RAM and a dedicated GPU for acceptable inference speed with 7B+ parameter models. The Python version requirement is 3.9 or higher; Python 3.11 is recommended for production because async streaming performs noticeably better. You'll also want `git` installed for version control, and a terminal where you can set environment variables persistently. No prior LangChain experience is required, though familiarity with Python type annotations helps since LangGraph relies heavily on `TypedDict` for state definitions.

```bash
python -m venv .venv
source .venv/bin/activate
pip install langgraph langchain-openai langchain-community
export OPENAI_API_KEY="sk-..."
```

## Step 1: Install LangGraph and Create Project Structure

LangGraph 1.1.6 is the current stable release as of April 2026. The package is split into `langgraph` (the core graph runtime that handles state machines, node execution, and edge routing), `langgraph-checkpoint` (persistence adapters for SQLite, PostgreSQL, and in-memory storage), and `langgraph-sdk` (the client library for interacting with LangGraph Platform REST APIs). For local development you only need the core package; add checkpointing separately when you're ready to persist state across sessions. Installing with explicit version pins is strongly recommended for production — LangGraph's API surface has stabilized in the 1.x series but minor releases do introduce behavioral changes to streaming and event types. Pin both `langgraph` and `langchain-openai` in your `requirements.txt` and test upgrades in a staging environment before rolling to production.

```bash
pip install langgraph==1.1.6 langgraph-checkpoint langgraph-checkpoint-sqlite
```

Project layout to follow for this tutorial:

```
my_agent/
  agent.py         # graph definition
  tools.py         # tool implementations
  state.py         # TypedDict schema
  main.py          # entry point with streaming
```

## Step 2: Define the Agent State Schema with TypedDict

Every LangGraph graph operates on a single state object — a `TypedDict` that flows through every node and accumulates updates via reducers you declare in the type annotation. Getting the state schema right is the most important design decision in your graph, because changing it later invalidates saved checkpoints. State fields that use `Annotated[list, add_messages]` accumulate across calls using LangGraph's built-in reducer (standard for conversation history); plain unannotated fields get overwritten by the latest node update. Design your schema by asking: what information must every node be able to read? What does each node need to write? Fields that are only needed in one part of the graph can stay in that node's local variables — don't bloat state with data that doesn't need to cross node boundaries. A minimal schema runs faster and costs less to serialize into checkpoints. For complex agents, consider nested TypedDicts for grouping related fields, keeping the top-level schema clean and readable.

```python
# state.py
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tool_calls_made: int
    final_answer: str | None
```

`add_messages` is LangGraph's built-in reducer that appends new messages rather than replacing the list — critical for maintaining conversation history across tool calls.

## Step 3: Create Tools for Agent Interaction

Tools are Python functions decorated with `@tool` from LangChain. LangGraph doesn't change how you define tools — it manages how tool calls flow through the graph and how tool results are incorporated into state. The tool's docstring becomes the description the LLM uses to decide when to call it, so write clear, specific docstrings that describe what the tool does, what input it expects, and what format it returns. Keep tools focused on single operations with narrow responsibilities; the agent will compose them as needed to solve multi-step problems. Tool functions should be idempotent where possible — if the LLM retries a tool call due to a parsing error or state rollback, running the same tool twice shouldn't cause side effects like duplicate database writes or duplicate API charges. For tools that modify external state (sending emails, writing to databases), add explicit confirmation logic or rely on LangGraph's human-in-the-loop feature to gate execution.

```python
# tools.py
from langchain_core.tools import tool
import httpx

@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic."""
    response = httpx.get(f"https://api.search.example.com?q={query}")
    return response.json().get("snippet", "No results found")

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

tools = [web_search, calculate]
```

## Step 4: Build Graph Nodes for Reasoning and Execution

Nodes are Python functions that take the current state and return a partial state update as a dictionary. LangGraph merges the returned dict into the existing state using the reducers you defined in Step 2 — you only return the keys you want to update, not the entire state. Two node types drive most ReAct-style agents: the LLM reasoning node (calls the model with current messages and returns the AI response) and the tool execution node (runs whatever tools the model requested and returns the results). The reasoning node is where you configure the LLM's behavior — temperature, system prompt, and which tools it has access to via `bind_tools`. The tool node handles the mechanical work of parsing tool call requests from the AI message, executing each tool function, and formatting results as `ToolMessage` objects that the LLM can read in the next reasoning step.

```python
# agent.py
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from state import AgentState
from tools import tools

llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

def reason(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)
```

## Step 5: Wire the Graph with Conditional Edges

Edges define the control flow between nodes. Static edges always go to the same next node. Conditional edges call a router function that returns the name of the next node based on the current state. The standard agent loop is `reason → tool_node → reason → ... → END` and breaks when the model stops requesting tools. LangGraph's `tools_condition` built-in router handles this automatically: it inspects the last AI message and returns `"tools"` if tool calls are present, or `END` if not. For custom routing — sending queries to specialist agents based on topic, or routing to different processing pipelines based on output type — replace `tools_condition` with your own function that returns a node name string. The router function has full access to state, so routing decisions can be arbitrarily complex.

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition

builder = StateGraph(AgentState)
builder.add_node("reason", reason)
builder.add_node("tools", tool_node)

builder.set_entry_point("reason")
builder.add_conditional_edges(
    "reason",
    tools_condition,
    {"tools": "tools", END: END}
)
builder.add_edge("tools", "reason")

graph = builder.compile()
```

## Step 6: Run the Agent and Handle Streaming Output

Running a compiled LangGraph graph means choosing between three execution modes based on your application's needs. `invoke` is the simplest: it blocks until the graph reaches END and returns the final complete state as a dictionary — use this for batch processing or scripts where you don't need intermediate updates. `stream` yields partial state updates after each node completes, letting you show users real-time progress (e.g., "searching the web...", "calculating result...") before the final answer arrives. `astream` is the async version of `stream`, designed for FastAPI and other async web frameworks. `stream_events` gives the finest-grained view, emitting individual token emissions from LLM nodes for character-by-character streaming to frontends. Always pass a `config` dict with a `thread_id` — this becomes the checkpointer key that ties together multiple calls in the same conversation session and enables state persistence across requests.

```python
# main.py
from agent import graph

config = {"configurable": {"thread_id": "demo-001"}}

for event in graph.stream(
    {"messages": [("user", "What's 15% of $847 and what's today's weather in Tokyo?")]},
    config=config,
    stream_mode="updates"
):
    for node_name, state_update in event.items():
        print(f"[{node_name}]", state_update["messages"][-1].content[:100])
```

## Step 7: Add Persistent Memory with SQLite Checkpointing

Persistent memory is what separates a demo agent from a production one. LangGraph's checkpointer saves the complete state snapshot after every node execution, keyed by the `thread_id` from your config. When you call the same `thread_id` again, LangGraph loads the most recent checkpoint and appends new messages to the existing history — the agent remembers everything from prior turns without you explicitly managing state. This is architecturally different from simply prepending history to each prompt: checkpoints store the full graph state including intermediate tool results, branching decisions, and accumulated metadata, not just the message list. SQLite checkpointing is built into `langgraph-checkpoint-sqlite` and requires zero infrastructure setup — the entire conversation history for all threads lives in a single `.db` file. For development and single-server deployments, SQLite is ideal. For multi-instance production deployments where multiple workers need to access the same state, switch to `PostgresSaver` from `langgraph-checkpoint-postgres`.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("agent_memory.db") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    
    # First call — agent stores "Alex" in checkpoint
    graph.invoke({"messages": [("user", "My name is Alex")]}, config)
    
    # Later call — agent remembers "Alex" from checkpoint
    result = graph.invoke(
        {"messages": [("user", "What's my name?")]},
        config  # same thread_id
    )
    print(result["messages"][-1].content)  # "Your name is Alex"
```

## Step 8: Implement Human-in-the-Loop Approval Gates

Human-in-the-loop (HITL) is LangGraph's most production-critical feature and one of its clearest architectural advantages over competing frameworks. By compiling the graph with `interrupt_before=["tools"]`, execution pauses before running any tool call, saves the complete pending state to the checkpointer, and returns control to your application code. A human operator can then inspect the pending tool calls — what function the agent wants to invoke, with what arguments — and either approve, modify, or reject the action before any side effects occur. This pause-and-resume mechanism works because LangGraph's checkpointer stores the full execution context, including the position in the graph and all pending work. Resuming is as simple as calling `graph.invoke(None, config)` with the same thread ID — LangGraph loads the checkpoint, skips the interrupt, and continues execution. This pattern is mandatory for agents with write access to email systems, databases, financial APIs, or any other external system where an incorrect action is hard to reverse.

```python
graph_with_hitl = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]
)

state = graph_with_hitl.invoke(input_data, config)
pending_tools = state["messages"][-1].tool_calls
print("Pending tool calls:", pending_tools)

approved = input("Approve? (y/n): ")
if approved == "y":
    result = graph_with_hitl.invoke(None, config)
```

## Step 9: Multi-Agent Collaboration with Supervisor Pattern

The Supervisor pattern connects multiple specialist LangGraph agents as subgraphs under a single coordinator node that routes tasks based on the nature of the request. This pattern solves the context window ceiling problem in complex workflows: instead of one agent accumulating an ever-growing message history across dozens of tool calls, the supervisor delegates focused subtasks to specialist agents that each operate within a fresh, bounded context. Each specialist agent is a complete LangGraph subgraph — it receives a targeted task, executes its full reasoning and tool-use loop, and returns a result to the supervisor. The supervisor then decides whether to call another specialist, request clarification, or synthesize a final answer. This architecture also enables parallelism: independent subtasks can be dispatched to multiple specialists simultaneously using LangGraph's `Send` primitive, cutting total execution time significantly for workflows with no data dependencies between subtasks. Common specializations: web research agent, code execution agent, data analysis agent, and a final synthesis agent that aggregates results.

```python
from typing import Literal

class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str

def supervisor(state: SupervisorState) -> dict:
    response = supervisor_llm.invoke(state["messages"])
    return {"next_agent": response.content}

def route_to_agent(state: SupervisorState) -> Literal["researcher", "coder", "__end__"]:
    return state["next_agent"]

supervisor_graph = StateGraph(SupervisorState)
supervisor_graph.add_node("supervisor", supervisor)
supervisor_graph.add_node("researcher", researcher_subgraph)
supervisor_graph.add_node("coder", coder_subgraph)
supervisor_graph.add_conditional_edges("supervisor", route_to_agent)
```

## Step 10: Integration Testing for AI Agents

Testing AI agents requires a layered strategy because LLM outputs are non-deterministic and full end-to-end tests are expensive. The practical approach has three layers: structural tests that mock the LLM and verify graph topology (does execution reach END? does the right node get called?), behavioral tests that use real LLMs with recorded fixtures to check that specific inputs produce the expected tool calls or answer formats, and cost-bounded integration tests against live APIs using a smaller model like GPT-4o-mini to catch regressions before production. Mock the LLM by patching the `llm` object in your agent module with a `MagicMock` that returns pre-constructed `AIMessage` objects — this lets you test graph structure at zero API cost. For behavioral regression tests, use LangSmith's dataset feature to record golden examples and run them on a schedule to catch model drift after prompt changes or LLM upgrades.

```python
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage

def test_agent_calls_search_tool():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(
        content="",
        tool_calls=[{"name": "web_search", "args": {"query": "test"}, "id": "1"}]
    )
    with patch("agent.llm", mock_llm):
        result = graph.invoke({"messages": [("user", "Search for Python news")]}, config)
    
    assert any(msg.type == "tool" for msg in result["messages"])
```

## Step 11: Deployment with LangGraph Platform and Docker

Deploying a LangGraph agent to production means choosing between self-hosted infrastructure and LangGraph Platform (formerly LangGraph Cloud), the managed deployment service from LangChain Inc. Self-hosted gives you full control over infrastructure, cost structure, and data residency — ideal for enterprise environments with compliance requirements or teams that prefer to manage their own Kubernetes or ECS deployments. LangGraph Platform is the managed path: point a `langgraph.json` manifest at your graph module, connect a GitHub repo, and get a scalable REST API with built-in persistence, run management, and a web UI for monitoring agent executions. Platform also provides streaming endpoints, webhook callbacks for long-running tasks, and SDK clients for Python and JavaScript. For teams without dedicated DevOps, Platform eliminates weeks of infrastructure work. For the self-hosted path, a minimal Docker deployment packages your graph as a FastAPI application and runs the checkpointer against an external PostgreSQL instance.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 12: Monitoring and Observability with LangSmith

LangSmith is LangChain's observability platform and the standard monitoring solution for LangGraph agents in production. It captures every LLM call, tool invocation, state transition, and error across your graph runs — organized by thread ID and run ID — without any code changes to your agent. Enabling it requires setting two environment variables; LangGraph's integration hooks pick them up automatically. Once enabled, every `graph.invoke()` call produces a full trace in the LangSmith dashboard: token counts and costs per node, end-to-end latency, tool call inputs and outputs, intermediate state snapshots, and the graph topology visualization showing which path execution took through the graph. For production monitoring, LangSmith supports alert rules on p95 latency and error rate, dataset-based regression testing for prompt changes, and a human review queue for flagging low-confidence outputs. The free tier covers development; production deployments with high volume need the Plus or Enterprise plan.

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__..."
export LANGCHAIN_PROJECT="my-agent-prod"
```

Every `graph.invoke()` call now appears in the LangSmith dashboard with full trace: token counts, latency per node, tool call inputs/outputs, and cost estimates.

## Advanced Patterns: Parallel Execution and Error Recovery

LangGraph's execution model supports true parallelism within a graph run by fanning out to multiple independent nodes simultaneously. When you add edges from one source node to multiple destination nodes with no dependency between them, LangGraph schedules them as concurrent coroutines — on IO-bound workloads like parallel web searches or multiple API calls, this can reduce end-to-end latency by 60–80% compared to sequential execution. The `Send` primitive enables dynamic fan-out: your router function returns a list of `Send` objects, each targeting a node with custom input data, rather than returning a single node name string. Results from parallel branches merge back into state via reducers when all branches complete. Error recovery follows a similar pattern — rather than letting tool exceptions propagate and crash the run, wrap tool nodes in try/except and return structured error messages to state, letting the LLM reason about whether to retry, use a fallback tool, or report the failure to the user cleanly.

### Parallel Tool Execution with Fan-Out

```python
from langgraph.graph import Send

def fan_out_tools(state: AgentState):
    tool_calls = state["messages"][-1].tool_calls
    return [Send("execute_tool", {"tool_call": tc}) for tc in tool_calls]

builder.add_conditional_edges("reason", fan_out_tools)
```

### Error Recovery with Graceful Fallback

Wrap tool nodes in try/except and return error messages to state rather than raising — the agent can then decide whether to retry, use a fallback, or report failure to the user.

## Framework Comparison: LangGraph vs CrewAI vs AutoGen

LangGraph occupies a specific niche in the AI agent framework ecosystem: it's the right choice when you need precise, explicit control over agent execution topology, persistent state across sessions, or human-in-the-loop approval gates at specific points in the workflow. CrewAI abstracts away the graph topology entirely in favor of role-based team simulations — you define agents by their roles and goals, and CrewAI infers the execution order. This is faster for prototyping but harder to customize at production scale. AutoGen from Microsoft Research is strongest for conversational multi-agent setups where agents collaborate through natural language dialogue rather than explicit graph transitions. As of 2026, LangGraph's 126,000+ GitHub stars and active enterprise adoption make it the most production-battle-tested choice of the three. The framework comparison below covers the dimensions that matter most when choosing for a production project.

| Dimension | LangGraph | CrewAI | AutoGen |
|---|---|---|---|
| Abstraction level | Low (explicit graph) | Medium (role-based) | Medium (conversational) |
| State management | Explicit TypedDict | Implicit | Message history |
| HITL support | Native interrupt/resume | Manual | Via human proxy agent |
| Parallel execution | Fan-out edges | Sequential by default | Async support |
| Production maturity | High (126k stars, 2026) | Medium | Medium |
| Best for | Complex cyclic agents | Team workflows | Chat-based multi-agent |

## Troubleshooting Common LangGraph Issues

**Graph never reaches END:** Check that `tools_condition` has `END` (the actual object from `langgraph.graph`) in the edge mapping, not the string `"END"`. Use `graph.get_graph().draw_ascii()` to visualize the topology and confirm edges are wired as expected.

**State not persisting between calls:** Confirm you're passing the same `config` dict with identical `thread_id` on every invocation, and that the checkpointer was compiled into the graph (not just imported).

**Tool calls not executing:** Verify `bind_tools(tools)` was called on the LLM instance. Check `print(state["messages"][-1].tool_calls)` to confirm the LLM is generating tool call objects.

**Infinite loops:** Add a step counter to state and a conditional edge that routes to END when `steps > MAX_STEPS`. `tools_condition` won't catch LLMs that always request tools.

**Checkpoint migration errors:** When you change `AgentState`, existing checkpoints may be incompatible. Use a new `thread_id` or delete the SQLite file during development. For production, implement checkpoint migration scripts before deploying schema changes.

## FAQ

LangGraph is now the dominant production AI agent framework in 2026, with 126,000+ GitHub stars and active adoption from enterprises running agents at scale. As teams move from prototype to production with LangGraph, five questions come up repeatedly: Python version compatibility, local/offline usage with Ollama, handling context length limits in long-running agents, understanding the difference between the execution modes (`invoke`, `stream`, `astream`, `stream_events`), and whether LangGraph is truly production-ready or still primarily a research and prototyping tool. The answers below are drawn from real production experience and cover the specific configuration choices that matter at scale. Whether you're building your first agent or debugging a multi-agent system serving hundreds of concurrent users, these answers address the most common sources of confusion that developers encounter after completing the basic tutorial steps above.

### What Python version does LangGraph 1.1.6 require?

LangGraph 1.1.6 requires Python 3.9 or higher, with Python 3.11 and 3.12 recommended for production. The async streaming features work best on 3.11+. JavaScript/TypeScript support is available via `@langchain/langgraph`.

### Can LangGraph work without an internet connection?

Yes. Combine LangGraph with Ollama for a fully local setup. Pull a model like `llama3` or `mistral` via `ollama pull`, then use `ChatOllama` from `langchain-community` instead of `ChatOpenAI`. You'll need at least 16GB RAM for 7B models; 32GB for 13B models at acceptable inference speed.

### How does LangGraph handle long-running agents that exceed context length?

Use LangGraph's built-in message trimming with `trim_messages` from LangChain, or implement a `summarize` node that compresses old messages when `len(messages) > N`. The supervisor pattern also helps: route specific subtasks to fresh subgraph instances with clean context windows.

### What's the difference between `invoke`, `stream`, and `astream`?

`invoke` blocks until the graph completes and returns the final state. `stream` yields state updates after each node completes (good for showing progress). `astream` is the async version of `stream` for use in async web servers (FastAPI, etc.). `stream_events` provides the lowest-level view: individual token emissions from LLM nodes.

### Is LangGraph suitable for production workloads or just prototyping?

LangGraph is production-ready. Companies including major financial institutions run LangGraph agents at scale for fraud detection, document processing, and customer support workflows. The main production considerations: use PostgreSQL checkpointer for multi-instance deployments, instrument with LangSmith for observability, and implement HITL gates for any action with real-world side effects.