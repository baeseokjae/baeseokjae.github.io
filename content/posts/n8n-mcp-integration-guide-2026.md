---
cover:
  alt: 'n8n MCP Integration Guide 2026: Connect Claude and AI Agents to Your Workflows'
  image: /images/n8n-mcp-integration-guide-2026.png
  relative: false
date: 2026-05-04 15:04:58+00:00
description: How to integrate n8n with Model Context Protocol (MCP) in 2026 — set
  up n8n as an MCP server, connect Claude Desktop, and build workflows without touchi...
draft: false
schema: schema-n8n-mcp-integration-guide-2026
tags:
- n8n
- MCP
- AI Agents
- Claude
- workflow-automation
title: 'n8n MCP Integration Guide 2026: Connect Claude and AI Agents to Your Workflows'
---

n8n MCP integration lets you expose your n8n workflows as tools that Claude, Cursor, and other AI agents can call directly — and lets n8n workflows consume external MCP servers like GitHub, Slack, or any tool that speaks the Model Context Protocol. The result: AI agents that can actually trigger automation, not just describe it.

## What Is n8n MCP Integration and Why It Matters in 2026

n8n MCP integration refers to connecting n8n's workflow automation platform with the Model Context Protocol (MCP), an open standard that lets AI assistants like Claude discover and invoke external tools at runtime. Rather than hardcoding API calls inside a chat model, MCP creates a structured bridge: the AI agent asks "what tools are available?" and then calls them with real parameters. With n8n's native MCP support — shipped as the MCP Server Trigger node and MCP Client Tool node — any n8n workflow becomes a first-class tool that Claude Desktop, Cursor, or any MCP-compatible AI client can discover and invoke. This matters because n8n already connects to 1,650 services via its node library; with MCP, that library becomes natively accessible to AI coding assistants. As of 2026, n8n has surpassed 230,000 active users and raised $180M at a $2.5B valuation, signaling that AI-native automation is the dominant growth vector. Gartner projects 40% of enterprise applications will embed task-specific AI agents by end of 2026, up from under 5% in 2025 — and n8n MCP is a direct path to that outcome.

## Two Modes of n8n MCP Integration Explained

n8n MCP integration operates in two distinct directions, and understanding both is essential before you touch any configuration. Mode 1 turns n8n into an MCP server — your workflows become discoverable tools that external AI agents can invoke by calling a standard HTTP endpoint. Mode 2 does the reverse — n8n acts as an MCP client, pulling in tools from external MCP servers (GitHub, Slack, Elasticsearch, etc.) and making them available to an AI Agent node inside your workflow. Most real deployments use both simultaneously: Claude orchestrates high-level tasks via Mode 1, but the n8n workflow itself calls out to other services via Mode 2. For example, Claude might invoke an n8n "research" workflow (Mode 1) that internally consults a Perplexity MCP server for live search results (Mode 2). Knowing which mode solves your specific problem saves hours of debugging the wrong node configuration. Mode 1 is configured via the MCP Server Trigger node; Mode 2 is configured via the MCP Client Tool node inside an AI Agent workflow.

### Mode 1 — n8n as MCP Server (Expose Your Workflows to AI Agents)

When n8n acts as an MCP server, you add an **MCP Server Trigger** node to a workflow. That node registers the workflow as a named tool — complete with a description and parameter schema — at an HTTP endpoint. Any MCP-compatible AI client (Claude Desktop, Cursor, VS Code Copilot, a custom agent) can then call `tools/list` to discover the tool and `tools/call` to invoke it. The trigger fires the rest of the workflow with the AI's parameters as input. This is the pattern that lets you say to Claude: "Book a meeting for me tomorrow at 2pm" and have Claude actually call your n8n calendar workflow, not just generate code for it.

### Mode 2 — n8n as MCP Client (Consume External MCP Servers in Workflows)

When n8n acts as an MCP client, an **AI Agent** node inside your workflow uses the **MCP Client Tool** node as one of its tool sources. You point the MCP Client Tool node at any external MCP server's SSE or HTTP Streamable endpoint, and the AI Agent node sees those remote tools as if they were native n8n tools. A practical example: connect your n8n AI Agent to an Elasticsearch MCP server, and your workflow can perform semantic search against a production index without writing a single Elasticsearch API call manually.

