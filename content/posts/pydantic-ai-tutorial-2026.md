---
cover:
  alt: 'Pydantic AI Tutorial 2026: Type-Safe Python Agents With Automatic Validation
    and Self-Correction'
  image: /images/pydantic-ai-tutorial-2026.png
  relative: false
date: 2026-04-22 01:13:32+00:00
description: 'Updated October 2026 for pydantic-ai 2.54.0 - the current provider strings, the output_type= and result.output API, corrected install instructions and a dated provider count.'
draft: false
schema: schema-pydantic-ai-tutorial-2026
tags:
- pydantic-ai
- python
- ai-agents
- llm
- type-safety
- tutorial
lastmod: 2026-10-08 00:00:00+00:00
title: 'Pydantic AI Tutorial 2026 (refreshed): Type-Safe Python Agents With Automatic Validation'
---

Pydantic AI is a Python agent framework from the Pydantic team: install it with `pip install pydantic-ai`, declare a Pydantic `BaseModel` as your agent's output type, and the framework validates the model's response and retries automatically when validation fails — no manual JSON parsing, no schema wrestling. This page was first published in April 2026. The October 2026 revision below re-checked every copy-paste surface on it against `pydantic-ai` 2.54.0 and the vendor's current documentation, because four of the strings the original page carried no longer resolve at all.

## What Is Pydantic AI?

Pydantic AI is an open-source Python agent framework that applies Pydantic's validation engine to LLM interactions. Its repository was created on 2024-06-21, and the current line is 2.54.0, uploaded to PyPI on 2026-10-03 ([repository](https://github.com/pydantic/pydantic-ai), [PyPI project page](https://pypi.org/project/pydantic-ai/)). The repository reports 20,489 stars and 2,879 forks as of 2026-10-08 ([pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)). Pydantic Validation is described by the project as the validation layer of the OpenAI SDK, the Anthropic SDK, the Google ADK and LangChain, and Pydantic AI applies that same approach to the agent loop itself ([README](https://github.com/pydantic/pydantic-ai/blob/main/README.md)).

Where LangChain offers broad abstractions over many integrations, Pydantic AI treats type safety as the core feature: every structured output is validated against a `BaseModel` at runtime, with automatic retries when the model returns something that does not parse. The project's own comparison page sets out where it differs from LangChain, Google ADK, the Claude Agent SDK and others ([comparisons](https://pydantic.dev/docs/ai/comparisons/overview/)). The design goal is the FastAPI ergonomics applied to agents — declare the schema, wire up the model, and let the framework handle validation and retries.

### The FastAPI Analogy

FastAPI replaced boilerplate route handlers with type-annotated functions that validate payloads and generate OpenAPI docs. Pydantic AI does the same for agents: instead of writing prompt templates and hand-parsing JSON, you declare a typed output model and the framework validates the result. That means static analysis tools such as mypy and pyright work across your agent code, and your IDE knows the shape of every agent result.

## Install and the Python Floor (corrected)

The core install is unchanged:

```bash
pip install pydantic-ai
```

