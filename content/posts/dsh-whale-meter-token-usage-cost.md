---
title: "dsh whale meter tokens: Track DeepSeek Harness Token Usage & Cost Tiers"
date: 2026-08-17T16:13:59+00:00
tags:
  - dsh whale meter
  - DeepSeek Harness
  - token tracking
  - cost dashboard
  - LLM cost optimization
description: "dsh-whale-meter shows your DeepSeek Harness token usage in 5 gamified tiers and estimates cost in CNY or USD, fully on-device with no telemetry."
draft: false
cover:
  image: "/images/dsh-whale-meter-token-usage-cost.png"
  alt: "dsh whale meter: Token Usage Tiers and Cost Dashboard for DSH"
  relative: false
schema: "schema-dsh-whale-meter-token-usage-cost"
---

**dsh-whale-meter is a one-line-install, zero-configuration plugin for DeepSeek Harness (DSH) that turns your raw token usage into five gamified tiers — from 🐟 small fry to 🐳 blue whale — and estimates your spend in CNY or USD, all stored locally on your machine with no telemetry and no network calls.** It went from a nice-to-have to a budgeting necessity on August 17, 2026, when DeepSeek raised v4-flash and v4-pro prices and introduced peak/off-peak billing. This guide explains exactly what it tracks, how the new pricing works, and whether it beats the alternative cost-tracking tools.

## What Is dsh-whale-meter and Why You Need It Now (Post-8-17 Price Hike Context)

DeepSeek Harness is a powerful agentic coding harness, but for a long time it gave users almost no visibility into how many tokens they were actually consuming or what those tokens cost. That gap is exactly what dsh-whale-meter (仓库: `Shiye-10Pages/dsh-whale-meter`) was built to close. It is a native DSH plugin written in TypeScript under an MIT License, released on August 16, 2026, with a design goal of "one-line install, zero config, all data local."

The timing is not accidental. On **August 17, 2026**, DeepSeek raised the prices of v4-flash and v4-pro and, for the first time, introduced **peak/off-peak billing** in China. That single change turned token spend from a background curiosity into a line item you must actively manage. As the broader industry scramble shows, teams are routinely blowing through their token budgets — TechCrunch reported in June 2026 that many teams were running at **3x their 2026 token budgets by April**, with individual engineers seeing monthly token spikes in the **$40,000 range**. The days of "just let the model run" are over.

dsh-whale-meter answers the three questions every heavy DSH user now asks daily: *How many tokens am I using?* *What am I actually spending?* *Is my usage tier creeping toward the top?*

## Key Features — Token Usage Tiers, Cost Dashboard, and the Whale Score Card

The headline feature is a **gamified usage ladder** with five tiers:

| Tier | Emoji | Meaning |
|------|-------|---------|
| Small fry | 🐟 | Light usage |
| Tropical fish | 🐠 | Moderate usage |
| Dolphin | 🐬 | Above-average usage |
| Humpback | 🐋 | Heavy usage |
| Blue whale | 🐳 | Extreme usage |

Each tier carries an **estimated percentile** — the project is careful to label this as an estimate, not a claimed global rank — plus a playful magnitude conversion that frames your usage as "≈ N reads of Three-Body." It turns an abstract number of tokens into something you can actually feel.

The **cost dashboard** is the practical workhorse. It reports spend across four time windows — **today, yesterday, month, and cumulative** — in CNY by default, swappable to USD. Costs are estimated from the official DeepSeek pricing pages, so they track the real tariff rather than a stale hardcoded rate.

Two features make the dashboard genuinely useful rather than decorative:

- **8-17 price-hike comparison.** The same usage is priced side-by-side under the old and new tariffs. Pre-August-17 usage is shown as a *preview* of what it would have cost under the new rate; post-August-17 usage gets a *retroactive back-calculation* of what it would have cost under the old rate. This makes the real impact of the hike measurable in one glance.
- **Cross-price-day correctness.** Price tables are organized by effective date ranges, so historical bills are never mis-computed against today's rates.

## How the 8-17 Price Change Works (v4-flash / v4-pro, Peak vs Off-Peak, Before-After Compare)

