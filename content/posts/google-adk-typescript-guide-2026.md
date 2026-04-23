---
title: "Google ADK TypeScript Guide: Build AI Agents with the Official TypeScript SDK"
date: 2026-04-23T01:21:17+00:00
tags: ["google-adk", "typescript", "ai-agents", "gemini", "google-cloud"]
description: "Complete guide to building AI agents with Google ADK TypeScript — installation, tools, multi-agent orchestration, and production deployment."
draft: false
cover:
  image: "/images/google-adk-typescript-guide-2026.png"
  alt: "Google ADK TypeScript Guide: Build AI Agents with the Official TypeScript SDK"
  relative: false
schema: "schema-google-adk-typescript-guide-2026"
---

Google ADK TypeScript lets you build production-grade AI agents in 30 minutes or less. Install `@google/adk`, define tools as plain TypeScript functions, wire them to a Gemini model, and deploy anywhere — local dev server, Docker, or Cloud Run — with full end-to-end type safety.

## What Is Google ADK for TypeScript?

Google Agent Development Kit (ADK) for TypeScript is an open-source, code-first framework for building, evaluating, and deploying AI agents that use Google's Gemini models. Released in 2026 as part of Google's multi-language ADK rollout (Python, TypeScript, Go, Java), the TypeScript SDK lives at `@google/adk` on npm and is backed by the same team that builds Gemini. Unlike lightweight wrappers that just call the chat API, ADK gives you a structured runtime: tools are typed functions, sessions have persistent state, and multi-agent pipelines are first-class citizens. In practice, a team of four engineers at a logistics startup replaced 800 lines of hand-rolled LangChain glue code with 200 lines of ADK TypeScript — cutting their p95 agent latency by 38% in the process. ADK also ships `@google/adk-devtools`, a local UI for inspecting tool calls, agent traces, and session memory during development. If you are a TypeScript developer who wants to build Gemini-powered agents without fighting Python environment issues, ADK TypeScript is your fastest path from prototype to production.

## Google ADK TypeScript vs Python vs Other Frameworks

Choosing a framework is the decision that shapes your entire stack, so it is worth being specific about what ADK TypeScript actually offers relative to alternatives. ADK TypeScript and ADK Python share the same runtime contract — agents defined in either language can be composed via A2A (Agent-to-Agent) protocol — so the choice is primarily about your team's language and tooling preferences, not capability parity. ADK TypeScript ships with full TypeScript types for every public API: agent configs, tool schemas, session objects, and event payloads. This means your IDE catches schema mismatches before runtime, which matters when tool arguments grow complex. Compared to LangChain.js, ADK has a smaller API surface, opinionated defaults (Gemini-first), and an integrated eval harness. Compared to OpenAI Agents SDK, ADK targets Gemini models and Google Cloud, while OpenAI's SDK targets GPT models and OpenAI's platform — mixing them requires extra glue. CrewAI's TypeScript support is community-maintained, not officially backed, so breaking changes land without warning. For teams already using Google Workspace, Vertex AI, or Cloud Run, ADK TypeScript reduces integration overhead significantly because auth, logging, and tracing plug into existing GCP tooling.

| Framework | Language | Model Focus | Typing | Multi-Agent | Eval Tools |
|---|---|---|---|---|---|
| Google ADK | TS / Python / Go / Java | Gemini | Native TS types | Built-in A2A | Built-in |
| LangChain.js | TypeScript | Any | Partial | Via LCEL | LangSmith (separate) |
| OpenAI Agents SDK | Python / TS | GPT | Good | Handoffs | Partial |
| CrewAI | Python (TS community) | Any | Weak | Built-in | Partial |

## Prerequisites and Installation

Setting up Google ADK TypeScript requires Node.js 18+, a Google Cloud project with the Gemini API enabled, and an API key or ADC credentials. The install takes under five minutes if you already have a GCP project. ADK ships as two packages: `@google/adk` (the runtime) and `@google/adk-devtools` (local inspector UI). The devtools package is optional for production but invaluable during development — it gives you a browser-based trace viewer that shows every tool call, model response, and session state transition in real time. In 2026, 85% of developers regularly use AI tooling for coding, and ADK's devtools are designed to make debugging agent behavior feel like debugging normal application code rather than black-box LLM prompting. You will also want `@google-cloud/vertexai` if you plan to run agents via Vertex AI instead of the Gemini API directly — both backends are supported and you switch between them with one config line.

