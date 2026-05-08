---
title: "Claude Code Task Budgets Guide 2026: Control Token Spend in Agentic Sessions"
date: 2026-05-07T06:00:00+00:00
tags: ["claude-code", "task-budgets", "claude-opus-4-7", "token-optimization", "agentic-sessions", "guide"]
description: "Claude Code task budgets 2026: how to set token spend limits for agentic sessions via API and CLI, avoid cost explosions, and tune budgets for real workloads."
draft: false
cover:
  image: "/images/claude-code-task-budgets-guide-2026.png"
  alt: "Claude Code Task Budgets Guide 2026: Control Token Spend in Agentic Sessions"
  relative: false
schema: "schema-claude-code-task-budgets-guide-2026"
---

Average enterprise Claude Code cost is $13 per developer per active day — and a single agentic prompt can burn 50,000 to 300,000 tokens, with users reporting single prompts eating 30-90% of a 5-hour budget. Agent teams using plan mode consume 7x more tokens than standard sessions. Before task budgets existed, the only options for controlling this spend were max_tokens (which cuts off mid-task) or manual session management. Task budgets, introduced in public beta on Claude Opus 4.7 in 2026, give you a third option: a soft advisory limit that lets Claude finish gracefully when approaching the budget, reporting progress and pausing rather than cutting off silently. Here's how to use them.

## What Are Claude Code Task Budgets? (And Why They Matter in 2026)

Task budgets are an advisory token spending limit for agentic Claude sessions, available in public beta on Claude Opus 4.7 via the `task-budgets-2026-03-13` beta header. Unlike max_tokens — which is a hard ceiling on output tokens per request — task budgets operate at the session level, tracking cumulative token usage across an entire agentic loop including thinking tokens, tool call outputs, and generated text. When Claude approaches the budget limit, it shifts behavior: it finishes current work, summarizes what was completed, and pauses to report status rather than cutting off mid-execution. The key distinction matters practically: max_tokens prevents runaway single responses; task budgets prevent runaway multi-step agentic loops. Enterprise Claude Code costs run $150-250 per developer per month for active users, and 40-70% savings are achievable through context management and budget controls. The minimum accepted task_budget.total is 20,000 tokens — values below this return a 400 error. Task budgets work only on Claude Opus 4.7 at launch; older models ignore the parameter.

## How the Budget Countdown Works Across an Agentic Loop

The budget countdown mechanism operates server-side. When you set a task budget, Claude receives a continuously updated internal signal tracking how many tokens have been consumed against the total budget across the entire agentic loop — including thinking tokens, tool call outputs, and generated text. As the budget depletes, Claude's behavior adapts progressively. At roughly 70% consumed, Claude may start scoping sub-tasks more aggressively. At 85-90%, it shifts toward wrapping up current work rather than starting new steps. When the budget is nearly exhausted, Claude pauses and reports: something like "28 of 35 subtasks complete, estimated 8,000 tokens to finish remaining work." This countdown is advisory, not a hard stop — Claude may slightly exceed the budget to finish a thought or tool call in progress. The "graceful finish" model is deliberately different from max_tokens truncation, which can leave partially modified files or incomplete state that requires manual cleanup. Budget awareness is also lossy at the per-step level: Claude knows the cumulative budget state but may not perfectly predict how many tokens an upcoming tool call will consume.

## Setting Up Task Budgets via the Anthropic API

Task budgets require the `task-budgets-2026-03-13` beta header and are configured in the `output_config` object:

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-7-20261101",
    max_tokens=16000,
    betas=["task-budgets-2026-03-13"],
    output_config={
        "task_budget": {
            "type": "tokens",
            "total": 100000   # advisory limit across the full agentic session
        }
    },
    messages=[{
        "role": "user",
        "content": "Review all Python files in the repo and fix type annotation issues"
    }]
)
```

The `total` field is the advisory budget in tokens. The `type` field currently only supports `"tokens"`. For multi-turn sessions where you want to carry the budget across context compaction events, add the `remaining` field (covered in its own section). The task budget is separate from — and layered under — max_tokens. max_tokens controls the ceiling for a single response generation; task_budget controls cumulative spend across the full loop. Both parameters should be set: max_tokens as the per-request safety net, task_budget as the session-level spending envelope.

A 400 error returns if `total` is below 20,000. Budget values that are clearly too small for the requested task cause Claude to aggressively reduce scope or decline to start — plan for at least 2x your p50 observed spend for similar tasks.

## Using Task Budgets in the Claude Code CLI

In the Claude Code CLI, the `/config` command sets task budgets for the session:

```bash
# Set a 50,000 token task budget for this session
/config task_budget 50000

# Check current budget status
/config

