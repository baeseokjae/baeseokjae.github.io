# Method: local SQLite memory-store span fixture

Run: 2026-11-16T06:15Z, single process, ~3 s wall including interpreter start.

Environment (measured, not assumed):
- Python 3.12.3, sqlite3 3.45.1 (stdlib only)
- No OpenTelemetry SDK installed in the run interpreter (`import opentelemetry` -> ModuleNotFoundError).
  Spans are written in OTLP/JSON shape by hand, so the dump can be replayed into a Collector
  later without re-running the instrumented code.
- SemConv reference pinned at open-telemetry/semantic-conventions-genai
  commit e6658f14c9d9ea0760825f029cb82e7673f48fab (committed 2026-11-06T03:31:30Z).

What the script does (`memory_spans.py`, stdlib, no network):
1. Creates `memory.sqlite` with a `memory(ns, key, value, updated_at)` table.
2. Trace 1: parent `invoke_agent memory-fixture` + one `create_memory` span writing 51 records
   (50 generated facts + one `fact-stale` = "user timezone is UTC+8").
3. Trace 2: two `search_memory` spans for the query `timezone`. Between them the stored value is
   updated to "user timezone is UTC+9 (Asia/Seoul)" with no write span emitted (this is the
   induced staleness: the second read returns a different value for the same query in the same trace).
4. Trace 3: one `delete_memory` span removing `fact-stale` with `memory.evicted_reason =
   superseded_by_newer_value`.

Observed output of this exact run:
    span counts: {"create_memory": 1, "delete_memory": 1,
                  "invoke_agent memory-fixture": 3, "search_memory": 2}
    pre-update hits:  [('fact-stale', 'user timezone is UTC+8')]
    post-update hits: [('fact-stale', 'user timezone is UTC+9 (Asia/Seoul)')]
    rows remaining: 50
    traces: 3  total spans: 7

Reproduce: `python3 memory_spans.py .` in this directory (writes `memory.sqlite`, `spans.json`).

Sanitisation: fixture facts are synthetic; record keys are replaced in span attributes by a
16-hex SHA-256 prefix (`memory.key_hash` / `gen_ai.memory.record.id`), so no user content is in
the dump except the synthetic timezone string used to demonstrate the value change.

Deviations from the proposal in the task `selection`, recorded for the writer:
- Operation names come from the GenAI SemConv enum (`create_memory`, `search_memory`,
  `delete_memory`), not the invented `memory.write` / `memory.retrieve` / `memory.evict`.
- Span kind is INTERNAL because the store runs in-process; the spec recommends CLIENT for
  out-of-process memory services.
- The dump is OTLP/JSON rather than SDK-emitted; attribute names and value types match the spec
  (stringValue / intValue / boolValue / doubleValue) so a Collector can ingest it as-is.
