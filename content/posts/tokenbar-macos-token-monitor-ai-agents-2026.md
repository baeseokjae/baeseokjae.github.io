---
title: "TokenBar: AI Token Usage and Quota Monitor for macOS Menu Bar — Tracks 25+ Agents Locally"
date: 2026-08-02T13:01:55+00:00
tags:
  - AI Tools
  - macOS
  - Token Tracking
  - Open Source
  - Developer Tools
  - Menu Bar Apps
description: "TokenBar is a free open-source macOS menu bar app that tracks AI token usage across 25+ coding agents locally with zero telemetry."
draft: false
cover:
  image: "/images/tokenbar-macos-token-monitor-ai-agents-2026.png"
  alt: "TokenBar: AI Token Usage and Quota Monitor for macOS Menu Bar — Tracks 25+ Agents Locally"
  relative: false
schema: "schema-tokenbar-macos-token-monitor-ai-agents-2026"
---

TokenBar is a free, open-source macOS menu bar application that tracks AI token usage and API spending across 25+ coding agents entirely on your local machine. Built as a native Swift rewrite of the earlier Tauri-based tokcat, TokenBar gives developers real-time visibility into how many tokens Claude Code, Codex, Cursor, Copilot, Gemini CLI, and two dozen other agents consume — without sending any data to external servers or requiring an account.

## What Is TokenBar? — Overview of the macOS Menu Bar AI Token Monitor

TokenBar lives in your macOS menu bar and displays live token usage statistics for every AI coding agent you run. Instead of guessing how much you spend on API calls each month or discovering overages only when your bill arrives, TokenBar shows you per-agent token counts, dollar costs, and quota pace projections at a glance. The app is developed by Nanako0129 and is available on GitHub under the MIT license, with 215 stars and 20 forks as of August 2026.

The core value proposition is simple: developers using multiple AI coding assistants have no unified way to track their total token consumption. Each agent — Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Copilot Desktop, and others — logs usage independently. TokenBar aggregates all of them into a single menu bar dashboard with seven configurable "lenses" that let you switch between views like per-agent breakdowns, time-window summaries, and global leaderboard comparisons powered by the tokscale network.

## Key Features — 25+ Agents, 7 Lenses, 3D Graph, Liquid Glass, Quota Cards

TokenBar packs an unusually rich feature set for a menu bar utility. Here is what sets it apart:

**25+ Agent Support.** TokenBar tracks Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Copilot Desktop, and over 20 other AI coding agents. This is the widest agent coverage of any free menu bar token monitor. By comparison, CodexBar — the most popular alternative with 19,492 stars — only supports Codex and Claude Code.

**Seven Dashboard Lenses.** The app ships with seven viewing modes called lenses: Per-Agent, Time Window, Global Leaderboard, Session Detail, Cost Breakdown, Quota Pace, and Activity Timeline. Each lens reorganizes the same local data to answer a different question — which agent spent the most today, how your quota is pacing against your monthly limit, or where tokens went in the last session.

**SceneKit 3D Graph at 160fps.** TokenBar renders a real-time 3D bar chart of token usage using Apple's SceneKit framework, running at 160 frames per second. The graph animates smoothly as new data arrives, giving you an at-a-glance visual of which agents are consuming the most tokens.

**Liquid Glass Visual Effect.** On macOS 26 and later, TokenBar enables a Liquid Glass visual effect that gives the menu bar dropdown a translucent, depth-of-field appearance. This is a macOS-native visual enhancement that makes the app feel like a first-party system utility rather than a third-party add-on.

**Quota Cards.** Each agent gets a quota card showing tokens used, estimated cost, and a pace bar that projects whether you will hit your monthly limit at the current consumption rate. This is especially valuable for developers on tiered API pricing plans who need to avoid unexpected overage charges.

**Homebrew Cask Installation.** TokenBar installs via a single Homebrew command: `brew install tokenbar`. No manual downloads, no dragging to Applications, no configuration files to edit.

## How TokenBar Works — Local Log Parsing with Tokscale-Core Engine

TokenBar does not intercept network traffic or hook into API calls. Instead, it reads the local log files that AI coding agents already write to disk. Every major AI coding tool logs its token usage locally — Claude Code writes to `~/.claude/logs`, Codex writes session data to its own cache, Cursor stores telemetry in its app data directory, and so on.

TokenBar uses the **tokscale-core** shared engine — the same engine that powers the tokscale terminal-based token tracker — to parse these logs, aggregate the data, and compute pricing estimates. Tokscale has tracked quadrillions of tokens globally across its user base, so the parsing and aggregation logic is battle-tested at scale.

