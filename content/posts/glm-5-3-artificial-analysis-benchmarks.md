---
title: "GLM-5.3 Benchmarks: Artificial Analysis Scores, Full Comparison Table, and Pricing"
date: "2026-10-01T05:03:36+00:00"
tags:
  - GLM-5.3 benchmarks
  - GLM-5.3 Artificial Analysis
  - GLM-5.3 Intelligence Index
  - GLM-5.3 Artificial Analysis score
  - GLM-5.3 vs GLM-5.2
  - GLM-5.3 vs GPT-5.6 Sol
  - GLM-5.3 vs Kimi K3
  - GLM-5.3 vs Claude Opus 4.8
  - GLM-5.3 vs DeepSeek V4 Pro
  - GLM-5.3 Terminal-Bench 3.0
  - GLM-5.3 DeepSWE
  - GLM-5.3 CyberGym
  - GLM-5.3 coding benchmarks
  - GLM-5.3 pricing
  - GLM-5.3 license
  - GLM-5.3 self-hosting
  - GLM-5.3 Flash vs GLM-5.3
  - GLM-5.3 open weights
description: "GLM-5.3 scores 45 on Artificial Analysis Intelligence Index v4.3.2, down from 60 in August. That drop is a re-base, not a regression."
draft: false
cover:
  image: "/images/glm-5-3-artificial-analysis-benchmarks.png"
  alt: "GLM-5.3 Benchmarks: Artificial Analysis Scores, Full Comparison Table, and Pricing"
  relative: false
schema: "schema-glm-5-3-artificial-analysis-benchmarks"
---

GLM-5.3 benchmarks today: 45 on Artificial Analysis Intelligence Index v4.3.2, 28.3 on Terminal-Bench 3.0, 66.9 on DeepSWE v1.1, and 1769 Elo on GDPval-AA v2 — the highest of any open-weight model. The famous "60" from August is the same model on an older index version.

That is the entire controversy compressed into two sentences. Everything below is the evidence behind it: the vendor table Z.ai published, the independent Artificial Analysis run, the price you actually pay per unit of work, and the capability gaps that did not close.

## What GLM-5.3 Is (and Isn't)? Post-Training on the GLM-5.2 Base

GLM-5.3 is a 753B-parameter mixture-of-experts model with 40B active parameters, a 1M-token context window, and up to 128K tokens of output. It ships as FP8 E4M3 weights, is served by 27 API providers, and is capped by a 1,048,576-token context ceiling that Z.ai markets as "full-repo" scale.

The most important structural fact is not in the launch marketing: **GLM-5.3 uses the same base model as GLM-5.2**. Z.ai's own model card states it plainly. Every benchmark gain you see in the head-to-head tables below came from post-training — reinforcement learning, data curation, and harness work — not from a new pretraining run. That matters when you read the size of the deltas, because it tells you Z.ai's post-training pipeline is doing the heavy lifting, and it means the family will not plateau until that pipeline does.

### Does GLM-5.3 support image input?

No. GLM-5.3 is text-in, text-out only. There is no vision path at all, which is the single clearest gap between it and GPT-5.6 Sol, Fable 5, or Grok 4.6. If your pipeline needs screenshots, diagrams, or PDF-as-image ingestion, you need a different model in the loop — GLM-5.3-Flash (separate weights, image input supported) or a closed frontier model.

### Can you disable thinking on GLM-5.3?

No, and this is a breaking change. Requests that disable thinking fail on GLM-5.3. It is a reasoning model with a `reasoning_effort` control that accepts low, high, or max, and the default is `max`. Migrating from GLM-5.2 with `thinking: disabled` in your request body will produce failures, not degraded answers. Budget your token spend accordingly.

## GLM-5.3 on Artificial Analysis: 45 Today, 60 in August — Why the Number Moved

This is the question that generates more confusion than any other about GLM-5.3 benchmarks. Both numbers are correct.

| Date | Index version | GLM-5.3 score | What changed in the harness |
| --- | --- | --- | --- |
| Aug 18, 2026 | Intelligence Index v4.1.1 | 60 | Original independent run by Artificial Analysis |
| Sep 7, 2026 | Intelligence Index v4.3 | 45 | GPQA Diamond removed; Terminal-Bench 4.0 and AutomationBench-AA added |
| Oct 2026 (current) | Intelligence Index v4.3.2 | 45 | Ranked #2 of 117 in class; class median 18 |

