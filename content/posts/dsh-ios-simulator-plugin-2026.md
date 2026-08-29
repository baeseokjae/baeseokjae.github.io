---
title: "DeepSeek Harness iOS Simulator Plugin: Drive iOS Apps from Your Coding Agent"
date: 2026-08-29T20:32:11+00:00
tags:
  - deepseek harness
  - dsh ios simulator
  - deepseek harness ios simulator plugin
  - ios simulator agent automation
  - ai coding agents
  - semantic ui automation
description: "The DSH iOS Simulator plugin turns your coding agent into a driver of live iOS apps: simulators and real iPhones, with 22 tools including AXe UI trees, OCR taps, and SwiftUI hot reload."
draft: false
cover:
  image: "/images/dsh-ios-simulator-plugin-2026.png"
  alt: "DeepSeek Harness iOS Simulator Plugin: Drive iOS Apps from Your Coding Agent"
  relative: false
schema: "schema-dsh-ios-simulator-plugin-2026"
---

The DeepSeek Harness iOS Simulator plugin is a live, interactive iOS simulator that runs inside a DeepSeek Harness (DSH) conversation — plus your real iPhone over USB — so your coding agent can see, tap, and verify the app it just changed. It ships 22 agent tools covering devices, screenshots, semantic UI navigation, build-and-run, SwiftUI preview hot reload, processes, and backtraces. This guide explains how it works, how to install it, and how it closes the verify gap that keeps coding agents from trusting their own Swift.

## What Is the DeepSeek Harness iOS Simulator Plugin?

The DeepSeek Harness iOS Simulator plugin (repo `ZSeven-W/dsh-ios`, npm package `@zseven-w/dsh-ios`, MIT license) is a plugin that plugs a full iOS runtime into a DSH conversation. Instead of your agent building an app and guessing whether the UI works, it opens a real simulator window you can watch, reads the accessibility tree, and taps elements by label — or drives a physical iPhone over USB through WebDriverAgent.

It is one plugin inside the DeepSeek Harness platform, the open-source "Everything is a Plugin" agent framework from deepseek-ai. DSH itself is one of the most-starred AI repos on GitHub, with roughly 203,297 stars and 23,448 forks as of the plugin's active development window (mid-to-late August 2026). The iOS plugin sits alongside siblings like the Android plugin (`dsh-android`, driven through adb) and desktop plugins, all installed into the same agent conversation.

The current plugin release is `0.1.0-rc.3`, tested against DSH `0.1.1-rc.1`. It is written in TypeScript and has gathered around 266 stars and 23 forks in the days since it was created on 2026-08-19. Because it is a release candidate, expect the tool set and API to evolve as the harness ecosystem matures.

## Why Agents Need a Real iOS Simulator (The Verify Gap)

Coding agents are good at writing Swift. They are historically bad at *using* the app they wrote. The gap is simple: an agent can edit a view, but until the change is compiled, launched, rendered, and visible on a screen, it has no trustworthy signal about whether the edit actually works. This is the "verify gap," and it is exactly what the iOS Simulator plugin is built to close.

Competitor tooling calls out the same premise. LIGH (`light-ios-simulator`) describes closing the loop "write → build → run → interact → verify → fix" and notes that "coding agents can edit Swift but cannot reliably USE the app they just changed." DSH iOS attacks the identical problem: an agent that can see a running app and tap its real UI can produce evidence instead of speculation.

Without a live target, agents fall back on brittle heuristics: they inspect the code statically, reason about what the framework "should" render, and hope. With a live simulator in the conversation, the agent observes actual render output, extracts the accessibility tree, taps the element, and reads the log — a closed feedback loop that converts "I think this works" into "this demonstrably works."

## How the Plugin Drives iOS Apps (The 22 Tools)

The plugin registers 22 agent tools across device lifecycle, interaction, build, inspection, and diagnostics. Grouped by function, they cover:

- **Device lifecycle:** list devices, boot and shut down simulators
- **Screen capture:** take screenshots of the current state
- **Interaction:** tap the screen, either by coordinates or semantically
- **Build and run:** compile and launch the target app on a chosen device
- **Unified logs:** stream device logs in one place
- **UI inspection:** dump the AXe-backed accessibility tree, enumerate list and feed rows
- **Vision/OCR:** find and tap text on screen when the tree is empty or degenerate
- **Preview hot reload:** SwiftUI previews that swap edits in seconds without relaunch
- **Process and diagnostics:** process listing, backtraces, leaks, and app info

The build-and-run path is the entry point: the agent targets a device, compiles the project, installs, and launches it. From there the interaction tools take over. Because every tool returns machine-readable output — an a11y tree, a row list, a log line — the agent can make decisions and act on them in the same heartbeat rather than pausing for human help.

