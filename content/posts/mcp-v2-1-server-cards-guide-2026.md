---
title: "MCP v2.1 Server Cards: Auto-Discovery for AI Agent Tool Registries (2026 Guide)"
date: 2026-05-21T19:24:37+00:00
tags: ["mcp", "ai-agents", "tool-discovery", "model-context-protocol", "developer-tools"]
description: "How to implement MCP v2.1 Server Cards and .well-known/mcp.json for automatic AI agent tool discovery — with Python and Node.js examples."
draft: false
cover:
  image: "/images/mcp-v2-1-server-cards-guide-2026.png"
  alt: "MCP v2.1 Server Cards: Auto-Discovery for AI Agent Tool Registries"
  relative: false
schema: "schema-mcp-v2-1-server-cards-guide-2026"
---

MCP v2.1 Server Cards are standardized JSON documents hosted at `/.well-known/mcp/server-card.json` that let AI clients like Claude and Cursor discover your server's capabilities before making a single connection — no manual configuration required. If you're running an MCP server in 2026 without one, you're invisible to half the ecosystem.

## What Is an MCP Server Card and Why It Matters in 2026

An MCP Server Card is a machine-readable metadata document that describes an MCP server's identity, transport options, available tool categories, authentication requirements, and capability flags — all served from a well-known URL path so any compliant AI client can discover the server automatically. Think of it as the `robots.txt` of AI tooling, except instead of telling crawlers what to ignore, it tells agents exactly what your server offers and how to connect. The specification is formalized in SEP-2127, a proposal submitted to the Model Context Protocol working group in early 2026. With 97 million monthly MCP SDK downloads as of January 2026, and more than 10,000 active public MCP servers now in the ecosystem, the discovery problem is acute: agents can't reason about tools they don't know exist. Server Cards solve this by decoupling tool discovery from tool execution — a client can read your server card, decide whether your tools are relevant, and only then initiate the full MCP handshake. Enterprise adoption is driving urgency: 78% of enterprise AI teams report at least one MCP-backed agent in production as of Q1 2026, up from 31% a year earlier. Without a standardized discovery layer, scaling that to hundreds of internal servers requires the kind of manual inventory that breaks under organizational velocity.

### Why Auto-Discovery Changes the Architecture

The traditional approach — hardcoding MCP server URLs in agent configuration — works at a handful of servers. It fails at fifty. Server Cards introduce a pull model: when an agent encounters a new domain or service, it checks `/.well-known/mcp/server-card.json` first. If the document exists, the agent knows the transport type (HTTP, WebSocket, stdio), the auth flow (OAuth 2.0, API key, none), and which tool namespaces are available before spending a single network round-trip on the MCP protocol itself. This is exactly how HTTPS certificate discovery works — a pattern the web has relied on for decades.

## How the .well-known/mcp/server-card.json Auto-Discovery Endpoint Works

The `.well-known` directory is an IETF-standardized path prefix (RFC 5785) that web services use to host machine-readable metadata at predictable URLs. MCP v2.1 follows this convention by specifying that any HTTP-based MCP server should serve its server card at `https://<your-domain>/.well-known/mcp/server-card.json`. When an MCP-compatible AI client — Claude Desktop, Cursor, or a custom agent built on the MCP SDK — encounters a new server URL, it performs a pre-flight GET request to this endpoint before attempting any tool call. If the server returns a valid server card with a 200 status and `Content-Type: application/json`, the client parses the document to determine connection parameters and capability scope. If the endpoint returns 404 or is missing, the client falls back to legacy handshake behavior. The discovery sequence takes fewer than 100 milliseconds on a warm connection and eliminates the round-trip cost of attempting an MCP handshake against a server that doesn't support the required transport or auth model. Public MCP server registries including Smithery, Glama, and the official MCP registry maintained by Anthropic now index server cards automatically by crawling `.well-known` endpoints — meaning publishing your server card is the single action that makes your server discoverable across the entire ecosystem.

### The Discovery Lifecycle Step by Step

