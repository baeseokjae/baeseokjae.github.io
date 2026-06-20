---
title: "Pi Agent Core Guide 2026: The Runtime-Agnostic TypeScript Agent Harness Behind Flue and Agno"
date: 2026-06-20T12:00:00+00:00
tags: ["pi agent core", "flue framework", "agno", "runtime-agnostic agent harness", "typescript agent framework", "pi-agent-core", "cloudflare agents"]
description: "Pi Agent Core is a minimal TypeScript agent harness by Mario Zechner (2.8M weekly npm downloads). This guide covers its architecture, the Flue and Agno frameworks built on top, Cloudflare integration, and how it compares to Claude Code SDK and OpenAI Agents SDK."
draft: false
cover:
  image: "/images/pi-agent-core-guide-2026.png"
  alt: "Pi Agent Core Guide 2026: The Runtime-Agnostic TypeScript Agent Harness Behind Flue and Agno"
  relative: false
schema: "schema-pi-agent-core-guide-2026"
---

Pi Agent Core (`pi-agent-core`) is a minimal, runtime-agnostic TypeScript agent harness by Mario Zechner with 2.8 million weekly npm downloads. It provides the foundational agent loop — tool execution, state management, and event streaming — without coupling you to any LLM provider, runtime environment, or framework. Two major ecosystems build on it: Flue (from the Astro team) as a full-stack agent framework, and Agno as a production agent platform SDK. Cloudflare adopted Pi as the harness in their three-layer agent architecture announced June 17, 2026. If you're building agents in TypeScript and want to understand the layer between your LLM API calls and your framework, this is where you start.

---

## What Is Pi Agent Core and Why Does It Exist?

Pi Agent Core is a deliberately minimal agent harness that implements exactly one thing: the perceive-reason-act loop that drives every AI agent. It sits between `pi-ai` (the unified multi-provider LLM API layer) and higher-level frameworks like Flue and Agno. Mario Zechner created it because existing agent SDKs were either tied to a specific LLM provider (Claude Code SDK, OpenAI Agents SDK) or so heavily abstracted that you couldn't inspect or override the core loop without wading through layers of indirection (LangChain). The Pi philosophy is that an agent harness should be small enough to read in one sitting, portable across runtimes, and designed so the agent can extend itself — not require you to learn a new framework abstraction for every feature.

The npm package weighs under 10KB gzipped. The core agent loop fits in roughly 300 lines of TypeScript. The system prompt is the shortest of any major agent harness — Zechner's design principle is that the harness should stay out of the way and let the agent's actual instructions drive behavior.

## How Does Pi Agent Core's Architecture Work?

Pi Agent Core's architecture follows a clean three-layer model that separates concerns without overlapping responsibilities.

### pi-ai: The Unified LLM API Layer

Pi-ai is the transport layer — a unified multi-provider API that normalizes calls to OpenAI, Anthropic, Google Gemini, AWS Bedrock, and local Ollama models under a single interface. You define your provider once, and pi-agent-core calls it without caring which backend is running. This is analogous to how the VSCode Language Server Protocol abstracts editor-specific features, but for LLM providers. Switching from Claude to GPT-4 to Gemini requires changing one line in your config, not rewriting your agent's tool calls.

### pi-agent-core: The Agent Harness

The core harness implements five things:

1. **Stateful agent runtime** — maintains conversation context, tool call history, and session state across turns
2. **Tool execution engine** — parses and dispatches tool calls from LLM responses, returns results back into context
3. **Event streaming** — emits structured events for every step (tool call started, tool call completed, error, state change) so frameworks and UIs can react
4. **Steering and follow-up queues** — manages the "the model wants to do ten things at once" problem by queueing and prioritizing tool calls
5. **Hooks system** — `beforeToolCall` and `afterToolCall` hooks let you intercept every interaction with the runtime

What Pi intentionally leaves out: no MCP support built in, no sub-agent spawning, no plan mode, no built-in sandboxing. You add these in the framework layer or via extensions. The default tool set is exactly four tools: Read, Write, Edit, Bash. That's it. You extend it by writing extensions — TypeScript functions that wrap new capabilities.

```typescript
import { createAgent, tool } from 'pi-agent-core'
import { piAi } from 'pi-ai'

const agent = createAgent({
  model: piAi('anthropic', { model: 'claude-sonnet-4-20260514' }),
  systemPrompt: 'You are a code reviewer. Analyze pull requests for security issues.',
  tools: [
    tool('readFile', async (path: string) => await fs.readFile(path, 'utf-8')),
    tool('listFiles', async (dir: string) => await fs.readdir(dir)),
  ],
  hooks: {
    beforeToolCall: (call) => {
      console.log(`Calling ${call.tool} with`, call.args)
      return call
    },
  },
})

for await (const event of agent.run('Review the PR in /workspace/pr-42')) {
  console.log(event.type, event.data)
}
```

