---
title: "Claude Opus 4.7 Developer Guide: xhigh Effort, Task Budgets, and Migration"
date: 2026-05-07T09:04:49+00:00
tags: ["Claude Opus 4.7", "Anthropic", "AI API", "developer guide", "task budgets", "xhigh effort", "migration"]
description: "Complete Claude Opus 4.7 developer guide: xhigh effort levels, task budgets, adaptive thinking, breaking API changes, and migration from Opus 4.6."
draft: false
cover:
  image: "/images/claude-opus-4-7-developer-guide-2026.png"
  alt: "Claude Opus 4.7 Developer Guide: xhigh Effort, Task Budgets, and Migration"
  relative: false
schema: "schema-claude-opus-4-7-developer-guide-2026"
---

Claude Opus 4.7 is Anthropic's most capable model as of April 2026, scoring 87.6% on SWE-bench Verified and introducing a redesigned thinking system that replaces manual `budget_tokens` with effort-based adaptive thinking. If you're upgrading from Opus 4.6, four breaking API changes require code updates before your apps will run.

## What's New in Claude Opus 4.7

Claude Opus 4.7, released April 16, 2026, represents a step-change in both coding capability and agentic architecture. The headline benchmark is SWE-bench Verified at 87.6% — up from 80.8% on Opus 4.6 — and SWE-bench Pro at 64.3% (up from 53.4%). On CursorBench, the real-world coding benchmark, Opus 4.7 scores 70% versus 58% for Opus 4.6. These gains come primarily from architectural improvements to multi-step reasoning: the model now plans across more steps before committing to an action, which matters most for complex debugging and refactoring tasks. Vision capability received an equally dramatic upgrade — visual acuity improved from 54.5% to 98.5%, and the model now supports 3.75MP images, three times the resolution of Opus 4.6. For computer use, Opus 4.7 scores 78.0% on OSWorld-Verified, the leading score among currently available models. Pricing stayed flat at $5/M input and $25/M output tokens, but a new tokenizer encodes the same text using up to 35% more tokens — so your actual bills will increase even without code changes.

| Benchmark | Opus 4.6 | Opus 4.7 | Change |
|---|---|---|---|
| SWE-bench Verified | 80.8% | 87.6% | +6.8pp |
| SWE-bench Pro | 53.4% | 64.3% | +10.9pp |
| CursorBench | 58% | 70% | +12pp |
| Visual Acuity | 54.5% | 98.5% | +44pp |
| OSWorld Computer Use | — | 78.0% | new |

## The Five Effort Levels: low, medium, high, xhigh, and max

Claude Opus 4.7's effort levels are a ranked abstraction over the model's internal thinking budget, replacing the manual `budget_tokens` integer you had to guess at in Opus 4.6. The five levels — `low`, `medium`, `high`, `xhigh`, and `max` — map to progressively larger internal thinking allocations. `low` uses roughly the same thinking depth as a non-extended-thinking call and is best for simple Q&A, summarization, or single-function code generation. `medium` suits multi-file edits or short agentic chains where you want some reasoning depth without excessive latency. `high` is the general-purpose pick for most production workloads: complex debugging, architecture reviews, and document analysis. `xhigh` is Claude Code's default for agentic tasks and gives the model significant headroom to plan before touching files. `max` is uncapped — use it only for research-grade tasks where cost is secondary and answer quality is paramount. The practical rule of thumb: start at `high`, step up to `xhigh` when the model visibly misses steps in multi-file tasks, and reserve `max` for tasks where a single wrong decision costs more than the extra inference spend.

```python
import anthropic

client = anthropic.Anthropic()

# Standard high-effort call
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=8096,
    thinking={
        "type": "enabled",
        "effort": "high"
    },
    messages=[{"role": "user", "content": "Refactor this auth module for async support."}]
)
```

### Effort Level Selection Guide

