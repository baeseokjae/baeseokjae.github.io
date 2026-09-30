---
title: "Rutis Review: A Five-Pillar Agent Kernel in Idiomatic Rust, Not a Full 'rust agent framework'"
date: 2026-09-30T01:08:59+00:00
tags:
  - rust agent framework
  - rust ai agent framework
  - rutis
  - rutis rust
  - rutis agent kernel
  - five pillar agent kernel
  - cordis rust port
  - cordis rust implementation
  - rutis-agent
  - rutis-cli
  - rust plugin framework
  - dependency driven reload rust
  - rust fiber lifecycle plugin
  - typed key service registry rust
  - rust event bus four dispatch
  - rust agent framework 2026
  - best rust agent framework
  - rig vs autoagents vs rutis
  - rust agent framework comparison
  - rust plugin hot reload
  - wasm sandbox rust agent
  - aimux rust llm
  - minimal rust coding agent tui
  - rust agent kernel lifecycle
description: "Rutis is a Rust reimplementation of the Cordis five-pillar plugin kernel with a minimal agent on top. Trial the kernel; hold it as an agent framework."
draft: false
cover:
  image: "/images/rutis-five-pillar-agent-kernel-rust.png"
  alt: "Rutis Review: A Five-Pillar Agent Kernel in Idiomatic Rust, Not a Full 'rust agent framework'"
  relative: false
schema: "schema-rutis-five-pillar-agent-kernel-rust"
---

Rutis is a Rust reimplementation of the Cordis five-pillar plugin kernel — plugin, fiber, typed service registry, four-semantics event bus, and dependency-driven reload — with a deliberately minimal coding agent layered on top. If you arrived searching for a "rust agent framework," the honest answer is that rutis is an agent *kernel*: the lifecycle machinery is the product, the agent is a sample.

That distinction decides everything about whether you should try it. Rutis does not compete with Rig or AutoAgents on agent features — no multi-agent orchestration, no tool sandbox, no guardrails, exactly two built-in tools. What it offers instead is loadable, unloadable capability plugins with automatic dependency-driven eviction, backed by an unusually rigorous parity audit against upstream Cordis. The verdict below is **trial for plugin hosts, hold for agent builders**.

## What is rutis, and is it actually a rust agent framework?

No — and the project says so itself. The current README titles the repository "A plugin framework for Rust" and files `rutis-agent` and `rutis-cli` under a "Built with rutis" heading. That is not modesty; it is an accurate description of the crate graph.

The workspace contains 11 crates in the current `arcships/rutis` repository (version 0.5.0, last push 2026-09-29): `rutis`, `rutis-agent`, `rutis-cli`, `rutis-cordis`, `rutis-dsh`, `aimux-llm`, `rutis-sdk`, `rutis-dylib`, `rutis-dylib-launcher`, `rutis-xtask`, and `rutis-interop`, plus example and dylib-fixture members. The kernel crate `rutis` is what you are evaluating. The agent crate is a demonstration that the kernel holds up under a real workload — a coding loop with LLM calls, streaming, tool dispatch, and cancellation.

The origin story matters for context. The project started at `eric8810/rutis` on 2026-08-18, reached 243 commits from a single contributor in roughly five weeks, and then moved to the `arcships` organization on 2026-09-22. The crates.io `repository` field was repointed alongside the move. The arcships org is small — 10 public repos created 2026-04-01 — but includes `aimux` (195 stars, the unified LLM access layer rutis consumes) and `dimcode` (37 stars, a multi-model CLI coding agent).

So what is the actual target user? Hysen Labs, the only independent analyst to cover the project, put it precisely: "Rust developers building a host process that loads and unloads capability plugins at runtime, not someone who wants an agent binary." Treat that as the acceptance criterion.

## What are the five pillars of rutis?

The Cordis paradigm rutis ports rests on five concepts. Each maps to a concrete Rust mechanism here.

