---
title: "PhoneBuddy SDK Review: A Mobile On-Device Agent SDK in Rust for iOS and Android"
date: 2026-10-01T08:05:33+00:00
tags:
  - mobile on-device agent sdk
  - embeddable rust llm agent ios android
  - phonebuddy sdk review
  - in-process mobile ai agent runtime
  - app store guideline 2.5.2 embedded agent
  - rust mobile llm agent engine
  - on-device agent sandbox security
  - grok-build mobile port
  - phonebuddy vs napaxi
  - llm agent c ffi swift kotlin bindings
description: "PhoneBuddy SDK review: a pure-Rust mobile on-device agent SDK for iOS and Android, with C FFI, Swift and Kotlin bindings — and the audit gaps behind it."
draft: false
cover:
  image: "/images/phonebuddy-sdk-rust-mobile-llm-agent.png"
  alt: "PhoneBuddy SDK Review: A Mobile On-Device Agent SDK in Rust for iOS and Android"
  relative: false
schema: "schema-phonebuddy-sdk-rust-mobile-llm-agent"
---

The best mobile on-device agent SDK answer in 2026 is a pure-Rust engine that runs entirely inside your app process. PhoneBuddySDK, open-sourced by APUS-AI-Lab under Apache-2.0, ships a planner, tool loop, sandboxed file system, virtual shell and JavaScript interpreter with C FFI, Swift and Kotlin bindings — and no child processes anywhere.

## What PhoneBuddy SDK Actually Is (and What It Is Not)

PhoneBuddySDK is a Rust core crate compiled to a C ABI (`phone_buddy.h`) with first-class Swift (`PhoneBuddy.swift`) and Kotlin (`NativeAgent.kt` plus JNI) wrappers layered on top. It landed on GitHub on 2026-08-18 under Apache-2.0. As of 2026-10-01 the repository shows 36 stars, 13 forks, one open issue, and a language breakdown of roughly 1.36 MB of Rust against 36 KB of C — a ratio that tells you where the engineering lives. The C layer is a boundary, not an implementation.

What it is not matters just as much:

- **It is not a cloud agent with a mobile client.** Every capability is re-implemented in Rust and executed in the app's own process.
- **It is not a GUI-automation agent.** It does not tap, swipe or read your screen. It calls typed tools.
- **It is not a hosted model service.** The default transport talks to remote frontier models; an alternate mode delegates inference to a model you host on the device.
- **It is not a finished platform.** There is no public CI workflow, no Android instrumentation suite, and no published app-store review record.

The project is explicit that it derives from xAI's open-source desktop harness, `xai-org/grok-build`. The NOTICE file enumerates the adaptations: `std::process` and `tokio::process` replaced by pure-Rust BusyBox applets, an in-memory Tokio task manager for subagents, `rustls-ring` TLS, and the new C FFI, Swift and Kotlin layers. That derivation is the real story here — not the feature list.

## Why Desktop Agent Architecture Breaks on a Phone

Desktop coding agents assume they may spawn a shell. Claude Code, Codex and Grok Build all build their power on `bash`, on subprocesses, on binaries that exist on the host. On iOS that assumption is fatal: there is no `fork`, no `exec`, no child process to hand a command to. On Android the process model technically permits it, but the Play policy surface around downloaded executable code does not welcome it.

So the interesting engineering problem is not "how do we run an agent on a phone." It is "what remains of a desktop harness when you delete every path that launches a process" — and whether the result still completes real tasks.

PhoneBuddySDK's answer is to replace the missing substrate rather than fake it. Instead of emulating a terminal to trick the model into thinking it has a shell, the SDK re-implements each capability in code and wraps every operation in an execution fence. A file read is a Rust function with a jailed root directory. A directory listing is a Rust function. A `grep` is a Rust function. The model sees familiar tool names; the runtime performs bounded, auditable work.

That distinction — reimplementation over emulation — is precisely what an independent audit was able to confirm statically. No `std::process`. No `tokio::process`. No child-process launch path in the core crates.

### What does "in-process" actually buy you?

Two things, and they cut in opposite directions.

The first is reach. Because the agent lives inside your app, its capability ceiling is your app's own permission set. An agent embedded in a photos app can touch photos. It cannot reach the contacts database. That is a hard boundary enforced by the operating system, not by prompt instructions — which is exactly the property that makes the whole design auditable. There is no escape hatch to audit because there is no escape hatch.

The second is the limitation. An agent in a photos app cannot book a flight. The in-process bet trades general capability for a small, checkable surface. For app developers shipping a specific feature, that is usually the right trade. For anyone hoping to reproduce a desktop coding agent on a phone, it is a ceiling worth understanding before adoption.

