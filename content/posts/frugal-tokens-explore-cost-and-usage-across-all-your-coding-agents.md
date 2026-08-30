---
title: "Frugal Tokens: Track Cost and Usage Across All Your Coding Agents"
date: "2026-08-25T10:02:22+00:00"
tags:
  - AI coding agent observability
  - token usage tracking
  - prompt caching cost
  - coding agent spend analysis
  - Claude Code
  - Codex
  - Cursor
description: "Frugal Tokens is a local, read-only tool that tracks token usage and reported cost across OpenCode, Claude Code, PI, Codex, and Cursor. Here's how it works and whether you need it."
draft: false
cover:
  image: "/images/frugal-tokens-explore-cost-and-usage-across-all-your-coding-agents.png"
  alt: "Frugal Tokens: Track Cost and Usage Across All Your Coding Agents"
  relative: false
schema: "schema-frugal-tokens-explore-cost-and-usage-across-all-your-coding-agents"
---

Frugal Tokens is a free, local-first, read-only tool that lets you see exactly how many tokens each of your AI coding agents consumed and what that cost you, across OpenCode, Claude Code, PI, Codex, and Cursor. It runs locally in Deno, never touches your agent databases, and surfaces per-session token usage plus the hidden cost of broken prompt-cache reuse. It is the sharpest per-session cost diagnostic we tested for teams that want to measure ROI on AI coding spend.

## What is Frugal Tokens? A local, read-only token-and-cost viewer across your coding agents

Frugal Tokens is an open-source utility that answers one question that most developers cannot answer today: *how much did my AI coding agents actually cost, and where did the tokens go?* It is built by dpclark4 and appeared on Hacker News as a Show HN (37 points), where it drew a crowd of developers who admitted they had "no idea how many cache misses were happening" during their sessions.

The tool runs entirely on your own machine using Deno (version 2.9+). It reads the local session and usage databases that your coding agents already write, normalizes them, and serves a read-only web view at `localhost:9000`. Because it is read-only, it never mutates or corrupts agent state — a meaningful safety property when you are poking around the internals of tools you rely on daily.

