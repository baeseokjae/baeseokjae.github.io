---
cover:
  alt: 'LangGraph TypeScript Guide: Build AI Agents in 2026'
  image: /images/langgraph-typescript-guide-2026.png
  relative: false
date: 2026-05-05 21:03:58+00:00
description: 'Complete LangGraph TypeScript guide for 2026: StateGraph, streaming,
  checkpointing, HITL, and multi-agent systems with real code examples.'
draft: false
schema: schema-langgraph-typescript-guide-2026
tags:
- LangGraph
- TypeScript
- AI Agents
- LangChain
- JavaScript
title: 'LangGraph TypeScript Guide: Build AI Agents in 2026'
---

LangGraph TypeScript (`@langchain/langgraph`) lets you build stateful, graph-based AI agents in Node.js with full type safety. As of 2026, it handles StateGraph, conditional edges, checkpointing, streaming, and human-in-the-loop — feature-parity with the Python version — and sees over 42,000 weekly npm downloads.

## What Is LangGraph TypeScript (and Why It Matters in 2026)

LangGraph TypeScript is a production-ready library for building stateful AI agent systems using a directed graph model, where nodes represent actions and edges represent transitions between states. Unlike simple chain-based frameworks, LangGraph lets agents loop, branch, pause for human input, and recover from failures without losing context. It reached full production stability in mid-2025, with feature parity to the Python version including StateGraph, conditional edges, checkpointing, streaming, and human-in-the-loop (HITL). The `@langchain/langgraph` npm package now records over 42,000 weekly downloads as of April 2026, making it the most-used graph-based agent framework in the JavaScript ecosystem.

Why does the graph model matter? Traditional LLM chains run top-to-bottom: prompt → LLM → output. That works for one-shot tasks but breaks down when agents need to retry, use tools, wait for approval, or coordinate with other agents. LangGraph models those workflows as graphs — each node is a function, each edge is a routing decision — giving you explicit control over execution flow. Companies like Klarna (85M active users), Replit, Uber, LinkedIn, GitLab, and Elastic all run LangGraph in production, which signals that the framework handles real scale. For TypeScript teams specifically, the type system catches entire categories of state-shape bugs at compile time that Python users only discover at runtime.

## Prerequisites and Installation (@langchain/langgraph Setup)

Setting up `@langchain/langgraph` requires Node.js 20 or later and TypeScript 5.4 or later — older versions lack the ES2022 features (structuredClone, native top-level await, improved class field semantics) that the library depends on. You also need an LLM provider package (typically `@langchain/openai` or `@langchain/anthropic`) and optionally `@langchain/community` for tool integrations like Tavily search or Wikipedia. The `zod` package is strongly recommended for defining tool input schemas with TypeScript type inference. For persistence, install `@langchain/langgraph-checkpoint-postgres` or `@langchain/langgraph-checkpoint-redis` depending on your production infrastructure — the in-process `MemorySaver` that ships with the core package is only suitable for local development. The full install for a production project looks like this:

```bash
npm install @langchain/langgraph @langchain/openai @langchain/core zod
```

Configure TypeScript with strict mode and module resolution set to `bundler` or `node16`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "outDir": "dist"
  }
}
```

Set your API key in the environment:

```bash
export OPENAI_API_KEY="sk-..."
```

For production projects, the `@langgraphjs/toolkit` companion package adds observability hooks, retry utilities, and structured error types. Run `npm install @langgraphjs/toolkit` and import it alongside the core library.

### Verifying the Install

Create `src/hello.ts` and confirm the import resolves:

```typescript
import { StateGraph, END, START } from "@langchain/langgraph";
console.log("LangGraph ready");
```

Run with `npx ts-node src/hello.ts`. If it prints without error, your environment is correctly set up.

## Core Concepts: StateGraph, Nodes, and Edges Explained

A `StateGraph` in LangGraph TypeScript is the central data structure that defines what your agent remembers (state), what it can do (nodes), and how it decides what to do next (edges). State is a typed object — typically defined with Zod or TypeScript interfaces — that flows through every node in the graph. Each node receives the current state, performs some action (calling an LLM, running a tool, making an API request), and returns a partial state update. The graph merges that update into the running state before routing to the next node. This model is how LangGraph agents maintain context across dozens of tool calls without losing information or re-prompting for context already established.

Here is the minimal structure of a LangGraph TypeScript app:

```typescript
import { StateGraph, END, START, Annotation } from "@langchain/langgraph";

