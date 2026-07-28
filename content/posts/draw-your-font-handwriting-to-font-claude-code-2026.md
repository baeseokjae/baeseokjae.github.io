---
title: "Draw Your Font: Turn Handwriting into a Real Font with Claude Code"
date: 2026-07-28T04:06:09+00:00
tags:
  - Claude Code
  - font creation
  - handwriting to font
  - open source
  - AI tools
  - typography
  - draw-your-font
description: "Turn your handwriting into a real TTF font using draw-your-font and Claude Code — no design skills, no subscriptions, all local and free."
draft: false
cover:
  image: "/images/draw-your-font-handwriting-to-font-claude-code-2026.png"
  alt: "Draw Your Font: Turn Handwriting into a Real Font with Claude Code"
  relative: false
schema: "schema-draw-your-font-handwriting-to-font-claude-code-2026"
---

## What Is draw-your-font and Why Does It Matter?

draw-your-font is an open-source Node CLI tool that turns a photo of your handwriting into a working TTF, WOFF, or WOFF2 font using Claude Code's AI capabilities. Released in July 2026, it reached 410 GitHub stars in its first six days and is completely free — no subscriptions, no uploads, no design experience required. Unlike services like Calligraphr ($8/month) or Fontself ($49 + Adobe CC), draw-your-font runs entirely on your local machine, preserving your privacy while giving you a real, installable font in minutes.

## How It Works — The Tech Stack Behind the Magic

draw-your-font combines several technologies to transform a simple photo into a functional typeface. The core pipeline works like this:

1. **Claude Code (AI layer)** — Claude's vision capabilities identify and label each letter from your handwriting photo. It also judges output quality and accepts natural-language refinement commands like "make the descenders longer" or "the lowercase g looks wrong."

2. **potrace (vectorization engine)** — The same bitmap-to-vector tracing engine used by FontForge and Inkscape converts your scanned letter shapes into clean SVG outlines. This is the same proven technology that powers professional open-source typography tools.

3. **Node.js CLI (orchestration)** — A set of commands (`template`, `segment`, `build`, `make`, `preview`) guides you through the entire process from template generation to final font export.

4. **Metrics calibration** — The tool aligns all letters to a shared em-square, ensuring consistent baseline, x-height, and spacing. This is the step that makes the output feel like a real font rather than a collection of mismatched letter images.

The tool has zero system dependencies beyond Node.js 18 or later. A single `npm install` pulls in everything you need — no FontForge, ImageMagick, or potrace binary required.

## Step-by-Step: Create Your Font with Claude Code

### Install the Skill

Getting started takes less than a minute. Open your terminal and run:

```bash
npx skills add danilo-znamerovszkij/draw-your-font
```

This installs the draw-your-font skill into your Claude Code environment. If you prefer to work without Claude Code, you can also install the CLI directly via npm:

```bash
npm install -g draw-your-font
```

The tool works on macOS, Linux, and Windows as long as you have Node.js 18 or newer installed.

### Write Your Alphabet (or Use the Template)

draw-your-font generates a printable template PDF with boxes for each character. Run:

```bash
npx draw-your-font template
```

Print the template and fill each box with your handwriting. Use a dark pen on white paper for best results — gel pens (0.5–0.7mm) or fine-tipped markers work well. Include uppercase letters, lowercase letters, numbers, and common punctuation for a complete font.

### Take a Photo and Let Claude Work

Take a well-lit, flat photo of your filled template. Then run:

```bash
npx draw-your-font segment path/to/photo.jpg
```

Claude Code's vision capability identifies each letter in the photo, labels it with the correct character, and extracts individual letter images. The `segment` command handles the heavy lifting — it detects the grid structure, isolates each character, and prepares them for vectorization.

Next, build the font:

```bash
npx draw-your-font build
```

This runs potrace on each segmented letter, converts the bitmaps to SVG vectors, and assembles them into a properly metrics-calibrated font file. The output is a working TTF font you can install on your system.

### Iterate with Natural Language

One of the most powerful features of draw-your-font is the ability to refine your font using natural language. After building, run:

```bash
npx draw-your-font make
```

This opens an interactive Claude Code session where you can say things like:

- "Make the letters rounder and softer"
- "The lowercase g looks uneven — fix it"
- "Increase the weight slightly"
- "The spacing between letters is too tight"

Claude Code evaluates your font, identifies issues, and applies adjustments. It can re-segment specific letters, adjust vector paths, and rebuild the font — all without you touching a design tool.

### Export and Install Your Font

