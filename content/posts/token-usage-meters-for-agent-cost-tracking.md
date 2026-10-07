---
title: "Agent Token Usage Meter: How to Measure and Control AI Agent Costs in 2026"
date: 2026-10-01T09:12:23+00:00
tags:
  - "agent token usage meter"
  - "how to measure agent token usage"
  - "token usage meter for AI agents"
  - "per-agent token cost tracking"
  - "agent cost tracking observability"
  - "OpenTelemetry gen_ai token metrics"
  - "gen_ai.client.inference.usage.input_tokens"
  - "LLM token metering for billing"
  - "per-run token usage OpenAI Agents SDK"
  - "cache read tokens cost calculation"
  - "tokens to dollars LLM cost formula"
  - "prompt cache hit rate cost"
  - "LiteLLM max_budget budget_duration spend tracking"
  - "Langfuse token and cost tracking"
  - "OpenMeter LLM token metering"
  - "agent run cost attribution boundary"
  - "runaway agent cost detection"
  - "usage-based billing for AI agents"
description: "An agent token usage meter logs the provider's per-call usage object, splits input, output and cache-read tokens, then converts each to dollars."
draft: false
cover:
  image: "/images/token-usage-meters-for-agent-cost-tracking.png"
  alt: "Agent Token Usage Meter: How to Measure and Control AI Agent Costs in 2026"
  relative: false
schema: "schema-token-usage-meters-for-agent-cost-tracking"
---

An agent token usage meter is the component that reads the provider's `usage` object on every model response, keeps input, output, and cache-read tokens separate, and converts those counts into dollars at log time using a versioned price table. It meters a run, not a request, because one agent task fans out into dozens of model calls.

That is the short answer. The rest of this guide separates the four quantities people keep collapsing into one number, shows where the ground truth actually lives, explains the OpenTelemetry contract the industry is converging on, and states plainly where the current tooling still fails.

## What an Agent Token Usage Meter Actually Has to Measure

The single most common metering bug is reporting "tokens used" as one figure. Four distinct quantities flow through every agent, and they are not priced remotely the same way.

| Quantity | Provider field (Anthropic) | Provider field (OpenAI) | How it is priced |
|---|---|---|---|
| Fresh input tokens | `input_tokens` | `prompt_tokens` | Full input rate per MTok |
| Cache-read tokens | `cache_read_input_tokens` | `input_tokens_details.cached_tokens` | Roughly 10% of the input rate on standard models |
| Cache-write tokens | `cache_creation_input_tokens` | `input_tokens_details.cache_write_tokens` | Above the input rate: 1.25x for a 5-minute write, 2x for 1 hour |
| Output tokens | `output_tokens` | `completion_tokens` | Full output rate per MTok, typically 3-5x input |
| Reasoning tokens | included in output | `completion_tokens_details.reasoning_tokens` | Billed as output |
| Dollars | not reported | not reported | Computed by you |

The practical consequence: any meter that does not break out cached input cannot tell you where the money went. Cache-read tokens bill at roughly 10% of the normal input rate, so the cached slice of a long session costs about a tenth of what the same tokens would cost fresh. Collapse cache-read into "input tokens" and you overstate that slice by up to 10x on exactly the workloads — long agent runs — where spend matters most.

There is also a boundary question hiding in the table. An agent run is not one request. A single task can issue 30 model calls across planning, tool use, retries, and synthesis. If your meter increments once per request and never aggregates upward, you will never be able to answer the only question finance asks: what did this task cost?

## Where the Numbers Come From: Provider Payloads, Agent SDKs, and Admin APIs

There are three places to read usage, in increasing order of usefulness.

**1. The provider's per-response `usage` object — the ground truth.** Every response from Anthropic and OpenAI carries token counts. This is the only authoritative source and it is free. Never estimate tokens with a character heuristic or a locally loaded tokenizer; you will be wrong by a margin large enough to make the meter useless, and you will be wrong precisely on the inputs that dominate your bill (tool output, JSON, code).

