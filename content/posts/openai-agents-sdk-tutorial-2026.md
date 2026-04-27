---
title: "OpenAI Agents SDK Tutorial 2026: Build Multi-Agent Pipelines in Python"
date: 2026-04-27T15:02:17+00:00
tags: ["openai", "agents", "python", "multi-agent", "ai-agents", "tutorial"]
description: "Step-by-step guide to building production multi-agent pipelines with OpenAI Agents SDK 0.13.4 — handoffs, guardrails, tracing, and cost optimization."
draft: false
cover:
  image: "/images/openai-agents-sdk-tutorial-2026.png"
  alt: "OpenAI Agents SDK Tutorial 2026: Build Multi-Agent Pipelines in Python"
  relative: false
schema: "schema-openai-agents-sdk-tutorial-2026"
---

The OpenAI Agents SDK lets you build production-grade multi-agent pipelines in Python with fewer than 100 lines of core logic. Install it with `pip install openai-agents`, define agents with instructions and tools, connect them via handoffs or an orchestrator, and run with `asyncio`. This tutorial walks through a complete three-agent pipeline from setup to deployment.

## What Is the OpenAI Agents SDK and Why Does It Matter in 2026?

The OpenAI Agents SDK is an open-source Python framework that provides four production-grade primitives — Agents, Handoffs, Guardrails, and Tracing — for building multi-step AI workflows without the boilerplate overhead of earlier frameworks. Released in early 2026 and reaching version 0.13.4 in April with full MCP server support, the SDK emerged as a response to a clear market need: 57% of organizations now deploy agents for multi-stage workflows, yet most teams were still stitching together ad-hoc pipelines using raw LLM calls and custom orchestration code. The SDK abstracts that complexity into composable primitives where each Agent is a configuration object wrapping an LLM with instructions, tool access, and optional output schemas. Handoffs allow agents to delegate work to peers; Guardrails validate inputs and outputs; Tracing captures every decision step for debugging and observability. The SDK is also model-agnostic — it supports any provider conforming to the chat completions API format, and integrates with 100+ LLMs via LiteLLM. For teams evaluating agentic frameworks in 2026, the SDK's minimal surface area and tight OpenAI integration make it the fastest path from prototype to production.

### How Does It Compare to LangGraph and CrewAI?

The OpenAI Agents SDK occupies the lower-abstraction end of the framework spectrum. LangGraph models workflows as directed graphs with explicit node transitions, giving maximum control for complex branching logic at the cost of more configuration. CrewAI uses a role-based crew metaphor suited to collaborative, loosely structured tasks. The OpenAI Agents SDK sits in the middle — simpler than LangGraph for linear pipelines, more structured than CrewAI for typed data flows. Use the SDK when you have clear handoff boundaries, need Pydantic-typed structured outputs between agents, and want built-in tracing without a separate observability stack.

## How to Set Up the OpenAI Agents SDK Development Environment

Setting up the OpenAI Agents SDK takes under five minutes on any machine running Python 3.10 or later. The SDK ships as a single PyPI package (`openai-agents`) with no mandatory external dependencies beyond the OpenAI Python client. Start by creating a virtual environment, installing the package, and exporting your OpenAI API key. Version 0.13.4 is the current stable release as of April 2026 and is the recommended target — earlier versions lack MCP server support and have known tracing bugs on Python 3.12. For development, also install `pydantic>=2.0` (bundled as a dependency but worth pinning explicitly) and `python-dotenv` for secret management. A minimal project structure separates agents, tools, guardrails, and runner logic into distinct modules, making it easier to swap components independently as the pipeline grows. All async execution runs on the standard `asyncio` event loop — no additional runtime is needed.

```bash
# Create and activate virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install SDK and development dependencies
pip install openai-agents>=0.13.4 python-dotenv pydantic>=2.0

# Set your API key
export OPENAI_API_KEY="sk-..."
```

Recommended project layout:

```
my_pipeline/
├── agents/
│   ├── researcher.py
│   ├── writer.py
│   └── reviewer.py
├── tools/
│   └── web_search.py
├── guardrails/
│   ├── input_guard.py
│   └── output_guard.py
├── models.py          # Pydantic output schemas
└── main.py            # Runner / entry point
```

## How to Build Your First Agent with Instructions and Tools

An Agent in the OpenAI Agents SDK is created by instantiating the `Agent` class with at minimum a `name`, `instructions`, and `model`. Instructions replace the system prompt — write them as a concise role definition describing what the agent does, what it must not do, and what format it should return. Tools are Python functions decorated with `@function_tool` and attached via the `tools` list. Structured outputs are enforced by passing a Pydantic model to `output_type`, which causes the SDK to use JSON mode under the hood and validate the response before returning it to your code. The agent does not execute itself; you run it via `Runner.run()` (async) or `Runner.run_sync()` (sync), passing the agent and a string or list of messages as input. The runner manages the conversation loop, tool calls, and output parsing automatically. A simple research agent that fetches facts and returns a typed result looks like this — and the core definition is fewer than 20 lines:

