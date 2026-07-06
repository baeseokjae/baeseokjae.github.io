---
title: "Anthropic OIDC Gateway for Claude Code 2026: Self-Hosted Enterprise SSO, Spend Caps, and Multi-Cloud Routing"
date: 2026-07-06
draft: false
tags:
  - Claude Code
  - OIDC
  - Enterprise SSO
  - AI Gateway
  - Cost Control
  - Multi-Cloud
categories:
  - Claude Code
  - Enterprise AI
description: "Complete guide to Anthropic's self-hosted OIDC gateway for Claude Code 2026: SSO with Okta/Entra ID/Google Workspace, spend caps, OTLP telemetry, multi-cloud failover routing, and VPC deployment."
slug: "anthropic-oidc-gateway-for-claude-code-2026"
cover:
  image: "/images/anthropic-oidc-gateway-for-claude-code-2026.png"
  alt: "Anthropic OIDC Gateway for Claude Code 2026"
  relative: false
schema: "schema-anthropic-oidc-gateway-for-claude-code-2026"
---

If you're running Claude Code across more than a handful of developers, the first thing you'll hit is credential sprawl. Every engineer has their own Anthropic API key, there's no central visibility into who's spending what, and when someone leaves the company, you're hunting down keys in Slack DMs and personal password managers. Anthropic's answer in July 2026 is the **Claude Apps Gateway** — a self-hosted OIDC gateway that replaces per-developer API keys with corporate SSO, enforces spend caps per user or group, routes traffic across multiple cloud providers with automatic failover, and emits OTLP telemetry to your own observability stack. It ships inside the `claude` binary itself — no separate product to install.

I've been running this in production for a small team, and here's what you need to know to set it up, where the sharp edges are, and whether it's the right move for your organization.

## What the Claude Apps Gateway Actually Does

The gateway is a stateless HTTP service that sits between Claude Code clients and your model provider. It's not a separate product — it's built into the `claude` CLI. You run it with a single command:

```yaml
# gateway.yaml
host: "0.0.0.0"
port: 8443
public_url: "https://claude-gateway.example.com"

oidc:
  issuer_url: "https://your-idp.example.com/.well-known/openid-configuration"
  client_id: "your-oidc-client-id"
  client_secret: "your-oidc-client-secret"

database:
  url: "postgresql://user:password@postgres:5432/gateway"

providers:
  - name: bedrock
    type: bedrock
    region: us-east-1
    priority: 1
  - name: anthropic
    type: anthropic
    api_key: "${ANTHROPIC_API_KEY}"
    priority: 2

telemetry:
  otlp_endpoint: "https://otel-collector.example.com:4318"
```

Then start it:

```bash
claude gateway --config gateway.yaml
```

That's it. The gateway handles OIDC authentication, translates the Anthropic Messages API protocol to whatever provider you're routing to, enforces budgets, and ships metrics to your observability pipeline. Developers point their Claude Code CLI at the gateway URL, authenticate with their corporate IdP, and never touch an API key.

## Why OIDC Matters More Than You Think

The obvious win is eliminating API key management. But the real value is in the onboarding/offboarding loop. When a developer joins, they authenticate through your existing IdP — Okta, Microsoft Entra ID, Google Workspace, Keycloak, Dex, or PingFederate. The gateway reads their email and group membership from the OIDC `id_token` or userinfo endpoint. When they leave, you disable their IdP account, and they lose access to the gateway instantly. No orphaned keys, no "I forgot to rotate that key from the contractor who left six months ago."

The gateway supports the authorization-code flow with PKCE, which is the standard you should be using anyway. Your IdP must serve a `/.well-known/openid-configuration` endpoint and return the user's email (and optionally groups) in the token or via the userinfo endpoint. Every major IdP supports this — I've tested with Okta and Entra ID, and both work without surprises.

## Architecture: Stateless Container, PostgreSQL Backend

The gateway is a single stateless container. All persistent state — user sessions, spend records, configuration — lives in PostgreSQL. This means you can run multiple replicas behind a load balancer without sticky sessions. The container image is included in the `claude` binary distribution, so there's no separate Docker image to pull.

Deployment requirements are straightforward:

- **PostgreSQL 14+** for the database
- **Private network only** — Claude Code clients only connect to private gateway addresses. Do not expose the gateway to the public internet.
- **TLS termination** — the gateway expects HTTPS. You can terminate TLS at your load balancer or configure it in the gateway itself.
- **OIDC provider reachability** — the gateway needs to reach your IdP's token and userinfo endpoints.

For Kubernetes, the deployment is a standard Deployment + Service + Ingress pattern. For Cloud Run, it's a single service with a Cloud SQL PostgreSQL instance. The [official deployment guide](https://code.claude.com/docs/en/claude-apps-gateway-deploy) covers both.

## Step-by-Step Setup

### 1. Register an OIDC Application in Your IdP

Create a confidential web application in your identity provider. The redirect URI must be:

```
https://<your-gateway-hostname>/oauth/callback
```

