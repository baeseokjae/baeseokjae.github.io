---
title: "GPT-5-Codex Developer Guide: OpenAI's SWE-Optimized Model API Explained"
date: 2026-05-25T00:04:49+00:00
tags: ["gpt-5-codex", "openai", "coding-ai", "responses-api", "agentic-coding"]
description: "Complete developer guide to GPT-5-Codex: API setup, agentic workflows, pricing, benchmarks, and when to use it over GPT-5.5."
draft: false
cover:
  image: "/images/gpt-5-codex-model-guide-2026.png"
  alt: "GPT-5-Codex Developer Guide: OpenAI's SWE-Optimized Model API Explained"
  relative: false
schema: "schema-gpt-5-codex-model-guide-2026"
---

GPT-5-Codex is OpenAI's software-engineering-optimized model family, built specifically for agentic coding tasks like feature development, debugging, and large-scale refactoring. Unlike general-purpose GPT models, it runs exclusively through the Responses API and powers the OpenAI Codex platform, which reached 4 million weekly active developers by April 2026.

## What Is GPT-5-Codex? Understanding OpenAI's SWE-Optimized Model Family

GPT-5-Codex is a specialized series of language models from OpenAI, purpose-built for software engineering tasks that require long-horizon reasoning, multi-file context comprehension, and autonomous code execution. Unlike general-purpose models such as GPT-5.5, the GPT-5-Codex family is optimized for agentic workflows — meaning it can plan a multi-step coding task, interact with tools like shells and file systems, and iterate on results without continuous human intervention. The original `gpt-5-codex` model was released on September 23, 2025, priced at $1.25 per 1M input tokens and $10.00 per 1M output tokens, and was immediately positioned as the backbone of OpenAI's Codex platform. A critical distinction developers must understand: GPT-5-Codex is available only through the **Responses API**, not the older Chat Completions API — this is not a minor implementation detail, but a paradigm shift in how you structure API calls, tool use, and conversation state. The model family has since expanded through GPT-5.1-Codex, GPT-5.2-Codex, and GPT-5.3-Codex, each improving SWE-Bench Pro scores while introducing better context compaction and reduced output token overhead.

### Why "Codex" Is Confusing: The Platform vs. the Model

Many developers confuse "OpenAI Codex" the platform with the `gpt-5-codex` model identifier. The Codex platform is a multi-surface agentic coding system (CLI, IDE extension, ChatGPT delegation) that runs on OpenAI's Codex-family models — currently using GPT-5.5 as its primary backbone in some configurations. When OpenAI says "Codex uses GPT-5.5," they mean the platform is using the latest capable model; the `gpt-5-codex` model ID in the API refers to a specific snapshot optimized for coding. For API integration purposes, always use the explicit versioned model IDs (e.g., `gpt-5.3-codex`) to avoid unexpected behavior from unannounced snapshot updates.

## GPT-5-Codex Model Versions: From gpt-5-codex to GPT-5.3-Codex (2025–2026)

GPT-5-Codex has evolved through four documented versions since its September 2025 launch, each iteration improving coding benchmark performance while refining token efficiency for production deployments. The original `gpt-5-codex` established the Responses API-only architecture and introduced the 400K token context window, enabling full-codebase operations in a single API call — a capability no previous OpenAI model offered at this scale. GPT-5.2-Codex, launched January 14, 2026, introduced context compaction algorithms that dramatically reduced token consumption on long-horizon tasks, bringing its price to $1.75/$14.00 per 1M input/output tokens. GPT-5.3-Codex reached 56.8% on SWE-Bench Pro, 77.3% on Terminal-Bench 2.0, and 64.7% on OSWorld-Verified as of mid-2026, establishing it as OpenAI's dedicated coding benchmark leader. The versioning pattern follows a clear convention: higher minor versions (`5.1`, `5.2`, `5.3`) are Codex-specific optimizations, while `5.5` represents the general-purpose branch. More than 85% of OpenAI's own employees use Codex weekly across all departments — including finance and marketing — evidence that the model's utility extends beyond pure engineering workflows.

