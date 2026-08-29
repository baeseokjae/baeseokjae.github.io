---
title: "DeepSeek Harness Plugin Hub: The 4000+ Plugin Marketplace Explained"
date: 2026-08-29T10:01:21+00:00
tags:
  - deepseek harness
  - plugin hub
  - dsh plugin marketplace
  - ai agents
  - developer tools
description: "The DeepSeek Harness plugin hub grew from 0 to 7,740 plugins in under 3 weeks. Here's how the 'everything is a plugin' marketplace works, how to install plugins, and what to check before you do."
draft: false
cover:
  image: "/images/dsh-plugin-hub-marketplace-2026.png"
  alt: "DeepSeek Harness Plugin Hub: The 4000+ Plugin Marketplace Explained"
  relative: false
schema: "schema-dsh-plugin-hub-marketplace-2026"
---

The DeepSeek Harness plugin hub is a decentralized, source-backed marketplace where every capability of the harness — models, tools, skills, sessions, sandboxes, storage, loops, scheduling, and the UI — is a swappable plugin. It grew from 0 to 7,740 plugins in under three weeks, making it one of the fastest-growing plugin ecosystems ever built. This guide explains how the hub works, how to install and publish plugins, and what to check before you trust one.

## What Is the DeepSeek Harness Plugin Hub?

The DeepSeek Harness plugin hub is the marketplace for plugins that extend the DeepSeek Harness, an open-source AI agent framework released in developer preview around August 12–13, 2026. Unlike a traditional app store with a central gatekeeper, the hub has no single owner: plugins are indexed directly from GitHub repositories tagged with `dsh-plugin`, which makes it a decentralized, source-backed marketplace.

The official project page describes the philosophy in three words: "Everything is a plugin." Every capability you might want to change — the model that powers the agent, the tools it can call, the skills it has learned, the session and sandbox it runs in, the storage it uses, the loops and scheduling that drive it, and even the user interface — is a plugin that can be swapped or recomposed without touching source code.

Because the harness is in developer preview, the ecosystem is still settling. Multiple independent registries have sprung up to index plugins, each with different counts and features. The hub is best understood not as one website but as a network of registries, directories, and package indexes that all point back to the same GitHub-tagged plugin repos.

## The "Everything Is a Plugin" Architecture Explained

The core idea behind the DeepSeek Harness is that you should never have to fork the framework to extend it. Instead, the harness is built on the Cordis kernel, which manages plugin mounting, unmounting, and dependency resolution. The design is described in the paper "A Programming Paradigm for Spatiotemporal Composability" (arXiv:2608.25512).

In practice, this means you compose the harness with configuration rather than code. You select, swap, or extend any capability by editing configuration, and the Cordis kernel handles the rest — loading the plugin, resolving its dependencies, and mounting it into the running harness.

This architecture has three practical consequences:

1. **You extend by composing, not forking.** To add a capability, you add a plugin. To change a capability, you swap one plugin for another. The harness core stays untouched.
2. **Capabilities are modular and recomposable.** Because each capability slot is independent, you can mix and match — a different model, a different storage backend, a different UI — without breaking the rest.
3. **The barrier to contribution is low.** Anyone can publish a plugin by tagging a GitHub repo with `dsh-plugin`. There is no approval process, which is both the ecosystem's greatest strength and its biggest risk.

The quickest way to see this in action is to run the official quick start: `npx @deepseek-ai/dsh web`, which launches the Web UI at `http://127.0.0.1:3080` by default.

## The 9 Capability Slots: What Each One Does

The DeepSeek Harness defines nine swappable capability slots. Each slot is a category of plugin that fills a specific role in the harness. Understanding these slots is the key to navigating the marketplace, because every plugin you see belongs to one of them.

| Capability Slot | What It Controls | Example Use |
|----------------|------------------|-------------|
| **Model** | The underlying language model powering the agent | Swap in a different model provider or a fine-tuned variant |
| **Tools** | The functions the agent can call | Add web search, code execution, or API integrations |
| **Skills** | Learned capabilities and workflows | Install a pre-built skill for a specific domain |
| **Session** | How conversations and state are managed | Change session persistence or context handling |
| **Sandbox** | The execution environment for code | Tighten or loosen isolation for running untrusted code |
| **Storage** | Where data and artifacts are kept | Swap local storage for cloud or database backends |
| **Loop** | How the agent iterates on tasks | Change the reasoning or retry loop behavior |
| **Scheduling** | When and how tasks are triggered | Add cron-style or event-driven scheduling |
| **UI** | The user interface | Replace the default web UI with a custom interface |

The DSH Plugin Directory (dshplugin.online) organizes its 7,740 plugins across exactly these nine slots. The independent DSH Plugin Registry (dshplugin.app) uses a slightly different set of eight categories, which is one reason the two sites report different totals.

## How Big Is the Marketplace? Growth From 0 to 7,740 Plugins

