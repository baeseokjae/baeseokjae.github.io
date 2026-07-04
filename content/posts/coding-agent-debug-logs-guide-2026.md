---
title: "Coding Agent Debug Logs Guide 2026: Claude Code, Codex, GitHub MCP, and Playwright MCP"
date: 2026-07-04T12:00:00+00:00
tags: ["Claude Code", "Codex CLI", "MCP", "Debugging", "Developer Tools"]
description: "A practical 2026 guide to debugging AI coding agents — Claude Code, Codex CLI, GitHub MCP Server, and Playwright MCP Server — with real commands, log locations, and troubleshooting patterns."
draft: false
cover:
  image: "/images/coding-agent-debug-logs-guide-2026.png"
  alt: "Coding Agent Debug Logs Guide 2026"
  relative: false
schema: schema-coding-agent-debug-logs-guide-2026
---

If you've been using AI coding agents daily in 2026, you've hit the wall where Claude Code freezes mid-task, Codex CLI silently drops an MCP connection, or Playwright MCP opens a headed browser that nobody asked for. The tools are powerful, but when they break, the debugging experience varies wildly between them.

I've spent the last six months running all four of these tools in production workflows — Claude Code for complex refactoring, Codex CLI for quick prototyping, GitHub MCP for PR automation, and Playwright MCP for browser testing. Here's what I've learned about getting useful debug output out of each one.

## Claude Code: The Most Debugging Tooling

Claude Code has the richest debugging toolkit of any coding agent I've used. It's not just about log files — there are built-in commands for almost every failure mode.

### The `/doctor` Command

When something feels off — slow responses, MCP servers not loading, hooks not firing — start here. Run `/doctor` inside Claude Code or `claude doctor` from the shell. It runs an automated health check covering installation integrity, settings validity, MCP configuration, and context usage. I run this as my first step whenever I suspect a configuration issue rather than a transient API error.

### Heap Dump Analysis for Memory Issues

Claude Code can consume surprising amounts of memory on large codebases. When you notice sluggishness or auto-compaction thrashing, run `/heapdump`. This writes a JavaScript heap snapshot to `~/Desktop/Claude\ Code.heapsnapshot` (or your home directory on Linux). Open it in Chrome DevTools → Memory → Load to see exactly what's eating memory. I've caught runaway context buffers and bloated MCP response caches this way.

### Safe Mode and Compaction

Two commands I use constantly:

- **`claude --safe-mode`** — Starts Claude Code with all customizations disabled (plugins, MCP servers, hooks). If the problem disappears, you know one of your extensions is the culprit. I use this to bisect which MCP server is causing startup delays.
- **`/compact`** — Reduces context size. The real power is `/compact keep only the plan and the diff`, which strips everything except what you're actively working on. I run this before every major task switch.

### Session Recovery

Crashes happen. `claude --resume` in the same directory picks up your previous session after a restart. Combined with `/clear` to drop irrelevant conversation history, this makes long-running sessions manageable. For persistent issues, `/feedback` sends diagnostics directly to Anthropic.

### Common Failure Patterns

| Symptom | First Thing to Try |
|---|---|
| High CPU / memory | `/heapdump` then `/compact` |
| MCP servers not loading | `claude --safe-mode` |
| Garbled terminal text | `/terminal-setup` or disable GPU acceleration |
| Slow search on WSL | Install ripgrep, set `USE_BUILTIN_RIPGREP=0` |
| 529 / 429 errors | Wait, then use `/compact` to reduce context |
| Auto-compaction thrashing | Read large files in chunks, use sub-agents |

For more on Claude Code's broader capabilities, check out the [Claude Code Artifacts guide](/posts/claude-code-artifacts-guide-2026-live-shareable-previews-from-ai-coding-sessions/).

## Codex CLI: TOML Config and Plaintext Logs

Codex CLI takes a different approach. Its debugging story centers on configuration files and log directories rather than interactive commands.

### Log Directory Setup

Codex writes logs to `$CODEX_HOME/log` by default. Setting this explicitly also enables the opt-in plaintext TUI log (`codex-tui.log`), which is invaluable for seeing what Codex is doing in real time. I set `CODEX_HOME` in my shell profile and tail the log during long operations:

```bash
export CODEX_HOME="$HOME/.codex"
tail -f "$CODEX_HOME/log/codex-tui.log"
```

### Configuration Debugging

Codex uses `~/.codex/config.toml` (TOML format, not JSON or YAML). The key sections for debugging are:

```toml
[mcp_servers.my-server]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
bearer_token_env_var = "MY_SERVER_TOKEN"

# Force a specific auth method
forced_login_method = "chatgpt"  # or "api_key"
```

