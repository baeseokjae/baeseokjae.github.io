---
title: "Claude Code Limits in 2026: The 50% Promotion Ended, the 25% Raise Stayed"
date: "2026-10-01T04:58:20+00:00"
tags:
  - Claude Code limits
  - claude code weekly limits
  - claude code usage limits 2026
  - claude code 50% promotion ended
  - claude code 25% permanent increase
  - claude code 17% reduction
  - claude code weekly limit reset time
  - claude code usage credits
  - claude code max 20x weekly limit
  - claude code per-model limits Fable 5.1
  - claude code subagent token burn
  - claude code /usage command
  - how to check claude code usage
  - claude code compact clear limits
  - claude code plan comparison heavy user
description: "The 50% Claude Code limits promotion ended Sep 13, 2026. A permanent 25% raise replaced it — here is what heavy users keep and how to stretch it."
draft: false
cover:
  image: "/images/claude-code-weekly-limits-promotion.png"
  alt: "Claude Code Limits in 2026: The 50% Promotion Ended, the 25% Raise Stayed"
  relative: false
schema: "schema-claude-code-weekly-limits-promotion"
---

Claude Code limits today are permanently 25% higher than the pre-promotion baseline for Pro, Max, Team, and seat-based Enterprise plans — but roughly 17% lower than the 50% promotional peak that ran from May 13 to September 13, 2026. Anthropic kept part of the boost, ended the rest, and never touched the separate five-hour session limit. That single paragraph is the whole story, and it is the reason so many heavy users simultaneously feel "the promotion ended" and "my plan got better this year."

Below is the exact math, what actually drains a weekly allowance in October 2026, and the levers — official ones, not folklore — that stretch it.

## What changed: the 2026 Claude Code limits timeline

Anthropic changed Claude Code usage limits three separate times in 2026. Heavy users who noticed only one of those changes have a distorted picture of what they are entitled to.

| Date | Change | Who it applied to | Source |
|---|---|---|---|
| May 6, 2026 | Five-hour window limits doubled; peak-hours limit reduction removed | Pro, Max (tied to a SpaceX Memphis data-center compute deal) | arstechnica.com |
| May 13, 2026 | Weekly limits raised 50% (promotion begins) | Pro, Max, Team, legacy seat-based Enterprise | support.claude.com |
| Sep 13, 2026 | Promotion expires at 11:59 PM PT | — | support.claude.com |
| Sep 14, 2026 | Weekly limits permanently raised 25% above the pre-promotion baseline | Pro, Max, Team, legacy seat-based Enterprise | support.claude.com |

Two of those three changes are still in force. The five-hour doubling from May 6 was never rolled back, and the permanent 25% weekly raise from September 14 is now the standard. Only the 50% promotional window closed.

The promotion itself ran automatically. There was no opt-in, no coupon, and no action required: if you were on an eligible subscription between May 13 and September 13, 2026, your weekly Claude Code allowance was 50% larger, and `/usage` in the CLI showed the elevated numbers. Free plans and consumption-based Enterprise seats were excluded from the start, because neither of them meters usage the way a subscription allowance does.

If you want the longer version of how that promotional window was announced and extended through the summer, our [earlier breakdown of the weekly limits promotion](/posts/claude-code-weekly-limits-promotion-2026/) walks through the announcement-by-announcement sequence.

## What the 50% promotion actually covered — and what it never touched

Misreading the scope is the most common reason heavy users misjudge their headroom. The promotion was narrower than "everything got 50% better."

**What was included.** The boost applied to the weekly usage allowance in Claude Code across every surface it runs on: the CLI, IDE extensions, the desktop app, and the web/agent experience. It covered Pro, Max, Team, and legacy seat-based Enterprise.

**What was excluded.** Free plans have no Claude Code allowance to boost, and consumption-based Enterprise seats are metered on consumption rather than on a subscription pool, so neither was eligible.

**What was never part of it.** The five-hour session limit. That meter was doubled on May 6 and left alone by the promotion. Claude chat and Claude Cowork limits were also untouched — the extra 50% was Claude Code only, in every surface Claude Code runs on, but nowhere else.