The August score of 60 put GLM-5.3 level with Kimi K3 (60), three points behind Claude Opus 5 (63), 8th of 181 models in its class against a class median of 35. It cost $0.68 per index task versus $0.84 for Kimi K3 and $2.34 for Claude Opus 5, and the full index run cost $1,238.50 on Z.ai's API.

The September re-base swapped a graduate-level science evaluation out and two agentic evaluations in. GLM-5.3's relative position barely moved — it still sits near the top of its class — but the absolute number fell by 15 points because the battery now weights the agentic work where GLM-5.3 is merely good rather than excellent.

**The practical rule: leaderboard snapshots are not comparable across index versions.** A model that "dropped 15 points" overnight without a weight change did not get worse. A vendor that quotes the highest number it ever received is not lying, but it is not being useful either.

## The Full Benchmark Table: GLM-5.3 vs GLM-5.2, Kimi K3, DeepSeek-V4 Pro and GPT-5.6 Sol

The table below is Z.ai's launch-day vendor-run table from August 14, 2026. Treat it as the vendor's claim, corroborated where Artificial Analysis ran the same evaluation independently.

| Benchmark | GLM-5.3 | GLM-5.2 | GPT-5.6 Sol | Fable 5 |
| --- | --- | --- | --- | --- |
| Terminal-Bench 3.0 | 28.3 | 4.6 | 34.6 | 33.7 |
| DeepSWE v1.1 | 66.9 | 46.2 | 72.7 | — |
| SWE-Marathon | 42.5 | 19.4 | — | — |
| Agents' Last Exam | 28.5 | 23.8 | — | — |
| AutomationBench v1.0.6 | 48.2 | 26.2 | — | — |
| CyberGym | 84.5 | 77.2 | — | — |
| ExploitBench | 54.4 | 24.4 | 76.5 | 78.0 |
| GDPval-AA v2 (Elo) | 1769 | 1508 | 1730 | — |

GDPval-AA v2 was run by Artificial Analysis rather than Z.ai, which makes it one of the more trustworthy rows: GLM-5.3's 1769 Elo beats GPT-5.6 Sol (1730), Kimi K3 (1682), DeepSeek-V4 Pro (1590), and Claude Opus 4.8 (1588). On real-world professional deliverables, the open-weight model is at the front of the field, not chasing it.

The rows where it loses are equally specific. GLM-5.3 trails GPT-5.6 Sol on Terminal-Bench 3.0 (28.3 vs 34.6) and DeepSWE v1.1 (66.9 vs 72.7), and it trails both Sol (76.5) and Fable 5 (78.0) badly on ExploitBench (54.4). The pattern is consistent: GLM-5.3 is competitive on general agentic work and clearly behind on adversarial and security-flavored coding.

## Coding and Agentic Benchmarks: Where the Post-Training Gains Actually Landed

The headline number — Terminal-Bench 3.0 going from 4.6 to 28.3 — deserves an honest read. A 6x improvement looks extraordinary, and it is real, but it is measured off a near-floor baseline. GLM-5.2 was barely functional on that harness, so the percentage overstates the absolute capability you are purchasing. The 28.3 figure itself is the number to plan against.

Where the gains are genuinely large against a meaningful baseline:

- **DeepSWE v1.1: 46.2 to 66.9** — a 20-point move on a software-engineering benchmark where GLM-5.2 was already respectable.
- **SWE-Marathon: 19.4 to 42.5** — more than double, on long-horizon software tasks.
- **ExploitBench: 24.4 to 54.4** — more than double, and the reason the safety discussion below exists.
- **CyberGym: 77.2 to 84.5** — a solid gain in an area that was already a strength.

Independent harnesses tell a similar but not identical story. In akitaonrails' OpenCode evaluation, GLM-5.3 scored 94 — two points behind Claude Fable 5 (96) — in 80 minutes at roughly $2.59 in API-equivalent cost, the highest score ever recorded on that harness. On Reinvently's Ed-o-meter, which runs 28 everyday tasks, GLM-5.3 became the first model to clear all five categories at a 100% pass rate with a 9.3 rubric score at $0.28 per lap, roughly one-fifth the cost of GPT-5.5. The cost of that quality is latency: a median 16.3 seconds to first token.

