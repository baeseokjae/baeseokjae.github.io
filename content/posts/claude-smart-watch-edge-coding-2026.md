---
title: "Hacking with Claude on a $27 Smart Watch: Edge AI Coding Case Study"
date: 2026-09-03T16:01:28+00:00
tags:
  - edge-ai
  - ai-coding
  - pinetime
  - embedded
  - firmware
  - case-study
description: "A $27 PineTime smart watch + an AI coding agent built a custom watch face in hours. Here's how edge AI coding works on cheap hardware."
draft: false
cover:
  image: "/images/claude-smart-watch-edge-coding-2026.png"
  alt: "Hacking with Claude on a $27 Smart Watch: Edge AI Coding Case Study"
  relative: false
schema: "schema-claude-smart-watch-edge-coding-2026"
---

Can you really build a custom smart watch face with an AI coding agent on a $27 watch? Yes — a staff software engineer at Strava did exactly that, turning a PineTime that had sat abandoned in a drawer for two years into a working Casio-style watch face in just a few hours. This case study breaks down how edge AI coding works on cheap, open-source hardware, and what it means for the future of embedded development.

## The $27 Watch That Sat in a Drawer for Two Years

The PineTime is a fully open-source smart watch from Pine64 that costs just $27. It ships with InfiniTime, a community-driven open-source firmware, and works with Linux, Windows, and Android. For most people, that price tag makes it a curiosity — a cheap gadget to tinker with once and then forget.

That is exactly what happened to the author of this case study. He bought the PineTime, played with it briefly, and then abandoned it for two years. The reason wasn't a lack of interest — it was a lack of time and motivation to learn the InfiniTime codebase from scratch. Embedded firmware development has a steep learning curve, and for a side project, the effort-to-reward ratio just wasn't there.

Then AI coding agents changed the calculus. Instead of spending weeks learning how InfiniTime renders watch faces, he could describe what he wanted and let an agent handle the boilerplate. The result: a working custom watch face in a few hours, on a project he had given up on years earlier.

## Why the PineTime Is the Perfect AI Hacking Sandbox

Not every piece of hardware is well-suited to AI-assisted development. The PineTime stands out for several reasons that make it an ideal sandbox for edge AI coding.

**It's cheap enough to be low-stakes.** At $27, you're not risking expensive hardware. If the AI agent produces broken code, you flash it again and try something different. This low-stakes environment is exactly what enables fast iteration — there's no production risk, no customer impact, and no fear of bricking a $500 device.

**The firmware is fully open source.** InfiniTime is community-driven and well-documented. The codebase is the kind of thing AI agents thrive on: clear structure, established patterns, and plenty of examples to learn from. The author notes that the well-documented codebase is one of the reasons Claude and similar agents perform so well on it.

**It runs on any RTOS.** The PineTime isn't locked into a single firmware. It runs on numerous real-time operating systems, and the default firmware shipped with the watch is InfiniTime. This flexibility means you can pick the environment that works best for your project.

**There's a great simulator.** InfiniSim, the official PineTime simulator, gives AI agents a fast feedback loop on your computer without flashing hardware. This is a game-changer for AI-assisted development, because it means the agent can iterate rapidly on code and see results immediately.

Here's a quick comparison of what makes the PineTime special versus a typical commercial smart watch:

| Feature | PineTime ($27) | Typical Commercial Smart Watch |
|---------|---------------|-------------------------------|
| Firmware | Fully open source (InfiniTime) | Proprietary, closed |
| Price | $27 | $100–$500+ |
| AI hackability | Excellent — documented, simulator, low-stakes | Poor — locked down |
| RAM | 64KB (painful bottleneck) | 1MB+ |
| Storage | 4MB user + 0.5MB OS | 8GB+ |
| Display | 1.3" 240x240 IPS touch | 1.3"–1.9" AMOLED |
| Community | Active, open-source | Closed ecosystem |

## Setting Up: InfiniSim Gives Claude a Fast Feedback Loop

The setup process is where the AI-first workflow really shines. The author started by cloning the InfiniSim repository, which includes a git submodule for the InfiniTime firmware. He then asked the AI agent to get a build working.

On Ubuntu, this was quick and easy. The agent could compile the firmware, run it in the simulator, and see the results — all without touching physical hardware. This is the key insight: **the simulator turns hardware development into a software development loop.**