For **Okta**, create a Web application with the OIDC sign-on method. For **Microsoft Entra ID**, register a new application and configure the redirect URI under Authentication > Web. For **Google Workspace**, create an OAuth 2.0 Client ID with application type "Web application."

Make sure you enable the authorization-code grant type with PKCE. The gateway handles PKCE automatically — you just need the client ID and client secret.

### 2. Create the Configuration File

The `gateway.yaml` file is the single source of truth. Here's a production-oriented version with multi-provider failover:

```yaml
host: "0.0.0.0"
port: 8443
public_url: "https://claude-gateway.example.com"

oidc:
  issuer_url: "https://okta.example.com/.well-known/openid-configuration"
  client_id: "0oa3abc123def456"
  client_secret: "${OIDC_CLIENT_SECRET}"
  scopes:
    - "openid"
    - "email"
    - "profile"
    - "groups"

database:
  url: "${DATABASE_URL}"

providers:
  - name: bedrock-primary
    type: bedrock
    region: us-east-1
    priority: 1
    models:
      - "anthropic.claude-sonnet-5-20260601"
      - "anthropic.claude-haiku-5-20260601"

  - name: gcp-failover
    type: google-cloud
    region: us-central1
    priority: 2
    project_id: "my-gcp-project"
    models:
      - "claude-sonnet-5@20260601"

  - name: anthropic-direct
    type: anthropic
    api_key: "${ANTHROPIC_API_KEY}"
    priority: 3

budgets:
  default:
    daily: 50
    monthly: 1000
  groups:
    engineering:
      daily: 100
      monthly: 2000
    interns:
      daily: 10
      monthly: 200

telemetry:
  otlp_endpoint: "https://otel-collector.example.com:4318"
  headers:
    "X-API-Key": "${OTEL_API_KEY}"
```

### 3. Deploy the Gateway Container

The gateway runs as a single process. For Docker Compose:

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: gateway
      POSTGRES_USER: gateway
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
    volumes:
      - pgdata:/var/lib/postgresql/data

  gateway:
    image: claude-gateway  # included in claude binary distribution
    ports:
      - "8443:8443"
    environment:
      OIDC_CLIENT_SECRET: "${OIDC_CLIENT_SECRET}"
      DATABASE_URL: "postgresql://gateway:${DB_PASSWORD}@postgres:5432/gateway"
      ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
    volumes:
      - ./gateway.yaml:/etc/claude/gateway.yaml
    command: ["claude", "gateway", "--config", "/etc/claude/gateway.yaml"]
    depends_on:
      - postgres