// 1. Define state schema with Annotation
const AgentState = Annotation.Root({
  messages: Annotation<string[]>({
    reducer: (prev, next) => [...prev, ...next],
    default: () => [],
  }),
  status: Annotation<"running" | "done">({
    reducer: (_, next) => next,
    default: () => "running",
  }),
});

// 2. Define a node
async function myNode(state: typeof AgentState.State) {
  return { messages: ["Hello from node"], status: "done" as const };
}

// 3. Build the graph
const graph = new StateGraph(AgentState)
  .addNode("myNode", myNode)
  .addEdge(START, "myNode")
  .addEdge("myNode", END)
  .compile();

// 4. Run
const result = await graph.invoke({ messages: [], status: "running" });
console.log(result);
```

### Reducers: How State Merges

The `reducer` function in each `Annotation` field controls how partial updates merge into state. For message history, you almost always want `(prev, next) => [...prev, ...next]` — append semantics. For a status field, you want `(_, next) => next` — last-write-wins. Getting reducers right is the most common source of bugs in early LangGraph projects.

### Conditional Edges

Edges can be static (`addEdge`) or conditional (`addConditionalEdges`). Conditional edges take a routing function that inspects state and returns the name of the next node:

```typescript
graph.addConditionalEdges("router", (state) => {
  return state.status === "done" ? END : "worker";
});
```

## Building Your First ReAct Agent in TypeScript

A ReAct (Reasoning + Acting) agent is the most common LangGraph pattern: the LLM reasons about what to do, calls a tool, observes the result, and repeats until it has a final answer. LangGraph TypeScript implements this as a two-node loop — one node calls the LLM, one node executes tools — connected by a conditional edge that routes to END when the LLM stops requesting tools. This pattern is behind the majority of production LangGraph deployments at companies like Klarna and Replit, where the agent must search databases, call APIs, and synthesize multi-step results before responding to users.

```typescript
import { StateGraph, END, START, Annotation } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { BaseMessage, HumanMessage } from "@langchain/core/messages";

// Define a tool
const searchTool = tool(
  async ({ query }: { query: string }) => {
    return `Search results for: ${query} — found 3 relevant documents.`;
  },
  {
    name: "search",
    description: "Search the web for information",
    schema: z.object({ query: z.string().describe("The search query") }),
  }
);

const tools = [searchTool];
const model = new ChatOpenAI({ model: "gpt-4o" }).bindTools(tools);

// State uses BaseMessage array for LangChain message history
const AgentState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (prev, next) => [...prev, ...next],
    default: () => [],
  }),
});

// Node 1: call the LLM
async function callModel(state: typeof AgentState.State) {
  const response = await model.invoke(state.messages);
  return { messages: [response] };
}

// Routing: did the LLM request a tool call?
function shouldContinue(state: typeof AgentState.State) {
  const lastMessage = state.messages[state.messages.length - 1];
  if ("tool_calls" in lastMessage && (lastMessage as any).tool_calls?.length > 0) {
    return "tools";
  }
  return END;
}

// Node 2: execute tools
const toolNode = new ToolNode(tools);

const reactGraph = new StateGraph(AgentState)
  .addNode("agent", callModel)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile();

// Run the agent
const result = await reactGraph.invoke({
  messages: [new HumanMessage("What are the latest TypeScript 5.5 features?")],
});
console.log(result.messages.at(-1)?.content);
```

The key detail: `ToolNode` from `@langchain/langgraph/prebuilt` handles serialization, error catching, and message formatting automatically. Don't implement tool execution by hand.

## Adding Real-Time Streaming to Your LangGraph Agent

Streaming in LangGraph TypeScript lets users see the agent's reasoning and partial outputs as they happen, instead of waiting for a complete response. This matters enormously for UX: research from Vercel and Anthropic both show that users tolerate 3-5x longer wait times when they see progress. LangGraph supports two streaming modes — `"values"` streams the full state after each node, and `"messages"` streams individual LLM tokens as they generate. For chat interfaces, you almost always want `"messages"` mode. For debugging pipelines, `"values"` gives you a snapshot of state at each step.

```typescript
// Stream tokens from the agent
const stream = await reactGraph.stream(
  { messages: [new HumanMessage("Explain LangGraph checkpointing")] },
  { streamingMode: "messages" }
);