### Model ID Reference Table

| Model ID | Release | Context | Input $/1M | Output $/1M | SWE-Bench Pro |
|---|---|---|---|---|---|
| `gpt-5-codex` | Sept 2025 | 400K | $1.25 | $10.00 | ~48% |
| `gpt-5.1-codex` | Nov 2025 | 400K | $1.50 | $12.00 | ~51% |
| `gpt-5.2-codex` | Jan 2026 | 400K | $1.75 | $14.00 | ~54% |
| `gpt-5.3-codex` | Apr 2026 | 400K | $2.00 | $15.00 | 56.8% |

## GPT-5-Codex vs GPT-5.5: Which Model Should You Use for Coding?

GPT-5-Codex and GPT-5.5 target fundamentally different workloads, and choosing between them comes down to task specificity, cost tolerance, and integration complexity. GPT-5.5 is OpenAI's general-purpose frontier model — it achieves 58.6% on SWE-Bench Pro and 82.7% on Terminal-Bench 2.0, making it a stronger performer on terminal-based coding tasks than GPT-5.3-Codex (56.8% SWE-Bench Pro, 77.3% Terminal-Bench 2.0). However, GPT-5.5 also uses approximately 40% more output tokens to complete identical Codex tasks compared to GPT-5.4, making it meaningfully more expensive at scale. GPT-5-Codex variants were specifically tuned for context compaction in agentic loops — they emit fewer intermediate tokens, maintain state more efficiently across long tasks, and are priced lower per-token for input. The practical rule: use GPT-5.3-Codex for high-volume automated workflows (CI/CD integration, overnight batch refactoring), and use GPT-5.5 when you need the highest raw capability for complex one-off engineering challenges. Note that Claude Opus 4.7 leads SWE-Bench Pro overall at 64.3%, which means neither OpenAI model is unambiguously dominant for pure coding benchmarks.

### Decision Framework

```
High volume, predictable tasks, budget sensitivity → gpt-5.3-codex
Maximum capability, one-off complex problems     → gpt-5.5
Cross-modal or multimodal coding tasks           → gpt-5.5
Overnight CI/CD agents with file system access   → gpt-5.3-codex
```

## Getting Started with the GPT-5-Codex API (Responses API Setup)

The GPT-5-Codex API uses OpenAI's Responses API exclusively — a stateful, tool-aware successor to Chat Completions that natively handles multi-turn agentic state, file I/O, shell execution, and computer use. Unlike Chat Completions where you pass a `messages` array, the Responses API uses a `input` field and returns a structured `output` object with typed action results. Authentication is identical to other OpenAI APIs: set your `OPENAI_API_KEY` environment variable. The minimum viable API call requires `model`, `input`, and (for coding tasks) at least the `computer_use_preview` or `code_interpreter` tool enabled. GPT-5-Codex models support multiple reasoning effort settings (`low`, `medium`, `high`) that trade response latency for solution quality — `high` reasoning is recommended for debugging and architecture tasks, `low` for code completion and boilerplate generation. The 400K token context window supports large-scale codebase operations, but developers should implement context compaction explicitly to avoid runaway costs on long sessions.

### Python Quickstart

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY from env

response = client.responses.create(
    model="gpt-5.3-codex",
    reasoning={"effort": "high"},
    tools=[{"type": "code_interpreter"}],
    input="Analyze the performance bottlenecks in this Python codebase and suggest optimizations.",
    # Attach files via file IDs from the Files API
)

print(response.output_text)
```

### Setting Reasoning Effort

```python
# For debugging complex issues — higher latency, better results
response = client.responses.create(
    model="gpt-5.3-codex",
    reasoning={"effort": "high"},
    input=prompt,
)

