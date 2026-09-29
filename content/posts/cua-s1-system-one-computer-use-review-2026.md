---
title: "CUA-S1 Review 2026: What trycua's System One Computer Use Model Actually Scores"
date: 2026-09-29T13:07:50+00:00
tags:
  - cua s1
  - cua-s1 system one
  - system one computer use
  - system one model
  - cua s1 review
  - cua-s1-forms
  - cua-s1-4b-0.2
  - cua-s1-4b-0.1
  - cua-s1-nano-0.1
  - trycua cua system one
  - specialist computer use model
  - small computer use model
  - option attention model
  - jev alternative open source
  - open source jev clone
  - System 1 vs System 2 AI agents
  - closed-set action selection agent
  - GUI form filling model
  - computer use benchmark cua-bench-s1
  - Qwen3.5-4B LoRA computer use
  - confidence calibration abstention agent
  - cua driver desktop automation
  - fast cheap computer use decisions
  - how to run cua-s1 locally
description: "CUA-S1 review: four checkpoints, closed-set option scoring, 0.929 multimodal held-out accuracy, and the 29.3% high-confidence skip failure worth knowing."
draft: false
cover:
  image: "/images/cua-s1-system-one-computer-use-review-2026.png"
  alt: "CUA-S1 Review 2026: What trycua's System One Computer Use Model Actually Scores"
  relative: false
schema: "schema-cua-s1-system-one-computer-use-review-2026"
---

CUA-S1 is not a computer-use agent. It is trycua's family of small "System One" models that score a closed set of (element, action) options in a single forward pass, returning a probability per option instead of generating action text. Planning, ordering, and execution stay in your application code.

That distinction is the whole review. Everything CUA-S1 does well, and everything it fails at, follows from the decision interface it chose.

## What CUA-S1 actually is — and what it refuses to be?

The name invites a Kahneman reading, and Cua itself pushes back on it. In their own wording, "System 1" is an engineering analogy for fast, bounded decisions: which value goes in a field, whether to leave an element alone. It is explicitly not a strict model-architecture classification, and not a replacement for a general-purpose agent's planning and reasoning. Treat it as a design intent, not a spec, and the label survives scrutiny; treat it as an architecture claim and it collapses immediately.

What CUA-S1 actually replaces is one narrow thing: the per-step LLM call that asks "which element, and which action?" In a conventional computer-use stack, that question is answered by generating tokens — a string like `click(element_14)` — which is slow, expensive, and can hallucinate a selector that does not exist. CUA-S1 replaces the generation with a classification.

The decoding contract is the core of the design:

- The caller enumerates a closed set of options (one per candidate element, plus fixed decisions such as check, click, and skip).
- For the 4B checkpoints, a chat-template prompt asks for a single letter identifying the chosen option.
- Each option letter is a verified single tokenizer token.
- One forward pass runs, and the final-position logits at the option-letter positions are softmaxed into per-option probabilities.

This is why the model "can't hallucinate" in the string sense — it cannot emit an action nobody enumerated. It is also the hard limit: it cannot propose an action nobody enumerated, and it cannot be evidence that the option set handed to it was safe or complete. If your enumerator is wrong, CUA-S1 will confidently choose among the wrong options.

Cua positions CUA-S1 beside Cua Driver (cross-OS desktop automation), Cua Fleets (isolated cloud desktops), Lume (local macOS/Linux VMs on Apple Silicon), and Cua Bench (task authoring and evaluation). The agent is your code plus Cua Driver. CUA-S1 is the decision layer inside it.

## Which checkpoints exist in the CUA-S1 family, and how do they compare?

Four checkpoints are published as of this review, and they are genuinely different products with different evidence behind them. Reading the launch narrative alone will mislead you: the launch story is about the tiny MIT forms demo, but the benchmark story is about the 4B LoRA adapters.

