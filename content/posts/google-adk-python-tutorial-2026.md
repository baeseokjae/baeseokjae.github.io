---
cover:
  alt: 'Google ADK Tutorial: Build Multi-Agent Systems with Python'
  image: /images/google-adk-python-tutorial-2026.png
  relative: false
date: 2026-05-09 18:04:05+00:00
lastmod: 2026-10-31 16:16:02+00:00
description: 'Google ADK Python tutorial re-verified against google-adk 2.13.0: the install that resolves, the Python 3.11+ floor, all 29 declared extras, sequential and parallel pipelines, and which tool errors ADK returns versus raises.'
draft: false
schema: schema-google-adk-python-tutorial-2026
tags:
- Google ADK
- multi-agent systems
- Python
- AI agents
- Gemini
title: 'Google ADK Python Tutorial 2026: Install 2.13.0 and Handle Tool Failures'
---

Google ADK (Agent Development Kit) is Google's open-source, code-first Python framework for building, evaluating and deploying agents, and installing it is still a single command. The problem is not the command — it is that a tutorial drifts out of date silently: the package moves, an import path disappears, and the snippet you copied stops working without telling you why. This edition was re-checked on 2026-10-31 against the release that `pip install google-adk` resolves today. The install, the imports, the agent construction, the session-service wiring and the tool boundary below were executed on that release in this pass. Two things were not. The scaffold CLI commands (`adk create`, `adk run`, `adk web`) were never run here, so their flags, file lists and directory notes are taken from Google's documentation. And of the Runner snippet below, only the session creation, the `Runner` construction and the `run` signature were exercised — that snippet is written for this tutorial, not quoted, and its model turn was never executed. Both limits are labelled where they appear.

Google's repository describes the framework as "an open-source, code-first Python framework for building, evaluating, and deploying sophisticated AI agents with flexibility and control" ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)), and the same README states the requirement plainly: **Requirements:** Python 3.11+.

## What this revision changes, and what it refuses to claim

- **The verified version moves from 2.12.0 to 2.13.0.** PyPI carries 2.13.0, uploaded 2026-10-23, and the recorded check on 2026-10-31 resolved exactly that release. The previous edition's evidence directory stays in the repository; this edition's raw output is under `refresh-2026-10-31/`.
- **The declared extras count moved from 28 to 29.** `otel` is new in this release and is listed below, read from the installed distribution's own metadata. There is still no `vertexai` extra, so `pip install google-adk[vertexai]` remains dead advice.
- **A tool-failure section was added.** The page now states which tool errors ADK turns into a result the model can see, and which ones abort the call — checked by invoking `FunctionTool.run_async` directly, with no model in the loop.
- **Earlier corrections are retained, not re-litigated:** the Python 3.11+ floor, the removed `A2AServer`/`A2AClient` names, the Workflow supersession of `SequentialAgent`/`ParallelAgent`, and the withdrawal of the May 2026 market-size statistics that no dated first-party source supported.
- **What this revision does not claim:** no Gemini or Vertex model call was made (no credential in this run), no optional extra was installed, and no pipeline was executed. Version numbers, import outcomes, construction results and tool-boundary behaviour are what the check covers; latency, answer quality and live agent behaviour are not.

## What Google ADK is in October 2026

The repository's own feature list leads with the **Workflow Runtime**, "a graph-based execution engine for composing deterministic execution flows for agentic apps", followed by a Task API for agent-to-agent delegation, modular multi-agent composition, the tool ecosystem (custom functions, OpenAPI specs, MCP tools) and "Deploy Anywhere" containers on Cloud Run or Vertex AI Agent Engine ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). That ordering matters if you are following an older tutorial: the tree-of-agents story those pages lead with is now the compatibility layer, not the headline.

