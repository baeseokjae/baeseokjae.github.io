# Method - local-llm-concurrent-agent-sessions-2026

Measured on 2026-11-02 (UTC) on the job host. This is a **CPU-only, single-host,
small-model** probe. It is not a throughput benchmark and does not transfer to GPU
serving.

## Host and versions
- Host: 2 vCPU (aarch64 Neoverse-N1), 11 GiB RAM, no GPU, Linux 6.17.0-1019-oracle.
- `ollama version is 0.20.3` (recorded from `ollama --version`).
- Model: `qwen2.5:0.5b` (a8b0c5157701, 397 MB), `num_ctx=2048`, `num_predict=64`,
  `temperature=0`, `seed=7`, `keep_alive=5m`, one fixed 59-token prompt.
- Request: single non-streaming `POST /api/generate` per virtual client, one call per
  client per cell. Prompt text is in `probe.py`.

## Configurations
1. `probe-default.json` - the system `ollama serve` with **no `OLLAMA_*` variables set**
   (verified with `env | grep '^OLLAMA'` returning nothing). Per the vendor FAQ this
   means `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_QUEUE=512`.
2. `probe-par4.json` - a second server on 127.0.0.1:11435 started as
   `OLLAMA_HOST=127.0.0.1:11435 OLLAMA_NUM_PARALLEL=4 OLLAMA_CONTEXT_LENGTH=2048    OLLAMA_MODELS=/usr/share/ollama/.ollama/models ollama serve`.

## Load and repeat
- Cells: N in {1,2,4} concurrent clients, started from a `threading.Barrier` so all
  requests enter the server within the same instant.
- Repeats: default config N=1 twice, N=2 once, N=4 twice; parallel=4 config N=4 twice
  and N=1 once (in that order, warm server). Run order is in the JSON `cells` array.
- A warm-up request precedes each configuration; its latency is not counted as a cell.

## Measured / not measured
- Measured: client-side wall time per request (ms), HTTP status, verbatim error body,
  response character count, `eval_count`, `done_reason`.
- Also recorded: `/api/ps` `context_length` after load.
- NOT measured: GPU serving, real coding-agent traffic, tool-calling payloads, context
  truncation or tool-argument truncation (none occurred in these cells; `done_reason`
  was `length` because of the `num_predict=64` cap we set, which is our cap, not a
  concurrency effect), token throughput, memory high-water mark.
- `llama-server` was not installed on this host, so the llama.cpp claims in the brief
  come from its documentation only and are labelled as such.

## Timestamps and uncertainty
- default-env probe: 2026-11-02T08:03:10Z -> 2026-11-02T08:03:49Z
- parallel=4 probe: 2026-11-02T08:04:54Z -> 2026-11-02T08:05:38Z
- Uncertainty is the observed spread across repeats, reported per cell in the JSON.
  Two repeats per cell is small; do not present these as p95 confidence intervals.