```python
# agents/researcher.py
from agents import Agent, function_tool
from pydantic import BaseModel

class ResearchResult(BaseModel):
    summary: str
    key_facts: list[str]
    confidence: float

@function_tool
def search_web(query: str) -> str:
    """Search the web for current information on a topic."""
    # Replace with real search integration (e.g., Serper, Tavily)
    return f"[Search results for: {query}]"

researcher = Agent(
    name="Researcher",
    instructions="""You are a research specialist. Given a topic, search for 
    current information and return a structured summary with key facts. 
    Always cite sources. Be factual, not speculative.""",
    model="gpt-4o-mini",
    tools=[search_web],
    output_type=ResearchResult,
)
```

### Running an Agent and Reading Output

```python
# main.py
import asyncio
from agents import Runner
from agents.researcher import researcher

async def main():
    result = await Runner.run(
        researcher,
        input="What are the key trends in AI agent adoption in 2026?"
    )
    output: ResearchResult = result.final_output
    print(f"Summary: {output.summary}")
    print(f"Facts: {output.key_facts}")
    print(f"Confidence: {output.confidence}")

asyncio.run(main())
```

## How Do Handoffs Work in Multi-Agent Pipelines?

Handoffs are the OpenAI Agents SDK's primary mechanism for agent-to-agent delegation — they let one agent transfer control to another when it determines the task is better handled by a specialist. A handoff is declared by adding an agent reference to the `handoffs` list of the delegating agent. At runtime, when the delegating agent decides to hand off, the SDK automatically routes the conversation to the target agent with the full context preserved. This creates a delegation chain where control flows linearly: Agent A handles the initial request, decides to hand to Agent B, and Agent B either completes the task or hands to Agent C. The entire chain executes within a single `Runner.run()` call — you don't manage the routing loop manually. In practice, handoffs work best for clear-boundary specialization: a triage agent routes to a research agent, which hands to a writing agent, which hands to a reviewer. The 2026 dev.to benchmark shows a three-agent handoff chain costs approximately $0.003 per run using gpt-4o-mini (7,000 input + 3,400 output tokens), making it economical even at scale.

```python
# agents/writer.py
from agents import Agent
from pydantic import BaseModel
from agents.researcher import researcher

class ArticleDraft(BaseModel):
    title: str
    body: str
    word_count: int

writer = Agent(
    name="Writer",
    instructions="""You are a technical writer. Take research results and 
    produce a clear, well-structured article draft. Target 800-1000 words. 
    Use concrete examples from the research.""",
    model="gpt-4o-mini",
    output_type=ArticleDraft,
)

# agents/reviewer.py
from agents import Agent
from pydantic import BaseModel

class ReviewedArticle(BaseModel):
    title: str
    body: str
    quality_score: float
    edits_made: list[str]

reviewer = Agent(
    name="Reviewer",
    instructions="""You are an editor. Review the article draft for clarity, 
    accuracy, and structure. Make improvements and score quality 0.0-1.0. 
    List each significant edit you made.""",
    model="gpt-4o",  # Higher quality model for final review
    output_type=ReviewedArticle,
)

# Wire up the handoff chain
from agents.researcher import researcher
researcher.handoffs = [writer]
writer.handoffs = [reviewer]
```

## What Is the Agents-as-Tools Orchestration Pattern?

The agents-as-tools pattern is an alternative to handoffs where a central orchestrator agent calls specialist agents as if they were functions — not by transferring control, but by invoking them and receiving their results. This gives the orchestrator full visibility and control over the pipeline: it decides which agents to call, in what order, and whether to call them in parallel. Specialist agents are wrapped with `agent.as_tool()`, which converts them into callable function tools. The orchestrator's LLM then decides which tools (agents) to invoke based on the task. This pattern is better than handoffs when the orchestrator needs to synthesize results from multiple specialists, branch based on intermediate results, or retry a failed subtask without losing overall context. The tradeoff is that the orchestrator model sees all intermediate results, which increases token cost. Use agents-as-tools for decision-heavy pipelines; use handoffs for linear specialization chains.

```python
# Orchestrator pattern
from agents import Agent, Runner

# Convert specialist agents to tools
research_tool = researcher.as_tool(
    tool_name="research_topic",
    tool_description="Research a topic and return structured facts"
)
write_tool = writer.as_tool(
    tool_name="write_article",
    tool_description="Write an article draft from research results"
)
review_tool = reviewer.as_tool(
    tool_name="review_article",
    tool_description="Review and improve an article draft"
)

orchestrator = Agent(
    name="Orchestrator",
    instructions="""You coordinate a content pipeline. 
    1. First research the topic thoroughly
    2. Then write an article based on the research
    3. Finally review and improve the article
    Return the final reviewed article.""",
    model="gpt-4o",
    tools=[research_tool, write_tool, review_tool],
)

async def run_pipeline(topic: str):
    result = await Runner.run(orchestrator, input=topic)
    return result.final_output
```

