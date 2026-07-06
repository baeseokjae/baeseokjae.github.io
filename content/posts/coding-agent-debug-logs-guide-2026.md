---
cover:
  alt: 'Coding Agent Debug Logs Guide 2026: Claude Code, Codex, GitHub MCP, and Playwright MCP'
  image: /images/coding-agent-debug-logs-guide-2026.png
  relative: false
date: 2026-07-04 04:00:00+00:00
description: 'Complete guide to debugging AI coding agents in 2026: Claude Code /doctor and heapdump, Codex CLI log_dir and TOML config, GitHub MCP error types, and Playwright MCP tracing tools.'
draft: false
schema: schema-coding-agent-debug-logs-guide-2026
tags:
- ai-coding
- developer-tools
- debugging
- claude-code
- openai-codex
- mcp
- playwright
title: 'Coding Agent Debug Logs Guide 2026: Claude Code, Codex, GitHub MCP, and Playwright MCP'
---

AI coding agents ship code faster than ever, but when they break, the debugging experience is nothing like a traditional stack trace. You don't get a line number and a segfault — you get a silent hang, a garbled terminal, a 529 from the API, or an MCP server that just won't connect. After spending the last year running Claude Code, Codex CLI, GitHub MCP Server, and Playwright MCP in production pipelines, I've collected the debug patterns that actually work. Here's the field guide I wish I'd had.

## Claude Code: The Most Debuggable Agent, If You Know Where to Look

Claude Code has the richest debug tooling of any coding agent in 2026 — I covered its overall capabilities in the [AI Coding Agent Capability Matrix 2026](/posts/ai-coding-agent-capability-matrix-2026/) — but most of it is hidden behind slash commands you'd never discover unless someone told you.

### The /doctor Command — Your First Stop

Before you dig into logs, run `/doctor` inside Claude Code or `claude doctor` from the shell. It runs an automated health check covering installation integrity, settings validity, MCP server connectivity, and context usage statistics. I've seen it catch a stale Node.js version that was silently breaking MCP tool calls — something that would have taken me an hour to trace manually.

When Claude Code feels sluggish or behaves oddly, `/doctor` is the fastest triage tool. It reports back in under five seconds and flags issues with severity levels.

### /heapdump for Memory Mysteries

If Claude Code is eating RAM and you don't know why, run `/heapdump`. It writes a JavaScript heap snapshot to `~/Desktop/` (or your home directory on Linux) as a `.heapsnapshot` file. Open that in Chrome DevTools → Memory → Load, and you can inspect object allocations, retained sizes, and closure chains. I used this to discover a plugin that was holding a reference to the entire file tree in memory — 1.2 GB of retained objects from a 50 MB project.

### Safe Mode and Compaction

When performance degrades mid-session, two commands save the day:

- **`claude --safe-mode`** — launches Claude Code with zero customizations: no plugins, no MCP servers, no hooks. If the problem disappears, one of your customizations is the culprit. Binary search your MCP servers from there.
- **`/compact`** — reduces context size by summarizing older conversation turns. I run `/compact keep only the plan and the diff` every 30-40 turns in a long session. Without it, auto-compaction kicks in and starts thrashing, which actually makes things worse.

### Session Recovery

Crashes happen. `claude --resume` in the same directory picks up your previous session. If the session file is corrupted, `/clear` starts fresh without losing your CLAUDE.md project config. And `/feedback` sends debug logs directly to Anthropic — use it when you hit something that feels like a real bug. For sharing session outputs, check out the [Claude Code Artifacts guide](/posts/claude-code-artifacts-guide-2026-live-shareable-previews-from-ai-coding-sessions/) for live previews.

### Common Claude Code Issues I've Hit

| Symptom | Likely Cause | Fix |
|---|---|---|
| High CPU, fan spinning | Context too large | `/compact` or `/clear`, restart |
| Garbled terminal text | GPU acceleration in editor | `terminal.integrated.gpuAcceleration: off` |
| Slow search on WSL | Missing ripgrep | Install ripgrep, set `USE_BUILTIN_RIPGREP=0` |
| 529 Overloaded | API capacity | Wait 30s, retry. Use off-peak hours |
| MCP servers not loading | Config syntax error | `claude --safe-mode` to isolate |

## Codex CLI: TOML Config and the Hidden TUI Log

Codex CLI takes a different approach. Where Claude Code has slash commands, Codex has a configuration file and a log directory.

### Finding the Logs

Codex writes logs to `$CODEX_HOME/log` by default. Setting `CODEX_HOME` explicitly also enables the opt-in plaintext TUI log (`codex-tui.log`), which is invaluable for debugging startup issues. If Codex CLI fails to launch or crashes immediately, check that file first — it captures what happened before the TUI even started.

The config lives at `~/.codex/config.toml` in TOML format. Here's a debug-oriented config I use:

```toml
[logging]
log_dir = "/home/me/.codex/logs"
level = "debug"

[mcp_servers.github]
command = "npx"
args = ["-y", "@github/github-mcp-server"]
env = { GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_TOKEN}" }
```

### Authentication Debugging

Codex CLI caches login details in a plaintext file at `~/.codex/auth.json`. Tokens refresh automatically during use, but if you're getting auth errors, check:

1. **MFA requirements** — Email/password login requires MFA. Social login (Google, Microsoft, Apple) doesn't.
2. **Forced login method** — Set `forced_login_method = "chatgpt"` or `"api_key"` in config.toml to enforce one auth path.
3. **Bearer token env var** — For MCP HTTP servers, use `bearer_token_env_var` in the MCP server config to source tokens from environment variables rather than hardcoding.

### MCP OAuth Gotcha

Codex CLI supports MCP OAuth with an optional fixed port for the callback server. If you're running in a devbox or behind ingress, set the base callback URL override. Without it, the OAuth redirect URL defaults to localhost and breaks in proxied environments.

## GitHub MCP Server: Structured Error Types

The GitHub MCP Server handles errors differently from the coding agents — it uses typed error objects that bubble through the MCP framework.

### Error Types You'll Encounter

The server defines two custom error types:

- **`GitHubAPIError`** — for REST API errors. Contains `Message`, `Response` (the full `*github.Response` object), and `Err` fields. When a tool call fails with a 404 or 403, this is what you get.
- **`GitHubGraphQLError`** — for GraphQL API errors. Contains `Message` and `Err` fields. GraphQL errors are trickier because the HTTP status is 200 even when the query fails — you have to inspect the error body.

Both types are stored in Go context via `errors.ContextWithGitHubErrors(ctx)` and retrieved with `errors.GetGitHubAPIErrors(ctx)` / `errors.GetGitHubGraphQLErrors(ctx)`. If you're building a custom MCP host, this middleware pattern lets you inspect all errors from a session in one place.

### Authentication Options

The GitHub MCP Server supports three auth methods:

1. **OAuth (browser-based)** — Token lives in memory only. Best for local development.
2. **Personal Access Token** — Set `GITHUB_PERSONAL_ACCESS_TOKEN` env var. Minimum scopes: `repo`, `read:packages`, `read:org`. Store in `.env`, never commit.
3. **GitHub App** — For GitHub Enterprise Server (GHES/ghe.com). Use `--gh-host https://your-subdomain.ghe.com`.

For enterprise setups, the `--gh-host` flag is required with the `https://` prefix. I've seen teams waste hours debugging "not found" errors only to realize the host flag was missing.

### Insiders Mode

Add `/insiders` to the URL path or set the `X-MCP-Insiders` header for early access to new features. Useful for testing, but don't rely on it in production — insiders features can change without notice.

## Playwright MCP: Browser-Level Debugging

