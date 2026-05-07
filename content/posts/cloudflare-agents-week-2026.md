---
title: "Cloudflare Agents Week 2026: Dynamic Workers, Sandboxes GA, and Project Think"
date: 2026-05-06T16:07:53+00:00
tags: ["cloudflare", "ai-agents", "dynamic-workers", "project-think", "serverless"]
description: "Cloudflare Agents Week 2026 launched Project Think, Dynamic Workers, Browser Run, and Agent Lee — a complete platform for production AI agents."
draft: false
cover:
  image: "/images/cloudflare-agents-week-2026.png"
  alt: "Cloudflare Agents Week 2026: Dynamic Workers, Sandboxes GA, and Project Think"
  relative: false
schema: "schema-cloudflare-agents-week-2026"
---

Cloudflare Agents Week (April 15–19, 2026) shipped five major capabilities in a single week: Project Think, Dynamic Workers, Browser Run, Agent Lee, and an Email Service for agents — transforming Cloudflare from a CDN and edge network into a batteries-included platform for building, deploying, and operating production AI agents at global scale.

## Cloudflare의 CDN에서 AI 에이전트 플랫폼으로의 진화

Cloudflare's evolution from a content delivery network to an AI agent platform is one of the most deliberate infrastructure pivots in cloud computing. In 2023, Cloudflare Workers were primarily used for edge caching, request routing, and lightweight serverless functions. By 2025, the Workers platform had grown to include durable objects, queues, and an AI inference layer — but the stack still treated AI as an add-on, not a first-class citizen. Agents Week 2026 changed that entirely. The April 2026 announcements represent a coordinated shift: every service launched — from Dynamic Workers to the Registrar API beta — was designed explicitly for the agentic workload pattern: long-running, stateful, capable of spawning sub-processes, and operating across multiple channels simultaneously. Internally, Cloudflare's own AI engineering stack processed 20 million requests routed through AI Gateway during the event week alone, with 241 billion tokens processed through Workers AI and more than 3,683 internal users serving inference. That internal adoption validates the platform at enterprise scale before external developers push their first agents to production. The architectural bet is clear: agents need durable execution, sandboxed code generation, browser control, email handling, and domain registration — and Cloudflare wants to supply all of it natively, without third-party integrations.

## 2026년 주요 발표: Project Think, Dynamic Workers, Browser Run, Agent Lee

Cloudflare Agents Week 2026 delivered five interconnected platform upgrades across April 15–19, each targeting a different gap in the AI agent developer experience. Project Think introduced a new Agents SDK architecture built around durable primitives — Fibers, Facets, and Sessions — replacing the previous lightweight abstraction layer with a full execution framework. Dynamic Workers gave agents the ability to generate, bundle, and execute TypeScript code inside isolated sandboxes with no ambient authority, operating approximately 100x faster and up to 100x more memory-efficiently than traditional containers. Browser Run (formerly Browser Rendering) rebranded with a complete feature expansion: Live View, Human in the Loop, CDP access, session recordings, and 4x higher concurrency limits. Agent Lee launched as an in-dashboard conversational interface powered by sandboxed TypeScript, capable of troubleshooting configurations and managing resources through a single prompt. The Email Service entered public beta, enabling agents to send, receive, and process email natively without external SMTP providers. A Registrar API beta let agents search, check availability, and register domains directly from editors or terminals. An AI Search primitive added dynamic retrieval instances with hybrid search and relevance boosting. Together, these releases mark Cloudflare's formal declaration that its edge network is now the preferred runtime for production-grade agentic AI systems.

## Project Think: 장기 실행 AI 에이전트를 위한 내구성 있는 실행

Project Think is Cloudflare's next-generation Agents SDK architecture, designed to replace stateless function calls with durable execution contexts that persist across network interruptions, model timeouts, and multi-step reasoning chains. Unlike traditional serverless patterns where each invocation is isolated, Project Think agents maintain state through Fibers — persistent execution contexts that survive failures and resume exactly where they left off. The SDK introduces three core primitives: Fibers for durable execution, Facets for modular sub-agents implemented as Durable Objects, and Sessions for tree-structured conversation management with branching support. Facet-to-Facet RPC latency is comparable to function calls rather than HTTP round-trips, which makes modular agent architectures practical at scale. As of April 2026, Project Think is in preview; APIs may change as developer feedback is incorporated. The shift from "SDK primitives" to "batteries-included platform" reflects Cloudflare's observation that agents in production require more than routing — they need execution guarantees, sub-agent coordination, and conversation persistence across sessions that span hours or days.

