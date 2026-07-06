---
cover:
  alt: 'CrewAI Tutorial 2026: Build Multi-Agent Systems in Python Step by Step'
  image: /images/crewai-tutorial-2026.png
  relative: false
date: 2026-04-19 11:46:58+00:00
description: 'Complete CrewAI tutorial for 2026: install, configure agents, add tools,
  implement memory, and deploy multi-agent Python systems to production.'
draft: false
schema: schema-crewai-tutorial-2026
tags:
- crewai
- multi-agent
- python
- ai-agents
- llm
title: 'CrewAI Tutorial 2026: Build Multi-Agent Systems in Python Step by Step'
---

CrewAI is a Python framework for building multi-agent AI systems where each agent has a defined role, goal, and backstory — and agents collaborate to complete complex tasks. Install it with `pip install crewai`, define agents and tasks in YAML files, then wire them together with a Python class. As of April 2026, CrewAI has 49k GitHub stars and over 14,800 monthly searches, making it the fastest-growing multi-agent framework available.

## Why CrewAI Is the Go-To Framework for Multi-Agent Systems in 2026

CrewAI is a purpose-built multi-agent orchestration framework — not a wrapper around LangChain, but an independent implementation written from scratch. It models agents as collaborative team members with distinct roles (Researcher, Writer, Analyst), each equipped with specific tools and a clear goal. Unlike graph-based alternatives such as LangGraph, CrewAI uses a role-playing paradigm that maps closely to how real teams divide work. The GitHub repository hit 49,000 stars with 6,700+ forks as of April 2026, and version 1.14.2 ships with built-in support for OpenAI, Anthropic, Google Gemini, Azure OpenAI, and Ollama via LiteLLM. Teams running production workloads report 40-60% reduction in prompt engineering time compared to single-agent setups, because each agent only needs instructions relevant to its narrow specialization. The framework ships with two primary abstractions: **Crews** for collaborative single-workflow agent teams, and **Flows** for multi-stage orchestration pipelines with conditional branching and state management. This tutorial walks through all 13 steps from installation to production deployment.

## Prerequisites: What You Need Before Installing CrewAI

CrewAI requires Python 3.10 or higher (3.12 or 3.13 recommended), at least one LLM provider API key, and `pip` or `uv` for package management. No GPU or specialized hardware is needed — all model inference happens via remote API calls to your chosen provider. A development machine with 4GB RAM and a modern CPU handles everything from installation through local testing. For following the web-search tool examples, a free-tier Serper API or Tavily API key is sufficient. The project scaffold generates a `.env` template listing every environment variable you need before you write a single line of code. For production deployments, Docker and a cloud provider account (AWS, GCP, Railway, Fly.io) are helpful for containerizing and running your crew as a long-lived service, but neither is required to complete this tutorial. If you're new to Python environments, use `python -m venv .venv && source .venv/bin/activate` before installing packages to keep your global Python installation clean.

## Step 1: How to Install CrewAI and Create Your First Project

Installing CrewAI follows the same pattern as any modern Python CLI tool — you install the core package, optionally add tools, then scaffold a project directory. The CLI generates the complete project structure including YAML configuration files, so you don't need to hand-write boilerplate.

```bash
# Install with uv (recommended) or pip
pip install crewai crewai-tools

# Scaffold a new project
crewai create crew my_research_crew
cd my_research_crew

# Install project dependencies
pip install -r requirements.txt
```

The `crewai create crew` command generates this structure:

```
my_research_crew/
├── src/
│   └── my_research_crew/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── tools/
│       │   └── custom_tool.py
│       ├── crew.py
│       └── main.py
├── pyproject.toml
└── .env
```

The `config/` directory holds your agent and task definitions in YAML — this is where most of your day-to-day configuration lives. The `crew.py` file wires everything together using Python decorators.

## Step 2: How to Configure LLM Providers with Environment Variables

CrewAI configures LLM providers entirely through environment variables, using LiteLLM as a universal adapter layer. This means switching from OpenAI GPT-4o to Anthropic Claude or Google Gemini requires changing two environment variables — no code changes. The default model is `gpt-4o` when `OPENAI_API_KEY` is set, but you can override this globally via `OPENAI_MODEL_NAME` or per-agent using the `llm` field in `agents.yaml`. In 2026, most production teams run mixed-model setups: a cheaper model like Claude Haiku or Gemini Flash for research and summarization agents, and a premium model like Claude Sonnet or GPT-4o only for the final synthesis or writing step. This hybrid approach reduces per-run cost by 50–70% without measurable quality loss for structured research workflows. The `.env` file pattern also makes it easy to rotate API keys or switch providers without touching agent or task definitions.

