#!/usr/bin/env python3
"""Frozen task-success harness for local coding models.

The harness drives a *task adapter* (a model plus the tool loop around it) through a frozen
set of small repository tasks and scores the END STATE of the repository after each task:
completed / partially / failed. It records wall-clock seconds, how many times the adapter
asked to run the test suite, and how often it escalated instead of finishing.

It deliberately does not measure tokens/second, acceptance rates or leaderboard scores.

Everything here is standard-library only. The sandbox under ./sandbox is a synthetic
fixture package, never a real project snapshot.

Adapter contract
----------------
class TaskAdapter:
    name = "human-readable, version-pinned identifier"
    def next_action(self, observation) -> dict

observation = {"task": {...}, "step": 0-based step index, "files": {relpath: text},
               "last_test_output": str | None, "steps_left": int}

Returned action is one of:
  {"op": "write",  "path": "inventory/store.py", "content": "..."}
  {"op": "patch",  "path": "...", "find": "...", "replace": "..."}
  {"op": "run_tests"}
  {"op": "escalate", "reason": "..."}   # gives up / asks a human
  {"op": "stop"}                        # believes the task is done

Scoring: "completed" = every check for the task passes; "partially" = at least one check
passes (for example the method exists but the suite is still red); "failed" = no check
passes, or the adapter stopped/escalated without changing anything that helps.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_TIMEOUT_S = 120


# ----------------------------------------------------------------------------- utilities
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_sha256(root: Path) -> str:
    """Deterministic hash of a file tree: sorted relative paths plus their bytes."""
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        h.update(rel.encode() + b"\0")
        h.update(path.read_bytes() + b"\0")
    return h.hexdigest()


def read_files(root: Path) -> dict:
    out = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            out[rel] = path.read_text()
        except UnicodeDecodeError:
            out[rel] = "<binary>"
    return out


def run_suite(workdir: Path, modules=None) -> str:
    """Run the sandbox unittest suite in a subprocess and return combined stdout+stderr.

    modules=None runs the whole discovered suite; a list of module names runs only those,
    which is how a task scopes its suite so an unrelated frozen failure cannot mask it.
    """
    env = dict(os.environ, PYTHONPATH=str(workdir), PYTHONDONTWRITEBYTECODE="1")
    if modules:
        cmd = [sys.executable, "-m", "unittest", "-v"] + list(modules)
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-v", "-s", "tests", "-t", "."]
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, env=env, capture_output=True, text=True, timeout=TEST_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return "TIMEOUT: suite exceeded %ds" % TEST_TIMEOUT_S
    return (proc.stdout + proc.stderr).strip()


# ----------------------------------------------------------------------------- verifiers
def _checks_T1(workdir: Path, suite: str, frozen: dict) -> dict:
    store = workdir / "inventory" / "store.py"
    src = store.read_text() if store.is_file() else ""
    exists = "def count(" in src
    tracks = False
    if exists:
        probe = (
            "from inventory import Store\n"
            "s = Store()\n"
            "assert s.count() == 0, s.count()\n"
            "s.add('a', 1.0); s.add('b', 2.0)\n"
            "assert s.count() == 2, s.count()\n"
            "s.remove('a')\n"
            "assert s.count() == 1, s.count()\n"
            "print('count-ok')\n"
        )
        env = dict(os.environ, PYTHONPATH=str(workdir))
        try:
            proc = subprocess.run([sys.executable, "-c", probe], cwd=workdir, env=env,
                                  capture_output=True, text=True, timeout=60)
            tracks = proc.returncode == 0 and "count-ok" in proc.stdout
        except subprocess.TimeoutExpired:
            tracks = False
    return {
        "count_method_defined": exists,
        "count_tracks_add_and_remove": tracks,
        "suite_passes": "OK" in suite and "FAILED" not in suite,
    }


def _checks_T2(workdir: Path, suite: str, frozen: dict) -> dict:
    module = workdir / "tests" / "test_count.py"
    # The verbose line for the new test must be present AND have passed; a missing module
    # also prints the word test_count in its error text, so matching the name alone is wrong.
    ran = any(line.startswith("test_count_tracks") and line.rstrip().endswith("ok")
              for line in suite.splitlines())
    return {
        "test_module_present": module.is_file(),
        "count_test_executed": ran,
        "suite_passes": "OK" in suite and "FAILED" not in suite,
    }


def _checks_T3(workdir: Path, suite: str, frozen: dict) -> dict:
    test = workdir / "tests" / "test_report.py"
    unmodified = test.is_file() and test.read_text() == frozen.get("tests/test_report.py", "")
    probe = (
        "from inventory import Store, format_total\n"
        "s = Store()\n"
        "s.add('a', 1.5); s.add('b', 2.0)\n"
        "print('RENDER:' + format_total(s))\n"
    )
    env = dict(os.environ, PYTHONPATH=str(workdir))
    rendered = ""
    try:
        proc = subprocess.run([sys.executable, "-c", probe], cwd=workdir, env=env,
                              capture_output=True, text=True, timeout=60)
        rendered = proc.stdout.strip()
    except subprocess.TimeoutExpired:
        rendered = "TIMEOUT"
    return {
        "suite_passes": "OK" in suite and "FAILED" not in suite,
        "renders_two_decimals": rendered == "RENDER:total: 3.50",
        "frozen_test_unmodified": unmodified,
    }


def _checks_T4(workdir: Path, suite: str, frozen: dict) -> dict:
    def sources():
        for path in sorted(workdir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            yield path.relative_to(workdir).as_posix(), path.read_text()

    def_removed = True
    call_removed = True
    for rel, text in sources():
        if "def add(" in text:
            def_removed = False
        for line in text.splitlines():
            stripped = line.split("#", 1)[0]
            if ".add(" in stripped or "import add" in stripped:
                call_removed = False
    insert_present = any("def insert(" in text for _, text in sources())
    return {
        "old_definition_gone": def_removed,
        "old_call_sites_gone": call_removed,
        "new_name_defined": insert_present,
        "suite_passes": "OK" in suite and "FAILED" not in suite,
    }


VERIFIERS = {"T1": _checks_T1, "T2": _checks_T2, "T3": _checks_T3, "T4": _checks_T4}


#: Checks that count towards the score. Suite-success guards are recorded in `checks`
#: but never grant partial credit on their own: the frozen tests/test_store.py is green,
#: so "the scoped suite passes" is not evidence that a task advanced.
SCORE_KEYS = {
    "T1": ["count_method_defined", "count_tracks_add_and_remove"],
    "T2": ["test_module_present", "count_test_executed"],
    "T3": ["renders_two_decimals", "suite_passes"],
    "T4": ["old_definition_gone", "old_call_sites_gone", "new_name_defined"],
}


def score(checks: dict, required=None) -> str:
    keys = list(required if required is not None else checks.keys())
    passed = [name for name in keys if checks.get(name)]
    if len(passed) == len(keys):
        return "completed"
    if passed:
        return "partially"
    return "failed"


# ----------------------------------------------------------------------------- runner
def load_tasks(tasks_path: Path) -> dict:
    return json.loads(tasks_path.read_text())


def materialize(sandbox: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(sandbox, dest)


def run_session(adapter, *, tasks_path: Path = None, workdir: Path, step_budget: int = None,
                wall_clock_budget_s: int = None) -> dict:
    """Run the frozen task set in order against one adapter, in one working copy."""
    tasks_path = tasks_path or (HERE / "tasks.json")
    spec = load_tasks(tasks_path)
    sandbox = tasks_path.parent / spec.get("sandbox_root", "sandbox")
    step_budget = step_budget or spec.get("step_budget", 12)
    wall_clock_budget_s = wall_clock_budget_s or spec.get("wall_clock_budget_s", 600)

    frozen = read_files(sandbox)
    materialize(sandbox, workdir)

    records, transcript = [], []
    session_start = time.monotonic()
    for task in spec["tasks"]:
        started = time.monotonic()
        steps = test_runs = escalations = 0
        last_output = None
        stopped = False
        while steps < step_budget and (time.monotonic() - session_start) < wall_clock_budget_s:
            action = adapter.next_action({
                "task": task,
                "step": steps,
                "files": read_files(workdir),
                "last_test_output": last_output,
                "steps_left": step_budget - steps,
            })
            op = (action or {}).get("op", "stop")
            note = ""
            if op == "write":
                target = workdir / action["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(action["content"])
                note = "wrote %d bytes" % len(action["content"])
            elif op == "patch":
                target = workdir / action["path"]
                text = target.read_text()
                if action["find"] not in text:
                    note = "patch anchor not found"
                else:
                    target.write_text(text.replace(action["find"], action["replace"], 1))
                    note = "patched"
            elif op == "run_tests":
                last_output = run_suite(workdir, task.get("suite_modules"))
                test_runs += 1
                note = "test run %d" % test_runs
            elif op == "escalate":
                escalations += 1
                note = "escalated: %s" % action.get("reason", "")
                steps += 1
                transcript.append({"task_id": task["id"], "step": steps, "op": op, "note": note})
                stopped = True
                break
            else:
                note = "stop"
                steps += 1
                transcript.append({"task_id": task["id"], "step": steps, "op": "stop", "note": note})
                stopped = True
                break
            steps += 1
            transcript.append({"task_id": task["id"], "step": steps, "op": op,
                               "target": action.get("path", ""), "note": note})

        suite = run_suite(workdir, task.get("suite_modules"))
        checks = VERIFIERS[task["verifier"]](workdir, suite, frozen)
        records.append({
            "task_id": task["id"],
            "category": task["category"],
            "status": score(checks, SCORE_KEYS[task["verifier"]]),
            "checks": checks,
            "steps": steps,
            "test_runs": test_runs,
            "escalations": escalations,
            "stopped_early": stopped,
            "wall_clock_s": round(time.monotonic() - started, 3),
            "suite_ok": "OK" in suite and "FAILED" not in suite,
        })

    counts = {"completed": 0, "partially": 0, "failed": 0}
    for rec in records:
        counts[rec["status"]] += 1
    aggregate = {
        "tasks": len(records),
        **counts,
        "completion_rate": round(counts["completed"] / len(records), 3) if records else None,
        "mean_wall_clock_s": round(sum(r["wall_clock_s"] for r in records) / len(records), 3) if records else None,
        "total_test_runs": sum(r["test_runs"] for r in records),
        "total_escalations": sum(r["escalations"] for r in records),
    }
    return {
        "adapter": getattr(adapter, "name", type(adapter).__name__),
        "task_set": spec["name"],
        "task_set_sha256": sha256_bytes(tasks_path.read_bytes()),
        "sandbox_tree_sha256": tree_sha256(sandbox),
        "step_budget": step_budget,
        "wall_clock_budget_s": wall_clock_budget_s,
        "session_wall_clock_s": round(time.monotonic() - session_start, 3),
        "records": records,
        "aggregate": aggregate,
        "transcript": transcript,
    }


def matrix_csv(result: dict) -> str:
    """The scoring sheet: one row per task, plus an aggregate row."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["task_id", "category", "status", "checks_passed", "checks_total",
                     "steps", "test_runs", "escalations", "wall_clock_s", "suite_ok"])
    for rec in result["records"]:
        passed = sum(1 for ok in rec["checks"].values() if ok)
        writer.writerow([rec["task_id"], rec["category"], rec["status"], passed,
                         len(rec["checks"]), rec["steps"], rec["test_runs"],
                         rec["escalations"], rec["wall_clock_s"], rec["suite_ok"]])
    agg = result["aggregate"]
    writer.writerow(["AGGREGATE", "", "completed=%d" % agg["completed"], "", "",
                     "", agg["total_test_runs"], agg["total_escalations"],
                     agg["mean_wall_clock_s"], ""])
    return buf.getvalue()
