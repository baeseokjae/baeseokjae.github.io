---
title: 'GPT-5.6 Sol Pricing: The 50% Cut Was Not OpenAI''s'
date: 2026-10-01T04:53:30+00:00
tags:
- gpt-5.6 sol
- openrouter
- llm pricing
- api cost optimization
- openai
description: GPT-5.6 Sol pricing fell from $5/$30 to $2/$10 on OpenRouter. But OpenAI cut the list price — not the 50% badge. Here is every live rate on Oct 1, 2026.
draft: false
cover:
  image: "/images/gpt-5-6-sol-pricing-cut-openrouter.png"
  alt: "GPT-5.6 Sol Pricing: The 50% Cut Was Not OpenAI's"
  relative: false
schema: "schema-gpt-5-6-sol-pricing-cut-openrouter"
---

GPT-5.6 Sol pricing now reads $2.00 input / $10.00 output per million tokens on OpenRouter's OpenAI route, down from $5.00 / $30.00 in mid-August. That is a real 50% cut. It was not OpenAI's price cut — it is a router promotion stacked on top of a separate OpenAI reduction to $4 / $20.

That distinction is the whole article, because the two numbers are different prices on different layers, and almost every story about this model conflates them.

## Did OpenAI cut GPT-5.6 Sol's price by 50%?

No. OpenAI's own advertised reduction was 20% on input and 33% on output. The 50% belongs to OpenRouter.

Three separate price events landed inside five days in August 2026, and only one of them was OpenAI repricing its own model.

| Date | Event | Who did it | Price | Scope |
|---|---|---|---|---|
| Aug 17, 2026 | 50% promotion goes live | OpenRouter | $5.00 / $30.00 → $2.50 / $15.00 | Non-BYOK traffic, OpenAI provider route only, announced to expire Sep 18 |
| Aug 21-22, 2026 | List price reduction | OpenAI | $5.00 / $30.00 → $4.00 / $20.00 | OpenAI's own rate card, "at least through November 21, 2026" |
| Result | Badge stayed, base moved | Both | $2.50 / $15.00 → $2.00 / $10.00 | Same 50% badge, new number underneath it |

OpenAI's wording is deliberately narrow. Its model page states: "GPT-5.6 Sol costs $4 per million input tokens and $20 per million output tokens, a 20% reduction in input pricing and a 33% reduction in output pricing." It also states: "GPT-5.6 Sol's promotional pricing is available at least through November 21, 2026."

OpenRouter gave users 50% off, but never claimed it was an OpenAI price cut, and the discount carries its own expiry. The tell is the asymmetry: when OpenAI genuinely repriced Luna by roughly 80% in July, the cut appeared on OpenAI's own documentation. Sol's 50% never did.

### Why the difference changes your bill

A promotion lives on a channel. A list price lives on a vendor. If you route through OpenRouter's OpenAI tag, you pay $2.00 / $10.00 and rely on a discount that has already outlived its announced expiry. If you call OpenAI, Azure, or Bedrock directly, you pay the list rate on that platform, and no router badge protects you. Budget against the list number and treat the router discount as upside with an unknown end date.

## What does GPT-5.6 Sol cost today, route by route?

The same model, same weights, seven endpoints, four different price levels. This table was pulled from OpenRouter's endpoints API on October 1, 2026, and cross-checked against OpenAI's pricing page the same day.

| Route | Provider tag | Input /1M | Cached input /1M | Cache write /1M | Output /1M |
|---|---|---|---|---|---|
| OpenRouter, batch | `openai/gpt-5.6-sol:batch` | $1.00 | — | — | $5.00 |
| OpenRouter, Flex | `openai/flex` | $1.00 | $0.10 | $1.25 | $5.00 |
| **OpenRouter, standard** | `openai` | **$2.00** | $0.20 | $2.50 | **$10.00** |
| OpenRouter, Fast | `openai/fast` | $4.00 | $0.40 | $5.00 | $20.00 |
| OpenAI direct | api.openai.com | $4.00 | $0.40 | $5.00 | $20.00 |
| Azure | `azure` | $4.00 | $0.40 | $5.00 | $20.00 |
| Azure US / EU, Bedrock us-east-1 | `azure/us`, `azure/eu`, `amazon-bedrock/us-east-1` | $4.40 | $0.44 | $5.50 | $22.00 |

