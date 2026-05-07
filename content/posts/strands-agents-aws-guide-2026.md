---
title: "AWS Strands Agents SDK: Build Production AI Agents in 2026"
date: 2026-05-05T12:05:41+00:00
tags: ["AWS Strands Agents", "AI agent framework", "Amazon Bedrock", "Python AI agents", "multi-agent orchestration"]
description: "Complete guide to AWS Strands Agents SDK — install, build, deploy, and monitor production AI agents with minimal code in 2026."
draft: false
cover:
  image: "/images/strands-agents-aws-guide-2026.png"
  alt: "AWS Strands Agents SDK: Build Production AI Agents in 2026"
  relative: false
schema: "schema-strands-agents-aws-guide-2026"
---

AWS Strands Agents is an open-source Python and TypeScript SDK that lets you build production-ready AI agents in under 10 lines of code. Released by AWS in May 2025 and reaching 14 million+ downloads, it uses a model-driven loop where you describe a goal, attach tools, and the agent decides at runtime what to call and in what order.

## What Is AWS Strands Agents SDK?

AWS Strands Agents SDK is an open-source AI agent framework developed by Amazon Web Services that uses a model-driven paradigm — you describe what you want the agent to achieve, attach a set of tools, and the underlying LLM decides which tools to call, in which order, and when to stop. Unlike graph-based frameworks that require you to wire explicit nodes and edges, Strands agents reason dynamically at runtime, adapting their execution plan based on intermediate results. Since its preview launch in May 2025, Strands has accumulated 14 million+ downloads and powers internal AWS services including Amazon Q Developer, AWS Glue, and the VPC Reachability Analyzer. The SDK supports 9+ model providers — Amazon Bedrock, Anthropic, OpenAI, Gemini, LiteLLM, Llama, Ollama, and Writer — through a unified API, so you can prototype locally with Ollama and deploy to Bedrock without touching your agent logic. Version 1.0 added Graph, Swarm, and Workflow multi-agent patterns and the A2A (Agent-to-Agent) protocol for cross-framework interoperability. The result is the lowest barrier-to-entry of any major agent framework available in 2026.

## Why Strands Agents? Key Advantages Over Competitors

Strands Agents stands out from competing frameworks through three core design decisions: minimal API surface, native MCP support, and built-in observability. Where LangGraph requires you to define state schemas, build graph topologies, and wire conditional edges before writing any business logic, a functional Strands agent is four lines: import the SDK, declare tools with a decorator, instantiate an `Agent`, and call it with a string. Verisk Analytics deployed a RAG-backed Strands agent on Amazon Bedrock and reduced mean-time-to-resolution (MTTR) by 60% without any manual coding pipeline. That outcome is possible because Strands handles the entire agentic loop — tool selection, execution, result injection, and follow-up reasoning — automatically. The framework is also model-agnostic by design: switching from Claude Sonnet on Bedrock to GPT-4o on OpenAI is a one-line config change, not a framework migration. Finally, OpenTelemetry instrumentation is built in — every tool call, reasoning step, and model invocation emits traces and metrics without additional setup, routing natively to AWS X-Ray and CloudWatch. For teams already running workloads on AWS, this is a compelling stack: write minimal Python, deploy to Bedrock AgentCore, and get full observability for free.

### When Strands Beats the Alternatives

Strands is the right choice when you want fast iteration, MCP tool reuse, or an AWS-native deployment path. If your workflow is deterministic and requires strict execution ordering with human-in-the-loop checkpoints, LangGraph's state-machine model is stronger. If you're organizing a large team of specialized agents with a crew/role mental model, CrewAI's abstractions are more intuitive for product managers. For everything else — especially when MCP tool servers already exist for your data sources — Strands wins on productivity.

## Installation and Quick Start (Python & TypeScript)

Installing AWS Strands Agents takes under a minute and requires no AWS account for local development with Ollama. For Python, run `pip install strands-agents` and optionally `pip install strands-agents-tools` for the 30+ built-in tools. For TypeScript, run `npm install @strands/agents`. A minimal working agent in Python requires four lines of code: import `Agent` and `tool`, decorate a function with `@tool`, create `agent = Agent(tools=[your_tool])`, and call `agent("your prompt")`. The agent calls your tool as many times as needed, reasons about the results, and returns a final answer — no graph, no state schema, no chain. For production use with Amazon Bedrock, set `AWS_DEFAULT_REGION` and install `strands-agents[bedrock]`; for Anthropic, set `ANTHROPIC_API_KEY` and pass `model=AnthropicModel("claude-sonnet-4-6")` to the `Agent` constructor. The model-swap is the only change required; all tool definitions, agent logic, and multi-agent patterns remain identical across providers.

### Your First Agent in Python