```bash
# .env file
OPENAI_API_KEY=sk-...              # For OpenAI (default provider)
ANTHROPIC_API_KEY=sk-ant-...       # For Claude models
GOOGLE_API_KEY=AIza...             # For Gemini models
SERPER_API_KEY=...                 # For web search tool
```

To use Claude Sonnet as your default model:

```bash
OPENAI_API_KEY=sk-ant-...
OPENAI_MODEL_NAME=claude-sonnet-4-6
OPENAI_API_BASE=https://api.anthropic.com/v1
```

Or configure it per-agent in YAML (shown in Step 3). For local models via Ollama, set `OPENAI_API_BASE=http://localhost:11434/v1` and use model names like `ollama/llama3.2`.

## Step 3: How to Define Agents in YAML with Roles, Goals, and Backstories

CrewAI agent definitions live in `config/agents.yaml`. Each agent has three required fields — `role`, `goal`, and `backstory` — plus optional fields for the LLM, tools, memory settings, and verbosity. The backstory is more important than it sounds: it provides the context that shapes how the LLM interprets ambiguous instructions within that agent's scope.

```yaml
# config/agents.yaml
researcher:
  role: >
    Senior Research Analyst
  goal: >
    Gather comprehensive, accurate information about {topic}
    from reliable sources. Identify key trends and data points.
  backstory: >
    You are a veteran research analyst with 10 years of experience
    in technology trends. You never cite sources you haven't verified,
    and you flag uncertainty explicitly when data is incomplete.
  verbose: true
  memory: true

writer:
  role: >
    Technical Content Writer
  goal: >
    Transform research findings into clear, engaging articles
    that developers can immediately apply to their work.
  backstory: >
    You write for senior developers who value precision over prose.
    You use concrete examples, avoid marketing language, and always
    include working code snippets when relevant.
  verbose: true
  llm: claude-sonnet-4-6  # Override global LLM for this agent
```

The `{topic}` placeholder is filled at runtime when you kick off the crew — this is CrewAI's template interpolation syntax.

## Step 4: How to Create Tasks in YAML with Dependencies and Context

Tasks in CrewAI map to discrete pieces of work assigned to specific agents. The key design decision is `context` — tasks can declare dependencies on other tasks, and their output gets injected into the dependent task's prompt automatically. This is how multi-agent collaboration actually happens in CrewAI.

```yaml
# config/tasks.yaml
research_task:
  description: >
    Research the following topic thoroughly: {topic}
    
    Focus on:
    1. Current state and key statistics (with dates)
    2. Leading tools, frameworks, or companies in this space
    3. Common use cases and real-world examples
    4. Known limitations or caveats
    
    Produce a structured research report with sources.
  expected_output: >
    A detailed research report in markdown format with:
    - Executive summary (100 words)
    - Key findings with citations
    - Data tables where relevant
    - Source list
  agent: researcher

writing_task:
  description: >
    Using the research report provided, write a technical blog post
    targeting senior developers. The article should be 1,500+ words,
    include code examples, and have a practical focus.
  expected_output: >
    A complete blog post in markdown format ready for publication.
  agent: writer
  context:
    - research_task  # Output from research_task is injected here
```

The `context` field is the most powerful feature in task design. When `writing_task` runs, CrewAI automatically prepends the output of `research_task` to the writer agent's prompt.

## Step 5: How to Build the Crew Definition with Python Decorators

The `crew.py` file uses Python decorators to bind YAML configurations to agent and task instances. The `@CrewBase` class decorator loads YAML files automatically. `@agent` methods return configured `Agent` instances. `@task` methods return configured `Task` instances. The `@crew` method assembles everything into a `Crew` object.

```python
# src/my_research_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class MyResearchCrew():
    """Multi-agent research and writing crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['writing_task'],
            output_file='output/article.md'  # Saves result to file
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Auto-collected from @agent methods
            tasks=self.tasks,    # Auto-collected from @task methods
            process=Process.sequential,
            verbose=True
        )
```

The `Process.sequential` setting means tasks execute in order. For parallel execution, use `Process.hierarchical` with a manager agent.

