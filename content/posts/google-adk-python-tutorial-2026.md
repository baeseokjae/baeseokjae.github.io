---
title: "Google ADK Tutorial: Build Multi-Agent Systems with Python (2026)"
date: 2026-05-09T18:04:05+00:00
tags: ["Google ADK", "multi-agent systems", "Python", "AI agents", "Gemini", "Vertex AI"]
description: "Step-by-step Google ADK tutorial: install google-adk, build LlmAgent pipelines, run parallel agents, and deploy to Vertex AI in 2026."
draft: false
cover:
  image: "/images/google-adk-python-tutorial-2026.png"
  alt: "Google ADK Tutorial: Build Multi-Agent Systems with Python"
  relative: false
schema: "schema-google-adk-python-tutorial-2026"
---

Google ADK (Agent Development Kit) lets you build a working multi-agent Python system in under 30 minutes — with LlmAgent for reasoning, SequentialAgent and ParallelAgent for orchestration, and a built-in dev UI for debugging. This tutorial walks you from zero to a deployed multi-agent pipeline.

## What Is Google ADK and Why It Matters in 2026

Google ADK (Agent Development Kit) is an open-source, code-first Python framework released by Google at Cloud Next 2025 for building, orchestrating, and deploying AI agents. Unlike drag-and-drop tools, ADK is built for developers who want full control over agent logic, tool integration, and multi-agent coordination. ADK is optimized for Gemini models but is genuinely model-agnostic through LiteLLM integration, meaning you can run the same agent code against GPT-4, Claude, or any OpenAI-compatible endpoint. The framework reached stable v1.0.0 in May 2025, and ADK Python 2.0 Beta with agent teams and advanced workflows shipped in early 2026. With 13 million developers already building on Google's generative models and Gemini API active developers up 118% year-over-year as of Q3 2025, ADK has become the default path for Google Cloud-native agent development. The AI agents market itself hit USD 7.63 billion in 2025 and is projected to grow at 49.6% CAGR through 2033 — choosing the right framework now has long-term career implications.

The three reasons to pick ADK over LangGraph or CrewAI in 2026: first, native Vertex AI Agent Engine deployment with one command; second, the A2A (Agent-to-Agent) protocol for cross-framework orchestration; third, a built-in dev web UI that shows you exactly what each agent said, which tools it called, and what the session state looks like at every step.

## Prerequisites and Installation (pip install google-adk)

Google ADK requires Python 3.10 or higher and a Google API key or Vertex AI credentials. For local development, a free Gemini API key from Google AI Studio is sufficient — no billing account required. For production Vertex AI deployment, you'll need a Google Cloud project with the Vertex AI API enabled. Install ADK with a single pip command:

```bash
pip install google-adk
```

For the full tutorial, also install optional dependencies:

```bash
pip install google-adk[vertexai] litellm python-dotenv
```

Create a project directory and set up your environment:

```bash
mkdir my-adk-project && cd my-adk-project
echo "GOOGLE_API_KEY=your_key_here" > .env
echo "GOOGLE_GENAI_USE_VERTEXAI=FALSE" >> .env
```

ADK projects follow a package convention: each agent lives in its own Python package directory with an `__init__.py` that exports a root `agent` variable. This structure is not optional — the `adk run` and `adk web` CLI commands discover agents by looking for this pattern. A minimal project looks like:

```
my-adk-project/
  .env
  my_agent/
    __init__.py
    agent.py
    tools.py
```

Verify installation with `adk --version`. If you see `google-adk 1.x.x` or later, you're ready.

## Core Concepts: LlmAgent, SequentialAgent, ParallelAgent, and Custom Agents

Google ADK organizes agent logic into four primitive types that compose into hierarchical agent trees. The LlmAgent (also aliased as `Agent`) is the reasoning primitive — it receives a system prompt, a set of tools, and a Gemini model name, then autonomously decides which tools to call and what to return. The SequentialAgent is a workflow primitive: it runs a list of child agents one after another, passing session state between them. The ParallelAgent runs child agents concurrently, collecting results via separate output keys to avoid write conflicts. Custom agents extend `BaseAgent` directly and let you implement arbitrary logic — database lookups, if/else branching, loops — without an LLM in the loop.

The key architectural insight is that these types compose freely. A SequentialAgent can contain LlmAgents and ParallelAgents. A ParallelAgent's children can themselves be mini-pipelines with their own SequentialAgent structure. This hierarchical tree is how ADK scales from a single-agent chatbot to a 20-agent enterprise pipeline without changing the core pattern.

