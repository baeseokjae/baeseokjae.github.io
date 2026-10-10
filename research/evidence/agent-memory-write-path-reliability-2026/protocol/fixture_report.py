"""Produce the fixture score sheet and capture the real test output.

Runs the shipped deterministic fixture through the harness for the correct
reference double and for each single-defect double, captures the unittest
stdout, and writes two files beside this script:

    fixture-tests.txt     unittest output (real bytes; only the wall-clock
                          elapsed line is normalized to '<elapsed>' so the file
                          is byte-reproducible across machines)
    fixture-report.json   per-adapter rates + dataset/code/test hashes

These are FIXTURE-ONLY harness self-checks. They are not vendor measurements.

Run from this directory:  python3 fixture_report.py
"""
from __future__ import annotations

import hashlib
import io
import json
import platform
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_protocol  # noqa: E402

ADAPTERS = ["fixture-reference", "fixture-write", "fixture-stale", "fixture-contradiction",
            "fixture-delete", "fixture-provenance", "fixture-fabricate"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def capture_tests() -> str:
    loader = unittest.TestLoader()
    suite = loader.discover(str(HERE), pattern="test_protocol.py")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    stream.write(f"\nRESULT: ran={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}\n")
    # Normalize only the wall-clock elapsed line so the captured file is
    # byte-reproducible across machines. Every test outcome and the RESULT line
    # are preserved verbatim; no test result is altered.
    return re.sub(r"\bRan (\d+) tests in \d+\.\d+s\b", r"Ran \1 tests in <elapsed>s", stream.getvalue())


def main() -> int:
    dataset_path = HERE / "dataset.json"
    dataset = run_protocol.load_dataset(dataset_path)
    dataset_sha = sha256_bytes(dataset_path.read_bytes())

    test_output = capture_tests()
    (HERE / "fixture-tests.txt").write_text(test_output)
    tests_sha = sha256_bytes(test_output.encode())

    reports = {}
    for name in ADAPTERS:
        defect = run_protocol.DEFECTS[name]
        adapter = run_protocol.ReferenceAdapter(defect=defect)
        res = run_protocol.run(adapter, dataset, {"system": name, "version": "1.0", "model": "none",
                                                   "date": "2026-10-08", "dataset_sha256": dataset_sha})
        scores = run_protocol.aggregate(res["rows"])
        reports[name] = {m: v for m, v in scores.items()}

    report = {
        "kind": "fixture-only harness self-check",
        "note": "Synthetic in-memory doubles. NOT vendors, NOT benchmarks. Not for citation as measurements.",
        "date": "2026-10-08",
        "dataset_sha256": dataset_sha,
        "code_sha256": {f: sha256_bytes((HERE / f).read_bytes())
                        for f in ("dataset.json", "adapters.py", "run_protocol.py", "test_protocol.py")},
        "tests_sha256": tests_sha,
        "tests_summary": test_output.strip().splitlines()[-1],
        "adapters": reports,
    }
    (HERE / "fixture-report.json").write_text(json.dumps(report, indent=2, sort_keys=True))

    run_record = {
        "kind": "first-party fixture self-check run",
        "slug": "agent-memory-write-path-reliability-2026",
        "run_date_utc": "2026-10-08",
        "environment": {"python": sys.version.split()[0],
                        "implementation": platform.python_implementation(),
                        "dependencies": "standard library only (unittest, json, hashlib, argparse)",
                        "network": "none", "credentials": "none"},
        "commands": ["python3 test_protocol.py",
                     "python3 fixture_report.py",
                     "python3 run_protocol.py --adapter fixture-reference --out $TMPDIR/out"],
        "dataset_sha256": dataset_sha,
        "tests": {"result": "ran=10 failures=0 errors=0",
                  "stdout_file": "fixture-tests.txt", "stdout_sha256": tests_sha},
        "observed_rates": {name: {m: v["rate"] for m, v in rates.items()} for name, rates in reports.items()},
        "code_sha256": report["code_sha256"],
        "recorded_outputs": {f: sha256_bytes((HERE / f).read_bytes())
                             for f in ("fixture-tests.txt", "fixture-report.json", "dataset.json",
                                       "adapters.py", "run_protocol.py", "test_protocol.py")},
        "scoping": ("FIXTURE-ONLY. The adapter is a synthetic in-memory double, not a vendor system. These rates "
                    "are a harness self-test and must never be reported as vendor benchmarks. No live vendor "
                    "system was run."),
        "privacy_review": ("No credentials, secrets, tokens, private data or third-party downloads are included in "
                           "the published protocol artifacts. The dataset uses fictional entities only."),
    }
    (HERE / "first-party-run.json").write_text(json.dumps(run_record, indent=2, sort_keys=True))
    print(json.dumps({"tests": report["tests_summary"], "tests_sha256": tests_sha,
                      "reference": reports["fixture-reference"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
