---
title: "AutoDesign Agent Review: The Open-Source Design Agent That Beats Claude Design (2026)"
date: 2026-09-30T23:58:57+00:00
tags:
  - autodesign agent
  - open source claude design alternative
  - autodesign vs claude design
  - posterbench benchmark
  - paper to poster ai
description: "AutoDesign is an open-source design agent scoring 78.32 on PosterBench vs Claude Design's 70.87. A full 2026 review of the harness, costs, and limits."
draft: false
cover:
  image: "/images/autodesign-open-source-design-agent.png"
  alt: "AutoDesign Agent Review: The Open-Source Design Agent That Beats Claude Design (2026)"
  relative: false
schema: "schema-autodesign-open-source-design-agent"
---

The AutoDesign agent is an open-source design agent that turns one research paper into four editable artifacts — a poster, a slide deck, a webpage, and a narrated captioned video. Its authors report 78.32 on their own PosterBench benchmark against 70.87 for Anthropic's closed-source Claude Design, with model weights frozen the entire time.

That last clause is the part worth your attention. AutoDesign did not win by training a better model. It won by optimizing the system **around** a fixed model — the scaffold, the tools, the critics, the loop control — and then publishing that scaffold so it can be attached to Codex, Claude Code, Kimi Code, OpenCode, or DeepSeek Harness. The leaderboard number is the marketing. The reusable harness is the actual contribution.

This review covers what AutoDesign is, how the meta-harness optimization loop works, which comparisons hold up, which numbers are author-reported rather than third-party verified, and who should actually install it.

## What Is the AutoDesign Agent?

AutoDesign is an open-source agentic design system from a 14-author team spanning Meituan, MBZUAI, HUST, Peking University, Tsinghua, CUHK, and SJTU, published as the paper *AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design* (arXiv:2608.13560, submitted 13 August 2026) and released publicly on GitHub on 2026-08-14.

It ships two things that are frequently confused with each other:

- **The product**: a local-first application that takes a paper and produces an editable academic poster, slide deck, research webpage, or narrated 1080p video.
- **DesignHarness**: the reusable, model-agnostic artifact-production harness the project evolved for itself, portable into other coding agents.

The repository reports 229 stars, 10 forks, 3 releases, and 2 contributors as of 2026-09-30, with its last push on 2026-09-05. It contains an MIT `LICENSE` file ("Copyright (c) 2026 Yaxin Luo") — I verified that file directly at the repository's raw URL. One caveat: GitHub's license API field reported `NOASSERTION` for the same repository on 2026-09-30, so if you are planning commercial or client work, confirm terms with the authors rather than trusting either signal alone.

Documentation ships in English, Simplified Chinese, and Korean, which is unusual for a research-adjacent agent project and a real signal for non-English research communities.

## Why Is the Harness, Not the Model, the Real Story?

Because attaching DesignHarness to seven matched code-agent/model configurations improved **every single** configuration, by +5.01 to +19.56 points on PosterBench. The average score across those seven setups rose from 54.99 to 67.39 — a 12.40-point gain, roughly 22.6% relative, achieved without a single gradient update.

The largest gain is +19.56 points for Claude Code paired with DeepSeek V4 Pro (34.73 → 54.29). Native Codex with GPT-5.5 rose 75.87 → 81.46. Claude Code with Kimi K2.7 rose 57.20 → 70.12.

This is the most transferable finding in the paper, and it is not really about posters. If a learned scaffold can move seven different model stacks by 5 to 20 points on a design benchmark, then "which model is best" is the wrong first question for anyone building an agentic pipeline. The system design around the model is a lever of the same order of magnitude, and it is the cheaper one to pull — you can rewrite a harness in an afternoon; you cannot retrain Claude.

The paper's framing is explicit: a **design harness** is the system around a fixed LLM or MLLM that converts a multimodal source into a human-facing artifact through an execution trajectory. A **meta-harness** improves that surrounding system. AutoDesign learns from complete rollouts while keeping weights frozen.

