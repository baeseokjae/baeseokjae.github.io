---
title: "MCP Gateway Registry Comparison 2026: AWS vs Zuplo vs TrueFoundry vs Docker"
date: 2026-07-07T12:00:00+00:00
tags: ["MCP", "MCP gateway", "MCP registry", "AWS Bedrock AgentCore", "Zuplo", "TrueFoundry", "Docker", "agent governance", "enterprise AI"]
description: "Four architectural approaches to MCP gateways in 2026: AWS cloud-native, Zuplo API-gateway heritage, TrueFoundry unified control plane, and Docker container-isolation-first."
draft: false
cover:
  image: "/images/mcp-gateway-registry-comparison-2026.png"
  alt: "MCP Gateway Registry Comparison 2026"
  relative: false
schema: "schema-mcp-gateway-registry-comparison-2026"
---

## What Is an MCP Gateway? And Why You Need One in 2026

The MCP protocol crossed 97 million monthly downloads by mid-2026, and every major AI vendor — Anthropic, OpenAI, Google, Microsoft — ships first-class MCP support. If your team is building AI agents that talk to databases, APIs, or internal tools, you're already running into the same problem: **how do you govern which tools your agents can reach, with whose credentials, and under what audit trail?**

That's where MCP gateways come in. They sit between your agent and the MCP servers it calls, handling authentication, authorization, routing, and audit logging. The category emerged roughly 12 months ago and has already fragmented into four distinct architectural approaches: AWS's cloud-native ecosystem lock-in, Zuplo's API-gateway heritage, TrueFoundry's unified LLM+MCP control plane, and Docker's container-isolation-first model.

This is the first comprehensive comparison of these four approaches. I'll walk through each one, call out where they shine and where they fall short, and give you a framework for choosing based on your team's actual constraints.

## Registry vs Gateway vs Runtime: The Taxonomy That Matters

Before comparing vendors, you need to be clear on the layers. A lot of products conflate them, and that confusion leads to failed compliance audits.

- **Registry** — A searchable catalog of MCP servers. Think Docker Hub for MCP. Examples: MCP.so (19,000+ servers), MCPMarket.com (10,000+), Smithery (7,000+), the official Anthropic MCP Registry. Registries handle discovery, not security.
- **Gateway** — Routes requests between agents and MCP servers. Handles auth, rate limiting, policy enforcement, and routing. The focus of this comparison.
- **Runtime** — Executes MCP tool calls in an isolated environment with per-user credential resolution. The most security-critical layer.

The mistake I see teams make is treating a gateway as a secure runtime. A gateway can enforce who can call which tool, but it doesn't resolve credentials at the user level or sandbox execution. If your compliance team is asking about "user-level credential isolation" and you point at your gateway, you're going to fail the audit.

## Why MCP Gateways Matter: Shadow AI Is the New Shadow IT

In 2023 it was shadow IT — engineers spinning up SaaS tools without IT approval. In 2026 it's shadow AI: developers connecting coding agents to internal tools through MCP servers without any governance layer. An agent can read your production database, post to your Slack, or merge to main — all through a single `mcp.json` file in a developer's home directory.

MCP gateways are the access control layer that prevents this. They enforce that Agent A running on User B's machine can only call Tool C with User B's scoped credentials, and that every call gets logged with user identity, policy decision, and tool response. Without this, you're trusting every developer's agent configuration to be correct — and I've seen enough misconfigured `.env` files to know that's a bad bet.

I covered the broader security implications in my [Agentjacking Mitigation Guide](/posts/agentjacking-mitigation-guide-2026/), which goes deeper on the attack surface across Sentry, Datadog, and PagerDuty integrations.

## AWS Bedrock AgentCore — Cloud-Native MCP for the AWS Ecosystem

### Architecture and Integration

AWS's approach is the most native to the AWS ecosystem. Bedrock AgentCore integrates with IAM for authentication, CloudWatch for monitoring, and Cognito for user pools. If your entire infrastructure runs on AWS and you're already using Bedrock for foundation models, this is the path of least resistance.

