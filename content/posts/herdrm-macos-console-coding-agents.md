---
title: "herdrm Review: The Coding Agent Console macOS Users Were Missing"
date: 2026-09-28T19:07:40+00:00
tags:
  - coding agent console macos
  - herdrm
  - herdr mac client
  - herdr alternative
  - coding agent multiplexer mac
  - claude code sidebar macos
  - multi-agent terminal dashboard
  - ssh remote coding agent client
  - herdrm license polyform noncommercial
  - macos 14 agent console app
description: "herdrm is a coding agent console for macOS and the herdr runtime: one sidebar for local and SSH agents, real PTYs, and a licence caveat."
draft: false
cover:
    image: "/images/herdrm-macos-console-coding-agents.png"
    alt: "herdrm Review: The Coding Agent Console macOS Users Were Missing"
    relative: false
schema: "schema-herdrm-macos-console-coding-agents"
---

herdrm is a native macOS SwiftUI client for herdr, the Y Combinator-backed agent runtime. It puts every space, coding agent, and terminal from your local Mac and any SSH device into a single sidebar, and clicking a row attaches the real agent PTY. It is a console, not an engine: it owns no terminals, and it does nothing without a herdr server behind it.

## Is herdrm a coding agent console on macOS, or just a window onto one?

The single most important thing to understand about herdrm is that it does not run agents. It renders them.

Every row you see in the sidebar comes off a Unix socket as newline-delimited JSON frames. herdrm holds no state that the herdr runtime does not already own. That architectural choice produces a failure model most agent UIs do not have: if herdrm crashes, your agents keep running, because the runtime never depended on the console. If herdr crashes, the work stops, and no amount of restarting herdrm brings it back.

Zentor's review of the app framed this as "a console, not an engine," and it is the cleanest way to describe it. The feature list reads like a window manager rather than an agent product precisely because the console is downstream of everything. Status, layout, session identity — all of it belongs to herdr. herdrm decides how it looks, not what it means.

That distinction matters economically too. herdrm is free-ish software rendering an Apache-2.0 runtime. If you evaluate only the Mac app, you are evaluating the smallest and least consequential piece of the stack.

| Layer | What it is | Licence | Fails as |
|---|---|---|---|
| herdr | Rust agent runtime, background server, local socket API, TUI built in | Apache 2.0 | Agents stop; the whole workflow halts |
| herdrm | SwiftUI macOS console that attaches to herdr sockets | PolyForm Noncommercial 1.0.0 | You lose the view; agents keep working |
| Agents (Claude Code, Codex, Cursor Agent, and others) | Real CLI processes owning real terminal panes | Vendor-specific | Only that pane is affected |

## How does herdrm talk to herdr (and why does that matter over SSH)?

herdrm connects to a herdr socket, and it treats a remote socket exactly like a local one. Remote sockets ride the normal OpenSSH path — typically `ssh -L` forwarding to the herdr daemon running on the far machine — with authentication handled by your OpenSSH config and agent, Tailscale SSH, or a password stored in the macOS Keychain. Because the transport is forwarding a Unix socket rather than inventing a second remote protocol, local and remote devices behave identically in the UI.

The practical consequence is the honest setup story: herdrm aggregates hosts but provides none. If you want an agent running at 3 a.m. on a machine that is not your laptop, that machine has to exist and stay awake — a VPS, a home server, a workbox that is always on. The Mac becomes the window, not the workspace. That connects directly to the always-on-agent pattern: the console is what makes it observable, not what makes it possible.

The app is also not Electron. It is a SwiftUI app with an embedded terminal engine, and the repository's language breakdown tells you something the marketing copy does not: on 2026-09-28, `missuo/herdrm` is 79.4% C and 19.9% Swift. The C share is the vendored libghostty (Ghostty) terminal engine, which arrived in the 0.6.x line; the README's architecture diagram still names SwiftTerm, which is documentation drift rather than a bug. Third-party coverage from August 2026 that reported the repo as "99.8% Swift" is describing a version of the project that no longer exists.