## Step 6: How to Run the Crew and Monitor Execution

Running a CrewAI crew is a single `kickoff()` call that blocks until all tasks complete and returns a `CrewOutput` object containing the raw text result, structured Pydantic output (if configured), and a token usage summary. Pass a dictionary of inputs to `kickoff()` — the keys must match the `{placeholder}` variables in your YAML task descriptions. When `verbose=True` is set on agents, you'll see real-time output showing each agent's current task, reasoning steps, tool calls and results, and final output. This verbose output is essential during development for catching misconfigured tasks — for instance, you'll quickly spot if an agent is querying the wrong source or if a task description is too vague and producing off-topic results. In production, set `verbose=False` to suppress the console output and log `result.token_usage` to your metrics system to track costs per run. The `CrewOutput.token_usage` field includes total tokens, prompt tokens, and completion tokens broken down by model — critical for cost attribution in multi-model setups.

```python
# src/my_research_crew/main.py
from my_research_crew.crew import MyResearchCrew

def run():
    inputs = {
        'topic': 'CrewAI multi-agent framework in 2026'
    }
    
    result = MyResearchCrew().crew().kickoff(inputs=inputs)
    print(result.raw)
    print(f"\nToken usage: {result.token_usage}")

if __name__ == "__main__":
    run()
```

```bash
crewai run
```

You'll see output like:

```
[2026-04-19 10:00:00][INFO]: Working Agent: Senior Research Analyst
[2026-04-19 10:00:00][INFO]: Starting Task: Research the following topic...
[2026-04-19 10:00:01][INFO]: Using tool: Search the internet
[2026-04-19 10:00:03][INFO]: Tool result: CrewAI has 49k stars...
```

The `result` object contains `.raw` (string output), `.pydantic` (structured output if configured), and `.token_usage` (cost tracking).

## Step 7: How to Add Tools for Web Search, Scraping, and File Operations

CrewAI ships with a rich tool library in `crewai-tools`. Tools are Python classes that agents can invoke during task execution. The most commonly used tools in production are `SerperDevTool` for web search, `ScrapeWebsiteTool` for scraping specific pages, `FileReadTool`/`FileWriteTool` for file I/O, and `PDFSearchTool` for document analysis.

```python
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    FileReadTool,
    FileWriteTool,
    PDFSearchTool,
    DirectoryReadTool,
)

# Assign tools to specific agents in crew.py
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config['researcher'],
        tools=[
            SerperDevTool(),           # Web search via Serper API
            ScrapeWebsiteTool(),       # Scrape any URL
            PDFSearchTool(),           # Semantic search in PDFs
        ]
    )

@agent
def data_analyst(self) -> Agent:
    return Agent(
        config=self.agents_config['data_analyst'],
        tools=[
            FileReadTool(file_path='./data/metrics.csv'),
            DirectoryReadTool(directory='./reports/'),
        ]
    )
```

Each tool handles its own error handling and retry logic. If a tool call fails, the agent receives the error message and can try an alternative approach or report the failure.

## Step 8: How to Create Custom Tools for Business-Specific Operations

Custom tools in CrewAI are Python classes that inherit from `BaseTool`. You define the tool's name, description (what agents see when deciding to use it), and `_run` method (the actual logic). The description is critical — agents use it to decide which tool to use for a given subtask.

```python
# src/my_research_crew/tools/database_tool.py
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import psycopg2

class DatabaseQueryInput(BaseModel):
    """Input schema for DatabaseQueryTool"""
    query: str = Field(description="SQL SELECT query to execute (read-only)")
    database: str = Field(description="Database name to query", default="analytics")

class DatabaseQueryTool(BaseTool):
    name: str = "Query Analytics Database"
    description: str = (
        "Execute read-only SQL queries against the analytics database. "
        "Use this to retrieve user metrics, conversion data, or event counts. "
        "Only SELECT statements are permitted."
    )
    args_schema: Type[BaseModel] = DatabaseQueryInput

    def _run(self, query: str, database: str = "analytics") -> str:
        if not query.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries are permitted."
        
        try:
            conn = psycopg2.connect(f"dbname={database}")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            conn.close()
            
            # Format as markdown table
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"
            rows = ["| " + " | ".join(str(v) for v in row) + " |" for row in results[:20]]
            return "\n".join([header, separator] + rows)
        except Exception as e:
            return f"Database error: {str(e)}"
```