### Is this a model problem or an execution problem?

Execution. The same underlying LLM delivers results an order of magnitude apart when you move it from a desktop harness to a phone chatbot. Nothing about the weights changes; what changes is whether the model has tools that produce side effects. Desktop harnesses give the model a filesystem, a shell and a package manager. Mobile chat apps give it a text box.

The research literature reaches the same conclusion from the opposite direction. GUI-action agents that tap and swipe produce long, interface-dependent action sequences and still cannot reach device capabilities directly. Device-tool agents — the pattern PhoneBuddySDK implements — get explicit arguments and defined execution boundaries instead. PalmClaw (arXiv 2607.13027, 2026-07-14), a native on-device agent framework built on the device-tool premise, reports an 11.5% relative improvement in task success and a 94.9% reduction in completion time against the strongest baseline. Those numbers are the framework's own, but the direction is consistent across the field.

## Inside the Engine: ReAct Loop, Virtual BusyBox, Boa JS Sandbox, In-Memory Subagents

Strip the bindings away and the core is a familiar agent harness assembled from parts that had to be rewritten for a process with no shell.

**The loop.** An autonomous planner plus a ReAct tool loop, with doom-loop detection, a history compactor, a session store, an in-memory subagent orchestrator, and cron-style scheduling with a task monitor.

**The file sandbox.** A jailed workspace rooted at a configured `root_dir`, with path-traversal prevention and the usual surfaces: `read_file`, `write_file`, `edit_file`, `list_dir`, `grep`.

**The virtual shell.** Pure-Rust BusyBox applets covering `cat`, `head`, `tail`, `ls`, `wc`, `sort`, `uniq`, `find`, `echo`, `mkdir`, `rm`, `cp`, `mv`, `du`. Each one is a library call wearing a command name.

**The JavaScript sandbox.** An embedded `boa_engine` instance exposed as `run_script` for computation and CSV or JSON manipulation — genuinely useful for data wrangling, and simultaneously the most policy-sensitive component in the stack.

**The subagent manager.** In-memory Tokio task orchestration with cooperative cancellation propagated through it. Subagents are tasks, not processes, which is the only shape that works on iOS.

### What are the verified limits?

This is where the SDK stops being marketing and starts being a system. An independent audit published on 2026-08-23 covering main commit `c661ba0` confirmed these bounds statically:

| Control | Verified limit |
| --- | --- |
| Boa JavaScript execution | 20,000,000-iteration cap |
| Built-in and host tools | 120-second timeout wrapper |
| Doom-loop guard | Nudge after 8 identical calls, break at 16 |
| Cancellation | Cooperative tokens propagated via the in-memory task manager |
| Child processes | None present in core crates |

These are the numbers that matter for a mobile deployment, because they are the difference between an agent that can hang forever and one that is bounded by construction. A 20-million-iteration ceiling on a scripting engine means a pathological script fails rather than pinning a thread until the OS intervenes. A 120-second wrapper means a misbehaving tool cannot silently outlive the user's patience. A doom-loop guard that nudges at 8 and breaks at 16 means a confused model gets two chances before the runtime stops it.

## Native Integration: C ABI, Swift and Kotlin in Practice

The portability bet is a C-ABI-first design: one Rust core, one C header, thin platform adapters. The alternative bet — what `antgroup/Napaxi` takes — is a shared Rust runtime with adapter contracts where Flutter is the first complete target and Android and iOS share a Core API boundary.

| Dimension | PhoneBuddySDK | Napaxi |
| --- | --- | --- |
| Core language | Rust | Rust |
| Boundary | C ABI + Swift + Kotlin wrappers | Core API with mobile adapters (Flutter first) |
| Stars / forks (2026-10-01) | 36 / 13 | 33 / 7 |
| License | Apache-2.0 (permissive) | GPL-3.0 (copyleft) |
| Created | 2026-08-18 | 2026-07-01 |
| Last push | 2026-09-13 | 2026-09-30 |
| MCP surface | Not advertised | Explicit |
| Cross-app connectivity | Not advertised | xApp / xAgent / xChannel |

The practical cost of the C-ABI route is real and worth stating plainly: Rust 1.94+, Android NDK r25+, and four target toolchains to keep building. That is a build-system tax paid on every CI run. In exchange, the integration surface your Swift and Kotlin engineers touch is small and stable — they call into a generated header, not into Rust lifetime rules.