**2. The agent framework's run-level aggregation.** The OpenAI Agents SDK tracks usage automatically for every run and exposes it at `result.context_wrapper.usage`, with `requests`, `input_tokens`, `output_tokens`, `total_tokens`, a per-request `request_usage_entries` breakdown, and detail fields for `cached_tokens`, `cache_write_tokens`, and `reasoning_tokens`. Crucially, that aggregation covers every model call the run made, including calls that produced tool calls or handoffs — the run is the natural metering boundary. Two details trip people up. First, streaming Chat Completions providers return no usage unless you explicitly set `ModelSettings(include_usage=True)`, so a streaming-based meter silently logs zeros. Second, with a session, each `Runner.run(...)` reports usage for that run only, but prior messages are re-fed as input, so input token counts compound turn over turn even though the per-call view looks flat. `RunResult.to_state()` snapshots accumulated usage so a resumed run continues from those totals; nested `Agent.as_tool()` runs are the deliberate exception, rolling their post-resume usage up into the outer run.

**3. Provider administrative usage APIs — for reconciliation, not for metering.** Anthropic's Usage & Cost Admin API reports usage with `bucket_width` of `1d`, `1h`, or `1m` (default limits 7, 24, and 60 buckets; maximums 31, 168, and 1,440), grouped by model, `workspace_id`, `api_key_id`, `inference_geo`, and `speed` (the last requiring the fast-mode beta header), with a separate `/v1/organizations/cost_report` endpoint that returns USD cents grouped by workspace or description at daily granularity only. Data typically appears within about five minutes. This is the right tool for a monthly invoice reconciliation and the wrong tool for a per-agent cost dashboard: it is minutes-late, coarse, and has no idea which of your agents caused the spend.

The three-tier framing worth internalizing: the vendor dashboard is a daily aggregate with no attribution, the agent's own counter is real-time but unattributed, and logging the per-call `usage` field **with a label** is the actual meter. Only the third can answer "which feature, which customer, which tool call caused this."

## The OpenTelemetry GenAI Contract: gen_ai.* Attributes and Counters

You do not want dashboards built around each provider's raw field names, because `prompt_tokens` and `input_tokens` and whatever Gemini calls it next year will keep diverging. The vendor-neutral schema is the OpenTelemetry GenAI semantic conventions, and the honest framing is that the *shape* is right while the *status* is still provisional.

On 12 June 2026, in semantic-conventions v1.42.0, the GenAI conventions moved out of the core repository into the dedicated `open-telemetry/semantic-conventions-genai` repository so the area could iterate faster than the core stability bar allows. As of October 2026 every `gen_ai.*` definition is still Development status; only inherited attributes like `error.type`, `server.address`, and `server.port` are Stable. Attribute names can therefore be renamed without a deprecation window. Pin the conventions version your dashboards assume.

A reference request-level event looks like this:

| Attribute | Purpose |
|---|---|
| `gen_ai.operation.name` | Which operation: chat, embeddings, invoke_agent, execute_tool |
| `gen_ai.request.model` | Model requested |
| `gen_ai.response.model` | Model actually served (differs on routing/fallback) |
| `gen_ai.usage.input_tokens` | Fresh input tokens |
| `gen_ai.usage.cache_read_input_tokens` | Cache-read tokens |
| `gen_ai.usage.output_tokens` | Output tokens |
| `gen_ai.response.finish_reasons` | Why generation stopped (truncation shows up here) |
| `llm.request_cost_usd` | Custom: dollars computed at log time |
| `llm.pricing_version` | Custom: which price table produced that number |

Two conventions are easy to get wrong. First, the spec deliberately does not define dollar cost. Compute it yourself from token counts and a price table you version alongside the standard usage fields — otherwise a provider price change silently rewrites the meaning of your historical data. Second, give every agent a unique `gen_ai.agent.name`; omit it and the span shows as `Unknown`, which destroys attribution. Sub-agents need their own distinct names rather than inheriting the parent's, and the *caller* should emit the `invoke_agent` span rather than the agent being called, so each agent's work and token spend stay separated in the trace.

