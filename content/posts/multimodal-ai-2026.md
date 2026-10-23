---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-04-09 15:23:00+00:00
description: Compare multimodal systems by task, API input preprocessing and failure behavior, with documented input limits and a concrete invoice-extraction validation example.
draft: false
schema: schema-multimodal-ai-2026
tags:
- multimodal AI
- AI comparison
- document extraction
- video understanding
- Gemini API
- artificial intelligence
- machine learning
- multimodal models
title: 'Multimodal AI: Image, Audio and Video Evaluation for Real Applications'
lastmod: '2026-10-21T00:18:32+00:00'
---

A model that accepts images is not automatically the best document reader, and a model that accepts video does not necessarily inspect every frame at full resolution. Multimodal evaluation should begin with the application's evidence and error tolerance.

This guide replaces a broad model ranking with a concrete extraction workflow. It does not report independent accuracy scores or a universal hallucination rate. The API details below are quoted from vendor documentation checked on the date shown; none of them was measured here.

## Separate input capability from task performance

Google's [image-understanding documentation](https://ai.google.dev/gemini-api/docs/image-understanding) separates three documented ways to get an image into a request: a public URL, inline base64 data, or a Files API upload. The inline path caps total request size — text prompts, system instructions and inline bytes together — at 20 MB, and the page recommends the Files API for larger or reused files. So "the model accepts images" is rarely the binding constraint; the upload path you choose is part of the experiment.

The same documentation records that Gemini 3 introduced `media_resolution`, which sets the maximum number of tokens allocated per input image or video frame. Higher settings improve the model's ability to read fine text or identify small details, and increase token usage and latency. That trade-off is a parameter you set, not a property of the model name.