## How Does the AutoDesign Pipeline Actually Work?

The architecture is two nested loops, five optimizable components, and four production stages. That decomposition is what makes it auditable rather than a black box.

### What are the two nested loops?

| Loop | What it improves | Mechanism |
|---|---|---|
| **Inner loop — artifact generation** | One editable artifact under a fixed harness | A **Designer** revises the artifact; a **Critic** returns localized feedback; their interaction forms an execution trajectory |
| **Outer loop — harness optimization** | The reusable harness across many tasks | A **MetaHarnessOptimizer** analyzes trajectories, evaluator scores, a persistent optimization record, and optional human guidance |

Every outer-loop iteration runs four stages: **rollout → evaluation → update proposal → acceptance**. The optimizer acts as a planner and code editor, updates **exactly one** harness component per iteration, and keeps the candidate only when training performance improves without regressing on an independent development set. Development trajectories are hidden from the update proposer — that is the anti-overfitting gate, and it is the detail that separates this from "we ran an agent in a loop and it got better."

### What are the five harness components?

| Component | What gets optimized |
|---|---|
| **Context and Memory** | Multimodal source management, task prompts, skills, reusable assets, persistent revision state |
| **Tools and Specifications** | Editable-artifact tools and specs for layout, typography, and provenance |
| **Execution Runtime** | Workspace and runtime for authoring, rendering, validating, exporting |
| **Orchestration** | Task routing, attempt budgets, loop control, candidate selection, fallback, finalization |
| **Evaluation and Feedback** | Rule-based validation, model-based critique, localized revision feedback |

### What happens in the four pipeline stages?

The optimized DesignHarness runs: **provenance-aware source ingestion** → **iterative editable HTML generation and revision** → **validation with dual critics** → **self-contained finalization**. Paper metadata, claims, figures, tables, and source locations become provenance-aware context. A coding-agent Designer edits native HTML. A rule-based validator plus a VLM critic return localized feedback. The best valid candidate is then made self-contained for delivery.

The current implementation permits up to **12 refinement attempts**. Blocking checks cover unsafe or missing assets, broken provenance, severe overflow or overlap, and required typography or layout constraints. If nothing passes within budget, the retained attempt history supports a constrained fallback before the same finalization stage.

The paper traces one real poster run across five selected attempts: the critic identifies a clipped analysis lane at attempt A1, A3 restores the fit, A5 refits the header, A6 rescales evidence, and A9 preserves the repaired composition and is accepted. Diagnostics drive localized edits, and valid layout plus source-derived content survive across revisions.

## What Does the PosterBench Leaderboard Actually Say?

PosterBench has two tracks: a 100-paper Main Track across five disciplines (AI/ML, biomedicine and health, climate and earth environment, economics and policy, physics and astronomy), and PosterBench-mini, a fixed 10-paper subset for controlled comparison. Every output is rendered to a common poster format before scoring.

Here is the full-scale Main Track, exactly as published in the AutoDesign README:

| Rank | Score | System | Design harness | Coding agent | Model |
|---:|---:|---|---|---|---|
| 1 | 78.32 | AutoDesign | DesignHarness | Claude Code | Claude 4.8 |
| 2 | 77.97 | AutoDesign | DesignHarness | Codex | GPT-5.5 |
| 3 | 73.37 | Codex | — | Codex | GPT-5.5 |
| 4 | 70.87 | Claude Design | Claude Design | Claude Code | Claude 4.8 |
| 5 | 70.01 | Claude Code | — | Claude Code | Claude 4.8 |
| 6 | 69.45 | OpenDesign | OpenDesign | Claude Code | Claude 4.8 |
| 7 | 62.17 | OpenDesign | OpenDesign | Codex | GPT-5.5 |
| 8 | 61.14 | Doubao | — | Claude Code | Seed 2.1 |
| 9 | 56.71 | PosterGen | — | — | Claude 4.8 |
| 10 | 52.22 | GLM | — | Claude Code | GLM 5.2 |
| 11 | 51.46 | Kimi | — | Claude Code | Kimi K2.7 |
| 12 | 49.09 | Any2Poster | — | — | Claude 4.8 |
| 13 | 46.01 | DeepSeek | — | Claude Code | DeepSeek V4 Pro |
| 14 | 44.61 | Paper2Poster | — | — | Claude 4.8 |