The licensing row is the one that decides corporate adoption. Apache-2.0 permits closed-source distribution. GPL-3.0 does not, in the general case, permit shipping a proprietary mobile app without releasing the corresponding source. For a commercial team evaluating the two closest options in this niche, that single line often settles the comparison before any technical criterion is evaluated.

## Bring Your Own Model: Hosted Protocols vs On-Device Inference

The transport layer supports three wire protocols: `responses` with SSE streaming, `chat_completions`, and `messages`. That is Anthropic, OpenAI and a Responses-style surface covered from one Rust client. Streaming runs HTTP/2 over `rustls-ring`.

The default path is a notable claim: the SDK can emulate client profiles for xAI Grok Build, OpenAI Codex and Anthropic Claude Code at 1:1 fidelity — replicating their exact HTTP headers, thinking signatures and JSON wire schemas from inside a mobile app. For developers building against providers whose APIs are tuned for those first-party clients, that emulation is the difference between working and being rate-limited or rejected.

The alternate path is `LlmMode::Host`, which delegates inference to a model running on the device through `PbLlmRequestCallback`. The intended targets are runtimes like `llama.cpp` and `llama.rn` on NPU-class hardware. This is the mode where the whole architecture pays off: no network round-trip, no per-token cost, no data leaving the phone.

The host-model ecosystem is finally ready for this. Apple exposes its on-device foundation model to third-party developers in Swift, and Google ships Gemini Nano through ML Kit GenAI APIs. Google's FunctionGemma turns natural language into function calls on-device with only 270M parameters — which is close to a purpose-built fit for a tool-calling loop that needs to emit structured arguments rather than prose.

The market context explains why the timing works. Edge AI is projected at $37.51B in 2026, up 29% year over year, with edge AI hardware on track for $58.9B by 2030. AI in mobile apps grew from $30.56B in 2025 to $41.33B in 2026 at a 35.2% CAGR, heading toward $135.54B by 2030. By the end of 2026, 90% of new mobile apps are expected to incorporate AI capabilities, and 63% of mobile app developers are already integrating AI features. Gartner projects 40% of enterprise applications will incorporate task-specific AI agents by the end of 2026, up from less than 5% in 2025.

## The App Store Compliance Question: Guideline 2.5.2 and the Google Play Interpreter Exception

The README asserts the SDK "passes Apple App Store and Google Play app sandbox security reviews with zero permission escalations." That is a project assertion. No public review record exists anywhere, and the independent audit searched for one and found nothing.

So treat the compliance question on the policy text, not on the claim.

**Apple Guideline 2.5.2** requires apps to be self-contained and restricts downloading, installing or executing code that introduces or changes app functionality. The clause exists to stop an app from becoming a launcher for arbitrary later code. An embedded JavaScript interpreter does not make that policy question disappear. An argument can be made that a `boa_engine` instance ships with the binary and can therefore only ever execute code the app already contained — but "an argument can be made" is a different standard from "a reviewer has accepted it," and no accepted instance is on record.

**Google Play's Device and Network Abuse policy** prohibits downloading executable `dex`, `JAR` or `.so` artifacts outside Play, while permitting VM and interpreter code under conditions. That carve-out is friendlier on its face, but it is conditional rather than blanket.

The practical position for a team planning to ship: the architecture is defensible, the claim is unverified, and the embedded JS engine is the specific component a reviewer will ask about. Prepare an answer for it before submission rather than after a rejection. If `run_script` is not on your product's critical path, disabling it removes the question entirely.

## What the Independent Audit Verified — and What Remains Unproven

The audit that did the real work here ran on main commit `c661ba0` and confirmed, statically: no process-launch path in the core crates, path jailing, bounded JavaScript, tool timeouts, cancellation-token propagation, and functioning Swift, Kotlin and C integration.

It also documented what it could not verify, and those caveats are the most valuable part of the report:

- **174 Rust tests are defined, but there is no public GitHub Actions workflow.** A test count is not a test result. The auditor could not execute them because the host lacked a Rust toolchain.
- **No Android instrumentation suite exists.** The platform with the more permissive process model is the one with no device-level test coverage published.
- **The v0.1.2 release points at an earlier commit than the audited main.** Findings from main must not be attributed to the release package without retesting. This is the single most important line in the audit: the sandbox properties you would be shipping are the ones in the tag, not the ones in `main`.
- **No public App Store or Google Play review record was found.**

An honest reading: the architecture is sound as designed, the static evidence is genuinely strong, and the verification stack that would let a team depend on it is incomplete. Those are three separate statements and none of them cancel out.

## Who Should Adopt It Today (and Who Should Wait)

