# Method — agent-memory-multi-hop-recall-2026

Run date: 2026-11-24 (UTC). All figures in the article come from this run's JSON files in
this directory. Nothing here is a vendor or benchmark score.

## Question

Can a small local memory store return both facts that a two-hop question needs, and where
does the failure sit: the store, the ranking cut, or the reader?

## Host

- 2 logical CPUs, aarch64, no GPU; 12,213,612 KiB RAM; Ollama 0.20.3 on 127.0.0.1.
- Python 3 standard library only (`json`, `math`, `urllib`). No numpy, no FAISS, no ANN index.
- Model digests as reported by the local daemon, recorded in `ollama-tags.json` and in this
  file (`summary.json` was not written by this run):
  - `all-minilm:latest` 1b226e2802db, 384 dimensions
  - `snowflake-arctic-embed:33m` e8db018629b4, 384 dimensions
  - `nomic-embed-text:latest` 0a109f422b47, 768 dimensions
  - reader `qwen2.5:0.5b` a8b0c5157701

## Fixture

`fixture.json` is generated deterministically by `multihop_probe.py` (no RNG, no seed
needed): 40 invented services, 8 regions, 8 teams, 120 facts of 7-12 words (mean 9.2).

| fact kind | count |
|---|---|
| service → region | 40 |
| service → team | 40 |
| region → database | 8 |
| team → on-call rotation | 8 |
| distractor: region → cost centre | 8 |
| distractor: team → incident queue | 8 |
| distractor: service → language | 8 |

Questions: 20 two-hop (12 database-through-region, 8 rotation-through-team) in three
phrasings, and 20 single-hop controls (10 region, 10 team). Each question carries the two
fact ids its answer needs (`fact_hop1`, `fact_hop2`) and one gold string.

## Arms

1. `top5` — cosine over the question vector, five nearest facts.
2. `top20` — twenty nearest facts.
3. `decomp` — one `/api/generate` call per two-hop question asking the reader model to split
   it into sub-questions (max 60 tokens, temperature 0, seed 42). Lines longer than 8
   characters are kept, at most 4. Each sub-query is embedded and retrieved at k=5; the
   union (deduplicated, first-seen order, capped at 10 facts) is the arm's retrieval set.
   This is a single rewrite pass, not an iterative retrieve-then-rewrite loop.
4. `oracle` — exactly the two gold facts (one for single-hop controls), in hop order.

## Reader and grading

Prompt: a fixed instruction to answer only from the FACTS list, reply with the value only,
and reply `UNKNOWN` if the facts do not contain it. `temperature: 0`, `seed: 42`,
`num_predict: 16`. Tokens recorded are the daemon's `prompt_eval_count` for that call.

Grading rule (implemented in `normalize_answer` / `grade`, not applied by eye): lowercase
the answer, replace every non-alphanumeric character with a space, remove all whitespace,
and check whether the normalised gold value is a substring of the normalised answer. The
rule is deliberately lenient about surrounding words and strict about the value itself.

## Coverage

`both_in_top5` / `both_in_top20` in `results-retrieval.json` are true when every required
fact id for that question is in the retrieved id list. Ranks are recorded to depth 50; a
null `hop2_rank` means the fact was not in the top 50.

## Deviations from the plan in the research file

- The plan says SQLite rows; the store is an in-process list of 120 vectors. No SQLite was
  used, so no database behaviour is measured.
- The plan lists a reader grid with two reader models. **No reader rows exist for this run.**
  The reader stage did not finish inside the run's time budget: the probe writes
  `results-reader.json` after every completed row and again at the end of the stage, and
  neither file exists here, so this directory holds no answer, prompt-token or per-call
  latency record and the article reports no answer accuracy. The only generation timings
  recorded are the 20 decomposition rewrites in `decomposition.json` (0.88-4.6 s each,
  47.2 s in total), which are rewrites and not answers over retrieved facts.
  `qwen2.5:0.5b` was used only as the decomposition rewriter.
- `results-decomp-coverage.json` holds the decomposition arm's retrieval coverage, produced
  with this probe's `embed`/`rank` functions and the union rule below, without reader calls.
- The plan's "three phrasings" were generated per question index, not randomised across
  question types; the phrasing distribution is fixed and recorded in `fixture.json`.
- Latency is wall-clock per call on an otherwise idle host and includes Ollama request
  overhead.

## Reproduce

```
python3 multihop_probe.py --out ./out --reader qwen2.5:0.5b --deadline-epoch $(( $(date +%s) + 5400 ))
```

Files written: `fixture.json`, `results-retrieval.json`, `decomposition.json`,
`results-reader.json`, `summary.json`. This run produced the first three. The reader stage has
to finish for the last two to be written, and the default 900 s budget stops that stage 240 s
before the deadline, so pass `--deadline-epoch` on a shared host.

Two runs on different hosts will not match on
latency and may differ on a few ranks if the daemon or model digests differ; the file
records the digests the run used.
