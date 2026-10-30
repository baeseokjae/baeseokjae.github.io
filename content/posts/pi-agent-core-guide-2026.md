---
cover:
  alt: 'Pi Agent Core guide: extending a running TypeScript agent with an extension'
  image: /images/pi-agent-core-guide-2026.png
  relative: false
date: 2026-06-20 12:00:00+00:00
lastmod: 2026-10-27T05:49:57.104533+00:00
description: Pi Agent Core is a TypeScript agent loop. Learn to register tools and model providers through extensions, with a local fixture and explicit test limits.
draft: false
schema: schema-pi-agent-core-guide-2026
tags:
- pi agent core
- flue framework
- agno
- runtime-agnostic agent harness
- typescript agent framework
- pi-agent-core
- pi extensions
title: 'Pi Agent Core: Extend a Running Agent Without a Rebuild (2026 Guide)'
---

Pi Agent Core is a runtime-agnostic TypeScript agent loop. The short answer to the question people actually arrive with — how do I add a tool or a model provider to a running Pi agent without forking or repackaging it — is: write one TypeScript file that exports a default factory, call `pi.registerTool()` or `pi.registerProvider()` inside it, and pass the file with `--extension`. Pi loads it through jiti, so there is no compile, build or publish step. This refresh keeps the architecture and ecosystem material and adds the extension lifecycle, plus a registration record from our own fixture with its limits stated plainly.

Both packages, `@earendil-works/pi-agent-core` and `@earendil-works/pi-coding-agent`, carried dist-tag `latest` 1.4.0 when the npm registry documents were read on 2026-10-27. Use the scoped names: the unscoped `pi-agent-core` on npm is an unrelated package.

## What Is Pi Agent Core and Why Does It Exist?

Pi Agent Core is a deliberately minimal agent harness that implements the perceive-reason-act loop: the agent sends context to a model, the model returns tool calls, the harness executes them and feeds results back. It sits between `pi-ai` (a unified multi-provider LLM API layer) and agent applications built on top of it.

The design brief is that the loop should be small enough to read in one sitting, portable across runtimes, and extensible at runtime rather than by rebuilding. What Pi intentionally leaves out: built-in MCP support, sub-agent spawning, plan mode and a built-in sandbox. Those arrive at the framework layer or through extensions. The default tool set in the coding agent is small — Read, Write, Edit, Bash — and everything else is an extension.

## How the Harness Architecture Fits Together

Three layers, separated so each can be replaced without touching the others.

**pi-ai** is transport. It normalises OpenAI, Anthropic, Google Gemini, AWS Bedrock and local Ollama endpoints behind one interface, so the loop calls a provider without caring which backend is behind it.

**pi-agent-core** is the loop. It keeps session state and tool-call history, parses and dispatches tool calls, streams structured events for every step, queues steering and follow-up messages, and exposes `beforeToolCall` / `afterToolCall` hooks for interception.

**pi-coding-agent** is the CLI and session surface on top, with the TUI in `pi-tui`. Cloudflare’s June 2026 Flue integration illustrates how a framework can connect a Pi harness to platform services. Agno is a separate higher-level option discussed below; the sources checked for this guide do not establish a Pi-to-Agno event-stream bridge.

## How an Extension Registers a Tool or Model Without a Rebuild

This is the part the previous version of this guide skipped in a single sentence.

### The factory contract

An extension exports a default factory that receives the `ExtensionAPI` object:

```ts
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // register tools, providers, commands here
}
```

The factory may be synchronous or asynchronous. Pi waits for asynchronous factories before startup continues, which is why a provider registered inside one is already available to startup model selection and to `pi --list-models`. Put registrations in the factory, and put anything that must be torn down at the end of a session in the session lifecycle hooks — not in the factory.

### registerTool

A tool declares a name, a model-facing description, a TypeBox parameter schema and an `execute()` function. The result needs model-facing `content` and a `details` field used for rendering or state reconstruction; pass `details: undefined` when there is nothing structured to return. Throwing from `execute()` produces a failed tool result rather than a crash.

Tools also carry an exposure setting. `direct` is the default: declared to the model while active and callable. `model-only` is declared but never called directly, and the other modes cover code-mode execution, deferred loading and hidden registration. "Registered" and "active" are different states — a tool can exist in the runtime without being in the model's tool list.

### registerProvider

