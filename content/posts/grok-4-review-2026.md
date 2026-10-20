---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-05-07 00:00:00+00:00
description: Correct the original Grok 4 release timeline, distinguish retired model IDs from current endpoints, and evaluate migration without fabricated benchmarks.
draft: false
schema: schema-grok-4-review-2026
tags:
- grok-4
- xai
- llm
- api
- benchmark
- review
title: 'Grok 4 Review: Release Evidence, Retired API Names and Migration Checks'
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

A Grok 4 review in an older search result can describe a model different from the one an API request serves today. Before comparing quality or cost, establish the exact model identifier, whether it is an alias and which release the evidence describes.

This review checks release and migration documentation. It is not an independent performance benchmark. The previous cross-vendor score table had no reproducible evaluation source and has been removed.

## Correct the timeline and product identity

The original [Grok 4 launch announcement](https://x.ai/news/grok-4) is dated **July 9, 2025**, not the second quarter of 2026. A later family member's context window or price must not be assigned to that original release.

The [May 2026 retirement guide](https://docs.x.ai/developers/migration/may-15-retirement) lists older API names, including `grok-4-0709` and Grok Fast variants, and describes replacement behavior. Its detailed coding section separately describes the replacement for `grok-code-fast-1`. Do not infer that all legacy names behave identically.

The [current model catalog](https://docs.x.ai/developers/models) is the place to check current offerings. It also says real-time information requires enabled search tools. A plain text request should not be advertised as automatically searching the web.

## A successful legacy request may still be a migration

Use the [model migration worksheet](/research/content-quality-batch2-2026-10/model-migration.csv). Record the requested name, returned model identity when supplied, endpoint, reasoning settings, enabled tools and usage fields. Keep the old configuration and a set of representative requests before changing anything.

Check semantics as well as availability. A request returning successfully does not establish that it used the old weights, pricing, context limit or reasoning policy. An alias can deliberately move to another release.

For production work, choose an explicitly documented model and configuration. If a provider offers a fixed release identifier, check its retirement policy too; “fixed” does not promise indefinite availability.

Test text output, structured data, tool calls and streaming separately when your application uses them. A compatible chat-completions route does not establish support for every parameter or tool type from another provider's API.

## How to assess coding quality without a fabricated leaderboard

Select repository tasks with a known starting commit and success criteria: a failing test, a constrained refactor and a bug requiring a multi-file change. Give each candidate the same context and tool permissions.

Record accepted patches, failing tests, human changes, retries, elapsed time and billed usage. Keep unsuccessful attempts. A benchmark score collected under a different harness or budget is not interchangeable with this application test.

When reading supplier benchmarks, retain the model release, benchmark revision, tools, sampling settings and pass aggregation. If these are missing, treat the number as incomplete evidence. Do not fill a comparison table with approximate values merely to make every cell look complete.

## Cost and context belong to the exact model

As checked on October 20, 2026, the [Grok 4.7 page](https://docs.x.ai/developers/models/grok-4.7) describes a **500,000-token** context window and separate pricing for requests above its stated long-context threshold. Those are specifications of that current model page, not retroactive Grok 4 specifications.

The [Grok API pricing guide](/posts/xai-grok-api-pricing-2026/) explains input, cached-input, output and tool charges with explicit arithmetic. Keep price comparisons tied to the exact model and billing condition.

## Practical verdict

The defensible recommendation is to evaluate the current API on your workload, not purchase a capability implied by this article's old title. Existing integrations should audit model aliases and billing before treating continued HTTP success as continuity.

No independent evidence collected for this revision establishes that Grok is universally better or worse than another provider for coding. What this review establishes is the release identity, the need to handle retired names and a reproducible way to make the decision.

## Revision note

**Updated October 20, 2026.** Corrected the original release year, removed unsupported architecture, context, price and benchmark claims, and replaced the production-testing language with a documented migration evaluation.

## Primary sources

Checked October 20, 2026: [grok launch](https://x.ai/news/grok-4); [grok retirement](https://docs.x.ai/developers/migration/may-15-retirement); [grok models](https://docs.x.ai/developers/models); [grok price](https://docs.x.ai/developers/models/grok-4.7).