That last point resolves a genuinely common confusion. If your Claude Code weekly pool felt enormous in July while your Claude chat allowance in the browser felt unchanged, that was by design, not by bug.

## The honest math: a 25% raise and a 17% cut at the same time

The numbers are only confusing if you mix up the baseline. Normalize your pre-promotion allowance to 100 units — the units are opaque, since Anthropic does not publish token counts for subscription plans:

| Period | Allowance index | vs. pre-May baseline | vs. promotional peak |
|---|---|---|---|
| Pre-May 2026 baseline | 100 | — | −33% |
| Promotion (May 13 – Sep 13) | 150 | +50% | — |
| Since Sep 14, 2026 | 125 | +25% | −16.7% (≈17%) |

Anthropic conceded the framing publicly: "Compared to today, this works out to a 17% reduction in weekly limits on Claude Code." That statement is accurate relative to the promotional peak and simultaneously consistent with the permanent 25% raise relative to the original baseline. Both descriptions point at the same number, 125.

The practical consequence for a heavy user is that you should stop sizing your workflow around August's ceiling. Your real budget is 25% above where you started the year and about a sixth below the temporary high point — and the weekly allowance was never a fixed count of prompts anyway. It varies with conversation length, model choice, tool usage, and effort level, which is why two developers on identical plans can have wildly different limits remaining at the end of a week.

## How Claude Code limits actually work in October 2026

"Claude Code limits" is shorthand for at least four distinct meters that behave differently and reset on different clocks.

| Meter | What it governs | Reset cadence | Affected by the promotion? |
|---|---|---|---|
| Weekly allowance | Your plan's overall budget across Claude Code | Fixed weekly window | Yes — now +25% permanently vs pre-May |
| Five-hour session limit | How much you can run in one working session | Every five hours | No — doubled May 6, unchanged by the promotion |
| Per-model weekly caps | Model-specific weekly ceilings (e.g. Fable 5.1) | Weekly, tied to the model | Not as a headline change, but new models moved the math |
| Length limit (context) | How large the conversation can grow before degradation | Per session, managed by you | No — this is the context window, not your plan allowance |

Two structural facts deserve emphasis. First, on subscription plans all Claude surfaces draw on one shared usage limit: claude.ai, Claude Code, and Claude Desktop are not separate pools. Second, API keys are metered per token and never touch your subscription allowance — so "I'll just switch to an API key" is a billing change, not a way to unlock more subscription headroom.

The distinction between the length limit and the usage limit is the one heavy users most often conflate. The context window is a technical ceiling you manage with `/compact` and `/clear`; the plan allowance is a commercial budget you can only refill by waiting, paying, or upgrading.

## Why your weekly limit drains faster than you expect

If your allowance is 25% larger than in January but still evaporates by Tuesday, the promotion is not the culprit. Five documented mechanisms are.

**1. Prompt-cache expiry forces re-caching.** When the prompt cache expires mid-session, Claude Code re-reads context it had already paid for. Developers have reported single re-cache events of roughly 800,000 tokens, charged against both the five-hour and the weekly meters.

**2. Subagent fan-out multiplies the burn.** A parent agent delegating to many subagents consumes allowance in parallel rather than serially. One report saw roughly 70% of a weekly Fable 5.1 allowance consumed mostly by subagents that were then killed by the rate limit; another burned 39% of a Max 20x weekly limit in under 24 hours by running about 16 maximum-effort reviewer subagents.

**3. Long-lived sessions accumulate context.** Because drain scales with conversation length, a session left open across days is the most expensive way to work. This is a hygiene problem, not a plan problem.

**4. Per-model weekly caps are invisible until they bite.** The status-line JSON exposes only `five_hour` and `seven_day` windows, so a per-model weekly limit — Fable 5.1, for instance — cannot be seen there at all. As of September 29, 2026 that visibility gap was still an open feature request.

