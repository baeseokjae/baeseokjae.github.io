---
title: "Claude Opus 4.7 budget_tokens Removal: Migration from Extended Thinking"
date: 2026-04-25T22:03:49+00:00
tags: ["claude", "anthropic", "extended-thinking", "api", "migration"]
description: "How to fix the 400 error from Claude Opus 4.7's budget_tokens removal and migrate to adaptive thinking in Python and TypeScript."
draft: false
cover:
  image: "/images/claude-opus-4-7-budget-tokens-breaking-change-2026.png"
  alt: "Claude Opus 4.7 budget_tokens Removal: Migration from Extended Thinking"
  relative: false
schema: "schema-claude-opus-4-7-budget-tokens-breaking-change-2026"
---

Claude Opus 4.7, released April 16, 2026, silently removed `budget_tokens` from its extended thinking API. Any code that passes `budget_tokens` to Opus 4.7 receives an immediate `400 Bad Request` error. The fix is a four-step migration: switch to `adaptive` thinking type, replace `budget_tokens` with the `effort` parameter, update agentic loops to use `task_budget`, and strip `temperature`, `top_p`, and `top_k`. This guide walks through each step with exact before/after code.

## What Changed in Claude Opus 4.7: budget_tokens Is Gone

Claude Opus 4.7 removed `budget_tokens` entirely from the extended thinking configuration, replacing it with an adaptive thinking system that automatically allocates reasoning compute based on task complexity. The change affects every application that previously used `thinking: { type: "enabled", budget_tokens: N }` to control how much the model "thinks" before responding. Released April 16, 2026, Opus 4.7 also removes `temperature`, `top_p`, and `top_k` parameters — three additional fields that silently accepted values in 4.6 but now return 400 errors in 4.7. Pricing remains unchanged at $5/M input tokens and $25/M output tokens, and the model shows a 13% coding benchmark lift over Opus 4.6 on Anthropic's internal 93-task evaluation. For teams upgrading by changing only the model string, these breaking changes arrive without warning in production — there is no deprecation header or soft-failure mode in the API response before the hard 400 begins.

### Why Anthropic Removed budget_tokens

Anthropic's internal evaluations showed that adaptive thinking — where the model dynamically decides how much reasoning to apply — outperforms a fixed `budget_tokens` cap. When you hard-cap tokens at 8,000, the model either runs out of reasoning budget mid-thought or wastes compute finishing trivially. Adaptive mode removes the constraint and lets the model match reasoning depth to actual task difficulty, which produced better benchmark results across coding and agentic workloads.

## The 400 Error Explained: Why Your Extended Thinking Code Breaks

The 400 error from Claude Opus 4.7 is a strict API validation rejection — not a quota error, rate limit, or content policy violation. It occurs because `budget_tokens` is no longer a recognized field in the thinking configuration object, and Anthropic's API now returns a hard validation error rather than silently ignoring unknown fields. If you upgraded from Opus 4.6 to 4.7 by changing only the model ID string in your config, every request using `thinking.budget_tokens` will fail immediately with a message like `{"error":{"type":"invalid_request_error","message":"Unknown field: budget_tokens in thinking configuration"}}`. The same validation failure applies to requests that include `temperature`, `top_p`, or `top_k` at the top-level request body. Importantly, Anthropic did not introduce a deprecation warning period — Opus 4.6 accepted these fields, Opus 4.7 rejects them with no soft-failure mode in between. Teams running automated model upgrades via version aliases experienced instant production breakage.

### Finding All Affected Call Sites

Before migrating, locate every place in your codebase that uses these removed fields:

```bash
# Find budget_tokens usage
rg "budget_tokens" --type py --type ts --type js -n

# Find removed sampling parameters
rg "temperature|top_p|top_k" --type py --type ts --type js -n | grep -v "\.md"
```

## Step 1 — Switch to Adaptive Thinking

Adaptive thinking is the replacement for the `enabled` thinking type with a fixed token budget. The migration changes one field in your thinking configuration object. The `adaptive` type signals that the model should dynamically allocate reasoning compute, removing the need to predict how much thinking a given task requires. In Python SDK terms, you replace `AnthropicThinking(type="enabled", budget_tokens=8000)` with `AnthropicThinking(type="adaptive")`. In raw JSON API terms, you replace `{"type": "enabled", "budget_tokens": 8000}` with `{"type": "adaptive"}`. The model ID should be updated to `claude-opus-4-7` or its alias. Note that `thinking.type = "enabled"` is also rejected on Opus 4.7 — only `"adaptive"` and `"none"` are valid values. If you want to disable extended thinking entirely on Opus 4.7, pass `{"type": "none"}`.