All state flows through `session.state`, a dictionary attached to each conversation session. An agent writes to `session.state["key"]` via the `output_key` field or tool return values; downstream agents read from it. This shared-whiteboard design means agents don't need direct references to each other — they communicate through state, which is inspectable, serializable, and debuggable.

## Building Your First Agent: A Simple LlmAgent with Custom Tools

An LlmAgent with custom tools is the starting point for every ADK project. Below is a complete working example of a code analysis agent that uses two Python functions as tools:

```python
# my_agent/tools.py
import subprocess

def run_pylint(file_path: str) -> str:
    """Run pylint on a Python file and return the output."""
    result = subprocess.run(
        ["python", "-m", "pylint", file_path, "--output-format=text"],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout or result.stderr

def read_file(file_path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {file_path}"
```

```python
# my_agent/agent.py
from google.adk.agents import LlmAgent
from .tools import run_pylint, read_file

root_agent = LlmAgent(
    name="code_reviewer",
    model="gemini-2.0-flash",
    description="Reviews Python code for quality and style issues",
    instruction="""You are a senior Python developer doing code review.
    When given a file path, read the file and run pylint on it.
    Summarize the issues found, grouping them by severity.
    Always end with an overall quality score from 1-10.""",
    tools=[read_file, run_pylint],
)
```

```python
# my_agent/__init__.py
from .agent import root_agent
```

ADK automatically converts plain Python functions into tools — it reads the docstring as the tool description and the type annotations as parameter schemas. This means no decorator boilerplate. Run the agent interactively with `adk run my_agent` or open the dev UI with `adk web` to test it visually.

## Building a Multi-Agent Pipeline: Sequential Workflow Example

A SequentialAgent chains multiple specialized agents into a pipeline where each agent's output becomes the next agent's input. This pattern is ideal for code review → test generation → documentation workflows. Here's a three-agent code review pipeline:

```python
# pipeline/agent.py
from google.adk.agents import LlmAgent, SequentialAgent

# Agent 1: reads and analyzes code quality
analyzer = LlmAgent(
    name="code_analyzer",
    model="gemini-2.0-flash",
    description="Analyzes Python code and extracts quality metrics",
    instruction="""Read the file at the path in session state key 'file_path'.
    Analyze it for: complexity, naming, documentation, error handling.
    Store your structured analysis in output_key='analysis'.""",
    output_key="analysis",
)

# Agent 2: generates improvement suggestions based on analysis
suggester = LlmAgent(
    name="improvement_suggester",
    model="gemini-2.0-flash",
    description="Generates specific improvement suggestions from code analysis",
    instruction="""Read the code analysis from session state key 'analysis'.
    Generate 5 specific, actionable improvement suggestions with code examples.
    Store suggestions in output_key='suggestions'.""",
    output_key="suggestions",
)

# Agent 3: writes the final review report
reporter = LlmAgent(
    name="report_writer",
    model="gemini-2.0-flash",
    description="Writes a structured code review report",
    instruction="""Using 'analysis' and 'suggestions' from session state,
    write a professional code review report in Markdown format.
    Include: executive summary, detailed findings, and action items.""",
    output_key="final_report",
)

root_agent = SequentialAgent(
    name="code_review_pipeline",
    description="Complete code review pipeline: analyze, suggest, report",
    sub_agents=[analyzer, suggester, reporter],
)
```

The `output_key` field is the key mechanism here: each LlmAgent writes its response text into `session.state[output_key]` automatically. Downstream agents reference these keys in their instruction prompts. The SequentialAgent guarantees execution order — analyzer finishes before suggester starts, suggester finishes before reporter starts.

To trigger the pipeline, pass the initial state when starting a session:

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="code_review", session_service=session_service)

session = session_service.create_session(
    app_name="code_review",
    user_id="dev_user",
    state={"file_path": "my_module.py"}
)

