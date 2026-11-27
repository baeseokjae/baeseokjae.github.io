# Method — deterministic truncation survival matrix (Part A)

Run: 2026-11-22T17:32Z, host `a1-instance`, Linux 6.17.0-1019-oracle
(aarch64, glibc 2.39), Python 3.12.3, single CPU-only host, stdlib only.
Script: `truncation_survival.py` (stdlib only). Results: `part_a_results.json`.
Reproduce: `python3 truncation_survival.py part_a_results.json` (~0.07 s).
The run's own environment block, as recorded in the results file:

```json
{"python": "3.12.3", "platform": "Linux-6.17.0-1019-oracle-aarch64-with-glibc2.39",
 "host": "a1-instance", "note": "single host, CPU-only, stdlib-only; no model"}
```

No vCPU count was recorded by the run, so none is stated here.

## Fixture
`build_payload()` emits deterministic line-oriented log text
(`2026-11-22T17:MM:SSZ INFO [service] step=… elapsed_ms=… msg="…"`) until the
payload reaches 400,000 characters, then inserts one evidence line at a
requested fraction of the payload, snapped forward to a line boundary:

    EVIDENCE-MARKER-7f3a build_id=8412 shard=blue-17 status=FAILED

Fractions used: 0.0, 0.25, 0.5, 0.75, 1.0. Observed payload size 400,110 chars
/ 400,110 bytes (ASCII); the 110-character overshoot is the last full line plus
the evidence line. Fixture SHA-256 per fraction is in `part_a_results.json`.

## Policies (all at a 20,000-character budget)
| policy | what it keeps |
|---|---|
| head-N | first 20,000 chars |
| tail-N | last 20,000 chars |
| head+tail | 10,000 chars from each end, joined by a 14-character separator `\n[...snip...]\n` (newline + 12 characters + newline); 20,014 chars emitted |
| middle-out | a 20,000-char window centred on the payload midpoint |
| match-centred | a 20,000-char window centred on the first line matching `ERROR\|FATAL\|Exception` |

The separator is not charged against the budget: `head_tail()` concatenates
`text[:10000]`, the separator and `text[-10000:]`, so the emitted string is
20,014 characters for every input that needs truncation. `kept_chars` in
`part_a_results.json` records 20,014 on all five head+tail rows, and
`marker_present` is `true` on all five. The other four policies emit exactly
20,000 characters.

## Scoring
`evidence_survived` = the exact evidence line is a substring of the emitted
string. `kept_spans` records the character ranges of the original that survive;
for the four substring policies the span is computed analytically at slice
time, and for head+tail the two emitted chunks are recorded separately.

## What this does not measure
- No tokenizer, so character budgets ignore token-boundary effects.
- No model call: Part B (qwen3:0.6b quote task) was not run in this stage; no
  model result is claimed in the brief.
- One fixture shape only; real grep/test output has different line-length and
  locality structure.

## Source verification
`codex_truncate.rs` = `openai/codex` @ `104d2564181d8eb4e67d0c92005f3ab1052051d4` (2026-11-22).
`ollama_prompt_v0.20.3.go` = tag `v0.20.3` (`8c8f8f3450d39735355fc6cd7f2e436c8aa42ab1`).
Ollama docs fetched as `.md` twins (`docs.ollama.com/faq.md`, `/api/generate.md`).
Every excerpt in the brief is asserted to be a verbatim substring of the saved
file at build time (`build_brief.py`).

## Revision log
- 2026-11-22T17:32Z — first run; this note as originally written.
- 2026-11-22 (correction, Writer round 1): the head+tail row said "12-char
  `[...snip...]` marker (20,012 chars emitted)". The code and the results file
  disagree with that text: the separator is the 14-character string
  `\n[...snip...]\n` and `kept_chars` is 20,014 on all five head+tail rows, as
  the article's own separator paragraph already stated. The row and the host
  line were corrected to match the recorded run. `truncation_survival.py`
  (SHA-256 `51b61129…`) and `part_a_results.json` (SHA-256 `b2c1e98f…`) were
  **not** modified: the historical raw output is preserved as produced, and a
  fresh re-run in an isolated scratch directory on 2026-11-22 reproduced all 25
  rows, the survival matrix and the per-fixture hashes exactly.