On the fixed 10-paper subset the ordering shifts: AutoDesign scores **81.46** with Codex + GPT-5.5, native Codex 75.87, AutoDesign 74.56 with Claude Code + Claude 4.8, OpenDesign 70.36, native Claude Code 69.55, Claude Design 66.83, OpenDesign with Codex 60.58, Kimi 57.20, Doubao 54.01, PosterGen 51.82, GLM 50.32, Any2Poster 46.88, Paper2Poster 42.06, DeepSeek V4 Pro 34.73.

The scores are computed across seven weighted dimensions — **Faithfulness 10, Coverage 10, Density 15, Visual Evidence 10, Layout 20, Readability 25, Aesthetics 10** — aggregated from programmatic evidence plus source-conditioned VLM judgments, and then capped by the strictest active ceiling for severe layout damage, insufficient presentation viability, confirmed visible failure, or protected render integrity. The mandated fair-comparison judge model is `gemini-3.5-flash`, and official runs must not pass `--allow-degraded-detectors`.

Two points of discipline matter here. First, the weight distribution tells you what the benchmark values: Readability (25) and Layout (20) carry 45% of the score, more than Faithfulness and Coverage combined. PosterBench is a design-quality benchmark as much as a content-fidelity one. Second, the metadata-only manifests are published on Hugging Face as `YaxinLuo/PosterBench` and `YaxinLuo/PosterBench-mini` — paper PDFs are not redistributed, so anyone reproducing the numbers supplies their own corpus.

## AutoDesign vs Claude Design: What Changes When the Design Agent Is Open?

Claude Design launched on 2026-04-17 as an Anthropic Labs research preview, powered by Claude Opus 4.7, cloud-only, paid, and locked to Anthropic's model and skills. It established the artifact-first mental model that AutoDesign, OpenDesign, and Open CoDesign all now copy: stop writing prose, ship a design artifact.

| Dimension | AutoDesign | Claude Design |
|---|---|---|
| License / cost model | Open source (repo ships MIT `LICENSE`) | Commercial, paid, cloud-only |
| Where it runs | Local-first; hosted demo retired | Anthropic cloud only |
| Model choice | Model-agnostic (Codex, Claude Code, Kimi Code, OpenCode, DeepSeek Harness) | Locked to Anthropic models |
| PosterBench (100 papers) | 78.32 (author-reported) | 70.87 |
| Scope | Academic artifacts: poster, deck, webpage, video | Briefs → designs, prototypes, slides, one-pagers |
| Provenance | Claims, figures, tables keep source location beside the run | Not documented |
| Editable output | Native HTML, text, tables, named assets | Design artifacts in Anthropic's environment |

The honest framing is narrower than "open source beats commercial." AutoDesign beats Claude Design **on academic poster production**, on a benchmark its own authors built. Claude Design is a general design product with a hosted experience, Anthropic's model pipeline, and no install cost. If your job is an A0 conference poster from a manuscript, AutoDesign is the better tool by its own measurements. If your job is a product landing page, neither product's validation covers you — and Claude Design is not claiming to be a poster tool.

## AutoDesign vs OpenDesign: Academic Specialist or General Workspace?

