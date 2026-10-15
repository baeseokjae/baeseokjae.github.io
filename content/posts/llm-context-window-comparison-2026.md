---
cover:
  alt: 'LLM Context Window Comparison 2026 cover graphic: the article title on a dark green background'
  image: /images/llm-context-window-comparison-2026.png
  relative: false
date: 2026-04-22 16:04:57+00:00
lastmod: 2026-10-15 00:00:00+00:00
description: 'Which LLM has the largest usable context window in 2026? A dated, first-party comparison of GPT-4.1, Claude Opus 4.6, Gemini 2.5 Pro and Llama 4 that separates advertised windows from billed and usable context.'
draft: false
schema: schema-llm-context-window-comparison-2026
tags:
- LLM
- context window
- GPT-4.1
- Claude Opus 4.6
- Gemini 2.5 Pro
- Llama 4
- AI comparison
title: 'LLM Context Window Comparison 2026 (refreshed): Ranked by Largest Usable Context, Not Advertised Maximum'
---

The 2026 version of "which model has the largest context window" no longer has a single winner among the hosted APIs developers actually call, because those models now advertise the same ~1M-token class: OpenAI's GPT-4.1 is documented at 1,047,576 tokens, Google's Gemini 2.5 Pro at 1,048,576 tokens, and Anthropic's Claude Opus 4.6 at 1M tokens. What still separates them is whether the long window is the default or a beta, how many tokens one response can generate inside that window, and how much of the window your document keeps once system prompts, tool definitions, tool results and the model's own output are counted against it. Every figure below was read from the vendors' own documentation on 2026-10-15, and the numbers this refresh could not confirm were withdrawn rather than restated.

One documented figure sits outside that hosted group. Meta's Llama 4 model card lists a "Context length" of 10M tokens for Llama 4 Scout (17Bx16E) and 1M tokens for Llama 4 Maverick (17Bx128E) - the largest advertised context figure in this comparison - but the same card states no API, price or maximum-output figure for either variant, so those numbers are checkpoint statements rather than hosted request limits, and they are listed separately below instead of being ranked against the APIs.

## Ranked: largest usable context window in 2026

The ranking below is by what a single API request can realistically spend on your content: the advertised window, whether long context is the default rather than a beta header, and the maximum output the same request can produce.

