---
title: "Cloudflare Agents Week 2026: Dynamic Workers, Sandboxes GA, and Project Think"
date: 2026-05-08T00:00:00+00:00
tags: ["cloudflare", "ai-agents", "workers", "dynamic-workers", "agents-week"]
description: "Cloudflare Agents Week 2026 shipped Dynamic Workers GA, Project Think, and Browser Rendering updates — a complete platform for production AI agents."
draft: false
cover: "/images/cloudflare-agents-week-2026.png"
schema: "schema-cloudflare-agents-week-2026"
---

Cloudflare Agents Week 2026 shipped five major platform capabilities in a single week: Project Think, Dynamic Workers GA, Browser Rendering API updates, an Agent Leaderboard, and significant Workers AI expansion — transforming Cloudflare from a CDN and edge network into a batteries-included platform for building, deploying, and operating production AI agents at global scale. The numbers behind the event are significant: 20 million requests routed through AI Gateway during the week, 241 billion tokens processed via Workers AI, and more than 3,683 internal users validating the platform at enterprise scale before external developers push their first agents to production.

## Cloudflare Agents Week 2026: The Platform Announcements

Cloudflare Agents Week 2026 represents the most coordinated set of platform announcements in the company's history, with every release targeting a distinct gap in the AI agent developer experience. Across April 2026, Cloudflare shipped Dynamic Workers GA for sandboxed code execution, Project Think as a framework for long-running durable agents, Browser Rendering API updates for headless browser automation, an Agent Leaderboard for community showcasing, and a major Workers AI expansion covering more models, lower latency, and expanded regional availability. The 20 million AI Gateway requests and 241 billion tokens processed through Workers AI during the week confirm that the platform absorbs real production load — these are not preview-only services. The architectural logic connecting all five releases is the same: agents in production need more than a serverless function invocation. They need durable execution that survives failures, sandboxed code generation that protects the host environment, browser control for web-native automation, and expanded model options for diverse reasoning tasks. Cloudflare's week of announcements is a deliberate answer to that full stack requirement, delivered on the same global edge network that already handles a significant portion of the world's HTTP traffic.

## Dynamic Workers GA: What AI-Safe Code Sandboxing Means in Practice

Dynamic Workers reached general availability during Agents Week 2026, marking the end of an extended preview period and the beginning of production-ready support for sandboxed AI-generated code execution. The headline performance metric is approximately 100x faster startup and up to 100x greater memory efficiency compared to container-based alternatives. Dynamic Workers achieve this by building on V8 isolates rather than full Linux container runtimes. Where Docker or AWS Fargate require kernel namespace creation, filesystem mounting, and a full process startup for each execution context, a Dynamic Worker starts as a new V8 context inside an already-running process, sharing the V8 heap allocator while maintaining strict memory isolation between isolates. The security model inverts the default: every Dynamic Worker starts with `globalOutbound: null`, meaning no network access, no filesystem access, and no credentials. Every capability — a KV namespace, a D1 database, an outbound HTTP binding — must be explicitly granted through a binding declaration. This design makes capability auditing straightforward: the binding list is the complete and exhaustive capability set of the Dynamic Worker. For teams that need to execute LLM-generated code in production, that explicitness is the difference between a defensible architecture and an unauditable one.

The Execution Ladder defines three isolation tiers. Tier 0 runs in-process with the parent Worker, sharing its isolate, with direct SQLite access and zero cold start — suitable for trusted data transformation. Tier 1 runs in a separate isolate with no network access and no npm imports, providing strong isolation for LLM-generated code that only operates on in-memory data. Tier 2 runs in a fully isolated Worker with explicit network and storage bindings, and supports npm package imports via the `worker-bundler` component, which fetches packages from the registry and bundles them with esbuild at runtime. Selecting the right tier is a security architecture decision: use the lowest tier that satisfies the workload's capability requirements. The `worker-bundler` approach is also a supply chain security improvement over pre-installed package environments — the code bundle is sealed at execution time rather than sourced from a pre-baked image that may drift from the installed dependencies.

