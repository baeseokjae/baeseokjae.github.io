#!/usr/bin/env python3
"""Count what a stdio MCP host actually leaves behind (mcp==2.2.0, Linux).

Scenarios
  L1  unread stdout + stdin EOF:  does the server process return on EOF?
      L1-control repeats the same sequence while draining stdout.
  L2  unencodable str in an outgoing message: is the failure contained?
  L3  ClientSessionGroup duplicate-name rejection: is the transport reachable?
  L4  re-registered session then disconnect: do old tools survive?

Every scenario writes a record with the observations that were actually taken:
/proc state samples, child-process counts, received byte counts and stderr text.
Run it with the interpreter that has mcp==2.2.0 installed:

    python probe_stdio_lifecycle.py --out results.json
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import anyio
from mcp import ClientSession, types
from mcp.client.session_group import ClientSessionGroup
from mcp.client.stdio import StdioServerParameters as ServerParameters, stdio_client

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
PY = sys.executable


def now():
    return datetime.now(timezone.utc).isoformat()


def proc_stat(pid):
    """Return the state field from /proc/<pid>/stat, or None if the pid is gone."""
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except FileNotFoundError:
        return None
    return raw.rsplit(")", 1)[1].split()[0]  # R/S/D; "Z" means exited, not reaped


def running(pid):
    """True only for a live, non-zombie process."""
    state = proc_stat(pid)
    return state is not None and state != "Z"


def children_of(pid):
    found = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            raw = (entry / "stat").read_text()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        after = raw.rsplit(")", 1)[1].split()
        if int(after[1]) == pid:
            found.append({"pid": int(entry.name), "state": after[0]})
    return found


def spawn(mode, catalog=None, blob_bytes=None):
    env = dict(os.environ)
    env["FIXTURE_MODE"] = mode
    if catalog:
        env["FIXTURE_CATALOG"] = str(catalog)
    if blob_bytes:
        env["BLOB_BYTES"] = str(blob_bytes)
    script = FIXTURES / ("fixture_stdio_writer.py" if mode in ("big", "surrogate") else "fixture_server.py")
    return subprocess.Popen([PY, str(script)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, bufsize=0)


def kill_tree(proc, sig=signal.SIGKILL):
    try:
        proc.send_signal(sig)
    except ProcessLookupError:
        pass


def l1(drain, blob_bytes):
    """Unread stdout + stdin EOF. drain=True is the control arm."""
    record = {"scenario": "L1", "arm": "drain_stdout_control" if drain else "leave_stdout_unread",
              "blob_bytes": blob_bytes, "started_at": now()}
    proc = spawn("big", blob_bytes=blob_bytes)
    received = {"bytes": 0}
    err_chunks = []

    def read_stdout():
        while True:
            chunk = proc.stdout.read(65536)
            if not chunk:
                return
            received["bytes"] += len(chunk)

    def read_stderr():
        for line in iter(proc.stderr.readline, b""):
            err_chunks.append(line.decode(errors="replace").strip())

    if drain:
        threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()

    time.sleep(2.0)  # give the writer time to fill the pipe
    record["alive_before_eof"] = proc_stat(proc.pid)
    proc.stdin.close()  # EOF on the server's stdin
    eof_at = time.monotonic()
    deadline = 10.0
    state_at_10s = None
    while time.monotonic() - eof_at < deadline:
        if not running(proc.pid):
            break
        state = proc_stat(proc.pid)
        state_at_10s = state
        time.sleep(0.2)
    record["seconds_waited_after_eof"] = deadline
    record["state_at_wait_end"] = proc_stat(proc.pid)
    record["exited_on_eof_within_10s"] = not running(proc.pid)
    if record["exited_on_eof_within_10s"]:
        record["exit_status"] = proc.wait(timeout=5)
        record["signal_needed"] = None
    else:
        kill_tree(proc, signal.SIGTERM)
        time.sleep(3.0)
        after_term = proc_stat(proc.pid)
        record["state_after_sigterm"] = after_term
        if not running(proc.pid):
            record["signal_needed"] = "SIGTERM"
        else:
            record["signal_needed"] = "SIGKILL"
        if after_term is None:
            try:
                record["exit_status"] = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                record["exit_status"] = "still waiting (zombie)"
        else:
            kill_tree(proc, signal.SIGKILL)
            try:
                record["exit_status"] = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                record["exit_status"] = "unkillable"
    record["stdout_bytes_read"] = received["bytes"]
    record["stderr_tail"] = err_chunks[-6:]
    record["finished_at"] = now()
    return record


def l2():
    record = {"scenario": "L2", "started_at": now()}
    proc = spawn("surrogate")
    received = {"bytes": 0, "lines": []}
    err_chunks = []

    def read_stdout():
        while True:
            chunk = proc.stdout.read(65536)
            if not chunk:
                return
            received["bytes"] += len(chunk)
            received["lines"].extend(chunk.split(b"\n"))

    def read_stderr():
        for line in iter(proc.stderr.readline, b""):
            err_chunks.append(line.decode(errors="replace").strip())

    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()
    time.sleep(6.5)  # fixture: bad send, 1 s pause, good send, 3 s pause
    record["stdout_bytes"] = received["bytes"]
    record["stdout_nonempty_lines"] = [x for x in received["lines"] if x.strip()][:4]
    record["stderr"] = err_chunks
    record["serialization_error_class"] = next(
        (x.split()[0] for x in err_chunks if "Error" in x or "error" in x), None)
    record["process_state_after"] = proc_stat(proc.pid)
    record["process_alive_after"] = running(proc.pid)
    proc.stdin.close()
    time.sleep(1.0)
    record["exits_on_stdin_eof"] = not running(proc.pid)
    if not record["exits_on_stdin_eof"]:
        kill_tree(proc, signal.SIGTERM)
        time.sleep(2.0)
        record["state_after_sigterm"] = proc_stat(proc.pid)
        if running(proc.pid):
            kill_tree(proc, signal.SIGKILL)
            record["signal_needed"] = "SIGKILL"
        else:
            record["signal_needed"] = "SIGTERM"
    else:
        record["signal_needed"] = None
    record["finished_at"] = now()
    return record


async def l3():
    record = {"scenario": "L3", "started_at": now()}
    catalog = HERE / "catalog_l3.json"
    catalog.write_text(json.dumps(["echo"]))
    params = ServerParameters(command=PY, args=[str(FIXTURES / "fixture_server.py")],
                              env={"FIXTURE_NAME": "dup", "FIXTURE_CATALOG": str(catalog)})
    me = os.getpid()
    async with ClientSessionGroup() as group:
        await group.connect_to_server(params)
        record["after_first_connect"] = {"sessions": len(group.sessions), "tools": sorted(group.tools),
                                         "children": len(children_of(me))}
        try:
            await group.connect_to_server(params)
            record["second_connect"] = "no error"
        except BaseException as exc:  # noqa: BLE001
            record["second_connect"] = f"{type(exc).__name__}: {exc}"
        await anyio.sleep(0.5)
        record["after_rejected_connect"] = {"sessions": len(group.sessions), "tools": sorted(group.tools),
                                            "children": len(children_of(me)),
                                            "children_detail": children_of(me)}
    await anyio.sleep(0.5)
    record["after_group_close"] = {"children": len(children_of(me))}
    record["finished_at"] = now()
    return record


async def l4():
    record = {"scenario": "L4", "started_at": now()}
    catalog = HERE / "catalog_l4.json"
    catalog.write_text(json.dumps(["old"]))
    params = ServerParameters(command=PY, args=[str(FIXTURES / "fixture_server.py")],
                              env={"FIXTURE_NAME": "ghost", "FIXTURE_CATALOG": str(catalog)})
    async with ClientSessionGroup() as group:
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                info = types.Implementation(name="ghost", version="0.0.1")
                await group.connect_with_session(info, session)
                record["first_registration_tools"] = sorted(group.tools)
                catalog.write_text(json.dumps(["new"]))
                await group.connect_with_session(info, session)
                record["second_registration_tools"] = sorted(group.tools)
                await group.disconnect_from_server(session)
                record["after_disconnect"] = {"sessions": len(group.sessions),
                                             "tools": sorted(group.tools)}
                record["stale_tools_remaining"] = [t for t in group.tools if "old" in t]
    record["finished_at"] = now()
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--blob-bytes", type=int, default=262144)
    ap.add_argument("--only", default="L1,L2,L3,L4")
    args = ap.parse_args()
    want = set(args.only.split(","))
    results = {"tool": "probe_stdio_lifecycle.py", "started_at": now(),
               "python": sys.version.split()[0],
               "platform_note": "Linux/CPython; pipe buffer 64 KiB default",
               "catalog_sha256_source": "fixtures/"}
    try:
        import importlib.metadata as md
        results["versions"] = {"mcp": md.version("mcp"), "anyio": md.version("anyio"),
                              "pydantic": md.version("pydantic")}
    except Exception as exc:  # noqa: BLE001
        results["versions"] = {"error": str(exc)}
    def save():
        Path(args.out).write_text(json.dumps(results, indent=2))

    if "L1" in want:
        results["L1_control_drain"] = l1(True, args.blob_bytes)
        save()
        results["L1_unread"] = l1(False, args.blob_bytes)
        save()
    if "L2" in want:
        results["L2"] = l2()
        save()
    if "L3" in want:
        results["L3"] = anyio.run(l3)
        save()
    if "L4" in want:
        results["L4"] = anyio.run(l4)
        save()
    results["finished_at"] = now()
    Path(args.out).write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
