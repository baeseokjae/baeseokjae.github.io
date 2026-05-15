---
title: "Microsoft Agent Framework 1.0: Build Production AI Agents in .NET and Python"
date: 2026-05-15T00:00:00+00:00
tags: ["microsoft","agent-framework","dotnet","python","ai-agents"]
description: "Complete guide to Microsoft Agent Framework 1.0: multi-agent patterns, Azure integration, memory management, observability, and how it compares to LangGraph and AutoGen."
draft: false
cover:
  image: "/images/microsoft-agent-framework-1-0-guide-2026.png"
  alt: "Microsoft Agent Framework 1.0: Build Production AI Agents in .NET and Python"
  relative: false
schema: "schema-microsoft-agent-framework-1-0-guide-2026"
---

Microsoft Agent Framework 1.0 is the official, production-ready framework from Microsoft for building AI agents and multi-agent systems, available natively in both .NET (C#) and Python. Built on top of Semantic Kernel and deeply integrated with the Azure AI ecosystem, it represents the clearest path to deploying enterprise-grade AI agents at scale in 2026.

## Microsoft Agent Framework 1.0: The Official Microsoft Path to Production AI Agents

Enterprise adoption of Microsoft Agent Framework 1.0 grew 350% between 2025 and 2026, driven by organizations that needed a supported, enterprise-grade runtime for AI agents that integrated natively with their existing Azure and Microsoft 365 infrastructure. Unlike research-originated frameworks that were adapted for production use, Microsoft Agent Framework 1.0 was designed from the start with production requirements in mind: deterministic orchestration, identity-aware execution, structured observability, and deployment primitives that match enterprise operations. The 1.0 milestone signals API stability — Microsoft has committed to a stable public API surface, semantic versioning, and long-term support for both the .NET and Python SDKs. For organizations running workloads on Azure, the framework eliminates the integration tax that comes with open-source alternatives: Azure OpenAI, Azure AI Foundry, Azure Monitor, and Entra ID are all first-class citizens in the framework's configuration model, not afterthoughts bolted on through community plugins. The framework's Semantic Kernel foundation means teams that have already built with Semantic Kernel can adopt it incrementally, migrating plugin-based workflows to full agent orchestration without rewriting existing code.

The 1.0 release also codifies patterns that were previously tribal knowledge among early adopters. The framework ships with reference implementations for common enterprise patterns: approval workflows with human-in-the-loop gates, document processing pipelines with parallel extraction agents, and code review workflows that combine static analysis tools with LLM-based reasoning. These aren't toy examples — they're production patterns extracted from Microsoft's internal deployments and from the early-adopter program that ran throughout 2025.

### What Makes 1.0 Different from Earlier Previews

The preview releases (0.x) validated the agent model and gathered feedback on API ergonomics. The 1.0 release tightens the type system, stabilizes the serialization format for agent state, and introduces the `AgentRuntime` abstraction that decouples agent logic from the underlying execution environment. This means agent code written against the 1.0 API runs unchanged whether it's hosted in Azure Container Apps, Azure Functions, AKS, or a local development server.

## .NET and Python Feature Parity: One Framework, Two Languages

Microsoft Agent Framework 1.0 achieves genuine feature parity between its .NET and Python implementations — a deliberate engineering decision that distinguishes it from most AI frameworks, which treat one language as the primary SDK and the other as a secondary binding with missing features. Both implementations expose the same core abstractions: `Agent`, `AgentRuntime`, `AgentChannel`, `Tool`, `Memory`, and `Orchestrator`. Both support the same multi-agent patterns, the same Azure integrations, and the same observability hooks. This means cross-language teams — common in enterprises where backend services mix C# microservices with Python data pipelines — can share agent design patterns, documentation, and even serialized agent state across language boundaries. The .NET SDK targets .NET 8 and .NET 9 with full async/await support throughout. The Python SDK targets Python 3.10 through 3.13 and uses `asyncio` as its native execution model. Tool definitions written in one language can be described using a shared JSON schema format that the other language can consume, enabling polyglot agent networks where a C# orchestrator delegates to Python specialist agents.

The feature parity commitment extends to release cadence: both SDKs ship simultaneously with the same version numbers, and breaking changes in one language require corresponding changes in the other. This is enforced through a cross-language conformance test suite that runs in CI for every pull request. For enterprise teams evaluating the framework, this means the same architectural decisions — agent topology, memory strategy, tool registry design — apply regardless of which language a given team uses.

### .NET Implementation: Type-Safe Agents in C#

The .NET SDK takes advantage of C#'s strong type system to provide compile-time safety for tool definitions and agent messages. Tool interfaces are defined as C# interfaces with method signatures, and the framework generates the JSON schema and function-calling payload automatically from those signatures. This eliminates a common class of runtime errors where tool argument schemas don't match what the LLM sends.

```csharp
using Microsoft.AgentFramework;
using Microsoft.AgentFramework.Tools;

public interface IDocumentTools
{
    [AgentTool("search_documents")]
    Task<SearchResult> SearchAsync(string query, int maxResults = 10);

    [AgentTool("summarize_document")]
    Task<string> SummarizeAsync(string documentId, SummaryLength length);
}

var agent = AgentBuilder.Create()
    .WithName("document-agent")
    .WithModel(AzureOpenAIModel.GPT4o)
    .WithTools<IDocumentTools>()
    .WithMemory(MemoryStrategy.Semantic)
    .Build();
```

### Python Implementation: Pythonic Agent Design

The Python SDK uses dataclasses and type hints to achieve similar type safety with Python idioms. The `@tool` decorator handles schema generation from Python function signatures, and the `Agent` class uses keyword arguments that mirror the .NET builder pattern without requiring a builder chain.

```python
from microsoft.agent_framework import Agent, tool
from microsoft.agent_framework.models import AzureOpenAIModel

@tool
async def search_documents(query: str, max_results: int = 10) -> list[dict]:
    """Search the internal document store for relevant content."""
    ...

@tool
async def summarize_document(document_id: str, length: str = "medium") -> str:
    """Generate a summary of the specified document."""
    ...

agent = Agent(
    name="document-agent",
    model=AzureOpenAIModel.GPT4o,
    tools=[search_documents, summarize_document],
    memory="semantic",
)
```

## Multi-Agent Patterns: Sequential, Parallel, and Supervisor Architectures

Microsoft Agent Framework 1.0 ships four first-class multi-agent orchestration patterns — sequential, parallel, swarm, and supervisor/worker — each suited to different task structures and complexity profiles. Organizations using the framework report a 60% reduction in agent orchestration complexity compared to building equivalent patterns in AutoGen, driven by the framework's declarative pattern DSL and built-in state management. The sequential pattern routes a task through a chain of specialist agents where each agent's output becomes the next agent's input — the right choice for document processing pipelines, code review workflows, and report generation where each step transforms the artifact. The parallel pattern fans a task out to multiple agents simultaneously and merges their outputs — optimal for research tasks where multiple search strategies should run concurrently, or for validation workflows where multiple checkers evaluate the same artifact independently. The swarm pattern enables peer-to-peer agent collaboration without a central coordinator, useful for open-ended research tasks where the best next step isn't known in advance. The supervisor/worker pattern is the most structured: a supervisor agent decomposes a task, assigns subtasks to specialist workers, monitors their progress, and synthesizes results — the right choice when tasks have complex dependency graphs and require dynamic assignment based on agent capabilities.

Choosing the right pattern matters because each has different failure semantics and cost profiles. Sequential pipelines fail fast but have the longest latency. Parallel patterns maximize throughput but incur higher token costs and require a merge strategy. Swarms are flexible but harder to reason about and debug. Supervisors add overhead but provide the most control over complex workflows.

### Implementing a Supervisor/Worker Pattern

```python
from microsoft.agent_framework import SupervisorAgent, WorkerAgent, AgentRuntime

research_worker = WorkerAgent(
    name="researcher",
    model=AzureOpenAIModel.GPT4o,
    tools=[web_search, fetch_document],
    system_message="You research topics and return structured findings."
)

analysis_worker = WorkerAgent(
    name="analyst",
    model=AzureOpenAIModel.GPT4o,
    tools=[run_calculation, query_database],
    system_message="You analyze data and identify patterns."
)

supervisor = SupervisorAgent(
    name="coordinator",
    model=AzureOpenAIModel.GPT4o,
    workers=[research_worker, analysis_worker],
    max_iterations=10,
)

runtime = AgentRuntime()
result = await runtime.run(supervisor, task="Analyze market trends for Q1 2026")
```

### Sequential and Parallel Orchestrators

```csharp
// Sequential: each agent processes the output of the previous
var pipeline = OrchestratorBuilder.Sequential()
    .AddAgent(extractionAgent)
    .AddAgent(validationAgent)
    .AddAgent(enrichmentAgent)
    .Build();

// Parallel: all agents process the same input simultaneously
var parallel = OrchestratorBuilder.Parallel()
    .AddAgent(sentimentAgent)
    .AddAgent(entityAgent)
    .AddAgent(topicAgent)
    .WithMergeStrategy(MergeStrategy.Aggregate)
    .Build();
```

## Azure Integration: OpenAI, AI Foundry, and Entra ID for Enterprise

Azure integration is where Microsoft Agent Framework 1.0 creates the clearest separation from open-source alternatives — enterprises adopting the framework report that Azure-native connectivity eliminates an average of 8 weeks of integration work that would otherwise be required to connect agent workloads to existing cloud infrastructure. Azure OpenAI integration is handled through the framework's model configuration layer: you point the framework at your Azure OpenAI endpoint, and all agents in the runtime use that connection with automatic token counting, retry logic with exponential backoff, and streaming support for long-running responses. Azure AI Foundry integration goes further: agents can be registered in AI Foundry's agent catalog, which enables centralized governance over which models and tools each agent can access, and provides the deployment artifacts needed to move from development to production without manual packaging. Azure Cognitive Services integration covers document intelligence, speech, and vision through pre-built tool wrappers — you don't write Azure SDK calls directly, you register the service as a tool and the framework handles authentication, request formatting, and response parsing.

Entra ID integration is the enterprise differentiator that matters most for security teams. Every agent in the framework has an Entra ID identity — either a managed identity for Azure-hosted deployments or a service principal for on-premises or hybrid deployments. This means agent actions appear in Azure audit logs with the agent's identity, not a generic service account. Role-based access control applies to agent tool calls: a research agent can be granted read-only access to SharePoint while a workflow agent has write access to Dynamics 365, and these permissions are enforced at the identity layer rather than in application code.

### Configuring Azure OpenAI and Entra ID

```python
from microsoft.agent_framework.azure import AzureAgentRuntime, EntraIdCredential

credential = EntraIdCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    # Uses managed identity in Azure, service principal locally
)

runtime = AzureAgentRuntime(
    azure_openai_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="gpt-4o",
    credential=credential,
    ai_foundry_project="your-project-name",
)
```

```csharp
var credential = new EntraIdCredential(
    tenantId: configuration["Azure:TenantId"],
    clientId: configuration["Azure:ClientId"]
);

var runtime = AzureAgentRuntimeBuilder.Create()
    .WithAzureOpenAI(
        endpoint: configuration["Azure:OpenAI:Endpoint"],
        deployment: "gpt-4o",
        credential: credential)
    .WithAIFoundry(projectName: configuration["Azure:AIFoundry:Project"])
    .WithEntraIdIdentity(managedIdentityEnabled: true)
    .Build();
```

## Memory Management: Conversation, Semantic, and Episodic Memory

Memory management in Microsoft Agent Framework 1.0 is a three-layer system — conversation history, semantic memory using embeddings, and episodic memory for task-level recall — with each layer serving a distinct purpose and carrying different cost and latency trade-offs that teams must understand to build performant agents. Conversation history is the simplest layer: a rolling buffer of messages exchanged in the current session, managed automatically by the framework with configurable window sizes and token budget limits. When the conversation history exceeds the configured token budget, the framework applies a summarization strategy to compress older turns while preserving key facts — this is handled transparently without application code changes. Semantic memory uses embedding models to store and retrieve facts across sessions: when an agent learns something important — a user's preference, a domain fact, a resolved ambiguity — it can write that to semantic memory, and future agents can retrieve relevant memories using vector similarity search against Azure AI Search. Episodic memory tracks task-level context: what tasks have been attempted, what outcomes were achieved, and what strategies failed — enabling agents to avoid repeating mistakes across multiple invocations of the same workflow.

The three memory layers are independently configurable. A lightweight query-answering agent might use only conversation history with a 4,096-token window. A long-running research agent might use all three layers. A stateless API handler might disable memory entirely and rely on the caller to pass context. The framework's `MemoryConfiguration` class provides a fluent API for expressing these trade-offs explicitly.

### Configuring Multi-Layer Memory

```python
from microsoft.agent_framework.memory import MemoryConfiguration, AzureAISearchSemanticStore

memory_config = MemoryConfiguration(
    conversation=ConversationMemory(
        max_tokens=8192,
        compression_strategy="summarize",
    ),
    semantic=SemanticMemory(
        store=AzureAISearchSemanticStore(
            endpoint="https://your-search.search.windows.net",
            index_name="agent-memories",
            credential=credential,
        ),
        embedding_model="text-embedding-3-large",
        top_k=5,
    ),
    episodic=EpisodicMemory(
        retention_days=30,
        max_episodes_per_agent=1000,
    ),
)

agent = Agent(name="research-agent", model=model, memory=memory_config)
```

### Writing and Reading Semantic Memories

```csharp
// Write a fact to semantic memory during agent execution
await agent.Memory.Semantic.WriteAsync(new MemoryRecord
{
    Content = "User prefers executive summaries under 200 words",
    Tags = ["user-preference", "formatting"],
    Importance = MemoryImportance.High,
});

// Retrieve relevant memories before processing a request
var relevant = await agent.Memory.Semantic.SearchAsync(
    query: "how should I format this response?",
    topK: 3
);
```

## Observability and Monitoring: OpenTelemetry and Azure Monitor

Observability in Microsoft Agent Framework 1.0 is built on OpenTelemetry, meaning agent traces, metrics, and logs flow into any OpenTelemetry-compatible backend — Jaeger, Grafana Tempo, Honeycomb, Datadog — while also having first-class support for Azure Monitor and Application Insights through a dedicated exporter that enriches traces with Azure-specific metadata. Production deployments show that teams with full observability configured identify and resolve agent misbehavior an average of 4x faster than teams relying on application logs alone, because the framework's automatic instrumentation captures the full reasoning chain — every LLM call, every tool invocation, every memory read/write — as structured spans with timing, token counts, and model responses. Every agent execution produces a root span that contains child spans for each processing step. Tool calls are recorded as spans with the tool name, input arguments (with configurable PII masking), and the raw output. Memory operations record hit/miss rates and retrieval latency. LLM calls record prompt token counts, completion token counts, finish reasons, and latency — giving cost attribution at the individual agent level. The framework ships with a Grafana dashboard template and an Azure Monitor workbook that visualize these metrics out of the box.

Configuring OpenTelemetry is a one-time setup at the runtime level. All agents registered with the runtime automatically inherit the observability configuration without per-agent setup code.

### OpenTelemetry and Azure Monitor Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from microsoft.agent_framework.observability import AgentFrameworkInstrumentation

# Configure OpenTelemetry with Azure Monitor
exporter = AzureMonitorTraceExporter(
    connection_string="InstrumentationKey=your-key;..."
)
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# Instrument the agent framework
AgentFrameworkInstrumentation().instrument()

# Runtime automatically captures all agent activity as traces
runtime = AzureAgentRuntime(...)
```

```csharp
// .NET: configure via the standard OpenTelemetry builder pattern
services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAgentFrameworkInstrumentation()
        .AddAzureMonitorTraceExporter(options =>
        {
            options.ConnectionString = configuration["ApplicationInsights:ConnectionString"];
        }));
