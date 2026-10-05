---
title: 'Qwen3.8 27B Benchmark: Artificial Analysis Says 52 Then, 34 Now'
date: 2026-10-01T04:48:06+00:00
tags:
- qwen 3.8
- artificial analysis
- llm benchmarks
- local llm deployment
- gguf quantization
description: Qwen3.8 27B scored 52 on Artificial Analysis in August 2026 and scores 34 today. Same model, re-versioned index — here is what it really measures.
draft: false
cover:
  image: "/images/qwen3-8-27b-artificial-analysis-52.png"
  alt: "Qwen3.8 27B Benchmark: Artificial Analysis Says 52 Then, 34 Now"
  relative: false
schema: "schema-qwen3-8-27b-artificial-analysis-52"
---

Qwen3.8 27B really did score 52 on the Artificial Analysis Intelligence Index — that was the correct figure on 2026-08-18, under index version v4.1.1, and it topped that board at #1 of 135. It also scores 34 today under v4.3.2. The model never changed; the index did.

That two-sentence answer is worth more than the number itself, because almost every article ranking for this keyword still prints "52" from an August snapshot and has never re-checked the live page. This post walks through what the Qwen3.8 27B benchmark actually says on 2026-10-01, why the total moved, and — more usefully — why the *shape* of the profile never moved at all.

## What is Qwen3.8 27B's Artificial Analysis score: 52 or 34?

Both. They are the same model measured by two different versions of the same index, and the distinction matters more than the digits.

- **52** — captured in the Wayback snapshot dated 20260818235916, which reads "Qwen3.8 27B scores 52 on the Artificial Analysis Intelligence Index," with the rank card showing "# 1 / 135" and a median of 9 for the comparable cohort. Index version: v4.1.1.
- **34** — the live page on 2026-10-01: "Qwen3.8 27B (Xhigh) scores 34 on the Artificial Analysis Intelligence Index, placing it well above average among comparable models (median: 8)." Rank card: "# 1 / 142," 4 of 4 units for Intelligence. Index version: v4.3.2.

| | August 18, 2026 snapshot | October 1, 2026 live page |
|---|---|---|
| Intelligence Index score | 52 | 34 |
| Index version | v4.1.1 | v4.3.2 |
| Evaluations counted | 9 | 10 |
| Rank (Intelligence) | # 1 / 135 | # 1 / 142 |
| Verbosity rank | # 23 / 135 (160M output tokens) | # 22 / 142 (200M output tokens) |
| Speed | N/A (no hosted endpoint yet) | 45.1 tok/s, # 54 / 142 |
| Hosted price | $0.00 in / $0.00 out | $0.50 in / $3.00 out per 1M tokens |

The one thing that did not change is the rank. It is still first. Treat 52 and 34 as different rulers, not as a decline.

## Why did the Artificial Analysis score drop from 52 to 34?

Because Artificial Analysis re-versioned the index twice between the snapshot and today, and this particular model was more exposed to those changes than most.

| Index version | What changed | Effect on this model |
|---|---|---|
| v4.1.1 (August, the "52") | 9 evaluations, including GPQA Diamond and tau3-Banking | Baseline for every August article |
| v4.2 | GPQA Diamond removed | Removes a knowledge-heavy row |
| v4.3 | tau3-Banking replaced by AutomationBench-AA; Terminal-Bench 2.1 upgraded to 4.0 | Swaps an agentic row and hardens another |
| v4.3.2 (current) | 10 evaluations: AA-Briefcase v1.1, GDPval-AA v2.1, AutomationBench-AA, Terminal-Bench 4.0, SciCode, HLE, GDP.pdf, CritPt, AA-Omniscience, AA-LCR v1.1 | Today's 34 |

An index is a composite. Change the constituent benchmarks and every score moves, even for a model whose weights are byte-identical to the August release. Artificial Analysis says so directly in its methodology: "Artificial Analysis Intelligence Index v4.3 replaces tau3-Banking with AutomationBench-AA, and upgrades Terminal-Bench to 4.0."

If you are citing this model in a deck, cite the version string next to the number. A bare "52" is a claim about an index that no longer exists.

### Does the index swap favour or punish this model?

For Qwen3.8 27B it is closer to neutral-to-punishing on the total, but flattering on the rows. Look at the current per-benchmark detail against GLM-5.2, taken from the live comparison page on 2026-10-01:

| Benchmark | Qwen3.8 27B | GLM-5.2 | Who wins |
|---|---|---|---|
| AA-Briefcase | 1401 | 1230 | Qwen3.8 27B |
| GDPval-AA | 1411 | 1358 | Qwen3.8 27B |
| AutomationBench-AA | 48% | 28% | Qwen3.8 27B (+20 pts) |
| Terminal-Bench 4.0 | 6% | 1% | Qwen3.8 27B |
| GDP.pdf | 17% | 10% | Qwen3.8 27B |
| AA-LCR | 82% | 78% | Qwen3.8 27B |
| SciCode | 47% | 51% | GLM-5.2 |
| HLE | 34% | 41% | GLM-5.2 |
| CritPt | 5% | 21% | GLM-5.2 |
| AA-Omniscience | -10 | 4 | GLM-5.2 |

Seven of ten go to the 27B dense model. The three heavy losses are all knowledge-recall flavoured. That is the entire story of this model in one table, and it is the same story the August index told — it just has a different total attached now.

## Beats Opus at doing, loses to Opus at knowing

The vendor table says Qwen's own model card claims wins over Claude Opus 4.6 Max on SWE-bench Pro (61.7 vs 53.4), IFBench (79.5 vs 62.5), OSWorld-Verified (84.3 vs 72.7), and AndroidWorld (81.9 vs 62.0), while losing HLE (30.8 vs 40.0) and GPQA Diamond (89.2 vs 91.3).

Those are **vendor-reported numbers from https://huggingface.co/Qwen/Qwen3.8-27B**, run on harnesses that were not identical across vendors. Alibaba is not measuring Opus in Claude's house, and Anthropic is not measuring Qwen in Qwen's. Regolo AI's write-up of the same table frames it as outperforming Opus 4.6 Max on 16 of 24 benchmarks — but a 24-row vendor sweep with mismatched harnesses is a marketing artifact as much as a technical one.

The direction of the claim, though, is corroborated by independent measurement. Artificial Analysis's own current verdict on the model is that it sits "amongst the leading models in intelligence" while being "notably slow and very verbose." AA also found AutomationBench-AA at 48% against GLM-5.2's 28%. Agentic doing, not encyclopedic knowing. Two unrelated evaluation regimes, same silhouette.

The honest one-liner: **Qwen3.8 27B beats much larger models at acting and loses to them at recalling.** Anyone quoting "beats Opus" without the second half is selling you half a model.

## Identical network, fourteen more points: what post-training bought

Here is the fact that explains the whole generational jump and gets buried in most coverage: the architecture is unchanged from Qwen3.6-27B.

The official spec is 27B parameters, hidden dimension 5120, 64 layers, laid out as `16 x (3 x (Gated DeltaNet -> FFN) -> 1 x (Gated Attention -> FFN))`, with Gated DeltaNet using 48 value heads and 16 QK heads at head dim 128, gated attention using 24 query heads and 4 KV heads at head dim 256, an FFN intermediate of 17,408, a vocab of 248,320, and MTP training across multiple steps. That 3:1 hybrid of linear attention to full attention — plus the multi-token-prediction head — is the network both generations share.

So the jump from the predecessor's score to 52 was **entirely post-training**. Nothing in the architecture changed; the model got better at using the network it already had. That is a much more interesting sentence than "new model is better," and it has a practical corollary: if you already tuned an inference stack for the older checkpoint, your deployment assumptions about memory and context carry over almost unchanged. See the [Qwen 3.6 local deployment guide](/posts/qwen-3-6-local-deployment-2026/) for the baseline that still applies.

The MTP head also has a deployment payoff. Unsloth publishes a separate 1.37 GB MTP Q4_0 speculative-decoding head, which you load alongside the main weights to recover generation speed — the single highest-leverage knob on this model outside of quantization.

## The hidden tax nobody puts in the headline: verbosity and xhigh

Artificial Analysis reports 200M output tokens for the index against a median of 82M, and grades the model 1 of 4 on speed at 45.1 tok/s — rank # 54 of 142. Note that the token accounting itself changed with the index version (160M at # 23 of 135 in August, 200M at # 22 of 142 now), while the verdict did not move.

Simon Willison measured the practical version of this in August: at the default reasoning effort, a single pelican-on-a-bicycle SVG took **21 minutes and 22,276 reasoning tokens** to produce 3,223 output tokens. With reasoning off, the same prompt took 137 seconds and 3,715 tokens. That is not a slow model so much as a model configured to think out loud indefinitely.

The configuration matters because it is the *default*. Artificial Analysis measures the "Xhigh" variant, and Qwen's documented ladder is xhigh (default, described as for "complex tasks demanding thorough analysis") / medium / low. Willison's assessment of the default is blunt: xhigh is "absolutely not a good way to run the model."