Version and cadence: the release that `pip install google-adk` resolved on 2026-10-31 is **google-adk 2.13.0**, uploaded 2026-10-23T18:26:31Z, and the same metadata document counts 98 releases for this package ([PyPI JSON API for google-adk](https://pypi.org/pypi/google-adk/json)). A tutorial that pins nothing is guaranteed to drift, which is why this page keeps `pip show` in the install sequence and does not pretend the version it saw is the version you will get.

Documentation host: the canonical docs live at **adk.dev**. Any `google.github.io/adk-docs` link you have bookmarked is the old host and should be treated as stale.

**This page is the install-and-run Python tutorial, and it does not replace these pages on the same site.** For the conceptual walkthrough see [Google ADK Tutorial 2026](https://baeseokjae.github.io/posts/google-adk-tutorial-2026/); for orchestration patterns at scale see [the multi-agent guide](https://baeseokjae.github.io/posts/google-adk-multi-agent-guide-2026/); for the protocol itself see [the A2A protocol guide](https://baeseokjae.github.io/posts/google-adk-a2a-protocol-guide-2026/); for the JavaScript/TypeScript bindings see [the TypeScript guide](https://baeseokjae.github.io/posts/google-adk-typescript-guide-2026/); for framework selection see [ADK vs LangGraph vs Mastra](https://baeseokjae.github.io/posts/google-adk-vs-langgraph-vs-mastra-2026/) and [ADK vs LangGraph vs CrewAI](https://baeseokjae.github.io/posts/google-adk-vs-langgraph-vs-crewai-2026/).

## Install Google ADK the way that actually resolves (Python 3.11+)

Google's [Python quickstart](https://adk.dev/get-started/python/index.md) opens with a prerequisites list that still reads `- Python 3.10 or later`, and the [installation page](https://adk.dev/get-started/installation/index.md) gives the commands below. The package disagrees with the first statement: the installed distribution reports `Requires-Python: >=3.11`, and the repository's `pyproject.toml` contains `requires-python = ">=3.11"` ([pyproject.toml](https://raw.githubusercontent.com/google/adk-python/main/pyproject.toml)). Use 3.11 or newer — on 3.10 the install you are told to run is not the install you will get.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install google-adk
pip show google-adk
adk --version
```

On the recorded check for this refresh, that sequence resolved **google-adk 2.13.0** alongside **google-genai 2.34.0** on Python 3.12.3 (Linux aarch64), `pip show google-adk` printed `Version: 2.13.0`, and `adk --version` printed `adk, version 2.13.0`. Both command outputs are in [local-run-pip-resolve.log](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-pip-resolve.log) (lines 13–25), and the machine-readable metadata read from the same install (`distribution.version`, `google_genai`) is in [local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json); a later resolution of a newer release is expected, which is exactly why `pip show` is in the sequence.

For a reproducible install, the README recommends the companion constraint files rather than a bare unpinned install: `pip install google-adk -c constraints-3.11.txt`, with one file published for each Python version from 3.11 to 3.15 ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). That is the pin to use in CI; the unpinned form stays in this tutorial because the point of the page is to show what a reader's first `pip install` actually gets.

### The extras that exist in 2.13.0 (there is no `vertexai` extra)

`pip install google-adk[vertexai]` appeared in this tutorial's earlier editions. It does not resolve to anything: the distribution declares 29 extras and `vertexai` is not one of them. Read verbatim from the installed package metadata:

```text
a2a, agent-identity, all, antigravity, benchmark, bigquery-analytics, community,
daytona, db, dev, docs, e2b, elevenlabs, eval, extensions, gcp, livekit, mcp,
mongodb, oci, openai, opensandbox, otel, otel-gcp, redis, slack, test, toolbox, tools
```

The ones a Python tutorial reader is likely to want are `a2a` for Agent-to-Agent exposure, `gcp` for Google Cloud integrations and Agent Engine deployment, `mcp` for MCP servers, `openai` for non-Gemini model providers, and `extensions` — the README's own example is `pip install "google-adk[extensions]"`. Note the honest caveat: this pass installed only the base package, so the dependency resolution of these extras is **unverified**; the names and their declared contents come from the package's metadata and `pyproject.toml`, not from an install.

### Create the project skeleton

The current quickstart scaffolds a project instead of asking you to create files by hand: `adk create my_agent` produces `my_agent/agent.py`, `my_agent/.env` for keys and project ids, and `my_agent/__init__.py`, and `agent.py` must expose a `root_agent` ([Python quickstart](https://adk.dev/get-started/python/index.md)). That scaffold was **not** run in this refresh — it writes files and, on first use, prompts for configuration — so treat the file list as documentation rather than observed output.

Where to run the CLI from is stated in the quickstart for one command only: the `adk web` step ends with "Run this command from the **parent directory** that contains your `my_agent/` folder. For example, if your agent is inside `agents/my_agent/`, run `adk web` from the `agents/` directory." The `adk run my_agent` step on the same page carries no such note, and neither command was executed here.

## Your first LlmAgent

An `LlmAgent` takes a name, a model, an instruction, and tools. Plain Python functions become tools: ADK reads the function signature for the parameter schema and the docstring for the description, so no decorator boilerplate is needed.

```python
# my_agent/tools.py
def read_file(file_path: str) -> dict:
    """Read a file and return its contents."""
    try:
        with open(file_path) as f:
            return {"status": "success", "content": f.read()}
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {file_path}"}
```

```python
# my_agent/agent.py
from google.adk.agents.llm_agent import Agent
from .tools import read_file

root_agent = Agent(
    name="code_reviewer",
    model="gemini-flash-latest",
    description="Reviews Python code for quality and style issues",
    instruction=(
        "You are a senior Python developer doing code review. When given a file "
        "path, read the file and summarize the issues you find, grouped by severity."
    ),
    tools=[read_file],
)
```

**About that model id.** `gemini-flash-latest` is the value printed in Google's own Python quickstart ([adk.dev Python quickstart](https://adk.dev/get-started/python/index.md)), while the repository README uses `model="gemini-3.5-flash"` ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). No model call was executed in this refresh — there was no API credential in the run — so this page does not assert which id is current for your project. Confirm it against the model configuration page the quickstart links, and prefer the `-latest` alias if you do not want to chase version bumps.

## Sequential agents: ordered pipelines (and the Workflow supersession)

Google's [sequential agents page](https://adk.dev/agents/workflow-agents/sequential-agents/index.md) describes `SequentialAgent` as a workflow agent that runs its sub-agents in the order you list them, with no model deciding the sequence and with one shared invocation context, so the children share session state. The same page now carries a banner that changes how you should read this section:

> Starting in ADK 2.0 for Python and Go, templated workflows have been superseded by more flexible workflow structures, including graph-based workflows and dynamic workflows.

Both classes still work in 2.13.0, and the interpreter tells you they are on the way out. Constructing a `SequentialAgent` emits, verbatim, `DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.` The second sentence is the practically important part: if you are building an `LlmAgent` that delegates to a sub-agent, you cannot simply swap `SequentialAgent` for `Workflow` yet. The full warning text, captured from the recorded run, is in [local-run-stderr.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-stderr.txt).

A minimal ordered pipeline therefore stays useful: each `LlmAgent` writes its reply into session state under `output_key`, and the next stage reads that key inside its instruction.

```python
# pipeline/agent.py
from google.adk.agents import LlmAgent, SequentialAgent

analyzer = LlmAgent(
    name="code_analyzer",
    model="gemini-flash-latest",
    instruction="Analyze the file at the path in state key 'file_path'. Report complexity, naming and error handling.",
    output_key="analysis",
)
suggester = LlmAgent(
    name="improvement_suggester",
    model="gemini-flash-latest",
    instruction="Read 'analysis' from state and give five actionable improvements.",
    output_key="suggestions",
)
reporter = LlmAgent(
    name="report_writer",
    model="gemini-flash-latest",
    instruction="Using 'analysis' and 'suggestions' from state, write a Markdown review report.",
    output_key="final_report",
)

root_agent = SequentialAgent(
    name="code_review_pipeline",
    description="Analyze, suggest, report",
    sub_agents=[analyzer, suggester, reporter],
)
```

Constructing exactly that shape — a two-child sequential, a two-child parallel, and a nested parallel-inside-sequential tree — succeeded in the recorded run, and the resulting child lists were read back and matched the definitions (`['c1','c2']`, `['p1','p2']`, `['inner','synth']`) ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)). What was **not** verified is execution order or state passing, because that needs a model call. Construction, imports and the deprecation surface are what this refresh checked.

## Parallel agents: concurrent subtasks without key collisions

`ParallelAgent` runs its sub-agents concurrently and is documented for independent, resource-intensive work such as multi-source retrieval ([parallel agents](https://adk.dev/agents/workflow-agents/parallel-agents/index.md)). Two constraints from that page drive the code you write:

1. Each sub-agent must be able to run without depending on its siblings: the page says "it is important that each sub-agent can operate without depending on the other sub-agents", because the branches do not automatically share conversation history or state.
2. Result order is not guaranteed, so anything that needs a deterministic merge must be done downstream.

```python
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search

docs = LlmAgent(name="docs_researcher", model="gemini-flash-latest",
                instruction="Research the topic in the official docs.",
                tools=[google_search], output_key="docs_findings")
issues = LlmAgent(name="issues_researcher", model="gemini-flash-latest",
                  instruction="Research the topic in issue trackers.",
                  tools=[google_search], output_key="issues_findings")

fan_out = ParallelAgent(name="parallel_researcher", sub_agents=[docs, issues])
synth = LlmAgent(name="synthesizer", model="gemini-flash-latest",
                 instruction="Merge 'docs_findings' and 'issues_findings' into one answer.",
                 output_key="final_answer")

root_agent = SequentialAgent(name="research_pipeline", sub_agents=[fan_out, synth])
```

`from google.adk.tools import google_search` and `from google.adk.agents.sequential_agent import SequentialAgent` both imported cleanly in the recorded check, alongside the package-level forms `from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)).

**A correction to the usual advice about `output_key`.** Earlier editions of this page said two parallel children sharing an `output_key` "causes a race condition". They collide, but the framework does not stop you: a `ParallelAgent` whose two children both declare `output_key="result"` constructed without an error in the recorded run, and the child keys read back as `['result','result']` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)). The hazard is a silent data overwrite at run time, not a validation error at import time — which is why unique keys matter more than the old wording implied. Use distinct keys (`docs_findings`, `issues_findings`) and merge downstream, as above.

## Handling tool failures: what ADK catches and what it does not

This is the part most tutorials skip, and it is the part that decides whether a production agent degrades gracefully or dies mid-turn. ADK derives a tool's parameter schema from your function; it does not enforce that schema on the way in, and it does not wrap your exceptions.

**The schema is generated, not declared.** For the `read_file(file_path: str)` function above, `FunctionTool(read_file)._get_declaration()` produced a declaration whose `parameters_json_schema` has `properties.file_path.type = "string"`, `required: ["file_path"]`, and the docstring `"Read a file and return its contents."` as the description ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)). That declaration is what a model backend is shown; it is not a runtime validator.