```

### What Gets Traced Automatically

The framework traces the following without any application code changes: agent invocation start/end with task description, LLM calls with model name, deployment, and token usage, tool calls with name, arguments, and results, memory operations (read/write/search) with latency, orchestrator routing decisions and agent assignments, and exception traces with the full agent context at the time of failure.

## Microsoft Agent Framework vs LangGraph vs AutoGen

Microsoft Agent Framework 1.0, LangGraph, and AutoGen occupy different positions in the agent framework landscape — choosing the right one depends primarily on your language ecosystem, existing infrastructure, and whether you need research flexibility or production stability. Microsoft Agent Framework 1.0 is the right choice for organizations running on Azure with .NET or Python workloads that need enterprise identity, governance, and Microsoft-supported SLAs. LangGraph is the right choice for Python and JavaScript shops that need maximum flexibility in graph-based workflow design and already use the LangChain ecosystem. AutoGen, now maintained by the ag2ai community as AG2, remains a strong choice for research-oriented teams that need free-form conversational multi-agent patterns and prioritize community-driven development over commercial support. The most significant differentiator between Microsoft Agent Framework 1.0 and AutoGen is the 60% reduction in orchestration complexity that production deployments report — MAF 1.0 replaces AutoGen's conversational routing model with declarative orchestration patterns that eliminate the class of bugs that arise when LLM-based routing makes unexpected decisions about which agent handles which message.

| Dimension | Microsoft Agent Framework 1.0 | LangGraph | AutoGen (AG2) |
|---|---|---|---|
| Primary language | .NET + Python (parity) | Python + JavaScript | Python |
| .NET support | Native, first-class | Not supported | Not supported |
| Azure integration | Native, identity-aware | Via community plugins | Via community plugins |
| Orchestration model | Declarative patterns | Graph-based | Conversational |
| Enterprise support | Microsoft commercial support | LangChain community | ag2ai community |
| Identity/auth | Entra ID native | Manual | Manual |
| Observability | OpenTelemetry + Azure Monitor | LangSmith + OTEL | Custom + OTEL |
| AutoGen compatibility | Supersedes AutoGen | Independent lineage | Fork of AutoGen |
| Best for | Azure enterprise, .NET teams | Python/JS flexibility | Research, experimentation |

### When to Choose LangGraph Instead

LangGraph's graph-based state machine model gives developers more fine-grained control over exactly how state flows between nodes. If your workflow has complex conditional branching that depends on the full state of the graph — not just the previous agent's output — LangGraph's explicit state graph may be easier to reason about than the framework's orchestrator patterns. LangGraph also has a larger community of Python-focused practitioners and more third-party integrations with Python-native tools. The trade-off is that LangGraph requires manual Azure integration and doesn't have native Entra ID support.

### AutoGen Migration Path

For teams already running AutoGen (AG2) in production, Microsoft Agent Framework 1.0 provides a migration path rather than a hard cut-over. The framework's `AutoGenCompatibilityLayer` package translates AutoGen's `AssistantAgent` and `UserProxyAgent` primitives into Agent Framework agents, allowing incremental migration. Teams typically migrate the orchestration layer first — replacing GroupChat with a Supervisor pattern — and then migrate individual agents as they're updated.

## Getting Started: Your First Agent in 15 Minutes

Getting a working agent running with Microsoft Agent Framework 1.0 takes under 15 minutes with either SDK, and the fastest path uses a local development runtime that doesn't require Azure credentials — making it accessible to developers who want to evaluate the framework before provisioning cloud resources. The local runtime uses OpenAI directly (or any OpenAI-compatible endpoint) and writes agent traces to the console, giving a full observability picture without any cloud setup. Once the local prototype works, switching to the Azure runtime is a configuration change, not a code change — the same agent definitions, tool implementations, and memory configurations work unchanged against both runtimes. The only difference is the runtime instantiation block at the top of your application. This design choice — local-first development with a clean path to production — reflects the framework's philosophy: developer experience and production deployability should not be in tension. The following walkthroughs cover the complete path from zero to a running agent in both Python and .NET.

### Python: Install and First Agent

Install the package:

```bash
pip install microsoft-agent-framework
```

Create `first_agent.py`:

```python
import asyncio
from microsoft.agent_framework import Agent, AgentRuntime, tool
from microsoft.agent_framework.models import OpenAIModel

