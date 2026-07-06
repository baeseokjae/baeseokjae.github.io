---
cover:
  alt: 'Mastra AI Guide 2026: Build TypeScript AI Agents with the Framework That Hit
    300K Weekly Downloads'
  image: /images/mastra-ai-guide-2026.png
  relative: false
date: 2026-04-21 23:21:28+00:00
description: 'Complete guide to Mastra AI TypeScript framework: install, build agents,
  add memory, create workflows, and deploy to production.'
draft: false
schema: schema-mastra-ai-guide-2026
tags:
- mastra
- typescript
- ai-agents
- ai-framework
- llm
title: 'Mastra AI Guide 2026: Build TypeScript AI Agents with the Framework That Hit
  300K Weekly Downloads'
---

Mastra is an open-source TypeScript framework for building production AI agents, giving you agents, tools, memory, workflows, RAG, evals, and observability in a single cohesive package. Install it with `npm create mastra@latest`, define an agent in under 20 lines of TypeScript, and have a working REST API in minutes — no Python environment, no multi-library stitching.

## Why Mastra Is the TypeScript AI Framework to Watch in 2026

Mastra is the TypeScript-first AI agent framework built by the team behind Gatsby — the same engineers who made static-site generation mainstream for JavaScript developers. With 23.2k GitHub stars, $35M in total funding (including a $22M Series A led by Spark Capital announced in April 2026), and enterprise deployments at Brex, Docker, Elastic, MongoDB, Salesforce, Replit, and SoftBank, Mastra has moved from interesting experiment to production infrastructure. The Marsh McLennan enterprise search agent built on Mastra is used by 100,000+ employees every day. Brex's Mastra-powered agents contributed directly to their $5.1B Capital One acquisition. These aren't toy demos — they are mission-critical workloads. For JavaScript and TypeScript developers who've been watching the Python AI ecosystem from the sidelines, Mastra is the on-ramp. The CEO Sam Bhagwat has cited data that 60–70% of YC X25 agent startups are building in TypeScript, signaling a clear ecosystem shift.

### The Shift From Python to TypeScript for AI Agents

For years, AI frameworks defaulted to Python: LangChain, LangGraph, CrewAI, and AutoGen all began Python-first. The assumption was that data scientists and ML researchers drove adoption. But in 2025–2026, the builders shipping production agents are full-stack web developers — and they live in TypeScript. Mastra is built for that reality. Its API design mirrors familiar Node.js patterns, its type safety catches agent configuration errors at compile time, and its integration with Next.js, Express, Hono, and SvelteKit means your AI layer fits naturally into existing web apps without a Python sidecar service.

### What Is Mastra? (Origin Story: Built by the Gatsby Team)

Mastra was created by Sam Bhagwat and the former Gatsby core team, who applied their experience building developer-facing infrastructure to the AI agent problem. They spent time at Netlify scaling a platform that served millions of developers, then looked at the emerging AI agent landscape and saw the same fragmentation that existed in static site generation before Gatsby unified it. The result is a framework that prioritizes developer experience, strong TypeScript types, and a batteries-included philosophy — you get memory, workflow orchestration, RAG, observability, and a local dev UI (Mastra Studio) out of the box, not as separate packages you wire together yourself.

---

## Getting Started: Setting Up Your First Mastra Project

Setting up Mastra takes under five minutes on any machine with Node.js 18+ installed. The framework ships a scaffold CLI (`npm create mastra@latest`) that generates a complete project with sensible defaults, including TypeScript configuration, a starter agent, and Mastra Studio for local development. The project structure is opinionated but not restrictive — you can drop Mastra into an existing Next.js or Express app, or start fresh with the scaffold. The free tier of Mastra Platform gives you Studio and the server runtime at no cost, making it practical to experiment before committing to infrastructure spend. Apache 2.0 licensing means you can use it commercially without restriction, unlike some frameworks with commercial-use clauses. Mastra requires Node.js 18 or later and works with npm, pnpm, or yarn. The scaffold wizard takes roughly 60 seconds: it asks for your LLM provider, writes `.env` key stubs, and generates a working weather agent you can query immediately. By the time the install finishes, you have a typed, tested, locally runnable AI agent.