The token counters themselves carry a required `gen_ai.token.modality` attribute (`text`, `image`, `audio`, `unknown`), so summing across modality equals the total even for providers that report no breakdown. The spec is also opinionated about truthfulness in a way most homegrown meters are not: when a system reports both used and billable tokens, instrumentation **must** report billable tokens, and instrumentation that cannot obtain token counts efficiently **must not** report usage metrics at all. That second rule exists because a fabricated number is worse than a missing one.

## Why Two Instrument Families Exist — and the p95 Trap

OpenTelemetry splits token metering into two instrument families, and conflating them produces quietly wrong dashboards.

**Usage counters** — `gen_ai.client.inference.usage.input_tokens` and `.output_tokens`, plus cache-read, cache-write, and reasoning subsets — are cumulative and are the only correct source for totals and cost approximation.

**Per-operation histograms** — `gen_ai.client.inference.operation.input_tokens` and `.output_tokens` — describe the distribution of a *single operation*. They must never be summed or averaged to produce a total.

Here is the trap, stated concretely. Run 100 operations that each consume 100 text tokens plus 200 image tokens. Add `gen_ai.token.modality` as a dimension on the histogram and your p95 reads **200**, because each modality series only sees its own slice. The true p95 of total tokens per operation is **300**. Nothing errors. The dashboard simply lies, and you make a capacity or caching decision on a number that is off by a third.

Recommended histogram boundaries are powers of four: per-operation token histograms use `[1, 4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216, 67108864]`; `gen_ai.invoke_agent.duration` uses boundaries from 0.1 to 409.6 seconds; `gen_ai.client.operation.duration` uses 0.01 to 81.92 seconds.

The agent-level instruments sit alongside the client-level ones: `gen_ai.invoke_agent.duration` (Histogram, unit `s`), `gen_ai.invoke_agent.inference_calls` (unit `{inference_call}`), `gen_ai.invoke_agent.tool_calls` (unit `{tool_call}`, explicitly including failed calls), `gen_ai.invoke_workflow.duration`, and `gen_ai.execute_tool.duration`. The failed-calls detail matters: retry storms are a top cause of runaway spend, and a tool-call counter that only counts successes hides them.

## From Tokens to Dollars: The Cost Formula and the Cache Multiplier

The formula is boring, which is the point:

```
cost = (fresh_input_tokens  x input_price / 1e6)
     + (cache_read_tokens   x input_price x 0.10 / 1e6)
     + (cache_write_tokens  x input_price x cache_write_multiplier / 1e6)
     + (output_tokens       x output_price / 1e6)
```

The only non-obvious multiplier is the cache-read discount: 0.10 of the input rate for most models, and lower still on the premium ones (0.025 on Fable 5.1 and Mythos 5.1, 0.05 on Opus 5.5 and Sonnet 5.5). A worked example at Sonnet 5's published rates — $2 per MTok input, $0.20 per MTok cache read, $10 per MTok output — makes the stakes clear: 18 turns, 2.4M input tokens of which 1.6M were cache reads, plus 40K output tokens. That is 0.8M fresh input × $2 + 1.6M cache reads × $0.20 + 40K output × $10, which lands at about **$2.32** for the task. Charge those same 1.6M tokens fresh instead and the session lands near $5.20. Nothing about the session changed except the cache-hit rate, and it is the difference between a cheap task and a mid-priced one.

Three implementation rules follow.

**Compute cost at log time, not in a monthly reporting job.** Pricing tables, model names, cache rules, and tool charges change quickly. A cost computed weeks later uses whatever price table exists then, not the one that applied when the tokens were spent. Store `llm.request_cost_usd` next to the raw token counts and stamp it with `llm.pricing_version`.

**Version the price table separately from the conventions.** These drift on different schedules. A spec bump that renames an attribute must not silently rewrite historical cost, and a price change must not invalidate your dashboards' schema assumptions.