| Effort | Latency | Cost | Best For |
|---|---|---|---|
| low | ~1s | $$ | Q&A, summaries, lookup |
| medium | ~3s | $$$ | Single-file edits, short chains |
| high | ~8s | $$$$ | Complex debugging, arch reviews |
| xhigh | ~20s | $$$$$ | Multi-repo agentic tasks |
| max | varies | $$$$$$ | Research, proof generation |

## xhigh Effort Deep Dive: Why Claude Code Defaults to It

`xhigh` is Claude Code's default effort level because agentic coding tasks require the model to hold a large working context simultaneously — current file state, test output, dependency graph, and user intent — before writing a single line. At `high` effort, the model reliably handles changes within one file but frequently misses implicit coupling between files (for example, updating a function signature but not its callers in sibling modules). At `xhigh`, the extra thinking headroom allows the model to trace call graphs before editing, which reduces multi-file regression rates by an estimated 40% based on internal Anthropic evaluations at the time of release. The cost difference between `high` and `xhigh` is roughly 2–3x on thinking-token spend; for a typical Claude Code session editing 5–10 files, this translates to a few cents of additional inference cost per session. The economic argument for defaulting to `xhigh` is straightforward: the cost of a missed cross-file bug (manual debugging time, CI churn, delayed PR) far exceeds the marginal thinking cost. When to step back to `high` or `medium`: read-only tasks (explaining code, generating docs), single-file changes with no external callers, and batch jobs where you're running thousands of identical operations and can afford occasional misses.

```python
# Claude Code equivalent — xhigh for agentic coding
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16384,
    thinking={
        "type": "enabled",
        "effort": "xhigh"
    },
    system="You are an autonomous coding agent. Plan before you act.",
    messages=[{"role": "user", "content": "Add rate limiting to all API endpoints."}]
)
```

## Task Budgets: The New Way to Control Agentic Token Spend

Task budgets are a beta feature in Claude Opus 4.7 that let you give the model a total token allowance for an agentic session, then watch the model use that countdown to self-regulate pacing and gracefully wrap up work before hitting the limit. A task budget is passed via the `anthropic-beta: task-budgets-2026-03` request header and an `output_config` block in the request body. The minimum task budget is 20,000 tokens; for agentic coding tasks, Anthropic recommends 50,000–128,000 tokens. When roughly 20% of the budget remains, the model begins summarizing instead of expanding, avoids opening new files, and writes transition notes so the next session can pick up cleanly. This is qualitatively different from simply setting `max_tokens`: a high `max_tokens` value tells the model how long a single response can be, while a task budget tells the model how much total computation the whole job is worth. The practical effect is that long-running agents stop mid-task gracefully rather than truncating mid-sentence when they run out of tokens.

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    extra_headers={
        "anthropic-beta": "task-budgets-2026-03"
    },
    thinking={
        "type": "enabled",
        "effort": "xhigh"
    },
    output_config={
        "task_budget_tokens": 80000
    },
    messages=[{
        "role": "user",
        "content": "Audit and fix all security issues in this repository."
    }]
)

# Check budget usage in response metadata
if hasattr(response, 'usage'):
    print(f"Budget used: {response.usage.task_budget_tokens_used}")
    print(f"Budget remaining: {response.usage.task_budget_tokens_remaining}")
