# Write-path reliability protocol — dataset, harness, scorer

A fixed, system-agnostic protocol for testing the **write path** of an
agent-memory system: whether a fact is recorded, superseded on update, flagged on
contradiction, removed on delete, and traceable to its source.

Files:

| file | what it is |
| --- | --- |
| `dataset.json` | the controlled fact set: 12 stable facts, 8 updates, 6 contradictions, 8 deletions, 6 out-of-scope probes (40 write units) |
| `adapters.py` | the **adapter contract** (`MemoryAdapter`) plus a deterministic in-memory double (`ReferenceAdapter`) |
| `run_protocol.py` | the generic harness: drives any adapter through ingest → update → contradiction → delete → provenance → out-of-scope and writes `transcript.json` + `scores.json` |
| `test_protocol.py` | deterministic fixture tests for every promised measure (10 tests, stdlib `unittest`, no external deps) |
| `fixture_report.py` | runs the reference + one-defect doubles and captures the real test output |
| `fixture-tests.txt`, `fixture-report.json` | the recorded, hashed output of those runs |

`scores.json` carries both the per-item result rows and the six aggregate rates,
plus a `transcript_sha256` linking it to the sanitized `transcript.json` log. The
per-item rows are the raw `pass`/detail for every fact; the rates are derived from
them, so a reader can recompute any rate from the rows.

## Adapter contract

Implement one class against a real system; the same dataset then drives it:

    write(item_id, text, scope)            -> persist a fact under a stable id
    update(item_id, new_text, scope)       -> change the current value
    delete(item_id, scope)                 -> remove from every store it touched
    retrieve_exact(item_id, scope)         -> str | None            (exact-key fetch)
    query(question, scope)                 -> str | None            (answer or abstain)
    semantic_hit(text, scope)              -> bool                  (search surfaces it)
    provenance(item_id, scope)             -> list[str]             (lineage; [] if none)
    contradiction_trace(question, scope)   -> {"flagged": bool, "values": list[str]}

## Run

    python3 test_protocol.py                                  # fixture unit tests
    python3 run_protocol.py --adapter fixture-reference --out "$TMPDIR/out"
    python3 fixture_report.py                                 # regenerate the report

Point a real system at the harness by importing `run_protocol.run` and passing a
`MemoryAdapter` that calls that system's documented write API. The fixture
adapters (`fixture-*`) exist only to prove the harness and scorer are runnable
with no credentials, network or hosting. **Their rates are fixture-only and must
never be reported as vendor measurements.**
