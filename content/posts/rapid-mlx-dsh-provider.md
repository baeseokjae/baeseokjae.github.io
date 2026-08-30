---
title: "Rapid-MLX DSH Provider: Native Apple Silicon Inference for the DeepSeek Harness"
date: 2026-08-30T13:04:27+00:00
tags:
  - mlx
  - deepseek-harness
  - apple-silicon
  - local-llm
  - rapid-mlx
  - dsh-provider
  - llm-inference
  - mlx-lm
description: "Connect the DeepSeek Harness to Rapid-MLX on Apple Silicon with a native dsh provider plugin that auto-reads model facts, fixes reasoning truth, and does memory-aware compaction."
draft: false
cover:
  image: "/images/rapid-mlx-dsh-provider.png"
  alt: "Rapid-MLX DSH Provider: Native Apple Silicon Inference for the DeepSeek Harness"
  relative: false
schema: "schema-rapid-mlx-dsh-provider"
---

The Rapid-MLX DSH Provider is a native npm plugin for the DeepSeek Harness (dsh) that lets the agent read its model configuration straight from a running Rapid-MLX server's `/v1/models` endpoint instead of hand-written `settings.yaml`. Instead of copying context windows, reasoning efforts, and `max_model_len` values by hand — and re-copying them every time you switch models — the provider serves those facts directly from Rapid-MLX's JSON schema, keeps reasoning control truthful, and compacts the context at the real memory limit of your Apple Silicon machine.

## What is the Rapid-MLX DSH Provider and why does DeepSeek Harness need it

DeepSeek Harness is a 204K-star LLM-agent harness built on a strict philosophy: "Everything is a Plugin." That philosophy is what makes a separate provider necessary — and useful. When you want to run a local model inside dsh, you do not patch the harness. You write a conformant `LlmAdapter` plugin that tells dsh the name of the model, the size of its effective context, and how to route reasoning and tool calls.