Two facts jump out of that table, and both are checkable in a single API call.

First, every OpenAI-tagged endpoint returns `discount: 0.5`. Azure and Bedrock return `discount: 0`. If you read a headline saying "GPT-5.6 Sol is half price on OpenRouter," the sentence is only true if you append "on the OpenAI route, non-BYOK." A request that lands on Azure pays full list.

Second, the spread is 4.4x on input for identical weights — $1.00 on the Flex route against $4.40 on Bedrock. The decision is no longer which model, it is which route, which service tier, and which provider tag.

### Where the long-context rate kicks in

Above 272,000 input tokens, the price doubles. OpenRouter exposes this as an `overrides` block on each endpoint rather than as a separate endpoint, which is why casual readers miss it.

| Route | Under 272K in / out | Over 272K in / out |
|---|---|---|
| OpenRouter OpenAI (discounted) | $2.00 / $10.00 | $4.00 / $15.00 |
| OpenRouter Flex (discounted) | $1.00 / $5.00 | $2.00 / $7.50 |
| OpenAI direct / Azure | $4.00 / $20.00 | $8.00 / $30.00 |
| Azure US / EU, Bedrock | $4.40 / $22.00 | $8.80 / $33.00 |

OpenAI states the rule plainly: "Prompts with >272K input tokens are priced at 2x input and 1.5x output for the full request."

## Why is the 50% badge still showing in October when the promotion expired September 18?

Because the promotion was a percentage, not a price, and percentages survive repricing.

The Aug 17 promo took 50% off whatever the base rate happened to be. When the base was $5.00 / $30.00, the badge read $2.50 / $15.00 — the number most articles still print. When OpenAI moved its base to $4.00 / $20.00 on Aug 21, the badge did not need to change. The number under it did. Today the same endpoint returns $2.00 / $10.00, and it still carries `discount: 0.5`.

This is why a promotion announced to expire on Sep 18 is still visible on Oct 1. There is no primary source restating the window either way, so treat the badge as evidence rather than a policy statement. The discount is live because the API says it is live today. Nothing promises it will be live tomorrow.

There is a second expiry running in parallel, on a different layer. OpenAI's November 21, 2026 date governs the *base* rate. If that promotional period ends, the base most likely returns toward list, and the 50% badge would then read $2.50 / $15.00 again — the original August number, restored by a change nobody made to the router.

## What eats the discount before you ever see it?

Two traps swallow most of the advertised saving, and neither appears in the headline.

**Trap one: the 272K cliff.** Any request whose input exceeds 272,000 tokens is billed at 2x input and 1.5x output *for the entire request*, not just the excess. On OpenAI's direct route that is $8.00 / $30.00. On the discounted OpenRouter route it is $4.00 / $15.00 — which is still at or above what you would pay OpenAI's standard rate for a short prompt. If your workload is "stuff the whole repository into the context window," the 50% promo is close to irrelevant: you are paying long-context rates either way, and the discount only pulls you back toward a price you would have paid for a shorter prompt.

**Trap two: reasoning tokens bill at the output rate.** GPT-5.6 Sol supports `reasoning.effort` values of `none`, `low`, `medium` (default), `high`, `xhigh`, and `max`. Reasoning tokens are billed as output tokens on every provider. Output is five times the input rate at list and five times at the discounted rate. A task that looks cheap at $10 per million output tokens is not cheap when a single hard request burns tens of thousands of hidden reasoning tokens. Raising effort from `medium` to `max` can multiply the cost of a request by an order of magnitude while looking like a one-word config change.

There is a third, smaller leak: cache writes bill at 1.25x the uncached input rate — $2.50 per million on the discounted OpenAI route, against $0.20 for a cache *read*. Caching is where the discount compounds, because agent sessions run roughly 20:1 input to output. Writing a prefix once and reading it twenty times costs $2.50 + 20 × $0.20 = $6.50 per million tokens, against $40 if every token were billed fresh.

## OpenRouter vs OpenAI direct vs Azure vs Bedrock vs batch: which should you use?

Each route wins on a different axis. None wins on all of them.