## Semantic UI Automation: Trees, OCR, and Taps That Aren't Guesswork

The biggest usability win in the plugin is semantic UI automation. Rather than tapping at guessed pixel coordinates — which break the moment the layout changes — the plugin drives the UI through the accessibility tree.

- `ios_sim_ui_tree` dumps an AXe-backed accessibility tree of the current screen.
- `ios_sim_tap_element` taps an element by its label or accessibility identifier.
- `ios_sim_find_text` runs OCR over the screen, used when the accessibility tree is empty or degenerate (for example, custom-drawn or GPU-rendered content).
- `ios_sim_tap_text` taps the matched text once found.

This design means the agent interacts by meaning ("tap the button labeled Submit") rather than by coordinates ("tap pixel 314,502"). Identity- and text-based taps are dramatically more durable across layout changes, device sizes, and orientation shifts.

For long, scrollable surfaces — feeds, inboxes, settings lists — the plugin adds `ios_sim_ui_rows`, which flattens a deep accessibility snapshot into indexed rows, and `ios_sim_tap_row`, which taps a row using relative coordinates and then verifies the tap landed by checking that the element's expected counter changed by ±1. That verification step is what separates reliable automation from fire-and-forget taps.

## Driving a Real iPhone Over USB with WebDriverAgent

The simulator is the easy path; the plugin also reaches physical devices. Via `ios_real_start_wda`, it builds and launches WebDriverAgent (the Appium control server) on a connected iPhone, then tunnels two ports over loopback `usbmux`: one for REST control and one for the MJPEG screen stream. The result is that the agent drives your actual device from the same conversation it uses for the simulator.

Real-device testing matters because the simulator does not replicate everything: sensors, network behavior, App Store signing, push notifications, and certain performance envelopes only exist on hardware. But real devices bring real maintenance costs, and the plugin documents them honestly. WebDriverAgent's free-team signing profiles expire after 7 days, at which point you must re-run `ios_real_start_wda` to recover from a "profile-expired" status. Every real-account tap is gated by identify-before-tap rules, so the agent confirms what it is about to touch rather than blindly interacting with production data.

## SwiftUI Preview Hot Reload for Fast Verify-Fix Loops

One of the strongest features for iteration speed is `ios_sim_preview`. Instead of rebuilding and relaunching the entire app to test a change, the plugin generates a disposable host app, builds the changed SwiftUI previews as a dynamic library (dylib), and hot-swaps the edits into the running simulator in roughly 2 to 5 seconds.

This transforms the verify-fix loop. A full build-and-launch cycle can take a developer tens of seconds or minutes; preview hot reload collapses it to a few seconds. An agent that can iterate in 2–5 seconds per change can afford to try multiple approaches, observe each result, and converge on a working UI quickly — the kind of tight loop that makes autonomous UI work feasible at all.

## Security Model: Loopback-Only Transport and Signed, Expiring URLs

Giving an agent the ability to touch your device raises an obvious security question, and the plugin answers it with a defense-in-depth design.

