# Method — stdio lifecycle probe (probe-r1)

Run date: 2026-10-30 (UTC). Stage: write (BLO-4483), slug `mcp-stdio-transport-lifecycle-2026`.
No paid API, no vendor system: everything below ran on the article's own Linux host.

## Environment

- Linux, CPython 3.12.3, isolated venv under the run scratch dir.
- `mcp==2.2.0`, `anyio==4.15.1`, `pydantic==2.14.2` (recorded in `results.json` → `versions`).
- Pipe buffer 64 KiB (Linux default). macOS/Windows pipe sizes differ; nothing here is generalised to them.

## What was run

`probe_stdio_lifecycle.py` (this directory) with the two fixtures in `fixtures/`.
Each scenario spawns real child processes and records observations rather than assertions:

1. **L1** — one JSON-RPC response with a 262,144-byte payload from the SDK's own server
   stdio transport, stdin closed 2 s later, `/proc/<pid>/stat` sampled for up to 10 s,
   then SIGTERM, then SIGKILL if still alive. Two arms: stdout drained by the parent
   (control) and stdout never read. The fixture closes its write stream after stdin EOF
   so the control arm can leave `stdout_writer` normally — without that, the control
   would hang for fixture reasons and prove nothing.
2. **L2** — one response whose `uri` came from `os.fsdecode(b"bad-\xff-name")`, then a
   second well-formed message. The parent drains stdout, so this arm cannot be explained
   by L1's backpressure. Recorded: stdout byte count, stderr text, process state.
3. **L3** — `ClientSessionGroup` with one duplicate-name registration; recorded
   `len(group.sessions)`, `sorted(group.tools)` and the number of children of the test
   process before, after the rejection, and after group close.
4. **L4** — one caller-owned session registered with a server advertising `old`, the
   fixture catalogue rewritten to `new`, the same session registered again, then
   `disconnect_from_server`; recorded `group.tools` and `group.sessions` at each step.

## Invocation history (honest)

- L1 and L2 ran in one invocation (`--only L1,L2`), then L1+L2 were re-run together with
  everything else to produce a single record file.
- L3 and L4 were executed in a separate invocation (`--only L3,L4`) and merged into
  `results.json`, because a combined run intermittently raised during `ClientSessionGroup`
  teardown after the rejected connect. Per-scenario `started_at`/`finished_at` in
  `results.json` show which window each record came from; the merge did not alter values.
- One run per arm. This is n=1 per scenario, not a distribution; the numbers are
  observations, not rates.

## Fixture caveats

The fixtures are written for this article. They call the SDK transports directly
(`mcp.server.stdio.stdio_server`, `mcp.client.stdio.stdio_client`,
`ClientSessionGroup`) rather than a third-party server, so the writer/reader/task-group
behaviour is the SDK's; the tool catalogue, payload size and timing are ours. L2's
exception class depends on the resolved pydantic version (2.14.2 here).

## Files

- `probe_stdio_lifecycle.py` — the probe.
- `fixtures/fixture_stdio_writer.py` — L1/L2 fixture (big payload / surrogate payload).
- `fixtures/fixture_server.py` — L3/L4 fixture; tool catalogue read from a JSON file on
  every `tools/list`, so a caller can change it between registrations.
- `results.json` — raw records, including `/proc` states, child pids, byte counts and
  stderr text.
