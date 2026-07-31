---
title: "BWB Browser MCP Server Review 2026: 30KB Browser Automation Without Bloat"
date: 2026-07-31T10:02:35+00:00
tags:
  - bwb browser
  - mcp server
  - browser automation
  - chrome devtools protocol
  - lightweight
  - termux
  - cdp
description: "BWB Browser MCP Server delivers 76KB of browser automation via raw CDP — no Playwright, no Puppeteer, no bloat. Here is the full 2026 review."
draft: false
cover:
  image: "/images/bwb-browser-mcp-server-2026.png"
  alt: "BWB Browser MCP Server Review 2026: 30KB Browser Automation Without Bloat"
  relative: false
schema: "schema-bwb-browser-mcp-server-2026"
---

## What Is BWB Browser MCP Server?

BWB Browser MCP Server is a 76KB open-source MCP (Model Context Protocol) server that gives AI agents direct browser control through raw Chrome DevTools Protocol (CDP) WebSocket connections. Created by solo developer Krish Tiwari (@krshforever), it provides 25 MCP tools including browser_act, browser_watch, and browser_diagnose — all without a single dependency on Playwright, Puppeteer, or Selenium. At just 76KB of source code, it is the smallest browser MCP server by a factor of 25x or more compared to alternatives that bundle entire browser engines.

### The 76KB Philosophy — Raw CDP, No Bloat

Every other browser MCP server in the ecosystem builds on top of high-level browser automation frameworks. Playwright MCP wraps Microsoft's Playwright. Puppeteer MCP wraps Google's Puppeteer. Each of those frameworks is itself a multi-megabyte abstraction layer over the Chrome DevTools Protocol.

BWB skips the middlemen entirely. It speaks CDP directly over WebSocket — the same protocol that Chrome DevTools itself uses. This means:

- **No Playwright dependency** — saves ~2MB of source and ~250MB of bundled Chromium
- **No Puppeteer dependency** — saves ~100MB+ of source and ~400MB of bundled Chromium
- **No Selenium dependency** — saves the entire Java runtime overhead
- **No node_modules bloat** — the entire install is under 1MB

The result is a server that installs in 5 seconds and starts in under 200ms. For AI agent developers who just need to navigate a page, click a button, or capture a screenshot, the heavyweight abstractions of Playwright and Puppeteer are unnecessary overhead.

### Who Built It and Why (The Termux Origin Story)

BWB was born from a practical constraint. Krish Tiwari, a developer in India, wanted to run browser automation on his Android phone via Termux. Every existing solution required either a cloud subscription or a desktop-class environment. Playwright MCP? Requires a full Chromium binary. Puppeteer MCP? Same problem. Browserbase? Cloud-hosted and paid.

