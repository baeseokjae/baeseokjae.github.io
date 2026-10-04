---
title: 'LLM Model Degradation: A Postmortem of Degraded Performance Across Multiple Models'
date: 2026-10-01T03:02:30+00:00
tags:
  - LLM model degradation
  - LLM degraded performance
  - LLM outage postmortem
  - model degradation postmortem
  - silent LLM degradation
  - LLM quality regression detection
  - canary eval LLM
  - LLM drift detection 2026
  - LLM incident response guide
  - status page degraded performance meaning
  - TTFT p95 monitoring LLM
  - LLM semantic observability
  - useful uptime LLM API
  - LLM postmortem template
  - LLM semantic observability checklist
description: "LLM model degradation means HTTP 200 with worse answers. Vendor postmortems from Anthropic, OpenAI and Azure show how to detect it across multiple models."
draft: false
cover:
  image: "/images/degraded-performance-multiple-models-postmortem.png"
  alt: "Degraded Performance for Multiple Models: An Outage Postmortem"
  relative: false
schema: "schema-degraded-performance-multiple-models-postmortem"
---

LLM model degradation is a slow, quiet loss of answer quality or speed that leaves every health check green: requests still return HTTP 200, error rates stay flat, and latency may not move at all. The 2025–2026 vendor postmortems show it is usually caused by infrastructure or configuration bugs — not by demand, time of day, or server load — and it is diagnosed by semantic monitoring, not uptime dashboards.

## What Does "Degraded Performance" Actually Mean for an LLM?

When OpenAI's status page says "Degraded performance," it is describing a service that answers requests but does so below its normal standard — partial errors, elevated latency, or outputs that are technically valid but wrong. That category now dominates the incident record. Aggregated status history from status.openai.com shows 112 OpenAI outages since January 27, 2026, and the overwhelming majority are degraded-performance events rather than full outages ([Pingoru OpenAI outage history](https://pingoru.io/providers/openai/outage-history)).

That reframing matters for anyone writing a postmortem, because the standard uptime number measures almost nothing about the experience your users had:

| Instrument | What it measures | Why it misses degradation |
|---|---|---|
| Uptime % (status page) | Did the endpoint respond at all | A wrong-but-valid answer counts as 100% up |
| Mean latency | Average response time | Hides tail latency — p99 can sit at 12s while the mean looks healthy ([MLflow](https://mlflow.org/articles/managing-ai-model-serving-latency-a-developers-guide)) |
| Error rate (5xx) | Hard failures | Silent bugs return 200, so the numerator never moves |
| Token velocity (tokens/sec) | Generation throughput | Detects slowness, not semantic corruption |
| Canary eval score | Answer correctness on a fixed panel | The only instrument that sees quality, not plumbing |

The practical definition to carry into a postmortem is "useful uptime": the fraction of requests that produced a correct, complete answer inside your latency bar. A model can post 99.98% API uptime and a terrible useful-uptime week at the same time, which is exactly what happened during OpenAI's May 2026 events.

## The Postmortem Evidence Base: What Vendors Have Admitted (2025–2026)

The most useful reliability syllabus available today is free: the vendors publish it themselves. Anthropic, OpenAI and Microsoft have all documented multi-model degradation in enough detail to extract reusable lessons.

| Vendor / event | Window | Root cause | Detection latency |
|---|---|---|---|
| Anthropic: three-bug cascade | Aug 5 – Sep 18, 2025 | Routing error, TPU misconfiguration, XLA:TPU miscompilation | Weeks to diagnose |
| Anthropic: Opus 4.7 coding quality | Mar 4 – Apr 10, 2026 | Reasoning effort silently lowered; prompt-cache bug | ~5 weeks to revert/fix |
| OpenAI: GPT-5.5 in Codex | ~May 13–16, 2026 | Two bugs degrading capability | ~48 hours to acknowledgement, fixed next day |
| OpenAI: GPT-5.5 performance degradation | May 15–17, 2026 | Degraded performance across API surfaces | ~32-hour window |
| OpenAI: API/ChatGPT/Codex | July 25, 2026 | Simultaneous multi-component failure | 1h 51m to restore, 17 consecutive abnormal days |
| Azure AI Foundry: gpt-5-mini tokens/sec | Apr 2026 | Shared-capacity queueing, regional demand, concurrency | Customer-reported, no dashboard incident |

Notice the shape of these incidents: they are not single-model events. Azure's gpt-5-mini slowdown, OpenAI's simultaneous API/ChatGPT/Codex failure across 31 components, and Anthropic's overlapping bugs all degraded *multiple models and surfaces at once*, which is why triage-by-symptom ("the model got dumber") is so unproductive.

## Case Study 1 — Anthropic's Three-Bug Cascade (August–September 2025)

Anthropic's official postmortem, ["A postmortem of three recent issues"](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues) (2025-09-17), remains the single best-documented case of silent multi-model degradation, because three independent bugs landed inside a three-week window and overlapped.

Bug 1 — context-window routing error. Introduced August 5, 2025, it initially affected roughly 0.8% of Sonnet 4 requests: some traffic was routed to a server type that mishandled the context window. Sticky routing made follow-up turns likely to hit the same bad server, so a single bad first request poisoned the rest of the conversation. By the worst hour on August 31, 16% of Sonnet 4 requests were affected, and about 30% of Claude Code users in that period had at least one message routed incorrectly. Bedrock peaked at 0.18%; Vertex AI stayed under 0.0004% between August 27 and September 16. Routing logic was corrected September 4, but rollout to Bedrock lagged until September 18.

Bug 2 — output corruption. A misconfiguration deployed to Claude API TPU servers on August 25 caused wrong tokens: Thai and Chinese characters appearing inside English answers, plus obvious syntax errors. Opus 4.1 and Opus 4 were hit August 25–28; Sonnet 4 was hit August 25 through September 2. Third-party platforms were unaffected.

Bug 3 — approximate top-k XLA:TPU miscompilation. An August 25 code change to token selection triggered a latent compiler bug, confirmed to affect Haiku 3.5 and believed to touch a subset of Sonnet 4 and Opus 3.

No server-side error fired for any of the three. That is the defining property of this failure class, and it is why the diagnosis took weeks. A load-balancing change on August 29 — after the bugs had landed — increased affected traffic, so some users saw failures while others saw normal performance. To the incident channel, that looked like ordinary feedback variation rather than a regression trend.

Anthropic's postmortem also carries the vendor denial worth quoting verbatim, because it draws the line that all of your detection design depends on: "We never reduce model quality due to demand, time of day, or server load. The problems our users reported were due to infrastructure bugs alone."

## Case Study 2 — The 2026 Degradation Wave (GPT-5.5, Opus 4.7, 112 OpenAI Incidents)

The 2026 record shows the pattern accelerating. OpenAI's May 15–16 event, labelled "GPT5.5 Performance Degradation," opened with an investigating status at 16:11 UTC on May 15 and was not resolved until May 17 — roughly a 32-hour degraded window on a single flagship model ([status.openai.com via Pingoru](https://pingoru.io/providers/openai/outage-history)). Days later, on May 19–20, both GPT-5.4 and GPT-5.5 showed elevated errors with Chat Completions and Responses marked "Degraded performance," detected and mitigated within about an hour and resolved to Operational by 00:37 UTC.

The human side of that incident is instructive for detection latency. OpenAI Codex lead Thibault Sottiaux acknowledged on May 15, 2026 that two bugs had degraded GPT-5.5 capability in Codex across roughly 48 hours, then confirmed the fix the next day — acknowledgement to closure inside 24 hours. Compare that with Anthropic's overlapping bugs, which took weeks to even diagnose.

Anthropic's own April 23, 2026 postmortem went further and admitted three product-layer changes that degraded Opus 4.7 coding quality: reasoning effort was silently lowered from high to medium on March 4 (reverted April 7), and a March 26 prompt-caching optimisation wiped prior thinking on every turn after an idle session instead of once (fixed April 10). This is degradation caused by the vendor's own product decisions, not by infrastructure failure — a category that no external monitoring can infer from the outside, and one that only shows up as "the model feels worse at this task."

The scale of the July 2026 wave puts the trend in perspective: on July 25, 2026, OpenAI's API, ChatGPT and Codex failed simultaneously across 31 service components and took 1 hour 51 minutes to fully restore. Third-party monitoring showed OpenAI had no fully normal day for 17 consecutive days — two major outages plus a run of degraded-performance and partial-outage days ([36Kr English](https://www.36kr.com/en), 2026-07).

## The Silent-Failure Class — HTTP 200, Broken Output

The FailureAtlas paper (arXiv 2607.17525, 2026-07-20) formalises what every operator has suspected: the most operationally severe failures in multi-provider LLM serving are silent. They return HTTP 200, pass every standard health check, and corrupt application state. Detecting them requires semantic-level observability, not latency, error-rate or pod-health monitoring.

The paper's first-hand examples are worth internalising:

- A concurrency race in conversation-state management. Two coroutines read history, append a turn, and write back; the second write silently overwrites the first. Turns vanish from the context window and generation quality degrades — with every request still returning HTTP 200 and no metric registering an anomaly. It was found only because a semantic continuity benchmark showed persona-adherence dropping under high concurrency.
- A streaming index collision that corrupts tool-call payloads while the stream completes normally.
- A retry storm in which 100 parallel agents retried on a fixed interval, synchronised into a thundering herd that saturated the provider's rate limit on every retry window, turning a momentary 502 into permanent failure for 25% of requests.

The paper also records a genuinely uncomfortable negative finding: the authors could not find a single evidence-grade, reproducible bug report of an infrastructure-level failure in model behaviour — which they describe as "a legitimate finding, not a gap in our survey." Most "the model got dumber" claims are therefore unproven, and a postmortem that asserts a model regression must bring evidence.

Industry telemetry reinforces how common the silent class is:

| Statistic | Source |
|---|---|
| 91% of production LLMs experience silent behavioural drift within 90 days of deployment | InsightFinder, via datarekha.com, "Model monitoring in 2026" |
| A support agent returned wrong answers on ~1 in 14 requests for nine days with every infrastructure dashboard green; ~$97/day in token burn plus downstream cost | Prefactor, "Canary evaluation for production AI agents" |
| 22 incidents over eight weeks in a production LLM agent runtime (8 providers, ~40 scheduled jobs, 4,286 unit tests, 827 governance checks) all had a silent phase; the meta-pattern of an error signal never reaching a human in actionable form appeared at least 28 times | arXiv 2606.14589, "When Errors Become Narratives", 2026-06-12 |
| 23% variance in GPT-4 response length across rolling 2,250-response samples; 31% instruction-following inconsistency for Mixtral | structured-prompt-drift study, via datarekha.com, 2025 |

## A Reusable Postmortem Taxonomy (Origin Layer × Loud/Silent)

Before writing the narrative, classify the incident. FailureAtlas proposes two axes — origin layer and detectability — and the grid tells you which instrument would have caught it.

| Origin layer | Typical loud symptom | Typical silent symptom | Instrument that catches the silent case |
|---|---|---|---|
| Network / Transport | Connection resets, 502/504 storms | Elevated p95 TTFT with 200s | TTFT percentile SLO + queue depth |
| Streaming / Protocol | Truncated streams, disconnects | Corrupted tool-call payloads, index collisions | Schema validation on streamed tool calls |
| State / Session | 409 conflicts, lost sessions | Turns silently overwritten, context shrink | Semantic continuity + persona-adherence benchmarks |
| Model Behaviour | Wrong model id, obvious gibberish | Subtly worse answers, lower reasoning effort | Canary eval panel vs. rolling baseline |
| Governance / Cost | Budget breach alerts | Silent scope drift, retry-storm cost amplification | Cost velocity + scope allowlist at the gateway |

Two design consequences follow from the grid. First, every cell in the "silent" column needs at least one instrument, and most teams have none. Second, FailureAtlas notes that governance and control-plane mechanisms are designed and tested against the happy path, so they are most likely to malfunction exactly when the upstream provider is degraded worst — meaning your circuit breakers and failover logic are also incident candidates.

## Timeline Reconstruction — Pin the Harness, Not Just the Model

The hardest part of a multi-model degradation postmortem is the timeline, and it fails for a mundane reason: the harness drifts. If your CLI version, system prompt, sampling parameters, or model ID change between the "before" and "after" windows, a changed harness looks exactly like a changed model, and the incident review turns into an argument instead of a fix.

Pin these alongside the model version in every evaluation run:

- Model ID *and* the provider-side version string where available, plus region and service tier.
- System-prompt hash and tool-schema hash — Anthropic's March 2026 caching bug shows that prompt handling itself can change behaviour silently.
- Sampling parameters: temperature, top-p, max tokens, reasoning-effort setting.
- Client stack: SDK version, CLI version, retry policy, timeout values, concurrency limits.
- Traffic shape: concurrent agents, queue depth, sticky-routing behaviour.

Store the pinned manifest with every canary result. When someone claims "the model got worse on the 14th," the first artefact you produce is the diff of that manifest — and in practice a meaningful share of regression reports end there, as harness noise rather than model behaviour.

## Detection Layer 1 — Canary Evals That Separate Regression From Noise

Averages and a handful of bad prompts prove nothing. Real regression detection needs a frozen question panel, paired per-item statistics, a control arm, and pre-registered decision rules.

The statistical trap is power. A canary that scores a model against itself screened 2,336 GPQA Diamond / MMLU-Pro / competition-math / AIME questions with 4 samples each; about 93% were answered correctly first try, and 97% of questions turned out to be always-right or always-wrong — leaving only 78 "sometimes right" questions with the statistical power to detect a real regression ([livenerf methodology via DEV Community](https://dev.to), 2026). Those 78 items are the entire instrument. A panel drawn from questions the model always gets right will report a flat score right through a genuine degradation.

Operational alert tiers that teams actually run:

| Canary signal | Threshold | Action |
|---|---|---|
| Score drop vs. rolling 7-day baseline | 2–3% | Investigate |
| Score drop | ≥5% | Priority alert |
| Score drop across two consecutive runs | ≥10% | Circuit breaker / rollback |
| Provider p95 TTFT | >3s | Warning — degraded performance |
| Error rate | >5% | Warning |
| Error rate | >20% | Critical page |
| 503/504 on 3+ consecutive checks | — | Switch to backup provider |
| Rate-limit utilisation | >70% | Warning |

The 2%/5% thresholds are attributed to Lloyds Banking Group practice in Prefactor's canary-eval writeup ([Prefactor](https://prefactor.com/)). The latency and error thresholds come from practitioner monitoring guides ([APIStatusCheck](https://apistatuscheck.com/blog/llm-api-monitoring-guide)). Pair the eval panel with a control arm — a frozen older model version or a self-hosted model — so you can distinguish "our provider degraded" from "our pipeline degraded."

## Detection Layer 2 — Latency Metrics That Actually Move (TTFT, p99, Queue Depth)

Tail latency is what users experience. "If you are only watching mean response time, you are watching the wrong number" is the correct framing from MLflow's serving-latency guide — average latency can look healthy while p99 sits at 12 seconds.

Three metrics do the heavy lifting:

1. Time to First Token (TTFT), as its own dashboard. A model that streams fast but takes three seconds to start feels broken even with excellent throughput. A sudden spike in p95 TTFT is often the first signal of upstream provider degradation, arriving before a full outage.
2. Queue depth, as a leading indicator. By the time utilisation crosses a threshold, the queue has already grown and p99 has already spiked. That is precisely the mechanism Microsoft cited in the April 2026 Azure AI Foundry case, where gpt-5-mini tokens/second degraded until the same job took 90–120 seconds instead of a 60-second worst case, while a newer model completed it in under 20 seconds. Microsoft attributed this to shared-capacity queueing, regional demand and concurrency ([Microsoft Q&A, Azure AI Foundry](https://learn.microsoft.com/en-us/answers/), 2026-04-24).
3. Cold-start decomposition. Model-weight loading, LoRA adapter initialisation, KV-cache allocation and container startup each need separate instrumentation, otherwise a cold-start regression masquerades as model slowness.

Two practical notes from the same body of work: the model is rarely the bottleneck — teams optimise inference time and then discover CPU preprocessing and tokenisation add more latency than the GPU step they just fixed — and tracing should use tail-based sampling, capturing 100% of requests above p99 and 100% of errors while sampling routine fast requests at 1–5%.

## Detection Layer 3 — Span-Attached Quality Scores and Drift Dashboards

Latency tells you a request was slow. It says nothing about whether the answer was right. The third detection layer attaches a quality score to the span that produced the output, so a dashboard can show semantic drift and latency side by side.

The pattern that works in production: run a small scored rubric (or an LLM-as-judge with a frozen prompt) on a sampled subset of live responses, attach the score as an attribute on the existing trace span, and alert on the rolling baseline rather than on absolute values. This is what would have caught the Prefactor case — a support agent returning wrong answers on roughly 1 in 14 requests for nine days while every infrastructure dashboard stayed green, at a cost of about $97/day in token burn plus the downstream cost of incorrect actions. Root cause: the team was monitoring health checks, not behavioural drift.

Pair the quality score with an explicit drift detector. The May 18, 2026 Azure Q&A thread documenting sudden latency increases with no customer-side change and consistent token volume is the canonical ambiguous case: analysis attributed it to a silent backend change — model version update, infrastructure rebalancing, or increased shared-tenant load — with no official incident on the health dashboard ([Microsoft Q&A, "Degraded Performance since May 18th 2026"](https://learn.microsoft.com/en-us/answers/)). When the vendor's dashboard is silent and your metrics move, span-level quality data is the only evidence you will have.

## Triaging Provider Degradation — Status Pages, Circuit Breakers, Retry Storms

Once you believe the provider is degraded, triage order matters, and OpenAI's own troubleshooting guidance is the right starting point ([OpenAI Help: troubleshooting API errors and latency](https://help.openai.com/en/articles/1000499-troubleshooting-api-errors-and-latency)):

- Filter before investigating. Always filter to a single model, a single service tier, and the affected project. Selecting multiple models aggregates rather than switches, so issues on a low-traffic model get hidden by high-volume traffic, and high-volume models make localised issues look global.
- Use the HTTP Requests view, not the Uptime tab, and read error *rates* rather than raw counts. If client-side errors appear with no corresponding service-health data, the requests likely never reached the provider — the fault is upstream, in timeouts, proxies or networking.
- Use percentiles, not averages, and prefer priority/scale tiers that carry defined SLAs, since the standard tier has no guaranteed latency. Track token velocity (tokens/sec, independent of prompt size) and request time.

Then bound the blast radius — and understand that naive retries are part of the blast radius. FailureAtlas's retry storm is the cautionary example: 100 parallel agents retrying on a fixed interval synchronised into a thundering herd that saturated the rate limit on every retry window, converting a momentary 502 into permanent failure for a quarter of requests. Mitigations that actually help:

| Control | Why it works |
|---|---|
| Jittered exponential backoff with a retry budget | Breaks synchronisation; caps total amplification |
| Circuit breaker at the gateway (not in agent code) | Stops the herd even when the agent keeps asking |
| Provider-level failover with a control-arm eval | Fails over on measured quality, not on a hunch |
| Per-provider rate-limit headroom ≥30% | Rate-limit utilisation above 70% is a warning sign |
| Sticky-routing awareness | Anthropic's bug shows bad routing follows a conversation |

One more triage note specific to multi-model incidents: check whether the degradation is model-specific or gateway-wide before escalating. Azure's shared-capacity queueing, regional demand and concurrency can slow one model while another completes the same job in a fraction of the time — the fix there is routing, not a vendor escalation.

## How Do You Write the Postmortem? Blameless Template and Action Items

The postmortem is a document with a job to do: change the system so the next silent degradation is caught in hours instead of weeks. A structure that survives review:

1. Summary — one paragraph, plain language: what degraded, for which models, for how long, and what users experienced.
2. Impact quantified in useful uptime — requests affected, percentage, tail latency, error rate, and the cost of incorrect downstream actions.
3. Timeline with timestamps in UTC — introduction, first user-visible symptom, first internal signal, diagnosis, mitigation, full resolution. Include the *detection latency* as its own line; it is the metric the action items must move.
4. Origin-layer classification — use the taxonomy table above, and state whether the failure was loud or silent.
5. Harness manifest — model ID, prompt hash, sampling params, client versions, concurrency, so the "was it the model or us?" question is answered by artefacts.
6. Contributing factors — overlapping bugs, load-balancing changes that amplified exposure, contradictory user reports that looked like ordinary variation.
7. What went well and what didn't — including honest gaps: which silent-cell instrument was missing.
8. Action items with owners and dates, each tied to a detection layer: canary panel items added, TTFT percentile SLO defined, span-attached quality score shipped, retry jitter deployed, circuit breaker moved out of agent code.
9. Open questions — including anything the vendor has not explained. Anthropic's postmortem is a model here for what it discloses; the harder lesson is noticing what a vendor postmortem leaves out, such as exact affected-request percentages for third-party platforms.

Keep it blameless in the specific sense that matters: blame lands on missing instrumentation, not on the engineer who noticed the answers looked worse.

## SLOs and a Pre-Flight Checklist for Model Degradation

Pre-registered SLOs are what turn a postmortem from a story into a control loop. Before the next incident, define and instrument:

| SLO | Suggested target | Detection layer |
|---|---|---|
| Useful uptime (correct answer within latency bar) | ≥99% per model per day | Canary eval |
| p95 TTFT per model | <3s warning, <5s page | Latency |
| p99 end-to-end latency | <12s (the number users actually feel) | Latency |
| Quality score vs. 7-day rolling baseline | <2% drift | Span-attached scoring |
| Retry-budget consumption | <20% of daily budget | Governance |
| Rate-limit utilisation | <70% | Governance |
| Detection latency | <4h from first symptom to acknowledgement | Process |

The last row is the one most teams omit and the one that separates OpenAI's 24-hour Codex closure from Anthropic's multi-week diagnosis. Detection latency is a process SLO, and it is the only one that improves the others.

## FAQ

### What does "degraded performance" mean on an LLM provider's status page?

It means requests are completing but below normal standard — partial errors, elevated latency, or unusable output. It is deliberately distinct from a full outage, and it covers most of the incident record: status.openai.com shows 112 outages since January 27, 2026, dominated by degraded-performance events rather than clean outages. Your uptime percentage will not move during one of these windows.

### Does an LLM provider throttle model quality during peak demand?

No — and the vendors have stated it explicitly. Anthropic's postmortem says: "We never reduce model quality due to demand, time of day, or server load. The problems our users reported were due to infrastructure bugs alone." Azure's gpt-5-mini slowdown was attributed to shared-capacity queueing, regional demand and concurrency rather than intentional throttling. The practical implication is that degradation is usually a bug to be diagnosed, not a load pattern to schedule around.

### How do I tell whether the model degraded or my own harness changed?

Pin a manifest with every eval run: model ID and provider version string, system-prompt hash, tool-schema hash, sampling parameters, SDK/CLI versions, retry policy and concurrency. Then diff the manifest across the two windows before diffing model outputs. A changed harness looks exactly like a changed model, so the manifest diff is the first artefact you should produce.

### How many test questions do I need to detect a real quality regression?

More than intuition suggests, and the questions must be discriminating. One published canary screened 2,336 questions with 4 samples each; 97% turned out to be always-right or always-wrong, leaving only 78 "sometimes right" items with the statistical power to detect a regression. Build the panel from items with observed variance, use paired per-item statistics, run a control arm, and pre-register the decision thresholds (commonly 2–3% to investigate, 5% to alert, 10% across two runs to roll back).

### What is the fastest way to limit damage while multiple models are degraded?

Stop amplification, then route around it. Use jittered exponential backoff with a hard retry budget, keep circuit breakers at the gateway rather than inside agent code, cap concurrency, and fail over on measured quality rather than on latency alone. The documented failure mode to avoid is the retry storm: 100 agents retrying on a fixed interval synchronised into a thundering herd that saturated the provider's rate limit and turned a momentary 502 into permanent failure for 25% of requests.