OpenDesign is the mainstream "open-source Claude Design alternative," and the adoption gap is not close: **98,937 stars and 11,459 forks** against AutoDesign's 229 stars as of 2026-09-30. It is Apache-2.0, TypeScript, created 2026-04-28, actively pushed 2026-09-30, with 1,165 open issues. It auto-detects 16 coding-agent CLIs (Claude Code, Codex, Cursor Agent, Gemini CLI, OpenCode, Qwen, Copilot CLI, Kimi, Pi, Kiro, Kilo, Hermes ACP, DeepSeek TUI, and more), drives them over stdio, and falls back to a BYOK proxy mode when no CLI is present. A commercial layer, the OpenDesign Go plan, starts around $8 for the first month with monthly credits across 10+ models.

| Dimension | AutoDesign | OpenDesign |
|---|---|---|
| Stars / forks (2026-09-30) | 229 / 10 | 98,937 / 11,459 |
| License | Repo ships MIT `LICENSE` (API field: NOASSERTION) | Apache-2.0 |
| Scope | Academic artifacts from a paper | General product design: prototypes, landing pages, dashboards, slides, images, video |
| PosterBench Main Track | 78.32 | 69.45 (Claude Code + Claude 4.8), 62.17 (Codex + GPT-5.5) |
| PosterBench 10-paper | 81.46 / 74.56 | 70.36 / 60.58 |
| Maintenance signal | 2 contributors, last push 2026-09-05 | Actively pushed 2026-09-30, 1,165 open issues |
| Team workflow | Single-user local run | Collaborative workspace, design systems, plugins |

This is a scope difference, not just a score difference. OpenDesign is a design workspace where your coding agent is the engine; AutoDesign is a paper-to-artifact specialist with a published poster benchmark. AutoDesign wins academic posters. OpenDesign wins product design, team collaboration, and ecosystem maturity.

A third option worth naming: **Open CoDesign** (7,984 stars, 838 forks, 88 open issues, MIT, local-first Electron desktop app) targets UI prototypes, decks, and prompt-to-artifact work, positioned against Claude Design, v0, Lovable, Bolt, and Figma AI. It is neither a poster tool nor a general workspace.

## AutoDesign vs Paper2Poster, P2P and PosterGen: What Is the Academic Lineage?

AutoDesign did not invent paper-to-poster. The real research lineage runs PosterBot (AAAI-22) → Paper2Poster / PosterGen / Any2Poster (2025) → AutoDesign + PosterBench (2026).

- **Paper2Poster** (3,972 stars, NeurIPS 2025 Datasets and Benchmarks Track, arXiv 2505.21497) introduced the first benchmark and metric suite for poster generation, with a Parser → Planner → Painter-Commenter pipeline. Its efficiency claim still stands: a 22-page paper to an editable `.pptx` for roughly **$0.005** using open-source Qwen-2.5 variants, with 87% fewer tokens than GPT-4o multi-agent systems. On PosterBench it scores 44.61 — the lowest-ranked academic baseline in the comparison, and the clearest illustration that "first benchmark" is not "best system."
- **PosterGen** (arXiv:2508.17188) is the closest architectural predecessor: a four-agent Parser/Curator → Layout → Stylist → Renderer pipeline with a VLM-based rubric for layout balance, readability, and aesthetic coherence — the direct ancestor of PosterBench's dimension scoring. It scores 56.71.
- **P2P** (56 stars, ICLR 2026) takes the competing evaluation philosophy: three specialized agents (Figure, Section, Orchestrate) with checker modules and reflection loops producing HTML posters, plus **P2PEVAL** (1,738 checklist items) and **P2PINSTRUCT** (~30,000 instruction examples). Its human-preference numbers set the bar AutoDesign is now measured against: 83.05% preferred-or-tied against Tencent YuanBao and 57.63% against original author-made posters. That is human-annotated checklist evaluation, not a weighted rubric with score ceilings.

The benchmark-philosophy split is the interesting one. PosterBench is a seven-dimension weighted rubric with a mandated judge model and record-level ceilings; P2PEVAL is a large human-annotated checklist with a trained preference model. Neither is obviously correct, and the disagreement is exactly why you should treat any single poster benchmark score as provisional.

