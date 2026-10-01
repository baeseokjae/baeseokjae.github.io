---
title: "Bivor Review: A macOS Desktop Workbench for the Pi Coding Agent (2026)"
date: 2026-10-01T00:37:44+00:00
tags:
  - pi coding agent
  - bivor
  - desktop workbench
  - macOS
  - coding agents
  - agent guardrails
  - git worktree
description: "Bivor is an open-source macOS workbench for the pi coding agent: parallel git worktree tasks, per-tool guardrails, checkpoints before every prompt, and CLI session interop."
draft: false
cover:
  image: "/images/bivor-macos-workbench-pi-agent.png"
  alt: "Bivor: A macOS Desktop Workbench for the Pi Coding Agent"
  relative: false
schema: "schema-bivor-macos-workbench-pi-agent"
---

Bivor is a free, MIT-licensed macOS desktop app that wraps the pi coding agent in an orchestration layer: it runs each chat as its own isolated pi process, gives every task a git worktree and branch, adds per-tool guardrails and turn/cost budgets, and snapshots the workspace before every prompt so you can roll back. It reads the same `~/.pi/agent/` session and config files as the pi CLI, so terminal and desktop sessions interoperate. It launched as v0.1.0 on 2026-08-15 and shipped v0.1.1 three days later.

That is the 55-word version. The rest of this review tests the claim on Bivor's own tagline — *"Your coding agent deserves a workbench, not a chat box"* — feature by feature, against the reality of a 0.1.x app with 209 stars, two releases, and a fast-moving upstream it does not control.

## What Is Bivor, and What Does "Workbench" Actually Mean Here?