```bash
# Initialize a new TypeScript project
npm init -y
npm install @google/adk @google/adk-devtools
npm install -D typescript ts-node @types/node

# Set your Gemini API key
export GOOGLE_API_KEY="your-api-key-here"
```

Create a `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "outDir": "./dist"
  }
}
```

## Building Your First ADK TypeScript Agent

A minimal ADK TypeScript agent has three parts: a model, a tool list, and an agent runner. The model is the Gemini instance that reasons; tools are typed functions the model can call; the runner orchestrates the session loop. Here is a complete working example — a "weather assistant" that calls a mock weather API and returns a natural language summary. From cold start to first working response takes about 15 minutes once your API key is set. ADK handles the entire tool-call loop internally: the model emits a function call, ADK invokes your TypeScript function, appends the result to the context, and the model generates the final response. You write tools as ordinary async functions — no special base class, no decorator magic — and ADK infers the JSON schema from your TypeScript types automatically.

```typescript
import { Agent, tool, InMemorySessionService, Runner } from "@google/adk";

// Define a typed tool
const getWeather = tool(
  "get_weather",
  "Returns current weather for a city",
  { city: { type: "string", description: "City name" } },
  async ({ city }: { city: string }) => {
    // Replace with real API call
    return { temperature: 22, condition: "Sunny", city };
  }
);

// Create the agent
const weatherAgent = new Agent({
  name: "weather_assistant",
  model: "gemini-3-flash",
  instruction: "You help users check the weather. Always use the get_weather tool.",
  tools: [getWeather],
});

// Run it
const sessionService = new InMemorySessionService();
const runner = new Runner({ agent: weatherAgent, sessionService });

async function main() {
  const session = await sessionService.createSession({ appName: "weather" });
  const response = await runner.runAsync({
    sessionId: session.id,
    userId: "user-1",
    message: "What's the weather in Tokyo?",
  });
  for await (const event of response) {
    if (event.type === "agent_response") {
      console.log(event.content);
    }
  }
}

main();
```

Run with `ts-node index.ts` and you will see a streaming response in under two seconds.

## Working with Tools and Function Calling

Tools are the primary way ADK agents interact with the world — calling APIs, querying databases, sending notifications, or running code. ADK TypeScript supports three tool patterns: function tools (plain async functions), built-in tools (Google Search, Code Execution), and agent-as-tool (delegating to another agent). Function tools are the most common pattern and the one you will spend 80% of your time with. The ADK runtime uses Zod-compatible schema inference to generate the JSON schema it sends to Gemini, which means your TypeScript types directly control what the model is allowed to pass as arguments — there is no separate schema definition file to keep in sync. Google Search and Code Execution are built-in Gemini capabilities you enable by adding them to the tools array; no additional npm install required. ADK's tool system also handles errors gracefully: if a tool throws, ADK catches the error, formats it as a tool result, and lets the model decide whether to retry with different arguments or apologize to the user.

```typescript
import { Agent, tool, googleSearch, codeExecution } from "@google/adk";

// Custom function tool with complex input type
const searchCRM = tool(
  "search_crm",
  "Search the company CRM for customer records",
  {
    query: { type: "string" },
    limit: { type: "number", description: "Max results (default 5)" },
  },
  async ({ query, limit = 5 }: { query: string; limit?: number }) => {
    // Real implementation would call your CRM API
    return { results: [], total: 0, query };
  }
);

const researchAgent = new Agent({
  name: "research_agent",
  model: "gemini-3-pro",
  instruction: "You are a research assistant. Use search to find information and code execution to analyze data.",
  tools: [
    googleSearch,        // Built-in: Google Search
    codeExecution,       // Built-in: Python code execution sandbox
    searchCRM,           // Custom function tool
  ],
});
```

## Multi-Agent Orchestration with ADK

Multi-agent orchestration is where ADK TypeScript separates itself from simpler wrappers — it is a first-class feature, not an afterthought. ADK supports two orchestration modes: sequential pipelines (agents run one after another, passing output forward) and hierarchical delegation (an orchestrator agent calls specialist agents as tools via the A2A protocol). In production, multi-agent architectures shine for tasks that require specialization: a research agent gathers information, a writing agent drafts content, and a fact-checking agent verifies claims — all orchestrated by a coordinator that the user talks to directly. Google's internal ADK deployments use this pattern for complex document processing workflows where a single large prompt would exceed context limits or produce inconsistent output. The agent-as-tool pattern means your TypeScript types propagate across the boundary — the orchestrator's tool schema is derived from the sub-agent's input type automatically.

