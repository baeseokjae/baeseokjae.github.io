---
title: "Two Agent Sessions, One Local Model Server: what concurrency does to latency, context and tool calls"
date: 2026-11-02T00:00:00+00:00
tags:
  - local llm concurrency
  - ollama num_parallel
  - llama-server parallel slots
  - agent session timeout
  - local model server queue
  - ollama max queue
  - coding agent latency
  - multi agent local llm
  - context window per slot
  - ollama api num_ctx
  - cpu inference queueing
  - parallel slots kv cache
description: "Ollama ships one parallel slot per model, so a second agent session waits behind the first: four concurrent requests serialised to 4.0x the single-request wall time on a 2-vCPU host, and OLLAMA_NUM_PARALLEL=4 made each request 4.4-8.0x slower against the default server's single-request baseline (3.8-7.0x against its own) instead of faster. Measured latency, the documented context rules, and what to log when a session stalls."
draft: false
schema: "schema-local-llm-concurrent-agent-sessions-2026"
---

Your first coding-agent session answers in a couple of seconds. You open a second one against the same local server, and now the first session's next request stalls for many seconds, or your client aborts with a read timeout while the server log shows no error at all. Restart the server and run one session: everything is fast again.

Nothing is wrong with the model or with either agent. Both sessions are sending requests to one server process that was never configured to work on more than one at a time, and the queue between them is invisible to your client. This article shows the documented defaults that decide how many requests a local server will actually run at once, measures what the second and fourth session do to wall time on a small CPU host, and lists what to record so you can prove the cause instead of guessing.

## The shared resource is the server, not the model weights

Two agents pointed at `http://localhost:11434` are two HTTP clients against one Ollama process. That process loads the model once and then decides how to schedule the requests it receives. Ollama's own documentation splits concurrency into two levels: how many *models* may be resident at once, and how many *parallel requests* a single model will process at the same time — [Ollama FAQ, concurrency section](https://docs.ollama.com/faq.md). The second number is the one that decides whether your two sessions overlap or take turns.

