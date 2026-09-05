---
title: "DeepSeek Harness Handbook 2026: The Source-Backed Guide to Agents, Plugins, and Runbooks"
date: 2026-09-05T01:01:41+00:00
tags:
  - deepseek harness
  - deepseek harness handbook
  - deepseek harness plugins
  - deepseek harness agents
  - deepseek harness runbook
  - dsh agent harness
  - deepseek harness tutorial
  - deepseek harness config
  - deepseek harness cordis
  - deepseek harness web ui
  - deepseek harness workflow
  - deepseek harness skills
description: "DeepSeek Harness (dsh) is an open-source, everything-is-a-plugin agent harness built on Cordis. This 2026 handbook covers agents, plugins, runbooks, and developer-preview pitfalls."
draft: false
cover:
    image: "/images/deepseek-harness-handbook-2026.png"
    alt: "DeepSeek Harness Handbook 2026: Source-Backed Guide to Agents, Plugins, and Runbooks"
    relative: false
schema: "schema-deepseek-harness-handbook-2026"
---

DeepSeek Harness (dsh) is an open-source agent harness by DeepSeek AI, built on an everything-is-a-plugin architecture powered by Cordis, where the model adapter, tool registry, session log, and even the agent loop itself are replaceable plugins. You can launch it in seconds with `npx @deepseek-ai/dsh web`, connect a DeepSeek API key in Settings, and start delegating file edits, command runs, and multi-agent workflows. This 2026 handbook is a source-backed guide to its agents, plugins, and runbooks.

## What Is DeepSeek Harness (dsh)?

DeepSeek Harness, tracked in the `deepseek-ai/deepseek-harness` repository, is an open-source agent harness that treats every part of the product as a plugin. According to the official architecture documentation, the model adapter, tool registry, session log, and the agent loop itself are each replaceable from configuration. The project is built on Cordis, a framework whose design is described in the arXiv paper "A Programming Paradigm for Spatiotemporal Composability" (arXiv:2608.25512).

The project is young and fast-moving. As of 2026-09-04, the repository had 212,253 GitHub stars and 24,916 forks, was created on 2026-08-13, and is MIT-licensed. It is explicitly in developer preview, meaning compatibility-breaking changes are expected. The official README describes dsh as an agent harness where plugins contribute services, typed events, and reversible effects to a shared context.

### The Everything-Is-a-Plugin Model

The defining architectural decision is that nothing is privileged. There is no core to patch. If you want to change how the agent loop behaves, how tools are registered, or how sessions are logged, you mount a plugin beside the others. This is a sharp departure from monolithic agent frameworks where customization means forking the core.

### Cordis as the Foundation

Cordis provides the composability layer. Plugins contribute services, typed events, and reversible effects to a shared context. When a plugin unloads, its registrations unwind automatically. This reversibility is what makes the everything-is-a-plugin model safe to experiment with.

## Why Config-Over-Code Matters

The config-over-code philosophy is a core differentiator for dsh. A Hacker News discussion titled "DeepSeek harness: what doors does config over code open?" highlights the community's interest in this design. The key insight is that registrations are effects that unwind when a plugin unloads, and there is no privileged core to patch.

### Reversible Registrations

Because plugin registrations are reversible, you can load and unload capabilities without leaving residue. This makes it practical to compose different tool sets, model adapters, and behaviors for different tasks without maintaining separate forks or branches.

### Replaceable Subsystems

Every subsystem is a candidate for replacement. The model adapter determines which model you talk to. The tool registry decides which tools the agent can call. The session log records what happened. The agent loop defines how turns and steps are processed. Each of these can be swapped from configuration, which means the harness adapts to your workflow rather than the reverse.

## Getting Started in 5 Minutes

The fastest way to try DeepSeek Harness is the npx one-liner. Run `npx @deepseek-ai/dsh web` from your terminal. The Web UI defaults to `http://127.0.0.1:3080`, and you can pass `--no-open` to skip the automatic browser launch.

