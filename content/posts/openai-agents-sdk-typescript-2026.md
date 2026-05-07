---
title: "OpenAI Agents SDK TypeScript: Complete Developer Guide 2026"
date: 2026-05-06T15:04:46+00:00
tags: ["OpenAI Agents SDK", "TypeScript", "AI agents", "multi-agent", "MCP"]
description: "Build production-ready AI agents in TypeScript with the OpenAI Agents SDK — handoffs, tools, guardrails, sessions, MCP, and voice agents explained."
draft: false
cover:
  image: "/images/openai-agents-sdk-typescript-2026.png"
  alt: "OpenAI Agents SDK TypeScript: Complete Developer Guide 2026"
  relative: false
schema: "schema-openai-agents-sdk-typescript-2026"
---

The OpenAI Agents SDK for TypeScript (`@openai/agents`) is a production-ready framework for building multi-agent AI systems in Node.js and browser environments. It ships four core primitives — Agents, Tools, Handoffs, and Guardrails — with first-class Zod integration, MCP support, and a dedicated RealtimeAgent for voice workflows.

## What Is the OpenAI Agents SDK for TypeScript?

The OpenAI Agents SDK for TypeScript is an open-source framework published as `@openai/agents` on npm, reaching approximately 1.5 million downloads in a single 30-day window as of March 2026. It is the official TypeScript successor to Swarm, OpenAI's earlier multi-agent experimentation library, and it ships production primitives that Swarm deliberately omitted: persistent sessions, guardrails, MCP tool servers, and a RealtimeAgent for speech-to-speech voice applications. Unlike the Python version — which has 19,000+ GitHub stars and 10.3 million monthly downloads — the TypeScript SDK targets developers who live in Node.js, Next.js, or edge runtimes where Python workers are not viable. The SDK wraps the OpenAI Chat Completions and Responses APIs, handles tool-call loops automatically, and lets you compose complex multi-agent pipelines without writing state machines by hand. It reached 2,100 GitHub stars and 128K weekly downloads within its first months, signaling fast adoption among the TypeScript AI community.

### Why TypeScript Instead of the Python SDK?

The TypeScript SDK is the right choice when your application already runs on Node.js, when you need browser-side agent execution, or when type safety at the tool-schema layer is critical. Zod schemas defined in TypeScript are automatically converted to JSON Schema for function calling — meaning your tool interfaces are type-checked at compile time and validated at runtime with a single source of truth. The SDK also ships RealtimeAgent and RealtimeSession, the voice-agent primitives that connect to OpenAI's speech-to-speech WebRTC pipeline — a TypeScript-first feature that has no equivalent in the Python SDK's current public interface.

## Installation and Setup

Setting up `@openai/agents` takes under two minutes for any Node.js project. The package requires Node 18+ and ships ESM-first, though CommonJS interop works via `require()` in recent versions. You will also install `zod` for tool schema definition and `openai` as a peer dependency if it is not already present. As of May 2026, the package is published as `@openai/agents` on npm and receives weekly releases with bug fixes and new features. The installation surface is intentionally minimal: three packages total for a full-featured agent runtime, compared to LangChain's 15+ required packages for equivalent functionality. This small footprint makes `@openai/agents` fast to install in CI pipelines, Docker build layers, and serverless cold starts where dependency count directly affects startup time.

```bash
npm install @openai/agents zod openai
```

Set your API key as an environment variable. The SDK reads `OPENAI_API_KEY` automatically:

```bash
export OPENAI_API_KEY="sk-..."
```

For TypeScript projects, ensure your `tsconfig.json` targets ES2022 or later and enables `moduleResolution: "bundler"` or `"node16"`. The SDK uses top-level `await` internally and ships declaration files for all public APIs:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true
  }
}
```

### Environment Variable Configuration

Beyond the API key, the SDK respects `OPENAI_MODEL` to override the default model (`gpt-4o`) and `OPENAI_BASE_URL` for custom endpoints such as Azure OpenAI or local Ollama proxies. For tracing, set `OPENAI_TRACE=1` to enable console trace output during development. Production applications should pass these values programmatically via the `OpenAI` client constructor rather than relying on environment variables to keep credentials out of process environments in container workloads.

## Your First Agent in 10 Lines of TypeScript

The OpenAI Agents SDK reduces agent creation to three steps: define an `Agent`, call `run()` with a user message, and read the output. The `Runner` class handles the full tool-call loop — model inference, tool dispatch, result injection, and termination — without any additional scaffolding from the developer's side.

```typescript
import { Agent, run } from "@openai/agents";