```

### When to Set a Task Budget

Set a task budget any time you're running an autonomous agent loop that could generate many tool calls — file reads, web searches, code execution — and you want cost predictability. Without a task budget, an agent loop on a large codebase can silently consume hundreds of thousands of tokens before you notice. With a task budget, the model treats the allowance as a resource to manage, not a limit to test. A reasonable heuristic: set the budget to 2–3x the token count of your initial prompt plus expected tool outputs.

## Adaptive Thinking: What Replaced Manual budget_tokens

Adaptive thinking is the internal mechanism behind Opus 4.7's effort levels — it is what actually replaced the manual `budget_tokens` integer from Opus 4.6's extended thinking API. In Opus 4.6, you had to supply an explicit `budget_tokens` integer (e.g., `32000`) and the model would use up to that many tokens on its internal reasoning chain before producing a response. In practice, this was difficult to tune: too low and the model skipped reasoning steps; too high and you paid for thinking tokens you didn't need. Adaptive thinking replaces this with a model-side allocation policy. When you select `effort: "xhigh"`, the model dynamically allocates thinking tokens based on task complexity — simple parts of a prompt get fewer thinking tokens, while novel or ambiguous sub-problems get more. Empirically, this produces better results at lower total thinking-token spend than a static `budget_tokens` value set to the theoretical maximum. The tradeoff: you lose direct control over thinking-token counts. If you were using `budget_tokens` for cost-bounding (capping spend on a cheap endpoint), use task budgets instead — they provide cost control at the session level rather than per-call.

```python
# Opus 4.6 style — deprecated in 4.7
# response = client.messages.create(
#     model="claude-opus-4-6",
#     thinking={"type": "enabled", "budget_tokens": 32000},
#     ...
# )

# Opus 4.7 style — effort replaces budget_tokens
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=8096,
    thinking={
        "type": "enabled",
        "effort": "high"  # model allocates thinking tokens adaptively
    },
    messages=[{"role": "user", "content": "Your prompt here"}]
)
```

## Migration Guide: Breaking Changes from Opus 4.6 to 4.7

There are four breaking changes when migrating from claude-opus-4-6 to claude-opus-4-7. Each requires a code update; none have automatic fallback behavior — requests with old-style parameters will return a 400 error.

**Breaking Change 1: `budget_tokens` removed from thinking config**

The `thinking.budget_tokens` field is no longer accepted. Replace with `thinking.effort`.

```python
# BEFORE (Opus 4.6)
thinking={"type": "enabled", "budget_tokens": 50000}

# AFTER (Opus 4.7)
thinking={"type": "enabled", "effort": "high"}
```

**Breaking Change 2: Model ID is `claude-opus-4-7` (not `claude-opus-4-7-20260416`)**

Opus 4.7 uses a simplified model ID without the date suffix. The dated variant is not accepted.

```python
# BEFORE
model="claude-opus-4-6-20251201"

# AFTER
model="claude-opus-4-7"
```

**Breaking Change 3: `output_config` replaces `max_tokens_to_sample` for agentic configs**

If you were passing `max_tokens_to_sample` in a non-standard field, the new structure is `output_config.max_tokens`.

```python
# BEFORE — non-standard field some integrations used
# "max_tokens_to_sample": 8096

# AFTER — use output_config for advanced output settings
output_config={
    "max_tokens": 8096,
    "task_budget_tokens": 80000  # optional
}
```

**Breaking Change 4: New tokenizer — recalibrate token budgets**

The Opus 4.7 tokenizer encodes the same English text using up to 35% more tokens than Opus 4.6. Any hardcoded token limits in your application need to be increased proportionally, or you will hit `max_tokens` truncation on responses that previously fit.

| Token Budget | Opus 4.6 Equivalent | Adjustment |
|---|---|---|
| 4,096 | ~5,500 Opus 4.6 tokens | Increase to 5,500+ |
| 8,192 | ~11,000 Opus 4.6 tokens | Increase to 11,000+ |
| 32,000 | ~43,000 Opus 4.6 tokens | Increase to 43,000+ |

## API Setup and Code Examples (Python SDK)

Claude Opus 4.7 API setup requires the Anthropic Python SDK version 0.52.0 or later, which added support for the `effort` field in the thinking config and the `output_config` block. Install or upgrade with `pip install anthropic>=0.52.0`.

```python
import anthropic

# Verify SDK version
print(anthropic.__version__)  # should be 0.52.0+

client = anthropic.Anthropic(api_key="your-api-key")

