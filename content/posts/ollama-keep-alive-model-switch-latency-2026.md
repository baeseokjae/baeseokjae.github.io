---
title: "Agent Loops That Alternate Local Models: Measuring Ollama keep_alive and Cold-Start Stalls (2026)"
date: 2026-11-08T00:00:00+00:00
description: "Twelve recorded responses on a two-core CPU-only Ollama host: keep_alive=0 reloaded on every switch, keep_alive=5m still evicted when OLLAMA_MAX_LOADED_MODELS=1, and keep_alive=-1 kept both models resident. Includes the load_duration/total_duration diagnostic and the recorded /api/ps residency states."
draft: false
schema: "schema-ollama-keep-alive-model-switch-latency-2026"
tags:
  - ollama keep_alive
  - ollama model switching latency
  - ollama load_duration
  - ollama max loaded models
  - local llm cold start
  - ollama api ps
  - multi model local inference
  - cpu-only llm inference
  - agent model routing
  - ollama eviction
  - local llm troubleshooting
---

Your agent finishes a coding turn, then calls a vision model to read a screenshot, then goes back to the coder. Each hand-off costs a pause the client reports as model latency: eight seconds, fifty seconds, eight seconds. The obvious diagnosis is that the model is slow, the quantization is wrong, or the machine needs more RAM. On the host measured here, none of those explained it. The model was being loaded from disk, again, on every switch, and the HTTP response said so in its own timing fields.

This article is the mechanism, a diagnostic you can run against a single response, and the measured residency behaviour of three `keep_alive` configurations on one CPU-only machine. Every number below comes from responses recorded on 2026-11-06 between 13:24:31Z and 13:33:36Z against Ollama 0.20.3, and the raw records ship with the post so you can recompute them instead of trusting a table.

## The pause that looks like model latency