const agent = new Agent({
  name: "Greeter",
  model: "gpt-4o",
  instructions: "You are a helpful assistant. Answer concisely.",
});

const result = await run(agent, "What is the capital of Japan?");
console.log(result.finalOutput); // "Tokyo"
```

`run()` returns a `RunResult` object with `finalOutput` (the last assistant message), `messages` (the full conversation history), and `toolCalls` (an array of every tool invocation that occurred). For streaming responses, swap `run()` for `runStream()`, which returns an async iterable of `StreamEvent` objects compatible with the Vercel AI SDK's stream protocol.

### Understanding the RunResult Object

The `RunResult` contains more than just the final answer. `result.usage` exposes prompt and completion token counts, `result.turnCount` reports how many model-tool round trips occurred, and `result.lastAgent` identifies which agent produced the final output — critical for multi-agent pipelines where handoffs transfer control mid-conversation. Inspecting these fields in development helps you tune instructions, catch runaway tool loops, and estimate per-request costs before they appear on your OpenAI bill.

## Function Tools with Zod — Automatic Schema Generation

Function tools are the mechanism by which agents call external code — APIs, databases, file systems, or any arbitrary logic you write. The TypeScript SDK uses Zod schemas to derive JSON Schema definitions automatically, eliminating the boilerplate of hand-writing parameter descriptions and type annotations. Define your input schema with `z.object()`, wrap the function with `tool()`, and the SDK handles registration, validation, and error surfacing.

```typescript
import { Agent, run, tool } from "@openai/agents";
import { z } from "zod";

const weatherTool = tool({
  name: "get_weather",
  description: "Returns the current temperature for a given city.",
  parameters: z.object({
    city: z.string().describe("The city name, e.g. 'Tokyo'"),
    unit: z.enum(["celsius", "fahrenheit"]).default("celsius"),
  }),
  execute: async ({ city, unit }) => {
    // Real implementation would call a weather API
    return `${city}: 22°${unit === "celsius" ? "C" : "F"}, partly cloudy`;
  },
});

const agent = new Agent({
  name: "WeatherBot",
  model: "gpt-4o",
  instructions: "Use the weather tool when users ask about temperature.",
  tools: [weatherTool],
});

const result = await run(agent, "What's the weather in Tokyo?");
console.log(result.finalOutput);
```

### Tool Error Handling and Retries

When `execute` throws, the SDK catches the error and feeds a formatted error message back to the model rather than crashing the run. The model can then decide to retry with corrected parameters, fall back to a different tool, or explain the failure to the user. You can customize this behavior by returning `{ error: string }` from `execute` instead of throwing — giving the model richer context about what went wrong and how to recover. For tools that call flaky external APIs, wrapping `execute` with a retry library like `p-retry` is recommended before surfacing errors to the model loop.

## Multi-Agent Orchestration with Handoffs

Handoffs allow one agent to transfer control to another agent mid-conversation, enabling modular architectures where specialized agents handle specific domains. A triage agent might classify user intent and hand off to a billing agent, a technical support agent, or an escalation agent — without any hardcoded routing logic in the orchestration layer. Handoffs preserve conversation history across transfers, so the receiving agent has full context.

```typescript
import { Agent, run, handoff } from "@openai/agents";

const billingAgent = new Agent({
  name: "BillingAgent",
  instructions: "Handle invoice questions, payment issues, and subscription changes.",
});

const techSupportAgent = new Agent({
  name: "TechSupportAgent",
  instructions: "Troubleshoot technical problems: bugs, outages, and API errors.",
});

const triageAgent = new Agent({
  name: "TriageAgent",
  instructions: `
    Classify user requests and hand off to the right specialist:
    - billing/payment → BillingAgent
    - technical issues → TechSupportAgent
    Do not answer questions directly — always hand off.
  `,
  handoffs: [handoff(billingAgent), handoff(techSupportAgent)],
});