# For batch code generation — faster, lower cost
response = client.responses.create(
    model="gpt-5.3-codex",
    reasoning={"effort": "low"},
    input=prompt,
)
```

### Shell Tool Integration

```python
response = client.responses.create(
    model="gpt-5.3-codex",
    tools=[
        {"type": "code_interpreter"},
        {
            "type": "bash",
            "allowed_commands": ["pytest", "git", "npm", "python"]
        }
    ],
    input="Run the test suite, identify failing tests, and fix the root causes.",
)
```

## Building Agentic Coding Workflows with GPT-5-Codex

Agentic coding workflows with GPT-5-Codex require a fundamentally different design pattern than traditional LLM API calls. In an agentic loop, GPT-5-Codex does not return a single answer — it executes a plan across multiple tool calls, observes results, and adapts its approach before returning a final output. This architecture is what enables long-horizon tasks like "implement OAuth2 login from scratch" or "refactor this 10,000-line module to use async/await" to complete without step-by-step human guidance. The Responses API's stateful design handles intermediate tool results natively, eliminating the manual re-injection of tool outputs required in Chat Completions-based agentic systems. To build production-grade agentic workflows, you need to handle three concerns: task decomposition (breaking large goals into model-executable subtasks), state management (deciding what context to carry across API calls), and interrupt handling (detecting when the model needs human input and surfacing it cleanly). OpenAI recommends providing an `AGENTS.md` file in the project root to give GPT-5-Codex durable project-level guidance — this dramatically improves consistency across long multi-session workflows.

### Multi-Step Agentic Loop Pattern

```python
import time
from openai import OpenAI

client = OpenAI()

def run_coding_agent(task: str, repo_files: list[dict]) -> str:
    """Run GPT-5-Codex as an agentic loop until task completion."""
    
    # Initial task submission
    response = client.responses.create(
        model="gpt-5.3-codex",
        reasoning={"effort": "high"},
        tools=[
            {"type": "code_interpreter"},
            {"type": "bash", "allowed_commands": ["pytest", "git", "grep", "ls"]},
        ],
        input=task,
        # Inject relevant file context
        file_inputs=repo_files,
    )
    
    # Poll until the response completes all tool calls
    while response.status in ("in_progress", "tool_calls_pending"):
        time.sleep(1)
        response = client.responses.retrieve(response.id)
    
    return response.output_text

# Example: Feature implementation task
result = run_coding_agent(
    task="Add rate limiting middleware to the Express API. Max 100 req/min per IP. Include tests.",
    repo_files=[
        {"path": "src/app.js", "content": open("src/app.js").read()},
        {"path": "src/routes/api.js", "content": open("src/routes/api.js").read()},
    ]
)
```

### Context Compaction Strategy

For long-running sessions, implement explicit context window management:

```python
def compact_context(messages: list[dict], threshold: int = 300_000) -> list[dict]:
    """Summarize earlier context when approaching the token limit."""
    total_tokens = estimate_tokens(messages)
    
    if total_tokens > threshold:
        # Keep system context + last N exchanges
        summarize_target = messages[1:-6]  # Preserve system + recent history
        summary = client.responses.create(
            model="gpt-5.3-codex",
            input=f"Summarize the key decisions and code changes made so far:\n\n{format_messages(summarize_target)}"
        ).output_text
        
        return [messages[0], {"role": "user", "content": f"[Context summary]: {summary}"}] + messages[-6:]
    
    return messages
