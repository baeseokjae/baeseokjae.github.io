---
title: "Cursor MCP v2.1 Setup: Full Tool Discovery and Server Cards Configuration"
date: 2026-05-24T00:06:13+00:00
tags: ["cursor", "mcp", "ai-tools", "developer-tools", "configuration"]
description: "Complete guide to setting up MCP servers in Cursor 2.x — Server Cards, tool discovery, mcp.json config, transport selection, and security after CVE-2025-54136."
draft: false
cover:
  image: "/images/cursor-mcp-v2-1-setup-guide-2026.png"
  alt: "Cursor MCP v2.1 Setup: Full Tool Discovery and Server Cards Configuration"
  relative: false
schema: "schema-cursor-mcp-v2-1-setup-guide-2026"
---

Cursor MCP v2.1 lets you connect AI agents to external tools — databases, GitHub, Figma, Slack — through a standardized protocol. This guide covers every setup path: Server Cards auto-discovery, the Cursor Marketplace, manual `mcp.json` configuration, transport selection, and the security changes enforced after two critical CVEs in early 2026.

## What Is MCP v2.1 and What Changed in Cursor

MCP (Model Context Protocol) v2.1 is the latest revision of Anthropic's open standard for connecting AI agents to external tools and data sources. In Cursor specifically, v2.1 arrived alongside Cursor 2.0 in late 2025 and introduced three breaking changes that affect every developer who previously configured MCP servers manually: mandatory per-tool approval by default, the Server Cards discovery format (`.well-known/mcp.json`), and first-class support for Streamable HTTP transport alongside the original stdio approach. As of Q2 2026, MCP has reached 97 million monthly downloads — a 970x increase in 18 months — and 9,400 published servers across four major registries, making proper setup hygiene more important than ever. The key behavioral shift in Cursor 2.0 is that Agent mode (Cmd+I / Ctrl+I) is now the only context where MCP tools can be invoked; Chat mode ignores them entirely. If you've been wondering why your MCP tools "disappeared," this is almost certainly why.

MCP v2.1 also formalized two concepts that were experimental in v1.x:

- **Tool annotations** — servers declare whether a tool is read-only, destructive, or idempotent, which Cursor uses to auto-apply different approval policies.
- **Server Cards** — a JSON manifest published at `/.well-known/mcp.json` that lets clients discover what a server offers without opening a live connection first.

The upstream protocol changelog matters here: v2.1 deprecated the `resources` endpoint for direct file injection (still functional but no longer recommended) and added `sampling` as a primitive — letting MCP servers request model completions from the host, not just the other way around.

## Server Cards Explained: Auto-Discovery via .well-known/mcp.json

Server Cards are MCP v2.1's answer to the "cold start" problem — the friction of connecting to a server just to find out what it does. A Server Card is a static JSON document published at `https://your-server.example.com/.well-known/mcp.json`, which registries and clients like Cursor can fetch without authenticating first. The spec requires this endpoint to be publicly accessible and cache-friendly (respond with `Cache-Control: max-age=3600` or longer). Server Cards reduce initial connection latency by 30% in environments with 100+ MCP servers by pre-fetching server capabilities before the user opens a project.

A minimal Server Card looks like this:

```json
{
  "mcpVersion": "2.1",
  "name": "github",
  "displayName": "GitHub MCP Server",
  "description": "Interact with GitHub repositories, issues, and PRs",
  "vendor": "GitHub, Inc.",
  "homepage": "https://github.com/github/github-mcp-server",
  "transport": ["streamable-http", "stdio"],
  "tools": [
    {
      "name": "search_repositories",
      "description": "Search public repositories by query",
      "annotations": { "readOnly": true }
    },
    {
      "name": "create_issue",
      "description": "Create a GitHub issue",
      "annotations": { "readOnly": false, "destructive": false }
    }
  ]
}
```

**Why Server Cards matter for Cursor users:** The Cursor Marketplace (launched February 17, 2026, with Cursor 2.5) reads Server Cards to populate the one-click install UI. When you click "Add" on a Marketplace server, Cursor fetches the `.well-known/mcp.json`, validates compatibility, and pre-fills the configuration form — including the correct transport and required environment variables. Without a Server Card, you'd do this manually.

If you're building a private MCP server for internal use, publishing a Server Card on your intranet gives your team the same zero-friction install experience. The only requirement is that the URL be reachable from Cursor at configuration time.

## Three Ways to Set Up MCP Servers in Cursor (UI, Marketplace, mcp.json)