Attach the custom tool to an agent the same way as built-in tools: `tools=[DatabaseQueryTool()]`.

## Step 9: How to Implement Structured Outputs with Pydantic Models

By default, CrewAI tasks return plain text. For production pipelines where downstream code needs to parse the output, you can enforce structured outputs using Pydantic models. When a task has `output_pydantic` set, CrewAI instructs the LLM to return JSON matching the schema and validates the result.

```python
# src/my_research_crew/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ResearchFinding(BaseModel):
    category: str = Field(description="Category: trend, statistic, tool, limitation")
    content: str = Field(description="The finding itself")
    source: Optional[str] = Field(description="URL or publication name")
    confidence: str = Field(description="high, medium, or low")

class ResearchReport(BaseModel):
    topic: str
    summary: str = Field(description="Executive summary in 100 words")
    findings: List[ResearchFinding]
    limitations: List[str] = Field(description="Known gaps or caveats in the research")
    sources: List[str]
```

Apply it to a task in `crew.py`:

```python
from my_research_crew.models import ResearchReport

@task
def research_task(self) -> Task:
    return Task(
        config=self.tasks_config['research_task'],
        output_pydantic=ResearchReport  # Enforce structured output
    )
```

Access the result in Python:

```python
result = MyResearchCrew().crew().kickoff(inputs=inputs)
report: ResearchReport = result.pydantic
print(f"Found {len(report.findings)} findings")
for finding in report.findings:
    if finding.confidence == "high":
        print(f"[{finding.category}] {finding.content}")
```

## Step 10: How to Use CrewAI Flows for Complex Multi-Stage Orchestration

CrewAI Flows extend the framework beyond single crews. A Flow coordinates multiple crews in sequence or parallel, passing state between them and enabling conditional branching. Flows are Python classes decorated with `@Flow` where methods decorated with `@start` and `@listen` define the execution graph.

```python
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel

class ContentPipelineState(BaseModel):
    topic: str = ""
    research: str = ""
    article: str = ""
    approved: bool = False
    revision_count: int = 0

class ContentPipelineFlow(Flow[ContentPipelineState]):

    @start()
    def gather_topic(self):
        self.state.topic = "AI agent frameworks in 2026"
        print(f"Starting pipeline for: {self.state.topic}")

    @listen(gather_topic)
    def run_research(self):
        result = ResearchCrew().crew().kickoff(
            inputs={"topic": self.state.topic}
        )
        self.state.research = result.raw

    @listen(run_research)
    def write_article(self):
        result = WritingCrew().crew().kickoff(
            inputs={
                "topic": self.state.topic,
                "research": self.state.research
            }
        )
        self.state.article = result.raw

    @router(write_article)
    def review_article(self):
        # Decide whether to approve or revise
        if len(self.state.article) > 2000 and self.state.revision_count < 2:
            return "approved"
        return "needs_revision"

    @listen("approved")
    def publish(self):
        with open("output/final_article.md", "w") as f:
            f.write(self.state.article)
        print("Article published!")

    @listen("needs_revision")
    def revise(self):
        self.state.revision_count += 1
        self.write_article()  # Re-run writing with accumulated state

# Run the flow
flow = ContentPipelineFlow()
flow.kickoff()
```

The `@router` decorator enables branching — returning different string values routes execution to different `@listen` methods.

## Step 11: How to Add Memory and Context for Agent Persistence

CrewAI supports three memory layers that persist agent context across task executions. Short-term memory stores recent conversation context within a session. Long-term memory persists key facts and outcomes across sessions using SQLite. Entity memory tracks people, organizations, and concepts mentioned across tasks. All three are enabled with a single flag.

```python
@crew
def crew(self) -> Crew:
    return Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,
        memory=True,              # Enables all memory layers
        verbose=True,
        # Optional: customize memory storage
        memory_config={
            "provider": "mem0",  # Default: built-in SQLite
        }
    )
```

With memory enabled, a researcher agent that found "CrewAI has 49k stars" in one task will recall that fact in subsequent tasks without re-querying. For multi-session workflows (e.g., a daily report generator), long-term memory ensures agents build on previous runs rather than starting from scratch. The default SQLite storage is sufficient for development; for production, configure an external store like Mem0 or a PostgreSQL-backed solution.

## Step 12: Error Handling, Guardrails, and Production Considerations