**Plugin as the unit of assembly.** A plugin's `apply()` function provides services, registers listeners, and registers cleanup — exactly once. There is no separate "initialize then register" dance; assembly and teardown are declared together.

**Fiber as lifecycle container.** Every plugin instance runs inside a fiber with a six-state machine: Pending, Loading, Active, Failed, Unloading, Disposed. Fibers gate on dependencies, cascade their unload to dependents, and run exactly-once LIFO cleanup with atomic rollback if a plugin half-registered its resources before failing. This is the mechanism that makes everything else work.

**Service as typed registry.** Services are identified by a `TypeKey` — by type, not by string name. The consequences are that a service lookup cannot silently return the wrong thing at runtime, and qualified keys let you hold multiple instances of one interface (two LLM providers, distinguished, both typed).

**Event bus with four dispatch semantics.** Rutis exposes `emit` (ordered per key), `parallel` (concurrent fan-out), `serial` (first-value short-circuit), and `waterfall` (middleware chain with `next()`). Upstream Cordis documents five modes including `bail`, which rutis folded into `serial`'s first-value short-circuit rather than exposing separately.

**Dependency-driven reload.** This is the headline capability. When a provider unloads, its consumers are evicted and reloaded automatically, without application code touching them. No code path in your host process says "now restart the LLM plugin." The kernel derives that from the dependency graph it already owns.

The trade is explicit and you should read it as the price of the product, not a footnote. Hysen Labs stated it well: "your plugins have to declare dependencies in the kernel's terms, and the kernel owns their lifetime." You are handing over your start/stop schedule. In exchange, reload correctness is not your problem anymore.

| Pillar | Rust mechanism | What it buys you | What it costs |
|---|---|---|---|
| Plugin | `apply()` provides services, listeners, cleanup once | Assembly and teardown declared together | Everything must be a plugin-shaped unit |
| Fiber | Six-state machine + dependency gating | Exactly-once LIFO cleanup, atomic rollback | Lifetime owned by the kernel |
| Service | `TypeKey` typed registry, isolate scopes, qualified keys | Compile-time-safe lookup; multiple instances per interface | Registrations go through the kernel's registry |
| Event bus | `emit` / `parallel` / `serial` / `waterfall` | Dispatch semantics are explicit and reviewable | Four modes to learn; `bail` folded into `serial` |
| Reload | Dependency graph drives eviction + reload | Provider swap needs zero application code | Dependency declarations must be authored in kernel terms |

## Why is the kernel the product? The fiber state machine and exactly-once cleanup

Most frameworks in the Rust agent space treat lifecycle as an afterthought — you construct a struct, you drop it, `Drop` runs, done. That works until the thing you are dropping made partial progress: opened a connection, registered a handler, spawned a task, then failed on step four of six.

Rutis makes the failure path a first-class state. A fiber that fails during loading transitions to Failed, and the resources it already registered are rolled back rather than leaked. A fiber that unloads runs its cleanup handlers in strict LIFO order, exactly once. Dependents cascade.

There is one deliberate divergence from upstream Cordis worth flagging, because it is a design choice rather than a port artifact: rutis runs cross-effect cleanup **strictly serially in LIFO order**, where upstream Cordis runs those effects concurrently. That is a determinism-for-throughput trade. Serial LIFO cleanup gives you a reproducible teardown order you can reason about and test; concurrent cleanup gives you faster shutdown with less predictable interleaving. For a kernel whose selling point is lifecycle correctness, choosing determinism is defensible — but it *is* a divergence, and anyone porting Cordis plugins should know it.

A second divergence is more structural. Per-key `emit` ordering had to be rebuilt explicitly in rutis because JavaScript's object key ordering — the property Cordis relies on — has no Rust equivalent. This is the kind of detail that tells you whether a port is real work or a transliteration. It is real work here.

## How faithful is the Cordis port? The spec parity ruling (96 reviewed, 58 locked, 38 refused)

This is the strongest and most verifiable thing in the entire repository, and it is completely invisible from the star count.