```

## GPT-5-Codex Pricing, Token Economics, and Cost Optimization

GPT-5-Codex pricing is structured to reward developers who manage context efficiently, with substantial discounts for cached input tokens and significant cost differences between reasoning effort levels. The GPT-5.2-Codex model costs $1.75 per 1M input tokens, $14.00 per 1M output tokens, and $0.175 per 1M cached input tokens — a 10× discount on cached context. At 400K tokens of context window capacity, an uncached full-context call at the input rate alone costs $0.70 per request, which becomes prohibitive in tight loop agentic scenarios without active compaction. GPT-5.5 uses approximately 40% fewer output tokens than GPT-5.4 for identical Codex tasks — a genuine cost improvement at the output side — but its per-token rate is higher than GPT-5.3-Codex. For teams running overnight agentic batch jobs (continuous integration, automated code review, dependency upgrades), GPT-5.3-Codex typically delivers 30–50% cost savings versus GPT-5.5 while achieving comparable quality on well-defined tasks. The most impactful optimization is always output token reduction: use `reasoning={"effort": "low"}` for boilerplate tasks, set concise output format instructions, and structure prompts to produce diff-style outputs rather than complete file rewrites.

### Cost Comparison by Workload

| Workload | Best Model | Estimated Cost/Task | Notes |
|---|---|---|---|
| Batch lint fixes | `gpt-5.3-codex` | $0.02–0.05 | Low reasoning, small context |
| Feature implementation | `gpt-5.3-codex` | $0.15–0.40 | High reasoning, medium context |
| Full refactor (10K LOC) | `gpt-5.5` | $1.50–4.00 | Maximum capability needed |
| Daily code review | `gpt-5.3-codex` | $0.10–0.25/PR | Cached context saves significantly |
| Debugging session | Either | $0.20–0.80 | Depends on codebase complexity |

### Caching Best Practices

```python
# Structure prompts so stable content (system prompt, file context) comes first
# This maximizes cache hit rate on the 10× cheaper cached input rate

response = client.responses.create(
    model="gpt-5.3-codex",
    input=[
        # Stable context first — maximizes cache hits
        {"role": "system", "content": STABLE_SYSTEM_PROMPT},
        {"role": "user", "content": STABLE_FILE_CONTEXT},
        # Variable task last
        {"role": "user", "content": f"Task: {current_task}"},
    ],
)
```

## SWE-Bench Benchmarks Explained: GPT-5-Codex Performance vs. Competitors

SWE-Bench benchmarks measure a model's ability to resolve real GitHub issues — not toy problems, but actual pull request tasks drawn from open-source repositories like Django, Flask, and NumPy. GPT-5.3-Codex achieves 56.8% on SWE-Bench Pro (the harder, less-contaminated version of SWE-Bench), 77.3% on Terminal-Bench 2.0, and 64.7% on OSWorld-Verified as of mid-2026. These numbers represent genuine production-relevant capability: 56.8% means the model successfully resolves slightly more than half of all test issues without human guidance. For comparison, GPT-5.5 achieves 58.6% on SWE-Bench Pro and 82.7% on Terminal-Bench 2.0, while Claude Opus 4.7 leads SWE-Bench Pro at 64.3%. The gap between GPT-5.3-Codex and Claude Opus 4.7 (7.5 percentage points) is significant in absolute terms but narrows dramatically when considering price per resolved issue — GPT-5.3-Codex's lower token cost means it often delivers better cost-per-fix ratios on high-volume batch workloads. Terminal-Bench 2.0 specifically tests shell-based autonomous coding, making it the most predictive benchmark for CI/CD integration use cases.

### Benchmark Comparison Table (Mid-2026)

| Model | SWE-Bench Pro | Terminal-Bench 2.0 | OSWorld-Verified | Input $/1M |
|---|---|---|---|---|
| Claude Opus 4.7 | **64.3%** | ~71% | ~60% | $15.00 |
| GPT-5.5 | 58.6% | **82.7%** | ~65% | Higher |
| GPT-5.3-Codex | 56.8% | 77.3% | 64.7% | $2.00 |
| GPT-5.2-Codex | ~54% | ~70% | ~60% | $1.75 |

### What SWE-Bench Results Mean in Practice

A 56.8% SWE-Bench Pro score means GPT-5.3-Codex correctly resolves about 568 out of 1,000 real GitHub issues autonomously. The remaining 442 issues either receive incorrect solutions or are incomplete — which means human review remains essential. In production, teams typically use GPT-5-Codex to handle the high-confidence subset of routine issues (dependency updates, type errors, lint violations, test failures from changed APIs) and escalate complex architectural issues to human engineers.

## Real-World Use Cases: Feature Development, Refactoring, and Debugging

GPT-5-Codex delivers measurable value across three primary engineering workflows: feature implementation from specification, large-scale refactoring, and debugging — each requiring distinct prompt patterns and tool configurations. For feature development, the model performs best when given a precise specification in the prompt and access to the relevant existing files via the Files API; open-ended "build X" prompts without codebase context produce generic implementations that require extensive revision. For refactoring, the 400K context window is the key differentiator — GPT-5-Codex can ingest an entire module or service, understand its interdependencies, and produce a coherent refactored version in a single agentic loop rather than the chunk-by-chunk approach required by smaller-context models. For debugging, setting `reasoning={"effort": "high"}` combined with shell access (allowing the model to run tests and observe output directly) dramatically outperforms prompts that simply describe the bug — the model should be able to reproduce the failure, not just read about it. Codex usage grew 10× since August 2025, with usage in ChatGPT Business and Enterprise growing 6× since January 2026, indicating that these workflows have found genuine product-market fit across organizations.

### Feature Development Pattern

```python
def implement_feature(spec: str, codebase_context: dict) -> dict:
    """
    Implement a feature from a written specification.
    Returns dict with files_changed, tests_added, and explanation.
    """
    prompt = f"""
    Feature specification:
    {spec}
    
    Requirements:
    - Follow existing code patterns and conventions in the codebase
    - Add unit tests for all new functions
    - Update relevant documentation strings
    - Output a unified diff format
    
    Return your changes as a structured JSON with:
    - files_changed: list of {{path, diff}} objects
    - tests_added: list of test file paths created
    - explanation: 2-3 sentence summary of the implementation approach
    """
    
    response = client.responses.create(
        model="gpt-5.3-codex",
        reasoning={"effort": "high"},
        tools=[{"type": "code_interpreter"}],
        input=prompt,
        file_inputs=list(codebase_context.values()),
    )
    
    return parse_structured_output(response.output_text)