Without a simulator, every change requires flashing the watch over Bluetooth, which is slow and tedious. With InfiniSim, the agent can iterate dozens of times in the time it would take to do one hardware flash. This fast feedback loop is what makes AI-assisted embedded development practical.

The workflow looks like this:

1. Clone InfiniSim (which includes InfiniTime as a submodule)
2. Ask the agent to get a build working
3. Run the build in the simulator
4. Iterate on the code with immediate visual feedback
5. Only flash the real hardware once the simulator version works

## Building the Casio-Style Watch Face — Rough First Pass

The actual build process was deliberately iterative. The author didn't ask the agent to produce a perfect watch face in one shot. Instead, he started with a rough first pass, then refined it one element at a time.

The goal was a Casio-style watch face — the classic digital watch look with a large time display, date, and other elements. The first pass got the basic structure in place: a time display, some static elements, and the overall layout.

From there, the author fixed one text element at a time. Each iteration was an isolated task with a concrete next step. This approach has a critical benefit: it saves tokens. Instead of letting the agent run unsupervised and burn through a budget exploring the codebase, the human provides specific, targeted feedback that keeps the agent focused.

This human-in-the-loop approach is the opposite of the "set it and forget it" style of AI coding. It's more deliberate, but it's also far more efficient on a limited budget.

## The Token-Budget Strategy: Human-in-the-Loop Iteration

One of the most valuable lessons from this case study is about token economics. The author used OpenCode with open-weights models — Kimi K3 and K2.6, DeepSeek v4 Pro and Flash — on a limited budget. He couldn't afford to let an agent run unsupervised for hours.

The strategy he settled on was simple: **give the agent one isolated task at a time, with a concrete next step.** Each prompt was specific about what to change and how. This keeps the agent from wandering, reduces wasted tokens, and produces cleaner results.

This is a meaningful counterpoint to the popular image of AI coding as a fully autonomous process. In practice, especially on constrained budgets, the best results come from a tight human-agent loop where the human acts as a project manager, breaking work into small, well-defined tasks.

The trade-off is clear:

| Approach | Token Cost | Result Quality | Best For |
|----------|-----------|---------------|----------|
| Unsupervised agent | High | Variable, often messy | Large budgets, simple tasks |
| Human-in-the-loop | Low | High, focused | Limited budgets, complex tasks |
| Hybrid (rough pass + targeted fixes) | Medium | High | Most real projects |

## The Fullscreen Background Trick and Hardware Limits

The PineTime's biggest constraint is its 64KB of RAM. That's a painful bottleneck for rendering, and it forced the author to get creative.

The solution was a clever optimization: **use a fullscreen background image for the static parts of the watch face, and only program the dynamic parts.** Instead of rendering every element from scratch each frame, the watch displays a pre-rendered background image and overlays only the changing elements (like the time) on top.

This worked in the simulator, but it pushed the hardware to its limits. Transferring a 240x240 fullscreen image over Bluetooth to the PineTime took about 10 minutes. Refreshing the whole screen on a swipe takes 1-2 seconds. And because of the RAM limits, the watch streams the image from the filesystem rather than holding it in memory.

These constraints are worth understanding because they shape what's possible:

- **64KB RAM** — the fundamental bottleneck; forces clever rendering strategies
- **10-minute Bluetooth transfer** — makes flashing slow, reinforcing the value of the simulator
- **1-2 second screen refresh** — limits how dynamic the watch face can be
- **Filesystem streaming** — a workaround for the RAM limit, but adds latency

The lesson here is that hardware constraints become creative constraints. The fullscreen background trick is exactly the kind of pragmatic solution that emerges when you understand your hardware's limits — and it's the kind of thing an AI agent can help you discover and implement.

## What "Claude" Actually Means Now (OpenCode + Open Weights)

There's an important clarification in this case study that's easy to miss. The author used "Claude" as a generic term for coding agents — but he actually used OpenCode with open-weights models like Kimi K3, K2.6, DeepSeek v4 Pro, and DeepSeek v4 Flash.

This is a fascinating example of genericization, similar to how "Xerox" became a verb for photocopying or "ChatGPT" became shorthand for any AI chatbot. "Claude" is becoming the category name for AI coding agents, even when the underlying model is something else entirely.

The HN discussion (which reached 110 points with 20 comments) picked up on this point specifically. The community noted that the author used OpenCode + open-weights models, not Claude itself — but the term "Claude" was used generically, like "Xerox" or "ChatGPT."

