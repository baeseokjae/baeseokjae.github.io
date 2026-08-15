---
title: "DeepSeek Harness Terminal UI: dsh-tianshu-tui Review (2026)"
date: 2026-08-15T16:01:21+00:00
tags:
  - deepseek harness
  - terminal ui
  - dsh tui
  - dsh-tianshu-tui
  - ai coding agent
  - deepseek v4
description: "dsh-tianshu-tui turns DeepSeek Harness into a full terminal workspace. Review of features, install, prefix-cache savings, and how it compares to other dsh TUIs."
draft: false
cover:
  image: "/images/dsh-tianshu-tui-2026.png"
  alt: "DeepSeek Harness Terminal UI: dsh-tianshu-tui Review"
  relative: false
schema: "schema-dsh-tianshu-tui-2026"
---

The DeepSeek Harness terminal UI (dsh-tianshu-tui) is an official plugin that turns the DeepSeek Harness CLI into a full interactive terminal workspace, with live rendering, session restore, image support, and a TDD-driven evidence gate. It is a pure display layer that derives all agent state from the session event stream, so it adds no prompts, tools, or context of its own. This review covers what it does, how to install it, and how it compares to the other DeepSeek Harness TUIs.

## What is DeepSeek Harness and why it needs a TUI

DeepSeek Harness (deepseek-ai/deepseek-harness) is the official open-source agent runtime from DeepSeek, and it is built around a simple but powerful philosophy: **"Everything is a Plugin."** As of August 15, 2026, the repository holds 111,829 stars and 10,833 forks, making it one of the most-watched agent frameworks on GitHub. The harness is not a monolithic IDE; it is a modular runtime where prompts, tools, context providers, and even the user interface are all swappable plugins.

That modularity is exactly why a terminal UI matters. The stock `dsh` CLI is a capable but bare command-line interface. When you are running long agent sessions, reviewing tool calls, steering mid-turn, and inspecting reasoning traces, a plain prompt loop gets cramped. A TUI — a terminal user interface — gives you a full-screen workspace without leaving the terminal. It keeps the zero-chrome, scriptable, git-native workflow that terminal users prefer, while adding the visual density of an IDE.

The ecosystem has responded with at least five community TUI implementations. The most prominent is **dsh-tianshu-tui**, an official plugin by huiliyi37 that evolved from the Tianshu-Tui rendering core. It is the subject of this review.

## dsh-tianshu-tui at a glance — the plugin that turns dsh into a terminal workspace

dsh-tianshu-tui is an npm package (`@huiliyi37/dsh-tianshu-tui`, Apache-2.0) that installs as a profile plugin for the official DeepSeek Harness CLI. It was created on August 13, 2026, and already has 158 stars and 6 forks, with the latest npm release at `0.1.2-rc.7` (August 15, 2026). The project co-evolved with the harness itself, accumulating 250+ commits between August 10 and August 13 on the August 9 baseline snapshot.

The key architectural decision is that the TUI is a **pure display layer**. It registers no prompts, no tools, and no context. Every piece of agent state — reasoning, tool calls, replies, subagent lifecycles — is derived from the session event stream. This means the TUI cannot interfere with the agent's behavior; it only renders what the harness already produces. That is a deliberate contrast to monolithic AI IDEs, where the interface and the agent logic are tightly coupled.

The result is a full in-terminal workspace with:

- Live rendering of the agent's activity
- Session restore across restarts
- `/fork` and `/rewind` for branching and replaying sessions
- `/export` to Markdown
- `/steer` for mid-turn steering

## Installation and setup

Installing dsh-tianshu-tui requires three things: the official CLI, a recent Node.js, and pnpm.

**Requirements:**

| Requirement | Version |
|---|---|
| Official CLI | `@deepseek-ai/dsh` 0.1.0-rc.6 |
| Node.js | `^22.19` or `>=24` |
| Package manager | pnpm on PATH |

The install command is a single line:

```bash
npx -y @deepseek-ai/dsh plugin --profile tui add @huiliyi37/dsh-tianshu-tui
```

This adds the plugin to the `tui` profile. You then launch the TUI through that profile.