Production CrewAI deployments need guardrails around three failure modes: LLM API errors (rate limits, timeouts), tool failures (network errors, invalid responses), and agent loops (agents that cycle without making progress). CrewAI provides built-in retry logic for API errors, but tool errors and agent loops require explicit handling.

```python
from crewai import Task
from typing import Tuple

def validate_research_output(result) -> Tuple[bool, str]:
    """Task guardrail - runs before output is passed to next task"""
    if len(result.raw) < 500:
        return (False, "Research output too short — retry with broader search terms")
    if "error" in result.raw.lower() and "source" not in result.raw.lower():
        return (False, "Output appears to be an error message — retry")
    return (True, "")  # (valid, error_message_if_invalid)

@task
def research_task(self) -> Task:
    return Task(
        config=self.tasks_config['research_task'],
        guardrail=validate_research_output,  # Validates output before proceeding
        max_retries=3                         # Retry up to 3 times if guardrail fails
    )
```

Additional production patterns:
- Set `max_iter=10` on agents to prevent infinite reasoning loops (default is 25)
- Use `cache=True` on agents to cache identical tool calls within a session
- Set task `async_execution=True` for tasks that can run in parallel
- Log `result.token_usage` to a database to track costs per crew run

## Step 13: How to Deploy CrewAI to Production with FastAPI

The simplest production deployment wraps the crew in a FastAPI endpoint. This gives you an HTTP API that downstream services can call, with async support for long-running crew executions.

```python
# api.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid, asyncio
from my_research_crew.crew import MyResearchCrew

app = FastAPI(title="Research Crew API")
jobs = {}  # In production, use Redis or a database

class ResearchRequest(BaseModel):
    topic: str
    
class JobStatus(BaseModel):
    job_id: str
    status: str
    result: str | None = None

@app.post("/research", response_model=JobStatus)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "result": None}
    background_tasks.add_task(run_crew, job_id, request.topic)
    return JobStatus(job_id=job_id, status="running")

async def run_crew(job_id: str, topic: str):
    try:
        result = await asyncio.to_thread(
            MyResearchCrew().crew().kickoff,
            inputs={"topic": topic}
        )
        jobs[job_id] = {"status": "complete", "result": result.raw}
    except Exception as e:
        jobs[job_id] = {"status": "failed", "result": str(e)}

@app.get("/research/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    job = jobs.get(job_id, {"status": "not_found", "result": None})
    return JobStatus(job_id=job_id, **job)
```

```bash
# Deploy with Docker
docker build -t research-crew .
docker run -p 8000:8000 --env-file .env research-crew
```

Use `asyncio.to_thread` to run the synchronous `kickoff()` call without blocking the FastAPI event loop.

## CrewAI vs LangGraph vs AutoGen: Which Framework Should You Use?

CrewAI, LangGraph, and AutoGen are the three dominant multi-agent frameworks in 2026, and they serve different use cases. The right choice depends on whether you prioritize simplicity, control, or conversation patterns.