There are three distinct setup paths in Cursor 2.x, and choosing the right one depends on your use case. The fastest path is the Marketplace (launched February 17, 2026 with Cursor 2.5), which uses Server Cards to pre-fill configuration and supports one-click install for 9,400+ published servers. The most flexible is direct `mcp.json` editing, which supports every option including custom environment variables, tool pinning, and conditional scoping per project. The Settings UI wizard falls in between — no Server Card required, but less control than direct editing. All three paths ultimately write to the same config files, so you can mix approaches freely. The key rule that catches many developers: every MCP server install requires a full Cursor quit-and-reopen — not just a settings panel reload — for the server to appear in Agent mode. The server must also show a green status dot before its tools are available.

### Option 1: Cursor Marketplace (One-Click)

Available since Cursor 2.5 (February 2026). Open **Settings → Tools & MCP → Browse Marketplace**. Find the server you want — GitHub, PostgreSQL, Figma, Slack, and hundreds more — click **Add**, fill in any required credentials, and restart Cursor. Team and Enterprise plan admins can also push servers to all org members from a Team Marketplace, eliminating per-developer setup.

The authorization flow uses color-coded status dots:
- **Green dot**: server connected, tools available in Agent mode.
- **Yellow dot**: server installed but requires OAuth / "Connect" click to complete authorization.
- **Red dot**: server failed to start — check logs via **Settings → Tools & MCP → [server name] → View Logs**.

### Option 2: Settings UI (New MCP Server Wizard)

Go to **Settings → Tools & MCP → New MCP Server**. Paste the server command or URL, give it a name, and save. Cursor writes the entry to your global `~/.cursor/mcp.json`. This is the right path for one-off personal servers that don't have a Marketplace listing yet.

### Option 3: Direct mcp.json Editing

For advanced configuration — environment variable injection, conditional scoping, pinned tool lists — edit `mcp.json` directly. The root key must be `mcpServers` (plural, camelCase); any other key causes silent failure with no error shown in the UI.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

## Configuring mcp.json: Project-Scoped vs Global and When to Use Each

Cursor supports two `mcp.json` locations with a clear precedence rule: `.cursor/mcp.json` in the project root takes priority over `~/.cursor/mcp.json` in your home directory. When the same server key appears in both files, the project-scoped version wins entirely — there is no merging. Understanding this precedence prevents subtle bugs where you update the global config but the project config silently overrides it.

**Project-scoped (`.cursor/mcp.json`)** — commit this to version control for servers that are intrinsic to the project: a PostgreSQL server pointing at the dev database, a Jira MCP pointing at the project's board, or a custom internal API. Every team member who clones the repo gets the same MCP configuration. Use `${env:VAR_NAME}` syntax for credentials so secrets stay out of git.

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${env:DATABASE_URL}"]
    }
  }
}
```

**Global (`~/.cursor/mcp.json`)** — for personal servers you use across all projects: your personal GitHub token, a local file-system server, or a dev-tools server you want available everywhere. Don't commit this file.

A practical strategy: project config handles data-layer servers (DB, APIs, git), global config handles personal productivity servers (calendar, email, note-taking). This split minimizes secrets-in-git risk and keeps project configs reviewable.

One subtle gotcha: if you add a server to the project config while Cursor is running, the server won't load until the next full restart. The UI refresh button in Settings reloads the panel display but does not actually restart server processes — only a full quit-and-reopen does.

## Enabling Full Tool Discovery in Agent Mode

Tool discovery in Cursor means the agent can see and invoke the full list of tools across all connected MCP servers. This only works in **Agent mode** — opened with Cmd+I (Mac) or Ctrl+I (Windows/Linux). In normal Chat mode, MCP tools are invisible. This is the most common source of confusion for developers new to Cursor MCP. The January 2026 dynamic context management update improved how Cursor loads tool schemas: instead of injecting all tool definitions upfront, it now fetches them on-demand, reducing token usage by 47% when using multiple servers simultaneously.

To verify tool discovery is working:

1. Open Agent mode (Cmd+I).
2. Type `@` — you should see MCP servers listed alongside files and docs.
3. Click the tools icon (wrench icon) in the agent panel — it shows all currently loaded tools.

If tools don't appear, check these in order:

- Server status dot in Settings → is it green?
- Did you restart Cursor fully (not just reload the window)?
- Is the `mcpServers` root key present and spelled correctly in your config?
- Are required environment variables set in your shell (not just in `.env` files — Cursor reads the shell environment at launch)?

**Tool pinning for faster discovery:** In the agent panel's tool list, you can pin frequently used tools so they're always in context. Unpinned tools are still available but loaded lazily. For latency-sensitive workflows, pin your five to ten most-used tools and leave the rest on-demand.

## Choosing a Transport: stdio vs Streamable HTTP

The transport layer determines how Cursor communicates with your MCP server process. Cursor v2.1 supports two transports: **stdio** (the original) and **Streamable HTTP** (formalized in v2.1). The choice is architectural — once you deploy a server, changing transports requires reconfiguring every client. Stdio achieves 10,000+ operations per second — an order of magnitude faster than HTTP-based transports under typical single-developer conditions. Streamable HTTP is slower per operation but scales to multiple concurrent clients and survives network boundaries that kill stdio pipes.

**stdio** — the server runs as a local subprocess. Cursor spawns it via `command` + `args`, communicates over stdin/stdout, and the process dies when Cursor closes. Ideal for:
- Local development tools (file system, local DB, git).
- Single-developer setups where the server doesn't need to be shared.
- Maximum throughput — no serialization overhead beyond JSON.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    }
  }
}
```