**Common pitfalls.** The review notes two recurring install failures. The first is `ERR_FS_EISDIR`, which typically appears when the plugin path is misconfigured or a stale directory is being treated as a file. The second is a "stale dsh" problem, where an older CLI version is still on PATH and the plugin refuses to load. Both are resolved by pinning the official CLI to exactly `0.1.0-rc.6` and ensuring pnpm is reachable. Because the plugin co-evolves rapidly with the harness, keeping the CLI version in sync matters more than with a stable tool.

## Core features — session workspace, images, input, and reasoning

Once running, dsh-tianshu-tui provides a dense but navigable interface. The core features fall into four groups.

**Session workspace.** The TUI supports live rendering, session restore, `/fork`, `/rewind`, and `/export` to Markdown. You can branch a session to try a different approach, rewind to an earlier checkpoint, and export the full transcript for sharing or documentation. `/steer` lets you redirect the agent mid-turn without killing the run.

**End-to-end images.** The plugin handles images from clipboard to inline render. You can paste an image from the clipboard, and it renders inline using the kitty or iTerm2 graphics protocol. The standout feature is the **vision bridge**: when the main model cannot see images, the TUI auto-detects an auxiliary vision model and routes image understanding through it, with graceful degradation if none is available. This is a practical solution to the common problem of a text-only main model being asked to reason about a screenshot.

**Complete input surface.** The input layer is grok-style: a slash menu for commands, `@`-path tab completion, bracketed paste support, optional vim keys, an external editor via Ctrl+E, and history search via Ctrl+F. For heavy terminal users, the vim keybindings and external editor integration make long sessions far more comfortable.

**Reasoning visualization.** The think channel streams live, then folds into compact rows to keep the screen readable. Ctrl+O expands a reasoning block inline when you want to inspect the model's chain of thought. This is a meaningful improvement over a plain chat UI, where reasoning either floods the screen or is hidden entirely.

## Harness-engineering differentiators — TDD evidence gate, memory, code intelligence

Beyond rendering, dsh-tianshu-tui exposes several harness-engineering features that set it apart from a plain chat interface.

**TDD-driven workflow and evidence gate.** The plugin supports a RED-first verification workflow: write a failing test, watch it fail, then implement until it passes. The evidence gate is an obligation state machine that tracks what must be verified before a task is considered done. If verification fails, the run is routed to failure handling rather than silently continuing. This is a real differentiator from chat UIs, which have no notion of "prove it works."

**Memory and cross-session recall.** The `/memory` command opens a project memory browser, and the underlying Tianshu-Tui core uses a Stigmergy (pheromone) self-decaying memory model. This shifts the tool from a stateless chat to a persistent agent partner that remembers context across sessions.

**Code intelligence and git tools.** The plugin integrates code intelligence retrieval and git tooling, so you can inspect repository context and manage version control from within the TUI.

**Personalized harness integration.** A `/doctor` command runs diagnostics, `/btw` spawns a background agent, and `/model` plus `/effort` let you hot-switch models and effort levels mid-session.

## The prefix-cache advantage — 95-99% hit rate and what it saves you

One of the most compelling technical details is the prefix-cache engineering in the Tianshu-Tui rendering core. In long sessions, the core reports a **steady-state prefix-cache hit rate of 95-99%** on DeepSeek V4.

What does that mean in practice? Prefix caching means the model provider does not recompute the shared prefix of a conversation on every request. When the hit rate is high, the cost and latency of each turn drop dramatically, because only the new tokens need to be processed. In a long agent session where the conversation history grows large, a 95-99% hit rate is the difference between a responsive, cheap workflow and one that degrades into slow, expensive recomputation.

This is a hidden cost lever that most TUI reviews miss. The interface itself does not save tokens, but by keeping sessions long-lived and well-structured, it maximizes the prefix-cache benefit. For teams running DeepSeek V4 at scale, this is a real operational advantage.

## How it compares to other DeepSeek Harness TUIs

dsh-tianshu-tui is not the only TUI in the ecosystem. Here is how it stacks up against the main alternatives.