The `for await` event stream is the key design choice — it makes Pi composable. Flue wraps this stream into HTTP responses, WebSocket pushes, and file outputs. Agno maps it into its FastAPI runtime. Cloudflare pipes it through Durable Objects for crash recovery.

## How Do Flue and Agno Build on Pi Agent Core?

This is where the ecosystem differentiation becomes useful. Pi is the harness. Flue and Agno are frameworks designed for fundamentally different use cases, and understanding which one you need starts with understanding what Pi gives them both.

### Flue: Full-Stack Agent Framework from the Astro Team

Flue, built by the Astro team (the same people behind the popular static site generator), treats Pi Agent Core as its execution engine and builds a full framework on top. It adds:

- **Declarative agent definitions** — You describe what the agent knows (Markdown files), not what it does (TypeScript code). Agent skills are `.md` files read at runtime, meaning the same skill file works in Claude Code, Cursor, and production Flue deployments.
- **Multi-target deployment** — One codebase deploys to Node.js, Cloudflare Workers, GitHub Actions, or GitLab CI. The framework handles the runtime adaptation; your agent code doesn't change.
- **Durable streams** — Append-only event logs that survive process crashes. If your agent runs for 20 minutes and the server restarts at minute 17, Flue replays the event log from the last durable checkpoint — not from the beginning.
- **Virtual sandbox** — A `just-bash` backend plus Cloudflare Shell provide sandboxed code execution without Docker overhead.
- **CLI** — `npx flue dev`, `npx flue deploy`, `npx flue logs` — the Astro team's DX sensibility applied to agents.

Flue is the right choice when you want a full opinionated framework, you're comfortable with TypeScript, and you want to deploy the same agent to multiple runtimes without rewriting it.

### Agno: Production Agent Platform SDK

Agno (disclosure: I covered its architecture in depth in the [Agno Framework Guide](/posts/agno-phidata-framework-guide-2026/)) takes Pi in a different direction. Instead of wrapping it in a TypeScript framework, Agno uses Pi as the execution core for its Python SDK. Yes — Pi is TypeScript, Agno is Python. Agno wraps Pi's event stream via a bridge layer and exposes it as Python agent primitives:

- **Framework-agnostic agent definitions** — Wrap Claude SDK, LangChain, or any agent framework. Pi handles the core loop; Agno handles connectivity to 100+ integrations.
- **AgentOS** — FastAPI-based production runtime with 50+ endpoints, SSE, WebSocket, session persistence, and RBAC.
- **Human-in-the-loop** — Built-in approval system for sensitive tool calls.
- **OpenTelemetry** — Production observability out of the box.
- **Session persistence** — Agents store state in your own PostgreSQL or SQLite database.

| Feature | Flue | Agno |
|---|---|---|
| Language | TypeScript | Python (wrap via bridge) |
| Deployment targets | Node, Cloudflare, GitHub Actions, GitLab CI | FastAPI / AgentOS |
| Agent definition | Markdown files (skills) | Python SDK with tools |
| Sandbox | Virtual (just-bash, Cloudflare Shell) | Docker / AgentOS |
| Observability | Durable streams + logs | OpenTelemetry native |
| Control plane | None (BYO) | AgentOS + hosted UI |
| Community | 5K GitHub stars | 40K+ GitHub stars |
| Best for | Teams that want runtime portability + skills in markdown | Teams that want Python SDK + production infra |

## Why Did Cloudflare Adopt Pi as Their Agent Harness?

The June 17, 2026 announcement from Cloudflare opened their Agents SDK to any harness, with Flue as the first officially supported framework. The architecture uses a three-layer model:

- **Framework layer**: Flue — project structure, conventions, CLI, DX
- **Harness layer**: Pi / Project Think — agentic loop that calls tools, reads results, manages context
- **Runtime layer**: Cloudflare Agents SDK — compute, state, storage primitives (durable execution, sandboxing)

Cloudflare's bet is that separating these concerns lets each layer evolve independently. The runtime layer provides primitives like `runFiber`/`stash`/`onFiberRecovered` for durable execution, Code Mode (dynamic Worker isolates with 10ms cold start), and Shell (SQLite-backed durable virtual filesystem). The harness layer (Pi) doesn't need to know about any of this — it just calls tools and streams events. Flue maps Pi's event stream to Cloudflare's Durable Objects transparently.