**Streamable HTTP** — the server runs as a persistent HTTP service. Cursor connects to it via URL. Ideal for:
- Team-shared servers (one instance, many Cursor clients).
- Cloud-deployed servers (authentication, audit logging, rate limiting).
- Servers that need to maintain state between calls.

```json
{
  "mcpServers": {
    "company-api": {
      "url": "https://mcp.internal.example.com/v1",
      "headers": {
        "Authorization": "Bearer ${env:MCP_API_TOKEN}"
      }
    }
  }
}
```

**Decision rule:** Use stdio for everything local and personal. Use Streamable HTTP when the server lives on a remote host, when multiple developers need to share the same server instance, or when you need centralized access control and audit logging.

## Security and Tool Approval — What Changed After CVE-2025-54136

Two CVEs in early 2026 forced significant security changes in how Cursor handles MCP tool execution. **CVE-2025-54136 (MCPoison)** demonstrated that a malicious MCP server could inject instructions into the tool description text that cause the AI agent to exfiltrate data or execute unintended commands — essentially prompt injection through the tool manifest. **CVE-2025-54135 (CurXecute)** showed that a compromised MCP server could escalate from read-only tool calls to arbitrary code execution by chaining tool calls in ways the user had approved individually. Cursor's response, shipped in Cursor 2.0, made per-tool-call approval mandatory by default and added tool annotation enforcement.

What this means in practice:

**Per-tool approval (default on):** Before Cursor runs any MCP tool call, it shows a confirmation dialog listing the tool name, server, and arguments. You approve or deny each call. This adds friction but prevents invisible exfiltration. You can disable it per-server in Settings, but only do so for servers you fully trust and control.

**Tool annotations enforcement:** If a server declares a tool as `readOnly: true` in its manifest (or Server Card), Cursor applies a more permissive approval policy — you can configure "auto-approve read-only tools" without opening up destructive actions. Only trust this if you verified the server's source code; a malicious server can lie about annotations.

**Practical security checklist:**
1. Only install MCP servers from the Cursor Marketplace or verified GitHub sources.
2. Use least-privilege credentials — give the GitHub MCP server a fine-grained PAT with only the scopes it needs.
3. Never install an MCP server that requires `command` pointing to a binary you downloaded from an untrusted source.
4. Audit your `mcp.json` files periodically — remove servers you no longer use.
5. Review tool call arguments in the approval dialog before clicking OK, especially for file-write or network-call tools.

Remember: only 12.9% of MCP servers score "high trust" (70+/100) on quality metrics covering documentation, maintenance, and reliability. Treat unknown servers as you'd treat an unknown npm package.

## Managing Tool Count: The 40-Tool Rule and Context Optimization

The single most counterintuitive truth about MCP in Cursor: more tools installed does not mean more capability. It means degraded accuracy. The recommended ceiling is approximately 40 active tools — beyond that, the agent starts picking the wrong tool because the tool list consumes too much of the context window, leaving less room for actual reasoning about the task. This isn't a Cursor-specific limitation; it's a fundamental consequence of how transformer models handle long context. The 40-tool ceiling applies to the number of *active and loaded* tools, not the number of *installed* servers.

**Strategies for staying under the ceiling:**

- **Disable servers you're not currently using.** Toggle servers on/off in Settings → Tools & MCP without deleting their config. A disabled server contributes zero tools to the context.
- **Use project-scoped config to scope activation.** A database MCP that's relevant to your backend project shouldn't be active when you're working on a frontend-only repo.
- **Pin only essential tools.** Unpinned tools are loaded lazily on demand, which means they don't count toward the upfront context load.
- **Prefer servers with fewer, well-scoped tools** over servers that expose dozens of operations. A GitHub server with 8 tools beats one with 40.
- **Use the tool filter in Agent mode.** Click the wrench icon → "Filter tools" → deselect categories you won't use in this session.

