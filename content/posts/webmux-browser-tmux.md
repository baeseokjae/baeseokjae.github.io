---
title: "WebMux Review: Like Tmux, but for the Browser — a Persistent Web Terminal Workspace"
date: 2026-09-01T10:02:00+00:00
tags:
  - webmux
  - web terminal
  - tmux
  - browser terminal multiplexer
  - ssh
  - vnc
  - rdp
  - self-hosted
description: "WebMux is a self-hosted browser terminal multiplexer that tiles persistent SSH, mosh, VNC, and RDP sessions in one web workspace — like tmux, but for the browser."
draft: false
cover:
  image: "/images/webmux-browser-tmux.png"
  alt: "WebMux: Like Tmux, but for the Browser"
  relative: false
schema: "schema-webmux-browser-tmux"
---

WebMux is a self-hosted, browser-based remote workspace that tiles persistent SSH, mosh, VNC, and RDP sessions into a single scrollable web interface — effectively "tmux, but for the browser." It started as a shared jump-box wall of terminals and has grown into a full multi-session terminal and desktop workspace with multi-user accounts, auto-reconnect, and OS service integration.

## What Is WebMux?

WebMux is an open-source TypeScript application that turns your browser into a persistent remote workspace. Instead of running a single terminal in a web page the way tools like ttyd or gotty do, WebMux gives you a 2D tiled grid of sessions — SSH terminals, mosh connections, and even VNC or RDP desktop views — all living in one interface that survives browser closes and server reboots.

The project was created on 2026-03-07 and is actively maintained, with its latest update on 2026-09-01. As of that date it holds 45 GitHub stars, 7 forks, and a single open issue on the `jordanhubbard/webmux` repository. It requires Node.js 20 or newer and an OpenSSH client, with optional support for sshpass, mosh, VNC targets, and Apache Guacamole's guacd for RDP.

## Why "Tmux, but for the Browser" — the Jump-Box Problem

The tagline exists for a reason: WebMux solves the jump-box problem. If you administer remote servers, you have likely SSH'd into a jump box, started a tmux session, and kept a wall of terminals open so your work survives disconnects. WebMux moves that entire pattern into the browser.

The core idea is a shared, scrollable wall of persistent SSH and mosh terminals. Rather than juggling multiple terminal windows or relying on a single tmux session on one host, you get a visual grid where every session is a tile you can add, resize, and cycle through. This is the "why" that skeptics on Hacker News said was unclear — and it is worth spelling out: WebMux is for people who live on remote machines and want their terminal workspace to be as persistent and organized as a desktop window manager.

## Core Features: Tiled Terminal Workspace

The heart of WebMux is its 2D tiled terminal workspace, built on a scrollable CSS Grid. You start with a blank grid and click the "+" placeholders to add a session directly to the right of or below any existing tile. This gives you a window-manager-like layout without needing a window manager.

Each terminal tile uses xterm.js for full terminal emulation, which means you get 256-color support, clickable links, and a 5,000-line scrollback buffer. For transport, WebMux supports both SSH and mosh through node-pty, with keepalive and auto-reconnect built in. That combination matters: mosh handles flaky connections gracefully, while SSH keepalive prevents idle sessions from dropping.

Beyond the grid, WebMux includes a minimap, a dock for minimized sessions, and keyboard shortcuts to cycle between terminals with Ctrl+Shift+< and Ctrl+Shift+>. If you need to send the same input to every session at once, the "Type to All" broadcast mode does exactly that.

## Beyond Terminals: VNC and RDP Desktop Sessions

Where WebMux separates itself from single-purpose terminal tools is its remote-desktop layer. In addition to the terminal workspace, it provides a second tiled workspace for VNC and RDP sessions, with fullscreen viewing. This means you can manage a headless Linux box's terminal and a Windows machine's desktop from the same browser tab.

This is a meaningful differentiator. ttyd and gotty are strictly terminal-sharing tools — they expose a shell in the browser and stop there. WebMux unifies terminal (SSH/mosh) and desktop (VNC/RDP) sessions in one interface, which makes it a more complete remote-lab or remote-administration tool rather than just a terminal viewer.

## Persistence and Auto-Reconnect

Persistence is arguably WebMux's killer feature. Sessions are not tied to a browser tab — they survive browser closes, and they survive server reboots. When the server comes back up, WebMux auto-reconnects to your sessions on startup.

For anyone who has lost work because a laptop closed or a network dropped mid-command, this is the difference between a toy and a tool. Combined with mosh's resilience and SSH keepalive, WebMux is designed so that your remote workspace is always where you left it.

## Multi-User, Multi-Viewer, and Type-to-All

WebMux is not just a single-user tool. It supports multi-user accounts with Argon2id password hashing, and it offers multi-viewer presence: multiple people can watch the same session, with click-to-focus keyboard control so the active viewer can type. The "Type to All" broadcast mode extends this to every session at once.

This makes WebMux useful for pair debugging, team demos, or training scenarios where an operator needs to show a remote session to colleagues. The presence model — where focus is explicit and clickable — avoids the chaos of multiple people typing into the same terminal at once.

## Security: Argon2id, JWT, and Trusted Mode