## How to Add Guardrails for Safety and Quality Control

Guardrails in the OpenAI Agents SDK are validation hooks that run before an agent processes input (input guardrails) or after it produces output (output guardrails). They let you enforce safety policies and quality standards without modifying the agent's core logic. An input guardrail is a function decorated with `@input_guardrail` that receives the user message and returns a `GuardrailFunctionOutput` — if it sets `tripwire_triggered=True`, the pipeline halts and raises a `InputGuardrailTripwireTriggered` exception that your runner can catch and handle gracefully. Output guardrails work identically but receive the agent's final output. In 2026, with 81% of organizations planning more complex agent deployments, guardrails are the primary mechanism for preventing prompt injection, enforcing output schemas, and maintaining brand safety in production pipelines. A well-placed input guardrail that rejects off-topic or harmful requests before they reach your expensive gpt-4o agents can also reduce token costs significantly.

```python
# guardrails/input_guard.py
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class TopicCheck(BaseModel):
    is_on_topic: bool
    reason: str

topic_checker = Agent(
    name="TopicChecker",
    instructions="Check if the user's request is about technology or AI. Return is_on_topic=True only for relevant topics.",
    model="gpt-4o-mini",
    output_type=TopicCheck,
)

@input_guardrail
async def check_topic(ctx, agent, input_text):
    result = await Runner.run(topic_checker, input=input_text, context=ctx.context)
    check: TopicCheck = result.final_output
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_on_topic,
    )

# Attach guardrail to your main agent
researcher.input_guardrails = [check_topic]
```

Handling guardrail rejections in the runner:

```python
from agents.exceptions import InputGuardrailTripwireTriggered

async def safe_run(topic: str):
    try:
        result = await Runner.run(researcher, input=topic)
        return result.final_output
    except InputGuardrailTripwireTriggered as e:
        return {"error": "Request rejected by safety guardrail", "reason": str(e)}
```

## How to Use Tracing and Observability in Production

The OpenAI Agents SDK ships with built-in tracing that captures every step of agent execution — LLM calls, tool invocations, handoffs, guardrail evaluations — and writes them to a structured trace log without any additional configuration. Tracing is enabled by default and can be observed via the OpenAI platform dashboard or exported to external systems using custom trace processors. Each trace entry includes timing, token counts, model used, input/output content, and whether the step succeeded or raised an exception. This granularity makes it possible to debug exactly where a pipeline failed, identify slow agents, and audit safety decisions. For teams integrating with existing observability stacks (Datadog, Langfuse, Arize), the SDK exposes a `add_trace_processor()` hook that receives every trace event and lets you forward it to any backend. In production, combine SDK tracing with application-level metrics (pipeline latency, guardrail trigger rate, cost per run) for full visibility.

```python
# Enable custom trace processor
from agents import add_trace_processor
from agents.tracing import TraceProcessor, Trace

class CustomProcessor(TraceProcessor):
    def process_trace(self, trace: Trace) -> None:
        # Forward to your observability stack
        print(f"[TRACE] {trace.name} | {trace.duration_ms}ms | {trace.total_tokens} tokens")

add_trace_processor(CustomProcessor())
```

### Deploying with FastAPI for Production

```python
# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from pipeline import orchestrator  # Your assembled pipeline

app = FastAPI()

class PipelineRequest(BaseModel):
    topic: str

@app.post("/run-pipeline")
async def run_pipeline(req: PipelineRequest):
    try:
        result = await Runner.run(orchestrator, input=req.topic)
        return {"status": "success", "output": result.final_output}
    except InputGuardrailTripwireTriggered:
        raise HTTPException(status_code=400, detail="Request rejected by safety guardrail")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## How to Optimize Costs for Multi-Agent Pipelines in 2026

Cost optimization for multi-agent pipelines in 2026 centers on three levers: model selection per agent, structured output efficiency, and parallel execution to reduce wall-clock time without increasing token cost. The benchmark three-agent pipeline (Research → Write → Review) costs approximately $0.003 per run with gpt-4o-mini — roughly 7,000 input tokens and 3,400 output tokens total. Switching the orchestrator to gpt-4o and keeping worker agents on gpt-4o-mini captures quality improvements where it matters while containing cost: gpt-4o-mini costs $0.15 per million input tokens vs $2.50 for gpt-4o (a 16x difference). Structured outputs via Pydantic also reduce cost by eliminating verbose freeform text — an agent that returns `{"summary": "...", "key_facts": [...]}` uses fewer tokens than one that narrates its findings in paragraphs. For pipelines processing many requests concurrently, `asyncio.gather()` runs independent agents in parallel, cutting total latency without duplicating token costs.

```python
# Parallel execution of independent agents
import asyncio
from agents import Runner