The August 17 change has two parts: a **price hike** and a **new peak/off-peak structure**. Both are baked into the whale-meter's built-in price table (version 2026-08-16 already contains the new rates).

For **v4-flash** (per million tokens, cache miss), the changes are:

| Cost component | Before 8-17 | Peak (after 8-17) | Off-peak (after 8-17) |
|----------------|-------------|--------------------|------------------------|
| Cache hit | ¥0.02 | ¥0.10 | ¥0.05 |
| Cache miss | ¥1 | ¥3 | ¥1.50 |
| Output | ¥2 | ¥9 | ¥4.50 |

**v4-pro** adjusted in parallel: peak pricing of ¥0.30 / ¥9 / ¥27 (hit / miss / output), with off-peak exactly half. **Peak hours are Beijing 9:00–12:00 and 14:00–18:00.**

The **non-obvious point most guides get wrong** is this: even if you run entirely off-peak, the off-peak rate is **still more expensive than the old flat pre-8-17 price**. Look at the v4-flash table above — the off-peak miss rate of ¥1.50 beats the old ¥1.00 flat rate, and off-peak output at ¥4.50 is more than double the old ¥2.00. Off-peak is a discount *relative to the new peak rate*, not a return to the old prices. The whale-meter makes this visible with a **⚡½ badge** shown during off-peak hours, and its before/after comparison panel surfaces exactly how much the hike costs you even on the cheapest schedule.

## Multi-Vendor Precision Pricing: 46 Models Across 6 Providers, Including China Tiered Rates

whale-meter is not limited to DeepSeek. It ships with a pricing database covering **46 models across 6 vendors**: DeepSeek, Anthropic, OpenAI, Google, Zhipu GLM, and Moonshot Kimi. Every model is itemized against the official pricing pages.

What sets it apart from most generic cost tools is how it handles **tiered pricing from Chinese vendors**, which most trackers simply ignore:

- **GLM-5.1** input is priced by context length: **<32K tokens costs ¥6, ≥32K costs ¥8** per million.
- **GLM-4.7** sub-divides even further, tiering by output length.

Because the tier boundary depends on per-call context size, a flat price-table lookup produces wrong numbers. whale-meter applies the correct tier per call. When a model is not yet in the table, it is explicitly marked **unpriced** rather than silently estimated — an honest design choice that prevents fabricated cost figures.

## Privacy & Data Locality: Fully On-Device, No Telemetry, Raw-Token-Only Storage

Privacy is a first-class design constraint, and it is the sharpest contrast with cloud-based dashboards. Everything runs on-device:

- Usage is stored in `~/.dsh/whale-meter/usage-YYYY-MM.jsonl`.
- Only **raw token counts** are persisted — monetary amounts are recomputed on read, so no dollar figures are ever frozen into storage.
- There are **no network requests** except the optional balance query you explicitly enable.
- There is **no telemetry** of any kind.

For a tool that sits next to all of your agent activity, this matters. A cloud dashboard necessarily exfiltrates at least aggregate usage data; whale-meter keeps the entire ledger local. The raw-token-only design also means a later price change can be applied retroactively to historical usage without storing contradictory amounts.

## Installation and Configuration (dsh plugin, zero-config, cordis.patch.yml options)

Installation is a single command. If you run DSH with a profile:

```bash
dsh plugin --profile <profile> add dsh-whale-meter
```

There is a **web panel** for TUI or headless setups at `http://127.0.0.1:3080/whale-meter/api/summary`. Configuration options live in `cordis.patch.yml`, letting you tweak behavior without touching source code. The project's stated goal is zero-config for the common case: install, open the panel, and you immediately see your tiers and spend.

## Limitations and Honest Caveats (Estimates Not Exact, Unknown Models Marked Unpriced, Community Plugin)

No cost tracker is perfect, and whale-meter is transparent about its boundaries:

- **Costs are estimates, not invoices.** Prices are drawn from official pages, but actual billing can differ due to rounding, promotions, or regional rules. Treat the dashboard as a budgeting guide, not an accounting record.
- **Unknown models are marked unpriced.** If whale-meter hasn't been updated for a newly released model, it will not invent a price — you'll see it flagged instead.
- **It's a community plugin.** The repo is young (created August 16, 2026, roughly 3 stars at time of research) and MIT-licensed. You're relying on an actively maintained community project rather than an official DeepSeek product.
- **Tiers are percentile estimates**, not confirmed global rankings. They give you a feel for where you sit, but "blue whale" is descriptive, not audited.

## dsh-whale-meter vs Alternative Cost-Tracking Tools (CacheLens, AgentLedger, Agentic Metric)

How does the DSH-native plugin compare to the wider field of agent cost trackers?

| Tool | Approach | Best for | Data locality |
|------|----------|----------|---------------|
| **dsh-whale-meter** | DSH-native plugin, zero-config, gamified tiers | DeepSeek Harness users who want instant local visibility | Fully on-device |
| **CacheLens** | Local-first proxy that tracks cache-hit savings | Anyone focused on cache economics as an observability layer | Local proxy |
| **AgentLedger** | SDK-based observability of real agent actions (SSE streaming) | Teams tracking actions, not just LLM calls | Cloud/streaming |
| **Agentic Metric** | Token/cost tracking for AI coding agents, broader than DSH | Multi-tool agent environments | Varies |

The trade-off is clear. Generic proxy and ledger tools (CacheLens, AgentLedger, Agentic Metric) are broader — AgentLedger, for instance, tracks every real-world agent action with sub-second SSE latency rather than just LLM calls. But they require integration, a proxy, or an SDK, and they don't understand DSH's internals. whale-meter's advantage is that it is a **zero-config native plugin**: no proxy to configure, no SDK to wire in, and it inherently knows the DSH data layout. If you're all-in on DSH, the plugin approach wins on speed and locality; if you span many tools, a broader tracker makes more sense.

## Verdict and Roadmap

For anyone running DeepSeek Harness seriously, dsh-whale-meter earns its place immediately. The 8-17 price hike means **running blind on tokens now costs real money** — and the peak/off-peak structure adds a scheduling decision you can only make with a meter. The gamified tiers make the abstract tangible, the before/after price comparison makes the hike measurable, and the fully-local, no-telemetry design makes it trustworthy.

The roadmap points in sensible directions: **CSV/Markdown export** for records and reporting, **off-peak scheduling suggestions** to help you shift work into the half-price window, and an enhanced **TUI**. Combined with the cache-ledger view — whose value *grows* after the hike, since the cache hit/miss price gap widened — these additions would round it into a complete cost-control tool.

If you use DSH and haven't looked at your token bill yet, now is the moment. Install whale-meter, read your tier, and schedule your heavy runs off-peak. Your wallet will thank you.

## FAQ

**What exactly does dsh-whale-meter track?**
It tracks your DeepSeek Harness token usage across five gamified tiers (🐟 small fry through 🐳 blue whale) and estimates your cost over today, yesterday, the current month, and cumulative totals, in CNY or USD.

**How does the 8-17 DeepSeek price change work?**
On August 17, 2026, DeepSeek raised v4-flash and v4-pro prices and introduced peak/off-peak billing. Peak hours are Beijing 9:00–12:00 and 14:00–18:00; off-peak costs exactly half the peak rate but is still more expensive than the old flat pre-8-17 price.

**Is whale-meter data private?**
Yes. All data is stored locally in `~/.dsh/whale-meter/usage-YYYY-MM.jsonl`, only raw token counts are persisted, and there is no telemetry or network traffic except an optional balance query you enable manually.

**Does whale-meter support models beyond DeepSeek?**
Yes. It covers 46 models across 6 vendors — DeepSeek, Anthropic, OpenAI, Google, Zhipu GLM, and Moonshot Kimi — including China vendors' tiered pricing such as GLM-5.1's <32K vs ≥32K input rates.

**Is whale-meter free and where do I get it?**
It is an MIT-licensed open-source project at `Shiye-10Pages/dsh-whale-meter`. Install with `dsh plugin --profile <profile> add dsh-whale-meter`, then open the web panel at `http://127.0.0.1:3080/whale-meter/api/summary`.
