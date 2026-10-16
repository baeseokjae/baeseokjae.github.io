#!/usr/bin/env python3
"""Bounded local verification of the commands/imports printed on
content/posts/google-adk-python-tutorial-2026.md, against the package that
pip actually resolves today. One attempt, no network, no model calls.
Run with the isolated venv interpreter created under $TMPDIR.
"""
import importlib, json, platform, subprocess, sys, traceback
from pathlib import Path

OUT = {}
OUT["python_version"] = sys.version
OUT["executable"] = sys.executable
OUT["platform"] = platform.platform()
OUT["utc_started"] = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                    capture_output=True, text=True).stdout.strip()

# --- 1. resolved package versions (what actually installed) ---
OUT["pip_show"] = subprocess.run(
    [sys.executable, "-m", "pip", "show", "google-adk", "google-genai"],
    capture_output=True, text=True).stdout

# --- 2. declared extras on the installed distribution ---
try:
    from importlib.metadata import metadata, version
    OUT["dist_version"] = version("google-adk")
    md = metadata("google-adk")
    OUT["provides_extra"] = md.get_all("Provides-Extra")
    OUT["requires_python"] = md.get("Requires-Python")
except Exception:
    OUT["provides_extra"] = traceback.format_exc()

# --- 3. every import statement the tutorial prints, one by one ---
IMPORTS = [
    "from google.adk.agents import LlmAgent",
    "from google.adk.agents import Agent",
    "from google.adk.agents import LlmAgent, SequentialAgent",
    "from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent",
    "from google.adk.runners import Runner",
    "from google.adk.sessions import InMemorySessionService",
    "from google.genai.types import Content, Part",
    "from google.adk.a2a import A2AServer",
    "from google.adk.a2a import A2AClient",
    "from google.adk.agents import BaseAgent",
    "from vertexai.preview import reasoning_engines",
]
OUT["imports"] = {}
for stmt in IMPORTS:
    try:
        exec(compile(stmt, "<tutorial-line>", "exec"), {})
        OUT["imports"][stmt] = {"ok": True}
    except Exception as e:
        OUT["imports"][stmt] = {"ok": False,
                               "error": f"{type(e).__name__}: {e}"}

# --- 4. top-level submodules that DO exist inside google.adk ---
try:
    import pkgutil, google.adk
    OUT["google_adk_submodules"] = sorted(
        m.name for m in pkgutil.iter_modules(google.adk.__path__))
except Exception:
    OUT["google_adk_submodules"] = traceback.format_exc()

# --- 5. construct the minimal agents the tutorial shows (no model call) ---
def show(label, fn):
    try:
        OUT.setdefault("construct", {})[label] = {"ok": True, "value": fn()}
    except Exception as e:
        OUT.setdefault("construct", {})[label] = {
            "ok": False, "error": f"{type(e).__name__}: {e}"}

def build():
    from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
    analyzer = LlmAgent(name="analyzer", model="gemini-2.0-flash",
                        instruction="Summarise the input.", output_key="analysis")
    suggester = LlmAgent(name="suggester", model="gemini-2.0-flash",
                         instruction="Use {analysis}.", output_key="suggestions")
    seq = SequentialAgent(name="pipeline", sub_agents=[analyzer, suggester])
    a = LlmAgent(name="docs", model="gemini-2.0-flash",
                 instruction="docs", output_key="docs_out")
    b = LlmAgent(name="issues", model="gemini-2.0-flash",
                 instruction="issues", output_key="issues_out")
    par = ParallelAgent(name="research", sub_agents=[a, b])
    return json.dumps({
        "sequential_name": seq.name,
        "sequential_children": [s.name for s in seq.sub_agents],
        "parallel_name": par.name,
        "parallel_children": [s.name for s in par.sub_agents],
        "llm_output_key": analyzer.output_key,
        "llm_model": analyzer.model,
    })

show("sequential_and_parallel_agents", build)

def nested():
    from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
    inner = SequentialAgent(name="inner", sub_agents=[
        LlmAgent(name="i1", model="gemini-2.0-flash", instruction="i1")])
    par = ParallelAgent(name="outer_par", sub_agents=[
        inner, LlmAgent(name="i2", model="gemini-2.0-flash", instruction="i2")])
    root = SequentialAgent(name="root", sub_agents=[
        par, LlmAgent(name="synth", model="gemini-2.0-flash", instruction="synth")])
    return json.dumps({"root": root.name,
                       "root_children": [c.name for c in root.sub_agents]})

show("hierarchical_tree_tutorial_shape", nested)

def aliased_agent():
    from google.adk.agents import Agent
    return json.dumps({"Agent_is": Agent.__name__})

show("Agent_alias", aliased_agent)

def same_output_key():
    """Tutorial claims duplicate output_key is the race-condition mistake.
    Check whether the framework rejects it at construction time."""
    from google.adk.agents import LlmAgent, ParallelAgent
    a = LlmAgent(name="a", model="gemini-2.0-flash", instruction="a",
                 output_key="result")
    b = LlmAgent(name="b", model="gemini-2.0-flash", instruction="b",
                 output_key="result")
    par = ParallelAgent(name="dup", sub_agents=[a, b])
    return json.dumps({"constructed": True, "children": [c.name for c in par.sub_agents]})

show("duplicate_output_key_construction", same_output_key)

# --- 6. ADK CLI the tutorial tells readers to verify with: `adk --version` ---
cli = Path(sys.executable).parent / "adk"
OUT["adk_cli_exists"] = cli.exists()
if cli.exists():
    r = subprocess.run([str(cli), "--version"], capture_output=True, text=True,
                       timeout=60)
    OUT["adk_cli_version"] = {"rc": r.returncode, "stdout": r.stdout.strip(),
                              "stderr": r.stderr.strip()}
    r2 = subprocess.run([str(cli), "--help"], capture_output=True, text=True,
                        timeout=60)
    OUT["adk_cli_help_head"] = "\n".join(r2.stdout.splitlines()[:25])

OUT["utc_finished"] = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                     capture_output=True, text=True).stdout.strip()
print(json.dumps(OUT, indent=2))