```typescript
// Dynamic Worker execution example — Tier 1 for LLM-generated code
const result = await env.DYNAMIC_WORKERS.execute({
  code: llmGeneratedCode,
  tier: 1,           // no network, no npm — strong isolation
  timeout: 5_000,    // 5 second wall-clock limit
  bindings: {},      // explicit: nothing granted
});

// Tier 2 for code that needs npm and outbound HTTP
const resultWithDeps = await env.DYNAMIC_WORKERS.execute({
  code: agentScript,
  tier: 2,
  timeout: 30_000,
  bindings: {
    DB: env.D1_DATABASE,   // explicit database grant
  },
  packages: ['zod', 'date-fns'],  // worker-bundler fetches at runtime
});
```

The GA milestone matters for production teams. Preview services carry API stability caveats that prevent adoption in customer-facing systems. GA Dynamic Workers can now be used in SLAs, compliance reviews, and production incident runbooks. Cloudflare's own Agent Lee — the in-dashboard conversational agent — runs on Dynamic Workers, providing a real production reference implementation that validates the runtime under actual load.

## Project Think: The Framework for Long-Running Durable AI Agents

Project Think is Cloudflare's next-generation Agents SDK framework, designed to replace stateless function invocations with durable execution contexts that persist across network interruptions, model timeouts, and multi-step reasoning chains. The core observation driving Project Think is that production AI agents fail not because the AI models are insufficient, but because the execution infrastructure has no durability guarantees. A 20-step research workflow that hits a model API timeout on step 14 has historically meant restarting from zero. Project Think eliminates that failure mode with three primitives: Fibers for durable execution, Facets for modular sub-agents, and Sessions for tree-structured conversation management. As of Agents Week 2026, Project Think is in preview with APIs subject to change as developer feedback is incorporated. The framework runs on Durable Objects, giving every Fiber access to co-located SQLite storage without cross-datacenter round-trips. Facet-to-Facet RPC latency is comparable to in-process function calls rather than HTTP hops, which makes deeply modular agent architectures practical at scale without accumulating network latency at every coordination point.

Fibers are persistent execution contexts that serialize their local state to Cloudflare's distributed storage whenever they suspend — waiting for an LLM response, a tool result, or a human confirmation. When the blocking operation completes, the Fiber resumes with full context intact, in under a second, with no explicit checkpointing code required in the application layer. An agent orchestrating a 20-step research workflow can pause for 30 minutes waiting for an async tool call and resume transparently. Facets are sub-agents implemented as Durable Objects, addressable by stable identifiers, spawnable in parallel across Cloudflare's global network, and capable of maintaining isolated state. A parent Fiber delegates to Facets for parallelism: one Facet scrapes, another validates schema, a third writes results — with minimal coordination overhead because RPC replaces HTTP. Sessions replace flat conversation histories with tree-structured branching, enabling agents to explore multiple reasoning paths simultaneously and merge results or select the highest-confidence branch.

```typescript
import { createFiber } from '@cloudflare/agents-think';

export default {
  async fetch(request: Request, env: Env) {
    const fiber = await createFiber(env.FIBERS, 'research-task');
    await fiber.run(async (ctx) => {
      const research = await ctx.llm.generate('Research AI infrastructure trends');
      await ctx.sleep(60_000); // pause without timing out the Worker
      const summary = await ctx.llm.generate(`Synthesize: ${research}`);
      await ctx.storage.put('result', summary);
    });
  }
}
```

The shift from "SDK primitives" to "batteries-included execution framework" reflects Cloudflare's observation that the hard part of building production agents is not the LLM call — it is everything around it: state persistence, failure recovery, sub-agent coordination, and conversation history management across sessions that span hours or days.

## Browser Rendering API: Headless Browser Automation for Agents