# Basic call with adaptive thinking
def analyze_code(code: str, effort: str = "high") -> str:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8096,
        thinking={
            "type": "enabled",
            "effort": effort
        },
        messages=[{
            "role": "user",
            "content": f"Review this code for bugs and security issues:\n\n{code}"
        }]
    )
    # Extract text blocks (thinking blocks are separate)
    text_blocks = [b for b in response.content if b.type == "text"]
    return text_blocks[0].text if text_blocks else ""

# Agentic session with task budget
def run_agent_session(task: str, budget: int = 80000) -> dict:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        extra_headers={"anthropic-beta": "task-budgets-2026-03"},
        thinking={"type": "enabled", "effort": "xhigh"},
        output_config={"task_budget_tokens": budget},
        messages=[{"role": "user", "content": task}]
    )
    return {
        "response": response.content,
        "budget_used": getattr(response.usage, "task_budget_tokens_used", None),
        "stop_reason": response.stop_reason
    }
```

### Streaming with Extended Thinking

When streaming Opus 4.7 responses with thinking enabled, thinking blocks arrive before text blocks. Filter them correctly:

```python
with client.messages.stream(
    model="claude-opus-4-7",
    max_tokens=4096,
    thinking={"type": "enabled", "effort": "high"},
    messages=[{"role": "user", "content": "Explain this architecture..."}]
) as stream:
    for event in stream:
        if hasattr(event, 'type'):
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    print("[Thinking block started]")
                elif event.content_block.type == "text":
                    print("[Response started]")
            elif event.type == "content_block_delta":
                if hasattr(event.delta, 'text'):
                    print(event.delta.text, end="", flush=True)
```

## Benchmarks and Performance vs. GPT-5.5 and Gemini 3.1 Pro

Claude Opus 4.7 holds the top position on SWE-bench Verified at 87.6%, ahead of GPT-5.5 (approximately 83% based on public leaderboard data) and Gemini 3.1 Pro (approximately 79%). On SWE-bench Pro — a harder variant requiring changes across multiple files — Opus 4.7 scores 64.3%, which represents a meaningful lead over competitors that have not published Pro scores. The CursorBench result of 70% is particularly notable because it measures performance on real-world developer tasks drawn from actual Cursor IDE sessions, not synthetic benchmarks. Context window parity: Opus 4.7 and GPT-5.5 both support 1M token contexts, while Gemini 3.1 Pro extends to 2M. For pricing comparison, GPT-5.5 costs approximately $15/M input and $60/M output — roughly 3x the price of Opus 4.7 at $5/$25. Gemini 3.1 Pro pricing is roughly equivalent to Opus 4.7 on input but higher on output. The practical conclusion for most developer teams: Opus 4.7 delivers the best coding benchmark results at mid-range frontier pricing.

| Model | SWE-bench Verified | Input $/M | Output $/M | Context |
|---|---|---|---|---|
| Claude Opus 4.7 | 87.6% | $5 | $25 | 1M |
| GPT-5.5 | ~83% | $15 | $60 | 1M |
| Gemini 3.1 Pro | ~79% | ~$5 | ~$30 | 2M |

## Real Cost Analysis: The Tokenizer Change and What It Means

The Opus 4.7 tokenizer is a significant hidden cost factor that Anthropic's "unchanged pricing" announcement underemphasizes. The new tokenizer encodes English prose using up to 35% more tokens than the Opus 4.6 tokenizer — which means the same input text costs 35% more to process, even though the per-token price is unchanged. The cause is a shift toward a more granular tokenization strategy that improves model reasoning on code and structured data but increases token counts for natural language. The financial impact compounds across both input and output: a 10,000-token Opus 4.6 prompt may become a 13,500-token Opus 4.7 prompt, and the model's longer internal reasoning chains (from adaptive thinking) further increase output token counts. For teams running high-volume APIs — batch processing, document analysis, code review pipelines — expect effective cost increases of 25–45% when migrating from Opus 4.6, even if the per-token price looks the same. To measure your actual exposure: run 100 representative prompts through the Anthropic token counter API against both model IDs before migrating, and compute the average token ratio. Use this ratio to adjust your cost projections and rate-limit configurations before full rollout.

```python
# Measure tokenizer difference before migrating
def compare_tokenization(text: str) -> dict:
    # Uses the tokenize endpoint (not a message call)
    result_46 = client.messages.count_tokens(
        model="claude-opus-4-6-20251201",
        messages=[{"role": "user", "content": text}]
    )
    result_47 = client.messages.count_tokens(
        model="claude-opus-4-7",
        messages=[{"role": "user", "content": text}]
    )
    return {
        "opus_4_6_tokens": result_46.input_tokens,
        "opus_4_7_tokens": result_47.input_tokens,
        "ratio": result_47.input_tokens / result_46.input_tokens
    }
