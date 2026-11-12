# Method — local-agent-turn-time-budget-2026 (research stage, 2026-11-08)

## What was attempted

A bounded single-stream prefill/decode measurement on the host this stage ran on.

- Host: 2 logical vCPUs, 11 GB RAM, Linux 6.17.0-1019-oracle (shared sandbox, other services resident).
- Backend: Ollama HTTP API, `POST http://127.0.0.1:11434/api/generate`, `stream:false`.
- Model artifact: `qwen3-vl:2b`, 2.1B params, `Q4_K_M`, 1,889,519,687 bytes,
  digest `0635d9d857d497aeadba3d7d27485746c50554446f9f6ec01ef39788221adbe`,
  modified 2026-11-03T16:12:51Z (from `/api/tags`).
- Request options: `num_predict: 48`, `num_ctx: 8192`, `temperature: 0`, `seed: 42`, `keep_alive: "10m"`.
- Fixtures: three prompts of different length (`short` ~32 prompt tokens, `medium`, `long`),
  3 repeats each. Two separate time limits applied to this run; see "Two limits" below.
- Derived rates, not server-reported headline numbers:
  `prefill_tps = prompt_eval_count / (prompt_eval_duration_ns / 1e9)`,
  `decode_tps = eval_count / (eval_duration_ns / 1e9)`.

## Two limits, both on the record

One run was governed by two different time limits, and the evidence keeps both:

- **Declared run budget: 110 s.** This is the deadline the stage was given for the measurement
  (`run_cap_s` 110 in the selection record), and it is the number the article quotes.
- **Script kill cap: 130 s.** The driver script this stage used was itself launched with a 130 s
  kill cap, a ceiling above the declared budget that ended the run once the budget was already
  spent and a slow request was still outstanding. The `provenance` field in both `runs.jsonl`
  records says exactly that: "killed by its 130 s cap before flushing runs.jsonl".

Neither number replaces the other: the 110 s figure is the budget the run was meant to fit in,
the 130 s figure is the hard stop that actually fired. Because the script buffered its records
until the end of the loop, no record was on disk at that point; the two surviving records were
recovered verbatim from the stage's own stdout and re-written with the provenance string quoted
above. Their measured fields (`wall_s`, `prompt_eval_count`, `eval_count`, `prefill_tps`,
`decode_tps`) are unchanged from the printed output and were not re-timed, edited or rounded in
this reconciliation.

## Result: rejected as noise

2 of 9 planned runs completed inside the deadline. Observed `decode_tps` 1.615 and 3.165
(96% spread), `prefill_tps` 3.781 and 228.859 (the first run includes cold model load).
Wall time for the same fixture and token counts: 79.8 s vs 16.9 s.

The selection's failure condition requires prefill and decode to be separated with under 10%
spread across three repeats. That gate is not met, so these numbers are **not** a baseline and
must never appear as a measured tokens/second figure. No GPU was measured; no cross-hardware
claim is possible from this host.

## Reproduce

The fixture and script are deterministic; the variance is the host, not the harness.
A rerun needs a quiet machine (no co-resident services) and a longer per-run cap so that
all 9 records flush to `runs.jsonl`. The script must write each record incrementally —
this attempt lost 7 records because records were only flushed at the end of the loop.

## Files

- `runs.jsonl` — the two records that completed (provenance field marks them as reconstructed
  verbatim from this stage's stdout after the script hit its cap before flush).
- `probe_generate.json` — a minimal `num_predict:4` response used to confirm the endpoint was
  live and fast (HTTP 200, 0.76 s) after an earlier request had stalled on model load.
- `raw-records-manifest.json` — file sizes and sha256 for every artifact, plus failed fetches.