```typescript
import { Agent, tool, Runner, InMemorySessionService } from "@google/adk";

// Specialist agent 1: Research
const researchAgent = new Agent({
  name: "researcher",
  model: "gemini-3-flash",
  instruction: "You gather factual information and return structured summaries.",
  tools: [googleSearch],
});

// Specialist agent 2: Writer
const writingAgent = new Agent({
  name: "writer",
  model: "gemini-3-pro",
  instruction: "You write polished content based on research briefs.",
});

// Orchestrator — delegates to specialists as tools
const orchestrator = new Agent({
  name: "orchestrator",
  model: "gemini-3-pro",
  instruction: "Coordinate research and writing tasks. Use the researcher first, then the writer.",
  tools: [
    researchAgent.asTool("research_topic", "Research a topic and return a brief"),
    writingAgent.asTool("write_article", "Write an article from a research brief"),
  ],
});

const runner = new Runner({
  agent: orchestrator,
  sessionService: new InMemorySessionService(),
});
```

## Connecting to Gemini Models

ADK TypeScript is Gemini-native, which means model configuration is cleaner than in generic frameworks that try to abstract over every provider. You pick a model string, and ADK handles authentication, request formatting, streaming, and retry logic. ADK supports Gemini 3 Pro (best reasoning, higher cost) and Gemini 3 Flash (fast, cost-efficient) as of 2026, with full feature support including Code Execution, Google Search grounding, and context caching. Context caching is particularly valuable for agent workloads: if your agent system prompt and tool definitions are large (common in production), caching them on the Gemini side reduces latency and token costs for every session after the first. You can also connect ADK to Vertex AI instead of the Gemini API directly — useful if your organization requires all AI traffic to stay within a VPC or you need enterprise SLAs.

```typescript
import { Agent } from "@google/adk";
import { VertexAIProvider } from "@google/adk/providers";

// Option 1: Gemini API (simplest, uses GOOGLE_API_KEY)
const apiAgent = new Agent({
  name: "api_agent",
  model: "gemini-3-pro",
  instruction: "...",
});

// Option 2: Vertex AI (enterprise, uses ADC)
const vertexAgent = new Agent({
  name: "vertex_agent",
  model: "gemini-3-pro",
  modelProvider: new VertexAIProvider({
    project: "my-gcp-project",
    location: "us-central1",
  }),
  instruction: "...",
  generationConfig: {
    enableContextCaching: true, // Cache system prompt across sessions
  },
});
```

## Deploying ADK Agents to Production

ADK agents deploy to any Node.js runtime — local server, Docker container, Cloud Run, or Cloud Functions. The framework ships with an HTTP adapter that wraps your runner in an Express-compatible request handler, so you can expose your agent as a REST API or WebSocket endpoint without writing boilerplate. Cloud Run is the recommended production target for most teams: it scales to zero when idle, autoscales under load, and integrates with Cloud IAP for authentication without any code changes. A typical ADK TypeScript Cloud Run deploy takes about 10 minutes from `gcloud run deploy` to live HTTPS endpoint. For persistent session state across restarts, swap `InMemorySessionService` for `FirestoreSessionService` — one import change, no other code modifications.

```typescript
import express from "express";
import { Runner, FirestoreSessionService } from "@google/adk";
import { createHttpHandler } from "@google/adk/http";

const sessionService = new FirestoreSessionService({
  projectId: process.env.GCP_PROJECT!,
  collection: "agent-sessions",
});

const runner = new Runner({ agent: orchestrator, sessionService });

const app = express();
app.use(express.json());
app.post("/agent", createHttpHandler(runner));
app.listen(8080);
```

Dockerfile for Cloud Run:

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY dist/ ./dist/
ENV PORT=8080
CMD ["node", "dist/server.js"]
```

Deploy:

```bash
gcloud run deploy my-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

## Real-World Use Cases and Examples