So he built his own. BWB started as a personal tool to automate browser tasks from a phone and grew into a full MCP server with 25 tools, published to npm on July 28, 2026. The project is MIT-licensed and available at [github.com/krshforever/bwb-browser](https://github.com/krshforever/bwb-browser).

This origin story matters because it explains the design philosophy: BWB is built for environments where every kilobyte counts. It is not a corporate product with a marketing budget. It is a focused tool built by someone who needed it to work on a phone.

## Feature Deep Dive — 25 Tools That Matter

BWB ships 25 MCP tools, but three stand out as genuinely innovative features that incumbents do not offer.

### browser_act — Natural Language Browser Control

The browser_act tool accepts natural language instructions like "click the login button" or "fill in the search box with 'weather forecast'" and executes them against the current page. Unlike Playwright MCP, which requires structured selectors and explicit navigation commands, browser_act interprets intent.

This is not an LLM-powered feature — BWB does not call an external AI model. Instead, it uses the page's accessibility tree and DOM structure to map natural language to CDP commands. The result is a lightweight, zero-cost natural language interface that works entirely offline.

### browser_watch — Live Console and Network Event Capture

browser_watch is arguably BWB's most unique feature. It opens a live stream of browser events — console.log output, network requests, JavaScript errors, and DOM mutations — and delivers them to the AI agent in real time.

Playwright MCP and Puppeteer MCP do not offer this capability. Their snapshot-based approach gives the agent a static view of the page at a single moment. browser_watch turns browser automation into an event-driven experience, where the agent can react to page changes as they happen.

Practical use cases include:

- Monitoring a dashboard for data changes and alerting when a threshold is crossed
- Debugging JavaScript errors by watching console output in real time
- Capturing network traffic for API inspection during automated workflows
- Waiting for a specific DOM element to appear before taking action

### browser_diagnose — AI Agent Self-Diagnosis

When something goes wrong — a page fails to load, a selector returns empty, a click misses its target — browser_diagnose runs a diagnostic sweep of the browser state. It checks the current URL, page load status, console errors, network connectivity, and available DOM elements, then returns a structured report.

This is particularly valuable for autonomous AI agents that need to recover from errors without human intervention. Instead of crashing on a failed navigation, the agent can call browser_diagnose, understand what went wrong, and adjust its approach.

### Session Persistence — Login Once, Agent Works for Days

BWB maintains persistent browser sessions across MCP connections. An AI agent can log into a service, and the session cookies, local storage, and authentication state remain valid for subsequent calls. This enables long-running automation workflows where the agent works for hours or days without re-authenticating.

Playwright MCP and Puppeteer MCP both support session persistence, but BWB's implementation is notably simpler — it stores the CDP WebSocket URL and reconnects to the same browser context, preserving all state without serialization overhead.

### Multi-Tab Management and Realistic Fingerprinting

BWB supports multiple browser tabs within a single session, each with its own CDP connection. The agent can open a new tab, navigate to a different site, and switch between tabs without losing state in any of them.

The server also includes realistic browser fingerprinting — it sets user-agent strings, viewport dimensions, and device metrics that match real browser profiles. This is critical for sites that detect and block automated browsers.

## Size Comparison: BWB vs Playwright MCP vs Puppeteer MCP

The size difference between BWB and its competitors is not incremental — it is two to three orders of magnitude.

### Source Size: 76KB vs 2MB vs 100MB+

| Server | Source Size | Dependencies | Bundled Browser |
|--------|------------|--------------|-----------------|
| BWB Browser MCP | **76 KB** | Zero | No (uses existing Chrome) |
| Playwright MCP | ~2 MB | Playwright (~2 MB) | Chromium (~250 MB) |
| Puppeteer MCP | ~100 MB+ | Puppeteer (~100 MB+) | Chromium (~400 MB) |
| ExecuteAutomation MCP | ~29 MB | Playwright | Chromium (~400 MB) |

BWB's source code is 76KB. Playwright MCP's source is roughly 2MB — 26 times larger. Puppeteer MCP's source exceeds 100MB. And these numbers only account for source code, not the bundled browser binaries.

### Total Install: ~1MB vs ~250MB vs ~400MB

When you factor in the browser binaries that Playwright and Puppeteer download during installation, the gap becomes staggering:

| Server | Total Install Size | Install Time |
|--------|-------------------|--------------|
| BWB Browser MCP | **~1 MB** | **~5 seconds** |
| Playwright MCP | ~250 MB | 2-5 minutes |
| Puppeteer MCP | ~400 MB | 3-8 minutes |
| ExecuteAutomation MCP | ~400 MB | 3-8 minutes |

BWB assumes Chrome or Chromium is already installed on the system. If it is not, the user provides the path to an existing installation. This design choice is the single biggest factor in BWB's size advantage.

### Platform Support: Termux/Android vs Desktop-Only

| Server | Linux | macOS | Windows | Termux/Android |
|--------|-------|-------|---------|----------------|
| BWB Browser MCP | ✅ | ✅ | ✅ | **✅ (only option)** |
| Playwright MCP | ✅ | ✅ | ✅ | ❌ |
| Puppeteer MCP | ✅ | ✅ | ✅ | ❌ |
| ExecuteAutomation MCP | ✅ | ✅ | ✅ | ❌ |
| Browserbase MCP | Cloud | Cloud | Cloud | ❌ |

BWB is the only browser MCP server that runs on Termux/Android. This is not a niche feature — with over 3 billion Android devices worldwide, the ability to run browser automation from a phone opens use cases that desktop-only solutions cannot address.

## Unique Advantages Over Incumbents

### Zero Dependencies, Zero node_modules Hell

Every Node.js developer knows the pain of a 500MB node_modules directory. BWB has zero runtime dependencies. The npm package installs in seconds and produces a node_modules folder measured in kilobytes, not gigabytes.

This makes BWB ideal for:

- **CI/CD pipelines** where every second of install time adds to build costs
- **Docker containers** where image size matters
- **Edge computing environments** with limited storage
- **Serverless functions** with cold start constraints
- **Mobile devices** where storage is at a premium

### Live Event Streaming — The Killer Feature

browser_watch is the feature that most clearly differentiates BWB from every competitor. Playwright MCP gives you a snapshot. Puppeteer MCP gives you a screenshot. BWB gives you a live feed of everything happening in the browser.

For AI agents that need to monitor real-time data — stock prices, server dashboards, social media feeds, chat messages — this is transformative. The agent does not poll. It does not guess. It receives events as they happen and can respond immediately.

### Natural Language Interaction Without LLM Costs

browser_act provides natural language browser control without calling an external LLM. This means zero API costs, zero latency from network calls, and zero privacy concerns about sending page content to third-party services.

The trade-off is that browser_act is less sophisticated than an LLM-powered approach. It cannot handle complex multi-step instructions or ambiguous requests. But for the 80% of browser automation tasks — clicking buttons, filling forms, navigating pages — it works reliably and costs nothing.

### Works on a Phone — Literally

Running browser automation from a smartphone is not a gimmick. Consider these real-world use cases:

- **Field service workers** who need to automate data entry on the go
- **Penetration testers** who want a portable browser automation toolkit
- **Students** who cannot afford a laptop but have an Android phone
- **IoT and embedded systems** where a full desktop OS is not available
- **Quick automation tasks** when you are away from your desk

BWB on Termux/Android connects to Chrome for Android via USB debugging or a remote CDP endpoint. The experience is identical to desktop — all 25 tools work the same way.

## Limitations and Risks

An honest review must address BWB's significant limitations. This is a very early-stage project, and it shows.

### Early Stage — 8 Stars, 3 Days Old

At the time of this review, BWB has 8 GitHub stars and 3 forks. The npm package was published on July 28, 2026 — three days ago. Weekly downloads are 983, which is respectable for a brand-new package but minuscule compared to Playwright MCP's 35,668 stars.

The project has not been battle-tested at scale. There are no enterprise users, no security audits, and no published case studies. Bugs are likely. Edge cases are undiscovered.

### Single Developer — Bus Factor Risk

Krish Tiwari is the sole maintainer. If he loses interest, gets busy with other projects, or simply cannot keep up with issues and pull requests, the project dies. There is no company backing, no paid support, and no guarantee of long-term maintenance.

This is the classic open-source risk. It does not mean BWB is a bad project — many great tools started as solo efforts. But it does mean users should evaluate their tolerance for abandonment risk before building production workflows around it.

### Chrome/Chromium Only — No Firefox or WebKit

BWB speaks CDP, which is a Chrome-specific protocol. It does not support Firefox (which uses the Remote Protocol, a different protocol) or WebKit/Safari. If your automation needs cross-browser testing, BWB is not the right tool.

Playwright MCP supports Chromium, Firefox, and WebKit out of the box. For cross-browser workflows, Playwright MCP remains the better choice.

### No Cloud/Hosted Option Yet (Roadmap Item)

BWB is a self-hosted tool. You install it on your machine, point it at a Chrome instance, and use it locally. There is no cloud-hosted version, no managed service, and no browser pool.

The project roadmap mentions cloud hosting as a future goal, but there is no timeline. For teams that want a managed browser automation service, Browserbase MCP or Webfuse are currently the only options.

## How to Install and Configure

Getting started with BWB is straightforward.

### npm install -g bwb-browser (5 Seconds)

```bash
npm install -g bwb-browser
```

That is it. No `npx playwright install`. No downloading Chromium. No `apt-get install` dependencies. The entire install completes in under 5 seconds on a typical internet connection.

### Auto-Discovery with bwb --setup

BWB includes an auto-discovery tool that finds Chrome or Chromium installations on your system:

```bash
bwb --setup
```

This scans common installation paths, detects the Chrome version, and generates the MCP configuration file. On Termux/Android, it detects Chrome for Android via USB debugging.

### MCP Config for Claude Code, OpenCode, Cline, Cursor, and More

BWB works with any MCP-compatible client. Here is the standard configuration:

```json
{
  "mcpServers": {
    "bwb-browser": {
      "command": "bwb-browser",
      "args": ["--port", "9222"],
      "env": {}
    }
  }
}
```

This configuration works with Claude Code, OpenCode, Cline, Cursor, and any other MCP client that supports the standard MCP protocol.

## Who Should Use BWB Browser MCP Server?

### Mobile Developers and Termux Users

If you develop on an Android phone or tablet, BWB is your only option for local MCP browser automation. There is no alternative that runs on Termux.

### CI/CD Pipelines Needing Lightweight Browser Automation

If your CI pipeline installs Playwright just to take a single screenshot or run a single navigation, BWB can replace it with a 5-second install and zero browser download. For teams paying per-minute for CI runners, the savings add up quickly.

### AI Agent Developers Wanting Unique Features (browser_watch)

If you are building AI agents that need real-time browser monitoring, browser_watch is a feature you cannot get anywhere else. Playwright MCP and Puppeteer MCP do not offer live event streaming.

### Anyone Frustrated with 400MB Downloads for Simple Browser Tasks

If you have ever run `npx playwright install` and watched it download 250MB of Chromium just to click a button, BWB is for you. It is a reminder that browser automation does not have to be bloated.

## Final Verdict — Is 76KB Enough?

BWB Browser MCP Server is not a replacement for Playwright MCP. It is not trying to be. It is a focused, lightweight alternative for a specific set of use cases where size, speed, and simplicity matter more than feature breadth.

**Strengths:**
- 76KB source, ~1MB total install — smallest browser MCP server by orders of magnitude
- Zero dependencies — no Playwright, Puppeteer, or Selenium
- Unique features (browser_watch, browser_diagnose) that incumbents lack
- Termux/Android support — the only mobile browser MCP server
- MIT licensed, free and open source
- 25 MCP tools covering navigation, interaction, monitoring, and diagnostics

**Weaknesses:**
- Very early stage — 8 stars, 3 days old at time of review
- Single developer — bus factor of 1
- Chrome/Chromium only — no Firefox or WebKit
- No cloud-hosted option
- Limited community and documentation

**The bottom line:** If you need browser automation on a phone, in a CI pipeline where every megabyte counts, or with live event streaming capabilities, BWB is the best tool for the job. If you need cross-browser testing, enterprise support, or a battle-tested solution with thousands of contributors, stick with Playwright MCP.

BWB proves that browser automation does not require 400MB of dependencies. Sometimes 76KB is enough.

## Frequently Asked Questions

### Is BWB Browser MCP Server free to use?

Yes. BWB is MIT-licensed and completely free to use for personal, commercial, and educational purposes. There are no paid tiers, no usage limits, and no cloud subscription required.

### Does BWB work with Firefox or Safari?

No. BWB uses the Chrome DevTools Protocol (CDP), which is specific to Chrome and Chromium-based browsers. It does not support Firefox or Safari/WebKit. For cross-browser automation, Playwright MCP is the recommended alternative.

### Can I use BWB in production?

BWB is very early-stage (8 GitHub stars, 3 days old at the time of this review). While it works for its intended use cases, it has not been security-audited or battle-tested at scale. Evaluate your risk tolerance before depending on it for production workflows.

### How is BWB different from Playwright MCP?

BWB is 25x smaller (76KB vs ~2MB source), has zero dependencies, supports Termux/Android, and offers unique features like browser_watch (live event streaming) and browser_diagnose (self-diagnosis). Playwright MCP has 35,668 GitHub stars, cross-browser support, enterprise backing from Microsoft, and a much larger community.

### Does BWB work on Windows and macOS?

Yes. BWB works on Linux, macOS, and Windows, in addition to Termux/Android. It requires an existing Chrome or Chromium installation on any of these platforms.