At the time of writing, Frugal Tokens supports at least five harnesses: OpenCode, Claude Code, PI (Apple's coding agent), Codex, and Cursor. That cross-harness coverage is what makes it unusual. Most developers work in one primary agent, but many now mix two or three. Frugal Tokens lets you compare them side by side.

## The real pain point: hidden prompt-cache misses and idle-gap TTL costs

To understand why a token tracker matters, you have to understand prompt caching — because that is where most silent AI cost lives. When you send repeated turns to a model like Claude or GPT, the provider can cache the shared prefix of your prompt. A cache *read* is dramatically cheaper than fresh *uncached* input. In Anthropic's pricing, cached input is typically about 90% cheaper than uncached input. If you keep your session alive and your context stable, subsequent turns bill at the cheap cache-read rate.

The problem is that caches expire. Anthropic's prompt cache, for example, has TTL windows (commonly 5 minutes and 1 hour) after which a cached entry is dropped. When you step away from your machine for a coffee break and come back, your next turn may no longer be cached — and it bills as full-priced uncached input.

The research brief captures a striking real-world example: a single TTL cache miss, in a Fable session where the user responded roughly 1.5 hours later, cost $6 for one message ([HN thread](https://news.ycombinator.com/item?id=49364223)). That is the hidden tax of idle gaps. Frugal Tokens specifically surfaces these failures through its cache-miss pricing analysis, which examines `uncachedInput`, `cacheRead`, and `cacheWrite` fields across the 5m/1h TTL windows to estimate the extra dollars you spent because a cache was not reused ([source code](https://github.com/dpclark4/frugal-tokens/blob/main/src/server/cacheMissPricing.ts)).

## How Frugal Tokens measures token usage across OpenCode, Claude Code, PI, Codex, and Cursor

Frugal Tokens does not intercept your traffic or wrap your CLI. Instead, it reads the telemetry your agents already persist locally:

- **Claude Code** stores session and usage data under its local project and config directories, including per-turn token counts and cache fields.
- **Codex** keeps JSONL session logs with usage records.
- **OpenCode** writes message and cost metadata to its storage.
- **Cursor** and **PI** expose session/usage structures that the tool parses and normalizes.

For each harness, Frugal Tokens extracts token usage and the *reported cost* — the dollar figure the vendor itself associates with those tokens. It deliberately relies on these reported values rather than computing its own pricing model. That is both a strength and a caveat: it gives you the vendor's own accounting, but if a vendor under-reports, so will the tool.

The cross-harness comparison is the feature developers actually wanted. The same logical task burns different token totals depending on the harness, the underlying model (Opus vs Sonnet vs Haiku tiering being a recurring theme), and how aggressively each tool caches. Independent, cross-harness data is, in the words of one HN commenter, "super important for companies measuring ROI on token spend as they recover from letting people go wild on token usage in the past year" ([source](https://news.ycombinator.com/item?id=49364223)).

## The per-session explorer and cache-miss pricing — the standout features

Two features distinguish Frugal Tokens from a plain "spend dashboard":

**The per-session explorer.** Rather than just rolling up a total, Frugal Tokens lets you drill into an individual session and see the token and cost breakdown turn by turn. You can spot the exact moment a session's cost spiked, correlate it with a long idle gap, and see whether that spike was a cache miss.

**Cache-miss pricing.** This is the feature that turns observability into action. Frugal Tokens estimates what a session *would have* cost had cache reuse worked, and compares it to what it *did* cost. When that gap is large, you have a concrete incentive to redesign your workflow — shorter sessions, faster turnarounds, or a tool with better caching — rather than blindly paying the difference.

Below is a representative breakdown of the cache states Frugal Tokens tracks and why each affects your bill:

| Cache state | What it means | Cost impact |
|---|---|---|
| `cacheWrite` (5m/1h) | Prompt prefix written to cache | Small write cost, enables future savings |
| `cacheRead` | Cached prefix reused from a live TTL window | ~90% cheaper than uncached input |
| `uncachedInput` | No cache hit; full prefix billed fresh | Full price — the expensive path |
| TTL miss | Cache expired because session sat idle too long | Billed as uncached; can cost dollars per turn |

## Frugal Tokens vs the field: AgentsView, Codeburn, BurnRate, and Agentic Metric

Frugal Tokens is not alone in the "agentic metrics" category, but it occupies a specific niche. Here is how it compares to the closest alternatives:

| Tool | Primary focus | Local-first | Cache-miss diagnostics | Session-level drill-down | Best for |
|---|---|---|---|---|---|
| **Frugal Tokens** | Token + reported cost across 5 harnesses | Yes (read-only) | Yes — TTL/cache pricing | Yes | Developers who want the hidden cache cost surfaced |
| **AgentsView** | Browse/search/analyze past sessions from dozens of agents | Yes (desktop/web + SQLite/Postgres/DuckDB backend) | Yes — cached vs uncached breakdown | Yes | Power users with many agents and export needs |
| **Codeburn** | Dollar spend only | Cloud | No — spend only | No | Teams that just want the bottom line |
| **BurnRate** | Team-wide spend + agent config + cost calculator | Yes (local-first, free tier) | Partial | Partial | Teams managing budgets across providers |
| **Agentic Metric** | Lightweight token/cost metrics | Yes | Limited | Limited | Minimal setups that want a lightweight counter |

The clearest distinction is **granularity vs. simplicity**. Codeburn explicitly tells you spend and "not messages and everything else," which an HN user flagged as a limitation. BurnRate goes further into team-wide cost management and even offers a "cut AI costs 40%" course. AgentsView reads from the widest set of agents (Claude Code, Codex, Gemini, Copilot, Cursor, Qwen, DeepSeek, OpenCode, and more) and is arguably the most full-featured suite.

Frugal Tokens sits on the diagnostic end: it is not trying to be your entire spend-management platform. It is trying to be the sharpest per-session and per-cache diagnostic available, and its single-session cache-miss pricing is the most precise we found.

## Local-first, read-only, and private: why that matters for teams

A large part of Frugal Tokens' appeal is architectural. Everything runs locally in Deno with no cloud dependency. Your agent data — which often contains source code context, file paths, and internal reasoning — never leaves your machine. For teams with sensitive codebases that are understandably wary of sending session telemetry to a third-party SaaS, this is a decisive advantage.

The read-only guarantee reinforces that trust. Frugal Tokens only opens agent databases to read them; it makes no writes. You are not handing your session history to another vendor, and you are not risking corruption of the very tools you depend on. If your security review requires "no external exfiltration and no writes," Frugal Tokens passes both checks out of the box.

That local-first posture is also a practical resilience win: no account to create, no API keys to leak, no dependency on a startup's uptime. It is a `deno run` away from a working dashboard.

## Who is Frugal Tokens for, and the trade-offs vs spend-only trackers

Frugal Tokens is for developers and small teams who want to *understand* their AI spend, not just see a number. It is the right fit if you:

- Work across two or more coding agents (Claude Code plus Codex, Cursor plus OpenCode) and want a fair comparison.
- Suspect prompt-cache misses are inflating your bill and want proof, per session.
- Operate under privacy constraints and refuse to send session data to a cloud dashboard.
- Are responsible for justifying AI tooling spend and need concrete, per-session evidence.

The trade-offs are real. First, because it relies on each vendor's *reported* cost, it is only as accurate as the vendors' own accounting. Second, it is not a team-wide budget management platform — if you need role-based access, team dashboards, and invoice-level cost management, BurnRate or a full observability suite is a better fit. Third, its harness coverage (five) is narrower than AgentsView's (dozens). Fourth, it is a developer-facing tool: there is no hosted version, so non-technical stakeholders cannot log in and check numbers.

If you only need a single bottom-line spend figure across the team, a spend-only tracker like Codeburn is simpler. If you need per-session cache diagnostics to *reduce* spend, Frugal Tokens is the sharper instrument.

## Verdict — should you add per-session token cost tracking to your workflow?

Yes — for most developers actively using AI coding agents, the answer is yes. The single most compelling argument is the $6 single-message TTL miss and the widespread admission that developers have "no idea" how many cache misses occur. If you cannot see cache misses, you cannot fix them, and you are silently paying a premium on every idle-gap resumption.

Frugal Tokens earns a strong recommendation for the developer who wants a privacy-preserving, read-only, per-session view across the five most common harnesses. It is free, local, and its cache-miss pricing turns vague anxiety about AI cost into a concrete, actionable number. Pair it with a spend-only or team-level tool if you also need the company-wide bottom line, but make Frugal Tokens (or its equivalent diagnostic depth) part of your workflow if you care about token cost tracking for coding agents at all.

The bottom line: AI coding cost is no longer opaque. Tools like Frugal Tokens put the per-session and per-cache truth back in your hands — and for teams measuring ROI on agent spend, that visibility is no longer a nicety. It is a governance requirement.

## Frequently Asked Questions

### Is Frugal Tokens free to use?
Yes. Frugal Tokens is open source and runs locally in Deno (2.9+). There is no hosted version and no subscription — you run it yourself on your own machine.

### Which coding agents does Frugal Tokens support?
It tracks token usage and reported cost for at least five harnesses: OpenCode, Claude Code, PI (Apple), Codex, and Cursor. This coverage is narrower than some rivals like AgentsView, which reads from dozens of agents.

### Why does my AI agent cost more after I step away from my keyboard?
Prompt caches expire on a TTL (commonly 5 minutes and 1 hour). If your session sits idle longer than the TTL, the next turn bills as fresh uncached input instead of a cheap cache read. Frugal Tokens surfaces these TTL misses and their dollar cost.

### Does Frugal Tokens send my data anywhere?
No. It is local-first and read-only. It reads your agents' local session databases, normalizes the data, and serves a local dashboard at localhost:9000. Nothing leaves your machine, and it makes no writes to your agent databases.

### How accurate is the cost Frugal Tokens reports?
It uses the reported cost figures that each vendor associates with the tokens consumed. That means it is accurate to the extent the vendors' own accounting is accurate. It does not compute its own pricing model, so a vendor that under-reports will show lower costs.
