# EXP-OLLAMA-SLOTS-2026-11-04 — method

Run window: 2026-11-04T00:33:20Z .. 2026-11-04T00:35:37Z (UTC, single session).

## Host
- `ollama version is 0.20.3` (release v0.20.3 published 2026-04-07 per GitHub release metadata)
- `Linux 6.17.0-1019-oracle aarch64`, `nproc` = 2, `free -m` total 11927 MiB
- CPU-only: `/api/ps` reports `size_vram: 0` in every config
- Model: qwen2.5:0.5b, Q4_K_M, 494.03M parameters, blob digest a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67
- Ollama defaults confirmed by the server's own log: `Ollama version 0.20.3`, `NumThreads:2`, config A untouched (default `OLLAMA_NUM_PARALLEL` absent -> compiled default 1)

## Configs
- A: the pre-existing server on 127.0.0.1:11434, environment untouched (vendor default)
- B: dedicated instance on 127.0.0.1:11500, `OLLAMA_NUM_PARALLEL=2 OLLAMA_MAX_QUEUE=1 OLLAMA_KEEP_ALIVE=120s OLLAMA_MODELS=/usr/share/ollama/.ollama/models`
- C: dedicated instance on 127.0.0.1:11501, same as B with `OLLAMA_NUM_PARALLEL=4`

Server log lines for B/C are saved as `server_b_lines.txt` / `server_c_lines.txt`
(`Parallel:2 ... KvSize:8192` and `Parallel:4 ... KvSize:16384`).

## Request shape
`POST /api/generate`, `stream: false`, `options: {temperature: 0, seed: 42, num_predict: 64}`, one fixed English prompt
(5-line PostgreSQL backup checklist). The server stopped at 46 output tokens
(`done_reason: length` is not enforced by the model, but every request produced `eval_count: 46`), so all
per-request token rates below are `eval_count / eval_duration` computed from the response body itself.

Timing fields are Ollama's own: `total_duration`, `load_duration`, `prompt_eval_duration`, `eval_duration`
(all nanoseconds, documented at https://docs.ollama.com/api/generate).

Derived: `queue_wait_s = total_duration - (load_duration + prompt_eval_duration + eval_duration)`.

`load_duration` is non-zero (0.197-1.04 s) even when the model is already resident, so a naive
`total - eval` diagnostic overstates waiting; all three components must be subtracted, as done here.

## Repetitions
5 labelled cells, 17 measured batches, one warm-up request per cell before measurement (not recorded):
A-n1 x4, A-n2 x4, B-n1 x2, B-n2 x4, C-n4 x3. Threads synchronize on a `threading.Barrier` so the N
requests leave together.

Cold batches excluded from the reported summaries and marked `cold=True` in `summary.csv`:
B-n2 rep 0 (prompt cache cold: one request shows `prompt_eval_duration` 1.58 s) and C-n4 reps 0-1
(model/KV allocation still warming; aggregate throughput 9.6 and 11.2 tok/s against 20.6 in the warm rep).

## Not claimed
- No GPU numbers: this host has none (`size_vram: 0`). GPU slot behaviour is explicitly out of scope.
- No cross-model generalisation: one 0.5B Q4_K_M model, 2 cores, short 46-token generations.
- The 3-minute-per-attempt bound applied: whole measurement took 137 s.