| # | Model | Advertised context window | Max output tokens | Published price | How the long window is documented | Source (checked 2026-10-15) |
|---|---|---|---|---|---|---|
| 1 | Claude Opus 4.6 | 1M tokens | up to 128k output tokens | $5 / MTok input, $25 / MTok output; the full window at standard pricing | Default: "1M is the default: you don't need a beta header" | [Anthropic context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) |
| 2 | Gemini 2.5 Pro | 1,048,576 tokens | 65,536 tokens | not restated in this refresh | Documented model limit on the Vertex AI model page (thinking supported) | [Google Cloud Vertex AI model page](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro) |
| 3 | GPT-4.1 | 1,047,576 tokens | 32,768 tokens | $2 / 1M input, $8 / 1M output | One flat published token price, plus a separate "Long Context" rate-limit tier starting at 128k input tokens | [OpenAI gpt-4.1 model page](https://platform.openai.com/docs/models/gpt-4.1) |

Reading the ranking honestly: the three hosted windows differ by at most 48,576 tokens out of roughly one million (1,048,576 versus 1,047,576 versus 1M) - under 5% of a million, which is not a meaningful difference in advertised size but noise in how each vendor states the number. They are ordered here by output headroom and by whether the long window is the default, because those are the differences that change a design.

### The largest documented figure is not in that ranking

| Model variant (as named on the card) | Documented context length | Max output tokens | Source (checked 2026-10-15) |
|---|---|---|---|
| Llama 4 Scout (17Bx16E) | 10M tokens | not stated on the model card | [Meta Llama 4 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md) |
| Llama 4 Maverick (17Bx128E) | 1M tokens | not stated on the model card | [Meta Llama 4 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md) |

Both rows come from the "Context length" column of the card's own model table. The card publishes no maximum-output figure for either variant, which is why there is no output column to compare against the hosted APIs above. It also contains exactly one mention of 128K: the label on its Long Context / MTOB evaluation row ("Context window is 128K"), which is the context setting used for that long-context evaluation rather than the context length the model table advertises. The card publishes no measured usable-context figure at any length, so neither row supports a claim about how much of the window is usable in practice.

## Advertised, billed and usable are three different numbers

**Advertised** is the maximum the API accepts. OpenAI's model page documents a 1,047,576-token context window for GPT-4.1; Google's Vertex AI page documents 1,048,576 tokens for Gemini 2.5 Pro; Anthropic lists Claude Opus 4.6 among the models with a 1M-token context window. None of those pages publishes retrieval accuracy at length, so an advertised maximum is a capacity statement, not a quality statement.

**Billed** is how the vendor charges for tokens inside that window - and the pricing shape differs by vendor, not by headline size. Anthropic states that Claude 4.6 and later models "include the full 1M token context window at standard pricing. (A 900k-token request is billed at the same per-token rate as a 9k-token request.)" The documented exception is Claude Haiku 5.5, which is priced by prompt length: prompts over 100,000 tokens pay higher prices ([Anthropic long context pricing](https://platform.claude.com/docs/en/about-claude/pricing)). OpenAI's GPT-4.1 page shows one flat text-token row - $2 per 1M input tokens, $8 per 1M output tokens - alongside a separate "Long Context" rate-limit tier labelled "128k input tokens". A rate-limit tier is not a price surcharge, and this refresh does not claim a length-based price multiplier for GPT-4.1 in either direction.

**Usable** is the smallest of the three, and it is the one most often ignored. Anthropic documents the accounting: "Everything in the request counts toward the context window: the system prompt, every message in `messages` (including tool results, images, and documents), and your tool definitions. The output Claude generates for the turn, including its extended thinking, counts too." That accounting is the practical difference between a 1M-token window and a 1M-token document budget: an agentic session spends window tokens on tool schemas and tool results that the author never wrote, and reasoning tokens are drawn from the same pool as the answer.

One more conversion trap sits inside the token count. Anthropic notes that 1M tokens is "roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7)", while "models before it fit about 750k words in 1M tokens", and that 200k tokens is roughly 150k words ([Anthropic models overview](https://platform.claude.com/docs/en/models/overview)). The same million tokens is therefore a different amount of text depending on which generation you call, which is why word-count-based capacity planning across model versions silently drifts.

## The constraint that actually binds long-document work: max output

For long-document and long-agent work, the output cap is usually what breaks first, and it is the one number the "largest window" framing hides. GPT-4.1 is documented at 32,768 max output tokens, Gemini 2.5 Pro at 65,536, and Anthropic's 1M-token models at up to 128k output tokens per request. Meta's Llama 4 model card states no maximum-output figure for either variant, so the open-weights checkpoint cannot be compared on this axis from the same kind of source. If your task is extraction, restructuring or summarisation - where the answer is itself long - a 1M-token input window paired with a 32K output cap will fail on the response before it ever fails on the input. Practical selection rules that follow from the documented limits:

- Long document, long answer (contract restatement, whole-codebase rewrite): rank by max output first, advertised window second.
- Long agent session (many turns of tool results, thinking tokens): check whether long context is the default or requires a beta, and budget for tool definitions and tool results inside the window.
- Cost-sensitive high-volume input: compare the published input price per 1M tokens and whether the vendor publishes a length-tiered price row for the window you intend to use.

## Why "largest" is the wrong criterion on its own

Anthropic states plainly that a bigger window is not automatically better: "A larger context window allows the model to handle more complex and lengthy prompts, but more context isn't automatically better. As token count grows, accuracy and recall degrade, a phenomenon known as *context rot*. This makes curating what's in context just as important as how much space is available." That is a qualitative vendor statement, and none of the documentation pages checked for this refresh publishes an accuracy-at-length curve - so the honest engineering takeaway is that capacity must be validated against your own task rather than assumed. If you are deciding between loading everything into a 1M-token window and retrieving smaller slices, the retrieval-side trade-off is covered separately in [Bigger context windows don't make RAG smarter](https://baeseokjae.github.io/posts/bigger-context-windows-rag-smarter-2026/).

## What this refresh corrected, withdrew or could not verify

This page previously carried several figures that no longer resolve against first-party documentation. They are listed here instead of being quietly deleted:

- The Claude row read "200K (1M beta)" with a 2x surcharge above 200K. Anthropic's current documentation lists Claude Opus 4.6 among the 1M-token models, states that "1M is the default: you don't need a beta header", and prices the full window at standard rates. The 200K-with-beta framing is stale for Opus 4.6.
- The GPT-4.1 claim "no surcharges at any length" has been narrowed to what the vendor page actually shows: one flat published token price row plus a Long Context rate-limit tier. Rate limits are not surcharges, and the page does not document a length-tiered price for GPT-4.1 either way.
- Qwen Long Latest's "10M tokens at $0.07/M input - the largest context available commercially" has been removed. The Alibaba Cloud Model Studio long-context page was fetched on 2026-10-15 but did not yield a quotable primary statement of a 10M-token window at that price, so the figure is marked unconfirmed rather than repeated.
- Gemini 2.5 Pro's published "1M tokens (2M beta)" has been narrowed to the documented 1,048,576-token figure on the Vertex AI model page. The ai.google.dev models page was fetched on 2026-10-15 and its body contained no quotable statement of a 2M-token window (the model table is client-rendered), so the 2M beta claim is withdrawn pending a quotable source.
- All inherited benchmark percentages (SWE-Bench shares, RULER deltas between 4K and 128K context, a safe-response rate, an LMArena rank) and the previous "200K pricing cliff doubles your bill" cost tables have been removed: none of them was re-verified against a dated first-party artifact for this refresh.

## Evidence dates and limitations

- Every advertised window, output cap and price above was read from the vendor documentation linked inline on 2026-10-15. This is a documentation review, not a benchmark run: no needle-in-a-haystack, RULER or long-context accuracy test was executed for this refresh, and no usable-context percentage is claimed or implied. The record of that reading is a private author-side verification, not a downloadable resource - the public primary sources for every figure are the vendor pages linked inline above.
- The two Llama 4 rows are checkpoint figures taken from the model card's "Context length" column, not hosted API limits, which is why they are listed outside the ranking. That card lives on the main branch of the meta-llama/llama-models repository and can change without notice, so both figures are bound to the 2026-10-15 fetch rather than stated as permanent.
- Prices are USD list prices per 1M tokens as published on those pages; no currency conversion, tax or enterprise agreement term is considered.
- Google figures come from the Vertex AI model documentation, Meta figures from the Llama 4 model card, Anthropic figures from the Claude context-windows, models overview and pricing pages, and OpenAI figures from the gpt-4.1 model page. Vendor documentation changes without notice, so each figure carries its check date rather than being stated as permanent.
- The existing cover graphic was preserved unchanged, as required for a refresh of this URL; its subtitle still reads "GPT-4o vs Claude vs Gemini", which is the framing this revision replaces.
- Model naming is as published: "Claude Opus 4.6", "Gemini 2.5 Pro", "GPT-4.1" and the two named Llama 4 variants refer to the models named on those pages, and Anthropic notes that other Claude models - including a deprecated Sonnet release - remain at 200k tokens, so "Claude" is not one window size.