The rutis team read all 96 upstream Cordis spec cases line by line and produced a ruling table with three outcomes: 58 language-agnostic invariants locked by automated parity tests (31 full, 27 partial), and 38 explicitly **not ported**, each with a declared reason.

The 38 refusals are all JavaScript-specific mechanisms that have no meaningful Rust analogue: Proxy, string event names, `internal/*` internals, sync bail, traceable/caller-shadow, `Context.filter`, `intercept`, async generator effects, and update-config semantics. Publishing a non-goals table with one reason per refusal is unusual. Almost no young open-source project does it — most leave you to discover the gaps from a failing test.

| Parity outcome | Count | Meaning for a Rust adopter |
|---|---|---|
| Reviewed upstream specs | 96 | The full Cordis behavioural surface was read, not sampled |
| Invariants locked by parity tests | 58 | 31 full + 27 partial; regression-guarded automatically |
| Explicitly not ported | 38 | JS-only mechanisms (Proxy, string event names, caller-shadow, async generator effects) each with a reason |
| Deliberate strengthenings | 2 | Serial LIFO cross-effect cleanup; per-key emit ordering rebuilt explicitly |

The kernel additionally carries 141 contract and differential tests per the current README. Note the discrepancy with third-party coverage: Hysen Labs reports 115, because its editorial is dated 2026-08-26 and its data snapshot predates the 0.3.0 and 0.5.0 releases. The 115 figure is stale, not contradictory — but it is a useful data point about how fast this project moves relative to the coverage of it.

## What does the rutis agent framework actually include?

Strip away the framing and the shipped agent is six elements:

**LLM backend.** An `Arc<dyn LanguageModel>` service obtained from `aimux`, consumed rather than re-declared. Rutis-agent writes no HTTP clients, no auth, no streaming protocol of its own — that all lives in `aimux-core` / `aimux-providers`.

**ToolRegistry as a plugin.** Tools are registered as a plugin, which means they participate in the same lifecycle as everything else.

**Session.** In-memory, ordered messages, and deliberately **not** a plugin. The design doc is explicit: the session is the single source of truth for the loop and lives in the driver's fiber. That is a considered refusal, not an oversight — making the session reloadable would make it ambiguous.

**Agent loop as a driver plugin** implementing the `Agent` interface.

**Event observation** via `agent/*` broadcasts plus waterfalls at `agent/pre-step`, `agent/request`, `tools/pre-execute`, `execute`, and `post-execute`. If you want to intercept or instrument the loop, these are the seams.

**Minimal-mode tools:** `bash` and `replace_text`. Two tools.

The TUI is `rutui` on ratatui 0.29 / crossterm 0.28, with streaming output, tool-call visibility, and Esc-to-cancel. That is a real, usable terminal harness — it is just a small one.

If you want a fully-featured coding agent from the same org, look at `dimcode` (37 stars) or the incumbent CLIs. Rutis-agent's own README calls it "a minimal coding agent sample," which is the correct expectation to hold.

## What do you get in the box, and how well is it tested?

Verification is where this project punches above its weight class. There are three layers, and they are honest about their own limits:

**Unit layer.** `ScriptedLlm` implements the real `LanguageModel` trait — including `do_stream` — so loop logic, multi-turn history, `max_steps`, cancellation, and failure feedback are all tested without a network.

**Integration layer.** `aimux`'s `MockReplayModel` does record-and-replay, covering dual gating, the unload-llm-triggers-evict-and-reload path, fiber unload cancelling in-flight work, and event observation.

**Real end-to-end layer.** Marked `#[ignore]`, requires `DEEPSEEK_API_KEY`, and **does not run in CI**.

That last sentence is the one an adopter has to sit with. The mechanism most worth trusting — a real provider round trip through the real loop — is the one that is not continuously verified. It is not a scandal; it is a normal resource constraint for a single-maintainer project. But "the reload works" and "the loop works against a real model" are verified at different levels of rigour, and the gap is exactly where integration bugs live.

## What do rutis's own benchmarks show, and which benchmark suite is it missing from?