If MCP servers aren't loading, check the `[mcp_servers]` section first. The `bearer_token_env_var` field is particularly useful for HTTP-transport MCP servers — it sources the token from an environment variable rather than hardcoding it.

### Auth Troubleshooting

Codex supports ChatGPT login (recommended) and API key auth. If you're getting auth failures:

- **MFA required** for email/password login. Social login (Google, Microsoft, Apple) doesn't need MFA.
- **Login caching** stores credentials in a plaintext file. Tokens refresh automatically during use.
- **Forced login method** — set `forced_login_method` in config to lock to one auth path.

### Snapshot Shell and Login Shell

Two config options that affect debugging:

- **`snapshot_shell`** (on by default) — Snapshots the shell environment to speed up repeated commands. Turn it off if you're changing environment variables between commands and they're not being picked up.
- **`allow_login_shell`** — Uses login-shell semantics for shell-based tools. Enable this if your tools depend on profile files.

## GitHub MCP Server: Structured Error Types

The GitHub MCP Server is unique among these four because it's a server, not a CLI agent. Its debugging story is about structured error handling rather than log files.

### Error Types

The server defines two custom error types that bubble up through the MCP framework:

- **`GitHubAPIError`** — For REST API errors. Contains `Message`, `Response` (the full `*github.Response` object), and `Err` fields.
- **`GitHubGraphQLError`** — For GraphQL API errors. Contains `Message` and `Err` fields.

These errors are stored in context for middleware inspection. You can retrieve them with:

```go
errors.GetGitHubAPIErrors(ctx)
errors.GetGitHubGraphQLErrors(ctx)
```

### Design Philosophy

The error handling follows a clear split:

- **User-actionable errors** (auth failures, rate limits, 404s) → Failed tool calls that the agent can handle
- **Developer errors** (JSON marshaling, internal logic) → Go errors that bubble up through the MCP framework

This means if you're building an agent that uses GitHub MCP, you should handle the first category in your agent's error recovery logic and let the second category crash to a log.

### Authentication Methods

The server supports three auth methods, and getting them wrong is the most common source of errors:

1. **OAuth** (browser-based, token stays in memory) — Best for interactive use
2. **Personal Access Token** (via `GITHUB_PERSONAL_ACCESS_TOKEN` env var) — Best for CI/CD
3. **GitHub App** — Required for GitHub Enterprise Server

Minimum PAT scopes: `repo`, `read:packages`, `read:org`. Store in `.env` files, never commit.

### Remote vs Local

The server can run remotely at `https://api.githubcopilot.com/mcp/` or locally via Docker (`ghcr.io/github/github-mcp-server`). For debugging, I prefer the local server with `--gh-host` pointing to my GHES instance — it gives me direct log output and I can restart it independently of the agent.

For a broader comparison of MCP capabilities across agents, see the [AI Coding Agent Capability Matrix](/posts/ai-coding-agent-capability-matrix-2026/).

## Playwright MCP: Console Levels and Browser Tracing

Playwright MCP is the most configurable of the four when it comes to debug output. It's also the one most likely to need debugging, because browser automation is inherently flaky.

### Console Level Filtering

The most important debug setting is the console level:

```bash
npx @playwright/mcp --console-level debug
# or
export PLAYWRIGHT_MCP_CONSOLE_LEVEL=debug
```

Levels cascade: `error` < `warning` < `info` < `debug`. I run at `debug` during development and `warning` in production. The debug level shows every browser console message, network request, and page event — noisy but essential when a test is failing silently.

### Output Modes

Playwright MCP supports two output modes:

- **`stdout`** (default) — Output goes to stdout. Good for local development.
- **`file`** — Output goes to `--output-dir`. Essential for CI/CD where you need to collect artifacts.

Set `--output-max-size` to control when old output files get evicted. I use 50MB for CI runs.

### Browser Tracing and Step Debugging

Two features that save me hours:

- **`browser_start_tracing` / `browser_stop_tracing`** — Records a Playwright trace that you can open in the Playwright Trace Viewer. This shows every network request, DOM mutation, and screenshot. I start tracing before any flaky test and stop it after.
- **`browser_pause` / `browser_resume`** — Pauses the browser at the current state. `browser_resume` with `step=true` pauses before the next action, letting you step through interactions one at a time.
- **`browser_set_debugger`** — Pauses at a specific `<file>:<line>` location. Think of it as a breakpoint for browser automation.

### Headless vs Headed

By default, Playwright MCP runs **headed** (you see the browser window). This is great for debugging but annoying in CI. Use `--headless` or `PLAYWRIGHT_MCP_HEADLESS=true` for automated runs.

For containerized environments, you'll likely need `--no-sandbox`. And if you're testing against a local dev server with self-signed certs, `--ignore-https-errors` is your friend.

### Session Persistence

