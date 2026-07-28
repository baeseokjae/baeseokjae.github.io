---
title: "Claude of Duty: Building a Call of Duty-Quality FPS from a Single Prompt"
date: 2026-07-28T07:03:42+00:00
tags:
  - AI Game Development
  - Claude of Duty
  - Single Prompt Game Generation
  - Three.js
  - Procedural Generation
  - AI Agent Orchestration
  - WebGL2
  - FPS Game
description: "Claude of Duty generated 55,000 lines of Call of Duty-quality FPS code from a single AI prompt. Here is how it works, how it scores, and what it means for game development."
draft: false
cover:
  image: "/images/claude-of-duty-single-prompt-fps-2026.png"
  alt: "Claude of Duty: Building a Call of Duty-Quality FPS from a Single Prompt"
  relative: false
schema: "schema-claude-of-duty-single-prompt-fps-2026"
---

## What Is Claude of Duty? — The Project Overview

Claude of Duty is an open-source project by Matt Shumer that generates a fully playable first-person shooter in the browser from a single AI prompt. Built entirely with Three.js r180 and WebGL2, the project produces approximately 55,000 lines of JavaScript across 11 coordinated subsystems — including rendering, physics, AI, weapons, audio, and UI — with zero external art assets, models, textures, or audio files. Every visual element is procedurally generated at load time.

Released on July 25, 2026, the project amassed over 1,084 GitHub stars and 210 forks within its first three days. The README is refreshingly honest: it scores itself 5.05 out of 10 against real Call of Duty and openly documents every shortcoming. This transparency, combined with the sheer technical ambition, has made Claude of Duty one of the most discussed AI game development projects of 2026.

## The Single Prompt That Built a Game — Breaking Down prompt.md

The entire game originates from a single markdown file: `prompt.md`. This prompt instructs the AI to fan out into multiple sub-agents, each responsible for a different subsystem, and to use harsh adversarial critics that compare every frame side-by-side with real Call of Duty footage.

### Key Elements of the Prompt

The prompt uses a `/loop` pattern for iterative improvement with visual quality checks. It tells the AI to:

1. **Fan out sub-agents** — Each subsystem (renderer, physics, AI, weapons, etc.) gets its own dedicated agent
2. **Use harsh critics** — 11 adversarial AI critics score every frame against real Call of Duty
3. **Compare side-by-side** — Blind A/B testing against actual CoD screenshots
4. **Iterate relentlessly** — The loop continues until quality targets are met

This structured approach to prompt engineering demonstrates that a well-crafted single prompt can orchestrate complex multi-agent code generation far more effectively than ad-hoc, uncoordinated prompting.

## 11 Subsystems, Zero Art Assets — Technical Architecture Deep Dive

Claude of Duty's architecture is defined by the OVERWATCH engine contract — a coordination mechanism that enforces strict rules across all 11 subsystems. Each subsystem owns its directory, must never import from another subsystem, and follows a standardized lifecycle: `init`, `fixedUpdate`, `update`, `lateUpdate`, `resize`, and `dispose`.

| Subsystem | Responsibility | Key Technical Detail |
|-----------|---------------|---------------------|
| Render | HDR pipeline, CSM, TAA, bloom | Full deferred rendering with temporal anti-aliasing |
| Materials | 19 procedural PBR surfaces | Concrete, brick, plaster, asphalt, sand, metals, wood, fabric, burlap, glass — all generated at load time |
| Sky | Atmospheric scattering | Physically-based sky model with dynamic sun |
| World | 120x120m market street | Modular building kit with enterable interiors, hundreds of instanced props |
| Physics | BVH, swept-capsule, ragdolls | Binned-SAH BVH: 29k triangles → 14k nodes in 22ms, 0.25 µs/raycast |
| Player | Movement state machine | Full locomotion, sprint, slide, jump states |
| Weapons | Procedural geometry, ballistics | Weapon models generated from code, physics-based projectile simulation |
| FX | GPU particles, decals | Compute-shader particle systems, dynamic decal placement |
| AI | Navmesh, cover behavior | Pathfinding with tactical cover selection |
| UI | DOM/CSS HUD | Health, ammo, minimap rendered via HTML/CSS overlay |
| Audio | Web Audio synthesis | All sound effects generated procedurally — no audio files |

The only runtime dependency is Three.js r180. There are no external images, models, HDRIs, or audio files. The triangle count grew from 5.9 million to 11.3 million over successive art passes.

## The Honest Score: 5.05/10 vs Call of Duty — Visual Quality Assessment

Claude of Duty's most refreshing feature is its honest self-assessment. The project uses 11 adversarial AI critics to score every frame against real Call of Duty. The scoring progression tells a compelling story:

