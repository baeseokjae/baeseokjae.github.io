---
cover:
  alt: 'UCP vs ACP 2026: Agent Commerce Protocols Compared'
  image: /images/ucp-vs-acp-agent-commerce-2026.png
  relative: false
date: 2026-07-13T20:00:00+00:00
description: 'UCP (Google) vs ACP (OpenAI/Stripe): two competing protocols for agent-led
  commerce in 2026. Architecture, adoption, trade-offs, and which one to bet on.'
draft: false
schema: schema-ucp-vs-acp-agent-commerce-2026
tags:
- UCP
- ACP
- Agent Commerce
- AI Agents
- Protocol
- Google
- OpenAI
- Stripe
title: 'UCP vs ACP 2026: Agent Commerce Protocols Compared'
---

## The Two Protocols Trying to Define How AI Agents Buy Things

By mid-2026, two competing standards are vying to become the default way AI agents handle commerce: Google's **Universal Commerce Protocol (UCP)** and OpenAI/Stripe's **Agentic Commerce Protocol (ACP)**. Both solve the same fundamental problem — how does an AI agent discover products, negotiate a purchase, and complete a transaction on behalf of a human — but they approach it from very different angles.

I've spent the last few weeks digging into both specs, reading the GitHub repos, and looking at who's actually implementing what. Here's what I found.

## What is UCP? Google's Universal Commerce Protocol

Google launched UCP in January 2026 as an open-source protocol co-developed with Shopify, Etsy, Wayfair, Target, and Walmart. It's backed by 20+ partners including Adyen, American Express, Best Buy, Mastercard, Stripe, and Visa. That's not a press release — those companies are listed as endorsing partners on the protocol's documentation.

UCP is designed as a **composable architecture** built around two core concepts: **Capabilities** and **Extensions**. A merchant declares what they can do (product listing, cart management, checkout, returns) through a standardized business profile, and agents discover those capabilities dynamically. The protocol is surface-agnostic — it works across chat, visual commerce, voice, and traditional web checkout.

Key architectural decisions:

- **Transports**: REST and JSON-RPC, with built-in support for A2A and MCP integration
- **Payments**: Integrates with AP2 (Agent Payments Protocol) for agent-initiated payments
- **Security**: Supports verifiable credentials and AP2 mandates for agent authorization
- **Merchant ownership**: The business remains Merchant of Record — full customer relationship ownership stays with the retailer

The UCP GitHub repo has **3,207 stars** as of July 2026, roughly 2.2x the community traction of ACP. Google is also expanding UCP beyond retail into lodging and food industries this year.

## What is ACP? OpenAI & Stripe's Agentic Commerce Protocol

ACP is maintained by OpenAI and Stripe, currently in beta. It defines the **Agentic Checkout Specification (ACS)** as a REST API contract that agents use to complete purchases. The merchant remains the system of record for orders, payments, taxes, and compliance — same fundamental principle as UCP, but the implementation is more focused.

ACP has shipped **six spec versions** since September 2025: 2025-09-29 (initial), 2025-12-12, 2026-01-16, 2026-01-30, and 2026-04-17. That's a rapid iteration cadence that tells me the OpenAI/Stripe team is actively responding to implementer feedback.

What ACP supports as of April 2026:

- **Capability negotiation**: Agents and merchants discover what each other can do
- **Payment handlers**: Multiple payment method support
- **Extensions**: Custom merchant-specific checkout flows
- **Discounts**: Agent-negotiated pricing and promotions
- **MCP integration**: Connects to the broader Model Context Protocol ecosystem

The ACP GitHub repo has **1,473 stars** — smaller than UCP, but the developer community is engaged and the issue tracker shows active discussion. ACP's tighter scope (checkout-first) means less surface area to implement, which matters for early adoption.

## Head-to-Head: UCP vs ACP

### Governance & Backing

UCP is a **broad industry coalition** led by Google. The partner list reads like a who's-who of retail and payments: Shopify, Etsy, Wayfair, Target, Walmart, Stripe, Visa, Mastercard, Adyen. That breadth gives UCP credibility with merchants who want to see their existing payment processors and retail platforms already on board.

ACP is a **two-company effort** (OpenAI + Stripe) with a narrower but deeper integration story. If you're already on Stripe for payments and using OpenAI for your AI stack, ACP is the path of least resistance. The question is whether that narrow focus becomes a strength (faster iteration, clearer decisions) or a weakness (harder to get Walmart and Target to adopt).

### Architecture & Design Philosophy

