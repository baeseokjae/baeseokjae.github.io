---
title: "Barehands: Webcam-Powered Hand Tracking to Control Your Screen Without a Headset"
date: 2026-09-07T22:01:54+00:00
tags: ["barehands hand tracking", "webcam hand tracking", "AI computer use", "MediaPipe", "gesture control", "touchless screen control"]
description: "Control your screen with nothing but your hands and a webcam. Barehands gives zero-install, touchless control over a glass board you and an AI can use."
draft: false
cover:
    image: "/images/barehands-hand-tracked-control.png"
    alt: "Barehands: Webcam-Powered Hand Tracking to Control Your Screen"
    relative: false
schema: "schema-barehands-hand-tracked-control"
---

Barehands is a free, open-source project that turns a standard webcam and the Chrome browser into a glass board you control with your hands — no headset, no controllers, no gloves. It uses Google MediaPipe to track your hands in real time and lets you tap, drag, scale, and throw items across your screen, even wiring in an AI that sees, hears, and acts through the same interface.

## What Is Barehands and Why It Matters

Barehands (jaredrhod/barehands on GitHub) is a webcam-based hand-tracking interface that lets you control a 3D "glass board" on your screen with natural hand gestures. Created in mid-August 2026, it already holds roughly 907 GitHub stars and about 199 forks, according to the GitHub API as of September 7, 2026 — remarkable velocity for a project less than a month old.

The core idea is deliberately simple: **a body waiting for a brain.** Barehands is a zero-install spatial interface — you gesture to move, scale, and arrange objects, and you can attach an AI to that same board. The AI gets a face (the "ring"), hands (board scripts), and a voice — turning a webcam setup into a touchless control surface for both you and an autonomous agent.

This matters because the "AI computer use" category is exploding. Tools like AIHawk (30,000+ stars) and e2b's open-computer-use (2,200+ stars) treat AI as the brain that acts on the screen programmatically. Barehands occupies a different lane: it is a *human* gestural interface whose board an AI can also inhabit.

## How Barehands Works Under the Hood

The genius of Barehands is what it does **not** require. There is no pip install, no compiled binary, no GPU, and no dedicated hardware beyond the camera that is already in your laptop.

The architecture breaks down like this:

- **Hand tracking:** Google MediaPipe loads from a CDN on first run and detects your hand landmarks in the webcam feed.
- **Rendering:** three.js (also from a CDN) renders the 3D glass board and the objects you can grab.
- **Server:** a standard-library-only Python server (`python3 server.py`, or `run.bat` on Windows) serves the page at `http://127.0.0.1:8794/stage.html`.
- **Camera geometry:** every gesture threshold is measured as a *shape ratio* against your own hand's span and geometry, not an absolute pixel size. That means it works at any camera distance and on any hand size.

The only real system requirement is **Python 3.9+** plus a webcam and Chrome. Everything else is fetched on demand.

### Why "No Installs" Matters for Computer Use

Traditional webcam virtual-mouse projects need OpenCV, PyAutoGUI, and a stack of native dependencies installed to your machine. Barehands sidesteps the entire dependency tree. Because the computer-vision and rendering logic run in the browser and server, there is nothing to compile and nothing that can silently break across OS updates.

## Install and First Run

Getting started takes about two minutes and does not require touching your system Python packages.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jaredrhod/barehands
   cd barehands
   ```

2. **Start the server** (Python 3.9+):
   ```bash
   python3 server.py
   ```
   On Windows, double-click `run.bat` instead.

3. **Open Chrome** and go to `http://127.0.0.1:8794/stage.html`. Allow camera access when prompted.

4. **First run downloads** MediaPipe and three.js from CDNs, so keep the network connected the first time.

That is it. You are now facing a glass board you can manipulate with your hands.

## The Gesture Language: Tap, Pinch-Drag, Scale, Throw, Clap, and the Claw

Barehands' gesture set is small but expressive, and every motion maps to how you would naturally grab a real object.

| Gesture | Motion | What It Does |
|---------|--------|--------------|
| **Tap** | Quick pinch | Open or close an item |
| **Pinch-Drag** | Pinch and move | Move items across the board |
| **Two hands / Scale** | Pinch with both hands and spread | Scale items up or down |
| **Flick** | Fast wrist throw | Throw items to reposition |
| **Clap** | Clap both hands | Clear the board |
| **The Claw** | Curled-finger grip | Rip items across the screen |
| **Empty pinch-drag** | Pinch with no item selected | Scrub a 3D model's exploded view |

The "claw" is the signature interaction — instead of dragging a virtual touchpoint, you grip an item and yank it across the glass board, which feels far more physical than pointer emulation.

If a gesture feels unreliable, remember that all thresholds are computed as ratios against your hand's geometry, so first adjust your distance to the camera and your hand's position in frame before changing sensitivity. The project's `TROUBLESHOOTING.md` covers the common failure modes in detail.

## Wiring in Your AI as the Brain

The differentiator that earned Barehands its rapid following is how easily an AI can join the board. The project deliberately markets the tool as a body, and it provides the joints to attach a brain.

