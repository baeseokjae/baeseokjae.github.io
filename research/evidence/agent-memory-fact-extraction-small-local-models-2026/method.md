# Method: local fact-extraction pilot (agent-memory-fact-extraction-small-local-models-2026)

Run date: 2026-11-21 (UTC). Host: Linux, 2 vCPU, 11 GiB RAM, no GPU. ollama 0.20.3.

## What was run
- Fixture: `research/evidence/agent-memory-fact-extraction-small-local-models-2026/fixture.json` — 16 authored turns (8 user / 8 assistant),
  19 ground-truth facts across 8 subjects, 8 distractor acknowledgements, 10 queries. The first 8 turns were used in this run.
- Scope rule: a fact or query counts only if all of its key tokens appear in the included turns' text,
  so denominators describe what was actually stated, not the whole fixture. 9 facts and 5 queries were in scope.
- Store arms: (a) one vector per raw turn, (b) two-turn sliding window, (c) facts extracted by
  qwen3:0.6b with prompt P1, (d) the same model with prompt P2, (e) facts extracted by qwen2.5:0.5b with P1,
  (f) turns + P1 facts scored by max. Encoder and k held fixed:
  snowflake-arctic-embed:33m (384-d), cosine, brute-force top-5.
- Extraction options: temperature 0, seed 42, num_predict 120, `think: false`. 24 calls in total (8 per extraction arm).
- Model builds, as reported by `/api/show`: `qwen3:0.6b` = GGUF Q4_K_M, 751.63M parameters; `qwen2.5:0.5b` = GGUF Q4_K_M, 494.03M parameters.
  These are two different Qwen generations, not two sizes of one family.
- Wall-clock cap: 185 s for all extraction calls; per-call records are appended to `raw-records.jsonl` before the next call,
  so a capped run is still complete evidence. Arms cut by the cap: none (last cumulative call time 129.8 s).

## Matching rule (reproduce exactly)
Normalise by lowercasing and collapsing every non-alphanumeric run to a space. A stored string contains a
fact when all of that fact's key tokens appear in the normalised string. A stored string counts as an acknowledgement
row when it contains a distractor acknowledgement after the same normalisation. `noise_rows` is that count;
`stored_rows` is the arm's row count, and the article reports the ratio per arm rather than a single rate, because
the denominators differ (8, 4, 12, 28, 16, 20).
Answerability@k means the top-k row contains the query's `expect_all` tokens. No hand audit was performed.

## Character metric (read this before quoting `mean_top5_chars`)
`mean_top5_chars` is `sum(len(row) for each of the 5 retrieved rows, for each of the 5 queries) / (5 * 5)`.
The denominator is k=5 whether or not five rows were retrieved, so the field is characters per retrieved row only for
arms that stored at least five rows. The top-5 prompt total quoted in the
article is five times that field: 365 (a), 685 (b), 230 (c), 50 (d), 60 (e), 260 (f).
Arm (b) is the exception: it stores four rows of 256, 160, 157 and 113 characters (686 in total), so its field is
686/5 = 137, its prompt total is 5 x 137 = 685, and its actual characters per retrieved row are 686/4 ~ 171.

## Reproduction
The scoring pass is reproducible from the published files: `fixture.json` holds the turns, facts and queries;
`raw-records.jsonl` holds the extracted items; `results.json` holds the per-arm fields. Re-embedding the stored rows
with snowflake-arctic-embed:33m and re-running the top-5 sort reproduces the answerability and character columns.
The driver script used here (`run_experiment.py`, stdlib + numpy + the local Ollama HTTP API) was scratch and is not
published with the article, so this is re-scorable rather than re-runnable end to end.

## Known gaps
- Full 60-turn / 40-query scale from the planning brief was not run: one qwen3:0.6b call costs 2-23 s on this host.
- No 20% hand audit of the matching rule, so recall is unvalidated (the article says so).
- One seed (42), one fixture, one host, one embedder; nothing here generalises to GPU serving or hosted extraction APIs.