```

For Kubernetes, use a standard Deployment with a ConfigMap for the YAML and a Secret for credentials. The gateway doesn't require special permissions — it's just an HTTP server.

### 4. Connect Developers

Developers configure their Claude Code CLI with a single environment variable:

```bash
export CLAUDE_GATEWAY_URL="https://claude-gateway.example.com"
```

On first request, the CLI opens a browser window to authenticate through your IdP. After that, the gateway issues a session token. The developer never sees an API key, never configures a model, and never worries about which provider they're hitting.

### 5. Configure Managed Settings and Policies

This is where the gateway shines for platform teams. You can push managed settings centrally — which models are available, what the max token limit is, whether tool use is allowed — without touching developer machines. The gateway enforces these settings on every request.

IdP groups map to model allowlists and policy tiers. For example, you can allow the full Claude Sonnet 5 1M-token context window for senior engineers while restricting interns to Claude Haiku 5 with a 32K-token cap. The group mapping is configured in the gateway YAML under a `policies` section.

### 6. Set Up Telemetry and Monitoring

The gateway emits OpenTelemetry Protocol (OTLP) metrics with:

- Token counts (input and output per request)
- Model identifier
- User identity (email from OIDC)
- Request latency
- Provider used
- Budget status

You can ship this to Datadog, Splunk, Grafana, or any OTLP-compatible collector. I route mine through a local OpenTelemetry Collector that fans out to Grafana for dashboards and S3 for long-term audit storage.

## Multi-Cloud Routing and Failover

The gateway supports provider routing with priority-based failover. In the config above, requests go to Amazon Bedrock (priority 1) first. If Bedrock returns a 503 or times out, the gateway automatically fails over to Google Cloud Vertex AI (priority 2). If both cloud providers are down, it falls back to the Anthropic API directly (priority 3).

This is useful for two reasons. First, it gives you a single endpoint that stays up even when one cloud region has an outage. Second, it lets you negotiate better pricing — you can route most traffic through your committed-spend cloud provider and only spill over to direct Anthropic API when needed.

The gateway handles protocol translation transparently. Clients speak the Anthropic Messages API, and the gateway translates to Bedrock's `InvokeModel` or Google Cloud's Vertex AI format. Your developers don't need to know or care which provider is serving their request.

## Spend Caps and Cost Control

The budget system supports daily, weekly, and monthly caps at three levels: organization-wide, per group, and per user. When a cap is hit, the gateway returns HTTP 429 with a clear error message. The developer sees "Budget exceeded — contact your admin" instead of a cryptic API error.

I've found the group-level caps to be the most useful. You set a generous monthly budget for the engineering team, a tighter one for contractors, and a minimal one for interns or trial users. The gateway tracks spend in PostgreSQL, so caps are enforced consistently across all replicas.

Claude Sonnet 5 pricing through the gateway depends on your provider. If you're routing through Bedrock or Vertex AI, you pay those cloud providers directly. If you're routing through the Anthropic API, the introductory pricing through August 31, 2026 is $2 per million input tokens and $10 per million output tokens. After that, standard pricing is $3/$15. Sonnet 5 ships with a native 1M-token context window, which is worth factoring into your budget calculations — a single large-context request can burn through a meaningful chunk of your daily cap.

## Security and Compliance Considerations

The gateway must be deployed on a private network. Claude Code only connects to private gateway addresses, so there's no public attack surface. All inference traffic stays inside your VPC when routed through Bedrock or Vertex AI — Anthropic never sees your code or prompts. This is the only self-hosted option for regulated industries (financial services, healthcare, government) that require VPC deployment.

The OIDC integration means you inherit your corporate IdP's security policies: MFA requirements, device compliance checks, session timeout policies, and IP allowlisting. If your IdP requires MFA for the Claude Code application, developers authenticate with MFA through the gateway.

For audit trails, the OTLP telemetry gives you a complete record of who called which model, when, with how many tokens, and through which provider. This satisfies most SOC 2 and ISO 27001 audit requirements for AI tool usage.

## Comparison: Claude Apps Gateway vs. Other LLM Gateways

The Claude Apps Gateway is not the only LLM gateway on the market, but it's the only one that's purpose-built for Claude Code. Here's how it compares:

| Feature | Claude Apps Gateway | Cloudflare AI Gateway | AWS A2A Gateway |
|---|---|---|---|
| OIDC SSO | Built-in | Via Cloudflare Access | Via Cognito/OIDC |
| Claude Code integration | Native (built into claude binary) | HTTP proxy | HTTP proxy |
| Multi-cloud failover | Yes (Bedrock, GCP, Foundry, Anthropic) | Yes (any OpenAI-compatible) | AWS-native only |
| Spend caps | Per-org, per-group, per-user | Per-request only | Via AWS Budgets |
| OTLP telemetry | Native | Via Cloudflare Logpush | Via CloudWatch |
| VPC deployment | Required (private network only) | Cloudflare network | AWS VPC |
| Protocol translation | Anthropic Messages → provider format | OpenAI-compatible only | OpenAI-compatible only |

The key differentiator is the native Claude Code integration. Other gateways speak the OpenAI API format and require you to configure model mappings manually. The Claude Apps Gateway speaks Anthropic's Messages API natively and handles the translation to Bedrock, Vertex AI, or Foundry automatically. If you're a Claude Code shop, the native integration saves you a configuration layer and eliminates protocol mismatch issues.

## Troubleshooting Common Issues

**OIDC callback fails with redirect_uri mismatch.** Double-check that the redirect URI in your IdP application registration exactly matches `https://<gateway-hostname>/oauth/callback` — no trailing slash, no extra path. This is the most common setup mistake.

**Users authenticated but get "no models available."** Check the group-to-model mapping in your gateway config. If the user's IdP groups don't match any configured policy, the gateway defaults to denying access. Add a `default` policy that covers ungrouped users.

**Spend cap returns 429 even though the cap hasn't been hit.** The gateway uses PostgreSQL for spend tracking. If the database connection is slow or the gateway can't reach PostgreSQL, it defaults to denying requests. Check that `database.url` is reachable and that connection pooling is configured correctly.

**Failover doesn't trigger.** The gateway only fails over on 5xx errors and timeouts. A 400-level error (like an invalid model name) won't trigger failover. Check your provider configuration and model name mappings.

## Is the Claude Apps Gateway Right for You?

If you have more than 10 developers using Claude Code, the gateway pays for itself in reduced API key management overhead alone. The spend caps prevent budget surprises — I've seen teams cut their Claude Code costs by 30-40% just by setting per-user monthly caps and letting developers see their own usage.

If you're in a regulated industry that requires VPC deployment, the gateway is currently the only self-hosted option for Claude Code. The combination of OIDC SSO, VPC isolation, and OTLP audit trails covers most compliance requirements out of the box.

If you have fewer than 5 developers and no compliance requirements, the gateway is probably overkill. The per-developer API key model works fine at that scale. But keep it in mind for when you grow — the migration path is straightforward since the gateway speaks the same Messages API that developers already use.

For more on enterprise AI governance, check out my guide on [AWS MCP Gateway Registry](/posts/aws-mcp-gateway-registry-guide-2026/) for governing MCP servers at scale, and the [GitHub Copilot AI Cost Centers guide](/posts/github-copilot-ai-cost-centers-guide-2026/) for a comparison on how other platforms handle AI cost management.
