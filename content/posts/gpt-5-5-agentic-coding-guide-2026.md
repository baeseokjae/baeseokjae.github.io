---
cover:
  alt: 'GPT-5.5 Agentic Coding Guide: Terminal-Bench 2.0, Computer Use, Workflows'
  image: /images/gpt-5-5-agentic-coding-guide-2026.png
  relative: false
date: 2026-04-26 09:04:22+00:00
description: 'Complete developer guide to GPT-5.5 agentic coding: Terminal-Bench 2.0
  results, computer use setup, Responses API workflows, and benchmark comparisons.'
draft: false
schema: schema-gpt-5-5-agentic-coding-guide-2026
tags:
- gpt-5.5
- agentic coding
- openai codex
- terminal-bench
- ai developer tools
title: 'GPT-5.5 Agentic Coding Guide: Terminal-Bench 2.0, Computer Use, Workflows'
---

GPT-5.5 is OpenAI's first fully retrained base model since GPT-4.5 — codenamed "Spud" internally — and it scores 82.7% on Terminal-Bench 2.0, making it the leading model for autonomous terminal-based coding tasks as of April 2026. If you're deciding whether to migrate Codex pipelines or agentic coding workflows to GPT-5.5, this guide covers benchmarks, setup, computer use, and real workflow patterns.

## What Is GPT-5.5 and Why It's a Big Deal for Developers

GPT-5.5 is OpenAI's most capable agentic model, launched April 23, 2026, to ChatGPT Plus, Pro, Business, and Enterprise subscribers. It is the first fully retrained base model since GPT-4.5 — internally codenamed "Spud" — rebuilt from the ground up for long-horizon agentic tasks rather than fine-tuned on top of GPT-5.4. Unlike incremental releases, GPT-5.5 changes the underlying model weights and reasoning patterns to prioritize terminal operations, computer use, and multi-step autonomous execution. On Terminal-Bench 2.0, it scores 82.7%, beating Claude Opus 4.7 (69.4%) by 13.3 percentage points and edging out Claude Mythos Preview (82.0%) in a near-statistical tie. On GDPval — a benchmark spanning 44 real-world occupations — it reaches 84.9%. For developers running coding agents, the practical implication is clear: GPT-5.5 handles bash-heavy autonomous workflows better than any prior model. However, on SWE-Bench Pro (real GitHub issue resolution), it scores 58.6% versus Claude Opus 4.7's 64.3%, which means the model to choose depends heavily on whether your tasks live in the terminal or in production codebases.

### Why "Fully Retrained" Matters

Most model point releases are fine-tuned variants of a common base. GPT-5.5's full retraining means its tool-calling behavior, context handling, and agentic reasoning were optimized holistically — not layered on top of an older base. The result is measurably more coherent multi-step behavior, fewer tool-call hallucinations mid-chain, and significantly better token efficiency on Codex tasks (using fewer tokens than GPT-5.4 for equivalent work).

## Terminal-Bench 2.0 Explained: What the Benchmark Actually Tests

Terminal-Bench 2.0 is a benchmark designed specifically to evaluate how well AI models operate as autonomous terminal agents — executing bash commands, navigating file systems, writing and debugging code, and completing multi-step engineering tasks without human intervention. Unlike SWE-Bench, which presents isolated GitHub issues as patches, Terminal-Bench 2.0 runs models inside a real shell environment with real tools: `git`, `pytest`, `make`, `curl`, compilers, package managers, and more. Tasks range from setting up a project from scratch to resolving CI failures, profiling bottlenecks, and refactoring across multiple files. Each task is scored on outcome correctness — whether the terminal ended in the desired state — not on intermediate steps. This makes it the most direct proxy for how Codex and similar agentic systems perform in practice. The benchmark's emphasis on stateful, chained operations catches failure modes that simpler coding benchmarks miss: context drift across long command sequences, incorrect assumptions about filesystem state, and error recovery when commands return unexpected output. GPT-5.5's 82.7% score represents a genuine capability threshold; below roughly 70%, models begin failing multi-step tasks at rates that make unsupervised execution impractical.

