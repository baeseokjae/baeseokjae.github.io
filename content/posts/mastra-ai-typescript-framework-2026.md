---
title: "Mastra AI: The TypeScript AI Agent Framework for 2026"
date: 2026-04-21
tags:
  - ai
  - typescript
  - mastra
  - llm
  - mcp
  - agents
  - developer-tools
description: "A practical guide to Mastra AI, the TypeScript-first framework for building production AI agents. Covers setup, agents, tools, MCP, workflows, RAG, evals"
draft: false
cover:
  image: /images/mastra-ai-typescript-framework-2026.png
  alt: "Mastra AI TypeScript Framework for 2026 – agents, tools, workflows, and production deployment"
schema: "mastra-ai-typescript-framework-2026"
---

## Introduction: Why Mastra Is the TypeScript AI Framework to Watch in 2026

Mastra has accumulated 23,200+ GitHub stars and $35M in funding as of April 2026, making it the most well-resourced TypeScript-native AI agent framework available—and the adoption data suggests it has earned that position. Built by the team behind Gatsby (the React static-site generator that peaked at 50,000+ GitHub stars), Mastra brings production-grade primitives for agents, tools, workflows, RAG, evals, and observability to TypeScript developers who previously had no equivalent to Python's LangChain or CrewAI ecosystems. The timing matters: 60–70% of YC X25 agent startups are building in TypeScript, not Python, according to Mastra CEO Sam Bhagwat. That demand existed before Mastra; Mastra is simply the first framework purpose-built to meet it at a production scale.

The AI agent ecosystem has a Python problem. Not with Python itself—it works fine—but with the fact that most agents ship as web services, and the teams building those services increasingly write TypeScript. Sam Bhagwat, CEO of Mastra, noted on Hacker News that 60–70% of YC X25 agent startups are building in TypeScript, not Python. The tooling hasn't caught up. LangChain, CrewAI, and AutoGen all originated in Python, leaving TypeScript developers either wrapping Python services or cobbling together their own agent infrastructure.

Mastra was built to close that gap.

### The shift from Python to TypeScript for AI agents

The shift is practical, not ideological. When your production stack runs on Node.js or edge runtimes, reaching for a Python framework introduces serialization overhead, deployment complexity, and a skills mismatch. TypeScript gives you shared types between your agent logic and your API layer, native streaming support for Server-Sent Events and WebSocket responses, and a single runtime for your entire backend. The ergonomics matter: you can define a tool's input schema with Zod, pass that schema directly to the LLM as a function definition, and validate the LLM's output against the same schema—no JSON Schema translation layer required.

### What is Mastra?

Mastra is an open-source (Apache 2.0) TypeScript framework for building AI agents. It was created by the team behind Gatsby, the React static-site generator that peaked at 50k+ GitHub stars. That team shipped a framework before; they understand the ergonomics of developer tooling. Mastra provides structured primitives for agents, tools, workflows, RAG pipelines, evals, and observability—all expressed as TypeScript code, not YAML DSLs or visual editors that generate unreadable files.

The project has accumulated 23,200+ GitHub stars, 14,334 commits, and 1,079 branches as of April 2026. The velocity is real. Mastra raised a $22M Series A led by Spark Capital in early 2026, bringing total funding to $35M.

### Enterprise adoption

The customer list is worth examining because it signals production readiness, not just developer enthusiasm:

| Company | Use Case |
|---|---|
| Docker | Event-driven PR management agents with MCP |
| Brex | Financial agents that helped drive the $5.1B Capital One acquisition |
| Marsh McLennan | Enterprise search agent used by 100k+ people daily |
| Elastic | Agentic RAG with Elasticsearch |
| SoftBank | Enterprise productivity at scale |
| Replit | Agent 3 built on Mastra primitives |
| MongoDB, Workday, Salesforce, Plaid | Various production agent deployments |

That's not a "coming soon" list. Marsh McLennan's agent is in daily production use by over 100,000 people. Brex's agents contributed to a multi-billion-dollar acquisition. These are load-bearing systems.

## Getting Started: Setting Up Your First Mastra Project

A Mastra project goes from zero to running agent in under five minutes with `npm create mastra@latest`—a single command that scaffolds everything including the interactive dev UI. You need Node.js 18+ and an API key from OpenAI, Anthropic, or Google; the scaffold prompts you to choose your preferred provider during setup. What you get is a TypeScript project with structured directories for agents, tools, workflows, and RAG pipelines—all expressed as typed code with no YAML DSLs or configuration files that generate unreadable output. The framework then auto-discovers and registers everything based on exports, so adding a new agent is as simple as exporting it from the agents directory. Mastra Studio, the local dev UI, starts on port 4111 and gives you a chat interface, workflow visualizer, and trace viewer without any additional configuration.