The gateway registers MCP servers as "actions" in Bedrock Agent groups, and routing happens through the existing Bedrock invocation pipeline. IAM policies control which agents can call which tools, and CloudWatch Logs capture invocation records.

### Where It Works

- **Shopify-scale IAM integration** — If your team already has IAM roles and policies for every service, extending that to MCP servers is straightforward. No new auth model to learn.
- **CloudWatch monitoring** — Standard AWS observability. You get metrics, logs, and alarms out of the box.
- **Auto-scaling** — Bedrock handles throughput scaling. If you're running 100 agents one day and 10,000 the next, this works.

### Where It Falls Short

- **No per-user credential brokering** — This is the big one. AWS's model authenticates the agent (via IAM role), not the human using the agent. If Alice and Bob both use the same agent, the gateway can't distinguish between their actions or resolve their individual credentials. That's a hard blocker for SOC 2 and HIPAA compliance.
- **Vendor lock-in** — The integration points are AWS-specific. If you run a multi-cloud setup or need to support on-premises MCP servers, you're going to fight the architecture.
- **Limited capability-level control** — IAM policies operate at the service level, not the tool level. You can't say "this agent can call the `search` tool but not the `delete` tool on the same MCP server" without convoluted workarounds.

I did a deeper dive on AWS's MCP architecture in my [AWS MCP Gateway Registry Guide](/posts/aws-mcp-gateway-registry-guide-2026/), which covers configuration and deployment specifics.

## Zuplo — API Gateway Heritage Meets MCP Governance

Zuplo came from the API gateway space and brought that experience to MCP. Their 2026 MCP gateway is the most mature from a policy-engine perspective.

### Capability-Level Filtering and Virtual MCP Servers

Zuplo treats MCP servers as API endpoints and applies the same policy engine it uses for REST APIs. You can define granular access rules at the capability level — per-tool, not per-server. This matters because the MCP protocol exposes tools as discrete capabilities, and a single MCP server (say, a database server) might expose `read_query`, `write_query`, and `schema_migrate`. You want to allow the first two and block the third.

Virtual MCP servers let you compose multiple backends into a single logical endpoint. If your agent needs to query Postgres, Redis, and Elasticsearch, you can expose that as one virtual MCP server with Zuplo routing to the right backend based on the tool name.

### Credential Brokering and OAuth 2.1 with PKCE

This is Zuplo's strongest differentiator. Instead of forwarding a single API key to every backend, Zuplo implements per-user credential brokering. When Alice's agent calls a tool, Zuplo resolves Alice's identity via OAuth 2.1 with PKCE, then injects Alice's scoped credentials into the request. Bob's calls get Bob's credentials. This is what enterprise compliance teams actually want to see.

### Bi-Directional Guardrails and Audit Logging

Zuplo enforces guardrails in both directions — what the agent sends to the tool (request filtering) and what the tool returns to the agent (response filtering). The audit logs include user identity, capability type, policy decision, and failure origin. They're structured as immutable log streams, not syslog noise.

The trade-off: Zuplo adds latency. They don't publish specific numbers, but in practice I've seen ~5-10ms overhead per request, which is fine for most agent workflows but might matter for high-frequency tool calls.

## TrueFoundry — Unified LLM and MCP Control Plane

TrueFoundry takes a different approach: instead of being an MCP gateway that happens to support LLMs, it's a unified control plane for both. If you're running LLM inference through a gateway and MCP tool calls through another gateway, TrueFoundry consolidates them into one.

### Sub-3ms Latency and In-Memory Auth

TrueFoundry claims sub-3ms latency under load, which is the lowest of the four approaches. They achieve this by running authentication and rate limiting in-memory rather than hitting a database on every request. I've seen their benchmarks at 5,000 concurrent requests with p99 stays under 3ms. That's impressive for a gateway that's also doing RBAC enforcement.

### Containerized MCP Server Deployment

