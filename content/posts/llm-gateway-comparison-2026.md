---
title: "LLM Gateway Comparison 2026: Portkey vs Helicone vs LiteLLM After the Shakeup"
date: 2026-05-21T09:34:26+00:00
tags: ["llm gateway", "portkey", "helicone", "litellm", "ai infrastructure", "llm routing"]
description: "Helicone was acquired and LiteLLM was compromised in 2026. Here's how Portkey, LiteLLM, Helicone, and emerging alternatives compare for routing, cost, and reliability."
draft: false
cover:
  image: "/images/llm-gateway-comparison-2026.png"
  alt: "LLM Gateway Comparison 2026: Portkey vs Helicone vs LiteLLM"
  relative: false
schema: "schema-llm-gateway-comparison-2026"
---

The short answer: **Portkey** is the best drop-in replacement if you're running Helicone or evaluating alternatives after the LiteLLM security scare. It covers 200+ providers, adds under 1ms of latency, and gives you routing, caching, and observability in a single package. LiteLLM is still viable for self-hosted open-source use if you pin a pre-compromise version and monitor CVEs actively.

## Why 2026 Is the Year of LLM Gateway Evaluation

The LLM gateway market hit a turning point in early 2026 with two simultaneous events that forced teams to re-evaluate their infrastructure. On March 3, 2026, Helicone was acquired by Mintlify — the documentation platform — and immediately entered maintenance mode, meaning no new features, only security patches and bug fixes. Within the same quarter, LiteLLM suffered a documented security compromise that raised concerns about the supply chain security of open-source proxy deployments. These two events hit simultaneously at a moment when enterprise LLM API spending had already grown from $3.5B in late 2024 to $8.4B by mid-2025 — a 2.4x increase in roughly six months. Teams that had quietly been running Helicone for observability or LiteLLM for routing suddenly had urgent migration decisions to make. Add to this that 37% of enterprises now run five or more LLMs in production, and the case for a robust, multi-provider gateway has never been stronger. This guide evaluates your real options with the current market in mind.

### Helicone Acquisition: What It Means for Users

Helicone joining Mintlify is good news for Mintlify's documentation product and bad news for teams relying on Helicone as an active LLM observability gateway. The official announcement confirmed the product is in maintenance mode: the team moved to San Francisco to work on Mintlify's core product. What this means practically is that any open issue you've filed is likely to stay open. Feature requests are dead. If you've built internal tooling around Helicone's API, you're on borrowed time. The proxy still works — it passes requests through and logs them — but you're now running a deprecated dependency with no clear sunset date. The sensible move is a planned migration rather than waiting for the surprise end-of-life notice.

### LiteLLM Security Compromise: How to Respond

The LiteLLM security incident in 2026 was a supply chain compromise — a compromised dependency in a specific version range. If you're running LiteLLM in a production environment and haven't audited your version and its transitive dependencies since early 2026, you need to. The community response was fast, and patched versions are available, but the incident highlighted a real risk with open-source proxies: you inherit the attack surface of every library they pull in. Enterprise teams running LiteLLM behind their API gateway got largely got away with shallow exposure, but teams with direct internet-facing LiteLLM deployments had a harder time. The takeaway isn't "never use LiteLLM" — it's "apply the same supply chain hygiene to your AI infrastructure as you would to any other production service."

## LLM Gateway Comparison: Portkey vs Helicone vs LiteLLM

The three tools in this comparison serve overlapping but distinct purposes, and their architecture choices reflect different bets about what matters most. Portkey is a commercial cloud gateway built for multi-provider routing at enterprise scale, supporting over 200 LLM providers with advanced routing logic, semantic caching, and built-in observability. Helicone was a proxy-based observability layer optimized for logging and monitoring — it sat in front of your LLM calls and captured metadata — but it was never primarily a routing engine. LiteLLM is the open-source universal interface that lets you call any LLM with the OpenAI SDK format, typically deployed self-hosted. Each of these sits at a different point on the control vs. convenience spectrum. Portkey maximizes capabilities at the cost of vendor dependency. LiteLLM maximizes control at the cost of operational overhead. Helicone, in maintenance mode, is the tool you're probably migrating away from. Enterprise LLM spending growth and the 37% figure on multi-LLM production deployments make clear that the routing and cost-optimization layer — Portkey's core value prop — matters more than ever.

### Portkey: Multi-Provider Enterprise Gateway

