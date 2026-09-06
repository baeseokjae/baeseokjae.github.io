---
title: "Vecline: Bit-Exact SVG and Document Toolkit for Measurable AI Image Output"
date: 2026-09-06T16:02:14+00:00
tags:
  - SVG
  - Image Conversion
  - Vectorization
  - MCP
  - Tools
  - AI Agents
description: "Vecline is a bit-exact SVG and document toolkit that turns logos and icons into lossless SVG (SSIM 1.0) and measures its own output with real metrics."
draft: false
cover:
  image: "/images/vecline-bit-exact-svg-ai-image-toolkit-2026.png"
  alt: "Vecline: Bit-Exact SVG and Document Toolkit for Measurable AI Image Output"
  relative: false
schema: "schema-vecline-bit-exact-svg-ai-image-toolkit-2026"
---

Vecline is a bit-exact SVG and document toolkit that converts flat art — logos, icons, UI, screenshots, pixel art — into editable SVG with perfectly measured output: SSIM 1.0000, PSNR infinity, zero differing pixels. Unlike most vectorizers that claim close-enough accuracy, Vecline re-renders every SVG it produces and scores it against the source, and its lossless mode fails rather than returning a near-miss. Built for JavaScript as a zero-dependency core with an MCP server, it is the honest answer to overhyped "100% accuracy" vectorizers.

## What Is Vecline and Why "Measured, Not Asserted" Matters

