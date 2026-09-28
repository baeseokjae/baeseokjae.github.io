---
title: "Laya Jev OS on Mac M4 CoreML: The Offline 45-Decisions/Second Claim, Fact-Checked"
date: 2026-09-28T20:37:57+00:00
tags:
  - laya jev os mac m4 coreml offline
  - laya coreml mac install
  - laya vs jev benchmark
  - laya offline decision model apple silicon
  - system one decision model mac
  - coreml neural engine transformer latency
  - open source jev alternative local
  - laya-coreml snake demo
  - 45 decisions per second mac ai
  - apple silicon typed decisions offline
  - laya 96 token limit ane
  - run decision model without cloud mac
description: "Laya on Mac M4 CoreML is real but the headline is stitched together: 45 decisions/s was measured on M3 Max, uncapped, and M4 is a gist title."
draft: false
cover:
    image: "/images/laya-jev-os-mac-m4-coreml-2026.png"
    alt: "Laya Jev OS on Mac M4 CoreML: The Offline 45-Decisions/Second Claim, Fact-Checked"
    relative: false
schema: "schema-laya-jev-os-mac-m4-coreml-2026"
---

Laya as an offline OS for Jev on Mac M4 Core ML is a headline stitched from three separate sources, and only one of them survives inspection. The Core ML port is real, Apache-2.0 licensed, and genuinely runs without a network. The M4 label comes from a four-line install gist title, not a benchmark. The 45 decisions per second figure is an uncapped average measured on an M3 Max, rounded down from 49.66/s — and when the same port was asked to hold a 50/s deadline, more than half the ticks missed.

That is the whole review in one paragraph, but the interesting part is not that a headline was inflated. It is that the repository behind it publishes its own failures in more detail than most projects publish their successes, and that the inflated number and the honest engineering come from the same author. Laya's port is worth running. The claim you probably arrived on is worth correcting first.

## What is Laya on Mac M4 Core ML, in one sentence per part?

Laya is a 322M–421M parameter non-autoregressive decision model that answers a multiple-choice question in a single forward pass. `mizorewww/laya-coreml` is a community port that compiles those same weights to Core ML so the Neural Engine can run them locally. "Mac M4" is a phrase from the fordnox gist description, and the M4 benchmark it implies does not exist anywhere in the repo.

Three claims, three verdicts:

| Claim in the headline | What the primary source actually says | Verdict |
|---|---|---|
| "Mac M4" | Every headline measurement is M3 Max, 40-core GPU, 128 GiB, macOS 27.2. No M4 benchmark exists in the repo. Phrase originates in the gist title "Laya on Mac m4 CoreML Offline" | Not verifiable |
| "CoreML offline" | Weights download once; inference afterwards needs no PyTorch, MLX or Transformers and no network | Verified |
| "45 decisions per second" | Closest published values are 49.1–50.0/s uncapped (M3 Max, pooled 49.66/s) and 44.21/s observed against a requested 50/s — which failed with 53.33% deadline misses | Partially verifiable |

The pattern is familiar enough that it is worth naming: a correct technical artifact acquires a simplified label in a one-line post title, and the label outlives the artifact. The gist that made "Mac m4 CoreML" the search phrase contains exactly four shell commands. It publishes no timing table of any kind. The only measurement in that thread is a `/usr/bin/sample` memory dump showing 560.4 MB physical footprint and 778.0 MB peak on macOS 27.0.

Even the original author walked it back. In the 178-point Hacker News thread, fordnox concedes that "maybe OS Jev is too strong of a wording." That is a fair concession, and it points at the real story underneath.

## What is Laya actually — a decision engine, not a chat model?

Laya is not a chatbot that happens to answer multiple-choice questions. It is a ModernBERT-large encoder, published by `convaiinnovations` on Hugging Face under Apache-2.0 on 2026-09-18, with three variants: a 421M English model at 512 tokens, a 322M multilingual model at 1024 tokens, and a 421M typed-decisions model. It outputs a scored judgement over a supplied option list rather than generating text token by token.