const result = await run(triageAgent, "My invoice shows the wrong amount.");
console.log(result.lastAgent.name); // "BillingAgent"
console.log(result.finalOutput);
```

### Handoff Conditions and Callbacks

Handoffs can carry `onHandoff` callbacks that execute custom code before control transfers — useful for logging, analytics, or injecting context into the next agent's instructions. The `handoff()` factory accepts an `inputSchema` argument that lets you require structured data from the handing-off agent before the transfer occurs, preventing incomplete context from crossing agent boundaries. This pattern is especially valuable in customer service workflows where the first-contact agent must collect account ID and issue type before escalating.

## Guardrails: Input and Output Validation

Guardrails are validation layers that run alongside agent execution, checking user input before it reaches the model or inspecting model output before it reaches the user. The SDK ships input guardrails (run on the initial user message) and output guardrails (run on each assistant response), with a `GuardrailFunctionOutput` return type that signals PASS or FAIL. When a guardrail trips, the run terminates with a `GuardrailTripwireTriggered` error rather than continuing to an unsafe state.

```typescript
import { Agent, run, inputGuardrail, GuardrailFunctionOutput } from "@openai/agents";

const toxicityGuardrail = inputGuardrail({
  name: "toxicity_check",
  execute: async ({ input }): Promise<GuardrailFunctionOutput> => {
    const hasToxicContent = /\b(spam|abuse)\b/i.test(input);
    return {
      tripwire: hasToxicContent,
      output: { isSafe: !hasToxicContent },
    };
  },
});

const agent = new Agent({
  name: "SafeBot",
  instructions: "Be helpful and safe.",
  inputGuardrails: [toxicityGuardrail],
});

try {
  await run(agent, "Normal user question");
} catch (e) {
  // Catches GuardrailTripwireTriggered for flagged input
  console.error("Input blocked by guardrail:", e.message);
}
```

Guardrails are intentionally lightweight — they are not meant to replace dedicated safety classifiers like OpenAI's Moderation API, but to enforce application-level policies like length limits, topic restrictions, or PII detection. For production, stack multiple guardrails in the array; they run in order and short-circuit on the first trip.

## Sessions and Persistent Memory

Sessions are the mechanism by which agents maintain conversation context across multiple turns without the caller manually managing message history. The SDK ships two built-in session types: `OpenAIConversationsSession`, which stores history server-side via the OpenAI Conversations API, and `MemorySession`, an in-process store useful for testing and single-process deployments. Without sessions, every call to `run()` starts a blank conversation; the caller must manually prepend prior messages to the input on each turn. Sessions eliminate that boilerplate and make multi-turn workflows — customer support threads, code review loops, guided onboarding flows — straightforward to implement. For production deployments, the `Session` interface is open for custom backends, so teams can bring their existing Redis or DynamoDB infrastructure rather than adopting a new data store.

```typescript
import { Agent, run } from "@openai/agents";
import { MemorySession } from "@openai/agents/sessions";

const session = new MemorySession();

const agent = new Agent({
  name: "MemoryBot",
  instructions: "Remember what the user tells you in this session.",
});

// First turn
await run(agent, "My name is Alex.", { session });

// Second turn — agent remembers "Alex" without re-sending history
const result = await run(agent, "What's my name?", { session });
console.log(result.finalOutput); // "Your name is Alex."
```

### Custom Memory Backends

For production deployments where session state must survive process restarts, implement the `Session` interface and plug in any durable store — Redis, DynamoDB, MongoDB, or PostgreSQL. The interface requires only `getHistory()` and `addMessage()` methods, making custom adapters straightforward. The MongoDB adapter pattern described in the official community resources shows how to map `SessionMessage` objects to BSON documents and query by `sessionId`, giving agents cross-restart memory with sub-millisecond read latency at typical session sizes.

## MCP Server Integration (Streamable HTTP vs stdio)

The Model Context Protocol (MCP) lets agents connect to external tool servers over a standardized interface, decoupling tool implementation from agent code. The TypeScript SDK supports both MCP transport types: stdio (spawning a local process) and Streamable HTTP (connecting to a remote endpoint over HTTP with Server-Sent Events).

```typescript
import { Agent, run } from "@openai/agents";
import { MCPServerStdio, MCPServerStreamableHttp } from "@openai/agents/mcp";

// stdio: spawn a local MCP process
const localMcp = new MCPServerStdio({
  name: "filesystem-server",
  command: "npx",
  args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
});