### Fibers: 지속적인 실행 컨텍스트

Fibers are Project Think's fundamental building block for durable execution. A Fiber is a persistent execution context that survives worker restarts, model API timeouts, and transient network failures. When a Fiber suspends — waiting for an LLM response, a tool result, or a human confirmation — it serializes its local state to Cloudflare's distributed storage and resumes transparently when the blocking operation completes. This eliminates the retry-and-replay boilerplate that makes complex multi-step agents brittle. Fibers run inside Durable Objects, giving them access to co-located SQLite storage without network hops. The practical implication: an agent orchestrating a 20-step research workflow can pause for 30 minutes waiting for an async tool call, and resume in under a second with full context intact — without any explicit checkpointing code in the application layer.

```typescript
import { createFiber } from '@cloudflare/agents-think';

export default {
  async fetch(request: Request, env: Env) {
    const fiber = await createFiber(env.FIBERS, 'research-task');
    await fiber.run(async (ctx) => {
      const research = await ctx.llm.generate('Research quantum computing trends');
      await ctx.sleep(60_000); // pause 1 minute without timing out
      const summary = await ctx.llm.generate(`Summarize: ${research}`);
      await ctx.storage.put('result', summary);
    });
  }
}
```

### Facets: 모듈형 서브 에이전트로서의 Durable Objects

Facets are sub-agents implemented as Durable Objects, addressable by stable identifiers and capable of running in parallel across Cloudflare's global network. A parent Fiber spawns Facets to delegate specialized tasks — one Facet scrapes data, another validates schema, a third writes to a database — with each Facet maintaining its own isolated state. The critical performance property is that Facet-to-Facet communication uses RPC rather than HTTP, delivering latency comparable to in-process function calls. In practice, a complex research agent that spawns 10 parallel Facets to process 10 documents simultaneously pays almost no coordination overhead. Facets can be scoped to individual conversations, shared across sessions, or made globally addressable — giving architects fine-grained control over state isolation without sacrificing performance.

### Sessions: 트리 구조 대화와 분기

Sessions in Project Think replace flat conversation histories with tree-structured branching. Each Session node represents a conversation turn, and branches can be created programmatically — letting agents explore multiple reasoning paths in parallel, then merge results or select the highest-confidence branch. This is particularly valuable for agent architectures that use speculative execution: running multiple tool-use strategies simultaneously and committing to whichever succeeds first. Sessions persist across browser reloads and network interruptions, enabling multi-day agent workflows that involve human-in-the-loop interruptions, approvals, or redirections without losing context.

## Dynamic Workers: AI가 생성한 코드를 위한 샌드박스 실행

Dynamic Workers are Cloudflare's answer to one of the hardest problems in agentic AI: how do you let an LLM generate and execute code safely at production scale? A Dynamic Worker is a sandboxed Cloudflare Worker spun up on demand to execute AI-generated TypeScript, with strict resource limits, explicit capability grants, and no ambient authority. The key security principle is that every Dynamic Worker starts with `globalOutbound: null` — no network access, no file system access, no credentials. Capabilities are added one at a time through explicit bindings, so a Dynamic Worker that needs to query a database gets exactly that binding and nothing else. Performance is the headline number: approximately 100x faster than traditional container cold starts and up to 100x more memory-efficient. The `worker-bundler` fetches npm packages from the registry and bundles them with esbuild at runtime, so Dynamic Workers can import arbitrary npm dependencies without pre-provisioning. This combination — security-by-default, explicit capability grants, and instant cold starts — makes Dynamic Workers the practical foundation for agents that generate and execute code as part of their reasoning loop.

### 실행 계층: Tier 0, Tier 1, Tier 2

The Execution Ladder defines three tiers of Dynamic Worker isolation, each balancing security against capability. Tier 0 runs in-process with the parent Worker, sharing its isolate and accessing SQLite storage directly — zero cold start, highest trust, suitable for data transformation and lightweight computation. Tier 1 runs in a separate isolate with no network access and no npm imports, providing strong isolation for untrusted code that only operates on data already in memory. Tier 2 runs in a fully isolated Worker with network access and npm package support via `worker-bundler`, making it suitable for agents that need to fetch external data, call third-party APIs, or import complex libraries at runtime.

