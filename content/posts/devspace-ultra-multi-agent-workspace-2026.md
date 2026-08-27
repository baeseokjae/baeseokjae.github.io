---
title: "DevSpace Ultra: Build a Multi-Agent Dev Workspace with ChatGPT Classic Workers"
date: 2026-08-27T04:01:17+00:00
tags:
  - multi-agent dev workspace
  - DevSpace Ultra
  - ChatGPT Classic workers
  - Chat Swarm
  - elastic worker pool
  - MCP server coding agent
  - self-hosted AI coding agent
  - multi-agent orchestration
description: "DevSpace Ultra turns one ChatGPT subscription into an elastic pool of parallel coding workers on your own machine. Here's how it works, what it costs, and who it's for."
draft: false
cover:
  image: "/images/devspace-ultra-multi-agent-workspace-2026.png"
  alt: "DevSpace Ultra: Multi-Agent Workspace with ChatGPT Classic Workers"
  relative: false
schema: "schema-devspace-ultra-multi-agent-workspace-2026"
---

A multi-agent dev workspace lets you run several AI coding workers in parallel on your own machine, and DevSpace Ultra is the open-source tool that makes it possible using nothing more than your existing ChatGPT subscription. It layers an elastic "Chat Swarm" control plane on top of the DevSpace local MCP workspace, so one ChatGPT account can power a pool of independent ChatGPT Classic worker conversations that scale up and down with your workload. This guide explains what DevSpace Ultra is, how the worker pool works, how to set it up, and the honest platform and cost trade-offs you need to know before adopting it.

## What Is DevSpace Ultra and Why Multi-Agent Workspaces Matter

DevSpace Ultra is an MIT-licensed distribution of DevSpace that adds a production-oriented multi-agent runtime layer. The upstream DevSpace project, created June 14, 2026, is a small self-hosted MCP server that lets ChatGPT open a real project folder, read and edit files, run shell commands, and show diffs — the same loop as Codex or Claude Code, but running on your laptop against the folder you actually have open. DevSpace Ultra keeps all of that local MCP workspace functionality (files, code search, editing, terminal, artifacts, skills, self-hosting) and adds a Chat Swarm control plane for running multiple independent ChatGPT Classic worker conversations on one computer.

Why does this matter? Plain ChatGPT chat has no filesystem access, and Code Interpreter only runs Python in a throwaway container. Codex works against a cloned repo in a cloud sandbox, not the folder open in your editor. A multi-agent dev workspace closes that gap: it gives you a real, local, parallel workforce of coding agents instead of a single sequential chat. The category is being legitimized by OpenAI itself, which introduced native workspace agents in ChatGPT — but DevSpace Ultra represents the self-hosted, community-driven alternative that keeps your code local and your data on your own hardware.

## DevSpace Ultra vs OpenAI Workspace Agents: Self-Hosted vs Native

The "multi-agent dev workspace" keyword now spans two very different approaches. OpenAI's native workspace agents are the mainstream, enterprise direction: they live inside ChatGPT, are managed by OpenAI, and require no self-hosting. DevSpace Ultra is the opposite: a self-hosted, open-source tool that orchestrates ChatGPT Classic workers you control.

| Feature | DevSpace Ultra (self-hosted) | OpenAI Workspace Agents (native) |
| --- | --- | --- |
| Hosting | Your own machine | OpenAI cloud |
| Code location | Local folder you open | Cloud sandbox / workspace |
| Cost | Free (MIT) + your ChatGPT plan | ChatGPT plan (paid tiers) |
| Worker pool | Elastic, user-controlled | Managed by OpenAI |
| Control plane | Chat Swarm backend | Native ChatGPT UI |
| Data control | Full (self-hosted MCP) | OpenAI-managed |
| Platform | Win/macOS/Linux (cloning Windows-only) | Cross-platform |