| Checkpoint | Parameters / size | Backbone | Licence | What it is |
|---|---|---|---|---|
| cua-s1-forms (cua-s1-form-v0) | 706,048 params / 2.8 MB | Tiny byte-level transformer (2-layer encoder, width 128, 4 heads) + option-attention head | MIT | Demo-grade form-filling scorer |
| cua-s1-nano-0.1 | 855,296 params per modality / 6.9 MB | From-scratch, text + multimodal contexts (SmolVLM-256M or SigLIP) | Apache-2.0 | Tiny baseline |
| cua-s1-4b-0.1 | 272 MB adapter | LoRA rank 16 on frozen Qwen/Qwen3.5-4B | Apache-2.0 (adapters only) | First 4B generation |
| cua-s1-4b-0.2 | 187 MB adapter | LoRA rank 16 on frozen Qwen/Qwen3.5-4B | Apache-2.0 (adapters only) | Current flagship |

Two details matter here. First, cua-s1-4b-0.2 does not replace cua-s1-4b-0.1 — both remain published, and they behave very differently. Second, the licence nuance: MIT covers the repository source, and the forms checkpoint is MIT, but nano and the 4B adapters are Apache-2.0 covering the adapters only. Qwen/Qwen3.5-4B keeps its own licence and is not redistributed by Cua.

The 0.2 flagship ships as two separately trained LoRA adapters on the same frozen base: one text (accessibility tree), one multimodal (screenshot). It was trained with a supervised stage plus an RL stage (RLOO) against live GUI environments. The base model itself is 9.34 GB of 16-bit weights in two safetensors shards, so inference needs more than 9.3 GB of memory before activations.

## How does Cua's benchmark evidence compare to what vendors usually publish?

This is the strongest part of the release, and it deserves to be said plainly: Cua publishes better evaluation data than most vendors in this category.

The `libs/cua-bench-s1` README carries raw and chance-corrected tables for jev, djev, semif, cua-s1-nano-0.1, cua-s1-4b-0.1, and cua-s1-4b-0.2, with a measured per-row `p_chance` and ECE (expected calibration error) reported. It publishes per-run dataset hashes and `eval_results` directories. It flags one of its own rows — pagination — as a family-taxonomy labeling artifact rather than a capability result. And it states the caveat that hardware and batch size are not standardized across runs: jev is a hosted API round-trip, djev and semif ran on GPU, nano is CPU-fast.

Almost no vendor does this. It also means the numbers cannot be read naively, because a lot of rows land at or below chance.

The headline results, all from Cua's own tables:

| Evaluation | cua-s1-4b-0.2 | Comparison |
|---|---|---|
| Multimodal hard cross-dataset, frozen 168-task GUI-360 split, ax_tree stripped | 0.929 overall, ECE 0.069 | djev 0.601 (ECE 0.360); semif 0.244 |
| Text hard cross-dataset, frozen 615-task GUI-360 split | 0.833–1.000 across five families | 0.429 on pagination; cua-s1-4b-0.1 ranges 0.167–0.571; nano 0.000 throughout |
| Live agentic rollouts (cua-bench-basic, held-out variants 2–4, N=18, 20-step cap) | text 0.944, multimodal 0.722 | djev 0.889 / 0.667; cua-s1-4b-0.1 text 0.000 / multimodal 0.333 |
| External general_decision (jevbench), text zero-shot, out-of-domain | 0.887 raw, 0.775 chance-corrected | jev 0.667; cua-s1-4b-0.1 0.632; djev 0.623; semif 0.563 |

Now the other side of the same tables. chess, evaluated on a real Stockfish-backed 800-position dataset with a fair N=15 subset, and game_control, evaluated on a live 82-task ViZDoom setup, show no measurable signal for any model once chance-corrected. cua-s1-4b-0.2's calibrated game_control task accuracy is 0.000 with element accuracy 0.138. On the external OSWorld next-action multimodal out-of-domain evaluation, every model scores at or below 0.083 task accuracy; the best element accuracy is semif at 0.531.