Playwright MCP is unique among these tools because it controls a real browser — similar to how [GitHub Copilot's browser tools](/posts/github-copilot-browser-tools-guide-2026/) work in VS Code, but with more granular control. Its debug features are built around browser instrumentation rather than log files.

### Console Level Filtering

Set the console output level with `--console-level <level>` or `PLAYWRIGHT_MCP_CONSOLE_LEVEL` env var. Values: `error`, `warning`, `info`, `debug`. Each level includes all more severe levels. I keep mine at `info` during development and bump to `debug` when a page interaction silently fails.

### Output Modes

`--output-mode <mode>` controls where Playwright MCP writes its output. Two options:

- **`stdout`** (default) — Output goes to standard out. Good for local development.
- **`file`** — Writes to `--output-dir <path>`. Essential for CI/CD pipelines where stdout is ephemeral.

Set `--output-max-size <bytes>` to control when old output files get evicted. I use 50 MB for long-running test suites.

### Browser Tracing and Step Debugging

This is where Playwright MCP shines:

- **`browser_start_tracing` / `browser_stop_tracing`** — Records a full browser trace (network requests, console logs, DOM mutations). Open the trace file in `https://trace.playwright.dev` for a frame-by-frame replay of what the browser did.
- **`browser_pause` / `browser_resume`** — Pauses and resumes execution. `browser_resume` with `step=true` pauses before the next action, giving you frame-by-frame control.
- **`browser_set_debugger`** — Pauses at a specific `<file>:<line>` location. Think of it as a breakpoint for browser automation.

I use tracing when a Playwright MCP test passes locally but fails in CI. The trace replay shows exactly where the page state diverged — usually a timing issue or a missing network response.

### Headless vs. Headed

Playwright MCP runs **headed by default** (you see the browser window). For CI or headless servers, pass `--headless`. In containerized environments, you may also need `--no-sandbox` and `--ignore-https-errors` depending on your setup.

### Persistent Profiles

Session data (cookies, localStorage, IndexedDB) is stored at a platform-specific location by default. Override with `--user-data-dir` to share sessions across runs. For security-sensitive tasks, use `--isolated` to keep the profile in memory only — nothing touches disk.

## Cross-Tool Debug Patterns

After debugging all four tools in anger, here are the patterns that apply across the board:

### 1. Environment Variables Are Your First Log

Every tool in this guide respects environment variables for debug configuration. Before you open a log file, check that your env vars are set correctly. A typo in `PLAYWRIGHT_MCP_CONSOLE_LEVEL` or a missing `GITHUB_PERSONAL_ACCESS_TOKEN` will fail silently.

### 2. MCP Server Health Check

When an MCP server won't connect, the problem is almost always one of three things:
- **Port conflict** — Another process is using the port. `lsof -i :<port>` to check.
- **Auth mismatch** — The token or OAuth session expired. Re-authenticate.
- **Path issue** — The `command` in your MCP config isn't on the agent's PATH. Use absolute paths in MCP server configs.

### 3. Session Persistence Is Fragile

Both Claude Code (`--resume`) and Codex CLI (auth cache) support session persistence, but neither is bulletproof. If you're running long-lived agent sessions, build checkpointing into your workflow — commit frequently, save intermediate results, and don't trust session files as your only state.

## Which Debug Approach Fits Your Workflow?

- **Claude Code** — Best debug tooling overall. Use `/doctor` for triage, `/heapdump` for memory issues, and `/compact` for context management. If you're running Claude Code daily, learn these commands.
- **Codex CLI** — Best for config-driven debugging. The TOML config and log directory give you fine-grained control. Use when you need to debug MCP server connections or auth flows.
- **GitHub MCP Server** — Best for API-level debugging. The typed error objects and context middleware make it the most engineer-friendly MCP server to troubleshoot. Use when you're building custom MCP hosts.
- **Playwright MCP** — Best for browser-level debugging. Tracing and step debugging are unmatched for diagnosing flaky browser automation. Use when your tests pass locally but fail in CI.

The reality is that most teams will use all four. Claude Code or Codex CLI as the primary coding agent, GitHub MCP for repository operations, and Playwright MCP for browser testing. Knowing the debug patterns for each one — before they break — is what separates a smooth workflow from a frustrating afternoon of staring at a silent terminal.

## FAQ

### How do I enable verbose logging in Claude Code?

Claude Code doesn't have a traditional verbose log flag. Instead, use `/doctor` for a health check, `/compact` to inspect context usage, and `claude --safe-mode` to isolate whether a plugin or MCP server is causing issues. For memory profiling, `/heapdump` writes a Chrome-compatible heap snapshot. If you need raw output, run `claude --verbose` from the shell — it prints more detail about tool calls and API requests.

### Codex CLI logs are empty — what's wrong?

If `$CODEX_HOME/log` is empty, you probably haven't set `CODEX_HOME` explicitly. Codex only writes the plaintext TUI log (`codex-tui.log`) when `CODEX_HOME` is set as an environment variable. Without it, logs go to a default location that may not be obvious. Set `CODEX_HOME=/home/you/.codex` in your shell profile, then restart Codex. Also check that your `config.toml` has a `[logging]` section with `level = "debug"`.

### Why does my GitHub MCP server return 404 for repos I can access?

This is almost always an authentication issue, not a missing repo. If you're using a Personal Access Token, verify it has the `repo` scope. If you're using OAuth, the token may have expired — re-authenticate. For GitHub Enterprise Server, the `--gh-host` flag must include the `https://` prefix (e.g., `--gh-host https://git.yourcompany.com`). Without it, the server defaults to github.com and can't find your enterprise repos.

### Playwright MCP tests pass locally but fail in CI — how do I debug this?

Use browser tracing. Add `browser_start_tracing` before the failing interaction and `browser_stop_tracing` after it. Open the trace file in [trace.playwright.dev](https://trace.playwright.dev) for a frame-by-frame replay. The most common CI-specific issues are: headed mode not available (pass `--headless`), sandbox restrictions (pass `--no-sandbox` in containers), and missing environment variables like `PLAYWRIGHT_MCP_CONSOLE_LEVEL`. Also check that `--output-mode file` is set so logs persist after the CI job ends.

### Can I use Claude Code and Codex CLI together in the same project?

Yes, but with caveats. Both tools respect `CLAUDE.md` / project config files, but they use different formats — Claude Code uses Markdown-based CLAUDE.md, while Codex uses TOML-based `config.toml` and `requirements.toml`. They won't interfere with each other, but you'll need to maintain two config files. I run Claude Code for architecture and planning work, then switch to Codex CLI for tasks where I want the ChatGPT subscription's model access. The MCP server configs are shared — both tools read the same MCP server binaries, so you only configure GitHub MCP or Playwright MCP once.