for await (const [message, metadata] of stream) {
  if (
    message._getType() === "AIMessageChunk" &&
    metadata.langgraph_node === "agent"
  ) {
    process.stdout.write(message.content as string);
  }
}
```

### Streaming in Next.js with the Vercel AI SDK

For Next.js apps, pipe LangGraph stream output through the Vercel AI SDK's `LangChainAdapter`:

```typescript
import { LangChainAdapter } from "ai";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const stream = await reactGraph.stream({ messages });
  return LangChainAdapter.toDataStreamResponse(stream);
}
```

This gives you `useChat()` hook compatibility on the frontend with zero extra plumbing.

## Persistence and Checkpointing: From MemorySaver to PostgreSQL

LangGraph checkpointing saves the full graph state after each node execution, enabling agents to pause, resume across restarts, and support human-in-the-loop interrupts. Without checkpointing, every agent run starts from scratch — no memory of previous interactions, no ability to pause for user input mid-execution. With checkpointing, your agent becomes stateful across sessions. LangGraph TypeScript ships with `MemorySaver` (in-process, for development) and supports PostgreSQL, Redis, and custom backends for production. The key design decision: all checkpointers implement the same interface, so you switch from `MemorySaver` to `PostgresSaver` with one line change — no agent code modifications required.

```typescript
import { MemorySaver } from "@langchain/langgraph";

// Development: in-memory checkpointing
const memorySaver = new MemorySaver();
const graphWithMemory = new StateGraph(AgentState)
  .addNode("agent", callModel)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile({ checkpointer: memorySaver });

// Each thread_id is an isolated conversation
const config = { configurable: { thread_id: "user-123-session-456" } };

const result1 = await graphWithMemory.invoke(
  { messages: [new HumanMessage("My name is Alex")] },
  config
);

const result2 = await graphWithMemory.invoke(
  { messages: [new HumanMessage("What is my name?")] },
  config // same thread_id = agent remembers "Alex"
);
```

### Switching to PostgreSQL in Production

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const postgresSaver = PostgresSaver.fromConnString(process.env.DATABASE_URL!);
await postgresSaver.setup(); // creates checkpoint tables

const productionGraph = reactGraph.compile({ checkpointer: postgresSaver });
```

The `thread_id` pattern maps naturally to user sessions, document IDs, or any entity that needs isolated state.

## Human-in-the-Loop: Pause, Review, and Resume Agent Execution

Human-in-the-loop (HITL) in LangGraph TypeScript lets you pause agent execution at a specific node, surface the pending action to a human for review, and resume only after approval. This is critical for high-stakes operations: financial transactions, sending emails, writing to production databases, or deleting records. Without HITL, autonomous agents operating on real systems create unacceptable risk. LangGraph implements HITL through `interrupt_before` — a compile-time option that tells the graph to pause before executing a named node and save state to the checkpointer. The human reviews the pending state, approves or modifies it, and calls `graph.invoke()` again with the same `thread_id` to resume. No state is lost during the pause.

```typescript
// Compile with interrupt_before the "tools" node
const hitlGraph = new StateGraph(AgentState)
  .addNode("agent", callModel)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile({
    checkpointer: memorySaver,
    interruptBefore: ["tools"], // pause before tool execution
  });

const config = { configurable: { thread_id: "approval-flow-001" } };

// First run: agent reasons, then pauses before tool call
const step1 = await hitlGraph.invoke(
  { messages: [new HumanMessage("Delete all records from the test table")] },
  config
);

// Inspect what the agent wants to do
const pendingState = await hitlGraph.getState(config);
console.log("Agent wants to call:", pendingState.values.messages.at(-1));

// Human approves: resume by calling invoke again with same config
// (no new messages needed — state is persisted)
const finalResult = await hitlGraph.invoke(null, config);
```

### Modifying State Before Resume

To reject or modify the pending action, use `updateState` before resuming:

```typescript
await hitlGraph.updateState(config, {
  messages: [new HumanMessage("Actually, only delete records from last week")],
});
const revised = await hitlGraph.invoke(null, config);
```