## How Much Does the DesignHarness Actually Add?

| Fixed code agent + model | Without DesignHarness | With DesignHarness | Gain |
|---|---:|---:|---:|
| Codex + GPT-5.5 | 75.87 | 81.46 | +5.59 |
| Claude Code + Kimi K2.7 | 57.20 | 70.12 | +12.92 |
| Claude Code + DeepSeek V4 Pro | 34.73 | 54.29 | +19.56 |
| **Average across 7 configurations** | **54.99** | **67.39** | **+12.40** |

The gain band is +5.01 to +19.56 points. Notice the shape of it: the harness helps the *weaker* model stacks the most. DeepSeek V4 Pro behind Claude Code gains nearly 20 points; native Codex + GPT-5.5, already strong, gains 5.59. That is a scaffolding effect — the harness compensates for what the underlying agent does not do well on its own, and its ceiling value is highest exactly where the model is cheapest. Controlled tracks on the 10-paper subset point the same way: holding AutoDesign and GLM 5.2 fixed, choosing Kimi Code as the coding harness yields 82.31 versus 64.33 for Claude Code and 69.53 for ZCode.

## What Does One Poster Cost in Time and Money?

A fully autonomous long-horizon run executes **253 tool calls and 11 editing turns in about 40 minutes for under $3** per paper (arXiv:2608.13560 abstract). Compare that to the baseline it replaces: commercial poster-tool documentation puts manual conference-poster production at **6–12 hours** per poster, most of it layout rather than intellectual work.

The cost-performance Pareto frontier on the fixed 10-paper subset is the practically useful table for a lab choosing a model route:

| Model route | PosterBench (10 papers) | Normalized designer-only cost |
|---|---:|---:|
| LongCat 2.0 | 55.13 | $0.27 |
| Doubao Seed 2.1 Pro | 71.83 | $2.75 |
| Claude 4.8 | 74.56 | $7.63 |
| GPT-5.5 | 81.46 | $10.02 |

Doubao Seed 2.1 Pro reaches **88% of the GPT-5.5 score at 27% of its normalized designer-only API cost**. For most labs producing conference posters on a deadline, that is the rational pick; GPT-5.5 buys the last 9.6 points at 3.6× the price. LongCat 2.0 at $0.27 is the floor — 55.13 points, roughly where a bare agent stack with no harness sits.

One caveat on the arithmetic: the "under $3" figure in the abstract is a single fully autonomous run, while the Pareto table reports normalized designer-only API cost on the 10-paper subset. They are different accounting scopes. Do not multiply $2.75 by your poster count and expect to match the $3 headline.

## Does the Benchmark Match Human Taste?

Partly — and the paper reports the gap itself, which is unusual and worth crediting.

The system-blind human study collected **936 responses from 11 volunteer reviewers**: 933 ranking judgments and 3 skips. AutoDesign holds the highest Bradley–Terry estimate at **64.0%** (95% interval 55.2–77.8%). Its tie-adjusted empirical preference is 61.3% versus Claude Code, 63.1% versus OpenDesign, and **67.6% versus Claude Design**.

Then the honesty: PosterBench correlates only **r = 0.34** (95% interval 0.22–0.44) with human preference. Agreement with the benchmark-preferred poster is **51.9%** when the score gap is 0–3 points — essentially a coin flip — and rises to **74.4%** only when the gap reaches 20 points or more.

The practical translation: a 7.45-point PosterBench lead over Claude Design is real evidence, but it is not a guarantee that a human will see a better poster. If you are choosing between two systems within a few points of each other, the benchmark cannot decide it for you — render both on your own paper and look.

## One Paper, Four Artifacts — and What Is Actually Validated?

The "Paper All-in-One" claim is one paper in, four artifacts out:

- **Poster** — editable HTML, one-page PDF, preview, provenance
- **Slide deck** — 24-slide formal academic talk as editable HTML, native editable PPTX, PDF
- **Webpage** — responsive editorial research project page, local HTML plus assets, desktop/mobile QA
- **Video** — six-minute 1080p narrated MP4 with AAC audio, transcript, and timed SRT/VTT subtitles, plus an editable HyperFrames project

The validation boundary is the part the marketing tends to skip, and AutoDesign's own README states it plainly: PosterBench formally validates **academic posters only**. Slides, webpages, and videos are pilot outputs whose research claims still lack medium-specific source–output data, evaluators, rendering and validation gates, and communication objectives to match the poster pipeline. The demo artifacts — AutoDesign's own paper rendered into its own Figure 2 poster, a 24-slide talk, a landing page, and a six-minute conference video — are real outputs, not mockups, but they are demonstrations, not benchmarked claims.

There is also a concrete design constraint worth knowing before you install: all four standalone Agent Skills require an **opaque white primary canvas** with no background image or paint effect that changes the rendered white. That exists so the paper's usual white-background figures stay visually coherent. Restrained light cards, panels, controls, captions, and overlays are allowed as local surfaces. If you want a dark-mode poster, the Skills edition is not the workflow for you.

## How Do You Install and Run It?

The hosted demo has been retired. `designanything.ai` now states generation is local-install only, so papers, API keys, and results stay on your machine. That is a genuine selling point for unpublished or confidential manuscripts — and it moves install and maintenance cost onto you.

| Route | Prerequisites | Commands |
|---|---|---|
| One-command launcher | Node.js 22+, `ffmpeg`/`ffprobe` | `curl -fsSL https://designanything.ai/install.sh \| bash` then `autodesign start`; verify with `autodesign doctor` |
| Source build | Python 3.10+, `uv`, Node.js 22+, npm, Playwright browsers, `ffmpeg`/`ffprobe` | `uv sync`; `uv run python scripts/install_playwright_browsers.py`; `cd runtime/video && npm ci --omit=dev`; `cd ../../web && npm install` |
| Agent Skills only | An existing coding agent (Codex, Claude Code, DeepSeek Harness) | Install the standalone `autodesign-poster`, `-ppt`, `-webpage`, or `-video` Skill; no AutoDesign server required |

The launcher installs under `~/.local/share/autodesign`, keeps state under `~/.autodesign`, and migrates existing `~/.designanything` state with a compatibility symlink. Single-run output lives under `out/runs/<run_id>/`, ignored by Git. The canonical module and launcher names are `autodesign` and `AUTODESIGN_*` environment variables; the older `design_anything` / `designanything` aliases are deprecated.

The **Agent Skills** route is the one most people should try first. Version 0.2.0 (2026-08-19) ships four independently installable, checksum-verified archives that run inside your existing coding agent, keeping editable artifacts, evidence, attempts, and review state in an output directory you choose, with no application server. The project's own guidance is explicit and worth repeating: the Skill edition is the convenient portable way to use part of AutoDesign, and it is **not** a replacement for the full harness when you are judging output quality.

## What Are the Honest Limits?

