---
title: "JFrog Skills and MCP Tools Guide 2026: Give Your Coding Agents Safe Artifact Context"
date: 2026-07-04T12:00:00+00:00
tags: ["jfrog", "mcp", "agent-skills", "supply-chain-security", "artifactory"]
description: "A practical 2026 guide to JFrog Skills and the JFrog MCP Server — two complementary paths for giving AI coding agents governed access to artifacts, vulnerabilities, and curation data."
draft: false
cover:
  image: "/images/jfrog-skills-mcp-tools-guide-2026.png"
  alt: "JFrog Skills and MCP Tools Guide 2026"
  relative: false
schema: "schema-jfrog-skills-mcp-tools-guide-2026"
---

If your coding agents can't see your artifact repository, they're flying blind. They'll guess dependency versions, hallucinate package names, and suggest upgrades that don't exist. But giving an AI agent direct access to Artifactory is a bad idea — one prompt injection and your entire binary repository is an attack surface.

JFrog solves this with two complementary paths: **JFrog Skills** (open-source agent skills) and the **JFrog MCP Server** (remote SaaS MCP server). Both give agents safe, governed access to artifact context, but they work differently and suit different use cases. Here is how both work, when to use each, and how to set them up without compromising security.

## Why JFrog for AI Coding Agents?

The core problem is straightforward: coding agents need artifact context to be useful. When I ask an agent "what's the latest version of log4j-core in our release repo?" or "is it safe to upgrade to lodash 4.17.21?", the agent needs to query Artifactory, check Xray for CVEs, and verify curation policies. Without that access, the agent either guesses or asks me to check manually — defeating the purpose.

The naive solution — giving the agent an API key and letting it call Artifactory directly — creates real risk. A compromised agent could download malicious artifacts, exfiltrate repository metadata, or modify repository configurations. I've seen teams burn weeks recovering from credential leaks in agent chat histories.

JFrog's thesis, which I find compelling, is that **agent skills are the new packages of AI**. The same supply chain governance JFrog applies to npm, Maven, and PyPI packages — curation, vulnerability scanning, provenance tracking — should apply to AI agent capabilities. A skill that searches artifacts should be curated, scanned, and audited the same way a library dependency is.

## What Are JFrog Skills?