The Rapid-MLX DSH Provider (`@raullenchai/dsh-provider`) is exactly that adapter, written natively for [Rapid-MLX](https://github.com/raullenchai/Rapid-MLX), the 3,584-star "fastest local AI engine for Apple Silicon." The pairing removes the most error-prone step in local-agent setup: hand-maintaining per-model config. Without the provider, every model swap means opening `settings.yaml` and hand-writing `contextWindow`, `reasoningEfforts`, and `max_model_len`. With it, dsh asks the server what model facts are real, and the server answers from a single source of truth.

## Before you begin: requirements

The provider is small, but the surrounding stack is specific. Before you install anything, confirm you have each of these:

- **Node.js >= 22.15.** This is not optional. dsh imports Node's Zstd stream API without declaring it in its own dependency tree, so an older Node runtime will fail at import time rather than at boot.
- **A running Rapid-MLX server.** The provider reads model facts from the server's `/v1/models` endpoint, so Rapid-MLX must be up and listening before dsh starts.
- **Apple Silicon.** Rapid-MLX is an Apple-metal inference engine, so an M-series Mac (M1, M2, M3, M4 — including Ultra variants) is implied. The upstream verification ran on an M3 Ultra.
- **A model already pulled into Rapid-MLX.** Context and reasoning facts are per-model, so at least one model must be stored locally before the first provider run.

These four are the whole setup surface. There is no separate compiler, no build step, and no additional Python environment, which distinguishes this provider from the MLX-LM-based alternative covered later in this guide.

## Install the provider plugin

You can install the provider either from npm or directly from source, and neither path involves a build step.

**From npm** — the published package is at version `0.3.0` as of 2026-08-30:

```
npm install @raullenchai/dsh-provider
```

**From source** — clone the repository and install:

```
git clone https://github.com/raullenchai/rapid-mlx-dsh-provider
cd rapid-mlx-dsh-provider
npm install
```

Whichever route you take, the provider registers itself as a dsh plugin. The upstream project verifies the source install against `dsh 0.1.0-rc.7` and reports API compatibility with `rc.8`. If you are on `npm latest` for the harness, the plugin remains API-compatible. Because the harness treats anything under `dsh.bundle` as a plugin, the provider becomes available the moment dsh starts with it on the bundle path — there is no manual registration dialog and no build output.

## Point the agent at the route in settings.yaml

After installing the plugin, you tell dsh which HTTP route to use. This is the one piece of config you do write by hand, and it is intentionally small: a single endpoint pointing at your Rapid-MLX `/v1` OpenAPI-compatible route.

In `settings.yaml`, set the provider's route to your Rapid-MLX server's OpenAI-compatible base URL. Rapid-MLX is a drop-in OpenAI replacement, so the route you already use for Claude Code, Cursor, or Aider is the same one you hand to the dsh provider. From that point on, the heavy lifting — model names, context windows, reasoning efforts, and max model length — comes from the server rather than from your editor.

This single-line indirection is the entire point: you stop hand-writing model facts and start letting the server own them. When you switch from one pulled model to another, the provider follows the server's reported schema automatically.

## The three things it fixes

The provider's value lands in three concrete behaviors.

### 1. No more hand-written model config

The biggest win is eliminating per-model manual config. When `contextWindow`, `reasoningEfforts`, and `max_model_len` are all served by Rapid-MLX's `/v1/models` JSON schema, there is nothing to hand-write when you switch models. Swap the model, and dsh follows automatically because it reads the same facts the server uses to run the model.

### 2. Reasoning control finally reports the truth

Local model configs have a chronic lie: they declare reasoning settings for models that do not actually have a reasoning parser. The provider fixes this because Rapid-MLX reports whether a model really has a reasoning parser, and the dsh provider surfaces that truth in the reasoning-control selector. You stop telling the agent to reason with a model that physically cannot.

### 3. Compaction timed to real memory, not advertised windows

The third fix is the subtlest and the most valuable on Apple Silicon: the provider prefers the server's `max_model_len` — a memory-fitted ceiling — over the model's advertised `context_window`. Apple Silicon unified memory is the real constraint on context length, and hardware-aware capacity beats the marketing number that hand-copied config frequently drifts away from. The result is compaction that actually matches your machine.

## Manage models with five tools and the /rapid-mlx command

The provider keeps its surface deliberately small — five tools total, split by which surface owns each fact:

| Tool | Surface | What it does |
|------|---------|--------------|
| `rapid_mlx_serving` | HTTP | Interacts with the Rapid-MLX server over HTTP |
| `rapid_mlx_cached` | CLI | Reads cached model state |
| `rapid_mlx_pull` | CLI | Pulls a model into local storage |
| `rapid_mlx_remove` | CLI | Removes a stored model |
| `rapid_mlx_health` | HTTP + CLI | Health-checks the server and CLI surfaces |

In addition to these tools, the provider exposes a `/rapid-mlx` slash command in the agent interface for quick model management. The split is deliberate: facts owned by the server surface flow through the HTTP tools, and facts owned by the local process flow through the CLI tools. Keeping the two apart avoids the confusion that a single mixed-surface tool tends to create.

## Verified results on M3 Ultra with dsh 0.1.0-rc.7

The provider is not theoretical. The upstream README documents an end-to-end verification on an M3 Ultra against `dsh 0.1.0-rc.7`. In that run, a multi-step bug-fixing task completed in 36 seconds on `qwen3.6-35b-8bit`. That number matters because it shows the plugin doing real work — a realistic agent task with multiple tool calls and reasoning steps — not just booting and idling. The 36-second figure is the best single proof that the provider's route plumbing, reasoning routing, and tool dispatch all function as a unit under load.

## What it does not do yet

Being precise about the current gaps saves you from assuming features that do not exist. The provider — and Rapid-MLX itself — still has roadmap items that are not wired up:

- **`recommended_sampling`.** Server-suggested sampling parameters are not yet consumed by the provider.
- **`tool_call_parser`.** Fast tool-call parsing directly on the server is not yet exposed through the provider.
- **Memory-aware capacity as a first-class feature.** The provider prefers `max_model_len` today, but fully adaptive capacity derived purely from the memory footprint of the loaded model is the roadmap's biggest remaining win. Right now you get the memory-fitted ceiling the server already reports; the future step is capacity that actively recomputes with load.

None of these block the core three fixes above, but they are worth knowing so your expectations match the current release.

## Conformance with the official LlmAdapter contract

Because DeepSeek Harness is plugin-driven, the bar for a new provider is conformance with the official `LlmAdapter` contract defined in `docs/cookbook/adding-an-llm-adapter.md`. The Rapid-MLX DSH Provider treats this as a test obligation: it ships per-protocol-obligation tests, one per rule in the contract, so conformance is not asserted in prose but demonstrated with executable tests.

This is a meaningful design choice. Most adapter plugins pass a smoke test and call it done. This provider structures its suite around the harness's own "protocol obligations," which means each method the harness relies on — model enumeration, context negotiation, reasoning-effort handling, tool-call framing — has a targeted test backing it. For anyone who has been burned by an agent plugin that silently violates a harness contract, this is the difference between a provider you can trust and one you debug at 2am.

## Three gotchas before you edit the provider

If you plan to extend or debug the plugin, these three details will save you real time:

1. **`dsh.bundle` makes it a plugin.** DeepSeek Harness treats anything under `dsh.bundle` as a plugin. If you fork the provider, keeping your code inside that bundle path is what makes the harness load it.
2. **`LlmReasoningEffortInfo.name` is required.** The reasoning-effort contract does not allow a missing `name` field. If the server reports a reasoning parser that maps to an effort entry without a name, the harness will reject it.
3. **DSH has no tool role.** Unlike some OpenAI-style APIs, DeepSeek Harness has no dedicated "tool" role in its message protocol. If you extend the provider, route tool-call framing through the roles dsh actually supports rather than assuming a `tool` role exists.

## Comparison: rapid-mlx DSH provider vs dsh-llm-mlx and other MLX Mac agents

The Rapid-MLX DSH provider is not the only way to run MLX models inside the DeepSeek Harness. The closest alternative is `dsh-llm-mlx`, which takes a different architectural route:

| Aspect | Rapid-MLX DSH Provider | dsh-llm-mlx |
|--------|------------------------|-------------|
| Underlying engine | Rapid-MLX server | mlx-lm / mlx-vlm |
| Integration path | Native `@raullenchai/dsh-provider` plugin | DSH built-in OpenAI-compatible adapter |
| Server ownership | Rapid-MLX runs as its own engine | Can manage `mlx_lm.server` / `mlx_vlm.server` for the lifetime of the dsh process |
| Bind address (managed) | Rapid-MLX default | `127.0.0.1` |
| External server reuse | Yes (OpenAI-compatible) | Yes, e.g. `http://127.0.0.1:18080/v1` |
| Extra runtime needed | Node >= 22.15 only | Local Python env with `mlx-lm` / `mlx-vlm` |
| OS for managed startup | Apple Silicon | Apple Silicon macOS |

The deciding factor is usually which engine you already run. If you use Rapid-MLX (with its 4.2x-over-Ollama claim, 0.08s cached TTFT, and 17 tool parsers), the native provider is the natural fit. If you prefer the mlx-lm stack and want dsh to own the model server lifecycle, `dsh-llm-mlx` is the better match. Both sit above a separate category of MLX coding agents — projects like `mlx-code`, the 57-star git-native coding agent for Mac — that prove the broader demand for Apple Silicon native agentic inference even though they are not dsh providers themselves.

## FAQ and troubleshooting

**Do I need a GPU to use the Rapid-MLX DSH provider?**
No. The provider is a config/adapter plugin — it does no inference itself. It delegates all model execution to a running Rapid-MLX server on your Apple Silicon machine, so you need an M-series chip, but no separate discrete GPU.

**Can the provider work with dsh 0.1.0-rc.8 or the npm release?**
Yes. The plugin was verified end-to-end against dsh `0.1.0-rc.7`, is API-compatible with `rc.8`, and the harness `npm latest` remains compatible with the published provider at `0.3.0`.

**Why does the provider prefer max_model_len over context_window?**
Because on Apple Silicon the unified memory footprint is the real ceiling on how long a context can grow, and `max_model_len` is the server's memory-fitted ceiling. The model's advertised `context_window` is often a marketing maximum that hand-copied config drifts away from, so preferencing the server's figure makes compaction match your actual hardware.

**How is this different from the built-in OpenAI-compatible adapter in dsh?**
The built-in adapter requires you to hand-maintain model facts in `settings.yaml` per model. The Rapid-MLX provider reads `contextWindow`, `reasoningEfforts`, and `max_model_len` from the server's `/v1/models` schema automatically, so switching models needs no manual re-config and reasoning settings report the server's truth.

**What happens if I run Node older than 22.15?**
dsh imports Node's Zstd stream API without declaring it, so on an older Node the harness fails at import time. Upgrade to Node >= 22.15 before troubleshooting anything else, because this error surfaces before the provider even loads.
