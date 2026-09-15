---
title: "Claude Code Weekly Limits in 2026: The 50% Promotion, the Permanent 25% Raise, and What Heavy Users Keep After Sep 13"
date: "2026-09-15T10:00:57+00:00"
tags:
  - claude code
  - anthropic
  - claude code weekly limits
  - claude usage limits
  - ai coding
description: "Claude Code weekly limits changed in 2026: a 50% promo ended Sep 13, replaced by a permanent 25% raise. Here's the exact math heavy users keep and how to stretch it."
draft: false
cover:
  image: "/images/claude-code-weekly-limits-promotion-2026.png"
  alt: "Claude Code Weekly Limits in 2026: the 50% promotion, the permanent 25% raise, and what heavy users keep"
  relative: false
schema: "schema-claude-code-weekly-limits-promotion-2026"
---

Claude Code weekly limits are higher in 2026 than they were at the start of the year, but the number that matters shifted on September 14: the 50% promotional boost that ran from May 13 to September 13 has expired, and Anthropic replaced it with a permanent 25% raise to standard weekly limits on Pro, Max, Team, and seat-based Enterprise plans. Relative to the promotional peak you may have grown used to, that is a drop of about 17% — so heavy users are essentially giving back part of their summer allowance while still keeping more than their original baseline. This guide walks through the full 2026 timeline, the exact math, and practical tactics to stretch the limits you actually have.

## The 2026 Timeline: How Claude Code Limits Changed This Year

Anthropic made three separate changes to Claude Code usage limits in 2026, and heavy users who only noticed one of them have a distorted picture of their allowance. Here is the order in which they landed.

**May 6, 2026 — five-hour limits doubled.** On this date Anthropic doubled Claude Code five-hour rate limits for Pro, Max, Team, and seat-based Enterprise plans, and simultaneously removed peak-hour reductions that had throttled usage during busy periods. This was a direct response to heavy users hitting session caps in the middle of long working sessions (source: morphllm.com).

**May 13, 2026 — 50% weekly promotion begins.** Just a week later, Anthropic raised Claude Code weekly usage limits by 50% for the same eligible plans. The increase applied automatically, with no action or opt-in required from the user (source: support.claude.com).

**September 14, 2026 — permanent 25% raise replaces the promotion.** The promotional 50% expired at 11:59 PM PT on September 13, and a permanent 25% raise to standard weekly limits took effect the next day for Pro, Max, Team, and seat-based Enterprise users (source: bleepingcomputer.com).

The net effect is that a heavy user's weekly ceiling today is higher than it was in early 2026, but noticeably lower than it was during the promotional window. Understanding that three-step sequence is the difference between "my limits got cut" and an accurate picture of where your allowance actually stands.

## What the 50% Promotion Covered (and What It Didn't)

The promotional increase was specifically about Claude Code weekly usage, and it did not touch several other limits that users often confuse with it.

**What was included.** The 50% boost applied to the weekly usage allowance in Claude Code across all its surfaces — the CLI, IDE extensions, the desktop app, and the web/agent experience. It covered Pro, Max, and Team plans, plus legacy seat-based Enterprise accounts. Free plan users and consumption-based (pay-as-you-go) Enterprise accounts were explicitly excluded, because neither of those meter usage the same way as subscription plans (source: support.claude.com).

**What was not included.** The promotion did not affect five-hour session limits at all — those remain governed by the separate per-session window that resets every five hours regardless of your weekly pool. It also did not change Claude chat or Cowork limits; the extra 50% was Claude Code only. If you were hoping the promotion would also stretch your Claude app conversation allowance, it did not (source: support.claude.com).

This matters for budgeting. A heavy user who maximized the promotional weekly pool but still hit the five-hour session cap kept getting stopped mid-afternoon, because the promotion deliberately did nothing for the session window. The session limit and the weekly limit are two independent meters, and only one of them was boosted.

## What Happens Now: The Permanent 25% Raise and the Honest "17% Cut" Math

Anthropic has acknowledged that framing this as a straightforward "cut" is confusing, and the numbers explain why. The three values to keep straight are your baseline, your promotional peak, and your new standard.

