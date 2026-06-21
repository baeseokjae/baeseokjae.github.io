---
cover:
  alt: 'AG2 (AutoGen v0.4) Guide: Event-Driven Multi-Agent Framework for Python Developers'
  image: /images/ag2-autogen-v0-4-guide-2026.png
  relative: false
date: 2026-04-19 16:31:58+00:00
description: 'Complete guide to AG2 (AutoGen v0.4): architecture, ConversableAgent,
  GroupChat, async messaging, and production best practices for Python developers.'
draft: false
schema: schema-ag2-autogen-v0-4-guide-2026
tags:
- ag2
- autogen
- multi-agent
- python
- ai-agents
- llm
title: 'AG2 (AutoGen v0.4) Guide: Event-Driven Multi-Agent Framework for Python Developers'
---

AG2 (formerly Microsoft AutoGen, now maintained by the ag2ai community) is a Python framework for building multi-agent AI systems where multiple LLM-powered agents collaborate, debate, and execute tasks autonomously. The v0.4 rewrite introduced an async-first, event-driven architecture that makes AG2 one of the most capable frameworks for complex conversational agent pipelines in 2026.

## What Is AG2 (AutoGen v0.4) and Why It Matters in 2026

AG2 is an open-source Python framework that enables developers to build networks of LLM-powered agents that communicate with each other through structured message passing to solve complex tasks collaboratively. Originally released as Microsoft AutoGen, the project transitioned to the independent ag2ai organization in November 2024 with over 54,000 GitHub stars and millions of cumulative downloads. The v0.4 release was a complete architectural redesign — not an incremental update — focused on async-first execution, improved code quality, robustness, and scalability for production workloads. In 2026, AG2 powers document review pipelines at enterprise scale, code generation workflows in CI/CD systems, and research automation for data teams. The framework supports Python 3.10 through 3.13 and integrates with OpenAI, Anthropic, Google Gemini, Alibaba DashScope, and local models via Ollama. What makes AG2 distinctive is its conversation-centric model: agents don't just call tools — they argue, critique, refine, and reach consensus through structured dialogue, which is fundamentally different from how LangGraph or CrewAI approach orchestration.

The shift from v0.2 to v0.4 wasn't just about adding features. The v0.2 API was synchronous by default and relied heavily on `initiate_chat()` as the entry point for everything. V0.4 separates concerns into three distinct layers — Core, AgentChat, and Extensions — and makes asynchronous execution the primary pattern. If you're running AutoGen in production on v0.2, migration requires meaningful refactoring. If you're starting fresh in 2026, use AG2 v0.4 from the beginning.

### Why the Community Fork Happened

Microsoft Research originally developed AutoGen as a research project. When the ag2ai community took over maintenance, it signaled a shift toward production stability over research experimentation. The AG2 team committed to semantic versioning, a stable public API, and a clear deprecation policy — things the research-focused AutoGen lacked. The GitHub community responded: the ag2ai/ag2 repo accumulated 20,000+ Discord members and 3,000+ GitHub forks within months of the transition.

## AG2 Architecture Deep Dive: Core, AgentChat, and Extensions Layers

AG2's v0.4 architecture is organized into three layers that each serve a distinct purpose, allowing developers to work at the abstraction level that fits their use case — from low-level message control to high-level team orchestration. The **Core layer** (`autogen_core`) provides the fundamental runtime: the actor model, message routing, async event loop, and subscription system. The **AgentChat layer** (`autogen_agentchat`) builds on Core with pre-built agent types — `AssistantAgent`, `UserProxyAgent`, `ConversableAgent` — and team coordination patterns like `RoundRobinGroupChat` and `SelectorGroupChat`. The **Extensions layer** (`autogen_ext`) provides integrations with external systems: vector databases, code executors, LLM clients for different providers, and tool adapters.

This layered design matters practically: if you need custom routing logic or want to implement a novel agent communication pattern, you work at the Core layer. If you're building a standard multi-agent pipeline, AgentChat has everything you need. If you're integrating with Qdrant, running code in Docker, or using Azure OpenAI, Extensions handles it. Most developers will work entirely within AgentChat with occasional dips into Extensions.

The Core layer implements the **actor model**: each agent is an independent actor with its own message inbox, local state, and processing loop. Agents don't call each other directly — they publish messages to a runtime that routes them based on topic subscriptions. This is what makes AG2's event-driven pattern different from simple function chaining. An agent can subscribe to multiple message types, emit messages that trigger other agents asynchronously, and handle failures without blocking the entire pipeline.

### Understanding the Runtime

The `SingleThreadedAgentRuntime` is the default for local development. For production distributed systems, AG2 provides distributed runtime support. The runtime manages agent lifecycle, handles message queuing, and enforces the subscription model. You register agents with the runtime, define their topic subscriptions, and then publish events — the runtime handles the rest.