## Building Multi-Agent Systems with LangGraph TypeScript

Multi-agent systems in LangGraph TypeScript use a supervisor/worker pattern where a coordinator agent routes tasks to specialized sub-agents based on the task requirements. Each sub-agent is a compiled LangGraph graph with its own state, tools, and logic — the supervisor treats sub-agents as nodes in its own graph. This architecture separates concerns: a coding agent handles code generation, a research agent handles web search, a writer agent handles document synthesis. In 2026, LangGraph's `@langchain/langgraph` supports two coordination patterns: supervisor (central router decides) and swarm (agents hand off directly to each other using `Command` returns).

```typescript
import { Command } from "@langchain/langgraph";

// Worker agents as nodes that return Command for routing
async function researchWorker(state: typeof AgentState.State) {
  const result = await researchGraph.invoke({ messages: state.messages });
  return new Command({
    update: { messages: result.messages },
    goto: "supervisor", // hand back to supervisor
  });
}

async function codeWorker(state: typeof AgentState.State) {
  const result = await codeGraph.invoke({ messages: state.messages });
  return new Command({
    update: { messages: result.messages },
    goto: "supervisor",
  });
}

// Supervisor routes to workers
async function supervisor(state: typeof AgentState.State) {
  const lastMessage = state.messages.at(-1)?.content as string;
  if (lastMessage.includes("search") || lastMessage.includes("research")) {
    return new Command({ goto: "research_worker" });
  }
  if (lastMessage.includes("code") || lastMessage.includes("implement")) {
    return new Command({ goto: "code_worker" });
  }
  return new Command({ goto: END });
}

const multiAgentGraph = new StateGraph(AgentState)
  .addNode("supervisor", supervisor)
  .addNode("research_worker", researchWorker)
  .addNode("code_worker", codeWorker)
  .addEdge(START, "supervisor")
  .compile({ checkpointer: memorySaver });
```

### When to Use Supervisor vs Swarm

Use **supervisor** when tasks have clear categories and the coordinator needs to track overall progress. Use **swarm** (direct `Command` handoffs) when agents need to chain dynamically based on intermediate results — like a research agent discovering it needs code generated and handing off directly without returning to supervisor.

## LangGraph TypeScript vs Mastra vs Vercel AI SDK: Which Should You Choose?

LangGraph TypeScript is the best choice for stateful, long-running agent workflows that require explicit control over execution flow, checkpointing, and human-in-the-loop interrupts. As of 2026, four frameworks dominate the TypeScript AI agent space: LangGraph (graph-based, stateful), Mastra (TypeScript-first, Vercel-native), Vercel AI SDK (streaming-first, serverless-optimized), and OpenAI Agents SDK (provider-locked, simple handoffs). Each occupies a different niche — TypeScript teams switching from LangGraph to Mastra report setup time reduction from ~41 hours to ~18 hours for simple deployments, but Mastra lacks LangGraph's granular checkpointing and conditional routing for complex workflows. LangGraph still leads for durable, stateful, graph-based workflows.

| Feature | LangGraph TS | Mastra | Vercel AI SDK | OpenAI Agents SDK |
|---|---|---|---|---|
| State persistence | PostgreSQL, Redis, custom | Built-in (Postgres) | Stateless by default | None |
| Human-in-the-loop | Native `interruptBefore` | Plugin-based | Not supported | Not supported |
| Streaming | `"messages"` + `"values"` | Supported | Core feature | Basic |
| Multi-agent | Supervisor + Swarm | Workflows | Not built-in | Handoffs |
| TypeScript safety | Strong (Annotation API) | Strong | Strong | Basic |
| Learning curve | High | Medium | Low | Low |
| Best for | Complex stateful agents | Next.js/Vercel teams | Chat UIs, edge | OpenAI-only projects |

### When to Pick Each Framework

**LangGraph TypeScript**: Stateful agents with complex routing, HITL for high-stakes ops, multi-agent systems, long-running workflows across sessions.

**Mastra**: TypeScript-first teams on Vercel/Next.js infrastructure who need agents integrated into existing serverless deployments with faster initial setup.

**Vercel AI SDK**: Chat interfaces and streaming UIs where agents are relatively simple and serverless execution is the constraint.