An Ollama server holds a model in memory for a while after answering, then unloads it. The FAQ states the default window plainly: [models are kept in memory for 5 minutes before being unloaded](https://docs.ollama.com/faq.md). `keep_alive` on `/api/generate` and `/api/chat` overrides that window, and the same page lists four accepted forms: a duration string such as `10m`, a number of seconds, any negative number, which keeps the model loaded, and `0`, which unloads the model immediately after generating a response.

Two models in one loop interact with two separate limits. The first is how long each model stays resident. The second is [OLLAMA_MAX_LOADED_MODELS, "the maximum number of models that can be loaded concurrently provided they fit in available memory", defaulting to 3 for CPU inference](https://docs.ollama.com/faq.md). When the number of models your loop touches exceeds the resident limit, or when the second model does not fit alongside the first, something has to be evicted — and an evicted model is a cold model on its next call, no matter what `keep_alive` says.

That is the trap: `keep_alive=5m` reads like "keep my model warm" and behaves like it only until a second model needs the slot.

## One response contains both phases

`/api/generate` reports its own timing breakdown in nanoseconds, and the field descriptions are specific: [`total_duration` is "time spent generating the response", `load_duration` is "time spent loading the model", `prompt_eval_duration` covers prompt evaluation and `eval_duration` covers token generation](https://docs.ollama.com/api/generate.md). The same page documents [`keep_alive`: "model keep-alive duration (for example 5m or 0 to unload immediately)"](https://docs.ollama.com/api/generate.md).

So one response is enough to classify a slow call. If `load_duration` is a large fraction of `total_duration`, you paid for a load. If it is near zero while the wall clock was still long, the time went somewhere else — a queued request behind another generation, which is a different problem with a different fix (covered in [the concurrency measurement on this site](/posts/ollama-concurrent-requests-latency-2026/)).

The ratio is the diagnostic:

```bash
curl -s http://127.0.0.1:11434/api/generate \
  -d '{"model":"qwen2.5:0.5b","prompt":"Reply with the single word ok.","stream":false}' \
| python3 -c 'import json,sys; r=json.load(sys.stdin); t=r["total_duration"]; l=r["load_duration"]; \
print(f"load {l/1e9:.2f}s of {t/1e9:.2f}s = {l/t:.0%}")'
```

`load 6.63s of 7.72s = 86%` is a load-dominated call. It means the model was not in memory when the request arrived, and no amount of prompt trimming or quantization tweaking will remove that second of wall clock.

To see *what* is resident rather than infer it, [`/api/ps` lists the models currently running, with an expiry timestamp and the VRAM they occupy](https://docs.ollama.com/api/ps.md). That endpoint is what turns a guess about eviction into an observation. The probe below calls it before and after every request.

## What was measured

Three configurations ran, out of four scripted, alternating a 0.5B text model and a 2.1B vision model on one endpoint, with `num_predict=64`, `temperature=0`, `seed=42` and the prompt `Reply with the single word ok.` Each configuration got a freshly started `ollama serve` on the same port — 11435 by default — stopped between phases, so that `OLLAMA_MAX_LOADED_MODELS` was re-applied and nothing stayed warm from a previous configuration.

| Config | keep_alive | OLLAMA_MAX_LOADED_MODELS | Calls recorded | Status |
|---|---|---|---|---|
| A | `0` | 3 | 6 | complete |
| B | `5m` | 1 | 4 | complete |
| D | `-1` | 3 | 2 | stopped at the attempt deadline |
| C | `5m` | 3 | 0 | not run |

The host is a two-core aarch64 machine with 11,927 MB total RAM and no swap, running Ollama 0.20.3 with CPU inference only — `/api/ps` reported `size_vram: 0` for every resident model, so nothing here describes GPU behaviour. Config C, the "warm second call with room for two" baseline, never executed: each `qwen3-vl:2b` load costs 29–63 seconds on this box, and the run's deadline arrived first. The gap is stated again under limits, because it is the difference between "pinning helps" and "pinning removes the load stall", and only the first was measured.

## Config A: keep_alive=0 reloads on every single call

Six calls, alternating models, unload immediately after each response.

| # | Model | total_duration | load_duration | load share | Resident after |
|---|---|---|---|---|---|
| 0 | qwen2.5:0.5b | 7.72 s | 6.63 s | 86% | qwen2.5:0.5b |
| 1 | qwen3-vl:2b | 72.09 s | 46.32 s | 64% | qwen3-vl:2b |
| 2 | qwen2.5:0.5b | 9.18 s | 8.09 s | 88% | qwen2.5:0.5b |
| 3 | qwen3-vl:2b | 49.87 s | 39.38 s | 79% | qwen3-vl:2b |
| 4 | qwen2.5:0.5b | 9.93 s | 8.13 s | 82% | qwen2.5:0.5b |
| 5 | qwen3-vl:2b | 65.89 s | 38.47 s | 58% | qwen3-vl:2b |

Six of six calls carried a non-zero `load_duration`. The text model's load share stayed between 82% and 88% (median 86%); the vision model's between 58% and 79% (median 64%). Each `keep_alive=0` response unloaded its own model after answering, so that model's next turn started cold: the `/api/ps` capture taken immediately after a response listed the model that had just answered, while every `resident_before` at the following switch listed only the other model and never both. Six calls, six loads.

Note the absolute numbers rather than only the shares. Loading the 0.5B model cost 6.6–8.1 seconds here; loading the 2.1B vision model cost 38.5–46.3 seconds. The share varies because the denominator includes generation, and the vision model's generation phase swung from 8.3 to 24.4 seconds across three calls on an otherwise idle two-core machine. Comparing load shares *across* two models with different output lengths confuses the two phases; comparing a single model across configurations does not.

## Config B: keep_alive=5m does not survive an eviction limit of 1

Same loop, `keep_alive=5m`, but `OLLAMA_MAX_LOADED_MODELS=1`.

| # | Model | total_duration | load_duration | load share | Resident before → after |
|---|---|---|---|---|---|
| 0 | qwen2.5:0.5b | 6.23 s | 5.12 s | 82% | none → qwen2.5:0.5b |
| 1 | qwen3-vl:2b | 58.76 s | 29.07 s | 49% | qwen2.5:0.5b → qwen3-vl:2b |
| 2 | qwen2.5:0.5b | 9.65 s | 4.88 s | 51% | qwen3-vl:2b → qwen2.5:0.5b |
| 3 | qwen3-vl:2b | 58.11 s | 39.14 s | 67% | qwen2.5:0.5b → qwen3-vl:2b |

Four of four calls loaded. Call 2 is the one that matters: the 0.5B model had been requested with `keep_alive=5m` two calls earlier, the 5-minute window had not elapsed, and it was still reloaded for 4.88 seconds — because call 1 had evicted it. Every `resident_before` list contains the other model and every `resident_after` list contains only the model that just answered. The keep-alive window was never the binding constraint; the resident slot count was.

One caveat on the default: the FAQ says the CPU default is 3, so `OLLAMA_MAX_LOADED_MODELS=1` is a deliberately tightened setting, used here to isolate the eviction rule with two small models on a small host. The rule it demonstrates is general — if the number of models your loop alternates exceeds the resident limit, `keep_alive` cannot save you — but the specific value 1 should not be read as a stock install. A recommendation to raise the limit to 2, as some guides make, only helps if both models actually fit; see the residency note below.

## Config D: keep_alive=-1 keeps both models resident

Two calls, then the deadline.

| # | Model | total_duration | load_duration | load share | Resident after |
|---|---|---|---|---|---|
| 0 | qwen2.5:0.5b | 15.49 s | 9.67 s | 62% | qwen2.5:0.5b |
| 1 | qwen3-vl:2b | 114.64 s | 62.77 s | 55% | qwen3-vl:2b, qwen2.5:0.5b |

Call 1 is the observation that configs A and B never produced: the probe's `resident_after` list for that call contains **both** models. The pinning request was honoured — `keep_alive=-1` kept the text model resident while a second model loaded alongside it. The record in `results.jsonl` carries the two names and `size_vram: 0` for each; the 2,947,025,696-byte (2.75 GiB) weight size is the `qwen3-vl:2b` entry in the [config-A](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/ps_A_ka0_max3.json) and [config-B](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/ps_B_ka5m_max1.json) `/api/ps` captures for the same digest. No post-phase `/api/ps` capture was saved for config D, so co-residency here is the per-call resident list, not a snapshot of the co-resident total.

What was *not* measured is the payoff. Call 2 would have been the first warm call in the whole matrix — the 0.5B model answering with no load phase — and it never ran. So the honest verdict is narrower than the usual advice: pinning both models changes the residency state as claimed, and this run does not contain a warm-call timing that proves the saved seconds. Anyone quoting a speed-up from `keep_alive=-1` on this evidence would be quoting something that was not recorded.

## The decision rule this supports

Given a working pair of models and one endpoint:

1. Run the loop twice with the diagnostic above. If `load_duration/total_duration` is consistently below roughly 0.1 while the wall clock is still long, loading is not your problem — look at queueing or at the client's own retries, not at `keep_alive`.
2. If the share is high and `/api/ps` between calls shows only one model, you are being evicted. Decide which of the two causes applies by checking whether both models fit: compare each model's reported `size` in `/api/ps` against free memory, and remember that the [KV cache is allocated per model on top of the weights](/posts/local-llm-vram-kv-cache-budget-2026/).
3. If they fit with headroom, pin them with `keep_alive=-1` and confirm with `/api/ps` that both entries appear. That removes the reload; it does not by itself make generation faster.
4. If they do not fit, `keep_alive` is the wrong lever. Batch the loop by model — all coder calls, then all vision calls — so each switch is paid once instead of once per turn, or give the second model its own endpoint so each server holds one resident model and neither evicts the other.
5. If you are choosing the pair itself, prefer the smaller model on the constrained side: the load cost scales with the weights, and 39 seconds against 7 seconds on the same machine is the difference between a usable loop and an unusable one.

The residency check is the part worth making routine. `keep_alive` tells the server what you want; `/api/ps` tells you what you got, and the two disagreed in every configuration measured here.

## Reproduce it

The runner and probe ship with this article and use only the Python standard library:

- [`run.sh`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/run.sh) — runs configurations B, D and C in that order, starting a fresh server per configuration on the same port and stopping it between phases so `OLLAMA_MAX_LOADED_MODELS` is re-applied, and captures `/api/ps` on both sides of each phase.
- [`probe.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/probe.py) — alternates the two models, records `total_duration`, `load_duration`, `prompt_eval_duration`, `eval_duration`, `eval_count`, HTTP status, the resident list before and after each call, and the derived `load_share`.
- [`results.jsonl`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/results.jsonl) — configs B and D as recorded, one JSON object per call.
- [`results_configA.jsonl`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/results_configA.jsonl) — the six config-A records from the original separate invocation of the same probe; the file also holds one extra cold-open B call that the tables do not use. `run.sh` does not run config A, so use the invocation below for it.
- [`ps_A_ka0_max3.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/ps_A_ka0_max3.json) and [`ps_B_ka5m_max1.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/ps_B_ka5m_max1.json) — the `/api/ps` captures taken before and after those phases.
- [`env.txt`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-keep-alive-model-switch-latency-2026/env.txt) — core count, `ollama --version`, `free -m` and swap state at run time.

Run `./run.sh` from a directory containing both scripts; it writes to `results.jsonl` in that directory and starts servers on port 11435 by default. It covers configurations B, D and C only. For the six config-A records, start a server with `OLLAMA_MAX_LOADED_MODELS=3` — `run.sh`'s `start_server 3` shows the environment it uses — and run `python3 probe.py http://127.0.0.1:11435 A_ka0_max3 0 6 results_configA.jsonl`: same label, `keep_alive=0` and six alternating calls as the shipped file. Every row of the tables above can be read straight out of those JSONL files, including the `resident_before` and `resident_after` arrays that carry the eviction and pinning evidence.

## Limits

- Everything here is CPU-only inference on a two-core host with no swap. GPU hosts load models in a fraction of the time and the load share will be much smaller; the diagnostic still applies, the numbers do not transfer.
- Each configuration started from a fresh server, so config-to-config timings also include cold page cache. Within-configuration comparisons are the sound ones; do not read config D's 114.64-second vision call as evidence that pinning made generation slower.
- Config C (5m with room for two models) never ran, and config D stopped after two calls. The matrix is therefore A complete, B complete, D partial — with the warm pinned call, which is the whole selling point of pinning, unmeasured. Config D also has no post-phase `/api/ps` capture, so its co-residency rests on the probe's `resident_after` list.
- The two models differ in output length for the same `num_predict` (the vision model returned 64 tokens with no visible text, consistent with reasoning tokens), so cross-model load shares are not directly comparable. Absolute `load_duration` values are.
- One model pair, one quantization each, one host. Other pairs will change the absolute load cost.
- The run used local hardware and no paid provider; attributable monetary cost is unknown, not zero.

The narrow takeaway: a multi-second pause on every model switch is usually a load, the response proves it in one field, and keep-alive only keeps a model resident while the server is allowed to keep it. If you never check `/api/ps`, you are tuning a window that an eviction already closed.