The trade-off is control versus convenience. Native workspace agents are easier and require no infrastructure, but they run in OpenAI's cloud. DevSpace Ultra keeps everything local and gives you fine-grained control over how many workers run, how they scale, and how they recover — at the cost of setup and maintenance. For developers who care about data locality, cost control, or running many parallel workers on one subscription, the self-hosted route is compelling.

## How the Chat Swarm Control Plane Works (Elastic Worker Pool)

The heart of DevSpace Ultra is the Chat Swarm backend, a control plane that manages a pool of independent ChatGPT Classic worker conversations. The key design decision is that it separates runtime capacity from task routing. You configure a desired number of workers, and the elastic scaling mechanism grows or shrinks the runtime and Swarm capacity to match.

The elastic worker pool works like this:

- **Main agent scales workers up and down** based on workload, so you are not stuck with a fixed pool.
- **Live Swarm resize** can happen without losing completed work — scaling down only removes safe idle tail capacity and never interrupts a busy worker.
- **Independent runtimes** on Windows use isolated package identities, profiles, sessions, and conversations, so each worker is a clean, separate ChatGPT Classic instance.
- **Same-worker context continuity** lets you reopen a worker at the exact saved ChatGPT conversation and continue with the held worker token.
- **Zero-copy bootstrap** launches a worker, minimizes it, sends it into a sub-agents ChatGPT Project, joins the Swarm, and parks it — without manual invite-code copy/paste.
- **Backend-first routing** means normal work is dispatched through the Chat Swarm backend; UI/CDP automation is reserved for lifecycle, bootstrap, and recovery only.

The backend supports create/join/status, dispatch/collect/cancel, long parked worker waits with submit/repark, targeted or first-available routing, idempotent taskKey retries, persistence across restart, worker recycle fallback, and safe live capacity resize. This is a genuinely production-oriented design rather than a script that spawns a few chat windows.

## Setting Up DevSpace Ultra: One-Click Install and Requirements

Installation is designed to be one command. On Windows, run the PowerShell installer; on macOS and Linux, use the shell installer; and there is also an npm global install:

```bash
# Windows (PowerShell)
irm https://.../install.ps1 | iex

# macOS / Linux
curl -fsSL https://.../install.sh | bash

# Any platform via npm
npm install -g github:enwong93-sketch/devspace-ultra#main
```

Before you install, check the requirements:

- **Node.js >= 22.19 and < 27** (Node 22 LTS recommended)
- **Windows 10/11 x64** for automatic isolated desktop runtime cloning
- **ChatGPT Classic Windows Desktop app** signed in
- **16 GB RAM** for 2-4 workers; **32 GB+** for larger pools
- **No GPU required**

The base MCP workspace, Chat Swarm backend, manual/browser workers, and elastic resize work on Windows, macOS, and Linux. But the automatic isolated desktop runtime cloning, recovery, and canary/rolling update manager are Windows-only. If you are on macOS or Linux, you get the full control plane but not the Windows package-identity worker-cloning path.

## Configuring ChatGPT Classic Workers and the sub-agents Project

Once installed, you configure how many workers you want and how they are organized. The `reservedWorkers` setting lets you reserve runtime capacity, and by default no runtime is reserved — you scale up on demand.

A useful organizational feature is the **sub-agents Project routing**: new worker conversations are created inside a configured ChatGPT Project instead of cluttering your general chat list. This keeps your worker pool tidy and separate from your personal conversations.

The runtime tools you will use include:

- `chat_swarm_runtime_status` / `ensure` / `scale` / `recover` / `autojoin` / `setup` / `stop`
- `chat_swarm_elastic_scale`
- `chat_swarm_update_status` / `rollout`

These give you direct control over the worker pool: check status, ensure runtimes are present, scale capacity, recover interrupted workers, autojoin the Swarm, and manage updates.

## The Production Flow: Assess, Scale, Dispatch, Collect, Shrink

DevSpace Ultra is designed around a repeatable production workflow rather than ad-hoc experimentation. The recommended flow is:

1. **Assess** the workload — how many parallel tasks do you actually need?
2. **Choose desiredWorkers** — set the target pool size.
3. **Elastic scale** the runtime and Swarm capacity to match.
4. **Dispatch** tasks to the worker pool.
5. **Collect and synthesize** the results.
6. **Shrink** the idle tail workers to free resources.

This assess → scale → dispatch → collect → shrink loop is what makes the tool feel like a real orchestration system rather than a batch script. Because scaling down only removes safe idle capacity, you can shrink the pool aggressively after a burst without risking in-flight work. The elastic scaling design is the key differentiator: one ChatGPT subscription can power a parallel worker pool that grows and shrinks with your workload.

## Recovery, Updates, and Resilience (Canary-First Rolling Updates)

A multi-agent system is only useful if it survives failures, and DevSpace Ultra invests heavily in resilience. The recovery system detects missing runtimes, interrupted connections, stale worker loops, and blocking UI notices, then reopens the exact worker conversation to continue where it left off.

The update compatibility manager is especially notable. It supports:

- **Canary runtime** — test a new version on one worker first
- **Profile backup** — snapshot before any change
- **Rolling worker update** — update workers incrementally
- **Exact-conversation restore** — bring workers back to their precise state
- **Verification and rollback** — confirm the update worked or revert

This canary-first approach means you can update your worker pool without losing completed work or breaking running conversations. For a tool that orchestrates live AI workers, this level of update hygiene is a real differentiator and a strong argument for the project's production readiness.

## Browser Control and the Unified Capability Runtime (v0.2/v0.3)

DevSpace Ultra has evolved quickly. Version 0.2.0 added local-first **DevSpace Browser Control**, a Chrome extension that gives workers exclusive per-tab claims. Each tab shows an "AGENT CLAIMED THIS TAB" strip, and the system provides semantic accessibility snapshots, screenshots, and console/network diagnostics. This lets workers interact with web pages in a controlled, credential-safe way.

Version 0.3 added the **Unified Agent Capability Runtime**, a `capability_*` surface for discovering, installing, inspecting, enabling, updating, isolating, and calling reusable capabilities. It understands Agent Skills, instruction packs, MCP tools/prompts/resources, DevSpace manifests, Claude/Codex plugin metadata, and MCP Registry metadata. In the v0.3 release, DevSpace Ultra scanned 71 Codex plugin manifests and found 71/71 structural compatibility — a strong signal that the capability layer is broadly interoperable with the existing plugin ecosystem.

## Security Model: Self-Hosted MCP, Tokens, and Credential Boundaries

Because DevSpace Ultra is self-hosted, security is your responsibility — and the project takes it seriously. The MCP model is self-hosted, and the guidance is to keep the server bound or exposed only through a controlled transport and to use authentication. Worker and orchestrator tokens are not written to normal controller logs, reducing the risk of credential leakage.

Browser Control uses one-time pairing and exclusive per-tab claims, and it persists only hashes of tokens rather than the tokens themselves. This credential-boundary design means a compromised worker cannot trivially exfiltrate your other credentials. As with any self-hosted tool, you should review the security model, keep the server behind controlled transport, and use auth before exposing it beyond localhost.

## Platform Support and the Windows-Only Reality Check

It is important to be honest about the platform story. The base MCP workspace, Chat Swarm backend, manual/browser workers, and elastic resize work on Windows, macOS, and Linux. But the headline features — automatic isolated desktop runtime cloning, recovery, and the canary/rolling update manager — are **Windows 10/11 x64 only**.

This is the key differentiator and the key limitation. If you are on Windows, you get the full package-identity worker-cloning path that makes the elastic pool seamless. If you are on macOS or Linux, you can still run the control plane and manage workers, but you lose the automatic runtime cloning and recovery that make the Windows experience so smooth. Before adopting DevSpace Ultra, confirm which features you actually need and whether your platform supports them.

## The "Free" Question: ChatGPT Plan Requirements

