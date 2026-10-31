---
date: 2026-10-30 02:45:00+00:00
description: Four stdio lifecycle failures in the MCP Python SDK 2.2.0, measured
  with a probe that counts processes and tools — plus a shutdown contract your
  agent host can enforce.
draft: false
schema: schema-mcp-stdio-transport-lifecycle-2026
tags:
- mcp
- python
- stdio
- agent-infrastructure
- debugging
title: 'MCP stdio Leaks: Why Your Agent''s Tool Servers Hang at Shutdown, Die on
  a Bad Filename and Leave Ghost Tools'
---

A stdio MCP server that never exits is not a mystery: the Python SDK's writer task can be blocked in a pipe write that only the reader can unblock, so cancelling it waits forever. In MCP Python SDK 2.2.0 on Linux, this probe reproduced that hang and three related lifecycle defects — an unencodable string that kills the connection with no JSON-RPC error, a rejected `ClientSessionGroup` registration that leaves a second server child alive and unreachable, and a disconnected session whose old tool name survives in `group.tools`. All four have a host-side workaround you can enforce today, and the probe below counts exactly what your host leaks.

The article is about what happens *after* the handshake. If you are still writing your first server, start with [building an MCP server in Python](/posts/build-mcp-server-python-2026/) or the [FastMCP 3 guide](/posts/fastmcp-3-python-mcp-server-guide-2026/) and come back here when your process table starts to fill.

## The four symptoms, one accounting frame

| Symptom in production | Where it comes from | What the probe recorded on mcp 2.2.0 |
| --- | --- | --- |
| Server never exits after the session ends | stdout write blocked on a full pipe; cancellation waits on the thread | alive 10 s after stdin EOF, SIGTERM needed, exit status −15 |
| One session dies, no error in the client | serialisation inside the writer task is not contained | `PydanticSerializationError`, 0 bytes written, connection gone |
| Extra server process after a failed connect | transport opened before components are validated | 2 children, 1 session in the group, 0 children only after group close |
| Tool the model calls no longer exists | reverse index replaced, aggregate dict updated only | `old` still in `group.tools` after disconnect, `group.sessions == []` |

## L1: the hang is a full pipe, not a missing exit

The mechanism is a Linux pipe: 64 KiB of buffered bytes, then `write(2)` blocks. The SDK's server writer serialises each outgoing message and writes it with `stdout.write` plus `stdout.flush` inside a worker thread (`to_thread`). If the client stops draining stdout while a response larger than the buffer is still in flight, that thread is stuck in the kernel. When stdin EOF then ends the session, the task group cancels the writer — and cancellation has to wait for a thread that cannot finish until the client reads.

The probe drives the same sequence twice: one response of 262,144 payload bytes, stdin closed 2 s later, 10 s of `/proc` sampling, then SIGTERM.

| Arm | stdout bytes read | State 10 s after EOF | Signal needed | Exit status |
| --- | --- | --- | --- | --- |
| Drain stdout (control) | 262,190 | exited | none | 0 |
| Leave stdout unread | 0 | `S` (sleeping) | SIGTERM | −15 |

