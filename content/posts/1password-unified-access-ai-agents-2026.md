---
cover:
  alt: '1Password Unified Access for AI Agents: Developer Security Guide'
  image: /images/1password-unified-access-ai-agents-2026.png
  relative: false
date: 2026-04-26 00:04:05+00:00
description: How to use 1Password Unified Access to securely inject credentials into
  AI agents at runtime — no hardcoded secrets, full audit trail.
draft: false
schema: schema-1password-unified-access-ai-agents-2026
tags:
- 1password
- ai-agents
- secrets-management
- developer-security
- non-human-identity
title: '1Password Unified Access for AI Agents: Developer Security Guide'
---

1Password Unified Access is a secrets management platform that lets you discover, secure, and audit credentials across human users, machine identities, and AI agents from a single control plane — launched as generally available on March 17, 2026, with partners Anthropic, Cursor, GitHub, Perplexity, and Vercel.

## What Is 1Password Unified Access (and Why AI Agents Need It Now)

1Password Unified Access is an enterprise identity platform that extends 1Password's credential management beyond human users to cover machine identities and AI agents. Launched on March 17, 2026, as generally available, Unified Access Pro introduces three operational pillars — Discover, Secure, and Audit — that give security and engineering teams a single pane of glass for managing every credential type in an organization. Unlike traditional password managers or standalone secrets managers, Unified Access is purpose-built for the era of autonomous AI agents, where software systems independently authenticate to APIs, databases, and third-party services without human involvement at each step. 1Password already secures 1.3 billion human and machine credentials across 180,000 businesses; Unified Access extends that trust model to agentic workloads. The core value proposition for developers: agents receive credentials at task runtime via SDK calls instead of reading static API keys from disk or environment files. This means a leaked agent configuration file exposes zero usable secrets.

### Why Runtime Injection Changes the Security Model

Traditional secrets management passes credentials once at startup via environment variables or config files. Runtime injection means your agent calls `secrets.resolve()` immediately before each API operation, receiving a short-lived credential that was never stored in the agent process environment. If an attacker compromises agent memory mid-execution, they capture a credential that expires within minutes rather than a static key valid for months.

## The Non-Human Identity Crisis: Why AI Agents Are the New Attack Surface

Non-human identities — service accounts, API keys, machine certificates, and AI agent credentials — now outnumber human users 100-to-1 in enterprise environments. Gartner projects that by 2026, 30% of enterprises will rely on AI agents that act independently, executing transactions and completing tasks without human approval at each step. This scale creates a credential sprawl problem that most organizations have not yet confronted: each agent needs its own scoped identity, and those identities must be provisioned, rotated, and deprovisioned as agents spin up and down at runtime. GitGuardian's 2025 report found 24 million leaked credentials on GitHub, with 70% of secrets leaked in 2022 still valid today. AI agents dramatically expand the attack surface because they are designed to take autonomous actions using those credentials. BeyondTrust frames overprivileged AI agents as "the new insider threat" — an agent with standing access to your production database, S3 bucket, and Stripe API is one prompt injection away from becoming a data exfiltration vector. The answer is treating each agent as a first-class identity with scoped authentication, just-in-time access, and ephemeral credentials rather than persistent API keys.

### What "First-Class AI Agent Identity" Means in Practice

A first-class identity means the agent has its own service account, its own audit trail, and its own access policy — not a shared service account borrowed from a human user or a CI pipeline. 1Password Unified Access provisions a dedicated vault per agent, scoped to only the credentials that agent requires. When the agent is decommissioned, the vault and its service account are removed, leaving no orphaned credentials.

## Core Architecture — Discover, Secure, Audit

1Password Unified Access Pro is built on three interdependent pillars that cover the complete credential lifecycle for AI agents. **Discover** continuously scans your infrastructure for exposed credentials — SSH keys, `.env` files, hardcoded tokens in repositories, and active AI agent sessions — giving you a live inventory of every credential and every identity accessing it. **Secure** centralizes those credentials into 1Password vaults, replaces hardcoded secrets with dynamic references, and enforces access policies that restrict each agent to exactly the credentials it needs. **Audit** maintains a unified access trail across every human, machine, and agent identity: who accessed what credential, when, and from which agent execution context. This Discover → Secure → Audit loop is the operational model for zero-trust agentic infrastructure. For developers, the practical entry point is Secure: create a vault, add your secrets, create a service account with read-only access scoped to that vault, and use the service account token to authenticate SDK calls from your agent. Discover and Audit run continuously in the background, surfacing anomalies and compliance evidence without developer intervention.