The growth of the DeepSeek Harness plugin ecosystem is remarkable by any measure. The DSH Plugin Directory tracked the following daily plugin counts:

| Date (Aug 2026) | Plugins Indexed |
|-----------------|-----------------|
| Aug 12 | 0 |
| Aug 13 | 202 |
| Aug 14 | 1,635 |
| Aug 15 | 2,713 |
| Aug 16 | 3,744 |
| Aug 17 | 4,473 |
| Aug 18 | 4,931 |
| Aug 19 | 5,329 |
| Aug 20 | 6,055 |
| Aug 21 | 6,466 |
| Aug 22 | 6,651 |
| Aug 23 | 6,842 |
| Aug 24 | 7,000 |
| Aug 25 | 7,164 |
| Aug 26 | 7,335 |
| Aug 27 | 7,472 |
| Aug 28 | 7,666 |
| Aug 29 | 7,740 |

That is roughly 1,000+ plugins per day in the first week, and the total reached 7,740 plugins from 4,796 authors by August 29, 2026. For context, the official `deepseek-ai/deepseek-harness` GitHub repository itself has 202,666 stars and 23,326 forks under an MIT license — an extraordinary adoption rate for a project that only launched in mid-August.

The independent DSH Plugin Registry (dshplugin.app) reports a smaller but still substantial 1,545 plugins across 8 categories. The difference in counts is not a contradiction; it reflects that the two registries use different indexing methods, category schemes, and update schedules. The largest categories by plugin count are Developer Tools (1,446), UI & Productivity (942), Terminal & TUI (667), and Security & Policy (604).

## The Major Plugin Registries and Directories (and How They Differ)

Because the DeepSeek Harness plugin hub is decentralized, there is no single canonical list. Instead, several independent services index the same GitHub-tagged plugin repos, and they differ in scope, features, and counts. Here is how the main ones compare:

| Registry | What It Is | Plugin Count | Key Feature |
|----------|-----------|--------------|-------------|
| **dshplugin.online** (DSH Plugin Directory) | "Every DeepSeek Harness Plugin" | 7,740 | Indexes all 9 capability slots from 4,796 authors; tracks daily growth |
| **dshplugin.app** (DSH Plugin Registry) | "Find and compare community plugins" | 1,545 | Source-backed capabilities, install paths, security signals, compatibility evidence |
| **dsh-index.xlings.org** (dsh index) | Plugins and Agents package index | 119 packages / 188 versions | Hosts ready-to-run Agents (Agent = Harness + Plugins) |
| **deepseek-ai/deepseek-harness** (GitHub) | Official repository | 202,666 stars | The source of truth for the harness itself |

The practical takeaway is that you should treat these as complementary tools. Use the directory (dshplugin.online) to see the full breadth of the ecosystem, use the registry (dshplugin.app) to compare plugins with security and compatibility signals, and use the package index (dsh-index) when you want a ready-to-run Agent rather than assembling plugins by hand.

## How to Install a DeepSeek Harness Plugin (Step by Step)

Installing a plugin is straightforward and is done through the `dsh` command-line tool. The general pattern is:

```bash
dsh plugin --profile <profile> add <source>
```

Here is a step-by-step walkthrough:

1. **Install the harness.** If you have not already, install the DeepSeek Harness. The official quick start is `npx @deepseek-ai/dsh web`, which launches the Web UI.
2. **Find a plugin.** Browse one of the registries (dshplugin.app or dshplugin.online) to find a plugin that fills the capability slot you need. Note its source repository.
3. **Add the plugin to a profile.** Use the `dsh plugin` command with a profile name and the plugin source:
   ```bash
   dsh plugin --profile my-agent add <source>
   ```
4. **Verify the plugin mounted.** Check the harness output or UI to confirm the plugin loaded without dependency errors.
5. **Compose with configuration.** If you want to swap or extend capabilities, edit the harness configuration rather than the source code. The Cordis kernel handles mounting and dependency resolution.

For ready-to-run Agents, the dsh-index package index supports installing a complete agent profile directly, for example `dsh:agent-web-coding`, which bundles the harness plus the plugins it needs. This is the fastest way to get a working agent without assembling plugins one by one.

## How to Publish Your Own Plugin to the Hub

Publishing a plugin to the DeepSeek Harness plugin hub is deliberately low-friction, which is why the ecosystem grew so fast. The core requirement is to tag your GitHub repository with `dsh-plugin`. Once tagged, the independent registries and directories pick it up and index it.

The basic steps are:

1. **Build your plugin.** Create a plugin that fills one of the nine capability slots (Model, Tools, Skills, Session, Sandbox, Storage, Loop, Scheduling, or UI).
2. **Tag your repository.** Add the `dsh-plugin` tag to your GitHub repo so the indexing services can find it.
3. **Provide good metadata.** Include a clear description, the capability slot it fills, and any dependency or compatibility information. Registries like dshplugin.app surface this metadata as "source-backed capabilities" and "compatibility evidence."
4. **Consider publishing to a package index.** If you want your plugin to be installable as part of a ready-to-run Agent, you can also publish it to the dsh-index package index.

