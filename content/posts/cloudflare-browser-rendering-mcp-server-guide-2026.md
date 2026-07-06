---
title: "Cloudflare Browser Rendering MCP Server Guide 2026: Screenshots, Crawls, and Web Data for Agents"
date: 2026-07-06T00:00:00+00:00
tags: ["cloudflare", "mcp", "browser-automation", "ai-agents", "web-scraping"]
description: "Practical guide to Cloudflare's Browser Rendering MCP server — setup for Claude Code, Cursor, and OpenCode, with real workflows for screenshots, Markdown, crawls, and structured data extraction."
cover:
  alt: "Cloudflare Browser Rendering MCP Server Guide 2026"
  image: /images/cloudflare-browser-rendering-mcp-server-guide-2026.png
  relative: false
---

If your AI coding agent needs to read a web page, take a screenshot, or crawl a site, you have two options: run a local browser stack (Playwright, Puppeteer) or call a hosted browser API. Cloudflare's Browser Rendering MCP server splits the difference — it gives you a managed browser in the cloud, exposed as MCP tools your agent can call directly.

I've been testing all three Cloudflare browser paths — the official Browser Rendering MCP server, the `@cloudflare/playwright-mcp` Worker, and the CDP-based `chrome-devtools-mcp` setup — across Claude Code, Cursor, and OpenCode. Here's what works, what doesn't, and how to pick the right path.

## What the Browser Rendering MCP Server Actually Does

Cloudflare announced 13 remote MCP servers on May 1, 2025, and the Browser Rendering server is the one that handles web page interaction. It wraps Cloudflare's [Browser Run](https://developers.cloudflare.com/browser-run/) REST API into MCP tools your agent can call without writing HTTP requests.

The tool surface covers the jobs you'd expect:

- **Screenshots** — full-page or viewport captures of any URL
- **Markdown conversion** — rendered page content as clean Markdown
- **HTML extraction** — raw rendered HTML
- **JSON extraction** — AI-assisted structured data from pages
- **Link discovery** — all links on a page
- **PDF rendering** — page as PDF
- **Element scraping** — specific CSS selector targets
- **Snapshots** — accessibility-tree snapshots for LLM consumption
- **Crawl** — multi-page crawl jobs

The key difference from running Playwright locally: you don't manage browser binaries, session state, or network egress. Cloudflare handles the Chromium instance in their edge network. Your agent just calls `take_screenshot` or `crawl` and gets back the result.

## Three Paths, One Browser Run

Cloudflare offers three ways to connect your agent to Browser Run. They're not interchangeable — each serves a different workflow.

### Path 1: Official Browser Rendering MCP Server

This is the simplest path. Cloudflare hosts the MCP server, you configure your MCP client with your API token, and you're done. The server exposes tools like `browser_render_content`, `browser_take_screenshot`, and `browser_crawl`.

**Best for:** Quick setup, standard web data workflows, teams that don't want to maintain a custom Worker.

### Path 2: `@cloudflare/playwright-mcp` Worker

This deploys a Playwright-based MCP server as a Cloudflare Worker with Browser Run and Durable Object bindings. You get 23 tools instead of the official server's subset — full Playwright control including click, type, navigation, and accessibility-tree snapshots.

The Worker exposes both `/sse` and `/mcp` endpoints. After deployment, you can test it in Cloudflare AI Playground before wiring it to your agent.

**Best for:** Teams that need full browser automation (click, type, form fill) rather than just extraction. The accessibility-tree snapshots are faster and more deterministic than screenshot-only loops for many LLM workflows.

### Path 3: CDP via `chrome-devtools-mcp`

This connects `chrome-devtools-mcp` directly to Cloudflare's CDP WebSocket endpoint at `wss://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/browser-rendering/devtools/browser`. You get raw Chrome DevTools Protocol access — the same protocol Chrome DevTools uses.

**Best for:** Debugging, persistent browser sessions, and workflows where you need to inspect network requests, console output, or DOM state over time.