Playwright MCP stores session data (cookies, localStorage) at a platform-specific location. Use `--user-data-dir` to override this, or `--isolated` to keep everything in memory (no disk writes). The `--save-session` flag saves the session into the output directory for later replay.

For more on browser-based agent workflows, see the [GitHub Copilot Browser Tools guide](/posts/github-copilot-browser-tools-guide-2026/).

## Cross-Tool Debugging Patterns

After using all four tools, here are the patterns that apply across the board:

### 1. Environment Variables Are Your First Debug Tool

Every one of these tools respects environment variables for debug configuration. Before diving into config files or interactive commands, check what env vars are available:

- Claude Code: `CLAUDE_CODE_*` vars
- Codex CLI: `CODEX_HOME`, `OPENAI_API_KEY`
- GitHub MCP: `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_TOKEN`
- Playwright MCP: `PLAYWRIGHT_MCP_*` vars

### 2. MCP Connection Issues Are the Most Common Failure

All four tools support MCP, and MCP connection issues are the single most common source of debugging pain. The fix is almost always:

- Check that the MCP server process is actually running
- Verify the transport (stdio vs HTTP) matches what the agent expects
- Check environment variables are being forwarded to the MCP server process
- For HTTP transport, verify the port and URL

### 3. Session Persistence Is Not a Given

Claude Code and Codex CLI both support session resume after crashes. GitHub MCP and Playwright MCP don't — they're stateless by design. If you're doing long-running work, prefer Claude Code or Codex CLI, or build your own session management around the stateless tools.

### 4. Log Levels Matter

Claude Code has `/doctor`, Codex CLI has `codex-tui.log`, Playwright MCP has `--console-level`, and GitHub MCP has structured error types. Learn the debug entry point for each tool before you need it — reading docs during an outage is never fun.

## Quick Reference: Where to Look First

| Tool | First Debug Step | Log Location |
|---|---|---|
| Claude Code | `/doctor` or `claude doctor` | Heap dump via `/heapdump` |
| Codex CLI | `tail -f $CODEX_HOME/log/codex-tui.log` | `$CODEX_HOME/log/` |
| GitHub MCP | Check `GITHUB_PERSONAL_ACCESS_TOKEN` | Structured errors in context |
| Playwright MCP | `--console-level debug` | `--output-dir` or stdout |

The reality is that AI coding agents in 2026 are still maturing. Each tool has its own debugging philosophy — Claude Code gives you interactive commands, Codex CLI gives you config files, GitHub MCP gives you structured errors, and Playwright MCP gives you browser-level tracing. None of them have a unified debug dashboard or a single log file that tells you everything.

But if you learn the debug entry point for each tool and keep a terminal tailing the relevant log, you'll cut your troubleshooting time by at least half. That's been my experience, and I've been doing this full-time since early 2026.

## FAQ

### Why does Claude Code freeze or slow down on large codebases?

Claude Code's context window fills up as your conversation grows. Run `/compact` to reduce context size, or `/compact keep only the plan and the diff` to strip everything except your active work. If memory usage is high, run `/heapdump` and inspect the heap snapshot in Chrome DevTools. For very large codebases, consider using sub-agents to parallelize work across smaller context windows.

### Codex CLI keeps failing to connect to my MCP server. What should I check first?

Three things in order: (1) Verify the MCP server process is running — `ps aux | grep <server-name>`. (2) Check your `~/.codex/config.toml` `[mcp_servers]` section for typos in the command, args, or `bearer_token_env_var`. (3) If using HTTP transport, confirm the port matches and the URL is reachable. Codex's `codex-tui.log` (enabled by setting `CODEX_HOME` explicitly) will show connection errors in plain text.

### Can I use GitHub MCP Server with GitHub Enterprise Server?

Yes. Start the local Docker server with `--gh-host https://your-ghes-instance.com`. You'll need a GitHub App for authentication — PAT and OAuth won't work with GHES. The server also supports `ghe.com` subdomains with the same `--gh-host` flag. For the remote server at `api.githubcopilot.com/mcp/`, GHES is not supported.

### Playwright MCP opens a browser window in CI. How do I make it headless?

Set `--headless` on the command line or `PLAYWRIGHT_MCP_HEADLESS=true` in your environment. By default Playwright MCP runs headed, which is useful for local debugging but breaks headless CI runners. You'll also want `--no-sandbox` in containerized environments and `--output-mode file` with `--output-dir` to collect artifacts.

### Which tool has the best session recovery after a crash?

Claude Code and Codex CLI both support session resume — `claude --resume` and Codex's automatic token refresh, respectively. GitHub MCP and Playwright MCP are stateless by design and don't persist sessions. For long-running work where crashes are costly, Claude Code's `/compact` + `--resume` workflow is the most robust. For stateless tools, build your own checkpointing by saving state to disk at each step.
