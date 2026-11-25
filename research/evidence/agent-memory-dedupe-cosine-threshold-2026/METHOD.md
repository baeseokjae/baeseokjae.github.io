# EXP-MEMDEDUPE-THRESHOLD-2026-11-10 — method

## Question
At write time, can a cosine-similarity gate tell a duplicate memory from a memory that differs by
one critical token (number, region, API version, environment word, primary/replica, flag polarity)?
And what happens to duplicate capture when the threshold is raised to stop the false merges?

## Fixture (40 pairs, hand-written, widen-40-v1)
- 16 `paraphrase` pairs — same fact, different wording. A gate SHOULD merge these.
  Two per category: port, TTL, region, retry count, retention, endpoint/API version,
  primary-vs-replica, feature flag.
- 16 `critical` pairs — identical sentence except one critical token. A gate MUST NOT merge these.
- 8 `control` pairs — unrelated topics. A gate MUST NEVER merge these.
Every pair carries a one-line provenance note in `pairs.json` (`provenance`) explaining why a memory
layer would hold both. Categories were fixed before the first embedding call; no pair was added,
removed or reworded after seeing a score.

## Runner
`run_experiment.py` (stdlib only) posts all 80 texts per encoder to a local Ollama daemon
`POST /api/embed` in one batch, computes cosine on the raw returned vectors, then derives:

1. Pair table: per pair, per encoder, cosine + whether the token guard passes.
2. Threshold sweep: tau = 0.80 to 0.995 in 0.005 steps, plus 0.999. Per tau and encoder:
   duplicate capture (paraphrases >= tau, of 16), false merge (critical pairs >= tau, of 16),
   controls merged (of 8), precision, recall, F1.
3. Store arm: a 30-fact store (the `a` side of the 16 critical pairs + the `a` side of 14
   paraphrase pairs) receives 30 writes — 14 paraphrases (true duplicates) and 16 critical
   variants (distinct facts). Each write is compared to everything already stored; if
   max cosine >= tau it is dropped. Reported per tau: store size after, duplicates collapsed
   (of 14), distinct facts lost (of 16).
4. Guard arm: merge only if cosine >= tau AND the critical-token multiset of both texts is
   identical. Critical tokens = numbers, `/api/vN`, region codes (`xx-name-N`), environment words
   (production/prod, staging/stage, development/dev, normalised), `primary`/`replica`,
   `enabled`/`disabled`/`on`/`off`, `port`. Reported per tau: false merge with guard,
   duplicate capture with guard, and merges blocked by the guard.

## Reproduction
`run.sh` captures `ollama --version`, `nproc`, `free -m`, and `ollama show <model>` for each encoder
(architecture, parameter count, context length, embedding length, quantization), then runs
`run_experiment.py`. Raw outputs: `results.jsonl` (per-call and per-pair records),
`sweep.csv` (the matrix), `summary.json` (derived per-encoder summary), `pairs.json` (fixture +
provenance). `CHECKSUMS.txt` hashes every artifact.

## Environment actually used
Ollama 0.20.3, 2 vCPU, 11.9 GiB RAM, F16 weights, this host, 2026-11-10 ~08:54 UTC.
Encoders: all-minilm:latest (384-d, 22.7M params, 512 ctx), snowflake-arctic-embed:33m
(384-d, 33M params, 512 ctx), nomic-embed-text:latest (768-d, 137M params, 2048 ctx).
Batch wall time for all 80 texts: 0.84 s / 2.93 s / 16.10 s; `prompt_eval_count`
1120 / 1120 / 1082 — i.e. no input hit the context limit, so `truncate` (default true in
`/api/embed`) never fired.

## What this method cannot show
- Embedding calls are prompt-free. `nomic-embed-text-v1.5` documents mandatory task prefixes
  (`search_document:`, `search_query:`, `clustering: ... remove semantic duplicates`);
  `snowflake-arctic-embed` documents a `query:` prefix for queries. Numbers here describe the
  un-prefixed call shape only and must not be read as those models' best-case behaviour.
- 40 single-sentence facts in infra vocabulary, one host, one tokenizer per model, no long
  documents, no multi-sentence memories, no temporal/decay features, no vendor dedupe code read.
- Cosine on raw vectors; no normalisation, whitening, PCA or per-store calibration was applied.
- The store arm reuses the pair fixture rather than sampling a real agent transcript.