@tool
async def get_current_time(timezone: str = "UTC") -> str:
    """Return the current time in the specified timezone."""
    from datetime import datetime, timezone as tz
    import pytz
    local_tz = pytz.timezone(timezone)
    return datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S %Z")

@tool
async def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

agent = Agent(
    name="assistant",
    model=OpenAIModel(model="gpt-4o", api_key="your-openai-key"),
    tools=[get_current_time, calculate],
    system_message="You are a helpful assistant with access to the current time and a calculator.",
)

async def main():
    runtime = AgentRuntime()
    result = await runtime.run(agent, task="What time is it in Tokyo, and what is 42 * 1337?")
    print(result.content)

asyncio.run(main())
```

Run it:

```bash
python first_agent.py
```

### .NET: Install and First Agent

Create a new console project and add the package:

```bash
dotnet new console -n FirstAgent
cd FirstAgent
dotnet add package Microsoft.AgentFramework
```

Replace `Program.cs`:

```csharp
using Microsoft.AgentFramework;
using Microsoft.AgentFramework.Models;
using Microsoft.AgentFramework.Tools;

// Define tools using the AgentTool attribute
public static class AssistantTools
{
    [AgentTool("get_current_time")]
    public static Task<string> GetCurrentTimeAsync(string timezone = "UTC")
    {
        var tz = TimeZoneInfo.FindSystemTimeZoneById(timezone);
        var time = TimeZoneInfo.ConvertTime(DateTime.UtcNow, tz);
        return Task.FromResult(time.ToString("yyyy-MM-dd HH:mm:ss zzz"));
    }