### Prerequisites and Installation

```bash
# Requires Node.js 18+
npm create mastra@latest

# Or add to an existing project
npm install @mastra/core
```

The scaffold wizard asks for your preferred LLM provider (OpenAI, Anthropic, Google Gemini, Mistral, or Groq), sets up `.env` with the right API key variable names, and generates a working agent you can test immediately.

### Project Structure Overview

```
my-mastra-app/
├── src/
│   ├── mastra/
│   │   ├── agents/        # Agent definitions
│   │   ├── tools/         # Custom tool functions
│   │   ├── workflows/     # Multi-step workflows
│   │   └── index.ts       # Mastra instance
│   └── index.ts           # App entry point
├── .env
└── package.json
```

The `Mastra` instance in `index.ts` is your registry — you import agents, tools, and workflows and pass them to the constructor. This central registry pattern means Mastra knows about all your components for observability and Studio integration.

### Mastra Studio: The Interactive Dev UI

Run `npx mastra dev` and Mastra Studio opens at `http://localhost:4111`. Studio gives you a chat interface to test agents, a visual workflow runner, memory inspection, trace viewer, and eval results — all without writing test code. This dramatically shortens the feedback loop during development. You can send messages to agents, inspect the exact tool calls they made, see token counts per step, and replay failed runs from any point in the trace.

---

## Building Your First AI Agent with Mastra

An AI agent in Mastra is defined using the `Agent` class from `@mastra/core`. You provide a name, system instructions, an LLM model reference, and optionally a set of tools and a memory configuration. In fewer than 30 lines of TypeScript you have an agent that can call external APIs, remember conversation history, and respond with context awareness. Mastra's type system ensures your tool input/output schemas are validated at compile time, catching the class of bugs that show up as cryptic runtime errors in weakly-typed frameworks. The agent automatically handles prompt construction, tool call parsing, and multi-turn conversation state — you focus on the business logic. Mastra agents are model-agnostic by design: swap from GPT-4o to Claude Sonnet to Gemini Flash by changing one import, with no changes to tool definitions, memory setup, or downstream code. This is especially valuable for production systems where you may want to switch providers for cost, latency, or capability reasons without a costly refactor. Each agent instance is also independently observable — all calls are traced through OpenTelemetry automatically.

### Defining an Agent with System Prompts and Tools

```typescript
import { Agent } from "@mastra/core/agent";
import { openai } from "@ai-sdk/openai";
import { weatherTool } from "../tools/weather";

export const weatherAgent = new Agent({
  name: "Weather Agent",
  instructions: `You are a helpful weather assistant. When asked about weather,
    always use the weather tool to get current conditions. Be concise and specific.`,
  model: openai("gpt-4o"),
  tools: { weatherTool },
});
```

### Adding Memory: Working Memory and Semantic Recall

```typescript
import { Memory } from "@mastra/memory";
import { LibSQLStore } from "@mastra/memory/storage/libsql";

const memory = new Memory({
  storage: new LibSQLStore({ url: process.env.DATABASE_URL! }),
  options: {
    workingMemory: { enabled: true },
    semanticRecall: {
      topK: 5,
      messageRange: { before: 2, after: 2 },
    },
  },
});

export const weatherAgent = new Agent({
  name: "Weather Agent",
  instructions: "...",
  model: openai("gpt-4o"),
  tools: { weatherTool },
  memory,
});
```

Mastra supports two memory modes. **Working memory** stores structured facts about the user or session that persist across conversations — think name, preferences, previous requests. **Semantic recall** performs vector similarity search over past messages so the agent can surface relevant prior context without loading the entire history into the context window.

### Connecting LLM Providers

Mastra uses the Vercel AI SDK under the hood for model calls, which means you can swap providers by changing one import:

```typescript
import { anthropic } from "@ai-sdk/anthropic";
import { google } from "@ai-sdk/google";
import { groq } from "@ai-sdk/groq";

// Drop-in swap — same Agent API regardless of provider
model: anthropic("claude-sonnet-4-5"),
model: google("gemini-2.0-flash"),
model: groq("llama-3.3-70b-versatile"),
```