| Route | Best for | Why it wins | What it costs you |
|---|---|---|---|
| OpenRouter OpenAI tag | General non-BYOK traffic | 50% off the current base; simplest path to the lowest standard rate | Discount is a channel promo with no restated expiry; no universal zero-data-retention guarantee |
| OpenRouter batch (`:batch`) | Offline pipelines, evals, backfills | $1.00 / $5.00, the cheapest published Sol rate anywhere | Asynchronous turnaround, no interactive latency guarantee |
| OpenRouter Flex | Cost-sensitive interactive work | Slightly better than Fast, still discounted | Slower than standard; not the default routing target |
| OpenAI direct | Compliance, data residency, first-party SLAs | Vendor list price, no intermediary, no promo dependency | $4.00 / $20.00 — twice the router's discounted input |
| Azure | Enterprise agreements, regional processing | Same list rate as OpenAI, region pinning | No discount at all on this model |
| Azure US/EU, Bedrock | AWS- or Azure-native architecture | Lives inside your existing cloud account and IAM | $4.40 / $22.00 — a 10% regional uplift on top of list |
| BYOK on OpenRouter | High-volume users | Free allowance up to $25,000/month of list-price usage | Forfeits the promo entirely — BYOK traffic bills at list |

The last row is the counterintuitive one. Bringing your own key sounds like it should preserve every discount; on this promotion it does the opposite, because the discount applies to non-BYOK traffic only.

### What is the real discount after fees?

About 47%, not 50%. OpenRouter does not add a per-token markup, but it charges on the money you deposit: 5.5% on card purchases with a $0.80 minimum, or 5% on crypto. Against paying OpenAI directly, the effective saving on a $2.00 input rate is roughly 47% once the top-up fee is amortized, and the same fee applies to the output side.

## Did the 50% cut actually work? Two usage numbers, only one of them Sol's

OpenRouter processed 1.59 trillion GPT-5.6 Sol tokens in the seven days ending October 1, 2026 — roughly 253 billion tokens per day across September, with September 30 alone logging 267.2 billion prompt plus 3.5 billion completion tokens, $196,653 of metered usage.

The famous multiplier in circulation is 13.8x. That number belongs to Luna, not Sol, and attaching it to Sol is the exact error the original coverage made and later corrected.

OpenRouter's own research post, published August 25, 2026, is explicit: during the July 27 – August 14 Terra/Luna discount window, daily Luna usage rose 13.8x and Terra rose 5.6x. Sol, which was still at list price throughout, moved only 1.1x — from 71.2 billion to 79.1 billion tokens per day. OpenRouter described that as an effectively flat control group.

Sol's own promotion started on August 17. OpenRouter notes that the shaded region on its chart "from Aug 17 onward is Sol's own 50% discount. Sol jumps immediately, reproducing the Terra/Luna pattern." It never published a final multiplier for Sol. So the honest reading is: the discount demonstrably coincided with a step change in Sol's volume, but the size of that response is unquantified by the platform itself, and the 13.8x figure is not evidence for it.

### Why a router discount might be worth more than the revenue it gives up

SemiAnalysis advanced a plausible incentive argument in August 2026: OpenRouter and Vercel are small slices of OpenAI's total token volume, but they are unusually important public data sources for estimating model share. Halving prices there is cheap, and it visibly doubles a model's volume on the exact charts people use to judge OpenAI against Anthropic.

That is third-party analysis, not a confirmed policy, and it should be labeled as such. OpenRouter announced it was being acquired by Stripe on August 19, 2026 — two days after the Sol promotion went live. The acquisition post does not mention the promotion at all, and OpenRouter committed to "same mission, same name, same product, same roadmap." The timing is a correlation worth noting and nothing more.

## Cost per million tokens vs cost per solved task: Sol vs Kimi K3 vs Grok 4.6 vs Opus 5

Per-token price is the wrong unit for agentic work, because a cheaper model that takes three times as many turns is not cheaper. Two independent evaluations make the point with real numbers.

