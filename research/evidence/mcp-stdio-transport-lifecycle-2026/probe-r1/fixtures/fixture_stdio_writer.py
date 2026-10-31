#!/usr/bin/env python3
"""Fixture for L1/L2: exercises mcp 2.2.0's server-side stdout writer directly.

L1 mode (FIXTURE_MODE=big): send one JSON-RPC response whose payload is larger
than a Linux pipe buffer, then keep the transport open until stdin EOF. If the
caller never reads stdout, the write blocks inside the SDK writer task.

L2 mode (FIXTURE_MODE=surrogate): send one response carrying a str built with
os.fsdecode() on a byte that is not valid UTF-8, then try to send a second,
well-formed message. Serialisation of the first message happens inside the
writer task (model_dump_json), which is where the failure lands.
"""
import os
import sys

import anyio
from mcp import types
from mcp.server.stdio import stdio_server
from mcp.shared.message import SessionMessage

MODE = os.environ.get("FIXTURE_MODE", "big")
BLOB_BYTES = int(os.environ.get("BLOB_BYTES", "262144"))


def log(line):
    print(line, file=sys.stderr, flush=True)


def msg(msg_id, result):
    return SessionMessage(types.JSONRPCResponse(jsonrpc="2.0", id=msg_id, result=result))


async def main():
    async with stdio_server() as (read_stream, write_stream):
        if MODE == "big":
            log(f"FIXTURE_READY mode=big blob_bytes={BLOB_BYTES}")
            await write_stream.send(msg(1, {"blob": "x" * BLOB_BYTES}))
            log("FIXTURE_BIG_QUEUED")
            async for _ in read_stream:
                pass
            log("FIXTURE_STDIN_EOF")
            # mimic the server session's shutdown: the writer stream is closed
            # so stdout_writer can leave its loop if it is not stuck in a write.
            await write_stream.aclose()
        elif MODE == "surrogate":
            bad = os.fsdecode(b"bad-\xff-name")
            log(f"FIXTURE_READY mode=surrogate repr={bad!r}")
            with anyio.fail_after(5):
                await write_stream.send(msg(2, {"uri": bad}))
            log("FIXTURE_BAD_QUEUED")
            await anyio.sleep(1.0)
            try:
                with anyio.fail_after(5):
                    await write_stream.send(msg(3, {"ok": True}))
                log("FIXTURE_GOOD_QUEUED")
            except BaseException as exc:  # noqa: BLE001
                log(f"FIXTURE_GOOD_SEND_FAILED {type(exc).__name__}: {exc}")
            await anyio.sleep(3.0)
            log("FIXTURE_STILL_ALIVE_AFTER_BAD_MESSAGE")
            async for _ in read_stream:
                pass
        else:
            log(f"FIXTURE_UNKNOWN_MODE {MODE}")


if __name__ == "__main__":
    try:
        anyio.run(main)
    except BaseException as exc:  # noqa: BLE001
        log(f"FIXTURE_TOP_LEVEL_EXIT {type(exc).__name__}: {exc}")
        raise