| TUI | Language / stack | Stars | Key strength |
|---|---|---|---|
| **dsh-tianshu-tui** | TypeScript (Tianshu-Tui core) | 158 | Pure display layer, vision bridge, TDD evidence gate, 95-99% prefix-cache |
| **Tianshu-Tui** | TypeScript, Apache-2.0 | 229 | Full standalone runtime, CVM + Stigmergy memory, 13,000+ tests |
| **openma-ai/deepseek-harness-tui** | Rust / ratatui, MIT | 25 | Up to 8 images per prompt, JSON-RPC runtime, token/cache metrics |
| **gxinxing/deepseek-harness-tui** | JavaScript (Ink) | 7 | Thin ~800-line UI, zero-chrome, OSC 11 theme detection |
| **oh-dsh** | TypeScript, MIT | 188 | Desktop + Web + TUI unified, plugin marketplace, Git Review |

**Tianshu-Tui** is the rendering core that dsh-tianshu-tui evolved from. It is a full standalone terminal coding agent runtime with 229 stars, 13,000+ passing tests, and the Stigmergy memory model. If you want the complete runtime rather than a plugin for the official harness, this is the base.

**openma-ai/deepseek-harness-tui** is the Rust/ratatui option. It is lighter on features but strong on image handling (up to 8 images per prompt) and exposes token and cache metrics. It runs either as a dsh profile plugin or directly against the SDK JSON-RPC runtime.

**gxinxing/deepseek-harness-tui** is deliberately minimal — about 800 lines of Ink (React for terminals). It is a thin, readable UI that folds tool calls into cells and derives its theme from your terminal via an OSC 11 probe. It is the choice for users who want the least chrome possible.

**oh-dsh** takes a different approach: it packages the DSH runtime into Desktop, Web, and TUI distributions with a shared plugin marketplace and a Git Review sidebar. If you want the same sessions across a desktop app, a browser, and a terminal, oh-dsh is the unified option.

## Who should use it and who should wait

dsh-tianshu-tui is best for developers who already live in the terminal and run DeepSeek Harness for real agent work — especially those doing TDD, long multi-turn sessions, or image-heavy tasks where the vision bridge matters. The prefix-cache benefit and the evidence gate make it a strong fit for teams that care about cost and verifiability.

You might wait if you prefer a minimal UI (gxinxing's Ink plugin), need a full standalone runtime (Tianshu-Tui), want multi-form Desktop/Web/TUI access (oh-dsh), or need the Rust/ratatui stack with heavy image staging (openma). Because the plugin is young and co-evolves rapidly with the harness, you should also be comfortable with frequent updates and the CLI version pin.

## Verdict and final thoughts

dsh-tianshu-tui is a well-engineered, feature-complete terminal UI for DeepSeek Harness. Its decision to be a pure display layer is the right one: it stays out of the agent's way while giving you a dense, navigable workspace. The vision bridge, TDD evidence gate, memory browser, and 95-99% prefix-cache hit rate are genuine differentiators, not cosmetic additions.

The main caveats are the young age of the project and the install friction around the CLI version pin. But for terminal-native DeepSeek Harness users, dsh-tianshu-tui is currently the most complete and polished option in the ecosystem. If you run dsh for serious agent work, it is worth installing today.

## FAQ

**What is the DeepSeek Harness terminal UI?**
It is a TUI plugin (dsh-tianshu-tui) that turns the DeepSeek Harness CLI into a full interactive terminal workspace with live rendering, session restore, image support, and a TDD evidence gate.

**How do I install dsh-tianshu-tui?**
Run `npx -y @deepseek-ai/dsh plugin --profile tui add @huiliyi37/dsh-tianshu-tui`. You need the official CLI `@deepseek-ai/dsh` 0.1.0-rc.6, Node.js `^22.19` or `>=24`, and pnpm on PATH.

**Does dsh-tianshu-tui change how the agent behaves?**
No. It is a pure display layer that derives all state from the session event stream and registers no prompts, tools, or context, so it cannot alter agent behavior.

**What is the vision bridge?**
When the main model cannot see images, the TUI auto-detects an auxiliary vision model and routes image understanding through it, with graceful degradation if none is available.

**What is the prefix-cache hit rate and why does it matter?**
The Tianshu-Tui core reports a 95-99% steady-state prefix-cache hit rate on DeepSeek V4 in long sessions, which cuts token cost and latency by avoiding recomputation of the shared conversation prefix.