- **Author-run evaluation.** The team that built the harness also built PosterBench and ran the evaluation, using their own judge protocol (`gemini-3.5-flash`). Treat 78.32 vs 70.87 as author-reported, not third-party verified. The mitigations are real — a frozen protocol distinct from the optimization-time evaluator, a fixed 10-paper subset, a mandated judge model, a documented train/development split — but they are self-imposed.
- **Benchmark–human alignment is weak.** r = 0.34, with 51.9% agreement on close scores. Quote that next to any score.
- **Maturity.** 229 stars, 10 forks, 2 contributors, last push 2026-09-05. This is a research artifact with a paper attached, not a maintained product. Compare with OpenDesign's actively pushed repository and 1,165 open issues of lived friction.
- **Poster-only validation.** Slides, webpages, and videos are pilots without medium-specific evaluation.
- **Autonomy still loses to a competent human nudge.** A commentary on the paper reports a representative case moving 49.00 (bare starting harness) → 80.88 (autonomous plateau) → **88.39** once a human redirects the search. Build the review step in; do not trust the loop blindly.
- **License metadata is ambiguous.** A MIT `LICENSE` file exists (verified directly), while GitHub's API reports `NOASSERTION`. Confirm before commercial use.
- **The print-production last mile is unsolved across the category.** Roundups of AI poster generators find almost no tool stating a DPI figure, and one explicitly disclaiming print resolution, colour matching, and bleed. AutoDesign's HTML-first pipeline inherits that same gap: verify output at your conference's print size and DPI yourself.
- **The category is nascent.** The AutoDesign arXiv submission drew 2 points and 0 comments on Hacker News; "Viable open source Claude Design alternative?" (2026-05-14) drew 26 points and 7 comments. The keyword space is genuinely uncrowded — and so is the peer-review space.
- **Ecosystem noise.** Several cloned repositories reuse OpenDesign's README copy verbatim, so verify star counts and licenses against the canonical org before citing a project.

## Who Should Use the AutoDesign Agent?

| Your situation | Recommendation |
|---|---|
| Researcher producing an A0/A1 conference poster from a manuscript | Strong fit. Under $3 and ~40 minutes versus 6–12 hours of manual layout, with editable HTML you can correct instead of regenerate |
| Lab standardizing poster production across many papers | Strong fit. Use Doubao Seed 2.1 Pro at ~$2.75 for the quality/cost knee, or GPT-5.5 if the last 9.6 points matter |
| Unpublished or embargoed work that cannot leave the machine | Strong fit. Local-first with your own API keys, hosted demo retired |
| You want editable output, not a flattened image | Strong fit. Native HTML, text, tables, and named assets stay revision-capable |
| You need project webpages or conference videos | Conditional. Pilots only, without PosterBench-grade validation |
| Product/UI design, landing pages, team collaboration | Not this. Use OpenDesign (98.9k stars, Apache-2.0) or Open CoDesign (MIT) |
| You need a hosted, zero-install experience | Not available. The demo is retired; expect Node 22+, ffmpeg, and maintenance |
| You need commercial license clarity before client work | Confirm with the authors first — the license metadata is ambiguous |

## Verdict

AutoDesign is the most substantiated open-source claim in the paper-to-artifact category right now, and it is substantiated in an unusual way. It beat a closed commercial design system — 78.32 against Claude Design's 70.87 — not by out-training it, but by evolving the scaffold around frozen weights across 7 days of traces, 224 subagent invocations, 123+ recursive iterations, and 54 accepted harness updates. The reusable result, DesignHarness, then lifted seven different code-agent/model stacks by 5 to 20 points.

The right response to a leaderboard like this is not to quote 78.32. It is to install it, render your own poster, and compare the result against the 6–12 hours you currently spend on layout. The paper tells you where to look: at 51.9% human agreement on close score gaps, the benchmark cannot see a 7-point lead — only your eyes at print size can.

If you want the harness-not-model lesson without the poster workflow, the transferable takeaway stands on its own. Attaching a learned scaffold to a fixed model moved scores more than most model upgrades move them. That is worth testing on your own agent stack before you spend the next budget cycle on a bigger model.

## FAQ

**Is AutoDesign really open source?**
Yes, with a caveat. The repository ships an MIT `LICENSE` file reading "Copyright (c) 2026 Yaxin Luo," which I verified directly at the raw URL. GitHub's license API field reported `NOASSERTION` for the same repository on 2026-09-30. For personal and academic use this is a non-issue; for commercial or client work, confirm terms with the authors first.