## Prerequisites: What You Need Before You Start

Before configuring n8n MCP integration, verify you have the following in place. A clear checklist prevents the most common setup failures.

**n8n instance requirements:**
- n8n version 1.68 or later (MCP Server Trigger and MCP Client Tool nodes require this)
- For self-hosted: a publicly reachable HTTPS URL (MCP clients need to reach your server; `http://localhost` will not work from Claude Desktop on another machine)
- For n8n Cloud: your workspace URL works out of the box

**AI client requirements:**
- Claude Desktop (mac or Windows) for testing MCP server mode
- Node.js 18+ installed on the machine running Claude Desktop (needed for `mcp-remote` proxy)
- Or: Cursor, VS Code with Claude, or any MCP-compatible client

**Optional but recommended:**
- An API key or bearer token for securing your MCP endpoints
- A reverse proxy (Nginx, Caddy, or Cloudflare Access) if exposing self-hosted n8n to the internet

## Step-by-Step: Setting Up n8n as an MCP Server

Setting up n8n as an MCP server means configuring the MCP Server Trigger node so that Claude or another AI client can discover and call your workflows as named tools. The MCP Server Trigger node is the entry point of any n8n workflow you want to expose — it registers a tool name, description, and parameter schema at an HTTPS endpoint, then fires the rest of the workflow when an AI client calls that tool. Each workflow becomes one MCP tool; if you want to expose five tools, you create five workflows each with their own MCP Server Trigger. The test URL is available while the workflow editor is open, but for real AI client usage you must activate the workflow so the production URL is live. This section walks through the complete setup for a single workflow tool, from adding the trigger node to verifying the endpoint responds correctly to a manual HTTP test. Follow the steps in order — skipping authentication is the most common cause of production incidents with MCP deployments.

### Adding the MCP Server Trigger Node

Open an existing workflow or create a new one in n8n. Delete or bypass any existing trigger node — MCP Server Trigger must be the workflow's entry point.

1. Click **Add first step** and search for **MCP Server Trigger**
2. In the node settings, set **Tool Name** to a short, descriptive name (e.g., `send_slack_message`). This is what Claude sees in its `tools/list` response.
3. Set **Tool Description** to a plain-English sentence explaining when to call this tool. Claude uses this to decide whether to invoke the tool.
4. Add **Parameters** for any inputs the tool needs (e.g., `channel: string`, `message: string`). These become the MCP tool's JSON schema.

### Connecting Tool Nodes to Your MCP Server

After the MCP Server Trigger, connect whatever workflow logic you need — HTTP Request, Slack, Gmail, Code, etc. The trigger node's output passes the AI's parameter values as `$json` fields to the next node. Reference them with `{{ $json.channel }}` or similar.

At the end of the workflow, return a response. The MCP Server Trigger node automatically packages the last node's output as the tool's response to the AI client.

### Configuring Authentication

In the MCP Server Trigger node, select an **Authentication** method:

| Method | When to use |
|---|---|
| None | Local dev only — never expose unauthenticated endpoints to the internet |
| Bearer Token | Simple production setup — paste a secret token in Claude's config |
| Generic Header | When your client sends a custom header (e.g., `X-API-Key`) |
| OAuth2 | Enterprise setups with existing OAuth2 infrastructure |

For most solo developers, **Bearer Token** is the right call. Generate a random 32+ character string and store it in n8n's credentials manager, not in the workflow itself.

### Getting Your MCP Endpoint URL

n8n generates two URLs for every MCP Server Trigger node:

- **Test URL**: `https://your-n8n-instance/webhook-test/{id}/mcp` — fires only while the workflow editor is open. Use this to test from Claude Desktop before activating.
- **Production URL**: `https://your-n8n-instance/webhook/{id}/mcp` — fires when the workflow is activated (toggle in the top-right of the workflow editor).

n8n supports two transport protocols:
- **HTTP Streamable** (recommended for new integrations): append `/mcp` to the base URL
- **SSE** (legacy, still supported): append `/sse` to the base URL