### Prerequisites and installation

You need Node.js 18+ and an LLM API key (OpenAI, Anthropic, or Google). Create a new project:

```bash
npm create mastra@latest
```

The scaffold prompts you for a project name, your preferred LLM provider, and whether you want the Mastra Studio dev UI included. After setup:

```bash
cd my-mastra-app
npm install
npm run dev
```

The dev server starts on port 4111 by default and opens Mastra Studio.

### Project structure overview

A scaffolded Mastra project looks like this:

```
my-mastra-app/
├── src/
│   └── mastra/
│       ├── agents/
│       │   └── index.ts        # Agent definitions
│       ├── tools/
│       │   └── index.ts        # Tool definitions
│       ├── workflows/
│       │   └── index.ts        # Workflow definitions
│       ├── rag/
│       │   └── index.ts        # RAG pipeline config
│       └── index.ts           # Mastra instance entry point
├── mastra.config.ts            # Framework configuration
├── package.json
└── tsconfig.json
```

All agent configuration lives in TypeScript files under `src/mastra/`. The framework discovers and registers agents, tools, and workflows based on exports from these files. No YAML, no code generation.

### Mastra Studio: the interactive dev UI

Mastra Studio runs locally at `http://localhost:4111` and provides:

- **Agent playground**: chat with any defined agent, inspect tool calls, and trace token usage in real time
- **Workflow visualizer**: see step DAGs, run workflows step by step, and inspect intermediate state
- **RAG testing**: query your knowledge base and verify retrieval quality
- **Eval runner**: execute model-graded and rule-based evaluations against agent outputs
- **Logs and traces**: structured view of every LLM call, tool invocation, and workflow transition

Studio is not required in production—it's a dev-time tool. But it replaces the ad-hoc `console.log`-driven debugging loop that most agent developers fall into.

## Building Your First AI Agent with Mastra

In Mastra, an agent is a typed TypeScript object—a model reference, a system prompt, and a set of tools—that can be defined in under 20 lines of code and immediately tested via Mastra Studio. The framework uses Zod schemas for tool input validation, which serves double duty: the same schema that validates runtime inputs is used to generate the JSON Schema that the LLM receives as its function-calling definition, eliminating the translation layer that causes silent mismatches in other frameworks. Mastra supports model-switching by changing a single line, since it uses the Vercel AI SDK model interface under the hood—any provider that implements that interface works without changing agent logic. Memory is built in, with two distinct primitives—working memory for structured short-term state and semantic recall for retrieving relevant past conversation turns—giving agents context-awareness that persists across a session without overloading the context window.

### Defining an agent with system prompts and tools

An agent in Mastra is a typed object with a system prompt, a model reference, and a set of tools. Here's a minimal research agent:

```typescript
import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import { openai } from "@ai-sdk/openai";

const searchTool = createTool({
  id: "web-search",
  description: "Search the web for information about a topic",
  inputSchema: z.object({
    query: z.string().describe("The search query"),
  }),
  execute: async ({ context }) => {
    const results = await fetchSearchResults(context.query);
    return { results };
  },
});

const researchAgent = new Agent({
  name: "research-agent",
  instructions: `You are a research assistant. When asked about a topic:
1. Search the web for relevant information
2. Synthesize the findings into a concise summary
3. Cite your sources
Always use the search tool before answering factual questions.`,
  model: openai("gpt-4o"),
  tools: { searchTool },
});
```

Key design decisions here: tools use Zod schemas for both input validation and LLM function-calling definition. The `instructions` field replaces the informal system-prompt string with a structured prompt that Mastra can version, evaluate against, and refactor across deployments.

### Adding memory

Mastra supports two memory primitives: **working memory** and **semantic recall**.

Working memory is a short-term scratchpad that persists within a conversation thread. It stores structured state the agent can read and write:

```typescript
import { Memory } from "@mastra/memory";

const memory = new Memory({
  options: {
    lastMessages: 10,        // Include last 10 messages in context
    workingMemory: {
      enabled: true,
      template: `
# User Profile
- Name: unknown
- Preferences: unknown
- Current Task: none
      `,
    },
    semanticRecall: {
      topK: 3,               // Recall 3 most relevant past messages
      messageRange: 2,       // Include 2 messages around each match
    },
  },
});

const contextualAgent = new Agent({
  name: "contextual-agent",
  instructions: "You are a helpful assistant that remembers user context.",
  model: openai("gpt-4o"),
  memory,
});
```

