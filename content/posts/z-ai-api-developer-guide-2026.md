---
cover:
  alt: Z.ai API Developer Guide 2026
  image: /images/z-ai-api-developer-guide-2026.png
  relative: false
date: 2026-05-15 06:05:13+00:00
description: 'Updated October 2026: the current GLM-5.3 / GLM-5.3-Flash lineup, credits-based
  Coding Plan pricing from 18 USD/month, per-1M-token API prices and verified base URLs.'
draft: false
schema: schema-z-ai-api-developer-guide-2026
tags:
- Z.ai
- Zhipu AI
- GLM
- API
- Claude Code
- developer guide
title: 'Z.ai API Developer Guide 2026: GLM-5.3 Models, Pricing and Setup'
lastmod: 2026-10-08 00:00:00+00:00
---

Z.ai is Zhipu AI's international developer platform for the GLM model family, exposing the models through both an Anthropic-compatible and an OpenAI-compatible API ([quick start](https://docs.z.ai/devpack/quick-start)). As of October 2026, the current flagship is GLM-5.3 with the cheaper GLM-5.3-Flash alongside it, and the GLM Coding Plan has moved from quarterly tiers to a credits-based subscription that the vendor advertises as starting at 18 USD per month ([plan overview](https://docs.z.ai/devpack/overview)). This refresh re-opened the vendor's own pages and replaced the model names, prices and base URLs that had gone stale since May.

## What Z.ai Is and the Current GLM Lineup (GLM-5.3 / GLM-5.3-Flash)