| Tier | 격리 수준 | 네트워크 | 스토리지 | 사용 사례 |
|------|-----------|---------|---------|----------|
| Tier 0 | 인프로세스 | 없음 | SQLite | 데이터 처리, 경량 계산 |
| Tier 1 | 별도 isolate | 없음 | 없음 | 비신뢰 코드, 샌드박스 로직 |
| Tier 2 | 별도 isolate | 있음 (바인딩) | 있음 (바인딩) | API 호출, DB 접근 |

Selecting the right tier is a security architecture decision: use Tier 0 for trusted internal logic, Tier 1 for LLM-generated code that only processes local data, and Tier 2 for agent-generated scripts that need external connectivity.

### 보안 모델: 앰비언트 권한 없음, 명시적 바인딩

The Dynamic Workers security model inverts traditional cloud permission models. Where AWS Lambda or Google Cloud Functions start with broad IAM roles that developers then restrict, Dynamic Workers start with zero permissions and require explicit grants for every resource they touch. A binding to a KV namespace gives read/write access to exactly that namespace. A binding to a specific D1 database gives SQL access to exactly that database. `globalOutbound: null` means no DNS resolution, no outbound HTTP, no phone-home behavior — unless a binding explicitly enables it. This design makes capability auditing straightforward: the binding list is the complete capability set. For security teams reviewing AI-generated code execution in production, this explicitness is the difference between a defensible architecture and an unauditable one. The `worker-bundler` component fetches npm packages at runtime using esbuild, which means the code bundle is sealed at execution time rather than pre-installed — a significant improvement for supply chain security.

### 성능: 100배 빠르고 100배 메모리 효율

Dynamic Workers achieve their performance advantage by building on the V8 isolate model rather than containerization. Traditional containers — Docker, AWS Fargate, GCP Cloud Run — require a full Linux process, kernel namespace creation, and filesystem mounting for each execution context. Isolate-based Workers skip all of that: a new Dynamic Worker starts as a V8 context within an already-running process, sharing the underlying V8 heap allocator while maintaining strict memory isolation. The result is cold starts measured in milliseconds rather than seconds, and memory overhead measured in kilobytes rather than megabytes. At the scale of an agent that spawns hundreds of code execution contexts per second, this efficiency gap translates directly to cost reduction and latency improvement. Cloudflare's benchmarks report approximately 100x faster starts and up to 100x lower memory overhead compared to Docker-based sandbox approaches.

## Browser Run: 에이전트에게 브라우저 제공

Browser Run is the rebranded and expanded version of Cloudflare's Browser Rendering service, rebuilt specifically for the AI agent use case. The previous Browser Rendering product was designed for screenshot generation and PDF rendering — static operations. Browser Run adds four capabilities that make it suitable for autonomous agent workflows: Live View lets developers watch agents interact with websites in real-time, Human in the Loop pauses execution at defined checkpoints for human verification or input, full Chrome DevTools Protocol (CDP) access enables advanced browser automation that goes beyond Puppeteer's public API, and session recordings capture complete agent interactions for replay and debugging. The concurrency improvement is significant: Browser Run supports 4x higher concurrent session limits than the previous service, which makes it practical to run large-scale web research agents or scraping pipelines without hitting rate limits. Cloudflare manages the browser fleet — no Kubernetes cluster of headless Chrome instances to operate. For developers who previously used Playwright or Puppeteer on self-managed infrastructure, Browser Run removes the entire infrastructure layer while adding observability features that previously required custom tooling.

### 라이브 뷰와 Human in the Loop

Live View provides a real-time streaming viewport into what a Browser Run agent is doing, rendered directly in the Cloudflare dashboard or embeddable in custom UIs. This is not a screen recording played back later — it is a live stream of the agent's browser activity, enabling developers to monitor and intervene during execution. Human in the Loop builds on this capability by letting agents signal that they need human input before proceeding: "I found a CAPTCHA," "This login page uses 2FA," "Please confirm before submitting this form." The agent pauses, the developer or end-user completes the action in the Live View window, and execution resumes. For enterprise automation that touches authenticated systems, Human in the Loop makes Browser Run compliant with audit requirements that prohibit fully unattended access to certain systems.