Once you're happy with the result, export your font:

```bash
npx draw-your-font build --formats ttf,woff,woff2 --smooth --weight medium
```

The `--smooth` flag applies anti-aliasing to vector paths, and `--weight` lets you choose from light, medium, or bold. You can export to TTF (system installation), WOFF (web use), and WOFF2 (compressed web use) simultaneously.

To preview your font before installing:

```bash
npx draw-your-font preview
```

This opens a browser-based preview showing your font rendering sample text at various sizes. On macOS, double-click the TTF file and click "Install Font." On Windows, right-click and select "Install." On Linux, copy the file to `~/.fonts/` and run `fc-cache -f`.

## CLI-Only Mode (No AI Needed)

If you don't want to use Claude Code, draw-your-font works entirely from the command line. The `segment` command includes a manual labeling mode where you specify which character each box contains. This is useful for:

- Users who prefer full manual control over the process
- Batch processing multiple handwriting samples
- Environments where AI APIs are unavailable
- Users who want to script font generation in CI/CD pipelines

The CLI-only mode still benefits from potrace vectorization and metrics calibration — you just handle the letter labeling yourself. The output quality is identical to the AI-assisted path.

## draw-your-font vs. Calligraphr vs. Fontself — Cost and Feature Comparison

| Feature | draw-your-font | Calligraphr | Fontself |
|---|---|---|---|
| **Price** | Free (open source, MIT) | $8/month | $49 one-time |
| **Additional costs** | None | None | Requires Adobe CC ($55+/month) |
| **Processing location** | Local machine | Cloud servers | Local (Adobe plugin) |
| **Privacy** | Full — no uploads | Handwriting uploaded | Local (but Adobe telemetry) |
| **Output formats** | TTF, WOFF, WOFF2 | TTF, OTF, WOFF | TTF, OTF, color fonts |
| **OpenType features** | Basic (v1) | Ligatures, randomization, alternates | Color fonts, variable fonts |
| **AI assistance** | Claude Code vision + refinement | None | None |
| **Design tool required** | No | No | Adobe Illustrator/Photoshop |
| **Platform** | macOS, Linux, Windows | Web browser | Adobe CC (macOS/Windows) |
| **Learning curve** | Low (CLI + natural language) | Low (web UI) | Medium (Adobe tools) |
| **License** | MIT (free, modifiable) | Proprietary | Proprietary |

draw-your-font wins on cost, privacy, and AI-assisted workflow. Calligraphr offers more advanced OpenType features like ligatures and randomization, while Fontself supports color and variable fonts — but both come with significant price tags and, in Fontself's case, ecosystem lock-in.

## Privacy and Local-First Design

One of the strongest arguments for draw-your-font is its privacy model. Your handwriting is a biometric identifier — it's as unique as your fingerprint or your signature. When you use a web-based service like Calligraphr, your handwriting sample is uploaded to their servers, processed, and stored. You have no control over what happens to that data after processing.

draw-your-font runs entirely on your local machine. The Claude Code session uses Anthropic's API for AI processing, but only the letter images are sent for vision analysis — and those are individual character crops, not your full handwriting sample. The vectorization, metrics calibration, and font assembly all happen locally.

For users who want zero data to leave their machine, the CLI-only mode eliminates all network calls. Your handwriting never touches the internet.

## Real-World Use Cases for Custom Handwriting Fonts

**Personal branding and signatures** — Create a font from your own handwriting for email signatures, personal websites, and digital correspondence. It adds a human touch that stock fonts cannot replicate.

**Wedding invitations and event materials** — Couples can create custom fonts from their own handwriting for save-the-dates, invitations, place cards, and thank-you notes. The consistent typeface keeps materials cohesive while preserving the personal feel.

**Children's handwriting keepsakes** — Turn a child's handwriting into a font before their writing style changes. Use it for birthday cards, storybooks, or family newsletters. It's a digital time capsule of their development.

**Indie game UI and assets** — Game developers can create unique fonts for their projects without hiring a type designer. A handwritten font adds personality to dialogue boxes, menus, and in-game signage.

**Classroom and educational materials** — Teachers can create fonts from their own handwriting for worksheets, handouts, and classroom materials. Students benefit from reading familiar letterforms.

**Accessibility and dyslexia-friendly fonts** — Create a font from your own handwriting that you find most readable. Some users with dyslexia report better reading comprehension with personalized letterforms.

## Tips for Best Results — Lighting, Paper, Pen Choice

The quality of your input photo directly determines the quality of your output font. Follow these guidelines:

**Pen selection** — Use a dark, consistent pen. Gel pens (0.5–0.7mm), fine-liner markers, or fountain pens with dark ink produce the cleanest results. Avoid ballpoint pens that leave uneven ink distribution. Stay away from light colors, glitter, or metallic inks.

**Paper quality** — Use smooth, bright white paper (at least 80 gsm). Avoid textured or colored paper that adds noise to the scan. The template PDF is designed for standard A4 or letter-size paper.

**Lighting** — Take your photo in bright, even lighting. Natural daylight from a window works well. Avoid direct sunlight that creates harsh shadows. If using artificial light, position two light sources at 45-degree angles to eliminate shadows from your hand.

**Photo capture** — Hold your camera parallel to the paper. Use a smartphone with at least 12MP resolution. Ensure the entire template is in frame with no cropping. Avoid wide-angle lenses that distort edges. A flatbed scanner produces the best results if you have one available.

**Consistent letterforms** — Write naturally but consistently. Keep the same letter size, slant, and spacing across all boxes. If you make a mistake, reprint the template rather than crossing out and rewriting.

## Limitations and What's Coming in v2

draw-your-font v1 is impressive but has limitations worth noting:

**No kerning pairs** — The current version does not generate kerning tables, so certain letter combinations (like "AV" or "To") may look unevenly spaced. Kerning is planned for v2.

**No ligatures** — Common typographic ligatures like "fi", "fl", and "ff" are not supported. The tool treats each character independently.

**No randomization** — Professional handwriting fonts often include multiple versions of each letter to simulate natural variation. draw-your-font uses a single glyph per character.

**Basic OpenType features** — Advanced OpenType features like contextual alternates, stylistic sets, and swashes are not yet implemented.

**Manual grid alignment** — The template uses a fixed grid. If your handwriting naturally slants or varies in size, some letters may be cropped incorrectly during segmentation.

The project's GitHub issues and roadmap indicate that kerning, ligature support, and multi-glyph variants are the top priorities for v2. The open-source nature means the community can contribute these features — and with 410 stars in week one, the community is growing fast.

## Conclusion — Why This Changes the Font Game

draw-your-font democratizes font creation. Before this tool, creating a custom handwriting font meant either paying a subscription ($8/month for Calligraphr), buying expensive software ($49 + Adobe CC for Fontself), or learning complex typography tools. The barrier was high enough that most people never bothered.

Now, anyone with a pen, a phone, and a terminal can create a real, installable font in under 30 minutes — for free. The combination of Claude Code's AI capabilities with open-source vectorization creates a workflow that is both powerful and accessible. You don't need to be a designer, a typographer, or a developer. You just need to write.

The privacy-first, local-only design means your handwriting — your unique biometric signature — never leaves your control. In an era where every creative tool wants your data in the cloud, draw-your-font takes a refreshingly different approach.

With 410 GitHub stars in its first week and an active development roadmap, draw-your-font is not just a novelty. It's the beginning of a new category: AI-assisted, privacy-respecting, open-source font creation. Try it today and see your handwriting become a real font.

## FAQ

**Q: Do I need Claude Code subscription to use draw-your-font?**
A: No. Claude Code is used for the AI-assisted workflow (automatic letter labeling and natural-language refinement), but draw-your-font also works in CLI-only mode where you label letters manually. The font building, vectorization, and export work without any AI API calls.

**Q: Can I use draw-your-font on Windows?**
A: Yes. draw-your-font works on macOS, Linux, and Windows as long as you have Node.js 18 or newer installed. The CLI commands are identical across all platforms.

**Q: What file formats does draw-your-font support?**
A: The tool exports to TTF (TrueType Font), WOFF (Web Open Font Format), and WOFF2 (compressed WOFF). You can export all three simultaneously using the `--formats ttf,woff,woff2` flag. CSS @font-face declarations are also generated for web use.

**Q: How is draw-your-font different from Calligraphr?**
A: draw-your-font is free, open-source, and runs entirely on your local machine. Calligraphr costs $8/month and processes your handwriting on their servers. draw-your-font uses Claude Code for AI-assisted letter labeling and refinement, while Calligraphr offers more advanced OpenType features like ligatures and randomization.

**Q: Can I edit my font after creating it?**
A: Yes. draw-your-font generates SVG vector files for each character during the build process. You can edit these SVGs in any vector editing tool (Inkscape, Illustrator, etc.) and rebuild the font. The `make` command also lets you refine the font using natural language through Claude Code.