1. Agent or client receives a base URL (e.g., `https://api.yourservice.com`)
2. Client GETs `https://api.yourservice.com/.well-known/mcp/server-card.json`
3. Server returns the card; client validates against the SEP-2127 schema
4. Client checks `transport` field — confirms HTTP/SSE or WebSocket match its capabilities
5. Client checks `auth` field — initiates OAuth flow or injects API key header
6. Client reads `tools.namespaces` to pre-filter relevance before calling `tools/list`
7. Full MCP handshake begins only if all preconditions are satisfied

## MCP Server Card JSON Schema: Required Fields and Full Structure

An MCP Server Card is a JSON document conforming to the SEP-2127 schema. The specification defines a small set of required fields and a larger set of optional fields that registries and clients use for ranking and filtering. The required fields are `name`, `version`, `description`, `transport`, and `mcp_version`. Everything else — authentication details, tool namespace declarations, contact info, license, rate limits — is optional but strongly recommended by every major registry. Missing optional fields don't prevent discovery, but they do lower your server's ranking in registry search results and may cause some governance-aware enterprise clients to reject the server automatically. The `mcp_version` field should be set to `"2.1"` for servers implementing the current spec. The `transport` object is where clients determine how to connect: valid types are `"http"`, `"websocket"`, and `"stdio"`. HTTP servers should also include `streaming: true` if they support Server-Sent Events for streamed responses. A well-formed server card for a production HTTP server weighs between 800 bytes and 3 KB — small enough to be served from a CDN edge cache with zero compute cost.

### Complete Server Card Example

```json
{
  "$schema": "https://schema.mcp.run/server-card/v1.json",
  "name": "acme-data-tools",
  "display_name": "ACME Data Tools",
  "version": "2.3.1",
  "mcp_version": "2.1",
  "description": "SQL query execution, schema inspection, and data export tools for ACME's internal data warehouse.",
  "url": "https://mcp.acme.internal/v2",
  "transport": {
    "type": "http",
    "streaming": true,
    "endpoint": "https://mcp.acme.internal/v2/mcp"
  },
  "auth": {
    "type": "oauth2",
    "authorization_url": "https://auth.acme.internal/oauth/authorize",
    "token_url": "https://auth.acme.internal/oauth/token",
    "scopes": ["mcp:read", "mcp:execute"]
  },
  "tools": {
    "count": 14,
    "namespaces": ["sql", "schema", "export"],
    "tags": ["database", "analytics", "warehouse"]
  },
  "rate_limits": {
    "requests_per_minute": 60,
    "tokens_per_minute": 100000
  },
  "contact": {
    "email": "platform@acme.internal",
    "support_url": "https://internal.acme.com/platform/mcp"
  },
  "license": "proprietary",
  "visibility": "private"
}
```

### Required vs. Optional Fields at a Glance

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Machine-readable server identifier (slug format) |
| `version` | Yes | Server software version (semver) |
| `mcp_version` | Yes | MCP spec version this server implements |
| `description` | Yes | Human-readable summary (max 256 chars) |
| `transport` | Yes | Connection type and endpoint URL |
| `auth` | No | Authentication method and parameters |
| `tools.namespaces` | No | High-level tool categories for pre-filtering |
| `rate_limits` | No | Throttling parameters for capacity planning |
| `visibility` | No | `public`, `private`, or `organization` |
| `license` | No | SPDX identifier or `proprietary` |

## Step-by-Step: Adding a Server Card to Your MCP Server (Python and Node.js)

Adding a server card to an existing MCP server takes under 30 minutes for a typical deployment and requires no changes to your tool implementations — it's purely additive. The server card endpoint is a static JSON file served from a fixed path, which means you can implement it as a simple static file route in any web framework. The main decision is whether to generate the card dynamically at startup (allowing it to reflect the current tool count and version automatically) or to maintain it as a static file committed to your repository. Dynamic generation is better for servers where tool count changes frequently; static files work well for stable servers and let you version-control the discovery metadata alongside your code. The examples below show both the Python (FastAPI) and Node.js (Express) approaches, covering the minimal implementation that satisfies all major registries and AI clients including Claude Desktop, Cursor, and the MCP Inspector developer tool.