```typescript
const browser = await env.BROWSER.launch();
const page = await browser.newPage();
await page.goto('https://example.com/checkout');

// Pause for human verification before payment
const approval = await env.HITL.requestApproval({
  message: 'Confirm purchase: $299 for Pro plan',
  timeout: 300_000,
});

if (approval.approved) {
  await page.click('#confirm-purchase');
}
```

### 세션 녹화와 CDP 접근

Session recordings capture the complete browser interaction history — every network request, DOM mutation, JavaScript evaluation, and screenshot — in a structured format that can be replayed, diffed, or fed back into the agent for debugging. When an agent fails midway through a 40-step checkout automation, the session recording identifies exactly which step triggered the failure and what the DOM looked like at that moment. Chrome DevTools Protocol access gives advanced users direct control over browser internals: intercepting network requests, injecting JavaScript into page contexts, manipulating service workers, and accessing storage APIs that Puppeteer's abstraction layer doesn't expose. This is particularly useful for agents that need to test authenticated API endpoints through a browser context or extract data from single-page applications that require JavaScript execution before content is visible.

### 4배 향상된 동시성 한도

Browser Run's 4x concurrency improvement addresses one of the key bottlenecks in production agent deployments. The previous Browser Rendering service had tight limits that made parallel web research agents impractical — if you needed to process 20 URLs simultaneously, you'd queue most of them. With the new limits, agentic pipelines that parallelize web scraping, screenshot generation, or form automation across dozens of concurrent sessions are now feasible without custom infrastructure. Cloudflare's managed fleet also handles browser updates, security patches, and crash recovery automatically.

## Agent Lee: Cloudflare 스택의 대화형 인터페이스

Agent Lee is Cloudflare's in-dashboard AI agent, designed to replace manual tab-switching and documentation-hunting with a single conversational interface to the entire Cloudflare stack. Built on sandboxed TypeScript and powered by Dynamic Workers, Agent Lee can inspect Worker configurations, analyze KV and D1 storage patterns, diagnose DNS issues, suggest cache rule optimizations, and execute management operations — all from a unified chat interface. The interface runs directly inside the Cloudflare dashboard and is accessible via the dashboard search bar or a persistent chat panel. Unlike generic AI assistants that provide generic advice, Agent Lee is grounded in the actual state of your account: it reads your real configurations, queries your real metrics, and generates recommendations specific to your deployment. The practical workflow shift is significant: instead of opening five tabs, reading three docs pages, and running two CLI commands, a developer asks "Why is my Workers function timing out?" and gets a specific, actionable diagnosis within seconds. Agent Lee is implemented using the same Dynamic Workers runtime it exposes to developers — Cloudflare's team built Agent Lee on the platform they're asking developers to use, which is a meaningful validation of the architecture.

### 샌드박스 TypeScript를 이용한 대시보드 관리

Agent Lee executes management actions through sandboxed TypeScript running in a Dynamic Worker, giving it the ability to take real actions — not just suggest them. When Agent Lee identifies a misconfigured cache rule, it can generate the corrected rule, show the TypeScript snippet it intends to execute, and apply it after user confirmation. The sandboxed execution model ensures that Agent Lee's generated code runs with only the permissions needed for the specific operation, with no access to unrelated parts of the account. This is architecturally distinct from dashboard automations that require pre-configured API tokens: Agent Lee composes new TypeScript at interaction time, scoped to the exact resources referenced in the conversation.

### 문제 해결과 구성 분석

Agent Lee's diagnostic capabilities are built on Cloudflare's observability data: access logs, edge trace data, DNS query histories, and Workers invocation metrics. When a developer asks "Why is my website slow?", Agent Lee queries recent performance metrics, identifies whether the bottleneck is at the DNS layer, the CDN cache, or inside the Worker function itself, and produces a prioritized list of changes. Concrete example from Cloudflare's own documentation: Agent Lee analyzes configuration, identifies that cache hit rate dropped from 87% to 12% after a code deploy, pinpoints the specific Workers route setting `Cache-Control: no-store`, and provides the corrected code. That grounded, specific response is what makes Agent Lee useful in production incidents.

## 멀티채널 확장: 이메일 서비스와 Registrar API