**Handle the models that cannot be inferred.** Cost inference works by matching the model name to a definition holding a price per usage type and multiplying by the observation's usage — this is how Langfuse's infer-then-ingest path works, preferring an ingested cost from the response when one is present. But reasoning models such as the OpenAI o1 family cannot have cost inferred at all without token counts, so ingested usage is required. In Langfuse, only generation and embedding observations carry usage or cost; other observation types do not, and usage keys must match the model definition's keys exactly or the multiplication silently no-ops.

## Choosing Your Metering Boundary: Call, Run, Session, or Customer

The metering boundary determines what you can actually bill or optimize, and it is a design decision you make *before* picking a tool.

| Boundary | Question it answers | Typical use |
|---|---|---|
| Per model call | Is this prompt/tool call expensive? | Prompt and context optimization |
| Per agent run | What did this task cost? | Feature and workflow costing |
| Per session | What did this conversation cost? | Support economics, session caps |
| Per customer or key | What do I invoice? | Usage-based billing, entitlements |
| Per agent identity | Which agent is burning budget? | Multi-agent fleet governance |

A meter built only at the call level answers the first question and structurally cannot answer the others. A meter built only at the customer level tells you a number moved without telling you which agent moved it. The OpenAI Agents SDK's choice to aggregate at the run boundary is a good default because a run maps to a unit of work a human can reason about — but you still need a stable identifier threaded through the run (task id, ticket id, feature flag) to roll runs up into a customer view. LiteLLM takes the complementary approach: `spend_logs_metadata` can be attached per key, team, or request tag, so attribution travels with the request rather than being reconstructed afterward.

## Attributing Spend to What Caused It

A total is alarming; a breakdown is actionable. Four cost drivers account for most agent spend, and each needs its own label.

**File reads.** Re-reading the same large file across turns is pure replay cost. Label these calls and a single bad tool-loop pattern becomes visible.

**Unfiltered tool output.** A shell command or API response that dumps 100K tokens into context is paid for on every subsequent turn of the session, not once. This is the single largest source of accidental spend in coding agents.

**The MCP manifest.** Every connected MCP server contributes tool definitions to the context on every turn — a constant per-turn tax independent of the task. Fifteen servers with verbose schemas can add thousands of input tokens per turn whether or not a single one of those tools is called. This is the most under-instrumented line item in agent cost tracking, because it never appears as a dramatic spike; it appears as a slightly-too-high baseline forever.

**Transcript replay.** In a sessioned agent, prior messages are re-fed as input on each run, so input tokens compound. The per-call view hides this; a session-level view exposes it immediately.

Tagging each call with a category converts "our agent costs $4,000 a month" into "40% of spend is transcript replay, 25% is one unfiltered log dump." Only the second sentence produces an engineering ticket.

## Turning the Meter into a Control: Budgets, Resets, and Kill Switches

Cost tracking without an enforcement edge is observability theatre. The same meter that produces the dashboard should feed a limit.

LiteLLM is the clearest reference implementation: `max_budget` and `budget_duration` are set per key, user, or team, with `budget_reset_at` defining the replenishment cycle, so enforcement lives next to the meter rather than in a separate reporting job. Provider-specific pricing is applied automatically when the response carries tier metadata (Vertex AI PayGo and priority pricing, Bedrock service tiers, Azure base-model mapping). The maintenance requirement is explicit: model pricing data has to be kept in sync from the upstream repository or reported costs diverge from the provider bill.

Three enforcement patterns are worth having, in escalating severity:

1. **Soft alert** — a threshold on cost per feature or cost per workspace that pages a human. Cheap, catches drift.
2. **Hard cap** — a budget keyed to a customer, team, or agent identity that refuses new requests when exceeded. This is what converts a runaway retry loop into an error message instead of an invoice.
3. **Circuit breaker** — a per-run ceiling that aborts the run itself. An agent stuck in a tool loop is metered and stopped before turn 40 rather than after.