### Python (FastAPI) Implementation

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json, importlib.metadata

app = FastAPI()

SERVER_CARD = {
    "$schema": "https://schema.mcp.run/server-card/v1.json",
    "name": "my-mcp-server",
    "display_name": "My MCP Server",
    "version": importlib.metadata.version("my-mcp-server"),
    "mcp_version": "2.1",
    "description": "Tools for interacting with the My Service API.",
    "url": "https://api.myservice.com",
    "transport": {
        "type": "http",
        "streaming": True,
        "endpoint": "https://api.myservice.com/mcp"
    },
    "auth": {
        "type": "api_key",
        "header": "X-API-Key"
    },
    "tools": {
        "count": 8,
        "namespaces": ["search", "create", "update"],
        "tags": ["productivity", "api"]
    },
    "visibility": "public"
}

@app.get("/.well-known/mcp/server-card.json")
async def server_card():
    return JSONResponse(
        content=SERVER_CARD,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*"
        }
    )

# Mount your existing MCP handler at /mcp
# app.mount("/mcp", your_mcp_app)
```

### Node.js (Express) Implementation

```javascript
import express from 'express';
import { readFileSync } from 'fs';

const app = express();
const pkg = JSON.parse(readFileSync('./package.json', 'utf8'));

const serverCard = {
  $schema: 'https://schema.mcp.run/server-card/v1.json',
  name: pkg.name,
  display_name: 'My MCP Server',
  version: pkg.version,
  mcp_version: '2.1',
  description: 'Tools for interacting with the My Service API.',
  url: 'https://api.myservice.com',
  transport: {
    type: 'http',
    streaming: true,
    endpoint: 'https://api.myservice.com/mcp'
  },
  auth: {
    type: 'oauth2',
    authorization_url: 'https://auth.myservice.com/oauth/authorize',
    token_url: 'https://auth.myservice.com/oauth/token',
    scopes: ['mcp:read', 'mcp:execute']
  },
  tools: {
    count: 8,
    namespaces: ['search', 'create', 'update'],
    tags: ['productivity', 'api']
  },
  visibility: 'public'
};

app.get('/.well-known/mcp/server-card.json', (req, res) => {
  res.set({
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=3600',
    'Access-Control-Allow-Origin': '*'
  });
  res.json(serverCard);
});

// Attach your MCP handler here
app.listen(3000);
```

### CORS and Caching Headers

Two headers matter for registry crawlers and browser-based AI clients:

- **`Access-Control-Allow-Origin: *`** — Required for browser-based AI clients and registry scanners that run in a browser context. Without it, cross-origin requests to your server card will fail.
- **`Cache-Control: public, max-age=3600`** — Allows CDN edges and registry crawlers to cache the document for up to one hour, reducing origin load for popular servers.

## Registering Your Server Card with Major MCP Registries (GitHub, Kong, Azure, Smithery)

Once your `.well-known/mcp/server-card.json` endpoint is live, you can register it with public and enterprise registries to maximize discoverability. The public MCP server registry expanded from 1,200 servers in Q1 2025 to over 9,400 in April 2026 — 18% month-over-month growth — driven almost entirely by the standardization of server cards as the submission format. Each major registry has slightly different submission requirements, but all of them require a valid server card as the minimum entry point. The table below summarizes the current state of the four most widely used registries as of May 2026, including which additional fields they require beyond the SEP-2127 baseline. Submitting to multiple registries is additive: they don't conflict, and each one reaches a different population of AI clients and developer teams.

| Registry | Submission Method | Additional Required Fields | Visibility Options | Enterprise Features |
|----------|-------------------|---------------------------|-------------------|---------------------|
| **Smithery** (smithery.ai) | URL submission via web UI or API | `contact.email`, `license` | Public only | Paid verified badge |
| **Glama** (glama.ai) | GitHub PR to registry repo | `tools.tags`, `display_name` | Public only | None |
| **Kong MCP Registry** | Kong Gateway plugin config | `auth`, `rate_limits` | Public + private | RBAC, policy enforcement |
| **Azure API Center** | Azure Portal or ARM template | `visibility: "organization"` | Private/org only | Azure RBAC, Entra ID |
| **Official MCP Registry** (mcp.run) | CLI: `mcp registry publish` | `$schema`, semver `version` | Public | Anthropic-verified badge |

### Submitting to the Official MCP Registry

```bash
# Install the MCP CLI
npm install -g @anthropic-ai/mcp-cli