Cloudflare's multi-channel expansion during Agents Week 2026 extended the platform beyond HTTP request handling into email and domain management — two channels that autonomous agents frequently need but have historically required external integrations to access. The Email Service entered public beta with a native API for sending, receiving, and processing email directly through the Workers runtime, without configuring external SMTP providers or managing email infrastructure. The Registrar API beta enabled agents to search domain availability, check pricing, and register domains at cost directly from Workers code or terminal commands — completing the loop for agents that need to provision new web properties as part of their workflows. Together, these additions mean an agent can now handle the full lifecycle of a new web project from a single Cloudflare-native stack: register the domain, deploy the Worker, configure DNS, send confirmation emails, and manage ongoing operations through Agent Lee — without leaving the platform. Cloudflare confirmed the Email Service is now processing real-world traffic in beta, with the Registrar API following a similar beta timeline.

### 에이전트를 위한 이메일 서비스 베타

The Cloudflare Email Service for agents provides a first-class API for transactional email from within Workers: send HTML or plain-text emails, attach files, receive inbound messages at custom addresses, and trigger Workers functions on incoming mail. The service handles the deliverability infrastructure — SPF, DKIM, DMARC configuration, bounce handling, reputation management — so developers write business logic rather than email plumbing. For agentic workflows, email is often the preferred notification channel for long-running operations: an agent that takes 4 hours to complete a research task can email its results rather than maintaining a persistent WebSocket connection. The public beta pricing model is usage-based, making it cost-effective for low-volume agentic use cases while remaining practical for high-volume transactional workflows.

### Registrar API: 터미널/에디터에서 도메인 등록

The Registrar API beta lets Workers code search domain availability across TLDs, check real-time pricing, and register domains at Cloudflare's at-cost pricing — the same pricing available in the dashboard, now accessible programmatically. For developers building SaaS platforms that provision custom domains for customers, this eliminates the dependency on third-party registrar APIs with markup pricing and rate limits. An agent can now run: check availability → register domain → create DNS records → deploy Worker → configure SSL — entirely through Cloudflare's own APIs without leaving the ecosystem. The API is available from the Workers runtime and from the Cloudflare CLI, making it accessible in both serverless agent code and local automation scripts.

## 첫 번째 에이전트 구축: 실전 가이드

Building a production agent on the full Cloudflare stack in 2026 starts with Project Think's Fiber and Facet primitives, then layers in Dynamic Workers for code execution, Browser Run for web interaction, and the Email Service for notifications. The architecture pattern that works best for research and data-gathering agents is a root Fiber that orchestrates a pool of Facets, with each Facet assigned to a specific subtask. A complete research agent using all Agents Week components looks like this:

```typescript
import { createFiber } from '@cloudflare/agents-think';

interface Env {
  FIBERS: DurableObjectNamespace;
  BROWSER: BrowserWorker;
  AI: Ai;
  KV: KVNamespace;
  EMAIL: EmailService;
  DYNAMIC_WORKERS: DynamicWorkerBinding;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { topic, userEmail } = await request.json<{ topic: string; userEmail: string }>();
    const fiber = await createFiber(env.FIBERS, `research-${Date.now()}`);

    const result = await fiber.run(async (ctx) => {
      // Step 1: Gather sources via Browser Run
      const browser = await env.BROWSER.launch();
      const page = await browser.newPage();
      await page.goto(`https://search.example.com?q=${encodeURIComponent(topic)}`);
      const urls = await page.$$eval('.result-link', els => els.map(e => e.href));
      await browser.close();

      // Step 2: Parallel Facets for summarization
      const summaries = await Promise.all(
        urls.slice(0, 5).map(url => ctx.facet('summarizer').summarize(url))
      );

      // Step 3: Dynamic Worker (Tier 1) for safe data transformation
      const processed = await env.DYNAMIC_WORKERS.execute({
        code: generateCleanupCode(summaries),
        tier: 1,
        timeout: 5000,
      });

      // Step 4: AI synthesis
      const synthesis = await env.AI.run('@cf/meta/llama-3-70b', {
        messages: [{ role: 'user', content: `Synthesize: ${JSON.stringify(processed)}` }]
      });

      // Step 5: Email results
      await env.EMAIL.send({
        to: userEmail,
        subject: `Research complete: ${topic}`,
        html: `<h1>${topic}</h1><p>${synthesis.response}</p>`,
      });

      await env.KV.put(`research:${topic}`, JSON.stringify(synthesis));
      return synthesis;
    });

    return Response.json({ result });
  }
};
```

The key architectural decision is tier selection for Dynamic Workers. Data transformation from trusted internal Facets belongs in Tier 0. LLM-generated code that shouldn't have network access belongs in Tier 1. Code that needs to call external APIs or import npm packages belongs in Tier 2 with explicit bindings.

## 프로덕션 고려사항: 비용, 보안, 확장성

Production deployment of Cloudflare agent workloads involves cost, security, and scaling considerations that differ meaningfully from traditional serverless. On cost: Dynamic Workers pricing is based on CPU time rather than wall-clock duration, which is advantageous for agents that spend most of their time waiting for LLM responses — billing stops during the wait. Durable Objects (which underpin Fibers and Facets) are billed by storage, requests, and compute duration, with the storage cost often dominating for long-running agents that maintain significant state. Browser Run sessions are billed per session-hour, which can accumulate quickly for agents running long browsing sessions; design agents to close sessions promptly and reuse sessions where possible. On security: the no-ambient-authority model of Dynamic Workers is only as strong as the binding configuration. Audit bindings regularly, use the principle of least privilege for every binding grant, and log all Dynamic Worker invocations with their binding configurations. For Agent Lee, review the TypeScript snippets it proposes before approving execution — the sandbox protects the rest of your account, but a misconfigured management operation can still affect the resources it's been granted access to. On scaling: Cloudflare's global network handles distribution automatically across 300+ data centers. The scaling consideration for agents is Durable Object location: co-locate Durable Objects with the users they serve using jurisdiction constraints, and avoid cross-continental Facet-to-Facet calls where latency matters.

## FAQ

**Q: Project Think과 기존 Cloudflare Agents SDK의 차이점은 무엇인가요?**

Project Think는 기존 Agents SDK의 다음 세대로, 경량 프리미티브 레이어에서 완전한 실행 프레임워크로 업그레이드됩니다. Fibers(내구성 있는 실행), Facets(모듈형 서브에이전트), Sessions(트리 구조 대화)를 도입해 이전 SDK에서는 별도로 구현해야 했던 상태 지속성, 서브에이전트 조율, 분기 대화를 플랫폼 수준에서 제공합니다. 2026년 4월 기준 프리뷰 상태이며 API는 변경될 수 있습니다.

**Q: Dynamic Workers는 기존 컨테이너 기반 코드 실행과 어떻게 다른가요?**

Dynamic Workers는 Docker나 Cloud Run 같은 컨테이너 런타임 대신 V8 isolate 위에서 실행됩니다. 콜드 스타트가 초 단위가 아닌 밀리초 단위이고, 메모리 오버헤드가 메가바이트가 아닌 킬로바이트 수준입니다. 보안 모델도 반전됩니다: 기본적으로 모든 권한이 거부되고(`globalOutbound: null`), 바인딩을 통해 명시적으로 권한을 부여하는 방식으로 IAM 역할 기반 모델보다 감사하기 쉽습니다.

**Q: Browser Run의 Human in the Loop 기능은 어떻게 작동하나요?**

에이전트가 인간 입력이 필요한 지점(CAPTCHA, 2FA, 민감한 폼 제출 확인 등)에 도달하면 실행을 일시 중지하고 개발자나 최종 사용자에게 알림을 보냅니다. 사용자는 Live View 창에서 해당 작업을 직접 완료한 뒤 에이전트 실행을 재개합니다. 완전 무인 접근이 불허되는 엔터프라이즈 규정 준수 시나리오에서 필수적인 기능입니다.

**Q: Agent Lee는 실제 Cloudflare 리소스를 수정할 수 있나요?**

네, Agent Lee는 사용자 확인 후 Dynamic Workers를 통해 실제 관리 작업을 실행할 수 있습니다. 모든 실행은 샌드박스 환경에서 이루어지며, Agent Lee가 제안하는 TypeScript 코드를 사용자가 먼저 검토합니다. 샌드박스 모델이 다른 리소스에 대한 무단 접근을 방지하지만, 승인된 작업은 실제로 적용됩니다.

**Q: Cloudflare Email Service 베타는 외부 SMTP 설정 없이 사용 가능한가요?**

네, Email Service는 Cloudflare 네이티브 API로 제공되며 SendGrid, Mailgun 등 외부 SMTP 프로바이더 설정이 필요 없습니다. 발송 인프라(SPF, DKIM, DMARC 설정, 반송 처리, 평판 관리)는 Cloudflare가 관리하며, Workers 코드에서 비즈니스 로직만 작성하면 됩니다. 퍼블릭 베타는 사용량 기반 요금제를 따릅니다.
