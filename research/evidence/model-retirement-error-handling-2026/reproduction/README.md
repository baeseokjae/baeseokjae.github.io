# Reproduction layout — model-retirement-error-handling-2026

This directory is the runnable copy of the article's first-party check. Everything here is
original to this article: no provider downloads, no credentials, no paid calls.

## Run it

```
cd research/evidence/model-retirement-error-handling-2026/reproduction
python3 compare.py
```

Standard library only (Python 3). The script starts a `ThreadingHTTPServer` bound to
`127.0.0.1:0`, serves six frozen envelopes from `envelopes/`, replays two retry policies
against each of them, and writes:

- `out/classification.csv` — one row per envelope: label, prediction, decision field, body sha256
- `out/retry-policy-compare.csv` — one row per (policy, envelope): server requests, client attempts,
  wall ms, final status
- `out/results.json` — full run record incl. per-event server log and the derived summary

The cover figure is regenerated with `python3 scripts/make_cover.py <path>.png`; it reads the class
assigned to each envelope from `out/classification.csv` and the request counts from
`out/retry-policy-compare.csv`, and plots nothing that is not in those two files.

## What is frozen here

- `envelopes/*.json` — six envelopes: three verbatim from vendor documentation or vendor source,
  three synthesised to spec as control rows. Each file carries `verification` and `source_url`.
  Byte-identical to the copies replayed in `../run-2026-11-01/envelopes/` (hashes in
  `../verification-2026-11-25.json`).
- `labels.json` — the hand-assigned classes, with `frozen_at` = 2026-11-01T16:19:12.389Z, written
  before any run. `labels.sha256` is its hash; `compare.py` re-hashes the file and derives
  `labels_frozen_before_run` from `frozen_at` versus the run start instead of asserting it.

## Dates

- Measurement windows reported in the article: 2026-11-01 (classification) and 2026-11-19T08:45:56Z
  –08:46:02Z (two-policy retry comparison). The 2026-11-19 run record is kept untouched in
  `../retry-compare-2026-11-01/`.
- 2026-11-25: this layout was created and the same script re-executed from it. Result:
  `verification-2026-11-25.json` — same six rows, 3/3 verbatim rows correct under the two
  in-scope classes, 6/6 across all rows, `retry_all` 3 and 3 requests, `no_retry_4xx` 1 and 3.

## Scope

No live provider API was called; wall times reflect a fixed 200 ms doubling backoff against a
loopback server. Six rows is a small fixture — the numbers are a property of this fixture, not
an accuracy claim about production traffic.