**OpenAI Agents SDK**: Prototypes or teams fully committed to OpenAI models who want minimal configuration and are comfortable with provider lock-in.

## Production Deployment Best Practices and Observability

Deploying LangGraph TypeScript agents to production requires attention to four areas: checkpointer durability, error handling, observability, and resource limits. The most common production failure mode is using `MemorySaver` in production — it doesn't persist across process restarts, so agent state is lost on every deploy. Switch to `PostgresSaver` or `RedisSaver` before going live. For observability, LangSmith (LangChain's tracing platform) integrates natively with LangGraph TypeScript: set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` and every node execution, LLM call, and tool invocation appears in the LangSmith dashboard with full token counts and latency. Companies like LinkedIn and GitLab use this for production monitoring of their LangGraph deployments.

```typescript
// Production-ready graph configuration
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

const productionSaver = PostgresSaver.fromConnString(process.env.DATABASE_URL!);
await productionSaver.setup();

const productionGraph = new StateGraph(AgentState)
  .addNode("agent", callModel)
  .addNode("tools", toolNode)
  .addEdge(START, "agent")
  .addConditionalEdges("agent", shouldContinue)
  .addEdge("tools", "agent")
  .compile({
    checkpointer: productionSaver,
    interruptBefore: process.env.REQUIRE_APPROVAL === "true" ? ["tools"] : [],
  });
```

### Setting LangSmith Tracing

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls__..."
export LANGCHAIN_PROJECT="my-production-agent"
```

Every graph invocation automatically sends traces to LangSmith — no code changes needed.

### Resource Limits and Timeouts

Agents in production loops can run indefinitely if the routing logic has a bug. Set recursion limits to catch runaway loops:

```typescript
const result = await productionGraph.invoke(
  { messages: [new HumanMessage(userInput)] },
  {
    configurable: { thread_id: sessionId },
    recursionLimit: 25, // max 25 node executions per invoke
  }
);
```

Also implement timeout wrappers for tool calls — external APIs can hang, and a hanging tool call blocks the entire agent thread.

### Deployment Options

**LangGraph Cloud**: Managed hosting with built-in persistence, scaling, and the LangGraph Studio debugger. Best for teams that want zero infrastructure management.

**Self-hosted on Railway/Fly.io**: Deploy as a Node.js service with `DATABASE_URL` pointing to a managed PostgreSQL instance. More control, similar simplicity.

**Vercel Edge Functions**: Works with Vercel AI SDK adapter for streaming, but `MemorySaver` only — no persistent checkpointing. Good for stateless chat agents.

---

## FAQ

**Q: Can I use LangGraph TypeScript without LangChain?**
Yes. `@langchain/langgraph` has minimal coupling to LangChain — you can use any LLM provider by wrapping it in a function that returns `BaseMessage` objects. The `@langchain/openai` and `@langchain/anthropic` packages are optional convenience wrappers.

**Q: What is the difference between `MemorySaver` and `PostgresSaver`?**
`MemorySaver` stores checkpoint state in process memory — it's fast, zero-config, and ideal for development and testing, but loses all state on process restart. `PostgresSaver` persists state to a PostgreSQL database, surviving restarts and scaling across multiple instances. Always use `PostgresSaver` (or `RedisSaver`) in production.

**Q: How do I debug a LangGraph agent that is looping indefinitely?**
First, set `recursionLimit` in your invoke config (e.g., `{ recursionLimit: 25 }`). Then enable LangSmith tracing to visualize the node execution sequence. Common causes: the conditional edge routing function never returns `END`, a tool call always fails and the agent retries infinitely, or state mutation produces a different result on each pass.

**Q: Is LangGraph TypeScript production-ready in 2026?**
Yes. LangGraph TypeScript reached production stability in mid-2025 with full feature parity to the Python version. Companies including Klarna (85M users), LinkedIn, Replit, Uber, and GitLab run LangGraph in production. The `@langchain/langgraph` package sees over 42,000 weekly npm downloads as of April 2026.

**Q: How does LangGraph TypeScript handle concurrent agent runs?**
Each run is scoped to a `thread_id` in the checkpointer. Multiple concurrent `thread_id` values execute independently — there is no shared mutable state across threads. For true parallel execution within a single agent run, LangGraph supports fan-out edges where multiple nodes execute concurrently and fan back in through a merge node.