The FAQ states the rule directly: "For a given model, if there is sufficient available memory when the model is loaded, it is configured to allow parallel request processing", and a model that is loaded with only one request processing at a time will make the second caller wait. Requests that cannot be served immediately are queued in arrival order — "Queued requests will be processed in order" — and only rejected when the queue itself is full ([Ollama FAQ](https://docs.ollama.com/faq.md)).

## Ollama's default is one slot per model, not four

Three server settings decide the shape of the queue, and all three have defaults you probably never set ([Ollama FAQ](https://docs.ollama.com/faq.md)) — the values below are quoted from that page, which is the same text this run read on 2026-11-02:

| Setting | Documented default | What it changes |
|---|---|---|
| `OLLAMA_NUM_PARALLEL` | 1 | Parallel requests the model processes at once; "Required RAM will scale by `OLLAMA_NUM_PARALLEL` * `OLLAMA_CONTEXT_LENGTH`" |
| `OLLAMA_MAX_LOADED_MODELS` | 3 (CPU) or 3 x GPUs | How many distinct models may stay resident |
| `OLLAMA_MAX_QUEUE` | 512 | Requests held while busy before new ones are rejected |

Check what your own server is running with before you theorise about it. An empty `env | grep '^OLLAMA'` means every value is a default, and the model row from `ollama ps` prints the context the server believes it is serving plus how long it will stay loaded:

```
$ env | grep '^OLLAMA'        # no output = all defaults, so OLLAMA_NUM_PARALLEL=1
$ ollama ps                   # NAME  ID  SIZE  PROCESSOR  CONTEXT  UNTIL
```

The per-request context is a separate knob from those server variables: `num_ctx` is the "Context length size (number of tokens)" in the [Generate API reference](https://docs.ollama.com/api/generate.md), and `options.num_ctx` is what an agent client sends with each call. A client that sets a generous context per request is not asking for a generous number of slots.

## What the probe measured on one CPU host

The measurement below is deliberately narrow: one machine, one small model, no GPU, and one fixed prompt. It answers "what does a second session cost on a host like mine", and it says nothing about throughput on hardware with more cores.

| Item | Value |
|---|---|
| Host | 2 vCPU aarch64 (Neoverse-N1), 11 GiB RAM, no GPU |
| Server | `ollama version is 0.20.3` |
| Model | `qwen2.5:0.5b`, 397 MB, Q4_K_M |
| Request | one non-streaming `POST /api/generate`, fixed 59-token prompt, `num_ctx=2048`, `num_predict=64`, `temperature=0`, `seed=7`, `keep_alive=5m` |
| Load | N concurrent clients released from a single barrier, so every request enters the server in the same instant |
| Config A | system server, no `OLLAMA_*` variables (defaults, therefore one slot) |
| Config B | second server on `127.0.0.1:11435` started as `OLLAMA_HOST=127.0.0.1:11435 OLLAMA_NUM_PARALLEL=4 OLLAMA_CONTEXT_LENGTH=2048 ollama serve` |

Wall time is measured client-side around the whole call, which is exactly what your agent's HTTP client sees. Every request in every cell returned HTTP 200 with `eval_count=64`.

| Config | N | Observed wall times (ms) | Slowest vs the 3256.9 ms default N=1 row |
|---|---|---|---|
| A: defaults (1 slot) | 1 | 3256.9; 3209.0 | 1.0x |
| A: defaults (1 slot) | 2 | 3223.4, 6235.9 | 1.9x |
| A: defaults (1 slot) | 4 | 4163.3, 7127.3, 10138.3, 13131.4 | 4.0x |
| A: defaults (1 slot) | 4 (repeat) | 3504.4, 6513.7, 9455.4, 12418.3 | 3.8x |
| B: `OLLAMA_NUM_PARALLEL=4` | 4 | 25586.7, 26199.3, 26211.4, 26212.7 | 8.0x |
| B: `OLLAMA_NUM_PARALLEL=4` | 4 (repeat) | 14003.7, 14316.3, 14320.7, 14325.4 | 4.4x |
| B: `OLLAMA_NUM_PARALLEL=4` | 1 | 3753.9 | 1.15x |

The last column divides by one denominator throughout: the 3256.9 ms N=1 row of configuration A, the default server. That makes the last three rows a comparison between two servers, not a before/after on one. Measured against the four-slot server's own single-request row (3753.9 ms), the same two four-slot cells are 7.0x and 3.8x — the same conclusion, a smaller factor, and the number that isolates what the slot setting did on that process.

Two shapes are worth reading out of that table. Under the default configuration the four requests finish at roughly 3.0-second intervals — 4163, 7127, 10138, 13131 ms in the first repeat, 2964 to 3011 ms apart, and 3504, 6514, 9455, 12418 ms in the second, 2942 to 3009 ms apart — which is about one single-request duration each, the signature of one slot serving four requests back to back rather than four requests progressing together. The N=2 cell shows the same thing at smaller scale: one request returned in 3223 ms, the second in 6236 ms, because it started by waiting for the first to finish.

With four slots the shape inverts, and it does not improve. In the first repeat all four requests finished within 630 ms of each other but each took 25.6 to 26.2 seconds, roughly twice as long as the slowest queued request under one slot. In the second repeat the same cell landed at 14.0 to 14.3 seconds. The single-request baseline on that second server was 3753.9 ms, so four slots bought parallelism without buying speed: the four requests shared the same two cores, and every one of them ran slower than it would have alone.

The honest confidence statement: most cells have two repeats, not twenty, and the N=2 cell and the second server's N=1 baseline have one. The spread between repeats is large — the same four-slot cell produced a 26-second band and a 14-second band — so treat these as order-of-magnitude figures for a two-core box, not as p95 latencies. They are not a throughput benchmark and they do not transfer to GPU serving.

## Why the client sees a timeout rather than a 503

The obvious hypothesis — "the second session gets rejected" — does not hold at the sizes a developer actually runs. `OLLAMA_MAX_QUEUE` defaults to 512 requests, so the server holds queued work instead of refusing it unless you are far past two or three agent sessions ([Ollama FAQ](https://docs.ollama.com/faq.md)). In the probe, 21 requests across all cells produced zero non-200 statuses and zero error bodies; the only observable effect of concurrency was elapsed time.

That is worse than an error, because the failure moves into your client. A queued request looks identical to a slow one until your own read timeout fires. An agent framework with a 30-second HTTP timeout on a host where a queued request can take 26 seconds will abort, retry, and — if the retried tool call carried a side effect — do the same work twice. If you have seen duplicate writes from a "flaky" local agent, the retry-on-timeout path is worth auditing alongside the queue behaviour in [agent tool retries and duplicate side effects](https://baeseokjae.github.io/posts/agent-tool-retry-duplicate-side-effects-2026/).

The practical consequence: on a one-slot server, your effective concurrency limit is set by the client timeout, not by the server's capacity. Two sessions are fine if a single request takes 3 seconds and your timeout is 30. Four sessions with a longer prompt are not, because the fourth request inherits three queue waits and only the last one looks slow.

## Context: multiplied by slots here, per-slot there

The memory side of concurrency is documented, and it is not what most people assume. Ollama does not divide one context window among parallel requests — it multiplies: "Parallel request processing for a given model results in increasing the context size by the number of parallel requests. For example, a 2K context with 4 parallel requests will result in an 8K context and additional memory allocation" ([Ollama FAQ](https://docs.ollama.com/faq.md)). Combined with the stated RAM rule (`OLLAMA_NUM_PARALLEL` x `OLLAMA_CONTEXT_LENGTH`), that means raising slots on a memory-tight box can turn a working setup into an allocation failure at load time, before any request is served.

The reported field is a trap. A server started with `OLLAMA_NUM_PARALLEL=4` and `OLLAMA_CONTEXT_LENGTH=2048` answered `/api/ps` with `context_length: 2048` for a model it had just loaded, even though the vendor rule says four slots allocate four times that context. Reading `ollama ps` CONTEXT as "the memory I am using" will therefore understate a multi-slot server; the recorded response is in the published evidence below.

llama.cpp's server takes the opposite configuration shape. Slots are counted explicitly with `-np, --parallel N` ("number of server slots, default: -1, -1 = auto"), and per-slot context is a separate flag: `--kv-unified-per-slot N`, "context limit per parallel slot; when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N" ([llama.cpp server README](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md)). So on llama-server you choose both the slot count and the per-slot window, while on Ollama the per-request `num_ctx` is multiplied by the slot count. Either way, the number that matters for memory is slots x context, not context.

Before you raise slots, do the arithmetic for the model you actually run — the KV-cache sizing formula and a measured check of it are in [sizing KV cache and context for a local coding model](https://baeseokjae.github.io/posts/local-llm-vram-kv-cache-budget-2026/). A 4-slot server is a 4x cache budget on the same weights.

## A decision table for two to four sessions

| Situation | What to configure | Why |
|---|---|---|
| Two or three agent sessions on a 2-core CPU box | Leave `OLLAMA_NUM_PARALLEL=1`; raise the client's read timeout well past a single request's worst case | Four slots on two cores measured 4.4-8.0x slower per request than the default server's 3256.9 ms single-request row, and 3.8-7.0x slower against the four-slot server's own 3753.9 ms row; queueing is cheaper than contention at this core count |
| Spare cores and spare memory | Try `OLLAMA_NUM_PARALLEL=N` with `OLLAMA_CONTEXT_LENGTH` set explicitly, then measure your own p50 | The vendor rule multiplies context by slots, so both time and memory change together; nothing here predicts your hardware |
| Sessions that must never block each other | Separate servers on separate ports with separate models, or separate hosts | Two processes cannot contend for the same slot, and each keeps its own context budget |
| llama-server instead of Ollama | Set `-np` explicitly, and set `--kv-unified-per-slot` when you want a hard per-session window | Auto slots hide how the shared KV pool is divided; explicit values make the memory budget auditable |

The middle row is the one to be sceptical about: the only first-party evidence in this article for raising slots is negative, on two cores. GPU serving divides work differently and was not measured here, so nothing above is a claim about what slots do on a GPU.

## What to log when a session stalls

If a session dies while another is running, the question is not "which agent is broken" but "what did this request wait for". Record these five items per request and the answer is usually visible in one table:

- Client-side wall time around the whole HTTP call — the number your timeout compares against.
- HTTP status and the verbatim response body on failure; a 200 with a body is a different bug from a 503.
- `done_reason` and `eval_count` from the response — a `length` stop means your own `num_predict` cap was hit, not that the server truncated anything.
- Start timestamps of every concurrent session, so queue waits can be attributed rather than assumed.
- The server's own row (`ollama ps` CONTEXT and UNTIL, or the llama-server slot log) taken while the requests are in flight, not after they finish.

None of that requires instrumenting the model. It does mean your agent's HTTP layer must log the call rather than only its own decision loop.

One thing this article does **not** establish: whether concurrency truncates tool-call arguments. No tool-calling payload was sent in this probe, no malformed tool call appeared in any cell, and no shortened context was observed — every response carried the same 316 characters and the same `eval_count`. If you are debugging a tool call that arrives with a cut-off JSON argument, the surfaces to inspect are the raw assistant message before your parser, the `done_reason`, and the per-request `num_ctx`, but this measurement gives you no evidence that a second session causes it.

## Files, method, and how to rerun it

The probe is a single stdlib Python script: it releases N clients from one barrier, records wall time, status and the verbatim error body per request, and flushes partial results after every cell so a deadline cannot lose data. These files are first-party and published with the article:

| File | What it is |
|---|---|
| [probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-concurrent-agent-sessions-2026/probe.py) | The driver: barrier-synchronised cells, per-request records, deadline and partial flush |
| [probe-default.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-concurrent-agent-sessions-2026/probe-default.json) | Raw records for config A (defaults, one slot), 2026-11-02T08:03:10Z to 08:03:49Z |
| [probe-par4.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-concurrent-agent-sessions-2026/probe-par4.json) | Raw records for config B (`OLLAMA_NUM_PARALLEL=4`), 08:04:54Z to 08:05:38Z |
| [ps-check.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-concurrent-agent-sessions-2026/ps-check.json) | The `/api/ps` response quoted above, with the server environment that produced it |
| [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-concurrent-agent-sessions-2026/method.md) | Host, versions, run order, and what was deliberately not measured |
| [raw-records-manifest.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-llm-concurrent-agent-sessions-2026/raw-records-manifest.json) | SHA-256 and byte counts of the research-stage files, so a rerun can be compared byte for byte; `ps-check.json` was recorded afterwards in the write run and its hash is in the review record rather than this manifest |

To repeat the default-configuration cells on your own box, keep the script in a scratch directory of your choosing and give it a deadline in epoch seconds:

```
OLLAMA_PROBE_BASE=http://127.0.0.1:11434 OLLAMA_PROBE_LABEL=my-host \
OLLAMA_PROBE_OUT="$TMPDIR/probe-mine.json" \
OLLAMA_PROBE_DEADLINE=$(( $(date +%s) + 150 )) \
python3 probe.py
```

For the four-slot cell, start a second server with your own model and flags, point `OLLAMA_PROBE_BASE` at it, and run `python3 probe.py n4`, which replays N=4 twice and then N=1 as the baseline. Compare the second client's wall time against the first: if the N=2 pair finishes at the same time, your server has two or more usable slots; if the second finishes at roughly twice the first, it has one.

## What this does and does not establish

Measured on one host: with the shipped default of one slot, four concurrent agent-shaped requests serialised and the last one took 4.0x the single-request wall time; setting `OLLAMA_NUM_PARALLEL=4` on the same two-core box made each request 4.4x to 8.0x slower than the default server's 3256.9 ms single-request row (3.8x to 7.0x against that server's own 3753.9 ms baseline) rather than faster; every request still returned HTTP 200.

Not measured, and not claimed: GPU serving of any kind, a real coding model generating hundreds of tokens, tool-calling payloads, throughput in tokens per second, memory high-water marks, and any comparison between Ollama and llama.cpp beyond their documented flag semantics. The absolute latencies here describe a two-vCPU host running a 397 MB model with a 64-token generation cap; your numbers will differ, and the shape — queueing at the default, contention when slots exceed cores — is what this article asks you to check rather than assume. For the wider comparison of engines and their parallel-request handling, see [vLLM vs Ollama in production](https://baeseokjae.github.io/posts/vllm-vs-ollama-production-2026/) and [local model serving frameworks](https://baeseokjae.github.io/posts/local-ai-model-serving-frameworks-2026/); for the multi-agent side, [running local AI agents](https://baeseokjae.github.io/posts/local-ai-agents-guide-2026/) covers what each session does with the model it gets.
