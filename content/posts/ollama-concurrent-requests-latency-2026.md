---
title: "Two Agents, One Ollama: Measuring Why the Second Request Queues Instead of Speeding Up (2026)"
date: 2026-11-04T00:00:00+00:00
tags:
  - ollama concurrent requests
  - ollama num_parallel
  - ollama queue latency
  - local llm server concurrency
  - ollama api total_duration
  - parallel agent requests local model
  - ollama max_queue
  - cpu-only llm inference
  - ollama throughput vs latency
  - ollama scheduler slots
  - local llm subagent fanout
  - ollama timing fields
description: "A CPU-only measurement of two simultaneous Ollama requests: the second one waits one full generation, and the response body proves it. Includes the one-line queue diagnostic, a 17-batch matrix for OLLAMA_NUM_PARALLEL 1/2/4, and why extra slots buy latency, not throughput."
draft: false
schema: "schema-ollama-concurrent-requests-latency-2026"
---

You start a second coding agent against the Ollama endpoint that already answers your first one. Nothing errors out. The second call simply sits there for two or three seconds, and when both finish your "parallel" run has taken longer than running the two prompts one after the other. The usual conclusion is that the model is slow, the quant is wrong, or the machine needs more RAM. On the host measured here, none of those were true: the second request was queued, and the HTTP response said so in its own timing fields.

This post is the mechanism, a diagnostic you can run against one response, and a measured verdict for CPU-only machines. Everything below comes from 17 recorded batches on a 2-core aarch64 box with Ollama 0.20.3 and `qwen2.5:0.5b`, run on 2026-11-04 between 00:33:20Z and 00:35:37Z. The raw records are published with the article so the numbers can be recomputed rather than trusted.

## What Ollama does with the second request

Ollama's own documentation describes two levels of concurrency: several models resident at once, and, inside one model, several requests processed in parallel. The second level is what a subagent fan-out or a background embedding call runs into, and it is a per-model setting rather than a per-request one — [the FAQ states that parallel request processing is configured when the model is loaded, and that a model is "configured to allow parallel request processing" only if memory allows](https://docs.ollama.com/faq.md). When memory does not allow it, "all new requests will be queued until the new model can be loaded", and "queued requests will be processed in order".

