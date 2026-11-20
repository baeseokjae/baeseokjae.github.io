---
title: "Ollama Thread Tuning on CPU: Measuring Where More Threads Stop Helping Token Generation (2026)"
date: 2026-11-04T00:00:00+00:00
tags:
  - ollama num_thread
  - cpu inference threads
  - ollama performance tuning
  - llama.cpp n_threads
  - local llm benchmark
  - cpu llm throughput
  - ollama api options
  - thread oversubscription
  - prompt eval vs generation
  - 2 vcpu host
  - ollama 0.20.3
  - num_thread default
description: "num_thread is a load-time Runner option whose API default is 0, and Ollama's documented configuration has no OLLAMA_NUM_THREAD variable. On a 2-vCPU host a fixed sweep measured 13.25 generation tok/s at one thread, about 22.9 at two in the fast-mode rows, and 0.56-0.65 at four, with prompt evaluation timed separately from generation."
draft: false
schema: "schema-ollama-num-thread-cpu-tuning-2026"
---

You follow the usual advice: the local model server is using all your cores, so you pin the thread count to the number of cores and expect token generation to speed up. On a 2-vCPU box the opposite happens. The same 66-token prompt that produced 55 tokens in about 4.5 seconds with one thread took 109 seconds with four, and two later requests at that setting, bounded at 90 seconds in the second window, never returned at all. Both completed requests returned HTTP 200 with an ordinary response body; nothing in them announced that the setting was wrong.

The advice is a number without a measurement behind it, and it never says which of the two timed phases it is supposed to change. Ollama reports prompt evaluation and token generation as separate durations, and they behave differently — but almost every "tokens per second" figure people quote divides output tokens by total wall time, which mixes the two. This article shows what `num_thread` actually is in Ollama 0.20.3, what the server's own default did on a small shared host, and a one-request-at-a-time sweep that separates the phases. It also reports the negative results: one cell was too noisy to average, four threads collapsed throughput instead of improving it, and eight threads was never measured.

## The knob exists; the environment variable does not

`num_thread` is a field on the `Runner` option struct in Ollama's Go API, alongside `num_ctx`, `num_batch` and `num_gpu`, and it is accepted in the `options` object of a generate request ([ollama/api/types.go](https://raw.githubusercontent.com/ollama/ollama/main/api/types.go)). The same file shows the default Ollama's own API layer fills in: `NumThread: 0, // let the runtime decide`. Zero is not a thread count; it is a request to the runtime to choose.