That is the honest envelope: the 4B adapters are strong on the six GUI families they target, and indistinguishable from chance outside them.

## Why is the 29.3% out-of-catalogue result the most instructive number in the release?

Because it shows what these models do when they are out of their depth — and the answer is not abstention.

The tiny forms model, cua-s1-form-v0, scores 97.5% (2,993/3,070) in-distribution on synthetic decisions. On held-out forms drawn from outside its catalogue — 41 decisions over five forms covering logistics, hardware, DevOps, veterinary, and a Chinese-language form — accuracy falls to 29.3% (12/41).

Then the detail that matters: 36 of those 41 predictions were "skip", at a mean confidence of 0.974.

The model does not say "I don't know." It says "there is nothing to do here," almost maximally confidently, and it is wrong. An executor that reads "skip" as "this form needs no action" will silently no-op an entire out-of-scope form without raising a single warning. This is the cleanest available demonstration that confidence scores from a specialist decision model are not a safety signal.

Cua's follow-up experiment nails the mechanism. Re-labeling the same held-out forms with in-catalogue wording restored accuracy to 11/11. Replacing only the element labels with unseen wording dropped accuracy to 25%. In other words, the model keys on label vocabulary, not on semantics — it is matching wording it has seen, not understanding what the field means.

That is a general lesson about the whole System One category, not just CUA-S1: closed-set scoring models inherit the distribution of their label vocabulary, and their abstention behaviour under distribution shift is a property you must measure yourself, not assume.

## What does the cua-s1-4b-0.1 collapse tell you about the training pipeline?

It tells you that SFT can remove agentic capability the model already had.

In live agentic rollouts with a 20-step cap over 18 held-out tasks, cua-s1-4b-0.1's text adapter succeeded 0.000 of the time. Cua documents the cause directly: the adapter returned "skip" on 340 of 360 steps. Its SFT stage removed agentic capability that the zero-shot base model already possessed — the zero-shot multimodal path scored 0.333.

A second adapter generation (0.2) was needed to recover the behaviour, via a supervised stage plus RL against live GUI environments. And 0.1 remains published.

Read this as an operational warning rather than a curiosity. A per-step scorer that has silently learned to prefer one action will produce runs that look like they are working — the stack executes, errors are not raised, and the episode simply never completes. If you are evaluating any checkpoint in this family, measure episode success with your own environment reward, not per-step agreement.

## How fast is CUA-S1 in practice, and what hardware do you actually need?

The cost shape is inverted from the pitch, and this is the part most reviews get wrong.

Latency was measured on one Apple M1 Ultra host (128 GB) and a GitHub `ubuntu-latest` runner. It does not generalize to "fast on any laptop."

| Scenario | Measured latency |
|---|---|
| cua-s1-4b-0.2 text, M1 Ultra / mps / float16 | 16.3 s load; 1.07 s for the 3-candidate fixture; 2.83 s for a 12-region, 8-candidate request (medians of 5 warm calls) |
| Same adapter, CPU / float32 | 18.3 s load; 19.5 s for 3 candidates; 32.1 s for 12-region/8-candidate |
| Mean per-task inference, 6 core families, text hard cross-dataset | cua-s1-4b-0.2 0.141 s; cua-s1-4b-0.1 0.121–0.128 s; nano 0.003 s; djev 0.809 s; hosted jev 0.556 s |
| cua-s1-nano-0.1 on the same families | 0.003 s mean per task — but 0.000 accuracy |

Two things fall out of that table. The 4B adapters are meaningfully faster than the hosted Jev API round-trip on the same task (0.141 s vs 0.556 s mean per task), which is a real win and the clearest argument for local deployment. And the tiny nano model is 47x faster than the 4B while scoring zero on the same families — so in this family you get cheap or correct, not both.

Memory is the harder constraint. The Qwen3.5-4B base is 9.34 GB of 16-bit weights, and Cua states an 8 GB host cannot run it at all; plan on 16 GB free. Peak memory has not been measured, which is a gap worth noting if you are sizing a fleet. Load time alone (16.3 s on M1 Ultra, 18.3 s on CPU) means you do not want to spin this up per decision.