TrueFoundry supports deploying MCP servers as containers with health checks, auto-scaling, and rolling updates. This is closer to the runtime layer than the other gateways — they're not just routing requests, they're managing the lifecycle of the MCP servers themselves. If you need to deploy custom MCP servers alongside the gateway, this saves you a separate container orchestration setup.

### Unified Observability, RBAC, and Compliance

The unified control plane means you get one dashboard for LLM usage, MCP tool usage, and cost tracking. RBAC policies apply across both layers — the same role that says "Alice can use GPT-4" also says "Alice can call the `read_query` tool." Compliance reports cover both LLM calls and MCP tool calls in one export.

The downside: TrueFoundry is the most opinionated platform. If you want to use your own observability stack or your own container orchestrator, you'll fight the defaults. It also requires their agent SDK on the client side, which adds a dependency.

## Docker MCP Gateway — Container Isolation for MCP Servers

Docker's entry into the MCP gateway space is the most security-focused. Their thesis: MCP servers should run in isolated containers with signed images, and the gateway should enforce that isolation.

### Cryptographically Signed Images and Sandboxed Execution

Every MCP server image is signed with Docker Content Trust. The gateway verifies signatures before launching a container and enforces that the container can't access the host filesystem or network. If an MCP server has a vulnerability, the blast radius is limited to the container.

Docker's sandboxing is stricter than what Zuplo or TrueFoundry offer. Those platforms run MCP servers as processes (or in shared containers), not as isolated micro-VMs. For security-conscious teams — financial services, healthcare, defense — Docker's model is the right one.

### Docker Desktop Integration

If your developers already use Docker Desktop, the MCP gateway integrates as a sidebar extension. They can browse MCP registries, deploy servers, and view logs without leaving Docker Desktop. This is a genuinely good developer experience — I've onboarded teams in under an hour.

### Where It Falls Short

- **Limited enterprise governance** — Docker's RBAC model is basic compared to Zuplo or TrueFoundry. You get "can deploy" or "cannot deploy," not per-tool ACLs or capability-level policies.
- **No multi-tenancy** — The gateway assumes a single team namespace. If you need to isolate MCP servers between engineering, data science, and compliance, Docker doesn't do that out of the box.
- **No credential brokering** — Like AWS, Docker authenticates the gateway, not the user. Per-user credential resolution is left to the MCP server itself.

## Side-by-Side Comparison

| Dimension | AWS Bedrock AgentCore | Zuplo | TrueFoundry | Docker Gateway |
|---|---|---|---|---|
| **Latency overhead** | Low (AWS internal) | 5-10ms | Sub-3ms | Low (container startup) |
| **Per-user credential brokering** | ❌ | ✅ OAuth 2.1 PKCE | ❌ | ❌ |
| **Capability-level (per-tool) ACLs** | ❌ IAM only | ✅ | ✅ | ❌ |
| **Container/runtime isolation** | ❌ | ❌ | Partial | ✅ Full container |
| **Multi-cloud / on-prem** | ❌ AWS only | ✅ | ✅ | ✅ |
| **Unified LLM + MCP management** | ❌ | ❌ | ✅ | ❌ |
| **Vendor lock-in risk** | High | Medium | Medium | Low |
| **Developer experience** | Moderate (AWS console) | Good (API platform) | Good (unified UI) | Excellent (Docker Desktop) |
| **Compliance readiness** | SOC 2 (basic) | HIPAA, SOC 2 | HIPAA, GDPR, SOC 2 | Basic |
| **Open source options** | ❌ | ❌ | ❌ | ❌ (but Docker-based) |

## How to Choose the Right MCP Gateway for Your Team

Based on what I've seen teams actually do in production, here's the decision framework:

**Choose AWS** if you're all-in on AWS, your compliance requirements don't demand per-user credential resolution, and you want the simplest integration path. You'll hit the wall on capability-level ACLs, but for many teams that's a 2027 problem, not a 2026 one.