```

## When to Use Opus 4.7 vs. Sonnet 4.6

Model selection between Opus 4.7 and Sonnet 4.6 comes down to three factors: task complexity, latency tolerance, and cost budget. Opus 4.7 wins on any task that requires multi-file reasoning, long planning chains, or vision analysis — its performance gap on complex coding tasks is large enough to justify the price difference. Sonnet 4.6 wins when you need fast responses under 2 seconds, when the task is straightforward (single-function generation, classification, extraction), or when you're running high-volume pipelines where cost per call matters more than peak performance. A practical segmentation for most teams: use Sonnet 4.6 as the default for your product's real-time interactive features (chat, autocomplete, Q&A), and reserve Opus 4.7 for background agentic tasks (automated code review, batch analysis, autonomous PR generation). This two-tier approach typically reduces inference spend by 60–70% compared to using Opus 4.7 everywhere, while preserving top-tier quality on the tasks that actually benefit from it. If you're already using Claude Code, xhigh effort on Opus 4.7 is the right default for coding agents and there's no reason to downgrade to Sonnet for agentic sessions — the task budget feature makes the cost predictable.

| Scenario | Recommended Model | Effort |
|---|---|---|
| Autonomous coding agent | Opus 4.7 | xhigh + task budget |
| Code review (batch) | Opus 4.7 | high |
| Real-time chat | Sonnet 4.6 | n/a |
| Document Q&A | Sonnet 4.6 | n/a |
| Complex architecture design | Opus 4.7 | max |
| Single-function generation | Sonnet 4.6 | n/a |

---

## FAQ

**Q: What is the model ID for Claude Opus 4.7?**
The model ID is `claude-opus-4-7` — no date suffix. Using the old pattern `claude-opus-4-7-20260416` will return a 400 error. Update your model strings before migrating.

**Q: Does Claude Opus 4.7 still support `budget_tokens` in the thinking config?**
No. The `budget_tokens` field was removed as a breaking change. Replace `thinking.budget_tokens` with `thinking.effort` using one of the five string values: `low`, `medium`, `high`, `xhigh`, or `max`. Requests with `budget_tokens` will return a 400 validation error.

**Q: What is the minimum task budget for Claude Opus 4.7?**
The minimum `task_budget_tokens` value is 20,000. Anthropic recommends 50,000–128,000 tokens for agentic coding sessions. You must also include the `anthropic-beta: task-budgets-2026-03` request header; without it, the `output_config` block is ignored.

**Q: Why is my Opus 4.7 bill higher even though pricing is the same?**
The new tokenizer encodes the same text using up to 35% more tokens than the Opus 4.6 tokenizer. Since you pay per token, the same prompts cost more. Use the `messages.count_tokens` endpoint to measure the ratio for your specific workloads before full migration.

**Q: When should I use `xhigh` versus `max` effort?**
Use `xhigh` for production agentic tasks where you want high-quality multi-step reasoning at a predictable cost. Use `max` only for research-grade tasks — proof generation, exhaustive security audits, or novel architecture design — where answer quality is the top priority and you've explicitly decided cost is secondary. Max effort has no internal token cap on thinking, so costs are unpredictable on long tasks without a task budget.