Independent numbers also expose the split the composite hides. On Artificial Analysis's own detailed evals, GLM-5.3 posts Terminal-Bench 4.0 at 42% versus 33% for Flash, and SciCode at 59% versus 52% — but it *trails* Flash on GDP.pdf (11% vs 15%) and ties Flash at 80% on AA-LCR v1.1. The 45-versus-42 composite makes the flagship look unambiguously better. It is not, on every task.

## Cost, Speed and Token Efficiency vs the Closed Frontier

| Metric | GLM-5.3 | Notes |
| --- | --- | --- |
| Input price (per 1M tokens) | $1.40 | Artificial Analysis listing |
| Output price (per 1M tokens) | $4.40 | 81% cache discount available |
| Blended (7:2:1) | $0.90 | Weighted mix |
| Avg cost per Intelligence Index task | $2.01 | Independent run |
| Output speed | 67.8 tok/s | 44.7 tok/s for GLM-5.3-Flash |
| Time to first token | 3.32 s | Slowest tier of frontier models |
| Output tokens across index run | 210M | vs 140M median — very verbose |

The cost-per-unit-of-work picture is more favorable than the raw prices suggest. Artificial Analysis measured $0.68 per index task for GLM-5.3 against $0.84 for Kimi K3 and $2.34 for Claude Opus 5 — a 3.4x advantage over Anthropic's model at comparable index score. An independent September 25 snapshot recorded 63 tok/s for GLM-5.3 against 43 tok/s for Flash.

The token-efficiency angle is where GLM-5.3 is most underrated. On Z.ai Code Bench at High reasoning effort, GLM-5.3 scores 31.4% using roughly 50K output tokens, while Claude Opus 4.8 scores 29.5% using roughly 120K tokens. GLM-5.3 reaches a higher score with less than half the spend. At Max effort it hits 34.5% at ~75K tokens (GLM-5.2: 23.4% at 96K). Fable 5 still leads at Max with 39.5%, but it is not twice as good for the price.

The counterweight is verbosity. 210M output tokens across the index run versus a 140M median means GLM-5.3 thinks at length, and at $4.40 per 1M output tokens that verbosity is billed.

## The Cyber Capability Story and the Delayed Open-Weights Release

GLM-5.3 was released on August 14, 2026, but the weights were withheld at launch and only published on August 28, 2026 under the GLM-5.3 Licence — roughly a two-week safety hold. This is unusual for a Z.ai release and it was driven by the model's security profile.

Anthropic's research reports that GLM-5.3's safeguards can be bypassed 64% to 100% of the time using simple techniques in simulated tests. NIST's CAISI called it "the most cyber-capable open-weight model released to date" and placed it roughly four months behind the US frontier. Those two statements, combined with ExploitBench nearly doubling from 24.4 to 54.4, explain the hold.

Practical consequence for deployers: the license permits commercial use but carries restrictions, and the safety posture means you should not expose GLM-5.3 to untrusted code execution, security tooling, or autonomous network access without your own guardrails. The model is capable; the model's built-in refusals are not the thing stopping a determined attacker.

Hacker News response tracked the shift in perception: the launch post "GLM-5.3: Frontier coding with emergent cyber capabilities" reached 1,171 points and 584 comments, and "GLM-5.3 is now open-weight" reached 806 points two weeks later. On Hugging Face, zai-org/GLM-5.3 recorded 1,372,510 downloads and 2,024 likes as of October 1, 2026.

## GLM-5.3 vs GLM-5.3-Flash: Which One Should You Actually Deploy?

The 753B/40B flagship is not a realistic self-hosting target for most teams. GLM-5.3-Flash is a different model with different weights, and for many workloads it is the better buy.

| | GLM-5.3 (flagship) | GLM-5.3-Flash |
| --- | --- | --- |
| Artificial Analysis Intelligence Index | 45 | 42 |
| Active/total parameters | 40B / 753B | 18B / 320B |
| License | GLM-5.3 Licence (restrictions) | MIT |
| Context | 1M | 1M |
| Image input | No | Yes |
| Price (in/out per 1M) | $1.40 / $4.40 | $0.15 / $0.50 |
| Output speed | 67.8 tok/s | 44.7 tok/s |
| Cost per index task | $2.01 | $0.25 |
| Terminal-Bench 4.0 | 42% | 33% |
| SciCode | 59% | 52% |
| GDP.pdf | 11% | 15% |
| AA-LCR v1.1 | 80% | 80% |