Portkey is the most feature-complete option in this comparison. The gateway supports 200+ LLM providers with a unified API surface. You get routing rules that span load balancing, fallback chains, and model-specific cost thresholds. Semantic caching — where Portkey recognizes semantically similar requests and serves cached responses — can cut costs meaningfully on high-traffic patterns. The observability layer captures latency, cost per call, token usage, and error rates across all providers. Setup is a one-line base URL swap if you're already using OpenAI's SDK format.

For teams migrating from Helicone, the operational continuity is smooth. Portkey's API is compatible with the same request/response format you're already using. The paid tier starts at $49/month for production use. There's a free tier for low-volume testing.

### Helicone: Maintenance Mode Reality Check

Helicone's architecture was a lightweight proxy that sat between your application and any LLM API. It added minimal latency — roughly 1-2ms — and captured extensive request/response logs. The dashboard was genuinely useful for cost tracking and debugging prompt regressions. But the acquisition changed the calculus. If you're still running Helicone, you should audit your integration against Mintlify's official maintenance mode statement: security patches and new model support only. No new features. Your logs are fine, your existing integrations work, but you're accumulating technical debt with every month you stay on it.

The migration path is straightforward. Portkey and Langfuse both offer Helicone-compatible logging adapters. The observability use case maps cleanly to either, while Portkey additionally covers the routing and cost-optimization angles Helicone never touched.

### LiteLLM: Open-Source Power With Operational Cost

LiteLLM's core promise — call 100+ LLMs with a single SDK interface — remains valid and useful. The proxy server mode gives you a self-hosted gateway that your team controls entirely. For teams with strong infrastructure preferences, data sovereignty requirements, or cost sensitivity at scale, LiteLLM's self-hosted deployment still makes sense.

The operational overhead is real, though. You own the deployment, the uptime, the version upgrades, and now, explicitly, the security audits. The 2026 compromise was a wakeup call for teams treating LiteLLM as a set-and-forget proxy. If you maintain LiteLLM, commit to a dependency audit cadence and subscribe to their security advisories.

The Python bottleneck is also worth acknowledging. Under heavy load — around 500+ requests per second — LiteLLM's Python-based routing adds measurable latency compared to alternatives like Bifrost (a Rust-based gateway that adds only 11 microseconds at 5,000 RPS). For most teams, this isn't a real-world constraint, but it matters for latency-sensitive applications.

## Key Differentiators: Feature Comparison Table

Choosing between LLM gateways means understanding where each tool draws its architectural boundaries. Portkey is a commercial gateway with routing and caching as core capabilities — it's not just an observability layer. Helicone was built specifically as an observability proxy that logged requests without modifying them, which is why it never shipped routing features. LiteLLM started as a Python abstraction layer (call any model with OpenAI syntax) and grew a self-hostable proxy server on top. These origins matter because they determine what each tool does well under production conditions. Portkey's routing handles provider outages transparently — if Anthropic returns a 529, Portkey reraises to your configured fallback without your application seeing the error. LiteLLM's routing requires explicit fallback configuration and re-raises errors differently. Helicone passed everything through with no modification, which was its strength (no risk of altering requests) and its ceiling (no ability to add intelligence). Understanding these architectural commitments helps explain the feature gaps in the table below.

| Feature | Portkey | Helicone | LiteLLM |
|---|---|---|---|
| Provider Support | 200+ | Any (proxy) | 100+ |
| Routing & Fallbacks | Yes (advanced) | No | Yes (basic) |
| Semantic Caching | Yes | No | Limited |
| Observability | Yes (built-in) | Yes (core feature) | Limited |
| Self-Hosted | Paid enterprise | Open source | Yes (free) |
| Maintenance Status | Active | Maintenance mode | Active (post-patch) |
| Latency Overhead | ~1ms | ~1-2ms | ~2-5ms (Python) |
| Security Compliance | SOC 2 Type II | N/A (maintenance) | Self-managed |
| Pricing | Free + $49/mo | Free (maintenance) | Free (self-hosted) |

### Provider Support: The Numbers Matter

Provider support at 200+ (Portkey) versus 100+ (LiteLLM) sounds like a marketing number until you need a specific model. In practice, the models you can't route through your gateway are the ones you end up calling directly — which creates a two-tier infrastructure and an observability gap. Portkey's broader coverage means you're less likely to hit the "this model isn't supported yet" wall when a new provider launches. LiteLLM's community-driven model additions are fast but depend on contributor bandwidth.