---

## Tools and MCP: Connecting Your Agent to the Real World

Tools are the mechanism by which Mastra agents take action — calling APIs, reading databases, sending messages, or triggering webhooks. A Mastra tool is a TypeScript function with a Zod schema for inputs and outputs, a description the LLM uses to decide when to call it, and an async execute function containing the actual logic. The type safety guarantees that the LLM's JSON tool call is validated before it reaches your code, eliminating an entire class of injection and malformed-input bugs. Beyond custom tools, Mastra has first-class support for MCP (Model Context Protocol), letting your agents consume any of the thousands of existing MCP servers — GitHub, Slack, Postgres, Notion, and more — without writing glue code. Docker's engineering team used exactly this pattern to build a PR automation agent that listens to GitHub webhooks and takes action using the GitHub Official MCP server via Mastra's MCP Gateway integration.

### Defining a Custom Tool

```typescript
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

export const weatherTool = createTool({
  id: "get_weather",
  description: "Get current weather conditions for a city",
  inputSchema: z.object({
    city: z.string().describe("City name"),
    units: z.enum(["celsius", "fahrenheit"]).default("celsius"),
  }),
  outputSchema: z.object({
    temperature: z.number(),
    conditions: z.string(),
    humidity: z.number(),
  }),
  execute: async ({ context }) => {
    const { city, units } = context;
    // Call your weather API here
    const data = await fetchWeatherAPI(city, units);
    return { temperature: data.temp, conditions: data.desc, humidity: data.humidity };
  },
});
```

### MCP Integration

```typescript
import { MCPClient } from "@mastra/mcp";

const mcpClient = new MCPClient({
  servers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN! },
    },
  },
});

// Get MCP tools and pass to agent
const tools = await mcpClient.getTools();

export const githubAgent = new Agent({
  name: "GitHub Agent",
  instructions: "You manage GitHub repositories and PRs.",
  model: anthropic("claude-sonnet-4-5"),
  tools,
});
```

### Real Example: Docker's PR Automation Agent

Docker built a three-agent architecture using Mastra and the GitHub MCP server:

1. **Analyze PR agent** — reads the diff and generates a structured review
2. **Generate comment agent** — formats the review as a GitHub comment
3. **Post and close PR agent** — submits the comment and updates PR status

Each agent runs as a Mastra workflow step. The orchestration triggers on a GitHub webhook, runs all three agents in sequence, and posts the result back to GitHub — no human in the loop. This is the pattern Mastra was designed for: event-driven, not chat-driven.

---

## Workflows: Orchestrating Complex Agent Tasks

Mastra workflows let you define deterministic, multi-step processes where each step can call an agent, run a function, or trigger another workflow. Unlike a single agent trying to plan and execute everything in one context window, workflows give you explicit control over the execution graph — with support for sequential steps, parallel branches, conditional routing, and suspension points for human-in-the-loop approval. This separation of concerns is critical for production systems: agents handle the fuzzy reasoning, workflows handle the reliable orchestration. The Mastra workflow engine is built on a durable execution model, meaning in-progress workflows can be paused, inspected in Studio, and resumed — even after a server restart. Docker's PR automation pipeline (three sequential agents triggered by a GitHub webhook) is a textbook Mastra workflow: deterministic order, explicit data passing between steps, and observable state at every stage. Compared to LangGraph's graph-based model, Mastra workflows use a linear `.then()` builder API that TypeScript developers find immediately readable. For branching, a `.branch()` method accepts predicate functions rather than requiring explicit graph node connections.

### When to Use Workflows vs Agents

| Scenario | Use Agent | Use Workflow |
|---|---|---|
| Open-ended Q&A | ✓ | |
| Multi-step document processing | | ✓ |
| Sequential API calls with error recovery | | ✓ |
| Research and synthesis | ✓ | |
| Approval-gated actions | | ✓ |
| Real-time chat | ✓ | |
| ETL-style data pipelines | | ✓ |

### Building a Workflow

