# Method: agent-memory-similarity-threshold-drops-constraints-2026

Date: 2026-11-14T19:54:55Z
Host: linux 6.17.0-1019-oracle, 2 vCPU class VM, local Ollama at 127.0.0.1:11434 (/api/embed).
Embedders (from `ollama list` at run time): all-minilm:latest (384 dims, digest 1b226e2802dbb772b5fc32a58f103ca1804ef7501331012de126ab22f67475ef), snowflake-arctic-embed:33m (384 dims, digest e8db018629b498a0a1a2eadbe8ab29477c1d7c4b6ba8ff2a69b0a6ed193713be).
Command: `python3 research/evidence/agent-memory-similarity-threshold-drops-constraints-2026/threshold_probe.py > probe_results.json`
Fixture: 12 facts (6 constraints: 2 prohibitions, 2 requirements, 1 exception, 1 exclusion; 6 descriptive) and 6 queries,
4 of which target a constraint (gold = a constraint fact), 2 descriptive. Synthetic; no customer data.
Scoring: exact cosine over full returned vectors (no ANN index). Threshold sweep 0.20-0.90, step 0.05 (15 thresholds).
Determinism: fixed texts and fixed model digests; re-runs reproduce scores to 3 decimals.
Not claimed: an effect size, generality across embedders/fixtures, or any vendor default threshold.

Correction note (2026-11-14, review D4-D6): the sweep range and the fixture-composition counts above were
restated to match the executed run record (15 thresholds, 0.20-0.90; 2 prohibitions c1/c3, 2 requirements c2/c5,
1 exception c4, 1 exclusion c6). No score, fact text or query text was changed, and probe_results.json bytes are
the original run output.
