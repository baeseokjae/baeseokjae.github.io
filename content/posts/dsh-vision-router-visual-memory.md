---
title: "dsh-vision-router Visual Memory: Eyes for Text-Only DeepSeek Harness Agents"
date: 2026-09-10T06:34:16+00:00
tags:
  - deepseek harness
  - dsh vision router
  - vision plugin
  - multimodal
  - visual memory
  - text-only llm
description: "dsh-vision-router gives text-only DeepSeek Harness agents eyes: pixel-faithful vision routing, 14 vision tools, cached visual memory, and a free keyless fallback."
draft: false
cover:
  image: "/images/dsh-vision-router-visual-memory.png"
  alt: "dsh-vision-router Visual Memory: Eyes for Text-Only DeepSeek Harness Agents"
  relative: false
schema: "schema-dsh-vision-router-visual-memory"
---

dsh-vision-router is a DeepSeek Harness (DSH) plugin that gives text-only agents eyes by routing image turns to a separate vision model while DeepSeek stays the reasoning brain. It installs with one command, needs no Python and no API key, and ships 14 deep vision tools plus cached visual memory so a text-only agent genuinely remembers earlier images without re-spending vision calls.

## What is dsh-vision-router and why text-only DeepSeek agents need eyes

DeepSeek Harness is a local agent framework built around DeepSeek models. Many of its most popular models, including deepseek-v4-flash, are text-only: they declare `inputModalities: ["text"]` and simply cannot accept image attachments. That is a real limitation for agent work, because a growing share of tasks — reading a screenshot, checking a rendered UI, verifying a chart, OCRing a receipt — are fundamentally visual.

dsh-vision-router solves this by keeping the architecture clean: DeepSeek remains the brain, and a separate vision model becomes the eyes. When an image arrives, the plugin hands that turn to a vision model, gets a description or a structured result, and feeds it back to DeepSeek as ordinary text. Text turns are untouched in model, cost, and context. The plugin is free by default, runs with no Python, and installs in a single command.

The project has drawn real attention: it carries roughly 1,093 GitHub stars on the DSH Hub catalog (updated 2026-09-09) and about 1,021 stars with 44 forks on the ysr666 repository. That level of adoption signals that "text-only brain plus separate vision model" is not a niche hack — it is becoming the standard architecture for local multimodal agent work.

## The problem: DSH rejects images for text-only models (MODEL_DOES_NOT_SUPPORT_IMAGES)

The root problem is documented in the DeepSeek Harness discussions. When the active model is text-only, DSH rejects image attachments at the GUI/host admission layer with the error `MODEL_DOES_NOT_SUPPORT_IMAGES`. The model's `inputModalities` array simply does not include `"image"`, so the harness refuses the attachment before the agent ever sees it.

A common private-deployment setup tries to work around this by pairing a text-only main model with a separate multimodal "vision helper" — for example Qwen3.6-27B served through llama.cpp as an MCP server exposing a `describe_image(path)` function. That MCP workaround works when you can hand it a file path, but the GUI attachment path never yields a reference the agent can actually see. The image is dropped at admission, and the agent is left blind.

This is exactly the gap dsh-vision-router fills. Instead of fighting the admission layer, it patches the harness composition so image turns are routed to a vision-capable model before DeepSeek has to process them. The result is that pasting an image into a text-only DeepSeek session just works, like an ordinary tool-calling turn.

## Routing bridge vs description bridge: how dsh-vision-router keeps pixels faithful

Most DSH vision plugins take a "description bridge" approach: they convert an image into a text description up front, then feed that text to the model. This is lossy, one-shot, and blind to pixels. If the description misses a detail, the model never gets a second chance to look.

dsh-vision-router is a "routing bridge" instead. It hands the image turn straight to a vision model, pixel-faithful, and lets that model do the actual seeing. The vision model can crop, ground, compare pixels, run OCR, trace contours, and take screenshots — operations that a text description can never capture. DeepSeek then reasons over the structured result.

