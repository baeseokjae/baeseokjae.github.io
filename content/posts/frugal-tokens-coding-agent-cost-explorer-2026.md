---
title: "Frugal Tokens: How to Track Coding Agent Cost and Usage Per Session"
date: 2026-09-05T19:04:09+00:00
tags:
  - AI coding agents
  - token cost tracking
  - observability
  - Claude Code
  - Codex
  - Cursor
  - prompt caching
description: "Frugal Tokens is a free, local, read-only dashboard that shows token usage and cost per session across OpenCode, Claude Code, PI, Codex, and Cursor."
draft: false
cover:
  image: "/images/frugal-tokens-coding-agent-cost-explorer-2026.png"
  alt: "Frugal Tokens: Exploring Cost and Usage Across Coding Agents"
  relative: false
schema: "schema-frugal-tokens-coding-agent-cost-explorer-2026"
---

Frugal Tokens is a free, local, read-only web dashboard that shows exactly how many tokens each of your AI coding agent sessions consumed and what those tokens cost, across OpenCode, Claude Code, PI, Codex, and Cursor. It runs entirely on your machine, never mutates your agent databases, and surfaces hidden costs like prompt-cache misses that most developers never see. This guide walks you through installing it, pointing it at your agents, and reading the per-session explorer to cut your coding agent spend.

## What is Frugal Tokens and why you need a per-session cost explorer

Most developers have no idea how much their AI coding agents actually cost. Your terminal shows you the code, but it rarely shows you the bill. Frugal Tokens is an open-source tool that fills that gap: it reads the local session data that OpenCode, Claude Code, PI (Apple), Codex, and Cursor already store on your machine and renders it into a per-session explorer of token usage and reported cost.

The tool appeared as a Show HN on August 19, 2026, earning 37 points from the Hacker News community. Reviewers called the per-session explorer "the best part" of the tool, and one commenter noted that independent, cross-harness data is "super important for companies measuring ROI on token spend." The core value is simple: before you can reduce coding agent cost, you have to be able to see it.

## Prerequisites — installing Deno 2.9+ on macOS or Linux

Frugal Tokens is written in Deno, so the only real prerequisite is a recent Deno runtime. The project requires **Deno 2.9 or newer**. If you do not have Deno installed, the official README recommends installing it with a single command:

```bash
curl -fsSL https://deno.land/install.sh | sh
```

After the installer finishes, make sure the `deno` binary is on your PATH. You can verify the version with:

```bash
deno --version
```

If the version prints 2.9.0 or higher, you are ready to move on. Frugal Tokens runs locally and serves a read-only web view at `localhost:9000`, so no cloud account, API key, or network dependency is required.

## First setup — copy .env.example, build, and start the local server

Once Deno is ready, clone the repository and run the two-command setup. From the project directory:

```bash
cp .env.example .env
deno task build && deno task start
```

That is the entire setup. The `cp` step creates your local configuration file, `deno task build` compiles the frontend, and `deno task start` launches the local server. When the server is running, open your browser to `http://localhost:9000` to see the dashboard.

If you are developing the tool itself rather than just using it, run `deno task dev` instead. Dev mode serves on port 5273 and computes its own API port, ignoring the `PORT` variable, so you can run a development instance alongside a production one without a port conflict.

## Opening the dashboard at localhost:9000 and the per-session explorer

The dashboard at `localhost:9000` is organized around sessions. Each row represents one agent session, and clicking into a session opens the per-session explorer that HN users singled out as the tool's best feature.

Inside the explorer you get a turn-by-turn breakdown: how many tokens were sent in, how many were read from cache, how many were written to cache, how many came back as output, and what the whole exchange cost. This granularity is what separates Frugal Tokens from simpler spend trackers. As one HN commenter put it, tools like Codeburn "only tell you spend not messages and everything else" — Frugal Tokens gives you the full picture.

## Pointing Frugal Tokens at your agents — the .env path variables

Frugal Tokens auto-discovers most agent data, but you can override where it looks using environment variables in your `.env` file. Each harness stores its data in a different place, and knowing these paths is the key to making the tool work with your exact setup.