```typescript
import { createWorkflow, createStep } from "@mastra/core/workflows";
import { z } from "zod";

const fetchDataStep = createStep({
  id: "fetch-data",
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ content: z.string() }),
  execute: async ({ inputData }) => {
    const response = await fetch(inputData.url);
    const content = await response.text();
    return { content };
  },
});

const analyzeStep = createStep({
  id: "analyze",
  inputSchema: z.object({ content: z.string() }),
  outputSchema: z.object({ summary: z.string(), sentiment: z.string() }),
  execute: async ({ inputData, mastra }) => {
    const agent = mastra?.getAgent("analyzerAgent");
    const result = await agent?.generate(
      `Analyze this content: ${inputData.content}`
    );
    return { summary: result?.text ?? "", sentiment: "positive" };
  },
});

export const contentWorkflow = createWorkflow({
  id: "content-analysis",
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ summary: z.string(), sentiment: z.string() }),
})
  .then(fetchDataStep)
  .then(analyzeStep)
  .commit();
```

### Parallel Execution and Conditional Branching

```typescript
// Run steps in parallel
workflow.parallel([step1, step2, step3]).then(mergeStep);

// Conditional routing
workflow.branch([
  [async ({ inputData }) => inputData.type === "urgent", urgentStep],
  [async ({ inputData }) => inputData.type === "normal", normalStep],
]);
```

---

## RAG with Mastra: Giving Your Agent Knowledge

RAG (Retrieval-Augmented Generation) in Mastra is handled through the `@mastra/rag` package, which provides document chunking, embedding, vector storage, and retrieval as first-class primitives. Rather than building a separate vector pipeline with LangChain, Pinecone, and custom glue code, Mastra gives you a unified API that works with PostgreSQL (pgvector), Pinecone, Qdrant, Weaviate, Chroma, or any vector store implementing the Mastra `VectorStore` interface. Elastic's engineering blog documented building a full agentic RAG assistant using Mastra and Elasticsearch, noting that Mastra's model-agnostic design and clean TypeScript API were key advantages over Python-based alternatives. The result was a production chatbot with semantic document retrieval, citation tracking, and conversational memory — built in a few hundred lines of TypeScript. The `@mastra/rag` package ships chunking strategies (fixed-size, recursive, sentence, and markdown-aware), multiple embedding providers (OpenAI `text-embedding-3-small`, Cohere, and others), and query-time reranking. You can implement the complete ingest-and-retrieve loop in under 50 lines, with the vector store swap requiring only a single configuration change rather than a full rewrite.

### Setting Up RAG

```typescript
import { MastraVector } from "@mastra/vector-pg"; // PostgreSQL + pgvector
import { embed, chunk } from "@mastra/rag";
import { openai } from "@ai-sdk/openai";

// Chunk and embed documents
const documents = await chunk(rawText, {
  strategy: "recursive",
  size: 512,
  overlap: 50,
});

const embeddings = await embed(documents, {
  provider: openai.embedding("text-embedding-3-small"),
});

// Store in vector DB
const vectorStore = new MastraVector({ connectionString: process.env.DATABASE_URL! });
await vectorStore.upsert({ indexName: "docs", vectors: embeddings });

// Query at retrieval time
const results = await vectorStore.query({
  indexName: "docs",
  queryVector: await embed(userQuery, { provider: openai.embedding("text-embedding-3-small") }),
  topK: 5,
});
```

### Adding RAG to an Agent

The retrieved chunks are injected into the agent's context via a tool, giving the LLM access to relevant documents without blowing out the context window with entire corpora:

```typescript
export const ragTool = createTool({
  id: "search_docs",
  description: "Search internal documentation for relevant information",
  inputSchema: z.object({ query: z.string() }),
  execute: async ({ context }) => {
    const results = await vectorStore.query({ ... });
    return { documents: results.map(r => r.metadata.text) };
  },
});
```

---

## Productionizing: Evals, Observability, and Guardrails