Providers have two registration forms. You can register a complete `Provider` from `@earendil-works/pi-ai`, which brings native authentication, model filtering, discovery, refresh and streaming behaviour, or register a provider name with a `ProviderConfig` — the legacy shape — which is enough to point at an OpenAI-compatible endpoint and declare its models. Provider registration also covers the narrow case: redirect an existing provider by overriding only its `baseUrl` and `headers`, without duplicating its model list.

Calls made after initial extension loading take effect immediately, and `pi.unregisterProvider()` removes a dynamic provider and restores the built-in behaviour it replaced — useful when an extension temporarily shadows a real provider.

### Why no rebuild is needed

Pi loads extensions through jiti, which transpiles TypeScript at import time. A local `.ts` file therefore needs no separate compilation step, no packaging and no reinstall. `pi --extension ./file.ts` loads it into the current process for development; extensions placed in the user or project extension directories load for every session; a Pi package is only needed when you distribute an extension to other people. Editing the file and restarting the session is the whole loop.

Dependencies still have to resolve. Pi's documentation says to keep npm dependencies in a `package.json` next to the extension — a bare file in a directory without them will fail on import. That failure mode is recorded below because it is easy to misread.

### Load order and lifecycle

The documented hook order is `input` → `before_agent_start` → `agent_start` → turns → `agent_end`, followed by a settle phase, and `agent_end` is explicitly not an idle signal: retries, compaction or queued work can start another run. A reload replaces the extension runtime, so state you expect to survive belongs in session-scoped resources rather than module scope.

### The trust boundary

Extensions run inside the Pi process with the same operating-system permissions. They can inspect prompts, tool calls, files, credentials and session history. There is no sandbox between an extension and your machine, so load only extension sources you trust.

## A First-Party Registration Record: What the Fixture Showed

The fixture is a single extension file that registers one tool and one provider. It is reproduced in full apart from a redacted API key, and it is what a private local check on our own host actually ran:

```ts
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "@sinclair/typebox";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "sum_numbers",
    description: "Add two integers. Registered by a runtime extension; no rebuild of Pi.",
    parameters: Type.Object({ a: Type.Number(), b: Type.Number() }),
    execute: async (_id, params) => ({
      content: [{ type: "text", text: String(params.a + params.b) }],
    }),
  } as any);

  pi.registerProvider("probe-local", {
    name: "Probe Local",
    baseUrl: "http://127.0.0.1:9/v1",
    apiKey: "<redacted>",
    api: "openai-completions",
    models: [{
      type: "chat", id: "probe-mini", name: "Probe Mini", reasoning: false,
      input: ["text"], cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 8192, maxTokens: 1024,
    }],
  });
}
```

Loaded with `pi --extension ./probe.ts` against Pi 1.4.0 on Node 24.21.0, the provider appeared in `--list-models` as a `probe-local / probe-mini` row, and in RPC mode `get_state` and `get_available_models` both reported `probe-mini` as the session model with `provider: "probe-local"`. A control run with no `--extension` flag returned zero matching rows, so the row came from the extension rather than from configuration. No build, install or publish step occurred between writing the file and the row appearing.

The second check drove the same file through a stub `ExtensionAPI` with jiti, the loader Pi itself uses. The stub recorded the registrations and called `execute()` directly: `sum_numbers({ a: 2, b: 40 })` returned content text `42`, exit code 0, on 2026-10-27.

### What this record does not show

No model ever called the tool. This host has no Pi provider credentials — `~/.pi/agent/auth.json` is an empty object — and the fixture provider points at an unreachable local address on purpose, so no completion was ever requested. That means model-side tool selection, Pi's own argument validation, the exposure rules and the `content`/`details` result contract were not exercised by these runs. In the stub path the tool object also omits `details`, and it still executed, which is exactly why the stub result must not be read as proof of the documented result contract. Treat this as evidence that runtime registration works and that an `execute()` body runs, and nothing stronger.

### Failure modes worth knowing before you try

- `MODULE_NOT_FOUND: @sinclair/typebox` when the extension imported `Type` before that dependency existed next to the file. Installing the dependency in the neighbouring `package.json` fixed it. Pi's docs state the dependency-location rule; the error is what it looks like when you skip it.
- `--list-models` loaded the file successfully even while that import was unresolved. A green `--list-models` is not proof that a tool body will import cleanly — check the tool path separately.
- Our RPC probe sent `{"jsonrpc":"2.0","id":1,"method":"tools/list"}` and received `Unknown command: undefined`. The request used a JSON-RPC `method` field, whereas [Pi’s documented RPC commands](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md) use a `type` field, for example `{"id":"req-1","type":"get_state"}`. This was a malformed probe, not a valid test of whether Pi supports tool listing or direct tool invocation. The successful `get_state` and `get_available_models` checks are separate observations; a model-backed tool call remains untested.