for event in runner.run(
    user_id="dev_user",
    session_id=session.id,
    new_message=Content(parts=[Part(text="Review the file.")])
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

## Running Agents in Parallel: Speeding Up Complex Workflows

ParallelAgent runs multiple child agents concurrently, which dramatically reduces latency for independent subtasks. The canonical use case is a research pipeline where you want to gather information from multiple sources simultaneously rather than waiting for each one sequentially. The critical constraint: each parallel child agent must write to a unique `output_key` — writing to the same key causes a race condition where the last-finishing agent overwrites earlier results.

Here's a parallel research agent that simultaneously searches documentation, checks GitHub issues, and scans blog posts:

```python
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

# These three agents run concurrently
docs_researcher = LlmAgent(
    name="docs_researcher",
    model="gemini-2.0-flash",
    description="Searches official documentation",
    instruction="Search the official ADK documentation for information about: {topic}. "
                "Return key facts and code examples. Store in output_key='docs_findings'.",
    output_key="docs_findings",
    tools=[search_docs_tool],  # your search tool
)

issues_researcher = LlmAgent(
    name="issues_researcher",
    model="gemini-2.0-flash",
    description="Searches GitHub issues for known problems and solutions",
    instruction="Search GitHub issues for: {topic}. "
                "Return relevant issues and their solutions. Store in output_key='issues_findings'.",
    output_key="issues_findings",
    tools=[search_github_tool],
)

blog_researcher = LlmAgent(
    name="blog_researcher",
    model="gemini-2.0-flash",
    description="Searches developer blog posts and tutorials",
    instruction="Find blog posts and tutorials about: {topic}. "
                "Summarize key insights. Store in output_key='blog_findings'.",
    output_key="blog_findings",
    tools=[search_web_tool],
)

# ParallelAgent runs all three simultaneously
parallel_research = ParallelAgent(
    name="parallel_researcher",
    description="Gathers information from multiple sources concurrently",
    sub_agents=[docs_researcher, issues_researcher, blog_researcher],
)

# SequentialAgent wraps the parallel step, then synthesizes
synthesizer = LlmAgent(
    name="synthesizer",
    model="gemini-2.0-flash",
    description="Synthesizes research from all sources into a final answer",
    instruction="""Synthesize the research from these session state keys:
    - docs_findings: official documentation results
    - issues_findings: GitHub issues findings
    - blog_findings: blog post findings
    Write a comprehensive, well-sourced answer.""",
    output_key="final_answer",
)

root_agent = SequentialAgent(
    name="research_pipeline",
    sub_agents=[parallel_research, synthesizer],
)
```

In practice, parallel ADK agents reduce latency by the time of the slowest subtask rather than the sum of all subtasks. A three-way parallel research step taking 8 seconds total beats a sequential 24-second equivalent.

## Agent Communication: Session State and the Shared Whiteboard Pattern

Session state is the backbone of multi-agent communication in ADK. It functions as a shared whiteboard: any agent can read from or write to it, it persists for the lifetime of a session, and the ADK web UI shows you its full contents at every step. Understanding how state flows prevents the most common multi-agent bugs — race conditions, overwritten keys, and agents that reference state keys that haven't been populated yet.

The three ways agents interact with session state are: automatic output key writing (when you set `output_key="key"`, the agent's final response text is stored there automatically); tool return values (tools can return dictionaries that get merged into state); and explicit state manipulation in custom agents (by accessing `ctx.session.state` directly in `BaseAgent` implementations).

A common mistake is having two ParallelAgent children write to the same key. The fix is to always use distinct output keys, then have a downstream agent merge them:

```python
# WRONG: race condition
agent_a = LlmAgent(name="a", output_key="result", ...)
agent_b = LlmAgent(name="b", output_key="result", ...)  # overwrites agent_a!

# CORRECT: unique keys, merged downstream
agent_a = LlmAgent(name="a", output_key="result_a", ...)
agent_b = LlmAgent(name="b", output_key="result_b", ...)

merger = LlmAgent(
    name="merger",
    instruction="Combine 'result_a' and 'result_b' from session state into a unified output.",
    output_key="result",
)
```

For complex pipelines, prefix output keys with the agent name: `"analyzer_summary"`, `"validator_report"`, `"formatter_output"`. This makes state inspection in the dev UI immediately readable and prevents accidental collisions across pipeline stages.

## Integrating A2A Protocol for Cross-Framework Agent Communication

The Agent-to-Agent (A2A) protocol is ADK's answer to framework fragmentation: a standard HTTP-based protocol for agents built in different frameworks — ADK, LangGraph, CrewAI, AutoGen — to delegate tasks to each other. An ADK agent can call a LangGraph agent as if it were a local tool, and vice versa. A2A was introduced alongside ADK at Google Cloud Next 2025 and is now supported by over 50 enterprise software vendors including Salesforce, SAP, and Atlassian.

To expose an ADK agent as an A2A server, wrap it in an `A2AServer`:

```python
from google.adk.a2a import A2AServer

server = A2AServer(agent=root_agent, port=8080)
server.start()
```

To call a remote A2A agent from within another ADK agent, use the `A2AClient` as a tool:

```python
from google.adk.a2a import A2AClient

remote_agent_tool = A2AClient(
    name="remote_validator",
    description="Validates code against company style guidelines using the remote validator agent",
    url="http://validator-service:8080",
)

orchestrator = LlmAgent(
    name="orchestrator",
    model="gemini-2.0-flash",
    instruction="Analyze the code, then use the remote_validator tool to check style compliance.",
    tools=[remote_agent_tool],
)
```

The A2A protocol handles authentication, streaming, and error propagation transparently. From the orchestrator's perspective, the remote agent looks identical to a local Python function tool. This is the key architectural benefit: you can start with all agents local, then split specific high-load agents into microservices without changing any orchestration code.

## Testing and Debugging with ADK's Built-in Dev UI

ADK ships with a local web UI that is the fastest way to test and debug multi-agent systems. Run `adk web` in your project directory and open `http://localhost:8000` in a browser. The UI shows real-time agent execution: which agent is active, what messages it sent to the model, which tools were called with what arguments, and the complete session state at every step.

The dev UI is far more useful than print statements for multi-agent debugging because it shows the agent tree visually. When a SequentialAgent runs, you see each child agent activate in sequence. When a ParallelAgent runs, you see all children fire simultaneously. Session state appears as a live JSON panel that updates after each agent writes its output key.

For automated testing, ADK provides `InMemorySessionService` and a synchronous `Runner` that makes unit testing individual agents straightforward:

```python
import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from my_agent import root_agent

def test_code_reviewer_returns_score():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="test_app",
        session_service=session_service
    )
    session = session_service.create_session(
        app_name="test_app", user_id="test_user"
    )
    
    events = list(runner.run(
        user_id="test_user",
        session_id=session.id,
        new_message=Content(parts=[Part(text="Review my_module.py")])
    ))
    
    final = next(e for e in events if e.is_final_response())
    assert "score" in final.content.parts[0].text.lower()
```

For integration testing multi-agent pipelines, assert on `session.state` after the run completes — this validates that each agent wrote its expected output key correctly.

## Deploying Your Multi-Agent System to Vertex AI Agent Engine

Vertex AI Agent Engine is the managed runtime for ADK agents in Google Cloud. It handles auto-scaling, session persistence, monitoring, and IAM integration — you ship the agent code; Google manages the infrastructure. The deployment path is a single CLI command after authenticating with Google Cloud:

```bash
gcloud auth application-default login
pip install google-cloud-aiplatform[adk,reasoningengine]
```

```python
# deploy.py
import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(project="your-project-id", location="us-central1")

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

remote_app = reasoning_engines.ReasoningEngine.create(
    app,
    requirements=["google-adk>=1.0.0", "google-cloud-aiplatform"],
    display_name="Code Review Multi-Agent System",
    description="Multi-agent pipeline for automated code review",
)

print(f"Deployed: {remote_app.resource_name}")
```

Running `python deploy.py` packages your agent code, uploads it to Vertex AI, and returns a resource name you use for all future invocations. The deployed agent gets a REST endpoint that accepts the same message format as the local runner — no code changes between local dev and production.

For production deployments, enable Cloud Trace integration by setting `enable_tracing=True` (as above). This gives you Gemini model latency breakdowns, tool call timing, and agent step traces in the Google Cloud Console — critical for diagnosing where pipeline latency comes from at scale.

## Google ADK vs LangGraph vs CrewAI: When to Choose Each

Google ADK, LangGraph, and CrewAI serve overlapping but distinct use cases. ADK is the right choice when you're building on Google Cloud, need Vertex AI deployment, or want the A2A protocol for cross-framework orchestration. LangGraph is the right choice when you need fine-grained control over agent execution graphs with custom branching, loops, and human-in-the-loop checkpoints — its graph-based model is more flexible than ADK's tree model for complex conditional workflows. CrewAI is the right choice for rapid prototyping with a role-based team metaphor — its higher-level abstractions are faster to write but less controllable.

| Dimension | Google ADK | LangGraph | CrewAI |
|---|---|---|---|
| **Primary abstraction** | Agent tree (hierarchical) | Directed graph | Role-based crew |
| **Gemini optimization** | Native | Via LangChain | Via LangChain |
| **Vertex AI deployment** | One command | Manual | Manual |
| **Dev UI built-in** | Yes (`adk web`) | No | No |
| **A2A protocol** | Native | Via adapter | Via adapter |
| **State management** | `session.state` dict | State schema + reducers | Context passing |
| **Learning curve** | Low (Python functions) | Medium (graph concepts) | Low (role prompts) |
| **Best for** | GCP-native, Gemini, enterprise | Complex branching, stateful loops | Quick prototypes, team simulation |

The practical decision rule: if your agents need to call each other across frameworks or you're deploying to GCP, use ADK. If your workflow has complex conditional branching or cycles, use LangGraph. If you want something running in a weekend, use CrewAI.

## Real-World Use Cases: Code Review, Customer Support, and Research Pipelines

Three production patterns demonstrate where multi-agent ADK systems deliver the most value.

**Code Review Pipeline** — The most natural fit for a SequentialAgent: analyzer reads code and extracts metrics, security scanner checks for OWASP vulnerabilities, style checker validates against company conventions, and a report writer synthesizes all findings. Companies like Sourcegraph have reported 40% reduction in human code review time when AI pre-review runs on every PR. The ADK implementation handles this with four LlmAgents in a SequentialAgent, each writing to a distinct output key, with the final report agent reading all three upstream keys.

**Customer Support Escalation** — A router LlmAgent classifies incoming tickets by type (billing, technical, account), then routes to a specialized agent for that category. Technical tickets can spawn a ParallelAgent that simultaneously searches the knowledge base, checks system status, and retrieves the customer's history. The specialized agents resolve or escalate based on their findings. ADK's session state persists conversation history, so escalated tickets carry full context to the human agent who picks them up.

**Research Summarization Workflow** — A parallel research step fetches from arXiv, GitHub, and blog sources simultaneously. A deduplication agent removes redundant findings. A synthesis agent writes the final summary. This pattern compresses 45 minutes of manual research into under 3 minutes when combined with Gemini's 1M-token context window and web search tools. The A2A protocol enables adding specialized external agents — a statistics analyzer, a domain-specific validator — without refactoring the core pipeline.

---

## FAQ

The questions below address the most common sticking points developers hit when starting with Google ADK in 2026. Google ADK (Agent Development Kit) is a production-ready, open-source Python framework for building multi-agent AI systems that reached stable v1.0.0 in May 2025. It is optimized for Gemini models and Google Cloud infrastructure, but works with any OpenAI-compatible model via LiteLLM. The framework uses a hierarchical agent tree model where LlmAgents handle reasoning, SequentialAgents and ParallelAgents orchestrate workflows, and session state acts as the shared communication layer. Deployment to Vertex AI Agent Engine requires minimal configuration and provides enterprise-grade scaling, monitoring, and IAM integration. With 13 million developers already on Google's generative model platform and the AI agents market growing at 49.6% CAGR, understanding ADK's core patterns — installation, agent composition, state management, and A2A cross-framework communication — is increasingly a baseline skill for Python developers building AI-powered applications in 2026.

### How do I install Google ADK?

Run `pip install google-adk` in a Python 3.10+ environment. For production Vertex AI deployment, use `pip install google-adk[vertexai]`. Set your `GOOGLE_API_KEY` environment variable or configure Application Default Credentials for Google Cloud. Verify with `adk --version`.

### What is the difference between LlmAgent and SequentialAgent in Google ADK?

LlmAgent is a reasoning primitive — it calls a Gemini model to decide what to do, which tools to invoke, and what to return. SequentialAgent is a workflow primitive — it has no model of its own, it just runs a list of child agents one after another in order. You compose them: a SequentialAgent contains LlmAgents as children.

### How does session state work in Google ADK multi-agent systems?

Session state (`session.state`) is a Python dictionary that persists for the lifetime of a conversation session. Agents write to it via `output_key` (the agent's response is automatically stored at that key) or by returning dictionaries from tool functions. All agents in the same pipeline share the same state object, so downstream agents read what upstream agents wrote.

### Can Google ADK work with models other than Gemini?

Yes. ADK supports non-Gemini models through LiteLLM integration. Install `litellm` and configure the model string as `"litellm/gpt-4o"` or `"litellm/claude-opus-4-7"` instead of a Gemini model name. This lets you run the same ADK agent code against any OpenAI-compatible model endpoint.

### How do I deploy a Google ADK agent to production?

For Vertex AI deployment, use `reasoning_engines.AdkApp` with `reasoning_engines.ReasoningEngine.create()`. This packages your agent code and deploys it to Google Cloud with auto-scaling and session management. Alternatively, export ADK agents as FastAPI apps using `adk api_server` for deployment to Cloud Run or any container infrastructure.