```python
from strands import Agent, tool

@tool
def get_weather(city: str) -> str:
    """Return current weather for a city."""
    return f"{city}: 22°C, partly cloudy"

agent = Agent(tools=[get_weather])
response = agent("What's the weather in Berlin?")
print(response)
```

That is a complete, runnable agent. Add a `model=` parameter to switch providers; add more `@tool` functions to expand capabilities. The agent loop handles everything else.

### TypeScript Quick Start

```typescript
import { Agent, tool } from "@strands/agents";
import { z } from "zod";

const getWeather = tool({
  name: "get_weather",
  description: "Return current weather for a city",
  parameters: z.object({ city: z.string() }),
  execute: async ({ city }) => `${city}: 22°C, partly cloudy`,
});

const agent = new Agent({ tools: [getWeather] });
await agent.run("What's the weather in Berlin?");
```

## Core Concepts: Tools, Model Providers, and the Agent Loop

The Strands agent loop is the runtime engine that drives all agent behavior: it feeds the user prompt and tool definitions to the model, receives tool-call responses, executes the designated tools, injects results back into the conversation context, and repeats until the model emits a final text response with no pending tool calls. This loop is fully managed — you never write it manually. Tools are the primary extension point: any Python function decorated with `@tool` automatically becomes callable by the model. The SDK introspects the function's type annotations and docstring to auto-generate the JSON Schema that Strands passes to the model, so documentation doubles as the tool spec. Model providers are swappable at `Agent` instantiation time: `BedrockModel`, `AnthropicModel`, `OpenAIModel`, `OllamaModel`, and others all implement the same interface. The agent loop itself does not care which model is running; only the `model=` parameter changes. For advanced control, you can set `max_parallel_tool_calls`, configure `system_prompt`, and attach `callbacks` for streaming output or custom logging — all without modifying the loop itself. This clean separation of concerns is what makes Strands agents easy to test and maintain at production scale.

### Understanding Tool Execution

When the model decides to call a tool, Strands validates the arguments against the tool's schema, executes the function (sync or async), and serializes the return value back into the conversation. If the model requests multiple tools simultaneously, Strands executes them in parallel by default, then batches the results into a single context injection. This parallelism is transparent — your tool functions do not need to know about concurrency.

## Built-in Tool Ecosystem and MCP Integration

Strands ships with 30+ production-ready tools in the `strands-agents-tools` package covering file operations, HTTP requests, shell execution, Python REPL, database queries, image analysis, and AWS service calls (S3, DynamoDB, Lambda invoke). Beyond built-ins, Strands has first-class Model Context Protocol (MCP) support — you can connect any MCP server to your agent with three lines of code and instantly access thousands of community-built tool servers covering GitHub, Slack, Postgres, Notion, and hundreds of other services. This MCP-first design means you rarely need to write custom tools for standard integrations. The pattern is: create an `MCPClient` pointing at your MCP server URL, call `.list_tools()` to get the tool list, and pass the list to `Agent(tools=mcp_tools)`. The agent treats MCP tools identically to native `@tool` functions — same loop, same observability, same parallelism. Practically, this means a team can build an agent that queries a Postgres database, creates GitHub issues, and sends Slack notifications using only MCP servers, with zero custom integration code and full OTEL tracing on every call.

```python
from strands import Agent
from strands.tools.mcp import MCPClient

with MCPClient("http://localhost:8080") as mcp:
    tools = mcp.list_tools()
    agent = Agent(tools=tools)
    agent("Query the last 10 orders from the database")
```

Connecting a new data source becomes a matter of running an MCP server — no bespoke integration code required.

## Multi-Agent Patterns: Graph, Swarm, and Workflow

Strands Agents 1.0 introduced three structured multi-agent patterns that cover the most common production topologies: Graph, Swarm, and Workflow. Graph mode lets you define explicit agent nodes and directed edges, giving you deterministic control over which agent hands off to which — useful when you need auditability or strict sequencing for compliance. Swarm mode spins up a pool of identical worker agents that pull tasks from a shared queue; each worker operates independently and reports back to a coordinator, making Swarm ideal for embarrassingly parallel workloads like bulk document processing or parallel API calls across accounts. Workflow mode is the simplest: a linear pipeline where each agent's output becomes the next agent's input, perfect for ETL-style tasks (extract → transform → load) or document processing pipelines (ingest → summarize → classify → store). All three patterns use the same underlying `Agent` primitive and the same tool and model interfaces — the pattern controls topology, not implementation. The A2A (Agent-to-Agent) protocol allows agents built with different frameworks (LangGraph, CrewAI, custom REST services) to be treated as tools by a Strands orchestrator, so you are not locked in even at the multi-agent layer. Each pattern ships with built-in session management, so state is durable across invocations.

