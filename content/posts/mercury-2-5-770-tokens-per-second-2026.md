---
title: "Mercury 2.5 at 770 Tokens/Second: Which of the Six Published Numbers You Are Actually Reading"
date: 2026-10-12T00:00:00+00:00
tags:
  - mercury 2.5 tokens per second
  - mercury 2.5 review
  - diffusion llm
  - inception labs mercury 2.5
  - mercury 2.5 benchmarks
  - diffusion llm agent loops
  - mercury 2.5 pricing
  - mercury 2.5 time to first token
  - mercury 2.5 vs claude haiku 4.5
  - mercury 2.5 tool calling
  - diffusion llm vs autoregressive
  - llm agent latency 2026
  - llm inference routing 2026
  - structured output json schema llm
  - time to first token benchmark
description: "Mercury 2.5's 770 tokens/second is output speed after the first chunk, not whole-request throughput. Here are the six published figures and what each measures."
draft: false
cover:
  image: "/images/mercury-2-5-770-tokens-per-second-2026.png"
  alt: "Mercury 2.5 at 770 Tokens/Second: Which of the Six Published Numbers You Are Actually Reading"
  relative: false
schema: schema-mercury-2-5-770-tokens-per-second-2026
---

Mercury 2.5's "770 tokens per second" is Artificial Analysis' measure of output speed *after* the first chunk has arrived — not throughput for a whole request. Inception Labs claims 1,107 tok/s as a decode rate on its own infrastructure, and the same independent test that measured 1,241 tok/s as a generation median recorded about 106 tok/s once the whole 600-word request was counted, because the model waited roughly 5.3 seconds before producing its first character.

That ambiguity is the whole story. Mercury 2.5 is simultaneously one of the fastest text generators available and the slowest model to *start* producing text. Everything below follows from that single mechanism, and every figure is dated because the numbers move.

## What Mercury 2.5 Is