JFrog Skills is an open-source repository at [github.com/jfrog/jfrog-skills](https://github.com/jfrog/jfrog-skills) (Apache 2.0, beta, v0.11.0 as of this writing). It provides three agent skills that any AI coding agent can install via `npx skills add`:

- **jfrog** (base) — CLI setup, artifact search/download, version queries, metadata, CVE lookups, upgrade safety, AQL queries, GraphQL (OneModel), build tracing, storage management, and platform administration.
- **jfrog-package-safety-and-download** — Checks whether npm, Maven, PyPI, Go, and other packages are safe, curated, or allowed before downloading through Artifactory.
- **jfrog-ai-catalog-skills** — Lets agents discover, install, update, and publish agent skills in the JFrog AI Catalog.

### Three-Tier Tool Selection

The architecture is worth understanding because it explains why Skills are more flexible than a plain MCP server. Skills use a **three-tier tool selection strategy**:

1. **JFrog MCP tools** (preferred) — If a matching MCP tool exists and succeeds, use it.
2. **jf CLI commands** (fallback) — If no MCP tool is available, fall back to the JFrog CLI.
3. **jf api REST/GraphQL** (last resort) — Direct API calls for operations the CLI doesn't expose.

This means Skills automatically use the most efficient path available. If you also have the JFrog MCP Server configured, Skills will prefer its MCP tools. If not, they drop to CLI or API. No configuration needed — it's built into the skill logic.

### Progressive Disclosure

Skills use a reference-file pattern: instead of loading the entire JFrog platform's capabilities into the agent's context, each skill ships focused reference files (`.md` files with prompt examples, tool descriptions, and parameter tables). The agent reads only the files relevant to the current task. This keeps context usage low and response quality high — the agent isn't drowning in irrelevant Artifactory documentation when it just needs to check a CVE.

## What Can You Do with JFrog Skills?

In practice, I've found the most useful operations fall into a few categories:

**Artifact operations** — Search by name, version, SHA256, or path. Download specific artifacts. Query metadata and properties. Run AQL queries for complex searches.

**Security queries** — Check CVEs affecting specific artifacts. Evaluate upgrade safety (will this version introduce new vulnerabilities?). Review security profiles and exposure findings including secrets, IaC misconfigurations, and AppSec results.

**Curation and compliance** — Verify curation status (is this package allowed?). Check license risks. Review audit events and violation tracking.

**Build tracing** — Trace what artifacts a build produced. List dependencies. Verify checksums. Pull VCS information.

**Storage management** — Find stale artifacts not downloaded in 90 days. Identify large artifacts wasting space. Query artifacts by custom properties.

**Multi-step workflows** — This is where Skills really shine. A single prompt like "upgrade requests to the latest safe version" triggers a workflow: check versions → check vulnerabilities → verify curation → download. The agent orchestrates the whole sequence.

## What Is the JFrog MCP Server?

The JFrog MCP Server is JFrog's official remote MCP server (SaaS, beta). Unlike Skills, it requires zero installation — it's maintained on JFrog's infrastructure. An admin enables it on a JPD, and users connect via OAuth.

**Key characteristics:**
- **OAuth authentication** — No API keys to manage or leak. The browser-based OAuth flow means credentials never touch your MCP client config.
- **Structured tool interface** — Tools for repository CRUD, AQL search, package info/versions/vulnerabilities, curation status, and Xray summaries.
- **Client support** — Works with VS Code, Cursor, Claude Desktop, Kiro, and Codex.
- **No upgrades** — JFrog manages the server. You just connect.

There is also an **experimental community MCP server** at [github.com/jfrog/mcp-jfrog](https://github.com/jfrog/mcp-jfrog) (119 stars, self-hosted via npm or Docker, 22+ tools). It is **not officially supported** and should only be used for development and testing. The README itself directs users to the official MCP Server for production use.

## JFrog Skills vs JFrog MCP Server: Which to Use?

| Capability | JFrog Skills | JFrog MCP Server (Official) |
|---|---|---|
| Type | Open-source agent skills (npx skills) | Remote SaaS MCP server |
| Auth | jf CLI config / access token | OAuth (browser-based) |
| Installation | npx skills add + jf CLI setup | None (SaaS, add URL to client) |
| Capabilities | Full platform: artifacts, builds, security, curation, storage, admin, AI Catalog | Repository CRUD, AQL, package info, vulnerabilities, curation, Xray |
| Multi-step workflows | Yes (e.g., check + download + verify) | No (single-tool calls) |
| Production readiness | Beta (Apache 2.0) | Beta (JFrog SaaS) |
| Best for | Deep platform integration, custom workflows, open-source flexibility | Quick, managed artifact context for any MCP client |

**Use JFrog Skills when:**
- You need full platform operations — build tracing, storage management, platform administration
- You want multi-step workflows ("check safety, then download, then verify")
- You prefer open-source, auditable code
- You're already using `npx skills` in your agent setup

**Use the JFrog MCP Server when:**
- You want a zero-install, managed connection
- OAuth-based auth is important for your security posture
- You only need basic artifact queries (versions, vulnerabilities, search)
- You're already using MCP clients and want to add JFrog as another tool

**Use both** when you want Skills' depth with the MCP Server's managed auth. Skills automatically prefer MCP tools when available, so they complement each other.

## Setting Up JFrog Skills in Cursor

The JFrog Cursor Plugin (v0.5.0+) is the most complete integration — it bundles JFrog Skills v0.11.0 and adds Agent Guard for MCP server management.

```bash
# Prerequisites
jf --version  # must be >= 2.100.0
jq --version  # must be on PATH
curl --version # must be on PATH

# Configure JFrog CLI
jf config add --artifactory-url https://yourinstance.jfrog.io \
  --access-token YOUR_TOKEN

# Install JFrog Skills (if not using the Cursor Plugin)
npx skills add git@github.com:jfrog/jfrog-skills.git -g \
  --skill jfrog \
  --skill jfrog-package-safety-and-download \
  --skill jfrog-ai-catalog-skills
```

If you're using the Cursor Plugin, Skills are vendored automatically. Just install the plugin from the marketplace, set `JFROG_PLATFORM_URL` and `JFROG_ACCESS_TOKEN` environment variables, and you're ready to ask natural-language questions about your artifacts.

## Setting Up the JFrog MCP Server

The MCP Server setup is simpler because there's nothing to install:

1. **Admin**: Enable MCP Server on a JPD in Integrations → MCP Server.
2. **Copy** the MCP Server URL: `https://<YOUR_INSTANCE>.jfrog.io/mcp`
3. **Add to your MCP client config** (Cursor example):

```json
{
  "mcpServers": {
    "jfrog": {
      "url": "https://yourinstance.jfrog.io/mcp",
      "auth": {
        "type": "oauth"
      }
    }
  }
}
```

4. **Authorize**: The OAuth flow opens in your browser. Complete it once, and the connection persists.

That's it. No CLI setup, no token management, no upgrades.

## Agent Guard: Managing MCP Servers Through JFrog

Agent Guard is a feature in the JFrog Cursor Plugin that I think is genuinely underappreciated. It lets you discover, install, configure, update, and remove MCP servers from the JFrog AI Catalog through natural language.

The security design is smart: when an agent needs to configure an MCP server with sensitive values (API keys, tokens), it doesn't set them directly. Instead, it returns a CLI command for you to run in your terminal. The secrets never appear in chat history. This is the same pattern I recommend in my [MCP security guide](/posts/mcp-security-guide-2026/) — keep credentials out of agent context.

When you switch projects, Agent Guard re-syncs the approved MCP servers and policies for that project. The AI Catalog governs which servers are approved, with version management and policy enforcement.

## Security and Governance Considerations

If you're evaluating JFrog for agent access, here is what the security model looks like in practice:

**Skills** use the jf CLI's authentication — the agent never sees raw credentials. The CLI handles token refresh and scoping. All operations go through JFrog's existing audit system, so you can trace every agent action back to a user and session.

**MCP Server** uses OAuth — no API keys in config files, no tokens in chat history. The OAuth token is scoped to the user's permissions on the JPD.

**AI Catalog** governs which MCP servers are approved per project. This is the supply chain governance piece: the same curation policies that block vulnerable npm packages can block malicious or unapproved MCP servers.

**Curation policies** apply to agent-downloaded packages the same as human-downloaded. If your curation policy blocks log4j versions with known CVEs, the agent can't bypass it by downloading directly.

For a deeper look at securing agent skills and MCP servers, see my [agent skills supply chain security guide](/posts/agent-skills-supply-chain-security-guide-2026/) and the [DevOps MCP servers guide](/posts/devops-mcp-servers-guide-2026/).

## Prompt Examples

Here are prompts I use regularly with JFrog Skills, organized by role:

**As a backend developer:**
- "What's the latest version of log4j-core in libs-release?"
- "Download guava 33.2.1-jre from libs-release-local"
- "Show me the dependencies of my-service:1.2.3"

**As a security engineer:**
- "Which of my artifacts are affected by CVE-2024-12345?"
- "Is it safe to upgrade to lodash 4.17.21?"
- "Show me curation audit events from the last 7 days"

**As a platform engineer:**
- "Find artifacts in libs-snapshot not downloaded in 90 days, larger than 10MB"
- "What artifacts were produced by the last build of my-service?"
- "I want to upgrade requests to the latest safe version. Check versions, vulnerabilities, and curation, then download."

## Troubleshooting

A few issues I've run into and their fixes:

**Skills not responding** — Verify `jf --version` >= 2.100.0, `jq` and `curl` are on PATH, and `jf config` shows a configured instance. The environment check caches results in `~/.jfrog/skills-cache/` — if you change config, clear the cache.

**MCP Server connection fails** — Verify the MCP Server is enabled on the JPD (admin setting), OAuth was completed, and the URL is correct. The URL must end in `/mcp`.

**Agent Guard can't find servers** — Check AI Catalog entitlement and project membership. Agent Guard only shows servers approved for your current project.

**Curation tools unavailable** — Curation and catalog tools require a unified or ultimate security package. Basic subscriptions won't see these tools.

**Experimental MCP server** — Check `JFROG_ACCESS_TOKEN` and `JFROG_URL` environment variables. The experimental server doesn't use OAuth.

## Decision Framework

Here is how I think about choosing the right path:

- **Start with the JFrog MCP Server** if you're on JFrog Cloud and want the simplest setup. Add the URL to your MCP client, authorize via OAuth, and you're done. This covers 80% of use cases — version checks, vulnerability lookups, basic searches.

- **Add JFrog Skills** when you hit the limits of the MCP Server: multi-step workflows, build tracing, storage management, or custom AQL queries. Skills are also the right choice if you want open-source, auditable code or need to run against a self-hosted JFrog instance.

- **Use both** for the best experience. Skills auto-detect MCP tools and prefer them when available, falling back to CLI or API for operations the MCP Server doesn't expose. You get the managed auth of OAuth with the depth of Skills.

- **Skip the experimental MCP server** for production. It's useful for testing custom deployments, but the README is clear it's not officially supported.

*Editor's note: JFrog Skills is at v0.11.0 and the JFrog MCP Server is in beta as of July 2026. Features, APIs, and requirements may change. Verify current versions before production deployment.*