That architectural difference is the whole reason the latency numbers look the way they do. There is no autoregressive decode loop, no KV cache growth per option, and no JSON to generate. You give it a question and a set of candidates; you get back a ranking with probabilities in one forward pass. TypeSafe's hosted Jev is the commercial version of the same idea, launched 2026-09-15 in early access at $0.042 per million input tokens with output tokens free and up to 255 options.

Engagement on the weights is substantial: 4,285 likes on the main Laya model, 127 on `laya-typed-decisions`, and 524 downloads of the Core ML ANE bundle checked on 2026-09-28.

The thing that actually changed in late September 2026 was not the model. It was the number of places it could run. Six runtimes appeared over roughly 72 hours from different people moving the identical weights: MLX, Core ML with Neural Engine, browser WASM, Node, Android LiteRT, and an edge NPU path. No retraining, no new checkpoints, no fine-tunes. The port is the story, and the port is what makes an offline OS claim interesting at all.

## Where did "Mac M4" come from?

It came from a gist title. `fordnox/e592d0f68b543fd044be8e6d040863a0`, posted 2026-09-20, now at 34 stars and 4 forks, is titled "Laya on Mac m4 CoreML Offline." Its entire body is four commands:

```bash
uv init
uv add 'laya-coreml[demo]'
hf download <the ANE bundle>
# then run the Snake demo
```

There is no `time`, no benchmark script, no throughput table, and no hardware spec beyond the phrase in the title. The one commenter who contributes a real measurement is ImJasonH, reporting an iPhone 15 Pro running the same weights with a one-shot decision in about 40 ms. That is a stronger portability signal than the M4 claim, and it is a third-party report rather than a controlled benchmark, so treat it as directional.

If you are buying an M4 because of this headline, you are buying based on a title. The repository measures M3 Max. A cross-backend bench comparing M5 Max and M4 Pro circulates in the wild, but it is a two-form-factor comparison, so thermal headroom is a confound rather than a controlled variable. Nobody has published an M4 number for this port.

## What does 45 decisions per second actually measure?

It measures an uncapped game loop on an M3 Max, and it is an average rather than a promise. Across three sequential 600-step Snake episodes — with three model questions per move, 1,800 decisions total — the port sustains 49.1 to 50.0 decisions/s, pooled at 49.66/s, with zero deaths and two safety interventions. The loop was never asked to hold a rate. It was allowed to run as fast as it could.

That distinction matters more than the two-point gap between 45 and 49.66, because it changes the claim from a measurement into a specification. An uncapped average tells you what the hardware did when nothing was watching the clock. A sustained rate tells you what you can build against. Those are different numbers, and the repo publishes both — which is why the rounded "45" is the tell:

| Setting | Observed rate | Deadline result |
|---|---|---|
| Uncapped (Snake loop) | 49.1–50.0/s, pooled 49.66/s | No deadline imposed |
| 20 req/s requested | 18.39–18.42/s over 600 moves | Passed, 0.67% misses |
| 30 req/s requested | — | Failed |
| 40 req/s requested | — | Failed |
| 50 req/s requested | 44.21/s | Failed, 53.33% deadline misses |
| 60 req/s requested | — | Failed |

Read the table the way an engineer would. The uncapped ceiling is about 50 decisions/s on an M3 Max. The highest rate that actually holds a deadline is 20/s, where the port observed 18.4/s and missed 0.67% of deadlines. Everything at 30/s and above failed. The "45" in the headline sits between the fastest thing the hardware ever did and the fastest thing it can be trusted to do, and it reads like the second one.

One more number in the brief is worth checking against the claim that this is a 10x speedup: the port's own comparison table claims a 10.4x average against TypeSafe's published Jev numbers. That is a comparison against a vendor's published figures, not a head-to-head run on identical hardware.

## The paced sweep nobody quotes

The 45 decisions/s headline and the paced sweep come from the same document, and only one of them travels. That is worth dwelling on, because the paced result is the more useful engineering artifact.