Semantic recall embeds past conversation turns and retrieves the top-K most relevant ones when a new message arrives. This means the agent can reference a preference mentioned 50 turns ago without loading the entire history into the context window. Working memory lets the agent maintain structured state—user profile, task progress, preferences—that persists across messages in the same thread.

### Connecting LLM providers

Mastra uses the Vercel AI SDK model interface, so any provider that implements that interface works:

```typescript
import { openai } from "@ai-sdk/openai";
import { anthropic } from "@ai-sdk/anthropic";
import { google } from "@ai-sdk/google";

// Swap models by changing one line
const agent = new Agent({
  name: "flexible-agent",
  instructions: "You are a versatile assistant.",
  model: anthropic("claude-sonnet-4-20250514"),
  // model: openai("gpt-4o"),
  // model: google("gemini-2.0-flash"),
});
```

Being model-agnostic matters operationally: you can run evals across models, fall back from one provider to another, and choose cost-effective models per task without rewriting agent logic.

## Tools and MCP: Connecting Your Agent to the Real World

Mastra tools use the `createTool` API with Zod input and output schemas, and every tool definition doubles as both a runtime validator and an LLM function-calling specification—meaning a single schema definition covers the full round-trip without manual JSON Schema translation. More significantly, Mastra implements both the client and server sides of MCP (Model Context Protocol), Anthropic's open standard for connecting LLMs to external tools and data sources. This gives Mastra agents access to a growing ecosystem of pre-built MCP servers—GitHub, Slack, filesystem, databases—without custom API integration code. Docker's production deployment demonstrates the pattern at scale: their PR automation agents connect through Mastra's MCPClient to the GitHub MCP server, using standard MCP tools to read diffs, post comments, and manage labels, with the entire integration reducible to a few lines of TypeScript configuration.

### Built-in tool types in Mastra

Mastra's `createTool` API is the foundational primitive. Every tool has an `id`, a `description` (used in the LLM's function-calling prompt), an `inputSchema` (Zod), and an `execute` function:

```typescript
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

const calculateTool = createTool({
  id: "calculate",
  description: "Evaluate a mathematical expression",
  inputSchema: z.object({
    expression: z.string().describe("Math expression to evaluate, e.g. '2 + 2'"),
  }),
  outputSchema: z.object({
    result: z.number(),
  }),
  execute: async ({ context }) => {
    // Safe evaluation — no eval()
    const result = safeMathEval(context.expression);
    return { result };
  },
});
```

The `outputSchema` is optional but recommended. When provided, Mastra validates the tool's output against it before returning the result to the agent. This catches malformed tool outputs early and prevents cascading errors.

### MCP (Model Context Protocol) integration

MCP is Anthropic's open protocol for connecting LLMs to external tools and data sources. Mastra implements both the client and server sides. As a client, Mastra can connect to any MCP server and expose its tools to agents:

```typescript
import { MCPClient } from "@mastra/mcp";

const mcp = new MCPClient({
  servers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: {
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_TOKEN!,
      },
    },
  },
});

// MCP tools are automatically available to agents
const tools = await mcp.tools();
```

This is how Docker connected their agents to GitHub. The GitHub MCP server provides tools for listing PRs, reading diffs, posting comments, and managing labels—all without writing custom API integration code.

### Real example: GitHub MCP server for PR automation

Docker's architecture is instructive. They built three sub-agents, each with a narrow responsibility:

1. **Analyze PR agent**: Reads the PR diff and generates a structured analysis
2. **Generate comment agent**: Takes the analysis and writes a review comment
3. **Post and close agent**: Posts the comment and manages PR labels

These agents are orchestrated by a Mastra workflow that triggers on a GitHub webhook event. The key insight: rather than one monolithic agent trying to do everything, each agent has a focused system prompt and minimal tool access. This reduces error rates and makes the system auditable—if the posted comment is wrong, you check agent 2, not the entire pipeline.

```typescript
// Simplified Docker-style PR automation workflow trigger
app.post("/webhook/github", async (req, res) => {
  const { action, pull_request } = req.body;
  if (action === "opened" || action === "synchronize") {
    await prReviewWorkflow.run({
      prNumber: pull_request.number,
      repo: pull_request.base.repo.full_name,
    });
  }
  res.status(200).send("ok");
});
```

