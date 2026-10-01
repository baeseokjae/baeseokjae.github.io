---
title: "Frugal Tokens Review 2026: Coding Agent Cost Tracking Compared"
date: 2026-09-30T15:32:01+00:00
tags:
  - coding agent cost tracking
  - token usage dashboard
  - cache miss cost
  - ccusage alternative
  - local first AI agent observability
description: "Frugal Tokens prices coding agent cache misses in dollars, not just token totals. Review, comparison, and verdict for 2026 fleets."
draft: false
cover:
  image: "/images/frugal-tokens-coding-agent-cost-tracking.png"
  alt: "Frugal Tokens Review 2026: Coding Agent Cost Tracking Compared"
  relative: false
schema: "schema-frugal-tokens-coding-agent-cost-tracking"
---

Frugal Tokens is a local, read-only Deno dashboard that reads the session transcripts Claude Code, Codex, OpenCode, PI, and Cursor already write to disk, then reports spend, estimated working time, and — its differentiator — the type and dollar cost of every prompt-cache miss. It answers why a bill grew, not just how large it was.

That distinction is the whole reason this tool deserves a closer look than its 25 GitHub stars suggest. Coding agent cost tracking in 2026 has become a solved collection problem and an unsolved interpretation problem: every serious tool parses the same local JSONL files, so the only thing left to compete on is what you do with them. Frugal Tokens bets on cache economics. This review tests whether that bet is worth running.

## What Frugal Tokens Actually Is, And What It Refuses To Be

Frugal Tokens is a self-hosted web dashboard for exploring the cost and usage history of coding agent sessions. You clone the repository, install Deno, copy `.env.example` to `.env`, run `deno task build && deno task start`, and open `http://localhost:9000`. There is no account, no sign-up, no hosted sync, and no telemetry egress. The optional demo at demo.frugaltokens.com exists purely so you can see the interface before you commit to running it.

What it refuses to be is more revealing. It is not an agent harness, not a proxy, and not a gatekeeper — it never sits in the request path and cannot block a runaway session. It does not rewrite your prompts, route your models, or enforce budgets. It is a read-only lens pointed at data that already exists on your disk, plus a SQLite database that caches its own parse so repeat visits are fast.

The repository itself was created on 2026-07-10 and last pushed on 2026-09-28, with 25 stars and 5 forks. It ships **without a license file**, which matters more than the star count for anyone considering it against corporate session data. The launch discussion — a Show HN post from late August 2026 that reached 37 points and 10 comments — is where the author's intent is clearest: he built it because he was "curious to see how much all of my sessions cost and how much cache misses affected that spend," and noticed that people with apparently similar workflows had wildly different spend profiles.

That is the thesis in one sentence. Most cost tooling answers "how much did this cost." Frugal Tokens tries to answer "what in my workflow is making it cost this much."

## Why Agent Spend Is a Context Lifecycle Problem, Not a Price Problem

If you are shopping for a cheaper model per million tokens, you are optimizing the wrong variable. Frontier coding agents are not dominated by the tokens you type or even the tokens the model writes. They are dominated by the conversation history that gets replayed and re-read on every single turn.

The clearest public evidence is Augment Code's head-to-head benchmark of its Auggie CLI against Claude Code on the identical frontier model, Opus 4.7. On Terminal Bench 2.0, the two harnesses landed within 1.1 percentage points on pass rate (67.4% versus 66.3% — inside run-to-run variance), yet the token and dollar profiles were nothing alike. Auggie completed the benchmark on 32% fewer total tokens for 33% less money. On the harder SWE-Bench Pro, the gap held at 30% fewer tokens and 23% lower cost, with a slightly better pass rate.

Both of those runs are vendor self-reported by Augment, so treat the specific percentages as directional rather than independently confirmed. What is hard to hand-wave away is the *composition* of the spend. In both harnesses, cache-read tokens were 93% of all tokens consumed:

- Auggie on Terminal Bench 2.0: 341,980,440 cache-read tokens out of 367,587,892 total.
- Claude Code on Terminal Bench 2.0: 506,455,124 cache-read tokens out of 543,090,485 total.