A deadline sweep is how you find out whether a system is suitable for a real-time workload. If you are deciding at a control-loop rate — a game tick, a robot safety check, a trading gate — you do not care about the average. You care about the tail. The M3 Max port, running a local decision model with no network hop, could not hold 30 requests per second while meeting its deadline. At the requested 50/s setting it delivered 44.21/s and missed on 53.33% of active ticks.

So the honest summary is: this thing is fast, and its fast is roughly 20 decisions/s if you need every decision inside a deadline. If you are batching offline analysis and latency does not gate correctness, the uncapped 50/s applies and the deadline discussion is academic.

The latency distribution during that uncapped loop is also published, which makes the picture concrete. A three-question API call took 16.32 ms at P50 and 21.33 ms at P95. A full active tick — the three-question call plus everything around it — took 19.07 ms at P50 and 25.96 ms at P95. Those are the numbers to build a budget from, not the headline rate.

## The single-question numbers that matter more for offline inference?

A single short multilingual decision lands at 4.98 ms P50 and 5.31 ms P95 on FP16 through the Neural Engine, measured over 65,598 stable calls. The W8 palette-compressed variant is 4.88 ms and 5.23 ms. Those two figures are the ones I would quote to someone designing an offline system, because they are the tail as well as the median, and the sample count is large enough to mean something.

The energy result is the more interesting engineering claim, and it is also the one carrying the most caveats. Against the port's own compiled MLX FP16 baseline at 6.94 ms P50 / 7.39 ms P95, the Neural Engine path is 1.39x faster and 2.78x better on whole-system energy per decision. With W8 compression it is 1.42x and 3.19x. In joules per decision, that is 0.4288 J for compiled MLX against 0.1540 J for ANE FP16 and 0.1344 J for ANE W8, with power sampled from SMC PSTR sensors across 1,101 retained samples peaking at 74.47 W.

Two things about that comparison deserve to be stated plainly. First, the author asked for 10x and published 1.39x. The gap between the requested target and the delivered result is in the repository, not in a footnote. Second, whole-system energy estimates carry sensor and background-load uncertainty, so the direction of the result is more trustworthy than the third decimal place.

There is also a trap hidden in those same benchmark files. A plain Core ML CPU+GPU export is *slower* than MLX on the same workload — 11.28 ms versus 7.87 ms P50 for one question. CPU-only measured 82.54 ms and CPU+NE 81.34 ms. In other words, the speedup does not come from "using Core ML." It comes from a specific graph rewrite that makes the Neural Engine the preferred compute unit. The repository's own CPU-plan attribution shows that in the plain export, the Neural Engine was never preferred. If you export this yourself without that rewrite, you will produce a slower model and conclude the port was overhyped.

Fidelity is checked too, which is the part that makes the speed numbers meaningful. Three general checkpoints match upstream on 189 of 189 validation questions. The ANE FP16 L96 configuration passes 59 of 59 with a maximum probability drift of 0.002925. The port also rejected its own 6-bit and 4-bit experiments at that fidelity gate rather than shipping them.

## How do you set this up offline, and what breaks first?

Installation really is short. The gist's four commands are approximately the whole procedure, assuming Apple Silicon, macOS 15 or newer, and Python 3.11 through 3.13. Your weights download once and are cached; after that, inference needs no PyTorch, MLX or Transformers — so no network, which is the claim that holds up.

The thing that breaks first is the token budget. The ANE bundle is capped at 96 total tokens covering question, options and state *combined*. A real 1024-token request on the separately exported ANE graph takes about 91.7 ms. So if your decision problem has a long context — a stack trace, a policy document, a long tool result — you are not running that on the Neural Engine path. You are back on CPU+GPU, which the same benchmarks show is slower than MLX.