Take a baseline weekly allowance of 100 (units are opaque — Anthropic does not publish token counts, so think of this as a normalized index). During the promotion it became 150. After September 14, with the permanent 25% raise over your pre-promotion baseline, it is 125. Compared to the promotional peak of 150, that new value of 125 is about a 17% reduction; compared to your original baseline of 100, it is still a 25% increase.

Anthropic acknowledged the framing directly on X, stating: "Compared to today, this works out to a 17% reduction in weekly limits on Claude Code" (source: bleepingcomputer.com). The honest reading is that heavy users are not being cut below where they started the year — they are being asked to give back roughly the top slice of a temporary bonus while keeping a permanently higher standard allowance.

For heavy users this is the practical number that matters: the days of a 50%-boosted pool are over, and your new monthly usable ceiling is 25% above your early-2026 level, not 50%. If you sized your workflow around the promotional peak, you now have roughly 17% less weekly headroom than you did in August, and you should plan accordingly.

## How Claude Code Weekly Limits Actually Work (Session vs Weekly vs Models)

A recurring source of confusion is that "Claude Code limits" actually refers to several distinct meters, and users regularly mix them up. Here is how the system breaks down.

**Weekly usage limit.** This is your plan's allowance that resets on a fixed weekly window. It is not a fixed number of prompts. Anthropic does not publish token counts; instead, plans are expressed as multipliers, and the actual drain per request varies with conversation length, which model you select, tool usage, and the effort level of the task (sources: claudecode101.com, superblocks.com).

**Five-hour session limit.** Separate from the weekly pool, this resets every five hours and governs how much you can run during a single working session. It was doubled on May 6 and was not part of the weekly promotion.

**Context / length limit.** The size of the conversation your model can hold before it degrades or must be trimmed. Managed with `/compact` and `/clear` rather than with any plan setting.

**Rate limit and credit / spend limit.** A rate limit throttles the pace of requests, while the credit/spend limit applies to API-key usage, which is metered per token rather than against a subscription allowance.

An additional wrinkle is shared accounting. On subscription plans, usage is shared across Claude surfaces — the Claude app and Claude Code draw from the same weekly pool — whereas API keys are metered per token and never touch your subscription allowance (source: claudecode101.com). Run `/usage` in the CLI to see your current allowance and how much of the window you have consumed, and `/cost` to see API spend.

## Heavy-User Tactics: /compact, /clear, Model-Switching, and Off-Peak Scheduling

Because the weekly allowance is not a fixed prompt count, the single most effective lever for heavy users is reducing how much of that allowance each task consumes rather than trying to raise the ceiling. These tactics are the ones the research consistently recommends.

**Use `/compact` and `/clear` aggressively.** A long-running conversation that accumulates weeks of context burns far more weekly allowance per prompt. `/compact` summarizes prior context into a shorter form, and `/clear` wipes the session entirely when you are starting a fresh task. For heavy users, trimming stale context is the difference between stretching a weekly pool and exhausting it by mid-week (source: claudecode101.com).

**Keep routine batch work on Sonnet and reserve Opus for planning.** Model choice changes the per-prompt cost dramatically. Sonnet is the sensible default for bulk code generation and refactoring, while the more expensive Opus is best reserved for complex architecture, planning, and high-stakes reasoning where its quality justifies the draw on your allowance (source: claudecode101.com).

**Schedule heavy work off-peak and keep sessions short.** With peak-hour reductions gone since May 6, the pacing advantage is now mostly about the five-hour session rhythm. Because the session limit is independent of the weekly pool, planning around five-hour resets — rather than burning through them — lets you stay productive across a full day without tripping the session cap.

**Treat context size as a budget.** Since drain scales with conversation length, breaking large tasks into smaller, fresh sessions after `/clear` keeps each prompt cheaper even if you run more of them.

## When You Still Hit the Cap: Wait, Enable Usage Credits, or Upgrade

Even with good hygiene, heavy users will eventually press against the weekly limit. At that point you have three realistic paths, and the right one depends on how frequently you hit the wall.

**Wait for the reset.** The weekly window resets on a fixed cadence, and the five-hour session limit resets continuously. If your need is sporadic, simply waiting is free and correct.

**Enable usage credits (pay-per-token).** Once you pass the plan cap, Claude Code can auto-switch to pay-per-token at API rates, so you can keep working without waiting for the reset. This comes with a spending ceiling of roughly $2,000 per day, and it can kick in without an explicit warning — worth knowing before you leave a long task running unattended (sources: superblocks.com, morphllm.com).