### How Terminal-Bench 2.0 Differs from SWE-Bench

SWE-Bench Pro measures patch quality against real GitHub issues — a narrower code-transformation task. Terminal-Bench 2.0 requires the model to drive the entire development loop: read, plan, write, run, observe, and iterate. A model that produces correct diffs but can't sequence bash commands reliably will score well on SWE-Bench and poorly on Terminal-Bench. This is exactly the pattern you see with Claude Opus 4.7: 64.3% on SWE-Bench Pro (best in class) versus 69.4% on Terminal-Bench 2.0 (second tier). GPT-5.5 inverts the ranking.

## GPT-5.5 Benchmark Results: Terminal-Bench, SWE-Bench Pro, and GDPval

GPT-5.5's benchmark profile is unambiguous for terminal-centric workloads: it leads on Terminal-Bench 2.0 and GDPval while trailing Claude Opus 4.7 on SWE-Bench Pro. Terminal-Bench 2.0 score of 82.7% makes it the top-ranked model for autonomous shell-based development as of April 2026, with Claude Mythos Preview (82.0%) effectively tied. Claude Opus 4.7 and Gemini 3.1 Pro trail significantly at 69.4% and 68.5% respectively. For agentic knowledge work measured across 44 occupations (GDPval), GPT-5.5's 84.9% reflects strong generalization beyond pure coding. The SWE-Bench Pro result (58.6%) is the one area where developers should pause — if your primary use case is automated PR generation against existing codebases, Claude Opus 4.7 currently outperforms GPT-5.5 by 5.7 percentage points.

| Model | Terminal-Bench 2.0 | SWE-Bench Pro | GDPval |
|---|---|---|---|
| GPT-5.5 | **82.7%** | 58.6% | **84.9%** |
| Claude Mythos Preview | 82.0% | — | — |
| Claude Opus 4.7 | 69.4% | **64.3%** | — |
| Gemini 3.1 Pro | 68.5% | — | — |

### What These Numbers Mean for Your Workflow

Use GPT-5.5 when your agent needs to operate autonomously in a terminal — building, testing, debugging, deploying. Use Claude Opus 4.7 when the primary output is a code patch to a complex existing codebase. The gap on Terminal-Bench 2.0 (13+ points) is large enough to be decisive; the SWE-Bench gap (5.7 points) is meaningful but narrower and may shrink as prompting strategies mature.

## How to Set Up GPT-5.5 for Agentic Coding (Codex + API)

Setting up GPT-5.5 for agentic coding requires either the Codex interface (GUI-based, available directly in ChatGPT) or the Responses API (programmatic, for pipeline integration). The Responses API is the right path for any automated workflow because it exposes tool-calling, multi-turn context management, and structured output natively. With GPT-5.5, the model ID in API calls is `gpt-5.5` for the standard tier and `gpt-5.5-pro` for the high-capacity Pro tier. The Responses API replaced the older Completions endpoint as the recommended interface for agentic applications; it handles tool call sequencing, maintains conversation state, and supports context compaction automatically for long-running sessions. At launch, GPT-5.5 is available to API customers with a valid key in Tier 3 and above. Context window is 1M tokens — large enough for most real codebases.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    input=[
        {
            "role": "user",
            "content": "Clone the repo at /workspace/myapp, run the test suite, and fix any failing tests. Commit the fixes."
        }
    ],
    tools=[
        {"type": "bash"},
        {"type": "text_editor"},
        {"type": "computer_use"}
    ],
    max_tokens=8192
)