These three observations are from the private run described above, not from the published documentation.

## What Changed in This Refresh, and Why No Download Figure Appears

The previous version of this page cited 2.8 million weekly npm downloads and undated star counts. Neither survives verification. When the npm downloads endpoint was queried on 2026-10-27 it returned a window of 2026-06-25 to 2026-07-01 rather than a current week, so no dated download figure can be supported and this page states none. Repository star counts below are dated single-day observations from 2026-10-27 and are not adoption metrics.

## How Do Flue and Agno Differ as Higher-Level Options?

**Flue**, from the Astro team, defines agents as TypeScript functions. Its [current README](https://github.com/withastro/flue/blob/main/README.md) shows a function configuring a model, sandbox, skills and tools. Markdown `SKILL.md` files supply reusable skills; they are not the agent-definition format. The README lists Node.js, Cloudflare Workers, GitHub Actions and GitLab CI/CD among its deployment targets. Its repository had 8,549 stars in the stored 2026-10-27 snapshot.

**Agno** is a separate agent platform. Its [README](https://github.com/agno-agi/agno/blob/main/README.md) lists the Agno, Claude Agent and Codex SDKs for building agents, with AgentOS providing APIs, authentication, durable execution and human approvals. Its [harness integration guide](https://docs.agno.com/tutorials/harnesses-as-a-service) describes running Claude and Codex behind AgentOS. Neither source establishes the Pi-core architecture or TypeScript-to-Python bridge previously claimed here; those claims are withdrawn. Its repository had 42,912 stars in the stored 2026-10-27 snapshot.

| Decision | Flue | Agno |
|---|---|---|
| Agent definition | TypeScript functions configuring model, sandbox, skills and tools | Agents built with the Agno, Claude Agent or Codex SDKs |
| Service/deployment layer | Multiple documented targets, including Node.js and Cloudflare Workers | AgentOS APIs, authentication and durable execution |
| Relationship to Pi established here | Cloudflare’s June 2026 Flue integration used Pi, as described below | No Pi-core or Pi-to-Python bridge established by the checked sources |
| Stars, snapshot 2026-10-27 | 8,549 | 42,912 |

Choose between these approaches based on the agent-definition and service interfaces your application needs. Shared terms such as “harness” or “agent platform” do not by themselves establish a shared execution core.

The `earendil-works/pi` repository itself had 118,073 stars on 2026-10-27 with a push the same day.

## Why Did Cloudflare Adopt Pi as Their Agent Harness?

Cloudflare's June 17, 2026 announcement opened their Agents SDK to any harness, with Flue as the first officially supported framework, in a three-layer model: Flue for project structure and developer experience, Pi for the agentic loop, and the Cloudflare Agents SDK for compute, durable execution and storage. The runtime supplies primitives such as `runFiber`/`stash`/`onFiberRecovered`, Code Mode worker isolates and a SQLite-backed shell; the harness stays unaware of them and just calls tools and streams events.

That split is the argument for a minimal harness: a loop that already contained MCP, sub-agents, plan mode and sandboxing could not have slotted under a platform that provides those natively. This paragraph is retained from the earlier sourcing of this page; this refresh re-verified repository metadata only, not Cloudflare's deployment behaviour.

## How Does Pi Compare to Other Agent Harnesses in 2026?

| Dimension | Pi Agent Core | Claude Code SDK | OpenAI Agents SDK | OpenHarness |
|---|---|---|---|---|
| **Provider lock-in** | None, pi-ai abstracts providers | Anthropic only | OpenAI only | None |
| **Language** | TypeScript | TypeScript | Python / TypeScript | Python |
| **MCP** | Not built-in, add via extension | Native | Native | Native |
| **Event streaming** | First-class | SDK-specific | SDK-specific | Debug-only |
| **Sub-agents** | Not built-in | Yes | Yes | Yes |
| **Runtime-agnostic** | Yes, Node, Cloudflare, Deno | Node only | Python runtime | Python only |
| **Default tools** | Small set (Read, Write, Edit, Bash) | Larger built-in set | Larger built-in set | Larger built-in set |

The comparison rows above are characterisations from earlier reporting on this page; apart from Pi's own repository metadata, they were not re-measured in this refresh, and the earlier table's per-harness download estimates and line counts have been removed because they could not be verified.

The distinctive capability is still that Pi agents can extend themselves: an agent that needs a new tool can write an extension, register it in the running process, and continue. No other harness in this table treats extension authoring as a runtime primitive — though, as the fixture section above shows, "register it" is the part that is demonstrated, and "the model then calls it" is the part that still depends on your provider being reachable. [OpenHarness](/posts/openharness-universal-agent-harness-2026/) takes the opposite approach with a larger built-in surface.

## When Should You Use Pi Agent Core vs. a Higher-Level Framework?

1. **You are building your own agent framework.** Pi gives you the loop without dictating the layer above it.
2. **You need multi-provider portability.** Different models for different tasks go behind one interface instead of one SDK per provider.
3. **You are deploying to edge runtimes.** Node, Cloudflare Workers, Deno and Bun all run it; the runtime adaptation is not yours to write.

For a single-agent coding assistant or a straightforward automation, Flue or Agno will save you the framework work. Pi is the foundation layer, not the product.

## Harness Engineering Next

If the question behind this page is really "how should the harness be shaped", two companion pieces go further without repeating this material: [AI Harness Engineering](/posts/ai-harness-engineering-guide-2026/) for structured, deterministic workflows, and [Coding Agent Harness Design and Performance](/posts/harness-design-coding-agent-performance-2026/) for the performance consequences of harness choices. If you need the extension directory location on Linux first, see [Pi Coding Agent Configuration on Linux](/posts/pi-coding-agent-config-linux/); for a plugin and skill catalogue, see [The Complete AI Coding Agent Setup Config](/posts/pi-config-coding-agent-setup/).

## FAQ

### Do Pi extensions need TypeScript compilation?

No. Pi loads extensions through jiti, which transpiles TypeScript at import time, so `pi --extension ./file.ts` runs the file as written. A Pi package is only required to distribute an extension to other users.

### Where do extension files live?

For development, pass the file with `--extension`. For persistence, place it in the user or project extension directory so it loads in every session. Keep its npm dependencies in a `package.json` beside it, or imports will fail even though `--list-models` looked fine.

### Can I add a model provider without forking Pi?

Yes. `pi.registerProvider()` accepts either a complete `Provider` or a legacy `ProviderConfig`, and an async factory is awaited before startup completes, so the provider is available to `--list-models` and to startup model selection. Narrower still: register an existing provider with only a different `baseUrl` and `headers`.

### Does registration prove a model can call the tool?

No. Registration and the `execute()` path can be verified without a model, as done here, but whether the model picks the tool depends on the provider being reachable and on Pi's exposure and validation rules. Verify that path with real credentials before relying on it.

### Is Pi Agent Core production-ready?

Cloudflare documented a Flue integration using Pi in June 2026. That integration example does not establish readiness for every workload. This refresh could not verify a current download figure or independently test a model-in-the-loop tool call, so judge readiness against your own provider and workload.

### Does Pi support Python?

Pi itself is TypeScript. The Agno sources checked here describe its own SDK and AgentOS service integrations; they do not establish an Agno Python binding or event-stream bridge for Pi. Evaluate a Python integration separately rather than assuming one from the framework comparison.

## Primary Sources

- Pi extension documentation (loader, factory contract, lifecycle, trust boundary): https://pi.dev/docs/latest/extensions
- Pi custom provider documentation (registration forms, async factories, unregisterProvider): https://pi.dev/docs/latest/custom-provider
- Extension reference in the repository, covering tool schema, result contract and exposure: https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/extensions.md
- npm registry document, `@earendil-works/pi-agent-core` (dist-tags read 2026-10-27): https://registry.npmjs.org/@earendil-works/pi-agent-core
- npm registry document, `@earendil-works/pi-coding-agent` (dist-tags read 2026-10-27): https://registry.npmjs.org/@earendil-works/pi-coding-agent
- GitHub REST metadata, `earendil-works/pi` (stars and last push, 2026-10-27): https://api.github.com/repos/earendil-works/pi
- GitHub REST metadata, `withastro/flue` (stars, 2026-10-27): https://api.github.com/repos/withastro/flue
- GitHub REST metadata, `agno-agi/agno` (stars, 2026-10-27): https://api.github.com/repos/agno-agi/agno

The registration fixture, transcripts and raw response bodies described in this article are a private local author verification, not a published download. The extension source is reproduced in full above so the check can be repeated against your own Pi install; the raw vendor responses are not redistributed.
