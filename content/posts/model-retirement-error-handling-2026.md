---
title: "Model Retirement Errors: Why 'Model Not Found' Is Permanent and Your Retry Loop Cannot Tell"
date: 2026-11-01T00:00:00+00:00
lastmod: 2026-11-25 00:00:00+00:00
tags:
  - "model retirement error"
  - "model not found 404"
  - "llm deprecation handling"
  - "retry loop 404"
  - "agent pipeline model retired"
  - "anthropic not_found_error"
  - "ollama model not found"
  - "gemini deprecation shutdown date"
  - "model unavailable classifier"
  - "retry policy comparison"
description: "None of the three providers checked publishes a retirement-specific error body: Anthropic's documented 404 is a generic not_found_error, Ollama says 'model not found' for typos and deleted tags alike, and Google publishes dates but no body. A frozen six-row fixture shows why a retry loop cannot tell permanence from a typo, and a two-policy replay measures the cost."
draft: false
schema: "schema-model-retirement-error-handling-2026"
cover:
  alt: "Diagram in two panels. Panel 1: an HTTP 404 not_found_error response and Ollama's 'model not found' string classify as model_unavailable, marked stop, with the note that the same bytes cover a retired ID and a typo; HTTP 429 classifies as rate_limit, and HTTP 500, 502, 503, 504 and 529 classify as transient, both marked retry. Panel 2: bar chart from the frozen fixture showing retry_all spending 3 server requests on both model_unavailable and transient rows, against 1 and 3 for no_retry_4xx."
  image: /images/model-retirement-error-handling-2026.png
  relative: false
---

An agent pipeline pins a model identifier and the provider retires it. From that moment every call fails with an error envelope that looks exactly like a typo: a plain HTTP 404 whose message names the request, not the lifecycle. The pipeline retries with backoff, spends its budget on a request that can never succeed, and fails the task with "provider error". The fix is not a better error message — none of the three providers checked publishes one. It is to stop reading permanence out of the body, decide it from a pinned-ID record plus a published shutdown date, and prove before the next retirement that the retry policy actually stops.

## What the absent-model envelope contains, per provider

Three providers were checked against their own documentation on 2026-11-01. None of them publishes a response body that says a model was retired.

| Provider | Documented status and type | Documented text | Names retirement? |
| --- | --- | --- | --- |
| Anthropic | 404 `not_found_error` | "The requested resource was not found. Check the endpoint path and any resource IDs in the request URL." | No |
| Ollama (local server) | 404, `error` string | `model '<name>' not found` | No |
| Google Gemini | not documented as a response at all | shutdown is "completely turned off, and the endpoint is no longer available" | No body published |