Rutis publishes its own event-dispatch microbenchmark, and the document is unusually careful.

The measured costs in nanoseconds per operation, for sync dispatch by listener count, run 412.8 (0 listeners) / 475.0 (1) / 971.8 (8) / 4345.7 (64). Sync waterfall dispatch runs 420.5 / 543.8 / 1085.2 / 5248.2 across the same listener counts, with a keyed no-listener waterfall at 458.6 ns/op. Prefix-pattern serial dispatch runs 94.1 (0 prefixes) / 568.7 (1) / 563.2 (8) / 702.6 (64) / 2309.9 (1024). Comparing the 0.3.0 line to the 0.4.0 development line on exact-key dispatch: 55.2 → 58.5 ns/op at zero listeners (+5.9%), 112.6 → 97.8 at one (−13.1%), 273.3 → 262.7 at eight (−3.9%), 1589.7 → 1605.5 at 64 (+1.0%).

Now the caveats, which the authors attach themselves. The benchmark ran on an Intel Core Ultra X7 358H with rustc 1.98.1, release build, Tokio limited to two worker threads, `taskset` to CPU 0, **no fixed CPU frequency, and no confidence intervals**. The document states outright that nanosecond differences must not be read as cross-machine conclusions.

Take them at their word. The +5.9% regression on the empty dispatch path is reported, not buried — that is the behaviour of a team that would rather be accurate than win an argument. And do not repurpose these numbers as a competitive claim against Rig or AutoAgents, because they measure a different thing entirely: dispatch cost, not agent throughput, memory, or reload latency.

On that last point, the honest gap. The widely cited Rust-vs-Python agent benchmark suite from January 2026 — 50 requests, 10 concurrent, gpt-5.1, identical hardware — includes Rig, AutoAgents, LangChain, LangGraph, LlamaIndex, PydanticAI, and GraphBit. **Rutis is not in it.** The headline structural results from that suite belong to other projects: Rust frameworks peak at roughly 1.0–1.1 GB against every Python framework exceeding 4.7 GB (AutoAgents 1,046 MB and Rig 1,019 MB versus LangChain 5,706 MB, LangGraph 5,570 MB, PydanticAI 4,875 MB, LlamaIndex 4,860 MB), extrapolating to ~51 GB versus ~279 GB at 50 concurrent instances.

Cold start in that same suite: AutoAgents and Rig at ~4 ms against 54–63 ms for LlamaIndex, PydanticAI, LangChain, and LangGraph, and 138 ms for GraphBit. Latency clusters tightly between 5.7 s and 7.0 s across all frameworks because the LLM network round trip dominates; framework overhead only becomes visible at P95, where LangGraph's 16,891 ms compares with AutoAgents' 9,652 ms.

Two things follow. First, "Rust is 5x lighter" is a true and well-evidenced claim — about Rig and AutoAgents, not about rutis. Second, and more importantly, that suite does not measure plugin lifecycle, reload, or eviction cost at all, which is precisely rutis's claim to fame. Rutis has no end-to-end agent throughput or memory benchmark. Neither does anyone measure what rutis is actually for.

## rutis vs Rig vs AutoAgents vs Cordis: which one should you use?

The keyword "rust agent framework" pulls four projects into one comparison, and they are not substitutes.

| Project | Stars | Crate downloads | Licence | What it is for | Plugin lifecycle |
|---|---|---|---|---|---|
| rutis | 21 (old repo) / 4 (current) | 197 lifetime (`rutis`), 54 (`rutis-agent`), 34 (`rutis-cli`) | MIT | Host processes that load/unload capability plugins | Yes — six-state fibers, dependency-driven reload |
| Cordis | 8,896 | n/a (TypeScript/npm) | MIT | The mature paradigm rutis ports; vendored in DeepSeek Harness | Yes — the original |
| Rig | 8,766 | 3,115,669 lifetime / 1,684,403 recent (`rig-core` v0.42.0) | Reported inconsistently (MIT per GitHub API; Apache-2.0 in one comparison table) | Building LLM apps and agents in Rust, start to finish | No |
| AutoAgents | 761 | 15,196 lifetime (`autoagents` v0.4.0) | Apache-2.0 | Multi-agent systems with actor-model coordination and WASM sandboxing | No |