print(response.output)
```

### Setting Up in the Codex Interface

For non-programmatic use, the Codex tab in ChatGPT gives you a sandbox environment where GPT-5.5 operates directly on your uploaded project files. To set it up: open ChatGPT → select Codex from the left sidebar → upload your repo or connect GitHub → select `gpt-5.5` as the model → enter your task. Codex handles the execution loop internally and surfaces a diff for review before any changes land. This is the fastest path to evaluating GPT-5.5's agentic capabilities without writing API integration code.

### Connecting a Custom Provider

If you're running an agent framework that treats models as OpenAI-compatible providers (AgentOne, LangChain, AutoGen), add GPT-5.5 as a custom endpoint:

```python
# LangChain example
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-5.5",
    openai_api_key="sk-...",
    temperature=0
)
```

Set `temperature=0` for agentic coding tasks — deterministic behavior is critical for reproducible multi-step execution.

## Computer Use Features: How GPT-5.5 Operates Software End-to-End

GPT-5.5's computer use capability allows the model to perceive a desktop environment through screenshots, then take actions — clicking, typing, scrolling, navigating menus — as if it were a human operator. Unlike the terminal-only Codex interface, computer use lets GPT-5.5 interact with GUI applications: IDEs, browsers, databases, design tools, and any software that doesn't expose a CLI or API. In practice this means GPT-5.5 can open Visual Studio Code, navigate to a failing test in the Problems panel, jump to the source file, edit code, and run the test runner — entirely through the UI. The model takes screenshots at each step, interprets the current state, and decides the next action based on the visible interface. OpenAI's implementation uses a coordinate-based action space (click at x, y; type text; press key) layered on a screen capture loop. The key limitation: computer use is slower than bash execution and more sensitive to UI layout changes. It's best reserved for tasks that genuinely require a GUI — visual debugging, browser-based testing, or working with tools that have no CLI equivalent.

### Enabling Computer Use in the API

```python
response = client.responses.create(
    model="gpt-5.5",
    input=[{"role": "user", "content": "Open the Chrome browser, navigate to localhost:3000, and take a screenshot of the app dashboard."}],
    tools=[{"type": "computer_use"}],
    computer_use={"display_width": 1280, "display_height": 800}
)
```

The model returns action objects (`click`, `type`, `screenshot`) that your runner executes in sequence. You need a real display or virtual framebuffer (Xvfb on Linux) for this to work in headless environments.

### When to Use Computer Use vs. Bash

Choose bash for anything that has a CLI. Choose computer use only when the task requires GUI interaction with no programmatic alternative. Computer use increases latency by 3-5x and token consumption significantly. For most agentic coding workflows, bash plus the text editor tool covers 90% of tasks.

## Building Multi-Step Agentic Workflows with GPT-5.5

Multi-step agentic workflows with GPT-5.5 follow a plan → execute → observe → iterate loop driven by the Responses API's tool-calling capability. The model receives a high-level goal, generates a sequence of tool calls (bash commands, file edits, searches), receives the results of each call, and proceeds to the next step based on observed output. GPT-5.5's full retraining specifically optimized this loop — it maintains goal context across dozens of sequential steps without the context drift that caused earlier models to abandon the original objective mid-workflow. For a typical "implement feature X from spec" task, the model will read the spec, explore the codebase, write the implementation, run tests, fix failures, and produce a commit — all without human checkpoints. The key architectural decision is whether to run the model in a single long Responses API call (stateful, built-in context compaction) or orchestrate it externally with a loop that appends results to a growing message array. For tasks under ~50 steps, the single-call approach is simpler; for longer tasks or workflows that need human checkpoints, external orchestration gives more control.

### Example: Automated Feature Implementation Workflow

```python
from openai import OpenAI
import subprocess

client = OpenAI()

def run_agentic_task(task_description: str, workspace: str):
    messages = [
        {
            "role": "system",
            "content": f"You are an expert developer working in {workspace}. Complete tasks autonomously using bash and file editing tools. Always run tests before finishing."
        },
        {
            "role": "user", 
            "content": task_description
        }
    ]
    
    tools = [
        {"type": "bash"},
        {"type": "text_editor"},
    ]
    
    max_iterations = 30
    for i in range(max_iterations):
        response = client.responses.create(
            model="gpt-5.5",
            input=messages,
            tools=tools,
            max_tokens=4096
        )
        
        # Check if model is done
        if response.stop_reason == "end_turn":
            return response
        
        # Append model output and continue
        messages.append({"role": "assistant", "content": response.output})
        
        # Execute tool calls and append results
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
    
    return response