| Model | AA Intelligence Index | Cost per task (AA) | DeepSWE cost per rollout | Solved tasks per $100 | Four-for-four reliability |
|---|---|---|---|---|---|
| GPT-5.6 Sol (max) | 61 | $1.23 | $8.37 | 5.3 | 84.5% |
| Grok 4.6 (high) | 61 | $0.84 | — | — | — |
| Kimi K3 (max) | 60 | $0.84 | $4.65 | 14.7 | 76.6% |
| Claude Fable 5 (max fallback) | 62 | $3.14 | — | — | — |

On Artificial Analysis' Intelligence Index, Grok 4.6 at high reasoning ties GPT-5.6 Sol at max reasoning at a score of 61, but costs $0.84 per task against Sol's $1.23. Claude Fable 5 scores one point higher and costs $3.14 per task — two and a half times Sol's cost for a single point.

On Terminal-Bench 2.1 the ordering shifts again: Sol at `xhigh` scores 89.5%, Claude Opus 5 at max 89.1%, Grok 4.6 88.4%. Sol is the strongest of the three on that specific benchmark.

On DeepSWE, Sol costs $8.37 per rollout against Kimi K3's $4.65, and delivers 5.3 solved tasks per $100 against K3's 14.7 — roughly 2.8x the work per dollar for K3. But Sol is more reliable: an 84.5% four-for-four pass rate with 61 rock-solid tasks, against K3's 76.6% and 45. Sol also finishes a median rollout in 17 minutes against K3's 66, using about 40% fewer steps.

The models fail differently — a per-task correlation of just 0.46 — which is what makes a cascade attractive. A Kimi-first pipeline that escalates to Sol reaches about 85.6% and covers 108 of 113 tasks, beating either model alone and even beating a perfect one-shot router at 83.4%.

That reframes the promotion. Sol's price cut makes an already-reliable model competitive on hard work. It does not make Sol the cheapest answer for bulk work that Kimi K3 or Luna already handles.

## Why did OpenAI cut the price now?

Because GPT-5.6 Sol stopped being the frontier model, and legacy flagships get repriced.

OpenAI's current flagship table lists `gpt-6-astra` at $10.00 input / $50.00 output and `gpt-6.1-sol` at $2.00 / $10.00. GPT-5.6 Sol, released July 9, 2026 with a February 16, 2026 knowledge cutoff, now sits in a legacy block at $4.00 / $20.00 short-context, doubling to $8.00 / $30.00 above 272K.

Read the "50% cut" in that context. It is not a frontier price war. It is a previous-generation flagship being repositioned to stay sellable against its own successor, which is already cheaper on input, and against Chinese open-weight models that have taken a large share of OpenRouter traffic.

There is one more wrinkle worth knowing about. The bare `gpt-5.6` alias routes to Sol. Leaving a model string unqualified means you are billing at flagship rates by default while Terra or Luna may have been sufficient — the single most expensive default in the family.

## How do you actually capture the discount in code?

The discount only applies to requests that land on the OpenAI provider tag with non-BYOK credentials. Default routing often gets there, but "often" is not a pricing guarantee.

Pin the provider explicitly:

```python
response = client.chat.completions.create(
    model="openai/gpt-5.6-sol",
    messages=messages,
    extra_body={
        "provider": {
            "order": ["openai"],
            "allow_fallbacks": False,
        }
    },
)
```

Three settings carry the rest of the saving:

- **Keep input under 272,000 tokens.** Chunk or summarize rather than stuffing. Crossing the cliff doubles input for the whole request and turns the promo into a rounding error.
- **Pin `reasoning.effort` deliberately.** The default is `medium`. Moving to `high` or `max` to chase a benchmark score multiplies output billing, and output is where the money goes. Set the level per workload, not globally.
- **Reuse cached prefixes.** Cache reads cost $0.20 per million on the discounted route against $2.00 for fresh input. Long system prompts, tool schemas, and retrieval preamble that repeat across calls should be marked cacheable.

Non-urgent work belongs on the batch route at $1.00 / $5.00 — half the standard discounted rate. Evals, backfills, nightly enrichment, and dataset labeling rarely need interactive latency, and this is the cheapest published rate for Sol anywhere.

### A worked monthly estimate

Assume an agent workload at a 20:1 input-to-output ratio — 100 million input tokens and 5 million output tokens per month, with 80% of the input served from cache.