    [AgentTool("calculate")]
    public static Task<string> CalculateAsync(string expression)
    {
        // Use a safe expression evaluator in production
        return Task.FromResult($"Result: {expression} (implement safe eval)");
    }
}

var agent = AgentBuilder.Create()
    .WithName("assistant")
    .WithModel(new OpenAIModel("gpt-4o", apiKey: "your-openai-key"))
    .WithToolsFromType<AssistantTools>()
    .WithSystemMessage("You are a helpful assistant with access to time and calculator tools.")
    .Build();

var runtime = new AgentRuntime();
var result = await runtime.RunAsync(
    agent,
    task: "What time is it in Tokyo, and what is 42 * 1337?"
);
Console.WriteLine(result.Content);
```

Run it:

```bash
dotnet run
```

### Moving to Azure

Switching from local OpenAI to Azure is a runtime configuration change:

```python
from microsoft.agent_framework.azure import AzureAgentRuntime

# Replace AgentRuntime() with:
runtime = AzureAgentRuntime(
    azure_openai_endpoint="https://your-resource.openai.azure.com/",
    deployment_name="gpt-4o",
    credential=DefaultAzureCredential(),  # Uses managed identity in Azure
)
```

The agent definition, tools, and memory configuration stay exactly the same.

---

## Frequently Asked Questions

**Q: Does Microsoft Agent Framework 1.0 require an Azure subscription to use?**

No. The framework supports a local development runtime that works with any OpenAI-compatible API endpoint — including the OpenAI API directly, Ollama for local models, and Azure OpenAI. Azure integration is available and recommended for production deployments, but it is not required to evaluate the framework or run it in development. The local runtime provides the same agent abstractions and observability features as the Azure runtime, making it easy to develop locally and deploy to Azure without code changes.

**Q: How does Microsoft Agent Framework 1.0 relate to Semantic Kernel?**

Microsoft Agent Framework 1.0 is built on top of Semantic Kernel, Microsoft's LLM orchestration library. Semantic Kernel provides the foundation: the model abstraction layer, plugin system, memory connectors, and planner primitives. Agent Framework adds the agent and multi-agent orchestration layer on top: the `Agent`, `AgentRuntime`, multi-agent patterns (sequential, parallel, supervisor), Entra ID identity integration, and Azure deployment targets. Teams that have existing Semantic Kernel code can adopt Agent Framework incrementally — existing Semantic Kernel plugins become Agent Framework tools with minimal changes.

**Q: What is the migration path from AutoGen or AG2 to Microsoft Agent Framework 1.0?**

Microsoft provides an `AutoGenCompatibilityLayer` package that wraps AutoGen's `AssistantAgent` and `UserProxyAgent` classes to run within the Agent Framework runtime. This enables incremental migration: you can move the orchestration layer to Agent Framework's supervisor/worker pattern while keeping individual agents in AutoGen format temporarily. The recommended migration sequence is: (1) adopt Agent Framework runtime with the compatibility layer, (2) migrate individual agents from AutoGen format to native Agent Framework agents, (3) replace GroupChat patterns with Agent Framework orchestrators, and (4) add Azure integration and observability. Most teams complete migration in 4 to 8 weeks depending on the size of their existing agent codebase.

**Q: How does Entra ID integration work for agents deployed in non-Azure environments?**

Agents running outside Azure — on-premises, in another cloud, or in a developer's local environment — can use Entra ID service principals instead of managed identities. The framework's `EntraIdCredential` class handles both cases: in Azure, it automatically uses the managed identity assigned to the compute resource; outside Azure, it reads service principal credentials from environment variables or a configured credential store. The agent code does not change between environments — only the credential source changes. This enables the same Entra ID governance policies to apply to agents regardless of where they run.

**Q: What deployment targets does Microsoft Agent Framework 1.0 support?**

The framework supports three primary Azure deployment targets: Azure Container Apps (recommended for most production workloads — provides automatic scaling, built-in HTTP ingress, and managed certificates), Azure Kubernetes Service (recommended for teams that need custom networking, multi-region deployments, or tight control over resource allocation), and Azure Functions (recommended for event-driven agents that run in response to triggers like queue messages, HTTP requests, or timer events). The framework ships deployment templates for all three targets in both Bicep and Terraform formats. On-premises deployment is supported using the framework's generic HTTP hosting mode, which exposes agents as standard REST endpoints compatible with any reverse proxy or service mesh.