### Configure a Model

Once the Web UI is running, open Settings and navigate to Models. Add a DeepSeek API key there. The model route becomes usable immediately without restarting the harness, which is a practical convenience during setup.

### Choose a Workspace

Before the session composer becomes available, you must choose a workspace. The agent can read and edit files in that workspace, run commands, delegate work, and maintain a plan. Approval prompts appear under the active permission policy, so you stay in control of what the agent is allowed to do.

## Understanding Profiles and Bundles

DeepSeek Harness ships with five profile templates: `web`, `headless`, `sdk`, `sdk-minimal`, and `acp`. The `dsh-base` profile is the shared first layer of `web`, `headless`, `sdk`, and `acp`. Profiles are layered using `cordis.patch.yml`, which lets you compose a configuration from base layers and targeted overrides.

| Profile | Primary Use | Notes |
|---------|-------------|-------|
| web | Interactive Web UI | Default for `npx @deepseek-ai/dsh web` |
| headless | Scripted, no UI | Good for automation and CI |
| sdk | Programmatic access | Full SDK surface |
| sdk-minimal | Lightweight SDK | Minimal footprint |
| acp | Agent Client Protocol | For ACP-compatible clients |
| dsh-base | Shared foundation | First layer of web/headless/sdk/acp |

### Layering with cordis.patch.yml

The `cordis.patch.yml` file is where you express your configuration as a series of patches over base profiles. This is the config-over-code model in action: you describe what you want, and the harness composes the final configuration from the layers you specify.

## Agents and the Agent Loop

The agent loop is the heart of dsh. It processes turns and steps, assembles the system prompt, classifies tools, and enforces the approval policy. Understanding this lifecycle helps you predict how the agent will behave in your workspace.

### Turn and Step Lifecycle

A session is composed of turns, and each turn is composed of steps. The agent reads the current state, decides on an action, and either executes a tool or produces output. The loop continues until the task is complete or the agent needs input.

### System-Prompt Assembly

The system prompt is assembled from multiple sources, including skills and configuration. Skills are optional instructions (not session events) merged from a provider registry across host and per-scope layers. This means you can inject domain knowledge without hardcoding it into the core.

### Tool Classification and Approval

Shipped model-facing tools include `ask_user_question`, `run_code`, `exit_plan_mode`, `bash`, `job_*` tools, the skill tool, and the workflow tool. Tools are classified, and the approval policy determines which actions require human confirmation. This is how the harness balances autonomy with safety.

## Plugins: The Everything-Is-a-Plugin Model

Writing a plugin is the primary way to extend dsh. Because everything is a plugin, your custom capability mounts beside the built-in ones, and its registrations unwind when it unloads.

### The Config Catalog

The config catalog defines what a plugin can configure. It is the declarative surface that the config-over-code model exposes. When you write a plugin, you describe its configurable options, and the harness handles the rest.

### The Tool Catalog

The tool catalog is where plugins register the tools the agent can call. The shipped tool catalog includes the model-facing tools listed above. Your plugin can add new tools that the agent discovers and uses.

### Publishing with the dsh-plugin Topic

To share a plugin, publish it and tag it with the `dsh-plugin` GitHub topic. This is how the community discovers new capabilities. The official README points to GitHub Discussions, Discord, and the `dsh-plugin` topic as the community channels.

## Runbooks and Workflows

The workflow seam is one of the most distinctive features of dsh. It runs a model-written orchestration script that starts subagents, using a `node:worker_threads` engine with one worker per run. This is a practical runbook pattern: the agent writes a script, and the harness executes it to coordinate multiple subagents.

### The Workflow Seam

The workflow tool lets the agent delegate to subagents. The orchestration script is written by the model, which means the coordination logic is generated dynamically based on the task. The `worker_threads` engine isolates each run in its own worker.

### A Practical Runbook Pattern

For a runbook, you describe the steps, and the agent writes an orchestration script that spawns subagents to execute them in parallel or sequence. This turns a static runbook into an executable workflow that adapts to the task.