Cache writes, by contrast, were under 5% of total volume in both runs, and output tokens were around 2%. This is the single most useful number in the entire cost-tracking category: **output tokens are not your bill.** Input-side context handling is your bill, and 93% of it is the same prefix being read back over and over again. Which is why a tool that only reports totals — total tokens, total cost, maybe a per-model split — is structurally incapable of telling you anything actionable. That is exactly the complaint that opens the long-running Ask HN thread on keeping coding agents from burning money: "the worse thing for me is that everything shows up as aggregate usage."

## How Frugal Tokens Works: Local Transcripts, Deno, and One Command

The architecture is deliberately boring, and that is a compliment. Coding agents already write structured session logs to disk as they run — JSONL files under `.claude`, Codex, OpenCode, PI, and Cursor session directories. Frugal Tokens watches those directories, detects changes, imports new records into a local SQLite database, and serves a web UI on top of it.

Setup is four steps:

1. Install Deno 2.9 or newer (`curl -fsSL https://deno.land/install.sh | sh` on macOS or Linux).
2. `cp .env.example .env`.
3. `deno task build && deno task start`.
4. Open `http://localhost:9000`.

Path overrides live in `.env`, so pointing it at a non-standard session directory is a configuration edit rather than a code change. The `PORT` variable controls the API port, and the README notes explicitly not to rename it because managed hosts auto-inject that variable. For development, `deno task dev` serves on a separate port with client and server hot reload.

What you get once it is running: an overview of total usage and spend, estimated working time and overlapping-session detection, spend broken down by model and by cache-miss category, session-level metrics with percentile breakdowns, a session list, and a session explorer that drills into individual model calls with their tool inputs and outputs. There is also a "jump to the cache miss" affordance that positions the timeline at the exact request where caching broke down — a small feature that turns a 200-row log into a single scroll.

The cost-comparison view is the sleeper feature. It re-prices a *recorded* session under another model's rates, and for Anthropic models it will price the same session under both 5-minute and 1-hour cache durations. That converts "should we switch models" from a guess into a calculation against your own real traffic instead of a synthetic benchmark.

## The Feature That Matters: Classifying Cache Misses and Pricing Them

Prompt caching is not free, and it is not free in two different ways that most dashboards conflate. The multipliers, per Anthropic's published pricing, are:

| Cache operation | Multiplier vs base input | Validity |
|---|---|---|
| 5-minute cache write | 1.25x base input price | 5 minutes |
| 1-hour cache write | 2x base input price | 1 hour |
| Cache read (hit) | 0.1x base input price | Same as the preceding write |

Two consequences follow directly. First, caching pays off after **one** read at the 5-minute duration, but only after **two** reads at the 1-hour duration — the 1-hour write costs twice as much up front, so a single hit does not break even. Second, cache-hit pricing is model-dependent in a way that breaks the "10%" rule of thumb: Anthropic documents a 0.025x multiplier on Claude Fable 5.1 and Claude Mythos 5.1 ($0.25 per million tokens) and 0.05x on Claude Opus 5.5 ($0.20 per million tokens).

Now consider what happens when the cache expires between two turns. The entire prefix is re-billed as a *write* rather than a read — at 1.25x or 2x base input price instead of 0.1x. That is a 12.5x to 20x step change in the cost of the same tokens, and it is invisible in any report that shows one input-token total. The author's own anecdote makes the magnitude concrete: using Fable at work, a single TTL miss after replying roughly ninety minutes after the previous message cost **$6 for one message**. One turn. Because a timer expired.

Frugal Tokens classifies misses into types — TTL expiry from an idle gap, first-write on a cold session, and truncation-driven misses where context was dropped and had to be re-established — and prices each category. That classification is what makes the output actionable, because each category has a different fix. TTL misses are a workflow problem (you stepped away; the fix is shorter sessions, or a 1-hour cache duration if you know you will return). Truncation misses are a context-management problem (too much history is being replayed; the fix is compaction, smaller threads, or artifact-based handoff between agents). First-write cost is a session-design problem.

A total spend number cannot distinguish those three. A dashboard that says "you spent $140 this week" cannot tell you that $40 of it happened in ninety-minute gaps where you left the terminal open. That is the entire value proposition, and it is a real one.