| Round | Average Score (out of 10) | Defects | Key Change |
|-------|--------------------------|---------|------------|
| 1 | 3.59 | 66 | Initial generation |
| 2 | 4.14 | — | First optimization pass |
| 3 | 4.05 | — | Art pass |
| 4 | 5.05 | 26 | Sequential single-owner pass |

In every single round, every critic picked the real Call of Duty frame in blind A/B testing. The project acknowledges this honestly: "critics always picked real CoD in blind A/B." The 5.05/10 score represents the critics' assessment of how close Claude of Duty comes to matching CoD's quality, not a pass/fail threshold.

### Key Visual Weaknesses

- **Blocky hands** — The viewmodel (player hands/weapon) lacks the geometric detail of AAA games
- **Procedural texture ceiling** — AI-generated textures, while impressive, cannot yet match photographed reality
- **Mannequin-like characters** — Enemy models lack the facial detail and animation fidelity of modern FPS games
- **No real global illumination** — Lighting relies on shadow mapping and screen-space effects rather than baked or real-time GI
- **28-30 fps at Retina resolution** — Performance is playable but far from the 60+ fps target of competitive shooters

## Performance Journey: From 12fps to 30fps — Optimization Case Study

The performance optimization story of Claude of Duty is as impressive as the game itself. Initial performance was 12-17 fps — barely playable. Through systematic optimization, the team achieved 28-30 fps with zero visual change.

### Optimization Milestones

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Average FPS | 12-17 | 28-30 | ~2x |
| Worst frame time | 728-1236ms | 66-82ms | ~12x |
| Shader compiles during gameplay | 34-35 | 0 | Eliminated |
| Boot time | 9-12s | 3.7-4.6s | ~2.5x |

The single biggest win came from `prewarm.js` — a shader pre-warming script that eliminated all 34-35 shader compilations during gameplay. This reduced worst frame time from over a second to under 82ms. The lesson is clear: in WebGL applications, shader compilation stalling is the single largest source of perceived lag, and pre-warming is the most impactful optimization available.

## Process Lessons: Sequential Beats Parallel for AI Code Generation

One of the most surprising findings from Claude of Duty is about AI agent orchestration strategy. The project compared two approaches:

**Parallel fan-out:** Multiple AI agents work simultaneously on different subsystems, then results are merged. This approach improved the critic score by +0.46 and left defects relatively high.

**Sequential single-owner passes:** A single AI agent works through the entire codebase in sequence, making focused improvements one at a time. This approach improved the score by +1.00 and cut defects from 66 to 26.

The sequential approach was decisively better — nearly 2x the quality improvement with less than half the defects. This contradicts the common assumption that parallel processing is always faster for AI code generation. The likely explanation is that sequential passes maintain better context about the full codebase, avoiding the integration bugs and inconsistent design decisions that plague parallel work.

## The Viewmodel Lighting Bug — A Case Study in Cascading Failures

One of the most instructive bugs in Claude of Duty's development was the viewmodel lighting bug. A single root cause — 20x irradiance on the viewmodel (the player's hands and weapon) — cascaded across the entire visual pipeline.

This bug is a perfect example of how subtle rendering errors can compound in complex systems. The viewmodel was receiving 20 times the correct lighting intensity, which:

1. Made player hands and weapons appear blown out and unrealistic
2. Caused inconsistent lighting between the viewmodel and the world
3. Confused the adversarial critics, who correctly identified the lighting mismatch
4. Required tracing through the entire lighting pipeline to find the root cause

The fix was simple once identified, but finding it required deep understanding of the full rendering chain. This case study underscores the importance of systematic debugging in AI-generated code — AI can produce complex systems, but understanding and debugging them still requires human expertise.

## Tooling and Reproducibility — baseline.mjs, imagediff.mjs, and the Testing Pipeline

Claude of Duty includes a sophisticated testing and reproducibility pipeline that is rare in AI-generated projects:

- **baseline.mjs** — Captures reference frames for bit-identical comparison
- **imagediff.mjs** — Performs pixel-level visual regression testing against baselines
- **Prewarm.js** — Eliminates shader compilation stalling during gameplay

This tooling enables reproducible testing across different runs and environments. When an optimization claims to improve performance without changing visuals, the imagediff tool can verify that claim objectively. This level of engineering rigor is unusual for a project that started as a single AI prompt and sets a standard for how AI-generated code should be validated.

## What This Means for AI Game Development in 2026

Claude of Duty arrives at a pivotal moment for AI-assisted game development. Several trends converge in this project:

### The Democratization of Game Prototyping