```

### Prompting for Reliable Multi-Step Execution

Structure your system prompt to include: the project context (language, framework, test runner command), a definition of "done" (tests pass, linter clean, commit made), and explicit instruction to verify outcomes after each step. Vague tasks like "improve the codebase" produce inconsistent results; specific tasks like "add pagination to the /users API endpoint, write unit tests using pytest, ensure all existing tests still pass" give GPT-5.5 a deterministic success criterion.

## GPT-5.5 vs Claude Opus 4.7 vs Gemini 3.1 Pro for Coding Tasks

Choosing between GPT-5.5, Claude Opus 4.7, and Gemini 3.1 Pro for agentic coding comes down to the nature of the task, not a single "best model." GPT-5.5 leads on Terminal-Bench 2.0 (82.7%) and is the clear choice for autonomous terminal operations, CI/CD automation, and workflows that run in shell environments. Claude Opus 4.7 leads on SWE-Bench Pro (64.3%) — about 5.7 points above GPT-5.5 — making it better for automated PR generation against complex existing codebases where patch quality matters more than operational fluency. Gemini 3.1 Pro trails both at 68.5% on Terminal-Bench 2.0, but it may be preferred in multi-modal workflows where video understanding or document-heavy contexts are involved. For enterprise teams running Codex-style agents that write, test, and deploy code autonomously, GPT-5.5 is currently the strongest choice. For teams using AI to triage and fix GitHub issues in existing production codebases, Claude Opus 4.7 holds the edge.

| Task Type | Best Model | Why |
|---|---|---|
| Autonomous terminal operations | GPT-5.5 | +13pts on Terminal-Bench 2.0 |
| Automated PR / patch generation | Claude Opus 4.7 | +5.7pts on SWE-Bench Pro |
| Computer use / GUI automation | GPT-5.5 | Native computer use support |
| Long-context code analysis | GPT-5.5 | 1M token context |
| Knowledge work (44 occupations) | GPT-5.5 | 84.9% on GDPval |

### The Real Workflow Split

Most mature agentic coding pipelines benefit from routing: send terminal-heavy tasks to GPT-5.5, send patch-generation tasks to Claude Opus 4.7. Both expose OpenAI-compatible APIs (Anthropic via the Messages API), so routing at the orchestration layer is straightforward. The added latency of model selection is negligible compared to the accuracy gains from specialization.

## Pricing Breakdown: GPT-5.5 vs GPT-5.5 Pro — Which Is Right for You?

GPT-5.5 is priced at $5 per 1M input tokens and $30 per 1M output tokens — double GPT-5.4's pricing. However, because GPT-5.5 uses fewer tokens than GPT-5.4 for equivalent Codex tasks, OpenAI estimates an effective cost increase of approximately 20% for the same workload volume. GPT-5.5 Pro is aimed at high-throughput enterprise deployments, priced at $30/1M input tokens and $180/1M output tokens — 6x the standard tier on outputs. For most developers and teams, GPT-5.5 standard is the right choice. GPT-5.5 Pro becomes relevant when you're running hundreds of concurrent agentic sessions with strict SLA requirements, need dedicated capacity, or are operating in regulated environments that require isolated compute. The token efficiency improvement (GPT-5.5 uses fewer tokens for the same Codex tasks) partially offsets the price increase — for workflows with a high ratio of tool-call results to generated text, the real cost delta is often smaller than the headline 2x price suggests.

| Tier | Input | Output | Best For |
|---|---|---|---|
| GPT-5.5 | $5/1M | $30/1M | Most teams, standard pipelines |
| GPT-5.5 Pro | $30/1M | $180/1M | Enterprise, high concurrency, SLA-critical |
| GPT-5.4 (prior) | $2.50/1M | $15/1M | Cost-sensitive, simpler tasks |

### Estimating Costs for a Typical Agentic Pipeline

A single agentic coding task (implement feature, write tests, fix failures, commit) typically generates 2,000–8,000 output tokens across tool calls. At $30/1M outputs, that's $0.06–$0.24 per task. Running 100 tasks per day costs $6–$24/day — well within the budget of most engineering teams. The GPT-5.5 Pro tier at $180/1M outputs scales that to $36–$144/day for the same volume, justified only if uptime guarantees or concurrency limits make standard tier insufficient.

## Prompting Best Practices for Agentic Coding with GPT-5.5

Effective prompting for GPT-5.5 agentic coding tasks follows five concrete principles that directly improve task completion rates and reduce wasted tool calls. First, specify the language, framework, and test runner explicitly — "Python 3.11, FastAPI, pytest" is better than "a backend API project." Second, define the success criterion precisely: "all tests pass, mypy reports no errors, the endpoint returns 200 for the happy path." Third, provide the correct start state: tell the model whether the environment is clean, whether dependencies are installed, and where relevant code lives. Fourth, for long tasks, give GPT-5.5 explicit checkpoints: "after writing the implementation, run tests before making additional changes." Fifth, constrain the scope: open-ended tasks like "improve code quality" generate unpredictable and sometimes destructive rewrites; scoped tasks like "extract the authentication logic from app.py into a new auth.py module" produce reliable, reviewable output. GPT-5.5's full retraining makes it more robust to ambiguous prompts than GPT-5.4, but specificity still directly correlates with success rate on Terminal-Bench-style tasks.

### Prompt Template for Agentic Coding Tasks

```
System:
You are an expert {language} developer working on a {framework} project located at {path}.
Test runner: {test_command}
Linter: {lint_command}
Success criteria: all tests pass, no lint errors, implementation matches spec.