The compiled defaults decide how often that path is taken. In the runtime's configuration source, [parallel request processing defaults to 1, the pending queue to 512, and the maximum number of resident models to 0, meaning automatic](https://raw.githubusercontent.com/ollama/ollama/main/envconfig/config.go). So a stock install handles exactly one generation per model at a time. The second request is not rejected and not run concurrently — it goes into the scheduler's pending channel, which is also where the "server busy" error comes from: [in the scheduler, a request whose runner is neither loaded nor reloadable is pushed to a pending channel, and only a full channel returns `ErrMaxQueue`](https://raw.githubusercontent.com/ollama/ollama/main/server/sched.go). Up to 512 requests can therefore wait politely for a slot before anything fails.

That is the whole trap. A queued request returns HTTP 200 with a normal-looking answer. The only trace of the wait is time that belongs to no phase of the work.

## The diagnostic: one response, four fields

`/api/generate` reports its own timing breakdown, in nanoseconds: `total_duration`, `load_duration`, `prompt_eval_duration`, and `eval_duration`, [documented in the generate API reference](https://docs.ollama.com/api/generate.md). For a request that was never queued, those three components add up to the total. For a request that waited, they do not, and the difference is the queue wait:

```bash
curl -s http://127.0.0.1:11434/api/generate -d '{"model":"qwen2.5:0.5b","prompt":"hello","stream":false}' \
| python3 -c 'import json,sys; r=json.load(sys.stdin); t=r["total_duration"]; \
q=t-(r["load_duration"]+r["prompt_eval_duration"]+r["eval_duration"]); \
print("total_s=%.2f queue_s=%.2f queue_fraction=%.2f" % (t/1e9, q/1e9, q/t))'
```

Two details make the difference between a working diagnostic and a misleading one. First, `load_duration` is not zero even when the model is already resident: on this host it was 0.20-0.30 s for a warm 0.5B model and 0.49-1.04 s on the 4-slot instance. Load plus prompt-eval overhead was 0.24-0.34 s on the default and 2-slot instances, 0.62-0.92 s in the warm 4-slot batch and 0.96-1.32 s in the second cold 4-slot batch, so subtracting only `eval_duration` from `total_duration` inflates apparent waiting by roughly a quarter to a third of a second at one or two slots and by up to about 1.3 s at four. (The first cold 4-slot batch is worse still — a prompt-cache miss put 4.64 s of prompt evaluation on three of its four requests — and is excluded from the reported table for that reason.) Second, the fraction matters more than the absolute value, because a long generation dilutes the same queue wait into a smaller share.

On the measured host the split was unambiguous. Solo requests in the default configuration left a residual of 0.05 s, about 2% of a 2.3-2.6 s total. In the same configuration, the second of two simultaneous requests showed a residual of 2.16, 2.27, 2.17 and 2.41 s across four batches — 40-51% of its total time — while the first request in that batch still finished with a 0.05 s residual.

## The measurement: 17 batches, three configurations

The runtime was Ollama 0.20.3, [published 2026-04-07 according to the GitHub release metadata](https://github.com/ollama/ollama/releases/tag/v0.20.3). The probe sends `POST /api/generate` with `stream: false`, `temperature: 0`, `seed: 42` and `num_predict: 64`, one fixed prompt, and every request produced `eval_count: 46`. Concurrent requests synchronise on a barrier so they leave together. Three server configurations were used: A is the pre-existing default server on port 11434; B is a dedicated instance on port 11500 with `OLLAMA_NUM_PARALLEL=2`; C is a dedicated instance on port 11501 with `OLLAMA_NUM_PARALLEL=4`. Both dedicated instances used the system model directory and `OLLAMA_MAX_QUEUE=1`, which is worth noting: with free slots available, nothing was rejected, so the single-queue-slot limit never fired.

| Config | Concurrency | Warm batches | Per-request total (s) | Per-request eval (s) | Queue residual (s) | Aggregate tok/s |
|---|---|---|---|---|---|---|
| A default | 1 | 3 | 2.30-2.59 | 2.00-2.27 | 0.05 | 17.7-20.0 |
| A default | 2 | 4 | 2.40-2.62 (first) / 4.49-5.69 (second) | 2.02-2.26 (first) / 1.96-3.13 (second) | 0.05 (first) / 2.16-2.41 (second) | 16.2-20.4 |
| B `NUM_PARALLEL=2` | 1 | 2 | 2.29-2.48 | 1.99-2.17 | 0.05 | 18.5-20.1 |
| B `NUM_PARALLEL=2` | 2 | 3 | 4.08-4.60 | 3.67-4.13 | 0.09-0.17 | 20.0-22.0 |
| C `NUM_PARALLEL=4` | 4 | 1 | 8.70-8.94 | 7.81-7.90 | 0.12-0.34 | 20.6 |

Four batches were excluded as cold and are marked `cold=true` in the per-batch summary: the very first solo batch (4.93 s, of which 4.61 s was `eval_duration` at 10.0 tok/s; `load_duration` was 0.22 s, no higher than the warm solo rows), one 2-slot batch on config B where a cold prompt cache pushed `prompt_eval_duration` to 1.58 s, and the two earliest 4-slot batches (19.2 s and 16.4 s): the first carries the 4.64 s prompt-eval miss on three requests described above, and the second spent 14.8 s of its 16.4 s in `eval_duration` at 3.1 tok/s with `load_duration` 0.73-1.04 s. They ran at 9.6 and 11.2 aggregate tok/s against 20.6 in the warm batch. Cold exclusion is stated because it changes the numbers: the excluded 4-slot batches are twice as slow as the one warm batch reported.

## What the numbers say

Under the default configuration, the second request waited about as long as one full generation. Its total was 4.49-5.69 s against 2.30-2.59 s for a solo request, and the wait it added — 2.16-2.41 s — is almost exactly the eval time of the batch-mate holding the slot (2.02-2.26 s). Per-request token rates mostly held: in three of the four batches the queued request generated at 22.0-23.4 tok/s against 20.3-22.8 for that batch-mate. The exception is rep 1, where the queued request ran at 14.7 tok/s (eval_duration 3.13 s) against 21.7 for the first, even though the first request's own latency was unchanged at 2.46 s. That is still a queue, not CPU contention: if the two generations had been sharing two cores for their whole duration, the first request's latency would have moved, and it did not.

Setting `OLLAMA_NUM_PARALLEL=2` removed the wait and replaced it with slower generations. Both requests came back in 4.08-4.60 s with `eval_duration` 3.67-4.13 s, against 2.00-2.27 s solo, and the queue residual fell to 0.09-0.17 s. Per-request throughput halved from roughly 20-23 tok/s to 11.1-12.5 tok/s. On two cores, two concurrent generations each run at about half speed, which is what a shared CPU should do.

Aggregate throughput barely moved. Warm batches gave a median of 19.1 tok/s solo on config A, 19.8 tok/s for config A at concurrency 2, 22.0 tok/s for config B at concurrency 2, and 20.6 tok/s for the single warm config C batch at concurrency 4. The best-case ratio that could be argued, 22.0 / 19.8 = 1.11x, sits inside a run-to-run spread of 16.2-22.0 tok/s, and far below the 1.5x improvement that would have made extra slots worth recommending on this hardware. Doubling or quadrupling the slot count changed latency per request by roughly 1.8-3.9x and throughput by nothing measurable.

The practical consequence is the counter-intuitive one: for two prompts on a CPU-only host, fanning out to two agents takes as long as — or slightly longer than — calling them one after the other, because the queue serialises them anyway when only one slot exists, and splits the cores when two exist. Parallelism on a CPU host is not free capacity; it is a different shape of the same capacity.

## What it costs in memory

Slots are not free. The FAQ states that parallel request processing increases the context size by the number of parallel requests, and the server log confirms the arithmetic: the load line reports `Parallel:2 ... KvSize:8192` for the 2-slot instance and `Parallel:4 ... KvSize:16384` for the 4-slot instance, against a 4,096-token default context. `KvSize` is the total KV allocation across slots, not a per-slot value.

`/api/ps` shows the result in reported model memory: `size` 442,191,360 bytes for the default server and 492,523,008 bytes with two slots — 50,331,648 bytes, or 48.0 MiB, more, a rise of 11.4%. One detail that catches readers out: `context_length` stayed at 4096 in both `/api/ps` captures, so a per-request context that halved is not what the API reports. The KV allocation doubles — `KvSize:8192` for two slots against the 4,096-token default context — while the total reported `size` rises by 11.4%. The reported per-slot context does not change. If you are sizing a second slot, do the arithmetic from context times slot count, as in [the KV-cache budget walkthrough for a local coding model](/posts/local-llm-vram-kv-cache-budget-2026/), rather than trusting the single `context_length` field.

Every one of these captures reports `size_vram: 0`. This host has no GPU, and nothing here should be read as a statement about GPU behaviour, where a second slot may overlap compute across SMs and actually raise throughput.

## What to do instead

Serialise, then batch. If the second call is an embedding step or a summarisation pass that does not need to interleave with the first, run it after the agent's tool call rather than beside it — you lose nothing on a CPU host, because the scheduler was serialising it anyway whenever the slot was busy.

If you do want concurrent slots, enable them deliberately and budget the memory, then verify with the residual diagnostic that requests are actually overlapping rather than queueing. A residual near zero with doubled `eval_duration` means the slots are working as intended; a residual equal to one solo generation means you are still at one slot, whatever the environment variable says, which is the usual symptom of setting it on the client instead of the server process.

Move to a GPU when throughput, not latency, is the goal. The 1.11x aggregate result here is a statement about two CPU cores, not about `OLLAMA_NUM_PARALLEL` in general — and even on a GPU, [the queue-versus-batching distinction is what decides whether a serving stack helps](/posts/vllm-vs-ollama-production-2026/).

## What this is not

It is not a GPU benchmark, a model comparison, or a vLLM comparison. One 0.5B Q4_K_M model, 46 generated tokens, two cores: long prompts and prefill-bound workloads were not measured, and `OLLAMA_MAX_LOADED_MODELS` behaviour — a second *model* being swapped in — was not tested at all. The 503 path behind `OLLAMA_MAX_QUEUE` is documented in the source linked above but was not reproduced live, because every request in this matrix eventually received a slot. The queue-versus-compute split is derived from Ollama's own duration fields; no external profiler or debug-level scheduler trace corroborates it.

If your local agent is underperforming, scheduler queueing is one of several causes. Context truncation is the other common one on the same endpoint, covered in [why a local model silently answers with less context than you sent](/posts/ollama-silent-context-truncation-2026/). If you leave Ollama for llama.cpp's server, the equivalent knob is `-np`, and its splitting behaviour differs from Ollama's scheduler — see [diagnosing llama-server context overflow](/posts/llama-server-context-overflow-diagnosis-2026/). For the environment-variable reference and the OpenAI-compatible endpoint, the [Ollama API integration guide](/posts/ollama-api-local-llm-integration-developer-guide-2026/) lists the same three settings; the tuning block in [the Aider + Ollama setup](/posts/aider-ollama-local-coding-2026/) is the one this post measures. And if you are choosing a model for a CPU-only host in the first place, [the coding-model shortlist for CPU inference](/posts/best-ollama-models-coding-2026/) is the better starting point than any concurrency tuning.

## Reproduce it

The measurement is reproducible on a 2-core CPU box in under three minutes: 17 batches took 137 s including model load. The files below are the exact inputs and outputs of the run described above, published so every figure in this article can be recomputed from the raw response bodies.

| File | What it is |
|---|---|
| [probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/probe.py) | stdlib-only probe: barrier-synchronised concurrent `POST /api/generate`, records status and all timing fields |
| [run.sh](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/run.sh) | the exact commands: host capture, `/api/ps` before and after, the three server configurations, per-cell warm-up |
| [results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/results.jsonl) | 17 batches, one JSON object per batch, every request's raw nanosecond fields |
| [summary.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/summary.csv) | per-batch derived rows: aggregate tok/s, per-request medians, queue residual, cold flag |
| [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/method.md) | request shape, derived formulas, what was deliberately not measured; the authoritative `cold` flag is in `summary.csv` |
| [host.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/host.txt) | `ollama --version`, `nproc`, `free -m`, kernel and architecture |
| [ps_A.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/ps_A.txt) / [ps_B.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/ps_B.txt) | `/api/ps` after each configuration: `size`, `size_vram`, `context_length` |
| [server_b_lines.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/server_b_lines.txt) / [server_c_lines.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-concurrent-requests-latency-2026/server_c_lines.txt) | the server config and load lines showing `OLLAMA_NUM_PARALLEL`, `Ollama version 0.20.3`, `Parallel` and `KvSize` |

To rerun on your own hardware, start a second server on a spare port against the same model directory rather than restarting the one your editor is using, point `probe.py` at it, and compare the residual fraction for concurrency 1 and 2. If the second request's residual is near zero and its `eval_duration` roughly doubles, your slots are working; if the residual is about one solo generation, they are not. Note that `summary.csv` reports the per-batch median across the requests in that batch, so a two-request batch with one queued request shows a residual median of roughly half the queued request's own wait — read the per-request fields in `results.jsonl` when you want the wait of the request that actually queued.
