# Method: retried tool call, duplicate side effects (local fault injection)

Run: 2026-11-01T00:48:20Z .. 2026-11-01T00:50:31Z, single Linux host, Python 3 / SQLite,
loopback only. No model calls, no vendor endpoint, no external network.

## Fixture
`tool_retry_fault_harness.py` starts a ThreadingHTTPServer on 127.0.0.1 with one POST /tool
endpoint. The endpoint writes an append-only row to `effects` (SQLite) and stores the
(response status, body) under the request's `Idempotency-Key`. Fault modes:

- `none` - commit, reply 200.
- `error_502_before` - reply 502 without touching the ledger.
- `timeout_before` - sleep past the client timeout, never commit.
- `timeout_after` - commit first, then sleep past the client timeout. The client cannot
  distinguish this from `timeout_before`.

Client timeout 0.12 s, server late reply 0.35 s, at most 4 attempts per trial.

## Policies
- `a_blind_new_key`: retry, regenerating both the tool call id and the Idempotency-Key.
- `b_reuse_key`: retry with the original tool call id as the Idempotency-Key.
- `c_arg_hash_dedupe`: retry with fresh keys; the server dedupes on (tool, sha256(args)) and
  answers 200 with the id of the effect it already wrote, instead of inserting a second row.
- `d_no_retry`: fail closed after the first attempt.

## Matrix
50 trials per policy per fault mode (4 x 3 x 50 = 600) plus a 50-trial no-fault control with
the blind policy = 650 rows in `ledger.csv`, one row per trial with the attempt trace.

## Controls
1. No-fault cell must commit exactly one effect per trial.
2. The pre-commit stall must produce zero duplicates under every policy. If it does not, the
   fault injector is wrong.

## Cost proxy
Characters resent per trial: the 1,920-character payload on the first attempt plus the payload
and a fixed 1,800-character transcript allowance on each retry. The payload is
`("You are an agent. Transcript: " + "lorem ipsum dolor sit amet " * 70)`, which is 30 + 70 x 27
= 1,920 characters; the harness line's `[:2000]` slice never truncates it, and the ledger's
`prompt_chars_resent` column records 1,920 / 5,640 / 13,080 for 1 / 2 / 4 attempts. This is a
character count, not a token count and not money; no tokenizer or vendor price is applied.

## Known deviations
- The stall is applied to the first attempt only. An earlier pass stalled every attempt, so no
  retry ever observed a stored response; that pass is discarded and not reported.
- Duplicate detection reads the ledger, not the client's view, so `d_no_retry` can show zero
  duplicates while leaving the effect unconfirmed.

## Reproduce
    python3 tool_retry_fault_harness.py --out ledger.csv --faults 50 --db "$TMPDIR/effects.sqlite"