# Publish (reads .well-known/mcp/server-card.json from your live URL)
mcp registry publish --url https://api.yourservice.com

# Verify registration
mcp registry lookup acme-data-tools
```

The CLI performs a live fetch of your server card, validates it against the SEP-2127 schema, and submits it to `registry.mcp.run`. Registration completes in under 60 seconds. Your server then appears in `mcp registry search` results and in Claude Desktop's built-in server browser.

## Enterprise Governance — Controlling Which Tools AI Agents Can Discover

Enterprise MCP deployments face a governance problem that consumer tooling doesn't: unregistered, unapproved MCP servers represent a shadow IT risk equivalent to unauthorized SaaS subscriptions. If any developer can expose a tool via MCP and agents can discover it automatically, sensitive internal systems can become inadvertently accessible to AI agents operating under broad permissions. The Server Cards specification addresses this with the `visibility` field (`public`, `private`, `organization`) and by design — auto-discovery only works when a client is configured to trust a given domain or registry. The real governance layer, however, sits in enterprise MCP registries like Kong and Azure API Center, which act as curated allow-lists. An enterprise agent configured to discover tools only from `registry.acme.internal` will never discover an unapproved server at `rogue.acme.internal`, even if it has a valid server card. Kong's MCP Registry implements this via gateway policy: only servers whose cards are approved by a platform team appear in the discovery API, and every tool call routes through Kong's gateway for logging, rate limiting, and policy enforcement. Microsoft's Azure API Center approach is complementary — servers are registered through the same governance workflows as traditional REST APIs, with Azure Entra ID controlling which agents can discover and use which servers.

### Recommended Enterprise Server Card Configuration

```json
{
  "name": "internal-hr-tools",
  "mcp_version": "2.1",
  "visibility": "organization",
  "auth": {
    "type": "oauth2",
    "authorization_url": "https://login.microsoftonline.com/tenant-id/oauth2/v2.0/authorize",
    "token_url": "https://login.microsoftonline.com/tenant-id/oauth2/v2.0/token",
    "scopes": ["api://hr-mcp-server/mcp.execute"]
  },
  "governance": {
    "owner_team": "platform-engineering",
    "data_classification": "confidential",
    "approved_agents": ["hr-assistant", "onboarding-bot"]
  }
}
```

The `governance` block is not part of the SEP-2127 core spec but is supported as an extension field by Kong, Azure, and several internal tooling frameworks. Clients that don't understand it safely ignore it; enterprise gateways that do understand it use it to enforce policy.

## Testing and Validating Your MCP Server Card Implementation

Validating your server card before submission to a registry prevents the most common causes of discovery failure: malformed JSON, missing required fields, incorrect CORS headers, and schema version mismatches. The MCP ecosystem provides three tiers of validation tooling: the official MCP Inspector (browser-based), the `mcp` CLI validator, and the community-maintained `mcp-card-lint` package for CI pipelines. Running all three before your first registry submission catches 95% of issues that would otherwise result in a failed crawl or a rejected submission. Pay particular attention to the `transport.endpoint` field — it must be a fully qualified HTTPS URL that actually responds to MCP handshake requests, not just the base domain. Registries crawl both the `.well-known` path and the declared endpoint URL as part of submission validation.

### Validation Commands

```bash
# Official MCP CLI validation
mcp card validate --url https://api.yourservice.com

# mcp-card-lint for CI (npm)
npx mcp-card-lint --url https://api.yourservice.com --strict

# Manual curl check (confirm headers and content)
curl -si https://api.yourservice.com/.well-known/mcp/server-card.json | head -30

