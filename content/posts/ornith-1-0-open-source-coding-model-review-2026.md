---
title: 'Ornith-1.0 Coding Model Review: Benchmark Evidence and Hardware Planning'
date: 2026-06-25
keyword: Ornith-1.0 DeepReinforce open source coding model 2026
type: review
draft: false
schema: schema-ornith-1-0-open-source-coding-model-review-2026
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
description: Read Ornith-1.0 model-card results with their harness conditions, calculate weight-memory lower bounds, and plan a reproducible evaluation.
lastmod: '2026-10-20T07:02:10.628622+00:00'
---

Ornith-1.0 is worth evaluating as a coding-model family, but its largest model's leaderboard result does not tell you what will run on your laptop. This review separates supplier-reported results from a hardware sizing calculation and a practical evaluation plan. No Ornith inference run or independent reproduction of its coding benchmarks is reported here.

## What the published scores actually describe

The [397B model card](https://huggingface.co/ornith-ai/Ornith-1.0-397B/raw/main/README.md) reports Terminal-Bench 2.1 at **77.5 with Terminus-2**, versus **78.2 with a Claude Code harness**, and SWE-bench Verified at **82.4**. Those are supplier results for a particular artifact and evaluation setup, not measurements made by RockB.

The card describes different harness settings across evaluations. A score should therefore travel with the model revision, benchmark version, harness, context limit, sampling configuration, resource allowance, and aggregation method. Copying one number into a comparison table strips away the conditions needed to interpret it.

The [9B card](https://huggingface.co/ornith-ai/Ornith-1.0-9B/raw/main/README.md) and [35B card](https://huggingface.co/ornith-ai/Ornith-1.0-35B/raw/main/README.md) describe separate model variants. Do not assign the largest variant's results to either of them. The large-model card labels its license MIT, but a README label alone is not a complete redistribution review; inspect the license files and upstream model conditions for the exact artifact you plan to distribute.

## A useful first filter: weight memory

Before downloading weights, calculate a lower bound. For a nominal parameter count expressed in billions:

`weight GB = parameters in billions × bits per parameter / 8`

| Nominal total parameters | BF16, 16 bits | Idealized 4-bit weights |
|---|---:|---:|
| 9B | 18 GB | 4.5 GB |
| 35B | 70 GB | 17.5 GB |
| 397B | 794 GB | 198.5 GB |

These are decimal gigabytes for parameter storage only. They exclude quantization metadata, KV cache, activations, runtime buffers, and any duplicated tensors. A mixture-of-experts model's active parameter count describes work per token; it does not mean only that fraction of the complete weight set needs storage. Offloading changes where weights reside and can change throughput.

The calculations are included in the [reproducible offline results](/research/content-quality-2026-10/offline-results.json). They are a quick rejection test for an impossible memory budget, not a promise that a configuration fits. For example, a device with less memory than the weight-only bound already needs offloading or another representation; being above the bound still requires a real load test.

## An evaluation you can actually compare

Build a small task set from the work you expect to do: a failing unit test, a constrained refactor, a dependency migration, and a task that requires finding an existing project convention. Freeze the repository revision and acceptance commands before running any model.

Record the following for every attempt:

| Field | Why it changes the decision |
|---|---|
| Model repository and revision | Makes the downloaded artifact identifiable |
| Quantization and execution engine | Changes memory and potentially output quality |
| Prompt, context files, and tool permissions | Prevents comparing different information or capabilities |
| Wall time, peak memory, and retries | Reveals whether a working solution fits your operating budget |
| Test result and reviewer changes | Distinguishes a plausible patch from an accepted patch |
| Failure transcript | Shows whether the problem was reasoning, tooling, context, or infrastructure |

Keep failed attempts in the denominator. Run a baseline with your current workflow. If the new model only wins after receiving additional context or retries, report that as a different configuration. Avoid a broad “better than” conclusion from a single successful task.

## Who should try it first

Start with a variant your existing hardware can accommodate and a task whose success you can check automatically. A team already operating large-model infrastructure can evaluate the larger artifact, but should still test workload fit before allocating a production budget.

For an individual developer, the next useful step is a local acceptance run, not extrapolating from the largest model's ranking. The [local-model selection guide](/posts/best-local-llm-models-2026/) covers the broader choice of runtime, context size, and model fit.

## Revision note

**Updated October 20, 2026.** Replaced the short promotional overview with attributed model-card evidence, explicit variant and harness distinctions, and a reproducible memory calculation. Removed the unsupported blanket superiority and security claims. The former hands-on cover did not describe the work performed and has been replaced.

## Primary sources

Checked October 20, 2026: [ornith 397b](https://huggingface.co/ornith-ai/Ornith-1.0-397B/raw/main/README.md); [ornith 9b](https://huggingface.co/ornith-ai/Ornith-1.0-9B/raw/main/README.md); [ornith 35b](https://huggingface.co/ornith-ai/Ornith-1.0-35B/raw/main/README.md).