| Route | Input cost | Cached input | Output cost | Monthly total |
|---|---|---|---|---|
| OpenAI direct | $4.00 × 20M = $80.00 | $0.40 × 80M = $32.00 | $20.00 × 5M = $100.00 | $212.00 |
| OpenRouter, discounted | $2.00 × 20M = $40.00 | $0.20 × 80M = $16.00 | $10.00 × 5M = $50.00 | $106.00 |
| OpenRouter batch | $1.00 × 20M = $20.00 | — | $5.00 × 5M = $25.00 | $45.00 |

The discounted route halves the bill; batch roughly quarters it. Add the ~5.5% top-up fee to the OpenRouter figures if you fund by card. Then re-run the same arithmetic at long-context rates to see what happens if a chunking bug lets a prompt cross 272K.

## Decision guide: when is Sol at the promo price the right buy?

Match the workload to the route rather than defaulting to the cheapest token.

| Workload | Best pick | Reasoning |
|---|---|---|
| Hard agentic coding, high reliability required | GPT-5.6 Sol via OpenRouter OpenAI tag | Top Terminal-Bench 2.1 score, 84.5% four-for-four reliability, $2.00 / $10.00 |
| Bulk work that tolerates retries | Kimi K3 | 14.7 solved tasks per $100 against Sol's 5.3 |
| Long-context document analysis | None of the discounted routes | The 272K cliff erases the promo; chunk instead |
| Nightly evals, backfills, labeling | OpenRouter batch | $1.00 / $5.00, the cheapest published rate |
| Regulated data or residency requirements | OpenAI direct or Azure | First-party handling; accept $4.00 / $20.00 and no promo |
| Cost-sensitive with retry budget | Grok 4.6 at high effort | Ties Sol's index score at $0.84 per task |
| Mixed pipeline | Kimi-first cascade escalating to Sol | ~85.6% coverage, better than either model alone |

The planning number is $4.00 / $20.00, because that is what OpenAI's own card says and it is protected only "at least through November 21, 2026." The router's $2.00 / $10.00 is upside with an expiry nobody has restated. Budget on the first and pocket the second if it is still there when your invoice arrives.

## FAQ

**Did OpenAI cut GPT-5.6 Sol's price by 50%?**

No. OpenAI's own reduction was 20% on input and 33% on output, taking the list rate from $5.00 / $30.00 to $4.00 / $20.00 per million short-context tokens. The 50% figure is OpenRouter's promotion on its OpenAI route for non-BYOK traffic, launched August 17, 2026 and announced to expire September 18, 2026.

**Is the OpenRouter discount still active?**

Yes, as of October 1, 2026. OpenRouter's endpoints API returns the OpenAI and OpenAI Flex tags at $2.00 / $10.00 and $1.00 / $5.00 respectively, each carrying `discount: 0.5`. The original window was announced to end September 18, so the badge has outlived its stated expiry. No primary source has restated the new end date — verify before you commit to a long-run cost model.

**Does BYOK qualify for the 50% discount?**

No. The promotion applies to non-BYOK traffic only. A bring-your-own-key request routed through OpenRouter bills at list price and forfeits the discount, though BYOK carries a separate free allowance of $25,000 per month of list-price usage on pay-as-you-go. The two benefits do not stack.

**What happens above 272,000 tokens?**

Pricing switches to long-context rates for the entire request, not just the excess. OpenAI charges 2x input and 1.5x output once a prompt exceeds 272K input tokens, so a discounted OpenRouter request at that size costs $4.00 / $15.00 — at or above OpenAI's standard short-context list of $4.00 / $20.00 on input. Long-context workloads see almost no benefit from the promotion. Chunk instead, and make sure no request silently crosses the line.

**Is the `gpt-5.6` model alias the same as Sol?**

Yes, and that is a trap. The bare `gpt-5.6` model string routes to GPT-5.6 Sol, so an unqualified alias bills at the most expensive tier in the family by default. If Terra or Luna can handle the task, name them explicitly — Terra lists far below Sol, and Luna sits in a different order of magnitude entirely.

---

*Every price in this article was verified on October 1, 2026 against OpenRouter's endpoints API (`/api/v1/models/openai/gpt-5.6-sol/endpoints`) and OpenAI's model and pricing pages. Router promotions change without notice; re-check the API before committing budget.*