Cordis is the mature option and the reason this paradigm is production-relevant rather than academic: its primer documents it as the plugin framework vendored inside DeepSeek Harness, with 8,896 stars, 554 forks, created 2022-05-17, last push 2026-09-08. Any decision to adopt rutis is really a decision to adopt Cordis semantics in Rust. If your team writes TypeScript, the case for the port is weak.

Rig is the incumbent answer to "I want to build an agent in Rust," and it needs no kernel. Rig.rs positions it as one composable trait system spanning completions, tools, streaming, RAG, and multi-agent workflows, with 20+ providers behind one API, typed tools and structured output, and mock models plus VCR cassette tests for determinism. Its scale — 3.1 million lifetime `rig-core` downloads against rutis's 197 — is not a popularity contest you can wave away. It is a statement about how many people had a problem Rig solved.

AutoAgents is what a Rust agent framework looks like when the framework, not the kernel, is the product: Ractor (Erlang/OTP-style actor model) for coordination, typed pub/sub, Basic and ReAct executors, derive macros for tools and structured outputs, sliding-window memory with pluggable backends, sandboxed WASM tool execution with fuel metering, and OpenTelemetry tracing. Its own claims in the benchmark article are 25% better latency than average Python frameworks and 43.7% better than LangGraph.

Rutis has none of that. It has lifecycle. Rig and AutoAgents have lifecycle as an implementation detail — or not at all. Rutis makes it the interface, and that is the only axis on which it competes.

## What does adopting a 0.x kernel cost, and how is rutis licensed?

Rutis is MIT throughout, inherited from Cordis (authored by Shigma). Commercial use, closed-source use, and redistribution are all permitted with attribution. There is no paid tier, no hosted service, no telemetry, and no cloud dependency. Rutis-agent and rutis-cli consume `aimux-core` / `aimux-providers` from crates.io at 0.3.0, so no sibling checkout is required just to build.

The real cost of adoption is not licence fees. It is API churn. The published crate versions tell the story directly:

| Crate | Release history | Downloads |
|---|---|---|
| `rutis` (kernel) | 0.1.0 (2026-08-19) → 0.2.0–0.2.5 (2026-09-22) → 0.3.0 (2026-09-24) → 0.5.0 (2026-09-28) | 197 lifetime; 0.5.0 = 28 |
| `rutis-agent` | 0.1.0 (2026-08-19) → 0.2.0 (2026-09-22) | 54 lifetime; 0.2.0 = 22 |
| `rutis-cli` | 0.1.0 (2026-08-19) → 0.2.0 (2026-09-22) | 34 lifetime; 0.2.0 = 17 |
| `rutis-cordis`, `rutis-dsh`, `aimux-llm` | Not published — HTTP 404 on crates.io | Git-only |

Nine versions of the kernel in six weeks — 0.1.0, 0.2.0 through 0.2.5, 0.3.0, and 0.5.0, with 0.4.0 never released separately. Kernel 0.5.0 is 142,358 bytes, declares `rust-version` 1.85 on edition 2021, and builds on docs.rs.

Two practical consequences. First, if a component you need is one of the three unpublished crates, you are building from a git dependency, and you own that decision forever. Second, and easy to miss: the published `rutis-agent` 0.2.0 depends on `rutis ^0.2.0` plus sibling `rutui-*` path crates, while the current `main` workspace is 0.5.0 and uses `rutui` 0.1.0 from crates.io. **The published agent is older than the repository.** The crates.io `rutis-cli` 0.2.0 dependency list is just aimux-core, aimux-providers, rutis, rutis-agent, serde_json, and tokio — and the TUI actually lives inside `rutis-agent`, not the CLI. Pin exactly, or build from git and accept drift.