**5. The meter is shared and your model mix changed.** Anthropic shipped Fable 5.1 and Mythos 5.1 on September 1, Opus 5.5 on September 22, and Sonnet 5.5 on September 28, 2026. New models on the same subscription change the effective cost per task even when the headline allowance does not move.

Two field reports put scale on the problem. A Max 20x user burned 9.6 billion tokens across 34 sessions in seven days (September 16–22, 2026), exhausted the weekly limit in about 2.5 days, and did 93.9% of that work on Opus 5. Separately, one developer measured a roughly 3.6x worse weekly consumption rate after the September 25, 2026 reset — about 93 responses per 1% before, roughly 30 after — on an unchanged workflow.

## Seven tactics that actually stretch a weekly allowance

Anthropic's own reduction playbook is the honest starting point, because it targets consumption rather than the ceiling: manage context proactively, choose the right model, cut MCP overhead, move standing instructions from CLAUDE.md into skills, adjust extended thinking, delegate verbose work to subagents deliberately, and manage agent-team token costs. Here is what those translate into in practice.

1. **Run `/compact` before you think you need it.** Compaction summarizes prior turns into a shorter form. Waiting until the context is full means you already paid for the bloat.
2. **Run `/clear` between unrelated tasks.** Carrying yesterday's context into today's task is the single largest avoidable drain.
3. **Default routine I/O work to a cheaper model and reserve the premium model for reasoning.** Spotify's engineering team documented a 90% cut in Claude Code token usage by routing non-reasoning "I/O" work — reading files, generating boilerplate, updating docs — to a cheaper worker model. Most agent work is I/O, not reasoning.
4. **Cap subagent fan-out deliberately.** Give subagents narrow scopes and a maximum-effort ceiling that matches the task. Sixteen max-effort reviewers is a budget decision, not a quality decision.
5. **Watch MCP overhead.** Every connected server's tool definitions occupy context on every turn. Disable the servers you are not using in a given session.
6. **Move instructions out of CLAUDE.md and into skills.** Standing instructions load constantly; skills load on demand.
7. **Right-size extended thinking.** Maximum effort on a task that does not need it is the cheapest way to burn a weekly allowance quickly.

Two older habits are now obsolete: there is no peak-hours reduction to schedule around (removed May 6, 2026), and switching to an API key is a billing model change rather than a way to extend your subscription pool.

## When you hit the cap: wait, usage credits, or upgrade

| Option | How it works | Cost signal | Best when |
|---|---|---|---|
| Wait for reset | Weekly window resets on a fixed cadence; five-hour window resets continuously | Free | You hit the cap sporadically |
| Enable usage credits | Keep working past included limits, billed at standard API rates | API rates; $2,000/day redemption limit; monthly spend cap and auto-reload configurable | You hit the cap occasionally and the overage is small |
| Upgrade the plan | Move to a larger multiplier (Max 5x → Max 20x) | Fixed monthly price | You hit the cap during normal, non-exceptional work |

Usage credits are available to Pro, Max 5x, and Max 20x subscribers. You enable them under Settings → Usage → Usage credits on claude.ai and prepay ("Add funds"), with optional auto-reload. Note that credits are billed separately from the subscription and appear as additional charges, and the daily redemption limit is $2,000. If you enable credits and then upgrade plans, verify the meter after switching — reported upgrade-timing bugs mean the displayed allowance is worth re-checking rather than assuming.

## Which plan a heavy user should actually buy

Pricing: Claude Pro is $20/month ($17/month billed annually); Max starts at $100/month with 5x and 20x tiers. The official Enterprise benchmark for Claude Code usage is about $13 per developer per active day and $150–250 per developer per month, with 90% of users below $30 per active day.

| Plan | Price | Claude Code capacity | Fits |
|---|---|---|---|
| Free | $0 | None | Claude chat only; Claude Code excluded |
| Pro | $20/mo ($17 annual) | Baseline multiplier; modest weekly pool | A few hours a day, mostly Sonnet |
| Max 5x | $100/mo | 5x Pro-class capacity | Daily work on large repos with Opus in the loop |
| Max 20x | $200/mo | 20x Pro-class capacity | Continuous or concurrent batch work |
| Team / seat-based Enterprise | Per seat | Seat multipliers; weekly limits now +25% vs pre-May | Teams needing shared, governed capacity |

