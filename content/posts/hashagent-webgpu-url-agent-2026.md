---
title: "HashAgent: Share an AI Agent as a URL That Runs Locally via WebGPU"
date: 2026-08-14T19:01:26+00:00
tags:
  - AI Agents
  - WebGPU
  - Local AI
  - Privacy
  - Browser Inference
  - LLM
description: "HashAgent is an open-source web app that compresses an AI agent's behavior into a #agent= URL and runs it entirely on your device via WebGPU — no server, account, or tracking."
draft: false
cover:
  image: "/images/hashagent-webgpu-url-agent-2026.png"
  alt: "HashAgent: Share an AI Agent as a URL That Runs Locally via WebGPU"
  relative: false
schema: "schema-hashagent-webgpu-url-agent-2026"
---

## What Is HashAgent? A Private AI Agent You Share as a URL

HashAgent is an open-source web application that lets you build, run, and share an AI agent as a single self-contained URL that executes entirely in your browser via WebGPU. Instead of sending your prompts to a cloud inference server, HashAgent packages an agent's behavior — its system prompt, tool wiring, and a runtime model profile — into one compressed `#agent=` URL. When someone opens that link, their own device downloads a small model and runs the agent locally, with no inference server, no account, and no tracking. It launched on Hacker News on August 14, 2026 (story 49298088) and hit the front page with 38 points and 4 comments at the time of writing.

The core idea is a genuine departure from the dominant cloud-agent model. Most agents today (ChatGPT, Claude, Gemini) are thin clients over a remote model. HashAgent inverts that: the agent definition and the inference both travel to the user's hardware and never leave it. That is the strongest differentiator against every hosted assistant, and it is the reason the project frames itself as a privacy-first answer to the question of where AI agents should actually run.

## How It Works — the #agent= URL Protocol and Local Execution

The technical heart of HashAgent is its URL protocol. The agent's behavior and runtime profile are compressed using deflate-raw and URL-safe base64 into a single `#agent=` fragment appended to the HashAgent URL. Because the payload sits in the URL fragment (after the `#`), it is never sent to a server in an HTTP request — the agent definition travels with the link, but only the browser ever reads it.

When a recipient opens the link, the runtime parses that fragment, reads the requested model profile, and selects a safe model for the current device. The agent then executes using two in-browser inference engines: WebLLM and Transformers.js. All inference happens on-device through WebGPU compute shaders, and any persistent state is kept in the browser's IndexedDB.

Protocol v2 adds an important refinement: it separates the agent's behavior from the runtime model. A phone does not blindly honor an agent that hints at an 8B model. Instead, the URL carries a device profile — `auto`, `mobile`, `balanced`, `quality`, or `vision` — and the client matches it to hardware before downloading anything. The practical effect is that the same shared agent URL renders differently on a phone than on a desktop, but always within the memory budget that device can actually handle.

## Why Local Matters: Privacy, No Account, No Inference Server

The privacy case is the headline feature, and it is unusually thorough for a web project. HashAgent runs no inference server, requires no account, collects no tracking, and serves no analytics code and no cookies. Chat is ephemeral by default, with optional IndexedDB persistence. Crucially, the agent payload is never transmitted in HTTP requests, so your agent definition and your conversation never cross a network boundary.

This matters in a category where "private" is usually marketing. A hosted agent necessarily ships your prompts, your tool calls, and often your retrieved documents to a third-party model endpoint. HashAgent genuinely does not have that failure mode because there is nothing to intercept — the model weights run in your GPU's shaders, not in someone's datacenter. For sensitive use cases (legal, medical, internal company data) the "no server" property is not a feature toggle; it is an architectural guarantee.

The trade-off, discussed honestly in the brief, is that only relatively small models fit in-browser. The Hacker News community praised making local AI accessible while noting that browser-fit models are tiny compared to frontier cloud models. Local privacy buys you capability headroom that is currently measured in single-digit billions of parameters, not hundreds of billions.

## Built-in Models and Honest Device Matching

The built-in model range illustrates both the promise and the ceiling of in-browser inference. At the low end, SmolLM2 360M downloads about 210 MB and uses roughly 580 MB of runtime memory. At the high end, Llama 3.1 8B needs about 4.3 GB to download and around 5.0 GB at runtime — beyond most phones and demanding even on many laptops. The auto profile picks SmolLM2 360M on phones and Qwen2.5 3B on desktop-class devices, which downloads ~1.66 GB and uses ~2.5 GB.