**The fix is one parameter.** Drop `reasoning_effort` to medium or low for routine work, or disable thinking entirely for tasks where you already know the answer shape — extraction, classification, formatting, short refactors. Budget the quality loss explicitly: xhigh genuinely helps on multi-step agentic work, which is precisely the profile this model is good at. What it does not help is a summarisation call, and it will happily spend twenty minutes proving it.

### Why does it feel so much slower than its predecessor?

Because it is, on identical hardware. TerminalBytes measured Qwen3.8 27B at roughly **14 tok/s** (Q4_K_M, 17 GB) on an M3 Ultra Mac Studio, against about **28.6 tok/s** for the previous generation on the same machine and prompts. Roughly half.

Part of that is verbosity — more tokens generated per useful answer. Part is the dense 27B active path. A commenter on the launch thread framed the serving economics structurally: "It's 27b active params vs 13b active params, so you'd expect it to be ~2x more expensive when serving multiple users." Dense models pay for every parameter on every token; mixture-of-experts models do not. This is the price of the agentic profile in the table above.

## What does it cost to run Qwen3.8 27B?

Free weights, expensive tokens. The paradox is real and it is worth understanding before you pick a deployment mode.

| Path | Cost signal | Source |
|---|---|---|
| Self-host (your hardware) | $0 per token, 6.19 GB to 54.7 GB on disk | Unsloth GGUF sizes |
| Hosted, Artificial Analysis figures | $0.50 / 1M input, $3.00 / 1M output, 80% cache discount, $0.10 cache-hit | AA model page, 2026-10-01 |
| Hosted, blended | Average **$1.01 per Intelligence Index task**, 48.23s to first answer token, 1233.15s per task | AA model page, 2026-10-01 |

Artificial Analysis calls the hosted model "particularly expensive when comparing to other open weight models of similar size." That is the sentence most launch coverage omitted. At launch there was no first-party endpoint at all — AA showed $0.00 in / $0.00 out and Speed N/A — so the $1.01-per-task figure is a *later* addition, arriving with Alibaba's API pricing.

Note also that AA's comparison rule is narrow: open-weight models are compared only against other open-weight models in the same size class (Small = 4B–40B). "# 1 / 142" means first among models of its size and openness, not first overall. Say it that way or don't say it.

## Local reality: which quantization actually holds up?

The quantization study is the most useful independent work published about this model. Piotr Migdal's Quesma benchmark found that the 17 GB Q4_K_M quantization matches the full BF16 model on Terminal-Bench 2.1 while fitting a 24 GB card with roughly 64k tokens of context left over. At 1-bit, by contrast, the model performs around random chance on GPQA Diamond — and longer reasoning makes it worse, not better.

| Quant | Size on disk | Realistic home |
|---|---|---|
| UD-IQ1_S | 6.19 GB | Demonstrates the failure mode; not for work |
| UD-IQ2_XXS / UD-Q2_K_XL | 7.27 GB / 9.83 GB | 8 GB cards, tolerant tasks only |
| UD-IQ3_S / UD-Q3_K_XL | 12 GB / 13.1 GB | 16 GB cards with modest context |
| UD-Q4_K_S / UD-Q4_K_M | 15.4 GB / 16.5 GB | 24 GB cards — the quality floor that holds |
| Q8_0 | 29 GB | 48 GB cards, quality headroom |
| BF16 | 54.7 GB | Reference only |
| MTP Q4_0 head | 1.37 GB (extra) | Speculative decoding, load alongside |