The January 2026 dynamic context management update helped significantly: Cursor now injects tool schemas only when the agent determines a tool is relevant to the current step, rather than all at once. The 47% token reduction this produced is most visible in sessions that span multiple servers — a typical scenario when using GitHub + Postgres + Slack simultaneously.

## Troubleshooting: Common MCP Setup Failures in Cursor

Most MCP setup failures in Cursor fall into five categories, and knowing which one you're hitting saves significant debugging time. The most common cause of "my tools disappeared" is switching from Agent mode to Chat mode — MCP tools are Agent-mode-only and will never appear in Chat. The second most common is forgetting to restart Cursor after editing `mcp.json`.

**"Server not found" / red dot immediately after setup:**
- Check the `command` path is on your `PATH` as seen by Cursor (not just your terminal). Cursor uses the environment it inherited at launch, which may differ from your interactive shell. Fix by adding the full absolute path to the command, or launching Cursor from a terminal with the correct environment.
- Verify Node.js / Python / whatever runtime the server needs is installed and accessible.
- Check **Settings → Tools & MCP → [server name] → View Logs** for the actual error message.

**Silent failure — server installed, no tools appear:**
- The most common cause: the root key in `mcp.json` is `mcpServer` (singular) instead of `mcpServers` (plural). Cursor silently ignores incorrectly keyed configs.
- Another common cause: the project-scoped `.cursor/mcp.json` is overriding the global config with a different or empty server list.

**Yellow dot / authorization stuck:**
- Click the yellow dot or the "Connect" button in the server entry — some servers require completing an OAuth flow before they'll turn green.
- For HTTP transport servers, verify the URL is reachable from Cursor's network context (not just your browser).

**Tools available but agent ignores them:**
- Confirm you're in Agent mode (Cmd+I), not Chat.
- Check if per-tool approval is blocking calls — the approval dialog may have appeared and timed out without you seeing it.
- Check total active tool count — if you're over ~40, the agent may be ignoring some tools due to context pressure.

**Environment variables not resolved:**
- Cursor resolves `${env:VAR}` at launch time, not at runtime. If you added an env var after launching Cursor, restart Cursor.
- For `.env` files: Cursor does not automatically read `.env` files. You must set variables in your shell before launching, or use a Cursor extension that injects `.env` into the process environment.

## FAQ

**What is MCP v2.1 and how is it different from v1.x in Cursor?**
MCP v2.1 adds Server Cards (`.well-known/mcp.json` discovery), mandatory tool annotations, Streamable HTTP transport as a first-class option, and a `sampling` primitive for server-to-model requests. In Cursor specifically, v2.1 arrived with Cursor 2.0 and enforced per-tool-call approval by default following two security CVEs. If you configured MCP in Cursor 1.x, your `mcp.json` files are still valid — you just need to add the `mcpServers` root key if it's missing.

**Why can't I see my MCP tools in Cursor?**
MCP tools only appear in Agent mode (Cmd+I or Ctrl+I). They are completely invisible in normal Chat mode. If you're already in Agent mode and tools still don't appear, restart Cursor fully (not just reload the window), check that the server status dot is green in Settings → Tools & MCP, and verify the `mcpServers` root key is spelled correctly in your config file.

**Should I use stdio or Streamable HTTP transport?**
Use stdio for local servers — it's an order of magnitude faster and simpler to configure. Use Streamable HTTP when the server runs on a remote host, when multiple team members need to share the same server instance, or when you need centralized access control. You can't easily switch later, so decide based on where the server will live, not just current convenience.

**How do I stay under the 40-tool limit without losing functionality?**
Disable servers you're not actively using via the toggle in Settings → Tools & MCP — disabled servers contribute zero tools. Use project-scoped `.cursor/mcp.json` to auto-scope which servers are active per project. Use the Agent mode tool filter to deselect tool categories you won't use in a given session. Prefer servers with narrow, well-scoped tool sets.

**Is the Cursor Marketplace safe to use?**
The Marketplace lists servers that have been reviewed by the Cursor team, which provides a baseline of safety — but "listed" is not the same as "audited." Always check the server's GitHub repo, review the permissions it requests, and use least-privilege credentials (fine-grained PATs with only necessary scopes). Only 12.9% of MCP servers across all registries meet "high trust" quality thresholds, so treat even Marketplace servers with appropriate skepticism until you've reviewed what they do.