Bivor is a macOS-only, Electron-based GUI for the pi coding agent (`@earendil-works/pi-coding-agent`). The project describes itself as a desktop workbench built to match the Codex and Claude desktop experiences and then go further with visual harness orchestration, guardrails, cloud VM sandboxes and parallel worktree tasks (source: [github.com/ryanlab/bivor](https://github.com/ryanlab/bivor)).

The word "workbench" is doing real work in that sentence. A chat box accepts one prompt and streams one answer. A workbench is where you arrange multiple jobs, control what each one is allowed to touch, watch what they cost, and undo them. Bivor's feature list maps onto exactly those four verbs:

- **Arrange:** multiple chats, each in its own isolated process, plus subagents, scheduled tasks and a Mission Control grid.
- **Control:** per-tool allow/ask/deny rules, bash regex rules, runtime presets, turn and cost budgets.
- **Watch:** token and cost metadata per task, live tool-call cards, a visual harness canvas.
- **Undo:** git checkpoint snapshots before every prompt, per-file restore, session tree forking.

Under the hood it is an Electron 43 / React 19 / TypeScript application managed with pnpm 10. The architecture splits into `src/main` (windows, menu, services), `src/host` (an agent host that embeds the pi SDK's `AgentSessionRuntime`), `src/preload` (a typed contextBridge), `src/renderer` (React + Zustand) and `src/shared/protocol.ts`. Each chat gets its own Electron utility process, which is what makes parallel tasks safe by construction rather than by convention.

## Is Pi's Deliberate Minimalism the Reason Bivor Exists?

Yes — and it is the single most important thing to understand before judging Bivor's feature list.

Armin Ronacher's write-up on Pi describes a deliberately tiny core: among the shortest system prompts he knows of, and just four tools (Read, Write, Edit, Bash). No built-in MCP support, no plan mode, no todos, and no subagents in core — all missing on purpose, on the theory that you ask the agent to extend itself (source: [lucumr.pocoo.org](https://lucumr.pocoo.org/2026/1/31/pi/)).

Critically, Pi core also ships **no permission system**. The upstream README states that Pi has no built-in permission system for filesystem, process, network or credential access, and runs with the permissions of the user who launched it; containerization is the documented mitigation (source: [github.com/earendil-works/pi](https://github.com/earendil-works/pi)).

That gap is the whole commercial and practical argument for a desktop layer. Everything Bivor adds — approve-before-write cards, bash pattern blocking, spend caps, disposable VMs — is a feature Pi core refuses to ship by philosophy. Bivor is not competing with Pi; it is monetizing the deliberate holes in Pi.

## What Does the Unsigned DMG Cost You at Install Time?

Bivor is distributed as a macOS DMG only. Both public releases — v0.1.0 (2026-08-15) and v0.1.1 (2026-08-18) — are explicitly unsigned, in arm64 and x64 builds (source: GitHub releases API, fetched 2026-10-01). This is not a Bivor-specific sin, but it is a Bivor-specific cost, and it does not change until the maintainer notarizes.

What that means in practice:

1. Download the DMG for your architecture from the GitHub releases page.
2. Try to open it. Gatekeeper will refuse and tell you the app is damaged or from an unidentified developer.
3. Right-click → Open, or run `xattr -cr /Applications/Bivor.app` to strip the quarantine attribute.
4. Install the pi CLI and authenticate a model provider first — Bivor is a front end for pi, not a replacement for it.
5. Verify what you installed before pointing it at work code.

That last step matters more than the other four combined. Petronella Technology Group's Pi.dev review makes the point that a compliance review is only valid for the exact build it was performed against, and recommends pinning the npm version you validated (source: [petronellatech.com](https://petronellatech.com/blog/pi-dev-platform-review/)). Bivor 0.1.1 wraps a Pi that is now on 0.99.2 with weekly releases. Pin both, or accept that your threat model drifts every week.

## How Do Parallel Tasks and Git Worktrees Work in Bivor?

This is Bivor's strongest structural idea, and it is the feature that most cleanly distinguishes a workbench from a chat box.

Every Bivor chat runs the pi SDK in its own isolated process, so two concurrent tasks cannot corrupt each other's state. On top of that, a **worktree task** creates a dedicated git worktree plus a branch named `pi/task-*`, and you merge the result back from a built-in merge panel.

Why this beats "just open two terminals": with plain concurrent agents, two sessions editing the same checkout race on the index and the working tree. Each agent sees the other's half-finished edits, and `git status` becomes noise. Worktrees give each task its own directory sharing one object store, so parallel agents are physically incapable of stepping on each other, and every task produces a reviewable branch instead of an interleaved mess.

The practical workflow that falls out of this:

- One worktree task per isolated unit of work — a migration, a test suite, a dependency bump.
- Let them run in the background while you keep working in the main checkout.
- Review each `pi/task-*` branch as a normal diff and merge from the panel, or discard it.

The limitation is honesty about git: worktree tasks are only as good as your repo hygiene. If your branch diverges badly, you are still doing a real merge — Bivor gives you a panel, not a merge fairy.

## What Is the Harness Canvas, and Why Is It Bivor's Real Differentiator?

Across the small field of Pi desktop apps, Bivor is the only one that exposes the agent's assembly as an editable live graph. The canvas surfaces the chain **model → system prompt → tools → extensions → skills** as connected nodes you can inspect and re-orchestrate while the harness is running, and the project also exposes a `harness_propose` path for self-tuning.

That matters because of how Pi is built. Ronacher notes that Pi's extension system can persist state into sessions — which is precisely what makes third-party assembly and orchestration layers possible in the first place. Bivor takes that affordance and puts a UI on it.

For most users this will be the least-used screen. For the audience that cares — people maintaining their own agent configurations, or debugging why an agent behaves differently in two contexts — it replaces a folder of config files and guesswork with a single diagram. It is also the feature most likely to break on an upstream Pi release, because it is coupled to internals rather than to a stable API.

## Do Bivor's Guardrails Actually Make a YOLO Agent Safe?

They are the strongest practical reason to put a GUI on Pi, and they are also where the honest caveats live. Bivor's guardrail set, per the repository:

- **Per-tool allow / ask / deny** policies, surfaced as inline approval cards in the conversation.
- **Regex rules for bash**, so you can block or force approval on shell patterns rather than whole commands.
- **Budgets** for turns, tool calls and session cost.
- **Subagent limits** plus a repeated-call circuit breaker that stops an agent looping on the same failing call.

**Runtime presets** reframe the app as four tools in one, because the capability envelope changes with the preset:

| Preset | Capability envelope | Realistic use |
| --- | --- | --- |
| Daily | No coding side effects | Non-coding questions, planning, writing |
| Coding | Full agent | Normal development work |
| Review | Read/search only — writes and bash denied | Audits, compliance passes, code reading |
| Minimal | bash + read + edit | Tight, deliberate sessions |

The Review preset is the underrated one. It is a credible safe mode for audit-heavy or compliance-sensitive work, and it is the closest thing in this category to a "read-only" switch that does not require you to trust the model.

Two caveats, stated plainly:

1. **Guardrails are app-level controls, not a sandbox.** They constrain what the agent is *asked* and *allowed* to do through Bivor. Pi's own warning stands: the agent runs with your user's permissions. The real isolation layer is the E2B cloud VM or a container.
2. **They are policy for a 0.1.x app.** Regex bash rules and cost budgets are only as good as the code path that enforces them, and there has been no commit to the repository since 2026-08-18.

## Checkpoints and Session Trees: How Much Can Bivor Undo?

More than any comparable Pi desktop app, and the implementation detail is better than the headline.

Before every prompt, Bivor takes a git snapshot under `refs/pi-checkpoints/`. Snapshots are stored as refs rather than commits on your branch, and the snapshot mechanism never touches your index — so your staged work is exactly as you left it. From a checkpoint you can:

- **Restore the whole workspace** to the pre-prompt state.
- **Restore individual files**, keeping unrelated agent edits you want to keep.
- **Fork the session tree** from any message, with LLM-generated summaries for abandoned branches so you can see what a discarded path was doing.

This combination — snapshot before every turn, restore at file granularity, branch the conversation at any point — is what makes a default-permissive coding agent tolerable on a real repository. Without it, one bad multi-file edit in a long session is a `git reset` archaeology project. With it, the cost of a bad idea is one click.

## What Runs Where — E2B Sandboxes, Subagents, Browser and Code Mode?

Bivor's optional integrations route work off your machine, and all of them require your own API keys:

| Capability | Where it runs | Requirement |
| --- | --- | --- |
| E2B cloud VM sandbox | Disposable cloud desktop with live screen streaming | E2B API key |
| Web search | Via Tavily | Tavily API key |
| Deploy tool + ops panel | Via Vercel | Vercel account |
| Browser control | Local browser binary, optional override | `CHROME_PATH` (optional) |
| Subagents | Spawned agent sessions under the parent task | Built in |
| Code mode | Script-driven tool calls | Built in |

The E2B integration is the genuinely unusual one in this category. The app exposes `vm_gui`, `vm_file` and `vm_screenshot`, so an agent can drive a GUI, move files and capture screenshots inside a throwaway desktop VM while your host machine stays untouched. If you have ever wanted to let an agent run an installer or click through a UI without risking your laptop, this is the closest thing to that here.

The cost is that each integration is a separate key, a separate vendor, and a separate thing that can be misconfigured. Nothing here is on by default, which is the right call for a 0.1.x app but also means "Bivor supports cloud sandboxes" describes a configuration you have to build.

## Mission Control and Cost Visibility: Who Is Burning the Budget?

Mission Control is a grid view showing, per task: status, the tool currently running, active subagents, tokens consumed, and cost. Combined with scheduled tasks (interval, daily, weekly) and the budgets from the guardrails layer, it answers the question every team eventually asks about agent tooling — *what is spending money right now, and on what?*

That is a real gap in the terminal experience. Pi's TUI shows you the current session; it does not give you a portfolio view across a dozen background tasks. For a single developer the grid is a convenience. For anyone running scheduled overnight agent work, it is the only place you can see the whole picture without opening twelve windows.

## Can You Use Bivor and the Pi CLI Interchangeably?

Yes, and this is the best migration story in the category.

Bivor reads and writes pi's own session files, auth, skills, prompts and MCP configuration under `~/.pi/agent/`. There is no separate session store, no import step and no export step. Practically:

- Start a task in the terminal, pick it up in Bivor — history intact, checkpoints intact.
- Start in Bivor for the visual review surface, finish in the terminal when you want to script something.
- Keep your skills, prompts and MCP servers in one place that both front ends read.

This is an anti-lock-in argument that most GUI wrappers cannot make, and it means choosing Bivor is not really a commitment — it is a second view onto work you already have.

## How Does Bivor Compare to OpenPi, Pi Desktop and the Pi TUI?

Bivor is not alone in this niche, and the comparison is where a purchase decision actually gets made.

| | **Bivor** | **OpenPi** | **Pi Desktop (pi-desktop.com)** | **Pi TUI (upstream)** |
| --- | --- | --- | --- | --- |
| Platform | macOS only | macOS (signed? no — not notarized) | macOS, Linux, Windows | Terminal, anywhere |
| Install | Unsigned DMG | `brew install --cask openpi` | DMG / AppImage / installer | `npm i -g` |
| Release cadence | 2 releases, latest 2026-08-18 | 30+ tagged betas, latest 2026-09-16 | v0.9.5, 2026-09-14 | Weekly, v0.99.2 on 2026-09-30 |
| GitHub stars | 209 | 217 | n/a (213 commits on tanRdev/pi-desktop) | 110,766 |
| Harness canvas (live graph) | Yes — unique here | No | No | No |
| Per-tool allow/deny + approvals | Yes | Not documented | Yes (review rail) | No |
| Cloud VM sandbox | Yes (E2B, live screen streaming) | No | No | No |
| Scheduled tasks | Yes | No | No | No |
| Git worktree tasks | Yes | No | Yes (optional new worktree) | No |
| Community / roadmap | 1 open issue, no roadmap | ROADMAP.md, AGENTS.md, r/PiCodingAgent | Public site + release notes | Huge |
| CLI session interop | Yes (`~/.pi/agent/`) | Yes (hosts the pi SDK) | Yes (pi + omp binaries) | n/a |

Read the table honestly and three things fall out.

First, **maturity is not Bivor's column.** OpenPi has thirty-plus tagged betas, an explicit roadmap, an `AGENTS.md`, and a subreddit. Bivor has two releases, one open issue, and its last ten commits are all dated 2026-08-18 — a single-burst project, not a steady cadence. If what you want is a maintained, community-reviewed app today, OpenPi is the safer bet.

Second, **Bivor is the only one that goes past the chat surface in orchestration terms.** The harness canvas, the E2B sandbox, scheduled tasks and git worktree merging in one app are not replicated by any competitor in this table.

Third, **the whole category is young.** Pi itself only became a branded package in May 2026, when the npm scope moved from `@mariozechner/pi-coding-agent` to `@earendil-works/pi-coding-agent` at version 0.74.0 (source: [pi.dev/news](https://pi.dev/news/2026/5/7/pi-has-a-new-home)). Every app in this table is a few months old and wrapping something that ships weekly.

## What Are Bivor's Honest Risks and Limitations in 0.1.x?

The risks are not hypothetical, and a review that skips them is marketing.

- **It is a 0.1.x app.** Two releases, three days apart, in August 2026. Expect rough edges and undocumented behavior.
- **No commit since 2026-08-18.** At the time of this research, the repository showed no activity for roughly six weeks. That is not abandonment, but it is not a heartbeat either.
- **Unsigned builds.** Gatekeeper workarounds are mandatory, and every user does the `xattr -cr` dance.
- **Single maintainer, single platform.** The one open issue is a request for Windows support, and the maintainer has scoped ports behind `process.platform` checks. macOS-only is the state of play.
- **Upstream churn is a structural risk.** Pi's npm package has published 52 versions since 2026-05-07 and moved 4,316,299 downloads in the week of 2026-09-23 to 2026-09-29 alone. Bivor couples to Pi internals (the SDK session runtime, extension state) rather than to a frozen interface. An upstream release can break the harness canvas before Bivor ships a fix.
- **Almost no discoverability.** Pi's flagship Hacker News launch hit 608 points in February 2026; there are zero HN submissions linking `bivor.dev` or `ryanlab/bivor`, and the adjacent "Is there a Pi with desktop version?" Ask HN got a single point. You will not find community troubleshooting threads because there are none yet.
- **Guardrails are not isolation.** Repeat: Pi runs with your user's permissions. Use E2B or a container for anything you would not run by hand.

## Who Should Use Bivor, and Who Should Wait?

**Use Bivor now if** you are on macOS, already invested in Pi, and the specific gaps you feel are orchestration-shaped: you want parallel worktree tasks, spend caps, approve-before-write cards, checkpoints you can restore per file, and a portfolio view of running agents. The harness canvas and the E2B sandbox have no real substitute in this category, and the CLI interop means trying it costs you nothing permanent.

**Wait if** you need a supported, notarized, community-tested app; if you are not on macOS; if you want release notes you can plan around; or if your compliance posture forbids unsigned binaries on principle. OpenPi is the more mature alternative for the first two; the plain pi TUI is still excellent for the rest.

**Price:** free and MIT-licensed. The app costs nothing; your provider API usage is the real bill, which is exactly why the budget and Mission Control features matter.

**Setup checklist before you commit to it:**

1. Pin the pi version you validated and check the package scope is `@earendil-works/*`, not the deprecated `@mariozechner/*` scope.
2. Decide session retention before your first session — where `~/.pi/agent/` lives, who can read it, how long it survives.
3. Start in the **Review** preset on any repository you do not fully trust.
4. Set turn, tool-call and cost budgets on day one, not after the first surprise invoice.
5. Configure E2B if you plan to let the agent execute anything you would not run yourself.
6. Verify the DMG hash and source before installing on a work machine.

**Verdict:** Bivor is a genuinely interesting 0.1.x app with the clearest thesis in its category — that a coding agent needs a workbench, not a chat box — and it backs the thesis with features Pi core deliberately omits. It is not yet the app most people should install by default. It is the app the right handful of people should try this month.

## FAQ

**Is Bivor free?**
Yes. Bivor is free and MIT-licensed, distributed as a macOS DMG from the project's GitHub releases. You pay only for your own model provider usage, plus any optional integrations you enable (E2B, Tavily, Vercel).

**Is Bivor safe to install on a work laptop?**
Only with deliberate steps. Both releases are unsigned, so you must bypass Gatekeeper with a right-click Open or `xattr -cr`, then verify the download and pin the exact pi version you validated. If unsigned binaries are disallowed by policy, build from source or wait for notarization.

**Does Bivor replace the pi CLI?**
No — it wraps it. Bivor reads and writes pi's own session files, auth, skills, prompts and MCP config under `~/.pi/agent/`, so the terminal and the desktop app share one history and you can move between them freely. You still install and authenticate the pi CLI.

**Can Bivor run on Windows or Linux?**
Not today. Bivor is macOS-only in 0.1.x; its single open issue is a request for Windows support, and the maintainer has scoped ports behind `process.platform` checks. Pi Desktop and the pi TUI are the cross-platform options.

**How is Bivor different from OpenPi?**
OpenPi is the more mature app: thirty-plus tagged beta releases, an explicit roadmap, a Homebrew cask, and a community subreddit. Bivor is younger (two releases) but adds things OpenPi does not — a live harness canvas for editing model, prompt, tools and skills as a graph; an E2B cloud VM sandbox with screen streaming; scheduled tasks; and pre-prompt git checkpoints under `refs/pi-checkpoints/` with per-file restore and session-tree forking.

---

*Sources: [bivor.dev](https://bivor.dev/), [github.com/ryanlab/bivor](https://github.com/ryanlab/bivor), GitHub REST API (repository, releases, commits and issues for ryanlab/bivor and earendil-works/pi, fetched 2026-10-01), [npm registry metadata for @earendil-works/pi-coding-agent](https://registry.npmjs.org/@earendil-works/pi-coding-agent), [Armin Ronacher on Pi](https://lucumr.pocoo.org/2026/1/31/pi/), [Petronella Technology Group Pi.dev review](https://petronellatech.com/blog/pi-dev-platform-review/), [pi-desktop.com](https://pi-desktop.com/), [github.com/heyhuynhgiabuu/openpi](https://github.com/heyhuynhgiabuu/openpi), HN Algolia API.*