- **The ring** is the AI's face. It reads a state file at `state/state`, cycling through `idle`, `listening`, `thinking`, and `speaking` so you can see what the AI is doing.
- **`board.sh` and `board-state.sh`** become the AI's hands and eyes — scripts that let the agent manipulate and observe the board.
- **Claude Code hooks** wire seamlessly: the setup builder in `barehands.md` adds hooks to `settings.json` where `UserPromptSubmit` writes `thinking` to `state/state` and `Stop` writes `idle`.
- **Crash safety:** a server-side `state_timeout_s` (10 minutes by default) settles the ring back to a sane state if the AI session crashes mid-thought.
- **Safety rails:** a server-side **action allowlist** and a `media/` airlock jail constrain what the AI can do and touch, which is what makes it safe to hand an autonomous agent this kind of control.

You can drive the same board with a local LLM, cron jobs, a Stream Deck, or any process that can read and write `state/state`. The brain is interchangeable — Barehands does not care which one you pick.

## Advanced: OBS Streaming, Portrait Mode, 4K, and Troubleshooting

Beyond the basics, Barehands is designed to be part of a live setup:

- **OBS streaming:** because the board renders in a browser tab, you can capture it directly into OBS as a window or browser source — no extra capture software needed.
- **Portrait / 9:16:** the board works in vertical aspect ratios, handy for phone or short-form video capture.
- **4K output:** the rendering pipeline can output high-resolution frames for clean, crisp recordings.
- **Troubleshooting:** consult `TROUBLESHOOTING.md` first. Since every threshold is a shape ratio, the same tuning advice — adjust camera distance, raise your hand in frame, and ensure even lighting — solves the majority of tracking problems.

## Barehands vs Traditional Virtual-Mouse Projects and AI Computer-Use Tools

Barehands is frequently compared to two other families of tools, but it is not a drop-in replacement for either.

| Category | Example Project | Approach | Barehands vs It |
|----------|-----------------|----------|-----------------|
| **Virtual mouse (cursor emulation)** | NonMouse (200+ stars) | Hands rest on desk; acts as a low-fatigue cursor | NonMouse is better for pure mouse-cursor control; Barehands is a spatial glass board, not a cursor replace |
| **Virtual mouse (classic)** | Gesture-Controlled-Virtual-Mouse (856+ stars) | MediaPipe + OpenCV + PyAutoGUI, hand becomes cursor | The "cursor emulation" school vs Barehands' "spatial manipulation + AI body" school |
| **AI computer use** | AIHawk (30k+ stars) | AI browser/computer-use agent acts on screen | Machine-driven automation vs a human gestural interface; Barehands' is human-first |
| **AI computer use (open LLM)** | e2b open-computer-use (2.2k+ stars) | AI acts via open-source LLMs in a Desktop Sandbox | Barehands differs by being an AI-inhabitable gesture surface |

The practical takeaway: if all you want is to move the mouse with your hand, a virtual-mouse project fits better. If you want a touchless, spatial glass board that a human *and* an AI can both manipulate, Barehands is the tool.

## The Jarvis Stack: Memory, Voice, Face, and Hands Together

Barehands is rarely deployed in isolation. In the wider ecosystem it slots into a four-part "Jarvis stack" assembled via `fullstack-agent`:

- **ai-memory-vault** — the memory
- **backtalk** — the voice
- **ai-visualizer** — the face
- **barehands** — the hands

You can also point it at an existing **Obsidian vault** and use it as a notes orb with zero plugin setup — an Obsidian vault is just a folder of markdown, so a hand-tracked glass board over that folder works as-is.

## Licensing and Where to Go Next

Barehands is licensed under **AGPL-3.0-or-later**. In practical terms:

- You are free to **use and sell it commercially inside your own business**.
- Any redistributed or modified **SaaS** version must **stay open**, with source available to users.
- **Closed-source commercial use** requires contacting `license@jaredrhod.com` for a separate arrangement.

To go further, clone the repo at `github.com/jaredrhod/barehands`, read the `barehands.md` setup builder to wire in your AI, and check `TROUBLESHOOTING.md` before tuning gestures.

## FAQ

**Q1: Do I need a VR headset or special hardware to use Barehands?**
No. Barehands runs entirely on a standard webcam and the Chrome browser. There is no headset, no controllers, and no gloves — the only hardware requirement is the camera already built into your laptop.

**Q2: Does Barehands require installing heavy dependencies like OpenCV?**
No. The server uses Python's standard library only (Python 3.9+ required), and both Google MediaPipe and three.js load from CDNs on first run. There is nothing to compile and no pip install.

**Q3: What is the difference between Barehands and a virtual mouse?**
A virtual-mouse project like NonMouse or Gesture-Controlled-Virtual-Mouse turns your hand into a literal cursor. Barehands instead gives you a spatial "glass board" you manipulate with gestures — and it is also inhabited by an AI, which cursor tools are not.

**Q4: Can I connect an AI like Claude to Barehands?**
Yes. The `barehands.md` setup builder wires Claude Code in via hooks in `settings.json` — `UserPromptSubmit` writes `thinking` to the ring state and `Stop` writes `idle`. The ring then shows the AI's state, and `board.sh` gives it hands and eyes on the board.

**Q5: Is Barehands free to use commercially?**
Yes, under the AGPL-3.0-or-later license. You can use and sell it inside your own business for free. If you distribute or modify it as a SaaS, it must stay open-source; closed-source commercial use requires contacting license@jaredrhod.com.