| Constraint | Value | What it means for you |
|---|---|---|
| ANE bundle token cap | 96 total (question + options + state) | Long-context decisions fall off the ANE path entirely |
| Long request on ANE graph | ~91.7 ms for 1024 tokens | Fine for batch, wrong for a control loop |
| Core ML model build | 3.4–4.2 s on first load | Not a per-request cost, but a cold-start cost |
| First short prediction | 313–475 ms before warmup | Warm up before you measure anything |
| Recommended default | Core ML CPU+GPU | The ANE path is the tuned option, not the default |
| Runtime memory | 560.4 MB physical, 778.0 MB peak | The Snake demo's footprint |
| Low-memory alternative | 171 ms at 0.74 GiB (streamed layers) | Or 32 ms at 2.11 GiB on the MPS port |

That last row is worth pulling out. `afshinm/laya-mps` takes the Metal Performance Shaders route instead, with a ~843 MB download and support for Apple Silicon M1 and up on macOS 14+. On an M5 Pro it measures 32 ms median latency at 2.11 GiB peak RSS in the normal configuration, or 171 ms at 0.74 GiB in minimal mode, where layers stream from disk. All three memory settings matched exactly on 260 of 260 decisions including probabilities, which is a genuinely useful correctness control. If you are memory-constrained rather than latency-constrained, that port is the better starting point.

Memory on this class of model also changes what "offline OS" plausibly means. A 778 MB peak footprint is small enough to sit resident on a laptop alongside real work, which is why the phrase is tempting. But 96 tokens of context is not an operating system's decision surface.

## The calibration warning that should be in every tutorial

The shipped `choice:11+` temperature bucket is 0.1006, and the port clamps it into a 0.5–5.0 range at serving time. Read that sentence twice, because it is the single most important operational detail in this whole ecosystem.

The reason for the clamp is that 0.1006 would have caused the model to report a coin flip as near-certainty. A temperature that low concentrates probability mass, so surface confidence comes back looking decisive when the underlying judgement is not. If you build a gate on top of that number — "only act if confidence exceeds 0.9" — you will build a gate that opens on noise.

The model card itself says the model is overconfident and needs domain-specific calibration, and `astgl.com`'s deployment writeup makes the same point from production experience: confidence here is entropy-derived, not a success probability. If you are shipping this, read `agent.temperature_raw` rather than trusting the surface confidence value, and calibrate against your own labelled decisions before you let the number gate anything.

The same writeup contains the design discipline that I think defines the correct use of this class of model. The deployed service on a Mac Studio M3 Ultra with 256 GB is local-only, exposes TypeSafe's exact wire shape on `127.0.0.1:8017`, and only ever ranks pre-filtered survivors — at most 5 options plus an abstain choice. Permission never comes from the model; the gateway re-validates the returned option, the confidence and the margin. It fails closed: it refuses to download anything at inference time, rejects over-budget token requests instead of letting the runtime silently truncate, caps `Choice` at 20 options, and serializes inference. One use case, post-failure recovery, failed acceptance testing and was disabled.

That is what a mature integration of a 322M decision model looks like. The model ranks. Your code decides.

## Where does Laya lose to Jev, and where does it win?

The strongest counterweight to the offline-OS framing is `gazelle93/decision-models-under-pressure`, which benchmarked seven systems across 200 items per domain against pre-registered pass/fail rules. It does not show that Laya is bad. It shows that the property Laya is marketed on — a fast, local, typed judgement — degrades with exactly the kind of input that makes typed decisions valuable.

| Measurement | Laya | Jev |
|---|---|---|
| Accuracy at 128 candidates | 39% | 60% |
| Accuracy at 128 candidates, best other open model | 41% | — |
| Chance baseline at K=128 | 0.8% | 0.8% |
| Accuracy loss per doubling of option list | −0.073 | −0.043 |
| Answer changes under option reordering | 49.4% | 14.6% |
| Answer changes with order fixed | 0.0% | 0.0% |
| Accuracy loss when distractors become plausible | −0.351 | −0.105 |