Because there is no central approval process, the quality and safety of plugins vary widely. That makes the metadata you provide — and the security signals surfaced by registries — especially important for building trust with users.

## Security and Compatibility: What to Check Before Installing

The decentralized nature of the DeepSeek Harness plugin hub is a double-edged sword. Anyone can publish, which means anyone can publish something malicious, broken, or abandoned. Before you install a plugin, check the following:

- **Dependency signals.** Registries like dshplugin.app surface dependency information. A plugin with many or unusual dependencies is harder to audit and more likely to break.
- **License signals.** Check the plugin's license. The official harness is MIT-licensed, but community plugins may use other licenses with different obligations.
- **Lifecycle-script signals.** Some plugins run scripts during installation or execution. Be cautious with plugins that execute arbitrary lifecycle scripts, especially if you run them in a privileged environment.
- **Compatibility evidence.** The harness is in developer preview, and the official repo warns: "THERE WILL BE COMPATIBILITY-BREAKING CHANGES." A plugin built for one version may not work on the next. Check the plugin's stated compatibility and pin versions where possible.
- **Repository facts.** Look at the plugin's source repository — its star count, activity, and maintainer history. A plugin with a few stars and no recent commits is a higher risk than an actively maintained one.

The security-first posture of the registries exists precisely because the ecosystem is open. Treat every plugin as untrusted until you have reviewed its source and signals.

## Top Community Plugins Worth Trying

A few community plugins have already risen to prominence in the young ecosystem. According to the DSH Plugin Registry, the most popular include:

- **dsh-routing-suite** (6.9k stars) — A routing suite that helps direct agent requests to the right model or tool, useful for complex multi-step workflows.
- **DSH Web UI** (6.3k stars) — A popular alternative web interface for the harness, demonstrating the power of the swappable UI slot.
- **ModLens** (3.7k stars) — A vision plugin that adds image understanding capabilities to the harness.

These plugins are worth trying because they are the most battle-tested in the ecosystem so far. Their high star counts reflect real usage and community validation, which is a useful signal in a marketplace where anyone can publish.

## The Future of the DeepSeek Harness Plugin Ecosystem

The trajectory of the DeepSeek Harness plugin hub suggests several likely developments. First, the growth rate — 0 to 7,740 plugins in under three weeks — will almost certainly slow as the ecosystem matures, but the sheer volume already makes curation and discovery a real problem. Expect better search, filtering, and recommendation features across the registries.

Second, the fragmentation across multiple registries (dshplugin.app, dshplugin.online, dsh-index) is likely to consolidate or at least standardize. Differing counts and category schemes confuse users, and there is pressure for a shared canonical index.

Third, security will become more important as the plugin count grows. The registries already surface security signals, and this is likely to deepen — possibly with automated scanning, signing, or reputation systems.

Finally, the shift toward ready-to-run Agents (Agent = Harness + Plugins) is the most interesting trend. If installing a complete agent profile becomes the default, the plugin hub evolves from a component marketplace into a full agent marketplace, dramatically lowering the barrier to using DeepSeek Harness for real work.

## FAQ: DeepSeek Harness Plugin Hub

**What is the DeepSeek Harness plugin hub?**
The DeepSeek Harness plugin hub is the decentralized marketplace for plugins that extend the DeepSeek Harness AI agent framework. Plugins are indexed from GitHub repos tagged `dsh-plugin`, and every capability of the harness — models, tools, skills, sessions, sandboxes, storage, loops, scheduling, and UI — is a swappable plugin.

**How many plugins are in the DeepSeek Harness plugin hub?**
Counts vary by registry. The DSH Plugin Directory (dshplugin.online) indexed 7,740 plugins from 4,796 authors as of August 29, 2026, while the DSH Plugin Registry (dshplugin.app) reported 1,545 plugins. The difference reflects different indexing methods and category schemes.

**How do I install a DeepSeek Harness plugin?**
Use the `dsh` command-line tool with the pattern `dsh plugin --profile <profile> add <source>`. For ready-to-run agents, you can install a complete profile from the dsh-index package index, such as `dsh:agent-web-coding`.

**Is the DeepSeek Harness plugin hub safe?**
The hub is decentralized with no central approval, so safety depends on the plugin. Check dependency, license, lifecycle-script, and compatibility signals surfaced by registries, and review the plugin's source repository before installing.

**How do I publish my own plugin to the hub?**
Tag your GitHub repository with `dsh-plugin`. The independent registries and directories will index it automatically. Provide clear metadata about the capability slot it fills, its dependencies, and its compatibility to help users trust it.