### How Unified Access Differs from 1Password Business

1Password Business manages human credentials with team sharing. Unified Access adds a machine identity layer: service accounts for agents, SDK-based resolution (not human UI flows), and the Discover scanner that identifies agentic credential exposure patterns. If you already use 1Password Business, Unified Access is an add-on tier rather than a separate product.

## Developer Quickstart: Integrating 1Password SDKs with AI Agents (Python, JS, Go)

The 1Password SDK enables runtime credential injection in three languages — Python, JavaScript/TypeScript, and Go — with a consistent pattern: authenticate with a service account token, then call `secrets.resolve()` with a secret reference URI to retrieve a credential immediately before use. The secret reference URI format is `op://{vault}/{item}/{field}`, where vault and item names match your 1Password vault structure. Here is the Python pattern for an AI agent that needs to call the Anthropic API without storing the key:

```python
import asyncio
from onepassword.client import Client

async def get_anthropic_key():
    client = await Client.authenticate(
        auth=os.environ["OP_SERVICE_ACCOUNT_TOKEN"],
        integration_name="my-ai-agent",
        integration_version="1.0.0"
    )
    return await client.secrets.resolve("op://ai-agents/anthropic/api-key")

# The key is fetched at task time, not at startup
api_key = asyncio.run(get_anthropic_key())
```

The JavaScript/TypeScript equivalent uses the same URI format:

```typescript
import { createClient } from "@1password/sdk";

const client = await createClient({
  auth: process.env.OP_SERVICE_ACCOUNT_TOKEN!,
  integrationName: "my-ai-agent",
  integrationVersion: "1.0.0",
});

const apiKey = await client.secrets.resolve("op://ai-agents/anthropic/api-key");
```

And in Go:

```go
client, err := op.NewClient(ctx,
    op.WithServiceAccountToken(os.Getenv("OP_SERVICE_ACCOUNT_TOKEN")),
)
secret, err := client.Secrets.Resolve(ctx, "op://ai-agents/anthropic/api-key")
```

The only value you set in the environment is `OP_SERVICE_ACCOUNT_TOKEN`, which is itself a 1Password-managed credential. You can inject it via `op run` at agent launch so even the token never touches your codebase.

### Creating the Service Account and Vault

In 1Password, create a dedicated vault named for your agent (`ai-agents` or more specific like `flight-booking-agent`). Add your API keys and credentials as items in that vault. Then create a service account with read-only access scoped to that vault only — the service account cannot read items in other vaults, cannot create or delete credentials, and has no UI access. Copy the service account token and store it as an environment variable in your deployment system (not in your code repository).

## MCP Server Integration — Giving Claude and Cursor Access to Your Vault

The Model Context Protocol (MCP) integration lets Claude, Cursor, and other MCP-compatible AI assistants pull credentials from your 1Password vault at runtime, without embedding tokens in configuration files. This is the mechanism that prevents credential exposure in MCP server config files — a common attack vector as developers configure local AI development environments. To configure the 1Password MCP server, add it to your MCP client configuration using the `op run` command as a transport wrapper, which injects secrets at launch time without touching config files. The `op run` command reads secret reference URIs from your command environment and resolves them against your vault before spawning the process. For Claude Desktop, the configuration looks like:

```json
{
  "mcpServers": {
    "1password": {
      "command": "op",
      "args": ["run", "--", "1password-mcp-server"],
      "env": {
        "OP_SERVICE_ACCOUNT_TOKEN": "op://dev-tools/mcp-service-account/token"
      }
    }
  }
}
```

This means the service account token itself is resolved from 1Password at startup, so the config file contains only a reference, not a credential. When Claude or Cursor needs to call an external API, the MCP server resolves the credential from the vault and passes it to the tool call. The Unified Access audit trail records each credential access with the MCP session context, giving you visibility into which AI assistant accessed which credential and when.

### Setting Up op run for Existing Agent Workflows

