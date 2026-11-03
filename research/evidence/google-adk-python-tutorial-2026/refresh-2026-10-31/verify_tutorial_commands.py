"""Bounded offline verification of the google-adk tutorial commands + tool error path.

No model call and no API credential are used: every check here is import,
construction, metadata or direct tool-invocation only. Run with:

    python verify_tutorial_commands.py > local-run-verify-output.json 2> local-run-stderr.txt

Environment for the recorded run: Python 3.12.3 on Linux aarch64, a fresh
`python3 -m venv` plus an unpinned `pip install google-adk`.
"""
from __future__ import annotations

import importlib
import importlib.metadata as md
import json
import platform
import sys
import traceback
import warnings

results: dict = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "machine": platform.machine(),
    "checks": [],
}


def record(kind: str, target: str, fn) -> None:
    try:
        value = fn()
        results["checks"].append({"kind": kind, "target": target, "status": "ok", "value": value})
    except Exception as exc:  # noqa: BLE001 - the exception text is the evidence
        results["checks"].append({
            "kind": kind,
            "target": target,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback_tail": traceback.format_exc().strip().splitlines()[-3:],
        })


def imports() -> None:
    targets = [
        ("module", "google.adk"),
        ("from", "from google.adk.agents.llm_agent import Agent"),
        ("from", "from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent"),
        ("from", "from google.adk.agents.sequential_agent import SequentialAgent"),
        ("from", "from google.adk.tools import google_search"),
        ("from", "from google.adk.runners import Runner"),
        ("from", "from google.adk.sessions import InMemorySessionService"),
        ("from", "from google.genai.types import Content, Part"),
        ("from", "from google.adk.a2a import A2AServer"),
        ("from", "from google.adk.a2a import A2AClient"),
        ("from", "from google.adk.a2a.utils.agent_to_a2a import to_a2a"),
    ]
    for kind, stmt in targets:
        def _run(stmt=stmt, kind=kind):
            if kind == "module":
                return importlib.import_module(stmt).__name__
            ns: dict = {}
            exec(stmt, ns)  # noqa: S102 - statement text is the literal tutorial import
            return sorted(k for k in ns if not k.startswith("__"))
        record("import", stmt, _run)


def construction() -> None:
    from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

    def child(name: str, key: str):
        return LlmAgent(name=name, model="gemini-flash-latest",
                        instruction="Analyze the file.", output_key=key)

    def seq():
        a = SequentialAgent(name="s", sub_agents=[child("c1", "k1"), child("c2", "k2")])
        return [c.name for c in a.sub_agents]

    def par():
        p = ParallelAgent(name="p", sub_agents=[child("p1", "k1"), child("p2", "k2")])
        return [c.name for c in p.sub_agents]

    def nested():
        p = ParallelAgent(name="inner", sub_agents=[child("n1", "k1"), child("n2", "k2")])
        s = SequentialAgent(name="outer", sub_agents=[p, child("synth", "final")])
        return [c.name for c in s.sub_agents]

    def colliding_keys():
        p = ParallelAgent(name="dup", sub_agents=[child("d1", "result"), child("d2", "result")])
        return [c.output_key for c in p.sub_agents]

    for name, fn in (("SequentialAgent", seq), ("ParallelAgent", par),
                     ("nested parallel-in-sequential", nested),
                     ("ParallelAgent with duplicate output_key", colliding_keys)):
        record("construct", name, fn)


def tool_schema() -> None:
    """The part this refresh adds: what ADK derives from a plain function."""
    from google.adk.tools import FunctionTool

    def read_file(file_path: str) -> dict:
        """Read a file and return its contents."""
        try:
            with open(file_path) as f:
                return {"status": "success", "content": f.read()}
        except FileNotFoundError:
            return {"status": "error", "error": f"File not found: {file_path}"}

    tool = FunctionTool(read_file)
    decl = tool._get_declaration()
    results["tool_schema"] = {
        "declaration": decl.model_dump(exclude_none=True) if hasattr(decl, "model_dump") else str(decl),
    }
    record("tool_attr", "FunctionTool.name", lambda: tool.name)


def tool_error_path() -> None:
    """Direct tool invocation with no model in the loop."""
    import asyncio

    from google.adk.tools import FunctionTool

    def read_file(file_path: str) -> dict:
        """Read a file and return its contents."""
        with open(file_path) as f:
            return {"status": "success", "content": f.read()}

    tool = FunctionTool(read_file)

    async def call(args: dict):
        fn = getattr(tool, "run_async", None)
        if fn is None:
            raise RuntimeError("FunctionTool has no run_async")
        out = fn(args=args, tool_context=None)
        if hasattr(out, "__await__"):
            out = await out
        return out

    def missing_file():
        return asyncio.run(call({"file_path": "/nonexistent/definitely-missing.txt"}))

    def wrong_type():
        return asyncio.run(call({"file_path": 123}))

    def missing_required_arg():
        return asyncio.run(call({}))

    for name, fn in (("missing file -> exception raised by tool body", missing_file),
                     ("wrong argument type", wrong_type),
                     ("required argument omitted", missing_required_arg)):
        def _run(fn=fn):
            out = fn()
            return {"returned": repr(out)[:600]}
        record("tool_call", name, _run)


def main() -> None:
    dist = md.distribution("google-adk")
    meta = dist.metadata
    results["distribution"] = {
        "version": md.version("google-adk"),
        "requires_python": meta.get("Requires-Python"),
        "summary": meta.get("Summary"),
        "extras": sorted(meta.get_all("Provides-Extra") or []),
        "google_genai": md.version("google-genai"),
    }
    results["recorded_at_utc"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat()

    imports()
    construction()
    tool_schema()
    tool_error_path()

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        main()
        sys.stderr.write("\n".join(
            f"{w.category.__name__}: {w.message}" for w in caught) + "\n")