Use HTTP Streamable when possible — it handles reconnections and multiplexing more reliably than SSE.

## Connecting Claude Desktop to Your n8n MCP Server

Connecting Claude Desktop to n8n requires a proxy layer because Claude Desktop uses stdio transport internally, but n8n's MCP Server Trigger uses HTTP over SSE or HTTP Streamable. The `mcp-remote` npm package bridges the gap — it runs as a local subprocess that Claude Desktop spawns on startup, accepts stdio commands from Claude, and forwards them as HTTP requests to your n8n endpoint. Without `mcp-remote`, Claude Desktop cannot connect to any remote HTTP MCP server, including n8n. The package is configured entirely through Claude Desktop's `claude_desktop_config.json` file — you specify the `npx mcp-remote` command, the n8n endpoint URL, and any authentication headers. Once configured, Claude Desktop restarts and shows a hammer icon in the interface, confirming that MCP tools are loaded. The tools remain available for the entire Claude Desktop session without re-authentication. This section covers the installation, configuration, and initial test cycle for connecting Claude Desktop to an n8n workflow endpoint you set up in the previous section.

### Installing and Configuring mcp-remote Proxy

On the machine running Claude Desktop, run:

```bash
npm install -g mcp-remote
```

Verify installation:

```bash
npx mcp-remote --version
```

`mcp-remote` acts as a local stdio server that forwards requests to a remote HTTP or SSE endpoint. You don't need to start it manually — Claude Desktop spawns it on startup.

### Adding n8n to Claude Desktop's Connector Settings

Open Claude Desktop's configuration file. On macOS:

```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

On Windows:

```
%APPDATA%\Claude\claude_desktop_config.json
```

Add your n8n workflow as an MCP server entry:

```json
{
  "mcpServers": {
    "n8n-workflows": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-n8n-instance/webhook/your-workflow-id/mcp",
        "--header",
        "Authorization: Bearer YOUR_SECRET_TOKEN"
      ]
    }
  }
}
```

Replace `your-n8n-instance` with your actual n8n URL and `YOUR_SECRET_TOKEN` with the bearer token you configured in n8n.

### Testing the Connection

1. Restart Claude Desktop completely (quit and reopen — reload is not enough)
2. In a new conversation, type: "What tools do you have available?"
3. Claude should list your n8n workflow tool by name and description
4. Test an invocation: ask Claude to call the tool with specific parameters
5. Verify the workflow executed in n8n's execution log

If Claude doesn't see the tool, check: (a) the workflow is **activated** in n8n, (b) the URL uses the production endpoint (not test), and (c) the bearer token matches exactly.

## Using the czlonkowski/n8n-mcp Package: Build Workflows via Claude Without the UI

The `czlonkowski/n8n-mcp` npm package is a separate tool from n8n's native MCP nodes — it gives Claude direct access to n8n's internal API so you can describe a workflow and have Claude build, validate, and deploy it without opening the n8n UI. This is fundamentally different from the MCP Server Trigger and MCP Client Tool nodes: those let you invoke existing workflows via MCP; this package lets you create new workflows through conversation. The package exposes all 1,650 n8n nodes (820 core + 830 community) with 99% node property coverage, 63.6% operation coverage, and 87% documentation coverage — synced with n8n releases within 48 hours. Early adopters report building n8n workflows 10x–20x faster with fewer configuration errors compared to manual UI work, because Claude knows exact node names, parameter schemas, and valid operation values instead of guessing from outdated training data. Use this package when you want to build new workflows from scratch using natural language; use the native MCP nodes when you want to invoke existing deployed workflows from external AI clients.

### Installation and Configuration

```bash
npm install -g @czlonkowski/n8n-mcp
```

Add it to Claude Desktop's config:

```json
{
  "mcpServers": {
    "n8n-builder": {
      "command": "npx",
      "args": ["@czlonkowski/n8n-mcp"],
      "env": {
        "N8N_URL": "https://your-n8n-instance",
        "N8N_API_KEY": "your-n8n-api-key"
      }
    }
  }
}
```

Get your n8n API key from **Settings → API → Create API Key** in the n8n UI.

### Giving Claude Knowledge of All 1,650 n8n Nodes

Once configured, Claude can answer questions like "which n8n nodes support OAuth2?" or generate a full workflow JSON from a plain-English description. The package loads node schemas on demand, so Claude doesn't hallucinate node names or parameter keys. A typical workflow-building session looks like:

> "Build me an n8n workflow that listens for a new GitHub issue, runs it through Claude to generate a triage label, then posts the label back to the issue via the GitHub API."

Claude returns a deployable workflow JSON you can import directly into n8n — no drag-and-drop required.

## Step-by-Step: Using n8n as an MCP Client

n8n acting as an MCP client means your n8n workflow can consume tools from external MCP servers — GitHub, Slack, Elasticsearch, or any service that exposes an MCP endpoint. The AI Agent node in n8n orchestrates the reasoning loop; the MCP Client Tool node provides the external tool connections by fetching the tool list from a remote server and making those tools available to the agent. This is the "inbound MCP" pattern: instead of Claude calling n8n, n8n calls external MCP servers to enrich its own AI Agent workflows. A practical example is connecting your n8n incident-response workflow to a Grafana MCP server — the AI Agent can query live metrics without you writing a single Grafana API call. MCP Client Tool supports both SSE and HTTP Streamable transports, and authentication is configured per-connection via n8n's credentials manager. You can connect multiple MCP Client Tool nodes to a single AI Agent, giving it tools from several external servers simultaneously. This section walks through a complete MCP client setup from creating the workflow to validating that the external tools appear in the agent's reasoning trace.

### Adding the MCP Client Tool Node to Your AI Agent Workflow

1. Create a workflow with a **trigger** (Chat Trigger, Webhook, Schedule, or manual)
2. Add an **AI Agent** node
3. In the AI Agent node, configure the **Language Model** (e.g., connect to OpenAI or Anthropic via n8n credentials)
4. In the **Tools** section of the AI Agent node, click **Add Tool** → **MCP Client Tool**

### Configuring SSE or HTTP Streamable Endpoint

In the MCP Client Tool node:

- **Connection Type**: Select **HTTP Streamable** for modern servers, **SSE** for legacy ones
- **SSE Endpoint** / **HTTP Streamable URL**: Paste the full URL of the external MCP server
- **Authentication**: Configure as required by the external server (Bearer Token is most common)

For public MCP servers, check their documentation for the endpoint URL. For a self-hosted GitHub MCP server:

```
https://your-github-mcp-server/sse
```

### Selecting Which Tools to Expose

The MCP Client Tool node fetches the tool list from the remote server at workflow execution time. In **Tools to Include**, you can:

- Select **All Tools** to expose everything the remote server offers
- Select **Specific Tools** and list tool names to limit exposure (recommended for production — principle of least privilege)

Limiting tools also speeds up the AI Agent node's reasoning loop — fewer tools means fewer tokens spent on tool selection.

## Real-World Use Cases and Workflow Examples

n8n MCP integration opens practical automation patterns that neither pure n8n nor pure AI could handle alone — the combination gives you AI reasoning applied to real integrations, with n8n handling authentication, rate-limiting, error handling, and execution history. The following three use cases represent real deployment patterns observed in production, not theoretical ones. Each example maps to a specific architecture: MCP tools exposed from n8n (Mode 1), MCP client tools consumed inside n8n AI Agent workflows (Mode 2), or both simultaneously in a multi-agent chain. Delivery Hero's deployment of n8n for IT operations automation saves 200+ hours of manual work monthly via a single well-designed workflow — that scale is achievable precisely because n8n handles the integration complexity while Claude handles the decision-making. Vodafone's security threat intelligence automation using n8n saves approximately £2.2M in annual operational costs. These numbers aren't marketing — they reflect what happens when AI reasoning is paired with reliable, observable automation infrastructure rather than fragile custom glue code.

### AI-Powered Customer Support Pipeline

A support team at a SaaS company exposes three n8n workflows as MCP tools: `search_knowledge_base`, `create_zendesk_ticket`, and `escalate_to_human`. Claude Desktop is configured with these tools. When a support agent types a customer issue into Claude, it automatically searches the knowledge base, drafts a resolution, creates a Zendesk ticket with the resolution pre-filled, and flags for human review if confidence is low — all in one conversation turn. The n8n workflows handle the API authentication, rate limiting, and error handling; Claude handles the reasoning. Delivery Hero-style deployments like this save 200+ hours of manual work monthly via a single well-designed workflow chain.

### Automated Incident Response with Claude + n8n

An ops team builds an incident response workflow where n8n listens for PagerDuty alerts via webhook, passes the alert details to a Claude-powered AI Agent node, and uses MCP Client Tool nodes to query a Grafana MCP server for relevant metrics and a GitHub MCP server for recent deploys. The AI Agent generates a preliminary root-cause hypothesis and posts it to the incident Slack channel within 30 seconds of the alert firing — before any human is paged. Vodafone uses a similar pattern for security threat intelligence, saving approximately £2.2M in operational costs annually.

### Multi-Agent Orchestration: Claude as Orchestrator, n8n Workflows as Tools

The most powerful pattern: Claude acts as the central orchestrator, and each n8n workflow is a specialized sub-agent exposed via MCP. A "research" workflow scrapes and summarizes URLs. A "draft" workflow writes structured content. A "publish" workflow posts to a CMS. Claude coordinates them in sequence based on a high-level instruction like "write and publish a summary of today's top AI news." This is the architecture behind fully autonomous content pipelines — the pattern that reduces human touch to a single input prompt and a final review.

## Security Best Practices for Production MCP Deployments

Security is non-negotiable when exposing n8n workflows to external AI clients over HTTP. An unsecured MCP endpoint is effectively an unauthenticated API that can trigger your workflows. The following practices form a production-ready baseline.

**Authentication — always required:**
- Use Bearer Token or OAuth2 authentication on every MCP Server Trigger node
- Rotate tokens quarterly or after any suspected compromise
- Store tokens in n8n's built-in credentials manager, never hardcoded in workflow JSON

**Network-level controls:**
- Self-hosted n8n: put a reverse proxy (Nginx, Caddy) in front of n8n and terminate TLS at the proxy
- Use Cloudflare Access to add a second authentication layer for sensitive workflows
- Restrict inbound traffic to known IP ranges if your AI client has a fixed egress IP

**Principle of least privilege:**
- Create one workflow per tool, not one monolithic workflow with branching
- Each workflow should do exactly one thing — easier to audit, easier to disable independently
- Use n8n's execution log to monitor for unexpected invocations

**Input validation:**
- Validate all parameters passed by the AI client inside the workflow, not just at the MCP layer
- Use n8n's Code node to sanitize inputs before passing them to downstream HTTP Request or database nodes
- Never pass AI-generated parameters directly to a SQL query or shell command without sanitization

| Threat | Mitigation |
|---|---|
| Unauthorized invocations | Bearer token + IP allowlist |
| Prompt injection via tool parameters | Input sanitization in Code node |
| Overprivileged workflows | One workflow per tool, least-privilege credentials |
| Plaintext credentials in workflow JSON | n8n credentials manager only |
| Public test URL exposure | Activate workflows before sharing production URL |

## n8n MCP vs Competitors: Zapier, Make.com, and Native Claude Tool Use

Choosing between n8n MCP, Zapier AI Actions, Make.com, and native Claude tool use depends on your scale, budget, and control requirements. n8n's execution-based pricing delivers 40–60% cost savings vs. Zapier's task-based model when running AI agent workflows at scale — a workflow that calls 10 tools per run costs one execution in n8n, but 10 tasks in Zapier.

| Capability | n8n MCP | Zapier AI Actions | Make.com | Native Claude Tools |
|---|---|---|---|---|
| MCP protocol support | Native (Server Trigger + Client Tool nodes) | Via Zapier MCP connector | Limited, via webhooks | N/A — custom tool definitions |
| Self-hosting | Yes (full control) | No | No | N/A |
| Node/integration count | 1,650+ | 6,000+ | 1,500+ | Unlimited (custom) |
| Pricing model | Execution-based (cheaper at scale) | Task-based (expensive at scale) | Operation-based | API tokens only |
| AI workflow building via Claude | Yes (czlonkowski/n8n-mcp) | No | No | Not applicable |
| Security controls | Full (reverse proxy, OAuth2, IP allowlist) | Limited | Limited | Full |
| Latency | Low (self-hosted) | Medium (SaaS) | Medium (SaaS) | Low (direct API) |

Native Claude tool use (defining tools directly in the Anthropic API `tools` array) gives maximum control and lowest latency but requires custom code for every integration. n8n MCP gives you 1,650 integrations pre-built, with visual debugging and execution logs — the right tradeoff for most production deployments.

## Troubleshooting Common n8n MCP Issues

n8n MCP integration fails in predictable ways. These are the five most common issues and their fixes.

**Issue: Claude doesn't list the tool after restart**

Check: Is the workflow **activated** (the toggle in the workflow editor)? The test URL only works while the editor is open. Claude Desktop needs the production URL (`/webhook/`, not `/webhook-test/`).

**Issue: "Connection refused" when mcp-remote starts**

Check: Is your n8n instance reachable at the URL in the config? Test with `curl https://your-n8n-instance/webhook/your-id/mcp` from the machine running Claude Desktop. Firewall rules and VPN configurations are the most common culprits.