## Prerequisites

All three paths share the same prerequisites:

- A Cloudflare account with **Browser Run** enabled
- A **Browser Rendering API token** with at least `browser_rendering:edit` permission
- Node.js v20.19 or newer (for the Playwright MCP and CDP paths)
- An MCP-compatible client (Claude Desktop, Claude Code, Cursor, OpenCode)

The API token scope matters. If your token only has `read` permissions, screenshot and crawl tools will fail silently. I spent 20 minutes debugging a 403 before realizing I'd generated the wrong token type.

## Quick Setup for Claude Code, Cursor, and OpenCode

Here's the configuration for each client using the official Browser Rendering MCP server:

### Claude Code

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cloudflare-browser": {
      "command": "npx",
      "args": ["@cloudflare/mcp-server-browser-rendering"],
      "env": {
        "CLOUDFLARE_API_TOKEN": "your-token-here",
        "CLOUDFLARE_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

### Cursor

In Cursor settings → MCP Servers, add:

```json
{
  "name": "cloudflare-browser",
  "type": "command",
  "command": "npx @cloudflare/mcp-server-browser-rendering",
  "env": {
    "CLOUDFLARE_API_TOKEN": "your-token-here",
    "CLOUDFLARE_ACCOUNT_ID": "your-account-id"
  }
}
```

### OpenCode

In `~/.opencode/config.yaml`:

```yaml
mcpServers:
  cloudflare-browser:
    command: npx
    args: ["@cloudflare/mcp-server-browser-rendering"]
    env:
      CLOUDFLARE_API_TOKEN: your-token-here
      CLOUDFLARE_ACCOUNT_ID: your-account-id
```

For the Playwright MCP path, you deploy a Worker first, then point your client at the Worker's `/sse` endpoint. The [Cloudflare docs](https://developers.cloudflare.com/browser-run/playwright/playwright-mcp/) have the full Wrangler config and deploy command.

## Core Tools and Workflows

### Screenshots

The most straightforward use case. Your agent calls `browser_take_screenshot` with a URL and gets back a screenshot URL valid for a limited time. I use this for:

- **QA workflows** — my agent deploys a preview, takes a screenshot, and checks visual regressions
- **Documentation capture** — snapshot docs pages before and after changes
- **Competitor monitoring** — periodic screenshot capture of competitor landing pages

The screenshot tool accepts viewport dimensions, full-page vs viewport-only, and optional wait-for-selector timing. Without a wait, you'll get blank screenshots on slow-loading SPAs.

### Markdown Conversion

`browser_render_content` with format `markdown` returns the page as clean Markdown. This is my most-used tool. It strips navigation, ads, and boilerplate better than most standalone Markdown converters I've tried.

The output is good enough to feed directly into an LLM context window. I've used it to:

- Feed documentation pages into Claude Code for code generation
- Extract blog post content for analysis
- Convert API docs into structured reference material

### Crawl Jobs

The `browser_crawl` tool accepts a starting URL and optional depth/max-pages parameters. It returns an array of crawled pages with their content. This is useful for:

- **Site mapping** — discover all pages under a path
- **Bulk content extraction** — grab all documentation pages at once
- **Link auditing** — find broken links across a site

The crawl respects `robots.txt` and has a configurable rate limit. I've found depth-1 crawls on medium-sized docs sites (50-100 pages) complete in 30-60 seconds.

### JSON Extraction

This is the hidden gem. `browser_extract_json` takes a URL and a JSON schema, and returns structured data extracted from the page using AI. For example, you can pass a schema for product listings and get back an array of product objects.

It's not perfect — complex schemas with nested arrays sometimes return partial results — but for simple extraction jobs it saves writing a custom parser.

## Example: Research Agent Workflow

Here's a real workflow I run regularly. My agent needs to research a competitor's pricing page, extract the plan tiers, and compare them against our pricing:

1. Call `browser_take_screenshot` on the pricing page for visual reference
2. Call `browser_render_content` with format `markdown` to get the text
3. Call `browser_extract_json` with a schema for plan name, price, features
4. Feed the results into a comparison table generation prompt

The whole pipeline takes about 15 seconds and produces a draft I can review. Without the MCP server, I'd be writing a Playwright script, running it, parsing the output, and formatting it — 15 minutes instead of 15 seconds.

## Security and Operational Considerations

**Token permissions.** Your API token needs `browser_rendering:edit` for most tools. The `read` scope only covers status checks. Store tokens in your MCP client's env config, not in shared config files.

**Session lifetime.** Browser Run sessions have a timeout. The official MCP server handles session creation and teardown automatically, but the Playwright MCP Worker's Durable Object sessions can persist longer. If you're running long crawl jobs, the Playwright MCP path is more reliable.

**Pricing.** Browser Run charges per rendering request. Screenshots and Markdown conversion count as one request each. Crawl jobs count each page as a separate request. At scale, the costs add up — check the [pricing page](https://developers.cloudflare.com/browser-run/pricing/) before building a high-volume pipeline.

**Rate limits.** The free tier has a per-account rate limit. If you're running multiple agents concurrently, you'll hit 429 responses. The official MCP server doesn't retry automatically — your agent needs to handle rate-limit errors and back off.

## When to Use Cloudflare Browser Run vs Local Playwright

Cloudflare's hosted browser is great when:

- You don't want to manage browser binaries and dependencies
- Your agent runs in a serverless or containerized environment without a display server
- You need occasional screenshots or page reads, not continuous browser sessions
- You want accessibility-tree snapshots without running a full browser locally

Local Playwright or Puppeteer is better when:

- You need persistent browser sessions (logged-in state, WebSocket connections)
- You're doing high-volume scraping (Cloudflare costs exceed local compute)
- You need to test against specific browser versions or device emulations
- Your workflow involves complex user interactions (multi-step forms, drag-and-drop)

For most AI coding agent workflows — reading docs, capturing screenshots, extracting structured data — the Cloudflare MCP server is the faster path. For anything that needs a real user session or runs at scale, go local.

## Troubleshooting Common Issues

**"Tool not found"** — Your MCP client version might not support the tool. Update to the latest version of Claude Code or Cursor. The official server requires MCP v2.1 or newer.

**Blank screenshots** — The page didn't finish loading before the screenshot was taken. Add a `wait_until` parameter or increase the timeout. SPAs are the most common culprit.

**403 on all requests** — Your API token has the wrong permissions. Regenerate it with `browser_rendering:edit` scope. The `read` scope looks like it works (no auth error) but returns empty results.

**Crawl returns one page** — The crawl depth parameter defaults to 0 (current page only). Set `max_depth: 1` or higher for multi-page crawls.

**WebSocket disconnects** — The CDP path has a session timeout. Set the `keep_alive` parameter or re-establish the connection. The Playwright MCP Worker's Durable Object handles reconnection better than the raw CDP path.

## The Bottom Line

Cloudflare's Browser Rendering MCP server is the fastest way to give your AI coding agent web access without running a browser stack. The official server covers 80% of use cases with zero infrastructure. The Playwright MCP Worker covers the remaining 20% with full browser automation. The CDP path is for debugging and specialized workflows.

For a broader look at the MCP server ecosystem, check out my [best MCP servers for developers](/posts/best-mcp-servers-for-developers-2026/) guide. If you're evaluating browser automation tools more broadly, the [AI browser agents comparison](/posts/ai-browser-agents-comparison-2026/) covers alternatives like Browser Use, Stagehand, and Playwright MCP. And for the full Cloudflare agent infrastructure picture, [Cloudflare Agents Week 2026](/posts/cloudflare-agents-week-2026/) covers Dynamic Workers, sandboxes, and Project Think.

Start with the official MCP server. If you hit its limits, deploy the Playwright MCP Worker. You'll have a working browser agent in under 30 minutes either way.
