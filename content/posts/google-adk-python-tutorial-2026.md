---
cover:
  alt: 'Google ADK Tutorial: Build Multi-Agent Systems with Python'
  image: /images/google-adk-python-tutorial-2026.png
  relative: false
date: 2026-05-09 18:04:05+00:00
lastmod: 2026-10-15 00:00:00+00:00
description: 'Google ADK Python tutorial refreshed against google-adk 2.12.0: the install command that resolves, verified import paths, working sequential and parallel agent pipelines, the Workflow deprecation, and A2A exposure with to_a2a().'
draft: false
schema: schema-google-adk-python-tutorial-2026
tags:
- Google ADK
- multi-agent systems
- Python
- AI agents
- Gemini
- Vertex AI
title: 'Google ADK Python Tutorial 2026 (refreshed): Install, Sequential and Parallel Agents With Verified Package Names'
---

Google ADK (Agent Development Kit) is Google's open-source, code-first Python framework for building, evaluating and deploying agents, and installing it is still a single command. The problem is not the command — it is that a tutorial written in July 2026 tells you to install a package that has moved on, and its copy-paste surface stops working silently rather than loudly. This edition was re-verified end to end on 2026-10-15 against the release that `pip install google-adk` actually resolves today, and every instruction below either runs on that release or is labelled as something this pass could not check.

Google's repository describes the framework as "an open-source, code-first Python framework for building, evaluating, and deploying sophisticated AI agents with flexibility and control" ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)), and the same README states the requirement plainly: **Requirements:** Python 3.11+.

## What this revision changes, and what it refuses to claim