The default install pulls the `pydantic_ai` package, its core dependencies, the libraries needed for the OpenAI, Anthropic and Google models, plus the CLI, MCP, Evals, Web UI and Logfire integrations ([installation doc](https://github.com/pydantic/pydantic-ai/blob/main/docs/install.md)). Anything else is an extra, for example `pydantic-ai[bedrock,temporal]`, or you can install `pydantic-ai-slim` with only the extras you need.

**Provider extras no longer exist on the root package.** The April version of this page told readers to run `pip install pydantic-ai[openai]`, `pydantic-ai[anthropic]` or `pydantic-ai[gemini]`. None of those three extras, nor `google`, is defined for the root package: an install attempt in a clean environment emits `warning: The package 'pydantic-ai==2.54.0' does not have an extra named 'gemini'`, and the extras PyPI publishes for `pydantic-ai` 2.54.0 contain neither `gemini`, `google`, `openai`, `anthropic` nor `gateway` ([pyproject.toml](https://github.com/pydantic/pydantic-ai/blob/main/pyproject.toml), [PyPI project page](https://pypi.org/project/pydantic-ai/)). The extras that do exist — `bedrock`, `temporal`, `xai`, `groq`, `voyageai` and so on — are forwarded to `pydantic-ai-slim`. For the three bundled providers, a plain `pip install pydantic-ai` is all you need.

**The Python floor is inconsistent across the vendor's own surfaces.** The repository's install doc says `(Requires Python 3.11+)`, while the rendered installation page at `pydantic.dev` shows `(Requires Python 3.10+)` and PyPI metadata declares `requires_python: >=3.10` ([installation doc](https://github.com/pydantic/pydantic-ai/blob/main/docs/install.md), [install page](https://pydantic.dev/docs/ai/overview/install/), [PyPI project page](https://pypi.org/project/pydantic-ai/)). This page now recommends Python 3.11 or newer, matching the stricter of the vendor's statements; nothing here was tested below 3.11.

**Environment variables follow the provider, and the Google one is `GOOGLE_API_KEY`.** The framework reads `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` for those providers, and the Gemini provider expects `GOOGLE_API_KEY` — the library's own error message for a Google model in 2.54.0 names `GOOGLE_API_KEY`, not `GEMINI_API_KEY` ([Google provider docs](https://pydantic.dev/docs/ai/models/google/)).

## Model Strings That Resolve Today

Every model is selected with a `<provider>:<model>` string, so switching providers is a one-line change. The table below lists the strings verified against the vendor's provider documentation on 2026-10-08.

| Provider | Current string | Note |
|---|---|---|
| OpenAI | `openai:gpt-6-sol` | Bare `openai:` resolves to `OpenAIResponsesModel` (the Responses API). Pin the legacy Chat Completions API with `openai-chat:`. |
| Anthropic | `anthropic:claude-sonnet-4-6` | Unchanged; still the documented example. |
| Google (Gemini API) | `google:gemini-3.7-flash` | The vendor's documented example. The `google-gla:` prefix is gone. Vertex AI uses `google-cloud:`. |
| Ollama (local) | `ollama:qwen3` | Documented example; any tag present in your local Ollama resolves through the same prefix. |

Sources for the table: the vendor's [OpenAI page](https://pydantic.dev/docs/ai/models/openai/) (bare `openai:` and the `openai-chat:` alternative), [Anthropic page](https://pydantic.dev/docs/ai/models/anthropic/), [Google page](https://pydantic.dev/docs/ai/models/google/) (the `google:` and `google-cloud:` prefixes) and [Ollama page](https://pydantic.dev/docs/ai/models/ollama/).

Re-running the original page's Google string in an isolated environment is the sharpest illustration of the change: `Agent('google-gla:gemini-2.0-flash')` now raises `UserError: Unknown model: google-gla:gemini-2.0-flash. Did you mean 'google:gemini-2.0-flash'?`, so a copied `google-gla:` line is a hard failure at agent construction, not a warning. Two cautions about reading that error message. First, the tag it suggests is the April string with only the prefix corrected — it is not the example the vendor currently documents. Second, construction validates the prefix, not the tag: `Agent('google:gemini-2.0-flash')` and `Agent('google:gemini-3.7-flash')` both construct and then fail identically asking for `GOOGLE_API_KEY`, so a successful construction is not evidence that a tag is still served. The vendor's Google page documents `Agent('google:gemini-3.7-flash')` as the Gemini-API example ([Google provider docs](https://pydantic.dev/docs/ai/models/google/)).

Two related corrections belong here. First, this page previously used `openai:gpt-4o` in every example; the vendor's OpenAI page now documents `openai:gpt-6-sol` and a bare `openai:` prefix that routes to the Responses API, so the examples below have been moved to the documented model and the routing difference is called out ([OpenAI provider docs](https://pydantic.dev/docs/ai/models/openai/)). Second, the Google provider error message is how you discover the environment variable name — a `google:` model without `GOOGLE_API_KEY` fails with that instruction rather than silently falling back.

The provider directory is larger than the April page suggested. Counting the vendor's provider table gives 34 provider rows and 37 distinct `<prefix>:` model-string prefixes as of 2026-10-08, so the old undated "20+ model providers" figure has been replaced with that dated count ([provider directory](https://pydantic.dev/docs/ai/models/overview.md), [rendered provider list](https://pydantic.dev/docs/ai/models/overview/)). The count is a documentation-directory count — the number of prefixes the vendor documents — not a count of independently verified integrations.

## Your First Agent

A Pydantic AI agent wraps a model, an optional set of instructions, optional tools and an output type. The keyword that declares a structured result is `output_type=`, not `result_type=`:

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class City(BaseModel):
    name: str
    country: str

agent = Agent(
    "openai:gpt-6-sol",
    output_type=City,
    instructions="Answer with the city and its country.",
)

result = agent.run_sync("What is the capital of France?")

print(result.output)          # validated City instance, not .data
print(result.usage)           # RunUsage(...) — a property, not a call
print(result.all_messages())  # full conversation history
```

Three API details changed since April 2026 and are the most common copy-paste failures readers hit with the old page. `result_type=` is gone — constructing an agent with it raises `TypeError: Agent.__init__() got an unexpected keyword argument 'result_type'`; the accepted parameter is `output_type`. The result object is `AgentRunResult` and the validated value is `result.output`, not `result.data` (`AgentRunResult` has no `data` attribute). Usage is a property (`result.usage`), not a method, so `result.usage()` raises `TypeError: 'RunUsage' object is not callable`. `result.all_messages()` is still a method and still returns the conversation history.

For async code use `await agent.run(prompt)`; for streaming text use `agent.run_stream(prompt)` as an async context manager. The full surface is described in the vendor's [agent documentation](https://pydantic.dev/docs/ai/core-concepts/agent/).

## Structured Outputs With Pydantic Models

Structured output is the feature the framework is built around: define a `BaseModel` as the agent's `output_type` and every response is validated against it, with automatic retries when validation fails. That removes the most common failure mode in LLM applications — brittle JSON parsing that breaks when a model adds a field, nests objects differently or answers in prose. The framework feeds the validation error back to the model on the next attempt, so the model can correct itself within the same run.

Retry behaviour is worth stating precisely, because the old page described it loosely. When an output tool is in use, each output tool gets its own retry counter, and the output side of the agent's retry budget is the default per-tool limit. The budget defaults to 1 and is set with an `AgentRetries` mapping — `Agent(..., retries={"output": 2})` on the agent, or `agent.run(..., retries={"output": 2})` for a single run — or per output tool with `ToolOutput(model, max_retries=N)` ([output documentation](https://pydantic.dev/docs/ai/core-concepts/output/)).

Nested models work the way Pydantic users expect:

```python
from typing import List, Optional
from pydantic import BaseModel
from pydantic_ai import Agent

class Address(BaseModel):
    street: str
    city: str
    country: str

class CompanyProfile(BaseModel):
    name: str
    founded: int
    headquarters: Address
    products: List[str]
    revenue_usd_millions: Optional[float] = None

agent = Agent("openai:gpt-6-sol", output_type=CompanyProfile)
profile = agent.run_sync("Tell me about Stripe, the payments company.").output
print(profile.headquarters.city)
```

Structured output and streaming are no longer mutually exclusive either. A structured agent can stream validated output with `stream_output()`, which yields the validated object as the stream progresses rather than only at the end; `stream_text()` remains the text path ([output documentation](https://pydantic.dev/docs/ai/core-concepts/output/)). The April answer to "can I stream and validate at the same time?" was no; on 2.54.0 it is yes, and the two-step workaround the old FAQ recommended is no longer necessary.

## Tool Calling and Dependency Injection

Tools are plain Python functions registered with `@agent.tool`; the model reads the docstring to decide when to call them and the type annotations to build the arguments. Tools that need no run context can be registered with `@agent.tool_plain`, and tools that do receive a `RunContext[Deps]` as their first argument ([agent documentation](https://pydantic.dev/docs/ai/core-concepts/agent/)).

```python
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

@dataclass
class Deps:
    user_id: int
    max_sources: int = 5

class OrderSummary(BaseModel):
    total_orders: int
    total_spent_usd: float
    most_recent_order: str

agent = Agent(
    "anthropic:claude-sonnet-4-6",
    deps_type=Deps,
    output_type=OrderSummary,
    instructions="Summarize the user's order history.",
)

@agent.tool
async def get_orders(ctx: RunContext[Deps]) -> list[dict]:
    """Fetch all orders for the current user from the database."""
    return await ctx.deps.db.fetch_orders(ctx.deps.user_id)

summary = agent.run_sync("How much have I spent?", deps=Deps(user_id=42)).output
```

Dependency injection is what makes agents testable: the dependency container is built outside the agent and passed at call time, so tests can inject a mock database or HTTP client instead of monkeypatching module state. The `deps_type=Deps` declaration is on the constructor; the value is supplied to `run_sync(prompt, deps=...)` or `run(prompt, deps=...)`.

## Testing With TestModel

`TestModel` is the deterministic mock shipped with the framework: it returns schema-conformant responses without any API call, which is what makes agent tests viable in CI. Install it as an override for the duration of a test:

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

def test_sentiment_analysis(agent, sentiment_model):
    with agent.override(model=TestModel()):
        result = agent.run_sync("I love this product!")
        assert isinstance(result.output, sentiment_model)
```

Note the assertion: `result.output`, the current accessor, not the `result.data` the April page used. The vendor's [testing guide](https://pydantic.dev/docs/ai/guides/testing/) covers `TestModel`, `FunctionModel` for tool-level control, and overriding the model with pytest fixtures, which is the cleaner way to share the override across a test session.

## Observability With Logfire

Logfire remains the native observability path, built on OpenTelemetry so traces and metrics export to any compatible backend. The three lines are unchanged:

```python
import logfire
from pydantic_ai import Agent

logfire.configure()
logfire.instrument_pydantic_ai()

agent = Agent("openai:gpt-6-sol", name="hello_world_agent", instructions="Be concise.")
agent.run_sync("Summarize why type safety matters in Python.")
```

`logfire.configure()` reads the project token from the environment and `logfire.instrument_pydantic_ai()` instruments agent runs, model requests, tool calls and validation events ([Logfire integration](https://pydantic.dev/docs/ai/integrations/logfire/)). One correction to the April production notes: the Pydantic AI Gateway is no longer reached through a `pydantic-ai[gateway]` extra — no such extra exists on the root package — it is a separate product with its own key and cost monitoring, and the vendor's install doc links it as a companion rather than an extra ([installation doc](https://github.com/pydantic/pydantic-ai/blob/main/docs/install.md)).

## Common Questions

**Does Pydantic AI work with local models such as Ollama?**
Yes, through the `ollama:` prefix. The vendor's documented example is `Agent('ollama:qwen3')` ([Ollama provider docs](https://pydantic.dev/docs/ai/models/ollama/)). Structured output requires the local model to support tool calling or JSON mode; whether a specific tag such as `llama3.2` is present depends on what you have pulled locally, which no documentation check can establish.

**How many validation retries happen before a run fails?**
The output retry budget defaults to 1 and is configured with an `AgentRetries` mapping, for example `Agent(..., retries={"output": 2})`, or per output tool through `ToolOutput(max_retries=N)` ([output documentation](https://pydantic.dev/docs/ai/core-concepts/output/)). Each retry carries the previous validation error as additional context.

**Can I stream and still get a validated object?**
Yes on 2.54.0: `stream_output()` yields validated structured output as the stream runs, so the two-call workaround the April version recommended is unnecessary ([output documentation](https://pydantic.dev/docs/ai/core-concepts/output/)).

## What Changed in This October 2026 Refresh

This revision corrects copy-paste surfaces that the April version published and that the current library no longer accepts:

- `google-gla:gemini-2.0-flash` (the April string) is replaced by the vendor's documented `google:gemini-3.7-flash`; `google-gla:` now raises `UserError` naming the replacement prefix, and Vertex AI remains `google-cloud:` ([Google provider docs](https://pydantic.dev/docs/ai/models/google/)).
- `result_type=` is replaced by `output_type=` throughout; the old keyword raises `TypeError` at agent construction ([Anthropic provider docs](https://pydantic.dev/docs/ai/models/anthropic/), [README](https://github.com/pydantic/pydantic-ai/blob/main/README.md)).
- `result.data` is replaced by `result.output`, and `result.usage()` by the `result.usage` property.
- The `pydantic-ai[gemini]` / `[openai]` / `[anthropic]` install lines are removed because no such extras exist; the default install already covers OpenAI, Anthropic and Google ([pyproject.toml](https://github.com/pydantic/pydantic-ai/blob/main/pyproject.toml), [PyPI project page](https://pypi.org/project/pydantic-ai/)).
- The `pydantic-ai[gateway]` reference is removed; the Gateway is a separate product.
- `GEMINI_API_KEY` is corrected to `GOOGLE_API_KEY` for the Gemini provider ([Google provider docs](https://pydantic.dev/docs/ai/models/google/)).
- The undated "20+ model providers" figure is replaced by a dated count of 34 provider rows and 37 prefixes (2026-10-08), and the April star and fork figures are replaced by 20,489 stars and 2,879 forks on the same date ([provider directory](https://pydantic.dev/docs/ai/models/overview.md), [repository](https://github.com/pydantic/pydantic-ai)).
- The claim that "streaming and structured outputs are mutually exclusive" is withdrawn; `stream_output()` provides both ([output documentation](https://pydantic.dev/docs/ai/core-concepts/output/)).
- The old FAQ's unsourced "near-100% first-attempt success" figure and the "thousands of daily agent interactions in production" line were not re-confirmable from any vendor page and have been removed rather than restated.
- The version is pinned to 2.54.0, the current release, uploaded 2026-10-03 ([releases](https://github.com/pydantic/pydantic-ai/releases/latest), [PyPI project page](https://pypi.org/project/pydantic-ai/)).

## Sources and Verification Notes

Everything factual above was re-read from the vendor's own documentation and package metadata on 2026-10-08 (UTC): the [installation doc](https://github.com/pydantic/pydantic-ai/blob/main/docs/install.md), [pyproject.toml](https://github.com/pydantic/pydantic-ai/blob/main/pyproject.toml), [provider directory](https://github.com/pydantic/pydantic-ai/blob/main/docs/models/overview.md), the [Google](https://pydantic.dev/docs/ai/models/google/), [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/), [Ollama](https://pydantic.dev/docs/ai/models/ollama/) and [OpenAI](https://pydantic.dev/docs/ai/models/openai/) provider pages, the [output](https://pydantic.dev/docs/ai/core-concepts/output/), [agent](https://pydantic.dev/docs/ai/core-concepts/agent/), [testing](https://pydantic.dev/docs/ai/guides/testing/) and [Logfire](https://pydantic.dev/docs/ai/integrations/logfire/) pages, the [README](https://github.com/pydantic/pydantic-ai/blob/main/README.md), the [repository](https://github.com/pydantic/pydantic-ai), the [latest release](https://github.com/pydantic/pydantic-ai/releases/latest) and the [PyPI project page](https://pypi.org/project/pydantic-ai/).

The four copy-paste failures described above were reproduced by installing `pydantic-ai` 2.54.0 into an isolated virtual environment (Python 3.12) and running the tutorial's own calls against the library's built-in `TestModel` path. No live model API key was available for this revision, so no claim is made about model output quality, real retry counts or token cost; the checks cover syntax, accepted keyword arguments, accessor names and error messages, which are independent of the model backend. Those local runs were author-side verification only and are not published as a downloadable dataset. Star, fork and version figures are point-in-time values read on 2026-10-08 and will move.