In fairness: the repository ships migration guides for both 0.1→0.2 and 0.3→0.5. Shipping migration guides through an API break is unusual honesty for a project this young, and it materially lowers the cost of the churn. It does not eliminate it.

## How do you get started with rutis?

The Rust version requirement is 1.85 with edition 2021 on the kernel crate. For a first evaluation, do not start by wiring up a provider — the point of the first hour is to see the lifecycle, not the model.

**Run the offline demo first.** The CLI supports `--scripted` and a `tui_scripted` mode that exercise the full loop without any API key. That means you can inspect the agent loop, the event waterfalls, and the tool dispatch with zero credentials and zero network. Most frameworks cannot be evaluated without a key; this one can.

**Then wire a real backend.** The LLM comes through `aimux`, which is why provider concerns are absent from rutis-agent. A local model works: `AIMUX_PROVIDER=ollama AIMUX_MODEL=qwen3:8b`. Rutis delegates all provider handling to `aimux`, whose repo description claims 325 providers while both rutis READMEs (old and current) say 329 — that discrepancy is unresolved in the sources, so treat "hundreds of providers backed by aimux" as the accurate claim and verify your specific provider.

**If you hack on a sibling crate locally**, use an uncommitted `[patch]` at the workspace root; the README documents this explicitly, and it is the intended workflow rather than a workaround.

**Watch the version you pin.** Given that the repository is at 0.5.0 while the published agent trails at 0.2.0, `cargo add rutis rutis-agent rutis-cli` will build something different from what the README describes. Start from git `main` if you are evaluating current behaviour; pin published crates only if you need reproducible builds and are content with older agent code.

## What are the risks and limitations of rutis?

Everything below is either sourced from the project's own documentation or from absence of evidence. Read it as the other half of the review.

**Governance and bus factor.** One contributor, 243 commits, five weeks. The repo moved organizations mid-flight from `eric8810/rutis` to `arcships/rutis` on 2026-09-22, and the crates.io repository field was repointed. That is a normal evolution for a young project, but it means any URL, CI config, or vendored dependency pointing at the old path is now a liability.

**Adoption is unproven.** 21 stars on the origin repo, 4 on the current org repo, 197 lifetime kernel downloads, 54 for the agent crate. There is no Hacker News thread for rutis at all — an Algolia story search returns only rotisserie, rUTI, and Ruby-shell results. Hysen Labs' analysis is the sole non-author coverage found, and it already describes superseded facts: it reports 115 contract tests (the README now says 141) and the 2026-08-19 push as latest.

**Naming is an active discovery tax.** The crate name collides with the medical abbreviation rUTI in search results; there is an unrelated `routis` (a local routing/audit CLI) and a `rudis` (mini Redis in Rust) on crates.io. For a project whose pitch is "adopt this kernel," discoverability sits below the threshold at which evidence gets read.

**Feature gaps, stated plainly.** No multi-agent orchestration. No tool sandbox — AutoAgents has WASM sandboxing with fuel metering; rutis has `bash` and `replace_text` running as your process. No guardrails. No documented retry or rollback policy for a *failed reload* — the kernel handles half-registered resources atomically, but the operational story for "reload failed on a live system" is not written down. Real-provider tests excluded from CI behind `#[ignore]`. Two built-in tools.

**The ambitious parts are unfinished.** The dylib SDK design (`design-dylib-sdk-2026-09-24.md`) promises first-party plugins loadable without republishing the host, shared Rust types with no serialization, and version rejection before load. The protocol-plugins work (`design-protocol-plugins-2026-09-25.md`) proposes mounting TypeScript Cordis plugins and Rust rutis plugins into one object space through proxies. The protocol work is a design document with **no implementation**. Treat both as roadmap, not feature list.