Mercury 2.5 is a proprietary, text-only diffusion large language model (dLLM) from [Inception Labs](https://www.inceptionlabs.ai/blog/introducing-mercury-2-5), released 2026-09-08. Its predecessor Mercury 2, shipped 2026-02-24, was the first reasoning dLLM. Mercury 2.5 doubles the context window to 260,000 tokens with a maximum output of 65,536 tokens, and it is served through Inception's API, Baseten, and OpenRouter behind an OpenAI-compatible chat completions endpoint. Per Inception's own model documentation, the standing list price is $0.20 per million input tokens and $0.75 per million output tokens, with an 80% launch discount to $0.04 and $0.15 that is still active.

The mechanism matters more than the spec sheet. A conventional autoregressive model such as Claude Haiku 4.5 or Gemini 3.5 Flash-Lite emits one token at a time, left to right, and can therefore stream a partial answer immediately. A diffusion model starts from a masked sequence and iteratively denoises the *entire* output in parallel. Inception's architecture paper describes the approach plainly: the models are "parameterized via the Transformer architecture and trained to predict multiple tokens in parallel".

That is the source of both the speed and the silence. If you want the underlying prefill/decode fundamentals, the [LLM Inference Engineering Guide](https://baeseokjae.github.io/posts/llm-inference-engineering-guide/) covers them; this article stays on what diffusion changes about the number on the box.

## "770 Tokens Per Second": Six Published Numbers, and What Each One Measures

Every search for "mercury 2.5 tokens per second" returns a different number, because the number depends entirely on where you start and stop the stopwatch. Every figure below is real. They measure different things.

| Figure | Source and read date | What it actually measures |
|---|---|---|
| 1,107 tok/s | Inception Labs launch post, read 2026-10-12 | Vendor decode rate on widely-available NVIDIA GPUs, on Inception's own infrastructure |
| 780.8 tok/s | Artificial Analysis, quoted by Ground Truth, 2026-09-24 | Output tok/s through the API, measured after the first streamed chunk |
| 770 tok/s | Artificial Analysis snapshot, HN item 49823348, 2026-09-23 | The same definition, an earlier snapshot — the headline this article's slug carries |
| 753.3 tok/s | Artificial Analysis model page, read 2026-10-12 | The same definition, the current reading; the metric moves |
| 1,241 tok/s median | Puter four-model hands-on test, 2026-09-10 | Median generation rate across 10 runs on a 600-word prompt; observed range 727–1,756 |
| 106 tok/s | Puter, same test | Effective rate across the whole request, including the wait for the first character |

The rule worth carrying into your own procurement notes: never write down a tokens-per-second figure without naming its measurement window. A vendor decode rate, a post-first-chunk benchmark rate, and a whole-request effective rate differ by more than an order of magnitude on the same model.

Two details deserve emphasis. First, the Artificial Analysis figure is a moving target: secondary coverage cites 780.8 tok/s with 2.91 seconds to first token on 2026-09-24, the Hacker News submission carried 770 tok/s on 2026-09-23, and the live page reads 753.3 tok/s with a 3.31-second wait to first token when read on 2026-10-12. Treat all three as dated snapshots of one vendor's continuously refreshed metric, not as constants, and not as a disagreement about the model. Second, that same live page places Mercury 2.5 second of 180 models on output speed while scoring 12 on the Artificial Analysis Intelligence Index against a median of 13 for comparable models — exceptional output speed, below-median raw intelligence for its price tier.

**Scope note.** An earlier draft of this article carried a billed end-to-end throughput range from a third-party benchmark. That source is no longer reachable (its host now serves a parked landing page, and no archived copy resolves), so the row was withdrawn rather than republished without a citable measurement. The six figures above are the ones that could be traced to a dated, reachable source on 2026-10-12.

## The Inversion: Fastest at Generating, Slowest at Starting

Parallel denoising has no partial draft to hand you. Puter's four-model test measured time to first token in every condition, and Mercury 2.5 came last every time:

| Condition | Mercury 2.5 | Claude Haiku 4.5 / Gemini 3.5 Flash-Lite |
|---|---|---|
| Short answer | 1,075 ms | ~600 ms |
| JSON response | ~1.1 s | ~600 ms |
| 600-word essay | 5,338 ms | ~620 ms |
| Long prefill | 1,720 ms | ~600 ms |

The delay scales with how much the model is about to *write*, not how much it read. That is the opposite of the conventional prefill bottleneck. Artificial Analysis independently measured a 3.31-second wait to the first answer token on the same model when read on 2026-10-12, which corroborates the direction.

One more finding is easy to miss: Mercury 2 was consistently *faster* to first token than Mercury 2.5, by 2.3x on the short prompt and 8.3x on the long one. The newer model regressed on the exact metric that voice agents depend on. Puter summarized the experience as "the request is mostly silence, then the finished output", and groundtruth.day's framing is the one to keep: unusually fast generation after a noticeable initial wait — not instant frontier intelligence.

## Why Diffusion Behaves This Way

Two architectural facts explain every number above.

**Parallel denoising.** The model predicts multiple tokens at once across the whole sequence rather than committing to token n before considering token n+1. That is where the decode speed comes from, and it is also why the response arrives in a handful of large blocks rather than a fine token stream. If your UI animates a token-by-token typewriter effect, expect it to render as a few abrupt chunks.

**Bidirectional attention and no causal cache.** Without a causal mask there is no incrementally reusable KV cache in the classic sense — open diffusion models historically had to recompute the full sequence at each denoising step, which is why early dLLMs were not actually fast in production. Inception's paper does not publish the caching strategy behind Mercury 2.5's rate, so the decode mechanism is asserted by the vendor rather than externally reproducible from the paper.

## What That Buys an Agent Loop, and What It Does Not

Inception's framing at launch was that one search request can trigger dozens of model calls, and it names search agents, RAG pipelines, voice agents, and coding subagents as target workloads. The arithmetic is straightforward: a five-step agent loop at two seconds of generation latency per step is ten seconds of pure model time before tool execution and network overhead enter the picture. If your bottleneck is decision *latency* rather than decision *quality*, a faster decoder is a bigger lever than a marginally smarter model.

The compounding argument only holds if the loop is latency-sensitive on the producing side and latency-insensitive on the consuming side.

- **Where it compounds in your favor:** batch pipelines, retrieval and reranking stages, context compaction, tool-call formatting, and autonomous pipelines with no human watching.
- **Where it backfires:** anything a human watches stream. Five seconds of silence followed by a wall of text *reads* slower than text that starts appearing in half a second, even when the wall of text finishes sooner in wall-clock terms.

Inception reports two production deployments at launch, both vendor-reported rather than independently audited: Augment Code cut context-compaction latency 82% (roughly 150 seconds to 27 seconds) and cost 90% while moving compaction, model routing, and MCP tool search to Mercury, with tool-search summaries under one second; OpenCall reports P99 response time falling from "several minutes to just one second" and P50 from 0.4 seconds to under 0.2 seconds. Take the direction seriously and the precise percentages as marketing until someone audits them.

## The Routing Table: Which Agent Steps Belong on Mercury 2.5

The useful insight is that latency and intelligence are now separable axes you can route on independently, the same way teams already route on cost. The [Multi-Model LLM Routing Guide 2026](https://baeseokjae.github.io/posts/multi-model-llm-routing-guide-2026/) covers the general pattern; here is the Mercury 2.5-specific split.

| Route to Mercury 2.5 | Keep on a frontier model |
|---|---|
| Structured intermediate steps: JSON tool-call formatting, diff and lint generation, template filling | The planning and reasoning step of any agent loop |
| Context compaction and summarization of long histories | Multi-file refactors with cross-file invariants |
| Reranking, extraction, classification, routing decisions | Security-sensitive code review |
| Judge and arbiter roles, draft-then-verify patterns | Quality-critical customer-facing generation |
| Document parsing and high-volume retrieval pre-processing | Anything where a wrong decision costs more than the latency saved |

The procurement question to answer first is not "is Mercury 2.5 good?" but "is my workload quality-limited or speed-and-cost-limited?" Search retrieval, compaction, tool-call summarization, document parsing, and classification typically are not quality-limited. With an Intelligence Index of 12 against a median of 13, the model is average in raw reasoning for its price tier while being exceptional at producing text quickly — and for a compaction step, that trade costs far less than the latency and money it saves. For an architectural planning step it is the entire ballgame.

## The Real Price: Two Numbers, Not One

| Line item | Launch rate (80% off) | Standing rate |
|---|---|---|
| Input | $0.04 / M tokens | $0.20 / M tokens |
| Output | $0.15 / M tokens | $0.75 / M tokens |
| Cached input | $0.004 / M tokens | $0.02 / M tokens |

The discount is promotional, not permanent. As of a 2026-10-12 read of OpenRouter's machine-readable endpoint metadata, the 0.8 launch discount was still active and the model advertises tool calling, structured outputs, and `reasoning_effort` among its supported parameters. Budget for the standing rate and treat the discount as an evaluation window. Artificial Analysis also lists the observed endpoint at $0.25 in / $0.75 out, so the price you will actually be billed depends on which route you send the call through — read the endpoint, not the launch post.

For agent loops specifically, cached-input pricing matters more than it looks, because a multi-turn loop re-sends the same context on every call. The [LLM Context Window Comparison 2026](https://baeseokjae.github.io/posts/llm-context-window-comparison-2026/) places the 260K window and 65,536 max output against the wider field.

## How to Evaluate It on Your Own Traffic

Do not benchmark tokens per second. Build a task set instead. This is an in-article checklist, not a downloadable fixture — it needs nothing from this site but your own payloads:

1. **Collect 20–50 real tasks** from the agent step you are considering moving — actual payloads, not synthetic prompts.
2. **Score cost per successful workflow**, not cost per call. A cheap call that returns nothing usable is infinitely expensive.
3. **Count tool-call accuracy and retries.** This is where diffusion's formatting weakness would surface in practice, and it is invisible in a throughput benchmark.
4. **Measure time to first token and total wall time separately**, at each `reasoning_effort` level, because the effort setting moves both.
5. **Test at your real output lengths** and compare the generation rate against the whole-request rate for that length specifically.
6. **Verify strict JSON schema against your own payloads**, not against the capability list.
7. **Re-run the same set on your current model** so the comparison is apples to apples on your traffic rather than someone else's prompt.

## Does the Agentic Evidence Hold Up?

Not fully, and the contradiction is worth stating plainly rather than resolving with marketing copy.

Inception lists schema-aligned JSON and parallel tool calls as headline capabilities. Against that, a peer-reviewed ACL 2026 paper — "The Bitter Lesson of Diffusion Language Models for Agentic Workflows" ([arXiv 2601.12979](https://arxiv.org/abs/2601.12979)) — evaluated diffusion LLMs including LLaDA and Dream across embodied and tool-calling agentic paradigms and reports that "current dLLMs fail to serve as reliable agentic backbones", that "in Embodied settings, dLLMs suffer repeated attempts, failing to branch under temporal feedback", and that "in Tool-Calling settings, dLLMs fail to maintain symbolic precision (e.g. strict JSON schemas) under diffusion noise". The paper also identifies where dLLMs *are* effective: "non-causal roles (e.g., memory summarization and tool selection)" — precisely the support-call territory Inception targets, not the planning call.

The caveat keeps this honest: the paper tests open diffusion models, not Mercury 2.5, which is proprietary and may carry inference-time fixes. It explicitly does not validate Mercury. What it does establish is that the burden of proof sits on the vendor for exactly the capabilities Mercury 2.5 markets.

Then there is field evidence from Hacker News. The launch submission drew 248 points on 2026-09-08, and the "Mercury 2.5 LLM hits 770 tokens per second" submission drew 151 points on 2026-09-23 — reception that treats the model as genuinely fast and genuinely not frontier. That is consistent with everything above: the throughput claim and the average-intelligence score are both real, and they describe different task types.

## Verdict: A Support Model, Not a Brain

Mercury 2.5 creates a real and new point on the price–speed–quality frontier: the fastest output generator in its field on post-first-chunk speed, and — critically — slow to start and only average in raw reasoning.

That combination is not a contradiction; it is a routing instruction. Route structured intermediate steps, compaction, reranking, extraction, judging, and other high-volume utility calls to Mercury 2.5. Keep planning, cross-file refactors, security review, and anything a human watches stream on a frontier model.

Its advantage is algorithmic rather than silicon — no special hardware, no speculative decoding — which is why it belongs beside [Cerebras CS-4](https://baeseokjae.github.io/posts/cerebras-cs-4-inference-hardware/) coverage as the software-side answer to the same wall-clock-latency problem for agent loops. The recurring community objections are that Cerebras-class hardware runs open models at comparable rates, that open-weight DeepSeek and Qwen models are cheaper at similar quality, and that diffusion LLMs are a dead end. The first two are routing constraints rather than refutations, and the third remains unsettled.

One last piece of context: the workload Inception targets most heavily is search and RAG, and bigger context windows have repeatedly failed to make retrieval smarter on their own. If that is your planned use case, the honest counterweight is [Bigger Context Windows Didn't Make Our RAG Smarter](https://baeseokjae.github.io/posts/bigger-context-windows-rag-smarter-2026/).

Bottom line: worth a routing-table slot this quarter, worth a 20-task evaluation before you commit, and not a frontier replacement. If a human is watching the output stream, look elsewhere.

## FAQ

**Is Mercury 2.5 really 1,107 tokens per second?**

That is Inception's decode-rate claim, measured on its own infrastructure, and it is a real number for what it measures: speed after output starts. Independent measurement lands differently once you change the window — 1,241 tok/s as a generation median over 10 runs in one four-model test, 753.3 tok/s on Artificial Analysis when read on 2026-10-12, and about 106 tok/s counted across the whole 600-word request.

**Why is the fastest model also the slowest to start?**

Because a diffusion model refines the entire answer in parallel instead of emitting token by token. There is no partial draft worth streaming, so the request is mostly silence and then the finished output. In a controlled four-model test Mercury 2.5 was last to first token in every condition — 1,075 ms on a short answer and 5,338 ms on a 600-word prompt, against roughly 600 ms for its designated peers — and the delay scaled with how much it was about to write, not how much it read.

**How much does Mercury 2.5 cost?**

The standing rate is $0.20 per million input tokens and $0.75 per million output tokens, with cached input at $0.02. The launch promotion is 80% off — $0.04 input, $0.15 output, $0.004 cached input — and it is promotional rather than permanent; OpenRouter's endpoint metadata showed the 0.8 discount still active on 2026-10-12, while Artificial Analysis listed the observed endpoint at $0.25/$0.75.

**Does Mercury 2.5 support tool calling and structured output?**

Both appear on the capability list, and OpenRouter's endpoint metadata advertises `tools`, `tool_choice`, `response_format`, `structured_outputs`, and `reasoning_effort` on the 260K-context endpoint. That is a capability declaration, not a measured accuracy result: no independent tool-calling benchmark was verified while writing this, and the ACL 2026 result above is a reason to test strict schemas on your own payloads rather than trust the list.

**Is Mercury 2.5 open source, and is it multimodal?**

No to both. It is proprietary, with no published weights, parameter count, or VRAM requirement, available only through Inception's API, Baseten, and OpenRouter. Input and output are text only, so vision or audio workloads need another model alongside it.

## Sources

- Inception Labs, "Introducing Mercury 2.5" — https://www.inceptionlabs.ai/blog/introducing-mercury-2-5
- Inception Labs model documentation (pricing, context, max output, modality) — https://docs.inceptionlabs.ai/get-started/models
- Artificial Analysis, Mercury 2.5 model page (read 2026-10-12) — https://artificialanalysis.ai/models/mercury-2-5
- Ground Truth, "Output speed the headline, first-token latency the caveat" (2026-09-24) — https://groundtruth.day/news/mercury-2-5-diffusion-llm-speed-second-on-artificial-analysis.html
- Puter, "Mercury 2.5 Review" (2026-09-10) — https://developer.puter.com/blog/mercury-2-5-review
- OpenRouter endpoint metadata for Inception Mercury 2.5 (read 2026-10-12) — https://openrouter.ai/api/v1/models/inception/mercury-2.5/endpoints
- Hacker News, "Mercury 2.5 LLM hits 770 tokens per second" (2026-09-23) — https://hn.algolia.com/api/v1/items/49823348
- Hacker News, "Mercury 2.5" launch submission (2026-09-08) — https://hn.algolia.com/api/v1/items/49616354
- Inception Labs, "Mercury: Ultra-Fast Language Models Based on Diffusion" — https://arxiv.org/abs/2506.17298
- Lu, Ding, Zhang, Zhang, Tao, "The Bitter Lesson of Diffusion Language Models for Agentic Workflows" (ACL 2026) — https://arxiv.org/abs/2601.12979