**Issue: Authentication failed (401)**

Check: The bearer token in Claude Desktop's config must match exactly what's in n8n's credential. Token comparison is case-sensitive. Re-copy both values to eliminate whitespace issues.

**Issue: Tool call succeeds but returns empty data**

Check: Is the last node in the workflow outputting data? n8n sends the last node's output as the tool response. If the last node is a Slack node (which sends but doesn't output), add a Set node after it to return a confirmation payload.

**Issue: mcp-remote proxy crashes with "ECONNRESET"**

Check: n8n's SSE connection has a default timeout. Switch from SSE to HTTP Streamable transport in both the n8n MCP Server Trigger node (select "HTTP Streamable" in Transport settings) and in the `mcp-remote` URL (use `/mcp` endpoint instead of `/sse`).

**Issue: High latency on first tool call**

Expected behavior — the first call after Claude Desktop restarts fetches the tool list, which takes ~1–2 seconds. Subsequent calls in the same session reuse the cached list and respond faster.

## FAQ

**What version of n8n do I need for MCP integration?**
n8n 1.68 or later includes the MCP Server Trigger and MCP Client Tool nodes. If you're on an older version, update first. Check your version at **Settings → About** in the n8n UI.

**Can I use n8n Cloud instead of self-hosted for MCP?**
Yes. n8n Cloud instances have a public HTTPS URL out of the box, which is required for MCP Server Trigger nodes to be reachable from Claude Desktop or other external MCP clients. Self-hosted instances need a public URL with TLS — typically achieved via a reverse proxy.

**What's the difference between the czlonkowski/n8n-mcp package and the native MCP nodes?**
The native MCP nodes (MCP Server Trigger and MCP Client Tool) let you invoke existing n8n workflows from external AI clients and let n8n workflows call external MCP servers. The `czlonkowski/n8n-mcp` package does something different: it gives Claude knowledge of n8n's node library so Claude can build and deploy new n8n workflows via the n8n API, without you using the visual editor. They solve different problems and can be used together.

**Is n8n MCP integration secure enough for production use?**
Yes, with proper configuration. Use Bearer Token or OAuth2 authentication on all MCP Server Trigger nodes, put n8n behind a reverse proxy, validate all AI-provided inputs in the workflow, and monitor the execution log. Don't rely solely on the MCP authentication layer — treat incoming tool parameters as untrusted user input.

**How does n8n MCP pricing compare to Zapier for AI agent workflows?**
n8n charges per workflow execution regardless of how many nodes run in that execution. Zapier charges per task (each node = one task). An AI agent workflow that runs 10 nodes per invocation costs 1 execution in n8n vs. 10 tasks in Zapier. At scale, n8n typically delivers 40–60% cost savings. For high-frequency AI agent workflows, the pricing difference compounds quickly.