OpenMeter approaches the same problem from the billing side: it meters LLM tokens with a CloudEvents event (type `prompt`, with token counts in `data.tokens` and `subject` set to the customer), aggregated `SUM` with `groupBy` over provider, model, and type. It is Apache-2.0, and its production users include Trigger.dev and Requestly — but self-hosting means running PostgreSQL, ClickHouse, Kafka, and the API server as four separate components, which is a real operational commitment for a company that has not already standardized on event-driven metering.

## The Tool Landscape: What Each Layer Actually Does

| Tool | Layer | What it gives you | Licensing / scale (Oct 2026) |
|---|---|---|---|
| LiteLLM | Proxy / gateway | Spend tracking for 100+ LLMs, per key/user/team budgets, daily spend breakdown API | 59,970 GitHub stars, actively pushed |
| Langfuse | Observability | Usage details and cost details per generation, infer-then-ingest pricing, metrics API | 35,256 stars |
| MLflow | Experiment + tracking | Run-level metrics including token counts and cost | 28,207 stars, Apache-2.0 |
| OpenLLMetry (Traceloop) | Instrumentation | OTel-native auto-instrumentation that emits GenAI spans | 7,463 stars, Apache-2.0 |
| Helicone | Gateway / observability | Request-level cost and usage with caching | 6,190 stars, Apache-2.0 |
| OpenLIT | Instrumentation | OTel-native LLM instrumentation | 2,809 stars, Apache-2.0 |
| OpenMeter | Metering / billing | Token metering as billable events, entitlements, credit balances | 2,356 stars, Apache-2.0 |
| OTel GenAI semconv | Standard | The `gen_ai.*` schema itself | 401 stars, Development status |

Read that last row carefully. The most important artifact in this table — the thing everything else is converging on — is the smallest repository in it. The metering primitives (proxies, SDKs, instrumentation libraries) are mature and commercially backed; the *standard* is young and explicitly provisional. That asymmetry is the defining risk of building a cost meter in 2026: your tooling will outlive the attribute names it currently emits.

The practical hedge is to keep raw provider token counts and a price table in your own store, in addition to whatever the vendor records. If `gen_ai.*` names change — and they can, without a deprecation window — you can re-derive your history from first principles instead of losing it.

## Building a Minimal Meter Today: Log, Tag, Roll Up

You do not need to adopt a platform to start metering. The minimum viable meter is roughly forty lines of code.

**Step 1 — Log the usage object on every response.** Capture the raw provider payload, unmodified, before any normalization. Include the model actually served, not just the model requested.

**Step 2 — Attach business metadata at the same moment.** Task or ticket id, feature name, customer or workspace id, agent name, sub-agent name if any, environment. This is the step teams skip and then regret, because metadata cannot be retroactively recovered.

**Step 3 — Compute cost immediately** using a price table stored in the repository under version control, and write `cost_usd` and `pricing_version` into the same record. Never recompute later.

**Step 4 — Roll up on read, at whatever boundary the question needs.** Request-level records are the atomic fact; run, session, feature, and customer views are aggregations over them. Doing it this way means adding a new dashboard dimension later requires no new instrumentation.

**Step 5 — Reconcile monthly.** Compare your rolled-up totals against the provider's admin usage and cost endpoints, or the invoice itself. A meter that has never been reconciled is a meter that might be wrong in a way nobody has noticed. Discrepancies usually trace to one of four things: a model routing fallback you did not log, cache-write tokens omitted from the formula, a price table that was not updated, or tokens served by a provider path your instrumentation does not wrap.

## Dashboards and Alerts That Earn Their Keep

Most token dashboards get abandoned because they show a total that goes up. Five panels actually drive decisions.

**Cost per feature or per workflow.** The only number product owners can act on. If "document summarization" costs 12x "chat," that is a roadmap input.

**Tokens per request and per session, as distributions, not averages.** The most useful panel is outlier requests. A single runaway request, a huge context window, or a retry loop distorts daily spend, and an average hides exactly that. Alert on tokens per request, tokens per session, cost per feature, and cost per workspace.