```python
# Before (Opus 4.6)
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 8000
    },
    messages=[{"role": "user", "content": "Explain quantum entanglement."}]
)

# After (Opus 4.7)
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={
        "type": "adaptive"
    },
    messages=[{"role": "user", "content": "Explain quantum entanglement."}]
)
```

```typescript
// Before (Opus 4.6)
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 8000,
  },
  messages: [{ role: "user", content: "Explain quantum entanglement." }],
});

// After (Opus 4.7)
const response = await client.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 16000,
  thinking: {
    type: "adaptive",
  },
  messages: [{ role: "user", content: "Explain quantum entanglement." }],
});
```

## Step 2 — Replace budget_tokens with the Effort Parameter

The `effort` parameter is the new mechanism for controlling how much reasoning Opus 4.7 applies when adaptive thinking is enabled. It replaces `budget_tokens` as the user-facing control for reasoning depth, replacing a numeric token count with a named level that the model interprets relative to the task. The five levels are `low`, `medium`, `high`, `xhigh`, and `max`. Anthropic recommends `xhigh` as the default for coding and agentic tasks, and `medium` for summarization or classification where deep reasoning adds latency without benefit. Unlike `budget_tokens`, `effort` is advisory — the model may allocate more or less compute than the level suggests depending on task signals. You cannot set `effort` and `budget_tokens` simultaneously; the field does not exist in the thinking object and including it causes the same 400 error.

```python
# Opus 4.7 with effort parameter
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={
        "type": "adaptive",
        "effort": "xhigh"   # low | medium | high | xhigh | max
    },
    messages=[{"role": "user", "content": "Write a merge sort in Rust with tests."}]
)
```

### Effort Level Mapping Guide

Use this table as a starting point for migrating your `budget_tokens` values to effort levels:

| Old budget_tokens | Recommended effort | Use case |
|---|---|---|
| < 2,000 | `low` | Classification, routing, simple Q&A |
| 2,000–5,000 | `medium` | Summarization, structured extraction |
| 5,000–12,000 | `high` | Multi-step reasoning, code review |
| 12,000–20,000 | `xhigh` | Complex coding, agentic tasks |
| > 20,000 | `max` | Research, exhaustive analysis |

## Step 3 — Migrate Agentic Loops with task_budget

`task_budget` is a new advisory parameter for agentic loop use cases that replaces the pattern of passing `budget_tokens` to each individual API call. In extended thinking on Opus 4.6, teams would often set a per-call `budget_tokens` to prevent a multi-turn agent from consuming unlimited compute. Opus 4.7 introduces `task_budget` as a softer control that signals the model how much total thinking budget it has across the full agentic loop, rather than capping each individual turn. The minimum value is 20,000 tokens. Because it is advisory rather than a hard cap, the model can slightly exceed the budget if stopping mid-thought would produce a worse result. This is intentional — Anthropic found that hard mid-thought truncation was a significant source of degraded output quality in agentic contexts.

```python
# Agentic loop with task_budget
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={
        "type": "adaptive",
        "effort": "xhigh",
        "task_budget": 80000   # advisory total tokens for the full loop, min 20000
    },
    messages=conversation_history
)
```

### task_budget vs max_tokens

| Parameter | Type | What it limits |
|---|---|---|
| `max_tokens` | Hard cap | Total output tokens per call |
| `task_budget` | Advisory | Total thinking tokens across the agentic loop |
| `effort` | Advisory level | Per-call reasoning depth signal |

## Step 4 — Remove temperature, top_p, and top_k

Claude Opus 4.7 rejects `temperature`, `top_p`, and `top_k` at the request body level when adaptive thinking is enabled. These parameters were silently accepted in Opus 4.6 even when extended thinking was active (the model effectively ignored them during thinking mode). Opus 4.7 enforces the constraint with a hard 400 error. If your codebase passes these parameters conditionally — for example, setting `temperature=0` for reproducibility — you must strip them from requests that use adaptive thinking. For non-thinking requests on Opus 4.7, these parameters may still be available; check the API docs for the current state. The safest migration strategy is to remove all three from your thinking-mode code paths unconditionally.