```

### Debugging with Shell Access

```python
def debug_failing_test(test_output: str, source_files: list) -> str:
    """Let GPT-5-Codex reproduce and fix a failing test."""
    
    response = client.responses.create(
        model="gpt-5.3-codex",
        reasoning={"effort": "high"},
        tools=[
            {"type": "code_interpreter"},
            {"type": "bash", "allowed_commands": ["pytest", "python", "grep"]},
        ],
        input=f"""
        The following test is failing:
        {test_output}
        
        Run the test, investigate the root cause, and produce a minimal fix.
        Do not change test assertions unless the specification has changed.
        """,
        file_inputs=source_files,
    )
    
    return response.output_text
```

## AGENTS.md and Configuration Best Practices for GPT-5-Codex

AGENTS.md is a Markdown file placed at the root of your repository that provides GPT-5-Codex with durable, project-level guidance persisted across all agentic sessions. It serves the same function as system prompts in single-session API calls, but its placement in the repository means it travels with the code, versioned in git, and is automatically picked up by OpenAI Codex tooling without requiring explicit injection in each API call. A well-crafted AGENTS.md dramatically improves consistency: instead of re-specifying "use TypeScript strict mode" or "all functions must have JSDoc comments" in every prompt, you encode these constraints once and the model applies them throughout all tasks. Best practices for AGENTS.md include: stating testing frameworks and commands explicitly (so the model knows to run `pytest -xvs` rather than `python test.py`), specifying forbidden patterns (e.g., "never use `eval()`, never commit `.env` files"), defining the PR format and commit message conventions, and listing MCP servers or external APIs the model has access to. AGENTS.md should be under 2,000 tokens to avoid unnecessarily consuming context budget, and should focus on invariants rather than task-specific instructions — those belong in the per-session prompt.

### AGENTS.md Template

```markdown
# AGENTS.md — [Project Name] Coding Agent Configuration