**Cache-hit rate, next to spend.** This is the highest-leverage dial most teams never touch. Since cache reads bill around 10% of the input rate, a cache-hit-rate improvement of 30 points is worth more than most prompt-engineering projects — and it is measurable.

**MCP manifest overhead per turn.** A flat line that you can actually shrink by disconnecting unused servers. It is the rare cost driver that is both boring and easy to fix.

**Reconciliation delta.** Your computed total minus the provider's. Trend it monthly; a growing delta means your price table or your instrumentation has drifted.

For engineering, request-level outliers and latency correlation come from the same events. For finance, an immutable per-period aggregate that reconciles to the invoice comes from the same events. Emit request-level telemetry once and roll it up for both audiences rather than maintaining a monthly spreadsheet.

## Common Mistakes

**Counting output tokens and ignoring input.** Output is the smaller number in almost every agent workload. Input, inflated by transcript replay, typically dominates.

**Ignoring cache entirely.** Either direction is wrong: treating cache reads as full-price input overstates the cached tokens by up to 10x, and treating cached tokens as free understates it.

**Estimating with a local tokenizer or a character heuristic.** The count will be wrong, and wrong most severely on exactly the dense content (tool output, code, JSON) that drives agent cost. The provider already gives you the number for free.

**Measuring one call instead of the whole run.** A single prompt looks cheap; the 34-call run around it is the actual cost unit.

**Assuming streaming responses report usage.** They do not by default on Chat Completions providers; you need an explicit usage flag, and without it your meter logs zeros with no error.

**Summing a histogram.** Per-operation token histograms with a breakdown dimension produce a p95 that is lower than reality — 200 instead of 300 in the worked example — with no warning.

**Putting every sub-agent under the parent's name.** Attribution collapses and you cannot tell which agent in a fleet is the expensive one.

**Never reconciling against the invoice.** Silent drift in a price table or a routing fallback is invisible until someone compares totals. Do it monthly.

## What Changes Next

Three things are moving, and each has a defensive posture.

**The conventions will be renamed.** `gen_ai.*` moved to its own repository in June 2026 and every GenAI attribute remains Development status, so renames can happen without a deprecation window. Keep raw token counts and your own price table so a spec change cannot orphan your history.

**Agent-level instruments are filling in.** The instrumentation is shifting from "client call" to "agent invocation," with `invoke_agent`, `invoke_workflow`, and `execute_tool` instruments joining the client-level ones. Cost dashboards built purely on client-side request counts will need to be re-scoped as this lands.

**Pricing drift is permanent.** Cache multipliers, tiered pricing, and reasoning-token accounting all change faster than quarterly. Version your price table, stamp every cost record with that version, and reconcile against the invoice. Everything else in a cost meter can be approximately right; the price table cannot.

The teams that get this right in 2026 are not the ones with the most sophisticated dashboards. They are the ones who logged the usage object with a label on day one, kept four numbers separate, computed cost at write time, and pointed a budget limit at the same meter. None of those steps require buying anything.

## FAQ

**What is an agent token usage meter?**

It is the component that captures the provider's `usage` object on every model response made by an agent, keeps input, output, cache-read, and cache-write tokens as separate fields, attaches business labels (task, feature, customer, agent name), and converts the counts into dollars at log time using a versioned price table. The distinguishing feature versus generic token counting is that it meters an agent *run* — dozens of model calls — rather than a single request.

**Why can't I just read my provider dashboard for agent costs?**