```python
from autogen_core import SingleThreadedAgentRuntime

runtime = SingleThreadedAgentRuntime()
await runtime.start()
# Register agents and publish messages
await runtime.stop_when_idle()
```

## Key Concepts: ConversableAgent, AssistantAgent, and Event-Driven Messaging

AG2's agent model centers on `ConversableAgent` — the base class that every agent in the AgentChat layer inherits from — which implements the core protocol for sending, receiving, and responding to messages within a multi-agent conversation. Every agent in AG2 can initiate a conversation, respond to messages, call tools, and delegate subtasks to other agents. `AssistantAgent` extends `ConversableAgent` with LLM-backed reasoning: it takes messages, constructs prompts, calls the configured LLM, and returns structured responses. `UserProxyAgent` acts as a human-in-the-loop stand-in: it can execute code, request human input, or auto-reply based on configured rules.

The event-driven messaging model in v0.4 works differently from the synchronous `initiate_chat()` pattern in v0.2. Instead of one agent kicking off a blocking conversation, agents publish messages to typed topics. Other agents that have subscribed to those topic types receive the messages and process them in their own async loops. This enables genuinely parallel agent execution — multiple agents can process messages simultaneously without waiting for each other.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o")

planner = AssistantAgent(
    name="planner",
    model_client=model_client,
    system_message="You break complex tasks into actionable steps."
)

executor = AssistantAgent(
    name="executor",
    model_client=model_client,
    system_message="You implement the steps provided by the planner."
)
```

### Tools and Function Calling

AG2 agents call Python functions as tools through the standard function-calling API. You define tools as regular Python functions with type annotations, register them with an agent, and the agent decides when to call them based on conversation context. AG2 supports OpenAI's function calling format and automatically generates the JSON schema from Python type hints.

```python
def search_docs(query: str) -> str:
    """Search internal documentation for the given query."""
    # implementation here
    return results

agent = AssistantAgent(
    name="researcher",
    model_client=model_client,
    tools=[search_docs]
)
```

## Getting Started: Installing AG2 and Your First Multi-Agent System

Installing AG2 and running your first multi-agent conversation requires Python 3.10+ and three pip packages — `autogen-agentchat` for the high-level agent API, `autogen-ext` for LLM provider clients, and optionally `autogen-core` if you need direct runtime access. The separation into multiple packages is intentional: it keeps dependency footprints small. A project that only needs OpenAI doesn't pull in Anthropic or Gemini client libraries.

```bash
pip install autogen-agentchat autogen-ext[openai]
```

For Anthropic Claude or Google Gemini:

```bash
pip install autogen-ext[anthropic]
pip install autogen-ext[gemini]
```

For local models via Ollama:

```bash
pip install autogen-ext[ollama]
```

Here's a minimal two-agent system that solves a coding task:

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="You are a helpful Python developer. Solve the task and say TERMINATE when done."
    )
    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config={"use_docker": False}
    )
    
    termination = TextMentionTermination("TERMINATE")
    team = RoundRobinGroupChat([assistant, user_proxy], termination_condition=termination)
    
    result = await team.run(task="Write a Python function that finds all prime numbers up to N using the Sieve of Eratosthenes.")
    print(result.messages[-1].content)

asyncio.run(main())
```

### Configuring LLM Providers

AG2 uses provider-specific client classes from `autogen_ext.models`. This is different from v0.2's config list approach. You instantiate a client for your provider and pass it to agents directly:

```python
# OpenAI
from autogen_ext.models.openai import OpenAIChatCompletionClient
client = OpenAIChatCompletionClient(model="gpt-4o", api_key="sk-...")

# Anthropic
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
client = AnthropicChatCompletionClient(model="claude-sonnet-4-6")

# Ollama (local)
from autogen_ext.models.ollama import OllamaChatCompletionClient
client = OllamaChatCompletionClient(model="llama3.2")
```

## Building Real-World Pipelines: GroupChat, Swarms, and Nested Chats

AG2's power emerges in multi-agent orchestration patterns — GroupChat for turn-based collaboration, Swarms for dynamic handoffs, and nested chats for hierarchical task decomposition. These patterns let you build pipelines where agents specialize, delegate, and verify each other's work rather than relying on a single LLM to do everything. A 4-agent GroupChat with 5 rounds generates at least 20 LLM calls, so pattern selection has direct cost implications. Choosing the right orchestration pattern for your task type is one of the most important architectural decisions in an AG2 system.

**RoundRobinGroupChat** cycles through agents in fixed order — simple, predictable, good for sequential workflows where each agent has a distinct phase:

```python
from autogen_agentchat.teams import RoundRobinGroupChat

team = RoundRobinGroupChat(
    participants=[researcher, writer, reviewer],
    termination_condition=TextMentionTermination("APPROVED")
)
```

**SelectorGroupChat** uses an LLM to dynamically select the next speaker based on conversation context — better for complex workflows where the optimal next step depends on what's happened so far:

```python
from autogen_agentchat.teams import SelectorGroupChat

team = SelectorGroupChat(
    participants=[planner, coder, tester, debugger],
    model_client=model_client,
    selector_prompt="Based on the conversation, select the most appropriate next agent."
)
```

**Swarm** implements handoff-based routing: agents pass control to each other explicitly using `HandoffMessage`. This is the pattern for customer service bots, triage systems, or any workflow where each agent knows when to escalate or delegate:

```python
from autogen_agentchat.teams import Swarm
from autogen_agentchat.messages import HandoffMessage

# Agents use HandoffMessage to transfer control
# Swarm routes to the specified agent automatically
team = Swarm(participants=[triage_agent, billing_agent, support_agent])
```

### Nested Chats for Complex Decomposition

Nested chats let a parent agent kick off an entire sub-conversation as part of its own reasoning. This is powerful for research tasks where an agent needs to gather information from multiple specialized sub-agents before synthesizing a response. In v0.4, you implement nested chats by having an agent's tool call `initiate_chat()` internally, creating a new conversation context.

## AG2 vs LangGraph vs CrewAI: Choosing the Right Framework in 2026

AG2 excels at multi-party conversational workflows, consensus-building, and scenarios where agents need to debate or critique each other — LangGraph is better for deterministic state machines with complex branching logic, and CrewAI is better for simple role-based pipelines where ease of setup matters more than flexibility. This is the practical decision guide based on actual production use patterns in 2026. All three frameworks are mature enough for production, but they optimize for fundamentally different problem shapes. The wrong choice means fighting the framework; the right choice means the framework amplifies your design.

| Criteria | AG2 | LangGraph | CrewAI |
|---|---|---|---|
| **Primary pattern** | Conversational agents | State machine graphs | Role-based crews |
| **Learning curve** | Medium | High | Low |
| **Async support** | Native (v0.4) | Yes | Limited |
| **Human-in-loop** | Built-in | Manual | Basic |
| **Debugging** | Conversation logs | Graph visualization | Simple logs |
| **Best for** | Group debates, consensus | Complex branching workflows | Simple automation |
| **Python skill needed** | Intermediate | Advanced | Beginner-friendly |
| **Cost per run** | High (many LLM calls) | Controllable | Medium |

**Choose AG2 when:**
- Your task benefits from agents critiquing each other's work (code review, document editing, research validation)
- You need flexible conversation routing that depends on semantic content
- You're building customer service, tutoring, or debate-style applications
- You want native async with multi-provider LLM support

**Choose LangGraph when:**
- Your workflow has predictable branches with clear state transitions
- You need fine-grained control over every execution step
- You're building workflows where correctness is more important than flexibility
- Your team has strong Python and graph-theory background

**Choose CrewAI when:**
- You need to ship fast and the workflow is straightforward
- Non-engineers are defining the agent roles and tasks
- The task doesn't require complex inter-agent negotiation

### Migration from AutoGen v0.2 to AG2 v0.4

The v0.2 to v0.4 migration involves breaking changes at every level. Key changes:

1. **Import paths changed**: `from autogen import AssistantAgent` → `from autogen_agentchat.agents import AssistantAgent`
2. **Config list removed**: Replace `llm_config={"config_list": [...]}` with provider-specific client objects
3. **`initiate_chat()` deprecated**: Use team-based APIs with `await team.run(task=...)`
4. **Synchronous code won't work**: Everything is async — wrap with `asyncio.run()` or use `asyncio.get_event_loop()`

## Production Best Practices: Cost Control, State Management, and Observability

Running AG2 in production requires explicit strategies for controlling LLM costs, persisting conversation state across sessions, and observing agent behavior — because the default configuration optimizes for flexibility, not cost or reliability. A 4-agent GroupChat with 5 rounds generates at least 20 LLM calls, each sending the full conversation history as context. Without cost controls, a single complex task can consume $5–$20 in API calls. With the right patterns, you can cut that by 60–80% while maintaining output quality.

**Cost Control Strategies:**

1. **Use cheaper models for simple agents**: Route tool-calling agents to `gpt-4o-mini` or `claude-haiku-4-5` and reserve expensive models for reasoning-heavy agents

2. **Set max_turns explicitly**: Always cap GroupChat rounds:
   ```python
   team = RoundRobinGroupChat(participants=[...], max_turns=5)
   ```

3. **Cache LLM responses**: For deterministic subtasks (document classification, entity extraction), cache results to avoid redundant LLM calls