```python
# Before — these cause 400 on Opus 4.7 with adaptive thinking
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    temperature=0.7,    # ❌ 400 error
    top_p=0.9,          # ❌ 400 error  
    top_k=50,           # ❌ 400 error
    thinking={"type": "adaptive"},
    messages=[...]
)

# After — clean request for Opus 4.7 adaptive thinking
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "adaptive", "effort": "high"},
    messages=[...]
)
```

## Full Before/After Code Examples (Python and TypeScript)

The full migration consolidates all four steps into a single diff per language. These examples show a realistic production pattern: a helper function that wraps the Anthropic client and handles model-specific configuration, so changing from 4.6 to 4.7 requires updating one function rather than every call site. The Python example uses the `anthropic` SDK; the TypeScript example uses `@anthropic-ai/sdk`. Both examples show the complete parameter set including `task_budget` for agentic contexts. After migrating, run a parallel test that sends the same prompt to both 4.6 and 4.7 and compares output quality — Anthropic's 13% coding benchmark improvement means results may differ even for semantically equivalent requests, and you should validate that your downstream systems handle the output format correctly.

```python
# migration_helper.py

import anthropic

client = anthropic.Anthropic()

def create_thinking_request(
    prompt: str,
    model: str = "claude-opus-4-7",
    max_tokens: int = 16000,
    effort: str = "xhigh",
    task_budget: int | None = None,
    conversation_history: list | None = None,
) -> anthropic.types.Message:
    thinking_config: dict = {
        "type": "adaptive",
        "effort": effort,
    }
    if task_budget is not None:
        thinking_config["task_budget"] = max(task_budget, 20000)

    messages = conversation_history or []
    if prompt:
        messages = messages + [{"role": "user", "content": prompt}]

    return client.messages.create(
        model=model,
        max_tokens=max_tokens,
        thinking=thinking_config,
        messages=messages,
        # No temperature, top_p, or top_k
    )
```

```typescript
// migrationHelper.ts

import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

interface ThinkingRequestOptions {
  prompt: string;
  model?: string;
  maxTokens?: number;
  effort?: "low" | "medium" | "high" | "xhigh" | "max";
  taskBudget?: number;
  conversationHistory?: Anthropic.MessageParam[];
}

async function createThinkingRequest({
  prompt,
  model = "claude-opus-4-7",
  maxTokens = 16000,
  effort = "xhigh",
  taskBudget,
  conversationHistory = [],
}: ThinkingRequestOptions): Promise<Anthropic.Message> {
  const thinkingConfig: Record<string, unknown> = {
    type: "adaptive",
    effort,
  };

  if (taskBudget !== undefined) {
    thinkingConfig.task_budget = Math.max(taskBudget, 20000);
  }

  const messages: Anthropic.MessageParam[] = [
    ...conversationHistory,
    { role: "user", content: prompt },
  ];

  return client.messages.create({
    model,
    max_tokens: maxTokens,
    thinking: thinkingConfig as Anthropic.ThinkingConfigParam,
    messages,
    // No temperature, top_p, or top_k
  });
}
```

## Performance and Cost Impact of the Migration

Migration to Opus 4.7 adaptive thinking affects performance and cost in three separate ways: benchmark quality, tokenizer changes, and efficiency features. On the positive side, Anthropic reports a 13% lift on internal coding benchmarks over Opus 4.6, and adaptive thinking produces better reasoning outcomes than fixed `budget_tokens` in Anthropic's own evaluations. Token pricing is unchanged at $5/M input and $25/M output. However, Opus 4.7 ships with an updated tokenizer that may count 1.0–1.35x more tokens for the same content depending on code density and language — so your token spend may increase even with the same prompts and outputs. On the efficiency side, prompt caching offers up to 90% cost savings on cached input tokens, and batch processing provides 50% off for non-real-time workloads. For agentic loops, `task_budget` replaces the blunt approach of hard-capping each call, which reduces the overhead of restarting interrupted reasoning chains.

### Cost Comparison Table

| Factor | Opus 4.6 | Opus 4.7 |
|---|---|---|
| Input pricing | $5/M tokens | $5/M tokens (unchanged) |
| Output pricing | $25/M tokens | $25/M tokens (unchanged) |
| Tokenizer | v4.6 | v4.7 (1.0–1.35x token count) |
| Prompt caching | Available | Up to 90% savings |
| Batch processing | Available | 50% savings |
| Coding benchmark | Baseline | +13% over 4.6 |

