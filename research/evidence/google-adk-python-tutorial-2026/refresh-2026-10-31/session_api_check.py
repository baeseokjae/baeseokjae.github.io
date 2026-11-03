"""Correction-pass check for the google-adk-python-tutorial-2026 article.

Scope: (a) is InMemorySessionService.create_session async in google-adk 2.13.0,
does the documented shape need await, and does a sync variant exist; (b) does the
article's Runner + session wiring construct with the real installed classes.
No model call, no credential, no network.
"""
import asyncio
import inspect
import json
import platform
import sys
from importlib.metadata import version

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

out = {
    "python": platform.python_version(),
    "platform": platform.platform(),
    "machine": platform.machine(),
    "google_adk": version("google-adk"),
    "google_genai": version("google-genai"),
    "checks": [],
}


def rec(kind, target, status, value=None, error=None):
    item = {"kind": kind, "target": target, "status": status}
    if value is not None:
        item["value"] = value
    if error is not None:
        item["error"] = error
    out["checks"].append(item)


svc_probe = InMemorySessionService()
rec("api", "InMemorySessionService.create_session exists",
    "ok" if hasattr(svc_probe, "create_session") else "error",
    value=hasattr(svc_probe, "create_session"))
rec("api", "inspect.iscoroutinefunction(create_session)", "ok",
    value=inspect.iscoroutinefunction(svc_probe.create_session))
rec("api", "hasattr(create_session_sync)",
    "ok" if hasattr(svc_probe, "create_session_sync") else "error",
    value=hasattr(svc_probe, "create_session_sync"))

agent = LlmAgent(name="code_reviewer", model="gemini-flash-latest",
                 instruction="Read the file and summarise the issues.")

# 1. The un-awaited call the previous edition printed.
try:
    svc_bad = InMemorySessionService()
    runner_bad = Runner(agent=agent, app_name="code_review", session_service=svc_bad)
    coro = svc_bad.create_session(app_name="code_review", user_id="dev_user",
                                  state={"file_path": "my_module.py"})
    rec("reproduce", "un-awaited create_session() return type", "ok",
        value=f"{type(coro).__name__} coroutine={inspect.iscoroutine(coro)}")
    try:
        _ = coro.id
        rec("reproduce", "session.id on un-awaited create_session()", "ok", value="no error")
    except Exception as exc:  # noqa: BLE001 - the failure mode is the evidence
        rec("reproduce", "session.id on un-awaited create_session()", "error",
            error=f"{type(exc).__name__}: {exc}")
finally:
    pass


async def corrected_async():
    svc = InMemorySessionService()
    runner = Runner(agent=agent, app_name="code_review", session_service=svc)
    session = await svc.create_session(app_name="code_review", user_id="dev_user",
                                       state={"file_path": "my_module.py"})
    got = await svc.get_session(app_name="code_review", user_id="dev_user",
                                session_id=session.id)
    return {
        "session_id": session.id,
        "state": session.state,
        "read_back_session_id": got.id,
        "read_back_state": got.state,
        "runner_type": type(runner).__name__,
        "runner_app_name": runner.app_name,
        "create_session_is_async": inspect.iscoroutinefunction(svc.create_session),
    }


res = asyncio.run(corrected_async())
out["corrected_async"] = res
rec("run", "await session_service.create_session(...) then session.id", "ok",
    value=res["session_id"])

# 2. The sync alternative the article now mentions.
svc_sync = InMemorySessionService()
if hasattr(svc_sync, "create_session_sync"):
    s2 = svc_sync.create_session_sync(app_name="code_review", user_id="dev_user",
                                      state={"file_path": "my_module.py"})
    out["corrected_sync"] = {"session_id": s2.id, "state": s2.state}
    rec("run", "create_session_sync(...) then session.id", "ok", value=s2.id)
else:
    rec("run", "create_session_sync(...) then session.id", "error",
        error="create_session_sync is not present on InMemorySessionService")

# 3. Runner.run signature is a sync generator in this release: confirm without calling.
sig = inspect.signature(Runner.run)
out["runner_run_signature"] = str(sig)
rec("api", "inspect.isgeneratorfunction(Runner.run)", "ok",
    value=inspect.isgeneratorfunction(Runner.run))
rec("api", "Runner.run is not a coroutine function", "ok",
    value=not inspect.iscoroutinefunction(Runner.run))

out["module_file"] = {
    "google.adk.sessions.in_memory_session_service":
        inspect.getsourcefile(InMemorySessionService),
}
out["not_covered"] = [
    "No Gemini/Vertex model call: no credential in this run, so Runner.run was never iterated.",
    "No response text, latency or answer quality is observed by this script.",
]
out["recorded_at_utc"] = __import__("datetime").datetime.now(
    __import__("datetime").timezone.utc).isoformat()

json.dump(out, sys.stdout, indent=2)
print()