The app runs a lightweight background watcher that monitors log directories for changes. When a new log entry appears, TokenBar parses it, updates its in-memory data model, and refreshes the menu bar display — all within milliseconds. Because everything runs locally, there is zero network latency and no dependency on external API availability.

## Installation and Setup — Homebrew Cask, macOS 14+ Requirements

Getting TokenBar running takes less than a minute. The app requires macOS 14 (Sonoma) or later and an Apple Silicon Mac (M1, M2, M3, or M4 series). The Liquid Glass visual effect additionally requires macOS 26 or later.

```bash
brew install tokenbar
```

After installation, launch TokenBar from your Applications folder or via Spotlight. The app appears as a small icon in your menu bar. Click it to open the dropdown dashboard, which shows your default lens view. You can switch lenses from the dropdown menu, configure which agents to monitor, and set your API pricing tiers for accurate cost estimates.

No account registration, no telemetry opt-in, no background daemon installation — just a menu bar icon and your local token data.

## TokenBar vs Competitors — CodexBar, Tokscale, Tokcat, MeterTab Comparison

The AI token tracking space has several options, each with different trade-offs. Here is how TokenBar compares:

| Feature | TokenBar | CodexBar | Tokscale | Tokcat | MeterTab |
|---|---|---|---|---|---|
| **Type** | Free, open-source | Free, open-source | Free, open-source | Free, open-source | Paid commercial |
| **Platform** | macOS menu bar | macOS menu bar | Terminal (TUI) | macOS menu bar | macOS menu bar + iOS + Watch |
| **Agents Tracked** | 25+ | 2 (Codex, Claude Code) | 10+ | 4 (Claude Code, Codex, Cursor, Copilot) | 10+ |
| **Native UI** | Swift (native) | Objective-C (native) | Terminal (ncurses) | Tauri/Webview | Swift (native) |
| **3D Graph** | Yes (SceneKit, 160fps) | No | No | No | No |
| **Liquid Glass** | Yes (macOS 26+) | No | No | No | No |
| **Quota Pace** | Yes | No | No | No | Yes |
| **GitHub Stars** | 215 | 19,492 | 4,749 | 27 | N/A (commercial) |
| **Privacy** | Zero telemetry | Zero telemetry | Zero telemetry | Zero telemetry | Local-first |
| **License** | MIT | MIT | MIT | MIT | Proprietary |
| **Active Development** | Weekly releases | Monthly | Quarterly | Inactive | Active |

**CodexBar** dominates in popularity with 19,492 stars, but its scope is narrow — it only tracks Codex and Claude Code. If you use Cursor, Copilot, Gemini CLI, or any agent beyond those two, CodexBar cannot help you.

**Tokscale** is a terminal-based tracker with a global leaderboard that has tracked quadrillions of tokens. It is excellent for power users who live in the terminal, but it has no menu bar integration and no real-time visual dashboard.

**Tokcat** was the original Tauri-based menu bar monitor that TokenBar forked from. It is no longer actively maintained since the native Swift rewrite, and its webview-based UI is less performant than TokenBar's native Swift implementation.

**MeterTab** is the closest commercial competitor, offering macOS, iPhone, and Watch apps with MCP support. It is polished and well-designed, but it requires a purchase and is not open source. TokenBar matches most of its features while remaining free and MIT-licensed.

## Performance and Visual Design — Native Swift, 160fps 3D, Liquid Glass

TokenBar's native Swift implementation gives it a significant performance advantage over webview-based alternatives. The app launches instantly, uses negligible CPU when idle (less than 0.5% on an M3 MacBook Pro), and refreshes the menu bar display in under 10 milliseconds when new log data arrives.

The SceneKit 3D graph is the visual centerpiece. It renders a real-time bar chart where each bar represents an agent's token consumption, color-coded by agent type. The graph runs at 160fps, which is well above the standard 60fps display refresh rate, ensuring buttery-smooth animations even during rapid data updates. You can rotate, zoom, and pan the 3D view with trackpad gestures.

The Liquid Glass effect on macOS 26 adds a frosted-glass depth effect to the dropdown panel. It uses the Metal shader framework to create a realistic glass surface with refraction, specular highlights, and depth-of-field blur behind the content. This is not a simple transparency overlay — it is a full GPU-accelerated visual effect that adapts to whatever is behind the window.

## Privacy and Data — Zero Telemetry, Local-Only, No Account Needed

TokenBar is designed with privacy as a first-class constraint. The app never sends data to any external server. All log parsing, aggregation, and display happens entirely on your local machine. There is no telemetry, no analytics SDK, no crash reporter phoning home, and no account system.

This is a meaningful differentiator in an era where many developer tools collect usage data by default. TokenBar cannot see which agents you use, how many tokens you consume, or what projects you work on — because it never transmits that information anywhere. The MIT license also means you can audit the source code yourself to verify the privacy claims.