# MCP Inspector (browser)
# Open: https://inspector.mcp.run and paste your server URL
```

### Common Validation Failures and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `CORS_MISSING` | No `Access-Control-Allow-Origin` header | Add `Access-Control-Allow-Origin: *` to the route |
| `SCHEMA_VERSION_MISMATCH` | `$schema` URL points to an old version | Update to `https://schema.mcp.run/server-card/v1.json` |
| `TRANSPORT_UNREACHABLE` | `transport.endpoint` returns non-200 | Confirm MCP handler is deployed and route matches |
| `MCP_VERSION_UNSUPPORTED` | `mcp_version` is `"1.0"` or missing | Set `mcp_version: "2.1"` |
| `CONTENT_TYPE_WRONG` | Response `Content-Type` is `text/plain` | Set `Content-Type: application/json` explicitly |
| `DISPLAY_NAME_MISSING` | Smithery requires `display_name` | Add `display_name` field to your card |

### Setting Up CI Validation

```yaml
# .github/workflows/validate-server-card.yml
name: Validate MCP Server Card
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate server card JSON schema
        run: |
          cat static/.well-known/mcp/server-card.json | \
            npx ajv-cli validate \
              -s https://schema.mcp.run/server-card/v1.json \
              -d /dev/stdin
```

For servers that generate their card dynamically, run the `mcp-card-lint` check as a post-deploy step in your CD pipeline rather than in CI, pointing it at your staging environment URL.

---

## FAQ

MCP Server Cards and the `.well-known` auto-discovery pattern answer the most common questions developers and architects ask when first encountering MCP v2.1. The questions below cover the core concepts — what a server card is, whether it's mandatory, how it relates to earlier spec versions, how registries use it, and whether it works for private internal deployments. These are the same recurring questions that surface in the `#mcp` channel on the official Anthropic Discord, in GitHub issues on the MCP SDK repos, and in enterprise platform-engineering discussions on Kong and Azure forums. If your question isn't covered here, the official SEP-2127 proposal on GitHub (modelcontextprotocol/modelcontextprotocol pull #2127) contains the full specification with worked examples, and the MCP Inspector at inspector.mcp.run provides interactive, browser-based debugging for any server card implementation.

### What is an MCP Server Card?

An MCP Server Card is a JSON metadata document that describes an MCP server — its name, version, transport type, authentication method, and available tool namespaces. It's served at `/.well-known/mcp/server-card.json` and allows AI clients to discover and connect to your server automatically without manual configuration.

### Is the .well-known/mcp.json endpoint required for MCP v2.1?

The `.well-known/mcp/server-card.json` endpoint is strongly recommended but not strictly required for MCP v2.1 compliance. However, without it, your server won't appear in public registries like Smithery or the official MCP registry, and AI clients that support auto-discovery (including Claude Desktop) won't be able to find it without an explicit URL entry in client configuration.

### What's the difference between SEP-2127 and the older server-card.json formats?

SEP-2127 is the current standardized proposal that unifies earlier experimental formats, including SEP-1649 (the original `server-card.json` concept) and SEP-1960 (the manifest format). The key differences are the `mcp_version` field (new), the nested `transport` object (replaces flat `transport_type`), and the `$schema` reference which enables automatic JSON Schema validation. If you implemented an earlier format, the migration is straightforward — mainly restructuring the `transport` field.

### How often do registries crawl server cards?

Crawl frequency varies by registry. The official MCP registry (`mcp.run`) crawls registered servers every 24 hours. Smithery crawls every 6 hours. Kong MCP Registry relies on push-based webhooks rather than crawling — you notify Kong when your card changes. For most production servers, setting `Cache-Control: public, max-age=3600` (one hour) is a good balance: fresh enough for registries to pick up version updates within a reasonable time, cached enough to avoid unnecessary origin hits.

### Can I use MCP Server Cards for private internal servers?

Yes. Set `"visibility": "private"` or `"visibility": "organization"` in your server card. Private servers can still serve the card (so authorized clients can validate before connecting) but won't be indexed by public registries. Enterprise MCP registries like Kong and Azure API Center support private registries where only approved clients can discover internal servers, giving you the benefits of auto-discovery while maintaining governance controls over which agents can see which tools.
