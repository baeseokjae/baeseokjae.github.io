---
title: "Cloudflare Project Think Guide 2026: Build Long-Running AI Agents with Durable Execution"
date: 2026-05-07T00:00:00+00:00
tags: ["cloudflare", "ai-agents", "workers", "durable-objects", "typescript", "serverless"]
description: "Cloudflare Project Think 2026: build long-running AI agents with durable execution, Fibers, Facets, and Workers infrastructure."
draft: false
cover:
  image: "/images/cloudflare-project-think-ai-agents-guide.png"
  alt: "Cloudflare Project Think Guide 2026: Build Long-Running AI Agents with Durable Execution"
  relative: false
schema: "schema-cloudflare-project-think-ai-agents-guide"
---

During Cloudflare Agents Week 2026, the internal AI engineering stack processed 20 million requests through AI Gateway and 241 billion tokens through Workers AI — the largest proof-of-concept for Cloudflare's own infrastructure as an AI agent runtime. Project Think is Cloudflare's answer to the question of how you build AI agents that run for minutes or hours, maintain state across tool calls, and spawn specialized sub-agents, all on serverless infrastructure. The framework provides a base class (`@cloudflare/think`) built on top of Durable Objects, giving agents persistent state, hibernation (zero billing during idle), and colocated sub-agent execution via RPC. As of April 2026, Project Think is in developer preview — APIs may change as feedback is incorporated. Here is a complete guide to the architecture and how to build with it.

## What is Cloudflare Project Think?

Cloudflare Project Think is a TypeScript framework for building long-running AI agents on Cloudflare's serverless infrastructure. It extends Durable Objects — Cloudflare's stateful, actor-model compute primitive — with primitives specifically designed for AI agent patterns: parallel execution threads (Fibers), modular sub-agents (Facets), persistent conversation trees (Sessions), and sandboxed code execution. The core insight behind Project Think is that most AI agent frameworks treat each tool call as a new stateless HTTP request. This works for short tasks but breaks for agents that need to maintain context across hours of execution, accumulate state between tool calls, and spawn specialized sub-agents for parallel work. Dynamic Workers, which power Project Think's sandboxed execution, are approximately 100x faster to start and up to 100x more memory-efficient than traditional containers — critical when agents need to spin up isolated execution environments on demand. Project Think is part of a broader 2026 Cloudflare push into AI infrastructure alongside Workers AI (model inference) and AI Gateway (observability and routing), positioning Cloudflare as a full-stack AI agent deployment target.

## Core Primitives: Fibers, Facets, Sessions, and Sandboxed Execution

Project Think introduces four primitives that extend the base Durable Object model for agent use:

**Fibers** are isolated execution threads within a single agent instance. Each Fiber runs independently and can be awaited, cancelled, or monitored. When an agent needs to parallelize work — run three web searches simultaneously, or process multiple files concurrently — it spawns Fibers for each task. Fibers share the parent agent's state but execute independently, making them appropriate for fan-out patterns within a single agent.

**Facets** are child Durable Objects (sub-agents) that are colocated with the parent agent. The key distinction from Fibers: Facets have their own persistent state, their own tool sets, and their own execution loops. RPC latency between a parent agent and its Facets is comparable to function calls, not HTTP round-trips. This makes Facets suitable for specialized sub-agents — a researcher Facet, an analyst Facet, a writer Facet — that maintain their own context and can be reused across multiple parent agent sessions.

**Sessions** implement tree-structured conversation history with branching support. Instead of a flat conversation list, Sessions allow agents to explore multiple reasoning paths and branch back to earlier points. This supports "what if" reasoning: the agent can try one approach, observe the result, branch back to an earlier state, and try an alternative approach — without losing the history of either path.

**Sandboxed Execution** provides isolated environments for running AI-generated code. Rather than executing model-generated code directly in the agent context, Project Think routes code execution through a sandboxed Dynamic Worker. The Execution Ladder (covered in its own section) controls which level of sandbox access an agent can escalate to, based on trust level.

## Getting Started with the Think Base Class (@cloudflare/think)

The Think base class wraps a Durable Object with the agent primitives. A basic agent implementation:

```typescript
import { Think } from '@cloudflare/think';
import { Anthropic } from '@anthropic-ai/sdk';

export class ResearchAgent extends Think {
  private client = new Anthropic();

  async run(query: string): Promise<string> {
    // think() manages the tool call loop
    const result = await this.think(query, {
      tools: [
        this.webSearch,
        this.readFile,
        this.writeFile,
      ],
      maxSteps: 20,
    });
    return result.output;
  }

  // Tool methods are automatically discovered and wrapped
  async webSearch(query: string): Promise<string> {
    // implementation
  }
}

// Worker export
export default {
  fetch: ResearchAgent.mount('/agent')
};
```

