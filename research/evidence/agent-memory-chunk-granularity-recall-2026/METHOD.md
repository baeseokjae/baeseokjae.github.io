# Method: chunk granularity vs. retrieval (agent-memory-chunk-granularity-recall-2026)

Measured 2026-11-15T00:46:10Z on the task host. Localhost only, no network, no credentials, no paid API.

## Reproduce

    python3 chunk_probe2.py fixture.json results2.json

`chunk_probe.py` is the earlier sweep (hits only, 66 s); `chunk_probe2.py` additionally records the
rank of each needle sentence to depth 8 and reports `both_in_top8` (54 s). Both need Ollama serving
the three models below at http://127.0.0.1:11434. Nothing else is required.

## Fixture

8 invented documents x 7 sentences (456-500 chars per document, 52-99 chars per sentence).
8 single-fact questions (one needle sentence per document) and 5 two-fact questions whose two
required sentences sit on opposite sides of a 3-sentence window boundary.

## Granularities and embedders

* whole_document: 8 vectors; three_sentence: 24 vectors (windows 1-3, 4-6, 7); single_sentence: 56 vectors.
* all-minilm:latest 384-d digest 1b226e2802db; snowflake-arctic-embed:33m 384-d digest e8db018629b4;
  nomic-embed-text:latest 768-d digest 0a109f422b47. Ollama 0.20.3, F16, 2 vCPU / 11 GiB.
* Scoring: cosine on L2-normalised /api/embed vectors, deterministic full sort, no sampling, no generation.

## Known deviations to carry into the article

* No task-instruction prefixes were sent. nomic-embed-text-v1.5's model card requires
  `search_document:` / `search_query:`; Ollama's own library example omits them. nomic's absolute
  numbers are therefore not a fair model comparison.
* `prompt_eval_count` was not recorded, so token counts are not measured; only characters are.
* The 5 two-fact pairs straddle a window boundary by construction: fine-granularity two-fact hit@1
  of 0 is a designed worst case, not an estimate.