## How does CUA-S1 compare to TypeSafe Jev and the broader System One field?

Jev, from TypeSafe AI, defined the category CUA-S1 belongs to. Its September 15, 2026 post introduced "System One Models" as fast, structured decisions software can consume directly rather than string generation, pitched Jev as "structured outputs and can't hallucinate," and introduced RLCD (Reinforcement Learning for Calibrated Decisions) as the training method framed against RLHF and RLVR.

Jev is a hosted, early-access API — the proprietary baseline every open clone is measured against, including in Cua's own tables. It is not open source, which is precisely what invited the wave.

The comparison that matters for buyers is not CUA-S1 vs Jev in the abstract. It is:

- **Forms-shaped work.** The forms checkpoint reports 99.7% vs 83.6% for hosted Jev (jev-latest, no fine-tuning) on the same task — but these are author-reported numbers, not reproduced in `libs/cua-s1`. Hosted Jev still scored 96% on judgement decisions and 74% on recognizing an already-filled field as a no-op, which is the harder half of form filling. Attach that caveat every time you quote the headline.
- **GUI-family decisions at scale.** Here the 4B adapters have reproducible, chance-corrected, ECE-reported evidence on their side, and they beat every open baseline on multimodal hard cross-dataset (0.929 vs djev 0.601, semif 0.244).
- **Everything else.** chess, game_control, and OSWorld next-action say wait.

The field around this is moving fast and crowded. Latent.Space's AINews documented six named open reimplementations within two days of Jev: Laya (421M, ModernBERT-large encoder plus two transformer layers, PPO over sequence embeddings), DiffusionGemmaJev, Bespoke Nimble (LoRA on Qwen3.5-9B), SemIf/OpenJev (4B and 35B Qwen3.5 backbone with a tiny three-class NLI head), Jevlike (40K byte-embedding option-attention model — the lineage of CUA-S1's forms head), and Kev-0.5B. The `awesome-jev` catalog counted 944 verified projects across 11 categories within about ten days, including 72 in a "Jev-like models" section and 75 in "Browser & computer use."

Adoption data supports the urgency: Vercel reported Jev reaching roughly 13% of teams on day one, 2x the GPT-5.6 family and 6x Fable 5.1 on AI Gateway. And the data provenance caveat is universally acknowledged — the training data behind this entire wave is 100% synthetic.

Choosing CUA-S1 in 2026 means choosing a fast-moving research line with a real vendor behind it, not a settled product.

## What is the artefact-integrity and licence story?

Better than average, and specific enough to verify.