### Routing Capabilities: Where Portkey Pulls Ahead

Load balancing across providers, automatic fallback chains, and cost-threshold routing are features Portkey was built around from day one. If your primary call to GPT-4o fails, Portkey can automatically retry with Claude 3.5 Sonnet or any other fallback you configure. You can set rules like "use the cheapest model that meets this latency threshold" or "failover to self-hosted Llama if OpenAI returns a 429."

LiteLLM has basic fallback support, but the configuration is more manual and the routing logic less sophisticated. Helicone never offered routing at all — it was observation-only.

### Security and Compliance: Portkey vs Self-Managed

Portkey holds SOC 2 Type II certification. For enterprise teams with compliance requirements, this matters more than feature lists. LiteLLM self-hosted means you're taking on the compliance posture yourself — which is fine if you have the infrastructure team to back it, but not fine if you're a startup trying to close an enterprise deal.

## Deployment Options: Cloud vs Self-Hosted vs Hybrid

Your deployment choice should be driven by data residency requirements, team operational capacity, and scale.

**Cloud (Portkey):** Fastest path to production. No infrastructure to manage. Data goes through Portkey's cloud, which is a non-starter for some regulated industries. Appropriate for most teams that don't have explicit data sovereignty requirements.

**Self-Hosted (LiteLLM):** Maximum control, maximum operational burden. Your data never leaves your infrastructure. Appropriate for financial services, healthcare, government, or any team with explicit data residency requirements. Requires a committed infrastructure owner.

**Hybrid:** Some teams run Portkey for external providers while keeping a self-hosted LiteLLM instance for calls to internal or on-premises models. This adds architectural complexity but gives you the best of both worlds for specific use cases.

Helicone had a self-hosted Docker option, but maintenance mode makes it risky to build new deployments on it.

## Real-World Migration Scenarios

The 2026 LLM gateway shakeup created three migration pressures simultaneously: Helicone users needing an actively developed replacement, LiteLLM users evaluating security posture, and teams still on bare-metal API calls realizing they need centralized cost management as their LLM spend scales. Each scenario has a different urgency and a different technical path. Helicone-to-Portkey is the cleanest migration: both use OpenAI-compatible API surfaces and the base URL swap is a one-line change in most codebases. LiteLLM-to-Portkey requires more careful alias mapping but eliminates the operational burden of running your own Python gateway process. Teams moving from direct API calls to a gateway for the first time need to decide between control (LiteLLM self-hosted) and convenience (Portkey cloud). What follows are concrete migration paths for each scenario, drawn from common deployment patterns rather than theoretical examples. Smart routing combined with caching — something you get from day one with Portkey — achieves 47–80% cost reduction in production AI systems, which typically pays for the migration effort within weeks.

### Migrating from Helicone to Portkey

The migration is a two-line change for most applications. Portkey uses the same OpenAI-compatible API surface. You swap your base URL from `https://oai.helicone.ai/v1` to `https://api.portkey.ai/v1` and add a `x-portkey-api-key` header. Your existing observability logging continues. You gain routing, caching, and a broader provider surface on top of what Helicone provided.

The one gotcha: Helicone's custom request metadata fields don't map 1:1 to Portkey's tagging system. If you've built reporting dashboards that depend on Helicone's specific log schema, you'll need to update those queries. The data is all there in Portkey — it just uses different field names.

### Migrating from LiteLLM to Portkey

If you moved off LiteLLM due to the security concerns or operational complexity, Portkey covers the same routing use cases with less maintenance burden. The critical difference: LiteLLM in proxy mode let you configure arbitrary model aliases that your application code never needed to change. Portkey's virtual key system achieves the same result. Audit your `config.yaml` to identify which provider aliases your application uses, map them to Portkey virtual keys, and update your base URL.

### Cost Optimization: Achieving 47-80% Savings With Gateway Routing

The cost-optimization case for an LLM gateway is compelling at scale. Smart routing combined with semantic caching achieves 47-80% cost reduction in production AI systems, according to benchmarks from teams like Mavik Labs. The mechanism: route simple queries to cheaper models (simple queries cost ~$0.10/M tokens vs complex coding tasks at ~$30/M — a 300x gap), cache semantically similar requests to avoid redundant API calls, and set cost-per-call thresholds that trigger automatic model downgrades.