### Using the Handoff Primitive

The `handoff` primitive passes control to another agent or a human reviewer without terminating the session. This is the key building block for human-in-the-loop workflows: an agent completes as much work as possible autonomously, then hands off to a human when it encounters ambiguity, and resumes when the human responds. Handoffs are serializable — the session state is stored in the Session Manager (backed by DynamoDB or any key-value store) so the resuming agent picks up exactly where the previous one stopped.

## Deploying to Production: Lambda, Fargate, and Bedrock AgentCore

Strands agents can be deployed to AWS Lambda for short-lived event-driven tasks, AWS Fargate for long-running streaming agents, or Amazon Bedrock AgentCore for a fully managed production path with built-in identity, memory, observability, and tool integration. Lambda deployments suit agents with sub-15-minute execution windows and sporadic invocation patterns — the pay-per-request model is cost-efficient at low to medium scale. Fargate is the right target when agents need to stream responses in real time or when execution windows exceed Lambda's limit; a recommended architecture uses API Gateway fronting a Fargate container running the agent loop, with Lambda functions backing individual tools. Bedrock AgentCore is AWS's managed runtime for Strands agents: it eliminates infrastructure provisioning, handles auto-scaling, provides persistent session storage, and integrates Strands observability with CloudWatch and X-Ray automatically. For enterprise teams, AgentCore is the fastest path from prototype to production because it removes the need to manage container registries, IAM roles for tool execution, or session storage backends. A typical Fargate-hosted streaming agent can be wired up in under 30 lines of FastAPI code and deployed as a Docker container with a standard ECS task definition.

```python
# Fargate: expose agent as streaming HTTP endpoint
from fastapi import FastAPI
from strands import Agent
from strands.models import BedrockModel

app = FastAPI()
agent = Agent(model=BedrockModel("us.anthropic.claude-sonnet-4-6-v1"))

@app.post("/run")
async def run_agent(prompt: str):
    async for chunk in agent.stream(prompt):
        yield chunk
```

For Lambda, package the agent with a handler that instantiates `Agent` per invocation and returns the `agent(event["prompt"])` response as JSON.

### Bedrock AgentCore Deployment

```python
from strands.deploy import BedrockAgentCore

core = BedrockAgentCore(
    agent=agent,
    region="us-east-1",
    memory_backend="dynamodb",
)
core.deploy()  # provisions all infrastructure
```

AgentCore handles IAM, VPC, scaling policies, and CloudWatch dashboards automatically.

## Observability and Monitoring with OpenTelemetry

Strands Agents ships with built-in OpenTelemetry instrumentation that requires zero configuration to activate — every agent invocation automatically emits spans for model calls, tool executions, and reasoning steps. This matters because AI agent debugging without traces is guesswork: you need to see which tools were called, in what order, with what arguments, and how long each step took. Strands traces integrate natively with AWS X-Ray (via the OTEL OTLP exporter pointing at the X-Ray collector), CloudWatch (via the CloudWatch OTEL Distro), and any third-party backend that accepts OTLP — Grafana, Jaeger, or Datadog. Fan-out routing is supported, so you can send traces to X-Ray for the AWS console while simultaneously forwarding to Grafana for team dashboards. Custom attributes added via standard OTEL APIs propagate through multi-agent chains, so a root trace from an orchestrator spans all downstream worker agent calls. Metrics include token counts per call, tool latency by name, and agent loop iteration counts — all available in CloudWatch without any custom metric publishing code. In practice, a Strands agent with three tools on Bedrock produces full end-to-end traces in X-Ray within the first invocation, with no instrumentation code written by the developer.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