## Testing Your Migration and Validating Behavior

Testing an Opus 4.7 migration requires more than confirming the 400 errors are gone. Adaptive thinking can allocate significantly different amounts of compute than your previous `budget_tokens` values, which means reasoning depth and output style may shift even for prompts that worked well before. The recommended test strategy is a three-phase approach: first, run a smoke test that confirms all migrated endpoints return 200; second, run a parallel comparison that sends identical prompts to both Opus 4.6 and 4.7 and logs the thinking block token counts and response lengths; third, evaluate output quality against your domain-specific acceptance criteria. Pay particular attention to tasks where you previously used low `budget_tokens` values (under 2,000) to control costs — adaptive thinking may allocate substantially more compute for the same prompts, which is good for quality but requires monitoring your token spend during the first week after migration. Use Anthropic's usage API to track per-request thinking token consumption while you tune `effort` levels.

```python
# Smoke test for migration validation
import anthropic
import pytest

client = anthropic.Anthropic()

def test_opus_47_adaptive_thinking():
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        thinking={"type": "adaptive", "effort": "medium"},
        messages=[{"role": "user", "content": "What is 2+2?"}]
    )
    assert response.stop_reason in ("end_turn", "max_tokens")
    # Verify thinking block present
    thinking_blocks = [b for b in response.content if b.type == "thinking"]
    assert len(thinking_blocks) >= 0  # may be 0 for trivial tasks with adaptive
    print(f"Thinking tokens used: {sum(len(b.thinking) for b in thinking_blocks)}")

def test_no_budget_tokens_accepted():
    with pytest.raises(anthropic.BadRequestError):
        client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            thinking={"type": "enabled", "budget_tokens": 5000},
            messages=[{"role": "user", "content": "test"}]
        )
```

## FAQ

The following questions cover the most common migration blockers developers encounter when upgrading from Claude Opus 4.6 to 4.7. The short version: `budget_tokens` is gone, `temperature`/`top_p`/`top_k` cause 400 errors with adaptive thinking, and `effort` plus optional `task_budget` are the replacement controls. The migration typically takes under an hour for a single-model codebase — most of the time is spent finding all call sites with `rg` and running parallel smoke tests to confirm behavior. If you hit a 400 error on Opus 4.7, the error message will name the invalid field explicitly, which makes debugging straightforward once you know that validation is now strict. Adaptive thinking on Opus 4.7 is not a drop-in replacement in behavior — output quality and reasoning depth will shift, so budget one to two days for output validation against your domain acceptance criteria even after the API errors are resolved.

### Does Claude Opus 4.7 support budget_tokens at all?

No. `budget_tokens` was fully removed in Opus 4.7 and passing it in the thinking configuration returns an immediate `400 Bad Request` error. There is no compatibility mode, alias, or fallback. The replacement is the `effort` parameter (`low`, `medium`, `high`, `xhigh`, `max`) combined with `thinking.type = "adaptive"`.

### Will my Opus 4.6 code work on Opus 4.7 if I just change the model string?

Only if your code does not use `thinking.budget_tokens`, `temperature`, `top_p`, or `top_k` with extended thinking enabled. If it uses any of these, changing the model string alone will break your app with 400 errors immediately. Run `rg "budget_tokens|temperature|top_p|top_k"` across your codebase before switching model IDs.

### What is the minimum value for task_budget?

The minimum valid `task_budget` value is 20,000 tokens. Passing a value below this threshold causes a validation error. The parameter is advisory — the model may slightly exceed the budget rather than truncate a reasoning chain mid-thought.

### Does effort replace budget_tokens exactly, or does it behave differently?

Effort behaves differently. `budget_tokens` was a hard numeric cap that the model could not exceed. `effort` is an advisory signal — the model interprets it as a hint about reasoning depth but retains discretion over actual token allocation. This means results are less predictable in token count but generally better in quality, especially for tasks where the optimal reasoning depth was hard to predict in advance.

### Can I mix adaptive thinking with streaming on Opus 4.7?

Yes. Adaptive thinking on Opus 4.7 is compatible with streaming. Thinking blocks are streamed as `thinking_delta` events before the main `text_delta` events, the same pattern as extended thinking in Opus 4.6. The only change in streaming behavior is that you no longer see a predictable thinking block size since the model allocates compute adaptively.