RouteLLM from UC Berkeley demonstrated 85% cost reduction on MT Bench benchmarks while maintaining 95% of GPT-4 performance quality. These numbers don't translate directly to every workload, but they establish the ceiling of what's achievable with intelligent routing.

## Future Trends: AI Gateway Landscape 2026–2030

The AI gateway layer is actively converging with agent orchestration infrastructure, and the tools that survive the next three years will be those that understand requests as part of longer workflows rather than isolated API calls. Current gateways treat each LLM call independently — you pass in a prompt, you get back a completion, the gateway logs cost and latency. But 40% of enterprise applications will embed task-specific AI agents by end of 2026 (Gartner), and those agents make dozens or hundreds of interdependent calls per task. A gateway that optimizes each call independently may actually harm agent performance by switching models mid-workflow, breaking the conversational context that a more expensive model was maintaining. The next generation of LLM gateways will need workflow-aware routing: understanding that calls belong to a session, that consistency across a task may outweigh per-call cost savings, and that agent failures have different recovery paths than single-call failures. Portkey's virtual session concept is early movement in this direction, but no gateway has fully solved workflow-aware routing yet. Here's where the three dimensions of future development are heading.

The gateway layer is converging toward three capabilities that current tools don't fully address:

**Agent-aware routing:** Current gateways treat every request as independent. The next generation will understand that a request is part of an agentic workflow and route accordingly — holding a model selection stable across a multi-step task rather than optimizing each call in isolation.

**MCP integration:** The Model Context Protocol is becoming the standard interface for tool use and context management. Gateways that integrate natively with MCP will be able to route based on tool availability, context size, and agent capability requirements.

**Real-time cost arbitrage:** As model pricing changes dynamically and new providers emerge monthly, gateways will need real-time pricing feeds and automated routing adjustments rather than static configuration.

## Decision Framework: Which Gateway Is Right for Your Team

**Choose Portkey if:**
- You're migrating from Helicone and want operational continuity
- You need SOC 2 compliance without building it yourself
- You're running multiple LLM providers and want centralized routing
- You want semantic caching without implementing it yourself

**Choose LiteLLM (self-hosted, post-audit) if:**
- You have strict data residency requirements
- You have the infrastructure team to maintain it
- You need to support on-premises or private model deployments
- Cost of commercial tools is prohibitive at your scale

**Stay on Helicone only if:**
- You're in active migration to an alternative
- Your use case is purely observability and you accept zero new features

**Consider Bifrost if:**
- Latency is your primary constraint (11μs overhead at 5,000 RPS)
- You're building latency-sensitive real-time applications
- You're comfortable with a less mature but extremely fast Rust-based option

## FAQ

**Is Helicone still safe to use in 2026?**
Yes, but with caveats. Helicone is in maintenance mode — security patches and new model support only. The proxy works and your existing integrations are stable, but you're accumulating technical debt. Plan your migration to an actively developed alternative within the next 6-12 months.

**Is LiteLLM safe to use after the 2026 security compromise?**
Yes, if you're running a patched version. The LiteLLM team released fixes quickly after the compromise was disclosed. Pin a verified version, subscribe to their security advisories (GitHub Dependabot or their mailing list), and run regular dependency audits. Self-hosted means you own the security posture.

**How much does Portkey cost for a production deployment?**
Portkey's paid tier starts at $49/month. For high-volume teams, they offer enterprise pricing. There's a free tier for development and low-volume testing. Given that a properly configured Portkey routing setup typically reduces total LLM spend by 20-50%, the gateway cost is usually a fraction of the savings it generates.

**What's the latency overhead of adding an LLM gateway?**
For Portkey and Helicone-style proxies, expect 1-3ms of added latency. Rust-based gateways like Bifrost add only 11 microseconds. LiteLLM's Python implementation adds roughly 2-5ms under normal load, with degradation at high concurrency. For most AI applications where LLM inference itself takes 500ms+, gateway overhead is effectively invisible.

**Can I run multiple gateways simultaneously?**
Yes, and some teams do. A common pattern: Portkey for external cloud providers (OpenAI, Anthropic, Gemini) and a self-hosted LiteLLM instance for internal or on-premises models. The added complexity is usually worth it for organizations with hybrid cloud and on-premises AI deployments. Route to the right gateway based on model name in your application config.