## Project Overview
[1-2 sentence description of what this codebase does]

## Technology Stack
- Language: Python 3.12 / TypeScript 5.4
- Framework: FastAPI / Next.js 15
- Database: PostgreSQL 16 (via SQLAlchemy ORM)
- Testing: pytest (Python) / Vitest (TypeScript)

## Testing Commands
- Run all tests: `pytest -xvs tests/`
- Run single test: `pytest -xvs tests/test_file.py::test_name`
- Type checking: `mypy src/ --strict`
- Linting: `ruff check src/`

## Code Conventions
- All public functions must have type annotations
- Use pathlib.Path, never os.path
- Prefer dataclasses over dicts for structured data
- Database queries must go through repository layer (never in routes)

## Forbidden Patterns
- Never use `eval()` or `exec()`
- Never hardcode secrets — use environment variables
- Never commit `.env` files or credentials

## Commit Message Format
feat: short description
fix: short description
refactor: short description

## MCP Integrations Available
- GitHub API (via GITHUB_TOKEN env var)
- Internal metrics API at http://metrics.internal/api/v1
```

### Per-Session Prompt Augmentation

Even with AGENTS.md, per-task prompts should include:

```python
TASK_PROMPT = """
Task: {task_description}

Constraints for this specific task:
- Only modify files in src/api/ and tests/api/
- Do not bump dependency versions
- Target Python 3.12 compatibility

Expected output format:
- Unified diff for all changed files
- Updated test coverage report
"""
```

## Frequently Asked Questions

**Q: Is GPT-5-Codex available through the Chat Completions API?**

No. GPT-5-Codex model family is exclusively available through the Responses API. Attempting to use model IDs like `gpt-5.3-codex` with the `/v1/chat/completions` endpoint will return an error. Migrate existing Chat Completions integrations to the Responses API before using any GPT-5-Codex variant.

**Q: What's the difference between `gpt-5-codex` and `gpt-5.3-codex`?**

`gpt-5-codex` (without a minor version number) is a floating alias that points to the latest Codex model snapshot — OpenAI updates it periodically without announcement, which can introduce unexpected behavior changes. `gpt-5.3-codex` is a pinned version. Use versioned model IDs in production for reproducible behavior; the floating alias is only appropriate for prototyping.

**Q: Can I use GPT-5-Codex with my existing LangChain or LlamaIndex integrations?**

Not directly — most LangChain and LlamaIndex abstractions are built on Chat Completions. You'll need to either use the OpenAI Python SDK directly with the Responses API client, or wait for framework updates that add native Responses API support. The Responses API's stateful tool execution model is architecturally different enough that Chat Completions-based wrappers don't translate cleanly.

**Q: How does the 400K token context window compare to competitors?**

GPT-5-Codex's 400K context window is competitive with Claude Opus 4.7 (200K) but below Gemini 1.5 Pro's 1M window. In practice, 400K tokens can fit roughly 300,000 lines of code — more than enough for most single-service repositories. The practical constraint is usually cost, not the hard limit: at $1.75/1M tokens for gpt-5.2-codex input, a full 400K context costs $0.70 per call before any output.

**Q: Should I use GPT-5-Codex or Claude Opus 4.7 for coding tasks?**

Both are excellent, and the choice depends on your existing infrastructure. Claude Opus 4.7 leads SWE-Bench Pro at 64.3% versus GPT-5.3-Codex's 56.8% — a meaningful gap for complex engineering tasks. However, GPT-5.5 leads Terminal-Bench 2.0 at 82.7%. If you're already in the OpenAI ecosystem (using OpenAI APIs for other features, running Codex platform tooling), GPT-5-Codex variants offer tighter integration. If you're starting fresh and raw coding benchmark performance is the priority, Claude Opus 4.7 currently has the edge on SWE-Bench Pro.