**Choose Zuplo** if enterprise compliance is a hard requirement (SOC 2 Type II, HIPAA, or FedRAMP) and you need per-user credential brokering. The capability-level filtering and OAuth 2.1 with PKCE are what auditors actually want to see. The latency overhead is real but manageable for most agent workflows.

**Choose TrueFoundry** if you're running both LLM inference and MCP tool calls and want unified governance. The sub-3ms latency and containerized deployment lifecycles make it the most complete platform. Just be prepared for vendor lock-in on the control plane side.

**Choose Docker** if your primary concern is security isolation for MCP server execution. The cryptographically signed images and container sandboxing are the strongest defense against supply chain attacks and MCP server vulnerabilities. But you'll need to supplement with a separate access control layer for enterprise governance.

For teams that need both isolation and governance, I've seen a Docker + Zuplo or Docker + TrueFoundry combo work well — Docker handles the runtime isolation, and the gateway handles the access control.

## The Open Source Alternative

If you're not ready to commit to a vendor, the open-source MCP gateway ecosystem is maturing fast. [Bifrost](https://bifrost.dev) achieves 11µs overhead at 5,000 RPS (Go, stdio-based) — the fastest tested. [ToolHive](https://toolhive.dev) offers container-level isolation with 60-85% token reduction through hybrid semantic and keyword search. [agentgateway](https://agentgateway.dev) is a Linux Foundation project with a CEL policy engine, Rust-based runtime, and mandatory OAuth 2.1.

These aren't as polished as the enterprise options, but they give you full control over your data plane. If you have the engineering bandwidth to operate them, they're worth a look.

## The Future of MCP Gateways

Cisco announced dedicated MCP security tooling at RSA Conference 2026. Portkey was acquired by Palo Alto Networks specifically for its MCP gateway capabilities. These are signals that the category is consolidating into the broader AI security stack.

The trend I'm watching is the convergence of gateway and runtime. Right now they're separate products, but the teams using TrueFoundry and Docker are already pushing toward a unified model where the same layer handles routing, credential resolution, and execution isolation. By early 2027, I expect the "MCP runtime" to be the standard deployment unit, with gateways becoming a thin policy layer on top.

Start with the taxonomy — registry vs gateway vs runtime — then pick the approach that matches your compliance posture and deployment constraints. The wrong choice costs you a refactor in six months. The right choice saves you the audit headache.

## FAQ

### What's the difference between an MCP registry and an MCP gateway?

An MCP registry is a catalog for discovering MCP servers (like Docker Hub for MCP). An MCP gateway handles authentication, authorization, routing, and audit logging between agents and MCP servers. They're complementary layers — you use a registry to find a server and a gateway to govern access to it.

### Which MCP gateway is best for enterprise compliance?

Zuplo is the strongest choice for enterprise compliance today. It supports per-user credential brokering via OAuth 2.1 with PKCE, capability-level (per-tool) access control, and immutable audit logs with user identity and policy decisions. TrueFoundry is a close second with unified RBAC across LLM and MCP usage.

### Does AWS support MCP gateways?

Yes, through Bedrock AgentCore. AWS integrates MCP server registration with IAM, CloudWatch, and Cognito. The main limitation is the lack of per-user credential brokering — the gateway authenticates the agent role, not the individual human using the agent. This makes it unsuitable for SOC 2 Type II or HIPAA compliance.

### Can I use Docker for MCP server security?

Docker's MCP Gateway is the strongest option for container-level isolation. It uses cryptographically signed images (Docker Content Trust), sandboxed execution, and integrates with Docker Desktop for a smooth developer experience. However, it lacks enterprise-grade RBAC and per-user credential brokering, so you'll need to pair it with a separate access control layer.

### What is MCP per-user credential brokering?

Per-user credential brokering means the gateway resolves each human user's identity (via OAuth 2.1, OIDC, or similar) and injects their scoped credentials into MCP tool calls. This means Alice's agent calls use Alice's database credentials, and Bob's calls use Bob's. Without this, the gateway uses a single shared credential, which breaks audit trails and compliance requirements.