The `think()` method manages the agent loop: it calls the LLM, executes tool calls, feeds results back to the model, and iterates until the task is complete or `maxSteps` is reached. The agent's state (conversation history, tool outputs, session tree) persists in the Durable Object's storage, surviving hibernation and resuming on the next wake event.

Wrangler configuration for a Think-based agent requires Durable Objects:

```toml
name = "my-agent"
main = "src/index.ts"
compatibility_date = "2026-04-01"

[[durable_objects.bindings]]
name = "AGENT"
class_name = "ResearchAgent"

[[migrations]]
tag = "v1"
new_classes = ["ResearchAgent"]
```

## The Execution Ladder: Progressive Security for AI-Generated Code

The Execution Ladder is Project Think's model for granting AI agents progressively more powerful code execution capabilities based on trust level and task requirements:

**Level 1 — Read-only execution**: The agent can read files, query databases, and call external APIs. No write operations permitted. Default level for new agents.

**Level 2 — Isolated write access**: The agent can write to temporary directories within a sandboxed Dynamic Worker. Changes don't persist to the host environment. Appropriate for data transformation tasks.

**Level 3 — Full system with audit trail**: The agent can execute arbitrary code, modify files, and interact with the host system, but all operations are logged with full audit trail. Appropriate for code generation and deployment tasks where human review of the audit log is built into the workflow.

The Execution Ladder prevents runaway code execution by requiring explicit escalation. An agent that starts at Level 1 must request Level 2 access and receive approval (manual or automated, depending on configuration) before gaining write capability. This applies even to self-authored extensions — when an agent writes a new tool and wants to execute it, the execution goes through the Execution Ladder rather than running directly in the agent context.

## Building Modular Agents with Facets (Sub-Agents)

Facets enable multi-agent architectures where specialized agents collaborate. The orchestrator spawns Facets for specific subtasks; Facets maintain their own state and return results to the orchestrator via RPC:

```typescript
export class OrchestratorAgent extends Think {
  async run(project: string): Promise<string> {
    // Spawn specialized Facets
    const researcher = await this.facet('ResearcherFacet');
    const analyst = await this.facet('AnalystFacet');
    const writer = await this.facet('WriterFacet');

    // Fan out to Facets in parallel using Fibers
    const [researchData, marketData] = await Promise.all([
      this.fiber(() => researcher.research(project)),
      this.fiber(() => analyst.marketAnalysis(project)),
    ]);

    // Writer Facet receives outputs from both
    const report = await writer.generate({
      research: researchData,
      market: marketData,
    });

    return report;
  }
}
```

Each Facet (ResearcherFacet, AnalystFacet, WriterFacet) is its own Durable Object with its own tool set, system prompt, and state. Colocated RPC means the latency between orchestrator and Facets is negligible — unlike HTTP-based multi-agent architectures where each agent-to-agent call adds network overhead.

## Persistent Sessions: Tree-Structured Conversations and Branching

The Sessions primitive implements conversation history as a tree rather than a flat array. This enables a key capability: the agent can "branch" to explore an alternative approach without losing the path not taken.

```typescript
const session = await this.session.create('task-001');

// Branch A: try approach 1
const branchA = await session.branch();
await branchA.execute(approach1);
const resultA = await branchA.evaluate();

// Branch B: try approach 2 (from same starting point)
const branchB = await session.branch();
await branchB.execute(approach2);
const resultB = await branchB.evaluate();

// Select the better result and continue from that branch
const bestBranch = resultA.score > resultB.score ? branchA : branchB;
await session.mergeBranch(bestBranch);
```

Sessions persist in Durable Object storage, making them available across agent restarts and hibernation events. For long-running tasks that span hours, the session tree provides a complete audit trail of every reasoning path the agent explored, which approach was selected, and why — valuable for debugging and compliance.

## Self-Authored Extensions: Agents That Build Their Own Tools

Project Think enables agents to write and register new tools at runtime. When an agent encounters a capability it needs but doesn't have, it can generate the tool implementation, register it via the Extensions API, and use it in subsequent steps — without redeployment:

```typescript
// Agent generates a tool when needed
const toolCode = await this.model.generate(
  `Write a TypeScript function that parses CSV files and returns structured data`
);

// Register the generated tool
await this.extensions.register({
  name: 'parseCSV',
  code: toolCode,
  sandbox: 'level-2',  // Execution Ladder level for this tool
});

// The tool is now available for subsequent steps
const data = await this.tools.parseCSV(csvContent);
```