The control arm is what makes this a finding rather than a fixture bug: identical fixture, identical message, only the read side differs. With the reader draining, the process exits 0 by itself. Without a reader, it is still alive after ten seconds and has to be signalled. This is the same sequence reported upstream in [issue #3674](https://github.com/modelcontextprotocol/python-sdk/issues/3674), where the reporter's thread dump shows a worker blocked behind `await stdout.flush()` in `mcp/server/stdio.py`.

Host-side consequence: closing stdin is not a shutdown. Any supervisor that only closes the pipe and waits will accumulate one sleeping child per session.

## L2: one unencodable string takes the whole connection

A `str` containing a lone surrogate cannot be encoded as UTF-8 JSON. It is easy to obtain without any malicious input: `os.fsdecode()` on a filename that is not valid UTF-8 returns one, and so does `open(..., errors="surrogateescape")` or a decoded `argv`. Validation passes, `model_dump(mode="json")` passes, and the failure lands in `model_dump_json()` inside the writer task, where only `anyio.ClosedResourceError` is caught.

In the probe the server sent one response whose `uri` field was built from `os.fsdecode(b"bad-\xff-name")`, then tried to send a second, valid message:

- stdout bytes delivered to the client: **0** — not even the bad message, because serialisation fails before the write.
- stderr: `pydantic_core._pydantic_core.PydanticSerializationError: Error serializing to JSON: UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' in position 4: surrogates not allowed`.
- The writer task ended, the task group tore down the session, and the fixture exited with an `ExceptionGroup` — the caller learns nothing about which request failed.

That matches [issue #3707](https://github.com/modelcontextprotocol/python-sdk/issues/3707), where the reporter describes the same class of failure for the server writer and for the client's `stdin_writer` on every transport. The exception class depends on the resolved pydantic version; this run used pydantic 2.14.2, so treat `PydanticSerializationError` as the shape, not the contract.

Host-side consequence: a single path, filename, or environment value that survives `surrogateescape` can kill a session, and the failure surfaces as a closed connection rather than an error for that request. Sanitise outbound payloads at the boundary (`json.dumps(..., ensure_ascii=True)` or explicit re-encoding with errors="replace") if any of your tool inputs come from the filesystem.

## L3: who owns a transport whose connect was rejected

`ClientSessionGroup.connect_to_server` starts the transport, initialises the session, and only then aggregates components. The duplicate-name check raises before the session is recorded:

```python
matching_tools = tools_temp.keys() & self._tools.keys()
if matching_tools:
    raise MCPError(code=types.INVALID_PARAMS, message=f"{matching_tools} already exist in group tools.")

# Aggregate components.
self._sessions[session] = component_names
```

That ordering is visible in the v2.2.0 source of [session_group.py](https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/v2.2.0/src/mcp/client/session_group.py), and the probe confirms the runtime effect: after the rejected second connect, `len(group.sessions)` is still 1 while the process table shows 2 children. The caller has no session object, so `disconnect_from_server()` cannot reach the transport; only closing the whole group reclaimed it (0 children after close).

This is [issue #3490](https://github.com/modelcontextprotocol/python-sdk/issues/3490). The caveat matters for your fix: it is a lifetime-scope mismatch, not an unbounded orphan. The second child lives until the group closes. In a long-lived host that keeps one group open for hours and re-registers servers per reconnect, that is still one leaked process per rejection.

## L4: ghost tools survive disconnect

The same aggregation path keeps an older catalogue. The probe registered one caller-owned session whose server advertised `old`, changed the server's catalogue to `new`, registered the same session again, then disconnected:

| Step | `group.tools` | `group.sessions` |
| --- | --- | --- |
| First registration | `['old']` | 1 |
| Second registration | `['new', 'old']` | 1 |
| After `disconnect_from_server` | `['old']` | 0 |

Disconnect removes only the names in the current reverse index for that session, while the aggregate dictionaries were merged on both registrations. That is [issue #3713](https://github.com/modelcontextprotocol/python-sdk/issues/3713), reported with exactly this shape. The model keeps a tool in its prompt that the host can no longer route.

## A shutdown contract your host can enforce

None of these need a fork of the SDK. They need four rules in the code that owns the child process:

1. **Close stdin, then drain stdout, then wait.** Never expect EOF alone to end a server whose response is still in a pipe. Read until EOF before you join the process, and put a wall-clock bound on the join.
2. **Escalate on a bound, and record which signal worked.** A server that ignores EOF is normal in this class; a server that survives SIGTERM is a different bug. Log both transitions with the pid so the next leak is countable.
3. **Close the transport on a failed connect, not just on a returned session.** Wrap `connect_to_server` yourself: on exception, close the group (or the transport you opened) before retrying, because the handle you would need was never returned.
4. **Verify the tool table after every disconnect.** `assert not group.tools` (or compare against the set you expect) is a one-line test that catches the ghost-tool class before a model tries to call a tool that is gone.

If you want the accounting view alongside this, the OpenTelemetry trace setup in [agent observability with OpenTelemetry](/posts/ai-agent-observability-opentelemetry-2026/) shows the span side, and [agent doctor](/posts/agent-doctor-local-observability/) covers local runtime health checks that can host the process-count assertion above.

## The probe: what it counts and what it does not

`probe_stdio_lifecycle.py` spawns real stdio children against `mcp==2.2.0`, samples `/proc/<pid>/stat` for state, walks `/proc` for children of the test process, and records stdout byte counts plus stderr text per scenario. It is not a harness for your own servers; it is a small reproducible check of the SDK paths above.

Files from this run, published with the article (origin: first-party run on 2026-10-30, Linux, CPython 3.12.3, no personal data):

- [probe_stdio_lifecycle.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/mcp-stdio-transport-lifecycle-2026/probe-r1/probe_stdio_lifecycle.py)
- [fixture_server.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/mcp-stdio-transport-lifecycle-2026/probe-r1/fixtures/fixture_server.py)
- [fixture_stdio_writer.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/mcp-stdio-transport-lifecycle-2026/probe-r1/fixtures/fixture_stdio_writer.py)
- [results.json (raw records)](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/mcp-stdio-transport-lifecycle-2026/probe-r1/results.json)
- [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/mcp-stdio-transport-lifecycle-2026/probe-r1/method.md)

Limits, stated plainly: one Linux host, one run per arm, one pinned version (2.2.0), fixture servers written for this article rather than third-party servers. L3 and L4 were executed in a second invocation of the same probe (`--only L3,L4`) and merged into `results.json`; timestamps in the record show both windows. The 64 KiB pipe buffer is a Linux default — macOS and Windows pipe sizes differ, and none of the timing or signal behaviour here should be transferred to them without re-running. v2.3.0 ships different bytes for `session_group.py` and `client/stdio.py`, so "still broken in 2.3.0" is not established by this run; the server writer path was byte-identical between the two tags when the sources were fetched.

If you do not run the probe, the four rules above still hold: they are derived from the source paths quoted here, not from a benchmark score.

## Sources

- [modelcontextprotocol/python-sdk#3674](https://github.com/modelcontextprotocol/python-sdk/issues/3674) — stdio server never exits on stdin EOF while the client leaves stdout unread.
- [modelcontextprotocol/python-sdk#3707](https://github.com/modelcontextprotocol/python-sdk/issues/3707) — a lone surrogate in an outgoing message kills the writer or the session.
- [modelcontextprotocol/python-sdk#3490](https://github.com/modelcontextprotocol/python-sdk/issues/3490) — a rejected `connect_to_server` leaves its transport running.
- [modelcontextprotocol/python-sdk#3713](https://github.com/modelcontextprotocol/python-sdk/issues/3713) — old tools survive after disconnecting a re-registered session.
- [modelcontextprotocol/python-sdk#3714](https://github.com/modelcontextprotocol/python-sdk/issues/3714) — strict decoding withholds fatal read errors until peer stdout EOF.
- [mcp/server/stdio.py at v2.2.0](https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/v2.2.0/src/mcp/server/stdio.py) — the writer task and its single `except` clause.
- [mcp/client/stdio.py at v2.2.0](https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/v2.2.0/src/mcp/client/stdio.py) — the shielded `_drain_stdout` in `finally`, and the process-stop escalation order.
- [mcp/client/session_group.py at v2.2.0](https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/v2.2.0/src/mcp/client/session_group.py) — the raise-before-record ordering and the disconnect loop over the current index.