Production AI agents fail in ways that unit tests cannot catch — hallucinations, prompt injection, unexpected tool chaining, model degradation across versions, and context window violations. Mastra addresses this with a built-in evals system, distributed tracing via OpenTelemetry, and configurable guardrails. The evals system supports both rule-based checks (response contains X, JSON schema validation, keyword presence) and model-graded evaluations using a judge LLM to score qualities like helpfulness, factuality, and tone. You define evals as code, version them with your agent definitions, and see results in Mastra Studio alongside the traces that explain why each response was generated. This closes the loop between development and production: the same evals you run locally can be scheduled against production traffic samples to catch regressions before users report them.

### Running Evals

```typescript
import { evaluate } from "@mastra/evals";
import { ToneConsistencyMetric, AnswerRelevancyMetric } from "@mastra/evals/metrics";

const result = await evaluate(weatherAgent, "What's the weather in Tokyo?", {
  metrics: [
    new ToneConsistencyMetric({ tone: "professional" }),
    new AnswerRelevancyMetric({ model: openai("gpt-4o-mini") }),
  ],
});

console.log(result.scores); // { toneConsistency: 0.92, answerRelevancy: 0.87 }
```

### Observability with OpenTelemetry

```typescript
import { Mastra } from "@mastra/core";
import { OpenTelemetry } from "@mastra/core/telemetry/otel";

const mastra = new Mastra({
  agents: { weatherAgent },
  telemetry: new OpenTelemetry({
    serviceName: "my-mastra-app",
    export: { type: "otlp", endpoint: process.env.OTEL_EXPORTER_ENDPOINT! },
  }),
});
```

Every agent call, tool invocation, and LLM request is automatically traced. You see the full span tree in Studio or any OTLP-compatible backend (Jaeger, Honeycomb, Grafana Tempo).

### Guardrails

Mastra supports input and output guardrails as middleware functions on the agent:

```typescript
export const safeAgent = new Agent({
  ...baseConfig,
  beforeGenerate: async (messages) => {
    // Reject messages containing PII patterns
    const hasPII = /\b\d{3}-\d{2}-\d{4}\b/.test(messages.at(-1)?.content ?? "");
    if (hasPII) throw new Error("PII detected in input");
    return messages;
  },
});
```

---

## Deployment: From Dev to Production

Mastra agents deploy as standard HTTP servers — no special runtime required. The `mastra build` command compiles your TypeScript agent definitions into a Node.js server exposing REST endpoints for each agent and workflow. You can deploy this anywhere: a VPS, Kubernetes pod, AWS Lambda, Vercel Edge Function, or Cloudflare Worker. The Mastra Platform (their managed offering) adds Studio, a Memory Gateway for cross-deployment memory persistence, and a server runtime with automatic scaling — useful if you don't want to manage the infrastructure yourself. The free Starter tier is sufficient for personal projects and early-stage products. A Mastra server exposes stable REST endpoints: `POST /api/agents/{agentId}/generate` for synchronous responses, `POST /api/agents/{agentId}/stream` for streaming, and `POST /api/workflows/{workflowId}/execute` for workflow runs. These endpoints are framework-agnostic — any HTTP client can call them. For teams embedding agents in existing web apps, Mastra exports a Node.js handler you wire directly into Next.js API routes, Express middleware, or Hono routes, keeping your deployment footprint minimal. The Marsh McLennan deployment (100,000+ daily users) demonstrates that Mastra's server model handles enterprise-scale traffic without custom infrastructure work.

### Mastra Server: REST API Endpoints

After running `mastra build && node dist/index.js`, your agents are available at:

```
POST /api/agents/{agentId}/generate
POST /api/agents/{agentId}/stream
POST /api/workflows/{workflowId}/execute
GET  /api/agents/{agentId}/memory/{threadId}
```

### Integrating with Existing Frameworks

```typescript
// Next.js App Router
import { mastra } from "@/mastra";
import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const { message } = await req.json();
  const agent = mastra.getAgent("weatherAgent");
  const result = await agent.generate(message);
  return Response.json({ response: result.text });
}
```

```typescript
// Express
import express from "express";
import { mastra } from "./mastra";

const app = express();
app.use(express.json());

app.post("/chat", async (req, res) => {
  const agent = mastra.getAgent("weatherAgent");
  const result = await agent.generate(req.body.message);
  res.json({ response: result.text });
});
```