User:
Task: {specific_task_description}
Context: {relevant_files_or_functions}
Constraints: {scope_limits}
Do not modify files outside {allowed_directories}.
After completing the implementation, run tests and fix any failures before stopping.
```

### Common Prompting Mistakes

- **Too vague**: "Make the API faster" → model doesn't know what "faster" means or which API
- **Missing context**: Not mentioning the test framework → model guesses wrong runner
- **No success criterion**: Model stops after writing code without verifying it works
- **Unbounded scope**: "Refactor the whole codebase" → model makes changes in unexpected files

## FAQ

**What is GPT-5.5 and when was it released?**
GPT-5.5 is OpenAI's first fully retrained base model since GPT-4.5, launched April 23, 2026. It was built from scratch (not fine-tuned from GPT-5.4) to optimize for agentic, terminal-based, and computer-use workflows.

**How does GPT-5.5 perform on Terminal-Bench 2.0?**
GPT-5.5 scores 82.7% on Terminal-Bench 2.0 as of April 2026, leading all publicly evaluated models. Claude Mythos Preview scores 82.0% (near tie), while Claude Opus 4.7 scores 69.4% and Gemini 3.1 Pro scores 68.5%.

**Is GPT-5.5 better than Claude Opus 4.7 for coding?**
It depends on the task. GPT-5.5 leads on Terminal-Bench 2.0 by 13+ points, making it better for autonomous shell-based workflows. Claude Opus 4.7 leads on SWE-Bench Pro by 5.7 points, making it better for automated patch generation on existing codebases.

**What does GPT-5.5 computer use actually do?**
GPT-5.5 computer use allows the model to take screenshots of a desktop environment, then take actions — click, type, scroll, navigate menus — to operate GUI applications without a CLI or API. It's slower than bash but enables automation of any software with a visual interface.

**How much does GPT-5.5 API access cost?**
GPT-5.5 standard is $5/1M input tokens and $30/1M output tokens. GPT-5.5 Pro is $30/1M input and $180/1M output. The standard tier is appropriate for most teams; Pro is for enterprise use cases requiring dedicated capacity or strict SLAs.