| Harness | Default storage location | .env variable |
|---------|--------------------------|----------------|
| OpenCode | `~/.local/share/opencode/opencode.db` (SQLite) | `OPENCODE_DB_PATH` |
| Claude Code | `~/.claude/projects/<encoded-cwd>` (JSONL transcripts) | `CLAUDE_CODE_PROJECT_PATH` |
| PI (Apple) | PI session directory | `PI_SESSION_DIR` |
| Codex | Codex session directory | `CODEX_SESSION_DIR` |
| Cursor | `~/.cursor/chats/<workspace>/<agent>/store.db` (SQLite) | `CURSOR_CHATS_PATH` |

The OpenCode path points to a SQLite database at `~/.local/share/opencode/opencode.db`, with the schema observed on July 10, 2026 using OpenCode 1.17.x. Claude Code stores JSONL transcript files under `~/.claude/projects/<encoded-cwd>`, with the version observed being Claude Code 2.1.202. Cursor keeps per-agent SQLite stores under `~/.cursor/chats/<workspace>/<agent>/store.db`.

You can also change the API port with the `PORT` variable. If your agent data lives somewhere non-standard, set the matching variable to the real path and restart the server.

## Understanding the cache fields — uncachedInput, cacheRead, cacheWrite, and derived metrics

To read the dashboard correctly, you need to understand the cache fields. Frugal Tokens maps each harness's usage data into a common vocabulary. For Claude Code, the mapping is:

- `input_tokens` → `uncachedInput`
- `cache_read_input_tokens` → `cacheRead`
- `cache_creation_input_tokens` → `cacheWrite`
- `output_tokens` → `output`

From these raw fields, Frugal Tokens derives two higher-level metrics:

- **freshPrompt (New input)** = input + reported cache write
- **processed (Total activity)** = input + cache read + cache write + output + reasoning

The distinction matters because cached tokens are dramatically cheaper than uncached ones. A session that reads most of its context from cache costs a fraction of one that re-sends everything as fresh input. The `cacheRead` field is where you see the savings, and the `cacheWrite` field is where you see the cost of establishing a cache in the first place.

## Spotting hidden prompt-cache misses and idle-gap TTL costs in your sessions

The single most expensive hidden cost in AI coding agents is the prompt-cache miss. When you step away from a session for an hour or more, the prompt cache expires, and the next message re-sends the entire context at full uncached prices.

This is not a theoretical concern. On the Frugal Tokens HN thread, one user reported that a single TTL cache miss — responding roughly 1.5 hours later — cost **$6 for one message** in a Fable session. Another commenter admitted they had "no idea how many cache misses were happening" after stepping away for an hour or more, and used the tool to uncover workflow and build-pipeline slowdowns in heavy sessions.

The per-session explorer makes these misses visible. When you see a cost spike that correlates with an idle gap in the session timeline, that is a TTL cache miss. The fix is behavioral: either keep sessions short, resume them before the cache TTL expires, or redesign your prompts so the expensive context is not re-sent from scratch every time.

## Comparing token usage and cost across harnesses (cross-harness view)

One of Frugal Tokens' most useful features is the cross-harness comparison. The same task burns different numbers of tokens depending on which agent you use, and the tool lets you see those differences side by side.

The demo surfaces clear tiering themes across models — Opus versus Sonnet versus Haiku, for example — showing that model choice has a direct, measurable effect on token consumption. For teams, this is independent verification that beats vendor claims. As one HN commenter put it, cross-harness token differences are "independently-verified data points for ROI measurement." If you are deciding whether to standardize on one agent or let developers pick their own, this view gives you the data to make that call.

## Optional — periodic sync with FRUGAL_TOKENS_SYNC_INTERVAL_SECONDS and changing the API port

By default, Frugal Tokens syncs your agent data once at boot. If you want the dashboard to stay fresh while you work, set the `FRUGAL_TOKENS_SYNC_INTERVAL_SECONDS` variable in your `.env` file to a positive number of seconds. The server will then re-import your session data on that interval.

If the variable is unset or set to `0`, the tool performs boot-only sync and does not re-import. For most users, leaving it unset is fine — you can restart the server when you want a fresh view. For teams that keep the dashboard open all day, a sync interval of 60 or 300 seconds keeps the numbers current without much overhead.