**The dual-core doctrine is a promise you can hold them to.** The written strategy is that rutis is the Rust spine and dsh (TypeScript) is the laboratory — "TS is the lab, Rust graduates" — with explicit rustification criteria (semantics converged, mechanism not wording, distribution-sensitive, not npm-bound, on a trust boundary) and an explicit commitment that prompt *assembly* mechanism rustifies while prompt *content* never does. That is a testable rule rather than a slogan, which is more than most projects offer. It is still a rule about future work.

**No independent performance evidence.** Self-published microbenchmarks with self-declared caveats, and absence from the one widely cited suite. That is the complete state of the performance case.

## Who should use rutis, and who should not

**Trial it if** you are building a host process in Rust that must load and unload capability plugins at runtime, and dependency-driven eviction is genuinely part of your requirements. The kernel's lifecycle semantics — six-state fibers, exactly-once LIFO cleanup, atomic rollback of half-registered resources, cascading unload — are the most carefully specified thing in the Rust plugin space, and the 58 locked parity invariants mean you can trust them. The offline `--scripted` demo lets you validate that in an afternoon.

**Hold — do not adopt yet — if** any of these are true: you need the API to be stable (nine releases in six weeks says no); you need every crate you depend on published to crates.io (three are git-only); you need an SLA or a support contract (one maintainer); you need real-provider behaviour continuously verified (it is `#[ignore]`d).

**Skip it entirely if** your actual requirement is "build an agent in Rust." Use Rig. It is in the millions of downloads, it is actively maintained with a last push of 2026-09-29, and it needs no kernel. If you need multi-agent orchestration or sandboxed tool execution, use AutoAgents. If you are a TypeScript shop and want this paradigm, use Cordis directly — it is 8,896 stars and four years old to rutis's 21 stars and five weeks.

The single most useful reframing the search results will never give you: the phrase "rust agent framework" describes what rutis does *not* primarily do. It is a plugin kernel with an agent-shaped demonstration, and the demonstration is deliberately minimal because its job is to prove the kernel, not to be your coding agent. Judge it as a kernel and it is promising but young. Judge it as an agent framework and it is not one.

## FAQ

**Is rutis free to use?**
Yes. Rutis is MIT-licensed throughout, with the licence inherited from Cordis (authored by Shigma). That permits commercial use, closed-source use, modification, and redistribution with attribution. There is no paid tier, no hosted offering, and no telemetry.

**Does rutis need an API key to run?**
No. The CLI supports `--scripted` and a `tui_scripted` mode that run the full agent loop offline with no credentials — which is how you should evaluate the kernel. A real backend requires a key (or a local model via `AIMUX_PROVIDER=ollama AIMUX_MODEL=qwen3:8b`), and the `#[ignore]`d end-to-end tests require `DEEPSEEK_API_KEY` but are excluded from CI.

**What Rust version does rutis require?**
The kernel crate 0.5.0 declares `rust-version` 1.85 on edition 2021. The published package is 142,358 bytes and docs.rs builds it successfully.

**Does rutis work with local models?**
Yes. All provider handling is delegated to `aimux`, the unified LLM access layer from the same organization, so rutis-agent contains no HTTP clients, auth code, or streaming protocol of its own. Setting `AIMUX_PROVIDER=ollama` with something like `AIMUX_MODEL=qwen3:8b` runs against a local server. Note that `aimux`'s repository description says 325 providers while both rutis READMEs say 329 — verify your specific provider rather than relying on the headline number.

**Is rutis the same thing as Cordis?**
No. Cordis is the TypeScript framework the paradigm comes from — 8,896 stars, created 2022, and documented as the plugin framework vendored inside DeepSeek Harness. Rutis is an idiomatic Rust implementation of that paradigm, not a translation. It reviewed 96 upstream spec cases and locked 58 language-agnostic invariants in automated parity tests, explicitly refusing the other 38 for JavaScript-specific reasons such as Proxy, string event names, caller-shadow, and async generator effects. It also diverges deliberately in two places: cross-effect cleanup runs strictly serial LIFO where Cordis runs effects concurrently, and per-key emit ordering was rebuilt from scratch because JavaScript object key ordering does not exist in Rust.