WebMux ships two security modes. The first is local auth, which combines Argon2id password hashing with JWT tokens and HTTPS. Argon2id is the memory-hard password-hashing function recommended by OWASP, so stored credentials are resistant to GPU-based brute force. JWT handles session authentication, and HTTPS protects traffic in transit.

The second mode is a "trusted" mode intended for isolated networks, where you can skip the full auth stack because the network itself is trusted. WebMux also maintains an append-only JSONL audit log covering logins and session lifecycle events, which is valuable for compliance and for tracing who accessed what and when.

## Installation and OS Service Integration

WebMux is designed to be a drop-in self-hosted tool. It installs as an OS service on all three major platforms: launchd on macOS, systemd on Linux, and the Windows Service Control Manager on Windows. Configuration lives in a YAML file under `~/.config/webmux/`.

The optional tmux-backed agent views are disabled by default, so you can keep the surface area small if you do not need them. The dependency footprint is modest: Node.js 20+, an OpenSSH client, and optional extras (sshpass, mosh, a VNC target, and Apache Guacamole's guacd for RDP).

## WebMux vs ttyd vs gotty: How It Compares

To understand where WebMux fits, it helps to compare it against the established "terminal in the browser" tools.

| Feature | WebMux | ttyd | gotty |
|---|---|---|---|
| GitHub stars (2026-09-01) | 45 | 12,288 | 19,548 |
| Language | TypeScript | C | Go |
| Tiled multi-session workspace | Yes | No | No |
| Persistent sessions across reboots | Yes | No | No |
| VNC / RDP desktop sessions | Yes | No | No |
| Multi-user accounts | Yes | No | No |
| Multi-viewer presence | Yes | No | No |
| OS service integration | launchd / systemd / Windows SCM | systemd / others | systemd / others |

The star counts tell the real story: ttyd and gotty are mature, widely adopted single-purpose tools. WebMux is young and small by comparison. But it targets a different problem. ttyd and gotty answer "how do I share one terminal in a browser?" WebMux answers "how do I run a persistent, multi-session, terminal-and-desktop workspace in a browser?" If you only need to expose a single shell, ttyd or gotty is the pragmatic choice. If you need a persistent jump-box workspace with tiling, desktop sessions, and multi-user presence, WebMux is the only one of the three that fits.

## What the Community Is Saying (HN Skepticism)

WebMux's Hacker News Show post reached 26 points, and the discussion surfaced two honest critiques. The first was that the README lacked a screenshot or demo link, making it hard to judge the tool at a glance. The second was more fundamental: one commenter wrote, "I genuinely don't understand what problem this solves. Running on operating systems that can run web browsers but not terminal emulators?"

That skepticism is fair, and it points to a documentation gap rather than a product gap. The use case — a persistent remote jump-box workspace — is real, but it needs to be explained clearly to win over people who have never needed one. The author's background as a long-time FreeBSD user since 1997 lends credibility to the project's focus on persistent remote sessions, a workflow that is second nature to veteran sysadmins but unfamiliar to many.

## Who Should Use WebMux

WebMux is a strong fit for a few specific profiles. Remote sysadmins and SREs who live on jump boxes will appreciate a persistent, tiled wall of SSH and mosh sessions that survives disconnects. Teams that need to share a remote session for pair debugging or demos will benefit from multi-viewer presence and Type-to-All. Anyone managing a mix of headless Linux servers and Windows or VNC-based desktops will value having terminal and desktop sessions in one browser tab.

It is less suited to users who just want to expose a single shell to the web — for that, ttyd or gotty is simpler and far more battle-tested. And because it is young (created in March 2026) with a small community, you should expect to self-support and watch the project's trajectory before betting critical infrastructure on it.

## Verdict: Is WebMux Worth It?

WebMux is a promising answer to a real problem: persistent, multi-session remote workspaces in the browser. Its tiled terminal grid, VNC/RDP desktop layer, auto-reconnect, and multi-user presence are genuinely differentiated from ttyd and gotty, and its security posture (Argon2id, JWT, HTTPS, audit log) is thoughtful.

The trade-offs are maturity and adoption. With 45 stars and a single maintainer's roadmap, it is early-stage software. If you need a persistent jump-box workspace today and are comfortable self-hosting and self-supporting, WebMux is worth a serious look. If you need a proven, single-terminal web share, stick with the established tools. For the specific niche it targets, WebMux is the most complete option available.

## FAQ

**What is WebMux?**
WebMux is a self-hosted, browser-based remote workspace that tiles persistent SSH, mosh, VNC, and RDP sessions into a single scrollable web interface — effectively "tmux, but for the browser."

**How is WebMux different from ttyd or gotty?**
ttyd and gotty expose a single terminal in the browser. WebMux adds a tiled multi-session workspace, persistent sessions that survive reboots, VNC/RDP desktop support, and multi-user accounts.

**Does WebMux keep my sessions alive if I close the browser?**
Yes. Sessions persist across browser closes and server reboots, and WebMux auto-reconnects to them on startup.

**What do I need to run WebMux?**
Node.js 20 or newer and an OpenSSH client. Optional dependencies include sshpass, mosh, a VNC target, and Apache Guacamole's guacd for RDP support.

**Is WebMux secure?**
It offers two modes: local auth with Argon2id password hashing, JWT, and HTTPS, plus a trusted mode for isolated networks. It also maintains an append-only JSONL audit log of logins and session lifecycle events.