Provider dashboards report daily aggregates with no attribution to which agent or feature caused the spend, and administrative usage APIs are minutes-late and coarse (Anthropic's, for example, defaults to 7 daily buckets and offers daily granularity on the cost report). They are excellent for reconciling a monthly invoice and structurally incapable of telling you that one sub-agent's retry loop cost $300 yesterday. Only per-call logging with labels answers that.

**How much does prompt caching actually save on agent workloads?**

Cache-read tokens bill at roughly 10% of the normal input rate, so the tokens that hit cache cost about a tenth of what they would fresh. Worked at Sonnet 5's published rates, 18 turns with 2.4M input tokens (1.6M of them cache reads) plus 40K output tokens comes to about $2.32 for the task, against roughly $5.20 if that same input were charged fresh. This is why cache-hit rate belongs on the cost dashboard next to spend, not in a separate caching doc.

**Should I use OpenTelemetry gen_ai.* attributes or my provider's raw field names?**

Use `gen_ai.*` as your dashboard schema so you are not rewriting queries when you add a provider, and persist the raw provider payload alongside it so you can re-derive history if attribute names change. Be aware that every `gen_ai.*` attribute is still Development status as of October 2026 and can be renamed without a deprecation window. Also note the spec intentionally does not define dollar cost — you compute that yourself and version the price table that produced it.

**Where should I put the enforcement limit?**

At the same layer as the meter, and at the boundary that matters to you. Per-key or per-team `max_budget` with a `budget_duration` and `budget_reset_at` (as LiteLLM implements it) converts a runaway loop into a refused request; a per-run ceiling aborts the run itself. A meter with no enforcement edge only tells you, after the fact, how expensive the outage was.

## Sources

- Anthropic, Usage and Cost Admin API (bucket widths, default and maximum limits, group-by dimensions, cost report granularity, ~5 minute freshness) — https://docs.claude.com/en/api/usage-cost-api
- Anthropic, Prompt caching (cache pricing table, 0.10x cache-read multiplier and per-model exceptions, 1.25x 5-minute and 2x 1-hour write premiums, `cache_read_input_tokens` / `cache_creation_input_tokens`) — https://docs.claude.com/en/docs/build-with-claude/prompt-caching
- OpenAI, Prompt caching (cache-read discount, `input_tokens_details.cached_tokens` and `input_tokens_details.cache_write_tokens`) — https://platform.openai.com/docs/guides/prompt-caching
- OpenAI Agents SDK, Usage (`result.context_wrapper.usage`, `request_usage_entries`, `ModelSettings(include_usage=True)`, `RunResult.to_state()`, nested `Agent.as_tool()` roll-up) — https://openai.github.io/openai-agents-python/usage/
- OpenTelemetry GenAI semantic conventions, inference token metrics (`gen_ai.client.inference.usage.*` counters vs per-operation histograms, `gen_ai.token.modality`, billable-token rule, powers-of-four boundaries) — https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-token-metrics.md
- OpenTelemetry GenAI semantic conventions, agent and tool metrics (`gen_ai.invoke_agent.*`, `gen_ai.invoke_workflow.duration`, `gen_ai.execute_tool.duration`, boundaries) — https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md
- OpenTelemetry semantic-conventions CHANGELOG v1.42.0 (12 June 2026: GenAI conventions moved to the dedicated repository) — https://github.com/open-telemetry/semantic-conventions/blob/main/CHANGELOG.md
- LiteLLM, Cost tracking (`max_budget` / `budget_duration`, provider tier pricing applied automatically, model cost map kept in sync from GitHub) — https://docs.litellm.ai/docs/proxy/cost_tracking
- LiteLLM, Virtual keys and budgets (`budget_reset_at` per key, user or team) — https://docs.litellm.ai/docs/proxy/users
- Langfuse, Token and cost tracking (infer-then-ingest order, price per usage type, o1 reasoning models needing ingested tokens, generation/embedding-only cost) — https://langfuse.com/docs/observability/features/token-and-cost-tracking
- OpenMeter, documentation (CloudEvents usage events, `SUM` aggregation, groupBy, Apache-2.0, four-component self-host) — https://openmeter.io/docs
- Repository and licence checks by the reviewer on 2026-10-07 — https://github.com/BerriAI/litellm ; https://github.com/langfuse/langfuse ; https://github.com/mlflow/mlflow ; https://github.com/traceloop/openllmetry ; https://github.com/Helicone/helicone ; https://github.com/openlit/openlit ; https://github.com/openmeterio/openmeter ; https://github.com/open-telemetry/semantic-conventions-genai