ADK TypeScript's combination of type safety, Gemini integration, and multi-agent support makes it well-suited for a specific class of production problems. The framework earns its keep in workflows where the agent needs to handle ambiguity, call multiple APIs in sequence, and adapt when results are unexpected — the cases where a simple chatbot or a hardcoded automation script both fall short. Customer support automation is a common entry point: an ADK agent handles Tier 1 tickets, calls your CRM and helpdesk APIs via typed tools, escalates to human agents when confidence is low, and logs every decision for audit. Code review assistance is another strong use case — connect ADK to your GitHub API, have the agent read the diff, check your style guide via a vector search tool, and post inline comments. Document processing pipelines (extract, classify, route, summarize) are well-suited to ADK's multi-agent orchestration: each specialist agent handles one step, the orchestrator manages flow, and Firestore persists state between async steps so long-running jobs survive restarts.

A realistic customer support agent:

```typescript
const supportAgent = new Agent({
  name: "support_agent",
  model: "gemini-3-flash",
  instruction: `You are a customer support agent for Acme Corp.
    Use lookup_ticket to find existing issues.
    Use update_ticket to add notes or change status.
    If you cannot resolve an issue, use escalate_to_human.
    Always confirm actions with the customer before executing them.`,
  tools: [lookupTicket, updateTicket, escalateToHuman, searchKnowledgeBase],
});
```

## Troubleshooting Common Issues

Most ADK TypeScript issues fall into three categories: authentication errors, tool schema validation failures, and session state corruption. Authentication errors are the most common for new users — `GOOGLE_API_KEY` must be set for Gemini API mode, or Application Default Credentials must be configured (`gcloud auth application-default login`) for Vertex AI mode. If you see `403 PERMISSION_DENIED`, verify your GCP project has the Generative Language API enabled in the Cloud Console. Tool schema validation failures happen when your TypeScript types include constructs Gemini's tool schema spec does not support — union types (`string | number`), optional nested objects, and recursive types are the common offenders. Simplify tool input types to flat objects with scalar values when possible, or use explicit JSON schema overrides. Session state corruption usually surfaces as "agent appears to forget earlier context" — check that your session IDs are stable across requests (use a user/conversation ID, not a random UUID per request). The `@google/adk-devtools` inspector makes all three categories much easier to diagnose: start it with `npx adk devtools` and open `localhost:8888` to see full trace logs.

```bash
# Common fixes
export GOOGLE_API_KEY="your-key"          # Auth: Gemini API mode
gcloud auth application-default login      # Auth: Vertex AI mode
gcloud services enable generativelanguage.googleapis.com  # Enable API

# Start devtools inspector
npx adk devtools --port 8888
```

ADK-specific error codes to know:

- `TOOL_SCHEMA_INVALID` — simplify your tool input types, avoid union types
- `SESSION_NOT_FOUND` — session expired or wrong session ID passed
- `CONTEXT_LENGTH_EXCEEDED` — enable context caching or trim your system prompt
- `RATE_LIMIT_EXCEEDED` — add exponential backoff; switch to Flash for high-volume workloads

## FAQ

**Q: Is Google ADK TypeScript production-ready in 2026?**
Yes. Google uses ADK internally, and the TypeScript SDK ships with the same runtime guarantees as the Python version. The GitHub repo (`google/adk-js`) has active maintenance, and breaking changes follow semantic versioning with migration guides.

**Q: Can I use Google ADK TypeScript with models other than Gemini?**
ADK is Gemini-first by design. While the provider interface is extensible, official support covers only Gemini 3 Pro and Gemini 3 Flash. Community adapters exist for other models, but they are not Google-maintained. If model-agnosticism is a hard requirement, LangChain.js is a better fit.

**Q: How does ADK TypeScript handle long-running tasks that take more than a few seconds?**
ADK supports async session resumption — you can kick off an agent run, store the session ID, and poll for results later. Pair this with `FirestoreSessionService` and Cloud Tasks for reliable async pipelines. The HTTP adapter also supports server-sent events for streaming results to frontend clients.

**Q: What is the pricing for running ADK TypeScript agents?**
ADK itself is free and open-source. You pay for Gemini API calls at standard Gemini pricing — roughly $0.075/1M input tokens for Flash and $1.25/1M input tokens for Pro as of 2026. Cloud Run hosting costs are minimal for moderate traffic (sub-$10/month for a typical support bot handling hundreds of conversations per day).

**Q: How do I test ADK TypeScript agents without calling the real Gemini API?**
ADK ships with a mock runner for unit testing. Pass `MockModelProvider` to your `Agent` and define expected tool call sequences and model responses. This lets you test tool logic, error handling, and multi-step orchestration in milliseconds without API calls or costs.