What makes this credible rather than naive is the honest device-matching layer. Protocol v2 prevents a phone from blindly loading an 8B model, and memory budgets and download sizes are surfaced to the user before any download begins. This is the "honest" part of the pitch: no silent OOM crashes, no surprise multi-gigabyte fetches on a phone. You see the cost before you commit, and the runtime refuses to let hardware overreach.

| Model | Download | Runtime memory | Typical device |
|---|---|---|---|
| SmolLM2 360M | ~210 MB | ~580 MB | Phones (auto) |
| Qwen2.5 3B | ~1.66 GB | ~2.5 GB | Desktop-class (auto) |
| Llama 3.1 8B | ~4.3 GB | ~5.0 GB | High-end desktops only |

The honest takeaway is that capability scales with hardware. On a phone you get a small but genuinely functional on-device assistant; on a beefy desktop you can approach 8B-class quality. That is a real, usable spectrum — but it is not parity with cloud frontier models.

## The Tools Layer: Local-tier APIs vs the Optional Cloudflare Gateway

HashAgent's tools are split into two tiers. Local-tier tools — weather via Open-Meteo and Wikipedia — are fetched directly from the browser, with no server in between. These are CORS-friendly public APIs that an agent can call straight from the page, preserving the no-server property.

The second tier is an optional, stateless Cloudflare Pages Functions gateway exposing `/api/search` and `/api/read`. It exists for a mundane but real reason: search providers and arbitrary public pages block direct browser CORS requests. The gateway routes around that browser limitation. Crucially, it is stateless, can be disabled, and is not required for core operation — which keeps it consistent with the project's sovereignty stance. If you want zero cloud dependence, you can turn it off and accept that search and arbitrary-page reads will not work from the browser directly.

## WebGPU as the Enabler: WebLLM + Transformers.js Under the Hood

HashAgent rides on two mature open-source engines. WebLLM (about 18.5k GitHub stars) is a high-performance in-browser LLM inference engine that ahead-of-time compiles models via Apache TVM into optimized WebGPU compute shaders; its `prebuiltAppConfig` model registry is what HashAgent checks against. Transformers.js (about 16.2k stars) runs Hugging Face Transformers in the browser via ONNX Runtime Web, with a WASM fallback when WebGPU is unavailable and a broader range of supported architectures — including verified ONNX community exports for models like Gemma 4, Qwen3.5, and LFM2. The WebGPU specification repo itself sits at about 5.4k stars.

WebGPU is the enabling abstraction because it gives browsers a low-level, GPU-parallel compute API that is fast enough for real neural-network inference. Before WebGPU, in-browser ML meant either WASM (slow, CPU-only) or WebGL hacks (fast but awkwardly repurposed). WebGPU lets engines like WebLLM compile optimized compute shaders that run LLM forward passes at near-native speed on supported hardware. HashAgent is essentially a demonstration that this stack has matured enough to power a usable, shareable agent rather than just a tech demo.

## Where It Falls Short: Tiny Models, iOS Limits, and Practical Ceilings

The limitations are real and worth stating plainly. First, the model ceiling: because everything runs in-browser, only relatively small models fit, roughly 360M to 8B. You get genuinely useful but not frontier-quality results, and 8B class is out of reach for most phones. Second, iOS is a hard constraint: ONNX Runtime Web's WebGPU execution provider is not supported on iOS browsers, so iPhones fall back to WebLLM and the mobile model tier. Third, hardware requirements are non-trivial — you need current Chrome or Edge 113+, or Safari 26+, on hardware with working WebGPU support, and the largest models demand several gigabytes of download and RAM. Fourth, initial model downloads are large: even the smallest built-in model is a ~210 MB fetch, and the first run on desktop can be a 1.6+ GB download. Finally, the search/read tools depend on the optional gateway because browsers block direct CORS to many endpoints, which slightly complicates the "no server" story for full tooling.

The honest framing is a trade-off between capability and locality. Local execution buys you privacy, offline capability after the initial download, and zero recurring cost. It costs you model size, hardware reach, and — in practice — the raw reasoning quality of hosted frontier models.

## How HashAgent Compares to BrowserAI, ThinkHere/LocalMind, and peerd