The [video-understanding documentation](https://ai.google.dev/gemini-api/docs/video-understanding) covers processing modes, temporal sampling and token accounting; those are the numbers that decide whether a video task is feasible at all.

Those details matter because resized images, sampled frames and audio representations can lose information needed by a task. A capability label such as "video input" does not establish frame-perfect event detection. Check the exact model and request settings.

Scope note: these statements describe the Gemini API request path. Consumer product surfaces apply their own upload and preprocessing behaviour, so a result you see in a chat app is not evidence about what the API does by default. Evaluate the endpoint you intend to use, not an entire provider brand.

Also separate understanding from generation. Reading text in a photograph and generating a new image are different operations.

## Video: the documented default is one frame per second

The video page states that video inputs use static processing by default — frames extracted at 1 FPS — across all models, including Gemini 4. An opt-in **agentic** mode is documented for Gemini 4 Argon, 3.8 Flash, 3.6 Flash and 3.5 Flash Lite, and later models, where the model explores the timeline, inspects transcripts first and adapts frame rates and resolution to the prompt.

| Mode | What it does | Availability |
|---|---|---|
| Static (default) | Frames at a fixed 1 FPS, placed in context in a single pass | All Gemini models, including Gemini 4 |
| Agentic (opt-in) | Model navigates the timeline and loads only what the prompt needs | Gemini 4 Argon, 3.8 Flash, 3.6 Flash, 3.5 Flash Lite and later |

Customisation is mode-specific: clipping intervals (`start_offset`, `end_offset`) and custom frame-rate sampling are documented as supported only in static mode.

The page also publishes static-mode token arithmetic that is worth copying into your own plan rather than guessing: a sampled frame costs 66 tokens when `media_resolution` is low and 258 tokens otherwise, audio adds 32 tokens per second, and metadata is added on top. Models with a 1M-token context window can process up to 3 hours of video at low media resolution, or up to 1 hour at high. For an agentic run, budget for navigation reasoning under `total_thought_tokens` as well as on-demand media retrieval under `total_tool_use_tokens`. The static per-frame calculation is not an agentic usage estimate.

The vendor states that agentic processing is up to 88% more token-efficient and roughly 7% higher quality on long-form content. Treat both numbers as vendor claims: the page does not publish the dataset, prompt set or scoring rubric behind them, and they should not be repeated as independent measurements or transferred to another provider.

What follows from a 1 FPS default is arithmetic, not a benchmark. An event shorter than the sampling interval has no guarantee of landing on a sampled frame, and the documentation publishes no accuracy guarantee for it. If your task depends on such an event, change the sampling configuration, record it as a new condition, and say so in the report.

## A concrete task: extract an invoice for human review

Define the required output before choosing a model: invoice identifier, invoice date, currency, total and source page. Keep the original document and a human-labeled answer set. Include clean scans, low-contrast scans, multiple currencies, missing fields and pages with unrelated totals.

Record which upload path you used. A long multi-page scan easily exceeds the 20 MB inline cap, so the Files API path becomes part of the condition rather than an implementation afterthought. If two runs differ in upload path or `media_resolution`, they are two conditions, not one comparison.

Ask the model to leave uncertain fields unresolved rather than inventing values. Keep source-page information so a reviewer can verify the answer. Do not let extracted text or instructions in the document trigger a payment or send data elsewhere.

Measure field-level exact match and meaningful errors separately. A misplaced decimal or wrong currency can matter much more than a punctuation difference in a supplier name. Track the number of records requiring human review and the time needed to correct them.

## Validate output without confusing validation with accuracy

The [offline validator](https://baeseokjae.github.io/research/content-quality-batch2-2026-10/evidence_checks.py) checks a small extracted-record format: required fields, a valid calendar date, supported example currencies, a nonnegative amount and a positive source-page number. The [execution record](https://baeseokjae.github.io/research/content-quality-batch2-2026-10/offline-results.json) includes a valid synthetic invoice and rejection cases for an impossible date, extra instruction field, negative amount and invalid page.

These checks catch malformed output. They do not prove that a valid-looking total matches the image. An extraction of `12.50` and one of `125.00` can both pass structural checks. A separate comparison against the document and business rules is still required.

The example's currency list and whole-won rule are deliberately narrow application assumptions. Adapt them to the actual contract rather than treating them as universal invoice rules.

## Build an evaluation matrix by modality

Use the [multimodal evaluation sheet](https://baeseokjae.github.io/research/content-quality-batch2-2026-10/multimodal-evaluation.csv). Its columns keep model, input preprocessing and human review minutes separate, and its result cells are intentionally empty: it is a protocol to fill in, not a set of collected measurements.

| Task | Representative failure | Evidence to retain |
|---|---|---|
| Document extraction | Wrong decimal, date or currency | Original page, expected fields and extracted fields |
| Audio transcription | Speaker overlap or proper-name error | Consent-cleared clip, reference transcript and timestamps |
| Video event detection | Short event missed between sampled frames | Sampling rate and clipping interval, time interval, expected event |
| Image question answering | Confident answer to an absent detail | Image, question and acceptable abstention |

Compare models with the same input preprocessing and output requirements. If you change resolution, upload path or video sampling, record that as a new condition. Include abstentions, timeouts and failed requests in the report.

## Cost, privacy and deployment

Account for modality-specific billing, preprocessing, storage, retries and human review. Text-token rates alone may not describe the cost of video or image processing, and an agentic video usage estimate must include both thought tokens and tool-use tokens rather than relying on the static per-frame calculation. Keep the provider's usage record with the application result.

Obtain appropriate permission for source material and avoid sending unnecessary personal data. Use independent review for consequential outputs. A low error rate on one benchmark cannot certify a healthcare, financial or legal workflow.

Start with one bounded task and expand only when its error handling is understood. The goal is an application whose mistakes can be found and corrected, not a table assigning "excellent" to every modality.

## Revision note

**Updated October 21, 2026.** Specified what the API documentation actually states about input paths, the 20 MB inline cap, `media_resolution`, the 1 FPS static default, the opt-in agentic mode and static-mode token accounting, and separated vendor headline figures from measurements. Removed model-version tags that the body no longer evaluates; the article makes no per-model ranking or price claim. Publication date and URL unchanged.

**Updated October 20, 2026.** Removed unsupported market forecasts, blanket model rankings, approximate hallucination rates and safety-critical recommendations. Added a concrete extraction protocol and honestly scoped executed validation checks.

## Primary sources

Checked October 21, 2026: [gemini image](https://ai.google.dev/gemini-api/docs/image-understanding); [gemini video](https://ai.google.dev/gemini-api/docs/video-understanding).

Checked October 21, 2026 (companion files, HTTP 200): [evaluation sheet](https://baeseokjae.github.io/research/content-quality-batch2-2026-10/multimodal-evaluation.csv); [execution record](https://baeseokjae.github.io/research/content-quality-batch2-2026-10/offline-results.json); [validator](https://baeseokjae.github.io/research/content-quality-batch2-2026-10/evidence_checks.py).