**A missing mandatory argument is caught for you.** Calling `run_async(args={})` on that tool did not raise. It returned an error object containing, verbatim:

```text
Invoking `read_file()` failed as the following mandatory input parameters are not present:
file_path
You could retry calling this tool, but it is IMPORTANT for you to provide all the mandatory parameters.
```

That string is the framework complaining, and it is the kind of message a model can read and retry from.

**An exception inside the tool body is not caught.** The same tool, called with a path that does not exist, raised `FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/definitely-missing.txt'` out of `run_async` instead of returning a tool result ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)). If your tool opens sockets, parses untrusted input or calls an API, an unhandled exception aborts the call rather than becoming something the agent can recover from.

**The schema is not a coercion step.** Passing `123` for a `str` parameter reached the Python body unchanged — `open(123)` produced `OSError: [Errno 9] Bad file descriptor`. Whatever the model emits, your function receives; validate types yourself.

The practical pattern is therefore to catch inside the tool and return a structured error, exactly as the `read_file` example at the top of this page does:

```python
def read_file(file_path: str) -> dict:
    """Read a file and return its contents."""
    if not isinstance(file_path, str):
        return {"status": "error", "error": "file_path must be a string path"}
    try:
        with open(file_path, encoding="utf-8") as f:
            return {"status": "success", "content": f.read()}
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {file_path}"}
    except OSError as exc:
        return {"status": "error", "error": f"Could not read {file_path}: {exc}"}
```