## What is actually in the console?

The sidebar is organised into spaces, agents, and terminals. Each device gets an OS badge and a tint, there is a device filter in the bottom-left corner, a `Cmd-K` search for jumping to a pane, notifications, and a live terminal view. Selecting a row runs the equivalent of `herdr agent attach` and drops you into the real PTY — no chat wrapper, no re-serialised transcript, no lossy tool-call rendering.

Status states are the part people trust too much. herdr decides whether an agent is running, waiting, or blocked; herdrm only renders that decision. Per the herdr agent documentation, state authority is layered: when an integration is installed (Pi, OMP, Kimi Code, MastraCode, OpenCode/Kilo via plugin), lifecycle hooks report state directly. When it is not, herdr falls back to a screen manifest — which is the path Claude Code, Codex, Cursor Agent, Copilot CLI, Grok, Antigravity, and Kiro take. Gemini CLI and Cline are detected but documented as less thoroughly tested. A screen-manifest agent can take several seconds to register a blocked prompt, and an agent that gets stuck in a way the manifest does not recognise can keep looking busy. Green dots are a hint, not ground truth.

## Why does a real terminal beat a chat wrapper for coding agents?

Because the workflows coding agents produce are not chat-shaped.

When Claude Code prints a diff, asks a permission question with a numbered menu, or opens a TUI of its own for a long-running plan, a chat-shaped client has to either emulate that UI or strip it. herdrm does neither: you get the actual pane, with shell history, logs, and running processes intact, and state rolls up from pane to tab to workspace. The same fidelity is why people keep diff viewers and pagers inside the agent session at all — they are readable only at real terminal width.

The cost of fidelity is that you inherit the terminal's own problems. One documented example: from 0.6.2 onward, every opened agent stayed mounted at zero opacity, so busy background agents kept drawing full-window Metal frames and typing in the visible pane lagged — worst over SSH and in large windows. It was fixed in 0.6.9 by telling Ghostty that hidden panes are occluded (issue #95). That is a real regression introduced and fixed inside a single minor line, which is what early-stage software looks like.

## What defaults should you change before you start?

The most consequential default in herdrm is one you should change on day one or consciously accept.

The New Agent picker enables each agent's own bypass-permissions flag by default. For Claude Code, that is `--dangerously-skip-permissions`. The maintainer's justification is coherent: detached agents run unattended, so a permission prompt that nobody answers is a dead end, and a console built around background sessions cannot afford dead ends. But the tradeoff is real, and it is not just a convenience footnote. An agent started that way will not stop to ask before it writes files, runs commands, or pushes.

A workable rule set:

- Keep bypass-permissions on only for agents running in a scratch or container-like workspace with no production credentials on the path.
- Turn it off for any agent with access to a real repository, cloud credentials, or a production SSH key.
- Never enable it for an agent on a machine you share with other people or workloads.
- Audit the notification settings at the same time; unattended agents are safe only if something is watching for the states you actually care about.

## How do you install herdrm without falling for the impersonation site?

herdrm has no official website. That sentence is not trivia — it is the reason a supply-chain incident happened in this project's name.

In 2026, a GitHub Pages site impersonating herdrm distributed a Windows payload (`zen.exe`, `Application.bat`, `key.txt`) under the herdrm brand. The maintainer confirmed in issue #86 that the only official sources are the GitHub repository `missuo/herdrm` and the Homebrew cask `owo-network/brew/herdrm`, and that genuine builds are signed by MOE AI LLC and notarised. If you install from anywhere else, you are trusting an unknown binary with your development machine.

The legitimate install path is short. The runtime first, on the Mac and on every remote box:

```bash
curl -fsSL https://herdr.dev/install.sh | sh
```

Then the console:

```bash
brew install owo-network/brew/herdrm
```