Sizes from [Unsloth's GGUF repository](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF). The engineering point is that quantization choice matters more in practice than two points of index score. A 4-bit run that fits your card and answers in 30 seconds beats a BF16 reference you cannot afford to serve.

One caution on the throughput contradiction: the Mac Studio figure (~14 tok/s at Q4_K_M) and the ~50 tok/s reported by Michal Piszczek for a 256K-context setup on a 24 GB GPU are not in conflict. Different quant, different hardware, different context length, and — in the faster report — a speculative-decoding setup. Never quote a single tokens-per-second number for this model without its context length attached.

### Quick reference: Qwen3.8 27B at a glance

| Attribute | Value |
|---|---|
| Parameters | 27B dense, 27B active |
| Modalities | Text, image, video (natively multimodal) |
| Native context | 262,144 tokens, extensible to 1M via YaRN |
| License | Apache 2.0 |
| Released | 2026-08-14 |
| Default reasoning effort | xhigh |
| AA Intelligence Index (2026-10-01) | 34, # 1 / 142 in its size class |
| AA Intelligence Index (2026-08-18) | 52, # 1 / 135 |

## Is "52" even meaningful? The benchmaxxing argument

This is the fairest question a reader can ask, and the launch thread is where it was fought out.

The critique, from Hacker News: "This one is very benchmaxxed, and you can tell from this page alone. Look at the huge variance in ranking per benchmark."

The rebuttal, from a practitioner who tested it against an internal workflow: it "doesn't look benchmaxxed... These '52 AA score' numbers feel real."

Look at the variance and you can see both sides. A twenty-point AutomationBench-AA lead over GLM-5.2 alongside a sixteen-point CritPt deficit is a jagged profile. That jaggedness is either a red flag or a fingerprint depending on whether your workload lives on the jagged part. For agentic and tool-use work — the part where this model is genuinely strong — the numbers agree across both vendor and independent measurement regimes.

And there is a precision floor that neither camp usually mentions. Artificial Analysis states the Intelligence Index is "a primarily text-based, English-language evaluation," targets **< +/-1% error on the index overall**, and warns that individual evaluations carry wider confidence intervals. A one- or two-point gap between neighbouring models is not a real difference. Anyone ranking models on a two-point delta is reading noise.

If you want a number you can trust, generate your own. Take twenty representative tasks from your actual workload, run them at medium reasoning effort against your real context length, and score them. That result will outperform both 52 and 34 for your purposes.

## Verdict: who should run Qwen3.8 27B in Q4 2026?

Run it if your work is agentic: tool calling, computer use, multi-step coding with test feedback, structured extraction against messy input. The profile is consistent across independent and vendor measurement, and a 27B dense model at Q4_K_M fits a 24 GB card without quality loss on the agentic benchmarks that hold up under quantization.

Wait, or reach for something else, if your workload is knowledge-recall heavy. HLE 34%, AA-Omniscience -10, CritPt 5% — those are the rows where larger and more retrieval-friendly setups win, and where the model's verbosity costs you latency without buying accuracy.

Whichever you choose, set `reasoning_effort` deliberately rather than accepting the xhigh default, budget for roughly half the throughput of the previous generation on identical hardware, and quote the index version whenever you quote the score.

The model did not change between August and October. The ruler did.

## FAQ

**What is Qwen3.8 27B's Artificial Analysis score?**
As of 2026-10-01, the live Artificial Analysis page reports 34 under index version v4.3.2, ranked # 1 of 142 within its size class. In the 2026-08-18 Wayback snapshot the same page reported 52 under index version v4.1.1, ranked # 1 of 135. Both readings are accurate for their date and index version.

**Is 52 still accurate?**
Only if you date and version it. 52 was correct under index v4.1.1 on 2026-08-18. The index has since been re-versioned twice — GPQA Diamond was removed in v4.2, and tau3-Banking was replaced by AutomationBench-AA with Terminal-Bench upgraded to 4.0 in v4.3 — so the current figure is 34. This is re-baselining, not a regression in model quality.

**Is Qwen3.8 27B better than Claude Opus 4.6 Max?**
Depends on the axis. Alibaba's model card claims wins on SWE-bench Pro (61.7 vs 53.4), IFBench (79.5 vs 62.5), OSWorld-Verified (84.3 vs 72.7), and AndroidWorld (81.9 vs 62.0), and losses on HLE (30.8 vs 40.0) and GPQA Diamond (89.2 vs 91.3). Those are vendor-reported numbers on non-identical harnesses. The pattern — better at doing, worse at knowing — is corroborated independently, but the specific deltas are not.

**How much VRAM do I need to run Qwen3.8 27B?**
A 24 GB card runs UD-Q4_K_M at 16.5 GB with roughly 64k tokens of context left over, and that quantization matches full BF16 on Terminal-Bench 2.1. 16 GB cards can run UD-IQ3_S or UD-Q3_K_XL at 12–13.1 GB with reduced context. Avoid 1-bit variants — around random chance on GPQA Diamond. Full BF16 is 54.7 GB.

**Why does Qwen3.8 27B feel so slow?**
Two reasons stacked. The default `reasoning_effort` is xhigh, which produced 22,276 reasoning tokens and a 21-minute generation for a single SVG in Simon Willison's test; dropping to low or medium, or disabling thinking, collapses that. And the model is dense (27B active parameters), running roughly 14 tok/s at Q4_K_M on an M3 Ultra against about 28.6 tok/s for its predecessor on the same machine.

**Is it worth upgrading from Qwen3.6 27B?**
If your tasks are agentic, yes — the architecture is identical, so your deployment assumptions carry over, and the gains came purely from post-training. If your tasks are knowledge-recall heavy, the upgrade buys you less, because that is the axis where the model trails both its competitors and larger peers. Either way, budget for roughly half the throughput.