The plugin is capability-aware: it auto-routes based on measured evidence, never inferred from model names. It classifies errors (region, ToS, quota, rate-limit, context, network) and applies Retry-After-aware cooldowns, so a failing vision backend does not silently break the turn.

## One-command install and the "👁 Vision" composer control

Installation is a single command:

```bash
npx @deepseek-ai/dsh plugin --profile web add dsh-vision-router
```

Then restart `dsh web`. The plugin ships its own composition patch (`dsh.bundle.patch`), so there are no manual file edits to make. After restart, a "👁 Vision" composer control appears in the web UI, and pasting an image into the chat works like any ordinary tool-calling turn.

The plugin is verified against DSH 0.1.5-alpha.1 (v2.1.5), with stable Host support through 0.1.2-rc.1. It requires Node.js 22 or newer.

## The 14 deep vision tools and what each one does

The plugin exposes 14 deep vision tools (15 with the privacy-gated `vision_screenshot` opt-in). Here is what each one does:

| Tool | Purpose |
|------|---------|
| `vision_describe` | Free-form visual Q&A about an image |
| `vision_ground` | Ground a phrase to a bounding region in the image |
| `vision_detect` | Detect objects or regions of interest |
| `vision_crop` | Crop a region for closer inspection |
| `vision_present` | Present an image or region back to the model |
| `vision_pixel_diff` | Compare two images pixel-by-pixel and report the diff |
| `vision_colors` | Extract the dominant color palette |
| `vision_ocr` | Extract text from the image |
| `vision_trace` | Trace contours into SVG paths |
| `vision_extract_foreground` | Cut out the foreground subject |
| `vision_html_screenshot` | Render HTML to a screenshot |
| `vision_screenshot` | Take a screenshot (opt-in, privacy-gated) |
| `vision_long_screenshot_ocr` | OCR a long/scrolling screenshot |
| `vision_bootstrap` | Initialize the vision pipeline |

The pipeline runs on `sharp` (downscale, crop, pixel diff), `potrace` (SVG trace), `tesseract` (OCR), and system Chrome (HTML screenshots) — no Python required.

## Visual memory: how image answers are cached and reused

The "visual memory" in the keyword is the plugin's caching layer. Vision answers are cached by attachment content hash, so when the same image appears again in a later text turn, the plugin substitutes the recorded description — marked as untrusted evidence — without re-spending a vision call.

By default the cache keeps answers for `cacheTtlSeconds` of 3600 seconds (one hour) and up to `cacheMaxEntries` of 200 entries. This matters for two reasons. First, it saves cost and latency: the same screenshot referenced three times costs one vision call, not three. Second, it gives the text-only agent genuine continuity: it can "remember" an image from earlier in the conversation even though DeepSeek itself never saw the pixels.

## The free vision chain: OVHcloud fallback and free key channels

The plugin is free out of the box. It ships a built-in keyless OVHcloud anonymous fallback chain with 5 model buckets. The anonymous tier is capped at about 2 requests per minute per IP per model, which across the independent buckets works out to roughly 10 RPM in theory.

User-provided vision models always run first. If you add a free OVHcloud AI Endpoints access key, the same Qwen2.5-VL-72B-Instruct endpoint jumps to 400 requests per minute per project per model — a 200x improvement over the anonymous cap.

Free-tier vision policies rotate, so the plugin's "free vision key channels" note tracks the current landscape: Cerebras retired its free tier in July 2026, SambaNova dropped to 20 requests per day, and Hugging Face is now $0.10 per month. The keyless fallback means you are never blocked when a free key disappears.

## Local-first privacy: Ollama and LM Studio backends

For private or offline work, the plugin supports optional Ollama and LM Studio keyless vision backends. This is the local-first privacy path: recognition happens entirely on your machine, with no external endpoint and no data leaving the host. It is the right choice when the images are sensitive, when you are offline, or when you simply want zero external dependencies.