UCP is **composable and broad**. The Capabilities + Extensions model lets merchants expose exactly what they want, from full checkout to partial flows. The embedded option lets retailers customize the checkout experience rather than handing it entirely to the agent. This is the right design for large retailers who have existing checkout infrastructure and don't want to rip it out.

ACP is **checkout-focused and opinionated**. The Agentic Checkout Specification defines a clear contract: here's how an agent adds items, applies discounts, selects shipping, and completes payment. Less flexibility, less ambiguity. For a developer building a shopping agent, ACP's narrower scope means fewer decisions to make.

### Community Adoption

The GitHub star numbers tell part of the story: UCP at 3,207 vs ACP at 1,473. But stars aren't adoption. What matters more is that **NVIDIA released a Retail Agentic Commerce Blueprint supporting both protocols**, and the open-source SDK **Agorio** (TypeScript) also supports both UCP and ACP. The multi-protocol tooling trend is the real signal here — developers don't want to pick one.

### Integration Ecosystem

UCP integrates with A2A (Agent-to-Agent Protocol), MCP (Model Context Protocol), and AP2 (Agent Payments Protocol). If you're building a multi-agent system that needs to handle the full commerce lifecycle — discovery, negotiation, payment, fulfillment — UCP's integration surface is more complete. I covered the A2A and MCP relationship in detail in my [MCP vs A2A Protocol 2026](/posts/mcp-vs-a2a-protocol-2026/) post.

ACP integrates with MCP and supports payment handlers, but doesn't have the same breadth of protocol interoperability. That may change as the spec matures.

### Industry Coverage

UCP is actively expanding into lodging and food in 2026. ACP is currently retail-focused. If you're in hospitality or food service, UCP is the only option today.

## The Broader Protocol Ecosystem

UCP and ACP aren't the only players. The agent commerce protocol landscape is fragmenting, and the trust/security layer may end up being the real battleground.

**Visa's Trusted Agent Protocol** (186 GitHub stars) focuses on agent-merchant trust — how does a merchant verify that an agent is authorized to spend money on behalf of a specific user? **Forter's Trusted Agentic Commerce Protocol** (178 stars) tackles the same problem from a fraud-prevention angle. Both are early-stage but address a real gap: neither UCP nor ACP fully solves the "how do I know this agent isn't a scammer" problem.

**NVIDIA's Retail Agentic Commerce Blueprint** supports both UCP and ACP, which is the pragmatic middle ground. NVIDIA isn't picking a side — they're building the infrastructure layer that works with both.

**Rankly Protocol Tracker** monitors 3 commerce protocols (UCP, ACP, NVIDIA RAC) and 7 payment protocols in real-time. The fact that someone built a tracker for this space tells you everything about the fragmentation problem.

## Which Protocol Should Merchants Choose?

I've been asking myself this question, and the honest answer is: **it depends on your AI ecosystem**.

If you're building on Google's AI stack (Gemini, Google ADK, A2A) and want the broadest industry compatibility, UCP is the safer bet. The composable architecture gives you more control over the checkout experience, and the partner list means your payment processor and retail platform are likely already involved. I covered how Google ADK works with A2A in my [Google ADK A2A Protocol Guide](/posts/google-adk-a2a-protocol-guide-2026/).

If you're building on OpenAI (ChatGPT, GPTs, Assistants API) and already use Stripe for payments, ACP is the natural choice. The tighter spec means less implementation surface, and the OpenAI ecosystem integration is deeper.

If you're building a platform or SDK that other developers will use, **support both**. Agorio and NVIDIA are showing the way — multi-protocol support is the pragmatic answer for anyone who doesn't want to bet the business on a single standard.

## The Future — Convergence or Fragmentation?

The agent commerce protocol space in 2026 reminds me of the early days of cloud APIs — multiple competing standards, each backed by a major player, with no clear winner yet. The difference is that UCP and ACP are both open-source and both designed to work with existing infrastructure. Neither requires merchants to rebuild their checkout.

My prediction: we'll see **de facto convergence at the tooling layer** rather than a single protocol winning. SDKs like Agorio will abstract away the protocol choice, NVIDIA's blueprint will support both, and merchants will implement whichever protocol their AI platform prefers while the tooling handles the translation. The real differentiation will shift to the trust and security layer — Visa's and Forter's protocols may end up mattering more than the commerce protocol itself.

## Conclusion

UCP and ACP are both serious, well-designed protocols for agent-led commerce. UCP has broader industry backing and a more composable architecture. ACP has tighter scope and deeper integration with the OpenAI/Stripe ecosystem. Neither is going away in 2026, and the smartest move for most merchants and developers is to build for multi-protocol support from day one.

The agent commerce future isn't about picking the right protocol — it's about building systems that can work with all of them.
