# Method — tool-call repeatability probe (bounded, r1)

Reproduce with the files in this directory. This is the method as actually run on
2026-11-15, including its deviations from the original plan.

## Environment

- Host: CPU-only Linux, 2 vCPU, 11 GB RAM, no GPU. SHARED with a concurrent stage run
  for the entire measurement window, so wall time is recorded but not interpretable.
- Server: Ollama 0.20.3 (`GET /api/version`, 2026-11-15T13:23Z).
- Model: `qwen3:0.6b`, digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`,
  Q4_K_M, 751.63M params (from `GET /api/tags`).
- `qwen2.5:0.5b` (digest `a8b0c5157701...`, Q4_K_M) was present but **not measured**.

## Request under test

`POST http://127.0.0.1:11434/api/chat`, `stream=false`, `think=false`,
`num_predict=80`, `num_ctx=4096`, `seed=42`, one tool `stat_path`
(`path` string, `mode` enum stat|read|hash, `max_bytes` integer; required path+mode),
instruction: "Check whether docs/config.md exists and get its hash. Use the tool."

Conditions: S1 single turn temp 0.0 · S2 one prior turn (user, assistant tool_call,
tool result) temp 0.0 · S3 repository path listing prefix (~1,220 tokens of the
1,420 total prompt tokens; 85 lines / 2,650 characters in `repeat_probe.py`) temp 0.0 ·
S4 single turn temp 0.7.

## Run

```
export PROBE_DIR=$PWD PROBE_BUDGET_S=118 PROBE_MAX_ROUNDS=6 \
       PROBE_MODEL=qwen3:0.6b PROBE_ORDER=S3,S4,S1,S2
timeout 150 /usr/bin/python3 repeat_probe.py
```

Three invocations with internal budgets 165 s / 150 s / 118 s and an external
`timeout` guard. Condition order was rotated between invocations so no condition
could end with zero samples. Each call is appended to `run.jsonl` and flushed
before the next call starts, so a cut cannot lose completed records.
No signals were sent to any process.

## Scoring

Per call, from `message.tool_calls[0].function.arguments`:
- **semantic form**: `sha256(json.dumps(args, sort_keys=True))`
- **byte form**: `sha256(json.dumps(args))`, plus the observed `key_order`

A condition is byte-identical N/N only if one `sha256_byte` covers all N calls.

## Result (13 calls, 0 errors)

| cond | N | sem distinct | byte distinct | byte identical | key orders | prompt_eval_count |
|------|---|--------------|---------------|----------------|------------|-------------------|
| S1 | 4 | 1 | 1 | 4/4 | (path,mode)×4 | 197 |
| S2 | 3 | 1 | 2 | 2/3 | (mode,path)×2, (path,mode)×1 | 268 |
| S3 | 3 | 1 | 2 | 2/3 | (path,mode)×2, (mode,path)×1 | 1420 |
| S4 | 3 | 1 | 1 | 3/3 | (path,mode)×3 | 197 |

All 13 calls: exactly one tool call, name `stat_path`, values
`path=docs/config.md, mode=hash`, no `max_bytes`. Argument values never drifted.

## Deviations from the original plan

1. **N=20 per condition (80 calls) was not run.** The attempt budget does not hold
   20-40 minutes of wall time on this host. The bounded design above replaced it and
   is disclosed in the brief and must be disclosed in the article.
2. **The host was not idle**, so no latency or throughput claim is offered.
3. **Second model dropped** in favour of completing four conditions on the primary
   model. No two-model claim is made.
4. **A prior, interrupted run's single S1 record** (`06-run.jsonl`, started
   2026-11-15T12:33:48Z, byte `807e8335...`, semantic `b5ffe708...`) was reused as one
   extra S1 observation because its hashes match this round's dominant S1 form. It is
   not merged into the S1 count of 4.

## Cached vendor documentation (not reader artifacts)

The citation check used live fetches of the vendor pages named in the article. Two
plain copies were kept while drafting (`ollama-api.md` from the repository `docs/`
directory, `vllm-reproducibility.html` from docs.vllm.ai) and one was saved from the
rendered docs site (`ollama-modelfile.md`); that rendered copy is not a copy of the
cited repository blob, so the Modelfile citation was re-checked against
`https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx` directly (HTTP 200,
quote verbatim) rather than against the saved file. All three copies now live in
`research/cache/agent-tool-call-repeatability-2026/`, outside this reader-facing
evidence directory. They are third-party documentation, are not offered as
downloads, and are not listed in the review receipt's `public_artifacts`. Only the
first-party files in this directory are reader artifacts.

## Limits of this method

Key order is scored on the arguments object **as the `/api/chat` JSON response
serialises it**. This run cannot separate a model-side token-order difference from a
server-side parse-and-reserialise step. With N=3-4 the counts cannot estimate a flip
rate. The fixture instruction has one obviously correct call, so argument-value drift
under ambiguity is untested.