## Workflows: Orchestrating Complex Agent Tasks

Mastra workflows provide deterministic control flow for multi-step processes, complementing agents that handle open-ended LLM reasoning—and the distinction matters in production because most real-world systems need both. A workflow in Mastra is a typed DAG of steps, each with an input schema, output schema, and execute function; steps can run sequentially, in parallel, or conditionally depending on prior step output. Docker's PR automation pipeline is a canonical example: three specialized sub-agents are orchestrated by a workflow that triggers on a GitHub webhook, with each agent handling one narrowly scoped responsibility. That design makes failures auditable—if the posted comment is wrong, you check agent 2, not the entire pipeline. Workflows also support nesting, so you can compose complex processes from smaller independently testable workflow units, and each nested workflow maintains its own state and can be run in isolation during development.

### When to use workflows vs agents

An agent with tools handles simple request-response patterns well. But when your task involves multiple sequential steps, conditional branching, parallel execution, or retry logic, you need a workflow. The distinction:

- **Agent**: LLM decides what to do next based on context. Good for open-ended reasoning.
- **Workflow**: You define the control flow. Good for deterministic multi-step processes.

If you can draw a flowchart for your process, use a workflow. If the process requires the LLM to decide its own path, use an agent. Many production systems combine both: a workflow orchestrates high-level steps, and agents handle LLM-driven reasoning within individual steps.

### Building step-based workflows

Mastra workflows are defined as a series of steps, each with an input schema, an output schema, and an execute function:

```typescript
import { Workflow, Step } from "@mastra/core/workflows";
import { z } from "zod";

const fetchContentStep = new Step({
  id: "fetch-content",
  inputSchema: z.object({ url: z.string() }),
  outputSchema: z.object({ content: z.string(), title: z.string() }),
  execute: async ({ context }) => {
    const page = await fetch(context.url).then((r) => r.text());
    const title = extractTitle(page);
    return { content: page, title };
  },
});

const summarizeStep = new Step({
  id: "summarize",
  inputSchema: z.object({ content: z.string() }),
  outputSchema: z.object({ summary: z.string() }),
  execute: async ({ context, mastra }) => {
    const agent = mastra.getAgent("research-agent")!;
    const result = await agent.generate(
      `Summarize this content concisely:\n\n${context.content}`
    );
    return { summary: result.text };
  },
});

const contentWorkflow = new Workflow({
  name: "content-summarizer",
  triggerSchema: z.object({ url: z.string() }),
});

contentWorkflow
  .step(fetchContentStep)
  .then(summarizeStep)
  .commit();
```

Steps can reference the Mastra instance to use agents, tools, or other workflows. The `context` object carries the output of the previous step(s).

### Parallel execution, conditional branching, and nesting

Workflows support `branch` for conditional paths and `parallel` for concurrent execution:

```typescript
contentWorkflow
  .step(fetchContentStep)
  .branch([
    {
      condition: ({ context }) => context.content.length > 5000,
      then: longContentStep,
    },
    {
      condition: ({ context }) => context.content.length <= 5000,
      then: shortContentStep,
    },
  ])
  .then(summarizeStep)
  .commit();

// Parallel execution
analysisWorkflow
  .parallel([sentimentStep, entityStep, keywordStep])
  .then(mergeResultsStep)
  .commit();
```

Workflows can also nest: a step can invoke another workflow as a sub-routine. This lets you compose complex processes from smaller, testable workflow units. Each nested workflow maintains its own state and can be run and debugged independently.

## RAG with Mastra: Giving Your Agent Knowledge

Mastra's built-in RAG module ships with embedding, vector search, query transformation, hybrid search, and re-ranking—all configurable via constructor options without external integrations. This matters because most agent frameworks treat RAG as an exercise left for the developer: you wire together an embedding model, a vector store, a retrieval function, and a prompt template yourself. Mastra provides the entire pipeline as a first-class primitive, and the `rag.asTool()` method wraps any RAG pipeline as a Mastra tool that any agent can call directly. Vector store support is vendor-agnostic: Pinecone, Elasticsearch, pgvector, and other stores are swappable without changing agent code. Elastic's published walkthrough demonstrates the pattern—indexing documents into Elasticsearch with dense vector fields, querying via the Mastra RAG module, and generating answers through a RAG-enabled agent—all in a single TypeScript codebase with shared types across the data layer and the agent interface.

### Embedding and vector search support

Mastra includes built-in embedding and vector search through its RAG module. You define an embedder and a vector store, then index documents:

```typescript
import { MastraRAG } from "@mastra/rag";
import { openai } from "@ai-sdk/openai";
import { PineconeVector } from "@mastra/pinecone";

const rag = new MastraRAG({
  embedder: openai.embedding("text-embedding-3-small"),
  vectorStore: new PineconeVector({
    indexName: "knowledge-base",
  }),
});

// Index documents
await rag.index({
  docs: [
    { id: "doc-1", text: "Mastra supports multiple LLM providers..." },
    { id: "doc-2", text: "Workflows enable conditional branching..." },
  ],
});

// Query
const results = await rag.retrieve({
  query: "How do I branch in a workflow?",
  topK: 5,
});
```

Mastra handles chunking, embedding, and storage. You control the chunk size, overlap, and embedding model.

### Mastra built-in RAG capabilities

Beyond basic retrieval, Mastra provides:

- **Query transformation**: Automatically rewrites user queries for better retrieval
- **Hybrid search**: Combines vector similarity with keyword matching for improved recall
- **Re-ranking**: Applies a second-pass relevance model to filter and reorder results

These are not external integrations—they ship with the framework and are configurable via the RAG constructor options.

### Integration with Elasticsearch and other vector stores

Elastic published a detailed walkthrough of building agentic RAG with Mastra and Elasticsearch. The pattern:

1. Index documents into Elasticsearch with dense vector fields
2. Use Mastra's RAG module with the Elasticsearch vector store adapter
3. Define an agent that retrieves context and generates answers

```typescript
import { MastraRAG } from "@mastra/rag";
import { ElasticsearchVector } from "@mastra/elasticsearch";

const rag = new MastraRAG({
  embedder: openai.embedding("text-embedding-3-small"),
  vectorStore: new ElasticsearchVector({
    indexName: "docs-index",
    client: esClient,
  }),
});

const ragAgent = new Agent({
  name: "rag-agent",
  instructions: `Answer questions based on the retrieved context.
If the context doesn't contain enough information, say so.
Always cite the source document.`,
  model: openai("gpt-4o"),
  tools: {
    retrieve: rag.asTool(),
  },
});
```

The `rag.asTool()` method wraps the RAG pipeline as a Mastra tool, making it available to any agent. The Elastic integration demonstrates that Mastra's RAG layer is vendor-agnostic—you can swap Pinecone for Elasticsearch for pgvector without changing agent code.

## Productionizing: Evals, Observability, and Guardrails

Mastra wires evals, OpenTelemetry tracing, and input/output guardrails into every framework primitive—a meaningful differentiator, since most agent frameworks leave all three as integration exercises. Every LLM call, tool invocation, and workflow step is automatically traced and surfaced in Mastra Studio with token usage, latency, tool call sequences, and memory retrieval scores. For production monitoring, Mastra exports to any OTel-compatible backend (Datadog, Grafana, Honeycomb) with a few lines of configuration. The eval framework supports two evaluation modes: model-graded assessments for open-ended quality measurement and rule-based deterministic checks for guardrails enforcement. This combination—observability built in, not bolted on—is the key reason enterprises like Marsh McLennan could confidently scale a Mastra-based agent to 100,000+ daily users, because the infrastructure to measure and monitor quality was available from day one rather than added after incidents surfaced.

### Running model-graded and rule-based evals

Mastra includes an evaluation framework that runs LLM outputs against criteria. Two eval types:

- **Model-graded**: An LLM judges the output against a rubric. Useful for open-ended quality assessment.
- **Rule-based**: Deterministic checks on output structure, content, or behavior. Useful for guardrails.

```typescript
import { Eval } from "@mastra/evals";
import { z } from "zod";

const relevanceEval = new Eval({
  name: "relevance",
  type: "model-graded",
  prompt: `Rate the relevance of the answer to the question on a scale of 1-5.
Question: {{input}}
Answer: {{output}}
Respond with a number only.`,
  model: openai("gpt-4o-mini"),
});

const noPIIEval = new Eval({
  name: "no-pii",
  type: "rule-based",
  check: ({ output }) => {
    const piiPatterns = [/\b\d{3}-\d{2}-\d{4}\b/, /\b[A-Z]\d{8}\b/];
    return !piiPatterns.some((p) => p.test(output));
  },
});
```

You run evals against datasets in Mastra Studio or programmatically. The results give you a quantifiable quality signal before deploying changes.

### Tracing agent calls and token usage

Every LLM call, tool invocation, and workflow step is automatically traced. In Mastra Studio, you see:

- Total latency per request
- Token usage breakdown (prompt vs. completion)
- Tool call sequences and their outputs
- Memory retrieval operations and their relevance scores

For production monitoring, Mastra integrates with OpenTelemetry. You can export traces to any OTel-compatible backend (Datadog, Grafana, Honeycomb, etc.):

```typescript
// mastra.config.ts
export default defineConfig({
  observability: {
    otel: {
      enabled: true,
      serviceName: "my-mastra-app",
      traceExporter: "otlp",
      endpoint: "http://localhost:4318/v1/traces",
    },
  },
});
```

This is a meaningful differentiator. Most agent frameworks leave observability as an exercise for the developer. Mastra wires it into every primitive.

### Guardrails for prompt injection prevention

Mastra provides input and output guardrails as middleware on agent calls:

```typescript
import { guardrail } from "@mastra/guardrails";

const agent = new Agent({
  name: "safe-agent",
  instructions: "You are a helpful assistant.",
  model: openai("gpt-4o"),
  guardrails: {
    input: [
      guardrail.injectionDetection(), // Detect common injection patterns
    ],
    output: [
      guardrail.lengthLimit({ maxTokens: 500 }),
      guardrail.piiDetection(),       // Block outputs containing PII
    ],
  },
});
```

Input guardrails run before the LLM call. Output guardrails run after. If a guardrail triggers, the agent returns a structured error instead of the raw LLM output. This is not a complete security solution—you still need proper access controls and sandboxing—but it adds a structured layer of defense.

### Mastra Studio metrics, logs, and datasets

Studio aggregates eval results, trace data, and token usage into dashboards. You can:

- Compare eval scores across model versions
- Track token cost trends over time
- Build evaluation datasets from production traces
- Replay failed conversations to diagnose issues

The dataset feature is particularly useful: you can capture production agent interactions, annotate them, and use them as regression test suites when you change prompts, models, or tools.

## Deployment: From Dev to Production

Mastra auto-generates a REST API from your agent and workflow definitions with no manual route wiring—`createServer(mastra)` exposes generate, stream, and workflow endpoints directly from your Mastra instance. The deployment surface covers the full spectrum from self-hosted to fully managed: you can deploy the auto-generated server to any Node.js host, integrate it as middleware into Next.js, Express, or Hono applications, or use the Mastra Platform for a hosted memory gateway and managed deployment with persistent cross-session state. Pricing on the managed platform starts at free (3 agents, 10,000 memory records), scales to $250 per team per month for unlimited agents and 1 million memory records on the Teams tier, and offers enterprise contracts with dedicated infrastructure and SLAs. The self-hosted path has no artificial limits—you control the infrastructure, and the framework's MIT-compatible Apache 2.0 license imposes no usage restrictions.

### Mastra Server: deploying as a REST API

Mastra generates a server that exposes your agents, tools, and workflows as REST endpoints:

```typescript
import { Mastra } from "@mastra/core";
import { createServer } from "@mastra/server";

const mastra = new Mastra({
  agents: { researchAgent, contextualAgent },
  workflows: { contentWorkflow },
});

const server = createServer(mastra);
server.listen(3000);
```

This gives you REST endpoints like:

- `POST /api/agents/researchAgent/generate` — single-turn generation
- `POST /api/agents/researchAgent/stream` — streaming generation
- `POST /api/workflows/contentWorkflow/run` — trigger a workflow
- `GET /api/workflows/contentWorkflow/runs/{runId}` — check workflow status

The API is auto-generated from your Mastra instance definition. No manual route wiring.

### Framework integration

Mastra integrates with popular Node.js frameworks as middleware:

**Next.js (App Router)**:
```typescript
// app/api/agents/[agentId]/route.ts
import { mastra } from "@/mastra";
import { NextRequest } from "next/server";

export async function POST(
  req: NextRequest,
  { params }: { params: { agentId: string } }
) {
  const agent = mastra.getAgent(params.agentId);
  const { message } = await req.json();
  const result = await agent.generate(message);
  return Response.json({ text: result.text });
}
```

**Express**:
```typescript
import express from "express";
import { mastra } from "./mastra";

const app = express();
app.use(express.json());

app.post("/api/agents/:agentId/generate", async (req, res) => {
  const agent = mastra.getAgent(req.params.agentId);
  const result = await agent.generate(req.body.message);
  res.json({ text: result.text });
});

app.listen(3000);
```

**Hono and SvelteKit** are similarly supported with adapter packages. The pattern is the same: import your Mastra instance, call `getAgent` or `getWorkflow`, and handle the request.