## The verifiable pixel loop for UI restoration

One of the plugin's most distinctive workflows is the verifiable pixel loop. Instead of eyeballing whether a UI rebuild matches a reference, you measure it:

1. Feed the reference image to the agent.
2. Use `vision_html_screenshot` to render the current implementation.
3. Use `vision_pixel_diff` to compare the two pixel-by-pixel.
4. Fix the mismatch, re-render, and repeat until the diff converges.

The project's demo verified a UI rebuild at a 2.54% final diff — 32,939 differing pixels out of 1,296,000, at a threshold of 16 per channel. That turns UI restoration from a subjective "looks close" into a measurable, converging number.

## Configuration essentials (routingMode, stealth, autoWrapProviders, cache)

The plugin's key configuration options:

- **routingMode** — how image turns are routed to vision backends (capability-aware auto-routing by default).
- **stealth** — optionally take over the official `deepseek-official` route so the model picker looks exactly like stock while each entry is an auto-vision wrapper.
- **autoWrapProviders** — automatically wrap provider entries so every model in the picker gets vision capability.
- **cacheTtlSeconds / cacheMaxEntries** — control the visual-memory cache lifetime and size (defaults 3600s and 200 entries).

## Troubleshooting common issues (BOM, sharp conflict, dsh-web-ui rewrite)

Three issues come up most often. First, a byte-order mark (BOM) in a config or patch file can break parsing — strip it if the plugin fails to load. Second, `sharp` can conflict with an existing native dependency in the project; resolve the version mismatch before the pipeline runs. Third, if you have customized `dsh-web-ui`, the plugin's composition patch may need to be re-applied after a rewrite, because the patch targets the stock UI structure.

## Alternatives compared

dsh-vision-router is not the only option. Here is how it stacks up against the main alternatives:

| Approach | How it works | Best for |
|----------|--------------|----------|
| dsh-vision-router | Routing bridge, pixel-faithful, 14 tools, free fallback | Text-only DeepSeek agents that need real vision |
| dsh-vision-sidecar / proxy | External vision service | Teams that already run a vision service |
| dsh-vision-toolkit | Tool collection, no routing | Simple, one-off vision calls |
| Pilco-mmbridge | Turns a text-only model multimodal without fine-tuning | Running multimodal benchmarks on text-only LLMs |
| MCP `describe_image` | File-path-based description helper | When you can pass file paths, not GUI attachments |

The plugin is a poor fit where the harness already provides the required vision route, or where external anonymous endpoints are unsuitable — the fallback is rate-limited to 2 req/min per IP per model. But for a text-only DeepSeek agent that needs real, pixel-faithful eyes with free fallback and cached visual memory, dsh-vision-router is the most complete option.

## FAQ

**Does dsh-vision-router require an API key?**
No. It works free out of the box with a built-in keyless OVHcloud anonymous fallback chain. You can optionally add your own vision model or a free OVHcloud key to lift the rate limit from ~2 to 400 requests per minute.

**Does it need Python?**
No. The entire pipeline runs on sharp, potrace, tesseract, and system Chrome. It requires Node.js 22 or newer.

**How do I install it?**
Run `npx @deepseek-ai/dsh plugin --profile web add dsh-vision-router`, restart `dsh web`, and a "👁 Vision" composer control appears. No manual file edits are needed.

**What is visual memory in dsh-vision-router?**
Vision answers are cached by attachment content hash (default 1-hour TTL, 200 entries). When the same image reappears, the plugin substitutes the recorded description without re-spending a vision call, so the text-only agent remembers earlier images.

**Which DeepSeek models does it support?**
It is designed for text-only models like deepseek-v4-flash that reject image attachments with `MODEL_DOES_NOT_SUPPORT_IMAGES`. It is verified against DSH 0.1.5-alpha.1 with stable Host support through 0.1.2-rc.1.