Cua ships safetensors plus JSON only. Older revisions of the forms checkpoint shipped a pickle `.pt` checkpoint; it was removed, and `cua_s1` now refuses pickle checkpoints by design (trycua/cua#3977). A SHA-256 tensor signature is validated before load. Pinned revisions are documented for reproduction:

```text
Qwen/Qwen3.5-4B        851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a
cua-s1-4b-0.2          16818868b0cc7813808aae4e87b417657046ab79
cua-s1-4b-0.1          3ebffb9868f31a1d54140948cb2434d35f35b281
cua-s1-nano-0.1        abbd98492307dc20373f79f7141725412df63c42
cua-s1-forms           4a7a9f42a3d42e6dfbd111c0c843e37ac50f1332
```

The repository is source-only — no weights, datasets, demo binaries, or recordings. Weights live separately on Hugging Face. `trycua/cua` is MIT, with 27,087 stars, 1,889 forks, and 1,042 open issues as of September 29, 2026, created January 31, 2025. The Show HN thread on September 19 drew 95 points and 10 comments, including author replies on the specialist-cascade idea.

One gap worth flagging: there is no weights-backed CI and no Cua Driver end-to-end validation for the forms checkpoint. That is Cua's own disclosure.

## Is CUA-S1 safe to run unsupervised?

No — and Cua says so more clearly than most vendors do.

The SECURITY.md guidance is unusually direct for a launch: treat screen content, documents, and model-generated actions as untrusted; isolate the runtime; apply least privilege; require human confirmation for consequential, irreversible, privileged, or external actions. It states that a specialist checkpoint "is not a security boundary" and that its outputs "must not be used as authorization."

Human confirmation for consequential actions is stated policy, not optional. Read together with the 29.3% high-confidence-skip result, the implication is concrete: a CUA-S1 deployment needs an external check that the option set was complete and that a "skip" was justified. The model will not tell you when it is out of scope — it will tell you there is nothing to do.

Cua's README carries the same tone: none of the checkpoints "should be treated as a general-purpose assistant or as evidence of reliable performance outside its evaluated task and environment boundaries."

## Verdict: who should use CUA-S1 today, and who should wait?

**Use it if** you are replacing a per-step LLM decision call inside a GUI agent you already control, your task families are close to the six Cua evaluated, you can enumerate options yourself, and you have 16 GB free per inference host. The multimodal hard cross-dataset result (0.929, ECE 0.069) and the live agentic numbers (0.944 text / 0.722 multimodal) are real, chance-corrected, and better-documented than anything else in the open field.

**Wait if** your work looks like chess, game control, or open-ended OS navigation — every model in the family is at or below chance there after correction, and OSWorld next-action tops out at 0.083 task accuracy. Wait also if you cannot enumerate options yourself, or cannot add an independent completeness check on the option set.

**The defensible verdict is positive with explicit boundaries.** Cua publishes the most honest evaluation data in the System One field — raw and chance-corrected tables, measured `p_chance`, ECE, dataset hashes, and self-flagged labeling artifacts. The 4B adapters are genuinely strong inside their envelope. Everything outside that envelope is either at chance or actively risky to trust, and the failure mode is a high-confidence "skip," not an error.

Judge CUA-S1 as a fast, calibrated classifier for a pre-enumerated decision set. Judge the agent as your code.

## FAQ

**Does CUA-S1 replace a general-purpose computer-use agent?**
No. CUA-S1 is a per-step decision scorer that chooses among options you enumerate. Planning, option enumeration, action ordering, and execution stay in the surrounding application code, optionally with Cua Driver. Cua states its checkpoints should not be treated as a general-purpose assistant.

**What does "System One" mean in CUA-S1?**
It is Cua's engineering analogy for fast, bounded decisions — which value goes in a field, whether to leave an element alone. Cua explicitly says it is not a strict model-architecture classification and not a replacement for an agent's planning and reasoning.

**How much memory and time does cua-s1-4b-0.2 need per decision?**
The Qwen3.5-4B base is 9.34 GB of 16-bit weights, so plan on at least 16 GB free; an 8 GB host cannot run it. On an M1 Ultra with mps and float16, load took 16.3 s and decisions took 1.07 s for a 3-candidate fixture and 2.83 s for a 12-region, 8-candidate request. Mean per-task latency on the six core families was 0.141 s.

**Why does the out-of-catalogue result matter so much?**
Because the tiny forms model scored 29.3% (12/41) on held-out out-of-catalogue forms while emitting "skip" on 36 of 41 predictions at mean confidence 0.974. It fails silently with high confidence, so an executor that treats "skip" as "nothing to do" will no-op an entire out-of-scope form. Re-labeling the same forms with in-catalogue wording restored accuracy to 11/11, showing the model keys on label vocabulary rather than semantics.

**Can I use CUA-S1 commercially?**
It depends on the checkpoint. The `trycua/cua` source and the cua-s1-forms checkpoint are MIT. cua-s1-nano-0.1 and the 4B LoRA adapters are Apache-2.0, but that covers the adapters only — Qwen/Qwen3.5-4B keeps its own licence and is not redistributed by Cua, so the base model's terms apply to your deployment as well.