## Coding Agent Cost Tracking Compared: ccusage, AgentsView, and the Long Tail

The category is now sharply stratified. Live figures pulled from the GitHub API on 2026-09-30:

| Tool | Stars | License | Last push | Agent coverage | Primary differentiator |
|---|---|---|---|---|---|
| [ccusage](https://github.com/ccusage/ccusage) | 18,811 | NOASSERTION | 2026-09-30 | 18 named sources | CLI-first, broadest harness list, statusline + billing-window blocks |
| [AgentsView](https://agentsview.io/) | 6,032 | MIT | 2026-09-30 | 60+ formats | Searchable SQLite archive of record, activity/concurrency analytics |
| [Frugal Tokens](https://github.com/dpclark4/frugal-tokens) | 25 | None | 2026-09-28 | 5 harnesses | Cache-miss classification priced in dollars |
| [Agentic Metric](https://github.com/MrQianjinsi/agentic-metric) | 200 | MIT | 2026-03-09 | n/a | Local monitoring; dormant since March |
| [Vigilo](https://github.com/Idan3011/vigilo) | 4 | MIT | 2026-02-25 | Claude Code, Cursor | Rust audit trail with an MCP surface; dormant |

ccusage is the incumbent by adoption, and its breadth is genuine rather than marketing: its README documents focused subcommands for Claude Code, Codex, OpenCode, Amp, Droid, Codebuff, Hermes Agent, pi-agent, Goose, OpenClaw, Kilo, Kimi, Qwen, GitHub Copilot CLI, Gemini CLI, Antigravity, Grok Build CLI, and ZCode — eighteen named sources, runnable through `npx`, `bunx`, or Nix. It reports by day, week, month, and session, understands Claude Code's 5-hour billing windows, ships a statusline hook, and emits JSON for automation. If your requirement is "track spend across every agent on the team and pipe it into CI," ccusage is the default answer and the burden of proof is on anything claiming otherwise.

AgentsView occupies a different niche it has largely built for itself: an archive of record. It parses more than 60 agent formats into SQLite (with optional PostgreSQL, DuckDB, or ClickHouse backends), then layers an activity dashboard on top — peak concurrency and when it happened, active versus idle time, agent-minutes across parallel sessions, and cost, filterable by project, agent, and machine. It tracks LiteLLM and OpenRouter pricing with an offline fallback and does cache-aware accounting for prompt-cache creation and reads. It is a single Go binary under MIT, with desktop, web, CLI, REST, and MCP surfaces.

Note what that last point means for Frugal Tokens' differentiation. In the launch thread, the AgentsView maintainer responded to the cache-angle claim directly with screenshots showing cached versus uncached tokens. AgentsView entered the cache-visibility lane too. Frugal Tokens is not competing against tools that ignore caching; it is competing against tools that surface cached/uncached splits and arguing that *classification of miss causes* is a further step. That argument is defensible — an uncached-token count still does not tell you whether the miss was TTL expiry or truncation — but the moat is narrower than the README implies.

Below that line, the long tail is a graveyard. Vigilo (Rust, MIT) frames the problem as audit rather than optimization and has 4 stars with no push since 2026-02-25. Agentic Metric (Python, MIT) has 200 stars and has been dormant since 2026-03-09. Both converge on the same local-transcript-parse architecture as everyone else; neither reached adoption. The practical lesson for anyone evaluating this space: check the last-push date before the feature list, because a dashboard you cannot trust to parse next month's transcript format is worth nothing regardless of its UI.

## Same Model, Different Harness: What the Benchmark Gap Means for Budgets

Returning to the Augment figures with the vendor caveat firmly attached, here is the comparison in full:

| Metric (Opus 4.7) | Auggie CLI | Claude Code | Delta |
|---|---|---|---|
| Terminal Bench 2.0 pass rate | 67.4% | 66.3% | +1.1 pt |
| Terminal Bench 2.0 total tokens | 367,587,892 | 543,090,485 | −32% |
| Terminal Bench 2.0 output tokens | 7,217,279 | 11,381,425 | −37% |
| Terminal Bench 2.0 cache reads | 341,980,440 | 506,455,124 | −32% |
| Terminal Bench 2.0 cache writes | 17,960,193 | 25,219,909 | −29% |
| Terminal Bench 2.0 total cost | $463.04 | $694.50 | −33% |
| SWE-Bench Pro total tokens | 1,651,716,301 | 2,349,143,356 | −30% |
| SWE-Bench Pro cache reads | 1,582,841,271 | 2,269,905,161 | −30% |
| SWE-Bench Pro cache writes | 52,849,663 | 63,777,293 | −17% |
| SWE-Bench Pro total cost | $1,448.63 | $1,869.97 | −23% |

The important structural reading is that *output* tokens moved the most on Terminal Bench 2.0 (−37%) but accounted for only about 2% of volume, so their reduction could not have driven the cost delta on its own. The cost delta tracks the input side: 30–32% fewer cache reads and 17–29% fewer cache writes. The vendor's own explanation is retrieval quality — a sharper context engine means the agent re-explores less and replays a smaller history each turn.

Independent of whether Auggie is actually better, the benchmark establishes the shape of the problem: **harness and retrieval quality move cost by roughly a third, while model choice moves the per-token rate.** Choosing between frontier models changes the multiplier on the same volume. Fixing your context lifecycle changes the volume. Practitioners in the cost-control threads converge on exactly that set of levers — model routing for cheap steps, fresh atomic context threads instead of one week-long session, compaction through a cheaper model, sub-agent briefs handed over as artifacts rather than replayed conversation, and hard iteration and retry caps.

That last lever is worth naming precisely because visibility does not supply it. The original poster in the Ask HN thread had already built per-call cost attribution and limits, and still reported the underlying failure mode as "agents retrying when they shouldn't." A dashboard is diagnostic, not therapeutic. A tool that shows you the cache miss cannot stop the retry loop that caused it — that takes a budget cap or a circuit breaker in the execution path.

## Claude Code OpenTelemetry Is Absorbing the Enterprise Use Case

The most consequential trend in this category is not a new entrant; it is first-party instrumentation. Claude Code now exports cost and token telemetry natively over OpenTelemetry:

- `claude_code.cost.usage` — cost of the session in USD
- `claude_code.token.usage` — tokens used
- plus `claude_code.session.count`, `claude_code.lines_of_code.count`, `claude_code.commit.count`, and `claude_code.pull_request.count`

Enable it with `CLAUDE_CODE_ENABLE_TELEMETRY=1` and an OTLP exporter. Metrics can be broken down by input/output type, user, team, model, `skill.name`, `plugin.name`, and `agent.name`, which means an organization can attribute spend to a specific skill, plugin, or subagent type without any third-party scraper touching a transcript file. Anthropic notes plainly that the cost metrics are approximations and that official billing lives with the API provider — the same caveat that applies to every local parser, stated honestly by the vendor itself.

Two details from that documentation matter for anyone designing a cost-tracking strategy around it. First, Claude Code **deliberately ignores** OpenTelemetry exporter variables set in a repository's `.claude/settings.json` or `.claude/settings.local.json`, so a checked-out repository cannot turn telemetry on, redirect it to an attacker-controlled collector, or capture spend data. Administrators configure it through managed settings, shell environment, or `~/.claude/settings.json`. Second, distributed traces are available in beta with span hierarchy, and `OTEL_LOG_RAW_API_BODIES` will emit full API request and response bodies — which include the entire conversation history, and which Anthropic documents as implying consent to everything the prompt and tool-content gates would otherwise protect.

The strategic implication is straightforward. For fleet-level spend reporting, the enterprise buyer has a first-party path that requires no per-developer installation, no local parser maintenance, and no license ambiguity. Third-party CLIs are not being displaced by a competitor; they are being partially absorbed by the platform. What remains for third-party tools is the developer-local case: cross-harness comparison in an organization that runs Claude Code, Codex, Cursor, and OpenCode side by side, where no single vendor's telemetry covers the whole fleet.

| Concern | Native Claude Code OTel | Local transcript parsers |
|---|---|---|
| Setup | Managed settings or shell env | Per-developer clone and run |
| Coverage | Claude Code only | Whatever harnesses are parsed |
| Cross-harness comparison | Not possible | Core strength |
| Cost attribution | By user, team, model, skill, plugin, agent | By session, model, cache category |
| Cache-miss *cause* | Not classified | Frugal Tokens' differentiator |
| License / trust surface | First-party docs | Depends on repo (Frugal Tokens: none) |

## Where Frugal Tokens Falls Short

Four weaknesses, in order of how much they should affect a decision.

**No license file.** The repository has no `LICENSE` at all, while ccusage is NOASSERTION-labeled and both AgentsView and the dormant entrants are MIT. For a tool that reads transcripts containing proprietary source code, tool outputs, and file contents, "no license" means no explicit grant of rights to use, modify, or redistribute — a genuine blocker for corporate legal review, and a strange omission for a project whose entire pitch is local-first trust. This is the single cheapest thing the author could fix and the highest-impact.

**The smallest audience of any credible entrant.** 25 stars against 18,811 and 6,032 is not just a popularity gap; it is a bus-factor and maintenance-risk gap. The formats it parses are undocumented internal file layouts that vendors change without notice. ccusage and AgentsView both pushed on 2026-09-30, the same day this review was written. A 25-star project must be assumed to break first and be fixed last when Claude Code or Codex changes a transcript schema.

**Narrow harness coverage.** Five harnesses — OpenCode, Claude Code, PI, Codex, Cursor — versus ccusage's 18 named sources and AgentsView's 60+ formats. If your team runs Copilot CLI, Gemini CLI, Amp, or Goose, Frugal Tokens reports a partial picture by construction, and a partial spend number is worse than no number because it looks complete.

**No enterprise path.** There is no hosted service, no SSO, no central aggregation across machines, and no admin policy surface. That is a coherent choice for a local-first tool, but it caps its addressable use case at the individual developer, and it means it will never be the answer to "what is the org spending."

## How To Set Up Coding Agent Cost Tracking Today

A practical sequence for a team that wants spend visibility without a six-week platform project:

1. **Establish a baseline with an installed tool.** Start with `ccusage` or AgentsView. Get a real weekly number for your actual harnesses before you optimize anything, because every subsequent change needs a before-and-after.
2. **Turn on first-party telemetry where it exists.** For Claude Code, set `CLAUDE_CODE_ENABLE_TELEMETRY=1` plus an OTLP exporter in managed settings or the developer shell, and break `claude_code.token.usage` down by `model` and `agent.name`. This is the cheapest durable fleet number you will get.
3. **Check the composition, not the total.** Confirm your own cache-read share against the 93% figure the benchmark runs showed. If your sessions look similar, stop tuning output tokens and start tuning context.
4. **Add cache-miss attribution on top.** This is where Frugal Tokens earns its place in a stack rather than replacing anything: run it locally, read the miss categories, and note how much spend lands in TTL misses after idle gaps.
5. **Fix the workflow category that dominates.** TTL misses: shorter sessions, tighter threads, and 1-hour caching where you know you will return within the hour. Truncation misses: compaction through a cheaper model and artifact handoff between agents instead of replayed history.
6. **Add a cap in the execution path.** Visibility last. A retry cap, an iteration budget, or a cost circuit breaker is what actually stops the spend; a dashboard only explains it afterward.

Steps 1 through 3 are one afternoon of work. Steps 5 and 6 are where the money actually moves.

## Verdict: Who Should Run Frugal Tokens

Frugal Tokens is the most interesting tool in a crowded category on exactly one axis, and it is an axis that matters: it is the only tracker reviewed here that treats a cache miss as a classified, priced event rather than a line in a cached/uncached split. If your agent spend is high, your session patterns include frequent idle gaps, and you have already concluded that "which model" is the wrong question, this is the tool that will show you where the money went in a way a totals dashboard cannot. The session explorer, the jump-to-cache-miss timeline, and the re-pricing comparison against your own recorded traffic are all genuinely useful, and none of them require sending your source code anywhere.

But it is not a fleet tracking solution, and it should not be the only tool you run. Run **ccusage** if you need broad harness coverage in a CLI that automates cleanly, **AgentsView** if you want a searchable archive with concurrency analytics and an MCP surface your agents can query, and **Claude Code's native OpenTelemetry** if you are an administrator who needs per-team spend attribution without deploying anything to developer machines. Layer Frugal Tokens on top for cache-miss forensics, where it has no direct equivalent.

Two caveats hold me back from a stronger recommendation. The absent license file is a real adoption blocker for corporate environments, and 25 stars is thin enough that you should budget for the possibility that it stops parsing your transcripts after an upstream format change. If those two facts change — a license file and a maintained release cadence — this becomes an easy recommendation for individual developers optimizing their own workflow. As of 2026-09-30, treat it as a high-value diagnostic companion, not the backbone of your cost tracking.

If you are building the rest of that stack, our guides on [agent token cost attribution](/posts/agent-token-cost-attribution-2026/), [AI agent observability with OpenTelemetry](/posts/ai-agent-observability-opentelemetry-2026/), and [agent cost circuit breaker patterns](/posts/agent-cost-circuit-breaker-pattern-guide-2026/) cover the attribution, telemetry, and enforcement layers that sit either side of a tool like this. For the underlying caching mechanics, see [LLM prompt caching explained](/posts/llm-prompt-caching-guide-2026/); for the budget context, [AI coding cost per developer](/posts/ai-coding-cost-per-developer-2026/); and for setup specifics on the earlier release, [Frugal Tokens per-session cost explorer](/posts/frugal-tokens-coding-agent-cost-explorer-2026/).

## Frequently Asked Questions

### Is Frugal Tokens free, and is it safe to run on work sessions?

Yes to free — there is no paid tier, no account, and no hosted component, so the running cost is a Deno runtime and a local SQLite file. Safety is more nuanced than the README suggests. The tool is read-only against your transcripts and makes no network calls to a vendor backend, which is the right architecture for data containing proprietary source code. The genuine gap is legal rather than technical: the repository ships with no license file, so there is no explicit grant of rights, which many corporate review processes treat as a blocker regardless of how the code behaves. Get that settled before pointing it at employer-owned sessions.

### Which coding agents does Frugal Tokens support?

Five, as of the 2026-09-28 push: OpenCode, Claude Code, PI, Codex, and Cursor. Session directories are configurable through `.env`, so a harness that follows the same transcript conventions may parse even if it is not named. That coverage is materially narrower than the category leaders — ccusage documents 18 named sources and AgentsView parses more than 60 formats — so if your team runs Copilot CLI, Gemini CLI, Amp, Goose, or Kimi, expect a partial spend picture rather than a complete one.

### Why did my agent bill spike after I stepped away for an hour?

Because the prompt cache expired and the next request had to re-write the entire prefix instead of reading it. Anthropic prices a cache read at 0.1x base input but a 1-hour cache write at 2x base input, so the same tokens can cost twenty times more after an idle gap. The Frugal Tokens author reports exactly this pattern costing $6 for a single message after replying roughly ninety minutes later. This is why idle gaps are a billing event, not a productivity metric — a 5-minute cache duration fails after five minutes of thinking time, and a 1-hour duration needs two subsequent reads simply to break even.

### How accurate are the reported costs?

Treat them as close estimates, not invoices. Every local parser — Frugal Tokens included — reconstructs cost from recorded token counts multiplied by a pricing table it maintains itself. Three things drift: vendors change prices, cache multipliers are now model-dependent (0.025x on Claude Fable 5.1 and Claude Mythos 5.1, 0.05x on Claude Opus 5.5, versus the 0.1x default), and cached versus uncached token accounting differs by harness. Anthropic's own documentation states that even its native `claude_code.cost.usage` metric is an approximation and that official billing belongs to the API provider. Use these numbers for relative comparison and trend detection, which is what they are good at, not for reconciliation.

### What is the best ccusage alternative for cache analysis?

If cache-miss *attribution* is the requirement, Frugal Tokens is currently the only tool in this comparison that classifies miss types — TTL expiry, first-write, and truncation — and prices each one separately; ccusage and AgentsView show cached versus uncached token splits but stop short of explaining what caused a miss. That said, ccusage remains the better default for most teams because of coverage and automation: eighteen named harnesses, JSON output, a statusline hook, and daily, weekly, monthly, and session reporting runnable through `npx`. The pragmatic answer is to run ccusage for breadth and Frugal Tokens alongside it for cache forensics rather than treating them as substitutes.