### Mastra Platform: Studio + Server + Memory Gateway

For teams that don't want to manage their own infrastructure, Mastra offers a hosted platform:

- **Mastra Studio (cloud)**: Same dev UI, hosted and shared across your team
- **Mastra Server (cloud)**: Managed deployment of your agents and workflows
- **Memory Gateway**: Hosted memory service with persistent storage, semantic recall, and cross-session state

### Pricing and tiers

| Tier | Price | Key Limits |
|---|---|---|
| Starter | Free | 3 agents, 10k memory records, community support |
| Teams | $250/team/month | Unlimited agents, 1M memory records, priority support |
| Enterprise | Custom | Dedicated infra, SLA, SSO, custom integrations |

The free tier is genuinely usable for prototyping and personal projects. The Teams tier is where production deployments land.

## Mastra vs Other AI Frameworks: TypeScript-First Comparison

Mastra's primary competitors—LangGraph and CrewAI—are Python frameworks, which is the most fundamental distinction in 2026 when 60–70% of YC X25 agent startups choose TypeScript. The operational cost of wrapping a Python framework in a Docker service and communicating via HTTP is real: it adds serialization overhead, prevents sharing types across your stack, requires separate test infrastructure, and adds a deployment dependency that TypeScript teams typically don't want. Beyond language, Mastra includes built-in evals, a RAG module, OpenTelemetry observability, and MCP client/server support—capabilities that require third-party integrations (LangSmith, custom retrieval chains) or are simply absent in LangGraph and CrewAI. The Vercel AI SDK is a complementary rather than competing tool: Mastra uses it under the hood for LLM calls and works alongside it in stacks that use the AI SDK for frontend streaming.

### Mastra vs LangGraph vs CrewAI

| Feature | Mastra | LangGraph | CrewAI |
|---|---|---|---|
| Language | TypeScript | Python | Python |
| Agent abstraction | `Agent` class with tools + memory | `StateGraph` with nodes/edges | `Crew` with `Agent` roles |
| Workflow model | Step-based with branch/parallel | State graph with conditional edges | Sequential/hierarchical process |
| Memory | Built-in (working + semantic recall) | Manual (checkpointer interface) | Short-term + long-term memory |
| Observability | Built-in OTel + Studio | LangSmith (separate product) | Manual or LangSmith |
| Eval framework | Built-in | LangSmith (separate product) | Not included |
| MCP support | Client + server | Client (via langchain-mcp) | Not native |
| RAG | Built-in module | Manual (LangChain retrieval) | Manual |
| Deployment | Built-in server + Platform | Manual or LangServe | Manual |
| License | Apache 2.0 | MIT | MIT |

The core distinction: LangGraph and CrewAI are Python frameworks that require the Python ecosystem for production deployment. If your stack is TypeScript, you'll write a Python service, wrap it in a Docker container, and communicate via HTTP. That works, but it adds operational overhead and prevents you from sharing types, tests, and utilities across your codebase.

### Mastra vs Vercel AI SDK

The Vercel AI SDK focuses on LLM integration at the transport layer: streaming responses, managing tool calls, and providing React hooks for chat UIs. Mastra operates at a higher level:

- **Vercel AI SDK**: "How do I call an LLM and stream the response to a React component?"
- **Mastra**: "How do I build an agent with memory, tools, and guardrails, evaluate it, and deploy it as an API?"

They're complementary. Mastra uses the Vercel AI SDK's model interface under the hood for LLM calls. You can use the Vercel AI SDK for your frontend chat UI and Mastra for your backend agent logic.

### When to choose Mastra (and when not to)

Choose Mastra when:
- Your backend is TypeScript/Node.js
- You need structured agents with memory, tools, and guardrails
- You want built-in evals and observability without extra tooling
- You're building multi-step workflows with conditional logic

Skip Mastra when:
- Your team is Python-first and you're happy with LangGraph or CrewAI
- You only need raw LLM streaming (use Vercel AI SDK directly)
- You need capabilities Mastra doesn't support yet (e.g., specialized multimodal agent patterns)

## Real-World Examples and Case Studies