async def parallel_research(topics: list[str]):
    tasks = [Runner.run(researcher, input=topic) for topic in topics]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r.final_output for r in results if not isinstance(r, Exception)]

# Model selection strategy
# Use gpt-4o-mini for: research, formatting, classification, guardrail checks
# Use gpt-4o for: final review, complex reasoning, synthesis across many sources

# Caching: cache stable instructions at the provider level
# (OpenAI prompt caching activates automatically for prompts >1024 tokens)
```

### Cost Breakdown by Agent Role

| Agent Role | Recommended Model | Est. Cost/Run | Why |
|---|---|---|---|
| Input guardrail | gpt-4o-mini | $0.0002 | Simple classification |
| Researcher | gpt-4o-mini | $0.001 | Tool-heavy, not reasoning-heavy |
| Writer | gpt-4o-mini | $0.001 | Structured output, clear instructions |
| Reviewer/Orchestrator | gpt-4o | $0.005 | Complex synthesis, high quality threshold |
| Output guardrail | gpt-4o-mini | $0.0002 | Simple validation |

## Advanced Patterns: Dynamic Instructions, Cloning, and Agent Context

Dynamic instructions let an agent adapt its behavior at runtime based on context — user preferences, session state, or upstream agent outputs. Instead of passing a string to `instructions`, pass a callable that receives the `RunContextWrapper` and returns a string. This lets you inject runtime variables (user name, selected language, output length) into the system prompt without creating separate agent definitions. Agent cloning creates a copy of an agent with modified parameters using `.clone()`, which is useful for creating locale variants or quality tiers from a single base definition. The `RunContextWrapper` also provides a shared context object that all agents in a pipeline can read and write, enabling stateful pipelines where downstream agents access data populated by upstream agents.

```python
# Dynamic instructions example
from agents import Agent, RunContextWrapper
from pydantic import BaseModel

class UserContext(BaseModel):
    language: str = "English"
    expertise_level: str = "intermediate"

def dynamic_instructions(ctx: RunContextWrapper[UserContext], agent: Agent) -> str:
    user = ctx.context
    return f"""You are a technical writer. Write in {user.language}. 
    Target audience: {user.expertise_level} developers. 
    Adjust technical depth and terminology accordingly."""

adaptive_writer = Agent(
    name="AdaptiveWriter",
    instructions=dynamic_instructions,
    model="gpt-4o-mini",
)

# Agent cloning for variants
spanish_writer = adaptive_writer.clone(name="SpanishWriter")

# Running with context
async def run_with_context(topic: str, user: UserContext):
    result = await Runner.run(
        adaptive_writer,
        input=topic,
        context=user,
    )
    return result.final_output
```

## FAQ

**Q: What Python version is required for the OpenAI Agents SDK?**
Python 3.10 or later is required. The SDK uses modern type hints and async features that are not available in earlier versions. Python 3.12 is recommended for best performance, but note that pre-0.13.x versions had tracing bugs on 3.12 — always use the current stable release.

**Q: Can I use the OpenAI Agents SDK with non-OpenAI models?**
Yes. The SDK is model-agnostic and works with any provider that implements the OpenAI chat completions API format. Via LiteLLM integration, you can route to 100+ models including Anthropic Claude, Google Gemini, and local models via Ollama. Set the model string to the LiteLLM routing format (e.g., `"anthropic/claude-3-5-sonnet-20241022"`).

**Q: What's the difference between handoffs and agents-as-tools?**
Handoffs transfer control from one agent to another — the delegating agent stops and the receiving agent takes over. Agents-as-tools keep the orchestrator in control while specialist agents are called as functions. Use handoffs for linear pipelines with clear boundaries; use agents-as-tools when an orchestrator needs to synthesize results from multiple specialists or make conditional routing decisions.

**Q: How do I debug a pipeline where an agent produces unexpected output?**
Enable verbose tracing by adding a custom trace processor that logs all trace events. Check the trace for the specific agent step that produced the wrong output, then examine its full input (including conversation history from upstream agents). Common causes: vague instructions that don't constrain output format, missing `output_type` Pydantic model, or a handoff passing too much/too little context.

**Q: What is the realistic cost of running a three-agent pipeline in production?**
At scale with gpt-4o-mini for worker agents and gpt-4o for the reviewer, expect approximately $0.003-$0.008 per pipeline run depending on input length and tool call count. For 10,000 runs/day, that's $30-$80/day — comparable to a basic cloud instance. Parallel execution and prompt caching can reduce this by 20-40% on stable, repetitive pipelines.