If you have an existing agent that reads credentials from environment variables, you can migrate to runtime injection incrementally using `op run`. Replace `ANTHROPIC_API_KEY=sk-...` in your `.env` with `ANTHROPIC_API_KEY=op://ai-agents/anthropic/api-key`, then launch your agent with `op run --env-file=.env -- python agent.py`. The `op run` command resolves the references and injects real values as environment variables before your process starts — zero code changes required.

## Service Accounts and Runtime Credential Delivery: Step-by-Step Setup

Service accounts are the identity primitive for AI agents in 1Password Unified Access. Each service account has a scoped token, an access policy, and an audit trail independent of any human user. Setting up runtime credential delivery takes five steps. First, create a vault in 1Password for your agent's credentials — one vault per agent or agent class, not a shared vault. Second, add your secrets as items in that vault: API keys, database passwords, OAuth client secrets. Third, create a service account in 1Password developer settings, assign it read-only access to your new vault, and copy the generated token. Fourth, store the service account token in your deployment environment as `OP_SERVICE_ACCOUNT_TOKEN` — in Kubernetes as a sealed secret, in GitHub Actions as an encrypted secret, in Vercel as an environment variable. Fifth, update your agent code to call `secrets.resolve()` with the `op://vault/item/field` URI pattern immediately before each credential use. The service account token is the only credential that leaves 1Password infrastructure; all other secrets remain in the vault and are resolved on demand. When you decommission the agent, delete the service account to immediately revoke all its access — no credential rotation required.

### Token Rotation and Expiry

Service account tokens support configurable expiry. For short-lived agent tasks (a single flight booking, an expense report submission), you can generate a token with a 24-hour TTL so it expires automatically after the task window. For persistent agents, configure automatic rotation via the 1Password API and update the token in your deployment secrets store on each rotation event.

## 1Password vs HashiCorp Vault vs Doppler vs Akeyless for AI Agent Workloads

Each secrets management platform has a different fit for AI agent workloads. 1Password Unified Access is the only platform that combines consumer-grade UX, developer secrets management, and AI agent identity in one product — with the Discover scanner and unified audit trail covering all three identity types.

| Platform | AI Agent Support | Operational Overhead | Developer UX | Agentic Audit Trail |
|---|---|---|---|---|
| **1Password Unified Access** | Native (SDK, MCP, service accounts) | Low (SaaS) | Excellent | Yes — unified across human + agent |
| **HashiCorp Vault** | Via dynamic secrets + AppRole | High (self-hosted) | Steep learning curve | Yes, but siloed |
| **Doppler** | Env injection only | Low (SaaS) | Strong | No agent-specific audit |
| **Akeyless** | Via API + zero-knowledge arch | Medium | Good | Partial |

HashiCorp Vault offers the most powerful secret engine capabilities — dynamic secrets, PKI, database credential rotation — but requires significant operational investment and a dedicated secrets infrastructure team. For a startup or mid-size company where developers manage their own tooling, the operational overhead often exceeds the security benefit. Doppler excels at developer experience for environment variable management but has no concept of AI agent identity or agentic audit trails. Akeyless brings a cloud-native zero-knowledge architecture that appeals to regulated industries, but its AI agent integration story lags behind 1Password's SDK and MCP support. The practical recommendation: if your organization already uses 1Password Business, Unified Access is the lowest-friction path to agentic secrets management. If you have existing investment in HashiCorp Vault, the AppRole auth method plus Vault Agent sidecar can cover AI agent credential delivery, but plan for significantly more infrastructure work.

## Best Practices for Governing AI Agent Credentials at Scale

Governing AI agent credentials at scale requires treating agents as first-class identities with the same lifecycle management as human employees. Four practices separate mature agentic security postures from credential sprawl. First, one vault per agent class — not per agent instance, but per behavioral class. A fleet of flight-booking agents shares one vault because they need the same credentials; a separate expense-reporting agent class gets its own vault with only the finance API credentials it needs. Second, minimum viable permissions: the service account for each agent class should have read access to exactly the items in its vault and nothing else. 1Password's vault access model makes this straightforward to enforce without complex policy expressions. Third, automated deprovisioning: tie service account lifecycle to your agent deployment pipeline. When a Kubernetes deployment is torn down, a post-hook calls the 1Password API to delete the service account. Fourth, alert on anomalous access patterns: the Unified Access audit trail surfaces deviations from baseline — an agent that normally accesses two credentials suddenly accessing ten is a signal worth investigating. Connect the 1Password audit log to your SIEM for automated alerting.