// Streamable HTTP: connect to a remote MCP endpoint
const remoteMcp = new MCPServerStreamableHttp({
  name: "github-server",
  url: "https://mcp.example.com/github",
  headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` },
});

const agent = new Agent({
  name: "DevAssistant",
  instructions: "Help with code and file operations.",
  mcpServers: [localMcp, remoteMcp],
});

await localMcp.connect();
await remoteMcp.connect();

const result = await run(agent, "List the files in /tmp");
console.log(result.finalOutput);

await localMcp.close();
await remoteMcp.close();
```

### Choosing Between stdio and Streamable HTTP

Use **stdio** for local development tools, CLI-based MCP servers, or when you need to spawn sandboxed subprocesses with controlled file-system access. Use **Streamable HTTP** for shared remote MCP servers, multi-tenant deployments, or when tool implementations live in a separate microservice that multiple agents should share. Streamable HTTP servers support authentication headers, connection pooling via a single persistent HTTP client, and horizontal scaling — none of which are possible with process-based stdio servers. In production, prefer HTTP unless the tool must run co-located with the agent process for latency or security reasons.

## Voice Agents with RealtimeAgent and RealtimeSession

The `RealtimeAgent` and `RealtimeSession` classes are the TypeScript SDK's standout differentiator — a first-class integration with OpenAI's speech-to-speech WebRTC pipeline that enables sub-200ms voice agents without client-side audio preprocessing. The SDK was officially announced alongside these voice features in mid-2025, making TypeScript the primary language for real-time voice agent development on the OpenAI platform.

```typescript
import { RealtimeAgent, RealtimeSession } from "@openai/agents/realtime";

const voiceAgent = new RealtimeAgent({
  name: "VoiceAssistant",
  voice: "alloy",
  instructions: "You are a friendly phone assistant. Keep answers brief.",
  tools: [weatherTool], // Reuse function tools from the standard SDK
});

const session = new RealtimeSession(voiceAgent, {
  model: "gpt-4o-realtime-preview",
});

// Connect to OpenAI's realtime WebRTC endpoint
await session.connect({ apiKey: process.env.OPENAI_API_KEY });

// In a browser context, connect a MediaStream
const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
session.connectMicrophone(mediaStream);

// Listen for agent audio output
session.on("audio", (audioBuffer) => {
  // Play audioBuffer through the browser's AudioContext
  playAudio(audioBuffer);
});

session.on("transcript", (text) => {
  console.log("Agent said:", text);
});
```

### RealtimeAgent vs Standard Agent for Voice Applications

`RealtimeAgent` uses a persistent WebSocket connection and processes audio natively without the speech-to-text → LLM → text-to-speech pipeline latency of standard agents. This reduces end-to-end voice latency from 1–3 seconds to under 300ms in well-connected environments — the difference between a natural conversation and an awkward pause. Standard agents can still be used for voice workflows with a preprocessing step (Whisper for STT, TTS API for output), but `RealtimeAgent` is the right choice for interactive voice response (IVR) systems, voice assistants, and any application where conversational cadence matters.

## Tracing, Debugging, and Observability

The SDK ships built-in tracing that records every model inference, tool call, and handoff in a structured trace tree. In development, set `OPENAI_TRACE=1` to print traces to the console. In production, configure a `TraceProcessor` to forward traces to OpenAI's Traces dashboard, Langfuse, Datadog, or any OpenTelemetry-compatible backend.

```typescript
import { Agent, run, setDefaultTraceProcessor } from "@openai/agents";
import { OpenAITraceProcessor } from "@openai/agents/tracing";

// Send traces to OpenAI's hosted trace viewer
setDefaultTraceProcessor(new OpenAITraceProcessor({ apiKey: process.env.OPENAI_API_KEY }));

const agent = new Agent({
  name: "TracedAgent",
  instructions: "Answer questions and use tools as needed.",
  tools: [weatherTool],
});

const result = await run(agent, "What's the weather in London?", {
  traceMetadata: { userId: "user-123", sessionId: "sess-abc" },
});
```

The trace includes `span_id`, `parent_span_id`, `start_time`, `end_time`, `latency_ms`, `input_tokens`, and `output_tokens` for each step, enabling per-agent cost attribution and latency profiling across complex multi-agent pipelines. The `traceMetadata` object is passed through to all child spans, making it straightforward to filter traces by user or session in the OpenAI dashboard.

### Custom Trace Processors

Implement the `TraceProcessor` interface to forward traces to your observability stack without relying on the OpenAI-hosted dashboard. The interface requires a single `processTrace(trace: Trace)` method, making it easy to write adapters for Grafana Tempo, Honeycomb, or a custom Postgres table. Running multiple processors simultaneously is supported — call `addTraceProcessor()` for each backend you want to receive events.

## TypeScript SDK vs Python SDK — Feature Gap in 2026

The TypeScript and Python SDKs share the same core primitives — Agents, Tools, Handoffs, Guardrails — but as of May 2026, several advanced features remain Python-only. Understanding the gap helps you decide which SDK to use and plan your migration timeline.

| Feature | TypeScript SDK | Python SDK |
|---|---|---|
| Agents, Tools, Handoffs | ✅ | ✅ |
| Guardrails | ✅ | ✅ |
| Sessions / Persistent Memory | ✅ | ✅ |
| MCP Integration | ✅ | ✅ |
| RealtimeAgent (voice) | ✅ | ❌ (limited) |
| Code Sandbox | ❌ | ✅ |
| Agent Harness / Eval | ❌ | ✅ |
| Code Mode (code interpreter) | ❌ | ✅ |
| Subagents (nested agents) | ❌ | ✅ |
| Streaming tool results | ✅ | ✅ |

The missing features — sandbox, harness, code mode, and subagents — are Python-only as of May 2026, with TypeScript support planned but no specific timeline announced. These gaps are intentional, not neglect: the TypeScript SDK prioritizes the runtime environments where TypeScript actually runs (browsers, edge workers, Next.js) over Python's data-science toolchain. If you need code interpreter execution or automated agent evaluation harnesses, the Python SDK is the correct choice for those workflows. For everything else — Next.js apps, voice agents, MCP-connected tools — TypeScript is ready for production.

## OpenAI Agents SDK vs Alternatives in 2026

Choosing the right TypeScript agent framework in 2026 means weighing simplicity, ecosystem fit, and feature completeness. The four realistic options for TypeScript developers are `@openai/agents`, Mastra, Vercel AI SDK, and LangGraph (TypeScript port).

| Framework | Stars | Weekly Downloads | Best For | Weakness |
|---|---|---|---|---|
| `@openai/agents` | 2,100 | 128K | OpenAI-native, voice agents | Python SDK feature gap |
| Mastra | 21,100 | 300K | All-in-one TS agent platform | Larger dependency surface |
| Vercel AI SDK | ~28K | 1.5M+ | Next.js / edge streaming | Limited multi-agent primitives |
| LangGraph (TS) | ~9K | ~80K | Complex stateful workflows | Verbose, steeper learning curve |

**Choose `@openai/agents`** when you are building on OpenAI models, need voice agent support via RealtimeAgent, or want the minimal-abstraction approach where OpenAI's own team controls the roadmap. The SDK's 1.5 million monthly downloads signal production readiness and community momentum.

**Choose Mastra** when you want an all-in-one TypeScript-first framework with built-in vector storage, workflow graphs, evaluation tooling, and OpenAI/Anthropic/Gemini model support. Mastra raised $13M and reached 21,100 GitHub stars, making it the dark horse that covers more use cases than `@openai/agents` at the cost of a larger dependency tree.

**Choose Vercel AI SDK** when your agents live in Next.js API routes or edge functions that need streaming responses, React Server Components integration, and the `useChat` hook on the frontend. The Vercel AI SDK is not a full agent framework but a streaming UI toolkit that integrates cleanly with `@openai/agents` on the backend.

**Choose LangGraph (TypeScript)** when your workflow requires complex state machines with checkpointing, branching, and time-travel debugging — patterns borrowed from LangChain's Python ecosystem. Expect more configuration than `@openai/agents` but finer control over state transitions.

## Production Deployment Best Practices

Deploying TypeScript agents to production requires attention to connection management, secret handling, error boundaries, and cost controls that development setups paper over. These patterns apply whether you deploy to AWS Lambda, Cloud Run, Fly.io, or a container on a VPS.

**Connection management:** MCP servers opened with `new MCPServerStdio()` or `new MCPServerStreamableHttp()` hold persistent connections. In serverless functions, open connections in the module initializer (cold start) and reuse them across invocations. Do not open a new MCP connection per request — the overhead from process spawning (stdio) or TCP handshake (HTTP) adds 50–500ms per call.

**Secret handling:** Never hardcode `OPENAI_API_KEY` in source code. Use environment variables injected at deployment time, AWS Secrets Manager, or GCP Secret Manager. For multi-tenant applications where each user has their own API key, pass the `OpenAI` client instance to `run()` explicitly rather than relying on the global environment variable.

**Error boundaries:** Wrap `run()` calls in try/catch and handle three distinct error types: `GuardrailTripwireTriggered` (safe to surface to users), `MaxTurnsReached` (indicates a runaway tool loop — log and alert), and `OpenAIAPIError` (network/quota issues — retry with exponential backoff). Letting all three bubble up as generic 500 errors loses valuable observability signal.

**Cost controls:** Set `maxTurns` on every production `run()` call to cap the number of model-tool round trips. A value of `10–20` is appropriate for most workflows; complex research agents may need `50+`. Log `result.usage` per request to aggregate per-user token consumption and trigger rate limiting before costs escalate.

**Graceful shutdown:** In long-running Node.js servers, register `SIGTERM` handlers that close MCP connections and flush pending trace batches before the process exits. Abrupt termination leaves MCP stdio processes orphaned and drops buffered trace data, making post-incident debugging harder.

## FAQ

The questions below address the most common points of confusion when adopting the OpenAI Agents SDK TypeScript in 2026. They cover production readiness, model compatibility, memory persistence, and orchestration limits based on the SDK's current public API and community-reported patterns. If you are evaluating whether `@openai/agents` fits your project, these answers should resolve the most frequent blockers before you write your first line of code. The SDK reached 1.5 million monthly downloads as of March 2026 — the adoption signal that the answers here reflect hard-won production experience, not just documentation-reading. The package is published weekly, breaking changes follow semantic versioning, and the OpenAI engineering team actively responds to GitHub issues in the `openai-agents-js` repository. For framework-level bugs that affect production behavior, the median time from issue filing to patch release has been under 72 hours in 2026.

### Is the OpenAI Agents SDK TypeScript production-ready in 2026?

Yes. The `@openai/agents` package reached 1.5 million downloads in a 30-day window as of March 2026, and the SDK is actively maintained by OpenAI's engineering team. Core primitives (Agents, Tools, Handoffs, Guardrails, Sessions, MCP) are stable. Some advanced features like code sandbox and subagents remain Python-only, but the TypeScript SDK covers the majority of production use cases including multi-agent pipelines and voice applications.

### How does `@openai/agents` differ from the OpenAI Python SDK's agent features?

The `@openai/agents` npm package is a dedicated agent framework, while the Python SDK embeds agent primitives as part of the main `openai` library. The TypeScript SDK uniquely ships RealtimeAgent for voice, while the Python version leads on code interpreter, sandbox, harness, and nested subagent features. Both share the same core primitives and are maintained by OpenAI, but they diverge on platform-specific capabilities.

### Can I use `@openai/agents` with models other than OpenAI's?

Yes, with caveats. The SDK wraps the `openai` client, so any OpenAI-compatible API endpoint works — including Azure OpenAI, Groq, Together AI, and local Ollama instances that expose the `/v1/chat/completions` endpoint. Pass a custom `OpenAI` client with `baseURL` set to your provider. Function calling behavior varies by model; not all providers implement tool call parsing identically.

### How do I persist agent memory across server restarts?

Implement the `Session` interface from `@openai/agents/sessions` with a durable backend. The interface requires `getHistory(sessionId: string)` returning `SessionMessage[]` and `addMessage(sessionId: string, message: SessionMessage)` returning `void`. Plug in Redis, DynamoDB, MongoDB, or any database your stack already uses. The built-in `MemorySession` is in-process only and resets on restart.

### What is the maximum number of agents I can orchestrate with handoffs?

There is no hard limit in the SDK, but practical limits emerge from the `maxTurns` cap you set on `run()`. Each handoff consumes one turn, and tool calls within the receiving agent consume additional turns. A pipeline with 5 specialized agents, each requiring 2–3 tool calls, needs `maxTurns` of at least 20. The SDK validates that handoff targets exist at initialization time, catching circular handoff graphs before runtime.