**Adopt it if you are prototyping.** Apache-2.0, pure Rust, a clear C boundary and an in-process design that maps directly onto iOS constraints make this the fastest way to find out whether an on-device agent does anything useful for your users. The 1.36 MB Rust / 36 KB C split means the core is small enough to audit yourself.

**Adopt it if you are building an agent inside one app's permission boundary** and you need a tool loop, a sandbox and a file layer rather than a chat wrapper. You are buying the parts nobody wants to write twice.

**Wait if you need a compliance guarantee before you build.** The review record does not exist. If your organization's ship gate requires either a documented app-store acceptance or a completed CI run over the 174 tests, you must produce that evidence yourself — which is doable and probably worth doing.

**Wait if you need a maintained, community-hardened runtime.** 36 stars and a last push of 2026-09-13 describe a young project. Bus factor is one of the real costs of adoption here, and no license grants you a maintenance commitment.

**Reconsider if your business cannot ship GPL-3.0.** If Napaxi's MCP surface and cross-app connectivity matter more to you than Apache-2.0 permissions, that comparison is genuine and reasonable — but check the license against your distribution model first, because it is the deciding constraint for most commercial apps.

## Verdict: Promising Architecture, Incomplete Verification Stack

PhoneBuddySDK is the most architecturally interesting entry in the mobile on-device agent SDK space right now, and it earns that position for one reason: it took a desktop agent harness and solved the problem of what remains when you delete the ability to spawn a process. The answer — reimplement every capability, fence every operation, bound every loop, and orchestrate subagents as tasks rather than children — is correct for the platform.

The independent audit supports that reading with verified constants: a 20-million-iteration JavaScript cap, a 120-second tool timeout, a doom-loop guard that nudges at 8 and breaks at 16, cooperative cancellation, and no child-process path in the core.

What it does not support is the marketing. There is no CI, no Android instrumentation suite, no public app-store review record, and the released tag lags the audited commit. An embedded JavaScript interpreter keeps Apple's Guideline 2.5.2 question open, and the `LlmMode::Host` path is the mode that best justifies the whole design — but the verification work an adopting team must do themselves is real.

The honest verdict: adopt it as an architecture and a prototype substrate today, and treat the sandbox and compliance claims as a test plan you inherit rather than a property you receive.

## FAQ

### Is PhoneBuddySDK really pure Rust?

The core agent engine is. The repository's language breakdown on 2026-10-01 shows approximately 1.36 MB of Rust against 36 KB of C, with a small shell component. The C exists as a stable ABI boundary — the `phone_buddy.h` header — that the Swift and Kotlin wrappers bind to. The agent loop, file sandbox, virtual shell, JavaScript engine integration and subagent manager are all Rust. No child-process path exists in the core crates, which the independent audit confirmed statically.

### Does it work on iOS given that iOS forbids spawning processes?

That constraint is the reason the SDK is built the way it is. Instead of shelling out, it re-implements each capability in Rust — file operations, a virtual BusyBox-style command set, a bounded JavaScript sandbox — and runs them in the host app's own process. The agent's reach is therefore bounded by the host app's own permissions. iOS compliance is an architectural premise of the project, not an afterthought, though no public App Store review record confirming an actual submission has been found.

### Can the agent write to arbitrary files on the device?

No. The file tools operate inside a jailed workspace rooted at a configured `root_dir`, with path-traversal prevention applied to the operations. That is verified statically by the independent audit. The practical consequence is that the agent can manipulate files your app can already reach, and cannot reach anything your app does not already have permission to touch.

### How does it compare to Napaxi?

Both are Rust mobile agent SDKs and they overlap on sessions, tools, workspace state and platform hooks. Napaxi is GPL-3.0 and takes an adapter-first approach with Flutter as the first complete target, plus an explicit MCP surface and cross-app connectivity through xApp, xAgent and xChannel. PhoneBuddySDK is Apache-2.0, uses a C ABI with first-class Swift and Kotlin wrappers, and does not advertise MCP. For closed-source commercial apps the license difference — permissive versus copyleft — is usually the deciding factor.

### Does it run models locally, or does it need the cloud?

Both are supported. The default transport speaks three wire protocols (`responses` with SSE streaming, `chat_completions`, and `messages`) over HTTP/2 with `rustls-ring`, and can emulate first-party client profiles for Grok Build, Codex and Claude Code. Separately, `LlmMode::Host` delegates inference to an on-device model through `PbLlmRequestCallback`, targeting runtimes such as `llama.cpp` and `llama.rn` on NPU-class hardware. The on-device path is the one that keeps prompts and data on the phone, and it pairs naturally with on-device foundation models that expose tool-calling APIs.