The Anthropic row is quoted from the Messages API error reference at [https://platform.claude.com/docs/en/api/errors](https://platform.claude.com/docs/en/api/errors): a 404 for a missing resource is the generic `not_found_error`, and the documented remedy is to check the endpoint path and any resource IDs in the request URL — advice that points away from a lifecycle diagnosis. The table quotes the page's 404 bullet; the replayed envelope below is the page's example response body for the same error (`{"type":"error","error":{"type":"not_found_error","message":"The requested resource could not be found."}}` with a `request_id`), so the two strings differ even though both come from that one page. The Ollama row is quoted from the vendor's own HTTP handler in [https://raw.githubusercontent.com/ollama/ollama/main/server/routes.go](https://raw.githubusercontent.com/ollama/ollama/main/server/routes.go), which returns `http.StatusNotFound` with `fmt.Sprintf("model '%s' not found", req.Model)`; the same file returns `"model %q not found, try pulling it first"` on another path. Both strings are produced for a typo, an unpulled tag and a deleted tag without distinction. The Google row comes from [https://ai.google.dev/gemini-api/docs/deprecations](https://ai.google.dev/gemini-api/docs/deprecations), which states that a shut-down model is "completely turned off, and the endpoint is no longer available" and tabulates shutdown dates per model, but publishes no status code, error type or body for a call that hits one.

A fourth provider, OpenAI, was attempted and is reported as an access limitation rather than as absence: its error-codes page returned content but no `model_not_found` section to extraction, so nothing from it is quoted here. The absence of a published retirement body is a finding about the pages that were checked on 2026-11-01, not a proof about every API surface.

For local servers the case is even plainer. Ollama's API documentation notes that the API "isn't strictly versioned" and that "deprecations are rare and will be announced in the release notes" ([https://docs.ollama.com/api](https://docs.ollama.com/api)). A missing tag there is an operator event — a deleted model, a pulled-later tag, a typo — not a provider announcement, and the server has no scheduled retirement mechanism to announce.

## Three causes, one byte-identical body

The practical consequence is that the envelope cannot separate the causes. In the frozen fixture behind this article, the row labelled "retired model" and the row labelled "bad endpoint path" are byte-identical: both are HTTP 404 with `error.type = not_found_error`, and the two bodies hash to the same SHA-256, `449f8c0d7617…`. The third row, Ollama's missing tag, differs only because the provider returns an untyped string instead of a typed object.

That single fact decides the design. A classifier that reads only the body can answer "is this model permanently unavailable, or is it transient?" It cannot answer "retired, or typo?" — and any tool that claims to is labelling a cause it did not observe. The per-row body hashes and the classifier's decision field for each row are in [classification.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/out/classification.csv), one row per fixture; the raw run record carrying the same array is [results.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/out/results.json). The retry CSV linked below has the request counts, not those fields.

## Where permanence actually lives

Permanence has two components, and neither is in the response.

The first is the pipeline's own record: the exact identifier that was pinned, when it was pinned, and whether anything deployed since then changed it. A dated ID such as `qwen3:8b-2026-05` or a hosted alias is an input to the diagnosis, not a derived fact.

The second is a provider-published shutdown date, and two of the three providers checked publish one. Google's deprecations page lists a shutdown date per model and marks already-shutdown models, with the caution that the listed dates "indicate the earliest possible dates on which a model might be retired". Anthropic's deprecations page is the more explicit calendar ([https://platform.claude.com/docs/en/about-claude/model-deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations), re-checked 2026-11-25): it defines "Retired: The model is no longer available for use. Requests to retired models fail.", carries per-model tables with the columns Retirement date, Deprecated model and Recommended replacement — for example November 30, 2026 for `claude-sonnet-4-5-20250929` against `claude-sonnet-5-5`, and August 5, 2026 for the already-retired `claude-opus-4-1-20250805` — and promises that impacted customers "will always be notified by email and in the documentation", with at least 60 days' notice for publicly released models. It also scopes itself: the dates cover Anthropic-operated platforms, while Amazon Bedrock and Google-managed Claude "set their own retirement schedules", so the same model can carry a different date on a partner platform. And even these dates are floors in places — `claude-haiku-4-5-20251001` is listed as Active with its retirement-date cell reading "Not sooner than October 15, 2026" — so an automated check compares a date, never a status label. Ollama publishes no calendar at all: its API documentation says only that "deprecations are rare and will be announced in the release notes". What none of the three publishes is the other half — a response body for a call to a retired model; Anthropic says such requests fail and documents the generic 404 instead, which is exactly what the fixture replays. That is why the confirm step in the fixture is written as a recorded human/registry lookup against a published date rather than an API call.

The combined rule is therefore: an envelope classifies the request as permanently unavailable, and the pinned ID plus a shutdown date confirms that the cause is retirement. Neither half is sufficient alone, and the article says so rather than inferring retirement from a 404.

## What the retry policy does with each class

The retry question is measurable, and the answer depends entirely on which policy is running. Two policies were replayed against the same six frozen envelopes over an in-process mock server on 2026-11-19T08:45:56Z–08:46:02Z (the same script and envelope set as the 2026-11-01 measurement, re-executed after the label timestamp was corrected). `retry_all` retries any non-success; `no_retry_4xx` retries only 408, 409, 429 and 5xx, with a three-attempt cap and 200 ms doubling backoff.

| Policy | Requests for a model-unavailable row | Requests for a transient row | Distinguishes them? |
| --- | --- | --- | --- |
| `retry_all` | 3 | 3 | No |
| `no_retry_4xx` | 1 | 3 | Yes |

Request counts are the server-side counts, not the client's intentions, and the two policies produce identical counts on the absence row and the transient row under `retry_all` — which is the amplification the article is about. The fixture also carries a 429 control row that the classifier puts in its own `rate_limit` class, and both policies retry it: that is correct for a throttle, and it is why the absence cell in the table is measured only against 404s. Under `no_retry_4xx` the permanent 404 costs one request and the transient 503 still gets its three attempts, with wall times in the 600 ms range for the retried cells and effectively zero for the single-attempt cells. That is not a latency benchmark; the backoff is fixed at 200 ms doubling and the server is local, so the timings only show that the retry arms actually waited.

Read the table as a policy statement, not a provider one: the separation comes from the HTTP status, which is 404 for both classes of absence. It tells you "do not retry this" — it does not tell you "this model was retired". Pipelines that retry every error, including the many built on generic HTTP clients with naive backoff, convert a permanent condition into three paid requests and a slower failure.

## A fixture you can freeze before the next retirement

The fixture is six envelopes: three verbatim from vendor documentation or vendor source, three synthesised to spec as control rows and excluded from the verbatim figures. The label file declares the time it was written and ships with its own hash, and the harness recomputes that hash and derives the ordering against the run start from the declared timestamp instead of asserting it — so a relabel after the fact is visible in the record rather than invisible in a claim.

The whole check is one directory and runs offline, standard library only, with no keys and no network access:

```
cd research/evidence/model-retirement-error-handling-2026/reproduction
python3 compare.py
```

- Layout, provenance and scope: [README.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/README.md)
- Two-policy comparison harness, starts its own loopback server: [compare.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/compare.py)
- Frozen labels and their hash, written before the run: [labels.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/labels.json) and [labels.sha256](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/labels.sha256)
- The six envelopes, each carrying `verification` and `source_url`: [envelopes/](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/envelopes/anthropic_retired_model.json)
- Per-row classification (label, prediction, decision field, body sha256): [out/classification.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/out/classification.csv)
- Per-cell results (fixture, policy, class, server requests, client attempts, wall time, final status): [out/retry-policy-compare.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/out/retry-policy-compare.csv)
- Full run record with server timestamps and isolation notes: [out/results.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/out/results.json)
- Relocation and re-execution record for this layout, 2026-11-25: [verification-2026-11-25.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/model-retirement-error-handling-2026/reproduction/verification-2026-11-25.json)

The figures in this article come from the 2026-11-01 and 2026-11-19 runs, whose records stay as written in the same evidence directory. The layout was consolidated under `reproduction/` on 2026-11-25 and the same script re-executed from its new paths: identical envelopes by hash, 3 of 3 verbatim rows and 6 of 6 rows correct under the two in-scope classes, 3 and 3 requests under `retry_all`, 1 and 3 under `no_retry_4xx`. That is a layout check recorded in `verification-2026-11-25.json`, not a new measurement window, and it does not change any date reported above.

To reuse it, replace the envelopes with your own provider's documented bodies, keep the label file separate and hash it, and run the comparison before the next deprecation window rather than during it. The one rule worth copying is the label vocabulary: `model_unavailable` versus `transient`, not `retired` versus `typo`. The former is observable from the envelope; the latter is a cause you will get wrong exactly when it matters.

## Limits

Six rows is a small fixture, and only three of them are verbatim; the synthesised control rows are labelled as such and are never counted in the verbatim figures. Classification scored 3 of 3 on the verbatim rows and 6 of 6 across all six under the two in-scope classes, with no `unknown` predictions — but that is a property of a six-row fixture, not an accuracy claim about production traffic. No live provider API was called: no keys were used, no paid requests were made, and nothing here measures real provider latency, cost or error text under load. Wall times reflect a fixed 200 ms doubling backoff against a loopback server.

The demand side is deliberately thin. Nine sampled search impressions across three rows, one of them the retirement-shaped string `the model 'z-ai/glm-5.3' has reached its end of life on 2026-10-28t08:00:00z and is no longer available.` on 2026-10-30 with 5 impressions and 0 clicks, are recorded as an observation that prompted the fixture — an editorial experiment, not evidence of volume. Search-console data for the same property held no query row containing retirement or deprecation language, which is an artefact of top-row coverage rather than proof of zero demand.

Two of the three providers checked publish retirement dates, in two different shapes: Google's page gives one shutdown date per model with an "earliest possible" caution, Anthropic's gives dated per-model tables plus partner-platform caveats, and neither publishes a retirement-specific response body; Ollama publishes no calendar at all. So the confirm-permanence step is a comparison against a published date together with the pipeline's own pinned-ID record — and where no calendar exists, a dated operator note is the honest substitute. A wider sweep would likely find more calendars, and possibly an absent-model body worded differently; nothing here claims otherwise.

## What to do when the classifier fires

Treat `model_unavailable` as a stop signal, not a retry signal: fail the task fast, mark the pinned identifier as blocked, and record the envelope hash. Then confirm the cause from the provider's shutdown page and the pipeline's own ID history, and only then choose a replacement. The migration itself is a different problem — the step-by-step examples live in the [Claude model migration guide](/posts/claude-opus-4-8-to-fable-5-migration-guide-2026/) and the [Assistants API to Responses API migration guide](/posts/openai-assistants-api-migration-responses-api-2026/); the provider whose retirement string appears in the observed search row is covered end to end in the [Z.ai API developer guide](/posts/z-ai-api-developer-guide-2026/), including the pricing and setup detail this article deliberately does not repeat.

For the surrounding containment — how to stop an agent loop from spending after a terminal failure — the [agent cost circuit breaker pattern](/posts/agent-cost-circuit-breaker-pattern-guide-2026/) is the mechanism this classification feeds. For call-site mechanics and error handling at the tool boundary, see the [function calling and tool use guide](/posts/llm-function-calling-tool-use-guide-2026/). Fallback model selection is out of scope here: this is the detection half, which decides when a fallback is even warranted.