Alternatively, unzip the release into `/Applications`. herdrm requires macOS 14 or later and ships as a universal binary (Apple Silicon and Intel) with Sparkle auto-updates. There is no CI gate to point at, and the release cadence is aggressive: the project went public on 2026-08-19 and shipped v0.6.9 on 2026-09-23, with 37 documented versions in `CHANGELOG.md` in roughly five weeks. As of 2026-09-28 the repository shows 721 stars, 60 forks, 10 open issues, 204 commits, and 22 contributors, with 66 pull requests and 37 issues opened in total. Downloads across the last ten releases stand at 5,333 (13,131 across all 37 releases), of which `herdrm-0.6.9.zip` accounts for 305 and the Sparkle `appcast.xml` for 1,321 hits.

| Signal | Value (2026-09-28) | What it tells you |
|---|---|---|
| Stars / forks / contributors | 721 / 60 / 22 | Small, real, and actively contributed to |
| Commits / public since | 204 / 2026-08-19 | Five weeks of history, no long track record |
| Latest release | v0.6.9 (2026-09-23) | 37 versions in the changelog |
| Release downloads (all 37) | 13,131 | Installed base is small in absolute terms |
| Language mix | 79.4% C, 19.9% Swift | Vendored Ghostty engine, not a pure Swift app |

## Is herdrm free for commercial use, or do teams need a licence?

herdrm is licensed under PolyForm Noncommercial 1.0.0. In practice: free to use, modify, and share for any noncommercial purpose; commercial use requires a separate licence from the maintainer. GitHub's licence API still reports the repository as "Other/NOASSERTION" because PolyForm is not one of GitHub's recognised licences, so a casual scan of the repo sidebar will not tell you what you are agreeing to.

The history is instructive. Issue #67 was opened asking for a licence at a point when the repository had none — source-available but under default copyright. The maintainer replied that no LICENSE file means default copyright, and that a licence was being chosen "because it interacts with upcoming product plans." PolyForm landed; a follow-up question in the same thread about what "noncommercial" actually means for ordinary company work remains open.

For an individual developer this is a non-issue. For a team, it is the sentence to read before you install: the runtime underneath is Apache 2.0, and the console on top is not free at work. Test it as "the free runtime, the free console, the not-free-at-work app."

## How does herdrm compare with Waku, cmux, Bessie and Heeler?

herdrm is one client in a young ecosystem, and the ecosystem is growing far faster than the runtime's feature set. herdr itself sits at 41,234 stars and 3,168 forks with 370 open issues, last pushed 2026-09-28, and its latest stable release v0.9.1 (2026-09-16) has pulled 158,102 asset downloads. The project site claims 40,432 GitHub stars, 1,046,795 installs, 1,324 community plugins, 22 detected agent CLIs, and carries a "$6M raised" banner. Note the licence churn underneath the app you are reviewing: a July 2026 comparison article listed herdr as AGPL-3.0, while the live site now states Apache 2.0 — the runtime relicensed during the summer.

| Tool | What it is architecturally | Platform | Licence | Stars | Best for |
|---|---|---|---|---|---|
| herdrm | Client for a herdr socket; owns no terminals | macOS 14+ | PolyForm Noncommercial 1.0.0 | 721 | Multi-machine herdr users who want one window |
| herdr TUI | The runtime's own interface, built in | macOS, Linux, Windows | Apache 2.0 | 41,234 | Staying where the work happens |
| Waku | Standalone native Mac harness that drives agent CLIs itself | macOS, Linux, Windows | GPL-3.0 | 1,543 | Native app without a runtime dependency |
| cmux | Ghostty-based macOS terminal app with vertical tabs, notifications and a control CLI | macOS | GPL-3.0-or-later (server/relay components under BSL 1.1) | 27,470 | A terminal-first composable workspace, not a herdr console |
| Bessie | Mac client bundling herdr 0.8.0 and libghostty | macOS | Apache 2.0 | 11 | A lighter, permissive alternative client |
| Heeler | iOS client for herdr | iOS 18+ | Apache 2.0 | 430 | Attaching to agents from a phone |