The Browser Rendering API received a significant update during Agents Week 2026, expanding from a screenshot-and-PDF service into a full headless browser automation layer designed for autonomous agent workflows. The most significant capability additions are Live View, which streams real-time browser activity directly to the Cloudflare dashboard or embeddable UIs; Human in the Loop, which pauses execution at defined checkpoints for human verification or input before the agent proceeds; full Chrome DevTools Protocol access for advanced automation beyond Puppeteer's public API surface; and session recordings that capture complete interaction histories for debugging and replay. The concurrency improvement is a concrete production enabler: Browser Rendering now supports 4x higher concurrent session limits than its previous version, making large-scale parallel web research agents and scraping pipelines practical without queuing on tight limits. Cloudflare manages the entire browser fleet — security patches, browser version updates, crash recovery — so development teams operating agents on Browser Rendering pay no infrastructure cost for running headless Chrome at scale. For developers who previously ran Playwright or Puppeteer on self-managed Kubernetes clusters of Chrome instances, the Browser Rendering API replaces that entire infrastructure layer while adding observability features — session recordings, live streaming, human-in-the-loop interrupts — that previously required significant custom tooling investment.

Human in the Loop is particularly relevant for enterprise agent deployments that touch authenticated systems. When an agent encounters a CAPTCHA, a two-factor authentication prompt, or a form requiring explicit human authorization before submission, execution pauses and the user receives a notification. The user completes the action directly in the Live View streaming window, and the agent resumes. This makes Browser Rendering compliant with enterprise audit requirements that prohibit fully unattended access to sensitive systems. Session recordings capture every network request, DOM mutation, JavaScript evaluation, and screenshot in a structured format that can be replayed or diffed — when an agent fails on step 37 of a 40-step checkout automation, the recording identifies the exact failure point and DOM state without requiring a re-run.

```typescript
const browser = await env.BROWSER.launch();
const page = await browser.newPage();
await page.goto('https://example.com/checkout');

// Pause for human confirmation before a sensitive action
const approval = await env.HITL.requestApproval({
  message: 'Confirm purchase: $299 for Pro subscription',
  timeout: 300_000,
});

if (approval.approved) {
  await page.click('#confirm-purchase');
}
await browser.close();
```

## Workers AI: Model Expansion and Performance Improvements

Workers AI expanded significantly during Agents Week 2026, adding new model options, reducing inference latency, and extending regional availability across Cloudflare's 300-plus data center network. The expansion covers both open-weight models available through the Workers AI inference layer and the models powering AI Gateway routing for third-party providers. The driving goal is to give agent developers access to the right model for each layer of their architecture — a fast, low-latency model for classification and routing decisions, a mid-tier model for summarization and extraction, and a high-capability model for complex reasoning — all within a single platform without requiring separate inference infrastructure for each tier. Lower latency at the edge matters for agent architectures that chain multiple LLM calls sequentially: every millisecond of inference latency compounds across the call graph. Expanded regional availability reduces the geographic distance between the agent's Durable Object state and its inference provider, which is particularly relevant for latency-sensitive user-facing agents. Workers AI's unified billing and quota model also simplifies cost management for teams running multiple agent types: one bill, one quota pool, consistent monitoring across all model usage.

The AI Gateway component processed 20 million requests during Agents Week alone, demonstrating that the routing, caching, and fallback layer is operating at production scale. AI Gateway adds request logging, cost tracking, rate limiting, and provider fallback to any LLM API call routed through it — capabilities that previously required custom middleware or third-party services. For agents that call multiple LLM providers depending on task requirements, AI Gateway provides a single control plane for observability and policy enforcement without per-provider integration work.

## The 241 Billion Token Milestone: Cloudflare's Own AI Infrastructure

The 241 billion tokens processed through Workers AI during Agents Week 2026 is not just a marketing number — it is a validation data point for the platform's production readiness at scale. To put the figure in context: 241 billion tokens at average output token lengths implies billions of individual LLM interactions, processed across Cloudflare's global edge network during a single week. The 3,683-plus internal users leveraging the platform during the same period confirms that Cloudflare's own engineering teams are running real workloads on the infrastructure they are asking external developers to adopt. Internal adoption at this scale is a meaningful signal because internal teams have access to private context about platform reliability, failure modes, and operational characteristics that external developers cannot see before committing to a platform. When Cloudflare's own agents — including Agent Lee, the in-dashboard conversational assistant — run on Dynamic Workers, Durable Objects, and Workers AI, the platform absorbs production traffic patterns, not just benchmark workloads.