## Frugal Tokens vs the field — AgentsView, BurnRate, Codeburn, and Agentic Metric

Frugal Tokens is not the only tool in this space, so it helps to know where it fits. The main alternatives are AgentsView, BurnRate, and Codeburn.

| Tool | Focus | Key difference from Frugal Tokens |
|------|-------|-----------------------------------|
| Frugal Tokens | Per-session token/cost explorer across 5 harnesses | Read-only, local, granular cache-miss visibility |
| AgentsView | Browsing/searching/analyzing past sessions | Auto-discovers dozens of agents; SQLite/Postgres/DuckDB backend |
| BurnRate | Team-wide cost observability | Tracks subagent behavior; zero config; brew install; paid tiers |
| Codeburn | Spend tracking | "Only tells you spend, not messages" — less granular |

AgentsView is a local-first desktop and web app that auto-discovers session data from dozens of agents including Claude Code, Codex, Gemini, Copilot, Cursor, Qwen, and DeepSeek, with token usage and cost reports plus a cached-versus-uncached breakdown. BurnRate is a free, local-first observability tool for Claude Code, Cursor, and Copilot that tracks subagent behavior and cost, with team-wide management and paid tiers. Codeburn is simpler but, as HN users noted, less granular.

## Privacy and read-only safety — why local-first matters for teams

Frugal Tokens is explicitly read-only. It never mutates your agent databases, and the Cursor capture sidecar is append-only. That design matters for two reasons.

First, it is safe. You can point it at your real session data without worrying that it will corrupt or alter anything. Second, it is private. No code leaves your machine, there is no cloud dependency, and no third party sees your prompts or code. For teams working on sensitive codebases, this local-first, read-only posture is a genuine advantage over hosted analytics tools.

## Common pitfalls — stale paths, missing session tags, Cursor's missing cost data, and Claude's absent reportedCost

A few gotchas trip up new users. The most common is a stale or wrong path in `.env` — if the dashboard shows no sessions, double-check that the path variables point at the real locations listed in the table above.

Cursor is a special case: it does not persist historical token usage or dollar cost in its chat stores. That means Frugal Tokens cannot show you cost data for Cursor sessions the way it can for OpenCode or Codex. The Cursor capture sidecar is append-only, so it records what it can without modifying Cursor's own data.

Claude Code is another special case. Its transcripts do not report dollar cost, so `reportedCost` is absent for Claude sessions. Frugal Tokens compensates by applying versioned model rate cards to emit a `computedCost` estimate. That estimate is a good approximation, but it is computed, not reported, so treat it accordingly.

## Verdict — should you add per-session token cost tracking to your workflow?

If you use AI coding agents regularly and care about what they cost, the answer is yes. Frugal Tokens is free, local, read-only, and takes about two minutes to set up. It gives you something most developers simply do not have: a clear, per-session view of token usage and cost across the agents you already use.

The hidden value is the cache-miss visibility. A single TTL cache miss can cost $6 for one message, and most people never see it coming. Once you can see where your money goes, you can act — by shortening sessions, resuming before cache expiry, or redesigning prompts to cut recurring cost. For individual developers and teams alike, that visibility is the first step to actually being frugal with tokens.

## FAQ

**Is Frugal Tokens free to use?**
Yes. Frugal Tokens is an open-source tool that runs entirely on your local machine. There is no cloud service, no subscription, and no API key required.

**Which coding agents does Frugal Tokens support?**
It supports at least five harnesses: OpenCode, Claude Code, PI (Apple), Codex, and Cursor. Each stores its session data locally, and Frugal Tokens reads that data to build the dashboard.

**Does Frugal Tokens modify my agent data?**
No. Frugal Tokens is strictly read-only. It never mutates your agent databases, and the Cursor capture sidecar is append-only, so your data is never altered.

**Why is my Cursor session missing cost data?**
Cursor does not persist historical token usage or dollar cost in its chat stores. Frugal Tokens can only show what the harness records, so Cursor sessions may lack the cost breakdown you see for other agents.

**What is a TTL cache miss and why is it expensive?**
A TTL cache miss happens when a prompt cache expires — often after you step away from a session for an hour or more. The next message re-sends the entire context at full uncached prices. One HN user reported a single TTL miss costing $6 for one message.