# Clear the budget limit for this session
/config task_budget 0
```

When the session approaches the budget limit, Claude Code reports progress inline: current subtask status, percentage complete, estimated tokens to finish. This transforms agentic sessions from "fire and forget, then check the bill" to active session management. The CLI budget setting persists for the session but resets when you start a new Claude Code session. For team deployments, budget defaults can be set in the organization settings or via environment configuration rather than requiring each developer to set them manually.

The interaction between the CLI budget and API parameters: when Claude Code calls the Anthropic API internally, it passes your session budget as the task_budget parameter. You don't need to configure the API directly when using the CLI — the `/config task_budget` command handles it.

## Task Budgets vs. max_tokens: Understanding the Difference

These two parameters control different dimensions of token usage and are frequently confused:

| | max_tokens | task_budget |
|---|---|---|
| **Scope** | Single API response | Entire agentic session |
| **Type** | Hard ceiling | Advisory hint |
| **What it counts** | Output tokens only | All tokens (thinking + output + tool calls) |
| **When exceeded** | Response cuts off mid-generation | Claude wraps up gracefully |
| **Use case** | Prevent runaway single outputs | Control session-level spend |
| **Required?** | Yes (always required) | No (optional beta feature) |

The practical implication: always set both. max_tokens as a per-request safety net (16,000-64,000 tokens depending on task complexity), task_budget as the session envelope. A task budget without max_tokens could still produce a single runaway 100,000-token response; max_tokens without task_budget won't prevent an agentic loop from consuming budget across 50 individual tool calls each under the max_tokens ceiling.

The "advisory" nature of task_budget is intentional. Anthropic's design preference is for Claude to finish work coherently rather than stopping mid-operation. A hard cutoff at the budget boundary would create worse outcomes (partial file modifications, incomplete database migrations) than a slight overrun on the budget. In practice, task budget overruns are small — typically under 10% of the budget total.

## Choosing the Right Budget Size for Your Tasks

Setting budgets without measurement leads to two failure modes: budgets too small that cause aggressive scope reduction or refusal-like behavior, and budgets too large that don't actually constrain anything. The right approach:

**1. Measure first.** Run your target tasks without task_budget enabled. Collect the token counts from several representative runs. Calculate p50 (median), p90 (90th percentile), and p99 (99th percentile) spend.

**2. Set budget based on percentile.** For tasks where you want Claude to complete most runs fully: set budget at p90. For tasks where you're willing to accept some scope reduction to bound cost: set at p75. For strict cost control with acceptable quality reduction: set at p50.

**3. Budget by task type:**

| Task Type | Typical Range | Recommended Budget |
|-----------|--------------|-------------------|
| Simple bug fix | 10k-40k tokens | 50k (above minimum) |
| Feature implementation | 50k-200k | 150k-250k |
| Codebase-wide refactor | 200k-500k+ | 300k-600k |
| Documentation generation | 30k-100k | 100k-150k |
| Full test suite creation | 100k-400k | 300k-500k |

**4. Account for Opus 4.7 cost multiplier.** Opus 4.7 costs approximately 1.7x more than Sonnet 4.6. The April 2026 tokenizer update can inflate effective costs up to 35% for code-heavy content. Budget headroom matters more than it did on previous models.

## Carrying Budget Across Context Compaction with 'remaining'

Context compaction — Claude's mechanism for summarizing long conversation history to stay within context limits — creates a budget tracking problem: after compaction, the session looks "fresh" to a naive implementation, resetting accumulated spend. The `remaining` field solves this:

```python
# First turn: set total budget
response = client.beta.messages.create(
    model="claude-opus-4-7-20261101",
    max_tokens=16000,
    betas=["task-budgets-2026-03-13"],
    output_config={
        "task_budget": {
            "type": "tokens",
            "total": 200000,
            "remaining": 200000  # same as total on first call
        }
    },
    messages=[...]
)

# Track spend
tokens_used = response.usage.input_tokens + response.usage.output_tokens
remaining = 200000 - tokens_used

# On compaction event (when context is summarized), carry remaining budget
response = client.beta.messages.create(
    model="claude-opus-4-7-20261101",
    max_tokens=16000,
    betas=["task-budgets-2026-03-13"],
    output_config={
        "task_budget": {
            "type": "tokens",
            "total": 200000,
            "remaining": remaining  # carry through compaction
        }
    },
    messages=[compacted_context]
)
```

Claude Code's built-in auto-compaction (which achieves 60-80% context size reduction) handles the `remaining` field automatically when task budgets are enabled via CLI. For custom API integrations, you must track and pass `remaining` manually. Failing to carry `remaining` through compaction effectively resets the budget counter — Claude sees a fresh context with full budget, defeating the purpose of the budget limit.

## Task Budgets + Effort Parameter: Combining Depth and Breadth Control

The effort parameter and task budgets control orthogonal dimensions of agentic behavior:

- **Effort** (`high`, `xhigh`, `max`) controls reasoning depth per step — how thoroughly Claude thinks through each decision before acting
- **Task budget** controls total breadth — how much total work Claude does across the full session

In Claude Code, xhigh effort is now the default and increases token spend 1-1.35x compared to Opus 4.6 behavior. The interaction: high effort with a small task budget means Claude thinks deeply about each step but stops earlier. xhigh effort with a large budget means deep reasoning across many steps.

Practical recommendations:
- **Deterministic, well-specified tasks** (add type annotations to these files): `effort: high` + budget at p75 of typical spend
- **Judgment-heavy tasks** (refactor this module for better testability): `effort: xhigh` + budget at p90 with larger headroom
- **Open-ended exploration** (find security issues in this codebase): `effort: max` + generous budget, monitor actively

Setting task budgets without considering effort means you may be paying for deep thinking that generates too few steps, or getting shallow thinking across many steps. Tune both parameters together.

## Task Budgets for Agent Teams: Controlling the 7x Token Multiplier

Multi-agent Claude Code deployments amplify costs dramatically. When agents run in plan mode, token consumption is approximately 7x higher than standard sessions. A 3-agent pipeline can balloon the orchestrator's context by 60,000+ tokens across just 10 cycles — even before accounting for the sub-agents' own consumption.

Task budgets at each layer of a multi-agent system:

```python
# Orchestrator budget: total session envelope
orchestrator_config = {
    "task_budget": {"type": "tokens", "total": 500000}
}