This matters because Cloudflare validated that Pi's minimal design is a feature, not a limitation. A harness that tries to do everything — built-in MCP, sub-agents, plan mode, sandboxing — can't slot cleanly into a platform that provides those capabilities natively. Pi's "just the loop" philosophy made it the right abstraction boundary.

## How Does Pi Compare to Other Agent Harnesses in 2026?

I've worked with Claude Code SDK, OpenAI Agents SDK, and OpenHarness in production. Here's how Pi positions against them:

| Dimension | Pi Agent Core | Claude Code SDK | OpenAI Agents SDK | OpenHarness |
|---|---|---|---|---|
| **Provider lock-in** | None (pi-ai abstracts all) | Anthropic only | OpenAI only | None |
| **Language** | TypeScript | TypeScript | Python / TypeScript | Python |
| **Core size** | ~300 lines | ~15K+ lines | ~10K+ lines | ~30K+ lines |
| **MCP** | Not built-in (add via extension) | Native | Native | Native |
| **Event streaming** | First-class | SDK-specific | SDK-specific | Debug-only |
| **Sub-agents** | Not built-in | Yes | Yes | Yes |
| **Runtime-agnostic** | Yes (Node, CF, Deno) | Node only | Python runtime | Python only |
| **npm downloads/week** | 2.8M | 1.2M (est.) | 900K (est.) | 40K (est.) |
| **Default tools** | 4 (Read, Write, Edit, Bash) | ~20 | ~15 | 43 |

The "agent extends itself" philosophy — where Pi agents write their own extensions during execution — is the most distinctive capability. If your agent needs a new tool to complete its task, it can write the extension, register it, and continue. No other harness treats extension-authoring as a runtime primitive.

[OpenHarness](/posts/openharness-universal-agent-harness-2026/) takes the opposite approach: more built-in tools, MCP-native, and a 10-subsystem architecture. It's better if you want everything out of the box. Pi is better if you want a core you understand completely and a framework layer (Flue, Agno, or your own) that adds exactly what you need.

## When Should You Use Pi Agent Core vs. a Higher-Level Framework?

Three scenarios where Pi makes the most sense:

1. **You're building a custom agent framework** — If you're shipping a product that wraps agents (like a customer support platform or a code review bot), Pi gives you the loop without dictating your architecture. You own the framework layer above it.

2. **You need multi-provider portability** — If your architecture requires running different models for different tasks (Claude for reasoning, GPT-4 for structured output, Gemini for multimodal), Pi's provider abstraction handles this without framework overhead.

3. **You're deploying to edge runtimes** — Cloudflare Workers, Deno, and Bun all run Pi without modification. Most SDKs assume Node.js or a Python runtime.

For everything else — single-agent coding assistants, research agents, simple automation — Flue or Agno will save you time. Pi is the foundation layer, not the end product.

## FAQ

### Is Pi Agent Core production-ready?

Yes. 2.8 million weekly npm downloads, adopted by Cloudflare as their reference harness, and powering production deployments of Flue and Agno. The core is small, well-tested, and has been in active development since late 2024.

### Does Pi Agent Core support Python?

No — Pi is TypeScript/JavaScript only. However, frameworks like Agno bridge Pi's event stream into Python via a runtime bridge. If you need a pure Python agent harness, [OpenHarness](/posts/openharness-universal-agent-harness-2026/) or LangGraph are better options.

### How is Pi different from Claude Code SDK?

Claude Code SDK is Anthropic's harness for building Claude-only agents. Pi is provider-agnostic — you can swap from Claude to GPT-4 to Gemini by changing one config line. Pi also has the "agent extends itself" runtime primitive and is open-source, whereas Claude Code SDK is not fully open.

### Does Pi work with MCP servers?

Not natively. Pi intentionally does not include built-in MCP support — it provides extension hooks where you can add MCP connectivity via the extension system. Flue adds native MCP support at the framework layer. If MCP is a requirement, start with Flue rather than raw Pi.

### Can I use Pi Agent Core with non-LLM agents?

The harness is designed for LLM-driven agents — the perceive-reason-act loop assumes a model that generates tool calls from context. If you're building rule-based automation or deterministic workflows, a traditional workflow engine (Temporal, Airflow) is more appropriate. Pi shines where you need an LLM deciding which tools to call and in what order.