Pick the flagship when you need the top of the agentic curve and the extra 3 index points are worth an 8x price multiple — long-horizon coding, complex tool orchestration, GDPval-style deliverable work. Pick Flash when you need multimodality, an MIT license, or throughput at a tenth of the cost, and accept that you give up ground on the hardest reasoning tasks.

## Vendor Numbers vs Independent Evaluations: How to Read Benchmark Claims

Sort every GLM-5.3 benchmark number into one of three tiers before you trust it.

1. **Independently run, versioned, reproducible.** Artificial Analysis Intelligence Index (45 on v4.3.2), GDPval-AA v2 (1769 Elo), the akitaonrails OpenCode harness (94), Reinvently's Ed-o-meter (9.3 rubric). These are run by third parties with published harnesses.
2. **Vendor-run on a third-party harness.** Z.ai's August 14 table — Terminal-Bench 3.0, DeepSWE, SWE-Marathon, CyberGym, ExploitBench. The harness is real; the run is the vendor's, and vendors choose prompts and attempts.
3. **Directional only.** Anything labeled "with tools," anything with sampling-parameter footnotes, anything whose harness version changed underneath it. HLE with tools is explicitly flagged this way in Z.ai's own footnotes.

A useful sanity check: when a vendor number and an independent number for the same evaluation disagree, the independent one is usually lower and usually closer to what you will experience.

## Verdict — Who Should Use GLM-5.3 in 2026

GLM-5.3 is the strongest open-weight model available on general agentic and professional-deliverable work, and it is not the strongest overall model. It wins on cost-adjusted performance — 1769 GDPval Elo and $0.68 per index task against $2.34 for a comparable closed model — and it loses on the hardest adversarial coding tasks, on multimodality, and on latency.

Deploy it if you run high-volume agentic or coding workloads where a 3x cost advantage compounds, you can absorb 67.8 tok/s and 3.32s to first token, and you are willing to build your own safety envelope. Do not deploy it if you need vision input, sub-second first-token latency, best-in-class security tooling, or turnkey self-hosting of the flagship model at 753B parameters.

Read any single benchmark number as directional. Read the version number next to it as mandatory.

## FAQ

**Is GLM-5.3 better than GLM-5.2?**
Yes, on every benchmark Z.ai and Artificial Analysis measured. The largest absolute gains are on long-horizon agentic tasks — SWE-Marathon (19.4 to 42.5) and ExploitBench (24.4 to 54.4) — because GLM-5.3 kept the GLM-5.2 base model and improved only through post-training.

**Why did GLM-5.3 drop from 60 to 45 on Artificial Analysis?**
The index changed, not the model. Artificial Analysis re-based from Intelligence Index v4.1.1 to v4.3 on September 7, 2026, removing GPQA Diamond and adding Terminal-Bench 4.0 and AutomationBench-AA. The new battery weights agentic work more heavily, which pulled the score down 15 points while leaving GLM-5.3 near the top of its class.

**What does GLM-5.3 cost?**
$1.40 per 1M input tokens and $4.40 per 1M output tokens on Artificial Analysis's listing, with an 81% cache discount and a $0.90 blended rate at a 7:2:1 mix. Average cost per Intelligence Index task measured $2.01. GLM-5.3-Flash is dramatically cheaper at $0.15/$0.50.

**Can I self-host GLM-5.3?**
Technically yes — the weights are open (published August 28, 2026 under the GLM-5.3 Licence, FP8 E4M3) — but the flagship is 753B total / 40B active parameters. Most teams cannot serve it economically. GLM-5.3-Flash at 320B/18B under an MIT license is the realistic self-hosting target.

**Does GLM-5.3 beat GPT-5.6 Sol?**
Head to head, no — it trades. GLM-5.3 wins GDPval-AA v2 (1769 vs 1730 Elo) and loses Terminal-Bench 3.0 (28.3 vs 34.6), DeepSWE v1.1 (66.9 vs 72.7), and ExploitBench (54.4 vs 76.5). It wins decisively on cost, at roughly a third of the closed model's price per index task.