Three rows are doing the real work. Laya loses accuracy roughly 1.7x faster than Jev as the candidate list grows. It changes its answer on 49.4% of decisions when you shuffle the option order, against Jev's 14.6% — so an unstable option order is not a cosmetic concern, it is a correctness concern. And it loses 0.351 accuracy when distractors get plausible, more than three times Jev's 0.105.

The order-sensitivity number has a direct mitigation, and it is in the same table: with option order fixed, both models are 0.0%. Stable, deterministic ordering is not an optimization for this class of model, it is a requirement.

The study's conclusion is quoted in the brief and deserves repeating, because it explains why the headline number and the under-pressure number can both be true: Laya is the weaker implementation of a real idea, and a single-number benchmark hides this because at K=2 Laya trails Jev by only two points. At two options, everything looks fine. At 128 options the gap is 21 points.

Where Laya wins is not accuracy. It is privacy, cost and control — and `astgl.com` says so explicitly, having chosen Laya over Jev for privacy and control and refusing to quote a hardware break-even number. If your decisions involve data that cannot leave the machine, a 39% model that runs on `127.0.0.1` beats a 60% model that does not. That is a real trade, not a rhetorical one.

There is also an architectural rebuttal circulating: Privatemode's writeup argues an off-the-shelf LLM such as GLM-5.3-Flash can be prompted into single-forward-pass typed decisions with per-option probabilities, reaching parity with Jev on accuracy and speed, because the JSON shape is known in advance and only the typed judgement tokens need reading from the logits. It also adds image-based typed decisions, which Jev cannot do. If that holds, specialized decision models are a latency and cost optimization over prompting rather than a capability class of their own. I would not dismiss the argument just because it is unflattering to the thing this article is about.

## How do you reproduce these numbers yourself?

Pin the revision, then compare like with like. The repo's last push was 2026-09-22, so take a commit SHA rather than `HEAD`, and note that the model construction takes 3.4–4.2 s with a 313–475 ms first prediction — so discard a warmup period before you record anything, or you will measure the build cost as latency.

Then be explicit about what you are comparing. Three comparisons get conflated constantly:

- Against the compiled MLX FP16 baseline, the ANE path is 1.39x faster and 2.78x better on energy. This is the port's own measured claim, and it is the right one to quote.
- Against TypeSafe's published Jev figures, the project's table claims a 10.4x average. That is a comparison to a vendor's numbers, not a head-to-head run on identical hardware.
- Against a plain Core ML CPU+GPU export, the ANE path wins but the plain export *loses* to MLX. If your export does not include the graph rewrite that makes the Neural Engine preferred, you will replicate the failure mode, not the result.

Measure the tail, not just the median. A P95 of 5.31 ms and a P95 of 25.96 ms for the full tick tell you very different things about whether this can sit in a request path. And run a paced sweep at your intended rate, because that is the test that separates the uncapped ceiling from the rate you can build on.