# Strands automatically picks up the configured OTEL provider
agent = Agent(tools=[...])
```

No Strands-specific configuration needed — standard OTEL SDK setup is sufficient.

## Strands Agents vs LangGraph vs CrewAI: Which Should You Use?

Strands Agents, LangGraph, and CrewAI each occupy a distinct position in the 2026 AI agent landscape, and the right choice depends on your workflow type, team composition, and deployment target. Strands is optimized for minimal code, fast iteration, and AWS-native deployment: it's the strongest choice for teams building on Bedrock, leveraging MCP tools, or needing to prototype and ship quickly. LangGraph is a production-grade state-machine framework — more verbose, but the most battle-tested option for complex deterministic workflows where execution order must be auditable and human-in-the-loop checkpoints are required at defined graph nodes. CrewAI uses a crew/role abstraction that maps well to organizational structures; product managers and non-engineers find it easier to reason about than graphs or loops. The critical differentiator for 2026: Strands is the only framework with a direct managed deployment target (Bedrock AgentCore) that eliminates infrastructure entirely, and it is the only one with MCP-first design that connects to community tool servers without custom code. Strands reached 1 million downloads and 3,000+ GitHub stars within just four months of its preview launch, a pace that signals strong developer adoption and active community investment.

| Feature | Strands Agents | LangGraph | CrewAI |
|---|---|---|---|
| Learning curve | Low (4 lines to start) | High (graph topology) | Medium (crew/role model) |
| Model agnostic | Yes (9+ providers) | Yes | Yes |
| MCP support | Native, first-class | Via LangChain tools | Via custom adapters |
| Managed deployment | Bedrock AgentCore | LangSmith Cloud | CrewAI Cloud |
| Multi-agent patterns | Graph, Swarm, Workflow | Graph, subgraphs | Crew, pipeline |
| Built-in observability | OTEL, X-Ray, CloudWatch | LangSmith tracing | Built-in logs |
| Best for | AWS workloads, fast iteration | Complex deterministic flows | Role-based team simulations |

### When to Stick With LangGraph

LangGraph remains the strongest choice when your workflow has complex conditional branching that must be fully deterministic — financial compliance pipelines, multi-step approval workflows, or any scenario where the execution graph needs to be audited after the fact. Its visual debugger in LangSmith is more mature than Strands tooling as of mid-2026.

## Real-World Use Cases and Enterprise Adoption

AWS Strands Agents has moved beyond early-adopter experimentation into enterprise production deployments. Amazon internal teams run it at scale: Amazon Q Developer uses Strands for IDE assistant workflows, AWS Glue uses it for automated ETL pipeline generation, and the VPC Reachability Analyzer uses Strands agents to diagnose complex network configurations. Outside AWS, Verisk Analytics — a Fortune 500 data analytics company serving the insurance industry — deployed a Strands-based RAG agent on Amazon Bedrock that reduced mean-time-to-resolution for data engineering incidents by 60%, entirely without manual coding pipelines. The pattern driving these results is consistent: Strands agents connect to existing data sources via MCP (replacing bespoke integrations), reason over retrieved context, and take actions through typed tools with full OTEL tracing on every step. Common enterprise patterns in production as of 2026 include DevOps agents that triage CloudWatch alarms and auto-remediate known failure modes, data engineering agents that generate and deploy Glue jobs from natural-language specs, and customer support agents that query CRM systems and escalate to humans when confidence is below threshold. The SDK's 14 million+ total downloads indicate these patterns are being replicated broadly across organizations already running on AWS infrastructure.

### Patterns Worth Reusing

The most reusable Strands pattern is the "read-reason-act" loop backed by a Session Manager: the agent reads current state (from DynamoDB, S3, or an MCP database tool), reasons about the delta between current and desired state, and calls action tools to close the gap. Session state is persisted after each loop iteration, so the agent can be interrupted and resumed across Lambda invocations without losing context.

## Frequently Asked Questions

**Q: Is AWS Strands Agents free and open source?**
Yes. Strands Agents SDK is Apache-2.0 licensed and available on GitHub at `strands-agents/sdk-python` and `strands-agents/sdk-js`. There is no cost to use the framework itself. You pay only for model inference (Bedrock, OpenAI, etc.) and any AWS infrastructure you deploy to (Lambda, Fargate, AgentCore).

**Q: Does Strands Agents require Amazon Bedrock?**
No. Bedrock is one of 9+ supported model providers, but Strands works with Anthropic, OpenAI, Gemini, Ollama, and others out of the box. You can build and run agents entirely locally using Ollama without any AWS account or credentials.

**Q: How does Strands Agents handle long-running tasks that exceed Lambda's timeout?**
Use Fargate for the agent loop (no timeout) and Lambda for individual tool executions. The recommended production architecture is API Gateway → Fargate (agent loop) → Lambda (tools), which lets you scale tool execution independently of the main loop. Alternatively, use the Session Manager to checkpoint state and continue across multiple Lambda invocations.

**Q: Can Strands Agents work with agents built on other frameworks like LangGraph or CrewAI?**
Yes, via the A2A (Agent-to-Agent) protocol introduced in Strands 1.0. Any agent exposing an A2A-compliant endpoint can be invoked as a tool by a Strands orchestrator. This enables hybrid architectures where a Strands orchestrator coordinates LangGraph sub-agents for complex deterministic sub-tasks.

**Q: What's the difference between Strands Agents and Amazon Bedrock Agents (the managed console feature)?**
Amazon Bedrock Agents is a no-code/low-code managed service configured through the AWS console. Strands Agents SDK is a code-first framework that you deploy yourself — it gives you full control over agent logic, tool definitions, and deployment targets. Strands can deploy to Bedrock AgentCore (the managed runtime), but it is a distinct product from the console-based Bedrock Agents service.