**Upgrade to a higher plan.** If you are regularly hitting the cap during normal work, the cleanest fix is a plan with a larger multiplier rather than paying per-token overages. Which one fits depends on the math in the next section.

## Which Plan Should a Heavy User Buy in 2026? (Pro vs Max 5x vs Max 20x vs Team)

The 2026 plan matrix gives heavy users a clear ladder. All subscription usage resets weekly plus on a five-hour window, and Anthropic expresses capacity as multipliers rather than token counts (source: superblocks.com).

| Plan | Price | Claude Code capacity | Best for |
|------|-------|----------------------|----------|
| Free | $0 | None (Claude Code excluded) | Experimenting with Claude chat only |
| Pro | $20/mo ($17/mo annual) | 5x free per-session baseline | Light-to-moderate users, a few hours/day mostly on Sonnet |
| Max 5x | $100/mo | 5x Pro per-session capacity | Heavy users on large repos who need Opus and long sessions |
| Max 20x | $200/mo | 20x Pro per-session capacity | Very heavy users running continuous batch work |
| Team Standard | $25/seat/mo | 1.25x multipliers per seat | Small teams with shared, moderate usage |
| Team Premium | $125/seat/mo | 6.25x multipliers per seat | Teams needing heavy shared capacity |

For a solo heavy user, the practical threshold is where you sit between Pro and Max. Pro is a good fit if you work a few hours a day and can stay on Sonnet; once you are regularly using Opus on large repositories, the research points to Max as the place where the per-session capacity stops being the bottleneck. Max 5x at $100/mo gives five times Pro's per-session capacity, and Max 20x at $200/mo gives twenty times — the choice between them is essentially whether a 5x session is enough to finish your typical working day, or whether you need the headroom of 20x for concurrent or round-the-clock batch workloads. A note on Fable 5: it draws from the same weekly pool as Claude Code and is capped at 50% of it on Max and premium seats, so plan around it as part of your total allowance (source: morphllm.com).

## Frequently Asked Questions

**Are Claude Code weekly limits higher now than they were at the start of 2026?**
Yes. The permanent 25% raise that took effect September 14 gives Pro, Max, Team, and seat-based Enterprise users a standard weekly allowance 25% above their pre-2026 baseline — even though it is lower than the temporary 50% promotional peak that ran May 13 through September 13 (source: bleepingcomputer.com).

**Is the 50% Claude Code promotion still active?**
No. The promotion expired at 11:59 PM PT on September 13, 2026. It was replaced by a permanent 25% raise to standard weekly limits, which compared to the promotional peak is roughly a 17% reduction in weekly capacity (sources: support.claude.com, bleepingcomputer.com).

**What counts toward my weekly limit, and how do I check it?**
Your weekly allowance covers all Claude Code usage on a subscription plan, and it is shared with the Claude app on the same account. The exact drain depends on conversation length, model, and tool usage rather than a fixed prompt count. Run `/usage` in the CLI to see your current and elevated limits (sources: claudecode101.com, support.claude.com).

**Did the promotion change my five-hour session limit?**
No. The 50% promotion applied to the weekly allowance only. Five-hour session limits were separately doubled on May 6, 2026, and were unaffected by the weekly promotion (sources: support.claude.com, morphllm.com).

**Does the Free plan include Claude Code?**
No. The Free plan does not include Claude Code at all, so it was never eligible for the promotion. Claude Code requires a paid subscription (Pro, Max, Team, or seat-based Enterprise) or an API-key setup with per-token metering (sources: superblocks.com, morphllm.com).

## Bottom Line for Heavy Claude Code Users

The 2026 story is not a loss for heavy users — it is a rebalancing. You end the year with a permanent weekly ceiling 25% higher than where you started, even though the summer's 50% bonus has come back down. The practical takeaway is to stop sizing your workflow around the promotional peak, treat the new standard as your real budget, and rely on the levers that actually control consumption: `/compact` and `/clear` to trim context, Sonnet for batch work with Opus reserved for planning, and five-hour session planning. Run `/usage` to see your new numbers, and if you are still hitting the wall regularly, the upgrade ladder from Pro to Max 5x to Max 20x is the cleaner answer than paying per-token overages on a regular basis.