The economics get uncomfortable fast at the top. A quarter of engineering leaders already report spending $200–500 per developer per month on tokens, with some above $2,000, and by 2028 AI coding costs are projected to exceed the average developer salary. That is the argument for treating model routing (tactic 3 above) as a budget control rather than a preference: if a Max 20x subscription is not enough, the correct first fix is usually to stop spending premium-model tokens on non-reasoning work, not to buy a bigger plan.

## How to monitor Claude Code usage — and what each tool cannot see

| Tool | What it shows | What it misses |
|---|---|---|
| `/usage` | Plan usage bars, Day/Week toggle, activity stats, usage breakdown | Per-model weekly caps; the "Session" block is API-oriented, not your subscription allowance |
| `/usage` (rate-limited) | Last-known bars from the past 60 minutes with a "Showing last-known usage" note (v2.1.208+); press `r` to retry | Live numbers while the endpoint is throttled |
| `/usage-credits` | Opens the right settings page by role (v2.1.211+; v2.1.248+ for Enterprise) | Only present while credits are enabled |
| `/insights` | Analyzes up to 200 recent sessions, writes ~/.claude/usage-data/report.html | Nothing below the session level |
| Status line | `five_hour` and `seven_day` windows | Any per-model weekly window (e.g. Fable 5.1) |
| Third-party trackers | Local trend lines and burn-rate estimates | Anything the CLI does not expose; per-model caps remain invisible |

The honest summary: no single surface shows your whole budget in October 2026. The weekly bars are authoritative, the status line is structural only, and per-model weekly limits stay invisible until they stop you.

## Frequently Asked Questions

**Are Claude Code weekly limits higher now than they were before the promotion?**
Yes. Since September 14, 2026, weekly limits are permanently 25% higher than the pre-promotion baseline for Pro, Max, Team, and legacy seat-based Enterprise plans. They are simultaneously about 17% lower than the promotional peak that ran May 13 to September 13, 2026.

**Is the 50% Claude Code promotion still active?**
No. The promotion expired at 11:59 PM PT on September 13, 2026, and was replaced the next day by a permanent 25% raise to standard weekly limits. Anthropic itself described the change as "a 17% reduction in weekly limits on Claude Code" relative to the promotional period.

**When does the Claude Code weekly limit reset?**
The weekly allowance resets on a fixed weekly window, and the five-hour session limit resets continuously every five hours. Per-model weekly caps follow their own weekly schedule, which the status line does not display — run `/usage` for the windows it can show.

**How do I check my Claude Code usage?**
Run `/usage` in the CLI for plan usage bars with a Day/Week toggle, activity stats, and a breakdown. If the usage endpoint is rate limited, v2.1.208+ shows last-known bars from the past 60 minutes with a "Showing last-known usage" note — press `r` to retry. `/usage-credits` opens the credit settings page when credits are enabled, and `/insights` writes a report from up to 200 recent sessions.

**Do subagents and `/compact` affect my weekly limit?**
Yes to subagents, and that is often the surprise. Subagents bill against the same weekly allowance, and reported cases include roughly 70% of a weekly allowance consumed mostly by subagents, plus 39% of a Max 20x weekly limit in under 24 hours via about 16 max-effort reviewer subagents. `/compact` works the opposite way: it reduces future drain by shrinking accumulated context, and `/clear` starts a clean, cheaper session.

## Bottom line

The 50% era is over and the 25% permanent raise is what you actually have. Anthropic's five-hour doubling stayed, the weekly promotion did not, and the meters that will stop you now are the ones almost nobody can see: subagent fan-out, prompt-cache re-reads, long-lived contexts, and per-model weekly caps. Keep the hygiene — `/compact`, `/clear`, cheaper models for I/O work, deliberate subagent budgets — and treat usage credits and the Max 5x → 20x step as escalations rather than defaults. Run `/usage` after any plan change and verify the number instead of trusting it.