Returning an error object keeps the turn alive and hands the model something actionable; letting the exception escape ends it. The limit of this evidence: it comes from direct `FunctionTool.run_async(..., tool_context=None)` calls on 2.13.0, with no model and no `Runner` in the loop, so it describes the tool boundary rather than model-side validation. A full Runner-driven run needs a credential and was not attempted here.

## Running agents: Runner, sessions and the dev UI

`adk run my_agent` gives an interactive terminal session and `adk web --port 8000` starts a browser UI at `http://localhost:8000`; both are documented commands, and neither was run in this refresh. Google is explicit about the boundary: "ADK Web is ***not meant for use in production deployments***. You should use ADK Web for development and debugging purposes only." ([Python quickstart](https://adk.dev/get-started/python/index.md)).

In code, a session service and a runner drive the agent; every import in the snippet below resolved in the recorded check, including `from google.genai.types import Content, Part` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)). What the imports do not tell you is that session creation is asynchronous in 2.13.0, which is where the previous version of this snippet broke.

```python
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part


async def main() -> None:
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name="code_review", session_service=session_service)
    session = await session_service.create_session(
        app_name="code_review", user_id="dev_user", state={"file_path": "my_module.py"}
    )
    for event in runner.run(
        user_id="dev_user",
        session_id=session.id,
        new_message=Content(parts=[Part(text="Review the file.")]),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)


asyncio.run(main())
```