### Human-in-the-Loop Approval for Sensitive Credentials

For credentials that grant write access to production systems — database write credentials, payment API keys, email sending credentials — consider a human-in-the-loop approval flow where the agent requests access and a human approves before the credential is injected. 1Password's API supports building this pattern: the agent calls a webhook, a human approves in a Slack message, and the approval triggers a time-limited service account token. The credential is injected only after approval and expires when the task completes.

## Roadmap: What's Coming to Unified Access in 2026

1Password's 2026 roadmap for Unified Access focuses on three capability areas based on public announcements and the patterns established at the March 2026 GA launch. Automated discovery is expanding from static scanning to real-time credential exposure detection — rather than scheduled scans, Discover will emit alerts within minutes of a new `.env` file appearing in a repository or a new API key being hardcoded in a deployment configuration. Cross-platform agent identity federation is in development, targeting OAuth 2.0-based agent authentication flows where an AI agent can authenticate to external services using a 1Password-managed identity rather than a static API key — aligning with the emerging standard for agentic OAuth grants being developed in collaboration with launch partners Anthropic and GitHub. Finally, consent and approval workflows for high-privilege operations are on the roadmap: structured flows where an AI agent requests access to a sensitive credential, the request surfaces to a human approver via Slack or email, and approval generates a time-limited token scoped to the specific operation. This brings the human-in-the-loop model from manual implementation patterns to a first-class platform feature.

---

## FAQ

The most common questions about 1Password Unified Access for AI agents center on three topics: how it differs from 1Password Business, which AI frameworks it supports, and how to handle credential rotation in autonomous agent workflows. Unified Access Pro — generally available since March 17, 2026 — is designed for engineering and security teams deploying autonomous agents at scale, not just individual developers managing passwords. The platform's service account model, SDK-based resolution, and Discover scanner address the specific failure modes of agentic systems: credential sprawl across agent configuration files, lack of visibility into which agent accessed which credential, and inability to revoke access quickly when an agent is decommissioned. The answers below address the practical implementation questions that come up most often when migrating from static API keys to runtime credential injection.

### How does 1Password Unified Access differ from 1Password Business?

1Password Business manages human user credentials with team sharing and a web or desktop UI. Unified Access adds a machine identity layer with service accounts for AI agents, SDK-based credential resolution (not human UI flows), and the Discover scanner that identifies exposed secrets and agentic credential patterns. If you already use 1Password Business, Unified Access is available as an add-on tier.

### Can I use 1Password Unified Access with any AI framework or only Anthropic Claude?

The 1Password SDK (Python, JavaScript/TypeScript, Go) works with any AI agent framework — LangChain, AutoGen, custom agent loops, or raw API calls. The MCP integration works with any MCP-compatible AI assistant, including Claude, Cursor, and others. The Anthropic partnership at launch means tighter integration for Claude-specific tooling, but the underlying SDK has no framework dependency.

### What is the `op run` command and when should I use it?

`op run` is a CLI wrapper that resolves 1Password secret references in environment variables before spawning a subprocess. Use it when you want to migrate an existing agent to runtime credential injection without changing code: replace credential values in your `.env` file with `op://vault/item/field` references and launch with `op run --env-file=.env -- your-agent-command`. For new agents, prefer the SDK for more granular control over when credentials are resolved.

### How do I handle credential rotation for AI agents?

With runtime injection via the SDK, rotation is transparent: update the credential value in your 1Password vault, and the next `secrets.resolve()` call returns the new value. There is no restart or redeployment required unless the agent caches credentials. The recommendation is never to cache credentials in agent memory; resolve them immediately before each use to ensure you always get the current value.

### Is the service account token itself secure if someone reads the environment of the running process?

Capturing the service account token from process environment gives an attacker the ability to resolve credentials from the scoped vault for as long as the token is valid. Mitigate this with short token TTLs (24 hours for task-scoped agents), vault access scoped to only necessary items, and 1Password's anomaly detection alerting on unusual resolution patterns. For highest security, use `op run` so even the token is injected from a 1Password reference and is not a static value in any configuration file.