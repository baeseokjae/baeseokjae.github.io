# Method: prompt-prefix cache invalidation probe

## What was run
First-party measurement, 2026-11-14 18:04:39–18:10:30 UTC, against the local Ollama
server on the same host that produced this article's evidence. No network, no
credentials, no paid API. Raw records: `results.jsonl` (10 requests). Environment:
`env.json`. Derived table: `summary.json`. Scripts: `probe.py`, `probe2.py`.

## Fixture (deterministic, no sampling)
- System block: 25 numbered `Policy line NNNN: ...` lines (~1.9k chars).
- Tool registry: 6 terse JSON function definitions (~1.7k chars).
- Conversation: 4 scripted user turns; each turn appends the next user line to the
  same history, so turn N's prompt is a strict prefix extension of turn N-1's prompt.
- Server-reported prompt size: 941–993 tokens. `num_predict=3`, `temperature=0`,
  `seed=42`, `raw=true`, `keep_alive=30m`.

## Variants
| label | variant | per-turn mutation |
|---|---|---|
| a  | append_only | none: system block + registry fixed, history appended |
| b  | timestamp_top | `Session started <ISO8601-with-microseconds>` prepended to the system block, regenerated each turn (+31 server-reported prompt tokens, 946->977 at turn 1 and 962->993 at turn 2; 44 characters, and digit sequences tokenise inefficiently) |
| c  | tools_permuted | registry re-serialised once with a shuffled JSON key order, then held constant |
| d  | tools_permuted_per_turn | registry re-serialised with a *different* shuffled key order on every turn |
| a2 | append_only (repeat) | repeat of (a) after the first sweep, to expose host drift |

Turn indexes are identical across variants; content is identical except the named
mutation. `raw=true` means no chat template is applied, so the sha256 of the exact
prompt string is a faithful prefix fingerprint (`results.jsonl: prompt_sha256`).

## Why variants were not interleaved
Ollama holds the evaluated prefix per loaded slot. Interleaving variant requests
would overwrite that prefix and manufacture the miss being measured, so each
variant's turns were sent consecutively. Cost of that choice: cross-variant
comparison carries host drift, which is why only classification is asserted.

## Cache-hit classification
The server did not return `prompt_eval_cached_count` in any of the 10 responses
(the 11 response keys are listed in `env.json`). Classification therefore uses
`prompt_eval_duration`: a hit re-uses the evaluated prefix and prefills at
300–1,100 tokens/s; a cold prefill of the same ~950-token prompt runs at
11–38 tokens/s. Observed separation: hits 0.88–2.96 s, misses 11.88–88.14 s
(floor of 4.0x between the slowest hit and the fastest miss). No threshold in
the 3–10 s band changes any label.

## Known limitations
1. Single host, 2 vCPU, shared with the blog automation pipeline. Five turn-1
   cold prefills of the same fixture (941–977 server-reported tokens, four
   distinct prompt hashes) measured 13.20 s, 25.19 s, 34.53 s, 87.90 s and 88.14 s
   in the same sweep — a 6.7x spread. Absolute seconds and any ratio derived from
   them are host- and load-dependent; only hit/miss is reported as a finding.
2. One repeat per variant (two for append_only). Within-variant repeat agreement is
   3.49x on the cold turn, far above the 10% band, so no per-turn ratio is quoted.
3. Three turns were planned; two were executed inside the attempt deadline. The
   multi-turn cost curve is stated as arithmetic over the measured per-turn cost,
   never as a measured cumulative.
4. Engine-internal cache policy (slot count, eviction, `--cache-reuse` behaviour)
   was not inspected in source. The finding is behavioural, on this version only.
5. `prompt_eval_cached_count` absent is a property of this server build; other
   builds may return it, which would make the token split directly readable.