The comparison that gets misstated most often is herdrm versus Waku. They look similar — both have a sidebar of agents — because herdrm borrowed Waku's sidebar idiom. But Waku drives the agent CLIs itself, normalising each one over its strongest native interface (stream-json, JSON-RPC, live events) into a provider-neutral model, with prompt checkpoints that stash the working tree under a hidden git ref so code and conversation roll back together. Waku is local by architecture: no account, no telemetry, no cloud in the middle, GPL-3.0, v0.1.19 released 2026-09-10. herdrm is explicitly "not Waku": it consumes a herdr socket and hands you the pane.

The strategic risk worth naming: since herdrm is a third-party client and the runtime ships its own TUI, an official Mac client landing inside herdr would change herdrm's calculus overnight.

That also frames the "herdr vs herdrm" question correctly. herdrm is not an alternative to herdr and it is not a competing runtime — it is the herdr Mac client. Anyone searching for a herdrm alternative because they dislike attach-based clients is really searching for a different runtime, and the honest answers there are Waku (own sessions) or a plain terminal multiplexer with no agent awareness at all.

## What actually breaks in practice, and who should install herdrm?

Four failure modes are documented rather than hypothetical.

First, status latency. Hook-based agents report instantly; screen-manifest agents lag by seconds, and a genuinely stuck agent can still render as busy. Do not use the sidebar as your only signal that a long run is healthy.

Second, remote latency. Over SSH the terminal is only as responsive as the link, and the 0.6.2–0.6.9 occlusion bug hit hardest exactly there.

Third, identity persistence is weaker than layout persistence. A kill -9 test of the runtime found the layout — panes, tabs, working directories — came back, but the registered agent record dropped from one to zero and every terminal ID changed. If your tooling keys off terminal IDs across a crash, it will break.

Fourth, the licence and the platform. It is Mac-only, and it is not free for commercial use.

Install herdrm if you already run herdr across more than one machine, want a single window over local and remote agents, and are comfortable living one step behind the runtime's releases. Stay on the herdr TUI if you work on one machine, read changelogs closely, or need a permissive licence at work — that path is Apache 2.0 and always in sync. And if you want a native Mac app that owns its own sessions rather than attaching to a runtime, Waku is the honest alternative, with a different licence and a different philosophy.

## FAQ

### Is herdrm a coding agent?

No. herdrm contains no agent loop, no model calls, and no task execution. It is a client: it reads frames from a herdr socket, draws a sidebar, and attaches your Mac to terminal panes that herdr owns. You still need the agent CLIs themselves (Claude Code, Codex, Cursor Agent, and the rest) plus the herdr runtime.

### Does herdrm work without herdr installed?

No, and this is the most common misconception. herdrm is useless without a herdr server reachable over a socket. Install herdr on the Mac and on every remote host first, verify the runtime is running, then add devices in the console. If herdr is down, the console has nothing to show.

### What macOS version does herdrm require, and how do I install it?

macOS 14 or later, universal binary for Apple Silicon and Intel. The two official install paths are `brew install owo-network/brew/herdrm` or unzipping the release into `/Applications`. There is no official herdrm website; genuine builds are signed by MOE AI LLC and notarised. A GitHub Pages lookalike once distributed Windows malware under this name, so treat any other download page as hostile.

### Can I use herdrm at work?

Not without a commercial licence. herdrm is licensed under PolyForm Noncommercial 1.0.0, which permits noncommercial use, modification, and sharing, and requires a separate licence from the maintainer for commercial use. The herdr runtime underneath is Apache 2.0, which makes the split easy to miss. Check with whoever owns licence compliance before deploying it on a company machine.

### Is herdrm safe if it starts agents with permissions bypassed?

It is as safe as the workspace you point it at. The New Agent picker enables each agent's bypass-permissions flag by default — for Claude Code that is `--dangerously-skip-permissions` — so an agent will not stop to ask before writing files or running commands. Keep that default only for scratch workspaces with no production credentials or SSH keys on the path, and turn it off for anything else.