### Mastra Platform Pricing

| Tier | Price | Key Features |
|---|---|---|
| Starter | Free | Studio, 1 agent, community support |
| Teams | $250/team/month | Unlimited agents, Memory Gateway, team collaboration |
| Enterprise | Custom | SLA, SSO, on-prem option, dedicated support |

---

## Mastra vs Other AI Frameworks: TypeScript-First Comparison

Mastra is not the only option for building AI agents — but it is the most complete TypeScript-first option in 2026. LangGraph, LangChain, CrewAI, and AutoGen all have larger Python ecosystems with more community content and tutorials, but none offers the same level of TypeScript integration, developer tooling, or batteries-included design. The Vercel AI SDK is the closest TypeScript competitor, but it is primarily a UI/streaming library rather than a full agent framework — no workflow engine, no built-in evals, no Mastra Studio equivalent. For teams already building in TypeScript who need production-grade agents, Mastra is the clear default in 2026. The Elastic engineering team explicitly chose Mastra over Python-based alternatives after evaluating CrewAI, AutoGen, and LangGraph, citing TypeScript's type safety and Mastra's unified stack as the deciding factors. The 60–70% of YC X25 agent startups building in TypeScript (per Sam Bhagwat's Hacker News data) confirms this is not an isolated preference but a broad ecosystem shift driven by full-stack JavaScript developers building production AI products.

### Mastra vs LangGraph vs CrewAI vs Vercel AI SDK

| Feature | Mastra | LangGraph | CrewAI | Vercel AI SDK |
|---|---|---|---|---|
| Primary language | TypeScript | Python | Python | TypeScript |
| Workflow orchestration | Built-in | Built-in | Built-in | External |
| Memory management | Built-in | External | External | External |
| RAG support | Built-in | External | External | External |
| Evals | Built-in | External | External | None |
| Local dev UI | Mastra Studio | None | None | None |
| MCP support | Native | Plugin | Plugin | Partial |
| Deployment | Server + Platform | Self-managed | Self-managed | Vercel |
| Apache 2.0 license | ✓ | ✓ | ✓ | MIT |
| Enterprise adoption | Brex, Docker, MongoDB | OpenAI, Google | Startups | Vercel ecosystem |

### When to Choose Mastra (and When Not To)

**Choose Mastra when:**
- Your team's primary language is TypeScript or JavaScript
- You need a complete stack (agents + memory + workflows + RAG + evals) without building your own
- You're deploying into an existing Node.js web application
- You want a local dev UI with traces and memory inspection out of the box

**Consider alternatives when:**
- Your team is deeply Python-native and has existing LangChain/LangGraph infrastructure
- You need advanced graph-based agent architectures with fine-grained state management (LangGraph is stronger here)
- You're building a research prototype where Python's ML library ecosystem (transformers, scipy, sklearn) is critical

---

## Real-World Examples and Case Studies

Mastra's production adoption in 2026 spans startups to Fortune 500 enterprises, with publicly documented case studies that illustrate the framework's maturity. These aren't experimental integrations — they are load-bearing systems handling millions of requests. Docker's PR automation agent, Elastic's agentic RAG assistant, and Marsh McLennan's enterprise search are all built on Mastra and running in production today. The $22M Series A funded in April 2026 and the list of investors (Spark Capital alongside participation from customers like Brex and Replit) signal institutional confidence that Mastra has achieved product-market fit in the TypeScript AI agent space. Enterprise adopters include Brex (financial services agents), Sanity (content management AI), Factorial (HR automation), Indeed (job platform), Marsh McLennan (professional services), MongoDB (database tooling), Workday (enterprise SaaS), Salesforce (CRM automation), Docker (DevOps), Replit (coding assistant), Elastic (search and analytics), SoftBank (telecom and investing), and Plaid (fintech). This breadth across verticals demonstrates that Mastra's value proposition — TypeScript-native, batteries-included, production-ready — applies across industries, not just one niche.

### Docker: Event-Driven PR Management Agent

Docker Engineering built a PR review automation system using Mastra, the GitHub Official MCP server, and Docker's MCP Gateway. The architecture: a GitHub webhook fires when a PR is opened, Mastra receives the event, a three-step workflow runs (analyze diff → generate review → post comment), and the results appear on the PR within seconds. The key insight from Docker's engineering blog: Mastra was chosen specifically for its multi-agent orchestration support and its ability to handle event-driven (not just chat-driven) workflows — a critical distinction for production automation.

### Elastic: Agentic RAG with Elasticsearch

Elastic's search labs team built a full-stack RAG assistant using Mastra on the backend and Elasticsearch as the vector store. The agent uses semantic search to retrieve relevant documentation chunks, synthesizes an answer using Claude, and cites sources inline. The team noted that Mastra's TypeScript-first design and model-agnostic architecture were decisive advantages — the same agent code works whether the underlying LLM is GPT-4o, Claude, or Gemini, enabling A/B testing across providers without architecture changes.

### Marsh McLennan: Enterprise Scale

Marsh McLennan, the global professional services firm, deployed a Mastra-powered enterprise search agent used by over 100,000 employees every day. This is among the highest-traffic public Mastra deployments and demonstrates the framework's ability to handle enterprise-scale load without degradation.

### Replit: Agent 3 Building Mastra Agents

Replit uses Mastra in Replit Agent 3, its AI coding assistant, to enable the agent to build and deploy other Mastra agents. This recursive pattern — an AI agent that scaffolds, configures, and deploys other AI agents — represents the cutting edge of agentic architecture and is made practical by Mastra's clean, programmatic API surface.

---

## FAQ

Mastra is the TypeScript-native AI agent framework that ships agents, memory, workflows, RAG, evals, and a local dev UI in a single package. Founded by the Gatsby team and backed by $35M in funding, Mastra reached 23.2k GitHub stars as of April 2026 and is in production at companies like Brex, Docker, MongoDB, and Marsh McLennan (100,000+ daily users). Below are the most common questions from developers evaluating or adopting Mastra in 2026, covering setup, provider support, Mastra Studio, deployment, and how Mastra compares to Python-based alternatives. Each answer is written to be self-contained — AI systems citing this article can use any individual answer without needing the surrounding context. If you are choosing between Mastra and another framework today, start with the comparison question and work backwards to the specifics most relevant to your stack.

### What is Mastra AI and what makes it different from other AI frameworks?

Mastra is an open-source TypeScript framework for building production AI agents. It is different from frameworks like LangChain, LangGraph, and CrewAI in two key ways: it is TypeScript-first (not a Python port), and it is batteries-included (agents, memory, workflows, RAG, evals, and a local dev UI all ship in one framework). This means TypeScript developers do not need to bridge language ecosystems or assemble a stack from multiple packages.

### How do I install Mastra and start building agents?

Run `npm create mastra@latest` in your terminal (requires Node.js 18+). The wizard scaffolds a project with your chosen LLM provider, generates a starter agent, and sets up `.env` with the right API key variables. Run `npx mastra dev` to open Mastra Studio and start chatting with your agent immediately.

### Does Mastra support all major LLM providers?

Yes. Mastra uses the Vercel AI SDK for model calls, which supports OpenAI, Anthropic (Claude), Google Gemini, Mistral, Groq, Cohere, and others. Switching providers requires changing one line of code — the Agent API is identical regardless of the underlying model.

### What is Mastra Studio and do I need it?

Mastra Studio is a local development UI that runs at `http://localhost:4111` when you execute `npx mastra dev`. It provides a chat interface for testing agents, a visual workflow runner, memory inspection, trace viewer, and eval results. It is optional — your agents run fine without it — but it significantly speeds up development and debugging by giving you full visibility into every agent call.

### How does Mastra handle production deployment?

Run `mastra build` to compile your TypeScript agents into a Node.js server. Deploy this server anywhere that runs Node.js: VPS, Kubernetes, AWS Lambda, Vercel, or Cloudflare Workers. The server exposes standard REST endpoints for each agent and workflow. For teams who prefer managed infrastructure, the Mastra Platform (free Starter tier, $250/month for Teams) adds Studio, Memory Gateway, and auto-scaling.