The 20 million AI Gateway requests provide a parallel data point for the routing and observability layer. AI Gateway sits between agent code and LLM provider APIs, handling caching, fallback routing, rate limiting, and cost tracking. Twenty million requests through that layer in a week represents a steady production traffic pattern, not a spike from a single large customer. For developers evaluating Cloudflare's agent platform against alternatives, these internal usage figures are the most credible performance evidence available before committing to the platform in production.

## Building on Cloudflare's Agent Platform: Getting Started

Getting started with Cloudflare's agent platform in 2026 means selecting the right combination of primitives for the agent's workload pattern. Stateless, single-step agents that invoke an LLM and return a response can run as standard Workers with a Workers AI binding — no additional primitives required. Multi-step agents that need to survive failures and maintain state across long operations should use Project Think's Fiber primitive, which provides durability with no explicit checkpointing code. Agents that need to parallelize subtasks across multiple specialized components should add Facets, with each Facet implementing a distinct capability as a Durable Object. Agents that generate and execute code as part of their reasoning loop should use Dynamic Workers at the appropriate tier for their security requirements. Agents that interact with web interfaces should use the Browser Rendering API, with Human in the Loop enabled for any workflow that touches authenticated systems or requires human confirmation before consequential actions.

```typescript
import { createFiber } from '@cloudflare/agents-think';

interface Env {
  FIBERS: DurableObjectNamespace;
  BROWSER: BrowserWorker;
  AI: Ai;
  KV: KVNamespace;
  DYNAMIC_WORKERS: DynamicWorkerBinding;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { topic } = await request.json<{ topic: string }>();
    const fiber = await createFiber(env.FIBERS, `research-${Date.now()}`);

    const result = await fiber.run(async (ctx) => {
      // Step 1: Web research via Browser Rendering
      const browser = await env.BROWSER.launch();
      const page = await browser.newPage();
      await page.goto(`https://search.example.com?q=${encodeURIComponent(topic)}`);
      const urls = await page.$$eval('.result-link', els => els.map(e => (e as HTMLAnchorElement).href));
      await browser.close();

      // Step 2: Parallel Facets for summarization
      const summaries = await Promise.all(
        urls.slice(0, 5).map(url => ctx.facet('summarizer').summarize(url))
      );

      // Step 3: Dynamic Worker Tier 1 for safe data transformation
      const processed = await env.DYNAMIC_WORKERS.execute({
        code: `module.exports = (data) => data.filter(s => s.length > 50).join(' ')`,
        tier: 1,
        timeout: 5_000,
        input: summaries,
      });

      // Step 4: AI synthesis
      const synthesis = await env.AI.run('@cf/meta/llama-3-70b', {
        messages: [{ role: 'user', content: `Synthesize these research summaries: ${processed}` }]
      });

      await env.KV.put(`research:${topic}`, JSON.stringify(synthesis));
      return synthesis;
    });

    return Response.json({ result });
  }
};
```

The Workers CLI (`wrangler`) handles local development, deployment, and secret management for all these primitives. The `wrangler dev` command runs a local simulation of Durable Objects, KV, D1, and the Workers AI binding, which makes the full agent stack testable without deploying to Cloudflare's network during development.

## How Cloudflare Compares to AWS and Azure for AI Agent Infrastructure

Cloudflare's agent platform competes directly with AWS Bedrock Agents and Azure AI Agent Service for the production AI agent infrastructure market, and the comparison reveals meaningful architectural differences. AWS Bedrock Agents provides a managed orchestration layer built on Lambda, with agent definitions stored in a proprietary JSON format and execution backed by AWS's regional container infrastructure. Cold starts on Lambda — even with provisioned concurrency — run in the hundreds of milliseconds range for Node.js runtimes. Azure AI Agent Service follows a similar pattern: managed orchestration, regional execution, container-backed isolation. Both services inherit the IAM permission model of their respective clouds, where Lambda functions and Azure Functions start with broad execution roles that teams then restrict through policy. Cloudflare's approach inverts the default at every layer: isolate-based execution with microsecond cold starts, zero-permission-by-default with explicit binding grants, and a global network that places execution near users without regional routing configuration.

The cost model also differs in ways that favor agent workloads specifically. Dynamic Workers bill on CPU time, not wall-clock duration, which means an agent that waits 10 minutes for an LLM response while suspended in a Fiber pays nearly nothing for that wait — the Worker is not consuming CPU. AWS Lambda bills on duration even when the function is blocked on an awaited promise, which can make long-running agent patterns unexpectedly expensive. Durable Objects bill on storage and compute duration, with storage often dominating for stateful agents — a predictable cost structure that is easier to model than container instance pricing. The tradeoff is ecosystem depth: AWS and Azure offer broader managed service integrations, more mature compliance certifications, and longer enterprise track records. Cloudflare's edge is performance, the isolate security model, and a developer experience designed from the ground up for the agentic workload pattern rather than adapted from traditional serverless.

## FAQ

**Q: What is the difference between Project Think and the existing Cloudflare Agents SDK?**

Project Think is the next generation of the Cloudflare Agents SDK, upgrading from a lightweight primitives layer to a full execution framework. It introduces Fibers for durable execution that survives failures and timeouts, Facets for modular sub-agents implemented as Durable Objects with low-latency RPC communication, and Sessions for tree-structured conversation management with branching support. The previous SDK required developers to implement state persistence and sub-agent coordination manually. Project Think provides those capabilities at the platform level. As of April 2026, it is in preview with APIs subject to change based on developer feedback.

**Q: How does Dynamic Workers differ from container-based code execution like AWS Fargate or Docker?**

Dynamic Workers build on V8 isolates rather than Linux container runtimes. Container cold starts involve kernel namespace creation, filesystem mounting, and a full process startup — measured in seconds. Dynamic Worker cold starts spin up a new V8 context inside an already-running process — measured in milliseconds, approximately 100x faster. Memory overhead follows the same ratio: containers carry megabytes of process overhead per instance, while isolates carry kilobytes. The security model is also inverted: Dynamic Workers start with zero permissions and require explicit binding grants for every resource, whereas Lambda and Fargate tasks start with an IAM execution role that developers restrict. The explicit binding model makes capability auditing straightforward for security teams reviewing AI-generated code execution in production.

**Q: What does the Human in the Loop feature in Browser Rendering API actually do?**

When an agent navigating a website reaches a checkpoint that requires human input — a CAPTCHA, a two-factor authentication prompt, a high-stakes form submission — it pauses execution and notifies the designated user or developer. The Live View streaming window shows the current browser state, and the human completes the action directly in that window before the agent resumes. This is not a polling mechanism: the agent suspends cleanly and resumes with full context once the human signals completion. For enterprise deployments that must comply with audit requirements prohibiting fully unattended access to sensitive systems, Human in the Loop makes Browser Rendering usable in those environments without requiring a separate automation governance layer.

**Q: How does Cloudflare's AI Gateway relate to Workers AI, and why does the 20M request figure matter?**

AI Gateway is a routing, caching, and observability layer that sits between agent code and LLM provider APIs — both Cloudflare's own Workers AI models and third-party providers like OpenAI, Anthropic, and Google. It adds request logging, cost tracking, rate limiting, semantic caching, and provider fallback without requiring changes to individual LLM API calls. The 20 million requests routed through AI Gateway during Agents Week represent real production traffic across those capabilities, not benchmark load. For agent developers, this confirms that AI Gateway's routing and fallback logic is validated at meaningful scale — critical for agents that rely on provider fallback when a primary LLM API is degraded.

**Q: What is the Agent Leaderboard and how do developers submit agents to it?**

The Agent Leaderboard is a community showcase of agents built on Cloudflare's platform, launched during Agents Week 2026 to surface real-world implementations across different domains — research agents, automation agents, customer-facing conversational agents, and developer tooling. Developers submit agents through the Cloudflare developer community portal with a description of what the agent does, which platform primitives it uses, and public source code or a demo link. The Leaderboard serves both as inspiration for developers evaluating what is buildable on the platform and as a reference library of working implementations using Project Think, Dynamic Workers, and Browser Rendering in combination.