All self-authored extensions execute through the Execution Ladder at the specified level — Level 2 by default, requiring explicit escalation to Level 3 for system access. The extensions registry persists in Durable Object storage, so tools the agent creates in one session are available in subsequent sessions.

## Project Think vs AWS Bedrock AgentCore vs Google ADK

| | Cloudflare Project Think | AWS Bedrock AgentCore | Google ADK |
|---|---|---|---|
| **Infrastructure** | Cloudflare Workers + Durable Objects | AWS Lambda + Bedrock | Google Cloud + Vertex |
| **State model** | Durable Object (actor model) | Session service | Session management |
| **Sub-agents** | Colocated Durable Objects (RPC) | Lambda functions (HTTP) | ADK agents (HTTP) |
| **Cold start** | ~0ms (Durable Objects warm) | 100-500ms (Lambda) | 100-500ms |
| **Idle billing** | Zero (hibernation) | Minimal (Lambda) | Minimal |
| **Code execution** | Sandboxed Dynamic Workers | AWS SageMaker/Batch | Cloud Run |
| **Best for** | Teams on Cloudflare, latency-sensitive agents | Teams on AWS, Bedrock models | Teams on GCP, Gemini-native |

Project Think's primary advantage is the actor model: Durable Objects never have cold starts after first activation, making agent wake-from-hibernation nearly instant. For agents that sleep for hours between user interactions, this eliminates the cold start latency that Lambda-based architectures introduce.

## Production Deployment: Cost, Scheduling, and Hibernation

**Hibernation** is the core cost-control mechanism. When a Think agent has no active requests or scheduled tasks, it hibernates — consuming zero compute billing. The next request or scheduled wake wakes the Durable Object, loading its state from storage. For agents that run tasks on user request rather than continuously, hibernation means you pay only during actual execution.

**Scheduling** with Cron triggers runs agents on a schedule without keeping them alive:

```typescript
// In wrangler.toml
[triggers]
crons = ["0 9 * * 1"]  # Every Monday at 9am UTC

// In agent
async scheduled(event: ScheduledEvent): Promise<void> {
  await this.run('generate weekly report');
}
```

**Pricing** for a Think-based agent on the Workers Paid plan ($5/month base): Durable Object requests at $0.15/million, Durable Object compute at $12.50/million GB-seconds, Workers AI inference at model-specific rates. For an agent that processes 100 requests per day with 30-second average execution at 128MB: roughly $15-25/month in Durable Object compute, plus model inference costs.

**SQLite storage** is available in Durable Objects for agents needing structured state beyond key-value: conversation history, tool outputs, session trees, and extension registries can all use SQLite within the Durable Object, without external database dependencies.

---

## FAQ

**What is Cloudflare Project Think?**

Project Think is a TypeScript framework in developer preview (April 2026) for building long-running AI agents on Cloudflare Workers infrastructure. It extends Durable Objects with agent-specific primitives: Fibers (parallel execution threads), Facets (colocated sub-agents), Sessions (tree-structured conversation history), and sandboxed code execution via the Execution Ladder. Agents built with Project Think persist state across tool calls and survive hibernation without losing context.

**How does Project Think differ from other agent frameworks like LangChain or CrewAI?**

Project Think is infrastructure-first rather than framework-first. LangChain and CrewAI provide high-level abstractions for agent logic that run on any infrastructure. Project Think provides lower-level infrastructure primitives (Durable Objects, Fibers, Facets) specifically designed for Cloudflare's deployment model. The advantage: zero cold starts via Durable Objects, zero idle billing via hibernation, and colocated sub-agent RPC. The tradeoff: tighter coupling to Cloudflare infrastructure.

**Is Project Think production-ready?**

As of April 2026, Project Think is in developer preview — Cloudflare explicitly notes APIs may change as feedback is incorporated. It's suitable for internal tools, prototypes, and teams willing to track API changes. Production deployments in regulated industries or with strict stability requirements should wait for general availability.

**What models does Project Think support?**

Project Think is model-agnostic. The `think()` loop works with any LLM that supports tool/function calling via an OpenAI-compatible API. Native integrations exist for Anthropic Claude, OpenAI GPT series, and models available via Cloudflare Workers AI. The agent implementation controls which model it calls; the framework handles state and execution management.

**How does billing work for hibernating agents?**

Durable Objects hibernate when idle, consuming zero compute billing. You pay only for the time the object is active: processing requests, executing tool calls, or running scheduled tasks. Storage costs (for persisted session state) continue during hibernation at Durable Object storage rates ($0.20/GB-month). For agents with low average utilization, this makes Project Think significantly cheaper than keeping a container or VM running continuously.