4. **Use selective context**: AG2 v0.4 supports message filtering — don't send the entire conversation history to every agent for every turn

**State Persistence:**

AG2 v0.4 introduces `save_state()` and `load_state()` on team objects, enabling conversation checkpointing:

```python
# Save after completion
state = await team.save_state()
with open("checkpoint.json", "w") as f:
    json.dump(state, f)

# Resume from checkpoint
new_team = RoundRobinGroupChat(participants=[...])
with open("checkpoint.json") as f:
    await new_team.load_state(json.load(f))
result = await new_team.run(task="Continue from where we left off")
```

**Observability:**

AG2 integrates with OpenTelemetry for distributed tracing. Each LLM call, tool invocation, and agent message is a traceable span. For production systems, connect to Jaeger, Datadog, or Honeycomb:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
# AG2 automatically instruments LLM calls and agent messages
```

### Error Handling and Retries

AG2 agents can fail silently if LLM calls time out or return malformed responses. Implement explicit retry logic at the team level and validate agent outputs before passing them downstream. The `on_messages_stream()` method lets you inspect messages in real-time and terminate early if an agent enters a failure loop.

## AG2 Beta and the Road to v1.0: What Python Developers Need to Know

AG2 Beta (`autogen.beta`) previews the v1.0 architecture, which introduces streaming-first agent responses, improved memory systems, and a unified tool registry that works across all agent types — changes that will affect how you build production systems starting in late 2026. The Beta track is importable today as `from autogen.beta import ...` alongside the stable v0.4 API. The ag2ai team has committed to not breaking stable v0.4 APIs before a 6-month deprecation window, but Beta APIs can change without notice. The most significant v1.0 changes for Python developers are:

**Streaming responses**: V1.0 makes streaming the default for all LLM calls, enabling real-time output for user-facing applications. In v0.4, streaming requires explicit configuration per agent. In v1.0, it's automatic with a unified `on_token()` callback.

**Memory architecture**: V1.0 introduces pluggable memory backends. Agents can store and retrieve context from vector databases (Qdrant, Pinecone, Chroma) without custom tool implementations. This replaces the manual retrieval patterns required in v0.4.

**Unified tool registry**: In v0.4, each agent has its own tool list. V1.0 introduces a shared registry where tools can be discovered and used by any agent in the system, reducing code duplication in large multi-agent pipelines.

**What to do now**: Build on stable v0.4 APIs for production systems. Experiment with `autogen.beta` in development to prepare for migration. Watch the ag2ai/ag2 GitHub releases for the v1.0 roadmap — the community is active and the release cadence is roughly quarterly.

---

## FAQ

**Q: Is AG2 the same as AutoGen?**
AG2 is the community continuation of Microsoft AutoGen. After the ag2ai organization took over in November 2024, they published the package as `ag2` on PyPI while maintaining the `autogen` namespace for backward compatibility. The codebase is the same project, now with community governance instead of Microsoft Research ownership.

**Q: Can I use AG2 with local LLMs?**
Yes. AG2 v0.4 supports Ollama via `autogen_ext.models.ollama.OllamaChatCompletionClient`. Install `pip install autogen-ext[ollama]`, start Ollama locally with `ollama serve`, and configure an `OllamaChatCompletionClient` pointing to `http://localhost:11434`. This enables fully offline multi-agent systems with models like Llama 3.2 or Mistral.

**Q: How does AG2 v0.4 differ from v0.2 in practice?**
V0.4 requires async code everywhere — you can't run `initiate_chat()` synchronously. The import paths changed (now `autogen_agentchat`, `autogen_core`, `autogen_ext` instead of just `autogen`). LLM configuration moved from config lists to provider-specific client objects. Team-based APIs replaced the direct `initiate_chat()` pattern. Plan for a meaningful refactoring effort when migrating from v0.2.

**Q: How much does running AG2 cost in production?**
Cost depends heavily on model choice and GroupChat configuration. A 4-agent GroupChat with 5 rounds generates at least 20 LLM calls. Using `gpt-4o-mini` ($0.15/1M input tokens) instead of `gpt-4o` ($2.50/1M input tokens) can reduce costs by 94% for agents that don't require advanced reasoning. Budget for 50–200 tokens of conversation history per message multiplied by the number of agents and rounds.

**Q: Is AG2 ready for production in 2026?**
Yes, with caveats. The stable v0.4 API is production-ready. The ag2ai community has implemented semantic versioning, a deprecation policy, and a stable public API contract. Large-scale enterprise deployment requires custom work for state persistence, observability, and cost management — AG2 provides the building blocks but doesn't solve these problems out of the box. For most teams building internal tools, automation pipelines, or customer-facing agents, v0.4 is stable enough to ship.