DevSpace Ultra itself is free and open-source (MIT), but the "free" label needs a reality check. The tool orchestrates ChatGPT Classic workers, which means you need a ChatGPT subscription. More importantly, custom ChatGPT Plugins (formerly connectors) live behind **Developer Mode**, which requires a paid plan — Plus, Pro, Business, Enterprise, or Edu — and is not available on the Free plan.

So the honest cost picture is:

- **DevSpace Ultra**: free (MIT, open source)
- **ChatGPT subscription**: required (paid plan for Developer Mode / Plugins)
- **Hardware**: 16 GB RAM for 2-4 workers, 32 GB+ for larger pools, no GPU

The value proposition is that one paid ChatGPT subscription can power many parallel workers, which is far cheaper than paying per-agent for a managed multi-agent platform. But it is not free in the absolute sense — you need a paid ChatGPT plan and a reasonably specced machine.

## Common Pitfalls and Rough Edges

DevSpace Ultra is genuinely new — the upstream project's first commit was June 14, 2026, and DevSpace Ultra itself was created August 18, 2026. As of the research date it had 35 GitHub stars and 5 forks, compared to 4,032 stars for the upstream Waishnav/devspace project. That maturity gap means you should expect rough edges:

- **Young project**: 35 stars and 5 forks means a small community and limited battle-testing.
- **Windows-only features**: the best features (runtime cloning, recovery, canary updates) do not work on macOS/Linux.
- **Paid plan required**: Developer Mode and Plugins need a paid ChatGPT plan, not Free.
- **Node version constraints**: you must be on Node >= 22.19 and < 27, which may conflict with other tooling.
- **Self-hosting burden**: you own the security, transport, and auth setup.

None of these are deal-breakers, but they are the reality of adopting a young, self-hosted tool. If you are comfortable with early-stage software and want local control, the trade-offs are acceptable.

## Conclusion: Is DevSpace Ultra Right for Your Multi-Agent Workflow?

DevSpace Ultra is a compelling answer to the question of how to build a multi-agent dev workspace without paying per-agent for a managed platform. It turns one ChatGPT subscription into an elastic pool of parallel coding workers on your own machine, with a production-grade control plane, recovery, and canary-first updates. The self-hosted MCP model keeps your code local, and the elastic scaling design is genuinely thoughtful.

It is not for everyone. The best features are Windows-only, you need a paid ChatGPT plan, and the project is very young. But if you are on Windows, want local control over your AI workforce, and are comfortable with early-stage open-source software, DevSpace Ultra is worth a serious look. For everyone else, it is a clear sign of where the multi-agent dev workspace category is heading — and a strong open-source alternative to OpenAI's native workspace agents.

## FAQ

**What is DevSpace Ultra?**
DevSpace Ultra is an MIT-licensed, open-source distribution of DevSpace that adds an elastic Chat Swarm control plane for running multiple independent ChatGPT Classic worker conversations on one computer, turning one ChatGPT subscription into a parallel pool of coding agents.

**Is DevSpace Ultra free?**
The software itself is free and open-source (MIT), but you need a paid ChatGPT plan because custom Plugins and Developer Mode are required and are not available on the Free plan. You also need a machine with at least 16 GB RAM for a small worker pool.

**What are the system requirements for DevSpace Ultra?**
You need Node.js >= 22.19 and < 27 (Node 22 LTS recommended), 16 GB RAM for 2-4 workers (32 GB+ for larger pools), no GPU, and a signed-in ChatGPT Classic Windows Desktop app for the automatic runtime cloning features.

**Does DevSpace Ultra work on macOS and Linux?**
Partially. The base MCP workspace, Chat Swarm backend, manual/browser workers, and elastic resize work on all three platforms, but the automatic isolated desktop runtime cloning, recovery, and canary/rolling update manager are Windows 10/11 x64 only.

**How is DevSpace Ultra different from OpenAI's native workspace agents?**
DevSpace Ultra is self-hosted and keeps your code and data local, with user-controlled elastic worker scaling. OpenAI's native workspace agents are managed in the cloud and easier to use but give you less control and keep your work in OpenAI's infrastructure.
