---
title: 'Building a Native App for Coding Agents in Rust and GPUI: A rust coding agent gui How-To'
date: 2026-10-01T07:34:23+00:00
tags:
- rust coding agent gui
- gpui
- gpui-component
- build desktop app rust
- native app coding agents
- zed ui framework
description: "Build a rust coding agent gui with GPUI: the dependency-channel trap, streaming without repaint storms, PTY panes, JSON-RPC control, and packaging."
draft: false
cover:
  image: "/images/native-app-for-coding-agents-rust-gpui.png"
  alt: "Building a Native App for Coding Agents in Rust and GPUI"
  relative: false
schema: "schema-native-app-for-coding-agents-rust-gpui"
---

Build a native coding-agent GUI in Rust by pairing Zed's GPU-accelerated GPUI framework with Longbridge's `gpui-component` kit, keeping both on the same dependency channel, and driving every update as an event rather than a polling timer.

## Why Build a Native GUI for Coding Agents in Rust and GPUI?

Because the interesting part of an agent app is not the chat bubble — it is the input path, the process boundary, and the frame budget. GPUI hands you all three as explicit primitives instead of hiding them behind a webview. The counter-argument is equally real: GPUI is pre-1.0, its dependency channels are genuinely confusing, and its first build compiles a graphics stack from source. This guide is the build path that currently does not exist as a single document — the popular GPUI tutorials stop at a static Linear-lookalike dashboard, and the best agent-specific write-up (Paneflow's post-mortem) is an architecture essay rather than a reproducible how-to.

### Is "native" actually worth it over Electron or Tauri?

The honest answer in 2026 is that the reason to go native is *control*, not megabytes. Paneflow — a GPUI terminal workspace for running Claude Code, Codex, and OpenCode side by side — abandoned a working Tauri prototype not because of memory, but because a webview could not give it raw key chords, clean IME behaviour, and inter-pane focus without a JavaScript round-trip ([post-mortem](https://dev.to/arthurj-dev/building-a-native-terminal-for-ai-coding-agents-in-rust-gpui-2bg4)). Its stated lesson: "when a framework asks you to work around its own abstraction for two basic features, you're building against the framework, not with it. Pivot."

Electron is rejected first in almost every one of these projects, and the reason is structural: an agent surface streams tokens continuously, repaints a terminal grid at 60–120fps, and must never drop a keystroke. That is a rendering workload, not a document workload.

### What do the shipping apps actually build?

Look at what exists as of October 2026:

| App | What it is | Framework evidence |
| --- | --- | --- |
| Zed | Reference implementation, 91,149 stars, 10,863 forks, v1.22.0 released 2026-09-30 | GPUI (it *is* GPUI) |
| Paneflow | Native terminal for Claude Code / Codex / OpenCode; 83 stars, GPL-3.0 | GPUI + `alacritty_terminal` |
| Waku | One agent-neutral timeline, git-ref checkpoint/rewind, Sparkle updates on macOS | Native Rust + GPUI (Show HN 2026-08-16, 39 points) |
| muxel | GPUI multi-agent multiplexer: tiled panes, worktrees, live agent status, scheduled runs, SSH | GPUI, GPL-3.0, first commit 2026-06-24 |
| code-assistant (stippi) | LLM coding assistant with GPUI GUI, TUI, and MCP/ACP modes; 182 stars, MIT | GPUI |
| deck | ~700-line starter app with a decision-log `LEARNINGS.md` | GPUI + gpui-component |

The pattern is general, not terminal-only: adjacent GPUI apps include zedis (Redis GUI, 2,120 stars), disktree (disk treemap, 2,050 stars), and Loungy (launcher, 1,733 stars).

## What Are the Prerequisites?

You need a recent Rust stable, a working GPU stack, and patience for one long first build.

- **Rust:** gpui HEAD uses just-stabilized standard-library APIs (for example `cold_path`), so an older toolchain fails. Zed pins Rust 1.95.0; Paneflow pins 1.96.1. Both do it through `rust-toolchain.toml` — copy that habit.
- **GPU backend:** macOS uses Metal (Xcode required). On Linux, the crates.io build goes through Blade/Vulkan while the git build goes through wgpu, since zed PR #46758 merged on 2026-02-13. Windows is the least-evidenced target: Paneflow defers its Windows ARM64 build pending GPUI DirectX reliability.
- **First build cost:** 5–15 minutes, once, because GPUI and wgpu compile from source. Rebuilds afterwards are fast.
- **Ecosystem context:** GPUI is a small crate next to the rest of Rust's UI world. Over the last 90 days crates.io served 19.75M downloads of ratatui, 12.82M of tauri, 5.69M of egui, 604K of iced, and 177K of `gpui`. That is exactly why the component kit matters so much.

## Which GPUI Dependency Path Should You Choose?

This is the decision that costs people the most time, and almost nobody documents it. There are three channels, and they are **not** interchangeable.

| Channel | What you get | Trade-off |
| --- | --- | --- |
| crates.io pair (`gpui` 0.2.x + `gpui-component` 0.5.x) | Official crates, `cargo add` simplicity | Frozen snapshot from Oct 2025; Blade/Vulkan on Linux |
| Git pair (`gpui` + `gpui_platform` + `gpui-component`, all from Zed/Longbridge git) | Current Zed main, wgpu on Linux, real components | Needs bleeding-edge Rust stable; commit a `Cargo.lock` |
| `gpui-unofficial` / forks | A tag-for-tag mirror, or added features (Kael) | Not a wgpu fork; incompatible with `gpui-component` |

### Why does `gpui` on crates.io look abandoned?

It is Zed's own official crate — repository `zed-industries/zed`, homepage `gpui.rs` — but the entire 0.2.x line shipped in October 2025. Version 0.2.0 landed 2025-10-09, 0.2.2 landed 2025-10-22, and nothing has been published since. On 2026-10-01 crates.io reports `gpui` 0.2.2 as max stable, roughly 11 months behind Zed main, with 316,531 all-time downloads and 177,435 in the last 90 days. Zed main has meanwhile split the framework into `gpui`, `gpui_platform`, `gpui_web`, and `gpui_macros` — and none of those split crates are on crates.io yet.

`gpui-component` moves faster: 0.7.0 released 2026-09-28, 159,788 all-time downloads, 94,980 in the last 90 days, backing the 15,377-star `longbridge/gpui-kit` repo. But its *published* releases are built against the frozen registry `gpui`.

### What is the E0277 trap?

This is the failure mode worth memorising. A published `gpui-component` is compiled against one specific `gpui`. If your `Cargo.toml` pulls a *different* GPUI lineage — `gpui-unofficial`, a mismatched git revision, or a crates.io/git mix — both dependencies compile cleanly and independently. Then **your** code fails with `E0277`:

```
error[E0277]: the trait bound `MyView: Render` is not satisfied
```

Your view implements one crate's `Render` trait; `open_window` and `Root::new` are asking for the other's. The dependencies compiled fine, so the error points at code you just wrote. The fix is to keep the pair matched: same channel for `gpui` and `gpui-component`, with a committed `Cargo.lock` for reproducibility.

The alternative single-dependency shortcut is `gpui-kit`, which bundles GPUI, the platform entry point, `gpui-component`, and assets in one crate — the simplest possible `Cargo.toml` for a first app.

## What Does the Minimal GPUI App Look Like?

GPUI exposes three registers: entity state (`Entity<T>` + `Context<T>`), high-level declarative views (`impl Render` returning a `div()` tree with a Tailwind-shaped builder API), and low-level imperative `Element`s for custom layout and virtualised lists. Actions are user-defined structs that map keystrokes to typed operations, and an async executor is integrated with the platform event loop.

The canonical skeleton is small:

```rust
Application::new().run(|cx: &mut App| {
    let bounds = Bounds::centered(None, size(px(900.), px(600.)), cx);
    cx.open_window(
        WindowOptions {
            window_bounds: Some(WindowBounds::Windowed(bounds)),
            ..Default::default()
        },
        |_, cx| cx.new(|_| HelloWorld { text: "World".into() }),
    ).unwrap();
});
```

Two rules make or break this step:

1. **Call `gpui_component::init(cx)` before opening any window.** Skip it and `cx.theme()` panics.
2. **`Root::new` must be the literal top layer** of your element tree, not nested inside a wrapper.

## How Do You Manage State Without a Browser?

There is no virtual DOM and no reconciler. You have entities, contexts, and notifications:

- `Entity<T>` holds state; `Context<T>` gives you a handle to mutate it.
- `cx.notify()` marks **that entity** dirty and schedules a repaint.
- `cx.spawn()` runs async work on the GPUI executor without blocking the UI thread.
- `cx.subscribe()` / `cx.emit()` wire entities to each other as event streams.

Four performance rules that follow directly:

- Never block the UI thread on I/O. Apply the state, call `cx.notify()` immediately, persist in the background.
- Notify the **smallest** entity that owns the change — a repaint of the root for a status-dot change is waste.
- Render large collections with `uniform_list` / `list`, never a flex column of N children.
- Filter in memory; do not re-query on every keystroke.

## How Do You Stream Agent Output Without Wrecking the Frame Budget?

Push, do not poll. This is the single highest-value lesson in the public record.

Paneflow measured **6–8 unnecessary repaints per second** while idle, caused by a 500ms port scan plus a 2-second working-directory poll. Migrating to `EventEmitter` with `cx.subscribe` / `cx.emit` took idle repaints to zero. As its author put it: "GPUI's diff repaint is cheap, but it isn't free."

The architecture that actually works:

1. **Model updates as events, not timers.** A token arrives → emit → subscribed entity appends to its buffer → `cx.notify()` on that entity only.
2. **Coalesce aggressively.** Paneflow drains terminal wakeups for up to **4ms or 100 events**, then issues exactly **one `cx.update()` and one `cx.notify()`** per batch. Your token stream should behave the same way: accumulate, then repaint once per frame.
3. **Respect terminal output semantics.** Honour DEC 2026 synchronized output (Paneflow tracks `sync_bytes_count()`), so a busy TUI cannot generate hundreds of wakeups per frame.
4. **Never call `cx.notify()` from a `setInterval`-shaped loop.** That is literally the pattern GPUI was designed to replace.

| Anti-pattern | Measured cost | Fix |
| --- | --- | --- |
| 500ms port-scan timer | part of 6–8 idle repaints/sec | event-driven port state |
| 2s CWD poll | part of 6–8 idle repaints/sec | OSC 7 title/CWD parsing in the reader thread |
| One `cx.notify()` per token | frames dominated by diff churn | batch: 4ms / 100 events, one notify |
| Repainting the root entity | repaint of the whole tree | notify the smallest owning entity |

## How Do You Embed a Real Terminal Instead of a Fake Log View?

Pin `alacritty_terminal` (0.26.0, updated 2026-04-06; 1,761,005 all-time downloads, 1,013,303 in 90 days) and drive it yourself. Paneflow migrated off Zed's internal fork as soon as 0.26 landed on crates.io, and the shape of its implementation is worth copying:

- Two hand-rolled detached threads rather than alacritty's `EventLoop::spawn`: a `pty_reader_loop` with a **4096-byte buffer** plus OSC 7 / 133 / XTVersion scanners, and a `pty_message_loop` for input and resize.
- A GPUI-side loop that drains wakeups for up to 4ms (maximum 100 events) and then does one `cx.update()` + one `cx.notify()`.
- The VTE processor advances against the locked `Term` on the reader thread; the UI reads a snapshot.

The reason to hand-roll this rather than use a shortcut: GPUI owns glyph rasterization end-to-end — shaping, atlasing, GPU draw. There is no "bring your own text path," so the boundary between your PTY thread and your `Entity<T>` is your responsibility.

## How Do You Give Agents a Control Plane?

A GUI that merely displays subprocess output is a viewer. A GUI that participates needs a protocol. Paneflow's answer is a local JSON-RPC 2.0 endpoint over a Unix socket at `$XDG_RUNTIME_DIR/paneflow/paneflow.sock` (a named pipe on Windows), with a 5-second dispatch timeout and an `ai.*` namespace — `session_start`, `prompt_submit`, `tool_use`, `notification`, `stop`, `session_end` — so a CLI agent can announce its own lifecycle to the sidebar.

Two details matter for correctness:

- The socket thread cannot touch `Entity<T>`. Dispatch to the GPUI main thread through an `mpsc` one-shot response channel with a timeout, or you will deadlock the executor.
- Use an explicit `ai.*` namespace rather than a generic `send` call. The UI can then render agent state (thinking / waiting / stalled / done) from typed events instead of guessing from stdout.

This is also where a GPUI app can beat a web app: because you own the process tree, you can surface permissions, sandbox scope, and pending approvals as first-class UI, not as a chat message the user has to scroll back to find.

## How Do You Get the Look Right?

Steal the component kit instead of rebuilding the DOM. `gpui-component` (the open core of `longbridge/gpui-kit`, 952 forks) ships **75+ documented components and primitives** across three layers: styled `gpui-component` widgets, unstyled behaviour in `gpui-base`, and `gpui-shell` JS extensions for a Rust host. It has powered the shipped Longbridge Pro commercial desktop app from day one, and it drew 515 points and 218 comments on Hacker News.

For an agent app specifically, three of its solved problems matter most:

- **Virtual lists** that render only the visible range, including variable-height items — your transcript will outgrow any flex column.
- **A code editor widget** that stays stable at 200K lines with Tree-sitter highlighting and LSP diagnostics, completion, and hover.
- **A serializable dock layout** with resizable panels, draggable tabs, and nested splits — persisted as data, not markup.

Also included: native Markdown/HTML rendering, a data table good for hundreds of thousands of rows, and UI integration testing with headless windows, synthetic pointer/keyboard input, and assertions on state, focus, layout, and accessibility.

Vendor claims to attribute rather than assert: "120 FPS" and "60–80% less memory than equivalent Electron apps" both come from Longbridge's blog. Similarly, the widely repeated "47–71% lower idle memory" and "8.2MB vs 121.7MB installer" figures are single-author blog benchmarks of Tauri versus Electron, not GPUI measurements.

### Where does clicking break?

Element IDs. GPUI's `on_click` requires the **same element ID between mouse-down and mouse-up**. If your render function derives IDs from a render-time counter, every frame creates what GPUI sees as a brand-new element, and `on_click` never fires while `on_mouse_down` does. Use user-provided or deterministically derived stable IDs.

### What else trips people up?

A digest of the sharp edges, all of them real:

- `.with_assets(gpui_component_assets::Assets)` is mandatory, or icons render blank.
- Never set `.selected()` on a list item inside `render_item` — `ListState` owns selection.
- `.searchable(true)` lives on `ListState`, not on the element.
- There is no `Modal`; use `Dialog`.
- `Input` is a stateful `InputState` entity, not a value.
- `KeyBinding::new` panics on malformed key strings.
- `cargo-bundle` 0.11 trips "No matching IconType" on a lone 1024px PNG.

And when a visual artifact survives several plausible fixes, suspect your data, not your math. Paneflow spent six GPU-math fixes chasing gaps between block characters (U+2580–259F); the actual cause was 11 missing codepoints in its coverage table.

## How Do You Package and Ship It?

Packaging is where weekend projects die, and the fix is to make it declarative. A `[package.metadata.bundle]` block read by `cargo-bundle` produces a double-clickable app, and signing/notarization stays opt-in.

Three things surprise people:

1. **Dock icon and app label are bundle-only.** Running `cargo run` shows the binary name and no icon; only the bundle carries identity.
2. **Signing needs money.** A frictionless macOS install requires a paid Apple Developer ID (`codesign` + `xcrun notarytool`). Linux ships as `.deb` / `.rpm` / `.AppImage`, Windows as `.msi` / `.exe`.
3. **Auto-update is thin.** Waku reports Sparkle binary deltas on macOS; muxel ships in-app updates. There is no widely adopted cross-platform updater for GPUI apps to recommend.

Also set expectations on size. The commonly blogged claim that "Zed is ~30MB" is false: Zed's actual v1.22.0 assets, published 2026-09-30, are `Zed-aarch64.dmg` at 112MB, `zed-linux-x86_64.tar.gz` at 119MB, and `Zed-aarch64.exe` at 68MB. GPUI gives you a smaller footprint than Electron because there is no Chromium and no Node runtime — not because a real app with fonts and assets is a 10MB artifact. Judge by idle CPU, idle RAM, and startup latency instead.

## How Do You Survive Pre-1.0 Churn?

GPUI's own README warns plainly: "There will often be breaking changes between versions." Budget for it mechanically rather than hoping.

The encouraging data point: the bump from the Oct-2025 snapshot to mid-2026 cost one project exactly **four one-line edits** — `Application::new()` became `gpui_platform::application()`, `Menu` gained a `disabled` field, and `window.focus()` gained a `cx` argument. That is a small, boring diff if your tree is small.

Pin your way to stability:

- Commit `Cargo.lock`. Reproducibility on the git channel comes from the lockfile, not from a version range.
- Pin the toolchain with `rust-toolchain.toml`.
- Keep the `gpui` / `gpui_platform` / `gpui-component` triple on one channel.
- Isolate UI code from agent logic, so a framework bump never touches your PTY or protocol layer.

## What Should Your First Week Look Like?

A realistic sequence, in order:

1. Build the skeleton window with a matched dependency pair and a committed lockfile. Confirm it compiles before writing any agent code.
2. Add `gpui_component::init(cx)` and `.with_assets(...)`; verify the theme and icons render.
3. Implement the agent loop as an `Entity<T>` with `EventEmitter`; drive it from a fake token source and confirm idle repaints stay at zero.
4. Add the PTY pane with `alacritty_terminal`, coalescing wakeups at 4ms / 100 events.
5. Add session persistence on `CloseWindow` — before it can hurt you.
6. Add the JSON-RPC control plane and render agent lifecycle state in the sidebar.
7. Only then do bundling, icons, and the first signed build.

One step deserves special emphasis. Paneflow shipped without session persistence, opened four workspaces, rebuilt the binary, and lost all four. Save state to something like `~/.cache/yourapp/session.json` on `CloseWindow`. It is the cheapest credibility you can buy, and the alternative is that the first real user experience your app delivers is data loss.

## FAQ

**Is crates.io `gpui` the real Zed framework or a fork?**
It is Zed's own official crate — repository `zed-industries/zed`, homepage `gpui.rs`. The catch is staleness, not provenance. The whole 0.2.x line shipped in October 2025 (0.2.0 on 2025-10-09, 0.2.2 on 2025-10-22) with nothing published since, so it lags Zed main by months. Zed main has also split the framework into `gpui`, `gpui_platform`, `gpui_web`, and `gpui_macros`, and none of those split crates are on crates.io yet.

**Why do I get E0277 trait-mismatch errors when both crates compile?**
You are mixing two GPUI lineages. A published `gpui-component` is built against one specific `gpui`; if your manifest pulls a different one — `gpui-unofficial`, a mismatched git revision, or a crates.io/git mix — both dependencies compile independently, but your `Render` impl satisfies one crate's `Render` trait while `open_window` and `Root::new` expect the other's. Keep the pair matched and commit the lockfile.

**Do I need a webview at all?**
No. GPUI has no webview and no JavaScript bridge: your UI is Rust, and GPUI owns text shaping, atlasing, and GPU draw end-to-end. If you want React ergonomics anyway, GPUIX (remorses/gpuix, 2,495 stars) paints a React tree from TypeScript into GPUI through napi on desktop or wasm-bindgen in the browser — instead of into the DOM.

**How do I stream tokens without killing the frame rate?**
Push, don't poll. Model updates as events with `EventEmitter` plus `cx.subscribe` / `cx.emit`, accumulate tokens into the receiving entity's state, and coalesce: Paneflow drains wakeups for up to 4ms or 100 events and then performs exactly one `cx.update()` and one `cx.notify()` for the batch. A timer-shaped `cx.notify()` loop is the exact pattern GPUI was built to replace — one project measured 6–8 wasted repaints per second from it.

**How big is the first build, and will my app be tiny?**
The first build compiles GPUI (and wgpu on Linux) from source: roughly 5–15 minutes, once, after which rebuilds are fast. You need a recent Rust stable because gpui HEAD uses just-stabilized standard-library APIs — Zed pins 1.95.0 and Paneflow pins 1.96.1 via `rust-toolchain.toml`. Your app will be smaller than an Electron one (no Chromium, no Node), but do not expect a 10MB artifact: Zed's own v1.22.0 installers are 112MB for macOS and 119MB for Linux, because that is fonts, assets, and a full editor.