If you want a broader map of what will actually run on your machine locally, my writeups on [on-device model options](/posts/best-local-llm-models-2026/) and [Apple's Foundation Models framework](/posts/apple-foundation-models-dynamic-profiles-multi-agent-2026/) cover the surrounding landscape; Laya is a different shape of tool from either.

## Verdict: a legitimate offline runtime with an overstated headline

Run it. The port is Apache-2.0, it runs offline after one download, it is fast, and the author publishes his own missed 10x target, his own failing paced sweep, CPU-plan attribution showing the Neural Engine was never preferred in the plain export, and 6-bit and 4-bit experiments rejected at the fidelity gate. That level of self-reporting is rare, and it is why the numbers in this article exist to be checked at all.

Then correct the headline before you repeat it. It is not an M4 result. It is not 45 decisions/s in the sense a specification implies. It is roughly 20 decisions/s if you need every decision inside a deadline on an M3 Max, or about 50/s uncapped, at about 5 ms per short question at P50 with a 96-token ceiling on the fast path.

And use it for what the under-pressure benchmark says it is good at: bounded, low-cardinality, order-stable decisions where the option list is short and you control the ordering. Treat it as a recommender, never as permission. The 39% at 128 candidates and the 49.4% answer flip under reordering are not footnotes to the speed claim — they are the operating envelope.

## FAQ

### Does Laya really run on Mac M4 with Core ML offline?

Core ML offline: yes, verified — weights download once and inference needs no network and no PyTorch, MLX or Transformers. Mac M4: no. Every headline measurement in `mizorewww/laya-coreml` is an M3 Max with a 40-core GPU, 128 GiB and macOS 27.2, and no M4 benchmark exists in the repository. The M4 label traces to the title of a four-command install gist, which publishes no timing data at all.

### Is 45 decisions per second a real number?

It is a real measurement rounded into a misleading shape. The port sustains 49.1–50.0/s pooled at 49.66/s across 1,800 decisions in an uncapped Snake loop on M3 Max. Separately, when asked to hit 50/s, it observed 44.21/s and missed 53.33% of active deadlines. The highest requested rate that passed the deadline test was 20/s, observing 18.4/s with 0.67% misses. So 45 sits between an uncapped average and a rate you can build on.

### How fast is a single decision, and how much energy does it use?

One short multilingual decision runs 4.98 ms P50 / 5.31 ms P95 on ANE FP16, or 4.88 / 5.23 ms with W8 compression, across 65,598 stable calls. Against the port's compiled MLX FP16 baseline that is 1.39x faster and 2.78x better on whole-system energy per decision — 0.1540 J versus 0.4288 J. The author asked for 10x and published 1.39x; energy figures are whole-system estimates with sensor and background-load uncertainty.

### Is Laya as accurate as Jev?

No, and the gap widens as the problem gets harder. At 128 candidates Jev scores 60% and Laya 39%, against a 0.8% chance baseline. Laya loses −0.073 accuracy per doubling of the option list versus Jev's −0.043, flips its answer on 49.4% of decisions when option order is shuffled versus 14.6%, and loses −0.351 accuracy when distractors become plausible versus −0.105. With option order fixed, both are stable at 0.0% — so pin your ordering.

### What are the real limits of the offline claim?

Three. The ANE bundle is capped at 96 tokens total covering question, options and state, so long-context decisions fall back to CPU+GPU — where a plain Core ML export is actually slower than MLX at 11.28 ms versus 7.87 ms P50. Core ML model construction takes 3.4–4.2 s with a 313–475 ms first prediction before warmup. And the shipped `choice:11+` temperature of 0.1006 is clamped to 0.5–5.0 precisely because it would have reported a coin flip as near-certainty, so calibrate before you trust the confidence value.

## Sources and verification notes

Every figure above is traceable to primary artifacts checked on 2026-09-28: `mizorewww/laya-coreml` (`docs/SNAKE_BENCHMARKS.md`, `docs/ANE_BENCHMARKS.md`, `BENCHMARKS.md`, `README.md`), the fordnox gist `e592d0f68b543fd044be8e6d040863a0` and its 178-point Hacker News thread (item 49777106), `gazelle93/decision-models-under-pressure`, `afshinm/laya-mps`, the `astgl.com` production deployment writeup of 2026-09-22, Privatemode's counter-argument of 2026-09-24, and the Hugging Face API for `convaiinnovations/laya`.

Three figures are weaker and are labelled as such in place. The 10.4x speedup over Jev comes from the Laya project's own comparison table against TypeSafe's published numbers rather than a controlled head-to-head. The iPhone 15 Pro ~40 ms report is an unverified third-party comment, not a benchmark. The M5 Max versus M4 Pro cross-backend comparison circulating in the wild is a two-form-factor comparison, so thermal headroom confounds it. The energy measurements are whole-system estimates derived from SMC PSTR power sampling, so their direction is more reliable than their precision.

The M4 claim is recorded here as not verifiable, not as false. Absence of an M4 benchmark in one repository is not evidence the code fails on M4 — it is evidence that no one has published the number the headline implies.