**Does AutoDesign actually beat Claude Design?**
On PosterBench's 100-paper Main Track, AutoDesign scores 78.32 versus Claude Design's 70.87 — a 7.45-point lead, with Claude Code + Claude 4.8 held fixed for the primary comparison. That result is author-reported on a benchmark the same team built. It is also not a guarantee of visible quality: PosterBench correlates only r = 0.34 with human preference, and reviewers agree with the benchmark just 51.9% of the time on score gaps of 0–3 points.

**Can I use AutoDesign with Codex or Claude Code instead of its own runtime?**
Yes, two ways. DesignHarness is harness-agnostic and model-agnostic, benchmarked across Codex, Claude Code, Kimi Code, ZCode, and OpenCode with Claude 4.8, GPT-5.5, Kimi K2.7, GLM 5.2, Seed 2.1 Pro, LongCat 2.0, and DeepSeek V4 Pro. Separately, four standalone Agent Skills (`autodesign-poster`, `-ppt`, `-webpage`, `-video`) install directly into Codex, Claude Code, or DeepSeek Harness without running the AutoDesign server. The project warns that the Skills edition does not replace the full harness when judging output quality.

**What does it cost to generate one poster?**
A fully autonomous run executes 253 tool calls and 11 editing turns in about 40 minutes for under $3 per poster. Model choice moves that materially: on the fixed 10-paper subset, the Pareto frontier runs from LongCat 2.0 (55.13 points at $0.27) through Doubao Seed 2.1 Pro (71.83 at $2.75) and Claude 4.8 (74.56 at $7.63) to GPT-5.5 (81.46 at $10.02). Budget for your own API key — the hosted demo is retired and everything runs locally.

**Does AutoDesign produce print-ready posters I can send to a conference printer?**
It produces editable HTML, a one-page PDF, and a preview, with poster canvas controls for aspect ratios and exact pixel sizes added on 2026-08-19. That is far better than a flattened image. But the project's validation covers poster design quality, not print production: no DPI, colour-matching, or bleed guarantee is published. Convert the HTML to print-resolution PDF at your conference's required size and verify the result yourself before submitting.

## Sources and Methodology

- [AutoDesign repository](https://github.com/Yaxin9Luo/AutoDesign) — README, `agent_skills/README.md`, `eval/README.md`, `LICENSE` (fetched 2026-09-30)
- [AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://arxiv.org/abs/2608.13560) (arXiv:2608.13560, 13 August 2026)
- [PosterBench dataset](https://huggingface.co/datasets/YaxinLuo/PosterBench) and PosterBench-mini on Hugging Face (metadata only)
- [OpenDesign repository](https://github.com/nexu-io/open-design); [Open CoDesign repository](https://github.com/OpenCoworkAI/open-codesign)
- [Paper2Poster](https://github.com/Paper2Poster/Paper2Poster) (NeurIPS 2025 D&B, arXiv:2505.21497); [P2P](https://github.com/multimodal-art-projection/P2P) (ICLR 2026); PosterGen (arXiv:2508.17188); PosterBot (AAAI-22)
- [Claude Design announcement](https://www.anthropic.com/news/claude-design-anthropic-labs) (Anthropic Labs, 2026-04-17)
- Commercial poster-generator documentation: [ChatSlide research poster guide](https://www.chatslide.ai/guides/research-poster-presentation-ai-guide), [PaperBanana scientific poster maker](https://paperbanana.me/scientific-poster-maker), [SciSpace poster generator](https://scispace.com/agents/scientific-poster-generator-vl135up1)
- Repository metrics via the GitHub API and repository pages on 2026-09-30; Hacker News interest via the HN Algolia API on 2026-09-30

Methodology note: all PosterBench scores, human-evaluation figures, cost figures, transfer gains, and repository metrics in this article are reported by their respective sources and are reproduced with attribution. Where a figure is author-reported rather than independently verified, the article says so in the sentence that carries the number. License status was checked two ways — the raw `LICENSE` file and GitHub's license API field — and the discrepancy is reported rather than resolved.