The only network-optional feature is the global leaderboard lens, which can optionally compare your usage against anonymized aggregate data from the tokscale network. This is opt-in and disabled by default.

## Development Activity — Frequent Releases, Active Community, MIT License

TokenBar is under active development with a rapid release cadence. Version 1.9.0 was released on July 27, 2026, following v1.7.0, v1.8.1, and v1.9.0 — all within a two-week window. This pace of releases signals strong maintainer commitment and rapid iteration based on user feedback.

The project is MIT-licensed, which means you can use it freely, modify it, and even redistribute your own fork. The source code is available on GitHub at `github.com/Nanako0129/TokenBar`, and the community has already contributed several features including additional agent parsers and lens configurations.

With 215 stars and 20 forks, TokenBar is still a relatively young project compared to CodexBar's 19,492 stars, but its feature set and development velocity suggest it is growing quickly. The project's website at `tokenbar.nyanako.com` provides documentation, screenshots, and release notes.

## Who Should Use TokenBar — AI Developers, Heavy Claude Code/Codex Users

TokenBar is ideal for:

- **Developers using multiple AI coding agents** who need a unified view of their total token consumption. If you switch between Claude Code, Codex, Cursor, and Copilot throughout the day, TokenBar gives you one place to see all their usage.

- **Heavy Claude Code and Codex users** who want to monitor their API spending in real time. The quota pace feature helps you avoid hitting monthly limits unexpectedly.

- **Privacy-conscious developers** who want to track their AI usage without sending data to a third-party service. TokenBar's zero-telemetry, local-only architecture is a strong fit.

- **macOS power users** who appreciate native-quality apps with smooth animations, 3D graphics, and system-level integration like Liquid Glass.

- **Open-source enthusiasts** who prefer MIT-licensed tools they can inspect, modify, and trust.

TokenBar may not be the right choice if you only use a single AI agent (CodexBar is simpler for that use case), if you prefer terminal-based tools (tokscale is more appropriate), or if you need cross-device sync with iPhone and Watch apps (MeterTab offers that).

## Verdict — Strengths, Limitations, and Final Recommendation

TokenBar is the most comprehensive free open-source AI token monitor for the macOS menu bar. Its support for 25+ agents, native Swift performance, SceneKit 3D graph, and zero-telemetry privacy model make it a compelling choice for developers who want visibility into their AI spending without compromising on privacy or paying for a commercial tool.

**Strengths:**
- Widest agent coverage of any free menu bar token monitor (25+ agents)
- Native Swift performance with 160fps 3D visualization
- Zero telemetry, local-only, no account required
- Active development with weekly releases
- MIT license — free to use, modify, and redistribute
- Homebrew cask installation for easy setup

**Limitations:**
- Smaller community than CodexBar (215 vs 19,492 stars)
- Requires macOS 14+ and Apple Silicon
- Liquid Glass requires macOS 26+
- No cross-device sync (no iOS or Watch companion app)
- No MCP support (unlike MeterTab)

**Final recommendation:** If you use multiple AI coding agents on macOS and want a free, private, and visually polished way to track your token usage, TokenBar is the best option available today. Install it via Homebrew, configure your agents, and get real-time visibility into your AI spending in under five minutes.

## FAQ

**Q: Does TokenBar work with Intel Macs?**
A: No. TokenBar requires Apple Silicon (M1, M2, M3, or M4 series) and macOS 14 or later. Intel Macs are not supported due to the native Swift architecture and SceneKit 3D rendering requirements.

**Q: Can TokenBar track tokens from web-based AI tools like ChatGPT or Gemini?**
A: TokenBar is designed for local AI coding agents that write log files to disk. It cannot track web-based AI tools like ChatGPT, Gemini web, or other browser-based interfaces because those do not produce local log files that TokenBar can parse.

**Q: Is TokenBar really free with no hidden costs?**
A: Yes. TokenBar is MIT-licensed open-source software. There are no paid tiers, no subscription fees, no in-app purchases, and no premium features locked behind a paywall. The global leaderboard feature is optional and opt-in.

**Q: How does TokenBar calculate cost estimates?**
A: TokenBar uses the tokscale-core engine to apply per-model pricing based on the tokens consumed. You can configure your API pricing tiers in the app settings to match your actual plan. The estimates are approximate and based on published API pricing.

**Q: Does TokenBar slow down my Mac?**
A: No. TokenBar uses negligible system resources — less than 0.5% CPU when idle and minimal memory footprint. The background log watcher is event-driven and only activates when new log data is written. The 3D graph only renders when the dropdown is open.