HashAgent is not alone in the in-browser-AI space, but it occupies a distinct niche. BrowserAI (about 1.4k stars) also runs LLMs in the browser via WebGPU with near-native performance, 100% privacy, zero server costs, and offline capability after initial download; it switches between MLC, Transformers.js, Flare, and Demucs engines and supports structured output, TTS, speech recognition, and audio source separation. But BrowserAI's focus is a dev library plus a no-code builder — it is not a shareable-URL agent protocol.

ThinkHere (from LocalMind) is a privacy-first chat app that runs entirely in the browser via WebLLM, Transformers.js, and WebGPU, with two runtimes (WebLLM+MLC precompiled shaders and Transformers.js+ONNX with WASM fallback), multimodal input, and a local RAG knowledge base with embeddings in IndexedDB. It is chat-focused, not an agent-shareable-URL system.

peerd is the most architecturally different: a web-native AI agent harness built on browser primitives (Workers, origins, sandboxing, OPFS, WASM/WASI, WebRTC, WebAuthn, WebExtensions) that can read and drive tabs, signed-in sessions, and web apps, with preliminary local WebGPU/WebNN support. Rather than a URL-shareable focused agent, peerd pulls the harness into the browser as a browser-native agent runtime.

| Project | Core purpose | Share-by-URL | Stars |
|---|---|---|---|
| HashAgent | Shareable on-device agent via URL | Yes (core) | new |
| BrowserAI | Dev library + no-code agents | No | ~1.4k |
| ThinkHere/LocalMind | Privacy-first in-browser chat | No | — |
| peerd | Browser-native agent harness | No | — |
| WebLLM (engine) | In-browser LLM inference | N/A (engine) | ~18.5k |
| Transformers.js (engine) | In-browser transformers | N/A (engine) | ~16.2k |

The niche HashAgent owns is the shareable-by-URL agent: a complete, compressed agent definition that runs locally when opened. Its competitors solve adjacent problems — libraries for developers, chat apps, or browser-native harnesses — but none make the *agent itself* portable as a link.

## Should You Use HashAgent? — Verdict and Use Cases

HashAgent is worth a look if you value privacy and control more than frontier reasoning power. The strongest use cases are: sharing a sensitive or domain-specific agent with a colleague where neither side wants prompts to hit a cloud endpoint; offline-capable assistants that keep working after an initial model download; and a zero-account, zero-cost way to run a genuinely private AI agent on your own hardware. For fully self-hosted users, the open-source codebase and the ability to disable the optional gateway make it attractive on sovereignty grounds.

It is a harder sell if your workload needs frontier-level reasoning, complex multimodal understanding, or reliably large context — those are simply beyond current in-browser model limits. You should also verify your hardware and browser support before relying on it, and budget for large first-run downloads.

Overall, HashAgent is a compelling demonstration that the WebGPU stack has matured enough to power real, shareable, on-device agents. Its privacy architecture is genuine rather than cosmetic, its device-matching is honest about memory and download costs, and its niche — the agent as a shareable URL that runs locally — is genuinely unoccupied. If you accept the small-model ceiling, it is a practical, private, and remarkably self-contained way to run AI agents today.

## FAQ

**Does HashAgent require a server or an account to run an agent?**
No. HashAgent runs inference entirely in your browser via WebGPU and requires no account, no inference server, no tracking, and no cookies. Optional features like search and arbitrary-page reads use a stateless Cloudflare gateway that can be disabled.

**How does sharing an AI agent as a URL actually work?**
The agent's behavior and runtime profile are compressed with deflate-raw and URL-safe base64 into a single `#agent=` fragment. The payload lives after the `#` in the URL, so it is never sent in an HTTP request — the browser reads it locally and runs the agent on-device.

**What browsers and hardware does HashAgent need?**
You need a current Chrome or Edge 113+ or Safari 26+ on hardware with WebGPU support. ONNX WebGPU is unsupported on iOS, so iPhones use the WebLLM runtime and stay on the mobile model tier.

**How big are the models, and what do they cost to download?**
Built-in models range from SmolLM2 360M (~210 MB download, ~580 MB runtime) up to Llama 3.1 8B (~4.3 GB download, ~5.0 GB runtime). The auto profile uses SmolLM2 360M on phones and Qwen2.5 3B on desktop (~1.66 GB download, ~2.5 GB runtime).

**Is HashAgent private compared to cloud AI assistants?**
Yes, architecturally. Because inference runs locally and the agent payload never leaves the browser, there is no server to intercept your prompts or agent definition. The trade-off is that browser-fit models are relatively small, so you get privacy at the cost of frontier-level reasoning power.