## Skills, Agent Teams, and Advanced Subsystems

Beyond the basics, dsh includes skills, experimental agent teams, and sandbox and permission presets.

### Skills Registry

Skills are optional instructions merged from a provider registry across host and per-scope layers. They are not session events; they are instructions that shape how the agent behaves. This is how you inject reusable expertise.

### Experimental Agent Teams

Agent Teams is an experimental domain with a durable mailbox. Each team task gets a `TeamTaskId` allocated as `task-<n>`, and members reach exactly one terminal phase: active or failed. This is a structured way to coordinate multiple agents on a shared objective.

### Sandbox and Permission Presets

Sandbox and permission presets control what the agent can do. The approval policy under the active permission preset determines which actions require confirmation. This is your safety boundary.

## The 2026 Plugin Ecosystem

The plugin economy around dsh is growing. Third-party registries such as `dshplugin.app` and `dsh-index.xlings.org` provide install commands, source-grounded capability analysis, security signals, compatibility evidence, and repository activity. The `dsh-plugin` GitHub topic is the canonical discovery surface.

| Registry | What It Offers |
|----------|----------------|
| dshplugin.app | Install commands, capability analysis, security signals, compatibility evidence |
| dsh-index.xlings.org | Community index of plugins |
| GitHub dsh-plugin topic | Canonical discovery and tagging |

### Security Signals

Because plugins are code, security matters. The registries surface security signals so you can evaluate a plugin before installing it. Source-grounded capability analysis tells you what a plugin can actually do, and compatibility evidence tells you whether it works with your version of dsh.

## Developer-Preview Pitfalls and Best Practices

DeepSeek Harness is in developer preview, and compatibility-breaking changes are expected. This is the most important thing to plan for in 2026.

### Version Pinning

Pin your dsh version. Because breaking changes are expected, a runbook that works today may not work after an upgrade. Pin the version in your project and upgrade deliberately, testing after each change.

### The Safety Notice

The official README includes a safety notice. Treat the harness as experimental, and do not rely on it for production-critical automation without testing. The everything-is-a-plugin model is powerful, but it also means behavior can change.

### Testing

Test your plugins and runbooks against a pinned version before relying on them. Because registrations are reversible, you can experiment safely, but you should still verify behavior in a controlled environment.

## Resources and Community

The official documentation lives at `deepseek-harness.github.io/deepseek-harness/`, covering the user guide (Web UI, models, providers, Python SDK, schedule) and the developer guide (basic, framework, practice), plus a Cordis primer and tutorial. The source repository is `deepseek-ai/deepseek-harness` on GitHub.

Community channels include GitHub Discussions, Discord, and the `dsh-plugin` GitHub topic. The project is MIT-licensed, so you can read the source, contribute, and build on it freely.

## FAQ

### What is DeepSeek Harness (dsh)?

DeepSeek Harness is an open-source agent harness by DeepSeek AI built on Cordis, where every part of the product — the model adapter, tool registry, session log, and agent loop — is a replaceable plugin. It is MIT-licensed and in developer preview.

### How do I start DeepSeek Harness?

Run `npx @deepseek-ai/dsh web` from your terminal. The Web UI defaults to `http://127.0.0.1:3080`. Add a DeepSeek API key in Settings → Models, then choose a workspace before starting a session.

### What does "everything-is-a-plugin" mean?

It means there is no privileged core to patch. Every subsystem, including the agent loop itself, is a plugin that can be replaced from configuration. Plugin registrations unwind automatically when a plugin unloads.

### What is the workflow seam in dsh?

The workflow seam runs a model-written orchestration script that starts subagents, using a `node:worker_threads` engine with one worker per run. It is a practical pattern for turning runbooks into executable multi-agent workflows.

### Is DeepSeek Harness production-ready?

No. It is in developer preview, and compatibility-breaking changes are expected. Pin your version, read the safety notice, and test your plugins and runbooks before relying on them in production.