The variable that articles and forum posts tell you to export, `OLLAMA_NUM_THREAD`, is not in the server's documented configuration. The FAQ's environment-variable list documents `OLLAMA_MAX_LOADED_MODELS`, `OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_QUEUE` and the host/model settings, and contains no thread-count variable ([Ollama FAQ](https://docs.ollama.com/faq.md)); the `envconfig` package that parses those variables on the main branch has no thread setting either ([envconfig/config.go](https://raw.githubusercontent.com/ollama/ollama/main/envconfig/config.go)). Absence from these files is not proof that the binary ignores an unknown variable, and older releases may differ, but it does mean the widely repeated export is not a documented control surface. The supported way to set the value is per request, in `options`.

| Control | Where it lives | Default | What it changes |
|---|---|---|---|
| `num_thread` | `options` object of `/api/generate`, load-time `Runner` field | `0` ("let the runtime decide") | Worker threads used by the loaded model |
| `OLLAMA_NUM_THREAD` | Not present in the FAQ list or `envconfig` | — | Nothing documented |
| `OLLAMA_NUM_PARALLEL` | Server environment variable | `1` | How many requests one model processes at once |
| `OLLAMA_MAX_QUEUE` | Server environment variable | `512` | Requests queued before new ones are rejected |

## What the default resolves to, and why this article will not name it

It is tempting to answer "four", because llama.cpp's context parameters default both thread counts to `GGML_DEFAULT_N_THREADS` ([llama-context.cpp](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/src/llama-context.cpp)), and `GGML_DEFAULT_N_THREADS` is defined as `4` ([ggml.h](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/ggml/include/ggml.h)). That is llama.cpp's own untouched default. It is not a statement about what the Ollama server passes down after it receives `NumThread: 0`, and the measurement below contradicts reading it that way.

`llama.cpp` also keeps two independent counts, and the header says so: `n_threads` is used "for generation (single token)" and `n_threads_batch` "for prompt and batch processing (multiple tokens)" ([llama.h](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/include/llama.h)). A single requested `num_thread` therefore has to be mapped onto two different worker pools, which is one reason a single "tokens/s" number cannot describe the effect.

On this host the default behaved like the two-thread setting, not the four-thread one. With `num_thread` omitted, two requests produced 21.37 and 23.61 generation tok/s (median 22.49, CV 5.0%, rows at 2026-11-04T17:18:03Z and 17:18:04Z) while an explicit four-thread request in the same window managed 0.65 tok/s. Four threads cannot be the setting that produced the default rows — the gap is roughly 35x. What the data cannot do is separate the rule "use `nproc`" from "use `min(4, nproc)`", because both evaluate to 2 on a 2-vCPU machine. So the honest statement is: the default runs in the two-thread band here, the four-thread constant does not describe it, and the exact resolution rule stays unresolved.

## Method

The host is a shared 2-vCPU Neoverse-N1 build machine with 11,927 MB of RAM, running Ollama 0.20.3 and kernel 6.17.0-1019-oracle. The model is `qwen2.5:0.5b` Q4_K_M, digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`, loaded with `num_ctx 2048`, `temperature 0`, `seed 42` and `keep_alive 5m`. Two fixed prompts were used: a 66-token short prompt and a 606-token long prompt, both counted by the server's own `prompt_eval_count`. `num_predict` was 96 for the explicit-thread cells and 32 for the default cells and one completed four-thread request, so generation tok/s normalises across them but wall-clock durations do not.

`num_thread` was passed in the request `options` rather than set globally, so every cell used the same resident model and the shared daemon was never restarted. Requests ran strictly one at a time, each a synchronous HTTP call, with a 180-second client timeout in the round-0 window and 90 seconds in the round-1 window — which is why the round-0 four-thread request is recorded as completing in 109.4 seconds while the two round-1 four-thread requests are recorded as timed out; no background process, no shell job control, no signal to the service. Rows were appended to separate files per window, and nothing was deleted or rewritten between rounds. The only load-average reading attached to an analysed round-0 request is 4.78 at 16:32:58Z, the start of the invocation that produced the four-thread row; a 4.04 reading was written at 16:23:11Z, at the end of the rejected dedicated-instance attempt and 32 seconds before the first analysed request, so it is a pre-window reading and not an end-of-window one. The round-1 rows store 4.13-4.69 next to the individual requests, against 2 runnable vCPUs.

The raw rows, probe scripts and method notes from both windows are kept in the author's private run record and are not published as downloadable files; the request body, host specification and field list in this article are everything needed to rerun the same sweep, and the numbers below are reported with their timestamps so they can be checked against that record.

## Results

Twenty-one records across two windows on 2026-11-04 (16:23-16:34 UTC and 17:14-17:18 UTC). All figures are generation tokens per second, computed from the server's `eval_count` and `eval_duration`, never from wall time. Every CV in the table is the population standard deviation divided by the mean of the rows listed for that cell, so the column is comparable across cells.

| Cell (2 vCPU host) | Requests | Median generation tok/s | Range | CV |
|---|---|---|---|---|
| 1 thread, 66-token prompt | 3 | 13.25 | 13.12-13.30 | 0.6% |
| 1 thread, 606-token prompt | 3 | 11.20 | 11.18-11.21 | 0.1% |
| 2 threads, 66-token prompt, fast mode | 3 | 22.88 | 22.48-23.00 | 1.0% |
| 2 threads, 66-token prompt, slow mode | 3 | 3.25 | 1.81-3.72 | not averaged |
| 2 threads, 606-token prompt | 3 | 18.58 | 18.49-18.62 | 0.3% |
| Default (no `num_thread`) | 2 | 22.49 | 21.37-23.61 | 5.0% |
| 4 threads, 66-token prompt | 2 (+2 timeouts) | 0.60 | 0.56-0.65 | 7.8% |
| 8 threads | 0 | not measured | — | — |

Two threads beat one on both prompt sizes in this sample: 13.25 to 22.88 tok/s on the short prompt and 11.20 to 18.58 tok/s on the long one, which is what you would expect when two real cores are given two worker threads. The size of the short-prompt gain should not be averaged — see the next section — and the long-prompt ratio (1.66x for twice the threads) is the more trustworthy of the two because that cell was stable.

## The two-thread short cell split into two modes

Six short-prompt rows at two threads exist across the two windows, three per window: 22.48, 22.88 and 22.99 tok/s in one mode, and 1.81, 3.25 and 3.72 tok/s in the other. The combined CV of those six rows is 77%, far past the 15% ceiling this experiment set for itself, so no averaged 1-to-2 gain is published from that cell. Both modes are real observations from the same server and model, and the fast mode matches the default cell's band, which is why the table reports them as two populations.

The plausible mechanism is host contention, not thread count: two of the three slow rows recorded load averages of 4.58 and 4.69 on 2 vCPUs, and the third stores no load average at all, while a neighbour taking the cores leaves the model's two threads runnable but not scheduled. The operational consequence is that on a shared box you cannot compare a thread setting against a baseline taken minutes earlier and attribute the difference to threads. Record load average next to every row, and if your repetitions split into two clusters, report the clusters instead of a mean.

## Four threads on a two-core host collapses throughput

Oversubscription did not produce a plateau. It produced a cliff. Two completed requests at `num_thread: 4` measured 0.56 tok/s (55 tokens in 109.4 s wall clock; the 4.78 load average was recorded at the window start, 16:32:58Z, two minutes before this row, which stores no load average of its own) and 0.65 tok/s (32 tokens in 50.9 s, load average 4.13, 17:16:51Z), with two more requests at the same setting in the second window timing out at 90 seconds. The collapse was reproduced in two windows about 42 minutes apart, on the same model digest and the same server instance, so it is not one bad request.

The magnitude is contention-dependent: both windows had load above the two available cores, so this measures oversubscribed threads on an oversubscribed host, which is the realistic condition for a shared CPU box but not a clean single-tenant figure. The direction is what the data supports — on a 2-vCPU machine, asking for twice the cores costs roughly 35-40x generation throughput relative to the server's own default, and some requests never complete. If you set `num_thread` from `nproc` on a machine where `nproc` already counts hyperthreads or is shared with other work, this is the failure you are signing up for.

## Why a single tokens/s number hides the effect

Ollama's generate response reports `prompt_eval_duration` as "time spent evaluating uncached prompt tokens", `eval_duration` as "time spent generating tokens", and `prompt_eval_cached_count` alongside them ([/api/generate](https://docs.ollama.com/api/generate.md)). Divide output tokens by total time and you mix prefill, generation and model load into one figure.

The clearest example is the first long-prompt request at one thread: 42.70 s total, of which 34.87 s was prompt evaluation and only 7.52 s was the 84 generated tokens. Generation was 11.18 tok/s; dividing 84 tokens by 42.70 s gives 1.97 tok/s, a 5.7x understatement of the thing you were trying to tune. The second identical request finished in 7.96 s because 606 prompt tokens came back from cache (`prompt_eval_duration` dropped from 34.87 s to 0.10 s). Any sweep that repeats one prompt without noticing `prompt_eval_cached_count` will "discover" a 5x speedup that is just the cache warming up.

Counting the phases separately is also the only way to see that the four-thread collapse hits both. In the long-prompt cell, prefill went from 17.4 tok/s at one thread (606 tokens in 34.87 s) to 31.1 tok/s at two (606 tokens in 19.50 s), a factor of 1.79, while generation went from 11.20 to 18.58 tok/s, a factor of 1.66 — so "prompt evaluation scales differently from generation" was not observed here; both phases responded to the same doubling, roughly equally. What the separation does buy you is attribution: at four threads the 66-token prompt evaluated at roughly 44 tok/s (1.50 s for 66 tokens) against roughly 873 tok/s at one thread, about 20x slower, while generation fell from 13.25 to 0.60 tok/s. Prefill is not immune to oversubscription just because it uses the batch worker pool.

## What to set, and when threads are the wrong lever

On a 2-vCPU host, the measured default was already at the two-thread band and matched an explicit two-thread request; there was nothing to gain by setting the value and a large loss at four. Leaving `num_thread` unset was the correct configuration here, and the null result is the finding worth keeping.

On 4- or 8-core machines the same protocol transfers but the conclusion does not: measure `nproc`, run three repetitions at one, `nproc` and `2 x nproc` threads with a fixed prompt, discard a warm-up request, and compare medians only if every cell's CV stays under about 15%. Past `nproc`, expect degradation rather than a plateau — the plateau in this data is not "more threads stop helping", it is "more threads than cores is actively harmful". If the reason you started tuning is that a second agent session is waiting for the first, thread count is the wrong lever: the requests are serialised by the server's parallel-slot setting, which is a separate queueing problem described in [two agent sessions against one local model server](https://baeseokjae.github.io/posts/local-llm-concurrent-agent-sessions-2026/). If you are squeezing a model into memory, that is a context and KV-cache budget, not a scheduling one ([VRAM and KV-cache budget](https://baeseokjae.github.io/posts/local-llm-vram-kv-cache-budget-2026/)).

The request that produced each row above is small enough to paste into a terminal, with the thread count as the only variable:

```
curl -s http://127.0.0.1:11434/api/generate -d '{
  "model": "qwen2.5:0.5b",
  "prompt": "<fixed prompt>",
  "stream": false,
  "keep_alive": "5m",
  "options": {"num_thread": 2, "num_ctx": 2048, "num_predict": 96,
              "temperature": 0, "seed": 42}
}'
```

Record `eval_count`, `eval_duration`, `prompt_eval_count`, `prompt_eval_duration`, `prompt_eval_cached_count`, `total_duration` and the host load average for every request; compute generation tok/s as `eval_count / (eval_duration / 1e9)`. Omit the `num_thread` key entirely for the default cell — passing `0` is not the same as omitting it, since `0` is what the API substitutes when the field is absent, and the comparison you care about is what the server does when nobody asks. Delete one warm-up request per cell before collecting, and never compare a cached prompt against an uncached one. Model choice on a CPU-only host is a bigger lever than any of this and is covered in [best local LLM models](https://baeseokjae.github.io/posts/best-local-llm-models-2026/) and [best Ollama coding models](https://baeseokjae.github.io/posts/best-ollama-models-coding-2026/); the API surface itself is in the [Ollama API integration guide](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/), and the agent-side tuning block most readers arrive from is in [Aider with Ollama](https://baeseokjae.github.io/posts/aider-ollama-local-coding-2026/).

## Limitations

No eight-thread cell exists. Every request above two threads either hit the client timeout of the window that ran it (90 seconds, in the second window) or completed at about 0.6 tok/s, so a further cell would have consumed the remaining measurement budget without producing a distinguishable result; nothing in this article implies eight threads were measured. The two-thread short cell is bimodal and is reported as two modes, not a mean, and neither round reached the nine repetitions the original plan targeted. Host load averaged above the two available cores for much of both windows, so absolute throughput is not a single-tenant number and the four-thread collapse magnitude would be smaller on an idle machine. The effective default thread count could not be resolved from source or from a readable server log, and this host cannot distinguish the two candidate rules because both give 2. All source checks are against main-branch files and current documentation read on 2026-11-04 and re-checked on 2026-11-19, not a tagged 0.20.3 release tarball; every quoted fact was present verbatim in both readings, though the files' bytes and line numbers changed between them, so a later main-branch change could still invalidate a quotation. Every figure above comes from a two-window local measurement; no vendor benchmark is quoted, and the observation that both phases respond to thread count rests on one prompt size and one 0.5B model, so a larger model or a different prefill length could still split them.