# Sub-agent budget: per-task limit for spawned agents  
sub_agent_config = {
    "task_budget": {"type": "tokens", "total": 100000}
}
```

Setting budgets at the sub-agent level prevents any single agent from consuming the entire available compute. Setting a budget at the orchestrator level bounds total pipeline cost. The combination creates a cost envelope that's predictable enough to budget against — critical for teams deploying multiple developer agents running simultaneously.

Rate limit configuration for team deployments: 200k-300k TPM per user for teams of 1-5, with budget settings calibrated to stay within these limits during peak usage (weekday 5-11am Pacific runs 1.3-1.5x the baseline burn rate).

## Common Pitfalls: The Too-Small Budget Trap and How to Avoid It

**The too-small budget trap.** Setting budgets below what a task actually requires causes one of two failure modes: Claude aggressively scopes down the task (omitting files, skipping edge cases, generating partial solutions), or Claude produces refusal-like behavior where it declines to start work it "knows" it can't complete within the budget. The minimum accepted value is 20,000 tokens, but a 20,000-token budget for a large refactor task will still produce the scope-reduction failure mode.

**The measurement gap.** Testing sessions typically cost less than production sessions because production accumulates history. A task that runs cleanly in 50,000 tokens in a fresh test session may consume 80,000-120,000 tokens in a production session with accumulated context. Add a 50% headroom buffer when translating test measurements to production budgets.

**Ignoring the tokenizer update.** The April 2026 tokenizer update inflates effective costs up to 35% for code-heavy content compared to previous estimates. If your budget baselines were established before April 2026, recalibrate.

**Not monitoring the right metrics.** Budget-per-task is a leading indicator; monthly API spend is a lagging indicator. Track both. A task that consistently uses 95%+ of its budget is a signal to investigate — either the budget is too tight or the task is expanding in scope.

The correct workflow: measure without budgets → calculate p50/p75/p90 → set budget at appropriate percentile for your tolerance → add 30-50% headroom for production vs test variance → monitor and adjust monthly.

---

## FAQ

**What is the minimum task budget I can set?**

The minimum accepted `task_budget.total` is 20,000 tokens. Requests with a total below 20,000 return a 400 error. In practice, tasks requiring less than 20,000 tokens don't benefit much from budget controls — the main value of task budgets is controlling longer agentic sessions that might otherwise consume 50,000-300,000+ tokens.

**Does setting a task budget reduce the quality of Claude's output?**

Not directly, but indirectly when the budget is approached. When Claude has ample budget remaining, behavior is unchanged. As the budget depletes, Claude begins prioritizing completion of in-flight work over starting new steps, which can mean fewer total tasks completed — but the quality of completed tasks isn't degraded. Setting budgets significantly below p50 spend will cause visible scope reduction.

**Are task budgets available on all Claude models?**

As of the 2026 launch, task budgets are only supported on Claude Opus 4.7. Requests to other models with the task_budget parameter are silently ignored — the budget has no effect, and no error is returned. Check the beta documentation for updated model support.

**How do task budgets interact with Claude Code's auto-compaction?**

Claude Code's built-in auto-compaction handles budget carryover automatically when task budgets are set via the CLI (`/config task_budget`). For custom API integrations, you must manually track tokens consumed and pass the `remaining` field on each post-compaction API call. Failing to carry `remaining` through compaction effectively resets the budget counter.

**Can I see real-time budget consumption during a session?**

In the Claude Code CLI, Claude reports budget status when approaching limits: percentage consumed, tasks completed, estimated tokens to finish. The Anthropic API returns usage data in each response (`response.usage.input_tokens` + `response.usage.output_tokens`) which you can use to track cumulative spend in custom integrations. There's no real-time streaming budget dashboard — you track it by summing response usage data.