A single prompt can now generate a playable 3D FPS with physics, AI, weapons, and audio. This dramatically lowers the barrier to entry for game prototyping. Indie developers and hobbyists can iterate on game concepts in hours rather than weeks. The quality may not match AAA studios, but the speed of iteration is unprecedented.

### The Procedural Ceiling

The project honestly documents the limits of procedural generation. AI-generated textures, while impressive, cannot yet match photographed or hand-authored assets. The "procedural texture ceiling" is a real constraint — and it may be the hardest barrier for AI game generation to overcome. Until AI can generate photorealistic textures that rival captured data, AI-generated games will have a distinct visual signature.

### AI Agent Orchestration Matures

The OVERWATCH engine contract and the sequential-vs-parallel findings represent genuine advances in how we think about AI agent coordination. The insight that sequential single-owner passes outperform parallel fan-out is counterintuitive but well-supported by the data. Future AI game development tools will likely adopt similar patterns.

### The Honest Benchmark Culture

Perhaps the most important contribution of Claude of Duty is its culture of honest self-assessment. The README doesn't claim to have solved AI game generation. It openly scores itself 5.05/10, documents every weakness, and provides reproducible benchmarks. This stands in refreshing contrast to the hype-driven culture that often surrounds AI projects.

## Where It Falls Short — The Procedural Ceiling and Remaining Gaps

For all its technical ambition, Claude of Duty has clear limitations that define the current frontier of AI game generation:

1. **Visual fidelity ceiling** — Procedural textures, while varied (19 surface types), lack the realism of photographed PBR materials. The blocky viewmodel geometry and mannequin-like characters are immediately noticeable to any gamer.

2. **Performance constraints** — 28-30 fps at Retina resolution is playable but not competitive. Modern FPS games target 60-144 fps. The browser-based WebGL2 rendering pipeline, while impressive, cannot match native engine performance.

3. **No real global illumination** — Lighting relies on shadow mapping and screen-space effects. There is no baked lightmaps, no real-time ray tracing, and no voxel-based GI. This is the single biggest visual gap between Claude of Duty and modern AAA games.

4. **Limited gameplay scope** — The project is a technical demo, not a full game. It demonstrates core FPS mechanics but lacks campaign, multiplayer, progression systems, or the content volume of a commercial title.

5. **Single map** — The 120x120m market street is the only environment. There is no level editor, no modding support, and no way to extend the world without regenerating from the prompt.

## Conclusion — A Technical Marvel That Knows Its Limits

Claude of Duty is not a Call of Duty killer. It is something more valuable: a honest, reproducible benchmark of what AI-assisted game development can achieve in mid-2026. The project demonstrates that a single well-crafted prompt can orchestrate 55,000 lines of code across 11 subsystems, producing a playable 3D FPS with physics, AI, procedural audio, and dynamic lighting — all in a browser, with zero external assets.

The 5.05/10 score against Call of Duty is not a failure. It is a baseline. Future projects will build on these techniques, and the gap will narrow. The sequential-over-parallel finding, the shader pre-warming optimization, the adversarial critic loop, and the OVERWATCH engine contract are all contributions that will influence how AI game development evolves.

For developers, Claude of Duty is a must-study project. For gamers, it is a glimpse of a future where AI-generated games are indistinguishable from hand-crafted ones. That future is not here yet — but Claude of Duty shows the path.

## FAQ

### What is Claude of Duty?

Claude of Duty is an open-source project that generates a playable first-person shooter game in the browser from a single AI prompt. It uses Three.js r180 and WebGL2 to create approximately 55,000 lines of JavaScript across 11 coordinated subsystems with zero external art assets.

### How does the single prompt work?

The prompt instructs AI agents to fan out into specialized sub-agents for each game subsystem, use adversarial critics to score every frame against real Call of Duty, and iterate through a /loop pattern until quality targets are met. It is a structured orchestration prompt, not a simple text description.

### How does Claude of Duty compare to real Call of Duty?

In blind A/B testing with 11 adversarial AI critics, every critic in every round picked the real Call of Duty frame. The project scores itself 5.05 out of 10 against Call of Duty, with key weaknesses in character models, procedural textures, global illumination, and frame rate.

### What performance does Claude of Duty achieve?

After optimization, Claude of Duty runs at 28-30 fps (up from 12-17 fps initially). Boot time is 3.7-4.6 seconds (down from 9-12 seconds). Shader compilation during gameplay was eliminated entirely through pre-warming.

### Can I play Claude of Duty?

Yes, the project is open source under the MIT License and available on GitHub at github.com/mshumer/Claude-of-Duty. It runs entirely in the browser — no downloads or installations required.
