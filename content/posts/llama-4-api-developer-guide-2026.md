---
cover:
  alt: 'Llama 4 API Developer Guide: Scout, Maverick, Provider Contracts and Memory Limits'
  image: /images/llama-4-api-developer-guide-2026.png
  relative: false
date: 2026-05-02 21:07:51+00:00
description: Distinguish Llama 4 model-card specifications from hosted API limits, estimate weight storage, and validate a provider integration before migration.
draft: false
schema: schema-llama-4-api-developer-guide-2026
tags:
- llama-4
- llm-api
- open-source-llm
- moe-architecture
- ai-development
title: 'Llama 4 API Developer Guide: Scout, Maverick, Provider Contracts and Memory Limits'
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

Llama 4 is a model family, not a promise that every hosting provider offers the same endpoint, context limit or price. A developer needs two records: which model artifact is intended and what the chosen service actually supports.

This guide uses Meta's model card and license, then provides a provider-contract checklist. It does not claim a live inference test or a GPU fit measurement.

## Scout and Maverick are different artifacts

Meta's [Llama 4 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md) records the release date as **April 5, 2025** and describes:

| Model | Active parameters | Total parameters | Model-card context |
|---|---:|---:|---:|
| Scout | 17B | 109B | 10M tokens |
| Maverick | 17B | 400B | 1M tokens |

These are model-card attributes. A hosted endpoint can expose a smaller limit or a specific quantized version. The card describes image and text input with text output; do not infer audio/video support or image generation merely from the word multimodal.

An active parameter count describes computation for a token. It does not mean the complete model occupies only that many parameters in storage.

## Memory arithmetic is a lower bound

For parameter storage alone:

`GB = total parameters in billions × bits per parameter / 8`

| Model | Idealized 4-bit storage | 16-bit storage |
|---|---:|---:|
| Scout, 109B total | 54.5 GB | 218 GB |
| Maverick, 400B total | 200 GB | 800 GB |

These decimal-GB figures exclude quantization scales, KV cache, activations, runtime buffers and duplicated tensors. They are not measured VRAM requirements. Offloading changes where data resides and can change performance; long context can add substantial memory demand.

Use the exact weight artifact and serving engine to perform a real load test. A marketing statement about a particular quantized configuration cannot be generalized to all context lengths and concurrency levels.

## Write down the hosted API contract

The [model migration worksheet](/research/content-quality-batch2-2026-10/model-migration.csv) can be used for Llama providers as well. Record:

- Provider endpoint and exact model identifier.
- Model revision or quantization when disclosed.
- Maximum input and output for the account/deployment.
- Supported request fields, image handling and tool-call format.
- Streaming termination and error behavior.
- Rate limits, retention settings and applicable prices.

Do not copy a model ID from one provider into another without checking its catalog. Even an OpenAI-compatible interface can support a different parameter subset. Start with a minimal text request, then add the features your application actually uses.

Keep provider credentials in the intended secret store. Do not embed them in client-side code, a public notebook or a repository example.

## Integration tests before a switch

Run the same small request set against the existing and proposed deployment. Include a valid image, malformed input, a response near your output limit and a tool call if the application needs one. Record both normal responses and errors.

For long documents, check retrieval or extraction accuracy at realistic sizes. Fitting input into an advertised window does not demonstrate that the answer uses every part correctly. Include a question whose answer is absent so the model's behavior on missing evidence is visible.

Measure accepted output, latency, retries and billed cost. Keep serving configuration attached to the result. If a quantized deployment fails a task another version passes, report the actual variants rather than attributing everything to the Llama 4 family.

## License and adoption decision

The weights are governed by the [Llama 4 Community License](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/LICENSE), including its incorporated use conditions and additional commercial provisions. Do not describe that as an unrestricted Apache or MIT license. Read the terms for your intended distribution and deployment.

Choose a hosted service when it meets the contract and operational requirements you can verify. Choose self-hosting when you can own the hardware, runtime, updates and data controls. Neither decision follows from active parameter count alone.

## Revision note

**Updated October 20, 2026.** Replaced unsupported universal API/pricing assumptions with exact model-card distinctions, transparent memory lower bounds, provider-contract checks and the actual model license.

## Primary sources

Checked October 20, 2026: [llama4 card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md); [llama4 license](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/LICENSE).