- **Python floor corrected to 3.11+.** The package metadata declares `Requires-Python: >=3.11` while the documentation page still says "Python 3.10 or later"; see [Install Google ADK the way that actually resolves](#install-google-adk-the-way-that-actually-resolves-python-311).
- **`pip install google-adk[vertexai]` removed.** No `vertexai` extra exists in google-adk 2.12.0. The real extras are listed below, read from the installed distribution's own metadata.
- **The A2A section was rewritten.** `from google.adk.a2a import A2AServer` and `A2AClient` raise `ImportError` on 2.12.0. The current documented entry point is `to_a2a()`, and it needs the `a2a` extra.
- **SequentialAgent and ParallelAgent are now documented as deprecated** in favour of the Workflow runtime, even though both still import and construct. The page says so instead of presenting them as the framework's primary orchestration primitives.
- **Hard-coded model ids were replaced.** The old `gemini-2.0-flash` strings are gone. No model call was made in this pass, so the page shows the ids Google's own docs and repository currently print and tells you to confirm the one you pay for.
- **The `vertexai.preview.reasoning_engines` deployment snippet was dropped** as unverified, and replaced with the deployment commands the current README documents.
- **Unattributed statistics from the May 2026 version were removed, not restated.** This page previously carried market-size and vendor-adoption figures that neither this pass nor the earlier one could tie to a dated first-party source. Unverifiable numbers are not refreshed; they are withdrawn.

## What Google ADK is in October 2026

The framework's own feature list leads with the **Workflow Runtime**, "a graph-based execution engine for composing deterministic execution flows for agentic apps, with support for routing, fan-out/fan-in, loops, retry, state management, dynamic nodes, human-in-the-loop, and nested workflows", followed by a Task API for agent-to-agent delegation, modular multi-agent composition, the tool ecosystem (custom functions, OpenAPI specs, MCP tools) and "Deploy Anywhere" containers on Cloud Run or Vertex AI Agent Engine ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). That ordering matters for anyone following an older tutorial: the tree-of-agents story this page used to lead with is now the compatibility layer, not the headline.

Version and cadence: the release that `pip install google-adk` resolved on 2026-10-15 is **google-adk 2.12.0**, uploaded 2026-10-13T16:42:55Z, and the README describes the release cadence as "roughly bi-weekly" ([PyPI JSON API for google-adk](https://pypi.org/pypi/google-adk/json)). The same metadata document lists 97 releases for this package, so a tutorial that pins nothing is guaranteed to drift.

Documentation host: the canonical docs now live at **adk.dev**. The index still served from the old host lists every page under the new one — the line `- [Installation](https://adk.dev/get-started/installation/index.md)` is a literal entry in [google.github.io/adk-docs/llms.txt](https://google.github.io/adk-docs/llms.txt) — so treat any `google.github.io/adk-docs` link you have bookmarked as stale.

**This page is the install-and-run Python tutorial, and it does not replace these pages on the same site.** For the conceptual walkthrough see [Google ADK Tutorial 2026](https://baeseokjae.github.io/posts/google-adk-tutorial-2026/); for orchestration patterns at scale see [the multi-agent guide](https://baeseokjae.github.io/posts/google-adk-multi-agent-guide-2026/); for the protocol itself see [the A2A protocol guide](https://baeseokjae.github.io/posts/google-adk-a2a-protocol-guide-2026/); for the JavaScript/TypeScript bindings see [the TypeScript guide](https://baeseokjae.github.io/posts/google-adk-typescript-guide-2026/); for framework selection see [ADK vs LangGraph vs Mastra](https://baeseokjae.github.io/posts/google-adk-vs-langgraph-vs-mastra-2026/) and [ADK vs LangGraph vs CrewAI](https://baeseokjae.github.io/posts/google-adk-vs-langgraph-vs-crewai-2026/).

## Install Google ADK the way that actually resolves (Python 3.11+)

Google's [Python quickstart](https://adk.dev/get-started/python/index.md) opens with a prerequisites list that still reads `- Python 3.10 or later`, and the [installation page](https://adk.dev/get-started/installation/index.md) gives the two commands below. The package disagrees with the first of those statements: the installed distribution reports `Requires-Python: >=3.11`, the repository's `pyproject.toml` contains `requires-python = ">=3.11"` ([pyproject.toml](https://raw.githubusercontent.com/google/adk-python/main/pyproject.toml)), and the README says Python 3.11+. Use 3.11 or newer — on 3.10 the install you are told to run is not the install you will get.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install google-adk
pip show google-adk
adk --version
```

On the recorded check for this refresh, that sequence resolved **google-adk 2.12.0** alongside **google-genai 2.31.0** on Python 3.12.3 (Linux aarch64), `pip show google-adk` printed `Version: 2.12.0`, and `adk --version` printed `adk, version 2.12.0`. The raw output is kept at [local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json); a later resolution of a newer release is expected, which is exactly why `pip show` is in the sequence.

For a reproducible install, the README recommends the companion constraint files rather than a bare unpinned install: `pip install google-adk -c constraints-3.11.txt`, with a per-version file published for Python 3.11 through 3.15 ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)).

### The extras that exist in 2.12.0 (there is no `vertexai` extra)

`pip install google-adk[vertexai]` was in this tutorial's earlier editions. It does not resolve to anything: the distribution declares 28 extras and `vertexai` is not one of them. Read verbatim from the installed package metadata:

```text
a2a, agent-identity, all, antigravity, benchmark, bigquery-analytics, community,
daytona, db, dev, docs, e2b, elevenlabs, eval, extensions, gcp, livekit, mcp,
mongodb, oci, openai, opensandbox, otel-gcp, redis, slack, test, toolbox, tools
```

The ones a Python tutorial reader is likely to want are `a2a` for Agent-to-Agent exposure, `gcp` for Google Cloud integrations and Agent Engine deployment, `mcp` for MCP servers, `openai` for non-Gemini model providers, and `extensions` — the README's own example is `pip install "google-adk[extensions]"`. Note the honest caveat: this pass installed only the base package, so the dependency resolution of these extras is **unverified**; the names and their declared contents come from the package's metadata and `pyproject.toml`, not from an install.

### Create the project skeleton

The current quickstart scaffolds a project instead of asking you to create files by hand: `adk create my_agent` produces `my_agent/agent.py` (the agent definition), `my_agent/.env` for keys and project ids, and `my_agent/__init__.py` ([Python quickstart](https://adk.dev/get-started/python/index.md)). `agent.py` must expose a `root_agent`. The CLI discovers agents relative to the directory you run it from, so run `adk run my_agent` and `adk web --port 8000` from the **parent** directory that contains `my_agent/`.

## Your first LlmAgent

An `LlmAgent` takes a name, a model, an instruction, and tools. Plain Python functions become tools: ADK reads the docstring as the tool description and the type annotations as the parameter schema, so no decorator boilerplate is needed.

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

**About that model id.** `gemini-flash-latest` is the value printed in Google's own Python quickstart ([adk.dev Python quickstart](https://adk.dev/get-started/python/index.md)); the sequential and parallel agent pages use `GEMINI_MODEL = "gemini-2.5-flash"` ([parallel agents](https://adk.dev/agents/workflow-agents/parallel-agents/index.md)) and the repository README uses `model="gemini-3.5-flash"` ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). Three first-party pages, three values. No model call was executed in this refresh — there was no API credential in the run — so this page does not assert which id is current for your project. Confirm it against the docs' model configuration page that the quickstart links, and prefer the `-latest` alias if you do not want to chase version bumps.

## Sequential agents: ordered pipelines (and the Workflow deprecation)

The docs describe `SequentialAgent` as a template workflow agent "that executes its sub-agents in the order they are specified in a list", with execution that "is not controlled by an AI model, and is deterministic", and note that the children share the same `InvocationContext` and therefore the same session state ([sequential agents](https://adk.dev/agents/workflow-agents/sequential-agents/index.md)). The same page carries a banner that changes how you should read this section:

> Starting in ADK 2.0 for Python and Go, templated workflows have been superseded by more flexible workflow structures, including graph-based workflows and dynamic workflows.

Both classes still work in 2.12.0 and the interpreter tells you they are on the way out. Constructing a `SequentialAgent` emits, verbatim, `DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.` The second sentence is the practically important part: if you are building an `LlmAgent` that delegates to a sub-agent, you cannot simply swap `SequentialAgent` for `Workflow` yet. The full warning text, captured from the recorded run, is in [local-run-stderr.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-stderr.txt).

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

Constructing exactly that shape — two-child sequential, two-child parallel, and a nested parallel-inside-sequential tree — succeeded in the recorded run, and the resulting child lists were read back and matched the definitions ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)). What was **not** verified is execution order or state passing, because that needs a model call. Construction, imports and the deprecation surface are what this refresh checked.

## Parallel agents: concurrent subtasks without key collisions

`ParallelAgent` "executes its sub-agents concurrently" and is documented for independent, resource-intensive work such as multi-source retrieval ([parallel agents](https://adk.dev/agents/workflow-agents/parallel-agents/index.md)). Two constraints from that page drive the code you write:

1. Each sub-agent must be able to run without depending on its siblings: "it is important that each sub-agent can operate without depending on the other sub-agents", because the branches do not automatically share conversation history or state.
2. Result order is not guaranteed, so anything that needs a deterministic merge must be done downstream.

```python
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search

docs = LlmAgent(name="docs_researcher", model="gemini-flash-latest",
                instruction="Research {topic} in the official docs.",
                tools=[google_search], output_key="docs_findings")
issues = LlmAgent(name="issues_researcher", model="gemini-flash-latest",
                  instruction="Research {topic} in issue trackers.",
                  tools=[google_search], output_key="issues_findings")

fan_out = ParallelAgent(name="parallel_researcher", sub_agents=[docs, issues])
synth = LlmAgent(name="synthesizer", model="gemini-flash-latest",
                 instruction="Merge 'docs_findings' and 'issues_findings' into one answer.",
                 output_key="final_answer")

root_agent = SequentialAgent(name="research_pipeline", sub_agents=[fan_out, synth])
```

`from google.adk.tools import google_search` and `from google.adk.agents.sequential_agent import SequentialAgent` both imported cleanly in the recorded check, alongside the package-level forms `from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent` ([extra-imports.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/extra-imports.txt)).

**A correction to the usual advice about `output_key`.** Earlier editions of this page said two parallel children sharing an `output_key` "causes a race condition". They collide, but the framework does not stop you: a `ParallelAgent` whose two children both declare `output_key="result"` constructed without an error in the recorded run ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)). The hazard is therefore a silent data overwrite at run time, not a validation error at import time — which is precisely why unique keys matter more than the old wording implied. Use distinct keys (`docs_findings`, `issues_findings`) and merge downstream, as in the example above.

## Running agents: Runner, sessions and the dev UI

`adk run my_agent` gives an interactive terminal session and `adk web --port 8000` starts a browser UI at `http://localhost:8000`. Google is explicit about the boundary: "ADK Web is ***not meant for use in production deployments***. You should use ADK Web for development and debugging purposes only." ([Python quickstart](https://adk.dev/get-started/python/index.md)).

In code, a session service and a runner drive the agent, and `Runner` plus `InMemorySessionService` are the two imports the tutorial's own examples need; both imported successfully in the recorded check, as did `from google.genai.types import Content, Part` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)).

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="code_review", session_service=session_service)
session = session_service.create_session(app_name="code_review", user_id="dev_user",
                                         state={"file_path": "my_module.py"})
for event in runner.run(user_id="dev_user", session_id=session.id,
                        new_message=Content(parts=[Part(text="Review the file.")])):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

## Exposing agents over A2A (updated entry point)

The A2A section of this tutorial used to wrap an agent in `A2AServer` and call remote agents with `A2AClient`. Neither name survives in 2.12.0: `from google.adk.a2a import A2AServer` fails with `ImportError: cannot import name 'A2AServer' from 'google.adk.a2a'`, and `A2AClient` fails the same way ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)).

The documented replacement is a function, not a server class: "You can take an existing agent built using ADK and make it A2A-compatible by simply wrapping it using the `to_a2a()` function" ([A2A quickstart: exposing](https://adk.dev/a2a/quickstart-exposing/index.md)).

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

a2a_app = to_a2a(root_agent, port=8001)   # serves the agent card for you
```

Two operational details from the same page: `to_a2a()` auto-generates the agent card in memory, and the alternative path is to host your own `agent.json` card with `adk api_server --a2a`, which keeps `adk web` usable for debugging. The page also states that ADK's A2A integration works with both `a2a-sdk` 0.3.x and 1.x.x, detecting the installed SDK version automatically, while recommending that new integrations target 1.x.x ([A2A quickstart: exposing](https://adk.dev/a2a/quickstart-exposing/index.md)).

**The import requires an extra, and the base install does not have it.** On the recorded check's base install, `from google.adk.a2a.utils.agent_to_a2a import to_a2a` raised `ModuleNotFoundError: No module named 'a2a'`; `pyproject.toml` declares the SDK only inside the extra — `optional-dependencies.a2a = ["a2a-sdk[http-server]>=0.3.4,<2"]` ([extra-imports.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/extra-imports.txt), [pyproject.toml](https://raw.githubusercontent.com/google/adk-python/main/pyproject.toml)). Install it with `pip install "google-adk[a2a]"` before copying any A2A snippet. That extra was not installed in this pass, so the end-to-end serving path is unverified here; [the A2A protocol guide](https://baeseokjae.github.io/posts/google-adk-a2a-protocol-guide-2026/) covers the protocol itself.

## Deployment: where to go after the tutorial

The earlier deployment section on this page called `pip install google-cloud-aiplatform[adk,reasoningengine]` and `vertexai.preview.reasoning_engines.AdkApp`. That path could not be checked here — the base install does not contain a `vertexai` module at all (`ModuleNotFoundError: No module named 'vertexai'`) — and the package metadata now says the Google Cloud extra pulls a different distribution: the `gcp` extra declares `google-cloud-agentplatform[agent_engines]>=2.2,<3`, with an inline note that the standalone package "carries no GAPIC stack, so `pip install google-adk[gcp]` no longer drags in ~1000 generated aiplatform_v1 modules" ([pyproject.toml](https://raw.githubusercontent.com/google/adk-python/main/pyproject.toml)). Rather than restate an unverified snippet, this page points at the deployment commands the repository documents today ([google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)):

```bash
adk deploy docker --with_ui <agent-folder>
adk deploy cloud_run --with_ui <agent-folder>
```

`adk --help` in the recorded environment lists a `deploy` subcommand described as "Deploys agent to hosted environments", so the CLI surface for this exists locally; the actual deploy was not run, because that needs a Google Cloud project and credentials ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)). For the framework-selection question — whether ADK, LangGraph or Mastra is the right runtime for your workload — this page deliberately does not duplicate the site's comparison pages linked at the top.

## How the local check was run, and what it does not cover

Everything labelled as verified above comes from one bounded, reproducible check, run in an isolated virtual environment under a private per-run scratch directory (Python 3.12.3, Linux aarch64), with the exact command list and timestamps recorded in [write-check-record.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/write-check-record.json). The sequence was `python3 -m venv venv`, `pip install --upgrade pip`, then the unpinned `pip install google-adk` that this tutorial shows, followed by a script that (a) reads the resolved version, `Requires-Python` and every declared extra from the installed metadata, (b) executes each import statement the tutorial prints, one at a time, recording the exception text when it fails, (c) constructs the sequential, parallel and nested agent shapes and reads the child lists back, and (d) runs `adk --version` and `adk --help`. The script is published as [local-run-script-verify_tutorial_commands.py](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/local-run-script-verify_tutorial_commands.py) and can be re-run against any later release; the pip resolution log is [local-run-pip-resolve.log](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-pip-resolve.log).

The limits, stated so you can judge the claims: **no model call was made** (no API credential in this run), so nothing here is a claim about agent behaviour, latency, output quality, or the correctness of the model ids; the extra packages (`a2a`, `gcp`, `all`) were **not** installed, so their dependency resolution is unverified; and the install was unpinned, so a later `pip install google-adk` may resolve a different version with different import results. This is an author-side check of installation, imports and construction — not a benchmark, and not a vendor claim.

## FAQ

### How do I install Google ADK in Python?

On Python 3.11 or newer, run `pip install google-adk`, then confirm with `pip show google-adk` and `adk --version`. The docs' installation page gives the same command with a virtual environment ([installation](https://adk.dev/get-started/installation/index.md)); the recorded run resolved google-adk 2.12.0 and printed `adk, version 2.12.0` ([local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)).

### Does Google ADK need Python 3.10 or 3.11?

Use 3.11+: the installed distribution declares `Requires-Python: >=3.11` and the repository README states "Python 3.11+" ([PyPI JSON for google-adk](https://pypi.org/pypi/google-adk/json), [google/adk-python README](https://raw.githubusercontent.com/google/adk-python/main/README.md)). The [Python quickstart](https://adk.dev/get-started/python/index.md) still lists 3.10 or later, so the docs page and the package currently disagree.

### What is the difference between LlmAgent and SequentialAgent?

An `LlmAgent` is the reasoning primitive: it calls a model and decides which tools to use. A `SequentialAgent` is a template workflow agent with no model of its own — it runs its children in the order given and is deterministic, sharing one invocation context and session state between them ([sequential agents](https://adk.dev/agents/workflow-agents/sequential-agents/index.md)).

### Are SequentialAgent and ParallelAgent deprecated in Google ADK?

They are documented as superseded starting in ADK 2.0 for Python and Go, in favour of graph-based and dynamic workflows ([sequential agents](https://adk.dev/agents/workflow-agents/sequential-agents/index.md), [parallel agents](https://adk.dev/agents/workflow-agents/parallel-agents/index.md)), and constructing either one emits `DeprecationWarning: ... is deprecated in favor of Workflow and will be removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.` Both still import and construct in 2.12.0 ([local-run-stderr.txt](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-stderr.txt)).

### Why does `from google.adk.a2a import A2AServer` fail?

Because that name no longer exists: the import raises `ImportError: cannot import name 'A2AServer' from 'google.adk.a2a'`. Expose an agent with `to_a2a()` from `google.adk.a2a.utils.agent_to_a2a` and install the `a2a` extra first — without it the import fails with `ModuleNotFoundError: No module named 'a2a'` ([A2A quickstart: exposing](https://adk.dev/a2a/quickstart-exposing/index.md), [local-run-verify-output.json](https://github.com/baeseokjae/baeseokjae.github.io/blob/main/research/evidence/google-adk-python-tutorial-2026/write-check/local-run-verify-output.json)).