Z.ai is the international-facing platform for Zhipu AI's GLM (General Language Model) series. It offers two compatibility layers: Claude Code and other Anthropic-protocol tools point at `https://api.z.ai/api/anthropic`, while OpenAI-protocol tools use the endpoints listed in the [quick start documentation](https://docs.z.ai/devpack/quick-start). The vendor's [release notes](https://docs.z.ai/release-notes/new-released) date the current generation: GLM-5.3 on 2026-08-18, GLM-5.3-Flash on 2026-08-26, GLM-5.2 on 2026-06-16 and GLM-5.1 on 2026-04-07.

GLM-5.3 is text-only, with a 1M-token context window and a maximum output length of 128K tokens; reasoning is always enabled and supports three effort levels (`low`, `high`, `max`), and disabling reasoning is no longer supported ([GLM-5.3 model page](https://docs.z.ai/guides/llm/glm-5.3)). GLM-5.3-Flash is a 320B-parameter model with 18B activated parameters; the vendor describes it as the first open-source frontier model to combine sparse and linear attention, reporting a 3.01x reduction in attention computation and a 4.44x reduction in KV cache versus GLM-5.3 ([GLM-5.3-Flash page](https://docs.z.ai/guides/vlm/glm-5.3-flash)). The preceding GLM-5.2 introduced 1M "lossless" context for long-horizon tasks ([release notes](https://docs.z.ai/release-notes/new-released)).

| Model | Released | Context | Input | Output |
|---|---|---|---|---|
| GLM-5.3 | 2026-08-18 | 1M | $1.40/M | $4.40/M |
| GLM-5.3-Flash | 2026-08-26 | 1M | $0.15/M | $0.50/M |
| GLM-5.3-FlashX | — | 1M | $0.37/M | $1.25/M |
| GLM-5.2 | 2026-06-16 | 1M | $1.40/M | $4.40/M |
| GLM-5.1 | 2026-04-07 | — | $1.40/M | $4.40/M |
| GLM-4.7 | — | — | $0.60/M | $2.20/M |
| GLM-4.7-Flash | — | — | Free | Free |
| GLM-4.5-Flash | — | — | Free | Free |

Prices and release dates above are taken verbatim from the vendor's [pricing page](https://docs.z.ai/guides/overview/pricing) and [release notes](https://docs.z.ai/release-notes/new-released) as read on 2026-10-08; context figures are the vendor's own statements.

### Which Model Should You Default To?

For a coding agent, the Coding Plan is designed around GLM-5.3 and GLM-5.3-Flash specifically, and the vendor routes older model names onto them automatically ([plan overview](https://docs.z.ai/devpack/overview)). For pay-as-you-go API work where cost dominates, GLM-5.3-Flash at $0.15/M input and $0.50/M output is roughly an order of magnitude cheaper than GLM-5.3, and GLM-4.7 at $0.60/$2.20 remains the mid-tier option ([pricing page](https://docs.z.ai/guides/overview/pricing)). The choice is a cost-versus-capability trade you should validate against your own task mix rather than a published benchmark.

This guide covers the platform, pricing and setup; for the models themselves see the [GLM-5 and GLM-5.1 developer review](/posts/glm-5-developer-review-2026/), for how GLM stacks against closed frontier models see the [GLM-5.1 vs Claude vs GPT-6 comparison](/posts/glm-5-1-vs-claude-gpt-2026/), and for how the Coding Plan price sits against other vendors see the [AI coding tools pricing comparison](/posts/ai-coding-tools-pricing-2026/).

## GLM Coding Plan: Credits-Based Pricing From 18 USD/Month

The GLM Coding Plan is a subscription package aimed at coding agents such as Claude Code, Cline and OpenCode ([plan overview](https://docs.z.ai/devpack/overview)). Zhipu AI moved it to a credits-based system with a notice dated 2026-07-30 (Singapore Standard Time), which also states that legacy subscribers are migrated to the current plan structure ([plan update announcement](https://docs.z.ai/devpack/notice/usage-revision)). Pricing starts at 18 USD per month according to the vendor's plan page ([plan overview](https://docs.z.ai/devpack/overview)), and the subscribe landing page states "Plans from 18/month" in its metadata ([z.ai/subscribe](https://z.ai/subscribe)).

All plans support GLM-5.3 and GLM-5.3-Flash. Requests naming GLM-5.2 or GLM-5.1 are automatically routed to GLM-5.3, and requests naming GLM-4.7 are routed to GLM-5.3-Flash ([plan overview](https://docs.z.ai/devpack/overview)). Each plan carries both a 5-hour and a weekly credit allowance:

| Plan | 5-Hour Credits | Weekly Credits |
|---|---|---|
| Lite | 2,000 | 10,000 |
| Pro | 12,000 | 60,000 |
| Max | 28,000 | 140,000 |

Credit consumption is not token count. The vendor's formula is `(input tokens × input multiplier + cached input tokens × cached multiplier + output tokens × output multiplier) / 10,000`, with MCP tool calls charged per call ([plan overview](https://docs.z.ai/devpack/overview)). Current multipliers are GLM-5.3 at 6.9 input / 1.7 cached / 24 output and GLM-5.3-Flash at 2.3 / 0.56 / 8; Web Search, Web Reader and Zread MCP calls each carry a multiplier of 1.2. Off-peak usage is charged at 50% of the standard credit rate, with peak hours defined as Monday to Friday 14:00–18:00 Singapore Standard Time ([plan overview](https://docs.z.ai/devpack/overview)).

For teams, the plan is sold per seat with its own allowances: a Standard Seat carries 15,000 five-hour and 66,000 weekly credits, and a Premium Seat carries 35,000 and 155,000 ([team plan](https://docs.z.ai/devpack/teamplan)).

The vendor's legacy migration notice lists the current standard plan prices as Lite $18, Pro $72 and Max $160 per month ([legacy plan migration notice](https://docs.z.ai/devpack/transition)). That page presents them in a migration context — legacy subscribers receive two complimentary months of the equivalent current tier — so treat the Pro and Max figures as the vendor's listed standard prices on the date read rather than as a checkout-confirmed quote.

## Pay-as-You-Go API Pricing per 1M Tokens

Separate from the subscription, the platform bills per token for direct API calls. The vendor's [pricing page](https://docs.z.ai/guides/overview/pricing), read on 2026-10-08, lists these text models (USD per 1M tokens, input / cached input / output):

| Model | Input | Cached Input | Output |
|---|---|---|---|
| GLM-5.3 | $1.40 | $0.26 | $4.40 |
| GLM-5.2 | $1.40 | $0.26 | $4.40 |
| GLM-5.1 | $1.40 | $0.26 | $4.40 |
| GLM-5 | $1.00 | $0.20 | $3.20 |
| GLM-4.7 | $0.60 | $0.11 | $2.20 |
| GLM-4.7-FlashX | $0.07 | $0.01 | $0.40 |
| GLM-4.6 | $0.60 | $0.11 | $2.20 |
| GLM-4.5 | $0.60 | $0.11 | $2.20 |
| GLM-4.5-X | $2.20 | $0.45 | $8.90 |
| GLM-4.5-Air | $0.20 | $0.03 | $1.10 |
| GLM-4.5-AirX | $1.10 | $0.22 | $4.50 |
| GLM-4-32B-0414-128K | $0.10 | — | $0.10 |
| GLM-4.7-Flash | Free | Free | Free |
| GLM-4.5-Flash | Free | Free | Free |

GLM-5.3-Flash is billed at $0.15 input / $0.03 cached / $0.50 output and GLM-5.3-FlashX at $0.37 / $0.075 / $1.25 on the same page. Cached input storage is marked "Limited-time Free" for every listed model except GLM-4-32B-0414-128K, so that line item may not persist ([pricing page](https://docs.z.ai/guides/overview/pricing)). A separate vision section lists GLM-4.6V at $0.30/$0.90, GLM-4.5V at $0.60/$1.80, GLM-4.6V-FlashX at $0.04/$0.40, GLM-OCR at $0.03, and GLM-4.6V-Flash as free.

## Endpoints: Anthropic, OpenAI Chat Completions, OpenAI Responses and the General API

Z.ai's Coding Plan endpoints are documented per protocol, and the May version of this guide's `https://api.z.ai/api/openai/v1` address does not appear in them ([quick start](https://docs.z.ai/devpack/quick-start), [latest model](https://docs.z.ai/devpack/latest-model)):

| Protocol | Base URL |
|---|---|
| Anthropic Messages (Claude Code, Goose) | `https://api.z.ai/api/anthropic` |
| OpenAI Chat Completions | `https://api.z.ai/api/coding/paas/v4` |
| OpenAI Responses (Codex) | `https://api.z.ai/api/v1` |

The general, non-plan API is a different address: `https://api.z.ai/api/paas/v4`, authenticated with `Authorization: Bearer YOUR_API_KEY` ([API reference](https://docs.z.ai/api-reference/introduction), [HTTP introduction](https://docs.z.ai/guides/develop/http/introduction)). The vendor explicitly warns Coding Plan users to configure their dedicated plan endpoint rather than the general one, since the two are not interchangeable ([API reference](https://docs.z.ai/api-reference/introduction)).

## Quick Start: OpenAI-Compatible API Setup in Python

Register on Z.ai, create an API key in the dashboard, and point any OpenAI SDK client at the Coding Plan chat-completions endpoint ([quick start](https://docs.z.ai/devpack/quick-start)):

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-z-ai-api-key",
    base_url="https://api.z.ai/api/coding/paas/v4"
)

response = client.chat.completions.create(
    model="glm-5.3",
    messages=[
        {"role": "user", "content": "Write a Python function to parse JWT tokens without a library."}
    ]
)

print(response.choices[0].message.content)
```

Model identifiers follow the lowercase hyphenated pattern the docs use, for example `glm-5.3` and `glm-5.3-flash` ([latest model](https://docs.z.ai/devpack/latest-model)). A 1M-token context is requested by appending the `[1m]` suffix to the model name, for example `glm-5.3[1m]` ([latest model](https://docs.z.ai/devpack/latest-model)). Note that GLM-5.3 is text-only, so multimodal inputs belong on GLM-5.3-Flash, which the vendor documents as a vision-capable model ([GLM-5.3-Flash page](https://docs.z.ai/guides/vlm/glm-5.3-flash)).

## Claude Code + Z.ai: Drop-In Setup via the Anthropic Endpoint

Claude Code talks to Z.ai through the Anthropic-compatible base URL. The vendor documents three approaches: an automated coding-tool helper, an install script for macOS and Linux, and manual configuration ([Claude Code setup](https://docs.z.ai/devpack/tool/claude)). The two essential variables are unchanged from any Anthropic-protocol redirect:

```bash
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-ai-api-key"
export API_TIMEOUT_MS="3000000"
```

The helper is invoked as `npx @z_ai/coding-helper`, and there is also a shell script at `https://cdn.bigmodel.cn/install/claude_code_zai_env.sh` that writes the values into `~/.claude/settings.json` ([Claude Code setup](https://docs.z.ai/devpack/tool/claude)). The manual configuration shown on the same page maps Claude Code's internal model slots to GLM names and enables 1M context directly:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your_zai_api_key",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-5.3-flash[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.3[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.3[1m]",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "API_TIMEOUT_MS": "3000000"
  }
}
```

Two details from the vendor's current page are worth noting because they differ from the May version of this guide. First, the default model mapping now points the Opus, Sonnet and Haiku slots at `GLM-5.3-Flash` before manual overrides, not at GLM-5.1 ([Claude Code setup](https://docs.z.ai/devpack/tool/claude)). Second, the documented timeout is `3000000` ms, not the `300000` ms shown previously ([Claude Code setup](https://docs.z.ai/devpack/tool/claude)). The vendor describes the helper as a companion that loads the Coding Plan into supported coding tools, installs tools, configures the plan and manages MCP servers ([Claude Code setup](https://docs.z.ai/devpack/tool/claude)).

## Other Coding Tools and Model Switching

Beyond Claude Code, the vendor's plan overview names Cline and OpenCode as supported coding tools ([plan overview](https://docs.z.ai/devpack/overview)), and the model-switching guide additionally covers Claude Code, Goose and Codex for endpoint configuration ([latest model](https://docs.z.ai/devpack/latest-model)). Codex uses the OpenAI Responses endpoint at `https://api.z.ai/api/v1`; other OpenAI-compatible tools use the chat-completions endpoint at `https://api.z.ai/api/coding/paas/v4` ([latest model](https://docs.z.ai/devpack/latest-model)). Model switching is done in the tool itself or by changing the model identifier in the environment variables, and the vendor's documentation walks through setting `glm-5.3` versus `glm-5.3-flash` and the `[1m]` context variant ([latest model](https://docs.z.ai/devpack/latest-model)).

## GLM Coding Plan vs Direct API: Which Should You Use?

The Coding Plan and pay-as-you-go pricing are optimized for different workload shapes. The plan is a fixed monthly price against a credit allowance with a rolling 5-hour window and a weekly cap, which suits bursty interactive coding sessions where per-request token counts are hard to predict ([plan overview](https://docs.z.ai/devpack/overview)). Direct per-token billing is charged by actual consumption and is easier to model for batch jobs, pipelines and other workloads with estimable monthly token volume, using the rates on the [pricing page](https://docs.z.ai/guides/overview/pricing).

| Scenario | Recommended | Why |
|---|---|---|
| Claude Code as a secondary daily driver | Coding Plan Lite (from $18/mo) | Flat price; credits reset within the plan's windows |
| Claude Code as the primary environment all day | Coding Plan Pro / Max | Larger 5-hour and weekly credit allowances |
| Production API with predictable volume | Direct per-token | Billing tracks actual usage with no quota to waste |
| Free exploration and prototypes | GLM-4.7-Flash / GLM-4.5-Flash | Listed as free on the pricing page |
| Budget-sensitive batch work | GLM-5.3-Flash or GLM-4.7-FlashX | Lowest listed input rates in the current table |

One planning note: credits are consumed by the weighted formula above, and MCP tool calls consume credits too, so an agent that leans on Web Search, Web Reader or Zread burns quota faster than raw token counts suggest ([plan overview](https://docs.z.ai/devpack/overview)).

## What Changed in This October 2026 Refresh

This revision corrects several figures that the May 2026 version of this page carried and that the vendor's own pages now contradict:

- The flagship is GLM-5.3, not GLM-5.1. GLM-5.1 is a legacy tier whose requests are routed onto GLM-5.3 ([release notes](https://docs.z.ai/release-notes/new-released), [plan overview](https://docs.z.ai/devpack/overview)).
- The previous SWE-bench Pro score for GLM-5.1 and the "first open-weight model to top the leaderboard" framing were not re-confirmable from any vendor page on 2026-10-08, so they have been removed from this article rather than restated.
- The quarterly Coding Plan prices ($30/$90/$240 per quarter) are gone. The vendor now advertises a credits-based plan from 18 USD/month, with standard prices of $18/$72/$160 listed in the migration notice ([plan overview](https://docs.z.ai/devpack/overview), [legacy plan migration notice](https://docs.z.ai/devpack/transition)).
- The OpenAI-compatible endpoint `https://api.z.ai/api/openai/v1` does not appear in the vendor's current Coding Plan endpoint table; the documented addresses are `https://api.z.ai/api/coding/paas/v4` (chat), `https://api.z.ai/api/v1` (responses) and `https://api.z.ai/api/anthropic` (Anthropic) ([quick start](https://docs.z.ai/devpack/quick-start), [latest model](https://docs.z.ai/devpack/latest-model)).
- The claim that the GLM-5.x models were trained without Nvidia hardware, and the 745B-parameter and 8-hour/21,500-QPS figures, were not confirmable from the vendor's current pages and have been removed.
- The GLM-4.7 price of $0.60/M input and $2.20/M output is confirmed unchanged on the current pricing page ([pricing page](https://docs.z.ai/guides/overview/pricing)); GLM-4.7-Flash and GLM-4.5-Flash remain free.

The previous FAQ entry about a "$3/month promotion" ending on a specific February date was not confirmable from vendor documentation and has been dropped.

## Frequently Asked Questions

**Q: Does Z.ai work as a Claude Code backend outside China?**
Z.ai is the international platform for the GLM family and its Anthropic-compatible endpoint at `https://api.z.ai/api/anthropic` is documented for Claude Code, Goose and similar tools ([Claude Code setup](https://docs.z.ai/devpack/tool/claude), [latest model](https://docs.z.ai/devpack/latest-model)). Registration and key creation happen on the Z.ai open platform ([Claude Code setup](https://docs.z.ai/devpack/tool/claude)).

**Q: Is GLM-5.3 open-weight, and can I run it locally?**
The vendor's model pages describe GLM-5.3-Flash as combining sparse and linear attention and report parameter counts, but this article does not claim a specific local-deployment hardware requirement because the current vendor pages reviewed here do not state one ([GLM-5.3-Flash page](https://docs.z.ai/guides/vlm/glm-5.3-flash)). Confirm licensing and weights from the vendor or model repository directly before planning local inference.

**Q: How do I get the 1M-token context window?**
Append the `[1m]` suffix to the model identifier, for example `glm-5.3[1m]` or `glm-5.3-flash[1m]`, and set `CLAUDE_CODE_AUTO_COMPACT_WINDOW` to `1000000` in the Claude Code configuration ([latest model](https://docs.z.ai/devpack/latest-model)).

**Q: Do Coding Plan quotas roll over?**
Credits are described as a 5-hour window that refreshes dynamically after consumption and a weekly allowance that resets every 7 days ([plan overview](https://docs.z.ai/devpack/overview)). There is no documented roll-over of unused credits across the weekly reset.

**Q: How are credits charged for MCP tool calls?**
MCP usage is charged as number of calls multiplied by the tool's output multiplier — 1.2 for Web Search, Web Reader and Zread — rather than by tokens ([plan overview](https://docs.z.ai/devpack/overview)).

## Sources and Verification Notes

Every price, model name, endpoint and date in this article was re-read from the vendor's own documentation on 2026-10-08 (UTC) at the pages linked inline above. The full Pro and Max monthly prices come from the vendor's migration notice, which frames them as current standard prices; the subscribe checkout page itself is a JavaScript application whose static HTML exposes only the "Plans from 18/month" description, so the Lite floor is the only figure visible there. No benchmark, parameter count, throughput or search-volume figure in this article is measured by the author, and vendor-reported multipliers and capability claims are labelled as vendor statements.