- **Loopback-only transport:** the streaming engine (`serve-sim`, by Expo's Evan Bacon, Apache-2.0) binds to `127.0.0.1` in a dedicated port range and enforces loopback Host and Fetch-Metadata checks.
- **Signed, expiring URLs:** visual bytes reach the browser UI only through HMAC-signed, expiring URLs under the `/_/_dsh/dsh-ios/*` routes — never as raw image blocks — and the capability URLs expire within 10 minutes.
- **Gate on real devices:** every real-account tap is gated by identify-before-tap rules.

This trades convenience for a constrained attack surface: nothing is exposed beyond the local loopback, nothing is addressable without a short-lived signed capability, and physical-device automation requires explicit confirmation before each tap. For an agent tool that manipulates a device, that is a defensible posture.

## Troubleshooting Common Issues and Coded Error Statuses

Early-version plugins are expected to break in expected ways. The plugin exposes several coded statuses worth knowing:

- **profile-expired:** the WebDriverAgent signing profile passed its 7-day lifetime; re-run `ios_real_start_wda`.
- **Idle stream stopping:** with zero consumers, the simulator MJPEG stream stops after 5 minutes and restarts automatically on the next tool call or panel open — this is idle management, not a crash.
- **Crashed streams:** a crashed stream restarts in about 5 seconds, so a brief video interruption is normal.
- **Empty/degenerate accessibility tree:** if OCR finds and taps text that the tree cannot see, that is the expected fallback path, not a failure of the plugin.

When something looks stuck, the fastest diagnostic is to check screenshots (`ios_sim_screenshot`), read the unified log, and inspect the process list — the three pieces of evidence the plugin is designed to surface.

## How It Compares to LIGH and Other iOS Agent Tools

DSH iOS is not alone in attacking the verify gap, but it takes a distinctly different shape than LIGH (`light-ios-simulator`, also by a third party) and other agent iOS tools. The table below summarizes the differences.

| **Aspect** | **DSH iOS Simulator** | **LIGH** |
|---|---|---|
| Runtime | DSH conversation plugin (TypeScript, MIT) | Host-side control plane (`ligh_*` MCP tools) |
| Device target | iOS Simulator + real iPhone over USB (WebDriverAgent) | Simulator + physical Expo debug builds |
| Interaction model | 22 agent tools; AXe a11y tree, OCR tap, row actions | Feel IR (structured interaction frame), Autopilot, TRAIL repair |
| UI semantics | AXe tree + OCR text taps | Structured interaction frame, not screenshot dump |
| Hot reload | SwiftUI preview dylib hot-swap (~2–5s) | N/A (repair engine does LLM-patched fixes) |
| Ecosystem | Siblings for Android (`dsh-android`) and desktop | Standalone MCP control plane |

Both projects agree on the core claim: agents cannot be trusted to fix Swift UI unless they can verify it. DSH iOS leans on the plugin model and a 22-tool semantic interaction surface; LIGH leans on an interaction frame, an Autopilot mode, and a TRAIL repair engine that classifies failures, localizes them, and applies a bounded set of LLM patches.

The ecosystem trend behind both is worth noting. DeepSeek Harness's plugin architecture ("Everything is a Plugin") has produced modular extensions — a VSCode client, an office plugin, an LLM-as-a-Verifier plugin, and now this mobile plugin. With iOS and Android plugins in place, a single agent conversation can drive both mobile platforms, using adb on the Android side and WebDriverAgent/the simulator on the Apple side.

## Getting Started: Install, Configure, and Add to Your DeepSeek Harness

Because DSH is plugin-based, adding iOS driving capability is a matter of installing one plugin and configuring it, rather than adopting a separate platform.

1. **Install the plugin** from npm: `@zseven-w/dsh-ios` (current release `0.1.0-rc.3`). Confirm your DSH version matches the tested pairing, `0.1.1-rc.1`.
2. **Add the plugin** to your DSH conversation so its 22 tools and presentation panel are registered.
3. **Choose your target.** Boot a simulator with the device tools, or connect a real iPhone over USB and run `ios_real_start_wda` to build and launch WebDriverAgent.
4. **Build and launch** your app on the selected device.
5. **Drive the UI semantically.** Use `ios_sim_ui_tree` / `ios_sim_tap_element` for accessibility-aware taps, or `ios_sim_find_text` / `ios_sim_tap_text` when OCR is needed.
6. **Iterate fast** with `ios_sim_preview` for SwiftUI hot reload.

Real-device users should plan around the 7-day signing-profile cycle and re-run `ios_real_start_wda` when they hit `profile-expired`. Everyone should treat the 5-minute idle stream stop and ~5-second crash restart as normal behavior, not defects.

## FAQ: DeepSeek Harness iOS Simulator Plugin

**Is DSH iOS Simulator a separate app, or a plugin for DeepSeek Harness?**
It is a plugin. You install `@zseven-w/dsh-ios` into an existing DeepSeek Harness conversation, where it registers 22 agent tools and a live simulator presentation panel.

**Does it only work with simulators, or real iPhones too?**
Both. The simulator is the primary target, and `ios_real_start_wda` extends it to a physical iPhone over USB by building WebDriverAgent and tunneling control and screen ports over loopback usbmux — with identify-before-tap gating on real accounts.

**How does the agent tap the right UI element reliably?**
Through the accessibility tree. `ios_sim_ui_tree` dumps the AXe-backed tree, `ios_sim_tap_element` taps by label or identifier, and OCR text taps (`ios_sim_find_text`, `ios_sim_tap_text`) serve as the fallback when the tree is empty or degenerate. It targets meaning, not guessed coordinates.

**What is SwiftUI preview hot reload, and why does it matter?**
`ios_sim_preview` builds changed SwiftUI previews as a dylib and hot-swaps them into the running simulator in roughly 2–5 seconds without relaunching the app, collapsing the verify-fix loop so agents can iterate quickly.

**What security protections does it have for a real device?**
The streaming engine binds loopback-only in a dedicated port range, visual bytes reach the UI only through HMAC-signed expiring URLs (10-minute capability lifetime), and every real-account tap is gated by identify-before-tap rules.

**Is the plugin production-ready?**
It is at `0.1.0-rc.3` — a release candidate tested against DSH `0.1.1-rc.1`. Expect the tool set and API to evolve. Known operational notes include a 7-day WebDriverAgent signing-profile lifetime and idle stream management that stops an unused stream after 5 minutes.