**The `await` is not optional.** `InMemorySessionService.create_session` is declared `async def` in 2.13.0 (`google/adk/sessions/in_memory_session_service.py`), so the un-awaited call returns a coroutine object and `session.id` raises, verbatim, `AttributeError: 'coroutine' object has no attribute 'id'` — reproduced, then fixed, in the correction pass. With the `await`, `create_session` returned a session whose `id` was `3fcb86b1-e2b3-4e80-9881-998e486e2ea9` and whose state read back as `{'file_path': 'my_module.py'}` from a second `get_session` call; `Runner(agent=..., app_name='code_review', session_service=...)` constructed alongside it. Two details worth knowing before you go looking for a synchronous escape hatch: `create_session_sync` exists and also returns a session object, but it prints `Deprecated. Please migrate to the async method.` to stderr; and `Runner.run` is a plain generator (`-> Generator[Event, None, None]`), not a coroutine, so it is iterated normally inside the async function. The raw JSON of that pass, including the failing and the corrected call, is [session-api-check.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/session-api-check.json).

What is still unverified here is the loop body's output: iterating `runner.run` to a final response needs a model credential, which this refresh did not have, so the session wiring and the generator shape are checked and the model turn is not.

## Exposing agents over A2A (updated entry point)

The A2A section of this tutorial used to wrap an agent in `A2AServer` and call remote agents with `A2AClient`. Neither name survives: `from google.adk.a2a import A2AServer` fails with `ImportError: cannot import name 'A2AServer' from 'google.adk.a2a'`, and `A2AClient` fails the same way ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)).

