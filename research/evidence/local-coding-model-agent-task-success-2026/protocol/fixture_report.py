#!/usr/bin/env python3
"""Run the harness self-check and record its real output.

  python3 fixture_report.py

Writes (into this directory):
  fixture-tests.txt    raw unittest stdout, with only the wall-clock line normalized
  fixture-report.json  per-double score sheet + hashes of the dataset and harness code

These are FIXTURE results. The doubles are synthetic and offline; not one of these numbers
is a measurement of any model or vendor system.
"""
from __future__ import annotations

import hashlib
import io
import json
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import harness  # noqa: E402
import models  # noqa: E402

NORMALIZE = re.compile(r"^Ran (\d+) tests? in [0-9.]+s$", re.M)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    started = datetime.now(timezone.utc)
    proc = subprocess.run([sys.executable, "test_harness.py"], cwd=HERE,
                          capture_output=True, text=True, timeout=900)
    raw = proc.stdout + proc.stderr
    normalized = NORMALIZE.sub(lambda m: "Ran %s tests in <elapsed>s" % m.group(1), raw)
    (HERE / "fixture-tests.txt").write_text(normalized)
    summary = re.findall(r"^(\w+.*)$", normalized, re.M)
    results = []
    with tempfile.TemporaryDirectory(prefix="rockb-fixture-") as tmp:
        for name, cls in sorted(models.FIXTURES.items()):
            run = harness.run_session(cls(), tasks_path=HERE / "tasks.json",
                                      workdir=Path(tmp) / ("repo-" + name))
            results.append({
                "double": name,
                "adapter": run["adapter"],
                "records": [{k: r[k] for k in ("task_id", "category", "status", "checks",
                                              "steps", "test_runs", "escalations", "wall_clock_s")}
                            for r in run["records"]],
                "aggregate": run["aggregate"],
                "matrix_csv": harness.matrix_csv(run),
            })
    report = {
        "kind": "fixture_self_check",
        "note": ("Synthetic, offline doubles used to validate the harness and scorer. "
                 "Never a benchmark of any model or vendor system. No model was loaded and "
                 "no GPU time was used."),
        "generated_at": started.isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "tests": {"returncode": proc.returncode, "raw_sha256": sha256(HERE / "fixture-tests.txt"),
                  "result_line": [line for line in reversed(normalized.splitlines())
                                  if "tests in" in line][:1]},
        "hashes": {"tasks_json": sha256(HERE / "tasks.json"),
                   "sandbox_tree": harness.tree_sha256(HERE / "sandbox"),
                   "harness.py": sha256(HERE / "harness.py"),
                   "models.py": sha256(HERE / "models.py")},
        "doubles": results,
    }
    (HERE / "fixture-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("fixture-tests.txt sha256=%s" % report["tests"]["raw_sha256"])
    print("tests returncode=%d result=%s" % (proc.returncode, report["tests"]["result_line"]))
    for entry in results:
        print("  %-16s completed=%d partially=%d failed=%d"
              % (entry["double"], entry["aggregate"]["completed"],
                 entry["aggregate"]["partially"], entry["aggregate"]["failed"]))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