When you vectorize an image, almost every tool on the market leans on a single, unverifiable promise: "trust us, it's accurate." Weirdly, in the age of AI that produces images by the thousands — whether you are [choosing a generator](https://baeseokjae.github.io/posts/best-ai-image-generators-2026/) or building a [ComfyUI pipeline](https://baeseokjae.github.io/posts/comfyui-workflow-ai-image-generation-guide-2026/) — most raster-to-SVG conversion remains an act of faith. You run potrace or vtracer, eyeball the result, and hope the curves look fine at print size.

Vecline is built on a different assumption. Instead of claiming accuracy, it *measures* it. The vectorizer renders the SVG it just produced back to pixels, then compares that render against the input using structural similarity (SSIM), peak signal-to-noise ratio (PSNR), and the CIEDE2000 colour-difference metric. If the result is bit-exact, the tool says so and you can see the numbers. If it is not, it tells you what it actually achieved.

This distinction is the whole product thesis. Most vectorizers guarantee their *method* — "we trace with Bézier curves." Vecline guarantees an *outcome* that it can prove. That is a meaningful difference when you are feeding generated images from an AI model into a design pipeline where one dropped pixel of a logo's edge becomes a visible artifact at 300 DPI.

## The Bit-Exact Promise: SSIM 1.0000 and the Five Conversion Modes

Vecline ships four conversion modes, plus a fifth behaviour for photographs, and each one is enforced by measurement rather than construction.

**`auto` (default).** Vecline inspects the artwork, guesses what strategy preserves the most information, and applies it. For flat graphics it does the exact work; for photos it falls back to embedding.

**`lossless`.** This is the mode that separates Vecline from everything else. It returns bit-exact SVG or it *errors out*. There is no silent near-miss. On a real logo, lossless mode returns a 24.0 KB SVG at SSIM 1.0000 — about a third of what imagetracerjs (64 KB) and vtracer (60 KB) spend while *only approximating* the same image. You are not trading quality for size here; you are getting a smaller file that is literally pixel-identical.

**`pixel`.** Produces genuine editable geometry — real rectangle and path shapes, one per pixel run — that rasterises back to the input with zero differing pixels. This is not "visually identical"; it is bit-exact, and it is editable, unlike a flat bitmap inside an SVG.

**`trace`.** The Bézier mode, used for photographs and organic shapes. This is approximate by nature and Vecline says so plainly. It reports the measured SSIM/PSNR after tracing, so you always know exactly how close the approximation landed.

**`embed`.** For photographs where vector geometry would be absurdly large, Vecline puts the real bitmap inside the SVG. This is bit-exact by construction, and it reports the size ratio so you understand the cost.

A single fact explains why photographs can never be auto-vectorised to exact geometry: a photograph holds more independent information than any compact set of Bézier curves can encode. Vecline documents this honestly rather than pretending otherwise. If you force it, it can emit a photo as exact geometry — but a 320x240 photo becomes a 1.99 MB file of 42,933 shapes, which is why auto mode uses embed and tells you the ratio instead.

## How It Stacks Up Against potrace, imagetracerjs, and vtracer

The best evidence is the official comparison harness at vecline.xyz/compare.html. Crucially, every tool's SVG is rendered with the *same* renderer and scored with the *same* metrics on the same white ground — so the comparison is apples to apples, not "our renderer vs our renderer."

**On flat art, Vecline is the only bit-exact contender.** potrace, imagetracerjs, and vtracer all approximate curved edges and antialiased pixels. Vecline lossless mode reaches SSIM 1.0000 where the others top out "visually identical." For logos, icons, favicons, and UI assets, that is the difference between shipping something exact and shipping something close.

**On photographs, Vecline leads SSIM across the board.** In the Kodak set at 480px, auto mode scored 0.9140 / 0.9453 / 0.8460 against vtracer's 0.7652 / 0.7624 / 0.7949 and imagetracerjs's 0.7093 / 0.7465 / 0.7615. PSNR tells the same story: 34.8 / 36.3 / 31.2 dB versus vtracer's 25.9 / 24.3 / 23.2. That is a materially better perceptual result on real photos.

| Tool | Flat-art exactness | Photo SSIM (best) | Photo PSNR (dB) | Small-logo speed |
|------|-------------------|-------------------|-----------------|------------------|
| Vecline (auto/lossless) | **Bit-exact (SSIM 1.0)** | **0.9453** | **36.3** | 280 ms |
| vtracer (Rust/OpenCV) | Approximate | 0.7652 | 25.9 | **69 ms** |
| imagetracerjs | Approximate | 0.7093 | 23.2 | ~180 ms |
| potrace | Approximate | N/A (binary) | N/A | — |

**Now the honest parts where Vecline is not the winner.** The maintainer publishes these trade-offs openly, and you should know them before adopting it:

- Vecline is slower than imagetracerjs on every fixture — 1.10x to 1.55x.
- On a small logo it is 4.08x slower than vtracer (280 ms vs 69 ms), largely due to Node module load overhead on small inputs.
- But on the two heavier photographs, Vecline beats vtracer in wall-clock time (portrait: 1001 ms vs 1386 ms), because the Node startup cost amortises away on bigger workloads.

So the honest rule of thumb: if you need raw speed on thousands of tiny icons, vtracer holds the crown. If you need any degree of exactness, or high-quality photo output, Vecline wins where it counts — in the output, not just the timer.

## A Full Document Toolkit, Not Just a Vectorizer

What makes Vecline more than a one-trick SVG tool is the breadth of the pipeline around it. The package reads and writes an 11x11 = 121-format conversion matrix — every format it reads, it writes: PNG, JPEG, WebP, AVIF, TIFF, GIF, BMP, ICO/CUR, PNM, TGA, and SVG — all run in CI on every commit so the claim never rots.

The measurement discipline extends to geometry. A plain disc renders as a real `<circle>` rather than a path — 68% smaller — and a four-slice pie chart goes from 2,323 bytes of Bézier curves down to 488 bytes of genuine arc shapes. That matters for CAD and DXF because real arcs and circles stay editable and true, rather than being flattened into hundreds of curve segments. Gradients get the same treatment: a synthetic vignette reconstructs as a radial SVG gradient at 0.998 SSIM in about 350 bytes, where flat bands would take 3–8 KB and score only 0.73–0.88.

For makers, Vecline Studio exports DXF with real physical cut size, alongside EPS, PDF, G-code, colour separations, sprite sheets, favicons, and BlurHash. That turns it into a real raster-to-fabrication pipeline — from a screenshot to a laser cut or CNC path — not just a developer utility. It also converts PDFs (via mupdf-WASM) and Office documents (via `vecline serve`, a local LibreOffice bridge), and `doc_to_images` and `images_to_pdf` round out the document side.

## Vecline for AI Agents: An MCP Server That Lets Models Verify Their Own Output

The most interesting angle for anyone building on LLMs is the MCP server. `vecline mcp` is officially registered under `io.github.shunyagatha/vecline` on the Model Context Protocol registry and on Smithery, and it exposes twelve tools: `vectorize`, `convert`, `centerline`, `measure`, `diff`, `crop`, `doc_to_images`, `office_convert`, `images_to_pdf`, `palette`, `placeholder`, and `image_info`.

The two tools that matter for AI agents are `measure` and `diff`. Both work by rendering the result back and computing real SSIM / PSNR / CIEDE2000. That means an agent — Claude, Codex, VS Code, Cursor — can call `vectorize`, then call `measure` or `diff` on its own output and *verify numerically* that the conversion actually succeeded instead of asserting it. That is a genuinely rare capability: most image tools return success because the function returned, not because the output is correct.

All twelve tools run with `openWorldHint: false` — nothing touches the network. Three are read-only and eight are destructive, and the destructive ones are annotated. There is even a one-click `.mcpb` launcher. For a team worried about a model silently corrupting an image asset, this is the closest thing to a self-checking loop in the ecosystem.

This dovetails with the wider theme of reliable tool use in agentic pipelines, the same "measure, don't assume" philosophy that applies to [generating images with open models like FLUX.1](https://baeseokjae.github.io/posts/flux-1-image-generation-developer-api-guide-2026/). Just as MCP itself has become the connective tissue of agent workflows, a tool that lets the model verify geometry numerically fits squarely in that camp.

## Vecline Studio: Free, Private, In-Browser and Offline

Vecline Studio (vecline.xyz) is the free, private, in-browser companion. Everything runs inside the tab in a Web Worker — there is no backend, no upload, no account. It works offline once cached. It measures its own output the same way the CLI does, rendering the SVG it produced and reporting real SSIM/PSNR/CIEDE2000 alongside a bit-exact badge. It even handles TGA/PNM/ICO formats that browsers cannot natively read, so the format breadth survives in the browser too.

The privacy model is worth calling out because cloud vectorizers are the norm. Competitors that host the conversion upload your artwork to their servers, often charging per image and retaining whatever they process. Vecline's Studio keeps the entire operation local-first: no upload means nothing can be retained, leaked, or used to train anything. That is a real contract for teams working with confidential UI or client logos.

## Privacy, Licensing, and the Honest Engineering Culture

Vecline collects nothing — no server, no analytics, no telemetry, no account. Every conversion, tracing, measurement, crop, PDF, and Office render runs on your own machine. The core `vecline/core` engine has zero dependencies and no Node built-ins, and CI asserts it bundles for a browser at about 96 KB minified, with a size tripwire so it cannot creep up silently.

The npm package `vecline` is v2.1.4, MIT-licensed, Node.js >= 18.17, with a `vecline` binary. Vecline Studio is source-available rather than open source, so be clear-eyed there: the CLI and core are MIT; the studio app is not FOSS in the strict sense.

The honest engineering culture is arguably the most distinctive thing about the project. The author publishes measured trade-offs rather than burying them, calls out vtracer's genuinely better small-logo speed and potrace's smaller output, and has even corrected earlier false claims in the changelog. In a tooling market full of inflated benchmarks, that willingness to publish where you lose is rare and worth rewarding.

## Limitations and Caveats You Should Know Before Adopting It

Be honest about what Vecline is *not* before you bet a pipeline on it.

- **Photographs cannot be bit-exact in vector form.** The information-theoretic limit is real. If you need lossless photo *vectors*, you are really asking for embedded bitmaps, not geometry. Vecline will tell you the truth; make sure your expectations match.
- **Speed.** The core is slower than imagetracerjs on every fixture, and 4x slower than vtracer on small logos due to Node startup. If you are batch-converting tens of thousands of 16px icons, that overhead compounds and vtracer may be the pragmatic choice.
- **License asymmetry.** The CLI and core are MIT, but Vecline Studio is only source-available. If your company mandates strict FOSS, verify which component you are allowed to redistribute or extend.
- **Brittle edges in exotic formats.** The 121-format matrix is impressive, but the CI coverage is about format *round-trips*, not about matching what Adobe Photoshop writes for every possible TIFF flag. Treat obscure-feature edge cases as verify-before-trust territory.
- **DXF at physical size is a feature, not a guarantee.** It computes a real cut size, but that still assumes your machine setup matches; double-check units before you hit run on a laser cutter.

## Verdict: Is Bit-Exact SVG the 2026 Standard for AI Image Output?

I believe yes, or at least it should be. When AI models now generate thousands of images per hour, "looks approximately right" is no longer an acceptable default for anything that will be printed, exported, fabricated, or reused as an asset. Measured, falsifiable output — with SSIM and PSNR numbers you can read on a badge — turns vectorization from a subjective craft into an objective operation you can put in a CI pipeline and sleep on.

Vecline is not the fastest tool in every corner, and it does not pretend to be. It is the tool that makes exact output the *default guarantee* for anything flat, gives you honest measurements when exactness is impossible, and — via the MCP server — lets an AI agent check its own work numerically. For a developer feeding generated images into a design-to-fabrication pipeline, that combination of verified quality, local-first privacy, and self-measuring agents is a genuinely stronger default than the "trust us" vectorizers.

## Frequently Asked Questions

**What is Vecline?**
Vecline is an MIT-licensed JavaScript toolkit that converts rasters (PNG, JPEG, WebP, AVIF, TIFF, GIF, BMP, ICO, PNM, TGA) into SVG and measures its own output. On flat art it produces bit-exact SVG — SSIM 1.0000, PSNR infinity, zero differing pixels — by rendering the result back and comparing it to the source.

**How is bit-exact different from "visually identical"?** Bit-exact means every output pixel equals the input with zero differing pixels, verified numerically, not judged by eye. Most vectorizers (potrace, imagetracerjs, vtracer) approximate curves and antialiasing; Vecline's lossless and pixel modes reach literal pixel-perfect output and fail rather than deliver a near-miss.

**Which Vecline mode should I use?** Start with `auto` for mixed workloads. Use `lossless` when you need guaranteed bit-exact output on flat art (it errors out if it cannot achieve it), `pixel` for editable bit-exact geometry, `trace` for photographs where you accept an approximation, and `embed` when a photo's exact geometry would be impractically large.

**Is Vecline faster than vtracer?** No. Vecline is 4.08x slower than vtracer on small logos (280 ms vs 69 ms, mostly Node startup) and 1.10x–1.55x slower than imagetracerjs. But on heavier photographs it wins in wall-clock time (1001 ms vs 1386 ms). Choose vtracer for bulk tiny-icon speed; choose Vecline for exactness and photo quality.

**Can Vecline vectorise photographs bit-exactly?** No, and it is upfront about it: a photograph contains more independent information than Bézier curves can compactly encode. It can emit a photo as exact geometry but that costs one rectangle per pixel (a 320x240 photo becomes a 1.99 MB file of 42,933 shapes), so auto mode embeds the bitmap and reports the size ratio instead.