The documented replacement is a function, not a server class: "You can take an existing agent built using ADK and make it A2A-compatible by simply wrapping it using the `to_a2a()` function" ([A2A quickstart: exposing](https://adk.dev/a2a/quickstart-exposing/index.md)).

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

a2a_app = to_a2a(root_agent, port=8001)   # serves the agent card for you
```

Two operational details from the same page: `to_a2a()` auto-generates the agent card in memory, and the alternative path is to host your own `agent.json` card with `adk api_server --a2a`, which keeps `adk web` usable for debugging. The page also states that ADK's A2A integration works with both `a2a-sdk` 0.3.x and 1.x.x, detects the installed SDK version automatically, and recommends targeting 1.x.x for new integrations ([A2A quickstart: exposing](https://adk.dev/a2a/quickstart-exposing/index.md)).

**The import requires an extra, and the base install does not have it.** On the recorded check's base install, `from google.adk.a2a.utils.agent_to_a2a import to_a2a` raised `ModuleNotFoundError: No module named 'a2a'`; `pyproject.toml` declares the SDK only inside the extra — `a2a-sdk[http-server]>=0.3.4,<2` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json), [pyproject.toml](https://raw.githubusercontent.com/google/adk-python/main/pyproject.toml)). Install it with `pip install "google-adk[a2a]"` before copying any A2A snippet. That extra was not installed in this pass, so the end-to-end serving path is unverified here; [the A2A protocol guide](https://baeseokjae.github.io/posts/google-adk-a2a-protocol-guide-2026/) covers the protocol itself.

## Deployment: where to go after the tutorial

The earlier deployment section on this page called `pip install google-cloud-aiplatform[adk,reasoningengine]` and `vertexai.preview.reasoning_engines.AdkApp`. That path is outside what this refresh checked, and the package metadata now points Google Cloud users at a different distribution: the `gcp` extra declares `google-cloud-agentplatform[agent_engines]>=2.2,<3` ([pyproject.toml](https://raw.githubusercontent.com/google/adk-python/main/pyproject.toml)). Rather than restate an unverified snippet, this page points at the deployment commands the repository documents today ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)):

```bash
adk deploy docker --with_ui <agent-folder>
adk deploy cloud_run --with_ui <agent-folder>
```

`adk --help` in the recorded environment lists a `deploy` subcommand described as "Deploys agent to hosted environments", so the CLI surface exists locally; the deploy itself was not run, because that needs a Google Cloud project and credentials. The captured help text is [adk-help.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/adk-help.txt). For the framework-selection question — whether ADK, LangGraph or Mastra is the right runtime for your workload — see the site's comparison pages linked near the top.

## How the local check was run, and what it does not cover

Everything labelled as verified above comes from one bounded, re-runnable check in an isolated virtual environment under a private per-run scratch directory (Python 3.12.3, Linux aarch64), with the exact commands and timestamps recorded in [write-check-record.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/write-check-record.json). The sequence was `python3 -m venv venv`, `pip install --upgrade pip`, the unpinned `pip install google-adk` this tutorial shows, then a script that (a) reads the resolved version, `Requires-Python` and every declared extra from the installed metadata, (b) executes each import statement the tutorial prints, one at a time, recording the exception text when it fails, (c) constructs the sequential, parallel and nested shapes and reads the child lists back, and (d) derives a tool declaration and invokes the tool with a missing file, a wrong-typed argument and a missing required argument. The script is published as [verify_tutorial_commands.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/verify_tutorial_commands.py) and can be re-run against any later release; the pip resolution log is [local-run-pip-resolve.log](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-pip-resolve.log).

A second, narrower pass ran after review on the same date, in a fresh venv with that same release pinned (`pip install google-adk==2.13.0`) so the session API could be probed without a resolution change: [session_api_check.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/session_api_check.py) reproduced the un-awaited `create_session` failure, ran the corrected async form, read the session back and probed the sync shim, producing [session-api-check.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/session-api-check.json); [adk-help.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/adk-help.txt) is that pass's capture of `adk --help`. Commands, timestamps and artifact hashes for both passes are recorded in [correction-pass-record.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/correction-pass-record.json).

The limits, stated so you can judge the claims: **no model call was made** (no API credential in this run), so nothing here is a claim about agent behaviour, latency, output quality, or the correctness of the model ids; `adk create`, `adk run` and `adk web` were not executed, so the scaffold file list and the CLI run behaviour are documentation, not observed output; the optional extras (`a2a`, `gcp`, `all`, `otel`) were **not** installed, so their dependency resolution is unverified; and the install was unpinned, so a later `pip install google-adk` may resolve a different version with different import results. This is an author-side check of installation, imports, construction, the session API and the tool boundary — not a benchmark of the framework and not a vendor claim. The raw files live in the same evidence directory and are linked where each one is used.

## FAQ

### How do I install Google ADK in Python?

On Python 3.11 or newer, run `pip install google-adk`, then confirm with `pip show google-adk` and `adk --version`. The docs' installation page gives the same command with a virtual environment ([installation](https://adk.dev/get-started/installation/index.md)); the recorded run resolved google-adk 2.13.0 and printed `adk, version 2.13.0` ([local-run-pip-resolve.log](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-pip-resolve.log), lines 13–25).

### Does Google ADK need Python 3.10 or 3.11?

Use 3.11+: the installed distribution declares `Requires-Python: >=3.11` and the repository README states "Python 3.11+" ([PyPI JSON for google-adk](https://pypi.org/pypi/google-adk/json), [google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). The [Python quickstart](https://adk.dev/get-started/python/index.md) still lists 3.10 or later, so the docs page and the package currently disagree.

### What is the difference between LlmAgent and SequentialAgent?

An `LlmAgent` is the reasoning primitive: it calls a model and decides which tools to use. A `SequentialAgent` is a template workflow agent with no model of its own — it runs its children in the order given, deterministically, sharing one invocation context and session state between them ([sequential agents](https://adk.dev/agents/workflow-agents/sequential-agents/index.md)).

### Are SequentialAgent and ParallelAgent deprecated in Google ADK?

They are documented as superseded starting in ADK 2.0 for Python and Go, in favour of graph-based and dynamic workflows ([sequential agents](https://adk.dev/agents/workflow-agents/sequential-agents/index.md), [parallel agents](https://adk.dev/agents/workflow-agents/parallel-agents/index.md)), and constructing either one emits `DeprecationWarning: ... is deprecated in favor of Workflow and will be removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.` Both still import and construct in 2.13.0 ([local-run-stderr.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-stderr.txt)).

### Why does `from google.adk.a2a import A2AServer` fail?

Because that name no longer exists: the import raises `ImportError: cannot import name 'A2AServer' from 'google.adk.a2a'`. Expose an agent with `to_a2a()` from `google.adk.a2a.utils.agent_to_a2a` and install the `a2a` extra first — without it the import fails with `ModuleNotFoundError: No module named 'a2a'` ([A2A quickstart: exposing](https://adk.dev/a2a/quickstart-exposing/index.md), [local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)).

### Why did my ADK tool exception abort the agent turn?

Because ADK only synthesises a tool result for arguments it can see are missing; it does not catch exceptions raised inside your function. In the recorded check, an omitted mandatory argument came back as a tool-result error the model could retry from, while a `FileNotFoundError` raised inside the tool body propagated out of `FunctionTool.run_async` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/refresh-2026-10-31/local-run-verify-output.json)). Catch expected exceptions in the tool and return a structured error dict.