The four most instructive Mastra deployments in production are Docker's event-driven PR automation (which processes GitHub webhooks with no human in the loop), Elastic's agentic RAG assistant (built in a single TypeScript codebase spanning frontend, backend, and vector search), Marsh McLennan's enterprise search agent (serving 100,000+ users daily in production), and Replit's Agent 3 (which can scaffold and deploy new Mastra agents from a natural-language description). Each case study illustrates a different production pattern: event-driven pipelines, full-stack TypeScript, enterprise scale, and meta-level agent composition. Together they confirm that Mastra handles the operational requirements—observability, memory management, workflow orchestration, and reliable tool execution—that separate production deployments from demos. Marsh McLennan's deployment alone serves over 100,000 users every day, making it one of the largest known Mastra-based rollouts in any industry. The details below explain what each team built and which Mastra primitives made the difference.

### Docker: Event-driven PR management agent

Docker built an event-driven agent system that responds to GitHub webhooks. When a PR is opened, their Mastra workflow:

1. Triggers on the webhook payload
2. Routes through the Docker MCP Gateway to the GitHub MCP server
3. Runs the analyze PR agent on the diff
4. Passes the analysis to the generate comment agent
5. Posts the comment via the post and close agent

This is not a chatbot. There's no human in the loop. The entire pipeline runs in response to an event, with no user interaction. That's a different deployment model from most demo agents, and it's where Mastra's workflow primitives matter—the pipeline is deterministic, observable, and can fail gracefully at any step.

### Elastic: Agentic RAG with Elasticsearch

Elastic built a RAG assistant combining a Vite + React frontend, a Mastra backend, and Elasticsearch as the vector store. Their writeup highlights the developer experience of staying in a single language stack: the same TypeScript types that define the search index schema also define the agent's tool interface and the frontend's API contract.

### SoftBank: Enterprise productivity at scale

SoftBank deployed Mastra-based agents internally for productivity tools. Scale is the notable aspect—this isn't a prototype serving 10 users. Mastra's memory gateway and observability infrastructure handle the traffic.

### Replit: Agent 3 building Mastra agents

Replit's Agent 3 can scaffold and deploy Mastra agents. This meta-pattern—an AI agent building other AI agents—validates Mastra's code-first API design. If an LLM can generate valid Mastra code from a description, the abstractions are well-defined enough to be machine-writable.

## Conclusion and Next Steps

Mastra addresses a real gap in the AI agent tooling ecosystem: a production-grade, TypeScript-native framework with first-class support for the primitives that matter—agents, tools, workflows, RAG, evals, and observability. The enterprise adoption numbers (100k+ daily users at Marsh McLennan, Brex's $5.1B acquisition involvement) confirm that it's not just developer-friendly but production-ready. The framework's 23,200+ GitHub stars and $35M in total funding reflect genuine developer adoption rather than marketing momentum—a distinction that matters when choosing infrastructure you'll depend on for years. For TypeScript teams evaluating AI agent frameworks in 2026, Mastra is the clearest option: it covers the full stack from local development through production deployment, it integrates with the tools you already use, and its growing community and enterprise backing make it a safe long-term bet.

### Key takeaways

1. **TypeScript-first is now a viable choice for AI agents.** With 60–70% of YC X25 agent startups choosing TypeScript, the ecosystem demand is clear. Mastra provides the framework primitives that Python alternatives have had for years.
2. **MCP integration is a differentiator.** Mastra's ability to connect to any MCP server as a tool source gives agents access to external systems without custom integration code. Docker's PR automation demonstrates this in production.
3. **Built-in evals and observability are not optional extras.** If you can't measure agent quality, you can't improve it. Mastra's eval framework and OpenTelemetry integration give you measurement from day one.
4. **Workflows complement agents.** Not every problem needs an LLM deciding what to do next. Mastra's workflow engine handles the structured part of your pipeline while agents handle the reasoning part.
5. **The Gatsby team's framework experience shows.** The DX decisions—Zod schemas, code-first configuration, Studio as a dev tool—reflect experience shipping a framework used by tens of thousands of developers.

### Resources

- **Mastra docs**: [mastra.ai/docs](https://mastra.ai/docs)
- **Mastra GitHub**: [github.com/mastra-ai/mastra](https://github.com/mastra-ai/mastra)
- **Mastra templates**: [mastra.ai/templates](https://mastra.ai/templates)
- **Agent Book**: [mastra.ai/agentbook](https://mastra.ai/agentbook) — community-contributed agent examples
- **Community Discord**: [mastra.ai/community](https://mastra.ai/community)

### The future of TypeScript AI development

The trajectory is clear. As agent deployments move from demos to production, the operational requirements—evals, observability, guardrails, memory management, workflow orchestration—become the differentiating factors. Mastra builds these into the framework rather than leaving them as integration exercises. For TypeScript teams building AI agents in 2026, Mastra is the framework that matches the language, runtime, and operational demands of the job.