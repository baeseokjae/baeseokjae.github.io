---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-05-07 12:00:00+00:00
description: Read Grok's model-specific rates, account for context tiers and tool charges, and reproduce a token-cost calculation with transparent assumptions.
draft: false
schema: schema-xai-grok-api-pricing-2026
tags:
- grok
- xai
- api-pricing
- llm-pricing
- cost-comparison
title: 'xAI Grok API Pricing: Current Rates, Cached Tokens, Tools and Legacy-Model Changes'
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

The cost of a Grok API job depends on the model actually served, token categories, context tier, tool use and retries. A single “price per million tokens” hides several of those inputs.

This guide records a checked public rate example and shows how to reconcile it with usage. It does not replace your account's bill or promise a universal saving against another model.

## A checked current model example

On October 20, 2026, the [Grok 4.7 model page](https://docs.x.ai/developers/models/grok-4.7) lists:

| Token category | Displayed base rate, USD per million tokens |
|---|---:|
| Input | $2.00 |
| Cached input | $0.50 |
| Output | $6.00 |

The same page notes different pricing for requests exceeding **200,000 context tokens**. Do not apply the base row to such requests without checking the applicable tier and region. This table is a dated example for one model, not a complete catalog.

Use the [current catalog](https://docs.x.ai/developers/models) to select other models. The [retirement guide](https://docs.x.ai/developers/migration/may-15-retirement) explains that legacy names can route to replacements with different prices. The old low-cost table in this article is therefore not a safe basis for current production estimates.

## Calculate disjoint token categories

Suppose a batch of requests, each within the base pricing conditions, totals **1,000,000 input tokens**, of which **200,000 are billed as cached**, plus **200,000 output tokens**. The uncached portion is **800,000**.

`token cost = 800,000/1,000,000 × $2 + 200,000/1,000,000 × $0.50 + 200,000/1,000,000 × $6 = $2.90`

Without cache billing on those inputs, the same aggregate would be **$3.20** at these base rates. This is a calculation, not a prediction that a request will receive cache hits.

The [calculator source](/research/content-quality-batch2-2026-10/evidence_checks.py) takes uncached, cached and output counts separately. Its [offline execution record](/research/content-quality-batch2-2026-10/offline-results.json) checks this example and rejects negative or non-finite inputs. It does not query your account or make API requests.

## Tools, retries and reasoning can change the bill

The [tool overview](https://docs.x.ai/developers/tools/overview) describes token charges plus tool invocation charges. A request can invoke more than one tool, so count actual calls rather than assuming one search per user message.

Keep provider usage fields and billing definitions intact. Do not add a reasoning-token subtotal again if it is already included in the billed output category. Likewise, do not add cached tokens to total input when they are already a subset of it.

Retries can repeat billed work. Record failed attempts and tool calls as part of the job, then reconcile totals with the provider's usage report. A successful final answer does not mean only the final attempt incurred cost.

## A tool-fee illustration, clearly separated from the tariff

If a separate tool hypothetically costs $5 per thousand calls and your batch makes 100 calls, the tool component is $0.50. Added to the $2.90 token illustration, that produces $3.40.

The $5 figure is an input assumption for demonstrating the formula, not a quoted xAI rate. Replace it with the current price of the actual tool. The same calculator accepts a tool-call count and per-thousand rate so the assumption remains visible.

## Reconcile an estimate with a real bill

Use the [API cost worksheet](/research/content-quality-batch2-2026-10/api-cost-ledger.csv). Record request/job ID, model requested, model served when exposed, region/tier, uncached input, cached input, output, tools, retries and billed amount.

Investigate differences by category. A model alias change, long-context request, missed cache, extra tool round or retried job can explain why an estimate diverges. Separate consumer subscriptions from API billing.

Compare providers by the cost of an accepted result on the same task, including rework. A cheaper input-token rate alone does not establish equivalent quality or lower total cost.

## Revision note

**Updated October 20, 2026.** Removed obsolete three-model pricing and unsupported cross-provider savings. Added a dated current rate example, long-context caveat, legacy-name warning and reproducible disjoint-token arithmetic.

## Primary sources

Checked October 20, 2026: [grok price](https://docs.x.ai/developers/models/grok-4.7); [grok models](https://docs.x.ai/developers/models); [grok retirement](https://docs.x.ai/developers/migration/may-15-retirement); [grok tools](https://docs.x.ai/developers/tools/overview).