| Feature | CrewAI | LangGraph | AutoGen |
|---|---|---|---|
| Paradigm | Role-based teams | Stateful graphs | Conversation agents |
| Config style | YAML + decorators | Python code graph | Python class hierarchy |
| Learning curve | Low | High | Medium |
| Flexibility | Medium | High | High |
| Built-in tools | Yes (crewai-tools) | Via LangChain | Via AutoGen tools |
| Memory | Built-in (3 layers) | Manual via state | Built-in (basic) |
| Flows/orchestration | Yes (Flows) | Native (it's a graph) | Nested chats |
| Best for | Structured workflows | Complex logic trees | R&D, conversational |
| GitHub stars (Apr 2026) | 49k | 11k | 38k |

**Choose CrewAI** when you have a well-defined workflow where different roles map to different agents — content pipelines, research automation, data analysis workflows. The YAML configuration and role-playing metaphor make it the easiest to onboard a team to.

**Choose LangGraph** when your workflow has complex conditional logic, cycles, or requires fine-grained control over state transitions. LangGraph is pure Python graph definition — no magic, no YAML — which makes debugging easier in complex scenarios.

**Choose AutoGen** when your use case involves ongoing conversations between agents (like a code review loop between a coder and reviewer) or when you're doing R&D that requires frequent configuration changes.

## Troubleshooting Common CrewAI Issues

**Agent produces empty or very short output:** Increase the `max_iter` parameter and add explicit length requirements to the task's `expected_output` field. Agents sometimes converge prematurely on simple answers.

**Tool not being used:** Check the tool description — the LLM decides which tool to use based on the description text alone. If the description doesn't match the task wording, the agent won't select it. Make descriptions specific.

**High token costs:** Enable agent-level caching (`cache=True`) to avoid repeat tool calls. Use a cheaper model for early research steps and a higher-quality model only for final synthesis.

**Rate limit errors:** Wrap your `kickoff()` call in a retry loop with exponential backoff, or configure `max_rpm` on the Crew object to throttle requests.

**"Agent stopped due to iteration limit":** The agent hit `max_iter` without completing the task. Increase `max_iter`, simplify the task description, or break one large task into two smaller tasks.

## Advanced Tips for Production CrewAI Systems

The following patterns separate proof-of-concept crews from production-grade systems:

**Use hierarchical process for parallel tasks.** When independent tasks can run simultaneously, switch from `Process.sequential` to `Process.hierarchical` and add a manager agent. CrewAI delegates tasks in parallel automatically.

**Version your YAML configs.** Treat `agents.yaml` and `tasks.yaml` like code — commit them to git, review changes in PRs. A one-word change in an agent backstory can significantly alter output quality.

**Build evaluation harnesses.** Create a small test dataset of `(input, expected_output_characteristics)` pairs and run your crew against it after every config change. CrewAI has no built-in eval tooling, so this is manual — but essential for production.

**Use structured outputs everywhere.** Even if you don't need machine-readable output, Pydantic models act as self-documenting contracts and catch model hallucinations early (e.g., an agent returning a list when your code expects a string).

**Instrument with LangSmith or Langfuse.** Add `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` to your `.env` to get full trace visibility into every agent decision and tool call. This is invaluable for debugging production issues.

## FAQ: Common Questions About Building with CrewAI

The following questions cover the most frequent issues developers encounter when learning CrewAI — from environment setup and cost management to async deployment and local model support. Each answer is self-contained so you can jump directly to the question relevant to your situation without reading the full tutorial. If your question isn't covered here, the official documentation at docs.crewai.com has comprehensive API references, and the GitHub Discussions tab has an active community answering framework-specific questions. CrewAI releases updates frequently (version 1.14.2 shipped in April 2026), so always check the changelog when upgrading to understand breaking changes in agent configuration or task output handling. Common stumbling points for new users include missing environment variables, agent outputs that are too short due to vague `expected_output` definitions, and rate limit errors when running multiple tool-heavy agents simultaneously. The answers below address each of these scenarios with concrete fixes you can apply immediately.

### What is CrewAI and how does it differ from LangChain?

CrewAI is a multi-agent orchestration framework where agents have defined roles, goals, and backstories and collaborate to complete tasks. It is built from scratch — not on top of LangChain — making it lighter and simpler to configure. LangChain is a lower-level toolkit for building LLM applications; CrewAI operates at a higher abstraction level specifically optimized for agent coordination.

### What Python version does CrewAI require?

CrewAI requires Python 3.10 or higher. The recommended versions are Python 3.12 or 3.13 for best compatibility with the latest package dependencies. Python 3.9 and below are not supported.

### Can I use CrewAI with local LLMs like Ollama?

Yes. Set `OPENAI_API_BASE=http://localhost:11434/v1` in your `.env` file and use model names prefixed with `ollama/` (e.g., `ollama/llama3.2`). Crew AI uses LiteLLM internally, so any provider supported by LiteLLM works. For local models, expect slower execution and potentially lower-quality reasoning compared to GPT-4o or Claude Sonnet.

### How much does running a CrewAI system cost?

Cost depends on the number of agents, task complexity, and chosen LLM. A simple two-agent research-and-write crew using GPT-4o typically costs $0.05–$0.20 per run. Using Claude Haiku for research and Claude Sonnet only for final writing can reduce costs by 60–70%. Enable agent caching to avoid paying for repeated tool call summaries within a session.

### Does CrewAI support async execution?

Crew AI's `kickoff()` method is synchronous. For async usage, wrap it in `asyncio.to_thread()` as shown in the FastAPI deployment step. CrewAI does support `async_execution=True` on individual tasks, which enables tasks without dependencies to run in parallel within a sequential process — but the overall `kickoff()` call still blocks until all tasks complete.