This matters for a few reasons:

1. **It shows how fast the AI coding space is moving.** Open-weights models are now good enough to handle embedded firmware development, a task that would have been unthinkable a couple of years ago.
2. **It highlights the commoditization of coding agents.** The specific tool matters less than the workflow — the simulator, the token strategy, the human-in-the-loop iteration.
3. **It signals that edge AI coding is accessible.** You don't need the most expensive model or the most hyped tool. Open-weights models on a $27 watch are enough to get real work done.

## Lessons Learned and the AGENTS.md Playbook

The author pushed his code to GitHub (in the mkasberg/InfiniTime repository, on a branch called "casio") and included an AGENTS.md file summarizing the lessons learned. This is a best practice worth adopting for any AI-assisted project.

An AGENTS.md file is essentially a playbook for AI agents working on a codebase. It documents the project's conventions, the key constraints, and the lessons learned from previous AI-assisted work. This makes future sessions dramatically more efficient, because the agent doesn't have to rediscover everything from scratch.

The core lessons from this case study:

- **Start with a simulator.** A fast feedback loop is the single biggest accelerator for AI-assisted embedded development.
- **Break work into isolated tasks.** One change at a time, with a concrete next step, saves tokens and improves quality.
- **Understand your hardware limits.** The 64KB RAM bottleneck shaped every design decision.
- **Use creative workarounds.** The fullscreen background trick turned a constraint into a feature.
- **Document what you learn.** An AGENTS.md file makes the next session faster and better.
- **Embrace low-stakes tinkering.** Fun, physical, rewarding projects are the ideal AI coding sandbox.

## The Future of Edge AI Coding on Cheap Hardware

This case study is a snapshot of where edge AI coding is heading, and the trajectory is clear. As open-weights models improve and coding agents get better at embedded development, the barrier to hardware hacking will keep falling.

Several developments point to the future:

**More capable hardware.** The PineTime Pro, with more RAM, is mentioned as a future solution to the 64KB bottleneck. More RAM means more complex watch faces, smoother animations, and fewer creative workarounds.

**Better alternatives.** The HN discussion suggested the Waveshare ESP32-S3 AMOLED 2.09" watch as an alternative with better display, peripherals, and CPU at a similar price. As cheap hardware gets more capable, the range of what's possible expands.

**Voice control — eventually.** The PineTime has no microphone, so voice control is currently impossible. But as hardware evolves, this limitation will likely disappear, opening up new interaction models.

**The democratization of embedded development.** The biggest story here is that a $27 watch plus an AI agent replaced months of learning a codebase. This is the same pattern we've seen in web development, data science, and other fields: AI tools lower the barrier to entry, letting more people build more things.

The author's own experience captures this perfectly. He had abandoned the watch for two years because the learning curve was too steep. AI made it approachable — and fun. That's the real promise of edge AI coding: not just faster development, but the ability to tackle projects you would never have started in the first place.

## FAQ

**Can you really code a smart watch with an AI agent?**
Yes. A staff software engineer at Strava used an AI coding agent to build a custom Casio-style watch face for the $27 PineTime in just a few hours, on a project he had abandoned for two years.

**What is the PineTime?**
The PineTime is a $27 fully open-source smart watch from Pine64. It runs InfiniTime firmware, has a 1.3-inch 240x240 IPS touch display, a Nordic nRF52832 64MHz processor, Bluetooth 5/BLE, 4MB user storage, and an all-week 180mAh battery.

**What is InfiniSim?**
InfiniSim is the official PineTime simulator. It gives AI agents a fast feedback loop on your computer without flashing hardware, making AI-assisted embedded development much faster and more practical.

**What are the PineTime's main hardware limits?**
The biggest constraint is 64KB of RAM, which makes rendering difficult. Transferring a fullscreen image over Bluetooth takes about 10 minutes, and refreshing the whole screen takes 1-2 seconds. The watch streams images from the filesystem to work around the RAM limit.

**Did the author actually use Claude?**
No — he used "Claude" as a generic term for coding agents. He actually used OpenCode with open-weights models like Kimi K3, K2.6, DeepSeek v4 Pro, and DeepSeek v4 Flash. This is an example of "Claude" becoming a generic term for AI coding agents, like "Xerox" or "ChatGPT."
